import pandas as pd
import pytest

from extractors import google_trends


class FakeTrendReq:
    """Records constructor and call arguments and returns a canned DataFrame."""

    instances = []

    def __init__(self, hl=None, tz=None):
        self.hl = hl
        self.tz = tz
        self.payload = None
        FakeTrendReq.instances.append(self)

    def build_payload(self, kw_list=None, timeframe=None, geo=None):
        self.payload = {"kw_list": kw_list, "timeframe": timeframe, "geo": geo}

    def interest_over_time(self):
        return pd.DataFrame({"Lula": [10]})


def test_fetch_batch_builds_payload_with_arguments(monkeypatch):
    FakeTrendReq.instances = []
    monkeypatch.setattr(google_trends, "TrendReq", FakeTrendReq)

    result = google_trends.fetch_interest_over_time_batch(
        terms=["Lula", "Jair Bolsonaro"],
        timeframe="2022-01-01 2022-12-31",
        geo="BR",
        hl="pt-BR",
        tz=180,
    )

    assert list(result.columns) == ["Lula"]
    assert len(FakeTrendReq.instances) == 1
    instance = FakeTrendReq.instances[0]
    assert instance.hl == "pt-BR"
    assert instance.tz == 180
    assert instance.payload == {
        "kw_list": ["Lula", "Jair Bolsonaro"],
        "timeframe": "2022-01-01 2022-12-31",
        "geo": "BR",
    }


def test_fetch_batch_rejects_empty_terms(monkeypatch):
    monkeypatch.setattr(google_trends, "TrendReq", FakeTrendReq)

    with pytest.raises(ValueError):
        google_trends.fetch_interest_over_time_batch(
            terms=[],
            timeframe="today 12-m",
            geo="BR",
            hl="pt-BR",
            tz=180,
        )


def test_fetch_batch_rejects_more_than_five_terms(monkeypatch):
    monkeypatch.setattr(google_trends, "TrendReq", FakeTrendReq)

    with pytest.raises(ValueError):
        google_trends.fetch_interest_over_time_batch(
            terms=["a", "b", "c", "d", "e", "f"],
            timeframe="today 12-m",
            geo="BR",
            hl="pt-BR",
            tz=180,
        )


def test_fetch_batch_retries_on_transient_error(monkeypatch):
    sleep_calls = []
    monkeypatch.setattr(
        google_trends.time, "sleep", lambda seconds: sleep_calls.append(seconds)
    )

    attempts = {"count": 0}

    class FlakyTrendReq(FakeTrendReq):
        def interest_over_time(self):
            attempts["count"] += 1
            if attempts["count"] == 1:
                raise RuntimeError("rate limited")
            return pd.DataFrame({"Lula": [42]})

    monkeypatch.setattr(google_trends, "TrendReq", FlakyTrendReq)

    result = google_trends.fetch_interest_over_time_batch(
        terms=["Lula"],
        timeframe="today 12-m",
        geo="BR",
        hl="pt-BR",
        tz=180,
    )

    assert attempts["count"] == 2
    assert len(sleep_calls) == 1
    assert list(result["Lula"]) == [42]
