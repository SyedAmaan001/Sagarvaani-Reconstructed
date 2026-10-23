"""
Sagarvani Reconstructed — Tests for Deterministic Backend Demo Runner
Validates that the demo runner executes all three scenarios offline without error,
conforming to canonical schemas and release policy guarantees.

Regression coverage:
  - DEC-20261024-09: Offline/mocked runs must never report data_mode=LIVE_FORECAST.
    They must report TEST_FIXTURE (or another non-live mode).
"""

from pathlib import Path
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.models.enums import DataMode
from scripts.demo_runner import (
    run_scenario_1_evidence_acquisition,
    run_scenario_2_source_failure,
    run_scenario_3_recovery_and_termination,
    run_demo,
)


class TestDemoRunner:
    """Test suite for the deterministic backend demo runner."""

    @pytest.fixture(autouse=True)
    def cleanup_overrides(self):
        yield
        app.dependency_overrides.clear()

    def test_scenario_1_evidence_acquisition(self):
        client = TestClient(app)
        res = run_scenario_1_evidence_acquisition(client)
        assert res["status"] == "COMPLETED"
        assert res["evidence_count"] == 6
        assert res["policy_verdict"] == "NOT_EVALUABLE"
        assert "ECMWF" in res["evidence_sample"][0] or "Open-Meteo" in res["evidence_sample"][0]
        assert res["field_headline"] == "Forecast Evidence Ready"

    def test_scenario_2_source_failure(self):
        client = TestClient(app)
        res = run_scenario_2_source_failure(client)
        assert res["status"] == "PARTIAL"
        assert res["evidence_count"] == 3
        assert "GAP_MARINE_SOURCE_ERROR" in res["gaps_detected"]
        assert res["policy_verdict"] == "BLOCK"

    @pytest.mark.asyncio
    async def test_scenario_3_recovery_and_termination(self):
        res = await run_scenario_3_recovery_and_termination()
        assert res["part_a_recovered_parameters"] == 6
        assert res["part_a_action"] == "retry_with_backoff"
        assert res["part_a_outcome"] == "SUCCEEDED"
        assert res["part_b_action"] == "abstain_and_log"
        assert res["part_b_outcome"] == "EXHAUSTED"
        assert res["cycles_executed"] == 1
        assert res["budget_limit"] == 2

    def test_run_demo_full_execution(self):
        exit_code = run_demo()
        assert exit_code == 0

    # ------------------------------------------------------------------
    # Regression: DEC-20261024-09 — Data-Mode Truthfulness
    # Offline/mocked runs must NOT report LIVE_FORECAST.
    # ------------------------------------------------------------------

    def test_scenario_1_data_mode_is_not_live_forecast(self):
        """Offline mocked Scenario 1 must not claim LIVE_FORECAST provenance."""
        client = TestClient(app)
        res = run_scenario_1_evidence_acquisition(client)
        assert res["data_mode"] != DataMode.LIVE_FORECAST.value, (
            f"Scenario 1 used mocked gateways but reported data_mode={res['data_mode']!r}. "
            "TEST_FIXTURE evidence must propagate a non-live data mode."
        )

    def test_scenario_1_data_mode_is_test_fixture(self):
        """Offline mocked Scenario 1 must specifically report TEST_FIXTURE."""
        client = TestClient(app)
        res = run_scenario_1_evidence_acquisition(client)
        assert res["data_mode"] == DataMode.TEST_FIXTURE.value, (
            f"Expected data_mode=TEST_FIXTURE for fixture-backed run, got {res['data_mode']!r}."
        )

    def test_scenario_2_data_mode_is_not_live_forecast(self):
        """Offline mocked Scenario 2 must not claim LIVE_FORECAST provenance."""
        client = TestClient(app)
        res = run_scenario_2_source_failure(client)
        assert res["data_mode"] != DataMode.LIVE_FORECAST.value, (
            f"Scenario 2 used mocked gateways but reported data_mode={res['data_mode']!r}. "
            "TEST_FIXTURE evidence must propagate a non-live data mode."
        )

    def test_scenario_2_data_mode_is_test_fixture(self):
        """Offline mocked Scenario 2 must specifically report TEST_FIXTURE."""
        client = TestClient(app)
        res = run_scenario_2_source_failure(client)
        assert res["data_mode"] == DataMode.TEST_FIXTURE.value, (
            f"Expected data_mode=TEST_FIXTURE for fixture-backed run, got {res['data_mode']!r}."
        )
