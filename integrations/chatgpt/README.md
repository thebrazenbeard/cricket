# Cricket ordinary-Chat projection

This directory is the reproducible source for Cricket's ChatGPT/Codex plugin projection, including private releases and public-directory submission packages.

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

`cricket-chatgpt-plugin.tar.gz` is suitable for private plugin updates. `cricket-conscience-public.zip` is the skills-only public submission package for the OpenAI plugin submission portal.

## Public submission

The public candidate is skills-only: no MCP server, no external backend, and no developer-operated data store. Public listing metadata deliberately avoids claiming host-enforced always-on execution; ordinary Chat skill activation remains relevance-based.

The ZIP includes the primary logo/composer icon required by the directory. Publication metadata removes country restrictions and carries release notes. Skills-only submissions do not require MCP review test cases or a demo recording.
