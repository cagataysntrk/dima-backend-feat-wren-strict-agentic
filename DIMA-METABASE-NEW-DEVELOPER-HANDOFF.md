# DIMA METABASE PLATFORM — NEW DEVELOPER HANDOFF

## NON-NEGOTIABLE CURRENT RULES

```text
DO NOT MODIFY METABASE CORE.
DO NOT REOPEN P13/P14/P15/P16.
DO NOT BUILD ANALYTICS IN DIMA.
METABASE + METABOT = ANALYTICAL ENGINE.
DIMA = INVESTIGATION / EPISTEMICS / DECISION BRAIN.
DIMA CHOOSES THE NEXT ANALYTICAL QUESTION.
METABASE ANSWERS IT NATIVELY.
RECURSIVE DEPTH = DIMA.
ANALYTICAL EXECUTION AT EVERY DEPTH = METABASE.
P17 INVESTIGATION GRAPH != P19 CAUSAL GRAPH.
NO UI/UX BEFORE P21.
DO NOT TUNE PRODUCT BEHAVIOR TO ONE PROBABILISTIC TEST TRAJECTORY.
CERTIFY AUTONOMOUS AGENTS BY AUTHORITY / SAFETY / OUTCOME INVARIANTS.
RED IS EVIDENCE, NOT AN INSTRUCTION TO PATCH.
THREE ATTEMPTS ARE PER FAILURE FAMILY.
CLASSIFY BY FIRST WRONG TRANSITION + OWNER + INVARIANT.
GIT OBJECT TRUTH BEATS CI EVENT PROJECTIONS FOR AUTHORIZATION IDENTITY.
```

## DMP-DEC-0053 — PERMANENT P17 BOUNDARY

```text
P17 IS AN INVESTIGATION LANGUAGE,
NOT AN ANALYTICS ENGINE.

AUTONOMY DOES NOT MEAN
EVERY FIELD COMBINATION IS LEGAL.

MODEL CHOOSES AMONG LEGAL MOVES.
DIMA OWNS MOVE LEGALITY.
METABASE OWNS ANALYTICAL EXECUTION.

BRANCH IDENTITY IS CREATED
BY INVESTIGATION SEMANTICS,
NOT BY THE PRESENCE OF A STRING FIELD.

P17 INVESTIGATION GRAPH != P19 CAUSAL GRAPH.

RAW NATIVE MATERIAL IS DURABLE.
MANAGER COGNITION PACKET IS A THIN PROJECTION.

DO NOT BUILD A PLANNER
TO FIX A LEGALITY PROBLEM.
```

Legality is a pure state projection. `InvestigationActionProfile` exposes legal moves **now**;
it does not score, rank, plan, pick a branch winner, choose an analytical dimension, summarize native
results, or choose the next correct trajectory. Luna chooses among legal moves. Metabot/Metabase
perform all analytical execution.

## CURRENT AUTHORITY SNAPSHOT — 2026-09-25

> **FORWARD AUTHORITY.** This block overrides older current/next/blocked language. Historical
> receipts remain append-only. Recovery accounting is failure-family-scoped.

```text
branch                                = feat/dima-metabase-platform
branch HEAD before living-doc repin   = 69237bae627dc4342bf91fa3c87ba4d69b6532e8
sealed lower/core behavior checkpoint = d1bc5291b315ff19c3456d08ff1820e983d85942
current P17 legality code candidate    = c5de2b41f00e67cd3b141610aa3a057bf8057e0d
forward authority                     = DMP-DEC-0048 + DMP-DEC-0049 + DMP-DEC-0050 + DMP-DEC-0051 + DMP-DEC-0052 + DMP-DEC-0053

engine SHA                            = cbe313af9ac2d5960f662068e433d328d896fb06
engine release                        = 0.63.18-dima.6
engine digest                         = sha256:40e9a44be49904de3ddf12d4683c768e70955851c10a928a9c8f7d8f60780353
engine certification                  = 36042062775 SUCCESS
engine changes/builds                 = 0 / 0

latest autonomous live                = 36149372671 FAILURE
latest live tested SHA                = f514dd53d978c38d27e62c3cf36f6f4da5de5415
latest live manager calls             = 8
latest live native P17 follow-ups     = 3
latest live VERIFIED occurrences      = 4 including base
new Evidence reached later turn       = YES
bounded termination                   = YES
P14 immutable                         = YES
P16 sole claim authority              = YES
native analytics only                 = YES
single receipt family                 = YES
P13 hot path                          = 0
second native executor                = 0
Dima Python analytics                 = 0
Wren/raw-SQL/admin fallback           = 0

closed family                         = p17-cert-auth-transport
closed family RED                     = 36137304596 / attempt 1

closed family                         = p17-manager-structured-schema
boundary crossed                      = 36147620834

closed family                         = p17-manager-semantic-output
boundary crossed                      = 36149372671

current failure family                = p17-investigation-language-legality
current authoritative RED             = 36149372671
attempt in current family             = 1 / 3
remaining attempts in same family     = 2
current family owner                  = P17 TYPED INVESTIGATION LANGUAGE
current family status                 = ROOT FIX IN PROVIDER-FREE CERTIFICATION

next authorization                    = p17-investigation-language-legality--attempt-002.json
next paid run                         = NOT UNTIL FULL DMP-0053 DETERMINISTIC SEAL IS GREEN

P14                                   = SEALED
P15                                   = SEALED
P16                                   = SEALED
P17 analytical/native substrate       = GREEN
P17 typed investigation legality      = ROOT FIX IN PROVIDER-FREE CERTIFICATION
P17 autonomous cognition              = LIVE RED / NOT SEALED
P17 overall                           = NOT SEALED
P18                                   = BLOCKED
UI / UX                               = FORBIDDEN UNTIL P21 SEALED
```

