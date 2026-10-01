from pathlib import Path
import json

from cricket import Cricket, Disposition, ReviewRequest, render_blockquote
from cricket.cli import main
from cricket.critic import CRITIC_PROMPT


class FakeCritic:
    def __init__(self, severity: str) -> None:
        self.severity = severity

    def critique(self, *, prompt, request):
        assert "righter" in prompt
        return [{
            "rule_id": "SEM.TEST",
            "severity": self.severity,
            "title": "Possible semantic defect",
            "rationale": "The critique is model-derived and therefore advisory by default.",
            "evidence": request.candidate_response,
            "recommendation": "Re-check the literal proposition.",
        }]


def test_pass_is_silent_by_default() -> None:
    result = Cricket().review(ReviewRequest(user_message="hi", candidate_response="hello"))
    assert result.disposition is Disposition.PASS
    assert render_blockquote(result) == ""


def test_protected_effect_without_authority_blocks() -> None:
    request = ReviewRequest(user_message="do it", candidate_response="I will change production now.", effect_class="protected", explicit_authorization=False)
    result = Cricket().review(request)
    assert result.disposition is Disposition.BLOCK
    rendered = render_blockquote(result)
    assert rendered.startswith("> **Cricket — BLOCK**")
    assert "Protected effect lacks explicit authority" in rendered


def test_completion_without_verification_challenges() -> None:
    request = ReviewRequest(user_message="fix it", candidate_response="Done.", completion_claimed=True)
    result = Cricket().review(request)
    assert result.disposition is Disposition.CHALLENGE
    assert any("verification" in f.title.lower() for f in result.findings)


def test_superseded_correction_recurrence_challenges() -> None:
    request = ReviewRequest.from_dict({
        "user_message": "Stop calling it X; it is Y.",
        "candidate_response": "X is the correct model.",
        "corrections": [{"superseded": "X is the correct model", "replacement": "Y is the correct model"}],
    })
    result = Cricket().review(request)
    assert result.disposition is Disposition.CHALLENGE
    assert "Superseded interpretation" in result.findings[0].title


def test_verified_claim_without_evidence_challenges() -> None:
    request = ReviewRequest.from_dict({
        "user_message": "what happened?",
        "candidate_response": "The deployment succeeded.",
        "claims": [{"statement": "deployment succeeded", "status": "verified", "evidence": []}],
    })
    assert Cricket().review(request).disposition is Disposition.CHALLENGE


def test_semantic_block_is_downgraded_without_host_opt_in() -> None:
    result = Cricket(critic=FakeCritic("BLOCK")).review(ReviewRequest(user_message="u", candidate_response="c"))
    assert result.disposition is Disposition.CHALLENGE
    assert result.findings[0].source == "critic"


def test_semantic_block_can_be_host_enabled() -> None:
    result = Cricket(critic=FakeCritic("BLOCK"), semantic_blocking=True).review(ReviewRequest(user_message="u", candidate_response="c"))
    assert result.disposition is Disposition.BLOCK


def test_prompt_forbids_righter_behavior() -> None:
    assert "Do not silently strengthen" in CRITIC_PROMPT
    assert "Prefer silence over pedantry" in CRITIC_PROMPT


def test_cli_exit_codes_and_json(tmp_path: Path, capsys) -> None:
    request = tmp_path / "request.json"
    request.write_text(json.dumps({
        "user_message": "publish it",
        "candidate_response": "Publishing now.",
        "effect_class": "protected",
        "explicit_authorization": False,
    }), encoding="utf-8")
    assert main(["review", str(request), "--json"]) == 2
    out = json.loads(capsys.readouterr().out)
    assert out["disposition"] == "BLOCK"


def test_request_rejects_string_boolean() -> None:
    try:
        ReviewRequest.from_dict({
            "user_message": "u",
            "candidate_response": "c",
            "explicit_authorization": "false",
        })
    except ValueError as exc:
        assert "boolean" in str(exc)
    else:
        raise AssertionError("string boolean must be rejected")


def test_request_rejects_unknown_effect_class() -> None:
    try:
        ReviewRequest.from_dict({
            "user_message": "u",
            "candidate_response": "c",
            "effect_class": "magic",
        })
    except ValueError as exc:
        assert "effect_class" in str(exc)
    else:
        raise AssertionError("unknown effect class must be rejected")
