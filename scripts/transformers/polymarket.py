import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional


@dataclass(frozen=True)
class PolymarketMarket:
    market_id: str
    candidate_name: str
    yes_token_id: str


@dataclass(frozen=True)
class PolymarketProbabilityRecord:
    market_id: str
    candidate_catalog_id: int
    candidate_name: str
    probability: float
    timestamp: datetime


def parse_markets(markets: List[dict]) -> List[PolymarketMarket]:
    """
    Converts raw Polymarket market payloads into candidate market references.
    """
    parsed_markets = []

    for market in markets:
        market_ref = parse_market(market)
        if market_ref is not None:
            parsed_markets.append(market_ref)

    return parsed_markets


def parse_market(market: dict) -> Optional[PolymarketMarket]:
    """
    Parses a single Polymarket market and skips placeholder candidate markets.
    """
    raw_market_id = market.get("id")
    candidate_name = market.get("groupItemTitle")

    if not raw_market_id or not candidate_name:
        return None

    market_id = str(raw_market_id)
    candidate_lower = candidate_name.lower()
    if "person " in candidate_lower or "another person" in candidate_lower:
        return None

    clob_tokens = parse_clob_tokens(market.get("clobTokenIds"))
    if not clob_tokens:
        return None

    return PolymarketMarket(
        market_id=market_id,
        candidate_name=candidate_name,
        yes_token_id=str(clob_tokens[0]),
    )


def parse_clob_tokens(clob_tokens_raw) -> list:
    """
    Parses Polymarket CLOB token IDs, which may arrive as JSON text or a list.
    """
    if not clob_tokens_raw:
        return []

    if isinstance(clob_tokens_raw, str):
        try:
            return json.loads(clob_tokens_raw)
        except json.JSONDecodeError:
            return []

    return clob_tokens_raw


def parse_price_history(
    market: PolymarketMarket,
    candidate_catalog_id: int,
    history_points: List[dict],
) -> List[PolymarketProbabilityRecord]:
    """
    Converts raw price history points into probability records ready to persist.
    """
    records = []

    for point in history_points:
        timestamp_seconds = point.get("t")
        price = point.get("p")

        if timestamp_seconds is None or price is None:
            continue

        try:
            timestamp = datetime.fromtimestamp(timestamp_seconds, timezone.utc).replace(tzinfo=None)
            probability = float(price)
        except (TypeError, ValueError, OSError):
            continue

        records.append(
            PolymarketProbabilityRecord(
                market_id=market.market_id,
                candidate_catalog_id=candidate_catalog_id,
                candidate_name=market.candidate_name,
                probability=probability,
                timestamp=timestamp,
            )
        )

    return records
