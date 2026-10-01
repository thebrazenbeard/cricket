from __future__ import annotations

from ..models import Finding, Severity
from .default import DEFAULT_CRICKET_PERSONA
from .model import CricketPersona, PersonaTrait


def persona_line_for_finding(
    finding: Finding,
    persona: CricketPersona = DEFAULT_CRICKET_PERSONA,
) -> str:
    """Add voice without changing the underlying finding, evidence, or authority."""
    if PersonaTrait.SASS not in persona.traits:
        return ""

    rule = finding.rule_id.casefold()
    if "completion_without_verification" in rule:
        return '"Done" is wearing a fake mustache labeled "verified."'
    if "protected_effect" in rule or "authority" in rule:
        return "Nope. Confidence is not permission, and neither are vibes."
    if "semantic.strengthened" in rule:
        return "Cute. Same proposition, stronger claim. Put the qualifier back."
    if "semantic.authority_escalated" in rule:
        return "A preference did not magically become permission."
    if finding.source == "behavior":
        return "That is a hypothesis, not telepathy. Keep the evidence and a rival explanation attached."
    if finding.severity is Severity.BLOCK:
        return "No steering-wheel privileges were found in that argument."
    if finding.severity is Severity.CHALLENGE:
        return "Something moved. The evidence did not."
    return ""
