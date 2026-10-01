# Cricket ordinary-Chat projection

This directory is the reproducible source for Cricket's private ChatGPT plugin projection.

It exists because ordinary Chat currently does **not** expose the same platform-enforced lifecycle hooks available to ChatGPT Work/Codex. Plugin skill selection is relevance-based and is not a platform guarantee that a skill runs on every ordinary-chat request.

The strongest ordinary-Chat workaround is therefore layered:

1. install the private `cricket-conscience` plugin;
2. give the plugin deliberately broad ordinary-chat activation metadata;
3. include `cricket-ordinary-chat-default`, whose activation description covers every normal user request;
4. place `CUSTOM_INSTRUCTIONS.md` in account-level ChatGPT Custom Instructions so every ordinary chat explicitly asks the model to apply Cricket;
5. when an executable hook surface is available, prefer the actual Cricket runtime over instruction-only review.

This is not a platform-enforced lifecycle hook. It is an instruction-layer projection with high-recall activation intent.

## Source of truth

- core package/reviewer behavior: `src/cricket/`;
- canonical persona: `src/cricket/persona.py`;
- ordinary-chat projection: this directory.

The parity tests in `tests/test_chatgpt_projection.py` protect critical invariants and the canonical persona motto from silent drift.

## Packaging

Run:

```bash
python scripts/build_chatgpt_plugin.py
```

The output archive can be uploaded as a private ChatGPT plugin release.
