# P21 — DECISION INTELLIGENCE PRE-DEVELOPMENT REVIEW

**Date:** 2026-09-26  
**Status:** **PRE-DEVELOPMENT REVIEW COMPLETE / DMP-DEC-0057 / IMPLEMENTATION NOT AUTHORIZED**  
**Consumes:** sealed CURRENT P20 ReportDocument  
**Production code:** 0  
**Tables/migrations:** 0  
**Model calls:** Luna = 0 / Sol = 0 / C1 = 0  
**Engine/Metabase modification:** 0 / 0  
**UI/UX:** NOT AUTHORIZED

## 1. Owner boundary

P21 answers:

```text
Given governed organizational truth,
what should the organization consider deciding or doing?
```

P21 owns advisory decision-intelligence structure:

```text
objective
+ constraints
+ governed factual premises
+ options
+ tradeoffs
+ recommendation
+ limitations
→ immutable/versioned DecisionBrief
```

P21 does not own analytics, Evidence truth, claim truth, causal/root-cause truth, report truth,
forecasting, optimization, human adoption truth, action execution, workflow automation or UI.

Permanent:

```text
P20 REPORT != P21 RECOMMENDATION
P21 RECOMMENDATION != HUMAN-ADOPTED DECISION
HUMAN-ADOPTED DECISION != ACTION EXECUTION
```

## 2. Source-of-truth boundary

The first P21 vertical consumes exactly one sealed and CURRENT P20 ReportDocument as its governed
factual premise boundary.

```text
P21
→ exact P20 typed statement identities
→ no direct P14/P16/P19 reach-around
```

P20 already retains exact upstream lineage. If a required factual premise is absent, P21 records a
limitation or requires a new governed P20 revision. It does not execute analytics or search lower
authorities for a stronger statement.

User-declared objectives and constraints are legal typed inputs, but remain user intent rather than
analytical truth.

## 3. Legacy DecisionRecord audit

Existing historical surface:

```text
backend/control_plane/models.py :: DecisionRecord
backend/app/decision.py
backend/app/routers/decisions.py
```

Observed durable semantics include:

```text
user_id
chosen_json
options_json
rationale
note
contract_ids_json
content_hash
supersedes
sablon_json
```

It is append-only and conceptually records a decision a user/human adopted.

Its evidence/replay assumptions are legacy:

```text
contract_ids_json → Query Contract identities
sablon_json       → cube_query replay
```

Decision:

```text
legacy DecisionRecord
= HISTORICAL HUMAN-ADOPTION COMPATIBILITY

legacy DecisionRecord
!= P21 DecisionBrief
legacy DecisionRecord
!= AI recommendation authority
```

Do not rename, mutate, repurpose or silently migrate it during the first P21 vertical. A future
human-adoption bridge must separately decide whether to adapt it safely or introduce a new adopted
decision authority.

## 4. Recommended first durable state

At most one new P21 durable record family:

```text
DecisionBrief
```

Conceptual minimum fields:

```text
decision_brief_id
report_id
tenant_binding
semantic_context_version
brief_key
revision
parent_decision_brief_id nullable

objective_json
constraints_json
options_json
tradeoffs_json
recommendation_json
premise_refs_json
limitations_json
model_provenance_json nullable

source_report_fingerprint
decision_source_fingerprint
brief_fingerprint
created_at
```

Do not create option/tradeoff/constraint/recommendation/action/workflow/score/forecast/optimization
tables without a measured durability requirement.

## 5. Transient typed contracts

Recommended transient contracts:

```text
DecisionObjective
DecisionConstraint
DecisionPremiseRef
DecisionOption
DecisionTradeoff
DecisionRecommendation
DecisionLimitation
DecisionBriefDraft
```

## 6. Objective and constraints

Objective is explicit before recommendation.

Minimum objective:

```text
objective_id
objective_text
source_kind = USER_DECLARED
```

Do not infer management intent from report prose.

Constraints may be:

```text
USER_DECLARED
P20_PREMISE
```

Report-derived constraints cite exact P20 statement ids. User-declared constraints stay user intent
and are not silently certified as analytical facts.

## 7. Options

Options are advisory candidates. A model or user may propose an option without proving it will work.

```text
OPTION EXISTS AS A PROPOSAL
!=
EXPECTED IMPACT IS PROVEN
```

Do not create a new option-ranking engine.

## 8. Tradeoffs and numeric constraints

Every factual tradeoff premise must cite exact P20 statement ids.

Numeric tradeoffs are legal only when the exact numeric value/unit already exists in P20 and is copied
without semantic transformation.

P21 may not locally calculate ROI, expected uplift, effect size, probability, forecast, weighted
score, optimization objective, contribution percentage, payback period or ranking metrics.

## 9. Recommendation

DecisionRecommendation is advisory.

Conceptual minimum:

```text
recommended_option_ids
rationale
premise_refs
assumption_refs
limitation_refs
```

It may recommend considering an option because governed facts matter under declared constraints.

It may not invent expected impact, causal effect, probability, optimality or root-cause certainty.

## 10. Epistemic ceiling

P21 never upgrades P20 certainty.

If P20 says:

```text
NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED
```

P21 may propose a low-risk experiment, investigation, reversible operational option or evidence
collection. It may not describe the target as a proven cause.

