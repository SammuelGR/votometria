import re
import unicodedata
from datetime import datetime
from itertools import groupby

from sqlalchemy.orm import Session

from app.models import CandidateCatalog, PolymarketProbability
from app.schemas.monthly_market_expectations import (
    MonthlyMarketExpectationPoint,
    MonthlyMarketExpectationsResponse,
)


CURRENT_ELECTION_START = datetime(2026, 1, 1)


def get_monthly_market_expectations(
    db: Session,
    *,
    candidate: str,
) -> MonthlyMarketExpectationsResponse:
    normalized_candidate = _normalize_candidate(candidate)

    if not normalized_candidate:
        return MonthlyMarketExpectationsResponse(points=[])

    records = (
        db.query(PolymarketProbability)
        .join(PolymarketProbability.candidate_catalog)
        .filter(CandidateCatalog.source == "polymarket")
        .filter(CandidateCatalog.normalized_name.contains(normalized_candidate))
        .filter(PolymarketProbability.timestamp >= CURRENT_ELECTION_START)
        .order_by(
            PolymarketProbability.candidate_catalog_id.asc(),
            PolymarketProbability.timestamp.asc(),
        )
        .all()
    )

    if not records:
        return MonthlyMarketExpectationsResponse(points=[])

    selected_candidate_id = _select_candidate_catalog_id(records)
    selected_records = [
        record
        for record in records
        if record.candidate_catalog_id == selected_candidate_id
    ]

    return MonthlyMarketExpectationsResponse(
        points=_build_monthly_closing_points(selected_records)
    )


def _normalize_candidate(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    without_accents = "".join(
        character
        for character in decomposed
        if not unicodedata.combining(character)
    )
    lowered = without_accents.lower()
    without_punctuation = re.sub(r"[^\w\s]", " ", lowered)
    return re.sub(r"\s+", " ", without_punctuation).strip()


def _select_candidate_catalog_id(records: list[PolymarketProbability]) -> int:
    latest_records = [
        max(candidate_records, key=lambda record: record.timestamp)
        for _, candidate_records in groupby(
            records,
            key=lambda record: record.candidate_catalog_id,
        )
    ]
    selected_record = min(
        latest_records,
        key=lambda record: (-record.probability, record.candidate_catalog.display_name),
    )

    return selected_record.candidate_catalog_id


def _build_monthly_closing_points(
    records: list[PolymarketProbability],
) -> list[MonthlyMarketExpectationPoint]:
    return [
        MonthlyMarketExpectationPoint(
            date=f"{year}-{month:02d}-01",
            probability=latest_record.probability * 100,
        )
        for (year, month), month_records in groupby(
            records,
            key=lambda record: (record.timestamp.year, record.timestamp.month),
        )
        for latest_record in [max(month_records, key=lambda record: record.timestamp)]
    ]
