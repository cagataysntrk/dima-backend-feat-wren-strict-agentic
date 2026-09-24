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


---

## DAY8 POST-LIVE CONTRACT HARVEST — 2026-09-23

| ID | Mechanism / invariant | Class | Failure prevented / value | Current proof / owner |
|---|---|---|---|---|
| H-073 | Opaque governed semantic identities must expose enough non-secret type/provenance metadata for cognition to use them against deterministic capability/task contracts. Canonical semantic values remain registry-owned. | MUST_PORT | needless semantic re-resolution, cognition dead-end caused by type-blind aliases, duplicate semantic work | `SEMANTIC_HANDLE_CATALOG` + `HypothesisLedger.semantic_handle_metadata`; focused `35898621489` GREEN, affected Day7 `35898591894` GREEN |

Supervised re-measurement receipt:

```text
run                    35898027005
validity               VALID
result                 RED
Sol calls              2
semantic-linker calls  0
temporal calls         0
scenario hash          8379daa7fc70a678514b7f87dcb41fcdfec4d317d8ded4cc2712ee7cfb4c8d6a
harness blob           4ae479eb171eccb709eb326309734779533079ab
```

First incorrect transition:
`hypothesis identity → resolve_semantics` where the canonical path required a governed
next-test proposal over existing handles.

Final classification:
`CONTRACT/ARCHITECTURE`.

Single owner:
post-acceptance Manager-safe semantic-handle projection.

Permanent split:

```text
opaque canonical value        YES
opaque server identity        YES
opaque semantic target kind   NO — cognition needs governed non-secret type metadata
```

This does not weaken semantic authority. The model still cannot mint, mutate or see canonical
semantic targets. It receives only registry-validated metadata needed to select among already
declared governed task shapes.

Paid Day8 total after the supervised re-measurement = 9 Sol calls.
No further paid rerun is authorized automatically.
Day8 deterministic/real-Wren remains GREEN; live certification remains OPEN.


---

## DAY9-A REPORT AUTHORITY HARVEST — 2026-09-23

| ID | Mechanism / invariant | Class | Failure prevented / value | Current proof / owner |
|---|---|---|---|---|
| H-074 | Report composition is a pure projection over governed Evidence/Findings; reference hydration and permission resolution are separate boundaries. | MUST_PORT | report worker silently becoming a second query/resolver/security engine | `ReportBuilder` dependency boundary + focused `35903324742` GREEN |
| H-075 | Presentation/render configuration is not analytical or Evidence truth. | MUST_PORT | chart/table settings mutating numeric value, lineage, semantic scope or epistemic label | `ReportRenderSpec` kept presentation-only; artifact failure does not mutate Evidence |
| H-076 | Access to a report/container is not permanent access to underlying warehouse-derived data; persisted replay must reauthorize the current viewer. | MUST_PORT | creator-access laundering across users/tenants | `ReportSourceProvenance` retains tenant/run/context + `CURRENT_RUN_ONLY_REAUTHORIZE_ON_REPLAY`; no fake Day9 security token |
| H-077 | Report artifacts reference canonical Evidence/Findings; they do not duplicate analytical truth by value. | MUST_PORT | second truth store, stale copied values, broken provenance | `ReportEvidenceRef`, `ReportFindingRef`, `ReportArtifactRef`; raw tool payload rejected |
| H-078 | Typed result-shape metadata may guide presentation but cannot become a semantic-truth owner. | MUST_PORT | column-name/name/unit heuristics silently manufacturing semantics | `ReportResultShape` is supplied presentation support only; ReportBuilder performs no semantic inference |

Day9-A structural grounding rules:

```text
NUMERIC / ANALYTICAL
→ governed current-run VERIFIED EvidenceRef required

EPISTEMIC
→ exactly one canonical FindingRef
→ finding provenance must match report source lineage
→ underlying Evidence lineage required
→ epistemic label/limitations preserved

CANDIDATE_CAUSE
→ remains CANDIDATE_CAUSE

CONFIRMED_CAUSE
→ unavailable / rejected
```

Identity policy:

```text
server owns report_id / section_id / block_id / followup_context_ref
presentation title/content/render settings
!=
authority identity
```

Current-viewer replay seam is deliberately retained, not implemented:
EvidenceRef + QueryContractRef + tenant/run/context provenance are kept so future security layers can
reauthorize. Same-request/current-run rendering is valid; cross-user persisted replay is not yet an
authorized cache behavior.

Legacy characterization:
- `app/report.py::compose_report` is NOT canonical Day9 authority because it queries;
- `app/report.py::bolumlerden_kur` is reference-only for composition of already-executed blocks;
- `app/viz.py` is deferred to a future presentation adapter and cannot own semantic truth.

Focused receipt:

```text
Day9 product SHA  2415948f9857cd8ec1707c0eb05f539c8c1edb9c
focused run       35903324742 = GREEN
tests             16 passed
paid calls        0
DB/Wren/LLM       0
```


