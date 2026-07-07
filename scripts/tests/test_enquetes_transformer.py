from datetime import datetime

import pandas as pd
import pytest

from transformers.enquetes import (
    build_gold,
    make_pesquisa_id,
    normalize_name,
    parse_percent,
    parse_pt_date,
    parse_sample_size,
    to_bronze,
    to_prata,
)


def test_parse_percent_handles_formats_and_absence():
    assert parse_percent("42%") == 42.0
    assert parse_percent("38,3%") == 38.3
    assert parse_percent("0%") == 0.0
    assert parse_percent("N/A") is None
    assert parse_percent("{{N/A}}") is None
    assert parse_percent("") is None
    assert parse_percent("-") is None
    # 'não pontuou' -> 0.0 (but caller keeps the original text separately)
    assert parse_percent("não pontuou") == 0.0


def test_parse_sample_size_handles_separators_and_absence():
    assert parse_sample_size("19.552") == 19552
    assert parse_sample_size("2 009") == 2009
    assert parse_sample_size("–") is None
    assert parse_sample_size("") is None
    assert parse_sample_size(None) is None


def test_parse_pt_date_variants():
    iso, ymd, note = parse_pt_date("5 de outubro de 2018", "2018")
    assert iso == "2018-10-05" and ymd == (2018, 10, 5)

    iso, ymd, _ = parse_pt_date("26 Jun", "2026")
    assert iso == "2026-06-26"

    iso, ymd, _ = parse_pt_date("01 Out", "2022")
    assert iso == "2022-10-01"

    # day-only yields a DAY_ONLY sentinel note (no iso)
    iso, ymd, note = parse_pt_date("28", "2022")
    assert iso == "" and note.startswith("DAY_ONLY")


def test_normalize_name_folds_accents_and_case():
    assert normalize_name("Flávio") == "flavio"
    assert normalize_name("  Lula ") == "lula"
    assert normalize_name("Ciro Gomes") == "ciro gomes"


def test_make_pesquisa_id_is_deterministic():
    a = make_pesquisa_id(2026, "Nexus/BTG", "26 Jun", "28 Jun", "2 009", "http://x")
    b = make_pesquisa_id(2026, "Nexus/BTG", "26 Jun", "28 Jun", "2 009", "http://x")
    c = make_pesquisa_id(2026, "Outro", "26 Jun", "28 Jun", "2 009", "http://x")
    assert a == b
    assert a != c
    assert a.startswith("psq_")


def _raw_frame():
    # Two candidates in one scenario of one poll; day-only start date.
    return pd.DataFrame(
        [
            {
                "ano": "2026", "mes": "Junho", "instituto_pesquisa": "Globo/Datafolha",
                "contratante_pesquisa_original": "Globo", "data_inicio_pesquisa": "26",
                "data_fim_pesquisa": "28 Jun", "tamanho_amostra": "2 009", "margem_erro": "2,00",
                "cenario_id": "cenario_1", "nome_candidato": "Lula", "partido": "PT",
                "percentual": "42%", "outros": "N/A", "indecisos_absentos": "8%",
                "fonte_titulo": "t", "fonte_url": "http://x", "fonte_website": "Carta",
                "fonte_data_publicacao": "", "fonte_data_acesso": "",
                "linha_original_wikitext": "raw", "observacoes_extracao": "",
            },
            {
                "ano": "2026", "mes": "Junho", "instituto_pesquisa": "Globo/Datafolha",
                "contratante_pesquisa_original": "Globo", "data_inicio_pesquisa": "26",
                "data_fim_pesquisa": "28 Jun", "tamanho_amostra": "2 009", "margem_erro": "2,00",
                "cenario_id": "cenario_1", "nome_candidato": "Flávio", "partido": "PL",
                "percentual": "35%", "outros": "N/A", "indecisos_absentos": "8%",
                "fonte_titulo": "t", "fonte_url": "http://x", "fonte_website": "Carta",
                "fonte_data_publicacao": "", "fonte_data_acesso": "",
                "linha_original_wikitext": "raw", "observacoes_extracao": "",
            },
        ]
    )


def test_to_bronze_adds_lineage_and_stable_hash():
    df = _raw_frame()
    ts = datetime(2026, 6, 30, 12, 0, 0)
    b1 = to_bronze(df, 2026, "pesquisa-2026", "f.csv", ts)
    b2 = to_bronze(df, 2026, "pesquisa-2026", "f.csv", datetime(2027, 1, 1))
    for col in ["ano_eleicao", "source_folder", "source_file", "ingestion_timestamp",
                "raw_row_number", "hash_linha"]:
        assert col in b1.columns
    assert b1["raw_row_number"].tolist() == [1, 2]
    # hash depends on data, not on ingestion timestamp
    assert b1["hash_linha"].tolist() == b2["hash_linha"].tolist()


