# DIMA + METABASE — LIVING STATUS

**Branch:** `feat/dima-metabase-platform`  
**Source branch:** `feat/ask-v2-mvp` — READ ONLY  
**Base certified SHA:** `3774484167f1056d89da0e0609246fb4a05057ec`  
**Current phase:** P5 CONTRACT GREEN — P6A SAME-SNAPSHOT CANARY NEXT  
**Product-code development:** P6A NOT STARTED; SHARED-SNAPSHOT CANARY NEXT; P10 ISSUER STILL SEPARATE  
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


---

## P4 live canonical RED — DMP-P4-RED-002

```text
tested SHA                         = 3db99a6b6827d0abaefce06b12d27ab981143da2
P4 workflow                        = 35743999330 = FAILURE
forbidden-file isolation           = PASS
compile P4 production boundary     = PASS
focused P4 binding+compiler        = PASS
provider-free regressions          = PASS
real Wren M1 regression            = PASS
pinned M2 lab startup              = PASS
pinned-live P3/P3A                 = reached
P4 canonical double construct      = FAIL
failure                            = NON_DETERMINISTIC_CANONICAL_SERIALIZATION
root cause                         = runtime-generated lib/uuid volatility
P5                                 = NOT STARTED / FORBIDDEN
production routing                 = UNCHANGED
```

DMP-DEC-0013 now defines durable canonical identity as exact equality after removing only the
documented runtime-volatile `lib/uuid` key. Any other canonical difference remains a hard RED.


---

## P4 supervisor architecture audit — filter sentinel correction

```text
DMP-P4-RED-002 canonical UUID fix      = IN PROGRESS
focused UUID exact-key proof           = GREEN @ 3e063e5fa793a15bee6b42660ce2158c8e21dbad
DMP-P4-AUDIT-003                       = OPEN / AUTHORIZED
special string sentinel semantics      = MUST BECOME 0
typed NULL upstream contract           = NOT PRESENT / NOT INVENTED
P5                                     = BLOCKED
```

DMP-DEC-0014 clarifies DMP-DEC-0011: supported textual filter values are literal equality payloads.
`"NULL"` is not SQL NULL. No token table/fallback is permitted.


---

## P4 live canonical RED — DMP-P4-RED-004

```text
tested SHA                         = 428ba51845966c95baf97dcace3ca9851c85762f
P4 workflow                        = 35752287941 = FAILURE
focused P4                         = PASS
provider-free regressions          = PASS
real Wren                          = PASS
pinned lab                         = PASS
P3 same-SHA workflow               = PASS
governance same-SHA                = PASS
exact lib/uuid stripping           = PASS provider-free
remaining live drift               = NON_DETERMINISTIC_CANONICAL_SEMANTICS
exact differing JSON path          = NOT YET OBSERVED
P5                                 = BLOCKED
```

No new volatile field is authorized. Next step is diagnostic-only exact path/value capture.


---

## P4 RED-004 root cause proven

```text
diagnostic SHA                    = 118adca3441a8b08503cda06020679aaf39f057b
diagnostic workflow               = 35752908054
exact drift path                  = $.stages[0].order-by[0][2][2]
portable ref                      = ["aggregation", {}, 0]
canonical ref                     = ["aggregation", {...}, "<aggregation lib/uuid>"]
pinned Metabase equality          = aggregation UUID -> same-stage index
general UUID stripping            = FORBIDDEN
authorized stabilization          = exact same-stage aggregation ref only
P5                                = BLOCKED
```

DMP-DEC-0015 is now the only authorized correction for this drift.


---

## P4 closure — GREEN

```text
final implementation SHA        = 0af815887d8e50274b39bdb7975eb37e6e63971a
P4 workflow                     = 35753630759 = SUCCESS
P3 same-SHA workflow            = 35753630526 = SUCCESS
M1 same-SHA workflow            = 35753630773 = SUCCESS
governance same-SHA             = 35753630765 = SUCCESS

focused P4                      = 44 PASS
provider-free P3A/P3/M1         = 40 PASS
real Wren                       = 5 PASS
pinned-live P3/P3A/P4           = 3 PASS
8-family canonical proof        = PASS
9/9 actual serialized execution = PASS

exact lib/uuid volatility       = PROVEN / STABILIZED
aggregation runtime refs        = PROVEN SAME-STAGE UUID->INDEX ONLY
other canonical drift           = HARD FAIL
literal NULL text               = literal equality / PASS
regex/fuzzy/sentinel fallback   = 0
implicit/unauthorized joins     = 0
silent source rebind            = 0
silent semantic slot loss       = 0
production routing change       = 0
Wren retirement                 = 0
P5 code                         = 0
source branch                   = READ ONLY @ 70fb5933982467c4acf9ecd847d8e48f900058ed
```

