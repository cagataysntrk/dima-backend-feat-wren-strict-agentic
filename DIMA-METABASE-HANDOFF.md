# DIMA METABASE PLATFORM — DEVELOPER HANDOFF

> **Read this before touching code.**
>
> Audited functional baseline:
> `4b60bc3f1e6ab9526cd590a0989c1b227c5c43be`
>
> The commit that adds this handoff is documentation-only. Treat the baseline above as the last
> audited product/milestone state unless a newer product commit is explicitly certified.

---

## 1. What are we building?

We are migrating Dima from Wren-dependent analytics execution toward an engine-independent
decision-intelligence architecture with Metabase as the target analytics substrate.

We are **not**:
- converting Dima into a Metabase chatbot;
- copying Metabase into the Dima backend;
- handing semantic authority to Metabase;
- deleting Wren before semantic/execution/security equivalence is understood.

Target ownership:

```text
User
→ LLM cognition
→ Dima semantic/security/trust authority
→ ResolvedAnalyticsIntent
→ analytics substrate
   - Metabase: target substrate
   - Wren: retained migration/compatibility substrate
→ DB
→ Dima QueryReceipt / Evidence
→ Research / Report / Decision UX
```

Responsibilities:

```text
LLM
= analytical cognition:
  strategy, hypotheses, evidence selection, next-tool choice,
  adaptive replanning, synthesis.

Dima
= truth/trust:
  semantic identity, authority, access, provenance, evidence,
  budgets, completion constraints, durable identity.

Metabase
= analytics operating substrate:
  structured query construction/execution, drivers, BI workspace,
  dashboards, saved questions, collections, query-builder surfaces.

Database
= numeric/data truth.
```

Binding doctrine:
`LLM_FIRST_COGNITION + DIMA_OWNED_TRUTH`.

`DimaSemanticSpec` is canonical business meaning. It is not a universal analytical planner.

---

## 2. Branch isolation is absolute

Only develop here:

```text
feat/dima-metabase-platform
```

Moving references only:

```text
feat/ask-v2-mvp
feat/dima-metabase-product-fast-track
```

Observed at handoff preparation:

```text
ask-v2:
80e2e101298cfb750231b4161b9e888e65323a04

Fast Track:
946cb933441381078941767e8ac6205349ff81e3
```

These SHAs are observations, not certified source pins. They can move.

Forbidden:

```text
NO MERGE
NO CHERRY-PICK
NO REBASE
NO WRITES TO ask-v2
NO WRITES TO Fast Track
NO certified-base replacement
```

If a primitive is useful, use **controlled harvest**:
1. fetch the then-current source HEAD;
2. inspect the exact primitive and its owner;
3. identify the Platform milestone that owns the need;
4. port the minimum architecture-independent contract;
5. preserve Platform semantic/security/provenance invariants;
6. prove it with Platform tests;
7. never bulk-import source-branch behavior.

---

## 3. Context-reset read order

After any context loss, read exactly:

1. `DIMA-METABASE-HANDOFF.md`
2. `DIMA-METABASE-DURUM.md`
3. `backend/belgeler/metabase/DIMA_METABASE_DECISION_RECEIPTS.md`
4. `backend/belgeler/metabase/DIMA_METABASE_FAILURE_RECEIPTS.md`
5. `backend/belgeler/metabase/DIMA_METABASE_NIHAI_FIZIBILITE_VE_MIMARI_RAPORU.md`
6. `backend/belgeler/metabase/DIMA_METABASE_NIHAI_UYGULAMA_YOL_HARITASI.md`
7. current milestone predev review
8. current milestone ticket
9. then current code/tests/workflow

Never infer current state from an old chat or commit title alone.

---

## 4. Mandatory development protocol

Every real slice follows:

```text
1. verify real branch HEAD
2. read living status + latest decisions/failures
3. read relevant normative report/roadmap sections
4. inspect current code/contracts/tests
5. inspect pinned upstream source when substrate behavior matters
6. write/seal predevelopment boundary
7. governance GREEN
8. implement one coherent owner/slice
9. focused provider-free proof
10. inherited critical regressions
11. pinned-live proof only when it adds information
12. classify every RED before patching
13. update living status + receipt
14. only then move on
```

A RED is not permission to patch.

Classify first:

```text
PRODUCT CONTRACT
ARCHITECTURE
SEMANTIC GAP
SECURITY GAP
PROVENANCE GAP
SUBSTRATE RUNTIME GAP
WREN COMPATIBILITY GAP
ORACLE / TEST ERROR
CI / GOVERNANCE DRIFT
FIXTURE / DATA GAP
```

Then patch the single owner.

Do not green a test via:
- case-specific product logic;
- regex/fuzzy/name-similarity semantic truth;
- hidden fallback;
- semantic guessing;
- silent field/requirement loss;
- raw-SQL escape;
- source-branch copying;
- weaker oracle without pinned-source evidence.

