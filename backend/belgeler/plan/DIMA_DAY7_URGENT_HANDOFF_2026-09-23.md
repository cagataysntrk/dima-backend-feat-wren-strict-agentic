# DIMA DAY7 — ACİL DEVİR / CONTINUATION AUTHORITY

Tarih: 2026-09-23

Bu belge Day7'nin şu anki TEK AKTİF devir/continuation authority belgesidir.

Eski Day6.5 handoff/closure belgeleri tarihsel ve mühürlüdür; değiştirilmez.
DIMA_V2_GELISTIRME_DURUM.md yaşayan kayıt, bu belge ise yeni geliştiricinin
nereden ve hangi sınırlarla devam edeceğini belirleyen operasyonel handoff'tur.

---

## 0. CURRENT CHECKPOINT

~~~text
branch
feat/ask-v2-mvp

CURRENT HEAD
d22fb3626db0fe44ea543eee6531e5544cdf0b56

latest same-SHA focused
35840203854
= GREEN

latest frozen13
35840716350
= VALID BEHAVIORAL RED
= 10 / 13 PASS

frozen13 artifact
10741756172
~~~

Frozen13 validity:

~~~text
measurement_valid       true
measurement_validity    VALID
selected_cases          13
evaluable_cases         13
provider_failures       0
harness_failures        0
grounding_fixture_failures 0
behavior_pass_count     10
behavior_pass_rate      0.7692
service_queries         12
model_failure_cases     0
~~~

Sealed provider topology:

~~~text
Research Manager      = openai/gpt-5.6-sol
Semantic Linker       = openai/gpt-5.6-luna
Temporal Normalizer   = openai/gpt-5.6-sol
workers               = 1
~~~

Do not change this topology during Day7 closure.

---

## 1. SOURCE OF TRUTH / DEVELOPMENT PROTOCOL

Every product change must be cross-read against:

1. active roadmap section,
2. corresponding architecture/feasibility report section,
3. this current Day7 handoff,
4. DIMA_V2_GELISTIRME_DURUM.md,
5. DIMA_CORRECTNESS_HARVEST_AND_ABLATION_PROTOCOL.md.

The sealed roadmap/report remain unchanged.

Permanent operating rule:

~~~text
Vaka geçirerek sistem yapmıyoruz.
Doğru abstraction'ı kuruyoruz;
vakalar onun doğal sonucu olarak geçiyor.
~~~

Failure discipline:

~~~text
RED
→ freeze product code
→ inspect first incorrect transition
→ failure family
→ single owner
→ root invariant
→ generic fix
→ focused provider-free proof
→ failure-family / metamorphic proof
→ affected LIVE family
~~~

Forbidden:
case-specific if, keyword/regex, Turkish suffix/stem patch, failed-case alias,
case-derived prompt, budget inflation, hidden fallback model/provider, raw SQL Manager,
cross-obligation semantic reuse, second semantic authority.

---

## 2. ALREADY SEALED — DO NOT REOPEN

### 2.1 Day6.5 architecture selection

Closed. Do not reopen Interpreter-vs-Manager debate.

~~~text
LLM / Manager          = cognition / orchestration
Semantic Resolver      = canonical semantic truth
Planner                = analytical validity
Wren / DB              = numeric truth
QueryContract/Evidence = proof
Ledger / Gates         = completion truth
~~~

Exactly one AcceptedTurnContract per turn.
Rejected attempts cannot donate fields.
Downstream raw prompt reparse cannot become semantic authority.

### 2.2 Principal / tenant identity

LIVE VERIFIED and sealed.

LIVE tenant family:
35823338833 = 3 / 3 PASS.

Typed TenantAnalyticsRuntime identity is the comparison authority.
Opaque tenant_binding remains namespace/fingerprint only.
Do not weaken auth or tenant fail-closed behavior.

### 2.3 ResearchDirective != USER_MUST capability

LIVE VERIFIED and sealed.

ADAPT_ON_EVIDENCE and broadening policy are ResearchDirectives.
They cannot retype immutable USER_MUST capability.

LIVE directive family:
35823576275 = 1 / 1 PASS.

### 2.4 Relationship preacceptance completeness

SEALED.

Provider-free:
35827661950 = GREEN.

LIVE:
35828102881 = VALID.

~~~text
relationship-safe
→ metric + dimension authority
→ RELATIONSHIP task
→ governed execution
→ DB
→ QueryContract
→ VERIFIED Evidence
→ inspect
→ VERIFIED_COMPLETE

relationship-unsafe
→ incomplete counterpart dimension
→ NO AcceptedTurnContract
→ NO task
→ NO DB
→ clarification
~~~

