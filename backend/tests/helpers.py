from datetime import datetime

from app.models import CandidateCatalog, PolymarketProbability
from app.schemas.market_expectations import MarketExpectationPoint, MarketExpectationSeries


def candidate_catalog(
    candidate_id=1,
    display_name="Candidate A",
    source_key="market-1",
):
    return CandidateCatalog(
        id=candidate_id,
        source="polymarket",
        source_key=source_key,
        raw_name=display_name,
        display_name=display_name,
        normalized_name=display_name.lower(),
        full_name=display_name,
    )


def polymarket_probability(
    candidate_catalog_id=1,
    candidate_name="Candidate A",
    market_id="market-1",
    probability=0.25,
    timestamp=datetime(2024, 1, 1, 10),
):
    return PolymarketProbability(
        candidate_catalog_id=candidate_catalog_id,
        candidate_name=candidate_name,
        probability=probability,
        timestamp=timestamp,
        market_id=market_id,
    )


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
