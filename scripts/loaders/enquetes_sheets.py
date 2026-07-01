"""
Publishes the enquetes datasets to the medallion spreadsheets, one tab per
dataset. Every write fully replaces the tab (full-refresh), so re-running the
pipeline is idempotent.

    bronze -> raw_enquetes_<ano>
    prata  -> proc_enquetes_long + validacao_enquetes
    ouro   -> gold_pesquisas_candidato_temporal / _ultima_por_candidato /
              _media_movel_candidato / _comparativo_candidatos
"""

from core.sheets import write_dataframe_to_tab
from constants_enquetes import (
    BRONZE_TAB_TEMPLATE,
    GOLD_COMPARATIVO_TAB,
    GOLD_MEDIA_MOVEL_TAB,
    GOLD_TEMPORAL_TAB,
    GOLD_ULTIMA_TAB,
    PRATA_TAB,
    VALIDACAO_TAB,
)


def save_bronze(spreadsheet, df, ano) -> str:
    title = BRONZE_TAB_TEMPLATE.format(ano=ano)
    write_dataframe_to_tab(spreadsheet, title, df)
    return title


def save_prata(spreadsheet, df) -> str:
    write_dataframe_to_tab(spreadsheet, PRATA_TAB, df)
    return PRATA_TAB


def save_validation(spreadsheet, df) -> str:
    write_dataframe_to_tab(spreadsheet, VALIDACAO_TAB, df)
    return VALIDACAO_TAB


def save_gold(spreadsheet, gold: dict) -> list:
    written = []
    for key, title in (
        ("temporal", GOLD_TEMPORAL_TAB),
        ("ultima", GOLD_ULTIMA_TAB),
        ("media_movel", GOLD_MEDIA_MOVEL_TAB),
        ("comparativo", GOLD_COMPARATIVO_TAB),
    ):
        df = gold.get(key)
        if df is None or df.empty:
            print(f"Warning: gold table '{title}' is empty; skipping.")
            continue
        write_dataframe_to_tab(spreadsheet, title, df)
        written.append(title)
    return written
