# DIMA DAY 6.5 — X0 THIN METABASE FEASIBILITY CONTRACT

**Date:** 2026-09-22  
**Status:** PREPARED / NOT EXECUTED  
**Entry authority:** D65-M0 receipt + pre-freeze decision gate  
**Product integration:** FORBIDDEN  
**Primary-substrate decision:** NOT AUTHORIZED

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
