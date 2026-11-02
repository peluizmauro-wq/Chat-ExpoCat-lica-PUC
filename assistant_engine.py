from pathlib import Path
import os
import re
import unicodedata

def _norm(text):
    return unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode("ascii").lower()

class ExpoAssistant:
    def __init__(self, db, rag, prompt_path, risk_model=None, coordinator=None, observability=None):
        self.db = db
        self.rag = rag
        self.risk_model = risk_model
        self.coordinator = coordinator
        self.observability = observability
        self.system_prompt = Path(prompt_path).read_text(encoding="utf-8")

    def _is_ml_question(self, q):
        nq = _norm(q)
        terms = [
            "modelo preditivo", "previsao de risco", "risco do cenario",
            "risco do cenário", "cenario 1", "cenario 2", "cenario 3",
            "cenário 1", "cenário 2", "cenário 3", "alto risco", "baixo risco"
        ]
        return any(t in nq for t in terms)

    def _is_data_question(self, q):
        nq = _norm(q)
        terms = [
            "estande", "metragem", "m2", "setor", "pendencia", "situacao do expositor",
            "status do contrato", "cidade do expositor", "segmento do expositor",
            "quantos expositores", "quais expositores"
        ]
        return any(t in nq for t in terms)

    def _offline_rag_answer(self, question, contexts):
        words = {w for w in re.findall(r"\w+", _norm(question)) if len(w) > 3}
        candidates = []
        for c in contexts:
            sentences = re.split(r"(?<=[.!?])\s+|\n+", c["text"])
            for sent in sentences:
                if len(sent.strip()) < 25:
                    continue
                sw = set(re.findall(r"\w+", _norm(sent)))
                score = len(words & sw)
                if score:
                    candidates.append((score, sent.strip(), c["source"]))
        candidates.sort(key=lambda x: x[0], reverse=True)
        chosen = []
        seen = set()
        for score, sent, src in candidates:
            key = sent[:80]
            if key not in seen:
                chosen.append((sent, src))
                seen.add(key)
            if len(chosen) == 4:
                break

        if not chosen:
            return (
                "Não encontrei informação suficiente nos documentos indexados para responder com segurança. "
                "Confirme esta questão com a organização/CAEX."
            )
        answer = "Com base nos documentos da ExpoCatólica 2026:\n\n"
        answer += "\n".join(f"- {sent}" for sent, _ in chosen)
        return answer

    def _openai_answer(self, question, contexts):
        from openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key or api_key.lower().startswith("cole_"):
            raise RuntimeError("OPENAI_API_KEY não configurada.")
        model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        context = "\n\n".join(
            f"[Fonte: {c['source']}]\n{c['text']}" for c in contexts
        )

        if self.observability:
            span_context = self.observability.span(
                "llm-openai-rag",
                input_data={"question": question, "context_sources": [c["source"] for c in contexts]},
                metadata={"model": model, "component": "LLM"}
            )
        else:
            from contextlib import nullcontext
            span_context = nullcontext(None)

        with span_context as span:
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=model,
                temperature=0.1,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {
                        "role": "user",
                        "content": (
                            f"Pergunta: {question}\n\n"
                            f"Contexto recuperado pelo RAG:\n{context}\n\n"
                            "Responda apenas com base no contexto. Cite os nomes dos arquivos-fonte ao final."
                        ),
                    },
                ],
            )
            output = response.choices[0].message.content
            if span is not None:
                usage = getattr(response, "usage", None)
                metadata = {}
                if usage is not None:
                    metadata = {
                        "input_tokens": getattr(usage, "prompt_tokens", None),
                        "output_tokens": getattr(usage, "completion_tokens", None),
                        "total_tokens": getattr(usage, "total_tokens", None),
                    }
                span.update(output=output, metadata=metadata)
            return output

    def answer(self, question, provider="Automático", role="Organização", requester_id=None):
        if self.coordinator is not None and self.coordinator.can_handle(question):
            result = self.coordinator.run(
                question, role=role, requester_id=requester_id
            )
            if result:
                return result

        if self._is_ml_question(question) and self.risk_model is not None:
            if self.observability:
                with self.observability.span(
                    "modelo-preditivo-direto",
                    input_data=question,
                    metadata={"tool": "FLAML/LightGBM"}
                ) as span:
                    answer, sources = self.risk_model.answer(question)
                    if span is not None:
                        span.update(output=answer)
            else:
                answer, sources = self.risk_model.answer(question)
            return answer, sources, "ml-preditivo"

        if self._is_data_question(question):
            if self.observability:
                with self.observability.span(
                    "consulta-duckdb-direta",
                    input_data=question,
                    metadata={"tool": "DuckDB"}
                ) as span:
                    answer, sql = self.db.answer_query(question, role=role, requester_id=requester_id)
                    if span is not None:
                        span.update(output=answer or "sem resultado")
            else:
                answer, sql = self.db.answer_query(question, role=role, requester_id=requester_id)
            if answer:
                sources = ["DuckDB: dados/expositores.csv + dados/estandes.csv + dados/pendencias.csv"]
                if sql:
                    sources.append("Consulta SQL parametrizada executada em memória.")
                return answer, sources, "dados"

        if self.observability:
            with self.observability.span(
                "retrieval-rag",
                input_data=question,
                metadata={"tool": "RAG", "backend": self.rag.backend}
            ) as span:
                contexts = self.rag.search(question, k=4)
                if span is not None:
                    span.update(
                        output=[{"source": c["source"], "score": c.get("score")} for c in contexts]
                    )
        else:
            contexts = self.rag.search(question, k=4)

        sources = []
        for c in contexts:
            if c["source"] not in sources:
                sources.append(c["source"])

        use_openai = provider == "OpenAI" or (
            provider == "Automático" and os.getenv("OPENAI_API_KEY", "").strip()
        )
        if use_openai:
            try:
                answer = self._openai_answer(question, contexts)
                return answer, sources, "rag+llm"
            except Exception as exc:
                answer = self._offline_rag_answer(question, contexts)
                answer += f"\n\n_Observação técnica: o modo LLM não pôde ser usado ({type(exc).__name__}); foi aplicado o modo local._"
                return answer, sources, "rag-local"

        answer = self._offline_rag_answer(question, contexts)
        return answer, sources, "rag-local"
