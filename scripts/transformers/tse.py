import os
import sys
from typing import Optional

import pandas as pd

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)

sys.path.append(PARENT_DIR)

from constants_tse import (
    TARGET_CSV_PRESIDENCY_2018,
    TARGET_CSV_PRESIDENCY_2022,
    TARGET_CSV_ELECTORATE_2018,
    TARGET_CSV_ELECTORATE_2022,
    INTEREST_COLUMNS_PRESIDENCY,
    INTEREST_COLUMNS_ELECTORATE,
    CSV_ENCODING,
    CSV_SEPARATOR,
    RAW_DATA_DIR,
)


# Output configuration
PARSED_TSE_DIR = os.path.join(os.path.dirname(RAW_DATA_DIR), "parsed_tse")
PARSED_PRESIDENCY_2018_FILENAME = "parsed_presidencia_2018"
PARSED_PRESIDENCY_2022_FILENAME = "parsed_presidencia_2022"
PARSED_ELECTORATE_2018_FILENAME = "parsed_eleitorado_2018"
PARSED_ELECTORATE_2022_FILENAME = "parsed_eleitorado_2022"


def load_presidency_csv(csv_filename: str) -> Optional[pd.DataFrame]:
    """
    Loads a presidency election CSV file from the raw data directory.

    Args:
        csv_filename: Name of the CSV file to load (e.g., "votacao_candidato_munzona_2018_BR.csv")

    Returns:
        DataFrame with the loaded data, or None if the file does not exist.
    """
    csv_path = os.path.join(RAW_DATA_DIR, csv_filename)

    if not os.path.exists(csv_path):
        print(f"Warning: File {csv_filename} not found in {RAW_DATA_DIR}. Skipping.")
        return None

    try:
        df = pd.read_csv(
            csv_path,
            encoding=CSV_ENCODING,
            sep=CSV_SEPARATOR,
            dtype={"NR_TURNO": "int64", "QT_VOTOS_NOMINAIS": "int64"},
        )
        return df
    except Exception as exc:
        print(f"Error loading {csv_filename}: {exc}")
        return None


def select_interest_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Selects only the columns of interest for presidency analysis.

    Args:
        df: DataFrame to filter

    Returns:
        DataFrame with only the interest columns, in the defined order.
    """
    missing_columns = [col for col in INTEREST_COLUMNS_PRESIDENCY if col not in df.columns]
    if missing_columns:
        print(f"Warning: Missing columns in the data: {missing_columns}")

    available_columns = [col for col in INTEREST_COLUMNS_PRESIDENCY if col in df.columns]
    return df[available_columns].copy()


def clean_presidency_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies cleaning and standardization transformations to presidency data.

    - Removes rows with null values in critical columns
    - Standardizes text fields (strip whitespace, uppercase where appropriate)
    - Ensures data type consistency

    Args:
        df: DataFrame with presidency data

    Returns:
        Cleaned DataFrame
    """
    df = df.copy()

    # Remove rows where critical columns are null
    critical_columns = ["NR_TURNO", "SG_UF", "NM_URNA_CANDIDATO", "QT_VOTOS_NOMINAIS"]
    df = df.dropna(subset=[col for col in critical_columns if col in df.columns])

    # Strip whitespace from string columns
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].str.strip()

    # Remove duplicate rows (if any)
    df = df.drop_duplicates()

    # Ensure vote count is non-negative
    if "QT_VOTOS_NOMINAIS" in df.columns:
        df = df[df["QT_VOTOS_NOMINAIS"] >= 0]

    return df


def transform_presidency_year(csv_filename: str, year: int) -> Optional[pd.DataFrame]:
    """
    Transforms presidency election data for a specific year.

    Args:
        csv_filename: Name of the CSV file to transform
        year: Election year (2018 or 2022)

    Returns:
        Cleaned and transformed DataFrame, or None if processing failed.
    """
    df = load_presidency_csv(csv_filename)
    if df is None:
        return None

    df = select_interest_columns(df)
    df = clean_presidency_data(df)
    print(f"  ✓ {csv_filename}: {len(df)} records loaded and cleaned")

    return df


