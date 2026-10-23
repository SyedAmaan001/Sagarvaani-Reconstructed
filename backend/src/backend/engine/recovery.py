"""
Sagarvani Reconstructed — Bounded Decision-Aware Recovery Controller (R3)
Manages targeted, budget-bounded corrective actions for identified evidence gaps.

Enforces:
- Maximum 2 recovery cycles per run (MAX_RECOVERY_CYCLES = 2).
- Strict allow-list of permitted actions.
- Progress detection via gap fingerprinting and action history tracking.
- Termination on no-progress, unrecoverable gap, budget exhaustion, or deadline exceeded.
- Revalidation after execution of recovery actions.
- Deterministic rules selector as the baseline active selector.
- Extensible RecoverySelector protocol for future Laya integration.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import hashlib
import time
from typing import Any, Callable, Dict, List, Optional, Protocol, Set, Tuple

from backend.core.config import settings
from backend.engine.harness import ExecutionHarness, GatewayCallable, HarnessResult
from backend.engine.validator import EvidenceValidator, ValidationResult
from backend.models.enums import (
    RecoveryActionType,
    RecoveryOutcome,
    RecoverySelectorType,
    TaskStatus,
)
from backend.models.evidence import EvidenceRecord
from backend.models.query import QueryContext
from backend.models.recovery import IdentifiedGap, RecoveryTraceEntry, SelectorTraceEntry
from backend.models.task import TaskContract, TaskResult


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_RECOVERY_CYCLES = 2

PERMITTED_ACTIONS: Set[RecoveryActionType] = {
    RecoveryActionType.RETRY_WITH_BACKOFF,
    RecoveryActionType.EXPAND_SPATIAL_RADIUS,
    RecoveryActionType.EXTEND_TEMPORAL_WINDOW,
    RecoveryActionType.SWITCH_FALLBACK_PROVIDER,
    RecoveryActionType.REQUEST_USER_CLARIFICATION,
    RecoveryActionType.ABSTAIN_AND_LOG,
}
ALLOWED_RECOVERY_ACTIONS = PERMITTED_ACTIONS


# ---------------------------------------------------------------------------
# Selectors (R1 / Rule-based)
# ---------------------------------------------------------------------------

class RecoverySelector(Protocol):
    """Protocol for recovery action selectors."""
    selector_type: RecoverySelectorType

    def select_action(
        self,
        gap: IdentifiedGap,
        cycle: int,
        history: List[RecoveryTraceEntry],
        allowed_actions: Set[RecoveryActionType],
    ) -> Optional[RecoveryActionType]:
        """Chooses one permitted recovery action for the targeted gap."""
        ...


class RuleBasedRecoverySelector:
    """
    Deterministic rule-based recovery selector.
    Baseline selector for Phase 5. Maps known gap codes directly to allow-listed actions.
    """
    selector_type: RecoverySelectorType = RecoverySelectorType.DETERMINISTIC_RULES

    def __init__(self) -> None:
        self.last_trace: Optional[SelectorTraceEntry] = None

    def _do_select(
        self,
        gap: IdentifiedGap,
        cycle: int,
        history: List[RecoveryTraceEntry],
        allowed_actions: Set[RecoveryActionType],
    ) -> Optional[RecoveryActionType]:
        code = gap.gap_code

        # Check if already attempted for this gap code
        attempted_actions = {h.action for h in history if h.target_gap.gap_code == code}

        chosen: Optional[RecoveryActionType] = None

        if code in ("GAP_WEATHER_SOURCE_ERROR", "GAP_MARINE_SOURCE_ERROR", "GAP_TASK_TIMED_OUT", "GAP_TASK_FAILED"):
            if RecoveryActionType.RETRY_WITH_BACKOFF not in attempted_actions:
                chosen = RecoveryActionType.RETRY_WITH_BACKOFF
            elif RecoveryActionType.SWITCH_FALLBACK_PROVIDER not in attempted_actions:
                chosen = RecoveryActionType.SWITCH_FALLBACK_PROVIDER
            else:
                chosen = RecoveryActionType.ABSTAIN_AND_LOG

        elif code == "GAP_SPATIAL_COVERAGE_EXCEEDED":
            if RecoveryActionType.EXPAND_SPATIAL_RADIUS not in attempted_actions:
                chosen = RecoveryActionType.EXPAND_SPATIAL_RADIUS
            else:
                chosen = RecoveryActionType.ABSTAIN_AND_LOG

        elif code == "GAP_TEMPORAL_WINDOW_MISMATCH":
            if RecoveryActionType.EXTEND_TEMPORAL_WINDOW not in attempted_actions:
                chosen = RecoveryActionType.EXTEND_TEMPORAL_WINDOW
            else:
                chosen = RecoveryActionType.ABSTAIN_AND_LOG

        elif code == "GAP_MISSING_LOCATION":
            chosen = RecoveryActionType.REQUEST_USER_CLARIFICATION

        elif code in ("GAP_STALE_EVIDENCE", "GAP_CONTRADICTORY_EVIDENCE"):
            if RecoveryActionType.SWITCH_FALLBACK_PROVIDER not in attempted_actions:
                chosen = RecoveryActionType.SWITCH_FALLBACK_PROVIDER
            else:
                chosen = RecoveryActionType.ABSTAIN_AND_LOG

        elif code in ("GAP_MISSING_WAVE_HEIGHT", "GAP_MISSING_WIND_SPEED", "GAP_MISSING_CORE_MARINE_FORECAST"):
            if RecoveryActionType.RETRY_WITH_BACKOFF not in attempted_actions:
                chosen = RecoveryActionType.RETRY_WITH_BACKOFF
            elif RecoveryActionType.SWITCH_FALLBACK_PROVIDER not in attempted_actions:
                chosen = RecoveryActionType.SWITCH_FALLBACK_PROVIDER
            else:
                chosen = RecoveryActionType.ABSTAIN_AND_LOG

        else:
            chosen = RecoveryActionType.ABSTAIN_AND_LOG

        # Ensure chosen action is in allow-list
        if chosen in allowed_actions:
            return chosen
        return None

    def select_action_with_trace(
        self,
        gap: IdentifiedGap,
        cycle: int,
        history: List[RecoveryTraceEntry],
        allowed_actions: Set[RecoveryActionType],
    ) -> Tuple[Optional[RecoveryActionType], SelectorTraceEntry]:
        start = time.perf_counter()
        chosen = self._do_select(gap, cycle, history, allowed_actions)
        latency = (time.perf_counter() - start) * 1000.0

        trace = SelectorTraceEntry(
            selector_type=self.selector_type,
            checkpoint=None,
            allowed_actions=sorted(list(allowed_actions), key=lambda a: a.value),
            raw_action=chosen.value if chosen else None,
            validated_action=chosen,
            is_valid=chosen is not None,
            latency_ms=round(latency, 2),
            fallback_reason=None,
            timestamp=datetime.now(timezone.utc),
        )
        self.last_trace = trace
        return chosen, trace

    def select_action(
        self,
        gap: IdentifiedGap,
        cycle: int,
        history: List[RecoveryTraceEntry],
        allowed_actions: Set[RecoveryActionType],
    ) -> Optional[RecoveryActionType]:
        action, _ = self.select_action_with_trace(gap, cycle, history, allowed_actions)
        return action


# ---------------------------------------------------------------------------
# Recovery Controller
# ---------------------------------------------------------------------------

class RecoveryController:
    """
    R3 — Bounded Decision-Aware Recovery Controller.
    Iteratively addresses evidence gaps, enforces strict cycle budgets (<= 2),
    detects lack of progress, and revalidates all evidence after each cycle.
    """

    def __init__(
        self,
        validator: Optional[EvidenceValidator] = None,
        selector: Optional[RecoverySelector] = None,
        max_cycles: int = MAX_RECOVERY_CYCLES,
    ):
        self.validator = validator or EvidenceValidator()
        if selector is not None:
            self.selector = selector
        elif getattr(settings, "enable_laya_selector", False):
            from backend.engine.laya_adapter import LayaRecoverySelector
            self.selector = LayaRecoverySelector()
        else:
            self.selector = RuleBasedRecoverySelector()
        self.max_cycles = max_cycles

    def compute_gap_fingerprint(self, gaps: List[IdentifiedGap]) -> str:
        """Computes a deterministic hash of current evidence gaps."""
        sorted_tuples = sorted((g.gap_code, g.affected_parameter or "") for g in gaps)
        raw = "|".join(f"{code}:{param}" for code, param in sorted_tuples)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    async def execute_recovery_loop(
        self,
        initial_gaps: List[IdentifiedGap],
        current_evidence: List[EvidenceRecord],
        context: Optional[QueryContext],
        gateway_registry: Dict[str, GatewayCallable],
        deadline: Optional[datetime] = None,
        now: Optional[datetime] = None,
    ) -> Tuple[List[EvidenceRecord], List[IdentifiedGap], List[RecoveryTraceEntry], ValidationResult]:
        """
        Executes bounded recovery cycles (max 2) until gaps are resolved,
        no progress is detected, or the budget expires.
        Returns:
            (final_evidence, final_gaps, recovery_trace, final_validation_result)
        """
        evidence = list(current_evidence)
        gaps = list(initial_gaps)
        trace: List[RecoveryTraceEntry] = []
        ref_time = now or datetime.now(timezone.utc)

        seen_fingerprints: Set[str] = set()

        # If there are no gaps, return immediately
        if not gaps:
            val_res = self.validator.validate(evidence, context, ref_time)
            return evidence, gaps, trace, val_res

        current_fingerprint = self.compute_gap_fingerprint(gaps)
        seen_fingerprints.add(current_fingerprint)

        cycle = 1
        while cycle <= self.max_cycles:
            # 1. Deadline check
            if deadline and datetime.now(timezone.utc) > deadline:
                trace.append(RecoveryTraceEntry(
                    cycle=cycle,
                    selector=self.selector.selector_type,
                    action=RecoveryActionType.ABSTAIN_AND_LOG,
                    target_gap=gaps[0],
                    parameters_applied={"reason": "deadline_exceeded"},
                    outcome=RecoveryOutcome.FAILED,
                    fallback_reason="Run wall-clock deadline exceeded",
                    selector_trace=None,
                    timestamp=datetime.now(timezone.utc),
                ))
                break

            # 2. Pick target gap
            target_gap = gaps[0]

            # 3. Select action from allow-list with trace
            sel_trace: Optional[SelectorTraceEntry] = None
            if hasattr(self.selector, "select_action_with_trace"):
                action, sel_trace = self.selector.select_action_with_trace(
                    target_gap,
                    cycle,
                    trace,
                    PERMITTED_ACTIONS,
                )
            else:
                action = self.selector.select_action(
                    target_gap,
                    cycle,
                    trace,
                    PERMITTED_ACTIONS,
                )
                sel_trace = getattr(self.selector, "last_trace", None)

            if not action:
                trace.append(RecoveryTraceEntry(
                    cycle=cycle,
                    selector=self.selector.selector_type,
                    action=RecoveryActionType.ABSTAIN_AND_LOG,
                    target_gap=target_gap,
                    parameters_applied={},
                    outcome=RecoveryOutcome.EXHAUSTED,
                    fallback_reason="No allowed action selectable for gap",
                    selector_trace=sel_trace,
                    timestamp=datetime.now(timezone.utc),
                ))
                break

            # 4. Check if terminal action selected
            if action in (RecoveryActionType.ABSTAIN_AND_LOG, RecoveryActionType.REQUEST_USER_CLARIFICATION):
                trace.append(RecoveryTraceEntry(
                    cycle=cycle,
                    selector=self.selector.selector_type,
                    action=action,
                    target_gap=target_gap,
                    parameters_applied={},
                    outcome=RecoveryOutcome.SUCCEEDED if action == RecoveryActionType.REQUEST_USER_CLARIFICATION else RecoveryOutcome.EXHAUSTED,
                    fallback_reason=None,
                    selector_trace=sel_trace,
                    timestamp=datetime.now(timezone.utc),
                ))
                break

            # 5. Execute corrective action
            new_evidence_items, action_params = await self._execute_action(
                action, target_gap, context, gateway_registry, cycle
            )

            # Merge new evidence (replace existing if duplicate evidence_id/parameter)
            if new_evidence_items:
                ev_dict = {f"{e.source_id}_{e.parameter}": e for e in evidence}
                for ne in new_evidence_items:
                    ev_dict[f"{ne.source_id}_{ne.parameter}"] = ne
                evidence = list(ev_dict.values())

            # 6. Revalidation
            val_res = self.validator.validate(evidence, context, ref_time)
            initial_task_gaps = [
                g for g in initial_gaps
                if g.gap_code.startswith("GAP_TASK_")
                or g.gap_code.endswith("_SOURCE_ERROR")
                or g.gap_code.endswith("_TIMEOUT")
            ]
            remaining_task_gaps = []
            for tg in initial_task_gaps:
                if "WEATHER" in tg.gap_code:
                    has_weather = any(e.source_id == "open_meteo_weather" for e in evidence)
                    if not has_weather:
                        remaining_task_gaps.append(tg)
                elif "MARINE" in tg.gap_code:
                    has_marine = any(e.source_id == "open_meteo_marine" for e in evidence)
                    if not has_marine:
                        remaining_task_gaps.append(tg)
                else:
                    remaining_task_gaps.append(tg)

            combined_gaps = list(remaining_task_gaps)
            for vg in val_res.gaps:
                if any("WEATHER" in tg.gap_code for tg in remaining_task_gaps) and vg.gap_code in ("GAP_MISSING_WIND_SPEED", "GAP_MISSING_CORE_MARINE_FORECAST"):
                    continue
                if any("MARINE" in tg.gap_code for tg in remaining_task_gaps) and vg.gap_code in ("GAP_MISSING_WAVE_HEIGHT", "GAP_MISSING_CORE_MARINE_FORECAST"):
                    continue
                if vg.gap_code not in {g.gap_code for g in combined_gaps}:
                    combined_gaps.append(vg)
            new_gaps = combined_gaps
            new_fingerprint = self.compute_gap_fingerprint(new_gaps)

            # 7. Progress evaluation
            if new_fingerprint in seen_fingerprints or (len(new_gaps) >= len(gaps) and not new_evidence_items):
                outcome = RecoveryOutcome.NO_PROGRESS
                trace.append(RecoveryTraceEntry(
                    cycle=cycle,
                    selector=self.selector.selector_type,
                    action=action,
                    target_gap=target_gap,
                    parameters_applied=action_params,
                    outcome=outcome,
                    fallback_reason="Action produced no new evidence or identical gap signature",
                    selector_trace=sel_trace,
                    timestamp=datetime.now(timezone.utc),
                ))
                gaps = new_gaps
                break

            outcome = RecoveryOutcome.SUCCEEDED
            trace.append(RecoveryTraceEntry(
                cycle=cycle,
                selector=self.selector.selector_type,
                action=action,
                target_gap=target_gap,
                parameters_applied=action_params,
                outcome=outcome,
                fallback_reason=None,
                selector_trace=sel_trace,
                timestamp=datetime.now(timezone.utc),
            ))

            gaps = new_gaps
            seen_fingerprints.add(new_fingerprint)

            if not gaps or val_res.is_valid:
                # Gaps fully resolved
                break

            cycle += 1

        final_validation = self.validator.validate(evidence, context, ref_time)
        return evidence, gaps, trace, final_validation

    async def _execute_action(
        self,
        action: RecoveryActionType,
        gap: IdentifiedGap,
        context: Optional[QueryContext],
        gateway_registry: Dict[str, GatewayCallable],
        cycle: int,
    ) -> Tuple[List[EvidenceRecord], Dict[str, Any]]:
        """Executes a single allow-listed recovery action against the gateway registry."""
        params_applied: Dict[str, Any] = {"action": action.value, "cycle": cycle}
        collected_evidence: List[EvidenceRecord] = []

        now = datetime.now(timezone.utc)
        lat = context.location.lat if context and context.location else 13.35
        lon = context.location.lon if context and context.location else 74.70

        if action == RecoveryActionType.RETRY_WITH_BACKOFF:
            # Determine which gateway to retry based on affected parameter or gap code
            target_gw = "open_meteo_marine"
            if gap.affected_parameter in ("wind_speed", "wind_gusts") or "WEATHER" in gap.gap_code:
                target_gw = "open_meteo_weather"

            gw_fn = gateway_registry.get(target_gw)
            params_applied["gateway_id"] = target_gw
            params_applied["backoff_seconds"] = 0.05 * cycle

            # Small bounded backoff
            await asyncio.sleep(0.05 * cycle)

            if gw_fn:
                try:
                    payload, ev_list = await gw_fn({
                        "lat": lat, "lon": lon,
                        "retrieved_at": now, "target_dt": now,
                    })
                    collected_evidence.extend(ev_list)
                except Exception as exc:
                    params_applied["retry_error"] = str(exc)

        elif action == RecoveryActionType.EXPAND_SPATIAL_RADIUS:
            # Query with slightly wider search / radius
            params_applied["expanded_radius_km"] = (context.operating_radius_km or 35.0) * 1.5
            gw_fn = gateway_registry.get("open_meteo_marine")
            if gw_fn:
                try:
                    payload, ev_list = await gw_fn({
                        "lat": lat, "lon": lon,
                        "retrieved_at": now, "target_dt": now,
                        "radius_km": params_applied["expanded_radius_km"],
                    })
                    collected_evidence.extend(ev_list)
                except Exception as exc:
                    params_applied["error"] = str(exc)

        elif action == RecoveryActionType.EXTEND_TEMPORAL_WINDOW:
            params_applied["extended_hours"] = 48
            gw_fn = gateway_registry.get("open_meteo_marine")
            if gw_fn:
                try:
                    payload, ev_list = await gw_fn({
                        "lat": lat, "lon": lon,
                        "retrieved_at": now, "target_dt": now,
                    })
                    collected_evidence.extend(ev_list)
                except Exception as exc:
                    params_applied["error"] = str(exc)

        elif action == RecoveryActionType.SWITCH_FALLBACK_PROVIDER:
            # Check if fallback provider is registered
            fallback_gw = gateway_registry.get("fallback_marine") or gateway_registry.get("fallback_weather")
            if fallback_gw:
                params_applied["fallback_invoked"] = True
                try:
                    payload, ev_list = await fallback_gw({
                        "lat": lat, "lon": lon,
                        "retrieved_at": now, "target_dt": now,
                    })
                    collected_evidence.extend(ev_list)
                except Exception as exc:
                    params_applied["fallback_error"] = str(exc)
            else:
                params_applied["fallback_available"] = False

        return collected_evidence, params_applied
