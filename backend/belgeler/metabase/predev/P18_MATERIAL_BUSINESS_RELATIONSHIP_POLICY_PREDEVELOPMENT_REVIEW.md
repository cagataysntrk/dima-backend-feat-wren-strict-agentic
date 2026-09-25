# P18 — MATERIAL BUSINESS RELATIONSHIP POLICY PRE-DEVELOPMENT REVIEW

**Date:** 2026-09-25  
**Status:** **SEALED / DMP-DEC-0054 / P18 GREEN / IMPLEMENTATION COMPLETE / P19 PRE-DEVELOPMENT READY**  
**Forward authority:** DMP-DEC-0048 + DMP-DEC-0049 + DMP-DEC-0053 + DMP-DEC-0054  
**Consumes:** P14 Evidence + P15 native Research material + P16 claim lineage + P17 sealed investigation state  
**Engine change:** NOT AUTHORIZED / NOT REQUIRED BY DEFAULT  
**Model/live run:** FORBIDDEN FOR P18 v1 — Luna/Sol/C1 = 0  
**UI/UX:** NOT AUTHORIZED

## 1. Purpose

P18 answers a narrow Dima-specific question:

```text
Which company/sector-specific business relationships are materially required
before downstream interpretation may be treated as governed?
```

It does **not** answer:

```text
How should Metabase join tables?
Which MBQL join path should be generated?
Which field/dimension should be selected?
Which analytical result is correct?
What is the causal relationship?
```

Permanent ownership:

```text
Metabase / Metabot
= native metadata + join mechanics + query planning/repair + permissions + execution

Dima P18
= explicit material business-relationship policy needed for safe interpretation
+ lineage to the Research/claim context that required it
+ fail-closed downstream eligibility when the policy is absent, stale or out of scope
```

P18 must not become a shadow semantic layer or a second join planner.

## 2. Sealed input authority

P18 starts only because P17 is SEALED:

```text
P17 product/code candidate = 3664d3d706d70225323126cbc994b8c2c732aaf4
P17 provider-free          = 36158440330 SUCCESS
P17 governance             = 36158440319 SUCCESS
P17 live                   = 36160559037 SUCCESS
```

Eligible context comes from the existing authority chain:

```text
ResearchSession / obligation
→ P14 VERIFIED Evidence + one DimaQueryReceipt family
→ P15 RESEARCH_MATERIAL
→ P16 explicit claim + support/challenge/context/insufficient lineage
→ P17 durable investigation topology / Evidence feedback / bounded stop
→ P18 relationship-policy requirement, if material to interpretation
```

P18 does not re-execute or reinterpret the underlying analytical query.

## 3. Native Metabase boundary

Metabase remains authoritative for physical/native relationship mechanics, including:
- database metadata and field identity;
- foreign-key/native relationship metadata;
- join construction and join execution;
- query processor / driver semantics;
- permissions for resources and data;
- native model/card/query semantics;
- Metabot analytical reasoning over those native capabilities.

Dima must not persist a competing physical join graph merely to reproduce Metabase internals.

Forbidden examples:

```text
table A.column_x -> table B.column_y join planner
preferred SQL/MBQL join path
cardinality estimator
join-order optimizer
dimension picker
relationship scoring/ranking
fuzzy table/column matcher
cross-database SQL federation fallback
```

If P18 implementation appears to require any of those, STOP and return to supervisor.

## 4. What counts as a material business relationship

A P18 relationship is a governed business interpretation dependency, not a physical join edge.

Conceptually, a future policy object may need to identify:
- stable relationship-policy id;
- tenant/company binding;
- semantic-context version;
- source business subject/ref;
- target business subject/ref;
- bounded business relationship statement;
- scope/population/time applicability;
- provenance / approving source;
- lifecycle state such as proposed/active/retired;
- limitations;
- created/updated timestamps.

This review intentionally does **not** freeze a broad ontology or relation taxonomy. The first
implementation must prove the smallest real material-policy vertical and add vocabulary only when a
concrete governed use case requires it.

