# P10 — PRE-DEVELOPMENT REVIEW

**Milestone:** P10 — Tenant / principal / effective-security mapping  
**Branch:** `feat/dima-metabase-platform`  
**P9B isolated lifecycle closure:** `d3f4bb8b8aa9a65796506193632f7c429eac8d7c`  
**P9B workflow:** `35782974669 = SUCCESS`  
**P9B governance:** `35782974647 = SUCCESS`  
**Source branch:** moving reference only; no merge/cherry-pick/rebase/base replacement.

Status: **SEALED / P10A PROVIDER-FREE SECURITY ISSUER CONTRACT AUTHORIZED / PRODUCTION ISSUANCE NOT AUTHORIZED**

## 1. Normative objective

P10 proves the real chain:

```text
authenticated Dima principal
+ accepted analytics principal
+ explicit tenant/data lens
+ authoritative policy / RLS / CLS facts
+ explicit database route/destination
+ explicit Metabase authenticated identity/lens
+ canonical source-object identity
        ↓
faithful issuer
        ↓
P5 ExecutionAccessSnapshot
        ↓
ExecutionAccessFingerprint
```

P10 does not redefine the snapshot. DMP-DEC-0024 makes P5 `ExecutionAccessSnapshot` the sole
durable execution-access contract.

## 2. Current concrete owners

### Dima principal

`backend/control_plane/authorize.py::Principal` is current authenticated request identity:
- user_id;
- tenant_id;
- is_superadmin;
- roles;
- branch_ids;
- tenant_slug.

`tenant_scope()` already fail-closes a non-superadmin missing tenant.

### Accepted analytics principal

`PrincipalContextRef` inside `ResolvedAnalyticsIntent` owns:
- tenant_binding;
- principal_subject;
- roles;
- deterministic principal fingerprint.

P10 must require exact agreement between current request identity and accepted intent identity.
No stale intent-principal reuse across a changed user/tenant/role set.

### P5 durable output

`ExecutionAccessSnapshot` already requires:
- tenant_binding;
- principal_subject;
- roles;
- attribute_policy_digest;
- policy_version;
- rls_versions;
- cls_versions;
- database_route;
- database_destination;
- impersonation_role;
- semantic_context_version;
- source_object_refs;
- security_parameter_digest;
- attestation_refs.

P10 issues this exact type; it does not fork it.

### Metabase

`MetabaseAgentClient` accepts an injected session token but intentionally does not own login,
tenant mapping, impersonation or API-key provisioning.

Therefore:
```text
session token possession != durable principal attestation
```

P10 must establish the authenticated Metabase subject/lens explicitly before production issuance.

## 3. P10A — provider-free issuer contract

First slice is pure/provider-free. It establishes the issuer boundary and mismatch rules without
claiming live permission parity.

Authorized shape:

```text
VerifiedExecutionSecurityFacts
  tenant_binding
  principal_subject
  roles
  attribute_policy_digest
  policy_version
  rls_versions
  cls_versions
  database_route
  database_destination
  impersonation_role
  semantic_context_version
  source_object_refs
  security_parameter_digest
  attestation_refs
  metabase_subject_ref
  evidence_refs

ExecutionAccessSnapshotIssuer.issue(
  current_principal,
  accepted_intent,
  canonical_projection,
  verified_security_facts,
) -> ExecutionAccessSnapshot
```

`VerifiedExecutionSecurityFacts` is an input evidence envelope, not a second durable identity.
It must not define its own competing access fingerprint.

## 4. P10A fail-closed invariants

Hard RED:
- current Dima principal absent;
- non-superadmin tenant absent;
- superadmin has no explicit effective tenant for tenant-bound execution;
- current Dima user != accepted principal subject;
- current/effective tenant != accepted tenant;
- current roles != accepted roles;
- semantic context mismatch;
- canonical projection identity mismatch;
- source-object refs differ from canonical resource ids;
- missing policy/RLS/CLS/database/security evidence;
- empty/unknown Metabase authenticated subject;
- implicit admin/service-account fallback;
- duplicate or empty attestation/evidence refs.

P10A never derives policy/security facts from names, role labels, SQL, formula text or a session token.

## 5. Superadmin rule

A Dima superadmin may be authorized at the control plane, but a tenant-bound Standard analytics
execution still requires an explicit effective tenant/data lens.

