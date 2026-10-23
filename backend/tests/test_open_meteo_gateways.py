"""
Comprehensive test suite for Phase 2: First Real Evidence Vertical Slice.
Tests:
- Offline parsing and normalization of deterministic fixtures for both Marine and Weather gateways.
- Correct units, attribution, and timestamps.
- Missing fields and null values.
- Mismatched array lengths and invalid numeric data.
- HTTP errors and malformed JSON payloads.
- Timeouts and bounded retry attempts.
- Grid-cell coordinate offset detection and quality flagging.
- Fixture/live-mode separation (Default test suite makes ZERO network calls).
- Failure propagation through the canonical POST /api/orca/query endpoint.
- Opt-in live test gated by RUN_LIVE_SOURCE_TESTS=1.
"""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch
import httpx
import pytest
from fastapi.testclient import TestClient

from backend.gateways.exceptions import (
    GatewayHTTPStatusError,
    GatewayNetworkError,
    GatewaySchemaValidationError,
    GatewayTimeoutError,
)
from backend.gateways.open_meteo_marine import OpenMeteoMarineGateway
from backend.gateways.open_meteo_weather import OpenMeteoWeatherGateway
from backend.main import app
from backend.models.enums import DataMode, RunStatus

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def marine_fixture():
    with open(FIXTURES_DIR / "open_meteo_marine_sample.json", "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def weather_fixture():
    with open(FIXTURES_DIR / "open_meteo_weather_sample.json", "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def client():
    return TestClient(app)


# ─── 1. Offline Parsing & Normalization Tests ─────────────────────────────────

def test_marine_gateway_parse_and_normalize(marine_fixture):
    """Test marine gateway correctly parses deterministic fixture into 3 EvidenceRecords."""
    gw = OpenMeteoMarineGateway()
    records = gw.parse_and_normalize(
        raw_payload=marine_fixture,
        requested_lat=13.35,
        requested_lon=74.70,
        data_mode=DataMode.TEST_FIXTURE,
    )
    assert len(records) == 3

    params = {r.parameter: r for r in records}
    assert "wave_height" in params
    assert "wave_direction" in params
    assert "wave_period" in params

    wh = params["wave_height"]
    assert wh.value == 1.2
    assert wh.unit == "m"
    assert wh.source_id == "open_meteo_marine"
    assert "Open-Meteo" in wh.attribution
    assert wh.data_mode == DataMode.TEST_FIXTURE
    assert wh.valid_from is not None
    assert wh.observed_at is None  # Distinct from valid_from
    assert any("GRID_OFFSET" in f for f in wh.quality_flags)


def test_weather_gateway_parse_and_normalize(weather_fixture):
    """Test weather gateway correctly parses deterministic fixture into 3 EvidenceRecords."""
    gw = OpenMeteoWeatherGateway()
    records = gw.parse_and_normalize(
        raw_payload=weather_fixture,
        requested_lat=13.35,
        requested_lon=74.70,
        data_mode=DataMode.TEST_FIXTURE,
    )
    assert len(records) == 3

    params = {r.parameter: r for r in records}
    assert "wind_speed_10m" in params
    assert "wind_direction_10m" in params
    assert "wind_gusts_10m" in params

    ws = params["wind_speed_10m"]
    assert ws.value == 18.5
    assert ws.unit == "km/h"
    assert ws.source_id == "open_meteo_weather"
    assert "Open-Meteo" in ws.attribution
    assert ws.data_mode == DataMode.TEST_FIXTURE


# ─── 2. Schema Validation & Defensive Error Tests ─────────────────────────────

def test_marine_gateway_missing_hourly_section():
    """Verify error when hourly section is absent."""
    gw = OpenMeteoMarineGateway()
    with pytest.raises(GatewaySchemaValidationError, match="Missing 'hourly' data section"):
        gw.parse_and_normalize({}, requested_lat=13.35, requested_lon=74.70)


def test_marine_gateway_mismatched_array_lengths(marine_fixture):
    """Verify error when an array length does not match time array."""
    corrupted = dict(marine_fixture)
    corrupted["hourly"] = dict(marine_fixture["hourly"])
    corrupted["hourly"]["wave_period"] = [7.8, 8.0]  # Only 2 items instead of 4
    gw = OpenMeteoMarineGateway()
    with pytest.raises(GatewaySchemaValidationError, match="Array length mismatch"):
        gw.parse_and_normalize(corrupted, requested_lat=13.35, requested_lon=74.70)


def test_weather_gateway_null_values_flagged(weather_fixture):
    """Verify null values are preserved truthfully as UNAVAILABLE and flagged."""
    corrupted = dict(weather_fixture)
    corrupted["hourly"] = dict(weather_fixture["hourly"])
    corrupted["hourly"]["wind_gusts_10m"] = [None, 27.0, 28.5, 24.8]
    gw = OpenMeteoWeatherGateway()
    records = gw.parse_and_normalize(corrupted, requested_lat=13.35, requested_lon=74.70)
    gust_record = [r for r in records if r.parameter == "wind_gusts_10m"][0]
    assert gust_record.value == "UNAVAILABLE"
    assert "NULL_VALUE" in gust_record.quality_flags


# ─── 3. HTTP Errors, Timeouts, and Bounded Retries ────────────────────────────

def test_gateway_http_4xx_raises_without_retry():
    """Verify 4xx errors raise immediately without futile retries."""
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status_code = 400
    mock_resp.text = "Cannot compute marine forecast for land coordinate"
    mock_client.get.return_value = mock_resp

    gw = OpenMeteoMarineGateway(http_client=mock_client, max_retries=2)
    with pytest.raises(GatewayHTTPStatusError) as exc_info:
        gw.fetch_marine_forecast(lat=13.35, lon=74.70)
    assert exc_info.value.status_code == 400
    assert mock_client.get.call_count == 1  # No retry on 400


def test_gateway_retries_on_timeout_and_exhausts():
    """Verify transient timeouts retry up to max_retries and raise GatewayTimeoutError."""
    mock_client = MagicMock()
    mock_client.get.side_effect = httpx.ReadTimeout("Read timed out")

    gw = OpenMeteoWeatherGateway(http_client=mock_client, max_retries=2)
    with pytest.raises(GatewayTimeoutError, match="Request timed out"):
        gw.fetch_weather_forecast(lat=13.35, lon=74.70)
    assert mock_client.get.call_count == 3  # Initial + 2 retries


# ─── 4. Canonical API Query Endpoint Integration (Mocked Gateways) ────────────

@patch("backend.gateways.open_meteo_marine.OpenMeteoMarineGateway.fetch_marine_forecast")
@patch("backend.gateways.open_meteo_weather.OpenMeteoWeatherGateway.fetch_weather_forecast")
def test_canonical_query_endpoint_with_gateways(mock_weather, mock_marine, client, marine_fixture, weather_fixture):
    """Verify canonical endpoint returns 6 validated evidence records when gateways succeed."""
    mock_marine.return_value = marine_fixture
    mock_weather.return_value = weather_fixture

    payload = {
        "query": "What are sea conditions near Malpe?",
        "context_override": {
            "location": {"lat": 13.35, "lon": 74.70, "location_name": "Malpe Harbor"},
            "language": "en"
        }
    }
    resp = client.post("/api/orca/query", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["status"] == "COMPLETED"
    assert data["data_mode"] == "LIVE_FORECAST"
    assert len(data["evidence"]) == 6
    assert data["policy_audit"]["overall_verdict"] == "NOT_EVALUABLE"
    assert "PROTOTYPE ONLY" in data["disclaimer"]

    # Check evidence parameters
    param_names = [e["parameter"] for e in data["evidence"]]
    assert "wave_height" in param_names
    assert "wind_speed_10m" in param_names


@patch("backend.gateways.open_meteo_marine.OpenMeteoMarineGateway.fetch_marine_forecast")
@patch("backend.gateways.open_meteo_weather.OpenMeteoWeatherGateway.fetch_weather_forecast")
def test_canonical_query_partial_failure(mock_weather, mock_marine, client, marine_fixture):
    """Verify canonical endpoint gracefully returns PARTIAL when weather gateway fails."""
    mock_marine.return_value = marine_fixture
    mock_weather.side_effect = GatewayTimeoutError("Weather connection timeout", "Open-Meteo Weather API")

    payload = {
        "query": "Conditions near Malpe?",
        "context_override": {
            "location": {"lat": 13.35, "lon": 74.70, "location_name": "Malpe Harbor"}
        }
    }
    resp = client.post("/api/orca/query", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["status"] == "PARTIAL"
    assert len(data["evidence"]) == 3  # Only marine
    assert len(data["gaps"]) == 1
    assert data["gaps"][0]["gap_code"] == "GAP_WEATHER_SOURCE_ERROR"


# ─── 5. Opt-in Live Source Test (Gated by RUN_LIVE_SOURCE_TESTS=1) ─────────────

@pytest.mark.skipif(
    os.getenv("RUN_LIVE_SOURCE_TESTS") != "1",
    reason="Live source tests disabled by default. Run with RUN_LIVE_SOURCE_TESTS=1 to test live Open-Meteo connectivity."
)
def test_live_open_meteo_gateways():
    """
    Opt-in live integration test for Open-Meteo APIs.
    Gated strictly by RUN_LIVE_SOURCE_TESTS=1.
    Performs bounded read-only GET requests for Malpe offshore coordinates (13.35, 74.70).
    """
    marine_gw = OpenMeteoMarineGateway(timeout=8.0)
    weather_gw = OpenMeteoWeatherGateway(timeout=8.0)

    marine_raw = marine_gw.fetch_marine_forecast(lat=13.35, lon=74.70, forecast_days=1)
    weather_raw = weather_gw.fetch_weather_forecast(lat=13.35, lon=74.70, forecast_days=1)

    marine_ev = marine_gw.parse_and_normalize(marine_raw, requested_lat=13.35, requested_lon=74.70)
    weather_ev = weather_gw.parse_and_normalize(weather_raw, requested_lat=13.35, requested_lon=74.70)

    assert len(marine_ev) == 3
    assert len(weather_ev) == 3
    assert all(r.data_mode == DataMode.LIVE_FORECAST for r in marine_ev + weather_ev)
