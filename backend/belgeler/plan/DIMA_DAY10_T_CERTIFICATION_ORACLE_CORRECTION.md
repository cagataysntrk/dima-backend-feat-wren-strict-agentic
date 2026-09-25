# DIMA DAY10-T — CERTIFICATION ORACLE CORRECTION RECEIPT

## LATEST AUTHORITY — DAY8 SEALED / CERTIFICATION ORACLE GREEN / DAY10 CORRECTED TWO-TURN MEASUREMENT AUTHORIZED

```text
branch                          feat/ask-v2-mvp
Product behavior                999d5e28facadd85aefd0d5b47cebec6c3daf4e6
backend/app/** diff              ZERO

Day8 FINAL                      SEALED
Day10 FINAL                     OPEN
certification oracle            GREEN

old run 36135227087             historical RED / EVAL-HARNESS-FIXTURE

PAID_EPOCH_1                    26 / 40 historical CLOSED
PAID_EPOCH_2                    0 / 40 fresh
PAID_EPOCH_2 remaining          40 / 40

next authorized measurement     ONE corrected CANONICAL_NS4 full two-turn run
per-run hard maximum            20 provider calls

ManagerBudget                   4 / 4 / 8 RATIFIED / UNCHANGED
provider topology               UNCHANGED

Day11                           NOT AUTHORIZED
DEV80                           NOT AUTHORIZED
Validation50                    NOT AUTHORIZED
Hidden50                        NOT AUTHORIZED
```

Current-authority rule: the block above is the physically discoverable current state.
Historical receipts below remain immutable audit history and do not override it.


Date: 2026-09-25

Status:

```text
Product behavior                      999d5e28facadd85aefd0d5b47cebec6c3daf4e6
Product patch required                NO
Product behavior diff                 ZERO
run 36135227087 GitHub result         RED (IMMUTABLE)
run 36135227087 Product classification AUTHORITATIVE PRODUCT LIFECYCLE COMPLETED
run 36135227087 harness classification EVAL / HARNESS / FIXTURE
first wrong transition                stale path-specific certification oracle
Day8 live debt                        CLOSED
Day8 FINAL                            SEALED
Day10 FINAL                           OPEN
paid used                             26 / 40
paid remaining                        14 / 40
new paid calls in this correction     0
```

## 1. First wrong transition

The first wrong transition was not Product cognition or Product state.

Historical `backend/lab/v2_day10_product_mvp_live.py` treated one valid execution
trajectory as lifecycle truth by requiring all of:

```text
adaptive_branch_executed observation
ADAPTIVE_BRANCH_OPENED Product event
ResearchDirectiveDisposition.status == APPLIED
non-empty branch_task_refs
```

That contradicted the already-existing conditional `ADAPT_ON_EVIDENCE /
MATERIAL_NEW_DIRECTION` contract, whose typed terminal states already include:

```text
APPLIED
NO_MATERIAL_DIRECTION
BLOCKED
OPEN
```

The correction changes only certification/evaluation ownership. Product runtime and
its ontology are unchanged.

## 2. New authoritative evaluator contract

New eval-only owner:

```text
backend/lab/v2_certification_oracle.py
```

The final/integrated evaluator now projects:

```text
accepted ResearchDirective
+ final ResearchDirectiveDisposition
+ governed Evidence
+ accepted/derived obligation lineage
+ branch/result provenance when applicable
+ CompletionGate/Product terminal state
→ AdaptiveLifecycleCertification
```

Status-specific behavior:

- `APPLIED`: requires governed trigger Evidence, branch task refs, VERIFIED result
  Evidence for the referenced branches, and consistent accepted-parent lineage.
- `NO_MATERIAL_DIRECTION`: requires current inspected VERIFIED parent-lineage
  Evidence, zero branch refs, and a bounded reason. It is validly accounted without
  manufacturing an adaptive branch.
- `BLOCKED`: remains a typed Product terminal. It is never rewritten to APPLIED;
  integrated certification records `VALID_PRODUCT_TERMINAL +
  CERTIFICATION_COVERAGE_INCOMPLETE` when execution coverage is incomplete.
