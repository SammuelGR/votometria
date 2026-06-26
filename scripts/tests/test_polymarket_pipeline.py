from core.time_windows import calculate_incremental_start_timestamp
from pipelines import polymarket
from tests.helpers import naive_utc_datetime, probability_record, utc_timestamp
from transformers.polymarket import PolymarketMarket


class PipelineTestSession:
    def __init__(self):
        self.commit_count = 0

    def commit(self):
        self.commit_count += 1


class PipelineTestCandidate:
    def __init__(self, candidate_id):
        self.id = candidate_id


class PipelineTestHarness:
    def __init__(self, monkeypatch):
        self.session = PipelineTestSession()
        self.candidate = PipelineTestCandidate(candidate_id=1)
        self.market = PolymarketMarket(
            market_id="market-1",
            candidate_name="Candidate A",
            yes_token_id="yes-token",
        )
        self.markets_payload = [{"id": self.market.market_id}]
        self.parsed_markets = [self.market]
        self.latest_timestamps_by_market = {}
        self.history_points_by_token = {
            self.market.yes_token_id: [{"t": utc_timestamp(2024, 1, 1), "p": 0.42}]
        }
        self.records_by_market = {
            self.market.market_id: [probability_record(market_id=self.market.market_id)]
        }
        self.failing_tokens = set()

        self.parse_markets_calls = []
        self.latest_timestamps_calls = []
        self.fetch_history_calls = []
        self.parse_history_calls = []
        self.save_records_calls = []
        self.catalog_calls = []

        monkeypatch.setattr(polymarket, "fetch_event_markets", self.fetch_event_markets)
        monkeypatch.setattr(polymarket, "parse_markets", self.parse_markets)
        monkeypatch.setattr(
            polymarket,
            "get_latest_timestamps_by_market",
            self.get_latest_timestamps_by_market,
        )
        monkeypatch.setattr(polymarket, "fetch_price_history", self.fetch_price_history)
        monkeypatch.setattr(polymarket, "parse_price_history", self.parse_price_history)
        monkeypatch.setattr(polymarket, "save_probability_records", self.save_probability_records)
        monkeypatch.setattr(
            polymarket,
            "get_or_create_candidate_catalog_entry",
            self.get_or_create_candidate_catalog_entry,
        )

    def fetch_event_markets(self):
        return self.markets_payload

    def parse_markets(self, markets_payload):
        self.parse_markets_calls.append(markets_payload)
        return self.parsed_markets

    def get_latest_timestamps_by_market(self, session):
        self.latest_timestamps_calls.append(session)
        return self.latest_timestamps_by_market

    def fetch_price_history(self, token_id, start_ts, end_ts):
        self.fetch_history_calls.append(
            {
                "token_id": token_id,
                "start_ts": start_ts,
                "end_ts": end_ts,
            }
        )

        if token_id in self.failing_tokens:
            raise RuntimeError("price history fetch failed")

        return self.history_points_by_token.get(token_id, [])

    def parse_price_history(self, market, candidate_catalog_id, history_points):
        self.parse_history_calls.append(
            {
                "market": market,
                "candidate_catalog_id": candidate_catalog_id,
                "history_points": history_points,
            }
        )
        return self.records_by_market.get(market.market_id, [])

    def save_probability_records(self, session, records):
        self.save_records_calls.append(
            {
                "session": session,
                "records": records,
            }
        )
        return len(records)

    def get_or_create_candidate_catalog_entry(self, session, source, source_key, raw_name, full_name=None):
        self.catalog_calls.append(
            {
                "session": session,
                "source": source,
                "source_key": source_key,
                "raw_name": raw_name,
                "full_name": full_name,
            }
        )
        return self.candidate

    def run(self):
        return polymarket.run_polymarket_pipeline(self.session)


