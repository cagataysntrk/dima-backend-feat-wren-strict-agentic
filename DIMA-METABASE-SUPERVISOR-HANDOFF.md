# DIMA METABASE PLATFORM — SUPERVISOR HANDOFF

**Authoritative supervisor takeover — 2026-09-24**

Audience: the incoming supervisor knows the project approximately through early P13/P13B but does not
know the work completed after that point.

This file is the current supervisor onboarding authority together with:
1. `backend/belgeler/metabase/DIMA_METABASE_CURRENT_PRODUCT_PLAN.md`;
2. the tail of `DIMA-METABASE-DURUM.md`;
3. DMP-DEC-0044 and DMP-DEC-0045 in the decision receipts;
4. exact Git SHAs / certified workflow artifacts.

The sealed historical roadmap remains audit history. It is not the sole P13+ implementation authority.

---

## 0. Current exact state

Platform:

```text
repo       = cagataysntrk/dima-backend-feat-wren-strict-agentic
branch     = feat/dima-metabase-platform
HEAD       = 6bce25331da3e0c467b49701ba77f90059fd8b21
governance = 36052986798 SUCCESS
```

Certified engine:

```text
repo          = UpcyTech/dima-metabase-engine
main          = cbe313af9ac2d5960f662068e433d328d896fb06
release       = 0.63.18-dima.6
upstream      = 2ba2485c78d7e00a9a25f82c00fc201da71590c4
certification = 36042062775 SUCCESS
digest        = sha256:40e9a44be49904de3ddf12d4683c768e70955851c10a928a9c8f7d8f60780353
build identity= github-actions:36042062775:cbe313af9ac2d5960f662068e433d328d896fb06
```

P14 foundation:

```text
implementation             = a8c7b5d2b922e85ff046c6c7ce1bfce92aa13552
integrated trust proof      = bab26fe51978929ace44f7703543f78099c692ce
provider-free               = 36052728145 SUCCESS
governance                  = 36052727756 SUCCESS
P14 focused                 = 6 passed
P13D/P10/P5 regression      = 69 passed
new engine build            = 0
model calls                 = 0
native Metabase/Metabot diff= 0
```

---

## 1. The architecture changed after early P13

Do not continue the old mental model that Dima must independently certify or re-model every Metabase
query operator.

The binding product sentence is:

```text
DIMA
= institutional intelligence / decision operating layer

ON TOP OF

METABASE + METABOT
= native analytics substrate
```

Metabase + Metabot own:
- native Metric / Model analytical definitions;
- field/query analytical semantics;
- analytical cognition and strategy;
- native query construction and repair;
- filters, breakouts, ranking, temporal mechanics and joins;
- MBQL / Query Processor / drivers;
- native data-permission enforcement;
- dashboards, visualization, Explorations and native lifecycle.

Dima owns:
- stable business concept identity;
- company terminology, aliases and sector context;
- mapping concept -> exact engine resource/version;
- product-specific material relationship policy;
- Research objectives, obligations, hypotheses, counter-evidence and stopping;
- claim lineage / Evidence epistemic state;
- Findings / Root Cause epistemic promotion;
- Decision / Action / Outcome / Memory;
- product-level tenant/principal/policy binding.

Do not independently author the same analytical formula in both systems.

---

## 2. Permanent reuse order

```text
USE_NATIVE
→ COMPOSE_NATIVE
→ WRAP_NATIVE
→ HOOK_NATIVE
→ DIMA_OWNS
```

Before approving a new Dima analytical mechanism ask:

```text
Does pinned Metabase/Metabot already own this capability?
```

If yes, use it in place.

`DIMA_OWNS` requires a measured product-specific gap, not preference.

---

## 3. Native substrate immutability

```text
NATIVE_SUBSTRATE_IMMUTABILITY = BINDING
NATIVE_CORE_PATCH              = EXCEPTION ONLY
DIMA_FIRST_FAULT_PRESUMPTION   = BINDING
```

Normal product development must not modify:
- Metabot prompts/profiles/skills;
- Metabot agent-loop cognition;
- Metabase Lib;
- Query Processor;
- drivers;
- native query repair/search semantics.

If a native capability works normally but fails through Dima, inspect the Dima integration seam first.

Even when a pinned-native defect is independently reproduced, prefer a reversible Dima-owned
compatibility seam to owning a permanent native-core fork.

Any native-core patch requires a separate supervisor decision.

---

## 4. Why P13 is now closed as a development loop

P13 proved the material trust boundary, not every possible query grammar form.

