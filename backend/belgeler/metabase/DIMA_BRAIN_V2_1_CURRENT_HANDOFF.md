# DIMA BRAIN V2.1 — CURRENT HANDOFF

> **Status:** CURRENT OPERATIONAL AUTHORITY  
> **Architecture:** FROZEN  
> **Branch:** `feat/dima-brain-v2-1-discovery-simplification`  
> **Documentation consolidation source HEAD:** `ed95d22a3dee4c3e3cac8932ebd3050a6c0d691e`  
> **Final semantic Product SHA:** `ce8704d6a0db10dc3fb6b1a7e5d0f86afe9ccdc9`  
> **Engine:** `d5c60dc9f37a9ec9c5b0117f178146bbcb8dca88` / `0.63.18-dima.9`  
> **Engine digest:** `sha256:22c384198740274bbbba78fb6d41aa63a6d204dfe708b19a6ca9bc322b458ba7`  
> **Engine builds in V2.1:** `0`

This handoff contains only the current closure state. Historical handoffs, roadmaps, REDs and
intermediate certification receipts are archived under `legacy/`.

---

## 1. Current decision — ROUND-2 30-CASE COMPLETED

The former pre-benchmark readiness claim is superseded by the actual broad benchmark.

Canonical adjudication:

`DIMA_BRAIN_V2_1_ROUND2_FINAL_ADJUDICATION_2026-10-02.md`

~~~text
BRAIN V2.1 ARCHITECTURE FROZEN

ROUND-2 30-CASE
COMPLETED

complete run
37027548693

artifact
11235884317

artifact digest
sha256:095d1593ceace7dba94ae872e7ad85f520a3d2b4f4d7de603cfe1f22e4a352f1

FINAL PRODUCT QUALITY SCORE
60.5 / 100

90+ PROVEN
NO

80+ PROVEN
NO

former 90+ HIGH-CONFIDENCE READINESS
INVALIDATED BY BROAD EVIDENCE

broad paid authorization
CLOSED

frontend
NOT IMPLEMENTED / NOT AUTHORIZED
~~~

The Product and engine remained frozen for the final complete benchmark:

~~~text
Product
ce8704d6a0db10dc3fb6b1a7e5d0f86afe9ccdc9

engine
d5c60dc9f37a9ec9c5b0117f178146bbcb8dca88
0.63.18-dima.9

model topology
Luna / Luna / no cascade
~~~

The complete run proves a strong speed/cost improvement but insufficient broad quality:

~~~text
30-case case-latency total = 648.852 s
median                    = 19.560 s
p90                       = 49.952 s

provider requests          = 137
prompt tokens              = 1,925,857
provider-reported cost     = $0.24909254
average cost / case        = $0.00830308
~~~

The first benchmark attempt `37027114003` completed only F01_S before a harness-only
model-budget validation defect aborted the run. It spent 3 provider requests / $0.00713981.
The semantic Product and engine were unchanged; the final quality score uses only the complete
run `37027548693`. Total campaign provider cost including that aborted harness attempt is
`$0.25623235`.

Do not rerun the broad benchmark on the same candidate. The next work is generic
provider-free recovery of the broad failure families, followed by targeted proofs. A later
30-case requires new explicit user authorization.

Any semantic Product change after `ce8704d6...` creates a new candidate and invalidates
affected carry-forward evidence.

---

## 2. Final permanent runtime

~~~text
Metabase / Metabot
= single analytical cognition engine

BrainV2Service / LangGraph
= single forward orchestrator

Dima
= intent / scope / material / Evidence / provenance / completion

CandidateSetProjector
= governed candidate identity only

P18
= relationship epistemic owner

P19
= RCA epistemic owner

P17
= typed NextTest / information-gain controller only

P20
= governed synthesis from terminal state
~~~

Final runtime hard gates:

~~~text
Agent API calls = 0
legacy final calls = 0
normal Discovery P17 provider = 0
normal observational Relationship P17 provider = 0
~~~

---

## 3. Final normal paths

### Discovery

