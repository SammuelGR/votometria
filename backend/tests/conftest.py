import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import gold_sheets
from tests.helpers import empty_gold_dataframe


@pytest.fixture(autouse=True)
def _default_gold(monkeypatch):
    """
    By default every test sees an empty gold dataset, so no test ever hits the
    network. Tests that need data override it via the ``set_gold`` fixture.
    """
    monkeypatch.setattr(
        gold_sheets, "load_polymarket_gold", lambda **kwargs: empty_gold_dataframe()
    )


@pytest.fixture
def set_gold(monkeypatch):
    """
    Installs a fake gold DataFrame as the market-expectations data source.
    """

    def _set(df):
        monkeypatch.setattr(
            gold_sheets, "load_polymarket_gold", lambda **kwargs: df.copy()
        )

    return _set


@pytest.fixture
def client():
    return TestClient(app)
