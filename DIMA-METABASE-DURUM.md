# DIMA + METABASE — LIVING STATUS

**Branch:** `feat/dima-metabase-platform`  
**Source branch:** `feat/ask-v2-mvp` — READ ONLY  
**Base certified SHA:** `3774484167f1056d89da0e0609246fb4a05057ec`  
**Current phase:** M2 / P2 — RUNTIME PINNED; ISOLATED LAB IMPLEMENTATION READY  
**Product-code development:** M1 CLOSED GREEN; M2 LAB IMPLEMENTATION NOT STARTED  
**Metabase runtime:** v0.63.18 / immutable image digest PINNED  
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

**M2 / P2:** Metabase source/runtime pin policy + isolated self-host lab bootstrap.

Before any M2 infrastructure/product change:
1. re-read sealed roadmap P2 and relevant architecture report sections;
2. revalidate source/runtime pin distinction and current living status;
3. inspect existing repo infrastructure without changing v2/source;
4. seal an M2 pre-development review + scoped ticket;
5. only then select an exact supported Metabase runtime release + immutable image digest.

No Dima product routing to Metabase is authorized in M2. P3A remains the semantic bridge gate.

## Known source-only deltas

Post-base ask-v2 fixes are reference-only. They are not silently inherited.
Any port requires Decision Receipt + branch-local proof.

## Stop conditions currently active

- P0 bootstrap is closed; product code may change only under an authorized M1/P1 ticket after mandatory pre-development source review;
- no source-branch synchronization;
- no Metabase primary switch;
- no Wren removal.


---

## P0 bootstrap closure — GREEN

```text
bootstrap governance commit = e7c77da5ccd610f580e8213beb7de124ff5d3566
governance CI run           = 35726153125
governance CI result        = SUCCESS
certified base ancestry     = PASS
sealed report blob          = PASS
sealed roadmap blob         = PASS
mandatory governance files  = PASS
legacy resolver v3 guard    = PASS
ask-v2 source HEAD observed = 4ad8238c4fe8ada02a8a1a79e0682606a6fbfe1a
ask-v2 writes               = 0
product-code changes        = 0
```

**P0 infrastructure/bootstrap status: CLOSED GREEN.**

Next authorized milestone: **M1 / P1 — engine-independent Dima contracts + Wren adapter with zero behavior drift.**
This status does not authorize Metabase production routing, Wren retirement, or source-branch synchronization.


---

## M1 / P1 pre-development review

Status: **SEALED / IMPLEMENTATION AUTHORIZED AFTER REVIEW COMMIT GREEN**

Review path:
`backend/belgeler/metabase/predev/M1_P1_PREDEVELOPMENT_REVIEW.md`

Reviewed:
- sealed roadmap P1;
- sealed architecture R0.2, R2, R5, R6, R7;
- source lock, operation, audit, failure/decision receipts;
- certified-base Standard authority/projection/execution/semantic-handle code;
- moving ask-v2 post-base deltas READ-ONLY.

Historical result: review commit `67a1ded2...` and governance run `35727494650` were GREEN; M1 implementation subsequently completed and certified.


---

## M1 / P1 closure — GREEN

```text
final M1 implementation SHA  = 17942f179b13fd2cb81fd284789ba0f6366d2ed8
M1 workflow run              = 35730916014 = SUCCESS
governance run               = 35730916118 = SUCCESS
provider-free contracts      = 15 PASS
real Wren parity + sentinels = 5 PASS
forbidden-file isolation     = PASS
v2/source files modified     = 0
ask-v2 source HEAD observed  = 7d970c6fc9f9cb275700e72e445427695e7252a4
automatic source sync        = 0
Metabase runtime dependency  = 0
production routing change    = 0
```

M1 invariants certified:
- engine-independent v3 contracts exist;
- Dima resolves semantic handles before substrate execution;
- Wren substrate does not own semantic handle resolution or raw-language interpretation;
- original resolver candidate provenance survives the seam;
- material semantic-surface completeness and shared Standard/Research XOR have v3 contract proofs;
- Wren SQL/CubeQuery/result/provenance and legacy audit-question persistence are parity-checked;
- retained v2 Wren trust-plane sentinels remain GREEN.

**Next:** M2/P2 pre-development review. M2 does not authorize Metabase product routing.


---

## M2 / P2 pre-development review

Status: **SEALED / RUNTIME RESEARCH AUTHORIZED AFTER GOVERNANCE GREEN**

Review:
`backend/belgeler/metabase/predev/M2_P2_PREDEVELOPMENT_REVIEW.md`

Ticket:
`backend/belgeler/metabase/tickets/M2_P2_METABASE_LAB_BOOTSTRAP.md`

Next action:
verify an official supported Metabase runtime release and immutable image digest. No lab compose
implementation is authorized until both pins are recorded.


### M2 runtime pin — SEALED

```text
Metabase runtime   = v0.63.18
Metabase digest    = sha256:1160b570cb11c107bce00e71293552df8a8363e01a32c2c7a048cee002dc8a73
PostgreSQL runtime = 17.11
Postgres digest    = sha256:67f41722b7a8cbdb868a44a4995c846eddfdc2973bccb291ce937dce88ad5675
```

Lab implementation may begin only inside the M2 allowlist. Product routing remains forbidden.
