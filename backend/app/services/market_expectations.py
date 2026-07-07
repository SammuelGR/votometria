from collections import OrderedDict
from datetime import datetime

from sqlalchemy import Integer, extract, func
from sqlalchemy.orm import Query, Session

from app.models import PolymarketProbability
from app.schemas.market_expectations import (
    MarketExpectationInterval,
    MarketExpectationLargestChange,
    MarketExpectationLeader,
    MarketExpectationLeaderMargin,
    MarketExpectationsMetadata,
    MarketExpectationPoint,
    MarketExpectationSeries,
    MarketExpectationsResponse,
    MarketExpectationsSummary,
)


SUPPORTED_MARKET_EXPECTATION_INTERVALS: tuple[MarketExpectationInterval, ...] = (
    "1h",
    "4h",
    "1d",
    "1w",
)


def get_market_expectations(
    db: Session,
    *,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    interval: MarketExpectationInterval = "1h",
    candidate_catalog_ids: list[int] | None = None,
) -> MarketExpectationsResponse:
    query = _build_market_expectations_query(
        db,
        from_date=from_date,
        to_date=to_date,
        interval=interval,
        candidate_catalog_ids=candidate_catalog_ids,
    )
    records = query.all()
    series = build_market_expectation_series(records)

    return MarketExpectationsResponse(
        sources=["polymarket"],
        metadata=build_market_expectations_metadata(db),
        summary=build_market_expectations_summary(series),
        series=series,
    )


def _build_market_expectations_query(
    db: Session,
    *,
    from_date: datetime | None,
    to_date: datetime | None,
    interval: MarketExpectationInterval,
    candidate_catalog_ids: list[int] | None,
) -> Query:
    if interval not in SUPPORTED_MARKET_EXPECTATION_INTERVALS:
        raise ValueError(f"Unsupported market expectation interval: {interval}")

    query = db.query(PolymarketProbability).join(PolymarketProbability.candidate_catalog)
    query = _apply_market_expectation_filters(
        query,
        from_date=from_date,
        to_date=to_date,
        candidate_catalog_ids=candidate_catalog_ids,
    )

    if interval != "1h":
        query = _apply_market_expectation_resampling(query, db, interval)

    return query.order_by(
        PolymarketProbability.candidate_catalog_id.asc(),
        PolymarketProbability.market_id.asc(),
        PolymarketProbability.timestamp.asc(),
    )


def _apply_market_expectation_filters(
    query: Query,
    *,
    from_date: datetime | None,
    to_date: datetime | None,
    candidate_catalog_ids: list[int] | None,
) -> Query:
    if from_date:
        query = query.filter(PolymarketProbability.timestamp >= from_date)

    if to_date:
        query = query.filter(PolymarketProbability.timestamp <= to_date)

    if candidate_catalog_ids:
        query = query.filter(
            PolymarketProbability.candidate_catalog_id.in_(candidate_catalog_ids)
        )

    return query


def _apply_market_expectation_resampling(
    query: Query,
    db: Session,
    interval: MarketExpectationInterval,
) -> Query:
    bucket = _get_market_expectation_bucket_expression(interval)
    row_number = func.row_number().over(
        partition_by=[
            PolymarketProbability.candidate_catalog_id,
            PolymarketProbability.market_id,
            bucket,
        ],
        order_by=PolymarketProbability.timestamp.desc(),
    )
    latest_records_by_bucket = query.with_entities(
        PolymarketProbability.id.label("probability_id"),
        row_number.label("row_number"),
    ).subquery()

    return (
        db.query(PolymarketProbability)
        .join(
            latest_records_by_bucket,
            PolymarketProbability.id == latest_records_by_bucket.c.probability_id,
        )
        .join(PolymarketProbability.candidate_catalog)
        .filter(latest_records_by_bucket.c.row_number == 1)
    )


