# DIMA DAY14 — DURABLE PERSISTENCE / RESUME CLOSURE

## Status

```text
branch                          feat/ask-v2-mvp
Day10 FINAL                     SEALED
Day14 expanded persistence gate 36233918780 = GREEN
Day14                           CLOSED / PROVIDER-FREE GREEN
DEV80 / Validation50 / Hidden50 NOT RUN
```

## Persisted canonical authority

The durable checkpoint contains typed authoritative state only:

```text
AcceptedTurnContract
UserObligationLedger
ManagerRunSnapshot
ResearchTask lifecycle
Evidence
HypothesisLedger state
directive disposition
ReportDocument lineage
Completion status
Conversation state where applicable
SemanticBinding records
```

Provider reasoning, ActionSet trajectory, raw prompts and scratch cognition are not
persisted as truth.

## Resume contract

Durable restore supports terminal states and canonical post-acceptance active states:

```text
CONTRACT_ACCEPTED
INVESTIGATING
COMPLETED
BUDGET_EXHAUSTED
BLOCKED
NEEDS_CLARIFICATION
FAILED
```

`INITIAL` and `UNDERSTANDING` remain excluded from canonical restore because
preacceptance/model scratch is intentionally not durable authority.

## Crash / idempotency matrix

Provider-free proofs cover:

```text
crash after accepted contract
crash after Evidence creation before obligation consumption
open ROOT / open directive state persistence
completed ResearchTask restart no duplicate side effect
exact checkpoint replay idempotency
foreign principal/context checkpoint miss
stale contract/report writer loses CAS
terminal restart opens same-lineage follow-up
report lineage survives checkpoint reconstruction
```

Atomic file replace + fsync and compare-and-swap revisioning prevent silent
last-write-wins.

## Receipt

```text
workflow  v2-day14-persistence
run       36233918780
result    GREEN
```