Forbidden:
```text
Principal(is_superadmin=true, tenant_id=None)
→ silently issue tenant-bound ExecutionAccessSnapshot
```

No implicit cross-tenant lens.

## 6. P10B — isolated mapping/security proof

Only after P10A GREEN.

Test topology:
```text
tenant A / tenant B
A1 / A2
admin
restricted
row-restricted
```

Required negative proofs:
- A sees B = 0;
- cached A result visible B = 0;
- missing creator/principal = fail closed;
- service/admin fallback = 0;
- permission revoked after execution -> reread denied;
- same semantic query under incompatible access lens cannot reuse result/receipt authority;
- runtime-only security state that cannot be faithfully serialized -> persistence forbidden.

This may require a dedicated lab fixture and explicit permission/RLS/CLS configuration. Do not fake it
with provider-free role names.

## 7. Read-time reauthorization

Creation-time permission is not a permanent right.

Any evidence/report/dashboard/cached-result reread path must be designed to gate on:
```text
current principal
+ current permission
+ compatible current data-access lens
```

P10A may define the contract; integrated read-path wiring is authorized only after its owner is
identified and reviewed.

## 8. Cache identity

Permission-sensitive cached results must be partitioned by faithful access identity.
Cross-user or cross-lens cache reuse is forbidden.

Do not create a second semantic/result cache inside P10 merely to prove this invariant.

## 9. Connection ownership

Connection ownership must be explicit:
- selected Standard analytics substrate owns its data-plane connection;
- Dima direct DB connection is allowed only as a separately governed specialized capability;
- duplicated credential/secret/rotation ownership is forbidden.

Secrets are not part of `ExecutionAccessSnapshot` or its fingerprint.

## 10. P7 security metadata

P7 structured-field coverage already surfaces security-related metadata as typed gaps.
P10 may consume explicit structured security facts only when a real owner/mapping is proven.
It must not infer enforcement behavior from `sensitivity`, names, descriptions or formula text.

## 11. DMP-P5-BLOCK-001

P10 is the active owner.

Closure requires a proven issuer/attestor that can faithfully populate every security-bearing
`ExecutionAccessSnapshot` field for production Standard analytics.

Until then:
```text
production official receipt issuance = BLOCKED
production customer P9B writes       = BLOCKED
primary routing cutover              = BLOCKED
```

## 12. Forbidden

```text
implicit tenant
implicit principal
service-account fallback
admin fallback
session-token-as-principal-id
role-name heuristic security
regex/fuzzy/morphology security mapping
SQL/formula-derived RLS/CLS
name-based source permission
secret in fingerprint
raw PII in receipt
cross-tenant cache reuse
creation-time permission reused forever
source-branch merge/cherry-pick/rebase
production routing change
```

## 13. Initial authorized files

```text
backend/app/v3/security_identity.py
backend/tests/test_v3_p10_security_identity.py
.github/workflows/dima-metabase-p10.yml
backend/belgeler/metabase/predev/P10_PREDEVELOPMENT_REVIEW.md
backend/belgeler/metabase/tickets/P10_TENANT_PRINCIPAL_SECURITY_MAPPING.md
backend/belgeler/metabase/*RECEIPTS*.md
DIMA-METABASE-DURUM.md
```

Initial slice does not modify:
- P5 `execution_identity.py`;
- `control_plane/authorize.py`;
- Metabase client/substrate;
- routing;
- P9 transport;
- ask-v2 source branch.

## 14. P10A high-information provider-free tests

At minimum:
1. exact current-principal + accepted-intent + projection + verified facts -> one P5 snapshot;
2. current user mismatch -> RED;
3. tenant mismatch -> RED;
4. role-set mismatch -> RED;
5. source-object mismatch -> RED;
6. semantic-context mismatch -> RED;
7. missing Metabase subject/evidence -> RED;
8. superadmin without explicit effective tenant -> RED;
9. deterministic snapshot fingerprint for same facts;
10. policy/RLS/CLS/database/security changes alter access fingerprint.

No giant suite.

## 15. Exit

P10A GREEN means the issuance contract is fail-closed and deterministic.

It does **not** close DMP-P5-BLOCK-001. That blocker closes only after P10B proves the real
Metabase/Dima/tenant/security mapping and the required negative security topology.
