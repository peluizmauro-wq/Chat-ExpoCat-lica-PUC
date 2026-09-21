from pathlib import Path
import os
import re
import unicodedata

def _norm(text):
    return unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode("ascii").lower()

class ExpoAssistant:
    def __init__(self, db, rag, prompt_path):
        self.db = db
        self.rag = rag
        self.system_prompt = Path(prompt_path).read_text(encoding="utf-8")

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
        return response.choices[0].message.content

    def answer(self, question, provider="Automático", role="Organização", requester_id=None):
        if self._is_data_question(question):
            answer, sql = self.db.answer_query(question, role=role, requester_id=requester_id)
            if answer:
                sources = ["DuckDB: dados/expositores.csv + dados/estandes.csv + dados/pendencias.csv"]
                if sql:
                    sources.append("Consulta SQL parametrizada executada em memória.")
                return answer, sources, "dados"

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
