# P5 — PRE-DEVELOPMENT REVIEW

**Milestone:** P5 — QueryReceipt + execution identity  
**Branch:** `feat/dima-metabase-platform`  
**P4 implementation:** `0af815887d8e50274b39bdb7975eb37e6e63971a`  
**P4 closure:** `c41ab1519b974632c56d52a119ec28e20b0f1e17`  
**P4 workflow:** `35753630759 = SUCCESS`  
**P4 closure governance:** `35754115603 = SUCCESS`  
**Metabase runtime:** `v0.63.18` / immutable digest pinned  
**Source branch:** `feat/ask-v2-mvp` — READ ONLY

Status: SEALED / P5 CONTRACT IMPLEMENTATION AUTHORIZED

Official Metabase receipt issuance remains **access-gated** and P5 may not close GREEN until the
execution-access snapshot is produced from a proven principal/auth/lens boundary.

## 1. Normative P5 flow re-read

Roadmap P5 requires a Dima receipt carrying at least:

```text
authority_id
projection_hash
resolved_intent_hash
canonical_query_fingerprint
canonical_query_representation?
ephemeral_query_handle?
principal_fingerprint
execution_access_fingerprint
semantic_context_version
resource_entity_ids
resource_fingerprints
substrate_runtime_version
substrate_image_digest
result_hash
row_count
warnings
```

Architecture R9 additionally requires obligation/tenant/principal/semantic refs, substrate,
database identity, execution time and limitations.

R10 requires:
- cross-tenant semantic/result leak = 0;
- missing principal execution = 0;
- implicit service/admin fallback = 0;
- authority/query mismatch = 0;
- permission-sensitive cache cross-user reuse = 0;
- security-bound replay without faithful serialization = 0.

R10.1 says every official execution/evidence receipt has a non-secret access fingerprint derived
from the effective access lens, including tenant/principal, roles, policy, RLS/CLS, database route,
impersonation, semantic context, source object refs and security parameters.

## 2. Existing code audit

Inspected:
- `app/v3/evidence.py::DimaQueryReceipt`;
- `app/v3/analytics_contract.py::PrincipalContextRef`;
- `app/v3/legacy_contract.py::LegacyV2QueryReceiptWriter`;
- `app/v3/substrate/base.py::QueryReceiptWriter`;
- `app/v3/substrate/wren.py`;
- `app/contracts.py::ContractStore.record_v2_minimum`;
- `control_plane.authorize::Principal`;
- `app/v2.models::TenantAnalyticsRuntimeV0`;
- P4 canonical/runtime identity contracts.

### Finding A — M1 receipt shell is intentionally incomplete

Current `DimaQueryReceipt` is a foundational M1 shell. Its
`execution_access_fingerprint` is optional and it lacks part of the full R9 receipt identity.

P5 must complete the official receipt contract without pretending the M1 shell already proves P5.

### Finding B — current legacy access fingerprint is NOT P5-compliant

`LegacyV2QueryReceiptWriter` currently emits:

```text
principal_fingerprint          = intent.principal.fingerprint
execution_access_fingerprint  = intent.principal.fingerprint
```

That preserves M1 parity but does not prove:
- attribute-policy identity;
- policy version;
- RLS/CLS versions;
- database route/destination;
- impersonation role;
- source-object access lens;
- security parameter digest;
- Metabase authenticated principal binding;
- DB effective access binding.

Therefore this value is **M1_COMPAT_ONLY** and is not acceptable as P5 official access evidence.

### Finding C — existing control-plane Principal is not enough by itself

Current `Principal` carries user/tenant/roles/branches, and `TenantAnalyticsRuntimeV0` carries
tenant/user/roles/catalog/schema. These are useful inputs but are not the complete R10.1 effective
access lens.

P5 must not manufacture missing fields from defaults or hash the partial principal and call it done.

## 3. P5 ownership split

```text
ResolvedAnalyticsIntent
+ CanonicalProjection (P4)
+ ExecutionAccessSnapshot (P5; externally proven)
+ exact substrate runtime identity
+ execution result
→ DimaQueryReceiptSealer
→ official DimaQueryReceipt
```

### Query identity owner

P4 owns:
- stable canonical query representation;
- stable canonical query fingerprint;
- resource entity ids/fingerprints;
- query-step role;
- actual executable serialized query.

P5 must consume these, not re-canonicalize them.

### Access identity owner

P5 introduces one engine-independent immutable `ExecutionAccessSnapshot` contract.

It contains enough non-secret material to deterministically derive the R10.1 fingerprint. The sealer
may validate the snapshot against the intent/canonical projection, but may not derive the snapshot
from `PrincipalContextRef` alone.

A later substrate-specific access attestor/issuer must prove where that snapshot came from.

## 4. Required ExecutionAccessSnapshot V1

Minimum fields:

```text
tenant_binding
principal_subject
roles
attribute_policy_digest
policy_version
rls_versions
cls_versions
database_route
database_destination
impersonation_role?
semantic_context_version
source_object_refs
security_parameter_digest
attestation_refs
```

Derived deterministically:
- role_set_digest;
- execution_access_fingerprint.

Rules:
- roles/source refs are canonicalized for hashing without changing their meaning;
- all policy/security digests are explicit inputs;
- no secret/token/session credential enters the fingerprint;
- no missing field gets a magic default;
- empty/missing attestation refs are invalid for an official snapshot.

## 5. P5 receipt authority invariants

