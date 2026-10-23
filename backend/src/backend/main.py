"""
Sagarvani Reconstructed — FastAPI Main Application (Phase 4)
Exposes health check and canonical query endpoints.
POST /api/orca/query now routes through the guarded FSM and concurrent task harness.
"""

import asyncio
from datetime import datetime, timedelta, timezone
import uuid
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.core.config import settings
from backend.engine.fsm import (
    DeadlineExceededError,
    FSMState,
    IllegalTransitionError,
    RunFSM,
    TerminalStateError,
)
from backend.engine.dag import TaskDAG, TaskDAGError
from backend.engine.harness import ExecutionHarness, GatewayCallable, HarnessResult
from backend.engine.validator import EvidenceValidator, ValidationResult
from backend.engine.recovery import RecoveryController, RuleBasedRecoverySelector
from backend.engine.policy import ReleasePolicy
from backend.models.enums import (
    DataMode,
    GateCheckOutcome,
    OverallGateVerdict,
    PresentationMode,
    RecoveryActionType,
    RunStatus,
    TaskStatus,
)
from backend.models.evidence import EvidenceRecord
from backend.models.query import (
    CanonicalQueryRequest,
    CanonicalQueryResponse,
    FieldCommunityProjection,
    MarineWarningItem,
    PolicyAudit,
    PolicyCheckItem,
    ProfessionalAnalysisProjection,
)
from backend.models.recovery import IdentifiedGap, RecoveryTraceEntry
from backend.models.task import TaskContract, TaskResult


class HealthResponse(BaseModel):
    status: str = Field(default="ok", description="Basic service availability status")
    app: str = Field(..., description="Application name")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(..., description="Current server time (UTC)")
    disclaimer: str = Field(
        default=(
            "Healthy basic server response. Does not indicate operational "
            "live marine data feeds or safety clearances."
        ),
        description="Health disclaimer",
    )


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Evidence-aware marine decision-intelligence backend API.",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Explicit CORS Origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check() -> HealthResponse:
    """Basic health check reporting backend service availability."""
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        version=settings.app_version,
        timestamp=datetime.now(timezone.utc),
    )


# ---------------------------------------------------------------------------
# Gateway async wrappers (production)
# These are passed into the harness registry and executed as async callables.
# Tests replace them with fakes via dependency injection.
# ---------------------------------------------------------------------------

async def _gateway_marine(params: Dict[str, Any]) -> tuple[Dict[str, Any], List[EvidenceRecord]]:
    """Async wrapper for OpenMeteoMarineGateway."""
    from backend.gateways.open_meteo_marine import OpenMeteoMarineGateway
    from backend.models.enums import DataMode

    gw = OpenMeteoMarineGateway()
    lat: float = params["lat"]
    lon: float = params["lon"]
    retrieved_at: datetime = params["retrieved_at"]
    target_dt: datetime = params.get("target_dt", retrieved_at)

    raw = await asyncio.to_thread(gw.fetch_marine_forecast, lat=lat, lon=lon)
    evidence = gw.parse_and_normalize(
        raw_payload=raw,
        requested_lat=lat,
        requested_lon=lon,
        retrieved_at=retrieved_at,
        data_mode=DataMode.LIVE_FORECAST,
        target_timestamp=target_dt,
    )
    return raw, evidence


async def _gateway_weather(params: Dict[str, Any]) -> tuple[Dict[str, Any], List[EvidenceRecord]]:
    """Async wrapper for OpenMeteoWeatherGateway."""
    from backend.gateways.open_meteo_weather import OpenMeteoWeatherGateway
    from backend.models.enums import DataMode

    gw = OpenMeteoWeatherGateway()
    lat: float = params["lat"]
    lon: float = params["lon"]
    retrieved_at: datetime = params["retrieved_at"]
    target_dt: datetime = params.get("target_dt", retrieved_at)

    raw = await asyncio.to_thread(gw.fetch_weather_forecast, lat=lat, lon=lon)
    evidence = gw.parse_and_normalize(
        raw_payload=raw,
        requested_lat=lat,
        requested_lon=lon,
        retrieved_at=retrieved_at,
        data_mode=DataMode.LIVE_FORECAST,
        target_timestamp=target_dt,
    )
    return raw, evidence


# Default production gateway registry
_PRODUCTION_REGISTRY: Dict[str, GatewayCallable] = {
    "open_meteo_marine": _gateway_marine,
    "open_meteo_weather": _gateway_weather,
}


