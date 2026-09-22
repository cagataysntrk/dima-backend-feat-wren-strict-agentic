# P4-001 — METABASE PROJECTION COMPILER

**Milestone:** P4  
**Predevelopment review:** `backend/belgeler/metabase/predev/P4_PREDEVELOPMENT_REVIEW.md`  
**Owner:** deterministic Dima semantic intent → canonical Metabase structured query  
**Status:** EXECUTION BINDING GREEN / COMPILER PRE-IMPLEMENTATION REVIEW REQUIRED

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


---

## Binding promotion stop-the-line

Before `compiler.py` or `canonical.py` may be created, DMP-P4-RED-001 must close GREEN.

Required end state:
```text
execution_binding.py = only owner of binding primitives
p3a_models.py        = P3A result/report models + exact production re-exports
P3A consumers        = production binding types
CurrentCatalog       = explicit governed observation, never search-derived
P4 binding workflow  = GREEN
```


---

## Execution-binding gate closure

```text
binding HEAD                   1771becb3e59395cf28f993345703449feb9a98d
P4 workflow                    35742516216 = SUCCESS
focused binding                18 passed
provider-free regressions      40 passed
real Wren regression           5 passed
pinned-live P3/P3A             2 passed
P3A workflow                   35742516331 = SUCCESS
P3 workflow                    35742516120 = SUCCESS
M1 workflow                    35742516339 = SUCCESS
governance                     35742516356 = SUCCESS
```

DMP-P4-RED-001: **CLOSED GREEN**.

Compiler remains not-started until the mandatory compiler pre-implementation re-read/review is sealed.
