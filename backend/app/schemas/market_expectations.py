from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ApiModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class MarketExpectationPoint(ApiModel):
    timestamp: datetime
    probability: float


class MarketExpectationSeries(ApiModel):
    candidate_catalog_id: int = Field(alias="candidateCatalogId")
    candidate_name: str = Field(alias="candidateName")
    display_name: str = Field(alias="displayName")
    market_id: str = Field(alias="marketId")
    points: list[MarketExpectationPoint]


class MarketExpectationsResponse(ApiModel):
    source: Literal["polymarket"]
    series: list[MarketExpectationSeries]
