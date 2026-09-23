# P13 — PRE-DEVELOPMENT REVIEW

**Milestone:** P13 — Production Standard  
**Branch:** `feat/dima-metabase-platform`  
**Read baseline:** `56799687d2a8018dd60b0b909fb8b0be5d4a79c7`  
**Audited functional/product baseline:** `4b60bc3f1e6ab9526cd590a0989c1b227c5c43be`  
**P12 closure decision:** `DMP-DEC-0028`  
**P13 sequencing decision:** `DMP-DEC-0029`

Status: **SEALED / PREDEVELOPMENT REVIEW COMPLETE / IMPLEMENTATION NOT AUTHORIZED PENDING SUPERVISOR REVIEW**

## 1. Purpose

P13 is the first real governed Standard vertical through the Metabase substrate.

It does not own:
- new analytical cognition;
- root-cause planning;
- front-door routing;
- Wren retirement;
- new semantic resolver machinery;
- global production security certification.

Binding doctrine:
```text
LLM_FIRST_COGNITION + DIMA_OWNED_TRUTH

LLM      = cognition
Dima     = truth/trust
Metabase = execution/workspace substrate
DB       = numeric truth
```

## 2. Verified takeover state

```text
Platform HEAD at review            = 56799687d2a8018dd60b0b909fb8b0be5d4a79c7
functional baseline                = 4b60bc3f1e6ab9526cd590a0989c1b227c5c43be
P11 workflow                       = 35816646368 = SUCCESS
baseline governance                = 35816646416 = SUCCESS
handoff governance                 = 35817394598 = SUCCESS
P11 focused                         = 16 PASS
P11 certified wording              = INITIAL LOW-CARDINALITY NATIVE PATH GREEN
DMP-P5-BLOCK-001                   = OPEN
DMP-P11-INTEGRATION-005            = OPEN / P13 OWNER
EV-05 / EV-06 / EV-07             = UNCERTIFIED
ask-v2 moving observation          = d430680a02256f4b9612730bd79b2e938a134132
Fast Track moving observation      = 5280dd37451ded59ce181b93b015bc9dfafe0696
source disposition                 = REFERENCE ONLY
merge/cherry-pick/rebase            = FORBIDDEN
```

The handoff HEAD differs from the audited functional baseline only by handoff/status documentation.

## 3. P12 prerequisite disposition

P12 evidence remains internally consistent. No new evidence requires a different UX composition.

Certified closure wording:
```text
P12 BI WORKSPACE FEASIBILITY = CLOSED / CLASSIFICATION GREEN
```

Composition:
```text
DIMA_SHELL + HEADLESS_API
LINK_OUT = mature workspace escape hatch
EMBED    = deferred / measured escalation only
```

No P12 integration/frontend code was written or harvested.

## 4. Current-code findings that P13 must respect

### 4.1 Filter authority already contains value

`StandardProjection.filter_handles` resolve through `SemanticHandleRegistry`.
`ResolvedAnalyticsIntentBuilder` expects the resulting canonical target to be
`V2ResolvedFilterRef`, and copies its `dimension_name` plus `value: str` into the final
`ResolvedFilterRef`.

Therefore:
```text
final filter handle
= dimension meaning + material string value
```

P11 value adoption cannot occur after accepted Standard authority is sealed without mutating accepted
meaning.

### 4.2 P10 authorization needs the canonical prepared artifact

`ExecutionAccessSnapshotIssuer.issue` requires:
- current authenticated Dima principal;
- accepted `ResolvedAnalyticsIntent`;
- exact `CanonicalProjection`;
- truthful `VerifiedExecutionSecurityFacts`.

It checks authority id, projection hash, resolved-intent hash, semantic-context version, current
principal/roles/tenant and exact canonical resource identity.

### 4.3 Current Metabase execution API is circular for P13

`MetabaseSubstrateAdapter` currently receives an `ExecutionAccessSnapshot` in its constructor, while
`execute_execution_intent` itself compiles and canonicalizes the query.

P13 cannot:
```text
prepare #1 → authorize → adapter prepare #2 → execute
```

The authorized artifact and executed artifact must be exactly the same frozen canonical projection.

### 4.4 Receipt identity already supports the correct design

