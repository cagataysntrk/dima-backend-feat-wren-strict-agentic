# DIMA + METABASE — DECISION RECEIPTS

## Mandatory schema

```text
decision_id
date
question
options_considered
evidence
decision
scope
invariants
rejected_shortcuts
revisit_condition
status
```

---

## DMP-DEC-0001 — Certified fork point

date: 2026-09-22

question:
Which immutable Dima commit is safe to fork without coupling this project to the moving ask-v2 branch?

evidence:
- `3774484167f1056d89da0e0609246fb4a05057ec`: real Standard Wren + retained Research sentinel `35718883950 = 2/2 PASS`.
- focused/provider-free gate before it recorded GREEN.
- observed moving HEAD `4ad8238...`: full-live run `35724830736` FAILURE.

decision:
Create `feat/dima-metabase-platform` from exact SHA `3774484167f1056d89da0e0609246fb4a05057ec`.

scope:
Branch/bootstrap only. It does not claim later ask-v2 deltas are wrong; they are simply not automatically inherited.

rejected_shortcuts:
- branch from moving HEAD;
- wait for source branch to stop moving;
- copy latest commits without revalidation.

revisit_condition:
Never mutate the base. Later source deltas are separate branch-local decisions.

status: SEALED.

---

## DMP-DEC-0002 — Source branch isolation

date: 2026-09-22

decision:
`feat/ask-v2-mvp` is read-only reference. No write, merge, rebase, cherry-pick or automatic synchronization is authorized.

reason:
The source branch has another active developer and continues to evolve independently.

revisit_condition:
Only an explicit future user instruction can change this policy.

status: SEALED.


---

## DMP-DEC-0003 — M1 inheritance and implementation boundary

date: 2026-09-22

question:
How should M1 obtain the post-base correctness improvements visible on the moving ask-v2 branch without coupling the platform branch to it?

options_considered:
- cherry-pick/merge later ask-v2 commits;
- branch again from moving source HEAD;
- re-derive the required invariants inside the new v3 contracts and certify them locally.

evidence:
- source branch is independently active and write-protected by project policy;
- post-base source deltas contain useful invariants: material semantic-surface accounting, two-phase cross-family authority validation/commit, distinct semantic/temporal role wiring;
- the same moving source line also contains full-live run `35724830736` = FAILURE;
- P1 requires engine-independent contracts and zero Wren behavior drift, not source-branch synchronization.

decision:
M1 will **not** merge/cherry-pick/rebase from `feat/ask-v2-mvp`.
Required correctness properties are re-derived as v3 contract invariants and proven on this branch.
The source delta remains evidence/reference only.

scope:
M1/P1 only.

invariants:
- ask-v2 writes = 0;
- v2 production path remains unchanged during M1;
- no second Research contract type;
- shared Standard/Research XOR;
- every material semantic surface bound or explicitly unresolved;
- semantic handle resolution occurs before substrate execution;
- Wren adapter receives only resolved execution intent;
- existing Wren behavior parity = 0 drift.

rejected_shortcuts:
- latest-is-best inheritance;
- importing failed full-live harness as proof;
- semantic resolution inside Wren substrate;
- Metabase code/routing during M1.

revisit_condition:
A later source delta may be ported only under a new explicit Decision Receipt and branch-local proof.

status: SEALED.


---

## DMP-DEC-0004 — M2 lab isolation topology

date: 2026-09-22

question:
Where should the Metabase P2 lab live without contaminating the existing Dima stack or the existing SQL Server restore lab?

options_considered:
- modify root `docker-compose.yml`;
- extend `backend/lab/docker-compose.yml`;
- create a dedicated `backend/lab/metabase/` stack.

evidence:
- root compose is active Dima dev infrastructure;
- backend/lab compose is a separate SQL Server restore environment with its own data/backups lifecycle;
- P2 requires Metabase + dedicated application Postgres + representative analytics DB and no product routing;
- isolation reduces accidental dependency and makes teardown/backup tests reproducible.

decision:
Create a dedicated `backend/lab/metabase/` stack. Do not modify either existing compose file in M2.

scope:
M2/P2 lab only.

invariants:
- private lab network;
- independent persistent app DB;
- no Dima product import/routing;
- exact runtime release + immutable digest required before compose implementation.

rejected_shortcuts:
- use `latest`;
- reuse Dima control-plane DB as Metabase app DB;
- attach Metabase directly to production/customer data for bootstrap;
- treat process health as Agent API capability.

revisit_condition:
Production packaging is a later decision after P3A/P8 evidence.

status: SEALED.


---

## DMP-DEC-0005 — M2 exact runtime artifact pins

date: 2026-09-22

question:
Which exact runtime artifacts should the isolated P2 lab certify?

evidence:
- official Metabase releases list 63.18 / tag `v0.63.18` as latest stable;
- official release specifies OSS Docker line `metabase/metabase:v0.63.18.x`;
- Docker Hub exposes multi-platform index digest
  `sha256:1160b570cb11c107bce00e71293552df8a8363e01a32c2c7a048cee002dc8a73`;
- Metabase recommends PostgreSQL for the application database;
- PostgreSQL 17.11 is a supported current minor and its Docker Official Image index is
  `sha256:67f41722b7a8cbdb868a44a4995c846eddfdc2973bccb291ce937dce88ad5675`.

decision:
- logical Metabase runtime version = `v0.63.18`;
- execute immutable image =
  `metabase/metabase@sha256:1160b570cb11c107bce00e71293552df8a8363e01a32c2c7a048cee002dc8a73`;
- both lab PostgreSQL services use
  `postgres@sha256:67f41722b7a8cbdb868a44a4995c846eddfdc2973bccb291ce937dce88ad5675`
  (PostgreSQL 17.11).

scope:
M2 lab only.

invariants:
- no `latest`;
- source audit SHA remains separate from runtime image;
- exact digest is the executable identity;
- later runtime upgrade requires new Decision Receipt + backup/restore/rehearsal.

rejected_shortcuts:
- floating `latest`;
- beta v0.64 runtime;
- assuming source-audit master SHA identifies Docker runtime;
- H2 application DB.

revisit_condition:
Only through explicit runtime-upgrade ticket.

status: SEALED.


---

## DMP-DEC-0006 — P3 primary integration surface is REST/Agent API

date: 2026-09-22

question:
Which Metabase interface should Dima certify first for the substrate boundary?

evidence:
- sealed roadmap names versioned REST/Agent API as the primary candidate and MCP as optional lab;
- M2 pinned-runtime proof exercised Agent API search/read/construct/execute/query successfully;
- REST serialized query and continuation semantics are explicit and independently testable;
- MCP query_handle lifecycle is session-bound and must not be conflated with durable Dima receipts.

decision:
P3 certifies REST/Agent API only. MCP is not part of the P3 production candidate boundary.

scope:
P3/P3A.

invariants:
- no raw-SQL method;
- no admin/content/semantic mutation methods;
- serialized query and continuation remain distinct types;
- durable identity remains Dima-owned.

revisit_condition:
MCP may be evaluated later as an optional interface under a separate decision.

status: SEALED.

---

## DMP-DEC-0007 — P3A seam candidate disposition

date: 2026-09-22

decision:
- Candidate A (`StandardProjection + opaque handles`) is rejected as the substrate seam because it
  would require semantic-handle resolution after the Dima authority boundary.
- Candidate C (Wren-specific planned representation) is rejected as canonical because it re-couples
  Dima to Wren.
- Candidate B (`ResolvedAnalyticsIntent`) is the only prototype candidate, but remains unproven.

P3A may pair B with an immutable **Dima-owned** lineage/spec snapshot. That snapshot may map stable
Dima semantic identity to physical portable lineage and execution semantics, but it may not become a
parallel Metabase business-semantic registry.

Known risk:
current context-bound source candidate IDs are not durable global Dima semantic IDs. P3A must expose,
not hide, any identity/lineage gap.

status: SEALED FOR PREFLIGHT; B NOT YET ACCEPTED.


---

## DMP-DEC-0008 — P3A result: candidate B passes representative bridge preflight

date: 2026-09-22

question:
Can accepted Dima semantic execution intent reach Metabase structured-query semantics without
raw-language reparse, semantic redefinition, label guessing, implicit joins or a second semantic owner?

evidence:
- P3A provider-free gate: 7 tests PASS;
- all 8 mandated representative families compile;
- negative proofs fail closed on missing candidate/time binding, stale semantic context and cross-table
  lineage without approved Dima relationship;
- compiler source does not use `canonical_name`, `source_scopes`, Metabase search/read-resource,
  request_ref or source-message text as locators;
- pinned v0.63.18 live gate constructs and executes 9 generated portable queries successfully;
- M1 and P3 regressions remain GREEN on the P3A app-code SHA.

decision:
`PASS_B_SEAM`.

Accepted architecture:
```text
ResolvedAnalyticsIntent
+ immutable DimaExecutionBindingSnapshot
  - context candidate key -> stable Dima semantic id
  - DimaSemanticSpec
  - SourceLineage
  - explicit temporal compatibility binding
→ deterministic portable MBQL
```

interpretation:
The snapshot is a Dima-owned execution projection, not a second semantic registry.
Context-bound candidate ids are compatibility lookup keys only. Durable semantic identity is the
Dima metric/dimension id. Physical lineage is explicit data from Dima SourceLineage.

limits:
- same-table representative preflight only; cross-table joins remain fail-closed;
- arbitrary metric formulas are not translated;
- snapshot production lifecycle/reconciliation is not implemented by this gate;
- semantic/numeric equivalence with Wren is not established;
- identity/tenant/security parity is not established;
- PASS_B_SEAM does not authorize cutover or Wren retirement.

next:
P4 may enter pre-development review for the production MetabaseProjectionCompiler under these
constraints.

status: SEALED.


---

## DMP-DEC-0009 — P4 promotes P3A execution bindings instead of forking them

date: 2026-09-22

decision:
P4 creates one production execution-binding/canonical compiler boundary and refactors P3A to consume
or re-export those production primitives. P3A and P4 may not carry independent semantic binding models.

reason:
Two independently evolving candidate→semantic-id/lineage contracts would recreate the
second-semantic-owner risk P3A was designed to eliminate.

status: SEALED.

---

## DMP-DEC-0010 — P4 current-catalog snapshot is mandatory for rename/rebind safety

date: 2026-09-22

decision:
`SourceLineage` physical names alone are insufficient for P4's
`rename drift silent rebind = 0` invariant.

P4 compiler requires a Dima-owned immutable current-catalog binding keyed by
`SourceLineage.source_id`, carrying the exact current physical locator and a resource fingerprint.
Expected SourceLineage and current catalog binding must match before a portable reference is emitted.

A mismatch fails closed as source-lineage drift. The compiler does not search by label/name for a replacement.

status: SEALED.

---

## DMP-DEC-0011 — P4 does not invent missing typed filter semantics

date: 2026-09-22

evidence:
The current engine-independent `ResolvedFilterRef` inherited from the certified v2 path contains an
entity-value equality payload with `value: str`; it does not encode a general predicate operator,
semantic NULL predicate, or typed numeric literal.

decision:
P4 preserves current categorical equality semantics and fails closed where meaning would require
string parsing/coercion or a missing predicate operator. It will not interpret `"null"` as SQL NULL
or `"42"` as a numeric predicate merely because Metabase could coerce it.

If full typed null/numeric/non-equality filtering is required to close a later gate, the upstream Dima
semantic contract must receive its own explicit receipt and proof before modification.

status: SEALED.


---

## DMP-DEC-0012 — P4 canonical proof uses double construct plus structural manifest

date: 2026-09-22

decision:
P4 canonicalization on the pinned Metabase v0.63.18 runtime requires two identical
`/api/agent/v2/construct-query` results for each identical portable input. The returned base64 JSON
is decoded for structural proof and fingerprinting.

The pre/post semantic-slot manifest treats both explicit joins and repair-added `source-field*`
options as join behavior. Initial P4 requires both counts to remain zero.

reason:
The pinned representations repair layer can introduce implicit-join source-field metadata. Counting
only top-level `joins` would not prove the invariant `unapproved implicit join = 0`.

limits:
This is structural/canonical proof, not P8 numeric equivalence or security parity.

status: SEALED.


---

## DMP-DEC-0013 — durable canonical identity excludes only runtime-volatile lib/uuid

date: 2026-09-22

supersedes:
Only the **byte-for-byte serialized equality** requirement of DMP-DEC-0012.
All structural-manifest, double-construction, implicit-join and fail-closed requirements remain.

evidence:
Pinned Metabase v0.63.18 normalization explicitly generates random `lib/uuid` values for MBQL
clauses that do not already have one. Live P4 proof confirms repeated construction of the same
portable query can therefore produce different serialized bytes.

decision:
For P4 durable canonical proof:
1. call `construct-query` twice;
2. decode both base64 JSON queries;
3. recursively remove **only** map key `lib/uuid`;
4. require the resulting complete JSON objects to be exactly equal;
5. derive durable canonical fingerprint from that stable representation;
6. separately compare the semantic-slot manifest and reject explicit/implicit join insertion;
7. execute the real serialized payload, not the stripped representation.

A difference outside `lib/uuid` is
`NON_DETERMINISTIC_CANONICAL_SEMANTICS`.

reason:
Runtime-local clause UUID is execution/editor identity, not Dima business meaning or a durable
query identity. Excluding precisely that documented volatile key preserves strict determinism
without normalizing away semantic changes.

status: SEALED.


---

## DMP-DEC-0014 — P4 filter strings are literal equality payloads, never sentinel semantics

date: 2026-09-22

clarifies:
`DMP-DEC-0011`.

decision:
The current certified `ResolvedFilterRef.value: str` contract carries an equality value, not a
typed predicate AST.

Therefore, for a supported textual dimension:
- every string payload is compiled as literal string equality;
- no sentinel token such as `"null"`, `"none"`, `"empty"`, `"unknown"`, `"n/a"`, or similar
  is interpreted as SQL NULL, missing value, operator, control flow, or any other semantic;
- the compiler does not special-case string content to infer missing typed semantics.

Semantic `IS NULL`, `IS NOT NULL`, typed numeric comparison, or non-equality semantics remain
**unrepresentable** in this input contract. Supporting them requires a separately authorized upstream
typed filter contract carrying explicit predicate/operator/value semantics.

The existing fail-closed rule for non-textual dimensions with untyped string payloads remains.

reason:
Rejecting the literal token `"NULL"` merely because it resembles SQL NULL is itself semantic
interpretation from string content. P4 must preserve the certified equality payload rather than build
a sentinel/keyword patch table.

status: SEALED.


---

## DMP-DEC-0015 — aggregation references stabilize by same-stage aggregation index, not UUID shape

date: 2026-09-22

evidence:
Pinned Metabase v0.63.18 live output showed the remaining canonical drift at:

`$.stages[0].order-by[0][2][2]`

The portable P4 query expresses ranking as:

`["aggregation", {}, 0]`

Pinned v0.63.18 representations repair converts integer aggregation references into canonical
aggregation UUID references. Metabase's own `metabase.lib.equality` stage comparison explicitly
builds `aggregation UUID -> index` maps on each side and compares aggregation references by their
same-stage index rather than by raw UUID value.

decision:
Dima durable canonical stabilization may rewrite only an aggregation-reference target that satisfies
**all** of these conditions:
1. clause head is exactly `"aggregation"`;
2. the target is a string;
3. the target exactly matches a `lib/uuid` belonging to one aggregation clause in the same stage;
4. that same-stage aggregation UUID mapping is unique.

The stable form rewrites that target to its 0-based same-stage aggregation index, then the existing
exact-key `lib/uuid` removal runs.

No UUID-format recognition is used. Unknown/unmatched aggregation-reference strings remain unchanged
and therefore continue to participate in exact equality/fingerprinting.

reason:
This mirrors the pinned runtime's own aggregation-reference equality semantics and reverses the
documented index -> runtime UUID representation rewrite without treating arbitrary UUID-looking
values as volatile.

status: SEALED.


---

## DMP-DEC-0016 — P4 initial compiler slice is certified; no semantic expansion in closure

date: 2026-09-22

