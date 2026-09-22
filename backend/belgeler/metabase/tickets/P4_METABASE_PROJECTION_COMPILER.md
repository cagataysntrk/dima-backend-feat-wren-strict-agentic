# P4-001 — METABASE PROJECTION COMPILER

**Milestone:** P4  
**Predevelopment review:** `backend/belgeler/metabase/predev/P4_PREDEVELOPMENT_REVIEW.md`  
**Owner:** deterministic Dima semantic intent → canonical Metabase structured query  
**Status:** AUTHORIZED AFTER PREDEV GOVERNANCE GREEN

## Goal

Promote the P3A B-seam proof into one production compiler contract without creating a second semantic owner.

## Input

```text
ResolvedAnalyticsIntent
Dima-owned immutable execution binding snapshot
current catalog snapshot
```

## Output

```text
portable MBQL
canonical serialized MBQL
decoded canonical proof shape
semantic-slot manifest
source/resource fingerprints
```

## Hard invariants

```text
handle resolution in compiler           0
raw user language                       0
Metabase semantic search                0
label guessing                          0
LLM portable refs                       0
silent lineage rebind                   0
unapproved implicit joins               0
silent required-slot drop               0
production routing changes              0
```

## Explicit fail-closed areas

- cross-table relationships without approved Dima path;
- arbitrary metric formula translation;
- semantic NULL predicate absent typed upstream contract;
- typed numeric/non-equality filter absent typed upstream contract.

## Exit

P4 closure requires the focused proof matrix and pinned v0.63.18 canonicalization evidence.
