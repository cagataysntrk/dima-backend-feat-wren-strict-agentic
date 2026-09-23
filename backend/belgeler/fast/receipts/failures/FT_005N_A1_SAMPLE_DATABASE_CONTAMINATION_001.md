# FT-005N FAILURE RECEIPT — A1_SAMPLE_DATABASE_CONTAMINATION_001

Status: ROOT CAUSE CONFIRMED
Date: 2026-09-23

Observed run:
`35821250965`

Tested SHA:
`2dd6999cedd106007d02f9a249b0f390fe276ae6`

Workflow conclusion:
`GREEN`

Important:
workflow GREEN means the stock native endpoint and stream harness operated successfully.
It does NOT mean the analytical answer was correct.

## What passed

- provider-free native stream parser = GREEN;
- frozen corpus integrity = GREEN;
- frozen Boyahane checkout = GREEN;
- exact pinned Metabase image digest = GREEN;
- runtime version = v0.63.18;
- stock /api/metabot/settings accepted OpenRouter + openai/gpt-5.6-luna;
- no license bypass;
- no feature-gate patch;
- no Metabase source patch;
- POST /api/metabot/agent-streaming = HTTP 202;
- native iterative tool loop executed:
  load_skill -> search -> search -> read_resource x3 -> construct_notebook_query x3;
- generated_entity + state returned;
- state contains charts/link-registry/queries.

## Analytical contamination observed

The generated Q1 link encoded:

```text
database = 1
source-table = 2
aggregation = SUM(field 5)
date filter = field 13
```

The native answer explicitly described:

```text
ORDERS
TOTAL
CREATED_AT
```

Frozen Boyahane schema inventory proves:
- no `orders` table;
- target table = `satis_siparisleri`;
- target measure = `toplam_tutar`;
- target date = `acilis_tarihi`.

Therefore the agent selected Metabase's automatically loaded Sample Database instead of the
Boyahane causal-control database.

## Classification

`HARNESS / CONTROL_METADATA_CONTAMINATION`

This is NOT yet:
- NATIVE_METABOT_SEMANTIC_WRONG;
- FAST_PASS_NATIVE_FAIL;
- NATIVE_PASS_FAST_FAIL;
- model-quality evidence.

The A1 fairness condition requires the same intended source DB, not an extra sample database.

## Root cause

Metabase defaults `MB_LOAD_SAMPLE_CONTENT` to true on fresh installs.

Pinned v0.63.18 source:
`src/metabase/config/core.clj / load-sample-content?`

The A1 compose did not disable sample content.

## Authorized correction

A1 harness only:
1. set `MB_LOAD_SAMPLE_CONTENT=false`;
2. after setup, enumerate Metabase analytical databases;
3. fail closed unless Boyahane is present and no Sample Database is present;
4. rerun the unchanged frozen Q1.

Forbidden:
- prompt patch;
- model patch;
- corpus edit;
- Fast product change;
- Metabase source patch;
- license bypass.

## Re-proof

The next Q1 is evaluable only if:
```text
database inventory = Boyahane only
Sample Database = 0
exact image digest = same
exact model/provider = same
question = unchanged
```