### CURRENT P17 GATE — DMP-DEC-0053

The latest live crossed authorization, provider strict-schema, provider semantic-output, native
Metabot execution, native Evidence lineage and bounded termination. The active defect is therefore
not Metabase and not a provider-schema family.

```text
first wrong transition:
typed manager proposal accepted
→ P17 language admitted an illegal topology combination
→ branch identity could be minted from loose branch_key presence
→ structurally weak InvestigationGraph persisted
→ trajectory-invariant evaluator rejected the graph

owner:
P17 TYPED INVESTIGATION LANGUAGE
```

Current root correction:

```text
ResearchManagerSnapshot
→ InvestigationActionProfile
→ Luna chooses one state-legal move
→ resolve_investigation_topology ONCE
→ ResolvedInvestigationTopology
→ validation / persistence / execution / evaluation consume that authority
```

The durable store no longer interprets `branch_key` as branch authority. Only a branch-opening
`EXPLORE_ALTERNATIVES` move may mint a child branch. Root gap, deepening, testing,
counter-Evidence, replan, claim and stop moves cannot mint a branch from a string field.

The cognition packet is also narrowed without touching durable P15 truth: raw native exploration
payload remains stored, while the manager sees source-backed provenance plus verbatim native
descriptors only. No Python analytics or summarization was added.

Before any paid Luna run the following must all be GREEN:

```text
InvestigationActionProfile tests
adversarial topology matrix
multiple fake-manager legal trajectories
trajectory-invariant evaluator
thin cognition projection
provider strict-schema/semantic envelope
existing P17 regressions
P16
P15
P14
governance
engine SHA unchanged
```

Only after that seal is one `p17-investigation-language-legality / attempt 2` Luna run authorized.
P18 remains blocked.

### DMP-DEC-0050 AUTONOMOUS LIVE RETURN — RED / INFRA TRANSPORT

The one authorized DMP-DEC-0050 certification dispatch was `36137304596 = FAILURE`.
It did not enter manager cognition. The authorization commit
`5801ac71ba00867921dec17edff20568dc0fce05` genuinely **added**
`AUTONOMOUS_LUNA_AUTHORIZATION.json` and modified only the compatibility entrypoint transport
marker. The entrypoint then required that added path to appear in the GitHub push event's
`head_commit.added` field; this Actions event did not surface the path there, so the fail-closed
transport rejected the dispatch before `autonomous_manager_canary.py` was entered.

```text
first wrong transition:
valid add-only authorization commit
→ event-field-based add-only check
→ authorization path not observed in head_commit.added
→ RuntimeError before autonomous canary entry

owner:
INFRA / EVALUATOR TRANSPORT

manager Luna calls        = 0
Metabot occurrences       = 0
/api/dataset occurrences  = 0
Sol                       = 0
engine builds             = 0
C1                        = 0
```

This RED does not invalidate P17 provider-free recursive authority or the DMP-DEC-0050
trajectory-invariant evaluator. It is not a manager-cognition, structured-output, state-machine,
native-analytics, lineage, or Metabase-engine failure.

