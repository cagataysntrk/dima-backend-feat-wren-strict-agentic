# M1-P1-001 — ENGINE-INDEPENDENT CORE + WREN COMPATIBILITY SUBSTRATE

**Milestone:** M1 / P1  
**Predevelopment review:** `backend/belgeler/metabase/predev/M1_P1_PREDEVELOPMENT_REVIEW.md` @ `67a1ded2a228855322116508c87047337f7a5a7b`  
**Owner:** v3 core contract boundary  
**Status:** AUTHORIZED / IMPLEMENTATION OPEN

## Goal

Create the engine-independent Dima contract boundary without changing the existing v2 product path.
Resolve semantic handles in the Dima plane exactly once, then execute the resulting
`ResolvedAnalyticsIntent` through a Wren substrate adapter with zero behavioral drift.

## Source evidence

```text
certified base             3774484167f1056d89da0e0609246fb4a05057ec
provider-free baseline     35718675540 = 25/25 PASS
real Wren baseline         35718883950 = 2/2 PASS
M1 predev governance       35727494650 = SUCCESS
ask-v2 source HEAD read    4ad8238c4fe8ada02a8a1a79e0682606a6fbfe1a (READ ONLY)
```

## Files to touch

```text
backend/app/v3/**
backend/tests/test_v3_m1_*.py
.github/workflows/dima-metabase-m1.yml
DIMA-METABASE-DURUM.md
backend/belgeler/metabase/tickets/M1_P1_ENGINE_INDEPENDENT_CORE.md
backend/belgeler/metabase/*RECEIPTS*.md   # only if RED/decision requires
```

## Files not to touch

```text
backend/app/v2/**
backend/app/routers/ask_v2.py
backend/app/main.py
backend/app/config.py
WrenAI-main/**
feat/ask-v2-mvp
```

## Invariants

```text
v2 behavior change                         = 0
source-branch write                        = 0
second Research authority model           = 0
same-turn Standard+Research authority      = 0
material semantic-surface silent loss      = 0
semantic resolution inside substrate       = 0
raw language inside substrate              = 0
Wren query/result drift                    = 0
Metabase runtime dependency                = 0
```

## Planned modules

```text
app/v3/semantic_spec.py
app/v3/authority.py
app/v3/analytics_contract.py
app/v3/evidence.py
app/v3/substrate/base.py
app/v3/substrate/wren.py
```

## Exit gate

- v3 contract tests GREEN;
- v3 Wren parity test GREEN;
- retained v2 real-Wren sentinels GREEN;
- governance GREEN;
- no forbidden file modified;
- living status records exact SHA/run IDs.

## Open debt after M1

Metabase lab/client/bridge remains CLOSED until M2/M3/P3A.
DimaSemanticSpec importer and full semantic equivalence remain P7/P8.
