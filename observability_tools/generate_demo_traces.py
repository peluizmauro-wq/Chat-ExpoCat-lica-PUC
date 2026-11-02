from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from database import ExpoDatabase
from rag_engine import RAGEngine
from ml_engine import ExpoRiskModel
from agents import OperationalAgent, RiskDataAgent, MultiAgentCoordinator
from assistant_engine import ExpoAssistant
from observability import Observability

def main():
    obs = Observability()
    if not obs.enabled:
        raise RuntimeError(
            "Langfuse não está ativo. Configure LANGFUSE_PUBLIC_KEY, "
            "LANGFUSE_SECRET_KEY e LANGFUSE_BASE_URL."
        )

    # Validação explícita de autenticação para evitar falso positivo no workflow.
    try:
        ok = obs.client.auth_check()
    except Exception as exc:
        raise RuntimeError(f"Falha ao validar autenticação no Langfuse: {exc}") from exc
    if not ok:
        raise RuntimeError(
            "Langfuse recusou as credenciais. Atualize PUBLIC_KEY e SECRET_KEY "
            "com um par novo criado no mesmo projeto."
        )
    print("OK: autenticação Langfuse validada.")

    db = ExpoDatabase(ROOT / "dados")
    rag = RAGEngine(ROOT / "documentos", ROOT / "chroma_db")
    risk_model = ExpoRiskModel(ROOT / "ml" / "model")

    op = OperationalAgent(rag, observability=obs)
    risk = RiskDataAgent(db, risk_model, observability=obs)
    coord = MultiAgentCoordinator(op, risk, observability=obs)
    assistant = ExpoAssistant(
        db,
        rag,
        ROOT / "system_prompt.txt",
        risk_model=risk_model,
        coordinator=coord,
        observability=obs,
    )

    questions = [
        "Quais são as datas e horários de montagem?",
        "Qual é o estande e a metragem da Editora Caminho Novo?",
        "Analise o risco do cenário 3.",
        "Use o Agente Operacional e informe o prazo do projeto técnico.",
        (
            "Faça uma análise integrada: consulte as pendências da Turismo Peregrino Brasil, "
            "analise o risco do cenário 3 e informe o prazo do projeto técnico."
        ),
    ]

    for i, question in enumerate(questions, start=1):
        with obs.trace(
            "chat-expocatolica",
            input_data=question,
            metadata={"source": "github-actions", "demo_trace": i}
        ) as holder:
            answer, sources, mode = assistant.answer(
                question,
                provider="Local (sem API)",
                role="Organização",
                requester_id=None,
            )
            obs.finish(
                holder,
                output=answer,
                metadata={"mode": mode, "sources": sources, "demo_trace": i}
            )
        print(f"Trace {i}/5: {mode} - {question}")

    obs.flush()
    print("OK: 5 traces enviados ao Langfuse.")

if __name__ == "__main__":
    main()