- `OPEN`: if Product is `VERIFIED_COMPLETE`, certification fails as a genuine
  completion/lifecycle accounting defect.

Diagnostic event/observation names are retained as telemetry only and cannot own the
final lifecycle verdict.

## 3. Day8 ROOT live-debt oracle

The final Day8 ROOT proof is now:

```text
accepted ROOT authority
→ server-owned hypothesis exists
→ governed next-test task exists
→ next-test task completed
→ new VERIFIED post-test Evidence exists
→ hypothesis has an admitted post-test Evidence relation
→ ROOT_CAUSE obligation is VERIFIED
→ canonical CANDIDATE_CAUSE exists
→ CONFIRMED_CAUSE count = 0
```

`adaptive_branch_executed` is not part of this final lifecycle definition.

Path-specific provider-free rehearsals that explicitly exist to prove the APPLIED
adaptive-branch path retain their exact trajectory assertions. They are not weakened.

## 4. Offline classification of run 36135227087

The historical GitHub workflow result remains:

```text
36135227087 = RED
```

It is not relabelled GREEN.

Captured run evidence proves:

```text
lane                 RESEARCH
Product status       REPORT
Product terminal     VERIFIED_COMPLETE
ROOT o4              VERIFIED
Wren cube_sql        5
Wren dry_plan        5
Wren query           5
ReportDocument       created
CANDIDATE_CAUSE      present
CONFIRMED_CAUSE      0
```

The final ROOT `o4=VERIFIED` is authoritative. Under the frozen
`RootCauseObligationVerifier`, that state cannot be written unless the hypothesis
ledger contains a non-OPEN typed hypothesis, at least one completed governed next-test
task, and a post-test Evidence link with the status-appropriate typed relation. The
captured structured transport receipt additionally records the server-issued
hypothesis reference and the repaired `propose_hypothesis_evidence_relation`
decision. The emitted ROOT candidate reference is produced only after
`EvidenceLinkedFindingBuilder` successfully creates a canonical finding.

Therefore the captured run supplies the required Day8 ROOT proof without using
`adaptive_branch_executed` as truth.

The accepted ADAPT directive was finally accounted as
`NO_MATERIAL_DIRECTION` against inspected VERIFIED parent-lineage Evidence. Product
then completed. The stale harness rejected the absence of
`adaptive_branch_executed`; that evaluator rejection is the first wrong transition.

Offline classification:

```text
Product execution classification = authoritative Product lifecycle completed
Harness classification           = EVAL / HARNESS / FIXTURE
Product behavior                  = 999d5e28facadd85aefd0d5b47cebec6c3daf4e6
Product patch required            = NO
```

## 5. Day8 final decision

Run `36135227087`, the frozen verifier invariants, the current provider-free
lifecycle oracle, and the affected Day8 gate jointly prove all required Day8 items.

```text
Day8 live debt = CLOSED
Day8 FINAL     = SEALED
```

No new Day8 paid run was executed.

## 6. Day10 final decision

The historical stale harness failed before the signed report-section continuation
could execute.

Therefore:

```text
Day10 FINAL = OPEN
```

The initial integrated Product turn is now correctly classified, but the intended
two-turn Day10 integrated proof remains incomplete.

No continuation shortcut was manufactured and no provider call was spent.

## 7. Provider-free proof

Authoritative current affected runs:

```text
Day10 focused
36138055136 = GREEN

Day8 affected
36138058114 = GREEN
```

Day8 includes the final certification-oracle behavior suite plus the affected ROOT,
epistemic, Evidence, ResearchTask, real-Wren and live-harness provider-free coverage.

No shared Product/Day7 runtime owner changed. Relevant Day7 Evidence and ResearchTask
regressions are included in the Day8 affected gate and are GREEN.

## 8. Bounded certification-oracle audit

Audited final/paid/certification surfaces only:

```text
backend/lab/v2_day10_product_mvp_live.py
backend/lab/v2_certification_oracle.py
backend/tests/test_v2_day10_paid_harness_contract.py
backend/tests/test_v2_day10_prepaid_hardening.py
backend/lab/v2_day10_ns4_provider_free_rehearsal.py
.github/workflows/v2-day10-product-mvp-paid-once.yml
```

Classification:

| Surface | Assertion family | Class | Final verdict owner? |
|---|---|---|---|
| paid workflow | manual-only scope, one job, hard call ceiling | SAFETY_INVARIANT | yes |
| paid harness | lane/status/CompletionGate/final directive state | AUTHORITY_STATE | yes |
| certification oracle | Evidence, branch, task and obligation lineage | PROVENANCE_INVARIANT | yes |
| paid harness | model/provider topology, CONFIRMED_CAUSE ceiling | SAFETY_INVARIANT | yes |
| Product events / observation names | progress and forensic chronology | DIAGNOSTIC_EVENT | no |
| NS4 provider-free applied-branch rehearsal | exact APPLIED adaptive path | PATH_SPECIFIC_TRAJECTORY | yes, only for that explicit path-specific rehearsal |
| final integrated gate | exact adaptive event name | PATH_SPECIFIC_TRAJECTORY | no |

Audit result:

```text
FINAL pass/fail owners:
AUTHORITY_STATE
PROVENANCE_INVARIANT
SAFETY_INVARIANT

DIAGNOSTIC_EVENT independently deciding final GREEN/RED:
NONE

unscoped PATH_SPECIFIC_TRAJECTORY independently deciding final GREEN/RED:
NONE
```

## 9. Permanent oracle constitution

```text
AUTHORITATIVE STATE > OBSERVATION STRING
LIFECYCLE CONTRACT > EXECUTION TRAJECTORY
EVENT != TRUTH
MODEL ACTION SELECTION != SUCCESSFUL TRANSITION
SUCCESSFUL TYPED RUNTIME TRANSITION = TRUTH

MULTIPLE VALID EXECUTION PATHS
must converge to the same lifecycle certification.

HISTORICAL RUNS ARE IMMUTABLE.
Oracle corrections create a new classification receipt;
they do not rewrite the old run result.
```

## 10. Failure artifact observability correction

Future paid failure receipts now carry eval-only authoritative summaries for:

```text
accepted directives
final directive dispositions
Evidence artifact/task/obligation/query-contract refs + verified status
final USER_MUST ledger states
ROOT obligation state
canonical findings
server-owned hypothesis / next-test / Evidence-relation receipts
Product terminal
CompletionGate state
```

Raw rows and SQL are not added for convenience. Observations/events remain diagnostic.

Historical run `36135227087` is not retroactively populated with fields it did not
serialize.

## 11. Metabase architecture harvest

Reference remains:

```text
metabase/metabase@2f3fe9904e4addbcbe4d32403d6a7ab2fc471100
```

Portable parallels retained, without copying runtime code:

1. resolved capability/scope before cognition → Dima authoritative state →
   `ManagerActionAvailability` → bounded schema → model;
2. attempted tool/action != successful terminal transition;
3. applicability before materialization; not-applicable work is not manufactured;
4. durable typed terminal state owns completion, not event chronology.

## 12. Remaining Day10 measurement options

No option is authorized by this receipt.

Current remaining paid envelope is only `14 / 40`; the historical initial integrated
turn itself consumed 14 calls, so a full two-turn measurement cannot be assumed safe
inside the remaining envelope.

Supervisor options to resolve later:

1. authorize a fresh bounded envelope for one corrected full two-turn canonical
   integrated measurement;
2. explicitly ratify a different final proof contract if a provider-free continuation
   proof is considered sufficient;
3. explicitly authorize a continuation-only measurement only after defining a
   reproducible authoritative continuation state. No such shortcut exists today.

Until a supervisor chooses one:

```text
paid execution  STOPPED
Day10 FINAL     OPEN
Day11           NOT AUTHORIZED
DEV80           NOT AUTHORIZED
Validation50    NOT AUTHORIZED
Hidden50        NOT AUTHORIZED
```