decision:
The initial P4 `ResolvedAnalyticsIntent + DimaExecutionBindingSnapshot -> portable MBQL -> pinned
Metabase canonical serialized query` slice is certified GREEN at
`0af815887d8e50274b39bdb7975eb37e6e63971a`.

Certified scope remains intentionally narrow:
- one governed metric;
- frozen mechanical aggregation vocabulary;
- same-table dimensions;
- textual literal equality filters;
- resolved time bounds;
- previous-period comparison;
- ranking/limit;
- current-catalog anti-drift;
- deterministic durable canonical identity after only the two proven runtime-identity transforms:
  exact `lib/uuid` removal and exact same-stage aggregation-ref UUID -> index stabilization.

No new aggregation aliases, typed filter inference, NULL predicates, cross-table joins, formula
compiler, fuzzy matching, Metabase semantic lookup, product routing, or Wren retirement are implied.

status: SEALED / P4 CLOSED GREEN.


---

## DMP-DEC-0017 — P5 access fingerprint is a separate proven identity, never an alias of principal fingerprint

date: 2026-09-22

question:
Can P5 satisfy `execution_access_fingerprint` by reusing the existing
`PrincipalContextRef.fingerprint`?

evidence:
- `PrincipalContextRef.fingerprint` contains tenant binding, principal subject and roles only;
- R10.1 additionally requires attribute-policy identity, policy version, RLS/CLS versions,
  database route/destination, impersonation, semantic context, source object refs and security
  parameters;
- current `LegacyV2QueryReceiptWriter` aliases the two fingerprints only as an M1 compatibility
  artifact;
- P4 lab execution used an admin session and does not prove tenant/user/access-lens parity.

decision:
No. P5 introduces an explicit immutable `ExecutionAccessSnapshot` and derives the official
`execution_access_fingerprint` from that complete snapshot. The P5 receipt sealer requires the
snapshot and fail-closes when it is absent or inconsistent with the resolved intent/canonical
resource identity.

The existing legacy alias is classified `M1_COMPAT_ONLY` and is not P5 certification evidence.

scope:
P5 execution/receipt identity.

invariants:
- principal fingerprint and access fingerprint are distinct concepts;
- no guessed access-policy fields;
- no missing-principal service/admin fallback;
- official receipt access snapshot required;
- P4 canonical query fingerprint remains query identity owner;
- source branch/read path unchanged.

rejected_shortcuts:
- hash only tenant/user/roles and call it access identity;
- set missing policy fields to empty/zero without an attested meaning;
- use Metabase admin session as a tenant-user access proof;
- defer the issue while marking P5 GREEN.

revisit_condition:
Only if the normative R10.1 security contract changes under a new explicit decision.

status: SEALED.


---

## DMP-DEC-0018 — receipt event identity vs durable execution fingerprint; P5 contract vs P10 issuer

date: 2026-09-22

decision:
- `canonical_query_fingerprint` = durable query identity owned by P4;
- `execution_access_fingerprint` = durable effective-access identity defined by P5 and issued in production by P10;
- `receipt_fingerprint` = deterministic execution-content fingerprint binding authority, projection,
  resolved intent, canonical query, access, semantic context, resources, runtime, step role,
  result hash and row count;
- `receipt_id` = execution-occurrence identity and includes explicit `execution_id`;
- `executed_at` = event metadata and is not folded into `receipt_fingerprint`.

P5 may close **CONTRACT GREEN** when the immutable `ExecutionAccessSnapshot` contract and strict
receipt sealer are complete and proven provider-free. P5 does not implement or guess the production
effective-access issuer.

DMP-P5-BLOCK-001 is transferred to the P10 security-mapping gate. Until P10 proves a real issuer,
production official receipt issuance remains blocked; P6/P7/P8/P9 development is not blocked by that
issuer work.

No secret/session token is durable identity. No default/guessed policy, RLS/CLS, database route,
principal or admin fallback is authorized.

status: SEALED.


---

## DMP-DEC-0019 — P6 parity uses one physical PostgreSQL snapshot

date: 2026-09-22

evidence:
Current Wren trust-plane tests execute boyahane DuckDB while Metabase P4 executes a separate synthetic
PostgreSQL orders dataset. Numeric comparison between them would be an invalid oracle.

decision:
P6 uses the pinned Metabase lab's analytics PostgreSQL as the single physical parity snapshot for both
arms. Wren reaches that exact database through its native PostgreSQL connector. A P6-only loopback
Compose override may expose analytics-db to the CI host; base M2 compose and its no-host-port default
remain unchanged.

P6 seed/manifest are isolated test artifacts. No production datasource routing changes.

result semantics:
MATCH, TYPED_GAP, or UNEXPLAINED_MISMATCH. Typed gaps remain visible and are not counted as parity.

status: SEALED.


---

## DMP-DEC-0020 — P6 broad corpus deferral and risk-based parity strategy

date: 2026-09-22

supersedes:
The exact 80-case corpus freeze/full-parity requirement as a **P6 closure gate**. It does not remove
later integrated Standard certification.

evidence:
- P6A0 proves the shared physical PostgreSQL snapshot and independent golden anchors;
- P6A1 exercises the true post-authority substrate seams;
- the first three same-intent cases already expose independent typed capability gaps:
  `SUBSTRATE_RUNTIME_GAP` and `WREN_COMPATIBILITY_GAP`;
- repeatedly exercising known gaps at large volume before P7-P13 architecture work has low
  information value and would be repeated after those layers change.

decision:
P6 is an early architecture/capability measurement milestone, not a declaration that Wren and
Metabase are equivalent.

P6 may close when:
- P6A0 shared snapshot + independent golden anchors pass;
- the same accepted Dima intent identity is offered to both real substrate seams;
- the thin Metabase adapter executes real structured queries;
- the real Wren seam is attempted without P6 product patching;
- every observed difference is either MATCH or an exact typed gap;
- `UNEXPLAINED_MISMATCH = 0`;
- raw-language reinterpretation, semantic search, fuzzy/regex/morphology authority, named-case
  product patches and silent fallback remain zero.

The broad cross-engine parity pack moves to integrated Standard certification, preferably around P14
after P10-P13 security/resource/entity-value work. That later pack is risk/capability weighted rather
than fixed to 80 cases; material families receive high-information positive and negative/edge proofs.

The final natural-language integrated evaluation remains separate (`DEV80` exactly once plus
Validation50/Hidden50).

status: SEALED.


---

## DMP-DEC-0021 — P7 closes as a loss-aware semantic migration baseline

date: 2026-09-22

evidence:
- P7 implementation SHA `2e233ea6122c9cc0ccc18ebe2978e2e896ebb41c`;
- P7 workflow `35772646640 = SUCCESS`;
- focused structured importer = 8 PASS;
- inherited provider-free regressions = 13 PASS / 2 SKIP;
- M1/Wren workflow `35772646558 = SUCCESS`;
- governance `35772646510 = SUCCESS`;
- current final composed demo MDL imports deterministically.

real composed inventory:
- 80 models;
- 23 cubes;
- 136 measures;
- 121 regular dimensions;
- 23 time dimensions;
- 31 relationships;
- 1 view;
- duplicate model/cube/relationship names = 0;
- missing cube baseObject targets = 0;
- dimension/time name overlap = 0.

observed typed representation gaps:
- 31 textual relationship join conditions lack structured JoinKeySpec;
- 29 calculated/derived dimension expressions are not exact physical columns;
- 25 calculated model columns are opaque in the current DimaSemanticSpec;
- 23 cube-level semantic entity surfaces have no top-level Dima owner;
- 1 view definition remains opaque;
- structured relationship-origin dimensions observed = 9, unresolved origin = 0.

decision:
P7 does not parse SQL/formula/join-condition text merely to make migration appear lossless.
The first importer establishes deterministic Dima-owned identity for structurally representable metric,
dimension, time and lineage surfaces and emits exact typed gaps for material source richness that the
current canonical spec cannot yet represent.

Those gaps become explicit P8 equivalence-matrix inputs. P8 decides whether each capability is:
`NATIVE_METABASE`, `DIMA_COMPILED`, `DIMA_RUNTIME`, `WREN_ONLY_GAP`, or `UNSUPPORTED`.

A later change to DimaSemanticSpec is allowed only when P8 proves a concrete canonical representation
need; importer convenience or gap-count reduction alone is not sufficient.

status: SEALED.


---

## DMP-DEC-0022 — P8 equivalence is a conservative capability matrix, not a parity score

date: 2026-09-22

evidence:
- P8 implementation SHA `23480aa433ba10fed84a015a85c9f1d88b31572e`;
- P8 workflow `35773470252 = SUCCESS`;
- focused P8 equivalence proof = 14 PASS;
- P7 importer regression = 8 PASS;
- M1/Wren workflow `35773470027 = SUCCESS`;
- governance `35773470111 = SUCCESS`.

decision:
P8 classifies each typed semantic surface independently as:
`NATIVE_METABASE`, `DIMA_COMPILED`, `DIMA_RUNTIME`, `WREN_ONLY_GAP`, or `UNSUPPORTED`.

The matrix is not a score and does not incentivize patches.

Opaque Wren formulas are not text-parsed into false native equivalence. Exact physical
dimension/time lineage may be native. Structured Dima relationship contracts may be Dima-compiled.
Security and Dima-owned terminology remain runtime/ownership concerns. Unknown P7 gap codes fail
closed.

A `WREN_ONLY_GAP` may be removed only by a separately proven canonical/compiler/runtime capability,
not by relabeling, regex parsing or Metabase name discovery.

status: SEALED.


---

## DMP-DEC-0022 — P9A lifecycle closure and P9B transport is resource-kind specific

date: 2026-09-22

P9A closure evidence:
- implementation/hardening SHA `7820ac77207f4245da150a5c80043d22708b87f0`;
- P9 workflow `35778418835 = SUCCESS`;
- focused P9A = 23 PASS;
- inherited P7/P8 = 39 PASS;
- M1/Wren `35778418797 = SUCCESS`;
- governance `35778418759 = SUCCESS`.

decision:
P9A desired-state planning is GREEN, including stale lifecycle, binding context/version coherence,
rollback-required mutation planning, exact locator behavior and one real composed P7→P8→explicit
policy→P9 proof.

P9B must not implement a generic resource CRUD client. Exact pinned Metabase v0.63.18 source shows
different lifecycle surfaces by resource kind:
- metrics are Card-backed content (`type="metric"`);
- dimensions are metadata attached to existing synced Fields;
- time semantics have no independent createable resource surface;
- relationship/FK metadata is attached to existing Fields and is not an arbitrary Dima relationship object.

Therefore every P9B transport kind requires its own proven representation contract. Unsupported
mutation surfaces are typed transport gaps, not workarounds.

status: SEALED.


---

## DMP-DEC-0023 — P9B metric persistence uses pinned Agent metric surface, not generic Card reconstruction

date: 2026-09-22

pinned source:
`metabase/metabase@2ba2485c78d7e00a9a25f82c00fc201da71590c4`

evidence:
- `POST /api/agent/v2/construct-query` returns a base64-encoded MBQL query;
- pinned `POST /api/agent/v1/metric` explicitly accepts that base64 query and saves a Card of
  `type=metric`;
- pinned metric endpoint validates the saved query has exactly one aggregation and at most one
  date/datetime grouping;
- pinned `PUT /api/agent/v1/metric/:id` updates only an existing metric Card and re-validates a
  replacement query;
- Agent create mirrors query-run and collection-create permission checks;
- Agent update starts with Card write-check and re-checks permissions when query/collection changes;
- Card model derives `:hook/entity-id`; insert generates NanoID when none is supplied;
- Agent create response returns numeric Card id but not entity_id; exact follow-up
  `GET /api/card/:id` may be used to read the created Card identity. Name search is forbidden.

decision:
P9B will not recreate Metabase's Card query persistence contract or add mutation methods to the P3
execution client.

A separate resource-transport boundary may consume an already-certified P4 canonical serialized query
and construct the exact Agent metric request.

P9B1 is provider-free and CREATE-only:
`ProvisionAction(CREATE metric) + CanonicalProjection + explicit collection_id
→ MetricCreateRequest`.

It must prove exact identity/context/query-shape coherence before any HTTP write code is authorized.

status: SEALED.


---

## DMP-DEC-0024 — P10 owns faithful issuance of the existing P5 access snapshot

date: 2026-09-22

decision:
P10 will not create a second durable access-identity model.

The durable execution-access contract remains P5 `ExecutionAccessSnapshot`.
P10 owns the production-grade evidence/mapping chain that is allowed to issue that snapshot.

Exact ownership:
- Dima current principal identity comes from the authenticated `control_plane.authorize.Principal`;
- accepted analytics identity comes from `ResolvedAnalyticsIntent.principal`;
- semantic/source identity comes from the accepted intent + canonical projection;
- effective policy/RLS/CLS/database-route/security facts must come from explicit authoritative
  security/runtime owners;
- Metabase session/service identity must be explicitly attested; possession of a session token alone
  is not a durable principal identity.

If any required snapshot field cannot be faithfully established, issuance fails closed.
Missing tenant/principal may not fall back to superadmin, service account, root collection, or a
different user. Superadmin execution still requires an explicit effective tenant/data lens before a
tenant-bound Standard analytics receipt may be issued.

Production official P5 receipt issuance remains blocked until P10 closes
`DMP-P5-BLOCK-001`.

status: SEALED.


---

## DMP-DEC-0025 — split P10 live proof into basic revocation and advanced data-lens proof

date: 2026-09-22

decision:
P10 live security certification has two independent evidence classes.

```text
P10B1
  authenticated Metabase subject
  basic data/query permission
  revocation under same session
  no admin/service fallback
  restore
  explicit permission revision evidence

P10B2
  row restriction
  column restriction
  sandbox / impersonation / database-route lens
  cross-lens cache/read isolation
  faithful RLS/CLS version issuance
```

P10B1 may run against the current pinned OSS lab.

P10B2 may not be simulated by role names or fake digest strings. It requires a real capability owner
(premium Metabase feature, DB-native security route, or another explicitly governed mechanism).

P10A + P10B1 do not close DMP-P5-BLOCK-001 by themselves.

status: SEALED.


---

## DMP-DEC-0026 — LLM-first cognition + adaptive governance + semantic necessity gate

date: 2026-09-23

clarifies:
The Metabase-platform architecture keeps Dima-owned semantic/security/evidence truth while making the
LLM the default owner of analytical cognition. This does not replace DimaSemanticSpec and does not
roll back P7-P10.

binding principles:

### LLM_FIRST_COGNITION

Default cognition owner is the LLM:
- analytical strategy;
- hypothesis generation;
- evidence-selection strategy;
- next-tool choice;
- adaptive replanning;
- interpretive synthesis;
- report reasoning.

Dima deterministic code must not recreate these functions merely because they can be expressed as a
state machine.

### SEMANTIC_CORE_IS_NOT_ANALYTICAL_PLANNER

DimaSemanticSpec remains canonical business truth:
metric/dimension/relationship/time identity, grain, additivity, semantic version, source lineage,
security metadata, business rules and managed-resource policy.

It is not a universal research-plan or root-cause sequencing language.

### MINIMUM EXECUTION ENVELOPE

There is no anonymous/unscoped/admin-default Level 0.

Even the thinnest native path is:

```text
LLM cognition
→ Dima minimum security/execution/provenance envelope
→ Metabase
→ Dima receipt/evidence
```

Minimum envelope:
authenticated principal, tenant binding, effective-access enforcement, database/resource boundary,
execution identity, basic provenance and receipt/evidence identity.

### ADAPTIVE_GOVERNANCE

Progressive semantic depth:
- Level 0 — native analytics + mandatory minimum Dima security/execution/provenance envelope;
- Level 1 — canonical metric/dimension identity, aliases, basic governed time, lineage, version;
- Level 2 — approved relationships, grain, additivity, advanced time/security/business lens;
- Level 3 — sector/decision semantics, business rules, decision skills, specialized governed workflows.

Effective governance may never be freely downgraded by the model:

```text
effective level
>= tenant minimum
>= capability-required minimum
>= security-required minimum
```

LLM may request escalation. It may not lower a mandatory level.

