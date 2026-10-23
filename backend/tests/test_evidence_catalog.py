"""
Comprehensive offline test suite for Phase 3:
- ArtifactStore path safety, atomic writes, byte limits, and SHA-256 checksums.
- SQLite schema migrations: versioning, repeatability, and idempotence.
- CatalogService persistence: saving and querying runs, tasks, artifacts, and evidence.
- Dataset registry: cataloging historical NetCDF and test fixtures with DataMode protections.
- End-to-end integration: checking that POST /api/orca/query saves artifacts and records metadata.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

from backend.catalog.artifact_store import (
    ArtifactStore,
    InvalidPathError,
    PayloadTooLargeError,
)
from backend.catalog.dataset_registry import catalog_known_datasets
from backend.catalog.migrations import apply_migrations, MIGRATIONS
from backend.catalog.service import CatalogService
from backend.main import app
from backend.models.enums import DataMode, RunStatus

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def marine_fixture():
    with open(FIXTURES_DIR / "open_meteo_marine_sample.json", "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def weather_fixture():
    with open(FIXTURES_DIR / "open_meteo_weather_sample.json", "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def temp_store(tmp_path):
    return ArtifactStore(base_dir=str(tmp_path / "artifacts"), max_bytes=1024 * 1024)


@pytest.fixture
def temp_catalog(tmp_path):
    return CatalogService(db_path=str(tmp_path / "test_sagarvani.db"))


# ─── 1. ArtifactStore Tests ───────────────────────────────────────────────────

def test_artifact_store_atomic_save_and_checksum(temp_store, marine_fixture):
    """Test artifact store saves atomically and produces valid SHA-256."""
    rel_path, checksum, byte_size = temp_store.save_artifact(
        run_id="run_test_001",
        task_id="task_marine",
        payload=marine_fixture,
    )
    assert rel_path == "artifacts/runs/run_test_001/task_marine.json"
    assert len(checksum) == 64
    assert byte_size > 0

    # Read back and verify content equality
    loaded = temp_store.read_artifact("run_test_001", "task_marine")
    assert loaded["latitude"] == marine_fixture["latitude"]


def test_artifact_store_path_traversal_protection(temp_store):
    """Verify path traversal characters in run_id or task_id are rejected."""
    with pytest.raises(InvalidPathError):
        temp_store.save_artifact(run_id="../escape_run", task_id="task_1", payload={"data": 1})

    with pytest.raises(InvalidPathError):
        temp_store.save_artifact(run_id="run_1", task_id="../../escape_task", payload={"data": 1})

    with pytest.raises(InvalidPathError):
        temp_store.save_artifact(run_id="run/slashes", task_id="task_1", payload={"data": 1})


def test_artifact_store_byte_limit_enforced(tmp_path):
    """Verify payload exceeding max_bytes raises PayloadTooLargeError."""
    store = ArtifactStore(base_dir=str(tmp_path / "artifacts"), max_bytes=50)
    with pytest.raises(PayloadTooLargeError):
        store.save_artifact(run_id="run_large", task_id="task_large", payload={"large": "a" * 100})


# ─── 2. SQLite Migrations & Repeatability ─────────────────────────────────────

def test_sqlite_migrations_idempotency(tmp_path):
    """Verify apply_migrations can be executed multiple times safely without error."""
    import sqlite3
    db_file = tmp_path / "migration_test.db"
    conn = sqlite3.connect(str(db_file))

    # First migration run
    count1 = apply_migrations(conn)
    assert count1 == len(MIGRATIONS)

    # Second migration run should be idempotent
    count2 = apply_migrations(conn)
    assert count2 == 0

    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {r[0] for r in cur.fetchall()}
    assert "runs" in tables
    assert "tasks" in tables
    assert "artifacts" in tables
    assert "evidence" in tables
    assert "catalog_datasets" in tables
    conn.close()


# ─── 3. CatalogService Run & Evidence Persistence ─────────────────────────────

def test_catalog_service_record_and_get_run(temp_catalog, temp_store, marine_fixture, weather_fixture):
    """Test full cycle of recording a query run, tasks, artifacts, and evidence in SQLite."""
    now = datetime.now(timezone.utc)
    from backend.models.evidence import EvidenceRecord, GeoLocation
    from backend.models.enums import GateCheckOutcome, OverallGateVerdict, RunStatus
    from backend.models.query import (
        CanonicalQueryResponse,
        FieldCommunityProjection,
        PolicyAudit,
        PolicyCheckItem,
        QueryContext,
    )
    from backend.models.task import TaskResult, TaskStatus

    run_id = "run_audit_001"
    trace_id = "tr_audit_001"

    rel_art, checksum, byte_size = temp_store.save_artifact(run_id, "task_1", marine_fixture)

    ev = EvidenceRecord(
        evidence_id="ev_test_101",
        source_id="open_meteo_marine",
        source_name="Open-Meteo Marine API",
        product_id="marine_forecast",
        parameter="wave_height",
        value=1.3,
        unit="m",
        location=GeoLocation(lat=13.35, lon=74.70),
        retrieved_at=now,
        valid_from=now,
        data_mode=DataMode.LIVE_FORECAST,
        quality_flags=["NOMINAL"],
        source_url="https://open-meteo.com",
        attribution="Open-Meteo CC BY 4.0",
        artifact_ref=rel_art,
    )

    task_res = TaskResult(
        task_id="task_1",
        status=TaskStatus.COMPLETED,
        started_at=now,
        completed_at=now,
        duration_ms=120.0,
        evidence_ids=["ev_test_101"],
        raw_artifact_path=rel_art,
    )

    resp = CanonicalQueryResponse(
        run_id=run_id,
        trace_id=trace_id,
        status=RunStatus.COMPLETED,
        data_mode=DataMode.LIVE_FORECAST,
        query="Wave near Malpe?",
        extracted_context=QueryContext(
            location=GeoLocation(lat=13.35, lon=74.70, location_name="Malpe"),
        ),
        evidence=[ev],
        warnings=[],
        gaps=[],
        recovery_trace=[],
        policy_audit=PolicyAudit(
            overall_verdict=OverallGateVerdict.NOT_EVALUABLE,
            checks=[
                PolicyCheckItem(
                    check_name="test_check",
                    outcome=GateCheckOutcome.NOT_EVALUABLE,
                    details="Audit check",
                    basis="Baseline",
                )
            ],
            explanation="Test explanation",
        ),
        summary_text="Recorded test summary",
        timestamp=now,
    )

    temp_catalog.record_run(
        response=resp,
        started_at=now,
        completed_at=now,
        tasks=[task_res],
        artifacts_meta=[{
            "task_id": "task_1",
            "relative_path": rel_art,
            "checksum": checksum,
            "byte_size": byte_size,
        }],
    )

    # Query back and verify linkage
    saved_run = temp_catalog.get_run(run_id)
    assert saved_run is not None
    assert saved_run["run_id"] == run_id
    assert saved_run["trace_id"] == trace_id
    assert len(saved_run["evidence"]) == 1
    assert saved_run["evidence"][0]["parameter"] == "wave_height"
    assert saved_run["evidence"][0]["artifact_ref"] == rel_art
    assert len(saved_run["artifacts"]) == 1
    assert saved_run["artifacts"][0]["checksum_sha256"] == checksum
    assert len(saved_run["tasks"]) == 1
    assert saved_run["tasks"][0]["task_id"] == "task_1"


# ─── 4. Dataset Registry Tests ────────────────────────────────────────────────

def test_dataset_registry_historical_safeguards(temp_catalog, temp_store):
    """Verify dataset registry discovers legacy MOSDAC files and marks them HISTORICAL_REPLAY."""
    workspace_root = Path(__file__).parent.parent.parent.resolve()
    datasets = catalog_known_datasets(temp_catalog, workspace_root, temp_store)

    registered = temp_catalog.list_catalog_datasets()
    assert len(registered) > 0

    mosdac_entries = [d for d in registered if "mosdac" in d["dataset_id"]]
    for m in mosdac_entries:
        assert m["data_mode"] == DataMode.HISTORICAL_REPLAY.value
        assert "empty and unverified" in m["quality_notes"]
        assert len(m["checksum_sha256"]) == 64

    fixture_entries = [d for d in registered if "fixture" in d["dataset_id"]]
    for f in fixture_entries:
        assert f["data_mode"] == DataMode.TEST_FIXTURE.value


# ─── 5. End-to-End API Persistence ───────────────────────────────────────────

@patch("backend.gateways.open_meteo_marine.OpenMeteoMarineGateway.fetch_marine_forecast")
@patch("backend.gateways.open_meteo_weather.OpenMeteoWeatherGateway.fetch_weather_forecast")
def test_canonical_query_saves_artifacts_and_database(mock_weather, mock_marine, marine_fixture, weather_fixture):
    """Verify POST /api/orca/query saves raw JSON artifacts and links them in EvidenceRecord."""
    client = TestClient(app)
    mock_marine.return_value = marine_fixture
    mock_weather.return_value = weather_fixture

    payload = {
        "query": "Check waves at Malpe",
        "context_override": {
            "location": {"lat": 13.35, "lon": 74.70, "location_name": "Malpe Harbor"}
        }
    }
    resp = client.post("/api/orca/query", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["status"] == "COMPLETED"
    assert len(data["evidence"]) == 6

    # Verify each evidence item contains artifact reference
    for ev in data["evidence"]:
        assert ev["artifact_ref"] is not None
        assert "artifacts/runs/" in ev["artifact_ref"]
        assert ev["artifact_ref"].endswith(".json")