def get_gateway_registry() -> Dict[str, GatewayCallable]:
    return _PRODUCTION_REGISTRY


# ---------------------------------------------------------------------------
# Canonical query endpoint
# ---------------------------------------------------------------------------

@app.post(
    "/api/orca/query",
    response_model=CanonicalQueryResponse,
    status_code=status.HTTP_200_OK,
    tags=["Canonical Decision Intelligence"],
)
async def canonical_orca_query(
    req: CanonicalQueryRequest,
    gateway_registry: Dict[str, GatewayCallable] = Depends(get_gateway_registry),
) -> CanonicalQueryResponse:
    """
    Canonical ORCA Query Endpoint (Phase 4 — FSM + DAG harness).

    Request routes through a guarded deterministic FSM.  Independent marine and
    weather retrieval tasks execute concurrently inside the execution harness.
    Missing context, gateway failures, timeouts and invalid DAGs all produce
    typed, auditable outcomes — never fabricated success.
    """
    now = datetime.now(timezone.utc)
    run_id = f"run_{uuid.uuid4().hex[:12]}"
    trace_id = f"tr_{uuid.uuid4().hex[:16]}"
    deadline = now + timedelta(seconds=settings.run_deadline_seconds)

    # ---- FSM initialisation -----------------------------------------------
    fsm = RunFSM(run_id=run_id, deadline=deadline)

    ctx = req.context_override

    # ---- REQUESTED → CONTEXT_VALIDATED (or ABSTAINED) ---------------------
    if ctx is None or ctx.location is None:
        fsm.transition(FSMState.ABSTAINED, "MISSING_LOCATION", "No geographic coordinates supplied")
        _persist_fsm(run_id, fsm, now)
        resp = _clarification_required_response(run_id, trace_id, req, ctx, now)
        _persist_run(resp, [], [], now, now)
        return resp

    try:
        fsm.transition(FSMState.CONTEXT_VALIDATED, "CONTEXT_OK", "Location and query context validated")
    except (IllegalTransitionError, DeadlineExceededError) as exc:
        resp = _fatal_fsm_response(run_id, trace_id, req, ctx, now, str(exc))
        _persist_run(resp, [], [], now, now)
        return resp

    # ---- CONTEXT_VALIDATED → TASK_GRAPH_READY -----------------------------
    target_dt = ctx.departure_time or now
    task_params = {"lat": ctx.location.lat, "lon": ctx.location.lon,
                   "retrieved_at": now, "target_dt": target_dt}

    contracts = [
        TaskContract(
            task_id="task_fetch_marine_forecast",
            task_name="Marine Forecast (Open-Meteo)",
            gateway_id="open_meteo_marine",
            dependencies=[],
            timeout_seconds=settings.gateway_timeout_seconds,
            parameters=task_params,
        ),
        TaskContract(
            task_id="task_fetch_weather_forecast",
            task_name="Weather Forecast (Open-Meteo)",
            gateway_id="open_meteo_weather",
            dependencies=[],
            timeout_seconds=settings.gateway_timeout_seconds,
            parameters=task_params,
        ),
    ]

    try:
        dag = TaskDAG(contracts)
    except TaskDAGError as exc:
        fsm.force_terminal(FSMState.FAILED, "DAG_INVALID", str(exc))
        _persist_fsm(run_id, fsm, now)
        resp = _build_error_response(run_id, trace_id, req, ctx, now, str(exc))
        _persist_run(resp, [], [], now, now)
        return resp

    try:
        fsm.transition(FSMState.TASK_GRAPH_READY, "DAG_VALIDATED", "Task graph validated")
    except (IllegalTransitionError, DeadlineExceededError) as exc:
        resp = _fatal_fsm_response(run_id, trace_id, req, ctx, now, str(exc))
        _persist_run(resp, [], [], now, now)
        return resp

    # ---- TASK_GRAPH_READY → EVIDENCE_ACQUISITION --------------------------
    try:
        fsm.transition(FSMState.EVIDENCE_ACQUISITION, "HARNESS_STARTED", "Concurrent task harness launched")
    except (IllegalTransitionError, DeadlineExceededError) as exc:
        resp = _fatal_fsm_response(run_id, trace_id, req, ctx, now, str(exc))
        _persist_run(resp, [], [], now, now)
        return resp

    harness = ExecutionHarness(
        dag=dag,
        registry=gateway_registry,
        max_concurrency=settings.max_task_concurrency,
        run_deadline=deadline,
    )

    harness_result: HarnessResult = await harness.execute()

    # Determine initial evidence / task results
    evidence_list = harness_result.evidence
    task_results = harness_result.task_results
    gaps_list: List[IdentifiedGap] = []
    recovery_trace: List[RecoveryTraceEntry] = []

    def _gap_code_for_task(task_id: str, is_timeout: bool = False) -> str:
        if "weather" in task_id:
            return "GAP_WEATHER_SOURCE_ERROR"
        if "marine" in task_id:
            return "GAP_MARINE_SOURCE_ERROR"
        return "GAP_TASK_TIMED_OUT" if is_timeout else "GAP_TASK_FAILED"

    if harness_result.failed_task_ids:
        for tid in harness_result.failed_task_ids:
            gaps_list.append(IdentifiedGap(
                gap_code=_gap_code_for_task(tid, is_timeout=False),
                description=f"Task '{tid}' failed during evidence acquisition.",
                suggested_action=RecoveryActionType.SWITCH_FALLBACK_PROVIDER,
            ))
    if harness_result.timed_out_task_ids:
        for tid in harness_result.timed_out_task_ids:
            gaps_list.append(IdentifiedGap(
                gap_code=_gap_code_for_task(tid, is_timeout=True),
                description=f"Task '{tid}' timed out.",
                suggested_action=RecoveryActionType.RETRY_WITH_BACKOFF,
            ))
    if harness_result.skipped_task_ids:
        for tid in harness_result.skipped_task_ids:
            gaps_list.append(IdentifiedGap(
                gap_code="GAP_TASK_SKIPPED",
                description=f"Task '{tid}' skipped due to failed prerequisites.",
                suggested_action=RecoveryActionType.ABSTAIN_AND_LOG,
            ))

    # ---- EVIDENCE_ACQUISITION → EVIDENCE_VALIDATION -----------------------
    if harness_result.timed_out_task_ids and not evidence_list:
        try:
            fsm.transition(FSMState.TIMED_OUT, "ALL_TASKS_TIMED_OUT", "No evidence acquired; all tasks timed out")
        except (IllegalTransitionError, TerminalStateError):
            pass
    elif not evidence_list:
        try:
            fsm.transition(FSMState.ABSTAINED, "NO_EVIDENCE", "No evidence acquired from any source")
        except (IllegalTransitionError, TerminalStateError):
            pass
    else:
        try:
            fsm.transition(FSMState.EVIDENCE_VALIDATION, "EVIDENCE_ACQUIRED", f"{len(evidence_list)} evidence items acquired")
        except (IllegalTransitionError, DeadlineExceededError):
            pass

    # ---- RUN EVIDENCE VALIDATOR -------------------------------------------
    validator = EvidenceValidator()
    val_res = validator.validate(evidence_list, ctx, now)
    
    # Merge validation gaps into gaps_list (preserving initial task errors without duplicating subsumed gaps)
    existing_gap_codes = {g.gap_code for g in gaps_list}
    has_weather_err = any("WEATHER" in c for c in existing_gap_codes)
    has_marine_err = any("MARINE" in c for c in existing_gap_codes)
    for vg in val_res.gaps:
        if has_weather_err and vg.gap_code in ("GAP_MISSING_WIND_SPEED", "GAP_MISSING_CORE_MARINE_FORECAST"):
            continue
        if has_marine_err and vg.gap_code in ("GAP_MISSING_WAVE_HEIGHT", "GAP_MISSING_CORE_MARINE_FORECAST"):
            continue
        if vg.gap_code not in existing_gap_codes:
            gaps_list.append(vg)
            existing_gap_codes.add(vg.gap_code)

    # ---- RECOVERY PLANNING (if gaps exist and state is EVIDENCE_VALIDATION)
    if gaps_list and fsm.state == FSMState.EVIDENCE_VALIDATION:
        try:
            fsm.transition(FSMState.RECOVERY_PLANNING, "GAPS_DETECTED", f"{len(gaps_list)} evidence gaps detected for recovery planning")
        except (IllegalTransitionError, DeadlineExceededError):
            pass

        recovery_controller = RecoveryController(validator=validator)
        evidence_list, gaps_list, recovery_trace, val_res = await recovery_controller.execute_recovery_loop(
            initial_gaps=gaps_list,
            current_evidence=evidence_list,
            context=ctx,
            gateway_registry=gateway_registry,
            deadline=deadline,
            now=now,
        )

        # Advance from RECOVERY_PLANNING to SAFETY_GATE_CHECK (or terminal state)
        if fsm.state == FSMState.RECOVERY_PLANNING:
            if not evidence_list:
                try:
                    fsm.transition(FSMState.ABSTAINED, "RECOVERY_EXHAUSTED", "Recovery completed without evidence")
                except (IllegalTransitionError, TerminalStateError):
                    pass
            else:
                try:
                    fsm.transition(FSMState.SAFETY_GATE_CHECK, "RECOVERY_DONE", "Recovery cycle completed; advancing to safety gate")
                except (IllegalTransitionError, DeadlineExceededError):
                    pass

    elif fsm.state == FSMState.EVIDENCE_VALIDATION:
        try:
            fsm.transition(FSMState.SAFETY_GATE_CHECK, "VALIDATION_PASSED", "Evidence validated; advancing to safety gate")
        except (IllegalTransitionError, DeadlineExceededError):
            pass

    # ---- INDEPENDENT RELEASE POLICY EVALUATION ---------------------------
    policy = ReleasePolicy()
    policy_audit = policy.evaluate(evidence_list, val_res, ctx)

    # ---- SAFETY_GATE_CHECK → RELEASED / BLOCKED / ABSTAINED ---------------
    if fsm.state == FSMState.SAFETY_GATE_CHECK:
        if policy.can_release(policy_audit):
            try:
                fsm.transition(FSMState.RELEASED, "POLICY_PASSED", "All safety gates passed")
            except (IllegalTransitionError, TerminalStateError):
                pass
        elif policy_audit.overall_verdict == OverallGateVerdict.BLOCK:
            try:
                fsm.transition(FSMState.BLOCKED, "POLICY_BLOCKED", "Safety gate blocked release")
            except (IllegalTransitionError, TerminalStateError):
                pass
        else:
            try:
                fsm.transition(
                    FSMState.ABSTAINED,
                    "GATE_NOT_EVALUABLE",
                    "Release gate NOT_EVALUABLE: required official bulletins and MPA geometries not integrated",
                )
            except (IllegalTransitionError, TerminalStateError):
                pass

    # ---- Persist FSM transitions ------------------------------------------
    completed_at = datetime.now(timezone.utc)
    _persist_fsm(run_id, fsm, now)

    # ---- Persist artifacts + run record ------------------------------------
    artifacts_meta = _save_raw_artifacts(run_id, harness_result)
    # Link artifact path into each evidence record
    for ev in evidence_list:
        for tr in task_results:
            if ev.evidence_id in tr.evidence_ids and tr.raw_artifact_path:
                ev.artifact_ref = tr.raw_artifact_path
                break

    # ---- Assemble response ------------------------------------------------
    lineage = list(val_res.lineage_audit) if val_res else []
    warnings: List[MarineWarningItem] = [
        MarineWarningItem(
            warning_code=chk.check_code,
            severity="WARNING",
            message=chk.details,
            source="deterministic_validator",
        )
        for chk in val_res.checks
        if chk.status == "WARN"
    ] if val_res else []

    response = _build_evidence_response(
        run_id=run_id,
        trace_id=trace_id,
        req=req,
        ctx=ctx,
        evidence_list=evidence_list,
        task_results=task_results,
        gaps_list=gaps_list,
        fsm_state=fsm.state,
        target_dt=target_dt,
        completed_at=completed_at,
        policy_audit=policy_audit,
        recovery_trace=recovery_trace,
        lineage_audit=lineage,
        warnings=warnings,
    )

    _persist_run(
        response=response,
        task_results=task_results,
        artifacts_meta=artifacts_meta,
        now=now,
        completed_at=completed_at,
    )

    return response


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _clarification_required_response(
    run_id: str,
    trace_id: str,
    req: CanonicalQueryRequest,
    ctx: Any,
    now: datetime,
) -> CanonicalQueryResponse:
    gap = IdentifiedGap(
        gap_code="GAP_MISSING_LOCATION",
        description="Operational coordinates or port location required for marine analysis.",
        suggested_action=RecoveryActionType.REQUEST_USER_CLARIFICATION,
    )
    policy_audit = PolicyAudit(
        overall_verdict=OverallGateVerdict.NOT_EVALUABLE,
        checks=[
            PolicyCheckItem(
                check_name="geospatial_bounds_check",
                outcome=GateCheckOutcome.NOT_EVALUABLE,
                details="Missing coordinates prevent spatial risk assessment.",
                basis="No spatial parameters provided in request.",
            ),
            PolicyCheckItem(
                check_name="marine_hazard_check",
                outcome=GateCheckOutcome.NOT_EVALUABLE,
                details="Cannot retrieve weather/wave conditions without geographic location.",
                basis="Location coordinates are null.",
            ),
        ],
        explanation="Safety policy checks are NOT_EVALUABLE: no geographic location specified.",
    )
    return CanonicalQueryResponse(
        run_id=run_id,
        trace_id=trace_id,
        status=RunStatus.CLARIFICATION_REQUIRED,
        data_mode=DataMode.NOT_AVAILABLE,
        query=req.query,
        extracted_context=ctx,
        evidence=[],
        warnings=[],
        gaps=[gap],
        recovery_trace=[],
        policy_audit=policy_audit,
        summary_text=(
            f"Query '{req.query}' cannot be processed: no operational location provided. "
            "Please specify coastal coordinates or a port name."
        ),
        field_view=FieldCommunityProjection(
            headline="Location Required",
            advisory_text="Please specify your departure harbor or coastal coordinates.",
            caution_flags=["MISSING_LOCATION"],
        ),
        professional_view=ProfessionalAnalysisProjection(
            scientific_summary="Request validation halted: missing geographic coordinates.",
            parameter_breakdown={},
            lineage_audit=[],
        ),
        timestamp=now,
    )