The historical DMP-DEC-0050 one-shot stop rule is superseded for recovery procedure by
DMP-DEC-0051. P17 remains **NOT SEALED** and P18 remains **BLOCKED**, but Cycle 1 / 3 may continue
after exact-Git transport provider-free proof and governance are GREEN.

### DMP-DEC-0051 PERMANENT RECOVERY RULES

```text
RED IS EVIDENCE, NOT AN INSTRUCTION TO PATCH.

FIRST WRONG TRANSITION → OWNER → ROOT CAUSE → GENERIC FIX.

MAX THREE BOUNDED RECOVERY CYCLES BEFORE SUPERVISOR STOP.

NO BLIND RERUNS.
NO REGEX / FUZZY / MORPH SEMANTIC PATCHES.
NO TEST-SPECIFIC PRODUCT BEHAVIOR.
DO NOT TUNE A PROBABILISTIC AGENT TO ONE TRAJECTORY.

GIT OBJECT TRUTH BEATS CI EVENT PROJECTIONS
FOR COMMIT/AUTHORIZATION IDENTITY.

METABASE + METABOT = ANALYTICAL ENGINE.
DIMA = INVESTIGATION / EPISTEMICS / DECISION BRAIN.
```

Current Cycle 1 owner is `INFRA / EVALUATOR TRANSPORT`. Product behavior is frozen. The historical
`AUTONOMOUS_LUNA_AUTHORIZATION.json` remains immutable evidence; new recovery receipts are
append-only under `backend/lab/metabase/p17/authorizations/`.

Permanent forward split:

```text
METABASE + METABOT = ANALYTICAL ENGINE

DIMA = INVESTIGATION
     + EPISTEMICS
     + DECISION BRAIN

DIMA CHOOSES THE NEXT ANALYTICAL QUESTION.
METABASE ANSWERS IT NATIVELY.

RECURSIVE DEPTH = DIMA.
ANALYTICAL EXECUTION AT EVERY DEPTH = METABASE.

P17 INVESTIGATION GRAPH != P19 CAUSAL GRAPH.
```

Permanent ownership:

```text
METABASE + METABOT
= analytics cognition + exploration + analytical semantics
+ native permissions + query construction/repair + execution

DIMA
= business context + Research + lineage + epistemic state
+ claims + hypotheses/root cause + reports
+ decisions + actions + outcomes + memory
```

```text
METABASE PROVES THE ANALYSIS.
DIMA PROVES THE LINEAGE, EPISTEMIC STATE, AND DECISION CONTEXT.
```

### P14 is CLOSED

P14 is not a place for more trust middleware. The sealed product hot path is:

```text
Research obligation
→ same principal-scoped native Metabot session
→ capture exact query A
→ persist query A/fingerprint
→ direct native Metabase /api/dataset execution ONCE
→ persist result/runtime/subject provenance
→ one DimaQueryReceipt(authority_kind=research_material)
→ Evidence
→ Research state
```

Durability is fail-closed:

```text
EXECUTED + persisted result
→ resume from persisted result
→ same deterministic receipt
→ NO second /api/dataset call

EXECUTION_STARTED + no persisted result
→ UNKNOWN OUTCOME
→ NO BLIND RETRY
→ explicit limitation/recovery path
```

Do not restore mandatory P13 attestation/re-execution, P10 synthetic Research access facts,
operator-level MBQL/resource validation, Standard projection hashes, Wren/raw-SQL/Agent-API fallback,
shared admin/service analytical sessions, or any second analytics/security/receipt authority.

P13 remains sealed beside the product path as a **CERTIFICATION / DEBUG / FORENSICS microscope**.

### Forward phase chain

```text
P14 Research                  SEALED
→ P15 native Exploration      SEALED
→ P16 claim-lineage Evidence  SEALED
→ P17 Research reasoning      OPEN NOW
→ P18 material business relationship policy
→ P19 Hypothesis / Root Cause
→ P20 ReportDocument
→ P21 DecisionBrief
→ only then UI/UX architecture
```

Every phase consumes the authority produced below it. No disconnected subsystem and no parallel truth
owner.

### Next bounded objective — P17

P17 matures the existing durable Research ledger into an agentic bounded investigation loop. It
consumes the already-sealed P14/P15/P16 authority chain:

```text
ResearchSession + obligations
+ P15 Research material
+ P14 Evidence
+ P16 claims / support-challenge lineage
→ Research Manager proposes the next bounded step
→ deterministic Dima layer validates/records the transition
```

The Research Manager may propose:
- inspect current Evidence/claims;
- identify a gap;
- request a bounded native analytical/exploration step;
- form or refine an explicit claim;
- seek counter-evidence;
- stop with a supported/challenged/inconclusive/insufficient result.

