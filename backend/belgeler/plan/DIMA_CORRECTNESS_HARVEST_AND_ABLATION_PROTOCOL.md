# DIMA — CORRECTNESS HARVEST & ORCHESTRATION ABLATION PROTOCOL

**Status:** ACTIVE DAY7 portability / comparative-evidence authority  
**Branch:** `feat/ask-v2-mvp`  
**Created after:** D7-SEED-SET root-fix GREEN  
**Reference proof:** `aecd0c0c4642d18711feff58b864c2c866b1fcd6` / `v2-day7-focused 35789148336 = GREEN`

This document has one job:

> Preserve every correctness lesson we have already paid for, while preventing a
> Wren-era implementation detail from becoming permanent product architecture merely
> because it exists.

It is additive to the sealed roadmap/report. It does not renumber days, reopen Day6.5,
replace the living status, or authorize Day8.

---

## 1. NON-NEGOTIABLE DISTINCTION

```text
INVARIANT
!=
CURRENT IMPLEMENTATION
```

An invariant states what must remain true across future engines, planners and product
surfaces.

An implementation states how the current Wren-primary MVP proves that invariant.

Portability decisions are therefore made at the invariant level first. Current code is
ported only when comparative evidence or engine constraints justify it.

---

## 2. CLASSIFICATION VOCABULARY

| Classification | Meaning |
|---|---|
| `MUST_PORT` | Catastrophic/silent correctness or security invariant. Any future execution substrate must preserve it. |
| `SHOULD_PORT` | Strong reliability/product invariant with proven value, but implementation may change. |
| `OPTIONAL` | Product-specific mechanism; retain only if measured value justifies complexity. |
| `WREN_SPECIFIC` | Current representation/extraction/planning mechanism tied to Wren. Underlying invariant may still be MUST/SHOULD_PORT. |
| `BENCHMARK_REQUIRED` | Orchestration/cognition mechanism whose marginal value must be proven by A/B evidence before permanent expansion. |
| `DO_NOT_PORT` | Proven unnecessary/harmful implementation pattern. Requires explicit evidence before resurrection. |

Do not use `OVERENGINEERED` as a pre-measurement label. Use
`BENCHMARK_REQUIRED` until comparative evidence exists.

---

## 3. HARVEST REGISTER

