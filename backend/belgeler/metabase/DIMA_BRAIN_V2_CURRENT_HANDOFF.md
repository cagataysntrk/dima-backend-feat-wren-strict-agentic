# DIMA BRAIN V2 — CURRENT HANDOFF

**Status:** ACTIVE — PHASE 1 ACCEPTANCE CLOSURE  
**Branch:** `feat/dima-brain-v2`  
**Decision:** DMP-DEC-0076  
**Roadmap:** `DIMA_BRAIN_V2_TWO_PHASE_ROADMAP.md`  
**Execution directive:** `DIMA BRAIN V2 — FINAL DEVELOPER EXECUTION DIRECTIVE`

## Current identities

~~~text
branch point / legacy Platform HEAD
8d1e011053b01005179ff7a31b7921bb3a7307b9

legacy Product behavior
c5069e8e4606e21bdd8ce41f4c1dc4bf7d23c789

engine
0f16f2b5a1ec774ac7afee6214c726e82f9ceb3c
0.63.18-dima.8

engine state
FROZEN

engine builds during Brain V2 work
0
~~~

The active branch HEAD moves with the small-commit acceptance work. Read the
branch HEAD directly before editing; do not use the historical HEAD embedded in
the original execution directive.

## Current architecture decision

Do not return to the historical ~70.8 candidate.

Do not restart the orchestration architecture.

Do not strategically extend the legacy custom orchestrator.

~~~text
Metabase / Metabot = analytics + native query cognition
LangGraph          = orchestration / routing / checkpoint / resume
Dima DB            = canonical truth
Thin Dima Brain    = business semantics / scope / Evidence / epistemics
Headless Product   = governed projection
~~~

Permanent invariant:

~~~text
LANGGRAPH STATE != DIMA TRUTH
~~~

No second Evidence/Hypothesis/Scope/Report authority is allowed.

## Critical user override

UI / UX / frontend work is currently forbidden.

Do not build:

~~~text
frontend
web UI
dashboard
Ask screen
Investigation screen
Evidence Drawer
Report/Decision UI
demo frontend
animations / visual product work
~~~

Current allowed scope:

~~~text
LangGraph orchestration
Dima Brain/domain
Metabase/Metabot integration
Evidence / scope / P18 / P19 / P20
checkpoint/resume
dedup/context efficiency
provider-free tests
surgical paid live tests
30-CASE READY preparation
~~~

Execution order:

~~~text
Brain + engine integration complete
→ provider-free GREEN
→ targeted live/manual quality strong
→ backend-only Phase 2 T1–T7 + metamorphic confidence
→ 30-CASE READY
→ STOP
~~~

The 30-case remains forbidden without separate explicit user authorization.

## Phase 1 implementation state

The low-level LangGraph V2 foundation is no longer the task list; it exists.

Implemented/proven provider-free:

~~~text
reference-only BrainGraphState
explicit StateGraph routing
Postgres-backed production checkpoint boundary
checkpoint/resume
tenant/principal isolation
scope mutation / historical-current separation
cognition request keys/dedup
native material request dedup
ONE_PASS route
ADAPTIVE route
DISCOVERY route
P17 direct next-test seam
P19 assessment
P20 governed report handoff
legacy-v2 semantic compatibility gates
~~~

Do not refactor these foundations unless a concrete correctness defect proves it
necessary.

## Latest ONE_PASS live receipt

Latest completed live:

~~~text
run
36764193520

candidate Product SHA
3f62c9e6a8b85def214314749baf6ea395c7af49

engine
0f16f2b5a1ec774ac7afee6214c726e82f9ceb3c
0.63.18-dima.8

mechanical
GREEN

provider requests
7 total
1 Research Intake
5 Metabase/Metabot
0 P17
1 P19

prompt tokens
88,838

native acquisitions
1

latency
28,883 ms

provider reported cost
$0.01218943
~~~

This is a material orchestration/cost improvement over the old custom runtime.

However **Phase 1 is NOT accepted yet**.

Manual Product adjudication found a real material-fidelity defect:

~~~text
accepted user authority:
May 2026 vs June 2026 causal investigation
+ maintenance-delay candidate
+ spare-part-delay candidate

native Evidence result:
columns
- Machine Downtime Minutes
- Maintenance Delay Hours
- Spare Part Delay Hours

rows
[656, 21.0, 10.0]
~~~

The result was one aggregate observation. It did not expose the accepted
May-vs-June comparison as result-level Evidence. P19 therefore correctly
terminalized with:

~~~text
NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED
~~~

and correctly stated that temporal comparison/ordering was unavailable.

Mechanical GREEN therefore did not equal Product-quality FULL. The current
ONE_PASS receipt is not the final 4/4 acceptance artifact.

## Current root-cause diagnosis

The first wrong transition was:

~~~text
typed temporal comparison authority
→ native analytical contract
→ native occurrence query semantics
→ aggregate result
→ Evidence admitted as obligation-complete
~~~

The defect is **not** LangGraph routing and **not** P19.

The missing invariant was result-level material coverage:

~~~text
User semantic comparison
→ typed AnalyticalRequestContract
→ exact native result
→ deterministic Evidence coverage
~~~

