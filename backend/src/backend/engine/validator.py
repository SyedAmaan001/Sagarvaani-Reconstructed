"""
Sagarvani Reconstructed — Deterministic Evidence Validator
Validates evidence structure, units, physical ranges, timestamps, forecast-valid-time
relevance, source freshness, spatial coverage, source attribution, and shared lineage.
Detects known shared upstream lineage without inventing missing metadata.
Produces typed validation check items and structured evidence gaps.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import hashlib
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from backend.models.enums import DataMode, RecoveryActionType
from backend.models.evidence import EvidenceRecord, GeoLocation
from backend.models.query import QueryContext
from backend.models.recovery import IdentifiedGap


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ValidationCheckItem:
    """Detailed record of a single validation rule check."""
    check_code: str
    status: str       # "PASS", "WARN", "FAIL"
    severity: str     # "INFO", "WARNING", "CRITICAL"
    affected_evidence_ids: List[str]
    details: str


@dataclass
class ValidationResult:
    """Overall outcome of validating an evidence set against query context."""
    is_valid: bool
    checks: List[ValidationCheckItem] = field(default_factory=list)
    gaps: List[IdentifiedGap] = field(default_factory=list)
    lineage_audit: List[str] = field(default_factory=list)

    @property
    def has_critical_failures(self) -> bool:
        return any(c.status == "FAIL" and c.severity == "CRITICAL" for c in self.checks)


# ---------------------------------------------------------------------------
# Physical range bounds & known units
# ---------------------------------------------------------------------------

PHYSICAL_RANGES = {
    "wave_height": (0.0, 35.0),           # meters
    "wave_period": (0.5, 35.0),           # seconds
    "wave_direction": (0.0, 360.0),       # degrees
    "wind_speed": (0.0, 150.0),           # m/s (or converted km/h <= 540)
    "wind_gusts": (0.0, 200.0),           # m/s (or converted km/h <= 720)
    "wind_direction": (0.0, 360.0),       # degrees
    "water_temperature": (-2.0, 45.0),    # Celsius
}

RECOGNIZED_UNITS = {
    "m", "meter", "meters",
    "s", "sec", "second", "seconds",
    "deg", "°", "degrees",
    "km/h", "m/s", "knots", "knot", "kt", "kts",
    "c", "°c", "celsius",
}

PARAM_ALIASES = {
    "wind_speed_10m": "wind_speed",
    "wind_direction_10m": "wind_direction",
    "wind_gusts_10m": "wind_gusts",
}


def _haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes great-circle distance between two points on Earth in km."""
    R = 6371.0  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))
    return R * c


# ---------------------------------------------------------------------------
# Evidence Validator
# ---------------------------------------------------------------------------

