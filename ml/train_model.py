from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix
)
from flaml import AutoML

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "dados" / "german.data"
MODEL_DIR = ROOT / "model"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

FEATURE_NAMES = [f"Attribute{i}" for i in range(1, 21)]
COLUMNS = FEATURE_NAMES + ["target"]

CATEGORICAL = [
    "Attribute1", "Attribute3", "Attribute4", "Attribute6", "Attribute7",
    "Attribute9", "Attribute10", "Attribute12", "Attribute14", "Attribute15",
    "Attribute17", "Attribute19", "Attribute20"
]

def load_data():
    df = pd.read_csv(DATA_PATH, sep=r"\s+", header=None, names=COLUMNS)
    # UCI: 1 = bom risco, 2 = mau risco. Aqui usamos 1 = risco (classe positiva).
    df["target"] = (df["target"] == 2).astype(int)
    X = pd.get_dummies(df[FEATURE_NAMES].copy(), columns=CATEGORICAL, dtype=int)
    y = df["target"].copy()
    return X, y

def escolher_threshold(y_true, probabilities):
    """
    A documentação do dataset usa custo 5 para classificar um mau risco como bom
    e custo 1 para o erro inverso. Escolhemos o threshold no conjunto de validação,
    nunca no teste, para respeitar essa assimetria.
    """
    candidates = np.linspace(0.10, 0.70, 61)
    best = None
    for threshold in candidates:
        pred = (probabilities >= threshold).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_true, pred, labels=[0, 1]).ravel()
        cost = (5 * fn) + fp
        recall = recall_score(y_true, pred, zero_division=0)
        precision = precision_score(y_true, pred, zero_division=0)
        item = (cost, -recall, -precision, float(threshold))
        if best is None or item < best:
            best = item
    return round(best[3], 2)

def main():
    X, y = load_data()

    # 70% treino, 10% validação para threshold, 20% teste final.
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, random_state=42, stratify=y
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=2/3, random_state=42, stratify=y_temp
    )

    automl = AutoML()
    automl.fit(
        X_train=X_train,
        y_train=y_train,
        task="classification",
        metric="f1",
        time_budget=45,
        estimator_list=["lgbm", "rf", "xgboost"],
        seed=42,
        verbose=0,
    )

    val_prob = automl.predict_proba(X_val)[:, 1]
    threshold = escolher_threshold(y_val, val_prob)

    y_prob = automl.predict_proba(X_test)[:, 1]
    y_pred = (y_prob >= threshold).astype(int)

    metrics = {
        "dataset": "Statlog (German Credit Data) - UCI 144",
        "registros": int(len(X)),
        "atributos_originais": 20,
        "treino": int(len(X_train)),
        "validacao": int(len(X_val)),
        "teste": int(len(X_test)),
        "classe_positiva": "mau risco (1)",
        "modelo_selecionado": str(automl.best_estimator),
        "threshold_escolhido": threshold,
        "criterio_threshold": "minimizar custo: 5 x falso negativo + 1 x falso positivo",
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, y_prob)), 4),
        "confusion_matrix": confusion_matrix(y_test, y_pred, labels=[0, 1]).tolist(),
        "random_state": 42,
        "time_budget_seconds": 45,
        "nota_contextual": (
            "No projeto ExpoCatólica, recall é prioritário porque um falso negativo "
            "representa deixar passar um caso de risco que precisaria de atenção preventiva."
        ),
    }

    joblib.dump(
        {
            "automl": automl,
            "feature_columns": X.columns.tolist(),
            "categorical_columns": CATEGORICAL,
            "threshold": threshold,
        },
        MODEL_DIR / "risk_model.joblib",
    )

    scored = X_test.copy()
    scored["probabilidade"] = y_prob
    scored["target_real"] = y_test.values
    ranked = scored.sort_values("probabilidade")
    picks = [
        ("Cenário 1", "baixo risco previsto", ranked.iloc[0]),
        ("Cenário 2", "risco intermediário previsto", ranked.iloc[len(ranked)//2]),
        ("Cenário 3", "alto risco previsto", ranked.iloc[-1]),
    ]

    scenarios = []
    for idx, (nome, descricao, row) in enumerate(picks, start=1):
        features = {
            c: (int(row[c]) if float(row[c]).is_integer() else float(row[c]))
            for c in X.columns
        }
        scenarios.append({
            "id": idx,
            "nome": nome,
            "descricao": descricao,
            "probabilidade_referencia": round(float(row["probabilidade"]), 4),
            "classe_real_dataset": int(row["target_real"]),
            "features": features,
        })

    (MODEL_DIR / "metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (MODEL_DIR / "scenarios.json").write_text(
        json.dumps(scenarios, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    summary = f"""# Resultado do treinamento ML

Dataset: {metrics['dataset']}
Registros: {metrics['registros']}
Divisão: {metrics['treino']} treino / {metrics['validacao']} validação / {metrics['teste']} teste
Modelo selecionado automaticamente pelo FLAML: {metrics['modelo_selecionado']}
Threshold escolhido no conjunto de validação: {metrics['threshold_escolhido']}
Critério: {metrics['criterio_threshold']}

## Métricas no conjunto de teste

- Accuracy: {metrics['accuracy']}
- Precision: {metrics['precision']}
- Recall: {metrics['recall']}
- F1-score: {metrics['f1']}
- ROC-AUC: {metrics['roc_auc']}

## Interpretação para o projeto

Este modelo é uma demonstração acadêmica por analogia. A base pública classifica risco de crédito.
No projeto ExpoCatólica, usamos a mesma lógica de classificação binária para demonstrar como
uma futura base histórica de expositores poderia apoiar alertas preventivos.

A métrica que destacamos é o recall. A própria base UCI atribui custo maior ao erro de considerar
como bom risco um caso que, na realidade, é mau risco. Por analogia, no projeto ExpoCatólica,
queremos reduzir a chance de deixar passar sem alerta um expositor que precisaria de atenção.
"""
    (MODEL_DIR / "RESULTADO_TREINAMENTO.md").write_text(summary, encoding="utf-8")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