---

## DAY9-B BOUNDED NARRATION HARVEST — 2026-09-23

| ID | Mechanism / invariant | Class | Failure prevented / value | Current proof / owner |
|---|---|---|---|---|
| H-079 | Probabilistic narration selects/orders canonical report references; it does not generate analytical truth. | MUST_PORT | valid Evidence paired with hallucinated factual narration | `NarrationPlanProposal` has reference-only schema; focused `35908601251` + live `35908863544` GREEN |
| H-080 | Executive summary is a projection of selected canonical blocks, not a new ungrounded summary claim. | MUST_PORT | summary hallucination / unsupported numbers or causal statements | deterministic renderer emits selected canonical `ReportBlock.content` verbatim |
| H-081 | Narration receives a minimum presentation-safe context; raw Evidence/query/semantic internals are not narration context. | MUST_PORT | narrator becoming a second analytics/semantic authority or leaking unnecessary governed internals | `NarrationPacket` excludes Evidence/Finding/QueryContract payloads, semantic scope, raw rows/SQL and conversation scratch |
| H-082 | Narration failure is a presentation failure domain; it cannot invalidate a valid ReportDocument. | MUST_PORT | provider/schema/plan failure being misreported as analytical failure or triggering query repair | exactly one structured call; invalid narration → deterministic fallback; no retry/repair/analytics |
| H-083 | Canonical report authority remains immutable under all presentation/narration variants. | MUST_PORT | presentation ordering mutating report Evidence, Findings, anchors or epistemic truth | frozen `ReportDocument` + presentation-only `ReportNarrationOverlay`; metamorphic tests + live equality proof |

D9-B permanent split:

```text
ReportDocument
= analytical/report authority

NarrationPlanProposal
= probabilistic reference ordering/selection only

NarrationPlanGate
= deterministic admissibility

ReportNarrationOverlay
= presentation-only server object

ReportNarrationRenderer
= canonical-text projection
```

Provider output cannot contain:
- factual summary prose,
- rewritten analytical/numeric claim,
- causal statement,
- EvidenceRef / FindingRef / ArtifactRef,
- semantic identity,
- overlay identity.

Material block omission is structurally forbidden:

```text
ordered_block_refs
= exact permutation of canonical section block IDs
```

Invalid narration never triggers a second model call.

Strict transport invariant:

```text
Pydantic domain schema
→ strict-native transport normalization
→ every object property required
→ additionalProperties=false
→ defaults removed from provider contract
```

This normalization is transport-only and does not change D9-A truth or D9-B plan semantics.

Provider-free receipt:

```text
run        35908601251
result     GREEN
tests      15 / 15
paid calls 0
```

Live receipt:

```text
run                    35908863544
result                 GREEN
model                  openai/gpt-5.6-sol
model calls            1
tool calls             0
semantic calls         0
Wren calls             0
DB calls               0
Research calls         0
invented IDs           0
new factual claims     0
candidate cause kept   yes
limitations kept       yes
ReportDocument changed no
```

No second live reassurance case was run.

Day8 live root-cause debt remains OPEN and is not superseded by this Day9 narration proof.


---

## DAY10 PRODUCT-MVP HARVEST — 2026-09-23

| ID | Mechanism / invariant | Class | Failure prevented / value | Current proof / owner |
|---|---|---|---|---|
| H-084 | A paid milestone gate must not run when sealed budget authority makes the canonical scenario structurally impossible. Measurement validity precedes spending. | MUST_PORT | paying for a guaranteed budget RED, then misclassifying it as model/product quality | Day10 budget receipt; `ManagerBudget.max_total_manager_turns=6`; paid Product-MVP NOT RUN |
| H-085 | Evidence from a sibling USER_MUST cannot be reused as ROOT_CAUSE Evidence merely to save turns. Causal Evidence must belong to the root obligation/derived ancestry. | MUST_PORT | causal provenance laundering and false budget compression | `HypothesisLedger._validate_evidence/_obligation_belongs_to_root` |
| H-086 | Real-Wren integration fixtures must provide bounded semantic cognition when a verified alias is legitimately ambiguous; disabling cognition is not proof that the resolver should guess. | MUST_PORT | test fixture forcing production deterministic semantic heuristics/automatic ambiguity picks | D10-F RED triage → bounded test provider → `35921618398` GREEN |
| H-087 | Section continuation inherits only signed governed section scope; inherited handles are context scope, never forged current-turn source bindings. | MUST_PORT | follow-up semantic laundering / old report state becoming new user-source authority | signed continuation tests + immutable contract v1→v2 |
| H-088 | Product streaming is an adapter over the same ProductCoordinator and existing Research lifecycle, not a parallel analytical core. | MUST_PORT | sync/stream semantic drift, duplicate cancellation/completion authority | Day10 focused `35921618398` GREEN |

Day10 deterministic milestone receipt:

