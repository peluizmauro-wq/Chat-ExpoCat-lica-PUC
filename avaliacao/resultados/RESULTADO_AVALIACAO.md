# Resultado dos testes do Golden Dataset

- Total de perguntas: **15**
- Aprovadas: **12**
- Taxa de aprovação: **80.0%**
- Answer Relevancy média: **0.9778**
- Faithfulness média: **0.7096**

## Casos

| ID | Categoria | Tipo | Relevancy | Faithfulness | Resultado |
|---|---|---|---:|---:|---|
| Q01 | facil | rag | 1.00 | 1.00 | OK |
| Q02 | facil | rag | 1.00 | 1.00 | OK |
| Q03 | facil | rag | 1.00 | 0.86 | OK |
| Q04 | facil | dados | 1.00 | 0.80 | OK |
| Q05 | facil | ml | 1.00 | 0.40 | REVER |
| Q06 | intermediaria | rag | 1.00 | 0.65 | OK |
| Q07 | intermediaria | rag | 1.00 | 1.00 | OK |
| Q08 | intermediaria | dados | 1.00 | 0.48 | OK |
| Q09 | intermediaria | agente | 1.00 | 0.56 | OK |
| Q10 | dificil | multiagente | 1.00 | 0.33 | REVER |
| Q11 | dificil | rag | 1.00 | 0.30 | REVER |
| Q12 | dificil | seguranca | 1.00 | 0.88 | OK |
| Q13 | ambigua | rag | 0.67 | 0.56 | OK |
| Q14 | ambigua | rag | 1.00 | 1.00 | OK |
| Q15 | fora_do_escopo | rag | 1.00 | 0.83 | OK |

## Leitura dos resultados

Os testes ajudam a separar dois problemas diferentes. Answer Relevancy mostra se a resposta realmente atende à pergunta. Faithfulness verifica se a resposta permanece ancorada nas evidências disponíveis, reduzindo risco de invenção.

Os casos marcados como REVER devem orientar melhorias em prompt, roteamento, recuperação RAG ou regras de resposta. Esse uso corresponde à lógica estudada na Aula 7 para avaliar sistemas RAG.