# WREN RESEARCH HARVEST MATRIX — DIMA V1 PHASE 1

Status: PATTERN HARVEST ONLY  
Date: 2026-09-27  
Wren reference branch observed: `feat/ask-v2-mvp@61f711c1f201b401c64fd9043438629db582b727`

This matrix imports no Wren runtime or source into the Metabase V1 product. It records only
research/epistemic patterns that can be expressed through existing or minimally extended Dima
owners.

Classification vocabulary:
- `ADOPT_PATTERN`
- `COMPOSE_EXISTING`
- `ALREADY_PRESENT`
- `REJECT`

## 1. Matrix

| Wren concept | Problem it solves | Existing Dima equivalent | Gap | Decision | Exact Dima owner | Required contract delta | Why no code/runtime import is required |
|---|---|---|---|---|---|---|---|
| AcceptedTurnContract | freezes what the current user turn materially asked for and prevents silent scope loss | ResearchBrief + ResearchScope + intake catalog | no first-class turn scope version/mutation identity | ADOPT_PATTERN | Research entry/scope contract | TurnScopeContract + ScopeVersion + typed ScopeMutation | contract shape is small and engine-independent; Wren semantic/runtime code is unnecessary |
| Research Goal / Task split | separates user/research goal authority from executable work authority | ResearchBrief questions + ProductInvestigationRequirement + P17 task lifecycle | split exists but is not uniformly named/exposed as V1 task authority | COMPOSE_EXISTING | P14 + Product routing + P17 | preserve goal authority; materialize only bounded investigation work where needed | current Dima already has durable goal and investigation task owners |
| ManagerActionSet | gives model only state-legal cognitive moves while server owns executable identities | InvestigationActionProfile + P17 validator | current provider still emits several machine/bookkeeping IDs | ADOPT_PATTERN | P17 | semantic-only provider proposal; deterministic identity binding; one repair | Dima already computes legal actions; only the server-bound-choice pattern is needed |
| Adaptive Branch | follows new material Evidence without turning the model into query planner | P17 InvestigationGraph + ProductInvestigationRequirement FOLLOW_VERIFIED_MATERIAL | mostly present; scope version and V1 max-depth/information-gain rules missing | COMPOSE_EXISTING | P17 | scope binding + hard max 3 + typed gain/stop rules | existing branch graph/tasks are already durable |
| HypothesisLedger | keeps competing hypotheses explicit and Evidence-linked | P19 hypothesis + grounding + assessment | current P19 lacks V1 NextTestRequest/scope-version recursive loop | COMPOSE_EXISTING | P19 | add minimum recursive discrimination contract; retain current durable P19 records | current P19 already owns hypotheses/groundings/assessment |
| Counter-evidence | prevents one-sided confirmation and supports contested conclusions | P16 CHALLENGES links + P17 SEEK_COUNTER_EVIDENCE + P19 CHALLENGES grounding | no fundamental gap | ALREADY_PRESENT | P16/P17/P19 | affected regression only | three sealed Dima owners already model counter-evidence explicitly |
| Discriminating Test | asks for the next piece of Evidence that can separate competing hypotheses | P17 TEST_DISCRIMINATING_EVIDENCE intent | P19 cannot yet emit a typed request back to P17 | ADOPT_PATTERN | P19 need + P17 execution legality, Product coordination | typed NextTestRequest + no-gain/data/duplicate gate | only the recursive contract pattern is needed; Metabase remains analytical engine |
| CompletionGate | prevents “looks done” completion when mandatory obligations are missing | ResearchBrief.must_requirement_ids + owner-scoped P14/P20 accounting + Product requirement projection | final V1 requirement disposition vocabulary/gate incomplete | COMPOSE_EXISTING | Product completion contract | FULFILLED/LIMITED/UNSUPPORTED/INCONCLUSIVE final accounting | existing immutable user contract and report accounting already provide most truth |
| Research Trace | makes adaptive reasoning auditable without treating hidden reasoning as authority | P17 durable ResearchReasoningStep / task store / Product trace | needs explicit scope-version and V1 next-test/stop semantics | COMPOSE_EXISTING | P17 | bind scope version and typed recursive reasons | current Dima durable trace already exists |

---

## 2. Detailed harvest notes

### 2.1 AcceptedTurnContract → TurnScopeContract

Wren's useful idea is not its turn implementation; it is the invariant that one accepted turn has
a durable material contract and follow-up mutation produces a new contract rather than silently
rewriting the prior one.

Dima already owns raw-language interpretation in Research Intake and the immutable
`ResearchBrief`. Therefore:

`ADOPT_PATTERN`, not Wren class/code.

Dima V1 delta:
- `ScopeVersion`;
- `TurnScopeContract`;
- `ScopeMutation`;
- lineage between prior/current scope versions.

Rejected Wren aspects:
- any Wren semantic authority;
- any Wren query/SQL path.

### 2.2 Research Goal / Task split