```text
product behavior SHA                 f4299a3bcfb48ab351db20f555483fe483e5e3e8
focused + real-Wren run              35921618398
provider-free                        29 passed
real-Wren Product vertical           1 passed
paid calls                           0
```

The D10-F real-Wren fixture initially returned CLARIFY because `bölüm` is a legitimate duplicate
verified alias across multiple cubes and `semantic_provider=None` correctly refuses an automatic
pick. The generic eval fix supplies a bounded decision provider that may select only candidate IDs
already supplied by the production linker within the fixture's governed cube scope. No production
regex/fuzzy/alias heuristic was added.

### Day10 paid-gate validity blocker

Current budget authority is intentionally:

```text
max_total_manager_turns = 6
max_preacceptance_turns = 2
max_manager_turns       = 6
```

Git authority:
`a32ed3560002ac46ed5173d8ff152852878b455d`
(`fix(v2-day7): restore global Manager turn ceiling`).

The Product path necessarily consumes two pre-acceptance Manager turns. The existing Day8 live
provider-free proof demonstrates that even from an already-inspected trigger Evidence the causal
sequence needs five Research cognition actions. Actual Product bootstrap is stricter.

Thus the integrated root-cause debt cannot fit into the remaining four post-acceptance turns without
one of the following forbidden changes:
- silently raising budget,
- no longer counting pre-acceptance against the global total,
- skipping explicit Evidence inspection,
- turning trigger Evidence into SUPPORTS,
- borrowing unrelated USER_MUST Evidence.

Per H-053/H-054, the paid gate is therefore blocked BEFORE provider execution. Paid call count for
this blocked measurement remains zero.


---

## DAY10-G PRE-PAID HARDENING HARVEST — 2026-09-24

| ID | Mechanism / invariant | Class | Failure prevented / value | Current proof / owner |
|---|---|---|---|---|
| H-089 | Content/correlation identity is not turn authority identity. Fresh server-owned turn identity prevents cross-request/cross-tenant authority registry collisions. | MUST_PORT | identical user payload becoming the same accepted turn/run/initial lineage | Product `turn_ref` + fresh-turn/cross-tenant/continuation attacks; Day10 focused `35957173325` GREEN |
| H-090 | A fresh governed tool result already disclosed in the Manager cognition packet does not require a second cognition turn merely to mark it inspected. Explicit inspect remains for undisclosed historical Evidence. | MUST_PORT | paid inspect ceremony and wasted Manager budget without adding cognition | post-success fresh-delta disclosure rule + provider-failure/old-Evidence attacks |
| H-091 | Accepted fully-bound DIRECT USER_MUST tasks are scheduling/execution work, not necessarily Manager cognition. Deterministic execution must still cross ToolContract/permission/budget/trust boundaries. | SHOULD_PORT / architecture-dependent | Manager becoming a query-execution remote control; avoidable execution echo turns | `ResearchTaskInvocationCompiler` + `DeterministicResearchScheduler` + real-Wren root Product proof |
| H-092 | Hypothesis Evidence relation and Hypothesis status are distinct: status is deterministically reconciled from admitted Evidence relations; the model does not mint epistemic lifecycle truth. | MUST_PORT | OPEN hypotheses with admitted support/contradiction; model-owned status inflation | `HypothesisLedger.reconcile_status` + SUPPORTS/CONTRADICTS/mixed attacks |
| H-093 | ROOT_CAUSE obligation VERIFIED means the requested bounded investigation was fulfilled; it never means causation was confirmed. | MUST_PORT | completion laundering from candidate-cause Evidence into causal truth | `RootCauseObligationVerifier` + CompletionGate + real-Wren root Product micro-gate |
| H-094 | Model-authored hypothesis prose is cognition/audit material, not canonical user-facing factual report content. | MUST_PORT | valid Evidence laundering invented numbers/claims into ReportDocument | deterministic `EvidenceLinkedFindingBuilder` semantic rendering; `%27` attack |
| H-095 | Exactly-one accepted authority must be physically shared across Standard and Research at the Product boundary, not only guaranteed by router convention. | MUST_PORT | future routing/refactor bug committing both authority families for one turn | one ProductCoordinator-owned `AcceptedAuthorityRegistry`; cross-family conflict attack |

### D10-G cognition/effect split

```text
Manager cognition:
- propose material adaptive branch
- form hypothesis
- select material hypothesis next test
- relate new governed Evidence to hypothesis

Deterministic runtime:
- execute fully-bound seed tasks
- execute unique lossless ROOT_CAUSE bootstrap
- execute one admitted exact next-test
- execute one admitted exact branch
- record fresh-result disclosure after successful cognition
- reconcile hypothesis lifecycle
- verify bounded ROOT_CAUSE obligation
- terminate through CompletionGate

Trust plane:
- semantic truth
- QueryContract
- numeric truth
- Evidence
- epistemic ceiling
- completion
```

### G16 lower-bound receipt

Run:
`35957173325 = GREEN`.

