# FT-001 — PRE-DEVELOPMENT REVIEW

Status: CLOSED / GOVERNANCE BOOTSTRAP
Ticket: FT-001
Goal: Isolated Fast Track branch and governance foundation.

## Current baseline

Repository:
cagataysntrk/dima-backend-feat-wren-strict-agentic

Parent exact SHA:
352205f112fe735d8f80065c7d255d78905398b9

New branch:
feat/dima-metabase-product-fast-track

Source references:
- feat/dima-metabase-platform@352205f112fe735d8f80065c7d255d78905398b9
- feat/ask-v2-mvp@6d65600842731112f2362261a30660217cbde05d

## User scenario

A developer who knows nothing about prior chats can open the Fast Track branch and know:
- where development may occur,
- which branches are read-only,
- which architecture is intended,
- what not to import,
- what gate is next,
- how failures are handled.

## Current owner

Source codebase from parent snapshot.

## Target owner

Fast Track branch-local governance + future `backend/app/fast/**`.

## Files to touch

- DIMA-FAST-OPERASYON.md
- DIMA-FAST-DURUM.md
- DIMA-FAST-DENETIM.md
- backend/belgeler/fast/**
- backend/app/fast/__init__.py
- backend/app/fast/README.md

## Files not to touch

- source branches
- backend/app/v2/**
- Wren owners
- V3 semantic/compiler owners
- legacy ask behavior
- shared runtime registration

## Invariants

- source branch write = 0
- functional analytics = 0
- Metabase call = 0
- LLM call = 0
- Wren/V2/V3 semantic runtime import = 0
- branch created from exact SHA
- next functional gate = F0A

## Focused proof

After commit:
- branch head differs from source branch only by governance/skeleton files
- source branch HEAD unchanged
- all branch-local documents readable
- app.fast contains no runtime dependency

## Live proof

Not required for FT-001. Live Metabase begins at F0A/FT-002.

## Rollback

Reset/delete Fast Track branch only.
Never modify source branches.

## Exit gate

F0 closes when governance bootstrap commit is present and branch isolation is re-verified.
