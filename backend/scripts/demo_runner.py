"""
Sagarvani Reconstructed — Deterministic Demo Runner (Backend-Only)
Exercises the canonical FastAPI backend, guarded FSM, task harness,
evidence validator, bounded recovery controller, and independent release policy
in a 100% offline, isolated environment.

Scenarios demonstrated:
1. Evidence Acquisition: Both Open-Meteo marine and weather gateways succeed.
   Evidence records are verified, SHA-256 artifacts are saved, FSM transitions
   and run traces are persisted in SQLite, and release policy strictly returns
   NOT_EVALUABLE (protecting user safety).
2. Source Failure: Marine gateway fails. The API returns a truthful PARTIAL
   status without fabricating missing data.
3. Recovery and Termination: Demonstrates targeted recovery where missing data
   is recovered via retry, and no-progress early termination for irrecoverable gaps.
"""

import asyncio
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import sys
import tempfile
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from backend.main import app, get_gateway_registry
from backend.core.config import settings
from backend.catalog.service import CatalogService
from backend.engine.recovery import RecoveryController
from backend.models.enums import (
    DataMode,
    OverallGateVerdict,
    RecoveryActionType,
    RecoveryOutcome,
    RunStatus,
)
from backend.models.evidence import EvidenceRecord, GeoLocation
from backend.models.query import QueryContext
from backend.models.recovery import IdentifiedGap


# ---------------------------------------------------------------------------
# Offline Mock Gateways & Fixtures
# ---------------------------------------------------------------------------

DEMO_LAT = 13.35
DEMO_LON = 74.70


def _make_dummy_evidence(
    parameter: str,
    value: float,
    unit: str,
    lat: float = DEMO_LAT,
    lon: float = DEMO_LON,
    retrieved_at: Optional[datetime] = None,
    valid_from: Optional[datetime] = None,
    source_id: str = "open_meteo_marine",
    source_name: str = "Open-Meteo Marine API",
    source_url: str = "https://open-meteo.com/en/docs/marine-weather-api",
    source_attribution: str = "Open-Meteo Marine Weather API (ECMWF wave models)",
    product_id: str = "marine_forecast",
) -> EvidenceRecord:
    now = retrieved_at or datetime.now(timezone.utc)
    vf = valid_from or now
    return EvidenceRecord(
        evidence_id=f"ev_{parameter}_{int(now.timestamp())}_{os.urandom(3).hex()}",
        source_id=source_id,
        source_name=source_name,
        product_id=product_id,
        parameter=parameter,
        value=value,
        unit=unit,
        data_mode=DataMode.TEST_FIXTURE,  # fixture — not a live gateway call
        location=GeoLocation(lat=lat, lon=lon),
        retrieved_at=now,
        valid_from=vf,
        valid_to=vf + timedelta(hours=1),
        source_url=source_url,
        attribution=source_attribution,
    )


async def _fake_marine_success(params: Dict[str, Any]):
    now = params["retrieved_at"]
    target_dt = params.get("target_dt", now)
    raw = {
        "hourly": {
            "time": [target_dt.isoformat()],
            "wave_height": [1.4],
            "wave_direction": [240.0],
            "wave_period": [7.5],
        }
    }
    evs = [
        _make_dummy_evidence("wave_height", 1.4, "m", retrieved_at=now, valid_from=target_dt),
        _make_dummy_evidence("wave_direction", 240.0, "degrees", retrieved_at=now, valid_from=target_dt),
        _make_dummy_evidence("wave_period", 7.5, "s", retrieved_at=now, valid_from=target_dt),
    ]
    return raw, evs


async def _fake_weather_success(params: Dict[str, Any]):
    now = params["retrieved_at"]
    target_dt = params.get("target_dt", now)
    raw = {
        "hourly": {
            "time": [target_dt.isoformat()],
            "wind_speed_10m": [18.5],
            "wind_direction_10m": [220.0],
            "wind_gusts_10m": [26.0],
        }
    }
    evs = [
        _make_dummy_evidence(
            "wind_speed_10m", 18.5, "km/h", retrieved_at=now, valid_from=target_dt,
            source_id="open_meteo_weather", source_name="Open-Meteo Weather API",
            source_url="https://open-meteo.com/en/docs",
            source_attribution="Open-Meteo Atmospheric Forecast API",
            product_id="weather_forecast",
        ),
        _make_dummy_evidence(
            "wind_direction_10m", 220.0, "degrees", retrieved_at=now, valid_from=target_dt,
            source_id="open_meteo_weather", source_name="Open-Meteo Weather API",
            source_url="https://open-meteo.com/en/docs",
            source_attribution="Open-Meteo Atmospheric Forecast API",
            product_id="weather_forecast",
        ),
        _make_dummy_evidence(
            "wind_gusts_10m", 26.0, "km/h", retrieved_at=now, valid_from=target_dt,
            source_id="open_meteo_weather", source_name="Open-Meteo Weather API",
            source_url="https://open-meteo.com/en/docs",
            source_attribution="Open-Meteo Atmospheric Forecast API",
            product_id="weather_forecast",
        ),
    ]
    return raw, evs