No generic GovernancePlanner/AdaptiveSemanticRouter framework is authorized merely to encode this
documentation. Implementation waits for a concrete front-door/onboarding owner.

### SEMANTIC_NECESSITY_GATE

Before adding a new deterministic semantic/cognition mechanism:
1. freeze a small high-information corpus, normally 5-20 cases;
2. keep data, tools, prompt contract, semantic config, permissions, runtime and truth oracle fixed;
3. run Luna first as default/economic baseline;
4. run Sol on the exact same corpus as cognition ceiling;
5. classify failure before adding architecture;
6. add only the minimum generic guardrail if a material correctness/security/trust failure remains;
7. rerun the same corpus;
8. record Architecture Value Delta.

Interpretation:
- Luna PASS + Sol PASS -> do not add deterministic mechanism by default;
- Luna FAIL + Sol PASS -> MODEL_COGNITION_GAP; prefer bounded context/tool-description or selective
  Sol escalation before permanent deterministic cognition;
- Luna FAIL + Sol FAIL on material semantic/security/provenance truth -> deterministic guardrail may
  be justified;
- any model violating mandatory security/trust invariant -> deterministic enforcement required.

No model-specific prompt branch, hidden example enrichment, or different tool/data contract is allowed
during the A/B.

Project model policy:
`LUNA = DEFAULT / ECONOMIC BASELINE`
`SOL = CEILING / HEADROOM MEASUREMENT`.

A Sol-only capability may be certified only as `SOL_ESCALATION_CAPABILITY`; it is not
`LUNA_DEFAULT_CERTIFIED`.

### Architecture Value Delta

Every proposed deterministic cognition/semantic mechanism must show that verified-success,
silent-wrong/security correctness, latency/cost/tool-call effects justify the added state,
maintenance surface and failure modes. No single scalar score is required.

### controlled harvest

Fast Track and ask-v2 are moving references, not merge sources. At the owning Platform milestone,
inspect the exact source contract, port only the smallest architecture-independent primitive, retain
Platform security/semantic invariants and prove value on the Platform corpus. No bulk merge or
cherry-pick.

status: SEALED.


---

## DMP-DEC-0027 — minimum entity-value adoption gate; no resolver framework

date: 2026-09-23

evidence:
`DMP-P11-MEASURE-001`.

decision:
Introduce one minimal Dima truth gate around model-proposed entity-value adoption.

The gate is **not** an entity resolver and owns no language cognition.

For a model proposal `BIND(semantic_ref, value)`, adoption is allowed only when all of the following
are already true from typed upstream evidence:

1. the value-binding request has exactly one approved semantic scope;
2. the proposed `semantic_ref` is that approved scope;
3. the candidate value is present by exact structured equality in current-lens evidence for that scope;
4. the evidence carries one coherent current access-lens reference and current-user retrieval state.

If the request still carries multiple approved/admissible scopes, direct BIND is vetoed to
`CLARIFY / AMBIGUOUS_SEMANTIC_SCOPE`.

If the model proposes a scope/value outside the approved evidence, adoption is blocked/typed-invalid.
No nearest string, translation table, regex, fuzzy similarity, stemming, morphology, SQL parsing,
physical-field guessing or global search is authorized.

The LLM remains cognition owner:
- it understands `Kuzey`;
- it may choose BIND/CLARIFY/NO_MATCH;
- it writes the clarification/synthesis.

Dima owns only the trust invariant:
`unresolved semantic scope cannot silently become canonical value authority`.

The P11 frozen corpus, retrieval evidence, prompt, model ids and oracles remain unchanged for the
post-guardrail rerun.

success criterion:
- raw model telemetry remains visible;
- EV-03 raw BIND may occur, but official guarded outcome must be CLARIFY;
- EV-01/02 exact safe binds remain allowed;
- EV-04 missing value remains non-bind;
- official silent-wrong = 0 across the same runnable corpus;
- if satisfied, deterministic **resolver** remains NOT_NEEDED for P11 V1.

status:
`SEALED / MINIMUM GUARDRAIL IMPLEMENTATION AUTHORIZED`.


---

## DMP-DEC-0028 — P12 BI workspace composition closure

date: 2026-09-23

question:
Which BI/workspace composition should the Platform use initially without transferring Dima semantic
authority to Metabase or prematurely implementing frontend/workspace integration?

options_considered:
- `DIMA_SHELL`;
- `HEADLESS_API`;
- `LINK_OUT`;
- `EMBED`;
- combinations of the above.

evidence:
- `P12_PREDEVELOPMENT_REVIEW.md` classifies P12 as product/workspace feasibility, not semantic cognition.
- `P12_UX_MODE_EVIDENCE_MATRIX.md` classifies all four modes and records the initial composition.
- `P12_BI_WORKSPACE_FEASIBILITY.md` selects the same composition and assigns P13 as the next integration owner.
- pinned Metabase v0.63.18 already provides mature dashboard/question/collection/query-builder workspace
  capability, but availability is not equivalent to Dima semantic authority or production security
  certification.
- audited functional baseline `4b60bc3f1e6ab9526cd590a0989c1b227c5c43be` remains the last
  product baseline; `56799687d2a8018dd60b0b909fb8b0be5d4a79c7` differs only by handoff/status
  documentation.
- baseline P11 workflow `35816646368 = SUCCESS`, baseline governance
  `35816646416 = SUCCESS`, handoff governance `35817394598 = SUCCESS`.
- takeover moving-reference observation: ask-v2 `d430680a02256f4b9612730bd79b2e938a134132`,
  Fast Track `5280dd37451ded59ce181b93b015bc9dfafe0696`; both remain reference-only and provide
  no new evidence requiring P12 harvest or reclassification.

decision:
```text
initial product shell          = DIMA_SHELL
analytics integration          = HEADLESS_API
mature workspace escape hatch  = LINK_OUT
EMBED                           = DEFERRED / MEASURED ESCALATION ONLY
```

P12 is closed as a feasibility/classification milestone only.

scope:
Product/workspace composition classification. No frontend/workspace integration implementation is
authorized by this decision.

invariants:
- Metabase Card/Dashboard/Question/Collection/UI navigation are not Dima semantic authority.
- Dima UX remains the primary product shell.
- Metabase remains analytics/workspace substrate.
- P10B2 advanced security gaps remain typed/open.
- `DMP-P5-BLOCK-001` remains OPEN.
- no Fast Track or ask-v2 harvest occurs during P12 closure.

rejected_shortcuts:
- frontend rewrite;
- Metabase frontend fork;
- collection/dashboard sync;
- embed implementation without measured need;
- bulk Fast Track import;
- treating Metabase UI/content names as business truth.

revisit_condition:
Revisit EMBED only after a measured continuity/context requirement plus explicit auth/session/
entitlement/security evidence. LINK_OUT context handoff and mobile/responsive behavior remain later
product implementation questions.

status:
`SEALED / P12 BI WORKSPACE FEASIBILITY = CLOSED / CLASSIFICATION GREEN`.

---

## DMP-DEC-0029 — P13 single-preparation Standard integration boundary

date: 2026-09-23

question:
What exact sequencing may P13 use to wire the already-certified semantic, security, query,
receipt and evidence contracts into the first real Metabase Standard vertical without introducing a
second semantic/access owner or authorizing a different query than the one executed?

evidence:
- `StandardProjection.filter_handles` are resolved by `ResolvedAnalyticsIntentBuilder` through
  `SemanticHandleRegistry` to `V2ResolvedFilterRef`, whose canonical target already contains both
  the dimension and the string value. Therefore a sealed filter handle already carries material
  filter meaning.
- `EntityValueAdoptionGate` is a minimum truth gate and does not own scope discovery, retrieval,
  translation, search or analytical planning.
- `ExecutionAccessSnapshotIssuer.issue` requires the accepted `ResolvedAnalyticsIntent`, the exact
  `CanonicalProjection`, the current principal and `VerifiedExecutionSecurityFacts`.
- current `MetabaseSubstrateAdapter` requires an `ExecutionAccessSnapshot` at construction while
  `execute_execution_intent` performs compile + canonicalize internally. Naively preparing once for
  authorization and again inside the adapter would create two prepared query instances across the
  trust boundary.
- `CanonicalProjection` is frozen and carries authority/projection/resolved-intent/catalog/query
  identity; `DimaQueryReceiptSealer` verifies these exact identities plus the P5/P10 access snapshot.

decision:

### P13A/B metric-only sequencing
```text
AcceptedStandardAuthority
→ ResolvedAnalyticsIntent
→ PREPARE ONCE
   MetabaseProjectionCompiler
   → MetabaseCanonicalizer
   → exact frozen CanonicalProjection
→ P10 ExecutionAccessSnapshotIssuer
   using current principal + truthful VerifiedExecutionSecurityFacts
→ EXECUTE THAT SAME CanonicalProjection
→ DimaQueryReceiptSealer using that same projection
→ VERIFIED EvidenceArtifact
```

No second compile, no second canonicalization and no query reconstruction are allowed on the P13
production vertical.

A narrow new P13 orchestration owner is planned at
`backend/app/v3/standard_execution.py`.
It coordinates existing owners; it is not a generic workflow/planner framework.

The minimum expected prior-owner change, only if provider-free implementation proves it necessary, is
a prepared-execution entry point in
`backend/app/v3/substrate/metabase/execution_adapter.py` that executes an already-created
`CanonicalProjection` without recompiling/recanonicalizing it. Existing certified P4/P5/P10
semantics are reused, not redefined.

### P13C filter-value ordering
For production use of P11 value evidence, value adoption occurs before final filter semantic-handle
minting and before `AcceptedStandardAuthority` sealing:

```text
LLM cognition
→ Dima-governed semantic scope candidates/bindings
→ Dima scope admissibility
→ authenticated current-principal Metabase value retrieval
→ narrow retrieval attestation/reference
→ LLM structured value proposal
→ EntityValueAdoptionGate
→ final governed textual filter binding / semantic handle
→ SemanticSurfaceCoverage complete
→ AcceptedStandardAuthority sealed
→ ResolvedAnalyticsIntent
```

An accepted Standard authority is never mutated after sealing.

Initial P13 filter capability is **exact string-valued equality only**. Non-string approved values,
typed comparison, NULL/IS NOT NULL and range remain typed capability gaps; no coercion or
`str(value)` fallback is allowed.

### Access timing / DMP-P11-INTEGRATION-005
Candidate-value retrieval may precede the final P10 snapshot. It therefore receives a narrow retrieval
attestation/reference, not a second durable access fingerprint. The attestation must preserve the
authenticated Metabase subject, tenant/principal, semantic-context and source-resource identity.
Before the bind/execution becomes official, P10 issuance must prove coherence and include the
retrieval proof in the facts/attestation chain. The sole durable access identity remains
`ExecutionAccessSnapshot.execution_access_fingerprint`, which is carried into the strict receipt.

`DMP-P11-INTEGRATION-005` remains OPEN during P13A/B and is owned for closure by P13C.

### Security profile
P13B may certify only an isolated **BASIC AUTHENTICATED LAB PROFILE** whose facts can be truthfully
established from the current authenticated Metabase user, exact basic query permission state and one
known DB route, following the existing P10B1 proof shape. `VerifiedExecutionSecurityFacts` remains a
P10-owned attested input; P13 does not discover or invent security facts.

`DMP-P5-BLOCK-001` remains OPEN. No global production-security claim follows from the P13B canary.

scope:
P13 predevelopment sequencing only. This decision does not authorize P13 product code yet.

invariants:
- LLM = cognition; Dima = semantic/security/provenance/evidence truth; Metabase = execution.
- AcceptedStandardAuthority XOR AcceptedTurnContract.
- no hidden third Metabase semantic authority.
- no second durable access fingerprint.
- no front-door changes in P13A/B.
- no Wren fallback on accepted Metabase Standard execution failure.
- no Wren deletion.
- no raw SQL, label guessing, implicit FK authority or display-name execution identity.
- P4 compiler/canonical semantics, P5 receipt semantics, P10 fingerprint definition and P11 adoption
  semantics remain frozen unless a classified RED proves their owner defective.

rejected_shortcuts:
- seal Standard authority and then mutate filter meaning;
- compile/canonicalize twice around authorization;
- invent value-access fingerprints;
- stringify non-string P11 values;
- fake `VerifiedExecutionSecurityFacts`;
- use admin analytical fallback;
- re-enter legacy V2 `SemanticResolver → CubePlanner`;
- merge/cherry-pick/rebase ask-v2 or Fast Track.

revisit_condition:
Only a classified P13 RED may reopen one of the existing certified owner contracts. Any new cognition
mechanism requires the semantic-necessity protocol.

status:
`SEALED PREDEVELOPMENT DECISION / P13 IMPLEMENTATION NOT AUTHORIZED PENDING SUPERVISOR REVIEW`.


---

## DMP-DEC-0030 — Metabase native engine seam evaluation

date: 2026-09-23

question:
Are we losing material Metabase analytical capability because the Platform is integrating at the
Agent API primitive seam instead of preserving Metabase's native Metabot/analytics-engine runtime?

status:
`HYPOTHESIS ACCEPTED FOR MEASUREMENT / ARCHITECTURE DECISION NOT YET MADE`.

source evidence:
- pinned runtime/source remains Metabase `v0.63.18 / 2ba2485c78d7e00a9a25f82c00fc201da71590c4`;
- `src/metabase/agent_api/api.clj` exposes headless BI primitives including search,
  construct-query, query, execute, read-resource and content endpoints;
- `src/metabase/metabot/api.clj` endpoint `POST /api/metabot/agent-streaming` invokes
  `metabase.metabot.agent.core/run-agent-loop`;
- `src/metabase/metabot/agent/profiles.clj` resolves profile-specific model/tool configuration;
  the NLQ profile has max 10 iterations and exposes native resource retrieval, resource reading,
  notebook-query construction, navigation and chart tools;
- the native agent core owns iterative tool-result feedback, terminal-tool handling and turn-local
  agent state instead of being equivalent to one Agent API primitive call;
- `cagataysntrk/metabase-boyahane@f0c4a6b053ead52ca2eac80002c448323dc34a35`
  is a realistic 80-table / 462,962-row fixture but currently uses
  `metabase/metabase:latest`, so its working vanilla runtime identity is not reproducibly pinned;
- Fast Track current moving reference observed at opening:
  `30659f7892ce2d4eafffec89716b75e2ce09ea48`;
- ask-v2 current moving reference observed at opening:
  `d8759c9cfe388560084a2886dd443c32c6346788`.
  Both remain read-only reference.

seams under evaluation:
```text
V0 = vanilla Metabase product

A  = external Dima cognition
     → Agent API primitives

B  = Dima/lab client
     → /api/metabot/agent-streaming
     → native run-agent-loop

C  = thin fork/in-process bridge
     → native run-agent-loop

D  = thin native runtime
     + minimum Dima trust hooks
```

decision:
Open `P12X — METABASE NATIVE ENGINE / FORK SEAM EVALUATION`.

Initial authorized measurement is **V0 + A + B only**.
Seam C/D are explicitly not authorized before the first supervisor checkpoint.

P13 disposition:
`P13 PAUSED FOR METABASE SEAM DECISION`.

DMP-DEC-0029 and the existing P13 predevelopment/ticket are retained. Their durable invariant remains:
the exact execution artifact authorized by Dima must be the artifact actually executed and receipted.
Only the future substrate seam may change.

measurement invariants:
- do not decide by preference;
- freeze Boyahane data identity and schema;
- freeze exact working vanilla Metabase image/version/digest;
- run a separate pinned v0.63.18 control;
- same task/database snapshot/authenticated user/permissions/model/provider across seams where technically possible;
- native Metabot keeps its own profile prompt, skills, tool descriptions, memory and state;
- approximately 12–16 high-information tasks, not DEV80;
- every case has an independent DB/clarification/gap oracle;
- Luna is primary/economic baseline; Sol is differential-only if a capability difference remains ambiguous;
- compute `VANILLA_CAPABILITY_RETENTION` in addition to absolute success;
- classify security, semantic authority, retrieval, orchestration, query construction and model cognition failures separately.