| ID | Mechanism / invariant | Current owner / implementation | Class | Engine dependency | Failure class prevented / value | Current proof | Future owner |
|---|---|---|---|---|---|---|---|
| H-001 | Exactly-one accepted semantic authority per turn | Accepted authority registries / AcceptanceGate | MUST_PORT | none | semantic owner conflict / field laundering | Day6.5 sealed + current Day7 focused GREEN | permanent |
| H-002 | USER_MUST immutability and explicit accounting | UserObligationLedger + CompletionGate | MUST_PORT | none | silent requirement loss | current Day7 focused GREEN | permanent |
| H-003 | Model cannot self-certify canonical semantic truth | SemanticResolver + opaque SemanticHandles + BindingGate | MUST_PORT | semantic resolver abstraction | fabricated metric/dimension/filter truth | Day6.5 seal | permanent |
| H-004 | Principal + tenant fail closed at execution | ResearchToolRunner ↔ GovernedManagerExecutor binding | MUST_PORT | none | cross-tenant/principal substitution | Day7 principal-binding focused proof | Day12–14 expands fingerprint |
| H-005 | Permission check is server-owned; capability presentation is not authorization | ResearchToolRegistry + `authorize()` | MUST_PORT | none | client/tool permission bypass | Day7 provider-free | permanent |
| H-006 | Query result cannot become product truth without sealed provenance | QueryContract concept + EvidenceArtifact | MUST_PORT | execution substrate adapter | unsealed numeric claim / unverifiable answer | real Wren Day7 vertical | permanent |
| H-007 | Evidence must be verified before obligation verification | Governed executor + ObligationVerifier | MUST_PORT | none | evidence laundering | Day7 focused GREEN | permanent |
| H-008 | Completion truth lives outside the LLM | CompletionGate over UOL | MUST_PORT | none | premature “done” / silent USER_MUST loss | Day6.5 + Day7 | permanent |
| H-009 | Task delivery identity/idempotency | run-scoped ResearchTaskRegistry | MUST_PORT | none | duplicate side effect | Day7 registry execution proof | durable replay Day14 |
| H-010 | Cancelled work cannot resurrect through late result | ResearchTaskRegistry + pre-Evidence commit guard | MUST_PORT | none | late cancelled result entering truth | Day7 cancel race proof | durable replay Day14 |
| H-011 | Deadline result cannot enter truth after timeout | execution lease + commit guard | MUST_PORT | none | post-deadline Evidence/UOL mutation | Day7 timeout atomicity proof | Day14 durable semantics |
| H-012 | Cross-domain relationship truth must be explicit business semantic truth | Wren relationship authority + CrossDomainJoinGate | MUST_PORT | current extraction Wren-specific | implicit FK / guessed join execution | Day7 relationship vertical GREEN | future engine adapter |
| H-013 | Grain/cardinality/fanout must be proven before cross-domain execution | CrossDomainJoinFactBuilder + JoinGate + fanout proof | MUST_PORT | current proof mechanics Wren-specific | double counting / wrong analytical grain | `06fc7eae...` + current GREEN | future engine adapter |
| H-014 | Hard tool/query/fanout bounds | ManagerBudget + ResearchFanoutPolicy | MUST_PORT | none | runaway cost/work / hidden overrun | Day7 focused GREEN | permanent |
| H-015 | Accumulated Research state and current-result delta are separate | ResearchStateView | SHOULD_PORT | none | stale-result cognition / state confusion | DD-08 Day7 proof | Day8+ |
| H-016 | Generic duplicate/no-progress prevention | ActionFingerprint + ProgressFingerprint frontier | SHOULD_PORT | none | repeated useless action loops | Day6.5/Day7 provider-free | benchmark ergonomics |
| H-017 | Typed Research tool contracts | ResearchToolContract/Registry | SHOULD_PORT | tool substrate adapters | schema/authority confusion | Day7 focused GREEN | Day7+ |
| H-018 | Bounded Research task lifecycle abstraction | ResearchTask + Registry | SHOULD_PORT | none | uncontrolled task identity/lifecycle | Day7 focused GREEN | durable form Day14 |
| H-019 | Wren MDL representation | Wren schema/MDL | WREN_SPECIFIC | Wren | current semantic representation | current real-Wren proofs | replace only with chosen engine |
| H-020 | CubePlanner/Wren compilation details | Core/Wren execution path | WREN_SPECIFIC | Wren | analytical compilation | real Wren tests | engine adapter |
| H-021 | Wren fanout certificate implementation | `fanout.py` + MDL freshness | WREN_SPECIFIC | Wren/current DB | current fanout proof mechanics | Day7 focused GREEN | preserve invariant H-013 |
| H-022 | Wren relationship metadata extraction | `wren_service.py` schema export | WREN_SPECIFIC | Wren | current relationship provenance | real Wren schema proof | preserve invariant H-012 |
| H-023 | Current CrossDomainJoinFactBuilder mechanics | `cross_domain_facts.py` | WREN_SPECIFIC | Wren | current fact reconstruction | relationship root-fix GREEN | preserve H-012/H-013 |
| H-024 | Initial 2–4 seed task pre-materialization | `seed_initial_user_must` | BENCHMARK_REQUIRED | none | possible cognitive scaffolding | correctness GREEN; marginal-value unmeasured | Day7 ablation / Day11 expansion |
| H-025 | Explicit `inspect_evidence` as its own Manager turn | Manager tool loop | BENCHMARK_REQUIRED | none | deliberate observation barrier vs added turn cost | correctness GREEN; marginal-value unmeasured | Day7 ablation |
| H-026 | Fine-grained deterministic Research scheduling | READY task projection / frontier / fanout scheduling | BENCHMARK_REQUIRED | none | reliability vs orchestration complexity | partial correctness evidence | Day7 ablation |
| H-027 | Cardinality scheduling above the hard safety bound | ResearchFanoutPolicy strategy | BENCHMARK_REQUIRED | none | work prioritization, not hard safety itself | hard bound GREEN; strategy value unmeasured | Day7 ablation |
| H-028 | Full explicit READY task state exposed to model | Manager prompt projection | BENCHMARK_REQUIRED | none | action ergonomics | seed-set GREEN | Day7 ablation |
| H-029 | Model chooses task_id vs reconstructs full typed action | current = full typed action | BENCHMARK_REQUIRED | none | complexity/semantic-restatement tradeoff | seed RED proved redesign NOT currently required | Day7 ablation / Day11 |
| H-030 | Interestingness / finding prioritization | not implemented in Day7 | BENCHMARK_REQUIRED | none | prioritization quality | correctly deferred | Day8 |
| H-031 | Durable crash/restart/replay task persistence | intentionally absent from run-scoped registry | SHOULD_PORT | persistence/MQ | crash recovery / at-least-once delivery | Metabase reference pattern only | Day14 |
| H-032 | Full ExecutionAccessFingerprint / permission-sensitive replay | Day7 only tenant+subject minimum | SHOULD_PORT | auth/persistence | stale permission replay | principal minimum GREEN | Day12–14 |
| H-033 | Physical FK as relationship authority | explicitly rejected | DO_NOT_PORT | none | unsafe semantic join inference | DD-24 + Day7 attacks | permanent prohibition |
| H-034 | Raw-SQL Manager / LLM join-key invention | explicitly prohibited | DO_NOT_PORT | none | truth/security bypass | architecture invariant | permanent prohibition |

---

## 4. METABASE REFERENCE CARRY-FORWARD

Pinned source evidence remains a design reference, not runtime/code authority.

