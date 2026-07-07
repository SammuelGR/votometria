import os
from typing import Optional

import pandas as pd

from core.sheets import get_layer_spreadsheets, write_dataframe_to_tab
from constants_tse import (
    CSV_ENCODING,
    CSV_SEPARATOR,
    OUTPUT_CSV_PRESIDENCY_2018,
    OUTPUT_CSV_PRESIDENCY_2022,
    PARSED_TSE_DIR,
)

RAW_TAB_PREFIX = "raw_"
PROCESSED_TAB_PREFIX = "proc_"
TSE_BASE_NAME = "tse"


def load_parsed_presidency_csv(filename: str) -> Optional[pd.DataFrame]:
    """
    Loads a transformed presidency CSV file from the parsed output directory.
    """
    file_path = os.path.join(PARSED_TSE_DIR, filename)
    if not os.path.exists(file_path):
        print(f"Warning: Parsed presidency file not found: {file_path}")
        return None

    try:
        return pd.read_csv(
            file_path,
            encoding=CSV_ENCODING,
            sep=CSV_SEPARATOR,
        )
    except Exception as exc:
        print(f"Error loading parsed presidency CSV {file_path}: {exc}")
        return None


def _candidate_votes_table(df: pd.DataFrame) -> pd.DataFrame:
    table = (
        df.groupby("NM_URNA_CANDIDATO", as_index=False)["QT_VOTOS_NOMINAIS"]
        .sum()
        .sort_values("QT_VOTOS_NOMINAIS", ascending=False)
        .reset_index(drop=True)
    )
    table.loc[len(table)] = {
        "NM_URNA_CANDIDATO": "SOMA",
        "QT_VOTOS_NOMINAIS": table["QT_VOTOS_NOMINAIS"].sum(),
    }
    return table


def _state_distribution_table(df: pd.DataFrame) -> pd.DataFrame:
    table = (
        df.pivot_table(
            index="SG_UF",
            columns="NM_URNA_CANDIDATO",
            values="QT_VOTOS_NOMINAIS",
            aggfunc="sum",
            fill_value=0,
        )
        .sort_index()
    )
    table["SOMA"] = table.sum(axis=1)
    table.loc["QT"] = table.sum(axis=0)
    return table.reset_index()


def _round_comparison_table(df: pd.DataFrame) -> pd.DataFrame:
    second_round_candidates = (
        df.loc[df["NR_TURNO"] == 2, "NM_URNA_CANDIDATO"].unique()
    )
    comparison = (
        df[df["NM_URNA_CANDIDATO"].isin(second_round_candidates)]
        .groupby(["NM_URNA_CANDIDATO", "NR_TURNO"])["QT_VOTOS_NOMINAIS"]
        .sum()
        .unstack(fill_value=0)
    )

    if isinstance(comparison.columns, pd.MultiIndex):
        turn_columns = [str(turno) for turno in comparison.columns.get_level_values(1)]
    else:
        turn_columns = [str(turno) for turno in comparison.columns]

    renamed_columns = []
    for turno in turn_columns:
        renamed_columns.append(f"QT_VOTOS_{turno}T")

    comparison.columns = renamed_columns
    for turno in [1, 2]:
        column_name = f"QT_VOTOS_{turno}T"
        if column_name not in comparison.columns:
            comparison[column_name] = 0

    comparison["DIFERENCA"] = (
        comparison.get("QT_VOTOS_2T", 0) - comparison.get("QT_VOTOS_1T", 0)
    )
    return comparison.reset_index().sort_values("QT_VOTOS_2T", ascending=False)


def save_raw_presidency_to_sheets(spreadsheet, df: pd.DataFrame, year: int) -> str:
    """
    Writes the parsed presidency source data to a raw worksheet.
    """
    title = f"{RAW_TAB_PREFIX}{TSE_BASE_NAME}_presidency_{year}"
    write_dataframe_to_tab(spreadsheet, title, df)
    return title


def save_presidency_round_to_sheets(
    spreadsheet,
    df: pd.DataFrame,
    year: int,
    turno: int,
) -> str:
    """
    Writes the cleaned, per-round presidency rows to a worksheet (silver layer).
    """
    title = f"{PROCESSED_TAB_PREFIX}{TSE_BASE_NAME}_{year}_presidency_t{turno}"
    write_dataframe_to_tab(spreadsheet, title, df)
    return title


def save_candidate_votes_by_round_to_sheets(
    spreadsheet,
    df: pd.DataFrame,
    year: int,
    turno: int,
) -> str:
    """
    Writes a candidate vote totals table to a Google Sheets worksheet.
    """
    table = _candidate_votes_table(df)
    title = (
        f"{PROCESSED_TAB_PREFIX}{TSE_BASE_NAME}_{year}_votes_t1"
        if turno == 1
        else f"{PROCESSED_TAB_PREFIX}{TSE_BASE_NAME}_{year}_votes_t2"
    )
    write_dataframe_to_tab(spreadsheet, title, table)
    return title


def save_state_vote_distribution_by_round_to_sheets(
    spreadsheet,
    df: pd.DataFrame,
    year: int,
    turno: int,
) -> str:
    """
    Writes a state vote distribution table to a Google Sheets worksheet.
    """
    table = _state_distribution_table(df)
    title = (
        f"{PROCESSED_TAB_PREFIX}{TSE_BASE_NAME}_{year}_state_dist_t1"
        if turno == 1
        else f"{PROCESSED_TAB_PREFIX}{TSE_BASE_NAME}_{year}_state_dist_t2"
    )
    write_dataframe_to_tab(spreadsheet, title, table)
    return title


def save_round_comparison_to_sheets(
    spreadsheet,
    df: pd.DataFrame,
    year: int,
) -> str:
    """
    Writes a round comparison table to a Google Sheets worksheet.
    """
    table = _round_comparison_table(df)
    title = f"{PROCESSED_TAB_PREFIX}{TSE_BASE_NAME}_{year}_comparison"
    write_dataframe_to_tab(spreadsheet, title, table)
    return title


def run_tse_load_to_sheets(layers: dict | None = None) -> bool:
    """
    Orchestrates the TSE load stage across the medallion layers:

        bronze -> raw parsed presidency source rows
        prata  -> cleaned, per-round presidency rows
        ouro   -> business aggregations (votes, state distribution, comparison)
    """
    print("\nLoading TSE tables to Google Sheets (bronze/prata/ouro)...")

    if layers is None:
        layers = get_layer_spreadsheets("bronze", "prata", "ouro")

    success = True
    for year in [2018, 2022]:
        try:
            filename = OUTPUT_CSV_PRESIDENCY_2018 if year == 2018 else OUTPUT_CSV_PRESIDENCY_2022
            df = load_parsed_presidency_csv(filename)
            if df is None:
                continue

            # Extractor output -> bronze.
            save_raw_presidency_to_sheets(layers["bronze"], df, year)

            for turno in sorted(df["NR_TURNO"].unique()):
                round_df = df[df["NR_TURNO"] == turno]
                # Transformer output (cleaned, per-round) -> prata.
                save_presidency_round_to_sheets(layers["prata"], round_df, year, int(turno))
                # Loader output (aggregations) -> ouro.
                save_candidate_votes_by_round_to_sheets(layers["ouro"], round_df, year, int(turno))
                save_state_vote_distribution_by_round_to_sheets(layers["ouro"], round_df, year, int(turno))

            save_round_comparison_to_sheets(layers["ouro"], df, year)
        except Exception as exc:
            print(f"Error loading TSE tables to sheets for {year}: {exc}")
            success = False

    return success
