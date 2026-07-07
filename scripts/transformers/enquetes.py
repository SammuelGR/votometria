"""
Transformer for the electoral-polls (enquetes) source.

Builds:
  * bronze frames  -> raw rows + lineage (minimal transformation);
  * the prata frame -> normalized long table (one row per candidate per
    scenario), with deterministic ids, ISO dates and numeric percentuais;
  * the gold frames -> analytical tables for temporal candidate analysis.

Rules honoured: never invent data, never turn absence into zero, keep the
original values alongside the normalized ones, and record ambiguity in
``observacoes_normalizacao``.
"""

import hashlib
import re
import unicodedata
from datetime import date

import pandas as pd

from constants_enquetes import (
    MEDIA_MOVEL_WINDOW,
    PERCENT_NULL_TOKENS,
    PT_MONTH_NAMES,
    PT_MONTHS,
)

# Token used to scope specific gold tables (temporal/ultima/media_movel/
# comparativo) to a single institute, case-insensitive substring match. This
# covers every Datafolha label ("Datafolha", "Globo/Datafolha",
# "Folha/Datafolha", "Globo e Folha/Datafolha"). The prata layer itself is NOT
# scoped to Datafolha (it keeps every institute from bronze) so that the
# multi-institutional monthly aggregation (``media_mensal``) has full month
# coverage to draw from; only the per-institute gold tables apply this filter.
DATAFOLHA_INSTITUTO_FILTER = "datafolha"

# Columns of the normalized (prata) long table, in order.
PRATA_COLUMNS = [
    "pesquisa_id",
    "cenario_id",
    "ano_eleicao",
    "mes_referencia",
    "instituto_pesquisa",
    "contratante_pesquisa",
    "data_referencia",
    "tamanho_amostra",
    "margem_erro",
    "nome_candidato",
    "nome_candidato_normalizado",
    "partido",
    "percentual_original",
    "percentual_numero",
    "outros_original",
    "outros_numero",
    "indecisos_absentos_original",
    "indecisos_absentos_numero",
    "fonte_titulo",
    "fonte_url",
    "fonte_website",
    "fonte_data_publicacao",
    "fonte_data_acesso",
    "hash_linha_bronze",
    "observacoes_normalizacao",
]

GOLD_TEMPORAL_COLUMNS = [
    "ano_eleicao",
    "data_referencia",
    "instituto_pesquisa",
    "pesquisa_id",
    "cenario_id",
    "nome_candidato",
    "nome_candidato_normalizado",
    "partido",
    "percentual_numero",
    "percentual_original",
    "tamanho_amostra",
    "margem_erro",
    "fonte_url",
    "fonte_website",
]

# Dedicated time-series columns: one row per (ano_eleicao, candidato, mês),
# ready for direct chart consumption (no further aggregation needed).
GOLD_MEDIA_MENSAL_COLUMNS = [
    "ano_eleicao",
    "data_referencia",
    "mes_referencia",
    "nome_candidato_normalizado",
    "percentual_agregado",
]


# --------------------------------------------------------------------------
# bronze
# --------------------------------------------------------------------------
def _row_hash(values, ano_eleicao, source_file) -> str:
    payload = "|".join("" if v is None else str(v) for v in values)
    payload = f"{ano_eleicao}|{source_file}|{payload}"
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()


def to_bronze(df, ano_eleicao, source_folder, source_file, ingestion_ts) -> pd.DataFrame:
    """
    Adds lineage columns to the raw frame with minimal transformation. The row
    hash is derived from the original values only (not the timestamp), so it is
    stable across runs.
    """
    original_cols = list(df.columns)
    bronze = df.copy()

    bronze.insert(0, "ano_eleicao", ano_eleicao)
    bronze.insert(1, "source_folder", source_folder)
    bronze.insert(2, "source_file", source_file)
    bronze.insert(3, "ingestion_timestamp", ingestion_ts.isoformat(sep=" ", timespec="seconds"))
    bronze.insert(4, "raw_row_number", range(1, len(bronze) + 1))

    bronze["hash_linha"] = [
        _row_hash([row[c] for c in original_cols], ano_eleicao, source_file)
        for _, row in df.iterrows()
    ]
    return bronze


