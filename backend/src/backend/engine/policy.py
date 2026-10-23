"""
Sagarvani Reconstructed — Independent Deterministic Release Policy
Evaluates mandatory safety and regulatory checks before any advisory release.
Holds unilateral veto authority over model text, recovery selectors, and formatters.

Mandatory rules:
1. CHECK_OFFICIAL_WARNINGS: NOT_EVALUABLE until official IMD/INCOIS warning feeds are integrated.
2. CHECK_MARINE_PROTECTED_AREAS: NOT_EVALUABLE until verified licensed MPA geometries are integrated.
3. CHECK_VESSEL_LIMITS: NOT_EVALUABLE until maritime domain experts review vessel wave/wind thresholds.
4. CHECK_EVIDENCE_ADEQUACY: PASS if wave and wind evidence exist and pass validation; BLOCK otherwise.

Overall Verdict:
- Any check BLOCK -> BLOCK
- Any check NOT_EVALUABLE -> NOT_EVALUABLE
- All checks PASS -> PASS

FSM Release Guard:
- The FSM may ONLY transition to RELEASED when overall verdict is PASS.
- In this prototype, because mandatory inputs are unintegrated, the verdict is NOT_EVALUABLE
  and the FSM must transition to ABSTAINED (or BLOCKED), never RELEASED.
"""

from __future__ import annotations

from typing import List, Optional

from backend.engine.validator import ValidationResult
from backend.models.enums import GateCheckOutcome, OverallGateVerdict
from backend.models.evidence import EvidenceRecord
from backend.models.query import PolicyAudit, PolicyCheckItem, QueryContext