Closed evidence includes:
- real native Metabot query authoring;
- DIMA-managed/native metric path;
- textual equality filter;
- tenant/principal binding;
- exact occurrence identity;
- exact execution;
- P10 access identity;
- P5 QueryReceipt;
- VERIFIED Evidence;
- independent DB oracles;
- immutable certified engine image;
- no Wren/raw-SQL/Agent-API/admin analytical fallback.

Current truthful state:

```text
P13A                         = GREEN
P13B                         = GREEN
P13C                         = GREEN
P13D BREAKDOWN live          = GREEN / VERIFIED
P13D TOP-N RANKING live      = GREEN / VERIFIED
P13D PERIOD COMPARISON       = DEFERRED COMPATIBILITY GAP / NOT GREEN

P13 STANDARD TRUST BASELINE  = SEALED
P13 OPERATOR GENERALIZATION  = STOPPED
P13E / P13F                  = DO NOT CREATE
```

Do not claim the original P13D three-case slice fully GREEN.

The comparison debt is explicit and real, but it is not a global product-development blocker.

---

## 5. P13D comparison debt

Final P13D live:

```text
run      = 36046994140 FAILURE
artifact = 10829286413
```

BREAKDOWN and RANKING completed with:
- exact attested=authorized=executed=receipted fingerprints;
- correct independent oracles;
- QueryReceipts;
- VERIFIED Evidence.

COMPARISON failed closed before authorization/execution with:

```text
NATIVE_QUERY_RUNTIME_REPRESENTATION_UNSUPPORTED
```

Policy:
- do not cut dima.7 merely to complete an old certification table;
- do not spend another Luna simply to rediscover representation;
- do not broaden the compatibility codec speculatively;
- do not rewrite the query;
- do not patch native core;
- if real P14/product work materially hits the same gap, capture the exact native representation and
  open only the smallest reversible Dima-local compatibility fix.

Independent Research obligations may continue while a materially unsupported execution becomes an
explicit obligation-scoped Research limitation.

---

## 6. DimaSemanticSpec role after DMP-DEC-0044

Existing P7/P8/P9 `DimaSemanticSpec` and DIMA_MANAGED resources are sealed compatibility/migration
assets. Do not delete or mass-refactor them during current P14 work.

But do not expand them into a shadow Metabase Metric/Model/query-definition engine.

Forward conceptual direction:

```text
DIMA BUSINESS ONTOLOGY / ENGINE MAPPING
```

Dima should increasingly retain:
- stable business concept identity;
- aliases / company terminology;
- sector meaning;
- decision relevance;
- exact engine-resource mapping/version.

Metabase should own the native analytical definition.

Any destructive semantic-ownership migration is a separate future milestone and STOP condition.

---

## 7. Evidence doctrine

```text
ENGINE
→ proves which native analytical resource/query executed
→ returns result + execution identity

DIMA
→ binds the result to a Research obligation / claim
→ records principal/scope/resource lineage
→ assigns Evidence epistemic state
→ promotes Findings/Hypotheses/Decisions only when justified
```

Short form:

```text
ENGINE PROVES ANALYTICS
DIMA PROVES CLAIM LINEAGE
```

Evidence is not a second MBQL interpreter.

---

## 8. Security doctrine

Metabase + DB own native data-access enforcement.

Dima:
- binds the correct tenant/principal to the native engine subject;
- retains P10 access/provenance identity;
- owns Research/Evidence/Decision/Action sharing and approval policy.

Do not build a generic second RLS/CLS engine.

---

## 9. P14 is already started and foundation is GREEN

Current owner:

```text
backend/app/v3/research.py
```

The foundation introduces durable/versioned:
- ResearchSession;
- ResearchObligation;
- Hypothesis;
- CounterEvidenceRef;
- EvidenceRef;
- ResearchBudget;
- StoppingState;
- NativeMetabotConversationRef;
- ResearchLimitation.

It does not contain an SQL/MBQL generator/parser, ranking/comparison/temporal planner, query repairer,
second receipt system, second access authority or Wren/Agent-API/raw-SQL fallback.

Provider-free integrated proof reuses:

```text
Research obligation
→ native Metabot delegation identity
→ existing P13 authorization
→ exact native occurrence execution
→ existing P10 access identity
→ existing P5 QueryReceipt
→ VERIFIED Evidence
→ Research state
```

The native HTTP boundary is mocked in the current provider-free proof; P13/P10/P5/Evidence are the
real production owners under test.

---

## 10. Immediate next P14 objective

Do not rebuild the foundation.

Continue with one coherent product-level Research/Ask integration slice:

1. wire ResearchSession into the real product Research/Ask orchestration boundary;
2. correlate a durable Research session with a real native Metabot conversation/session;
3. delegate governed Research obligations to the native engine instead of creating analytical tools in
   ResearchManager;
