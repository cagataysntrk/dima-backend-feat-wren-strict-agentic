# Dima Backend

The backend is the headless governed company-intelligence layer over the frozen
Metabase / Metabot analytical engine.

It contains no frontend and no Wren execution runtime.

## Canonical runtime surfaces

~~~text
app/v3/                         Dima Product/domain authorities
app/v3/brain_v2/                BrainV2Service / LangGraph forward runtime
app/v3/substrate/metabase/      native Metabase/Metabot bridge
app/v3/core_a/                  ActionWork / Outcome / Memory / Watch / Signal owners
control_plane/                  tenant/principal/auth/durable state
migrations/                     Alembic
tests/                          provider-free/stateful/metamorphic/security certification
belgeler/metabase/              current architecture documentation
belgeler/metabase/legacy/       historical docs only
lab/metabase/                   certification/evaluation harnesses
~~~

Canonical documentation entry point:

`belgeler/metabase/README.md`

Do not start development from a file under `belgeler/metabase/legacy/`.

## Run

~~~bash
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload
~~~

Configure `DIMA_METABASE_NATIVE_BASE_URL` to enable native Research execution against
the certified Metabase runtime.

## Permanent boundaries

- analytics: Metabase / Metabot;
- orchestration: BrainV2Service / LangGraph;
- Dima: requirement/scope/material/Evidence/provenance/completion;
- P18: relationship epistemics;
- P19: RCA epistemics;
- P17: bounded NextTest only;
- P20: governed terminal synthesis;
- no Wren fallback;
- no shadow analytics;
- no Agent API final path;
- no legacy composer final path;
- no frontend/UI implementation until separately authorized.