def _fatal_fsm_response(
    run_id: str, trace_id: str, req: CanonicalQueryRequest,
    ctx: Any, now: datetime, reason: str,
) -> CanonicalQueryResponse:
    return _build_error_response(run_id, trace_id, req, ctx, now, reason)


def _build_error_response(
    run_id: str, trace_id: str, req: CanonicalQueryRequest,
    ctx: Any, now: datetime, reason: str,
) -> CanonicalQueryResponse:
    return CanonicalQueryResponse(
        run_id=run_id,
        trace_id=trace_id,
        status=RunStatus.FAILED,
        data_mode=DataMode.NOT_AVAILABLE,
        query=req.query,
        extracted_context=ctx,
        evidence=[],
        warnings=[],
        gaps=[IdentifiedGap(
            gap_code="GAP_INTERNAL_ERROR",
            description=reason,
            suggested_action=RecoveryActionType.ABSTAIN_AND_LOG,
        )],
        recovery_trace=[],
        policy_audit=PolicyAudit(
            overall_verdict=OverallGateVerdict.NOT_EVALUABLE,
            checks=[],
            explanation=f"Run failed before evidence acquisition: {reason}",
        ),
        summary_text=f"Internal error: {reason}",
        field_view=FieldCommunityProjection(
            headline="Internal Error",
            advisory_text="An unexpected error occurred. Please retry.",
            caution_flags=["INTERNAL_ERROR"],
        ),
        professional_view=ProfessionalAnalysisProjection(
            scientific_summary=reason,
            parameter_breakdown={},
            lineage_audit=[],
        ),
        timestamp=now,
    )


