import pandas as pd

from hack_dbab4d08_ai_job_hunter.schemas import RecommendationRequest


def build_explanation(
    contractor: pd.Series,
    request: RecommendationRequest,
) -> str:

    reasons = []

    price = int(contractor["price_from_kzt"])
    difference = request.budget - price
    event_date = request.date.strftime("%d.%m.%Y")

    reasons.append(
    f"Свободен на выбранную дату {event_date}."
    )

    # Бюджет
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

    # Длительность
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
                    f"что покрывает необходимые "
                    f"{request.duration_hours} часов."
                )

    # Semantic match
    semantic_score = contractor.get(
        "semantic_score",
        0,
    )

    if request.preferences and semantic_score > 0.20:
        description = str(
            contractor.get("description", "")
        )

        description_summary = get_description_summary(
            description
        )

        if description_summary:
            reasons.append(
                f"По описанию: {description_summary}"
            )

    return " ".join(reasons)


def get_description_summary(
    description: str,
    max_length: int = 160,
) -> str:

    if not description:
        return ""

    # Берём первое содержательное предложение
    sentences = description.replace(
        "\n", " "
    ).split(".")

    for sentence in sentences:
        sentence = sentence.strip()

        if len(sentence) >= 20:
            if len(sentence) > max_length:
                return sentence[:max_length].rstrip() + "..."

            return sentence + "."

    return ""