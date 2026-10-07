# DIMA BRAIN V2.1 — SEMANTIC AUTHORITY CONSTITUTION

> **Status:** CURRENT / PERMANENT ARCHITECTURE LAW  
> **Branch family:** Brain V2.1 forward runtime  
> **Active semantic Product candidate:** `eee7583cb67d50779784805c469230ef2b82a5a2`  
> **Frozen engine:** `686671fa7e55f715e4fb5ac155f9e66019fd12d8` / `0.63.18-dima.11.2`

This document is normative. It exists to prevent representation-by-representation fix
loops and semantic authority drift.

The governing principle is:

> **Every business-semantic fact has exactly one canonical owner.**

A downstream component may project it, transport it, structurally observe execution
against it, verify fulfillment, or consume it. It may not reinterpret the same fact and
become a second veto authority.

## 1. Canonical analytical authority chain

~~~text
USER
  |
  v
THIN INTAKE
  |
  v
ResearchBrief / ResearchScope
  |  canonical WHAT + ScopeVersion/currentness
  v
AnalyticalIntentV1
  |  execution-facing projection
  v
METABASE / METABOT
  |  owns HOW
  v
ExecutionManifest
  |  records what happened
  v
verify_analytical_fulfillment_v1
  |  ONLY Intent <-> Execution semantic judge
  v
Evidence
  |
  +--> Direct terminal
  +--> P18 relationship
  +--> P19 RCA -> optional P17 NextTest
  +--> P20 synthesis
  v
Completion Ledger
~~~

## 2. Owner matrix

| Surface | Role | Semantic authority? | Must not do |
|---|---|---:|---|
| Intake | resolve user language into governed refs | bounded entry authority | runtime capability whitelist |
| ResearchBrief / ResearchScope | canonical business WHAT + scope/currentness | YES | query planning |
| AnalyticalRequestContract | deterministic internal projection/transport | NO independent authority | reinterpret ResearchScope |
| AnalyticalIntentV1 | execution-facing projection of accepted WHAT | NO second truth | invent semantics |
| MaterialGroup | minimum acquisition grouping/dedup/dependency planning | NO | fulfillment judgment |
| Metabase / Metabot | analytical realization/query construction | HOW owner | redefine Dima business authority |
| Attestation / native observation | exact occurrence, engine/query/result/provenance structure | NO business meaning | infer business semantics from physical shape |
| ExecutionManifest | stable record of observed analytical execution | observed facts only | redefine request |
| verify_analytical_fulfillment_v1 | Intent <-> Execution compatibility | YES: sole semantic admission judge | query planning |
| Evidence | governed observed analytical truth | YES for admitted observation | causal promotion |
| P18 | relationship epistemics over Evidence | YES for relationship outcome | execute analytics |
| P19 | RCA/hypothesis epistemics over Evidence | YES for RCA outcome | execute analytics |
| P17 | typed information-gain NextTest re-entry | control only | normal discovery/relationship analyst |
| Completion | terminal requirement ledger | accounting only | reinterpret semantics |
| P20 | synthesis from governed terminal state | presentation only | create analytics/Evidence |
| LangGraph | orchestration/checkpoint/resume | NO | business truth |

## 3. Acquisition identity is not requirement identity

Permanent law:

~~~text
USER_MUST requirement identity != native acquisition identity
~~~

A user may create several logical obligations that can be satisfied from one governed
analytical acquisition.

Example:

~~~text
May vs June
+ downtime
+ department
+ CHANGE ranking
+ top 2
~~~

The legal execution shape is:

~~~text
one acquisition
-> one governed result
-> N independent fulfillment checks
-> one Evidence package with explicit consumer identities
~~~

It is forbidden to manufacture N native conversations merely because consumer contracts
have different ranking/top-k/presentation facets.

Conversely, genuinely different metric/filter/period/grain/dependency/currentness/security
authority must not consolidate. A result-dependent child remains a later occurrence.

Dima never calculates comparison/change/ranking/top-k to make consolidation work.
Metabase/Metabot owns analytical HOW.

## 4. Runtime validator law

A new runtime validator is legal only if it can name a semantic fact that has no existing
owner.

Before adding one, the reviewer must answer:

1. Which canonical fact does this validator own?
2. Where is that fact currently owned?
3. Why is projection from the existing owner insufficient?
4. Does this create a second reject/veto path for the same business meaning?

If the fact already has an owner, the validator is rejected.

Structural validators remain legal for:

- tenant/principal identity;
- ScopeVersion/currentness identity;
- exact native occurrence;
- engine/runtime identity;
- query/result fingerprints;
- receipt/provenance linkage;
- duplicate execution prevention;
- durable resume correlation.

Structural validation must not infer business meaning from SQL/MBQL/query topology.

## 5. Closed grammar law

Closed V1 grammar/composition tables are specification and conformance tools.

They may:

- enumerate tested compositions;
- drive provider-free/metamorphic coverage;
- document expected grammar closure.

They may not:

- veto a production request that already has a legal typed ResearchScope/AnalyticalIntent;
- become a capability whitelist;
- force case-specific Product branches.

Executable guardrail:
`test_closed_v1_grammar_is_conformance_only_not_runtime_veto`.

## 6. Fulfillment law

`verify_analytical_fulfillment_v1` is the only runtime semantic judge between accepted
analytical intent and observed execution.

All consumer requirements sharing one acquisition are verified independently.

~~~text
one ExecutionManifest
-> verify consumer A
-> verify consumer B
-> ...
-> admit shared Evidence only if every intended direct consumer passes
~~~

A richer governed result may fulfill a narrower requirement only through explicit coverage
semantics. Example: unbounded governed ranking may fulfill top-2; top-2 cannot fulfill an
unbounded ranking requirement.

No MaterialGroup, observer, completion ledger or report layer may duplicate this judgment.

## 7. Evidence law

Evidence is the only governed observed analytical truth.

Evidence must retain exact:

- tenant/principal;
- authority/session;
- ScopeVersion/currentness;
- material/acquisition identity;
- native occurrence;
- receipt;
- result hash;
- consumer requirement identities.

A real scope/currentness change makes prior Evidence historical. A new user turn alone does
not erase durable Evidence.

P17/P18/P19/P20 consume Evidence; they do not recreate analytics truth.

## 8. Turn-owned projection law

A new accepted analytical turn and a new ScopeVersion are different events.

Turn-owned LangGraph P18 projection state is one atomic bundle:

~~~text
p18_requirement_ids
p18_result_refs
p18_claim_refs
p18_policy_use_refs
~~~

On a fresh requirement plan/new analytical turn, these refs clear together through one
projection helper. Durable historical P18 artifacts remain stored.

A report-only continuation does not reopen analytics and does not erase valid historical
P18/Evidence artifacts.

## 9. Epistemic-owner law

P18:
- relationship interpretation only;
- no query semantics;
- no scope mutation;
- no causal promotion.

P19:
- hypothesis/RCA adjudication only;
- no query execution.

P17:
- only a typed NextTest after a genuine information gap;
- no normal discovery or relationship cognition.

P20:
- governed synthesis only;
- no new analytics;
- no new Evidence;
- no upstream completion decision.

## 10. Orchestration law

LangGraph may own:

- node routing;
- interrupt/resume;
- checkpoint;
- current-turn refs/revisions;
- idempotency coordination.

LangGraph may not own:

- metric meaning;
- time meaning;
- ranking meaning;
- Evidence truth;
- relationship/RCA truth.

Checkpoint state stores references/projections, not duplicated canonical owner objects.

## 11. Failure classification law

When one layer accepts and another rejects, do not add another validator.

Classify the first wrong boundary:

~~~text
INTAKE / canonical WHAT
ACQUISITION GROUPING
METABOT HOW
STRUCTURAL PROVENANCE
FULFILLMENT
EVIDENCE CURRENTNESS
EPISTEMICS
COMPLETION
SYNTHESIS
ORCHESTRATION STATE
~~~

Fix exactly one canonical owner/boundary.

Forbidden recovery patterns:

- prompt-only patch;
- regex/fuzzy/morphology patch;
- benchmark/case branch;
- provider ceiling increase as semantic fix;
- Python analytics replacing Metabase;
- physical query-shape business inference;
- duplicate semantic store;
- new Brain generation to avoid a local invariant.

## 12. Change-review invariant

Every Product change must preserve:

~~~text
one semantic fact -> one owner
one analytical HOW owner -> Metabase/Metabot
one Intent/Execution judge -> verify_analytical_fulfillment_v1
one governed observed truth -> Evidence
duplicate native = 0
stale Evidence = 0
cross-scope reuse = 0
~~~

If a proposed change cannot satisfy those statements provider-free, it does not enter paid
validation.

## 13. Executable enforcement

Primary guardrails:

- `backend/tests/test_v3_brain_v2_runtime_guardrails.py`
  - closed grammar cannot become runtime veto;
  - fulfillment verifier has one runtime admission owner;
  - MaterialGroup cannot become semantic judge;
  - P18/P19/P20 cannot execute native analytics.
- `backend/tests/test_v3_brain_v2_semantic_authority_metamorphic.py`
  - exactly 192 generated authority scenarios.
- `backend/tests/test_v3_brain_v2_material_groups.py`
  - acquisition grouping invariance and result-dependent separation.
- `backend/tests/test_v3_analytical_boundary.py`
  - N independent consumer fulfillment checks.
- `backend/tests/test_v3_brain_v2_graph.py`
  - atomic new-turn P18 projection reset.

## 14. Constitutional test for any new layer

Ask:

> "Does this component own a new semantic fact, or is it only carrying/checking an existing one?"

If it carries/checks an existing fact, it must be a projection/structural consumer with no
independent semantic veto.

If it claims a new semantic fact that already has an owner:

> **DO NOT ADD THE LAYER.**

This rule is stronger than reducing class/module count. The goal is not fewer files; the
goal is fewer competing semantic authorities.
