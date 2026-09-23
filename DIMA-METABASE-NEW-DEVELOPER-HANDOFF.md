# DIMA METABASE PLATFORM — NEW DEVELOPER HANDOFF

**Authoritative onboarding snapshot — 2026-09-23**

This document is the current handoff for a developer with **zero prior chat context**. Read it before
touching code. Historical handoffs and older P13/P13B stop-points remain useful as evidence, but they
are superseded by the exact state below.

## 0. One-sentence state

Dima now uses a pinned native Metabase engine for analytical cognition/query-candidate authoring,
while Dima remains the authority for business semantics, execution authorization, security,
provenance, receipts and Evidence. P13B provider-free trust + semantic availability are GREEN on the
current dima.3 engine; the **only next model-bearing action is one Luna PX-01 live canary, then STOP
for supervisor audit**.

## 1. Exact authoritative repository state

Platform:

```text
repo    = cagataysntrk/dima-backend-feat-wren-strict-agentic
branch  = feat/dima-metabase-platform
HEAD    = 2ea02530fbaa2999d1dac1d6166064e49bd8f51c
```

Certified engine:

```text
repo           = UpcyTech/dima-metabase-engine
main           = 10960f7c36bb84425b1794b557b78211c14d7f5f
Platform gitlink engine/metabase
               = 10960f7c36bb84425b1794b557b78211c14d7f5f
release        = 0.63.18-dima.3
revision       = 3
upstream base  = 2ba2485c78d7e00a9a25f82c00fc201da71590c4
semantic behavior changes = 0
```

Current exact-head proofs:

```text
engine P13B certification
35909836120 = SUCCESS

Platform governance
35911051608 = SUCCESS

provider-free native semantic availability
35911051644 = SUCCESS

P13B provider-free trust/regression on current Platform HEAD
35914038368 = SUCCESS
```

The P13B provider-free job includes:
- semantic-availability contract tests;
- observed-vs-expected P13B trust tests;
- P13A + P5 + P10 regressions;
- P12X C2 provider-free native bridge regression.

Do not describe P13B-3 as GREEN yet. The new dima.3 live Luna canary has **not** been spent.

## 2. Product architecture in plain terms

Current ownership:

```text
Native Metabot
= analytical cognition
= tool orchestration
= native query-candidate author

Dima
= canonical business semantic truth
= execution authority
= security/access authority
= provenance authority
= receipt authority
= Evidence authority
= durable conversation / decision intelligence truth

Metabase Query Processor
= MBQL execution engine

Database
= numerical/data truth
```

Binding doctrine:

```text
LLM_FIRST_COGNITION + DIMA_OWNED_TRUTH
```

The hot path is **not**:
- Dima deterministic NL-to-query planning;
- Agent API analytical execution;
- Wren fallback;
- raw SQL fallback;
- a Python MBQL parser;
- fuzzy/regex/morphological semantic matching.

## 3. Why P13 exists

P12X proved that Dima can use a pinned native Metabot engine. It did **not** prove that any query
Metabot produces is acceptable business truth.

P13 adds the trust boundary:

```text
Accepted Dima authority
→ native Metabot authors candidate
→ engine attests what was actually built
→ Dima maps observed facts to canonical semantics
→ ALLOW | CLARIFY_REPLAN | BLOCK
→ exact same artifact executes
→ P10 access identity
→ P5 QueryReceipt
→ independent correctness gate
→ VERIFIED Evidence
```

Dima verifies. It does not rewrite the native query.

## 4. P13A — already closed

P13A introduced:
- `NativeQueryCandidate`;
- `NativeCandidateAuthorizationGate`;
- `AuthorizedExecutionArtifact`;
- exact artifact fingerprint/mutation protection;
- use of the existing P10 access identity;
- use of the existing P5 receipt system.

P13A is historical prerequisite and remains GREEN.

Do not create:
- a second access fingerprint;
- a second receipt type;
- a parallel native receipt system.

## 5. P13B-1 — engine attestation and identity

