# Dima Official UI — Native Engine Architecture

This branch is the official Dima product UI on the native-first analytics architecture.

## Current architecture

```text
User
  ↓
Dima UI / Next.js product
  ↓
Dima product API
  ↓
server-side native engine adapter
  ↓
UpcyTech/dima-metabase-engine
release 0.63.18-dima.0
  ↓
POST /api/metabot/agent-streaming
profile = nlq
  ↓
native Metabot agent loop
  ↓
Metabase analytics/query primitives
  ↓
customer DB
```

Dima owns the user-facing product. Metabase is not the product shell.

## Canonical branches

Supervisor/integration branch:

`cagataysntrk/dima-backend-feat-wren-strict-agentic@feat/native-engine-official-ui`

Team/developer mirror:

`UpcyTech/dima-frontend@feat/native-engine-official-ui`

The refactor is complete. New UI/UX work should build on this native-first baseline rather than recreating the old analytical agent.

## Canonical engine

- repository: `UpcyTech/dima-metabase-engine`
- source pin: `6bb6924452e5b9dc42b3745bb88c3125a468b297`
- release: `0.63.18-dima.0`
- published runtime contract:
  `sha256:0e6819e36c3bd347238159ae483bbaa8db3f0f36bf23cc5d2d8a23012fe111d9`

The engine source is available in this workspace as:

`engine/dima-metabase-engine`

Initialize it with:

```bash
git submodule update --init --recursive
```

## Product app

The current product app is:

`apps/metabase-poc`

Despite the historical directory name, this is the official Dima UI baseline for the native-engine path.

Preserved product surfaces include:
- login and organization/tenant handling;
- application shell and navigation;
- chat UX and streaming;
- cards, charts and tables;
- dashboards;
- browse/data;
- schema/data-model views;
- settings;
- i18n;
- loading/error states.

## Chat ownership

The old frontend intelligence path is gone.

Forbidden architecture:

```text
/api/chat
-> frontend OpenRouter client
-> custom prompt/tool/run_sql loop
-> Metabase
```

Current architecture:

```text
/api/chat
-> src/server/engine/native-chat.ts
-> /api/metabot/agent-streaming
-> native Metabot
```

The frontend does not own:
- `OPENROUTER_API_KEY`;
- `OPENROUTER_MODEL`;
- SQL-generation cognition;
- query-repair cognition;
- a custom analytics agent loop.

There is no silent fallback to the deleted custom agent.

## Multi-turn

Native:
- `conversation_id`;
- `history`;
- `state`;

are preserved across turns in an opaque authenticated context token.

The token is bound to:
- the Dima tenant;
- the Dima product conversation.

The browser transports it but does not interpret native Metabot state.

## Environment

Start from:

`apps/metabase-poc/.env.local.example`

Required frontend-side configuration:

```text
DIMA_ENGINE_URL
DIMA_ENGINE_ADMIN_API_KEY
DIMA_ENGINE_TENANTS
DATABASE_URL
BETTER_AUTH_SECRET
BETTER_AUTH_URL
```

Model/provider credentials belong to the engine, not this UI runtime.

## Development

```bash
bun install --frozen-lockfile
git submodule update --init --recursive

cd apps/metabase-poc
cp .env.local.example .env.local
bun run auth:migrate
bun run seed:users
bun run dev
```

Mandatory quality gate from repository root:

```bash
bun run turbo run lint typecheck test build --filter @dima/metabase-poc
```

Current certified public quality run:

`35836810779 GREEN`

## Live analytical diagnostic

The frontend/native compatibility path has been exercised end-to-end through:
- engine boot;
- tenant/bootstrap;
- Dima login;
- `/api/chat`;
- native Metabot;
- model/provider;
- Metabase tools;
- `/api/dataset`;
- customer-data fixture.

The remaining observed RED is analytical correctness inside the native engine lane, not a frontend migration failure.

Observed diagnostic:

```text
question:
1-22 Haziran 2026 arasında satış siparişlerinin toplam tutarı ne kadar?

native result:
274244700.53000027

independent DB oracle:
4655391.95
```

Do not repair this by reintroducing frontend SQL/prompt intelligence.

If analytical correctness work is needed, the owner is:

`UpcyTech/dima-metabase-engine`

## Important clarification about DB files

The PostgreSQL/Boyahane/bootstrap pieces under the live-E2E harness exist only to reproduce a complete integration test.

They are NOT:
- a new production database architecture;
- a DB migration project;
- a tenant redesign;
- part of the UI refactor scope.

Do not expand them unless working specifically on test infrastructure.

## Handoff

Read this before continuing development:

`docs/NATIVE_ENGINE_REFACTOR_HANDOFF.md`
