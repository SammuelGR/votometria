from app.schemas.market_expectations import ApiModel


class MonthlyMarketExpectationPoint(ApiModel):
    date: str
    probability: float


class MonthlyMarketExpectationsResponse(ApiModel):
    points: list[MonthlyMarketExpectationPoint]
