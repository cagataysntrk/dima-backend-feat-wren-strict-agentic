# DIMA DAY 6.5 — METABASE ADOPTION MATRIX

**Phase:** D65-M0  
**Status:** SOURCE AUDIT READY / NOT YET A PRODUCT DECISION  
**Canonical repo:** `metabase/metabase`  
**Historical pinned reference:** `74216b30981d8310c4cf724d63ca282e2e63529d`  
**Current upstream master verified 2026-09-22:** `fff70175e0b5f82dc0eb267593c717c4a6130206`

Git comparison: current upstream is one commit ahead of the historical snapshot and no files
under the relevant `src/metabase/metabot/agent`, `src/metabase/agent_api` or
`src/metabase/mcp/v2` families changed between those SHAs.

Source copy / port / transliteration / vendoring into Dima is forbidden.

## 1. Matrix semantics

Each mechanism is classified with:

```text
mechanism
exact source evidence
problem solved
Dima equivalent
already adopted?
gap?
should adopt?
timing = NOW | D65-X0 | FULL-D65-X | DAY7-10 | DAY11-15 | POST-MVP
reason
risk
license/API dependency
status
```

Allowed status during M0:

```text
VERIFIED_SOURCE
UNDER_AUDIT
ADOPT_PATTERN_ONLY
TEST_IN_X0
TEST_IN_FULL_X
DEFER_PRODUCT_UX
NOT_APPLICABLE
DECISION_PENDING
```

M0 itself does not write product code.

## 2. Current adoption matrix

