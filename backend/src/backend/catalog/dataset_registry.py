"""
Sagarvani Reconstructed — Dataset Registry
Discovers, computes checksums, and catalogs verified local datasets and historical NetCDF/SAR fixtures.
Enforces that historical/replay fixtures cannot masquerade as live observations.
"""

from pathlib import Path
from typing import Any, Dict, List

from backend.catalog.artifact_store import ArtifactStore
from backend.catalog.service import CatalogService
from backend.models.enums import DataMode


def catalog_known_datasets(
    catalog_service: CatalogService,
    workspace_root: Path,
    artifact_store: ArtifactStore,
) -> List[Dict[str, Any]]:
    """
    Inspects legacy data directories, calculates SHA-256 checksums, and registers datasets with explicit DataMode.
    """
    registered = []

    # 1. MOSDAC Global Ocean Surface Currents (Jan–Jun 2026 dates, empty global attributes)
    currents_dir = workspace_root / "legacy" / "Sagrvani Complete" / "MOSDAC" / "Global Ocean Surface Current"
    if currents_dir.exists():
        for nc_file in currents_dir.glob("*/*.nc"):
            try:
                checksum, byte_size = artifact_store.compute_file_checksum(nc_file)
                # Extracted date from filename e.g. ISRO_CURRENT_TOT_20260131.nc
                date_str = nc_file.stem.split("_")[-1] if "_" in nc_file.stem else "unknown"
                rel_path = str(nc_file.relative_to(workspace_root)).replace("\\", "/")

                dataset_id = f"ds_mosdac_current_{nc_file.stem}"
                catalog_service.register_dataset(
                    dataset_id=dataset_id,
                    name=f"MOSDAC Ocean Surface Current ({nc_file.stem})",
                    category="hydrodynamic_ocean_currents",
                    data_mode=DataMode.HISTORICAL_REPLAY.value,
                    relative_path=rel_path,
                    checksum=checksum,
                    observation_date=date_str,
                    variables=["u_current", "v_current", "current_speed"],
                    quality_notes=(
                        "Historical replay / test fixture only. While filenames carry 2026 dates, "
                        "global attributes are empty and unverified. Must never be treated as verified live ocean state."
                    ),
                )
                registered.append({"dataset_id": dataset_id, "file": nc_file.name, "checksum": checksum})
            except Exception:
                pass

    # 2. Open-Meteo Deterministic Fixtures
    fixtures_dir = workspace_root / "backend" / "tests" / "fixtures"
    if fixtures_dir.exists():
        for json_file in fixtures_dir.glob("*.json"):
            try:
                checksum, byte_size = artifact_store.compute_file_checksum(json_file)
                rel_path = str(json_file.relative_to(workspace_root)).replace("\\", "/")
                dataset_id = f"ds_fixture_{json_file.stem}"

                catalog_service.register_dataset(
                    dataset_id=dataset_id,
                    name=f"Open-Meteo Test Fixture ({json_file.stem})",
                    category="test_fixtures",
                    data_mode=DataMode.TEST_FIXTURE.value,
                    relative_path=rel_path,
                    checksum=checksum,
                    observation_date="2026-10-24",
                    variables=["wave_height", "wave_direction", "wave_period"] if "marine" in json_file.stem else ["wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"],
                    quality_notes="Deterministic test fixture for offline unit and regression test suites.",
                )
                registered.append({"dataset_id": dataset_id, "file": json_file.name, "checksum": checksum})
            except Exception:
                pass

    return registered
