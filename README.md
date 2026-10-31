# Cricket — AI response and action-review hook

Cricket is a **provider-neutral Python package and CLI** for reviewing proposed AI responses and actions before a host emits or executes them. It combines deterministic checks with an optional semantic critic, preserves disagreements as review findings, and can render interventions as clearly attributed Markdown blockquotes.

Use it to add a bounded review step to an application, test review policies offline, or inspect compatibility assumptions against upstream projects. Cricket does **not** execute protected actions, authenticate providers, issue consent, or replace a host's authorization service.

## Capabilities

| Surface | What is implemented | Important boundary |
| --- | --- | --- |
| `Cricket().review(...)` | Deterministic `PASS`, `CHALLENGE`, or `BLOCK` findings for structured requests | The host must truthfully classify effects and supply authorization/evidence fields |
| Semantic review | Typed proposition, referent, modality, scope, provenance, and correction checks; optional completion-client critic | Model-generated critique is advisory; semantic `BLOCK` is downgraded by default |
| Behavioral interpretation | Evidence-linked hypotheses and rival explanations | Not a diagnosis or proof of anyone's motives |
| `ReviewRuntime` | Initial review, at most one candidate revision, then final review | `BLOCK` never triggers an automatic retry |
| `cricket simulate` | Five deterministic host-contract scenarios and a receipt ledger | A reference simulation, not proof of deployed integration |
| JSONL receipts | SHA-256-linked append/verification of local review entries | Tamper-evident is not tamper-proof or an externally trusted audit service |
| `cricket upstreams` | Compare host-supplied Git commit observations with pinned compatibility baselines | No network fetch; `MOVED` requires re-review, not proof of incompatibility |

The repository contains JSON schemas under [`schemas/`](schemas/review-request.schema.json), principle packs under [`principles/`](principles/default.json), and a sample host adapter in [`examples/host_runtime.py`](examples/host_runtime.py).

## Install and try it

Requires **Python 3.11+**. From a checkout:

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
python -m pytest
```

Inspect an example review request:

```bash
cricket review examples/review.json --json
```

The supplied example is deliberately an **unauthorized protected effect**. It reports `BLOCK` and exits with code `2`; that nonzero exit is an expected policy result, not a failed installation.

Run the self-contained host simulation:

```bash
cricket simulate --state-dir ./cricket-sim --json
cricket verify-ledger ./cricket-sim/cricket-reference-receipts.jsonl
```

The simulation produces five review receipts and verifies its own chain. Use a writable state directory; treat the files as local test evidence, not an authority grant.

Python integration:

```python
from cricket import Cricket, ReviewRequest, render_blockquote

request = ReviewRequest(
    user_message="Tell me when the operation is verified.",
    candidate_response="It is complete.",
    completion_claimed=True,
)
result = Cricket().review(request)
print(result.disposition.value)
print(render_blockquote(result))
```

See [`docs/RUNTIME_INTEGRATION.md`](docs/RUNTIME_INTEGRATION.md) for the structured host contract. The host retains effect execution, independently verified authorization, and the final decision on how to use review findings.

### Command reference

```bash
cricket review examples/review.json --principle-pack principles/default.json --json
cricket review examples/review.json --receipt-ledger ./review-receipts.jsonl
cricket verify-ledger ./review-receipts.jsonl
cricket prompt
cricket upstreams --observed ./observed-heads.json --json
```

For `review`, exit codes are `0=PASS`, `1=CHALLENGE`, `2=BLOCK`. For `upstreams`, they are `0=CURRENT`, `1=UNKNOWN`, `2=MOVED`. Supply `observed-heads.json` as a JSON mapping from repository names to Git commit IDs collected by your own trusted observer; a missing observation remains `UNKNOWN`.

## Where Cricket belongs

An application can call Cricket at the **pre-send/pre-effect** boundary and optionally after a response. Host-supplied fields, not the model's assertions, determine protected effect classification and the authorization evidence available to the deterministic rules. An optional completion client can formulate a critique, but cannot mint permissions or override a host-grounded block.

The named **Cricket persona** is a presentation style (candor, concise loyal opposition, and occasional dry humor), not a separate legal principal or proof of independent consciousness. The repository borrows the *narrative analogy* of a conscience without copying the fictional character or its material. See [`personality/CRICKET_PERSONA.md`](personality/CRICKET_PERSONA.md).

## Evidence and limits

- Structural rules and passing tests demonstrate the implemented review behavior on covered cases. They do not establish factual truth, general AI reliability, provider identity, verified human consent, or operational host enforcement.
- Semantic and behavioral hypotheses are explicitly uncertain. An LLM's disagreement is not independent verification or evidence of the user's hidden motives.
- Upstream compatibility status is bound to the pinned and observed Git commits; a source change makes prior qualification historical. See [`docs/UPSTREAM_CURRENTNESS.md`](docs/UPSTREAM_CURRENTNESS.md).
- The historical editor-startup loader was removed by a source-security repair; it must not be treated as an authorized installation mechanism.
- There is **no root `LICENSE` or `COPYING` file in this checkout**. Public source visibility alone does not grant permission for redistribution or commercial reuse; obtain the copyright holder's terms before those uses.

For threat boundaries, research rationale, and integration details, see [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), [`docs/RESEARCH.md`](docs/RESEARCH.md), and [`docs/WEBHOOK_INJECTION.md`](docs/WEBHOOK_INJECTION.md).
