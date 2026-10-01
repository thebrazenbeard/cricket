from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Severity(str, Enum):
    NOTE = "NOTE"
    CHALLENGE = "CHALLENGE"
    BLOCK = "BLOCK"


class Disposition(str, Enum):
    PASS = "PASS"
    CHALLENGE = "CHALLENGE"
    BLOCK = "BLOCK"


@dataclass(frozen=True)
class Claim:
    statement: str
    status: str = "asserted"
    evidence: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Claim":
        evidence = raw.get("evidence", [])
        if not isinstance(evidence, list) or not all(isinstance(x, str) for x in evidence):
            raise ValueError("claim evidence must be a list of strings")
        return cls(
            statement=str(raw.get("statement", "")).strip(),
            status=str(raw.get("status", "asserted")).strip().lower(),
            evidence=tuple(evidence),
        )


@dataclass(frozen=True)
class Correction:
    superseded: str
    replacement: str

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Correction":
        return cls(
            superseded=str(raw.get("superseded", "")).strip(),
            replacement=str(raw.get("replacement", "")).strip(),
        )


@dataclass(frozen=True)
class ReviewRequest:
    user_message: str
    candidate_response: str
    phase: str = "pre_send"
    effect_class: str = "none"
    explicit_authorization: bool = False
    completion_claimed: bool = False
    verification_evidence: tuple[str, ...] = ()
    claims: tuple[Claim, ...] = ()
    corrections: tuple[Correction, ...] = ()
    principles: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.effect_class not in {"none", "reversible", "protected"}:
            raise ValueError("effect_class must be one of: none, reversible, protected")
        if not isinstance(self.explicit_authorization, bool):
            raise ValueError("explicit_authorization must be a boolean")
        if not isinstance(self.completion_claimed, bool):
            raise ValueError("completion_claimed must be a boolean")

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "ReviewRequest":
        if not isinstance(raw, dict):
            raise ValueError("review request must be an object")
        verification = raw.get("verification_evidence", [])
        principles = raw.get("principles", [])
        if not isinstance(verification, list) or not all(isinstance(x, str) for x in verification):
            raise ValueError("verification_evidence must be a list of strings")
        if not isinstance(principles, list) or not all(isinstance(x, str) for x in principles):
            raise ValueError("principles must be a list of strings")
        claims_raw = raw.get("claims", [])
        corrections_raw = raw.get("corrections", [])
        if not isinstance(claims_raw, list) or not all(isinstance(x, dict) for x in claims_raw):
            raise ValueError("claims must be a list of objects")
        if not isinstance(corrections_raw, list) or not all(isinstance(x, dict) for x in corrections_raw):
            raise ValueError("corrections must be a list of objects")
        metadata = raw.get("metadata", {})
        if not isinstance(metadata, dict):
            raise ValueError("metadata must be an object")
        explicit_authorization = raw.get("explicit_authorization", False)
        completion_claimed = raw.get("completion_claimed", False)
        if not isinstance(explicit_authorization, bool):
            raise ValueError("explicit_authorization must be a boolean")
        if not isinstance(completion_claimed, bool):
            raise ValueError("completion_claimed must be a boolean")
        effect_class = str(raw.get("effect_class", "none")).strip().lower()
        if effect_class not in {"none", "reversible", "protected"}:
            raise ValueError("effect_class must be one of: none, reversible, protected")
        return cls(
            user_message=str(raw.get("user_message", "")),
            candidate_response=str(raw.get("candidate_response", "")),
            phase=str(raw.get("phase", "pre_send")),
            effect_class=effect_class,
            explicit_authorization=explicit_authorization,
            completion_claimed=completion_claimed,
            verification_evidence=tuple(verification),
            claims=tuple(Claim.from_dict(x) for x in claims_raw),
            corrections=tuple(Correction.from_dict(x) for x in corrections_raw),
            principles=tuple(principles),
            metadata=dict(metadata),
        )


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: Severity
    title: str
    rationale: str
    evidence: str = ""
    recommendation: str = ""
    source: str = "deterministic"

    def to_dict(self) -> dict[str, str]:
        return {
            "rule_id": self.rule_id,
            "severity": self.severity.value,
            "title": self.title,
            "rationale": self.rationale,
            "evidence": self.evidence,
            "recommendation": self.recommendation,
            "source": self.source,
        }


@dataclass(frozen=True)
class ReviewResult:
    disposition: Disposition
    findings: tuple[Finding, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "disposition": self.disposition.value,
            "findings": [finding.to_dict() for finding in self.findings],
        }
