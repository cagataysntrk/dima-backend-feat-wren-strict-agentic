# Documentation

This directory contains durable product, engineering, and planning references for
the dima frontend. Keep each document in the domain it describes; avoid adding
ad-hoc files to this root.

## Directory map

| Directory | Purpose | Start here |
| --- | --- | --- |
| [`contracts/`](./contracts/) | Frontend-facing API contracts that are agreed but not yet generated from the backend | [CEO demo contract](./contracts/ceo-demo.md) |
| [`plans/`](./plans/) | Time-bounded implementation plans, research, and delivery runbooks | [Marketing implementation pack](./plans/marketing/implementation-pack/README.md) |

## Conventions

- Use lowercase, hyphenated filenames: `query-contracts.md`, not `Query Contracts.md`.
- Put long-lived reference material in a named domain directory such as
  `architecture/`, `guides/`, or `contracts/`; add the directory to this index.
- Keep active plans under `plans/<initiative>/`. Completed material stays with its
  plan so its context and delivery stages remain traceable.
- Backend-derived types belong in `packages/contracts/src/generated.ts`. A document
  in `contracts/` may only describe an explicitly agreed, not-yet-generated shape.
- When moving a document, update source links and code comments in the same change.

## Current coverage

The repository currently carries an agreed CEO-demo contract and a complete
marketing-site implementation plan. Deployment, architecture decision records,
and brand guidance are referenced by older material but are not currently present
in this repository; add them as dedicated documents rather than embedding them in
unrelated plans.