# --------------------------------------------------------------------------
# value parsing
# --------------------------------------------------------------------------
def parse_sample_size(raw):
    """
    Returns an int sample size parsed from the raw ``tamanho_amostra`` text
    (thousands separator may be a space or a dot, e.g. "2 009"/"19.552"), or
    ``None`` when missing/unparseable (e.g. the "–" placeholder). Never
    invents a number for absence.
    """
    digits = re.sub(r"\D", "", raw or "")
    if not digits:
        return None
    return int(digits)


def parse_percent(raw):
    """Returns a float, ``0.0`` for 'não pontuou', or ``None`` for absence."""
    s = (raw or "").strip()
    low = s.lower()
    if "não pontuou" in low or "nao pontuou" in low:
        return 0.0
    if low in PERCENT_NULL_TOKENS:
        return None
    m = re.search(r"-?\d+(?:[.,]\d+)?", s)
    if not m:
        return None
    try:
        return float(m.group(0).replace(",", "."))
    except ValueError:
        return None


def _iso(y, m, d):
    try:
        return date(int(y), int(m), int(d)).isoformat()
    except (ValueError, TypeError):
        return ""


def parse_pt_date(raw, default_year):
    """
    Returns ``(iso, ymd_tuple_or_None, note)``. ``iso`` is '' when the date
    cannot be safely interpreted (the original is always preserved elsewhere).
    A day-only value (e.g. '28') yields a ``DAY_ONLY:<n>`` note so the caller can
    borrow the month/year from the range end.
    """
    s = (raw or "").strip()
    if not s:
        return "", None, "data vazia"
    low = s.lower()

    m = re.search(r"(\d{1,2})\s+de\s+([a-zçãéêíóú]+)\s+de\s+(\d{4})", low)
    if m:
        mo = PT_MONTHS.get(m.group(2))
        if mo:
            y, d = int(m.group(3)), int(m.group(1))
            iso = _iso(y, mo, d)
            return iso, (y, mo, d), ("" if iso else f"data inválida: {s}")
        return "", None, f"mês não reconhecido: {m.group(2)}"

    m = re.search(r"(\d{1,2})\s+([a-zçãéêíóú]{3,})", low)
    if m:
        mo = PT_MONTHS.get(m.group(2)) or PT_MONTHS.get(m.group(2)[:3])
        if mo and default_year:
            y, d = int(default_year), int(m.group(1))
            iso = _iso(y, mo, d)
            return iso, (y, mo, d), ("" if iso else f"data inválida: {s}")
        return "", None, f"mês/ano indeterminado: {s}"

    if re.fullmatch(r"\d{1,2}", s):
        return "", None, f"DAY_ONLY:{s}"

    return "", None, f"data não interpretada: {s}"


def normalize_name(raw):
    s = (raw or "").strip().lower()
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s).strip()


def normalize_party(raw):
    return re.sub(r"\s+", " ", (raw or "").strip())


def make_pesquisa_id(ano_eleicao, instituto, data_inicio, data_fim, amostra, url):
    key = "|".join(
        [
            str(ano_eleicao),
            (instituto or "").strip().lower(),
            (data_inicio or "").strip(),
            (data_fim or "").strip(),
            (amostra or "").strip(),
            (url or "").strip(),
        ]
    )
    return "psq_" + hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]


