# Resultado dos testes do Golden Dataset

- Total de perguntas: **15**
- Aprovadas: **8**
- Taxa de aprovação: **53.3%**
- Answer Relevancy média: **0.5867**
- Faithfulness média: **0.6917**

## Casos

| ID | Categoria | Tipo | Relevancy | Faithfulness | Resultado |
|---|---|---|---:|---:|---|
| Q01 | facil | rag | 0.40 | 0.82 | REVER |
| Q02 | facil | rag | 0.17 | 0.87 | REVER |
| Q03 | facil | rag | 0.67 | 0.91 | OK |
| Q04 | facil | dados | 1.00 | 0.80 | OK |
| Q05 | facil | ml | 1.00 | 0.31 | REVER |
| Q06 | intermediaria | rag | 1.00 | 0.58 | OK |
| Q07 | intermediaria | rag | 0.67 | 0.95 | OK |
| Q08 | intermediaria | dados | 1.00 | 0.48 | OK |
| Q09 | intermediaria | agente | 0.50 | 1.00 | OK |
| Q10 | dificil | multiagente | 0.80 | 0.30 | REVER |
| Q11 | dificil | rag | 0.60 | 0.54 | OK |
| Q12 | dificil | seguranca | 0.00 | 0.06 | REVER |
| Q13 | ambigua | rag | 0.00 | 0.91 | REVER |
| Q14 | ambigua | rag | 1.00 | 0.92 | OK |
| Q15 | fora_do_escopo | rag | 0.00 | 0.93 | REVER |

## Leitura dos resultados

Os testes ajudam a separar dois problemas diferentes. Answer Relevancy mostra se a resposta realmente atende à pergunta. Faithfulness verifica se a resposta permanece ancorada nas evidências disponíveis, reduzindo risco de invenção.

Os casos marcados como REVER devem orientar melhorias em prompt, roteamento, recuperação RAG ou regras de resposta. Esse uso corresponde à lógica estudada na Aula 7 para avaliar sistemas RAG.