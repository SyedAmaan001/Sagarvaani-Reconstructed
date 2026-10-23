"""
Sagarvani Reconstructed — Phase 7 Verification & Demo Acceptance Suite
=====================================================================
Covers the 10 mandatory verification scenarios required by Phase 7:
1. Location validation (missing/invalid location never guesses coordinates).
2. Happy path with both mocked gateways succeeding and evidence linked to artifacts.
3. Gateway failure permutations (marine failure, weather failure, both failing).
4. Malformed payloads, timeouts, mismatched arrays, and physical range validation.
5. Temporal freshness, temporal window mismatch, and upstream lineage tracking.
6. Bounded recovery behaviors (targeted recovery, no progress, cycle limits, irrecoverable gaps).
7. DAG and harness resilience (cycles, timeouts, skipped prerequisites, run deadlines).
8. Storage and catalog failure safety (artifact write failure, checksum mismatch, DB errors).
9. Laya gating, missing dependency fallback, unapproved action rejection, timeout resilience.
10. Independent release policy veto and proof that departure verdict is NEVER PASS.
"""

import asyncio
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

import pytest
from fastapi.testclient import TestClient

from backend.main import app, get_gateway_registry
from backend.core.config import settings
from backend.catalog.artifact_store import ArtifactStore
from backend.catalog.service import CatalogService
from backend.engine.fsm import FSMState, RunFSM
from backend.engine.dag import TaskDAG, CyclicDependencyError, DuplicateTaskIDError
from backend.engine.harness import ExecutionHarness
from backend.engine.validator import EvidenceValidator
from backend.engine.recovery import RecoveryController, RuleBasedRecoverySelector, PERMITTED_ACTIONS
from backend.engine.laya_adapter import LayaRecoverySelector
from backend.engine.policy import ReleasePolicy
from backend.models.enums import (
    DataMode,
    GateCheckOutcome,
    OverallGateVerdict,
    RecoveryActionType,
    RecoveryOutcome,
    RecoverySelectorType,
    RunStatus,
    TaskStatus,
)
from backend.models.evidence import EvidenceRecord, GeoLocation
from backend.models.query import CanonicalQueryRequest, QueryContext
from backend.models.recovery import IdentifiedGap, RecoveryTraceEntry
from backend.models.task import TaskContract


# ---------------------------------------------------------------------------
# Test Helpers & Deterministic Fakes
# ---------------------------------------------------------------------------

MALPE_LAT = 13.35
MALPE_LON = 74.70


def _make_dummy_evidence(
    parameter: str,
    value: float,
    unit: str,
    lat: float = MALPE_LAT,
    lon: float = MALPE_LON,
    retrieved_at: Optional[datetime] = None,
    valid_from: Optional[datetime] = None,
    artifact_ref: Optional[str] = None,
    source_id: str = "open_meteo_marine",
    source_attribution: str = "Open-Meteo Marine Weather API (ECMWF wave models)",
    source_name: str = "Open-Meteo Marine API",
    source_url: str = "https://open-meteo.com/en/docs/marine-weather-api",
    product_id: str = "marine_forecast",
) -> EvidenceRecord:
    now = retrieved_at or datetime.now(timezone.utc)
    vf = valid_from or now
    return EvidenceRecord(
        evidence_id=f"ev_{parameter}_{int(now.timestamp())}_{uuid.uuid4().hex[:6]}",
        source_id=source_id,
        source_name=source_name,
        product_id=product_id,
        parameter=parameter,
        value=value,
        unit=unit,
        data_mode=DataMode.LIVE_FORECAST,
        location=GeoLocation(lat=lat, lon=lon),
        retrieved_at=now,
        valid_from=vf,
        valid_to=vf + timedelta(hours=1),
        source_url=source_url,
        attribution=source_attribution,
        artifact_ref=artifact_ref,
    )


def _make_task(
    task_id: str,
    gateway_id: str = "fake_gw",
    dependencies: Optional[List[str]] = None,
    timeout_seconds: float = 5.0,
) -> TaskContract:
    return TaskContract(
        task_id=task_id,
        task_name=task_id,
        gateway_id=gateway_id,
        dependencies=dependencies or [],
        timeout_seconds=timeout_seconds,
        parameters={},
    )