forbidden:
- P13 product implementation while P12X is open;
- `standard_execution.py` / `execute_prepared()`;
- product routing;
- Wren retirement;
- frontend rewrite;
- P4/P5/P10/P11 mutation;
- modifying `metabase-boyahane`;
- creating a Metabase fork before V0+A+B results;
- merge/cherry-pick/rebase/write to ask-v2 or Fast Track;
- interpreting DMP-DEC-0028 HEADLESS_API product composition as a permanent Agent-API engine selection.

revisit_condition:
After the V0+A+B checkpoint:
- if B approximately retains Vanilla and A materially loses it, classify
  `NATIVE_RUNTIME_MATERIAL_ADVANTAGE` and return for Seam C authorization;
- if A approximately equals B approximately equals Vanilla, investigate version/dataset/metadata/model/
  permissions/frontend-context confounders before any fork;
- if Agent API retains the relevant capability, resume P13 with DMP-DEC-0029 as written.

status:
`SEALED / P12X V0+A+B MEASUREMENT AUTHORIZED / C+D NOT AUTHORIZED`.


---

## DMP-DEC-0031 — thin Metabase fork as primary production-engine candidate

date: 2026-09-23

supersedes:
Only DMP-DEC-0030's prerequisite that Seam C/fork bootstrap must wait for completion of the full V0+A+B Agent-API bake-off. DMP-DEC-0030 history and source/runtime findings remain intact.

evidence:
- current-corpus native sanity is executable GREEN: workflow `35824464298`, job `107063206949`;
- corpus fingerprint `fd6e5934438795f64e9ec7d64b74b56056c3c1304aa51598d18c170839b792a0`;
- pinned native Metabot `v0.63.18 / 2ba2485` selected exact Boyahane `public.satis_siparisleri`, generated the query, executed scalar `126`, and matched independent oracle `126` with provider/tool errors `0`;
- native Metabot retains profiles, skills, engine-local memory/state, iterative tool-result feedback, MBQL/query construction and permission-aware orchestration that Dima must not reimplement.

decision:
A thin upstream-derived Metabase fork is the principal production-engine candidate.

```text
DIMA PRODUCT
→ DIMA CONVERSATION / DECISION INTELLIGENCE
→ DIMA SEMANTIC + SECURITY + EVIDENCE CONTROL PLANE
→ DIMA ENGINE BRIDGE
→ DIMA METABASE ENGINE
→ native Metabot + profiles + skills + memory/state + MBQL + Query Processor + drivers
→ CUSTOMER DB
```

Fork identity:
```text
target repo          = UpcyTech/dima-metabase-engine
upstream             = metabase/metabase
initial tag           = v0.63.18
initial upstream SHA  = 2ba2485c78d7e00a9a25f82c00fc201da71590c4
initial engine rev    = 0.63.18-dima.0
```

The repository must preserve upstream Git history. Blank-repo/source-copy bootstrap is forbidden. Existing `UpcyTech/dima-metabase` remains untouched.

ordered stages:
```text
P12X-C0 = exact fork bootstrap + source build; modified existing upstream source files = 0
P12X-C1 = stock-vs-fork native capability parity on 4–6 frozen high-information cases
P12X-C2 = stable Dima engine bridge + bridge/native parity
P12X-C3 = upstream-sync + DIMA_PATCH_SURFACE certification
P13     = Production Standard over Dima Metabase Engine
```

C1 closure requires `FORK_CAPABILITY_RETENTION = 100%` of stock-PASS tasks, new silent wrong = 0, permission regression = 0, dataset-scope drift = 0. Material stochastic divergence is repeated only on the divergent case twice with prompt/data/model unchanged.

C2 bridge is deliberately thin: stable engine identity, correlation/trace identity, native request delegation and native stream/result observation. It must reuse the closest native Metabot orchestration boundary and must not reimplement `run-agent-loop`, profiles, skills, memory, tool registry or query construction.

DIMA_PATCH_SURFACE is mandatory from C0: upstream base SHA, engine HEAD, modified pre-existing upstream files, Dima-specific files, deleted upstream files, upstream-owned line delta, Dima integration LOC, sync conflicts/manual interventions, upstream-test failures and Dima-test failures.

ownership direction:
```text
USE_NATIVE      = run-agent-loop, profiles, skills, engine-local state, tool registry, MBQL, query construction/repair, Query Processor, drivers, native BI primitives
WRAP/HOOK_NATIVE= permission-aware execution and later proven material trust transitions
DIMA_OWNS       = DimaSemanticSpec, business relationships/grain/additivity, tenant/principal product truth, ExecutionAccessSnapshot, QueryReceipt, Evidence lifecycle, durable conversation/research/decision lineage, Decision Skills/Sector Packs
```

P13 is reframed as `P13 — PRODUCTION STANDARD OVER DIMA METABASE ENGINE` and remains `PAUSED UNTIL FORK CAPABILITY PARITY + STABLE ENGINE BRIDGE`. Do not implement Agent-API production Standard, `standard_execution.py`, `execute_prepared()` or P13 governance hooks yet.

DMP-DEC-0029 remains valid at trust level: the material execution artifact Dima authorizes must be the artifact actually executed and receipted. `CanonicalProjection` is retained; its native-engine role is decided later in P13.

full bake-off disposition:
The 16-case P12X corpus is retained, but full V0+A+B Agent-API bake-off is `DEFERRED / NOT FORK-BLOCKING` and becomes a later native capability regression/stabilization asset.

distribution:
One Dima Metabase Engine artifact serves SaaS and self-host. Customer/sector-specific engine source forks are forbidden.

status:
`SEALED / THIN FORK PRIMARY CANDIDATE / C0→C1→C2→C3 AUTHORIZED IN ORDER / P13 GOVERNANCE NOT AUTHORIZED`.


---

## DMP-DEC-0032 — Dima Metabase Engine is a pinned Platform submodule

date: 2026-09-23

question:
How should the upstream-derived Dima Metabase Engine be represented inside the Platform repository
without vendoring Metabase source or losing independent upstream/fork history?

evidence:
- the real fork exists at `UpcyTech/dima-metabase-engine` and preserves
  `metabase/metabase` ancestry;
- C0 source build is GREEN from the fork;
- Platform development needs engine source visible in the same workspace for bridge/parity work;
- copying/subtree-vendoring Metabase into Platform would duplicate history and weaken upstream-sync
  accounting;
- a git submodule records an exact engine commit as a first-class Platform dependency while preserving
  the independent engine repository.

decision:
```text
Platform path     = engine/metabase
dependency type   = Git submodule / mode 160000 gitlink
allowed remote    = https://github.com/UpcyTech/dima-metabase-engine.git
moving branch     = NOT product provenance
source vendoring  = FORBIDDEN
subtree copy      = FORBIDDEN
```

Development order:
```text
engine change
→ engine-owned proof
→ engine commit SHA
→ Platform gitlink bump to exact SHA
→ Platform integration/governance proof
```

The Platform commit is the deployment/integration authority for which exact engine revision it consumes.

governance:
- `.gitmodules` must contain exactly the approved engine path/URL;
- `engine/metabase` must be a Git tree entry with mode `160000`;
- the gitlink must be a 40-hex commit identity;
- Platform CI must fail if the submodule is replaced by a directory/vendor copy;
- engine `main` may move during development, but Platform never consumes it implicitly;
- upstream synchronization stays candidate-only inside the engine repo.

status:
`SEALED / ENGINE SUBMODULE MODEL AUTHORITATIVE`.


---

## DMP-DEC-0033 — Engine upstream-sync mechanism certified candidate-only

date: 2026-09-23

evidence:
```text
engine repo                     = UpcyTech/dima-metabase-engine
engine HEAD                     = c56b71ab23bf2a2d266bac2fba8d165ac059d613
C3 workflow                     = 35835881375 = SUCCESS
C3 artifact                     = 10739391786
artifact digest                 = sha256:267888ba37f29d9a399518d5f70036fd31326fa7f295cacbfdbf795759c2b4d3
self-test candidate             = v0.63.18
candidate SHA                   = 2ba2485c78d7e00a9a25f82c00fc201da71590c4
candidate-only                  = true
main mutated                    = false
source build                    = true
patch-surface C0 assertion      = true
modified upstream files         = 0
deleted upstream files          = 0
upstream-owned line delta       = +0 / -0
Dima-specific files             = 12
Dima integration line delta     = +1321 / -0
```

decision:
The engine upstream synchronization contract is certified as candidate-only:
```text
exact upstream ref
→ local sync candidate
→ conflict report or merge/no-op classification
→ DIMA_PATCH_SURFACE
→ source build
→ smoke
→ sync/<ref> candidate branch
→ explicit manual promotion decision
```

`main` and production are never automatically promoted.

The Platform submodule may now advance from `6bb6924...` to
`c56b71ab23bf2a2d266bac2fba8d165ac059d613`.
The delta contains sync-workflow/governance files only; Metabase runtime source is unchanged.

status:
`SEALED / P12X-C3 UPSTREAM-SYNC CERTIFICATION = GREEN`.


---

## DMP-DEC-0034 — P12X C2 stable native-engine bridge certified; C0→C3 sequence complete

date: 2026-09-23

evidence:
```text
Platform proof SHA                 = 094b5f6e0f1be939172b95fde66cab055c66ae54
governance                         = 35839639348 = SUCCESS
C2 live/parity workflow            = 35839639339 = SUCCESS
C2 artifact                        = 10742000058
artifact digest                    = sha256:c799261cd36499c7579bdf1d6f97ecc07ce0cfaab782afe861deef169d877d94
corpus fingerprint                 = fd6e5934438795f64e9ec7d64b74b56056c3c1304aa51598d18c170839b792a0
engine workspace gitlink           = c56b71ab23bf2a2d266bac2fba8d165ac059d613
upstream base                      = 2ba2485c78d7e00a9a25f82c00fc201da71590c4
runtime tag                        = v0.63.18-dima.0
restricted-user live canary        = GREEN
PX-01 observed/oracle              = 126 / 126
native stream errors               = 0
Agent API analytical fallback      = 0
Wren fallback                      = 0
raw SQL fallback                   = 0
```

C2 bounded direct-native vs typed-bridge parity:
```text
selected cases                     = PX-01, PX-07, PX-13, PX-16
initial material divergence        = PX-07, PX-13, PX-16
required repeats                   = 2 per side / divergent case
reproducible direct-PASS/bridge-FAIL = 0
reproducible new bridge silent wrong = 0
reproducible permission regression   = 0
reproducible dataset-scope drift     = 0
bridge transport contract failures   = 0
stochastic variance                  = PX-07, PX-13, PX-16
final C2 status                      = GREEN
```

interpretation:
The typed Dima bridge does not create a second analytical planner. It delegates one request to the
native Metabot `/api/metabot/agent-streaming` boundary, preserves the ordered native stream and Dima
correlation identity, and retains current-user permissions. The first C2 seam required no Metabase
runtime-source hook.

decision:
```text
P12X-C0 = CLOSED GREEN
P12X-C1 = CLOSED GREEN
P12X-C2 = CLOSED GREEN
P12X-C3 = CLOSED GREEN
P12X fork/bridge/sync sequence = COMPLETE
```

The certified architecture entering the supervisor checkpoint is:

```text
DIMA PRODUCT
→ DIMA CONVERSATION / DECISION INTELLIGENCE
→ DIMA SEMANTIC + SECURITY + EVIDENCE CONTROL PLANE
→ typed DIMA ENGINE BRIDGE
→ pinned DIMA METABASE ENGINE submodule
→ native Metabot / profiles / skills / engine-local state / MBQL / Query Processor / drivers
→ CUSTOMER DB
```

ownership:
- native Metabot retains analytical cognition/orchestration/query construction;
- Dima retains canonical business semantic, security, provenance, evidence and durable decision truth;
- bridge owns transport/correlation/engine identity only;
- no Agent API analytical fallback, Wren fallback or raw-SQL escape is introduced by C2.

P13 disposition:
`P13 — PRODUCTION STANDARD OVER DIMA METABASE ENGINE` remains **PAUSED / NOT AUTHORIZED** at this
checkpoint. DMP-DEC-0029's trust invariant remains binding — the material execution artifact Dima
authorizes must be the artifact actually executed and receipted — but its execution seam must be
re-read/reconciled against the now-certified native-engine bridge before P13 implementation.

The earlier P13 draft must not be resumed mechanically.

status:
`SEALED / P12X C0→C3 COMPLETE / SUPERVISOR CHECKPOINT REACHED / P13 STOP`.


---

## DMP-DEC-0035 — Pre-P13 handoff checkpoint is authoritative

date: 2026-09-23

question:
Is the repository now ready to hand off at the exact supervisor-requested stop point, with P12X C0-C3
closed and P13 still intentionally unopened?

evidence:
```text
Platform current documentation HEAD     = 9179ad880ff0376fed0bb83971c9d61fe87e735c
final functional P12X proof SHA          = 094b5f6e0f1be939172b95fde66cab055c66ae54
current Platform governance              = 35841686789 = SUCCESS
current Platform P12X regression         = 35841687850 = SUCCESS
engine repository                         = UpcyTech/dima-metabase-engine
engine certified HEAD                     = c56b71ab23bf2a2d266bac2fba8d165ac059d613
Platform engine gitlink                   = c56b71ab23bf2a2d266bac2fba8d165ac059d613
engine upstream base                      = 2ba2485c78d7e00a9a25f82c00fc201da71590c4
P12X-C0                                  = CLOSED GREEN
P12X-C1                                  = CLOSED GREEN
P12X-C2                                  = CLOSED GREEN
P12X-C3                                  = CLOSED GREEN
ask-v2 moving observation                 = d22fb3626db0fe44ea543eee6531e5544cdf0b56
Fast Track moving observation             = 8b9397b4f883f9c188a5fdadafa3db0dc418ec34
merge/cherry-pick/rebase from source refs = 0
P13 product code                          = 0 after checkpoint
```

decision:
The project is **READY FOR HANDOFF BEFORE P13**.

The authoritative architecture at handoff is:
```text
DIMA PRODUCT / CONVERSATION / DECISION INTELLIGENCE
→ DIMA semantic + security + provenance + evidence control plane
→ typed DIMA native-engine bridge
→ pinned UpcyTech/dima-metabase-engine submodule
→ native Metabot / profiles / skills / engine-local state / MBQL / Query Processor / drivers
→ customer database
```

The old P13 predevelopment document and ticket are preserved as historical trust-design inputs, but
they are **not implementation authority** in their current Agent-API-oriented form.

Before any P13 product implementation, the next developer must perform one fresh P13 reconciliation:
1. read DMP-DEC-0029 and DMP-DEC-0031..0035;
2. retain the invariant that Dima authorizes exactly what is executed and receipted;
3. re-map `ResolvedAnalyticsIntent`, `ExecutionAccessSnapshot`, `CanonicalProjection`,
   `QueryReceipt`, `EvidenceArtifact`, `DimaSemanticSpec` and `EntityValueAdoptionGate` onto the
   certified native-engine bridge;
4. keep native Metabot as analytical cognition/orchestration/query-construction owner;
5. keep Dima as semantic/security/provenance/evidence truth owner;
6. define how `DMP-P11-INTEGRATION-005` closes without a second semantic or access owner;
7. write a replacement P13 predevelopment boundary and ticket before changing product code.

Open debt intentionally carried forward:
- `DMP-P5-BLOCK-001`;
- `DMP-P11-INTEGRATION-005`;
- EV-05/06/07;
- P10B2 advanced security gaps;
- P9 dimension/time/relationship transport gaps;
- P7/P8 relationship/calculated/view semantic gaps;
- historical typed Wren compatibility debt.

forbidden at handoff:
- mechanically resume the old P13 Agent-API execution seam;
- implement `standard_execution.py` or `execute_prepared()` from the old draft without reconciliation;
- add Agent API analytical fallback, Wren fallback, raw SQL escape or second analytical planner;
- move the Platform gitlink to engine `main` implicitly;
- merge/cherry-pick/rebase ask-v2 or Fast Track.

status:
`SEALED / PRE-P13 HANDOFF READY / P13 NOT STARTED`.


---

## DMP-DEC-0036 — P13 native-engine trust boundary and normative precedence

date: 2026-09-23

