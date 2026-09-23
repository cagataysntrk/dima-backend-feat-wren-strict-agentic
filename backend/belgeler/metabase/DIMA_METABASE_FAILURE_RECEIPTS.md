# DIMA + METABASE — FAILURE RECEIPTS

> RED → classify → single owner → root cause → allowed files → proof. Patch önce receipt.

## Mandatory schema

```text
receipt_id
ticket
tested_sha
run_id
observed_failure
failure_stage
failure_class
failure_tag?
classification_evidence
single_owner
root_cause
failure_family
forbidden_patch_alternatives
allowed_files_to_touch
files_not_to_touch
invariant_being_fixed
focused_proof
family_or_live_proof
status
```

Allowed top-level failure classes:
```text
MODEL_COGNITION
CONTRACT/ARCHITECTURE
RESOLVER_TRUTH
EVAL_ORACLE
TRANSPORT/PROVIDER
```

Metabase tags:
```text
SUBSTRATE_QUERY
PERMISSION
ACCESS_LENS
RESOURCE_DRIFT
IMPLICIT_JOIN
CACHE_ISOLATION
PERSISTENCE_REPLAY
```

---

## REFERENCE — SOURCE-HEAD-FULL-LIVE-001

This is **source-selection evidence**, not a platform-branch product failure.

tested_sha: `4ad8238c4fe8ada02a8a1a79e0682606a6fbfe1a`  
run_id: `35724830736`  
result: FAILURE  
observed: `si-live-001 / metric_only_non_exact` ended `CLARIFICATION_REQUIRED`; expected `ACCEPTED`.  
effect on this branch: the moving source HEAD was not promoted to `DIMA_BASE_CERTIFIED_SHA`.  
product patch on source branch: **FORBIDDEN BY THIS WORK / NONE PERFORMED**.  
status: CLOSED AS BASE-SELECTION EVIDENCE.


---

## DMP-M1-RED-001 — legacy ContractStore parameter-name oracle

receipt_id: `DMP-M1-RED-001`  
ticket: `M1-P1-001`  
tested_sha: `6aa7f9ab2b661bae96074ab7c79e0ce8d4503eb5`  
run_id: `35728158584`

observed_failure:
`test_wren_substrate_has_no_semantic_handle_or_raw_language_dependency` rejected the source because
the token `question` appears in `record_v2_minimum(question=intent.request_ref, ...)`.

failure_stage:
M1 architecture guard test, before any semantic/query parity assertion.

failure_class:
`EVAL_ORACLE`

classification_evidence:
- `WrenSubstrateAdapter.execute_execution_intent` accepts only `ResolvedAnalyticsIntent`;
- `ResolvedAnalyticsIntent` contains request_ref + source_message_hash, not the raw user question;
- the value passed to the legacy API field named `question` is `intent.request_ref`;
- the test performs a raw substring search and cannot distinguish API keyword names from raw-language data flow;
- compile and provider-free contract gate were GREEN.

single_owner:
`backend/tests/test_v3_m1_wren_adapter.py` architecture oracle.

root_cause:
lexical substring assertion encoded the word `question` as forbidden rather than asserting the actual
contract: no raw-language field/input reaches the substrate.

failure_family:
source-code architecture tests that confuse identifier/parameter names with runtime data provenance.

forbidden_patch_alternatives:
- rename external `ContractStore` API just to satisfy the substring;
- weaken the substrate boundary by adding raw question;
- hide strings/comments from inspection;
- modify v2 ContractStore.

allowed_files_to_touch:
- `backend/tests/test_v3_m1_wren_adapter.py`

files_not_to_touch:
- `backend/app/v2/**`
- `backend/app/v3/substrate/wren.py` for this failure

invariant_being_fixed:
oracle must prove data-flow boundary, not identifier spelling.

focused_proof:
rerun M1 architecture test.

family_or_live_proof:
full M1 workflow.

status:
`CLASSIFIED / PATCH AUTHORIZED — TEST ORACLE ONLY`.

---

## DMP-M1-RED-002 — candidate provenance lost across ResolvedAnalyticsIntent

receipt_id: `DMP-M1-RED-002`  
ticket: `M1-P1-001`  
tested_sha: `6aa7f9ab2b661bae96074ab7c79e0ce8d4503eb5`  
run_id: `35728158584`

observed_failure:
real Wren parity produced the same canonical metric/cube/query semantics but v3 rebuilt
`AnalyticsIR.metrics[0].candidate_id` as the opaque `sem_*` handle instead of the certified
resolver candidate id `m1-parity-metric`.

failure_stage:
`ResolvedAnalyticsIntent → WrenSubstrateAdapter → AnalyticsIR` compatibility projection.

failure_class:
`CONTRACT/ARCHITECTURE`

classification_evidence:
- old IR: `candidate_id=m1-parity-metric`;
- v3 IR: `candidate_id=sem_2c438d6ee368048988caf582`;
- target kind, canonical name, source cube and query execution remained aligned;
- the builder discarded the original resolver `candidate_id` while retaining only the semantic handle id;
- adapter cannot reconstruct that provenance without violating the no-second-semantic-resolution rule.

single_owner:
`app/v3/analytics_contract.py` resolved semantic-ref contract.

root_cause:
`ResolvedSemanticRef` / `ResolvedFilterRef` did not preserve the already-resolved source candidate provenance required for lossless Wren compatibility.

failure_family:
any resolved metric/dimension/filter whose downstream compatibility representation requires stable resolver provenance in addition to the opaque authority handle.

forbidden_patch_alternatives:
- make Wren adapter reopen SemanticHandleRegistry;
- infer candidate id from canonical name;
- use label/name guessing;
- weaken parity oracle to ignore provenance;
- modify certified v2 execution.

allowed_files_to_touch:
- `backend/app/v3/analytics_contract.py`
- `backend/app/v3/substrate/wren.py`
- `backend/tests/test_v3_m1_contracts.py`
- `backend/tests/test_v3_m1_wren_adapter.py`

files_not_to_touch:
- `backend/app/v2/**`
- source branch
- Metabase/runtime/front-door files

invariant_being_fixed:
handle resolution occurs exactly once in Dima, and the resolved intent is **lossless enough** for the substrate to reproduce certified execution/provenance without semantic lookup.

focused_proof:
v3 intent builder asserts both opaque semantic_ref and stable source_candidate_id.

family_or_live_proof:
real Wren v3-v2 AnalyticsIR/query/result parity plus retained v2 sentinels.

status:
`CLASSIFIED / ROOT CONTRACT PATCH AUTHORIZED`.


---

## DMP-M1-RED-003 — AST oracle indentation on method source

receipt_id: `DMP-M1-RED-003`  
ticket: `M1-P1-001`  
tested_sha: `a9f20c482d262b95a37fee9d26b8f27002dab67c`  
run_id: `35728504998`

observed_failure:
`test_wren_substrate_has_no_semantic_handle_or_raw_language_dependency` raised
`IndentationError: unexpected indent` while parsing `inspect.getsource(bound_class_method)`.

failure_stage:
architecture test oracle only.

failure_class:
`EVAL_ORACLE`

classification_evidence:
- compile = PASS;
- provider-free v3 M1 contract gate = PASS;
- the real v3-v2 Wren parity test passed after the candidate-provenance contract fix;
- both retained v2 Wren sentinels also passed in the same step;
- the only remaining failure occurs before the AST assertion because method source retains class indentation.

single_owner:
`backend/tests/test_v3_m1_wren_adapter.py` AST inspection helper.

root_cause:
method-level `inspect.getsource` output was not dedented before `ast.parse`.

failure_family:
architecture/source AST tests on nested/indented definitions.

forbidden_patch_alternatives:
- product code changes;
- substrate changes;
- weakening no-raw-language/no-semantic-resolution invariant;
- modifying v2.

allowed_files_to_touch:
- `backend/tests/test_v3_m1_wren_adapter.py`

files_not_to_touch:
- `backend/app/v3/**` for this failure
- `backend/app/v2/**`
- source branch

invariant_being_fixed:
architecture oracle must parse the inspected source correctly while preserving the same data-flow assertions.

focused_proof:
rerun architecture test.

family_or_live_proof:
full M1 workflow.

status:
`CLASSIFIED / TEST-ONLY PATCH AUTHORIZED`.

### DMP-M1-RED-002 interim proof

On run `35728504998`, the previously failing real v3-v2 Wren parity assertion passed after
`source_candidate_id` was preserved in `ResolvedAnalyticsIntent`. Final closure waits for a
fully GREEN M1 workflow; no further product patch is currently justified.


---

## DMP-M1-RED-004 — isolation gate shallow-checkout oracle

receipt_id: `DMP-M1-RED-004`  
ticket: `M1-P1-001`  
tested_sha: `7ed76d3de8a8f566466bb4c4816a3bbb074d6941`  
run_id: `35729019518`

observed_failure:
M1 stopped at `Enforce M1 forbidden-file isolation` with:
`fatal: Invalid symmetric difference expression 377448...HEAD`.

failure_stage:
CI isolation harness before compile/tests.

failure_class:
`EVAL_ORACLE`

classification_evidence:
- GitHub compare measured forbidden M1 paths = 0 immediately before this commit family;
- the workflow uses default shallow `actions/checkout@v4` depth;
- the certified base commit is therefore absent from local runner history;
- failure occurs in `git diff BASE...HEAD` before the forbidden-path grep executes;
- governance for the same HEAD is GREEN.

single_owner:
`.github/workflows/dima-metabase-m1.yml` checkout/history setup.

root_cause:
the new ancestry/diff gate requires the immutable certified base object but checkout fetched only the current shallow tip.

failure_family:
CI gates that compare against an immutable historical SHA while using shallow checkout.

forbidden_patch_alternatives:
- remove the isolation gate;
- compare only HEAD^;
- silently ignore git-diff failure;
- product/v2 changes.

allowed_files_to_touch:
- `.github/workflows/dima-metabase-m1.yml`

files_not_to_touch:
- `backend/app/v3/**`
- `backend/app/v2/**`
- source branch

invariant_being_fixed:
isolation gate must prove the entire platform-branch delta from certified base, not merely the last commit.

focused_proof:
workflow reaches and passes the forbidden-file isolation step with full history.

family_or_live_proof:
full M1 workflow.

status:
`CLASSIFIED / CI-ONLY PATCH AUTHORIZED`.


---

## DMP-M1-RED-005 — hidden legacy QueryContract question-field behavior drift

receipt_id: `DMP-M1-RED-005`  
ticket: `M1-P1-001`  
tested_sha: `580d17ae5f0d3d48f89f8de5be63c6c4ce861004`  
run_id: `35729177007` (workflow GREEN; defect found by post-green architecture audit)

observed_failure:
The v3 Wren compatibility path writes `intent.request_ref` into the legacy
`ContractStore.record_v2_minimum(question=...)` field, while the certified v2 path writes
the original user question. SQL/result/IR parity is GREEN, but persisted audit behavior is not.

