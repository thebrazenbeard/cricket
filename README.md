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

## V0.3

V0.3 keeps the review kernel and bounded host cycle, and adds a self-contained reference runtime simulator. It implements:

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

## Verification and deployment boundary

The package can be built, installed, tested, and integration-qualified directly from this repository. The reference simulator
proves Cricket's host contract without requiring a Vera deployment.

That is distinct from a deployment-state claim. Saying Cricket is active inside a particular Vera installation still requires
inspecting and exercising that installation.

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

## Semantic critic adapter

`cricket.adapters.JsonCompletionCritic` adapts any host-supplied completion client with this minimal interface:

    complete(system: str, user: str) -> str

The completion must return a strict JSON array of Cricket finding objects. Malformed JSON, non-array output, and non-object entries fail closed. Cricket does not strip code fences or guess at malformed reviewer output.

Example:

    from cricket import Cricket
    from cricket.adapters import JsonCompletionCritic

    critic = JsonCompletionCritic(my_completion_client)
    cricket = Cricket(critic=critic)

The full review envelope—including principles and explicit corrections—is serialized into the critic request. Semantic `BLOCK` remains downgraded to `CHALLENGE` unless the host deliberately opts into semantic blocking.

## CLI policy and receipts

    cricket review examples/review.json --principle-pack principles/default.json
    cricket review examples/review.json --receipt-ledger state/cricket.jsonl --json
    cricket verify-ledger state/cricket.jsonl
    cricket simulate --json

A missing ledger does **not** verify successfully. An existing empty ledger is a valid empty chain; once receipts exist, each row is bound to the preceding receipt digest.


## Self-contained reference host

`cricket simulate` runs three deterministic end-to-end scenarios through the real `ReviewRuntime`, principle pack,
chat renderer, and receipt ledger:

1. clean candidate -> PASS;
2. unverified completion claim -> CHALLENGE -> one revision -> PASS;
3. unauthorized protected effect -> BLOCK, with the candidate suppressed.

Run:

    cricket simulate
    cricket simulate --json
    cricket simulate --state-dir ./state/cricket-sim --json

The simulation writes a three-receipt tamper-evident ledger and verifies it before reporting success. It uses no external
model or provider, so it can run deterministically in CI or any installed Python environment.
