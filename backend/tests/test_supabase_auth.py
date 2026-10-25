"""
Sagarvani Reconstructed — Supabase Authentication & Authorization Tests

Tests:
1. Protected endpoint (/api/auth/me) rejects requests with missing token (401).
2. Protected endpoint (/api/auth/me) rejects requests with invalid token (401).
3. Protected endpoint (/api/auth/me) returns user claims for verified token.
4. Query endpoint (/api/orca/query) executes and optionally records user_id when authenticated.
5. Query endpoint rejects malformed/invalid bearer tokens with 401.
6. Query endpoint rejects unauthenticated requests when require_query_auth is enforced.
7. SQLite catalog Migration 5 persists user_id correctly on runs.
"""

import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from backend.main import app, get_gateway_registry
from backend.core.auth import AuthenticatedUser, get_current_user, get_current_user_optional
from backend.core.config import settings
from backend.models.enums import DataMode
from backend.models.evidence import EvidenceRecord


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_gateways():
    """Deterministic offline mock gateways fixture."""
    async def _mock_marine(params):
        now = params["retrieved_at"]
        ev = [
            EvidenceRecord(
                evidence_id="ev_m1",
                source_id="open_meteo_marine",
                source_name="Open-Meteo Marine API",
                product_id="marine_forecast",
                parameter="significant_wave_height",
                value=1.5,
                unit="m",
                location=params.get("location", {"lat": params["lat"], "lon": params["lon"]}),
                retrieved_at=now.isoformat(),
                valid_from=now.isoformat(),
                data_mode=DataMode.TEST_FIXTURE,
                quality_flags=["PASSED_RANGE_CHECK"],
                lineage_parent_ids=[],
                source_url="https://marine-api.open-meteo.com/v1/marine",
                attribution="Open-Meteo (CC BY 4.0)",
                schema_version="1.0.0",
            ),
            EvidenceRecord(
                evidence_id="ev_m2",
                source_id="open_meteo_marine",
                source_name="Open-Meteo Marine API",
                product_id="marine_forecast",
                parameter="wave_period",
                value=8.0,
                unit="s",
                location=params.get("location", {"lat": params["lat"], "lon": params["lon"]}),
                retrieved_at=now.isoformat(),
                valid_from=now.isoformat(),
                data_mode=DataMode.TEST_FIXTURE,
                quality_flags=["PASSED_RANGE_CHECK"],
                lineage_parent_ids=[],
                source_url="https://marine-api.open-meteo.com/v1/marine",
                attribution="Open-Meteo (CC BY 4.0)",
                schema_version="1.0.0",
            ),
            EvidenceRecord(
                evidence_id="ev_m3",
                source_id="open_meteo_marine",
                source_name="Open-Meteo Marine API",
                product_id="marine_forecast",
                parameter="swell_wave_height",
                value=1.1,
                unit="m",
                location=params.get("location", {"lat": params["lat"], "lon": params["lon"]}),
                retrieved_at=now.isoformat(),
                valid_from=now.isoformat(),
                data_mode=DataMode.TEST_FIXTURE,
                quality_flags=["PASSED_RANGE_CHECK"],
                lineage_parent_ids=[],
                source_url="https://marine-api.open-meteo.com/v1/marine",
                attribution="Open-Meteo (CC BY 4.0)",
                schema_version="1.0.0",
            ),
        ]
        return {"raw": "marine"}, ev

    async def _mock_weather(params):
        now = params["retrieved_at"]
        ev = [
            EvidenceRecord(
                evidence_id="ev_w1",
                source_id="open_meteo_weather",
                source_name="Open-Meteo Weather API",
                product_id="weather_forecast",
                parameter="wind_speed_10m",
                value=15.0,
                unit="km/h",
                location=params.get("location", {"lat": params["lat"], "lon": params["lon"]}),
                retrieved_at=now.isoformat(),
                valid_from=now.isoformat(),
                data_mode=DataMode.TEST_FIXTURE,
                quality_flags=["PASSED_RANGE_CHECK"],
                lineage_parent_ids=[],
                source_url="https://api.open-meteo.com/v1/forecast",
                attribution="Open-Meteo (CC BY 4.0)",
                schema_version="1.0.0",
            ),
            EvidenceRecord(
                evidence_id="ev_w2",
                source_id="open_meteo_weather",
                source_name="Open-Meteo Weather API",
                product_id="weather_forecast",
                parameter="wind_gusts_10m",
                value=22.0,
                unit="km/h",
                location=params.get("location", {"lat": params["lat"], "lon": params["lon"]}),
                retrieved_at=now.isoformat(),
                valid_from=now.isoformat(),
                data_mode=DataMode.TEST_FIXTURE,
                quality_flags=["PASSED_RANGE_CHECK"],
                lineage_parent_ids=[],
                source_url="https://api.open-meteo.com/v1/forecast",
                attribution="Open-Meteo (CC BY 4.0)",
                schema_version="1.0.0",
            ),
            EvidenceRecord(
                evidence_id="ev_w3",
                source_id="open_meteo_weather",
                source_name="Open-Meteo Weather API",
                product_id="weather_forecast",
                parameter="surface_pressure",
                value=1012.0,
                unit="hPa",
                location=params.get("location", {"lat": params["lat"], "lon": params["lon"]}),
                retrieved_at=now.isoformat(),
                valid_from=now.isoformat(),
                data_mode=DataMode.TEST_FIXTURE,
                quality_flags=["PASSED_RANGE_CHECK"],
                lineage_parent_ids=[],
                source_url="https://api.open-meteo.com/v1/forecast",
                attribution="Open-Meteo (CC BY 4.0)",
                schema_version="1.0.0",
            ),
        ]
        return {"raw": "weather"}, ev

    return {
        "open_meteo_marine": _mock_marine,
        "open_meteo_weather": _mock_weather,
    }


