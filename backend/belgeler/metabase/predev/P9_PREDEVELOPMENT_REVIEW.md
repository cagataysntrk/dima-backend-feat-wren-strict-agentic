# P9 — PRE-DEVELOPMENT REVIEW

**Milestone:** P9 — Semantic resource provisioner  
**Branch:** `feat/dima-metabase-platform`  
**P8 implementation:** `23480aa433ba10fed84a015a85c9f1d88b31572e`  
**P8 workflow:** `35773470252 = SUCCESS`  
**Pinned Metabase:** `v0.63.18 / commit 2ba2485c78d7e00a9a25f82c00fc201da71590c4`  
**Source branch:** `feat/ask-v2-mvp@5789e729115fe044b689739d5960021aba0aca32` — REFERENCE ONLY / READ ONLY

Status: **SEALED / P9A RESOURCE PLAN IMPLEMENTATION AUTHORIZED**

## 1. Objective

P9 owns deterministic lifecycle management for Dima-managed Metabase semantic resources:

```text
DimaSemanticSpec
+ P8 equivalence classification
+ explicit ManagedResourcePolicy
+ current resource inventory
        ↓
dry-run diff / reconciliation plan
        ↓
pinned Metabase resource transport (later P9B gate)
```

DimaSemanticSpec remains the single business-meaning owner. Metabase resources are executable/UI
representations.

## 2. P9A before transport

The first slice is provider-free and does **not** write to Metabase.

Reason:
pinned v0.63.18 exposes multiple resource surfaces; new metrics are Card-backed while metric read/
dataset behavior also lives under `/api/metric`. P9 must not assume a single generic mutation API.

P9A therefore certifies desired-state identity, diff, ownership, drift and rollback planning before
any REST mutation client is added.

P9B may add the exact pinned write transport only after a separate source/runtime review.

## 3. Identity rule

Durable Dima identity:

```text
tenant_binding
Dima canonical semantic id
resource kind
semantic_context_version
desired resource fingerprint/version
```

Metabase numeric database/card/table/field IDs are adapter-local locators, never Dima semantic IDs.

Metabase stable `entity_id` may be stored as an external binding locator, but it never replaces the
Dima canonical id.

No name, label or description is a binding key.

## 4. Explicit ownership only

A resource is Dima-managed only when `ManagedResourcePolicy` explicitly says `DIMA_MANAGED`.

`USER_MANAGED` and `EXTERNAL` content is never overwritten or promoted to semantic authority.

Same-name unmanaged content is unrelated unless an explicit binding record already exists.

No search-by-name adoption.

## 5. Desired resource scope

P9A may create desired resource descriptors only for:
- semantic refs that exist in DimaSemanticSpec;
- explicit `DIMA_MANAGED` policies;
- P8 classifications whose strategy allows managed representation.

Initial P9A allows:
- `NATIVE_METABASE`;
- `DIMA_COMPILED` only as a planned resource type, not transport execution.

Initial P9A does not provision:
- `WREN_ONLY_GAP`;
- `UNSUPPORTED`;
- security/runtime-only behavior as a Metabase semantic resource.

`DIMA_RUNTIME` stays Dima-owned runtime state unless a later resource-specific contract says
otherwise.

## 6. Provider-free contracts

### ManagedResourceBinding

```text
tenant_binding
canonical_id
resource_kind
semantic_context_version
metabase_entity_id?       # external locator only
metabase_local_id?        # adapter-local; never durable semantic identity
applied_version
applied_fingerprint
ownership
```

### DesiredResource

```text
tenant_binding
canonical_id
resource_kind
semantic_context_version
desired_version
desired_fingerprint
payload
ownership = DIMA_MANAGED
reconciliation
```

### ProvisionAction

```text
CREATE
NOOP
UPDATE
REJECT_DRIFT
IMPORT_AS_NEW_VERSION
RETIRE_STALE
```

Every mutating action carries a rollback descriptor.

## 7. Reconciliation policy

For a Dima-managed bound resource whose observed fingerprint differs from desired:

- `OVERWRITE` -> UPDATE with previous snapshot rollback;
- `REJECT` -> REJECT_DRIFT / no write;
- `IMPORT_AS_NEW_VERSION` -> IMPORT_AS_NEW_VERSION preserving previous binding/version.

Missing current resource under an existing Dima binding is typed drift; it is not silently recreated
until policy explicitly allows the recovery action.

Unbound same-name resource never counts as current state.

## 8. Idempotency

Required:

```text
same desired spec + same inventory twice
→ identical plan
→ NOOP for already-applied Dima-managed resources
```

Plan fingerprint is deterministic and independent of inventory ordering.

## 9. Tenant scope

Binding key always includes tenant binding.

Two tenants may use the same canonical semantic id but cannot share a resource binding accidentally.

P9 does not implement P10 user/principal permissions.

## 10. Drift/fingerprint

Observed resource fingerprint must cover the exact managed representation that P9 owns.

If an observed resource changes outside the Dima desired fingerprint:
- classify drift;
- apply explicit reconciliation policy;
- never silently rebind to a similar resource.

Rename does not trigger name search. Existing stable binding locator is used; missing locator/object is
typed drift.

## 11. Rollback

P9A rollback is a deterministic plan, not an executed mutation.

- CREATE -> rollback DELETE/ARCHIVE_CREATED_RESOURCE;
- UPDATE -> rollback RESTORE_PREVIOUS_SNAPSHOT;
- IMPORT_AS_NEW_VERSION -> rollback RESTORE_PREVIOUS_BINDING / RETIRE_NEW_VERSION.

Exact transport semantics are P9B-owned.

## 12. Real P8 consequence

Current imported Wren metrics are opaque formula-backed and therefore P8 `WREN_ONLY_GAP`.
P9 must not manufacture Metabase metrics for them to improve migration score.

Resource provisioning begins only for semantics with explicit ownership + representable strategy.

## 13. Forbidden

```text
name/label search binding
fuzzy matching
regex semantic interpretation
formula parsing
implicit resource adoption
Metabase numeric ID as Dima identity
unmanaged overwrite
silent resource recreation
silent drift acceptance
P10 permission/security implementation
Wren patch
P4 compiler patch
source branch merge/cherry-pick/rebase
```

## 14. Authorized P9A files

```text
backend/app/v3/resource_provisioning.py
backend/tests/test_v3_p9_resource_provisioning.py
.github/workflows/dima-metabase-p9.yml
backend/belgeler/metabase/predev/P9_PREDEVELOPMENT_REVIEW.md
backend/belgeler/metabase/tickets/P9_RESOURCE_PROVISIONER.md
backend/belgeler/metabase/*RECEIPTS*.md
DIMA-METABASE-DURUM.md
```

No P9A changes to `semantic_spec.py`, P7/P8 import/classification, substrate code, P5 receipts or
routing.

## 15. P9A focused gate

High-information cases:
- explicit DIMA_MANAGED native semantic -> CREATE;
- same applied fingerprint -> NOOP;
- overwrite drift -> UPDATE + rollback;
- reject drift -> REJECT_DRIFT;
- import-as-new-version -> versioned action + rollback;
- USER_MANAGED/EXTERNAL -> never mutating;
- same-name unbound resource -> never adopted;
- cross-tenant binding -> never reused;
- missing bound resource -> typed drift, no silent recreate;
- WREN_ONLY/UNSUPPORTED -> not provisionable;
- inventory order does not change plan fingerprint;
- duplicate binding key -> hard fail;
- unknown reconciliation -> validation fail.

No live Metabase stack for P9A.
