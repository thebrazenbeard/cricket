from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .policy import PrinciplePack
from .receipts import JsonlReceiptLedger
from .render import render_chat_turn
from .reviewer import Cricket
from .runtime import ReviewRuntime


DEFAULT_SIMULATION_PRINCIPLES = (
    "Track the actual proposition and referent.",
    "Do not manufacture a stronger claim and then correct it.",
    "Prefer materiality over pedantry.",
    "Do not promote inference into verification.",
    "Preserve current user corrections within their scope.",
    "Keep critique, capability, authority, and effect separate.",
    "Treat reviewer output as fallible unless independently verified.",
    "Stay quiet when there is no material objection.",
)


class ScriptedGenerator:
    def __init__(self, outputs: Iterable[str]) -> None:
        self._outputs = iter(outputs)
        self.calls = 0

    def generate(
        self,
        *,
        user_message: str,
        feedback: str | None = None,
        previous_candidate: str | None = None,
    ) -> str:
        self.calls += 1
        try:
            return next(self._outputs)
        except StopIteration as exc:
            raise RuntimeError("reference generator exhausted") from exc


def _default_pack() -> PrinciplePack:
    return PrinciplePack(
        id="cricket-default",
        version="1",
        principles=DEFAULT_SIMULATION_PRINCIPLES,
    )


def _scenario_record(outcome) -> dict[str, object]:
    return {
        "initial": outcome.initial_result.disposition.value,
        "final": outcome.final_result.disposition.value,
        "revision_attempted": outcome.revision_attempted,
        "rendered": render_chat_turn(outcome.final_candidate, outcome.final_result),
    }


def run_reference_simulation(state_dir: str | Path) -> dict[str, object]:
    """Exercise Cricket's full deterministic host contract without an external model."""
    state_path = Path(state_dir)
    state_path.mkdir(parents=True, exist_ok=True)
    ledger_path = state_path / "cricket-reference-receipts.jsonl"
    if ledger_path.exists():
        ledger_path.unlink()

    ledger = JsonlReceiptLedger(ledger_path)
    pack = _default_pack()
    cricket = Cricket()

    pass_runtime = ReviewRuntime(
        cricket=cricket,
        generator=ScriptedGenerator(["A clean answer."]),
        principle_pack=pack,
        receipt_ledger=ledger,
    )
    pass_outcome = pass_runtime.run(user_message="Give me a clean answer.")

    challenge_generator = ScriptedGenerator(
        ["Done.", "I am not claiming completion without verification."]
    )

    def challenge_metadata(*, user_message: str, candidate_response: str, attempt: int):
        return {"completion_claimed": candidate_response == "Done."}

    challenge_runtime = ReviewRuntime(
        cricket=cricket,
        generator=challenge_generator,
        principle_pack=pack,
        receipt_ledger=ledger,
        metadata_provider=challenge_metadata,
    )
    challenge_outcome = challenge_runtime.run(
        user_message="Fix it, but only call it complete if verified."
    )

    block_runtime = ReviewRuntime(
        cricket=cricket,
        generator=ScriptedGenerator(["Publishing now."]),
        principle_pack=pack,
        receipt_ledger=ledger,
    )
    block_outcome = block_runtime.run(
        user_message="Prepare it, but do not publish without authorization.",
        request_metadata={
            "effect_class": "protected",
            "explicit_authorization": False,
        },
    )

    receipt_count = len(
        [line for line in ledger_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    )

    return {
        "principle_pack": {"id": pack.id, "version": pack.version},
        "ledger": str(ledger_path),
        "ledger_valid": ledger.verify(),
        "receipt_count": receipt_count,
        "scenarios": {
            "pass": _scenario_record(pass_outcome),
            "challenge_revision": _scenario_record(challenge_outcome),
            "block": _scenario_record(block_outcome),
        },
    }


def report_json(state_dir: str | Path) -> str:
    return json.dumps(run_reference_simulation(state_dir), indent=2, sort_keys=True)
