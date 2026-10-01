from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Force(str, Enum):
    POSSIBLE = "POSSIBLE"
    PROBABLE = "PROBABLE"
    ASSERTED = "ASSERTED"
    CERTAIN = "CERTAIN"


FORCE_RANK = {
    Force.POSSIBLE: 0,
    Force.PROBABLE: 1,
    Force.ASSERTED: 2,
    Force.CERTAIN: 3,
}


class TransformationKind(str, Enum):
    PRESERVED = "PRESERVED"
    STRENGTHENED = "STRENGTHENED"
    WEAKENED = "WEAKENED"
    REFERENT_CHANGED = "REFERENT_CHANGED"
    PREDICATE_CHANGED = "PREDICATE_CHANGED"
    DROPPED = "DROPPED"
    ADDED = "ADDED"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class SemanticProposition:
    anchor_id: str
    referent: str
    predicate: str
    force: Force = Force.ASSERTED

    def __post_init__(self) -> None:
        for name, value in (
            ("anchor_id", self.anchor_id),
            ("referent", self.referent),
            ("predicate", self.predicate),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be non-empty text")
        if not isinstance(self.force, Force):
            raise ValueError("force must be a Force")


@dataclass(frozen=True)
class SemanticFrame:
    propositions: tuple[SemanticProposition, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.propositions, tuple) or not all(
            isinstance(item, SemanticProposition) for item in self.propositions
        ):
            raise ValueError("propositions must be a tuple of SemanticProposition objects")
        anchors = [item.anchor_id for item in self.propositions]
        if len(anchors) != len(set(anchors)):
            raise ValueError("semantic proposition anchor_id values must be unique")


@dataclass(frozen=True)
class SemanticChange:
    anchor_id: str
    kind: TransformationKind
    source: SemanticProposition | None
    candidate: SemanticProposition | None
    material: bool
    rationale: str


@dataclass(frozen=True)
class SemanticIntegrityReport:
    changes: tuple[SemanticChange, ...]

    @property
    def material_change(self) -> bool:
        return any(change.material for change in self.changes)