def test_to_prata_normalizes_and_borrows_start_month():
    df = _raw_frame()
    bronze = to_bronze(df, 2026, "pesquisa-2026", "f.csv", datetime(2026, 6, 30))
    prata = to_prata(bronze)

    assert len(prata) == 2
    # data_referencia = parsed end date (start is day-only and only feeds the
    # reference date when the end date is missing).
    assert prata["data_referencia"].tolist() == ["2026-06-28", "2026-06-28"]
    assert prata["percentual_numero"].tolist() == [42.0, 35.0]
    # outros 'N/A' -> NULL, never 0
    assert prata["outros_numero"].isna().all()
    assert prata["nome_candidato_normalizado"].tolist() == ["lula", "flavio"]
    # both rows share one pesquisa_id and one cenario_id
    assert prata["pesquisa_id"].nunique() == 1
    assert prata["cenario_id"].nunique() == 1


def test_to_prata_keeps_every_institute():
    # Unlike earlier versions of the pipeline, prata is no longer restricted to
    # Datafolha: a non-Datafolha row must be kept (institute scoping now
    # happens per-table inside build_gold, not at the prata stage).
    df = _raw_frame()
    df.loc[1, "instituto_pesquisa"] = "Paraná Pesquisas"
    df.loc[1, "nome_candidato"] = "Ciro"
    bronze = to_bronze(df, 2026, "pesquisa-2026", "f.csv", datetime(2026, 6, 30))
    prata = to_prata(bronze)

    assert len(prata) == 2
    assert set(prata["instituto_pesquisa"]) == {"Globo/Datafolha", "Paraná Pesquisas"}


def test_to_prata_rewrites_2022_trimester_to_month():
    df = _raw_frame()
    # 2022 rows carry a trimester label; it must become the month of the end date.
    df["ano"] = "2022"
    df["mes"] = "3º trimestre"
    df["data_fim_pesquisa"] = "29 Set"
    df["instituto_pesquisa"] = "Datafolha"
    bronze = to_bronze(df, 2022, "pesquisa-2022", "f.csv", datetime(2022, 9, 30))
    prata = to_prata(bronze)

    assert prata["mes_referencia"].tolist() == ["Setembro", "Setembro"]
    assert prata["observacoes_normalizacao"].str.contains("mes_referencia derivado").all()


def test_build_gold_temporal_and_moving_average():
    df = _raw_frame()
    bronze = to_bronze(df, 2026, "pesquisa-2026", "f.csv", datetime(2026, 6, 30))
    prata = to_prata(bronze)
    gold = build_gold(prata)

    assert len(gold["temporal"]) == 2
    # not enough dates for a 3-window moving average -> NULL (never invented)
    assert gold["media_movel"]["media_movel"].isna().all()
    # comparativo has one row (one scenario) with candidate columns
    assert len(gold["comparativo"]) == 1
    assert "lula" in gold["comparativo"].columns


def _poll_row(
    *,
    cenario_id="cenario_1",
    data_fim="28 Jun",
    tamanho_amostra="2 009",
    nome_candidato="Lula",
    percentual="42%",
    ano="2026",
    mes="Junho",
    instituto="Globo/Datafolha",
):
    return {
        "ano": ano, "mes": mes, "instituto_pesquisa": instituto,
        "contratante_pesquisa_original": "Globo", "data_inicio_pesquisa": "26",
        "data_fim_pesquisa": data_fim, "tamanho_amostra": tamanho_amostra, "margem_erro": "2,00",
        "cenario_id": cenario_id, "nome_candidato": nome_candidato, "partido": "PT",
        "percentual": percentual, "outros": "N/A", "indecisos_absentos": "8%",
        "fonte_titulo": "t", "fonte_url": "http://x", "fonte_website": "Carta",
        "fonte_data_publicacao": "", "fonte_data_acesso": "",
        "linha_original_wikitext": "raw", "observacoes_extracao": "",
    }


def _build_gold_from_rows(rows, ano_eleicao=2026):
    df = pd.DataFrame(rows)
    bronze = to_bronze(df, ano_eleicao, f"pesquisa-{ano_eleicao}", "f.csv", datetime(2026, 6, 30))
    prata = to_prata(bronze)
    return build_gold(prata)


