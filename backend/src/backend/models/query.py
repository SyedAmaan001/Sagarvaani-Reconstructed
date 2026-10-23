"""
Sagarvani Reconstructed — Canonical Request, Policy Audit, and Response Contracts
Contracts consumed by the canonical query API (POST /api/orca/query) and future frontend views.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from backend.models.enums import (
    DataMode,
    GateCheckOutcome,
    OverallGateVerdict,
    PresentationMode,
    RunStatus,
    StakeholderRole,
)
from backend.models.evidence import EvidenceRecord, GeoLocation
from backend.models.recovery import IdentifiedGap, RecoveryTraceEntry


class QueryContext(BaseModel):
    """Normalized query parameters extracted or provided with the request."""
    location: Optional[GeoLocation] = Field(default=None, description="Coordinates and port identifier")
    departure_time: Optional[datetime] = Field(default=None, description="Planned departure or reference valid time")
    vessel_type: Optional[str] = Field(default=None, description="Specific vessel class, e.g., artisanal_canoe, motorized_craft")
    operating_radius_km: Optional[float] = Field(default=35.0, ge=1.0, le=200.0, description="Operating distance from coast/port")
    language: str = Field(default="en", description="Target language code (ISO 639-1)")


class CanonicalQueryRequest(BaseModel):
    """Input payload for POST /api/orca/query."""
    query: str = Field(..., min_length=2, max_length=1000, description="User's natural language inquiry or operational question")
    session_id: Optional[str] = Field(default=None, description="Session identifier for multi-turn tracking")
    stakeholder_role: StakeholderRole = Field(
        default=StakeholderRole.FISHERMAN_COMMUNITY,
        description="Target stakeholder persona"
    )
    presentation_mode: PresentationMode = Field(
        default=PresentationMode.FIELD_COMMUNITY,
        description="Initial display preference (does not change underlying evidence)"
    )
    context_override: Optional[QueryContext] = Field(
        default=None,
        description="Optional explicitly provided context (location, vessel, departure time)"
    )


class PolicyCheckItem(BaseModel):
    """Individual safety or regulatory check performed by the independent release policy."""
    check_name: str = Field(..., description="Name of policy check, e.g., vessel_wave_tolerance, mpa_geofence")
    outcome: GateCheckOutcome = Field(..., description="PASS, BLOCK, or NOT_EVALUABLE")
    details: str = Field(..., description="Reasoning and threshold comparison")
    basis: str = Field(..., description="Source of threshold or note on why check is unvalidated/unapproved")


class PolicyAudit(BaseModel):
    """Independent deterministic release policy audit report."""
    overall_verdict: OverallGateVerdict = Field(..., description="Final release gate decision")
    checks: List[PolicyCheckItem] = Field(default_factory=list, description="All evaluated policy checks")
    explanation: str = Field(..., description="Clear explanation of the verdict")


class MarineWarningItem(BaseModel):
    """Warning item derived from official bulletins or threshold violations."""
    warning_code: str = Field(..., description="Warning identifier, e.g., WARN_HIGH_SWELL")
    severity: str = Field(..., description="INFORMATIONAL, CAUTION, WARNING, DANGER")
    message: str = Field(..., description="Warning text")
    source: str = Field(..., description="Attributed source of the warning")


class FieldCommunityProjection(BaseModel):
    """Low-cognitive-load, mobile-first summary projection for field and coastal communities."""
    headline: str = Field(..., description="Concise, plain-language operational status")
    advisory_text: str = Field(..., description="Clear contextual guidance")
    caution_flags: List[str] = Field(default_factory=list, description="Immediate visual alert tags")


class ProfessionalAnalysisProjection(BaseModel):
    """Detailed analytics and lineage projection for scientists, port operators, and analysts."""
    scientific_summary: str = Field(..., description="Technical summary with physical parameters")
    parameter_breakdown: Dict[str, Any] = Field(default_factory=dict, description="Structured values by parameter")
    lineage_audit: List[str] = Field(default_factory=list, description="Data sources and upstream lineage notes")


class CanonicalQueryResponse(BaseModel):
    """Canonical response schema for POST /api/orca/query."""
    run_id: str = Field(..., description="Unique run identifier for this execution, e.g., run_abc123")
    trace_id: str = Field(..., description="Correlation trace ID for request lifecycle")
    status: RunStatus = Field(..., description="High-level execution status")
    data_mode: DataMode = Field(..., description="Attribute characterizing evidence freshness/type")
    query: str = Field(..., description="Original user query text")
    extracted_context: Optional[QueryContext] = Field(default=None, description="Context used during processing")
    
    evidence: List[EvidenceRecord] = Field(default_factory=list, description="All verified evidence items")
    warnings: List[MarineWarningItem] = Field(default_factory=list, description="Identified warning notices")
    gaps: List[IdentifiedGap] = Field(default_factory=list, description="Unresolved or detected evidence gaps")
    recovery_trace: List[RecoveryTraceEntry] = Field(default_factory=list, description="Trace of recovery actions attempted")
    
    policy_audit: PolicyAudit = Field(..., description="Independent release policy verdict")
    summary_text: str = Field(..., description="Grounded, evidence-backed narrative summary")
    
    field_view: Optional[FieldCommunityProjection] = Field(default=None, description="Field / Community projection")
    professional_view: Optional[ProfessionalAnalysisProjection] = Field(default=None, description="Professional / Analysis projection")
    
    timestamp: datetime = Field(..., description="Response generation timestamp")
    disclaimer: str = Field(
        default="PROTOTYPE ONLY: Not certified marine navigation or safety advice. Do not use for real-world vessel departure or evacuation decisions.",
        description="Mandatory prototype boundary notice"
    )