Intervention proposal != causal proof.

## 11. DecisionLegalityGate

Future implementation should contain one deterministic:

```text
DecisionLegalityGate
```

At minimum it verifies:

```text
source P20 report exists
same tenant/context
source P20 report is CURRENT
every factual premise exists in that exact report
premise kind does not exceed P20 statement/epistemic ceiling
numeric premise preserves exact P20 value/unit
recommendation rationale accounts for factual premises
assumptions are explicit
limitations are explicit
no action/execution semantics
no adopted-human-decision claim
```

It validates decision-publication legality, not analytical truth discovery.

## 12. Model role

A model is not required for the first authority vertical.

Provider-free authority can prove typed DecisionBrief, exact P20 provenance, deterministic legality,
immutability, versioning and staleness.

If a later supervisor explicitly authorizes model-backed proposal generation:

```text
MODEL MAY PROPOSE:
options
qualitative tradeoffs
recommendation wording
questions / assumptions

DETERMINISTIC DIMA OWNS:
source legality
tenant/context
P20 currentness
factual premise binding
numeric exactness
epistemic ceiling
limitation preservation
identity/versioning
seal legality
```

No model-generated number or causal statement becomes authority by itself.

Default future certification, only if a model subphase is authorized:

```text
provider-free GREEN
→ one bounded Luna canary
→ STOP
```

Sol/C1 are not default P21 requirements.

## 13. Human adoption boundary

DecisionBrief is advisory. It is not evidence that a human accepted the recommendation.

The first P21 vertical must not automatically write legacy DecisionRecord, approval state, execution
task, action record, workflow or notification.

Human adoption is an explicit later boundary with actor identity and consent.

## 14. Immutability, idempotency and revisions

DecisionBrief is immutable.

Same exact canonical inputs:

```text
same P20 report/fingerprint
same objective
same constraints
same options
same tradeoffs
same recommendation
same limitations
same model provenance, when applicable
```

must reproduce the same identity/fingerprint after restart.

Changed governed source or decision context creates a new revision plus parent_decision_brief_id.
Never rewrite the old brief.

## 15. Currentness / staleness

Do not use mutable is_current as truth.

Derive staleness from source_report_fingerprint, decision_source_fingerprint and current P20
authority. Historical DecisionBrief remains readable but is never silently revalidated.

## 16. Security / tenant boundary

DecisionBrief binds tenant_binding, semantic_context_version, report_id and source_report_fingerprint.
Cross-tenant report discovery fails closed without becoming an existence oracle. P21 does not clone
Metabase permissions.

## 17. Static governance

Future P21 production owner must not directly use/import:

```text
Metabase native executor / bridge
query planner
MBQL / SQL generator
Wren analytical execution
Agent API analytical execution
numpy / pandas / scipy / statistics analytical shortcuts
P14 Evidence creation
P16 claim creation/mutation
P19 assessment creation/mutation
P20 ReportDocument mutation
legacy cube replay
legacy DecisionRecord write path
Action/execution modules
```

## 18. Provider-free first proof set

If implementation is later authorized, minimum proof includes:

```text
1. only CURRENT sealed P20 report can seal a new DecisionBrief
2. stale P20 report rejects new seal
3. foreign tenant/context rejects
4. factual premise missing from source report rejects
5. exact P20 numeric value/unit preserved
6. new numeric calculation rejects
7. P20 uncertainty cannot become causal certainty
8. NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED cannot become "root cause fix"
9. recommendation remains advisory
10. unreferenced factual rationale rejects
11. assumptions remain explicit assumptions
12. limitations survive seal
13. restart idempotency
14. changed governed source creates a revision, never rewrite
15. historical brief becomes stale without mutation
16. legacy DecisionRecord unchanged
17. P14-P20 unchanged
18. analytical execution = 0
19. duplicate receipt/Evidence/claim/P19/report authority writes = 0
20. engine changes/builds = 0
21. model calls = 0 for first authority vertical
22. UI/UX = 0
```

## 19. STOP conditions

Stop future P21 implementation if it requires fresh analytics, forecasting, optimization, new causal
inference, direct lower-authority bypass, P20 mutation, legacy DecisionRecord repurposing, Cube replay
as recommendation authority, action execution, workflow automation, new Evidence/claim/report
authority, UI/UX, or engine/Metabase core modification.

Also stop if advisory recommendation cannot be cleanly separated from human adoption truth.

## 20. Expected future implementation surface

If later authorized, prefer approximately:

```text
backend/app/v3/decision_intelligence.py

backend/control_plane/models.py
  + one DecisionBrief durable model

backend/migrations/versions/
  + one P21 migration

backend/tests/test_v3_p21_decision_intelligence.py

.github/workflows/dima-metabase-p21-provider-free.yml
```

Default:

```text
NO ROUTER
NO UI
NO ANALYTICAL EXECUTION
NO MODEL REQUIRED
```

## 21. Pre-development exit

```text
P20 = SEALED

P21 PRE-DEVELOPMENT = COMPLETE
P21 IMPLEMENTATION = NOT AUTHORIZED

legacy DecisionRecord
= historical human-adoption compatibility
= unchanged

recommended next bounded objective
= provider-free DecisionBrief + DecisionLegalityGate first vertical
  only after explicit supervisor authorization
```

No P21 production code was created by this review.