---

## 5. Binding architecture decisions

### DMP-DEC-0026

Binding:

```text
LLM_FIRST_COGNITION
SEMANTIC_CORE_IS_NOT_ANALYTICAL_PLANNER
ADAPTIVE_GOVERNANCE
SEMANTIC_NECESSITY_GATE
```

Model policy:

```text
Luna = default / economic baseline
Sol  = ceiling / headroom measurement
```

Before creating a new deterministic cognition/semantic mechanism:
1. freeze a small high-information corpus;
2. hold data/tools/prompt/context/permissions/oracle constant;
3. run Luna;
4. run Sol on exactly the same contract;
5. classify failure;
6. add only the minimum generic guardrail if materially necessary;
7. rerun the same corpus;
8. record Architecture Value Delta.

A Luna failure alone does not justify permanent deterministic cognition.

### Adaptive governance

```text
Level 0 = native analytics + mandatory security/execution/provenance envelope
Level 1 = canonical metric/dimension/time/lineage/version
Level 2 = relationship/grain/additivity/advanced time/security/business lens
Level 3 = sector/decision semantics + specialized governed workflows
```

There is no anonymous/unscoped Level 0.

Effective level cannot fall below tenant/capability/security minimums.

---

## 6. The central seam

The key substrate-independent seam is:

```text
Accepted Dima Authority
→ ResolvedAnalyticsIntent
→ substrate adapter
```

Metabase does not reinterpret user meaning.

Long-term:

```text
DimaSemanticSpec = semantic truth
WrenAdapter       = retained migration/compatibility substrate
MetabaseAdapter   = target analytics substrate
```

---

## 7. Key code map

### Semantic / authority

- `backend/app/v3/semantic_spec.py`
  - canonical Dima semantic types.
- `backend/app/v3/semantic_import.py`
  - final composed Wren MDL -> DimaSemanticSpec.
- `backend/app/v3/semantic_equivalence.py`
  - Wren/Dima/Metabase capability classification.
- `backend/app/v3/analytics_contract.py`
  - ResolvedAnalyticsIntent.
- `backend/app/v3/authority.py`
  - Dima authority boundary.

### Metabase execution

- `backend/app/v3/substrate/metabase/execution_binding.py`
- `backend/app/v3/substrate/metabase/compiler.py`
- `backend/app/v3/substrate/metabase/canonical.py`
- `backend/app/v3/substrate/metabase/execution_adapter.py`
- `backend/app/v3/substrate/metabase/client.py`

### Wren compatibility

- `backend/app/v3/substrate/wren.py`

Do not patch Wren compatibility simply to make parity tests green.

### Identity / evidence / resources / security

- `backend/app/v3/execution_identity.py`
- `backend/app/v3/evidence.py`
- `backend/app/v3/resource_provisioning.py`
- `backend/app/v3/resource_transport.py`
- `backend/app/v3/security_identity.py`
- `backend/app/v3/entity_value_gate.py`

---

## 8. Milestone history

### P0 / bootstrap

Created an isolated Metabase-platform branch and governance/living-status discipline without touching
ask-v2.

### M1 — engine-independent core + Wren zero-drift

Separated Dima authority/contracts from substrate identity and preserved existing Wren behavior through
the compatibility adapter.

### M2 — pinned Metabase lab

Pinned:
```text
Metabase v0.63.18
source pin 2ba2485c78d7e00a9a25f82c00fc201da71590c4
```

Runtime/image identity, health/bootstrap and lab lifecycle are governed.

### P3 / P3A — structured client + bridge preflight

Established the pinned structured Metabase client/Agent API behavior and proved that the bridge can be
evaluated without giving Metabase semantic authority.

### P4 — projection compiler + canonical proof

Implemented:
- pure ResolvedAnalyticsIntent -> portable MBQL projection;
- pinned `construct-query` canonicalization;
- structural semantic-slot manifest;
- no implicit join authority;
- fail-closed unsupported formula/relationship/grain cases.

Important runtime fact:
Metabase injects volatile `lib/uuid`. Durable canonical identity removes only exact
`lib/uuid`; every other canonical field remains strict.

### P5 — execution/access identity + strict QueryReceipt

Implemented:
- `ExecutionAccessSnapshot`;
- runtime identity;
- strict receipt sealer;
- access/query/result/resource provenance;
- paired entity/fingerprint resource identity;
- durable receipt fingerprint vs execution occurrence identity.

Still open globally:

```text
DMP-P5-BLOCK-001
```

Do not claim global production official receipt issuance is fully certified.

### P6 — targeted Wren/Metabase parity probe

Built one deterministic PostgreSQL snapshot and exercised real substrate seams.

Result:

```text
P6 measurement GREEN
Wren/Metabase equivalence NOT claimed
typed gaps carried forward
UNEXPLAINED_MISMATCH = 0
```

Broad fixed 80-case parity was intentionally deferred to later integrated Standard certification.

### P7 — semantic migration baseline

Implemented structured final-composed-MDL -> DimaSemanticSpec import.

Rules:
- structured source fields only;
- formulas remain opaque;
- relationship condition text is not parsed;
- exact lineage only;
- unsupported richness -> typed gap.

Coverage was hardened so every non-empty structured source key is:
`CONSUMED`, `GAP_OWNED`, or explicitly operational metadata.

Unknown non-empty fields are hard gaps.

### P8 — semantic equivalence matrix

Classifications:

```text
NATIVE_METABASE
DIMA_COMPILED
DIMA_RUNTIME
WREN_ONLY_GAP
UNSUPPORTED
```

No formula parser or relationship-condition parser was added.

### P9 / P9B — managed resources + isolated metric lifecycle

P9A:
- desired resource planning;
- CREATE/UPDATE/NOOP/stale reconciliation;
- metadata coherence;
- rollback contract;
- real P7→P8→policy→P9 proof.

P9B:
- tenant-bound metric transport;
- projection/resolved-intent/catalog/canonical-query provenance;
- exact-id create/read/NOOP/archive/read/restore/read/cleanup proof.

P9B is isolated-lab proof only.

Still open:
- dimension transport gap;
- time transport gap;
- relationship transport gap.

### P10 — access/security identity

P10A:
- P5 `ExecutionAccessSnapshot` remains the sole durable access identity;
- principal/intent/projection/security facts bind fail-closed.

P10B1 live:
- same restricted authenticated user;
- query succeeds before revoke;
- same session gets HTTP 403 after revoke;
- succeeds after restore;
- no admin analytical fallback.

P10B2 status:

```text
tenant identity                  PROVEN
principal identity               PROVEN
basic DB query permission        PROVEN
same-session revocation          PROVEN
collection permission            CAPABILITY_GAP
RLS                              NOT_CONFIGURED / block if required
CLS                              NOT_CONFIGURED / block if required
impersonation                    REQUIRES_EXTERNAL_OWNER
database routing                 REQUIRES_EXTERNAL_OWNER
cache/result reauthorization     CAPABILITY_GAP
service/admin fallback ban       PROVEN
```

Do not fake RLS/CLS/impersonation with labels.

### P11 — entity-value Semantic Necessity Gate

P11 is the model for future architecture decisions.

Frozen EV-01..04 experiment:
- EV-01 exact categorical = Luna PASS / Sol PASS;
- EV-02 cross-language `Kuzey → North` = PASS/PASS without translation dictionary/fuzzy/stemming;
- EV-03 unresolved region-vs-customer scope = both models sometimes silently BIND;
- EV-04 missing value = PASS/PASS.

Because both Luna and Sol had the same material EV-03 truth failure, one minimum deterministic
mechanism was justified:

```text
EntityValueAdoptionGate
```

It answers only:

```text
may this model-proposed BIND become Dima truth?
```

It does not own language understanding, retrieval, search, translation, candidate generation,
physical-field discovery or analytical planning.

Post-guardrail official result:
```text
Luna = 4/4
Sol  = 4/4
official silent wrong = 0
entity resolver framework = NOT NEEDED
```

Final P11 correctness hardening:
- exact adoption = same scalar type + same scalar value;
- bool/int/float type-crossing collisions blocked;
- P11 CI directly runs necessity-contract and product-gate families;
- exact focused count = 16 PASS.

Certified wording:

```text
P11 INITIAL LOW-CARDINALITY NATIVE PATH GREEN
```

Not certified:
- EV-05 high cardinality;
- EV-06 stale index;
- EV-07 permission-hidden value.

Forward integration requirement:

```text
DMP-P11-INTEGRATION-005 = OPEN / P13 OWNER
```

---

## 9. Current audited state

Audited functional baseline:

```text
4b60bc3f1e6ab9526cd590a0989c1b227c5c43be
```

At that baseline:

```text
P11 workflow = 35816646368 = SUCCESS
governance   = 35816646416 = SUCCESS
```

P11 is closed.

Current phase:

```text
P12 BI WORKSPACE FEASIBILITY / CLASSIFICATION
```

No P12 integration implementation is authorized by the current ticket.

---

## 10. P12 — current product/workspace decision

P12 is not a semantic-cognition milestone.

Current initial product composition:

```text
DIMA_SHELL + HEADLESS_API
```

Workspace escape hatch:

```text
LINK_OUT
```

Optional future escalation:

```text
EMBED
```

Ownership invariant:

```text
Metabase Dashboard/Card/Collection/Question
!= Dima business truth

Metabase UI navigation
!= Dima semantic authority
```

