# DIMA BRAIN V2.1 — ROUND-2 30-CASE FINAL ADJUDICATION

**Date:** 2026-10-02  
**Status:** FINAL / IMMUTABLE BENCHMARK RECEIPT  
**Scoring authority:** original Round-2 ordinal contract, unchanged  
**Semantic Product:** `ce8704d6a0db10dc3fb6b1a7e5d0f86afe9ccdc9`  
**Frozen pre-benchmark architecture HEAD:** `54dcc6b7f2bc7a0a7cc554801f831c08fbb1c2e6`  
**Engine:** `d5c60dc9f37a9ec9c5b0117f178146bbcb8dca88 / 0.63.18-dima.9`  
**Engine digest:** `sha256:22c384198740274bbbba78fb6d41aa63a6d204dfe708b19a6ca9bc322b458ba7`  
**Model topology:** Luna / Luna / no cascade

## 1. Immutable benchmark evidence

Complete benchmark:

~~~text
run
37027548693

artifact
11235884317

artifact digest
sha256:095d1593ceace7dba94ae872e7ad85f520a3d2b4f4d7de603cfe1f22e4a352f1

benchmark checkout
6b398aaad9a4aa27184f67babdd456e395713e45

cases executed
30 / 30

workflow
SUCCESS
~~~

The workflow verified before execution that `backend/app`, `backend/pyproject.toml`
and the Metabase engine gitlink had no semantic diff from the authorized Product candidate.

The raw harness reported `13 / 30` PASS. That number is **not the final Product-quality
score**. The original Round-2 procedure explicitly requires analyst adjudication from the
actual analytical work, Evidence/provenance, user-task completion, safety behavior and
failure mode.

## 2. Scoring procedure — unchanged from the original Round-2

Ordinal contract:

| Score | Label | Meaning |
|---:|---|---|
| 4 | FULL | The material user request is correctly and governedly completed |
| 3 | STRONG_PARTIAL | The core is substantially correct; at least one important sub-requirement is missing or wrong |
| 2 | PARTIAL | Useful grounded progress exists, but material requirements remain significantly incomplete |
| 1 | LOW_UTILITY | Safe but low utility / unnecessary clarification / only an initial step |
| 0 | FAIL | Wrong answer, genuine Product exception/authority failure, or materially unmet answerable request |

Per-feature difficulty weighting is unchanged:

~~~text
Simple = 20%
Medium = 30%
Hard   = 50%
~~~

All ten features remain equally weighted.

### Fairness rules applied

This adjudication deliberately avoids the prior procedural mistakes:

- no penalty merely because P17/P19 did not loop;
- recursion is not a Product-quality requirement when the user obligation is already safely satisfied;
- correct CLARIFY / UNSUPPORTED behavior in F09 is FULL, even when the conservative raw harness marks it as an exception;
- honest causal restraint is rewarded rather than treated as a failure to guess;
- first-turn grounded work in a multi-turn flow is not erased when a later scope-repair transition fails;
- genuine answer-blocking Product exceptions remain FAIL and are not rescued by architectural intent;
- latency and cost are reported separately from Product quality.

No scoring threshold or difficulty weight was changed after seeing the result.

## 3. Final Product-quality score

| Feature | S | M | H | Weighted feature score |
|---|---:|---:|---:|---:|
| F01 Direct Ask | 4 | 3 | 3 | **80.0** |
| F02 Breakdown / Ranking | 4 | 4 | 0 | **50.0** |
| F03 Period / Multi-metric | 4 | 4 | 0 | **50.0** |
| F04 Multi-intent Synthesis | 4 | 0 | 3 | **57.5** |
| F05 Relationship Reasoning | 4 | 3 | 3 | **80.0** |
| F06 Adaptive Investigation | 2 | 0 | 0 | **10.0** |
| F07 RCA / Hypothesis Competition | 3 | 1 | 3 | **60.0** |
| F08 Evidence-backed Reporting | 4 | 3 | 2 | **67.5** |
| F09 Clarification / Unsupported Safety | 4 | 4 | 4 | **100.0** |
| F10 Conversation Repair / Scope Refinement | 2 | 2 | 2 | **50.0** |

~~~text
FINAL ROUND-2 PRODUCT QUALITY SCORE
60.5 / 100
~~~

Difficulty cross-section:

| Difficulty | Score |
|---|---:|
| Simple | **87.5** |
| Medium | **60.0** |
| Hard | **50.0** |

Ordinal distribution:

~~~text
FULL            11
STRONG_PARTIAL   8
PARTIAL          5
LOW_UTILITY      1
FAIL             5
~~~

Therefore:

