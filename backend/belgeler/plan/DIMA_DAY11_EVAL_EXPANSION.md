# DIMA DAY11 — EVAL EXPANSION FINAL CLOSURE

## Status

```text
branch                           feat/ask-v2-mvp
Day10 Product behavior           e1b3823b82cd28bbe9b4725abf81a4aa49d578ba
Day10 final paid                 36229302570 = GREEN / SEALED

Day11 eval candidate             ce9cd0c02b23b6aaa9aa07ac38f42d102adbd5bd
Day11 workflow                   36229918083 = GREEN
backend/app/** after Day10       ZERO DIFF

Day11                            CLOSED / PROVIDER-FREE GREEN
DEV80                            NOT RUN
Validation50                     NOT RUN
Hidden50                         NOT RUN
paid/live Day11                  NOT RUN
```

## Day11 success card

Roadmap P14 / Day11 requires the product evaluation surface to move from demo-only
confidence toward real-language variation without consuming the final certification
corpora.

Final provider-free receipt:

```text
canonical Day6.5 taxonomy                18 / 18 represented in visible DEV seed
Day7–10 known regression family map      18 / 18 represented
metamorphic invariants                    7 / 7 GREEN
holdout separation                        PASS
hidden prompt bodies committed            0
DEV80 runs consumed by Day11              0
Product code changed by Day11             0
```

Canonical Day11 files:

```text
eval/v2_day11_eval_expansion_manifest.json
tests/test_v2_day11_eval_expansion.py
.github/workflows/v2-day11-eval-expansion.yml
```

## Corpus ownership

Day11 does not create a new truth engine or evaluation authority.

```text
v2_day6_5_dev_cases.yaml
= visible development source
= tuning allowed
= not executed as DEV80 by Day11

v2_day6_research_cases.yaml
= visible complex-research / real-language source

v2_day4_conversation_cases.yaml
= visible multi-turn / repair source

lab/gercek_dunya.py
lab/deneyim.py
= historical scenario sources only
!= Product authority
!= certification authority

Validation50
= unavailable until DEV freeze / authorized phase

Hidden50
= external sealed
= prompt bodies never committed
= external attestation contract preserved
```

## Real-world family coverage

The Day11 manifest fail-closes unless every known family below has committed visible
evidence or a provider-free regression proof:

```text
typo / no-diacritics
incomplete / ellipsis / coreference
topic switch + return
negative research / unsupported
ambiguity / clarification
repair / versioning
exclusion / control boundary
trust-plane bypass
complex research / root cause
adaptive branch lifecycle
source-truth revision
ActionSet materializability / hydration
signed continuation / report immutability
Standard cube coherence
cross-domain governance
temporal / conversation repair
tenant / principal isolation
budget / no-progress
```

The original canonical Day6.5 taxonomy is also cross-checked independently against
the 80-case visible DEV corpus. Day11 cannot claim 100% coverage by redefining its own
family list.

## Metamorphic gate

The Day11 workflow executes the actual existing test nodes for:

```text
source-owner permutation keeps canonical truth
candidate-order permutation keeps semantic identity
same source + different kind remains isolated
scope-group generation is permutation-stable
scope-group classifier is permutation-invariant
ActionSet candidate order keeps ActionSet identity
report supersession leaves prior report immutable
```

A missing test reference is RED. A reference existing only as text is insufficient:
the selected nodes are executed by the workflow.

## Holdout / certification separation

Permanent rule:

```text
DAY11 EVAL EXPANSION
!= DEV80
!= Validation50
!= Hidden50
```

The workflow explicitly asserts that no certification report artifact for these phases
was produced. Existing external holdout attestation tests remain GREEN.

The canonical freeze policy remains:

```text
DEV80 max once per engineering-freeze candidate
code change after DEV80 => new candidate / new DEV80
Validation50 => no tuning
Hidden50 => external sealed / no prompt text in repo
```

## Stop-the-line

Day11 is invalid if any of the following occurs:

```text
hidden or validation prompt bodies enter the Day11 manifest
Day11 automatically starts DEV80 / Validation50 / Hidden50
legacy gercek_dunya / deneyim becomes Product authority
eval failure creates case-specific Product patch
metamorphic proof node is missing
known regression family lacks visible evidence
```

## Exit

```text
all known real-world regression families represented = 100%
holdout separated                                 = PASS
metamorphic invariants                            = GREEN

DAY11 FINAL                                       = CLOSED
NEXT                                               = DAY12
```

Day12 proceeds under the roadmap's Query Contract hardening + telemetry scope.
DEV80 remains unspent until its explicit final integrated-candidate authorization point.