| Mechanism | Day7 disposition | Dima invariant / proof | Deferred owner |
|---|---|---|---|
| DD-08 accumulated state != current delta | IMPLEMENTED | ResearchStateView + result-aware loop | — |
| DD-13 idempotency/cancel/race | RUN-SCOPED IMPLEMENTED | Registry duplicate/cancel/late-race proofs | durable replay Day14 |
| DD-14 missing principal fail-closed | IMPLEMENTED | principal/tenant binding proof | access fingerprint Day12–14 |
| DD-15 bounded fanout | IMPLEMENTED + LIVE ENFORCED | fanout policy + adaptive materialization | benchmark strategy separately |
| DD-11 capability != authorization | IMPLEMENTED | server registry + authorize() | — |
| DD-24 implicit FK != relationship truth | IMPLEMENTED | Wren relationship authority + attacks | — |
| DD-16 interestingness != truth | DEFERRED CORRECTLY | no Day7 causal/interestingness authority | Day8 |
| permission-sensitive replay | DEFERRED | Day7 receipt binds tenant+subject only | Day12–14 |
| derived viewer reauthorization | DEFERRED | not a Day7 concern | Day9/13 |
| durable security-bound state refusal | DEFERRED | run-scoped only today | Day14 |

Do not reopen the Metabase execution runtime. Do not copy Metabase code. Harvest only the
proven reliability invariant.

---

## 5. FREE_COGNITION vs GOVERNED_ORCHESTRATION — SHADOW ABLATION

This benchmark answers one question:

> Does additional deterministic orchestration improve quality/reliability enough to
> justify its cognitive and operational complexity?

It is NOT an unsafe-agent-vs-safe-system comparison.

### Shared hard trust plane — identical in both arms

```text
same accepted authority
same SemanticHandles / semantic truth
same Principal + tenant + permissions
same governed Wren tools
same QueryContract
same Evidence verification
same relationship / grain / cardinality safety
same timeout + cancellation truth boundary
same task side-effect idempotency requirements
same hard query/tool/fanout budgets
same CompletionGate
```

A violation of one of these is an implementation defect, not evidence for removing the
guardrail.

### Arm A — FREE_COGNITION

```text
Sol RESEARCH_MANAGER
+ same governed trust-plane tools
+ minimal orchestration
+ dynamic next-action choice
+ no heavy precomputed Research plan
+ minimum scheduling machinery required for safety
```

### Arm B — GOVERNED_ORCHESTRATION

```text
same Sol RESEARCH_MANAGER
+ current ResearchTask
+ seed/fanout/state/frontier
+ current governed orchestration
```

### Frozen comparison metrics

Quality:
- answer correctness,
- USER_MUST / requirement coverage,
- Evidence coverage,
- completion quality,
- expected adaptive branch,
- unnecessary branch rate.

P0:
- silent wrong,
- cross-tenant,
- permission bypass,
- unverified numeric truth,
- unsafe relationship/grain execution,
- USER_MUST silent loss.

Efficiency/complexity:
- query count,
- LLM turn count,
- latency,
- cost,
- repeated/no-progress action count,
- code/operational complexity.

### Timing

Do NOT run this benchmark while deterministic Day7 closure is still incomplete.

Required sequence:

```text
Day7 deterministic capability closure
→ focused workers=1 LIVE SOL corpus
→ same 8–12 high-information cases on both orchestration arms
→ classify H-024..H-029 from evidence
→ small failure-family/metamorphic confirmation
→ harvest reconciliation
→ Day7 closeout
```

Do not create DEV80/Validation50/Hidden50 here. Day11 Eval Expansion owns the broader
formal ablation/regression study.

---

## 6. DECISION RULE

For any NEW deterministic cognition/orchestration mechanism:

1. Does it protect authority, security, semantic truth, execution safety, Evidence,
   completion truth, hard budget/fanout bounds, or side-effect correctness?
   - **Yes:** it may be implemented as a hard invariant with focused proof.
   - **No:** classify it `BENCHMARK_REQUIRED` first.
2. If benchmarked, does it produce material reliability/quality gain relative to its
   complexity/latency/cost?
   - **Yes:** promote to `SHOULD_PORT` or justified `OPTIONAL`.
   - **No:** demote to `OPTIONAL` / `DO_NOT_PORT`.
3. Never turn a named testcase failure into a permanent cognition rule.

Core rule:

> Cognition stays flexible. Determinism exists where it protects truth/safety, or where
> comparative evidence proves material product value.


---

## 7. DAY7 TOOL-FAMILY PRIMITIVE AUDIT

**Audit checkpoint:** `a7303dec8a83bbb11a1d40c992da75f88444858c`  
**Scope:** `app/stats.py`, `app/yoy.py`, `app/contribution.py`, `app/ilkeller.py`, `app/drill.py`

No implementation is authorized by enum presence alone. The table separates pure
analytical primitives from legacy query/orchestration paths.

