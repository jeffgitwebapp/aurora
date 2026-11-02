import asyncio

import pytest
from fastapi.testclient import TestClient

from aurora_backend.contexts.referral.services.catalog.models import (
    RecommendationResult,
    RecommendationStatus,
    ServiceOption,
    ServiceTier,
)
from aurora_backend.contexts.referral.services.catalog.port import CatalogUnavailableError
from aurora_backend.contexts.referral.services.catalog.service import CatalogService
from aurora_backend.main import create_app

ENDPOINT = "/api/referral/recommendations"


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app(catalog_service=CatalogService()))


def recommend(city: str, state: str) -> RecommendationResult:
    return asyncio.run(CatalogService().recommend(city=city, state=state))


@pytest.mark.parametrize(("city", "state"), [("Recife", "PE"), ("São Paulo", "SP")])
def test_catalog_returns_up_to_three_demo_services_in_legal_hierarchy(
    city: str,
    state: str,
) -> None:
    result = recommend(city, state)

    assert result.status is RecommendationStatus.FOUND
    assert 1 <= len(result.services) <= 3
    tiers = [service.tier for service in result.services]
    assert tiers == sorted(tiers)
    assert tiers[0] is ServiceTier.PUBLIC_BODY
    assert all(service.demo for service in result.services)
    assert all(service.contact is None for service in result.services)
    assert all(service.last_verified_at is None for service in result.services)


def test_catalog_matches_city_ignoring_case_and_accents() -> None:
    assert recommend("sao paulo", "sp").status is RecommendationStatus.FOUND


@pytest.mark.parametrize(
    ("city", "state"),
    [("Recife", "SP"), ("Olinda", "PE"), ("Cidade Inexistente", "MG")],
)
def test_city_outside_catalog_returns_no_verified_result(city: str, state: str) -> None:
    result = recommend(city, state)

    assert result.status is RecommendationStatus.NO_VERIFIED_RESULT
    assert result.services == ()


def test_result_model_rejects_more_than_three_services() -> None:
    service = ServiceOption(
        id="s",
        name="Serviço",
        tier=ServiceTier.PUBLIC_BODY,
        category="Órgão público",
        description="Teste.",
    )
    with pytest.raises(ValueError):
        RecommendationResult(status=RecommendationStatus.FOUND, services=(service,) * 4)


def test_endpoint_returns_prioritized_cards(client: TestClient) -> None:
    response = client.post(ENDPOINT, json={"city": "  Recife ", "state": "pe"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "found"
    assert payload["city"] == "Recife"
    assert payload["state"] == "PE"
    assert payload["demo"] is True
    assert [service["priority"] for service in payload["services"]] == [1, 2, 3]
    assert [service["category"] for service in payload["services"]] == [
        "Órgão público",
        "Serviço especializado",
        "Sociedade civil",
    ]


def test_endpoint_returns_no_verified_result(client: TestClient) -> None:
    response = client.post(ENDPOINT, json={"city": "Olinda", "state": "PE"})

    assert response.status_code == 200
    assert response.json()["status"] == "no_verified_result"
    assert response.json()["services"] == []


@pytest.mark.parametrize(
    "body",
    [
        {"city": "", "state": "PE"},
        {"city": "   ", "state": "PE"},
        {"city": "Recife", "state": "XX"},
        {"city": "Recife", "state": ""},
        {"city": "Recife"},
        {"city": "Recife", "state": "PER"},
    ],
)
def test_endpoint_rejects_invalid_location(client: TestClient, body: dict[str, str]) -> None:
    assert client.post(ENDPOINT, json=body).status_code == 422


def test_endpoint_ignores_and_never_echoes_coordinate_fields(client: TestClient) -> None:
    response = client.post(
        ENDPOINT,
        json={"city": "Recife", "state": "PE", "latitude": -8.05, "longitude": -34.88},
    )

    assert response.status_code == 200
    assert "latitude" not in response.text


def test_catalog_failure_returns_503() -> None:
    class FailingCatalog:
        async def recommend(self, *, city: str, state: str) -> RecommendationResult:
            del city, state
            raise CatalogUnavailableError

    failing_client = TestClient(create_app(catalog_service=FailingCatalog()))
    response = failing_client.post(ENDPOINT, json={"city": "Recife", "state": "PE"})

    assert response.status_code == 503
    assert "Recife" not in response.text
