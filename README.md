# Dima — Brain V2.1 / Metabase Platform

This repository contains the canonical headless Dima backend and governed company-intelligence runtime.

## Current authority

```text
working branch
feat/dima-brain-v2-1-specification-closure

architecture
Brain V2.1 = FROZEN

analytics
Metabase / Metabot = single analytical cognition engine

orchestration
BrainV2Service / LangGraph = single forward runtime

engine
4c49b8da6b424b0fa4d8ef340ca1b238d12980c1
0.63.18-dima.11.1
sha256:0ff1e378b532cc986d871ed3945e677a7a6d0bfb28686b344dfa4ec8d397327d
CERTIFIED / FROZEN

frontend / UI / UX implementation
NOT AUTHORIZED
```

Dima owns business intent, scope/currentness, material requirements, Evidence/provenance,
epistemic-owner dispatch, completion, and governed report/decision semantics. It does not own
SQL/MBQL planning or a second analytical engine.

Permanent owner split:

```text
Metabase / Metabot = analytics and native query cognition
LangGraph          = routing / durable forward orchestration
P18                = relationship epistemic owner
P19                = RCA epistemic owner
P17                = bounded NextTest / information-gain controller only
P20                = governed synthesis from terminal state
```

## Specification-closure recovery

The immutable Round-2 broad benchmark is sealed:

```text
run       37027548693
artifact  11235884317
quality   60.5 / 100
simple    87.5
medium    60.0
hard      50.0
```

That benchmark is now a counterexample corpus, not a development loop. Broad paid authorization
is closed. Do not rerun the 30-case without new explicit authorization.

Current recovery objective:

```text
REACH 30-CASE READY WITHOUT RUNNING THE 30-CASE:
COLLAPSE ANALYTICAL MEANING INTO ONE VERSIONED INTENT / EXECUTION BOUNDARY,
PROVE RESULT-DEPENDENT CONTINUATION, CLOSED V1 GRAMMAR, PROVIDER-FREE RECERT,
THEN ONE SAME-SHA 9-CAPABILITY SENTINEL PANEL.
```

Provider-free specification closure is active. Production changes must come from independent
semantic laws, provider-free reproductions, generated/metamorphic siblings, and one-owner root
fixes. Fuzzy/regex/morph/prompt semantic patches and case-specific branches are forbidden.

The living recovery log is:

`backend/belgeler/metabase/DIMA_BRAIN_V2_1_30CASE_READINESS_PROGRESS.md`

## Repository map

- `backend/app/v3/` — canonical Dima Product/domain authorities.
- `backend/app/v3/brain_v2/` — BrainV2Service, LangGraph state, activities, routing adapters.
- `backend/app/v3/substrate/metabase/` — native Metabase/Metabot bridge.
- `backend/control_plane/` — tenant/principal/authorization/durable authority database.
- `backend/migrations/` — canonical Alembic history.
- `backend/tests/` — provider-free, semantic, stateful, metamorphic, security and certification tests.
- `backend/belgeler/metabase/` — current Brain V2.1 documentation authority plus `legacy/`.
- `backend/lab/metabase/` — certification/evaluation harnesses.
- `engine/metabase` — frozen Metabase engine gitlink.

## Canonical documentation

Start with:

`backend/belgeler/metabase/README.md`

Then read, in order:

1. `DIMA_BRAIN_V2_1_FINAL_ARCHITECTURE.md`
2. `DIMA_BRAIN_V2_1_ENGINEERING_PLAYBOOK.md`
3. `DIMA_BRAIN_V2_1_CURRENT_HANDOFF.md`
4. `DIMA_BRAIN_V2_1_SPECIFICATION_CLOSURE_PROGRESS.md`
5. `DIMA_BRAIN_V2_1_FORWARD_RUNTIME_LAWS.md`

Historical documents live only under `backend/belgeler/metabase/legacy/` and are not current
execution authority.

## Local backend

```bash
cd backend
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload
```

`GET /health` is liveness. `GET /health/ready` checks control-plane readiness and reports the
analytical-engine identity.
