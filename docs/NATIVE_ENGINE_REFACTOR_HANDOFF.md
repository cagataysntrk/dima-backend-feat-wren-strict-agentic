# Native Engine Compatibility Refactor — Developer Handoff

Status: **CLOSED / COMPATIBILITY REFACTOR COMPLETE**

Date: `2026-09-23`

This document is the normative handoff for the next developer. Read it before changing chat, engine integration, tenant mapping, analytics execution, or UI architecture.

---

## 1. Executive summary

The requested job was narrow:

> Preserve the existing Dima product/UI experience and replace the old frontend-owned analytics intelligence path with the canonical Dima Metabase Engine v0.63.18 native Metabot path.

That refactor is complete.

We did **not** redesign:
- the UI;
- auth architecture;
- tenants;
- dashboards;
- cards;
- schema/model UX;
- customer databases;
- application persistence.

The current frontend is now a product/UI layer over the native engine.

---

## 2. Canonical architecture

```text
DIMA FRONTEND
        ↓
DIMA PRODUCT API
        ↓
existing product/run/chat presentation layer
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
Metabase search/resources/query/chart primitives
        ↓
customer DB
```

Normative ownership:

### Dima frontend owns
- UI/UX;
- product routes/API surface;
- login/session presentation;
- tenant/product identity;
- native stream normalization;
- browser stop/abort behavior;
- opaque native conversation-context transport;
- cards/charts/tables/dashboard presentation;
- frontend experimentation.

### Dima engine owns
- LLM provider/model;
- native Metabot loop;
- resource discovery;
- analytical iteration;
- query construction;
- query repair;
- skills;
- query/chart mechanics;
- DB drivers/execution behavior.

The frontend must not become a second analytics intelligence engine again.

---

## 3. Branches and repositories

### Supervisor/integration truth

Repository:

`cagataysntrk/dima-backend-feat-wren-strict-agentic`

Branch:

`feat/native-engine-official-ui`

Current handoff baseline before this docs-only reconciliation:

`256af2ea97977a9b5ffab2f600598a627f7ed484`

Latest public quality run on that baseline:

`35836810779 GREEN`

### Team/developer mirror

Repository:

`UpcyTech/dima-frontend`

Branch:

`feat/native-engine-official-ui`

Mirror handoff baseline:

`f04d27c7108c13a63ef4e1c120d2a3e42fffde81`

The private branch preserves some developer-only history/docs while carrying the native-engine refactor.

For normal team UI/UX work, develop from the UpcyTech mirror unless the supervisor explicitly asks to work on the public integration branch.

Do not run two independent architecture branches and later try to reconcile them manually.

---

## 4. Canonical engine pin

Repository:

`UpcyTech/dima-metabase-engine`

Source pin:

`6bb6924452e5b9dc42b3745bb88c3125a468b297`

Release:

`0.63.18-dima.0`

Release contract:

`semantic_behavior_changes = 0`

Published runtime contract recorded for Dima:

`sha256:0e6819e36c3bd347238159ae483bbaa8db3f0f36bf23cc5d2d8a23012fe111d9`

Source workspace:

`engine/dima-metabase-engine`

Initialize:

```bash
git submodule update --init --recursive
```

### Important CI distinction

The manual live analytical diagnostic currently uses the exact source-equivalent upstream v0.63.18 Metabase image:

`metabase/metabase@sha256:1160b570cb11c107bce00e71293552df8a8363e01a32c2c7a048cee002dc8a73`

Why:
- the pinned Dima engine revision declares zero semantic behavior changes;
- the diagnostic verifies source equivalence separately;
- this avoids confusing a package-publication/GHCR issue with frontend compatibility.

Do not replace deployment pins with floating `latest`.

---

## 5. What changed

### 5.1 Runtime configuration

Old frontend naming/ownership was retired from the official path.

Canonical frontend-side variables:

```text
DIMA_ENGINE_URL
DIMA_ENGINE_ADMIN_API_KEY
DIMA_ENGINE_TENANTS
```

Frontend no longer owns:

```text
OPENROUTER_API_KEY
OPENROUTER_MODEL
```

Model/provider configuration belongs to the engine.

### 5.2 Chat intelligence seam

Old:

```text
ChatView
→ /api/chat
→ server/chat/agent.ts
→ OpenRouter
→ custom prompt/tool/run_sql loop
→ Metabase
```

Current:

```text
ChatView
→ /api/chat
→ src/server/engine/native-chat.ts
→ /api/metabot/agent-streaming
→ native Metabot
```

There is no silent fallback.

### 5.3 Legacy intelligence removal

Removed from product tree:
- `src/server/chat/agent.ts`;
- `src/server/chat/openrouter.ts`;
- `src/server/chat/prompt.ts`.

Architecture tests require these files to remain absent.

### 5.4 Existing UX contract preserved

Native stream is adapted to the existing UI contract:

```text
native tool/search/query activity → step
native text delta                 → token
native completion                 → done
native failure                    → error
browser abort                     → stop
```

ChatView was not rewritten into a Metabase UI.

### 5.5 Multi-turn preserved

Native:
- `conversation_id`;
- `history`;
- `state`;

are carried between turns in an encrypted/authenticated opaque engine-context token.

Token binding:
- Dima tenant;
- Dima product conversation.

The browser does not interpret or mint native Metabot state.

### 5.6 Non-chat product surfaces preserved

Current:
- cards;
- charts;
- tables;
- dashboards;
- browse/data;
- schema/model;
- settings;
- tenant/collection mapping;

were deliberately not redesigned.

Existing REST access continues through `src/server/metabase/*`, now pointed at the canonical Dima engine target/config.

---

## 6. Most important files

### Engine adapter

`apps/metabase-poc/src/server/engine/client.ts`

Responsibilities:
- server-side engine request;
- tenant API-key authentication;
- timeout/error normalization.

`apps/metabase-poc/src/server/engine/native-chat.ts`

Responsibilities:
- call `/api/metabot/agent-streaming`;
- parse native stream protocol;
- normalize native tool activity to UI steps;
- forward answer deltas;
- carry native state/history;
- execute generated query for Dima result rendering;
- emit final Dima chat event.

`apps/metabase-poc/src/server/engine/context.ts`

Responsibilities:
- seal/open opaque engine context;
- tenant binding;
- Dima conversation binding;
- tamper rejection.

### Product API

`apps/metabase-poc/src/app/api/chat/route.ts`

Must route only to the native engine adapter.

### UI

`apps/metabase-poc/src/app/app/chat/ChatView.tsx`

Preserves:
- current composer/chat UX;
- step display;
- answer streaming;
- stop behavior;
- result/chart/table presentation.

### Existing Metabase/product REST layer

`apps/metabase-poc/src/server/metabase/*`

Do not bulk-rewrite this layer during unrelated UI work.

### Architecture guard

`apps/metabase-poc/src/server/engine/architecture.test.ts`

This is a critical regression barrier.

It asserts:
- native adapter owns chat hot path;
- legacy custom analytics agent is absent;
- frontend OpenRouter ownership is absent;
- canonical engine release/digest is documented.

---

## 7. Quality status

Public branch final quality gate:

`35836810779 GREEN`

The push gate covers:

```text
lint
typecheck
unit tests
production build
architecture invariants
```

Canonical command:

```bash
bun run turbo run lint typecheck test build --filter @dima/metabase-poc
```

Private team mirror was also reconciled and quality-tested during refactor completion.

---

## 8. Live native diagnostic status

The manual live workflow is:

`.github/workflows/native-engine-live-e2e.yml`

It is **diagnostic**, not the normal push-blocking UI gate.

It has proven the compatibility chain far enough to show:

- engine source pin checkout works;
- v0.63.18 source/release equivalence check works;
- engine boots;
- Boyahane test data imports;
- native Metabot config works;
- Dima auth bootstrap works;
- official UI builds;
- official UI starts;
- login path works;
- `/api/chat` reaches native Metabot;
- native Metabot reaches the model;
- native tools/search/query are exercised;
- `/api/dataset` executes.

Observed Q1 diagnostic:

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

This is not a frontend compatibility-refactor defect.

Do not fix it by reintroducing:
- frontend SQL generation;
- custom frontend prompts;
- a second query agent;
- fallback to the deleted legacy pipeline.

If this analytical result must be corrected, work belongs in the engine repository.

---

## 9. Why there are DB/import/bootstrap files

