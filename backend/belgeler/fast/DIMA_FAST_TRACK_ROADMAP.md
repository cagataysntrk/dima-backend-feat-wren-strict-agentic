# DIMA FAST TRACK — DIMA-NATIVE INTELLIGENCE PRODUCT ROADMAP

Status: NORMATIVE BRANCH ROADMAP
Audit verdict: FEASIBLE_WITH_OSS_ANALYTICS_SUBSTRATE
Last architecture reconciliation: 2026-09-22

## 1. Product thesis

Fast Track is not Wren-first, DimaSemanticSpec-first, or a Metabase frontend fork.

The product is:

```text
DIMA-NATIVE INTELLIGENCE WORKSPACE
on
METABASE ANALYTICS SUBSTRATE
```

Normative boundary:

```text
DIMA     = entire user-facing product experience
METABASE = hidden analytics/query/optional-rendering engine
```

Users do not operate a generic BI workspace.
They work with Dima as an analyst.

Backend topology remains:

```text
User
-> Dima Intelligence / Orchestration
-> Dima Fast Backend
-> Fast-owned Metabase Gateway
-> Metabase Agent API / analytics substrate
-> Customer DB
```

Frontend/product composition is now:

```text
Dima Product
├─ Ask
├─ Analyst
├─ Research
├─ Root Cause
├─ Evidence
├─ Findings
├─ Hypotheses
├─ Recommendations
├─ Decisions
├─ Reports
└─ context-specific charts/tables
       ↓
  Fast Backend
       ↓
  Metabase
  query / execution / optional rendering
       ↓
      DB
```

The product principle is:

> Do not turn Dima into a BI tool. Use Metabase to avoid rebuilding analytics infrastructure, while Dima owns the complete analyst experience.

## 2. Ownership boundary

### Metabase owns hidden analytics capabilities

Reuse where useful:
- Agent API;
- metadata/resource discovery;
- query construction;
- query execution;
- database drivers;
- permissions machinery where applicable;
- result processing;
- selected visualization/dashboard rendering only when it reduces Dima frontend cost;
- saved analytical assets only where internally useful.

Metabase does NOT own Dima information architecture or the user-facing shell.

### Dima owns differentiated intelligence

Primary owner for:
- Ask Dima;
- Analyst Mode;
- Research Mode;
- Root Cause / Driver Analysis;
- research progress;
- Evidence Drawer;
- Hypothesis Ledger;
- Findings;
- recommendations;
- Decision Records;
- executive reports;
- conversation/history;
- proactive insights;
- action-oriented UX.

Dima evidence, research, conversation, decision, recommendation and report state remains Dima-owned state.

Any Metabase asset state used internally remains substrate state and must not define the Dima product navigation.

## 3. Hard non-goals

The critical path does NOT include:
- Wren runtime;
- Wren MDL requirement;
- DimaSemanticSpec compiler;
- dual-engine parity;
- custom query planner;
- custom DB driver framework;
- Metabase frontend source fork;
- patches to Metabase internal React source;
- copying Metabase frontend source into Dima;
- unrestricted native SQL;
- arbitrary autonomous loops;
- rebuilding collections/dashboard/query-builder UX in Dima by default.

## 4. Backend product modes

Quick:
`question -> resource -> construct -> execute -> answer`

Analyst:
`baseline -> comparison -> selected breakdowns -> synthesis`

Research / Root Cause:
`target -> comparator -> candidate drivers -> breadth scans -> drill -> alternatives -> data-quality checks -> synthesis`

All loops are bounded.

## 5. Resource safety

The model may not invent raw Metabase IDs.

```text
user phrase
-> Agent search
-> CandidateResource[]
-> opaque fast_handle[]
-> SELECT(handle) | ABSTAIN
-> gateway validates
-> inspect / construct
```

Material ambiguity -> clarification.

Frontend context uses typed resource identity, not DOM scraping.

## 6. Temporal safety

Relative time becomes typed `TemporalIntent`.
Exact dates are computed deterministically by backend authority.

Evidence stores:
- exact bounds;
- timezone;
- incomplete-period state;
- comparison policy.

## 7. Evidence Lite

Every user-visible numeric finding must reference at least one evidence item.

Evidence stores:
- query fingerprint;
- access fingerprint;
- Metabase resource refs;
- constructed query;
- exact temporal bounds;
- result digest;
- bounded summary;
- row count;
- truncation state;
- runtime version.

Model rationale is not evidence.

## 8. Root-cause constraints

Metric type:
`ADDITIVE | SEMI_ADDITIVE | RATIO | DISTINCT_COUNT | NON_ADDITIVE | UNKNOWN`

Only representable decompositions are allowed.

Special cases:
- total delta = 0;
- offsetting contributors;
- NULL spike;
- incomplete period;
- insufficient seasonality history;
- high cardinality;
- permission-blocked driver;
- query failure;
- stale resource.

Data-quality risk is not silently converted into a business cause.

## 9. Security

Internal alpha may use a shared dev credential only inside an isolated development environment.