def test_media_mensal_columns_match_expected_schema():
    gold = _build_gold_from_rows([_poll_row()])
    mensal = gold["media_mensal"]

    assert list(mensal.columns) == [
        "ano_eleicao", "data_referencia", "mes_referencia",
        "nome_candidato_normalizado", "percentual_agregado",
    ]
    assert mensal["data_referencia"].tolist() == ["2026-06-01"]
    assert mensal["mes_referencia"].tolist() == ["Junho"]
    assert mensal["percentual_agregado"].tolist() == [42.0]


def test_media_mensal_uses_weighted_average_by_sample_size():
    rows = [
        _poll_row(cenario_id="cenario_1", data_fim="5 Jun", tamanho_amostra="1000", percentual="40%"),
        _poll_row(cenario_id="cenario_2", data_fim="20 Jun", tamanho_amostra="3000", percentual="50%"),
    ]
    gold = _build_gold_from_rows(rows)
    mensal = gold["media_mensal"]

    assert len(mensal) == 1
    # weighted: (40*1000 + 50*3000) / 4000 = 47.5; simple mean would be 45.0
    assert mensal["percentual_agregado"].iloc[0] == pytest.approx(47.5)


def test_media_mensal_falls_back_to_simple_mean_without_any_weight():
    rows = [
        _poll_row(cenario_id="cenario_1", data_fim="5 Jun", tamanho_amostra="–", percentual="40%"),
        _poll_row(cenario_id="cenario_2", data_fim="20 Jun", tamanho_amostra="–", percentual="50%"),
    ]
    gold = _build_gold_from_rows(rows)
    mensal = gold["media_mensal"]

    assert len(mensal) == 1
    assert mensal["percentual_agregado"].iloc[0] == pytest.approx(45.0)


def test_media_mensal_excludes_unweighted_row_when_others_have_weight():
    rows = [
        _poll_row(cenario_id="cenario_1", data_fim="5 Jun", tamanho_amostra="1000", percentual="40%"),
        _poll_row(cenario_id="cenario_2", data_fim="15 Jun", tamanho_amostra="3000", percentual="50%"),
        _poll_row(cenario_id="cenario_3", data_fim="25 Jun", tamanho_amostra="–", percentual="90%"),
    ]
    gold = _build_gold_from_rows(rows)
    mensal = gold["media_mensal"]

    assert len(mensal) == 1
    # the unweighted 90% row is excluded from the weighted computation
    assert mensal["percentual_agregado"].iloc[0] == pytest.approx(47.5)


def test_media_mensal_single_record_group_degenerates_to_its_own_value():
    gold = _build_gold_from_rows([_poll_row(percentual="33%", tamanho_amostra="–")])
    mensal = gold["media_mensal"]

    assert mensal["percentual_agregado"].tolist() == [33.0]


def test_media_mensal_does_not_merge_same_month_across_different_years():
    # ano_eleicao=2022 (not 2018) so the row isn't affected by the 2018-only
    # out-of-cycle-year filter tested separately below.
    rows = [
        _poll_row(cenario_id="cenario_1", data_fim="5 de setembro de 2021", percentual="10%"),
        _poll_row(cenario_id="cenario_2", data_fim="5 de setembro de 2022", percentual="90%"),
    ]
    gold = _build_gold_from_rows(rows, ano_eleicao=2022)
    mensal = gold["media_mensal"]

    # same ano_eleicao cycle and same month name, but different calendar years:
    # must produce two distinct monthly points, never averaged together.
    assert sorted(mensal["data_referencia"].tolist()) == ["2021-09-01", "2022-09-01"]
    assert sorted(mensal["percentual_agregado"].tolist()) == [10.0, 90.0]


def test_to_prata_drops_2018_cycle_rows_outside_2018():
    rows = [
        _poll_row(cenario_id="cenario_1", data_fim="5 de setembro de 2017", nome_candidato="Bolsonaro", percentual="10%"),
        _poll_row(cenario_id="cenario_2", data_fim="5 de setembro de 2018", nome_candidato="Bolsonaro", percentual="20%"),
    ]
    df = pd.DataFrame(rows)
    bronze = to_bronze(df, 2018, "pesquisa-2018", "f.csv", datetime(2018, 9, 30))
    prata = to_prata(bronze)

    assert len(prata) == 1
    assert prata["data_referencia"].tolist() == ["2018-09-05"]
    assert prata["percentual_numero"].tolist() == [20.0]


