# P19 — HYPOTHESIS / ROOT CAUSE PRE-DEVELOPMENT REVIEW

**Date:** 2026-09-25  
**Status:** **SEALED REVIEW / DMP-DEC-0055 / P19 MINIMAL IMPLEMENTATION AUTHORIZED / PRODUCTION CODE STARTING**  
**Authority consumed:** sealed P14 + P15 + P16 + P17 + permanently sealed/hardened P18  
**Engine:** `cbe313af9ac2d5960f662068e433d328d896fb06` / `0.63.18-dima.6`  
**Paid work in this review:** Luna = 0 / Sol = 0 / C1 = 0  
**Engine build/modification:** 0 / 0  
**UI/UX:** NOT AUTHORIZED

> This review defines the smallest forward epistemic boundary. DMP-DEC-0055 now authorizes the
> minimal P19 code/migration/provider-free vertical and one bounded Luna canary only after deterministic
> GREEN. Engine patches, UI, generic causal platforms, Sol and local analytics remain unauthorized.

## 1. What P19 owns

P19 owns the governed epistemic meaning of already-available investigation material:

```text
candidate explanations
→ source-backed support/challenge comparison
→ preservation of viable alternatives
→ qualitative contribution/evidence assessment
→ explicit causal-identification limitations
→ defensible root-cause conclusion OR explicit inconclusive outcome
```

P19 may decide whether an explanation remains epistemically defensible. It may not calculate the
underlying analytics itself.

Permanent boundary:

```text
METABASE COMPUTES ANALYTICS.
DIMA P19 GOVERNS WHAT THOSE RESULTS JUSTIFY EPISTEMICALLY.

P17 InvestigationGraph != P19 causal graph / contribution structure.
P18 business-policy direction != causal direction.
P16 claim state != P19 hypothesis state.
```

P19 is not a second Evidence owner, claim owner, receipt family, analytical executor, query planner,
semantic layer, relationship graph or causal-discovery engine.

## 2. What Metabase owns

Pinned dima.6 source audit confirms native analytical machinery already exists and remains the first
place for computation:

- `src/metabase/metabot/api.clj`: native Clojure Metabot agent/streaming execution;
- `src/metabase/query_processor.clj`: primary MBQL Query Processor entrypoints;
- `src/metabase/lib/drill_thru.cljc`: automatic insights, distribution, pivot, summarize-column,
  summarize-by-time, underlying-records and time-series/geographic/bin drill capabilities;
- `src/metabase/analyze/fingerprint/insights.clj`: native statistical insight machinery including
  time-series change, simple regression/trend slope and best-fit trendline selection;
- `resources/automagic_dashboards/table/GenericTable/Correlations.yaml`: native correlation-oriented
  exploratory visualization;
- `src/metabase/metabot/tools/generate_insights.clj`: native insight/X-ray generation entrypoint.

Current Dima native bridge already exposes Metabot invocation, captured-query execution,
`/api/dataset`, and native adhoc exploration. P19 must not create another bridge or executor.

These capabilities prove that trend/correlation/exploration computation belongs on the native side.
They do **not** prove causal identification. A native correlation, trendline or regression output is
analytical evidence, not automatically a cause.

Permanent order for any future analytical need:

```text
USE_NATIVE
→ COMPOSE_NATIVE
→ WRAP_NATIVE
→ HOOK_NATIVE
→ DIMA_OWNS only after explicit supervisor review
```

No Python analytics is justified by this pre-development review.

## 3. Old P14 Hypothesis machinery remains historical compatibility

Existing `backend/app/v3/research.py` contains:

```text
Hypothesis
HypothesisState = OPEN / SUPPORTED / CHALLENGED / CONTESTED
EvidenceRelation
ResearchSession.hypotheses
ResearchManager.add_hypothesis()
ResearchManager.admit_receipted_evidence()
```

That machinery is P14-era compatibility state and is too coarse for P19. It is frozen except for
sealed P14 compatibility maintenance.

P19 must not:
- add new forward states to `HypothesisState`;
- turn `ResearchSession.hypotheses` into P19 persistence;
- build P19 through `ResearchManager.add_hypothesis()`;
- reinterpret old P14 support/counter edges as causal authority.

