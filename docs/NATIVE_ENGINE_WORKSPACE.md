# Dima official UI + native engine workspace

Status: **ACTIVE BASELINE / NATIVE ENGINE REFACTOR COMPLETE**

This branch is the canonical working line for the existing Dima UI/UX on the native-first architecture.

## Source ownership

- UI/product: this repository/branch
- engine source: `engine/dima-metabase-engine` git submodule
- engine repository: `UpcyTech/dima-metabase-engine`
- engine source pin: `6bb6924452e5b9dc42b3745bb88c3125a468b297`
- engine release: `0.63.18-dima.0`
- published runtime digest:
  `sha256:0e6819e36c3bd347238159ae483bbaa8db3f0f36bf23cc5d2d8a23012fe111d9`

Clone/update with:

```bash
git submodule update --init --recursive
```

The submodule provides source inspection/development parity. Runtime deployments must use an immutable release pin.

## Current architecture

```text
Dima UI
→ /api/chat
→ server-side native engine adapter
→ Dima Metabase Engine
→ /api/metabot/agent-streaming
→ native Metabot
→ Metabase analytics primitives
→ customer DB
```

No frontend OpenRouter owner. No custom frontend SQL/query agent. No silent legacy fallback.

## Refactor state

Complete:
- UI/navigation preserved;
- existing REST product surfaces preserved;
- chat hot path native;
- native stream adapted to step/token/done/error;
- opaque native multi-turn context transport;
- legacy custom chat intelligence removed;
- architecture guard tests installed;
- quality gate GREEN.

The manual live analytical diagnostic currently exposes an engine-owned Q1 correctness issue. See:

`NATIVE_ENGINE_REFACTOR_HANDOFF.md`

## Scope warning

The databases/import/bootstrap files in the native live-E2E harness are test infrastructure only. They do not redefine production DB/auth/tenant architecture.

## Next work

Normal UI/UX development is unblocked.

Before modifying architecture, read:

`docs/NATIVE_ENGINE_REFACTOR_HANDOFF.md`