P4 is **CLOSED GREEN**.

Next authorized activity is **P5 pre-development review only**. P5 implementation is not authorized
until that review is sealed and governance is GREEN. The open principal/access coherence debt must be
handled explicitly there; it must not be hidden behind the current lab-admin execution proof.


---

## P5 pre-development review

Review:
`backend/belgeler/metabase/predev/P5_PREDEVELOPMENT_REVIEW.md`

Key classification:
```text
P4 query identity                         = GREEN / authoritative
M1 DimaQueryReceipt                       = foundational shell only
principal_fingerprint                     = tenant/principal/roles identity
legacy execution_access_fingerprint alias = M1_COMPAT_ONLY
P5 official access fingerprint            = complete ExecutionAccessSnapshot required
DMP-P5-BLOCK-001                          = OPEN
P5 contract                              = implementation authorized
P5 CONTRACT GREEN                         = requires complete snapshot contract + strict sealer
production official receipt issuance      = BLOCKED until P10 closes DMP-P5-BLOCK-001
production routing                        = unchanged
```


---

## P5/P10 ownership clarification — DMP-DEC-0018

```text
P5 owner                         = ExecutionAccessSnapshot contract + strict receipt sealer
P10 owner                        = production effective-access issuer/mapping
P5 contract closure              = allowed independently
production official receipt      = blocked until P10
DMP-P5-BLOCK-001                 = OPEN / TRANSFERRED TO P10
P6/P7/P8/P9                      = not blocked by issuer implementation
```

Receipt identities are now explicitly separated:
`canonical_query_fingerprint` (query), `execution_access_fingerprint` (access),
`receipt_fingerprint` (durable execution content), and `receipt_id` (execution occurrence).


---

## P5 contract implementation candidate

```text
implementation SHA              = c8be6720f8f0f908b3cc6459fb817d760d417c8e
P5 provider-free workflow       = 35759329146 = SUCCESS
focused P5                      = 34 PASS
provider-free P4 regression     = 44 PASS
M1 critical regression          = 15 PASS
full M1/Wren workflow           = 35759329091 = SUCCESS
governance                      = 35759329034 = SUCCESS
production access issuer        = NOT IMPLEMENTED / P10
product routing                 = UNCHANGED
```

Closure candidate adds one missing runtime-identity negative proof and runs the pinned-live
P3/P3A/P4 suite exactly once. P6 remains blocked until that closure proof is GREEN.


---

## P5 contract closure — GREEN

```text
P5 product implementation SHA        = c8be6720f8f0f908b3cc6459fb817d760d417c8e
P5 closure candidate SHA             = 94e9b3da892a80253495324b2a256f128b037d1b
P5 closure workflow                  = 35759691357 = SUCCESS
governance @ closure candidate       = 35759691408 = SUCCESS
focused P5 identity/receipt          = 35 PASS
provider-free P4 regression          = 44 PASS
M1 critical regression               = 15 PASS
full M1/Wren @ implementation SHA    = 35759329091 = SUCCESS
pinned-live P3/P3A/P4                = 3 PASS
pinned Metabase health/bootstrap     = PASS

ExecutionAccessSnapshot              = COMPLETE CONTRACT
role/source order invariance         = PASS
policy/RLS/CLS/DB/security drift     = fingerprint-changing
missing access/runtime               = HARD FAIL
authority/projection/intent mismatch = HARD FAIL
tenant/principal/roles/context       = HARD FAIL
source-resource mismatch             = HARD FAIL
query/result/event cardinality       = HARD FAIL
receipt_fingerprint                  = durable execution-content identity
receipt_id                           = execution occurrence identity
executed_at                          = event metadata only
ephemeral handle/session identity    = excluded
regex/fuzzy/morphology resolver      = 0
production routing change            = 0

DMP-P5-BLOCK-001                     = OPEN / P10 SECURITY MAPPING GATE
production official receipt issuance = BLOCKED UNTIL P10
source branch                        = READ ONLY @ 875c446476b6ae4907f5cac5d1c7b512e5157538
```

