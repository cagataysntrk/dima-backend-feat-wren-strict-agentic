# Native Engine Compatibility Refactor — Final Handoff

Status: **CLOSED / REFACTOR COMPLETE**

Branch:
`feat/native-engine-official-ui`

Date:
`2026-09-23`

## Canonical architecture

```text
Dima UI / existing product experience
        ↓
/api/chat
        ↓
server-side native engine adapter
        ↓
DIMA_ENGINE_URL
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

## Refactor result

Completed:

- existing UI/layout/navigation preserved;
- login/app shell preserved;
- cards/charts/tables/dashboards/model/schema REST surfaces preserved;
- tenant/collection mapping preserved;
- `DIMA_ENGINE_URL` / `DIMA_ENGINE_TENANTS` are canonical frontend runtime configuration;
- frontend no longer owns `OPENROUTER_API_KEY` or `OPENROUTER_MODEL`;
- `/api/chat` routes only to the native engine adapter;
- native Metabot stream is adapted back to the existing UI contract:
  - step;
  - token;
  - done;
  - error;
  - browser abort/stop;
- native `conversation_id + history + state` are carried across turns through an opaque authenticated context token;
- context token is tenant + Dima conversation bound;
- late result cannot silently fall back to the old custom agent;
- old `server/chat/agent.ts`, `server/chat/openrouter.ts`, and legacy prompt loop are removed;
- no silent fallback to custom OpenRouter intelligence exists.

## Canonical engine

Repository:
`UpcyTech/dima-metabase-engine`

Source pin:
`6bb6924452e5b9dc42b3745bb88c3125a468b297`

Release:
`0.63.18-dima.0`

Published runtime contract recorded in workspace configuration:
`sha256:0e6819e36c3bd347238159ae483bbaa8db3f0f36bf23cc5d2d8a23012fe111d9`

The frontend is engine-URL based. Model/provider configuration belongs to the engine.

## Quality certification

Public working branch quality gate:

Run:
`35835138638`

Result:
`GREEN`

Scope:
- lint;
- typecheck;
- tests;
- production build;
- architecture invariants.

## Native live diagnostic

Run:
`35835138646`

Infrastructure and compatibility portions proved:

- exact canonical engine source checkout = PASS;
- source/release equivalence = PASS;
- engine boot = PASS;
- image verification = PASS;
- data import/bootstrap = PASS;
- native Metabot configuration = PASS;
- Dima auth DB/bootstrap = PASS;
- official UI build = PASS;
- official UI start/login path reached;
- `/api/chat -> native Metabot -> OpenRouter Luna -> search/read/query -> /api/dataset` executed.

The diagnostic failed on an **engine-owned analytical correctness oracle**:

```text
question:
1-22 Haziran 2026 arasında satış siparişlerinin toplam tutarı ne kadar?

native result:
274244700.53000027

independent DB oracle:
4655391.95
```

Classification:

`ENGINE_NATIVE_METABOT_ANALYTICAL_CORRECTNESS`

This is **not repaired in the frontend refactor** by design.

The live analytical workflow is therefore manual diagnostic only and is not a push-blocking UI compatibility gate.

## Hard architecture invariants

```text
OLD_DIMA_METABASE_DEPENDENCY = 0
CUSTOM_OPENROUTER_CHAT_HOT_PATH = 0
FRONTEND_MODEL_PROVIDER_OWNERSHIP = 0
SILENT_LEGACY_FALLBACK = 0
NATIVE_METABOT_CHAT_PATH = 1
EXISTING_UI_UX_PRESERVED = required
TENANT_MAPPING_REWRITE = 0
AUTH_ARCHITECTURE_REWRITE = 0
```

## What the next developer should do

Normal UI/UX development may continue from this branch.

Do not reintroduce:
- custom frontend analytical agent loops;
- frontend OpenRouter credentials;
- SQL/tool-loop cognition in the UI repository;
- silent fallback to the old agent.

If Q1/Q2/Q3 analytical quality needs improvement, work belongs in:
`UpcyTech/dima-metabase-engine`

The frontend should consume the improved native engine through the same adapter contract.

## Current ownership

Dima frontend owns:
- UI/UX;
- product API;
- native stream normalization;
- stop/abort behavior;
- tenant/product session;
- opaque native conversation context transport;
- cards/charts/tables/dashboard presentation.

Dima engine owns:
- model/provider;
- native Metabot loop;
- resource discovery;
- query construction;
- query repair;
- skills;
- analytics iteration;
- database execution mechanics.
