# DIMA + METABASE — CURRENT PRODUCT PLAN OVERLAY

**Authority:** DMP-DEC-0044  
**Date:** 2026-09-24  
**Role:** Binding forward-development overlay for P13+.

The sealed historical roadmap
`backend/belgeler/metabase/DIMA_METABASE_NIHAI_UYGULAMA_YOL_HARITASI.md`
remains byte-for-byte immutable for audit/governance. Where its older P13+ language conflicts with
this file or DMP-DEC-0044, this current plan is the forward implementation authority.

---

## 1. Product sentence

```text
DIMA = institutional intelligence / decision operating layer
ON TOP OF
METABASE + METABOT = native analytics substrate
```

The product is not a second BI/query engine.

Metabase/Metabot supply native analytical capability. Dima turns company context + native analytical
results into Research, Evidence, Findings, Decisions, Actions and Memory.

---

## 2. Permanent native inheritance contract

```text
USE_NATIVE
→ COMPOSE_NATIVE
→ WRAP_NATIVE
→ HOOK_NATIVE
→ DIMA_OWNS
```

Before building any Dima analytical mechanism ask:

```text
Does pinned Metabase/Metabot already own this capability?
```

If yes, use it in place.

Do not port native filter, breakout, ranking, temporal, repair, query-lifecycle, visualization,
Explorations or permission machinery into Python.

`DIMA_OWNS` requires a measured product-specific gap that native Metabase does not own.

---

## 3. Native substrate immutability

```text
NATIVE_SUBSTRATE_IMMUTABILITY = BINDING
NATIVE_CORE_PATCH              = EXCEPTION ONLY
```

Normal Dima integration work does not modify Metabot prompts/profiles/skills, Metabase Lib, Query
Processor or drivers.

If a native capability works without Dima but fails through Dima, investigate Dima first.

Even when a pinned-native defect is independently reproduced, prefer a reversible Dima integration
compatibility seam over owning a permanent native-core fork.

---

## 4. Ownership split — no duplicate truth engine

For the native Metabase path:

```text
METABASE + METABOT OWN
- persisted native Metric / Model analytical definitions
- field/query analytical semantics
- analytical cognition and strategy
- native query construction / repair
- filters / breakouts / ranking / temporal mechanics
- MBQL / Query Processor / drivers
- native data-permission enforcement
- dashboards / visualization / Explorations / native lifecycle

DIMA OWNS
- stable business concept identity
- company terminology / aliases / sector context
- mapping concept → exact engine resource/version
- material business relationship policy when product-specific
- Research objectives / obligations / hypotheses / stopping
- claim lineage / Evidence epistemic state
- Findings / Root Cause epistemic promotion
- Decision / Action / Outcome / Memory
- product-level tenant/principal/policy binding
```

Do not independently author the same analytical formula in both systems.

Existing P7/P8/P9 `DimaSemanticSpec` / DIMA_MANAGED resources remain valid sealed migration and
compatibility assets. Do not delete or mass-refactor them during P14. New work must not expand them
into a shadow Metric/Model/query-definition engine.

A later explicit semantic-ownership migration may narrow DimaSemanticSpec toward:

```text
DIMA BUSINESS ONTOLOGY / ENGINE MAPPING
```

but that migration is not part of P14 foundation and may not silently rewrite sealed semantics.

---

## 5. Security split

Metabase + DB enforce native data access.

Dima:
- binds tenant/principal to the correct native engine subject;
- retains P10 access/provenance identity;
- owns Research/Evidence/Decision/Action sharing and approval policy.

Do not build a generic second RLS/CLS engine in Dima.

P10 is a binding/provenance contract, not a replacement database-permission system.

---

## 6. Evidence split

```text
ENGINE
→ proves what native analytical resource/query executed
→ produces result + execution identity

DIMA
→ binds result to a Research obligation / claim
→ records principal/scope/resource lineage
→ assigns Evidence epistemic state
→ promotes Findings/Hypotheses/Decisions only when justified
```