```text
provider-free focused                  47 passed
real-Wren ROOT_CAUSE Product           1 passed
paid calls                              0

preacceptance cognition                 2
Research Manager cognition              4
Manager total                           6
global Manager ceiling                  6
headroom                                0

deterministic task executions           5
fresh Evidence disclosures              3
explicit historical Evidence inspect    0
redundant fresh inspect cognition        0
redundant execution-control cognition    0

paid structural status
STRUCTURALLY_ADMISSIBLE_AT_CEILING
```

The six-turn budget was not raised.

### Cancellation invariant

The deterministic scheduler uses the same Day7 `ResearchTaskRegistry` lifecycle and
`ResearchToolRunner` commit guard.

If cancellation becomes true before Evidence commit:

```text
governed query attempt may already be metered
ResearchTask -> cancelled
Evidence commit -> 0
late completion -> cannot resurrect task
```

Attempt accounting and Evidence authority are deliberately distinct.

### Metabase pattern refresh

Reference:
`metabase/metabase@fa7362a1e4792c2e83faffc11fba7f36c2dd49d4`.

Patterns harvested:
- tool output -> completed step -> working memory -> next cognition;
- fresh message identity -> UUID-like identity, not content hash;
- conversation lock + stale parent/retry validation -> fail closed;
- successful deterministic terminal state need not spend another model turn saying FINISH.

Dima keeps its stronger trust-plane owners and copies no Metabase runtime/source.

### Paid harness boundary

The integrated Day10 paid harness is prepared but unexecuted.

It is:
- manual `workflow_dispatch` only;
- one job, no matrix;
- explicit `CANONICAL_NS4` scope;
- explicit supervisor confirmation string;
- hard provider-call ceiling before first provider request;
- fixed role topology;
- maximum two Product turns (initial + one signed section continuation).

Preparing this harness does not close Day8 live debt and does not make Day10 FINAL GREEN.


---

## DAY10-H FINAL PRE-PAID SEAL HARVEST — 2026-09-24

| ID | Mechanism / invariant | Class | Failure prevented / value | Current proof / owner |
|---|---|---|---|---|
| H-096 | ROOT_CAUSE trigger Evidence may create a hypothesis but cannot by itself complete the investigation. Completion requires post-hypothesis Evidence produced by a linked completed governed next test. | MUST_PORT | trigger Evidence laundering into root completion without actually testing the hypothesis | `RootCauseObligationVerifier` linked-task provenance check + H2 A–G attacks + real-Wren root micro-gate |
| H-097 | ResearchDirective is policy, not USER_MUST. Completion-relevant conditional directives require typed disposition; authorization-only directives do not silently become hidden obligations. | MUST_PORT | conditional research policy permanently blocking finish or being retyped as fake business deliverable | `ResearchDirectiveDisposition`; ADAPT lifecycle; BROADEN non-blocking attack |
| H-098 | ADAPT_ON_EVIDENCE is accounted either by an admitted governed material branch or an explicit evidence-grounded NO_MATERIAL_DIRECTION disposition. | MUST_PORT | hidden adaptive work, fake branch completion, or unnecessary extra Manager cognition | branch execution -> APPLIED; typed no-branch admission -> NO_MATERIAL_DIRECTION; directive-bearing G16 |
| H-099 | Product content/correlation fingerprint is not Product turn/event identity. Event identity must be scoped by server-owned unique turn identity. | MUST_PORT | identical repeated user payloads sharing Product/UI telemetry identity | `ProductResponse.turn_ref`; turn-scoped `ProductEventSink`; repeated-request + stream one-turn attacks |

### Root-cause completion provenance

Permanent completion rule:

```text
trigger Evidence
→ hypothesis creation context only

ROOT_CAUSE VERIFIED
requires, for every accounted hypothesis:
  status != OPEN
  + non-empty next_test_task_refs
  + linked current governed ResearchTask COMPLETE
  + admitted relation Evidence whose EvidenceArtifact.task_id
    belongs to that linked COMPLETE next test
```

Status/relation alignment:

```text
SUPPORTED
→ post-test SUPPORTS relation required

REFUTED
→ post-test CONTRADICTS relation required

INCONCLUSIVE
→ completed next test + governed post-test relation/accounting required
```

A different Evidence ID is not enough; task provenance is structural.

`ROOT_CAUSE VERIFIED != CONFIRMED_CAUSE` remains permanent.

### ResearchDirective lifecycle

```text
USER_MUST
= business result owed to user

ResearchDirective
= conditional research policy / authorization
```

Completion-relevant `ADAPT_ON_EVIDENCE` runtime states:

```text
OPEN
APPLIED
NO_MATERIAL_DIRECTION
BLOCKED
```

`APPLIED` requires a governed executed/accounted branch and branch task refs.

`NO_MATERIAL_DIRECTION` requires:
- accepted directive ID/type/parent,
- current VERIFIED Evidence,
- Evidence inspected/disclosed,
- Evidence in directive parent obligation lineage,
- bounded reason,
- no new branch task,
- no fake Evidence/Finding.

