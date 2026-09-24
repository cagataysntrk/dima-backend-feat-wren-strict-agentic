# DIMA METABASE PLATFORM — NEW DEVELOPER HANDOFF

**Authoritative developer takeover — 2026-09-24**

You know the project approximately through early P13/P13B. Do not restart P13 and do not repeat
historical analysis. Continue from the exact current state below.

For forward work, this file and
`backend/belgeler/metabase/DIMA_METABASE_CURRENT_PRODUCT_PLAN.md`
supersede older P13+ onboarding text.

---

## 0. Exact current state

Platform:

```text
repo       = cagataysntrk/dima-backend-feat-wren-strict-agentic
branch     = feat/dima-metabase-platform
HEAD       = 6bce25331da3e0c467b49701ba77f90059fd8b21
governance = 36052986798 SUCCESS
```

Engine:

```text
repo          = UpcyTech/dima-metabase-engine
main          = cbe313af9ac2d5960f662068e433d328d896fb06
release       = 0.63.18-dima.6
upstream      = 2ba2485c78d7e00a9a25f82c00fc201da71590c4
certification = 36042062775 SUCCESS
digest        = sha256:40e9a44be49904de3ddf12d4683c768e70955851c10a928a9c8f7d8f60780353
```

P14 foundation:

```text
implementation        = a8c7b5d2b922e85ff046c6c7ce1bfce92aa13552
integrated proof      = bab26fe51978929ace44f7703543f78099c692ce
provider-free         = 36052728145 SUCCESS
P14 focused           = 6 passed
P13D/P10/P5 regression= 69 passed
engine builds         = 0
model calls           = 0
```

---

## 1. What changed after the P13B era you know

Do not use the old model:

```text
Dima semantic/query engine
→ Metabase executor
```

Current binding architecture:

```text
DIMA
= Research / Evidence / Hypothesis / Decision / Action / Memory
+ business ontology / company + sector context
+ engine-resource mapping
+ product identity/policy binding

ON TOP OF

METABASE + METABOT
= native analytical definitions
+ analytical cognition
+ query construction/repair
+ filters/breakouts/ranking/temporal/joins
+ MBQL/QP/drivers
+ native permissions
+ dashboards/visualization/Explorations/lifecycle
```

Do not build a second analytics engine.

---

## 2. Permanent reuse rule

```text
USE_NATIVE
→ COMPOSE_NATIVE
→ WRAP_NATIVE
→ HOOK_NATIVE
→ DIMA_OWNS
```

If Metabase/Metabot already owns a capability, use it.

`DIMA_OWNS` requires a measured product-specific gap.

---

## 3. Native core is read-only by default

```text
NATIVE_SUBSTRATE_IMMUTABILITY = BINDING
DIMA_FIRST_FAULT_PRESUMPTION   = BINDING
```

Do not modify:
- Metabot prompts/profiles/skills/agent-loop;
- Metabase Lib;
- Query Processor;
- drivers;
- native query repair/search mechanics.

If something native works without Dima but not through Dima, fix Dima first.

A native-core patch requires supervisor authorization.

---

## 4. P13 status — do not reopen

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

Do not claim all P13D GREEN.

Do not fix comparison proactively.

If real P14/product work hits the same compatibility gap:
- fail the material execution closed;
- record a Research limitation;
- capture the exact native representation;
- only then consider a focused reversible Dima-local fix.

No dima.7 just to complete an old test table.

---

## 5. DimaSemanticSpec rule

Existing P7/P8/P9 DimaSemanticSpec/DIMA_MANAGED resources remain valid sealed compatibility assets.

Do not delete them.

Do not expand them into a shadow Metric/Model/query-definition engine.

Forward direction is conceptually:

```text
DIMA BUSINESS ONTOLOGY / ENGINE MAPPING
```

Metabase owns the native analytical definition.

Dima owns stable concept identity, aliases/company/sector meaning, decision relevance and mapping to the
exact engine resource/version.

