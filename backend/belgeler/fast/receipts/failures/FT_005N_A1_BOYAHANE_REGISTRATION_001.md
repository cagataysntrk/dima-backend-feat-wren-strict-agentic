# FT-005N FAILURE RECEIPT — A1_BOYAHANE_REGISTRATION_001

Status: ROOT CAUSE CONFIRMED
Date: 2026-09-23

Observed run:
`35821660360`

Observed SHA:
`6bc6e27d1ebc6a57cae7489aae9234576b3e86af`

Failed step:
`Configure stock native Metabot`

Failure:
```text
A1_CONTROL_DATABASE_MISSING: []
```

Native Q1:
`NOT RUN`

## Root cause

The FT-005N bootstrap relied on the fresh-install `POST /api/setup` database payload as if it
were sufficient proof that Boyahane became a registered analytical database.

The repository's already-proven Metabase lab bootstrap does not make that assumption.

Canonical local reference:
`backend/lab/metabase/scripts/bootstrap.py`

It performs:

```text
ensure_setup()
-> GET /api/database
-> if warehouse absent:
     POST /api/database
```

The FT-005N harness omitted this explicit registration step.

With sample content disabled, the database inventory therefore exposed the harness defect instead
of silently letting the Sample Database satisfy native discovery.

## Classification

`HARNESS / A1_DATABASE_REGISTRATION`

This is not:
- native Metabot model-quality evidence;
- Metabase primitive failure;
- Fast architecture evidence;
- a corpus defect.

## Authorized patch

A1 harness only:
1. use the proven list-payload helper shape;
2. explicitly `ensure_database(session)` for Boyahane;
3. retain `MB_LOAD_SAMPLE_CONTENT=false`;
4. verify database inventory contains Boyahane and no Sample Database;
5. wait for Boyahane metadata/table discovery before native Q1;
6. keep exact image/model/question/corpus unchanged.

Forbidden:
- prompt/model change;
- Fast product code change;
- Metabase source patch;
- license bypass;
- corpus mutation.

## Re-proof

Before Q1:
```text
Boyahane registered = YES
Sample Database present = NO
Boyahane table metadata ready = YES
exact v0.63.18 digest = YES
OpenRouter/Luna config = YES
```
