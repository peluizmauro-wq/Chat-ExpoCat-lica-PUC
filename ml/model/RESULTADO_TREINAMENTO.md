# Resultado do treinamento ML

Dataset: Statlog (German Credit Data) - UCI 144
Registros: 1000
Divisão: 800 treino / 200 teste
Modelo selecionado automaticamente pelo FLAML: lgbm

## Métricas no conjunto de teste

- Accuracy: 0.72
- Precision: 0.54
- Recall: 0.45
- F1-score: 0.4909
- ROC-AUC: 0.7476

## Interpretação para o projeto

Este modelo é uma demonstração acadêmica por analogia. A base pública classifica risco de crédito.
No projeto ExpoCatólica, usamos a mesma lógica de classificação binária para demonstrar como
uma futura base histórica de expositores poderia apoiar alertas preventivos.

A métrica que destacamos no contexto do projeto é o recall, porque um falso negativo significa
que o sistema considerou um caso de baixo risco quando ele, na realidade, exigia atenção.