failure_stage:
post-execution QueryContract persistence / compatibility side effect.

failure_class:
`CONTRACT/ARCHITECTURE`

classification_evidence:
- P1 requires first Wren adapter behavior drift = 0;
- `ContractLog.question` is a real product/audit field, not dead metadata;
- `admin_app/routers/contracts.py` displays it and filters contracts with
  `ContractLog.question ILIKE q`;
- certified v2 `WrenStandardExecutionAdapter.execute(... question=raw_question)` persists
  that raw question;
- current v3 substrate substitutes `request_ref`, changing observable audit/search behavior;
- the substrate must still not reparse or semantically consume raw user language.

single_owner:
M1 execution/persistence boundary between Dima-owned audit/receipt writing and
`WrenSubstrateAdapter`.

root_cause:
The initial M1 seam made the Wren substrate itself own legacy QueryContract persistence.
Because the substrate correctly receives only `ResolvedAnalyticsIntent`, the original
non-semantic audit question was unavailable and was silently replaced by `request_ref`.

failure_family:
compatibility side effects that require non-semantic request/audit context even though the
analytics substrate must consume only resolved execution intent.

forbidden_patch_alternatives:
- add raw user question to `ResolvedAnalyticsIntent`;
- let Wren substrate parse/reinterpret raw language;
- keep `request_ref` and weaken zero-drift definition;
- modify v2 ContractStore/admin behavior;
- pass semantic handles back into the substrate.

allowed_files_to_touch:
- `backend/app/v3/evidence.py`
- `backend/app/v3/legacy_contract.py` (new Dima-owned compatibility writer)
- `backend/app/v3/substrate/base.py`
- `backend/app/v3/substrate/wren.py`
- `backend/tests/test_v3_m1_wren_adapter.py`
- `backend/tests/test_v3_m1_contracts.py`
- `.github/workflows/dima-metabase-m1.yml` only if compile list needs the new module
- M1 status/ticket/receipt docs

files_not_to_touch:
- `backend/app/v2/**`
- `backend/app/routers/ask_v2.py`
- `backend/app/main.py`
- `backend/app/config.py`
- `WrenAI-main/**`
- `feat/ask-v2-mvp`

invariant_being_fixed:
- analytics substrate input remains only `ResolvedAnalyticsIntent`;
- raw user language is not a substrate semantic input and is never reparsed there;
- Dima-owned compatibility receipt writer may carry the immutable audit question solely
  to reproduce the certified QueryContract side effect;
- legacy persisted question, SQL, CubeQuery, result hash, row count, schema version and
  v2 provenance remain behaviorally identical.

focused_proof:
v3-v2 parity test must assert persisted `question` equality in addition to SQL/query/result/provenance.

family_or_live_proof:
full M1 workflow + retained v2 real-Wren sentinels + forbidden-file isolation.

status:
`CLASSIFIED / ROOT BOUNDARY PATCH AUTHORIZED`.


---

## DMP-M1-RED-006 — parity-family fixture stale constructor after receipt-boundary split

receipt_id: `DMP-M1-RED-006`  
ticket: `M1-P1-001`  
tested_sha: `cd72dddc1a24774eefc94f20c4f21692ea16a757`  
run_id: `35730482937`

observed_failure:
Eight provider-free parity-family cases fail before assertions with:
`TypeError: WrenSubstrateAdapter.__init__() got an unexpected keyword argument 'contract_store'`.

failure_stage:
test fixture construction in `test_v3_m1_parity_families.py::_case`.

failure_class:
`EVAL_ORACLE`

classification_evidence:
- forbidden-file isolation = PASS;
- v3 compile including `legacy_contract.py` = PASS;
- all failures share the identical stale constructor call;
- these tests call only `adapter._to_ir(intent)` and never execute/persist a query;
- receipt-boundary patch intentionally replaced substrate-owned `contract_store/session_id`
  with optional `receipt_writer`.

single_owner:
`backend/tests/test_v3_m1_parity_families.py` fixture.

root_cause:
test helper retained constructor arguments removed by the authorized DMP-M1-RED-005 boundary correction.

failure_family:
provider-free adapter projection tests that instantiate execution adapters only to access deterministic compatibility conversion.

forbidden_patch_alternatives:
- reintroduce contract_store/session_id into Wren substrate;
- add compatibility kwargs solely for tests;
- weaken/skip parity families;
- modify v2.

allowed_files_to_touch:
- `backend/tests/test_v3_m1_parity_families.py`

files_not_to_touch:
- `backend/app/v3/**` for this failure
- `backend/app/v2/**`
- source branch

invariant_being_fixed:
test harness must instantiate the current boundary without reintroducing persistence ownership into the substrate.

focused_proof:
provider-free v3 M1 contract + parity-family gate.

family_or_live_proof:
full M1 workflow including real Wren parity and retained v2 sentinels.

status:
`CLASSIFIED / TEST-ONLY PATCH AUTHORIZED`.


---

## DMP-M1-RED-007 — Wren evidence-id hash import removed during receipt split

receipt_id: `DMP-M1-RED-007`  
ticket: `M1-P1-001`  
tested_sha: `6a88a61399f741eb4a902f4e143e490cdba304a5`  
run_id: `35730716030`

observed_failure:
Real Wren parity reaches verified execution and then fails while creating the v3 evidence
artifact with `NameError: name 'hashlib' is not defined` in `app/v3/substrate/wren.py`.

failure_stage:
post-query evidence artifact identity construction.

failure_class:
`CONTRACT/ARCHITECTURE`

classification_evidence:
- forbidden-file isolation = PASS;
- compile = PASS (undefined runtime symbol is not a syntax error);
- provider-free v3 contract/family gate = 15 PASS;
- retained real-Wren step reached the v3 execution path;
- the receipt-boundary refactor removed `hashlib` together with moved query-fingerprint helpers,
  but `hashlib.sha256` remains legitimately required for evidence artifact id generation.

single_owner:
`backend/app/v3/substrate/wren.py` import set.

root_cause:
over-broad import cleanup during DMP-M1-RED-005 implementation.

failure_family:
runtime-only missing imports after moving one of several hashing responsibilities between modules.

forbidden_patch_alternatives:
- move evidence-id hashing back into receipt writer;
- weaken/skip real Wren parity;
- change evidence identity contract;
- modify v2.

allowed_files_to_touch:
- `backend/app/v3/substrate/wren.py`

files_not_to_touch:
- all v2 files
- source branch
- semantic/authority contracts for this failure

invariant_being_fixed:
existing deterministic evidence identity generation remains intact after persistence ownership split.

focused_proof:
real v3 Wren parity test.

family_or_live_proof:
full M1 workflow including retained v2 real-Wren sentinels.

status:
`CLASSIFIED / NARROW IMPLEMENTATION PATCH AUTHORIZED`.


---

## M1 closure matrix

final_sha: `17942f179b13fd2cb81fd284789ba0f6366d2ed8`  
workflow: `35730916014 = SUCCESS`  
governance: `35730916118 = SUCCESS`

```text
DMP-M1-RED-001  CLOSED GREEN — corrected oracle
DMP-M1-RED-002  CLOSED GREEN — candidate provenance preserved; real parity passed
DMP-M1-RED-003  CLOSED GREEN — AST oracle corrected
DMP-M1-RED-004  CLOSED GREEN — full-history isolation gate passed
DMP-M1-RED-005  CLOSED GREEN — raw audit question preserved outside substrate; parity passed
DMP-M1-RED-006  CLOSED GREEN — parity fixture aligned; 15 provider-free tests passed
DMP-M1-RED-007  CLOSED GREEN — evidence hash dependency restored; real Wren step passed
```

No M1 failure remains open. Any future regression receives a new receipt id; historical receipts are not reopened.


---

## DMP-M2-RED-001 — shell-sourced lab env rejects unquoted spaced values

receipt_id: `DMP-M2-RED-001`  
ticket: `M2-P2-001`  
tested_sha: `e4036a45027ccb963d92f9b2790420754e0efdff`  
run_id: `35732250412`

observed_failure:
M2 stack creation succeeds and both PostgreSQL services become healthy. The bootstrap step exits
127 before any Metabase API call because shell sourcing `.env` reports:
`./.env: line 16: Lab: command not found`.

failure_stage:
CI/lab environment loading before bootstrap/capability probe.

failure_class:
`EVAL_ORACLE`

classification_evidence:
- M2 forbidden-file isolation = PASS;
- immutable image pin gate = PASS;
- Docker network/volumes/containers created successfully;
- both Postgres services = healthy;
- failure occurs at `source .env`, before runtime capability assertions;
- `.env.example` contains whitespace-bearing values without shell quotes.

single_owner:
`backend/lab/metabase/.env.example` shell compatibility.

root_cause:
The same env file is intentionally consumed by both Docker Compose and shell scripts. Compose accepts
unquoted whitespace values, while bash `source` interprets following words as commands.

failure_family:
dual-consumer env syntax mismatch in lab harness.

forbidden_patch_alternatives:
- remove shell `set -e`;
- ignore source errors;
- hard-code secrets/settings into scripts;
- modify product config or existing compose files.

allowed_files_to_touch:
- `backend/lab/metabase/.env.example`

files_not_to_touch:
- Dima v2/v3 product code;
- root compose;
- existing SQL Server lab;
- source branch.

invariant_being_fixed:
one lab env file must parse identically enough for Compose and POSIX-style bash sourcing.

focused_proof:
next M2 live workflow must pass env load and reach bootstrap API.

family_or_live_proof:
full M2 live workflow.

status:
`CLASSIFIED / TEST-HARNESS PATCH AUTHORIZED`.


---

## DMP-M2-RED-002 — v0.63.18 boolean setting key suffix lost in bootstrap API path

receipt_id: `DMP-M2-RED-002`  
ticket: `M2-P2-001`  
tested_sha: `4ea89e12bc900fe55f88e103799159eed6fdc3a2`  
run_id: `35732445427`

observed_failure:
Metabase health passes and `POST /api/setup` returns 200. Bootstrap then receives HTTP 500 on
`PUT /api/setting/ai-features-enabled`: runtime reports unknown setting and lists the registered
setting as `ai-features-enabled?` (likewise `agent-api-enabled?`).

failure_stage:
lab bootstrap settings configuration after successful instance setup.

failure_class:
`EVAL_ORACLE`

classification_evidence:
- immutable image + stack startup = PASS;
- health = PASS;
- initial Metabase setup = PASS;
- v0.63.18 runtime registered-setting list explicitly exposes `ai-features-enabled?` and
  `agent-api-enabled?`;
- audited v0.63.18 source defines those boolean settings with question-mark names;
- a literal `?` in a URL path must be percent-encoded to avoid becoming query-string syntax.

single_owner:
`backend/lab/metabase/scripts/bootstrap.py::set_setting` and its setting keys.

root_cause:
bootstrap used display/export naming instead of exact REST setting identifiers and did not URL-encode
setting path segments.

failure_family:
runtime API identifier encoding mismatch in lab harness.

