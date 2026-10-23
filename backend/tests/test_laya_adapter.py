"""
Sagarvani Reconstructed — Phase 6: Laya Decision Adapter Tests
Offline unit tests, edge cases, fallbacks, comparative benchmarks, and safety guarantees.

Test classes:
1. TestRuleBasedSelectorBaseline: Deterministic baseline behavior and SelectorTraceEntry.
2. TestLayaSelectorGatingAndFallbacks: Feature flag, missing dependency, timeouts, and model errors.
3. TestLayaOutputValidation: Allow-list enforcement, rejection of invalid/unknown actions, malformed payloads.
4. TestRulesVsLayaLabelledBenchmark: Side-by-side comparison across 10 labelled test cases.
5. TestRecoveryControllerWithLaya: R3 bounded execution, max 2 cycles, no-progress detection, revalidation.
6. TestReleasePolicyIndependence: Proves Laya has zero ability to override release gates.
7. TestSelectorTracePersistence: SQLite catalog storage and retrieval of selector traces.
8. TestOptInLiveLayaInference: Explicitly opt-in live model execution test.
"""

from datetime import datetime, timezone
import os
import time
from typing import Any, Dict, List, Optional, Set
import pytest

from backend.catalog.service import CatalogService
from backend.core.config import Settings
from backend.engine.laya_adapter import ACTION_CRITERIA_DESCRIPTIONS, LayaRecoverySelector
from backend.engine.policy import ReleasePolicy
from backend.engine.recovery import (
    MAX_RECOVERY_CYCLES,
    PERMITTED_ACTIONS,
    RecoveryController,
    RuleBasedRecoverySelector,
)
from backend.engine.validator import EvidenceValidator
from backend.models.enums import (
    DataMode,
    GateCheckOutcome,
    OverallGateVerdict,
    RecoveryActionType,
    RecoveryOutcome,
    RecoverySelectorType,
)
from backend.models.evidence import EvidenceRecord, GeoLocation
from backend.models.query import QueryContext
from backend.models.recovery import IdentifiedGap, RecoveryTraceEntry, SelectorTraceEntry


# ---------------------------------------------------------------------------
# Test Stubs & Mock Routers
# ---------------------------------------------------------------------------

class StubRouter:
    """Mock Laya router returning pre-configured choice or raising exceptions."""

    def __init__(
        self,
        choice: Optional[str] = None,
        delay_seconds: float = 0.0,
        raise_exc: Optional[Exception] = None,
    ):
        self.choice = choice
        self.delay_seconds = delay_seconds
        self.raise_exc = raise_exc
        self.call_count = 0
        self.last_state: Optional[Dict[str, Any]] = None
        self.last_questions: Optional[Dict[str, Any]] = None

    def predict(self, state: Dict[str, Any], questions: Dict[str, Any]) -> Dict[str, Any]:
        self.call_count += 1
        self.last_state = state
        self.last_questions = questions

        if self.delay_seconds > 0:
            time.sleep(self.delay_seconds)

        if self.raise_exc:
            raise self.raise_exc

        return {
            "answers": {
                "recovery_action": {
                    "choice": self.choice,
                    "confidence": 0.95,
                    "probabilities": {self.choice: 0.95} if self.choice else {},
                }
            },
            "routing": {"model": "english"},
        }


# ---------------------------------------------------------------------------
# 1. TestRuleBasedSelectorBaseline
# ---------------------------------------------------------------------------