def _get_market_expectation_bucket_expression(interval: MarketExpectationInterval):
    timestamp = PolymarketProbability.timestamp

    if interval == "4h":
        bucket_hour = (func.floor(extract("hour", timestamp) / 4) * 4).cast(Integer)

        return func.date_trunc("day", timestamp) + func.make_interval(0, 0, 0, 0, bucket_hour)

    if interval == "1d":
        return func.date_trunc("day", timestamp)

    return func.date_trunc("week", timestamp)


def build_market_expectation_series(
    records: list[PolymarketProbability],
) -> list[MarketExpectationSeries]:
    series_by_key = OrderedDict()

    for record in records:
        key = (record.candidate_catalog_id, record.market_id)
        if key not in series_by_key:
            series_by_key[key] = MarketExpectationSeries(
                candidate_catalog_id=record.candidate_catalog_id,
                candidate_name=record.candidate_name,
                display_name=record.candidate_catalog.display_name,
                market_id=record.market_id,
                points=[],
            )

        series_by_key[key].points.append(
            MarketExpectationPoint(
                timestamp=record.timestamp,
                probability=record.probability,
            )
        )

    return list(series_by_key.values())


def build_market_expectations_metadata(
    db: Session,
) -> MarketExpectationsMetadata:
    latest_timestamp = db.query(func.max(PolymarketProbability.timestamp)).scalar()

    return MarketExpectationsMetadata(latest_timestamp=latest_timestamp)


def build_market_expectations_summary(
    series: list[MarketExpectationSeries],
) -> MarketExpectationsSummary:
    latest_points = _get_latest_points_by_series(series)

    return MarketExpectationsSummary(
        current_leader=_get_current_leader(latest_points),
        leader_margin=_get_leader_margin(latest_points),
        largest_change=_get_largest_change(series),
    )


def _get_latest_points_by_series(
    series: list[MarketExpectationSeries],
) -> list[tuple[MarketExpectationSeries, MarketExpectationPoint]]:
    latest_points = []

    for candidate_series in series:
        if candidate_series.points:
            latest_points.append((candidate_series, candidate_series.points[-1]))

    return latest_points


def _get_current_leader(
    latest_points: list[tuple[MarketExpectationSeries, MarketExpectationPoint]],
) -> MarketExpectationLeader | None:
    if not latest_points:
        return None

    leader_series, leader_point = max(
        latest_points,
        key=lambda item: item[1].probability,
    )

    return MarketExpectationLeader(
        candidate_catalog_id=leader_series.candidate_catalog_id,
        display_name=leader_series.display_name,
        probability=leader_point.probability,
    )


def _get_leader_margin(
    latest_points: list[tuple[MarketExpectationSeries, MarketExpectationPoint]],
) -> MarketExpectationLeaderMargin | None:
    if len(latest_points) < 2:
        return None

    sorted_latest_points = sorted(
        latest_points,
        key=lambda item: item[1].probability,
        reverse=True,
    )
    leader_series, leader_point = sorted_latest_points[0]
    runner_up_series, runner_up_point = sorted_latest_points[1]

    return MarketExpectationLeaderMargin(
        value=leader_point.probability - runner_up_point.probability,
        leader_candidate_catalog_id=leader_series.candidate_catalog_id,
        runner_up_candidate_catalog_id=runner_up_series.candidate_catalog_id,
    )


def _get_largest_change(
    series: list[MarketExpectationSeries],
) -> MarketExpectationLargestChange | None:
    changes = []

    for candidate_series in series:
        if len(candidate_series.points) < 2:
            continue

        for from_point, to_point in zip(
            candidate_series.points,
            candidate_series.points[1:],
        ):
            value = to_point.probability - from_point.probability
            changes.append((candidate_series, from_point, to_point, value, abs(value)))

    if not changes:
        return None

    selected_series, from_point, to_point, value, absolute_value = max(
        changes,
        key=lambda item: item[4],
    )

    return MarketExpectationLargestChange(
        candidate_catalog_id=selected_series.candidate_catalog_id,
        display_name=selected_series.display_name,
        value=value,
        absolute_value=absolute_value,
        from_timestamp=from_point.timestamp,
        to_timestamp=to_point.timestamp,
    )
