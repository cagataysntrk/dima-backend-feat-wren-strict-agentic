# P9B-001 — pinned Metabase resource transport

**Status:** SOURCE REVIEW COMPLETE / P9B1 METRIC CARD CONTRACT NEXT  
**Pinned source:** `metabase/metabase@2ba2485c78d7e00a9a25f82c00fc201da71590c4`

## Proven transport surfaces

Metric:
`Card(type=metric)` via POST/PUT/DELETE `/api/card`; `/api/metric` is read/query.

Dimension:
metadata on existing Field via PUT `/api/field/:id` and POST/DELETE
`/api/field/:id/dimension`; no generic standalone create resource.

Time:
no independent CRUD surface proven.

Relationship:
existing Field FK metadata only; no arbitrary Dima RelationshipSpec CRUD surface.

## Next gate

Provider-free P9B1 must prove an exact Dima metric desired-resource -> pinned Card persistence contract
without formula parsing or raw SQL. Other kinds remain typed transport gaps until separately proven.

No Metabase writes are authorized by this ticket yet.