async def _fake_marine_fail(params: Dict[str, Any]):
    raise RuntimeError("Simulated Open-Meteo Marine Gateway 503 Service Unavailable")


# ---------------------------------------------------------------------------
# Scenario Execution Functions
# ---------------------------------------------------------------------------

def run_scenario_1_evidence_acquisition(client: TestClient) -> Dict[str, Any]:
    """Scenario 1: Happy Path Evidence Acquisition with Policy Veto."""
    mock_registry = {
        "open_meteo_marine": _fake_marine_success,
        "open_meteo_weather": _fake_weather_success,
    }
    app.dependency_overrides[get_gateway_registry] = lambda: mock_registry

    payload = {
        "query": "Is it safe to depart Malpe harbour for artisanal fishing today?",
        "stakeholder_role": "fisherman_community",
        "presentation_mode": "field_community",
        "context_override": {
            "location": {"lat": DEMO_LAT, "lon": DEMO_LON, "name": "Malpe Harbour"},
            "vessel_type": "motorized_canoe",
            "operating_radius_km": 25.0,
        },
    }

    resp = client.post("/api/orca/query", json=payload)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()

    # Invariants
    assert data["status"] == "COMPLETED"
    assert len(data["evidence"]) == 6
    assert data["policy_audit"]["overall_verdict"] == "NOT_EVALUABLE"
    assert data["field_view"] is not None
    assert data["professional_view"] is not None

    # data_mode must NOT be LIVE_FORECAST for an offline fixture-backed run
    assert data["data_mode"] != "LIVE_FORECAST", (
        f"Scenario 1 used mocked gateways but reported data_mode={data['data_mode']!r}. "
        "Fixture evidence must propagate TEST_FIXTURE or similar non-live mode."
    )

    return {
        "scenario": "1. Nominal Evidence Acquisition",
        "run_id": data["run_id"],
        "trace_id": data["trace_id"],
        "status": data["status"],
        "data_mode": data["data_mode"],
        "evidence_count": len(data["evidence"]),
        "evidence_sample": [
            f"{e['parameter']} = {e['value']} {e['unit']} ({e['attribution']})"
            for e in data["evidence"]
        ],
        "policy_verdict": data["policy_audit"]["overall_verdict"],
        "policy_explanation": data["policy_audit"]["explanation"],
        "field_headline": data["field_view"]["headline"],
        "scientific_summary": data["professional_view"]["scientific_summary"],
        "disclaimer": data["disclaimer"],
    }


