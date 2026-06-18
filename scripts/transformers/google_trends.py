from datetime import datetime
from typing import List, Optional

import pandas as pd

from constants import GOOGLE_TRENDS_SOURCE_NAME

# Columns produced per batch (before the anchor-based rescaling step).
BATCH_LONG_COLUMNS = [
    "date",
    "election_year",
    "term",
    "interest_raw",
    "geo",
    "timeframe",
    "source",
    "batch_id",
    "anchor_term",
    "is_anchor",
    "is_partial",
    "collected_at",
]

# Final processed columns (after rescaling adds interest_scaled).
PROCESSED_COLUMNS = [
    "date",
    "election_year",
    "term",
    "interest_raw",
    "interest_scaled",
    "geo",
    "timeframe",
    "source",
    "batch_id",
    "anchor_term",
    "is_anchor",
    "is_partial",
    "collected_at",
]


def transform_batch_interest_over_time(
    df: pd.DataFrame,
    election_year: str,
    batch_id: str,
    anchor_term: str,
    geo: str,
    timeframe: str,
    collected_at: Optional[datetime] = None,
) -> pd.DataFrame:
    """
    Transforms one raw wide-format batch DataFrame into long/tidy format.

    The input index is the date and there is one column per term, plus an optional
    ``isPartial`` flag. Produces one row per (date, term) with ``interest_raw`` and
    the batch/anchor metadata. ``interest_scaled`` is added later by
    :func:`rescale_batches_by_anchor`.
    """
    if collected_at is None:
        collected_at = datetime.now()
    collected_at_iso = collected_at.isoformat(timespec="seconds")

    if df is None or df.empty:
        return pd.DataFrame(columns=BATCH_LONG_COLUMNS)

    df = df.reset_index()
    df = df.rename(columns={df.columns[0]: "date", "isPartial": "is_partial"})

    if "is_partial" not in df.columns:
        df["is_partial"] = False
    df["is_partial"] = df["is_partial"].astype(bool)

    long_df = df.melt(
        id_vars=["date", "is_partial"],
        var_name="term",
        value_name="interest_raw",
    )

    long_df["date"] = pd.to_datetime(long_df["date"]).dt.strftime("%Y-%m-%d")
    long_df["interest_raw"] = (
        pd.to_numeric(long_df["interest_raw"], errors="coerce")
        .fillna(0)
        .round()
        .astype(int)
    )
    long_df["election_year"] = election_year
    long_df["geo"] = geo
    long_df["timeframe"] = timeframe
    long_df["source"] = GOOGLE_TRENDS_SOURCE_NAME
    long_df["batch_id"] = batch_id
    long_df["anchor_term"] = anchor_term
    long_df["is_anchor"] = long_df["term"] == anchor_term
    long_df["collected_at"] = collected_at_iso

    return long_df[BATCH_LONG_COLUMNS].reset_index(drop=True)


def rescale_batches_by_anchor(
    batch_dfs: List[pd.DataFrame],
    anchor_term: str,
    base_batch_id: str = "batch_01",
) -> pd.DataFrame:
    """
    Consolidates the long batches of a single election year and adds
    ``interest_scaled`` by rescaling every batch to the base batch's anchor.

    For each date the scale factor is ``base_anchor / batch_anchor`` and
    ``interest_scaled = interest_raw * scale_factor``. The base batch keeps its
    raw values (factor 1). When the anchor is zero/missing on a date the point
    cannot be rescaled and ``interest_scaled`` is left as null (NaN) — this is an
    intentional, documented approximation. The raw values are always preserved.

    The anchor term is kept only from the base batch in the final output to avoid
    repeating it across every batch.
    """
    non_empty = [df for df in batch_dfs if df is not None and not df.empty]
    if not non_empty:
        return pd.DataFrame(columns=PROCESSED_COLUMNS)

    combined = pd.concat(non_empty, ignore_index=True)

    # Anchor value of the base batch, per date (numerator of the scale factor).
    base_anchor_mask = (
        (combined["batch_id"] == base_batch_id) & (combined["term"] == anchor_term)
    )
    base_anchor = combined.loc[base_anchor_mask].set_index("date")["interest_raw"]
    base_anchor = base_anchor[~base_anchor.index.duplicated()]
    base_anchor_map = base_anchor.to_dict()

    # Anchor value of each batch, per (batch_id, date) (denominator).
    anchor_rows = combined[combined["term"] == anchor_term]
    batch_anchor_map = {
        (row.batch_id, row.date): row.interest_raw
        for row in anchor_rows.itertuples()
    }

    def _scaled(row) -> float:
        if row.batch_id == base_batch_id:
            return float(row.interest_raw)
        base_val = base_anchor_map.get(row.date)
        batch_val = batch_anchor_map.get((row.batch_id, row.date))
        if base_val is None or batch_val is None or batch_val == 0:
            return float("nan")
        return round(row.interest_raw * (base_val / batch_val), 1)

    combined["interest_scaled"] = [_scaled(row) for row in combined.itertuples()]

    # Keep the anchor only from the base batch to avoid duplicating it everywhere.
    drop_anchor_dupes = (
        (combined["term"] == anchor_term) & (combined["batch_id"] != base_batch_id)
    )
    combined = combined[~drop_anchor_dupes].reset_index(drop=True)

    return combined[PROCESSED_COLUMNS]
