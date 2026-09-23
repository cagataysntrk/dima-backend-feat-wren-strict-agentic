# DIMA FAST TRACK — DURUM

Status: LIVING AUTHORITY
Branch: `feat/dima-metabase-product-fast-track`

## CURRENT_STATE

PRE_SEAL_FT004_HEAD:
`5114372fb78049d95a7b4ba763e73817d7052a55`

OBSERVED_BRANCH_HEAD:
`30659f7892ce2d4eafffec89716b75e2ce09ea48`

CURRENT_PRODUCT_GATE:
`FT-005N — NATIVE METABOT CAPABILITY RETENTION CONTROL`

FT-003_FINAL:
`CLOSED / GREEN`

FT-004_FINAL:
`CLOSED / GREEN`

FT-005_CORE:
`GREEN`
run: `35784476690`

FT-005_REAL_MODEL:
`RED`
run: `35786550995`
tested SHA: `19628e973b6ceee3b50620a7a544903364823e77`

FT-005_REAL_METABASE_FOLLOWUP:
`RED`
run: `35786695054`
tested SHA: `68c53f4d1247a1fe813ebaf6bcc901916f6f2660`

FT-005_FINAL:
`OPEN`

FT-005_DETERMINISTIC_PROMPT_REPAIR:
`GREEN`
product repair: `2282df3b6d9fc77e9cd20046da8e6d95d860921e`

FT-005_REAL_MODEL_RECERTIFICATION:
`PENDING / OPENROUTER CAPACITY RESTORED BY USER, RE-PROOF NOT YET RECORDED`

FT-005N:
`OPEN / NATIVE METABOT CONTROL`

FT-006:
`BLOCKED`

OPEN_RED:
`FT-005 FINAL CERTIFICATION + FT-005N ARCHITECTURE CONTROL`

FT-004_POST_SEAL_INVARIANTS:
`CLOSED / GREEN`

POST_SEAL_CORE:
`35781659952 GREEN`

POST_SEAL_LIVE:
`35781660160 GREEN`

POST_SEAL_GATEWAY:
`35781659866 GREEN`

POST_SEAL_BROWSER:
`35781660084 GREEN`

TARGET:
`Dima-native Intelligence Workspace on Metabase Analytics Substrate`

SELECTED_RENDERING:
`OPTION_A — Dima-native chart/table`

## FT-004 CERTIFIED RUNS

FT-004_CORE_API_SSE:
`GREEN`
run: `35778861234`
tested SHA: `5114372fb78049d95a7b4ba763e73817d7052a55`

FT-004_REAL_METABASE_LIFECYCLE:
`GREEN`
run: `35778861380`
tested SHA: `5114372fb78049d95a7b4ba763e73817d7052a55`
artifact digest:
`sha256:0ef6a463b386b4548128cc3dde2d580c6620ca91d851d9bffea042fbca7cb660`

FT-003_BROWSER_REGRESSION:
`GREEN`
run: `35778348522`
tested SHA: `0e0a948202eac24bbdca05c954764d8a370f3d89`

FT-002B_GATEWAY_REGRESSION:
`GREEN`
run: `35778348296`
tested SHA: `0e0a948202eac24bbdca05c954764d8a370f3d89`

FT-003_LIVE_REGRESSION:
`GREEN`
run: `35778100295`
tested SHA: `c14c60fc2c718212b6a78ab98fe47c34d47e2e40`

## FT-004 PROVEN CHAIN

```text
POST /fast/runs
-> opaque run_id
-> CREATED
-> bounded worker
-> RUNNING
-> sealed FastAskService
-> real pinned Metabase
-> real analytics DB
-> evidence + deterministic answer
-> COMPLETED
-> canonical snapshot
-> replayable SSE events
```

Real live COUNT:
`20`

Real answer:
`Sonuç: 20 kayıt.`

Successful event sequence:
```text
RUN_CREATED
RUN_STARTED
RUN_COMPLETED
```

Clarification/cancel live sequence:
```text
RUN_CREATED
RUN_STARTED
RUN_WAITING_CLARIFICATION
CANCEL_REQUESTED
RUN_CANCELLED
```

## FT-004 LIFECYCLE AUTHORITY

Canonical states:
- CREATED;
- RUNNING;
- WAITING_CLARIFICATION;
- PARTIAL;
- COMPLETED;
- FAILED;
- CANCEL_REQUESTED;
- CANCELLED;
- INTERRUPTED.

