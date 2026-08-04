"""HTTP contract tests for the stateless FastAPI calculation boundary."""

from __future__ import annotations

from collections.abc import AsyncIterator
import logging

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
    assert meta.json()["profile_schema_version"] == "profile-calculation-result-v3"
    assert meta.json()["knowledge_bundle"] == "numra-knowledge-de-v2"
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
async def test_v1_endpoint_rejects_a_foreign_method_version(client: AsyncClient) -> None:
    """Der V1-Endpunkt darf v2 nicht still als v1 rechnen, sondern muss ablehnen.

    Ohne Guard antwortet die Route mit 200 und einem v1-Ergebnis, das die
    v2-Policy im Envelope traegt — eine fuer Clients unsichtbare Fehletikettierung.
    """
    request = _request()
    policy = request["policy"]
    assert isinstance(policy, dict)
    policy["version"] = "v2"

    response = await client.post(
        "/api/v1/profiles/calculate",
        json=request,
        headers={"X-Correlation-ID": "method-version-case"},
    )

    assert response.status_code == 422
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["code"] == "METHOD_VERSION_MISMATCH"
    assert response.json()["correlation_id"] == "method-version-case"


@pytest.mark.integration
@pytest.mark.anyio
async def test_v1_endpoint_still_accepts_its_own_method_version(client: AsyncClient) -> None:
    """Der Guard darf den bestehenden v1-Vertrag nicht veraendern."""
    response = await client.post("/api/v1/profiles/calculate", json=_request())

    assert response.status_code == 200
    assert response.json()["policy"]["version"] == "v1"


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
async def test_unsafe_cross_origin_post_is_rejected(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/profiles/calculate",
        json=_request(),
        headers={"Origin": "https://evil.example"},
    )

    assert response.status_code == 403
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["code"] == "ORIGIN_NOT_ALLOWED"


@pytest.mark.integration
@pytest.mark.anyio
async def test_security_headers_are_attached_to_api_responses(client: AsyncClient) -> None:
    response = await client.get("/api/v1/meta")

    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["permissions-policy"] == (
        "camera=(), microphone=(), geolocation=(), payment=(), usb=()"
    )
    assert response.headers["cache-control"] == "no-store"
    assert (
        response.headers["content-security-policy"] == "default-src 'none'; frame-ancestors 'none'"
    )


@pytest.mark.integration
@pytest.mark.anyio
async def test_oversized_request_is_rejected_before_validation() -> None:
    app = create_app(
        ApiSettings(
            environment="test",
            allowed_origins=("https://numra.example",),
            max_request_body_bytes=256,
        )
    )
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="https://testserver",
    ) as local_client:
        response = await local_client.post(
            "/api/v1/profiles/calculate",
            content=b"x" * 257,
            headers={"Content-Type": "application/json", "X-Correlation-ID": "body-too-large"},
        )

    assert response.status_code == 413
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["code"] == "REQUEST_BODY_TOO_LARGE"
    assert response.json()["correlation_id"] == "body-too-large"


@pytest.mark.integration
@pytest.mark.anyio
async def test_names_have_a_stable_upper_bound(client: AsyncClient) -> None:
    request = _request()
    person = request["person"]
    assert isinstance(person, dict)
    person["core_name"] = "A" * 201

    response = await client.post("/api/v1/profiles/calculate", json=request)

    assert response.status_code == 422
    assert any(
        error["field"] == "person.core_name" and error["code"] == "string_too_long"
        for error in response.json()["field_errors"]
    )


@pytest.mark.integration
@pytest.mark.anyio
async def test_access_logs_do_not_contain_personal_request_data(
    client: AsyncClient,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO, logger="numerology_api.access")

    response = await client.post("/api/v1/profiles/calculate", json=_request())

    assert response.status_code == 200
    messages = "\n".join(record.getMessage() for record in caplog.records)
    assert "/api/v1/profiles/calculate" in messages
    assert "Max Mustermann" not in messages
    assert "Max Power" not in messages
    assert "1985-07-25" not in messages


@pytest.mark.integration
@pytest.mark.anyio
async def test_unhandled_errors_are_generic_and_logs_redact_exception_details(
    caplog: pytest.LogCaptureFixture,
) -> None:
    app = create_app(ApiSettings(environment="test"))

    @app.get("/test/unhandled", include_in_schema=False)
    async def fail_for_test() -> None:
        raise RuntimeError("Max Mustermann 1985-07-25 provider-secret")

    caplog.set_level(logging.ERROR, logger="numerology_api.error")
    async with AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False),
        base_url="https://testserver",
    ) as local_client:
        response = await local_client.get(
            "/test/unhandled",
            headers={"X-Correlation-ID": "safe-error"},
        )

    assert response.status_code == 500
    assert response.json()["code"] == "INTERNAL_SERVER_ERROR"
    assert response.json()["correlation_id"] == "safe-error"
    serialized = response.text + "\n".join(record.getMessage() for record in caplog.records)
    assert "Max Mustermann" not in serialized
    assert "1985-07-25" not in serialized
    assert "provider-secret" not in serialized


@pytest.mark.integration
@pytest.mark.anyio
async def test_openapi_contains_only_v1_public_routes(client: AsyncClient) -> None:
    schema = (await client.get("/openapi.json")).json()

    assert "/api/v1/profiles/calculate" in schema["paths"]
    assert "/api/v1/analyses/report" in schema["paths"]
    assert "/api/v1/analyses/follow-up" in schema["paths"]
    assert "ProblemDetails" in schema["components"]["schemas"]