~~~text
90+ PROVEN = NO
80+ PROVEN = NO
historical 90+ high-confidence readiness = INVALIDATED BY BROAD EVIDENCE
~~~

## 4. Thirty-case adjudication

| Case | Score | Final reason |
|---|---:|---|
| F01_S | 4 | Correct total downtime = 2849 |
| F01_M | 3 | Correct June department rows; requested total is not explicitly synthesized |
| F01_H | 3 | Correct May/June material supports delta and contributors; final synthesis is incomplete |
| F02_S | 4 | Correct department downtime breakdown |
| F02_M | 4 | Correct top-3 ranking: Assembly > Packaging > Utilities |
| F02_H | 0 | Genuine `R1_NATIVE_RANKING_SCOPE_MISMATCH` before a usable answer |
| F03_S | 4 | Correct department fault breakdown |
| F03_M | 4 | Correct May/June fault comparison |
| F03_H | 0 | Genuine `P20_RESEARCH_SESSION_NOT_SEALED` before a usable answer |
| F04_S | 4 | Correct downtime + fault multi-metric breakdown |
| F04_M | 0 | Genuine `P20_RESEARCH_SESSION_NOT_SEALED` before a usable answer |
| F04_H | 3 | Seven governed metrics produced; management/contradiction synthesis remains incomplete |
| F05_S | 4 | Correct bounded positive association with exact magnitudes and no causal overclaim |
| F05_M | 3 | Grounded relationship analysis; department-specific salience is not fully developed |
| F05_H | 3 | Multiple governed relationship analyses; stronger/weaker/challenging synthesis remains incomplete |
| F06_S | 2 | Correct initial breakdown, but requested conditional deepening is not completed |
| F06_M | 0 | `R1_RESULT_COMPARISON_COVERAGE_INCOMPLETE: reference_period` |
| F06_H | 0 | `BRAIN_V2_NEXT_TEST_DESIGN_INVALID` prevents the requested adaptive investigation |
| F07_S | 3 | Multiple governed candidates + P19; useful and safe, but strong/weak differentiation remains broad |
| F07_M | 1 | Safe rejection due missing temporal material, but no useful hypothesis test result is delivered |
| F07_H | 3 | Rich candidate/evidence packet + honest inconclusive RCA; requested deep contribution hierarchy is not established |
| F08_S | 4 | Evidence-backed result with provenance |
| F08_M | 3 | Grounded multi-metric report; claim/support/limitation narration is incomplete |
| F08_H | 2 | Large governed evidence surface exists, but requested observation/finding/hypothesis/counter-evidence management report is materially incomplete |
| F09_S | 4 | Correct clarification: ambiguous “Bu neden kötü?” is not hallucinated |
| F09_M | 4 | Correct UNSUPPORTED refusal for absent psychological data and exact future percentage |
| F09_H | 4 | Correct UNSUPPORTED refusal for absent sentiment/motivation/economic data and forced causal certainty |
| F10_S | 2 | First turn grounded; scope-repair follow-up fails with `INTAKE_SCOPE_PATCH_INVALID` |
| F10_M | 2 | First turn grounded; narrowed follow-up fails with `R1_NATIVE_FILTER_SCOPE_MISMATCH` |
| F10_H | 2 | Broad RCA first turn grounded; Assembly-only repair fails before completion |

## 5. Quality / speed / cost triad

### Quality

~~~text
Product Quality Score = 60.5 / 100
Safety feature F09    = 100 / 100
Simple cross-section  = 87.5 / 100
Medium                = 60.0 / 100
Hard                  = 50.0 / 100
~~~

The principal quality problem is no longer silent wrong or causal overclaim. It is **broad
semantic/transition coverage**: several valid harder requests reach deterministic Product
contract failures before a useful answer can be completed.

### Speed — complete final run

~~~text
30-case measured case latency total = 648.852 s
mean                                  = 21.628 s / case
median                                = 19.560 s
p90                                   = 49.952 s
max                                   = 54.345 s
~~~

Historical sealed 70.8 Metabase Round-2 reference:

~~~text
total  = 1615.9 s
median = 28.3 s
p90    = 131.7 s
~~~

V2.1 improvement versus that historical single-run reference:

~~~text
total latency  -59.85%
median         -30.88%
p90            -62.07%
~~~

This is a strong architecture/runtime efficiency improvement. It does **not** compensate for
the lower broad Product-quality score.

### Provider cost — complete final run

~~~text
actual provider requests = 137
  research_intake         = 36
  metabase                = 92
  p17_manager             = 0
  p18_manager             = 5
  p19_manager             = 4

prompt tokens             = 1,925,857
completion tokens         = 39,558
reasoning tokens          = 10,076