Evidence is not a second MBQL interpreter.

`VERIFIED` still requires no unresolved material ambiguity. Unsupported native representation or
unresolved engine-resource mapping must fail closed or become an explicit limitation.

---

## 7. P13 final disposition

P13's purpose was to prove that native Metabot analytics can cross Dima's identity/provenance/
execution/Evidence boundary safely.

That proof is sufficient.

```text
P13A                               = GREEN
P13B                               = GREEN
P13C                               = GREEN

P13D BREAKDOWN LIVE                = GREEN / VERIFIED
P13D TOP-N RANKING LIVE            = GREEN / VERIFIED
P13D PERIOD COMPARISON             = DEFERRED COMPATIBILITY GAP / NOT GREEN

P13 STANDARD TRUST BASELINE        = SEALED
P13 OPERATOR-FAMILY GENERALIZATION = STOPPED
P13E / P13F                        = DO NOT CREATE
```

Do not claim the original three-case P13D slice fully GREEN.

The comparison gap is explicit technical debt, not a global product blocker.

---

## 8. Current comparison debt

Certified engine:

```text
SHA           = cbe313af9ac2d5960f662068e433d328d896fb06
release       = 0.63.18-dima.6
certification = 36042062775 SUCCESS
digest        = sha256:40e9a44be49904de3ddf12d4683c768e70955851c10a928a9c8f7d8f60780353
```

Final P13D live:

```text
run = 36046994140
```

Breakdown and ranking completed with exact fingerprint chains, QueryReceipts, independent oracles and
VERIFIED Evidence.

Comparison fail-closed at Dima native compatibility with
`NATIVE_QUERY_RUNTIME_REPRESENTATION_UNSUPPORTED`.

Policy:

- do not cut dima.7 merely to complete the old certification table;
- do not spend another Luna to rediscover the representation;
- if real P14/product work hits it materially, capture the exact native representation;
- fix only the smallest reversible Dima compatibility seam provider-free;
- never rewrite the native query to force success;
- native core remains immutable by default.

---

## 9. P14 — Native Research — FOUNDATION GREEN / CONTINUE PRODUCT INTEGRATION

P14 is no longer blocked by comparison certification.

The first coherent Research foundation vertical is already sealed GREEN:

```text
implementation             = a8c7b5d2b922e85ff046c6c7ce1bfce92aa13552
integrated exact-occurrence = bab26fe51978929ace44f7703543f78099c692ce
provider-free               = 36052728145 SUCCESS
P14 focused                 = 6 passed
P13D/P10/P5 regression      = 69 passed
engine build                = 0
model calls                 = 0
native Metabase/Metabot diff= 0
```

Current Research foundation owns:

```text
ResearchSession
ResearchObligation
Hypothesis
CounterEvidenceRef
EvidenceRef
ResearchBudget
StoppingState
NativeMetabotConversationRef
ResearchLimitation
```

The integrated provider-free flow already proves:

```text
Research obligation
→ native Metabot delegation identity
→ existing P13 authorization
→ exact native occurrence execution
→ P10 access identity
→ P5 QueryReceipt
→ VERIFIED Evidence
→ Research state
```

ResearchManager does not see or author raw MBQL/SQL as analytical strategy.

It owns **what must be investigated and what the evidence means**, not **how Metabase constructs the
query**.

Next coherent P14 slice is product-level integration, not another foundation rewrite:

1. wire the Research aggregate into the real Ask/Research orchestration boundary;
2. durably correlate ResearchSession with a real native Metabot conversation/session;
3. delegate governed obligations to the native engine;
4. reuse the same P13 exact-occurrence/P10/P5/Evidence chain for every material execution;
5. add durable resume/correlation and obligation-scoped limitations;
6. keep engine builds and model calls at zero until a real native Research bridge exists and one
   bounded live evaluation can change a product/architecture decision.

---

## 10. P15 — Native Metabase Explorations Integration

Use native Explorations in place.

