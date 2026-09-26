# Dima Metabase Platform — Current Handoff

**Date:** 2026-09-26  
**Branch:** `feat/dima-metabase-platform`  
**Directive start:** `af544a64f80e6e92553f28a9181d06530d0ddc85`

## Current truth

~~~text
P14-P21 = SEALED
Human Adoption = SEALED
ActionAuthorization = SEALED
Core A = SEALED
repository canonicalization = ACTIVE
Core B = NEXT immediately after cleanup seal
UI/UX = FORBIDDEN
external production execution = DEFERRED
DEV80 = DO NOT RUN
~~~

Canonical architecture is **Dima Core + Metabase/Metabot**. Wren and Ask-v2 are historical only and
must not be restored.

Current verified proofs at directive start:

~~~text
governance      36233076092 SUCCESS
Core A final    36233076110 SUCCESS
cleanup-focused 36232970637 SUCCESS
Alembic head    fb4e6d2a1074
engine          cbe313af9ac2d5960f662068e433d328d896fb06
~~~

## Immediate sequence

1. seal final repository canonicalization;
2. begin Core B without returning;
3. build stable headless product contracts/projections/resume/timeline/orchestration;
4. create clean `eval/core_b/` rehearsal corpus;
5. pass 24+ provider-free scenarios and security variants;
6. run 20–25 hardest-case pre-certification rehearsal;
7. freeze DEV80-ready candidate;
8. STOP without running DEV80 and without implementing UI.

Failure handling is always first wrong transition → owner → root cause → generic fix → focused proof.
