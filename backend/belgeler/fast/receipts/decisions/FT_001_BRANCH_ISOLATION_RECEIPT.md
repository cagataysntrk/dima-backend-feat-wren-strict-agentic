# FT-001 — BRANCH ISOLATION RECEIPT

Status: SEALED
Date: 2026-09-22

## Fast Track branch

Branch:
`feat/dima-metabase-product-fast-track`

Created from exact SHA:
`352205f112fe735d8f80065c7d255d78905398b9`

Governance bootstrap commit:
`6569d0505565d0917b9f4c032ad2f7366f540f23`

Parent of bootstrap commit:
`352205f112fe735d8f80065c7d255d78905398b9`

This proves the branch started from the pinned snapshot, not a moving branch ref.

## Source references

Pinned read-only snapshots:
- Dima+Metabase: `352205f112fe735d8f80065c7d255d78905398b9`
- Ask-v2: `6d65600842731112f2362261a30660217cbde05d`

At post-bootstrap verification, live source branch heads were observed as:
- `feat/dima-metabase-platform` -> `94e9b3da892a80253495324b2a256f128b037d1b`
- `feat/ask-v2-mvp` -> `875c446476b6ae4907f5cac5d1c7b512e5157538`

Those moving heads are NOT inherited into Fast Track.

## Write audit

During Fast Track preparation, write operations targeted only:
- creation of `feat/dima-metabase-product-fast-track`
- commits/files on `feat/dima-metabase-product-fast-track`

No write operation targeted:
- `feat/dima-metabase-platform`
- `feat/ask-v2-mvp`

## Bootstrap scope

Added only:
- Fast Track governance
- source lock
- branch-local roadmap
- FT-001 pre-development review
- empty-by-design `backend/app/fast` namespace

Functional analytics:
- Metabase query calls: 0
- LLM analytics calls: 0
- Wren calls: 0
- V2/V3 semantic runtime dependencies: 0

## Decision

F0 branch-isolation/bootstrap foundation is accepted.

Next gate:
F0A / FT-002 — pinned Metabase capability preflight + branch-owned gateway preparation.

Until F0A is green:
- no Ask implementation
- no Analyst implementation
- no Root Cause implementation
