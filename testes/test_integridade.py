from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[1]

def count_rows(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return sum(1 for _ in csv.DictReader(f))

def test_files_exist():
    required = [
        "app.py", "database.py", "rag_engine.py", "assistant_engine.py",
        "system_prompt.txt", "requirements.txt", ".env.example", ".gitignore",
        "dados/expositores.csv", "dados/estandes.csv", "dados/pendencias.csv",
        "documentos/01_manual_expositor_2026.txt",
        "documentos/02_regulamento_geral_2026.txt",
        "documentos/03_normas_pro_magno_2026.txt",
    ]
    missing = [p for p in required if not (ROOT / p).exists()]
    assert not missing, f"Arquivos ausentes: {missing}"

def test_structured_data():
    assert count_rows(ROOT / "dados/expositores.csv") >= 10
    assert count_rows(ROOT / "dados/estandes.csv") >= 10
    assert count_rows(ROOT / "dados/pendencias.csv") >= 10

if __name__ == "__main__":
    test_files_exist()
    test_structured_data()
    print("OK: estrutura e dados básicos validados.")
