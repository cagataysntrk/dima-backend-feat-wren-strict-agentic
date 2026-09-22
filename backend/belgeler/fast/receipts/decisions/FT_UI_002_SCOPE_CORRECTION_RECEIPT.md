# FT-UI-002 — SCOPE CORRECTION RECEIPT

Status: SEALED
Date: 2026-09-22
Branch: `feat/dima-metabase-product-fast-track`

## Observation

Before the supervisor correction, FT-UI-002 had only documentation/planning changes.

Functional implementation status:
```text
CollectionBrowser code        = 0
Query Builder code            = 0
Metabase navigation code      = 0
native workspace code         = 0
Questions browser code        = 0
Metabase Search UI code       = 0
modular SDK dependency        = 0
full-app dependency           = 0
```

No product code rollback/deletion was required.

## Superseded thesis

`Metabase-first Analytics Workspace + Dima Intelligence Experience`

## Normative thesis

`Dima-native Intelligence Workspace on Metabase Analytics Substrate`

## Core invariants

- METABASE_LICENSE_BUDGET = 0
- PAID_METABASE_FEATURE_REQUIRED_FOR_CORE_PRODUCT = 0
- METABASE_FULL_APP_EMBED_REQUIRED = 0
- METABASE_MODULAR_SDK_REQUIRED_IN_PRODUCTION = 0
- METABASE_NATIVE_WORKSPACE_REQUIRED_FOR_USER = 0
- DIMA_PRODUCT_MUST_RUN_ON_METABASE_OSS = required

## FT-UI-002 new purpose

Compare:
A. Dima-native chart/table
B. optional OSS guest visualization
C. hybrid

and select the simplest viable rendering strategy.

FT-003 remains blocked only until this small rendering/composition POC is GREEN.
