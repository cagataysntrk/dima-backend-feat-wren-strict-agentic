# FT-004 FAILURE RECEIPT — POST_SEAL_RETRY_IDENTITY_001

Status: CLOSED / STRICT_RETRY_IDENTITY
Date: 2026-09-22

OBSERVED_RUN:
`35781293132`

OBSERVED_SHA:
`4849fd9480142e95330a9fc87ffdcd656303090b`

FAILURE_CLASS:
`RETRY_PROVENANCE_IDENTITY`

## Focused cases

Source run:
- terminal FAILED;
- question = original analytical request;
- as_of_date = 2026-09-07.

Observed:
1. different question + retry_of_run_id -> accepted;
2. same question but as_of_date 2026-09-08 + retry_of_run_id -> accepted.

Expected:
both rejected.

## Root cause

`FastRunStore.retry_lineage()` validates:
- owner;
- terminal retryable state;

but does not validate that the new analytical request equals the immutable source request.

Therefore `retry_of_run_id` can currently describe a different analytical request.

## Normative contract

```text
retry = same immutable analytical request
follow-up = new turn / new analytical request
```

FT-004 strict retry identity:
- question must match;
- as_of_date must match.

## Authorized patch

Fast run store/manager lineage owner only:
- validate new request against source run request before allocating the retry run;
- reject mismatch with FastRunTransitionError;
- preserve same-request retry;
- preserve original terminal immutability/root lineage/attempt increment.

HTTP mapping remains typed 409 through existing run router behavior.

## Forbidden

- silently rewriting retry request;
- treating follow-up as retry;
- reopening terminal run;
- FT-005 semantics inside FT-004;
- fuzzy question comparison.


## Closure

Store validation commit:
`6951f62419962209d91c84d186e4eb312dbc2212`

Manager wiring commit:
`f8018800c773019f0e79907fec3e15edec72dbb0`

Final focused/core proof:
`35781659952 GREEN`

Verified:
- same immutable question + as_of_date retry remains allowed;
- different question retry rejected;
- different as_of_date retry rejected;
- original terminal run remains immutable;
- root lineage and attempt increment remain intact;
- HTTP path retains typed 409 mapping through existing router contract.

Failure CLOSED.
