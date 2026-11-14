# Análise Crítica — Etapa 3
## AI Factory: Building Intelligent Systems
### Projeto: Assistente ao Expositor — ExpoCatólica 2026

**Site publicado:** https://assistente-expocatolica-2026.streamlit.app  
**Repositório:** https://github.com/peluizmauro-wq/Chat-ExpoCat-lica-PUC

---

## Parte A — Revisitando o desafio

### Grande ideia

Desde o início eu quis trabalhar com um problema que fizesse parte da minha realidade profissional. Por isso escolhi a ExpoCatólica e o relacionamento com os expositores. É uma operação que envolve muitos documentos, regras, prazos, pendências e dúvidas que se repetem durante a preparação do evento.

A grande ideia foi verificar como a inteligência artificial poderia ajudar a organizar esse fluxo e facilitar o acesso às informações.

### Pergunta essencial

**Como a IA pode facilitar o acesso dos expositores às informações da ExpoCatólica e reduzir a dependência da equipe para resolver dúvidas e acompanhar pendências?**

### Desafio

O desafio foi construir um assistente que conseguisse reunir, no mesmo ambiente de conversa, informações dos documentos da feira, dados estruturados de expositores e recursos de análise, sem perder controle de acesso, rastreabilidade e segurança.

### O sistema resolve o desafio?

Na minha avaliação, resolve uma parte importante do problema e comprova que a ideia é viável.

Hoje o sistema está publicado na internet e pode ser acessado por uma URL pública. O usuário consegue fazer perguntas em linguagem natural sobre prazos, montagem, documentação e regras da ExpoCatólica. O assistente também consegue consultar dados estruturados no DuckDB, executar um modelo preditivo e combinar mais de uma ferramenta quando a pergunta exige.

Um exemplo prático foi o teste com a Turismo Peregrino Brasil. Na mesma pergunta, o sistema consultou pendências, informou o prazo do projeto técnico e executou a análise de risco do cenário 3. Isso mostrou, para mim, que o projeto foi além de um FAQ simples.

Ao mesmo tempo, eu não considero o sistema pronto para ser colocado em produção real na ExpoCatólica. Os dados de expositores usados no projeto são fictícios e o modelo preditivo foi treinado com uma base pública de crédito, utilizada apenas como exercício acadêmico. Portanto, a arquitetura já funciona, mas a parte preditiva precisaria ser treinada novamente com dados históricos reais da própria operação.

A publicação no Streamlit foi importante porque tirou o projeto do ambiente local. Passei a testar o sistema do ponto de vista de um usuário que acessa um endereço na internet, e não apenas como alguém executando código no computador.

---

## Parte B — Análise técnica

### O que funcionou bem

#### Integração das diferentes partes do sistema

O principal resultado do projeto foi conseguir juntar várias tecnologias sem obrigar o usuário a saber qual delas está sendo usada.

Se a pergunta é documental, o sistema consulta a base de documentos pelo RAG. Se a pergunta envolve dados de expositor, usa DuckDB. Se envolve o modelo preditivo, chama o modelo de machine learning. Quando a pergunta exige mais de uma dessas partes, o coordenador aciona os agentes necessários e reúne a resposta.

Essa foi uma mudança importante na minha compreensão da disciplina. No começo eu associava muito IA a chatbot e LLM. Ao longo das aulas fui entendendo que um sistema inteligente pode ser formado por diferentes componentes, cada um fazendo a tarefa em que funciona melhor.

#### Modelo preditivo integrado ao chat

Na Aula 5 eu entendi melhor por que machine learning tradicional continua importante para dados estruturados.

Usei o dataset público Statlog German Credit para a parte acadêmica do treinamento. O FLAML selecionou um modelo LightGBM. No conjunto de teste, os resultados foram:

- Accuracy: **0,6200**
- Precision: **0,4298**
- Recall: **0,8167**
- F1-score: **0,5632**
- ROC-AUC: **0,7796**

A métrica que priorizei foi recall. Para o cenário que eu quis simular, considero pior deixar passar sem alerta um caso que mereceria atenção do que gerar alguns alertas adicionais. Essa escolha também me ajudou a entender, na prática, que melhorar uma métrica pode significar aceitar perda em outra.

#### Agentes especializados

Na Aula 6 eu passei a enxergar agente como algo diferente de simplesmente dar outro nome ao chatbot.

