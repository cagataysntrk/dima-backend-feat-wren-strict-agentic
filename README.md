# Dima — Brain V2.1 / Metabase Platform

This repository contains the canonical headless Dima backend and governed company-intelligence
runtime.

## Current architecture

~~~text
METABASE / METABOT
= single analytical cognition engine

BRAIN V2 SERVICE / LANGGRAPH
= single forward orchestrator

DIMA
= requirement meaning
+ scope/currentness
+ material authority
+ Evidence/provenance
+ completion

P18
= relationship epistemic owner

P19
= RCA epistemic owner

P17
= typed NextTest / information-gain controller only

P20
= governed synthesis from terminal state
~~~

There is no Wren execution runtime, no dual analytics engine, no Agent API final path and no
legacy composer in final certification.

## Repository map

- `backend/app/v3/` — canonical Dima Product/domain authorities.
- `backend/app/v3/brain_v2/` — BrainV2Service, LangGraph state/activities/owner adapters.
- `backend/app/v3/substrate/metabase/` — native Metabase/Metabot bridge.
- `backend/control_plane/` — tenant/principal/authorization/durable authority database.
- `backend/migrations/` — canonical Alembic history.
- `backend/tests/` — provider-free, stateful, metamorphic, security and certification tests.
- `backend/belgeler/metabase/` — current documentation authority plus `legacy/`.
- `backend/lab/metabase/` — certification/evaluation harnesses.
- `engine/metabase` — frozen Metabase engine gitlink.

## Current state

~~~text
BRAIN V2.1 ARCHITECTURE FROZEN

semantic Product
ce8704d6a0db10dc3fb6b1a7e5d0f86afe9ccdc9

engine
d5c60dc9f37a9ec9c5b0117f178146bbcb8dca88
0.63.18-dima.9

90+ HIGH-CONFIDENCE READINESS = YES
30-CASE READY = YES

90+ PROVEN = NO
30-case = NOT RUN

frontend = NOT IMPLEMENTED
~~~

Final provider-free closure:

~~~text
Phase-1 provider-free              37020220583 GREEN
Phase-2/headless + metamorphic     37020220833 GREEN
~~~

## Canonical documentation

Start here:

`backend/belgeler/metabase/README.md`

Do not use historical recovery/roadmap documents as current authority. They are archived under
`backend/belgeler/metabase/legacy/`.

## Local backend

~~~bash
cd backend
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload
~~~

`GET /health` is liveness. `GET /health/ready` checks control-plane readiness and reports
the analytical-engine identity.
