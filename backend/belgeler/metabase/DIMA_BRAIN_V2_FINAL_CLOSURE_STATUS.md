# DIMA BRAIN V2 — FINAL CLOSURE STATUS

CURRENT GATE
G4

Platform HEAD
7e1c48531ff2c5833efccd66577ac232e4c9ef1c

semantic Product SHA
bf7dd7b0a39418471141327994ac3e2a773aa749

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
run: 36912879070
artifact: dima-brain-v2-live-R_LIVE_2_ADAPTIVE-36912879070
mechanical: GREEN
manual: 4/4 provisional pending G2/G3 shared material-seam closure

Manual basis:
- accepted user candidate identities preserved exactly
- initial aggregate Evidence was insufficient for discrimination
- exactly one typed P17 temporal-order re-entry
- follow-up Evidence materially changed from 1 aggregate row to 8 governed daily observations
- two native acquisitions total, no third acquisition
- P19 reassessed after new Evidence and terminated honestly
- both candidates remain observationally plausible; no causal direction or candidate discrimination fabricated
- P20 preserves limitations instead of inventing counter-Evidence

PROVIDER REQUESTS
T3 diagnostic GREEN: 8 total
research_intake=1
metabase=4
p17=1
p19=2

TOKENS
T3 diagnostic GREEN:
prompt=95913
completion=3618
reasoning=605

LATENCY
42838 ms

COST
$0.01892568

EXCEPTIONS
0 in run 36912879070

DUPLICATE NATIVE
0 known

STALE EVIDENCE
0 known

KNOWN BLOCKERS
- T3 4/4 run 36912879070 is provisional because G2/G3 changed shared adaptive material semantics after that run.
- Exactly one fresh T3 recertification is required on bf7dd7b0... with G3 PF 36914969117.
- T4/T5/T6/T7 final lives pending.

SEALED CAPABILITIES
T1 SCOPE RESUME = 36908273500 = GREEN = 4/4
T2 ONE_PASS = 36908926530 = GREEN = 4/4

NEXT EXACT ACTION
Freeze bf7dd7b0a39418471141327994ac3e2a773aa749 with G3 PF 36914969117.
Run exactly one fresh R_LIVE_2_ADAPTIVE recertification.
If mechanical GREEN and manual >=3, seal T3 and move immediately to G5 T4 DISCOVERY.
No same-candidate retry.

90+ HIGH-CONFIDENCE READINESS
NO

30-CASE READY
NO

30-case
NOT RUN

frontend
NOT IMPLEMENTED
