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
