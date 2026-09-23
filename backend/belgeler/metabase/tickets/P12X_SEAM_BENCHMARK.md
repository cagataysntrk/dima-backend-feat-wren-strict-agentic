# P12X-001 — Vanilla vs Agent API vs native Metabot seam benchmark

**Milestone:** P12X  
**Status:** AUTHORIZED LAB MEASUREMENT / NO PRODUCT ROUTING / NO FORK  
**Decision:** `DMP-DEC-0030`

## Goal

Produce a reproducible V0+A+B capability comparison on the Boyahane 80-table dataset and determine
whether the Agent API integration boundary loses material native Metabot capability.

## Required outputs

```text
dataset_identity.json
schema_snapshot.json
corpus_v1.json
oracle_v1.json
runtime_identity.json
vanilla_results.json
agent_api_results.json
native_metabot_results.json
comparison_report.json
```

## Files allowed

```text
backend/lab/metabase/p12x/**
backend/belgeler/metabase/predev/P12X_*
backend/belgeler/metabase/tickets/P12X_*
backend/belgeler/metabase/UPSTREAM_ENGINE_HARVEST_MAP.md
.github/workflows/dima-metabase-p12x.yml
DIMA-METABASE-DURUM.md
DIMA-METABASE-HANDOFF.md
decision/failure receipts
```

## Files forbidden

Product owners:
```text
backend/app/v3/**
backend/app/fast/** on Platform
/api/ask-v2 routing
frontend product code
```

External/source:
```text
feat/ask-v2-mvp
feat/dima-metabase-product-fast-track
cagataysntrk/metabase-boyahane
metabase/metabase
```

No merge/cherry-pick/rebase.

## Phases

X0:
freeze dataset/runtime/corpus/oracle and reproduce exact benchmark Vanilla.

X1-A:
run existing external-cognition/Agent API representative path without copying Fast code.

X1-B:
run minimal lab-only native agent-streaming harness.

Compare and classify. Stop.

## Fork gate

`P12X-C = NOT AUTHORIZED`.

## Product gate

`P13 = PAUSED FOR METABASE SEAM DECISION`.