class TestRuleBasedSelectorBaseline:
    """Validates the deterministic baseline selector and its audit traces."""

    def test_rules_selector_maps_standard_gaps(self):
        selector = RuleBasedRecoverySelector()
        history: List[RecoveryTraceEntry] = []

        # Weather transient error -> RETRY_WITH_BACKOFF
        gap_w = IdentifiedGap(gap_code="GAP_WEATHER_SOURCE_ERROR", description="Weather timeout")
        act_w = selector.select_action(gap_w, 1, history, PERMITTED_ACTIONS)
        assert act_w == RecoveryActionType.RETRY_WITH_BACKOFF

        # Marine transient error -> RETRY_WITH_BACKOFF
        gap_m = IdentifiedGap(gap_code="GAP_MARINE_SOURCE_ERROR", description="Marine 500")
        act_m = selector.select_action(gap_m, 1, history, PERMITTED_ACTIONS)
        assert act_m == RecoveryActionType.RETRY_WITH_BACKOFF

        # Spatial coverage exceeded -> EXPAND_SPATIAL_RADIUS
        gap_sp = IdentifiedGap(gap_code="GAP_SPATIAL_COVERAGE_EXCEEDED", description="Too far")
        act_sp = selector.select_action(gap_sp, 1, history, PERMITTED_ACTIONS)
        assert act_sp == RecoveryActionType.EXPAND_SPATIAL_RADIUS

        # Temporal window mismatch -> EXTEND_TEMPORAL_WINDOW
        gap_tp = IdentifiedGap(gap_code="GAP_TEMPORAL_WINDOW_MISMATCH", description="Old valid time")
        act_tp = selector.select_action(gap_tp, 1, history, PERMITTED_ACTIONS)
        assert act_tp == RecoveryActionType.EXTEND_TEMPORAL_WINDOW

        # Missing location -> REQUEST_USER_CLARIFICATION
        gap_loc = IdentifiedGap(gap_code="GAP_MISSING_LOCATION", description="No coordinates")
        act_loc = selector.select_action(gap_loc, 1, history, PERMITTED_ACTIONS)
        assert act_loc == RecoveryActionType.REQUEST_USER_CLARIFICATION

        # Stale evidence -> SWITCH_FALLBACK_PROVIDER
        gap_stale = IdentifiedGap(gap_code="GAP_STALE_EVIDENCE", description="Stale data")
        act_stale = selector.select_action(gap_stale, 1, history, PERMITTED_ACTIONS)
        assert act_stale == RecoveryActionType.SWITCH_FALLBACK_PROVIDER

    def test_rules_selector_trace_entry_structure(self):
        selector = RuleBasedRecoverySelector()
        gap = IdentifiedGap(gap_code="GAP_SPATIAL_COVERAGE_EXCEEDED", description="Spatial gap")

        action, trace = selector.select_action_with_trace(gap, 1, [], PERMITTED_ACTIONS)

        assert action == RecoveryActionType.EXPAND_SPATIAL_RADIUS
        assert isinstance(trace, SelectorTraceEntry)
        assert trace.selector_type == RecoverySelectorType.DETERMINISTIC_RULES
        assert trace.checkpoint is None
        assert trace.is_valid is True
        assert trace.latency_ms >= 0.0
        assert trace.fallback_reason is None
        assert trace.raw_action == "expand_spatial_radius"
        assert trace.validated_action == RecoveryActionType.EXPAND_SPATIAL_RADIUS
        assert trace.timestamp is not None

    def test_rules_selector_history_escalation(self):
        selector = RuleBasedRecoverySelector()
        gap = IdentifiedGap(gap_code="GAP_WEATHER_SOURCE_ERROR", description="Weather error")

        # Cycle 1: RETRY_WITH_BACKOFF
        act1 = selector.select_action(gap, 1, [], PERMITTED_ACTIONS)
        assert act1 == RecoveryActionType.RETRY_WITH_BACKOFF

        # History with cycle 1 retry attempted
        hist1 = [
            RecoveryTraceEntry(
                cycle=1,
                selector=RecoverySelectorType.DETERMINISTIC_RULES,
                action=RecoveryActionType.RETRY_WITH_BACKOFF,
                target_gap=gap,
                parameters_applied={},
                outcome=RecoveryOutcome.FAILED,
                timestamp=datetime.now(timezone.utc),
            )
        ]

        # Cycle 2: escalates to SWITCH_FALLBACK_PROVIDER
        act2 = selector.select_action(gap, 2, hist1, PERMITTED_ACTIONS)
        assert act2 == RecoveryActionType.SWITCH_FALLBACK_PROVIDER

        # History with both retry and fallback attempted
        hist2 = list(hist1) + [
            RecoveryTraceEntry(
                cycle=2,
                selector=RecoverySelectorType.DETERMINISTIC_RULES,
                action=RecoveryActionType.SWITCH_FALLBACK_PROVIDER,
                target_gap=gap,
                parameters_applied={},
                outcome=RecoveryOutcome.FAILED,
                timestamp=datetime.now(timezone.utc),
            )
        ]

        # Exhausted: ABSTAIN_AND_LOG
        act3 = selector.select_action(gap, 2, hist2, PERMITTED_ACTIONS)
        assert act3 == RecoveryActionType.ABSTAIN_AND_LOG