def save_presidency_data(df: pd.DataFrame, year: int, format: str = "csv") -> bool:
    """
    Saves the transformed presidency dataset to disk.

    Args:
        df: DataFrame to save
        year: Election year (2018 or 2022)
        format: Output format ("csv" or "parquet")

    Returns:
        True if save was successful, False otherwise.
    """
    os.makedirs(PARSED_TSE_DIR, exist_ok=True)

    if year == 2018:
        filename = PARSED_PRESIDENCY_2018_FILENAME
    elif year == 2022:
        filename = PARSED_PRESIDENCY_2022_FILENAME
    else:
        print(f"Error: Unsupported year '{year}'")
        return False

    file_extension = f".{format}"
    output_path = os.path.join(PARSED_TSE_DIR, f"{filename}{file_extension}")

    try:
        if format == "csv":
            df.to_csv(
                output_path,
                encoding=CSV_ENCODING,
                sep=CSV_SEPARATOR,
                index=False,
            )
        elif format == "parquet":
            df.to_parquet(output_path, engine="pyarrow", index=False)
        else:
            print(f"Error: Unsupported format '{format}'")
            return False

        print(f"  ✓ Saved to {output_path}")
        return True
    except Exception as exc:
        print(f"Error saving presidency data for {year}: {exc}")
        return False


def run_presidency_transformation() -> bool:
    """
    Orchestrates the complete presidency transformation pipeline.

    Processes 2018 and 2022 election data separately, generating:
    - data/parsed_tse/parsed_presidencia_2018.csv
    - data/parsed_tse/parsed_presidencia_2022.csv

    Returns:
        True if all transformations and saves were successful, False otherwise.
    """
    print("\nTransforming TSE presidency election data...")

    presidency_configs = [
        (TARGET_CSV_PRESIDENCY_2018, 2018),
        (TARGET_CSV_PRESIDENCY_2022, 2022),
    ]

    all_success = True

    for csv_filename, year in presidency_configs:
        df = transform_presidency_year(csv_filename, year)

        if df is None or df.empty:
            print(f"Error: No data to save for {year}.")
            all_success = False
            continue

        if not save_presidency_data(df, year, format="csv"):
            all_success = False

    return all_success


def load_voter_profile_csv(csv_filename: str) -> Optional[pd.DataFrame]:
    """
    Loads a voter profile CSV file from the raw data directory.

    Args:
        csv_filename: Name of the CSV file to load (e.g., "perfil_eleitorado_2018.csv")

    Returns:
        DataFrame with the loaded data, or None if the file does not exist.
    """
    csv_path = os.path.join(RAW_DATA_DIR, csv_filename)

    if not os.path.exists(csv_path):
        print(f"Warning: File {csv_filename} not found in {RAW_DATA_DIR}. Skipping.")
        return None

    try:
        df = pd.read_csv(
            csv_path,
            encoding=CSV_ENCODING,
            sep=CSV_SEPARATOR,
            dtype={"QT_ELEITORES_PERFIL": "Int64"},
        )
        return df
    except Exception as exc:
        print(f"Error loading {csv_filename}: {exc}")
        return None


