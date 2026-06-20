from collections import OrderedDict

from sqlalchemy.orm import Session

from app.models import PolymarketProbability
from app.schemas.market_expectations import (
    MarketExpectationLargestChange,
    MarketExpectationLeader,
    MarketExpectationLeaderMargin,
    MarketExpectationsMetadata,
    MarketExpectationPoint,
    MarketExpectationSeries,
    MarketExpectationsResponse,
    MarketExpectationsSummary,
)


def get_market_expectations(db: Session) -> MarketExpectationsResponse:
    records = (
        db.query(PolymarketProbability)
        .join(PolymarketProbability.candidate_catalog)
        .order_by(
            PolymarketProbability.candidate_catalog_id.asc(),
            PolymarketProbability.market_id.asc(),
            PolymarketProbability.timestamp.asc(),
        )
        .all()
    )
    series = build_market_expectation_series(records)

    return MarketExpectationsResponse(
        sources=["polymarket"],
        metadata=build_market_expectations_metadata(series),
        summary=build_market_expectations_summary(series),
        series=series,
    )


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
    series: list[MarketExpectationSeries],
) -> MarketExpectationsMetadata:
    latest_timestamp = max(
        (point.timestamp for candidate_series in series for point in candidate_series.points),
        default=None,
    )

    return MarketExpectationsMetadata(latest_timestamp=latest_timestamp)


def build_market_expectations_summary(
    series: list[MarketExpectationSeries],
) -> MarketExpectationsSummary:
    latest_points = get_latest_points_by_series(series)

    return MarketExpectationsSummary(
        current_leader=get_current_leader(latest_points),
        leader_margin=get_leader_margin(latest_points),
        largest_change=get_largest_change(series),
    )


def get_latest_points_by_series(
    series: list[MarketExpectationSeries],
) -> list[tuple[MarketExpectationSeries, MarketExpectationPoint]]:
    latest_points = []

    for candidate_series in series:
        if candidate_series.points:
            latest_points.append((candidate_series, candidate_series.points[-1]))

    return latest_points


def get_current_leader(
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


def get_leader_margin(
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


def get_largest_change(
    series: list[MarketExpectationSeries],
) -> MarketExpectationLargestChange | None:
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

    selected_series, value, absolute_value = max(
        changes,
        key=lambda item: item[2],
    )

    return MarketExpectationLargestChange(
        candidate_catalog_id=selected_series.candidate_catalog_id,
        display_name=selected_series.display_name,
        value=value,
        absolute_value=absolute_value,
    )
