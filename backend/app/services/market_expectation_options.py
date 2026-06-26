from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import CandidateCatalog, PolymarketProbability
from app.schemas.market_expectation_options import (
    MarketExpectationDateRange,
    MarketExpectationOptionCandidate,
    MarketExpectationOptionsResponse,
)
from app.services.market_expectations import SUPPORTED_MARKET_EXPECTATION_INTERVALS


DEFAULT_MARKET_EXPECTATION_CANDIDATE_LIMIT = 5


def get_market_expectation_options(db: Session) -> MarketExpectationOptionsResponse:
    min_timestamp, max_timestamp = _get_market_expectation_date_range(db)
    candidates = _get_market_expectation_candidates(db)

    return MarketExpectationOptionsResponse(
        date_range=MarketExpectationDateRange(
            min=min_timestamp,
            max=max_timestamp,
        ),
        intervals=list(SUPPORTED_MARKET_EXPECTATION_INTERVALS),
        candidates=candidates,
        default_candidate_catalog_ids=[
            candidate.candidate_catalog_id
            for candidate in candidates[:DEFAULT_MARKET_EXPECTATION_CANDIDATE_LIMIT]
        ],
    )


def _get_market_expectation_date_range(db: Session):
    return (
        db.query(
            func.min(PolymarketProbability.timestamp),
            func.max(PolymarketProbability.timestamp),
        )
        .one()
    )


def _get_market_expectation_candidates(
    db: Session,
) -> list[MarketExpectationOptionCandidate]:
    latest_record_rank = func.row_number().over(
        partition_by=PolymarketProbability.candidate_catalog_id,
        order_by=PolymarketProbability.timestamp.desc(),
    )
    latest_records_by_candidate = (
        db.query(
            PolymarketProbability.id.label("probability_id"),
            latest_record_rank.label("row_number"),
        )
        .subquery()
    )
    candidates = (
        db.query(
            CandidateCatalog.id,
            CandidateCatalog.display_name,
            PolymarketProbability.probability.label("latest_probability"),
        )
        .join(
            latest_records_by_candidate,
            latest_records_by_candidate.c.probability_id == PolymarketProbability.id,
        )
        .join(
            CandidateCatalog,
            CandidateCatalog.id == PolymarketProbability.candidate_catalog_id,
        )
        .filter(latest_records_by_candidate.c.row_number == 1)
        .order_by(
            PolymarketProbability.probability.desc(),
            CandidateCatalog.display_name.asc(),
        )
        .all()
    )

    return [
        MarketExpectationOptionCandidate(
            candidate_catalog_id=candidate.id,
            display_name=candidate.display_name,
            latest_probability=candidate.latest_probability,
        )
        for candidate in candidates
    ]
