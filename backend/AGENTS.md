# Dima Metabase Platform — Agent Engineering Contract

## 1. Product authority

~~~text
branch = feat/dima-metabase-platform
analytics engine = Metabase / Metabot
Dima = organizational intelligence + governed closed loop
P14-P21 = sealed
Core A = sealed
Core B = forward objective
external execution = deferred
UI/UX = forbidden
Wren = non-canonical historical architecture
~~~

## 2. One analytics engine

Never add a second analytical execution path, local dataframe/statistics shadow engine, raw-SQL
fallback, Wren fallback, or dual-engine abstraction. Dima may decide what should be investigated;
Metabase/Metabot owns analytical computation.

## 3. Sealed-owner discipline

P14-P21, Human Adoption, ActionAuthorization and Core A owners are modified only for a measured
defect. Product projections/orchestration must delegate to them instead of duplicating truth.

Permanent distinctions:

~~~text
analytics != organizational authority
Outcome != causality
Memory != truth authority
Watch != analytics engine
Decision != human adoption
Adoption != external execution
timeline != authority
~~~

## 4. Failure protocol

~~~text
FIRST WRONG TRANSITION
→ identify OWNER
→ establish ROOT CAUSE
→ make GENERIC FIX
→ run FOCUSED PROOF
~~~

Do not patch downstream symptoms. Do not tune deterministic semantics to test wording. Three failed
generic fixes on the same invariant is a supervisor STOP.

## 5. Testing and CI economy

Provider-free first. Use the smallest affected proof, then the required milestone closure. Do not
blind-rerun REDs. Do not spend broad final corpora during ordinary development.

DEV80 is a one-shot final broad gate and is explicitly forbidden by the current directive. The
current target is a DEV80-ready frozen candidate, not a DEV80 result.

## 6. Core B rules

Core B is a headless product layer, not a new truth authority. It may own DTOs, projection,
navigation, correlation, pagination, resume, capability discovery, observability and orchestration.

It must:
- expose stable tenant-bound product identities;
- reauthorize the current Principal on protected reads/resume;
- preserve non-oracle behavior;
- resume from persisted IDs/artifacts only;
- provide read-only artifact timeline projection;
- never expose raw internal table shapes as the product contract.

## 7. Prohibited work

- UI/frontend implementation
- external action execution or `action:execute`
- Wren restoration or bake-off
- Metabase core modification without genuine STOP
- migration edits merely for cleanup
- second truth/receipt/analytics owner
- archive folders for deleted legacy code
- routine Sol topology
- DEV80 dispatch
