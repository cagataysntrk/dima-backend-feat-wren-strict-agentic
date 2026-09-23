# FT-005N — SEAM CORPUS V1 FREEZE RECEIPT

Status: FROZEN BEFORE NATIVE BEHAVIOR RESULTS
Date: 2026-09-23

Corpus:
`backend/eval/ft005n_seam_corpus_v1.json`

Boyahane source:
- repo: `cagataysntrk/metabase-boyahane`
- SHA: `f0c4a6b053ead52ca2eac80002c448323dc34a35`
- 80 tables / 462,962 rows.

Schema/date inventory evidence:
- run `35820722216` = GREEN;
- `satis_siparisleri.acilis_tarihi` range = 2023-11-28 .. 2026-06-22.

## Freeze rationale

The original synthetic Q1/Q2/Q3 chain is preserved exactly as a reference lane.

Boyahane's sales-order data ends in June 2026. Using the wall-clock phrase "son 30 gün" on
September 23, 2026 would create an empty-window confounder. Therefore the causal Boyahane lane
uses explicit June/May 2026 dates while preserving the same analytical capabilities:

```text
Q1 absolute-period SUM
Q2 contextual temporal replacement
Q3 contextual breakdown
```

No native Metabot answer, Fast answer, model output, or A/B/C benchmark result was used to choose
or edit these cases.

## Frozen families

Core:
- retrieval;
- temporal;
- SUM;
- follow-up;
- breakdown.

Extended:
- cross-language schema discovery;
- ambiguous entity;
- previous period;
- "same analysis" breakdown;
- broad analysis;
- self-contained topic switch;
- existing chart analysis;
- saved analytical asset reuse;
- query-error repair;
- contradictory follow-up;
- previous-result challenge / revalidation.

Fixture-dependent cases are explicitly marked and may produce SAFE_UNSUPPORTED if the arm naturally
cannot represent the capability.

## Mutation rule

After the first A0/A1/B/C behavioral result:
- case text cannot be edited;
- expected family cannot be changed;
- hidden oracle semantics cannot be changed;
- failures require receipts, not corpus repair.

A new experiment requires a new corpus version.
