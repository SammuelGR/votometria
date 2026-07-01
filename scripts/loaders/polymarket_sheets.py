"""
Publishes the Polymarket datasets to the medallion spreadsheets, replacing the
former PostgreSQL persistence. The pipeline is stateless: every run refetches
the full price history and fully rewrites the tabs.

    bronze -> raw markets + raw price-history points
    prata  -> parsed probability records (long)
    ouro   -> consolidated probability series (read by the backend API)
"""

from typing import List

import pandas as pd

from core.sheets import write_dataframe_to_tab
from transformers.polymarket import PolymarketMarket, PolymarketProbabilityRecord

RAW_MARKETS_TAB = "raw_polymarket_markets"
RAW_HISTORY_TAB = "raw_polymarket_price_history"
PARSED_TAB = "proc_polymarket_probabilities_long"
GOLD_TAB = "proc_polymarket_probabilities"


def save_raw_markets_to_bronze(spreadsheet, markets: List[PolymarketMarket]) -> str:
    df = pd.DataFrame(
        [
            {
                "market_id": market.market_id,
                "candidate_name": market.candidate_name,
                "yes_token_id": market.yes_token_id,
            }
            for market in markets
        ]
    )
    write_dataframe_to_tab(spreadsheet, RAW_MARKETS_TAB, df)
    return RAW_MARKETS_TAB


def save_raw_history_to_bronze(spreadsheet, rows: List[dict]) -> str:
    """
    ``rows`` are ``{market_id, candidate_name, t, p}`` raw price-history points.
    """
    df = pd.DataFrame(rows, columns=["market_id", "candidate_name", "t", "p"])
    write_dataframe_to_tab(spreadsheet, RAW_HISTORY_TAB, df)
    return RAW_HISTORY_TAB


def _records_to_dataframe(records: List[PolymarketProbabilityRecord]) -> pd.DataFrame:
    df = pd.DataFrame(
        [
            {
                "candidate_catalog_id": record.candidate_catalog_id,
                "candidate_name": record.candidate_name,
                "display_name": record.candidate_name,
                "market_id": record.market_id,
                "probability": record.probability,
                "timestamp": record.timestamp.isoformat(sep=" "),
            }
            for record in records
        ],
        columns=[
            "candidate_catalog_id",
            "candidate_name",
            "display_name",
            "market_id",
            "probability",
            "timestamp",
        ],
    )
    if not df.empty:
        df = df.sort_values(
            ["candidate_catalog_id", "market_id", "timestamp"]
        ).reset_index(drop=True)
    return df


def save_records_to_prata(spreadsheet, records: List[PolymarketProbabilityRecord]) -> str:
    write_dataframe_to_tab(spreadsheet, PARSED_TAB, _records_to_dataframe(records))
    return PARSED_TAB


def save_records_to_ouro(spreadsheet, records: List[PolymarketProbabilityRecord]) -> str:
    """
    Writes the consolidated probability series to the gold layer. Same long shape
    as the silver tab; this is the table the backend API reads to serve the
    market-expectations endpoints.
    """
    write_dataframe_to_tab(spreadsheet, GOLD_TAB, _records_to_dataframe(records))
    return GOLD_TAB
