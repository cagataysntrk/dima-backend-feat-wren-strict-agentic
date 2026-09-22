# FT-UI-001 — METABASE WORKSPACE FEASIBILITY + UI ARCHITECTURE RECONCILIATION

Status: FEASIBILITY COMPLETE / DOCUMENTATION GATE GREEN
Branch: `feat/dima-metabase-product-fast-track`
Review baseline HEAD: `3f9b3d705f481da3d5939e90d9938025434fde61`
Date: 2026-09-22

## 1. Purpose

Reconcile the Fast Track frontend/product composition before FT-003.

Backend/F0/F0A/Gateway architecture is preserved.

This review changes the UI ownership model only.

## 2. Materials reviewed

Fast Track:
- `backend/belgeler/fast/DIMA_FAST_TRACK_ROADMAP.md`
- `DIMA-FAST-OPERASYON.md`
- `DIMA-FAST-DURUM.md`
- `DIMA-FAST-DENETIM.md`
- `backend/belgeler/fast/DIMA_FAST_SOURCE_LOCK.md`
- FT-002/F0A predev and live receipt
- FT-002B Gateway predev

Existing Dima frontend:
- `dima-frontend-demo-master/src/app/page.tsx`
- `src/app/layout.tsx`
- `ReportPanel.tsx`
- `AnalysisCanvas.tsx`
- `ChatPanel.tsx`
- `HistoryPanel.tsx`
- `DashboardView.tsx`
- `DashboardsPanel.tsx`
- frontend `package.json`

Pinned Metabase:
- v0.63.18 runtime;
- pinned Docker digest;
- native Metabase lab;
- Agent API capability receipt.

External technical evidence:
- Metabase official embedding introduction
- full-app embedding docs
- modular embedding SDK docs
- collection browser docs
- dashboard/question SDK API
- embedding security/auth docs

No Metabase frontend source was copied or patched.

## 3. Existing Dima frontend observation

Current frontend is a capable custom analytical/chat shell, but it already owns several commodity BI concerns:

- `page.tsx` coordinates custom chat/result/dashboard overlays;
- `DashboardView.tsx` owns custom dashboard rendering, polling, widget layout, refresh, pinning, width, delete/restore and report export;
- `DashboardsPanel.tsx` owns dashboard CRUD/navigation;
- custom result/chart rendering is Dima-owned;
- search/collection/query-builder/navigation maturity is not comparable to Metabase's native workspace.

At the same time, the existing frontend contains genuinely differentiated Dima surfaces:
- conversation/history;
- ReportPanel;
- AnalysisCanvas;
- research/progress interaction patterns;
- Dima-specific evidence/report/decision affordances.

Conclusion:
Do not delete the frontend.
Stop expanding its commodity BI ownership.

## 4. Supported Metabase integration surfaces

### Full-app embedding

Official supported shape:
- full Metabase application in an iframe;
- SSO integration;
- Metabase permissions retained;
- query-builder, collections, dashboard navigation available;
- URL flags can alter top nav, side nav, search, logo, +New;
- entity-ID URLs exist for question/model/collection navigation.

Technical strengths:
- fastest route to mature analytics workspace;
- lowest amount of custom BI frontend;
- highest immediate UX completeness.

Technical limits for Dima:
- host/iframe boundary;
- official full-app docs expose URL/chrome controls, not the rich typed host callbacks available in the SDK;
- typed “what exactly is open right now?” context cannot be assumed from iframe DOM/location;
- cross-origin DOM scraping is forbidden and brittle;
- SameSite/cross-site browser behavior is an operational constraint.

Therefore full-app is a valid accelerator but not a sufficient permanent Context Bridge architecture.

### Modular embedding

Official supported surfaces include:
- dashboard components;
- question/query-builder components;
- collection browser;
- interactive/editable dashboards;
- interactive questions;
- save/edit flows;
- drill-through/entity navigation;
- theming;
- React hooks/plugins/callbacks.

Useful typed callbacks include:
- dashboard `onLoad`;
- dashboard `onParametersChange`;
- dashboard `onVisualizationChange`;
- collection browser `onClick(item)`;
- question `onRun`;
- question `onSave`;
- question parameter/visualization callbacks.

This is materially better for Dima's Context Bridge.

### Runtime/frontend compatibility

Current Dima frontend:
- Next.js 16.2.10;
- React 19.2.4.

Current Metabase SDK requirements:
- React 18 or 19;
- Node 20+;
- Metabase >= 52;
- no SSR support for SDK components.

Pinned Metabase v0.63.18 is version-compatible by major-generation rules.

POC rule:
- use client-side components;
- resolve/pin the exact SDK package compatible with major 63 before implementation;
- do not rely on unpinned `latest`.

### Capability dependency

Current F0A lab uses the pinned OSS image and proves Agent API, not authenticated embedding entitlement.

Authenticated full-app and interactive modular embedding are capability-gated surfaces.

This is treated as a technical dependency, not a commercial/product decision.

FT-UI-002 cannot be certified until an embedding-capable runtime is available and exact runtime/image/SDK pins are recorded.

The existing F0A substrate pin must not be mutated to make UI POC convenient.

## 5. Model comparison

