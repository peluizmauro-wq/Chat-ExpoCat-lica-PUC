# Observabilidade — Langfuse

A Etapa 2 adiciona observabilidade ao Assistente ao Expositor.

## O que é registrado

Cada pergunta pode gerar um trace principal com etapas internas, incluindo:

- roteamento da pergunta;
- recuperação RAG;
- consulta a dados estruturados;
- execução do modelo preditivo;
- atuação dos agentes;
- geração de resposta;
- latência total.

Quando uma LLM externa estiver configurada, a chamada também poderá ser registrada como geração com modelo, tokens e custo.

## Configuração segura

As credenciais NÃO ficam no repositório.

Variáveis usadas:

```env
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

Se as chaves não estiverem configuradas, a aplicação continua funcionando normalmente e a instrumentação fica desativada.

## Meta da atividade

Gerar pelo menos 5 traces reais para registrar no relatório e no vídeo.
