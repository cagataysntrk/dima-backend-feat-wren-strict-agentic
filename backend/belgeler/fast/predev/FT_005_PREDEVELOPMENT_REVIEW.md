# FT-005 — CONVERSATION + FOLLOW-UP CONTEXT PRE-DEVELOPMENT REVIEW

Status: APPROVED FOR PROVIDER-FREE IMPLEMENTATION
Date: 2026-09-22
Branch: `feat/dima-metabase-product-fast-track`

Upstream seals:
- FT-003 First Real Ask: CLOSED / GREEN
- FT-004 Run Lifecycle: CLOSED / GREEN
- FT-004 post-seal invariants: CLOSED / GREEN
- final post-seal audited SHA: `f8018800c773019f0e79907fec3e15edec72dbb0`
- focused post-seal run: `35781659952 GREEN`

## 1. Goal

FT-005 adds Dima-owned conversation identity, turn lineage and safe follow-up context above the sealed Fast Ask + run layers.

The target is NOT a chat-history prompt.

The target is:

```text
new user turn
+
typed accepted prior context
↓
bounded follow-up cognition
↓
current resource/field permission revalidation
↓
new immutable Fast run
↓
new evidence
↓
turn result
```

Every analytical execution is a separate run.

Terminal runs never reopen.

## 2. Critical distinction

```text
conversation != model chat-history dump
retry        != follow-up
follow-up    != clarification
clarification != reopen old run
new turn     != retry attempt
new run      != mutation of prior run
```

These identities are normative.

## 3. Legacy conversation audit — READ ONLY

Inspected:
- `backend/app/routers/conversations.py`
- `backend/app/v2/conversation.py`
- `control_plane.models.Conversation`
- `control_plane.models.ConversationMessage`
- `migrations/versions/a7c3f1e9d5b2_conversation_persist.py`
- `tests/test_conversations.py`

### Legacy router verdict

`REFERENCE_ONLY`

Useful historical capabilities:
- per-user conversation listing;
- non-enumerating ownership;
- soft delete;
- stored response history.

Not reusable as Fast runtime owner because it directly carries legacy assumptions including:
- legacy `/ask` response payload history;
- cube/viz refresh;
- `from app import cube_router, viz`;
- `wren_for_request(request).schema()`;
- legacy company/data-plane coupling.

Fast runtime MUST NOT import this router.

### V2 conversation verdict

`REFERENCE_ONLY`

Useful ideas:
- explicit pending clarification state;
- deterministic delta application;
- prior-result anchors;
- compatibility validation before follow-up.

Not reusable as Fast runtime owner because it is coupled to:
- V2 AnalyticsIR;
- SemanticResolver-era hypothesis types;
- cube metadata;
- V2 planner/result contracts.

No app.v2 import enters Fast Track.

### Legacy persistence model verdict

Existing `Conversation`:
- tenant_id;
- user_id;
- session_id;
- title;
- message_count;
- timestamps;
- soft delete.

Existing `ConversationMessage`:
- conversation_id;
- seq;
- question;
- payload_json;
- created_at.

Observed migration limitation:
- no unique `(conversation_id, seq)` constraint.

Missing native Fast authority fields:
- turn_id;
- parent_turn_id;
- reply_to_turn_id;
- run_id;
- context_source_turn_ids;
- evidence references;
- accepted context;
- explicit turn/run relation types.

Storing Fast authority only inside opaque `payload_json` is rejected.

## 4. Store strategy decision

Evaluated:

### A — adapter over existing Conversation / ConversationMessage

Pros:
- already persistent;
- existing history infrastructure.

Cons:
- legacy semantics;
- authority would drift into payload_json;
- missing native lineage constraints;
- migration-free reuse would be semantically dishonest.

Verdict:
`REJECT FOR FT-005 AUTHORITY`

### B — new Fast-owned persistent conversation tables

Pros:
- durable;
- clean schema;
- explicit constraints.

Cons:
- migration + transaction + recovery scope expands FT-005;
- persistence design would dominate the follow-up semantic proof;
- higher coupling before the contracts are experimentally stable.

Verdict:
`DEFER UNTIL CONTRACTS ARE SEALED`

### C — FastConversationStore protocol + initial in-memory implementation

Pros:
- clean Fast authority boundary;
- fastest way to prove identity/lineage/context semantics;
- no legacy imports;
- replaceable with persistent implementation later;
- mirrors the deliberate FT-004 store-boundary strategy.

Cons:
- process restart loses conversations.

Verdict:
`SELECTED`

Hard disclosure:

`CONVERSATION_DURABILITY = NOT YET CERTIFIED`

No persistent-history claim is allowed in FT-005.

## 5. Canonical ownership identity

Conversation ownership uses the same durable principle sealed post-FT-004:

```text
owner identity = tenant_id + user_id
mutable roles / is_superadmin != durable ownership identity
```

Superadmin status does not automatically expose another user's conversation.

Foreign owner/tenant:
`404`

## 6. Canonical identifiers

Opaque Fast-owned IDs:

```text
conversation_id = conv_<32 lowercase hex>
turn_id         = turn_<32 lowercase hex>
run_id          = run_<32 lowercase hex>
```

Do not encode tenant, user, Metabase IDs, resource IDs or semantic meaning in identifiers.

## 7. Canonical conversation model

```text
FastConversation
  conversation_id
  owner_key
  title?
  created_at
  updated_at
  latest_turn_id?
  active_turn_id?
  turn_count
```

Public snapshots never expose internal owner material.

## 8. Canonical turn model

```text
FastTurn
  turn_id
  conversation_id
  seq
  parent_turn_id?
  reply_to_turn_id?
  clarifies_run_id?
  user_question
  run_id
  status
  context_source_turn_ids[]
  accepted_context?
  created_at
  updated_at
```

Required invariant:
`(conversation_id, seq)` unique inside the Fast store.

A turn is immutable in identity and lineage.
Status/result linkage may advance according to the associated run.

## 9. Turn relation semantics

### parent_turn_id

Structural lineage.
Normally previous accepted conversation turn.

### reply_to_turn_id

Explicit user-selected semantic reference.

If supplied, it overrides "latest turn" as the primary context source.

### clarifies_run_id

Used only when the new turn answers a prior WAITING_CLARIFICATION run.

It does not reopen that run.

## 10. Accepted context authority

```text
FastAcceptedContext
  source_turn_ids[]
  resource_ref?
  accepted_field_refs
  exact_time_bounds?
  aggregation?
  evidence_ids[]
  query_fingerprints[]
```

Optional implementation-support metadata may include bounded display/name hints derived from accepted execution authority.

Context is NOT:
- assistant prose;
- frontend chat strings;
- hidden memory;
- raw model rationale;
- a prior request-local opaque handle.

Context IS:
`accepted prior authority + evidence references`

## 11. Prior handles are not durable authority

Request-local:
- `fast_res_###`;
- `fast_field_###`.

These MUST NOT be copied into a later turn as execution authority.

Durable context may retain:
- stable Metabase resource reference as a hint/provenance reference;
- accepted field names/refs;
- exact temporal bounds;
- executed query fingerprint;
- evidence ID.

Before every new query:
- current principal authorization is evaluated;
- current metadata/resource access is revalidated;
- new opaque handles are minted from the current candidate set;
- new evidence is produced.

## 12. Follow-up cognition contract

Introduce a Fast-owned typed follow-up cognition contract.

Suggested result:

```text
FastFollowupResolution
  status:
    SELF_CONTAINED
    CONTEXTUAL
    CLARIFICATION_REQUIRED
    UNSUPPORTED

  context_source_turn_ids[]
  inherited_slots[]
  replaced_slots[]
  effective_draft?
  clarification_reason?
```

Slots:

```text
ENTITY
AGGREGATION
MEASURE
TEMPORAL
BREAKDOWN
```

The model may decide which accepted slots are relevant.
It may not create database IDs, resource handles, field handles, SQL or answer numbers.

## 13. Effective draft rule

For CONTEXTUAL resolution the output is a full typed analytical draft equivalent in shape to the sealed FT-003 `AskDraft`.

Examples:

Turn 1:
`Son 30 günde sipariş tutarı ne kadar?`

Accepted slots:
- entity = orders-context;
- aggregation = SUM;
- measure = amount;
- temporal = last 30 days.

Turn 2:
`Peki geçen ay?`

Resolution:

```text
inherit:
  ENTITY
  AGGREGATION
  MEASURE

replace:
  TEMPORAL = PREVIOUS_MONTH
```

Turn 3:
`Bölgelere göre?`

Resolution:

```text
inherit:
  ENTITY
  AGGREGATION
  MEASURE
  TEMPORAL

add/replace:
  BREAKDOWN = region
```

## 14. Self-contained / topic-switch rule

A new self-contained topic must not accidentally inherit old context.

The follow-up cognition contract can return:
`SELF_CONTAINED`

Then:
- context_source_turn_ids = empty;
- normal current question semantics own the draft;
- prior context is not injected into execution authority.