No projeto existem dois papéis principais. O Agente Operacional trabalha com documentos, regras e prazos. O Agente de Dados e Risco trabalha com DuckDB e com o modelo preditivo. O coordenador identifica quando a pergunta exige a participação dos dois.

O teste realizado no site publicado confirmou esse funcionamento. Uma única pergunta gerou resposta operacional, consulta de pendências e análise de risco.

#### Observabilidade e testes

O Langfuse me ajudou a entender o que acontece dentro do sistema e não apenas olhar a resposta final. Na Aula 6, os conceitos de trace e span pareciam mais abstratos; depois que consegui visualizar cada etapa da requisição, ficaram mais claros.

Na Aula 7, o Golden Dataset trouxe outra mudança importante. Em vez de simplesmente considerar uma resposta boa porque ela “parece correta”, passei a medir o comportamento do sistema.

Foram usadas 15 perguntas de teste. O resultado final foi:

- **12 de 15 aprovadas**
- taxa de aprovação de **80%**
- Answer Relevancy média de **0,9778**
- Faithfulness média de **0,7096**

Mantive três casos como pontos a rever. Preferi mostrar a limitação encontrada do que ajustar o teste apenas para chegar a 100%.

#### Segurança

Na Etapa 3, com base principalmente na Aula 8, incluí uma camada de segurança antes e depois do processamento.

Na entrada, o sistema verifica tentativas de prompt injection, jailbreak, toxicidade, tópicos proibidos e dados pessoais. Na saída, há proteção para PII, secrets e informações internas.

Os testes automatizados bloquearam três tipos de ataque e também verificaram que uma pergunta normal continua funcionando.

Depois disso fiz o mesmo teste diretamente na aplicação publicada. A pergunta tentando mandar o sistema ignorar as regras e revelar o prompt interno foi recusada e identificada como bloqueio de segurança.

### O que ainda funciona de forma limitada

#### O modelo preditivo não representa a realidade dos expositores

Esta é, para mim, a principal limitação do projeto.

O dataset German Credit serviu para aprender e demonstrar o processo de classificação, AutoML e integração do modelo ao chat. Porém, ele não representa o comportamento de expositores da ExpoCatólica.

Por isso a própria aplicação deixa claro que a previsão é uma demonstração acadêmica. Para usar essa camada de forma real, seria necessário construir uma base histórica própria da ExpoCatólica.

#### O RAG publicado usa TF-IDF como fallback

No ambiente publicado, o RAG está funcionando em modo TF-IDF local. Isso tornou o deploy mais leve e previsível, mas a busca é menos semântica do que seria com embeddings e uma base vetorial completa.

Na prática, perguntas que usam palavras muito diferentes das encontradas nos documentos podem recuperar conteúdos menos precisos.

#### O site público está funcionando sem uma LLM externa

A aplicação publicada funciona sem chave de LLM. Isso foi útil porque permitiu manter o sistema disponível sem depender de custo de API.

Por outro lado, respostas mais abertas e sínteses mais complexas ficam limitadas. Em uma versão de produção, eu utilizaria uma LLM externa configurada por variável de ambiente e manteria o modo local apenas como fallback.

#### Os guardrails atuais são baseados principalmente em regras

A camada de segurança passou nos ataques que testei e é fácil de entender e auditar. Porém, ataques escritos de maneiras mais sofisticadas podem não seguir os padrões previstos.

Em uma versão mais madura, eu combinaria essas regras com ferramentas especializadas, como LLM Guard e Presidio, além de testes adicionais.

#### A avaliação de Faithfulness pode evoluir

A avaliação atual é reproduzível e funciona sem depender de outra API, o que foi útil no projeto. Mesmo assim, uma métrica mais semântica teria melhor capacidade de reconhecer respostas corretas que usam palavras diferentes do texto esperado.

Essa é uma das razões pelas quais eu considero interessante, futuramente, usar LLM-as-a-judge junto com a avaliação atual.

### Limitações conhecidas

Hoje eu considero como principais limites do protótipo:

- os dados de expositores são fictícios;
- o modelo preditivo usa um dataset de outro domínio;
- o RAG publicado trabalha com TF-IDF;
- o deploy atual não utiliza LLM externa;
- os guardrails são majoritariamente determinísticos;
- a avaliação semântica ainda pode ser ampliada;
- o sistema não está integrado aos sistemas reais da Promocat;
- o perfil de expositor ainda é demonstrativo e não representa uma autenticação real.

