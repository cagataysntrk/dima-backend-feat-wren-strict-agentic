# P9B — PRE-DEVELOPMENT SOURCE/API REVIEW

**Milestone:** P9B — pinned Metabase semantic-resource transport  
**Branch:** `feat/dima-metabase-platform`  
**P9A hardening:** `7820ac77207f4245da150a5c80043d22708b87f0`  
**P9 workflow:** `35778418835 = SUCCESS`  
**Pinned Metabase:** `v0.63.18 / 2ba2485c78d7e00a9a25f82c00fc201da71590c4`  
**Ask-v2 relationship reference:** `b815d19cc8f07ecbd617e3e417e1405503a59542` — REFERENCE ONLY

Status: **SEALED / P9B SOURCE REVIEW COMPLETE / WRITE IMPLEMENTATION NOT YET AUTHORIZED**

## 1. Review rule

P9B source truth is the pinned Metabase commit, not current master and not documentation from another
release.

No live write is authorized by this review.

## 2. Explicit policy owner

P9B does not infer managed ownership from Wren, P8 classification, Metabase object type or names.

Canonical policy owner is the existing:
`DimaSemanticSpec.managed_resources -> ManagedResourcePolicy`.

The transport consumes only an already-explicit Dima policy. If the canonical spec has no
`DIMA_MANAGED` policy for a semantic ref, P9B creates/updates/deletes nothing.

How a production semantic/tenant configuration materializes that explicit policy is upstream of the
transport and must not be invented from substrate state.

## 3. Metric — Card-backed resource surface

Pinned source:
- `src/metabase/metrics/api.clj`: GET `/api/metric` and GET `/api/metric/:id` read Cards with
  `type="metric"`; `/api/metric/dataset` is execution, not CRUD.
- `src/metabase/queries_rest/api/card.clj`: POST `/api/card` creates Cards and explicitly allows
  `type=metric`; PUT `/api/card/:id` updates; PUT with `archived=true` is soft archive;
  DELETE `/api/card/:id` hard-deletes.
- Card creation requires a valid `dataset_query`, display, visualization settings and name; optional
  `entity_id` and collection are supported.
- Create checks include query run permissions and collection create permission.
- Update/delete require Card write permission; query changes re-check data/query permissions.
- `src/metabase/queries/models/card.clj` derives Card from `:hook/entity-id`.
- `src/metabase/models/interface.clj` generates a NanoID on insert only when `entity_id` was not
  already supplied.

Identity implication:
after create, P9 may bind both numeric Card id and stable Card `entity_id`; Dima canonical id remains
the authoritative semantic id.

### Metric blocker before write code

Current P9 `DesiredResource` contains canonical semantic payload, not a proven Card
`dataset_query` persistence projection.

P4 proves deterministic query execution construction, not that its serialized execution query can be
stored unchanged as a metric Card.

Therefore metric REST write code is **not authorized yet**. First prove a provider-free
`DesiredMetricResource -> CardCreateContract` mapping against the exact pinned Card schema, then one
isolated live create/read/archive/restore/delete canary.

No raw SQL or formula parser may be introduced to build the Card query.

## 4. Dimension — existing Field metadata, not standalone content

Pinned `src/metabase/warehouse_schema_rest/api/field.clj`:
- PUT `/api/field/:id` mutates metadata on an existing synced Field and requires Field write access;
- POST `/api/field/:id/dimension` creates/updates a Dimension record attached to that Field;
- DELETE `/api/field/:id/dimension` removes that attached Dimension;
- external remapping may require an exact human-readable target Field id.

There is no generic standalone create-Dima-dimension content resource analogous to Card.

Initial disposition:
`P9B_DIMENSION_TRANSPORT_GAP` until P9 proves an exact current-catalog Field binding and an owned
metadata subset. Same-name field search/adoption is forbidden.

## 5. Time — no independent resource CRUD surface proven

A Dima TimeSpec currently points at a dimension. The reviewed pinned source does not expose an
independent create/update/archive Time resource.

Initial disposition:
`P9B_TIME_TRANSPORT_GAP`.

A future mapping may intentionally use exact Field metadata, but only under its own contract; it may
not pretend time is a Card-like resource.

## 6. Relationship — no generic Dima relationship object surface

Pinned Field metadata can set `fk_target_field_id`/semantic relationship type on an existing Field.
That is physical metadata mutation, not an arbitrary Dima relationship object.

Current real P7 import also has:
`31 RELATIONSHIP_JOIN_KEY_GAP` and zero portable RelationshipSpec with exact join keys.

Initial disposition:
`P9B_RELATIONSHIP_TRANSPORT_GAP`.

No Wren textual `condition` may be transported or parsed to manufacture FK mutation.

## 7. Table surface is metadata-only for existing synced tables

Pinned `src/metabase/warehouse_schema_rest/api/table.clj` PUT endpoints edit metadata for existing
Tables and require write access. They do not create canonical semantic tables from Dima specs.

P9B must not use table metadata endpoints as a generic semantic resource provisioning escape hatch.

## 8. Required next implementation slice

Before any live mutation:

```text
P9B1 provider-free metric Card contract
DesiredResource(kind=METRIC)
+ explicit DIMA_MANAGED policy
+ exact current resource/catalog binding where needed
→ exact Card create/update/archive contract OR typed transport gap
```

The contract must prove:
- no formula parsing;
- no name search/adoption;
- no raw SQL;
- explicit collection destination;
- exact pinned Card body keys;
- Dima canonical id remains separate from Card local/entity ids;
- rollback maps to archive/restore or exact prior snapshot;
- dimension/time/relationship remain typed transport gaps unless separately proven.

Only after P9B1 provider-free GREEN may one isolated pinned-live metric mutation canary be proposed.

## 9. Forbidden

- one generic CRUD endpoint for all semantic resource kinds;
- POST/PUT based on resource display name;
- field/table search by similar name;
- treating `/api/metric/dataset` as metric persistence;
- using Wren relationship condition as FK payload;
- assuming current master API equals v0.63.18;
- writes before a sealed P9B1 contract;
- source branch merge/cherry-pick/rebase.
