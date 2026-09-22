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
