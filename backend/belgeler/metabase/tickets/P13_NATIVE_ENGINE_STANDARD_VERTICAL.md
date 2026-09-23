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
