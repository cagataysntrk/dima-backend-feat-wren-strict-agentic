# DIMA DAY 6.5 — M0E METABASE CAPABILITY EXHAUSTION + BUILD-vs-BUY

**Status:** ACTIVE READ/CLASSIFICATION GATE  
**Date:** 2026-09-22  
**Phase:** current M0 completion gate; **NOT a new Day**  
**Implementation mandate:** NONE by default  
**Source-copy/port/vendor/transliteration:** FORBIDDEN  
**Production Metabase dependency:** OFF

## 1. Purpose

D65-M0E exists to answer one question before X0:

> Have all Dima-relevant Metabase capabilities been classified so we do not either
> reimplement mature generic infrastructure blindly or outsource Dima's unique trust/cognition
> responsibilities to an external runtime?

M0E is an **exhaustion/classification gate**, not an implementation spree.

## 2. Source identity

Canonical upstream:

```text
repo                 = metabase/metabase
pinned reference SHA = 74216b30981d8310c4cf724d63ca282e2e63529d
current master SHA   = fff70175e0b5f82dc0eb267593c717c4a6130206
current delta        = 1 commit
relevant code drift  = NONE
delta files          = locale *.po only
```

The pinned SHA remains the M0E source authority until a later explicit repin receipt.

## 3. Build-vs-buy default

```text
BUILD ONLY WHAT MAKES DIMA DIMA.

REUSE MATURE GENERIC INFRASTRUCTURE
WHEN IT ALREADY SOLVES THE GENERIC PROBLEM
WITHOUT BREAKING DIMA AUTHORITY / SECURITY / SEMANTIC OWNERSHIP.
```

Do not rebuild mature generic infrastructure merely because "native is cleaner".
Do not add Metabase runtime merely because "Metabase already has it".

## 4. Allowed dispositions

Every Dima-relevant Metabase mechanism MUST end in exactly one disposition:

```text
DIMA_CORE_NATIVE
WREN_OWNS
METABASE_RUNTIME_CANDIDATE
PATTERN_ONLY
DEFER_PRODUCT
NOT_APPLICABLE
REJECT
```

Definitions:

- **DIMA_CORE_NATIVE** — Dima's differentiating cognition/trust/product semantics. We own it.
- **WREN_OWNS** — Wren already owns the semantic primitive correctly; do not duplicate it.
- **METABASE_RUNTIME_CANDIDATE** — mature runtime capability worth testing through supported API in X0/full-X.
- **PATTERN_ONLY** — upstream behavior/invariant is valuable but a Metabase runtime dependency is unnecessary.
- **DEFER_PRODUCT** — relevant later, not required for current MVP architecture.
- **NOT_APPLICABLE** — no material Dima relevance.
- **REJECT** — conflicts with Dima architecture/security/authority or has unacceptable dependency cost.

## 5. Mandatory row schema

Every classified mechanism records:

```text
mechanism
exact upstream source evidence
problem solved
maturity / why it exists
Dima equivalent
Wren equivalent if any
current gap
disposition
WHY this disposition
native implementation cost = LOW | MEDIUM | HIGH
Metabase runtime dependency if reused
authority/security impact
semantic duplication risk
operational dependency
license/API implication
required behavioral proof
timing = PRE-X0 | X0 | FULL-X | DAY7-15 | POST-MVP
```

## 6. Capability families to exhaust

This is capability-level, not "read every file".

Already-audited families remain valid:
- `metabot`
- `agent_api`
- `mcp`

M0E expands the map across at least:

```text
agent_lib

query_processor
lib
lib_be
lib_metric

query_permissions
permissions
api_scope
api_keys

search

metrics
models
model_persistence

cache
sync
driver

dashboards
collections

activity_feed
audit_app

embedding
```

Workflow per family:

```text
subsystem map
→ identify Dima-relevant mechanisms
→ exact-source read only for those mechanisms
→ disposition
→ required behavioral proof
```

## 7. Default ownership model before X0

```text
DIMA
= cognition
  accepted authority
  uncertainty / clarification
  research
  evidence
  root-cause
  recommendations / decisions
  QueryContract / trust plane

WREN
= agent-facing semantic backbone
  MDL
  models
  relationships
  views
  cubes
  knowledge / business context
  semantic compilation

METABASE
= mature runtime candidate for overlapping generic BI/query-lifecycle mechanisms
  + architecture/reference source
  + future workspace/product candidate

DB
= underlying result/data execution truth
```

