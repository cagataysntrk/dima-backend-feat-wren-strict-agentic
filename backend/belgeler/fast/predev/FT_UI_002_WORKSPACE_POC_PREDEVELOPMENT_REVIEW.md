# FT-UI-002 — DIMA-NATIVE RENDERING / COMPOSITION POC PRE-DEVELOPMENT REVIEW

Status: CLOSED / GREEN
Branch: `feat/dima-metabase-product-fast-track`
Supersedes: prior modular-workspace POC scope
Date: 2026-09-22

## 1. Supervisor correction

No functional FT-UI-002 implementation existed when this scope changed.

Classification:

```text
NE YAZILDI?
- docs/predev/capability-lock only

SADECE POC MU?
- yes, planning only

PRODUCT DEPENDENCY MI?
- no

REUSE EDILEBILIR MI?
- backend F0/F0A/FT-002B remains fully reusable
- modular/full-app research remains reference-only
```

No product code deletion is required.

## 2. Goal

Answer only:

> How can Dima render real Metabase analytical results inside a Dima-native analyst experience with minimal frontend cost?

This ticket is NOT:
- Ask implementation;
- Analyst loop;
- Root Cause;
- generic BI workspace;
- Metabase navigation integration.

## 3. Product thesis

```text
DIMA = entire user-facing experience
METABASE = hidden analytics/query/optional-rendering substrate
```

The user works with an analyst, not a BI tool.

## 4. OSS-only invariant

```text
METABASE_LICENSE_BUDGET = 0
PAID_METABASE_FEATURE_REQUIRED_FOR_CORE_PRODUCT = 0
METABASE_FULL_APP_EMBED_REQUIRED = 0
METABASE_MODULAR_SDK_REQUIRED_IN_PRODUCTION = 0
METABASE_NATIVE_WORKSPACE_REQUIRED_FOR_USER = 0
DIMA_PRODUCT_MUST_RUN_ON_METABASE_OSS = required
```

## 5. Options under test

### A — Dima-native result rendering

Metabase result rows/schema -> Dima table/chart.

Reuse only generic safe primitives:
- `EChart`;
- `ResultTable`.

Do not reuse legacy BI navigation/dashboard ownership.

### B — OSS guest visualization

Evaluate, not require:
- guest embedded question/dashboard;
- server-signed JWT;
- embedding secret server-side only;
- view-only semantics;
- synthetic/non-sensitive data.

### C — Hybrid

Default native Dima renderer.
Guest visualization only where a complex view-only visualization materially saves effort.

## 6. Files allowed

- `dima-frontend-demo-master/src/app/fast-poc/**`
- `dima-frontend-demo-master/src/features/fast-poc/**`
- focused Fast POC fixture/tests/workflow
- `backend/belgeler/fast/**`

Existing generic components may be imported without modification.

## 7. Files forbidden

- `src/app/page.tsx`
- DashboardView
- DashboardsPanel
- ReportPanel
- AnalysisCanvas
- Metabase source/frontend
- V2/V3/Wren
- source branches
- production navigation
- generic Collections/Questions/Search/Query Builder UI

## 8. Real-data proof

POC uses a sanitized fixture generated from the real pinned Metabase lab/Gateway path.

Required provenance:
- exact Fast Gateway tested commit;
- exact Metabase runtime;
- query/result receipt;
- synthetic lab data only.

FT-003 will be the first live user-question -> Gateway -> evidence -> answer end-to-end product path.

## 9. Dima analyst-shell POC

Minimal composition:

```text
DIMA

Question / investigation intent

Result / finding area
  -> chart or table
Evidence/provenance summary

[Derinleştir] [Karar Kaydet] [Raporla]
```

No fake AI response.
No fake finding.
POC fixture content must be clearly labeled as rendering proof.

## 10. Rendering behavior

- tabular result always has table fallback;
- chart shown only when shape is safely chartable;
- chart is evidence visualization, not product destination;
- empty result != zero;
- unsupported shapes fall back to table;
- no dashboard/navigation shell.

## 11. Guest embed evaluation

Document only unless clearly useful.

Facts:
- guest embedding is available on OSS;
- charts/dashboards are view-only;
- server signs JWT;
- signing secret never reaches browser;
- no Query Builder/drill-through;
- no Metabase user identity;
- locked parameters are the restriction mechanism.

Guest embed is never required for FT-003.

## 12. Responsive target

Desktop:
- single-column analyst narrative;
- chart/table within result/evidence card.

Narrow:
- same vertical analyst flow;
- responsive chart/table;
- no two-column BI workspace.

## 13. Hard GREEN gate

- [x] Dima-native analyst shell POC
- [x] real Metabase result fixture rendered inside Dima
- [x] simple table path
- [x] simple chart path
- [x] safe table fallback
- [x] optional guest visualization evaluated
- [x] no Metabase workspace dependency
- [x] no Collections UI dependency
- [x] no Query Builder dependency
- [x] no native Metabase Search dependency
- [x] no paid Metabase feature dependency
- [x] no Metabase frontend fork
- [x] no browser service/admin secret
- [x] responsive analyst UX acceptable
- [x] selected rendering strategy documented
- [x] build/type gate green

## 14. Selection rule

SELECT A when native Dima renderer handles common shapes cleanly with trivial maintenance.

SELECT C when A is sufficient by default but guest visualization is clearly valuable for rare complex view-only views.

SELECT B only if guest rendering is materially simpler for common product output without weakening Dima UX.

Current hypothesis:
A or C.

## 15. Exit

When GREEN:
1. seal FT-UI-002 receipt;
2. update status/audit;
3. immediately open FT-003 predev;
4. do not wait for modular/full-app work.

FT-003 target:

```text
question
-> resource candidates
-> temporal binding
-> construct
-> execute
-> Evidence
-> Dima answer
-> appropriate chart/table
```


## 16. Certification

Selected strategy:
`OPTION_A — Dima-native chart/table`

Workflow:
`dima-fast-ui-rendering-poc`

GREEN run:
`35768067813`

Tested commit:
`3f4a34356d7b32a78c3c18f1c96a1879253001a2`

Proof:
- real Metabase rows seen: 250;
- committed rendering rows verified: 12;
- chart canvas: GREEN;
- table rows: 12;
- 390x844 viewport: no horizontal overflow;
- Next production build: GREEN;
- package manifest unchanged: no embedding SDK dependency;
- production main page unchanged.

Guest embed evaluation result:
use only as a future optional view-only visualization escape hatch. It is not justified for the common FT-003 path.

Exit:
FT-UI-002 GREEN. FT-003 OPEN.