`DimaQueryReceiptSealer` checks the exact intent/projection/access/resource/query identities.
Therefore P13 should route one prepared canonical projection through authorization, execution and
receipt rather than weakening P5.

## 5. Exact filter-binding ordering decision

P13C, not P13A, owns P11 production integration.

Approved conceptual order:
```text
LLM cognition
↓
governed Dima semantic scope candidates/bindings
↓
Dima scope admissibility
↓
authenticated current-principal Metabase value retrieval
↓
retrieval attestation/reference
↓
LLM structured value proposal
↓
EntityValueAdoptionGate
↓
final governed textual filter binding / semantic handle
↓
SemanticSurfaceCoverage complete
↓
AcceptedStandardAuthority sealed
↓
ResolvedAnalyticsIntent
```

Rules:
- allowed semantic scopes are Dima-governed, not LLM self-asserted;
- the official authority is sealed only after the material filter value is resolved;
- P13 initial filter type is exact `str` equality only;
- `int | float | bool | NULL | range | typed comparison` remain explicit typed gaps;
- no coercion/stringification.

## 6. Retrieval-attestation and final access identity

A value lookup can happen before final canonical projection/P10 issuance.

It may carry a narrow reference with:
```text
retrieval_event_ref
authenticated Metabase subject ref
tenant/principal ref
semantic_context_ref
source_resource_ref
```

This is not a fingerprint and not an authority.

P10 final issuance must prove that the retrieval lens is coherent with the accepted intent and exact
prepared resource set, and must include the retrieval proof in the existing attestation/evidence chain.

Only:
```text
ExecutionAccessSnapshot.execution_access_fingerprint
```
is durable access identity.

## 7. Single prepared execution seam

P13A design:
```text
AcceptedStandardAuthority
→ ResolvedAnalyticsIntent
→ PREPARE ONCE
   compiler → canonicalizer → frozen CanonicalProjection
→ P10 authorize exact projection
→ ExecutionAccessSnapshot
→ execute exact same CanonicalProjection
→ strict DimaQueryReceipt
→ VERIFIED EvidenceArtifact
```

No:
- second compile;
- second canonicalization;
- query reconstruction;
- post-authorization semantic repair.

Planned narrow orchestration owner:
`backend/app/v3/standard_execution.py`.

Expected minimum execution-adapter evolution, only after supervisor authorization:
an explicit prepared-execution method that consumes the already-created `CanonicalProjection` and
does not prepare it again. Existing `execute_execution_intent` may remain for compatibility; the
P13 production seam must use the prepared path.

## 8. Ten required P13 answers

### Q1 — P11 adoption relative to handle minting/authority sealing
Before final filter-handle minting, coverage completion and Standard authority sealing. The sealed
authority must already contain the adopted material filter meaning.

### Q2 — Retrieval facts to final P10 identity
Use a narrow retrieval attestation/reference. P10 issuance later verifies same tenant/principal,
Metabase subject, semantic context and source-resource lens and carries the proof into the sole
`ExecutionAccessSnapshot.execution_access_fingerprint`/receipt chain. No second fingerprint.

### Q3 — Prepare once, authorize, execute same artifact
Create one frozen `CanonicalProjection`; authorize that object/identity; execute that exact object;
seal receipts from that exact object. The P13 path never invokes a second prepare after authorization.

### Q4 — Initial supported filter type
Exact string-valued equality only. Everything else is a typed capability gap. No `str(value)`.

### Q5 — Supplier of `VerifiedExecutionSecurityFacts`
P10 security ownership remains authoritative. For P13A provider-free tests, explicit fixture facts.
For the isolated P13B live canary, facts are truthfully assembled from the actual authenticated
restricted Metabase lab subject + exact basic permission/database state using the already-proven P10B1
shape. P13 does not discover/invent security truth.

### Q6 — How `DMP-P5-BLOCK-001` stays open
P13B certifies only the explicit BASIC AUTHENTICATED LAB PROFILE. No RLS/CLS/impersonation/advanced
routing/cache-lens/global production claim is made. The blocker is not edited closed.

### Q7 — Exact orchestration owner
New narrow P13 module:
`backend/app/v3/standard_execution.py`.
It composes existing certified owners and contains no LLM planning or semantic guessing.

