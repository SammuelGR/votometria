from datetime import datetime

import pandas as pd
import pytest

from transformers.google_trends import (
    BATCH_LONG_COLUMNS,
    MONTHLY_COLUMNS,
    build_monthly_interest,
    filter_by_min_date,
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


def _dated_frame():
    return pd.DataFrame(
        {
            "date": ["2025-10-01", "2025-12-31", "2026-01-01", "2026-03-01"],
            "term": ["Lula", "Lula", "Lula", "Lula"],
        }
    )


def test_filter_by_min_date_drops_rows_before_threshold():
    result = filter_by_min_date(_dated_frame(), "2026-01-01")

    assert list(result["date"]) == ["2026-01-01", "2026-03-01"]


def test_filter_by_min_date_returns_unchanged_when_min_date_is_none():
    df = _dated_frame()

    result = filter_by_min_date(df, None)

    assert list(result["date"]) == list(df["date"])


def test_filter_by_min_date_returns_unchanged_when_min_date_is_empty_string():
    df = _dated_frame()

    result = filter_by_min_date(df, "")

    assert list(result["date"]) == list(df["date"])


def _daily_interest_frame():
    return pd.DataFrame(
        {
            "election_year": ["2026", "2026", "2026", "2026", "2026", "2022"],
            "date": ["2026-06-01", "2026-06-15", "2026-06-30", "2026-07-01", "2026-07-15", "2026-06-01"],
            "term": ["Lula", "Lula", "Lula", "Lula", "Lula", "Lula"],
            "interest_raw": [40, 60, 50, 20, 30, 10],
        }
    )


def test_build_monthly_interest_averages_within_each_month():
    result = build_monthly_interest(_daily_interest_frame())

    assert list(result.columns) == MONTHLY_COLUMNS

    june_2026 = result[(result["election_year"] == "2026") & (result["date"] == "2026-06-01")].iloc[0]
    assert june_2026["term"] == "Lula"
    assert june_2026["interest_mean"] == pytest.approx(50.0)  # mean(40, 60, 50)

    july_2026 = result[(result["election_year"] == "2026") & (result["date"] == "2026-07-01")].iloc[0]
    assert july_2026["interest_mean"] == pytest.approx(25.0)  # mean(20, 30)


def test_build_monthly_interest_keeps_election_years_separate():
    result = build_monthly_interest(_daily_interest_frame())

    june_2022 = result[(result["election_year"] == "2022") & (result["date"] == "2026-06-01")]
    # 2022's June row must not be averaged together with 2026's June rows.
    assert june_2022["interest_mean"].iloc[0] == pytest.approx(10.0)
    assert len(result) == 3  # 2026-06, 2026-07, 2022-06


def test_build_monthly_interest_handles_empty_frame():
    result = build_monthly_interest(pd.DataFrame(columns=["election_year", "date", "term", "interest_raw"]))

    assert list(result.columns) == MONTHLY_COLUMNS
    assert result.empty
