# M2-P2-001 — ISOLATED METABASE LAB BOOTSTRAP

**Milestone:** M2 / P2  
**Predevelopment review:** `backend/belgeler/metabase/predev/M2_P2_PREDEVELOPMENT_REVIEW.md`  
**Owner:** Metabase runtime pin + isolated lab infrastructure  
**Status:** RUNTIME PINNED / LAB IMPLEMENTATION AUTHORIZED AFTER GOVERNANCE GREEN

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
