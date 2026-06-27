from datetime import datetime

import pandas as pd

from transformers.google_trends import (
    BATCH_LONG_COLUMNS,
    transform_batch_interest_over_time,
)


def _raw_wide_frame():
    index = pd.to_datetime(["2022-03-13", "2022-03-20"])
    index.name = "date"
    return pd.DataFrame(
        {
            "Lula": [80, 60],
            "Jair Bolsonaro": [70, 50],
            "isPartial": [False, True],
        },
        index=index,
    )


def test_transform_batch_produces_long_format_with_metadata():
    collected_at = datetime(2026, 6, 18, 20, 0, 0)

    result = transform_batch_interest_over_time(
        _raw_wide_frame(),
        election_year="2022",
        batch_id="batch_01",
        anchor_term="Lula",
        geo="BR",
        timeframe="2022-01-01 2022-12-31",
        collected_at=collected_at,
    )

    assert list(result.columns) == BATCH_LONG_COLUMNS
    assert len(result) == 4  # 2 dates x 2 terms
    assert set(result["term"]) == {"Lula", "Jair Bolsonaro"}

    anchor_row = result[(result["term"] == "Lula") & (result["date"] == "2022-03-13")].iloc[0]
    assert anchor_row["election_year"] == "2022"
    assert anchor_row["batch_id"] == "batch_01"
    assert anchor_row["anchor_term"] == "Lula"
    assert bool(anchor_row["is_anchor"]) is True
    assert anchor_row["interest_raw"] == 80
    assert anchor_row["source"] == "google_trends"
    assert anchor_row["collected_at"] == "2026-06-18T20:00:00"

    candidate_row = result[result["term"] == "Jair Bolsonaro"].iloc[0]
    assert bool(candidate_row["is_anchor"]) is False


def test_transform_batch_enforces_types_and_preserves_is_partial():
    result = transform_batch_interest_over_time(
        _raw_wide_frame(),
        election_year="2022",
        batch_id="batch_01",
        anchor_term="Lula",
        geo="BR",
        timeframe="2022-01-01 2022-12-31",
        collected_at=datetime(2026, 6, 18, 20, 0, 0),
    )

    assert result["interest_raw"].dtype == "int64"
    assert result["is_partial"].dtype == "bool"
    partial_rows = result[result["date"] == "2022-03-20"]
    assert partial_rows["is_partial"].all()


def test_transform_batch_handles_empty_frame():
    result = transform_batch_interest_over_time(
        pd.DataFrame(),
        election_year="2022",
        batch_id="batch_01",
        anchor_term="Lula",
        geo="BR",
        timeframe="2022-01-01 2022-12-31",
    )

    assert list(result.columns) == BATCH_LONG_COLUMNS
    assert result.empty
