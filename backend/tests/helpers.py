from datetime import datetime

import pandas as pd

from app.schemas.market_expectations import MarketExpectationPoint, MarketExpectationSeries

GOLD_COLUMNS = [
    "candidate_catalog_id",
    "candidate_name",
    "display_name",
    "market_id",
    "probability",
    "timestamp",
]


def empty_gold_dataframe() -> pd.DataFrame:
    df = pd.DataFrame(columns=GOLD_COLUMNS)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def gold_row(
    candidate_catalog_id=1,
    candidate_name="Candidate A",
    display_name=None,
    market_id="market-1",
    probability=0.25,
    timestamp=datetime(2024, 1, 1, 10),
):
    return {
        "candidate_catalog_id": candidate_catalog_id,
        "candidate_name": candidate_name,
        "display_name": display_name or candidate_name,
        "market_id": market_id,
        "probability": probability,
        "timestamp": timestamp,
    }


def gold_dataframe(rows) -> pd.DataFrame:
    """
    Builds a gold-layer DataFrame (same schema the backend reads from the ouro
    tab) from a list of ``gold_row`` dicts.
    """
    if not rows:
        return empty_gold_dataframe()

    df = pd.DataFrame(rows, columns=GOLD_COLUMNS)
    df["candidate_catalog_id"] = df["candidate_catalog_id"].astype(int)
    df["market_id"] = df["market_id"].astype(str)
    df["probability"] = df["probability"].astype(float)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def market_expectation_point(
    timestamp=datetime(2024, 1, 1, 10),
    probability=0.25,
):
    return MarketExpectationPoint(timestamp=timestamp, probability=probability)


def market_expectation_series(
    candidate_catalog_id=1,
    candidate_name="Candidate A",
    display_name="Candidate A",
    market_id="market-1",
    points=None,
):
    return MarketExpectationSeries(
        candidate_catalog_id=candidate_catalog_id,
        candidate_name=candidate_name,
        display_name=display_name,
        market_id=market_id,
        points=points or [],
    )
