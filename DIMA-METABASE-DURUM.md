# DIMA + METABASE — LIVING STATUS

## CURRENT AUTHORITY SNAPSHOT — 2026-09-25

> **FORWARD AUTHORITY.** This block overrides any older "current", "next", "blocked", or
> "immediate work" language later in this living document. Older sections remain historical
> evidence only unless they explicitly say they are current under DMP-DEC-0048.

```text
authoritative implementation checkpoint = 01140b059318b2487b002a0c94f989fd693ce6f2
branch                              = feat/dima-metabase-platform
forward authority                   = DMP-DEC-0048
engine gitlink                      = cbe313af9ac2d5960f662068e433d328d896fb06
engine release                      = 0.63.18-dima.6
engine certification                = 36042062775 SUCCESS
engine digest                       = sha256:40e9a44be49904de3ddf12d4683c768e70955851c10a928a9c8f7d8f60780353

P14 final provider-free             = 36102734433 SUCCESS
P14 final governance                = 36102734425 SUCCESS
P14 real native-direct Luna canary  = 36100443464 SUCCESS
second paid P14 model run           = 0

CURRENT SEALED PHASE                = P14 NATIVE-DIRECT RESEARCH
CURRENT OPEN PHASE                  = P15 NATIVE METABASE EXPLORATION
P16                                 = NEXT AFTER P15 GREEN
UI / UX                             = FORBIDDEN UNTIL P21 SEALED
```

Permanent ownership:

```text
METABASE + METABOT
= analytics cognition + exploration + analytical semantics
+ native permissions + query construction/repair + execution

DIMA
= business context + Research + lineage + epistemic state
+ claims + hypotheses/root cause + reports
+ decisions + actions + outcomes + memory
```

```text
METABASE PROVES THE ANALYSIS.
DIMA PROVES THE LINEAGE, EPISTEMIC STATE, AND DECISION CONTEXT.
```

### P14 is CLOSED

P14 is not a place for more trust middleware. The sealed product hot path is:

```text
Research obligation
→ same principal-scoped native Metabot session
→ capture exact query A
→ persist query A/fingerprint
→ direct native Metabase /api/dataset execution ONCE
→ persist result/runtime/subject provenance
→ one DimaQueryReceipt(authority_kind=research_material)
→ Evidence
→ Research state
```

Durability is fail-closed:

```text
EXECUTED + persisted result
→ resume from persisted result
→ same deterministic receipt
→ NO second /api/dataset call

EXECUTION_STARTED + no persisted result
→ UNKNOWN OUTCOME
→ NO BLIND RETRY
→ explicit limitation/recovery path
```

Do not restore mandatory P13 attestation/re-execution, P10 synthetic Research access facts,
operator-level MBQL/resource validation, Standard projection hashes, Wren/raw-SQL/Agent-API fallback,
shared admin/service analytical sessions, or any second analytics/security/receipt authority.

P13 remains sealed beside the product path as a **CERTIFICATION / DEBUG / FORENSICS microscope**.

### Forward phase chain

```text
P14 Research                  SEALED
→ P15 native Exploration      OPEN NOW
→ P16 claim-lineage Evidence
→ P17 Research reasoning
→ P18 material business relationship policy
→ P19 Hypothesis / Root Cause
→ P20 ReportDocument
→ P21 DecisionBrief
→ only then UI/UX architecture
```

Every phase consumes the authority produced below it. No disconnected subsystem and no parallel truth
owner.

### Next bounded objective — P15

Use pinned native Metabase capability. Current source audit identifies the first provider-free vertical
as the native X-Ray / automagic ad-hoc analysis surface over the exact P14-captured query, under the
same authenticated native subject. Dima may persist only Research-material provenance/lead identity.

P15 must not implement Python interestingness, variants, Top-N, temporal exploration, query repair,
join planning, or an analytical scorer. Native "interesting" output remains **RESEARCH_MATERIAL**;
it is not a VERIFIED Dima claim. P16 owns claim/Evidence promotion.

### Current STOP conditions

Stop for supervisor only if one of these becomes concrete:

- Metabot/QP/Lib/driver/core engine modification is necessary;
- principal-scoped native security cannot be preserved;
- native permission enforcement is insufficient for a real Dima-specific policy;
- a second analytical, security, or receipt authority appears necessary;
- silent wrong can enter trusted claim/finding/decision state;
- destructive semantic migration is required;
- large paid evaluation is required;
- a phase cannot consume prior-phase authority without a parallel system.

Otherwise continue through the core chain. Do not return to UI work before P21.

---

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


---

## P11 INITIAL NATIVE PATH — GREEN

```text
implementation SHA                  = d31b83437400dd7f1b70e1b478efad2e8cff781e
P11 workflow                        = 35790011788 = SUCCESS
provider-free                       = GREEN
live Luna/Sol                       = GREEN
M1/Wren                             = 35790011932 = SUCCESS
governance                          = 35790011855 = SUCCESS
corpus fingerprint                  = da7f13e804c643c376d085b0e0fa94e132fdd8877e1945e4c19257160d03e06c
raw Luna first-pass                 = 3/4
raw Sol first-pass                  = 3/4
official Luna first-pass            = 4/4
official Sol first-pass             = 4/4
raw silent-wrong rerun              = 6
official silent-wrong               = 0
guardrail                           = SUFFICIENT
resolver decision                   = NOT_NEEDED
entity resolver framework           = 0
translation/fuzzy/morphology        = 0
EV-05 high-cardinality              = UNCERTIFIED / FIXTURE REQUIRED
EV-06 stale index                   = UNCERTIFIED / FIXTURE REQUIRED
EV-07 permission-hidden             = UNCERTIFIED / P10B2 OWNER REQUIRED
DMP-P5-BLOCK-001                    = OPEN
```

P11 V1 proves that native current-user Metabase value retrieval + LLM cognition + the minimum Dima
value-adoption truth gate is sufficient for the initial low-cardinality profile. It does **not** claim
full entity-value resolution certification.

DMP-P11-CI-RED-001 is a separate stale M2 cross-trigger correction.


---

## P11 final correctness hardening candidate

```text
audited base HEAD                 = 91333d39e63c245b637a4d2be2e49a5a227271c7
DMP-P11-AUDIT-003                = CORRECTION APPLIED
DMP-P11-AUDIT-004                = CORRECTION APPLIED
P11 focused CI                    = necessity contract + product gate
scalar equality                   = SAME TYPE + SAME VALUE
model-visible contract changed    = NO
Luna/Sol rerun                    = NOT REQUIRED
DMP-P11-INTEGRATION-005           = OPEN / P13 OWNER
EV-05/06/07                       = UNCERTIFIED / UNCHANGED
resolver framework                = 0
```

P11 V1 is not reopened architecturally; this candidate closes two proof/correctness gaps only.


---

## P11 FINAL V1 CLOSURE — GREEN

```text
closure SHA                       = 9de113b779ebd261b1d0b14ba58c893b79d145b2
P11 provider-free                 = 35816344869 = SUCCESS
P11 focused exact count           = 16 PASS
governance                        = 35816344862 = SUCCESS
M1/Wren                           = 35816344966 = SUCCESS
Luna/Sol rerun                    = SKIPPED / NOT REQUIRED
DMP-P11-AUDIT-003                 = CLOSED GREEN
DMP-P11-AUDIT-004                 = CLOSED GREEN
typed scalar equality             = SAME TYPE + SAME VALUE
DMP-P11-INTEGRATION-005           = OPEN / P13 OWNER
EV-05 / EV-06 / EV-07             = UNCERTIFIED
resolver framework                = 0
```

Certified wording:
**P11 INITIAL LOW-CARDINALITY NATIVE PATH GREEN**.

---

## P12 workspace feasibility — OPENED

```text
Fast Track observed reference      = 3fc686c9fa4f86927a5ea51f43cf688b9c010a6c
ask-v2 observed reference          = 3d807ee2698733ea01620e5ce6c85e88466b785a
source disposition                 = REFERENCE ONLY
initial UX mode                    = DIMA_SHELL + HEADLESS_API
workspace escape hatch             = LINK_OUT
EMBED                               = OPTIONAL FUTURE ESCALATION
Metabase UI object as truth         = FORBIDDEN
P12 integration code                = NOT STARTED
```

**Current phase:** P12 BI WORKSPACE FEASIBILITY / CLASSIFICATION.  
P13 production Standard seam remains the next integration owner after P12 classification.


---

## DEVELOPER HANDOFF SNAPSHOT

Authoritative context-reset handoff:

```text
DIMA-METABASE-HANDOFF.md
```

Audited functional baseline used by the handoff:

```text
4b60bc3f1e6ab9526cd590a0989c1b227c5c43be
```

Proof at that baseline:

```text
P11 workflow                      = 35816646368 = SUCCESS
governance                        = 35816646416 = SUCCESS
P11 focused exact count           = 16 PASS
P11 certified scope               = INITIAL LOW-CARDINALITY NATIVE PATH GREEN
P11 resolver framework            = 0
DMP-P11-INTEGRATION-005           = OPEN / P13 OWNER
EV-05 / EV-06 / EV-07             = UNCERTIFIED
DMP-P5-BLOCK-001                  = OPEN
P12 mode                          = DIMA_SHELL + HEADLESS_API
P12 escape hatch                  = LINK_OUT
P12 integration code              = NOT AUTHORIZED / NOT STARTED
next integration owner            = P13 Production Standard
```

