import json
from pathlib import Path

from cricket.persona import DEFAULT_CRICKET_PERSONA


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "integrations" / "chatgpt"


def read(path: str) -> str:
    return (PLUGIN / path).read_text(encoding="utf-8")


def test_chatgpt_projection_manifest_is_public_submission_ready() -> None:
    manifest = json.loads(read("plugin.json"))
    assert manifest["name"] == "cricket-conscience"
    assert manifest["version"] == "0.4.0"
    description = manifest["description"].casefold()
    assert "ordinary-chat" in description
    assert "response review" in description
    keywords = {item.casefold() for item in manifest["keywords"]}
    assert {"ordinary-chat", "review", "conscience"} <= keywords


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


def test_plugin_builder_packages_only_plugin_runtime_files(tmp_path, monkeypatch) -> None:
    import importlib.util
    import tarfile

    script = ROOT / "scripts" / "build_chatgpt_plugin.py"
    spec = importlib.util.spec_from_file_location("build_chatgpt_plugin", script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    output = tmp_path / "cricket-chatgpt-plugin.tar.gz"
    monkeypatch.setattr(module, "DIST", tmp_path)
    monkeypatch.setattr(module, "OUTPUT", output)

    built = module.build()
    assert built == output
    assert built.is_file()

    with tarfile.open(built, "r:gz") as archive:
        names = set(archive.getnames())

    assert "plugin.json" in names
    assert ".codex-plugin/plugin.json" in names
    assert "skills/cricket/SKILL.md" in names
    assert "skills/ordinary-chat-default/SKILL.md" in names
    assert "README.md" not in names
    assert "CUSTOM_INSTRUCTIONS.md" not in names


def test_public_submission_manifest_and_privacy_contract() -> None:
    manifest = json.loads(read("plugin.json"))
    interface = manifest["extensions"]["com.openai"]["interface"]

    assert manifest["version"] == "0.4.0"
    assert len(interface["displayName"]) <= 30
    assert len(interface["shortDescription"]) <= 30
    assert len(interface["longDescription"]) <= 4000
    assert len(interface["developerName"]) <= 80
    assert interface["category"] == "Developer Tools"
    assert 1 <= len(interface["capabilities"]) <= 20
    assert interface["privacyPolicyURL"].startswith("https://github.com/thebrazenbeard/cricket/")
    assert interface["supportURL"].startswith("https://github.com/thebrazenbeard/cricket/")
    assert "always-on" not in interface["longDescription"].casefold()
    publication = manifest["extensions"]["com.openai"]["publication"]
    assert publication["countries"] == []
    assert "initial public skills-only release" in publication["release_notes"].casefold()

    privacy = (ROOT / "PRIVACY.md").read_text(encoding="utf-8").casefold()
    assert "does not operate an external server" in privacy
    assert "does not independently collect" in privacy
    assert "retention" in privacy
    assert "user controls" in privacy


def test_public_zip_contains_complete_skills_only_package(tmp_path, monkeypatch) -> None:
    import importlib.util
    import zipfile

    script = ROOT / "scripts" / "build_chatgpt_plugin.py"
    spec = importlib.util.spec_from_file_location("build_chatgpt_plugin_public", script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    monkeypatch.setattr(module, "DIST", tmp_path)
    monkeypatch.setattr(module, "OUTPUT", tmp_path / "cricket-chatgpt-plugin.tar.gz")
    monkeypatch.setattr(module, "PUBLIC_OUTPUT", tmp_path / "cricket-conscience-public.zip")

    built = module.build_public_zip()
    assert built.name == "cricket-conscience-public.zip"
    with zipfile.ZipFile(built) as archive:
        names = set(archive.namelist())
    assert "plugin.json" in names
    assert ".codex-plugin/plugin.json" in names
    assert "skills/cricket/SKILL.md" in names
    assert "skills/ordinary-chat-default/SKILL.md" in names
    assert "assets/cricket-256.png" in names
    assert "README.md" not in names
    assert "CUSTOM_INSTRUCTIONS.md" not in names
