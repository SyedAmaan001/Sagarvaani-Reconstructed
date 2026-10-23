"""
Sagarvani Reconstructed — Recovery Schemas
Typed contracts for identifying gaps, selecting bounded corrective actions, and tracing recovery.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from backend.models.enums import RecoveryActionType, RecoveryOutcome, RecoverySelectorType


class IdentifiedGap(BaseModel):
    """Specific evidence gap or deficiency detected by the validator."""
    gap_code: str = Field(..., description="Stable error code, e.g., GAP_STALE_EVIDENCE, GAP_MISSING_WAVE_HEIGHT")
    description: str = Field(..., description="Human-readable description of what is missing or invalid")
    affected_parameter: Optional[str] = Field(default=None, description="Physical variable affected, if any")
    suggested_action: Optional[RecoveryActionType] = Field(default=None, description="Preliminary suggested action")


class SelectorTraceEntry(BaseModel):
    """Structured audit record for a single selector decision attempt."""
    selector_type: RecoverySelectorType = Field(..., description="Target selector (rules or laya)")
    checkpoint: Optional[str] = Field(default=None, description="Model checkpoint name or revision if applicable")
    allowed_actions: List[RecoveryActionType] = Field(..., description="Allow-listed actions available for this decision")
    raw_action: Optional[str] = Field(default=None, description="Raw action selected before validation")
    validated_action: Optional[RecoveryActionType] = Field(default=None, description="Validated permitted action")
    is_valid: bool = Field(..., description="Whether raw selection passed validation against allow-list")
    latency_ms: float = Field(..., description="Elapsed decision latency in milliseconds")
    fallback_reason: Optional[str] = Field(default=None, description="Reason if fallback occurred")
    timestamp: datetime = Field(..., description="Timestamp of selector evaluation")


class RecoveryTraceEntry(BaseModel):
    """Auditable log entry for an attempted recovery action."""
    cycle: int = Field(..., ge=1, le=2, description="Recovery cycle index (max 2 cycles)")
    selector: RecoverySelectorType = Field(..., description="Selector that chose the action (rules or laya)")
    action: RecoveryActionType = Field(..., description="Permitted allow-listed recovery action taken")
    target_gap: IdentifiedGap = Field(..., description="The specific evidence gap targeted")
    parameters_applied: Dict[str, Any] = Field(default_factory=dict, description="Parameters used for corrective action")
    outcome: RecoveryOutcome = Field(..., description="Outcome of the recovery attempt")
    fallback_reason: Optional[str] = Field(default=None, description="Reason if rule-based fallback occurred")
    selector_trace: Optional[SelectorTraceEntry] = Field(default=None, description="Underlying selector audit record")
    timestamp: datetime = Field(..., description="Execution timestamp of this recovery attempt")

