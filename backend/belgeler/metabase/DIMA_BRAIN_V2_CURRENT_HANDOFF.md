# DIMA BRAIN V2 — CURRENT HANDOFF

**Status:** ACTIVE  
**Branch:** feat/dima-brain-v2  
**Decision:** DMP-DEC-0076  
**Roadmap:** DIMA_BRAIN_V2_TWO_PHASE_ROADMAP.md

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
~~~

## Current decision

Do not return to the historical 70.8 candidate.

Do not continue strategic feature development inside the legacy custom orchestrator.

Preserve the current Dima domain authorities and Metabase/Metabot integration.

Build Brain V2 as a strangler path over the current state.

~~~text
Metabase / Metabot = analytics
LangGraph          = orchestration/checkpoint
Dima DB            = canonical truth
Thin Dima Brain    = semantics/evidence/epistemics/decision
UX                 = governed projection
~~~

## Phase 1 immediate implementation order

1. add the low-level LangGraph dependency and exact lock;
2. create backend/app/v3/brain_v2 package;
3. define BrainGraphState containing IDs/revisions, not duplicate truth bodies;
4. add owner-specific StateView projections;
5. add EvidenceDigest projection;
6. add CognitionRequestKey and NativeMaterialRequestKey;
7. wrap current Intake, Metabot/P14, Evidence, P19, P17 and P20 owners as graph activities/nodes;
8. build ONE_PASS path first;
9. prove checkpoint/resume and idempotent provider/native reuse;
10. add ADAPTIVE path;
11. add DISCOVERY path;
12. add one multi-turn scope-repair/resume path;
13. run provider-free legacy-vs-V2 replay;
14. freeze one V2 candidate;
15. run Luna ONE_PASS / ADAPTIVE / DISCOVERY live certification;
16. accept/reject V2 against the Phase-1 roadmap gate.

Do not migrate P18, Action, Watch or full Decision Desk before Phase-1 graph acceptance unless an acceptance case genuinely requires them.

## Phase 2 immediate implementation order

After V2 acceptance:

1. expose thin Brain V2 Product API;
2. expose bounded progress/event stream;
3. expose current scope, Evidence, hypotheses, limitations and reports;
4. build Ask demo surface;
5. build Investigation surface;
6. build Evidence drawer;
7. build Report / Decision surface;
8. build visible multi-turn scope-repair flow;
9. certify the seven final targeted capability cases;
10. run independent metamorphic confidence cases;
11. freeze candidate;
12. declare 80+/90+ readiness only if thresholds are earned;
13. declare 30-CASE READY;
14. STOP.

The 30-case benchmark remains forbidden until the user separately authorizes it.

## Permanent boundaries

~~~text
NO SQL/MBQL planner in Dima
NO second analytics engine
NO second Evidence authority
NO LangGraph checkpoint as business truth
NO regex/fuzzy/morphology semantic patch
NO benchmark-specific Product branch
NO retry-until-lucky
NO provider-limit inflation
NO engine rebuild during Brain V2 Phase 1
~~~

## Model policy

~~~text
default = Luna

Terra = one controlled A/B only
        after clean architecture + Luna quality <=2

Sol = reference ceiling only
      after Luna and Terra both prove insufficient

cascade = NONE
~~~

## Live/reference receipts

Historical orchestration cost reference:

~~~text
R_LIVE_1_ONE_PASS
36694760361
20 provider requests
16 Metabot/Metabase
289,626 prompt tokens
~~~

Latest legacy scope-repair reference:

~~~text
CONVERSATION_F10_H_RECOVERY
36729329926
artifact 11103899467
Product c5069e8...

8 provider requests
113,149 prompt tokens
~61s
$0.01726479

RED:
INTAKE_SCOPE_MUTATION_INVALID
NARROW_ENTITY must only narrow entity values
~~~

These are immutable baselines for V2 comparison, not bugs to keep patching on the legacy path.

## Exit

The next developer should return only when:

~~~text
PHASE 1 LANGGRAPH V2 ACCEPTED
~~~

or an explicit Phase-1 STOP condition from the canonical roadmap is reached.

After Phase 1 acceptance, continue directly into Phase 2 unless the user/supervisor changes authority.
