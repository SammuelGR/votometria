from datetime import datetime

from pydantic import Field

from app.schemas.market_expectations import ApiModel, MarketExpectationInterval


class MarketExpectationDateRange(ApiModel):
    min: datetime | None
    max: datetime | None


class MarketExpectationOptionCandidate(ApiModel):
    candidate_catalog_id: int = Field(alias="candidateCatalogId")
    display_name: str = Field(alias="displayName")
    latest_probability: float | None = Field(alias="latestProbability")


class MarketExpectationOptionsResponse(ApiModel):
    date_range: MarketExpectationDateRange = Field(alias="dateRange")
    intervals: list[MarketExpectationInterval]
    candidates: list[MarketExpectationOptionCandidate]
    default_candidate_catalog_ids: list[int] = Field(alias="defaultCandidateCatalogIds")
