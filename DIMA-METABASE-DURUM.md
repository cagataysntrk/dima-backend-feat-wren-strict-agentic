# DIMA + METABASE — LIVING STATUS

**Branch:** `feat/dima-metabase-platform`  
**Source branch:** `feat/ask-v2-mvp` — READ ONLY  
**Base certified SHA:** `3774484167f1056d89da0e0609246fb4a05057ec`  
**Current phase:** P4 EXECUTION BINDING GREEN — COMPILER IMPLEMENTATION AUTHORIZED  
**Product-code development:** P4 COMPILER AUTHORIZED; COMPILER CODE NOT STARTED  
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

- each new milestone requires its own sealed pre-development review + scoped ticket before code;
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


---

## M2 / P2 closure — GREEN

```text
final M2 implementation SHA      = a05bd12ff56ac3c66eef01f7340c1f991ae07681
M2 workflow run                  = 35732633996 = SUCCESS
governance run                   = 35732633999 = SUCCESS
immutable Metabase image pin     = PASS
immutable PostgreSQL image pin   = PASS
isolated stack startup           = PASS
Metabase health                  = PASS
initial bootstrap                = PASS
Agent API authenticated ping     = PASS
unauthenticated Agent denial     = PASS
search/read-resource             = PASS
construct-query                  = PASS
execute                          = PASS
combined query                   = PASS
pagination                       = 200 + 5 rows observed
raw-SQL kill-switch              = PASS / HTTP 403
restart persistence              = PASS
Metabase app-DB backup           = PASS
restore smoke                    = PASS / 176 public tables
Dima v2/v3 product-code changes  = 0
Dima→Metabase product routing    = 0
source-branch writes/sync        = 0
ask-v2 source HEAD observed      = 6f7b3524dd692b6aefb68d9844cb606f0f25a2cd
```

M2 proves only the pinned runtime/lab capability boundary. It does **not** prove semantic bridge
feasibility, semantic equivalence, production tenant mapping, or Metabase substrate selection.

**Next authorized activity:** P3/P3A pre-development review only.
No P3 product code until that review/ticket is sealed and governance is GREEN.


---

## P3 / P3A pre-development review

Status: **SEALED — P3 transport implementation waits for governance GREEN**

Review:
`backend/belgeler/metabase/predev/P3_P3A_PREDEVELOPMENT_REVIEW.md`

Tickets:
- `backend/belgeler/metabase/tickets/P3_METABASE_CLIENT_BOUNDARY.md`
- `backend/belgeler/metabase/tickets/P3A_BRIDGE_PREFLIGHT.md`

Decisions:
- REST/Agent API is the P3 primary surface;
- candidate B (`ResolvedAnalyticsIntent`) is the only P3A prototype seam;
- P3A remains blocked until P3 is GREEN;
- no P4 work is authorized.


---

## P3 live RED — DMP-P3-RED-001

```text
tested SHA                    = 3d3302baf52ad02d9fc6d59c758e418f91822a49
P3 workflow                   = 35734065244 = FAILURE
forbidden-file isolation      = PASS
compile                       = PASS
provider-free P3              = PASS
pinned M2 lab startup         = PASS
live P3 Agent API proof       = FAIL / KeyError: 'name'
M1 regression                 = 35734065106 = SUCCESS
governance                    = 35734065224 = SUCCESS
M2                            = CLOSED GREEN / NOT REOPENED
P3A                           = BLOCKED
P4                            = FORBIDDEN
```

Owner: exact v0.63.18 read-resource transport contract, not semantic/compiler code.

### Open architecture debt — principal/access coherence

Not proven yet:

```text
ResolvedAnalyticsIntent.principal
== Dima effective execution principal
== Metabase authenticated principal
== DB/effective access principal
== durable ExecutionAccessFingerprint
```

P3 correctly receives a caller-injected Metabase session and does not own identity mapping.
The current lab-admin proof therefore **does not** establish permission parity, tenant isolation,
or a complete ExecutionAccessFingerprint. M1's current
`execution_access_fingerprint = principal_fingerprint` remains an interim M1 compatibility value,
not the final P5/P10 access-lens contract.

This debt must be discharged fail-closed before the first security-sensitive Dima→Metabase
execution/cutover. It is not a reason to add identity logic to P3 transport.


---

## P3 closure — GREEN

```text
final P3 implementation SHA    = 7a4d1d12e59b52edf8493c0aa0b147947ff4ecf9
P3 workflow                    = 35736253380 = SUCCESS
governance                     = 35736253664 = SUCCESS
provider-free P3               = 16 PASS
pinned live P3                 = 1 PASS
M1 regression                  = 35736253552 = SUCCESS
M1 provider-free               = 15 PASS
M1 real Wren + sentinels       = 5 PASS
exact read-resource envelope   = PASS
resource content/error XOR     = PASS
resource-level HTTP-200 error  = typed/preserved
malformed resource envelope    = fail-closed
resource URI/count integrity   = fail-closed
handshake read-resource proof  = real probe
serialized query/continuation  = distinct
raw SQL client method          = 0
admin/content mutation method  = 0
semantic handle resolution     = 0
raw user language dependency   = 0
M2                             = CLOSED GREEN / unchanged
source branch writes/sync      = 0
```

Historical RED `DMP-P3-RED-001` remains in the failure ledger and is now CLOSED GREEN.

**Next:** P3A eight-family semantic-duplication preflight. P4 remains forbidden until P3A records
one of: `PASS_B_SEAM`, `BLOCKED_DIMA_CONTRACT_GAP`, or
`REJECT_METABASE_STRUCTURED_EXECUTION`.


---

## P3A closure — PASS_B_SEAM