forbidden_patch_alternatives:
- disable Agent API capability checks;
- treat health as Agent API proof;
- modify Metabase runtime/source;
- ignore setting errors.

allowed_files_to_touch:
- `backend/lab/metabase/scripts/bootstrap.py`

files_not_to_touch:
- Dima product code;
- source branch;
- runtime pin;
- existing compose files outside isolated lab.

invariant_being_fixed:
M2 bootstrap uses exact v0.63.18 runtime setting identifiers and verifies failures loudly.

focused_proof:
next M2 run must pass setup + settings and reach Agent API probe.

family_or_live_proof:
full M2 live workflow.

status:
`CLASSIFIED / LAB API FIXTURE PATCH AUTHORIZED`.


---

## M2 closure matrix

final_sha: `a05bd12ff56ac3c66eef01f7340c1f991ae07681`  
workflow: `35732633996 = SUCCESS`  
governance: `35732633999 = SUCCESS`

```text
DMP-M2-RED-001  CLOSED GREEN — shell/Compose env compatibility fixed; bootstrap reached runtime
DMP-M2-RED-002  CLOSED GREEN — exact encoded v0.63.18 setting identifiers; full live lab passed
```

Certified runtime observations:
```text
health                         true
unauthenticated Agent denied   true
agent_api_ping                 true
search                         true
read_resource                  true
construct_query                true
execute_query                  true
combined_query                 true
continuation_observed          true
observed_page_rows             200
observed_second_page_rows      5
raw_sql_disabled               true
restart persistence            true
backup                         PASS
restore                        PASS / 176 public tables
```

No M2 failure remains open. Future M2 regressions use new receipt ids.


---

## DMP-P3-RED-001 — exact Agent API read-resource envelope not modeled

receipt_id: `DMP-P3-RED-001`  
ticket: `P3-001`  
tested_sha: `3d3302baf52ad02d9fc6d59c758e418f91822a49`  
run_id: `35734065244`

observed_failure:
Pinned v0.63.18 live proof reaches search/read-resource and fails with
`KeyError: 'name'` because the live test assumes
`resources[0].content.name`.

Exact v0.63.18 source contract instead returns a per-resource envelope:

```text
resources[]
  uri
  content?  -> resource-specific payload, commonly {"structured-output": ...}
  error?    -> per-resource failure even when outer HTTP status is 200
output      -> formatted aggregate representation
```

For `metabase://database/{id}`, the database entity is produced through `entity-result`,
so the programmatic name lives under:
`resources[0].content["structured-output"]["name"]`.

failure_stage:
P3 typed read-resource transport contract / live runtime proof.

failure_class:
`CONTRACT/ARCHITECTURE`

classification_evidence:
- P3 forbidden-file isolation = PASS;
- compile = PASS;
- provider-free P3 = PASS;
- pinned M2 lab startup = PASS;
- M1 regression = PASS;
- governance = PASS;
- live failure is exactly `KeyError: 'name'`;
- v0.63.18 `::read-resource-item` defines optional `content` and `error` with documented
  either/or semantics;
- `fetch-single-uri` returns `{uri, content}` OR `{uri, error}`;
- `read-resource` returns both `resources` and top-level `output`;
- current P3 model collapses resource items to raw dicts and therefore does not preserve
  the resource-level error state as a typed contract;
- current startup handshake reports `read_resource=True` without actually probing a resource.

single_owner:
P3 read-resource transport representation and capability handshake.

root_cause:
P3 modeled the outer HTTP call but not the exact v0.63.18 per-resource envelope. Callers therefore
had to know raw nested dictionary layout, malformed/mixed resource states were not fail-closed, and
the handshake could claim read-resource capability without direct proof.

failure_family:
transport-contract drift between typed client models and pinned Agent API resource envelopes.

authorized_correction:
- model an explicit resource content/envelope type;
- require exactly one of content/error per resource;
- model top-level `output`;
- verify response resource count/order against requested URIs;
- preserve resource-level error state without string/regex semantic classification;
- make handshake execute a real read-resource probe before claiming the capability;
- update live proof to use the exact `content["structured-output"]` contract with no fallback.

forbidden_patch_alternatives:
- hard-code `"Dima Analytics Lab"` fallback;
- catch `KeyError` and continue;
- treat resource-level error as content success;
- map arbitrary error strings to permission/not-found taxonomy;
- change Metabase source/runtime;
- reopen M2;
- enter P3A/compiler code;
- add schema/name guessing;
- touch v2/Wren/authority/semantic contracts.

allowed_files_to_touch:
- `backend/app/v3/substrate/metabase/models.py`
- `backend/app/v3/substrate/metabase/client.py`
- `backend/tests/test_v3_p3_metabase_client.py`
- `backend/tests/test_v3_p3_metabase_client_live.py`
- P3 failure/status/ticket docs

focused_proof:
provider-free typed resource envelope, resource-error, malformed-envelope and handshake tests.

family_or_live_proof:
full P3 pinned-runtime workflow + M1 regression + governance.

status:
`CLASSIFIED / CONTRACT PATCH AUTHORIZED`.


---

## P3 closure matrix

final_sha: `7a4d1d12e59b52edf8493c0aa0b147947ff4ecf9`  
workflow: `35736253380 = SUCCESS`  
governance: `35736253664 = SUCCESS`  
M1 regression: `35736253552 = SUCCESS`

```text
DMP-P3-RED-001  CLOSED GREEN — exact typed read-resource envelope + real handshake resource probe
```

P3A remained blocked throughout the RED and was not implemented before P3 closure.


---

## DMP-P4-RED-001 — P4 execution-binding promotion forked instead of unified

receipt_id: `DMP-P4-RED-001`  
ticket: `P4-001`  
tested_sha: `af1750dfdfd283bfe824c9c6b40b90dca1a63cb3`  
detection: post-green architecture audit; no compiler/canonical work authorized

observed_failure:
P4 introduced production execution bindings in
`backend/app/v3/substrate/metabase/execution_binding.py`, while P3A continues to define and consume
independent copies of the same candidate/temporal/snapshot contracts in `p3a_models.py`.

At the tested SHA:
- `execution_binding.py` defines `CandidateSemanticBinding`,
  `TemporalSemanticBinding`, `DimaExecutionBindingSnapshot`,
  `CurrentCatalogObject`, `CurrentCatalogSnapshot`, and `MetabaseCompilationBlocked`;
- `p3a_models.py` separately defines `CandidateSemanticBinding`,
  `TemporalSemanticBinding`, `DimaExecutionBindingSnapshot`, and `P3ABridgeBlocked`;
- `p3a_preflight.py`, `p3a_fixture.py`, and P3A tests still consume the prototype-owned types.

failure_stage:
P4 execution-binding promotion boundary before production compiler implementation.

failure_class:
`CONTRACT/ARCHITECTURE`

single_owner:
P4 execution-binding promotion boundary.

root_cause:
Promotion was implemented as "copy production contract first, migrate prototype later" instead of
atomically establishing one authoritative contract. That temporarily creates two independently
evolvable execution-binding truths and violates DMP-DEC-0009 / P4 predevelopment review.

invariant_being_fixed:
```text
authoritative execution-binding module        = execution_binding.py
parallel candidate→semantic binding models    = 0
parallel temporal binding models              = 0
parallel execution snapshot models            = 0
parallel compilation-blocked semantics         = 0
P3A/P4 type identity                           = required
compiler/canonical implementation              = blocked until binding gate GREEN
```

authorized_correction:
- make `execution_binding.py` the single owner of production binding primitives;
- make `p3a_models.py` import/re-export those primitives rather than implement copies;
- alias `P3ABridgeBlocked` to `MetabaseCompilationBlocked` for compatibility;
- migrate P3A preflight/fixture/tests to the production binding contract;
- make the P3A synthetic fixture construct an explicit `CurrentCatalogSnapshot`;
- ensure P3A compilation validates expected SourceLineage against current catalog before emitting
  physical portable locators;
- add focused P4 binding tests, including class identity and drift/fingerprint failure proofs;
- add a dedicated P4 workflow and run P3A/P3/M1 regressions.

forbidden_patch_alternatives:
- keep shape-equivalent duplicate P3A classes;
- introduce adapters that copy between prototype and production snapshots;
- start `compiler.py` or `canonical.py` before this gate is GREEN;
- derive current catalog by Metabase label/name search;
- treat `canonical_name`, `source_scopes`, or candidate ids as physical locators;
- touch v2, authority, semantic_spec, analytics_contract, Wren, routers, main/config, or source branch;
- change P3A result semantics merely to force GREEN.

files_allowed:
- `backend/app/v3/substrate/metabase/execution_binding.py`
- `backend/app/v3/substrate/metabase/p3a_models.py`
- `backend/app/v3/substrate/metabase/p3a_preflight.py`
- `backend/app/v3/substrate/metabase/p3a_fixture.py`
- `backend/tests/test_v3_p4_execution_binding.py`
- `backend/tests/test_v3_p3a_bridge_preflight*.py`
- `.github/workflows/dima-metabase-p4.yml`
- P4 failure/status/ticket docs

focused_proof:
- type identity, not only shape equivalence;
- semantic context/candidate/time integrity;
- duplicate rejection;
- current-catalog source_id uniqueness/missing binding;
- exact DB/schema/table/column drift fail-closed;
- incomplete lineage and column-required fail-closed;
- deterministic catalog fingerprint and fingerprint sensitivity;
- P3A eight-family provider-free regression.

family_or_live_proof:
P4 workflow plus pinned-live P3A regression, P3 regression, M1 regression and governance.

status:
`CLASSIFIED / BINDING-UNIFICATION PATCH AUTHORIZED; COMPILER BLOCKED`.


---

## DMP-P4-RED-001 closure

final_binding_sha: `1771becb3e59395cf28f993345703449feb9a98d`  
p4_binding_workflow: `35742516216 = SUCCESS`  
p3a_workflow: `35742516331 = SUCCESS`  
p3_workflow: `35742516120 = SUCCESS`  
m1_workflow: `35742516339 = SUCCESS`  
governance: `35742516356 = SUCCESS`

```text
focused P4 binding tests          18 PASS
provider-free P3A/P3/M1           40 PASS
real Wren M1                      5 PASS
pinned-live P3 + P3A              2 PASS
exact production/P3A type identity PASS
parallel execution-binding models 0
parallel blocked-exception models 0
current-catalog lineage drift      fail-closed
compiler/canonical during gate     0
```

status:
`CLOSED GREEN`.

The historical RED remains recorded. Compiler implementation is a subsequent gate and receives its
own pre-implementation review before code.


---

## DMP-P4-RED-002 — byte-level canonical determinism conflicts with pinned Metabase lib/uuid semantics

receipt_id: `DMP-P4-RED-002`  
ticket: `P4-001`  
tested_sha: `3db99a6b6827d0abaefce06b12d27ab981143da2`  
run_id: `35743999330`