Deterministic Dima code owns only:
- allowed state transitions;
- obligation and claim identity;
- Evidence eligibility;
- budgets;
- no-progress detection;
- completion/stopping rules;
- restart durability.

Do **not** build a giant deterministic analytics state machine such as
`if trend → breakdown → segment → compare`. The LLM/Research Manager proposes investigative steps;
Metabase remains analytical owner. Counter-evidence is first-class and no forced answer is required.

Start provider-free with a typed manager-proposal contract and scripted/fake manager tests. Use one
bounded Luna canary only if actual manager cognition cannot be resolved provider-free and changes the
decision. No Sol by default. No UI/UX before P21.

### Current STOP conditions

Stop for supervisor only if one of these becomes concrete:

- Metabot/QP/Lib/driver/core engine modification is necessary;
- principal-scoped native security cannot be preserved;
- native permission enforcement is insufficient for a real Dima-specific policy;
- a second analytical, security, or receipt authority appears necessary;
- silent wrong can enter trusted claim/finding/decision state;
- destructive semantic migration is required;
- large paid evaluation is required;
- a phase cannot consume prior-phase authority without a parallel system.

Otherwise continue through the core chain. Do not return to UI work before P21.

---

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


---

## 19. 2026-09-25 TAKEOVER UPDATE — P14 RUNTIME RETURN POINT B

Current Platform HEAD after bounded accepted-context work:

```text
HEAD       = 367f5e6e468f6b86ebe02816f2310b0f1330830c
governance = 36092002345 SUCCESS
engine     = cbe313af9ac2d5960f662068e433d328d896fb06 / 0.63.18-dima.6
```

Two bounded commits were added:
- `af7de7e5...`: persist the exact accepted `ResearchBrief` inside the durable/fingerprinted
  `ResearchSession`; preserve typed ranking/comparison payloads;
- `367f5e6e...`: bind those typed operation payloads into the ResearchBrief authority identity.

Do not revert these to a raw-prompt resume scheme.

The next developer/supervisor must not start P15 yet. P14 production runtime is blocked at the owner
boundary, not at Metabot analytics:

```text
Dima Principal
  -> [MISSING EXISTING PRODUCTION OWNER]
  -> exact authenticated Metabase subject/session

accepted Research named-month surface
  -> [MISSING ACCEPTED TYPED ABSOLUTE PERIOD BINDING]
  -> P13 ResolvedPeriod authority

current Dima business/engine mapping
  -> [MISSING PRODUCT RUNTIME PROVIDER]
  -> DimaExecutionBindingSnapshot / ManagedResourceBinding / verified security facts
```

Do not close these by inventing a service/admin session, new identity broker, string/date parser,
second planner, or lab-fixture production binding. The correct continuation is to identify or
explicitly authorize the existing production owners/seams. If doing that requires a new identity,
semantic, security or receipt authority, return to supervisor before implementation.

No P14 provider-free seal was run after these partial runtime changes; only governance is GREEN.
No Luna/Sol/C1/live canary was run.
---

# 2026-09-25 — CURRENT TAKEOVER OVERRIDE — DMP-DEC-0047

This section supersedes the temporal part of the previous `DMP-P14-RUNTIME-STOP-001` handoff.

Current Platform checkpoint before this docs decision:

```text
abc7bff31e46047cc81b89dbccf99bbf459a26de
```

Engine remains:

```text
cbe313af9ac2d5960f662068e433d328d896fb06
0.63.18-dima.6
36042062775 SUCCESS
sha256:40e9a44be49904de3ddf12d4683c768e70955851c10a928a9c8f7d8f60780353
```

Do not restart P13. Do not repair P13D comparison now.

P14 accepted-context durability is already implemented:
- exact accepted `ResearchBrief` persists in the Research checkpoint;
- resolver-proven refs survive resume;
- ranking/comparison typed payloads participate in authority identity;
- no old-prompt reparse.

## Important reclassification

Ordinary named-month temporal language is NO LONGER a generic P14 production blocker.

Do NOT create:
- absolute-month parser;
- second temporal planner;
- P13 `ResolvedPeriod` compiler for every Research task.

Metabase/Metabot own native temporal analytical mechanics. Dima preserves the accepted Research
objective and later records the exact executed scope/result in claim-lineage Evidence.

## Actual work now

Build only these two production seams:

```text
A. NativeSubjectSessionProvider
   Dima Principal
   → exact native Metabase subject/session

B. NativeResourceBindingProvider
   Dima business concept/context
   → exact current Metabase resource identity/version/security lens
```

Names are conceptual; reuse existing code/contracts if an owner already exists.

Neither provider is allowed to become a new authority.

A must reuse native Metabase authentication/session/security and never use shared admin/service-user
analytical fallback.

B must reuse P9/P10/P13/current native facts and must not duplicate Metric/Model formulas or hard-code
Boyahane fixtures.

Then wire existing P14 `ResearchMaterialExecutor` through the thin native gateway:

```text
Research obligation
→ native Metabot
→ exact occurrence
→ material principal/resource/runtime checks
→ native execution
→ P5 QueryReceipt
→ Evidence
→ Research state
```

Do not force each Research task back through a full operator-by-operator P13 semantic interpreter.

`feat/ask-v2-mvp` is READ ONLY and may be inspected only for patterns:
principal pass-through, durable/idempotent task lifecycle, obligation-scoped failure and resume.
Do not copy Wren planner/cube/SQL/temporal ownership.

Default budgets until those seams are GREEN:

```text
engine build = 0
Luna         = 0
Sol          = 0
C1           = 0
```

Return after:
- the thin native production gateway + real Research material flow is provider-free GREEN; or
- a genuine native auth/resource-binding architectural STOP.



---

# 2026-09-25 — CURRENT TAKEOVER OVERRIDE — DMP-DEC-0048

This is the forward implementation authority. It supersedes the ordinary-Research execution model in
DMP-DEC-0047 while preserving all sealed history.

Do not restart P13 and do not make P13 ordinary product middleware.

Current state:

```text
HEAD               = 3dc544b95c05044e35c6903b720a6ddb824e9b37
governance         = 36095837229 SUCCESS
P14 provider-free  = 36095837211 FAILURE (13 PASS / 6 FAIL)
engine             = cbe313af9ac2d5960f662068e433d328d896fb06
release            = 0.63.18-dima.6
P14                = NOT SEALED
P15                = NOT STARTED
```

## Product ownership

```text
METABASE + METABOT = ANALYTICAL TRUTH + EXECUTION
DIMA               = ONTOLOGY + RESEARCH + LINEAGE + DECISION SYSTEM
```

P13 = **CERTIFICATION MICROSCOPE**, not mandatory request middleware.

## What to build now

1. Prove from pinned source/tests where the exact Metabot-produced query representation already lives.
   Prefer capture, never reconstruction.
2. Persist enough of query A in existing `ResearchExecutionLink` to resume it without another
   Metabot turn.
3. Add the smallest direct transport to existing `NativeEngineBridge`:
   same authenticated client → exact query A → native `/api/dataset` execution.
4. Keep `NativeSubjectBinding` only as explicit identity correlation and verify
   `/api/user/current`; Metabase owns permission decisions.
5. Bypass/remove mandatory P13 attestation/re-execution, P10 synthetic access facts and operator-level
   resource/MBQL inspection from ordinary Research.
6. Widen the **one** `DimaQueryReceipt` contract cleanly for `research_material`. Do not fake
   Standard projection/resolved-intent hashes.
7. Evidence means receipted native execution/result lineage; it does not mean Dima re-proved native
   COUNT/ranking/temporal/filter/breakout semantics.
8. Fix focused test harness and timezone-aware defaults for new P14 binding rows.
9. Run one focused provider-free seal + P5 receipt regressions.
10. Only if necessary, one deterministic no-model native compatibility probe.
11. After GREEN, one Luna Research canary. No automatic second paid run.
12. If the canary is GREEN, P14 is done; immediately move to P15 Native Metabase Explorations.

## Never do

- shared admin/global service analytical session;
- admin fallback;
- second planner/compiler/canonicalizer;
- Dima MBQL parser or query normalization layer;
- Wren/raw SQL/Agent API fallback;
- mandatory `attest_native_query()` / `execute_native_query()` in production Research;
- mandatory NativeResourceBinding row for each native query;
- second RLS/security authority;
- second receipt family;
- P13 grammar expansion;
- engine/Metabot/QP/Lib/driver patch unless a genuine STOP is proven.

## Stop only for a real architectural condition

Stop if principal-scoped native auth cannot be maintained, Metabot query A cannot reach an existing
native Metabase execution route unchanged without engine/core modification, direct execution loses
tenant/security enforcement, or a duplicate analytics/security/receipt authority becomes necessary.

Otherwise keep building product.
