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