| Criterion | Model A — Existing Dima Shell | Model B — Full Workspace + Sidecar | Model C — Thin Shell + Modular Surfaces |
|---|---|---|---|
| Time-to-product | Fast for current custom UI, slow for full BI parity | Fastest mature BI workspace | Medium |
| UI quality | Custom / uneven | High, native Metabase | High |
| Analytics completeness | Low-medium | Highest immediately | High, composable |
| Dima frontend maintenance | Highest | Lowest for BI | Medium-low |
| Metabase upgrade risk | Low UI coupling | Low-medium iframe contract | Medium SDK contract, manageable by pin |
| Customization ceiling | Highest but expensive | Medium-low | High |
| Typed context sharing | High only because we own everything | Weakest supported bridge | Strongest supported bridge |
| Dashboard/query integration | Must build/maintain | Native | Native components |
| Search/navigation | Must build | Native | Browser component + host routing |
| Permissions | Dima must mirror carefully | Metabase native with SSO | Metabase native with SSO |
| Authentication | Dima custom | SSO | SSO |
| Branding | Full control | Moderate | High |
| Mobile/responsive | Our burden | Metabase burden + iframe composition | Shared burden |
| Accessibility | Our burden | Primarily Metabase | Metabase components + Dima shell |
| Performance | Full control but more code | iframe overhead, low host code | bundle/runtime integration overhead |
| Future replacement | Easy technically, expensive because all ours | Coarse-grained | Best selective replacement |
| Fork risk | None | None | None |
| Engineering effort | Highest total | Lowest initial | Best long-term balance |

## 6. Feasibility decision

There is a real blocker against declaring Model B permanent:

> full-app iframe composition does not provide the same supported typed context/event integration surface as modular SDK components.

Therefore:

- Model A is rejected as primary BI architecture.
- Model B is accepted as acceleration/baseline/early workspace strategy.
- Model C is the strategic target for context-rich Dima composition.
- The practical migration is B -> C, not B forever.

Normative product statement:

```text
METABASE-FIRST ANALYTICS WORKSPACE
+
DIMA INTELLIGENCE EXPERIENCE
```

## 7. Context Bridge design rule

Dima context must be represented as a typed host-side object.

Proposed minimum contract:

```text
AnalyticsContext {
  resource_type
  resource_entity_id
  sequential_id?
  collection_id?
  dashboard_id?
  question_id?
  model_or_table_ref?
  filter_state
  date_range
  visualization_type?
  source_event
}
```

The exact schema belongs to FT-UI-002/FT-003 after live POC.

Forbidden:
- reading Metabase iframe DOM;
- scraping visible titles;
- guessing IDs from labels;
- trusting frontend-hidden filters as authorization.

## 8. UI POC plan

### POC-A — native baseline

Run native pinned Metabase UI on representative dev data.

Capture:
- home;
- collections;
- dashboard;
- question;
- query builder;
- filters;
- drill;
- search.

### POC-B — full-app workspace/frame

Only when embedding-capable exact runtime is available.

Prove:
- Dima parent frame;
- embedded workspace;
- branding/chrome;
- SSO;
- permissions;
- sidecar coexistence;
- responsive composition.

Do NOT claim Context Bridge GREEN merely because iframe is visible.

### POC-C — modular context bridge

Prove at least:
- CollectionBrowser click -> typed resource;
- InteractiveDashboard load/parameter/visualization callbacks;
- question open/run/save state where applicable;
- Dima sidecar receives typed resource context;
- no browser service secret;
- permissions remain Metabase-authoritative.

If POC-B is strong for workspace but POC-C is needed for typed context, hybrid composition is valid.

## 9. FT-UI-002 GREEN criteria

- Metabase workspace usable;
- branding acceptable;
- Dima sidecar coexists;
- no Metabase source fork;
- no browser service/admin secret;
- typed current-resource context obtainable;
- dashboard/question navigation intact;
- permission boundary preserved;
- acceptable responsive behavior;
- SDK/runtime pin recorded;
- browser/session failure behavior documented.

## 10. Failure simulation

### Embedding entitlement unavailable

Classification:
`EMBED_CAPABILITY_UNAVAILABLE`

Action:
- keep backend work moving;
- do not fall back to custom BI by default;
- do not mark UI POC GREEN;
- resolve capability/runtime input.

### Full-app iframe shows workspace but no typed current context

Classification:
`FULL_APP_CONTEXT_BRIDGE_INSUFFICIENT`

Action:
- keep full-app as optional analytics surface;
- promote modular SDK for context-sensitive surfaces.

### SDK package/runtime mismatch

Classification:
`SDK_RUNTIME_MISMATCH`

Action:
- pin exact major-compatible package;
- no latest;
- rerun POC.

### SSO works but permissions differ from backend principal

Classification:
`PRINCIPAL_MAPPING_MISMATCH`

Action:
- stop;
- do not mask with Dima-side filtering;
- fix principal/group mapping.

### Dashboard filters visible but host context stale

Classification:
`CONTEXT_DESYNC`

Action:
- controlled parameter state / supported callbacks;
- if not representable, mark context partial and require clarification.

### Responsive sidecar crushes workspace

Classification:
`COMPOSITION_RESPONSIVE_FAILURE`

Action:
- drawer/overlay mode on narrow viewport;
- preserve Metabase navigation;
- no permanent two-column desktop assumption.

## 11. OLD -> NEW reconciliation

See:
`backend/belgeler/fast/receipts/decisions/FT_UI_001_WORKSPACE_RECONCILIATION_RECEIPT.md`

## 12. Gate impact

Preserved:
- F0;
- F0A;
- FT-002B gateway;
- evidence;
- root-cause;
- security;
- branch isolation.

New blocker before FT-003:
- FT-UI-001;
- FT-UI-002.

FT-003 frontend definition becomes:

> Produce Dima Ask experience inside the selected Metabase-first product workspace.

FT-009 becomes Metabase-first asset/dashboard integration, not a mandate to build a separate dashboard UI.

## 13. Exit

FT-UI-001 documentation gate = GREEN.

No UI implementation was performed in this reconciliation.

Next UI action:
FT-UI-002 predev + isolated POC.

Backend FT-002B may continue independently because this review does not alter its transport contract.