```text
final P3A HEAD                 = 480ea9a12c8a23458319df445c34ec67ef720695
P3A workflow                  = 35737923480 = SUCCESS
P3A provider-free             = 7 PASS
P3A pinned-live               = 1 PASS
representative families       = 8 / 8 compiled
portable query executions     = 9 / 9 completed
P3A forbidden-file isolation  = PASS
governance @ final HEAD        = 35737923380 = SUCCESS
M1 regression @ app-code SHA  = 35737822084 = SUCCESS
P3 regression @ app-code SHA  = 35737822159 = SUCCESS
result                         = PASS_B_SEAM
```

What PASS_B_SEAM means:
- candidate B remains viable: `ResolvedAnalyticsIntent + Dima-owned immutable execution snapshot`;
- context-bound candidate ids are lookup keys only, never durable semantic identity;
- stable business identity comes from DimaSemanticSpec ids;
- DB/schema/table/field locators come only from Dima SourceLineage;
- canonical/display names and `source_scopes` are not Metabase locators;
- period compatibility token is mapped explicitly to a stable Dima dimension id;
- missing mappings fail closed;
- cross-table lineage fails closed without an approved Dima relationship path;
- no Metabase search/read-resource is used as semantic authority;
- no raw user language reaches the compiler;
- no implicit FK join is emitted.

What it does **not** mean:
- production generation/reconciliation of the immutable snapshot is complete;
- arbitrary metric formula expressivity is proven;
- cross-table relationship compilation is proven;
- Wren/Metabase numeric equivalence is proven;
- permission/tenant/access-fingerprint parity is proven;
- Metabase is production primary;
- Wren can be retired.

**Next:** P4 pre-development review only. P4 product code remains forbidden until that review/ticket
is sealed and governance is GREEN.


---

## P4 pre-development review

Status: **SEALED / IMPLEMENTATION WAITS FOR GOVERNANCE GREEN**

Review:
`backend/belgeler/metabase/predev/P4_PREDEVELOPMENT_REVIEW.md`

Ticket:
`backend/belgeler/metabase/tickets/P4_METABASE_PROJECTION_COMPILER.md`

Key decisions:
- promote P3A execution binding; do not fork it;
- current catalog snapshot/fingerprint required for silent-rebind safety;
- no invented NULL/numeric/non-equality filter semantics;
- no cross-table implicit FK;
- no arbitrary metric-formula translation;
- no product routing.


---

## P4 execution-binding audit RED — DMP-P4-RED-001

```text
tested HEAD                    = af1750dfdfd283bfe824c9c6b40b90dca1a63cb3
P3                             = CLOSED GREEN
P3A                            = CLOSED / PASS_B_SEAM
P4 predevelopment              = GREEN
P4 production code             = STARTED
production execution_binding   = PRESENT
P3A duplicate binding models   = PRESENT / VIOLATION
P4 binding gate                = RED
compiler.py                    = NOT STARTED / BLOCKED
canonical.py                   = NOT STARTED / BLOCKED
source branch                  = READ ONLY
production routing             = UNCHANGED
```

Required correction:
one authoritative execution-binding truth in `execution_binding.py`, with P3A importing/re-exporting
the exact same classes and using an explicit governed current-catalog snapshot.

Historical P3/P3A closure evidence remains valid and is not overwritten. The P3A feasibility result
is not reopened; this RED concerns P4 production promotion discipline.

Compiler/canonical implementation is forbidden until a dedicated P4 binding workflow proves the
unified contract GREEN.

### Reminder — access/security debt remains open

The existing principal/access coherence debt is unchanged. Lab-admin P3/P3A/P4 representation proofs
do not establish tenant isolation, permission parity, RLS/CLS parity, revocation parity, or final
ExecutionAccessFingerprint correctness. Do not implement identity mapping inside the P4 compiler.


---

## P4 execution-binding promotion closure — GREEN

```text
binding implementation HEAD       = 1771becb3e59395cf28f993345703449feb9a98d
P4 binding workflow               = 35742516216 = SUCCESS
focused P4 binding                = 18 PASS
provider-free P3A/P3/M1           = 40 PASS
real Wren M1 regression           = 5 PASS
pinned-live P3 + P3A              = 2 PASS
P3A workflow                      = 35742516331 = SUCCESS
P3 workflow                       = 35742516120 = SUCCESS
M1 workflow                       = 35742516339 = SUCCESS
governance                        = 35742516356 = SUCCESS
binding type identity             = PASS
parallel binding implementations  = 0
current-catalog drift proof       = PASS
compiler.py                       = ABSENT / NOT STARTED
canonical.py                      = ABSENT / NOT STARTED
source branch observed            = 70fb5933982467c4acf9ecd847d8e48f900058ed
source branch writes/sync         = 0
```

DMP-P4-RED-001 is CLOSED GREEN.

Authoritative binding owner:
`backend/app/v3/substrate/metabase/execution_binding.py`

P3A now imports/re-exports the exact production binding primitives; its synthetic fixture carries an
explicit Dima-owned `CurrentCatalogSnapshot`, and P3A compilation validates expected SourceLineage
against current catalog before emitting physical locators.

**Next:** re-read P4 roadmap/report/compiler constraints and seal a compiler implementation review.
Only after that review/governance may `compiler.py` / `canonical.py` be created.


---

## P4 compiler implementation sub-gate — SEALED

Binding gate is CLOSED GREEN and the compiler-specific roadmap/report/pinned-runtime source re-read is
complete.

Authorized next files:
```text
backend/app/v3/substrate/metabase/compiler.py
backend/app/v3/substrate/metabase/canonical.py
backend/tests/test_v3_p4_metabase_compiler.py
backend/tests/test_v3_p4_metabase_canonical_live.py
.github/workflows/dima-metabase-p4.yml
```

No front-door/product routing is authorized.
