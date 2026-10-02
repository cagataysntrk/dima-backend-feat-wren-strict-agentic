# DIMA BRAIN V2.1 — CANONICAL DOCUMENTATION INDEX

> **Status:** CURRENT AUTHORITY  
> **Branch:** `feat/dima-brain-v2-1-discovery-simplification`  
> **Documentation consolidation source HEAD:** `ed95d22a3dee4c3e3cac8932ebd3050a6c0d691e`  
> **Final semantic Product SHA:** `ce8704d6a0db10dc3fb6b1a7e5d0f86afe9ccdc9`  
> **Engine:** `d5c60dc9f37a9ec9c5b0117f178146bbcb8dca88` / `0.63.18-dima.9`

This directory intentionally contains only the current Brain V2.1 authority set plus
`legacy/`. If a developer is unsure what is current, start here.

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

4. **[DIMA_BRAIN_V2_1_FORWARD_RUNTIME_LAWS.md](./DIMA_BRAIN_V2_1_FORWARD_RUNTIME_LAWS.md)**  
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

90+ HIGH-CONFIDENCE READINESS = YES
30-CASE READY = YES

90+ PROVEN = NO
30-case = NOT RUN
frontend = NOT IMPLEMENTED

semantic Product
ce8704d6a0db10dc3fb6b1a7e5d0f86afe9ccdc9

engine
d5c60dc9f37a9ec9c5b0117f178146bbcb8dca88
0.63.18-dima.9
engine builds in V2.1 = 0
~~~

Final fresh capability runs:

| Capability | Run | Mechanical | Manual |
|---|---:|---|---:|
| T1 Scope / Resume | 37002719189 | GREEN | 4/4 |
| T2 ONE_PASS | 37003097196 | GREEN | 4/4 |
| T3 ADAPTIVE | 37003440451 | GREEN | 4/4 |
| T4 DISCOVERY | 37003830042 | GREEN | 3/4 |
| T5 Relationship | 37017824173 | GREEN | 4/4 |
| T6 Contextual Report | 37017824173 | GREEN | 4/4 |
| T7 Multi-intent | 37019171940 | GREEN | 3/4 |

Final provider-free seals:

~~~text
Phase-1 provider-free              37020220583 GREEN
Phase-2/headless + metamorphic     37020220833 GREEN
~~~

## Historical documentation

All superseded roadmaps, recovery notes, pre-development reviews, old handoffs,
old readiness receipts and comparison material are under:

- **[legacy/README.md](./legacy/README.md)**

Nothing under `legacy/` is current execution authority unless one of the four current
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