Moving-source observations at handoff preparation:

```text
ask-v2                            = 80e2e101298cfb750231b4161b9e888e65323a04
Fast Track                        = 946cb933441381078941767e8ac6205349ff81e3
disposition                       = REFERENCE ONLY
merge/cherry-pick/rebase          = FORBIDDEN
```

The documentation handoff commit is not a new product-code baseline.

**Current phase:** P12 BI WORKSPACE FEASIBILITY / CLASSIFICATION.  
**Next real integration owner:** P13 Production Standard seam after deliberate P12 closure.


---

## NEW DEVELOPER TAKEOVER — P12 CLOSURE / P13 PREDEVELOPMENT BOUNDARY

```text
takeover read HEAD                  = 56799687d2a8018dd60b0b909fb8b0be5d4a79c7
audited functional baseline         = 4b60bc3f1e6ab9526cd590a0989c1b227c5c43be
baseline P11 workflow               = 35816646368 = SUCCESS
baseline governance                 = 35816646416 = SUCCESS
handoff governance                  = 35817394598 = SUCCESS
ask-v2 moving observation           = d430680a02256f4b9612730bd79b2e938a134132
Fast Track moving observation       = 5280dd37451ded59ce181b93b015bc9dfafe0696
source writes/merge/cherry-pick     = 0
product code changed by takeover    = 0
```

### P12

Decision receipt:
`DMP-DEC-0028`.

Certified wording:
```text
P12 BI WORKSPACE FEASIBILITY = CLOSED / CLASSIFICATION GREEN
```

Composition:
```text
DIMA_SHELL + HEADLESS_API
LINK_OUT = mature workspace escape hatch
EMBED    = deferred / measured escalation only
```

P12 workspace/frontend integration remains unimplemented by design.

### P13

Predevelopment review:
`backend/belgeler/metabase/predev/P13_PREDEVELOPMENT_REVIEW.md`.

Ticket:
`backend/belgeler/metabase/tickets/P13_PRODUCTION_STANDARD_VERTICAL.md`.

Sequencing decision:
`DMP-DEC-0029`.

Current phase:
```text
P13 PRODUCTION STANDARD — PREDEVELOPMENT SEALED
P13 PRODUCT CODE — NOT AUTHORIZED PENDING SUPERVISOR REVIEW
```

Binding design:
```text
ResolvedAnalyticsIntent
→ PREPARE ONCE
→ exact frozen CanonicalProjection
→ P10 authorize exact prepared artifact
→ ExecutionAccessSnapshot
→ EXECUTE SAME PREPARED ARTIFACT
→ strict QueryReceipt
→ VERIFIED Evidence
```

P13C owns `DMP-P11-INTEGRATION-005`; it remains OPEN.
`DMP-P5-BLOCK-001`, EV-05/06/07, P10B2 advanced gaps, P9 transport gaps and P7/P8 semantic gaps all
remain OPEN/typed exactly as before.


---

## P12X OPENED — METABASE NATIVE ENGINE / FORK SEAM EVALUATION

```text
opening Platform HEAD               = ef56f6d53ebe9399a9ab322a890c6a23c5cd5c01
DMP-DEC-0030                        = SEALED
P13                                 = PAUSED FOR METABASE SEAM DECISION
P13 product code                    = 0 / STOPPED
P12X initial scope                  = V0 + A + B
Seam C / fork                       = NOT AUTHORIZED
Seam D / Dima hooks                 = NOT AUTHORIZED
Boyahane fixture SHA                = f0c4a6b053ead52ca2eac80002c448323dc34a35
Boyahane expected tables            = 80
Boyahane expected rows              = 462962
Boyahane compose image              = metabase/metabase:latest / UNPINNED
pinned control                      = v0.63.18
pinned control image                = sha256:1160b570cb11c107bce00e71293552df8a8363e01a32c2c7a048cee002dc8a73
ask-v2 moving observation           = d8759c9cfe388560084a2886dd443c32c6346788
Fast Track moving observation       = 30659f7892ce2d4eafffec89716b75e2ce09ea48
source writes/merge/cherry-pick     = 0
```

Next:
freeze dataset/runtime/corpus/oracle, then run lab-only V0+A+B benchmark and stop at the supervisor checkpoint.


---

## P12X first native canary — RED CLASSIFIED

```text
tested SHA                         = 2fdad83dcb844c8288293a9c6f39f89cf9cd365e
P12X workflow                     = 35821554136 = SUCCESS infrastructure
native canary job                 = 107054430015 = SUCCESS transport
PX-01 oracle                      = 126
native executed result            = 264
selected database                 = Sample Database / OUT OF BENCHMARK SCOPE
Boyahane catalog                  = PRESENT / SEARCHABLE
restricted Metabot permissions    = ALL YES
provider/tool stream errors       = 0
classification                    = ORACLE_FIXTURE / DATA-SCOPE CONTAMINATION
receipt                           = DMP-P12X-CANARY-RED-001
product-code changes              = 0
```

Authorized next action: disable bundled sample content **only in the P12X lab fixture** and rerun the
same canary. No architecture conclusion may be drawn from this RED.


---

## P12X current-corpus proof audit

```text
receipt                     = DMP-P12X-AUDIT-002
opening SHA                 = 13cb9747da80fad820b6fb62f9dc0059808c7655
clean prior native canary   = 6a19c279... / 35821886266 GREEN
prior corpus fingerprint    = b05bc01b1e8b41cc9dbd8c475058accc1cb39af2bdfe62f6dad17cfb78a15233
current corpus fingerprint  = fd6e5934438795f64e9ec7d64b74b56056c3c1304aa51598d18c170839b792a0
classification              = ORACLE_FIXTURE / CURRENT-CORPUS PROOF IDENTITY DRIFT
P13                         = PAUSED UNTIL FORK CAPABILITY PARITY + STABLE ENGINE BRIDGE
fork bootstrap              = BLOCKED ON CURRENT-HEAD PX-01 EXECUTABLE ORACLE GREEN
```

Authorized next action: add the lab-only executable PX-01 scorer and rerun exactly one native canary.


### P12X executable-oracle first RED

```text
tested SHA        = d17c7dac487d327070a4ebe69583d17cb9569dc0
workflow          = 35824180896
native selection  = CORRECT BOYAHANE RESOURCE
response prefix   = rows:[[126]]
scorer            = RED
classification    = ORACLE_FIXTURE / HARNESS RESULT-CAPTURE CONTRACT
owner             = backend/lab/metabase/p12x/native_probe.py
product patch     = 0
```

Only the 202-success capture contract is authorized for correction.


---

## P12X NATIVE SANITY GATE GREEN / THIN ENGINE FORK PATH OPEN

```text
native proof SHA                   = e35b68e4b7f60fc46c677317e7a001a1d66e88ac
workflow                           = 35824464298 = SUCCESS
native canary job                  = 107063206949 = SUCCESS
artifact                           = 10734247411
current corpus fingerprint         = fd6e5934438795f64e9ec7d64b74b56056c3c1304aa51598d18c170839b792a0
PX-01 resource                     = Dima Analytics Lab / public / satis_siparisleri
PX-01 observed                     = 126
PX-01 oracle                       = 126
provider/tool errors               = 0
DMP-P12X-AUDIT-002                 = CLOSED GREEN
DMP-DEC-0031                       = SEALED
full V0+A+B bake-off               = DEFERRED / NOT FORK-BLOCKING
P13                                = PAUSED UNTIL FORK CAPABILITY PARITY + STABLE ENGINE BRIDGE
Fast moving observation            = ac05a20452027314a8b092cf128a4e09c23a2a40
ask-v2 moving observation          = 11b59a0928af1104ea1552352dac2184ba4e5af0
source branch writes/merge/rebase  = 0
```

Authorized next sequence:
```text
P12X-C0 exact upstream-history fork bootstrap/source build
→ P12X-C1 stock-vs-fork native capability parity
→ P12X-C2 stable Dima bridge + bridge/native parity
→ P12X-C3 upstream-sync / DIMA_PATCH_SURFACE certification
→ STOP / supervisor checkpoint
```

P13 governance hooks remain unauthorized.


### P12X-C0 provisioning state

```text
DMP-P12X-C0-BLOCK-001           = OPEN / REPOSITORY_PROVISIONING
required repo                   = UpcyTech/dima-metabase-engine
repo exists                     = NO
old UpcyTech/dima-metabase      = UNTOUCHED / FORBIDDEN SUBSTITUTE
Platform bootstrap kit          = PRESENT @ backend/lab/metabase/engine_bootstrap/
remote C0 bootstrap             = WAITING ONLY FOR CREATE/FORK CAPABILITY
P13                             = PAUSED
```


---

## P12X-C0 fork provisioning GREEN / source-build environment RED classified

```text
engine repo                    = UpcyTech/dima-metabase-engine
fork parent                    = metabase/metabase
immutable base                 = 2ba2485c78d7e00a9a25f82c00fc201da71590c4
engine overlay commit          = b284739d582ce6743c17cc688a04845bfd1e30b5
modified upstream files        = 0
deleted upstream files         = 0
upstream line delta            = +0 / -0
DMP-P12X-C0-BLOCK-001          = CLOSED GREEN
first C0 workflow              = 35826126089 = RED
RED classification             = BUILD_ENVIRONMENT / upstream Bullseye package mirror 404
engine/source regression       = NO EVIDENCE
manual unchanged retry         = 35826362027 / IN PROGRESS
P13                            = PAUSED
```