Terminal states:
- COMPLETED;
- FAILED;
- CANCELLED;
- INTERRUPTED.

Proven:
- terminal exactly once;
- terminal immutable;
- duplicate-event dedupe;
- monotonic event IDs;
- Last-Event-ID replay;
- foreign principal -> 404;
- owner -> allowed;
- retry lineage creates a new run;
- original terminal run never reopens;
- root_run_id preserved;
- attempt increments;
- nonterminal recovery -> INTERRUPTED;
- cooperative cancel discards late success.

## CLOSED FT-004 FAILURE FAMILIES

- `FT_004_WAITING_CLARIFICATION_CANCEL_001`
  - class: RUN_STATE_MACHINE_IMPLEMENTATION;
  - fixed by preserving pre-cancel state and finalizing quiescent cancellation;
  - closed by core runs `35778574189` and `35778861234`.

- `FT_004_ASK_COMPATIBILITY_TEST_FIXTURE_001`
  - class: EVAL_ORACLE_FIXTURE_CONTRACT;
  - production `FastAskService` type guard retained;
  - test fixture corrected;
  - closed by core runs `35778574189` and `35778861234`.

## OPEN DEBT / NOT FT-004 BLOCKERS

```text
PROCESS_RESTART_DURABILITY = NOT YET CERTIFIED
PERSISTENT_RUN_EVENT_STORE = NOT YET IMPLEMENTED
DISTRIBUTED_WORKERS = NOT YET IMPLEMENTED
CROSS_INSTANCE_SSE_FANOUT = NOT YET IMPLEMENTED
HARD_CANCEL_RUNNING_METABASE_QUERY = NOT YET IMPLEMENTED
```

Current run/event store is intentionally in-process behind a Fast-owned store boundary.
These become mandatory before production/external pilot where applicable.

FT-003 deliberate debt remains:
`MULTI_CANDIDATE_RESOLUTION = CONSERVATIVE_CLARIFICATION`

## CURRENT INVARIANTS

- writes only to Fast Track branch;
- source branches read-only;
- Wren/V2/V3 modification = forbidden;
- sealed FT-003 cognition/query/evidence semantics are not duplicated;
- `/fast/ask` remains compatibility/Quick adapter;
- lifecycle ownership belongs to Fast run layer;
- run terminal state exactly once;
- model does not own run state;
- raw SQL = 0;
- joins = 0 in sealed FT-003 family;
- METABASE_LICENSE_BUDGET = 0;
- paid Metabase core dependency = 0;
- browser Metabase service/admin secret = 0.

## POST-SEAL FT-004 INVARIANTS

```text
cancel-before-RUNNING
-> Ask call = 0

run owner identity
= tenant_id + user_id

retry
= same question + same as_of_date
```

Closed receipts:
- `FT_004_POST_SEAL_CANCEL_START_RACE_001`;
- `FT_004_POST_SEAL_OWNER_IDENTITY_001`;
- `FT_004_POST_SEAL_RETRY_IDENTITY_001`.

## FT-005 CURRENT IMPLEMENTATION

Implemented and provider-free GREEN:
- FastConversationStore;
- FastConversationService;
- StructuredJsonFastFollowupCognition;
- ContextBoundFastCognition;
- authenticated conversation HTTP surface;
- typed accepted context;
- turn lineage;
- explicit older-turn reply;
- self-contained topic switch isolation;
- active-run conflict;
- clarification continuation with new child turn/new run;
- accepted USER-question lineage;
- owner isolation;
- retry/follow-up separation.

Current core proof:
`35784476690 GREEN`

Current audited implementation SHA:
`d88e599ec702c4a3edaaecbaeba236af30a92139`

Hard debt:
`CONVERSATION_DURABILITY = NOT YET CERTIFIED`

## NEXT_EXACT_ACTION

1. Do NOT open FT-006.
2. Preserve FT-005 final status OPEN.
3. Current minimal generic follow-up prompt repair is provider-free GREEN.
4. Wait only on canonical model-certification capacity; do not invent another model/provider substitute.
5. When OpenRouter capacity is available, run Luna frozen focused corpus first.
6. If Luna hard gates pass, run Luna real-Metabase Q1 -> Q2 -> Q3 with independent DB oracle.
7. Run Sol comparable only for Luna RED/borderline families plus full three-turn confirmation.
8. Keep Sol ceiling reasoning in a separate lane.
9. Any new RED -> receipt before patch.
10. Only after honest model + Metabase + DB certification: seal FT-005.
11. Then add Research Doctrine docs-only reconciliation.
12. Then open FT-006.

