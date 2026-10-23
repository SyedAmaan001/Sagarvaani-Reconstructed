"""
Sagarvani Reconstructed — Phase 4 Offline Tests
Tests for:
1. FSM — allowed and illegal transitions
2. FSM — terminal-state enforcement
3. FSM — deadline exceeded behaviour
4. DAG — cycle detection
5. DAG — duplicate task IDs
6. DAG — unknown dependencies
7. DAG — correct topological / wave ordering
8. Harness — concurrent independent task execution
9. Harness — dependency skip propagation on failure
10. Harness — per-task timeout enforcement
11. Harness — unregistered gateway produces FAILED
12. Harness — typed failure results, no silent success
13. Canonical endpoint — FSM + harness integration
14. Canonical endpoint — missing context returns CLARIFICATION_REQUIRED
15. Canonical endpoint — gateway failure yields typed gaps
16. Phase 1–3 regression: existing contracts, gateways, catalog still pass
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.engine.fsm import (
    DeadlineExceededError,
    FSMState,
    IllegalTransitionError,
    RunFSM,
    TERMINAL_STATES,
    TerminalStateError,
    ALLOWED_TRANSITIONS,
)
from backend.engine.dag import (
    CyclicDependencyError,
    DuplicateTaskIDError,
    TaskDAG,
    UnknownDependencyError,
)
from backend.engine.harness import ExecutionHarness, HarnessResult
from backend.models.enums import DataMode, RunStatus, TaskStatus
from backend.models.evidence import EvidenceRecord, GeoLocation
from backend.models.task import TaskContract, TaskResult
from backend.main import app

client = TestClient(app)


# ============================================================
# Helpers
# ============================================================

def make_task(
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


def make_evidence(task_id: str) -> EvidenceRecord:
    """Creates a minimal EvidenceRecord for testing."""
    now = datetime.now(timezone.utc)
    return EvidenceRecord(
        evidence_id=f"ev_{task_id}",
        source_id="test_source",
        source_name="Test Source",
        product_id="test_product",
        parameter="wave_height",
        value=1.2,
        unit="m",
        location=GeoLocation(lat=13.35, lon=74.70),
        retrieved_at=now,
        data_mode=DataMode.TEST_FIXTURE,
        valid_from=now,
        source_url="http://test.example.com",
        attribution="Test attribution",
    )


async def ok_gateway(params: Dict[str, Any]):
    """Fake gateway that succeeds immediately."""
    await asyncio.sleep(0)
    return {"status": "ok"}, [make_evidence(params.get("task_id", "ok"))]


async def failing_gateway(params: Dict[str, Any]):
    """Fake gateway that raises an exception."""
    raise RuntimeError("Simulated gateway failure")


async def slow_gateway(params: Dict[str, Any]):
    """Fake gateway that sleeps longer than typical timeout."""
    await asyncio.sleep(60)
    return {}, []


# ============================================================
# 1–3. FSM — transitions
# ============================================================

class TestFSMTransitions:

    def test_initial_state_is_requested(self):
        fsm = RunFSM(run_id="run_001")
        assert fsm.state == FSMState.REQUESTED

    def test_valid_transition_requested_to_context_validated(self):
        fsm = RunFSM(run_id="run_002")
        evt = fsm.transition(FSMState.CONTEXT_VALIDATED, "CONTEXT_OK", "ok")
        assert fsm.state == FSMState.CONTEXT_VALIDATED
        assert evt.from_state == FSMState.REQUESTED
        assert evt.to_state == FSMState.CONTEXT_VALIDATED
        assert evt.event_code == "CONTEXT_OK"

    def test_valid_full_happy_path(self):
        fsm = RunFSM(run_id="run_003")
        path = [
            (FSMState.CONTEXT_VALIDATED, "CONTEXT_OK", "ok"),
            (FSMState.TASK_GRAPH_READY, "DAG_VALIDATED", "ok"),
            (FSMState.EVIDENCE_ACQUISITION, "HARNESS_STARTED", "ok"),
            (FSMState.EVIDENCE_VALIDATION, "EVIDENCE_ACQUIRED", "ok"),
            (FSMState.SAFETY_GATE_CHECK, "VALIDATION_DONE", "ok"),
            (FSMState.ABSTAINED, "GATE_NOT_EVALUABLE", "not evaluable"),
        ]
        for to_state, code, reason in path:
            fsm.transition(to_state, code, reason)
        assert fsm.state == FSMState.ABSTAINED
        assert fsm.is_terminal

    def test_illegal_transition_raises_typed_error(self):
        fsm = RunFSM(run_id="run_004")
        with pytest.raises(IllegalTransitionError) as exc_info:
            fsm.transition(FSMState.RELEASED, "SKIP_TO_RELEASE", "bad")
        err = exc_info.value
        assert err.from_state == FSMState.REQUESTED
        assert err.to_state == FSMState.RELEASED
        assert "run_004" in str(err)

    def test_illegal_transition_does_not_change_state(self):
        fsm = RunFSM(run_id="run_005")
        with pytest.raises(IllegalTransitionError):
            fsm.transition(FSMState.EVIDENCE_ACQUISITION, "JUMP", "skip")
        assert fsm.state == FSMState.REQUESTED

    def test_all_transitions_in_table_are_valid(self):
        """Smoke-test: every entry in ALLOWED_TRANSITIONS is accepted by the FSM."""
        for from_state, targets in ALLOWED_TRANSITIONS.items():
            if from_state in TERMINAL_STATES:
                continue
            for to_state in targets:
                fsm = RunFSM(run_id=f"run_tt_{from_state}_{to_state}")
                # Manually set internal state to test from_state
                fsm._state = from_state
                evt = fsm.transition(to_state, "TABLE_CHECK", "ok")
                assert evt.to_state == to_state

    def test_event_log_is_ordered(self):
        fsm = RunFSM(run_id="run_006")
        fsm.transition(FSMState.CONTEXT_VALIDATED, "E1", "e1")
        fsm.transition(FSMState.TASK_GRAPH_READY, "E2", "e2")
        events = fsm.events
        assert len(events) == 2
        assert events[0].event_code == "E1"
        assert events[1].event_code == "E2"

    def test_recovery_planning_can_loop_back_to_evidence_acquisition(self):
        fsm = RunFSM(run_id="run_007")
        fsm._state = FSMState.RECOVERY_PLANNING
        evt = fsm.transition(FSMState.EVIDENCE_ACQUISITION, "RETRY", "retry attempt")
        assert fsm.state == FSMState.EVIDENCE_ACQUISITION
        assert evt.event_code == "RETRY"


# ============================================================
# 2. Terminal-state enforcement
# ============================================================

class TestFSMTerminalStates:

    @pytest.mark.parametrize("terminal_state", list(TERMINAL_STATES))
    def test_no_transition_from_terminal_state(self, terminal_state: FSMState):
        fsm = RunFSM(run_id=f"run_term_{terminal_state.value}")
        fsm._state = terminal_state
        # Attempt any transition
        with pytest.raises(TerminalStateError) as exc_info:
            fsm.transition(FSMState.REQUESTED, "RESET", "bad")
        assert exc_info.value.current_state == terminal_state

    def test_is_terminal_flag_correct(self):
        fsm = RunFSM(run_id="run_008")
        assert not fsm.is_terminal
        fsm._state = FSMState.FAILED
        assert fsm.is_terminal

    def test_force_terminal_on_non_terminal_raises(self):
        fsm = RunFSM(run_id="run_009")
        with pytest.raises(ValueError):
            fsm.force_terminal(FSMState.CONTEXT_VALIDATED, "BAD", "bad")

    def test_force_terminal_succeeds(self):
        fsm = RunFSM(run_id="run_010")
        evt = fsm.force_terminal(FSMState.TIMED_OUT, "SIGNAL", "forced")
        assert fsm.state == FSMState.TIMED_OUT
        assert evt.to_state == FSMState.TIMED_OUT


# ============================================================
# 3. Deadline enforcement
# ============================================================

class TestFSMDeadline:

    def test_expired_deadline_forces_timed_out(self):
        past = datetime.now(timezone.utc) - timedelta(seconds=1)
        fsm = RunFSM(run_id="run_dl_01", deadline=past)
        with pytest.raises(DeadlineExceededError):
            fsm.transition(FSMState.CONTEXT_VALIDATED, "CONTEXT_OK", "ok")
        assert fsm.state == FSMState.TIMED_OUT

    def test_future_deadline_does_not_block(self):
        future = datetime.now(timezone.utc) + timedelta(seconds=60)
        fsm = RunFSM(run_id="run_dl_02", deadline=future)
        fsm.transition(FSMState.CONTEXT_VALIDATED, "CONTEXT_OK", "ok")
        assert fsm.state == FSMState.CONTEXT_VALIDATED

    def test_transitioning_to_terminal_not_blocked_by_deadline(self):
        """Transitioning directly to a terminal state should bypass deadline check."""
        past = datetime.now(timezone.utc) - timedelta(seconds=1)
        fsm = RunFSM(run_id="run_dl_03", deadline=past)
        # FAILED is in ALLOWED_TRANSITIONS[REQUESTED] and is terminal; should not trigger deadline
        evt = fsm.transition(FSMState.FAILED, "CRITICAL", "emergency stop")
        assert fsm.state == FSMState.FAILED


# ============================================================
# 4–6. DAG validation
# ============================================================

class TestTaskDAGValidation:

    def test_valid_simple_dag(self):
        tasks = [make_task("t1"), make_task("t2")]
        dag = TaskDAG(tasks)
        assert len(dag.contracts) == 2

    def test_duplicate_task_id_raises(self):
        tasks = [make_task("t1"), make_task("t1")]
        with pytest.raises(DuplicateTaskIDError) as exc_info:
            TaskDAG(tasks)
        assert "t1" in str(exc_info.value)

    def test_unknown_dependency_raises(self):
        tasks = [make_task("t1", dependencies=["t_ghost"])]
        with pytest.raises(UnknownDependencyError) as exc_info:
            TaskDAG(tasks)
        assert "t_ghost" in str(exc_info.value)

    def test_cyclic_dependency_raises(self):
        # t1 depends on t2, t2 depends on t1
        tasks = [
            make_task("t1", dependencies=["t2"]),
            make_task("t2", dependencies=["t1"]),
        ]
        with pytest.raises(CyclicDependencyError):
            TaskDAG(tasks)

    def test_self_loop_raises(self):
        tasks = [make_task("t1", dependencies=["t1"])]
        with pytest.raises(CyclicDependencyError):
            TaskDAG(tasks)

    def test_topological_order_respects_deps(self):
        # t2 depends on t1; t1 must appear first
        tasks = [
            make_task("t2", dependencies=["t1"]),
            make_task("t1"),
        ]
        dag = TaskDAG(tasks)
        order = dag.topological_order()
        ids = [t.task_id for t in order]
        assert ids.index("t1") < ids.index("t2")

    def test_independent_tasks_in_same_wave(self):
        tasks = [make_task("t1"), make_task("t2")]
        dag = TaskDAG(tasks)
        waves = dag.independent_groups()
        assert len(waves) == 1
        assert len(waves[0]) == 2

    def test_dependent_tasks_in_separate_waves(self):
        tasks = [
            make_task("t1"),
            make_task("t2", dependencies=["t1"]),
        ]
        dag = TaskDAG(tasks)
        waves = dag.independent_groups()
        assert len(waves) == 2
        assert waves[0][0].task_id == "t1"
        assert waves[1][0].task_id == "t2"

    def test_empty_dag_valid(self):
        dag = TaskDAG([])
        assert dag.topological_order() == []
        assert dag.independent_groups() == []


# ============================================================
# 7–12. Execution harness
# ============================================================

class TestExecutionHarness:

    @pytest.mark.anyio
    async def test_independent_tasks_execute_concurrently(self):
        """Two independent tasks should complete; both succeed with evidence."""
        tasks = [make_task("t1", gateway_id="ok_gw"), make_task("t2", gateway_id="ok_gw")]
        dag = TaskDAG(tasks)
        registry = {"ok_gw": ok_gateway}
        harness = ExecutionHarness(dag, registry)
        result = await harness.execute()
        completed = {t.task_id for t in result.task_results if t.status == TaskStatus.COMPLETED}
        assert "t1" in completed
        assert "t2" in completed
        assert result.all_succeeded

    @pytest.mark.anyio
    async def test_failed_prerequisite_skips_dependent(self):
        """If t1 fails, t2 (which depends on t1) must be SKIPPED."""
        tasks = [
            make_task("t1", gateway_id="fail_gw"),
            make_task("t2", gateway_id="ok_gw", dependencies=["t1"]),
        ]
        dag = TaskDAG(tasks)
        registry = {"fail_gw": failing_gateway, "ok_gw": ok_gateway}
        harness = ExecutionHarness(dag, registry)
        result = await harness.execute()
        by_id = {t.task_id: t for t in result.task_results}
        assert by_id["t1"].status == TaskStatus.FAILED
        assert by_id["t2"].status == TaskStatus.SKIPPED
        assert "t1" in result.failed_task_ids
        assert "t2" in result.skipped_task_ids

    @pytest.mark.anyio
    async def test_task_timeout_produces_timed_out_result(self):
        """A task that exceeds its timeout becomes TIMED_OUT, not FAILED."""
        tasks = [make_task("t_slow", gateway_id="slow_gw", timeout_seconds=0.05)]
        dag = TaskDAG(tasks)
        registry = {"slow_gw": slow_gateway}
        harness = ExecutionHarness(dag, registry)
        result = await harness.execute()
        assert result.timed_out_task_ids == ["t_slow"]
        by_id = {t.task_id: t for t in result.task_results}
        assert by_id["t_slow"].status == TaskStatus.TIMED_OUT

    @pytest.mark.anyio
    async def test_unregistered_gateway_produces_failed(self):
        """A task with no registered gateway yields FAILED with descriptive error."""
        tasks = [make_task("t_no_gw", gateway_id="nonexistent_gw")]
        dag = TaskDAG(tasks)
        harness = ExecutionHarness(dag, {})
        result = await harness.execute()
        by_id = {t.task_id: t for t in result.task_results}
        assert by_id["t_no_gw"].status == TaskStatus.FAILED
        assert "nonexistent_gw" in (by_id["t_no_gw"].error_message or "")

    @pytest.mark.anyio
    async def test_gateway_exception_produces_failed_not_exception(self):
        """An exception inside a gateway produces FAILED result, not an uncaught exception."""
        tasks = [make_task("t_exc", gateway_id="fail_gw")]
        dag = TaskDAG(tasks)
        registry = {"fail_gw": failing_gateway}
        harness = ExecutionHarness(dag, registry)
        result = await harness.execute()
        by_id = {t.task_id: t for t in result.task_results}
        assert by_id["t_exc"].status == TaskStatus.FAILED
        assert "Simulated gateway failure" in (by_id["t_exc"].error_message or "")

    @pytest.mark.anyio
    async def test_run_deadline_cancels_pending_tasks(self):
        """Passing an already-expired deadline should cancel tasks before they start."""
        past = datetime.now(timezone.utc) - timedelta(seconds=1)
        tasks = [make_task("t1", gateway_id="ok_gw"), make_task("t2", gateway_id="ok_gw")]
        dag = TaskDAG(tasks)
        registry = {"ok_gw": ok_gateway}
        harness = ExecutionHarness(dag, registry, run_deadline=past)
        result = await harness.execute()
        for tr in result.task_results:
            assert tr.status == TaskStatus.TIMED_OUT

    @pytest.mark.anyio
    async def test_concurrency_bounded(self):
        """Max concurrency = 1 means tasks run serially but all complete."""
        call_log: List[str] = []

        async def logging_gateway(params: Dict[str, Any]):
            call_log.append(params.get("_task_label", "?"))
            await asyncio.sleep(0)
            return {}, [make_evidence(params.get("_task_label", "x"))]

        tasks = [
            make_task("ta", gateway_id="log_gw"),
            make_task("tb", gateway_id="log_gw"),
        ]
        # Inject label into params
        tasks[0] = tasks[0].model_copy(update={"parameters": {"_task_label": "ta"}})
        tasks[1] = tasks[1].model_copy(update={"parameters": {"_task_label": "tb"}})
        dag = TaskDAG(tasks)
        harness = ExecutionHarness(dag, {"log_gw": logging_gateway}, max_concurrency=1)
        result = await harness.execute()
        assert result.all_succeeded
        assert set(call_log) == {"ta", "tb"}

    @pytest.mark.anyio
    async def test_evidence_collected_from_successful_tasks(self):
        tasks = [make_task("t_ev", gateway_id="ok_gw")]
        dag = TaskDAG(tasks)
        harness = ExecutionHarness(dag, {"ok_gw": ok_gateway})
        result = await harness.execute()
        assert len(result.evidence) == 1

    @pytest.mark.anyio
    async def test_no_evidence_when_all_fail(self):
        tasks = [make_task("t_f", gateway_id="fail_gw")]
        dag = TaskDAG(tasks)
        harness = ExecutionHarness(dag, {"fail_gw": failing_gateway})
        result = await harness.execute()
        assert not result.any_evidence
        assert not result.all_succeeded


# ============================================================
# 13–15. Canonical endpoint integration
# ============================================================

VALID_QUERY_PAYLOAD = {
    "query": "Is it safe to fish near Malpe today?",
    "context_override": {
        "location": {"lat": 13.35, "lon": 74.70, "location_name": "Malpe"},
        "departure_time": "2026-11-01T06:00:00Z",
    },
}

MISSING_LOC_PAYLOAD = {
    "query": "What are the fishing conditions?",
}


def _make_fake_registry(succeed: bool = True):
    """Returns a gateway registry with fake async gateways for tests."""
    if succeed:
        async def _fake_marine(params):
            now = datetime.now(timezone.utc)
            ev = [
                _make_ev("wave_height", "m", params),
                _make_ev("wave_direction", "°", params),
                _make_ev("wave_period", "s", params),
            ]
            return {"fake": "marine"}, ev

        async def _fake_weather(params):
            now = datetime.now(timezone.utc)
            ev = [
                _make_ev("wind_speed_10m", "km/h", params),
                _make_ev("wind_direction_10m", "°", params),
                _make_ev("wind_gusts_10m", "km/h", params),
            ]
            return {"fake": "weather"}, ev
    else:
        async def _fake_marine(params):
            raise RuntimeError("Simulated marine failure")

        async def _fake_weather(params):
            raise RuntimeError("Simulated weather failure")

    return {
        "open_meteo_marine": _fake_marine,
        "open_meteo_weather": _fake_weather,
    }


def _make_ev(param: str, unit: str, params: Dict[str, Any]) -> EvidenceRecord:
    now = datetime.now(timezone.utc)
    lat = params.get("lat", 13.35)
    lon = params.get("lon", 74.70)
    return EvidenceRecord(
        evidence_id=f"ev_{param}_{id(param)}",
        source_id="test",
        source_name="Test",
        product_id="test_product",
        parameter=param,
        value=1.0,
        unit=unit,
        location=GeoLocation(lat=lat, lon=lon),
        retrieved_at=now,
        data_mode=DataMode.TEST_FIXTURE,
        valid_from=now,
        source_url="http://test.example",
        attribution="Test",
    )


class TestCanonicalEndpointIntegration:

    def test_missing_location_returns_clarification_required(self):
        resp = client.post("/api/orca/query", json=MISSING_LOC_PAYLOAD)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "CLARIFICATION_REQUIRED"
        assert data["policy_audit"]["overall_verdict"] == "NOT_EVALUABLE"
        gap_codes = [g["gap_code"] for g in data["gaps"]]
        assert "GAP_MISSING_LOCATION" in gap_codes

    def test_invalid_payload_returns_422(self):
        resp = client.post("/api/orca/query", json={"not_a_query": True})
        assert resp.status_code == 422

    def test_policy_audit_always_not_evaluable(self):
        """Policy must remain NOT_EVALUABLE regardless of evidence quality."""
        with patch("backend.main._PRODUCTION_REGISTRY", _make_fake_registry(succeed=True)):
            resp = client.post("/api/orca/query", json=VALID_QUERY_PAYLOAD)
        assert resp.status_code == 200
        data = resp.json()
        assert data["policy_audit"]["overall_verdict"] == "NOT_EVALUABLE"

    def test_valid_query_with_fake_gateways_returns_completed(self):
        with patch("backend.main._PRODUCTION_REGISTRY", _make_fake_registry(succeed=True)):
            resp = client.post("/api/orca/query", json=VALID_QUERY_PAYLOAD)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] in ("COMPLETED", "PARTIAL")
        assert len(data["evidence"]) > 0

    def test_gateway_failure_produces_typed_gaps_not_success(self):
        """When all gateways fail, response must not fabricate successful evidence."""
        with patch("backend.main._PRODUCTION_REGISTRY", _make_fake_registry(succeed=False)):
            resp = client.post("/api/orca/query", json=VALID_QUERY_PAYLOAD)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] in ("SOURCE_UNAVAILABLE", "PARTIAL", "TIMED_OUT")
        assert len(data["evidence"]) == 0
        assert len(data["gaps"]) > 0

    def test_run_id_and_trace_id_present(self):
        resp = client.post("/api/orca/query", json=MISSING_LOC_PAYLOAD)
        data = resp.json()
        assert data["run_id"].startswith("run_")
        assert data["trace_id"].startswith("tr_")

    def test_health_check_still_works(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"


# ============================================================
# 16. Phase 1–3 regression
# ============================================================

class TestPhase13Regression:

    def test_enums_completeness(self):
        from backend.models.enums import (
            GateCheckOutcome, OverallGateVerdict, RunStatus, TaskStatus,
            RecoveryActionType, RecoveryOutcome, RecoverySelectorType,
        )
        assert "PASS" in [e.value for e in GateCheckOutcome]
        assert "BLOCK" in [e.value for e in GateCheckOutcome]
        assert "NOT_EVALUABLE" in [e.value for e in GateCheckOutcome]
        assert TaskStatus.TIMED_OUT in TaskStatus
        assert TaskStatus.SKIPPED in TaskStatus

    def test_evidence_record_strict_temporal_model(self):
        from backend.models.evidence import EvidenceRecord, GeoLocation
        now = datetime.now(timezone.utc)
        ev = EvidenceRecord(
            evidence_id="ev_001",
            source_id="open_meteo_marine",
            source_name="Open-Meteo Marine",
            product_id="marine_v1",
            parameter="wave_height",
            value=1.5,
            unit="m",
            location=GeoLocation(lat=13.35, lon=74.70),
            retrieved_at=now,
            data_mode=DataMode.LIVE_FORECAST,
            valid_from=now,
            source_url="https://marine-api.open-meteo.com",
            attribution="Open-Meteo (CC BY 4.0)",
        )
        assert ev.observed_at is None
        assert ev.issued_at is None
        assert ev.model_run_at is None
        assert ev.artifact_ref is None

    def test_task_contract_serialization(self):
        tc = TaskContract(
            task_id="task_fetch_marine_forecast",
            task_name="Marine Forecast",
            gateway_id="open_meteo_marine",
            dependencies=[],
            timeout_seconds=10.0,
            parameters={"lat": 13.35, "lon": 74.70},
        )
        data = tc.model_dump()
        assert data["task_id"] == "task_fetch_marine_forecast"
        assert data["timeout_seconds"] == 10.0

    def test_recovery_trace_entry(self):
        from backend.models.recovery import RecoveryTraceEntry, IdentifiedGap
        from backend.models.enums import RecoveryActionType, RecoveryOutcome, RecoverySelectorType
        now = datetime.now(timezone.utc)
        entry = RecoveryTraceEntry(
            cycle=1,
            selector=RecoverySelectorType.DETERMINISTIC_RULES,
            action=RecoveryActionType.RETRY_WITH_BACKOFF,
            target_gap=IdentifiedGap(
                gap_code="GAP_STALE",
                description="Stale evidence detected",
                suggested_action=RecoveryActionType.RETRY_WITH_BACKOFF,
            ),
            parameters_applied={"max_age_hours": 6},
            outcome=RecoveryOutcome.SUCCEEDED,
            timestamp=now,
        )
        assert entry.cycle == 1
        assert entry.outcome == RecoveryOutcome.SUCCEEDED

    def test_artifact_store_still_works(self, tmp_path):
        from backend.catalog.artifact_store import ArtifactStore
        store = ArtifactStore(base_dir=str(tmp_path))
        payload = {"hello": "world"}
        rel, chk, size = store.save_artifact("run_test", "task_a", payload)
        assert "runs/run_test/task_a" in rel
        assert len(chk) == 64
        assert size > 0

    def test_sqlite_migrations_idempotency(self, tmp_path):
        import sqlite3
        from backend.catalog.migrations import apply_migrations, MIGRATIONS
        db = str(tmp_path / "test.db")
        with sqlite3.connect(db) as conn:
            n1 = apply_migrations(conn)
        with sqlite3.connect(db) as conn:
            n2 = apply_migrations(conn)
        assert n1 == len(MIGRATIONS)
        assert n2 == 0   # Second run applies nothing

    def test_fsm_transitions_persisted_to_sqlite(self, tmp_path):
        """FSM transitions should be queryable from the catalog after a run."""
        import sqlite3
        from backend.catalog.migrations import apply_migrations
        from backend.catalog.service import CatalogService
        db = str(tmp_path / "fsm_test.db")
        svc = CatalogService(db_path=db)
        fsm = RunFSM(run_id="run_fsm_persist")
        fsm.transition(FSMState.CONTEXT_VALIDATED, "CONTEXT_OK", "test")
        fsm.transition(FSMState.ABSTAINED, "MISSING", "test abstain")
        svc.record_fsm_transitions("run_fsm_persist", fsm.events)
        rows = svc.get_fsm_transitions("run_fsm_persist")
        assert len(rows) == 2
        assert rows[0]["from_state"] == "REQUESTED"
        assert rows[0]["to_state"] == "CONTEXT_VALIDATED"
        assert rows[1]["to_state"] == "ABSTAINED"
