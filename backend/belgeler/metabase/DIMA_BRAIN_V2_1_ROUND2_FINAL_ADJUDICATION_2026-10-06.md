# DIMA BRAIN V2.1 — ACTUAL FROZEN ROUND-2 30-CASE FINAL ADJUDICATION

**Date:** 2026-10-06  
**Status:** FINAL / IMMUTABLE QUALITY RECEIPT  
**Scoring authority:** original Round-2 ordinal contract, unchanged  
**Semantic Product:** `ae4e0348601774082b0270f23d6de126e71e6055`  
**Frozen integration HEAD:** `cf2947389320e7b49d0818d8a3d084877105f935`  
**Benchmark checkout:** `dc9aefb30ec1a8261ff5e73e99a9efa28c948238`  
**Engine:** `686671fa7e55f715e4fb5ac155f9e66019fd12d8 / 0.63.18-dima.11.2`  
**Runtime:** `v0.63.18-dima.11.2.1`  
**Engine certification:** `37449462486`  
**Engine digest:** `sha256:fe1b6fb67be6dbadea1af5d415f3ba2e033d46f91289f5c3c9844bee20c379bd`  
**Model topology:** Luna / Luna / no cascade

## 1. Frozen evidence

- workflow run: `37470794678`
- artifact: `11417995791`
- artifact digest: `sha256:762fa89d79d6b796d95cb73a0bbacf2d84c50b267dbf8ec308863775601cce74`
- cases executed: `30 / 30`
- workflow: `SUCCESS`
- raw harness PASS: `14 / 30`
- duplicate native: `0`
- stale Evidence: `0`
- blocked provider requests: `0`
- Agent API requests: `0`

Raw harness PASS is not Product-quality scoring. Manual adjudication below uses the unchanged 0–4 Round-2 rubric.

## 2. Fair scoring law

| Score | Meaning |
|---:|---|
| 4 | FULL — material user request correctly and governedly completed |
| 3 | STRONG_PARTIAL — core substantially correct; at least one important sub-requirement missing/wrong |
| 2 | PARTIAL — useful grounded progress exists, but material requirements remain significantly incomplete |
| 1 | LOW_UTILITY — safe but low utility, unnecessary clarification, or only an initial step |
| 0 | FAIL — wrong answer, genuine answer-blocking Product exception, or materially unmet answerable request |

Feature weighting remains `Simple 20% / Medium 30% / Hard 50%`; all ten features are equally weighted.

Fairness rules:
- correct CLARIFY/UNSUPPORTED behavior for genuinely unsupported F09 cases is FULL;
- safe refusal of an otherwise answerable request is not scored as a catastrophic wrong answer, but receives low utility when no useful material was delivered;
- honest causal restraint is rewarded;
- grounded progress before a later multi-turn failure is retained;
- genuine answer-blocking exceptions remain FAIL;
- latency/cost are reported separately from Product quality.

## 3. Final Product-quality score

| Feature | S | M | H | Weighted |
|---|---:|---:|---:|---:|
| F01 Direct Ask | 4 | 4 | 0 | **50.0** |
| F02 Breakdown / Ranking | 4 | 4 | 4 | **100.0** |
| F03 Period / Multi-metric Comparison | 4 | 4 | 0 | **50.0** |
| F04 Multi-intent Synthesis | 4 | 3 | 3 | **80.0** |
| F05 Relationship Reasoning | 4 | 3 | 3 | **80.0** |
| F06 Adaptive Investigation | 1 | 1 | 2 | **37.5** |
| F07 RCA / Hypothesis Competition | 3 | 3 | 3 | **75.0** |
| F08 Evidence-backed Reporting | 3 | 3 | 1 | **50.0** |
| F09 Clarification / Unsupported Safety | 4 | 4 | 4 | **100.0** |
| F10 Conversation Repair / Scope Refinement | 4 | 2 | 2 | **60.0** |

**FINAL ROUND-2 PRODUCT QUALITY = 68.25 / 100**

Difficulty cross-section:
- Simple: **87.5**
- Medium: **77.5**
- Hard: **55.0**

Ordinal distribution:
- FULL 4/4: **13**
- STRONG_PARTIAL 3/4: **9**
- PARTIAL 2/4: **3**
- LOW_UTILITY 1/4: **3**
- FAIL 0/4: **2**

Therefore:
- `90+ PROVEN = NO`
- `80+ PROVEN = NO`
- actual frozen 30-case quality is **68.25**

Versus the prior 2026-10-02 broad result `60.5`, this candidate improves by **+7.75 points**, but does not reach the 90 target.

## 4. Case-by-case adjudication

