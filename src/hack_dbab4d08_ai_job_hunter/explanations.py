import pandas as pd

from hack_dbab4d08_ai_job_hunter.schemas import RecommendationRequest


def build_explanation(
    contractor: pd.Series,
    request: RecommendationRequest,
) -> str:

    reasons = []

    price = int(contractor["price_from_kzt"])

    # Бюджет
    difference = request.budget - price

    if difference > 0:
        reasons.append(
            f"Стоимость {price:,} ₸ ниже бюджета на {difference:,} ₸."
        )
    else:
        reasons.append(
            f"Стоимость {price:,} ₸ точно соответствует бюджету."
        )

    # Язык
    if request.language is not None:
        languages = [
            language.lower()
            for language in contractor["languages"]
        ]

        if request.language.lower() in languages:
            reasons.append(
                f"Работает на языке «{request.language}»."
            )

    # Продолжительность
    if request.duration_hours is not None:
        max_hours = contractor["max_hours"]

        if pd.notna(max_hours):
            max_hours = int(max_hours)

            if max_hours == request.duration_hours:
                reasons.append(
                    f"Может работать необходимые {max_hours} часов."
                )
            elif max_hours > request.duration_hours:
                reasons.append(
                    f"Может работать до {max_hours} часов, "
                    f"что покрывает необходимые {request.duration_hours} часов."
                )

    # Пожелания
    semantic_score = contractor.get("semantic_score", 0)

    if request.preferences and semantic_score > 0.05:
        reasons.append(
            "Описание подрядчика совпадает с указанными пожеланиями."
        )

    return " ".join(reasons)