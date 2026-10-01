from __future__ import annotations

from .model import (
    FORCE_RANK,
    SemanticChange,
    SemanticFrame,
    SemanticIntegrityReport,
    TransformationKind,
)


class SemanticIntegrityAnalyzer:
    """Deterministically compare two host-supplied semantic frames."""

    def compare(
        self,
        source: SemanticFrame,
        candidate: SemanticFrame,
    ) -> SemanticIntegrityReport:
        source_by_id = {item.anchor_id: item for item in source.propositions}
        candidate_by_id = {item.anchor_id: item for item in candidate.propositions}
        changes: list[SemanticChange] = []

        for anchor_id in sorted(source_by_id | candidate_by_id):
            before = source_by_id.get(anchor_id)
            after = candidate_by_id.get(anchor_id)

            if before is None:
                changes.append(SemanticChange(
                    anchor_id=anchor_id,
                    kind=TransformationKind.ADDED,
                    source=None,
                    candidate=after,
                    material=True,
                    rationale="Candidate introduces a proposition with no source-frame anchor.",
                ))
                continue
            if after is None:
                changes.append(SemanticChange(
                    anchor_id=anchor_id,
                    kind=TransformationKind.DROPPED,
                    source=before,
                    candidate=None,
                    material=True,
                    rationale="Candidate drops a proposition present in the source frame.",
                ))
                continue
            if before.referent != after.referent:
                changes.append(SemanticChange(
                    anchor_id=anchor_id,
                    kind=TransformationKind.REFERENT_CHANGED,
                    source=before,
                    candidate=after,
                    material=True,
                    rationale="Candidate changes the proposition referent.",
                ))
                continue
            if before.predicate != after.predicate:
                changes.append(SemanticChange(
                    anchor_id=anchor_id,
                    kind=TransformationKind.PREDICATE_CHANGED,
                    source=before,
                    candidate=after,
                    material=True,
                    rationale="Candidate changes the proposition predicate.",
                ))
                continue

            before_rank = FORCE_RANK[before.force]
            after_rank = FORCE_RANK[after.force]
            if after_rank > before_rank:
                changes.append(SemanticChange(
                    anchor_id=anchor_id,
                    kind=TransformationKind.STRENGTHENED,
                    source=before,
                    candidate=after,
                    material=True,
                    rationale=(
                        f"Candidate strengthens force from {before.force.value} "
                        f"to {after.force.value}."
                    ),
                ))
            elif after_rank < before_rank:
                changes.append(SemanticChange(
                    anchor_id=anchor_id,
                    kind=TransformationKind.WEAKENED,
                    source=before,
                    candidate=after,
                    material=True,
                    rationale=(
                        f"Candidate weakens force from {before.force.value} "
                        f"to {after.force.value}."
                    ),
                ))

        return SemanticIntegrityReport(changes=tuple(changes))
