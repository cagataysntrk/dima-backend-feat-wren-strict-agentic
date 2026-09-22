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

Status: STRATEGIC TARGET AND FIRST POC TARGET.

Strength:
- supported React SDK callbacks for dashboard parameters, visualization/question lifecycle, question run/save, and collection item clicks;
- best path to typed current-resource context;
- best customization ceiling without forking Metabase;
- current Dima frontend is React 19 and technically compatible with the SDK's React 18/19 requirement.

Constraint:
- production authenticated embedding is a separate capability/security qualification;
- local/evaluation modular POC is attempted first against the existing pinned Metabase major 63 substrate;
- if the current OSS runtime does not expose the required modular capability, classify that as a POC capability result; do NOT mutate the F0A substrate merely to make the UI test pass;
- the SDK is client-side and does not support SSR;
- exact SDK package resolution must be pinned before functional POC code.

### Normative path

FT-UI-002 has two distinct capability levels:

```text
POC-A / UI-P0
Local Modular Workspace + Context Bridge POC
-> may open FT-003 when GREEN

POC-B / UI-P1
Authenticated Production Embedding Qualification
-> required before external pilot / F9
```

POC-A is NOT production authentication certification.
POC-B is NOT required to begin the product vertical slice.

Implementation order:

```text
UX-0 native Metabase baseline
-> prove Model C first: modular workspace/frame
-> Dima Intelligence Sidecar
-> typed Context Bridge
-> architecture decision rule
-> FT-003 if POC-A GREEN
-> production embedding qualification before F9
```

Full-app remains an acceleration/fallback option, not a mandatory prerequisite to FT-003.
If Model C is GREEN, full-app may leave the critical path.

`full-app = optional acceleration/fallback strategy`

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

Before FT-003 product UI implementation, FT-UI-002 / POC-A must prove:

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

POC-A minimum hard gate additionally requires:
- existing F0A substrate unchanged;
- SDK major 63;
- exact SDK version pinned in lockfile;
- isolated `/fast-poc` route;
- Collection Browser;
- Dashboard;
- Question/query surface;
- Dima sidecar coexistence;
- at least three real typed context event families;
- normalized `AnalyticsContext`;
- DOM scraping = 0;
- guessed resource identity = 0;
- admin/service credential in browser = 0;
- desktop + narrow responsive proof;
- visible loading/error states;
- architecture model selected by rule.

POC-B remains required before external pilot / F9:
- production JWT SSO;
- individual Metabase principal;
- group/permission mapping;
- revocation/denial proof;
- production origin/session qualification.

## 16. Gate sequence

Backend gates are preserved:

```text
F0   governance / branch isolation
F0A  pinned Metabase capability
FT-002B Fast-owned Metabase Gateway
```

Before FT-003:

```text
FT-UI-001       Metabase Workspace Feasibility + UI Architecture Reconciliation
FT-UI-002/POC-A Local Modular Workspace + Context Bridge POC
FT-003          Fast Ask vertical slice
```

Before external pilot / F9:

```text
FT-UI-002/POC-B Authenticated Production Embedding Qualification
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
- FT-UI-002 / POC-A — local modular workspace + typed context POC
- FT-UI-002 / POC-B — authenticated production embedding qualification
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


## 22. FT-UI-002 automatic architecture decision rule

CASE A — SELECT MODEL C when:
- Collection browsing GREEN;
- Dashboard GREEN;
- Question/query workflow GREEN;
- Typed context GREEN;
- Navigation ACCEPTABLE;
- Responsive ACCEPTABLE;
- Local evaluation auth GREEN.

CASE B — SELECT HYBRID when:
- modular typed context is strong;
- broad workspace/navigation would otherwise require excessive custom host UI;
- full-app/native workspace provides the broad BI exploration surface;
- modular surfaces are used where Dima needs deep typed context.

CASE C — SELECT MODEL B FOR PRODUCT V1 when:
- modular has a material blocker;
- full-app is stronger for the V1 workspace;
- context completeness is explicitly FULL / PARTIAL / RESOURCE_ONLY;
- unknown filter/card state is never guessed.

CASE D — STOP when:
- both supported Metabase integration models fail critical POC requirements.

Do not automatically return to the legacy Dima BI shell.

## 23. FT-UI-002 isolated implementation boundary

POC route:
`dima-frontend-demo-master/src/app/fast-poc/page.tsx`

Preferred feature root:
`dima-frontend-demo-master/src/features/fast-poc/**`

Do NOT migrate or modify as part of POC:
- main `src/app/page.tsx`;
- DashboardView;
- DashboardsPanel;
- ReportPanel;
- AnalysisCanvas;
- existing production navigation.

POC composition only:
- thin Dima frame;
- modular Metabase surfaces;
- Dima sidecar;
- context inspector.

No fake Ask answer, fake AI result, fake root cause, or hardcoded finding.
