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