def select_voter_profile_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Selects only the columns of interest for voter profile analysis.

    Args:
        df: DataFrame to filter

    Returns:
        DataFrame with only the interest columns, in the defined order.
    """
    missing_columns = [col for col in INTEREST_COLUMNS_ELECTORATE if col not in df.columns]
    if missing_columns:
        print(f"Warning: Missing columns in the data: {missing_columns}")

    available_columns = [col for col in INTEREST_COLUMNS_ELECTORATE if col in df.columns]
    return df[available_columns].copy()


def clean_voter_profile_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies cleaning and standardization transformations to voter profile data.

    - Removes rows with null values in critical columns
    - Standardizes text fields (strip whitespace, uppercase where appropriate)
    - Ensures data type consistency

    Args:
        df: DataFrame with voter profile data

    Returns:
        Cleaned DataFrame
    """
    df = df.copy()

    critical_columns = [
        "SG_UF",
        "CD_MUNICIPIO",
        "NR_ZONA",
        "DS_FAIXA_ETARIA",
        "QT_ELEITORES_PERFIL",
    ]
    df = df.dropna(subset=[col for col in critical_columns if col in df.columns])

    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].str.strip()

    df = df.drop_duplicates()

    if "QT_ELEITORES_PERFIL" in df.columns:
        df["QT_ELEITORES_PERFIL"] = pd.to_numeric(df["QT_ELEITORES_PERFIL"], errors="coerce")
        df = df.dropna(subset=["QT_ELEITORES_PERFIL"])
        df = df[df["QT_ELEITORES_PERFIL"] >= 0]
        df["QT_ELEITORES_PERFIL"] = df["QT_ELEITORES_PERFIL"].astype("int64")

    return df


def transform_voter_profile_data(csv_filename: str, year: int) -> Optional[pd.DataFrame]:
    """
    Transforms voter profile data for a specific year.

    Args:
        csv_filename: Name of the CSV file to transform
        year: Election year (2018 or 2022)

    Returns:
        Cleaned and transformed DataFrame, or None if processing failed.
    """
    df = load_voter_profile_csv(csv_filename)
    if df is None:
        return None

    df = select_voter_profile_columns(df)
    df = clean_voter_profile_data(df)
    print(f"  ✓ {csv_filename}: {len(df)} records loaded and cleaned")

    return df


def save_voter_profile_data(df: pd.DataFrame, year: int, format: str = "csv") -> bool:
    """
    Saves the transformed voter profile dataset to disk.

    Args:
        df: DataFrame to save
        year: Election year (2018 or 2022)
        format: Output format ("csv" or "parquet")

    Returns:
        True if save was successful, False otherwise.
    """
    os.makedirs(PARSED_TSE_DIR, exist_ok=True)

    if year == 2018:
        filename = PARSED_ELECTORATE_2018_FILENAME
    elif year == 2022:
        filename = PARSED_ELECTORATE_2022_FILENAME
    else:
        print(f"Error: Unsupported year '{year}'")
        return False

    file_extension = f".{format}"
    output_path = os.path.join(PARSED_TSE_DIR, f"{filename}{file_extension}")

    try:
        if format == "csv":
            df.to_csv(
                output_path,
                encoding=CSV_ENCODING,
                sep=CSV_SEPARATOR,
                index=False,
            )
        elif format == "parquet":
            df.to_parquet(output_path, engine="pyarrow", index=False)
        else:
            print(f"Error: Unsupported format '{format}'")
            return False

        print(f"  ✓ Saved to {output_path}")
        return True
    except Exception as exc:
        print(f"Error saving voter profile data for {year}: {exc}")
        return False


def run_voter_profile_transformation() -> bool:
    """
    Orchestrates the complete voter profile transformation pipeline.

    Processes 2018 and 2022 voter profile data separately, generating:
    - data/parsed_tse/parsed_eleitorado_2018.csv
    - data/parsed_tse/parsed_eleitorado_2022.csv

    Returns:
        True if all transformations and saves were successful, False otherwise.
    """
    print("\nTransforming TSE voter profile data...")

    electorate_configs = [
        (TARGET_CSV_ELECTORATE_2018, 2018),
        (TARGET_CSV_ELECTORATE_2022, 2022),
    ]

    all_success = True

    for csv_filename, year in electorate_configs:
        df = transform_voter_profile_data(csv_filename, year)

        if df is None or df.empty:
            print(f"Error: No data to save for voter profile {year}.")
            all_success = False
            continue

        if not save_voter_profile_data(df, year, format="csv"):
            all_success = False

    return all_success
