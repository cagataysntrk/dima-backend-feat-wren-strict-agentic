# FT-UI-002 — MODULAR WORKSPACE POC PRE-DEVELOPMENT REVIEW

Status: APPROVED FOR POC-A ONLY
Branch: `feat/dima-metabase-product-fast-track`
Observed HEAD: `32b19feb8265c501c1a4547ce21c6729a74829f3`
Date: 2026-09-22

## 1. Goal

Prove Model C first:

```text
Thin Dima Frame
+
Metabase Modular Surfaces
+
Dima Intelligence Sidecar
```

This ticket is a product-composition proof, not FT-003 Ask implementation.

## 2. Capability split

### POC-A / UI-P0 — local modular evaluation

May open FT-003 when GREEN.

Purpose:
- composition;
- modular surface viability;
- real browser event payloads;
- typed AnalyticsContext;
- responsive sidecar;
- local evaluation auth only.

### POC-B / UI-P1 — production authenticated embedding qualification

Required before external pilot / F9.

Purpose:
- production JWT SSO;
- individual principal;
- permission/group mapping;
- production origin/session behavior;
- denial/revocation qualification.

POC-A GREEN does not certify POC-B.

## 3. Immutable prerequisites

Sealed backend remains unchanged:
- F0 GREEN;
- F0A GREEN;
- FT-002B Gateway GREEN.

F0A Metabase pin remains:
- major: 63;
- runtime: v0.63.18;
- image: `sha256:1160b570cb11c107bce00e71293552df8a8363e01a32c2c7a048cee002dc8a73`.

Do NOT mutate the F0A runtime pin for UI convenience.

## 4. SDK package policy

Official major-match rule:
- use `@metabase/embedding-sdk-react@63-stable` for Metabase major 63.

Resolved package at review time:
- exact version: `0.63.1`.

Implementation MUST:
- write exact `0.63.1` to package manifest/lock;
- record resolved package integrity from the generated lockfile;
- never leave `63-stable` or `latest` as the shipped dependency.

## 5. Current owner

Existing main Dima frontend is NOT migrated in this ticket.

POC owner:
- `dima-frontend-demo-master/src/app/fast-poc/page.tsx`
- `dima-frontend-demo-master/src/features/fast-poc/**`

## 6. Files allowed

Functional POC commit may touch only:
- `dima-frontend-demo-master/package.json`
- existing package lock file, or one package lock consistent with the repo package manager;
- `dima-frontend-demo-master/src/app/fast-poc/**`
- `dima-frontend-demo-master/src/features/fast-poc/**`
- focused POC tests/e2e files explicitly named for fast-poc;
- `backend/belgeler/fast/**`
- Fast UI-specific workflow if needed.

## 7. Files forbidden

Do NOT modify:
- `dima-frontend-demo-master/src/app/page.tsx`;
- DashboardView;
- DashboardsPanel;
- ReportPanel;
- AnalysisCanvas;
- legacy product navigation;
- backend Fast Gateway;
- backend V2/V3;
- Wren;
- Metabase source tree;
- read-only branches.

## 8. POC composition

Write no commodity BI replacement.

Use supported Metabase surfaces:
- MetabaseProvider;
- Collection Browser;
- Interactive Dashboard;
- Interactive Question/query surface.

Dima-only POC UI:
- thin frame;
- collapsible sidecar;
- AnalyticsContext inspector;
- visible loading/error state.

No:
- custom dashboard;
- custom query builder;
- custom collection browser;
- new charting engine.

## 9. Local evaluation auth

POC-A status:
`LOCAL_EVALUATION_AUTH`

Rules:
- admin/service credential in browser = forbidden;
- real customer data = forbidden;
- committed API key = forbidden;
- synthetic/non-sensitive dev DB only;
- localhost only;
- env/gitignore;
- logs/screenshots redact secrets;
- any dedicated evaluation key must be minimum-scope and revoked/rotated after POC.

If current OSS runtime cannot expose modular SDK capability:
- classify `EMBED_CAPABILITY_UNAVAILABLE`;
- do not mutate F0A;
- do not fake the POC;
- evaluate supported fallback according to decision rule.

## 10. AnalyticsContext host contract

Initial normalized contract:

```ts
type AnalyticsContext = {
  source: "metabase";
  resourceType:
    | "collection"
    | "dashboard"
    | "question"
    | "model"
    | "table"
    | "unknown";
  entityId?: string;
  collectionId?: string;
  dashboardId?: string;
  questionId?: string;
  modelId?: string;
  tableId?: string;
  filters?: unknown;
  dateRange?: unknown;
  visualization?: unknown;
  sourceEvent:
    | "collection_click"
    | "dashboard_load"
    | "dashboard_parameters"
    | "dashboard_visualization"
    | "question_run"
    | "question_save"
    | "navigation"
    | "unknown";
  completeness: "FULL" | "PARTIAL" | "RESOURCE_ONLY";
  updatedAt: string;
};
```

