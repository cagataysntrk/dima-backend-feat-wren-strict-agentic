# DIMA DAY 6.5 — M0 SOURCE AUDIT RECEIPT

**Date:** 2026-09-22  
**Phase:** D65-M0  
**Status:** SOURCE AUDIT SUFFICIENT FOR X0 PREPARATION / NO PRODUCT DECISION  
**Dima branch:** `feat/ask-v2-mvp`  
**Entry checkpoint:** `f2b246a7f186705f8ddd98a61e60d950f606d326`

## Source identity

Canonical source:
```text
repo = metabase/metabase
pinned source SHA = 74216b30981d8310c4cf724d63ca282e2e63529d
verified upstream master 2026-09-22 = fff70175e0b5f82dc0eb267593c717c4a6130206
relevant agent/API/MCP family delta = NONE
```

No Metabase source was copied, ported, transliterated or vendored into Dima.

## Exact mechanisms audited

1. Generic agent loop / successful terminal / failed-terminal self-correction
   - `src/metabase/metabot/agent/core.clj`
   - functions: `successful-tool-output?`, `terminal-tool-call?`,
     `should-continue?`, `finish-reason`, `loop-step`.
2. Profiles / budgets / profile-level access
   - `src/metabase/metabot/agent/profiles.clj`
   - `src/metabase/metabot/agent/core.clj` permission/profile initialization.
3. Agent API auth/permissions/reference
   - `src/metabase/agent_api/reference.md`
   - `src/metabase/agent_api/api.clj`
   - `src/metabase/agent_api/validation.clj`.
4. Native-query guards and replay permission revalidation
   - `src/metabase/agent_api/query_guards.clj`.
5. Search / exact resources
   - `src/metabase/mcp/v2/tools/search.clj`
   - `src/metabase/mcp/v2/resources.clj`.
6. Metrics / governed reusable semantic content
   - `src/metabase/mcp/v2/tools/metric.clj`.
7. Construct / validate / repair / resolve / execute
   - Agent API construct/query paths
   - MCP v2 query execution paths.
8. Query handles / visualization
   - `src/metabase/mcp/v2/tools/query.clj`
   - `src/metabase/mcp/v2/tools/visualize.clj`.
9. Questions, dashboard, collections
   - `question.clj`, `dashboard.clj`, `collection.clj`.
10. Exploration/research-plan state
    - `src/metabase/metabot/tools/explorations.clj`.

Detailed evidence and Dima mapping live in
`DIMA_DAY6_5_METABASE_ADOPTION_MATRIX.md §2A–2C`.

## Findings

### F1 — Generic process-control is a pattern, not truth authority

Metabase confirms a useful boundary: generic loop mechanics own iteration/terminal/retry
behavior; profile/tool/domain code owns actual capability. Dima already follows this with
`BoundedAgentRuntimeKernel` and should keep its stricter same-action/same-state NO_PROGRESS guard.

Disposition: **ADOPT_PATTERN_ONLY / ALREADY ADOPTED**.

### F2 — Discovery and exact resource inspection are distinct

Search/retrieval returns ranked candidates. Exact resource inspection is a separate scoped
operation.

Disposition: confirms Dima invariant
`retrieval score != semantic truth`; no new semantic owner.

### F3 — Proposal → validation/repair/resolution → execution is real

Metabase's agent-facing query path accepts an external query proposal and passes it through
server-side representation validation/repair/metadata resolution before execution. Agent-input
errors are surfaced for self-correction.

Disposition: **material X0 candidate**. Compare this execution substrate boundary against
Dima's current `StandardProjection → Planner/Wren`, without moving Dima semantic authority.

### F4 — Raw SQL is a separate privilege boundary

Structured-query paths reject native SQL; native execution has separate scopes/kill switch.
Nested/malformed representations are scanned fail-closed for native markers.

Disposition: **mandatory X0 negative proof**.