---

## P12X-C0 GREEN

```text
engine SHA                  = 9fb21da0177935aff5882472577c8e14a67ebd65
workflow                    = 35827292630 = SUCCESS
source build                = PASS
smoke health                = PASS
upstream source files mod   = 0
upstream line delta         = +0 / -0
image                       = ghcr.io/upcytech/dima-metabase-engine:0.63.18-dima.0
digest                      = sha256:674d1ac4a929b95ab476bcdf37baa43099b398c444bc3f53fef404318892554b
P12X-C0                     = CLOSED GREEN
next                        = P12X-C1 stock-vs-fork native capability parity
P13                         = PAUSED
```


---

## P12X-C0 COMPLETE / C1 ACTIVE

```text
C0 engine HEAD                    = 9fb21da0177935aff5882472577c8e14a67ebd65
C0 workflow                       = 35827292630 = SUCCESS
C0 artifact                       = 10736021635
fork image digest                 = sha256:674d1ac4a929b95ab476bcdf37baa43099b398c444bc3f53fef404318892554b
modified upstream files           = 0
upstream line delta               = +0 / -0
source build                      = GREEN
smoke /api/health                 = GREEN
GHCR push                         = GREEN
P12X-C0                           = CLOSED GREEN
P12X-C1                           = ACTIVE / stock-vs-fork native parity
P13                               = PAUSED
```

C1 must use immutable stock and fork image digests, the frozen Boyahane snapshot, the same restricted
principal and Luna provider/model. Closure still requires 100% retention of stock-PASS tasks, zero new
silent wrong, zero permission regression and zero dataset-scope drift.


---

## Engine workspace integration — fork is now inside Platform as an exact gitlink

```text
Platform path       = engine/metabase
dependency type     = Git submodule / gitlink
engine repository   = UpcyTech/dima-metabase-engine
engine parent       = metabase/metabase
pinned engine SHA   = 6bb6924452e5b9dc42b3745bb88c3125a468b297
source vendoring    = 0
subtree copy        = 0
moving-ref runtime  = forbidden
```

Development ownership is now explicit:

```text
ENGINE CHANGE
→ commit/test in UpcyTech/dima-metabase-engine
→ exact engine SHA
→ update Platform engine/metabase gitlink
→ Platform integration/governance proof
```

This preserves upstream history and syncability while making the engine a first-class component of the
Dima Platform workspace.


---

## P12X-C1 initial run GREEN but divergence repeat required before seal

```text
initial canonical workflow         = 35828372103 = SUCCESS
artifact                           = 10736593524
artifact digest                    = sha256:57c0e3c07ceb69480b3b0f27c7480b495dff3a949e0a50851a8437ab04e31d3a
initial stock PASS                 = 4 / 6
fork retained stock-PASS           = 4 / 4 = 100%
new silent wrong                   = 0
permission regression              = 0
dataset-scope drift                = 0
material divergence                = PX-13, PX-16 (stock wrong / fork correct)
C1 seal                            = HELD
reason                             = supervisor protocol requires 2 extra repeats per divergent case
engine Platform gitlink            = 6bb6924452e5b9dc42b3745bb88c3125a468b297
runtime-source delta vs C0 SHA     = no Metabase runtime source changes
```

The canonical C1 scorer/workflow is upgraded to discover material divergence and rerun only those cases
twice on both stock and fork with prompt/data/model/principal unchanged. C1 is sealed only after the
bounded repeat stage proves no stock-PASS/fork-FAIL regression, no new silent wrong, no permission
regression and no dataset-scope drift.


---

## Engine submodule governance sealed

```text
decision              = DMP-DEC-0032
Platform path          = engine/metabase
remote                 = UpcyTech/dima-metabase-engine
dependency form        = mode 160000 gitlink
current pinned SHA     = 6bb6924452e5b9dc42b3745bb88c3125a468b297
source vendoring       = 0
subtree copy           = 0
moving-ref consumption = forbidden
```

Every audited engine change now requires an explicit Platform gitlink bump.


### Engine-submodule governance CI RED classified

```text
tested SHA      = 79c9d5a9e776680be5c2e24d7070e52eb1706258
workflow        = 35830303270
classification  = CI/GOVERNANCE / WORKFLOW SERIALIZATION
submodule state = no evidence of defect
C1 live run     = untouched
owner           = governance YAML only
```


### P12X-C1 run 35830152880 RED classified

```text
failure point       = PX-13 / stock native stream
exception           = httpx.ReadTimeout
scorer reached      = NO
fork regression     = NO EVIDENCE
classification      = TRANSPORT_RUNTIME / BENCHMARK_HARNESS_FAIL_FAST
owner               = C1 lab harness/workflow only
corrective rule     = persist candidate-level failure artifact, then continue to divergence scoring
C1 seal             = HELD
C2 implementation   = STOP
```


---

## P12X-C1 CLOSED GREEN / C2 AUTHORIZED

```text
C1 frozen run                       = 35831869602
C1 corrected no-model rescore       = 35834874194 = SUCCESS
reproducible fork regression        = 0
reproducible new silent wrong       = 0
reproducible permission regression  = 0
reproducible dataset-scope drift    = 0
stochastic variance cases           = PX-01, PX-03, PX-06, PX-16
P12X-C1                              = CLOSED GREEN
P12X-C2                              = AUTHORIZED
P13                                  = PAUSED
```


---

## P12X-C3 CLOSED GREEN

```text
engine certified HEAD              = c56b71ab23bf2a2d266bac2fba8d165ac059d613
sync self-test                     = 35835881375 = SUCCESS
artifact                           = 10739391786
candidate-only                     = PASS
source build                       = PASS
main auto-promotion                = 0
sync conflicts in self-test        = 0
modified upstream files            = 0
upstream-owned line delta          = +0 / -0
Platform engine gitlink target     = c56b71ab23bf2a2d266bac2fba8d165ac059d613
P12X-C3                            = CLOSED GREEN
```

C2 remains the only open P12X closure gate.


---

## P12X-C2 CLOSED GREEN / SUPERVISOR CHECKPOINT REACHED

```text
C2 proof SHA                         = 094b5f6e0f1be939172b95fde66cab055c66ae54
C2 workflow                          = 35839639339 = SUCCESS
C2 artifact                          = 10742000058
artifact digest                      = sha256:c799261cd36499c7579bdf1d6f97ecc07ce0cfaab782afe861deef169d877d94
engine gitlink                       = c56b71ab23bf2a2d266bac2fba8d165ac059d613
restricted-user canary               = GREEN
PX-01                                = 126 == 126
selected parity cases                = PX-01 / PX-07 / PX-13 / PX-16
divergence repeated                  = PX-07 / PX-13 / PX-16
repeat count                         = 2 per side
reproducible bridge regression       = 0
reproducible bridge silent wrong     = 0
reproducible permission regression   = 0
reproducible dataset-scope drift     = 0
bridge transport contract failures   = 0
Agent API analytical fallback        = 0
Wren fallback                        = 0
raw SQL fallback                     = 0
P12X-C2                              = CLOSED GREEN
```

### P12X sequence

```text
C0 exact fork/source build            = CLOSED GREEN
C1 stock-vs-fork native parity         = CLOSED GREEN
C2 stable bridge/direct-native parity  = CLOSED GREEN
C3 upstream-sync/patch-surface         = CLOSED GREEN
```

Current architecture:
```text
Dima control plane
→ typed native engine bridge
→ pinned UpcyTech/dima-metabase-engine submodule
→ native Metabot stack
→ customer DB
```

Current stop:
```text
SUPERVISOR CHECKPOINT = REACHED
P13 PRODUCT CODE      = NOT AUTHORIZED
```

Before any P13 implementation, the P13 predevelopment/ticket must be re-read and revised for the
certified native-engine bridge. Do not mechanically continue the old Agent-API execution seam.


---

# FINAL PRE-P13 HANDOFF STATUS

```text
Platform HEAD at handoff           = 9179ad880ff0376fed0bb83971c9d61fe87e735c
functional proof SHA               = 094b5f6e0f1be939172b95fde66cab055c66ae54
governance                         = 35841686789 = SUCCESS
P12X regression                    = 35841687850 = SUCCESS

C0                                 = CLOSED GREEN
C1                                 = CLOSED GREEN
C2                                 = CLOSED GREEN
C3                                 = CLOSED GREEN

engine gitlink                     = c56b71ab23bf2a2d266bac2fba8d165ac059d613
engine main                        = c56b71ab23bf2a2d266bac2fba8d165ac059d613
upstream base                      = 2ba2485c78d7e00a9a25f82c00fc201da71590c4

ask-v2 moving observation          = d22fb3626db0fe44ea543eee6531e5544cdf0b56
Fast Track moving observation      = 8b9397b4f883f9c188a5fdadafa3db0dc418ec34
source-branch write/merge/rebase   = 0

repo handoff readiness             = READY
P13 product code                   = NOT STARTED
next legal action                  = fresh P13 predevelopment reconciliation
```

Do not mechanically resume the historical P13 Agent-API-oriented ticket.
See DMP-DEC-0035 and the final section of `DIMA-METABASE-HANDOFF.md`.


---

## P13 NATIVE-ENGINE TAKEOVER — NORMATIVE RECONCILIATION