Do not duplicate one metric formula in Dima and Metabase.

---

## 6. Evidence rule

```text
ENGINE PROVES ANALYTICS
DIMA PROVES CLAIM LINEAGE
```

Engine proves which native resource/query executed and returns result + execution identity.

Dima binds that result to:
- Research obligation;
- claim;
- principal/scope/resource lineage;
- Evidence epistemic state;
- Findings/Hypotheses/Decisions.

Evidence is not a second MBQL interpreter.

---

## 7. P14 foundation is already implemented

Current owner:

```text
backend/app/v3/research.py
```

Existing foundation includes:
- ResearchSession;
- ResearchObligation;
- Hypothesis;
- CounterEvidenceRef;
- EvidenceRef;
- ResearchBudget;
- StoppingState;
- NativeMetabotConversationRef;
- ResearchLimitation.

It reuses:
- P13 NativeStandardTrustOrchestrator;
- exact-occurrence engine execution;
- P10 ExecutionAccessSnapshot;
- P5 DimaQueryReceipt;
- EvidenceArtifact.

Do not recreate any of these.

Do not write SQL/MBQL generation or analytical planners into ResearchManager.

---

## 8. Your immediate work order

Continue P14; do not rebuild the foundation.

Build one coherent product-level Research/Ask integration slice:

1. inspect the current product Ask/Research entry boundary and wire ResearchSession into it;
2. create durable correlation from a Dima ResearchSession to a real native Metabot conversation/session;
3. delegate governed Research obligations to native Metabot;
4. every material native execution must reuse the existing P13 exact-occurrence path;
5. reuse the same P10 access identity and P5 receipt;
6. admit only eligible receipted Evidence into Research state;
7. add durable resume/correlation without reparsing raw prompt text into a new authority;
8. preserve obligation-scoped limitations;
9. allow independent obligations to continue when one unsupported execution fails closed;
10. add only focused provider-free tests for the new owner.

Do not return after tiny commits.

---

## 9. Model/test budget

For ordinary P14 state/orchestration development:

```text
engine build = 0
Luna         = 0
Sol          = 0
C1           = 0
full corpus  = 0
```

Development cadence:

```text
coherent product slice
→ focused owner tests
→ one provider-free seal
→ model/live only when native cognition is genuinely under test
  and the result changes a product/architecture decision
→ continue
```

Do not rerun P13B/P13C.

Do not rebuild unchanged engine.

---

## 10. What P14 must NOT become

Do not build Python:
- query planner;
- breakdown engine;
- ranking engine;
- comparison engine;
- temporal planner;
- MBQL parser;
- query repairer;
- generic analytics state machine.

ResearchManager owns:
- what must be investigated;
- obligations;
- hypotheses/counter-evidence;
- budgets/stopping;
- what Evidence means.

Metabot/Metabase own how the analytics is performed.

---

## 11. Next P14 target after product wiring

After the product-level Research/Ask bridge is coherent:

- prove durable session resume/correlation;
- prove one native conversation can satisfy or limit Research obligations without duplicate authority;
- prove VERIFIED Evidence updates Research state;
- prove counter-evidence cannot silently promote a hypothesis;
- prove budget/stopping is durable and fail-closed.

Only then consider one small live Research evaluation if it can change a real design decision.

---

## 12. P15 direction

P15 is:

```text
NATIVE METABASE EXPLORATIONS INTEGRATION
```

not primitive harvesting.

Use native capabilities in place:
- applicability;
- variants;
- interestingness;
- top-N + Other;
- temporal patterns;
- stored results;
- cancel/restart;
- idempotency;
- native permissions/lifecycle.

```text
Metabase interestingness != Dima VERIFIED Finding
```

Do not port these primitives into Python.

---

## 13. Later product corridor

```text
P16 Evidence / claim lineage
P17 Research maturation / inspect-replan / durable resume
P18 material relationship policy
P19 Hypothesis / Root Cause epistemics
P20 ReportDocument
P21 DecisionBrief
```

