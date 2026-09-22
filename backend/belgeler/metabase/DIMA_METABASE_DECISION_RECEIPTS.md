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
