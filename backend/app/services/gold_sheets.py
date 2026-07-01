"""
Reads Polymarket data from the gold (ouro) spreadsheet published by the data
pipeline, replacing the former PostgreSQL source for the market-expectations
endpoints. The gold tab is fetched as CSV from the public gviz endpoint (no
credentials required when the sheet is shared by link / published) and cached
in-process with a short TTL so the API does not hit Google Sheets on every
request.
"""

import io
import time
from urllib.parse import urlencode

import pandas as pd
import requests

from app.core.config import get_ouro_sheet_id

POLYMARKET_GOLD_TAB = "proc_polymarket_probabilities"
_CACHE_TTL_SECONDS = 300
_cache: dict[str, tuple[float, pd.DataFrame]] = {}

REQUIRED_COLUMNS = (
    "candidate_catalog_id",
    "candidate_name",
    "display_name",
    "market_id",
    "probability",
    "timestamp",
)


def _gviz_csv_url(tab_name: str) -> str:
    sheet_id = get_ouro_sheet_id()
    params = urlencode({"tqx": "out:csv", "sheet": tab_name})
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?{params}"


def load_polymarket_gold(*, force_refresh: bool = False) -> pd.DataFrame:
    """
    Returns the consolidated Polymarket probability series from the gold tab as a
    cleaned DataFrame. Cached for ``_CACHE_TTL_SECONDS`` between calls.
    """
    now = time.monotonic()
    cached = _cache.get(POLYMARKET_GOLD_TAB)
    if cached and not force_refresh and (now - cached[0]) < _CACHE_TTL_SECONDS:
        return cached[1]

    response = requests.get(_gviz_csv_url(POLYMARKET_GOLD_TAB), timeout=30)
    response.raise_for_status()

    df = pd.read_csv(io.StringIO(response.text))

    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise RuntimeError(
            f"Gold tab '{POLYMARKET_GOLD_TAB}' is missing columns: {missing}."
        )

    df["candidate_catalog_id"] = pd.to_numeric(
        df["candidate_catalog_id"], errors="coerce"
    ).astype("Int64")
    df["market_id"] = df["market_id"].astype(str)
    df["candidate_name"] = df["candidate_name"].astype(str)
    df["display_name"] = df["display_name"].astype(str)
    df["probability"] = pd.to_numeric(df["probability"], errors="coerce")
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    df = df.dropna(
        subset=["candidate_catalog_id", "probability", "timestamp"]
    ).reset_index(drop=True)
    df["candidate_catalog_id"] = df["candidate_catalog_id"].astype(int)

    _cache[POLYMARKET_GOLD_TAB] = (now, df)
    return df