P5 is **CONTRACT GREEN**. This certifies the immutable access snapshot contract and strict receipt
sealer only. It does not certify a production access issuer, tenant isolation, permission parity,
Metabase primary routing, or Wren retirement.

**Next:** P6 pre-development review + frozen 80-case parity corpus. P10 issuer blocker remains separate.


---

## P6 pre-development review — SEALED

Review:
`backend/belgeler/metabase/predev/P6_PREDEVELOPMENT_REVIEW.md`

Ticket:
`backend/belgeler/metabase/tickets/P6_WREN_METABASE_PARITY.md`

First proven gap:
`DATA/FIXTURE_GAP` — existing Wren and Metabase live suites use different databases.

Decision DMP-DEC-0019 requires one shared PostgreSQL parity snapshot before any numeric A/B claim.

Next after governance GREEN:
freeze the exact 80-case post-authority corpus and its fingerprint. No P6 execution patch precedes
that freeze.


---

## P5 provenance audit correction — GREEN

```text
fix SHA                           = e9eb74b7edf00406187fa250ceb911dc0de9e4d7
DMP-P5-RED-001                    = CLOSED GREEN
P5 workflow                       = 35763693146 = SUCCESS
focused P5                        = 41 PASS
provider-free P4 critical         = 44 PASS
M1 critical                       = 15 PASS
M1/Wren workflow                  = 35763692416 = SUCCESS
governance                        = 35763692629 = SUCCESS
resource pairing loss             = FIXED
partial resource identity         = HARD FAIL
warnings/limitations/attestations = DURABLY BOUND
P10 production issuer             = STILL BLOCKED / SEPARATE
```

P6 review is minimally amended:
- `RECEIPT/PROVENANCE_GAP` is a first-class mismatch owner;
- implementation order is now P6A same-snapshot canary → P6B corpus freeze → P6C full parity.

**Next:** P6A shared PostgreSQL same-snapshot canary.


---

## P6A0 shared-snapshot infrastructure canary — GREEN

```text
current corrective HEAD             = 5f64379c28187d021f9bb7a813bb678ce60f5174
P6 workflow                         = 35765566189 = SUCCESS
M2 repaired self-run                = 35765566147 = SUCCESS
governance                          = 35765566328 = SUCCESS
fixture version                     = p6-shared-v1
p6_orders                           = 8 rows
p6_customers                        = 4 rows
snapshot_id                         = a6ef6ba31738b90e939adafb49830291b2d3a74497d83940ed3479adffa23f74
content checksum                    = 78eec96fb8901b72828fbbeae9ea065da5e7bb8a60a87b39e66155d682c74a23
golden total                        = 2000
golden January                      = 750
P6A0 live                           = 3 PASS
DMP-P6-RED-001                      = CLOSED GREEN
DMP-P6-RED-002                      = CLOSED GREEN
DMP-P6-AUDIT-003                    = OPEN
source branch observed              = 1e1c33e8750366d149bcceef1452b70da3774682
source branch writes/sync           = 0
```

**Current phase:** P6A0 SHARED-SNAPSHOT INFRASTRUCTURE CANARY GREEN — P6A1 TRUE SUBSTRATE-SEAM CANARY NEXT

P6A0 proves physical-data/connectivity and independent golden-anchor correctness only. It is not
full substrate parity because the Wren arm currently uses hand-authored SQL.

P6 full corpus: **NOT FROZEN**.  
P6 full parity: **NOT STARTED**.

P6A1 must send the same accepted Dima meaning through the existing Wren substrate seam and a thin
Metabase execution adapter. Only substrate implementation may vary.


---

## P6A1 governance activation RED — DMP-P6-RED-004

