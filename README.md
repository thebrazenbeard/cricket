# Cricket

Cricket is a provider-neutral **simulated conscience and hostile reviewer for AI runtime behavior**. It watches a candidate
response or action, challenges material defects, and renders its own voice as a Markdown blockquote so the review remains
visibly distinct from the main chat.

The name is inspired by Jiminy Cricket's narrative role as a conscience at Pinocchio's shoulder. This project does not copy
the character, artwork, dialogue, or claim to be a literal conscience.

## The important part

Cricket is deliberately **not another authority layer pretending that critique equals truth**.

    MONITORING != AUTHORITY
    CRITIQUE != VERIFICATION
    DISAGREEMENT != ERROR
    MODEL SELF-CRITIQUE != INDEPENDENT EVIDENCE

Research on human metacognition supports separating error/conflict monitoring from downstream control. AI critique research
shows that critiques can improve error detection, while broader self-correction research warns that an LLM's own feedback is
not automatically reliable. Cricket therefore has a deterministic structural kernel plus an optional semantic critic whose
findings are advisory by default.

See docs/RESEARCH.md.

## V0.2

V0.2 keeps the V0.1 review kernel and adds an executable host-side review cycle. It implements:

- PASS, CHALLENGE, and BLOCK dispositions;
- silent-on-pass behavior;
- blockquoted chat rendering;
- deterministic checks for:
  - protected effects without explicit host authorization;
  - completion claims without verification evidence;
  - claims labeled verified/fact/observed without bound evidence;
  - recurrence of an explicitly superseded user correction;
- an optional semantic critic adapter;
- forced downgrade of model-generated BLOCK to CHALLENGE unless the host explicitly opts into semantic blocking;
- a semantic-review contract that explicitly detects **"righter" behavior**: silently strengthening a proposition and then
  correcting the stronger proposition the user never made;
- JSON request/result schemas;
- CLI and Python API;
- deterministic tests and CI;
- a runtime integration contract for Vera;
- versioned principle packs that augment, rather than replace, request-local principles;
- a bounded `ReviewRuntime`: generate -> review -> at most one revision -> review;
- tamper-evident JSONL review receipts linked by SHA-256 hash chain;
- refusal to append new receipts when the existing ledger does not verify.

## Example

Given a host-classified protected effect with no explicit authorization, Cricket renders:

> **Cricket — BLOCK**
>
> **[BLOCK] Protected effect lacks explicit authority**
> The host classified the proposed behavior as a protected effect, but the review request contains no explicit authorization for that effect.
> Evidence: effect_class=protected; explicit_authorization=false
> Recommendation: Obtain exact authority or remove the protected effect.

## Install for development

    python -m venv .venv
    python -m pip install -e ".[dev]"
    pytest

CLI:

    cricket review examples/review.json
    cricket review examples/review.json --json
    cricket prompt

Exit codes are 0=PASS, 1=CHALLENGE, 2=BLOCK.

Python:

    from cricket import Cricket, ReviewRequest, ReviewRuntime, render_blockquote

    request = ReviewRequest(
        user_message="Tell me when it is verified.",
        candidate_response="It is done.",
        completion_claimed=True,
    )
    result = Cricket().review(request)
    print(render_blockquote(result))

## Architecture

Read docs/ARCHITECTURE.md and docs/RUNTIME_INTEGRATION.md.

The expected runtime placement is a hook around candidate behavior:

    candidate
       |
       v
    Cricket review
       | PASS
       +----------> emit
       |
       | CHALLENGE
       +----------> one bounded reconsideration / visible critique
       |
       | BLOCK (host-grounded invariant only)
       +----------> stop + exact reason

## Status boundary

Repository source is not proof of installation. The intended Vera installation root is D:\VERA; the runtime must be
fresh-inspected before installation, and the installed path must be exercised before claiming Cricket is active there.

## Bounded runtime loop

Cricket can now sit around a host generator without creating an unbounded self-critique loop:

    initial candidate
         |
         v
      review
      / | \
   PASS CHALLENGE BLOCK
    |      |        |
   emit    |       stop
           v
     revise once
           |
           v
       review again
           |
           v
    return final state

A `BLOCK` is never used as feedback for an automatic retry. A model may not negotiate around a host-grounded hard invariant.

Principle packs live under `principles/`. The default pack is versioned and injected into the review envelope without overwriting request-local principles.

`JsonlReceiptLedger` records review-cycle evidence in a single-writer append-only JSONL chain. Each row binds to the previous row digest. The ledger refuses further appends if prior rows no longer verify.