question:
After P12X certified the upstream-derived Dima Metabase Engine and typed native bridge, what architecture
is authoritative for P13 and how does Dima prevent native analytical cognition from becoming official
business truth without deterministic authorization?

supersedes:
- the implementation-authority portions of DMP-DEC-0029 that assumed Agent-API
  `CanonicalProjection` was the universal production execution artifact;
- every historical roadmap/report assumption that Agent API is the primary production analytical seam.

does_not_supersede:
- DMP-DEC-0029's trust invariant that the material execution artifact Dima authorizes must be the
  artifact actually executed and receipted;
- P5 one-receipt-system semantics;
- P10 one-durable-access-identity semantics;
- Standard/Research authority XOR;
- P11 adoption semantics and open forward-integration requirement;
- open security/semantic/transport debt.

evidence:
```text
Platform audited HEAD              = 6a74994b9f968a1c3c318456832d0b68b321d202
functional P12X proof SHA          = 094b5f6e0f1be939172b95fde66cab055c66ae54
P12X C2 workflow                   = 35839639339 = SUCCESS
engine repo                        = UpcyTech/dima-metabase-engine
engine gitlink                     = c56b71ab23bf2a2d266bac2fba8d165ac059d613
upstream base                      = 2ba2485c78d7e00a9a25f82c00fc201da71590c4
runtime                            = v0.63.18-dima.0
Agent API analytical fallback      = 0
Wren fallback                      = 0
raw SQL fallback                   = 0
```

Pinned source evidence shows native `construct_notebook_query` already performs repair, source-table
permission checks, validation, numeric pMBQL resolution, runability/editor validation and portable
export, then emits structured output containing native query-id, the exact resolved pMBQL query,
portable query-json and result columns. Dima must not rebuild this query.

decision:

### Current authoritative architecture

```text
Native Metabot
= ANALYTICAL COGNITION
= QUERY-CANDIDATE AUTHOR

Dima
= BUSINESS TRUTH
= EXECUTION AUTHORITY
= SECURITY / PROVENANCE / EVIDENCE AUTHORITY

Metabase Query Processor
= EXECUTOR
```

The native-engine hot path is primary. Agent API analytical execution is
`LEGACY / AUXILIARY / NON-PRIMARY`.

### Native trust transition

P13A introduces a typed `NativeQueryCandidate` representing one exact native query occurrence.
It carries at least:
- exact engine identity;
- Dima request/trace ids;
- native conversation id and query-id;
- exact resolved pMBQL artifact;
- portable/exported representation when present;
- stable Dima-governed source/resource bindings;
- native validation provenance;
- exact candidate artifact fingerprint;
- query count.

Candidate fingerprint means **exact execution-artifact identity**, not semantic equivalence. It is the
SHA-256 of deterministic serialization of the exact pMBQL artifact that may execute. Dima must not
strip or rewrite native fields merely to make independent candidates hash alike.

The Dima authorization gate may return only:
`ALLOW | CLARIFY/REPLAN | BLOCK`.
The gate verifies; it does not write/rewrite MBQL.

Initial P13A certification is deliberately narrow:
```text
one governed metric
one governed source
optional single accepted time scope
one material query
no arbitrary filters
no approved relationship path yet
no research/multi-query planning
```

Any unapproved extra metric/source/time/filter/join/query material is blocked.

### One trust plane, engine-independent execution artifact

P5 and P10 must stop depending directly on the Agent-API concrete `CanonicalProjection`.
P13A introduces one narrow common contract, `AuthorizedExecutionArtifact` (or equivalent), exposing:
- authority id;
- projection hash;
- resolved-intent hash;
- semantic-context version;
- semantic refs;
- stable resource-id/fingerprint bindings;
- exact substrate artifact fingerprint(s);
- exact substrate artifact representation(s) needed for receipt/audit;
- query count / step role;
- engine/substrate identity.

For native Metabase, the substrate artifact is the exact resolved pMBQL candidate.
For the historical Agent API path, an adapter maps `CanonicalProjection` into the same contract.

There will be:
- one P10 `ExecutionAccessSnapshotIssuer`;
- one P5 `DimaQueryReceiptSealer`;
- one `ExecutionAccessSnapshot.execution_access_fingerprint`;
- one Dima receipt system.

No `NativeAccessSnapshot`, `NativeQueryReceipt` or second receipt/access owner is permitted.

### Exact-artifact invariant

```text
native candidate pMBQL
→ fingerprint exact artifact
→ Dima authorization
→ AuthorizedExecutionArtifact
→ execute THE SAME pMBQL
→ result
→ DimaQueryReceipt with THE SAME artifact fingerprint
→ Evidence promotion
```

`candidate A → authorize A → construct/execute B` is a hard fail.

Native Metabot prose is never VERIFIED Evidence. Official numeric claims require authorized execution,
receipt and Evidence promotion.

### Engine identity source-review conclusion

Current bridge runtime verification checks only the runtime tag. Upstream build source confirms
`version.properties` contains the build tag plus only the first seven git-hash characters. This was
adequate for P12X C2 because CI separately pinned exact source/image, but is insufficient by itself as
the long-term P13B production attestation for exact engine source + image.

P13A therefore makes **no engine-source change**.

Before P13B, one of these must be separately certified:
1. deployment/runtime attestation that binds exact engine SHA + immutable image digest to the running
   instance; or
2. a minimal isolated Dima-owned engine identity endpoint/build manifest.

No patch to `run-agent-loop`, profiles, skills, native query construction or Query Processor is
authorized for identity.

### Historical code disposition

Keep, do not delete:
- `MetabaseAgentClient`;
- `MetabaseSubstrateAdapter`;
- `MetabaseProjectionCompiler`;
- `CanonicalProjection`;
- historical canonicalization tests.

They remain regression/migration/auxiliary assets, not primary Standard hot-path authority.

### Open debt

Remain explicitly open:
- `DMP-P5-BLOCK-001`;
- `DMP-P11-INTEGRATION-005`;
- EV-05/06/07;
- P10B2 RLS/CLS/impersonation/advanced routing/cache-result reauthorization;
- P9 dimension/time/relationship transport;
- P7/P8 calculated/relationship/view semantic gaps;
- historical Wren typed gaps.

status:
`SEALED / CURRENT NORMATIVE P13 ARCHITECTURE / P13A PROVIDER-FREE IMPLEMENTATION AUTHORIZED AFTER GOVERNANCE REPIN`.


---

## DMP-DEC-0037 — P13B native candidate attestation and runtime identity boundary

date: 2026-09-23

question:
How can P13B prove that the facts used to authorize a native Metabot query came from the query
Metabase actually built, and that the exact authorized artifact is executed on the exact certified
runtime, without making Dima a Python MBQL parser or reopening Agent API as the analytical hot path?

audited_state:
```text
Platform branch      = feat/dima-metabase-platform
Platform HEAD        = 86faaa339b75d261e31da1dd0dec8939f58620e6
engine repo           = UpcyTech/dima-metabase-engine
engine gitlink/main   = c56b71ab23bf2a2d266bac2fba8d165ac059d613
upstream source audit = 2ba2485c78d7e00a9a25f82c00fc201da71590c4
runtime tag           = v0.63.18-dima.0
P13A                  = GREEN
P13B                  = NOT AUTHORIZED at audit start
```

source_findings:
1. `construct_notebook_query` already emits the exact resolved pMBQL and query-id after native
   repair, validation, permission-aware source checking and resolution.
2. Native agent memory stores `query-id → exact query`, and final conversation state persists it.
3. Metabase Lib already exposes bounded query-inspection APIs for source, aggregations, breakouts,
   filters, joins, order, referenced columns and stage count.
4. QP preprocessing materializes implicit joins and tags them `:qp/is-implicit-join true`.
5. QP permission code can expose the full table-id set used by current-user permission checks.
6. `POST /api/dataset` accepts MBQL5 and executes it through current-user Query Processor
   middleware without Agent API query reconstruction.
7. current runtime properties expose only tag + seven-character git hash; P12X CI pinning is strong
   lab evidence but not a request-relevant production source/image/instance attestation surface.

decision:

### Candidate fact provenance

A live P13B candidate may not be built from caller-supplied semantic refs, resource bindings,
filter/join counts, time fingerprints or validation strings.

The native engine must expose a bounded attestation envelope keyed by:

```text
conversation_id + native_query_id
```

and derive the exact query from server-side native state.

It returns:
- exact serialized pMBQL;
- exact query fingerprint;
- bounded `NativeExecutionManifest` physical/query facts;
- typed native validation/permission provenance;
- current authenticated Metabase subject;
- runtime identity.

Dima maps physical ids to business truth via
`CurrentCatalogSnapshot + SourceLineage + DimaSemanticSpec` and compares them with accepted
authority. Metabase never invents Dima semantic ids.

### Query-inspection ownership

```text
Metabase Lib/QP = understands/observes MBQL
Dima             = maps observed facts to business semantics and authorizes/rejects
```

No Python recursive MBQL parser/normalizer/repair layer is permitted.

### Engine patch decision

Existing native state is sufficient to retrieve the exact query but no current stable endpoint
provides the required typed attestation manifest. Therefore:

```text
ENGINE PATCH REQUIRED = YES
```

only after supervisor authorization, and only in an isolated Dima namespace.

Proposed minimum patch:
```text
src/metabase/dima/native_attestation.clj
src/metabase/dima/api.clj
test/metabase/dima/native_attestation_test.clj
test/metabase/dima/api_test.clj
src/metabase/api_routes/routes.clj          # minimal route registration
.dima/docker/Dockerfile.c0                  # immutable build identity only
```

No changes to cognition, profiles, skills, query construction/repair, QP semantics or drivers.

### Runtime identity

Deployment-only evidence is rejected as the sole production scheme because the current Platform has
no durable request-relevant control-plane attestation that binds the exact live instance to source
SHA + immutable image.

Chosen design:

```text
MINIMAL ENGINE IDENTITY SEAM
GET /api/dima/engine/v1/identity
```

Full source SHA/upstream/release/build facts are baked into the Dima build. Immutable image digest is
the exact launched image identity supplied by certified deployment. Runtime instance id is
process-scoped. Missing identity is a hard fail.

Required equality:
```text
candidate engine/runtime
==
attested running engine/runtime
==
runtime that executes /api/dataset
==
runtime sealed into receipt
```

### Exact same-artifact execution

```text
POST /api/dataset = selected execution seam
```

The exact serialized pMBQL returned by native attestation is the body Dima authorizes and submits.
QP may add its own security/preprocess/default-constraint machinery; no analytical query is
re-authored by Agent API, SQL conversion or Wren.

### First vertical

```text
PX-01
Haziran 2026'da kaç satış siparişi açıldı?
source      = satis_siparisleri
aggregation = COUNT(*)
period      = [2026-06-01, 2026-07-01)
oracle      = 126
```

Independent oracle remains the frozen Boyahane DuckDB oracle built by
`backend/lab/metabase/p12x/build_oracle.py`.

### Legacy quarantine

Future live Platform orchestration is reserved under `backend/app/v3/native_standard/`.
Governance must forbid that future hot path from importing the historical compiler/canonical/
execution-adapter analytical seam or `MetabaseAgentClient`.

The existing `native_execution.py` compatibility adapter is not moved merely to satisfy this rule.

open:
- DMP-P13B-BLOCK-001 remains implementation-open;
- DMP-P13B-BLOCK-002 remains implementation-open;
- DMP-P5-BLOCK-001;
- DMP-P11-INTEGRATION-005;
- EV-05/06/07;
- P10B2 advanced security;
- P9 dimension/time/relationship transport;
- P7/P8 calculated/relationship/view semantics;
- historical Wren typed gaps.

status:
`SEALED / P13B NATIVE ATTESTATION DESIGN / IMPLEMENTATION PENDING SUPERVISOR AUTHORIZATION`.

---

## DMP-DEC-0038 — P13B-1 engine promotion and P13B-2 provider-free trust integration

date: 2026-09-23

question:
After the isolated P13B engine candidate is certified, what exact engine identity becomes production
authority for the Platform branch, and what work is authorized next without reopening expensive
model-backed parity testing?

decision:

```text
engine repo       = UpcyTech/dima-metabase-engine
promoted main SHA = 3ac50a0ad1c2fb53d538c9fccf621db816c305e1
upstream SHA      = 2ba2485c78d7e00a9a25f82c00fc201da71590c4
release           = 0.63.18-dima.1
revision          = 1
semantic_behavior_changes = 0
```

The exact promoted SHA passed the P13B deterministic certification workflow
`35876198926`:

```text
focused       = SUCCESS
source-build  = SUCCESS
patch-surface = SUCCESS
certification = SUCCESS
```

Promotion is a fast-forward of engine `main`; no squash, rebase, history rewrite, or merge-only SHA
was introduced.

The Platform gitlink is therefore permitted to move from
`c56b71ab23bf2a2d266bac2fba8d165ac059d613` to
`3ac50a0ad1c2fb53d538c9fccf621db816c305e1`.

P13B-1 status:

`GREEN / CLOSED`.

P13B-2 is now authorized as a provider-free trust-plane phase under
`backend/app/v3/native_standard/`.

Required authority separation remains:

```text
NativeExecutionManifest = observed physical/query facts from Metabase
ResolvedAnalyticsIntent + DimaSemanticSpec + SourceLineage + CurrentCatalogSnapshot
                        = accepted Dima business meaning
comparison              = authorization decision
```

P13B-2 must reuse:
- existing `NativeCandidateAuthorizationGate`;
- existing `AuthorizedExecutionArtifact`;
- existing `ExecutionAccessSnapshotIssuer`;
- existing `DimaQueryReceiptSealer`.

It must not create:
- a Python MBQL parser/normalizer/repairer;
- a second receipt or access-identity system;
- Agent API, Wren, raw-SQL, or admin analytical fallback.

The successful full C1 proof on engine candidate
`78b8ee66464435daece5a8e3b4cffce5a77937c3` is retained as the expensive
pre-promotion capability baseline. Because the subsequent changes are trust/infrastructure-only,
P13B-2 requires focused provider-free deterministic tests, not a new full stock-vs-fork C1.

status:
`SEALED / P13B-1 GREEN / P13B-2 PROVIDER-FREE IMPLEMENTATION AUTHORIZED`.

---

## DMP-DEC-0039 — P13B-2 provider-free GREEN and P13B-3 first pinned-live authorization

date: 2026-09-23

audited_state:
```text
Platform branch = feat/dima-metabase-platform
Platform certified base = 4c3ac500dd1ec35b0420bb6f3fd61bae65269364
engine main/gitlink = 3ac50a0ad1c2fb53d538c9fccf621db816c305e1
engine release = 0.63.18-dima.1

P13B provider-free = 35879190512 SUCCESS
P5 regression      = 35879190568 SUCCESS
P13A regression    = 35879190231 SUCCESS
M1 regression      = 35879190285 SUCCESS
governance         = 35879190688 SUCCESS
```

decision:

P13B-2 provider-free trust integration is GREEN.

P13B-3 is authorized for exactly one model-backed positive vertical:

```text
PX-01
Haziran 2026'da kaç satış siparişi açıldı?
source      = satis_siparisleri
aggregation = COUNT(*)
time field  = acilis_tarihi
period      = [2026-06-01, 2026-07-01)
oracle      = 126
model       = openrouter/openai/gpt-5.6-luna
primary user turns = 1
```

The live path reuses NativeEngineBridge and the same authenticated Metabase session for:
- engine identity;
- native-query attestation;
- exact /api/dataset execution.

Hard invariant:
```text
attested pMBQL fingerprint
==
authorized artifact fingerprint
==
submitted dataset-body fingerprint
==
P5 receipt query fingerprint
```

Runtime source/build/image/instance identity must also remain exact from engine identity through
attestation, exact execution and receipt. Official numeric truth is emitted only after P5 receipt,
independent oracle PASS, and VERIFIED EvidenceArtifact.

P12X C2 live is manual regression only. Deterministic negatives remain provider-free. The duplicate
engine-side C1 harness is NON-AUTHORITATIVE / DEFERRED.

No Agent API analytical fallback, Wren fallback, raw SQL fallback, admin analytical fallback,
query reconstruction, Python MBQL parser, or stochastic retry is authorized.

