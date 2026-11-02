import re
import unicodedata
from dataclasses import dataclass

def _norm(text):
    return unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode("ascii").lower()

@dataclass
class AgentResult:
    agent: str
    answer: str
    sources: list
    tools_used: list

class OperationalAgent:
    name = "Agente Operacional ExpoCatólica"
    role = "Especialista em regras, prazos, montagem, desmontagem e normas do evento"

    def __init__(self, rag, observability=None):
        self.rag = rag
        self.observability = observability

    def _summarize(self, question, contexts):
        q = _norm(question)
        if ("projeto tecnico" in q or "art/rrt" in q) and "prazo" in q:
            return (
                "O prazo para envio do projeto técnico com ART/RRT é 10 de junho de 2026. "
                "Se ainda estiver pendente, confirme a regularização com a organização/CAEX."
            )
        if "montagem" in q and ("data" in q or "horario" in q):
            return (
                "As montadoras terceirizadas trabalham em 20 e 21 de julho de 2026, "
                "das 12h às 21h. Em 22 de julho, a organização interna pelo expositor ocorre das 10h às 21h."
            )

        words = {w for w in re.findall(r"\w+", q) if len(w) > 3}
        candidates = []
        for c in contexts:
            for sent in re.split(r"(?<=[.!?])\s+|\n+", c["text"]):
                sent = sent.strip()
                if len(sent) < 25 or sent.lower().startswith("pergunta:"):
                    continue
                score = len(words & set(re.findall(r"\w+", _norm(sent))))
                if score:
                    candidates.append((score, sent, c["source"]))
        candidates.sort(key=lambda x: x[0], reverse=True)
        chosen, seen = [], set()
        for score, sent, src in candidates:
            key = sent[:90]
            if key not in seen:
                chosen.append((sent, src))
                seen.add(key)
            if len(chosen) >= 4:
                break
        if not chosen:
            return (
                "Não encontrei base documental suficiente para responder com segurança. "
                "A orientação é confirmar com a organização/CAEX."
            )
        return "\n".join(f"- {sent}" for sent, _ in chosen)

    def run(self, question):
        if self.observability:
            with self.observability.span(
                "agente-operacional-rag",
                input_data=question,
                metadata={"agent": self.name, "tool": "RAG"}
            ) as span:
                contexts = self.rag.search(question, k=4)
                sources = []
                for c in contexts:
                    if c["source"] not in sources:
                        sources.append(c["source"])
                answer = self._summarize(question, contexts)
                if span is not None:
                    span.update(
                        output=answer,
                        metadata={"sources": sources, "rag_backend": self.rag.backend}
                    )
        else:
            contexts = self.rag.search(question, k=4)
            sources = []
            for c in contexts:
                if c["source"] not in sources:
                    sources.append(c["source"])
            answer = self._summarize(question, contexts)

        return AgentResult(
            agent=self.name,
            answer=answer,
            sources=sources,
            tools_used=["RAG", self.rag.backend],
        )

