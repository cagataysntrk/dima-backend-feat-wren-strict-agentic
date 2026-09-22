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