| Primitive | Input requirements | Output | Pure / deterministic | Executes DB | Creates SQL | Creates CubeQuery | Semantic assumptions | Causality assumptions | Can consume verified Evidence | Can preserve QueryContract lineage | Safe disposition |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `stats.trend(values)` | ordered numeric series; >=5 samples; governed time-axis/order must be proven by caller | slope, r2, direction, n | yes | no | no | no | function itself knows neither time axis nor metric identity | none; r2 is not significance/confidence | yes, through typed adapter | yes, derived artifact can inherit parent refs | **ADOPT_AS_DERIVED_EVIDENCE** |
| `yoy._merge(...)` | already-aligned current/previous rows plus declared dims/measures | merged rows + percentage deltas | deterministic but legacy temporal shape | no | no | no | infers time columns from row shape/date parsing | none | technically yes | only if wrapper supplies lineage | **UTILITY_ONLY**; never TREND authority |
| `yoy.compute(...)` | CubeQuery + service + temporal mode/time dimension | executes current/previous queries and merges | deterministic orchestration | **yes** | via service | **yes / mutates CQ** | owns legacy period shifting/YTD behavior | none | no; it creates its own execution path | not through current V2 boundary | **REJECT_LEGACY_PATH** |
| `contribution.contributions(rows, dim, measure)` | verified aligned comparison rows containing dim, measure, `measure_gecen`; additivity must be governed externally | per-segment delta/net share/gross share/surprise metrics | yes | no | no | no | assumes row alignment and missing-value policy; caller must validate required columns | **none**; contribution != cause | yes | yes | **ADOPT_AS_DERIVED_EVIDENCE** behind typed preconditions |
| `contribution.toplanabilirlik/ayristirilabilir_mi` | cube metadata + measure | additivity classification / eligibility | deterministic | no | no | no | current implementation includes legacy name-pattern fallback when metadata is silent | none | n/a | n/a | **UTILITY_ONLY**; V2 authority must require explicit governed metadata, not naming heuristics |
| `contribution.decompose(...)` | contribution rows + CubeQuery | formatted report + per-segment clickable CubeQueries | deterministic transform plus query-shape mutation | no | no | **yes** | inherits legacy CQ semantics | wording risks explanatory framing but no formal causal proof | parent rows can be verified | parent refs are not first-class | **REJECT_LEGACY_PATH** as V2 authority; reuse only pure math below it |
| `contribution.pvm_pairs(...)` | explicit cube `pvm` metadata | declared value/volume pairs | yes | no | no | no | safe only when metadata explicitly declares pair | none | n/a | n/a | **UTILITY_ONLY** metadata reader |
| `contribution.pvm(rows,...)` | verified aligned comparison rows + explicitly governed value/volume pair | price/volume/mixed decomposition | yes | no | no | no | requires explicit pair declaration and required columns | decomposition, not causal truth | yes | yes | **ADOPT_AS_DERIVED_EVIDENCE** if/when CONTRIBUTION subtype needs PVM |
| `contribution.pvm_report(...)` | PVM rows + CubeQuery | report + clickable CubeQueries | deterministic transform plus query mutation | no | no | **yes** | legacy CQ semantics | no causal authority | parent rows can be verified | not first-class | **REJECT_LEGACY_PATH** |
| `contribution.rank_dimensions(...)` | multiple decomposition reports | ranking/prioritization | yes | no | no | no | “interesting/explanatory first” scheduling choice | may be misread as explanation/importance | yes | yes | **UTILITY_ONLY**; prioritization value belongs Day8/ablation, not truth |
| `contribution._akran_kiyasi(...)` | CubeQuery/cube metadata/service | peer result + extra driver scans | deterministic orchestration | **yes, repeatedly** | via service | **yes / rewrites CQ** | peer target/direction and extra-measure scan coupled to legacy cube metadata | “driver” language risks causal overreach | no; it manufactures new execution | not through current V2 boundary | **REJECT_LEGACY_PATH** |
| `contribution.arastir(...)` | schema + CubeQuery + service | multi-dimension contribution research | deterministic legacy orchestrator | **yes** | via `yoy.compute` | **yes** | chooses dimensions/modes and executes legacy follow-ups | explanation/prioritization mixed with execution | no | legacy receipts only | **REJECT_LEGACY_PATH** |
| `ilkeller.hesapla(rows,boyut,olcu,hedef)` | governed target entity, governed peer grouping, governed dimension+metric, >=2 peers | target vs peer mean/fark/% | yes | no | no | no | does **not** define peers; caller must prove peer universe + target | none | yes | yes | **ADOPT_AS_DERIVED_EVIDENCE** |
| `ilkeller.bagla(...)` | rows + governed direction policy | picks one entity/value | yes | no | no | no | selecting target is a cognition/policy act, not peer math | none | yes | yes | **UTILITY_ONLY**; do not silently replace accepted target |
| `drill.available_dimensions(...)` | cube metadata + current CubeQuery | candidate dimensions ordered by hop/certification cost | yes | no | no | no | scheduling/candidate semantics from legacy cube metadata | none | n/a | n/a | **UTILITY_ONLY**; scheduling value is benchmark territory |
| `drill.expand_cube_query/select_cube_query/jump_to_related_cube` | CubeQuery + dimension/entity/cube metadata | mutated/new CubeQuery | yes | no | no | **yes** | legacy query-shape authority; related-cube path is not current V2 relationship authority | none | no | no | **REJECT_LEGACY_PATH** as V2 authority |
| `drill.build_raw_row_sql(...)` | physical base object + filters | raw SQL | deterministic | no | **yes** | no | physical schema authority | none | no | no | **REJECT_LEGACY_PATH** for Research Manager |

