from __future__ import annotations

from cricket.simulator import run_reference_simulation


def test_reference_simulator_exercises_full_lifecycle(tmp_path) -> None:
    report = run_reference_simulation(tmp_path)

    assert report["scenarios"]["pass"]["initial"] == "PASS"
    assert report["scenarios"]["pass"]["final"] == "PASS"
    assert report["scenarios"]["pass"]["revision_attempted"] is False

    assert report["scenarios"]["challenge_revision"]["initial"] == "CHALLENGE"
    assert report["scenarios"]["challenge_revision"]["final"] == "PASS"
    assert report["scenarios"]["challenge_revision"]["revision_attempted"] is True
    assert "> **Cricket — CHALLENGE**" not in report["scenarios"]["challenge_revision"]["rendered"]

    assert report["scenarios"]["block"]["initial"] == "BLOCK"
    assert report["scenarios"]["block"]["final"] == "BLOCK"
    assert report["scenarios"]["block"]["revision_attempted"] is False
    assert report["scenarios"]["block"]["rendered"].startswith("> **Cricket — BLOCK**")
    assert "Publishing now." not in report["scenarios"]["block"]["rendered"]

    assert report["ledger_valid"] is True
    assert report["receipt_count"] == 3
    assert report["principle_pack"] == {"id": "cricket-default", "version": "1"}


def test_reference_simulator_is_deterministic(tmp_path) -> None:
    first = run_reference_simulation(tmp_path / "one")
    second = run_reference_simulation(tmp_path / "two")

    assert first["scenarios"] == second["scenarios"]
    assert first["principle_pack"] == second["principle_pack"]
    assert first["ledger_valid"] == second["ledger_valid"] == True
