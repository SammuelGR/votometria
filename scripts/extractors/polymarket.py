import requests
from typing import List, Optional

from constants import (
    POLYMARKET_ELECTION_EVENT_ID,
    POLYMARKET_GAMMA_EVENT_URL,
    POLYMARKET_HISTORY_FIDELITY_MINUTES,
    POLYMARKET_PRICE_HISTORY_URL,
)


def fetch_event_markets(event_id: str = POLYMARKET_ELECTION_EVENT_ID) -> List[dict]:
    """
    Fetches the configured Polymarket event and returns its associated markets.
    """
    url = POLYMARKET_GAMMA_EVENT_URL.format(event_id=event_id)
    print(f"Querying Polymarket Gamma API for Event ID {event_id}...")

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    event_data = response.json()
    return event_data.get("markets", [])


def fetch_price_history(
    token_id: str,
    start_ts: Optional[int] = None,
    end_ts: Optional[int] = None,
) -> List[dict]:
    """
    Fetches historical CLOB prices for a token using an absolute time window when provided.
    """
    params = {
        "market": token_id,
        "fidelity": POLYMARKET_HISTORY_FIDELITY_MINUTES,
    }

    if start_ts is not None:
        params["startTs"] = start_ts
    if end_ts is not None:
        params["endTs"] = end_ts
    if start_ts is None and end_ts is None:
        params["interval"] = "max"

    response = requests.get(POLYMARKET_PRICE_HISTORY_URL, params=params, timeout=30)
    response.raise_for_status()

    history_data = response.json()
    if isinstance(history_data, list):
        return history_data
    if isinstance(history_data, dict):
        return history_data.get("history", [])

    return []
