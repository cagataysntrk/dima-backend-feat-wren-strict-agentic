# DIMA V1 — PHASE-1 EXECUTION STATUS

Status: LIVING EXECUTION LEDGER  
Baseline authority: `4906c99f7f52aa800c42279b2fb68fc4435b911f`  
Engine: `cbe313af9ac2d5960f662068e433d328d896fb06` / `0.63.18-dima.6`

The historical baseline remains `DIMA_V1_PHASE1_GAP_MAP.md`. This file records
execution progress only.

Status vocabulary is exact:

`NOT_STARTED | IN_PROGRESS | FOCUSED_GREEN | WAVE_GREEN | SEALED`

| ID | Baseline classification | Current status | Behavior SHA | Focused proof | Affected regression | Remaining blocker |
|---|---|---|---|---|---|---|
| P1 | CONTRACT_MISMATCH | IN_PROGRESS | PENDING_WAVE_A_SHA | semantic-only DTO; server-bound IDs; one repair; internal/provider split candidate | P17/Core-B affected closure pending Wave-A CI | focused rerun after final hardening |
| P2 | MISSING | IN_PROGRESS | PENDING_WAVE_A_SHA | ScopeVersion/mutations + production follow-up/lineage-head candidate | P14/P16/P19/P20 cross-scope suite pending Wave-A CI | Wave-A focused proof |
| P3 | CONTRACT_MISMATCH | IN_PROGRESS | PENDING_WAVE_A_SHA | AnalyticalRequestContract structural boundary candidate | P13D retained-trust regression pending Wave-A CI | focused proof |
| P4 | PARTIAL_MUST_EXTEND | IN_PROGRESS | PENDING_WAVE_A_SHA | Completion Ledger candidate | owner-scoped MUST/Product regression pending Wave-A CI | focused proof |
| P5 | PARTIAL_MUST_EXTEND | IN_PROGRESS | PENDING_WAVE_A_SHA | one-based V1 depth contract + hard cap 3 + typed positive-gain action rule candidate | P17 regression pending Wave-A CI | focused proof |
| P6 | CONTRACT_MISMATCH | NOT_STARTED | - | - | - | Wave A must close first |
| P7 | PARTIAL_MUST_EXTEND | NOT_STARTED | - | - | - | Wave A must close first |
| P8 | MISSING | NOT_STARTED | - | - | - | Wave A must close first |
| P9 | PARTIAL_MUST_EXTEND | NOT_STARTED | - | - | - | Wave A must close first |
| P10 | ALREADY_PROVEN | NOT_STARTED | retained | existing P20 proof retained | Wave-B affected proof only | Wave B |
| P11 | PARTIAL_MUST_EXTEND | NOT_STARTED | - | - | - | Wave B |
| P12 | PARTIAL/MISSING | NOT_STARTED | - | - | - | Wave C only |
| P13 | MISSING | NOT_STARTED | - | - | - | Wave C only |

## Wave A acceptance

Wave A becomes `WAVE_GREEN` only when all are true:

- repository story lifecycle governance GREEN;
- P1 provider invalidity is the only repairable family;
- P2 stale/cross-scope negative proofs GREEN;
- P3 request-contract architecture proof GREEN while retained trust/security proof stays GREEN;
- every USER_MUST has a terminal P4 completion disposition;
- P5 hard contract depth is 1..3 and depth-increasing moves carry typed positive-gain requirement;
- affected provider-free closure GREEN;
- engine diff = 0;
- UI/frontend diff = 0;
- Wren runtime/code import = 0.

Wave A GREEN authorizes automatic entry into Wave B. It does not authorize Phase 2.
