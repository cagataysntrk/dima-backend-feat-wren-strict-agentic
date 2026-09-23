# FT-005 REPAIR RECEIPT — MINIMAL_FOLLOWUP_PROMPT_CONTRACT_001

Status: PROVIDER_FREE_GREEN / LIVE_REPROOF_BLOCKED
Date: 2026-09-23
Branch: `feat/dima-metabase-product-fast-track`

PRODUCT_REPAIR_SHA:
`2282df3b6d9fc77e9cd20046da8e6d95d860921e`

PROMPT_CONTRACT_TEST_SHA:
`bfa721ff80ade67fa1978b5e3c83bc2be44db7e7`

## Why this repair was authorized

Evidence before the patch:

1. Luna and Sol full model matrix:
   `35816894471`

   Shared failure family:
   executable CONTEXTUAL/SELF_CONTAINED drafts repeatedly carried a short non-null reason,
   while the product validator requires executable reason=null.

2. Production follow-up prompt did not state that cross-field rule.

3. The prompt also did not explicitly state:
   - unsupported operations must use top-level UNSUPPORTED;
   - COUNT measure_hint must be null;
   - ambiguity must fail closed;
   - clarification answers complete the unresolved clarification question.

4. Real pinned-Metabase retrieval probe:
   `35817396762 GREEN`

   proved Turkish-only entity terms and entity+metric phrase missed direct SEARCH against English
   metadata, while an English entity/table lookup term hit directly.

## Product change

Only:
`backend/app/fast/followup_cognition.py`

Added explicit generic instructions for:
- executable vs non-executable typed shape;
- top-level UNSUPPORTED representation;
- COUNT/SUM measure-hint shape;
- FT-003-equivalent entity/table metadata lookup wording;
- likely English entity/table term for non-English questions;
- ambiguity fail-closed;
- clarification-answer completion semantics.

Unchanged:
- FastFollowupResolution schema;
- AskDraft schema;
- conversation service;
- context authority;
- run manager;
- resource registry;
- query builder;
- Metabase Gateway;
- temporal binder;
- evidence builder.

Added algorithms:
`0`

Added dictionaries/glossaries:
`0`

## Deterministic regression proof

FT-005 core on product repair:
`35817877655 GREEN`

Passed:
- Fast boundary static;
- FT-005 conversation semantics/API;
- FT-004 lifecycle regression;
- FT-003 regression.

FT-005 core on prompt-contract test commit:
`35817891294 GREEN`

Real Gateway regression:
`35817877667 GREEN`

Real browser regression:
`35817877576 GREEN`

## Live model re-proof state

Eval-only Luna contract probe:
`35817686083`

Result:
`TRANSPORT_PROVIDER_FAILURE`

All calls:
`HTTP 403 — OpenRouter key total limit exceeded`

No semantic output was produced.

Third-model real-Metabase E2E after product repair:
`35817877779`

Result:
`TRANSPORT_PROVIDER_FAILURE`

Failure occurred on first model call before a turn/result/evidence could be established.

Measurement credential probe:
`35818129429`

Result:
`BLOCKED_NO_MEASURE_CREDENTIAL`

The two-case Luna smoke was skipped before any API call.

## Certification decision

The repair is:
`DETERMINISTICALLY SAFE`

The repair is NOT yet:
`REAL_MODEL_CERTIFIED`

Therefore:
`FT-005_FINAL = OPEN`

No claim is made that Luna/Sol semantic failures are fixed until the canonical live matrix can run again.

## Exact unblock / re-proof

When canonical OpenRouter capacity becomes available:

1. run Luna frozen focused corpus;
2. require hard cases GREEN;
3. run Luna real-Metabase Q1 -> Q2 -> Q3;
4. require exact DB oracle:
   - Q1 SUM = 16270;
   - Q2 SUM = 21994;
   - Q3 East/North/South/West = 5523/5425/5474/5572;
5. run Sol comparable on remaining RED/borderline cases;
6. run Sol ceiling confirmation separately;
7. re-run FT-003/FT-004 regressions if any further product patch occurs;
8. seal FT-005 only after the above.

Do not open FT-006 before FT-005 seal.