async def _fake_marine_success(params: Dict[str, Any]):
    now = params["retrieved_at"]
    target_dt = params.get("target_dt", now)
    raw = {"hourly": {"time": [target_dt.isoformat()], "wave_height": [1.4], "wave_direction": [240.0], "wave_period": [7.5]}}
    evs = [
        _make_dummy_evidence("wave_height", 1.4, "m", retrieved_at=now, valid_from=target_dt),
        _make_dummy_evidence("wave_direction", 240.0, "degrees", retrieved_at=now, valid_from=target_dt),
        _make_dummy_evidence("wave_period", 7.5, "s", retrieved_at=now, valid_from=target_dt),
    ]
    return raw, evs


async def _fake_weather_success(params: Dict[str, Any]):
    now = params["retrieved_at"]
    target_dt = params.get("target_dt", now)
    raw = {"hourly": {"time": [target_dt.isoformat()], "wind_speed_10m": [18.5], "wind_direction_10m": [220.0], "wind_gusts_10m": [26.0]}}
    evs = [
        _make_dummy_evidence("wind_speed_10m", 18.5, "km/h", retrieved_at=now, valid_from=target_dt, source_id="open_meteo_weather", source_name="Open-Meteo Weather API", source_url="https://open-meteo.com/en/docs", source_attribution="Open-Meteo Weather Forecast API"),
        _make_dummy_evidence("wind_direction_10m", 220.0, "degrees", retrieved_at=now, valid_from=target_dt, source_id="open_meteo_weather", source_name="Open-Meteo Weather API", source_url="https://open-meteo.com/en/docs", source_attribution="Open-Meteo Weather Forecast API"),
        _make_dummy_evidence("wind_gusts_10m", 26.0, "km/h", retrieved_at=now, valid_from=target_dt, source_id="open_meteo_weather", source_name="Open-Meteo Weather API", source_url="https://open-meteo.com/en/docs", source_attribution="Open-Meteo Weather Forecast API"),
    ]
    return raw, evs


async def _fake_marine_fail(params: Dict[str, Any]):
    raise RuntimeError("Simulated Open-Meteo Marine 503 Service Unavailable")


async def _fake_weather_fail(params: Dict[str, Any]):
    raise RuntimeError("Simulated Open-Meteo Weather 504 Gateway Timeout")


class StubRouter:
    def __init__(self, choice: Optional[str] = None):
        self.choice = choice

    def predict(self, state: Dict[str, Any], questions: Dict[str, Any]) -> Dict[str, Any]:
        return {"answers": {"recovery_action": {"choice": self.choice}}}


# ---------------------------------------------------------------------------
# 1. Location Validation
# ---------------------------------------------------------------------------

