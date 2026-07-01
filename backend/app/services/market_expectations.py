"""
Market-expectations service backed by the gold (ouro) spreadsheet.

The former implementation queried PostgreSQL (``PolymarketProbability`` +
``CandidateCatalog``). Polymarket now lives in the gold layer, so this reads the
consolidated probability series from the gold tab and reproduces the same
filtering / resampling / summary logic over a pandas DataFrame. The response
schema is unchanged, so the frontend keeps working as-is.
"""

from collections import OrderedDict

import pandas as pd

from app.schemas.market_expectations import (
    MarketExpectationInterval,
    MarketExpectationLargestChange,
    MarketExpectationLeader,
    MarketExpectationLeaderMargin,
    MarketExpectationPoint,
    MarketExpectationSeries,
    MarketExpectationsMetadata,
    MarketExpectationsResponse,
    MarketExpectationsSummary,
)
from app.services import gold_sheets

SUPPORTED_MARKET_EXPECTATION_INTERVALS: tuple[MarketExpectationInterval, ...] = (
    "1h",
    "4h",
    "1d",
    "1w",
)


def get_market_expectations(
    df: pd.DataFrame | None = None,
    *,
    from_date=None,
    to_date=None,
    interval: MarketExpectationInterval = "1h",
    candidate_catalog_ids: list[int] | None = None,
) -> MarketExpectationsResponse:
    if interval not in SUPPORTED_MARKET_EXPECTATION_INTERVALS:
        raise ValueError(f"Unsupported market expectation interval: {interval}")

    if df is None:
        df = gold_sheets.load_polymarket_gold()

    filtered = _apply_filters(df, from_date, to_date, candidate_catalog_ids)
    resampled = _apply_resampling(filtered, interval)
    series = build_market_expectation_series(resampled)

    return MarketExpectationsResponse(
        sources=["polymarket"],
        metadata=build_market_expectations_metadata(df),
        summary=build_market_expectations_summary(series),
        series=series,
    )


def _apply_filters(
    df: pd.DataFrame,
    from_date,
    to_date,
    candidate_catalog_ids: list[int] | None,
) -> pd.DataFrame:
    frame = df
    if from_date is not None:
        frame = frame[frame["timestamp"] >= pd.Timestamp(from_date)]
    if to_date is not None:
        frame = frame[frame["timestamp"] <= pd.Timestamp(to_date)]
    if candidate_catalog_ids:
        frame = frame[frame["candidate_catalog_id"].isin(candidate_catalog_ids)]
    return frame


def _bucket_series(timestamps: pd.Series, interval: MarketExpectationInterval) -> pd.Series:
    if interval == "4h":
        return timestamps.dt.floor("4h")
    if interval == "1d":
        return timestamps.dt.floor("D")
    # 1w: Monday-anchored week, matching Postgres date_trunc('week').
    return timestamps.dt.to_period("W-SUN").dt.start_time


def _apply_resampling(
    df: pd.DataFrame, interval: MarketExpectationInterval
) -> pd.DataFrame:
    if df.empty:
        return df

    if interval == "1h":
        frame = df
    else:
        frame = df.copy()
        frame["_bucket"] = _bucket_series(frame["timestamp"], interval)
        # Keep the latest record within each (candidate, market, bucket).
        latest_idx = frame.groupby(
            ["candidate_catalog_id", "market_id", "_bucket"]
        )["timestamp"].idxmax()
        frame = frame.loc[latest_idx].drop(columns="_bucket")

    return frame.sort_values(
        ["candidate_catalog_id", "market_id", "timestamp"]
    ).reset_index(drop=True)


def build_market_expectation_series(df: pd.DataFrame) -> list[MarketExpectationSeries]:
    series_by_key: "OrderedDict[tuple, MarketExpectationSeries]" = OrderedDict()

    for row in df.itertuples(index=False):
        key = (int(row.candidate_catalog_id), str(row.market_id))
        if key not in series_by_key:
            series_by_key[key] = MarketExpectationSeries(
                candidate_catalog_id=int(row.candidate_catalog_id),
                candidate_name=str(row.candidate_name),
                display_name=str(row.display_name),
                market_id=str(row.market_id),
                points=[],
            )

        series_by_key[key].points.append(
            MarketExpectationPoint(
                timestamp=row.timestamp.to_pydatetime(),
                probability=float(row.probability),
            )
        )

    return list(series_by_key.values())


def build_market_expectations_metadata(df: pd.DataFrame) -> MarketExpectationsMetadata:
    latest = None if df.empty else df["timestamp"].max().to_pydatetime()
    return MarketExpectationsMetadata(latest_timestamp=latest)


def build_market_expectations_summary(
    series: list[MarketExpectationSeries],
) -> MarketExpectationsSummary:
    latest_points = _get_latest_points_by_series(series)

    return MarketExpectationsSummary(
        current_leader=_get_current_leader(latest_points),
        leader_margin=_get_leader_margin(latest_points),
        largest_change=_get_largest_change(series),
    )


def _get_latest_points_by_series(series):
    latest_points = []
    for candidate_series in series:
        if candidate_series.points:
            latest_points.append((candidate_series, candidate_series.points[-1]))
    return latest_points


def _get_current_leader(latest_points) -> MarketExpectationLeader | None:
    if not latest_points:
        return None

    leader_series, leader_point = max(
        latest_points, key=lambda item: item[1].probability
    )
    return MarketExpectationLeader(
        candidate_catalog_id=leader_series.candidate_catalog_id,
        display_name=leader_series.display_name,
        probability=leader_point.probability,
    )


def _get_leader_margin(latest_points) -> MarketExpectationLeaderMargin | None:
    if len(latest_points) < 2:
        return None

    sorted_points = sorted(
        latest_points, key=lambda item: item[1].probability, reverse=True
    )
    leader_series, leader_point = sorted_points[0]
    runner_up_series, runner_up_point = sorted_points[1]

    return MarketExpectationLeaderMargin(
        value=leader_point.probability - runner_up_point.probability,
        leader_candidate_catalog_id=leader_series.candidate_catalog_id,
        runner_up_candidate_catalog_id=runner_up_series.candidate_catalog_id,
    )


def _get_largest_change(series) -> MarketExpectationLargestChange | None:
    changes = []
    for candidate_series in series:
        if len(candidate_series.points) < 2:
            continue
        first_point = candidate_series.points[0]
        last_point = candidate_series.points[-1]
        value = last_point.probability - first_point.probability
        changes.append((candidate_series, value, abs(value)))

    if not changes:
        return None

    selected_series, value, absolute_value = max(changes, key=lambda item: item[2])
    return MarketExpectationLargestChange(
        candidate_catalog_id=selected_series.candidate_catalog_id,
        display_name=selected_series.display_name,
        value=value,
        absolute_value=absolute_value,
    )