Do not harvest/rewrite its primitives.

Reuse where supported:

- metric-dimension applicability;
- variants;
- top-N + Other;
- temporal patterns;
- interestingness;
- runner;
- stored results;
- cancellation/restart;
- idempotency;
- derived permissions;
- native query/result lifecycle.

Dima binds these to Research obligations, Evidence and decision context.

```text
Metabase interestingness
!=
Dima VERIFIED Finding
```

---

## 11. P16 — Evidence / claim lineage

Evolve Evidence around:

```text
claim
research obligation
engine resource
native occurrence / execution
result
scope
principal
freshness
receipt
epistemic state
```

Do not add operator-level semantic interpreters.

---

## 12. P17 — Research Manager maturation

Add:
- obligation ledger;
- inspect/replan loop;
- bounded budgets;
- no-progress;
- counter-evidence;
- stopping/completion;
- durable resume.

The loop is agentic cognition, not a deterministic:
`trend → breakdown → segment → compare`
state machine.

---

## 13. P18 — Relationships

Metabase owns native join mechanics.

Dima owns only material business relationship policy that is company/sector specific and required for
safe interpretation.

Do not mirror Metabase's join planner.

Unapproved material relationship use may block VERIFIED promotion, but physical/native join
representation is not reimplemented in Dima.

---

## 14. P19–P21 — Dima differentiation

P19:
Hypothesis / Root Cause epistemics.

P20:
ReportDocument / claim-to-evidence synthesis.

P21:
DecisionBrief / options / tradeoffs / recommendation / limitation.

These are core Dima product value and should receive development effort instead of additional P13
operator certification.

---

## 15. Product direction after P21

The broader product becomes:

```text
CONNECT
→ UNDERSTAND
→ WATCH
→ AUDIT
→ THINK / INVESTIGATE
→ DECIDE
→ ACT
→ REMEMBER
```

Metabase remains strongest in analytical execution/BI surfaces.

Dima adds company/sector intelligence, continuous monitoring, Research, optimization, decisions,
actions and institutional memory.

Chat is one interface to this brain, not the product itself.

---

## 16. One Ask surface

Do not expose "Metabase mode" versus "Dima mode" to the user.

There is one Dima Ask/Research surface.

Internally a native execution either:
- satisfies the material binding/provenance requirements and can support VERIFIED Evidence;
- fails closed / records an explicit limitation.

A future scoped-evidence state may be introduced only by an explicit Evidence-plane decision. Do not
silently downgrade truth requirements.

---

## 17. Speed and test economy

Permanent cadence:

```text
build coherent product slice
→ focused owner tests
→ one provider-free seal
→ model/live only if cognition changed and the result changes a decision
→ continue
```

Do not:
- rerun P13B/P13C;
- rebuild unchanged engine;
- certify every Metabase operator;
- run Sol/C1/full corpus for Dima state-model changes;
- stop after every small commit.

---

## 18. STOP conditions

Stop for supervisor only if:

1. native Metabot/QP/driver/Lib modification appears necessary;
2. a second analytics planner is being introduced;
3. a second semantic formula owner is being introduced;
4. a second security/receipt authority is being introduced;
5. silent wrong reaches VERIFIED Evidence;
6. a broad paid/model corpus is proposed without a decision-changing hypothesis;
7. destructive P7/P9 semantic ownership migration is proposed.

Ordinary P14 implementation progress is not a STOP.

---

## 19. Immediate developer objective

Do not touch engine first.

Do not fix comparison first.

Do not rebuild the already-GREEN P14 foundation.

Continue P14 at the real product boundary.

Return after substantial progress:

```text
real Ask/Research orchestration
+
durable ResearchSession ↔ native Metabot conversation correlation
+
existing P13 exact-occurrence execution reuse
+
P10 / P5 / Evidence reuse
+
provider-free Research → receipted Evidence → Research state path
```

or after one genuine STOP condition.

Ordinary P14 implementation progress is not a STOP.