def test_pipeline_stops_when_event_has_no_markets(monkeypatch):
    pipeline = PipelineTestHarness(monkeypatch)
    pipeline.markets_payload = []

    saved_count = pipeline.run()

    assert saved_count == 0
    assert pipeline.session.commit_count == 0
    assert pipeline.parse_markets_calls == []
    assert pipeline.catalog_calls == []
    assert pipeline.fetch_history_calls == []
    assert pipeline.save_records_calls == []


def test_pipeline_stops_when_no_candidate_markets_are_found(monkeypatch):
    pipeline = PipelineTestHarness(monkeypatch)
    pipeline.parsed_markets = []

    saved_count = pipeline.run()

    assert saved_count == 0
    assert pipeline.session.commit_count == 0
    assert pipeline.parse_markets_calls == [pipeline.markets_payload]
    assert pipeline.latest_timestamps_calls == []
    assert pipeline.catalog_calls == []
    assert pipeline.fetch_history_calls == []
    assert pipeline.save_records_calls == []


def test_pipeline_fetches_incremental_history_for_existing_markets(monkeypatch):
    pipeline = PipelineTestHarness(monkeypatch)
    last_timestamp = naive_utc_datetime(2024, 1, 2)
    expected_start_ts = calculate_incremental_start_timestamp(last_timestamp)
    pipeline.latest_timestamps_by_market = {pipeline.market.market_id: last_timestamp}

    saved_count = pipeline.run()

    fetch_history_call = pipeline.fetch_history_calls[0]
    assert saved_count == 1
    assert pipeline.session.commit_count == 1
    assert len(pipeline.fetch_history_calls) == 1
    assert fetch_history_call["token_id"] == pipeline.market.yes_token_id
    assert fetch_history_call["start_ts"] == expected_start_ts
    assert isinstance(fetch_history_call["end_ts"], int)
    assert pipeline.catalog_calls == [
        {
            "session": pipeline.session,
            "source": "polymarket",
            "source_key": pipeline.market.market_id,
            "raw_name": pipeline.market.candidate_name,
            "full_name": pipeline.market.candidate_name,
        }
    ]
    assert pipeline.parse_history_calls[0]["candidate_catalog_id"] == pipeline.candidate.id


def test_pipeline_fetches_full_history_for_new_markets(monkeypatch):
    pipeline = PipelineTestHarness(monkeypatch)

    saved_count = pipeline.run()

    assert saved_count == 1
    assert pipeline.fetch_history_calls == [
        {
            "token_id": pipeline.market.yes_token_id,
            "start_ts": None,
            "end_ts": None,
        }
    ]


def test_pipeline_continues_after_candidate_processing_error(monkeypatch):
    pipeline = PipelineTestHarness(monkeypatch)
    failing_market = pipeline.market
    successful_market = PolymarketMarket(
        market_id="market-2",
        candidate_name="Candidate B",
        yes_token_id="yes-token-2",
    )
    pipeline.parsed_markets = [failing_market, successful_market]
    pipeline.failing_tokens = {failing_market.yes_token_id}
    pipeline.history_points_by_token = {
        successful_market.yes_token_id: [{"t": utc_timestamp(2024, 1, 1), "p": 0.24}]
    }
    pipeline.records_by_market = {
        successful_market.market_id: [
            probability_record(
                market_id=successful_market.market_id,
                candidate_name=successful_market.candidate_name,
            )
        ]
    }

    saved_count = pipeline.run()

    assert saved_count == 1
    assert pipeline.session.commit_count == 1
    assert len(pipeline.fetch_history_calls) == 2
    assert pipeline.save_records_calls == [
        {
            "session": pipeline.session,
            "records": pipeline.records_by_market[successful_market.market_id],
        }
    ]


def test_pipeline_does_not_commit_when_no_new_records_are_saved(monkeypatch):
    pipeline = PipelineTestHarness(monkeypatch)
    pipeline.records_by_market = {pipeline.market.market_id: []}

    saved_count = pipeline.run()

    assert saved_count == 0
    assert pipeline.session.commit_count == 0
    assert len(pipeline.save_records_calls) == 1
