from cricket.semantic import (
    Force,
    SemanticFrame,
    SemanticIntegrityAnalyzer,
    SemanticProposition,
    TransformationKind,
)


def test_semantic_analyzer_detects_modality_strengthening() -> None:
    source = SemanticFrame(
        propositions=(
            SemanticProposition(
                anchor_id="p1",
                referent="cricket",
                predicate="needs_personality",
                force=Force.PROBABLE,
            ),
        )
    )
    candidate = SemanticFrame(
        propositions=(
            SemanticProposition(
                anchor_id="p1",
                referent="cricket",
                predicate="needs_personality",
                force=Force.ASSERTED,
            ),
        )
    )

    report = SemanticIntegrityAnalyzer().compare(source, candidate)

    assert report.material_change is True
    assert [change.kind for change in report.changes] == [TransformationKind.STRENGTHENED]
