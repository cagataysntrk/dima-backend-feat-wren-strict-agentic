# P9-001 — Dima-managed semantic resource provisioner

**Milestone:** P9  
**Review:** `backend/belgeler/metabase/predev/P9_PREDEVELOPMENT_REVIEW.md`  
**Status:** P9A PROVIDER-FREE PLAN AUTHORIZED

## Goal

Build deterministic tenant-scoped desired-state planning before any Metabase mutation transport.

```text
DimaSemanticSpec + P8 matrix + ManagedResourcePolicy + ResourceInventory
→ ProvisionPlan
```

The plan owns identity, fingerprints, reconciliation, idempotency and rollback descriptors.

## Non-goals

No Metabase writes in P9A. No name search/adoption. No permissions. No formula parser. No Wren/P4
patches.

## P9B trigger

After P9A GREEN, inspect the exact v0.63.18 mutation API for each resource kind and add a narrow pinned
transport under a separate receipt/live canary. Do not generalize one resource endpoint across all
Metabase content.
