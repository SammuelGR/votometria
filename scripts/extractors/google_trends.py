import time
from typing import List

import pandas as pd
from pytrends.request import TrendReq

from constants import (
    GOOGLE_TRENDS_BACKOFF_SECONDS,
    GOOGLE_TRENDS_MAX_RETRIES,
    GOOGLE_TRENDS_MAX_TERMS_PER_REQUEST,
)


def build_trends_batches(
    terms: List[str],
    anchor_term: str,
    max_terms_per_request: int = GOOGLE_TRENDS_MAX_TERMS_PER_REQUEST,
) -> List[List[str]]:
    """
    Splits a list of terms into batches that can be compared via an anchor term.

    Each batch is ``[anchor_term] + up to (max_terms_per_request - 1)`` candidates.
    The anchor appears in every batch exactly once, candidate order is preserved
    and the anchor is never duplicated as a candidate. Returns an empty list when
    there are no candidates besides the anchor.
    """
    if max_terms_per_request < 2:
        raise ValueError("max_terms_per_request must allow the anchor plus one candidate.")

    # Drop the anchor and any duplicate from the candidate list while preserving order.
    seen = {anchor_term}
    candidates = []
    for term in terms:
        if term in seen:
            continue
        seen.add(term)
        candidates.append(term)

    if not candidates:
        return []

    chunk_size = max_terms_per_request - 1
    batches = []
    for start in range(0, len(candidates), chunk_size):
        chunk = candidates[start:start + chunk_size]
        batches.append([anchor_term] + chunk)

    return batches


def fetch_interest_over_time_batch(
    terms: List[str],
    timeframe: str,
    geo: str,
    hl: str,
    tz: int,
) -> pd.DataFrame:
    """
    Fetches the Google Trends interest over time for a single batch of terms.

    A batch must be non-empty and contain at most ``GOOGLE_TRENDS_MAX_TERMS_PER_REQUEST``
    terms. Returns the raw wide-format DataFrame from pytrends; an empty DataFrame
    is returned as-is for the pipeline to handle. Retries with backoff on transient
    failures (e.g. rate limiting).
    """
    if not terms:
        raise ValueError("A Google Trends batch requires at least one term.")
    if len(terms) > GOOGLE_TRENDS_MAX_TERMS_PER_REQUEST:
        raise ValueError(
            f"A Google Trends batch accepts at most {GOOGLE_TRENDS_MAX_TERMS_PER_REQUEST} "
            f"terms, but {len(terms)} were provided."
        )

    print(
        f"Querying Google Trends for batch {terms} "
        f"(geo={geo}, timeframe='{timeframe}')..."
    )

    last_error = None
    for attempt in range(1, GOOGLE_TRENDS_MAX_RETRIES + 1):
        try:
            pytrends = TrendReq(hl=hl, tz=tz)
            pytrends.build_payload(kw_list=terms, timeframe=timeframe, geo=geo)
            return pytrends.interest_over_time()
        except Exception as exc:
            last_error = exc
            print(
                f"Google Trends request failed on attempt {attempt}/"
                f"{GOOGLE_TRENDS_MAX_RETRIES}: {exc}"
            )
            if attempt < GOOGLE_TRENDS_MAX_RETRIES:
                time.sleep(GOOGLE_TRENDS_BACKOFF_SECONDS * attempt)

    raise last_error
