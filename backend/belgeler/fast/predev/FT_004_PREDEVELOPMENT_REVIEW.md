# FT-004 — RUN LIFECYCLE / STREAMING / CANCEL PRE-DEVELOPMENT REVIEW

Status: APPROVED
Branch: `feat/dima-metabase-product-fast-track`
FT-003 seal commit: `2261cb430863efc8edf39068f66b057c059d2fd5`
Date: 2026-09-22

## 1. Goal

Wrap the sealed FT-003 Ask vertical in a Dima-owned asynchronous run lifecycle.

Target:

```text
POST /fast/runs
-> run_id

GET /fast/runs/{run_id}
-> canonical run snapshot

GET /fast/runs/{run_id}/events
-> SSE event stream

POST /fast/runs/{run_id}/cancel
-> cooperative cancellation request
```

Existing:

`POST /fast/ask`

remains a compatibility/simple Quick adapter.

FT-004 MUST NOT rewrite or fork the sealed FT-003 cognition/query/evidence pipeline.

## 2. Non-goals

Do NOT add:
- new semantic logic;
- new retrieval semantics;
- new aggregation kinds;
- AVG/MIN/MAX;
- joins;
- arbitrary filters;
- multi-table execution;
- conversation/follow-up semantics;
- Analyst;
- Research;
- Root Cause;
- decision/report features;
- main frontend migration.

## 3. Ownership boundary

```text
FastAskService
= sealed analytical operation

FastRunManager
= lifecycle/orchestration owner

FastRunStore
= canonical run/event state owner

FastRunRouter
= HTTP/SSE surface
```

Metabase remains query/execution substrate.

The model never owns run state.

## 4. Canonical states

```text
CREATED
RUNNING
WAITING_CLARIFICATION
PARTIAL
COMPLETED
FAILED
CANCEL_REQUESTED
CANCELLED
INTERRUPTED
```

Terminal states:

```text
COMPLETED
FAILED
CANCELLED
INTERRUPTED
```

Stable non-terminal/quiescent state:

`WAITING_CLARIFICATION`

FT-004 does not yet implement clarification continuation. A run may stop work and remain WAITING_CLARIFICATION; later conversation work owns resume semantics.

## 5. Allowed state transitions

```text
CREATED -> RUNNING
CREATED -> CANCEL_REQUESTED
CREATED -> CANCELLED
CREATED -> INTERRUPTED

RUNNING -> PARTIAL
RUNNING -> WAITING_CLARIFICATION
RUNNING -> COMPLETED
RUNNING -> FAILED
RUNNING -> CANCEL_REQUESTED
RUNNING -> INTERRUPTED

PARTIAL -> RUNNING
PARTIAL -> WAITING_CLARIFICATION
PARTIAL -> COMPLETED
PARTIAL -> FAILED
PARTIAL -> CANCEL_REQUESTED
PARTIAL -> INTERRUPTED

WAITING_CLARIFICATION -> CANCEL_REQUESTED
WAITING_CLARIFICATION -> CANCELLED
WAITING_CLARIFICATION -> INTERRUPTED

CANCEL_REQUESTED -> CANCELLED
CANCEL_REQUESTED -> INTERRUPTED
```

No transition leaves a terminal state.

No second terminal event may be emitted.

## 6. FT-003 response mapping

When FastAskService returns:

```text
SUCCESS
-> COMPLETED

UNSUPPORTED
-> COMPLETED
   handled typed product outcome

CLARIFICATION_REQUIRED
-> WAITING_CLARIFICATION

FAILED
-> FAILED
```

This distinguishes:
- analytical/product outcome;
- run transport/lifecycle failure.

The full FastAskResponse is retained in the run snapshot for canonical retrieval.

## 7. Cancellation semantics

FT-004 cancellation is cooperative.

The current FT-003 Ask path contains blocking Metabase calls and has no internal cancellation token.

Therefore:

1. cancel before worker starts:
   - emit CANCEL_REQUESTED;
   - do not call FastAskService;
   - emit CANCELLED.

2. cancel while FastAskService is running:
   - emit CANCEL_REQUESTED immediately;
   - allow the already-started bounded call to return;
   - discard any later success result as run authority;
   - emit CANCELLED exactly once.

3. cancel after terminal:
   - no new event;
   - return existing terminal snapshot.

Do NOT mutate FT-003 query code merely to simulate hard interruption.

True transport-level query abort is a later capability unless Metabase exposes a bounded supported mechanism.

## 8. Run identity

Opaque IDs:

`run_<32 lowercase hex>`

Event IDs are monotonically increasing integers within a run.

No database/query/resource IDs are encoded in run IDs.

## 9. Principal ownership

Every run stores a Fast-owned owner key derived from the authenticated Dima principal.

At minimum:
- Dima user ID;
- tenant ID;
- superadmin status only as identity context, not implicit cross-run authority.

FT-004 initial rule:
the creating principal owns the run.

GET/events/cancel from a different principal:
`404` or equivalent non-enumerating denial.

Do not expose whether a foreign run exists.

## 10. Canonical run snapshot

Required fields:

```text
run_id
state
question
as_of_date
created_at
updated_at
owner_key (internal/not browser authority)
response
error
last_event_id
terminal_event_id
retry_of_run_id
root_run_id
attempt
```

Public response excludes internal owner material.

## 11. Structured event contract

Each event:

```text
event_id
run_id
type
state
occurred_at
payload
dedupe_key
```

Initial event types:

```text
RUN_CREATED
RUN_STARTED
RUN_PARTIAL
RUN_WAITING_CLARIFICATION
RUN_COMPLETED
RUN_FAILED
CANCEL_REQUESTED
RUN_CANCELLED
RUN_INTERRUPTED
```

Payloads are bounded typed JSON.

Do not stream chain-of-thought.

Events may expose:
- state;
- safe status text;
- final FastAskResponse;
- typed error;
- evidence IDs/fingerprints already safe for the product.

## 12. Duplicate-event handling

Store owns a request-local/run-local dedupe index by `dedupe_key`.

If the same logical event is emitted twice:
- return the existing event;
- do not append a duplicate;
- do not increment sequence.

Terminal transition additionally has a hard exactly-once guard independent of dedupe key.

## 13. SSE

Endpoint:

`GET /fast/runs/{run_id}/events`

Response:
`text/event-stream`

Format:

```text
id: <event_id>
event: <event_type>
data: <compact JSON>

```

Reconnect:
- accept standard `Last-Event-ID`;
- optional `after_event_id` query parameter may be used by tests/clients;
- stream only events with `event_id > cursor`.

The stream closes when:
- run is terminal; or
- run is in WAITING_CLARIFICATION and all current events have been delivered.

Clients may reconnect safely without duplicate event delivery.

## 14. Storage strategy for FT-004

Use a Fast-owned in-process store with a clear protocol boundary.

Reason:
- FT-004 is proving lifecycle semantics, not production durability;
- adding schema migration/persistent queue now would broaden scope;
- the API/store interface must allow later persistent replacement.

Hard limitation to document:
`PROCESS_RESTART_DURABILITY = NOT YET CERTIFIED`

`INTERRUPTED` is still modeled and tested through explicit stale-run recovery logic.

Before external pilot, a persistent store/job execution design is mandatory.

## 15. Worker strategy

Use a bounded `ThreadPoolExecutor`.

Default:
`max_workers = 4`

No unbounded thread/task creation.

The worker receives:
- immutable FastAskRequest;
- captured authenticated principal;
- run_id.

Before calling Ask:
- re-check cancel state.

After Ask returns:
- re-check cancel state before accepting result.

## 16. Recovery / interrupted semantics

Store/manager exposes deterministic recovery:

`interrupt_nonterminal_runs()`

For:
- CREATED;
- RUNNING;
- PARTIAL;
- CANCEL_REQUESTED;
- WAITING_CLARIFICATION where desired by explicit shutdown/recovery policy;

emit `RUN_INTERRUPTED` exactly once.

For the initial in-memory runtime this is exercised in provider-free tests.

No claim of process-restart persistence is made.

## 17. Retry / lineage

No automatic retry of cognition/query inside FT-004.

A new run may declare:
`retry_of_run_id`

Manager validates:
- referenced run exists;
- same owner;
- source run is terminal FAILED / INTERRUPTED / CANCELLED, or explicitly retryable by contract.

New run receives:
- new run_id;
- `retry_of_run_id`;
- `root_run_id`;
- `attempt = prior attempt + 1`.

Do not mutate/reopen a terminal run.

## 18. HTTP contracts

### POST /fast/runs

Request:
- `question`;
- optional `as_of_date`;
- optional `retry_of_run_id`.

Response:
- HTTP 202;
- public run snapshot.

### GET /fast/runs/{run_id}

Response:
- HTTP 200 canonical snapshot;
- 404 for absent/foreign run.

### GET /fast/runs/{run_id}/events

