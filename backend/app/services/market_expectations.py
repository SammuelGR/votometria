from collections import OrderedDict

from sqlalchemy.orm import Session

from app.models import PolymarketProbability
from app.schemas.market_expectations import (
    MarketExpectationPoint,
    MarketExpectationSeries,
    MarketExpectationsResponse,
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

    return MarketExpectationsResponse(
        source="polymarket",
        series=list(series_by_key.values()),
    )
