# P10B1 — PRE-DEVELOPMENT REVIEW

**Milestone:** P10B1 — Isolated OSS authenticated-user and basic permission revocation proof  
**Branch:** `feat/dima-metabase-platform`  
**P10A:** `1abf43657453a771954a939de834e6b48f55620e` — GREEN  
**P10A workflow:** `35783766213 = SUCCESS`  
**DMP-DEC-0025:** SEALED

Status: **SEALED / ONE ISOLATED P10B1 BASIC SECURITY CANARY AUTHORIZED / P10B2 NOT AUTHORIZED**

## Goal

Prove with the real pinned Metabase permission engine that:
1. a session maps to one exact authenticated Metabase user;
2. a non-admin user can execute one certified structured query while permitted;
3. revoking basic query permission takes effect for the same existing session and the same serialized
   query;
4. denial does not fall back to admin/service identity;
5. restoring permission restores execution;
6. permission revision/current-user evidence can feed P10A attestation without treating session token
   as identity.

## Pinned-source boundary

v0.63.18 provides:
- `GET /api/user/current`;
- admin `GET/PUT /api/permissions/graph`;
- basic `create-queries` permissions;
- query run permission checks in Agent execution.

Current OSS lab does not prove:
- sandboxes / row security;
- advanced blocked access;
- connection impersonation;
- complete CLS;
- permission-sensitive cached-result hydration across incompatible lenses.

Those remain P10B2.

## Canary

Use the existing isolated lab:
- admin session only as permission-control-plane actor;
- restricted user session as the data-plane execution actor;
- exact current-user read on restricted session;
- exact existing fixture database;
- one existing P4 certified query;
- save original permission graph;
- set `create-queries=no` for every real group that currently grants the restricted user query
  creation on the fixture DB;
- reuse the same restricted session and same serialized query;
- require typed Metabase permission denial;
- verify `GET /api/user/current` still returns the same restricted subject;
- restore exact original permission graph using the current revision;
- require the same restricted session/query to execute again.

No search/name adoption for semantic resources. Lab fixture names may identify the explicit lab group
and lab database only; they are not production bindings.

## Permission graph safety

The test must:
- snapshot the full original graph;
- update using the graph revision contract;
- restore in `finally`;
- never alter production/customer state;
- teardown the whole lab even on failure.

## P10A bridge

After restored permission:
- calculate test-only deterministic policy/security evidence from the exact current-user identity and
  permission graph revision/relevant group-db entries;
- set `metabase_subject_ref = metabase:user:<numeric id>`;
- issue one P5 ExecutionAccessSnapshot through the production P10A issuer;
- assert the Metabase subject evidence is present in snapshot attestation refs.

This proves the issuer can consume real external evidence. It does not claim the lab facts are a
production policy issuer.

## Expected classifications

Unknown HTTP/error shape = RED.

Expected revocation outcome:
`MetabaseClientError.code == METABASE_PERMISSION`.

If OSS group coalescing prevents denial, classify the exact permission-model gap; do not add a
special case or switch execution to admin.

## P10B2 gap

DMP-P10-AUDIT-001 remains open:
row/column/impersonation/database-route lens proof requires a capable real owner.

## Forbidden

```text
admin execution fallback
new session after revocation to make test pass
raw SQL
permission name heuristic
fake RLS/CLS version
sandbox mock
session token as subject id
search/list semantic adoption
production route/write
broad security matrix
```

## Authorized files

```text
backend/tests/test_v3_p10b_basic_security_live.py
.github/workflows/dima-metabase-p10.yml
backend/belgeler/metabase/predev/P10B1_PREDEVELOPMENT_REVIEW.md
backend/belgeler/metabase/tickets/P10_TENANT_PRINCIPAL_SECURITY_MAPPING.md
backend/belgeler/metabase/*RECEIPTS*.md
DIMA-METABASE-DURUM.md
```

No product security/Metabase/auth code change is authorized in P10B1.

## Exit

P10B1 GREEN requires one isolated canary proving allow -> same-session revoke denial -> restore allow,
stable authenticated subject, no fallback, and P10A issuance from real lab evidence.

It does not close P10 or DMP-P5-BLOCK-001.
