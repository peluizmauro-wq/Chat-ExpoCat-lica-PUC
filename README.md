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