### Audit verdict by Day7 family

```text
TREND
  SAFE_PRIMITIVE_FOUND:
    stats.trend
  QUERY SIDE:
    existing V2 AnalyticsIR must already be able to yield a governed ordered series;
    yoy.compute is NOT adopted.
  if no governed ordered series exists:
    TREND query primitive remains PRIMITIVE_GAP.

CONTRIBUTION
  SAFE_PRIMITIVE_FOUND:
    contribution.contributions
    optional explicit-metadata PVM: contribution.pvm
  PRECONDITIONS:
    verified aligned comparison Evidence
    governed metric + dimension
    explicit additive/decomposable metadata
    required columns present
  REJECT:
    decompose/pvm_report CubeQuery mutation
    arastir/yoy query execution
  SEMANTICS:
    contribution is observed decomposition, NEVER causal truth.

PEER_COMPARE
  SAFE_PRIMITIVE_FOUND:
    ilkeller.hesapla
  PRECONDITIONS:
    accepted/governed target
    accepted/governed peer universe/grouping
    governed dimension + metric
    verified parent Evidence
  REJECT:
    automatic peer discovery
    contribution._akran_kiyasi query scan
    bagla selecting a new target in place of accepted target.
```

### Derived-Evidence architecture decision

No new Evidence model.

Minimum backward-compatible V2 extension may add explicit lineage fields to
`EvidenceArtifact` (or equivalently a typed lineage payload if schema compatibility
requires it), but the invariant is fixed:

```text
source_kind = DERIVED_ANALYTICAL
parent_evidence_refs = explicit
parent_query_contract_refs = explicit
transformation = TREND | CONTRIBUTION | PEER_COMPARE
verified = true only when:
  every parent is verified
  + typed transform succeeds
  + family invariants pass
```

A derived transform performs zero DB queries and must not mint semantic handles,
relationships, peer sets, time axes or causal claims.

### Harvest classification additions

| ID | Mechanism / invariant | Current owner / implementation | Class | Engine dependency | Failure class prevented / value | Current proof | Future owner |
|---|---|---|---|---|---|---|---|
| H-035 | Pure trend computation over governed ordered series | `stats.trend` | SHOULD_PORT | none | deterministic trend math without model arithmetic | primitive audit @ a7303dec | Day7 derived adapter |
| H-036 | Legacy YoY query/time-shift execution is not V2 trend authority | `yoy.compute` | DO_NOT_PORT | legacy CubeQuery/Wren service | bypass of canonical temporal/query trust plane | primitive audit @ a7303dec | permanent prohibition unless redesigned through V2 |
| H-037 | Contribution decomposition is derived Evidence over verified comparison rows | `contribution.contributions` math | SHOULD_PORT | none | preserves additive decomposition without new query authority | primitive audit @ a7303dec | Day7 derived adapter |
| H-038 | Legacy contribution CubeQuery/drill orchestration | `decompose/arastir/_akran_kiyasi` plumbing | WREN_SPECIFIC | legacy CubeQuery/Wren service | avoids hidden follow-up execution path | primitive audit @ a7303dec | do not port as V2 authority |
| H-039 | Peer comparison math does not define peer semantics | `ilkeller.hesapla` | SHOULD_PORT | none | target-vs-peer math without semantic invention | primitive audit @ a7303dec | Day7 derived adapter |
| H-040 | Automatic peer-set discovery is absent | no V2 governed peer-definition contract | BENCHMARK_REQUIRED | future semantic contract | prevents invented peer universe | primitive audit @ a7303dec | future explicit contract / clarify |
| H-041 | Derived analytics preserve parent Evidence + QueryContract lineage | backward-compatible EvidenceArtifact extension required | MUST_PORT | none | provenance loss / derived-result laundering | audit invariant; provider-free proof pending | Day7 |
| H-042 | Interestingness/prioritization is not truth | legacy `rank_dimensions` / future scheduling | BENCHMARK_REQUIRED | none | prevents “interesting” from becoming “true/causal” | DD-16 + audit | Day8/ablation |
| H-043 | Evaluation availability is separate from product behavior | live eval measurement-validity classifier + provider preflight | MUST_PORT | evaluator/provider independent | provider outage falsely counted as semantic/safety/product failure | `c67bc7a...` / focused `35818843086` GREEN | every future live/ablation evaluator |
| H-044 | Principal and governed tenant identity must be compared in the same typed representation | typed TenantAnalyticsRuntime identity + ResearchToolRunner execution identity gate | MUST_PORT | none | false tenant denial or unsafe cross-tenant equivalence caused by opaque/raw identifier mixing | focused `35822334385` GREEN + LIVE tenant family `35823338833` 3/3 | permanent invariant; representation implementation-specific |
| H-045 | Research control directives cannot mutate USER_MUST semantic capability | ResearchDirective ontology separated from UserObligation capability | MUST_PORT | none | policy/cognition instruction laundering into semantic authority and USER_MUST retyping | focused `35822334385` GREEN + LIVE directive family `35823576275` 1/1 | permanent ontology invariant |
| H-046 | Retrieval/index hit must be rehydrated against current governed truth before authority use | Dima candidate-id rehydration; Metabase current entity-retrieval/search reference | MUST_PORT | retrieval-backend independent | stale/unpublished/index-lag result laundering into semantic truth | Metabase `6ec07f75184dd7f06d84c551d57c58687cf4b859`; Dima semantic path | permanent semantic invariant |
| H-047 | Server-owned discovery scope may constrain visible candidates but cannot mint semantic truth | governed sibling cube scope / future retrieval confinement | MUST_PORT | none | scope hint becoming semantic or relationship authority | Metabase current scope/search reference + Dima sibling-scope LAB | permanent discovery invariant |
| H-048 | Semantic/search diagnostics expose the first disqualifying stage | retrieval/binding diagnostic taxonomy | SHOULD_PORT | none | collapsing catalog absence, retrieval miss, filtering, linker abstain and binding rejection into one fake semantic gap | Metabase search `diagnose` + Dima Day7 diagnostic receipts | Day7+ observability |
| H-049 | Multi-engine retrieval/rank fusion | term + semantic / RRF-style discovery | BENCHMARK_REQUIRED | future search engine | potentially higher recall at additional infra/complexity cost | Metabase reference only; no Dima need proven | reopen only after measured sibling-scope inadequacy |



