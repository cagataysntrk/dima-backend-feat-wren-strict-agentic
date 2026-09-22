# DIMA — DAY6.5 FINAL CLOSURE AND DAY7 HANDOFF

**Date:** 2026-09-22  
**Branch:** `feat/ask-v2-mvp`  
**Final Day6.5 product checkpoint:** `dd5c16bbe444b6d9183faea9e9937be11260f394`  
**Documentation closure payload commit:** `2147a7e858a38e1526b0bbd343bdd750cac47a50`  
**Day6.5:** **CLOSED**  
**Next canonical ticket:** **P10 / DAY7 RESULT-AWARE RESEARCH LOOP**  
**Production /ask-v2:** OFF  
**DEV80 / Validation50 / Hidden50 / FINAL FREEZE:** FORBIDDEN NOW

This is the single current continuation authority for a new developer.
Historical receipts remain audit evidence but do not override this document.

> Git note: the authoritative handoff branch is `feat/ask-v2-mvp`; verify its HEAD before work.
> The product-code checkpoint is fixed above. `2147a7e...` is the complete closure payload commit;
> any later commit in this closure must be documentation-only consistency metadata.

## A. Final checkpoint and closed evidence

```text
product checkpoint                    dd5c16bbe444b6d9183faea9e9937be11260f394

D65-SI                                FINAL GREEN / SEALED
provider-free final                   73/73 GREEN
focused live 001/005                  GREEN
frozen six-case full-live             GREEN
real Wren sentinel                    GREEN

provider topology                     SEALED ENGINEERING TOPOLOGY
  SEMANTIC_LINKER                     Luna
  TEMPORAL_NORMALIZER                 Sol
  RESEARCH_MANAGER                    Sol

M0E-DEEP-DELTA                        FINAL GREEN / SEALED
Metabase source pin                   74216b30981d8310c4cf724d63ca282e2e63529d

X0 bridge CI                          35761526816 SUCCESS
bridge terminal                       HEAVY_SEMANTIC_DUPLICATION
runtime_started                       false
Metabase API called                   false
```

Bridge evidence:

```text
representative families               8
thin/lossless                         7/8

non-lossless family                   cari.bakiye
metric semantics                      SUM(borc - alacak)
metric_formula_duplication            true
grain_additivity_duplication          true
unsupported shape                     computed_metric_expression:bakiye

manual semantic mappings              0
unapproved implicit joins             0
second semantic authority             0
semantic handle remint                0
duplicated semantic definitions       2
unsupported semantic shapes           1
```

This was a **successful negative preflight**, not a failed Metabase benchmark.

## B. Closed architecture decisions

### Dima owns

```text
cognition
accepted authority
trust plane
Research orchestration
Evidence
completion truth
future root-cause / decision intelligence
product decision records
```

### Wren owns

```text
MDL
models / views / cubes
metrics
metric formulas
relationships
grain / additivity
business semantic knowledge
semantic compilation
governed analytical execution
```

### Metabase — current release

```text
structured analytical execution runtime dependency = NO
Agent API production dependency                     = NO
X0-REST                                              = NOT RUN / NOT REQUIRED
```

Metabase remains valuable as:

```text
architecture reference
security-pattern reference
query-lifecycle reference
async/workflow reference
permission/replay/cache reference
product/workspace candidate
  dashboards
  charts
  saved questions
  collections
  search/workspace UX
  exploration UX
  embedding/product surfaces
```

The REJECT is scoped:

> **retained Wren semantic truth → thin Metabase structured execution** is rejected for this release
> because full fidelity for computed/semi-additive semantics requires semantic formula/grain
> reconstruction.

Do not restate this as “Metabase cannot compute metrics” or “Metabase permanently rejected.”
Independent future evidence may reopen it.

## C. Permanent anti-patch / authority invariants

