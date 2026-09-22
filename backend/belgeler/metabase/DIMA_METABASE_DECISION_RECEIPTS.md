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
