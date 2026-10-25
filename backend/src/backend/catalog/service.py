"""
Sagarvani Reconstructed — SQLite Metadata Catalog Service
Provides thread-safe persistence and querying for:
- Query runs
- Task execution results
- Artifact checksums and references
- Evidence provenance
- Dataset catalog records
"""

from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
from typing import Any, Dict, List, Optional

from backend.catalog.migrations import apply_migrations
from backend.core.config import settings
from backend.models.evidence import EvidenceRecord
from backend.models.query import CanonicalQueryResponse
from backend.models.task import TaskResult


class CatalogService:
    """Manages SQLite metadata storage and dataset registry."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path or settings.sqlite_db_path).resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self) -> None:
        """Applies schema migrations upon initialization."""
        with self._get_connection() as conn:
            apply_migrations(conn)

    def close(self) -> None:
        """No-op: connections are opened and closed per-operation.
        Provided for test teardown compatibility (Windows SQLite file locking).
        """
        pass

    def record_run(
        self,
        response: CanonicalQueryResponse,
        started_at: datetime,
        completed_at: datetime,
        tasks: Optional[List[TaskResult]] = None,
        artifacts_meta: Optional[List[Dict[str, Any]]] = None,
        user_id: Optional[str] = None,
    ) -> None:
        """Persists a complete query run, its tasks, evidence items, and artifact metadata."""
        ctx = response.extracted_context
        req_lat = ctx.location.lat if ctx and ctx.location else None
        req_lon = ctx.location.lon if ctx and ctx.location else None
        loc_name = ctx.location.location_name if ctx and ctx.location else None

        with self._get_connection() as conn:
            cur = conn.cursor()

            # 1. Insert Run
            cur.execute(
                """
                INSERT INTO runs (
                    run_id, trace_id, query, status, data_mode,
                    stakeholder_role, presentation_mode,
                    requested_lat, requested_lon, location_name,
                    started_at, completed_at, policy_verdict, summary_text, user_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(run_id) DO UPDATE SET
                    trace_id=excluded.trace_id,
                    query=excluded.query,
                    status=excluded.status,
                    data_mode=excluded.data_mode,
                    stakeholder_role=excluded.stakeholder_role,
                    presentation_mode=excluded.presentation_mode,
                    requested_lat=excluded.requested_lat,
                    requested_lon=excluded.requested_lon,
                    location_name=excluded.location_name,
                    started_at=excluded.started_at,
                    completed_at=excluded.completed_at,
                    policy_verdict=excluded.policy_verdict,
                    summary_text=excluded.summary_text,
                    user_id=excluded.user_id;
                """,
                (
                    response.run_id,
                    response.trace_id,
                    response.query,
                    response.status.value,
                    response.data_mode.value,
                    "unknown",
                    "field_community",
                    req_lat,
                    req_lon,
                    loc_name,
                    started_at.isoformat(),
                    completed_at.isoformat(),
                    response.policy_audit.overall_verdict.value,
                    response.summary_text,
                    user_id,
                ),
            )

            # 2. Insert Tasks
            if tasks:
                for t in tasks:
                    cur.execute(
                        """
                        INSERT OR REPLACE INTO tasks (
                            task_id, run_id, task_name, gateway_id,
                            status, duration_ms, error_message, started_at, completed_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                        """,
                        (
                            t.task_id,
                            response.run_id,
                            t.task_id,
                            t.task_id,
                            t.status.value,
                            t.duration_ms,
                            t.error_message,
                            t.started_at.isoformat(),
                            t.completed_at.isoformat(),
                        ),
                    )

            # 3. Insert Artifacts
            if artifacts_meta:
                for art in artifacts_meta:
                    cur.execute(
                        """
                        INSERT OR REPLACE INTO artifacts (
                            artifact_id, run_id, task_id, relative_path,
                            checksum_sha256, byte_size, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?);
                        """,
                        (
                            f"{response.run_id}_{art['task_id']}",
                            response.run_id,
                            art["task_id"],
                            art["relative_path"],
                            art["checksum"],
                            art["byte_size"],
                            completed_at.isoformat(),
                        ),
                    )

            # 4. Insert Evidence Records
            for ev in response.evidence:
                cur.execute(
                    """
                    INSERT OR REPLACE INTO evidence (
                        evidence_id, run_id, source_id, source_name, product_id,
                        parameter, value_text, unit, lat, lon,
                        valid_from, valid_to, retrieved_at, data_mode,
                        quality_flags, source_url, attribution, artifact_ref, schema_version
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        ev.evidence_id,
                        response.run_id,
                        ev.source_id,
                        ev.source_name,
                        ev.product_id,
                        ev.parameter,
                        str(ev.value),
                        ev.unit,
                        ev.location.lat,
                        ev.location.lon,
                        ev.valid_from.isoformat() if ev.valid_from else None,
                        ev.valid_to.isoformat() if ev.valid_to else None,
                        ev.retrieved_at.isoformat(),
                        ev.data_mode.value,
                        json.dumps(ev.quality_flags),
                        ev.source_url,
                        ev.attribution,
                        ev.artifact_ref,
                        ev.schema_version,
                    ),
                )

            # 5. Insert Recovery Trace
            if hasattr(response, "recovery_trace") and response.recovery_trace:
                for tr in response.recovery_trace:
                    params_json = json.dumps(tr.parameters_applied) if hasattr(tr, "parameters_applied") else "{}"
                    gap_code = tr.target_gap.gap_code if hasattr(tr.target_gap, "gap_code") else str(tr.target_gap)
                    cur.execute(
                        """
                        INSERT INTO recovery_trace
                            (run_id, cycle, selector, action, gap_code, parameters_json, outcome, fallback_reason, executed_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                        """,
                        (
                            response.run_id,
                            tr.cycle,
                            str(tr.selector.value if hasattr(tr.selector, "value") else tr.selector),
                            str(tr.action.value if hasattr(tr.action, "value") else tr.action),
                            gap_code,
                            params_json,
                            str(tr.outcome.value if hasattr(tr.outcome, "value") else tr.outcome),
                            tr.fallback_reason,
                            tr.timestamp.isoformat() if hasattr(tr.timestamp, "isoformat") else str(tr.timestamp),
                        ),
                    )
                    if hasattr(tr, "selector_trace") and tr.selector_trace:
                        st = tr.selector_trace
                        allowed_act_json = json.dumps([a.value if hasattr(a, "value") else str(a) for a in st.allowed_actions])
                        cur.execute(
                            """
                            INSERT INTO selector_traces
                                (run_id, cycle, selector_type, checkpoint, allowed_actions_json,
                                 raw_action, validated_action, is_valid, latency_ms, fallback_reason, recorded_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                            """,
                            (
                                response.run_id,
                                tr.cycle,
                                str(st.selector_type.value if hasattr(st.selector_type, "value") else st.selector_type),
                                st.checkpoint,
                                allowed_act_json,
                                st.raw_action,
                                str(st.validated_action.value if hasattr(st.validated_action, "value") else st.validated_action) if st.validated_action else None,
                                1 if st.is_valid else 0,
                                st.latency_ms,
                                st.fallback_reason,
                                st.timestamp.isoformat() if hasattr(st.timestamp, "isoformat") else str(st.timestamp),
                            ),
                        )

            # 6. Insert Policy Checks
            if hasattr(response, "policy_audit") and response.policy_audit and response.policy_audit.checks:
                for chk in response.policy_audit.checks:
                    cur.execute(
                        """
                        INSERT INTO policy_checks
                            (run_id, check_name, outcome, details, basis, evaluated_at)
                        VALUES (?, ?, ?, ?, ?, ?);
                        """,
                        (
                            response.run_id,
                            chk.check_name,
                            str(chk.outcome.value if hasattr(chk.outcome, "value") else chk.outcome),
                            chk.details,
                            chk.basis,
                            completed_at.isoformat(),
                        ),
                    )

            conn.commit()

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves run metadata and associated evidence items."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM runs WHERE run_id = ?;", (run_id,))
            run_row = cur.fetchone()
            if not run_row:
                return None

            run_dict = dict(run_row)

            cur.execute("SELECT * FROM evidence WHERE run_id = ?;", (run_id,))
            run_dict["evidence"] = [dict(r) for r in cur.fetchall()]

            cur.execute("SELECT * FROM artifacts WHERE run_id = ?;", (run_id,))
            run_dict["artifacts"] = [dict(r) for r in cur.fetchall()]

            cur.execute("SELECT * FROM tasks WHERE run_id = ?;", (run_id,))
            run_dict["tasks"] = [dict(r) for r in cur.fetchall()]

            return run_dict

    def register_dataset(
        self,
        dataset_id: str,
        name: str,
        category: str,
        data_mode: str,
        relative_path: Optional[str] = None,
        checksum: Optional[str] = None,
        observation_date: Optional[str] = None,
        variables: Optional[List[str]] = None,
        quality_notes: str = "",
    ) -> None:
        """Registers a verified or historical local dataset fixture into catalog."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT OR REPLACE INTO catalog_datasets (
                    dataset_id, name, category, relative_path,
                    checksum_sha256, data_mode, observation_date,
                    variables, quality_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    dataset_id,
                    name,
                    category,
                    relative_path,
                    checksum,
                    data_mode,
                    observation_date,
                    json.dumps(variables or []),
                    quality_notes,
                ),
            )
            conn.commit()

    def list_catalog_datasets(self) -> List[Dict[str, Any]]:
        """Lists all registered datasets in catalog."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM catalog_datasets ORDER BY dataset_id ASC;")
            return [dict(r) for r in cur.fetchall()]

    def record_fsm_transitions(self, run_id: str, events: List[Any]) -> None:
        """Persists FSM transition event records for a run.

        ``events`` should be a list of ``FSMTransitionEvent`` dataclass instances,
        or any object with attributes ``from_state``, ``to_state``, ``event_code``,
        ``reason``, and ``timestamp``.
        """
        if not events:
            return
        with self._get_connection() as conn:
            cur = conn.cursor()
            # Ensure placeholder run exists so foreign key is satisfied
            cur.execute(
                """
                INSERT OR IGNORE INTO runs (
                    run_id, trace_id, query, status, data_mode,
                    stakeholder_role, presentation_mode,
                    started_at, completed_at, policy_verdict, summary_text
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    run_id,
                    f"tr_{run_id}",
                    "FSM query run",
                    "IN_PROGRESS",
                    "LIVE_FORECAST",
                    "unknown",
                    "field_community",
                    datetime.now(timezone.utc).isoformat(),
                    datetime.now(timezone.utc).isoformat(),
                    "NOT_EVALUABLE",
                    "FSM transition tracking run stub",
                ),
            )
            for evt in events:
                cur.execute(
                    """
                    INSERT INTO fsm_transitions
                        (run_id, from_state, to_state, event_code, reason, transitioned_at)
                    VALUES (?, ?, ?, ?, ?, ?);
                    """,
                    (
                        run_id,
                        str(evt.from_state.value if hasattr(evt.from_state, "value") else evt.from_state),
                        str(evt.to_state.value if hasattr(evt.to_state, "value") else evt.to_state),
                        str(evt.event_code),
                        str(evt.reason),
                        evt.timestamp.isoformat() if hasattr(evt.timestamp, "isoformat") else str(evt.timestamp),
                    ),
                )
            conn.commit()

    def get_fsm_transitions(self, run_id: str) -> List[Dict[str, Any]]:
        """Returns all FSM transitions recorded for a run, ordered by id."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM fsm_transitions WHERE run_id = ? ORDER BY id ASC;",
                (run_id,),
            )
            return [dict(r) for r in cur.fetchall()]

    def record_recovery_trace(self, run_id: str, entries: List[Any]) -> None:
        """Persists recovery trace entries for a run."""
        if not entries:
            return
        with self._get_connection() as conn:
            cur = conn.cursor()
            # Ensure placeholder run exists
            cur.execute(
                """
                INSERT OR IGNORE INTO runs (
                    run_id, trace_id, query, status, data_mode,
                    stakeholder_role, presentation_mode,
                    started_at, completed_at, policy_verdict, summary_text
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    run_id,
                    f"tr_{run_id}",
                    "Recovery run",
                    "IN_PROGRESS",
                    "LIVE_FORECAST",
                    "unknown",
                    "field_community",
                    datetime.now(timezone.utc).isoformat(),
                    datetime.now(timezone.utc).isoformat(),
                    "NOT_EVALUABLE",
                    "Recovery tracking run stub",
                ),
            )
            for tr in entries:
                params_json = json.dumps(tr.parameters_applied) if hasattr(tr, "parameters_applied") else "{}"
                gap_code = tr.target_gap.gap_code if hasattr(tr.target_gap, "gap_code") else str(tr.target_gap)
                cur.execute(
                    """
                    INSERT INTO recovery_trace
                        (run_id, cycle, selector, action, gap_code, parameters_json, outcome, fallback_reason, executed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        run_id,
                        tr.cycle,
                        str(tr.selector.value if hasattr(tr.selector, "value") else tr.selector),
                        str(tr.action.value if hasattr(tr.action, "value") else tr.action),
                        gap_code,
                        params_json,
                        str(tr.outcome.value if hasattr(tr.outcome, "value") else tr.outcome),
                        tr.fallback_reason,
                        tr.timestamp.isoformat() if hasattr(tr.timestamp, "isoformat") else str(tr.timestamp),
                    ),
                )
            conn.commit()

    def get_recovery_trace(self, run_id: str) -> List[Dict[str, Any]]:
        """Returns all recovery trace entries recorded for a run, ordered by cycle and id."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM recovery_trace WHERE run_id = ? ORDER BY cycle ASC, id ASC;",
                (run_id,),
            )
            return [dict(r) for r in cur.fetchall()]

    def record_policy_checks(self, run_id: str, checks: List[Any], evaluated_at: Optional[datetime] = None) -> None:
        """Persists individual policy check evaluations for a run."""
        if not checks:
            return
        ts = evaluated_at or datetime.now(timezone.utc)
        with self._get_connection() as conn:
            cur = conn.cursor()
            # Ensure placeholder run exists
            cur.execute(
                """
                INSERT OR IGNORE INTO runs (
                    run_id, trace_id, query, status, data_mode,
                    stakeholder_role, presentation_mode,
                    started_at, completed_at, policy_verdict, summary_text
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    run_id,
                    f"tr_{run_id}",
                    "Policy run",
                    "IN_PROGRESS",
                    "LIVE_FORECAST",
                    "unknown",
                    "field_community",
                    ts.isoformat(),
                    ts.isoformat(),
                    "NOT_EVALUABLE",
                    "Policy check run stub",
                ),
            )
            for chk in checks:
                cur.execute(
                    """
                    INSERT INTO policy_checks
                        (run_id, check_name, outcome, details, basis, evaluated_at)
                    VALUES (?, ?, ?, ?, ?, ?);
                    """,
                    (
                        run_id,
                        chk.check_name,
                        str(chk.outcome.value if hasattr(chk.outcome, "value") else chk.outcome),
                        chk.details,
                        chk.basis,
                        ts.isoformat(),
                    ),
                )
            conn.commit()

    def get_policy_checks(self, run_id: str) -> List[Dict[str, Any]]:
        """Returns all policy checks recorded for a run, ordered by id."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM policy_checks WHERE run_id = ? ORDER BY id ASC;",
                (run_id,),
            )
            return [dict(r) for r in cur.fetchall()]

    def record_selector_traces(self, run_id: str, traces: List[Any], cycle: int = 1) -> None:
        """Persists individual selector audit records for a run."""
        if not traces:
            return
        ts = datetime.now(timezone.utc)
        with self._get_connection() as conn:
            cur = conn.cursor()
            # Ensure placeholder run exists
            cur.execute(
                """
                INSERT OR IGNORE INTO runs (
                    run_id, trace_id, query, status, data_mode,
                    stakeholder_role, presentation_mode,
                    started_at, completed_at, policy_verdict, summary_text
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    run_id,
                    f"tr_{run_id}",
                    "Selector run",
                    "IN_PROGRESS",
                    "LIVE_FORECAST",
                    "unknown",
                    "field_community",
                    ts.isoformat(),
                    ts.isoformat(),
                    "NOT_EVALUABLE",
                    "Selector trace run stub",
                ),
            )
            for st in traces:
                allowed_act_json = json.dumps([a.value if hasattr(a, "value") else str(a) for a in st.allowed_actions])
                rec_at = st.timestamp.isoformat() if hasattr(st.timestamp, "isoformat") else str(st.timestamp)
                cur.execute(
                    """
                    INSERT INTO selector_traces
                        (run_id, cycle, selector_type, checkpoint, allowed_actions_json,
                         raw_action, validated_action, is_valid, latency_ms, fallback_reason, recorded_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        run_id,
                        cycle,
                        str(st.selector_type.value if hasattr(st.selector_type, "value") else st.selector_type),
                        st.checkpoint,
                        allowed_act_json,
                        st.raw_action,
                        str(st.validated_action.value if hasattr(st.validated_action, "value") else st.validated_action) if st.validated_action else None,
                        1 if st.is_valid else 0,
                        st.latency_ms,
                        st.fallback_reason,
                        rec_at,
                    ),
                )
            conn.commit()

    def get_selector_traces(self, run_id: str) -> List[Dict[str, Any]]:
        """Returns all selector traces recorded for a run, ordered by id."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM selector_traces WHERE run_id = ? ORDER BY cycle ASC, id ASC;",
                (run_id,),
            )
            return [dict(r) for r in cur.fetchall()]

