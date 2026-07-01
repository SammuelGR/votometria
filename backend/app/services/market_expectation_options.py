"""
Options endpoint for the market-expectations module, backed by the gold (ouro)
spreadsheet instead of PostgreSQL.
"""

import pandas as pd

from app.schemas.market_expectation_options import (
    MarketExpectationDateRange,
    MarketExpectationOptionCandidate,
    MarketExpectationOptionsResponse,
)
from app.services import gold_sheets
from app.services.market_expectations import SUPPORTED_MARKET_EXPECTATION_INTERVALS

DEFAULT_MARKET_EXPECTATION_CANDIDATE_LIMIT = 5


def get_market_expectation_options(
    df: pd.DataFrame | None = None,
) -> MarketExpectationOptionsResponse:
    if df is None:
        df = gold_sheets.load_polymarket_gold()

    min_timestamp = None if df.empty else df["timestamp"].min().to_pydatetime()
    max_timestamp = None if df.empty else df["timestamp"].max().to_pydatetime()
    candidates = _get_candidates(df)

    return MarketExpectationOptionsResponse(
        date_range=MarketExpectationDateRange(min=min_timestamp, max=max_timestamp),
        intervals=list(SUPPORTED_MARKET_EXPECTATION_INTERVALS),
        candidates=candidates,
        default_candidate_catalog_ids=[
            candidate.candidate_catalog_id
            for candidate in candidates[:DEFAULT_MARKET_EXPECTATION_CANDIDATE_LIMIT]
        ],
    )


def _get_candidates(df: pd.DataFrame) -> list[MarketExpectationOptionCandidate]:
    if df.empty:
        return []

    latest_idx = df.groupby("candidate_catalog_id")["timestamp"].idxmax()
    latest = df.loc[latest_idx].sort_values(
        ["probability", "display_name"], ascending=[False, True]
    )

    return [
        MarketExpectationOptionCandidate(
            candidate_catalog_id=int(row.candidate_catalog_id),
            display_name=str(row.display_name),
            latest_probability=float(row.probability),
        )
        for row in latest.itertuples(index=False)
    ]
