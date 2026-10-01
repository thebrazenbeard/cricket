import json
from pathlib import Path

from cricket.persona import DEFAULT_CRICKET_PERSONA


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "integrations" / "chatgpt"


def read(path: str) -> str:
    return (PLUGIN / path).read_text(encoding="utf-8")


def test_chatgpt_projection_manifest_is_high_recall_and_private_plugin_ready() -> None:
    manifest = json.loads(read("plugin.json"))
    assert manifest["name"] == "cricket-conscience"
    assert manifest["version"] == "0.2.0"
    description = manifest["description"].casefold()
    assert "ordinary-chat" in description
    assert "every normal" in description or "always-on" in description
    keywords = {item.casefold() for item in manifest["keywords"]}
    assert {"ordinary-chat", "always-on", "conscience"} <= keywords


def test_ordinary_chat_default_skill_explicitly_applies_to_every_normal_turn() -> None:
    skill = read("skills/ordinary-chat-default/SKILL.md")
    header = skill.split("---", 2)[1].casefold()
    assert "every ordinary chatgpt conversation" in header
    assert "every normal user request" in header
    assert "unless the user explicitly opts out" in header


def test_full_cricket_skill_preserves_core_invariants() -> None:
    skill = read("skills/cricket/SKILL.md")
    for invariant in (
        "CRITIQUE != AUTHORITY",
        "PERSONALITY != AUTHORITY",
        "SASS != EVIDENCE",
        "CONFIDENCE != VERIFICATION",
        "OBSERVED_BEHAVIOR != HIDDEN_MOTIVE_FACT",
        "DISAGREEMENT != ERROR",
    ):
        assert invariant in skill
    assert "Righter" in skill
    assert "one bounded Cricket review pass" in skill
    assert "At most one automatic revision pass" in skill


def test_projected_persona_matches_canonical_cricket_persona() -> None:
    persona = read("skills/cricket/references/CRICKET_PERSONA.md")
    assert DEFAULT_CRICKET_PERSONA.motto in persona
    for trait in ("absolute candor", "dry", "self-skeptic"):
        assert trait in persona.casefold()


def test_custom_instructions_force_cricket_as_account_level_default() -> None:
    instructions = read("CUSTOM_INSTRUCTIONS.md")
    folded = instructions.casefold()
    assert "cricket-conscience" in folded
    assert "every turn" in folded
    assert "cricket off" in folded
    assert "one bounded cricket review pass" in folded
    assert "silent" in folded and "clean" in folded
    assert "righter" in folded


def test_projection_documents_platform_guarantee_ceiling() -> None:
    docs = read("README.md")
    assert "not a platform-enforced lifecycle hook" in docs
    assert "relevance-based" in docs
    assert "Custom Instructions" in docs