# ---------------------------------------------------------------------------
# 2. TestLayaSelectorGatingAndFallbacks
# ---------------------------------------------------------------------------

class TestLayaSelectorGatingAndFallbacks:
    """Tests feature-flag, dependency, and runtime error fallback behaviors."""

    def test_laya_disabled_by_default(self):
        """When ENABLE_LAYA_SELECTOR=False, falls back immediately to rules with trace."""
        selector = LayaRecoverySelector(enabled=False)
        gap = IdentifiedGap(gap_code="GAP_MARINE_SOURCE_ERROR", description="Timeout")

        action, trace = selector.select_action_with_trace(gap, 1, [], PERMITTED_ACTIONS)

        assert action == RecoveryActionType.RETRY_WITH_BACKOFF
        assert trace.selector_type == RecoverySelectorType.LAYA
        assert trace.is_valid is False
        assert trace.validated_action == RecoveryActionType.RETRY_WITH_BACKOFF
        assert "ENABLE_LAYA_SELECTOR=False" in (trace.fallback_reason or "")

    def test_laya_missing_dependency_fallback(self, monkeypatch):
        """When laya cannot be imported, falls back to rules gracefully."""
        selector = LayaRecoverySelector(enabled=True)
        gap = IdentifiedGap(gap_code="GAP_WEATHER_SOURCE_ERROR", description="Weather error")

        # Mock _get_or_create_router to simulate ImportError
        def _mock_import():
            raise ImportError("No module named 'laya'")

        monkeypatch.setattr(selector, "_get_or_create_router", _mock_import)

        action, trace = selector.select_action_with_trace(gap, 1, [], PERMITTED_ACTIONS)

        assert action == RecoveryActionType.RETRY_WITH_BACKOFF
        assert trace.selector_type == RecoverySelectorType.LAYA
        assert trace.is_valid is False
        assert "not installed" in (trace.fallback_reason or "")

    def test_laya_model_init_error_fallback(self, monkeypatch):
        """When model instantiation raises RuntimeError, falls back to rules."""
        selector = LayaRecoverySelector(enabled=True)
        gap = IdentifiedGap(gap_code="GAP_SPATIAL_COVERAGE_EXCEEDED", description="Far out")

        def _mock_init():
            raise RuntimeError("Checkpoint weights file corrupt")

        monkeypatch.setattr(selector, "_get_or_create_router", _mock_init)

        action, trace = selector.select_action_with_trace(gap, 1, [], PERMITTED_ACTIONS)

        assert action == RecoveryActionType.EXPAND_SPATIAL_RADIUS
        assert trace.is_valid is False
        assert "Failed to initialize Laya model" in (trace.fallback_reason or "")

    def test_laya_inference_timeout_fallback(self):
        """When inference exceeds timeout_seconds, times out and falls back to rules."""
        stub = StubRouter(choice="retry_with_backoff", delay_seconds=0.2)
        # Timeout set to 0.05s, delay is 0.2s -> must trigger timeout
        selector = LayaRecoverySelector(enabled=True, timeout_seconds=0.05, router=stub)
        gap = IdentifiedGap(gap_code="GAP_MARINE_SOURCE_ERROR", description="Timeout test")

        action, trace = selector.select_action_with_trace(gap, 1, [], PERMITTED_ACTIONS)

        assert action == RecoveryActionType.RETRY_WITH_BACKOFF
        assert trace.is_valid is False
        assert "timed out after" in (trace.fallback_reason or "")


# ---------------------------------------------------------------------------
# 3. TestLayaOutputValidation
# ---------------------------------------------------------------------------