```text
tested SHA              = 28c4ca6525bbde0193901362b1d70c92ffc0347f
governance run          = 35768149721 = FAILURE
failed gate             = Require sealed P6 review before parity code exists
classification          = CI/GOVERNANCE SEAL-TOKEN DRIFT
product/semantic owner  = NONE
P6A1 product patch      = UNCHANGED
```

Correction is documentation-only: sealed authorization wording now explicitly states that corpus
freeze/parity harness authorization is contingent on **P6A1 GREEN**.


---

## P6A1 first true-seam measurement — typed gap found

```text
product SHA                       = 28c4ca6525bbde0193901362b1d70c92ffc0347f
P6 run                            = 35768149802 = FAILURE (measurement harness stopped early)
P6A0 snapshot/golden              = PASS
provider-free inherited gates     = PASS
Metabase bootstrap                = PASS
M1/Wren regression                = PASS @ 35768149702
P3 regression                     = PASS @ 35768149806
governance seal correction        = PASS @ 35768404434
CANARY-03 validation              = WREN_COMPATIBILITY_GAP
exact reason                      = unsupported Wren period kind: absolute
wren.py changes                   = 0
P4 compiler changes               = 0
corpus                            = NOT FROZEN
```

Next harness run must measure cases independently:
CANARY-01 and CANARY-02 execute through both real substrate seams; CANARY-03 is expected to remain a
typed Wren compatibility gap unless a later milestone explicitly owns that feature.


---

## P6A1 second typed gap — Wren PostgreSQL runtime contract

```text
tested SHA                       = d317ea9370270e2381fde1d06a54c90aa4cbb339
P6 run                           = 35768689486 = FAILURE (instrument stopped on typed runtime gap)
P6A0                             = PASS
provider-free P6A1               = PASS
Metabase bootstrap               = PASS
CANARY-01 Wren execution         = SUBSTRATE_RUNTIME_GAP
exact field                      = kwargs.connect_timeout
produced value/type              = 15 / int
installed Wren expected type     = string
CANARY-03 known gap              = WREN_COMPATIBILITY_GAP / absolute period
wren.py                          = UNCHANGED
wren_service.py                  = UNCHANGED
corpus                           = NOT FROZEN
```

P6A1 is now **TYPED GAP FOUND**, not GREEN. Measurement harness may continue and report the exact
gaps; it may not repair WrenService inside P6.


---

## P6 closure strategy — DMP-DEC-0020

```text
P6 role                           = targeted architecture/capability measurement
fixed 80-case P6 blocker          = SUPERSEDED
broad cross-engine parity         = DEFERRED TO INTEGRATED STANDARD CERTIFICATION
preferred broad timing            = after P10 minimum / preferably P13 / around P14
current known semantic/runtime gaps= typed and carried forward
unknown/unexplained mismatch      = MUST REMAIN 0
test strategy                     = maximum information per test
```

ASK_V2_DAY7_REFERENCE_SHA = `5789e729115fe044b689739d5960021aba0aca32`  
disposition = `REFERENCE_ONLY / NO_CODE_INHERITANCE_YET`

No merge, cherry-pick, rebase, certified-base replacement or source-branch write is authorized.


---

## P6 TARGETED PARITY PROBE — CLOSED

```text
closure SHA                       = 03912a8702b27eca634e8411b151acdd56491d2c
final focused P6 workflow         = 35771661991 = SUCCESS
governance                        = 35771661812 = SUCCESS
P6A0 shared snapshot              = GREEN
independent golden anchors        = GREEN
P6A1 same-intent measurement      = COMPLETE
CANARY-01                         = SUBSTRATE_RUNTIME_GAP
CANARY-02                         = SUBSTRATE_RUNTIME_GAP
CANARY-03                         = WREN_COMPATIBILITY_GAP
UNEXPLAINED_MISMATCH              = 0
oracle fossilization              = FIXED
broad parity                      = DEFERRED / DMP-DEC-0020
Wren/Metabase equivalence claim   = NO
```

P6 result is **measurement GREEN / parity incomplete with typed gaps**.

**Current phase:** P7 PRE-DEVELOPMENT — DimaSemanticSpec V1 + structured Wren MDL importer.


---

## P7 DimaSemanticSpec importer — CLOSED BASELINE

