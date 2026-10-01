# DIMA BRAIN V2.1 — CURRENT HANDOFF

Status: ACTIVE  
Branch: feat/dima-brain-v2-1-convergence  
Decision: DMP-DEC-0077  
Roadmap: DIMA_BRAIN_V2_1_CONVERGENCE_ROADMAP.md

## Exact identities

~~~text
branch point
f910f705da5840b30ea776a85ff61aa545ced9f2

engine
d5c60dc9f37a9ec9c5b0117f178146bbcb8dca88
0.63.18-dima.9

engine state
FROZEN

additional engine builds
0 authorized
~~~

## Current first task

The source branch currently has one deterministic RED:

~~~text
report_document.py
NameError:
ResearchClaimRecord is not defined
~~~

Close this first.

No paid live is legal before the provider-free baseline is fully GREEN.

## Current architecture

~~~text
Metabase / Metabot
= single analytical cognition engine

LangGraph
= orchestration

Dima
= meaning / scope / material / Evidence / completion

P19
= epistemic judge

P18
= relationship judge

P20
= governed report

P17
= investigation controller / next-test only
~~~

## V2.1 primary change

Replace normal provider-backed DISCOVERY:

~~~text
Evidence
-> P17 provider candidate discovery
-> FORM_CLAIM
-> hypothesis sync
-> P19
~~~

with:

~~~text
Evidence
-> deterministic CandidateSetProjector
-> durable candidate hypotheses
-> P19
~~~

CandidateSetProjector may use only:

~~~text
accepted governed candidate vocabulary
current ScopeVersion
VERIFIED observed governed material
~~~

It may project identity and provenance only.

It may not calculate causal strength, correlation, probability or winner.

## Adaptive path

Do not remove adaptive P17 re-entry.

Current intended adaptive path remains:

~~~text
P19 identifies information gap
-> P17 designs/controls one bounded next test
-> Metabot
-> new Evidence
-> P19
~~~

Only simplify this later if an independent characterization proves a redundant provider call without reducing T3 quality.

Do not reopen accepted T3 merely for architectural elegance.

## Relationship audit

Do not blindly refactor T5.

First characterize whether a P17 provider call adds any new analytical/epistemic value after native relationship Evidence exists.

If no:

~~~text
Metabot relationship Evidence
-> P18
-> P20/Product
~~~

If yes:

keep the call until an owner-correct replacement is proven.

Never compute correlation/statistics inside Dima Product code.

## Quality engineering

Hypothesis already exists in backend optional test dependencies.

Expand RuleBasedStateMachine testing across:

~~~text
scope mutations
resume/checkpoint
historical/current
report-only
relationship
ONE_PASS
ADAPTIVE
DISCOVERY
repeated mutation
no-op mutation
next-test
honest-stop
~~~

Add OpenTelemetry tracing/events around Brain boundaries.

Do not record full prompts or hidden reasoning.

After headless API freeze, add Schemathesis stateful API testing.

No other runtime framework is authorized now.

## OSS boundary

Authorized now:

~~~text
Metabase/Metabot
LangGraph
Hypothesis
OpenTelemetry
~~~

After API freeze:

~~~text
Schemathesis
~~~

Future only:

~~~text
Temporal for Action/Watch/external durable work
DSPy offline optimization
OpenLineage/DataHub enterprise lineage
Cedar/OPA policy if later needed
~~~

Reference only:

~~~text
Wren
OpenHands
Letta
Cube
MetricFlow
~~~

## Hard prohibitions

~~~text
NO Metabase Agent API
NO raw SQL fallback
NO MCP analytical production fallback
NO second analytics engine
NO Dima SQL/MBQL/statistics planner
NO regex/fuzzy/morphology semantic authority
NO benchmark-specific branches
NO provider-limit inflation
NO retry-until-lucky
NO dima.10
NO engine rebuild
NO frontend/UI/UX
NO 30-case without explicit user authorization
~~~

## Development order

~~~text
1. close current P20 NameError
2. full provider-free GREEN
3. characterize candidate projection
4. implement CandidateSetProjector
5. route DISCOVERY directly to P19
6. prove P17 discovery provider calls = 0
7. discovery metamorphic closure
8. expand Hypothesis state-machine suite
9. add OpenTelemetry
10. relationship P17 value characterization
11. simplify relationship only if redundancy proven
12. close contextual P20
13. full provider-free + stateful + metamorphic freeze
14. fresh T4 live
15. fresh T6 live
16. fresh T5 only if relationship semantics changed
17. carry T1/T2/T3/T7 only with explicit non-affection proof
18. readiness calculation
19. declare 30-CASE READY if gates are earned
20. STOP
~~~

## Target

Preferred final panel:

~~~text
T1 Scope Repair                4/4
T2 ONE_PASS                    4/4
T3 ADAPTIVE                    4/4
T4 DISCOVERY                   4/4 target
T5 Relationship                4/4
T6 Report                      4/4
T7 Multi-intent                4/4
~~~

Do not fabricate certainty to make every case 4/4.

A data-identification-limited answer may honestly remain below FULL.

## Return condition

Return only when:

~~~text
30-CASE READY
~~~

or a genuine STOP condition in the V2.1 roadmap occurs.

Final handoff must include:

~~~text
final HEAD
final semantic Product SHA
engine identity
engine builds
CandidateSetProjector design
P17 discovery provider count
Dima native acquisition count
Metabot provider request count
P19 count
Hypothesis state-machine results
OpenTelemetry boundary map
T4/T5/T6 live receipts as applicable
manual scores
provider/tokens/cost/latency
known limitations
90+ HIGH-CONFIDENCE READINESS YES/NO
30-CASE READY YES/NO
30-case NOT RUN
frontend NOT IMPLEMENTED
~~~