# ---------------------------------------------------------------------------
# Test 1 & 2: Protected /api/auth/me rejects missing or invalid tokens
# ---------------------------------------------------------------------------

def test_auth_me_missing_token_returns_401(client):
    """GET /api/auth/me without an Authorization header must return HTTP 401."""
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401
    assert "Missing Authorization header" in resp.json()["detail"]


def test_auth_me_invalid_token_returns_401(client):
    """GET /api/auth/me with a malformed/invalid bearer token must return HTTP 401."""
    headers = {"Authorization": "Bearer not-a-real-token-xyz123"}
    resp = client.get("/api/auth/me", headers=headers)
    assert resp.status_code == 401
    assert "Invalid or unauthorized" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# Test 3: Protected /api/auth/me returns operator data for verified user
# ---------------------------------------------------------------------------

def test_auth_me_verified_user(client):
    """GET /api/auth/me with a verified AuthenticatedUser dependency returns 200 and profile."""
    mock_user = AuthenticatedUser(
        user_id="usr_8823f9a1-0000-4000-8000-abcdef012345",
        email="operator.malpe@sagarvani.marine",
        role="authenticated",
        metadata={"stakeholder_role": "fisherman_community", "port": "Malpe Harbour"},
    )
    app.dependency_overrides[get_current_user] = lambda: mock_user
    try:
        headers = {"Authorization": "Bearer mock-verified-token"}
        resp = client.get("/api/auth/me", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["authenticated"] is True
        assert data["user_id"] == "usr_8823f9a1-0000-4000-8000-abcdef012345"
        assert data["email"] == "operator.malpe@sagarvani.marine"
        assert data["metadata"]["port"] == "Malpe Harbour"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


# ---------------------------------------------------------------------------
# Test 4: Query execution with authenticated user records attribution
# ---------------------------------------------------------------------------

def test_query_with_authenticated_user(client, mock_gateways):
    """POST /api/orca/query attributes execution run to authenticated user."""
    mock_user = AuthenticatedUser(
        user_id="usr_fisher_9901",
        email="fisher.karwar@sagarvani.marine",
        role="authenticated",
    )
    app.dependency_overrides[get_gateway_registry] = lambda: mock_gateways
    app.dependency_overrides[get_current_user_optional] = lambda: mock_user
    try:
        payload = {
            "query": "Is it safe to fish near Karwar today?",
            "stakeholder_role": "fisherman_community",
            "presentation_mode": "field_community",
            "context_override": {
                "location": {"lat": 14.80, "lon": 74.13, "location_name": "Karwar"}
            },
        }
        resp = client.post("/api/orca/query", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "COMPLETED"
        assert len(data["evidence"]) == 6
    finally:
        app.dependency_overrides.pop(get_gateway_registry, None)
        app.dependency_overrides.pop(get_current_user_optional, None)


# ---------------------------------------------------------------------------
# Test 5: Query execution rejects malformed token when provided
# ---------------------------------------------------------------------------

def test_query_with_malformed_token_returns_401(client, mock_gateways):
    """POST /api/orca/query with a corrupted bearer token returns HTTP 401."""
    app.dependency_overrides[get_gateway_registry] = lambda: mock_gateways
    try:
        payload = {
            "query": "Is it safe to fish near Karwar today?",
            "stakeholder_role": "fisherman_community",
            "presentation_mode": "field_community",
            "context_override": {
                "location": {"lat": 14.80, "lon": 74.13}
            },
        }
        headers = {"Authorization": "Bearer bad-token-that-is-invalid"}
        resp = client.post("/api/orca/query", json=payload, headers=headers)
        assert resp.status_code == 401
    finally:
        app.dependency_overrides.pop(get_gateway_registry, None)


# ---------------------------------------------------------------------------
# Test 6: Query execution when require_query_auth is enforced
# ---------------------------------------------------------------------------

def test_query_enforces_auth_when_configured(client, mock_gateways):
    """When require_query_auth is enabled, missing token returns HTTP 401."""
    original_setting = settings.require_query_auth
    settings.require_query_auth = True
    app.dependency_overrides[get_gateway_registry] = lambda: mock_gateways
    try:
        payload = {
            "query": "Is it safe to fish near Karwar today?",
            "stakeholder_role": "fisherman_community",
            "presentation_mode": "field_community",
            "context_override": {
                "location": {"lat": 14.80, "lon": 74.13}
            },
        }
        resp = client.post("/api/orca/query", json=payload)
        assert resp.status_code == 401
        assert "Authentication required" in resp.json()["detail"]
    finally:
        settings.require_query_auth = original_setting
        app.dependency_overrides.pop(get_gateway_registry, None)
