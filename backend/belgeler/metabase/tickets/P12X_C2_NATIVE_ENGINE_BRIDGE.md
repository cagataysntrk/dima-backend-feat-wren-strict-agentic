# P12X-C2-001 — Stable native engine bridge + direct-native parity

**Status:** ACTIVE / C1 GREEN / IMPLEMENTATION AUTHORIZED  
**Milestone:** P12X-C2

## Goal

Introduce one thin typed Platform bridge to the fork's native Metabot endpoint and prove that bridge
transport preserves direct-native analytical capability.

## Planned files

```text
NEW backend/app/v3/substrate/metabase/native_models.py
NEW backend/app/v3/substrate/metabase/native_engine.py
NEW backend/tests/test_v3_p12x_c2_native_engine_bridge.py
NEW .github/workflows/dima-metabase-p12x-c2.yml
DOC predev/status/decision/failure receipts
```

## Frozen/forbidden without classified RED

```text
engine/metabase/src/metabase/metabot/**
engine/metabase/src/metabase/api_routes/**
backend/app/v3/authority.py
backend/app/v3/analytics_contract.py
backend/app/v3/security_identity.py
backend/app/v3/execution_identity.py
backend/app/v3/entity_value_gate.py
P4/P5/P10/P11 owner semantics
/api/ask-v2
feat/ask-v2-mvp
feat/dima-metabase-product-fast-track
```

## Provider-free tests first

- request model rejects missing correlation IDs;
- bridge uses only `/api/metabot/agent-streaming`;
- ordered stream parser preserves all raw events;
- stream error fails closed;
- malformed final state fails closed when final state is required;
- no Agent API/Wren/raw SQL fallback;
- engine identity mismatch fails closed;
- caller session identity is passed, never replaced by admin session.

## Live parity

After provider-free GREEN:
- same exact fork runtime;
- same restricted user;
- same Luna model;
- PX-01/PX-07/PX-13/PX-16;
- direct native vs bridge;
- bounded repeats only on material divergence.

## Exit

`P12X-C2 = GREEN` only after bridge/native capability retention and identity/security invariants are
proven.

Implementation remains blocked until P12X-C1 is formally sealed.
