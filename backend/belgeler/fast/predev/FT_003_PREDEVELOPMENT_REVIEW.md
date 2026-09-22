# FT-003 — FIRST REAL DIMA ASK VERTICAL SLICE PRE-DEVELOPMENT REVIEW

Status: APPROVED
Branch: `feat/dima-metabase-product-fast-track`
Observed HEAD: `1e60d4882ee785d0897635a43ab7cfa733ab0ad6`
Date: 2026-09-22

## 1. Goal

Build the first real Dima product slice:

```text
Turkish user question
-> bounded cognition
-> Metabase candidate discovery
-> deterministic authority binding
-> typed temporal binding
-> deterministic portable query
-> FastMetabaseGateway construct + execute
-> evidence
-> Dima answer
-> Option-A Dima-native chart/table result
```

This must be a real query against the pinned Metabase OSS substrate.

## 2. Product boundary

```text
DIMA     = user-facing analyst product
METABASE = hidden analytics engine
```

No generic Metabase UI is introduced.

## 3. Supported family for FT-003

Intentionally narrow:

```text
SOURCE:
  exactly one Metabase table

AGGREGATION:
  COUNT rows
  or SUM one numeric field

TIME:
  optional one date/datetime field
  with one supported typed period

BREAKDOWN:
  optional one same-table field

OTHER FILTERS:
  none in FT-003

JOINS:
  none

RAW SQL:
  forbidden
```

Supported period kinds:
- NONE
- LAST_N_DAYS
- CURRENT_MONTH
- PREVIOUS_MONTH
- ABSOLUTE_DATE_RANGE

Bounds are deterministic and inclusive/exclusive as documented below.

Example target prompts:
- "Son 30 günde kaç sipariş var?"
- "Son 30 gündeki sipariş tutarı ne kadar?"
- "Son 30 günde bölgelere göre sipariş tutarı"
- "Eylül 2026 sipariş sayısı" only if model normalizes it to explicit absolute bounds.

The family is not expanded merely because the model asks for more.

## 4. Cognition vs authority

LLM/model may do only bounded cognition:

### Draft cognition

Model returns:
- search terms;
- operation: COUNT | SUM;
- measure hint for SUM;
- optional breakdown hint;
- typed temporal intent.

It does NOT return:
- Metabase numeric IDs;
- portable FKs;
- MBQL;
- SQL;
- answer numbers.

### Resource selection

Metabase search creates a bounded candidate set.

Dima converts candidates to opaque handles:
`fast_res_*`

Selection model returns only:
- one provided handle;
- or ABSTAIN.

If one exact unique safe table candidate is deterministically sufficient, model selection may be skipped.

### Field selection

After `metabase://table/{id}/fields`, Dima creates bounded field candidates:
`fast_field_*`

The model selects only handles for:
- SUM measure;
- temporal field;
- optional breakdown.

No field name/ID invented by the model becomes authority.

### Authority

Only deterministic Fast code turns accepted handles into:
- exact database/schema/table names;
- exact portable field FKs;
- exact dates;
- exact MBQL external query.

## 5. Temporal contract

Fast-owned temporal engine.

Initial request-level anchor:
`as_of_date`

Production default can later derive from authenticated user timezone/current date.
Tests/live proof pass an explicit anchor for reproducibility.

Semantics:

### LAST_N_DAYS

For anchor date D and N:

```text
start = D - (N - 1) days
end_exclusive = D + 1 day
```

Filter:
`field >= start AND field < end_exclusive`

### CURRENT_MONTH

```text
start = first day of anchor month
end_exclusive = first day of next month
```

### PREVIOUS_MONTH

```text
start = first day of previous month
end_exclusive = first day of anchor month
```

### ABSOLUTE_DATE_RANGE

Model supplies ISO start and ISO end dates.
Backend validates and converts:

```text
start inclusive
end_exclusive = supplied end + 1 day
```

Model never performs final calendar arithmetic.

## 6. Query builder

Fast deterministic builder emits canonical portable MBQL 5.

Field ref:

```json
["field", {}, ["DB", "SCHEMA", "TABLE", "FIELD"]]
```

COUNT:

```json
"aggregation": [["count", {}]]
```

SUM:

```json
"aggregation": [["sum", {}, <accepted-measure-field-ref>]]
```

Temporal filter:

```json
"filters": [[
  "and", {},
  [">=", {}, <accepted-time-field-ref>, "YYYY-MM-DD"],
  ["<",  {}, <accepted-time-field-ref>, "YYYY-MM-DD"]
]]
```

Optional breakout:

```json
"breakout": [[
  "field", {}, <accepted-breakdown-field-portable-fk>
]]
```

No model-authored portable query is accepted in FT-003.

Before execution:
`FastMetabaseGateway.construct_query()`

Then:
`execute_serialized()`

This proves both construction and execution paths.

## 7. Result / evidence contract

Every successful Ask returns an evidence record containing at least:
- evidence_id;
- question;
- selected resource handle + stable Metabase resource ref;
- selected field identities;
- exact time bounds;
- canonical portable query;
- query fingerprint;
- access fingerprint;
- Metabase runtime version;
- result columns;
- result rows;
- row_count;
- result digest.

The opaque encoded query returned by Metabase is not exposed to the model.

## 8. Answer contract

FT-003 answer generation is deterministic.

No narrative LLM is required.

COUNT scalar:
> "Sonuç: <N> kayıt."

SUM scalar:
> "Sonuç: <value>."

Breakdown:
> "<K> kırılım döndü."

Numeric values are copied from the validated Metabase result only.

No cause/recommendation/forecast is generated.

This makes:
`silent numeric hallucination = 0 by construction`

## 9. Rendering contract

Response result shape is normalized into the existing Fast POC `QueryResult` form.

Option A remains:
`Dima-native EChart + ResultTable`

For scalar results:
- value card / table-safe representation;
- no fake chart.

For breakdown:
- chart when safely chartable;
- table always available.

## 10. Fast-owned modules

Allowed new backend owners:

```text
backend/app/fast/
├── ask_models.py
├── ask_errors.py
├── ask_cognition.py
├── resource_registry.py
├── temporal.py
├── query_builder.py
├── evidence.py
├── ask_service.py
├── router.py
└── application.py
```

Names may be narrowed during implementation; ownership must remain `app.fast`.

## 11. Common infrastructure allowed

Read/reuse:
- `app.config`
- `app.llm.build_generator` only as provider transport for structured JSON, never SQL generation
- `app.kaset.belki_sar` only if needed for existing provider guard
- `app.auth.dependencies.get_current_principal`
- `control_plane.security`
- `control_plane.authorize.Principal`

Forbidden runtime imports:
- `app.v2.*`
- `app.v3.*`
- Wren owners
- legacy ask orchestrators
- legacy SemanticResolver

If common `app.llm` import is shown to pull prohibited runtime owners, stop and replace it with a Fast-specific provider adapter rather than weakening the boundary.

## 12. Fast-only application proof

FT-003 must be provable without starting the legacy Wren-owned `app.main`.

Preferred test/proof owner:
`app.fast.application`

The Fast-only app may include:
- Fast Ask router;
- existing auth dependency machinery if required;
- Fast health endpoint.

It must not instantiate Wren, V2, or V3.

Later production integration into a shared process is a separate deployment decision.

## 13. Metabase auth in FT-003 proof

Server-side only.

Live CI obtains a Metabase session for the synthetic lab and constructs:
`FastMetabaseAuthContext`

No Metabase credential reaches browser.

Dima principal and Metabase principal remain separate explicit contexts.

## 14. Model provider architecture

Define a Fast-owned cognition protocol.

Provider-free tests use a scripted structured cognition implementation.

Real runtime adapter may wrap the common structured-json provider.

The planner response is Pydantic-validated and fail-closed.

If no structured model provider is configured:
- typed `COGNITION_UNAVAILABLE`;
- no rule/regex semantic fallback;
- no SQL fallback.

FT-003 live Metabase correctness proof does not require an external paid LLM secret in CI; it uses the exact same bounded contracts with a scripted cognition provider.

A later model-in-loop sentinel is required before pilot, but CI absence of provider credentials must not make query/evidence correctness untestable.

## 15. Clarification / abstention