### Evaluation measurement-validity invariant

```text
SERVICE UNAVAILABLE != PRODUCT NEGATIVE RESULT
```

A behavior metric is defined only for a behavior-evaluable case. Provider auth/quota/
availability failure, harness failure, or fixture failure must be reported outside the
semantic/product numerator and denominator. Hard-safety scoring likewise applies only
after the required cognition call actually produced an evaluable response.

Provider preflight is an evaluation cost/validity guard, not a model fallback mechanism.
It must never silently switch provider/model to manufacture a valid measurement.


---

## TEST ECONOMY HARVEST — 2026-09-23

| ID | Mechanism / invariant | Class | Failure class prevented / value | Current proof / owner |
|---|---|---|---|---|
| H-053 | Evaluation scope must be proportional to the uncertainty being resolved. Narrowest falsifying test runs first; broader paid corpus is forbidden while a narrower probe answers the same question. | MUST_PORT | unnecessary paid-eval cost, noisy debugging, broad-corpus misuse | Day7 supervisor test-economy protocol; permanent eval policy |
| H-054 | Paid evaluation must declare and enforce a model-call budget before provider execution. Guard checks occur before each provider request and artifact records role/total call counts plus exhaustion state. | MUST_PORT | silent API-cost overrun, post-hoc-only accounting | Day7 live/ablation evaluator cost-safety work |
| H-055 | Broad/certification corpora are milestone resources, not iterative debugging tools. | MUST_PORT | DEV80/frozen/validation churn during active tuning | Day7 progressive-widening protocol |

Permanent progressive widening:

```text
LOCAL UNIT / CONTRACT / METAMORPHIC
→ ONE LIVE SENTINEL
→ AFFECTED PAIR
→ MICRO CANARY / MICRO ABLATION
→ MILESTONE CORPUS
→ CERTIFICATION CORPUS
```

STOP-THE-LINE for evaluation cost:
- full frozen corpus to debug one case,
- 8–12 case A/B before 2-case contrast,
- paid LIVE before provider-free proof,
- blank paid workflow input meaning “run all”,
- increasing product/model-turn budget merely to make a scenario pass,
- broad rerun after docs/test-only change.

Current Day7 ablation policy:
- keep 8-case corpus frozen for later,
- first paid ablation = `adaptive-material` + `stable-no-extra-branch`,
- two arms only,
- hard total model-call ceiling = 20,
- if decisive, STOP; if ambiguous, add only `simple-performance`,
- broad ablation deferred to Day11 Eval Expansion.


---

## DAY7 FINAL MICRO-ABLATION RECEIPT — 2026-09-23

### Scope / cost receipt

Provider-free dry-run:

```text
run                         35871834654 = SUCCESS
selected_cases              2
arms                        2
maximum_loop_records        4
configured Manager hard cap 6
provider_requests_made      0
model_calls_budget          16
```

Authorized one-time paid run:

```text
run                  35873755069 = SUCCESS
measurement_valid    true
selected/evaluable   2 / 2
completed records    4
shared authority     verified
Manager model        openai/gpt-5.6-sol
semantic linker      0 calls
temporal normalizer  0 calls
total model calls    16 / 16
service queries      3
budget_exhausted     true
hard safety failures 0
```

