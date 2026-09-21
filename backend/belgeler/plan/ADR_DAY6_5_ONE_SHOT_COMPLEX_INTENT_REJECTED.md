# ADR — ONE-SHOT UNIVERSAL COMPLEX INTENT COMPILATION REJECTED

**Status:** ACCEPTED  
**Date:** 2026-09-21  
**Scope:** Dima V2 complex natural-language control plane  
**Supersedes:** none  
**Related:** P9, P10, R11, R12, Day 6.5 Manager Architecture Validation & Seal

## Context

Dima V2 P9 attempted the following front-door architecture:

```text
raw complex user turn
→ one-shot TurnInterpreter
→ immutable typed complex operation graph
→ SemanticResolver
→ ResearchBrief
→ downstream research execution
```

The architecture had strong deterministic downstream controls:
- source grounding,
- typed contracts,
- Resolver-owned canonical binding,
- ResearchBriefBuilder without raw-prompt access,
- query=0 Day 6 boundary,
- semantic relationship blocking,
- no legacy fallback.

Provider-free tests proved that, **given a correct typed interpretation**, downstream
contracts behaved correctly.

The unresolved question was whether a real language model could reliably produce the
complete complex typed graph in one shot without silently dropping or inventing user
obligations.

## Evidence

Historical Frozen16 / reference-language measurement:

- workflow run: `35593735023`
- cases: 16
- case pass: **43.8%**
- goal coverage: **65.6%**
- MUST coverage: **73.2%**
- research act: **90.9%**
- negatives: **100%**
- invented operations: **12**
- retry rate: **12.5%**

Observed failures included:
- relationship focus omitted,
- one relationship decomposed into wrong direction/edges,
- duplicate relationship requirements,
- sibling analytical operation dropped,
- requested/non-requested deliverable confusion,
- root-cause decomposed into an additional relationship requirement,
- coreference loss,
- schema-valid but semantically incomplete graphs.

These failure classes persisted after:
- presentation/research decoupling,
- deliverable separation,
- typed ResearchModePolicy,
- atomic relationship contracts,
- provider-native structured output work,
- stronger reference-language models,
- schema/prompt refinement.

## Rejected architecture

> **One-shot universal complex intent compilation**

Definition:

A single model call must completely and correctly compile arbitrary complex natural
language into a closed, immutable semantic AST/graph that contains every obligation,
exclusion, coreference relation, operation decomposition, polarity, scope and
relationship orientation needed by all downstream research logic.

## Reason for rejection

The hypothesis failed the product-quality semantic coverage requirement.

The problem is not that deterministic governance is wrong. The failed assumption is that
**human intent understanding itself can be treated like a one-shot deterministic
compiler front-end**.

Adding more prompt examples, regexes, provider-specific post-processing or special-case
schema branches would create the exact multi-owner patch accumulation V2 was designed
to avoid.

Adding a Supervisor after an incorrect immutable brief does not solve the problem:
- if Supervisor trusts the brief, front-door loss remains;
- if Supervisor rereads raw intent and repairs/adds obligations, it has become the
  semantic cognition owner and the architecture is already a Manager architecture.

## Decision

**Accepted decision:** one-shot universal complex intent compilation is rejected as a
production architecture.

**Selected candidate for validation:** bounded iterative Manager runtime.

Manager is NOT yet sealed as production architecture. It becomes production authority
only if Day 6.5 hidden/security/trust-plane/fast-path hard gates pass.

```text
human language
→ iterative probabilistic cognition
→ proposed obligations / exclusions / ambiguity
→ deterministic acceptance + semantic binding
→ accepted versioned contract
→ deterministic representability decision
→ governed execution/evidence/completion
```

Deterministic authority remains mandatory for:
- semantic canonical binding,
- opaque SemanticHandle issuance,
- capability checks,
- contract acceptance,
- representability,
- query/task validation,
- grain/join safety,
- Wren dry-plan,
- RLS/CLS,
- numeric execution,
- evidence,
- budget,
- completion.

### Candidate architecture

```text
human language
→ bounded iterative Manager candidate
→ proposed obligations / exclusions / ambiguity
→ deterministic acceptance + semantic binding
→ accepted versioned contract
→ deterministic representability decision
→ governed execution/evidence/completion
```

## New principle

```text
UNDERSTAND THE HUMAN
→ probabilistic, iterative, bounded

VERIFY THE TRUTH
→ deterministic, governed, auditable
```

## Consequences

### Positive

- Manager no longer has to emit a perfect final AST before doing useful work.
- Ambiguity can be clarified instead of guessed.
- Missing semantics can be resolved when needed.
- Evidence can change later task selection.
- User obligation completeness is separated from execution-plan completeness.
- Canonical semantics remain outside the LLM's authority.
- Model capability floor can be measured independently from architecture correctness.

### Costs

- More explicit state/versioning contracts are required.
- Manager runtime needs bounded tool/call budgets.
- Acceptance and completion become first-class gates.
- Evaluation must test iterative behavior, not just one JSON object.
- Hidden architecture holdout is required to avoid tuning to Frozen16.

## What remains valid from P9

The following are retained:
- SemanticResolver as canonical authority,
- source evidence/provenance discipline,
- ResearchBrief/obligation concepts where useful,
- query=0 separation for intent-contract phases,
- no silent requirement loss,
- no invented semantic ref,
- relationship/grain safety,
- P9 code as historical/reference baseline.

The following is no longer the production hypothesis:
- complete complex intent must be compiled into one immutable graph before any iterative
  cognition can occur.

## Prohibited rollback

Do not reintroduce this rejected architecture through:
- giant prompt rule lists,
- regex semantic routing,
- provider-specific semantic patches,
- downstream fallback that rereads intent,
- test-fixture literals,
- "one more schema field" loops whose purpose is only to make the same one-shot compiler
  pass seen examples.

Any future proposal to restore one-shot universal compilation must provide materially new
evidence, not merely a stronger model score on the already-seen Frozen16 corpus.
