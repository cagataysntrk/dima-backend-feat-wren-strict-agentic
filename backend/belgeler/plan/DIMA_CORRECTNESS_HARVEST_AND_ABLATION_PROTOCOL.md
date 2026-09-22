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