observed_failure:
All static/provider-free/compiler/regression gates pass, pinned M2 lab starts, and the live P4
canonical proof fails on the first family with:

`NON_DETERMINISTIC_CANONICAL_SERIALIZATION: construct-query changed for primary step`

failure_stage:
pinned v0.63.18 canonicalization determinism oracle.

failure_class:
`CONTRACT/ARCHITECTURE`

classification_evidence:
- compile = PASS;
- focused P4 binding+compiler = PASS;
- provider-free P3A/P3/M1 regressions = PASS;
- real Wren M1 regression = PASS;
- pinned lab startup = PASS;
- only live canonical double-construct equality fails;
- exact v0.63.18 `representations.resolve` documents that normalize adds `:lib/uuid` to every clause;
- exact v0.63.18 `lib.schema.common/normalize-options-map` adds
  `(str (random-uuid))` when `:lib/uuid` is missing;
- `/api/agent/v2/construct-query` serializes the normalized query to JSON/base64.

single_owner:
P4 canonical durable-identity normalization and determinism proof.

root_cause:
DMP-DEC-0012 equated byte-identical runtime serialization with semantic/canonical determinism.
The pinned runtime intentionally injects volatile per-normalization `lib/uuid` identity, so the raw
base64 payload is an executable serialization but is not a stable durable fingerprint input.

invariant_being_fixed:
```text
raw serialized query may contain runtime-volatile lib/uuid
durable canonical identity must ignore only explicitly proven volatile lib/uuid
all non-volatile canonical fields must match exactly across repeated construct-query calls
structural semantic-slot manifest must remain identical
explicit/implicit join introduction remains forbidden
execution still uses the actual returned serialized query
```

authorized_correction:
- recursively remove only map key `lib/uuid` from decoded canonical queries for durable comparison;
- compare the two stripped decoded canonical queries exactly;
- fail if any other field differs;
- fingerprint the stripped stable canonical representation;
- retain one real serialized query for execution;
- add provider-free proof that UUID-only drift passes and any other drift fails;
- rerun the full P4 gate on pinned v0.63.18.

forbidden_patch_alternatives:
- accept arbitrary differences;
- regex/remove every field containing `uuid`;
- skip the second construct-query call;
- hash portable input instead of canonical runtime output;
- suppress live determinism proof;
- change Metabase runtime/source;
- weaken join/silent-drop checks;
- touch semantic/authority/Wren/v2 contracts.

allowed_files_to_touch:
- `backend/app/v3/substrate/metabase/canonical.py`
- `backend/tests/test_v3_p4_metabase_compiler.py`
- `backend/tests/test_v3_p4_metabase_canonical_live.py` only if proof output needs explicit stable assertions
- P4 failure/status/ticket/decision docs

status:
`CLASSIFIED / CANONICAL IDENTITY PATCH AUTHORIZED`.


---

## DMP-P4-AUDIT-003 — remove filter sentinel heuristic before P4 closure

receipt_id: `DMP-P4-AUDIT-003`  
ticket: `P4-001`  
detection: supervisor architecture audit; no CI failure required

observed_issue:
`MetabaseProjectionCompiler` currently contains a content-based rule:

```python
if ref.value.strip().lower() == "null":
    raise UNTYPED_NULL_FILTER_UNSUPPORTED
```

This treats one string token as semantically special even though `ResolvedFilterRef.value` exposes
only an untyped string equality payload.

failure_class:
`ARCHITECTURE / SEMANTIC-HEURISTIC`

root_cause:
A missing typed NULL predicate contract was guarded using input-word recognition rather than by
respecting the actual upstream contract boundary.

authorized_correction:
- remove the `"null"` sentinel branch;
- compile textual dimension values, including `"NULL"`, as literal equality strings;
- retain fail-closed behavior for non-textual dimensions with untyped string payloads;
- add regression proving `"NULL"` remains a literal string;
- add/retain architecture proof that regex/fuzzy semantic matching dependencies are absent;
- do not add any replacement sentinel table or fallback.

forbidden:
- recognizing `none`, `empty`, `unknown`, `n/a`, etc.;
- parsing typed NULL/numeric/operator semantics from strings;
- regex/fuzzy/embedding matching;
- Metabase semantic search/name fallback;
- changing the upstream filter contract inside this audit correction.

status:
`CLASSIFIED / NARROW HEURISTIC-REMOVAL PATCH AUTHORIZED`.


---

## DMP-P4-RED-004 — non-lib/uuid canonical drift remains after exact volatility stripping

receipt_id: `DMP-P4-RED-004`  
ticket: `P4-001`  
tested_sha: `428ba51845966c95baf97dcace3ca9851c85762f`  
run_id: `35752287941`

observed_failure:
The exact-key `lib/uuid` volatility correction passes focused/provider-free proof but pinned-live
canonicalization still hard-fails:

`NON_DETERMINISTIC_CANONICAL_SEMANTICS: non-volatile construct-query output changed for primary step`

classification_evidence:
- forbidden-file isolation = PASS;
- P4 production compile = PASS;
- focused P4 binding/compiler proof = PASS;
- provider-free P3A/P3/M1 regressions = PASS;
- real Wren M1 regression = PASS;
- pinned M2 lab startup = PASS;
- P3 live workflow at same SHA = SUCCESS;
- governance at same SHA = SUCCESS;
- only P4 pinned-live canonical equality = FAIL.

failure_class:
`RUNTIME-CONTRACT / CANONICAL-IDENTITY DIAGNOSTIC REQUIRED`

current_root_cause:
Unknown exact non-`lib/uuid` JSON path. No additional volatility field is authorized for
normalization until observed directly in the pinned v0.63.18 output.

single_owner:
P4 canonical proof/diagnostics.

authorized_next_step:
- add deterministic structured diff diagnostics for the already UUID-stripped JSON trees;
- report exact first differing JSON path and bounded values in the failure detail;
- rerun pinned-live P4;
- do not change equality semantics, fingerprint semantics, or volatility allowlist.

forbidden:
- strip `lib/source-uuid` or any other field based on name speculation;
- regex/generalized UUID removal;
- ignore map/list ordering;
- sort arrays;
- coerce values;
- weaken structural manifest;
- skip double construct;
- move to P5.

status:
`OPEN / DIAGNOSTIC-ONLY PATCH AUTHORIZED`.


---

## DMP-P4-RED-004 classification update — exact drift identified

diagnostic_sha: `118adca3441a8b08503cda06020679aaf39f057b`  
diagnostic_run: `35752908054`

observed_exact_difference:
```text
path   = $.stages[0].order-by[0][2][2]
first  = 59254553-ad13-4b66-9167-272a273a24b9
second = 2c05c7b5-d204-4905-b30f-91da325390b1
```

portable_source_shape:
`["aggregation", {}, 0]`

root_cause:
Pinned v0.63.18 repair resolves same-stage integer aggregation references to the target aggregation's
runtime `lib/uuid`. Because aggregation clause `lib/uuid` is freshly generated per normalization,
the corresponding aggregation-reference target is also runtime-volatile. Pinned Metabase equality
itself compares these references by mapping each side's aggregation UUID back to its stage index.

authorized_correction:
Implement only DMP-DEC-0015's exact same-stage aggregation-ref UUID -> index stabilization, followed
by existing exact-key `lib/uuid` stripping. Add negative tests proving unmatched UUID-like values
and similar-looking keys are not normalized.

status:
`ROOT CAUSE PROVEN / NARROW PATCH AUTHORIZED`.


---

## P4 closure — GREEN

final_implementation_sha: `0af815887d8e50274b39bdb7975eb37e6e63971a`  
p4_workflow: `35753630759 = SUCCESS`  
p3_workflow_same_sha: `35753630526 = SUCCESS`  
m1_workflow_same_sha: `35753630773 = SUCCESS`  
governance_same_sha: `35753630765 = SUCCESS`

```text
execution-binding single owner         PASS
parallel binding models                0

focused P4 binding/compiler            44 PASS
provider-free P3A/P3/M1                40 PASS
real Wren + retained sentinels         5 PASS
pinned-live P3/P3A/P4                  3 PASS
P4 live families                       8 / 8
P4 executable query steps              9 / 9

raw-language reinterpretation          0
canonical_name locator use             0
source_scopes locator use              0
Metabase semantic search               0

regex/fuzzy semantic resolver          0
special value sentinel semantics       0

silent source rebind                   0
implicit join                          0
explicit unauthorized join             0
silent semantic slot drop              0

lib/uuid runtime volatility            tolerated exactly
same-stage aggregation runtime ref      stabilized by proven UUID->index relation only
unmatched/other canonical volatility    HARD FAIL

stable canonical fingerprint           PASS across repeated canonicalize
actual serialized execution            PASS
current-catalog fingerprint             PASS
literal "NULL" text equality            PASS

production routing change              0
Wren retirement                        0
P5 implementation                      0
source branch write/sync                0
```

Historical closure:
- `DMP-P4-RED-001`: CLOSED GREEN;
- `DMP-P4-RED-002`: CLOSED GREEN;
- `DMP-P4-AUDIT-003`: CLOSED GREEN;
- `DMP-P4-RED-004`: CLOSED GREEN.

P4 proves only the initial supported semantic slice and canonical structured-query boundary.
It does **not** prove P5 receipt persistence/completion, final principal/access-lens parity,
P8 Wren/Metabase numeric equivalence, Metabase primary routing, or Wren retirement.

status:
`P4 CLOSED GREEN`.


---

## DMP-P5-BLOCK-001 — effective access snapshot issuer not yet proven

receipt_id: `DMP-P5-BLOCK-001`  
milestone: `P5`

observed:
P4 proves query construction/canonicalization/execution in the pinned lab, but the current branch
does not yet have a Dima-owned mechanism that proves the complete effective access lens required by
R10.1 for each official execution.

Known partial contexts:
- `ResolvedAnalyticsIntent.principal`: tenant/principal/roles;
- control-plane `Principal`: tenant/user/roles/branches;
- `TenantAnalyticsRuntimeV0`: tenant/user/roles/catalog/schema;
- P3 client: authenticated Metabase session transport;
- P4 current catalog: governed physical resource identity.

Missing proven composition:
```text
Dima execution principal
↔ authenticated substrate principal/access lens
↔ database route/effective security context
↔ policy/RLS/CLS versions
↔ security parameter digest
```

classification:
`SECURITY / ACCESS-IDENTITY PRECONDITION`

authorized:
P5A contract/sealer implementation that **requires** an externally proven access snapshot.

not_authorized:
inventing or defaulting the missing access data, or declaring P5 GREEN from lab-admin execution.

closure_condition:
P10 produces and certifies the production effective-access snapshot issuer/attestor with fail-closed
principal/tenant/security mapping.

status:
`OPEN / TRANSFERRED TO P10 SECURITY MAPPING GATE`.

P5 may close **CONTRACT GREEN** without a production issuer, but production official receipt issuance
remains prohibited until this blocker closes at P10.


---

## P5 contract closure matrix

