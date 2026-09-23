# FT-005N — NATIVE METABOT CAPABILITY RETENTION CONTROL PRE-DEVELOPMENT REVIEW

Status: APPROVED / FROZEN BEFORE IMPLEMENTATION
Date: 2026-09-23
Branch: `feat/dima-metabase-product-fast-track`
Entry HEAD: `30659f7892ce2d4eafffec89716b75e2ce09ea48`

## 1. Decision question

FT-005N answers one question only:

> Under the same Metabase version, same source database, same user/permissions and, where causally possible, the same model/provider, does analytical capability that works through Metabase's native agent loop degrade when routed through Fast's Agent-API-based custom cognition/orchestration seam?

This is an architecture experiment, not a production migration.

## 2. Why this sub-gate exists

Pinned Metabase v0.63.18 contains two relevant layers:

```text
shared/native analytics primitives
search / resources / construct / execution
```

and:

```text
native Metabot orchestration
profile prompt
+ skills
+ iterative agent loop
+ state/memory
+ tool repair
+ contextual history
```

The customer-facing Agent API reuses native Metabot search/construct/resources implementations.

Therefore the leading hypothesis is:

```text
primitive capability loss     = likely small
orchestration capability loss = potentially material
```

FT-005N measures this instead of adding another Fast-side algorithm.

## 3. Existing Fast product value is preserved

Out of scope for replacement during this spike:

```text
Dima-native UI
Dima renderer
Fast run lifecycle
SSE normalization
cancel/retry
conversation identity
turn lineage
owner isolation
evidence model
Fast security boundary
browser product shell
```

Only the analytics/cognition substrate is under comparison.

## 4. Read-only references

```text
cagataysntrk/metabase-boyahane
metabase/metabase@v0.63.18
feat/ask-v2-mvp
```

Forbidden:
- import from `app.v2`;
- merge/cherry-pick/sync source branches;
- write to Boyahane main;
- write to ask-v2;
- patch Metabase licensing or paid gates.

## 5. Controls

### A0 — OBSERVED VANILLA

Current user's working Boyahane environment.

Repository control:
- repo HEAD: `f0c4a6b053ead52ca2eac80002c448323dc34a35`;
- configured image ref: `metabase/metabase:latest`;
- data: 80 tables / 462,962 rows.

A0 must capture, without mutation:
- configured image ref;
- running local image ID;
- RepoDigest;
- Metabase version;
- Metabase application DB state identity/digest where safely obtainable;
- configured LLM provider;
- configured exact model;
- AI/Metabot enable state.

Never capture API key values.

A0 is behavioral evidence, not causal architecture evidence.

### A1 — PINNED VANILLA

Separate isolated control:
- exact Metabase runtime: `v0.63.18`;
- exact image digest:
  `sha256:1160b570cb11c107bce00e71293552df8a8363e01a32c2c7a048cee002dc8a73`;
- same Boyahane source DB;
- same relevant metadata/config;
- same principal/permission shape where possible.

A1 does not alter A0 or Boyahane main compose.

### B — DIRECT NATIVE METABOT ENDPOINT

Stock endpoint:
`POST /api/metabot/agent-streaming`

Initial profile:
`nlq`

Minimal request:

```json
{
  "profile_id": "nlq",
  "message": "...",
  "context": {},
  "conversation_id": "<uuid>",
  "history": [],
  "state": {}
}
```

For follow-ups:
- same conversation_id;
- carry forward native returned history;
- carry forward native returned state;
- do not invent new native memory semantics.

### C — CURRENT FAST

Current production candidate unchanged:

```text
User
-> Fast conversation cognition
-> Fast authority
-> Fast Gateway
-> Agent API
-> Metabase
```

No benchmark-driven Fast code modification during the control run.

## 6. Native profile policy

First lane:
`profile_id = nlq`

It is closest to the product question:
natural-language analytics -> discover -> read -> construct -> chart.

Second lane, only after NLQ evidence:
`profile_id = internal`

Use only for broader analysis/research-like cases.

Never combine profile scores.

## 7. Stock capability and license rule

Absolute:

```text
ENTERPRISE_GATE_BYPASS = 0
LICENSE_CHECK_PATCH = 0
PAID_FEATURE_PATCH = 0
```

Possible outcomes:

```text
NATIVE_ENDPOINT_AVAILABLE
NATIVE_ENDPOINT_NOT_AVAILABLE_IN_THIS_STOCK_CONFIG
```

A permission/license block is evidence; it is not authorization to patch the block.

## 8. No fork yet

Disposable Metabase source fork is forbidden in phase 1.

Fork may be proposed only if:
1. direct stock native endpoint materially wins;
2. stock endpoint lacks one required safe integration primitive.

Fork objective, if ever approved:
`thin Dima integration seam`

Never:
- Metabase frontend replacement;
- paid capability unlock;
- new analytics engine.

## 9. Frozen core corpus