`BROADEN_WITHIN_BUDGET` remains permission/policy. Its mere presence does not fabricate
work or block CompletionGate.

### Manager budget interpretation

```text
max_total_manager_turns = 6
max_preacceptance_turns  = 4
```

The preacceptance value `4` is a phase safety cap for at most two bounded
draft+coverage attempts. It is NOT additional Manager spend.

Canonical successful path remains:

```text
preacceptance actual = 2
Research cognition   = 4
Manager total        = 6
headroom             = 0
```

The seventh total Manager call fails closed.

### Product identity

```text
request_ref
= deterministic content/correlation fingerprint

turn_ref
= fresh server-owned Product turn identity

event_id
= hash(turn_ref + request_ref + governed transition identity)
```

Repeated identical requests therefore may keep the same `request_ref`, but must have different
`turn_ref` and different event-id sets. Re-emitting the same governed transition inside one
turn remains idempotent.

Streaming mints exactly one `turn_ref` and threads that same identity through:
router -> ProductEventSink -> ProductCoordinator -> ProductResponse.

### Final deterministic receipt

Product behavior SHA:

`3db7f8688a5598188ae70375f778d2bef90452cf`

Authoritative Day10-H run:

`35961399933`

```text
focused provider-free            65 passed
real-Wren ROOT_CAUSE Product     GREEN
G16 directive-bearing NS4        GREEN

directive_count                  1
directive_id                     R_ADAPT_ROOT
directive_type                   ADAPT_ON_EVIDENCE
directive_final_status           APPLIED
directive_accounting_evidence    runtime-observed VERIFIED Evidence
directive_branch_task_refs       non-empty governed branch refs

preacceptance calls              2
Research cognition               4
Manager total                    6
headroom                         0

root trigger-only completion     impossible
root fresh-test completion       proven
CONFIRMED_CAUSE                  0

paid workflow dispatched         NO
paid calls                       0
```

Affected trust-plane regressions:
- Day7 full focused `35960964752 = GREEN`
- Day8 focused `35960964807 = GREEN`

The manual paid Product-MVP workflow remains prepared but unexecuted.

---

## DAY10-J PAID-RED FORENSICS + STANDARD OMISSION ROUTING HARVEST — 2026-09-24

| ID | Mechanism / invariant | Class | Failure prevented / value | Current proof / owner |
|---|---|---|---|---|
| H-100 | A paid Product harness must preserve the exact Product terminal and underlying StandardLaneOutcome before aborting on a lane/status gate. | MUST_PORT | collapsing CLARIFY / UNSUPPORTED / FAILED / ACCEPTED into an undiagnosable "got STANDARD" artifact | eval-only CapturingStandardLane + diagnostic snapshot + controlled Standard structured-output capture |
| H-101 | RESEARCH_NEED_OMITTED is the only CoverageVeto issue that may force StandardLaneStatus.RESEARCH_REQUIRED. Other coverage veto kinds remain non-Research terminals. | MUST_PORT | silent loss of material Research intent or broad FAILED/CLARIFY/UNSUPPORTED -> Research fallback | StandardLaneEngine typed coverage routing + focused failure-family tests |
| H-102 | Standard -> Research transition carries zero rejected Standard semantics. Research receives the raw Product request and shared infrastructure context only. | MUST_PORT | rejected CandidateObligation / projection / semantic binding becoming hidden Research authority | ProductCoordinator transition seam + omission-route carry-over attack |
| H-103 | A malformed StandardIntentDraft gets at most one generic typed-contract repair. The repair contains no fixture phrase, expected capability, language token or business literal; second failure is terminal. | MUST_PORT | testcase-specific prompt repair, semantic guessing after schema failure, unbounded draft loops | max_draft_attempts=2 + DRAFT_CONTRACT_REJECTED generic feedback tests |
| H-104 | Correctly typed Research capability is routed by the existing deterministic RepresentabilityGate before CoverageVeto spends another cognition call. | MUST_PORT | redundant FAST coverage call and duplicated lane classifier | preliminary decide_bound proof + no-coverage correctly-typed Research attack |
| H-105 | AcceptedAuthorityRegistry is shared across Standard and Research; after successful Research acceptance the valid registry family is RESEARCH, not "empty". Cross-family XOR proves no Standard authority was accepted first. | MUST_PORT | false test oracle interpreting successful Research authority as Standard carry-over | strengthened real-Wren omission-veto routing sentinel |

### Paid RED forensic correction

Historical paid run:

```text
run                                   35963884332
tested SHA                            8c85996c16a4bcecd9332d9fd335e57f6bf3a69f
classification                        VALID RED

FAST_LANGUAGE                         1
RESEARCH_MANAGER                      0
SEMANTIC_LINKER                       0
TEMPORAL_NORMALIZER                   0
REPORT_NARRATOR                       0
TOTAL                                 1

Research entered                      NO
historical Standard terminal subtype  UNRESOLVED
previous MODEL_COGNITION root cause   NOT SEALED
paid authorization                    CONSUMED
```

