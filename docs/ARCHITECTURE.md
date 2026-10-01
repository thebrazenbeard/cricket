# Cricket Architecture V0.1

Cricket is a provider-neutral **simulated conscience and hostile-review layer** for AI runtime behavior.
It is not a second identity, moral oracle, policy authority, or hidden agent. It reviews a concrete candidate
response/action against explicit evidence and host-supplied boundaries, then emits a distinct blockquoted voice.

## Control loop

    user/context
        |
        v
    candidate response/action
        |
        v
    Cricket review
        |
        +--> PASS ------> normal response
        +--> CHALLENGE -> bounded reconsideration / visible critique
        +--> BLOCK -----> only host-declared hard invariant

Cricket separates three jobs:

1. **Monitoring** — inspect what the system is about to say/do or has just done.
2. **Critique** — identify a material mismatch, uncertainty, contradiction, authority problem, or evidence problem.
3. **Control** — decide what consequence follows. Control belongs to the host, not to a model-generated critique.

CRITIQUE != AUTHORITY

DISAGREEMENT != ERROR

SEMANTIC_CRITIC_OUTPUT != PROOF

## Deterministic kernel

V0.1 ships with structural rules for defects that can be checked without pretending to understand arbitrary language:

- protected effect without explicit authority;
- completion claim without verification evidence;
- a claim labeled verified/fact/observed without bound evidence;
- reassertion of an explicitly superseded correction.

These rules can emit BLOCK only where the review envelope itself supplies the hard boundary.

## Semantic critic

Some failures require semantic judgment: proposition substitution, hidden assumptions, contradiction, material omissions,
or needless corrective pedantry. Hosts may supply a CriticAdapter for this lane.

Semantic critic findings are **advisory by default**. Even if the critic asks for BLOCK, Cricket downgrades that to
CHALLENGE unless the host explicitly enables semantic_blocking. This prevents an LLM reviewer from silently
manufacturing new authority.

The built-in critic contract names a specific anti-pattern: **"righter" behavior** — strengthening or broadening a user's
actual proposition, then correcting the invented stronger proposition. Cricket is instructed to critique the literal
referent actually present and to prefer silence over irrelevant precision.

## Chat rendering

render_blockquote() emits a separate Markdown blockquote voice. PASS is silent by default to avoid turning Cricket into
a nagging narrator.

## Runtime seams

A host integration needs only a ReviewRequest, Cricket.review(), and render_blockquote(). The host remains responsible for:

- assembling truthful review metadata;
- determining effect classes and authorization;
- selecting any semantic critic model/provider;
- deciding whether a challenge causes revision, user-visible critique, or no action;
- preserving the user's current corrections and authoritative project state.

## Non-goals

V0.1 does not claim consciousness, conscience in the human phenomenological sense, moral truth, psychological equivalence,
or guaranteed error detection. "Conscience" is a functional metaphor for a monitoring-and-challenge role.