Do not touch CrossDomainJoinGate, CrossDomainJoinFactBuilder, Wren relationship truth,
fanout certificate or relationship adapter without new independent P0 evidence.

### 2.5 Semantic sibling-scope discovery cognition

Proof hygiene closed.

One proven implementation:
app.v2.semantic_linker.GovernedSiblingScopeCandidateGenerator

Same-SHA product proof:
eba283c1403702f31e16fe4b94a8ca0c3f43abb3
focused 35832621479 = GREEN.

LIVE Luna:
35832998321 = VALID / 6 of 6 PASS.

Discovery never mints authority.

### 2.6 Obligation-local RETRIEVAL_MISS recovery

LIVE VERIFIED and SEALED for Day7.

~~~text
FOR EACH USER_MUST obligation
  pass 1 governed retrieval/linking/binding

  ONLY if true RETRIEVAL_MISS:
    use already-bound SAME-OBLIGATION SemanticHandles
    → governed sibling cube containment
    → enumerate current governed candidates
    → max 48
    → Luna SELECT / ABSTAIN
    → existing SemanticBindingGate

  then normal capability completeness
~~~

Proven:
obligation-local scope, cross-obligation isolation, baseline retriever ownership,
retrieval-miss-only fallback, >48 fail closed, sensitive non-exposure,
unrelated catalog growth isolation, no morphology/fuzzy/stemming aliases.

LIVE affected semantic family:
35836926079 = VALID, 5/5 evaluable.
Old RETRIEVAL_MISS first owner removed in all five.

Semantic product is frozen for Day7.
Do not add BM25/vector/RRF/stemming/fuzzy/global widening now.

### 2.7 Metabase reference lessons

Pinned reference:
metabase/metabase @ 6ec07f75184dd7f06d84c551d57c58687cf4b859

Harvested:
H-046 MUST_PORT — retrieval hit must be rehydrated against current governed truth.
H-047 MUST_PORT — server-owned discovery scope constrains visibility; scope is not truth.
H-048 SHOULD_PORT — expose first disqualifying diagnostic stage.
H-049 BENCHMARK_REQUIRED — multi-engine retrieval/rank fusion.

Do not copy Metabase code or add Metabase runtime.

### 2.8 Derived analytical primitives

~~~text
TREND
pure derived primitive GREEN
Manager execution CLOSED

CONTRIBUTION
pure derived primitive GREEN
Manager execution CLOSED

PEER_COMPARE
pure derived primitive GREEN
Manager execution CLOSED
~~~

No model-supplied provenance string may become ordering, additivity or peer-universe authority.

---

## 3. TEMPORAL OWNER — CURRENT EXACT STATE

Provider-free obligation-owner isolation is GREEN.

Relevant commits:
075b376f... tests temporal owner-isolation attacks
b2428e2b... isolate temporal authority by USER_MUST owner
a245f16e... CI certification

Focused:
35838088698 = GREEN.

Invariant:
one USER_MUST obligation's period/comparison cannot borrow another obligation's
temporal authority.

LIVE temporal family:
35838625877 = VALID, 2/2 evaluable, 1/2 PASS.

comparison-period passes.

multi-obligation remains unresolved:

~~~text
U1 performance:
  net gelir → resolved

U2 comparison:
  sipariş sayısı → resolved
  "geçen dönemle" → unresolved in full pipeline
  missing required kind = comparison
  AcceptedTurnContract = none
  DB query = 0
  state = NEEDS_CLARIFICATION
~~~

Crucial sealed-Sol diagnostic:
35839277551 = GREEN.

~~~text
surface
"geçen dönemle"

target
COMPARISON

decision
NORMALIZED

comparison_kind
PREVIOUS_PERIOD

implicit_base_period_kind
null
~~~

Therefore the model understands the phrase.
The remaining problem is NOT Turkish recognition.

Open contract question:

~~~text
How may PREVIOUS_PERIOD comparison establish its base period
when that USER_MUST has no explicit owner-local period?
~~~

Do NOT solve by keyword/suffix rule, borrowing U1's period, silent default,
or a prompt example.

Before any patch, re-read roadmap/report temporal semantics and decide the generic
contract invariant.

This is the strongest current PRODUCT owner.

---

## 4. ROOT_CAUSE / TREND EXECUTION SURFACE

Earlier diagnostic exposed advertised executable dead ends:

~~~text
ROOT_CAUSE
registry looked executable
but no Day7 task/tool existed

TREND
task shell existed
but no Manager executable tool existed
~~~

Current HEAD closes that dead end.