External pilot requires:
- per-user/principal mapping;
- tenant isolation;
- permission denial;
- revocation;
- cache isolation;
- evidence/history current-viewer authorization;
- no service/admin secret in browser.

Shared API key is not end-user identity.

## 10. Fast-owned Metabase Gateway

Single Fast Track gateway owns:
- auth context;
- search;
- inspect/read-resource;
- construct;
- execute;
- pagination;
- timeout/retry;
- typed errors;
- later asset writes.

Native SQL default is OFF.

Observed Agent API page limit: 200 rows; continuation is explicit.

## 11. Run lifecycle

```text
CREATED
RUNNING
WAITING_CLARIFICATION
PARTIAL
COMPLETED
FAILED
CANCEL_REQUESTED
CANCELLED
INTERRUPTED
```

Terminal state occurs exactly once.

Same conversation: at most one active research run.

## 12. UI architecture decision

Previous workspace-centric guidance is superseded.

The user-facing product is:

```text
DIMA-NATIVE INTELLIGENCE WORKSPACE
ON METABASE ANALYTICS SUBSTRATE
```

Metabase user-facing workspace surfaces are NOT product goals:

- Collections;
- Questions browser;
- Query Builder;
- Metabase Search;
- generic BI navigation;
- generic exploration workspace;
- native Metabase drill workspace;
- Metabase-first asset-management UX.

These may be inspected as engineering/reference surfaces, but they are not Dima information architecture.

## 13. OSS-only / zero-license hard invariants

```text
METABASE_LICENSE_BUDGET = 0

PAID_METABASE_FEATURE_REQUIRED_FOR_CORE_PRODUCT = 0
METABASE_FULL_APP_EMBED_REQUIRED = 0
METABASE_MODULAR_SDK_REQUIRED_IN_PRODUCTION = 0
METABASE_NATIVE_WORKSPACE_REQUIRED_FOR_USER = 0

DIMA_PRODUCT_MUST_RUN_ON_METABASE_OSS = required
METABASE_FRONTEND_FORK = 0
METABASE_SOURCE_PATCH_FOR_DIMA_UI = 0
METABASE_SERVICE_SECRET_IN_BROWSER = 0
```

Paid Metabase capabilities may be evaluated outside the core path, but no critical product flow may require them.

## 14. FT-UI-002 new scope — rendering/composition POC

FT-UI-002 no longer asks:

> “How do we put a Metabase workspace inside Dima?”

It asks:

> “How do we reuse Metabase analytics/rendering inside a Dima-native analyst UX with the least frontend cost?”

Three rendering strategies are compared.

### OPTION A — Dima-native chart/table

```text
Metabase result
-> rows/schema
-> Dima chart/table renderer
```

Pros:
- total Dima UX control;
- no embedding dependency;
- OSS-only;
- clean evidence/analysis composition.

### OPTION B — OSS guest embedded visualization

```text
published Metabase question/dashboard
-> server-signed guest JWT
-> view-only chart/dashboard inside a Dima analysis card
```

Pros:
- reuse Metabase visualization rendering;
- guest embedding is available on OSS;
- no per-user Metabase account required.

Limits:
- view-only;
- no query builder;
- no drill-through;
- no Metabase user identity/row-column permission model;
- locked parameters are required for data restriction;
- embedding secret stays server-side.

OPTION B is optional, not a core requirement.

### OPTION C — Hybrid

Default:
- simple chart/table -> Dima-native.

Use guest embed only when:
- a complex Metabase visualization materially saves implementation cost;
- view-only semantics are sufficient;
- security can be expressed with published resource + locked parameters.

## 15. FT-UI-002 hard GREEN gate

FT-UI-002 GREEN requires:

- [ ] Dima-native analyst shell POC;
- [ ] real Metabase result rendered inside Dima;
- [ ] simple chart/table path proven;
- [ ] optional guest visualization path evaluated;
- [ ] no Metabase workspace dependency;
- [ ] no Collections UI dependency;
- [ ] no Query Builder dependency;
- [ ] no native Metabase Search dependency;
- [ ] no paid Metabase feature dependency;
- [ ] no Metabase frontend fork;
- [ ] no browser service/admin secret;
- [ ] responsive analyst UX acceptable;
- [ ] selected rendering strategy documented.

No modular SDK or full-app embedding proof is required to open FT-003.

## 16. UI implementation boundary

Isolated POC route:

`dima-frontend-demo-master/src/app/fast-poc/page.tsx`

Preferred feature root:

`dima-frontend-demo-master/src/features/fast-poc/**`

Do NOT migrate:
- main `src/app/page.tsx`;
- DashboardView;
- DashboardsPanel;
- ReportPanel;
- AnalysisCanvas;
- existing product navigation.

POC should compose only:
- Dima analyst shell;
- analysis/result card;
- chart/table;
- evidence/provenance summary;
- optional guest visualization comparison if useful.

Do NOT build:
- CollectionBrowser;
- Query Builder;
- Metabase navigation;
- Questions browser;
- Metabase Search;
- generic workspace shell;
- custom dashboard product.

