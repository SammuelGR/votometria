from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.market_expectations import MarketExpectationsResponse
from app.services.market_expectations import get_market_expectations


router = APIRouter()


@router.get(
    "/market-expectations",
    response_model=MarketExpectationsResponse,
)
def read_market_expectations(db: Session = Depends(get_db)):
    return get_market_expectations(db)
