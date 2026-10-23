"""
Offline tests for Phase 1 Canonical API and Typed Contracts.
Validates schemas, health check, canonical query endpoint, missing-context handling, and error behavior.
"""

from datetime import datetime, timezone
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.models.enums import (
    DataMode,
    GateCheckOutcome,
    OverallGateVerdict,
    PresentationMode,
    RecoveryActionType,
    RecoveryOutcome,
    RecoverySelectorType,
    RunStatus,
    StakeholderRole,
    TaskStatus,
)
from backend.models.evidence import EvidenceRecord, GeoLocation
from backend.models.query import (
    CanonicalQueryRequest,
    CanonicalQueryResponse,
    FieldCommunityProjection,
    MarineWarningItem,
    PolicyAudit,
    PolicyCheckItem,
    ProfessionalAnalysisProjection,
    QueryContext,
)
from backend.models.recovery import IdentifiedGap, RecoveryTraceEntry
from backend.models.task import TaskContract, TaskResult


@pytest.fixture
def client():
    return TestClient(app)


def test_health_check_endpoint(client):
    """Verify GET /health returns expected status and metadata without claiming marine safety."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "Sagarvani Reconstructed" in data["app"]
    assert "disclaimer" in data
    assert "Does not indicate operational live marine data feeds" in data["disclaimer"]


def test_enums_completeness():
    """Verify all explicit enums required by AGENTS.md and BUILD_PLAYBOOK.md exist."""
    assert OverallGateVerdict.PASS == "PASS"
    assert OverallGateVerdict.BLOCK == "BLOCK"
    assert OverallGateVerdict.NOT_EVALUABLE == "NOT_EVALUABLE"

    assert RunStatus.COMPLETED == "COMPLETED"
    assert RunStatus.PARTIAL == "PARTIAL"
    assert RunStatus.SOURCE_UNAVAILABLE == "SOURCE_UNAVAILABLE"
    assert RunStatus.INSUFFICIENT_EVIDENCE == "INSUFFICIENT_EVIDENCE"
    assert RunStatus.CLARIFICATION_REQUIRED == "CLARIFICATION_REQUIRED"

    assert DataMode.HISTORICAL_REPLAY == "HISTORICAL_REPLAY"
    assert DataMode.TEST_FIXTURE == "TEST_FIXTURE"
    assert DataMode.LIVE_FORECAST == "LIVE_FORECAST"

    assert StakeholderRole.FISHERMAN_COMMUNITY == "fisherman_community"
    assert len(list(StakeholderRole)) == 8


def test_evidence_record_strict_temporal_model():
    """Verify EvidenceRecord enforces separate temporal fields and geo validation."""
    now = datetime.now(timezone.utc)
    ev = EvidenceRecord(
        evidence_id="ev_001",
        source_id="open_meteo_marine",
        source_name="Open-Meteo Marine API",
        product_id="marine_forecast",
        parameter="wave_height",
        value=1.2,
        unit="m",
        location=GeoLocation(lat=13.35, lon=74.70, location_name="Malpe"),
        retrieved_at=now,
        valid_from=now,
        data_mode=DataMode.LIVE_FORECAST,
        source_url="https://open-meteo.com",
        attribution="Open-Meteo non-commercial terms",
    )
    assert ev.value == 1.2
    assert ev.location.lat == 13.35
    assert ev.observed_at is None  # Distinct from valid_from/retrieved_at


def test_query_missing_location_returns_clarification(client):
    """Verify that a request with no geographic coordinates returns CLARIFICATION_REQUIRED and NOT_EVALUABLE."""
    req_payload = {
        "query": "Can I leave port tomorrow at 5 AM?",
        "stakeholder_role": "fisherman_community",
        "presentation_mode": "field_community",
    }
    resp = client.post("/api/orca/query", json=req_payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["status"] == "CLARIFICATION_REQUIRED"
    assert data["data_mode"] == "NOT_AVAILABLE"
    assert data["policy_audit"]["overall_verdict"] == "NOT_EVALUABLE"
    assert len(data["gaps"]) == 1
    assert data["gaps"][0]["gap_code"] == "GAP_MISSING_LOCATION"
    assert len(data["evidence"]) == 0
    assert "PROTOTYPE ONLY" in data["disclaimer"]


@patch("backend.gateways.open_meteo_marine.OpenMeteoMarineGateway.fetch_marine_forecast")
@patch("backend.gateways.open_meteo_weather.OpenMeteoWeatherGateway.fetch_weather_forecast")
def test_query_with_location_context_gateway_unreachable(mock_weather, mock_marine, client):
    """Verify request with location context handles gateway unreachability truthfully without fabricating live data."""
    from backend.gateways.exceptions import GatewayTimeoutError
    mock_marine.side_effect = GatewayTimeoutError("Marine timeout", "Open-Meteo Marine API")
    mock_weather.side_effect = GatewayTimeoutError("Weather timeout", "Open-Meteo Weather API")

    req_payload = {
        "query": "Can I leave Malpe tomorrow at 5 AM?",
        "stakeholder_role": "fisherman_community",
        "presentation_mode": "field_community",
        "context_override": {
            "location": {
                "lat": 13.35,
                "lon": 74.70,
                "location_name": "Malpe Harbor"
            },
            "vessel_type": "motorized_craft",
            "operating_radius_km": 30.0,
            "language": "en"
        }
    }
    resp = client.post("/api/orca/query", json=req_payload)
    assert resp.status_code == 200
    data = resp.json()

    # Truthful unavailable status when upstream gateways fail
    assert data["status"] == "SOURCE_UNAVAILABLE"
    assert data["data_mode"] == "NOT_AVAILABLE"
    assert data["policy_audit"]["overall_verdict"] == "NOT_EVALUABLE"
    assert data["extracted_context"]["location"]["location_name"] == "Malpe Harbor"
    assert len(data["gaps"]) == 2
    assert data["field_view"]["headline"] == "Forecast Sources Unavailable"


def test_query_invalid_payload_validation_error(client):
    """Verify that empty/invalid query strings trigger HTTP 422 Unprocessable Entity."""
    # Query must be at least 2 characters
    resp = client.post("/api/orca/query", json={"query": ""})
    assert resp.status_code == 422

    # Invalid latitude (> 90.0)
    invalid_coord_payload = {
        "query": "Checking coordinates",
        "context_override": {
            "location": {
                "lat": 105.0,  # Invalid
                "lon": 74.70
            }
        }
    }
    resp = client.post("/api/orca/query", json=invalid_coord_payload)
    assert resp.status_code == 422


def test_task_contract_serialization():
    """Verify TaskContract and TaskResult serialization."""
    contract = TaskContract(
        task_id="task_001",
        task_name="Fetch Marine Forecast",
        gateway_id="open_meteo_marine",
        parameters={"lat": 13.35, "lon": 74.70}
    )
    assert contract.timeout_seconds == 10.0

    now = datetime.now(timezone.utc)
    res = TaskResult(
        task_id="task_001",
        status=TaskStatus.COMPLETED,
        started_at=now,
        completed_at=now,
        duration_ms=45.2,
        evidence_ids=["ev_001"]
    )
    assert res.status == TaskStatus.COMPLETED
    assert res.duration_ms == 45.2


def test_recovery_trace_entry():
    """Verify recovery trace entry models bounded cycle limit."""
    now = datetime.now(timezone.utc)
    entry = RecoveryTraceEntry(
        cycle=1,
        selector=RecoverySelectorType.DETERMINISTIC_RULES,
        action=RecoveryActionType.SWITCH_FALLBACK_PROVIDER,
        target_gap=IdentifiedGap(gap_code="GAP_TIMEOUT", description="Provider timed out"),
        parameters_applied={"fallback_provider": "local_mock"},
        outcome=RecoveryOutcome.SUCCEEDED,
        timestamp=now
    )
    assert entry.cycle == 1
    assert entry.action == RecoveryActionType.SWITCH_FALLBACK_PROVIDER
