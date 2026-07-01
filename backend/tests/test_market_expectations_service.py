from datetime import datetime

import pytest

from app.services.market_expectations import (
    build_market_expectation_series,
    build_market_expectations_metadata,
    build_market_expectations_summary,
    get_market_expectations,
)
from tests.helpers import (
    empty_gold_dataframe,
    gold_dataframe,
    gold_row,
    market_expectation_point,
    market_expectation_series,
)


def test_build_market_expectation_series_groups_records_by_candidate_and_market():
    df = gold_dataframe(
        [
            gold_row(1, "Candidate A", market_id="market-1", probability=0.25,
                     timestamp=datetime(2024, 1, 1, 10)),
            gold_row(1, "Candidate A", market_id="market-1", probability=0.50,
                     timestamp=datetime(2024, 1, 1, 11)),
            gold_row(2, "Candidate B", market_id="market-2", probability=0.125,
                     timestamp=datetime(2024, 1, 1, 10)),
        ]
    )

    series = build_market_expectation_series(df)

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


def test_build_market_expectations_metadata_returns_latest_timestamp():
    df = gold_dataframe(
        [
            gold_row(1, "Candidate A", probability=0.25, timestamp=datetime(2024, 1, 1, 10)),
            gold_row(1, "Candidate A", probability=0.50, timestamp=datetime(2024, 1, 1, 12)),
        ]
    )

    metadata = build_market_expectations_metadata(df)

    assert metadata.latest_timestamp == datetime(2024, 1, 1, 12)


def test_build_market_expectations_metadata_returns_none_without_records():
    metadata = build_market_expectations_metadata(empty_gold_dataframe())

    assert metadata.latest_timestamp is None


def test_get_market_expectations_rejects_unsupported_interval():
    with pytest.raises(ValueError, match="Unsupported market expectation interval"):
        get_market_expectations(interval="weekly")


def test_build_market_expectations_summary_returns_leader_margin_and_largest_change():
    series = [
        market_expectation_series(
            candidate_catalog_id=1,
            candidate_name="Candidate A",
            display_name="Candidate A",
            market_id="market-1",
            points=[
                market_expectation_point(probability=0.25, timestamp=datetime(2024, 1, 1, 10)),
                market_expectation_point(probability=0.50, timestamp=datetime(2024, 1, 1, 11)),
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
            "value": 0.25,
            "absoluteValue": 0.25,
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
    }


def test_build_market_expectations_summary_returns_null_metrics_without_data():
    summary = build_market_expectations_summary([])

    assert summary.model_dump(by_alias=True) == {
        "currentLeader": None,
        "leaderMargin": None,
        "largestChange": None,
    }
