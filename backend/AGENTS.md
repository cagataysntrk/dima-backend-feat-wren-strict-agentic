# Dima Metabase Platform — Agent Engineering Contract

## Product authority

~~~text
branch = feat/dima-metabase-platform
canonical analytics = Metabase / Metabot
Dima = organizational intelligence + governed closed loop
repository canonicalization = SEALED
P14-P21 = SEALED
Core A = SEALED
Core B = ACTIVE
final target = SEALED NEUTRAL-COMPARISON CANDIDATE
external execution = DEFERRED
UI/UX = FORBIDDEN
Wren = historical / non-canonical
DEV80 / Validation50 / Hidden50 = NOT AUTHORIZED
~~~

## One analytics engine

Never add a second analytical execution path, dataframe/statistics shadow engine, raw-SQL fallback,
Wren fallback, or dual-engine abstraction. Metabase/Metabot owns analytical computation.

## Sealed-owner discipline

P14-P21, Human Adoption, ActionAuthorization and Core A change only for a measured defect.
Core B delegates to them and never duplicates truth.

Permanent distinctions:

~~~text
analytics != organizational authority
Outcome != causality
Memory != truth authority
Watch != analytics engine
Decision != Human Adoption
Adoption != external execution
timeline != authority
~~~

## Failure protocol

~~~text
FIRST WRONG TRANSITION
→ OWNER
→ ROOT CAUSE
→ GENERIC FIX
→ FOCUSED PROOF
~~~

Three rooted failures on the same invariant is an architecture STOP.

## Core B rules

Core B may own product DTOs, projection, navigation, correlation, deterministic pagination, resume,
capability discovery, observability and headless orchestration.

It must:
- reauthorize the current Principal on protected read/resume;
- preserve non-oracle behavior;
- resume from durable IDs/artifacts only;
- expose stale/superseded/inconclusive state explicitly;
- project timeline from existing owners;
- avoid raw SQLModel/table-shaped product contracts;
- add zero durable truth families unless a measured blocker proves one necessary.

## Testing / cost control

Use focused provider-free proofs during development, then one coherent provider-free closure.
Do not run DEV80, Validation50 or Hidden50. Do not restore them as automatic CI. Do not perform or
score the later neutral comparison.

## Prohibited work

- UI/frontend implementation
- external action execution or `action:execute`
- Wren restoration, evaluation, merge or winner selection
- Metabase core modification without genuine STOP
- second truth/receipt/analytics owner
- broad paid final certification
- hidden semantic fallback or test-trajectory branching