P12 open product gaps:
- tenant-user collection persistence permission not production-certified;
- RLS/CLS advanced profiles uncertified;
- Dima Shell does not reproduce all native Metabase workspace breadth;
- LINK_OUT context handoff unspecified;
- EMBED auth/session/entitlement contract uncertified;
- mobile/responsive production composition unmeasured.

Relevant current docs:
- `backend/belgeler/metabase/predev/P12_PREDEVELOPMENT_REVIEW.md`
- `backend/belgeler/metabase/predev/P12_UX_MODE_EVIDENCE_MATRIX.md`
- `backend/belgeler/metabase/tickets/P12_BI_WORKSPACE_FEASIBILITY.md`

---

## 11. What the next developer should do

### First: re-verify, do not code

1. confirm current Platform HEAD;
2. read this handoff;
3. read latest `DIMA-METABASE-DURUM.md` tail;
4. read P12 review/matrix/ticket;
5. observe current ask-v2/Fast Track HEADs as read-only;
6. verify governance is GREEN.

### Then: close P12 classification deliberately

The current P12 documents already contain:
- four UX modes;
- initial selected composition;
- ownership rules;
- explicit gaps;
- no premature integration.

If no new evidence contradicts them, add an explicit P12 classification closure receipt/status.

Do not turn P12 closure into frontend implementation.

### Then: open P13 Production Standard predevelopment

P13 is the next real integration owner.

Required seam:

```text
accepted Dima semantic authority
→ allowed semantic scopes

ExecutionAccessSnapshot
→ value-evidence access identity

governed Dima semantic/source binding
→ physical field locator

current principal
→ current-user Metabase value retrieval

LLM structured proposal
→ EntityValueAdoptionGate

approved bind
→ ResolvedAnalyticsIntent filter

ResolvedAnalyticsIntent
→ MetabaseSubstrateAdapter

execution
→ strict QueryReceipt / Evidence
```

No missing seam may be filled by name guessing.

### P13 must close DMP-P11-INTEGRATION-005

Before production Standard uses P11 value evidence:
- allowed semantic scopes come from accepted Dima authority/governed binding;
- value evidence comes from governed retrieval;
- access identity binds to existing
  `ExecutionAccessSnapshot.execution_access_fingerprint`;
- no second access fingerprint;
- `CURRENT_USER_RETRIEVAL` remains a typed claim, not self-proving authority.

---

## 12. Controlled Fast Track harvest in P12/P13

Fast Track may become useful only under an owning implementation ticket.

Candidate primitives:
- Dima-native chart/table rendering;
- run state machine;
- SSE/replay;
- cancel/retry;
- conversation lineage;
- typed Metabase gateway.

At the owning ticket:
1. fetch then-current Fast Track HEAD;
2. inspect exact primitive;
3. compare ownership;
4. port only the minimum contract;
5. keep Platform tests/authority/security.

Do not import Fast Ask semantic/retrieval heuristics into P12.

ask-v2 remains more restricted and reference-only.

---

## 13. Open debt — never silently mark GREEN

### Global production issuance

```text
DMP-P5-BLOCK-001 = OPEN
```

### P10B2/profile security

Unproven/profile-dependent:
- collection persistence permission;
- RLS;
- CLS;
- impersonation;
- advanced DB routing;
- cache/result reauthorization.

If a profile requires one, missing proof blocks that profile.

### P11

Uncertified:
- EV-05;
- EV-06;
- EV-07.

Do not build a large resolver merely because they are uncertified.

### P11 → P13

```text
DMP-P11-INTEGRATION-005 = OPEN
```

### P9 transport

Still gaps:
- dimension;
- time;
- relationship transport.

### P7/P8 semantic richness

Typed gaps remain around:
- textual relationship join conditions without structured join keys;
- calculated dimensions/model columns;
- view lineage;
- cube-level semantic metadata;
- other explicitly classified P8 gaps.

Do not parse free-form SQL/condition text just to erase gap counts.

### P6/Wren

Historical Wren runtime/compatibility gaps remain typed debt.
Do not patch Wren solely to claim parity.

---

## 14. Forbidden shortcuts

Do not add without a new owner + necessity proof:

```text
regex semantic truth
fuzzy matching as authority
stemming/morphology as authority
translation dictionary as truth
physical schema guessing
display-name semantic ownership
implicit FK join authority
raw SQL escape
silent requirement loss
silent field drop
automatic ambiguity pick
admin execution fallback
fake RLS/CLS/impersonation facts
parallel access fingerprint
LLM self-authorized semantic scope
large entity resolver framework
universal deterministic root-cause sequence
Metabase UI objects as business truth
bulk Fast Track/ask-v2 import
```

---

## 15. Testing philosophy

