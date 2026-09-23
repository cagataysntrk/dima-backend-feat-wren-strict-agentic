# P13 — NATIVE ENGINE STANDARD VERTICAL

**Milestone:** P13  
**Current authorized slice:** P13A provider-free native trust contract  
**Decision:** `DMP-DEC-0036`  
**Status:** IMPLEMENTATION AUTHORIZED AFTER GOVERNANCE REPIN / P13B NOT AUTHORIZED

## Goal

Allow native Metabot to author an analytical candidate while Dima deterministically decides whether
that exact artifact may become official execution truth.

## P13A deliverables

- `NativeQueryCandidate`;
- engine-independent `AuthorizedExecutionArtifact`;
- candidate authorization gate;
- exact-artifact fingerprint/mutation checks;
- minimal P10 generalization to common execution-resource identity;
- minimal P5 generalization to common execution-artifact identity;
- `CanonicalProjection` compatibility adapter;
- focused provider-free tests and CI.

## Initial capability

```text
one metric
one source
optional one accepted time scope
one query
no arbitrary filter family
no approved relationship path
no research
```

## Forbidden

- Agent API as Standard hot path;
- Agent API/Wren/raw SQL fallback;
- Dima rebuilding or silently fixing pMBQL;
- executing native query before Dima authorization;
- second access fingerprint;
- second receipt system;
- native prose promoted to VERIFIED Evidence;
- engine `main` consumed without exact gitlink;
- source-branch merge/cherry-pick/rebase;
- P13B live implementation in this cycle.

## Candidate → truth boundary

```text
NativeQueryCandidate
→ Dima authorization gate
→ ALLOW / CLARIFY_REPLAN / BLOCK
→ AuthorizedExecutionArtifact only on ALLOW
→ P10 exact resource/access authorization
→ execution contract must use same artifact
→ P5 exact artifact receipt
→ Evidence promotion later
```

## Tests

Provider-free high-information family only. REDs are classified before patching:
`NATIVE_CANDIDATE_EXTRACTION | AUTHORITY_MISMATCH | SEMANTIC_SCOPE_VIOLATION |
TIME_SCOPE_VIOLATION | RELATIONSHIP_GRAIN_VIOLATION | EXECUTION_ARTIFACT_MISMATCH |
ACCESS_IDENTITY_MISMATCH | RESOURCE_PROVENANCE_MISMATCH | ENGINE_IDENTITY |
RECEIPT_PROVENANCE | EVAL_ORACLE | TRANSPORT_RUNTIME | CI_GOVERNANCE`.

## Engine identity

P13A does not change engine source. Current runtime tag/short hash is not sufficient for P13B exact
production attestation. Exact source+image attestation decision is a pre-P13B gate.

## Stop

After P13A focused + P5 + P10 + C2 + governance are GREEN, seal only:
`P13A NATIVE TRUST CONTRACT = GREEN`.
Then STOP before P13B.


---

## P13A NATIVE TRUST CONTRACT — CLOSED GREEN

Certified wording:
```text
P13A NATIVE TRUST CONTRACT = GREEN
```

Product implementation commit:
`17dea824dddf8af185d9596abc5bfdbedd11e04a`

CI/governance guard closure:
`c7a95fe4c48687914b89c350b8130793467c36e6`

Evidence:
```text
P13A native trust workflow   35846503106 = SUCCESS
  focused P13A               12 PASS
  P5 + P10 critical          61 PASS
  P12X C2 bridge              7 PASS

P10 regression              35846797870 = SUCCESS
P5 regression               35846797938 = SUCCESS
governance                  35846797967 = SUCCESS
M1 regression               35846503059 = SUCCESS
```

Implemented:
- `NativeQueryCandidate` exact native pMBQL occurrence contract;
- exact candidate artifact fingerprint = deterministic serialization of the exact execution artifact,
  not semantic equivalence;
- bounded `ALLOW | CLARIFY_REPLAN | BLOCK` authorization gate for the P13A one-metric/one-source
  surface;
- `AuthorizedExecutionArtifact` engine-independent trust identity;
- exact-artifact mutation/substitution hard-fail;
- P10 `ExecutionAccessSnapshotIssuer` generalized to the common execution-resource identity without
  weakening principal/tenant/role/semantic-context/source checks;
- P5 `DimaQueryReceiptSealer` generalized to the same common execution identity without creating a
  second receipt system;
- historical `CanonicalProjection` remains supported through a compatibility adapter;
- P13-aware CI isolation guards preserve milestone ownership.

Exact engine remains:
```text
engine repo    = UpcyTech/dima-metabase-engine
Platform path  = engine/metabase
gitlink        = c56b71ab23bf2a2d266bac2fba8d165ac059d613
upstream base  = 2ba2485c78d7e00a9a25f82c00fc201da71590c4
runtime        = v0.63.18-dima.0
engine changes during P13A = 0
```

Engine identity source-review conclusion:
- current runtime properties expose tag + upstream build's seven-character git hash;
- P12X C2 was safe because CI externally pinned exact source/image;
- that surface alone is not enough for long-term P13B exact source+image attestation;
- P13A therefore made no engine patch;
- before P13B choose/certify either deployment/runtime exact source+immutable-image attestation or a
  minimal isolated Dima engine-identity endpoint/build manifest.

Explicitly NOT proven:
```text
P13 STANDARD = GREEN                         NO
production security = GREEN                  NO
native analytics absolute correctness = GREEN NO
P13B live vertical = authorized              NO
```

Still OPEN:
- `DMP-P5-BLOCK-001`;
- `DMP-P11-INTEGRATION-005` (P13C owner);
- EV-05 / EV-06 / EV-07;
- P10B2 RLS / CLS / impersonation / advanced routing / cache-result reauthorization;
- P9 dimension / time / relationship transport gaps;
- P7/P8 calculated / relationship / view semantic gaps;
- historical Wren typed gaps;
- P13B engine runtime exact source+image attestation decision.

STOP:
```text
P13B = NOT AUTHORIZED
```