def _build_evidence_response(
    run_id: str,
    trace_id: str,
    req: CanonicalQueryRequest,
    ctx: Any,
    evidence_list: List[EvidenceRecord],
    task_results: List[TaskResult],
    gaps_list: List[IdentifiedGap],
    fsm_state: FSMState,
    target_dt: datetime,
    completed_at: datetime,
    policy_audit: Optional[PolicyAudit] = None,
    recovery_trace: Optional[List[RecoveryTraceEntry]] = None,
    lineage_audit: Optional[List[str]] = None,
    warnings: Optional[List[MarineWarningItem]] = None,
) -> CanonicalQueryResponse:
    loc = ctx.location

    # Derive data_mode from evidence records: propagate lowest-fidelity mode upward.
    # TEST_FIXTURE overrides LIVE_FORECAST — an offline/mocked run must never report
    # as live. Priority (lowest wins): TEST_FIXTURE > HISTORICAL_REPLAY > LIVE_FORECAST.
    _MODE_PRIORITY = {
        DataMode.TEST_FIXTURE: 0,
        DataMode.HISTORICAL_REPLAY: 1,
        DataMode.LIVE_OBSERVATION: 2,
        DataMode.LIVE_FORECAST: 3,
        DataMode.NOT_AVAILABLE: 4,
    }
    if evidence_list:
        derived_mode = min(
            (ev.data_mode for ev in evidence_list),
            key=lambda m: _MODE_PRIORITY.get(m, 99),
        )
    else:
        derived_mode = DataMode.NOT_AVAILABLE

    if len(evidence_list) == 6:
        run_status = RunStatus.COMPLETED
        data_mode = derived_mode
        summary_text = (
            f"Retrieved 6 forecast variables for ({loc.lat:.2f}, {loc.lon:.2f}) from Open-Meteo. "
            f"Forecast valid for {target_dt.strftime('%Y-%m-%d %H:%M UTC')}."
        )
        head_text = "Forecast Evidence Ready"
        adv_text = "Atmospheric and wave forecasts retrieved. Consult official local bulletins before departure."
    elif evidence_list:
        run_status = RunStatus.PARTIAL
        data_mode = derived_mode
        summary_text = (
            f"Partial evidence retrieved ({len(evidence_list)} variables). Some sources were unavailable."
        )
        head_text = "Partial Evidence Available"
        adv_text = "Some weather/marine data is missing. Exercise caution."
    else:
        if fsm_state == FSMState.TIMED_OUT:
            run_status = RunStatus.TIMED_OUT
        else:
            run_status = RunStatus.SOURCE_UNAVAILABLE
        data_mode = DataMode.NOT_AVAILABLE
        summary_text = "Unable to retrieve real-time forecast evidence from Open-Meteo gateways."
        head_text = "Forecast Sources Unavailable"
        adv_text = "No forecast data could be retrieved. Decision withheld."

    # Use provided policy audit or default fallback
    audit = policy_audit or PolicyAudit(
        overall_verdict=OverallGateVerdict.NOT_EVALUABLE,
        checks=[],
        explanation="Default policy audit.",
    )

    param_dict = {ev.parameter: {"value": ev.value, "unit": ev.unit} for ev in evidence_list}

    lineage = list(lineage_audit) if lineage_audit else [
        "Open-Meteo Marine Weather API (ECMWF/DWD wave models)",
        "Open-Meteo Atmospheric Forecast API",
    ]

    return CanonicalQueryResponse(
        run_id=run_id,
        trace_id=trace_id,
        status=run_status,
        data_mode=data_mode,
        query=req.query,
        extracted_context=ctx,
        evidence=evidence_list,
        warnings=warnings or [],
        gaps=gaps_list,
        recovery_trace=recovery_trace or [],
        policy_audit=audit,
        summary_text=summary_text,
        field_view=FieldCommunityProjection(
            headline=head_text,
            advisory_text=adv_text,
            caution_flags=["UNVALIDATED_PROTOTYPE_RELEASE"],
        ),
        professional_view=ProfessionalAnalysisProjection(
            scientific_summary=f"Processed {len(evidence_list)} parameters via FSM-DAG harness.",
            parameter_breakdown=param_dict,
            lineage_audit=lineage,
        ),
        timestamp=completed_at,
    )


