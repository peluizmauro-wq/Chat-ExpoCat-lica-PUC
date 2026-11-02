# Relatório Técnico — Etapa 2
## AI Factory: Building Intelligent Systems
### Projeto: Assistente ao Expositor da ExpoCatólica 2026

Nesta segunda etapa eu procurei evoluir o projeto que já havia construído na Etapa 1. Antes, o sistema conseguia responder perguntas com RAG, consultar dados estruturados em DuckDB e manter uma conversa com o usuário. Agora a proposta foi acrescentar três capacidades que eu considerei importantes: fazer uma previsão com machine learning, dividir tarefas entre agentes especializados e acompanhar o que acontece dentro do sistema com observabilidade e testes.

## 1. Modelo preditivo

Na Aula 5 eu entendi melhor que nem todo problema de inteligência artificial precisa ser resolvido com uma LLM. Quando temos dados estruturados e queremos prever uma classe, algoritmos tradicionais de machine learning podem ser mais adequados. Por isso escolhi trabalhar com classificação binária de risco.

Usei o dataset público **Statlog (German Credit Data)**, disponível no UCI Machine Learning Repository. A base possui 1.000 registros e 20 atributos. A variável-alvo separa casos de bom e mau risco. O uso no meu projeto é por analogia: eu não considero que risco de crédito seja igual ao comportamento de um expositor. O objetivo foi experimentar uma lógica que, no futuro, poderia ser treinada com dados históricos reais da ExpoCatólica para identificar expositores com maior risco de atraso em documentos, pagamentos ou outras pendências.

O treinamento foi feito com **FLAML**, ferramenta apresentada na Aula 5 como uma alternativa de AutoML. O que mais me chamou atenção foi entender que AutoML não elimina a necessidade de interpretar o problema. Ele ajuda a testar modelos e parâmetros, mas ainda precisamos escolher o que significa um bom resultado.

O FLAML selecionou um modelo LightGBM. A divisão utilizada foi de 700 registros para treino, 100 para validação e 200 para teste. As métricas finais foram: accuracy de **0,6200**, precision de **0,4298**, recall de **0,8167**, F1-score de **0,5632** e ROC-AUC de **0,7796**.

A métrica que considero mais importante para este contexto é o **recall**. Na Aula 5 eu aprendi que essa métrica merece mais atenção quando o falso negativo é o erro mais grave. No meu caso, considero pior deixar passar sem alerta um expositor que realmente precisaria de atenção do que gerar alguns alertas preventivos a mais. Por isso o sistema também utiliza um limite de decisão ajustado em validação, em vez de aceitar automaticamente o corte padrão de 50%.

## 2. Agentes especializados

Na Aula 6 eu entendi que um agente não é apenas um chatbot com outro nome. Ele precisa ter um papel, um objetivo e ferramentas para executar tarefas. A partir disso criei dois agentes especializados e um coordenador.

O **Agente Operacional ExpoCatólica** é responsável por regras, prazos, montagem, desmontagem e normas do evento. Ele utiliza a camada de RAG e consulta o Manual do Expositor, o Regulamento Geral e as normas do Pro Magno.

O **Agente de Dados e Risco** consulta o DuckDB, os dados de expositores, estandes e pendências e também pode acionar o modelo preditivo treinado com FLAML.

Além deles, existe um **Coordenador Multiagente**, que identifica quando uma pergunta exige mais de uma camada. Por exemplo, em uma pergunta que pede as pendências de um expositor, uma análise de risco e o prazo de um documento, o coordenador aciona o agente de dados e risco e também o agente operacional.

Essa parte me ajudou a entender na prática o padrão estudado na Aula 6, em que o sistema precisa decidir qual ferramenta usar, observar o resultado e continuar a tarefa até chegar a uma resposta.

## 3. Observabilidade com Langfuse

Outro aprendizado importante da Aula 6 foi o conceito de observabilidade. Antes eu via apenas a resposta final do chat. Com o Langfuse passei a entender que também é possível acompanhar a trajetória da requisição.

