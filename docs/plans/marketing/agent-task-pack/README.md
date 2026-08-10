# Dima Marketing — AI Agent Task Pack

This is the execution layer for building Dima's public marketing website one stage at a time. It is intentionally separate from the existing [implementation pack](../implementation-pack/README.md): the implementation pack is the detailed product/architecture plan; this pack is the copy/paste brief, competitor evidence, stage contract, and release handoff for an AI coding agent.

## How to use it

1. Send [`MASTER_PROMPT.md`](./MASTER_PROMPT.md) to the coding agent.
2. Send exactly one stage file from `stages/` with the master prompt.
3. Require the stage completion report before sending the next stage.
4. Keep the agent inside `frontend/apps/web` unless the stage explicitly names a shared package or documentation file.
5. Keep the evidence and claims files open during copy and visual implementation.

The recommended order is:

| Stage | Outcome |
|---|---|
| 00 | Repository, evidence, and baseline audit |
| 01 | Safe public/auth/product route and provider boundaries |
| 02 | Typed content, claim status, locale, metadata, and SEO foundations |
| 03 | Marketing tokens and reusable page primitives |
| 04 | Shared header, mobile navigation, footer, and page chrome |
| 05 | Homepage narrative and deterministic product proof |
| 06 | Product and How It Works pages |
| 07 | Solutions index and textile/dyehouse vertical page |
| 08 | Security, integrations, and trust pages |
| 09 | About, contact, privacy, and terms |
| 10 | Accessibility, performance, SEO, analytics, visual QA, and handoff |

## Source-of-truth order

When sources disagree, use this order:

1. Existing Dima code, tests, API contracts, and security behavior.
2. [`../implementation-pack/`](../implementation-pack/), especially the architecture, claims, IA, and quality documents.
3. This task pack and its competitor evidence.
4. Competitor sites, only for patterns and category context—not for copy, assets, logos, or claims.

## Research artifacts

The crawl was completed outside the repository so the working tree is not burdened with more than a gigabyte of screenshots:

- Coverage metadata: [`/tmp/dima-competitor-research/coverage-v2.json`](/tmp/dima-competitor-research/coverage-v2.json)
- Screenshot index: [`/tmp/dima-competitor-research/visual-index-v2.json`](/tmp/dima-competitor-research/visual-index-v2.json)
- Full-page captures: [`/tmp/dima-competitor-research`](/tmp/dima-competitor-research)
- Seek origin limitation: [`/tmp/dima-competitor-research/seek-origin-block.json`](/tmp/dima-competitor-research/seek-origin-block.json)
- Human-readable scope summary: [`COMPETITOR_CRAWL_COVERAGE.md`](./COMPETITOR_CRAWL_COVERAGE.md)

## Non-negotiable product boundaries

- Marketing routes are public; `/app/**`, auth routes, API routes, tenant behavior, and product business logic remain protected.
- Marketing proof is local, typed, sanitized, and deterministic. It never calls the production backend anonymously.
- No fake customer logos, testimonials, metrics, certifications, connector counts, pricing, security guarantees, or availability claims.
- Every capability is marked `available`, `pilot`, or `planned` when its production status is not unambiguous.
- Dima's visual direction is **Editorial Industrial Intelligence**: warm editorial surfaces, restrained technical detail, real product proof, and a consistent token system.
- The AI agent must not copy competitor copy, assets, layouts, trademarks, or distinctive illustrations.