### F5 — Query handles are useful provenance, not permanent authorization

Handles represent executed/resolved queries, are user/session scoped and are rechecked on replay.
Holding a handle does not preserve authorization after permission changes.

Disposition: **material X0 proof** for QueryContract/Evidence bindability.

### F6 — Product workspace capabilities are independent of substrate winner

Question/save, dashboards, collections and visualization are useful product patterns, but do not
answer which governed analytics execution substrate should be primary.

Disposition: defer according to roadmap; do not bias X0.

### F7 — Exploration UX does not replace Dima Research truth model

Metabase Research plan tools separate compact model-visible summaries from heavier FE state.
This is useful as a state-channel/UI pattern. It does not provide Dima's USER_MUST / Evidence /
Completion truth contract.

Disposition: **pattern only**.

## Changeable runtime/license verification

Current docs checked 2026-09-22:
- https://www.metabase.com/docs/latest/ai/agent-api
- https://www.metabase.com/license

Recorded implications:
- Agent API is documented as versioned/headless and permission scoped.
- Current auth options include API key, session and JWT.
- API key is group-scoped, not individual-user scoped; X0 must use a representative
  per-user identity path for permission-fidelity evidence.
- JWT is documented as Pro/Enterprise only.
- OSS Metabase is AGPL; Enterprise uses commercial licensing.

These are external/runtime facts, not pinned-source invariants; X0 receipt must re-pin runtime
version/image and chosen auth mode.

## M0 gate result

```text
exact source identity               PASS
core loop/profile source evidence   PASS
query guard source evidence         PASS
construct/execute evidence          PASS
handle/replay evidence              PASS
permission model evidence           PASS
product UX surfaces separated       PASS
source-copy/vendor                  0
product integration                 0
authority boundary change           0

M0 sufficient for X0 preparation    YES
M0 selects Metabase                 NO
M0 authorizes full D65-X            NO
```

## X0 promotion set

Only these mechanisms enter X0:
- authenticated principal continuity;
- optional search/read-resource needed for construction;
- construct-query;
- validation/repair/resolution;
- execute;
- query-handle identity;
- permission revalidation;
- native-SQL separation;
- Dima QueryContract/Evidence binding;
- latency/integration complexity.

Everything else stays out of the substrate winner test.


## Post-audit exact-source reinforcement — 2026-09-22

Additional pinned-source verification at
`metabase/metabase@74216b30981d8310c4cf724d63ca282e2e63529d`:

- `src/metabase/mcp/v2/queries.clj::execute-representations-query` is the shared
  validate → repair → resolve entry point for agent-authored structured queries and attaches
  bounded recovery hints to agent-input failures.
- `queries.clj::resolve-query-handle!` resolves a handle for the current user and then re-runs
  native rejection, serialized-shape validation and current permission checks. A handle is
  execution identity/provenance, not durable authorization.
- `queries.clj::resolve-query-handle-for-save!` deliberately re-checks shape + permissions on
  save and fails closed when bound runtime parameters would be silently lost by persistence.
- `src/metabase/mcp/v2/resolve.clj::resolve-and-read-with` collapses non-existence and unreadable
  existence into the same not-found surface, preventing an ID/resource existence oracle.
- Agent API continuation-token execution revalidates query permissions before later pages; a
  pagination token does not confer persistent authority.

Dima implication:

```text
Metabase query_handle / continuation token
= replay/provenance mechanism
≠ Dima semantic authority
≠ permanent permission grant
```

These findings strengthen the existing X0 P0s:
`permission bypass = 0`, `cross-user handle access = 0`,
`unprovable executed query = 0`.

**Sequencing correction:** M0 remains sufficient for X0 *preparation*, but X0 execution is now
blocked by `D65-SI STANDARD INTEGRATION CLOSURE`. The substrate comparison must consume the
real `AcceptedStandardAuthority → StandardProjection` chain, never the historical Research
surrogate.