Prefer maximum information per test, not maximum test count.

Use:
- focused provider-free contract proof;
- inherited critical regressions;
- one pinned-live canary when runtime behavior is genuinely uncertain;
- pinned-source inspection when source settles the question;
- fixtures only for truths they actually model.

Do not rerun Luna/Sol unless the model-visible contract materially changes.

A CI GREEN does not prove architecture if the relevant product test is not actually executed.

---

## 16. Model policy

P11 empirically reinforced:

```text
Luna = default
Sol  = escalation/ceiling only when capability evidence justifies it
```

Sol did not rescue the P11 ambiguity family.

The successful pattern was:

```text
model reasons
→ model sometimes errs
→ Dima blocks only the material trust violation
→ model keeps reasoning
```

Do not turn that one successful guardrail into a larger deterministic resolver framework.

---

## 17. Handoff snapshot

At handoff preparation:

```text
audited functional baseline:
4b60bc3f1e6ab9526cd590a0989c1b227c5c43be

P11 workflow:
35816646368 = SUCCESS

governance:
35816646416 = SUCCESS

moving ask-v2 observation:
80e2e101298cfb750231b4161b9e888e65323a04

moving Fast Track observation:
946cb933441381078941767e8ac6205349ff81e3
```

These moving references can already be stale when this is read. Re-query before harvest.

---

## 18. First-session checklist

Before changing code:

```text
[ ] confirm current feat/dima-metabase-platform HEAD
[ ] confirm audited functional baseline above is an ancestor
[ ] read latest living-status tail
[ ] read latest decision receipts
[ ] read latest failure receipts
[ ] read P12 predev review
[ ] read P12 UX evidence matrix
[ ] read P12 ticket
[ ] observe current ask-v2/Fast Track refs read-only
[ ] verify current governance GREEN
[ ] do not implement without explicit milestone owner/predev
```

For P13:

```text
[ ] write P13 predev first
[ ] include DMP-P11-INTEGRATION-005 explicitly
[ ] preserve P5/P10 access identity ownership
[ ] preserve Dima semantic authority
[ ] require current-principal retrieval
[ ] use EntityValueAdoptionGate only as post-cognition truth gate
[ ] use Metabase adapter as execution substrate, not semantic brain
[ ] define QueryReceipt/Evidence path
[ ] define rollback/cancellation behavior where relevant
[ ] define focused provider-free proof before live integration
```

---

## 19. One-sentence state

**Dima now has an engine-independent semantic/trust core, a structured Metabase execution path,
semantic migration/equivalence contracts, isolated resource/security proofs, and a necessity-tested
LLM-first entity-value path; the project is currently closing the BI workspace composition before P13
wires the proven pieces into the first production Standard path.**


---

## TAKEOVER UPDATE — 2026-09-23

A new developer completed the required re-verification at HEAD
`56799687d2a8018dd60b0b909fb8b0be5d4a79c7`.

No product code was changed.

New read-only moving observations:
```text
ask-v2    = d430680a02256f4b9612730bd79b2e938a134132
Fast Track= 5280dd37451ded59ce181b93b015bc9dfafe0696
```

No merge/cherry-pick/rebase/write occurred.

P12 is now explicitly closed by `DMP-DEC-0028` with the certified wording:
```text
P12 BI WORKSPACE FEASIBILITY = CLOSED / CLASSIFICATION GREEN
```

P13 predevelopment is sealed by:
- `DMP-DEC-0029`;
- `backend/belgeler/metabase/predev/P13_PREDEVELOPMENT_REVIEW.md`;
- `backend/belgeler/metabase/tickets/P13_PRODUCTION_STANDARD_VERTICAL.md`.

The required next state is:
```text
P13 PRODUCT CODE = NOT AUTHORIZED PENDING SUPERVISOR REVIEW
```

Do not repeat P12 classification. On the next context reset, read the P13 predevelopment review and
ticket after this handoff/status/receipts.


---

## P12X ARCHITECTURE-MEASUREMENT OVERRIDE

DMP-DEC-0030 opens `P12X — METABASE NATIVE ENGINE / FORK SEAM EVALUATION`.

Current state:
```text
P12 = CLOSED / CLASSIFICATION GREEN
P13 = PAUSED FOR METABASE SEAM DECISION
P12X = V0+A+B LAB MEASUREMENT AUTHORIZED
fork / Seam C = NOT AUTHORIZED
Dima hooks / Seam D = NOT AUTHORIZED
```

Do not implement the P13 `standard_execution.py` / `execute_prepared()` design while P12X is open.

After context reset read:
1. this handoff;
2. living status;
3. DMP-DEC-0030;
4. `predev/P12X_METABASE_NATIVE_ENGINE_SEAM_EVALUATION.md`;
5. `tickets/P12X_SEAM_BENCHMARK.md`;
6. `UPSTREAM_ENGINE_HARVEST_MAP.md`.