No destructive migration of historical P14 state is authorized.

## 4. Exact first vertical

The first future P19 vertical should consume one existing sealed Research investigation with:

```text
one ResearchSession + obligation
at least two candidate explanations
supporting Evidence for at least one candidate
counter-Evidence OR explicit missing Evidence for at least one candidate
P16 claim lineage
P17 reasoning/investigation history
one P18 policy-use decision if a material business relationship is required
```

It should produce:

```text
candidate A assessment
candidate B assessment
→ both may remain viable
→ each keeps explicit source lineage
→ contribution/evidence axes remain independent
→ causal-identification limitations remain explicit
→ final outcome is either:
   ROOT_CAUSE_ESTABLISHED
   MULTIPLE_MATERIAL_CONTRIBUTORS
   NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED
```

No candidate is required to win. No UI is part of this vertical.

## 5. Minimum future durable records

Review conclusion: the first vertical can remain bounded to **three durable record types maximum**.
No case table is needed because `ResearchSession + obligation_id` is already the case identity.

### 5.1 HypothesisRecord — stable candidate identity

Conceptually:

```text
hypothesis_id
research_session_id
obligation_id
tenant_binding
semantic_context_version
statement
identity_fingerprint
created_at
```

It is a candidate explanation identity, not a claim, Evidence record or causal conclusion.

### 5.2 HypothesisGroundingLink — append-only bounded source linkage

Conceptually one hypothesis may link to already-governed source identities with an explicit,
small relation vocabulary such as:

```text
SUPPORTS
CHALLENGES
CONTEXT
INSUFFICIENT
```

Allowed source families are explicitly bounded to sealed authorities:

```text
P14 Evidence id / receipt provenance
P15 material id
P16 claim id
P17 reasoning-step id
P18 policy-use id
```

This is not a generic graph: one side is always one P19 hypothesis; the other side is one typed
sealed source reference. No arbitrary hypothesis-to-hypothesis causal edge is authorized here.

### 5.3 RootCauseAssessment — immutable aggregate epistemic snapshot

One append-only assessment references the candidate hypotheses and records the current legal
epistemic interpretation, limitations and terminal/nonterminal outcome.

It may contain canonical structured assessment data, but must not copy P14 Evidence payload,
P15 native material, P16 claim text/state, P17 topology, or P18 policy meaning. Reference IDs plus
P19-owned epistemic judgments only.

No fourth table, causal-edge table, generic graph table or path table is justified by this review.

## 6. Hypothesis epistemic state model

Do not overload one scalar state with observation, contribution and causation.

### 6.1 Epistemic class

P19 recognizes these conceptual distinctions:

```text
OBSERVATION
ASSOCIATION
CONTRIBUTION
CANDIDATE_CAUSE
COMPETING_HYPOTHESIS
ROOT_CAUSE_CONCLUSION
```

For the first vertical:
- OBSERVATION remains an input from P14/P15, not a new P19 hypothesis row;
- candidate hypotheses may be assessed as ASSOCIATION, CONTRIBUTION, CANDIDATE_CAUSE or
  COMPETING_HYPOTHESIS;
- ROOT_CAUSE_CONCLUSION belongs only to the aggregate RootCauseAssessment.

No automatic promotion exists between classes.

### 6.2 Candidate disposition

Within one immutable assessment snapshot:

```text
OPEN
RETAINED
WEAKENED
REJECTED
```

A later assessment after genuinely new governed Evidence may change the disposition without rewriting
the old assessment.

### 6.3 Aggregate conclusion status

```text
IN_PROGRESS
NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED
MULTIPLE_MATERIAL_CONTRIBUTORS
ROOT_CAUSE_ESTABLISHED
```

`NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED` is a successful terminal epistemic outcome, not an error.

## 7. Two independent assessment axes

P19 must keep two axes separate.

### Axis A — effect / contribution

Initial bounded qualitative vocabulary:

```text
DOMINANT
MATERIAL
SECONDARY
LOW
UNKNOWN
```

### Axis B — evidence strength

```text
STRONG
MODERATE
WEAK
INSUFFICIENT
CONTRADICTED
```

A strong association does not imply dominant contribution. A material contribution does not imply
causal identification.