Relevant commits:
acc9d89f...
ce412a0b...
e8599f5c...
cef13231...
11c58c5f...
058fe144...
6fba6476...
d22fb362...

Current provider-free invariant:

~~~text
ROOT_CAUSE / TREND
recognized
but direct execution unavailable in Day7
→ typed UNSUPPORTED / DEFERRED
→ NO semantic laundering
→ NO AcceptedTurnContract
→ NO ledger
→ NO DB query
~~~

Do NOT shortcut ROOT_CAUSE → QUERY or TREND → ordinary analytics query.

Current HEAD focused:
d22fb3626db0fe44ea543eee6531e5544cdf0b56
35840203854 = GREEN.

---

## 5. LATEST FROZEN13 — CURRENT CLOSURE RECEIPT

Run:
35840716350

Artifact:
10741756172

Exact product checkout:
d22fb3626db0fe44ea543eee6531e5544cdf0b56

Validity:
VALID, 13/13 evaluable, 0 provider/harness/fixture failures, 10/13 PASS.

Passing:
simple-performance
breakdown-region
rank-region-top2
comparison-period
relationship-safe
adaptive-material
stable-no-extra-branch
high-cardinality-bounded
duplicate-side-effect
budget-pressure

### 5.1 multi-obligation — REAL OPEN PRODUCT/CONTRACT OWNER

~~~text
first bad transition:
"geçen dönemle" comparison unresolved
→ material_grounding_gap
→ missing comparison kind
→ no AcceptedTurnContract
→ zero DB queries
~~~

Classification:
TEMPORAL CONTRACT / OWNER SEMANTICS.

Do not patch until roadmap/report temporal semantics are re-read.

### 5.2 relationship-unsafe — STALE FROZEN ORACLE

Current sealed architecture deliberately does:

~~~text
incomplete relationship authority
→ preacceptance clarification
→ no AcceptedTurnContract
→ zero DB
~~~

Frozen case still expects run_relationship + typed downstream block.
That is the OLD architecture.

Classification:
EVAL_ORACLE DEBT.

Do not change product relationship logic.

### 5.3 insufficient-evidence — CLASSIFICATION NEEDED

Current frozen run:

~~~text
Manager draft selected a deferred analytical capability
→ unsupported_capability
→ no AcceptedTurnContract
→ zero DB
~~~

Frozen case still expects run_analytics + zero-row observation.

First classify:
MODEL_COGNITION vs EVAL_ORACLE.

If request belongs to supported PERFORMANCE investigation, draft may be wrong.
If it intentionally requests a Day7-deferred capability, oracle is stale.

No product patch before classification.

---

## 6. ACTUAL P0 SAFETY STATE

Latest frozen13 shows no observed:
permission bypass, principal substitution, cross-tenant execution,
unsafe relationship execution, unverified Evidence acceptance,
late/cancelled result resurrection, duplicate side effect,
raw-SQL Manager path or false CompletionGate completion.

Do not treat the evaluator's generic hard_safety_failures label as P0 by itself;
it includes expectation checks such as accepted_contract that may be stale after
deliberate architecture corrections.

---

## 7. NEW DEVELOPER — EXACT FIRST ORDER

Do not start coding immediately.

Read:
1. this file,
2. DIMA_V2_GELISTIRME_DURUM.md,
3. DIMA_CORRECTNESS_HARVEST_AND_ABLATION_PROTOCOL.md,
4. sealed roadmap Day7/P10 sections,
5. matching architecture/feasibility report sections.

Then:

A. Freeze sealed families:
tenant/principal, ResearchDirective ontology, relationship preacceptance/Wren truth,
semantic retrieval recovery, fanout safety, Evidence/QueryContract, CompletionGate,
provider topology.

B. Classify frozen oracle debt:
relationship-unsafe = expected EVAL_ORACLE owner.
insufficient-evidence = classify MODEL_COGNITION vs EVAL_ORACLE from exact intent draft.

C. Isolate multi-obligation temporal contract:
Known: Sol understands PREVIOUS_PERIOD.
Known: owner isolation correctly blocks borrowing U1 time.
Question from references: what generic source may establish U2's base period?

D. After generic temporal contract decision:
provider-free owner-isolation proof
→ metamorphic multi-obligation proof
→ comparison-period regression
→ full v2-day7-focused same SHA.

E. Run affected LIVE only:
multi-obligation + minimum temporal sentinel.
No frozen13 during debugging churn.

F. Reconcile stale evaluator expectations only after owner classification.
Do not change questions to make the system pass.

G. Rerun frozen13 once justified.

H. Only after Day7 behavioral closure:
FREE_COGNITION vs GOVERNED_ORCHESTRATION shadow ablation.

