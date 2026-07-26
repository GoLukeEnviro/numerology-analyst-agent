"""HTTP contract tests for the stateless FastAPI calculation boundary."""

from __future__ import annotations

from collections.abc import AsyncIterator

from httpx import ASGITransport, AsyncClient
import pytest

from numerology_api.app import ApiSettings, create_app


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    app = create_app(
        ApiSettings(
            environment="test",
            allowed_origins=("https://numra.example",),
        )
    )
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="https://testserver",
    ) as http_client:
        yield http_client


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def _request() -> dict[str, object]:
    return {
        "person": {
            "core_name": "Max Mustermann",
            "active_name": "Max Power",
            "birth_date": "1985-07-25",
            "as_of_date": "2026-07-26",
            "locale": "de",
            "consent_given": False,
        },
        "policy": {
            "system": "pythagorean",
            "version": "v1",
            "y_mode": "phonetic",
            "umlaut_policy": "de-direct-v1",
            "name_basis": "both_separate",
            "date_method": "both",
            "locale": "de",
            "master_numbers": [11, 22, 33],
        },
    }


@pytest.mark.integration
@pytest.mark.anyio
async def test_health_and_meta_are_versioned(client: AsyncClient) -> None:
    live = await client.get("/api/v1/health/live")
    ready = await client.get("/api/v1/health/ready")
    meta = await client.get("/api/v1/meta")

    assert live.status_code == 200
    assert live.json() == {"status": "ok"}
    assert ready.status_code == 200
    assert ready.json()["engine"] == "ready"
    assert meta.status_code == 200
    assert meta.json()["profile_schema_version"] == "profile-calculation-result-v2"
    assert meta.json()["knowledge_bundle"] == "numra-knowledge-de-v1"
    assert meta.json()["llm"]["enabled"] is False


@pytest.mark.integration
@pytest.mark.anyio
async def test_calculate_returns_complete_profile(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/profiles/calculate",
        json=_request(),
        headers={"X-Correlation-ID": "test-correlation-42"},
    )

    assert response.status_code == 200
    assert response.headers["X-Correlation-ID"] == "test-correlation-42"
    payload = response.json()
    assert payload["core_name"]["expression"]["reduced_value"] == 5
    assert payload["cycles"]["personal_day"]["reduced_value"] == 3
    assert len(payload["deterministic_hash"]) == 64


@pytest.mark.integration
@pytest.mark.anyio
async def test_validation_error_is_problem_details(client: AsyncClient) -> None:
    request = _request()
    person = request["person"]
    assert isinstance(person, dict)
    person["birth_date"] = "2030-01-01"

    response = await client.post(
        "/api/v1/profiles/calculate",
        json=request,
        headers={"X-Correlation-ID": "validation-case"},
    )

    assert response.status_code == 422
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.headers["X-Correlation-ID"] == "validation-case"
    assert response.json()["code"] == "REQUEST_VALIDATION_FAILED"
    assert response.json()["correlation_id"] == "validation-case"
    assert response.json()["field_errors"][0]["field"].startswith("person.")


@pytest.mark.integration
@pytest.mark.anyio
async def test_unknown_fields_are_rejected(client: AsyncClient) -> None:
    request = _request()
    request["unexpected"] = "not allowed"

    response = await client.post("/api/v1/profiles/calculate", json=request)

    assert response.status_code == 422
    assert any(error["code"] == "extra_forbidden" for error in response.json()["field_errors"])


@pytest.mark.integration
@pytest.mark.anyio
async def test_cors_allows_only_configured_origin(client: AsyncClient) -> None:
    allowed = await client.options(
        "/api/v1/profiles/calculate",
        headers={
            "Origin": "https://numra.example",
            "Access-Control-Request-Method": "POST",
        },
    )
    denied = await client.options(
        "/api/v1/profiles/calculate",
        headers={
            "Origin": "https://evil.example",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert allowed.status_code == 200
    assert allowed.headers["access-control-allow-origin"] == "https://numra.example"
    assert denied.status_code == 400


@pytest.mark.integration
@pytest.mark.anyio
async def test_openapi_contains_only_v1_public_routes(client: AsyncClient) -> None:
    schema = (await client.get("/openapi.json")).json()

    assert "/api/v1/profiles/calculate" in schema["paths"]
    assert "/api/v1/analyses/report" not in schema["paths"]
    assert "ProblemDetails" in schema["components"]["schemas"]
