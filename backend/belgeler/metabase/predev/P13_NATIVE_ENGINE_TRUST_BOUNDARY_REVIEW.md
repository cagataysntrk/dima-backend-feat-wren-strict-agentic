# P13 — NATIVE ENGINE TRUST BOUNDARY PRE-DEVELOPMENT REVIEW

**Milestone:** P13-0 / P13A  
**Branch:** `feat/dima-metabase-platform`  
**Read HEAD:** `6a74994b9f968a1c3c318456832d0b68b321d202`  
**Functional P12X proof:** `094b5f6e0f1be939172b95fde66cab055c66ae54`  
**Engine gitlink:** `c56b71ab23bf2a2d266bac2fba8d165ac059d613`  
**Normative decision:** `DMP-DEC-0036`

Status: **SEALED / P13A PROVIDER-FREE IMPLEMENTATION AUTHORIZED AFTER GOVERNANCE REPIN**

## 1. Purpose

P13A proves one trust transition:

```text
native Metabot candidate authoring
→ Dima deterministic authorization
→ exact authorized execution artifact identity
→ P10 access authorization
→ exact same artifact execution contract
→ one P5 receipt identity
```

It does not prove P13B live production execution, global production security, arbitrary filters,
relationships, research, frontend routing or Wren retirement.

## 2. Authoritative ownership

```text
Native Metabot = cognition + query candidate author
Dima           = business truth + execution/security/provenance/evidence authority
Metabase QP    = executor
DB             = numeric truth
```

The P13 gate is a verifier, not a query planner.

## 3. Native candidate source

Pinned engine source at `c56b71a...` proves `construct_notebook_query` resolves/validates a query and
emits structured output with:
- native query-id;
- exact resolved pMBQL `query`;
- portable/exported `query-json`;
- result columns.

P13A contract tests may construct frozen candidates directly; no Luna/Sol and no live engine are needed.

## 4. NativeQueryCandidate

Required fields:
```text
engine_identity
dima_request_id
dima_trace_id
native_conversation_id
native_query_id
resolved_pmbql
portable_query?
resource_bindings
native_validation_refs
candidate_artifact_fingerprint
query_count
```

Fingerprint:
- deterministic canonical JSON of the exact resolved pMBQL occurrence;
- exact artifact identity, not semantic equivalence;
- no volatility stripping for the purpose of making separately generated candidates look equal.

No prose parsing or chart-URL inference.

## 5. Candidate authorization gate

P13A supports one metric/source and optional accepted time scope, one query only.

Gate outcomes:
`ALLOW | CLARIFY_REPLAN | BLOCK`.

Initial checks:
- authority/projection/resolved-intent/semantic-context identity matches;
- candidate source/resource set exactly equals authorized resource set;
- candidate query count equals one;
- candidate material semantic refs are a subset/equal to accepted semantic refs for the certified
  metric-only capability;
- candidate may not introduce filters, joins or an unaccepted time scope;
- resource fingerprints must match current Dima-governed bindings;
- exact candidate fingerprint must match the artifact packaged for authorization.

P13A does not implement full relationship comparison or arbitrary filter semantics.

## 6. AuthorizedExecutionArtifact

One engine-independent contract exposes P5/P10 common facts:
```text
authority_id
projection_hash
resolved_intent_hash
semantic_context_version
semantic_refs
resource_bindings[]
steps[]:
  role
  artifact_fingerprint
  artifact_representation
query_count
substrate / engine identity
```

For native Metabase, artifact representation is exact resolved pMBQL.
For historical Agent API, `CanonicalProjection` is adapted to this contract.

Semantic authority does not move into this model.

## 7. P10 adaptation

`ExecutionAccessSnapshotIssuer` remains the sole issuer and keeps all existing principal/role/tenant/
semantic-context/security-fact checks.

Only its execution-resource input is generalized from concrete `CanonicalProjection` to
`AuthorizedExecutionArtifact`.

Verified source objects must exactly cover authorized resource ids. No check is weakened.

## 8. P5 adaptation

`DimaQueryReceiptSealer` remains the only official receipt seal point.

Only its execution-artifact input is generalized. Receipt semantics remain:
authority + resolved intent + exact artifact fingerprint + access fingerprint + resources + runtime +
result hash + row count + execution occurrence.

`CanonicalProjection` remains supported through an adapter. No NativeReceipt type is created.

## 9. Exact-artifact rule

Authorization consumes the exact candidate fingerprint and exact pMBQL representation. Execution
contract must reference the same artifact. Receipt seals the same fingerprint/representation.

Any substitution/mutation after authorization hard-fails.

## 10. Engine identity P13-0 source review

Current native bridge checks `runtime_tag` from `/api/session/properties`.

Pinned upstream build source:
`bin/build/src/build/version_properties.clj` records tag and only seven git-hash characters.
The runtime therefore does not currently provide a full-SHA + image-digest identity surface.

Conclusion:
- P13A: no engine change required;
- P13B: current runtime tag check alone is insufficient;
- before P13B certify either deployment/runtime exact source+image attestation or a minimal isolated
  Dima identity endpoint/build manifest;
- do not patch native engine core speculatively.

## 11. P13A focused proof

Approximately 8–12 provider-free tests:
1. exact metric/source candidate → ALLOW;
2. wrong semantic/source scope → BLOCK;
3. time overscope → BLOCK;
4. unexpected material filter → BLOCK;
5. unapproved join → BLOCK;
6. query_count > 1 → BLOCK;
7. authority/projection/resolved-intent mismatch → BLOCK;
8. resource id/fingerprint mismatch → BLOCK;
9. candidate mutation after authorization → BLOCK/HARD FAIL;
10. AuthorizedExecutionArtifact → P10 preserves every existing check;
11. P5 seals the exact authorized artifact fingerprint/representation;
12. historical `CanonicalProjection` adapter preserves existing P5/P10 behavior.

## 12. Required regression proof

After P13A:
- new P13A focused provider-free family;
- P5 focused family;
- P10 focused family;
- P12X C2 provider-free bridge family;
- governance.

No live model benchmark.

## 13. Files

Likely new owner:
`backend/app/v3/native_execution.py`.

Potential necessary edits only:
- `backend/app/v3/security_identity.py`;
- `backend/app/v3/execution_identity.py`;
- `backend/app/v3/substrate/metabase/native_models.py`;
- focused tests/workflow.

Do not modify the pinned engine during P13A by default.

## 14. Stop gate

Success wording:
`P13A NATIVE TRUST CONTRACT = GREEN`.

Do not claim:
- P13 Standard green;
- production security green;
- native analytical correctness green.

Then stop before P13B.
