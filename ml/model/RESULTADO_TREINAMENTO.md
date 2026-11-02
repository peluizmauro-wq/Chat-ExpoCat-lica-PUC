# Resultado do treinamento ML

Dataset: Statlog (German Credit Data) - UCI 144
Registros: 1000
Divisão: 700 treino / 100 validação / 200 teste
Modelo selecionado automaticamente pelo FLAML: lgbm
Threshold escolhido no conjunto de validação: 0.13
Critério: minimizar custo: 5 x falso negativo + 1 x falso positivo

## Métricas no conjunto de teste

- Accuracy: 0.62
- Precision: 0.4298
- Recall: 0.8167
- F1-score: 0.5632
- ROC-AUC: 0.7796

## Interpretação para o projeto

Este modelo é uma demonstração acadêmica por analogia. A base pública classifica risco de crédito.
No projeto ExpoCatólica, usamos a mesma lógica de classificação binária para demonstrar como
uma futura base histórica de expositores poderia apoiar alertas preventivos.

A métrica que destacamos é o recall. A própria base UCI atribui custo maior ao erro de considerar
como bom risco um caso que, na realidade, é mau risco. Por analogia, no projeto ExpoCatólica,
queremos reduzir a chance de deixar passar sem alerta um expositor que precisaria de atenção.