No numeric confidence, interestingness or relationship-strength score is authorized.

## 5. Policy use versus analytical execution

A relationship policy may affect **whether downstream interpretation is eligible**, never how
Metabase computes the analytical result.

Target flow:

```text
P17 investigation/claim requires a material business relationship
→ Dima resolves an exact in-scope P18 policy or records an explicit limitation
→ Metabase still performs any analytical work natively
→ Evidence/claim lineage retains policy-use provenance
→ downstream trusted promotion fails closed if a required material policy is unresolved
```

The P18 gate must not mutate P14 Evidence truth, invent new Evidence, or silently rewrite P16 claim
state.

## 6. Fail-closed semantics

Future implementation should distinguish at least:

```text
policy not required for this interpretation
policy required + exact active in-scope policy found
policy required + missing
policy required + stale/retired
policy required + foreign tenant/context/scope
policy requirement ambiguous
```

Missing/invalid material relationship policy must become an explicit limitation or blocked downstream
eligibility. It must not trigger:
- guessed joins;
- raw SQL;
- Wren;
- admin analytical sessions;
- heuristic relationship inference;
- LLM-generated trusted relationship facts.

## 7. P18 is not P19

P18 relationship policy is not causal epistemics.

Forbidden P18 authority:
- causal direction;
- causal effect;
- contribution percentage;
- path strength;
- root-cause ranking;
- counterfactual effect;
- probabilistic causal confidence.

```text
P17 InvestigationGraph != P19 causal graph.
P18 business relationship policy != P19 causal relationship.
```

P19 remains the future Hypothesis / Root Cause authority.

## 8. Minimum provider-free implementation plan

Implementation is **not authorized by this handoff**, but the first authorized slice should be
provider-free and prove only a minimal vertical.

Expected proof matrix:

1. create/load one exact tenant/context-bound business relationship policy;
2. reject foreign tenant/context/scope refs;
3. bind one P17/P16 interpretation requirement to an exact policy id;
4. preserve P14/P15/P16/P17 identities without copying their truth;
5. missing required policy fails closed with an explicit limitation;
6. retired/stale policy cannot silently satisfy the requirement;
7. restart reproduces the same policy-use lineage;
8. no query, SQL, MBQL, join construction or analytical execution occurs in P18;
9. no Python analytics/scoring/ranking exists;
10. no P19 causal semantics or confidence exists;
11. P17/P16/P15/P14 regressions remain GREEN;
12. engine identity remains exact dima.6 unless a future supervisor decision changes it.

No Luna/Sol/C1 run is required for the provider-free relationship-policy state model by default.

## 9. Questions the implementation review must answer before code

Before P18 code is authorized, the implementing developer must resolve from current repository/native
Metabase source:
- which existing native semantic/resource refs are stable enough to reference without mirroring them;
- where a relationship-policy requirement belongs in the existing Research/claim lineage;
- whether the first vertical needs a dedicated durable policy record, a policy-use binding, or both;
- exact lifecycle and freshness semantics;
- exact limitation code/state when required policy is absent;
- how policy version/context changes invalidate prior downstream eligibility;
- whether any proposed field accidentally duplicates Metabase join metadata.

Do not answer these by inventing a broad enterprise ontology.

## 10. STOP conditions

Return to supervisor before implementation if any of these becomes necessary:
- Metabase/QP/Lib/driver/core modification;
- physical/native join graph replication in Dima;
- second semantic formula owner;
- raw SQL/Wren/Agent-API analytical fallback;
- admin/service analytical fallback;
- cross-source federation engine;
- probabilistic relationship scorer;
- LLM-generated trusted relationship facts without governed source;
- P19 causal/contribution authority;
- destructive migration;
- UI/UX work;
- paid model evaluation to prove a deterministic policy-state contract.

## 11. Exit criteria for a future P18 implementation

A future P18 slice may close only when:

