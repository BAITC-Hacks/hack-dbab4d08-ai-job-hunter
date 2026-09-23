from datetime import date

from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    city: str
    date: date
    event_format: str
    category: str
    budget: int = Field(gt=0)

    duration_hours: int | None = Field(default=None, gt=0)
    language: str | None = None


class ContractorRecommendation(BaseModel):
    id: str
    name: str
    category: str
    city: str
    price_from_kzt: int
    explanation: str


class RecommendationResponse(BaseModel):
    status: str
    count: int
    recommendations: list[ContractorRecommendation]
    message: str | None = None