One FAST call is inconsistent with a successful Standard ACCEPTED path at that SHA because
that path requires both the draft and StandardCoverageVeto structured calls. Therefore the
product RED is real, but the old artifact cannot prove which one-call Standard terminal
family occurred. That historical subtype remains UNRESOLVED; no inference is substituted
for missing measurement.

### D10-J routing law

```text
draft
→ exact-source validation
→ governed grounding

material semantic gap?
    CoverageVeto may test for omitted Research
    RESEARCH_NEED_OMITTED -> RESEARCH_REQUIRED
    otherwise -> CLARIFICATION_REQUIRED

control request?
    CoverageVeto may test for independently omitted Research
    RESEARCH_NEED_OMITTED -> RESEARCH_REQUIRED
    otherwise -> safe control/clarification terminal

no gap/control:
    RepresentabilityGate
    typed Research -> RESEARCH_REQUIRED without CoverageVeto

    otherwise CoverageVeto where needed
    RESEARCH_NEED_OMITTED -> RESEARCH_REQUIRED
    other VETO -> preserve correct non-Research failure/terminal
```

Coverage remains veto-only. It does not choose ROOT_CAUSE/RELATIONSHIP, mint a Research
obligation, mint a SemanticHandle, create AcceptedTurnContract or seal Standard authority.

### Bounded draft repair

A structured provider/API success may still fail StandardIntentDraft parse/validation.

Current bounded behavior:

```text
attempt 1 malformed
→ generic revision feedback only:
  DRAFT_CONTRACT_REJECTED
  typed response did not satisfy StandardIntentDraft

attempt 2 valid
→ continue normal deterministic routing

attempt 2 malformed
→ FAILED

Research fallback from draft-contract failure
→ forbidden
```

### D10-J proof receipt

Product behavior SHA:

a449bcfd62ede142ced7d2c9631fba2430534d62

Final deterministic / real-Wren run:

35967647254 = GREEN

```text
compile D10-J routing owners          GREEN
focused provider-free                96 passed
real-Wren omission-veto -> Research  1 passed
G16 provider-free rehearsal          GREEN

G16 preacceptance calls              2
G16 Research Manager calls           4
G16 Manager headroom                 0
G16 CONFIRMED_CAUSE                  0
G16 ADAPT_ON_EVIDENCE                APPLIED

paid calls                            0
```

Intermediate RED classification:
- 35967138289 / 35967181704: EVAL/HARNESS/FIXTURE stale invalid Research fixture;
- 35967487249 / 35967571343: test-oracle error about the shared authority registry;
- no Product patch was made from either failure family.

The historical paid authorization remains consumed. D10-J does not close Day8 live debt and
does not seal Day10 FINAL. A future paid remeasurement, if any, requires a new supervisor
decision.



### D10-L harvest additions

**H-106 — MUST_PORT**  
A source-grounded REQUIRED Research capability must be routed by deterministic Representability authority before Standard semantic grounding or control handling can preempt it.

**H-107 — MUST_PORT**  
`NON_AUTHORITATIVE_CONTROL_REQUEST` cannot override or block independently valid business authority; it never owns lane selection.

**H-108 — MUST_PORT**  
`CONVERSATION_REPAIR` and `NON_AUTHORITATIVE_CONTROL_REQUEST` are distinct control classes and must not share accidental terminal semantics.

**H-109 — SHOULD_PORT (performance + correctness)**  
Correctly typed Research routing must not spend Standard semantic-linker, coverage or Wren work after deterministic Research necessity is proven.

**H-110 — MUST_PORT**  
Standard CoverageVeto is an omission safety net for a still-Standard candidate; it must not run after deterministic typed capability authority already forbids Standard.

Evidence receipt: D10-K paid run `35970179887` exposed the ordering defect; D10-L deterministic proof `35972060988` is GREEN with 104 focused provider-free tests, both real-Wren routing paths, and zero paid calls.


---

## D10-N RESEARCH SEMANTIC APPLICABILITY HARVEST — 2026-09-24