P12X must stop after the first V0+A+B classification and return to supervisor.


---

## DMP-DEC-0031 — CURRENT HANDOFF OVERRIDE

The engine direction is now accepted:
```text
DIMA CONTROL PLANE
→ DIMA ENGINE BRIDGE
→ THIN DIMA METABASE ENGINE
→ NATIVE METABOT / MBQL / QUERY PROCESSOR / DRIVERS
```

Current-corpus native sanity is executable GREEN at `e35b68e4b7f60fc46c677317e7a001a1d66e88ac`:
workflow `35824464298`, job `107063206949`, PX-01 `126 == 126`, exact Boyahane resource, zero provider/tool errors.

The full V0+A+B Agent-API bake-off remains useful evidence but is no longer fork-blocking.

Next developer order:
1. read DMP-DEC-0031;
2. confirm engine repo/bootstrap state;
3. execute C0 from exact upstream history `v0.63.18 / 2ba2485c78d7e00a9a25f82c00fc201da71590c4`;
4. C1 stock-vs-fork parity on frozen cases;
5. only after C1 GREEN add C2 stable bridge and native parity;
6. establish C3 sync/patch-surface discipline;
7. stop before P13 hooks.

Do not implement `standard_execution.py`, `execute_prepared()` or Agent-API production Standard while this override is active.


---

## CURRENT HANDOFF — P12X C0→C3 COMPLETE

This section supersedes earlier P12X progress snapshots.

```text
Platform proof SHA                 = 094b5f6e0f1be939172b95fde66cab055c66ae54
engine gitlink                     = c56b71ab23bf2a2d266bac2fba8d165ac059d613
upstream base                      = 2ba2485c78d7e00a9a25f82c00fc201da71590c4

P12X-C0 fork/source build          = GREEN
P12X-C1 stock-vs-fork parity       = GREEN
P12X-C2 stable bridge parity       = GREEN
P12X-C3 upstream-sync              = GREEN
P13                                = STOP / NOT AUTHORIZED
```

C2 final proof:
`35839639339 = SUCCESS`, artifact `10742000058`,
digest `sha256:c799261cd36499c7579bdf1d6f97ecc07ce0cfaab782afe861deef169d877d94`.

The bridge is deliberately thin:
```text
Dima request/trace identity
→ restricted current-user session
→ /api/metabot/agent-streaming
→ native run-agent-loop
→ lossless-enough ordered stream observation
```

It does not implement planning, semantic resolution, skills, memory, tool selection, query
construction, Agent-API fallback, Wren fallback or raw SQL.

The next developer must **not** start the old P13 ticket verbatim. First perform a new P13
predevelopment reconciliation against DMP-DEC-0031..0034 and the certified engine bridge, while
preserving DMP-DEC-0029's authorize-exactly-what-executes trust invariant.

Supervisor-requested stop point has been reached.


---

# FINAL PRE-P13 HANDOFF — AUTHORITATIVE CURRENT ENTRY POINT

This section supersedes every earlier progress snapshot in this file.

## A. Exact repository state

```text
Platform branch                    = feat/dima-metabase-platform
Platform handoff HEAD              = 9179ad880ff0376fed0bb83971c9d61fe87e735c
final functional P12X proof SHA    = 094b5f6e0f1be939172b95fde66cab055c66ae54
current governance                 = 35841686789 = SUCCESS
current P12X regression            = 35841687850 = SUCCESS

engine repo                        = UpcyTech/dima-metabase-engine
engine certified HEAD              = c56b71ab23bf2a2d266bac2fba8d165ac059d613
Platform submodule path            = engine/metabase
Platform gitlink                   = c56b71ab23bf2a2d266bac2fba8d165ac059d613
upstream base                      = v0.63.18 / 2ba2485c78d7e00a9a25f82c00fc201da71590c4
```

Read-only moving source observations at final handoff:
```text
ask-v2                             = d22fb3626db0fe44ea543eee6531e5544cdf0b56
Fast Track                         = 8b9397b4f883f9c188a5fdadafa3db0dc418ec34
```

They are not source pins and were not merged/cherry-picked/rebased.

## B. Supervisor sequence result

```text
C0 exact fork/source build                    = CLOSED GREEN
C1 stock-vs-fork native capability parity     = CLOSED GREEN
C2 stable Dima bridge/direct-native parity    = CLOSED GREEN
C3 candidate-only upstream-sync discipline    = CLOSED GREEN
SUPERVISOR CHECKPOINT                         = REACHED
P13                                            = NOT STARTED
```

Key proof:
- C1 corrected rescore: `35834874194 = SUCCESS`;
- C2 final parity: `35839639339 = SUCCESS`, artifact `10742000058`,
  digest `sha256:c799261cd36499c7579bdf1d6f97ecc07ce0cfaab782afe861deef169d877d94`;
