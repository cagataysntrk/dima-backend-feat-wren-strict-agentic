# DIMA BRAIN V2.1 — CANONICAL DOCUMENTATION INDEX

> **Status:** CURRENT AUTHORITY  
> **Working recovery branch:** `feat/dima-brain-v2-1-specification-closure`  
> **Documentation consolidation source HEAD:** `ed95d22a3dee4c3e3cac8932ebd3050a6c0d691e`  
> **Final semantic Product SHA:** `ce8704d6a0db10dc3fb6b1a7e5d0f86afe9ccdc9`  
> **Engine:** `d5c60dc9f37a9ec9c5b0117f178146bbcb8dca88` / `0.63.18-dima.9`

This directory intentionally contains only the current Brain V2.1 authority set plus
`legacy/`. If a developer is unsure what is current, start here. During the active
post-benchmark recovery, `DIMA_BRAIN_V2_1_SPECIFICATION_CLOSURE_PROGRESS.md` is the living
execution log; it may advance run IDs and the next legal action without changing frozen
architecture laws.

## Read in this order

1. **[DIMA_BRAIN_V2_1_FINAL_ARCHITECTURE.md](./DIMA_BRAIN_V2_1_FINAL_ARCHITECTURE.md)**  
   Canonical first-principles architecture, owner model, runtime topology, T1–T7
   capability foundation, UX-readiness boundary and final readiness status.

2. **[DIMA_BRAIN_V2_1_ENGINEERING_PLAYBOOK.md](./DIMA_BRAIN_V2_1_ENGINEERING_PLAYBOOK.md)**  
   Mandatory development method: owner analysis, RED loop, provider-free first,
   stateful/metamorphic testing, paid-live discipline, observability, security,
   commit discipline and repository-wide anti-patterns.

3. **[DIMA_BRAIN_V2_1_CURRENT_HANDOFF.md](./DIMA_BRAIN_V2_1_CURRENT_HANDOFF.md)**  
   Exact current closure receipt and next legal action. This is the operational
   starting point for the next developer.

4. **[DIMA_BRAIN_V2_1_ROUND2_FINAL_ADJUDICATION_2026-10-02.md](./DIMA_BRAIN_V2_1_ROUND2_FINAL_ADJUDICATION_2026-10-02.md)**  
   Immutable broad 30-case quality/speed/cost receipt and the current benchmark verdict.

5. **[DIMA_BRAIN_V2_1_SPECIFICATION_CLOSURE_PROGRESS.md](./DIMA_BRAIN_V2_1_SPECIFICATION_CLOSURE_PROGRESS.md)**  
   Living provider-free recovery log and current certification status.

6. **[DIMA_BRAIN_V2_1_FORWARD_RUNTIME_LAWS.md](./DIMA_BRAIN_V2_1_FORWARD_RUNTIME_LAWS.md)**  
   Compact permanent architecture laws backed by executable CI guardrails.

## Authority precedence

When documents appear to disagree, use this order:

~~~text
executable Product contracts / tests / receipts
>
DIMA_BRAIN_V2_1_FORWARD_RUNTIME_LAWS.md
>
DIMA_BRAIN_V2_1_FINAL_ARCHITECTURE.md
>
DIMA_BRAIN_V2_1_ENGINEERING_PLAYBOOK.md
>
DIMA_BRAIN_V2_1_CURRENT_HANDOFF.md for operational status
>
legacy/ only for historical forensics
~~~

The handoff may advance run IDs, status and the next legal action. It may not silently
change the permanent architecture laws.

## Current closure

~~~text
BRAIN V2.1 ARCHITECTURE FROZEN

ROUND-2 30-CASE = COMPLETED
FINAL PRODUCT QUALITY = 60.5 / 100

90+ PROVEN = NO
80+ PROVEN = NO
former 90+ HIGH-CONFIDENCE READINESS = INVALIDATED BY BROAD EVIDENCE

frontend = NOT IMPLEMENTED / NOT AUTHORIZED
broad paid authorization = CLOSED

semantic Product
ce8704d6a0db10dc3fb6b1a7e5d0f86afe9ccdc9

engine
d5c60dc9f37a9ec9c5b0117f178146bbcb8dca88
0.63.18-dima.9
engine builds in V2.1 = 0
~~~

Canonical broad receipt:

~~~text
complete run      37027548693
artifact          11235884317
artifact digest   sha256:095d1593ceace7dba94ae872e7ad85f520a3d2b4f4d7de603cfe1f22e4a352f1

case latency total 648.852 s
median             19.560 s
p90                49.952 s

provider requests  137
prompt tokens      1,925,857
provider cost      $0.24909254
~~~

The earlier targeted T1-T7 panel remains useful diagnostic history, but its 90+ readiness
inference was disproven by the frozen broad corpus. The broad result is now higher authority
for Product quality.

Final provider-free/stateful seals remain valid architecture evidence:

~~~text
Phase-1 provider-free              37020220583 GREEN
Phase-2/headless + metamorphic     37020220833 GREEN
~~~

## Historical documentation

All superseded roadmaps, recovery notes, pre-development reviews, old handoffs,
old readiness receipts and comparison material are under:

- **[legacy/README.md](./legacy/README.md)**

Nothing under `legacy/` is current execution authority unless one of the current
documents above explicitly cites it for historical evidence.

## Documentation hygiene law

Do not add another `CURRENT_*`, `FINAL_*` or roadmap document beside the canonical set.

For future changes:

1. update the architecture document only if a permanent boundary changes;
2. update the engineering playbook only if the development protocol changes;
3. update the handoff for every new sealed semantic candidate or certification;
4. update runtime laws only through an explicit architecture decision plus executable guard;
5. archive superseded material under `legacy/` in the same commit that supersedes it.

Historical files are evidence. They are not living instructions.