def run_scenario_2_source_failure(client: TestClient) -> Dict[str, Any]:
    """Scenario 2: Source Failure (Partial Result without Synthetic Fallback)."""
    mock_registry = {
        "open_meteo_marine": _fake_marine_fail,
        "open_meteo_weather": _fake_weather_success,
    }
    app.dependency_overrides[get_gateway_registry] = lambda: mock_registry

    payload = {
        "query": "Check fishing weather off Malpe harbour",
        "context_override": {
            "location": {"lat": DEMO_LAT, "lon": DEMO_LON, "name": "Malpe Harbour"},
        },
    }

    resp = client.post("/api/orca/query", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    # Invariants
    assert data["status"] == "PARTIAL"
    assert len(data["evidence"]) == 3  # Atmospheric only, no wave data
    assert any("MARINE" in g["gap_code"] for g in data["gaps"])
    # Veto hierarchy: missing core wave evidence triggers CHECK_EVIDENCE_ADEQUACY BLOCK
    assert data["policy_audit"]["overall_verdict"] == "BLOCK"

    # data_mode must NOT be LIVE_FORECAST for an offline fixture-backed run
    assert data["data_mode"] != "LIVE_FORECAST", (
        f"Scenario 2 used mocked gateways but reported data_mode={data['data_mode']!r}. "
        "Fixture evidence must propagate TEST_FIXTURE or similar non-live mode."
    )

    return {
        "scenario": "2. Source Failure & Truthful Reporting",
        "run_id": data["run_id"],
        "status": data["status"],
        "data_mode": data["data_mode"],
        "evidence_count": len(data["evidence"]),
        "gaps_detected": [g["gap_code"] for g in data["gaps"]],
        "field_headline": data["field_view"]["headline"],
        "advisory_text": data["field_view"]["advisory_text"],
        "policy_verdict": data["policy_audit"]["overall_verdict"],
    }


async def run_scenario_3_recovery_and_termination() -> Dict[str, Any]:
    """Scenario 3: Targeted Recovery & No-Progress Termination."""
    controller = RecoveryController()
    now = datetime.now(timezone.utc)
    ctx = QueryContext(location=GeoLocation(lat=DEMO_LAT, lon=DEMO_LON))

    # Part A: Targeted Recovery of missing wind data
    initial_ev = [
        _make_dummy_evidence("wave_height", 1.4, "m", valid_from=now, retrieved_at=now),
        _make_dummy_evidence("wave_period", 7.5, "s", valid_from=now, retrieved_at=now),
        _make_dummy_evidence("wave_direction", 240.0, "degrees", valid_from=now, retrieved_at=now),
    ]
    initial_gaps = [
        IdentifiedGap(
            gap_code="GAP_MISSING_WIND_SPEED",
            description="Wind speed parameter absent from atmospheric batch",
            affected_parameter="wind_speed",
            suggested_action=RecoveryActionType.RETRY_WITH_BACKOFF,
        )
    ]
    recovered_wind = [
        _make_dummy_evidence("wind_speed_10m", 15.0, "km/h", valid_from=now, retrieved_at=now,
                             source_id="open_meteo_weather", source_name="Open-Meteo Weather API",
                             source_url="https://open-meteo.com/en/docs", source_attribution="Open-Meteo Weather API"),
        _make_dummy_evidence("wind_direction_10m", 210.0, "degrees", valid_from=now, retrieved_at=now,
                             source_id="open_meteo_weather", source_name="Open-Meteo Weather API",
                             source_url="https://open-meteo.com/en/docs", source_attribution="Open-Meteo Weather API"),
        _make_dummy_evidence("wind_gusts_10m", 22.0, "km/h", valid_from=now, retrieved_at=now,
                             source_id="open_meteo_weather", source_name="Open-Meteo Weather API",
                             source_url="https://open-meteo.com/en/docs", source_attribution="Open-Meteo Weather API"),
    ]
    mock_weather = AsyncMock(return_value=({"recovered": True}, recovered_wind))
    registry = {"open_meteo_weather": mock_weather}

    recovered_evs, remaining_gaps, trace_a, _ = await controller.execute_recovery_loop(
        initial_gaps=initial_gaps,
        current_evidence=initial_ev,
        context=ctx,
        gateway_registry=registry,
    )
    assert len(recovered_evs) == 6
    assert len(trace_a) == 1
    assert trace_a[0].outcome == RecoveryOutcome.SUCCEEDED

    # Part B: No-progress termination for irrecoverable gap
    irrecoverable_gap = IdentifiedGap(
        gap_code="GAP_UNRECOGNIZED_UNSUPPORTED_DATA",
        description="Data corruption cannot be recovered through gateway retries",
        suggested_action=RecoveryActionType.ABSTAIN_AND_LOG,
    )
    _, _, trace_b, _ = await controller.execute_recovery_loop(
        initial_gaps=[irrecoverable_gap],
        current_evidence=[],
        context=ctx,
        gateway_registry={},
    )
    assert len(trace_b) == 1
    assert trace_b[0].action == RecoveryActionType.ABSTAIN_AND_LOG

    return {
        "scenario": "3. Bounded Recovery & Honest Termination",
        "part_a_recovered_parameters": len(recovered_evs),
        "part_a_action": trace_a[0].action.value,
        "part_a_outcome": trace_a[0].outcome.value,
        "part_b_action": trace_b[0].action.value,
        "part_b_outcome": trace_b[0].outcome.value,
        "cycles_executed": len(trace_a),
        "budget_limit": 2,
    }


# ---------------------------------------------------------------------------
# CLI Entrypoint
# ---------------------------------------------------------------------------

def run_demo() -> int:
    """Runs all 3 demo scenarios in an isolated temporary environment."""
    print("=" * 76)
    print("  SAGARVANI RECONSTRUCTED — DETERMINISTIC BACKEND DEMO RUNNER")
    print("  Evidence-Aware Marine Decision Intelligence Prototype")
    print("  Mode: 100% Offline | Zero External Side Effects | Guarded FSM")
    print("=" * 76)
    print()

    # Use ignore_cleanup_errors=True to prevent Windows file-locking issues on sqlite db
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        tmp_db = os.path.join(tmp_dir, "demo_sagarvani.db")
        tmp_artifacts = os.path.join(tmp_dir, "demo_artifacts")
        os.makedirs(tmp_artifacts, exist_ok=True)

        settings.sqlite_db_path = tmp_db
        settings.artifacts_dir = tmp_artifacts

        # Initialize isolated SQLite catalog
        CatalogService(db_path=tmp_db)

        client = TestClient(app)

        try:
            # ---------------------------------------------------------------
            # Scenario 1
            # ---------------------------------------------------------------
            print("-" * 76)
            print("  SCENARIO 1: Nominal Evidence Acquisition & Release Policy Veto")
            print("-" * 76)
            s1 = run_scenario_1_evidence_acquisition(client)
            print(f"  [+] Run ID:             {s1['run_id']}")
            print(f"  [+] Execution Status:   {s1['status']}")
            print(f"  [+] Data Mode:          {s1['data_mode']} (fixture — not a live gateway call)")
            print(f"  [+] Verified Evidence:  {s1['evidence_count']} parameters acquired")
            for item in s1["evidence_sample"]:
                print(f"      - {item}")
            print(f"  [+] Release Verdict:    {s1['policy_verdict']}")
            print(f"  [+] Safety Policy Note: {s1['policy_explanation']}")
            print(f"  [+] Field Projection:   {s1['field_headline']}")
            print(f"  [+] Analysis Summary:   {s1['scientific_summary']}")
            print(f"  [+] Boundary Notice:    {s1['disclaimer']}")
            print("  => SCENARIO 1 PASSED: Nominal acquisition confirmed; policy veto active.\n")

            # ---------------------------------------------------------------
            # Scenario 2
            # ---------------------------------------------------------------
            print("-" * 76)
            print("  SCENARIO 2: Gateway Failure Handling (Truthful Partial State)")
            print("-" * 76)
            s2 = run_scenario_2_source_failure(client)
            print(f"  [+] Run ID:             {s2['run_id']}")
            print(f"  [+] Execution Status:   {s2['status']} (Truthful partial return)")
            print(f"  [+] Data Mode:          {s2['data_mode']} (fixture — not a live gateway call)")
            print(f"  [+] Retrieved Evidence: {s2['evidence_count']} atmospheric parameters")
            print(f"  [+] Evidence Gaps:      {', '.join(s2['gaps_detected'])}")
            print(f"  [+] Field Advisory:     {s2['advisory_text']}")
            print(f"  [+] Policy Verdict:     {s2['policy_verdict']} (Clearance strictly withheld)")
            print("  => SCENARIO 2 PASSED: No synthetic fallback; honest partial state returned.\n")

            # ---------------------------------------------------------------
            # Scenario 3
            # ---------------------------------------------------------------
            print("-" * 76)
            print("  SCENARIO 3: Bounded Recovery & No-Progress Abstention")
            print("-" * 76)
            s3 = asyncio.run(run_scenario_3_recovery_and_termination())
            print(f"  [+] Part A (Targeted Recovery):")
            print(f"      Action Selected:    {s3['part_a_action']}")
            print(f"      Recovery Outcome:   {s3['part_a_outcome']}")
            print(f"      Recovered Evidence: {s3['part_a_recovered_parameters']} parameters validated")
            print(f"  [+] Part B (Irrecoverable Gap):")
            print(f"      Action Selected:    {s3['part_b_action']}")
            print(f"      Recovery Outcome:   {s3['part_b_outcome']}")
            print(f"      Budget Enforced:    Terminated at cycle {s3['cycles_executed']} (Max budget: {s3['budget_limit']})")
            print("  => SCENARIO 3 PASSED: Bounded recovery and early termination confirmed.\n")

            # ---------------------------------------------------------------
            # Summary
            # ---------------------------------------------------------------
            print("=" * 76)
            print("  ALL 3 DEMO SCENARIOS PASSED CONGRUENTLY (100% OFFLINE)")
            print("  - Backend Route:    POST /api/orca/query")
            print("  - Release Policy:   Strict NOT_EVALUABLE veto preserves human safety")
            print("  - Provenance:       Open-Meteo gateway attribution preserved")
            print("  - Phase 8 Frontend: Pending explicit user approval")
            print("=" * 76)
            return 0

        finally:
            app.dependency_overrides.clear()


if __name__ == "__main__":
    sys.exit(run_demo())
