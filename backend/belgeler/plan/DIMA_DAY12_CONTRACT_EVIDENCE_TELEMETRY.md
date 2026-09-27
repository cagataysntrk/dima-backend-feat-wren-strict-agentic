# DIMA DAY12 — QUERYCONTRACT / EVIDENCE / TELEMETRY HARDENING

## Status

```text
branch                         feat/ask-v2-mvp
Day10 FINAL                    SEALED
Day12 focused                  36233461322 = GREEN
Day12                          CLOSED / PROVIDER-FREE GREEN
DEV80 / Validation50 / Hidden50 NOT RUN
```

## QueryContract / execution audit

Day12 keeps ContractStore / QueryContract as execution authority and adds a
secret-minimized diagnostic receipt beside the sealed contract. The receipt makes
explicit:

```text
accepted authority
requested capability
obligation IDs
canonical semantic handles + canonical metric/dimension names
model/cube authority
grain
filters
period
comparison
ranking
relationship/join authority when applicable
execution identity
Research run/task identity
tenant/principal/context
planner identity
```

The receipt does not expose raw SQL rows/provider messages and does not authorize
execution.

## Evidence hardening

EvidenceStore is scoped by tenant/principal/context, exact replay is idempotent,
same artifact identity with different truth is rejected, and distinct artifacts for
one task remain distinct rather than being silently collapsed.

Canonical Evidence remains immutable and QueryContract-provenanced. Derived Evidence
preserves parent Evidence / parent QueryContract lineage.

## Telemetry

ProductEvent and Day12 performance receipts are diagnostic only:

```text
EVENT != TRUTH
PERFORMANCE SAMPLE != COMPLETION AUTHORITY
ONE SAMPLE != p95
```

Comparison instrumentation can record first status, first VERIFIED Evidence,
report-ready latency, total latency, provider calls by role, Wren query/dry-plan/
cube-SQL counts and Manager turns without changing Product authority.

## Receipt

```text
workflow  v2-day12-hardening
run       36233461322
result    GREEN
```