def test_to_prata_keeps_2018_rows_without_parseable_date():
    # A row whose date can't be parsed at all is not dropped by the 2018-year
    # filter (it's already excluded from every gold table by the existing
    # data_referencia != "" rule in build_gold).
    df = pd.DataFrame([_poll_row(data_fim="não interpretável")])
    df.loc[0, "data_inicio_pesquisa"] = ""
    bronze = to_bronze(df, 2018, "pesquisa-2018", "f.csv", datetime(2018, 9, 30))
    prata = to_prata(bronze)

    assert len(prata) == 1
    assert prata["data_referencia"].tolist() == [""]


def test_build_gold_datafolha_tables_exclude_other_institutes():
    rows = [
        _poll_row(cenario_id="cenario_1", data_fim="5 Jun", instituto="Globo/Datafolha", percentual="40%"),
        _poll_row(cenario_id="cenario_2", data_fim="20 Jun", instituto="PoderData", percentual="60%"),
    ]
    gold = _build_gold_from_rows(rows)

    # temporal/ultima/media_movel/comparativo stay Datafolha-only, even though
    # prata now carries every institute.
    assert gold["temporal"]["instituto_pesquisa"].tolist() == ["Globo/Datafolha"]
    assert gold["ultima"]["instituto_pesquisa"].tolist() == ["Globo/Datafolha"]
    assert len(gold["comparativo"]) == 1


def test_media_mensal_pools_every_institute():
    rows = [
        _poll_row(cenario_id="cenario_1", data_fim="5 Jun", instituto="Globo/Datafolha", percentual="40%"),
        _poll_row(cenario_id="cenario_2", data_fim="20 Jun", instituto="PoderData", percentual="60%"),
    ]
    gold = _build_gold_from_rows(rows)
    mensal = gold["media_mensal"]

    # unlike the Datafolha-only tables, media_mensal pools both institutes for
    # the same month.
    assert len(mensal) == 1
    assert mensal["percentual_agregado"].iloc[0] == pytest.approx(50.0)


def test_media_mensal_fills_month_missing_from_datafolha_using_other_institute():
    rows = [
        _poll_row(cenario_id="cenario_1", data_fim="10 Mai", instituto="Globo/Datafolha", percentual="35%"),
        # Datafolha has no poll in June; PoderData does. media_mensal must
        # still have a June point (Datafolha-only tables would have a gap).
        _poll_row(cenario_id="cenario_2", data_fim="15 Jun", instituto="PoderData", percentual="45%"),
    ]
    gold = _build_gold_from_rows(rows)
    mensal = gold["media_mensal"]
    temporal = gold["temporal"]

    assert sorted(mensal["data_referencia"].tolist()) == ["2026-05-01", "2026-06-01"]
    junho = mensal[mensal["data_referencia"] == "2026-06-01"]
    assert junho["percentual_agregado"].iloc[0] == pytest.approx(45.0)
    # confirms the gap is real for the Datafolha-only table (the point of the fix)
    assert temporal["data_referencia"].tolist() == ["2026-05-10"]


def test_build_gold_folds_haddad_2018_alias_scenarios_into_haddad():
    rows = [
        _poll_row(cenario_id="cenario_1", data_fim="10 Jun", ano="2018", nome_candidato="Haddad", percentual="30%"),
        _poll_row(
            cenario_id="cenario_2",
            data_fim="15 Jun",
            ano="2018",
            nome_candidato="algum candidato apoiado por Lula",
            percentual="35%",
        ),
        _poll_row(
            cenario_id="cenario_3",
            data_fim="20 Jun",
            ano="2018",
            nome_candidato="Haddad, apoiado por Lula",
            percentual="40%",
        ),
        _poll_row(cenario_id="cenario_4", data_fim="10 Jun", ano="2018", nome_candidato="Lula", percentual="25%"),
    ]
    gold = _build_gold_from_rows(rows, ano_eleicao=2018)
    temporal = gold["temporal"]

    haddad_rows = temporal[temporal["nome_candidato_normalizado"] == "haddad"]
    assert len(haddad_rows) == 3
    assert set(haddad_rows["nome_candidato"]) == {"Haddad"}
    assert sorted(haddad_rows["percentual_numero"].tolist()) == [30.0, 35.0, 40.0]

    # "Lula" himself is a distinct candidate and must not be merged in.
    assert temporal[temporal["nome_candidato_normalizado"] == "lula"]["percentual_numero"].tolist() == [25.0]
    assert "algum candidato apoiado por lula" not in temporal["nome_candidato_normalizado"].tolist()
    assert "haddad, apoiado por lula" not in temporal["nome_candidato_normalizado"].tolist()


