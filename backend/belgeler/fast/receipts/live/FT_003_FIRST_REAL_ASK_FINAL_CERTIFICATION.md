# FT-003 — FIRST REAL ASK FINAL CERTIFICATION RECEIPT

Status: CLOSED / GREEN
Date: 2026-09-22
Branch: `feat/dima-metabase-product-fast-track`

## Certification statement

FT-003 proves the first complete Dima Fast Track product vertical:

```text
Turkish real user question
-> real structured model
-> bounded intent
-> real Metabase metadata discovery
-> Dima opaque resource/field authority
-> deterministic temporal binding
-> deterministic portable query
-> real pinned OSS Metabase
-> real analytics DB
-> evidence
-> deterministic answer
-> Dima-native chart/table browser experience
```

A model mistake or material ambiguity does not automatically become execution authority.

## Certified code / oracle SHAs

Product retrieval + Ask code:
`2635ecc26f8093b67636ba581e705a4ed132be6f`

Provider-free retrieval-contract test:
`f86475228074530a426542b9f5674ba12cbb7298`

Browser hydration-stabilized test oracle:
`9faa65eb8ac830285a55ce93940daf68da13f699`

## GREEN run matrix

| Gate | Run | Tested SHA | Result |
| --- | --- | --- | --- |
| FT-003 deterministic core | 35776527074 | f86475228074530a426542b9f5674ba12cbb7298 | GREEN |
| FT-003 real pinned-Metabase live | 35776518129 | 2635ecc26f8093b67636ba581e705a4ed132be6f | GREEN |
| FT-002B Gateway regression | 35776518246 | 2635ecc26f8093b67636ba581e705a4ed132be6f | GREEN |
| FT-003 real-model retrieval sentinel | 35776518107 | 2635ecc26f8093b67636ba581e705a4ed132be6f | GREEN |
| FT-003 real-model + real-Metabase E2E | 35776518184 | 2635ecc26f8093b67636ba581e705a4ed132be6f | GREEN |
| FT-003 browser real /fast/ask | 35777010348 | 9faa65eb8ac830285a55ce93940daf68da13f699 | GREEN |

## Artifact digests

Live Metabase receipt:
`sha256:104d5131d7b8de944777a94d52d18c40ce145c39b49de940599cfd3b4d60098b`

Real-model retrieval diagnostic:
`sha256:bcb98f02e35644f81a72986d333b8d949058b40350626912bceb68c14eb9dd6a`

Real-model E2E:
`sha256:14c4ea5e455f15643c46538afaaabad17eef756c93842f9915f523cc94310c5a`

## Independent DB oracle

Anchor:
`2026-09-07`

Window:
`2026-08-09 <= order_date < 2026-09-08`

Expected and observed:

```text
COUNT = 20
SUM = 16270

East  = 4085
North = 4015
South = 4050
West  = 4120
```

Real-model E2E outputs:
- COUNT answer = `Sonuç: 20 kayıt.`
- SUM answer = `Sonuç: 16270.`
- BREAKDOWN answer = `4 kırılım döndü.`
- all numeric result values equal the independent Postgres oracle.

## Evidence contract

For successful certified requests:
- exact temporal bounds present;
- Metabase resource ref present;
- accepted field refs present;
- canonical portable query present;
- query fingerprint present;
- access fingerprint present;
- result digest present;
- pinned Metabase runtime version present.

No user-visible numeric answer is generated independently from the executed result.

## Retrieval contract

Final model retrieval diagnostic:
- structured schema = PASS;
- supported/unsupported typing = PASS;
- COUNT/SUM = PASS;
- LAST_N_DAYS = PASS;
- CURRENT_MONTH = PASS;
- PREVIOUS_MONTH = PASS;
- ABSOLUTE_DATE_RANGE = PASS;
- direct metadata SEARCH hit = PASS for supported certification cases;
- candidate names/URIs recorded;
- opaque selected handle recorded;
- invented IDs = 0.

Generic contract:
- search terms represent the primary entity/table;
- useful user-language entity terminology may be retained;
- non-English questions include likely English entity/table lookup terminology;
- operation/aggregation words do not own resource retrieval;
- measures/dimensions do not pollute table retrieval unless needed to distinguish the resource.

Explicitly absent:
- Turkish->English dictionary;
- phrase patch;
- regex glossary;
- custom ontology;
- synonym registry.

Bounded catalog discovery remains a permission-filtered safety fallback, not semantic authority.

## Authority fail-closed proof

Ambiguous two-resource case:
- final status = `CLARIFICATION_REQUIRED`;
- error = `AMBIGUOUS_RESOURCE`;
- metadata read after gate = 0;
- construct = 0;
- execute = 0.

Unsupported AVG:
- final status = `UNSUPPORTED`;
- Gateway factory calls = 0.

Unknown field handle:
- fails closed before construct/execute.

Duplicate canonical resource URI:
- request-local dedupe produces one candidate.

## Browser proof

Run:
`35777010348`

Observed:
- backend = real `/fast/ask`;
- Metabase = real pinned OSS;
- DB = real synthetic lab;
- COUNT = PASS;
- SUM = PASS;
- BREAKDOWN = PASS;
- loading = PASS;
- clarification = PASS;
- unsupported = PASS;
- failed = PASS;
- chart = PASS;
- table = PASS;
- desktop = 1440x900 PASS;
- mobile = 390x844 PASS;
- mobile document scrollWidth = 390.

The browser receives no Metabase service/admin secret.

## Failure history closed

### LIVE_SENTINEL_RED_001
Class:
`EVAL_ORACLE`

The product returned 16270 correctly; Decimal normalization produced scientific notation only in the test expectation.
Product formatter was not changed.

### REAL_MODEL_SENTINEL_RED_001
Classes:
- retrieval contract;
- unsupported contract;
- ambiguity oracle ownership.

Closed generically:
- typed UNSUPPORTED;
- authority-owned ambiguity block;
- cross-language metadata retrieval contract;
- no phrase dictionary.

### MODEL_RETRIEVAL_RED_002
Class:
`RETRIEVAL_CONTRACT`

Closed by entity-only metadata lookup semantics.
Final direct SEARCH diagnostic run:
`35776518107 GREEN`.

### BROWSER_HYDRATION_RACE_001
Class:
`EVAL_ORACLE_TIMING`

SSR heading was visible before React client handlers were guaranteed hydrated.
Only the E2E oracle received a bounded hydration settle.
Production UI/backend timing was unchanged.

Final browser run:
`35777010348 GREEN`.

## Hard invariants

```text
RAW_SQL = 0
JOIN = 0
WREN_RUNTIME_DEPENDENCY = 0
V2_RUNTIME_DEPENDENCY = 0
V3_RUNTIME_DEPENDENCY = 0
METABASE_LICENSE_BUDGET = 0
PAID_METABASE_CORE_DEPENDENCY = 0
METABASE_FRONTEND_FORK = 0
METABASE_SERVICE_SECRET_IN_BROWSER = 0
```

## Deliberate debt

`MULTI_CANDIDATE_RESOLUTION = CONSERVATIVE_CLARIFICATION`

This is intentionally conservative for the one-table FT-003 family.
Do not build candidate scoring/multi-table semantics inside FT-003.

## Gate decision

`FT-003 = CLOSED / GREEN`

Next:
`FT-004 — RUN LIFECYCLE / STREAMING / CANCEL`

Do not alter the sealed FT-003 cognition/query/evidence semantics while implementing FT-004.