Per-case receipt:

```text
adaptive-material
  FREE_COGNITION          quality=true   calls=10 queries=1
  GOVERNED_ORCHESTRATION  quality=true   calls=4  queries=1

stable-no-extra-branch
  FREE_COGNITION          quality=true   calls=2  queries=1
  GOVERNED_ORCHESTRATION  NOT EVALUATED TO COMPLETION:
                          0 model calls; global eval budget already exhausted
```

### Interpretation

This experiment is **INCONCLUSIVE / DAY11 DEFER**.

The final governed stable case did not receive a cognition call because the shared
sequential evaluation budget reached 16/16. Therefore its `quality=false` field is not
a product-quality observation and MUST NOT be interpreted as FREE_COGNITION winning.

There is useful directional signal:
- on `adaptive-material`, both arms were safe/complete and governed used fewer Manager
  calls (4 vs 10);
- FREE_COGNITION consumed 12 calls across its two records and included one no-progress
  action;
- no arm produced a hard-safety violation.

But the pair is not complete under symmetric measurement, so Day7 makes **no product
refactor/retention decision from this micro experiment**.

Per supervisor rule:
```text
NO RETRY
NO 20/30/50/80 call rerun
NO 8-case Day7 ablation
broader FREE vs GOVERNED measurement -> Day11
```

### New evaluation invariant

| ID | Mechanism / invariant | Class | Failure prevented / value |
|---|---|---|---|
| H-056 | Comparative A/B evaluator budgets must be symmetric enough that execution order cannot censor one arm and masquerade as a quality result. Budget exhaustion is an evaluation outcome, not an arm failure. | MUST_PORT | order-biased A/B conclusions, false product regression, cost-driven censoring |

Day11 should use a predeclared symmetric per-arm/per-record allocation or an equivalent
order-independent budget design before drawing comparative architecture conclusions.

No Day7 product code was changed as a result of this ablation.


---

## DAY8 EPISTEMIC HARVEST — 2026-09-23

| ID | Mechanism / invariant | Class | Failure prevented / value | Current proof / owner |
|---|---|---|---|---|
| H-057 | Candidate-test priority / interestingness is scheduling metadata, not epistemic truth. Correlation magnitude, anomaly/outlier score, contribution share or salience may choose what to inspect next but cannot directly produce SUPPORTED, CANDIDATE_CAUSE or CONFIRMED_CAUSE. | MUST_PORT | prioritization laundering into causal truth | D8-A2 `EpistemicLabelGate`; run `35880777420` GREEN |
| H-058 | Only completed VERIFIED governed results may become hypothesis Evidence. Planned queries/tests are not Evidence; derived Evidence must preserve parent Evidence and QueryContract lineage. | MUST_PORT | plan-as-proof, unverified-result claims, lineage loss | D8-A1 `HypothesisLedger` + existing Day7 Evidence model; runs `35880144722`, `35880777420` GREEN |
| H-059 | Hypothesis evidence synthesis must preserve one compatible governed execution context. Evidence must be attached to the current run and belong to the ROOT_CAUSE obligation lineage; unrelated/foreign evidence cannot be silently combined. | MUST_PORT | cross-run / cross-obligation / incompatible-access evidence mixing | D8-A1 current-run Evidence + obligation-ancestry validation; run `35880144722` GREEN |
| H-060 | Manager next-test references must resolve to server-governed ResearchTask identity. Model-minted task, semantic-handle or Evidence IDs are never execution authority. | MUST_PORT | fabricated IDs becoming executable authority | D8-A1 SemanticHandleRegistry / ResearchTaskRegistry / EvidenceStore validation; run `35880144722` GREEN |

Day8 permanent epistemic rules:

```text
trigger Evidence != supporting Evidence
status != epistemic label
association != causation
contribution != causation
interestingness != truth
candidate cause != confirmed cause

CONFIRMED_CAUSE
→ default deny
→ CAUSAL_NOT_IDENTIFIED
```

Current Day8 test-economy receipt:

```text
D8-A1 paid calls = 0
D8-A2 paid calls = 0
no LIVE Sol
no frozen13
no DEV80
no Validation50
no Hidden50
```


---

## DAY8 D8-B HARVEST — 2026-09-23