Permanent boundary:
- Metabase may not mint Dima semantic authority.
- Metabase execution success does not transfer semantic ownership.
- Wren semantic definitions are not silently duplicated/re-owned by Metabase.

## 8. Baseline classification hypotheses

These are defaults to be source-verified, not blind conclusions:

| Capability | Default disposition |
|---|---|
| Research cognition | DIMA_CORE_NATIVE |
| Accepted authority | DIMA_CORE_NATIVE |
| Evidence / completion truth | DIMA_CORE_NATIVE |
| QueryContract / trust receipt | DIMA_CORE_NATIVE |
| MDL / models / relationships / cubes / knowledge | WREN_OWNS |
| construct / validate / repair / resolve query lifecycle | METABASE_RUNTIME_CANDIDATE |
| permission-aware execute/replay | METABASE_RUNTIME_CANDIDATE + Dima invariant |
| query handle / continuation identity | METABASE_RUNTIME_CANDIDATE or PATTERN_ONLY, X0 decides |
| generic agent-loop mechanics | PATTERN_ONLY / already adopted |
| raw/native SQL bypass surfaces | REJECT for Dima governed path |
| dashboard / collections / workspace | DEFER_PRODUCT or later runtime candidate |
| semantic authority | REJECT for Metabase ownership |

## 9. Behavioral-proof rule

"Pattern adopted" is not enough.

For every PRE-X0 `PATTERN_ONLY` / `DIMA_CORE_NATIVE` security or authority invariant:

```text
upstream mechanism
→ Dima invariant
→ implementation owner
→ executable behavioral proof
```

Examples:

```text
query_handle != authorization
→ QueryContract/reference != permission
→ permission revoked
→ replay denied
```

```text
structured query cannot smuggle SQL
→ governed structured execution boundary
→ nested native marker
→ fail closed
```

## 10. Wren semantic backbone default-retain

Binding default:

```text
Wren semantic backbone = RETAIN
```

Includes:
- MDL
- models
- relationships
- views
- cubes
- knowledge/business context
- semantic compilation

D65-X0 is **not** a Wren semantic-removal experiment.

Any Wren semantic-backbone removal/replacement requires a separate architecture consultation,
semantic-equivalence/migration evidence and explicit authority change.

## 11. Relation to D65-SI and X0

M0E runs in parallel with the provider-control ladder.

Required progression:

```text
chosen provider topology P0=0
+
M0E classification/exhaustion sufficiently complete
→ D65-SI

D65-SI GREEN
→ real Standard Wren sentinel GREEN
→ M0E final cross-check
→ X0
```

No Metabase implementation spree before X0.

## 12. X0 question after M0E

Naive question:

```text
Wren vs Metabase?
```

is rejected.

The correct question:

> Does Metabase runtime provide enough **residual engineering value** on top of Dima + retained
> Wren semantics to justify a permanent runtime dependency?

Primary arms:

```text
ARM A
Dima
+ retained Wren semantics
+ Wren execution/query lifecycle
+ accepted Dima-native Metabase-derived invariants

ARM B
Dima
+ SAME retained Wren semantic meaning
+ thin Metabase Agent API construct/validate/execute lifecycle
+ SAME Dima authority/evidence
```

## 13. M0E exit gate

Before X0:

```text
Dima-relevant Metabase mechanisms UNCLASSIFIED                  = 0
PRE-X0 authority/security mechanisms without disposition        = 0
PATTERN_ONLY / DIMA_CORE_NATIVE PRE-X0 items without owner      = 0
WREN_OWNS items with duplicate Metabase semantic ownership      = 0
METABASE_RUNTIME_CANDIDATE items without explicit X0 question   = 0
```

`DEFER_PRODUCT` does not require implementation.

## 14. STOP / consultation

STOP before:
- copying/porting/vendorizing Metabase source;
- changing Dima authority/trust ownership because Metabase has a similar mechanism;
- changing Wren semantic-backbone ownership;
- production Metabase dependency;
- full D65-X;
- any runtime choice based only on UI attractiveness or one query result.
