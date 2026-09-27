> **CURRENT RELEASE DISPOSITION — X0 NOT RUN / NOT REQUIRED**
>
> Bridge preflight terminal = `HEAVY_SEMANTIC_DUPLICATION`.
> Metabase structured analytical execution is rejected for the current release before X0 runtime.
> Wren semantics + analytical execution remain primary. This is a scoped architecture decision, not
> a permanent rejection of Metabase. See `DIMA_DAY6_5_X0_BRIDGE_PREFLIGHT.md` and the final Day6.5 handoff.

# DIMA DAY 6.5 — X0 THIN METABASE FEASIBILITY CONTRACT

**Date:** 2026-09-22  
**Status:** PREPARED / BLOCKED BY D65-SI FINAL + M0E-DEEP-DELTA + X0-BRIDGE-PREFLIGHT / NOT EXECUTED  
**Entry authority:** D65-SI FINAL + M0E-DEEP-DELTA FINAL + X0-BRIDGE-PREFLIGHT GREEN  
**Product integration:** FORBIDDEN  
**Primary-substrate decision:** NOT AUTHORIZED

## Precondition — D65-SI

X0 may not execute until `DIMA_DAY6_5_STANDARD_INTEGRATION_CLOSURE.md` is GREEN and the real
Standard Wren sentinel proves:

```text
AcceptedStandardAuthority
→ StandardProjection
→ Wren
→ QueryContract
→ Evidence
```

A Research `AcceptedTurnContract` surrogate is not valid X0 input.

## Mandatory pre-runtime bridge gate

Before any Metabase service/runtime X0:
`DIMA_DAY6_5_X0_BRIDGE_PREFLIGHT.md` MUST be GREEN.

Runtime spin-up is forbidden if the bridge requires manual metric/relationship redefinition,
label guessing, second semantic authority, or unapproved implicit FK joins.

Primary runtime surface, if preflight is GREEN, is `X0-REST` Agent API.
MCP query-handle semantics are a separate optional experiment and must not be conflated with REST.

## Purpose

Answer one bounded question:

> Can a separate Metabase Agent API service execute representative already-accepted Dima
> Standard projections under the same representative identity/permissions and return enough
> execution provenance for Dima to bind a trustworthy receipt, without becoming a second semantic
> authority or an equal production truth engine?

This is not a Metabot-vs-Dima cognition test.

## Isolation

```text
Dima AcceptedStandardAuthority
→ frozen representative StandardProjection
→ thin LAB adapter
→ separate Metabase service / Agent API
→ construct / validate / execute
→ raw result + Metabase execution identity
→ Dima-side X0 receipt
```

Current Wren production/incumbent path is unchanged.

Forbidden:
- production routing,
- Wren removal,
- raw-SQL shortcut,
- Metabase source copy/port/vendor,
- product semantic reparse,
- Metabase-issued Dima semantic handles,
- two equal production truth engines.

## Runtime pinning before first execution

X0 may not execute until the receipt records:

```text
metabase_source_reference_sha
metabase_runtime_version
metabase_immutable_image_digest
Dima tested SHA
X0 adapter SHA
X0 corpus version/hash
DB identity
principal/auth mode
permission/group snapshot
```

If any identity is unknown, X0 is INVALID / TRANSPORT-ENVIRONMENT rather than a substrate result.

## Identity rule

Use the same representative database and equivalent user-level permission context for Wren and
Metabase arms.

A group-scoped generic API key alone is insufficient to prove per-user fidelity.

Preferred evidence path:
- Metabase session for a dedicated representative user; or
- JWT only if the selected edition/runtime supports it and the exact deployment is pinned.

Never put credentials in repo or receipts.

## Representative corpus — 8 StandardProjection families

The X0 corpus is built from existing accepted Standard semantics; X0 does not parse raw language.

1. metric only
2. metric + one dimension
3. metric + filter
4. metric + period
5. metric + period + previous-period comparison
6. metric + dimension + ranking/limit
7. metric + two compatible dimensions
8. metric + filter + period + dimension

Selection rules:
- use only semantics already valid in the same representative Dima tenant;
- no Research/relationship/root-cause case;
- no unsupported/no-path join;
- no raw SQL;
- same frozen projection object/meaning goes to both substrate adapters;
- no case added or removed after first comparative result.

The concrete corpus is frozen only after the X0 runtime/DB identity is available, because opaque
Dima semantic handles are context/tenant-bound and must not be fabricated in a docs-only phase.

## Adapter boundary

Thin LAB adapter may know:
- how to translate a **sealed StandardProjection** into the supported Metabase Agent API
  construct representation;
- how to call construct/execute;
- how to capture response/handle/provenance into X0 receipt format.

Adapter may not know:
- raw user language,
- Dima semantic resolution policy,
- Research obligations/directives,
- model routing,
- Dima authority minting,
- SQL generation.

If translation requires reconstructing business semantics from labels/raw prompt, X0 fails the
architecture boundary.

## Mandatory negative/security cases

In addition to 8 positive projections:

