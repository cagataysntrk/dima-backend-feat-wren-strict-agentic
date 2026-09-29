# Dima Metabase Platform

This repository contains the canonical **headless Dima backend/brain**.

## Architecture

~~~text
METABASE + METABOT
= analytical cognition / query construction / execution

DIMA
= company meaning
+ investigation
+ Evidence governance
+ epistemics
+ reporting
+ decision context
+ internal work loop
+ Outcome interpretation
+ institutional memory
~~~

The canonical production analytical engine is **Metabase / Metabot**. There is no Wren
source tree or dual-engine runtime in the canonical Platform.

## Repository map

- `backend/app/v3/` — sealed Dima authority and native Metabase integration.
- `backend/app/v3/core_a/` — closed-loop ActionWork / Outcome / Memory / Watch / Signal owners.
- `backend/control_plane/` — tenant, principal, authorization and durable authority database.
- `backend/product_contracts/` — pre-UI product/UX foundation contracts.
- `backend/migrations/` — canonical Alembic history.
- `backend/tests/` — retained Platform regressions and final certification.
- `backend/belgeler/metabase/` — active architecture, receipts, roadmap and handoff.
- `backend/lab/metabase/` — only active certification/evaluation material.
- `engine/metabase` — frozen Metabase engine gitlink.

## Current state

Core Closure A is sealed. Repository canonicalization precedes Core Closure B.

~~~text
UI IMPLEMENTATION = NOT STARTED
EXTERNAL ACTION EXECUTION = DEFERRED
DEFAULT ACTION CAPABILITY REGISTRY = EMPTY
ENGINE = cbe313af9ac2d5960f662068e433d328d896fb06 / 0.63.18-dima.6
~~~

## Local backend

~~~bash
cd backend
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload
~~~

`GET /health` is liveness. `GET /health/ready` checks the control-plane DB and
reports the frozen analytical-engine identity.

For forward architecture and execution state, read
`backend/belgeler/metabase/DIMA_METABASE_CORE_CLOSURE_FINAL_ROADMAP.md`.