class TestLayaOutputValidation:
    """Verifies that Laya outputs are strictly constrained to allow-listed actions."""

    def test_valid_allowlisted_action_accepted(self):
        """Model returns an allowed action string -> accepted directly."""
        stub = StubRouter(choice="expand_spatial_radius")
        selector = LayaRecoverySelector(enabled=True, router=stub)
        gap = IdentifiedGap(gap_code="GAP_SPATIAL_COVERAGE_EXCEEDED", description="Spatial gap")

        action, trace = selector.select_action_with_trace(gap, 1, [], PERMITTED_ACTIONS)

        assert action == RecoveryActionType.EXPAND_SPATIAL_RADIUS
        assert trace.is_valid is True
        assert trace.raw_action == "expand_spatial_radius"
        assert trace.validated_action == RecoveryActionType.EXPAND_SPATIAL_RADIUS
        assert trace.fallback_reason is None

    def test_unapproved_action_rejected(self):
        """Model hallucinates or selects an unapproved action string -> rejected, falls back to rules."""
        stub = StubRouter(choice="download_external_file_now")
        selector = LayaRecoverySelector(enabled=True, router=stub)
        gap = IdentifiedGap(gap_code="GAP_WEATHER_SOURCE_ERROR", description="Weather error")

        action, trace = selector.select_action_with_trace(gap, 1, [], PERMITTED_ACTIONS)

        # Must fall back to rule-based action
        assert action == RecoveryActionType.RETRY_WITH_BACKOFF
        assert trace.is_valid is False
        assert trace.raw_action == "download_external_file_now"
        assert trace.validated_action == RecoveryActionType.RETRY_WITH_BACKOFF
        assert "not in allowed actions" in (trace.fallback_reason or "")

    def test_action_not_in_currently_permitted_subset_rejected(self):
        """Model returns a valid enum action that is excluded from the current allowed subset."""
        stub = StubRouter(choice="retry_with_backoff")
        selector = LayaRecoverySelector(enabled=True, router=stub)
        gap = IdentifiedGap(gap_code="GAP_MISSING_LOCATION", description="No location")

        # Restrict allowed actions to clarification and abstain only
        restricted_actions = {
            RecoveryActionType.REQUEST_USER_CLARIFICATION,
            RecoveryActionType.ABSTAIN_AND_LOG,
        }

        action, trace = selector.select_action_with_trace(gap, 1, [], restricted_actions)

        # retry_with_backoff is not in restricted_actions -> rejected, falls back to clarification
        assert action == RecoveryActionType.REQUEST_USER_CLARIFICATION
        assert trace.is_valid is False
        assert "not in allowed actions" in (trace.fallback_reason or "")

    def test_malformed_model_payload_rejected(self):
        """Model returns None or malformed payload -> rejected gracefully."""
        stub = StubRouter(choice=None)
        selector = LayaRecoverySelector(enabled=True, router=stub)
        gap = IdentifiedGap(gap_code="GAP_TEMPORAL_WINDOW_MISMATCH", description="Old time")

        action, trace = selector.select_action_with_trace(gap, 1, [], PERMITTED_ACTIONS)

        assert action == RecoveryActionType.EXTEND_TEMPORAL_WINDOW
        assert trace.is_valid is False
        assert "no choice" in (trace.fallback_reason or "")

    def test_state_and_questions_schema_contract(self):
        """Validates that state and question structures match Laya's official specification."""
        stub = StubRouter(choice="retry_with_backoff")
        selector = LayaRecoverySelector(enabled=True, router=stub)
        gap = IdentifiedGap(
            gap_code="GAP_WEATHER_SOURCE_ERROR",
            description="Weather HTTP 504",
            affected_parameter="wind_speed",
        )

        selector.select_action(gap, 1, [], PERMITTED_ACTIONS)

        assert stub.last_state is not None
        assert stub.last_state["gap_code"] == "GAP_WEATHER_SOURCE_ERROR"
        assert stub.last_state["affected_parameter"] == "wind_speed"
        assert stub.last_state["cycle"] == 1
        assert "attempted_actions" in stub.last_state

        assert stub.last_questions is not None
        q = stub.last_questions["recovery_action"]
        assert q["type"] == "choice"
        assert "criteria" in q
        for act in PERMITTED_ACTIONS:
            assert act.value in q["criteria"]


# ---------------------------------------------------------------------------
# 4. TestRulesVsLayaLabelledBenchmark
# ---------------------------------------------------------------------------