The sealer MUST hard-fail if:
- intent authority id != canonical authority id;
- projection hash differs;
- resolved intent hash differs;
- semantic context differs;
- access tenant/principal differs from the resolved intent;
- access role set differs from the resolved intent principal roles;
- access semantic context differs;
- access source-object refs do not faithfully cover the canonical resource identity;
- runtime version/image digest is missing;
- query/result cardinality differs;
- official access snapshot is absent.

This is the P5 form of:

`Authority A + Query B = hard fail`.

## 6. Durable vs ephemeral identity

Durable receipt material:
- P4 stable canonical representation/fingerprint;
- authority/projection/intent identity;
- complete execution-access fingerprint;
- resource identity;
- runtime version + immutable image digest;
- result hash + row count;
- execution timestamp.

Ephemeral and never durable identity:
- pagination continuation token;
- MCP query handle;
- HTTP session token;
- Metabase session id;
- runtime `lib/uuid`.

REST P4 serialized execution payload remains execution material but runtime-local `lib/uuid`
does not become the durable fingerprint.

## 7. Replay/read-time rule

P5 receipt identity is not authorization.

Any later replay/read of permission-sensitive evidence must:
1. resolve the current principal;
2. obtain a current access snapshot;
3. compare lens compatibility under the active policy;
4. fail closed on mismatch or missing principal.

P5 will define the identity contract needed for this check. It will not silently add a cache/replay
authorization implementation to unrelated product paths.

## 8. M1 compatibility boundary

Do not break the certified Wren path merely to make its legacy receipt look P5-complete.

During P5:
- `LegacyV2QueryReceiptWriter` remains compatibility code;
- its legacy access field is explicitly not P5 certification evidence;
- P5 official sealer is a new strict path;
- no fallback converts an M1 compatibility receipt into a P5 official receipt.

P6 parity can later compare Wren/Metabase under the same proven access snapshot.

## 9. P5 allowed files

```text
backend/app/v3/evidence.py
backend/app/v3/execution_identity.py
backend/app/v3/substrate/base.py          # only if protocol typing needs extension
backend/tests/test_v3_p5_*.py
.github/workflows/dima-metabase-p5.yml
.github/workflows/dima-metabase-governance.yml
backend/belgeler/metabase/predev/P5_PREDEVELOPMENT_REVIEW.md
backend/belgeler/metabase/tickets/P5_QUERY_RECEIPT_EXECUTION_IDENTITY.md
backend/belgeler/metabase/*RECEIPTS*.md
DIMA-METABASE-DURUM.md
```

Compatibility inspection only unless a new receipt authorizes a change:
```text
backend/app/v3/legacy_contract.py
backend/app/v3/substrate/wren.py
```

## 10. P5 forbidden files absent a new receipt

```text
backend/app/v2/**
backend/app/contracts.py
backend/control_plane/**
backend/app/v3/authority.py
backend/app/v3/analytics_contract.py
backend/app/v3/semantic_spec.py
backend/app/v3/substrate/metabase/compiler.py
backend/app/v3/substrate/metabase/canonical.py
backend/app/v3/substrate/metabase/client.py
backend/app/routers/**
backend/app/main.py
backend/app/config.py
backend/lab/metabase/**
WrenAI-main/**
feat/ask-v2-mvp
```

No product routing or principal/auth mapping is smuggled into P5 contract work.

## 11. Focused proof matrix

Provider-free:
- deterministic role-set digest and access fingerprint;
- order-insensitive role/source-ref hashing;
- policy/RLS/CLS/database/security changes alter access fingerprint;
- secret/session/token fields do not exist in the model;
- missing access snapshot hard-fails official receipt;
- authority/projection/intent/context mismatch hard-fails;
- tenant/principal/role mismatch hard-fails;
- source-object mismatch hard-fails;
- canonical step count/result count mismatch hard-fails;
- stable receipt id on identical durable identity;
- result mutation changes result hash/receipt id;
- comparison plan produces one receipt per executed query step;
- no ephemeral continuation/query handle enters durable receipt hash;
- M1 compatibility writer is not accepted as an access attestor.

Regression:
- P4 compiler/canonical GREEN;
- P3/P3A GREEN;
- M1/Wren GREEN;
- governance GREEN.

## 12. P5 sub-gates

### P5A — receipt/access identity contracts

Authorized after this review governance is GREEN:
- complete the receipt model;
- implement `ExecutionAccessSnapshot`;
- implement strict receipt sealer;
- provider-free proof.

### P5B — effective access attestation

Not automatically authorized by P5A.

Before P5 can close GREEN, a separate review/receipt must identify how a real execution obtains:
- current Dima principal;
- authenticated Metabase principal/lens;
- database route/effective security context;
- policy/RLS/CLS versions;
- source-object security parameters.

If the runtime cannot produce this faithfully, P5 remains BLOCKED rather than hashing guessed values.

## 13. Exit semantics

P5 closes GREEN only when:
```text
official receipt missing access snapshot      = HARD FAIL
principal_fingerprint == access fingerprint   = NOT ASSUMED
authority/query mismatch                      = HARD FAIL
complete access fingerprint                   = PASS
durable canonical identity                    = P4 fingerprint
runtime identity                              = pinned version + image digest
resource identity                             = entity ids + fingerprints
result identity                               = deterministic
ephemeral identity in durable fingerprint     = 0
service/admin fallback                        = 0
P4/P3/P3A/M1 regressions                      = GREEN
product routing change                        = 0
```

P5 GREEN does not mean P6 Wren/Metabase numeric/permission parity, Metabase primary routing, or Wren
retirement.

## 14. Authorization

P5A implementation may begin only after this review commit's governance workflow is GREEN.

P5B effective-access implementation requires a subsequent explicit review/receipt. P5 product closure
is forbidden before P5B is proven.
