import pandas as pd

from hack_dbab4d08_ai_job_hunter.schemas import RecommendationRequest


def get_rejection_stats(
    contractors: pd.DataFrame,
    request: RecommendationRequest,
) -> dict:
    stats = {
        "wrong_format": 0,
        "over_budget": 0,
        "busy": 0,
        "duration": 0,
    }

    # Берём только нужный город
    candidates = contractors[
        contractors["city"].str.lower() == request.city.lower()
    ]

    # И только нужную категорию
    candidates = candidates[
        candidates["categories"].apply(
            lambda categories: request.category.lower()
            in [category.lower() for category in categories]
        )
    ]

    event_date = request.date.isoformat()

    for _, contractor in candidates.iterrows():

        # 1. Не работает с таким форматом
        formats = [
            event_format.lower()
            for event_format in contractor["event_formats"]
        ]

        if request.event_format.lower() not in formats:
            stats["wrong_format"] += 1
            continue

        # 2. Не проходит по бюджету
        if contractor["price_from_kzt"] > request.budget:
            stats["over_budget"] += 1
            continue

        # 3. Занят
        if event_date in contractor["busy_dates"]:
            stats["busy"] += 1
            continue

        # 4. Не хватает часов
        if (
            request.duration_hours is not None
            and pd.notna(contractor["max_hours"])
            and contractor["max_hours"] < request.duration_hours
        ):
            stats["duration"] += 1
            continue

    return stats
    
def build_no_matches_message(stats: dict) -> str:
    reasons = []

    if stats["wrong_format"] > 0:
        reasons.append(
            f"{stats['wrong_format']} не работают с таким форматом мероприятия"
        )

    if stats["over_budget"] > 0:
        reasons.append(
            f"{stats['over_budget']} превышают указанный бюджет"
        )

    if stats["busy"] > 0:
        reasons.append(
            f"{stats['busy']} заняты на выбранную дату"
        )

    if stats["duration"] > 0:
        reasons.append(
            f"{stats['duration']} не могут работать столько часов"
        )

    if not reasons:
        return "Подходящих подрядчиков не найдено."

    return "Подходящих подрядчиков не найдено: " + ", ".join(reasons) + "."