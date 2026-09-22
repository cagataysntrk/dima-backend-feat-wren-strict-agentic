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
| Generic agent loop | `src/metabase/metabot/agent/core.clj` | Dima `BoundedAgentRuntimeKernel` direction already adopted | Compare terminal/retry semantics | M0 | UNDER_AUDIT |
| Agent profiles | `src/metabase/metabot/agent/profiles.clj` | Dima Standard/Research profile/tool boundaries | Compare capability/tool scoping | M0 | UNDER_AUDIT |
| Iteration / budget controls | `core.clj`, `profiles.clj` | bounded budgets/progress in Dima | Compare failure/terminal behavior | M0 | UNDER_AUDIT |
| Successful terminal semantics | `core.clj`, profile terminal tool definitions | Dima terminal outcomes exist | Need exact semantic comparison | M0 | UNDER_AUDIT |
| Failed-terminal self-correction | `core.clj` | Dima bounded repair/no-progress | Need exact comparison | M0 | UNDER_AUDIT |
| Permission/capability-scoped tools | profiles + Agent API/MCP registry surfaces | Dima auth/tenant + governed tools | Need permission/tool-capability mapping | M0 | UNDER_AUDIT |
| Agent API auth/user scope | `src/metabase/agent_api/api.clj`, `reference.md` | Dima explicit principal/tenant execution | Need real integration proof | X0 | TEST_IN_X0 |
| Query guards / native-query separation | `src/metabase/agent_api/query_guards.clj` | Dima raw-SQL prohibition / governed execution | Compare bypass resistance | M0 + X0 | UNDER_AUDIT |
| Agent API validation | `src/metabase/agent_api/validation.clj` | Dima StandardProjection/planner validation | Map semantics | M0 | UNDER_AUDIT |
| Search / retrieve entities | `src/metabase/mcp/v2/tools/search.clj`, resources/registry | Dima SemanticCatalogRetriever | Compare retrieval/resource model | M0 | UNDER_AUDIT |
| Read/resource surfaces | `src/metabase/mcp/v2/resources.clj`, browse/content tools | Dima bounded semantic/context surfaces | Potential reusable API concept | M0 | UNDER_AUDIT |
| Metrics inspection | `src/metabase/mcp/v2/tools/metric.clj` | Dima semantic model metrics | Compare metadata/resource semantics | M0 | UNDER_AUDIT |
| Query construct/resolve | Agent API + `src/metabase/mcp/v2/query.clj`, `queries.clj`, `resolve.clj` | Dima StandardProjection → planner/Wren | Core execution contender | X0 | TEST_IN_X0 |
| Query execute separation | Agent API / MCP query surfaces | Dima official execution boundary | Core execution contender | X0 | TEST_IN_X0 |
| Opaque query / handle semantics | Agent API/MCP query surfaces | Dima QueryContract identity | Important provenance/replay comparison | X0 | TEST_IN_X0 |
| Permission revalidation on execute/replay | Agent API/query guard path | Dima principal-aware execution/replay requirements | Must verify with real user contexts | X0 | TEST_IN_X0 |
| Question/saved query | `src/metabase/mcp/v2/tools/question.clj` | Dima saved analysis/report direction | Product capability candidate | DAY11-15 / POST-MVP | DEFER_PRODUCT_UX |
| Dashboard | `src/metabase/mcp/v2/tools/dashboard.clj` | Dima dashboard/UI roadmap | UX/product pattern, not substrate winner itself | POST-MVP unless backend contract impacts release | DEFER_PRODUCT_UX |
| Collections | `src/metabase/mcp/v2/tools/collection.clj` | Dima persistence/workspace concepts | Product/UX candidate | POST-MVP | DEFER_PRODUCT_UX |
| Visualization | `src/metabase/mcp/v2/tools/visualize.clj` | Dima VizSpec/report/chart pipeline | Compare pattern only unless core contract impact | DAY9-12 / POST-MVP | UNDER_AUDIT |
| Native NLQ / Metabot behavior | metabot agent/profile/prompt surfaces | Dima Standard cognition | Secondary challenger, separate from substrate test | FULL-D65-X secondary | DECISION_PENDING |
| Workspace/exploration UX | MCP tools + Metabot surfaces + product UI | Dima future BI workspace | Independent adoption value | POST-MVP | DEFER_PRODUCT_UX |

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
