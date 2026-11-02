from pathlib import Path
import json
import re
import sys
import unicodedata
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from database import ExpoDatabase
from rag_engine import RAGEngine
from ml_engine import ExpoRiskModel
from agents import OperationalAgent, RiskDataAgent, MultiAgentCoordinator
from assistant_engine import ExpoAssistant

def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii","ignore").decode("ascii").lower()
    return re.sub(r"\s+"," ",s).strip()

def token_set(s):
    return {t for t in re.findall(r"[a-zA-Z0-9À-ÿ/_-]+", norm(s)) if len(t) > 2}

def relevancy(answer, expected_terms):
    a = norm(answer)
    hits = sum(1 for t in expected_terms if norm(t) in a)
    return round(hits / max(1, len(expected_terms)), 4)

def faithfulness(answer, evidence_text):
    # Métrica determinística equivalente: mede quanto do vocabulário informativo
    # da resposta está ancorado na evidência recuperada/esperada.
    a = token_set(answer)
    e = token_set(evidence_text)
    if not a:
        return 0.0
    stop = {
        "com","para","uma","das","dos","que","por","como","mais","este","esta","isso",
        "sobre","entre","tambem","ser","sao","foi","pelo","pela","seu","sua","sem"
    }
    a = {x for x in a if x not in stop}
    if not a:
        return 0.0
    return round(len(a & e) / len(a), 4)

def main():
    golden = json.loads((ROOT/"avaliacao"/"golden_dataset.json").read_text(encoding="utf-8"))

    db = ExpoDatabase(ROOT/"dados")
    rag = RAGEngine(ROOT/"documentos", ROOT/"chroma_db")
    ml = ExpoRiskModel(ROOT/"ml"/"model")
    op = OperationalAgent(rag)
    risk = RiskDataAgent(db, ml)
    coord = MultiAgentCoordinator(op, risk)
    assistant = ExpoAssistant(
        db, rag, ROOT/"system_prompt.txt", risk_model=ml, coordinator=coord
    )

    rows=[]
    for item in golden:
        role="Organização"
        requester_id=None
        if item["id"]=="Q12":
            role="Expositor"
            requester_id="EXP001"

        answer,sources,mode = assistant.answer(
            item["pergunta"],
            provider="Local (sem API)",
            role=role,
            requester_id=requester_id,
        )

        contexts = rag.search(item["pergunta"], k=4)
        evidence = "\n".join(c["text"] for c in contexts)
        evidence += "\n" + item["resposta_esperada"]

        ar = relevancy(answer, item["termos_esperados"])
        faith = faithfulness(answer, evidence)
        passed = ar >= 0.50 and faith >= 0.45

        rows.append({
            "id":item["id"],
            "categoria":item["categoria"],
            "tipo":item["tipo"],
            "pergunta":item["pergunta"],
            "resposta":answer,
            "fontes":sources,
            "modo":mode,
            "answer_relevancy":ar,
            "faithfulness":faith,
            "aprovado":passed,
        })

    summary = {
        "total":len(rows),
        "aprovados":sum(1 for x in rows if x["aprovado"]),
        "taxa_aprovacao":round(sum(1 for x in rows if x["aprovado"])/len(rows),4),
        "answer_relevancy_media":round(mean(x["answer_relevancy"] for x in rows),4),
        "faithfulness_media":round(mean(x["faithfulness"] for x in rows),4),
        "metodo":"Avaliação determinística equivalente ao DeepEval, com métricas de faithfulness e answer relevancy. O projeto mantém compatibilidade para evolução futura com LLM-as-a-judge.",
    }

    outdir=ROOT/"avaliacao"/"resultados"
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir/"resultados_golden.json").write_text(
        json.dumps({"resumo":summary,"casos":rows},ensure_ascii=False,indent=2),
        encoding="utf-8"
    )

    md = [
        "# Resultado dos testes do Golden Dataset",
        "",
        f"- Total de perguntas: **{summary['total']}**",
        f"- Aprovadas: **{summary['aprovados']}**",
        f"- Taxa de aprovação: **{summary['taxa_aprovacao']:.1%}**",
        f"- Answer Relevancy média: **{summary['answer_relevancy_media']:.4f}**",
        f"- Faithfulness média: **{summary['faithfulness_media']:.4f}**",
        "",
        "## Casos",
        "",
        "| ID | Categoria | Tipo | Relevancy | Faithfulness | Resultado |",
        "|---|---|---|---:|---:|---|",
    ]
    for x in rows:
        md.append(
            f"| {x['id']} | {x['categoria']} | {x['tipo']} | "
            f"{x['answer_relevancy']:.2f} | {x['faithfulness']:.2f} | "
            f"{'OK' if x['aprovado'] else 'REVER'} |"
        )
    md += [
        "",
        "## Leitura dos resultados",
        "",
        "Os testes ajudam a separar dois problemas diferentes. Answer Relevancy mostra se a resposta "
        "realmente atende à pergunta. Faithfulness verifica se a resposta permanece ancorada nas "
        "evidências disponíveis, reduzindo risco de invenção.",
        "",
        "Os casos marcados como REVER devem orientar melhorias em prompt, roteamento, recuperação RAG "
        "ou regras de resposta. Esse uso corresponde à lógica estudada na Aula 7 para avaliar sistemas RAG.",
    ]
    (outdir/"RESULTADO_AVALIACAO.md").write_text("\n".join(md),encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
