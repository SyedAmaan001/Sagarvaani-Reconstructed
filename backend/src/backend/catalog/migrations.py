"""
Sagarvani Reconstructed — SQLite Metadata Migrations
Versioned, repeatable, non-destructive schema migrations for SQLite metadata catalog.
Tables:
- schema_version: tracks migration history
- runs: query execution run metadata
- tasks: task execution audit and timings
- artifacts: raw response file references and SHA-256 checksums
- evidence: normalized evidence items and provenance
- catalog_datasets: registration of local/historical and external feeds
"""

import sqlite3
from typing import List


MIGRATIONS: List[str] = [
    # Migration 1: Base catalog and run metadata
    """
    CREATE TABLE IF NOT EXISTS schema_version (
        version INTEGER PRIMARY KEY,
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        description TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS runs (
        run_id TEXT PRIMARY KEY,
        trace_id TEXT NOT NULL,
        query TEXT NOT NULL,
        status TEXT NOT NULL,
        data_mode TEXT NOT NULL,
        stakeholder_role TEXT NOT NULL,
        presentation_mode TEXT NOT NULL,
        requested_lat REAL,
        requested_lon REAL,
        location_name TEXT,
        started_at TIMESTAMP NOT NULL,
        completed_at TIMESTAMP NOT NULL,
        policy_verdict TEXT NOT NULL,
        summary_text TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS tasks (
        task_id TEXT NOT NULL,
        run_id TEXT NOT NULL,
        task_name TEXT NOT NULL,
        gateway_id TEXT NOT NULL,
        status TEXT NOT NULL,
        duration_ms REAL NOT NULL,
        error_message TEXT,
        started_at TIMESTAMP NOT NULL,
        completed_at TIMESTAMP NOT NULL,
        PRIMARY KEY (run_id, task_id),
        FOREIGN KEY (run_id) REFERENCES runs (run_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS artifacts (
        artifact_id TEXT PRIMARY KEY,
        run_id TEXT NOT NULL,
        task_id TEXT NOT NULL,
        relative_path TEXT NOT NULL,
        checksum_sha256 TEXT NOT NULL,
        byte_size INTEGER NOT NULL,
        created_at TIMESTAMP NOT NULL,
        FOREIGN KEY (run_id) REFERENCES runs (run_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS evidence (
        evidence_id TEXT PRIMARY KEY,
        run_id TEXT NOT NULL,
        source_id TEXT NOT NULL,
        source_name TEXT NOT NULL,
        product_id TEXT NOT NULL,
        parameter TEXT NOT NULL,
        value_text TEXT NOT NULL,
        unit TEXT NOT NULL,
        lat REAL NOT NULL,
        lon REAL NOT NULL,
        valid_from TIMESTAMP,
        valid_to TIMESTAMP,
        retrieved_at TIMESTAMP NOT NULL,
        data_mode TEXT NOT NULL,
        quality_flags TEXT NOT NULL,
        source_url TEXT NOT NULL,
        attribution TEXT NOT NULL,
        artifact_ref TEXT,
        schema_version TEXT NOT NULL,
        FOREIGN KEY (run_id) REFERENCES runs (run_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS catalog_datasets (
        dataset_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        relative_path TEXT,
        checksum_sha256 TEXT,
        data_mode TEXT NOT NULL,
        observation_date TEXT,
        variables TEXT NOT NULL,
        quality_notes TEXT NOT NULL,
        registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_runs_trace ON runs (trace_id);
    CREATE INDEX IF NOT EXISTS idx_evidence_run ON evidence (run_id);
    CREATE INDEX IF NOT EXISTS idx_tasks_run ON tasks (run_id);
    CREATE INDEX IF NOT EXISTS idx_artifacts_run ON artifacts (run_id);
    """,
    # Migration 2: FSM transition audit table
    """
    CREATE TABLE IF NOT EXISTS fsm_transitions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT NOT NULL,
        from_state TEXT NOT NULL,
        to_state TEXT NOT NULL,
        event_code TEXT NOT NULL,
        reason TEXT NOT NULL,
        transitioned_at TIMESTAMP NOT NULL,
        FOREIGN KEY (run_id) REFERENCES runs (run_id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_fsm_run ON fsm_transitions (run_id);
    """,
    # Migration 3: Recovery trace and policy checks audit tables
    """
    CREATE TABLE IF NOT EXISTS recovery_trace (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT NOT NULL,
        cycle INTEGER NOT NULL,
        selector TEXT NOT NULL,
        action TEXT NOT NULL,
        gap_code TEXT NOT NULL,
        parameters_json TEXT NOT NULL,
        outcome TEXT NOT NULL,
        fallback_reason TEXT,
        executed_at TIMESTAMP NOT NULL,
        FOREIGN KEY (run_id) REFERENCES runs (run_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS policy_checks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT NOT NULL,
        check_name TEXT NOT NULL,
        outcome TEXT NOT NULL,
        details TEXT NOT NULL,
        basis TEXT NOT NULL,
        evaluated_at TIMESTAMP NOT NULL,
        FOREIGN KEY (run_id) REFERENCES runs (run_id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_recovery_run ON recovery_trace (run_id);
    CREATE INDEX IF NOT EXISTS idx_policy_run ON policy_checks (run_id);
    """,
    # Migration 4: Selector trace audit table
    """
    CREATE TABLE IF NOT EXISTS selector_traces (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT NOT NULL,
        cycle INTEGER NOT NULL,
        selector_type TEXT NOT NULL,
        checkpoint TEXT,
        allowed_actions_json TEXT NOT NULL,
        raw_action TEXT,
        validated_action TEXT,
        is_valid INTEGER NOT NULL,
        latency_ms REAL NOT NULL,
        fallback_reason TEXT,
        recorded_at TIMESTAMP NOT NULL,
        FOREIGN KEY (run_id) REFERENCES runs (run_id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_selector_run ON selector_traces (run_id);
    """
]


def apply_migrations(conn: sqlite3.Connection) -> int:
    """Applies all pending migrations idempotently. Returns count of applied migrations."""
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS schema_version (version INTEGER PRIMARY KEY, applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, description TEXT NOT NULL);"
    )
    conn.commit()

    cursor.execute("SELECT version FROM schema_version ORDER BY version ASC;")
    applied = {row[0] for row in cursor.fetchall()}

    newly_applied = 0
    for idx, script in enumerate(MIGRATIONS, start=1):
        if idx not in applied:
            cursor.executescript(script)
            cursor.execute(
                "INSERT INTO schema_version (version, description) VALUES (?, ?);",
                (idx, f"Migration {idx}")
            )
            conn.commit()
            newly_applied += 1

    return newly_applied