Integrei o projeto ao **Langfuse Cloud** e gerei pelo menos cinco traces diferentes. Eles representam consultas ao RAG, ao DuckDB, ao modelo preditivo e aos agentes. Dentro desses traces também existem etapas internas, os chamados spans, que permitem identificar qual parte do sistema foi utilizada.

Isso é útil porque, se uma resposta estiver errada ou lenta, não precisamos analisar apenas o resultado final. Podemos verificar se o problema aconteceu na recuperação dos documentos, na consulta ao banco, na previsão ou na coordenação dos agentes.

## 4. Golden Dataset e avaliação

Na Aula 7 eu aprendi que sistemas com IA generativa não devem ser avaliados apenas pela impressão de que a resposta “parece boa”. Por isso criei um **golden dataset com 15 perguntas**, incluindo casos fáceis, intermediários, difíceis, ambíguos e fora do escopo.

As avaliações usam duas ideias principais apresentadas na aula. A primeira é **Answer Relevancy**, que verifica se a resposta realmente atende à pergunta. A segunda é **Faithfulness**, que verifica se a resposta permanece fiel às evidências disponíveis e evita inventar informações.

A avaliação foi automatizada no GitHub Actions e foi construída como uma alternativa equivalente ao processo apresentado com DeepEval/RAGAS. O objetivo principal foi tornar o teste reproduzível e permitir que futuras mudanças no sistema sejam avaliadas novamente sem depender apenas de uma conferência manual.

No teste final foram avaliadas **15 perguntas**. **12 foram aprovadas**, resultando em uma taxa de aprovação de **80%**. A média de **Answer Relevancy foi 0,9778**, mostrando que, de modo geral, as respostas atenderam muito bem ao que foi perguntado. A média de **Faithfulness foi 0,7096**, indicando que a maior parte das respostas permaneceu ancorada nas evidências disponíveis.

Três casos ficaram marcados como **REVER**. Em vez de esconder esses resultados, considerei isso importante para a análise, porque a Aula 7 mostra que os testes também servem para descobrir onde o sistema ainda precisa melhorar. Os pontos identificados envolvem principalmente respostas do modelo preditivo e tarefas compostas, nas quais a resposta inclui explicações e coordenação que a métrica determinística de fidelidade nem sempre consegue relacionar diretamente às evidências.

Os resultados detalhados ficam salvos em `avaliacao/resultados/RESULTADO_AVALIACAO.md`. Como melhoria futura, eu ajustaria a avaliação de faithfulness com um avaliador semântico/LLM-as-a-judge e ampliaria o golden dataset.

## 5. O que aprendi

O principal aprendizado desta etapa foi perceber que um sistema de IA não é apenas o modelo que responde. Ele é formado por várias camadas que precisam trabalhar juntas.

O machine learning acrescentou uma capacidade preditiva. Os agentes permitiram distribuir responsabilidades. O Langfuse tornou o funcionamento interno mais visível. E o golden dataset criou uma forma mais objetiva de testar qualidade.

Também percebi que aumentar uma métrica pode reduzir outra. O aumento do recall do modelo, por exemplo, veio acompanhado de uma precision menor. Isso me ajudou a entender melhor que não existe uma métrica isolada que determine se um sistema é bom. A escolha depende do problema e do custo de cada erro.

Para uma próxima evolução, eu gostaria de substituir o dataset público por um histórico real de expositores da ExpoCatólica, aumentar o golden dataset e incluir avaliações com LLM-as-a-judge, mantendo sempre controle de acesso e cuidado com dados pessoais.

## Referências das aulas utilizadas

- **Aula 5 — IA preditiva e AutoML:** classificação, treino/teste, FLAML, matriz de confusão e métricas como accuracy, precision, recall, F1 e ROC-AUC.
- **Aula 6 — Agentes autônomos e observabilidade:** agentes, ferramentas, padrão ReAct, sistemas multiagente, traces e spans.
- **Aula 7 — Testes e avaliação de sistemas de IA:** Faithfulness, Answer Relevancy, golden dataset, RAGAS, DeepEval e LLM-as-a-judge.
- **UCI Machine Learning Repository:** Statlog (German Credit Data), dataset 144.