| Mechanism | Exact source evidence | Dima equivalent / current state | Preliminary gap | Candidate timing | Status |
|---|---|---|---|---|---|
| Generic agent loop | `src/metabase/metabot/agent/core.clj` | Dima `BoundedAgentRuntimeKernel` already adopted | Dima has stricter no-progress guard | M0 | ADOPT_PATTERN_ONLY |
| Agent profiles | `src/metabase/metabot/agent/profiles.clj` | Dima Standard/Research profile/tool boundaries | No material architecture gap | M0 | ADOPT_PATTERN_ONLY |
| Iteration / budget controls | `core.clj`, `profiles.clj` | bounded budgets/progress in Dima | No material architecture gap | M0 | VERIFIED_SOURCE |
| Successful terminal semantics | `core.clj`, profile terminal tool definitions | Dima terminal outcomes exist | Per-profile successful-only terminal pattern verified | M0 | VERIFIED_SOURCE |
| Failed-terminal self-correction | `core.clj` | Dima bounded repair/no-progress | Failed terminal call may self-correct; Dima keeps no-progress guard | M0 | VERIFIED_SOURCE |
| Permission/capability-scoped tools | profiles + Agent API/MCP registry surfaces | Dima auth/tenant + governed tools | Real principal mapping remains | X0 | TEST_IN_X0 |
| Agent API auth/user scope | `agent_api/reference.md`, `api.clj` + current Agent API docs | Dima explicit principal/tenant execution | API-key group identity is insufficient for per-user proof | X0 | TEST_IN_X0 |
| Query guards / native-query separation | `src/metabase/agent_api/query_guards.clj` | Dima raw-SQL prohibition / governed execution | Source behavior verified; attack in integration | X0 | TEST_IN_X0 |
| Agent API validation | `src/metabase/agent_api/validation.clj` | Dima feature/runtime gate | API enablement verified; query validation lives deeper | M0 | VERIFIED_SOURCE |
| Search / retrieve entities | `src/metabase/mcp/v2/tools/search.clj`, resources/registry | Dima SemanticCatalogRetriever | Retrieval remains discovery-only | M0 | ADOPT_PATTERN_ONLY |
| Read/resource surfaces | `src/metabase/mcp/v2/resources.clj`, Agent API read-resource | Dima bounded semantic/context surfaces | Useful supported API in thin adapter | X0 | TEST_IN_X0 |
| Metrics inspection | `src/metabase/mcp/v2/tools/metric.clj` | Dima semantic model metrics | Not a replacement for BindingGate | X0 / later | VERIFIED_SOURCE |
| Query construct/resolve | Agent API + representations/resolve pipeline | Dima StandardProjection → planner/Wren | Material execution-substrate contender | X0 | TEST_IN_X0 |
| Query execute separation | Agent API / MCP query surfaces | Dima official execution boundary | Structured/raw SQL boundary source-verified | X0 | TEST_IN_X0 |
| Opaque query / handle semantics | MCP query/visualize surfaces | Dima QueryContract identity | Need receipt binding without authority laundering | X0 | TEST_IN_X0 |
| Permission revalidation on execute/replay | query guards + handle resolution | Dima principal-aware execution/replay requirements | Source verified; real-user proof remains | X0 | TEST_IN_X0 |
| Question/saved query | `src/metabase/mcp/v2/tools/question.clj` | Dima saved analysis/report direction | Product capability candidate | DAY11-15 / POST-MVP | DEFER_PRODUCT_UX |
| Dashboard | `src/metabase/mcp/v2/tools/dashboard.clj` | Dima dashboard/UI roadmap | UX/product pattern, not substrate winner itself | POST-MVP unless backend contract impacts release | DEFER_PRODUCT_UX |
| Collections | `src/metabase/mcp/v2/tools/collection.clj` | Dima persistence/workspace concepts | Product/UX candidate | POST-MVP | DEFER_PRODUCT_UX |
| Visualization | `src/metabase/mcp/v2/tools/visualize.clj` | Dima VizSpec/report/chart pipeline | Handle/UI separation is useful, not substrate criterion | DAY9-12 / POST-MVP | DEFER_PRODUCT_UX |
| Deployment topology / self-hosted service | official Docker/JAR + production app-DB docs | No Dima equivalent; external component if selected | Operational/runtime burden must be measured | X0 | TEST_IN_X0 |
| Horizontal scaling / HA | official Metabase scale docs | Dima service scaling is separate | Need coupled failure/latency/HA assessment | X0 / FULL-D65-X | TEST_IN_X0 |
| Metabase application DB | production docs recommend dedicated PostgreSQL | Dima has its own persistence; Metabase adds separate state DB | Additional backup/migration/ops burden | X0 | TEST_IN_X0 |
| Cloud vs self-host boundary | Metabase Cloud and self-host are distinct products | Dima trust model prefers controlled infra for experiment | Vendor-cloud data boundary must not be assumed | X0 | VERIFIED_SOURCE |
| OSS licensing boundary | Metabase OSS = AGPL | Dima proprietary/product licensing separate | Source copy/fork/embedding requires explicit legal/license review | M0 / decision | DECISION_PENDING |
| Native NLQ / Metabot behavior | `agent/core.clj`, `profiles.clj` | Dima Standard cognition | Multi-turn governed NLQ verified; quality unmeasured | FULL-D65-X secondary | DECISION_PENDING |
| Workspace/exploration UX | explorations + MCP question/dashboard/collection tools | Dima future Research/workspace UI | State-channel patterns useful; not substrate criterion | POST-MVP | DEFER_PRODUCT_UX |

## 3. Mandatory M0 questions

For each row:

1. What exact problem does Metabase solve?
2. Is Dima already solving it?
3. Is Dima re-inventing it unnecessarily?
4. Can we adopt a **pattern or supported API** without weakening Dima authority/trust?
5. Does this affect the release backend architecture before final freeze?
6. If yes, should it be tested in X0/full-X?
7. If not, should it be deferred to Day7–15 or post-MVP?
8. What security/license/experimental-API dependency is introduced?

## 4. D65-X0 promotion candidates

Only mechanisms that materially affect governed analytical execution can promote into X0.

Current candidates for real feasibility:

```text
Agent API user/principal scope
search/read-resource if required
construct-query
query validation/repair/resolution
execute
opaque query/query-handle identity
permission revalidation
native SQL separation
QueryContract bindability
EvidenceArtifact compatibility
latency / integration complexity
```

UI/workspace desirability alone is not a reason to select Metabase as the execution substrate.

## 5. Decision discipline

M0 finding:
```text
source observation
→ Dima comparison
→ gap
→ candidate timing
```

is not automatically:

```text
→ implement
```

STOP and consult before:
- adopting a pattern that changes Dima authority/security,
- starting full D65-X,
- replacing Wren,
- introducing production Metabase dependency.