# --------------------------------------------------------------------------
# prata
# --------------------------------------------------------------------------
def to_prata(bronze_all: pd.DataFrame) -> pd.DataFrame:
    records = []
    for _, r in bronze_all.iterrows():
        ano_eleicao = r["ano_eleicao"]
        row_year = (r.get("ano") or "").strip() or str(ano_eleicao)

        instituto = (r.get("instituto_pesquisa") or "").strip()
        contratante = (r.get("contratante_pesquisa_original") or "").strip()
        di_raw = r.get("data_inicio_pesquisa") or ""
        df_raw = r.get("data_fim_pesquisa") or ""
        amostra = (r.get("tamanho_amostra") or "").strip()
        url = (r.get("fonte_url") or "").strip()

        notes = []

        fim_iso, fim_ymd, fim_note = parse_pt_date(df_raw, row_year)
        ini_iso, ini_ymd, ini_note = parse_pt_date(di_raw, row_year)

        # Day-only start date: borrow month/year from the (parsed) end date.
        if ini_note.startswith("DAY_ONLY") and fim_ymd:
            day = int(ini_note.split(":", 1)[1])
            y, mo, _ = fim_ymd
            ini_iso = _iso(y, mo, day)
            ini_note = "dia sem mês; mês/ano herdados de data_fim"
        if fim_note and not fim_note.startswith("DAY_ONLY"):
            notes.append(f"data_fim: {fim_note}")
        if ini_note and not ini_note.startswith("DAY_ONLY"):
            notes.append(f"data_inicio: {ini_note}")

        data_referencia = fim_iso or ini_iso

        # The 2018 folder also carries hypothetical pre-race polls dated
        # 2015-2017 (and an even earlier 2014 result); the 2018 cycle table
        # must only represent calendar year 2018 itself. Rows without a parsed
        # date are left alone here (they are already excluded from every gold
        # table by the existing `data_referencia != ""` filter in build_gold).
        if ano_eleicao == 2018 and data_referencia and not data_referencia.startswith("2018"):
            continue

        # 2022 rows carry a trimester in ``mes`` instead of a month; rewrite it to
        # the actual month name taken from the poll end date (data_referencia).
        mes_ref = (r.get("mes") or "").strip()
        if "trimestre" in mes_ref.lower():
            iso_for_month = fim_iso or ini_iso
            if iso_for_month:
                mes_month = PT_MONTH_NAMES.get(int(iso_for_month[5:7]))
                if mes_month:
                    notes.append(f"mes_referencia derivado de data_fim (era '{mes_ref}')")
                    mes_ref = mes_month

        pesquisa_id = make_pesquisa_id(ano_eleicao, instituto, di_raw, df_raw, amostra, url)
        cenario_label = (r.get("cenario_id") or "cenario_1").strip()
        cenario_id = f"{pesquisa_id}_{cenario_label}"

        perc_orig = (r.get("percentual") or "").strip()
        outros_orig = (r.get("outros") or "").strip()
        indec_orig = (r.get("indecisos_absentos") or "").strip()

        obs_extracao = (r.get("observacoes_extracao") or "").strip()
        if obs_extracao:
            notes.append(f"extracao: {obs_extracao}")

        records.append(
            {
                "pesquisa_id": pesquisa_id,
                "cenario_id": cenario_id,
                "ano_eleicao": ano_eleicao,
                "mes_referencia": mes_ref,
                "instituto_pesquisa": instituto,
                "contratante_pesquisa": contratante,
                "data_referencia": data_referencia,
                "tamanho_amostra": amostra,
                "margem_erro": (r.get("margem_erro") or "").strip(),
                "nome_candidato": (r.get("nome_candidato") or "").strip(),
                "nome_candidato_normalizado": normalize_name(r.get("nome_candidato")),
                "partido": normalize_party(r.get("partido")),
                "percentual_original": perc_orig,
                "percentual_numero": parse_percent(perc_orig),
                "outros_original": outros_orig,
                "outros_numero": parse_percent(outros_orig),
                "indecisos_absentos_original": indec_orig,
                "indecisos_absentos_numero": parse_percent(indec_orig),
                "fonte_titulo": (r.get("fonte_titulo") or "").strip(),
                "fonte_url": url,
                "fonte_website": (r.get("fonte_website") or "").strip(),
                "fonte_data_publicacao": (r.get("fonte_data_publicacao") or "").strip(),
                "fonte_data_acesso": (r.get("fonte_data_acesso") or "").strip(),
                "hash_linha_bronze": r.get("hash_linha"),
                "observacoes_normalizacao": " | ".join(notes),
            }
        )

    return pd.DataFrame(records, columns=PRATA_COLUMNS)


