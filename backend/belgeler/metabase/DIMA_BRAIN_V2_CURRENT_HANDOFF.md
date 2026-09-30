# DIMA BRAIN V2 — CURRENT HANDOFF

**Status:** ACTIVE — PHASE 1 ACCEPTANCE CLOSURE  
**Branch:** `feat/dima-brain-v2`  
**Decision:** DMP-DEC-0076  
**Roadmap:** `DIMA_BRAIN_V2_TWO_PHASE_ROADMAP.md`  
**Execution directive:** `DIMA BRAIN V2 — FINAL DEVELOPER EXECUTION DIRECTIVE`


## Current identities

~~~text
branch
feat/dima-brain-v2

current Platform HEAD
cf94c31a45dd11baa8532364f25763f4c9b8791a

current semantic Product
27adda56a5ed8369766bad879cf327511e1c5885

Product -> Platform proof
27adda56... -> cf94c31...
backend/app/** = ZERO DIFF
backend/pyproject.toml = ZERO DIFF
engine/metabase = ZERO DIFF

current provider-free authority
36771765176
SUCCESS

engine
0f16f2b5a1ec774ac7afee6214c726e82f9ceb3c
0.63.18-dima.8
FROZEN

engine builds during Brain V2
0
~~~

Read branch HEAD directly before every edit. Older embedded HEADs are historical only.

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

Latest completed ONE_PASS live before the current P19 interpretation fix:

~~~text
run
36770386638

candidate
733da230311240b8a0b782a3780c71c51cbef798

mechanical
GREEN

provider requests
7 total
1 Research Intake
5 Metabase/Metabot
0 P17
1 P19

native acquisitions
1

prompt / completion / reasoning
97,620 / 2,330 / 617

latency
~27.9 sec

provider reported cost
$0.01346711
~~~

Observed governed native result:

~~~text
Event Date Month | Machine Downtime | Maintenance Delay | Spare Part Delay
May 2026         | 291              | 8                 | 4
June 2026        | 365              | 13                | 6
~~~

Therefore the historical aggregate-material defect is CLOSED in this artifact:
two accepted periods are observable, all required candidate metrics are present, and native
acquisition cardinality remains one.

The remaining quality gap was downstream epistemic interpretation. Both candidate Evidence
groundings were CONTEXT, so P19 retained both candidates without useful discrimination. P19
correctly did not invent causality.

Current semantic Product after that live:

~~~text
27adda56a5ed8369766bad879cf327511e1c5885
~~~

It adds bounded assessment-local support/challenge refs and typed candidate
support/challenge interpretation.

Current full provider-free authority:

~~~text
36771765176
SUCCESS
~~~

Exact next action:

~~~text
ONE fresh R_LIVE_1_ONE_PASS
on semantic Product 27adda56...
then immediate disarm
then manual 0-4 adjudication
~~~

No same-candidate retry.


## Current root-cause diagnosis

Historical temporal-material root cause is CLOSED.

Current acceptance frontier:

~~~text
LangGraph routing/checkpoint = SEALED unless defect proven
dedup                       = SEALED unless defect proven
engine dima.8               = FROZEN
native acquisition count    = healthy for ONE_PASS
temporal material fidelity  = healthy in latest live
P19 Evidence interpretation = CURRENT ACCEPTANCE FRONTIER
ONE_PASS acceptance         = YELLOW
~~~

Do not reopen temporal/material architecture unless a new independent reproducer proves a
generic regression.


## Current fix family

Latest generic P19 interpretation family:

~~~text
21fe0a19  feat(p19): persist assessment-local support challenge refs
27adda56  feat(p19): type candidate support challenge interpretation
924b1643  test(p19): seal assessment-local evidence interpretation refs
94e53900  test(p19): close support challenge refs to candidate groundings
51ea0482  test(p19): preserve foreign-grounding ownership regression
cf94c31a  ci(brain-v2): revalidate P19 evidence interpretation
~~~

Provider-free closure:

~~~text
36771765176
GREEN
~~~

No further Product patch is authorized before the fresh live unless a provider-free
reproducer exposes a structural defect.

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
