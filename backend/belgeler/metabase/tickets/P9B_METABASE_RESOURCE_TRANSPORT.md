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


## DMP-DEC-0023 — P9B1 metric create boundary

Pinned Agent API already accepts the exact base64 MBQL produced by `construct-query`.
P9B1 therefore does not synthesize Card `dataset_query` independently.

Next implementation:
provider-free `ProvisionAction(CREATE metric) + CanonicalProjection + explicit collection_id
→ MetricCreateContract`.

No HTTP mutation yet.


## Identity hardening — DMP-P9B-AUDIT-002

P9B1 transport contract is tenant-bound and retains the existing P4 projection/catalog provenance:
`tenant_binding`, `projection_hash`, `resolved_intent_hash`,
`current_catalog_fingerprint`, and `canonical_query_fingerprint`.

The explicit target must carry the same tenant as the desired P9 resource. No tenant/collection
discovery or default target is authorized.


## Isolated live proof authorization

After DMP-P9B-AUDIT-002 provider-free GREEN, exactly one pinned v0.63.18 lab lifecycle is authorized:
fresh P4 projection → P9 CREATE → tenant-bound P9B contract → exact create response id → exact-id
Card read-back → stable binding → P9 NOOP → archive → exact-id read → restore → exact-id read →
hard-delete cleanup.

No search/list/name adoption is permitted. This is a lab proof, not production write authorization.