# --------------------------------------------------------------------------
# gold
# --------------------------------------------------------------------------

# 2018-only candidate identity reconciliation: before Haddad was confirmed as
# PT's candidate (after Lula's candidacy was blocked by the TSE), some
# institutes polled placeholder/hypothetical scenarios naming him indirectly
# instead of by name. These are the same candidate for analytical purposes and
# are folded into Haddad's own identity here (gold layer only — prata keeps
# the original, distinct labels for audit). "Lula" itself is untouched; only
# the two scenarios that stand in for Haddad are merged.
HADDAD_2018_ALIAS_NORMALIZED = {
    "haddad, apoiado por lula",
    "algum candidato apoiado por lula",
}


def _reconcile_haddad_2018_aliases(df: pd.DataFrame) -> pd.DataFrame:
    is_alias = (df["ano_eleicao"] == 2018) & (df["nome_candidato_normalizado"].isin(HADDAD_2018_ALIAS_NORMALIZED))

    if not is_alias.any():
        return df

    df = df.copy()
    df.loc[is_alias, "nome_candidato"] = "Haddad"
    df.loc[is_alias, "nome_candidato_normalizado"] = "haddad"
    return df


# ``gold_pesquisas_media_mensal_candidato`` is the table crossed against Google
# Trends terms (``proc_google_trends_all_elections_interest_monthly``, terms
# configured per cycle in ``GOOGLE_TRENDS_ELECTION_GROUPS`` in constants.py) to
# build attention-vs-polling charts. Its ``nome_candidato_normalizado`` values
# were the raw wikitext surname folded to lowercase (e.g. "alckmin",
# "meirelles"), which never matches a Trends term like "Geraldo Alckmin" or
# "Henrique Meirelles" — the chart would show polling with no attention line
# (or vice-versa). This maps each (ano_eleicao, raw normalized name) pair to
# the exact Trends term string for that candidate/cycle; a ``None`` target
# means the name is not an actual candidate for that election (a placeholder
# or another office entirely) and its rows are dropped from this table only.
# Scoped to media_mensal alone: the other four gold tables (temporal, ultima,
# media_movel, comparativo) keep the raw lowercase-folded form, and prata is
# untouched (kept for audit).
MEDIA_MENSAL_CANDIDATE_NAMES = {
    2018: {
        "alckmin": "Geraldo Alckmin",
        "amoedo": "João Amoêdo",
        "barbosa": None,  # Joaquim Barbosa was not a 2018 candidate
        "bolsonaro": "Bolsonaro",
        "dias": "Alvaro Dias",
        "doria": None,
        "gomes": "Ciro Gomes",
        "haddad": "Haddad",
        "lula": "Lula",
        "meirelles": "Henrique Meirelles",
        "silva": "Marina Silva",
        "temer": None,
        "wagner": None,
    },
    2022: {
        "bivar": None,
        "bolsonaro": "Bolsonaro",
        "d'avila": "Felipe d'Avila",
        "doria": None,
        "eymael": "Eymael",
        "gomes": "Ciro Gomes",
        "janones": None,
        "jefferson": None,
        "kelmon": "Padre Kelmon",
        "leite": None,
        "lula": "Lula",
        "manzano": "Sofia Manzano",
        "marcal": None,
        "moro": None,
        "pacheco": None,
        "pericles": "Léo Péricles",
        "salgado": None,
        "tebet": "Simone Tebet",
        "thronicke": "Soraya Thronicke",
        "vieira": None,
    },
    2026: {
        "aecio": None,
        "barbosa": None,
        "bolsonaro": "Bolsonaro",
        "caiado": "Ronaldo Caiado",
        "costa": "Edmilson Costa",
        "cury": "Augusto Cury",
        "daciolo": "Cabo Daciolo",
        "dias": "Hertz Dias",
        "flavio": "Flávio Bolsonaro",
        "gomes": None,
        "haddad": None,
        "leite": None,
        "lula": "Lula",
        "michelle": None,
        "pimenta": "Rui Costa Pimenta",
        "ratinho": None,
        "rebelo": "Aldo Rebelo",
        "renan": "Renan Santos",
        "samara": "Samara Martins",
        "tarcisio": None,
        "zema": "Romeu Zema",
    },
}


