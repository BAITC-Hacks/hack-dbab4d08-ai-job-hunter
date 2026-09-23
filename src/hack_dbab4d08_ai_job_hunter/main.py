from fastapi import FastAPI

from hack_dbab4d08_ai_job_hunter.data_loader import load_contractors
from hack_dbab4d08_ai_job_hunter.filters import filter_by_city_and_category
from hack_dbab4d08_ai_job_hunter.schemas import RecommendationRequest


app = FastAPI()

contractors = load_contractors()


@app.post("/recommend")
def recommend(request: RecommendationRequest):
    filtered = filter_by_city_and_category(contractors, request)

    return {
        "total": len(contractors),
        "after_filter": len(filtered),
        "contractors": filtered[
            ["id", "anon_name", "city", "price_from_kzt"]
        ].to_dict(orient="records"),
    }