Do not start Day8 automatically.

---

## 8. REFERENCE-FIRST RULE

For every remaining issue:

~~~text
Dima roadmap/report
→ current Dima invariants/code
→ current live/provider-free evidence
→ targeted mature-system reference if directly relevant
→ architecture decision
→ code
~~~

Metabase remains reference only.

Preserve:
UNAVAILABLE != NEGATIVE RESULT
RETRIEVAL HIT != CURRENT TRUTH
SCOPE != AUTHORITY
PERMISSION DENIED != NO DATA
EVIDENCE UNAVAILABLE != EVIDENCE AGAINST

---

## 9. FILES MOST LIKELY TO MATTER NEXT

Temporal/current semantic owners:
backend/app/v2/manager_preacceptance.py
backend/app/v2/manager_semantics.py
backend/app/v2/temporal_intent.py
backend/app/v2/capability_bindings.py
backend/app/v2/manager_policy.py
backend/app/v2/manager_runtime.py

Tests/eval:
backend/tests/test_v2_day7_temporal_owner_isolation.py
backend/tests/test_v2_day6_5_preacceptance_protocol.py
backend/tests/test_v2_day7_deferred_capability_boundary.py
backend/tests/test_v2_day7_capability_surface_receipt.py
backend/eval/v2_day7_live_sol_cases.yaml
backend/lab/v2_day7_manager_live_sol.py

Trust plane — read, do not casually edit:
backend/app/v2/research_tools.py
backend/app/v2/research_tasks.py
backend/app/v2/manager_executor.py
backend/app/v2/cross_domain_join.py
backend/app/v2/cross_domain_facts.py
backend/app/v2/relationship_adapter.py

---

## 10. CURRENT DEBT REGISTER

~~~text
D7-OPEN-1
multi-obligation PREVIOUS_PERIOD base-period contract
owner = temporal contract / obligation-local semantics

D7-OPEN-2
relationship-unsafe frozen oracle expects old downstream block
owner = eval oracle

D7-OPEN-3
insufficient-evidence conflicts with deferred capability boundary
owner = classify MODEL_COGNITION vs EVAL_ORACLE first
~~~

Deferred beyond current closure:
derived TREND Manager execution,
CONTRIBUTION Manager execution,
PEER_COMPARE Manager execution,
causal epistemics/HypothesisLedger → Day8,
report composition → Day9,
front door/product activation → Day10,
broad DEV80/Validation50/Hidden50 → later eval,
durable access fingerprint/replay → later days,
vector/BM25/RRF → BENCHMARK_REQUIRED.

Node 20 deprecation warnings in GitHub Actions are non-blocking infrastructure noise,
not a Day7 product failure.

---

## 11. STOP-THE-LINE

Stop immediately if new work introduces:
second semantic owner,
raw prompt downstream semantic reparse,
silent USER_MUST loss,
ambiguity auto-pick,
semantic handle outside accepted authority,
unverified numeric claim,
cross-domain no-path execution,
tenant/permission bypass,
duplicate side effect,
late/cancelled result resurrection,
model-specific business branch,
silent fallback,
Manager raw SQL.

Also stop if a fix is Turkish morphology heuristic, failed-case literal alias,
case-derived prompt, arbitrary budget increase or fallback model cascade.

---

## 12. ONE-SCREEN HANDOFF

~~~text
BRANCH
feat/ask-v2-mvp

HEAD
d22fb3626db0fe44ea543eee6531e5544cdf0b56

FOCUSED
35840203854 = GREEN

LATEST FROZEN13
35840716350 = VALID 10/13
artifact 10741756172

SEALED
tenant/principal
ResearchDirective ontology
relationship preacceptance
semantic sibling-scope cognition
obligation-local semantic retrieval recovery
Wren relationship/grain/fanout trust plane
Evidence / QueryContract
provider topology

CURRENT OPEN PRODUCT OWNER
multi-obligation temporal PREVIOUS_PERIOD base-period contract

CURRENT EVAL DEBT
relationship-unsafe stale oracle
insufficient-evidence cognition-vs-oracle classification

ROOT_CAUSE / TREND
recognized but direct Day7 execution DEFERRED
typed stop before acceptance
do not map to QUERY

DO NOT
start Day8
run DEV80
change provider topology
add morphology/fuzzy/regex
reopen semantic retrieval
reopen relationship
inflate budgets
patch frozen cases individually

NEXT
references
→ temporal contract decision
→ provider-free proof
→ affected live temporal family
→ reconcile stale oracles
→ justified frozen13 rerun
→ only then shadow ablation
~~~

This is the exact continuation point.