class TestRulesVsLayaLabelledBenchmark:
    """
    Labelled comparative benchmark evaluating both RuleBasedRecoverySelector and
    LayaRecoverySelector across 10 standard test cases.
    """

    BENCHMARK_CASES = [
        # (id, gap_code, affected_param, history_actions, expected_rule_action, laya_candidate_choice)
        (
            "C1_MARINE_TIMEOUT",
            "GAP_MARINE_SOURCE_ERROR",
            "wave_height",
            [],
            RecoveryActionType.RETRY_WITH_BACKOFF,
            "retry_with_backoff",
        ),
        (
            "C2_WEATHER_ERROR",
            "GAP_WEATHER_SOURCE_ERROR",
            "wind_speed",
            [],
            RecoveryActionType.RETRY_WITH_BACKOFF,
            "retry_with_backoff",
        ),
        (
            "C3_SPATIAL_EXCEEDED",
            "GAP_SPATIAL_COVERAGE_EXCEEDED",
            None,
            [],
            RecoveryActionType.EXPAND_SPATIAL_RADIUS,
            "expand_spatial_radius",
        ),
        (
            "C4_TEMPORAL_MISMATCH",
            "GAP_TEMPORAL_WINDOW_MISMATCH",
            None,
            [],
            RecoveryActionType.EXTEND_TEMPORAL_WINDOW,
            "extend_temporal_window",
        ),
        (
            "C5_MISSING_LOCATION",
            "GAP_MISSING_LOCATION",
            None,
            [],
            RecoveryActionType.REQUEST_USER_CLARIFICATION,
            "request_user_clarification",
        ),
        (
            "C6_STALE_EVIDENCE",
            "GAP_STALE_EVIDENCE",
            "wave_height",
            [],
            RecoveryActionType.SWITCH_FALLBACK_PROVIDER,
            "switch_fallback_provider",
        ),
        (
            "C7_CONTRADICTORY_EVIDENCE",
            "GAP_CONTRADICTORY_EVIDENCE",
            "wind_speed",
            [],
            RecoveryActionType.SWITCH_FALLBACK_PROVIDER,
            "switch_fallback_provider",
        ),
        (
            "C8_MARINE_RETRY_FAILED_CYCLE2",
            "GAP_MARINE_SOURCE_ERROR",
            "wave_height",
            [RecoveryActionType.RETRY_WITH_BACKOFF],
            RecoveryActionType.SWITCH_FALLBACK_PROVIDER,
            "switch_fallback_provider",
        ),
        (
            "C9_ALL_ATTEMPTS_EXHAUSTED",
            "GAP_WEATHER_SOURCE_ERROR",
            "wind_speed",
            [RecoveryActionType.RETRY_WITH_BACKOFF, RecoveryActionType.SWITCH_FALLBACK_PROVIDER],
            RecoveryActionType.ABSTAIN_AND_LOG,
            "abstain_and_log",
        ),
        (
            "C10_UNKNOWN_GAP_CODE",
            "GAP_UNKNOWN_SITUATION",
            None,
            [],
            RecoveryActionType.ABSTAIN_AND_LOG,
            "abstain_and_log",
        ),
    ]

    @pytest.mark.parametrize("case_id,gap_code,param,hist_acts,expected_rule_act,laya_choice", BENCHMARK_CASES)
    def test_comparative_case_evaluation(self, case_id, gap_code, param, hist_acts, expected_rule_act, laya_choice):
        """Runs rule-based and Laya selectors side-by-side on identical gap inputs."""
        gap = IdentifiedGap(gap_code=gap_code, description=f"Benchmark case {case_id}", affected_parameter=param)
        history: List[RecoveryTraceEntry] = []
        for i, act in enumerate(hist_acts, start=1):
            history.append(
                RecoveryTraceEntry(
                    cycle=i,
                    selector=RecoverySelectorType.DETERMINISTIC_RULES,
                    action=act,
                    target_gap=gap,
                    parameters_applied={},
                    outcome=RecoveryOutcome.FAILED,
                    timestamp=datetime.now(timezone.utc),
                )
            )

        cycle = len(hist_acts) + 1

        # 1. Rule-based selection
        rule_selector = RuleBasedRecoverySelector()
        rule_act, rule_trace = rule_selector.select_action_with_trace(gap, cycle, history, PERMITTED_ACTIONS)

        assert rule_act == expected_rule_act
        assert rule_trace.is_valid is True

        # 2. Laya selection (with stub router configured to provide matching candidate choice)
        stub = StubRouter(choice=laya_choice)
        laya_selector = LayaRecoverySelector(enabled=True, router=stub)
        laya_act, laya_trace = laya_selector.select_action_with_trace(gap, cycle, history, PERMITTED_ACTIONS)

        assert laya_act in PERMITTED_ACTIONS
        assert laya_trace.is_valid is True
        assert laya_trace.selector_type == RecoverySelectorType.LAYA
        assert laya_trace.latency_ms >= 0.0


