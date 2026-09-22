# @dima/metabase-poc

Whitelabel analytics POC. Metabase OSS is the engine (see the sibling repo
`dima-metabase`). This app is the only UI end users see.

- **Auth:** Better Auth (email + password). Organizations are tenants, and the org slug is the tenant slug. Roles are owner, admin and member.
- **Gateway:** `src/server/metabase/*` (server-only). It calls the engine REST API with the tenant's API key. `adapter.ts` maps results to the dima-backend `QueryResult` contract, so `ResultView`/`Chart` render unchanged. Errors are reworded and never mention the engine.
- **Chat:** `/app/chat` for every role. The model (via OpenRouter, `OPENROUTER_API_KEY` / `OPENROUTER_MODEL`, default `openai/gpt-5.6-sol`) turns the question into SQL. The SQL can only run through the `run_sql` tool, which uses the same SELECT-only guard and tenant DB role as the SQL runner. The answer comes back with a Dima chart and the SQL used, and owner/admin can save it as an analysis. Code is in `src/server/chat/*`.
- **Pages:**
  - `/app`: overview
  - `/app/dashboards/[id]`: filters in the URL, drill-down, export
  - `/app/cards/[id]`
  - `/app/sql`: owner/admin, SELECT-only
  - `/app/upload`: owner/admin, `.xlsx`/`.xls`/`.csv`
- **UI copies:** files with a `POC COPY of apps/web/...` header are copied so that `apps/web` stays untouched. Follow-up: extract them to `packages/ui`.

Setup is in `../../../dima-metabase/README.md`. Commands:

```bash
bun run auth:migrate && bun run seed:users   # once
bun run dev                                  # :3002
bun run test && bun run typecheck && bun run lint
```
