# Dima official UI + native engine workspace

This branch is the canonical working line for the existing Dima UI/UX on the native-first architecture.

## Source ownership

- UI/product: this repository
- Engine source: `engine/dima-metabase-engine` git submodule
- Engine repository: `UpcyTech/dima-metabase-engine`
- Engine source pin: `6bb6924452e5b9dc42b3745bb88c3125a468b297`
- Engine release: `0.63.18-dima.0`
- Runtime image: `ghcr.io/upcytech/dima-metabase-engine:0.63.18-dima.0`
- Runtime digest: `sha256:0e6819e36c3bd347238159ae483bbaa8db3f0f36bf23cc5d2d8a23012fe111d9`

Clone with:

```bash
git clone --recurse-submodules <repo>
git submodule update --init --recursive
```

The submodule is for source inspection/development parity. Runtime deployments must pin the image digest above.

## Current refactor boundary

Keep existing UI, navigation, cards, dashboards, schema/model pages, tables, i18n and loading/error states.

Replace only the chat intelligence seam:

```text
/api/chat
-> Dima server-side native engine adapter
-> /api/metabot/agent-streaming
-> native Metabot
```

No frontend OpenRouter owner. No silent fallback to the legacy custom agent.
