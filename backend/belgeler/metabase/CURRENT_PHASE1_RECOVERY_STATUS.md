# Current Phase-1 Recovery Status

Latest binding authority: R8 recovery directive received 2026-09-29.

```text
branch
feat/dima-metabase-platform

Platform HEAD before this receipt
4f44c062f7b20641b98ae372864d1ca4c8249463

R8 Product behavior
af5f0477176c0b3b1ec3b7f733ad393e5fe80bb3

engine
14323cdde4f258c65c63bbd88f1034f814a7ecb3
0.63.18-dima.7
sha256:75a96218bb6a881d792ec13895e438aa5fa897d06a7743c0c3416fa244d13b30

engine certification
36532842632 = GREEN
```

## R8-A provider-free closure

The exact reproducer proved that the top-level user scope mutation is valid. The prior Product
failure came from reopening derived relationship material as a fresh P14 Research root.

Product behavior `af5f0477176c0b3b1ec3b7f733ad393e5fe80bb3` keeps derived relationship
reasoning under the already accepted ResearchSession / obligation. The P14 fail-closed lineage
guard is unchanged.

```text
Core-B focused             36601184795 = GREEN
Core-B seal                36601184682 = GREEN
Core-A final               36601184704 = GREEN
Phase-1 focused            36601184606 = GREEN
Phase-1 final provider-free 36601652755 = GREEN
P12 provider-free          36601652669 = GREEN
governance                 36601184647 = GREEN
```

## R8-A exact paid execution

```text
probe
SCOPE_CURRENTNESS_HARD_V4

checkout
44fdcc4ce54de92e9ea7bf77a8e1bf32ad91fc68

Product behavior
af5f0477176c0b3b1ec3b7f733ad393e5fe80bb3

run
36602428211

artifact
11049457487

artifact digest
sha256:7719c5c85dc2178958e1b65a85ca38d0df3dbd5c15e3234f6c623f534795d097

result
RED / IMMUTABLE

turns expected / completed
2 / 1

orchestration boundary units
7 / 12

actual provider requests
19 / 24

provider requests by source
research_intake = 2
metabase = 16
p17_manager = 1
```

First wrong transition:

```text
native material observation
→ engine HTTP 500
→ clojure.lang.ArityException
→ Wrong number of args (3) passed to:
  metabase.dima.native-material-observation/fail!
→ R1_NATIVE_MATERIAL_OBSERVATION_UNAVAILABLE
```

The earlier `P14_SCOPE_LINEAGE_REQUIRED` Product failure is no longer the first wrong transition
on this candidate.

## Binding disposition

The current supervisor authority freezes the certified dima.7 engine for this recovery:

```text
DO NOT rebuild dima.7
DO NOT rerun engine source-build certification
DO NOT create dima.8
```

It also requires immediate supervisor STOP if an engine product change appears necessary. The
current RED requires an engine product correction in
`metabase.dima.native-material-observation`, so autonomous recovery stops here.

```text
A = RED / IMMUTABLE
B = BLOCKED / NOT RUN
C = BLOCKED / NOT RUN
D = BLOCKED / NOT RUN
E = BLOCKED / NOT RUN

same-SHA retry = FORBIDDEN
second paid candidate = BLOCKED ON SUPERVISOR DECISION
paid push trigger = CLOSED
workflow = MANUAL-ONLY
broad / 30-case = FORBIDDEN
DEV80 / Validation50 / Hidden50 = FORBIDDEN
Sol = NOT RUN

PHASE 1 = IN_PROGRESS / NOT SEALED
30-CASE READY = NO
DIMA BRAIN V1 = NOT SEALED
```

Post-disarm checks:

```text
governance
36602880104 = GREEN

P12 provider-free
36602880265 = GREEN
```

Next legal action: supervisor decision on the engine-owned
`native-material-observation/fail!` arity defect. No further paid execution is legal before that
decision.
