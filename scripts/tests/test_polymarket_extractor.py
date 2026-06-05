import os
import sys
import types
import unittest
from unittest.mock import Mock, patch


SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPTS_DIR)
sys.modules.setdefault("requests", types.SimpleNamespace(get=Mock()))

from constants import POLYMARKET_HISTORY_FIDELITY_MINUTES
from extractors.polymarket import fetch_price_history


class PolymarketExtractorTest(unittest.TestCase):
    @patch("extractors.polymarket.requests.get")
    def test_fetch_price_history_requests_hourly_fidelity(self, requests_get):
        response = Mock()
        response.json.return_value = {"history": []}
        requests_get.return_value = response

        fetch_price_history(
            token_id="yes-token",
            start_ts=1704067200,
            end_ts=1704070800,
        )

        request_params = requests_get.call_args.kwargs["params"]
        self.assertEqual(request_params["fidelity"], POLYMARKET_HISTORY_FIDELITY_MINUTES)


if __name__ == "__main__":
    unittest.main()
