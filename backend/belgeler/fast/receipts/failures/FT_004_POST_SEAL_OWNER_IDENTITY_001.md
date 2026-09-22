# FT-004 FAILURE RECEIPT — POST_SEAL_OWNER_IDENTITY_001

Status: CLOSED / DURABLE_OWNER_IDENTITY
Date: 2026-09-22

OBSERVED_RUN:
`35781293132`

OBSERVED_SHA:
`4849fd9480142e95330a9fc87ffdcd656303090b`

FAILURE_CLASS:
`DURABLE_OWNER_IDENTITY`

## Focused setup

Same durable identity:

```text
user_id   = stable-user
tenant_id = tenant-a
```

Only current authorization claim changed:

```text
is_superadmin: false -> true
```

## Observed

The same user received:

`FastRunNotFound`

for their own run.

## Root cause

`FastRunOwner` equality currently includes:

`is_superadmin`

This mixes mutable/current authorization state with durable object ownership identity.

## Normative contract

```text
RUN OWNERSHIP IDENTITY = tenant_id + user_id
CURRENT PRIVILEGES     = authorization context

is_superadmin/roles != durable run identity
```

Superadmin status must not grant access to a different user's run.
A same-user claim change must not orphan that user's own run.

## Authorized patch

Owner:
`backend/app/fast/run_store.py`

Remove mutable superadmin state from the FastRunOwner identity key.
Keep current principal authorization behavior outside ownership identity.

## Forbidden

- superadmin global run bypass;
- foreign-user access;
- tenant bypass;
- changing run IDs;
- FT-003 changes.


## Closure

Corrective owner commit:
`6951f62419962209d91c84d186e4eb312dbc2212`

Final focused/core proof:
`35781659952 GREEN`

Tested SHA:
`f8018800c773019f0e79907fec3e15edec72dbb0`

Final invariant:

```text
FastRunOwner = tenant_id + user_id
mutable is_superadmin claim != ownership identity
```

Foreign user/owner isolation remains fail-closed.

Failure CLOSED.