```text
read HEAD                         = 6a74994b9f968a1c3c318456832d0b68b321d202
functional P12X proof             = 094b5f6e0f1be939172b95fde66cab055c66ae54
engine gitlink                    = c56b71ab23bf2a2d266bac2fba8d165ac059d613
Fast Track observation            = 8b9397b4f883f9c188a5fdadafa3db0dc418ec34
ask-v2 latest read-only observation = 6f163d10aa760a69a196c74a5cc23aa2a2671a73
merge/cherry-pick/rebase/write    = 0
```

DMP-DEC-0036 seals the current precedence:
```text
native Metabot = cognition/query candidate author
Dima           = business + execution/security/provenance/evidence truth
Metabase QP    = executor
```

New current P13 docs:
- `backend/belgeler/metabase/predev/P13_NATIVE_ENGINE_TRUST_BOUNDARY_REVIEW.md`;
- `backend/belgeler/metabase/tickets/P13_NATIVE_ENGINE_STANDARD_VERTICAL.md`.

Historical P13 Agent-API documents remain for evidence only.

Next gate:
`normative-doc governance repin → P13A provider-free implementation`.


---

## P13A NATIVE TRUST CONTRACT — CLOSED GREEN

Certified wording:
```text
P13A NATIVE TRUST CONTRACT = GREEN
```

Product implementation commit:
`17dea824dddf8af185d9596abc5bfdbedd11e04a`

CI/governance guard closure:
`c7a95fe4c48687914b89c350b8130793467c36e6`

Evidence:
```text
P13A native trust workflow   35846503106 = SUCCESS
  focused P13A               12 PASS
  P5 + P10 critical          61 PASS
  P12X C2 bridge              7 PASS

P10 regression              35846797870 = SUCCESS
P5 regression               35846797938 = SUCCESS
governance                  35846797967 = SUCCESS
M1 regression               35846503059 = SUCCESS
```

Implemented:
- `NativeQueryCandidate` exact native pMBQL occurrence contract;
- exact candidate artifact fingerprint = deterministic serialization of the exact execution artifact,
  not semantic equivalence;
- bounded `ALLOW | CLARIFY_REPLAN | BLOCK` authorization gate for the P13A one-metric/one-source
  surface;
- `AuthorizedExecutionArtifact` engine-independent trust identity;
- exact-artifact mutation/substitution hard-fail;
- P10 `ExecutionAccessSnapshotIssuer` generalized to the common execution-resource identity without
  weakening principal/tenant/role/semantic-context/source checks;
- P5 `DimaQueryReceiptSealer` generalized to the same common execution identity without creating a
  second receipt system;
- historical `CanonicalProjection` remains supported through a compatibility adapter;
- P13-aware CI isolation guards preserve milestone ownership.

Exact engine remains:
```text
engine repo    = UpcyTech/dima-metabase-engine
Platform path  = engine/metabase
gitlink        = c56b71ab23bf2a2d266bac2fba8d165ac059d613
upstream base  = 2ba2485c78d7e00a9a25f82c00fc201da71590c4
runtime        = v0.63.18-dima.0
engine changes during P13A = 0
```

Engine identity source-review conclusion:
- current runtime properties expose tag + upstream build's seven-character git hash;
- P12X C2 was safe because CI externally pinned exact source/image;
- that surface alone is not enough for long-term P13B exact source+image attestation;
- P13A therefore made no engine patch;
- before P13B choose/certify either deployment/runtime exact source+immutable-image attestation or a
  minimal isolated Dima engine-identity endpoint/build manifest.

Explicitly NOT proven:
```text
P13 STANDARD = GREEN                         NO
production security = GREEN                  NO
native analytics absolute correctness = GREEN NO
P13B live vertical = authorized              NO
```

Still OPEN:
- `DMP-P5-BLOCK-001`;
- `DMP-P11-INTEGRATION-005` (P13C owner);
- EV-05 / EV-06 / EV-07;
- P10B2 RLS / CLS / impersonation / advanced routing / cache-result reauthorization;
- P9 dimension / time / relationship transport gaps;
- P7/P8 calculated / relationship / view semantic gaps;
- historical Wren typed gaps;
- P13B engine runtime exact source+image attestation decision.

STOP:
```text
P13B = NOT AUTHORIZED
```


---

## P13B-0 SOURCE AUDIT + PREDEVELOPMENT — SEALED

```text
audit Platform HEAD             = 86faaa339b75d261e31da1dd0dec8939f58620e6
engine gitlink/main             = c56b71ab23bf2a2d266bac2fba8d165ac059d613
upstream exact source audited   = 2ba2485c78d7e00a9a25f82c00fc201da71590c4
Fast Track observation          = 8b9397b4f883f9c188a5fdadafa3db0dc418ec34
ask-v2 observation              = b069b1cdce097f7ce02c055a2614d8f990b1eb3f
source-branch writes            = 0
engine changes                  = 0
gitlink bump                    = 0
```

DMP-DEC-0037 is the P13B predevelopment authority.

Closed design decisions:
- exact native query provenance comes from server-side native conversation/query state;
- query facts are observed inside Metabase using Lib/QP, not parsed recursively in Python;
- a bounded `NativeExecutionManifest` is required;
- existing public surfaces are insufficient for that typed manifest;
- future engine patch is therefore required, but is **not authorized in P13B-0**;
- runtime identity chooses a minimal isolated Dima identity seam rather than relying on the current
  P12X lab pin alone;
- exact same-artifact execution seam is `POST /api/dataset`;
- first vertical is PX-01, June 2026 sales-order count, independent oracle = 126;
- future live Platform orchestration owner is `backend/app/v3/native_standard/`;
- governance now quarantines that future owner from historical Agent-API analytical dependencies.

Current blockers:
```text
DMP-P13B-BLOCK-001 = DESIGN SEALED / IMPLEMENTATION OPEN
DMP-P13B-BLOCK-002 = DESIGN SEALED / IMPLEMENTATION OPEN
```

Current stop:
```text
P13B NATIVE ATTESTATION DESIGN = SEALED
P13B IMPLEMENTATION = PENDING SUPERVISOR AUTHORIZATION
```


---

## P13B-0 CLOSURE PROOF

Predevelopment/governance commit:
`90c6da7d5bf50c305f4d91c02263660bf8b9232a`

Governance:
`35852118661 = SUCCESS`

Verified after push:
```text
changed files                    = docs/governance only
product-code changes             = 0
engine-source changes            = 0
engine gitlink bump              = 0
engine gitlink                   = c56b71ab23bf2a2d266bac2fba8d165ac059d613
ask-v2/Fast Track writes         = 0
live P13B orchestration          = 0
```

Certified closure wording:
```text
P13B NATIVE ATTESTATION DESIGN = SEALED
P13B IMPLEMENTATION = PENDING SUPERVISOR AUTHORIZATION
```


---

## NEW DEVELOPER HANDOFF CHECKPOINT

Consolidated onboarding file:

DIMA-METABASE-NEW-DEVELOPER-HANDOFF.md

State verified immediately before this handoff commit:

    Platform HEAD        = b9bcc110e4d352a3bada7587e7a812abf7b68ed3
    governance           = 35852421592 SUCCESS
    engine gitlink/main  = c56b71ab23bf2a2d266bac2fba8d165ac059d613
    ask-v2 observation   = 1cdddb024fd0d8f4e5548cd7ca862afc3b3ee404
    Fast Track           = 8b9397b4f883f9c188a5fdadafa3db0dc418ec34

No product or engine code is changed by this handoff.

Current authoritative stop:

    P13A NATIVE TRUST CONTRACT = GREEN
    P13B NATIVE ATTESTATION DESIGN = SEALED
    P13B IMPLEMENTATION = PENDING SUPERVISOR AUTHORIZATION

Next developer must read the consolidated handoff before any write.


---

## NEW-DEVELOPER HANDOFF PUBLISH PROOF

    onboarding/handoff commit = e40cdbf8eebf0aad393a292ec1b10ce03ff5a9c2
    governance                = 35853381889 SUCCESS
    product-code changes      = 0
    engine-source changes     = 0
    engine gitlink bump       = 0
    source-branch writes      = 0

The handoff package is therefore governance-certified.

Current stop remains unchanged:

    P13B NATIVE ATTESTATION DESIGN = SEALED
    P13B IMPLEMENTATION = PENDING SUPERVISOR AUTHORIZATION

---

## P13B-1 ENGINE NATIVE ATTESTATION + IDENTITY — GREEN

Certified engine promotion:

```text
engine repo       = UpcyTech/dima-metabase-engine
engine main SHA   = 3ac50a0ad1c2fb53d538c9fccf621db816c305e1
upstream base     = 2ba2485c78d7e00a9a25f82c00fc201da71590c4
release           = 0.63.18-dima.1
revision          = 1
semantic changes  = 0
P13B engine run   = 35876198926 = SUCCESS
```

Authoritative deterministic gates on the exact promoted SHA:

```text
focused P13B tests = SUCCESS
source build/smoke = SUCCESS
patch surface      = SUCCESS
certification      = SUCCESS
```

Thin-fork invariant remains:

```text
modified pre-existing upstream runtime files = 1
src/metabase/api_routes/routes.clj
```

P13B-1 closes the two implementation blockers at the engine boundary:
- server-side native query occurrence attestation now supplies observed physical/query facts;
- exact repository/SHA/upstream/release/build/image/instance identity is available for Platform binding.

