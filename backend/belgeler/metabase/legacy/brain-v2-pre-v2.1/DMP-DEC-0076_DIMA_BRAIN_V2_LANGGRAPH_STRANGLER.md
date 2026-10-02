# DMP-DEC-0076 — DIMA BRAIN V2 LANGGRAPH STRANGLER DECISION

**Date:** 2026-09-30  
**Status:** RATIFIED / FORWARD AUTHORITY  
**Branch:** feat/dima-brain-v2  
**Branch point:** 8d1e011053b01005179ff7a31b7921bb3a7307b9  
**Roadmap:** backend/belgeler/metabase/DIMA_BRAIN_V2_TWO_PHASE_ROADMAP.md  
**Roadmap creation commit:** 5bc7876adeeb6e39f052c90dfe4d501021d41dda

## Decision

The historical ~70.8 Product candidate is not restored as forward development baseline.

The current Metabase/Metabot + Dima domain state is preserved.

A parallel Brain V2 path is created from the current platform HEAD using LangGraph as the low-level orchestration/checkpoint runtime.

This is a strangler migration, not a big-bang rewrite.

## Preserved authorities

The following remain canonical Dima truth owners:

~~~text
ResearchBrief / ScopeVersion
DimaQueryReceipt
Evidence
current/historical lineage
P18 relationship semantics
P19 hypothesis/root-cause epistemics
P20 ReportDocument
Decision / Action / Outcome / Memory
tenant / principal / security
~~~

Metabase/Metabot remains the sole analytical engine/query-cognition owner.

## Replaced responsibility

The migration target is custom orchestration plumbing:

~~~text
next-owner routing
checkpoint/resume
workflow progress
bounded re-entry
minimum owner context
activity idempotency
cognition/native dedup
~~~

LangGraph may own orchestration progress only.

It must never become a second business/epistemic truth store.

## Legacy disposition

feat/dima-metabase-platform and the c5069e8 Product candidate remain historical/reference and fallback material.

No new strategic feature work should be added to the legacy custom orchestrator while Brain V2 spike is active, except a critical security/data-integrity fix required to preserve the reference baseline.

Rollback during migration means routing back to the legacy path.

Rollback does not mean reverting the repository to the historical 70.8 candidate.

## Current live evidence motivating the decision

Historical ONE_PASS custom orchestration:

~~~text
20 actual provider requests
16 Metabot/Metabase requests
289,626 prompt tokens
requirement_complete = false
~~~

Latest F10 live on current branch point:

~~~text
run 36729329926
artifact 11103899467
Product c5069e8e4606e21bdd8ce41f4c1dc4bf7d23c789

8 actual provider requests
5 Metabot/Metabase requests
2 Research Intake requests
1 P17 request
113,149 prompt tokens
~61s latency
$0.01726479

mechanical FAIL
INTAKE_SCOPE_MUTATION_INVALID
NARROW_ENTITY must only narrow entity values
~~~

The lower cost is progress, but the repeated appearance of independent state-transition seams is accepted as orchestration-complexity debt.

## Framework authority

LangGraph is authorized only as:

~~~text
state-machine runtime
routing runtime
checkpoint/resume runtime
bounded node execution framework
~~~

High-level generic agent abstractions do not own Dima Product semantics.

OpenHands, Letta and Temporal are pattern references only for V1.

No second workflow runtime is authorized.

## Engine

~~~text
engine SHA
0f16f2b5a1ec774ac7afee6214c726e82f9ceb3c

release
0.63.18-dima.8

status
FROZEN
~~~

Brain V2 Phase 1 is Platform-only.

No engine build is authorized by this decision.

## Model policy

~~~text
default = Luna

Terra = controlled same-candidate A/B only
        after deterministic architecture is GREEN
        and Luna quality is <= 2/4

Sol = reference ceiling only
      after Luna and Terra both prove insufficient

cascade = NONE
~~~

## Two phases

### Phase 1

LangGraph orchestration V2 spike/strangler.

Required certification modes:

~~~text
ONE_PASS
ADAPTIVE
DISCOVERY
scope mutation/resume
~~~

Phase-1 exit requires provider-free closure, no second truth authority, resume/idempotency proof, live manual quality >=3/4 for all three RCA modes, and material efficiency improvement over legacy.

### Phase 2

Thin Dima Brain Product/API + demo/UX layer.

Required final capability panel:

~~~text
scope repair
ONE_PASS RCA
ADAPTIVE RCA
DISCOVERY RCA
observational relationship
contextual report
multi-intent synthesis
~~~

The UX may display and request governed Brain state. It may not own analytics, Evidence, hypotheses, causality or business semantics.

## 90+ policy

Targeted live/manual tests may establish:

~~~text
80+ HIGH-CONFIDENCE READINESS
90+ HIGH-CONFIDENCE READINESS
~~~

They do not prove the final benchmark score.

The frozen 30-case benchmark remains forbidden until the user separately authorizes it.

Only a separately authorized final 30-case result >=90.0 may be called:

~~~text
90+ PROVEN
~~~

## Permanent forbidden patterns

~~~text
regex business semantics
fuzzy semantic matching
morphological patches
embedding-threshold truth
benchmark-specific logic
fixture-specific logic
retry-until-lucky
provider-limit inflation
Dima SQL/MBQL planner
second analytics engine
second Evidence authority
LangGraph checkpoint as business truth
~~~

## Licensing gate

LangGraph's low-level core is acceptable for this technical spike under its current MIT license.

Metabase distribution/embedding remains a separate release/commercial licensing gate because the OSS edition is AGPL and commercial embedding options also exist.

## Forward sequence

~~~text
feat/dima-brain-v2
→ Phase 1 LangGraph spike
→ provider-free characterization
→ ONE_PASS / ADAPTIVE / DISCOVERY live certification
→ V2 accepted
→ Phase 2 thin demo/UX
→ targeted capability panel
→ metamorphic confidence
→ 90+ high-confidence readiness
→ 30-case READY
→ STOP
→ explicit user authorization required
→ one frozen 30-case proof
~~~