```text
regex semantic authority              = 0
fuzzy semantic authority              = 0
stemming/morphology semantic authority= 0
named-case product branch             = 0

retrieval != authority
index hit != authority
retrieval miss != semantic gap

candidate selection = bounded cognition
SemanticBindingGate = sem_* authority

LLM cognition
Resolver / governed binding = semantic truth
Wren planner/execution       = analytical/numeric truth
Evidence/QueryContract       = proof/trust

raw SQL Manager path         = forbidden
second semantic owner        = forbidden
silent USER_MUST loss        = forbidden
unverified numeric claim     = forbidden
```

Day6.5 semantic discovery / Standard integration must not be reopened without new independent
invalidating P0 evidence.

## D. Day7 exact starting position

Canonical ticket:

```text
P10 / DAY7 RESULT-AWARE RESEARCH LOOP
```

Target shape:

```text
Accepted Research authority
→ bounded Research tasks
→ governed tool execution
→ EvidenceArtifact
→ observe actual result
→ adapt / replan
→ coverage + budget
→ repeat or terminal
```

### Read these code surfaces first

1. `app/v2/agent_runtime.py`
2. `app/v2/manager_loop.py`
3. `app/v2/manager_runtime.py`
4. `app/v2/manager_tools.py`
5. `app/v2/manager_executor.py`
6. `app/v2/manager_progress.py`
7. `app/v2/manager_policy.py`
8. `app/v2/manager_preacceptance.py`
9. `app/v2/manager_models.py`
10. `app/v2/research.py`

Then read:
- `DIMA_NIHAI_UYGULAMA_YOL_HARITASI.md` P10 / Day7;
- corresponding R sections in the sealed audit report;
- this handoff's carry-forward matrix below.

### Reuse; do not rewrite

`agent_runtime.py`
- reuse bounded counters/budgets/observations/action+state fingerprints/no-progress/terminal mechanics;
- keep it authority-blind.

`manager_preacceptance.py`
- reuse finite pre-acceptance authority flow;
- do not re-open AcceptedTurnContract semantics in Day7.

`manager_runtime.py`
- reuse exactly-one Research acceptance/shared cross-family authority behavior;
- extend post-acceptance result-aware execution, not pre-acceptance ownership.

`manager_tools.py`
- preserve closed typed tool contracts;
- add only roadmap-authorized Research tools/contracts;
- no raw SQL.

`manager_executor.py`
- reuse governed core execution adapters and evidence-producing boundaries;
- do not create a second planner/semantic engine.

`manager_progress.py`
- reuse action/progress fingerprints;
- Day7 loop must stop duplicate/no-progress cycles generically.

`manager_policy.py`
- preserve role-scoped model abstraction;
- no model-name branches in domain logic.

`manager_models.py`
- extend typed Research state/tasks/evidence only when P10 requires it;
- do not create another semantic authority type.

`research.py`
- preserve ResearchBrief as projection/UI/audit view;
- accepted semantic authority and living ResearchState remain conceptually distinct.

### Day7 must not rewrite

- Standard semantic discovery/linker;
- StandardLaneEngine;
- provider topology;
- Wren semantic backbone;
- QueryContract semantics merely to fit the new loop;
- front-door router (Day10 owner);
- Metabase execution bridge.

## E. Open release debt / ownership

```text
Day7   Result-Aware Research Loop
Day8   HypothesisLedger / root cause
Day9   ReportDocument
Day10  /ask-v2 STANDARD|RESEARCH front-door ownership closure
Day11  eval expansion
Day12  QueryContract / evidence / telemetry hardening
Day13  principal / PII / security hardening
Day14  persistence / resume
Day15  pilot flag / rollback code

then final 20–25 integrated rehearsal
then DEV80 exactly once
then code freeze
then Validation50 no tuning
then fresh Hidden50 no tuning
then certification
then pilot activation
```

`FRONTDOOR_OWNERSHIP_CLOSURE` remains a Day10 release blocker:
authoritative legacy `SemanticResolver` / heuristic fallback must be zero before FINAL FREEZE.

## F. Metabase carry-forward matrix — DO NOT LOSE THESE GAINS