```text
material relationship requirement
→ exact governed business policy
→ tenant/context/scope/freshness validation
→ explicit policy-use lineage
→ fail-closed limitation when unresolved
→ downstream eligibility signal
```

is durable and restart-safe while:

```text
Metabase physical join authority       = unchanged
Dima analytical execution              = 0
second receipt family                  = 0
P19 causal authority                   = 0
engine patch/build                     = 0 by default
UI/UX                                  = 0
```

## 12. Current stop point

This file is the complete P18 pre-development review requested after the P17 live GREEN seal.

```text
P17 = SEALED
P18 PREDEVELOPMENT = COMPLETE
P18 IMPLEMENTATION = NOT STARTED
NEXT ACTION = SUPERVISOR AUTHORIZATION / IMPLEMENTATION DIRECTIVE
```

No P18 production code, model, migration, engine change or UI change is part of this handoff.


## DMP-DEC-0054 IMPLEMENTATION AUTHORIZATION ADDENDUM

This addendum supersedes this review's previous implementation-not-authorized stop point.

Authorized P18 v1 surface:

```text
backend/app/v3/business_relationship_policy.py
backend/control_plane/models.py
one Alembic migration
backend/tests/test_v3_p18_business_relationship_policy.py
.github/workflows/dima-metabase-p18-provider-free.yml
governance/docs
```

Maximum durable P18 tables:

```text
business_relationship_policy
business_relationship_policy_use
```

No requirement table, relationship node/edge graph, join-path registry, scoring table or policy rule
DSL is authorized.

The implementation must use exact deterministic canonical JSON identity, exact scope equality, ACTIVE
versus RETIRED lifecycle, explicit sealed P16/P17 references, immutable/idempotent policy-use lineage
and a thin downstream eligibility result.

The implementation must not parse free text to discover relationship requirements and must not import
native analytical execution, Wren, raw-SQL analytics, MBQL/query planning, P13 re-execution, Metabase
join metadata or P19 causal/root-cause authority.

Current authorized completion target:

```text
DMP-DEC-0054 recorded
→ minimal two-table P18 vertical
→ focused P18 provider-free GREEN
→ P17/P16/P15/P14 regressions GREEN
→ governance GREEN
→ engine unchanged
→ model calls 0
→ P18 SEALED
→ STOP before P19 implementation
```


## FINAL P18 IMPLEMENTATION SEAL

```text
P18 product/code candidate     = fdf15611e7f0aa57e80f75fe7f8630d8434a2af3
P18 integrated seal candidate  = ce56a7c478393d5656824b0f9715263bb837756c
Alembic head                   = f5a1d7c9e2b4
provider-free                  = 36166506385 SUCCESS
governance                     = 36166506443 SUCCESS

P18                            = 23 PASS
P17 regressions                = 95 PASS
P16                            = 6 PASS
P15                            = 5 PASS
P14                            = 17 PASS

Luna / Sol / C1                = 0 / 0 / 0
engine builds                  = 0
Metabase modifications         = 0
```

Exit criterion is satisfied. P18 is now SEALED.

Implementation stayed within the authorized surface:
- exactly two durable P18 tables;
- one transient typed requirement;
- exact canonical fingerprints;
- exact tenant/context/scope/business-ref resolution;
- ACTIVE/RETIRED lifecycle;
- immutable/idempotent policy-use lineage;
- thin eligibility decision;
- no P16 claim mutation;
- no Evidence or receipt creation;
- no NativeResourceBinding dependency;
- no legacy relationships.yml truth;
- no Metabase physical locator/join graph;
- no analytical executor/query planner;
- no fuzzy inference/scoring;
- no causality/P19 state.

```text
P18 DEVELOPMENT = STOP
P18B / P18C = NOT AUTHORIZED
P19 = PRE-DEVELOPMENT AUTHORIZATION REQUIRED
P19 IMPLEMENTATION = NOT AUTHORIZED
```