~~~text
Metabot
-> VERIFIED Evidence
-> CandidateSetProjector
-> P19
~~~

P17 normal discovery calls = 0.

### Adaptive RCA

~~~text
P19 identifies exact information gap
-> typed NextTestRequest
-> P17 bounded controller
-> Metabot
-> new VERIFIED Evidence
-> P19 reassessment
~~~

### Observational relationship

~~~text
Metabot
-> VERIFIED Evidence
-> bounded P18 interpretation
-> immutable RelationshipResult
-> Completion
-> P20 if presentation required
~~~

P17 relationship calls = 0.

### Presentation-only

~~~text
existing governed terminal state
-> P20
~~~

Research/Scope/native/P17/P18/P19 analytical delta = 0.

### Multi-intent

~~~text
multiple USER_MUST requirements
-> deterministic requirement dispatch
-> compatible requirements may share MaterialGroup
-> one governed Evidence packet with explicit consumers
-> each requirement terminates through its own owner
-> Completion Ledger
-> P20
~~~

Shared material never implies shared fulfillment.

---

## 4. Final capability panel

| Capability | Fresh run | Mechanical | Manual | Main proof |
|---|---:|---|---:|---|
| T1 Scope / Resume | 37002719189 | GREEN | 4/4 | one lineage, scope mutation, historical/current Evidence, resume |
| T2 ONE_PASS | 37003097196 | GREEN | 4/4 | bounded RCA, no redundant re-entry |
| T3 ADAPTIVE | 37003440451 | GREEN | 4/4 | exactly one typed high-information NextTest |
| T4 DISCOVERY | 37003830042 | GREEN | 3/4 | governed projected candidates, P17 discovery = 0 |
| T5 Relationship | 37017824173 | GREEN | 4/4 | P18-owned cross-sectional relationship, P17 = 0 |
| T6 Contextual Report | 37017824173 | GREEN | 4/4 | report-only analytical delta = 0 |
| T7 Multi-intent | 37019171940 | GREEN | 3/4 | shared MaterialGroup, distinct owners, all MUST terminal |

Manual panel:

~~~text
total = 26 / 28
average = 3.71 / 4
FULL 4/4 = 5 / 7
~~~

T4 is 3/4 because differentiation remains broad rather than FULL.
T7 is 3/4 because the ranking narrative is less explicit than FULL management synthesis.

These are known Product-quality ceilings, not unresolved architecture families.

---

## 5. Final provider-free/stateful/metamorphic seal

~~~text
Phase-1 provider-free
37020220583 = GREEN

Phase-2/headless + metamorphic
37020220833 = GREEN
~~~

Hypothesis floors:

~~~text
Material/state reducer      1000 examples x 24 steps
Scope patch reducer         1000 examples x 30 steps
Discovery lifecycle          200 examples x 30 steps
P18 relationship owner       200 examples x 12 steps
Completion owner             200 examples x 12 steps
~~~

Metamorphic coverage includes at least two executable variants for:

- scope/currentness;
- ONE_PASS RCA;
- ADAPTIVE;
- relationship;
- reporting;
- multi-intent;
- alternate RCA family.

Do not reduce these floors to make CI pass.

---

## 6. Final zero-violation receipt

~~~text
exception = 0
silent wrong = 0
security violation = 0
cross-tenant violation = 0
unsupported causal promotion = 0
duplicate native = 0
stale Evidence = 0
hidden MUST = 0
Agent API calls = 0
legacy final calls = 0
normal Discovery P17 provider = 0
normal observational Relationship P17 provider = 0
unresolved architecture family = 0
~~~

T7 additionally proves:

~~~text
one shared MaterialGroup
one native acquisition
P18 exactly once
P20 terminal report
all USER_MUST terminal
requirement_complete = true
checkpoint roundtrip = true
~~~

---

## 7. Provenance closure

Exact relationship magnitudes shown to managers are not arbitrary model coordinates.

Final path:

