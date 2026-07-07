"""
Constants for the electoral-polls (enquetes) medallion pipeline.

Raw source: ``pesquisas_presidenciais_<ano>.csv`` files produced from the
Wikipedia wikitext in ``votometria/pesquisa-<ano>/``. The pipeline follows the
same architecture as the other sources: extractors -> bronze, transformers ->
prata, loaders -> ouro (Google Sheets tabs, full-refresh / idempotent).
"""

from constants import PROJECT_ROOT

ENQUETES_SOURCE_NAME = "enquetes"

# Election year (folder) -> source folder. The folder year is the *election*
# the table refers to; individual rows may carry an older poll year.
ENQUETES_FOLDERS = {
    2018: PROJECT_ROOT / "pesquisa-2018",
    2022: PROJECT_ROOT / "pesquisa-2022",
    2026: PROJECT_ROOT / "pesquisa-2026",
}
ENQUETES_CSV_TEMPLATE = "pesquisas_presidenciais_{ano}.csv"

# --- worksheet (tab) names per layer ---------------------------------------
BRONZE_TAB_TEMPLATE = "raw_enquetes_{ano}"
PRATA_TAB = "proc_enquetes_long"
VALIDACAO_TAB = "validacao_enquetes"

GOLD_TEMPORAL_TAB = "gold_pesquisas_candidato_temporal"
GOLD_ULTIMA_TAB = "gold_pesquisas_ultima_por_candidato"
GOLD_MEDIA_MOVEL_TAB = "gold_pesquisas_media_movel_candidato"
GOLD_COMPARATIVO_TAB = "gold_pesquisas_comparativo_candidatos"

# Rolling-average window (number of consecutive field dates) used by the moving
# average gold table. A candidate needs at least this many distinct dates to get
# a value; otherwise the moving average is left NULL (never invented).
MEDIA_MOVEL_WINDOW = 3

# --- Portuguese month parsing ----------------------------------------------
PT_MONTHS = {
    "jan": 1, "janeiro": 1,
    "fev": 2, "fevereiro": 2,
    "mar": 3, "março": 3, "marco": 3,
    "abr": 4, "abril": 4,
    "mai": 5, "maio": 5,
    "jun": 6, "junho": 6,
    "jul": 7, "julho": 7,
    "ago": 8, "agosto": 8,
    "set": 9, "setembro": 9,
    "out": 10, "outubro": 10,
    "nov": 11, "novembro": 11,
    "dez": 12, "dezembro": 12,
}

# Month number -> capitalized Portuguese month name. Used to rewrite the
# ``mes_referencia`` of trimester-labelled 2022 rows into the actual month
# (derived from the poll end date), matching the format used by the other years.
PT_MONTH_NAMES = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
}

# Tokens that mean "no value" in a percentage cell -> NULL (never 0).
PERCENT_NULL_TOKENS = {"", "-", "–", "—", "n/a", "{{n/a}}", "na"}