FT005N core V1:

```text
Q1: Son 30 günde sipariş tutarı ne kadar?
Q2: Peki geçen ay?
Q3: Bölgelere göre?
```

Synthetic Fast fixture oracle remains:

```text
Q1 = 16270
Q2 = 21994
Q3:
East  = 5523
North = 5425
South = 5474
West  = 5572
```

Boyahane exact oracle is computed independently per selected Boyahane cases.

## 10. Extended seam corpus

Freeze before results as:
`FT005N_SEAM_CORPUS_V1`

Families:
- Turkish question -> English schema;
- ambiguous entity;
- previous period;
- breakdown follow-up;
- "aynı analizi bölgeye göre yap";
- "başka ne dikkat çekiyor?";
- self-contained topic switch;
- existing chart analysis;
- existing saved question/metric reuse;
- query error -> repair;
- contradictory follow-up;
- previous result challenge.

If an arm naturally cannot represent a capability:
`SAFE_UNSUPPORTED`
is a valid outcome.

## 11. Fairness

For causal A1/B/C:
- same Metabase version;
- same app metadata where possible;
- same source database;
- same user/permissions;
- same field/table metadata;
- same exact model/provider where possible.

Normative model order:
1. Luna default/economic baseline;
2. Sol capability ceiling.

A0 may use a different already-working model; if so its result is labeled:
`BEHAVIORAL_CONTROL_SIGNAL`
not architecture-causal evidence.

## 12. Trace contract

Per case:

```text
case_id
arm
Metabase version
Metabase image digest
profile_id
model provider
exact model
input question
conversation_id
input state digest
input history count
tool sequence
search terms
resources considered
resource selected
query construction actions
query repair attempts
execution count
chart/analyze actions
iteration count
final state digest
final answer
numeric result
DB oracle
latency
error class
```

Do not store private reasoning / chain-of-thought.

Allowed trace:
- system profile identity;
- available tool names;
- skill IDs;
- structured tool calls;
- structured tool results;
- state/history digests;
- final result.

## 13. Outcome taxonomy

```text
CORRECT_SUPPORTED
SAFE_CLARIFICATION
SAFE_UNSUPPORTED
WRONG_VISIBLE
SILENT_WRONG
PROVIDER_FAILURE
PERMISSION_BLOCKED
HARNESS_FAILURE
```

Cross-arm families:
- NATIVE_PASS_FAST_FAIL;
- FAST_PASS_NATIVE_FAIL;
- BOTH_PASS;
- BOTH_FAIL.

## 14. Capability-retention metric

Top-level:
`VANILLA_CAPABILITY_RETENTION`

Definition:
Fast hard-pass ratio over cases where pinned native Metabot hard-passes.

Mandatory breakdown:
- retrieval retention;
- follow-up retention;
- temporal retention;
- breakdown retention;
- repair retention;
- chart-context retention.

Do not collapse architecture decision into one score.

## 15. Decision table

A0 good + A1 bad:
`VERSION / CONFIGURATION DRIFT`
No Fast-seam conclusion.

A1/B good + C bad:
`INTEGRATION_SEAM_CAPABILITY_LOSS`
Stop prompt/algorithm patching; cluster native-vs-Fast differences.

A good + B bad:
direct harness may be missing UI-carried context/history/state/profile.
Fix harness parity before judging endpoint.

B approximately C:
native loop is not materially rescuing the relevant capability.
Return to FT-005 certification.

B materially greater than C:
stop expanding custom Fast cognition/orchestration.
Open architecture-pivot receipt.

## 16. If native wins

First architecture to test:

```text
Dima UI
-> Dima Conversation / Run Lifecycle
-> server-side NativeMetabotGateway
-> stock /api/metabot/agent-streaming
-> Metabase native agent loop
-> Metabase tools
-> DB
```

Dima keeps:
- identity/session;
- product conversation identity;
- run lifecycle;
- SSE normalization;
- cancel/retry;
- UI;
- evidence wrapper;
- decision/report state.

Metabase may own:
`analytics cognition/tool loop`

Evidence integration is a later question and must not be pre-implemented in FT-005N.

## 17. GREEN gate for FT-005N experiment

- [ ] status synced;
- [ ] source audit sealed;
- [ ] A0 non-mutating runtime capture mechanism;
- [ ] A0 behavior receipt;
- [ ] A1 pinned v0.63.18 isolated control;
- [ ] stock endpoint availability classified;
- [ ] native stream parser;
- [ ] Q1 native smoke;
- [ ] Q1->Q2->Q3 native NLQ;
- [ ] Q1->Q2->Q3 current Fast;
- [ ] independent DB oracle;
- [ ] extended corpus frozen before results;
- [ ] A/B/C traces;
- [ ] capability-retention breakdown;
- [ ] difference decomposition;
- [ ] decision receipt.

FT-006 remains blocked until this experiment closes.