- C3 sync self-test: `35835881375 = SUCCESS`;
- current governance: `35841686789 = SUCCESS`;
- current P12X regression: `35841687850 = SUCCESS`.

## C. Certified architecture

```text
Model/native Metabot thinks and orchestrates analytics.
Dima owns material business/trust truth.
Metabase Engine executes the native analytical runtime.
```

Concretely:
```text
Dima product / durable conversation / decision intelligence
→ Dima semantic + security + provenance + evidence control plane
→ typed Dima Engine Bridge
→ pinned Dima Metabase Engine submodule
→ native Metabot:
   profiles
   skills
   native state/memory
   tool registry
   MBQL/query construction/repair
   Query Processor
   drivers
→ customer database
```

C2 introduced no Agent-API analytical fallback, Wren fallback or raw SQL escape.

## D. What the next developer reads first

Exact order:
1. `DIMA-METABASE-HANDOFF.md` — this final section first;
2. `DIMA-METABASE-DURUM.md` tail;
3. `backend/belgeler/metabase/DIMA_METABASE_DECISION_RECEIPTS.md` — DMP-DEC-0029 and 0031..0035;
4. `backend/belgeler/metabase/DIMA_METABASE_FAILURE_RECEIPTS.md` latest P12X receipts;
5. `backend/belgeler/metabase/predev/P12X_C2_ENGINE_BRIDGE_PREDEVELOPMENT.md`;
6. `backend/belgeler/metabase/UPSTREAM_ENGINE_HARVEST_MAP.md`;
7. only then the old P13 predev/ticket as historical input.

## E. P13 rule

Do **not** continue the old P13 ticket verbatim.

The old documents were written before the native-engine fork/bridge was certified. Their trust
invariants remain valuable, especially:
```text
Dima must authorize exactly the material execution that is actually executed and receipted.
```

But the implementation seam must be redesigned around the certified native engine bridge.

The first legal P13 action is **documentation/predevelopment reconciliation**, not product code.

Required replacement predev must answer:
- where Dima accepted semantic authority enters native Metabot;
- how allowed semantic scopes constrain native cognition without becoming a second planner;
- how current-principal retrieval and P11 value adoption occur before material authority is sealed;
- how the exact native query/material execution is bound to `ExecutionAccessSnapshot`;
- how the executed native artifact is represented/attested for `QueryReceipt`;
- how Evidence promotion remains Dima-owned;
- how cancellation/retry/replay preserve engine/request/access/provenance identity;
- how `DMP-P11-INTEGRATION-005` closes;
- what the first metric-only Standard vertical is;
- what remains profile-scoped because `DMP-P5-BLOCK-001` is still open.

## F. Open debt that must remain open

```text
DMP-P5-BLOCK-001             = OPEN
DMP-P11-INTEGRATION-005      = OPEN / P13 OWNER
EV-05 / EV-06 / EV-07       = UNCERTIFIED
P10B2 advanced security      = OPEN / profile-scoped
P9 dimension/time/relationship transport gaps = OPEN
P7/P8 semantic richness gaps = OPEN / typed
Wren historical compatibility gaps = typed debt
```

None of these are closed by C0-C3.

## G. Engine development rule

```text
engine change
→ test/certify in UpcyTech/dima-metabase-engine
→ exact engine commit SHA
→ explicit Platform engine/metabase gitlink bump
→ Platform governance/integration proof
```

Never consume moving engine `main` implicitly.

Upstream update:
```text
exact upstream stable ref
→ sync candidate
→ conflict/patch-surface/source-build/smoke/native regression
→ candidate branch
→ explicit manual promotion
```

No automatic promotion to engine `main` or production.

## H. Final stop state

```text
P12X                       = COMPLETE
repo                       = READY TO HAND OFF
engine                     = PINNED + SYNC GOVERNED
native bridge              = CERTIFIED
P13 product implementation = STOP
next action                = NEW P13 PREDEV RECONCILIATION
```

This is the intended supervisor stop point.


---

# FINAL P13A HANDOFF — NATIVE TRUST CONTRACT GREEN

Current closure state:
```text
P13A NATIVE TRUST CONTRACT = GREEN
P13B = NOT AUTHORIZED
```

Read in this order on context reset:
1. this section;
2. latest `DIMA-METABASE-DURUM.md` tail;
3. `DMP-DEC-0036`;
4. `P13_NATIVE_ENGINE_TRUST_BOUNDARY_REVIEW.md`;
5. `P13_NATIVE_ENGINE_STANDARD_VERTICAL.md`;
6. `backend/app/v3/native_execution.py`;
7. P10/P5 common-artifact adaptations.

