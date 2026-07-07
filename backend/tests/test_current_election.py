from datetime import datetime

from tests.helpers import candidate_catalog, polymarket_probability


def test_health_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_cors_allows_local_frontend_origin(client):
    response = client.options(
        "/api/current-election/market-expectations",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_market_expectations_returns_empty_series_when_no_data_exists(client):
    response = client.get("/api/current-election/market-expectations")

    assert response.status_code == 200
    assert response.json() == {
        "sources": ["polymarket"],
        "metadata": {
            "latestTimestamp": None,
        },
        "summary": {
            "currentLeader": None,
            "leaderMargin": None,
            "largestChange": None,
        },
        "series": [],
    }


def test_monthly_market_expectations_returns_empty_points_for_unknown_candidate(client):
    response = client.get(
        "/api/current-election/monthly-market-expectations",
        params={"candidate": "Unknown"},
    )

    assert response.status_code == 200
    assert response.json() == {"points": []}


def test_monthly_market_expectations_returns_monthly_closing_points(
    client,
    db_session_factory,
):
    with db_session_factory() as session:
        session.add(
            candidate_catalog(
                candidate_id=1,
                display_name="Luiz Inácio Lula da Silva",
                source_key="market-1",
            )
        )
        session.add_all(
            [
                polymarket_probability(
                    candidate_catalog_id=1,
                    candidate_name="Luiz Inácio Lula da Silva",
                    probability=0.21,
                    timestamp=datetime(2026, 1, 2, 10),
                ),
                polymarket_probability(
                    candidate_catalog_id=1,
                    candidate_name="Luiz Inácio Lula da Silva",
                    probability=0.31,
                    timestamp=datetime(2026, 1, 30, 18),
                ),
                polymarket_probability(
                    candidate_catalog_id=1,
                    candidate_name="Luiz Inácio Lula da Silva",
                    probability=0.37,
                    timestamp=datetime(2026, 2, 3, 9),
                ),
                polymarket_probability(
                    candidate_catalog_id=1,
                    candidate_name="Luiz Inácio Lula da Silva",
                    probability=0.99,
                    timestamp=datetime(2025, 12, 31, 23),
                ),
            ]
        )
        session.commit()

    response = client.get(
        "/api/current-election/monthly-market-expectations",
        params={"candidate": "Lula"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "points": [
            {"date": "2026-01-01", "probability": 31.0},
            {"date": "2026-02-01", "probability": 37.0},
        ]
    }


def test_monthly_market_expectations_picks_highest_latest_probability_match(
    client,
    db_session_factory,
):
    with db_session_factory() as session:
        session.add_all(
            [
                candidate_catalog(
                    candidate_id=1,
                    display_name="Flávio Bolsonaro",
                    source_key="market-1",
                ),
                candidate_catalog(
                    candidate_id=2,
                    display_name="Michelle Bolsonaro",
                    source_key="market-2",
                ),
            ]
        )
        session.add_all(
            [
                polymarket_probability(
                    candidate_catalog_id=1,
                    candidate_name="Flávio Bolsonaro",
                    probability=0.41,
                    timestamp=datetime(2026, 3, 15, 10),
                ),
                polymarket_probability(
                    candidate_catalog_id=2,
                    candidate_name="Michelle Bolsonaro",
                    market_id="market-2",
                    probability=0.22,
                    timestamp=datetime(2026, 3, 15, 10),
                ),
            ]
        )
        session.commit()

    response = client.get(
        "/api/current-election/monthly-market-expectations",
        params={"candidate": "Bolsonaro"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "points": [
            {"date": "2026-03-01", "probability": 41.0},
        ]
    }


def test_market_expectations_returns_grouped_candidate_series(client, db_session_factory):
    with db_session_factory() as session:
        session.add_all(
            [
                candidate_catalog(
                    candidate_id=1,
                    display_name="Candidate A",
                    source_key="market-1",
                ),
                candidate_catalog(
                    candidate_id=2,
                    display_name="Candidate B",
                    source_key="market-2",
                ),
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
                    timestamp=datetime(2024, 1, 1, 11),
                ),
                polymarket_probability(
                    candidate_catalog_id=2,
                    candidate_name="Candidate B",
                    probability=0.125,
                    timestamp=datetime(2024, 1, 1, 10),
                    market_id="market-2",
                ),
            ]
        )
        session.commit()

    response = client.get("/api/current-election/market-expectations")

    assert response.status_code == 200
    assert response.json() == {
        "sources": ["polymarket"],
        "metadata": {
            "latestTimestamp": "2024-01-01T11:00:00",
        },
        "summary": {
            "currentLeader": {
                "candidateCatalogId": 1,
                "displayName": "Candidate A",
                "probability": 0.5,
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
                "fromTimestamp": "2024-01-01T10:00:00",
                "toTimestamp": "2024-01-01T11:00:00",
            },
        },
        "series": [
            {
                "candidateCatalogId": 1,
                "candidateName": "Candidate A",
                "displayName": "Candidate A",
                "marketId": "market-1",
                "points": [
                    {
                        "timestamp": "2024-01-01T10:00:00",
                        "probability": 0.25,
                    },
                    {
                        "timestamp": "2024-01-01T11:00:00",
                        "probability": 0.5,
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
                        "timestamp": "2024-01-01T10:00:00",
                        "probability": 0.125,
                    },
                ],
            },
        ],
    }


def test_market_expectations_filters_by_candidate_catalog_ids(client, db_session_factory):
    with db_session_factory() as session:
        session.add_all(
            [
                candidate_catalog(
                    candidate_id=1,
                    display_name="Candidate A",
                    source_key="market-1",
                ),
                candidate_catalog(
                    candidate_id=2,
                    display_name="Candidate B",
                    source_key="market-2",
                ),
                polymarket_probability(
                    candidate_catalog_id=1,
                    candidate_name="Candidate A",
                    probability=0.25,
                    timestamp=datetime(2024, 1, 1, 10),
                ),
                polymarket_probability(
                    candidate_catalog_id=2,
                    candidate_name="Candidate B",
                    probability=0.50,
                    timestamp=datetime(2024, 1, 1, 10),
                    market_id="market-2",
                ),
            ]
        )
        session.commit()

    response = client.get(
        "/api/current-election/market-expectations",
        params={"candidateCatalogIds": 2},
    )

    assert response.status_code == 200
    response_body = response.json()
    assert [series["candidateCatalogId"] for series in response_body["series"]] == [2]
    assert response_body["summary"]["currentLeader"] == {
        "candidateCatalogId": 2,
        "displayName": "Candidate B",
        "probability": 0.5,
    }


def test_market_expectations_returns_empty_series_for_unknown_candidate_catalog_id(
    client,
    db_session_factory,
):
    with db_session_factory() as session:
        session.add_all(
            [
                candidate_catalog(
                    candidate_id=1,
                    display_name="Candidate A",
                    source_key="market-1",
                ),
                polymarket_probability(
                    candidate_catalog_id=1,
                    candidate_name="Candidate A",
                    probability=0.25,
                    timestamp=datetime(2024, 1, 1, 10),
                ),
            ]
        )
        session.commit()

    response = client.get(
        "/api/current-election/market-expectations",
        params={"candidateCatalogIds": 999},
    )

    assert response.status_code == 200
    response_body = response.json()
    assert response_body["metadata"]["latestTimestamp"] == "2024-01-01T10:00:00"
    assert response_body["summary"] == {
        "currentLeader": None,
        "leaderMargin": None,
        "largestChange": None,
    }
    assert response_body["series"] == []


def test_market_expectations_filters_by_date_range(client, db_session_factory):
    with db_session_factory() as session:
        session.add_all(
            [
                candidate_catalog(
                    candidate_id=1,
                    display_name="Candidate A",
                    source_key="market-1",
                ),
                polymarket_probability(
                    candidate_catalog_id=1,
                    candidate_name="Candidate A",
                    probability=0.20,
                    timestamp=datetime(2024, 1, 1, 9),
                ),
                polymarket_probability(
                    candidate_catalog_id=1,
                    candidate_name="Candidate A",
                    probability=0.30,
                    timestamp=datetime(2024, 1, 1, 10),
                ),
                polymarket_probability(
                    candidate_catalog_id=1,
                    candidate_name="Candidate A",
                    probability=0.40,
                    timestamp=datetime(2024, 1, 1, 11),
                ),
            ]
        )
        session.commit()

    response = client.get(
        "/api/current-election/market-expectations",
        params={
            "fromDate": "2024-01-01T10:00:00",
            "toDate": "2024-01-01T10:00:00",
        },
    )

    assert response.status_code == 200
    response_body = response.json()
    assert response_body["metadata"]["latestTimestamp"] == "2024-01-01T11:00:00"
    assert response_body["series"][0]["points"] == [
        {
            "timestamp": "2024-01-01T10:00:00",
            "probability": 0.3,
        }
    ]


def test_market_expectations_returns_empty_series_for_out_of_range_dates(
    client,
    db_session_factory,
):
    with db_session_factory() as session:
        session.add_all(
            [
                candidate_catalog(
                    candidate_id=1,
                    display_name="Candidate A",
                    source_key="market-1",
                ),
                polymarket_probability(
                    candidate_catalog_id=1,
                    candidate_name="Candidate A",
                    probability=0.20,
                    timestamp=datetime(2024, 1, 1, 9),
                ),
            ]
        )
        session.commit()

    response = client.get(
        "/api/current-election/market-expectations",
        params={
            "fromDate": "2024-01-02T00:00:00",
            "toDate": "2024-01-02T23:59:59",
        },
    )

    assert response.status_code == 200
    response_body = response.json()
    assert response_body["metadata"]["latestTimestamp"] == "2024-01-01T09:00:00"
    assert response_body["summary"] == {
        "currentLeader": None,
        "leaderMargin": None,
        "largestChange": None,
    }
    assert response_body["series"] == []


def test_market_expectations_rejects_inverted_date_range(client):
    response = client.get(
        "/api/current-election/market-expectations",
        params={
            "fromDate": "2024-01-02T00:00:00",
            "toDate": "2024-01-01T00:00:00",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "message": "fromDate must be earlier than or equal to toDate.",
    }


def test_market_expectations_rejects_unsupported_interval(client):
    response = client.get(
        "/api/current-election/market-expectations",
        params={"interval": "2h"},
    )

    assert response.status_code == 422
    response_body = response.json()
    assert response_body == {
        "message": "Invalid request.",
        "errors": [
            {
                "field": "interval",
                "message": "Input should be '1h', '4h', '1d' or '1w'",
            }
        ],
    }


def test_market_expectation_options_returns_empty_values_when_no_data_exists(client):
    response = client.get("/api/current-election/market-expectations/options")

    assert response.status_code == 200
    assert response.json() == {
        "dateRange": {
            "min": None,
            "max": None,
        },
        "intervals": ["1h", "4h", "1d", "1w"],
        "candidates": [],
        "defaultCandidateCatalogIds": [],
    }


def test_market_expectation_options_returns_available_values(
    client,
    db_session_factory,
):
    with db_session_factory() as session:
        session.add_all(
            [
                candidate_catalog(
                    candidate_id=1,
                    display_name="Candidate A",
                    source_key="market-1",
                ),
                candidate_catalog(
                    candidate_id=2,
                    display_name="Candidate B",
                    source_key="market-2",
                ),
                polymarket_probability(
                    candidate_catalog_id=1,
                    candidate_name="Candidate A",
                    probability=0.25,
                    timestamp=datetime(2024, 1, 1, 10),
                ),
                polymarket_probability(
                    candidate_catalog_id=2,
                    candidate_name="Candidate B",
                    probability=0.50,
                    timestamp=datetime(2024, 1, 3, 12),
                    market_id="market-2",
                ),
            ]
        )
        session.commit()

    response = client.get("/api/current-election/market-expectations/options")

    assert response.status_code == 200
    response_body = response.json()
    assert response_body["dateRange"] == {
        "min": "2024-01-01T10:00:00",
        "max": "2024-01-03T12:00:00",
    }
    assert response_body["intervals"] == ["1h", "4h", "1d", "1w"]
    assert response_body["candidates"] == [
        {
            "candidateCatalogId": 2,
            "displayName": "Candidate B",
            "latestProbability": 0.5,
        },
        {
            "candidateCatalogId": 1,
            "displayName": "Candidate A",
            "latestProbability": 0.25,
        },
    ]
    assert response_body["defaultCandidateCatalogIds"] == [2, 1]


def test_market_expectation_options_ignores_candidates_without_probabilities(
    client,
    db_session_factory,
):
    with db_session_factory() as session:
        session.add_all(
            [
                candidate_catalog(
                    candidate_id=1,
                    display_name="Candidate A",
                    source_key="market-1",
                ),
                candidate_catalog(
                    candidate_id=2,
                    display_name="Candidate B",
                    source_key="market-2",
                ),
                polymarket_probability(
                    candidate_catalog_id=1,
                    candidate_name="Candidate A",
                    probability=0.25,
                    timestamp=datetime(2024, 1, 1, 10),
                ),
            ]
        )
        session.commit()

    response = client.get("/api/current-election/market-expectations/options")

    assert response.status_code == 200
    assert response.json()["candidates"] == [
        {
            "candidateCatalogId": 1,
            "displayName": "Candidate A",
            "latestProbability": 0.25,
        }
    ]


def test_market_expectation_options_does_not_duplicate_candidates(
    client,
    db_session_factory,
):
    with db_session_factory() as session:
        session.add_all(
            [
                candidate_catalog(
                    candidate_id=1,
                    display_name="Candidate A",
                    source_key="market-1",
                ),
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
                    timestamp=datetime(2024, 1, 1, 11),
                ),
            ]
        )
        session.commit()

    response = client.get("/api/current-election/market-expectations/options")

    assert response.status_code == 200
    assert response.json()["candidates"] == [
        {
            "candidateCatalogId": 1,
            "displayName": "Candidate A",
            "latestProbability": 0.5,
        }
    ]


def test_market_expectation_options_orders_candidates_by_latest_probability(
    client,
    db_session_factory,
):
    with db_session_factory() as session:
        session.add_all(
            [
                candidate_catalog(
                    candidate_id=1,
                    display_name="Candidate A",
                    source_key="market-1",
                ),
                candidate_catalog(
                    candidate_id=2,
                    display_name="Candidate B",
                    source_key="market-2",
                ),
                polymarket_probability(
                    candidate_catalog_id=1,
                    candidate_name="Candidate A",
                    probability=0.90,
                    timestamp=datetime(2024, 1, 1, 10),
                ),
                polymarket_probability(
                    candidate_catalog_id=1,
                    candidate_name="Candidate A",
                    probability=0.20,
                    timestamp=datetime(2024, 1, 1, 11),
                ),
                polymarket_probability(
                    candidate_catalog_id=2,
                    candidate_name="Candidate B",
                    probability=0.50,
                    timestamp=datetime(2024, 1, 1, 10),
                    market_id="market-2",
                ),
            ]
        )
        session.commit()

    response = client.get("/api/current-election/market-expectations/options")

    assert response.status_code == 200
    response_body = response.json()
    assert response_body["candidates"] == [
        {
            "candidateCatalogId": 2,
            "displayName": "Candidate B",
            "latestProbability": 0.5,
        },
        {
            "candidateCatalogId": 1,
            "displayName": "Candidate A",
            "latestProbability": 0.2,
        },
    ]
    assert response_body["defaultCandidateCatalogIds"] == [2, 1]


def test_market_expectation_options_returns_top_five_default_candidates(
    client,
    db_session_factory,
):
    with db_session_factory() as session:
        records = []

        for candidate_id in range(1, 7):
            records.extend(
                [
                    candidate_catalog(
                        candidate_id=candidate_id,
                        display_name=f"Candidate {candidate_id}",
                        source_key=f"market-{candidate_id}",
                    ),
                    polymarket_probability(
                        candidate_catalog_id=candidate_id,
                        candidate_name=f"Candidate {candidate_id}",
                        probability=candidate_id * 0.1,
                        timestamp=datetime(2024, 1, 1, 10),
                        market_id=f"market-{candidate_id}",
                    ),
                ]
            )

        session.add_all(records)
        session.commit()

    response = client.get("/api/current-election/market-expectations/options")

    assert response.status_code == 200
    assert response.json()["defaultCandidateCatalogIds"] == [6, 5, 4, 3, 2]
