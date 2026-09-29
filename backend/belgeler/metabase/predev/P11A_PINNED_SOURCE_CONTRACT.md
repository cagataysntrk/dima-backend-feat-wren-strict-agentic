# P11A — PINNED METABASE VALUE-RETRIEVAL SOURCE CONTRACT

**Metabase tag:** `v0.63.18`  
**Exact commit:** `2ba2485c78d7e00a9a25f82c00fc201da71590c4`  
**Decision:** `DMP-DEC-0026`  
**Status:** SEALED / SOURCE CONTRACT ONLY

## Proven pinned surfaces

### Current-user field values

`GET /api/field/:id/values`

Pinned source:
- `src/metabase/warehouse_schema_rest/api/field.clj`
- `src/metabase/parameters/field_values.clj`

The endpoint applies `api/query-check` to the Field and delegates to current-user FieldValues.
The returned shape carries `values`, `field_id`, and `has_more_values`.
Human-readable remapping is preserved as `[original, display]` pairs when configured.

### Search

`GET /api/field/:id/search/:search-id`

Pinned source requires both the base field and search field to be readable. If `value` is omitted,
an explicit request limit is required. Search is a value-retrieval surface, not semantic authority.

### Advanced current-lens identity

Pinned `hash-input-for-field-values` includes:
- field identity;
- sandbox context;
- impersonation context;
- linked-filter constraints;
- database-routing context.

This demonstrates that advanced FieldValues cache identity is lens-sensitive. It does **not** certify
those advanced enterprise capabilities in the current OSS lab; P10B2 classifications remain binding.

## P11 logical tool boundary

The LLM-facing logical contract is:

```text
lookup_dimension_values(
  semantic_ref,
  query?,
  limit
)
```

The model never receives or invents:
- Metabase numeric field ids;
- physical database field identity;
- tenant routing;
- security lens identity.

A Dima adapter owns:
`semantic_ref -> exact current physical field locator`.

The retrieval surface returns bounded evidence only. It does not make the final semantic decision.

## P11 V1 evaluation mode

EV-01..EV-04 are low-cardinality. To preserve the supervisor's 8-primary-call budget, V1 preloads
current-user values for only the case's already-governed semantic scopes before the single model
decision. The model then returns `BIND | CLARIFY | NO_MATCH`.

This does not certify model-driven search-term selection. If later necessity evidence requires search,
the same logical boundary may use the pinned search endpoint without exposing physical identifiers.

Indexed entities are explicitly **not required** for V1.