## FT-005 CURRENT CERTIFICATION RED

Provider-free core:
`35784476690 GREEN`

Focused current third-model diagnostic:
`35786550995 RED`

Real-model + pinned-Metabase three-turn E2E:
`35786695054 RED`

Pinned Metabase startup:
`GREEN`

Independent DB oracle:

```text
Q1 last-30-day SUM = 16270
Q2 previous-month SUM = 21994
Q3 previous-month breakdown:
East = 5523
North = 5425
South = 5474
West = 5572
```

Current classification:
- A: EVAL_ORACLE_OVERCONSTRAINT;
- B: MODEL_STRUCTURED_OUTPUT_RELIABILITY;
- C: RETRIEVAL_CONTRACT_DRIFT candidate.

No product prompt patch is authorized yet.

Next:
1. open RED receipts;
2. add eval-only structured-output diagnostics;
3. separate HARD vs DIAGNOSTIC oracle;
4. repeat current Gemini diagnostic;
5. run Luna baseline and Sol ceiling on the frozen corpus;
6. classify model dependency;
7. only then authorize minimal fixes.


## FT-005 OBSERVABILITY DIAGNOSTIC

Gemini focused diagnostic rerun:
`35788724994 RED`

Gemini E2E diagnostic rerun:
`35788733890 RED`

Current evidence:
- provider transport = healthy;
- JSON parse = healthy;
- repeated q3 schema mismatch = systematic 3/3;
- executable reason/schema mismatch = observed;
- retrieval contract drift = observed;
- exact inherited_slots labeling = DIAGNOSTIC, not execution authority.

Authorized next step:
`MODEL DEPENDENCY MATRIX`

Roles:
- `google/gemini-2.5-flash-lite` = THIRD_MODEL_DIAGNOSTIC;
- `gpt-5.6-luna` = LUNA_BASELINE / economic default candidate;
- `gpt-5.6-sol` = SOL_CEILING / capability reference.

Frozen inputs/contracts only; model changes.


## FT-005 MODEL DEPENDENCY MATRIX — BLOCKED

Matrix workflow:
`35789207838`

Matrix SHA:
`b606a95f089cb4ca9fc65ea0024825ea4fc0fd5f`

LUNA_BASELINE:
`BLOCKED_NO_CREDENTIAL`

Exact model:
`gpt-5.6-luna`

Artifact digest:
`sha256:0ebe4d78b8671f9886d4ce189ee3e3c9fbbc3fe17db0c86369e621c81f1a9321`

SOL_CEILING:
`BLOCKED_NO_CREDENTIAL`

Exact model:
`gpt-5.6-sol`

Artifact digest:
`sha256:3a5aa74c90a47b959c80822ca4a5bce0145b04d8453d23a849665d81fbecd578`

Missing canonical benchmark credential:
`DIMA_OPENAI_API_KEY`
(fallback accepted by workflow: `OPENAI_API_KEY`)

Important:
- workflow job conclusion SUCCESS means the blocker receipt was emitted successfully;
- it does NOT mean either model corpus passed;
- Luna was not silently replaced;
- Sol was not silently replaced;
- Gemini remains THIRD_MODEL_DIAGNOSTIC and remains RED;
- no model-dependency conclusion is authorized until Luna/Sol actually execute.

Latest Gemini frozen diagnostic:
`35789186261 RED`

Gemini artifact digest:
`sha256:cd68d419c8262a123e9a99166afa8b2160bfee5102bba264974f2505473059d3`

Current external blocker:
`OPENAI_BENCHMARK_CREDENTIAL`

Current product-code authorization:
`NO PROMPT / SCHEMA / ALGORITHM PATCH UNTIL MODEL MATRIX EXECUTES`


## FT-005 MATRIX FAIL-CLOSED CONFIRMATION

Canonical blocked rerun:
`35789534149`

Tested SHA:
`f677493c2722cc2117e1795cd0aa94e283cc81d4`

Luna job:
`FAILURE / corpus SKIPPED / BLOCKED_NO_CREDENTIAL`

Sol job:
`FAILURE / corpus SKIPPED / BLOCKED_NO_CREDENTIAL`

