from datetime import datetime, timezone

from tests.helpers import utc_timestamp
from transformers.polymarket import (
    PolymarketMarket,
    PolymarketProbabilityRecord,
    parse_market,
    parse_markets,
    parse_price_history,
)


def test_parse_market_returns_candidate_market_from_expected_payload(market_payload):
    market = parse_market(market_payload)

    assert market == PolymarketMarket(
        market_id=market_payload["id"],
        candidate_name=market_payload["groupItemTitle"],
        yes_token_id="yes-token",
    )


def test_parse_market_accepts_clob_tokens_as_list(market_payload):
    market_payload["clobTokenIds"] = ["yes-token", "no-token"]

    market = parse_market(market_payload)

    assert market.yes_token_id == "yes-token"


def test_parse_markets_filters_non_candidate_markets(market_payload):
    placeholder_market = {
        "id": "placeholder-market",
        "groupItemTitle": "Another person",
        "clobTokenIds": ["placeholder-yes-token", "placeholder-no-token"],
    }
    market_without_tokens = {
        "id": "market-without-tokens",
        "groupItemTitle": "Candidate B",
    }

    markets = parse_markets([market_payload, placeholder_market, market_without_tokens])

    assert markets == [
        PolymarketMarket(
            market_id="market-1",
            candidate_name="Candidate A",
            yes_token_id="yes-token",
        )
    ]


def test_parse_price_history_returns_probability_records(candidate_market):
    history_point = {
        "t": utc_timestamp(2024, 1, 1, 12),
        "p": 0.42,
    }

    records = parse_price_history(candidate_market, 1, [history_point])

    assert records == [
        PolymarketProbabilityRecord(
            market_id=candidate_market.market_id,
            candidate_catalog_id=1,
            candidate_name=candidate_market.candidate_name,
            probability=history_point["p"],
            timestamp=datetime.fromtimestamp(history_point["t"], timezone.utc).replace(tzinfo=None),
        )
    ]


def test_parse_price_history_ignores_incomplete_points(candidate_market):
    valid_point = {
        "t": utc_timestamp(2024, 1, 1),
        "p": 0.42,
    }
    incomplete_points = [
        {"t": utc_timestamp(2024, 1, 1, 1)},
        {"p": 0.43},
    ]

    records = parse_price_history(candidate_market, 1, [valid_point, *incomplete_points])

    assert records == [
        PolymarketProbabilityRecord(
            market_id=candidate_market.market_id,
            candidate_catalog_id=1,
            candidate_name=candidate_market.candidate_name,
            probability=valid_point["p"],
            timestamp=datetime.fromtimestamp(valid_point["t"], timezone.utc).replace(tzinfo=None),
        )
    ]
