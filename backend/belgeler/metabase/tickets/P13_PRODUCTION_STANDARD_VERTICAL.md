# P13-001 — Production Standard vertical

**Milestone:** P13  
**Status:** PREDEVELOPMENT SEALED / P13 PAUSED FOR METABASE SEAM DECISION / IMPLEMENTATION STOPPED  
**Decision dependencies:** `DMP-DEC-0029`  
**P11 forward requirement:** `DMP-P11-INTEGRATION-005 = OPEN / P13C OWNER`

## Goal

Build the first real governed Standard vertical through Metabase by composing the already-proven Dima
authority, canonical-query, P10 access, P5 receipt and Evidence contracts.

The first slice is deliberately metric-only.

## Non-goals

- no front-door routing;
- no Research integration;
- no deterministic analytical planner;
- no new entity resolver;
- no typed filter expansion;
- no global security certification;
- no Wren removal;
- no source-branch harvest unless a measured P13 gap later proves it necessary.

## P13A — provider-free orchestration

Target flow:
```text
accepted authority
→ resolved intent
→ prepare once
→ exact canonical projection
→ P10 access issuance
→ execute exact prepared projection
→ strict receipt
→ VERIFIED evidence
```

Planned owner:
`backend/app/v3/standard_execution.py`.

Expected minimal adapter seam:
execute an already-prepared frozen canonical projection without invoking compiler/canonicalizer again.

Exit gate:
- provider-free focused family GREEN;
- preparation count exactly one;
- no second canonicalization;
- authority/projection/resource/access/query identity consistent end-to-end;
- no fallback/raw SQL/admin execution/legacy semantic resolver.

## P13B — one pinned-live metric-only canary

Profile:
`BASIC AUTHENTICATED LAB PROFILE`.

One tenant, one restricted authenticated Metabase subject, one governed metric, one exact prepared
query, one truthful P10 facts envelope, one P10 access snapshot, one Metabase execution, one strict
receipt, one VERIFIED EvidenceArtifact.

This does not close `DMP-P5-BLOCK-001`.

## P13C — textual filter + P11 integration

Only after P13A/B are green and the pre-sealed filter-ordering decision remains valid.

Must close:
`DMP-P11-INTEGRATION-005`.

Requirements:
- allowed scopes from Dima-governed semantic binding;
- current-user value retrieval under authenticated Metabase subject;
- narrow retrieval attestation only;
- final P10 coherence check;
- one durable execution-access fingerprint;
- exact string equality only;
- multi-scope BIND becomes CLARIFY;
- no coercion/fuzzy/translation/physical-field guessing.

## P13D — selected existing Standard families

Only then consider already-certified:
- breakdown;
- comparison;
- ranking.

No mechanical test-volume expansion.

## Files to touch — P13A candidate set

```text
NEW     backend/app/v3/standard_execution.py
MINIMAL backend/app/v3/substrate/metabase/execution_adapter.py
NEW     backend/tests/test_v3_p13_standard_execution.py
NEW     .github/workflows/dima-metabase-p13.yml
DOCS    current P13/status/receipt records
```

Any additional prior-owner file requires a classified RED and explicit decision.

## Files not to touch — P13A

```text
backend/app/v3/authority.py
backend/app/v3/analytics_contract.py
backend/app/v3/entity_value_gate.py
backend/app/v3/security_identity.py
backend/app/v3/execution_identity.py
backend/app/v3/substrate/metabase/compiler.py
backend/app/v3/substrate/metabase/canonical.py
backend/app/v3/semantic_spec.py
backend/app/v3/semantic_import.py
backend/app/v3/semantic_equivalence.py
backend/app/v3/resource_provisioning.py
backend/app/v3/resource_transport.py
backend/app/v3/substrate/wren.py
/api/ask-v2 routing
feat/ask-v2-mvp
feat/dima-metabase-product-fast-track
```

## Focused proof

High-information only:
- happy single-preparation metric path;
- mismatch/fail-closed identities;
- current-principal mismatch;
- resource mismatch;
- prepared artifact substitution;
- exact once compiler/canonicalizer call;
- receipt/evidence identity closure;
- fallback/admin/raw-SQL/legacy-resolution absence.

No Luna/Sol for P13A because the model-visible cognition contract does not change.

## Failure classes

```text
CONTRACT
AUTHORITY ORDERING
ACCESS IDENTITY
PROJECTION IDENTITY
PROVENANCE
SUBSTRATE RUNTIME
P11 INTEGRATION
ORACLE
CI/GOVERNANCE
FIXTURE
```

Classify before patching.

## Current authorization

Documentation/predevelopment only.

```text
P13 implementation = STOP
until supervisor reviews the sealed boundary.
```


## P12X pause

DMP-DEC-0030 pauses P13 implementation until the V0+A+B Metabase seam benchmark is classified. Do not create `standard_execution.py` or `execute_prepared()` during P12X.