This replaces the misleading dashboard interpretation of the earlier successful blocker-emission run.
The actual model matrix remains unexecuted.


## FT-005 MODEL MATRIX TRANSPORT TRIAGE

Observed blocked matrix:
`35789696098`

Observed matrix state:
- LUNA_BASELINE = BLOCKED_NO_CREDENTIAL / corpus NOT RUN;
- SOL_CEILING = BLOCKED_NO_CREDENTIAL / corpus NOT RUN.

This is NOT Luna/Sol model-quality evidence.

Root cause:
`BENCHMARK_TRANSPORT_CREDENTIAL_MISMATCH`

The Fast matrix attempted a new direct-OpenAI credential path:
`DIMA_OPENAI_API_KEY || OPENAI_API_KEY`

Repository reference evidence shows the established Luna/Sol benchmark path already uses:
`OpenRouter + DIMA_OPENROUTER_API_KEY || OPENROUTER_API_KEY`

Current exact correction:
- transport provider = OPENROUTER;
- Luna request model = `openai/gpt-5.6-luna`;
- Sol request model = `openai/gpt-5.6-sol`;
- strict json_schema;
- provider.allow_fallbacks = false;
- explicit reasoning policy;
- bounded max_tokens;
- production provider/runtime code untouched.

MODEL_MATRIX:
`BLOCKED_BY_WRONG_TRANSPORT_CREDENTIAL_WIRING`

Product capability blocker:
`NO`


## FT-005 OPENROUTER TRANSPORT SMOKE — CLOSED / GREEN

Run:
`35816680632`

Tested SHA:
`57943518e9c4ca85710795423f1cd0ee2090f809`

Provider-free contract:
`GREEN`

LUNA_BASELINE transport:
`GREEN`
request model: `openai/gpt-5.6-luna`
artifact: `sha256:19f90afab4bc728896183a23ba732088a63eb99357d6e858cda0d1f4e43751bb`

SOL_CEILING comparable transport:
`GREEN`
request model: `openai/gpt-5.6-sol`
artifact: `sha256:feb9bab21a5e763e96b9ed975041ad4d1b271fbb63e70e8f8820a3a349d8e3de`

Proven:
- canonical OpenRouter credential path works;
- exact request/response model identity recorded;
- strict JSON-schema accepted;
- provider fallback disabled;
- typed output valid;
- product runtime/provider code untouched.

MODEL_MATRIX:
`TRANSPORT_READY / FULL_FROZEN_CORPUS_NEXT`


## FT-005 FULL MODEL MATRIX — PARTIALLY EVALUABLE RED

Run:
`35816894471`

Tested SHA:
`946cb933441381078941767e8ac6205349ff81e3`

LUNA_BASELINE / MODEL_COMPARABLE:
`RED / EVALUABLE`

SOL_CEILING / MODEL_COMPARABLE:
`RED / PARTIALLY EVALUABLE`

SOL_CEILING / MODEL_CEILING:
`RED / PARTIALLY EVALUABLE`

Why partially evaluable:
later Sol calls hit OpenRouter HTTP 403 total key limit and are transport/provider failures, not model wrongs.

Current proven families:
- shared executable-reason typed-contract mismatch;
- retrieval-language/entity lookup drift candidate;
- Sol ceiling unsafe ambiguity auto-pick;
- unsupported representation mismatch;
- Luna clarification temporal semantic mismatch;
- OpenRouter provider-limit rows excluded from model-quality scoring.

Current conclusion:
`STRONGER_MODEL_REQUIREMENT = NOT PROVEN`

`SHARED_CONTRACT_REPRESENTATION_DEBT = PROVEN`

Next exact action:
real pinned-Metabase metadata SEARCH proof for observed retrieval terms before any retrieval prompt change.


## FT-005 RETRIEVAL LANGUAGE PROBE — GREEN

Run:
`35817396762`

Tested SHA:
`f7c74d7a7b2127e14c3fd1680e70588a68352a75`

Artifact:
`sha256:39b584620675917648ce8f43e7d73b4f1c95a97620b4fa97920d7535094d0b41`

Confirmed:
- Turkish-only order lookup terms -> SEARCH miss -> CATALOG_FALLBACK;
- English entity/table term -> direct SEARCH;
- mixed user-language + English entity term -> direct SEARCH;
- metric phrase -> SEARCH miss.

`RETRIEVAL_DRIFT_PRODUCT_IMPACT = CONFIRMED`