This is where Dima differentiation lives.

Do not spend the next sprint expanding P13 operator certification.

---

## 14. Absolute prohibitions

No:
- Wren analytical fallback;
- raw-SQL analytical fallback;
- Agent API analytical hot path;
- admin analytical fallback;
- fuzzy/regex/morphology semantic authority;
- duplicate metric formula owner;
- second QueryReceipt;
- second access-fingerprint system;
- generic second RLS/CLS engine;
- native Metabot/QP/Lib/driver patch without supervisor authorization;
- P13E/P13F operator-family work.

---

## 15. STOP conditions

Stop only if:
1. native Metabot/QP/driver/Lib modification appears necessary;
2. a second analytics planner appears necessary;
3. a second analytical formula owner appears necessary;
4. a second security/receipt authority appears necessary;
5. silent wrong reaches VERIFIED Evidence;
6. destructive semantic-ownership migration is proposed;
7. broad paid/model evaluation is proposed without a decision-changing hypothesis.

Otherwise keep developing.

---

## 16. Read order

1. this file;
2. `backend/belgeler/metabase/DIMA_METABASE_CURRENT_PRODUCT_PLAN.md`;
3. tail of `DIMA-METABASE-DURUM.md`;
4. DMP-DEC-0044 and DMP-DEC-0045;
5. `backend/app/v3/research.py`;
6. `backend/tests/test_v3_p14_research.py`;
7. current P13 trust path only as reused infrastructure.

Historical P13B handoff text is evidence, not current work authorization.

---

## 17. Return point

Return only after substantial progress:

A. real product Research/Ask orchestration + durable native-conversation correlation + one provider-free
receipted Evidence path is GREEN;

or

B. a genuine STOP condition is proven.

Keep moving otherwise.


---

## 18. CURRENT TAKEOVER AFTER DMP-DEC-0046 — P14 PRODUCT BOUNDARY SEALED

This section supersedes the earlier P14 product-wiring target above.

Exact code checkpoint before this docs-only update:

```text
Platform code HEAD                 = dbef0499abe6b7804b5f09d8ec7ad76b99946b1c
P14 provider-free                  = 36057793900 SUCCESS
governance                         = 36057794099 SUCCESS
P14 focused                        = 13 passed
P13D/P10/P5 inherited regression   = 69 passed

engine SHA                         = cbe313af9ac2d5960f662068e433d328d896fb06
release                            = 0.63.18-dima.6
engine builds                      = 0
model calls                        = 0
native Metabase/Metabot changes    = 0
```

P14 now has both:
1. the DMP-DEC-0045 Research foundation; and
2. the DMP-DEC-0046 durable product Research/Ask boundary.

Read these active files first:
- `backend/app/v3/research.py`;
- `backend/app/v3/research_store.py`;
- `backend/app/v3/research_product.py`;
- `backend/app/routers/ask_v2.py`;
- `backend/tests/test_v3_p14_research.py`;
- `backend/tests/test_v3_p14_product.py`.

Important runtime boundary:
the product layer does not own Metabase authentication. It never creates a shared admin/service
session. Native material work requires the existing principal-scoped P13/P10 runtime owner to be
installed into the P14 runtime seam. If absent, material execution fails closed with 503. Do not
"fix" that by adding an admin fallback or a second security identity system.

Do not reopen P14 foundation or P13 operator certification. P13D comparison remains deferred debt.

Next coherent phase is P15:
`NATIVE METABASE EXPLORATIONS INTEGRATION`.

P15 must reuse native applicability, variants, interestingness, Top-N + Other, temporal patterns,
stored results, runner/cancel/restart/idempotency and derived permissions in place. Do not port those
primitives into Python. Dima maps native Exploration output into Research/Evidence; Metabase
interestingness is not itself a Dima VERIFIED Finding.

If P15 exposes a genuine need for a native Metabot/QP/Lib/driver patch or a second
security/receipt/analytical authority, stop for supervisor. Otherwise keep developing.