product_implementation_sha: `c8be6720f8f0f908b3cc6459fb817d760d417c8e`  
closure_candidate_sha: `94e9b3da892a80253495324b2a256f128b037d1b`  
p5_workflow: `35759691357 = SUCCESS`  
governance: `35759691408 = SUCCESS`  
full_m1_wren: `35759329091 = SUCCESS`

```text
ExecutionAccessSnapshot complete      PASS
required security fields/defaults     PASS / NO MAGIC DEFAULTS
role order invariant                  PASS
source-ref order invariant            PASS
policy/RLS/CLS/DB/security sensitivity PASS
missing access snapshot               HARD FAIL
missing runtime identity              HARD FAIL
authority/query identity mismatch     HARD FAIL
tenant/principal/role mismatch        HARD FAIL
semantic-context mismatch             HARD FAIL
source-resource mismatch              HARD FAIL
query/result/event cardinality        HARD FAIL
stable receipt_fingerprint            PASS
new execution event -> new receipt_id PASS
result mutation -> fingerprint change PASS
comparison step receipts              PASS
ephemeral identity excluded           PASS
regex/fuzzy/morphology dependency     0
pinned-live P3/P3A/P4                 3 PASS
```

P5 contract status:
`CLOSED GREEN`.

DMP-P5-BLOCK-001 status is unchanged:
`OPEN / TRANSFERRED TO P10 SECURITY MAPPING GATE`.


---

## DMP-P5-RED-001 — receipt resource pairing and durable qualifier binding loss

receipt_id: `DMP-P5-RED-001`  
milestone: `P5`  
tested_sha: `8f283ed9da44d7b8a079fe82b37c23af863fed33`  
detection: post-closure supervisor provenance audit

observed:
The P5 sealer hashes `resource_entity_ids` and `resource_fingerprints` as independently sorted
collections. That loses the positional entity↔fingerprint association. It also stores
`warnings`, `limitations`, and `access_attestation_refs` on the receipt without binding them
into `receipt_fingerprint`.

classification:
`PROVENANCE / DURABLE RECEIPT IDENTITY`

root_cause:
Receipt content identity was modeled as independent resource columns plus core execution fields
instead of the exact resource association and all durable receipt qualifiers.

authorized_correction:
- require entity-id/fingerprint cardinality equality;
- preserve positional pairs from P4 and hash deterministically sorted pairs;
- hard-fail partial resource identity as `RESOURCE_IDENTITY_CARDINALITY_MISMATCH`;
- bind sorted attestation refs as proof-set identity;
- bind warnings/limitations exactly in supplied order;
- keep `executed_at` outside `receipt_fingerprint`;
- keep `execution_id` only in execution-occurrence `receipt_id`;
- add focused negative proofs and run P5/P4 regressions.

forbidden:
- second receipt hash abstraction;
- fuzzy/similar resource association;
- Metabase lookup/search;
- P4 compiler/canonical changes;
- Wren adapter changes;
- P10 access issuer work.

status:
`OPEN / SURGICAL P5 SEALER CORRECTION AUTHORIZED; P6 PRODUCT IMPLEMENTATION HELD`.


---

## DMP-P5-RED-001 closure

fix_sha: `e9eb74b7edf00406187fa250ceb911dc0de9e4d7`  
P5 workflow: `35763693146 = SUCCESS`  
M1/Wren workflow: `35763692416 = SUCCESS`  
governance: `35763692629 = SUCCESS`

```text
focused P5 receipt/access proofs      41 PASS
provider-free P4 critical regression  44 PASS
M1 critical regression                15 PASS
resource entity↔fingerprint pairing   bound as exact pairs
partial resource identity             HARD FAIL
attestation proof refs                bound in receipt_fingerprint
warnings/limitations                  bound exactly in supplied order
executed_at                           remains event metadata only
execution_id                          remains receipt occurrence identity
second receipt hash abstraction       0
P4 compiler/canonical changes         0
Wren adapter changes                  0
P10 issuer work                       0
```

status:
`CLOSED GREEN`.


---

## DMP-P6-RED-001 — stale M2 workflow cross-trigger on P6 lab-only files

receipt_id: `DMP-P6-RED-001`  
tested_sha: `65ef9cce522fe249ec98699c1b07b59b958ee207`  
failed_run: `35764852700` / `dima-metabase-m2`

observed:
Adding only P6-scoped files under `backend/lab/metabase/p6/**` triggered the legacy M2 workflow.
Its isolation gate compared the historical M2 base SHA to current HEAD, so already-certified later
P3/P4/P5 `backend/app/v3/**` history was reclassified as an M2 forbidden change.

classification:
`CI/GOVERNANCE SCOPE`

root_cause:
- M2 trigger glob included later milestone subdirectories;
- M2 isolation measured cumulative branch history rather than the current push/change set.

authorized_correction:
- exclude `backend/lab/metabase/p6/**` from M2 path triggering;
- retain M2 forbidden-file rules, but evaluate them against `github.event.before...HEAD`;
- on manual dispatch fallback to `HEAD^`;
- do not alter M2 runtime pins, bootstrap, restore proof, product code, P6 canary semantics or any
  P3/P4/P5 contract.

proof_required:
the corrective M2 workflow self-run must pass isolation and the P6A workflow on the unchanged P6
candidate remains independently classified.

status:
`OPEN / CI OWNER CORRECTION AUTHORIZED`.


---

## DMP-P6-RED-002 — P6A Wren PostgreSQL harness used psycopg field names

receipt_id: `DMP-P6-RED-002`  
tested_sha: `65ef9cce522fe249ec98699c1b07b59b958ee207`  
failed_run: `35764852696` / P6A same-snapshot canary

observed:
P6A provider-free proof, shared PostgreSQL startup, deterministic seed, Metabase health and bootstrap
all passed. The live canary failed before the first Wren query while validating connection info.

exact_failure:
`PostgresConnectionInfo` validation reported required field `database` missing.

source_evidence:
- Wren `DataSource.postgres` validates raw connection dicts as `PostgresConnectionInfo`;
- `PostgresConnectionInfo` requires `host, port, database, user`;
- the P6 harness reused psycopg kwargs, which correctly use `dbname`, for Wren as well.

classification:
`DATA/FIXTURE_GAP / HARNESS CONNECTION CONTRACT`

root_cause:
One connection dictionary was incorrectly shared across two libraries with different typed field
names. No semantic, compiler, runtime, or database-content mismatch was observed.

authorized_correction:
- keep psycopg kwargs with `dbname`;
- create a separate exact Wren connection dict with `database`;
- add provider-free contract proof using `DataSource.postgres.get_connection_info`;
- rerun the unchanged three-case same-snapshot canary.

forbidden:
- dependency pin changes;
- Wren adapter/source changes;
- semantic reinterpretation;
- raw-SQL Metabase bypass;
- changing fixture expected values to force GREEN.

status:
`OPEN / HARNESS CORRECTION AUTHORIZED`.


### DMP-P6-RED-001 corrective-attempt addendum

Corrective SHA `bf3a0fdf3d26489cd9d5c57d5815d6dfdaf5b0eb` attempted to scope M2 CI but
the workflow text transformation malformed `.github/workflows/dima-metabase-m2.yml`, producing
run `35765097935` with no executable jobs.

This is a patch-construction defect, not an M2/P6 product failure.

Authorized repair:
restore the complete known-good M2 workflow body, retain immutable runtime/bootstrap/restore proof,
exclude only `backend/lab/metabase/p6/**` from the M2 path trigger, and evaluate forbidden-file
isolation against the current push diff rather than cumulative post-M2 branch history.

DMP-P6-RED-001 remains OPEN until the repaired M2 self-run is GREEN.


---

## DMP-P6-RED-001 closure

final_corrective_sha: `5f64379c28187d021f9bb7a813bb678ce60f5174`  
m2_workflow: `35765566147 = SUCCESS`

Proof:
- complete M2 workflow body restored;
- immutable runtime pins unchanged;
- bootstrap/backup/restore proof unchanged;
- `backend/lab/metabase/p6/**` no longer cross-triggers M2;
- isolation checks the current change set instead of cumulative post-M2 branch history.

Nuance:
the repaired current M2 self-run proves the workflow still functions after scope correction. It does
not replace the original sealed historical M2 isolation certification.

status:
`CLOSED GREEN`.

---

## DMP-P6-RED-002 closure

final_corrective_sha: `5f64379c28187d021f9bb7a813bb678ce60f5174`  
p6_workflow: `35765566189 = SUCCESS`

Proof:
- psycopg harness uses `dbname`;
- Wren PostgresConnectionInfo uses `database`;
- typed `DataSource.postgres` validation passes;
- deterministic shared PostgreSQL seed passes;
- Wren and Metabase both reach the exact P6 physical snapshot;
- 3-case lower-level live canary passes against independent fixture anchors.

status:
`CLOSED GREEN`.

---

## DMP-P6-AUDIT-003 — P6A0 connectivity proof is not yet substrate-seam parity

receipt_id: `DMP-P6-AUDIT-003`  
tested_sha: `5f64379c28187d021f9bb7a813bb678ce60f5174`

observed:
The current P6 live canary executes Wren with three hand-authored SQL statements while the Metabase
arm executes a Dima `ResolvedAnalyticsIntent` through the production compiler/canonicalizer.

classification:
`EVAL_ORACLE / HARNESS ARCHITECTURE OVERCLAIM`

what P6A0 proves:
- same physical PostgreSQL snapshot;
- same deterministic snapshot checksum;
- Wren reaches and queries that snapshot;
- Metabase reaches and queries that snapshot;
- independent golden values agree.

what it does not prove:
- same `ResolvedAnalyticsIntent` reaches both engines;
- existing `WrenSubstrateAdapter` executes the fixture;
- production thin `MetabaseSubstrateAdapter` executes the fixture;
- receipt/provenance parity.

required_next_gate:
`P6A1 — TRUE SUBSTRATE-SEAM CANARY` with exactly CANARY-01 metric,
CANARY-02 metric+breakdown, CANARY-03 metric+absolute-period.

forbidden:
- modifying `backend/app/v3/substrate/wren.py`;
- custom ResolvedIntent→Wren SQL compiler;
- raw prompt input;
- fuzzy/regex/synonym semantic binding;
- fake Metabase projection for Wren receipts;
- freezing the 80-case corpus before P6A1 resolves.

status:
`OPEN / P6A1 AUTHORIZED`.


---

## DMP-P6-RED-004 — dormant P6 governance seal predicate activated stale review wording

receipt_id: `DMP-P6-RED-004`  
tested_sha: `28c4ca6525bbde0193901362b1d70c92ffc0347f`  
failed_run: `35768149721`

observed:
P6A1 added the first production `execution_adapter.py`, activating the governance guard that requires
a sealed P6 predevelopment review. The guard still searched for the earlier authorization wording
`CORPUS FREEZE + PARITY HARNESS AUTHORIZED`, while the review status line had evolved to
`P6A SAME-SNAPSHOT CANARY NEXT`.

