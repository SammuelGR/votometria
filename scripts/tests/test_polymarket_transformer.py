import os
import sys
import unittest
from datetime import datetime, timezone


SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPTS_DIR)

from transformers.polymarket import parse_market, parse_price_history


def timestamp_from_utc(year, month, day):
    return int(datetime(year, month, day, tzinfo=timezone.utc).timestamp())


class PolymarketTransformerTest(unittest.TestCase):
    def test_parse_market_accepts_json_clob_tokens(self):
        market = {
            "id": "123",
            "groupItemTitle": "Candidate A",
            "clobTokenIds": '["yes-token", "no-token"]',
        }

        parsed = parse_market(market)

        self.assertEqual(parsed.market_id, "123")
        self.assertEqual(parsed.candidate_name, "Candidate A")
        self.assertEqual(parsed.yes_token_id, "yes-token")

    def test_parse_market_accepts_list_clob_tokens(self):
        market = {
            "id": "123",
            "groupItemTitle": "Candidate A",
            "clobTokenIds": ["yes-token", "no-token"],
        }

        parsed = parse_market(market)

        self.assertEqual(parsed.yes_token_id, "yes-token")

    def test_parse_market_skips_placeholder_candidates(self):
        market = {
            "id": "123",
            "groupItemTitle": "Another person",
            "clobTokenIds": ["yes-token", "no-token"],
        }

        self.assertIsNone(parse_market(market))

    def test_parse_price_history_ignores_incomplete_points(self):
        market = parse_market(
            {
                "id": "123",
                "groupItemTitle": "Candidate A",
                "clobTokenIds": ["yes-token", "no-token"],
            }
        )
        valid_point = {
            "t": timestamp_from_utc(2024, 1, 1),
            "p": 0.42,
        }
        incomplete_points = [
            {"t": timestamp_from_utc(2024, 1, 2)},
            {"p": 0.43},
        ]
        history_points = [valid_point, *incomplete_points]

        records = parse_price_history(market, history_points)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].probability, valid_point["p"])
        self.assertEqual(
            records[0].timestamp,
            datetime.fromtimestamp(valid_point["t"], timezone.utc).replace(tzinfo=None),
        )


if __name__ == "__main__":
    unittest.main()
