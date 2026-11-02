# Assistente ao Expositor — ExpoCatólica 2026
## AI Factory: Building Intelligent Systems — Etapa 1, Item 2

Protótipo funcional de um assistente inteligente para apoiar expositores da ExpoCatólica 2026.  
O sistema combina **interface de chat**, **RAG sobre documentos operacionais**, **dados estruturados em DuckDB** e **integração opcional com LLM**.

## O que o sistema faz

- Responde perguntas sobre prazos, montagem, credenciamento, comercialização, segurança e uso do pavilhão.
- Recupera contexto de pelo menos 3 documentos do domínio.
- Consulta 3 tabelas relacionadas: `expositores`, `estandes` e `pendencias`.
- Exibe as fontes usadas em cada resposta.
- Mantém histórico da conversa durante a sessão.
- Apresenta respostas com streaming visual.
- Possui perfil **Organização** e perfil **Expositor**, com bloqueio de consultas estruturadas de outro expositor.
- Funciona sem chave de API em modo local e pode usar OpenAI quando a chave for configurada.

## Arquitetura

```text
Streamlit (chat)
      |
      +--> Detector de intenção
              |
              +--> Dados estruturados --> DuckDB --> CSVs relacionados
              |
              +--> Pergunta documental --> RAG --> ChromaDB
                                            |
                                            +--> LLM (se configurada)
                                            +--> resposta local (fallback)
```

O pipeline tenta utilizar **ChromaDB + SentenceTransformers**. Se o ambiente não conseguir carregar o modelo de embeddings, o protótipo ativa automaticamente um mecanismo local de recuperação por **TF-IDF**.

## Como executar

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

### Sem chave de API

Selecione **Local (sem API)** na barra lateral. O RAG e as consultas DuckDB continuam funcionando.

### Com LLM

Copie `.env.example` para `.env` e configure:

```env
OPENAI_API_KEY=sua_chave
OPENAI_MODEL=gpt-4.1-mini
```

Nunca publique o arquivo `.env`.

## Perguntas para demonstração

### RAG
1. `Quais são as datas e horários de montagem?`
2. `Até quando posso solicitar energia adicional e hidráulica?`
3. `Posso compartilhar meu estande com outra marca?`

### Dados estruturados
1. `Qual é o estande e a metragem da Editora Caminho Novo?`
2. `Quais pendências estão abertas para a Turismo Peregrino Brasil?`

## Estrutura

- `app.py`: interface Streamlit
- `assistant_engine.py`: roteamento, LLM e respostas
- `database.py`: DuckDB e consultas estruturadas
- `rag_engine.py`: indexação e recuperação
- `dados/`: 3 tabelas CSV relacionadas
- `documentos/`: base documental do RAG
- `docs/`: arquitetura, perguntas e roteiro de vídeo
- `testes/`: teste de integridade

## Segurança

- Chaves somente via variável de ambiente.
- `.env` ignorado pelo Git.
- Consultas SQL definidas e parametrizadas.
- Perfil Expositor não consulta dados estruturados de outro expositor.
- Casos sem base suficiente são encaminhados para confirmação com a organização/CAEX.

## Observação acadêmica

Os dados de expositores deste repositório são **fictícios** e foram criados exclusivamente para a atividade acadêmica.


---

## Etapa 2 — Machine Learning preditivo

Foi adicionada uma camada de Machine Learning ao Assistente ao Expositor.

- **Dataset:** Statlog (German Credit Data), UCI Machine Learning Repository, dataset 144.
- **Tarefa:** classificação binária de risco.
- **Registros:** 1.000.
- **Divisão:** 700 treino, 100 validação e 200 teste.
- **AutoML:** FLAML 2.7.0.
- **Modelo selecionado automaticamente:** LightGBM.
- **Threshold:** escolhido no conjunto de validação com custo maior para falsos negativos.
- **Integração:** perguntas em linguagem natural no mesmo chat.

### Métricas do teste final

- Accuracy: **0,6200**
- Precision: **0,4298**
- Recall: **0,8167**
- F1-score: **0,5632**
- ROC-AUC: **0,7796**

Neste projeto, o **recall** é a métrica priorizada. A lógica é preventiva: é mais problemático deixar passar sem alerta um caso realmente arriscado do que gerar alguns alertas adicionais. O uso do dataset é acadêmico e por analogia; o modelo não avalia expositores reais.

Exemplos no chat:

```text
Mostre os cenários do modelo preditivo.
Analise o risco do cenário 3.
```


---

## Etapa 2 — Agentes especializados

O assistente agora possui dois agentes especializados e um coordenador:

1. **Agente Operacional ExpoCatólica**
   - consulta o RAG;
   - usa Manual do Expositor, Regulamento e normas do Pro Magno;
   - responde sobre prazos, montagem, desmontagem, credenciamento e regras.

2. **Agente de Dados e Risco**
   - consulta o DuckDB;
   - lê dados demonstrativos de expositores, estandes e pendências;
   - executa o modelo preditivo treinado com FLAML.

3. **Coordenador Multiagente**
   - identifica tarefas que exigem mais de uma camada;
   - aciona os dois agentes;
   - combina o resultado no mesmo chat.

### Pergunta recomendada para demonstrar os agentes

```text
Faça uma análise integrada: consulte as pendências da Turismo Peregrino Brasil,
analise o risco do cenário 3 e informe o prazo do projeto técnico.
```

Essa pergunta força o sistema a usar DuckDB + ML + RAG em uma única tarefa coordenada.

A implementação é uma orquestração multiagente equivalente, construída de forma transparente para fins acadêmicos. Os papéis, ferramentas e tarefas seguem o mesmo conceito apresentado em frameworks como CrewAI.