P13B engine work is isolated under Dima-owned engine namespaces.

Core engine files:

```text
src/metabase/dima/native_attestation.clj
src/metabase/dima/api.clj
test/metabase/dima/native_attestation_test.clj
test/metabase/dima/api_test.clj
```

Minimal upstream registration/build surface only:
- route registration;
- Dima build/runtime identity wrapper.

The engine exposes:
- exact native query occurrence keyed by conversation/query id;
- exact serialized original pMBQL;
- exact pMBQL fingerprint;
- bounded query facts;
- current-user permission provenance;
- authenticated Metabase subject;
- exact engine/build/image/instance identity.

Hard invariant:

```text
ORIGINAL pMBQL
= immutable execution identity

QP-expanded / normalized semantic view
= observation only
```

Never execute the observation view.

Required identity chain:

```text
fingerprint(attested original A)
==
fingerprint(authorized original A)
==
fingerprint(submitted original A)
==
fingerprint(receipted original A)
```

## 6. The decisive live RED and its real root cause

The latest meaningful live dima.2 canary was:

```text
workflow = 35895585715
model    = openrouter/openai/gpt-5.6-luna
case     = PX-01
question = Haziran 2026'da kaç satış siparişi açıldı?
oracle   = 126
status   = RED
owner    = dima-trust-authorization
error    = NATIVE_AGGREGATION_MISMATCH: PX-01 requires exact COUNT(*)
```

The exact native query used:

```text
DISTINCT(field)
```

rather than canonical `COUNT(*)`.

This was **not** permission to weaken Dima trust. Dima correctly blocked a semantically wrong native
query.

Root cause:

```text
Metabot had physical schema
but did not have the canonical Dima-managed business metric
needed for PX-01.
```

Therefore the root solution is **semantic resource availability**, not:
- prompt teaching;
- regex;
- fuzzy matching;
- morphology/stemming;
- query repair patches;
- hard-coded PX-01 query construction;
- accepting DISTINCT as equivalent to COUNT(*).

## 7. Canonical semantic metric path — P9/P9B reused

PX-01 metric truth must originate from the same canonical Dima semantic truth used by authorization:

```text
DimaSemanticSpec
→ ManagedResourcePolicy
→ P9 desired resource
→ P9/P9B transport
→ native Metabase Metric
→ ManagedResourceBinding
```

Canonical metric:

```text
metric.sales_order_count
name        = Sales Order Count
base source = satis_siparisleri
aggregation = COUNT(*)
ownership   = DIMA_MANAGED
```

Important distinction:

P9B may use a Metabase Agent/resource-management endpoint to provision the metric **out of band**.

Allowed:

```text
DimaSemanticSpec
→ provision managed native Metabase semantic resource
```

Forbidden:

```text
user question
→ Dima analytical planner
→ Agent API analytical execution
```

Agent API is not the Standard analytical hot path.

## 8. Provider-free semantic availability — now GREEN

Current exact-head provider-free native proof:

```text
workflow 35911051644 = SUCCESS
engine   10960f7c36bb84425b1794b557b78211c14d7f5f
runtime  v0.63.18-dima.3
```

The proof runs with **no model credentials** and under the same restricted analytical principal class
used by PX-01.

It proves:
- P9/P9B can provision the Dima-managed COUNT(*) metric;
- native search discovers the metric;
- native `read_resource` can read the metric resource/identity;
- the same restricted principal can read the persisted metric card;
- the exact persisted definition matches the P9B canonical projection after stripping only
  runtime-volatility such as `lib/uuid`;
- stable Metabase local id + portable entity id are bound back to `ManagedResourceBinding`;
- semantic context/version/ownership are exact.

Do **not** hard-code the ephemeral local metric id from any prior run. The authoritative identity is
the current run's typed `ManagedResourceBinding`.

## 9. Native metric attestation — dima.3 root fix

Native Metabot can represent a metric aggregation as a persistent metric reference. Therefore
attestation must understand the native metric identity without pretending the metric never existed.