status:
`SEALED / P13B-2 PROVIDER-FREE GREEN / P13B-3 FIRST PINNED-LIVE PX-01 AUTHORIZED`.

---

## DMP-DEC-0040 — P13B-3 dima.3 first pinned-live Standard GREEN and supervisor stop

date: 2026-09-23

question:
Did the single authorized Luna PX-01 live occurrence on the certified dima.3 engine preserve the
sealed Dima-owned truth chain from managed semantic resource through native Metabot, exact native
attestation, authorization, exact execution, P5 receipt, independent oracle and VERIFIED Evidence?

decision:

```text
YES — for the bounded PX-01 P13B-3 vertical only.
```

Authoritative occurrence:

```text
Platform live SHA      = 8993009b14f9a3f443b23ef681e181cfee210b6d
live attempt id        = p13b-px01-native-metric-dima3-1
governance             = 35915780178 SUCCESS
live workflow          = 35915780089 SUCCESS
artifact id            = 10774804897
artifact digest        = sha256:744d1c0913bb20267e544b896d65c50da54196bacd33fbdc2d98d829496940a0
engine SHA             = 10960f7c36bb84425b1794b557b78211c14d7f5f
engine release         = 0.63.18-dima.3
model                  = openrouter/openai/gpt-5.6-luna
question               = Haziran 2026'da kaç satış siparişi açıldı?
oracle                 = 126
official answer        = 126
primary user turns     = 1
```

The same live runtime first provisioned and verified the P9/P9B DIMA_MANAGED resource
`metric.sales_order_count` with Metabase local id `1`, portable entity id
`VEzPLLv1IBWZfl7mJ9Xnb`, and persisted `COUNT(*)` definition. Semantic availability used zero
model calls.

The one native Metabot occurrence then produced one material native query. Dima accepted it only
after engine attestation and exact P9 binding proved the persistent metric identity.

Mandatory immutable query chain:

```text
attested   = acef568a9051f27e90c3743afefcb9f01b4f5ff77d8ba2117c405f29a56dd787
authorized = acef568a9051f27e90c3743afefcb9f01b4f5ff77d8ba2117c405f29a56dd787
submitted  = acef568a9051f27e90c3743afefcb9f01b4f5ff77d8ba2117c405f29a56dd787
receipted  = acef568a9051f27e90c3743afefcb9f01b4f5ff77d8ba2117c405f29a56dd787
```

Runtime chain:

```text
repository          = UpcyTech/dima-metabase-engine
revision SHA        = 10960f7c36bb84425b1794b557b78211c14d7f5f
upstream base       = 2ba2485c78d7e00a9a25f82c00fc201da71590c4
runtime tag         = v0.63.18-dima.3
build identity      = github-actions:35915780089:10960f7c36bb84425b1794b557b78211c14d7f5f
image identity      = sha256:0520e0b02a94e0d39b645443731e3d9436ee370624b61aa721ff914c9a293849
runtime instance id = c88856ed-6f82-4709-ab6f-0c86113edb92
```

Existing identity systems remained singular:

```text
P5 QueryReceipt id              = dqr_d096c10ab01354391bae0c62
P5 receipt fingerprint          = 5526cfc9c201fae9f65876675b7992e00a3dbd8effba0d81472e7e3c094e2df1
ExecutionAccess fingerprint     = 3b5aca37a6ed684aa68cfdfe6b276dfcc2ea8b794351732bfeb545ca8e329571
Evidence id                     = evi_17fc5054faf60aec1d1e3e6a
Evidence state                  = VERIFIED
```

The proof cardinality is exactly one authority, one material native query, one attestation, one
authorized artifact, one ExecutionAccessSnapshot, one database execution, one Dima QueryReceipt and
one VERIFIED Evidence. `silent_wrong = 0`; Agent API analytical fallback, Wren fallback, raw SQL
fallback and admin analytical fallback are all `0`.

This decision does not certify:
- P13 Standard as a generalized/final production closure;
- P13C entity-value integration;
- EV-05/06/07;
- P10B2 advanced security;
- P9 dimension/time/relationship transport;
- calculated/relationship/view semantics;
- multi-instance production runtime identity;
- Research/P14.

CI economy disposition:
the live workflow currently recompiles the engine from source. That is safe but expensive. A future
separately reviewed CI milestone may publish the already source-certified engine as an immutable
digest-pinned image and make Platform live jobs pull that digest while preserving all current
runtime-identity equality checks. This optimization is not implemented by this decision and must not
remove source-build certification.

status:
`SEALED / P13B-3 BOUNDED LIVE GREEN / STOP FOR SUPERVISOR AUDIT`.



---

## DMP-DEC-0041 — P13C predevelopment seal and certified-image CI authorization

date: 2026-09-23

The post-P13B supervisor audit authorizes two linked bounded goals:

1. eliminate repeated Platform engine source builds by certifying/publishing one immutable engine
   image per real engine candidate;
2. then open the first same-table low-cardinality textual equality P13C Standard vertical.

Provider-free source inspection proves dima.3 cannot safely authorize the textual predicate:
the engine reports `non_temporal_filter_count` but not the typed physical field/operator/literal
facts required to map the native query to Dima-owned filter truth. Therefore the next real engine
revision requires a bounded native textual-equality attestation extension.

The next engine release is derived from the existing 1→2→3 release history as
`0.63.18-dima.4`; this is an observation/trust seam extension, not a Metabot cognition change.

P11 production integration must reuse `EntityValueAdoptionGate` and the existing P5/P10
`ExecutionAccessSnapshot.execution_access_fingerprint`. A second access fingerprint/resolver is
forbidden. P10 may expose a bounded expected-resource issuance path using the same snapshot contract
and fingerprint algorithm so current-user value evidence can carry the final durable lens identity
before native candidate authorization.

P13A may accept at most one governed filter only with an exact filter-scope fingerprint and exact
authorized resource equality. P13B's zero-filter path remains a required regression.

The dima.4 candidate must also establish the permanent build-once/pull-many pattern:
cheap gates first, one BuildKit-cached source build, smoke, GHCR publish, immutable digest resolution,
pull-by-digest, runtime /identity verification and a machine-readable certified-image receipt.

No model call is authorized before provider-free P13C GREEN. After that, one Luna P13C canary is
authorized; a GREEN result requires an immediate supervisor stop.

status:
`SEALED / P13C BOUNDED IMPLEMENTATION + DIMA.4 CERTIFIED-IMAGE CI AUTHORIZED`.

---

## DMP-DEC-0042 — Product-first native-engine inheritance, corrected Research/Explorations ownership and fast corridor

date: 2026-09-24

Current authority update:

```text
METABASE + METABOT = primary native analytics engine
Dima                = business semantic/security/provenance/Evidence/Research/Decision truth
```

Native capability reuse is the default:

```text
USE_NATIVE
→ COMPOSE_NATIVE
→ WRAP_NATIVE
→ HOOK_NATIVE
→ DIMA_OWNS
```

`DIMA_OWNS` is last. DMP-DEC-0026 `SEMANTIC_NECESSITY_GATE` applies before introducing new
Dima-owned deterministic cognition/heuristic machinery; it does not require a justification cycle
before simply using an already-native Metabase capability under the established Dima trust boundary.

Normative consequences:
- P14 is Native Research integration: ResearchManager owns obligations, hypotheses, counter-evidence,
  budget/stopping, Evidence synthesis and Decision state; native Metabot/Metabase owns analytical work.
- P15 is Native Metabase Explorations Integration, not primitive harvest.
- native variants, top-N-other, temporal patterns, interestingness, stored results, lifecycle,
  cancel/restart and derived permissions are not ported to Python by default.
- P23 reuses native lifecycle/job machinery when it satisfies the execution contract; Dima does not
  create a second generic background analytics runner.
- moving engine SHA/digest values live in gitlink/runtime-lock/status/receipts, not conceptual
  architecture prose.
- P13C GREEN no longer implies a supervisor stop; after one sealed P13C live proof, continue directly
  to cohesive P13D unless an explicit supervisor-stop condition is crossed.

Fast-CI consequences:
- old M2 excludes `backend/lab/metabase/p13c/**`;
- P13C provider-free suite is deliberate `workflow_dispatch`, not every micro-push;
- expensive runtime/model proofs remain marker/manual boundaries.

Current dima.4 state:

```text
engine main/certified SHA = cdd117558fea3b0a80f6b89bb872ffb6e9ab175f
release                   = 0.63.18-dima.4
certification             = 35951538259 SUCCESS
certified digest          = sha256:ce8d135163faba74f80c18c8e0a585037be2e6049a7ca74d4f477e655e039a71
build identity            = github-actions:35951538259:cdd117558fea3b0a80f6b89bb872ffb6e9ab175f
```

P13C runtime run `35953149626` failed before runtime start at GHCR digest pull with
`manifest unknown` after successful login. This is classified as registry/package access until
disproven. It is not negative evidence about P13C semantics, P11, P10, native attestation, Metabot,
authorization or dataset execution. Model calls and analytical executions for that run are zero.

status:
`SEALED / PRODUCT-FIRST NATIVE ENGINE INHERITANCE + FAST CORRIDOR ACTIVE / GHCR ACCESS OWNER OPEN`.


---

## DMP-DEC-0043 — P13C textual-equality Standard seal and anonymous public-digest runtime corridor

date: 2026-09-24

P13C is sealed GREEN.

The certified `0.63.18-dima.4` engine was not rebuilt. The runtime lock, engine SHA, immutable
digest and product/trust/Metabot implementation remained unchanged while the Platform runtime
failure was isolated to CI authentication.

Root cause and disposition:

```text
public GHCR exact-digest anonymous pull              = WORKS
cross-owner repository-scoped GITHUB_TOKEN login    = REMOVED FROM ACTIVE DIGEST CONSUMERS
old failed run 35953149626                           = NOT RERUN
legacy p12x-c2 live workflow                         = UNTOUCHED
PAT / duplicate image / alternate registry           = NOT INTRODUCED
```

The first corrected runtime run proved exact-digest pull and the complete runtime/P11 chain, then
failed only because the integration job had installed the package without the repository's canonical
`.[dev]` test extra. The root fix reused that existing extra; no ad-hoc pytest dependency was
introduced.

Final provider-free runtime integration:

```text
commit = c3397f68d4af5e524455fec5bff2d1f21b489d0d
run    = 35956274118 SUCCESS
```

Exactly one P13C Luna user-turn canary was then run:

```text
commit                  = c0cfd65f1162cda31bd8d984dcaa2865e7d2466c
run                     = 35956538018 SUCCESS
artifact id             = 10790995760
artifact digest         = sha256:52ffc8c96e9ba30ca9f1764dc5b695ea7b25e63d1bf409523961dd3be700c69a
model                   = openrouter/openai/gpt-5.6-luna
question                = Haziran 2026'da Web kanalından kaç satış siparişi açıldı?
official answer         = 27
oracle                  = 27
silent_wrong            = 0
```

The native textual predicate was attested as exact stage-0 equality on physical field id `531`,
type `type/Text`, literal `Web`. Dima bound it to the accepted semantic filter and exact
current-lens P11 evidence before authorization.

Immutable execution identity:

```text
attested   = 950ea75436af26ea9d307cf37421a4b98fe2a86fbceee4e2487001ed8dadb393
authorized = 950ea75436af26ea9d307cf37421a4b98fe2a86fbceee4e2487001ed8dadb393
submitted  = 950ea75436af26ea9d307cf37421a4b98fe2a86fbceee4e2487001ed8dadb393
receipted  = 950ea75436af26ea9d307cf37421a4b98fe2a86fbceee4e2487001ed8dadb393
```

Existing truth systems remained singular:

```text
AcceptedStandardAuthority = asa_365b8456f7d15192697cc339
QueryReceipt              = dqr_36e99d80963cb15f9db629c5
Evidence                  = evi_c5bf623c5f7ef98c796ee4d7 / VERIFIED
ExecutionAccess lens      = existing P5/P10 fingerprint path
```

Fallback cardinality is zero for Wren, raw SQL, Agent API analytical fallback and admin analytical
fallback. There is one material native query and one database execution.

This seal also certifies the intended CI economy for unchanged engine candidates:
source-build/certify once, publish immutable digest once, then pull and re-attest that digest from
Platform jobs. It does not authorize moving tags or skipping engine source certification when engine
code truly changes.

Per DMP-DEC-0042, P13C GREEN is not a supervisor stop. Continue directly to the cohesive P13D
breakout + ordering/top-N + period-comparison Standard slice unless an explicit stop condition is
crossed.

status:
`SEALED / P13C TEXTUAL EQUALITY GREEN / DIGEST CORRIDOR GREEN / CONTINUE P13D`.


---

## DMP-DEC-0044 — Seal P13 trust baseline, stop operator-by-operator generalization, authorize Native Research

date: 2026-09-24

question:
After the certified dima.6 exact-occurrence path and the final cohesive live attempt, should Platform
continue extending P13 one Metabase operator/representation family at a time, or treat the trust
architecture as proven and move to Dima's Research/Evidence/Decision product layer while carrying
unsupported native representations as explicit fail-closed compatibility debt?

evidence:

```text
Platform audited pre-decision HEAD = 77000d07da0af4d43688bf963880ebc5120c8f1f
engine main / dima.6 SHA            = cbe313af9ac2d5960f662068e433d328d896fb06
engine release                      = 0.63.18-dima.6
engine certification                = 36042062775 SUCCESS
immutable digest                    = sha256:40e9a44be49904de3ddf12d4683c768e70955851c10a928a9c8f7d8f60780353
Platform exact-occurrence gate      = 36046089168 SUCCESS
native bridge regression            = 36046089305 SUCCESS
final cohesive live                 = 36046994140 FAILURE
```

dima.6 remained a thin Dima integration seam. No native Metabot prompt/profile/skill, Query
Processor, driver or Metabase Lib source was modified.

The final live run proved two advanced native Standard cases end to end:

```text
BREAKDOWN = GREEN
QueryReceipt = dqr_1ba94e6399d85042e37723a7
Evidence     = evi_c8ff53766d3d684f2cc48744 / VERIFIED

TOP-N RANKING = GREEN
QueryReceipt = dqr_ca8dcbbc1180a9cd2355db25
Evidence     = evi_87349d18181df8342ffe0ebd / VERIFIED
```

In both cases the attested, authorized, executed and receipted query fingerprint was identical and
the independent oracle matched.

The third case, period comparison, failed closed before authorization/execution with:

```text
NATIVE_QUERY_RUNTIME_REPRESENTATION_UNSUPPORTED
```

The failure is in the Dima-owned compatibility codec for one unobserved absolute-datetime serialized
representation. No un-attested comparison execution, QueryReceipt or VERIFIED Evidence was emitted.

decision:

```text
P13 STANDARD TRUST BASELINE          = SEALED
P13 OPERATOR-FAMILY GENERALIZATION   = STOPPED
P13D BREAKDOWN LIVE                  = GREEN
P13D TOP-N RANKING LIVE              = GREEN
P13D PERIOD COMPARISON               = DEFERRED COMPATIBILITY GAP / NOT GREEN
P13D WHOLE ORIGINAL THREE-CASE SEAL  = NOT CLAIMED
P14 NATIVE RESEARCH FOUNDATION       = AUTHORIZED
P13E / P13F                          = DO NOT CREATE
```

Rationale:
P13 was created to prove that real native Metabot analytics can cross Dima's identity, provenance,
execution and Evidence boundary without silent wrong or fallback. P13B/P13C plus the dima.6
breakdown/ranking evidence and fail-closed comparison behavior are sufficient proof of that
architecture. Continuing one operator/representation at a time would turn Dima into a shadow
Metabase and reduce product velocity without proportionate information gain.

### Native Capability Inheritance Contract

Compatible functionality present in the pinned Metabase/Metabot engine is inherited by default:

```text
USE_NATIVE
→ COMPOSE_NATIVE
→ WRAP_NATIVE
→ HOOK_NATIVE
→ DIMA_OWNS
```

Do not create a Dima parser/planner/validator merely because native Metabase used a different query
primitive. Dima adds deterministic machinery only for a measured material business/security/
provenance/product-intelligence gap.