Contract may evolve only from measured callback payloads.

Never authoritative:
- raw DOM text;
- visible title scraping;
- CSS selector;
- iframe DOM;
- label -> guessed ID.

## 11. Event families to measure live

At least three real families:

Collection Browser:
- item click;
- actual payload;
- normalized context;
- missing fields.

Dashboard:
- load;
- parameter change;
- visualization/card interaction when supported;
- actual payload;
- normalized context;
- missing fields.

Question:
- open/run/save where supported;
- actual payload;
- normalized context;
- missing fields.

Documentation claim alone does not satisfy the gate.

## 12. Native Metabase baseline

Before or in parallel with modular POC inspect:
- Home;
- Collections;
- Dashboard;
- Question;
- Query Builder;
- Filters;
- Drill;
- Search.

Receipt fields:
- surface;
- works?;
- useful?;
- must Dima duplicate?;
- context relevance?.

Keep this concise; it is a commodity-BI benchmark, not a redesign exercise.

## 13. Layout target

Desktop:
- Metabase workspace ~72–76%;
- Dima sidecar ~24–28%;
- sidecar collapsible.

Narrow:
- Metabase primary full-width;
- Dima sidecar becomes drawer/bottom sheet;
- no two cramped columns.

POC should be clean enough to judge product composition, not pixel-perfect.

## 14. Sidecar scope

POC may show:
- current context;
- selected resource;
- filter/date state;
- visual Ask input;
- “Analyze current context” affordance.

POC must NOT fabricate:
- Ask response;
- AI answer;
- root cause;
- finding.

Real Ask belongs to FT-003.

## 15. Browser sizes

Desktop:
- 1440x900;
- 1280x800.

Narrow:
- 390x844.

## 16. Required flows

1. open collection;
2. open dashboard;
3. alter dashboard filter;
4. open question;
5. run/change question where supported;
6. Dima sidecar reflects context;
7. navigate elsewhere;
8. context updates;
9. collapse sidecar;
10. narrow viewport.

## 17. Negative flows

- SDK load failure;
- Metabase unavailable;
- auth denied;
- resource permission denied;
- context callback missing;
- stale context.

## 18. Automatic architecture decision

CASE A -> MODEL C:
all core modular surfaces + typed context GREEN, navigation/responsive acceptable.

CASE B -> HYBRID:
typed modular context strong, but broad workspace navigation would require excessive host work.

CASE C -> MODEL B V1:
modular materially blocked and full-app is stronger; context completeness explicit and never guessed.

CASE D -> STOP:
both supported integration models fail critical requirements; do not auto-return to legacy Dima BI.

Full-app is NOT required to open FT-003 when Model C POC-A is GREEN.

Supported full-app `postMessage`/location tracking may be tested as fallback; iframe DOM scraping remains forbidden.

## 19. Hard GREEN gate

POC-A GREEN requires:

- [ ] F0A substrate unchanged;
- [ ] SDK major 63;
- [ ] exact SDK version locked;
- [ ] package integrity/lock committed;
- [ ] isolated /fast-poc;
- [ ] no Metabase fork/source patch;
- [ ] Collection Browser works;
- [ ] Dashboard works;
- [ ] Question/query surface works;
- [ ] Dima sidecar coexists;
- [ ] >=3 real typed event families;
- [ ] AnalyticsContext normalization demonstrated;
- [ ] DOM scraping = 0;
- [ ] guessed resource identity = 0;
- [ ] admin/service credential in browser = 0;
- [ ] desktop responsive acceptable;
- [ ] narrow drawer strategy acceptable;
- [ ] navigation usable;
- [ ] error/loading state visible;
- [ ] live/browser receipt;
- [ ] architecture model selected.

## 20. Commit protocol

Commit 1:
`docs(fast-ui): open FT-UI-002 modular workspace POC`

Only:
- this predev;
- UI capability-lock skeleton;
- roadmap/status/audit nuance.

Commit 2:
`feat(fast-ui): prove modular Metabase workspace context bridge`

Only:
- isolated /fast-poc;
- exact SDK lock;
- modular components;
- context bridge;
- sidecar;
- focused tests.

Commit 3:
`docs(fast-ui): seal FT-UI-002 workspace decision`

Only:
- live/browser receipt;
- selected model;
- status/audit;
- next action.

## 21. Exit

If POC-A GREEN:
- FT-003 becomes OPEN;
- immediately create FT-003 predev;
- do not wait for POC-B.

If POC-A RED:
- write failure receipt;
- apply CASE B/C/D decision rule;
- no silent fallback.

POC-B remains a production/external-pilot gate before F9.