~~~text
current VERIFIED Evidence
-> deterministic closed legal EvidenceCellRef set
-> P18 may select only a legal ref
-> selected ref resolves to exact current Evidence/receipt/result
-> P20 verifies provenance before rendering
~~~

Forbidden:

- stale Evidence cell;
- cross-scope cell;
- invented row/column coordinate;
- model-generated numeric value not present in governed Evidence;
- hidden statistic computed inside P18/P20.

---

## 8. Engine status

~~~text
engine SHA
d5c60dc9f37a9ec9c5b0117f178146bbcb8dca88

release
0.63.18-dima.9

digest
sha256:22c384198740274bbbba78fb6d41aa63a6d204dfe708b19a6ca9bc322b458ba7

V2.1 engine builds
0
~~~

Do not create a new engine build for a Product-owned defect.

---

## 9. UX transition status

The backend is **contract-ready for UX**, not frontend-complete.

Stable Product primitives exist for:

- Ask / governed answer;
- Scope controls;
- durable Investigation / RCA;
- Candidate/P19 state;
- RelationshipResult;
- Evidence/provenance drawer;
- contextual ReportDocument;
- multi-intent completion status;
- checkpoint/resume/history.

Frontend must project canonical backend authority.
It must not reconstruct or own alternate business truth.

Still not implemented:

~~~text
frontend
web UI
Ask screen
Investigation screen
Evidence Drawer
Report/Decision UI
dashboard integration
demo frontend
visual Product layer
~~~

---

## 10. What the next developer must not do

Do not:

- create Brain V3;
- restore Wren execution;
- add a second analytics engine;
- restore Agent API;
- route normal discovery to P17 provider;
- route normal observational relationship to P17 provider;
- add SQL/MBQL planning inside Dima;
- duplicate canonical domain stores into graph state;
- use fuzzy/regex/morph/prompt keyword semantic routing;
- patch benchmark wording;
- increase provider ceilings as a correctness fix;
- retry the same paid SHA hoping for luck;
- reduce stateful floors;
- weaken security/currentness/P14/P18/P19 invariants;
- start frontend because backend is “ready.”

---

## 11. Development method

For every new RED:

~~~text
RED
-> first invalid boundary
-> exact owner
-> generic invariant
-> provider-free reproducer
-> stateful/metamorphic siblings
-> one generic root fix
-> affected PF
-> wider PF
-> freeze one semantic candidate
-> one fresh surgical live proof
-> receipt / handoff update
~~~

Read `DIMA_BRAIN_V2_1_ENGINEERING_PLAYBOOK.md` before modifying Product code.

---

## 12. Next legal action

The frozen broad benchmark has now run and is sealed.

Next action:

~~~text
BROAD 30-CASE RECOVERY
= GENERIC FAILURE-FAMILY CLOSURE ONLY
~~~

Required order:

1. preserve run `37027548693` and artifact `11235884317` as immutable benchmark authority;
2. do not rerun the 30-case on the same candidate;
3. reproduce the broad failure families provider-free;
4. close ranking-admission, completion/sealing, adaptive-material, causal-temporal and scope-repair invariants generically;
5. add stateful/metamorphic siblings before any live proof;
6. use only targeted paid probes when they generate new information;
7. freeze a new semantic Product candidate only after provider-free closure;
8. reassess readiness from the generic fixes;
9. request new explicit user authorization before any future broad 30-case.

Current status:

~~~text
30-case = COMPLETED
final score = 60.5 / 100
broad authorization = CLOSED
frontend = NOT IMPLEMENTED / NOT AUTHORIZED
architecture = FROZEN
~~~

---

## 13. New developer reading order

~~~text
1. backend/belgeler/metabase/README.md
2. DIMA_BRAIN_V2_1_FINAL_ARCHITECTURE.md
3. DIMA_BRAIN_V2_1_ENGINEERING_PLAYBOOK.md
4. DIMA_BRAIN_V2_1_CURRENT_HANDOFF.md
5. DIMA_BRAIN_V2_1_FORWARD_RUNTIME_LAWS.md
~~~

Do not begin from `legacy/`.

Historical material is available for forensic context only.
