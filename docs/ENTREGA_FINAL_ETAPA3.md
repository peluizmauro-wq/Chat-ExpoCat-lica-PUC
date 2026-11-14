# Entrega Final — Etapa 3
## AI Factory: Building Intelligent Systems
### Fábio Castro — Assistente ao Expositor ExpoCatólica 2026

Este arquivo reúne os itens da entrega final, exceto o vídeo, que será enviado separadamente.

## 1. Site público

**Assistente ao Expositor — ExpoCatólica 2026**  
https://assistente-expocatolica-2026.streamlit.app

Status: publicado e validado em ambiente público.

## 2. Repositório do projeto

https://github.com/peluizmauro-wq/Chat-ExpoCat-lica-PUC

O repositório é público. Por isso, conforme a orientação da atividade, não é necessário enviar ZIP adicional do código.

## 3. Documento de análise crítica

Arquivo principal para entrega:

**Analise_Critica_Etapa3_AI_Factory_Fabio_Castro_FINAL.docx**

Versão em Markdown no repositório:

https://github.com/peluizmauro-wq/Chat-ExpoCat-lica-PUC/blob/main/docs/ANALISE_CRITICA_ETAPA3.md

## 4. Evidências de segurança

Resultado dos guardrails:

https://github.com/peluizmauro-wq/Chat-ExpoCat-lica-PUC/blob/main/docs/RESULTADO_SEGURANCA_ETAPA3.md

Workflow automatizado aprovado:

https://github.com/peluizmauro-wq/Chat-ExpoCat-lica-PUC/actions/runs/43610087120

Validação inclui:
- prompt injection bloqueado;
- jailbreak bloqueado;
- tópico proibido bloqueado;
- pergunta legítima permitida;
- anonimização de e-mail e CPF;
- proteção de secrets e PII na saída.

## 5. Evidência do deploy

https://github.com/peluizmauro-wq/Chat-ExpoCat-lica-PUC/blob/main/docs/VALIDACAO_DEPLOY_ETAPA3.md

O teste público confirmou:
- Agente Operacional;
- Agente de Dados e Risco;
- DuckDB;
- modelo preditivo;
- coordenação multiagente;
- bloqueio de prompt injection.

## 6. README profissional

https://github.com/peluizmauro-wq/Chat-ExpoCat-lica-PUC/blob/main/README.md

Inclui:
- descrição do desafio;
- arquitetura;
- stack;
- instruções de execução;
- segurança;
- avaliação;
- limitações;
- evidências;
- URL pública.

## 7. Arquivos exigidos no repositório

### Dependências pinadas

`requirements.txt`

https://github.com/peluizmauro-wq/Chat-ExpoCat-lica-PUC/blob/main/requirements.txt

### Exemplo de variáveis de ambiente

`.env.example`

https://github.com/peluizmauro-wq/Chat-ExpoCat-lica-PUC/blob/main/.env.example

Nenhum secret real está versionado.

### Golden Dataset

`avaliacao/golden_dataset.json`

https://github.com/peluizmauro-wq/Chat-ExpoCat-lica-PUC/blob/main/avaliacao/golden_dataset.json

### Resultado dos testes

https://github.com/peluizmauro-wq/Chat-ExpoCat-lica-PUC/blob/main/avaliacao/resultados/RESULTADO_AVALIACAO.md

Resultado:
- 15 perguntas;
- 12 aprovadas;
- 80% de aprovação;
- Answer Relevancy: 0,9778;
- Faithfulness: 0,7096.

## 8. Evidências das etapas anteriores mantidas no projeto

### Machine Learning

https://github.com/peluizmauro-wq/Chat-ExpoCat-lica-PUC/blob/main/ml/model/RESULTADO_TREINAMENTO.md

### Agentes

https://github.com/peluizmauro-wq/Chat-ExpoCat-lica-PUC/blob/main/docs/AGENTES_ETAPA2.md

### Observabilidade

https://github.com/peluizmauro-wq/Chat-ExpoCat-lica-PUC/blob/main/docs/OBSERVABILIDADE_LANGFUSE.md

## 9. Diretórios principais

```text
/
├── app.py
├── assistant_engine.py
├── security.py
├── agents.py
├── database.py
├── rag_engine.py
├── ml_engine.py
├── observability.py
├── requirements.txt
├── .env.example
├── README.md
│
├── dados/
│   ├── expositores.csv
│   ├── estandes.csv
│   └── pendencias.csv
│
├── documentos/
│   └── base documental do RAG
│
├── ml/
│   ├── dados/
│   └── model/
│
├── avaliacao/
│   ├── golden_dataset.json
│   └── resultados/
│
├── testes/
│   ├── test_agents.py
│   ├── test_security.py
│   └── test_deploy_smoke.py
│
├── docs/
│   ├── ANALISE_CRITICA_ETAPA3.md
│   ├── RESULTADO_SEGURANCA_ETAPA3.md
│   ├── VALIDACAO_DEPLOY_ETAPA3.md
│   ├── DEPLOY_ETAPA3.md
│   ├── AGENTES_ETAPA2.md
│   └── OBSERVABILIDADE_LANGFUSE.md
│
└── .github/workflows/
    ├── test-security.yml
    ├── deploy-smoke.yml
    ├── test-agents.yml
    └── evaluate-golden.yml
```

## 10. Capturas de tela

As capturas reais de:
- funcionamento multiagente no site público;
- bloqueio do ataque de prompt injection;

estão incorporadas no documento Word final de análise crítica e registradas na documentação de validação.

## 11. Vídeo

O vídeo final não faz parte deste pacote porque será enviado/publicado separadamente, conforme definido na entrega.

---

## Checklist final

- [x] Código completo e organizado
- [x] README profissional
- [x] Arquitetura documentada
- [x] Stack documentada
- [x] Execução local documentada
- [x] Limitações documentadas
- [x] requirements.txt com versões pinadas
- [x] .env.example
- [x] Golden Dataset
- [x] Testes automatizados
- [x] Pipeline de segurança
- [x] PII anonimizada
- [x] Pelo menos 3 ataques bloqueados
- [x] URL pública funcional
- [x] Secrets fora do repositório
- [x] Documento de análise crítica
- [x] Propostas de evolução
- [x] Reflexão pessoal
- [x] Evidências de funcionamento
- [ ] Vídeo final — enviado separadamente