4. route every material native execution through the existing P13 exact-occurrence path;
5. admit only receipted, eligible Evidence into Research state;
6. implement durable resume/correlation without reparsing raw user prompts into new authority;
7. preserve obligation-scoped limitations so one unsupported material execution does not erase valid
   independent evidence;
8. keep model calls at zero until a real native Research bridge is coherent and one bounded live
   evaluation can change a product/architecture decision.

Do not stop after tiny commits.

---

## 11. P15 and later direction

P15 is:

```text
NATIVE METABASE EXPLORATIONS INTEGRATION
```

not primitive harvesting.

Use native Explorations in place:
- applicability;
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

```text
Metabase interestingness != Dima VERIFIED Finding
```

P16:
Evidence / claim lineage.

P17:
Research Manager maturation: inspect/replan, bounded budgets, no-progress, counter-evidence, stopping,
durable resume.

P18:
relationships; Metabase owns native join mechanics, Dima only material company/sector policy.

P19:
Hypothesis / Root Cause epistemics.

P20:
ReportDocument / claim-to-evidence synthesis.

P21:
DecisionBrief / options / tradeoffs / recommendation / limitations.

Development effort belongs here, not in additional P13 operator certification.

---

## 12. Product direction after P21

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

Metabase is the analytics substrate.

Dima is the company/sector intelligence, Research, optimization, decision, action and institutional
memory layer.

Chat is one interface to this brain, not the product itself.

---

## 13. One Ask surface

Do not expose "Metabase mode" and "Dima mode".

There is one Dima Ask/Research surface.

A native execution either:
- satisfies material identity/provenance requirements and can support VERIFIED Evidence; or
- fails closed / records an explicit limitation.

Do not silently weaken truth requirements.

---

## 14. Speed / test economy

Permanent cadence:

```text
BUILD COHERENT PRODUCT SLICE
→ FOCUSED OWNER TESTS
→ ONE PROVIDER-FREE SEAL
→ MODEL/LIVE ONLY IF COGNITION CHANGED AND RESULT CHANGES A DECISION
→ CONTINUE
```

Do not:
- rerun P13B/P13C;
- rebuild unchanged engine;
- certify every Metabase operator;
- run Sol/C1/full corpus for Dima state-model changes;
- stop after every small commit;
- produce docs after every function.

One root-cause fix beats multiple defensive patches.

---

## 15. Supervisor STOP conditions

Stop only if:
1. native Metabot/QP/driver/Lib modification appears necessary;
2. a second analytics planner is being introduced;
3. a second analytical formula owner is being introduced;
4. a second security/receipt authority is being introduced;
5. silent wrong reaches VERIFIED Evidence;
6. a broad paid/model corpus is proposed without a decision-changing hypothesis;
7. destructive P7/P9 semantic ownership migration is proposed;
8. Research orchestration begins authoring MBQL/SQL/query-repair logic.

Ordinary P14 implementation is not a STOP.

---

## 16. What not to reopen

Do not reopen merely because the incoming supervisor was absent:
- P1-P5 execution/receipt foundations;
- P7/P8/P9 historical semantic/resource proofs;
- P10 identity;
- P11 minimum entity-value gate;
- P12X native-engine decision;
- P13A/B/C;
- P13D BREAKDOWN/RANKING;
- dima.6 certification.

Audit sealed work only when a real regression crosses its owner boundary.

---

## 17. Binding read order

1. this file;
2. `backend/belgeler/metabase/DIMA_METABASE_CURRENT_PRODUCT_PLAN.md`;
3. tail of `DIMA-METABASE-DURUM.md`;
4. DMP-DEC-0044 and DMP-DEC-0045 in
   `backend/belgeler/metabase/DIMA_METABASE_DECISION_RECEIPTS.md`;
5. DMP-P13D-LIVE-003 in
   `backend/belgeler/metabase/DIMA_METABASE_FAILURE_RECEIPTS.md`;
6. `backend/app/v3/research.py`;
7. `backend/tests/test_v3_p14_research.py`;
8. current `backend/app/v3/native_standard/**`;
9. engine `src/metabase/dima/**` only when an actual owner boundary requires it.

The sealed historical roadmap remains audit evidence. Do not use stale P13+ prose over the current
product-plan overlay.

---

## 18. Supervisor operating principle

```text
Metabase knows how to analyze.

Dima knows what the organization is trying to investigate,
what evidence supports which claim,
what remains uncertain,
what decision follows,
what action is approved,
and what must be remembered.
```

The largest current architectural risk is no longer lack of analytics capability.

It is accidentally building a second Metabase above Metabase.

Prevent that.