No Metabot cognition, prompt/profile/skill, query-construction/repair, Query Processor semantic, or
driver behavior was changed.

The successful full C1 evidence from exact candidate
`78b8ee66464435daece5a8e3b4cffce5a77937c3` is retained as the P13B pre-promotion native
capability baseline. Non-cognition release/trust changes do not trigger another routine full C1.

Current phase:

```text
P13B-1 ENGINE NATIVE ATTESTATION + IDENTITY = GREEN
P13B-2 PLATFORM TRUST INTEGRATION            = OPEN / AUTHORIZED
P13B-3 PINNED-LIVE PX-01                     = NOT STARTED
```

Platform engine gitlink is promoted in the same checkpoint to:

`3ac50a0ad1c2fb53d538c9fccf621db816c305e1`

P13B-2 is provider-free. Its owner is:

`backend/app/v3/native_standard/`

It may orchestrate trust only. It may not plan analytics, parse general MBQL, repair/rewrite queries,
generate SQL, or reopen Agent API/Wren analytical fallback.



---

## 2026-09-23 — P13B DIMA.3 SEMANTIC-METRIC HANDOFF CHECKPOINT

This section supersedes the earlier P13B-1/P13B-2-open checkpoint above.

Exact current state at handoff preparation:

```text
Platform HEAD                    = 2ea02530fbaa2999d1dac1d6166064e49bd8f51c
engine main                      = 10960f7c36bb84425b1794b557b78211c14d7f5f
Platform engine gitlink          = 10960f7c36bb84425b1794b557b78211c14d7f5f
engine release                   = 0.63.18-dima.3
upstream base                    = 2ba2485c78d7e00a9a25f82c00fc201da71590c4

engine P13B certification        = 35909836120 SUCCESS
governance                       = 35911051608 SUCCESS
provider-free semantic availability = 35911051644 SUCCESS
P13B provider-free current HEAD  = 35914038368 SUCCESS
```

Decisive prior live RED:

```text
run      = 35895585715
engine   = 0.63.18-dima.2 / 05fccf3595623a41886cb2a7a89192636580324e
model    = openrouter/openai/gpt-5.6-luna
owner    = dima-trust-authorization
error    = NATIVE_AGGREGATION_MISMATCH
observed = DISTINCT(field)
required = COUNT(*)
```

Interpretation:
- Dima trust behaved correctly and blocked the wrong query;
- root cause was missing canonical Dima metric availability to native Metabot, not a need to weaken
  authorization;
- P9/P9B is now reused to provision `metric.sales_order_count` as a DIMA_MANAGED native Metabase
  metric;
- provider-free proof now verifies restricted discoverability/readability, exact persisted metric
  definition, stable native identity and `ManagedResourceBinding`;
- engine dima.3 now attests native metric identity and uses Metabase QP metric expansion as an
  observation view while preserving original pMBQL as execution identity;
- Platform trust binds that native identity back to the exact P9 Dima metric binding.

Current certification wording:

```text
P13B-1 ENGINE ATTESTATION + IDENTITY            = GREEN
P13B-2 PLATFORM TRUST                           = PROVIDER-FREE GREEN
P13B NATIVE SEMANTIC AVAILABILITY              = GREEN
P13B NATIVE METRIC ATTESTATION                 = GREEN
P13B-3 ONE LUNA PINNED-LIVE PX-01 ON DIMA.3    = NEXT / NOT YET SPENT
```

Next legal action:

```text
one Luna PX-01 canary
→ no automatic retry
→ GREEN or RED evidence
→ STOP for supervisor audit
```

Canonical onboarding:
`DIMA-METABASE-NEW-DEVELOPER-HANDOFF.md`.

---

## 2026-09-23 — P13B-3 FIRST PINNED-LIVE STANDARD — GREEN / SUPERVISOR STOP

Authorized live occurrence:

```text
Platform live SHA                  = 8993009b14f9a3f443b23ef681e181cfee210b6d
authorization                      = p13b-px01-native-metric-dima3-1
model                              = openrouter/openai/gpt-5.6-luna
question                           = Haziran 2026'da kaç satış siparişi açıldı?
oracle                             = 126
primary user turns                 = 1
governance                         = 35915780178 SUCCESS
P13B live run                      = 35915780089 SUCCESS
artifact id                        = 10774804897
artifact digest                    = sha256:744d1c0913bb20267e544b896d65c50da54196bacd33fbdc2d98d829496940a0
```

Certified engine/runtime:

```text
engine repo                        = UpcyTech/dima-metabase-engine
engine SHA                         = 10960f7c36bb84425b1794b557b78211c14d7f5f
release                            = 0.63.18-dima.3
upstream base                      = 2ba2485c78d7e00a9a25f82c00fc201da71590c4
build identity                     = github-actions:35915780089:10960f7c36bb84425b1794b557b78211c14d7f5f
runtime image identity             = sha256:0520e0b02a94e0d39b645443731e3d9436ee370624b61aa721ff914c9a293849
runtime instance id                = c88856ed-6f82-4709-ab6f-0c86113edb92
```

Semantic-resource proof in the same live runtime:

```text
canonical metric                   = metric.sales_order_count
ownership                          = DIMA_MANAGED
Metabase metric local id           = 1
Metabase metric portable entity id = VEzPLLv1IBWZfl7mJ9Xnb
persisted definition               = COUNT(*)
semantic availability              = GREEN
semantic availability model calls  = 0
```

Live Standard proof:

```text
official answer                    = 126
independent oracle                 = 126
authority                          = 1
native material query              = 1
attestation                        = 1
authorized artifact                = 1
ExecutionAccessSnapshot            = 1
database execution                 = 1
Dima QueryReceipt                  = 1
VERIFIED Evidence                  = 1
silent wrong                       = 0
Agent API analytical fallback      = 0
Wren fallback                      = 0
raw SQL fallback                   = 0
admin analytical fallback          = 0
```

Exact execution identity remained immutable across the full chain:

```text
attested   = acef568a9051f27e90c3743afefcb9f01b4f5ff77d8ba2117c405f29a56dd787
authorized = acef568a9051f27e90c3743afefcb9f01b4f5ff77d8ba2117c405f29a56dd787
submitted  = acef568a9051f27e90c3743afefcb9f01b4f5ff77d8ba2117c405f29a56dd787
receipted  = acef568a9051f27e90c3743afefcb9f01b4f5ff77d8ba2117c405f29a56dd787
```

Receipt/Evidence:

```text
QueryReceipt id                    = dqr_d096c10ab01354391bae0c62
QueryReceipt fingerprint           = 5526cfc9c201fae9f65876675b7992e00a3dbd8effba0d81472e7e3c094e2df1
ExecutionAccess fingerprint        = 3b5aca37a6ed684aa68cfdfe6b276dfcc2ea8b794351732bfeb545ca8e329571
Evidence id                        = evi_17fc5054faf60aec1d1e3e6a
Evidence state                     = VERIFIED
```

Measured live economics:

```text
native agent latency               = 15948 ms
dataset latency                    = 94 ms
live proof end-to-end              = 16278 ms
native tool calls                  = 6
analytical queries                 = 1
provider token/cost counters       = NOT EXPOSED BY NATIVE STREAM
```

Interpretation:
- the prior dima.2 semantic failure was corrected at its real owner by making the canonical
  Dima-managed metric available to native Metabot;
- native Metabot selected the persistent native metric identity rather than authoring the prior
  DISTINCT(field) physical aggregation;
- engine attestation observed that metric identity while original pMBQL remained the immutable
  execution artifact;
- Dima bound that identity to the exact P9 ManagedResourceBinding, authorized the exact artifact,
  executed the same pMBQL, sealed the existing P5 receipt, checked the independent oracle, and only
  then promoted VERIFIED Evidence;
- no prompt patch, regex/fuzzy/morphology semantic authority, Python MBQL repair, hard-coded PX-01
  query, raw SQL, Wren, Agent API analytical hot-path, admin fallback, second access identity or
  second receipt system was introduced.

Current certification wording:

```text
P13B-1 ENGINE ATTESTATION + IDENTITY            = GREEN
P13B-2 PLATFORM TRUST                           = PROVIDER-FREE GREEN
P13B NATIVE SEMANTIC AVAILABILITY              = GREEN
P13B NATIVE METRIC ATTESTATION                 = GREEN
P13B-3 ONE LUNA PINNED-LIVE PX-01 ON DIMA.3    = GREEN

P13 STANDARD FINAL CLOSURE                      = NOT CLAIMED
P13C ENTITY-VALUE INTEGRATION                   = NOT STARTED
P14 RESEARCH                                    = NOT STARTED
PRODUCTION MULTI-INSTANCE SECURITY CLOSURE      = NOT CLAIMED
```

Open debt remains open exactly as before:
- DMP-P5-BLOCK-001;
- DMP-P11-INTEGRATION-005;
- EV-05 / EV-06 / EV-07;
- P10B2 RLS / CLS / impersonation / advanced routing / cache-result reauthorization;
- P9 dimension / time / relationship transport;
- P7/P8 calculated / relationship / view semantics;
- historical Wren typed gaps;
- multi-instance runtime/deployment closure.

