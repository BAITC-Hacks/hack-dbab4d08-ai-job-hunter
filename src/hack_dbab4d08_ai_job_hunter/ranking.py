import pandas as pd

from hack_dbab4d08_ai_job_hunter.schemas import RecommendationRequest


def rank_contractors(
    contractors: pd.DataFrame,
    request: RecommendationRequest,
) -> pd.DataFrame:
    ranked = contractors.copy()

    ranked["score"] = 0

    # Нужный язык
    if request.language is not None:
        ranked["score"] += ranked["languages"].apply(
            lambda languages: (
                30
                if request.language.lower()
                in [language.lower() for language in languages]
                else 0
            )
        )

    ranked = ranked.sort_values(
        by=["score", "price_from_kzt", "id"],
        ascending=[False, True, True],
    )

    return ranked