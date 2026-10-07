# Tattler reasoning-surface results — 2026-10-07

Status: REVIEW EVIDENCE / INDEPENDENCE AND CLAIM-CEILING INPUT

## Shared experiment result

On 2026-10-07, the same repository stress-test prompt was run through three ChatGPT surfaces while WorkLaptop was instrumented with Tattler plus a companion Codex process/network tracer.

Observed controlled windows:

- Desktop Chat, GPT-5.6 Sol High: **0 MXC launches** and **2 new established Codex TLS connections** in the companion tracer.
- ChatGPT Desktop Work, Ultra: **59 MXC launches** and **73 new established Codex TLS connections** using the same companion-tracer definitions.
- Firefox cloud Work, Max: browser-side traffic was observable locally, but the provider's server-side worker topology was not.

The bounded conclusion is that Desktop Work used materially different local orchestration from ordinary High Chat in this runtime. It does **not** establish that sockets or MXC processes equal agents, that connection fanout grants a reasoning tier, or that a client can promote High into Ultra/Max by imitating transport behavior.

Canonical detailed evidence is being preserved in `thebrazenbeard/tattler` PR #7 and the reasoning interpretation in `thebrazenbeard/rezon` PR #103.


## Why Cricket needs this result

Cricket already treats model self-critique as non-independent evidence. The Ultra/Max comparison supplies a concrete adjacent case: different reasoning labels and product surfaces can produce useful convergence without automatically establishing independent evidence.

For any semantic critic or external reviewer receipt, preserve:
- provider/model family when known;
- product surface and reasoning label;
- prompt lineage;
- exact subject/head;
- shared context/evidence;
- whether the reviewer saw the candidate or another review;
- tool/runtime overlap.

```text
different reasoning label != independent evidence
different product surface != independent evidence
different process/socket topology != independent cognition
```

## Observability implication

Tattler can help show that two local execution paths differ operationally. That is useful evidence about runtime behavior, but Cricket must not use MXC count, socket count, or endpoint diversity as a shortcut for reviewer independence or critique quality.
