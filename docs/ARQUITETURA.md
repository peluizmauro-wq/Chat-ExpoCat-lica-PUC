# Arquitetura técnica

O protótipo foi separado em quatro responsabilidades:

1. `app.py`: interface Streamlit, histórico e streaming.
2. `database.py`: carregamento dos CSVs no DuckDB e consultas seguras.
3. `rag_engine.py`: chunking, indexação e recuperação semântica.
4. `assistant_engine.py`: roteamento entre dados e RAG, aplicação do system prompt e integração com LLM.

## Decisão de projeto
Perguntas sobre estande, metragem e pendências usam dados estruturados.
Perguntas normativas e operacionais usam RAG.

## RAG
O backend principal é ChromaDB com embeddings SentenceTransformers. Há fallback TF-IDF para permitir execução local quando o modelo de embeddings não estiver disponível.

## Proteção
Não há senhas ou chaves no código. A integração LLM lê a chave apenas do `.env`.