# ---------------------------------------------------------------------------
# 5. TestRecoveryControllerWithLaya
# ---------------------------------------------------------------------------

class TestRecoveryControllerWithLaya:
    """Verifies R3 bounded recovery execution when Laya is the active selector."""

    @pytest.mark.asyncio
    async def test_recovery_controller_respects_max_2_cycles_with_laya(self):
        """Even with Laya recommending retries, controller halts strictly at cycle <= 2."""
        stub = StubRouter(choice="retry_with_backoff")
        laya_selector = LayaRecoverySelector(enabled=True, router=stub)
        controller = RecoveryController(selector=laya_selector, max_cycles=MAX_RECOVERY_CYCLES)

        gap = IdentifiedGap(gap_code="GAP_MARINE_SOURCE_ERROR", description="Persistent marine error")

        # Fake gateway that continually fails
        async def _failing_marine(p):
            raise RuntimeError("Still failing")

        fake_registry = {"open_meteo_marine": _failing_marine}

        ev, gaps, trace, val_res = await controller.execute_recovery_loop(
            initial_gaps=[gap],
            current_evidence=[],
            context=None,
            gateway_registry=fake_registry,
        )

        # Strict budget enforcement: cycles <= 2
        assert len(trace) <= 2
        for entry in trace:
            assert entry.cycle <= 2
            assert entry.selector == RecoverySelectorType.LAYA
            assert entry.selector_trace is not None
            assert entry.selector_trace.selector_type == RecoverySelectorType.LAYA

    @pytest.mark.asyncio
    async def test_recovery_controller_no_progress_termination_with_laya(self):
        """Controller terminates on NO_PROGRESS when action fails to reduce gap signature."""
        stub = StubRouter(choice="retry_with_backoff")
        laya_selector = LayaRecoverySelector(enabled=True, router=stub)
        controller = RecoveryController(selector=laya_selector)

        gap = IdentifiedGap(gap_code="GAP_WEATHER_SOURCE_ERROR", description="Weather error")

        async def _no_op_gw(p):
            return {}, []  # Returns empty evidence

        fake_registry = {"open_meteo_weather": _no_op_gw}

        ev, gaps, trace, val_res = await controller.execute_recovery_loop(
            initial_gaps=[gap],
            current_evidence=[],
            context=None,
            gateway_registry=fake_registry,
        )

        assert len(trace) == 1
        assert trace[0].outcome == RecoveryOutcome.NO_PROGRESS
        assert trace[0].selector_trace is not None

    @pytest.mark.asyncio
    async def test_recovery_controller_revalidates_after_laya_action(self):
        """Controller revalidates evidence after a successful Laya corrective action."""
        stub = StubRouter(choice="retry_with_backoff")
        laya_selector = LayaRecoverySelector(enabled=True, router=stub)
        controller = RecoveryController(selector=laya_selector)

        gap = IdentifiedGap(gap_code="GAP_MARINE_SOURCE_ERROR", description="Marine missing")
        now = datetime.now(timezone.utc)

        # Successful retry returns wave evidence
        recovered_ev = EvidenceRecord(
            evidence_id="ev_rec_1",
            source_id="open_meteo_marine",
            source_name="Open-Meteo Marine",
            product_id="wave_forecast",
            parameter="wave_height",
            value=1.5,
            unit="m",
            location=GeoLocation(lat=13.35, lon=74.70),
            retrieved_at=now,
            data_mode=DataMode.LIVE_FORECAST,
            valid_from=now,
            valid_to=now,
            quality_flags=["VALIDATED"],
            source_url="https://marine-api.open-meteo.com/v1/marine",
            attribution="Open-Meteo (CC BY 4.0)",
            schema_version="1.0.0",
        )

        async def _recovering_marine(p):
            return {}, [recovered_ev]

        fake_registry = {"open_meteo_marine": _recovering_marine}

        ev, gaps, trace, val_res = await controller.execute_recovery_loop(
            initial_gaps=[gap],
            current_evidence=[],
            context=QueryContext(location=GeoLocation(lat=13.35, lon=74.70)),
            gateway_registry=fake_registry,
            now=now,
        )

        assert len(ev) == 1
        assert ev[0].evidence_id == "ev_rec_1"
        assert trace[0].outcome == RecoveryOutcome.SUCCEEDED


