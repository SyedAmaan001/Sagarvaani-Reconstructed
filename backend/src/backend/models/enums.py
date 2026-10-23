"""
Sagarvani Reconstructed — Core Domain Enums
Explicit, stable enumerations governing the evidence intelligence lifecycle.
"""

from enum import Enum


class RunStatus(str, Enum):
    """Lifecycle and terminal statuses for an ORCA query execution run."""
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"


class DataMode(str, Enum):
    """Attribution and nature of the processed marine data."""
    LIVE_FORECAST = "LIVE_FORECAST"
    LIVE_OBSERVATION = "LIVE_OBSERVATION"
    HISTORICAL_REPLAY = "HISTORICAL_REPLAY"
    TEST_FIXTURE = "TEST_FIXTURE"
    NOT_AVAILABLE = "NOT_AVAILABLE"


class GateCheckOutcome(str, Enum):
    """Deterministic release gate outcomes for an individual policy check."""
    PASS = "PASS"
    BLOCK = "BLOCK"
    NOT_EVALUABLE = "NOT_EVALUABLE"


class OverallGateVerdict(str, Enum):
    """Overall release decision across all policy checks."""
    PASS = "PASS"
    BLOCK = "BLOCK"
    NOT_EVALUABLE = "NOT_EVALUABLE"


class StakeholderRole(str, Enum):
    """The 8 supported stakeholder profiles in Sagarvani Reconstructed."""
    FISHERMAN_COMMUNITY = "fisherman_community"
    PORT_OPERATOR = "port_operator"
    SCIENTIST_RESEARCHER = "scientist_researcher"
    DISASTER_MANAGEMENT = "disaster_management"
    AQUACULTURE_FARMER = "aquaculture_farmer"
    COASTAL_TOURISM = "coastal_tourism"
    OFFSHORE_INDUSTRY = "offshore_industry"
    MARINE_CONSERVATION = "marine_conservation"


class PresentationMode(str, Enum):
    """Presentation modes that project the same underlying decision and evidence."""
    FIELD_COMMUNITY = "field_community"
    PROFESSIONAL_ANALYSIS = "professional_analysis"


class TaskStatus(str, Enum):
    """Execution status of an individual task within the execution harness / DAG."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"
    SKIPPED = "SKIPPED"


class RecoverySelectorType(str, Enum):
    """Selector responsible for choosing the recovery action."""
    DETERMINISTIC_RULES = "deterministic_rules"
    LAYA = "laya"
    HUMAN = "human"


class RecoveryActionType(str, Enum):
    """Closed allow-list of permitted recovery actions."""
    RETRY_WITH_BACKOFF = "retry_with_backoff"
    EXPAND_SPATIAL_RADIUS = "expand_spatial_radius"
    EXTEND_TEMPORAL_WINDOW = "extend_temporal_window"
    SWITCH_FALLBACK_PROVIDER = "switch_fallback_provider"
    LOAD_HISTORICAL_ANALOG = "load_historical_analog"
    REQUEST_USER_CLARIFICATION = "request_user_clarification"
    ABSTAIN_AND_LOG = "abstain_and_log"


class RecoveryOutcome(str, Enum):
    """Outcome of an attempted recovery action."""
    SUCCEEDED = "SUCCEEDED"
    NO_PROGRESS = "NO_PROGRESS"
    EXHAUSTED = "EXHAUSTED"
    FAILED = "FAILED"
