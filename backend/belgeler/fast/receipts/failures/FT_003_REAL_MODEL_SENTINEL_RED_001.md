# FT-003 FAILURE RECEIPT — REAL_MODEL_SENTINEL_RED_001

Status: ROOT CAUSES CLASSIFIED
Date: 2026-09-22

OBSERVED_RUN:
`35773339156`

OBSERVED_SHA:
`9d8fa373d34a4dfc91e16ba73cfceed75ad0d258`

MODEL:
`google/gemini-2.5-flash-lite`

PROVIDER:
`OpenRouter / existing structured_json transport`

WORKERS:
`1 / sequential`

TRANSPORT:
`PASS`

SCHEMA TRANSPORT:
`PASS`

INVENTED_ID_COUNT:
`0`

## Failure family A — retrieval contract

The model correctly produced typed intent for supported cases, including:
- COUNT;
- SUM;
- LAST_N_DAYS;
- CURRENT_MONTH;
- PREVIOUS_MONTH;
- ABSOLUTE_DATE_RANGE.

But it naturally produced Turkish metadata terms such as:
- `sipariş`;
- `tutar`.

FastAskService currently sends only:
`term_queries=draft.search_terms`.

Pinned Metabase table metadata is English (`orders`), so the term-only search returned no supported table candidate in these cases.

Classification:
`RETRIEVAL_CONTRACT`

Generic correction:
use Metabase's supported semantic search surface with the original user question in addition to bounded term queries.

Forbidden:
phrase-specific English translation tables.

## Failure family B — ambiguity abstention

Given two plausible opaque resource candidates and a generic question, the real model selected:
`fast_res_001`

instead of abstaining.

Classification:
`AMBIGUITY_ABSTENTION`

Generic correction:
- authority must remain fail-closed when multiple resource candidates are materially unresolved;
- candidate ordering/rank is not authority;
- selection prompt may be strengthened generically to require explicit distinguishing evidence, not phrase-specific examples.

## Failure family C — unsupported contract

Question:
`Siparişlerin ortalama tutarı nedir?`

FT-003 supports only COUNT/SUM.

Current `AskDraft` cannot express UNSUPPORTED, so strict schema forced the model into:
- aggregation = SUM
- measure_hint describing a workaround

Classification:
`UNSUPPORTED_CONTRACT`

Generic correction:
the typed draft must explicitly represent whether the request is inside FT-003's supported family.
Service must stop before metadata/query execution when unsupported.

Forbidden:
- detect AVG with regex/phrase list;
- reinterpret AVG as SUM;
- expand FT-003 to AVG;
- raw SQL fallback.

## Patch boundary

Allowed:
- Fast-owned AskDraft contract;
- StructuredJsonFastCognition generic prompt;
- FastAskService search/authority gate;
- focused tests;
- real-model sentinel.

Forbidden:
- Wren/V2/V3;
- joins;
- arbitrary filters;
- new aggregation types;
- phrase patches;
- Analyst/Research/Root Cause.

## Re-proof

Run the same small real-model sentinel, workers=1.

Required:
- supported typed intents correct;
- search discovers the real orders candidate;
- correct resource/field opaque handles;
- ambiguity fails closed;
- unsupported becomes typed UNSUPPORTED;
- invented ID = 0.


## Observation 2 — run 35774170106

Observed SHA:
`6d495e97542e5927f76fc6e74d6b036322468c81`

The second real-model run confirmed the remaining dominant failure as metadata retrieval language alignment.

Model behavior that passed:
- strict schema;
- typed SUPPORTED/UNSUPPORTED;
- COUNT/SUM;
- LAST_N_DAYS;
- CURRENT_MONTH;
- PREVIOUS_MONTH;
- ABSOLUTE_DATE_RANGE;
- invented IDs = 0;
- AVG -> typed UNSUPPORTED.

Observed retrieval failure:
Turkish metadata lookup terms such as `sipariş`, `sipariş tutarı`, and `bölge` did not directly match the pinned English table metadata `orders`.

Classification:
`RETRIEVAL_LANGUAGE_METADATA_ALIGNMENT`

The ambiguity expectation was also refined: model abstention is diagnostic; the hard safety gate belongs to FastAskService.

## Partial closure — run 35775125029

Tested SHA:
`1adc55467a02363db9a1fb76c09615a568696c35`

Result:
`GREEN`

This run proves:
- real structured model transport works;
- supported typed cognition passes;
- resource/field opaque handle selection passes;
- typed UNSUPPORTED passes;
- invented IDs = 0;
- bounded metadata catalog fallback safely recovers cross-language lookup in the one-table FT-003 lab.

However this does NOT fully close FT-003 because:
1. many Turkish cases still reported `direct_search_hit=false`;
2. the sentinel explicitly does not execute analytics queries;
3. primary real-model -> real-Metabase -> DB-oracle E2E is still pending.

Therefore this failure receipt is root-cause closed at the diagnostic layer but FT-003 remains OPEN until the final model E2E seal.
