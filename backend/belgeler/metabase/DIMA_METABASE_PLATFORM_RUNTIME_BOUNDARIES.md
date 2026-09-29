# DIMA METABASE — CANONICAL RUNTIME AND SECURITY BOUNDARIES

**Status:** ACTIVE CANONICAL PLATFORM CONTRACT  
**Date:** 2026-09-26

## Runtime

~~~text
Dima FastAPI headless shell
→ control-plane tenant/principal authority
→ P14-P21 + Core A Dima authorities
→ native Metabase / Metabot analytical runtime
~~~

There is no Wren runtime, demo data runtime, alternate analytical engine or frontend in the
canonical Platform tree.

## Identity and authorization

- authenticated Principal identity is derived from signed access-token claims;
- tenant/role/superadmin authority is never trusted from request payloads;
- the central authorization matrix remains `control_plane.authorize`;
- tenant-scoped entity lookup preserves non-oracle behavior where the owner requires it;
- sealed P14-P21, Human Adoption, ActionAuthorization and Core A ownership are unchanged.

## Persistence

- control-plane SQLModel/Alembic remains the durable authority database;
- SQLite is local-development convenience only;
- production schema evolution is owned by Alembic;
- canonical migration head at Core A seal is `fb4e6d2a1074`.

## Analytical ownership

~~~text
METABASE + METABOT = analytical computation/execution
DIMA = organizational meaning/authority
~~~

No local Dima aggregation/forecast/root-cause math is introduced by repository cleanup.

## External execution

~~~text
DEFAULT_ACTION_CAPABILITY_REGISTRY = EMPTY
action:execute = ABSENT
real email / Slack / ERP / bank writes = DEFERRED
~~~

The retained Resend seam is productization debt only.

## UI

~~~text
UI IMPLEMENTATION = NOT STARTED
UI AUTHORITY = NOT GRANTED
~~~
