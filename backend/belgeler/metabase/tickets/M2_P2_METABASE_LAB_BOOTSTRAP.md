# M2-P2-001 — ISOLATED METABASE LAB BOOTSTRAP

**Milestone:** M2 / P2  
**Predevelopment review:** `backend/belgeler/metabase/predev/M2_P2_PREDEVELOPMENT_REVIEW.md`  
**Owner:** Metabase runtime pin + isolated lab infrastructure  
**Status:** CLOSED GREEN

## Goal

Select an exact supported Metabase runtime artifact and build a reproducible, isolated,
self-hosted lab that can be started/restarted/backed-up/probed without any Dima product routing.

## Runtime must be pinned before implementation

```text
METABASE_SOURCE_AUDIT_SHA      = 74216b30981d8310c4cf724d63ca282e2e63529d
METABASE_RUNTIME_VERSION       = v0.63.18
METABASE_RUNTIME_IMAGE_DIGEST  = sha256:1160b570cb11c107bce00e71293552df8a8363e01a32c2c7a048cee002dc8a73
```

No `latest`.

## Files to touch

Only the M2 allowlist from the pre-development review.

## Hard invariants

```text
existing root compose changed             = 0
existing SQL Server lab changed           = 0
Dima v2/v3 product code changed           = 0
Dima→Metabase product routing             = 0
source branch write                       = 0
app DB persistence                        = required
app DB sensitive-store treatment          = required
runtime release + digest                  = exact
Agent API capability inferred from health = forbidden
raw SQL policy assumed from docs          = forbidden
```

## Proof plan

1. config/static validation;
2. immutable image pin check;
3. stack startup + health;
4. bootstrap/persistence/restart;
5. representative analytics connection/query;
6. denied principal/permission negative proof;
7. app-DB backup/restore smoke;
8. Agent API endpoint/auth/capability probe;
9. raw-SQL policy observation;
10. pagination/row-budget observation;
11. teardown/restart reproducibility.

## Exit

Ticket closes only with exact run receipts and SOURCE_LOCK runtime pins.


## Runtime pin receipt

```text
Metabase release   v0.63.18
Metabase image     metabase/metabase@sha256:1160b570cb11c107bce00e71293552df8a8363e01a32c2c7a048cee002dc8a73
PostgreSQL         17.11
Postgres image     postgres@sha256:67f41722b7a8cbdb868a44a4995c846eddfdc2973bccb291ce937dce88ad5675
```

Next: implement only the isolated lab allowlist.


---

## Closure receipt

```text
final implementation SHA       a05bd12ff56ac3c66eef01f7340c1f991ae07681
M2 workflow                    35732633996 = SUCCESS
governance                     35732633999 = SUCCESS
bootstrap                      PASS
Agent API ping                 PASS
search/read-resource           PASS
construct + execute            PASS
combined query                 PASS
pagination                     first=200, second=5
raw SQL kill-switch            403 / PASS
restart persistence            PASS
app DB backup                  PASS
restore smoke                  PASS / 176 public tables
product routing                0
v2/v3 product code edits       0
source branch writes           0
```

Closed failure receipts:
- DMP-M2-RED-001 — shell-sourced env quoting mismatch;
- DMP-M2-RED-002 — exact v0.63.18 setting key/path encoding mismatch.

Exit gate: **GREEN**.

This closure does not authorize P3 client code until a separate P3/P3A pre-development review is sealed.