These patterns came from the M0E/M0E-DEEP-DELTA audit. Metabase execution rejection does not
erase them.

### DAY7 — Research loop

| Mechanism | Day7 invariant / owner |
|---|---|
| Missing principal / creator | **FAIL CLOSED** before any async/governed execution |
| Async task identity | idempotent; duplicate delivery cannot duplicate side effects |
| Cancel / planning race | canceled work cannot resurrect after late plan/task materialization |
| Research fanout | cardinality-bounded; high/unknown cardinality → bounded Top-K + Other/equivalent |
| Prior accumulated state vs current-turn delta | keep distinct; prior state cannot silently create USER_MUST or mutate current authority |
| Retrieval/search/index | discovery only; never authority |
| Retrieval availability | `UNAVAILABLE != NO_MATCH != SEMANTIC_GAP` |
| High-cardinality indexed entity | current-principal live re-read before governed filter/handle |

### DAY8 — epistemic/root-cause

```text
interestingness = prioritization signal only
interestingness != truth
interestingness != cause
interestingness != verified finding
```

Only verified Evidence may support root-cause/hypothesis conclusions.

### DAY9 — report/evidence

```text
derived Report/Evidence/result
→ current-viewer authorization required

official-content / verification metadata
→ preserve provenance
```

Creator identity or saved artifact reference is not permanent authorization.

### DAY10 — front door

```text
/api/ask-v2
→ STANDARD | RESEARCH dispatcher

legacy SemanticResolver authoritative execution = 0
legacy heuristic fallback                       = 0
```

Do not migrate this during Day7.

### DAY12–14 — trust/replay

Design/propagate `ExecutionAccessFingerprint`:

```text
tenant_binding
principal_subject
role_set_digest
attribute_policy_digest
policy_version
RLS/CLS rule-version digests
database route / destination / impersonation role
semantic_context_version
source object refs
security parameter digest
```

No raw PII/sensitive attributes in persisted fingerprint.

Also preserve:

```text
permission-sensitive result/cache reuse
→ current access fingerprint compatibility required

security-bound persistence:
cannot faithfully serialize security binding
→ persistence/replay FORBIDDEN

representation repair
→ idempotent

retrieval candidate
→ current-principal hydration before authority
```

### DAY14 — resume/replay

```text
resume/replay
→ current principal reauthorization
→ access fingerprint compatibility
→ otherwise deny or recompute
```

### PRODUCT / WORKSPACE TRACK — separate from correctness critical path

Preserve for later product evaluation:

```text
saved questions
charts
dashboards
collections
workspace/search
exploration UX
embedding/product surfaces
```

No Metabase execution runtime is required to preserve this track.

## G. Day7 development protocol

- Plan + sealed audit report are authority.
- Read P10 and corresponding R sections before code.
- Living status gets commit/SHA, reason, test result, debt, failure family and next action.
- Fast vertical slices.
- Normal test loop: code → focused/provider-free → focused real LLM when material → failure family/metamorphic → small real scenarios.
- workers=1 before concurrency/performance.
- RED → receipt/classification before patch.
- Infra/provider failure != semantic failure.
- No regex/keyword/morphology/fuzzy/case-derived prompt patches.
- No model-specific business branches.
- No raw SQL Manager tool.
- User MUST immutable; agent-derived task is separate.
- Evidence must govern result-aware adaptation.
- Budget/no-progress/duplicate loop must be deterministic.

## H. Day7 STOP-THE-LINE conditions

Stop and fix abstraction if any appear:

```text
second semantic owner
silent requirement loss
ambiguity auto-pick
raw prompt downstream semantic reparse
unverified numeric claim
cross-domain no-path join
tenant/security bypass
missing principal widened to default execution
duplicate async task side effect
cancelled work resurrected
unbounded research fanout
model-specific business branch
silent fallback
```

## I. Day7 developer startup prompt

