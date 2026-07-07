from datetime import datetime

import pytest

from app.services.market_expectations import (
    build_market_expectation_series,
    build_market_expectations_metadata,
    build_market_expectations_summary,
    get_market_expectations,
)
from tests.helpers import (
    candidate_catalog,
    market_expectation_point,
    market_expectation_series,
    polymarket_probability,
)


def test_build_market_expectation_series_groups_records_by_candidate_and_market():
    candidate_a = candidate_catalog(candidate_id=1, display_name="Candidate A")
    candidate_b = candidate_catalog(
        candidate_id=2,
        display_name="Candidate B",
        source_key="market-2",
    )
    records = [
        polymarket_probability(
            candidate_catalog_id=1,
            candidate_name="Candidate A",
            probability=0.25,
            timestamp=datetime(2024, 1, 1, 10),
            market_id="market-1",
        ),
        polymarket_probability(
            candidate_catalog_id=1,
            candidate_name="Candidate A",
            probability=0.50,
            timestamp=datetime(2024, 1, 1, 11),
            market_id="market-1",
        ),
        polymarket_probability(
            candidate_catalog_id=2,
            candidate_name="Candidate B",
            probability=0.125,
            timestamp=datetime(2024, 1, 1, 10),
            market_id="market-2",
        ),
    ]
    records[0].candidate_catalog = candidate_a
    records[1].candidate_catalog = candidate_a
    records[2].candidate_catalog = candidate_b

    series = build_market_expectation_series(records)

    assert [candidate_series.model_dump(by_alias=True) for candidate_series in series] == [
        {
            "candidateCatalogId": 1,
            "candidateName": "Candidate A",
            "displayName": "Candidate A",
            "marketId": "market-1",
            "points": [
                {
                    "timestamp": datetime(2024, 1, 1, 10),
                    "probability": 0.25,
                },
                {
                    "timestamp": datetime(2024, 1, 1, 11),
                    "probability": 0.50,
                },
            ],
        },
        {
            "candidateCatalogId": 2,
            "candidateName": "Candidate B",
            "displayName": "Candidate B",
            "marketId": "market-2",
            "points": [
                {
                    "timestamp": datetime(2024, 1, 1, 10),
                    "probability": 0.125,
                },
            ],
        },
    ]


def test_build_market_expectations_metadata_returns_latest_database_timestamp(
    db_session_factory,
):
    with db_session_factory() as session:
        session.add_all(
            [
                candidate_catalog(candidate_id=1, display_name="Candidate A"),
                polymarket_probability(
                    candidate_catalog_id=1,
                    candidate_name="Candidate A",
                    probability=0.25,
                    timestamp=datetime(2024, 1, 1, 10),
                ),
                polymarket_probability(
                    candidate_catalog_id=1,
                    candidate_name="Candidate A",
                    probability=0.50,
                    timestamp=datetime(2024, 1, 1, 12),
                ),
            ]
        )
        session.commit()

        metadata = build_market_expectations_metadata(session)

        assert metadata.latest_timestamp == datetime(2024, 1, 1, 12)


def test_build_market_expectations_metadata_returns_none_without_database_records(
    db_session_factory,
):
    with db_session_factory() as session:
        metadata = build_market_expectations_metadata(session)

        assert metadata.latest_timestamp is None


def test_get_market_expectations_rejects_unsupported_interval(db_session_factory):
    with db_session_factory() as session:
        with pytest.raises(ValueError, match="Unsupported market expectation interval"):
            get_market_expectations(session, interval="weekly")


def test_build_market_expectations_summary_returns_leader_margin_and_largest_change():
    series = [
        market_expectation_series(
            candidate_catalog_id=1,
            candidate_name="Candidate A",
            display_name="Candidate A",
            market_id="market-1",
            points=[
                market_expectation_point(probability=0.25, timestamp=datetime(2024, 1, 1, 10)),
                market_expectation_point(probability=0.75, timestamp=datetime(2024, 1, 1, 11)),
                market_expectation_point(probability=0.50, timestamp=datetime(2024, 1, 1, 12)),
            ],
        ),
        market_expectation_series(
            candidate_catalog_id=2,
            candidate_name="Candidate B",
            display_name="Candidate B",
            market_id="market-2",
            points=[
                market_expectation_point(probability=0.125, timestamp=datetime(2024, 1, 1, 10)),
            ],
        ),
    ]

    summary = build_market_expectations_summary(series)

    assert summary.model_dump(by_alias=True) == {
        "currentLeader": {
            "candidateCatalogId": 1,
            "displayName": "Candidate A",
            "probability": 0.50,
        },
        "leaderMargin": {
            "value": 0.375,
            "leaderCandidateCatalogId": 1,
            "runnerUpCandidateCatalogId": 2,
        },
        "largestChange": {
            "candidateCatalogId": 1,
            "displayName": "Candidate A",
            "value": 0.50,
            "absoluteValue": 0.50,
            "fromTimestamp": datetime(2024, 1, 1, 10),
            "toTimestamp": datetime(2024, 1, 1, 11),
        },
    }


def test_build_market_expectations_summary_preserves_negative_largest_change():
    series = [
        market_expectation_series(
            candidate_catalog_id=1,
            candidate_name="Candidate A",
            display_name="Candidate A",
            market_id="market-1",
            points=[
                market_expectation_point(probability=0.80, timestamp=datetime(2024, 1, 1, 10)),
                market_expectation_point(probability=0.30, timestamp=datetime(2024, 1, 1, 11)),
            ],
        ),
        market_expectation_series(
            candidate_catalog_id=2,
            candidate_name="Candidate B",
            display_name="Candidate B",
            market_id="market-2",
            points=[
                market_expectation_point(probability=0.20, timestamp=datetime(2024, 1, 1, 10)),
                market_expectation_point(probability=0.35, timestamp=datetime(2024, 1, 1, 11)),
            ],
        ),
    ]

    summary = build_market_expectations_summary(series)

    assert summary.largest_change.model_dump(by_alias=True) == {
        "candidateCatalogId": 1,
        "displayName": "Candidate A",
        "value": -0.50,
        "absoluteValue": 0.50,
        "fromTimestamp": datetime(2024, 1, 1, 10),
        "toTimestamp": datetime(2024, 1, 1, 11),
    }


def test_build_market_expectations_summary_returns_null_metrics_without_data():
    summary = build_market_expectations_summary([])

    assert summary.model_dump(by_alias=True) == {
        "currentLeader": None,
        "leaderMargin": None,
        "largestChange": None,
    }
