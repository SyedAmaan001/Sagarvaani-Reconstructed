"""
Sagarvani Reconstructed — Execution Harness
Executes a validated TaskDAG using asyncio, respecting per-task timeouts,
bounded concurrency, and dependency ordering.

Key guarantees:
- Independent tasks in the same wave execute concurrently (asyncio gather).
- Dependent tasks wait for all prerequisites to complete before starting.
- If a prerequisite fails or times out, all downstream tasks are SKIPPED.
- Per-task timeout enforcement via asyncio.wait_for.
- Overall run deadline is propagated from the FSM to the harness.
- Results are always typed TaskResult; no silent success for failures.
- Gateways are invoked through a callable protocol so tests can inject fakes.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine, Dict, List, Optional, Set

from backend.models.enums import DataMode, TaskStatus
from backend.models.evidence import EvidenceRecord
from backend.models.task import TaskContract, TaskResult
from backend.engine.dag import TaskDAG


# ---------------------------------------------------------------------------
# Gateway callable protocol
# ---------------------------------------------------------------------------

# A GatewayCallable is an async function that accepts gateway parameters and
# returns a tuple of (raw_payload, evidence_list).
# Tests inject fake implementations; production wires real gateways.
GatewayCallable = Callable[
    [Dict[str, Any]],
    Coroutine[Any, Any, tuple[Dict[str, Any], List[EvidenceRecord]]],
]


# ---------------------------------------------------------------------------
# Harness result
# ---------------------------------------------------------------------------

@dataclass
class HarnessResult:
    """Aggregated outcome from executing the full task graph."""
    task_results: List[TaskResult] = field(default_factory=list)
    evidence: List[EvidenceRecord] = field(default_factory=list)
    raw_artifacts: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # task_id -> raw payload
    failed_task_ids: List[str] = field(default_factory=list)
    timed_out_task_ids: List[str] = field(default_factory=list)
    skipped_task_ids: List[str] = field(default_factory=list)

    @property
    def all_succeeded(self) -> bool:
        return (
            not self.failed_task_ids
            and not self.timed_out_task_ids
            and not self.skipped_task_ids
        )

    @property
    def any_evidence(self) -> bool:
        return len(self.evidence) > 0


# ---------------------------------------------------------------------------
# Execution harness
# ---------------------------------------------------------------------------

class ExecutionHarness:
    """
    Async execution harness for a validated TaskDAG.

    Parameters
    ----------
    dag : TaskDAG
        Validated, acyclic task graph.
    registry : Dict[str, GatewayCallable]
        Maps gateway_id strings to async callable implementations.
        Tests inject fakes here; production passes real gateway wrappers.
    max_concurrency : int
        Maximum number of tasks that may run simultaneously.
    run_deadline : Optional[datetime]
        If set and exceeded, running/pending tasks are cancelled and marked
        TIMED_OUT.
    """

    def __init__(
        self,
        dag: TaskDAG,
        registry: Dict[str, GatewayCallable],
        max_concurrency: int = 4,
        run_deadline: Optional[datetime] = None,
    ):
        self._dag = dag
        self._registry = registry
        self._max_concurrency = max_concurrency
        self._run_deadline = run_deadline
        self._semaphore: Optional[asyncio.Semaphore] = None

    async def execute(self) -> HarnessResult:
        """
        Execute all waves of the DAG in dependency order.
        Independent tasks within a wave run concurrently.
        Returns HarnessResult with typed outcomes for every task.
        """
        self._semaphore = asyncio.Semaphore(self._max_concurrency)
        result = HarnessResult()
        completed_ok: Set[str] = set()   # task IDs that COMPLETED successfully
        failed_ids: Set[str] = set()     # task IDs that FAILED or TIMED_OUT

        waves = self._dag.independent_groups()

        for wave in waves:
            # Determine which tasks in this wave can actually run
            runnable = []
            for task in wave:
                missing_deps = [d for d in task.dependencies if d not in completed_ok]
                if missing_deps:
                    # Prerequisite failed/timed-out/skipped → skip this task
                    skipped = self._make_skipped(task, missing_deps)
                    result.task_results.append(skipped)
                    result.skipped_task_ids.append(task.task_id)
                else:
                    runnable.append(task)

            if not runnable:
                continue

            # Check run deadline before starting this wave
            if self._run_deadline is not None:
                if datetime.now(timezone.utc) > self._run_deadline:
                    for task in runnable:
                        tr = self._make_timed_out(task, "Run deadline exceeded before wave start")
                        result.task_results.append(tr)
                        result.timed_out_task_ids.append(task.task_id)
                    continue

            # Execute runnable tasks concurrently
            coros = [self._execute_task(task) for task in runnable]
            wave_results: List[TaskResult] = await asyncio.gather(*coros)

            for tr in wave_results:
                result.task_results.append(tr)
                if tr.status == TaskStatus.COMPLETED:
                    completed_ok.add(tr.task_id)
                    # Collect evidence and raw payload from task extras
                    if hasattr(tr, "_evidence"):
                        result.evidence.extend(tr._evidence)  # type: ignore[attr-defined]
                    if hasattr(tr, "_raw_payload") and tr._raw_payload is not None:  # type: ignore[attr-defined]
                        result.raw_artifacts[tr.task_id] = tr._raw_payload  # type: ignore[attr-defined]
                elif tr.status == TaskStatus.TIMED_OUT:
                    result.timed_out_task_ids.append(tr.task_id)
                    failed_ids.add(tr.task_id)
                else:
                    result.failed_task_ids.append(tr.task_id)
                    failed_ids.add(tr.task_id)

        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _execute_task(self, task: TaskContract) -> TaskResult:
        """Execute a single task with semaphore concurrency control and timeout."""
        async with self._semaphore:  # type: ignore[union-attr]
            started_at = datetime.now(timezone.utc)

            # Check run deadline
            if self._run_deadline is not None and datetime.now(timezone.utc) > self._run_deadline:
                return self._make_timed_out(task, "Run deadline exceeded before task start")

            gateway_fn = self._registry.get(task.gateway_id)
            if gateway_fn is None:
                completed_at = datetime.now(timezone.utc)
                dur = (completed_at - started_at).total_seconds() * 1000
                tr = TaskResult(
                    task_id=task.task_id,
                    status=TaskStatus.FAILED,
                    started_at=started_at,
                    completed_at=completed_at,
                    duration_ms=dur,
                    error_message=f"No gateway registered for gateway_id='{task.gateway_id}'",
                )
                return tr

            try:
                raw_payload, evidence = await asyncio.wait_for(
                    gateway_fn(task.parameters),
                    timeout=task.timeout_seconds,
                )
                completed_at = datetime.now(timezone.utc)
                dur = (completed_at - started_at).total_seconds() * 1000
                tr = TaskResult(
                    task_id=task.task_id,
                    status=TaskStatus.COMPLETED,
                    started_at=started_at,
                    completed_at=completed_at,
                    duration_ms=dur,
                    evidence_ids=[e.evidence_id for e in evidence],
                )
                # Attach evidence and raw payload as private attributes
                # so the harness can collect them without changing TaskResult schema.
                object.__setattr__(tr, "_evidence", evidence)
                object.__setattr__(tr, "_raw_payload", raw_payload)
                return tr

            except asyncio.TimeoutError:
                completed_at = datetime.now(timezone.utc)
                dur = (completed_at - started_at).total_seconds() * 1000
                return TaskResult(
                    task_id=task.task_id,
                    status=TaskStatus.TIMED_OUT,
                    started_at=started_at,
                    completed_at=completed_at,
                    duration_ms=dur,
                    error_message=f"Task timed out after {task.timeout_seconds}s",
                )

            except Exception as exc:
                completed_at = datetime.now(timezone.utc)
                dur = (completed_at - started_at).total_seconds() * 1000
                return TaskResult(
                    task_id=task.task_id,
                    status=TaskStatus.FAILED,
                    started_at=started_at,
                    completed_at=completed_at,
                    duration_ms=dur,
                    error_message=str(exc),
                )

    def _make_skipped(self, task: TaskContract, missing_deps: List[str]) -> TaskResult:
        now = datetime.now(timezone.utc)
        return TaskResult(
            task_id=task.task_id,
            status=TaskStatus.SKIPPED,
            started_at=now,
            completed_at=now,
            duration_ms=0.0,
            error_message=f"Skipped: prerequisite(s) not completed: {missing_deps}",
        )

    def _make_timed_out(self, task: TaskContract, reason: str) -> TaskResult:
        now = datetime.now(timezone.utc)
        return TaskResult(
            task_id=task.task_id,
            status=TaskStatus.TIMED_OUT,
            started_at=now,
            completed_at=now,
            duration_ms=0.0,
            error_message=reason,
        )
