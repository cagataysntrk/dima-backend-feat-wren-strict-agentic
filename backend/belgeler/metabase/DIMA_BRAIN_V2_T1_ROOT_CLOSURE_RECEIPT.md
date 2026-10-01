# DIMA BRAIN V2 — T1 ROOT CLOSURE RECEIPT

**Status:** SEALED — FULL 4/4  
**Date:** 2026-10-01  
**Branch:** `feat/dima-brain-v2`  
**Semantic Product:** `9de0cc6668689f2fc4fc303b7392043ee715049c`  
**Checkout trigger:** `055f298fedb4c3073638ddd28aa790ecf2efb233`  
**Provider-free authority:** `36907439396 = SUCCESS`  
**Live:** `36908273500 = SUCCESS`  
**Artifact:** `dima-brain-v2-live-R_LIVE_4_SCOPE_RESUME-36908273500`  
**Artifact digest:** `sha256:349d386d64873c3d33798c70b3b42dbd9f55df80ee8501dc17329600eeb5230f`

**Engine:** `d5c60dc9f37a9ec9c5b0117f178146bbcb8dca88 / 0.63.18-dima.9`  
**Engine digest:** `sha256:22c384198740274bbbba78fb6d41aa63a6d204dfe708b19a6ca9bc322b458ba7`  
**Second dima.9 build:** `0`

## Manual adjudication

```text
T1 scope/conversation repair = 4 / 4
```

Verified in the live artifact:

```text
scope_v1 -> scope_v2
same logical lineage
Assembly = exact current entity filter
period = 2026-05-01T00:00:00 -> 2026-07-01T00:00:00
prior Evidence != current Evidence
current Evidence is verified against scope_v2
checkpoint roundtrip = true
duplicate native execution = 0
blocked provider requests = 0
stale Evidence used as current = 0
P17 provider calls = 0
exception = 0
```

P19 no longer uses the historical broad objective as scope authority. The final assessment is
bound to the resolved scope fingerprint and does not emit the historical
`SCOPE_INCONSISTENT` limitation. Its remaining limitations are epistemic/causal limitations,
which are correct for the observed aggregate Evidence.

## Efficiency

```text
provider requests = 10
Research Intake    = 2
Metabot            = 6
P17                = 0
P19                = 2

native acquisitions = 2

prompt tokens       = 115,304
completion tokens   = 3,032
reasoning tokens    = 938
latency              = 44,895 ms
provider cost        = $0.01672515
```

Two native acquisitions are expected for this two-turn scope mutation: one for the original
accepted scope and one for the materially changed scope. No completed native work was duplicated.

## Root-closure architecture

Current scope transition authority is:

```text
FOLLOW_UP
-> typed TurnScopePatch
-> pure deterministic scope reducer
-> ResolvedScopeVersion + scope fingerprint
-> single material contract
-> native semantic observation
-> Evidence
-> P19/P20 current-scope projection
```

Absent facets inherit prior accepted scope. CLEAR is explicit. The provider does not own
mutation-kind classification.

## Seal law

T1 is frozen unless a new independent metamorphic/provider-free reproducer proves a generic
scope-transition defect.

No frontend work and no 30-case run are authorized by this receipt.