The model may propose these qualitative labels from grounded source packets; deterministic Dima
validates legal vocabulary and source lineage. Numeric percentages, confidence values, effect sizes
or contribution shares are forbidden unless an exact native/statistical analytical source produced
them and its provenance is explicitly referenced.

No LLM-generated `83%`, causal probability or pseudo-score is allowed.

## 8. Evidence, claim and P18 policy lineage

P19 consumes but does not mutate:
- P14 Evidence/receipt provenance;
- P15 Research material;
- P16 claim lineage and claim epistemic state;
- P17 reasoning-step / InvestigationGraph history;
- P18 RelationshipPolicyDecision / BusinessRelationshipPolicyUse.

Rules:

```text
unknown source ref                 → reject
foreign session/tenant/context     → reject
P16 challenged/contested material  → remains visible
P18 NOT_REQUIRED                   → no policy gate
P18 SATISFIED                      → interpretation may participate, not causal proof
P18 blocked required policy        → that relationship-dependent explanation cannot support a
                                     trusted causal/root-cause conclusion
```

P19 never promotes or demotes the underlying P16 claim.

## 9. Multiple contributors and leading cause

Permanent:

```text
LEADING CAUSE != CONTRIBUTION
```

The first vertical must allow multiple candidate hypotheses to be simultaneously RETAINED and
MATERIAL. `MULTIPLE_MATERIAL_CONTRIBUTORS` is legal even when no defensible leading/root cause can
be established.

A `ROOT_CAUSE_ESTABLISHED` assessment may reference one or more defensible root-cause hypotheses.
A separate leading-cause label is optional and may exist only when the source/identification basis
actually distinguishes it. No winner-takes-all rule and no ranking score is authorized.

## 10. Direct / indirect mediation and double-count protection

P17 parent/child edges are investigation history only. They must never become causal edges.

The first P19 vertical may represent mediation only as an **assessment-local bounded annotation**,
not a causal graph platform. Conceptually a mediation annotation can contain:

```text
ordered hypothesis ids
outcome/business scope
source refs supporting the mediation interpretation
identification limitation
```

No separate path/edge table is pre-authorized.

Double-count rule:

```text
if A → B → outcome is treated as one mediated explanatory path,
A and B must not be summed as two independent additive contributions
unless an explicit native analytical source provides non-overlapping direct/indirect effects.
```

Without such a source, P19 keeps qualitative contributors and records
`MEDIATION_NOT_IDENTIFIED` / equivalent limitation. It does not invent path mathematics.

## 11. Causal identification gate

Association or segment difference never becomes CAUSE automatically.

A future deterministic promotion gate for a trusted causal/root-cause conclusion must require, where
material to the case:

```text
temporal/order consistency
relevant supporting Evidence
counter-Evidence retained and considered
material competing explanations considered
scope/population/time consistency
P18 relationship-policy eligibility when required
data-quality / missing-data limitations visible
identification limitations explicit
no unresolved fatal contradiction
numeric effect, if any, source-backed by legitimate analytics
```

Conceptual causal qualification for a candidate should remain distinct from disposition:

```text
NOT_CLAIMED
CAUSAL_CANDIDATE
IDENTIFICATION_LIMITED
DEFENSIBLE_CAUSAL_CONCLUSION
```

`DEFENSIBLE_CAUSAL_CONCLUSION` is illegal if any required P18 policy is blocked, the material
identification limitation is unresolved, or only an association/correlation source exists.

If the gate does not pass, the correct result is inconclusive or multiple contributors with causal
identification insufficient.

## 12. Model role versus deterministic role

### Model may propose

```text
candidate explanation
interpretation of already-governed source material
which assumption matters
which alternative remains viable
qualitative contribution/evidence-strength assessment
what additional Evidence would discriminate
```

### Deterministic Dima owns

```text
hypothesis identity
legal enums/states
tenant/session/context scope
source-reference existence and lineage
support/challenge relation vocabulary
P18 policy eligibility
legal state/class promotion
numeric-value provenance rule
causal promotion gate
assessment identity / idempotency
budgets/limits
terminal conclusion legality
prohibited truth promotion
```

P19 itself does not execute an analytical query. If more Evidence is needed, first-vertical P19
returns a typed evidence need; a separately governed existing Research/investigation owner may act on
it later. P19 does not open a new executor path.

