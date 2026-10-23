"""
Sagarvani Reconstructed — Guarded Deterministic Finite-State Machine (FSM)
Manages the lifecycle of a single ORCA query run through explicit, validated state transitions.

Design principles:
- All transitions must be in the allow-list; illegal attempts raise a typed error.
- Terminal states are terminal: no further transitions are permitted.
- Every transition is recorded with timestamp, reason/event code, and run ID.
- Deadline enforcement: if the wall-clock deadline has passed, any non-terminal
  transition attempt terminates the run as TIMED_OUT.
- The FSM is deterministic and LLM-independent.
- RELEASED may only be reached after SAFETY_GATE_CHECK; the release gate check
  itself remains NOT_EVALUABLE until Phase 5 evidence validation is implemented.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, FrozenSet, List, Optional, Tuple


# ---------------------------------------------------------------------------
# States
# ---------------------------------------------------------------------------

class FSMState(str, Enum):
    """All explicit lifecycle states for an ORCA query run."""
    REQUESTED = "REQUESTED"
    CONTEXT_VALIDATED = "CONTEXT_VALIDATED"
    TASK_GRAPH_READY = "TASK_GRAPH_READY"
    EVIDENCE_ACQUISITION = "EVIDENCE_ACQUISITION"
    EVIDENCE_VALIDATION = "EVIDENCE_VALIDATION"
    RECOVERY_PLANNING = "RECOVERY_PLANNING"
    SAFETY_GATE_CHECK = "SAFETY_GATE_CHECK"
    RELEASED = "RELEASED"
    ABSTAINED = "ABSTAINED"
    BLOCKED = "BLOCKED"      # gate evaluated and explicitly blocks release
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"


# ---------------------------------------------------------------------------
# Terminal states — no transitions out of these
# ---------------------------------------------------------------------------

TERMINAL_STATES: FrozenSet[FSMState] = frozenset({
    FSMState.RELEASED,
    FSMState.ABSTAINED,
    FSMState.BLOCKED,
    FSMState.FAILED,
    FSMState.TIMED_OUT,
})


# ---------------------------------------------------------------------------
# Allowed transition table
# Source state -> set of legal target states
# ---------------------------------------------------------------------------

ALLOWED_TRANSITIONS: Dict[FSMState, FrozenSet[FSMState]] = {
    FSMState.REQUESTED: frozenset({
        FSMState.CONTEXT_VALIDATED,
        FSMState.ABSTAINED,
        FSMState.FAILED,
        FSMState.TIMED_OUT,
    }),
    FSMState.CONTEXT_VALIDATED: frozenset({
        FSMState.TASK_GRAPH_READY,
        FSMState.ABSTAINED,
        FSMState.FAILED,
        FSMState.TIMED_OUT,
    }),
    FSMState.TASK_GRAPH_READY: frozenset({
        FSMState.EVIDENCE_ACQUISITION,
        FSMState.FAILED,
        FSMState.TIMED_OUT,
    }),
    FSMState.EVIDENCE_ACQUISITION: frozenset({
        FSMState.EVIDENCE_VALIDATION,
        FSMState.RECOVERY_PLANNING,
        FSMState.ABSTAINED,
        FSMState.FAILED,
        FSMState.TIMED_OUT,
    }),
    FSMState.EVIDENCE_VALIDATION: frozenset({
        FSMState.SAFETY_GATE_CHECK,
        FSMState.RECOVERY_PLANNING,
        FSMState.ABSTAINED,
        FSMState.FAILED,
        FSMState.TIMED_OUT,
    }),
    FSMState.RECOVERY_PLANNING: frozenset({
        FSMState.EVIDENCE_ACQUISITION,
        FSMState.SAFETY_GATE_CHECK,
        FSMState.ABSTAINED,
        FSMState.FAILED,
        FSMState.TIMED_OUT,
    }),
    FSMState.SAFETY_GATE_CHECK: frozenset({
        FSMState.RELEASED,
        FSMState.ABSTAINED,
        FSMState.BLOCKED,
        FSMState.FAILED,
        FSMState.TIMED_OUT,
    }),
    FSMState.RELEASED: frozenset(),
    FSMState.ABSTAINED: frozenset(),
    FSMState.BLOCKED: frozenset(),
    FSMState.FAILED: frozenset(),
    FSMState.TIMED_OUT: frozenset(),
}


# ---------------------------------------------------------------------------
# Typed errors
# ---------------------------------------------------------------------------

class FSMError(Exception):
    """Base class for FSM errors."""

    def __init__(self, message: str, run_id: str = "", current_state: Optional[FSMState] = None):
        super().__init__(message)
        self.run_id = run_id
        self.current_state = current_state


class IllegalTransitionError(FSMError):
    """Raised when a transition is not in the allow-list."""

    def __init__(self, run_id: str, from_state: FSMState, to_state: FSMState):
        super().__init__(
            f"[{run_id}] Illegal FSM transition: {from_state.value} -> {to_state.value}",
            run_id=run_id,
            current_state=from_state,
        )
        self.from_state = from_state
        self.to_state = to_state


class TerminalStateError(FSMError):
    """Raised when a transition is attempted from a terminal state."""

    def __init__(self, run_id: str, current_state: FSMState):
        super().__init__(
            f"[{run_id}] Cannot transition from terminal state {current_state.value}",
            run_id=run_id,
            current_state=current_state,
        )


class DeadlineExceededError(FSMError):
    """Raised when the run wall-clock deadline has been exceeded."""

    def __init__(self, run_id: str, current_state: FSMState):
        super().__init__(
            f"[{run_id}] Run deadline exceeded in state {current_state.value}; run terminated as TIMED_OUT",
            run_id=run_id,
            current_state=current_state,
        )


# ---------------------------------------------------------------------------
# Transition event record
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FSMTransitionEvent:
    """Immutable audit record for a single FSM state transition."""
    run_id: str
    from_state: FSMState
    to_state: FSMState
    event_code: str           # e.g. "CONTEXT_OK", "GATEWAY_TIMEOUT", "PARTIAL_EVIDENCE"
    reason: str               # human-readable
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# FSM implementation
# ---------------------------------------------------------------------------

class RunFSM:
    """
    Guarded deterministic FSM for a single ORCA query run.

    Thread-safe: a threading.Lock protects internal state.
    All transitions must be explicitly allowed; illegal transitions raise
    typed errors rather than silently advancing state.
    """

    def __init__(
        self,
        run_id: str,
        deadline: Optional[datetime] = None,
    ):
        self.run_id = run_id
        self.deadline = deadline
        self._state: FSMState = FSMState.REQUESTED
        self._events: List[FSMTransitionEvent] = []
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def state(self) -> FSMState:
        """Current FSM state (thread-safe read)."""
        with self._lock:
            return self._state

    @property
    def events(self) -> List[FSMTransitionEvent]:
        """Ordered list of all recorded transition events (copy)."""
        with self._lock:
            return list(self._events)

    @property
    def is_terminal(self) -> bool:
        """True if the current state is terminal."""
        return self._state in TERMINAL_STATES

    def transition(
        self,
        to_state: FSMState,
        event_code: str,
        reason: str,
    ) -> FSMTransitionEvent:
        """
        Attempt a guarded state transition.

        Raises:
            TerminalStateError: current state is terminal.
            DeadlineExceededError: wall-clock deadline exceeded (transitions
                the run to TIMED_OUT before raising).
            IllegalTransitionError: transition is not in the allow-list.

        Returns the recorded FSMTransitionEvent on success.
        """
        with self._lock:
            from_state = self._state

            # 1. Terminal-state guard
            if from_state in TERMINAL_STATES:
                raise TerminalStateError(self.run_id, from_state)

            # 2. Deadline guard (force TIMED_OUT if deadline exceeded and
            #    target is not already a terminal state)
            if self.deadline is not None and to_state not in TERMINAL_STATES:
                now = datetime.now(timezone.utc)
                if now > self.deadline:
                    evt = self._record_transition(
                        from_state, FSMState.TIMED_OUT,
                        "DEADLINE_EXCEEDED", "Run wall-clock deadline exceeded",
                    )
                    raise DeadlineExceededError(self.run_id, from_state)

            # 3. Allow-list guard
            allowed = ALLOWED_TRANSITIONS.get(from_state, frozenset())
            if to_state not in allowed:
                raise IllegalTransitionError(self.run_id, from_state, to_state)

            # 4. Record and apply
            return self._record_transition(from_state, to_state, event_code, reason)

    def force_terminal(
        self,
        to_state: FSMState,
        event_code: str,
        reason: str,
    ) -> FSMTransitionEvent:
        """
        Force a transition to a terminal state without checking the allow-list.
        Used only for deadline/signal-driven emergency termination.
        Raises ValueError if to_state is not terminal.
        """
        if to_state not in TERMINAL_STATES:
            raise ValueError(f"force_terminal requires a terminal state; got {to_state}")
        with self._lock:
            from_state = self._state
            return self._record_transition(from_state, to_state, event_code, reason)

    def transition_table(self) -> List[Tuple[FSMState, FrozenSet[FSMState]]]:
        """Returns the full static transition table for inspection/logging."""
        return [(s, t) for s, t in ALLOWED_TRANSITIONS.items()]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _record_transition(
        self,
        from_state: FSMState,
        to_state: FSMState,
        event_code: str,
        reason: str,
    ) -> FSMTransitionEvent:
        """Records and applies a transition. Caller must hold the lock."""
        evt = FSMTransitionEvent(
            run_id=self.run_id,
            from_state=from_state,
            to_state=to_state,
            event_code=event_code,
            reason=reason,
        )
        self._events.append(evt)
        self._state = to_state
        return evt
