import pandas as pd

from hack_dbab4d08_ai_job_hunter.schemas import RecommendationRequest
from hack_dbab4d08_ai_job_hunter.semantic import calculate_semantic_scores


def rank_contractors(
    contractors: pd.DataFrame,
    request: RecommendationRequest,
) -> pd.DataFrame:

    ranked = contractors.copy()

    ranked["score"] = 0.0

    # Язык
    if request.language is not None:
        ranked["score"] += ranked["languages"].apply(
            lambda languages: (
                30
                if request.language.lower()
                in [language.lower() for language in languages]
                else 0
            )
        )

    # Бюджет
    ranked["budget_score"] = (
        (request.budget - ranked["price_from_kzt"])
        / request.budget
        * 20
    ).clip(lower=0, upper=20)

    ranked["score"] += ranked["budget_score"]

    # Длительность
    if request.duration_hours is not None:
        ranked["score"] += ranked["max_hours"].apply(
            lambda max_hours: get_duration_score(
                max_hours,
                request.duration_hours,
            )
        )

    # Совпадение пожеланий с description
    if request.preferences:
        descriptions = (
            ranked["description"]
            .fillna("")
            .astype(str)
            .tolist()
        )

        semantic_scores = calculate_semantic_scores(
            descriptions,
            request.preferences,
        )

        ranked["semantic_score"] = semantic_scores

        ranked["score"] += ranked["semantic_score"] * 40

    else:
        ranked["semantic_score"] = 0.0

    # Сортировка
    ranked = ranked.sort_values(
        by=["score", "price_from_kzt", "id"],
        ascending=[False, True, True],
    )

    return ranked


def get_duration_score(
    max_hours: float,
    required_hours: int,
) -> int:

    if pd.isna(max_hours):
        return 10

    if max_hours == required_hours:
        return 15

    if max_hours > required_hours:
        return 10

    return 0