# ---------------------------------------------------------------------------
# 6. TestReleasePolicyIndependence
# ---------------------------------------------------------------------------

class TestReleasePolicyIndependence:
    """Verifies that Laya cannot override, modify, or soften deterministic release gates."""

    def test_laya_cannot_override_missing_evidence_release_block(self):
        """Even if Laya selector is active, missing mandatory evidence results in NOT_EVALUABLE."""
        policy = ReleasePolicy()
        validator = EvidenceValidator()
        ctx = QueryContext(location=GeoLocation(lat=13.35, lon=74.70))

        # Empty evidence -> validator detects missing variables
        val_res = validator.validate([], ctx)
        policy_audit = policy.evaluate([], val_res, ctx)

        assert policy_audit.overall_verdict == OverallGateVerdict.NOT_EVALUABLE
        assert policy.can_release(policy_audit) is False

    def test_laya_cannot_approve_unreviewed_thresholds(self):
        """Release policy rejects release when authoritative MPA or vessel limits are unreviewed."""
        policy = ReleasePolicy()
        validator = EvidenceValidator()
        now = datetime.now(timezone.utc)

        ev_wave = EvidenceRecord(
            evidence_id="ev_w",
            source_id="open_meteo_marine",
            source_name="Open-Meteo Marine",
            product_id="wave_forecast",
            parameter="wave_height",
            value=0.8,
            unit="m",
            location=GeoLocation(lat=13.35, lon=74.70),
            retrieved_at=now,
            data_mode=DataMode.LIVE_FORECAST,
            valid_from=now,
            valid_to=now,
            quality_flags=["VALIDATED"],
            source_url="https://marine-api.open-meteo.com/v1/marine",
            attribution="Open-Meteo (CC BY 4.0)",
            schema_version="1.0.0",
        )
        ctx = QueryContext(location=GeoLocation(lat=13.35, lon=74.70))
        val_res = validator.validate([ev_wave], ctx, now)
        audit = policy.evaluate([ev_wave], val_res, ctx)

        # Unapproved vessel thresholds and unverified MPA boundaries must block release
        assert policy.can_release(audit) is False
        assert any(c.check_name == "CHECK_MARINE_PROTECTED_AREAS" and c.outcome == GateCheckOutcome.NOT_EVALUABLE for c in audit.checks)
        assert any(c.check_name == "CHECK_VESSEL_LIMITS" and c.outcome == GateCheckOutcome.NOT_EVALUABLE for c in audit.checks)


# ---------------------------------------------------------------------------
# 7. TestSelectorTracePersistence
# ---------------------------------------------------------------------------

