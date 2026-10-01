from __future__ import annotations

from typing import Any

from .behavior import BehavioralHypothesis, BehavioralPattern, HypothesisState
from .model import (
    Force,
    Polarity,
    ProvenanceKind,
    SemanticFrame,
    SemanticProposition,
    SemanticScope,
    SpeechAct,
    TemporalStatus,
)


def frame_from_dict(raw: dict[str, Any]) -> SemanticFrame:
    if not isinstance(raw, dict):
        raise ValueError("semantic frame must be an object")
    allowed = {"propositions", "unresolved_interpretations", "behavioral_hypotheses"}
    unknown = set(raw) - allowed
    if unknown:
        raise ValueError("unknown semantic frame fields: " + ", ".join(sorted(unknown)))

    propositions_raw = raw.get("propositions", [])
    unresolved = raw.get("unresolved_interpretations", [])
    hypotheses_raw = raw.get("behavioral_hypotheses", [])

    if not isinstance(propositions_raw, list) or not all(isinstance(x, dict) for x in propositions_raw):
        raise ValueError("semantic propositions must be a list of objects")
    if not isinstance(unresolved, list) or not all(isinstance(x, str) and x.strip() for x in unresolved):
        raise ValueError("unresolved_interpretations must be a list of non-empty strings")
    if not isinstance(hypotheses_raw, list) or not all(isinstance(x, dict) for x in hypotheses_raw):
        raise ValueError("behavioral_hypotheses must be a list of objects")

    return SemanticFrame(
        propositions=tuple(_proposition_from_dict(item) for item in propositions_raw),
        unresolved_interpretations=tuple(unresolved),
        behavioral_hypotheses=tuple(_behavior_from_dict(item) for item in hypotheses_raw),
    )


def _proposition_from_dict(raw: dict[str, Any]) -> SemanticProposition:
    allowed = {
        "anchor_id",
        "referent",
        "predicate",
        "force",
        "polarity",
        "scope",
        "speech_act",
        "temporal_status",
        "provenance",
    }
    unknown = set(raw) - allowed
    if unknown:
        raise ValueError("unknown semantic proposition fields: " + ", ".join(sorted(unknown)))
    missing = [key for key in ("anchor_id", "referent", "predicate") if key not in raw]
    if missing:
        raise ValueError("required semantic proposition fields missing: " + ", ".join(missing))

    scope_raw = raw.get("scope")
    scope = None
    if scope_raw is not None:
        if not isinstance(scope_raw, list) or not all(isinstance(x, str) and x.strip() for x in scope_raw):
            raise ValueError("semantic proposition scope must be a list of non-empty strings")
        scope = SemanticScope(members=frozenset(scope_raw))

    try:
        return SemanticProposition(
            anchor_id=raw["anchor_id"],
            referent=raw["referent"],
            predicate=raw["predicate"],
            force=Force(raw.get("force", "ASSERTED")),
            polarity=Polarity(raw.get("polarity", "AFFIRMED")),
            scope=scope,
            speech_act=SpeechAct(raw.get("speech_act", "DESCRIPTION")),
            temporal_status=TemporalStatus(raw.get("temporal_status", "CURRENT")),
            provenance=ProvenanceKind(raw.get("provenance", "UNKNOWN")),
        )
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid semantic proposition: {exc}") from exc


def _behavior_from_dict(raw: dict[str, Any]) -> BehavioralHypothesis:
    allowed = {"pattern", "subject", "evidence_refs", "rationale", "state"}
    unknown = set(raw) - allowed
    if unknown:
        raise ValueError("unknown behavioral hypothesis fields: " + ", ".join(sorted(unknown)))
    missing = [key for key in ("pattern", "subject", "evidence_refs", "rationale") if key not in raw]
    if missing:
        raise ValueError("required behavioral hypothesis fields missing: " + ", ".join(missing))
    refs = raw["evidence_refs"]
    if not isinstance(refs, list):
        raise ValueError("behavioral hypothesis evidence_refs must be a list")
    try:
        return BehavioralHypothesis(
            pattern=BehavioralPattern(raw["pattern"]),
            subject=raw["subject"],
            evidence_refs=tuple(refs),
            rationale=raw["rationale"],
            state=HypothesisState(raw.get("state", "PROPOSED")),
        )
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid behavioral hypothesis: {exc}") from exc