No keyword/regex topic-switch table.

## 15. Missing usable context

If the new utterance is context-dependent but no safe accepted context exists:

`CLARIFICATION_REQUIRED`

Do not guess from:
- assistant prose;
- arbitrary chronological history;
- frontend memory;
- a failed/unverified turn.

## 16. Explicit reply to older turn

When `reply_to_turn_id` is supplied:
- verify same conversation;
- verify same owner;
- load that turn's accepted context;
- do not silently use the newest chronological turn instead;
- record that turn in `context_source_turn_ids`.

This is a required test family.

## 17. Current authorization revalidation

Prior accepted context is only cognition input / provenance.

It never replaces current access checks.

Every new analytical execution re-enters the sealed authority path:

```text
metadata discovery / resource validation
-> field validation
-> deterministic time bind
-> portable query construction
-> Metabase execution
-> new evidence
```

If a prior resource is deleted, stale or permission-lost:
fail closed / clarification / typed failure according to current Fast Ask contract.

## 18. Conversation-to-Ask composition seam

FT-005 MUST NOT duplicate FastAskService query/evidence logic.

The preferred composition is:

```text
FastConversationService
-> FastFollowupCognition
-> full typed effective AskDraft
-> context-bound FastCognition
-> existing FastAskService authority/execution
-> existing FastRunManager lifecycle
```

Because `FastRunManager` currently owns a fixed FastAskService, FT-005 may require one internal composition seam allowing a conversation-owned context-bound analytical operation to be submitted to the SAME run store/lifecycle.

Rules for that seam:
- Python-internal only;
- not user-selectable over HTTP;
- no lifecycle duplication;
- no second run store;
- no bypass around ownership/cancel/SSE;
- default `/fast/runs` behavior remains the sealed FastAskService;
- exhaustive FT-004 post-seal regressions required.

Do NOT implement a second lifecycle manager for conversations.

## 19. Clarification continuation

FT-004 WAITING_CLARIFICATION run remains immutable and is never resumed.

When the user supplies clarification:

```text
old run = WAITING_CLARIFICATION
new clarification turn arrives
-> validate same conversation/owner
-> cancel/finalize old waiting run
-> create new child turn
-> create new run
-> record clarifies_run_id
```

No silent reopen.

If old waiting run is already terminal by race:
use canonical terminal state and create the new turn only if policy still permits.

## 20. Active-run rule

Same conversation:
`at most one active analytical run`

Active conflict states:

```text
CREATED
RUNNING
PARTIAL
CANCEL_REQUESTED
```

V1 default:
`409 ACTIVE_RUN_EXISTS`

No silent parallel mutation.

Replacement requires an explicit future action such as:
`cancel/replace`

WAITING_CLARIFICATION is quiescent but unresolved.
A new turn against it must be either:
- explicit clarification continuation; or
- explicit cancel/replace/new-topic action.

## 21. Retry vs follow-up

Post-FT-004 sealed invariant:

```text
retry_of_run_id
=> exact same question + exact same as_of_date
```

Therefore:
- "Peki geçen ay?" is not retry;
- "Bölgelere göre?" is not retry;
- clarification answer is not retry.

They create new turns and new runs.

## 22. Turn success/evidence rule

Every successful analytical turn must have:
- its own run_id;
- its own FastAskResponse;
- its own evidence_id;
- its own query_fingerprint;
- its own result_digest.

Old evidence may inform context.
Old evidence is never relabeled as the new turn's evidence.

## 23. Store protocol

Initial protocol should support:

```text
create_conversation(owner)
get_conversation(conversation_id, owner)
list_turns(conversation_id, owner)
get_turn(turn_id, owner)
append_turn(...)
bind_run(turn_id, run_id)
update_turn_from_run(...)
latest_accepted_context(...)
context_for_reply(turn_id,...)
assert_no_active_run(...)
```

In-memory implementation:
- thread-safe;
- monotonic seq;
- unique seq;
- non-enumerating owner denial;
- deterministic ordering.

## 24. HTTP shape — initial proposal

Do not expose internal accepted context as user-editable authority.

### POST /fast/conversations

Create conversation.

### GET /fast/conversations/{conversation_id}

Conversation + bounded turn snapshots.

### POST /fast/conversations/{conversation_id}/turns

Request:

```text
question
as_of_date?
reply_to_turn_id?
clarifies_run_id?
```

Response:
- HTTP 202;
- new turn snapshot including new run_id.

### GET /fast/conversations/{conversation_id}/turns/{turn_id}

Canonical turn snapshot.

