# @dima/metabase-poc

The official Dima product UI for the native-first analytics architecture. End users see Dima only; the canonical analytics runtime is `UpcyTech/dima-metabase-engine`.

## Runtime boundary

```text
Browser
→ Dima Next.js product API
→ server-side Dima engine adapter
→ dima-metabase-engine
→ native Metabot agent loop / Metabase REST APIs
→ customer database
```

- **Engine release:** `0.63.18-dima.0`
- **Runtime image:** `ghcr.io/upcytech/dima-metabase-engine:0.63.18-dima.0`
- **Runtime digest:** `sha256:674d1ac4a929b95ab476bcdf37baa43099b398c444bc3f53fef404318892554b`
- **Engine source:** repository submodule at `../../engine/dima-metabase-engine`

The archived `UpcyTech/dima-metabase` repository is not a runtime dependency.

## Product surfaces

The existing Dima UI remains authoritative:

- Better Auth login and organizations/tenants
- chat UX and streaming
- cards and charts
- dashboards
- browse/data
- schema and data model
- SQL runner
- uploads
- settings and i18n

Existing non-chat analytics APIs continue through `src/server/metabase/*` with each tenant's engine API key.

## Chat

`/api/chat` no longer owns an LLM provider or a custom SQL agent. It calls:

```text
POST /api/metabot/agent-streaming
profile_id = nlq
```

through `src/server/engine/*`.

Native `conversation_id`, `history`, and `state` are preserved between turns inside an authenticated opaque context token bound to the Dima tenant and product conversation. The browser does not interpret native state.

Native events are adapted to the existing Dima UI contract:

```text
native tool activity → step
native text delta    → token
native completion    → done
native failure       → error
```

There is no silent fallback to the legacy custom OpenRouter agent.

LLM provider/model configuration is engine-owned. The frontend does not require `OPENROUTER_API_KEY` or `OPENROUTER_MODEL`.

## Environment

Copy `.env.local.example` and configure:

```text
DIMA_ENGINE_URL
DIMA_ENGINE_ADMIN_API_KEY
DIMA_ENGINE_TENANTS
DATABASE_URL
BETTER_AUTH_SECRET
BETTER_AUTH_URL
```

`DIMA_ENGINE_TENANTS` keeps the current tenant mapping shape so existing cards, dashboards, permissions and collections remain compatible during this refactor.

## Development

From the repository root:

```bash
git submodule update --init --recursive
bun install
cd apps/metabase-poc
bun run auth:migrate
bun run seed:users
bun run dev
```

Quality gate:

```bash
bun run lint
bun run typecheck
bun run test
bun run build
```

The engine itself remains independently releasable; the submodule pins the source revision while deployments pin the immutable image digest.
