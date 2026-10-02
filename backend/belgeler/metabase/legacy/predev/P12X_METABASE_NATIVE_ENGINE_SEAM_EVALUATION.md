# P12X — METABASE NATIVE ENGINE / FORK SEAM EVALUATION

**Milestone:** P12X  
**Branch:** `feat/dima-metabase-platform`  
**Opening HEAD:** `ef56f6d53ebe9399a9ab322a890c6a23c5cd5c01`  
**Decision:** `DMP-DEC-0030`  
**Pinned Metabase control:** `v0.63.18 / 2ba2485c78d7e00a9a25f82c00fc201da71590c4`  
**Boyahane fixture:** `cagataysntrk/metabase-boyahane@f0c4a6b053ead52ca2eac80002c448323dc34a35`

Status: **SEALED / V0+A+B LAB MEASUREMENT AUTHORIZED / NO PRODUCT OR FORK IMPLEMENTATION**

## 1. Purpose

Measure whether the current external-cognition + Agent API architecture loses analytical capability
that exists in Metabase's native Metabot engine.

No architecture preference is assumed.

## 2. Why P12X exists

Pinned source proves two materially different integration surfaces:

```text
Agent API
= headless primitive BI/query/content surface

/api/metabot/agent-streaming
= native iterative Metabot runtime
= run-agent-loop
```

The native runtime includes profile-specific prompt/model/tool registry, permission-scoped tools,
skills, memory/state, iterative tool-result feedback, self-correction and terminal semantics.

A primitive surface and an iterative native runtime must not be treated as equivalent without
measurement.

## 3. Authorized seams

```text
V0 vanilla Metabase product
A  existing external-cognition / Agent API path
B  native /api/metabot/agent-streaming
```

Not authorized:
```text
C thin fork/in-process run-agent-loop
D native runtime + Dima hooks
```

## 4. Runtime confounder rule

Boyahane currently uses `metabase/metabase:latest`.

P12X must record the exact pulled Vanilla:
- version returned by runtime;
- image repo digest;
- image id;
- benchmark timestamp.

It must also run/control against:
```text
v0.63.18
sha256:1160b570cb11c107bce00e71293552df8a8363e01a32c2c7a048cee002dc8a73
```

`latest-vs-v0.63.18` must never be conflated with
`native-runtime-vs-Agent-API`.

## 5. Dataset freeze

Boyahane is read-only evidence.

Freeze:
- repo SHA;
- DuckDB Git blob SHA;
- DuckDB SHA-256 computed in CI;
- exact table count;
- exact row count;
- ordered PostgreSQL schema snapshot;
- schema snapshot SHA-256.

Known repository expectations:
```text
tables = 80
rows   = 462962
```

Do not modify the Boyahane repository.

## 6. Corpus

Freeze 12–16 high-information cases covering at minimum:
- simple count;
- simple sum/metric;
- metric + breakdown;
- time-filtered metric;
- previous-period comparison;
- Top-N/ranking;
- entity/value filter;
- Turkish/multilingual request;
- follow-up using prior result/context;
- ambiguous resource/entity;
- wrong-join trap;
- grain trap;
- query/tool repair;
- missing/nonexistent value.

No near-duplicate volume.

## 7. Oracle

Each case has one independent expected outcome:
- exact DB value/result shape; or
- explicit clarification; or
- explicit unsupported/gap.

Candidate prose is never its own oracle.

## 8. Model policy

Primary:
`openai/gpt-5.6-luna` through the same OpenRouter provider credential where the seam supports it.

Native Metabot is configured as:
`openrouter/openai/gpt-5.6-luna`.

Hold constant where possible:
- task;
- DB snapshot;
- authenticated user;
- permissions;
- provider;
- model;
- temperature when controllable.

Do not replace native Metabot prompt/skills/tools/memory with Dima prompt/state. Those are part of the
candidate engine.

Sol is differential-only after first-pass classification.

## 9. Seam A control

Do not copy Fast Track code.

The Fast branch remains read-only. P12X may:
- inspect exact current Fast code/receipts;
- run the exact branch in an isolated checkout/worktree inside CI when useful;
- invoke its public/internal test entry points as a control;
- record its SHA.

No Platform import dependency and no harvest.