```text
Repo: cagataysntrk/dima-backend-feat-wren-strict-agentic
Branch: feat/ask-v2-mvp

Before changing code:
1. Verify branch HEAD.
2. Read backend/belgeler/plan/DIMA_DAY6_5_FINAL_CLOSURE_AND_DAY7_HANDOFF.md.
3. Read backend/belgeler/plan/DIMA_V2_GELISTIRME_DURUM.md.
4. Read backend/belgeler/plan/DIMA_RELEASE_FINAL_INTEGRATED_GATE.md.
5. Read sealed roadmap P10 / Day7 and the audit report sections it references.
6. Read backend/AGENTS.md, backend/CLAUDE.md and backend/MIMARI.md.
7. Inspect, in order:
   app/v2/agent_runtime.py
   app/v2/manager_loop.py
   app/v2/manager_runtime.py
   app/v2/manager_tools.py
   app/v2/manager_executor.py
   app/v2/manager_progress.py
   app/v2/manager_policy.py
   app/v2/manager_preacceptance.py
   app/v2/manager_models.py
   app/v2/research.py

Authority already closed:
- Day6.5 CLOSED.
- D65-SI FINAL GREEN / SEALED.
- Semantic=Luna, Temporal=Sol, Research=Sol engineering topology sealed.
- M0E-DEEP-DELTA FINAL GREEN / SEALED.
- Metabase bridge preflight ended HEAVY_SEMANTIC_DUPLICATION.
- Metabase structured execution is rejected for the CURRENT RELEASE only.
- X0-REST was not run and is not required.
- Wren semantic backbone and analytical execution remain PRIMARY.
- Metabase production runtime dependency is OFF.
- /ask-v2 remains OFF and its ownership migration belongs to Day10.
- DEV80/Validation50/Hidden50/final freeze are forbidden now.

Your only canonical ticket:
P10 / DAY7 RESULT-AWARE RESEARCH LOOP.

Goal:
accepted Research authority
→ bounded tasks
→ governed execution
→ EvidenceArtifact
→ observe actual result
→ adapt/replan
→ coverage + budget
→ repeat/terminal.

Reuse existing agent/runtime/authority/tool/evidence abstractions.
Do NOT rewrite Standard semantic discovery, provider topology, Wren semantics/execution,
or build a new semantic resolver/planner.

Carry forward these mandatory patterns:
- missing principal/creator → fail closed;
- async task identity → idempotent;
- cancellation → no race resurrection;
- fanout → cardinality bounded;
- prior accumulated state != current-turn delta;
- retrieval/index != authority;
- interestingness != truth/cause (Day8);
- derived artifact reads require current-viewer authorization (Day9);
- ExecutionAccessFingerprint + permission-sensitive replay/cache (Day12–14);
- security binding not faithfully serializable → persistence/replay forbidden;
- resume/replay → current-principal reauthorization (Day14).

Development protocol:
focused/provider-free first, workers=1 first, RED classify before patch,
no regex/fuzzy/morphology/named-case prompt patches, no raw SQL Manager tool,
no hidden fallback, no model-specific business branch.

Do not start Day8, Day9, Day10, DEV80, Validation50, Hidden50, final freeze or pilot.
Document every meaningful commit/test/debt in living status.
```

## J. Read order for the new developer

1. this file;
2. `DIMA_V2_GELISTIRME_DURUM.md`;
3. `DIMA_RELEASE_FINAL_INTEGRATED_GATE.md`;
4. sealed roadmap P10 / Day7 + referenced audit R sections;
5. `AGENTS.md`;
6. `CLAUDE.md`;
7. `MIMARI.md`;
8. the ten Day7 code surfaces in §D;
9. M0E-DEEP-DELTA receipt only when implementing its mapped future invariant.

## K. Final boundary

The Day6.5 closer does **not** implement Day7.

No Research scheduler/loop changes, HypothesisLedger, ReportDocument, front-door migration,
DEV80, Validation50, Hidden50, final freeze or pilot work belongs in this closure.