### Ownership refinement

The phrase "Dima semantic authority" is henceforth split so it cannot be misread as authority over
Metabase's entire analytical grammar.

For the native Metabase path:

```text
Metabase + Metabot
= analytical definition/cognition/execution authority inside the selected analytics substrate

Dima
= business ontology + company/sector context + engine-resource mapping
+ research/evidence/decision/action/memory authority
+ product-level identity/policy binding
```

Metabase owns persisted native Metric/Model analytical definitions, field/query semantics, query
construction/repair, MBQL, filters, breakouts, ranking, temporal operations, Query Processor, drivers
and native data-permission enforcement.

Dima owns business concept IDs, aliases, company terminology, sector meaning, decision relevance,
mapping to exact engine resources/versions, accepted obligations, claim lineage, Evidence epistemic
state, hypotheses/findings, decisions, actions and institutional memory.

Existing P7/P8/P9 DimaSemanticSpec/DIMA_MANAGED resources are not removed by this decision. They are
sealed compatibility/migration assets for existing certified paths. New work must not expand them
into a second independently-authored analytics-definition store. A future explicit migration may
narrow DimaSemanticSpec toward "Business Ontology / Engine Mapping"; no silent destructive migration
is authorized here.

### Evidence and security consequences

Evidence proves claim lineage and epistemic status, not every internal Metabase operator. VERIFIED
still requires exact provenance, correct principal/scope/resource binding and no unresolved material
ambiguity.

Metabase/database remain the native data-permission enforcers. Dima binds the correct tenant/principal
and owns product-level Research/Evidence/Decision/Action policy. P10 remains identity/provenance
binding and must not grow into a duplicate generic RLS engine.

### Comparison compatibility debt

No dima.7, no extra Luna and no speculative codec widening is authorized merely to make the old
three-case certification table all green. Record the comparison gap. If a real P14/product path
materially encounters it, capture the exact representation and apply the smallest reversible
Dima-local compatibility correction provider-free. Native core source remains immutable by default.

### Immediate next phase

P14 starts now with zero model calls required for foundation work:

```text
ResearchSession / durable Research state
ResearchObligation
Hypothesis + counter-evidence links
budget / stopping state
native Metabot conversation/session reference
reuse existing exact-occurrence execution
reuse P10 / P5 / Evidence
```

ResearchManager does not author MBQL/SQL and does not recreate compare/breakdown/rank/root-cause
query tools. Native Metabot/Metabase owns analytical cognition; Dima owns investigation epistemics,
synthesis and decision intelligence.

status:
`SEALED / P13 TRUST BASELINE CLOSED / P14 NATIVE RESEARCH AUTHORIZED / COMPARISON COMPATIBILITY DEBT CARRIED EXPLICITLY`.


governance note:
The sealed historical roadmap is intentionally not rehashed/resealed by DMP-DEC-0044. The binding
forward plan is now
`backend/belgeler/metabase/DIMA_METABASE_CURRENT_PRODUCT_PLAN.md`.
Governance retains the original sealed-roadmap blob for audit history.


---

## DMP-DEC-0045 — P14 native Research foundation vertical is GREEN

Date: 2026-09-24

Authority:
DMP-DEC-0044 authorized P14 Native Research and explicitly closed P13 as the product-development loop.

Implementation/proof checkpoint:

\`\`\`text
foundation implementation       = a8c7b5d2b922e85ff046c6c7ce1bfce92aa13552
integrated trust proof          = bab26fe51978929ace44f7703543f78099c692ce
provider-free seal              = 36052728145 SUCCESS
governance                      = 36052727756 SUCCESS
P14 focused tests               = 6 passed
P13D/P10/P5 regressions         = 69 passed
engine SHA                      = cbe313af9ac2d5960f662068e433d328d896fb06
new engine build                = 0
Luna / Sol / C1 calls           = 0 / 0 / 0
native Metabot/Metabase changes = 0
\`\`\`

The first coherent P14 vertical now provides durable/versioned Research state:

\`\`\`text
ResearchSession
ResearchObligation
Hypothesis
CounterEvidenceRef
EvidenceRef
ResearchBudget
StoppingState
NativeMetabotConversationRef
ResearchLimitation
\`\`\`

ResearchManager owns investigation obligations, evidence admission, hypothesis/counter-evidence
epistemics, budget and stopping. It does not own SQL/MBQL generation, parsing, ranking, comparison,
temporal planning, query repair or a second analytics state machine.

The provider-free proof exercises the existing product authority chain rather than faking a second
Dima execution authority:

\`\`\`text
accepted Research obligation
→ native Metabot delegation
→ existing P13 NativeStandardTrustOrchestrator authorization
→ existing exact-occurrence execution request/transport
→ existing P10 ExecutionAccessSnapshot
→ existing P5 DimaQueryReceipt seal
→ VERIFIED EvidenceArtifact
→ Research obligation / hypothesis state
\`\`\`

The native HTTP boundary alone is mocked in the provider-free test. P13 authorization, P10 access
identity, P5 receipt sealing and Dima Evidence/Research admission are the production owners under
test.

Evidence admission is fail-closed:
- only VERIFIED Evidence is eligible;
- the exact P5 receipt must be linked;
- authority, obligation, tenant, principal and semantic-context identity must match;
- material execution identity fields must be present;
- counter-evidence remains explicit and cannot silently promote a hypothesis.

The carried P13D comparison compatibility gap remains unchanged and is not reclassified GREEN.
A matching real P14 failure may be recorded as an obligation-scoped Research limitation while
independent valid obligations continue. No dima.7, codec widening or native query rewrite was
introduced.

status:
\`SEALED / P14 FIRST COHERENT RESEARCH FOUNDATION VERTICAL GREEN / NATIVE SUBSTRATE UNCHANGED\`.

Next coherent P14 slice:
wire the sealed Research aggregate into the product Research/Ask orchestration boundary with durable
session resume and real native conversation/result correlation, while continuing to reuse the same
P13 exact-occurrence, P10, P5 and Evidence authorities. No model-backed evaluation is required until
that result would change an architectural/product decision.


---

## DMP-DEC-0046 — P14 product Research/Ask orchestration is provider-free GREEN

Date: 2026-09-24

DMP-DEC-0045's next coherent slice is complete.

```text
product implementation checkpoint = 47ac0d4ecae7addbd7d79cff6452b6e60b7a3d9b
CI-economy correction             = 939f51facba7951bf0a07d4ef8facb38c9e11d13
final focused code checkpoint     = dbef0499abe6b7804b5f09d8ec7ad76b99946b1c
provider-free seal                = 36057793900 SUCCESS
governance                        = 36057794099 SUCCESS
P14 focused tests                 = 13 passed
P13D/P10/P5 regressions           = 69 passed