For an accepted two-period comparison, a result that does not actually expose
both accepted periods must not become FULL/VERIFIED obligation coverage.

## Current fix family

Do not solve this with regex, month names, metric names, benchmark wording or
provider-limit inflation.

The active generic fix family is:

1. typed temporal comparison canonicalization:
   - temporal comparison authority comes from typed `TEMPORAL_PERIOD`
     comparison + exact accepted periods;
   - operational baseline/comparison roles are canonicalized deterministically;
   - the RCA-specific prompt patch is removed;

2. deterministic result coverage before Evidence promotion:
   - exact governed time-field identity comes from native bindings;
   - Metabase dataset column metadata must expose that exact time field;
   - result rows must contain at least one value in each accepted half-open
     comparison period;
   - incomplete coverage fails closed before VERIFIED Evidence is created;

3. persist a bounded `material_result_coverage` receipt inside Evidence payload.

Current small commits in this fix family include:

~~~text
446f33d3  fix(intake): canonicalize typed temporal comparison authority
c8023fe7  feat(p14): verify typed temporal result coverage before Evidence
7189cbab  feat(p14): fail closed on incomplete comparison Evidence coverage
23c37227  test(p14): prove typed comparison result coverage
80623d58  ci(brain-v2): include material result coverage in closure
~~~

The full provider-free closure for this family is:

~~~text
36766883034
~~~

Treat its final conclusion as the next authority before any paid rerun.

## Paid/live discipline

Paid trigger is disarmed after run `36764193520`.

Never rerun the same SHA hoping for luck.

Sequence:

~~~text
provider-free reproducer
→ generic typed fix
→ metamorphic sibling
→ full provider-free closure
→ freeze candidate
→ ONE surgical live
→ inspect artifact
→ manual adjudication
~~~

No broad paid run.

## Phase 1 remaining acceptance order

Do not skip ahead.

~~~text
1. temporal material fidelity provider-free GREEN
2. ONE_PASS live mechanical GREEN + manual 4/4
3. ADAPTIVE live mechanical GREEN + manual >=3
4. DISCOVERY live mechanical GREEN + manual >=3
5. live multi-turn scope mutation/resume proof
6. 3-mode average >=3.3
7. checkpoint/resume + dedup + security remain GREEN
8. engine remains dima.8
9. Phase 1 ACCEPTED
~~~

Only after Phase 1 acceptance may Phase 2 backend certification continue.

## Phase 2 interpretation under current override

Phase 2 currently means **backend/headless Brain productization only**.

Allowed:

~~~text
stable thin Brain contracts
bounded progress/event projections
current scope projection
investigation timeline projection
Evidence list/detail projection
hypothesis/P19 projection
ReportDocument projection
clarification/resume contract
limitations/terminal projection
P18 observational relationship
contextual report reuse
multi-intent management synthesis
T1–T7 certification harness
metamorphic confidence
~~~

Forbidden:

~~~text
all frontend / UI / UX implementation
~~~

Reuse the existing `app/v3/product/contracts.py`, `projections.py`, and
`service.py` headless projection layer. Do not create another Product truth
authority.

## Phase 2 targeted panel

On one frozen Brain V2 candidate:

~~~text
T1 scope/conversation repair
T2 ONE_PASS RCA
T3 ADAPTIVE RCA
T4 DISCOVERY RCA
T5 observational relationship
T6 contextual evidence-backed report
T7 multi-intent management synthesis
~~~

Every case requires:

~~~text
mechanical verdict
+
manual Product quality 0–4
~~~

Readiness rules remain those in the execution directive.

## Permanent boundaries

~~~text
NO frontend before separate authorization
NO 30-case without explicit authorization
NO SQL/MBQL planner in Dima
NO second analytics engine
NO second Evidence authority
NO LangGraph checkpoint as business truth
NO regex/fuzzy/morphology semantic patch
NO benchmark-specific Product branch
NO prompt-only semantic patch as the durable authority
NO retry-until-lucky
NO provider-limit inflation
NO dima.9 / engine rebuild during current Phase 1
NO strategic growth of owner_adapter.py into a new monolith
~~~

When adding semantics, prefer:

~~~text
typed DTO
→ deterministic canonicalizer
→ coverage/invariant
→ owner-specific adapter
→ graph routing only
~~~

## Failure localization rule

For every failure identify the first wrong transition:

~~~text
Intent
?
Material contract
?
Metabot/native material
?
Evidence coverage
?
P18/P19 epistemics
?
P20 report
?
~~~

Fix the earliest wrong authority boundary. Do not patch the downstream symptom.

## Model policy

~~~text
default = Luna

Terra = one controlled same-candidate A/B only
        after mechanical GREEN + Luna manual <=2
        and no deterministic Product defect explains failure

Sol = reference ceiling only
      after Luna and Terra both prove insufficient

automatic cascade = NONE
~~~

## Exit authority

Return as complete only when:

~~~text
30-CASE READY
~~~

or a genuine STOP condition from the canonical directive is reached.

Final 30-case status must remain:

~~~text
NOT RUN
~~~

until the user separately authorizes it.
