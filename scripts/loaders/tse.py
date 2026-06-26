import os
import sys
from typing import Optional

import pandas as pd

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)

sys.path.append(PARENT_DIR)

from constants_tse import (
    CSV_ENCODING,
    CSV_SEPARATOR,
    OUTPUT_CSV_COMPARACAO_TURNOS_2018,
    OUTPUT_CSV_COMPARACAO_TURNOS_2022,
    OUTPUT_CSV_DISTRIBUICAO_ESTADO_TURNO_1_2018,
    OUTPUT_CSV_DISTRIBUICAO_ESTADO_TURNO_1_2022,
    OUTPUT_CSV_DISTRIBUICAO_ESTADO_TURNO_2_2018,
    OUTPUT_CSV_DISTRIBUICAO_ESTADO_TURNO_2_2022,
    OUTPUT_CSV_PRESIDENCY_2018,
    OUTPUT_CSV_PRESIDENCY_2022,
    OUTPUT_CSV_VOTOS_CANDIDATOS_TURNO_1_2018,
    OUTPUT_CSV_VOTOS_CANDIDATOS_TURNO_1_2022,
    OUTPUT_CSV_VOTOS_CANDIDATOS_TURNO_2_2018,
    OUTPUT_CSV_VOTOS_CANDIDATOS_TURNO_2_2022,
    RAW_DATA_DIR,
)

PARSED_TSE_DIR = os.path.join(os.path.dirname(RAW_DATA_DIR), "parsed_tse")
TABLES_DIR = os.path.join(os.path.dirname(RAW_DATA_DIR), "tables")


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


def ensure_tables_directory() -> None:
    """
    Ensures that the table output directory exists.
    """
    os.makedirs(TABLES_DIR, exist_ok=True)


def save_table(df: pd.DataFrame, filename: str) -> None:
    """
    Saves a DataFrame to the tables output directory.
    """
    output_path = os.path.join(TABLES_DIR, filename)
    df.to_csv(output_path, index=False, encoding=CSV_ENCODING, sep=CSV_SEPARATOR)
    print(f"  ✓ Saved table: {output_path}")


def save_candidate_votes_by_round(year: int) -> None:
    """
    Saves candidate vote totals by round for a given election year.
    """
    filename = OUTPUT_CSV_PRESIDENCY_2018 if year == 2018 else OUTPUT_CSV_PRESIDENCY_2022
    df = load_parsed_presidency_csv(filename)
    if df is None:
        return

    for turno in sorted(df["NR_TURNO"].unique()):
        table = (
            df[df["NR_TURNO"] == turno]
            .groupby("NM_URNA_CANDIDATO", as_index=False)["QT_VOTOS_NOMINAIS"]
            .sum()
            .sort_values("QT_VOTOS_NOMINAIS", ascending=False)
        )

        table.loc[len(table)] = {
            "NM_URNA_CANDIDATO": "SOMA",
            "QT_VOTOS_NOMINAIS": table["QT_VOTOS_NOMINAIS"].sum()
        }

        output_filename = (
            OUTPUT_CSV_VOTOS_CANDIDATOS_TURNO_1_2018
            if year == 2018 and turno == 1
            else OUTPUT_CSV_VOTOS_CANDIDATOS_TURNO_2_2018
            if year == 2018
            else OUTPUT_CSV_VOTOS_CANDIDATOS_TURNO_1_2022
            if turno == 1
            else OUTPUT_CSV_VOTOS_CANDIDATOS_TURNO_2_2022
        )
        save_table(table, output_filename)


def save_state_vote_distribution_by_round(year: int) -> None:
    """
    Saves state vote distribution tables by round for a given election year.
    """
    filename = OUTPUT_CSV_PRESIDENCY_2018 if year == 2018 else OUTPUT_CSV_PRESIDENCY_2022
    df = load_parsed_presidency_csv(filename)
    if df is None:
        return

    for turno in sorted(df["NR_TURNO"].unique()):
        table = (
            df[df["NR_TURNO"] == turno]
            .pivot_table(
                index="SG_UF",
                columns="NM_URNA_CANDIDATO",
                values="QT_VOTOS_NOMINAIS",
                aggfunc="sum",
                fill_value=0
            )
            .sort_index()
        )

        table["SOMA"] = table.sum(axis=1)
        table.loc["QT"] = table.sum(axis=0)

        output_filename = (
            OUTPUT_CSV_DISTRIBUICAO_ESTADO_TURNO_1_2018
            if year == 2018 and turno == 1
            else OUTPUT_CSV_DISTRIBUICAO_ESTADO_TURNO_2_2018
            if year == 2018
            else OUTPUT_CSV_DISTRIBUICAO_ESTADO_TURNO_1_2022
            if turno == 1
            else OUTPUT_CSV_DISTRIBUICAO_ESTADO_TURNO_2_2022
        )
        save_table(table.reset_index(), output_filename)


def save_round_comparison(year: int) -> None:
    """
    Saves the round comparison table for a given election year.
    """
    filename = OUTPUT_CSV_PRESIDENCY_2018 if year == 2018 else OUTPUT_CSV_PRESIDENCY_2022
    df = load_parsed_presidency_csv(filename)
    if df is None:
        return

    second_round_candidates = (
        df.loc[df["NR_TURNO"] == 2, "NM_URNA_CANDIDATO"]
        .unique()
    )

    comparison = (
        df[df["NM_URNA_CANDIDATO"].isin(second_round_candidates)]
        .groupby(["NM_URNA_CANDIDATO", "NR_TURNO"])["QT_VOTOS_NOMINAIS"]
        .sum()
        .unstack(fill_value=0)
    )

    comparison.columns = ["QT_VOTOS_1T", "QT_VOTOS_2T"]

    comparison["DIFERENCA"] = (
        comparison["QT_VOTOS_2T"] -
        comparison["QT_VOTOS_1T"]
    )

    comparison = (
        comparison
        .reset_index()
        .sort_values("QT_VOTOS_2T", ascending=False)
    )

    output_filename = OUTPUT_CSV_COMPARACAO_TURNOS_2018 if year == 2018 else OUTPUT_CSV_COMPARACAO_TURNOS_2022
    save_table(comparison, output_filename)


def run_tse_load() -> bool:
    """
    Orchestrates the load stage for TSE aggregated tables.
    """
    print("\nLoading TSE aggregated tables...")
    ensure_tables_directory()

    success = True
    for year in [2018, 2022]:
        try:
            save_candidate_votes_by_round(year)
            save_state_vote_distribution_by_round(year)
            save_round_comparison(year)
        except Exception as exc:
            print(f"Error loading tables for {year}: {exc}")
            success = False

    return success
