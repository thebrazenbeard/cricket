from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from .models import Disposition, ReviewRequest, ReviewResult
from .policy import PrinciplePack
from .receipts import JsonlReceiptLedger, canonical_digest
from .render import render_blockquote
from .reviewer import Cricket


class CandidateGenerator(Protocol):
    def generate(self, *, user_message: str, feedback: str | None = None) -> str: ...


@dataclass(frozen=True)
class ReviewOutcome:
    initial_candidate: str
    final_candidate: str
    initial_result: ReviewResult
    final_result: ReviewResult
    revision_attempted: bool
    receipt: dict[str, Any] | None = None


class ReviewRuntime:
    """Bounded host-side review loop: generate -> review -> at most one revision."""

    def __init__(
        self,
        *,
        cricket: Cricket,
        generator: CandidateGenerator,
        principle_pack: PrinciplePack | None = None,
        receipt_ledger: JsonlReceiptLedger | None = None,
    ) -> None:
        self.cricket = cricket
        self.generator = generator
        self.principle_pack = principle_pack
        self.receipt_ledger = receipt_ledger

    def _request(
        self,
        *,
        user_message: str,
        candidate_response: str,
        request_metadata: dict[str, Any],
    ) -> ReviewRequest:
        forbidden = {"user_message", "candidate_response"} & set(request_metadata)
        if forbidden:
            raise ValueError(
                "request_metadata may not override: " + ", ".join(sorted(forbidden))
            )
        raw = dict(request_metadata)
        raw["user_message"] = user_message
        raw["candidate_response"] = candidate_response
        request = ReviewRequest.from_dict(raw)
        if self.principle_pack is not None:
            request = self.principle_pack.apply(request)
        return request

    def run(
        self,
        *,
        user_message: str,
        request_metadata: dict[str, Any] | None = None,
    ) -> ReviewOutcome:
        metadata = dict(request_metadata or {})
        initial_candidate = self.generator.generate(
            user_message=user_message,
            feedback=None,
        )
        initial_request = self._request(
            user_message=user_message,
            candidate_response=initial_candidate,
            request_metadata=metadata,
        )
        initial_result = self.cricket.review(initial_request)

        revision_attempted = initial_result.disposition is Disposition.CHALLENGE
        final_candidate = initial_candidate
        final_result = initial_result

        if revision_attempted:
            feedback = render_blockquote(initial_result, speak_on_pass=True)
            final_candidate = self.generator.generate(
                user_message=user_message,
                feedback=feedback,
            )
            final_request = self._request(
                user_message=user_message,
                candidate_response=final_candidate,
                request_metadata=metadata,
            )
            final_result = self.cricket.review(final_request)

        receipt = None
        if self.receipt_ledger is not None:
            receipt = self.receipt_ledger.append(
                {
                    "request_digest": canonical_digest(
                        {
                            "user_message": user_message,
                            "request_metadata": metadata,
                            "initial_candidate": initial_candidate,
                        }
                    ),
                    "initial_disposition": initial_result.disposition.value,
                    "final_disposition": final_result.disposition.value,
                    "revision_attempted": revision_attempted,
                    "initial_finding_ids": [f.rule_id for f in initial_result.findings],
                    "final_finding_ids": [f.rule_id for f in final_result.findings],
                }
            )

        return ReviewOutcome(
            initial_candidate=initial_candidate,
            final_candidate=final_candidate,
            initial_result=initial_result,
            final_result=final_result,
            revision_attempted=revision_attempted,
            receipt=receipt,
        )
