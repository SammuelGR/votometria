import math
from datetime import datetime

import pandas as pd

from transformers.google_trends import (
    PROCESSED_COLUMNS,
    rescale_batches_by_anchor,
    transform_batch_interest_over_time,
)

COLLECTED_AT = datetime(2026, 6, 18, 20, 0, 0)


def _batch(term_values, batch_id):
    """Builds a long batch DataFrame from a wide dict of term -> [v1, v2]."""
    index = pd.to_datetime(["2022-03-13", "2022-03-20"])
    index.name = "date"
    data = dict(term_values)
    data["isPartial"] = [False, False]
    wide = pd.DataFrame(data, index=index)
    return transform_batch_interest_over_time(
        wide,
        election_year="2022",
        batch_id=batch_id,
        anchor_term="Lula",
        geo="BR",
        timeframe="2022-01-01 2022-12-31",
        collected_at=COLLECTED_AT,
    )


def test_rescale_preserves_raw_and_adds_scaled_columns():
    base = _batch({"Lula": [80, 60], "Bolsonaro": [70, 50]}, "batch_01")
    other = _batch({"Lula": [40, 30], "Tebet": [10, 5]}, "batch_02")

    result = rescale_batches_by_anchor([base, other], "Lula")

    assert list(result.columns) == PROCESSED_COLUMNS
    # interest_raw is preserved as-is.
    bolso = result[(result["term"] == "Bolsonaro") & (result["date"] == "2022-03-13")].iloc[0]
    assert bolso["interest_raw"] == 70


def test_base_batch_scaled_equals_raw():
    base = _batch({"Lula": [80, 60], "Bolsonaro": [70, 50]}, "batch_01")
    other = _batch({"Lula": [40, 30], "Tebet": [10, 5]}, "batch_02")

    result = rescale_batches_by_anchor([base, other], "Lula")

    base_rows = result[result["batch_id"] == "batch_01"]
    assert (base_rows["interest_scaled"] == base_rows["interest_raw"]).all()


def test_non_base_batch_is_rescaled_by_anchor():
    base = _batch({"Lula": [80, 60], "Bolsonaro": [70, 50]}, "batch_01")
    # anchor at half the base scale -> factor 80/40 = 2
    other = _batch({"Lula": [40, 30], "Tebet": [10, 5]}, "batch_02")

    result = rescale_batches_by_anchor([base, other], "Lula")

    tebet = result[(result["term"] == "Tebet") & (result["date"] == "2022-03-13")].iloc[0]
    assert tebet["interest_scaled"] == 20.0  # 10 * (80 / 40)


def test_division_by_zero_yields_null_scaled():
    base = _batch({"Lula": [80, 60], "Bolsonaro": [70, 50]}, "batch_01")
    other = _batch({"Lula": [0, 0], "Tebet": [5, 5]}, "batch_02")

    result = rescale_batches_by_anchor([base, other], "Lula")

    tebet = result[result["term"] == "Tebet"].iloc[0]
    assert math.isnan(tebet["interest_scaled"])
    # raw is still preserved for audit
    assert tebet["interest_raw"] == 5


def test_anchor_kept_only_from_base_batch():
    base = _batch({"Lula": [80, 60], "Bolsonaro": [70, 50]}, "batch_01")
    other = _batch({"Lula": [40, 30], "Tebet": [10, 5]}, "batch_02")

    result = rescale_batches_by_anchor([base, other], "Lula")

    anchor_rows = result[result["term"] == "Lula"]
    assert anchor_rows["batch_id"].unique().tolist() == ["batch_01"]


def test_rescale_handles_empty_input():
    result = rescale_batches_by_anchor([], "Lula")
    assert list(result.columns) == PROCESSED_COLUMNS
    assert result.empty
