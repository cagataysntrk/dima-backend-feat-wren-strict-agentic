# DIMA + METABASE — LIVING STATUS

**Branch:** `feat/dima-metabase-platform`  
**Source branch:** `feat/ask-v2-mvp` — READ ONLY  
**Base certified SHA:** `3774484167f1056d89da0e0609246fb4a05057ec`  
**Current phase:** P0 / M0 — branch + baseline + source lock + governance bootstrap  
**Product-code development:** NOT STARTED  
**Metabase runtime:** NOT SELECTED  
**Production routing:** UNCHANGED / NOT CONNECTED

## Completed

- [x] Source branch inspected without writes.
- [x] Moving source HEAD rejected as base after full-live RED evidence.
- [x] Immutable certified source SHA selected: `3774484167f1056d89da0e0609246fb4a05057ec`.
- [x] New isolated branch created: `feat/dima-metabase-platform`.
- [x] User-approved final architecture report mirrored and sealed.
- [x] User-approved final roadmap mirrored and sealed.
- [x] Source-lock policy established.
- [x] Operation / audit / receipt system established.
- [x] Governance CI added for this branch only.

## Baseline evidence

```text
focused/provider-free       35718675540 = 25/25 PASS, compile PASS
real Wren sentinels         35718883950 = 2/2 PASS @ 3774484167f1056d89da0e0609246fb4a05057ec
moving-head full-live       35724830736 = FAILURE @ 4ad8238...
ask-v2 writes by this work  0
product code touched        0
```

## Open — next gate

P0 bootstrap CI must run green on this branch.

After P0:
M1 / P1 engine-independent contracts + Wren adapter begins.
No Metabase product routing before P3A bridge preflight.

## Known source-only deltas

Post-base ask-v2 fixes are reference-only. They are not silently inherited.
Any port requires Decision Receipt + branch-local proof.

## Stop conditions currently active

- no product code until bootstrap governance is green;
- no source-branch synchronization;
- no Metabase primary switch;
- no Wren removal.
