"""
Sagarvani Reconstructed — Laya Decision Adapter (R1)
Experimental non-autoregressive decision selector for bounded recovery.

Responsibilities:
- Evaluates evidence gaps using Laya's non-autoregressive System 1 decision engine.
- Strictly maps discrete decisions onto the closed allow-list (PERMITTED_ACTIONS).
- Operates behind the ENABLE_LAYA_SELECTOR feature flag (default: False).
- Completely fail-closed: falls back to RuleBasedRecoverySelector on:
    * Feature flag disabled
    * Missing dependency (laya / torch)
    * Checkpoint loading / initialization failure
    * Wall-clock inference timeout
    * Malformed, missing, or unknown model outputs
- Validates every candidate action against allowed_actions.
- Captures structured SelectorTraceEntry audit logs without hidden chain-of-thought.
- Does NOT execute actions (delegated to R3 Execution / RecoveryController).
- Cannot override release gates or fabricate safe verdicts.
"""

from __future__ import annotations

import concurrent.futures
from datetime import datetime, timezone
import time
from typing import Any, Dict, List, Optional, Set, Tuple

from backend.core.config import settings
from backend.models.enums import RecoveryActionType, RecoverySelectorType
from backend.models.recovery import IdentifiedGap, RecoveryTraceEntry, SelectorTraceEntry


# Canonical descriptions for allow-listed recovery actions provided to Laya's criteria
ACTION_CRITERIA_DESCRIPTIONS: Dict[RecoveryActionType, str] = {
    RecoveryActionType.RETRY_WITH_BACKOFF: (
        "Transient network failure, gateway timeout, or temporary HTTP 5xx error."
    ),
    RecoveryActionType.EXPAND_SPATIAL_RADIUS: (
        "Spatial coverage exceeded or data points not found in narrow immediate radius."
    ),
    RecoveryActionType.EXTEND_TEMPORAL_WINDOW: (
        "Forecast time window mismatch or temporal coverage gap."
    ),
    RecoveryActionType.SWITCH_FALLBACK_PROVIDER: (
        "Primary data source stale, persistent errors, contradictory data, or unavailable."
    ),
    RecoveryActionType.REQUEST_USER_CLARIFICATION: (
        "Missing critical user inputs such as coordinates, operating port, or vessel type."
    ),
    RecoveryActionType.LOAD_HISTORICAL_ANALOG: (
        "Offline historical analog dataset available for comparison."
    ),
    RecoveryActionType.ABSTAIN_AND_LOG: (
        "Unrecoverable gap, no progress possible, safety boundary, or repeated failures."
    ),
}


