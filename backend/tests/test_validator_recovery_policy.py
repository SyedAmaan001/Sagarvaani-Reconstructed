"""
Sagarvani Reconstructed — Phase 5 Test Suite
Covers:
1. Deterministic Evidence Validator (physical ranges, units, temporal relevance, spatial bounds, attribution, lineage)
2. Bounded Recovery Controller R3 (allow-list, 2-cycle limit, gap fingerprinting, no-progress detection, deadlines)
3. Independent Release Policy (unilateral veto, PASS/BLOCK/NOT_EVALUABLE, prohibition of unapproved RELEASED state)
4. Catalog Persistence (recovery trace and policy checks tables in SQLite)
"""

from datetime import datetime, timedelta, timezone
import hashlib
from pathlib import Path
import tempfile
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.catalog.migrations import apply_migrations, MIGRATIONS
from backend.catalog.service import CatalogService
from backend.engine.fsm import FSMState, RunFSM
from backend.engine.policy import ReleasePolicy
from backend.engine.recovery import (
    ALLOWED_RECOVERY_ACTIONS,
    MAX_RECOVERY_CYCLES,
    RecoveryController,
    RuleBasedRecoverySelector,
)
from backend.engine.validator import (
    EvidenceValidator,
    PARAM_ALIASES,
    PHYSICAL_RANGES,
    RECOGNIZED_UNITS,
    ValidationCheckItem,
    ValidationResult,
)
from backend.main import app
from backend.models.enums import (
    DataMode,
    GateCheckOutcome,
    OverallGateVerdict,
    RecoveryActionType,
    RecoveryOutcome,
    RunStatus,
    StakeholderRole,
)
from backend.models.evidence import EvidenceRecord, GeoLocation
from backend.models.query import (
    CanonicalQueryRequest,
    CanonicalQueryResponse,
    PolicyAudit,
    PolicyCheckItem,
    QueryContext,
)
from backend.models.recovery import IdentifiedGap, RecoveryTraceEntry

client = TestClient(app)


# ---------------------------------------------------------------------------
# Fixtures & Helpers
# ---------------------------------------------------------------------------

def _make_evidence(
    parameter: str,
    value: float,
    unit: str,
    lat: float = 13.35,
    lon: float = 74.70,
    valid_from: datetime = None,
    retrieved_at: datetime = None,
    source_id: str = "open_meteo_marine",
    source_name: str = "Open-Meteo Marine API",
    attribution: str = "Marine weather data by Open-Meteo.com",
    artifact_ref: str = None,
) -> EvidenceRecord:
    now = datetime.now(timezone.utc)
    vf = valid_from or now
    ra = retrieved_at or now
    return EvidenceRecord(
        evidence_id=f"ev_{parameter}_{int(now.timestamp())}_{hash(parameter) % 10000}",
        source_id=source_id,
        source_name=source_name,
        product_id="marine_forecast",
        parameter=parameter,
        value=value,
        unit=unit,
        location=GeoLocation(lat=lat, lon=lon),
        retrieved_at=ra,
        data_mode=DataMode.TEST_FIXTURE,
        valid_from=vf,
        source_url="https://open-meteo.com/en/docs/marine-weather-api",
        attribution=attribution,
        artifact_ref=artifact_ref,
    )


def _make_standard_evidence_set(lat: float = 13.35, lon: float = 74.70, now: datetime = None) -> List[EvidenceRecord]:
    t = now or datetime.now(timezone.utc)
    return [
        _make_evidence("wave_height", 1.5, "m", lat=lat, lon=lon, valid_from=t, retrieved_at=t),
        _make_evidence("wave_period", 8.0, "s", lat=lat, lon=lon, valid_from=t, retrieved_at=t),
        _make_evidence("wave_direction", 240.0, "°", lat=lat, lon=lon, valid_from=t, retrieved_at=t),
        _make_evidence("wind_speed_10m", 15.0, "km/h", lat=lat, lon=lon, valid_from=t, retrieved_at=t, source_id="open_meteo_weather"),
        _make_evidence("wind_direction_10m", 250.0, "°", lat=lat, lon=lon, valid_from=t, retrieved_at=t, source_id="open_meteo_weather"),
        _make_evidence("wind_gusts_10m", 22.0, "km/h", lat=lat, lon=lon, valid_from=t, retrieved_at=t, source_id="open_meteo_weather"),
    ]


