# Dima Metabase Platform — Developer Guide

Current branch: `feat/dima-metabase-platform`

## Canonical product

~~~text
DIMA CORE
+
METABASE / METABOT
=
CANONICAL PRODUCTION ARCHITECTURE
~~~

Wren/Ask-v2 is historical only. Do not restore Wren runtime, dual-engine abstractions, old frontend,
or deleted operation trees.

## Read first

1. `backend/belgeler/metabase/DIMA_METABASE_CORE_CLOSURE_FINAL_ROADMAP.md`
2. `backend/belgeler/metabase/DIMA_METABASE_CURRENT_PRODUCT_PLAN.md`
3. `backend/belgeler/metabase/DIMA_METABASE_DECISION_RECEIPTS.md`
4. `backend/belgeler/metabase/DIMA_METABASE_CURRENT_HANDOFF.md`
5. relevant code + focused tests

## Current state

- Repository canonicalization: SEALED
- P14-P21: SEALED
- Human Adoption: SEALED
- ActionAuthorization: SEALED
- Core Closure A: SEALED
- Core Closure B: ACTIVE
- Final target: SEALED NEUTRAL-COMPARISON CANDIDATE
- External production execution: deferred
- UI/UX implementation: forbidden
- DEV80 / Validation50 / Hidden50: not authorized

## Engineering rules

Do not reopen sealed owners without a measured defect. Metabase/Metabot is the sole analytical
computation/execution owner. Dima owns organizational meaning, evidence, epistemics, reporting,
decision context and closed-loop organizational authority.

Normal failure handling:

~~~text
FIRST WRONG TRANSITION
→ OWNER
→ ROOT CAUSE
→ GENERIC FIX
→ FOCUSED PROOF
~~~

No regex/fuzzy/morph semantic patches. No shadow analytics. No test-specific behavior.
Provider-free first and CI economy always.

Core B is headless projection/orchestration over sealed owners. It exposes deliberate product DTOs,
reauthorizes the current Principal, preserves non-oracle behavior, resumes only from durable IDs,
and introduces no new truth family by default.

Git history is the archive. Do not recreate legacy/archive directories.
