from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

MarketExpectationInterval = Literal["1h", "4h", "1d", "1w"]


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


class MarketExpectationsMetadata(ApiModel):
    latest_timestamp: datetime | None = Field(alias="latestTimestamp")


class MarketExpectationLeader(ApiModel):
    candidate_catalog_id: int = Field(alias="candidateCatalogId")
    display_name: str = Field(alias="displayName")
    probability: float


class MarketExpectationLeaderMargin(ApiModel):
    value: float
    leader_candidate_catalog_id: int = Field(alias="leaderCandidateCatalogId")
    runner_up_candidate_catalog_id: int = Field(alias="runnerUpCandidateCatalogId")


class MarketExpectationLargestChange(ApiModel):
    candidate_catalog_id: int = Field(alias="candidateCatalogId")
    display_name: str = Field(alias="displayName")
    value: float
    absolute_value: float = Field(alias="absoluteValue")


class MarketExpectationsSummary(ApiModel):
    current_leader: MarketExpectationLeader | None = Field(alias="currentLeader")
    leader_margin: MarketExpectationLeaderMargin | None = Field(alias="leaderMargin")
    largest_change: MarketExpectationLargestChange | None = Field(alias="largestChange")


class MarketExpectationsResponse(ApiModel):
    sources: list[str]
    metadata: MarketExpectationsMetadata
    summary: MarketExpectationsSummary
    series: list[MarketExpectationSeries]
