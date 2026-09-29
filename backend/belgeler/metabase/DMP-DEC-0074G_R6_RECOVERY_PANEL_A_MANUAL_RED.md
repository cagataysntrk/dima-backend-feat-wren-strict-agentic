# DMP-DEC-0074G — R6 Recovery Panel A Manual RED

Status: IMMUTABLE MANUAL RED / STOP

## Frozen candidate

```text
Platform checkout SHA
4b850d4f0b549f3da10e18c99884aba6bd80712a

Product behavior SHA
4829bcb22fedd6f1c97d947ccc106fdc4085895c

engine SHA
14323cdde4f258c65c63bbd88f1034f814a7ecb3

engine release
0.63.18-dima.7

engine immutable digest
sha256:75a96218bb6a881d792ec13895e438aa5fa897d06a7743c0c3416fa244d13b30

engine certification run
36532842632

upstream Metabase SHA
2ba2485c78d7e00a9a25f82c00fc201da71590c4

migration head
fd2a7c9e4b61
```

## Deterministic closure before live probe

```text
full Phase-1 provider-free
36568873204 = GREEN

governance
36568873350 = GREEN

Phase-1 focused
36569083312 = GREEN

P12 provider-free
36569083369 = GREEN

latest governance guard
36569083097 = GREEN
```

No engine build or recertification was rerun.

## Panel A

```text
probe
SCOPE_CURRENTNESS_HARD_V4

run
36569284693 = WORKFLOW RED

artifact
11033800455

artifact digest
sha256:90c612c37f78052bb7d132730bf573e0715832427ce66e97ca6f8e5154cb7bb2

manual verdict
FAIL / RED
```

The product probe step itself completed, but the hard mechanical envelope failed.
Manual artifact inspection confirms a material semantic RED, so workflow RED is not
being overridden.

## First wrong transition

Research Intake accepted the intended typed scope correctly:

```text
time dimension
dimension.event_date

May 2026
[2026-05-01T00:00:00, 2026-06-01T00:00:00)

June 2026
[2026-06-01T00:00:00, 2026-07-01T00:00:00)

metrics
metric.machine_downtime_minutes
metric.fault_count

dimension
dimension.department
```

The first Metabot native query then executed successfully but encoded no temporal
filter at all. It grouped by department and month and used the two requested
native metrics, but its query semantics were unbounded in time. The fixture
happened to contain May and June rows only; that data accident is not legal
scope authority.

R5 material observation therefore correctly rejected Evidence admission with:

```text
R1_NATIVE_TIME_SCOPE_MISMATCH
observed temporal bounds differ from accepted half-open period
```

Owner classification:

```text
FIRST WRONG TRANSITION
accepted typed Research scope
→ Metabot/native query construction
→ executed native query omits accepted temporal bounds

OWNER
Metabot native query construction / semantic query realization

NOT OWNER
Research Intake
R5 material observer
R1 fail-closed comparison
P13
dima.7 engine certification
P14 lineage
```

R1 is behaving correctly by refusing to infer scope from fixture contents.

## Later failure family in the same turn

The second obligation produced a native query containing all eight governed
native metrics rather than the accepted material metric set. R1 correctly
blocked it with:

```text
R1_NATIVE_METRIC_IDENTITY_MISMATCH
observed governed Metabase metric identities differ from accepted scope
```

This is later than the first temporal-scope wrong transition and does not change
the owner of the first RED.

## Downstream noise

Because Turn 1 produced no VERIFIED Evidence and ended PARTIAL/LIMITED, Turn 2
could not legally continue scope mutation and failed closed with:

```text
P14_SCOPE_LINEAGE_REQUIRED
mutated scope requires the exact prior Research session
```

This is downstream noise for this Panel A adjudication. Do not patch P14 from
this receipt.

## Evidence / execution state

```text
Turn 1 READY
true

Turn 1 terminal
LIMITED / PARTIAL

VERIFIED Evidence
0

turns expected / executed
2 / 1

P17 calls
0

P19 calls
0
```

Native analytical execution occurred. Evidence admission failed after execution,
at the material-semantic comparison boundary. No silent fallback converted the
results into VERIFIED Evidence.

## Provider accounting

```text
actual forwarded provider requests
18 / 24

Research Intake
2 / 2

Metabase
16 / 16

P17 manager
0 / 4

P19 manager
0 / 2

prompt tokens
222270 / 350000

completion tokens
3212 / 16000

reasoning tokens
923 / 12000

provider-reported cost
$0.2234343 / $1.00

blocked requests
6

blocked source
metabase

blocked reason
PROVIDER_SOURCE_CEILING_EXHAUSTED
```

All six blocked requests were stopped locally and were not forwarded upstream.
Setup/background paid calls were zero. Sol calls were zero.

## Binding decision

```text
Panel A = MANUAL RED

Panel B = BLOCKED / NOT RUN
Panel C = BLOCKED / NOT RUN
Panel D = BLOCKED / NOT RUN
Panel E = BLOCKED / NOT RUN

no retry
no second A
no RCA
no broad paid
no Sol
no quick Product patch
```

Paid push triggers are removed after this receipt. Further Product changes or
paid probes require fresh supervisor authority.

```text
DMP-DEC-0075 = NOT CREATED
PHASE 1 = IN_PROGRESS / NOT SEALED
DIMA BRAIN V1 = NOT SEALED
```
