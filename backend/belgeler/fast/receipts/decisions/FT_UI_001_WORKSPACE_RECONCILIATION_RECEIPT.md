# FT-UI-001 — WORKSPACE ARCHITECTURE RECONCILIATION RECEIPT

Status: SEALED
Date: 2026-09-22
Branch: `feat/dima-metabase-product-fast-track`

## Decision 1

OLD DECISION:
Existing Dima Next.js frontend is the main BI/product shell.

WHY CHANGED:
The current shell contains useful Dima-specific interaction patterns, but it also duplicates dashboard, chart, BI asset and navigation concerns that Metabase already owns at greater maturity.

NEW DECISION:
Metabase-first Analytics Workspace + Dima Intelligence Experience.

WHAT REMAINS VALID:
- Dima brand/frame;
- Dima auth/application shell where needed;
- conversation/history;
- ReportPanel concepts;
- AnalysisCanvas concepts;
- evidence/research/decision/report surfaces.

WHAT IS DEFERRED:
Custom Dima BI navigation/dashboard/query-builder expansion.

## Decision 2

OLD DECISION:
Fast frontend work may grow under Dima-owned feature folders until the full BI experience is ours.

WHY CHANGED:
That path increases permanent maintenance and moves engineering effort away from Dima's differentiated intelligence.

NEW DECISION:
Commodity BI surfaces are Metabase-owned by default. Dima feature folders own intelligence surfaces and integration glue.

WHAT REMAINS VALID:
Dima-native code for Analyst, Research, Evidence, Root Cause, Hypotheses, Decision, Reports.

WHAT IS DEFERRED:
Rebuilding collections/search/query-builder/dashboard lifecycle without measured gap.

## Decision 3

OLD DECISION:
Dima-native renderer is the primary surface for every analytical result and dashboard.

WHY CHANGED:
Metabase provides mature interactive dashboard/question/filter/drill UX and supported embedding surfaces.

NEW DECISION:
Use Metabase rendering/workspace for commodity analytics. Use Dima-native renderer where Dima adds intelligence not represented by Metabase.

WHAT REMAINS VALID:
Dima-native research timeline, evidence, hypotheses, decisions, reports, explanatory intelligence.

WHAT IS DEFERRED:
Custom dashboard renderer as primary product workspace.

## Decision 4

OLD DECISION:
Dashboard lifecycle is a Dima-owned frontend concern.

WHY CHANGED:
The existing `DashboardView` and `DashboardsPanel` duplicate mature Metabase asset lifecycle.

NEW DECISION:
FT-009 reuses Metabase dashboard/question/collection lifecycle first.

WHAT REMAINS VALID:
Dima can attach evidence/findings/decisions to Metabase asset identity.

WHAT IS DEFERRED:
Dima-native dashboard lifecycle unless a measured capability gap requires it.

## Decision 5

OLD DECISION:
Full-app embedding could become the final workspace architecture if it looks good enough.

WHY CHANGED:
Full-app is iframe-based and does not expose the same rich supported host callbacks/context surface as modular SDK components.

NEW DECISION:
Full-app may accelerate UX-0/UX-1.
Modular surfaces are the strategic context-rich composition target.

WHAT REMAINS VALID:
Metabase native workspace remains the analytics UX benchmark and may remain a major product surface.

WHAT IS DEFERRED:
Permanent commitment to a monolithic iframe.

## Invariants added

- METABASE_FRONTEND_FORK = 0
- METABASE_SOURCE_PATCH_FOR_DIMA_UI = 0
- DIMA_INTELLIGENCE_OWNER = DIMA
- METABASE_BI_WORKSPACE_OWNER = METABASE
- DIMA_BACKEND_CAN_RUN_WITHOUT_METABASE_EMBED = required
- METABASE_SERVICE_SECRET_IN_BROWSER = 0
- RAW_DOM_CONTEXT_SCRAPING = 0
- DIMA_CONTEXT_USES_TYPED_RESOURCE_IDS = required
- METABASE_AI_BECOMES_DIMA_RESEARCH_OWNER = 0
- DIMA_EVIDENCE_AND_DECISION_STATE_IN_METABASE_ONLY = 0

## Ticket impact

Preserve:
FT-001 -> FT-002 / FT-002B

Insert before FT-003:
FT-UI-001 -> FT-UI-002

Then:
FT-003 and later product gates.

## No-code statement

This receipt changes architecture documentation only.

No frontend product implementation is authorized by this receipt.
