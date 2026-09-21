from pathlib import Path
import duckdb
import re
import unicodedata

def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", text.lower()).strip()

class ExpoDatabase:
    def __init__(self, data_dir: str | Path):
        self.data_dir = Path(data_dir)
        self.con = duckdb.connect(database=":memory:")
        self._load()

    def _load(self):
        for table in ("expositores", "estandes", "pendencias"):
            path = (self.data_dir / f"{table}.csv").as_posix()
            self.con.execute(
                f"CREATE OR REPLACE TABLE {table} AS "
                f"SELECT * FROM read_csv_auto('{path}', header=true)"
            )

    def exhibitors(self):
        rows = self.con.execute(
            "SELECT expositor_id, nome_fantasia FROM expositores ORDER BY nome_fantasia"
        ).fetchall()
        return [{"id": r[0], "nome": r[1]} for r in rows]

    def find_exhibitor(self, text: str):
        nt = _norm(text)
        for item in self.exhibitors():
            if _norm(item["nome"]) in nt:
                return item
        return None

    def _check_access(self, target, role, requester_id):
        if role == "Organização":
            return True
        return bool(target and requester_id and target["id"] == requester_id)

    def answer_query(self, question: str, role="Organização", requester_id=None):
        q = _norm(question)
        target = self.find_exhibitor(question)

        if ("quant" in q and "expositor" in q and ("pend" in q or "abert" in q)):
            if role != "Organização":
                return ("Esta consulta agregada está disponível apenas para o perfil Organização.", None)
            sql = """
                SELECT COUNT(DISTINCT expositor_id)
                FROM pendencias
                WHERE lower(status) <> 'concluída'
            """
            n = self.con.execute(sql).fetchone()[0]
            return (f"Há {n} expositores com pelo menos uma pendência ainda não concluída.", sql)

        if ("quais" in q or "listar" in q or "liste" in q) and "pend" in q and "expositor" in q and not target:
            if role != "Organização":
                return ("A listagem geral de pendências está disponível apenas para o perfil Organização.", None)
            sql = """
                SELECT e.nome_fantasia, COUNT(*) AS abertas
                FROM pendencias p
                JOIN expositores e USING (expositor_id)
                WHERE lower(p.status) <> 'concluída'
                GROUP BY e.nome_fantasia
                ORDER BY abertas DESC, e.nome_fantasia
            """
            rows = self.con.execute(sql).fetchall()
            if not rows:
                return ("Não há pendências abertas.", sql)
            body = "\n".join(f"- {nome}: {qtd} pendência(s)" for nome, qtd in rows)
            return ("Expositores com pendências não concluídas:\n" + body, sql)

        if target:
            if not self._check_access(target, role, requester_id):
                return ("Por segurança, o perfil Expositor só pode consultar os próprios dados estruturados.", None)

            if any(k in q for k in ("estande", "metragem", "metro", "setor", "localiza")):
                sql = """
                    SELECT e.nome_fantasia, s.codigo_estande, s.setor, s.metragem_m2, s.tipo_montagem
                    FROM expositores e
                    JOIN estandes s USING (expositor_id)
                    WHERE e.expositor_id = ?
                """
                row = self.con.execute(sql, [target["id"]]).fetchone()
                if not row:
                    return ("Não encontrei estande para esse expositor.", sql)
                nome, codigo, setor, m2, tipo = row
                return (
                    f"{nome}: estande {codigo}, setor {setor}, {m2} m², tipo de montagem: {tipo}.",
                    sql,
                )

            if any(k in q for k in ("pend", "situacao", "situação", "prazo", "document")):
                sql = """
                    SELECT descricao, status, prazo, prioridade
                    FROM pendencias
                    WHERE expositor_id = ?
                    ORDER BY CASE prioridade WHEN 'Alta' THEN 1 WHEN 'Média' THEN 2 ELSE 3 END, prazo
                """
                rows = self.con.execute(sql, [target["id"]]).fetchall()
                if not rows:
                    return (f"Não há pendências cadastradas para {target['nome']}.", sql)
                body = "\n".join(
                    f"- {desc} — {status} — prazo {prazo} — prioridade {prio}"
                    for desc, status, prazo, prio in rows
                )
                return (f"Pendências de {target['nome']}:\n{body}", sql)

            if any(k in q for k in ("cidade", "segmento", "contrato")):
                sql = """
                    SELECT nome_fantasia, segmento, cidade, uf, status_contrato
                    FROM expositores WHERE expositor_id = ?
                """
                row = self.con.execute(sql, [target["id"]]).fetchone()
                nome, segmento, cidade, uf, status = row
                return (
                    f"{nome}: segmento {segmento}; origem {cidade}/{uf}; contrato {status}.",
                    sql,
                )

        return (None, None)