### Q8 — Files forbidden to modify in P13A without classified RED
- `backend/app/v3/authority.py`;
- `backend/app/v3/analytics_contract.py`;
- `backend/app/v3/entity_value_gate.py`;
- `backend/app/v3/security_identity.py`;
- `backend/app/v3/execution_identity.py`;
- P4 compiler semantic behavior and canonical volatility rules;
- P7 importer;
- P8 equivalence;
- P9 resource lifecycle/transport;
- Wren adapter;
- legacy v2 semantic resolver/front door;
- ask-v2 and Fast Track branches.

### Q9 — Minimal provider-free proof
P13A should prove with a small high-information family:
1. happy metric-only path prepares once and returns one exact prepared projection;
2. authority/projection/resolved-intent mismatch fails closed;
3. current principal mismatch fails closed through existing P10 issuer;
4. resource identity mismatch fails closed;
5. prepared projection substitution/replacement is rejected by identity checks;
6. compiler/canonicalizer are called exactly once on the production seam;
7. execute-prepared does not compile/canonicalize;
8. receipt/evidence carry the same projection, resolved-intent, catalog/resource/query and access
   identities;
9. no Wren fallback/admin execution/raw SQL/display-name lookup occurs.

P13C later adds filter-specific provider-free proofs:
- multi-scope proposal → CLARIFY;
- retrieval-lens mismatch → fail;
- non-string approved value → typed unsupported;
- DMP-P11-INTEGRATION-005 coherence → pass/fail cases.

### Q10 — One live canary
After P13A provider-free GREEN:
```text
one explicit tenant
+ one restricted authenticated Metabase user
+ one governed metric
+ one ResolvedAnalyticsIntent
+ one prepared CanonicalProjection
+ one truthful basic-profile security-facts envelope
+ one ExecutionAccessSnapshot
+ one Metabase execution
+ one strict DimaQueryReceipt
+ one VERIFIED EvidenceArtifact
```

Expected:
```text
query_count = 1
receipt_count = 1
receipt_fingerprint != null
execution_access_fingerprint != null
evidence.state = VERIFIED
fallback_count = 0
admin_analytical_execution = 0
```

## 9. P13 phasing

```text
P13A provider-free orchestration + single-preparation contract
P13B one pinned-live metric-only Standard vertical
P13C textual filter + P11 integration / close DMP-P11-INTEGRATION-005
P13D selected already-certified breakdown/comparison/ranking families
```

No front-door change in P13A/B.

## 10. Planned files to modify after supervisor authorization

P13A expected:
- NEW `backend/app/v3/standard_execution.py`;
- MINIMAL `backend/app/v3/substrate/metabase/execution_adapter.py` prepared-execution seam;
- NEW `backend/tests/test_v3_p13_standard_execution.py`;
- NEW `.github/workflows/dima-metabase-p13.yml`;
- living status / decision/failure receipts as evidence requires.

P13B expected:
- NEW `backend/tests/test_v3_p13_standard_live.py` or a narrowly equivalent live canary;
- no production security-discovery framework.

P13C files are not authorized yet; exact retrieval/binding owner is decided only after P13A/B proof
and a fresh pre-implementation read.

## 11. Effectively frozen at P13 start

Without explicit classified RED + decision:
- P4 compiler semantic behavior;
- P4 canonical volatility rules;
- P5 receipt identity semantics;
- P7 importer;
- P8 equivalence matrix;
- P9 resource lifecycle;
- P10 access-fingerprint definition;
- P11 adoption semantics;
- Wren adapter;
- `/api/ask-v2` and production front door;
- source branches.

## 12. Failure policy

Every P13 RED is classified before patching as one of:
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

The single true owner is fixed. No case-derived patch.

## 13. Stop gate

This document is a predevelopment boundary, not product implementation authorization.

Before P13 implementation the supervisor must review:
- P12 closure receipt/wording;
- this predevelopment review;
- P13 ticket;
- Q1-Q10 answers;
- filter-binding ordering;
- prepare/authorize/execute design;
- DMP-P11-INTEGRATION-005 closure plan;
- security-facts owner;
- files to modify/freeze;
- provider-free proof and live canary.

Until then:
```text
P13 PRODUCT CODE = NOT AUTHORIZED
```
