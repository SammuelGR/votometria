"""
Publishes the Google Trends datasets straight to the destination Google Sheets
spreadsheet — one worksheet per dataset, with no CSV files written to disk.

Raw batches and processed datasets go to separate, clearly-prefixed tabs so the
two layers stay visibly apart in the spreadsheet:

    raw_*   -> raw batches collected from Google Trends
    proc_*  -> consolidated, rescaled long datasets
"""

import pandas as pd

from core.sheets import write_dataframe_to_tab

ALL_ELECTIONS_BASE_NAME = "google_trends_all_elections_interest_long"

# Worksheet name prefixes that keep raw and processed data visibly separated.
RAW_TAB_PREFIX = "raw_"
PROCESSED_TAB_PREFIX = "proc_"


def save_raw_google_trends_batch(
    spreadsheet,
    df: pd.DataFrame,
    election_year: str,
    batch_id: str,
) -> str:
    """
    Writes one raw Google Trends batch to a ``raw_*`` worksheet with minimal
    changes, only promoting the date index to a ``date`` column.

    Worksheet name: ``raw_google_trends_{election_year}_{batch_id}``.
    Returns the worksheet title.
    """
    raw_df = df.reset_index()
    raw_df = raw_df.rename(columns={raw_df.columns[0]: "date"})

    title = f"{RAW_TAB_PREFIX}google_trends_{election_year}_{batch_id}"
    write_dataframe_to_tab(spreadsheet, title, raw_df)
    return title


def save_processed_google_trends_year(
    spreadsheet,
    df: pd.DataFrame,
    election_year: str,
) -> str:
    """
    Writes the consolidated, rescaled long DataFrame of a single election year
    to a ``proc_*`` worksheet.

    Worksheet name: ``proc_google_trends_{election_year}_interest_long``.
    Returns the worksheet title.
    """
    title = f"{PROCESSED_TAB_PREFIX}google_trends_{election_year}_interest_long"
    write_dataframe_to_tab(spreadsheet, title, df)
    return title


def save_processed_google_trends_all(spreadsheet, df: pd.DataFrame) -> str:
    """
    Writes the consolidated long DataFrame across all election years to a
    ``proc_*`` worksheet.

    Worksheet name: ``proc_google_trends_all_elections_interest_long``.
    Returns the worksheet title.
    """
    title = f"{PROCESSED_TAB_PREFIX}{ALL_ELECTIONS_BASE_NAME}"
    write_dataframe_to_tab(spreadsheet, title, df)
    return title
