# P6-001 — WREN VS METABASE STANDARD PARITY

**Milestone:** P6  
**Review:** `backend/belgeler/metabase/predev/P6_PREDEVELOPMENT_REVIEW.md`  
**Status:** AUTHORIZED AFTER PREDEV GOVERNANCE GREEN

## Goal

Complete a targeted post-authority same-intent substrate measurement on one physical PostgreSQL
snapshot. Broad risk-weighted cross-engine certification is deferred by DMP-DEC-0020 to integrated
Standard certification after the architecture is materially closer to final.

## Historical 80-case corpus plan — SUPERSEDED AS P6 EXIT GATE

```text
standard           30
time/comparison    10
ranking/top-N      10
filters/entity     10
join/relationship  10
error/edge         10
TOTAL              80
```

No raw prompt is a parity input.

## First blocker already classified

Existing Wren and Metabase live tests use different physical datasets.

`DATA/FIXTURE_GAP` must be closed by one shared PostgreSQL parity snapshot before numeric A/B.

## Hard invariants

```text
same authority/projection/intent             required
same access snapshot contract                required
same physical data snapshot                  required
raw-language reinterpretation                0
semantic search/label guessing               0
prompt-specific patches                      0
silent fallback                              0
unexplained mismatch                         0 at closure
production security issuer                   out of scope / P10
Wren retirement                              out of scope
```

## Exit artifact

A typed P6 parity report with per-case:
case id, family, frozen-input hashes, Wren outcome, Metabase outcome, parity dimensions,
latency, receipt completeness, status and optional typed gap classification.


## Execution order correction

```text
P6A0 shared-snapshot connectivity/golden proof = GREEN
  ↓
P6A1 true same-intent substrate-seam canary    = NEXT
  ↓
P6B/P6C broad parity corpus = DEFERRED BY DMP-DEC-0020
  ↓
P14-area integrated Standard certification
```

The shared-data assumption is proven before spending effort on the 80-case corpus.

Mismatch taxonomy additionally includes:
`RECEIPT/PROVENANCE_GAP` and `WREN_COMPATIBILITY_GAP`.

Wren legacy receipt behavior must be measured, not rewritten or wrapped in fake Metabase projection
objects to manufacture receipt parity.


## P6A1 observed capability gap

`DMP-P6-GAP-005`: current Wren compatibility adapter cannot represent
`ResolvedPeriod.kind="absolute"`.

P6 must report this as `TYPED_GAP / WREN_COMPATIBILITY_GAP`; `wren.py` remains forbidden.
The P6A1 harness is authorized to continue measuring CANARY-01/02 and record CANARY-03 as the exact
typed gap rather than aborting the entire instrument.


## Additional P6A1 runtime gap

`DMP-P6-GAP-006`: existing WrenService PostgreSQL timeout injection emits integer
`kwargs.connect_timeout`, while installed Wren `PostgresConnectionInfo` requires string.

Classification: `TYPED_GAP / SUBSTRATE_RUNTIME_GAP`.

P6 harness may recognize only this exact typed failure as a known gap. Any other Wren execution
exception remains `UNEXPLAINED_MISMATCH`/RED. Production WrenService is not patched in P6.


## DMP-DEC-0020 closure rule

P6 closes as a **targeted parity probe** when P6A0/P6A1 measurement is complete, every observed
difference is MATCH or an exact typed gap, and `UNEXPLAINED_MISMATCH = 0`.

This does not certify Wren/Metabase equivalence. Known runtime, temporal compatibility and
receipt/provenance gaps are carried forward to their real owners.
