# P15 — NATIVE METABASE EXPLORATION SOURCE REVIEW

**Date:** 2026-09-25  
**Status:** **SEALED / PROVIDER-FREE P15 NATIVE EXPLORATION IMPLEMENTATION AUTHORIZED**  
**Forward authority:** DMP-DEC-0048  
**Platform input checkpoint:** `01140b059318b2487b002a0c94f989fd693ce6f2`  
**Pinned engine:** `UpcyTech/dima-metabase-engine@cbe313af9ac2d5960f662068e433d328d896fb06`  
**Release:** `0.63.18-dima.6`

## 1. Scope

P15 does not create an Exploration Engine in Python.

The purpose of this review is to identify the real native analytical exploration owners already
present in the pinned Metabase engine and authorize the smallest product vertical that consumes them
without copying their algorithms.

Permanent boundary:

```text
Metabase / Metabot
= analytical exploration + interestingness + query semantics

Dima
= Research obligation + provenance + lead/material lineage + later epistemic promotion
```

Native "interesting" never means Dima VERIFIED finding.

## 2. Pinned-source findings

### 2.1 Metabot chart analysis is native interestingness

Pinned:
`src/metabase/metabot/tools/analyze_chart.clj`

The native `analyze_chart` tool consumes chart configurations already seeded into Metabot memory.
It calls:

```text
metabase.interestingness.core/compute-chart-stats
metabase.interestingness.core/generate-representation
```

and is intended for trends, outliers, volatility and pattern analysis.

Pinned:
`src/metabase/interestingness/core.clj`

This is the public facade for the native interestingness implementation.

Therefore Dima must not port chart statistics, outlier logic, trend logic or interestingness scoring
to Python.

### 2.2 Metabot memory is a native owner

Pinned:
`src/metabase/metabot/agent/core.clj`
`src/metabase/metabot/agent/memory.clj`

Native agent state owns queries/charts. Viewing-context `chart_configs` are seeded into native
agent memory; query/chart tool outputs update that state.

Dima may correlate Research work to native state/occurrences but must not create a competing
analytics-state model.

### 2.3 X-Ray / automagic dashboard is a provider-free native exploration capability

Pinned:
`src/metabase/xrays/api.clj`
`src/metabase/xrays/api/automagic_dashboards.clj`
`src/metabase/xrays/automagic_dashboards/core.clj`
`src/metabase/xrays/automagic_dashboards/interesting.clj`

The native route family is:

```text
/api/automagic-dashboards/
```

The ad-hoc entity path accepts a base64/form-encoded JSON dataset query.

Before analysis, the pinned route calls native
`query-perms/check-data-perms` for the ad-hoc query. It then delegates to
`automagic-dashboards.core/automagic-analysis`.

The native automagic implementation owns:
- field/dimension matching;
- metric/filter grounding;
- template selection;
- candidate-card generation;
- interestingness/selection;
- Top-N card selection;
- native metadata/query semantics.

Dima must not reproduce any of this.

Pinned encoding owner:
`src/metabase/xrays/automagic_dashboards/util.clj::encode-base64-json`

Conceptually:
```text
JSON query
→ UTF-8 bytes
→ base64
→ form encode
```

This is transport encoding only, not analytical compilation.

### 2.4 Important negative finding: generate_insights is not the selected product seam

Pinned file:
`src/metabase/metabot/tools/generate_insights.clj`

exists, but the current pinned `src/metabase/metabot/tools.clj` registry does not import/register
that tool in the active profile tool map reviewed here.

Do not build P15 around an assumed `generate_insights` tool merely because its source file exists.

### 2.5 Profile reality

Pinned:
`src/metabase/metabot/agent/profiles.clj`

The `:internal` profile exposes `analyze_chart`.
The ordinary `:nlq` profile is query-focused and does not expose `analyze_chart`.

P15 must respect actual profile/tool availability rather than assume a generic "Exploration" mode.

## 3. Authorized first P15 vertical

Use the already-sealed P14 occurrence as input:

```text
ResearchSession / obligation
→ VERIFIED P14 ResearchExecutionLink
→ exact persisted native query A
→ same principal-scoped NativeEngineBridge client
→ native GET /api/automagic-dashboards/adhoc/<encoded A>
→ native automagic/X-Ray material
→ durable P15 Research material record
→ source P14 Evidence/query provenance refs
```

This first vertical is intentionally provider-free and does not require a model call.

The same native session means Metabase remains permission authority.

## 4. P15 material semantics

Persisted P15 output is:

```text
RESEARCH_MATERIAL
```

It may be described as:
- exploration material;
- lead;
- candidate pattern;
- interesting native result;
- suggested follow-up.

It is **not**:
- VERIFIED claim;
- finding;
- root-cause evidence by itself;
- a confidence score owned by Dima.

P16 decides which explicit claims eligible Evidence supports/challenges/contextualizes.

## 5. Durable identity

A P15 material record must be bound to the prior authority chain:

```text
research_session_id
obligation_id
P14 ResearchExecutionLink id
native conversation/query identity
exact P14 query fingerprint
source Evidence ref(s)
native exploration kind
native payload fingerprint
created_at
epistemic state = RESEARCH_MATERIAL
```

Restart must reuse persisted material instead of repeating exploration blindly.

It is not an analytical definition store.

## 6. Forbidden implementation

P15 Python code must not contain or own:
- interestingness formulas/scorers;
- Top-N algorithm;
- trend/outlier/volatility algorithms;
- temporal analytics;
- query planner/repair;
- MBQL interpretation;
- join planning;
- X-Ray dashboard templates;
- native metric/dimension grounding;
- P13 attestation/re-execution middleware;
- Wren/raw SQL/Agent API fallback.

No engine patch is authorized.

## 7. Focused proof

Provider-free P15 must prove:
1. only a VERIFIED P14 occurrence can be explored;
2. same principal/native-subject session boundary is reused;
3. exact persisted query A is the native X-Ray input;
4. permission/native HTTP failures stay native failures;
5. native exploration payload is stored with deterministic fingerprint;
6. source P14 Evidence/query provenance remains linked;
7. epistemic state remains `RESEARCH_MATERIAL`;
8. restart returns persisted material without a second native exploration call;
9. no Python analytical primitive exists;
10. P14 native-direct regressions remain GREEN.

No Luna/Sol/C1/engine build is needed for this vertical unless provider-free evidence proves a
decision-changing native cognition uncertainty.

## 8. Exit

P15 closes when the vertical:

```text
Research obligation
→ native exploration
→ native analytical material
→ durable native provenance
→ Research lead/material record
→ prior execution/Evidence linkage
```

is provider-free GREEN with:

```text
Python analytical primitive copies = 0
engine patch                       = 0
second analytics authority        = 0
```

Then P16 claim-lineage implementation starts immediately.


---

## Implementation seal evidence

```text
tested SHA          = c529f28d34712d149f1c3c1e594a413974c37130
provider-free       = 36103561534 SUCCESS
engine changes      = 0
model calls         = 0
analytical copies   = 0
```

The provider-free gate also re-ran sealed P14 native-direct regressions successfully.

Status after implementation:
`SEALED / P15 NATIVE EXPLORATION GREEN / P16 CLAIM-LINEAGE NEXT`.
