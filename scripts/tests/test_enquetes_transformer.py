from datetime import datetime

import pandas as pd

from transformers.enquetes import (
    build_gold,
    make_pesquisa_id,
    normalize_name,
    parse_percent,
    parse_pt_date,
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


def test_to_prata_keeps_only_datafolha():
    df = _raw_frame()
    # Turn the second row into a non-Datafolha institute; it must be dropped.
    df.loc[1, "instituto_pesquisa"] = "Paraná Pesquisas"
    df.loc[1, "nome_candidato"] = "Ciro"
    bronze = to_bronze(df, 2026, "pesquisa-2026", "f.csv", datetime(2026, 6, 30))
    prata = to_prata(bronze)

    assert len(prata) == 1
    assert prata["instituto_pesquisa"].tolist() == ["Globo/Datafolha"]
    assert prata["nome_candidato"].tolist() == ["Lula"]


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
