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

Wren/Ask-v2 is historical only. Do not restore Wren runtime, Wren source, dual-engine abstractions,
old frontend, or deleted legacy operation paths.

## Read first

1. `backend/belgeler/metabase/DIMA_METABASE_CORE_CLOSURE_FINAL_ROADMAP.md`
2. `backend/belgeler/metabase/DIMA_METABASE_CURRENT_PRODUCT_PLAN.md`
3. `backend/belgeler/metabase/DIMA_METABASE_DECISION_RECEIPTS.md`
4. `backend/belgeler/metabase/DIMA_METABASE_CURRENT_HANDOFF.md`
5. relevant code + focused tests

## Current state

- P14-P21: SEALED
- Human Adoption: SEALED
- ActionAuthorization: SEALED
- Core Closure A: SEALED
- Repository canonicalization: active until sealed
- Forward objective: Core Closure B headless product engine
- External execution: deferred
- UI/UX implementation: forbidden
- DEV80: do not run under the current directive

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

No regex/fuzzy/morph/prompt patches for semantic truth. No shadow analytics. No test-specific
business behavior. Provider-free first; broad gates only at their authorized milestone.

Core B must remain headless and expose product DTO/projection contracts rather than raw SQLModel
tables. Resume uses persisted IDs/artifacts; never raw-prompt reinterpretation.

Git history is the archive. Do not create new legacy/archive directories for deleted systems.