This confused scope during development, so the distinction is now explicit.

Files under:
- `apps/metabase-poc/e2e/native-engine/`;
- `apps/metabase-poc/scripts/native-engine-bootstrap.py`;
- `apps/metabase-poc/scripts/native-ui-e2e.py`;

exist only to create a reproducible live integration test:

```text
temporary Boyahane DB
+ temporary engine application DB
+ temporary Better Auth DB
+ exact engine runtime
+ official UI
→ full E2E diagnostic
```

They do **not** represent:
- a new production DB architecture;
- a DB migration project;
- a tenant redesign;
- an auth rewrite;
- product persistence redesign.

Unless you are working on E2E infrastructure, leave them alone.

---

## 10. Hard invariants

Keep these true:

```text
OLD_DIMA_METABASE_DEPENDENCY = 0
CUSTOM_OPENROUTER_CHAT_HOT_PATH = 0
FRONTEND_MODEL_PROVIDER_OWNERSHIP = 0
SILENT_LEGACY_FALLBACK = 0
NATIVE_METABOT_CHAT_PATH = 1
EXISTING_UI_UX_PRESERVED = required
TENANT_MAPPING_REWRITE = 0 unless explicitly approved
AUTH_ARCHITECTURE_REWRITE = 0 unless explicitly approved
FRONTEND_ANALYTICS_ENGINE = 0
```

---

## 11. What the next developer should do

The compatibility refactor is finished.

The next developer may continue normal Dima UI/UX/product work from this baseline.

Priority rule:

```text
UI/product problem
→ fix in frontend

native analytics/query/retrieval/reasoning problem
→ fix in dima-metabase-engine
```

Do not blur this ownership boundary.

### Before every meaningful change

Run:

```bash
bun run turbo run lint typecheck test build --filter @dima/metabase-poc
```

For chat changes additionally verify:
- step stream still renders;
- token stream still renders;
- done/error states still work;
- Stop aborts browser consumption;
- late result cannot overwrite cancelled UI state;
- new conversation starts with new native context;
- same conversation carries native context;
- TR/EN presentation remains intact.

---

## 12. Local start

```bash
git checkout feat/native-engine-official-ui
git pull
git submodule update --init --recursive
bun install --frozen-lockfile

cd apps/metabase-poc
cp .env.local.example .env.local
```

Configure:
- `DIMA_ENGINE_URL`;
- `DIMA_ENGINE_ADMIN_API_KEY`;
- `DIMA_ENGINE_TENANTS`;
- `DATABASE_URL`;
- `BETTER_AUTH_SECRET`;
- `BETTER_AUTH_URL`.

Then:

```bash
bun run auth:migrate
bun run seed:users
bun run dev
```

Do not add OpenRouter credentials to the frontend env.

---

## 13. Do not resurrect old architecture

Do not:
- restore deleted `server/chat/*` intelligence;
- add frontend LLM calls;
- route native failure to a legacy fallback;
- copy engine prompt/tool logic into React/Next;
- redesign tenant/auth while doing UI work;
- treat live-E2E temporary databases as production architecture;
- point runtime at old `UpcyTech/dima-metabase`;
- use floating `latest` as a canonical runtime pin.

---

## 14. If you need to change the engine

Engine repository:

`UpcyTech/dima-metabase-engine`

Current source pin:

`6bb6924452e5b9dc42b3745bb88c3125a468b297`

If engine behavior changes:
1. make the change in the engine repo;
2. test/release it there;
3. create a new immutable engine version/digest;
4. update the frontend submodule pin;
5. update `NATIVE_ENGINE_WORKSPACE.md`, `.env.local.example`, architecture tests and this handoff;
6. rerun frontend quality;
7. rerun manual live diagnostic where relevant.

Never silently mutate the meaning of an existing released engine pin.

---

## 15. Handoff decision

```text
NATIVE ENGINE COMPATIBILITY REFACTOR = COMPLETE
FRONTEND QUALITY = GREEN
LEGACY CUSTOM ANALYTICS AGENT = REMOVED
NORMAL UI/UX DEVELOPMENT = UNBLOCKED
ENGINE ANALYTICAL CORRECTNESS Q1 = OPEN IN ENGINE OWNER
```

This is the baseline to continue from.