If the current Fast product cannot represent a corpus family, record a typed
`ORCHESTRATION_CAPABILITY_LOSS`/unsupported classification rather than extending Fast during P12X.

## 10. Seam B harness

Lab-only path:
`backend/lab/metabase/p12x/`.

Responsibilities:
- authenticate the same restricted Metabase user;
- send task/context/history/state to `POST /api/metabot/agent-streaming`;
- collect the complete stream;
- retain native final state;
- retain observable tool calls/results/debug stream where available;
- extract final query/result/answer when available;
- record latency/model identity/iterations/tool count/query count;
- make no Dima semantic intervention.

No product imports beyond generic benchmark utilities.

## 11. Vanilla baseline

V0 must be reproducible before architecture conclusions.

Where direct UI automation is unavailable, P12X may use the same native Metabot endpoint with the
vanilla product context/profile as a transport-equivalent engine baseline **only if** the distinction
is explicitly recorded. A true UI/browser run remains preferred when the existing deployment is
available.

If exact user's historical `latest` image cannot be recovered, classify:
`VANILLA_HISTORICAL_RUNTIME_IDENTITY_UNRECOVERABLE`.
Then benchmark the exact newly pulled `latest` digest and the pinned v0.63.18 control separately.

## 12. Metrics

Per task/seam:
- first-query correctness;
- final-answer correctness;
- silent wrong;
- clarification behavior;
- retrieval success;
- multilingual retrieval;
- follow-up consistency;
- query repair;
- semantic drift;
- wrong join;
- wrong grain;
- tool-call count;
- query count;
- agent iterations;
- latency;
- token/model cost where observable;
- permission behavior.

Architecture:
- new code LOC;
- new files;
- modified upstream files;
- dependency surface;
- maintenance surface.

Mandatory:
```text
VANILLA_CAPABILITY_RETENTION
= candidate PASS among Vanilla-PASS tasks
  / total Vanilla-PASS tasks
```

Absolute candidate success is reported separately.

## 13. Failure taxonomy

```text
SECURITY_DENIAL
SEMANTIC_AUTHORITY_BLOCK
RETRIEVAL_FAILURE
ORCHESTRATION_CAPABILITY_LOSS
QUERY_CONSTRUCTION_FAILURE
MODEL_COGNITION_FAILURE
VERSION_CONTEXT_CONFOUNDER
ORACLE_FIXTURE
TRANSPORT_RUNTIME
```

Classify before changing harness/oracle.

## 14. Stop gate

Initial execution order ends after V0+A+B measurement and classification.

Return:
- Platform HEAD;
- exact corpus fingerprint;
- dataset fingerprint/schema fingerprint;
- exact Vanilla latest version/digest;
- pinned v0.63.18 control;
- exact Luna runtime/provider id;
- per-case oracle/results;
- Vanilla capability retention;
- failure classification;
- tool/iteration/query/latency/cost summary;
- one of:
  `AGENT_API_RETAINS_CAPABILITY`,
  `NATIVE_RUNTIME_MATERIAL_ADVANTAGE`,
  `VERSION/CONTEXT_CONFOUNDER`.

No Seam C/fork before supervisor authorization.


---

## DMP-DEC-0031 override — fork bootstrap authorized

The original measurement thesis remains valid, but the full V0+A+B Agent-API bake-off is no longer a prerequisite for fork bootstrap.

Executable current-corpus sanity:
```text
fingerprint = fd6e5934438795f64e9ec7d64b74b56056c3c1304aa51598d18c170839b792a0
workflow    = 35824464298 = SUCCESS
job         = 107063206949 = SUCCESS
runtime     = v0.63.18 / 2ba2485
resource    = Dima Analytics Lab / public / satis_siparisleri
PX-01       = 126 == oracle 126
errors      = 0
scorer      = GREEN
```

New ordered authorization:
```text
P12X-C0 = exact upstream-history fork bootstrap + fork-source build
P12X-C1 = stock-vs-fork native capability parity
P12X-C2 = stable Dima bridge + bridge/native parity
P12X-C3 = upstream-sync + DIMA_PATCH_SURFACE certification
```

The frozen 16-case corpus is retained for later native capability regression/stabilization. P13 remains paused until C1/C2 are GREEN.