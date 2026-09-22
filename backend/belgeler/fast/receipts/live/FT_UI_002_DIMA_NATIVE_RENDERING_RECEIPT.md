# FT-UI-002 — DIMA-NATIVE RENDERING CERTIFICATION RECEIPT

Status: GREEN / SEALED
Date: 2026-09-22
Branch: `feat/dima-metabase-product-fast-track`

## Product boundary

```text
DIMA = entire user-facing analyst product
METABASE = hidden analytics/query/optional-rendering engine
```

No generic Metabase workspace was introduced.

## Tested implementation

Functional POC commit:
`9217a99c1e09ebf422ece74cc78caca23bcb4eb9`

Final browser-proof commit:
`3f4a34356d7b32a78c3c18f1c96a1879253001a2`

GREEN workflow run:
`35768067813`

Workflow:
`.github/workflows/dima-fast-ui-rendering-poc.yml`

Real-result artifact:
`dima-fast-ui-real-result-3f4a34356d7b32a78c3c18f1c96a1879253001a2`

Artifact digest:
`sha256:2ecaec2ad248f5d22d12503fa3dad3dab46539b85f3999b7b404f556a03780b3`

## Isolation proof

Functional commit diff from the approved scope baseline contained only:
- Fast UI workflow;
- isolated `/fast-poc` page;
- `src/features/fast-poc/**`;
- focused Fast POC browser E2E.

Not changed:
- main `src/app/page.tsx`;
- DashboardView;
- DashboardsPanel;
- ReportPanel;
- AnalysisCanvas;
- production navigation;
- Fast Gateway;
- V2/V3/Wren;
- source branches.

## Real Metabase proof

Pinned runtime:
`v0.63.18`

Fast-owned gateway:
`FastMetabaseGateway`

Observed live:
- source rows seen = 250;
- fixture rows verified = 12;
- columns = id, order_date, region, channel, amount;
- fixture derived from synthetic pinned lab data;
- committed fixture equality = GREEN.

This proves the UI fixture is not an invented visual mock.

## Frontend proof

- frozen pnpm install = GREEN;
- Next production build = GREEN;
- isolated Next route start = GREEN;
- protected route entered without weakening production auth = GREEN;
- ECharts canvas = GREEN;
- table path = GREEN;
- rendered table rows = 12;
- narrow viewport width = 390;
- browser viewport = 390;
- document scrollWidth = 390.

No horizontal overflow was observed at the required narrow viewport.

## Safe fallback

The rendering card computes a chart only for a bounded chartable shape.

If chart inference returns no valid chart:
- initial mode is table;
- table renderer remains available for every QueryResult shape.

The browser proof also exercises the table renderer explicitly.

## Guest visualization evaluation

Official Metabase docs confirm:
- guest embedding is available on OSS/all plans;
- guest resources are JWT-signed;
- signing secret must remain server-side;
- guest embed has no Metabase user identity;
- guest embeds are view-only;
- no drill-through;
- no Query Builder;
- locked parameters are needed for data restriction.

References:
- https://www.metabase.com/docs/latest/embedding/introduction
- https://www.metabase.com/docs/latest/embedding/guest-embedding
- https://www.metabase.com/docs/latest/embedding/securing-embeds

Decision:
Guest embed is useful only as a future optional complex visualization escape hatch.
It is unnecessary for the common first product path.

## Rendering decision

SELECT:
`OPTION_A — DIMA_NATIVE_CHART_TABLE`

Reason:
- already passes real-result rendering;
- lowest frontend and security complexity;
- zero license dependency;
- total Dima UX control;
- existing EChart/ResultTable primitives are sufficient;
- direct fit with evidence-first analyst narrative.

Option C remains an allowed future escalation if a real visualization gap is measured.

## Failure receipts closed

1. `FT_UI_002_CI_SHALLOW_CHECKOUT_HEAD_PARENT`
   - CI shallow checkout only.
   - fixed with parent-aware checkout.

2. `FT_UI_002_SETUP_NODE_PNPM_CACHE_ORDER`
   - setup-node cache ordering only.
   - fixed by activating pinned pnpm after Node setup.

3. `FT_UI_002_E2E_AUTH_GUARD_REDIRECT`
   - production route guard redirected the test browser.
   - fixed in E2E oracle only; production proxy/auth unchanged.

None required a product-architecture workaround.

## Gate decision

FT-UI-002 = GREEN / CLOSED.

FT-003 = OPEN.

Next exact action:
create FT-003 pre-development review and implement the first real Dima Ask vertical slice.