def _save_raw_artifacts(run_id: str, harness_result: HarnessResult) -> List[Dict[str, Any]]:
    """Persists raw response payloads to the artifact store and returns metadata list."""
    from backend.catalog.artifact_store import ArtifactStore
    artifact_store = ArtifactStore()
    artifacts_meta = []

    for tr in harness_result.task_results:
        raw = harness_result.raw_artifacts.get(tr.task_id)
        if raw is None:
            continue
        try:
            rel_path, checksum, byte_size = artifact_store.save_artifact(
                run_id=run_id,
                task_id=tr.task_id,
                payload=raw,
            )
            # Attach artifact path back onto the TaskResult for evidence linking
            object.__setattr__(tr, "raw_artifact_path", rel_path)
            artifacts_meta.append({
                "task_id": tr.task_id,
                "relative_path": rel_path,
                "checksum": checksum,
                "byte_size": byte_size,
            })
        except Exception:
            pass  # Non-blocking; artifact save failure does not fail the run

    return artifacts_meta


def _persist_fsm(run_id: str, fsm: RunFSM, now: datetime) -> None:
    """Persists FSM transition events into SQLite."""
    try:
        from backend.catalog.service import CatalogService
        svc = CatalogService()
        svc.record_fsm_transitions(run_id, fsm.events)
    except Exception:
        pass  # Non-blocking


def _persist_run(
    response: CanonicalQueryResponse,
    task_results: List[TaskResult],
    artifacts_meta: List[Dict[str, Any]],
    now: datetime,
    completed_at: datetime,
) -> None:
    """Persists run metadata, evidence, tasks, recovery trace, and policy checks via CatalogService."""
    try:
        from backend.catalog.service import CatalogService
        svc = CatalogService()
        svc.record_run(
            response=response,
            started_at=now,
            completed_at=completed_at,
            tasks=task_results,
            artifacts_meta=artifacts_meta,
        )
    except Exception:
        pass  # Non-blocking