1. principal loses table permission between construct and replay → replay must fail;
2. foreign/unreadable table/resource → no existence leak beyond authorized behavior;
3. structured-query path containing nested native SQL marker → reject;
4. stale/foreign query handle → reject;
5. Agent API disabled / auth invalid → typed environment/security failure, not semantic wrong.

## Measurements

For each Wren and Metabase arm:

```text
projection_id
Dima authority_id
principal identity fingerprint (non-secret)
permission snapshot id
construct success
execution success
result-shape match
numeric/result equivalence where comparable
executed-query provability
execution/handle identity
permission-revalidation evidence
QueryContract bindability
EvidenceArtifact bindability
p50/p95 latency
integration steps/errors
runtime/provider failures
```

P0:

```text
second semantic authority        = 0
raw SQL bypass                   = 0
permission bypass                = 0
cross-user handle access         = 0
unprovable executed query        = 0
Dima authority laundering        = 0
```

## Decision rule

X0 is **not promising** if:
- it cannot preserve representative permissions,
- construct/execute cannot be bound to Dima receipts,
- it requires semantic authority duplication,
- raw SQL is needed for representative Standard cases,
- integration complexity is clearly worse without material correctness/operability benefit.

Then:
```text
Wren remains primary
→ record X0 receipt
→ continue architecture closure
```

X0 is **promising** if it passes P0 and shows material evidence that the Agent API may improve
governed execution correctness, repairability, permission fidelity, provenance or operational
cost/complexity enough to justify full comparison.

Then:
```text
STOP
→ present M0 matrix + X0 receipt + preliminary Wren-vs-Metabase evidence
→ consult user
→ full D65-X only after explicit approval
```

No production substrate choice is made in X0.


---

## WREN_SEMANTIC_BACKBONE_RETENTION_DECISION

> **D65-X0 Wren'in MDL/cube semantic backbone'unu kaldırma deneyi değildir. İlk aşamada yalnız
> analytics execution/query-lifecycle overlap'ını ölçer. Wren semantic-layer retention ayrı bir
> architecture decision'dır.**

Binding implications:

```text
X0 MAY compare:
  StandardProjection → Wren execution/query lifecycle
  vs
  StandardProjection → Metabase construct/validate/execute lifecycle

X0 MAY NOT infer:
  "Metabase query execution works"
  ⇒ "Wren MDL/cube semantic backbone is redundant"
```

During X0:
- current Dima semantic authority remains `SemanticBindingGate + accepted authority`;
- existing Wren MDL/cube semantics may remain the semantic backbone even if Metabase is tested as
  an execution/query-lifecycle component;
- metric meaning, cube relationships, grain/additivity/unit/time semantics are not silently
  re-owned by Metabase;
- removing or replacing the Wren semantic layer requires a separate explicit architecture
  decision and consultation, with its own semantic-equivalence and migration evidence.

Therefore a promising X0 can justify a **full execution-substrate/query-lifecycle comparison**,
not automatic Wren semantic-layer removal.


---

## Residual-value / runtime-necessity override

X0's main question is now:

> Does Metabase runtime provide enough residual engineering value on top of Dima + retained Wren
> semantics to justify a permanent runtime dependency?

Primary arms:

```text
ARM A:
Dima + SAME retained Wren semantics
+ Wren execution/query lifecycle
+ accepted Dima-native Metabase-derived invariants

ARM B:
Dima + SAME retained Wren semantics
+ thin Metabase Agent API construct/validate/execute lifecycle
+ SAME Dima authority/evidence
```

### First-class semantic-duplication metrics

```text
manual_dual_semantic_definitions
semantic_sync_mechanisms_required
semantic_drift_risk
duplicate metric definitions
duplicate relationship definitions
duplicate grain/additivity definitions
duplicate time semantics
```

Target:
`manual dual semantic maintenance = 0`.

### Residual engineering-value metrics

Existing correctness/security metrics remain. Add:

```text
custom_code_avoided
custom_components_avoided
maintenance_surface_delta
adapter_LOC / conceptual complexity
metadata_sync_burden

new_deployable_services
new_persistent_state_DB
steady_RAM
cold_start
CPU_basic
network_overhead
upgrade_migration_surface
failure_blast_radius

new_DB_onboarding_burden
driver_connector_leverage
time_to_add_query_lifecycle_capability
```

### METABASE_RUNTIME_NECESSITY_GATE

X0 returns one of:

```text
METABASE_RUNTIME_NECESSARY = NO | FULL_X_REQUIRED
```

`NO`:
production Metabase runtime/Agent API rejected; Metabase remains reference/oracle/pattern source.

`FULL_X_REQUIRED`:
P0=0 plus material correctness/repair/permission/provenance/custom-code/product-runtime leverage;
STOP/CONSULT before full D65-X.

No single percentage/latency threshold determines this decision.


## Additional current P0

```text
unapproved_metabase_implicit_join       = 0
manual_metric_definition_duplication    = 0
manual_relationship_duplication         = 0
semantic_reparse_from_label             = 0
access_lens_mismatch_reuse              = 0
second_semantic_authority               = 0
```