Engine dima.3:
- preserves the original native pMBQL;
- records native metric reference location;
- records Metabase metric local id;
- records stable Metabase metric entity id;
- uses Metabase's own QP preprocessing / metric expansion for **observation**;
- derives expanded aggregation facts from the native Metabase-owned definition;
- currently certifies the bounded one-metric aggregation case only;
- keeps COUNT(field) distinct from COUNT(*);
- keeps DISTINCT(field) distinct from COUNT(*).

Platform contract:

```text
NativeMetricReferenceFact
stage_number
aggregation_index
metabase_metric_id
metabase_metric_entity_id
```

Platform trust then requires exact managed-resource binding:

```text
tenant
resource_kind == METRIC
canonical_id == metric.sales_order_count
ownership == DIMA_MANAGED
semantic_context_version
applied_version
metabase_local_id
metabase_entity_id
```

Wrong, missing, ambiguous, stale or identity-mismatched bindings fail closed.

This is the intended chain:

```text
native metric ref identity
+
Metabase-owned expanded definition facts
+
P9 ManagedResourceBinding
+
DimaSemanticSpec
→ trusted semantic verification
```

## 10. Current P13B-v1 capability — intentionally narrow

Supported current certification target:

```text
one metric
one source
COUNT(*)
optional exact absolute period
one material query
no arbitrary non-temporal filter
no join
no relationship
no arbitrary calculated metric
```

This narrowness is not a bug.

Not authorized now:
- arbitrary calculated metrics;
- nested metric algebra;
- cross-source metrics;
- arbitrary formulas;
- generic semantic graph;
- P13C entity-value integration;
- breakdown/ranking generalization;
- relationship reasoning;
- P14 Research.

## 11. Current key Platform code map

Semantic/resource truth:

```text
backend/app/v3/semantic_spec.py
backend/app/v3/resource_provisioning.py
backend/app/v3/resource_transport.py
backend/app/v3/substrate/metabase/execution_binding.py
```

Native Standard trust:

```text
backend/app/v3/native_standard/contracts.py
backend/app/v3/native_standard/trust.py
backend/app/v3/native_execution.py
backend/app/v3/security_identity.py
backend/app/v3/execution_identity.py
backend/app/v3/evidence.py
```

Native bridge:

```text
backend/app/v3/substrate/metabase/native_models.py
backend/app/v3/substrate/metabase/native_engine.py
```

P13B lab/proof:

```text
backend/lab/metabase/p13b/px01_semantic_availability.py
backend/lab/metabase/p13b/px01_live_standard.py
backend/tests/test_v3_p13b_semantic_availability.py
backend/tests/test_v3_p13b_native_standard.py
.github/workflows/dima-metabase-p13b.yml
.github/workflows/dima-metabase-p13b-semantic-availability.yml
.github/workflows/dima-metabase-p12x-c2-live.yml
```

## 12. What is GREEN now

```text
P12X engine fork/bridge                   = GREEN
P13A native trust contract                = GREEN
P13B engine attestation/runtime identity  = GREEN
P13B native metric attestation dima.3     = GREEN
P13B provider-free Platform trust         = GREEN
P13B provider-free semantic availability  = GREEN
P13B current-head regressions             = GREEN
governance                                = GREEN

P13B-3 one Luna live semantic canary       = NOT YET RUN ON dima.3
P13 Standard final closure                 = NOT CLAIMED
production multi-instance security closure = NOT CLAIMED
```

## 13. The exact next legal action

Before any write:
1. re-query Platform branch HEAD;
2. re-query engine main and Platform gitlink;
3. confirm they still match this handoff or read newer receipts;
4. confirm governance/provider-free proofs remain GREEN;
5. inspect the current live workflow and P13B artifacts.

Then:

```text
ONE Luna PX-01 canary only
model    = openrouter/openai/gpt-5.6-luna
question = Haziran 2026'da kaç satış siparişi açıldı?
oracle   = 126
primary user turns = 1
```

No Sol.
No C1.
No six-case corpus.
No automatic retry.

The existing live job is in:

```text
.github/workflows/dima-metabase-p12x-c2-live.yml
job = p13b-px01-live
```

It already:
- builds exact dima.3;
- boots one exact engine instance;
- provisions/verifies the Dima-managed metric in that same live runtime;
- passes the resulting semantic-availability receipt to `px01_live_standard.py`;
- asks one Luna turn;
- attests the exact query;
- authorizes against Dima truth;
- executes exact same pMBQL via `/api/dataset`;
- seals P5 receipt;
- checks independent oracle;
- promotes Evidence only after correctness.

Current trigger is a push whose commit message contains `[p13b-live]`.

**Do not make a fake product change merely to spend the canary.**
If no legitimate code change exists, the clean solution is CI-only trigger plumbing that explicitly
permits this already-authorized one P13B live job to be manually dispatched, without altering product,
semantic, model or trust behavior.

## 14. What to do after the one canary

If GREEN:

```text
record exact run/artifact/fingerprints
update living status + receipts
do not generalize
STOP for supervisor audit
```

If RED:

```text
STOP
preserve failure artifact
classify failure owner
do not retry automatically
do not prompt-patch
do not regex/fuzzy/morph-patch
do not weaken trust
return to supervisor with the exact evidence
```

The latest supervisor instruction is explicit:

```text
provider-free semantic availability
→ native metric attestation
→ one Luna PX-01 canary
→ STOP for supervisor audit
```

## 15. Forbidden shortcuts

Do not introduce or revive:

```text
regex semantic authority
fuzzy semantic authority
stemming/morphology as truth
translation dictionary as truth
display-name guessing
physical-schema guessing
manual Python MBQL parser
Python query normalizer/repairer
hard-coded PX-01 query
raw SQL analytical fallback
Wren analytical fallback
Agent API analytical hot path
admin analytical fallback
silent requirement loss
silent field drop
automatic ambiguity choice
second access identity
second receipt system
Metabase UI object as Dima business truth
prompt injection that teaches the answer
```

A RED is evidence, not permission to patch.

## 16. Open debt that remains outside this bounded handoff

Still open globally:
- `DMP-P5-BLOCK-001`;
- `DMP-P11-INTEGRATION-005` — P13C owner, not now;
- EV-05 / EV-06 / EV-07;
- P10B2 RLS / CLS / impersonation / advanced routing / cache-result reauthorization;
- P9 dimension / time / relationship transport gaps;
- P7/P8 calculated / relationship / view semantic gaps;
- historical Wren typed gaps;
- multi-instance production runtime-identity/deployment closure.

Do not silently mark these GREEN because PX-01 passes.

## 17. Mandatory read order after context loss

Read in this order:

1. `DIMA-METABASE-NEW-DEVELOPER-HANDOFF.md` — this file.
2. tail of `DIMA-METABASE-DURUM.md`.
3. `backend/belgeler/metabase/predev/P13B_NATIVE_CANDIDATE_ATTESTATION_AND_LIVE_STANDARD_REVIEW.md`.
4. `backend/belgeler/metabase/tickets/P13_NATIVE_ENGINE_STANDARD_VERTICAL.md` for historical milestone contract.
5. latest P13B sections in decision/failure receipts.
6. current `backend/app/v3/native_standard/**`.
7. current P13B lab scripts/tests/workflows.
8. engine `src/metabase/dima/**` and its exact current tests.

When documents conflict with current certified evidence, the latest exact SHA + CI artifact wins, and
the discrepancy must be recorded rather than silently guessed.

## 18. Final architectural invariant

The target is:

```text
DimaSemanticSpec
→ Dima-managed semantic resource
→ native Metabot reasoning
→ exact native query
→ engine observation/attestation
→ Dima authorization
→ exact same execution
→ P10 access identity
→ P5 receipt
→ independent oracle
→ VERIFIED Evidence
```

Do not teach Metabot the answer.

Give Metabot the canonical business semantic resource the architecture says it should have, then let
native Metabot reason. Dima remains the truth boundary.