CI economy note — OPEN / NOT IMPLEMENTED:
the successful live run still rebuilt the exact engine from source inside the Platform canary. The
run itself lasted about 10m44s, while the model-backed Standard proof reported only 16.278s
end-to-end. A future supervisor-reviewed CI milestone may move the expensive source build to engine
certification, publish a digest-pinned immutable certified image once, and make Platform live proofs
pull that exact digest and re-attest the same repository/SHA/upstream/release/build/image/runtime
identity. Source-build certification must remain; it must not be silently deleted or replaced by a
moving tag. No such CI optimization is authorized or implemented by this closure.

Current stop:

```text
P13B-3 FIRST PINNED-LIVE STANDARD = GREEN
NO RETRY
NO SECOND MODEL RUN
NO P13C
NO RESEARCH
NO GENERALIZATION
STOP FOR SUPERVISOR AUDIT
```



---

## 2026-09-23 — P13C PREDEVELOPMENT + CI ECONOMY AUTHORIZED

New supervisor directive supersedes the prior P13B stop only for the two bounded next milestones.
P13B itself remains sealed and will not be rerun.

Provider-free source inspection result:

```text
engine dima.3 textual filter typed attestation = INSUFFICIENT
non_temporal_filter_count                      = PRESENT
typed field/operator/literal/type              = ABSENT
engine attestation extension needed            = YES
Python MBQL parser                              = NO
Metabot cognition change                        = NO
```

Authorized next engine revision, derived from release history:

```text
0.63.18-dima.4
```

The same revision must establish permanent CI economy:

```text
cheap deterministic gates
→ one cached source build
→ smoke
→ publish exact GHCR image
→ immutable digest
→ pull exact digest
→ /identity verify
→ certified-image receipt
```

P13C first capability stays one same-table low-cardinality textual equality filter. The frozen
Boyahane schema confirms `satis_siparisleri.kanal` exists as VARCHAR, but no value is frozen until
the actual fixture and restricted-current-user retrieval prove it.

Security invariant:
P11 evidence must use the existing P5/P10 `execution_access_fingerprint`; no second lens hash or
resolver framework is allowed.

Model budget before provider-free GREEN:

```text
Luna = 0
Sol  = 0
C1   = 0
```

Current next action:
bounded dima.4 engine filter-attestation + certified-image CI implementation, then Platform
gitlink/runtime-lock migration and provider-free P13C proof.

---

## 2026-09-24 — DIMA.4 CERTIFIED / P13C RUNTIME BLOCKED AT GHCR ACCESS ONLY

Exact certified runtime:

```text
engine main              = cdd117558fea3b0a80f6b89bb872ffb6e9ab175f
release                  = 0.63.18-dima.4
certification            = 35951538259 SUCCESS
certified image          = ghcr.io/upcytech/dima-metabase-engine@sha256:ce8d135163faba74f80c18c8e0a585037be2e6049a7ca74d4f477e655e039a71
build identity           = github-actions:35951538259:cdd117558fea3b0a80f6b89bb872ffb6e9ab175f
Platform pinned HEAD     = bb8fb6edd36611ecccfbb18acccc7f2098d44569
Platform engine gitlink  = cdd117558fea3b0a80f6b89bb872ffb6e9ab175f
```

The certified-image artifact proves exact digest pull and runtime-identity verification succeeded
inside engine certification.

Current P13C runtime integration:

```text
run                      = 35953149626 FAILURE
failed owner             = GHCR package/repository Actions access
failed step              = Pull exact certified engine digest
login                    = SUCCESS
docker pull              = manifest unknown
engine started           = NO
model calls              = 0
analytical executions    = 0
```

Therefore the run proves nothing negative about P13C semantic mapping, P11/P10, native textual-filter
attestation, Metabot cognition, candidate authorization or dataset execution. Do not modify those
owners for this RED.

Required next boundary action:
grant the Platform repository GitHub Actions read access to the existing GHCR package (or make the
package public only if that is the intended owner policy), then rerun the same failed P13C runtime
boundary. No engine rebuild, new engine revision, PAT, duplicated image, moving tag or alternate
registry workaround is authorized.

Product-first architecture correction is now normative:
native Metabase/Metabot capability reuse is default; Dima adds only its differentiated semantic,
security, provenance, Evidence, Research epistemics and Decision truth.


---

## 2026-09-24 — P13C SEALED GREEN / PRODUCT-FIRST DIGEST CORRIDOR PROVEN

The prior GHCR blocker is closed at its actual owner. The certified engine package is public and the
exact immutable digest is anonymously pullable. The Platform failure was caused by authenticating
the public cross-owner GHCR pull with the repository-scoped `GITHUB_TOKEN`.

CI-only correction:

```text
active workflows changed:
- dima-metabase-p13c-integration.yml
- dima-metabase-p13c-live.yml
- dima-metabase-p13b-semantic-availability.yml

removed:
docker login ghcr.io ...

preserved:
docker pull "$IMMUTABLE_IMAGE_REF"
docker image inspect ... | grep -Fx "$IMMUTABLE_IMAGE_REF"

legacy dima-metabase-p12x-c2-live.yml = untouched
packages: read                         = retained
runtime lock                           = unchanged
product/trust/Metabot code             = unchanged
```

Proof sequence:

```text
anonymous-pull CI fix commit          = ac6013fcdc31c9c8e8fb072f2f6dc14451f02a3d
first new runtime run                 = 35956052648
exact digest pull                     = SUCCESS
runtime/P11 chain                     = SUCCESS
failure owner                         = CI test dependency only
failure                               = pytest: command not found

canonical dev-extra fix commit        = c3397f68d4af5e524455fec5bff2d1f21b489d0d
final P13C runtime integration run    = 35956274118 SUCCESS

single Luna canary trigger commit     = c0cfd65f1162cda31bd8d984dcaa2865e7d2466c
single Luna live run                  = 35956538018 SUCCESS
live artifact id                      = 10790995760
live artifact digest                  = sha256:52ffc8c96e9ba30ca9f1764dc5b695ea7b25e63d1bf409523961dd3be700c69a
```

Certified runtime remained exactly:

```text
engine SHA              = cdd117558fea3b0a80f6b89bb872ffb6e9ab175f
release                 = 0.63.18-dima.4
immutable image         = ghcr.io/upcytech/dima-metabase-engine@sha256:ce8d135163faba74f80c18c8e0a585037be2e6049a7ca74d4f477e655e039a71
engine certification    = 35951538259 SUCCESS
```

P13C-01 live proof:

```text
question                         = Haziran 2026'da Web kanalından kaç satış siparişi açıldı?
model                            = openrouter/openai/gpt-5.6-luna
primary user turns               = 1
official answer                  = 27
independent oracle               = 27
silent_wrong                     = 0

attested fingerprint             = 950ea75436af26ea9d307cf37421a4b98fe2a86fbceee4e2487001ed8dadb393
authorized fingerprint           = 950ea75436af26ea9d307cf37421a4b98fe2a86fbceee4e2487001ed8dadb393
submitted fingerprint            = 950ea75436af26ea9d307cf37421a4b98fe2a86fbceee4e2487001ed8dadb393
receipted fingerprint            = 950ea75436af26ea9d307cf37421a4b98fe2a86fbceee4e2487001ed8dadb393

typed predicate                  = field_id 531 / type/Text / "=" / "Web" / stage 0
QueryReceipt                     = dqr_36e99d80963cb15f9db629c5
Evidence                         = evi_c5bf623c5f7ef98c796ee4d7 / VERIFIED
authority                        = asa_365b8456f7d15192697cc339

native material queries          = 1
database executions              = 1
Wren fallback                    = 0
raw SQL fallback                 = 0
Agent API analytical fallback    = 0
admin analytical fallback        = 0
```

The permanent fast corridor is therefore operational:

```text
source-build once in engine certification
→ publish immutable digest
→ Platform pulls exact digest
→ verify RepoDigest + /identity
→ run bounded Platform proof
```

P13C is closed. Per DMP-DEC-0042/Product-First authority, development continues directly to one
cohesive P13D Standard analytical-expansion slice; no P13B rerun and no dima.4 rebuild is required
for the P13C closure.

---

## 2026-09-24 — P13D TRUST CORRECTED / SECOND LIVE STOP AT DIMA.5 ATTESTATION RESTORE

Current exact engine/runtime:
```text
engine main / SHA       = 71788caff1f366593a24d21161db6f212de69006
release                 = 0.63.18-dima.5
engine certification    = 35961869359 SUCCESS
immutable image         = ghcr.io/upcytech/dima-metabase-engine@sha256:2ace4b5ec406578188b5147c932ff7f91ff6e4706257c8d4c261ff920c18f444
build identity          = github-actions:35961869359:71788caff1f366593a24d21161db6f212de69006
```

The first P13D live RED was reclassified under the recovery directive. Dima had conflated presentation
ordering with result-set-changing ranking. General trust correction:
- no ranking + any LIMIT => BLOCK;
- no ranking + order-only over the already-authorized breakout or sole metric aggregation => ALLOW;
- hidden/unaccepted order targets => BLOCK;
- explicit ranking remains exact direction + exact metric target + exact limit.

Correction evidence:
```text
trust/diagnostic fix commit       = 6055c8b981c09f33176ca80dc5d8c435539066ba
provider-free seal               = 35967035036 SUCCESS
engine changes                   = 0
Metabot cognition changes        = 0
QP/driver changes                = 0
runtime rebuild/rerun            = 0
```

