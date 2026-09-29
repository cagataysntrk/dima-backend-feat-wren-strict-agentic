# P12 — UX MODE EVIDENCE MATRIX

**Milestone:** P12 — BI Workspace Feasibility  
**Platform baseline:** `9de113b779ebd261b1d0b14ba58c893b79d145b2`  
**Pinned Metabase:** `v0.63.18 / 2ba2485c78d7e00a9a25f82c00fc201da71590c4`  
**Observed Fast Track:** `3fc686c9fa4f86927a5ea51f43cf688b9c010a6c` — moving reference only  
**Observed ask-v2:** `3d807ee2698733ea01620e5ce6c85e88466b785a` — reference only

This matrix is product/workspace evidence. Metabase content/UI objects are not Dima semantic authority.

## 1. Pinned Metabase workspace surface

Pinned v0.63.18 source/docs contain native:
- dashboards and dashboard filtering/interaction;
- collection browsing;
- saved question/Card lifecycle;
- query builder;
- interactive questions;
- full-app embedding surfaces;
- modular embedding surfaces including CollectionBrowser, InteractiveDashboard,
  EditableDashboard and InteractiveQuestion.

This establishes product capability availability, not entitlement/security certification for every
embedding mode.

## 2. Fast Track reference evidence

The current moving Fast Track branch contains sealed evidence for:
- Dima-native chart/table rendering from real pinned-Metabase results;
- Dima-owned run lifecycle;
- replayable SSE;
- clarification/cancel state;
- conversation lineage primitives;
- typed Metabase gateway.

These are controlled-harvest candidates only. No code is merged or cherry-picked in P12.

## 3. UX mode matrix

| Mode | User continuity | Auth/session | Tenant isolation | Visualization | Saved artifacts / collections / QB | Branding/control | Coupling | Initial engineering cost | Evidence status |
|---|---|---|---|---|---|---|---|---|---|
| EMBED | medium-high if integrated well; iframe/modular boundary matters | requires explicit embed/session/SSO proof | must preserve Metabase principal/permissions; P10B2 advanced lenses still profile-gated | strongest native Metabase surface | strongest native workspace surface | medium for full-app, high for modular | medium-high | medium-high | CAPABILITY AVAILABLE / NOT INITIAL DEFAULT |
| LINK_OUT | context switch to Metabase | independent Metabase authenticated session | native Metabase permissions | full native UI | full native workspace | low Dima control | low | lowest | AVAILABLE ESCAPE HATCH |
| HEADLESS_API | seamless inside Dima | Dima server controls current principal and substrate calls | aligns with P5/P10 execution envelope | requires Dima renderer or bounded optional escalation | saved-workspace lifecycle must be explicitly bridged | high | low-medium | low-medium | STRONG FOR INITIAL ANALYTICS |
| DIMA_SHELL | strongest Dima product continuity | Dima-owned app/session; substrate stays hidden | strongest control, but every workspace feature must keep Metabase permission truth | Fast Track proves native chart/table path | commodity BI breadth is not automatically reproduced | highest | lowest UI identity coupling | low for current Ask path, high if rebuilding all BI | PRIMARY PRODUCT SHELL |

## 4. Initial product selection

Selected initial composition:

```text
DIMA_SHELL
+
HEADLESS_API
+
LINK_OUT for mature native Metabase workspace needs
```

Reason:
- Dima Ask/research/evidence/decision experience remains primary;
- current Fast Track proves real-result Dima-native rendering and run lifecycle primitives;
- Metabase stays hidden as analytics substrate for the common path;
- no need to rebuild the entire Metabase workspace before product progress;
- advanced collection/dashboard/query-builder work can use controlled LINK_OUT initially;
- EMBED remains an optional escalation only when a measured continuity/context requirement justifies
  its auth/session/coupling cost.

This is a feasibility selection, not integration authorization.

## 5. Non-negotiable ownership

```text
Metabase dashboard/question/collection/card
!= Dima business truth

Metabase UI navigation
!= semantic authority

Fast Track renderer/run lifecycle
!= Platform semantic/security authority
```

P12 may harvest presentation/run-lifecycle primitives later only under an owning implementation ticket.

## 6. Open product gaps

- production tenant-user collection persistence permission remains P10B2 `CAPABILITY_GAP`;
- RLS/CLS/advanced lens profiles remain uncertified;
- Dima Shell does not yet provide native Metabase collection/query-builder breadth;
- LINK_OUT continuity/context handoff is not yet specified;
- EMBED exact auth/session/entitlement/runtime contract is not certified on Platform;
- mobile/responsive behavior must be measured on the chosen production composition.

## 7. Exit

P12 feasibility can close without embedding implementation when:
- the four modes are classified;
- an initial product mode is selected;
- semantic authority remains Dima-owned;
- unresolved security/workspace gaps remain explicit;
- Fast Track remains controlled harvest only.
