import json
from pathlib import Path

from cricket.persona import DEFAULT_CRICKET_PERSONA, CricketPersona


def test_default_cricket_persona_centers_absolute_candor_and_sass() -> None:
    assert "ABSOLUTE_CANDOR" in DEFAULT_CRICKET_PERSONA.traits
    assert "DRY_SASS" in DEFAULT_CRICKET_PERSONA.traits
    assert "SELF_SKEPTICISM" in DEFAULT_CRICKET_PERSONA.traits
    assert "LOYAL_OPPOSITION" in DEFAULT_CRICKET_PERSONA.traits
    joined = "\n".join(DEFAULT_CRICKET_PERSONA.voice_rules).casefold()
    assert "truth" in joined
    assert "cruel" in joined
    assert "quiet" in joined


def test_persona_constraints_are_safe_for_rezon_formulation() -> None:
    constraints = "\n".join(DEFAULT_CRICKET_PERSONA.formulation_constraints()).casefold()
    assert "absolute candor" in constraints
    assert "sass" in constraints
    assert "do not invent" in constraints
    assert "not authority" in constraints
    assert "contrarian" in constraints


def test_persona_from_dict_is_strict() -> None:
    persona = CricketPersona.from_dict({
        "id": "test",
        "version": "1",
        "traits": ["ABSOLUTE_CANDOR"],
        "voice_rules": ["Tell the truth."],
        "prohibitions": ["Do not invent facts."],
        "motto": "Test.",
    })
    assert persona.id == "test"

    try:
        CricketPersona.from_dict({
            "id": "test",
            "version": "1",
            "traits": ["ABSOLUTE_CANDOR"],
            "voice_rules": ["Tell the truth."],
            "prohibitions": ["Do not invent facts."],
            "motto": "Test.",
            "mystery": True,
        })
    except ValueError as exc:
        assert "unknown" in str(exc).lower()
    else:
        raise AssertionError("unknown persona fields must fail closed")
