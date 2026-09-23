# @dima/metabase-poc

This directory is the current official Dima product UI for the native-first analytics architecture.

## Runtime boundary

```text
Browser
→ Dima Next.js product API
→ server-side Dima engine adapter
→ dima-metabase-engine
→ native Metabot agent loop / Metabase REST APIs
→ customer database
```

Canonical engine:

- release: `0.63.18-dima.0`
- repository: `UpcyTech/dima-metabase-engine`
- source pin: `6bb6924452e5b9dc42b3745bb88c3125a468b297`
- published runtime digest:
  `sha256:0e6819e36c3bd347238159ae483bbaa8db3f0f36bf23cc5d2d8a23012fe111d9`

The source pin is exposed through `../../engine/dima-metabase-engine`.

## Preserved product surfaces

- Better Auth login and organizations/tenants
- chat UX and streaming
- cards and charts
- dashboards
- browse/data
- schema and data model
- SQL runner
- uploads
- settings and i18n

Existing non-chat analytics REST surfaces continue through `src/server/metabase/*` with the current tenant mapping.

## Chat

`/api/chat` no longer owns an LLM provider or custom analytics agent.

Current path:

```text
/api/chat
→ src/server/engine/native-chat.ts
→ POST /api/metabot/agent-streaming
→ profile_id = nlq
```

Native events are adapted to the existing Dima UI contract:

```text
native tool activity → step
native text delta    → token
native completion    → done
native failure       → error
browser abort        → stop
```

Native `conversation_id + history + state` are carried between turns through an authenticated opaque context token bound to the tenant and product conversation.

There is no silent fallback to the legacy custom OpenRouter agent.

Deleted legacy owners:
- `src/server/chat/agent.ts`
- `src/server/chat/openrouter.ts`
- `src/server/chat/prompt.ts`

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

Do not add frontend `OPENROUTER_API_KEY` or `OPENROUTER_MODEL`. Model/provider selection is engine-owned.

## Development

From repository root:

```bash
git submodule update --init --recursive
bun install --frozen-lockfile
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

Or from repository root:

```bash
bun run turbo run lint typecheck test build --filter @dima/metabase-poc
```

## Live-E2E test infrastructure

`e2e/native-engine`, `scripts/native-engine-bootstrap.py` and `scripts/native-ui-e2e.py` are integration-test infrastructure.

Their temporary databases exist to prove login + product + engine + customer-data integration in CI. They are not a new production DB architecture and are not a reason to redesign auth, tenants or data storage.

The manual live diagnostic currently reaches the native engine successfully but exposes an engine-owned analytical correctness issue on the frozen Q1 oracle. See:

`../../docs/NATIVE_ENGINE_REFACTOR_HANDOFF.md`
