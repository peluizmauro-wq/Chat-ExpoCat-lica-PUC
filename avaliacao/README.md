# Golden Dataset e avaliação

Foram criadas **15 perguntas** para testar o Assistente ao Expositor.

A distribuição inclui:
- 5 perguntas fáceis;
- 4 intermediárias;
- 3 difíceis;
- 2 ambíguas;
- 1 fora do escopo.

As duas métricas usadas são:
- **Answer Relevancy:** se a resposta atende de fato à pergunta;
- **Faithfulness:** se a resposta permanece ancorada nas evidências disponíveis.

A disciplina apresenta RAGAS/DeepEval e LLM-as-a-judge. Nesta implementação, a avaliação principal roda de forma determinística e reproduzível no GitHub Actions, funcionando como alternativa equivalente sem depender de uma segunda chave de LLM. A arquitetura pode ser evoluída para DeepEval/LLM-as-a-judge sem mudar o golden dataset.

Arquivos:
- `golden_dataset.json`
- `run_evaluation.py`
- `resultados/RESULTADO_AVALIACAO.md`
- `resultados/resultados_golden.json`