class LayaRecoverySelector:
    """
    R1 — Laya Decision Adapter.
    Translates an identified evidence gap and permitted recovery actions into a typed
    Laya question, runs inference with strict timeouts and fallbacks, validates the
    choice against the allow-list, and produces an auditable selector trace.
    """
    selector_type: RecoverySelectorType = RecoverySelectorType.LAYA

    def __init__(
        self,
        enabled: Optional[bool] = None,
        checkpoint: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        fallback_selector: Optional[Any] = None,
        router: Any = None,
    ):
        self.enabled = enabled if enabled is not None else settings.enable_laya_selector
        self.checkpoint = checkpoint or settings.laya_model_checkpoint
        self.timeout_seconds = timeout_seconds if timeout_seconds is not None else settings.laya_timeout_seconds
        
        # Lazy fallback selector instance to avoid circular imports
        if fallback_selector is not None:
            self.fallback_selector = fallback_selector
        else:
            from backend.engine.recovery import RuleBasedRecoverySelector
            self.fallback_selector = RuleBasedRecoverySelector()
            
        self._router = router
        self.last_trace: Optional[SelectorTraceEntry] = None

    def build_state(
        self,
        gap: IdentifiedGap,
        cycle: int,
        history: List[RecoveryTraceEntry],
    ) -> Dict[str, Any]:
        """Constructs a compact, structured recovery state representation for Laya."""
        attempted = [h.action.value for h in history if h.target_gap.gap_code == gap.gap_code]
        return {
            "cycle": cycle,
            "gap_code": gap.gap_code,
            "description": gap.description,
            "affected_parameter": gap.affected_parameter or "none",
            "attempted_actions": attempted,
        }

    def build_questions(
        self,
        allowed_actions: Set[RecoveryActionType],
    ) -> Dict[str, Any]:
        """Builds a typed choice question mapping each allowed recovery action to its criteria."""
        criteria: Dict[str, str] = {}
        for act in sorted(allowed_actions, key=lambda a: a.value):
            criteria[act.value] = ACTION_CRITERIA_DESCRIPTIONS.get(
                act, f"Execute corrective action: {act.value}"
            )

        return {
            "recovery_action": {
                "type": "choice",
                "instructions": (
                    "Select the single most effective corrective recovery action "
                    "to resolve the identified marine evidence gap."
                ),
                "criteria": criteria,
            }
        }

    def validate_choice(
        self,
        raw_choice: Any,
        allowed_actions: Set[RecoveryActionType],
    ) -> Optional[RecoveryActionType]:
        """Validates that the model's raw selection is an allowed, valid RecoveryActionType."""
        if not raw_choice or not isinstance(raw_choice, str):
            return None
        try:
            candidate = RecoveryActionType(raw_choice.strip().lower())
            if candidate in allowed_actions:
                return candidate
        except (ValueError, KeyError):
            return None
        return None

    def _get_or_create_router(self) -> Any:
        """Lazily imports and instantiates Laya's Router or raises ImportError / RuntimeError."""
        if self._router is not None:
            return self._router

        import laya  # noqa: F401
        from laya import Router

        # Instantiate Router with configured checkpoint
        self._router = Router(models={"english": self.checkpoint})
        return self._router

    def select_action_with_trace(
        self,
        gap: IdentifiedGap,
        cycle: int,
        history: List[RecoveryTraceEntry],
        allowed_actions: Set[RecoveryActionType],
    ) -> Tuple[Optional[RecoveryActionType], SelectorTraceEntry]:
        """
        Selects a permitted recovery action using Laya when enabled, falling back
        safely to RuleBasedRecoverySelector on any failure or invalid output.
        Returns (action, selector_trace).
        """
        start_time = time.perf_counter()
        now = datetime.now(timezone.utc)
        sorted_allowed = sorted(list(allowed_actions), key=lambda a: a.value)

        # 1. Check feature flag
        if not self.enabled:
            fb_action, _ = self.fallback_selector.select_action_with_trace(
                gap, cycle, history, allowed_actions
            )
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            trace = SelectorTraceEntry(
                selector_type=self.selector_type,
                checkpoint=self.checkpoint,
                allowed_actions=sorted_allowed,
                raw_action=None,
                validated_action=fb_action,
                is_valid=False,
                latency_ms=round(elapsed_ms, 2),
                fallback_reason="Laya selector disabled by feature flag ENABLE_LAYA_SELECTOR=False",
                timestamp=now,
            )
            self.last_trace = trace
            return fb_action, trace

        # 2. Check and acquire Router instance (lazy import)
        try:
            router = self._get_or_create_router()
        except ImportError as exc:
            fb_action, _ = self.fallback_selector.select_action_with_trace(
                gap, cycle, history, allowed_actions
            )
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            trace = SelectorTraceEntry(
                selector_type=self.selector_type,
                checkpoint=self.checkpoint,
                allowed_actions=sorted_allowed,
                raw_action=None,
                validated_action=fb_action,
                is_valid=False,
                latency_ms=round(elapsed_ms, 2),
                fallback_reason=f"laya dependency not installed: {exc}",
                timestamp=now,
            )
            self.last_trace = trace
            return fb_action, trace
        except Exception as exc:
            fb_action, _ = self.fallback_selector.select_action_with_trace(
                gap, cycle, history, allowed_actions
            )
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            trace = SelectorTraceEntry(
                selector_type=self.selector_type,
                checkpoint=self.checkpoint,
                allowed_actions=sorted_allowed,
                raw_action=None,
                validated_action=fb_action,
                is_valid=False,
                latency_ms=round(elapsed_ms, 2),
                fallback_reason=f"Failed to initialize Laya model: {exc}",
                timestamp=now,
            )
            self.last_trace = trace
            return fb_action, trace

        # 3. Build input state and typed question schema
        state = self.build_state(gap, cycle, history)
        questions = self.build_questions(allowed_actions)

        # 4. Execute prediction under timeout
        raw_choice: Optional[str] = None
        inference_error: Optional[str] = None

        def _predict_call() -> Any:
            return router.predict(state, questions)

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_predict_call)
                pred_result = future.result(timeout=self.timeout_seconds)

            # Extract choice from prediction response
            if isinstance(pred_result, dict):
                answers = pred_result.get("answers", {})
                q_ans = answers.get("recovery_action", {})
                if isinstance(q_ans, dict):
                    raw_choice = q_ans.get("choice")
                elif isinstance(q_ans, str):
                    raw_choice = q_ans
            elif hasattr(pred_result, "choice"):
                raw_choice = getattr(pred_result, "choice")
            elif isinstance(pred_result, str):
                raw_choice = pred_result

        except concurrent.futures.TimeoutError:
            inference_error = f"Laya inference timed out after {self.timeout_seconds}s"
        except Exception as exc:
            inference_error = f"Laya inference error: {exc}"

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        # 5. Handle inference errors with fallback
        if inference_error:
            fb_action, _ = self.fallback_selector.select_action_with_trace(
                gap, cycle, history, allowed_actions
            )
            trace = SelectorTraceEntry(
                selector_type=self.selector_type,
                checkpoint=self.checkpoint,
                allowed_actions=sorted_allowed,
                raw_action=raw_choice,
                validated_action=fb_action,
                is_valid=False,
                latency_ms=round(elapsed_ms, 2),
                fallback_reason=inference_error,
                timestamp=now,
            )
            self.last_trace = trace
            return fb_action, trace

        # 6. Validate selected choice against allow-list
        validated = self.validate_choice(raw_choice, allowed_actions)
        if validated is not None:
            # Model selection passed validation
            trace = SelectorTraceEntry(
                selector_type=self.selector_type,
                checkpoint=self.checkpoint,
                allowed_actions=sorted_allowed,
                raw_action=str(raw_choice) if raw_choice is not None else None,
                validated_action=validated,
                is_valid=True,
                latency_ms=round(elapsed_ms, 2),
                fallback_reason=None,
                timestamp=now,
            )
            self.last_trace = trace
            return validated, trace

        # 7. Model selection was invalid or unapproved; fallback to deterministic rules
        fb_action, _ = self.fallback_selector.select_action_with_trace(
            gap, cycle, history, allowed_actions
        )
        invalid_reason = (
            f"Laya output '{raw_choice}' is not in allowed actions"
            if raw_choice is not None
            else "Laya returned no choice"
        )
        trace = SelectorTraceEntry(
            selector_type=self.selector_type,
            checkpoint=self.checkpoint,
            allowed_actions=sorted_allowed,
            raw_action=str(raw_choice) if raw_choice is not None else None,
            validated_action=fb_action,
            is_valid=False,
            latency_ms=round(elapsed_ms, 2),
            fallback_reason=invalid_reason,
            timestamp=now,
        )
        self.last_trace = trace
        return fb_action, trace

    def select_action(
        self,
        gap: IdentifiedGap,
        cycle: int,
        history: List[RecoveryTraceEntry],
        allowed_actions: Set[RecoveryActionType],
    ) -> Optional[RecoveryActionType]:
        """Implements RecoverySelector Protocol."""
        action, _ = self.select_action_with_trace(gap, cycle, history, allowed_actions)
        return action