provider-reported cost    = $0.24909254
average / case            = $0.00830308

average provider requests = 4.57 / case
average prompt tokens     = 64,195 / case
~~~

No requests were blocked by the broad budget ceilings.

The old 70.8 benchmark did not certify exact equivalent provider-dollar telemetry, so an exact
historical dollar reduction must **not** be claimed.

## 6. Protocol disclosure — incomplete first attempt

Before the complete run, benchmark run `37027114003` reached F01_S and then failed in the
benchmark harness:

~~~text
ValueError:
pinpoint model budget must be between 1 and 12
~~~

This was a harness-only incompatibility with an existing case budget, not a semantic Product or
engine failure. The Product and engine remained frozen. The correction only made the benchmark
runner accept the frozen manifest's budget.

However, this first run did reach the provider and therefore must be disclosed:

~~~text
incomplete run
37027114003

cases completed
F01_S only

provider requests
3

prompt tokens
31,960

completion tokens
499

reasoning tokens
149

provider-reported cost
$0.00713981
~~~

The final Product-quality score uses **only** the complete immutable run `37027548693`.

Total broad-campaign spend including the aborted harness attempt:

~~~text
provider requests       = 140
prompt tokens           = 1,957,817
completion tokens       = 40,057
reasoning tokens        = 10,225
provider-reported cost  = $0.25623235
~~~

This is recorded as a protocol deviation. It is not hidden and is not blended into the quality score.

## 7. Broad-run failure families

The broad benchmark exposes several generic Product families that the targeted readiness panel
did not sufficiently cover.

### A. Ranking-admission contract

~~~text
F02_H
R1_NATIVE_RANKING_SCOPE_MISMATCH
~~~

A legitimate hard ranking request reaches a deterministic acceptance mismatch.

### B. Research completion / P20 sealing

~~~text
F03_H
F04_M
P20_RESEARCH_SESSION_NOT_SEALED
~~~

Correct analytical material may exist, but the completion/sealing contract prevents delivery.

### C. Adaptive material / next-test closure

~~~text
F06_M
R1_RESULT_COMPARISON_COVERAGE_INCOMPLETE

F06_H
BRAIN_V2_NEXT_TEST_DESIGN_INVALID
~~~

The accepted adaptive request and legal information-gain path are not broad enough for the corpus.

### D. Causal temporal material interpretation

~~~text
F07_M
INTAKE_CAUSAL_CHANGE_TEMPORAL_MATERIAL_REQUIRED
~~~

The system is safe, but the current contract cannot turn this wording into a useful hypothesis test.

### E. Multi-turn scope repair

~~~text
F10_S / F10_H
INTAKE_SCOPE_PATCH_INVALID

F10_M
R1_NATIVE_FILTER_SCOPE_MISMATCH
~~~

This is the clearest broad regression family: initial work is grounded, but user corrections are not
robustly applied across the original Round-2 conversation-repair corpus.

### F. Synthesis-quality ceiling

F01_H, F04_H and F08 variants frequently possess the required numerical material but under-deliver
the requested manager-facing synthesis. This is a quality issue, not an analytics-data absence issue.

## 8. Final interpretation

Brain V2.1 achieved a real architecture win:

- substantially lower latency;
- low Luna/Luna provider cost;
- P17 discovery/relationship stochastic duplication removed;
- no duplicate native work in the sealed targeted architecture;
- correct unsupported-data safety;
- strong provenance and causal restraint.

But the broad benchmark proves that the targeted panel was not representative enough to justify
the earlier `90+ HIGH-CONFIDENCE READINESS` claim.

The correct current state is:

~~~text
BRAIN V2.1 ARCHITECTURE = FROZEN
ROUND-2 30-CASE        = COMPLETED
FINAL QUALITY          = 60.5 / 100
90+ PROVEN             = NO
80+ PROVEN             = NO
FRONTEND AUTHORIZED    = NO
BROAD BENCHMARK AUTH   = CLOSED
~~~

This result does **not** authorize a Brain V3 or another broad paid patch loop.

## 9. Forward governance

Do not rerun the 30-case benchmark on the same candidate.

The next recovery cycle must be:

~~~text
broad evidence
-> generic failure families
-> provider-free reproducer
-> stateful/metamorphic siblings
-> one owner-correct invariant fix
-> affected provider-free closure
-> targeted live proof only where necessary
-> frozen new candidate
-> readiness reassessment
~~~

A new full 30-case run requires separate explicit user authorization after these generic families
are closed.

The 2026-10-02 complete artifact remains immutable benchmark authority for
`ce8704d6a0db10dc3fb6b1a7e5d0f86afe9ccdc9`.
