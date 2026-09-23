# P12X-C2 — DIMA ENGINE BRIDGE PRE-DEVELOPMENT REVIEW

**Milestone:** P12X-C2  
**Branch:** `feat/dima-metabase-platform`  
**Engine submodule:** `engine/metabase`  
**Current pinned engine:** `c56b71ab23bf2a2d266bac2fba8d165ac059d613`  
**Upstream native base:** `v0.63.18 / 2ba2485c78d7e00a9a25f82c00fc201da71590c4`

Status: **CLOSED GREEN / C2 CERTIFIED / DMP-DEC-0034**

## 1. Goal

Create the stable Dima Engine Bridge without reimplementing native Metabot cognition.

The bridge owns:
- exact engine identity;
- authenticated transport identity;
- Dima request/correlation/trace identity;
- native request delegation;
- native stream observation;
- typed terminal/result capture;
- safe telemetry.

It does **not** own:
- analytical planning;
- Metabot profiles;
- skills;
- tool registry;
- query construction/repair;
- native memory/state;
- MBQL;
- Query Processor;
- business semantic truth;
- execution authorization truth;
- QueryReceipt/Evidence promotion.

## 2. Native seam evidence

Pinned Metabase source shows:
- `POST /api/metabot/agent-streaming` delegates to `metabase.metabot.agent.core/run-agent-loop`;
- the native endpoint owns conversation persistence, profile resolution, permission checks, native
  state, tool loop, streaming protocol and terminal state;
- `run-agent-loop` resolves current-user Metabot permissions and scopes internally;
- Dima must not duplicate that orchestration.

Therefore the first C2 bridge must delegate to the existing native endpoint instead of adding a
second agent runtime inside the fork.

## 3. Initial bridge location

Initial C2 implementation owner after C1 GREEN:

```text
backend/app/v3/substrate/metabase/native_engine.py
backend/app/v3/substrate/metabase/native_models.py
backend/tests/test_v3_p12x_c2_native_engine_bridge.py
.github/workflows/dima-metabase-p12x-c2.yml
```

No engine source modification is authorized for the first bridge attempt.

Rationale:
- Platform already owns authenticated Metabase transport boundaries;
- the fork is the runtime/substrate;
- a typed Platform bridge can preserve native engine behavior with zero upstream-source patch;
- only if a measured C2 gap cannot be solved outside the engine may a minimal engine hook be proposed.

## 4. Stable request contract

The bridge request must contain explicit typed fields only:

```text
engine_identity
session_token supplied by caller
profile_id
metabot_id?
message
context
conversation_id
history?
state?
dima_request_id
dima_trace_id
```

Rules:
- no raw SQL field;
- no Dima semantic handle resolution in the bridge;
- no display-name guessing;
- no fallback to Agent API;
- no fallback to Wren;
- no admin analytical execution;
- no silent provider/model substitution.

`conversation_id` remains the native Metabot conversation identity.
`dima_request_id` and `dima_trace_id` are Dima-side correlation identities and are not treated as
Metabase semantic authority.

## 5. Stable response/observation contract

The bridge must preserve the native AI-SDK stream losslessly enough to reconstruct:
- text parts;
- data parts;
- generated entity/query parts;
- tool calls;
- tool results;
- stream/provider errors;
- finish parts;
- final native state;
- observable usage/model identity when emitted;
- HTTP status;
- latency;
- exact engine identity.

The bridge may provide parsed typed views, but must retain the raw ordered stream events for audit.

## 6. Engine identity

C2 may not use a moving `main` ref as runtime identity.

Required:
```text
engine repository
Platform gitlink SHA
runtime version/tag
runtime image digest OR exact source-build identity
upstream base SHA
```

A bridge invocation whose configured engine identity does not match observed runtime identity fails
closed before being certified.

## 7. Permission/security ownership

Native Metabot keeps current-user permission enforcement.

Dima security truth remains separate:
- the bridge authenticates with the caller-provided current-user session;
- it does not mint/upgrade privileges;
- it does not create a second access fingerprint;
- P10 `ExecutionAccessSnapshot` remains the sole durable execution-access identity when later P13
  execution becomes official.

C2 only proves bridge/native equivalence; it does not close `DMP-P5-BLOCK-001`.

## 8. C2 parity proof

Minimum high-information proof after C1 GREEN:

```text
direct native call
vs
Dima Engine Bridge call
```

Hold constant:
- exact engine SHA/image;
- Boyahane snapshot;
- restricted principal;
- Luna provider/model;
- profile;
- question;
- conversation state initial conditions.

Cases:
- PX-01 simple count;
- PX-07 entity/value filter;
- PX-13 grain trap;
- PX-16 semantic ratio.

Closure:
- every direct-native PASS is retained by bridge;
- new silent wrong = 0;
- permission difference = 0;
- dataset-scope drift = 0;
- native stream event loss that changes terminal/result interpretation = 0;
- no extra analytical LLM call introduced by bridge;
- no extra query construction layer introduced by bridge.

Material stochastic divergence is repeated only for the divergent case twice per side.

## 9. Fork hook escalation gate

Engine-source hook is **not authorized** initially.

A minimal hook may be proposed only if provider-free/live evidence proves one of these cannot be
faithfully established externally:
- exact engine revision attestation;
- correlation propagation required inside native logs/stream;
- material trust transition interception;
- lossless native terminal observation.

Even then:
- one new Dima-owned namespace is preferred;
- one minimal upstream route-registration patch maximum for first hook;
- `run-agent-loop`, profiles, skills, memory, tools and query construction remain untouched.

## 10. P13 relationship

P13 remains paused.

C2 does not implement:
- `standard_execution.py`;
- `execute_prepared()`;
- production Standard routing;
- QueryReceipt issuance from native agent output;
- Evidence promotion;
- Wren retirement.

C2 only establishes a stable, auditable bridge to the native engine.

## 11. Stop gate

```text
P12X-C1 = SEALED GREEN
→ C2 PRODUCT CODE = AUTHORIZED
```

After C1 closure, re-read current HEAD, engine gitlink and this document before implementation.


## C2 closure evidence

```text
workflow                         = 35839639339 = SUCCESS
artifact                         = 10742000058
artifact digest                  = sha256:c799261cd36499c7579bdf1d6f97ecc07ce0cfaab782afe861deef169d877d94
four-case final parity           = GREEN
reproducible bridge regression   = 0
new reproducible silent wrong    = 0
permission regression            = 0
dataset-scope drift              = 0
transport contract failures      = 0
```

No engine runtime-source hook was required for C2.