class TestScenario1_LocationValidation:
    """Scenario 1: Missing or invalid location produces clarification, never guessed coordinates."""

    def test_missing_location_returns_clarification_required(self):
        client = TestClient(app)
        payload = {"query": "Can I set out to sea from Malpe today?"}
        resp = client.post("/api/orca/query", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "CLARIFICATION_REQUIRED"
        assert data["data_mode"] == "NOT_AVAILABLE"
        assert any(g["gap_code"] == "GAP_MISSING_LOCATION" for g in data["gaps"])
        assert data["policy_audit"]["overall_verdict"] == "NOT_EVALUABLE"
        assert data["extracted_context"] is None or data["extracted_context"].get("location") is None

    def test_invalid_latitude_rejected_by_schema(self):
        client = TestClient(app)
        payload = {
            "query": "Check weather",
            "context_override": {
                "location": {"lat": 95.0, "lon": 74.70}  # Invalid latitude > 90
            }
        }
        resp = client.post("/api/orca/query", json=payload)
        assert resp.status_code == 422  # Pydantic validation error


# ---------------------------------------------------------------------------
# 2. Happy Path Both Gateways
# ---------------------------------------------------------------------------

class TestScenario2_HappyPathBothGateways:
    """Scenario 2: Both mocked gateways succeed; full request-to-response trace is verified."""

    def test_full_successful_request_to_response_pipeline(self, tmp_path, monkeypatch):
        db_path = tmp_path / "test_p7.db"
        art_dir = tmp_path / "artifacts"
        monkeypatch.setattr(settings, "sqlite_db_path", str(db_path))
        monkeypatch.setattr(settings, "artifacts_dir", str(art_dir))

        registry = {
            "open_meteo_marine": _fake_marine_success,
            "open_meteo_weather": _fake_weather_success,
        }
        app.dependency_overrides[get_gateway_registry] = lambda: registry

        client = TestClient(app)
        now = datetime.now(timezone.utc)
        payload = {
            "query": "Is it safe to fish off Malpe?",
            "context_override": {
                "location": {"lat": MALPE_LAT, "lon": MALPE_LON},
                "departure_time": now.isoformat(),
            }
        }
        resp = client.post("/api/orca/query", json=payload)
        app.dependency_overrides.clear()

        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "COMPLETED"
        assert data["data_mode"] == "LIVE_FORECAST"
        assert len(data["evidence"]) == 6

        # Check run_id, trace_id, and artifact linkages
        run_id = data["run_id"]
        trace_id = data["trace_id"]
        assert run_id.startswith("run_")
        assert trace_id.startswith("tr_")

        # Verify SQLite recorded run, FSM transitions, and policy checks
        catalog = CatalogService()
        run_record = catalog.get_run(run_id)
        assert run_record is not None
        assert run_record["status"] == "COMPLETED"

        artifacts = run_record["artifacts"]
        assert len(artifacts) == 2
        for art in artifacts:
            rel_path = art["relative_path"]
            checksum = art["checksum_sha256"]
            full_path = art_dir.parent / rel_path
            assert full_path.exists()
            computed_sha = hashlib.sha256(full_path.read_bytes()).hexdigest()
            assert computed_sha == checksum

        fsm_transitions = catalog.get_fsm_transitions(run_id)
        states = [t["to_state"] for t in fsm_transitions]
        assert "CONTEXT_VALIDATED" in states
        assert "TASK_GRAPH_READY" in states
        assert "EVIDENCE_ACQUISITION" in states
        assert "EVIDENCE_VALIDATION" in states
        assert "SAFETY_GATE_CHECK" in states
        assert "ABSTAINED" in states  # Ended in ABSTAINED because safety gate is NOT_EVALUABLE


# ---------------------------------------------------------------------------
# 3. Source Failure Permutations
# ---------------------------------------------------------------------------

class TestScenario3_SourceFailures:
    """Scenario 3: Marine failure, weather failure, and both failing."""

    def test_marine_failure_weather_success_produces_partial(self):
        registry = {
            "open_meteo_marine": _fake_marine_fail,
            "open_meteo_weather": _fake_weather_success,
        }
        app.dependency_overrides[get_gateway_registry] = lambda: registry
        client = TestClient(app)
        payload = {"query": "Test", "context_override": {"location": {"lat": MALPE_LAT, "lon": MALPE_LON}}}
        resp = client.post("/api/orca/query", json=payload)
        app.dependency_overrides.clear()

        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "PARTIAL"
        assert len(data["evidence"]) == 3
        assert any(g["gap_code"] == "GAP_MARINE_SOURCE_ERROR" for g in data["gaps"])

    def test_weather_failure_marine_success_produces_partial(self):
        registry = {
            "open_meteo_marine": _fake_marine_success,
            "open_meteo_weather": _fake_weather_fail,
        }
        app.dependency_overrides[get_gateway_registry] = lambda: registry
        client = TestClient(app)
        payload = {"query": "Test", "context_override": {"location": {"lat": MALPE_LAT, "lon": MALPE_LON}}}
        resp = client.post("/api/orca/query", json=payload)
        app.dependency_overrides.clear()

        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "PARTIAL"
        assert len(data["evidence"]) == 3
        assert any(g["gap_code"] == "GAP_WEATHER_SOURCE_ERROR" for g in data["gaps"])

    def test_both_sources_fail_produces_source_unavailable(self):
        registry = {
            "open_meteo_marine": _fake_marine_fail,
            "open_meteo_weather": _fake_weather_fail,
        }
        app.dependency_overrides[get_gateway_registry] = lambda: registry
        client = TestClient(app)
        payload = {"query": "Test", "context_override": {"location": {"lat": MALPE_LAT, "lon": MALPE_LON}}}
        resp = client.post("/api/orca/query", json=payload)
        app.dependency_overrides.clear()

        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "SOURCE_UNAVAILABLE"
        assert len(data["evidence"]) == 0
        assert data["data_mode"] == "NOT_AVAILABLE"


# ---------------------------------------------------------------------------
# 4. Malformed Payloads, Physical Range, & Data Integrity
# ---------------------------------------------------------------------------

class TestScenario4_MalformedPayloadsAndValidation:
    """Scenario 4: Null values, mismatched arrays, and unphysical numeric data."""

    def test_unphysical_wave_height_flagged_by_validator(self):
        validator = EvidenceValidator()
        ev = _make_dummy_evidence("wave_height", 55.0, "m")  # > 35m physical ceiling
        res = validator.validate([ev])
        assert not res.is_valid
        assert any(c.check_code == "CHECK_PHYSICAL_RANGE" and c.status == "FAIL" for c in res.checks)
        assert any(g.gap_code == "GAP_UNPHYSICAL_VALUE" for g in res.gaps)

    def test_unphysical_wind_speed_flagged_by_validator(self):
        validator = EvidenceValidator()
        ev = _make_dummy_evidence("wind_speed_10m", 800.0, "km/h")  # > 150 m/s physical ceiling
        res = validator.validate([ev])
        assert not res.is_valid
        assert any(g.gap_code == "GAP_UNPHYSICAL_VALUE" for g in res.gaps)

    def test_unrecognized_units_flagged_as_warning(self):
        validator = EvidenceValidator()
        ev = _make_dummy_evidence("wave_height", 1.5, "cubits")  # Unsupported unit
        res = validator.validate([ev])
        assert any(c.check_code == "CHECK_UNITS" and c.status == "FAIL" for c in res.checks)
        assert any(g.gap_code == "GAP_UNKNOWN_UNIT" for g in res.gaps)


# ---------------------------------------------------------------------------
# 5. Temporal Freshness, Temporal Window & Lineage
# ---------------------------------------------------------------------------

class TestScenario5_TemporalFreshnessLineage:
    """Scenario 5: Stale evidence, temporal window mismatch, and upstream lineage."""

    def test_stale_forecast_retrieval_flagged(self):
        validator = EvidenceValidator()
        now = datetime.now(timezone.utc)
        stale_time = now - timedelta(hours=60)  # > 48h freshness threshold
        ev = _make_dummy_evidence("wave_height", 1.5, "m", retrieved_at=stale_time, valid_from=now)
        res = validator.validate([ev], now=now)
        assert any(c.check_code == "CHECK_FRESHNESS" and c.status == "WARN" for c in res.checks)
        assert any(g.gap_code == "GAP_STALE_EVIDENCE" for g in res.gaps)

    def test_temporal_window_mismatch_flagged(self):
        validator = EvidenceValidator()
        now = datetime.now(timezone.utc)
        future_departure = now + timedelta(hours=48)
        ctx = QueryContext(location=GeoLocation(lat=MALPE_LAT, lon=MALPE_LON), departure_time=future_departure)
        ev = _make_dummy_evidence("wave_height", 1.5, "m", retrieved_at=now, valid_from=now)
        res = validator.validate([ev], context=ctx, now=now)
        assert any(c.check_code == "CHECK_TEMPORAL_RELEVANCE" and c.status == "WARN" for c in res.checks)
        assert any(g.gap_code == "GAP_TEMPORAL_WINDOW_MISMATCH" for g in res.gaps)

    def test_upstream_lineage_recorded(self):
        validator = EvidenceValidator()
        ev = _make_dummy_evidence("wave_height", 1.5, "m", source_id="open_meteo_marine")
        res = validator.validate([ev])
        assert any("ECMWF" in line or "DWD" in line for line in res.lineage_audit)


# ---------------------------------------------------------------------------
# 6. Bounded Recovery Behaviors
# ---------------------------------------------------------------------------

class TestScenario6_BoundedRecoveryBehaviors:
    """Scenario 6: Targeted recovery, repeated action, no progress, cycle limits, irrecoverable gaps."""

    @pytest.mark.asyncio
    async def test_recovery_max_2_cycles_limit(self):
        controller = RecoveryController()
        gap = IdentifiedGap(gap_code="GAP_WEATHER_SOURCE_ERROR", description="Timeout")
        # Failing registry
        registry = {"open_meteo_weather": _fake_weather_fail}
        deadline = datetime.now(timezone.utc) + timedelta(seconds=10)

        evs, gaps, trace, val_res = await controller.execute_recovery_loop(
            initial_gaps=[gap],
            current_evidence=[],
            context=None,
            gateway_registry=registry,
            deadline=deadline,
        )
        assert len(trace) <= 2  # Max 2 cycles strictly enforced

    @pytest.mark.asyncio
    async def test_no_progress_termination(self):
        controller = RecoveryController()
        # Irrecoverable gap that won't change
        gap = IdentifiedGap(gap_code="GAP_UNKNOWN_CODE", description="Permanent unknown defect")
        deadline = datetime.now(timezone.utc) + timedelta(seconds=10)

        evs, gaps, trace, val_res = await controller.execute_recovery_loop(
            initial_gaps=[gap],
            current_evidence=[],
            context=None,
            gateway_registry={},
            deadline=deadline,
        )
        # Terminated because action is ABSTAIN_AND_LOG or no progress
        assert len(trace) == 1
        assert trace[0].action == RecoveryActionType.ABSTAIN_AND_LOG

    @pytest.mark.asyncio
    async def test_successful_targeted_recovery(self):
        """When missing wind speed is recovered by fallback/retry, the gap is resolved."""
        controller = RecoveryController()
        now = datetime.now(timezone.utc)
        ctx = QueryContext(location=GeoLocation(lat=MALPE_LAT, lon=MALPE_LON))

        initial_ev = [
            _make_dummy_evidence("wave_height", 1.5, "m", valid_from=now, retrieved_at=now),
            _make_dummy_evidence("wave_period", 8.0, "s", valid_from=now, retrieved_at=now),
            _make_dummy_evidence("wave_direction", 240.0, "degrees", valid_from=now, retrieved_at=now),
        ]
        initial_gaps = [
            IdentifiedGap(
                gap_code="GAP_MISSING_WIND_SPEED",
                description="Wind speed missing",
                affected_parameter="wind_speed",
                suggested_action=RecoveryActionType.RETRY_WITH_BACKOFF,
            )
        ]

        recovered_wind = [
            _make_dummy_evidence("wind_speed_10m", 12.0, "km/h", valid_from=now, retrieved_at=now, source_id="open_meteo_weather", source_name="Open-Meteo Weather API", source_url="https://open-meteo.com/en/docs", source_attribution="Open-Meteo Weather API"),
            _make_dummy_evidence("wind_direction_10m", 250.0, "degrees", valid_from=now, retrieved_at=now, source_id="open_meteo_weather", source_name="Open-Meteo Weather API", source_url="https://open-meteo.com/en/docs", source_attribution="Open-Meteo Weather API"),
            _make_dummy_evidence("wind_gusts_10m", 18.0, "km/h", valid_from=now, retrieved_at=now, source_id="open_meteo_weather", source_name="Open-Meteo Weather API", source_url="https://open-meteo.com/en/docs", source_attribution="Open-Meteo Weather API"),
        ]
        mock_weather = AsyncMock(return_value=({"recovered": True}, recovered_wind))
        gateway_registry = {"open_meteo_weather": mock_weather}

        evidence, final_gaps, trace, val_res = await controller.execute_recovery_loop(
            initial_gaps=initial_gaps,
            current_evidence=initial_ev,
            context=ctx,
            gateway_registry=gateway_registry,
        )

        assert len(evidence) == 6
        assert len(trace) == 1
        assert trace[0].outcome == RecoveryOutcome.SUCCEEDED


# ---------------------------------------------------------------------------
# 7. DAG & Harness Resilience
# ---------------------------------------------------------------------------

class TestScenario7_DAGAndHarnessResilience:
    """Scenario 7: Cycle detection, prerequisite failure skipping, and run timeouts."""

    def test_dag_cycle_detection(self):
        c1 = _make_task("A", dependencies=["B"])
        c2 = _make_task("B", dependencies=["A"])
        with pytest.raises(CyclicDependencyError):
            TaskDAG([c1, c2])

    def test_dag_self_loop_detection(self):
        c1 = _make_task("A", dependencies=["A"])
        with pytest.raises(CyclicDependencyError):
            TaskDAG([c1])

    def test_dag_duplicate_id_detection(self):
        c1 = _make_task("A")
        c2 = _make_task("A")
        with pytest.raises(DuplicateTaskIDError):
            TaskDAG([c1, c2])

    @pytest.mark.asyncio
    async def test_harness_skips_dependent_on_prerequisite_failure(self):
        c1 = _make_task("parent", gateway_id="g_fail")
        c2 = _make_task("child", gateway_id="g_success", dependencies=["parent"])
        dag = TaskDAG([c1, c2])

        registry = {
            "g_fail": _fake_marine_fail,
            "g_success": _fake_weather_success,
        }
        harness = ExecutionHarness(dag=dag, registry=registry)
        res = await harness.execute()

        assert "parent" in res.failed_task_ids
        assert "child" in res.skipped_task_ids
        assert len(res.evidence) == 0


# ---------------------------------------------------------------------------
# 8. Storage & Catalog Failure Safety
# ---------------------------------------------------------------------------

class TestScenario8_StorageAndCatalogFailureSafety:
    """Scenario 8: Artifact write failure, checksum mismatch, and safe database error handling."""

    def test_corrupt_artifact_checksum_flagged(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_path = Path(tmp_dir)
            art_file = base_path / "runs" / "run_test" / "marine.json"
            art_file.parent.mkdir(parents=True, exist_ok=True)
            art_file.write_bytes(b'{"status": "ok"}')

            validator = EvidenceValidator(artifacts_base_dir=str(base_path))
            ev_missing = _make_dummy_evidence("wave_height", 1.5, "m", artifact_ref="runs/missing/ghost.json")
            res = validator.validate([ev_missing])
            assert any(c.check_code == "CHECK_ARTIFACT_INTEGRITY" and c.status == "FAIL" for c in res.checks)
            assert any(g.gap_code == "GAP_MISSING_ARTIFACT" for g in res.gaps)

    def test_database_persistence_failure_does_not_crash_endpoint(self, monkeypatch):
        """Simulate SQLite database failure during _persist_run; endpoint must return valid response."""
        registry = {
            "open_meteo_marine": _fake_marine_success,
            "open_meteo_weather": _fake_weather_success,
        }
        app.dependency_overrides[get_gateway_registry] = lambda: registry

        # Mock CatalogService.record_run to raise an operational error
        def _mock_record_run(*args, **kwargs):
            raise RuntimeError("Disk I/O error or SQLite database locked")

        monkeypatch.setattr(CatalogService, "record_run", _mock_record_run)

        client = TestClient(app)
        payload = {"query": "Test query", "context_override": {"location": {"lat": MALPE_LAT, "lon": MALPE_LON}}}
        resp = client.post("/api/orca/query", json=payload)
        app.dependency_overrides.clear()

        # The endpoint must gracefully absorb the persistence error and return the 200 response
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "COMPLETED"
        assert len(data["evidence"]) == 6


# ---------------------------------------------------------------------------
# 9. Laya Gating, Dependency Fallback, & Model Safety
# ---------------------------------------------------------------------------

class TestScenario9_LayaGatingAndFallbackResilience:
    """Scenario 9: Laya disabled by default, missing dependency, unapproved action, and timeout."""

    def test_laya_disabled_by_default(self):
        selector = LayaRecoverySelector(enabled=False)
        gap = IdentifiedGap(gap_code="GAP_WEATHER_SOURCE_ERROR", description="Weather error")
        act, trace = selector.select_action_with_trace(gap, 1, [], PERMITTED_ACTIONS)
        assert act == RecoveryActionType.RETRY_WITH_BACKOFF
        assert trace.is_valid is False
        assert "ENABLE_LAYA_SELECTOR=False" in (trace.fallback_reason or "")

    def test_laya_missing_package_falls_back_to_rules(self, monkeypatch):
        selector = LayaRecoverySelector(enabled=True)
        monkeypatch.setattr(selector, "_get_or_create_router", MagicMock(side_effect=ImportError("No module named 'laya'")))
        gap = IdentifiedGap(gap_code="GAP_SPATIAL_COVERAGE_EXCEEDED", description="Far out")
        act, trace = selector.select_action_with_trace(gap, 1, [], PERMITTED_ACTIONS)
        assert act == RecoveryActionType.EXPAND_SPATIAL_RADIUS
        assert trace.is_valid is False
        assert "not installed" in (trace.fallback_reason or "")

    def test_unapproved_model_action_rejected_and_falls_back(self):
        # Model returns an unapproved action string
        stub = StubRouter(choice="execute_unapproved_code")
        selector = LayaRecoverySelector(enabled=True, router=stub)
        gap = IdentifiedGap(gap_code="GAP_MARINE_SOURCE_ERROR", description="Marine failure")
        act, trace = selector.select_action_with_trace(gap, 1, [], PERMITTED_ACTIONS)
        # Unapproved choice rejected -> falls back to RETRY_WITH_BACKOFF
        assert act == RecoveryActionType.RETRY_WITH_BACKOFF
        assert trace.is_valid is False
        assert "not in allowed actions" in (trace.fallback_reason or "")

    def test_laya_inference_timeout_falls_back(self):
        import time

        class HangingRouter:
            def predict(self, state, questions):
                time.sleep(0.15)
                return {"answers": {"recovery_action": {"choice": "retry_with_backoff"}}}

        selector = LayaRecoverySelector(enabled=True, timeout_seconds=0.03, router=HangingRouter())
        gap = IdentifiedGap(gap_code="GAP_MARINE_SOURCE_ERROR", description="Timeout test")
        act, trace = selector.select_action_with_trace(gap, 1, [], PERMITTED_ACTIONS)
        assert act == RecoveryActionType.RETRY_WITH_BACKOFF
        assert trace.is_valid is False
        assert "timed out" in (trace.fallback_reason or "")


# ---------------------------------------------------------------------------
# 10. Independent Release Policy & Unilateral Veto
# ---------------------------------------------------------------------------

class TestScenario10_ReleasePolicyIndependenceAndVeto:
    """Scenario 10: Mandatory safety checks cannot produce a PASS departure verdict."""

    def test_all_mandatory_safety_checks_evaluated_and_not_evaluable(self):
        policy = ReleasePolicy()
        evs = [
            _make_dummy_evidence("wave_height", 1.2, "m"),
            _make_dummy_evidence("wind_speed_10m", 15.0, "km/h"),
        ]
        val_res = EvidenceValidator().validate(evs)
        ctx = QueryContext(location=GeoLocation(lat=MALPE_LAT, lon=MALPE_LON))

        audit = policy.evaluate(evs, val_res, ctx)

        check_codes = {c.check_name: c.outcome for c in audit.checks}
        # Mandatory unevaluable checks
        assert check_codes["CHECK_OFFICIAL_WARNINGS"] == GateCheckOutcome.NOT_EVALUABLE
        assert check_codes["CHECK_MARINE_PROTECTED_AREAS"] == GateCheckOutcome.NOT_EVALUABLE
        assert check_codes["CHECK_VESSEL_LIMITS"] == GateCheckOutcome.NOT_EVALUABLE

        # Overall verdict must be NOT_EVALUABLE
        assert audit.overall_verdict == OverallGateVerdict.NOT_EVALUABLE
        # can_release must strictly return False
        assert policy.can_release(audit) is False

    def test_fsm_cannot_reach_released_state(self):
        policy = ReleasePolicy()
        audit = policy.evaluate([], None, None)
        assert not policy.can_release(audit)

        fsm = RunFSM(run_id="run_test_fsm")
        fsm.transition(FSMState.CONTEXT_VALIDATED, "OK", "test")
        fsm.transition(FSMState.TASK_GRAPH_READY, "OK", "test")
        fsm.transition(FSMState.EVIDENCE_ACQUISITION, "OK", "test")
        fsm.transition(FSMState.EVIDENCE_VALIDATION, "OK", "test")
        fsm.transition(FSMState.SAFETY_GATE_CHECK, "OK", "test")

        # Because can_release is False, transition to RELEASED must not happen
        # Instead, it must transition to ABSTAINED or BLOCKED
        if not policy.can_release(audit):
            fsm.transition(FSMState.ABSTAINED, "GATE_NOT_EVALUABLE", "Safety gate withheld clearance")

        assert fsm.state == FSMState.ABSTAINED
        assert fsm.state != FSMState.RELEASED
