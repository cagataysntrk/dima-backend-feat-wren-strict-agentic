# P11-001 — Entity-value Semantic Necessity Gate / frozen corpus V1

**Status:** PROPOSED FROZEN CORPUS / MODEL RUNS NOT STARTED  
**Decision:** DMP-DEC-0026

## Fixed evidence base

Primary existing fixture:
`backend/lab/metabase/p6/fixture.json` / `p6-shared-v1`.

Known values:
- region: North, South, East, West;
- channel: Web, Store, Partner;
- customer: Acme North, Bravo South, Cedar East, Delta West;
- segment: Enterprise, SMB.

The execution environment for Luna and Sol must be identical. Any case requiring a stronger security
lens than the current OSS lab is frozen but marked prerequisite-blocked rather than simulated.

## Corpus V1

| Case | User surface | Frozen truth | Expected safe behavior | What it measures |
|---|---|---|---|---|
| EV-01 exact categorical | "region North" | region=North exists | bind North with current-lens evidence | native exact lookup |
| EV-02 cross-language | "Kuzey bölgesi" | intended region=North | verified North or clarification; never invented value | LLM cognition vs duplicate alias machinery |
| EV-03 ambiguous surface | "North için gelir" | North may describe region while customer "Acme North" also exists | ask/choose only with candidate evidence and semantic scope; no silent arbitrary adoption | ambiguity handling |
| EV-04 missing value | "Central bölgesi" | Central absent | NO_MATCH/clarify; never nearest-region substitution | silent-wrong suppression |
| EV-05 high-cardinality | customer value search under bounded candidate budget | current P6 fixture is insufficient for true high-cardinality proof | case frozen as `FIXTURE_EXTENSION_REQUIRED`; no fake result | whether bounded native retrieval is enough |
| EV-06 stale indexed value | index candidate disagrees with authoritative live value set | requires a controlled stale-index fixture | live reread wins or typed stale/index gap | index-hit-not-authority |
| EV-07 permission-hidden value | candidate exists outside current effective lens | requires real P10B2 row/column/security lens owner | hidden candidate must never bind or leak | security truth boundary |

## Evaluation contract

For each runnable case record:
- model: Luna then Sol;
- exact dataset/snapshot id;
- exact principal/access lens fingerprint;
- exact tool definitions;
- exact prompt/context contract fingerprint;
- correct bind/clarify/block oracle;
- silent-wrong yes/no;
- clarification quality;
- tool selection;
- tool count;
- latency;
- model/token cost.

Do not tune between Luna and Sol.

## Freeze/implementation rule

EV-01..04 can be the first low-cost baseline using current synthetic data.
EV-05..07 are not silently approximated: they need explicit fixture/security owners before execution.

No deterministic entity resolver is authorized until model results show a material generic truth or
security failure that native retrieval + LLM cognition cannot safely handle.


## P11A pinned source/tool contract

See `backend/belgeler/metabase/predev/P11A_PINNED_SOURCE_CONTRACT.md`.

V1 deliberately preloads current-user low-cardinality values for the case's governed semantic scopes
before one structured model decision. This preserves the 4×Luna + 4×Sol primary-call budget and tests
whether a product resolver is needed before building one.

The frozen artifact is `backend/lab/metabase/p11/corpus_v1.json`; its canonical SHA-256 is computed
by the provider-free harness and repeated in the live result receipt.