| ID | Mechanism / invariant | Class | Failure prevented / value | Current proof / owner |
|---|---|---|---|---|
| H-111 | A capability-required semantic binding gap is not automatically a user clarification if bounded current-turn governed context can still supply non-authoritative candidate applicability. | MUST_PORT | premature clarification even though the same source message already contains sufficient governed semantic context | D10-N current-turn applicability recovery + preacceptance acceptance attacks |
| H-112 | Current-turn sibling semantic authority may be reused only as discovery context; an unresolved obligation receives authority only through a fresh bounded linker decision + SemanticBindingGate. | MUST_PORT | cross-obligation handle laundering / copied semantic authority | GovernedCurrentTurnCandidateGenerator + fresh source-bound binding tests |
| H-113 | Cross-obligation semantic context is current-message/current-tenant/current-context/current-attempt only and must never silently copy handles between obligations. | MUST_PORT | stale-turn, foreign-tenant, report-lineage or sibling provenance leakage | manager semantic adapter scoping + foreign/prior-turn/sensitive attacks |
| H-114 | Material semantic grounding errors should consume the cheapest bounded cognition layer capable of resolving them; do not spend an extra Manager turn when Semantic Linker cognition suffices. | SHOULD_PORT | Manager-budget failure caused by unnecessary redraft/replanning | semantic-linker recovery before clarification; global Manager ceiling unchanged |
| H-115 | A RED classification identifies the repair owner; it is not itself a reason to halt engineering. | MUST_PORT | repeated supervisor STOP cycles for developer-owned contract/eval/resolver defects | D10-N continuous RED→owner→root-fix→narrow-proof loop |

### Authority-preserving applicability law

```text
retrieval candidate
!= applicability

applicability
!= semantic authority

linker SELECT
!= semantic authority

SemanticBindingGate
= only owner that mints sem_* authority
```

D10-N recovery:

```text
current-message governed USER_SOURCE metric/dimension truth
→ bounded candidate applicability only
→ unresolved obligation exact source context
→ bounded linker SELECT | ABSTAIN
→ SemanticBindingGate
→ fresh source-bound sem_* edge
```

Never:

```text
missing ROOT_CAUSE metric
→ copy PERFORMANCE metric handle
```

Scope:
- metric/dimension only;
- same current message/tenant/context/attempt;
- sensitive candidates excluded;
- no filter/entity cross-owner reuse;
- no temporal/comparison cross-owner reuse;
- no prior conversation/report/run truth;
- no exact-ambiguity override;
- no same-set ABSTAIN retry;
- no cube-cooccurrence auto-bind.

### Metabase pattern cross-check

Reference pattern from current Metabase Exploration query planning:

```text
metadata hydration
→ metric/dimension applicability
→ candidate plan item
→ materialization
→ execution/result
```

Harvested principle only:

```text
known governed context should be available before declaring an operation impossible,
but candidate context is still not authority.
```

Dima did not import Metabase semantic matching or runtime execution.

### D10-N deterministic receipt

Semantic Product behavior SHA:

`8b2ea59045a87ec03d78517d6dbe653fcc9b14f6`

Final deterministic candidate SHA:

`7c5b8be2bc46178a0f8b4e33882223203f4c57cd`

```text
Day10  36035224902 = GREEN
  focused provider-free             106 passed
  semantic/preacceptance attacks     59 passed
  real-Wren Product/sentinel          3 passed
  G16 provider calls                  0
  G16 preacceptance                   2
  G16 Research cognition              4
  G16 Manager headroom                0
  G16 directive                       APPLIED
  G16 root_status                     VERIFIED
  G16 CONFIRMED_CAUSE                 0

Day8   36035224892 = GREEN
Day7   36035224835 = GREEN
```

D10-M paid run `36016509479` remains historical VALID RED and is not rewritten.

D10-N paid development envelope after deterministic closure:

```text
new paid dispatches used    0 / 2
new provider calls          0 / 30
```

Day8 live debt and Day10 FINAL remain OPEN until the integrated paid Product measurement proves the
full initial report + signed continuation chain. Day11 remains unauthorized.


---

## D10-O LIVE HARVEST — 2026-09-24

**H-116 — MUST_PORT**  
Current-turn applicability may hydrate governed metric/dimension candidates from one coherent current USER_SOURCE cube scope, but cross-domain context must not broaden candidate truth.

**H-117 — MUST_PORT**  
Applicability narrowing remains non-authoritative. Semantic Linker still owns SELECT vs ABSTAIN and SemanticBindingGate still owns new `sem_*` authority.

**H-118 — MUST_PORT**  
A model-authored semantic decomposition can be the first wrong transition. Safe resolver abstention after that point must not be repaired by forced candidate selection.

**H-119 — SHOULD_PORT**  
Track movement of the live failure frontier, not only final GREEN/RED. D10-O attempt 2 proved the applicability repair by newly grounding `Makine duruşları` and `bölüm` even though the Product turn remained RED.

**H-120 — MUST_PORT**  
Temporary measurement-trigger infrastructure must be removed after the bounded measurement envelope.

Receipts:

```text
attempt 1  run 36039697895  calls 4  RED
attempt 2  run 36041398308  calls 5  RED
total calls                           9
measurements                          2 / 2
```

Second-run blocker:

```text
source phrase:
"bölüm bazındaki performansı"

Research draft:
breakdown REQUIRED
  dimension = "bölüm"
  metric    = "performansı"

live result:
dimension = BOUND
metric candidate pool = 4 governed maintenance metrics
linker = ABSTAIN / NO_MATCH
material_grounding_gap = breakdown metric
```

