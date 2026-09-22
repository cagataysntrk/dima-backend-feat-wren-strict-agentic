# FT-003 FAILURE RECEIPT — MODEL_RETRIEVAL_RED_002

Status: ROOT CAUSE CONFIRMED
Date: 2026-09-22

OBSERVED_RUN:
`35776185321`

OBSERVED_SHA:
`1ddbf7805fa3cf71062ed0590801511a35f8dae1`

MODEL:
`google/gemini-2.5-flash-lite`

FAILURE_CLASS:
`RETRIEVAL_CONTRACT`

## What passed

- structured schema;
- typed supported/unsupported contract;
- aggregation selection;
- temporal intent;
- opaque resource/field handle discipline;
- invented IDs = 0;
- ambiguity model abstention remained diagnostic-only;
- several Turkish prompts produced direct Metabase SEARCH hits.

## Failed families

The certification-grade retrieval diagnostic required:
`metadata_search_direct_hit = true`

Failures:

1. `breakdown_last_n_days`
   - question: Turkish SUM-by-region order request
   - model mixed table retrieval with measure/dimension terms;
   - observed family included terms such as entity+measure phrase / region;
   - direct table search missed and bounded catalog fallback recovered.

2. `sum_previous_month`
   - question: Turkish previous-month SUM request
   - model returned user-language entity/measure/operation terms without a useful English entity/table alias;
   - direct table search missed and bounded catalog fallback recovered.

## Root cause

The first generic prompt revision improved cross-language retrieval, but remained too permissive.

It said to:
- identify the primary entity;
- include likely English equivalents;
- avoid measure/dimension pollution.

The model still had freedom to:
- emit entity+metric phrases rather than a standalone entity lookup term;
- omit English entity/table terminology on some non-English questions;
- emit operation words such as count/total as table-search terms.

This is a generic retrieval-contract weakness, not a missing Turkish phrase mapping.

## Authorized correction

Tighten the same existing `search_terms` semantics:

- every search term must independently help retrieve the primary business/data entity;
- search terms are for table/resource discovery only;
- do not emit aggregation/operation terms;
- do not emit measure or breakdown/dimension terms unless strictly required to distinguish the resource;
- do not combine the entity with a metric/dimension into a retrieval phrase when a standalone entity term is available;
- for non-English user questions, include at least one likely English entity/table lookup term;
- keep useful user-language entity terminology where helpful;
- maximum four terms.

## Forbidden

- Turkish->English dictionary;
- `sipariş -> orders` hardcode;
- synonym registry;
- ontology;
- regex phrase repair;
- question-specific prompt examples;
- expansion of FT-003 query family.

## Re-proof

Re-run the same real-model retrieval sentinel.

Required:
- all supported cases `metadata_search_direct_hit = true`;
- candidate_count/candidate_names/candidate_uris recorded;
- correct opaque selected handle;
- invented IDs = 0.
