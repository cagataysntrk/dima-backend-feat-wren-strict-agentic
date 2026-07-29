# Contracts

Cross-repository agreements that the frontend may reference before the backend
has generated corresponding types.

## Rules

- Prefer generated OpenAPI types in `packages/contracts/src/generated.ts` once an
  endpoint exists.
- Keep provisional shapes small, explicitly feature-gated, and linked from the
  frontend code that consumes them.
- Move a contract to the backend schema/code-generation workflow when it becomes
  implemented; do not let this directory become a second source of truth.

## Documents

- [CEO demo contract](./ceo-demo.md) — agreed shapes for demo capabilities that
  are not yet available from `dima-backend`.