def _apply_media_mensal_candidate_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renames/drops rows of ``df`` per ``MEDIA_MENSAL_CANDIDATE_NAMES``, keyed by
    (``ano_eleicao``, ``nome_candidato_normalizado``). Names outside the map
    are left untouched. Must run before any groupby that keys off
    ``nome_candidato_normalizado`` — none of the per-year target names collide
    with each other, so renaming ahead of the aggregation is equivalent to
    renaming after it.
    """
    df = df.copy()
    keep = pd.Series(True, index=df.index)

    for ano, mapping in MEDIA_MENSAL_CANDIDATE_NAMES.items():
        year_mask = df["ano_eleicao"] == ano
        for original, target in mapping.items():
            row_mask = year_mask & (df["nome_candidato_normalizado"] == original)
            if target is None:
                keep &= ~row_mask
            else:
                df.loc[row_mask, "nome_candidato_normalizado"] = target

    return df[keep].reset_index(drop=True)


def build_gold(prata: pd.DataFrame) -> dict:
    """
    Builds the gold analytical tables from the prata long table. Rows without a
    candidate name, without a numeric percentual or without a reference date are
    excluded from the gold layer (they remain fully preserved in prata). 2018
    scenarios standing in for Haddad before he was confirmed as candidate
    (``_reconcile_haddad_2018_aliases``) are folded into his identity here too
    — prata keeps the original, distinct labels.

    ``temporal``, ``ultima``, ``media_movel`` and ``comparativo`` are scoped to
    Datafolha only (``datafolha_base``), matching their original, documented
    per-institute analytical purpose. ``media_mensal`` is the exception: it
    draws from every institute in ``base`` so that a month missing from
    Datafolha can still be covered by another institute's poll, guaranteeing no
    gaps in the monthly time series used by charts.
    """
    base = prata[
        (prata["nome_candidato_normalizado"] != "")
        & (prata["percentual_numero"].notna())
        & (prata["data_referencia"] != "")
    ].copy()
    base = _reconcile_haddad_2018_aliases(base)

    datafolha_base = base[
        base["instituto_pesquisa"].str.lower().str.contains(DATAFOLHA_INSTITUTO_FILTER)
    ]

    temporal = datafolha_base[GOLD_TEMPORAL_COLUMNS].sort_values(
        ["ano_eleicao", "nome_candidato_normalizado", "data_referencia", "instituto_pesquisa"]
    ).reset_index(drop=True)

    # Latest poll per candidate x election x institute.
    ultima = (
        temporal.sort_values("data_referencia")
        .groupby(["ano_eleicao", "instituto_pesquisa", "nome_candidato_normalizado"], as_index=False)
        .tail(1)
        .sort_values(["ano_eleicao", "nome_candidato_normalizado", "instituto_pesquisa"])
        .reset_index(drop=True)
    )

    # Moving average per candidate over the daily mean across institutes/scenarios.
    daily = (
        temporal.groupby(
            ["ano_eleicao", "nome_candidato_normalizado", "data_referencia"], as_index=False
        )["percentual_numero"]
        .mean()
        .rename(columns={"percentual_numero": "media_percentual_dia"})
        .sort_values(["ano_eleicao", "nome_candidato_normalizado", "data_referencia"])
        .reset_index(drop=True)
    )
    daily["media_movel"] = (
        daily.groupby(["ano_eleicao", "nome_candidato_normalizado"])["media_percentual_dia"]
        .transform(lambda s: s.rolling(window=MEDIA_MOVEL_WINDOW, min_periods=MEDIA_MOVEL_WINDOW).mean())
    )
    daily["janela_media_movel"] = MEDIA_MOVEL_WINDOW

    # Monthly aggregation dedicated to time-series charts: one row per
    # (ano_eleicao, candidato, mês), pooling EVERY institute (not just
    # Datafolha, unlike temporal/ultima/media_movel/comparativo above) so a
    # month missing from Datafolha alone can still be covered by another
    # institute's poll that month. Weighted by tamanho_amostra when parseable;
    # falls back to a simple mean for a given month when no row in it has a
    # usable sample size (never invents a weight). Mixing institutes trades
    # gap-free months for exposure to each institute's own methodology/"house
    # effect" — documented in docs/enquetes_pipeline.md.
    if not base.empty:
        mensal_base = _apply_media_mensal_candidate_names(base)
        # pd.to_numeric coerces the mixed int/None result of parse_sample_size
        # into a proper float64 column (NaN for None); without it the column
        # stays object-dtype and a later 0/0 raises ZeroDivisionError instead
        # of yielding NaN.
        mensal_base["tamanho_amostra_numero"] = pd.to_numeric(
            mensal_base["tamanho_amostra"].map(parse_sample_size), errors="coerce"
        )
        # Real calendar year-month, not the ano_eleicao cycle: the 2018 folder,
        # for example, also carries hypothetical 2015-2017 rows, so grouping by
        # ano_eleicao + mes_referencia name alone would merge e.g. "Setembro" of
        # different calendar years into a single point.
        mensal_base["ano_mes_referencia"] = mensal_base["data_referencia"].str.slice(0, 7)

        group_cols = ["ano_eleicao", "nome_candidato_normalizado", "ano_mes_referencia"]

        mensal_base["_peso"] = mensal_base["tamanho_amostra_numero"].fillna(0)
        mensal_base["_produto"] = mensal_base["percentual_numero"] * mensal_base["_peso"]

        agg = mensal_base.groupby(group_cols, as_index=False).agg(
            _soma_produto=("_produto", "sum"),
            _soma_peso=("_peso", "sum"),
            _soma_percentual=("percentual_numero", "sum"),
            _contagem=("percentual_numero", "count"),
        )
        # Weighted mean when the group has any usable sample size (soma_peso >
        # 0); simple mean as fallback (0/0 -> NaN -> fillna) when no row in the
        # month has a parseable tamanho_amostra.
        agg["_percentual_ponderado"] = agg["_soma_produto"] / agg["_soma_peso"]
        agg["_percentual_simples"] = agg["_soma_percentual"] / agg["_contagem"]
        agg["percentual_agregado"] = agg["_percentual_ponderado"].fillna(agg["_percentual_simples"])

        agg["data_referencia"] = agg["ano_mes_referencia"] + "-01"
        agg["mes_referencia"] = agg["ano_mes_referencia"].str.slice(5, 7).astype(int).map(PT_MONTH_NAMES)

        mensal = (
            agg[GOLD_MEDIA_MENSAL_COLUMNS]
            .sort_values(["ano_eleicao", "nome_candidato_normalizado", "data_referencia"])
            .reset_index(drop=True)
        )
    else:
        mensal = pd.DataFrame(columns=GOLD_MEDIA_MENSAL_COLUMNS)

    # Wide comparison: one row per scenario, one column per normalized candidate.
    if not datafolha_base.empty:
        comparativo = (
            datafolha_base.pivot_table(
                index=[
                    "ano_eleicao",
                    "pesquisa_id",
                    "cenario_id",
                    "instituto_pesquisa",
                    "data_referencia",
                ],
                columns="nome_candidato_normalizado",
                values="percentual_numero",
                aggfunc="mean",
            )
            .reset_index()
            .sort_values(["ano_eleicao", "data_referencia", "instituto_pesquisa"])
            .reset_index(drop=True)
        )
        comparativo.columns.name = None
    else:
        comparativo = pd.DataFrame()

    return {
        "temporal": temporal,
        "ultima": ultima,
        "media_movel": daily,
        "media_mensal": mensal,
        "comparativo": comparativo,
    }
