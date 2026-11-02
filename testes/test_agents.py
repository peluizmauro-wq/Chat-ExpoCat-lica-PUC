from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from database import ExpoDatabase
from rag_engine import RAGEngine
from ml_engine import ExpoRiskModel
from agents import OperationalAgent, RiskDataAgent, MultiAgentCoordinator

def build():
    db = ExpoDatabase(ROOT / "dados")
    rag = RAGEngine(ROOT / "documentos", ROOT / "chroma_db")
    ml = ExpoRiskModel(ROOT / "ml" / "model")
    op = OperationalAgent(rag)
    risk = RiskDataAgent(db, ml)
    return MultiAgentCoordinator(op, risk)

def test_two_agents_compound_task():
    coord = build()
    q = (
        "Faça uma análise integrada: consulte as pendências da Turismo Peregrino Brasil, "
        "analise o risco do cenário 3 e informe o prazo do projeto técnico."
    )
    assert coord.can_handle(q)
    answer, sources, mode = coord.run(q)
    assert "Agente Operacional" in answer
    assert "Agente de Dados e Risco" in answer
    assert mode == "multiagente"
    assert any("DuckDB" in s for s in sources)
    assert any("UCI" in s for s in sources)

if __name__ == "__main__":
    test_two_agents_compound_task()
    print("OK: dois agentes especializados executaram uma tarefa composta.")
