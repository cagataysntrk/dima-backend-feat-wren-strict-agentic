# DIMA BRAIN V2 — FINAL CLOSURE STATUS

CURRENT GATE
G1

Platform HEAD
270e3a4c13ffdeb887fd20001de8179d7e7ead4e

semantic Product SHA
9de0cc6668689f2fc4fc303b7392043ee715049c
(telemetry-only commits after this SHA do not intentionally change Product semantics)

engine SHA/release
d5c60dc9f37a9ec9c5b0117f178146bbcb8dca88
0.63.18-dima.9
FROZEN
second build forbidden

WHAT CHANGED
- Added provider-free T3 DIMENSION_SCOPE family reproducer.
- Added structured material-boundary diagnostics.
- Propagated scope/material fingerprints and expected/observed semantic shapes through Research -> Brain V2 -> live receipt.
- No SQL/MBQL, prompt, regex, fuzzy, morphology, provider-ceiling or benchmark-specific logic added.

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
run: 36912454275
result: RED — diagnostic projection only; field-identity alias exposed entity_value as breakout label.
root: telemetry normalization, not Product/material acceptance.
fix: 270e3a4c13ffdeb887fd20001de8179d7e7ead4e
current rerun: PENDING

METAMORPHIC
result:
existing equality-filter / optional-time / unrelated-extra-breakout family retained;
G2 expansion pending after exact classification.

LIVE
run: 36909399128 (historical RED)
mechanical: RED / R1_NATIVE_DIMENSION_SCOPE_MISMATCH
manual: N/A

PROVIDER REQUESTS
historical T3 RED: 4 total
research_intake=1
metabase=3
p17=0
p19=0

TOKENS
historical T3 RED:
prompt=62148
completion=1789
reasoning=656

LATENCY
22778 ms

COST
$0.00884729

EXCEPTIONS
1 historical T3 exception at current frontier

DUPLICATE NATIVE
0 known

STALE EVIDENCE
0 known

KNOWN BLOCKERS
- exact T3 observed dimension shape must be captured before Product acceptance logic changes
- T3/T4/T5/T6/T7 not yet final-sealed

SEALED CAPABILITIES
T1 SCOPE RESUME = 36908273500 = GREEN = 4/4
T2 ONE_PASS = 36908926530 = GREEN = 4/4

NEXT EXACT ACTION
Rerun full current provider-free closure for G1 telemetry/reproducer on 270e3a4c.

If GREEN, freeze the diagnostic candidate and run exactly one fresh T3 ADAPTIVE live to classify the native dimension boundary with structured semantic shapes.
Do not patch acceptance until that classification exists.

90+ HIGH-CONFIDENCE READINESS
NO

30-CASE READY
NO

30-case
NOT RUN

frontend
NOT IMPLEMENTED
