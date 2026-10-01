# DMP-DEC-0077 — DIMA BRAIN V2.1 DISCOVERY SIMPLIFICATION

**Date:** 2026-10-02  
**Status:** RATIFIED / BRANCH-LOCAL FORWARD AUTHORITY  
**Branch:** feat/dima-brain-v2-1-discovery-simplification  
**Branch point:** ed60bc1e5fc868deaead0cc321fdf58785cd5d8b  
**Roadmap:** DIMA_BRAIN_V2_1_DISCOVERY_SIMPLIFICATION_ROADMAP.md

## Decision

Brain V2 architecture is retained.

No Brain V3.

No rollback to the historical 70.8 Product.

No Agent API.

No second analytics engine.

The V2.1 spike targets one remaining high-leverage architecture smell:

~~~text
provider-backed P17 DISCOVERY
after Metabot has already produced governed analytical material
~~~

The normal DISCOVERY path will be tested against:

~~~text
Metabot analytical material
→ VERIFIED Evidence
→ deterministic governed CandidateSet projection
→ P19 epistemic assessment
~~~

P17 remains the Investigation Controller for bounded next-test/escalation and durable investigation state.

P17 is no longer accepted as a normal second analytical/discovery model if the candidate identities are already deterministically observable from governed material.

## Owner decomposition

~~~text
METABASE / METABOT
= single analytical cognition engine

LANGGRAPH
= orchestration/checkpoint/resume

DIMA
= intent/scope/material requirement
= Evidence/provenance
= candidate identity
= completion

P19
= epistemic judge

P18
= relationship judge

P20
= governed synthesis/report

P17
= next-test / investigation controller
≠ second analyst
~~~

## Candidate projection restriction

Candidate projection is allowed to produce identity and provenance only.

It may not produce:
- support strength;
- cause likelihood;
- ranking of causes;
- causal conclusion;
- probability.

Candidate identities must be the exact intersection of accepted candidate authority, current scope, VERIFIED observed bindings and candidate-eligible governed semantics, excluding the effect/outcome identity.

## Evidence relation

Projected candidates may be grounded to exact VERIFIED Evidence as CONTEXT.

SUPPORTS/CHALLENGES may not be fabricated deterministically.

P19 owns epistemic interpretation.

## Native acquisition rule

The permanent invariant is not "always exactly one query".

The invariant is:

~~~text
minimum necessary bounded native work
duplicate acquisitions = 0

new acquisition only after:
- typed P19 NextTestRequest
or
- exact deterministic missing-material authority
~~~

Historical T4 is expected to close from one bounded initial acquisition.

## Merge gate

This simplification may merge only if:
- T4 manual quality is preserved or improved;
- P17 discovery provider calls become zero;
- P19 is reached legally;
- candidate diversity is preserved/improved;
- duplicate native execution remains zero;
- ONE_PASS and ADAPTIVE do not regress;
- safety/scope/Evidence invariants remain GREEN;
- provider/token cost is materially no worse and preferably lower.

If the gate fails, reject the spike and retain Brain V2.

## Engineering quality plane

Hypothesis is already adopted and must be expanded for sequence/state-machine invariants.

OpenTelemetry is authorized as an observability bridge over existing BoundaryTrace/BrainRunTelemetry.

OpenTelemetry owns no Product truth.

Schemathesis is deferred until backend API contract freeze.

Temporal is deferred to future Action/Watch execution, not Brain reasoning.

DSPy is offline/conditional only after architecture closure.

Cube/MetricFlow are not additive components while Metabase remains the analytics/semantic engine.

## Engine

~~~text
SHA
d5c60dc9f37a9ec9c5b0117f178146bbcb8dca88

release
0.63.18-dima.9

digest
sha256:22c384198740274bbbba78fb6d41aa63a6d204dfe708b19a6ca9bc322b458ba7

certification
36812902584 = SUCCESS

V2.1 builds authorized
0
~~~

Do not create dima.10 automatically.

## Current readiness note

Historical 30-CASE READY receipts remain references only.

The current codebase has semantic changes after older readiness seals.

This V2.1 branch must freshly seal affected capabilities before it may declare 30-CASE READY.

## UI / 30-case

Frontend/UI/UX remains forbidden.

30-case remains forbidden until separate explicit user authorization.

V2.1 stops at:

~~~text
90+ HIGH-CONFIDENCE READINESS
30-CASE READY
30-case NOT RUN
frontend NOT IMPLEMENTED
~~~
