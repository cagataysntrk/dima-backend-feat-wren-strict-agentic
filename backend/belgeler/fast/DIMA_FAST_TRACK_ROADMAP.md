# DIMA FAST TRACK — METABASE-FIRST PRODUCT ROADMAP

Status: NORMATIVE BRANCH ROADMAP
Audit verdict: FEASIBLE_WITH_GATED_UI_COMPOSITION
Last architecture reconciliation: 2026-09-22

## 1. Product thesis

Fast Track is not Wren-first, DimaSemanticSpec-first, or a Metabase frontend fork.

The product is:

```text
DIMA PRODUCT
├─ Analytics Workspace ........ Metabase-owned
└─ Intelligence Experience .... Dima-owned
```

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
Dima frame
├─ Analytics
│  ├─ Metabase browser / collections
│  ├─ Metabase dashboards
│  ├─ Metabase questions / query builder
│  ├─ Metabase filters / drill-down
│  └─ Metabase BI asset lifecycle
└─ Intelligence
   ├─ Ask Dima
   ├─ Analyst
   ├─ Research
   ├─ Evidence
   ├─ Root Cause
   ├─ Hypotheses
   ├─ Decisions
   └─ Reports
```

The product principle is:

> Do not rewrite mature commodity BI UX. Spend Dima engineering effort on analyst cognition, research, evidence, root cause, hypotheses, decisions, and action-oriented workflows.

## 2. Ownership boundary

### Metabase owns commodity BI workspace

Primary owner for:
- analytics navigation;
- collections;
- dashboards;
- saved questions;
- graphical query builder;
- visualizations;
- filters;
- drill-down;
- search;
- metric/model exploration;
- BI asset lifecycle.

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

Dima evidence, research, conversation, decision, and report state remains Dima-owned state.

Metabase question/dashboard/collection state remains Metabase app-DB-owned state.

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

Three models were reviewed in `predev/FT_UI_METABASE_WORKSPACE_RECONCILIATION.md`.

### Model A — Existing Dima Shell

Existing Next.js Dima frontend + Metabase only as backend/API.

Status: NOT NORMATIVE as the primary BI workspace.

Reason:
- quickest only if embedding capability is unavailable;
- duplicates mature BI navigation/dashboard/query-builder/search lifecycle;
- highest long-term frontend maintenance;
- current Dima-specific surfaces remain valuable, but commodity BI surfaces should not be expanded as the primary path.

### Model B — Full Metabase Workspace + Dima Intelligence Layer

Metabase full workspace + Dima frame/branding + Dima sidecar.

Status: VALID ACCELERATION STRATEGY, NOT PERMANENT ARCHITECTURE.

Strength:
- fastest route to complete analytics workspace UX;
- mature collections/search/navigation/query/drill behavior.

Constraint:
- supported full-app embedding is iframe-based;
- supported host-side typed context callbacks are much weaker than the modular SDK;
- full-app is therefore insufficient as the permanent answer to the typed Context Bridge requirement.

### Model C — Thin Dima Shell + Modular Metabase Surfaces

Dima frame + modular Metabase browser/dashboard/question/query-builder + Dima-native intelligence.

Status: STRATEGIC TARGET.

Strength:
- supported React SDK callbacks for dashboard parameters, visualization/question lifecycle, question run/save, and collection item clicks;
- best path to typed current-resource context;
- best customization ceiling without forking Metabase;
- current Dima frontend is React 19 and technically compatible with the SDK's React 18/19 requirement.

Constraint:
- authenticated interactive modular surfaces are a Metabase capability/entitlement dependency;
- the SDK is client-side and does not support SSR;
- exact SDK/runtime version must be pinned before POC.

### Normative path

```text
UX-0 native Metabase baseline
-> UX-1 Metabase-first workspace/frame POC
-> UX-2 Dima Intelligence Sidecar
-> UX-3 typed Context Bridge
-> UX-4 Dima-native Research/Decision surfaces
-> UX-5 selective modularization / modular-first convergence
```

The implementation strategy may use full-app early for acceleration, but the architecture converges toward modular Metabase surfaces where Dima requires typed context and richer composition.

`full-app = acceleration strategy`

`full-app != permanent architecture`

## 13. UI hard invariants

```text
METABASE_FRONTEND_FORK = 0
METABASE_SOURCE_PATCH_FOR_DIMA_UI = 0

DIMA_INTELLIGENCE_OWNER = DIMA
METABASE_BI_WORKSPACE_OWNER = METABASE

DIMA_BACKEND_CAN_RUN_WITHOUT_METABASE_EMBED = required
METABASE_SERVICE_SECRET_IN_BROWSER = 0

RAW_DOM_CONTEXT_SCRAPING = 0
DIMA_CONTEXT_USES_TYPED_RESOURCE_IDS = required