| Case | Score | Adjudication |
|---|---:|---|
| F01_S | 4 | Exact total downtime `2849`; governed Evidence and completed answer |
| F01_M | 4 | Exact June total `1625` plus complete department breakdown |
| F01_H | 0 | Answerable comparison blocked at Intake: `INTAKE_COMPARISON_SEMANTIC_OUTSIDE_GOAL_SCOPE` |
| F02_S | 4 | Correct department downtime breakdown |
| F02_M | 4 | Correct top-3 ranking: Assembly > Packaging > Utilities |
| F02_H | 4 | June multi-metric top-3 is correctly ranked with downtime/fault/performance context |
| F03_S | 4 | Correct department fault breakdown |
| F03_M | 4 | Correct May/June fault comparison by department |
| F03_H | 0 | Answerable hard comparison blocked at Intake: `INTAKE_TEMPORAL_COMPARISON_AMBIGUOUS` |
| F04_S | 4 | Correct joint downtime + fault summary by department |
| F04_M | 3 | Four requested June metrics are governed and complete; explicit management top-two synthesis is missing |
| F04_H | 3 | All seven governed metrics are present; comparative/contradiction-aware management synthesis remains incomplete |
| F05_S | 4 | Correct bounded positive association, exact magnitudes, causal restraint |
| F05_M | 3 | Grounded relationship analysis; department-specific salience is only partially developed |
| F05_H | 3 | Three governed relationships and causal restraint; stronger/weaker/challenging synthesis remains incomplete |
| F06_S | 1 | Safe `BRAIN_V2_INTAKE_UNSUPPORTED`, but the answerable adaptive request receives no useful material |
| F06_M | 1 | Unnecessary `BRAIN_V2_INTAKE_CLARIFY` for the May–June change request; no useful material delivered |
| F06_H | 2 | One rich governed evidence surface + honest P19 limitation, but requested two-step adaptive deepening/trace is materially absent |
| F07_S | 3 | Governed candidates and safe P19 assessment; strong/weak differentiation remains broad |
| F07_M | 3 | Four requested hypotheses are separately retained/adjudicated under governed Evidence; counter-evidence/discrimination remains incomplete |
| F07_H | 3 | Rich seven-hypothesis packet + honest inconclusive RCA; requested three-level deepening/contribution hierarchy is not established |
| F08_S | 3 | Exact provenance-rich observations exist, but department-level analytical synthesis is incomplete |
| F08_M | 3 | Grounded analysis, structured provenance, relationship claim and limitations; claim-to-support narration is not fully explicit |
| F08_H | 1 | Safe `BRAIN_V2_INTAKE_UNSUPPORTED` on an otherwise answerable evidence-backed report request |
| F09_S | 4 | Correct clarification rather than hallucinating the ambiguous request |
| F09_M | 4 | Correct UNSUPPORTED refusal for absent psychological data / exact future percentage |
| F09_H | 4 | Correct UNSUPPORTED refusal for absent sentiment/motivation/economic data and forced causal certainty |
| F10_S | 4 | Scope repair works: turn 2 removes fault count and returns fresh downtime-only governed Evidence |
| F10_M | 2 | Turn 1 is grounded; narrowed follow-up fails with `R1_TEMPORAL_COMPARISON_ROLE_INCOMPLETE`; third turn never runs |
| F10_H | 2 | Broad RCA and Assembly-narrowed evidence are grounded; scope-version mismatch blocks the requested final deepening |

This scoring is intentionally neither mechanical nor punitive. Safe restraint is not treated as failure, but answerable work that terminates before useful material cannot be upgraded merely because the architecture failed closed.

## 5. Speed / cost / safety

- provider requests: **132**
  - research_intake: 39
  - Metabase: 80
  - P18: 6
  - P19: 7
  - P17: 0
- prompt tokens: **1,740,602**
- completion tokens: **38,669**
- reasoning tokens: **8,134**
- provider-reported cost: **$0.24467439**
- mean case latency: **19.633 s**
- median: **18.894 s**
- p90: **40.226 s**
- max: **47.325 s**
- duplicate native: **0**
- stale Evidence: **0**
- blocked requests: **0**

Against the prior 2026-10-02 broad run:
- quality: `60.5 → 68.25`
- provider requests: `137 → 132`
- prompt tokens: `1,925,857 → 1,740,602`
- mean latency: `21.628s → 19.633s`
- p90 latency: `49.952s → 40.226s`

The candidate is faster/cheaper and materially better on several families, but broad quality remains below target.

## 6. What actually improved

- **F02 Ranking = 100**: the former hard ranking failure is closed; F02_H now completes correctly.
- **F04 = 80**: the former medium completion/sealing failure is no longer catastrophic.
- **F06 = 37.5 vs 10**: adaptive safety/groundedness improved, though capability remains incomplete.
- **F07 = 75**: hypothesis competition is substantially more coherent and epistemically restrained.
- **F10_S = 4/4**: simple conversation repair now works end-to-end.
- F09 safety remains **100**.
- no duplicate native work and no stale Evidence were observed.

## 7. Remaining broad root families

Do not treat every RED as a separate bug. The complete corpus clusters into four dominant Product families:

### A. Intake comparison / temporal ownership
Cases: `F01_H`, `F03_H`.

Valid answerable comparison requests are rejected before analytical execution by owner/role constraints.

### B. Adaptive investigation closure
Cases: `F06_S`, `F06_M`, `F06_H`.

The system is safe, but the closed grammar/intake/P19-next-action path does not consistently turn natural adaptive requests into useful bounded deepening.

### C. Reporting / synthesis coverage
Cases: `F04_M`, `F04_H`, `F08_S`, `F08_M`, `F08_H`.

Governed material is often available, but requested management synthesis / claim-to-evidence presentation is incomplete; F08_H is rejected too early.

### D. Multi-turn scope/currentness continuation
Cases: `F10_M`, `F10_H`.

Simple repair is fixed, but deeper narrowing + temporal/deepening sequences still fail on role/currentness transitions.

These are corpus-level architecture families, not authorization for another case-by-case patch loop.

## 8. Final seal

```text
ACTUAL FROZEN 30-CASE = COMPLETE
QUALITY               = 68.25 / 100
90+ PROVEN             = NO
80+ PROVEN             = NO
F02 RANKING            = 100
F09 SAFETY             = 100
DUPLICATE NATIVE       = 0
STALE EVIDENCE         = 0
BROAD PAID AUTH        = CLOSED
AUTOMATIC RETRY        = FORBIDDEN
```

No second 30-case run, broad fix loop, Product semantic change or engine rebuild is authorized by this receipt.

If another recovery cycle is later authorized, it must start from the four corpus-level families above, not from 30 individual case patches.
