# Stage 00 — Preflight, Repository Audit, and Evidence Baseline

## Objective

Understand the existing frontend and convert the competitor crawl into a usable implementation baseline before changing UI code.

## Read

- frontend/docs/plans/marketing/implementation-pack/
- COMPETITOR_CRAWL_COVERAGE.md
- COMPETITOR_EVIDENCE_AND_LESSONS.md
- CONTENT_CLAIMS_REGISTER.md
- apps/web/src/app/
- apps/web/src/proxy.ts or the current proxy location
- root layout, providers, globals, motion, messages, and E2E files

## Tasks

1. Record branch, worktree, package scripts, current route tree, current providers, and baseline test state.
2. Identify whether / is currently product, marketing, or a mixed boundary.
3. Identify the current locale/default-locale behavior and whether locale-prefixed URLs already exist.
4. Identify product-only imports that must not enter public marketing routes.
5. Inspect representative competitor screenshots from the raw index: one context-layer product, one self-serve analytics product, one industrial/manufacturing product, one docs-heavy product, and Datyo.
6. Write a short evidence note in the stage report: “pattern observed → Dima translation → pattern rejected.”

## Do not

- Change implementation code unless needed to prove a baseline or fix a stage-00 documentation issue.
- Treat the four blocked Seek records as captured content.
- Copy competitor copy, assets, logos, screenshots, or page source.

## Acceptance criteria

- The agent can name the current route/provider/auth boundary.
- The agent has identified all files likely to change in Stage 01.
- Baseline commands and pre-existing failures are recorded.
- Evidence notes are based on the crawl and not on vague category memory.

## Handoff

Return the stage report plus a planned file list for Stage 01. Do not implement Stage 01 in the same pass.
