# FT-003 FAILURE RECEIPT — FASTAPI_ROUTE_ORACLE_INCLUDED_ROUTER

Status: ROOT CAUSE CONFIRMED
Date: 2026-09-22

FAILURE_ID:
`FT_003_FASTAPI_ROUTE_ORACLE_INCLUDED_ROUTER`

WORKFLOW_RUN:
`35770265501`

TEST:
`test_fast_only_application_does_not_mount_legacy_ask`

FAILURE_CLASS:
`EVAL_ORACLE`

## Evidence

FT-003 core:
- static boundary = PASS
- deterministic core = 11 PASS

FT-003 service/API:
- 5 PASS
- 1 RED

RED:
```text
AttributeError: '_IncludedRouter' object has no attribute 'path'
```

## Root cause

FastAPI/Starlette current route collection may contain an internal `_IncludedRouter`
entry without a `.path` attribute.

The test incorrectly assumed every `app.routes` member exposes `.path`.

This does not indicate:
- Fast Ask route failure;
- auth failure;
- legacy Ask mounting;
- service failure.

The positive authenticated HTTP test already passed.

## Allowed patch

Change only the test oracle to collect path values safely:

```python
paths = {
    path
    for route in app.routes
    if (path := getattr(route, "path", None)) is not None
}
```

## Forbidden patches

- application/router changes;
- remove legacy-route assertion;
- mount/unmount shared app;
- weaken auth;
- V2/V3/Wren changes.

## Focused proof

Re-run `tests/test_fast_ask_service.py`.

Expected:
6 passed.