## 13. Provider-free proof matrix for a future implementation

Before any model can be called, provider-free tests should prove at least:

```text
unknown Evidence/material/claim/step/policy-use ref
→ reject

foreign tenant/session/context/obligation
→ reject

P14 legacy Hypothesis state
→ not used as forward P19 authority

two hypotheses with distinct evidence
→ both can remain RETAINED

support + challenge links
→ challenge remains visible; no silent overwrite

only correlation/association source
→ causal/root-cause promotion rejected

required P18 policy blocked
→ relationship-dependent causal/root conclusion rejected

P18 SATISFIED
→ eligibility only; causation still unproven

multiple MATERIAL contributors
→ legal without winner

no defensible root cause
→ legal terminal success

numeric contribution/confidence without native analytical provenance
→ reject

native-sourced numeric result
→ reference accepted; Dima does not recompute

mediated A→B path with no direct/indirect decomposition
→ independent additive double-counting rejected

old assessment
→ immutable after new Evidence

same exact assessment inputs
→ restart/idempotency reproduces identity

P16 claim state
→ unchanged

P17 InvestigationGraph
→ unchanged

P18 policy-use
→ unchanged

analytical execution inside P19 owner
→ zero

second Evidence owner / receipt family / claim authority
→ zero
```

P18/P17/P16/P15/P14 regressions and governance remain mandatory.

## 14. Future Luna canary decision

Review conclusion: **one bounded Luna canary will likely be required for a model-enabled P19
vertical**, but only after:
1. supervisor explicitly authorizes P19 implementation;
2. deterministic P19 provider-free state/lineage contracts are fully GREEN;
3. a trajectory-invariant evaluator exists;
4. no paid run is needed to debug deterministic contract failures.

The canary must not prescribe a winner such as "candidate A must win". It should certify invariants:
legal source use, viable-alternative preservation, challenge visibility, no unsupported causal
promotion, no fake numeric confidence, legal inconclusive outcome and bounded termination.

This pre-development review authorizes **zero** Luna/Sol/C1 calls.

## 15. STOP conditions

Return to supervisor before implementation if the proposed P19 vertical requires any of:

```text
Metabase core patch
new native execution path
second DimaQueryReceipt family
second Evidence authority
second P16 claim authority
Python analytics as default
generic causal DAG/graph platform
Bayesian network engine
causal discovery framework
relationship/knowledge graph expansion
fuzzy/regex/morph causal inference
LLM-generated numeric confidence/effect
automatic correlation→cause promotion
destructive P14/P16 migration
P18 relationship-graph expansion
arbitrary causal path DSL
```

A need for real statistical computation is not automatically a Dima implementation requirement:
audit native Metabase first and return to supervisor before any `DIMA_OWNS` computation.

## 16. Authorized first implementation boundary — DMP-DEC-0055

DMP-DEC-0055 authorizes exactly this first slice:

```text
sealed ResearchSession + obligation
+ 2 explicit typed candidate hypotheses
+ governed source refs
+ optional exact P18 policy-use refs
→ deterministic grounding validation
→ immutable hypothesis/source lineage
→ one bounded epistemic assessment
→ multiple-contributor preservation
→ causal promotion gate
→ ROOT_CAUSE_ESTABLISHED
   OR MULTIPLE_MATERIAL_CONTRIBUTORS
   OR NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED
```

No HTTP/UI router is needed for the first slice. No causal graph table is needed. No model is needed
until the deterministic state model is independently certified.

## 17. Current return point

```text
P14 = SEALED
P15 = SEALED
P16 = SEALED
P17 = SEALED
P18 = PERMANENTLY SEALED / HARDENED

P19 PRE-DEVELOPMENT = COMPLETE
P19 IMPLEMENTATION = AUTHORIZED BY DMP-DEC-0055
P19 PRODUCTION CODE = STARTING

Luna / Sol / C1 = 0 / 0 / 0
engine build = 0
Metabase modification = 0
UI / UX = FORBIDDEN UNTIL P21 SEALED
```

DMP-DEC-0055 is now ratified and this review is the implementation contract. P19 must remain within
its three-record durable boundary and provider-free-first certification protocol.
