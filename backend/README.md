# Dima Metabase Platform Backend

The backend is a headless organizational-intelligence layer over the frozen
Metabase / Metabot analytical engine.

It does not contain a frontend, a Wren runtime, bundled demo data or an external-action executor.

## Active backend surfaces

~~~text
app/v3/                         sealed Dima authorities
app/v3/substrate/metabase/      native Metabase/Metabot bridge
app/v3/core_a/                  ActionWork / Outcome / Memory / Watch / Signal
control_plane/                  tenant/principal/auth/durable state
product_contracts/              pre-UI contracts
migrations/                     Alembic
tests/                          retained canonical regression
belgeler/metabase/              active authority documentation
lab/metabase/                   active certification only
~~~

The canonical Python runtime contains no Ask-v2 compatibility namespace and no Wren runtime.
Sealed product contracts live under `app/v3/`; historical implementations remain available only
through Git history.

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

- analytics: Metabase / Metabot
- Dima: organizational authority and interpretation
- no Wren fallback
- no shadow analytics
- no external production side effects
- no frontend/UI implementation
- `DEFAULT_ACTION_CAPABILITY_REGISTRY` remains empty until separately authorized