Wren's sealed rule `RESEARCH GOAL AUTHORITY != EXECUTABLE RESEARCH TASK AUTHORITY` is useful.
Dima already has the equivalent ownership separation:
- accepted Research questions in P14;
- Product investigation requirement routing;
- P17 durable investigation tasks.

Therefore `COMPOSE_EXISTING`.
Do not add a parallel Wren-style task registry merely for naming symmetry.

### 2.3 ManagerActionSet

The strongest harvest is server-bound action identity.

Wren's action set projects executable/legal action instances from authoritative state before model
choice. Dima's `InvestigationActionProfile` already projects legal intent/parent/branch behavior,
so a second ManagerActionSet would be duplicate authority.

The delta is to stop making the model echo server bookkeeping identities. Dima can retain its P17
action profile and bind the selected semantic move to deterministic state identities.

Decision: `ADOPT_PATTERN` inside existing P17, never source import.

### 2.4 Adaptive Branch

Dima P17 already has:
- branch graph;
- open/stopped branch identities;
- parent/child reasoning steps;
- legal STOP_BRANCH / STOP_INVESTIGATION;
- Product adaptive requirement over verified material.

Decision: `COMPOSE_EXISTING`.

Only V1 contracts missing from the roadmap are added:
scope version, hard max depth 3, typed information-gain/stop rules.

### 2.5 HypothesisLedger

Wren proves a useful pattern:
- hypothesis identity;
- governed Evidence links;
- contradictory Evidence;
- next-test linkage;
- no fake Evidence/task identities.

Dima P19 already has durable hypothesis / grounding / assessment records and stronger production
epistemic boundaries than importing the Wren ledger wholesale.

Decision: `COMPOSE_EXISTING`.

The useful missing pattern is the typed discriminating-test request, not the Wren ledger/runtime.

### 2.6 Counter-evidence

Dima already has:
- P16 `ClaimEvidenceRelation.CHALLENGES`;
- P17 `SEEK_COUNTER_EVIDENCE`;
- P19 `GroundingRelation.CHALLENGES`;
- P19 provider rule that challenge grounding cannot be hidden.

Decision: `ALREADY_PRESENT`.

No new owner.

### 2.7 Discriminating Test

Dima has P17's action name but not the end-to-end epistemic loop.
Wren demonstrates the value of an explicit next-test contract linked to a hypothesis and governed
Evidence.

Decision: `ADOPT_PATTERN`.

Dima implementation must be:
`P19 unresolved ambiguity → typed NextTestRequest → existing P17 legality → Metabase → Evidence → P19 reevaluation`.

No Wren dry-plan/query code is involved.

### 2.8 CompletionGate

Dima already preserves exact USER_MUST IDs and separates P14 analytical completion from P20
presentation fulfillment. That is the correct foundation.

Decision: `COMPOSE_EXISTING`.

The V1 delta is one final Product completion disposition vocabulary and gate. Do not port Wren's
CompletionGate class.

### 2.9 Research Trace

P17 already persists reasoning steps/tasks, branch identity, inspected Evidence/material,
proposal fingerprint and terminal state.

Decision: `COMPOSE_EXISTING`.

V1 adds only scope-version and recursive-discrimination semantics needed for audit.

---

## 3. Explicit rejects

The following Wren surfaces are `REJECT` for Dima V1:

| Surface | Decision | Reason |
|---|---|---|
| Wren runtime | REJECT | engine decision is closed |
| Wren SQL/query engine | REJECT | Metabase/Metabot is canonical analytical engine |
| Wren semantic authority | REJECT | would create duplicate analytical truth |
| Wren query planner / dry-plan runtime | REJECT | would create dual planning/engine surface |
| exact-surface gating | REJECT | V1 accepts material request invariants, not benchmark/query-shape cloning |
| Wren model cascade | REJECT | V1 topology remains Luna-only unless separately authorized |
| wholesale Wren source | REJECT | pattern harvest only |
| Wren provider-specific IDs/contracts | REJECT | Dima owns its own durable identities |

---

## 4. Pattern-to-owner convergence rule

No harvested concept may create a new authority if an existing Dima owner can express the invariant.

Canonical convergence:

```text
AcceptedTurnContract pattern
  → Research scope contract

ManagerActionSet pattern
  → existing P17 InvestigationActionProfile

Adaptive Branch
  → existing P17 InvestigationGraph

HypothesisLedger pattern
  → existing P19 hypothesis/grounding/assessment

Counter-evidence
  → existing P16/P17/P19 Evidence relations

Discriminating Test
  → new typed seam between existing P19 and P17

CompletionGate
  → Product projection over immutable ResearchBrief + owner states

Research Trace
  → existing P17 durable reasoning store
```

This is convergence, not a second brain.

---

## 5. Harvest exit

The harvest is complete for the nine mandated concepts.

Code/runtime import required: **none**.

Wren remains a historical/reference research architecture. All accepted patterns are implemented,
if needed, through Dima's current owners over the pinned Metabase/Metabot engine.