Classification: `MODEL_COGNITION`.

Do not repair this by nearest-metric selection, retrieval ranking as truth, one/few-candidate auto-bind, phrase rules, fuzzy matching, required-kind weakening, BindingGate weakening, or Manager-budget increase.

Potential next bounded owner, subject to supervisor authorization: preacceptance revision policy for model-authored required-kind decomposition gaps. It should preserve exact source proof and semantic authority boundaries.


---

## D10-O METABASE REFERENCE AUDIT / SUPERVISOR DECISION NOTE — 2026-09-24

Reference upstream inspected:

`metabase/metabase@b6f625ed4b0c6e6716dbbd61b8691841e34d626d`

Relevant files:

- `src/metabase/metabot/tools/explorations.clj`
- `src/metabase/explorations/query_plan/context.clj`
- `src/metabase/explorations/query_plan/mechanical.clj`
- `src/metabase/metabot/agent/profiles.clj` / profile tests

### What the working Metabase flow actually separates

Metabase Exploration does not ask the planner to infer a metric identity from an ambiguous generic phrase.

Its research tool flow is structurally:

```text
list_research_metrics
→ choose explicit metric IDs
→ get_research_candidates(metric_ids)
→ expose only dimensions applicable to those already-chosen metrics
→ add_research_groups(metric_id, dimension_ids)
→ hydrate selected metric/dimension metadata
→ compute per-pair applicability
→ planner sees only applicable metric × dimension pairs
→ materialize
→ execute
```

`query_plan/context.clj` explicitly hydrates chosen metrics/dimensions and snapshots per-pair
applicability before the planner. Dimensions that resolve on no selected metric are dropped rather
than surfaced as planner noise.

The mechanical planner then iterates the already-computed applicability matrix; existence in the
catalog is not enough.

Metabot profiles independently enforce the analogous control-plane rule:

```text
resolved profile
→ advertised tool surface
→ capability/permission filtering
→ actual executable tool surface
```

### D10-O implication

The second D10-O live RED is not evidence that the bounded linker should be more willing to select.

Live receipt:

```text
source phrase              "bölüm bazındaki performansı"
draft breakdown dimension  "bölüm"
draft breakdown metric     "performansı"

current-turn applicability
→ 4 legitimate maintenance metrics

linker
→ ABSTAIN / NO_MATCH

material gap
→ breakdown requires metric
```

This is a model-authored decomposition problem upstream of semantic authority.

The closest safe Dima analogue to the Metabase pattern is therefore:

```text
Research draft
→ exact-source validation
→ governed semantic grounding
→ material required-kind gap

if the gap is caused by model-authored decomposition
and current exact source already contains grounded governed semantic material:
    one bounded Research-draft revision
    with typed MATERIAL_GROUNDING_REJECTED feedback
    containing only:
      - obligation/capability
      - missing required kind
      - exact source surfaces
      - safe grounding summary / already-grounded kinds
      - instruction to re-express intent from source evidence only

revision
→ exact-source validation again
→ ordinary semantic linker
→ SemanticBindingGate
→ contract validity

second unresolved material gap
→ CLARIFICATION_REQUIRED
```

The revision must NOT receive canonical IDs, candidate IDs, semantic handles as truth, SQL, or an
instruction to choose one of the four candidates.

It may restructure the user intent only when the exact current message supports that structure.
For example, a broad breakdown phrase may be re-expressed around separately source-grounded metrics
already named by the user, but only if the revised obligation remains exact-source-valid.

### New harvested invariants

**H-121 — MUST_PORT**  
Metric identity must be established before metric/dimension applicability can safely constrain
planning. Applicability may narrow valid combinations; it must not invent metric identity.

**H-122 — MUST_PORT**  
A linker ABSTAIN over multiple applicable candidates is a valid semantic outcome, not a resolver
failure. Never convert it into nearest/top-1 truth.

**H-123 — SHOULD_PORT**  
A model-authored required-kind decomposition gap should consume at most one bounded typed draft
revision before becoming user clarification, when exact current source already contains governed
semantic material that can support a different valid decomposition.

**H-124 — MUST_PORT**  
Any such revision is cognition repair only. It must re-enter exact-source validation and the normal
Semantic Linker → SemanticBindingGate authority path; no semantic handle/candidate authority is
copied into the revised obligation.

**H-125 — SHOULD_PORT**  
Planner/agent advertised capability surfaces should be derived from the same executable profile or
capability registry so the model is not invited to express work the runtime cannot actually admit.

### Current boundary

No Product code was changed from this reference audit.

```text
D10-O paid measurements     2 / 2
D10-O provider calls        9 / 30
third paid measurement      NOT AUTHORIZED

Day8 live debt              OPEN
Day10 FINAL                 OPEN
Day11                       NOT AUTHORIZED
```

Supervisor decision required before implementing the bounded preacceptance-revision owner described
above, because the D10-O two-measurement TRUE STOP boundary has been reached.