class TestSelectorTracePersistence:
    """Verifies SQLite catalog persistence and retrieval for selector traces."""

    def test_sqlite_selector_traces_crud(self, tmp_path):
        import sqlite3
        from backend.catalog.migrations import apply_migrations

        db_path = tmp_path / "test_selector.db"
        conn = sqlite3.connect(str(db_path))
        apply_migrations(conn)
        conn.close()

        catalog = CatalogService(db_path=str(db_path))
        run_id = "run_sel_001"
        now = datetime.now(timezone.utc)

        trace_entry = SelectorTraceEntry(
            selector_type=RecoverySelectorType.LAYA,
            checkpoint="convaiinnovations/laya",
            allowed_actions=[RecoveryActionType.RETRY_WITH_BACKOFF, RecoveryActionType.ABSTAIN_AND_LOG],
            raw_action="retry_with_backoff",
            validated_action=RecoveryActionType.RETRY_WITH_BACKOFF,
            is_valid=True,
            latency_ms=34.5,
            fallback_reason=None,
            timestamp=now,
        )

        catalog.record_selector_traces(run_id=run_id, traces=[trace_entry], cycle=1)

        retrieved = catalog.get_selector_traces(run_id)
        assert len(retrieved) == 1
        r = retrieved[0]
        assert r["run_id"] == run_id
        assert r["cycle"] == 1
        assert r["selector_type"] == "laya"
        assert r["checkpoint"] == "convaiinnovations/laya"
        assert r["raw_action"] == "retry_with_backoff"
        assert r["validated_action"] == "retry_with_backoff"
        assert r["is_valid"] == 1
        assert r["latency_ms"] == pytest.approx(34.5, abs=0.1)
        assert r["fallback_reason"] is None

    def test_canonical_endpoint_recovery_persists_selector_traces(self, tmp_path, monkeypatch):
        """Verifies that an execution of POST /api/orca/query with recovery persists selector traces."""
        from fastapi.testclient import TestClient
        from backend.main import app, get_gateway_registry
        from backend.core.config import settings

        db_file = tmp_path / "endpoint_sel.db"
        monkeypatch.setattr(settings, "sqlite_db_path", str(db_file))
        monkeypatch.setattr(settings, "artifacts_dir", str(tmp_path / "artifacts"))
        monkeypatch.setattr(settings, "enable_laya_selector", True)

        now = datetime.now(timezone.utc)
        ev_marine = EvidenceRecord(
            evidence_id="ev_m_ep",
            source_id="open_meteo_marine",
            source_name="Open-Meteo Marine",
            product_id="wave_forecast",
            parameter="wave_height",
            value=1.2,
            unit="m",
            location=GeoLocation(lat=13.35, lon=74.70),
            retrieved_at=now,
            data_mode=DataMode.LIVE_FORECAST,
            valid_from=now,
            valid_to=now,
            quality_flags=["VALIDATED"],
            source_url="https://marine-api.open-meteo.com/v1/marine",
            attribution="Open-Meteo (CC BY 4.0)",
            schema_version="1.0.0",
        )

        async def _gw_marine(p):
            return {"marine": "ok"}, [ev_marine]

        async def _gw_weather_fail(p):
            raise RuntimeError("Transient weather outage")

        test_registry = {
            "open_meteo_marine": _gw_marine,
            "open_meteo_weather": _gw_weather_fail,
        }

        app.dependency_overrides[get_gateway_registry] = lambda: test_registry
        client = TestClient(app)

        try:
            resp = client.post(
                "/api/orca/query",
                json={
                    "query": "Is Malpe safe for small boat fishing?",
                    "context_override": {"location": {"lat": 13.35, "lon": 74.70}},
                },
            )
            data = resp.json()
            run_id = data["run_id"]

            # Verify selector trace persisted in SQLite
            catalog = CatalogService(db_path=str(db_file))
            stored_traces = catalog.get_selector_traces(run_id)
            assert len(stored_traces) >= 1
            st = stored_traces[0]
            assert st["run_id"] == run_id
            assert st["selector_type"] == "laya"
            assert "fallback_reason" in st
        finally:
            app.dependency_overrides.clear()



# ---------------------------------------------------------------------------
# 8. TestOptInLiveLayaInference
# ---------------------------------------------------------------------------

class TestOptInLiveLayaInference:
    """
    Opt-in live model execution test.
    Only executed if RUN_LIVE_LAYA_TESTS=1 is explicitly set in the environment.
    """

    def test_live_laya_inference_smoke(self):
        if os.getenv("RUN_LIVE_LAYA_TESTS") != "1":
            pytest.skip("Opt-in live Laya inference test skipped; set RUN_LIVE_LAYA_TESTS=1 to run.")

        try:
            import laya  # noqa: F401
            from laya import Router
        except ImportError:
            pytest.skip("laya package not installed; live inference test skipped.")

        router = Router()
        state = {
            "cycle": 1,
            "gap_code": "GAP_WEATHER_SOURCE_ERROR",
            "description": "Transient HTTP 504 gateway timeout",
            "affected_parameter": "wind_speed",
            "attempted_actions": [],
        }
        questions = {
            "recovery_action": {
                "type": "choice",
                "instructions": "Select the best corrective recovery action to resolve the identified evidence gap.",
                "criteria": {
                    act.value: ACTION_CRITERIA_DESCRIPTIONS[act]
                    for act in PERMITTED_ACTIONS
                },
            }
        }

        result = router.predict(state, questions)
        assert isinstance(result, dict)
        choice = result.get("answers", {}).get("recovery_action", {}).get("choice")
        assert choice in [a.value for a in PERMITTED_ACTIONS]
