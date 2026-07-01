"""
Tests for the stateless, sheets-based Polymarket pipeline (no PostgreSQL).

The pipeline fetches the full price history on every run and publishes to the
medallion layers: raw markets + price history -> bronze, parsed probability
records -> prata, consolidated series -> ouro.
"""

from pipelines import polymarket
from transformers.polymarket import PolymarketMarket


class PipelineTestHarness:
    def __init__(self, monkeypatch):
        self.market = PolymarketMarket(
            market_id="market-1",
            candidate_name="Candidate A",
            yes_token_id="yes-token",
        )
        self.markets_payload = [{"id": self.market.market_id}]
        self.parsed_markets = [self.market]
        self.history_points_by_token = {
            self.market.yes_token_id: [{"t": 1_704_067_200, "p": 0.42}]
        }
        self.failing_tokens = set()

        self.fetch_history_calls = []
        self.saved = {"bronze_markets": None, "bronze_history": None, "prata": None, "ouro": None}

        monkeypatch.setattr(polymarket, "fetch_event_markets", self.fetch_event_markets)
        monkeypatch.setattr(polymarket, "parse_markets", self.parse_markets)
        monkeypatch.setattr(polymarket, "fetch_price_history", self.fetch_price_history)
        monkeypatch.setattr(
            polymarket,
            "get_layer_spreadsheets",
            lambda *layers: {"bronze": object(), "prata": object(), "ouro": object()},
        )
        monkeypatch.setattr(polymarket, "save_raw_markets_to_bronze", self.save_raw_markets)
        monkeypatch.setattr(polymarket, "save_raw_history_to_bronze", self.save_raw_history)
        monkeypatch.setattr(polymarket, "save_records_to_prata", self.save_prata)
        monkeypatch.setattr(polymarket, "save_records_to_ouro", self.save_ouro)

    def fetch_event_markets(self):
        return self.markets_payload

    def parse_markets(self, markets_payload):
        return self.parsed_markets

    def fetch_price_history(self, token_id):
        self.fetch_history_calls.append(token_id)
        if token_id in self.failing_tokens:
            raise RuntimeError("price history fetch failed")
        return self.history_points_by_token.get(token_id, [])

    def save_raw_markets(self, spreadsheet, markets):
        self.saved["bronze_markets"] = list(markets)
        return "raw_polymarket_markets"

    def save_raw_history(self, spreadsheet, rows):
        self.saved["bronze_history"] = list(rows)
        return "raw_polymarket_price_history"

    def save_prata(self, spreadsheet, records):
        self.saved["prata"] = list(records)
        return "proc_polymarket_probabilities_long"

    def save_ouro(self, spreadsheet, records):
        self.saved["ouro"] = list(records)
        return "proc_polymarket_probabilities"

    def run(self):
        return polymarket.run_polymarket_pipeline()


def test_pipeline_stops_when_event_has_no_markets(monkeypatch):
    pipeline = PipelineTestHarness(monkeypatch)
    pipeline.markets_payload = []

    published = pipeline.run()

    assert published == 0
    assert pipeline.fetch_history_calls == []
    assert pipeline.saved["ouro"] is None


def test_pipeline_stops_when_no_candidate_markets_are_found(monkeypatch):
    pipeline = PipelineTestHarness(monkeypatch)
    pipeline.parsed_markets = []

    published = pipeline.run()

    assert published == 0
    assert pipeline.fetch_history_calls == []


def test_pipeline_fetches_full_history_and_publishes_to_all_layers(monkeypatch):
    pipeline = PipelineTestHarness(monkeypatch)

    published = pipeline.run()

    # Stateless: full history fetch (no start/end timestamps).
    assert pipeline.fetch_history_calls == [pipeline.market.yes_token_id]
    # One probability record published to prata and ouro.
    assert published == 1
    assert len(pipeline.saved["prata"]) == 1
    assert len(pipeline.saved["ouro"]) == 1
    # Raw markets + raw price-history points went to bronze.
    assert pipeline.saved["bronze_markets"] == [pipeline.market]
    assert pipeline.saved["bronze_history"][0]["market_id"] == pipeline.market.market_id
    # Stable catalog id assigned (1 for the single market).
    assert pipeline.saved["ouro"][0].candidate_catalog_id == 1


def test_pipeline_assigns_stable_catalog_ids_by_market(monkeypatch):
    pipeline = PipelineTestHarness(monkeypatch)
    market_b = PolymarketMarket(
        market_id="market-0",  # sorts before "market-1"
        candidate_name="Candidate B",
        yes_token_id="yes-token-b",
    )
    pipeline.parsed_markets = [pipeline.market, market_b]
    pipeline.history_points_by_token[market_b.yes_token_id] = [{"t": 1_704_067_200, "p": 0.30}]

    pipeline.run()

    ids = {record.market_id: record.candidate_catalog_id for record in pipeline.saved["ouro"]}
    # ids are assigned by sorted market_id -> "market-0"=1, "market-1"=2
    assert ids == {"market-0": 1, "market-1": 2}


def test_pipeline_continues_after_candidate_processing_error(monkeypatch):
    pipeline = PipelineTestHarness(monkeypatch)
    successful_market = PolymarketMarket(
        market_id="market-2",
        candidate_name="Candidate B",
        yes_token_id="yes-token-2",
    )
    pipeline.parsed_markets = [pipeline.market, successful_market]
    pipeline.failing_tokens = {pipeline.market.yes_token_id}
    pipeline.history_points_by_token[successful_market.yes_token_id] = [
        {"t": 1_704_067_200, "p": 0.24}
    ]

    published = pipeline.run()

    # Both markets attempted; only the successful one yields a record.
    assert len(pipeline.fetch_history_calls) == 2
    assert published == 1
    assert pipeline.saved["ouro"][0].market_id == successful_market.market_id
