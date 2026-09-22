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
