from sqlalchemy import func, tuple_
from sqlalchemy.orm import Session
from typing import Dict, List

from models import PolymarketProbability
from transformers.polymarket import PolymarketProbabilityRecord


def get_latest_timestamps_by_market(session: Session) -> Dict[str, object]:
    """
    Returns the latest persisted timestamp for each Polymarket market.
    """
    rows = (
        session.query(
            PolymarketProbability.market_id,
            func.max(PolymarketProbability.timestamp),
        )
        .group_by(PolymarketProbability.market_id)
        .all()
    )

    return dict(rows)


def save_probability_records(
    session: Session,
    records: List[PolymarketProbabilityRecord],
) -> int:
    """
    Persists new Polymarket probability records and skips records already stored.
    """
    if not records:
        return 0

    batch_keys = {(record.market_id, record.timestamp) for record in records}
    existing_keys = set(
        session.query(PolymarketProbability.market_id, PolymarketProbability.timestamp)
        .filter(
            tuple_(
                PolymarketProbability.market_id,
                PolymarketProbability.timestamp,
            ).in_(list(batch_keys))
        )
        .all()
    )

    saved_count = 0
    seen_keys = existing_keys.copy()

    for record in records:
        key = (record.market_id, record.timestamp)
        if key in seen_keys:
            continue

        session.add(
            PolymarketProbability(
                candidate_name=record.candidate_name,
                probability=record.probability,
                timestamp=record.timestamp,
                market_id=record.market_id,
            )
        )
        seen_keys.add(key)
        saved_count += 1

    return saved_count
