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


## Baseline measurement — DMP-P11-MEASURE-001

```text
SHA                         = 977faa99cdf6581ce02c13b55add4077750fe540
workflow                    = 35789082927 = SUCCESS
corpus fingerprint          = da7f13e804c643c376d085b0e0fa94e132fdd8877e1945e4c19257160d03e06c
Luna runtime                = openai/gpt-5.6-luna
Sol runtime                 = openai/gpt-5.6-sol
EV-01                       = PASS / PASS
EV-02                       = PASS / PASS
EV-03                       = SILENT BIND / SILENT BIND
EV-04                       = PASS / PASS
silent-wrong occurrences    = 5
classification              = MATERIAL_TRUTH_GAP / UNRESOLVED_SEMANTIC_SCOPE_ADOPTION
resolver framework          = NOT AUTHORIZED
minimum adoption gate       = AUTHORIZED BY DMP-DEC-0027
```

The post-guardrail run must reuse the same frozen artifact and preserve raw model decisions alongside
the official guarded outcome.


## Post-guardrail result

`d31b83437400dd7f1b70e1b478efad2e8cff781e` / workflow `35790011788`:

```text
same corpus fingerprint       = da7f13e804c643c376d085b0e0fa94e132fdd8877e1945e4c19257160d03e06c
raw model first-pass          = Luna 3/4, Sol 3/4
official guarded first-pass   = Luna 4/4, Sol 4/4
raw silent wrong              = 6
official silent wrong         = 0
guardrail                     = SUFFICIENT
resolver decision             = NOT_NEEDED
```

P11 initial native path may close GREEN while EV-05/06/07 remain explicitly uncertified.


## Final V1 correctness hardening

P11 provider-free proof must include both:
`tests/test_v3_p11_necessity_contract.py` and
`tests/test_v3_p11_entity_value_gate.py`.

Entity-value adoption uses exact typed-scalar identity, not Python cross-type equality.

Forward production seam:
`DMP-P11-INTEGRATION-005` is P13-owned. Accepted semantic authority supplies allowed scopes and the
P5/P10 execution-access fingerprint remains the durable access-identity owner.

No model rerun is required for this hardening.
