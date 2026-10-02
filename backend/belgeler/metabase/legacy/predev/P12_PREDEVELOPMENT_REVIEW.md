# P12 — PRE-DEVELOPMENT REVIEW

**Milestone:** P12 — BI Workspace Feasibility  
**Branch:** `feat/dima-metabase-platform`  
**P11 closure:** `9de113b779ebd261b1d0b14ba58c893b79d145b2`  
**Pinned Metabase:** `v0.63.18 / 2ba2485c78d7e00a9a25f82c00fc201da71590c4`

Status: **SEALED / WORKSPACE FEASIBILITY CLASSIFICATION AUTHORIZED / INTEGRATION NOT AUTHORIZED**

## 1. Purpose

P12 is a product/workspace track.

Evaluate:
- charts;
- dashboards;
- collections;
- saved questions;
- query builder;
- exploration/navigation detail

against the intended Dima product UX.

P12 does not own semantic cognition, semantic truth, query authority or security truth.

## 2. Product invariant

```text
Dima UX = primary user product

Metabase UI/content = workspace/substrate capability

Metabase UI object != Dima business truth
```

No P12 decision may make a Dashboard/Card/Collection name authoritative semantic identity.

## 3. Candidate modes

Evaluate only:
- `EMBED`;
- `LINK_OUT`;
- `HEADLESS_API`;
- `DIMA_SHELL`.

Evidence matrix:
`backend/belgeler/metabase/predev/P12_UX_MODE_EVIDENCE_MATRIX.md`.

## 4. Initial feasibility decision

Initial product mode:

```text
DIMA_SHELL + HEADLESS_API
with LINK_OUT as mature-workspace escape hatch
```

`EMBED` remains a future measured escalation, not the default.

This decision minimizes product coupling while preserving Dima-native conversation/evidence/research UX
and avoiding a premature rebuild of commodity BI.

## 5. Fast Track controlled harvest

Observed moving reference at review time:
`3fc686c9fa4f86927a5ea51f43cf688b9c010a6c`.

Relevant candidate primitives already evidenced there:
- Dima-native chart/table rendering;
- run state machine;
- SSE/replay;
- cancel/retry lineage;
- conversation lineage;
- typed Metabase gateway.

Rules:
- reference only;
- fetch then-current Fast Track SHA at the owning implementation ticket;
- inspect exact primitive and ownership;
- port only the minimum architecture-independent contract;
- no merge/cherry-pick/rebase;
- no Fast Ask semantic/retrieval heuristics in P12.

## 6. Security constraints

P12 inherits P10B2:
- collection permission = capability gap;
- RLS/CLS profile-dependent/unproven;
- advanced database routing = external owner;
- cache/result reauthorization = capability gap;
- global production official issuance blocker remains open.

Workspace capability must never bypass these gaps.

## 7. No implementation yet

This review does not authorize:
- embedding runtime integration;
- collection/dashboard persistence code;
- frontend rewrite;
- Metabase frontend fork;
- Fast Track bulk import;
- semantic logic harvest.

A later P12 implementation/POC ticket must specify the exact product gap being tested.

## 8. Exit

P12 feasibility classification is complete when the mode matrix and initial selection are reviewed.
P13 may begin production Standard seam work independently; unresolved enterprise/workspace families stay
typed and profile-blocking where required.