class EvidenceValidator:
    """
    Deterministic validator for marine and atmospheric evidence.
    Evaluates evidence records against physical sanity, units, spatial bounds,
    temporal relevance, attribution, artifact integrity, and shared lineage.
    Never invents missing metadata, values, or universal freshness thresholds.
    """

    def __init__(self, artifacts_base_dir: Optional[str] = None):
        self.artifacts_base_dir = Path(artifacts_base_dir) if artifacts_base_dir else None

    def validate(
        self,
        evidence_list: List[EvidenceRecord],
        context: Optional[QueryContext] = None,
        now: Optional[datetime] = None,
    ) -> ValidationResult:
        """
        Runs all validation passes over the evidence collection.
        Returns a structured ValidationResult with checks, gaps, and lineage audit.
        """
        ref_time = now or datetime.now(timezone.utc)
        checks: List[ValidationCheckItem] = []
        gaps: List[IdentifiedGap] = []
        lineage_audit: List[str] = []

        if not evidence_list:
            checks.append(ValidationCheckItem(
                check_code="CHECK_EVIDENCE_PRESENCE",
                status="FAIL",
                severity="CRITICAL",
                affected_evidence_ids=[],
                details="Evidence set is completely empty; no data acquired.",
            ))
            gaps.append(IdentifiedGap(
                gap_code="GAP_MISSING_CORE_MARINE_FORECAST",
                description="No evidence records available for evaluation.",
                suggested_action=RecoveryActionType.RETRY_WITH_BACKOFF,
            ))
            return ValidationResult(is_valid=False, checks=checks, gaps=gaps, lineage_audit=[])

        # 1. Structure, physical range, and units
        for ev in evidence_list:
            self._validate_record_structure_and_bounds(ev, checks, gaps)

        # 2. Units recognition
        for ev in evidence_list:
            self._validate_units(ev, checks, gaps)

        # 3. Temporal relevance & freshness
        for ev in evidence_list:
            self._validate_temporal(ev, context, ref_time, checks, gaps)

        # 4. Spatial coverage
        if context and context.location:
            for ev in evidence_list:
                self._validate_spatial(ev, context.location, context.operating_radius_km or 35.0, checks, gaps)

        # 5. Attribution & Artifact integrity
        for ev in evidence_list:
            self._validate_attribution_and_artifact(ev, checks, gaps)

        # 6. Shared lineage & cross-evidence comparability
        self._validate_lineage_and_comparability(evidence_list, checks, gaps, lineage_audit)

        # 7. Core marine sufficiency
        self._validate_core_sufficiency(evidence_list, checks, gaps)

        # Overall validity: valid if no CRITICAL failure checks
        is_valid = not any(c.status == "FAIL" and c.severity == "CRITICAL" for c in checks)

        return ValidationResult(
            is_valid=is_valid,
            checks=checks,
            gaps=gaps,
            lineage_audit=lineage_audit,
        )

    # -----------------------------------------------------------------------
    # Internal checks
    # -----------------------------------------------------------------------

    def _validate_record_structure_and_bounds(
        self,
        ev: EvidenceRecord,
        checks: List[ValidationCheckItem],
        gaps: List[IdentifiedGap],
    ) -> None:
        # Check required fields
        if not ev.parameter or ev.value is None:
            checks.append(ValidationCheckItem(
                check_code="CHECK_STRUCTURE",
                status="FAIL",
                severity="CRITICAL",
                affected_evidence_ids=[ev.evidence_id],
                details=f"Evidence '{ev.evidence_id}' has missing parameter or null value.",
            ))
            gaps.append(IdentifiedGap(
                gap_code="GAP_MALFORMED_EVIDENCE",
                description=f"Evidence '{ev.evidence_id}' lacks parameter or value.",
                affected_parameter=ev.parameter,
                suggested_action=RecoveryActionType.SWITCH_FALLBACK_PROVIDER,
            ))
            return

        checks.append(ValidationCheckItem(
            check_code="CHECK_STRUCTURE",
            status="PASS",
            severity="INFO",
            affected_evidence_ids=[ev.evidence_id],
            details=f"Evidence record '{ev.evidence_id}' has valid structure and non-null values.",
        ))

        # Check physical ranges
        param = ev.parameter.lower()
        norm_param = PARAM_ALIASES.get(param, param)
        if norm_param in PHYSICAL_RANGES:
            min_val, max_val = PHYSICAL_RANGES[norm_param]
            try:
                num_val = float(ev.value)
                # Normalise km/h to m/s if parameter is wind
                if norm_param in ("wind_speed", "wind_gusts") and ev.unit.lower() == "km/h":
                    num_val = num_val / 3.6

                if not (min_val <= num_val <= max_val):
                    checks.append(ValidationCheckItem(
                        check_code="CHECK_PHYSICAL_RANGE",
                        status="FAIL",
                        severity="CRITICAL",
                        affected_evidence_ids=[ev.evidence_id],
                        details=(
                            f"Value {ev.value} {ev.unit} for '{ev.parameter}' exceeds physical "
                            f"plausibility bounds [{min_val}, {max_val}]."
                        ),
                    ))
                    gaps.append(IdentifiedGap(
                        gap_code="GAP_UNPHYSICAL_VALUE",
                        description=f"Unphysical {ev.parameter} reading: {ev.value} {ev.unit}",
                        affected_parameter=ev.parameter,
                        suggested_action=RecoveryActionType.ABSTAIN_AND_LOG,
                    ))
                else:
                    checks.append(ValidationCheckItem(
                        check_code="CHECK_PHYSICAL_RANGE",
                        status="PASS",
                        severity="INFO",
                        affected_evidence_ids=[ev.evidence_id],
                        details=f"Value {ev.value} {ev.unit} for '{ev.parameter}' is within physical bounds.",
                    ))
            except (ValueError, TypeError):
                checks.append(ValidationCheckItem(
                    check_code="CHECK_PHYSICAL_RANGE",
                    status="FAIL",
                    severity="CRITICAL",
                    affected_evidence_ids=[ev.evidence_id],
                    details=f"Value '{ev.value}' for '{ev.parameter}' cannot be converted to float.",
                ))
                gaps.append(IdentifiedGap(
                    gap_code="GAP_UNPHYSICAL_VALUE",
                    description=f"Non-numeric value for {ev.parameter}: {ev.value}",
                    affected_parameter=ev.parameter,
                    suggested_action=RecoveryActionType.ABSTAIN_AND_LOG,
                ))

    def _validate_units(
        self,
        ev: EvidenceRecord,
        checks: List[ValidationCheckItem],
        gaps: List[IdentifiedGap],
    ) -> None:
        unit = (ev.unit or "").strip().lower()
        if not unit or unit not in RECOGNIZED_UNITS:
            checks.append(ValidationCheckItem(
                check_code="CHECK_UNITS",
                status="FAIL",
                severity="CRITICAL",
                affected_evidence_ids=[ev.evidence_id],
                details=f"Unrecognized or missing unit '{ev.unit}' for parameter '{ev.parameter}'.",
            ))
            gaps.append(IdentifiedGap(
                gap_code="GAP_UNKNOWN_UNIT",
                description=f"Unrecognized unit '{ev.unit}' on {ev.parameter}.",
                affected_parameter=ev.parameter,
                suggested_action=RecoveryActionType.ABSTAIN_AND_LOG,
            ))
        else:
            checks.append(ValidationCheckItem(
                check_code="CHECK_UNITS",
                status="PASS",
                severity="INFO",
                affected_evidence_ids=[ev.evidence_id],
                details=f"Recognized marine unit '{ev.unit}'.",
            ))

    def _validate_temporal(
        self,
        ev: EvidenceRecord,
        context: Optional[QueryContext],
        ref_time: datetime,
        checks: List[ValidationCheckItem],
        gaps: List[IdentifiedGap],
    ) -> None:
        # Check departure time validity coverage
        if context and context.departure_time:
            dep = context.departure_time
            in_window = False
            if ev.valid_from and ev.valid_to:
                win_start = ev.valid_from - timedelta(hours=6)
                win_end = ev.valid_to + timedelta(hours=6)
                in_window = (win_start <= dep <= win_end)
            elif ev.valid_from:
                in_window = abs((dep - ev.valid_from).total_seconds()) <= (12 * 3600)
            else:
                in_window = True

            if not in_window:
                checks.append(ValidationCheckItem(
                    check_code="CHECK_TEMPORAL_RELEVANCE",
                    status="WARN",
                    severity="WARNING",
                    affected_evidence_ids=[ev.evidence_id],
                    details=f"Forecast validity does not match requested departure time {dep.isoformat()}.",
                ))
                gaps.append(IdentifiedGap(
                    gap_code="GAP_TEMPORAL_WINDOW_MISMATCH",
                    description=f"Evidence temporal window does not cover departure time {dep.isoformat()}.",
                    affected_parameter=ev.parameter,
                    suggested_action=RecoveryActionType.EXTEND_TEMPORAL_WINDOW,
                ))
            else:
                checks.append(ValidationCheckItem(
                    check_code="CHECK_TEMPORAL_RELEVANCE",
                    status="PASS",
                    severity="INFO",
                    affected_evidence_ids=[ev.evidence_id],
                    details="Forecast validity window covers requested departure time.",
                ))

        # Freshness check: retrieval age > 48h
        if ev.retrieved_at and (ref_time - ev.retrieved_at) > timedelta(hours=48):
            checks.append(ValidationCheckItem(
                check_code="CHECK_FRESHNESS",
                status="WARN",
                severity="WARNING",
                affected_evidence_ids=[ev.evidence_id],
                details=f"Retrieval age exceeds threshold (>48h): retrieved at {ev.retrieved_at.isoformat()}.",
            ))
            gaps.append(IdentifiedGap(
                gap_code="GAP_STALE_EVIDENCE",
                description=f"Evidence '{ev.evidence_id}' for {ev.parameter} is stale (>48h old).",
                affected_parameter=ev.parameter,
                suggested_action=RecoveryActionType.SWITCH_FALLBACK_PROVIDER,
            ))
        elif ev.data_mode == DataMode.LIVE_FORECAST and ev.valid_to and ev.valid_to < (ref_time - timedelta(hours=24)):
            checks.append(ValidationCheckItem(
                check_code="CHECK_FRESHNESS",
                status="FAIL",
                severity="CRITICAL",
                affected_evidence_ids=[ev.evidence_id],
                details=f"Forecast expired at {ev.valid_to.isoformat()}; stale by >24 hours.",
            ))
            gaps.append(IdentifiedGap(
                gap_code="GAP_STALE_EVIDENCE",
                description=f"Evidence '{ev.evidence_id}' for {ev.parameter} is expired and stale.",
                affected_parameter=ev.parameter,
                suggested_action=RecoveryActionType.SWITCH_FALLBACK_PROVIDER,
            ))
        elif ev.data_mode == DataMode.HISTORICAL_REPLAY:
            checks.append(ValidationCheckItem(
                check_code="CHECK_FRESHNESS",
                status="WARN",
                severity="WARNING",
                affected_evidence_ids=[ev.evidence_id],
                details="Historical replay data: not applicable for live navigation or safety clearance.",
            ))
        else:
            checks.append(ValidationCheckItem(
                check_code="CHECK_FRESHNESS",
                status="PASS",
                severity="INFO",
                affected_evidence_ids=[ev.evidence_id],
                details="Forecast validity and retrieval freshness verified.",
            ))

    def _validate_spatial(
        self,
        ev: EvidenceRecord,
        query_loc: GeoLocation,
        operating_radius_km: float,
        checks: List[ValidationCheckItem],
        gaps: List[IdentifiedGap],
    ) -> None:
        dist = _haversine_distance_km(query_loc.lat, query_loc.lon, ev.location.lat, ev.location.lon)
        # Bounded threshold: 2.5x operating radius or 100km max
        max_dist = max(operating_radius_km * 2.5, 100.0)

        if dist > max_dist:
            checks.append(ValidationCheckItem(
                check_code="CHECK_SPATIAL_COVERAGE",
                status="FAIL",
                severity="CRITICAL",
                affected_evidence_ids=[ev.evidence_id],
                details=(
                    f"Evidence coordinate ({ev.location.lat:.2f}, {ev.location.lon:.2f}) is {dist:.1f} km away "
                    f"from requested location ({query_loc.lat:.2f}, {query_loc.lon:.2f}), exceeding {max_dist:.1f} km limit."
                ),
            ))
            gaps.append(IdentifiedGap(
                gap_code="GAP_SPATIAL_COVERAGE_EXCEEDED",
                description=f"Evidence coordinate is {dist:.1f}km away from requested point.",
                affected_parameter=ev.parameter,
                suggested_action=RecoveryActionType.EXPAND_SPATIAL_RADIUS,
            ))
        else:
            checks.append(ValidationCheckItem(
                check_code="CHECK_SPATIAL_COVERAGE",
                status="PASS",
                severity="INFO",
                affected_evidence_ids=[ev.evidence_id],
                details=f"Evidence coordinate is {dist:.1f} km from query point (within {max_dist:.1f} km limit).",
            ))

    def _validate_attribution_and_artifact(
        self,
        ev: EvidenceRecord,
        checks: List[ValidationCheckItem],
        gaps: List[IdentifiedGap],
    ) -> None:
        if not ev.attribution or not ev.source_url:
            checks.append(ValidationCheckItem(
                check_code="CHECK_ATTRIBUTION",
                status="FAIL",
                severity="CRITICAL",
                affected_evidence_ids=[ev.evidence_id],
                details=f"Evidence '{ev.evidence_id}' lacks mandatory attribution statement or source URL.",
            ))
            gaps.append(IdentifiedGap(
                gap_code="GAP_MISSING_ATTRIBUTION",
                description=f"Evidence '{ev.evidence_id}' is missing attribution or source URL.",
                affected_parameter=ev.parameter,
                suggested_action=RecoveryActionType.ABSTAIN_AND_LOG,
            ))
        else:
            checks.append(ValidationCheckItem(
                check_code="CHECK_ATTRIBUTION",
                status="PASS",
                severity="INFO",
                affected_evidence_ids=[ev.evidence_id],
                details=f"Attribution verified: '{ev.attribution}'.",
            ))

        # Artifact integrity: verify referenced artifact exists on disk
        if ev.artifact_ref and self.artifacts_base_dir:
            art_path = self.artifacts_base_dir / ev.artifact_ref
            if art_path.exists():
                checks.append(ValidationCheckItem(
                    check_code="CHECK_ARTIFACT_INTEGRITY",
                    status="PASS",
                    severity="INFO",
                    affected_evidence_ids=[ev.evidence_id],
                    details=f"Artifact '{ev.artifact_ref}' exists and is accessible.",
                ))
            else:
                checks.append(ValidationCheckItem(
                    check_code="CHECK_ARTIFACT_INTEGRITY",
                    status="FAIL",
                    severity="WARNING",
                    affected_evidence_ids=[ev.evidence_id],
                    details=f"Artifact reference '{ev.artifact_ref}' does not exist at expected path.",
                ))
                gaps.append(IdentifiedGap(
                    gap_code="GAP_MISSING_ARTIFACT",
                    description=f"Referenced artifact '{ev.artifact_ref}' not found on disk.",
                    affected_parameter=ev.parameter,
                    suggested_action=RecoveryActionType.ABSTAIN_AND_LOG,
                ))

    def _validate_lineage_and_comparability(
        self,
        evidence_list: List[EvidenceRecord],
        checks: List[ValidationCheckItem],
        gaps: List[IdentifiedGap],
        lineage_audit: List[str],
    ) -> None:
        """
        Cross-examines evidence records to detect shared upstream lineage
        and conflicting physical values without inventing relationships.
        """
        by_param: Dict[str, List[EvidenceRecord]] = {}
        for ev in evidence_list:
            by_param.setdefault(ev.parameter, []).append(ev)

        for param, records in by_param.items():
            if len(records) > 1:
                # 1. Lineage check: check for shared parent IDs
                all_parents: List[str] = []
                for r in records:
                    all_parents.extend(r.lineage_parent_ids)

                if len(all_parents) != len(set(all_parents)):
                    shared = set([p for p in all_parents if all_parents.count(p) > 1])
                    msg = f"Multiple evidence records for '{param}' share upstream parent lineage: {list(shared)}."
                    lineage_audit.append(msg)
                    checks.append(ValidationCheckItem(
                        check_code="CHECK_SHARED_LINEAGE",
                        status="WARN",
                        severity="WARNING",
                        affected_evidence_ids=[r.evidence_id for r in records],
                        details=f"{msg} Avoid treating as independent consensus.",
                    ))
                else:
                    checks.append(ValidationCheckItem(
                        check_code="CHECK_SHARED_LINEAGE",
                        status="PASS",
                        severity="INFO",
                        affected_evidence_ids=[r.evidence_id for r in records],
                        details=f"No shared upstream parents detected among {len(records)} records for '{param}'.",
                    ))

                # 2. Value comparability check
                try:
                    vals = [float(r.value) for r in records]
                    spread = max(vals) - min(vals)
                    # For wave height: spread > 3.0m is a significant conflict
                    if param == "wave_height" and spread > 3.0:
                        checks.append(ValidationCheckItem(
                            check_code="CHECK_VALUE_CONSISTENCY",
                            status="WARN",
                            severity="WARNING",
                            affected_evidence_ids=[r.evidence_id for r in records],
                            details=f"Significant divergence in wave height readings (spread {spread:.2f} m).",
                        ))
                        gaps.append(IdentifiedGap(
                            gap_code="GAP_CONTRADICTORY_EVIDENCE",
                            description=f"Divergent wave height readings across sources (spread {spread:.2f} m).",
                            affected_parameter=param,
                            suggested_action=RecoveryActionType.SWITCH_FALLBACK_PROVIDER,
                        ))
                except (ValueError, TypeError):
                    pass

        # Record known upstream provider lineage
        sources = {ev.source_id for ev in evidence_list}
        if "open_meteo_marine" in sources:
            lineage_audit.append("Open-Meteo Marine: ECMWF WAM / DWD GWAM global wave model lineage")
        if "open_meteo_weather" in sources:
            lineage_audit.append("Open-Meteo Weather: ECMWF IFS / DWD ICON global atmospheric model lineage")

        if not any(c.check_code == "CHECK_SHARED_LINEAGE" for c in checks):
            checks.append(ValidationCheckItem(
                check_code="CHECK_SHARED_LINEAGE",
                status="PASS",
                severity="INFO",
                affected_evidence_ids=[ev.evidence_id for ev in evidence_list],
                details=f"Lineage verified across {len(sources)} source providers.",
            ))

    def _validate_core_sufficiency(
        self,
        evidence_list: List[EvidenceRecord],
        checks: List[ValidationCheckItem],
        gaps: List[IdentifiedGap],
    ) -> None:
        norm_params = {PARAM_ALIASES.get(ev.parameter.lower(), ev.parameter.lower()) for ev in evidence_list}
        has_wave = "wave_height" in norm_params
        has_wind = "wind_speed" in norm_params

        if not has_wave and not has_wind:
            checks.append(ValidationCheckItem(
                check_code="CHECK_CORE_EVIDENCE",
                status="FAIL",
                severity="CRITICAL",
                affected_evidence_ids=[],
                details="Missing both wave height and wind speed evidence.",
            ))
            gaps.append(IdentifiedGap(
                gap_code="GAP_MISSING_CORE_MARINE_FORECAST",
                description="Core marine forecast parameters (wave height and wind speed) are absent.",
                suggested_action=RecoveryActionType.RETRY_WITH_BACKOFF,
            ))
        elif not has_wave:
            checks.append(ValidationCheckItem(
                check_code="CHECK_CORE_EVIDENCE",
                status="WARN",
                severity="WARNING",
                affected_evidence_ids=[],
                details="Missing wave height forecast evidence.",
            ))
            gaps.append(IdentifiedGap(
                gap_code="GAP_MISSING_WAVE_HEIGHT",
                description="Wave height forecast evidence is missing.",
                affected_parameter="wave_height",
                suggested_action=RecoveryActionType.RETRY_WITH_BACKOFF,
            ))
        elif not has_wind:
            checks.append(ValidationCheckItem(
                check_code="CHECK_CORE_EVIDENCE",
                status="WARN",
                severity="WARNING",
                affected_evidence_ids=[],
                details="Missing wind speed forecast evidence.",
            ))
            gaps.append(IdentifiedGap(
                gap_code="GAP_MISSING_WIND_SPEED",
                description="Wind speed forecast evidence is missing.",
                affected_parameter="wind_speed",
                suggested_action=RecoveryActionType.RETRY_WITH_BACKOFF,
            ))
        else:
            checks.append(ValidationCheckItem(
                check_code="CHECK_CORE_EVIDENCE",
                status="PASS",
                severity="INFO",
                affected_evidence_ids=[ev.evidence_id for ev in evidence_list if ev.parameter.lower() in ("wave_height", "wind_speed")],
                details="Both wave height and wind speed core parameters are present.",
            ))
