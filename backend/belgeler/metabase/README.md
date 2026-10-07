# DIMA BRAIN V2.1 — CANONICAL DOCUMENTATION INDEX

> **Status:** CURRENT AUTHORITY  
> **Working recovery branch:** `feat/dima-brain-v2-1-specification-closure`  
> **Current readiness program:** `DIMA_BRAIN_V2_1_30CASE_READINESS_PROGRESS.md`  
> **Active semantic recovery candidate:** `eee7583cb67d50779784805c469230ef2b82a5a2` — Fix A/B provider-free GREEN, not final-frozen  
> **Certified engine:** `686671fa7e55f715e4fb5ac155f9e66019fd12d8` / `0.63.18-dima.11.2`  
> **Engine digest:** `sha256:fe1b6fb67be6dbadea1af5d415f3ba2e033d46f91289f5c3c9844bee20c379bd`

This directory intentionally contains only the current Brain V2.1 authority set plus
`legacy/`. If a developer is unsure what is current, start here. During the active
post-benchmark recovery, `DIMA_BRAIN_V2_1_30CASE_READINESS_PROGRESS.md` is the single canonical
readiness execution log. Historical specification-closure receipts remain evidence, but they do
not override its latest phase status or next legal action.

## Read in this order

1. **[DIMA_BRAIN_V2_1_FINAL_ARCHITECTURE.md](./DIMA_BRAIN_V2_1_FINAL_ARCHITECTURE.md)**  
   Canonical first-principles architecture, owner model, runtime topology, T1–T7
   capability foundation, UX-readiness boundary and final readiness status.

2. **[DIMA_BRAIN_V2_1_SEMANTIC_AUTHORITY_CONSTITUTION.md](./DIMA_BRAIN_V2_1_SEMANTIC_AUTHORITY_CONSTITUTION.md)**  
   Permanent semantic-owner law: exactly one owner per business-semantic fact; projections/transport/structural validation may not become second veto authorities.

3. **[DIMA_BRAIN_V2_1_ENGINEERING_PLAYBOOK.md](./DIMA_BRAIN_V2_1_ENGINEERING_PLAYBOOK.md)**  
   Mandatory development method: owner analysis, RED loop, provider-free first,
   stateful/metamorphic testing, paid-live discipline, observability, security,
   commit discipline and repository-wide anti-patterns.

4. **[DIMA_BRAIN_V2_1_CURRENT_HANDOFF.md](./DIMA_BRAIN_V2_1_CURRENT_HANDOFF.md)**  
   Exact current closure receipt and next legal action. This is the operational
   starting point for the next developer.

5. **[DIMA_BRAIN_V2_1_ROUND2_FINAL_ADJUDICATION_2026-10-02.md](./DIMA_BRAIN_V2_1_ROUND2_FINAL_ADJUDICATION_2026-10-02.md)**  
   Immutable broad 30-case quality/speed/cost receipt and the current benchmark verdict.

6. **[DIMA_BRAIN_V2_1_30CASE_READINESS_PROGRESS.md](./DIMA_BRAIN_V2_1_30CASE_READINESS_PROGRESS.md)**  
   Single canonical Phase 0–10 readiness log, exact current candidate, gates and next legal action.

7. **[DIMA_BRAIN_V2_1_SPECIFICATION_CLOSURE_PROGRESS.md](./DIMA_BRAIN_V2_1_SPECIFICATION_CLOSURE_PROGRESS.md)**  
   Earlier specification-closure evidence retained for forensics; not the latest readiness authority.

8. **[DIMA_BRAIN_V2_1_FORWARD_RUNTIME_LAWS.md](./DIMA_BRAIN_V2_1_FORWARD_RUNTIME_LAWS.md)**  
   Compact permanent architecture laws backed by executable CI guardrails.

## Authority precedence

When documents appear to disagree, use this order:

~~~text
executable Product contracts / tests / receipts
>
DIMA_BRAIN_V2_1_SEMANTIC_AUTHORITY_CONSTITUTION.md
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

## Current readiness overlay

The historical Round-2 result below is intentionally preserved as immutable counterexample evidence.
It does **not** describe the current recovery candidate. Current state is:

~~~text
semantic recovery candidate = 34d0bbd461222e2a0859ed196a5a950e362c8622
certified engine             = 4c49b8da6b424b0fa4d8ef340ca1b238d12980c1 / 0.63.18-dima.11.1
provider-free readiness      = GREEN
A3 original live             = pending rerun after operational workflow pin
30-case                      = CLOSED / NOT EXECUTED on this candidate
frontend                      = FORBIDDEN
~~~

Do not infer 30-case readiness from provider-free GREEN alone. Follow
`DIMA_BRAIN_V2_1_30CASE_READINESS_PROGRESS.md` phase order.

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