Response:
- SSE;
- replay after cursor;
- then live wait until terminal/quiescent.

### POST /fast/runs/{run_id}/cancel

Response:
- HTTP 200 current snapshot.

Idempotent after terminal.

## 19. /fast/ask compatibility

Keep existing endpoint behavior unchanged.

Do not implement `/fast/ask` by recursively HTTP-calling `/fast/runs`.

Both surfaces call the same sealed FastAskService owner.

No duplicated cognition/query/evidence implementation.

## 20. Proposed files

Fast-owned:

```text
backend/app/fast/
├── run_models.py
├── run_store.py
├── run_manager.py
└── run_router.py
```

Minimal integration:
- `app.fast.application` mounts run router/manager;
- existing `app.fast.router` may remain Ask owner.

Tests:
- `backend/tests/test_fast_run_lifecycle.py`
- `backend/tests/test_fast_run_api.py`

Workflow:
- `.github/workflows/dima-fast-ft004-core.yml`

No Wren/V2/V3 edits.

## 21. Provider-free test matrix

State machine:
- CREATED -> RUNNING -> COMPLETED;
- SUCCESS maps COMPLETED;
- UNSUPPORTED maps COMPLETED;
- CLARIFICATION maps WAITING_CLARIFICATION;
- FAILED maps FAILED;
- invalid transition rejected;
- terminal cannot transition;
- terminal event exactly once.

Cancel:
- cancel before execution -> no Ask call;
- cancel while worker blocked -> CANCEL_REQUESTED then CANCELLED;
- late result cannot overwrite CANCELLED;
- cancel terminal is idempotent;
- cancel race terminal exactly once.

Events:
- monotonic IDs;
- duplicate dedupe key -> one event;
- ordered replay;
- cursor replay excludes already-seen events;
- no chain-of-thought field;
- final response event bounded.

SSE:
- correct content type;
- id/event/data framing;
- Last-Event-ID replay;
- terminal stream closes;
- WAITING_CLARIFICATION stream closes after current events.

Authorization:
- unauthenticated create/get/events/cancel -> 401;
- foreign principal -> 404;
- owner -> allowed.

Lineage:
- retry creates new run ID;
- original terminal stays immutable;
- root_run_id preserved;
- attempt increments;
- foreign retry source denied.

Recovery:
- nonterminal -> INTERRUPTED;
- terminal untouched;
- interrupted event exactly once.

## 22. Live sentinel

Use scripted cognition + real pinned Metabase.

Prove:
```text
POST /fast/runs
-> CREATED/RUNNING
-> real FastAskService
-> real Metabase
-> COMPLETED
-> canonical final FastAskResponse
```

Then SSE replay:
- RUN_CREATED;
- RUN_STARTED;
- RUN_COMPLETED.

Also prove:
- clarification -> WAITING_CLARIFICATION;
- cancel path;
- no Wren/V2/V3.

No real-model dependency is needed for FT-004 lifecycle correctness because real-model analytical correctness is sealed by FT-003.

## 23. Browser scope

FT-004 browser work is minimal.

Do NOT redesign Fast POC.

A focused future proof may show:
- run started;
- streamed status;
- cancel;
- final result.

Backend lifecycle gate comes first.

## 24. Hard GREEN gate

- [ ] run models
- [ ] FastRunStore
- [ ] FastRunManager
- [ ] bounded worker pool
- [ ] owner authorization
- [ ] state-transition table
- [ ] terminal exactly once
- [ ] event monotonicity
- [ ] event dedupe
- [ ] POST /fast/runs
- [ ] GET /fast/runs/{id}
- [ ] SSE /events
- [ ] Last-Event-ID reconnect
- [ ] POST /cancel
- [ ] cooperative cancellation race
- [ ] WAITING_CLARIFICATION mapping
- [ ] FAILED mapping
- [ ] retry lineage
- [ ] INTERRUPTED recovery
- [ ] provider-free tests
- [ ] live pinned-Metabase run
- [ ] Wren/V2/V3 dependency = 0
- [ ] raw SQL = 0
- [ ] FT-003 regressions remain GREEN
- [ ] receipt sealed

## 25. Known debt after FT-004

Not certified here:
- persistent run/event store;
- process-restart durable recovery;
- distributed workers;
- cross-instance SSE fanout;
- hard cancellation of an already-running Metabase query;
- conversation continuation;
- partial analytical findings semantics.

These must remain explicit.

## 26. Exit

When FT-004 GREEN:

`FT-005 — conversation + follow-up context`

Do not start FT-005 before FT-004 seal.