classification:
`CI/GOVERNANCE SEAL-TOKEN DRIFT`

root_cause:
The P6 guard was dormant before parity product code existed, so stale exact status wording was not
exercised by prior GREEN governance runs.

authorized_correction:
Use a semantically accurate status line that preserves the existing sealed-authorization token while
making the P6A1 prerequisite explicit:
`SEALED / CORPUS FREEZE + PARITY HARNESS AUTHORIZED AFTER P6A1 GREEN`.

No product code, semantic contract, adapter behavior, corpus, or workflow logic changes are authorized
under this receipt.

status:
`CORRECTION APPLIED / AWAITING GOVERNANCE GREEN`.


---

## DMP-P6-GAP-005 — Wren compatibility seam cannot represent absolute period intent

receipt_id: `DMP-P6-GAP-005`  
tested_product_sha: `28c4ca6525bbde0193901362b1d70c92ffc0347f`  
p6_run: `35768149802`

observed:
P6A0 shared snapshot/golden proof remains GREEN. P6A1 reaches the real Wren substrate validation
boundary and fails before execution because CANARY-03 carries
`ResolvedPeriod(kind="absolute", start="2026-01-01", end="2026-01-31")`.

Exact compatibility evidence:
- `WrenSubstrateAdapter._period()` converts with `PeriodKind(value.kind)`;
- current V2 `PeriodKind` supports `this_* / previous_* / last_n_*`;
- `absolute` is not a valid V2 PeriodKind;
- adapter therefore returns `unsupported Wren period kind: absolute`.

classification:
`TYPED_GAP / WREN_COMPATIBILITY_GAP`

owner:
current Wren compatibility contract, not P6 harness, not Metabase compiler, not data snapshot.

not_a_failure_of:
- shared PostgreSQL fixture;
- Metabase execution;
- P4 compiler/canonicalization;
- P5 receipt contract;
- Wren runtime connectivity.

P6 rule:
Do not modify `backend/app/v3/substrate/wren.py` to make the canary green.
The harness must execute supported cases and report this unsupported semantic shape as a typed gap.

status:
`OPEN GAP / MEASUREMENT MUST REPORT; NO P6 PRODUCT PATCH AUTHORIZED`.


---

## DMP-P6-GAP-006 — WrenService PostgreSQL timeout kwargs violate installed Wren typed contract

receipt_id: `DMP-P6-GAP-006`  
tested_sha: `d317ea9370270e2381fde1d06a54c90aa4cbb339`  
failed_run: `35768689486`

observed:
P6A0 remains GREEN and provider-free P6A1 remains GREEN. CANARY-01 reaches the existing
`WrenSubstrateAdapter -> CubePlanner -> WrenService.dry_plan -> WrenEngine` production path and
fails constructing the engine.

exact_failure:
```text
PostgresConnectionInfo
kwargs.connect_timeout
Input should be a valid string
input_value=15
input_type=int
```

source_owner:
`WrenService._zaman_asimli_baglanti()` injects PostgreSQL
`kwargs["connect_timeout"] = min(timeout, 15)` as an integer.

existing_test_gap:
`backend/tests/test_sorgu_zaman_asimi.py::test_POSTGRES_baglanti_zaman_asimi_kisaltilir`
asserts the intermediate dictionary contains integer `15`, but does not prove that the produced
dictionary is accepted by `DataSource.postgres / PostgresConnectionInfo / WrenEngine`.

classification:
`TYPED_GAP / SUBSTRATE_RUNTIME_GAP`

why_not_patched_in_P6:
P6 is a measurement milestone. Fixing WrenService or its timeout test merely to improve parity would
change the measured Wren substrate. The defect needs a separately owned runtime correction outside
the P6 measurement patch set.

P6 measurement rule:
- CANARY-01/02 may report `SUBSTRATE_RUNTIME_GAP` when this exact typed engine-construction failure occurs;
- CANARY-03 remains `WREN_COMPATIBILITY_GAP` because absolute period fails earlier at intent validation;
- Metabase still must execute each supported canary and match the independent golden anchor;
- any different Wren exception remains unexplained and RED.

status:
`OPEN GAP / OWNER = WREN RUNTIME CONTRACT; NO P6 PRODUCT PATCH AUTHORIZED`.


---

## DMP-P6-AUDIT-007 — known-gap fossilization oracle

receipt_id: `DMP-P6-AUDIT-007`  
tested_sha: `e19ee7614ea39b6cab61b839252e4ecd44fe25e4`

observed:
The P6A1 evaluator required the currently observed defects as fixed expected outcomes:
CANARY-01/02 had to be `SUBSTRATE_RUNTIME_GAP` and CANARY-03 had to be
`WREN_COMPATIBILITY_GAP`.

classification:
`EVAL_ORACLE`

risk:
A future legitimate fix would improve a case from `TYPED_GAP` to `MATCH` but make the P6 CI fail,
thereby fossilizing defects.

authorized_correction:
- CANARY-01/02 accept either semantic `MATCH` or the exact structurally classified
  `SUBSTRATE_RUNTIME_GAP`;
- CANARY-03 accepts either semantic `MATCH` or the exact
  `WREN_COMPATIBILITY_GAP`;
- a MATCH must still equal the independent golden oracle;
- receipt/provenance remains an independent dimension and may be MATCH or exact
  `RECEIPT/PROVENANCE_GAP`;
- any other validation failure, runtime exception, gap class or result mismatch remains RED;
- keep the exact pydantic runtime classifier; no message substring/regex/catch-all classification.

status:
`CORRECTION APPLIED / AWAITING FINAL FOCUSED P6 WORKFLOW`.


---

## P6 targeted parity probe closure — GREEN measurement / typed gaps carried forward

closure_sha: `03912a8702b27eca634e8411b151acdd56491d2c`  
final_p6_workflow: `35771661991 = SUCCESS`  
governance: `35771661812 = SUCCESS`

P6A0:
- shared physical snapshot = PASS;
- deterministic snapshot identity = PASS;
- independent golden total/breakdown/January anchors = PASS.

P6A1:
- same accepted intent identity is presented to both substrate seams = PASS;
- thin Metabase real execution seam = PASS;
- existing Wren real substrate seam attempted = PASS;
- CANARY-01 = exact `SUBSTRATE_RUNTIME_GAP`;
- CANARY-02 = exact `SUBSTRATE_RUNTIME_GAP`;
- CANARY-03 = exact `WREN_COMPATIBILITY_GAP`;
- unknown/unexplained mismatch = 0.

Oracle:
DMP-P6-AUDIT-007 is CLOSED. The evaluator now accepts future improvement to MATCH and recognizes only
the exact already-receipted typed gaps; every other outcome remains RED.

Interpretation:
`P6 MEASUREMENT GREEN / WREN-METABASE PARITY INCOMPLETE WITH TYPED GAPS`.

No claim of engine equivalence is made. Broad cross-engine certification is deferred by DMP-DEC-0020.

Carried debt:
- `WREN_POSTGRES_CONNECT_TIMEOUT_TYPE_DEBT` -> P8 or earliest genuine Wren PostgreSQL owner;
- absolute-period temporal representation -> P7/P8 semantic-equivalence analysis;
- receipt/provenance differences -> later genuine provenance owner; no fake Metabase projection for Wren.

status:
`P6 TARGETED PARITY PROBE CLOSED`.


---

## P7 structured semantic importer closure — GREEN baseline / typed gaps explicit

implementation_sha: `2e233ea6122c9cc0ccc18ebe2978e2e896ebb41c`  
p7_workflow: `35772646640 = SUCCESS`  
governance: `35772646510 = SUCCESS`  
m1_wren_regression: `35772646558 = SUCCESS`

proof:
- final composed MDL -> DimaSemanticSpec import is deterministic;
- formulas are preserved opaque, never regex/SQL-text parsed;
- exact model/table/column lineage is imported where structurally present;
- final-composed override changes alter semantic fingerprints deterministically;
- aliases, units, additivity and time dimensions are preserved from explicit structured fields;
- relationships without structured join keys are typed gaps, not guessed;
- calculated dimensions/model columns/views/cube semantic entity debt is explicit;
- no Metabase search, fuzzy matching, morphology, raw prompt or source-branch inheritance.

interpretation:
`P7 MIGRATION BASELINE GREEN / LOSSLESS EQUIVALENCE NOT CLAIMED`.

status:
`P7 CLOSED FOR INITIAL CANONICAL IMPORT; P8 EQUIVALENCE MATRIX NEXT`.


---

## P8 semantic equivalence matrix closure — GREEN

implementation_sha: `23480aa433ba10fed84a015a85c9f1d88b31572e`  
p8_workflow: `35773470252 = SUCCESS`  
governance: `35773470111 = SUCCESS`  
m1_wren_regression: `35773470027 = SUCCESS`

proof:
- focused equivalence matrix = 14 PASS;
- P7 structured importer regression = 8 PASS;
- deterministic matrix ordering/fingerprint = PASS;
- exact physical dimension/time native classification = PASS;
- explicit mechanical metric native fixture = PASS;
- opaque formula metric remains `WREN_ONLY_GAP`;
- structured relationship fixture = `DIMA_COMPILED`;
- security/cube semantic ownership gaps = `DIMA_RUNTIME`;
- relationship/calculated/view representation gaps = `WREN_ONLY_GAP`;
- unknown gap code = HARD RED;
- formula SQL parsing / fuzzy / regex / Metabase discovery = 0.

interpretation:
`P8 EQUIVALENCE MATRIX GREEN / WREN REMOVAL NOT AUTHORIZED`.

status:
`P8 CLOSED; P9 SEMANTIC RESOURCE PROVISIONER NEXT`.


---

## DMP-P7-AUDIT-001 — structured source-field coverage

receipt_id: `DMP-P7-AUDIT-001`  
tested_sha: `c650ee1a9257d892b2b402ac2f3b1d687f54b8da`

classification:
`SEMANTIC MIGRATION COVERAGE`

observed:
The P7 importer was structurally safe but did not account for every non-empty structured field in the
current composed MDL. Material metadata such as metric directionality/type/NL hints, sensitivity,
grain/key markers, relationship cardinality/expose metadata and cube domain/PVM metadata could be
present without a consumed/gap/non-semantic disposition.

authorized correction:
Introduce an exact-key structured-field coverage contract. Every non-empty source field must be:
`CONSUMED`, `GAP_OWNED`, or `IGNORED_OPERATIONAL_METADATA`.
Unknown non-empty fields become `UNMAPPED_STRUCTURED_FIELD`.

No field content is interpreted. Formula/join-condition parsing, fuzzy matching and name inference
remain forbidden.

status:
`CORRECTION APPLIED / AWAITING P7+P8 GREEN`.


---

## DMP-P9-AUDIT-002 — stale Dima-managed resource lifecycle

receipt_id: `DMP-P9-AUDIT-002`  
tested_sha: `c650ee1a9257d892b2b402ac2f3b1d687f54b8da`

