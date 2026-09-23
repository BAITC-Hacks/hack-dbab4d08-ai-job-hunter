from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    city: str
    date: date
    event_format: str
    category: str
    budget: int = Field(gt=0)

    duration_hours: int | None = Field(default=None, gt=0)
    language: str | None = None
    preferences: str | None = None


class ContractorRecommendation(BaseModel):
    id: str
    name: str
    category: str
    city: str
    price_from_kzt: int
    languages: list[str]

    score: float
    semantic_score: float

    explanation: str


class RejectionStats(BaseModel):
    wrong_format: int
    over_budget: int
    busy: int
    duration: int


class RecommendationResponse(BaseModel):
    status: Literal[
        "success",
        "category_not_found",
        "no_matches",
    ]

    count: int
    message: str | None = None

    rejection_stats: RejectionStats | None = None
    contractors: list[ContractorRecommendation]