The one authorized compact Luna retry was then run unchanged:
```text
live trigger commit              = 6ae0fc66af7f638550c9342300097fd16f8a9901
live workflow                    = 35967191948 FAILURE
live artifact                    = 10794717399
artifact digest                  = sha256:17da8ebdb7c73b9c18b6182bdf7ae4d5bc05afa13eba35f8c18b281dcafab90f
attempt                          = p13d-cohesive-dima5-top2-002
```

The run passed the exact digest pull, restricted principal, Dima-managed metric provisioning and
provider-free pre-live boundary, then advanced past BREAKDOWN into P13D-RANKING. The ranking case
failed before Dima trust authorization at the native-query-attestation endpoint:

```text
failure owner = native-query-attestation
HTTP          = 500
engine        = dima.5 exact certified digest
native query  = dH2WJPR7FtxB70vwm6MyH
tool calls    = 12

root exception:
optimize-temporal-filters/optimize-temporal-clauses
No implementation of :truncate-to for java.lang.String
```

The engine error payload shows a native ranking query containing a `between` temporal filter whose
bounds are serialized `absolute-datetime` strings. Dima's attestation restore path currently feeds the
persisted JSON query into `lib/query` and then QP preprocess. The pinned Metabase source also exposes
`lib.serialize/prepare-after-deserialization` as the native inverse for REST/app-DB query
deserialization. This makes a Dima-local persisted-query restore/hydration compatibility defect the
leading root-cause candidate; it is not evidence that Metabot cognition, ranking semantics, QP core or
a driver is wrong.

Diagnostic nuance:
the failure artifact's attestation-derived pMBQL fields still contain the preceding successful
BREAKDOWN attestation because the RANKING attestation failed before those fields could be replaced.
The authoritative ranking-failure evidence is therefore the new `native_query_id`, failure owner,
tool count and the engine HTTP 500 payload/query fragment. Do not treat the stale breakdown pMBQL in
that failure artifact as the failed ranking query.

Current boundary:
```text
P13D provider-free        = GREEN
P13D digest runtime       = GREEN
presentation-order fix    = GREEN
P13D live                 = RED / engine attestation restore-preprocess compatibility
P13D sealed               = NO
P14 started               = NO
```

The current recovery directive explicitly forbids dima.6 / engine rebuild and authorized only one new
compact Luna retry. Therefore no engine patch, no additional model run, no P14 start and no query
rewrite/fallback is performed here. Supervisor authorization is required for a bounded observational
engine compatibility correction plus its post-fix certification/live budget.



---

## 2026-09-24 — DIMA.6 EXACT-OCCURRENCE MIGRATION GREEN / FINAL P13D LIVE STOPS AT COMPARISON CODEC

Certified engine/runtime is now:

```text
engine main / SHA       = cbe313af9ac2d5960f662068e433d328d896fb06
release                 = 0.63.18-dima.6
certification           = 36042062775 SUCCESS
immutable digest        = sha256:40e9a44be49904de3ddf12d4683c768e70955851c10a928a9c8f7d8f60780353
build identity          = github-actions:36042062775:cbe313af9ac2d5960f662068e433d328d896fb06
upstream base           = 2ba2485c78d7e00a9a25f82c00fc201da71590c4
```

dima.6 certification proved one source build, smoke, publish, pull-by-digest and runtime identity
verification. Engine `main` was non-force fast-forwarded to the certified SHA.

Platform coherent migration:

```text
migration commit         = dd4e69a762f28f3eae78f73d4ac00e3ecf22d570
final live HEAD          = af66d2999e1710717c4ef117f936b302bd3b3870
engine gitlink           = cbe313af9ac2d5960f662068e433d328d896fb06
runtime lock             = exact dima.6 SHA/digest/certification identity
governance               = 36046089473 SUCCESS
native bridge regression = 36046089305 SUCCESS
provider-free P13D       = 36046089168 SUCCESS
```

The canonical execution seam is now exact-occurrence identity only:

```text
Platform authorization keeps attested A
→ execution transport sends:
   conversation_id
   native_query_id
   expected_pmbql_fingerprint
   expected_attestation_id
→ caller pMBQL body is not sent
→ engine reloads/re-attests the same persisted occurrence
→ engine executes it through native QP
→ engine returns executed fingerprint + re-attestation
→ Platform binds those facts into existing P5 QueryReceipt
```

P5 QueryReceipt and P10 ExecutionAccessSnapshot remain the only receipt/security authorities.
No second planner, semantic authority, security fingerprint or receipt system was introduced.

Final compact Luna gate:

```text
run                      = 36046994140 FAILURE
artifact                 = 10829286413
artifact digest          = sha256:7106a194b029225d3b9959b6d02c5898f5ca07ec1d410b5abdf4aab686880e02
attempt                   = p13d-final-dima6-exact-occurrence-001
deterministic preflight  = 66/66 PASS
pre-live boundary        = GREEN
```

Live evidence:
- BREAKDOWN = GREEN / oracle exact / QueryReceipt + VERIFIED Evidence;
- RANKING = GREEN / oracle exact / QueryReceipt + VERIFIED Evidence;
- COMPARISON = RED before authorization/execution at `native-query-attestation`;
- COMPARISON engine error = HTTP 422 / `NATIVE_QUERY_RUNTIME_REPRESENTATION_UNSUPPORTED`;
- current codec rejected a string `:absolute-datetime` literal because it was not parseable as a
  local ISO LocalDateTime;
- exact failed literal value is not present in the artifact/log, so no speculative codec widening
  is permitted.

Current binding boundary:

```text
NATIVE_SUBSTRATE_IMMUTABILITY = BINDING
NATIVE_CORE_PATCH = EXCEPTION ONLY

P13D provider-free        = GREEN
P13D BREAKDOWN live       = GREEN
P13D RANKING live         = GREEN
P13D COMPARISON live      = RED / FAIL-CLOSED
P13D sealed               = NO
P14 started               = NO
second Luna authorized    = NO
dima.7 authorized         = NO
codec diagnostic patch    = NO
```

Supervisor authorization is required before any further P13D engine compatibility work or paid/model
live attempt. Do not rerun `36046994140`.


---

## 2026-09-24 — P13 TRUST BASELINE SEALED / P14 NATIVE RESEARCH AUTHORIZED — DMP-DEC-0044

Supervisor audit after the certified dima.6 final P13D live:

```text
audited Platform checkpoint       = 77000d07da0af4d43688bf963880ebc5120c8f1f
engine main                       = cbe313af9ac2d5960f662068e433d328d896fb06
release                           = 0.63.18-dima.6
certification                     = 36042062775 SUCCESS
immutable digest                  = sha256:40e9a44be49904de3ddf12d4683c768e70955851c10a928a9c8f7d8f60780353

P13D BREAKDOWN live               = GREEN / VERIFIED
P13D TOP-N RANKING live           = GREEN / VERIFIED
P13D PERIOD COMPARISON            = DEFERRED COMPATIBILITY GAP / NOT GREEN

P13 STANDARD TRUST BASELINE       = SEALED
P13 OPERATOR-FAMILY EXPANSION     = STOPPED
P14 NATIVE RESEARCH               = AUTHORIZED
```

The comparison RED is not hidden or reclassified as GREEN. It remains fail-closed compatibility debt
in the Dima-owned runtime representation seam. No additional dima.7/Luna cycle is authorized merely
to complete the historical three-case matrix.

Binding product direction:

```text
METABASE + METABOT
= native analytics substrate

DIMA
= business ontology / engine mapping
+ Research / Evidence / Hypothesis / Decision / Action / Memory
```

Native capabilities are inherited by default. Dima does not certify or reimplement every MBQL
operator family. Existing P7/P9 semantic resources remain sealed compatibility assets; duplicate
formula/query ownership must not expand.

Immediate next action:
implement the P14 durable Research foundation and native Metabot delegation using existing P13
exact-occurrence execution, P10, P5 and Evidence contracts. Initial P14 foundation uses zero new
engine builds and zero model calls.



---

## 2026-09-24 — P14 NATIVE RESEARCH FOUNDATION VERTICAL GREEN — DMP-DEC-0045

P14 has started under DMP-DEC-0044. The first coherent Research foundation vertical is sealed GREEN.

