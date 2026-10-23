"""
Sagarvani Reconstructed — Task DAG Validator
Validates a dependency graph of TaskContracts before execution.

Checks performed before any task runs:
- No duplicate task IDs
- All declared dependencies reference known task IDs
- No cyclic dependencies (DFS-based)

Tasks are returned in a valid topological execution order.
"""

from __future__ import annotations

from typing import Dict, List, Set

from backend.models.task import TaskContract


# ---------------------------------------------------------------------------
# Typed errors
# ---------------------------------------------------------------------------

class TaskDAGError(Exception):
    """Base class for DAG validation errors."""


class DuplicateTaskIDError(TaskDAGError):
    """Raised when two tasks share the same task_id."""

    def __init__(self, task_id: str):
        super().__init__(f"Duplicate task ID in DAG: '{task_id}'")
        self.task_id = task_id


class UnknownDependencyError(TaskDAGError):
    """Raised when a task declares a dependency on an unknown task ID."""

    def __init__(self, task_id: str, dep_id: str):
        super().__init__(
            f"Task '{task_id}' depends on unknown task '{dep_id}'"
        )
        self.task_id = task_id
        self.dep_id = dep_id


class CyclicDependencyError(TaskDAGError):
    """Raised when the dependency graph contains a cycle."""

    def __init__(self, cycle_path: List[str]):
        path_str = " -> ".join(cycle_path)
        super().__init__(f"Cyclic dependency detected: {path_str}")
        self.cycle_path = cycle_path


class SelfLoopError(CyclicDependencyError):
    """Raised when a task directly depends on itself."""

    def __init__(self, task_id: str):
        super().__init__([task_id, task_id])


# Aliases for naming flexibility
DuplicateTaskIdError = DuplicateTaskIDError


# ---------------------------------------------------------------------------
# DAG validator
# ---------------------------------------------------------------------------

class TaskDAG:
    """
    Validates and provides topological ordering for a list of TaskContracts.

    Usage::

        dag = TaskDAG(contracts)           # raises on invalid graph
        ordered = dag.topological_order()  # list of TaskContract in exec order

    Independent tasks (no shared dependencies) appear in unspecified relative
    order and may be executed concurrently by the harness.
    """

    def __init__(self, contracts: List[TaskContract]):
        self._contracts: List[TaskContract] = contracts
        self._index: Dict[str, TaskContract] = {}
        self._validate()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def contracts(self) -> List[TaskContract]:
        return list(self._contracts)

    def task_by_id(self, task_id: str) -> TaskContract:
        return self._index[task_id]

    def topological_order(self) -> List[TaskContract]:
        """
        Returns tasks in a valid topological execution order (Kahn's algorithm).
        Tasks with no remaining prerequisites appear first.
        """
        in_degree: Dict[str, int] = {t.task_id: 0 for t in self._contracts}
        dependants: Dict[str, List[str]] = {t.task_id: [] for t in self._contracts}

        for t in self._contracts:
            for dep in t.dependencies:
                in_degree[t.task_id] += 1
                dependants[dep].append(t.task_id)

        # Start with all zero-in-degree tasks (stable sort by task_id for determinism)
        queue: List[str] = sorted(
            [tid for tid, deg in in_degree.items() if deg == 0]
        )
        result: List[TaskContract] = []

        while queue:
            tid = queue.pop(0)
            result.append(self._index[tid])
            for child in dependants[tid]:
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)
                    queue.sort()  # keep deterministic order

        return result

    def independent_groups(self) -> List[List[TaskContract]]:
        """
        Returns tasks grouped by execution wave (tasks in the same wave
        have no dependency on each other and may run concurrently).
        """
        waves: List[List[TaskContract]] = []
        remaining = set(t.task_id for t in self._contracts)
        completed: Set[str] = set()
        index = self._index

        while remaining:
            wave = [
                index[tid] for tid in sorted(remaining)
                if all(dep in completed for dep in index[tid].dependencies)
            ]
            if not wave:
                # Shouldn't happen after _validate(), but guard defensively
                raise CyclicDependencyError(list(remaining))
            for t in wave:
                remaining.discard(t.task_id)
                completed.add(t.task_id)
            waves.append(wave)

        return waves

    # ------------------------------------------------------------------
    # Internal validation
    # ------------------------------------------------------------------

    def _validate(self) -> None:
        """Validates uniqueness, dependency references and acyclicity."""
        # 1. Duplicate ID check
        seen: Set[str] = set()
        for t in self._contracts:
            if t.task_id in seen:
                raise DuplicateTaskIDError(t.task_id)
            seen.add(t.task_id)
            self._index[t.task_id] = t

        # 2. Unknown dependency check
        for t in self._contracts:
            for dep in t.dependencies:
                if dep not in self._index:
                    raise UnknownDependencyError(t.task_id, dep)

        # 3. Cycle detection via DFS
        visited: Set[str] = set()
        in_stack: Set[str] = set()

        def dfs(tid: str, path: List[str]) -> None:
            visited.add(tid)
            in_stack.add(tid)
            for dep in self._index[tid].dependencies:
                if dep not in visited:
                    dfs(dep, path + [dep])
                elif dep in in_stack:
                    raise CyclicDependencyError(path + [dep])
            in_stack.discard(tid)

        for t in self._contracts:
            if t.task_id not in visited:
                dfs(t.task_id, [t.task_id])
