# DIMA BRAIN V2 — FINAL CLOSURE STATUS

CURRENT GATE
G5

Platform HEAD
8f2fabf63f1a803981632079dfb60d8f4abcc16a

semantic Product SHA
3b8f3c44d3a23a41f2ce55b9b8031f3a3d024e4a

Proof:
bf7dd7b0... -> 6e5430df...
backend/app/** = ZERO DIFF

engine SHA/release
d5c60dc9f37a9ec9c5b0117f178146bbcb8dca88
0.63.18-dima.9
FROZEN
second build forbidden

WHAT CHANGED
- G1 boundary telemetry is provider-free GREEN.
- T3 diagnostic live 36912879070 is mechanical GREEN and provisional manual 4/4.
- Added deterministic MaterialCoverageContract projection over existing AnalyticalRequestContract.
- Native metric/dimension validation now consumes explicit required/allowed material algebra without changing user scope authority.
- Added typed ChildMaterialDelta for ADAPTIVE; governed semantic universe is explicit.
- Adaptive re-entry keeps scope fingerprint unchanged while material fingerprint changes.
- No SQL/MBQL, prompt, regex/fuzzy/morph, new truth store, engine change, or owner_adapter domain expansion.

ROOT CAUSE / INVARIANT
Current live family: R1_NATIVE_DIMENSION_SCOPE_MISMATCH.
Invariant under test:
required_breakouts ⊆ observed_breakouts ⊆ allowed_breakouts.
Accepted equality-filter fields may be redundant breakouts; unrelated breakouts remain RED.
Old live artifact did not retain observed semantic shape, so A/B/C/D classification is not yet asserted as fact.

FIRST INVALID BOUNDARY
Expected from the family:
dima.material.compile -> dima.native.observe
Exact semantic shape from the old live is unavailable by design; new boundary receipt closes this diagnostic gap.

FILES CHANGED
- backend/tests/test_v3_p14_native_gateway.py
- backend/app/v3/research_analytical_scope.py
- backend/app/v3/research_product.py
- backend/app/v3/research_native_gateway.py
- backend/app/v3/brain_v2/owner_adapter.py
- backend/lab/metabase/brain_v2/phase1_live.py
- backend/belgeler/metabase/DIMA_BRAIN_V2_FINAL_CLOSURE_STATUS.md

PROVIDER-FREE
G1 run: 36912627188 = GREEN
G2 run: 36914380205 = GREEN
G3 full run: 36914969117 = GREEN

METAMORPHIC
result: GREEN in G3 full workflow 36914969117
covered family:
1 required diagnostic breakout present -> GREEN
2 required diagnostic breakout missing -> RED
3 fixed equality dimension repeated as breakout -> GREEN
4 accepted temporal grain breakout -> GREEN where allowed
5 governed P17 child breakout -> GREEN
6 unknown child semantic ref -> RED
7 unrelated native breakout -> RED
8 same scope + child material -> same scope_fp / different material_fp
9 duplicate material fingerprint -> effectively once
10 same result hash -> BRAIN_V2_NEXT_TEST_NO_INFORMATION_GAIN; no P19 reassess
Hypothesis analytical-material state-machine added with production material/delta projectors.

LIVE
T3 final recertification:
run: 36915701021
artifact: dima-brain-v2-live-R_LIVE_2_ADAPTIVE-36915701021
artifact id: 11189563441
artifact digest: sha256:7f0bb6773368c5fea0837a3123c8a680bca8b1a1b91eba6f29bc4e60e5d8862d
mechanical: GREEN
manual: 4/4
candidate: bf7dd7b0a39418471141327994ac3e2a773aa749

Manual basis:
- accepted user candidate identities preserved exactly
- initial aggregate Evidence was insufficient for discrimination
- exactly one typed P17 adaptive child material re-entry
- follow-up Evidence changed from 1 aggregate row to 8 governed daily observations
- evidence revision advanced before P19 reassessment
- two native acquisitions total; no third acquisition
- P19 retained both candidates as observationally plausible and did not invent causal direction
- P20 carried limitations forward without fabricated challenge/counter-Evidence
- duplicate native = 0
- stale Evidence = 0
- exception = 0

PROVIDER REQUESTS
T3 final: 8 total
research_intake=1
metabase=4
p17=1
p19=2

TOKENS
T3 final:
prompt=91635
completion=3170
reasoning=483

LATENCY
37286 ms

COST
$0.0173724

EXCEPTIONS
0 in run 36915701021

DUPLICATE NATIVE
0 known

STALE EVIDENCE
0 known

KNOWN BLOCKERS
- T4 DISCOVERY live 36916272244 = RED.
- error = P17_DOWNSTREAM_REENTRY_INTENT_MISMATCH.
- first wrong transition: Brain V2 discovery adapter authorizes {FORM_CLAIM, STOP_INVESTIGATION} to P17, then pins run_one downstream result to FORM_CLAIM only.
- STOP_INVESTIGATION is already a legal P17 global-control terminal intent; graph already routes discovery terminal without hypotheses to HONEST_STOP.
- exact provider-free reproducer commit fdd0d412... failed only the new honest-stop case: 1 failed / 25 passed / 1 skipped.
- typed allowed-outcome fix: 8c792990... + 3b8f3c44...
- focused Brain V2 PF 36917795650 = GREEN with both FORM_CLAIM and honest STOP discovery siblings.
- full Phase-1 PF 36917925669 = GREEN across Brain V2, Research/Scope, P17, P19, P20, security and hygiene.
- T4 mechanical contract now separates structural mechanics from Product quality: governed candidate path OR typed honest insufficient terminal.
- harness tests at 9c884d8c... = provider-free GREEN in 36918446124.
- Product freeze = 3b8f3c44d3a23a41f2ce55b9b8031f3a3d024e4a; later status/CI-only commit has backend/app/** zero diff.
- T5 RELATIONSHIP fresh live pending.
- T6 CONTEXTUAL REPORT fresh live pending.
- T7 MULTI-INTENT fresh live pending.

SEALED CAPABILITIES
T1 SCOPE RESUME = 36908273500 = GREEN = 4/4
T2 ONE_PASS = 36908926530 = GREEN = 4/4
T3 ADAPTIVE = 36915701021 = GREEN = 4/4

NEXT EXACT ACTION
Run one current-head full Phase-1 provider-free closure after T4 harness correction.
If GREEN, preserve semantic Product 3b8f3c44... and use that new PF run as T4 live authority.
Then run exactly one fresh R_LIVE_3_DISCOVERY.
Manual Product score remains separate from mechanical outcome.

90+ HIGH-CONFIDENCE READINESS
NO

30-CASE READY
NO

30-case
NOT RUN

frontend
NOT IMPLEMENTED
