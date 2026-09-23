# FT-005 LIVE RECEIPT — RETRIEVAL_LANGUAGE_SEARCH_PROBE_001

Status: GREEN / PRODUCT IMPACT CONFIRMED
Date: 2026-09-23
Branch: `feat/dima-metabase-product-fast-track`

RUN:
`35817396762`

TESTED_SHA:
`f7c74d7a7b2127e14c3fd1680e70588a68352a75`

ARTIFACT:
`sha256:39b584620675917648ce8f43e7d73b4f1c95a97620b4fa97920d7535094d0b41`

Pinned Metabase:
`REAL OSS LAB`

Synthetic target table:
`orders`

Question:
`Son 30 günde sipariş tutarı ne kadar?`

## Measured direct SEARCH behavior

| term_queries | direct orders hit | combined semantic-query hit | Fast discovery |
| --- | --- | --- | --- |
| `["sipariş"]` | NO | NO | CATALOG_FALLBACK |
| `["siparişler"]` | NO | NO | CATALOG_FALLBACK |
| `["sipariş","siparişler"]` | NO | NO | CATALOG_FALLBACK |
| `["sipariş","order"]` | YES | YES | SEARCH |
| `["order"]` | YES | YES | SEARCH |
| `["orders"]` | YES | YES | SEARCH |
| `["sipariş tutarı"]` | NO | NO | CATALOG_FALLBACK |

## Conclusion

`RETRIEVAL_DRIFT_PRODUCT_IMPACT = CONFIRMED`

The frozen semantic oracle was not merely requiring cosmetic English wording.

Against the actual pinned Metabase metadata catalog:
- Turkish-only order terms do not directly retrieve the English `orders` table;
- the Turkish metric phrase does not retrieve it;
- a likely English entity/table lookup term does;
- the mixed Luna output `["sipariş","order"]` preserves user-language terminology while still hitting SEARCH directly.

The current catalog fallback can recover the only permitted table in this tiny synthetic fixture.
That does NOT eliminate the retrieval defect because:
- direct SEARCH contract is missed;
- broader real catalogs can contain multiple permitted tables;
- fallback can become ambiguous;
- fallback should remain bounded safety fallback, not primary cross-language retrieval.

## Authorized generic retrieval requirement

For non-English user questions:

```text
search_terms
= primary entity/table lookup terms
+ at least one likely English entity/table lookup term
when metadata may be English
```

Keep useful user-language entity terminology when useful.

Do NOT add:
- translation dictionary;
- phrase patch;
- regex glossary;
- fixed sipariş->orders mapping.

This requirement already exists in sealed FT-003 Ask cognition.

FT-005 follow-up cognition should preserve the same generic retrieval contract.

## Product code authorization

This receipt authorizes a minimal generic follow-up prompt-contract repair for retrieval wording only.
It does not authorize deterministic semantic algorithms.
