# FT-002B — FAST-OWNED METABASE GATEWAY PRE-DEVELOPMENT REVIEW

Status: APPROVED
Prerequisite: F0A GREEN
F0A run: 35761155049
F0A tested commit: c8175ea2a05be79eeae7c61d8fb568c36fbe3773

## Goal

Create a Fast Track-owned typed Metabase transport boundary.

This is transport/infrastructure only.

It MUST NOT interpret raw user language, choose business meaning, build Dima semantics, author SQL, or call Wren/V2/V3.

## Architecture

```text
future Fast orchestrator
  -> FastMetabaseGateway
      -> Metabase Agent API
          -> customer analytics DB
```

Gateway owns:
- auth header injection
- timeouts
- typed upstream errors
- safe telemetry
- search
- read-resource
- construct query
- execute
- combined query
- continuation
- pinned runtime handshake

Gateway does NOT own:
- semantic resource selection
- temporal intent
- root cause
- conversation
- report/decision
- asset mutation in this ticket
- password login
- tenant mapping policy

## Files to touch

New:
- backend/app/fast/metabase_errors.py
- backend/app/fast/metabase_models.py
- backend/app/fast/metabase_telemetry.py
- backend/app/fast/metabase_gateway.py
- backend/app/fast/auth_context.py
- backend/tests/test_fast_metabase_gateway.py
- backend/tests/test_fast_metabase_gateway_live.py
- .github/workflows/dima-fast-ft002-gateway.yml
- Fast receipts/status docs

## Files not to touch

- backend/app/v3/substrate/metabase/**
- backend/app/v2/**
- WrenAI-main/**
- legacy routers
- backend/app/main.py
- backend/app/config.py
- source branches

## Port policy

The P3 Metabase client was inspected as READ-ONLY reference.

Fast code may reuse transport ideas, but:
- no `app.fast -> app.v3` import
- Fast error taxonomy follows Fast roadmap
- Fast auth/access provenance is explicit
- Fast code gets its own tests and live proof

## Required models

At minimum:
- FastMetabaseRuntimePolicy
- FastMetabaseAuthContext
- FastAccessFingerprint
- ConstructedQuery
- ContinuationToken
- ExecutionResponse
- QueryPage
- SearchResponse
- ReadResourceResponse
- CapabilityHandshake

Secrets must not be included in fingerprints or telemetry.

## Required error taxonomy

- METABASE_UNAVAILABLE
- AGENT_API_DISABLED
- AUTH_FAILED
- PERMISSION_DENIED
- RESOURCE_NOT_FOUND
- QUERY_CONSTRUCT_FAILED
- QUERY_EXECUTION_FAILED
- DB_TIMEOUT
- ROW_BUDGET_EXCEEDED
- PAGINATION_INVALID
- RATE_LIMITED
- UPSTREAM_CONTRACT_CHANGED

## Invariants

- raw SQL method absent
- admin/content mutation methods absent
- no user-language input method
- no semantic handle minting
- continuation != serialized query
- non-JSON upstream response -> typed contract error
- 202 failed body != success
- page row_count > pinned page size -> reject
- secret excluded from repr/fingerprint/telemetry
- missing principal cannot silently become admin
- no app.v3 import

## Provider-free tests

Must cover:
- public surface forbids raw SQL/admin methods
- session header
- API-key header contract
- access fingerprint excludes secret
- happy health/ping/search/read/construct/execute/query
- continuation
- 401/403/404/429/5xx taxonomy
- Agent-disabled detection
- timeout/transport
- malformed response
- URI/count mismatch
- failed 202 body
- page budget violation

## Live test

Pinned lab:
- session login outside gateway
- instantiate Fast gateway
- search orders
- inspect database resource
- construct portable query
- execute
- query 205 rows
- observe 200 + continuation + 5
- assert raw SQL method does not exist
- handshake ready

## Exit

FT-002B GREEN only if:
- provider-free suite green
- py_compile green
- live Fast gateway suite green
- no app.v3 import
- source branches unchanged

Then FT-003 may begin.

## Rollback

Revert only Fast Track gateway/test/workflow commits.