---

## Parte C — Visão de futuro

### 1. Criar uma base histórica real da ExpoCatólica

**O que eu mudaria:** substituiria o dataset usado no exercício por dados históricos reais e anonimizados da operação.

**Tecnologias:** ETL, PostgreSQL ou DuckDB, pandas, FLAML/LightGBM e acompanhamento das métricas do modelo.

**Impacto esperado:** permitir que a equipe identifique antecipadamente expositores que precisam de atenção por atraso de documentos, pagamentos ou outras pendências.

### 2. Evoluir o RAG para uma base vetorial de produção

**O que eu mudaria:** passaria a trabalhar com embeddings, metadados e documentos separados por edição da feira.

**Tecnologias:** ChromaDB ou outra base vetorial, embeddings, reranking e chunking mais bem estruturado.

**Impacto esperado:** melhorar a recuperação quando o expositor faz a pergunta usando palavras diferentes das encontradas no manual e evitar mistura entre regras de anos diferentes.

### 3. Integrar o assistente aos sistemas reais

**O que eu mudaria:** substituiria os CSVs demonstrativos por integrações reais e criaria autenticação efetiva para expositores e equipe.

**Tecnologias:** APIs, PostgreSQL, autenticação, perfis de acesso e logs de auditoria.

**Impacto esperado:** permitir ao expositor consultar seus próprios documentos, estande, solicitações e pendências, sem depender da equipe para buscas simples e sem acessar dados de terceiros.

### 4. Ampliar a segurança

**O que eu mudaria:** manteria os guardrails atuais e acrescentaria uma camada semântica de segurança.

**Tecnologias:** LLM Guard, Presidio, classificadores de conteúdo, rate limiting e monitoramento no Langfuse.

**Impacto esperado:** maior proteção contra ataques menos óbvios e maior controle sobre dados pessoais.

### 5. Levar o assistente para outros canais

**O que eu mudaria:** usaria a mesma base de inteligência em canais que já fazem parte da rotina do expositor.

**Tecnologias:** integração por API com WhatsApp, e-mail e portal do expositor.

**Impacto esperado:** reduzir a dispersão do atendimento e transformar o assistente em uma ferramenta de operação, não apenas em um site isolado.

---

## Reflexão final

O que mais mudou durante a disciplina foi a minha visão sobre o que significa construir um sistema de inteligência artificial.

No começo, minha referência estava muito ligada ao chatbot. Ao longo do projeto fui percebendo que a resposta que aparece na tela é apenas uma parte. Existem dados, recuperação de documentos, modelos preditivos, agentes, observabilidade, métricas, testes, segurança e publicação.

Essa experiência se conecta diretamente com minha atuação profissional porque a ExpoCatólica faz parte da minha realidade. O problema escolhido não foi criado apenas para cumprir a atividade. Existe, de fato, uma operação com muitos expositores, documentos, regras, prazos e dúvidas recorrentes.

O projeto ainda é um protótipo, mas me mostrou de forma prática que parte desse atendimento pode evoluir para um serviço digital inteligente.

Se eu começasse novamente, faria duas escolhas diferentes desde o início.

A primeira seria organizar uma base histórica própria da ExpoCatólica, mesmo que pequena e anonimizada. Isso permitiria trabalhar a parte preditiva com dados realmente relacionados ao problema.

A segunda seria pensar em testes, observabilidade, segurança e deploy desde a primeira versão. No projeto, essas camadas foram entrando conforme as etapas avançaram. Hoje eu entendo que elas fazem parte da arquitetura do sistema desde o começo.

Para mim, esse foi o principal resultado da disciplina: sair de uma ideia de chatbot e chegar a um sistema publicado, testado e protegido, ainda com limitações, mas já capaz de mostrar uma aplicação real para um problema da minha atividade profissional.

---

## Referências das aulas

- **Aula 5:** machine learning tradicional, classificação, AutoML, FLAML e métricas.
- **Aula 6:** agentes, ferramentas, coordenação, traces e spans.
- **Aula 7:** Golden Dataset, Answer Relevancy, Faithfulness, RAGAS/DeepEval e LLM-as-a-judge.
- **Aula 8:** guardrails, prompt injection, jailbreak, PII, segurança, privacidade e publicação.
