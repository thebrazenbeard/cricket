from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class BehavioralPattern(str, Enum):
    MOTIVATED_REASONING = "MOTIVATED_REASONING"
    RATIONALIZATION = "RATIONALIZATION"
    STATUS_DEFENSE = "STATUS_DEFENSE"
    GRIEVANCE_ESCALATION = "GRIEVANCE_ESCALATION"
    MANIPULATION = "MANIPULATION"
    DEPENDENCY_ENGINEERING = "DEPENDENCY_ENGINEERING"
    DECEPTION_RISK = "DECEPTION_RISK"
    AVOIDANCE = "AVOIDANCE"
    RELATIONAL_BID = "RELATIONAL_BID"
    DOMINANCE = "DOMINANCE"
    IDENTITY_PROTECTION = "IDENTITY_PROTECTION"
    SELF_JUSTIFICATION = "SELF_JUSTIFICATION"


class HypothesisState(str, Enum):
    PROPOSED = "PROPOSED"
    SUPPORTED = "SUPPORTED"
    CONTESTED = "CONTESTED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class BehavioralHypothesis:
    pattern: BehavioralPattern
    subject: str
    evidence_refs: tuple[str, ...]
    rationale: str
    state: HypothesisState = HypothesisState.PROPOSED

    def __post_init__(self) -> None:
        if not isinstance(self.pattern, BehavioralPattern):
            raise ValueError("pattern must be a BehavioralPattern")
        if not isinstance(self.subject, str) or not self.subject.strip():
            raise ValueError("subject must be non-empty text")
        if not isinstance(self.evidence_refs, tuple) or not self.evidence_refs or not all(
            isinstance(item, str) and item.strip() for item in self.evidence_refs
        ):
            raise ValueError("behavioral hypothesis evidence_refs must contain evidence")
        if not isinstance(self.rationale, str) or not self.rationale.strip():
            raise ValueError("rationale must be non-empty text")
        if not isinstance(self.state, HypothesisState):
            raise ValueError("state must be a HypothesisState")
