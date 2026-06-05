from datetime import datetime, timezone
from typing import Optional

from constants import POLYMARKET_HISTORY_OVERLAP_SECONDS


def calculate_incremental_start_timestamp(last_timestamp: Optional[datetime]) -> Optional[int]:
    """
    Converts the last persisted timestamp into an API start timestamp with a safety overlap.
    """
    if last_timestamp is None:
        return None

    timestamp = last_timestamp.replace(tzinfo=timezone.utc).timestamp()
    return max(0, int(timestamp) - POLYMARKET_HISTORY_OVERLAP_SECONDS)
