# FT-002B — FAST-OWNED METABASE GATEWAY LIVE RECEIPT

Status: GREEN / SEALED
Date: 2026-09-22
Branch: `feat/dima-metabase-product-fast-track`

## Tested implementation

Workflow:
`.github/workflows/dima-fast-ft002-gateway.yml`

Workflow run:
`35763124599`

Tested commit:
`6c845b3dfdde70fa54590cef58a7a26c7b3dc6e5`

Pinned substrate:
- Metabase v0.63.18
- image digest `sha256:1160b570cb11c107bce00e71293552df8a8363e01a32c2c7a048cee002dc8a73`

## Gate results

Compilation:
- Fast auth context: PASS
- Fast typed errors/models/telemetry: PASS
- Fast Metabase Gateway: PASS

Static boundary:
- 3 passed
- no `app.v2` runtime import
- no `app.v3` runtime import
- no Wren runtime import
- missing tenant/user/principal rejected
- no embedded browser/admin service-secret default

Provider-free Gateway contract:
- 21 passed
- auth header contracts
- secret-free access fingerprint
- health/ping/search/read-resource
- construct/execute/query
- continuation contract
- HTTP error taxonomy
- Agent API disabled classification
- malformed upstream envelope
- failed-202 rejection
- page-budget violation rejection
- URI/count mismatch rejection
- typed timeout
- bounded transport retry

Live pinned-Metabase proof:
- 1 passed
- real Agent API search
- real database resource read
- real portable query construct
- real execute
- real combined query
- 205-row pagination observed as 200 + continuation + 5
- startup handshake ready
- raw SQL method absent
- secret-free access fingerprint produced

## Ownership proof

The Fast runtime transport owner is:
`backend/app/fast/metabase_gateway.py`

It does NOT own:
- raw user-language interpretation
- semantic resource selection
- temporal intent
- root cause
- conversation
- report/decision state
- Metabase admin/content mutation

No silent fallback to Wren/V2/V3 exists.

## Isolation proof

Writes remained on:
`feat/dima-metabase-product-fast-track`

No write/merge/rebase/cherry-pick targeted the read-only source branches.

## Decision

FT-002B = CLOSED / GREEN.

This authorizes subsequent product work only according to the current normative gate order.

Because FT-UI-001 inserted a new product gate, FT-003 is still BLOCKED until:
`FT-UI-002 — Metabase/Dima Workspace POC`

is GREEN.

Next exact product gate:
FT-UI-002 pre-development + capability/runtime/SDK lock.
