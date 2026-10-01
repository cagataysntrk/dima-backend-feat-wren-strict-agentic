# DIMA BRAIN V2 — FINAL CLOSURE STATUS

CURRENT GATE
G5 — T4 DISCOVERY candidate-vocabulary family closure

Platform HEAD
48d1abd8fc41c4b469badcbd2e53fb1543115165

semantic Product SHA
d6a8eddf46a6ec83f0339cf3368df4dbc87350cb

Proof:
d6a8eddf... -> 48d1abd8...
backend/app/** = ZERO DIFF

engine SHA/release
d5c60dc9f37a9ec9c5b0117f178146bbcb8dca88
0.63.18-dima.9
FROZEN
second build forbidden

WHAT CHANGED
- T1 SCOPE RESUME remains SEALED at 36908273500 = GREEN = 4/4.
- T2 ONE_PASS remains SEALED at 36908926530 = GREEN = 4/4.
- T3 ADAPTIVE remains SEALED at 36915701021 = GREEN = 4/4.
- T4 recertification 36918861962 produced three Evidence-linked P17 claims but all three normalized to the same governed mechanism identity metric.fault_count.
- Added a deterministic remaining-candidate vocabulary projection from durable current-scope P17 claim state.
- Each discovery turn now offers only governed mechanism refs not already represented by an admissible typed Evidence-linked candidate claim.
- Foreign obligation, historical scope, untyped and no-Evidence claims do not consume the current vocabulary.
- Provider output that escapes the remaining governed vocabulary fails closed.
- No prompt/regex/fuzzy/morph/benchmark-specific logic, no new analytics engine, no LangGraph semantic expansion.

ROOT CAUSE / INVARIANT
T4 live family:
repeated governed candidate identity across discovery turns.

Earliest invariant:
durable admitted candidate identity
must be removed from the next legal P17 discovery vocabulary.

Formally:
remaining_t = governed_candidates - admissible_current_scope_candidate_claims_t

P17 still owns candidate cognition.
Dima only projects the closed governed vocabulary from durable authority.

FIRST INVALID BOUNDARY
last_valid_boundary:
dima.p17.discovery.snapshot

first_invalid_boundary:
dima.p17.discovery.allowed_candidate_vocabulary

The old adapter re-opened the full governed candidate set on every discovery turn.

FILES CHANGED
- backend/app/v3/brain_v2/discovery_candidate_design.py
- backend/app/v3/brain_v2/owner_adapter.py
- backend/tests/test_v3_brain_v2_owner_integration.py
- backend/tests/test_v3_brain_v2_discovery_candidate_design.py
- backend/belgeler/metabase/DIMA_BRAIN_V2_FINAL_CLOSURE_STATUS.md

PROVIDER-FREE
exact reproducer:
36919863363 = RED
1 failed / 26 passed / 1 skipped
failure = repeated candidate family remained INCONCLUSIVE

focused fix:
36920356170 = GREEN

metamorphic sibling closure:
36920558912 = GREEN

full Phase-1 closure:
PENDING — triggered by this status commit

METAMORPHIC
result:
focused GREEN

covered:
1 durable current-scope typed Evidence-linked candidate -> consumed
2 foreign obligation claim -> not consumed
3 historical lineage/scope claim -> not consumed
4 untyped claim -> not consumed
5 no-Evidence claim -> not consumed
6 governed order/dedup preserved
7 existing honest-stop discovery path remains covered by owner integration suite

LIVE
latest T4:
run: 36918861962
artifact: dima-brain-v2-live-R_LIVE_3_DISCOVERY-36918861962
artifact id: 11190972486
artifact digest: sha256:322c450a58aacdaa2a4a2036f412ac9b0068333b7c15e7bf0f72030bdd6cbc4d
mechanical: RED
manual: NOT SCORED — mechanical terminal contract failed
candidate: 3b8f3c44d3a23a41f2ce55b9b8031f3a3d024e4a

Observed:
- one initial native acquisition
- governed Evidence present
- 3 P17 claims
- 1 unique hypothesis identity
- P19 assessment absent
- no duplicate native execution
- no blocked provider request
- exception = 0

PROVIDER REQUESTS
latest T4:
7 total
research_intake=1
metabase=3
p17=3
p19=0

TOKENS
latest T4:
prompt=87006
completion=5224
reasoning=539

LATENCY
53238 ms

COST
$0.01611813

EXCEPTIONS
0 in 36918861962

DUPLICATE NATIVE
0 known

STALE EVIDENCE
0 known

KNOWN BLOCKERS
- Full Phase-1 provider-free closure for semantic Product d6a8eddf... is pending.
- No paid T4 retry is authorized until that full closure is GREEN.
- T5 RELATIONSHIP fresh proof pending.
- T6 CONTEXTUAL REPORT fresh proof pending.
- T7 MULTI-INTENT fresh proof pending.

SEALED CAPABILITIES
T1 SCOPE RESUME = 36908273500 = GREEN = 4/4
T2 ONE_PASS = 36908926530 = GREEN = 4/4
T3 ADAPTIVE = 36915701021 = GREEN = 4/4

NEXT EXACT ACTION
1. Complete one full current-head Phase-1 provider-free closure.
2. If GREEN, freeze semantic Product d6a8eddf...
3. Arm exactly one fresh R_LIVE_3_DISCOVERY.
4. Disarm immediately after trigger.
5. Manually adjudicate actual artifact.
6. If accepted, seal T4 and move to T5/T6.

90+ HIGH-CONFIDENCE READINESS
NO

30-CASE READY
NO

30-case
NOT RUN

frontend
NOT IMPLEMENTED
