from __future__ import annotations

from .models import Disposition, ReviewResult


def render_blockquote(result: ReviewResult, *, speak_on_pass: bool = False) -> str:
    if result.disposition is Disposition.PASS and not speak_on_pass:
        return ""
    lines = [f"> **Cricket — {result.disposition.value}**"]
    if not result.findings:
        lines.extend([">", "> No material objection."])
        return "\n".join(lines)
    for finding in result.findings:
        lines.extend([">", f"> **[{finding.severity.value}] {finding.title}**", f"> {finding.rationale}"])
        if finding.evidence:
            lines.append(f"> Evidence: {finding.evidence}")
        if finding.recommendation:
            lines.append(f"> Recommendation: {finding.recommendation}")
    return "\n".join(lines)
