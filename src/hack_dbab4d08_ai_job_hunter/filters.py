import pandas as pd

from hack_dbab4d08_ai_job_hunter.schemas import RecommendationRequest


def filter_contractors(
    contractors: pd.DataFrame,
    request: RecommendationRequest,
) -> pd.DataFrame:

    event_date = request.date.isoformat()

    # Город
    mask = (
        contractors["city"].str.lower()
        == request.city.lower()
    )

    # Категория
    mask &= contractors["categories"].apply(
        lambda categories: request.category.lower()
        in [category.lower() for category in categories]
    )

    # Формат мероприятия
    mask &= contractors["event_formats"].apply(
        lambda formats: request.event_format.lower()
        in [event_format.lower() for event_format in formats]
    )

    # Бюджет
    mask &= contractors["price_from_kzt"] <= request.budget

    # Свободен на дату
    mask &= contractors["busy_dates"].apply(
        lambda busy_dates: event_date not in busy_dates
    )

    # Длительность
    if request.duration_hours is not None:
        mask &= (
            contractors["max_hours"].isna()
            | (contractors["max_hours"] >= request.duration_hours)
        )

    return contractors.loc[mask].copy()


def category_exists_in_city(
    contractors: pd.DataFrame,
    request: RecommendationRequest,
) -> bool:

    city_contractors = contractors[
        contractors["city"].str.lower()
        == request.city.lower()
    ]

    return city_contractors["categories"].apply(
        lambda categories: request.category.lower()
        in [category.lower() for category in categories]
    ).any()