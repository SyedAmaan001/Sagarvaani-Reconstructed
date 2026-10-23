"""
Sagarvani Reconstructed — Evidence and Provenance Schemas
Strict contracts for raw observations, forecasts, attribution, and data lineage.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from backend.models.enums import DataMode


class GeoLocation(BaseModel):
    """Geographic coordinate representation."""
    lat: float = Field(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees")
    lon: float = Field(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees")
    location_name: Optional[str] = Field(default=None, description="Optional port/landmark identifier")


class EvidenceRecord(BaseModel):
    """
    Canonical evidence record.
    Every measurement shown must map to this schema with exact attribution and timestamps.
    """
    evidence_id: str = Field(..., description="Unique evidence identifier, e.g., ev_12345")
    source_id: str = Field(..., description="Machine identifier of the source, e.g., open_meteo_marine")
    source_name: str = Field(..., description="Human-readable provider name, e.g., Open-Meteo Marine API")
    product_id: str = Field(..., description="Specific product identifier, e.g., marine_forecast")
    parameter: str = Field(..., description="Physical variable, e.g., wave_height, wind_speed")
    value: Any = Field(..., description="Scalar reading, numeric value, or structured measurement")
    unit: str = Field(..., description="SI or standard marine unit, e.g., m, km/h, knots, °C")
    location: GeoLocation = Field(..., description="Spatial coordinate associated with the evidence")
    
    # Distinct temporal semantics
    observed_at: Optional[datetime] = Field(default=None, description="Physical observation time by sensor/buoy")
    issued_at: Optional[datetime] = Field(default=None, description="Official bulletin release time")
    model_run_at: Optional[datetime] = Field(default=None, description="Numerical weather model run initialization time")
    valid_from: Optional[datetime] = Field(default=None, description="Start of forecast validity window")
    valid_to: Optional[datetime] = Field(default=None, description="End of forecast validity window")
    retrieved_at: datetime = Field(..., description="Timestamp when Sagarvani retrieved the data")
    
    data_mode: DataMode = Field(..., description="Mode indicating live forecast/observation, replay or fixture")
    quality_flags: List[str] = Field(default_factory=list, description="Quality assessment flags, e.g., CLOUD_MASKED")
    lineage_parent_ids: List[str] = Field(default_factory=list, description="IDs of upstream runs or parent sources")
    source_url: str = Field(..., description="Authoritative documentation or retrieval URL")
    attribution: str = Field(..., description="Legal and scientific attribution statement")
    artifact_ref: Optional[str] = Field(default=None, description="Path to raw response artifact stored on disk")
    schema_version: str = Field(default="v1.0", description="Contract schema version")
