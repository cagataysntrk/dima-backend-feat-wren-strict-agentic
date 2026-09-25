# P16 — CLAIM-LINEAGE EVIDENCE PRE-DEVELOPMENT REVIEW

**Date:** 2026-09-25  
**Status:** **SEALED / P16 CLAIM-LINEAGE IMPLEMENTATION AUTHORIZED**  
**Forward authority:** DMP-DEC-0048  
**Consumes:** P14 sealed Evidence + P15 sealed native Research material  
**Engine change:** NOT AUTHORIZED / NOT REQUIRED

## 1. Purpose

P16 answers:

```text
What explicit claim does governed Evidence support, challenge, contextualize,
or fail to establish?
```

It does not answer the analytical query again and does not validate Metabase operators.

Permanent distinction:

```text
native analytical result
!=
P15 Research material / lead
!=
P16 claim
!=
later finding / root-cause conclusion
```

## 2. Authority inputs

Eligible Evidence identity comes from the sealed P14 Research authority chain:

```text
ResearchSession
→ EvidenceRef
→ DimaQueryReceipt
→ ResearchExecutionLink
→ native result provenance
```

P15 `ResearchExplorationMaterial` may be recorded as claim origin/context only. A P15 lead is
**not** Evidence and cannot promote a claim by itself.

## 3. Durable claim identity

Minimum durable claim record:

```text
claim_id
research_session_id
obligation_id
tenant_binding
principal_subject
semantic_context_version
claim_text
structured proposition
scope
time/freshness
origin Research-material refs
epistemic_state
limitations
created_at / updated_at
```

No numeric confidence score is introduced.

## 4. Durable Evidence relationship

Each claim-to-Evidence edge must retain:

```text
claim_id
evidence_id
receipt_id
source execution link
relation
created_at
```

Allowed bounded relations:

```text
SUPPORTS
CHALLENGES
CONTEXTUALIZES
INSUFFICIENT
```

The edge is valid only when:
- the Evidence exists in the same durable ResearchSession;
- its obligation is the claim obligation;
- its receipt id matches the session EvidenceRef;
- exactly one sealed ResearchExecutionLink carries that Evidence/receipt pair;
- the execution link is VERIFIED.

No arbitrary external id may be attached as trusted Evidence.

## 5. Epistemic state

P16 state is derived from explicit eligible Evidence edges only:

```text
no support/challenge edges        → PROPOSED
SUPPORTS only                     → SUPPORTED
CHALLENGES only                   → CHALLENGED
SUPPORTS + CHALLENGES             → CONTESTED
INSUFFICIENT without support/challenge → INSUFFICIENT_EVIDENCE
```

`CONTEXTUALIZES` enriches lineage but does not promote truth.

P16 does not create a `VERIFIED` shortcut from:
- LLM prose;
- Metabot summary;
- one chart;
- P15 interestingness;
- P15 lead existence.

## 6. Claim creation

Claim text/proposition is an explicit P16 object. In this provider-free slice it is supplied by the
caller/test authority; P16 does not invent a claim-generation heuristic.

P17 Research Manager may later propose claims/research steps, but deterministic P16 code remains the
state/lineage owner.

## 7. Origin material

A claim may cite zero or more P15 lead ids as origin material. Every cited lead must belong to the
same ResearchSession and obligation.

Origin material means:

```text
where the research idea came from
```

not:

```text
proof that the claim is true
```

## 8. Forbidden

P16 must not introduce:
- query execution;
- MBQL parsing;
- interestingness/scoring;
- a second Evidence/receipt family;
- a second analytics authority;
- raw SQL/Wren/Agent API fallback;
- numeric confidence synthesis;
- automatic "interesting → supported" promotion.

## 9. Provider-free proof

Focused P16 tests must prove:
1. claim creation is durable and principal/session/context bound;
2. P15 material origin does not promote the claim;
3. eligible P14 Evidence can SUPPORT/CHALLENGE/CONTEXTUALIZE/INSUFFICIENT;
4. foreign-session/foreign-obligation Evidence is rejected;
5. receipt/execution provenance mismatch is rejected;
6. SUPPORT + CHALLENGE becomes CONTESTED;
7. insufficient-only becomes INSUFFICIENT_EVIDENCE;
8. restart preserves claim and edges;
9. no analytical primitive or model call participates;
10. P15/P14 regressions remain GREEN.

## 10. Exit

P16 closes when:

```text
native executions/results
→ P14 Evidence
→ explicit P16 claims
→ support/challenge/context/insufficient lineage
```

is durable, inspectable and restart-safe.

Then P17 Research Manager maturation consumes this claim/evidence authority.
