from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_db
from app.main import app
from app.models import Base, CandidateCatalog, PolymarketProbability


@pytest.fixture
def create_test_session_factory():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def client(create_test_session_factory):
    def override_get_db():
        db = create_test_session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_health_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_market_expectations_returns_empty_series_when_no_data_exists(client):
    response = client.get("/api/current-election/market-expectations")

    assert response.status_code == 200
    assert response.json() == {
        "source": "polymarket",
        "series": [],
    }


def test_market_expectations_returns_grouped_candidate_series(client, create_test_session_factory):
    with create_test_session_factory() as session:
        session.add_all(
            [
                CandidateCatalog(
                    id=1,
                    source="polymarket",
                    source_key="market-1",
                    raw_name="Candidate A",
                    display_name="Candidate A",
                    normalized_name="candidate a",
                    full_name="Candidate A",
                ),
                CandidateCatalog(
                    id=2,
                    source="polymarket",
                    source_key="market-2",
                    raw_name="Candidate B",
                    display_name="Candidate B",
                    normalized_name="candidate b",
                    full_name="Candidate B",
                ),
                PolymarketProbability(
                    candidate_catalog_id=1,
                    candidate_name="Candidate A",
                    probability=0.42,
                    timestamp=datetime(2024, 1, 1, 10),
                    market_id="market-1",
                ),
                PolymarketProbability(
                    candidate_catalog_id=1,
                    candidate_name="Candidate A",
                    probability=0.43,
                    timestamp=datetime(2024, 1, 1, 11),
                    market_id="market-1",
                ),
                PolymarketProbability(
                    candidate_catalog_id=2,
                    candidate_name="Candidate B",
                    probability=0.20,
                    timestamp=datetime(2024, 1, 1, 10),
                    market_id="market-2",
                ),
            ]
        )
        session.commit()

    response = client.get("/api/current-election/market-expectations")

    assert response.status_code == 200
    assert response.json() == {
        "source": "polymarket",
        "series": [
            {
                "candidateCatalogId": 1,
                "candidateName": "Candidate A",
                "displayName": "Candidate A",
                "marketId": "market-1",
                "points": [
                    {
                        "timestamp": "2024-01-01T10:00:00",
                        "probability": 0.42,
                    },
                    {
                        "timestamp": "2024-01-01T11:00:00",
                        "probability": 0.43,
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
                        "probability": 0.2,
                    },
                ],
            },
        ],
    }
