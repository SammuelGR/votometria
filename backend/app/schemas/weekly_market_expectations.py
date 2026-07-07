from app.schemas.market_expectations import ApiModel


class WeeklyMarketExpectationPoint(ApiModel):
    date: str
    probability: float


class WeeklyMarketExpectationsResponse(ApiModel):
    points: list[WeeklyMarketExpectationPoint]