Return typed non-success outcomes:
- UNSUPPORTED
- CLARIFICATION_REQUIRED
- NO_RESOURCE
- AMBIGUOUS_RESOURCE
- NO_MEASURE_FIELD
- NO_TEMPORAL_FIELD
- COGNITION_UNAVAILABLE

Do not silently choose a materially ambiguous candidate.

## 16. Files allowed

Backend:
- new `backend/app/fast/**` FT-003 owners;
- `backend/tests/test_fast_ask*.py`;
- Fast-specific workflow;
- Fast docs/receipts.

Frontend:
- isolated `dima-frontend-demo-master/src/app/fast-poc/**`;
- `src/features/fast-poc/**`;
- focused fast-poc E2E.

Minimal shared registration:
- NOT required for initial proof if Fast-only application is used.

## 17. Files forbidden

- legacy `backend/app/main.py` unless a later explicit integration predev authorizes it;
- `backend/app/v2/**`;
- `backend/app/v3/**`;
- Wren files;
- legacy Ask routers;
- source branches;
- main frontend page;
- DashboardView/DashboardsPanel;
- Metabase source;
- raw SQL path.

## 18. Provider-free test matrix

At minimum:

Cognition:
- schema-invalid model response rejected;
- invented candidate handle rejected;
- ABSTAIN -> clarification;
- SUM without measure -> fail closed.

Temporal:
- LAST_N_DAYS exact bounds;
- current month boundary;
- previous month across year boundary;
- absolute range;
- invalid N/range rejected.

Registry:
- opaque handles stable within request;
- unknown handle rejected;
- no raw ID accepted from model.

Builder:
- COUNT query exact;
- SUM query exact;
- date filter exact;
- breakout exact;
- no SQL/native query;
- no join.

Evidence:
- deterministic query/result digest;
- access fingerprint included;
- number in answer originates from result.

Service:
- happy COUNT;
- happy SUM;
- breakdown;
- no resource;
- ambiguous resource;
- missing field;
- Metabase execution failure;
- empty result.

API:
- unauthenticated -> 401;
- authenticated -> response;
- malformed question -> 422.

## 19. Live pinned-Metabase sentinel

Synthetic `orders` table.

Use explicit reproducible anchor:
`2026-09-07`

Required live prompts/contracts:

1. COUNT:
`"Son 30 günde kaç sipariş var?"`

Expected deterministic window:
`2026-08-09 <= order_date < 2026-09-08`

Expected lab count:
derive from DB; do not hardcode before execution.

2. SUM:
`"Son 30 gündeki sipariş tutarı ne kadar?"`

Use accepted:
- table = orders
- measure = amount
- temporal = order_date

3. BREAKDOWN:
`"Son 30 günde bölgelere göre sipariş tutarı"`

Use accepted:
- breakdown = region

For each:
- Agent API search;
- table fields read;
- portable query constructed deterministically;
- construct-query succeeds;
- execute succeeds;
- evidence written in response;
- answer numbers equal result.

## 20. Frontend/browser proof

Evolve isolated `/fast-poc` only after backend service gate is green.

User enters a prompt.

Browser:
- calls Fast Ask endpoint;
- shows loading;
- shows deterministic answer;
- shows evidence/provenance summary;
- shows appropriate chart/table;
- no fake result;
- no Metabase workspace.

Required viewport:
- 1440x900;
- 390x844.

## 21. Hard GREEN gate

- [ ] Fast cognition contracts
- [ ] opaque resource/field handles
- [ ] deterministic temporal engine
- [ ] deterministic portable query builder
- [ ] real Fast Gateway construct + execute
- [ ] evidence
- [ ] deterministic answer
- [ ] provider-free tests
- [ ] no V2/V3/Wren runtime import
- [ ] live COUNT
- [ ] live SUM
- [ ] live BREAKDOWN
- [ ] API auth negative/positive proof
- [ ] isolated browser Ask proof
- [ ] chart/table result proof
- [ ] no paid Metabase dependency
- [ ] no raw SQL
- [ ] receipt sealed

## 22. Exit

When GREEN:
FT-003 closes.

Then proceed according to roadmap:
- conversation;
- evidence expansion;
- Analyst;
- Root Cause.

Do NOT begin Analyst or Root Cause inside FT-003.