| ID | Mechanism / invariant | Class | Failure prevented / value | Current proof / owner |
|---|---|---|---|---|
| H-061 | Only active accepted ROOT_CAUSE authority may own mutable hypothesis state. Allowed lifecycle statuses are ACCEPTED, READY, IN_PROGRESS; unaccepted or terminal states fail closed. | MUST_PORT | terminal/unaccepted causal authority manufacturing new epistemic state | `HypothesisLedger._validate_root_authority`; focused `35884577376` GREEN |
| H-062 | Hypothesis/test proposal is planning; only completed VERIFIED governed Evidence may alter epistemic evidence state. | MUST_PORT | plan-as-proof / proposed-test laundering | HypothesisLedger Evidence validation + D8-B proposal boundary |
| H-063 | Hypothesis trigger/relation proposals may reference only current, VERIFIED and cognition-inspected governed Evidence. | MUST_PORT | unseen Evidence becoming model support/contradiction | `CurrentRunEvidenceView` + `HypothesisProposalBoundary`; focused `35884577376` |
| H-064 | Priority/interestingness failure or magnitude cannot invalidate valid Evidence and cannot itself become causal SUPPORTS truth. | MUST_PORT | ranking metadata laundering into causal state | `EpistemicLabelGate.is_priority_only` + D8-B relation admission |
| H-065 | ROOT_CAUSE is an orchestration umbrella, not a ResearchTaskKind and not a QUERY alias. | MUST_PORT | fake direct root-cause query path / capability dead-end | ROOT_CAUSE remains `executable=false`; D8-B does not touch execution mapping |
| H-066 | A run-scoped HypothesisLedger observes newly committed current-run Evidence through the existing Day7 runtime without reconstructing ledger authority or creating another Evidence registry. | MUST_PORT | stale Evidence snapshot / second-ledger authority drift | `CurrentRunEvidenceView` live-view attack; focused `35883953741` + `35884577376` |

Permanent D8-B split:

```text
model cognition
→ proposes hypothesis text / existing governed IDs / SUPPORTS-or-CONTRADICTS relation

proposal boundary
→ requires current + VERIFIED + inspected Evidence

HypothesisLedger
→ validates authority/lineage/IDs and mints hypothesis_id

EpistemicLabelGate
→ limits public claim class

none of these
→ execute DB
→ infer causality
```

Trigger Evidence remains distinct from SUPPORTS Evidence.
Status remains distinct from epistemic label.


---

## DAY8 D8-C ORCHESTRATION HARVEST — 2026-09-23

| ID | Mechanism / invariant | Class | Failure prevented / value | Current proof / owner |
|---|---|---|---|---|
| H-067 | Proposal != applicable task != materialized task != VERIFIED Evidence. | MUST_PORT | proposal/plan being laundered into result or proof | D8-C orchestration boundaries + focused `35895808495` GREEN |
| H-068 | Day8 cognition may select governed identifiers; server owns ResearchTask identity. | MUST_PORT | model-minted task IDs becoming execution authority | `HypothesisNextTestProposal` has no task identity; server `rt_*` mint + registry idempotency |
| H-069 | Execution Evidence and priority/interestingness metadata have independent failure domains. | MUST_PORT | scoring/scheduling failure invalidating a successful governed result | Epistemic gate + Metabase reference pattern + Day8 Evidence boundary |
| H-070 | ROOT_CAUSE cannot create hypotheses from empty epistemic state: inspected Evidence or governed observational bootstrap is required. | MUST_PORT | causal hypothesis from no governed observation | `RootCauseBootstrapPolicy` + current VERIFIED inspected Evidence gate |
| H-071 | An orchestration capability may be semantically bindable without being a directly executable task. | MUST_PORT | bool-executable conflating semantic acceptance with task execution | `ManagerCapabilityExecutionMode.ORCHESTRATED`; ROOT_CAUSE direct executable remains false |
| H-072 | ROOT_CAUSE observational bootstrap is a governed subtask under causal authority, not ROOT_CAUSE→QUERY capability aliasing. | MUST_PORT | hidden direct causal-query path / fake ResearchTaskKind | server-owned observational seed reuses existing DIRECT task families; no `ResearchTaskKind.ROOT_CAUSE` |

D8-C additionally exposed a provider-contract invariant:

```text
advertised cognition surface
=
runtime-admissible governed task families
```

A valid live Sol measurement selected a task/action path that the deterministic trust plane
could not admit. Root cause was not a reason to weaken admission: the provider-facing next-test
surface exposed broader `ResearchTaskKind` vocabulary than the Day8 boundary could honestly
materialize, and the task-kind vocabulary was not mapped back to the existing capability algebra.

Generic owner fix:
- one shared next-test task-kind → existing capability/tool projection,
- the same projection drives provider schema and runtime admission,
- `ROOT_CAUSE_NEXT_TEST_CONTRACT` exposes only existing DIRECT governed families and semantic
  shape requirements,
- runtime gates remain authoritative,
- no keyword/business-case/provider-specific rule was added.

Post-fix deterministic closure:
`35895808495 = GREEN`, including Day8 orchestration, Manager-loop, affected Day7 regressions,
provider-free live-harness contract, and the one real-Wren root-cause sentinel.

Paid receipt:
- `35894577133`: INVALID MEASUREMENT / harness stopped on a correctly rejected proposal;
  2 Sol calls, no semantic/temporal calls.
- `35895279649`: VALID behavior measurement, RED before full end-to-end cognition closure;
  5 Sol calls, no semantic/temporal calls.
- combined paid model calls = 7.
- no third paid case/run was executed.