Authorized next:
eval-only generic follow-up contract repair experiment covering:
1. executable reason representation;
2. outer UNSUPPORTED representation;
3. FT-003-equivalent entity-centric cross-language retrieval wording;
4. ambiguity must remain fail-closed.

Product code remains unchanged until that experiment isolates the minimal repair.


## FT-005 MINIMAL PROMPT REPAIR — DETERMINISTIC GREEN / LIVE BLOCKED

Product repair:
`2282df3b6d9fc77e9cd20046da8e6d95d860921e`

Prompt-contract test:
`bfa721ff80ade67fa1978b5e3c83bc2be44db7e7`

Provider-free core:
- `35817877655 GREEN`
- `35817891294 GREEN`

Real Gateway regression:
`35817877667 GREEN`

Real browser regression:
`35817877576 GREEN`

Live model re-proof:
- Luna eval contract probe `35817686083` -> HTTP 403 key total limit before semantic output;
- third-model E2E `35817877779` -> HTTP 403 before first turn;
- measurement credential probe `35818129429` -> BLOCKED_NO_MEASURE_CREDENTIAL before API call.

Current external blocker:
`OPENROUTER_CANONICAL_KEY_CAPACITY`

Current product assessment:
`DETERMINISTIC_REPAIR_GREEN / REAL_MODEL_CERTIFICATION_PENDING`

FT-005:
`OPEN`

FT-006:
`NOT OPENED`


## FT-005N — NATIVE METABOT CAPABILITY RETENTION CONTROL

Opened after supervisor source audit.

Purpose:
`Determine whether Fast loses analytical capability by replacing Metabase native agent orchestration with custom Fast cognition/orchestration while retaining largely the same underlying Metabase primitives.`

This is:
- an architecture experiment;
- a control study;
- NOT a production migration;
- NOT authorization to fork Metabase;
- NOT authorization to bypass licensing;
- NOT FT-006.

Control arms:
- A0 = observed current Boyahane / current `latest` runtime;
- A1 = isolated pinned vanilla Metabase v0.63.18;
- B = direct stock `/api/metabot/agent-streaming`;
- C = current Fast architecture.

Current Boyahane source control:
- repo = `cagataysntrk/metabase-boyahane`;
- observed HEAD = `f0c4a6b053ead52ca2eac80002c448323dc34a35`;
- configured Metabase image ref = `metabase/metabase:latest`;
- source DB shape = 80 tables / 462,962 rows;
- current local image ID / RepoDigest / runtime version / provider / exact model = NOT YET CAPTURED BY THIS CLOUD WORKSPACE.

Pinned causal control:
- runtime = `v0.63.18`;
- image digest = `sha256:1160b570cb11c107bce00e71293552df8a8363e01a32c2c7a048cee002dc8a73`;
- main Boyahane compose must remain unchanged.

Hard rules:
- `ENTERPRISE_GATE_BYPASS = 0`;
- `LICENSE_CHECK_PATCH = 0`;
- `PAID_FEATURE_PATCH = 0`;
- Metabase source modification = NOT YET;
- fork = NOT YET;
- Fast product code must not be changed to make the native benchmark win or lose.

Source audit receipt:
`backend/belgeler/fast/receipts/audits/FT_005N_NATIVE_METABOT_SOURCE_AUDIT.md`

Predevelopment authority:
`backend/belgeler/fast/predev/FT_005N_NATIVE_METABOT_CONTROL_PREDEVELOPMENT_REVIEW.md`

## FT-005N NEXT EXACT ACTION

1. Freeze FT005N seam corpus before results.
2. Add Fast-owned A0 runtime-capture helper without modifying Boyahane.
3. Create isolated A1 pinned v0.63.18 Boyahane benchmark.
4. Test stock `/api/metabot/agent-streaming` availability with no feature-gate patch.
5. If available, Q1 native NLQ smoke.
6. Parse native stream into structured trace: tool calls, tool results, state, history, final result.
7. Carry returned history/state exactly as native frontend does for Q1→Q2→Q3.
8. Run current Fast on the same analytical cases.
9. Compute independent DB oracle.
10. Classify A1/B/C outcomes and `VANILLA_CAPABILITY_RETENTION`.
11. If native materially wins, STOP before Fast prompt/algorithm patches and open architecture-pivot decision receipt.
12. If native does not materially win, return to FT-005 model recertification.
13. FT-006 remains blocked until FT-005N decision closes.
