"""
Automatic validations for the enquetes medallion pipeline.

Produces a tidy DataFrame (``verificacao``, ``resultado``, ``severidade``) that
is printed and published to the ``validacao_enquetes`` tab. Nothing here mutates
data; it only measures it.
"""

import pandas as pd


def _pesquisas_where_all(prata, column, predicate) -> int:
    """Count distinct pesquisa_id whose rows all satisfy ``predicate`` on column."""
    grouped = prata.groupby("pesquisa_id")[column]
    flagged = grouped.apply(lambda s: bool(s.map(predicate).all()))
    return int(flagged.sum())


def run_validations(bronze_by_year: dict, prata: pd.DataFrame, gold: dict):
    rows = []

    def add(verificacao, resultado, severidade="INFO"):
        rows.append({"verificacao": verificacao, "resultado": str(resultado), "severidade": severidade})

    # 1. arquivos lidos por ano
    add("arquivos_lidos_por_ano", {ano: 1 for ano in sorted(bronze_by_year)})
    add("total_arquivos_lidos", len(bronze_by_year))

    # 2. linhas na bronze
    linhas_bronze = {ano: len(df) for ano, df in bronze_by_year.items()}
    total_bronze = sum(linhas_bronze.values())
    add("linhas_bronze_por_ano", linhas_bronze)
    add("total_linhas_bronze", total_bronze)

    # 3. pesquisas distintas na prata
    add("pesquisas_distintas_prata", prata["pesquisa_id"].nunique())
    add("cenarios_distintos_prata", prata["cenario_id"].nunique())
    add("linhas_prata", len(prata))

    # 4. candidatos distintos por ano
    cand_por_ano = (
        prata[prata["nome_candidato_normalizado"] != ""]
        .groupby("ano_eleicao")["nome_candidato_normalizado"]
        .nunique()
        .to_dict()
    )
    add("candidatos_distintos_por_ano", cand_por_ano)

    # 5. percentuais fora de 0..100
    pn = pd.to_numeric(prata["percentual_numero"], errors="coerce")
    fora = int(((pn < 0) | (pn > 100)).sum())
    add("percentuais_fora_0_100", fora, "ERRO" if fora else "OK")

    # 6. pesquisas sem instituto
    sem_inst = _pesquisas_where_all(prata, "instituto_pesquisa", lambda v: (v or "").strip() == "")
    add("pesquisas_sem_instituto", sem_inst, "AVISO" if sem_inst else "OK")

    # 7. pesquisas sem data (nenhuma data_referencia em nenhuma linha)
    sem_data = _pesquisas_where_all(prata, "data_referencia", lambda v: (v or "").strip() == "")
    add("pesquisas_sem_data", sem_data, "AVISO" if sem_data else "OK")

    # 8. pesquisas sem fonte_url
    sem_url = _pesquisas_where_all(prata, "fonte_url", lambda v: (v or "").strip() == "")
    add("pesquisas_sem_fonte_url", sem_url, "AVISO" if sem_url else "OK")

    # 9. candidatos sem partido
    cand = prata[prata["nome_candidato_normalizado"] != ""]
    sem_partido = int((cand["partido"].fillna("").str.strip() == "").sum())
    add("linhas_candidato_sem_partido", sem_partido, "AVISO" if sem_partido else "OK")

    # 10. duplicidades por (cenario_id, nome_candidato_normalizado)
    dup_base = prata[prata["nome_candidato_normalizado"] != ""]
    dup = dup_base.groupby(["cenario_id", "nome_candidato_normalizado"]).size()
    dup_count = int((dup > 1).sum())
    add("duplicidades_cenario_candidato", dup_count, "ERRO" if dup_count else "OK")

    # 11. registros da ouro sem correspondência na prata
    prata_cenarios = set(prata["cenario_id"])
    gold_cenarios = set(gold["temporal"]["cenario_id"]) if not gold["temporal"].empty else set()
    orfaos_ouro = len(gold_cenarios - prata_cenarios)
    add("ouro_sem_correspondencia_prata", orfaos_ouro, "ERRO" if orfaos_ouro else "OK")

    # 12. registros da prata sem correspondência na bronze
    bronze_hashes = set()
    for df in bronze_by_year.values():
        bronze_hashes.update(df["hash_linha"].tolist())
    orfaos_prata = int((~prata["hash_linha_bronze"].isin(bronze_hashes)).sum())
    add("prata_sem_correspondencia_bronze", orfaos_prata, "ERRO" if orfaos_prata else "OK")

    validation_df = pd.DataFrame(rows, columns=["verificacao", "resultado", "severidade"])

    headline = {
        "total_bronze": total_bronze,
        "linhas_prata": len(prata),
        "pesquisas_distintas": prata["pesquisa_id"].nunique(),
        "linhas_gold_temporal": len(gold["temporal"]),
        "erros": int((validation_df["severidade"] == "ERRO").sum()),
        "avisos": int((validation_df["severidade"] == "AVISO").sum()),
    }
    return validation_df, headline
