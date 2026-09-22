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
