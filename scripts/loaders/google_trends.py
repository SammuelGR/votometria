import os
from datetime import datetime

import pandas as pd

ALL_ELECTIONS_BASE_NAME = "google_trends_all_elections_interest_long"


def _save_with_snapshot(df: pd.DataFrame, output_dir: str, base_name: str) -> str:
    """
    Saves the DataFrame as the canonical CSV plus a timestamped snapshot so that
    executions are not silently overwritten. Returns the canonical file path.
    """
    os.makedirs(output_dir, exist_ok=True)

    canonical_path = os.path.join(output_dir, f"{base_name}.csv")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_path = os.path.join(output_dir, f"{base_name}_{timestamp}.csv")

    df.to_csv(canonical_path, index=False, encoding="utf-8")
    df.to_csv(snapshot_path, index=False, encoding="utf-8")

    return canonical_path


def save_raw_google_trends_batch_csv(
    df: pd.DataFrame,
    output_dir: str,
    election_year: str,
    batch_id: str,
) -> str:
    """
    Saves one raw Google Trends batch to ``/dados-brutos`` with minimal changes,
    only promoting the date index to a ``date`` column.

    File name: ``google_trends_{election_year}_{batch_id}.csv``.
    """
    raw_df = df.reset_index()
    raw_df = raw_df.rename(columns={raw_df.columns[0]: "date"})
    base_name = f"google_trends_{election_year}_{batch_id}"
    return _save_with_snapshot(raw_df, output_dir, base_name)


def save_processed_google_trends_year_csv(
    df: pd.DataFrame,
    output_dir: str,
    election_year: str,
) -> str:
    """
    Saves the consolidated, rescaled long DataFrame of a single election year to
    ``/dados-processados``.

    File name: ``google_trends_{election_year}_interest_long.csv``.
    """
    base_name = f"google_trends_{election_year}_interest_long"
    return _save_with_snapshot(df, output_dir, base_name)


def save_processed_google_trends_all_csv(df: pd.DataFrame, output_dir: str) -> str:
    """
    Saves the consolidated long DataFrame across all election years to
    ``/dados-processados``.

    File name: ``google_trends_all_elections_interest_long.csv``.
    """
    return _save_with_snapshot(df, output_dir, ALL_ELECTIONS_BASE_NAME)