## 17. Gate sequence

```text
F0       governance                         GREEN
F0A      pinned Metabase capability         GREEN
FT-002B  Fast-owned Gateway                 GREEN
FT-UI-001 architecture reconciliation       GREEN
FT-UI-002 Dima-native rendering POC         GREEN
FT-003    first real Ask vertical slice     OPEN
```

Then:

```text
F1A / FT-003 safety completion
F2 / FT-005 conversation
F3 / FT-006 evidence
F4 / FT-007 analyst
F5 / FT-008 root cause
F6 / FT-009 selected analytical assets only where useful
F7 decision/report
F8 product polish
F9 pilot security
F10 benchmark
F11 pilot readiness
F12 production candidate
```

FT-009 does not create a Metabase-first asset-management UX.
Analytical assets remain implementation/supporting artifacts unless Dima explicitly surfaces them in a task-specific flow.

Core tickets:
- FT-001 — branch/governance
- FT-002 — capability + Fast-owned Metabase Gateway
- FT-UI-001 — UI architecture reconciliation
- FT-UI-002 — Dima-native rendering/composition POC
- FT-003 — real Ask vertical slice
- FT-004 — streaming/run-state/cancel
- FT-005 — conversation
- FT-006 — Evidence Lite
- FT-007 — Analyst Mode
- FT-008 — Root Cause v1
- FT-009 — optional analytical assets/rendering integrations
- FT-010 — decision
- FT-011 — report
- FT-012 — polish
- FT-013 — pilot security
- FT-014 — benchmark/failure injection/release rehearsal

## 18. Test pyramid

- L0 governance/static
- L1 unit
- L2 contract
- L3 live pinned Metabase
- L4 model-in-loop focused
- L5 workspace/frontend E2E
- L6 security
- L7 failure injection

Initial golden corpus:
- DEV90
- VALIDATION30
- HOLDOUT30

Zero tolerance:
- silent numeric wrong;
- resource hallucination;
- finding without evidence;
- cross-tenant leak;
- permission bypass;
- silent fallback;
- browser service secret;
- DOM-scraped analytics identity.

## 19. Mandatory failure families

Backend:
- no resource;
- ambiguous resource;
- permission denied;
- Agent API disabled;
- pagination/truncation;
- empty vs zero;
- incomplete period;
- stale resource;
- timeout/5xx;
- malformed model action;
- repeated query/no-progress;
- cancel race;
- duplicate delivery;
- duplicate asset write;
- revoked permission after run;
- backend restart;
- app DB restore;
- high-cardinality dimension;
- ratio decomposition unsupported;
- seasonality insufficient data;
- missing principal in retry job.

UI/rendering:
- result schema cannot be normalized;
- chart inference unsuitable -> table fallback;
- empty result vs zero confused;
- unsupported column shape;
- guest embed unavailable;
- guest JWT/signing misconfiguration;
- guest resource unpublished;
- locked parameter mismatch;
- responsive analysis-card failure;
- browser service secret exposure.

## 20. Fast Track escalation criteria

Escalate toward Dima semantic core if repeated pilot evidence shows:
- metric identity drift;
- relationship ambiguity;
- ratio/non-additive ceiling;
- same business term binding drift;
- Metabase catalog provenance insufficient;
- multi-source semantic governance mandatory.

Rendering escalation rule:
- prefer native Dima chart/table;
- use guest embed only for a measured visualization-cost advantage;
- never make a generic Metabase workspace the fallback;
- never require paid embedding for the core product.

## 21. Definition of done

A user can:
1. ask a business question;
2. see Dima investigate it;
3. receive a supported finding;
4. inspect relevant chart/table evidence;
5. deepen the investigation;
6. review hypotheses;
7. receive recommendations;
8. record a decision;
9. produce a report;
10. return to history;

without needing to operate Metabase, a query builder, a collection browser, or a generic BI workspace.

Metabase remains an analytics engine behind Dima.


## 22. FT-UI-002 sealed rendering decision

Selected:
`OPTION_A = DIMA_NATIVE_CHART_TABLE`

Why:
- real pinned-Metabase result shape rendered successfully;
- existing generic `EChart` + `ResultTable` primitives are sufficient for the common product output;
- no new visualization framework or paid Metabase dependency is required;
- Dima keeps complete control over analyst narrative/evidence composition;
- browser proof passed on desktop flow and 390px viewport;
- guest embedding would add published-resource/JWT/locked-parameter machinery for a view-only surface that the common path does not currently need.

Guest embedding remains:
`OPTIONAL_FUTURE_VISUALIZATION_ESCAPE_HATCH`

It is not:
- FT-003 blocker;
- production dependency;
- required core capability.

FT-UI-002 certified run:
`35768067813`

Tested commit:
`3f4a34356d7b32a78c3c18f1c96a1879253001a2`

Real-result artifact digest:
`sha256:2ecaec2ad248f5d22d12503fa3dad3dab46539b85f3999b7b404f556a03780b3`

FT-003 is now OPEN.
