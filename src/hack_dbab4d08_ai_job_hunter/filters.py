import pandas as pd

from hack_dbab4d08_ai_job_hunter.schemas import RecommendationRequest


def filter_by_city_and_category(
    contractors: pd.DataFrame,
    request: RecommendationRequest,
) -> pd.DataFrame:

    filtered = contractors[
        contractors["city"].str.lower() == request.city.lower()
    ]

    filtered = filtered[
        filtered["categories"].apply(
            lambda categories: request.category.lower()
            in [category.lower() for category in categories]
        )
    ]

    return filtered