```text
implementation SHA                 = 2e233ea6122c9cc0ccc18ebe2978e2e896ebb41c
P7 workflow                        = 35772646640 = SUCCESS
focused importer                   = 8 PASS
inherited provider-free            = 13 PASS / 2 SKIP
M1/Wren                            = 35772646558 = SUCCESS
governance                         = 35772646510 = SUCCESS
models observed                    = 80
cubes observed                     = 23
metrics imported                   = 136
regular dimensions imported        = 121
time dimensions imported           = 23
relationships observed             = 31
views observed                     = 1
duplicate semantic source names    = 0
missing cube baseObject            = 0
relationship join-key gaps         = 31
calculated dimension gaps          = 29
calculated model-column gaps       = 25
cube semantic-entity gaps          = 23
view definition gaps               = 1
```

P7 result: **migration baseline GREEN / typed representation gaps explicit**.

**Current phase:** P8 PRE-DEVELOPMENT — semantic equivalence matrix.


---

## P8 semantic equivalence matrix — CLOSED

```text
implementation SHA                 = 23480aa433ba10fed84a015a85c9f1d88b31572e
P8 workflow                        = 35773470252 = SUCCESS
focused equivalence                = 14 PASS
P7 regression                      = 8 PASS
M1/Wren                            = 35773470027 = SUCCESS
governance                         = 35773470111 = SUCCESS
unknown gap default                = 0 / HARD RED
formula text parsing               = 0
relationship-condition parsing     = 0
Metabase semantic discovery        = 0
Wren removal                       = NOT AUTHORIZED
```

P8 result: **capability matrix GREEN / semantic equivalence remains typed per feature**.

**Current phase:** P9 PRE-DEVELOPMENT — semantic resource provisioner.


---

## P7/P8 correctness hardening — structured-field coverage

```text
DMP-P7-AUDIT-001                = OPEN / CORRECTION APPLIED
coverage invariant              = every non-empty structured key accounted
unknown structured key          = UNMAPPED_STRUCTURED_FIELD / P8 HARD RED
formula parsing                 = 0
join-condition parsing          = 0
fuzzy/name similarity           = 0
P9B                              = HELD
ASK_V2_RELATIONSHIP_REFERENCE   = b815d19cc8f07ecbd617e3e417e1405503a59542
source disposition              = REFERENCE_ONLY
```


---

## P7/P8 hardening — GREEN

```text
hardening SHA                    = d0bbb77c846713f50f856146dd3377bd5d025a9d
P7 workflow                     = 35777948476 = SUCCESS
P7 focused                      = 11 PASS
P8 workflow                     = 35777948438 = SUCCESS
P8 focused                      = 28 PASS
P7 regression inside P8         = 11 PASS
M1/Wren                         = 35777948408 = SUCCESS
governance                      = 35777948509 = SUCCESS
DMP-P7-AUDIT-001                = CLOSED GREEN
unknown structured field        = HARD GAP / P8 RED
```

## P9A lifecycle hardening

```text
DMP-P9-AUDIT-002                = OPEN / CORRECTION APPLIED
stale DIMA_MANAGED lifecycle    = explicit reconciliation
NOOP metadata coherence         = enforced
mutating rollback contract      = enforced
real P7→P8→policy→P9 proof      = added
P9B                             = HELD UNTIL GREEN
```


---

## P9A HARDENING — CLOSED GREEN

```text
hardening SHA                     = 7820ac77207f4245da150a5c80043d22708b87f0
P9 workflow                       = 35778418835 = SUCCESS
P9 focused                        = 23 PASS
P7+P8 inherited                   = 39 PASS
M1/Wren                           = 35778418797 = SUCCESS
governance                        = 35778418759 = SUCCESS
DMP-P9-AUDIT-002                  = CLOSED GREEN
stale lifecycle                   = GREEN
binding metadata coherence        = GREEN
mutating rollback enforcement     = GREEN
real P7→P8→policy→P9 chain        = GREEN
```

## P9B pinned-source review

