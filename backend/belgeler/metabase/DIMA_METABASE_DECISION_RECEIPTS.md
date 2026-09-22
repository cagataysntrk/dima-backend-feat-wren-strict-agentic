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