Key implementation:
```text
Native Metabot candidate
→ NativeQueryCandidate
→ Dima ALLOW / CLARIFY_REPLAN / BLOCK
→ AuthorizedExecutionArtifact
→ P10 ExecutionAccessSnapshot
→ exact same artifact execution contract
→ P5 DimaQueryReceipt
→ Evidence later
```

Do not reopen Agent API as the primary Standard hot path.
Do not start P13B without a new predevelopment decision covering exact runtime source+image identity
and the first pinned-live vertical.

Closure evidence:
```text
product commit       17dea824dddf8af185d9596abc5bfdbedd11e04a
CI guard commit      c7a95fe4c48687914b89c350b8130793467c36e6
P13A                 35846503106 SUCCESS (12 + 61 + 7 PASS)
P10                  35846797870 SUCCESS
P5                   35846797938 SUCCESS
governance            35846797967 SUCCESS
engine gitlink        c56b71ab23bf2a2d266bac2fba8d165ac059d613
```


---

# P13B-0 HANDOFF — ATTESTATION DESIGN SEALED

Read next:
1. DMP-DEC-0037;
2. `P13B_NATIVE_CANDIDATE_ATTESTATION_AND_LIVE_STANDARD_REVIEW.md`;
3. latest `DIMA-METABASE-DURUM.md` tail;
4. P13 ticket P13B-0 section;
5. only then consider a supervisor-authorized engine feature branch.

Binding design:

```text
native server-side query occurrence
→ engine Lib/QP observation
→ NativeExecutionManifest
→ Dima physical→business mapping
→ NativeQueryCandidate authorization
→ exact same pMBQL /api/dataset execution
→ one P10 access identity
→ one P5 receipt
→ Evidence later
```

Important:
- no Python MBQL parser;
- no Agent API analytical fallback;
- no Wren fallback;
- no query reconstruction;
- no engine core patch;
- no engine gitlink bump in P13B-0.

Future engine patch is expected to be minimal and isolated:
```text
metabase.dima native attestation
+
metabase.dima engine identity
+
minimal route registration/build identity
```

First vertical:
```text
PX-01
June 2026 sales-order count
oracle = 126
```

Stop:
```text
P13B NATIVE ATTESTATION DESIGN = SEALED
P13B IMPLEMENTATION = PENDING SUPERVISOR AUTHORIZATION
```


---

## P13B-0 CLOSURE PROOF

```text
predev/governance commit = 90c6da7d5bf50c305f4d91c02263660bf8b9232a
governance               = 35852118661 SUCCESS
engine gitlink           = c56b71ab23bf2a2d266bac2fba8d165ac059d613
engine source changes    = 0
live P13B implementation = 0
```

Current supervisor stop remains:
```text
P13B NATIVE ATTESTATION DESIGN = SEALED
P13B IMPLEMENTATION = PENDING SUPERVISOR AUTHORIZATION
```


---

# NEW DEVELOPER AUTHORITATIVE HANDOFF — 2026-09-23

A consolidated onboarding document now exists:

DIMA-METABASE-NEW-DEVELOPER-HANDOFF.md

For a new developer with no prior context, read that file first.

It consolidates:
- project history and architecture transitions;
- exact repo/branch/engine state;
- P12X/P13A/P13B-0 certification;
- DMP-DEC-0037;
- code/file ownership;
- source-audit conclusions;
- proposed engine patch surface;
- exact next sequence;
- open debt;
- failure protocol;
- absolute stop conditions.

Verified immediately before this handoff commit:

    Platform HEAD before handoff commit = b9bcc110e4d352a3bada7587e7a812abf7b68ed3
    engine gitlink/main                 = c56b71ab23bf2a2d266bac2fba8d165ac059d613
    current-head governance             = 35852421592 SUCCESS

    ask-v2 read-only observation        = 1cdddb024fd0d8f4e5548cd7ca862afc3b3ee404
    Fast Track read-only observation    = 8b9397b4f883f9c188a5fdadafa3db0dc418ec34

Current stop remains:

    P13B NATIVE ATTESTATION DESIGN = SEALED
    P13B IMPLEMENTATION = PENDING SUPERVISOR AUTHORIZATION

Do not begin an engine patch or live P13B orchestration without a new supervisor authorization.


---

## NEW-DEVELOPER HANDOFF PUBLISH PROOF

    onboarding/handoff commit = e40cdbf8eebf0aad393a292ec1b10ce03ff5a9c2
    governance                = 35853381889 SUCCESS
    product-code changes      = 0
    engine-source changes     = 0
    engine gitlink bump       = 0
    source-branch writes      = 0

The handoff package is therefore governance-certified.

Current stop remains unchanged:

    P13B NATIVE ATTESTATION DESIGN = SEALED
    P13B IMPLEMENTATION = PENDING SUPERVISOR AUTHORIZATION