```text
Metabase pin                      = v0.63.18 / 2ba2485c78d7e00a9a25f82c00fc201da71590c4
metric persistence                = Card(type=metric) / api/card
api/metric                        = read/query, not CRUD
dimension persistence             = existing Field metadata / attached Dimension
time standalone CRUD              = NOT PROVEN
relationship standalone CRUD      = NOT PROVEN
metric Card projection contract   = NOT PROVEN
live writes                       = 0
```

**Current phase:** P9B1 PROVIDER-FREE METRIC CARD CONTRACT PRE-DEVELOPMENT.  
P10: **NOT STARTED**.


---

## P9B1 boundary — AUTHORIZED PROVIDER-FREE

```text
DMP-DEC-0023                    = SEALED
pinned create surface           = POST /api/agent/v1/metric
pinned update surface           = PUT /api/agent/v1/metric/:id
query source                    = construct-query base64 MBQL
generic Card query reconstruction= FORBIDDEN
P9B1                            = provider-free CREATE contract
live writes                     = 0 / NOT AUTHORIZED
dimension/time/relationship     = typed transport gaps
```


---

## P9B1 first focused RED — classified

```text
tested SHA                    = 606f89aee8f31c4c866669dbc6efb64dfa58d9d9
P9B workflow                  = 35780048833 = FAILURE
compile/isolation             = PASS
focused                       = 7 PASS / 6 FAIL
M1/Wren same SHA              = 35780048770 = SUCCESS
governance same SHA           = 35780048790 = SUCCESS
classification                = contract error precedence + test oracle
HTTP writes                   = 0
semantic/compiler changes     = 0
```

DMP-P9B-RED-001 correction is minimal: structural rejection precedes semantic-id equality and the
anti-SQL test no longer confuses Python import syntax with SQL.


---

## P9B1 identity hardening — DMP-P9B-AUDIT-002

```text
DMP-P9B-RED-001                  = CLOSED GREEN
closing SHA                      = aa461134ddb044798be6275f7dc68d3979aff810
closing workflow                 = 35780384430 = SUCCESS
focused before audit             = 13 PASS
P7/P8/P9 inherited              = 62 PASS
DMP-P9B-AUDIT-002                = CORRECTION APPLIED / AWAITING GREEN
transport tenant identity        = REQUIRED
target tenant mismatch           = HARD FAIL
projection_hash                  = CONTRACT-BOUND
resolved_intent_hash             = CONTRACT-BOUND
current_catalog_fingerprint      = CONTRACT-BOUND
live writes                      = 0
P10                              = NOT STARTED
ASK_V2 observed                  = aef1032a514cf27bf41e53294b4e1ce669d45813
ASK_V2 disposition               = REFERENCE_ONLY
```


---

## P9B1 tenant/projection provenance — GREEN

```text
hardening SHA                      = 33c93fa3cd579e9d2e42eef0335215747183590c
P9B workflow                       = 35782035041 = SUCCESS
focused P9B1                       = 18 PASS
P7/P8/P9 inherited                 = 62 PASS
governance                         = 35782035058 = SUCCESS
M1/Wren                            = 35782035064 = SUCCESS
DMP-P9B-AUDIT-002                  = CLOSED GREEN
production writes                  = BLOCKED
authorized next                    = ONE ISOLATED PINNED-LIVE METRIC LIFECYCLE
```


---

## P9B live lifecycle first RED — DMP-P9B-RED-003

```text
tested SHA                      = 9f33d9f97faa331666a12fa2382fdb649a7481a2
workflow                        = 35782467824
provider-free P9B               = GREEN
create                          = PASS
exact-id created read           = PASS
stable entity binding           = PASS
P9 replan NOOP                  = PASS
archive mutation                = PASS
archived exact-id read          = ORACLE RED
root cause                      = Metabase presents directly archived Card in Trash collection
product-code owner              = NONE
teardown                        = PASS
```

Correction is test-only. Archived state no longer requires the original collection presentation;
restore state still must return to the explicit original collection and preserve entity identity.


---

## P9B METRIC TRANSPORT — ISOLATED LIFECYCLE GREEN

