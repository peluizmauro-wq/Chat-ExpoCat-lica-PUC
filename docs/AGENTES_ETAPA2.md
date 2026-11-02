# Agentes da Etapa 2

A implementação usa uma arquitetura multiagente equivalente ao conceito estudado na Aula 6.

## 1. Agente Operacional ExpoCatólica

**Papel:** especialista em regras, prazos e operação do evento.

**Ferramentas:**
- RAG;
- ChromaDB/SentenceTransformers ou fallback TF-IDF;
- Manual do Expositor;
- Regulamento Geral;
- Normas do Pro Magno.

**Exemplo de pergunta:**
`Use o Agente Operacional e informe o prazo do projeto técnico.`

## 2. Agente de Dados e Risco

**Papel:** consultar dados estruturados e executar a demonstração de classificação preditiva.

**Ferramentas:**
- DuckDB;
- tabelas de expositores, estandes e pendências;
- modelo de ML treinado com FLAML.

**Exemplo de pergunta:**
`Use o Agente de Dados e Risco e analise o risco do cenário 3.`

## 3. Coordenador Multiagente

Quando uma pergunta mistura camadas, o coordenador aciona os dois agentes e apresenta os resultados juntos.

**Pergunta recomendada para o vídeo:**

`Faça uma análise integrada: consulte as pendências da Turismo Peregrino Brasil, analise o risco do cenário 3 e informe o prazo do projeto técnico.`

Esta pergunta exige:
1. consulta ao DuckDB;
2. execução do modelo ML;
3. recuperação documental no RAG;
4. coordenação das respostas no mesmo chat.

## Observação

A implementação foi mantida transparente e simples para fins acadêmicos. Em uma próxima evolução, o mesmo desenho pode ser conectado diretamente a um framework como CrewAI, sem alterar os papéis, ferramentas e tarefas já definidos.