\`\`\`text
implementation                  = a8c7b5d2b922e85ff046c6c7ce1bfce92aa13552
integrated exact-occurrence proof = bab26fe51978929ace44f7703543f78099c692ce
provider-free                   = 36052728145 SUCCESS
governance                      = 36052727756 SUCCESS
P14 focused                     = 6 passed
P13D/P10/P5 regression          = 69 passed

engine                          = cbe313af9ac2d5960f662068e433d328d896fb06
engine build                    = 0
model calls                     = 0
native Metabase/Metabot files   = 0
duplicate analytics mechanisms  = 0
\`\`\`

New P14 owner:
\`backend/app/v3/research.py\`.

It introduces durable/versioned ResearchSession state, obligations, hypotheses, explicit
counter-evidence, Evidence refs, bounded budget/stopping, native Metabot conversation identity and
obligation-scoped limitations.

The integrated provider-free proof uses the existing chain:

\`\`\`text
Research obligation
→ native Metabot delegation
→ P13 authorization
→ exact native occurrence
→ P10 access identity
→ P5 QueryReceipt
→ VERIFIED Evidence
→ Research state
\`\`\`

ResearchManager contains no SQL/MBQL generator/parser, comparison/ranking/temporal planner, query
repairer, second receipt/access authority or Wren/Agent-API/raw-SQL analytical fallback.

P13D period-comparison remains explicit deferred compatibility debt. It was not retried, widened or
marked GREEN.

Current status:

\`\`\`text
P13 STANDARD TRUST BASELINE      = SEALED
P13D BREAKDOWN / RANKING         = LIVE GREEN / VERIFIED
P13D PERIOD COMPARISON           = DEFERRED COMPATIBILITY GAP / NOT GREEN

P14 NATIVE RESEARCH              = IN PROGRESS
P14 FOUNDATION VERTICAL          = GREEN / SEALED
P15                              = NOT STARTED
\`\`\`

Next coherent P14 work:
product-level Research/Ask orchestration + durable resume/correlation around this aggregate, reusing
the same native Metabot and P13/P10/P5/Evidence path. No engine rebuild or paid/model run is needed
for that integration by default.


---

## 2026-09-24 — P14 PRODUCT RESEARCH/ASK INTEGRATION GREEN — DMP-DEC-0046

The DMP-DEC-0045 foundation is now wired to the product Ask boundary and sealed provider-free.

```text
implementation                    = 47ac0d4ecae7addbd7d79cff6452b6e60b7a3d9b
CI economy                        = 939f51facba7951bf0a07d4ef8facb38c9e11d13
final focused code                = dbef0499abe6b7804b5f09d8ec7ad76b99946b1c
provider-free                     = 36057793900 SUCCESS
governance                        = 36057794099 SUCCESS
P14 focused                       = 13 passed
P13D/P10/P5 regression            = 69 passed

engine                            = cbe313af9ac2d5960f662068e433d328d896fb06
engine build                      = 0
model calls                       = 0
native Metabase/Metabot files     = 0
duplicate analytics mechanisms    = 0
```

Product flow now exists:

```text
/ask-v2 READY ResearchBrief
→ durable ResearchSession
→ governed/delegatable obligation
→ durable native conversation/request correlation
→ NativeEngineBridge delegation
→ exact native occurrence correlation
→ existing P13/P10/P5 material owner
→ eligible VERIFIED Evidence
→ durable Research state
```

Resume uses `research_session_id` and bypasses re-interpretation of the old prompt. Restart after
exact native occurrence capture resumes the same occurrence. Unknown/unsupported material work
becomes an obligation-level limitation and does not poison independent valid obligations.

Production does not use a shared Metabase admin/session fallback. The application installs the
durable Research product owner, but material native execution remains fail-closed until the existing
principal-scoped native/P13 runtime owner is supplied through the bounded runtime seam.

The old P13D comparison gap is unchanged and remains deferred / NOT GREEN.

Current phase:

```text
P13 STANDARD TRUST BASELINE       = SEALED
P14 FOUNDATION                    = GREEN / SEALED
P14 PRODUCT RESEARCH/ASK          = PROVIDER-FREE GREEN / SEALED
P15 NATIVE EXPLORATIONS           = NEXT / NOT STARTED
```


---

## 2026-09-25 — P14 PRODUCTION RUNTIME ACTIVATION / RETURN POINT B

Supervisor runtime-closure directive was applied from the current remote state without reopening P13
or the sealed P14 foundation.

Code progress:

```text
accepted Research context persistence = IMPLEMENTED
context implementation                = af7de7e5ae0d84384fc45752cc3f3608b771ba02
typed operation identity hardening    = 367f5e6e468f6b86ebe02816f2310b0f1330830c
governance                            = 36092002345 SUCCESS
engine changes                        = 0
model calls                           = 0
engine builds                         = 0
```

The exact accepted `ResearchBrief` is now part of the fingerprinted durable `ResearchSession`
checkpoint. Resolver-proven semantic refs plus typed ranking/comparison payloads survive restart.
Ranking/comparison payloads are also bound into `ResearchBrief.brief_id`; resume does not reparse the
old prompt.

Production runtime is **not** GREEN. Current source audit proves three unresolved owner boundaries:

1. **Principal-scoped native identity owner is absent from product runtime.**
   Dima auth issues the Dima principal/JWT, while `NativeEngineBridge` requires an authenticated
   Metabase session. No production principal -> exact Metabase subject credential/session provider is
   present in current product config/control-plane/startup. P10B1 proves the native subject contract in
   an isolated lab but explicitly is not a production identity/session issuer.

2. **Accepted named-month temporal authority is not yet losslessly carried to P13.**
   Research currently persists the accepted temporal surface, e.g. `Haziran 2026`, but P13 trust
   requires exact accepted period bounds/time dimension. The newer typed `TemporalBindingEngine` is
   deterministic after a typed normalization choice, but the current Research acceptance path does not
   persist such a choice and its closed ontology does not represent an absolute named month. Reparsing
   the old surface during resume would create a new semantic/temporal decision and is forbidden.

3. **Production current execution/resource-binding provider is absent.**
   `DimaExecutionBindingSnapshot` / `ManagedResourceBinding` contracts exist and P13 live proofs use
   them, but current product runtime has no durable production provider for the exact current
   Dima-to-Metabase binding/security facts. Lab Boyahane helpers are not promoted to product truth.

Forbidden shortcuts were not used:
- shared admin or global service-account analytical session;
- new identity broker;
- old-prompt reparse;
- new temporal/parser/planner;
- hard-coded Boyahane production binding;
- Wren/raw SQL/Agent API analytical fallback;
- P13/native-core patch.

Current milestone state:

```text
P14 FOUNDATION                       = GREEN / SEALED
P14 PRODUCT BOUNDARY                 = GREEN / SEALED
P14 ACCEPTED CONTEXT DURABILITY      = IMPLEMENTED / GOVERNANCE GREEN
P14 PRODUCTION NATIVE RUNTIME        = BLOCKED / NOT GREEN
P14 LIVE RESEARCH CANARY             = NOT RUN
P15                                  = NOT STARTED
```

This is a genuine supervisor Return Point B. Do not run the P14 provider-free seal or a Luna canary
until an existing production owner is identified/authorized for the missing identity/security/binding
boundary and the accepted temporal authority can reach P13 without reinterpretation.
---

## 2026-09-25 — P14 runtime STOP reclassified by DMP-DEC-0047

Audit of `abc7bff31e46047cc81b89dbccf99bbf459a26de`, DMP-DEC-0044/current product ownership,
the external architecture analysis and read-only `feat/ask-v2-mvp` patterns found that the previous
P14 runtime STOP bundled one obsolete P13-era requirement with two real deployment seams.

Reclassification:

```text
accepted named-month → exact P13 ResolvedPeriod before Research
= NOT A GENERIC P14 BLOCKER

Dima Principal → exact Metabase subject/session
= REAL THIN DEPLOYMENT SEAM

Dima concept/context → current Metabase resource/security binding
= REAL THIN DEPLOYMENT SEAM
```

Metabase/Metabot own ordinary temporal/query analytical semantics. P14 must not create a shadow
temporal planner or compile each Research obligation back into full P13 operator semantics.

Ask-v2 remains reference only. Its useful patterns are principal pass-through and durable/idempotent
Research lifecycle; its Wren-specific planner/cube/temporal ownership is not imported.

Current next action:
implement the two thin production providers and bind the existing P14 Research material flow to native
Metabot/exact-occurrence/P5 Evidence without a second analytics/security/temporal authority.

P15 remains NOT STARTED until one real P14 production runtime/canary boundary exists.



---

# 2026-09-25 — DMP-DEC-0048 CURRENT EXECUTION STATUS

Forward authority is now DMP-DEC-0048. DMP-DEC-0047 is transitional/history only.

Current checkpoint before refactor:

```text
HEAD                      = 3dc544b95c05044e35c6903b720a6ddb824e9b37
governance                = 36095837229 SUCCESS
P14 provider-free         = 36095837211 FAILURE
focused tests             = 13 PASS / 6 FAIL
P14 native-direct         = IN PROGRESS / NOT SEALED
P15                       = NOT STARTED
engine change/build       = 0 / 0
Luna / Sol / C1           = 0 / 0 / 0
```

The current 523-LOC-style thick gateway is not the target and must not be patched to preserve its
architecture.

Forward production path:

```text
ResearchSession / obligation
→ principal-scoped native Metabot
→ exact Metabot-produced query A
→ direct native Metabase execution under same subject
→ native result
→ one DimaQueryReceipt
→ Evidence
→ Research state / user output
```

Mandatory removals/bypasses from generic P14 hot path:
- P13 attestation as mandatory middleware;
- P13 Dima re-execution endpoint as mandatory middleware;
- operator-level NativeExecutionManifest semantic inspection;
- AuthorizedExecutionArtifact synthesis only to satisfy historical P13 shape;
- synthetic P10 `VerifiedExecutionSecurityFacts → ExecutionAccessSnapshot`;
- required NativeResourceBinding row for every ordinary query;
- Dima MBQL/operator/time/filter/ranking/breakout revalidation.

Keep:
- durable Research lifecycle and accepted brief;
- no old-prompt reparse;
- explicit Dima principal ↔ native subject correlation;
- same principal-scoped native session;
- exact native query occurrence capture and restart;
- native runtime/result provenance;
- one receipt family;
- Evidence/Research linkage;
- obligation-scoped failure isolation.

Current RED classification:
- `SimpleNamespace.headers` = focused test harness issue;
- timezone-naive timestamps = legitimate owner bug; fix new P14 binding defaults timezone-aware
  without global legacy timestamp refactor.

But fix these only in the native-direct refactor, not by sealing the obsolete thick gateway.
