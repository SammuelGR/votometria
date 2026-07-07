from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.market_expectation_options import MarketExpectationOptionsResponse
from app.schemas.market_expectations import MarketExpectationInterval, MarketExpectationsResponse
from app.schemas.monthly_market_expectations import MonthlyMarketExpectationsResponse
from app.services.market_expectation_options import get_market_expectation_options
from app.services.market_expectations import get_market_expectations
from app.services.monthly_market_expectations import get_monthly_market_expectations


router = APIRouter()


@router.get(
    "/market-expectations",
    response_model=MarketExpectationsResponse,
)
def read_market_expectations(
    from_date: datetime | None = Query(default=None, alias="fromDate"),
    to_date: datetime | None = Query(default=None, alias="toDate"),
    interval: MarketExpectationInterval = Query(default="1h"),
    candidate_catalog_ids: list[int] | None = Query(
        default=None,
        alias="candidateCatalogIds",
    ),
    db: Session = Depends(get_db),
):
    if from_date and to_date and from_date > to_date:
        raise HTTPException(
            status_code=400,
            detail="fromDate must be earlier than or equal to toDate.",
        )

    return get_market_expectations(
        db,
        from_date=from_date,
        to_date=to_date,
        interval=interval,
        candidate_catalog_ids=candidate_catalog_ids,
    )


@router.get(
    "/monthly-market-expectations",
    response_model=MonthlyMarketExpectationsResponse,
)
def read_monthly_market_expectations(
    candidate: str = Query(default=""),
    db: Session = Depends(get_db),
):
    return get_monthly_market_expectations(db, candidate=candidate)


@router.get(
    "/market-expectations/options",
    response_model=MarketExpectationOptionsResponse,
)
def read_market_expectation_options(db: Session = Depends(get_db)):
    return get_market_expectation_options(db)