class ReleasePolicy:
    """
    Deterministic release gatekeeper with absolute veto authority.
    Evaluates individual policy check items and derives the overall verdict.
    """

    def evaluate(
        self,
        evidence_list: List[EvidenceRecord],
        validation_result: Optional[ValidationResult] = None,
        context: Optional[QueryContext] = None,
    ) -> PolicyAudit:
        """
        Evaluates mandatory safety gates against current evidence and validation results.
        Returns a complete PolicyAudit with individual check items and overall verdict.
        """
        checks: List[PolicyCheckItem] = []

        # 1. Official Warning Bulletins Check
        # IMD/INCOIS live cyclone and high-wave warning feeds are not yet integrated
        checks.append(PolicyCheckItem(
            check_name="CHECK_OFFICIAL_WARNINGS",
            outcome=GateCheckOutcome.NOT_EVALUABLE,
            details=(
                "Official IMD/INCOIS cyclone and storm warning bulletin feeds are not yet integrated. "
                "Advisory cannot confirm the absence of active government weather warnings."
            ),
            basis="AGENTS.md & MASTER_BLUEPRINT.md: Official warning checks are NOT_EVALUABLE until authoritative feed is integrated.",
        ))

        # 2. Marine Protected Area Boundary Check
        # Verified licensed shapefiles / geometries not yet integrated
        checks.append(PolicyCheckItem(
            check_name="CHECK_MARINE_PROTECTED_AREAS",
            outcome=GateCheckOutcome.NOT_EVALUABLE,
            details=(
                "Verified, licensed Marine Protected Area (MPA) boundary geometries are unintegrated. "
                "Spatial regulatory clearance cannot be evaluated."
            ),
            basis="AGENTS.md: Protected-area checks are NOT_EVALUABLE unless suitable, licensed, verified geometry source is integrated.",
        ))

        # 3. Vessel Sea-State Tolerance Check
        # Vessel operational risk thresholds have not undergone maritime expert review
        vessel_name = (context.vessel_type if context and context.vessel_type else "unspecified craft")
        checks.append(PolicyCheckItem(
            check_name="CHECK_VESSEL_LIMITS",
            outcome=GateCheckOutcome.NOT_EVALUABLE,
            details=(
                f"Vessel risk thresholds for '{vessel_name}' have not received formal maritime domain-expert review. "
                "Operational navigation clearance cannot be certified."
            ),
            basis="AGENTS.md: Marine risk thresholds are unapproved until supported by authoritative guidance and domain-expert review.",
        ))

        # 4. Evidence Adequacy Check
        # Evaluates whether core forecast parameters exist and are structurally valid
        has_critical_validation_failure = (
            validation_result is not None and validation_result.has_critical_failures
        )
        params = {e.parameter.lower() for e in evidence_list}
        has_wave = "wave_height" in params
        has_wind = any(p in params for p in ("wind_speed", "wind_speed_10m"))

        if not evidence_list:
            checks.append(PolicyCheckItem(
                check_name="CHECK_EVIDENCE_ADEQUACY",
                outcome=GateCheckOutcome.NOT_EVALUABLE,
                details="No marine evidence acquired from upstream sources; evidence adequacy cannot be evaluated.",
                basis="Deterministic Evidence Adequacy Policy: Absent evidence cannot be evaluated for safety release.",
            ))
        elif has_critical_validation_failure:
            checks.append(PolicyCheckItem(
                check_name="CHECK_EVIDENCE_ADEQUACY",
                outcome=GateCheckOutcome.BLOCK,
                details=(
                    "Critical marine evidence (wave height and wind speed) is absent or failed validation; "
                    "release is blocked."
                ),
                basis="Deterministic Evidence Adequacy Policy: Missing core marine forecast blocks advisory release.",
            ))
        elif not has_wave or not has_wind:
            checks.append(PolicyCheckItem(
                check_name="CHECK_EVIDENCE_ADEQUACY",
                outcome=GateCheckOutcome.BLOCK,
                details=(
                    f"Partial core evidence: wave_height={'present' if has_wave else 'missing'}, "
                    f"wind_speed={'present' if has_wind else 'missing'}. Release blocked for incomplete core evidence."
                ),
                basis="Deterministic Evidence Adequacy Policy: Both wave and wind forecast must be present.",
            ))
        else:
            checks.append(PolicyCheckItem(
                check_name="CHECK_EVIDENCE_ADEQUACY",
                outcome=GateCheckOutcome.PASS,
                details="Core marine forecast evidence (wave height and wind speed) is present and verified by validator.",
                basis="Deterministic Evidence Adequacy Policy: Core parameters verified.",
            ))

        # Determine overall verdict
        overall_verdict = self.compute_overall_verdict(checks)

        explanation = (
            "Safety release gate: mandatory official warnings, MPA geofencing, and vessel thresholds "
            "remain NOT_EVALUABLE until external authoritative feeds and domain reviews are integrated. "
            "No certified 'GO' or operational navigation clearance can be issued."
        )
        if overall_verdict == OverallGateVerdict.BLOCK:
            explanation = "Safety release gate: BLOCKED due to critical evidence gaps or validation failures."

        return PolicyAudit(
            overall_verdict=overall_verdict,
            checks=checks,
            explanation=explanation,
        )

    def compute_overall_verdict(self, checks: List[PolicyCheckItem]) -> OverallGateVerdict:
        """
        Computes overall verdict from individual checks.
        Veto hierarchy:
        1. Any BLOCK -> BLOCK
        2. Any NOT_EVALUABLE -> NOT_EVALUABLE
        3. All PASS -> PASS
        """
        outcomes = {c.outcome for c in checks}
        if GateCheckOutcome.BLOCK in outcomes:
            return OverallGateVerdict.BLOCK
        if GateCheckOutcome.NOT_EVALUABLE in outcomes:
            return OverallGateVerdict.NOT_EVALUABLE
        return OverallGateVerdict.PASS

    def can_release(self, audit: PolicyAudit) -> bool:
        """
        Determines whether the FSM is permitted to transition to RELEASED.
        Release is permitted IF AND ONLY IF the overall verdict is PASS.
        """
        return audit.overall_verdict == OverallGateVerdict.PASS
