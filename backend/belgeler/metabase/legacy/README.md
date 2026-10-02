# DIMA DOCUMENTATION LEGACY ARCHIVE

> **Status:** HISTORICAL / NON-AUTHORITATIVE  
> **Current docs:** `../README.md`

Everything below this directory is preserved for forensic history, decision provenance,
old run receipts and architecture evolution. It is **not** current development authority.

If a legacy file conflicts with current Brain V2.1 documentation, the current documentation
wins.

## Archive categories

- `v2.1-execution-history/` — completed V2.1 spike directive, roadmap and branch-local decision.
- `brain-v2-pre-v2.1/` — pre-V2.1 Brain V2 decisions, roadmaps, receipts and handoffs.
- `v1/` — Dima V1 execution plans/status.
- `metabase-platform/` — earlier Metabase Platform/Core-A/Core-B/recovery/current-status material.
- `predev/` — historical pre-development reviews for P3–P21 and related surfaces.
- `comparison/` — historical Wren vs Metabase neutral-comparison report.

Archive counts in this canonicalization commit:

~~~text
brain-v2-pre-v2.1          9
comparison                 1
metabase-platform          22
predev                     34
v1                         5
v2.1-execution-history     3
total archived files         74
~~~

## How to use this archive

Use legacy files only to answer questions such as:

- Why was an owner boundary chosen?
- What exact RED originally exposed a failure family?
- Which historical run/receipt motivated a generic invariant?
- How did the architecture evolve?

Do **not** use a legacy file to answer:

- What branch/status is current?
- What should I implement next?
- What is the current engine?
- Is the 30-case authorized?
- Which runtime/owner is canonical now?

For those, return to `../README.md`.

## Link policy

Some archived files intentionally preserve historical paths, branch names and relative links.
Those references are part of the historical record and are not maintained as current navigation.

Do not “fix” archived facts to match the present.

## Archive immutability

Historical receipts should not be rewritten to make old decisions appear consistent with the
current architecture. If a historical statement is wrong in hindsight, preserve it and document
the correction in current authority.
