# DMP-DEC-0074F — Recovery Panel A Manual RED

Date: 2026-09-29

## Authority and frozen identities

```text
checkout = 714ae70e249658d6184fa060e207eb45675fc4aa
Product behavior = e6b706433e808ff24dc19638328dd1b0df01f0c3
engine = 14323cdde4f258c65c63bbd88f1034f814a7ecb3
release = v0.63.18-dima.7
engine digest = sha256:75a96218bb6a881d792ec13895e438aa5fa897d06a7743c0c3416fa244d13b30
upstream Metabase = 2ba2485c78d7e00a9a25f82c00fc201da71590c4
migration = fd2a7c9e4b61
topology = Terra / Terra / no cascade
```

Commits after the Product behavior SHA through this checkout are CI/test authority changes only;
no `backend/app/**` semantic change is part of this receipt.

dima.7 certification remains immutable and is not rerun:

```text
certification run 36532842632 = SUCCESS
bounded engine tests = GREEN
patch surface = GREEN
source build = GREEN
runtime smoke = GREEN
publish + immutable digest resolution = GREEN
public exact-digest pull = GREEN
runtime identity verification = GREEN
```

Current deterministic closure:

```text
final provider-free 36557781127 = SUCCESS
Human Adoption 36557218727 = SUCCESS
ActionAuthorization 36557442739 = SUCCESS
P12 provider-free 36558203908 = SUCCESS
Phase-1 focused 36558203851 = SUCCESS
governance 36558203766 = SUCCESS
```

## Zero-provider preflight receipt

Run `36558001495` stopped before provider execution because two test contracts still expected the
superseded Product SHA. It is not a paid A result.

```text
provider requests = 0
Product execution = 0
classification = TEST AUTHORITY / PREFLIGHT DEFECT
test-only corrections = 61de3c06... , 714ae70e...
```

## Probe A manual adjudication

```text
probe = SCOPE_CURRENTNESS_HARD_V4
run = 36558258557
artifact = 11028596196
artifact digest = sha256:d4687210df35f5a4e2f9bef2a323720627576f43db9e6cf0ae692f69de411461
```

Historical manual scale:

```text
FAIL=0
LOW_UTILITY=1
PARTIAL=2
STRONG_PARTIAL=3
FULL=4
scoring_authority=MANUAL_ARTIFACT_ADJUDICATION_ONLY
```

Manual inspection of the artifact:

| Requirement | Finding |
|---|---|
| both turns READY | FAIL — 0/2 turns executed |
| native execution > 0 | FAIL — 0 |
| material observation > 0 | FAIL — 0 |
| governed Evidence > 0 | FAIL — 0 |
| scope/currentness transition | NOT REACHED |
| June narrowing | NOT REACHED |
| ranking preservation | NOT REACHED |
| exception = 0 | FAIL |
| silent analytical answer | NONE — failure was fail-closed |

Authoritative verdict:

```text
A = FAIL / 0
```

This verdict is based on manual artifact inspection, not the workflow's mechanical verdict.

## First wrong transition

```text
Research Intake provider response completed
-> typed ResearchIntakeCompiler validation
-> accepted time-surface / typed-period coverage check
-> INTAKE_TIME_PERIOD_SURFACE_MISMATCH
-> public fail-closed UNAVAILABLE
-> Research turns = 0
```

Owner:

```text
RESEARCH_INTAKE
backend/app/v3/research_intake.py
typed time_periods.source_text <-> accepted time_surfaces binding
```

The generic invariant requires the typed period source keys to exactly cover accepted time-surface
keys. The failure occurs before native execution, R5 material observation, P14 lineage, P17/P18/P19,
P20, or Evidence admission. The exact private provider text is not persisted, so divergent strings
are not reconstructed or guessed.

This is generic because the same binding applies to any explicit calendar/time surface; there is no
May/June-specific or benchmark-ID-specific Product branch.

Provider accounting:

```text
orchestration units = 1
actual provider requests = 1
research_intake requests = 1
metabase requests = 0
P17 requests = 0
P19 requests = 0
blocked requests = 0
prompt tokens = 4048
completion tokens = 436
reasoning tokens = 0
provider cost = USD 0.0153505
Sol calls = 0
automatic retry = 0
broad paid runs = 0
```

## Panel disposition

```text
A = RED / MANUAL FAIL 0 / IMMUTABLE
B = NOT RUN / BLOCKED
C = NOT RUN / BLOCKED
D = NOT RUN / BLOCKED
E = NOT RUN / BLOCKED

RECOVERY FLOOR GATE = NOT GREEN
RECOVERY + GROWTH PANEL = NOT GREEN
30-CASE = FORBIDDEN / NOT ELIGIBLE
DMP-DEC-0075 = NOT CREATED
PHASE 1 = IN_PROGRESS / NOT SEALED
DIMA BRAIN V1 = NOT SEALED
```

No aggregate score projection is produced. Historical runs from different Product behavior SHAs are
kept as RCA evidence and are not mixed into this panel certification.

Future continuation requires a generic Research Intake owner correction, provider-free proof, a new
frozen semantic candidate, and then only the failed A family may be rerun under fresh authority.