## 6. Next audit work after approval

Read and extract exact behavior from:
- `metabot/agent/core.clj`
- `metabot/agent/profiles.clj`
- `agent_api/reference.md`
- `agent_api/api.clj`
- `agent_api/query_guards.clj`
- `agent_api/validation.clj`
- MCP v2 registry/resources/query/search/metric/question/dashboard/visualize surfaces

Then fill:
```text
exact behavior
Dima equivalent
gap
adopt?
when?
risk
receipt evidence
```

No source code is copied.


## 2A. Exact-source audit — 2026-09-22

**Audit mode:** pinned source evidence first; changeable runtime/license facts separately
re-verified against current Metabase documentation. This section records source behavior only.
It does **not** authorize D65-X or a production dependency.

Pinned source:
\`metabase/metabase@74216b30981d8310c4cf724d63ca282e2e63529d\`

Current upstream cross-check already recorded:
\`fff70175e0b5f82dc0eb267593c717c4a6130206\`
(one commit ahead; no relevant agent/API/MCP-family delta).

### M0-01 — Generic agent loop / terminal semantics

**Exact source**
- \`src/metabase/metabot/agent/core.clj:169-235\`
  - \`successful-tool-output?\`
  - \`terminal-tool-call?\`
  - \`should-continue?\`
  - \`finish-reason\`
- \`src/metabase/metabot/agent/core.clj:549-632\` — \`loop-step\`

**Exact behavior**
- A successful answer-producing tool exposes \`:structured-output\`.
- A tool is terminal only if its profile declares it terminal **and** that call succeeded.
- Failed terminal-tool calls do not terminate the loop; the next model turn may self-correct.
- Continuation is bounded by \`max-iterations\`, requires a tool call, rejects truncated turns,
  and stops on successful terminal-tool calls.
- Non-retryable terminal tool errors (notably permission denial) terminate explicitly.
- Tool outputs are appended to memory before the next turn.

**Problem solved**
Bounded self-correction without treating every tool failure as fatal or every tool call as
permission to continue indefinitely.

**Dima equivalent**
\`BoundedAgentRuntimeKernel\` + profile-owned terminal semantics + typed observations.

**Gap / reinvention**
The core process-control pattern is already adopted. Dima's extra
\`ActionFingerprint + StateFingerprint → NO_PROGRESS\` guard is stricter than this source and
should be retained.

**Decision**
\`ADOPT_PATTERN_ONLY / ALREADY_ADOPTED\`. Do not copy loop code.

**Security / authority**
No semantic or numeric authority is granted by the loop itself.

**Runtime / license**
Pattern-only reference; no runtime dependency.

### M0-02 — Profiles, tool scoping, budgets

**Exact source**
- \`src/metabase/metabot/agent/profiles.clj:50-105\` — profile registration/validation.
- \`src/metabase/metabot/agent/profiles.clj:108-180\` — NLQ/SQL/document profiles.
- \`src/metabase/metabot/agent/core.clj:451-505\` — profile permission gate and tool resolution.

**Exact behavior**
- Profiles own \`max-iterations\`, tool list, optional required-tool behavior and terminal tools.
- Registration rejects malformed tool metadata, duplicate tool names and terminal tools not
  exposed by the profile.
- \`:nlq\` uses a 15-iteration budget and a bounded discovery/read/construct/chart/save tool set.
- \`:sql\` uses a distinct 20-iteration profile, required-tool-call behavior and explicit
  successful terminal tools.
- Profile access is permission-gated before the loop starts.

**Problem solved**
Separates generic loop mechanics from domain/tool capabilities and user permissions.

**Dima equivalent**
Generic \`BoundedAgentRuntimeKernel\` + Standard/Research profile ownership.

**Gap / reinvention**
No material loop/profile gap found. Dima should keep domain truth outside the generic kernel.

**Decision**
\`ADOPT_PATTERN_ONLY / ALREADY_ADOPTED\`.

### M0-03 — Permission-scoped tools and resources

**Exact source**
- \`src/metabase/mcp/v2/resources.clj:31-96\`
- individual tools carry \`:scope\` metadata, e.g. query/visualization/content-write tools.
- \`src/metabase/metabot/agent/core.clj:451-468\` profile-level permission gate.

**Exact behavior**
- Resources are registered with explicit scopes.
- Data resources are read only when token scopes satisfy the resource scope.
- UI shell resources contain no data; scoped credentials are only handed to authorized callers.
- Tool/profile permission is enforced independently from LLM reasoning.

**Problem solved**
Capability visibility and data access are governed by runtime identity rather than model choice.

**Dima equivalent**
tenant/principal runtime + governed tool registry + RLS/CLS boundary.

**Gap / reinvention**
X0 must prove that Dima's representative principal maps to equivalent Metabase permissions;
a generic API key is not sufficient evidence for per-user fidelity.

**Decision**
\`TEST_IN_X0\` for actual identity mapping; pattern already adopted.

### M0-04 — Agent API authentication / principal semantics

**Pinned source**
- \`src/metabase/agent_api/reference.md\` — authenticated-user-scoped Agent API contract.

**Current external verification — 2026-09-22**
- \`https://www.metabase.com/docs/latest/ai/agent-api\`
- Agent API is documented as versioned and scoped to authenticated permissions.
- Current docs support API key, session token and JWT.
- API-key permissions belong to the key's assigned group, **not an individual user**.
- Session auth is user-scoped.
- JWT auth is documented as Pro/Enterprise only.

**Problem solved**
Headless agent execution over a stable supported API with runtime permissions.

**Dima equivalent**
Explicit principal/tenant analytics runtime.

**Gap**
For X0, use a representative user/session or JWT configuration that preserves per-user semantics.
Do not claim permission fidelity from a group-scoped API key.

**Decision**
\`TEST_IN_X0\`.

**Security impact**
Principal continuity is a P0. Authentication convenience cannot weaken Dima's per-user authority.

### M0-05 — Search / retrieval is discovery, not truth

**Exact source**
- \`src/metabase/mcp/v2/tools/search.clj:250+\` — filter validation, narrowing disclosure,
  permission-aware search.
- \`src/metabase/agent_api/reference.md\` — \`POST /v1/search\`.
- NLQ profile uses retrieve/search + read-resource before query construction.

**Exact behavior**
- Search supports term and semantic queries; multiple query results are merged/ranked.
- Invalid filter/type combinations become teaching errors; implicit narrowing is disclosed instead
  of silently changing meaning.
- Permission filtering occurs at the resource/content boundary.
- Search returns candidates; exact resource reading is a separate operation.

**Problem solved**
Efficient discovery over large catalogs without treating ranking as semantic truth.

**Dima equivalent**
\`SemanticCatalogRetriever\` candidate discovery + \`SemanticBindingGate\` authority.

**Gap / reinvention**
No Day6.5 architecture gap. Future backend quality/indexing can improve independently.

**Decision**
\`ADOPT_PATTERN_ONLY / ALREADY_ADOPTED\`.
Permanent invariant: \`retrieval score != semantic truth\`.

### M0-06 — Read-resource / exact resource inspection

**Exact source**
- \`src/metabase/agent_api/reference.md\` — \`POST /v1/read-resource\`.
- \`src/metabase/mcp/v2/resources.clj\` — resource registry/scope.
- MCP v2 read/resource surfaces.

**Exact behavior**
- One unified resource surface drills into databases, collections, tables, models, questions,
  metrics and dashboards.
- Per-resource permission checks are performed; unreadable list entries are filtered.
- Resource inspection is distinct from ranked search.

**Problem solved**
Lets an agent verify exact metadata after approximate discovery.

**Dima equivalent**
LLM-safe candidate cards + catalog binding metadata; no separate heavyweight hydrator is required.

**Gap**
X0 may use Metabase's supported read-resource API as part of a thin adapter if exact construct
needs metadata.

**Decision**
\`TEST_IN_X0\` as API capability; no source adoption.

### M0-07 — Metric/entity inspection

**Exact source**
- \`src/metabase/mcp/v2/tools/metric.clj:82-120\` query-source and metric-shape gates.
- \`src/metabase/mcp/v2/tools/metric.clj:140-210\` shared save/check stack.
- \`src/metabase/agent_api/reference.md\` metric dimensions/resource contract.

**Exact behavior**
- Metric writes resolve inline definition or an existing query handle.
- Query handles are rechecked on resolution.
- Native SQL is rejected as a metric definition.
- A metric must satisfy a constrained saveable shape.
- Shared card permission/persistence checks are reused rather than reimplemented.

**Problem solved**
Reusable governed semantic metrics with explicit shape and permission guarantees.

**Dima equivalent**
MDL/catalog metric definitions + governed semantic handles.

**Gap**
Not required to replace Dima semantic authority. Useful as an execution/workspace resource if
Metabase becomes substrate or BI workspace.

**Decision**
\`DEFER_PRODUCT_UX\` for authoring; resource inspection may participate in X0.

### M0-08 — Query construction / validation / repair / resolution

**Exact source**
- \`src/metabase/agent_api/reference.md\` — \`POST /v2/construct-query\`.
- Agent API construct path calls the representations pipeline.
- \`src/metabase/agent_api/api.clj\` \`evaluate-external-query-to-live-query\`.
- construct tool/pipeline reports agent-facing input errors such as unknown database/table/field,
  ambiguous FK and no-FK-path.

**Exact behavior**
\`\`\`text
external query proposal
→ validate
→ convert/repair
→ metadata-backed resolve
→ permission-aware live query
→ serialized executable query
\`\`\`
Input failures are surfaced as typed/user-facing 4xx/teaching feedback so the agent can correct
its proposal.

**Problem solved**
LLM may propose a query representation without becoming canonical query truth.

**Dima equivalent**
\`StandardProjection → Planner → Wren dry-plan/query\` with typed validation feedback.

**Gap / reinvention**
This is the most material X0 candidate. Need to measure whether Metabase can consume a thin,
engine-independent Dima projection without duplicating semantic authority.

**Decision**
\`TEST_IN_X0\`.

### M0-09 — Structured execute separated from raw SQL

**Exact source**
- \`src/metabase/mcp/v2/tools/query.clj\`
  - \`resolve-input\`
  - \`execute!\`
  - \`execute-query\`
  - separate \`execute_sql\` gates.
- \`src/metabase/agent_api/query_guards.clj\` native-query guards.

**Exact behavior**
- Fresh structured query runs validate/repair/resolve before execution.
- Stored handle/cursor re-resolves through guard paths.
- Structured execute rejects native SQL at any depth.
- Raw SQL is a separate tool/path with separate scope and instance kill switch.
- Caller-controlled query metadata is whitelisted before Query Processor execution.

**Problem solved**
Prevents a structured-query capability from becoming a raw-SQL bypass.

**Dima equivalent**
Manager raw-SQL prohibition + official execution boundary + Wren guard/security.

**Gap**
X0 must prove no adapter shortcut bypasses Dima's raw-SQL prohibition.

**Decision**
\`TEST_IN_X0\`, P0.

### M0-10 — Native-SQL fail-closed guards

**Exact source**
- \`src/metabase/agent_api/query_guards.clj:80-260\`
  - \`native-query?\`
  - \`reject-native-query!\`
  - \`validate-serialized-query!\`
  - \`check-mcp-ui-native-query!\`

**Exact behavior**
- Native detection raw-scans structural nested query edges instead of normalize-then-inspect.
- Malformed structures are deep-scanned so a buried native marker cannot pass because
  normalization failed.
- MBQL-scoped execution rejects native SQL.
- MCP UI native execution requires explicit SQL scope and an enabled kill switch.

**Problem solved**
Fail-closed prevention of SQL smuggling across a lower-privilege structured-query boundary.

**Dima equivalent**
SQL guard + official governed execution boundary.

**Gap**
No architecture gap. X0 should attack this boundary with negative tests.

**Decision**
\`TEST_IN_X0\` security proof; pattern strongly endorsed.

### M0-11 — Query handles / opaque execution identity

**Exact source**
- \`src/metabase/mcp/v2/tools/query.clj\` resolve/mint-handle paths.
- \`src/metabase/mcp/v2/tools/visualize.clj:30-81\`.
- \`src/metabase/agent_api/reference.md\` opaque construct/execute contract.

**Exact behavior**
- Execution mints opaque handles for the resolved query that actually ran.
- Handle/cursor resolution is user/session scoped.
- A handle can be reused for save/visualize without asking the model to reconstruct the query.
- Visualization prefers an existing query handle.

**Problem solved**
Separates stable execution identity from model context and enables replay/presentation.

**Dima equivalent**
\`QueryContract\` / Evidence identity.

**Gap**
Need X0 proof that a Metabase handle can be bound into Dima receipt provenance without making
the handle itself Dima authority.

**Decision**
\`TEST_IN_X0\`.

### M0-12 — Permission revalidation on replay

**Exact source**
- \`src/metabase/agent_api/query_guards.clj:250+\` — \`check-token-query-permissions!\`.
- \`src/metabase/mcp/v2/tools/query.clj\` handle/cursor \`resolve-input\`.
- save/metric tools resolve handles through guarded save paths.

**Exact behavior**
- Current user's permissions are revalidated for stored/client-supplied queries.
- Stage-0 explicit check provides early 403; Query Processor permission middleware remains the
  authoritative execution backstop.
- Holding a stored handle is not treated as permanent authorization.

**Problem solved**
Prevents stale authority after user permissions change.

**Dima equivalent**
principal-aware execution/replay requirement.

**Gap**
This is a mandatory X0 acceptance condition.

**Decision**
\`TEST_IN_X0\`, P0.

### M0-13 — Visualization keeps row data out of model context

**Exact source**
- \`src/metabase/mcp/v2/tools/visualize.clj:1-120\`.
- \`src/metabase/mcp/v2/resources.clj:79-121\`.

**Exact behavior**
- Visualization returns a query handle + scoped UI resource.
- Result rows are fetched by the UI surface rather than injected into model context.
- Existing handle is reused; fresh query is validated/resolved first.
- Handle lookup is user-scoped.

**Problem solved**
Interactive BI rendering without spending model context on entire result sets.

**Dima equivalent**
VizSpec / report UI + evidence/result references.

**Gap**
Useful product/UX pattern, not an execution-substrate selection criterion by itself.

**Decision**
\`DEFER_PRODUCT_UX\` / revisit Day9–12 or post-MVP.

### M0-14 — Saved question / reusable content

**Exact source**
- \`src/metabase/mcp/v2/tools/question.clj:152-210\` — query source resolution/gates.
- \`src/metabase/mcp/v2/tools/question.clj:331-467\` — dashboard/collection/write permission checks.
- \`src/metabase/mcp/v2/tools/question.clj:550+\` — \`question_write\`.

**Exact behavior**
- Save consumes query handle, inline MBQL or separately-gated native SQL.
- Native save re-spends SQL scope/kill-switch; possession of a handle is not sufficient.
- Dashboard/collection reads and writes are permission checked.
- Shared REST card save checks/cycle checks are reused.

**Problem solved**
Turns governed query artifacts into reusable BI content without rebuilding permissions.

**Dima equivalent**
saved analyses/report/dashboard roadmap.

**Decision**
\`DEFER_PRODUCT_UX\` / Day11–15 candidate. Not X0 winner criterion except receipt compatibility.

### M0-15 — Dashboards

**Exact source**
- \`src/metabase/mcp/v2/tools/dashboard.clj:40-123\` read/permission/validation.
- \`src/metabase/mcp/v2/tools/dashboard.clj:428-518\` compile/save/\`dashboard_write\`.

**Exact behavior**
- Ordered dashboard ops are compiled and validated.
- Update ops are applied as one save.
- \`validate_only\` can compile without writing.
- Referenced cards require read permission; dashboard writes require write permission.
- Source explicitly documents a create-path caveat: real permission/save failure can still occur
  after initial validation.

**Problem solved**
Agent-editable persistent BI workspace with server-side validation.

**Dima equivalent**
future dashboard/workspace roadmap.

**Decision**
\`DEFER_PRODUCT_UX\`. Do not let dashboard desirability select the execution substrate.

### M0-16 — Collections / workspace hierarchy

**Exact source**
- \`src/metabase/mcp/v2/tools/collection.clj:72-112\` resolve/update permission behavior.
- \`src/metabase/mcp/v2/tools/collection.clj:155+\` — \`collection_write\`.

**Exact behavior**
- Existing collection resolution happens behind read checks.
- “Missing” and “exists but unreadable” collapse to avoid existence leakage.
- Parent/write and authority-level constraints are delegated to domain functions.
- Tool returns readback of the resulting collection.

**Problem solved**
Permission-aware organization of persistent BI artifacts.

**Dima equivalent**
future collections/workspace/persistence organization.

**Decision**
\`DEFER_PRODUCT_UX\`.

### M0-17 — Explorations / research-plan tooling

**Exact source**
- \`src/metabase/metabot/tools/explorations.clj:1-80\` research-plan context injection.
- \`list_research_metrics\`, \`get_research_candidates\`, \`add_research_groups\`,
  \`remove_from_research_plan\`, \`set_research_name\`, \`select_research_timelines\`.

**Exact behavior**
- Research plan is explicit mutable product/UI state supplied back to the agent each turn.
- Read and write tool scopes are distinct.
- Candidate metric/dimension ids must come from governed discovery tools.
- Large picker hydration is intentionally kept out of LLM context while a compact summary is
  returned to the model.

**Problem solved**
Bounded, inspectable research-plan construction without stuffing all artifact state into model
context.

**Dima equivalent**
\`UserObligationLedger + ResearchDirective + ResearchState\`.

**Gap / reinvention**
Dima's research correctness model is stricter because USER_MUST/evidence/completion truth are
explicit. Do not replace it with Metabase Exploration semantics.

**Decision**
\`ADOPT_PATTERN_ONLY\`: UI/state-channel separation is useful; Research authority remains Dima-owned.

### M0-18 — Native NLQ / Metabot

**Exact source**
- \`src/metabase/metabot/agent/profiles.clj\` \`:nlq\` / \`:nlq-fallback\`.
- \`src/metabase/metabot/agent/core.clj\` bounded loop.
- NLQ profile discovery → read → construct → chart/save tool surface.

**Exact behavior**
NLQ is a bounded multi-turn tool-using agent, not a guaranteed one-shot parser. Discovery tool
may vary with index health; query construction still flows through governed server validation.

**Problem solved**
Natural-language BI over a semantic/query platform.

**Dima equivalent**
Standard cognition / StandardBuilder.

**Gap**
Potential secondary benchmark only. NLQ quality is not the same question as execution substrate
quality and must not contaminate X0.

**Decision**
\`DECISION_PENDING\` for a later secondary full-D65-X comparison if full-X is explicitly opened.

### M0-19 — Runtime/API/license dependency chain

**Pinned source fact**
D65-X would integrate through a separate Metabase service and supported Agent API; source copy,
port, transliteration and vendoring are forbidden.

**Current external verification — 2026-09-22**
- Agent API docs: \`https://www.metabase.com/docs/latest/ai/agent-api\`
  - versioned headless agent API;
  - requests respect authenticated permissions;
  - API key, session and JWT auth are documented;
  - JWT is Pro/Enterprise only;
  - API-key identity is group-scoped, not individual-user scoped.
- License: \`https://www.metabase.com/license\`
  - Open Source Edition is AGPL;
  - Enterprise Edition uses Metabase Commercial Software License.

**Implication**
A separate-service integration still creates an operational/API/runtime dependency.
Any production choice must separately review:
- edition/features needed by the chosen auth/API path,
- deployment/runtime image pin,
- upgrade policy,
- license obligations,
- principal mapping,
- external API stability.

**Decision**
No production dependency in M0. X0 receipt must pin
\`source_reference_sha + runtime_version + immutable image digest + Dima SHA + adapter SHA +
permission context\`.

## 2B. M0 preliminary adoption classification

| Mechanism | Source status | Dima disposition | Timing |
|---|---|---|---|
| generic agent loop | VERIFIED_SOURCE | pattern already adopted; keep stricter no-progress guard | NOW / no code |
| profiles + budgets | VERIFIED_SOURCE | pattern already adopted | NOW / no code |
| terminal/retry semantics | VERIFIED_SOURCE | compare semantics; no source copy | NOW |
| profile/tool permissions | VERIFIED_SOURCE | preserve Dima runtime identity; prove mapping | X0 |
| search/retrieval | VERIFIED_SOURCE | candidate discovery only | already adopted |
| resource inspection | VERIFIED_SOURCE | supported API candidate | X0 |
| construct/validate/repair/resolve | VERIFIED_SOURCE | execution-substrate challenger | X0 |
| structured execute | VERIFIED_SOURCE | execution-substrate challenger | X0 |
| native-SQL guards | VERIFIED_SOURCE | mandatory negative proof | X0 |
| query handles | VERIFIED_SOURCE | bind as provenance, never Dima authority | X0 |
| permission revalidation | VERIFIED_SOURCE | mandatory P0 proof | X0 |
| metrics | VERIFIED_SOURCE | optional semantic/workspace resource | X0 / later |
| explorations | VERIFIED_SOURCE | UI/state pattern only; Dima Research truth stays | DAY7-10 / later |
| questions/save | VERIFIED_SOURCE | useful workspace feature | DAY11-15 / post-MVP |
| visualization | VERIFIED_SOURCE | useful UI pattern | DAY9-12 / post-MVP |
| dashboards | VERIFIED_SOURCE | useful workspace feature | post-MVP unless roadmap pulls earlier |
| collections | VERIFIED_SOURCE | useful workspace feature | post-MVP |
| native NLQ/Metabot | VERIFIED_SOURCE | secondary challenger, not X0 substrate criterion | full-X secondary |
| licensing/runtime | CURRENT_EXTERNAL_VERIFIED | production choice needs explicit dependency review | X0/full-X |

## 2C. M0 conclusion so far

M0 already supports a bounded X0 question without deciding the winner:

> Can a separate, permission-faithful Metabase Agent API service execute 5–10 representative
> Dima \`StandardProjection\` cases through construct/validate/execute and return a provenance
> receipt that Dima can bind to \`AcceptedStandardAuthority\` / \`QueryContract\` / Evidence
> without creating a second semantic or numeric authority?

What M0 does **not** currently support:
- replacing Dima Research Manager with Metabot;
- replacing \`SemanticBindingGate\`;
- choosing Metabase because dashboards/collections are attractive;
- running Metabase and Wren as equal production truth engines;
- source copy/port/vendor;
- starting full D65-X without an X0 result and consultation.


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


## 7. Deployment topology authority

Detailed engineering decision record:
`DIMA_DAY6_5_METABASE_DEPLOYMENT_TOPOLOGY_DECISION.md`.

Current X0 default:
```text
self-hosted pinned Metabase runtime
private service network
Agent API
no vendor Cloud dependency
```

This is an experiment topology, not a production selection.

Production selection must measure:
- extra JVM/service footprint,
- application PostgreSQL,
- upgrade/migration/backup,
- monitoring,
- horizontal scaling,
- tenant/principal mapping,
- QueryContract/Evidence compatibility,
- failure blast radius,
- licensing/commercial implications.

Direct source copy/port/vendor remains forbidden.


---

## WREN_SEMANTIC_BACKBONE_RETENTION_DECISION

> **D65-X0 Wren'in MDL/cube semantic backbone'unu kaldırma deneyi değildir. İlk aşamada yalnız
> analytics execution/query-lifecycle overlap'ını ölçer. Wren semantic-layer retention ayrı bir
> architecture decision'dır.**

Binding implications:

```text
X0 MAY compare:
  StandardProjection → Wren execution/query lifecycle
  vs
  StandardProjection → Metabase construct/validate/execute lifecycle

X0 MAY NOT infer:
  "Metabase query execution works"
  ⇒ "Wren MDL/cube semantic backbone is redundant"
```

During X0:
- current Dima semantic authority remains `SemanticBindingGate + accepted authority`;
- existing Wren MDL/cube semantics may remain the semantic backbone even if Metabase is tested as
  an execution/query-lifecycle component;
- metric meaning, cube relationships, grain/additivity/unit/time semantics are not silently
  re-owned by Metabase;
- removing or replacing the Wren semantic layer requires a separate explicit architecture
  decision and consultation, with its own semantic-equivalence and migration evidence.

Therefore a promising X0 can justify a **full execution-substrate/query-lifecycle comparison**,
not automatic Wren semantic-layer removal.