classification:
`RESOURCE LIFECYCLE / DESIRED-STATE RECONCILIATION`

observed:
`ProvisionActionKind.RETIRE_STALE` existed, but P9A built actions only by iterating current desired
resources. A previously bound DIMA-managed resource whose semantic disappeared from desired state
therefore produced no action and could survive indefinitely.

Additional hardening:
- matching payload fingerprints alone were sufficient for NOOP even when binding semantic context or
  applied version drifted;
- the ProvisionAction model documented rollback for mutating actions but did not enforce it.

authorized correction:
- reconcile current-tenant DIMA-managed inventory entries absent from desired;
- removed semantic -> RETIRE_STALE + exact previous-binding rollback;
- semantic still present but non-provisionable -> REJECT_DRIFT;
- ownership transfer/policy removal -> REJECT_DRIFT;
- enforce context/version coherence before NOOP;
- require rollback for every mutating action in model validation;
- add one real composed P7→P8→explicit policy→P9 provider-free proof.

No Metabase write transport is authorized by this receipt.

status:
`CORRECTION APPLIED / AWAITING P9A GREEN`.


---

## DMP-P9-AUDIT-002 closure — GREEN

final_sha: `7820ac77207f4245da150a5c80043d22708b87f0`  
p9_workflow: `35778418835 = SUCCESS`  
m1_wren: `35778418797 = SUCCESS`  
governance: `35778418759 = SUCCESS`

proof:
- removed semantic -> RETIRE_STALE with previous-binding rollback;
- semantic still present but no longer provisionable -> REJECT_DRIFT;
- ownership transfer / removed management policy -> explicit REJECT_DRIFT;
- matching payload does not NOOP across context/applied-version drift;
- every mutating ProvisionAction requires a rollback descriptor by model validation;
- external locator coherence remains exact; no name fallback or same-name adoption;
- real composed P7→P8→explicit Dima managed policy→P9 produces one deterministic CREATE with rollback.

status:
`CLOSED GREEN`.


---

## DMP-P9B-RED-001 — P9B1 negative-oracle precedence + anti-SQL false positive

receipt_id: `DMP-P9B-RED-001`  
tested_sha: `606f89aee8f31c4c866669dbc6efb64dfa58d9d9`  
failed_run: `35780048833`

classification:
`CONTRACT ERROR PRECEDENCE + TEST ORACLE`

observed:
- invalid multi-step/breakout/filter/time/ranking projections were correctly rejected, but the builder
  checked full semantic-id equality before query structural shape, so tests observed the more general
  `P9B1_PROJECTION_SEMANTIC_ID_MISMATCH` instead of the exact structural owner;
- anti-SQL source assertion rejected Python `from ... import` syntax because it searched raw source
  for the substring `"from "`.

root_cause:
Fail-closed behavior was intact, but diagnostic precedence was less specific than the P9B1 contract,
and one test oracle used a language-agnostic raw substring.

authorized correction:
- validate query cardinality/role/shape before semantic-id equality;
- retain semantic-id equality as a hard gate for structurally admissible queries;
- remove the ambiguous raw `"from "` substring assertion while keeping AST import bans and explicit
  SQL/parser/search dependency bans.

No HTTP write, query compiler, semantic expansion or fallback is authorized.

status:
`CORRECTION APPLIED / AWAITING P9B1 GREEN`.


---

## DMP-P9B-RED-001 closure — GREEN

final_sha: `aa461134ddb044798be6275f7dc68d3979aff810`  
p9b_workflow: `35780384430 = SUCCESS`  
governance: `35780384123 = SUCCESS`  
m1_wren: `35780384142 = SUCCESS`

proof:
- invalid query shape is rejected before semantic-id equality so the exact structural owner is visible;
- anti-SQL test no longer mistakes Python import syntax for SQL;
- focused P9B1 = 13 PASS;
- inherited P7/P8/P9 = 62 PASS;
- no semantic special case, regex workaround, fallback, query rewriting or HTTP write was added.

status:
`CLOSED GREEN`.

---

## DMP-P9B-AUDIT-002 — transport tenant identity and projection provenance

receipt_id: `DMP-P9B-AUDIT-002`  
tested_sha: `aa461134ddb044798be6275f7dc68d3979aff810`

classification:
`RESOURCE TRANSPORT IDENTITY / PROVENANCE`

observed:
P9A desired identity is tenant-scoped, but P9B1 `MetricCreateTarget` and
`MetricCreateContract` omitted `tenant_binding`. The contract also persisted only the canonical
query fingerprint from P4, omitting the enclosing `projection_hash`,
`resolved_intent_hash`, and `current_catalog_fingerprint`.

risk:
Two otherwise identical resource requests from different tenants, or the same query bytes under a
different certified projection/catalog state, could collapse to the same transport-contract identity.

authorized correction:
- require `MetricCreateTarget.tenant_binding`;
- hard-fail target/desired tenant mismatch as `P9B1_TARGET_TENANT_MISMATCH`;
- persist `tenant_binding`, `projection_hash`, `resolved_intent_hash`, and
  `current_catalog_fingerprint` in `MetricCreateContract`;
- include those exact existing identities in `contract_fingerprint`;
- keep collection explicit;
- no tenant discovery, collection search, default root/personal collection or P10 permission logic.

status:
`CORRECTION APPLIED / AWAITING PROVIDER-FREE P9B1 GREEN`.


---

## DMP-P9B-AUDIT-002 closure — PROVIDER-FREE GREEN

final_sha: `33c93fa3cd579e9d2e42eef0335215747183590c`  
p9b_workflow: `35782035041 = SUCCESS`  
governance: `35782035058 = SUCCESS`  
m1_wren: `35782035064 = SUCCESS`

proof:
- focused P9B1 = 18 PASS;
- inherited P7/P8/P9 = 62 PASS;
- target tenant is explicit and must equal desired-resource tenant;
- transport contract carries tenant, projection hash, resolved-intent hash, catalog fingerprint and
  canonical-query fingerprint;
- tenant/projection/catalog provenance changes transport contract fingerprint;
- no collection search/default, tenant discovery, HTTP write, P10 permission mapping or semantic
  reinterpretation added.

status:
`CLOSED GREEN / ONE ISOLATED PINNED-LIVE METRIC LIFECYCLE AUTHORIZED`.


---

## DMP-P9B-RED-003 — archived Card GET presents Trash collection identity

receipt_id: `DMP-P9B-RED-003`  
tested_sha: `9f33d9f97faa331666a12fa2382fdb649a7481a2`  
workflow: `35782467824`

classification:
`LIVE TEST ORACLE / PINNED READ REPRESENTATION`

observed:
The isolated lifecycle passed metric create, exact-id read-back, stable entity binding, P9 replanning
to NOOP and archive mutation. It failed only because the archived exact-id GET was asserted to retain
the original collection id.

pinned-source evidence:
Metabase v0.63.18 Card GET applies `present-in-trash-if-archived-directly`, which deliberately
presents directly archived Cards with the Trash collection id. The underlying lifecycle identity
remains the exact Card id/entity id.

authorized correction:
- archived exact-id read must still prove id/type/name/entity_id and `archived=true`;
- do not require original collection while directly archived;
- after restore, original explicit collection id is required again;
- entity_id must remain stable across create/archive/restore;
- no product transport, semantic, P9 planner or API behavior changes.

status:
`ORACLE CORRECTION APPLIED / ONE CORRECTED PINNED-LIVE RERUN AUTHORIZED`.


---

## DMP-P9B-RED-003 closure — GREEN

final_sha: `d3f4bb8b8aa9a65796506193632f7c429eac8d7c`  
p9b_workflow: `35782974669 = SUCCESS`  
governance: `35782974647 = SUCCESS`  
live_test: `1 PASS`

proof:
- pinned Metabase v0.63.18 health/bootstrap = PASS;
- fresh P4 projection -> tenant-bound P9B metric-create contract = PASS;
- exact metric create response numeric id captured;
- exact-id Card read proves id/type/name/explicit collection/entity_id;
- Dima canonical binding captures numeric id + stable entity_id;
- observed snapshot + binding replans to P9 `NOOP`;
- exact-id archive -> read proves archived state and stable entity_id;
- archive Trash collection presentation handled according to pinned source;
- exact-id restore -> read proves original explicit collection restored and entity_id stable;
- exact-id hard-delete cleanup = PASS;
- no search, list scan, name adoption, generic CRUD product client or production route change.

interpretation:
`P9B METRIC TRANSPORT PROOF GREEN IN ISOLATED LAB`.

This authorizes no customer/production write. Dimension/time/relationship transport gaps remain open.
P10 security issuer gate is now the next architecture owner.

status:
`CLOSED GREEN`.


---

## P10A provider-free access snapshot issuer — GREEN

implementation_sha: `1abf43657453a771954a939de834e6b48f55620e`  
p10_workflow: `35783766213 = SUCCESS`  
governance: `35783766051 = SUCCESS`  
m1_wren: `35783766157 = SUCCESS`

proof:
- focused P10A = 20 PASS;
- inherited P5 identity + P9B transport = 59 PASS;
- current principal / accepted intent / canonical projection / verified facts mismatch paths fail closed;
- source-object identity is exact;
- security-lens changes alter the existing P5 execution-access fingerprint;
- VerifiedExecutionSecurityFacts has no competing fingerprint and no session token/secret field;
- P5 ExecutionAccessSnapshot remains the only durable access identity.

status:
`P10A CONTRACT GREEN / DMP-P5-BLOCK-001 STILL OPEN`.


---

## DMP-P10-AUDIT-001 — current OSS lab cannot prove advanced row/column/impersonation lens

receipt_id: `DMP-P10-AUDIT-001`  
classification: `SECURITY CAPABILITY / LAB TOPOLOGY`

evidence:
- current pinned lab image is OSS `metabase/metabase@sha256:1160...8a73`;
- v0.63.18 `enable-sandboxes?` is a premium feature gate;
- v0.63.18 `enable-advanced-permissions?` gates block access / connection impersonation;
- OSS permission-graph augmentation returns no sandbox/impersonation state;
- blocked view-data validation requires advanced-permissions;
- basic `create-queries` permission and authenticated current-user identity are available in OSS.

decision:
Do not fake row restriction, CLS or impersonation with Dima role labels.

P10B is split:
- P10B1: isolated OSS proof for exact Metabase current-user attestation, basic query permission
  revocation, same-session denial, no admin fallback, restore;
- P10B2: real row/column/impersonation/database-route lens proof using an actually capable security
  owner/runtime.

DMP-P5-BLOCK-001 remains open until P10B2 (or an equivalent faithful DB-native security owner) is
proven.

status:
`P10B1 AUTHORIZABLE / P10B2 CAPABILITY GAP OPEN`.


---

## DMP-GOV-RED-001 — authorized DMP-DEC-0026 normative amendment invalidated old blob pins

receipt_id: `DMP-GOV-RED-001`  
tested_sha: `4363a9604483aee5c8029bb6a6447bda34b42eaf`  
failed_run: `35786752576`

