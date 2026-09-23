from fastapi import FastAPI

from hack_dbab4d08_ai_job_hunter.data_loader import load_contractors
from hack_dbab4d08_ai_job_hunter.explanations import build_explanation
from hack_dbab4d08_ai_job_hunter.filters import (
    category_exists_in_city,
    filter_contractors,
)
from hack_dbab4d08_ai_job_hunter.ranking import rank_contractors
from hack_dbab4d08_ai_job_hunter.schemas import RecommendationRequest
from hack_dbab4d08_ai_job_hunter.diagnostics import (
    build_no_matches_message,
    get_rejection_stats,
)


app = FastAPI()

contractors = load_contractors()


@app.post("/recommend")
def recommend(request: RecommendationRequest):
    # Проверяем, существует ли такая категория в выбранном городе
    category_exists = category_exists_in_city(contractors, request)

    if not category_exists:
        return {
            "status": "category_not_found",
            "count": 0,
            "message": (
                f"В городе {request.city} нет подрядчиков "
                f"категории «{request.category}»."
            ),
            "contractors": [],
        }

    # Применяем все жёсткие фильтры
    filtered = filter_contractors(contractors, request)

    # Категория есть, но никто не прошёл условия
    if filtered.empty:
        stats = get_rejection_stats(contractors, request)

    return {
        "status": "no_matches",
        "count": 0,
        "message": build_no_matches_message(stats),
        "rejection_stats": stats,
        "contractors": [],
    }

    # Ранжируем оставшихся кандидатов
    ranked = rank_contractors(filtered, request)

    # Берём максимум 3
    top_contractors = ranked.head(3).copy()

    # Создаём объяснение
    top_contractors["explanation"] = top_contractors.apply(
        lambda contractor: build_explanation(contractor, request),
        axis=1,
    )

    return {
        "status": "success",
        "count": len(top_contractors),
        "contractors": top_contractors[
            [
                "id",
                "anon_name",
                "city",
                "price_from_kzt",
                "languages",
                "score",
                "explanation",
            ]
        ].to_dict(orient="records"),
    }