def test_build_gold_haddad_alias_reconciliation_feeds_media_mensal():
    rows = [
        _poll_row(cenario_id="cenario_1", data_fim="10 Jun", ano="2018", nome_candidato="Haddad", percentual="30%"),
        _poll_row(
            cenario_id="cenario_2",
            data_fim="20 Jun",
            ano="2018",
            nome_candidato="Haddad, apoiado por Lula",
            percentual="40%",
        ),
    ]
    gold = _build_gold_from_rows(rows, ano_eleicao=2018)
    mensal = gold["media_mensal"]

    # media_mensal renames 2018 "haddad" to the Google Trends term "Haddad"
    # (see test_media_mensal_renames_candidate_to_trends_term_by_year below);
    # the other gold tables (checked in the sibling temporal-focused test)
    # keep the raw lowercase-folded "haddad".
    haddad_mensal = mensal[mensal["nome_candidato_normalizado"] == "Haddad"]
    assert len(haddad_mensal) == 1
    assert haddad_mensal["data_referencia"].iloc[0] == "2018-06-01"
    # both rows share the same tamanho_amostra (2 009), so the weighted mean
    # collapses to the simple mean of 30 and 40.
    assert haddad_mensal["percentual_agregado"].iloc[0] == pytest.approx(35.0)


def test_build_gold_does_not_apply_haddad_2018_alias_outside_2018():
    rows = [
        _poll_row(
            cenario_id="cenario_1",
            data_fim="10 Jun",
            ano="2022",
            nome_candidato="algum candidato apoiado por Lula",
            percentual="20%",
        ),
    ]
    gold = _build_gold_from_rows(rows, ano_eleicao=2022)
    temporal = gold["temporal"]

    assert temporal["nome_candidato_normalizado"].tolist() == ["algum candidato apoiado por lula"]


def test_media_mensal_renames_candidate_to_trends_term_by_year():
    # "Alckmin"/2018 -> "Geraldo Alckmin" (matches the Google Trends term in
    # GOOGLE_TRENDS_ELECTION_GROUPS["2018"], so attention-vs-polling charts
    # can cross the two series).
    rows = [_poll_row(ano="2018", nome_candidato="Alckmin", percentual="15%")]
    gold = _build_gold_from_rows(rows, ano_eleicao=2018)
    mensal = gold["media_mensal"]

    assert mensal["nome_candidato_normalizado"].tolist() == ["Geraldo Alckmin"]


def test_media_mensal_rename_is_scoped_to_media_mensal_only():
    # The other gold tables must keep the raw lowercase-folded form; only
    # media_mensal is rewritten to the Trends term.
    rows = [_poll_row(ano="2018", nome_candidato="Alckmin", percentual="15%")]
    gold = _build_gold_from_rows(rows, ano_eleicao=2018)

    assert gold["temporal"]["nome_candidato_normalizado"].tolist() == ["alckmin"]


def test_media_mensal_drops_non_candidate_names_by_year():
    # "Doria" never ran in 2018 or 2022; its media_mensal rows are dropped for
    # both years without affecting a real candidate's aggregate for that month.
    rows = [
        _poll_row(cenario_id="cenario_1", ano="2018", nome_candidato="Doria", percentual="15%"),
        _poll_row(cenario_id="cenario_2", ano="2018", nome_candidato="Lula", percentual="40%"),
    ]
    gold = _build_gold_from_rows(rows, ano_eleicao=2018)
    mensal = gold["media_mensal"]

    assert mensal["nome_candidato_normalizado"].tolist() == ["Lula"]


def test_media_mensal_rename_disambiguates_bolsonaro_family_in_2026():
    # 2026: "Bolsonaro" (the family/brand term) and "Flávio" (Datafolha's label
    # for Flávio Bolsonaro) must resolve to two distinct Trends terms,
    # "Bolsonaro" and "Flávio Bolsonaro" respectively.
    rows = [
        _poll_row(cenario_id="cenario_1", nome_candidato="Bolsonaro", percentual="30%"),
        _poll_row(cenario_id="cenario_2", nome_candidato="Flávio", percentual="10%"),
    ]
    gold = _build_gold_from_rows(rows, ano_eleicao=2026)
    mensal = gold["media_mensal"]

    assert sorted(mensal["nome_candidato_normalizado"].tolist()) == ["Bolsonaro", "Flávio Bolsonaro"]