classification:
`GOVERNANCE / EXPECTED SEALED-BLOB PIN UPDATE`

observed:
DMP-DEC-0026 explicitly authorized surgical amendments to the current architecture report and roadmap.
The governance workflow correctly rejected those changed blobs because it still pinned the pre-0026
hashes.

diff audit:
- architecture report changes are limited to R2.2, R3.10, R6, R8 and R17;
- roadmap changes are limited to P11, P15, P17, P19, P39 and P41;
- sealed historical milestone receipts were not rewritten;
- product/runtime code changed = 0.

authorized correction:
advance only the two governance blob pins to the reviewed DMP-DEC-0026 versions:
- report blob `aa5f3e048dea56ec52110023e7399fc1fe957805`;
- roadmap blob `01d1893bf85a482f5970d27ec70a60df7b836219`.

status:
`CORRECTION APPLIED / AWAITING GOVERNANCE GREEN`.


---

## DMP-GOV-RED-001 closure — GREEN

final_sha: `e6b8d98190369b010cf8dcd743fdc3d4ece645c0`  
governance: `35786915071 = SUCCESS`  
p10a_provider_free_on_docs_sha: `35786752567 = SUCCESS`

proof:
- reviewed DMP-DEC-0026 report and roadmap blobs are pinned by governance;
- certified-base ancestry remains intact;
- mandatory governance files and prior sealed milestone guards remain GREEN;
- product/runtime code changed by the normative amendment = 0;
- historical sealed P6-P10 receipts rewritten = 0.

status:
`CLOSED GREEN`.


---

## DMP-P11-MEASURE-001 — EV-03 persistent multi-scope silent bind

tested_sha: `977faa99cdf6581ce02c13b55add4077750fe540`  
workflow: `35789082927 = SUCCESS`  
artifact: `p11-luna-sol-eval / 10721845683`  
corpus_fingerprint: `da7f13e804c643c376d085b0e0fa94e132fdd8877e1945e4c19257160d03e06c`

frozen setup:
- pinned Metabase `v0.63.18 / 2ba2485c78d7e00a9a25f82c00fc201da71590c4`;
- restricted current-user FieldValues retrieval;
- same dataset, scopes, evidence envelope, prompt and structured output contract for both models;
- Luna runtime/requested id = `openai/gpt-5.6-luna`;
- Sol runtime/requested id = `openai/gpt-5.6-sol`.

first-pass result:
- EV-01 exact categorical: Luna PASS / Sol PASS;
- EV-02 cross-language `Kuzey -> North`: Luna PASS / Sol PASS;
- EV-03 unresolved region-vs-customer semantic scope: Luna SILENT BIND / Sol SILENT BIND;
- EV-04 missing `Central`: Luna NO_MATCH PASS / Sol NO_MATCH PASS.

variance repeats:
- Luna EV-03: BIND, BIND, CLARIFY -> 2 silent wrong occurrences;
- Sol EV-03: BIND, BIND, BIND -> 3 silent wrong occurrences;
- total silent wrong = 5;
- security/truth-critical majority vote = NOT APPLICABLE.

cost/latency including repeats:
- Luna: 6 calls, 3531 tokens, 21.273 s aggregate provider latency, USD 0.0015242;
- Sol: 6 calls, 3183 tokens, 14.941 s aggregate provider latency, USD 0.0101260;
- total: 12 calls, 6714 tokens, 36.214 s, USD 0.0116502.

classification:
`MATERIAL_TRUTH_GAP / UNRESOLVED_SEMANTIC_SCOPE_ADOPTION`.

root cause:
The cognition model was allowed to make a final value BIND while the upstream value-binding request
still carried more than one admissible semantic scope. Both model classes optimized toward the exact
`North` region value instead of preserving the unresolved business-scope ambiguity.

This is not evidence for a deterministic entity resolver, translation table, fuzzy matcher or
analytical planner. EV-02 already proves the LLM can perform cross-language cognition without such
machinery. EV-04 proves it can reject a missing value.

required next:
A minimum deterministic adoption gate must prevent a model BIND from becoming authority while the
semantic scope itself remains unresolved/multi-scope. The same frozen corpus must then be rerun without
prompt/case/tool/data changes.

status:
`MEASURED / MINIMUM GUARDRAIL CANDIDATE`.


---

## DMP-P11-CI-RED-001 — M2 stale cross-trigger on P11 lab files

tested_sha: `d31b83437400dd7f1b70e1b478efad2e8cff781e`  
failed_run: `35790011814`

classification:
`CI / MILESTONE CROSS-TRIGGER`.

observed:
The M2 workflow path filter still watched all `backend/lab/metabase/**` except P6. The P11 eval
harness therefore triggered M2. M2's own isolation gate then correctly rejected the same commit's
`backend/app/v3/entity_value_gate.py`, even though M2 neither owns nor needs P11 product code.

evidence:
- failure occurs at `Enforce M2 forbidden-file isolation` before runtime bootstrap;
- P11 provider-free = GREEN;
- P11 live = GREEN;
- governance = GREEN;
- full M1/Wren regression = GREEN;
- an immediately preceding P11 freeze-only commit triggered M2 and completed full M2 smoke GREEN.

authorized correction:
Exclude `backend/lab/metabase/p11/**` from the M2 push path trigger, exactly as P6 lab files are
already excluded. M2's own workflow file remains a trigger so M2 can self-validate this correction.

No product code or M2 runtime behavior changes are authorized.

status:
`CORRECTION APPLIED / AWAITING M2 GREEN`.

---

## DMP-P11-MEASURE-001 closure — minimum adoption gate sufficient

implementation_sha: `d31b83437400dd7f1b70e1b478efad2e8cff781e`  
workflow: `35790011788 = SUCCESS`  
artifact: `p11-luna-sol-eval / 10721593598`  
corpus_fingerprint: `da7f13e804c643c376d085b0e0fa94e132fdd8877e1945e4c19257160d03e06c`

same frozen contract:
- cases/data/tool evidence/prompt/model ids/oracle unchanged;
- Luna runtime = `openai/gpt-5.6-luna`;
- Sol runtime = `openai/gpt-5.6-sol`;
- 8 primary evaluations; EV-03 raw failure repeats retained;
- 12 total model calls.

post-guardrail:
- raw first-pass Luna = 3/4;
- raw first-pass Sol = 3/4;
- official first-pass Luna = 4/4;
- official first-pass Sol = 4/4;
- raw silent-wrong occurrences = 6;
- official silent-wrong occurrences = 0;
- EV-03 official outcome on every attempt = `CLARIFY / AMBIGUOUS_SEMANTIC_SCOPE`;
- EV-01/02 safe exact binds remain BIND;
- EV-04 remains NO_MATCH.

cost/latency including raw-failure repeats:
- Luna: 6 calls, 3472 tokens, 18.560 s aggregate provider latency, USD 0.0014534;
- Sol: 6 calls, 3125 tokens, 11.025 s aggregate provider latency, USD 0.0095460;
- total: 12 calls, 6597 tokens, 29.585 s, USD 0.0109994.

architecture value delta:
- verified official first-pass: 6/8 -> 8/8;
- official silent wrong: baseline 5 observed -> 0 on rerun;
- raw model cognition is not hidden and still demonstrates the same failure family;
- model calls added by guardrail = 0;
- model/prompt/tool specialization added = 0;
- new permanent product mechanism = one pure adoption gate;
- new semantic resolver/search/translation/fuzzy state = 0.

classification:
`MINIMUM_GUARDRAIL SUFFICIENT / DETERMINISTIC ENTITY RESOLVER NOT NEEDED FOR P11 V1`.

scope:
This closes only the initial EV-01..EV-04 native-path family. EV-05 high-cardinality, EV-06 stale
index and EV-07 permission-hidden remain explicitly uncertified and blocked on their real fixtures/
security owners.

status:
`P11 INITIAL NATIVE PATH GREEN`.


---

## DMP-P11-AUDIT-003 — P11 product-gate focused test family absent from P11 CI proof

receipt_id: `DMP-P11-AUDIT-003`  
tested_sha: `91333d39e63c245b637a4d2be2e49a5a227271c7`

classification:
`CI / PROOF COMPLETENESS`

observed:
The P11 provider-free job compiled and executed only the frozen necessity-contract family. The
product mechanism authorized by DMP-DEC-0027, `EntityValueAdoptionGate`, had its own focused unit
tests but that family was not executed by the P11 workflow.

authorized correction:
- compile `app/v3/entity_value_gate.py`;
- compile both P11 test files;
- execute `test_v3_p11_necessity_contract.py` and `test_v3_p11_entity_value_gate.py` together;
- no model rerun;
- no new product behavior except the separately classified AUDIT-004 comparator correction.

status:
`CORRECTION APPLIED / AWAITING PROVIDER-FREE GREEN`.

---

## DMP-P11-AUDIT-004 — scalar type-crossing equality in exact value adoption

receipt_id: `DMP-P11-AUDIT-004`  
tested_sha: `91333d39e63c245b637a4d2be2e49a5a227271c7`

classification:
`TRUTH GATE / EXACT SCALAR IDENTITY`

observed:
The gate used Python value equality directly. In the declared scalar domain,
`True == 1`, `False == 0`, and `1 == 1.0`, so "EXACT_CURRENT_LENS_EVIDENCE" was not
type-strict.

authorized correction:
Exact adoption requires both:
`type(proposed) is type(candidate)` and `proposed == candidate`.

Forbidden:
- stringify;
- numeric coercion;
- casefold/lower;
- fuzzy/similarity;
- model rerun;
- corpus/prompt/tool changes.

required negatives:
- evidence int 1 / proposal bool True -> BLOCK;
- evidence bool True / proposal int 1 -> BLOCK;
- evidence float 1.0 / proposal int 1 -> BLOCK;
- evidence int 1 / proposal float 1.0 -> BLOCK;
- existing `North` vs `north` exactness remains.

status:
`CORRECTION APPLIED / AWAITING PROVIDER-FREE GREEN`.

---

## DMP-P11-INTEGRATION-005 — production entity-value evidence access binding

owner:
`P13 Production Standard integration`

requirement:
Before `EntityValueAdoptionGate` is wired into the production Standard path:
- `allowed_semantic_scopes` must originate from accepted Dima semantic authority / governed binding,
  not from the same cognition model's unsupported assertion;
- current-lens value evidence must originate from the governed P11 retrieval path;
- evidence access identity must bind to the owning P5/P10
  `ExecutionAccessSnapshot.execution_access_fingerprint`;
- no new parallel access fingerprint may be invented;
- semantic context / source resource / retrieval receipt may be bound when the P13 seam requires them;
- the literal freshness state `CURRENT_USER_RETRIEVAL` is a claim and does not itself confer authority.

This is a forward integration requirement. It does not reopen P11 V1 or authorize a large provenance
framework inside P11.

status:
`OPEN / P13 OWNER`.
