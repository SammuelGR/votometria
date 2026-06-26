from datetime import datetime, timezone

from transformers.polymarket import PolymarketProbabilityRecord


def utc_timestamp(year, month, day, hour=0):
    return int(datetime(year, month, day, hour, tzinfo=timezone.utc).timestamp())


def naive_utc_datetime(year, month, day, hour=0):
    return datetime(year, month, day, hour)


def probability_record(
    market_id="market-1",
    candidate_catalog_id=1,
    candidate_name="Candidate A",
    hour=0,
):
    return PolymarketProbabilityRecord(
        market_id=market_id,
        candidate_catalog_id=candidate_catalog_id,
        candidate_name=candidate_name,
        probability=0.42,
        timestamp=naive_utc_datetime(2024, 1, 1, hour),
    )