```text
closure SHA                       = d3f4bb8b8aa9a65796506193632f7c429eac8d7c
P9B workflow                      = 35782974669 = SUCCESS
governance                        = 35782974647 = SUCCESS
provider-free contract            = GREEN
isolated pinned-live lifecycle    = 1 PASS
create                            = PASS
exact-id read                     = PASS
stable entity_id                  = PASS
P9 replan                         = NOOP
archive / exact-id read           = PASS
restore / exact-id read           = PASS
cleanup                           = PASS
search/name adoption              = 0
production customer writes        = 0 / BLOCKED
dimension transport               = GAP
time transport                    = GAP
relationship transport           = GAP
```

P9B result: **metric transport proof GREEN in isolated lab only**.

**Current phase:** P10 PRE-DEVELOPMENT — tenant/principal/security mapping + production
ExecutionAccessSnapshot issuer. DMP-P5-BLOCK-001 remains OPEN.


---

## P10A ACCESS SNAPSHOT ISSUER — GREEN

```text
implementation SHA                 = 1abf43657453a771954a939de834e6b48f55620e
P10 workflow                       = 35783766213 = SUCCESS
focused P10A                       = 20 PASS
P5 + P9B inherited                 = 59 PASS
M1/Wren                            = 35783766157 = SUCCESS
governance                         = 35783766051 = SUCCESS
durable access model               = P5 ExecutionAccessSnapshot ONLY
DMP-P5-BLOCK-001                   = OPEN
production official receipt        = BLOCKED
production P9B writes              = BLOCKED
```

DMP-P10-AUDIT-001:
current OSS lab can prove basic query permission/revocation, but cannot honestly prove premium
sandbox/advanced-permission/impersonation row/column lens.

**Current phase:** P10B1 isolated authenticated-user + permission-revocation proof.


---

## P10B1 BASIC REAL SECURITY CANARY — CLOSED GREEN

```text
audited HEAD                      = e422df46cefa9ef7207030e48fcc28cd0b78bb51
P10B1 workflow                    = 35784824929 = SUCCESS
P10A workflow                     = 35783766213 = SUCCESS
P10A focused                      = 20 PASS
P5/P9B inherited                  = 59 PASS
same authenticated restricted user= PASS
allow before revoke               = PASS
same-session revoke               = HTTP 403 / PASS
restore                           = PASS
permission graph cleanup          = PASS
admin analytical execution fallback= 0
DMP-P5-BLOCK-001                  = OPEN
```

P10B1 proves the basic authenticated-subject + permission-revocation slice only. It does not certify
RLS/CLS/impersonation/advanced route/cache-lens security.

---

## Architecture refinement — DMP-DEC-0026

```text
LLM_FIRST_COGNITION                  = BINDING
SEMANTIC_CORE_IS_NOT_ANALYTICAL_PLANNER = BINDING
ADAPTIVE_GOVERNANCE                  = LEVEL 0..3 / SECURITY BASELINE AT LEVEL 0
SEMANTIC_NECESSITY_GATE              = REQUIRED FOR NEW DETERMINISTIC COGNITION
Luna                                 = DEFAULT / ECONOMIC BASELINE
Sol                                  = CEILING / HEADROOM
Fast Track                           = CONTROLLED HARVEST ONLY
ask-v2                               = CONTROLLED HARVEST / REFERENCE ONLY
bulk merge/cherry-pick               = FORBIDDEN
```

Simple/native path remains scoped:
`LLM → minimum Dima security/execution/provenance envelope → Metabase → receipt/evidence`.

---

## P10B2 capability classification

```text
advanced security implementation = NOT AUTHORIZED
tenant identity                  = PROVEN
principal identity               = PROVEN
basic DB query permission        = PROVEN
same-session revocation          = PROVEN
collection permission            = CAPABILITY_GAP
RLS                              = NOT_CONFIGURED / BLOCK IF REQUIRED
CLS                              = NOT_CONFIGURED / BLOCK IF REQUIRED
impersonation                    = REQUIRES_EXTERNAL_OWNER
database routing                 = REQUIRES_EXTERNAL_OWNER
cache/result reauthorization     = CAPABILITY_GAP
service/admin fallback prohibition= PROVEN
DMP-P5-BLOCK-001                 = OPEN / GLOBAL PRODUCTION OFFICIAL ISSUANCE
```

