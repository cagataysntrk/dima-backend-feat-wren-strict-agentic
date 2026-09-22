# P6-001 — WREN VS METABASE STANDARD PARITY

**Milestone:** P6  
**Review:** `backend/belgeler/metabase/predev/P6_PREDEVELOPMENT_REVIEW.md`  
**Status:** AUTHORIZED AFTER PREDEV GOVERNANCE GREEN

## Goal

Run an 80-case frozen post-authority Standard corpus against Wren and Metabase with identical intent,
access contract and physical PostgreSQL snapshot.

## Corpus

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
P6B  deterministic 80-case corpus freeze
  ↓
P6C  full parity harness
```

The shared-data assumption is proven before spending effort on the 80-case corpus.

Mismatch taxonomy additionally includes:
`RECEIPT/PROVENANCE_GAP` and `WREN_COMPATIBILITY_GAP`.

Wren legacy receipt behavior must be measured, not rewritten or wrapped in fake Metabase projection
objects to manufacture receipt parity.