METABASE_AI_BECOMES_DIMA_RESEARCH_OWNER = 0
DIMA_EVIDENCE_AND_DECISION_STATE_IN_METABASE_ONLY = 0
```

## 14. UX phases

### UX-0 — Metabase Baseline

Open pinned Metabase in native UI against representative data.

Audit:
- home;
- collections;
- dashboard;
- question;
- query builder;
- filters;
- drill-down;
- search;
- responsive behavior;
- basic accessibility.

Output:
- screenshots/receipts;
- Dima-vs-Metabase UX gap inventory;
- explicit list of commodity UI we will stop rebuilding.

### UX-1 — Dima Branding / Frame POC

Prove Metabase analytics can live inside the Dima parent experience without source fork.

Test:
- logo/brand treatment;
- typography/colors;
- chrome/nav visibility;
- Dima parent shell;
- full-app embed or supported equivalent;
- auth;
- permissions;
- responsive layout.

Do not put a Metabase service/admin secret in browser.

### UX-2 — Dima Analyst Sidecar

Same screen:
- Ask Dima;
- Analyst;
- Research;
- Evidence.

The Dima Fast backend is the cognition owner.

Metabase AI is not the Dima research owner.

### UX-3 — Context Bridge

Minimum typed context:

```text
current dashboard
current question
current card/model/table
metric
filters
date range
selected visualization
```

Target user action:
> “Investigate the drop in this chart.”

No raw DOM scraping.

Prefer supported Metabase SDK callbacks/resource objects and stable entity IDs.

### UX-4 — Dima-native Intelligence Workspace

Dima-native:
- research timeline;
- evidence;
- root cause;
- hypotheses;
- decisions;
- reports.

### UX-5 — Selective Modularization

Weak full-app areas can be replaced with supported modular components.

Expected eventual mix:

```text
Home / Research / Decisions / Reports .... Dima-native
Collections / Dashboard / Question ....... Metabase
Query Builder / Drill / Filters .......... Metabase
Analyst / Evidence / Root Cause .......... Dima-native
```

## 15. UI POC hard gate

Before FT-003 product UI implementation, FT-UI-002 must prove:

1. Metabase workspace is usable inside Dima parent experience.
2. Dima sidecar can coexist on the same screen.
3. Current analytics context can be transferred to Dima through typed identifiers/state.

GREEN criteria:

```text
Metabase workspace usable
branding acceptable
Dima analyst panel coexists
no Metabase frontend fork
no browser service secret
typed current-resource context obtainable
dashboard/question navigation intact
permissions not bypassed
acceptable responsive behavior
```

If RED:
- classify cause;
- do not immediately fall back to custom Dima BI;
- compare full-app vs modular remediation separately.

## 16. Gate sequence

Backend gates are preserved:

```text
F0   governance / branch isolation
F0A  pinned Metabase capability
FT-002B Fast-owned Metabase Gateway
```

Before FT-003:

```text
FT-UI-001 Metabase Workspace Feasibility + UI Architecture Reconciliation
FT-UI-002 Metabase/Dima Workspace POC
FT-003    Fast Ask vertical slice
```

Then:

```text
F1 / FT-003   one question, one real answer in selected workspace
F1A           temporal/resource safety
F2 / FT-005   conversation
F3 / FT-006   evidence
F4 / FT-007   analyst
F5 / FT-008   root cause
F6 / FT-009   Metabase-first dashboard/asset integration
F7            decision/report
F8            product polish
F9            pilot security
F10           frozen benchmark
F11           pilot readiness
F12           production candidate
```

No authority-changing gate is skipped.

FT-009 no longer means “build a separate Dima dashboard product by default.”
It means:
1. reuse Metabase dashboard lifecycle first;
2. bind Dima findings/evidence to Metabase assets by typed identity;
3. add Dima-native dashboard UI only where a measured product gap remains.

## 17. Core tickets

- FT-001 — branch/governance
- FT-002 — capability + Fast-owned Metabase Gateway
- FT-UI-001 — workspace feasibility + architecture reconciliation
- FT-UI-002 — Metabase/Dima workspace POC
- FT-003 — real Ask vertical slice in selected Metabase-first workspace
- FT-004 — streaming/run-state/cancel
- FT-005 — conversation
- FT-006 — Evidence Lite
- FT-007 — Analyst Mode
- FT-008 — Root Cause v1
- FT-009 — Metabase-first dashboards/assets
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

UI/workspace:
- embed capability unavailable;
- SSO/session failure;
- third-party cookie/SameSite failure;
- SDK/runtime version mismatch;
- iframe/full-app context bridge insufficient;
- modular callback/context incomplete;
- entity navigation broken;
- save/edit permission mismatch;
- parent/embedded route desynchronization;
- responsive layout failure;
- inaccessible sidecar/focus flow.

## 20. Fast Track escalation criteria

Escalate toward Dima semantic core if repeated pilot evidence shows:
- metric identity drift;
- relationship ambiguity;
- ratio/non-additive ceiling;
- same business term binding drift;
- Metabase catalog provenance insufficient;
- multi-source semantic governance mandatory.

Escalate from full-app toward modular surfaces if:
- typed context cannot be obtained;
- navigation state cannot be synchronized safely;
- Dima sidecar cannot coexist responsively;
- branding/chrome is materially insufficient;
- product action hooks require supported callbacks unavailable in iframe composition.

The Dima intelligence UX must survive either escalation.

## 21. Definition of done

A user can:
1. enter a mature analytics workspace;
2. browse governed BI content;
3. ask Dima about current analytics context;
4. follow up;
5. request analysis;
6. ask why;
7. see bounded research;
8. inspect evidence;
9. save/reuse Metabase BI assets;
10. record a Dima decision;
11. produce a Dima report;
12. return to history;

without silent fallback, hidden semantic substitution, Metabase frontend fork, or duplicated commodity BI ownership.