class RiskDataAgent:
    name = "Agente de Dados e Risco"
    role = "Analista de dados estruturados e demonstrações de classificação preditiva"

    def __init__(self, db, risk_model, observability=None):
        self.db = db
        self.risk_model = risk_model
        self.observability = observability

    def run(self, question, role="Organização", requester_id=None):
        parts = []
        sources = []
        tools = []

        target = self.db.find_exhibitor(question)
        q = _norm(question)
        data_terms = (
            "pendencia", "estande", "metragem", "setor", "expositor",
            "contrato", "cidade", "segmento"
        )
        if target or any(t in q for t in data_terms):
            if self.observability:
                with self.observability.span(
                    "agente-dados-duckdb",
                    input_data=question,
                    metadata={"agent": self.name, "tool": "DuckDB"}
                ) as span:
                    data_answer, sql = self.db.answer_query(
                        question, role=role, requester_id=requester_id
                    )
                    if span is not None:
                        span.update(output=data_answer or "sem resultado")
            else:
                data_answer, sql = self.db.answer_query(
                    question, role=role, requester_id=requester_id
                )
            if data_answer:
                parts.append(data_answer)
                sources.append("DuckDB: dados estruturados da demonstração")
                tools.append("DuckDB")

        ml_terms = (
            "cenario", "cenário", "risco", "modelo preditivo",
            "previsao", "previsão", "classificacao", "classificação"
        )
        if self.risk_model is not None and any(t in q for t in ml_terms):
            if self.observability:
                with self.observability.span(
                    "agente-risco-modelo-ml",
                    input_data=question,
                    metadata={"agent": self.name, "tool": "FLAML/LightGBM"}
                ) as span:
                    ml_answer, ml_sources = self.risk_model.answer(question)
                    if span is not None:
                        span.update(output=ml_answer)
            else:
                ml_answer, ml_sources = self.risk_model.answer(question)
            parts.append(ml_answer)
            sources.extend(ml_sources)
            tools.append("Modelo ML/FLAML")

        if not parts:
            parts.append(
                "Não identifiquei uma consulta de dados ou previsão que possa executar com segurança."
            )

        return AgentResult(
            agent=self.name,
            answer="\n\n".join(parts),
            sources=list(dict.fromkeys(sources)),
            tools_used=list(dict.fromkeys(tools)),
        )

class MultiAgentCoordinator:
    name = "Coordenador Multiagente"

    def __init__(self, operational_agent, risk_agent, observability=None):
        self.operational_agent = operational_agent
        self.risk_agent = risk_agent
        self.observability = observability

    def _needs_operational(self, question):
        q = _norm(question)
        terms = (
            "manual", "regulamento", "regra", "prazo", "montagem", "desmontagem",
            "credencial", "energia", "hidraul", "compartilhar", "marca", "extintor",
            "material promocional", "caex", "horario", "horário", "norma"
        )
        return any(t in q for t in terms)

    def _needs_risk(self, question):
        q = _norm(question)
        terms = (
            "cenario", "cenário", "risco", "modelo preditivo", "previsao", "previsão",
            "pendencia", "pendência", "estande", "metragem", "setor", "expositor",
            "contrato", "cidade", "segmento"
        )
        return any(t in q for t in terms) or self.risk_agent.db.find_exhibitor(question) is not None

    def can_handle(self, question):
        q = _norm(question)
        explicit = any(x in q for x in (
            "agente operacional", "agente de dados", "agente de risco",
            "analise integrada", "análise integrada", "equipe de agentes",
            "multiagente", "dois agentes"
        ))
        return explicit or (self._needs_operational(question) and self._needs_risk(question))

    def run(self, question, role="Organização", requester_id=None):
        if self.observability:
            context = self.observability.span(
                "coordenador-multiagente",
                input_data=question,
                metadata={"component": self.name}
            )
        else:
            from contextlib import nullcontext
            context = nullcontext(None)

        with context as coord_span:
            results = []
            if self._needs_operational(question) or "agente operacional" in _norm(question):
                results.append(self.operational_agent.run(question))
            if self._needs_risk(question) or any(
                x in _norm(question) for x in ("agente de dados", "agente de risco")
            ):
                results.append(
                    self.risk_agent.run(question, role=role, requester_id=requester_id)
                )

            if not results:
                return None

            blocks = []
            all_sources = []
            actions = []
            for r in results:
                blocks.append(f"### {r.agent}\n{r.answer}")
                all_sources.extend(r.sources)
                actions.append(
                    f"{r.agent}: " + ", ".join(r.tools_used or ["sem ferramenta externa"])
                )

            if len(results) > 1:
                blocks.append(
                    "### Coordenação\n"
                    "Os dois agentes foram acionados porque a pergunta exige combinar "
                    "informação documental com dados e/ou previsão. O resultado acima mantém "
                    "cada evidência em sua camada de origem."
                )

            sources = list(dict.fromkeys(all_sources))
            sources.append("Orquestração: " + " | ".join(actions))
            answer = "\n\n".join(blocks)

            if coord_span is not None:
                coord_span.update(
                    output=answer,
                    metadata={"agents_used": [r.agent for r in results]}
                )

            return answer, sources, "multiagente"