engine SHA                        = cbe313af9ac2d5960f662068e433d328d896fb06
engine release                    = 0.63.18-dima.6
new engine build                  = 0
Luna / Sol / C1 calls             = 0 / 0 / 0
native Metabase/Metabot files     = 0
duplicate analytics mechanisms    = 0
```

The product Ask boundary now turns a READY, already-grounded ResearchBrief into one durable
ResearchSession and returns its session identity on the same `/ask-v2` surface. Research resume
uses `research_session_id` and enters the durable P14 state before any language interpreter runs.
The old raw prompt is therefore not reparsed into a new semantic authority during resume.

Durability is explicit:
- `research_session` stores the immutable/fingerprinted Research checkpoint and revision;
- `research_execution_link` stores obligation → Dima request/trace → native conversation →
  exact native query occurrence → attestation/receipt/Evidence correlation;
- optimistic revision checks prevent lost Research-state updates;
- a DELEGATED state without durable correlation is not replayed;
- a delegated native turn with unknown outcome is converted to an obligation-level limitation
  rather than issuing duplicate cognition;
- once an exact native query occurrence is captured, restart resumes that occurrence instead of
  invoking Metabot again.

The P14 product owner still does not perform analytics. It delegates the analytical objective to
`NativeEngineBridge` and requires a separately installed, principal-scoped existing P13 material
executor. Receipt/Evidence admission remains the DMP-DEC-0045 ResearchManager contract: only eligible
VERIFIED Evidence linked to a complete existing P5 QueryReceipt and matching tenant/principal/context
can advance Research state.

The provider-free product tests mock only the external native HTTP transport/material boundary needed
to exercise lifecycle and crash/restart correlation. In the same P14 seal, the inherited DMP-DEC-0045
foundation tests continue to exercise the real existing P13 NativeStandardTrustOrchestrator, P10
ExecutionAccessSnapshot and P5 DimaQueryReceipt owners. No second execution, access or receipt
authority was introduced.

Production startup intentionally does **not** mint a shared Metabase admin/service session and does
not invent a second identity broker. Until the existing principal-scoped native/P13 runtime owner is
installed through the bounded runtime seam, Research material execution returns fail-closed
`P14_NATIVE_RUNTIME_NOT_CONFIGURED` / HTTP 503. This is a security invariant, not an analytical
fallback.

The historical M1 workflow had been broadly triggered by `backend/app/v3/**` and then rejected the
legitimate P14 product-boundary changes against its old certified-base isolation rule. P14 Research
paths are now excluded from M1 and that CI-economy rule is enforced by governance. P14's own
provider-free seal remains authoritative for this slice.

P13D period-comparison remains deferred compatibility debt. No dima.7, codec widening, query rewrite,
native-core patch or additional model/live run was performed.

status:
`SEALED / P14 PRODUCT RESEARCH-ASK BOUNDARY PROVIDER-FREE GREEN / P13 TRUST REUSED / NATIVE SUBSTRATE UNCHANGED`.

Next phase:
`P15 NATIVE METABASE EXPLORATIONS INTEGRATION` is next and is not started by this decision receipt.
---

## DMP-DEC-0047 — Thin Native Analytics Gateway; P14 temporal-gate reclassification

date: 2026-09-25

context:
DMP-P14-RUNTIME-STOP-001 correctly stopped production wiring rather than inventing a shared admin
session, a second security authority, fixture-backed production truth or a new temporal parser.
A follow-up architecture audit compared that STOP against DMP-DEC-0044/current product ownership and
the read-only `feat/ask-v2-mvp` patterns.

The earlier STOP mixed one obsolete P13-era requirement with two real deployment seams.

### Decision

```text
METABASE + METABOT
= analytical definition / temporal-query semantics / query cognition / execution owner

DIMA
= business ontology + exact engine-resource mapping
+ product principal/policy binding
+ Research / claim-lineage Evidence / Findings / Decision / Action / Memory
```

P13 remains a sealed trust/provenance baseline. P14 MUST NOT recreate full
`ResolvedAnalyticsIntent` / operator-by-operator analytical authority for every Research obligation.

### Reclassified blocker — absolute named-month temporal authority

The requirement:

```text
Research "Haziran 2026"
→ Dima must independently mint exact ResolvedPeriod bounds
→ only then native Research may execute
```

is REMOVED as a generic P14 production-runtime prerequisite.

Reason:
- DMP-DEC-0044 already assigns native temporal/query mechanics to Metabase/Metabot;
- forcing Research to create a second absolute-month temporal owner would restart P13 operator
  generalization and create a shadow analytical engine;
- accepted Research context still preserves the user's temporal surface/objective for lineage;
- native Metabot may interpret that temporal analytical request using its native cognition;
- Dima records the actual engine resource, executed native occurrence, observed scope/result,
  principal, receipt and Evidence lineage;
- explicit company/sector fiscal-calendar policy or unresolved material business ambiguity remains
  Dima-owned and must fail closed when genuinely material.

Therefore P14 must NOT add a generic absolute-month parser, second temporal planner or old-prompt
reparse merely to satisfy P13's historical Standard shape.

### Real deployment seam 1 — principal to native subject/session

A production binding is still required between:

```text
authenticated Dima Principal
→ exact effective Metabase native subject/session
```

This is a thin integration/provider seam, NOT a new identity authority.

It may:
- resolve an already-configured/native Metabase user/session for the authenticated Dima principal;
- carry tenant/principal correlation and expected native subject identity;
- use native Metabase authentication/session/SSO mechanisms.

It may NOT:
- decide data permissions independently of Metabase/DB;
- invent a Dima RLS engine;
- use shared admin/global analytical sessions;
- silently downgrade to a service user;
- create a second product authentication authority.

Before implementation, inspect pinned Metabase authentication/session surfaces and existing product
deployment configuration. Prefer pass-through/native session binding over a custom identity broker.

### Real deployment seam 2 — business concept/resource binding

Production Research still needs a truthful mapping:

```text
Dima business concept/context
→ exact current Metabase Metric / Model / field / resource identity
```

This must reuse existing P9/P10/P13 persisted contracts and current native resource facts where
available. It must NOT duplicate Metabase analytical formulas or promote Boyahane lab fixtures as
production truth.

`DimaSemanticSpec` remains a sealed compatibility asset, but new native work treats it as business
ontology / engine-resource mapping rather than a second analytical-definition store.

### Research execution contract after this decision

```text
accepted Research obligation
→ native Metabot conversation/session
→ native analytical cognition
→ exact native material occurrence
→ thin Native Analytics Gateway checks:
     principal/native-subject correlation
     exact engine-resource mapping when materially required
     exact occurrence/runtime identity
     unresolved material business-policy ambiguity
→ native Metabase execution
→ existing P5 QueryReceipt
→ claim-lineage Evidence
→ Research state
```

The gateway does NOT interpret every filter/order/breakout/temporal primitive.

`VERIFIED` Evidence proves claim lineage, principal/resource/runtime provenance and absence of
unresolved material business ambiguity. It does not mean Dima independently reimplemented and
reproved every internal Metabase operator.

### Ask-v2 reference policy

`feat/ask-v2-mvp` remains READ ONLY.

Useful patterns that may be adopted conceptually:
- principal is passed through to substrate execution rather than replaced by a second identity owner;
- Research task/obligation lifecycle is durable and idempotent;
- failure is obligation-scoped and independent work may continue;
- accepted typed context is persisted rather than reconstructed on resume.

Do NOT import:
- Wren cube/planner semantics;
- Wren-specific SQL/query contracts;
- legacy temporal ownership merely because that branch contains a temporal subsystem;
- any second analytical planner.

### P14/P15 gate

P14 production runtime is now blocked only on the real native-subject/session and current
engine-resource/security binding seams. Absolute named-month P13 authority is not a generic blocker.

After those thin seams are provider-free GREEN, run one bounded real native Research canary if it can
change a product decision. P15 remains gated until that P14 runtime/canary boundary is real.

No engine change, dima.7, P13 reopening, Luna/Sol/C1 run or native-core patch is authorized by this
decision.

status:
`SEALED / P14 THIN NATIVE GATEWAY AUTHORIZED / TEMPORAL SHADOW-AUTHORITY BLOCKER REMOVED`.



---

## DMP-DEC-0048 — Native Direct Execution / P13 Certification Microscope Cutover

date: 2026-09-25

supersedes forward authority:
`DMP-DEC-0047` for ordinary production Research execution.

DMP-DEC-0047 remains append-only historical evidence and is reclassified as a transitional
thin-gateway correction that removed the temporal shadow-authority error but still carried too much
P13/P10 machinery into the ordinary P14 hot path.

### Binding decision

```text
METABASE + METABOT
= ANALYTICAL TRUTH + ANALYTICAL EXECUTION

DIMA
= BUSINESS ONTOLOGY
+ RESEARCH
+ EVIDENCE / CLAIM LINEAGE
+ HYPOTHESIS
+ ROOT CAUSE
+ DECISION
+ ACTION
+ OUTCOME
+ MEMORY
```

```text
METABASE PROVES THE ANALYSIS.
DIMA PROVES THE LINEAGE AND DECISION CONTEXT.
```

### P13

P13 is not deleted and its sealed history is not rewritten.

Forward role:
`CERTIFICATION MICROSCOPE`.

Allowed:
release/certification, benchmark diagnostics, incidents, forensics, silent-wrong investigation and
high-risk compatibility analysis.

Not allowed as mandatory ordinary Research middleware:
`/api/dima/engine/v1/native-query-attestation` and
`/api/dima/engine/v1/native-query-execution`.

No P13 operator-grammar extension.

### Production execution contract

```text
Research obligation
→ same principal-scoped authenticated native Metabot session
→ Metabot produces query A
→ capture query A exactly
→ same authenticated Metabase client
→ native dataset execution of query A
→ native result
→ one DimaQueryReceipt
→ Evidence
→ Research state
```

Exactly one analytical execution. Dima neither rewrites query A nor creates query B.

Metabase owns query validation/repair, permissions, metadata resolution, MBQL, QP, drivers and
execution.

### Principal/security decision

`NativeSubjectBinding` is identity correlation only.
Runtime must verify the presented native session with `/api/user/current`.

Metabase remains permission authority.

Forbidden:
shared admin analytical session, global analytical service user, admin fallback and Dima-built
shadow RLS/permission truth.

Existing `security_profile` / `policy_version` columns may remain temporarily as
non-authoritative compatibility metadata; no cosmetic migration churn is required.

### Resource mapping decision

Dima resource mappings may support business ontology/provenance/discovery, but they are not an
operator-level authorization system and are not required for every ordinary native Research query.

Generic P14 hot path must not inspect aggregation/temporal/filter/breakout/order-by structure to
decide whether Metabase may execute its own native query.

### P10 decision

Generic P14 Research no longer requires
`ExecutionAccessSnapshotIssuer.issue_research_material()`.

Authenticated Metabase execution is the native permission enforcement owner. Add Dima-specific
security checks only when they represent real product policy not owned by Metabase/database.

### Receipt decision

There remains exactly one receipt family: `DimaQueryReceipt`.

For `authority_kind=research_material`, the single receipt contract is widened conditionally to
native Research provenance. Research does not pretend to own Standard `projection_hash` or
`resolved_intent_hash` semantics.

Standard receipt behavior remains unchanged and must remain regression-GREEN.

### Evidence decision

Native Research `VERIFIED` means verified execution/subject/result/receipt/obligation lineage, not
Dima re-certification of native analytical operator semantics. Receipted native result is Evidence;
claim-level maturation remains P16+.

### Current state at decision

```text
Platform HEAD before 0048 = 3dc544b95c05044e35c6903b720a6ddb824e9b37
governance                 = 36095837229 SUCCESS
P14 provider-free          = 36095837211 FAILURE
focused                    = 13 PASS / 6 FAIL
engine                     = cbe313af9ac2d5960f662068e433d328d896fb06
release                    = 0.63.18-dima.6
engine certification       = 36042062775 SUCCESS
```

The six RED tests are not authority to preserve the thick gateway. Architecture is cut first.

status:
`SEALED ARCHITECTURE / NATIVE-DIRECT P14 AUTHORIZED / P13 CERTIFICATION MICROSCOPE / CURRENT IMPLEMENTATION NOT YET SEALED`.


---

## DMP-DEC-0048 — IMPLEMENTATION / P14 FINAL SEAL EVIDENCE

date: 2026-09-25

This is implementation evidence under the existing DMP-DEC-0048 authority. It is **not** a new
architecture decision and does not create DMP-DEC-0049.

Final implementation checkpoint before documentation-only overlays:

```text
Platform code SHA                  = 01140b059318b2487b002a0c94f989fd693ce6f2
engine gitlink                     = cbe313af9ac2d5960f662068e433d328d896fb06
engine release                     = 0.63.18-dima.6
engine certification               = 36042062775 SUCCESS
final P14 governance               = 36102734425 SUCCESS
final P14 provider-free seal       = 36102734433 SUCCESS
real native-direct Luna canary     = 36100443464 SUCCESS
second paid P14 model run          = 0
```

The final P14 seal proves the DMP-DEC-0048 production contract:

```text
Metabot produces query A
→ Dima captures A exactly
→ A + fingerprint are durable
→ same principal-scoped Metabase client executes A through /api/dataset
→ result/runtime/native subject are durable
→ one DimaQueryReceipt(authority_kind=research_material)
→ Evidence
→ Research obligation
```

Final durability hardening closes the remote-call crash window:

```text
CANDIDATE_CAPTURED
→ persist EXECUTION_STARTED
→ only then call /api/dataset

EXECUTION_STARTED without persisted result
→ outcome UNKNOWN
→ NO blind retry
→ explicit limitation/recovery

EXECUTED with persisted result
→ resume persisted result
→ same deterministic receipt
→ NO second /api/dataset
```

Transport-correctness closure reuses the already-paid live artifact from run
`36100443464`. The future canary now asserts the frozen Boyahane result:

```text
Mevcut Müşteri = 34
Web             = 27
Fuar            = 22
Saha Ziyareti   = 22
Referans        = 21
```

No second Luna run was made merely to add the sentinel.

Final ownership proof:

```text
P13 attestation hot-path calls     = 0
P13 re-execution hot-path calls    = 0
P10 synthetic Research access path = 0
operator-level Dima MBQL proof     = 0
Wren fallback                      = 0
raw SQL fallback                   = 0
Agent API analytical fallback      = 0
admin/service analytical fallback  = 0
second receipt family              = 0
second analytics authority         = 0
second security authority          = 0
engine changes/builds              = 0
```

P13 remains SEALED as certification/debug/forensics machinery beside the product path.

Final phase status:

```text
P14 FOUNDATION                    = GREEN / SEALED
P14 PRODUCT RESEARCH              = GREEN / SEALED
P14 ACCEPTED CONTEXT DURABILITY   = GREEN / SEALED
P14 PRINCIPAL-SCOPED SESSION      = GREEN / SEALED
P14 NATIVE-DIRECT EXECUTION       = GREEN / SEALED
P14 SINGLE RECEIPT / EVIDENCE     = GREEN / SEALED
P14 RESTART / IDEMPOTENCY         = GREEN / SEALED
P14 LIVE NATIVE CANARY            = GREEN / SEALED
P14 TRANSPORT CORRECTNESS         = GREEN / SEALED
P14                              = CLOSED
P15 NATIVE METABASE EXPLORATION   = AUTHORIZED / NEXT
```

Do not reopen P14 as P14B/P14C. Do not restore thick-gateway/P13 middleware.

status:
`SEALED IMPLEMENTATION / P14 CLOSED / DMP-DEC-0048 FORWARD AUTHORITY / P15 NEXT`.


---

## DMP-DEC-0048 — P15 / P16 CORE-AUTHORITY IMPLEMENTATION EVIDENCE

date: 2026-09-25

No new DMP-DEC is created. DMP-DEC-0048 remains the forward architecture authority.

### P15 Native Metabase Exploration

```text
seal commit / tested SHA          = c529f28d34712d149f1c3c1e594a413974c37130
provider-free run                 = 36103561534 SUCCESS
governance                        = GREEN
engine patch/build                = 0
model calls                       = 0
Python analytical primitive copy = 0
```

The first P15 vertical consumes one VERIFIED P14 native occurrence, reuses its exact captured query
A and principal-scoped native session, delegates to pinned Metabase X-Ray/automagic analysis, and
stores only durable native Research material/provenance.

P15 output is explicitly `RESEARCH_MATERIAL`. It is not a claim or finding.

### P16 Claim-lineage Evidence

```text
seal commit / tested SHA = 9fa97e041bf51e87518943d010a070cce6b0dcac
provider-free run        = 36104299903 SUCCESS
governance run           = 36104299868 SUCCESS
engine patch/build       = 0
model calls              = 0
```

The P16 gate proves the entire authority chain in one run:

```text
P16 claim-lineage focused proof = SUCCESS
P15 native Exploration regression = SUCCESS
P14 native-direct regression = SUCCESS
```

P16 durable semantics:
- P15 lead/material may be claim origin only;
- claim begins `PROPOSED`;
- only eligible P14 Evidence edges change epistemic state;
- `SUPPORTS`, `CHALLENGES`, `CONTEXTUALIZES`, `INSUFFICIENT` are explicit;
- support + challenge becomes `CONTESTED`;
- insufficient-only becomes `INSUFFICIENT_EVIDENCE`;
- contextual material does not promote truth;
- Evidence relation for a claim is immutable once recorded;
- receipt/execution provenance mismatch fails closed;
- no numeric confidence exists.

Current phase state:

```text
P14 = SEALED
P15 = SEALED
P16 = SEALED
P17 = AUTHORIZED / OPEN
```

The next owner is P17 Research Manager maturation. It consumes P14/P15/P16; it must not invent a
parallel analytics or claim authority.

---

## DMP-DEC-0049 — RECURSIVE INVESTIGATION / ANALYTICAL DELEGATION / P17-P19 AUTHORITY SPLIT

date: 2026-09-25

### Decision

DMP-DEC-0048 remains authoritative for native-direct analytical ownership, the sealed P13
certification/debug/forensics role, Metabase analytical authority, the single
`DimaQueryReceipt` family, and Evidence provenance.

DMP-DEC-0049 extends forward authority for recursive investigation, multi-branch investigation
topology, multi-factor explanation boundaries, the P17/P19 split, and analytical-delegation
invariants.

Permanent architecture:

```text
METABASE + METABOT
= ANALYTICAL ENGINE

DIMA
= INVESTIGATION
+ EPISTEMICS
+ DECISION BRAIN
```

Permanent invariant 1:

```text
DIMA NEVER COMPUTES AN ANALYTICAL ANSWER
THAT METABASE CAN NATIVELY COMPUTE.

DIMA DECIDES WHICH ANALYTICAL QUESTION
SHOULD BE ASKED NEXT
AND HOW THE RESULTING EVIDENCE
CHANGES THE INVESTIGATION STATE.
```

Permanent invariant 2:

```text
RECURSIVE DEPTH BELONGS TO DIMA.

ANALYTICAL DEPTH EXECUTION
BELONGS TO METABASE.
```

These invariants bind P17 through P21.

### P17 authority: investigation topology, not causal truth

P17 owns durable investigation topology and orchestration:

```text
question
observed gap
candidate explanation to investigate
test target
child question
Evidence
counter-Evidence
branch stop
investigation stop
```

A parent→child investigation edge means only:

```text
WE CHOSE TO INVESTIGATE DEEPER
```

It does not assert causal truth. P17 must not introduce root-cause ranking, causal confidence,
causal scoring, contribution attribution, direct/indirect effect calculation, Bayesian
probabilities, causal-path strength, or causal-graph inference.

P17 may decide:

```text
what explanation should be investigated
which branch matters
which alternative remains untested
what Evidence could falsify a claim/explanation
whether a branch should deepen
whether a branch should stop
whether the investigation should stop
```

All analytical fulfillment at every recursive depth remains Metabot/Metabase-owned.

### Durable topology rule

The existing P17 reasoning/task ledger remains the truth store. Recursive investigation extends that
ledger minimally with parent/depth/branch/target identity. Any `InvestigationGraph` is a projection
of durable ledger state, never a second persistence authority and never a generic graph engine.

Accepted P14 obligations remain immutable. Recursive nodes are subordinate P17 state.

### Recursive intent semantics

P17 may evolve its bounded investigation vocabulary toward:

```text
INVESTIGATE_GAP
EXPLORE_ALTERNATIVES
SEEK_COUNTER_EVIDENCE
DEEPEN_EXPLANATION
TEST_DISCRIMINATING_EVIDENCE
REPLAN
STOP_BRANCH
STOP_INVESTIGATION
```

These are investigation intents, not analytical operators. Existing persisted P17 action values may
remain as compatibility representation. No destructive action-enum migration is required merely for
renaming.

Example:

```text
DEEPEN_EXPLANATION
= create a child investigation question about the current explanation
!= decomposition()
```

### Multi-branch / recursion / stopping

P17 must preserve multiple candidate branches. It must not collapse alternatives into a single
winner. Sibling branches may deepen, stop, remain unresolved, or be contradicted independently.

Recursive depth is bounded and configurable. Default policy may use `max_depth = 5`, but depth is a
budget, never a target.

Branch-local stopping is distinct from investigation-global stopping. Branch outcomes may include:

```text
NO_NEW_EVIDENCE
NO_MEANINGFUL_GAIN
DATA_UNAVAILABLE
CONTRADICTED
OUT_OF_SCOPE
ROOT_EXTERNAL_TO_AVAILABLE_DATA
BUDGET_EXHAUSTED
CAUSAL_IDENTIFICATION_LIMIT
```

No branch is forced deeper merely because budget remains.

Expected information gain may remain typed qualitative/model rationale. P17 must not invent numeric
information-gain/confidence scores without a real measured/statistical quantity.

### P17 native analytical delegation

Every recursive node requiring analytics must reuse the same sealed native-direct occurrence path.

```text
P14_BASE != P17_FOLLOWUP

P17_FOLLOWUP
→ NativeResearchOccurrenceRunner
→ principal-scoped Metabot/Metabase
→ exact captured query
→ one native execution
→ one DimaQueryReceipt family
→ Evidence
```

No second native executor, receipt family, analytical authority, or security authority is permitted.

P15 native Exploration may be reused at any recursive depth, but remains `RESEARCH_MATERIAL`.

P16 remains the single claim↔Evidence lineage authority at every depth. P17 must not create
`P17Claim`, `RootCauseClaim`, or `RecursiveClaim` as parallel truth owners.

### P19 future authority boundary — locked now, implemented later

P19, not P17, owns causal/contribution epistemics.

Permanent distinction:

```text
LEADING CAUSE != CONTRIBUTION
```

A real change may have multiple material contributors. P19 must not be designed as winner-takes-all
root-cause selection.

Future P19 interpretation uses two separate axes:

```text
AXIS 1 — EFFECT / CONTRIBUTION
DOMINANT | MATERIAL | SECONDARY | LOW | UNKNOWN

AXIS 2 — EVIDENCE STRENGTH
STRONG | MODERATE | WEAK | INSUFFICIENT | CONTRADICTED
```

These are qualitative epistemic states, not LLM confidence probabilities.

If contribution is quantitatively measurable, Dima asks the analytical question and native
Metabase capability performs/supplies the analytical computation wherever possible:

```text
USE_NATIVE
→ COMPOSE_NATIVE
→ WRAP_NATIVE
→ HOOK_NATIVE
→ DIMA_OWNS
```

`DIMA_OWNS` is last resort and requires supervisor review.

P19 must preserve enough path identity to distinguish direct from indirect/mediated contribution and
avoid double counting. P17 must not implement that math.

### Auditable investigation trace

The product-level trace is factual system activity, not hidden model chain-of-thought. It should be
derivable from durable authority objects:

```text
ResearchReasoningStep
ResearchInvestigationTask
native occurrence
Evidence
P16 claim lineage
future P19 hypothesis state
```

Permissible trace facts include what question was investigated, which branch opened, which native
work occurred, which Evidence was produced, which branch stopped/deepened, and what remains
unresolved.

Do not persist hidden LLM chain-of-thought.

### Engine / phase boundary

Pinned engine remains:

```text
cbe313af9ac2d5960f662068e433d328d896fb06
0.63.18-dima.6
sha256:40e9a44be49904de3ddf12d4683c768e70955851c10a928a9c8f7d8f60780353
```

No Metabot/QP/Lib/driver patch, engine build, or dima.7 is authorized during P17 recursive closure.

P18 remains blocked until P17 recursive authority is provider-free GREEN and one bounded real Luna
recursive-investigation canary is GREEN. P19 is not authorized for implementation by this decision;
only its future authority boundary is locked.

UI/UX remains forbidden until P21 is sealed.

### STOP conditions

Stop for supervisor if recursive closure appears to require any of:

- an analytics algorithm in Dima;
- Metabot/QP/Lib/driver/core engine modification;
- a new analytical truth owner;
- a second Evidence/claim authority;
- a second native execution path;
- mutation of accepted P14 obligations;
- P17 causal/root-cause truth decisions;
- invented numeric contribution/confidence without analytical/statistical evidence;
- cross-branch Evidence leakage/misbinding;
- destructive migration;
- broad paid evaluation.

Otherwise continue with bounded P17 recursive closure.

status:
`SEALED ARCHITECTURE / DMP-DEC-0048 + DMP-DEC-0049 FORWARD AUTHORITY / P17 RECURSIVE IMPLEMENTATION AUTHORIZED / P18 BLOCKED`.

