from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class RecommendationRequest(BaseModel):
    city: Literal[
        "Алматы",
        "Астана",
        "Зарубежье",
    ]

    date: date

    event_format: Literal[
        "свадьба",
        "той",
        "корпоратив",
        "конференция",
        "юбилей",
        "день рождения",
    ]

    category: str

    budget: int = Field(
        gt=0,
        description="Бюджет в тенге",
    )

    duration_hours: int | None = Field(
        default=None,
        gt=0,
        le=24,
    )

    language: Literal[
        "русский",
        "казахский",
        "английский",
    ] | None = None

    preferences: str | None = Field(
        default=None,
        max_length=500,
    )

    @field_validator("date")
    @classmethod
    def validate_event_date(cls, value: date):
        min_date = date(2026, 9, 23)
        max_date = date(2026, 12, 31)

        if not min_date <= value <= max_date:
            raise ValueError(
                "Дата должна быть в диапазоне "
                "23.09.2026–31.12.2026"
            )

        return value


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