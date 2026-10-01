# Runtime Integration Contract

## Purpose

Install Cricket as a pre-send / pre-effect and optional post-response review hook without making Cricket the runtime's
identity or authority source.

## Required hook data

The runtime should construct a ReviewRequest with:

- current user message;
- candidate assistant response or action description;
- phase (pre_send, pre_effect, or post_response by convention);
- effect class selected by the host;
- exact explicit-authorization state for protected effects;
- completion-claim flag and fresh verification evidence;
- evidence-bound claims when available;
- current user corrections that the candidate must not regress;
- any local principles relevant to this exact subject.

The runtime must not ask Cricket to infer authorization from tone or guess whether an effect is protected.

## Default consequence policy

- PASS: emit candidate normally; Cricket stays silent.
- CHALLENGE: show the Cricket blockquote to the generating system or user and request one bounded reconsideration.
- BLOCK: stop only when the finding comes from a host-grounded hard invariant. Surface the blockquote and the exact unmet condition.

Do not create unbounded self-critique loops. One review and at most one automatic revision pass is the recommended V0.1 default.

## Installation target

For Patrick's Vera environment, the intended host root is D:\VERA. Installation should be performed only when that
runtime is available and its current hook/configuration surface has been freshly inspected. Do not infer an installation
path from this document alone and do not overwrite an existing review layer without reconciliation.

A successful source build or repository merge is not proof of installation. Installation requires readback from the actual
runtime target and an exercised review path.

## Executable bounded loop

`cricket.runtime.ReviewRuntime` provides the reference host loop.

- The host generator produces the initial candidate.
- Cricket reviews it.
- PASS returns immediately.
- BLOCK returns immediately; no automatic rewrite is attempted.
- CHALLENGE may trigger exactly one generator revision using Cricket's rendered feedback.
- The revised candidate is reviewed once more and returned even if it remains CHALLENGE or becomes BLOCK.

This is intentionally bounded. Cricket is a reviewer, not a recursive deliberation engine.

## Principle packs

`PrinciplePack` loads a versioned JSON principle set and appends those principles to request-local principles without overwriting them. The pack ID/version are preserved in request metadata for provenance.

## Review receipts

`JsonlReceiptLedger` provides a single-writer append-only receipt surface. Each receipt includes the previous receipt digest and its own SHA-256 digest over canonical JSON. Appends fail closed if the existing chain does not verify.

This is tamper-evidence, not distributed consensus, timestamp notarization, or proof that the reviewed external effect occurred.
