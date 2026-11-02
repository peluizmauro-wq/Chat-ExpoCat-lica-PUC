# Roteiro do vídeo — Etapa 2
## Duração alvo: 4 minutos

### 0:00–0:30 — Introdução
“Na Etapa 1 eu construí um Assistente ao Expositor da ExpoCatólica com chat, RAG e dados estruturados. Nesta segunda etapa eu acrescentei machine learning, agentes especializados, observabilidade e testes.”

### 0:30–1:15 — Machine Learning
Mostrar o arquivo `ml/model/RESULTADO_TREINAMENTO.md`.

Fala:
“Na Aula 5 eu aprendi que machine learning tradicional continua sendo útil quando o problema envolve dados estruturados e classificação. Eu usei um dataset público da UCI com mil registros. O FLAML escolheu automaticamente um modelo LightGBM. O resultado que eu priorizei foi recall de 81,67%, porque no meu contexto eu considero pior deixar passar um caso de risco sem alerta.”

Mostrar rapidamente as métricas.

### 1:15–2:05 — Agentes
Mostrar `docs/AGENTES_ETAPA2.md` ou o chat.

Fala:
“Na Aula 6 eu entendi que um agente precisa ter papel e ferramentas. Criei um Agente Operacional, que consulta documentos via RAG, e um Agente de Dados e Risco, que consulta DuckDB e o modelo de ML. Um coordenador chama os dois quando a pergunta exige uma tarefa composta.”

Usar a pergunta:
“Faça uma análise integrada: consulte as pendências da Turismo Peregrino Brasil, analise o risco do cenário 3 e informe o prazo do projeto técnico.”

### 2:05–2:45 — Langfuse
Abrir Langfuse → Tracing.

Fala:
“O Langfuse me permitiu ver o que acontece dentro do sistema. Na Aula 6 eu aprendi que o trace representa a jornada completa da requisição e os spans mostram as etapas internas. Aqui eu consigo ver os cinco rastreamentos que gerei.”

Mostrar os 5 traces e abrir um deles.

### 2:45–3:25 — Golden Dataset
Abrir:
`avaliacao/golden_dataset.json`
e depois:
`avaliacao/resultados/RESULTADO_AVALIACAO.md`.

Fala:
“Na Aula 7 eu aprendi que não basta uma resposta parecer boa. Criei um golden dataset com 15 perguntas, incluindo perguntas fáceis, difíceis, ambíguas e fora do escopo. Avaliei principalmente relevância da resposta e fidelidade às evidências.”

### 3:25–4:00 — Conclusão
“Esta etapa me ajudou a perceber que um sistema de IA não é só uma LLM. Ele envolve dados, previsão, agentes, monitoramento e avaliação. Também aprendi que não existe uma métrica perfeita. No modelo de risco, por exemplo, aumentar o recall fez a precision diminuir, e precisei decidir qual erro era mais importante evitar no meu contexto.”
