import pandas as pd
from fastapi.testclient import TestClient

import hack_dbab4d08_ai_job_hunter.main as main_module
from hack_dbab4d08_ai_job_hunter.filters import filter_contractors
from hack_dbab4d08_ai_job_hunter.schemas import RecommendationRequest


client = TestClient(main_module.app)


def make_contractors() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "id": "HK-1",
                "anon_name": "Первый",
                "categories": ["Фотограф"],
                "city": "Астана",
                "price_from_kzt": 200000,
                "event_formats": ["свадьба"],
                "languages": ["русский"],
                "max_hours": 10.0,
                "busy_dates": {"2026-10-15"},
                "description": "Свадебный фотограф.",
            },
            {
                "id": "HK-2",
                "anon_name": "Второй",
                "categories": ["Фотограф"],
                "city": "Астана",
                "price_from_kzt": 250000,
                "event_formats": ["свадьба"],
                "languages": ["русский", "казахский"],
                "max_hours": 10.0,
                "busy_dates": set(),
                "description": "Фотограф мероприятий.",
            },
            {
                "id": "HK-3",
                "anon_name": "Третий",
                "categories": ["Фотограф"],
                "city": "Астана",
                "price_from_kzt": 280000,
                "event_formats": ["свадьба"],
                "languages": ["русский"],
                "max_hours": 8.0,
                "busy_dates": set(),
                "description": "Свадебная фотография.",
            },
            {
                "id": "HK-4",
                "anon_name": "Четвертый",
                "categories": ["Фотограф"],
                "city": "Астана",
                "price_from_kzt": 290000,
                "event_formats": ["свадьба"],
                "languages": ["русский"],
                "max_hours": 12.0,
                "busy_dates": set(),
                "description": "Репортажный фотограф.",
            },
            {
                "id": "HK-5",
                "anon_name": "Пятый",
                "categories": ["Фотограф"],
                "city": "Астана",
                "price_from_kzt": 300000,
                "event_formats": ["свадьба"],
                "languages": ["русский"],
                "max_hours": 8.0,
                "busy_dates": set(),
                "description": "Фотограф для свадеб.",
            },
        ]
    )


def make_request(
    date: str = "2026-10-15",
    budget: int = 300000,
) -> RecommendationRequest:
    return RecommendationRequest(
        city="Астана",
        date=date,
        event_format="свадьба",
        category="Фотограф",
        budget=budget,
        duration_hours=8,
        language="русский",
    )


def test_busy_contractor_is_excluded():
    contractors = make_contractors()

    request = make_request(
        date="2026-10-15",
    )

    result = filter_contractors(
        contractors,
        request,
    )

    ids = result["id"].tolist()

    assert "HK-1" not in ids


def test_over_budget_contractor_is_excluded():
    contractors = make_contractors()

    request = make_request(
        date="2026-10-16",
        budget=260000,
    )

    result = filter_contractors(
        contractors,
        request,
    )

    assert all(
        result["price_from_kzt"] <= 260000
    )


def test_api_returns_maximum_three_contractors(monkeypatch):
    contractors = make_contractors()

    monkeypatch.setattr(
        main_module,
        "contractors",
        contractors,
    )

    response = client.post(
        "/recommend",
        json={
            "city": "Астана",
            "date": "2026-10-16",
            "event_format": "свадьба",
            "category": "Фотограф",
            "budget": 300000,
            "duration_hours": 8,
            "language": "русский",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert data["count"] <= 3
    assert len(data["contractors"]) <= 3


def test_same_request_returns_same_order(monkeypatch):
    contractors = make_contractors()

    monkeypatch.setattr(
        main_module,
        "contractors",
        contractors,
    )

    request = {
        "city": "Астана",
        "date": "2026-10-16",
        "event_format": "свадьба",
        "category": "Фотограф",
        "budget": 300000,
        "duration_hours": 8,
        "language": "русский",
    }

    first_response = client.post(
        "/recommend",
        json=request,
    )

    second_response = client.post(
        "/recommend",
        json=request,
    )

    first_ids = [
        contractor["id"]
        for contractor in first_response.json()["contractors"]
    ]

    second_ids = [
        contractor["id"]
        for contractor in second_response.json()["contractors"]
    ]

    assert first_ids == second_ids

def test_category_not_found(monkeypatch):
    contractors = make_contractors()

    monkeypatch.setattr(
        main_module,
        "contractors",
        contractors,
    )

    response = client.post(
        "/recommend",
        json={
            "city": "Астана",
            "date": "2026-10-15",
            "event_format": "свадьба",
            "category": "Видеограф",
            "budget": 300000,
            "duration_hours": 8,
            "language": "русский",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "category_not_found"
    assert data["count"] == 0
    assert data["contractors"] == []

def test_different_dates_change_results(monkeypatch):
    contractors = make_contractors()

    monkeypatch.setattr(
        main_module,
        "contractors",
        contractors,
    )

    request = {
        "city": "Астана",
        "event_format": "свадьба",
        "category": "Фотограф",
        "budget": 300000,
        "duration_hours": 8,
        "language": "русский",
    }

    first_response = client.post(
        "/recommend",
        json={
            **request,
            "date": "2026-10-15",
        },
    )

    second_response = client.post(
        "/recommend",
        json={
            **request,
            "date": "2026-10-16",
        },
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    first_ids = [
        contractor["id"]
        for contractor in first_response.json()["contractors"]
    ]

    second_ids = [
        contractor["id"]
        for contractor in second_response.json()["contractors"]
    ]

    assert first_ids != second_ids