# DIMA FAST TRACK — METABASE-NATIVE PRODUCT ROADMAP

Status: NORMATIVE BRANCH ROADMAP
Audit verdict: FEASIBLE_WITH_GATED_SCOPE

## 1. Tez

Bu yol:
- Wren-first değildir.
- DimaSemanticSpec-first değildir.
- Metabase frontend fork'u değildir.

Topoloji:

User
-> Dima Product Shell
-> Dima Fast Backend
-> Metabase Agent/REST boundary
-> Customer DB

Dima owns:
- conversation
- analyst orchestration
- bounded research
- evidence
- hypothesis state
- synthesis
- report
- decision
- UX

Metabase owns:
- connection/metadata
- query construction
- query execution
- permissions machinery
- saved questions
- dashboards
- collections
- optional embedded BI

## 2. Non-goals

İlk kritik yolda YOK:
- Wren runtime
- Wren MDL requirement
- DimaSemanticSpec compiler
- dual-engine parity
- custom query planner
- custom DB driver framework
- Metabase UI fork
- unrestricted native SQL
- arbitrary autonomous agent

## 3. Product modes

Quick:
question -> resource -> construct -> execute -> answer

Analyst:
baseline -> comparison -> selected breakdowns -> synthesis

Research/Root Cause:
target -> comparator -> candidate drivers -> breadth scans -> drill -> alternative hypotheses -> data-quality checks -> synthesis

All loops bounded.

## 4. Resource safety

Model raw Metabase IDs invent edemez.

user phrase
-> Agent search
-> CandidateResource[]
-> opaque fast_handle[]
-> SELECT(handle) | ABSTAIN
-> gateway validates
-> inspect/construct

Material ambiguity -> clarification.

## 5. Temporal safety

Relative time becomes typed TemporalIntent.
Exact dates backend computes deterministically.

Evidence stores:
- exact bounds
- timezone
- incomplete-period state
- comparison policy

## 6. Evidence Lite

Every user-visible numeric finding must reference >=1 evidence item.

Evidence stores:
- query fingerprint
- access fingerprint
- Metabase resource refs
- constructed query
- exact temporal bounds
- result digest
- bounded summary
- row count
- truncation state
- runtime version

Model rationale is not evidence.

## 7. Root cause constraints

Metric type:
ADDITIVE | SEMI_ADDITIVE | RATIO | DISTINCT_COUNT | NON_ADDITIVE | UNKNOWN

Only representable decompositions are allowed.

Special cases:
- total delta = 0
- offsetting contributors
- NULL spike
- incomplete period
- seasonality insufficient history
- high cardinality
- permission-blocked driver
- query failure
- stale resource

Data-quality risk is not silently converted to business cause.

## 8. Security

Internal alpha may use shared dev key only in isolated environment.

External pilot requires:
- per-user/principal mapping
- tenant isolation
- revocation tests
- permission denial
- cache isolation
- evidence/history current-viewer checks

Shared API key is not user identity.

## 9. Gateway

Single Fast Track Metabase Gateway owns:
- auth context
- search
- inspect
- construct
- execute
- pagination
- timeout/retry
- typed errors
- asset writes

Native SQL default OFF.

Observed Agent API page max: 200 rows; continuation must be explicit.

## 10. Run lifecycle

CREATED
RUNNING
WAITING_CLARIFICATION
PARTIAL
COMPLETED
FAILED
CANCEL_REQUESTED
CANCELLED
INTERRUPTED

Terminal state exactly once.

Same conversation: one active research run.

## 11. Gates

F0 — immutable branch + governance
F0A — pinned Metabase capability preflight
F1 — one question, one real answer
F1A — temporal/resource safety
F2 — conversation
F3 — evidence
F4 — analyst mode
F5 — root cause
F6 — dashboards/saved assets
F7 — decision + report
F8 — product polish
F9 — pilot security
F10 — frozen benchmark
F11 — pilot readiness
F12 — production candidate

No authority-changing gate is skipped.

## 12. Core tickets

FT-001 branch/governance
FT-002 capability + Metabase Gateway
FT-003 real Ask vertical slice
FT-004 streaming/run-state/cancel
FT-005 conversation
FT-006 Evidence Lite
FT-007 Analyst Mode
FT-008 Root Cause v1
FT-009 dashboards/assets
FT-010 decision
FT-011 report
FT-012 polish
FT-013 pilot security
FT-014 benchmark/failure injection/release rehearsal

## 13. Test pyramid

L0 governance/static
L1 unit
L2 contract
L3 live pinned Metabase
L4 model-in-loop focused
L5 frontend E2E
L6 security
L7 failure injection

Initial golden corpus: 150 scenarios
- DEV90
- VALIDATION30
- HOLDOUT30

Hard zero-tolerance:
- silent numeric wrong
- resource hallucination
- finding without evidence
- cross-tenant leak
- permission bypass
- silent fallback

## 14. Mandatory failure families

- no resource
- ambiguous resource
- permission denied
- Agent API disabled
- 200-row pagination
- empty vs zero
- incomplete period
- stale resource
- timeout / 5xx
- malformed model action
- repeated query/no-progress
- cancel race
- duplicate SSE
- duplicate asset write
- revoked permission after run
- backend restart
- app DB restore
- embed unavailable
- high-cardinality dimension
- ratio decomposition unsupported
- seasonality insufficient data
- missing principal in retry job

## 15. Fast Track escalation criteria

Escalate toward Dima semantic core if repeated pilot evidence shows:
- metric identity drift
- relationship ambiguity
- ratio/non-additive ceiling
- same business term binding drift
- Metabase catalog provenance insufficient
- multi-source semantic governance mandatory

Fast Track UX survives; semantic authority can be inserted later below it.

## 16. Definition of done

A user can:
1. connect/use a governed data source,
2. ask,
3. follow up,
4. request analysis,
5. ask why,
6. see bounded research,
7. inspect evidence,
8. save to dashboard,
9. record a decision,
10. produce a report,
11. return to history,

without silent fallback or hidden semantic substitution.