Run events remain on:
`GET /fast/runs/{run_id}/events`

Do not duplicate SSE in conversation router.

## 25. Provider-free test matrix

1. first turn creates conversation;
2. second turn stays in same conversation;
3. "Peki geçen ay?" inherits entity/aggregation/measure and replaces temporal;
4. "Bölgelere göre?" inherits prior accepted context and adds breakdown;
5. explicit reply to older turn uses that turn, not newest turn;
6. self-contained topic switch inherits old context = 0;
7. missing safe context -> clarification;
8. stale/deleted/permission-lost prior resource -> current revalidation fails closed;
9. foreign user conversation -> 404;
10. foreign tenant -> 404;
11. mutable superadmin/role change does not alter same-owner identity;
12. active-run conflict -> 409;
13. clarification continuation -> old waiting run finalized + new turn + new run;
14. old waiting run never reopens;
15. retry != follow-up;
16. every successful turn has distinct run/evidence;
17. assistant prose is never context authority;
18. request-local opaque handles are never persisted as later authority;
19. `(conversation_id, seq)` uniqueness;
20. explicit context source turn IDs recorded.

## 26. Focused real-model sentinel

Small corpus only, approximately 6–10 prompts.

Required families:
- prior SUM -> "Peki geçen ay?";
- prior SUM previous month -> "Bölgelere göre?";
- explicit older-turn reply;
- self-contained topic switch;
- context-dependent utterance without usable context;
- ambiguous follow-up -> clarification;
- unsupported operation remains unsupported.

Measure:
- typed resolution;
- inherited/replaced slots;
- no invented IDs/handles;
- no assistant prose authority.

Broad benchmark is NOT FT-005.

## 27. Real pinned-Metabase follow-up sentinel

Required sequence:

```text
Turn 1
Son 30 günde sipariş tutarı ne kadar?
-> new run
-> real Metabase
-> evidence A

Turn 2
Peki geçen ay?
-> typed context from Turn 1
-> current metadata/permission revalidation
-> new run
-> real Metabase
-> evidence B

Turn 3
Bölgelere göre?
-> typed context from Turn 2
-> revalidation
-> new run
-> real Metabase
-> evidence C
```

Assert:
- three distinct run IDs;
- three distinct evidence IDs;
- no terminal run reopened;
- current DB oracle equality for each supported synthetic-lab query;
- context lineage exact.

## 28. Scope exclusions

Do NOT add in FT-005:
- Analyst loop;
- Research;
- Root Cause;
- recommendations;
- decisions;
- reports;
- AVG/MIN/MAX;
- joins;
- arbitrary filters;
- multi-table semantics;
- semantic graph;
- vector conversation memory;
- long-term memory;
- dashboard;
- main frontend migration.

FT-005 is only:

```text
CONVERSATION IDENTITY
TURN LINEAGE
SAFE FOLLOW-UP CONTEXT
```

## 29. Hard GREEN gate

- [ ] Fast conversation/turn/context typed models;
- [ ] FastConversationStore protocol;
- [ ] in-memory store;
- [ ] CONVERSATION_DURABILITY explicitly NOT CERTIFIED;
- [ ] owner isolation;
- [ ] seq uniqueness;
- [ ] turn lineage;
- [ ] explicit older-turn reply;
- [ ] typed accepted context;
- [ ] bounded follow-up cognition;
- [ ] self-contained topic switch non-inheritance;
- [ ] missing context clarification;
- [ ] current resource/field permission revalidation;
- [ ] new run per analytical turn;
- [ ] active-run conflict rule;
- [ ] clarification continuation creates new run;
- [ ] old waiting run not reopened;
- [ ] retry/follow-up separation;
- [ ] assistant prose authority = 0;
- [ ] request-local handle persistence = 0;
- [ ] provider-free tests;
- [ ] real-model focused sentinel;
- [ ] real pinned-Metabase follow-up sentinel;
- [ ] FT-003 regression;
- [ ] FT-004 regression;
- [ ] final receipt sealed.

## 30. Known debt after FT-005

```text
CONVERSATION_DURABILITY = NOT YET CERTIFIED
PERSISTENT_CONVERSATION_STORE = NOT YET IMPLEMENTED
PROCESS_RESTART_CONVERSATION_HISTORY = NOT CERTIFIED
DISTRIBUTED_CONVERSATION_COORDINATION = NOT IMPLEMENTED
```

Before external pilot, persistent conversation/turn storage must be designed and migrated.

## 31. Exit

When FT-005 is GREEN:

`FT-006 — Evidence expansion`

Do not jump to Analyst before FT-006.
