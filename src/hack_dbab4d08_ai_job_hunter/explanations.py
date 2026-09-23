import pandas as pd

from hack_dbab4d08_ai_job_hunter.schemas import RecommendationRequest


def build_explanation(
    contractor: pd.Series,
    request: RecommendationRequest,
) -> str:
    reasons = []

    price = int(contractor["price_from_kzt"])

    reasons.append(
        f"Стоимость {price:,} ₸ укладывается в бюджет {request.budget:,} ₸."
    )

    if request.language is not None:
        languages = [lang.lower() for lang in contractor["languages"]]

        if request.language.lower() in languages:
            reasons.append(
                f"Подрядчик работает на языке: {request.language}."
            )

    if request.duration_hours is not None and pd.notna(contractor["max_hours"]):
        reasons.append(
            f"Может работать до {int(contractor['max_hours'])} часов."
        )

    return " ".join(reasons)