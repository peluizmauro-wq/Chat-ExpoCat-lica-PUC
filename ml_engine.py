from pathlib import Path
import json
import re
import joblib
import pandas as pd

class ExpoRiskModel:
    def __init__(self, model_dir):
        self.model_dir = Path(model_dir)
        self.model_path = self.model_dir / "risk_model.joblib"
        self.metrics_path = self.model_dir / "metrics.json"
        self.scenarios_path = self.model_dir / "scenarios.json"
        self.bundle = None
        self.metrics = {}
        self.scenarios = []
        self._load()

    def _load(self):
        if self.model_path.exists():
            try:
                self.bundle = joblib.load(self.model_path)
            except Exception:
                self.bundle = None
        if self.metrics_path.exists():
            self.metrics = json.loads(self.metrics_path.read_text(encoding="utf-8"))
        if self.scenarios_path.exists():
            self.scenarios = json.loads(self.scenarios_path.read_text(encoding="utf-8"))

    @property
    def available(self):
        return self.bundle is not None and bool(self.scenarios)

    def describe(self):
        if not self.available:
            return "Modelo ainda não treinado."
        return (
            f"Modelo ML disponível: {self.metrics.get('modelo_selecionado', 'AutoML')}; "
            f"recall={self.metrics.get('recall', 'n/d')}; "
            f"F1={self.metrics.get('f1', 'n/d')}."
        )

    def _scenario_from_question(self, question):
        m = re.search(r"(?:cenario|cenário)\s*(\d+)", question.lower())
        if m:
            sid = int(m.group(1))
            for s in self.scenarios:
                if s["id"] == sid:
                    return s
        if "alto risco" in question.lower():
            return self.scenarios[-1] if self.scenarios else None
        if "baixo risco" in question.lower():
            return self.scenarios[0] if self.scenarios else None
        return None

    def answer(self, question):
        if not self.available:
            return (
                "O modelo preditivo ainda não está disponível neste ambiente. "
                "Execute o treinamento para gerar os artefatos do modelo.",
                ["ML: modelo indisponível"],
            )

        scenario = self._scenario_from_question(question)
        if scenario is None:
            options = "\n".join(
                f"- Cenário {s['id']}: {s['descricao']}" for s in self.scenarios
            )
            return (
                "Posso demonstrar a classificação de risco usando três cenários do dataset público:\n"
                + options
                + "\n\nPergunte, por exemplo: **Analise o risco do cenário 3.**",
                ["UCI Statlog German Credit + modelo FLAML"],
            )

        columns = self.bundle["feature_columns"]
        row = pd.DataFrame([scenario["features"]]).reindex(columns=columns, fill_value=0)
        automl = self.bundle["automl"]
        prob = float(automl.predict_proba(row)[:, 1][0])
        threshold = float(self.bundle.get("threshold", 0.5))
        classe = int(prob >= threshold)
        if prob >= max(0.50, threshold * 2):
            nivel = "ALTO"
        elif prob >= threshold:
            nivel = "ATENÇÃO"
        else:
            nivel = "BAIXO"

        text = (
            f"**{scenario['nome']} — risco {nivel}**\n\n"
            f"Probabilidade estimada pelo modelo: **{prob:.1%}**. "
            f"Limite de decisão definido na validação: **{threshold:.0%}**. "
            f"Classificação binária: **{'caso de risco' if classe else 'caso sem risco'}**.\n\n"
            "Esta é uma demonstração acadêmica por analogia, treinada em uma base pública de risco de crédito. "
            "Ela mostra como uma futura base histórica da ExpoCatólica poderia apoiar alertas preventivos, "
            "mas não representa avaliação real de um expositor."
        )
        return text, [
            "UCI Machine Learning Repository — Statlog German Credit Data (dataset 144)",
            f"FLAML — {self.metrics.get('modelo_selecionado', 'modelo AutoML')}",
        ]
