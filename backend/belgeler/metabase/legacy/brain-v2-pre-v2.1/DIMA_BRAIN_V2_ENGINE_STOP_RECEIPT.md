# DIMA BRAIN V2 — ENGINE OWNER STOP RECEIPT

**Status:** ARCHITECTURAL STOP — ENGINE OWNER REVIEW REQUIRED  
**Branch:** `feat/dima-brain-v2`  
**Platform HEAD entering stop:** `d172b05eb453ea0d53803b7b68a0d433952c1d89`  
**Semantic Product:** `0ed82ef7341fae9ef00057a4f0fa8d0fadf45de6`  
**Provider-free authority:** `36795446842 = SUCCESS`  
**Engine:** `0f16f2b5a1ec774ac7afee6214c726e82f9ceb3c / 0.63.18-dima.8`  
**Engine digest:** `sha256:b1130357b9046d1208880c196ca0b5f3afba56580fca91fadede89a464521577`  
**Engine builds during Brain V2:** `0`

## Why this is a genuine stop

The current failure is not a Dima semantic, LangGraph, Evidence, P19, prompt, provider-limit,
or benchmark-specific defect. It is a lifecycle incompatibility inside the frozen native Metabot
acquisition boundary.

The relevant native path is:

```text
one accepted analytical obligation
-> one Metabot native acquisition
-> successful construct_notebook_query
-> exact native query id
-> persisted successful producer occurrence
-> native material observation
```

The frozen engine currently cannot complete that path without either:

1. opening one unnecessary post-query LLM iteration, or
2. treating the client disconnect used to prevent that iteration as an aborted assistant turn.

Both outcomes break a required invariant.

## Exact live reproducer A — full stream

Run:

```text
36794892540
candidate = dcf6aa70016d57e17440f6a9ce1f15965f0c6637
```

Observed engine sequence:

```text
iterations 1..6
-> discovery/read_resource cognition

iteration 7
-> construct_notebook_query succeeds
-> exact query artifact exists

iteration 8
-> Metabot calls Luna again
-> local provider ceiling rejects the unnecessary request with HTTP 429
-> native stream emits an error
-> Dima fails closed with P14_NATIVE_TRANSPORT_FAILED
```

The provider ceiling is not the defect. The 8th call has no analytical information value after the
exact executable query is already produced.

Increasing the provider ceiling is forbidden and would only hide the lifecycle defect.

## Exact live reproducer B — client stops at generated query

Generic Dima-side repair candidate:

```text
195ebec9  test(native): reproduce post-query agent overrun
0ed82ef7  fix(native): stop material stream at exact generated query
8d4c1622  ci: include native stream boundary regression
36795446842  full provider-free SUCCESS
```

Fresh live:

```text
36808793721
candidate = 0ed82ef7341fae9ef00057a4f0fa8d0fadf45de6
```

Result:

```text
Metabot query artifact captured
-> Dima closes streaming response
-> exact query is executed
-> native material observation by
   conversation_id + native_query_id

HTTP 404
NATIVE_QUERY_OCCURRENCE_NOT_FOUND

"No persisted producer occurrence matches the requested native query id"
```

This proves that early client termination cannot be the durable fix.

## Frozen dima.8 source proof

Exact engine SHA:

```text
0f16f2b5a1ec774ac7afee6214c726e82f9ceb3c
```

Relevant engine facts:

### 1. Agent core already supports successful terminal tools

`src/metabase/metabot/agent/core.clj`:

```text
terminal-tool-call?
should-continue?
finish-reason
```

A successful tool listed in a profile's `terminal-tools` stops the loop normally.

### 2. NLQ exposes construct_notebook_query but does not make it terminal

`src/metabase/metabot/agent/profiles.clj`:

```text
:name :nlq
...
:tools [
  ...
  construct-notebook-query-tool
  ...
]

terminal-tools = absent
```

The `:nlq-fallback` profile also exposes the same query-construction tool, while an external
`:nlq` request keeps the `:nlq` profile identity during fallback selection.

### 3. Client disconnect is intentionally persisted as aborted

`src/metabase/metabot/api.clj` documents and implements:

```text
client disconnect
-> pipeline reduced
-> assistant turn finalized
-> finished? = false
```

### 4. Dima exact-occurrence authority requires a finalized successful producer

`src/metabase/dima/native_occurrence.clj` requires:

```text
producer tool = construct_notebook_query
AND
assistant message finished = true
AND
producer query exists
AND
conversation state contains same query
```

Therefore Dima cannot legally manufacture or infer a durable occurrence after an aborted stream.

## Earliest wrong transition

```text
NATIVE ANALYTICS / METABOT AGENT-LIFECYCLE OWNERSHIP

successful exact query creation
-> SHOULD terminate native analytical cognition
-> SHOULD finalize assistant turn successfully
-> SHOULD persist query occurrence
```

Current dima.8 instead performs:

```text
successful exact query creation
-> another LLM iteration
```

This is upstream of Dima Evidence admission and P19.

## Rejected workarounds

Do NOT:

```text
raise provider ceiling
ignore blocked provider requests
retry until lucky
prompt the model to "stop after query"
regex/fuzzy/morph route the case
fabricate an occurrence in Dima
read/write Metabase app DB from Dima as a substitute authority
reconstruct material semantics in Python
weaken finished=true occurrence authority
ignore NATIVE_QUERY_OCCURRENCE_NOT_FOUND
reopen LangGraph
patch P19
```

## Minimal owner-correct repair for review

The engine already has the required primitive. The narrow owner-correct change is to make a
successful `construct_notebook_query` terminal for the `:nlq` profile.

Conceptually:

```clojure
(register-profile!
 {:name :nlq
  ...
  :terminal-tools #{"construct_notebook_query"}
  :tools [...]})
```

Because the `:nlq` fallback resolution retains the `:nlq` profile while swapping its tools and
prompt, the terminality rule remains attached to the external NLQ profile.

This is not a new agent architecture. It uses the engine's existing terminal-tool mechanism.

## Required engine-owner proof if approved

Before any new Brain V2 paid run:

```text
1. engine provider-free:
   successful construct_notebook_query is terminal in NLQ
2. failed construct_notebook_query remains retryable
3. persisted assistant turn is finished=true
4. persisted producer query and conversation-state query agree
5. native material observation resolves exact occurrence
6. no post-query LLM request occurs
7. no raw SQL / Agent API / fallback path opens
8. certify one immutable engine build
9. update runtime lock only after certification
10. run full affected Brain V2 provider-free closure
11. run ONE surgical ONE_PASS live
```

## Stop law

The continuation directive permits engine reconsideration only after one analytical obligation,
one native acquisition, and no duplicate orchestration have isolated a broken native acquisition.
Those conditions are now satisfied.

No engine modification or build is made in this receipt. The frozen dima.8 identity remains intact.

## Current product status

```text
Phase 1              STOPPED at engine owner review
ONE_PASS acceptance  NOT SEALED
ADAPTIVE live         NOT RUN after this stop
DISCOVERY live        NOT RUN after this stop
scope-resume live     NOT RUN after this stop
Phase 2 backend       NOT STARTED under exit gate
80+ readiness         NO
90+ readiness         NO
30-CASE READY         NO
30-case               NOT RUN
frontend              NOT IMPLEMENTED
```
