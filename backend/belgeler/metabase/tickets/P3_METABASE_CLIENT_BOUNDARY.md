# P3-001 — METABASE REST/AGENT API CLIENT BOUNDARY

**Milestone:** P3  
**Predevelopment review:** `backend/belgeler/metabase/predev/P3_P3A_PREDEVELOPMENT_REVIEW.md`  
**Owner:** Metabase transport/runtime boundary  
**Status:** CLOSED GREEN

## Goal

Create a typed, version-aware REST/Agent API client boundary against the pinned v0.63.18 runtime,
without introducing semantic compilation or product routing.

## Required surface

```text
health
agent ping
search
read_resource
construct_query
execute serialized query
combined query
continuation
startup/capability handshake
typed telemetry
```

## Explicitly absent

```text
raw SQL
admin mutation
dashboard write
question/metric/model mutation
semantic mutation
semantic handle resolution
raw user prompt/question
```

## Error taxonomy

```text
METABASE_TRANSPORT
METABASE_AUTH
METABASE_PERMISSION
METABASE_QUERY_INVALID
METABASE_RESOURCE_NOT_FOUND
METABASE_TIMEOUT
METABASE_INTERNAL
```

## Proof

Provider-free:
- HTTP status/error mapping;
- serialized-query vs continuation type separation;
- no forbidden method/import surface;
- handshake refuses healthy-but-Agent-disabled state.

Live pinned runtime:
- P2 lab startup/bootstrap;
- client handshake;
- search/read-resource;
- construct;
- execute;
- combined query + continuation;
- observed page cap;
- no raw-SQL client method.

No Dima front-door routing.

## Exit

P3 GREEN is required before P3A implementation.


---

## RED receipt linkage

`DMP-P3-RED-001` is open against live run `35734065244`.

Do not advance to P3A. The correction owner is limited to the exact read-resource transport
envelope + capability handshake. M2 remains GREEN.


---

## Closure receipt

```text
implementation SHA             7a4d1d12e59b52edf8493c0aa0b147947ff4ecf9
P3 workflow                    35736253380 = SUCCESS
governance                     35736253664 = SUCCESS
provider-free                  16 passed
pinned live                    1 passed
M1 regression                  15 + 5 passed
DMP-P3-RED-001                 CLOSED GREEN
```

P3 transport is certified only as a runtime/transport boundary. Principal mapping, tenant security
parity and final ExecutionAccessFingerprint remain open architecture debt.