**Current phase:** P11 PRE-DEVELOPMENT — entity-value Semantic Necessity Gate.  
Deterministic entity resolver: **NOT AUTHORIZED**.  
First proposed Luna/Sol corpus: `P11_ENTITY_VALUE_NECESSITY_GATE.md`.


---

## DMP-DEC-0026 governance repin

```text
docs SHA                         = 4363a9604483aee5c8029bb6a6447bda34b42eaf
governance run                   = 35786752576 = FAILURE
classification                   = expected sealed-blob pin drift
product/runtime owner            = NONE
architecture report reviewed blob= aa5f3e048dea56ec52110023e7399fc1fe957805
roadmap reviewed blob            = 01d1893bf85a482f5970d27ec70a60df7b836219
historical receipt rewrite       = 0
DMP-GOV-RED-001                  = CORRECTION APPLIED / AWAITING GREEN
```


---

## DMP-DEC-0026 / P10B2 classification closure

```text
current HEAD                      = e6b8d98190369b010cf8dcd743fdc3d4ece645c0
governance                        = 35786915071 = SUCCESS
P10A provider-free after docs     = 35786752567 = SUCCESS
DMP-GOV-RED-001                   = CLOSED GREEN
P10B2 classification              = COMPLETE
P10B2 advanced implementation     = NOT AUTHORIZED
DMP-P5-BLOCK-001                  = OPEN
P11 predev                        = SEALED
P11 deterministic resolver        = NOT AUTHORIZED
P11 Luna/Sol necessity corpus V1 = PROPOSED / MODEL RUNS NOT STARTED
```

P11 may now proceed only with the Semantic Necessity Gate. A deterministic entity resolver requires
measured material failure first.


---

## P11A source contract + frozen necessity evaluation V1

```text
resolver product code              = 0
pinned Metabase                    = v0.63.18 / 2ba2485c78d7e00a9a25f82c00fc201da71590c4
value list                         = GET /api/field/:id/values
value search                       = GET /api/field/:id/search/:search-id
current-user permission boundary   = PINNED SOURCE PROVEN
physical field ids visible to LLM = 0
indexed entities mandatory         = NO
runnable now                       = EV-01..EV-04
blocked                            = EV-05..EV-07
Luna requested model               = openai/gpt-5.6-luna
Sol requested model                = openai/gpt-5.6-sol
primary evaluations                = 8 maximum before failure repeats
model runs                         = AWAITING CI
```


---

## P11 V1 baseline Luna/Sol measurement

```text
measurement SHA                    = 977faa99cdf6581ce02c13b55add4077750fe540
workflow                           = 35789082927 = SUCCESS
provider-free freeze               = GREEN
governance                         = GREEN
corpus fingerprint                 = da7f13e804c643c376d085b0e0fa94e132fdd8877e1945e4c19257160d03e06c
Luna exact runtime id              = openai/gpt-5.6-luna
Sol exact runtime id               = openai/gpt-5.6-sol
primary evaluations                = 8
repeat calls                       = 4
total model calls                  = 12
EV-01                              = PASS / PASS
EV-02                              = PASS / PASS
EV-03                              = SILENT BIND / SILENT BIND
EV-04                              = PASS / PASS
raw silent-wrong occurrences       = 5
Luna total cost                    = USD 0.0015242
Sol total cost                     = USD 0.0101260
classification                     = MATERIAL_TRUTH_GAP
root cause                         = unresolved multi-scope value adoption
DMP-DEC-0027                       = SEALED
entity resolver                    = NOT AUTHORIZED
minimum adoption gate              = AUTHORIZED
DMP-P5-BLOCK-001                   = OPEN
```

Next: implement only the DMP-DEC-0027 adoption gate, then rerun the exact same frozen corpus.


---

## P11 minimum adoption gate implementation candidate

```text
decision                         = DMP-DEC-0027
mechanism                        = EntityValueAdoptionGate
language cognition              = 0
candidate retrieval             = 0
translation dictionary          = 0
regex/fuzzy/stemming/morphology = 0
physical field discovery        = 0
multi-scope direct BIND          = VETO → CLARIFY
single-scope exact current-lens  = ALLOW
invented/unapproved bind         = BLOCK
frozen corpus changes            = 0
next proof                       = exact same EV-01..04 Luna/Sol rerun
```