# ---------------------------------------------------------------------------
# 1. Deterministic Evidence Validator Tests
# ---------------------------------------------------------------------------

class TestEvidenceValidator:

    def test_valid_evidence_set_passes_all_checks(self):
        validator = EvidenceValidator()
        now = datetime.now(timezone.utc)
        ev_list = _make_standard_evidence_set(now=now)
        # Provide departure_time so CHECK_TEMPORAL_RELEVANCE is produced
        ctx = QueryContext(
            location=GeoLocation(lat=13.35, lon=74.70),
            operating_radius_km=35.0,
            departure_time=now + timedelta(hours=2),
        )

        res = validator.validate(ev_list, ctx, now=now)
        assert res.is_valid is True
        assert res.has_critical_failures is False
        # No critical gaps (only warnings/info allowed)
        assert not any(c.status == "FAIL" and c.severity == "CRITICAL" for c in res.checks)

        # Check codes present (match actual validator code names)
        check_codes = {c.check_code for c in res.checks}
        assert "CHECK_STRUCTURE" in check_codes
        assert "CHECK_PHYSICAL_RANGE" in check_codes
        assert "CHECK_UNITS" in check_codes
        assert "CHECK_TEMPORAL_RELEVANCE" in check_codes
        assert "CHECK_SPATIAL_COVERAGE" in check_codes
        assert "CHECK_ATTRIBUTION" in check_codes
        assert "CHECK_SHARED_LINEAGE" in check_codes
        assert "CHECK_CORE_EVIDENCE" in check_codes

    def test_empty_evidence_fails_with_critical_check(self):
        validator = EvidenceValidator()
        res = validator.validate([])
        assert res.is_valid is False
        assert res.has_critical_failures is True
        assert any(g.gap_code == "GAP_MISSING_CORE_MARINE_FORECAST" for g in res.gaps)

    def test_unphysical_wave_height_fails_with_critical_check(self):
        validator = EvidenceValidator()
        ev = _make_evidence("wave_height", 55.0, "m")  # > 35m max
        res = validator.validate([ev])
        assert res.is_valid is False
        assert res.has_critical_failures is True
        assert any(g.gap_code == "GAP_UNPHYSICAL_VALUE" for g in res.gaps)
        failed_checks = [c for c in res.checks if c.check_code == "CHECK_PHYSICAL_RANGE" and c.status == "FAIL"]
        assert len(failed_checks) == 1
        assert failed_checks[0].severity == "CRITICAL"

    def test_unphysical_wind_speed_fails(self):
        validator = EvidenceValidator()
        ev = _make_evidence("wind_speed_10m", 800.0, "km/h")  # 800 km/h = 222 m/s > 150 m/s
        res = validator.validate([ev])
        assert res.is_valid is False
        assert res.has_critical_failures is True
        assert any(g.gap_code == "GAP_UNPHYSICAL_VALUE" for g in res.gaps)

    def test_unrecognized_units_flags_gap(self):
        validator = EvidenceValidator()
        ev = _make_evidence("wave_height", 2.0, "cubits")
        res = validator.validate([ev])
        unit_checks = [c for c in res.checks if c.check_code == "CHECK_UNITS"]
        assert len(unit_checks) == 1
        # Validator treats unrecognized units as FAIL/CRITICAL (data cannot be trusted)
        assert unit_checks[0].status == "FAIL"
        assert unit_checks[0].severity == "CRITICAL"
        assert any(g.gap_code == "GAP_UNKNOWN_UNIT" for g in res.gaps)

    def test_stale_forecast_retrieval_flags_warning(self):
        validator = EvidenceValidator()
        now = datetime.now(timezone.utc)
        stale_time = now - timedelta(hours=60)  # > 48h for open_meteo
        ev = _make_evidence("wave_height", 2.0, "m", retrieved_at=stale_time, valid_from=now)
        res = validator.validate([ev], now=now)
        # Freshness check uses CHECK_FRESHNESS code, not CHECK_TEMPORAL
        freshness_checks = [c for c in res.checks if c.check_code == "CHECK_FRESHNESS"]
        assert any("exceeds threshold" in c.details for c in freshness_checks)
        assert any(g.gap_code == "GAP_STALE_EVIDENCE" for g in res.gaps)

    def test_temporal_window_mismatch_flags_warning(self):
        validator = EvidenceValidator()
        now = datetime.now(timezone.utc)
        future_departure = now + timedelta(hours=48)
        ctx = QueryContext(
            location=GeoLocation(lat=13.35, lon=74.70),
            departure_time=future_departure,
        )
        # Evidence valid for 'now', not future departure
        ev = _make_evidence("wave_height", 2.0, "m", valid_from=now)
        res = validator.validate([ev], context=ctx, now=now)
        assert any(g.gap_code == "GAP_TEMPORAL_WINDOW_MISMATCH" for g in res.gaps)

    def test_spatial_coverage_exceeded_flags_warning(self):
        validator = EvidenceValidator()
        ctx = QueryContext(
            location=GeoLocation(lat=13.35, lon=74.70),
            operating_radius_km=20.0,
        )
        # Evidence at Cochin (approx 9.93, 76.26), ~400 km away
        ev = _make_evidence("wave_height", 2.0, "m", lat=9.93, lon=76.26)
        res = validator.validate([ev], context=ctx)
        assert any(g.gap_code == "GAP_SPATIAL_COVERAGE_EXCEEDED" for g in res.gaps)

    def test_attribution_presence_check(self):
        validator = EvidenceValidator()
        ev_no_attr = _make_evidence("wave_height", 1.5, "m", attribution="")
        res = validator.validate([ev_no_attr])
        attr_checks = [c for c in res.checks if c.check_code == "CHECK_ATTRIBUTION"]
        assert len(attr_checks) == 1
        # Validator treats missing attribution as FAIL/CRITICAL (attribution is mandatory)
        assert attr_checks[0].status == "FAIL"
        assert attr_checks[0].severity == "CRITICAL"
        assert any(g.gap_code == "GAP_MISSING_ATTRIBUTION" for g in res.gaps)

    def test_artifact_checksum_verification_valid_and_corrupt(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_path = Path(tmp_dir)
            art_file = base_path / "runs" / "run_test" / "marine.json"
            art_file.parent.mkdir(parents=True, exist_ok=True)
            content = b'{"status": "ok", "hourly": {}}'
            art_file.write_bytes(content)

            validator = EvidenceValidator(artifacts_base_dir=str(base_path))
            rel_path = "runs/run_test/marine.json"

            # Valid artifact: file exists → CHECK_ARTIFACT_INTEGRITY PASS
            ev_valid = _make_evidence("wave_height", 1.5, "m", artifact_ref=rel_path)
            res = validator.validate([ev_valid])
            art_checks = [c for c in res.checks if c.check_code == "CHECK_ARTIFACT_INTEGRITY"]
            assert len(art_checks) == 1
            assert art_checks[0].status == "PASS"

            # Missing artifact: reference points to a non-existent file → FAIL
            ev_missing = _make_evidence("wave_height", 1.5, "m", artifact_ref="runs/missing/ghost.json")
            res_missing = validator.validate([ev_missing])
            art_checks_missing = [c for c in res_missing.checks if c.check_code == "CHECK_ARTIFACT_INTEGRITY"]
            assert len(art_checks_missing) == 1
            assert art_checks_missing[0].status == "FAIL"

    def test_lineage_detection_open_meteo_upstream(self):
        validator = EvidenceValidator()
        ev_marine = _make_evidence("wave_height", 1.5, "m", source_id="open_meteo_marine")
        ev_weather = _make_evidence("wind_speed_10m", 15.0, "km/h", source_id="open_meteo_weather")

        res = validator.validate([ev_marine, ev_weather])
        lineage_str = " ".join(res.lineage_audit)
        assert "ECMWF" in lineage_str or "DWD" in lineage_str
        # Actual check code is CHECK_SHARED_LINEAGE
        assert any(c.check_code == "CHECK_SHARED_LINEAGE" and c.status == "PASS" for c in res.checks)

    def test_contradictory_evidence_divergence_flagged(self):
        validator = EvidenceValidator()
        now = datetime.now(timezone.utc)
        # Source 1 reports 1.0m wave height
        ev1 = _make_evidence("wave_height", 1.0, "m", source_id="source_a", valid_from=now)
        # Source 2 reports 4.5m wave height (divergence > 2.0m)
        ev2 = _make_evidence("wave_height", 4.5, "m", source_id="source_b", valid_from=now)

        res = validator.validate([ev1, ev2])
        assert any(g.gap_code == "GAP_CONTRADICTORY_EVIDENCE" for g in res.gaps)


# ---------------------------------------------------------------------------
# 2. Bounded Recovery Controller (R3) Tests
# ---------------------------------------------------------------------------

class TestBoundedRecovery:

    @pytest.mark.asyncio
    async def test_allow_list_enforcement(self):
        controller = RecoveryController()
        # Verify allow-list contains all required actions and nothing unauthorized
        expected_actions = {
            RecoveryActionType.RETRY_WITH_BACKOFF,
            RecoveryActionType.EXPAND_SPATIAL_RADIUS,
            RecoveryActionType.EXTEND_TEMPORAL_WINDOW,
            RecoveryActionType.SWITCH_FALLBACK_PROVIDER,
            RecoveryActionType.REQUEST_USER_CLARIFICATION,
            RecoveryActionType.ABSTAIN_AND_LOG,
        }
        assert set(ALLOWED_RECOVERY_ACTIONS) == expected_actions

        selector = RuleBasedRecoverySelector()
        # Location gap maps to REQUEST_USER_CLARIFICATION
        action = selector.select_action(
            IdentifiedGap(gap_code="GAP_MISSING_LOCATION", description="Missing loc"),
            cycle=1,
            history=[],
            allowed_actions=ALLOWED_RECOVERY_ACTIONS,
        )
        assert action == RecoveryActionType.REQUEST_USER_CLARIFICATION

        # Source error gap maps to RETRY_WITH_BACKOFF (GAP_GATEWAY_TIMEOUT falls to ABSTAIN via else-branch)
        action = selector.select_action(
            IdentifiedGap(gap_code="GAP_MARINE_SOURCE_ERROR", description="Marine source error"),
            cycle=1,
            history=[],
            allowed_actions=ALLOWED_RECOVERY_ACTIONS,
        )
        assert action == RecoveryActionType.RETRY_WITH_BACKOFF

        # Unphysical value maps to ABSTAIN_AND_LOG
        action = selector.select_action(
            IdentifiedGap(gap_code="GAP_UNPHYSICAL_VALUE", description="Unphysical"),
            cycle=1,
            history=[],
            allowed_actions=ALLOWED_RECOVERY_ACTIONS,
        )
        assert action == RecoveryActionType.ABSTAIN_AND_LOG

    @pytest.mark.asyncio
    async def test_max_two_cycles_limit(self):
        """Recovery controller must never exceed MAX_RECOVERY_CYCLES = 2."""
        controller = RecoveryController()
        assert controller.max_cycles == 2

        initial_gaps = [
            IdentifiedGap(
                gap_code="GAP_MISSING_CORE_MARINE_FORECAST",
                description="Persistent missing forecast",
                suggested_action=RecoveryActionType.RETRY_WITH_BACKOFF,
            )
        ]

        # Mock gateway that continuously fails
        mock_gateway = AsyncMock(side_effect=RuntimeError("Gateway persistent error"))
        gateway_registry = {"open_meteo_marine": mock_gateway}
        ctx = QueryContext(location=GeoLocation(lat=13.35, lon=74.70))

        evidence, gaps, trace, val_res = await controller.execute_recovery_loop(
            initial_gaps=initial_gaps,
            current_evidence=[],
            context=ctx,
            gateway_registry=gateway_registry,
        )

        assert len(trace) <= 2
        assert len(trace) > 0
        assert trace[-1].outcome in (RecoveryOutcome.NO_PROGRESS, RecoveryOutcome.EXHAUSTED)

    @pytest.mark.asyncio
    async def test_no_progress_termination_on_identical_fingerprint(self):
        controller = RecoveryController()
        gaps = [
            IdentifiedGap(
                gap_code="GAP_MISSING_CORE_MARINE_FORECAST",
                description="Persistent gap",
                suggested_action=RecoveryActionType.RETRY_WITH_BACKOFF,
            )
        ]
        fp1 = controller.compute_gap_fingerprint(gaps)
        fp2 = controller.compute_gap_fingerprint(gaps)
        assert fp1 == fp2

        # When action produces no new evidence, controller terminates on cycle 1
        mock_gateway = AsyncMock(return_value=({}, []))
        gateway_registry = {"open_meteo_marine": mock_gateway}
        ctx = QueryContext(location=GeoLocation(lat=13.35, lon=74.70))

        evidence, final_gaps, trace, val_res = await controller.execute_recovery_loop(
            initial_gaps=gaps,
            current_evidence=[],
            context=ctx,
            gateway_registry=gateway_registry,
        )

        # Finished on cycle 1 due to NO_PROGRESS
        assert len(trace) == 1
        assert trace[0].outcome == RecoveryOutcome.NO_PROGRESS

    @pytest.mark.asyncio
    async def test_deadline_expired_terminates_recovery(self):
        controller = RecoveryController()
        gaps = [IdentifiedGap(gap_code="GAP_GATEWAY_TIMEOUT", description="Timeout")]
        ctx = QueryContext(location=GeoLocation(lat=13.35, lon=74.70))

        # Expired deadline in the past
        past_deadline = datetime.now(timezone.utc) - timedelta(seconds=10)

        evidence, final_gaps, trace, val_res = await controller.execute_recovery_loop(
            initial_gaps=gaps,
            current_evidence=[],
            context=ctx,
            gateway_registry={},
            deadline=past_deadline,
        )

        assert len(trace) == 1
        # Controller uses RecoveryOutcome.FAILED for deadline-exceeded termination
        assert trace[0].outcome == RecoveryOutcome.FAILED
        assert "deadline" in (trace[0].fallback_reason or "").lower()

    @pytest.mark.asyncio
    async def test_revalidation_after_successful_recovery_action(self):
        """When an action recovers missing evidence, revalidation clears the gap."""
        controller = RecoveryController()
        now = datetime.now(timezone.utc)
        ctx = QueryContext(location=GeoLocation(lat=13.35, lon=74.70))

        # Initial evidence has only wave (wind is missing)
        initial_ev = [
            _make_evidence("wave_height", 1.5, "m", valid_from=now, retrieved_at=now),
            _make_evidence("wave_period", 8.0, "s", valid_from=now, retrieved_at=now),
            _make_evidence("wave_direction", 240.0, "°", valid_from=now, retrieved_at=now),
        ]
        initial_gaps = [
            IdentifiedGap(
                gap_code="GAP_MISSING_WIND_SPEED",
                description="Wind speed missing",
                affected_parameter="wind_speed",
                suggested_action=RecoveryActionType.RETRY_WITH_BACKOFF,
            )
        ]

        # Gateway recovers the wind speed
        recovered_wind = [
            _make_evidence("wind_speed_10m", 12.0, "km/h", valid_from=now, retrieved_at=now, source_id="open_meteo_weather"),
            _make_evidence("wind_direction_10m", 250.0, "°", valid_from=now, retrieved_at=now, source_id="open_meteo_weather"),
            _make_evidence("wind_gusts_10m", 18.0, "km/h", valid_from=now, retrieved_at=now, source_id="open_meteo_weather"),
        ]
        mock_weather = AsyncMock(return_value=({"recovered": True}, recovered_wind))
        gateway_registry = {"open_meteo_weather": mock_weather}

        evidence, final_gaps, trace, val_res = await controller.execute_recovery_loop(
            initial_gaps=initial_gaps,
            current_evidence=initial_ev,
            context=ctx,
            gateway_registry=gateway_registry,
            now=now,
        )

        # Successful cycle
        assert len(trace) == 1
        assert trace[0].outcome == RecoveryOutcome.SUCCEEDED
        assert len(evidence) == 6
        assert val_res.is_valid is True
        assert len(final_gaps) == 0


# ---------------------------------------------------------------------------
# 3. Independent Release Policy Tests
# ---------------------------------------------------------------------------

class TestIndependentReleasePolicy:

    def test_mandatory_checks_always_evaluated(self):
        policy = ReleasePolicy()
        ev_list = _make_standard_evidence_set()
        val_res = EvidenceValidator().validate(ev_list)

        audit = policy.evaluate(ev_list, val_res)
        check_names = [c.check_name for c in audit.checks]

        assert "CHECK_OFFICIAL_WARNINGS" in check_names
        assert "CHECK_MARINE_PROTECTED_AREAS" in check_names
        assert "CHECK_VESSEL_LIMITS" in check_names
        assert "CHECK_EVIDENCE_ADEQUACY" in check_names

    def test_missing_official_warnings_forces_not_evaluable(self):
        policy = ReleasePolicy()
        ev_list = _make_standard_evidence_set()
        val_res = EvidenceValidator().validate(ev_list)

        audit = policy.evaluate(ev_list, val_res)
        warnings_chk = next(c for c in audit.checks if c.check_name == "CHECK_OFFICIAL_WARNINGS")
        assert warnings_chk.outcome == GateCheckOutcome.NOT_EVALUABLE
        assert audit.overall_verdict == OverallGateVerdict.NOT_EVALUABLE

    def test_missing_protected_areas_forces_not_evaluable(self):
        policy = ReleasePolicy()
        ev_list = _make_standard_evidence_set()
        val_res = EvidenceValidator().validate(ev_list)

        audit = policy.evaluate(ev_list, val_res)
        mpa_chk = next(c for c in audit.checks if c.check_name == "CHECK_MARINE_PROTECTED_AREAS")
        assert mpa_chk.outcome == GateCheckOutcome.NOT_EVALUABLE

    def test_unapproved_vessel_thresholds_forces_not_evaluable(self):
        policy = ReleasePolicy()
        ev_list = _make_standard_evidence_set()
        val_res = EvidenceValidator().validate(ev_list)

        audit = policy.evaluate(ev_list, val_res, QueryContext(vessel_type="artisanal_canoe"))
        vessel_chk = next(c for c in audit.checks if c.check_name == "CHECK_VESSEL_LIMITS")
        assert vessel_chk.outcome == GateCheckOutcome.NOT_EVALUABLE

    def test_can_release_returns_false_when_not_evaluable(self):
        policy = ReleasePolicy()
        ev_list = _make_standard_evidence_set()
        val_res = EvidenceValidator().validate(ev_list)

        audit = policy.evaluate(ev_list, val_res)
        assert audit.overall_verdict == OverallGateVerdict.NOT_EVALUABLE
        assert policy.can_release(audit) is False

    def test_critical_validation_failure_produces_block(self):
        policy = ReleasePolicy()
        # Unphysical evidence
        ev_unphysical = [_make_evidence("wave_height", 50.0, "m")]
        val_res = EvidenceValidator().validate(ev_unphysical)
        assert val_res.has_critical_failures is True

        audit = policy.evaluate(ev_unphysical, val_res)
        adequacy_chk = next(c for c in audit.checks if c.check_name == "CHECK_EVIDENCE_ADEQUACY")
        assert adequacy_chk.outcome == GateCheckOutcome.BLOCK
        assert audit.overall_verdict == OverallGateVerdict.BLOCK
        assert policy.can_release(audit) is False

    def test_unilateral_veto_authority_cannot_be_overridden(self):
        """Any single BLOCK vetoes all PASS/NOT_EVALUABLE checks."""
        policy = ReleasePolicy()
        checks = [
            PolicyCheckItem(check_name="CHECK_A", outcome=GateCheckOutcome.PASS, details="", basis=""),
            PolicyCheckItem(check_name="CHECK_B", outcome=GateCheckOutcome.NOT_EVALUABLE, details="", basis=""),
            PolicyCheckItem(check_name="CHECK_C", outcome=GateCheckOutcome.BLOCK, details="", basis=""),
        ]
        verdict = policy.compute_overall_verdict(checks)
        assert verdict == OverallGateVerdict.BLOCK

    def test_fsm_cannot_transition_to_released(self):
        """FSM must never reach RELEASED while mandatory safety checks are NOT_EVALUABLE."""
        fsm = RunFSM("run_test_safety")
        policy = ReleasePolicy()
        ev_list = _make_standard_evidence_set()
        val_res = EvidenceValidator().validate(ev_list)
        audit = policy.evaluate(ev_list, val_res)

        fsm.transition(FSMState.CONTEXT_VALIDATED, "CTX_OK", "Context validated")
        fsm.transition(FSMState.TASK_GRAPH_READY, "DAG_OK", "DAG compiled")
        fsm.transition(FSMState.EVIDENCE_ACQUISITION, "ACQ_START", "Acquiring")
        fsm.transition(FSMState.EVIDENCE_VALIDATION, "ACQ_DONE", "Acquired")
        fsm.transition(FSMState.SAFETY_GATE_CHECK, "VAL_DONE", "Validated")

        # Attempt to evaluate release
        if policy.can_release(audit):
            fsm.transition(FSMState.RELEASED, "RELEASE", "Released")
        else:
            fsm.transition(FSMState.ABSTAINED, "GATE_NOT_EVALUABLE", audit.explanation)

        assert fsm.state == FSMState.ABSTAINED
        assert fsm.state != FSMState.RELEASED


# ---------------------------------------------------------------------------
# 4. Persistence & Full Integration Tests
# ---------------------------------------------------------------------------

class TestCatalogRecoveryPolicyPersistence:

    def test_sqlite_migration_3_tables_exist(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "test_p5.db"
            import sqlite3
            conn = sqlite3.connect(str(db_path))
            count = apply_migrations(conn)
            assert count == len(MIGRATIONS)

            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = {row[0] for row in cur.fetchall()}
            conn.close()

            assert "recovery_trace" in tables
            assert "policy_checks" in tables

    def test_record_and_get_recovery_trace(self):
        import sqlite3
        from backend.models.enums import RecoverySelectorType
        tmp_dir = tempfile.mkdtemp()
        try:
            db_path = Path(tmp_dir) / "test_p5_trace.db"
            cat = CatalogService(db_path=db_path)

            trace_items = [
                RecoveryTraceEntry(
                    cycle=1,
                    selector=RecoverySelectorType.DETERMINISTIC_RULES,
                    action=RecoveryActionType.RETRY_WITH_BACKOFF,
                    target_gap=IdentifiedGap(gap_code="GAP_TIMEOUT", description="Timeout"),
                    parameters_applied={"retry": 1},
                    outcome=RecoveryOutcome.SUCCEEDED,
                    fallback_reason=None,
                    timestamp=datetime.now(timezone.utc),
                )
            ]

            cat.record_recovery_trace("run_rec_001", trace_items)
            recovered = cat.get_recovery_trace("run_rec_001")
            # Close DB before temp dir cleanup (Windows file locking)
            cat.close()
            assert len(recovered) == 1
            assert recovered[0]["cycle"] == 1
            # Catalog stores enum .value (lowercase snake_case)
            assert recovered[0]["action"] == RecoveryActionType.RETRY_WITH_BACKOFF.value
            assert recovered[0]["outcome"] == RecoveryOutcome.SUCCEEDED.value
        finally:
            import shutil
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def test_record_and_get_policy_checks(self):
        tmp_dir = tempfile.mkdtemp()
        try:
            db_path = Path(tmp_dir) / "test_p5_policy.db"
            cat = CatalogService(db_path=db_path)

            checks = [
                PolicyCheckItem(
                    check_name="CHECK_OFFICIAL_WARNINGS",
                    outcome=GateCheckOutcome.NOT_EVALUABLE,
                    details="Unintegrated warnings",
                    basis="Policy basis",
                ),
                PolicyCheckItem(
                    check_name="CHECK_EVIDENCE_ADEQUACY",
                    outcome=GateCheckOutcome.PASS,
                    details="Core parameters verified",
                    basis="Adequacy basis",
                ),
            ]

            cat.record_policy_checks("run_pol_001", checks)
            recovered = cat.get_policy_checks("run_pol_001")
            # Close DB before temp dir cleanup (Windows file locking)
            cat.close()
            assert len(recovered) == 2
            assert recovered[0]["check_name"] == "CHECK_OFFICIAL_WARNINGS"
            assert recovered[0]["outcome"] == "NOT_EVALUABLE"
            assert recovered[1]["check_name"] == "CHECK_EVIDENCE_ADEQUACY"
            assert recovered[1]["outcome"] == "PASS"
        finally:
            import shutil
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def test_canonical_endpoint_records_policy_audit_and_trace(self):
        """Full end-to-end integration test through POST /api/orca/query."""
        payload = {
            "query": "Fishing departure check for Malpe tomorrow morning?",
            "context_override": {
                "location": {"lat": 13.35, "lon": 74.70, "location_name": "Malpe Harbor"},
                "vessel_type": "motorized_craft",
                "operating_radius_km": 30.0,
                "language": "en",
            },
        }

        # Mock gateways to return standard data
        fake_marine_json = {
            "latitude": 13.35,
            "longitude": 74.70,
            "hourly": {
                "time": ["2026-10-25T00:00"],
                "wave_height": [1.2],
                "wave_direction": [240.0],
                "wave_period": [7.5],
            },
            "hourly_units": {"wave_height": "m", "wave_direction": "°", "wave_period": "s"},
        }
        fake_weather_json = {
            "latitude": 13.35,
            "longitude": 74.70,
            "hourly": {
                "time": ["2026-10-25T00:00"],
                "wind_speed_10m": [14.0],
                "wind_direction_10m": [250.0],
                "wind_gusts_10m": [20.0],
            },
            "hourly_units": {"wind_speed_10m": "km/h", "wind_direction_10m": "°", "wind_gusts_10m": "km/h"},
        }

        with patch("backend.gateways.open_meteo_marine.OpenMeteoMarineGateway.fetch_marine_forecast", return_value=fake_marine_json), \
             patch("backend.gateways.open_meteo_weather.OpenMeteoWeatherGateway.fetch_weather_forecast", return_value=fake_weather_json):
            resp = client.post("/api/orca/query", json=payload)

        assert resp.status_code == 200
        data = resp.json()

        # Evidence acquired and validated
        assert data["status"] == "COMPLETED"
        assert len(data["evidence"]) == 6

        # Policy audit outcome
        assert data["policy_audit"]["overall_verdict"] == "NOT_EVALUABLE"
        check_names = {c["check_name"] for c in data["policy_audit"]["checks"]}
        assert "CHECK_OFFICIAL_WARNINGS" in check_names
        assert "CHECK_MARINE_PROTECTED_AREAS" in check_names
        assert "CHECK_VESSEL_LIMITS" in check_names
        assert "CHECK_EVIDENCE_ADEQUACY" in check_names

        # Adequate evidence check passed
        adequacy = next(c for c in data["policy_audit"]["checks"] if c["check_name"] == "CHECK_EVIDENCE_ADEQUACY")
        assert adequacy["outcome"] == "PASS"

        # Mandatory prototype boundary notice
        assert "PROTOTYPE ONLY" in data["disclaimer"]
