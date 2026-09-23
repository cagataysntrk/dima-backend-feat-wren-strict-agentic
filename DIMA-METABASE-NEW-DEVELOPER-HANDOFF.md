# DIMA METABASE PLATFORM — NEW DEVELOPER HANDOFF

AUTHORITATIVE ONBOARDING DOCUMENT

This file is written so a developer with no prior chat context can understand what the project is,
why the architecture changed, what has already been certified, what is still open, and exactly what
may happen next.

Read this file first. Then follow the exact read order in section 13.

## 0. One-sentence project state

Dima has moved from a Wren/Agent-API-centered analytics architecture to a pinned native Metabase
engine fork in which native Metabot owns analytical cognition/query-candidate authoring, while Dima
owns business semantic truth, execution authority, security, provenance, receipts and evidence.

Current stop:

    P13A NATIVE TRUST CONTRACT = GREEN
    P13B NATIVE ATTESTATION DESIGN = SEALED
    P13B IMPLEMENTATION = PENDING SUPERVISOR AUTHORIZATION

No live P13B Standard orchestration is currently authorized.

## 1. Exact repository state

Platform:

    repo:
    cagataysntrk/dima-backend-feat-wren-strict-agentic

    branch:
    feat/dima-metabase-platform

    handoff source HEAD:
    b9bcc110e4d352a3bada7587e7a812abf7b68ed3

    P13B-0 predevelopment/governance commit:
    90c6da7d5bf50c305f4d91c02263660bf8b9232a

    P13B-0 closure commit:
    b9bcc110e4d352a3bada7587e7a812abf7b68ed3

    P13B-0 governance:
    35852118661 = SUCCESS

    current-head governance:
    35852421592 = SUCCESS

Pinned Dima Metabase Engine:

    repo:
    UpcyTech/dima-metabase-engine

    Platform submodule path:
    engine/metabase

    gitlink / engine main:
    c56b71ab23bf2a2d266bac2fba8d165ac059d613

    upstream Metabase base:
    v0.63.18
    2ba2485c78d7e00a9a25f82c00fc201da71590c4

    runtime tag:
    v0.63.18-dima.0

The engine gitlink is deliberate and immutable until an explicit engine change is separately
implemented, tested, certified and approved for a Platform gitlink bump.

Other active branches — READ ONLY:

    ask-v2:
    1cdddb024fd0d8f4e5548cd7ca862afc3b3ee404

    Fast Track:
    8b9397b4f883f9c188a5fdadafa3db0dc418ec34

These are moving references, not source pins.

Absolute rule:

    NO MERGE
    NO CHERRY-PICK
    NO REBASE
    NO WRITE

If a useful primitive is ever needed from another branch, use controlled harvest only:
identify the owning milestone, inspect the exact primitive, re-derive or minimally port the
architecture-independent contract into Platform, and re-certify it here.

## 2. Why the architecture changed

The project has gone through three materially different execution eras.

### Era A — Wren-centered Dima

Early Dima used:

    Dima cognition
    → Dima semantic authority
    → Wren semantics/execution
    → DB

What survived:
- semantic authority;
- Standard/Research separation;
- fail-closed behavior;
- typed temporal semantics;
- requirement completeness;
- evidence and provenance discipline;
- bounded research runtime;
- authority/query identity checks.

What did not survive as current production architecture:
- Wren as the universal semantic/execution owner.

### Era B — Metabase Agent API substrate

The first Metabase architecture moved analytics execution toward Agent API and introduced:
- Metabase transport/client boundary;
- compiler/canonical projection;
- one P5 receipt identity;
- one P10 access identity;
- resource lifecycle and parity infrastructure.

Historical modules still exist:
- MetabaseAgentClient;
- MetabaseProjectionCompiler;
- MetabaseCanonicalizer;
- MetabaseSubstrateAdapter;
- CanonicalProjection.

Do not delete them. They still matter for regression, migration and resource-management contracts.

They are no longer the primary Standard analytical hot path.

### Era C — current architecture: pinned native Metabase Engine

P12X proved that Dima can operate against a pinned fork of Metabase's native Metabot stack.

Current architecture:

    DIMA PRODUCT
    → DIMA CONVERSATION / DECISION INTELLIGENCE
    → DIMA SEMANTIC + SECURITY + PROVENANCE + EVIDENCE CONTROL PLANE
    → TYPED NATIVE ENGINE BRIDGE
    → PINNED DIMA METABASE ENGINE
    → native Metabot / profiles / skills / state / memory
    → native query construction + repair
    → MBQL / Query Processor / drivers
    → CUSTOMER DB

Current ownership:

    Native Metabot
    = analytical cognition
    = orchestration
    = query-candidate author

    Dima
    = business semantic truth
    = execution authority
    = security authority
    = provenance authority
    = receipt/evidence authority
    = durable conversation/research/decision truth

    Metabase Query Processor
    = execution engine

    Database
    = numeric result truth

Binding doctrine:

    LLM_FIRST_COGNITION + DIMA_OWNED_TRUTH

Model/native Metabot may think freely. Dima stops material trust violations.

## 3. P12X — fork and bridge certification

P12X established the engine/submodule model.

Certified sequence:

    C0 exact fork/source build                 = GREEN
    C1 stock-vs-fork native capability parity  = GREEN
    C2 stable Dima native bridge parity         = GREEN
    C3 upstream-sync discipline                 = GREEN

Important proof:
- C2 final parity workflow: 35839639339 = SUCCESS;
- engine gitlink: c56b71ab23bf2a2d266bac2fba8d165ac059d613;
- no Agent API analytical fallback;
- no Wren fallback;
- no raw SQL fallback.

P12X solved:

    Can Dima call a pinned native Metabot engine reliably?
    YES

It did not prove that every query produced by native Metabot is correct business truth.

That distinction is why P13 exists.

## 4. P13A — native trust contract

P13A is CLOSED GREEN.

Certified wording:

    P13A NATIVE TRUST CONTRACT = GREEN

Core implementation:
backend/app/v3/native_execution.py

P13A introduced NativeQueryCandidate, NativeCandidateAuthorizationGate and
AuthorizedExecutionArtifact.

NativeQueryCandidate represents one exact native query occurrence.

NativeCandidateAuthorizationGate has bounded outcomes:

    ALLOW
    CLARIFY_REPLAN
    BLOCK

Dima verifies. Dima does not rewrite MBQL.

AuthorizedExecutionArtifact is the engine-independent trust identity shared by P10/P5.

P10 remains the single access authority:
ExecutionAccessSnapshotIssuer.

P5 remains the single receipt authority:
DimaQueryReceiptSealer.

Historical CanonicalProjection remains supported through a compatibility adapter.

P13A proof:

    P13A workflow             35846503106 = SUCCESS
    focused P13A              12 PASS
    P5 + P10 critical         61 PASS
    P12X C2 bridge             7 PASS

    P10 regression            35846797870 = SUCCESS
    P5 regression             35846797938 = SUCCESS
    governance                35846797967 = SUCCESS

P13A did NOT prove:

    P13 Standard GREEN                         NO
    production security GREEN                  NO
    native analytical correctness GREEN        NO
    live P13B vertical GREEN                   NO

## 5. Why P13B-0 was necessary

Provider-free P13A could safely use caller-constructed candidate facts in tests.

A live production path cannot.

The following fields must not be trusted merely because Platform copied expected facts into a
candidate:

    semantic_refs
    resource_bindings
    native_validation_refs
    time_scope_fingerprint
    material_filter_count
    material_join_count
    query_count

Forbidden live authorization pattern:

    AcceptedIntent
    → copy expected facts into candidate
    → compare candidate back to AcceptedIntent
    → ALLOW

That is tautological authorization.

Correct principle:

    Metabase tells us what query it actually built.

    Dima decides whether that actual query
    is allowed to become business truth.

Two forward blockers:

    DMP-P13B-BLOCK-001
    NATIVE CANDIDATE FACT PROVENANCE

    DMP-P13B-BLOCK-002
    AUTHORIZED ARTIFACT ↔ RUNNING RUNTIME IDENTITY BINDING

They do not make P13A RED.

## 6. P13B-0 — source audit and sealed design

P13B-0 is complete as design/predevelopment only.

Decision:
DMP-DEC-0037 — P13B native candidate attestation and runtime identity boundary.

Review:
backend/belgeler/metabase/predev/P13B_NATIVE_CANDIDATE_ATTESTATION_AND_LIVE_STANDARD_REVIEW.md

Certified wording:

    P13B NATIVE ATTESTATION DESIGN = SEALED
    P13B IMPLEMENTATION = PENDING SUPERVISOR AUTHORIZATION

All Metabase implementation claims were audited against exact upstream:

    metabase/metabase@
    2ba2485c78d7e00a9a25f82c00fc201da71590c4

Not documentation, not latest master.

Pinned source proves:
- construct_notebook_query repairs, permission-checks sources, validates and resolves to pMBQL;
- it emits exact resolved pMBQL plus query-id;
- native agent memory stores query-id to exact query;
- final state persists it;
- persistence retains query-id/query structured output.

Therefore live query occurrence can be bound server-side by:

    conversation_id + native_query_id

Caller-provided query facts are not proof.

## 7. Metabase owns MBQL understanding

Strictly forbidden:

    Python recursive MBQL parser
    Python aggregation parser
    Python filter parser
    Python join parser
    Python query repair
    Python MBQL normalizer
    recreation of Metabase Lib

Metabase Lib/QP owns observation of:
- database id;
- primary source;
- referenced sources;
- aggregation;
- breakouts;
- filters;
- joins;
- implicit joined sources;
- order/limit/stage facts;
- permission-relevant table use.

Dima maps physical/query facts to business truth through:
- DimaSemanticSpec;
- CurrentCatalogSnapshot;
- SourceLineage;
- governed resource bindings.

Metabase must not invent Dima semantic IDs.

## 8. NativeExecutionManifest design

P13B requires a bounded native attestation envelope. It is not a universal query AST.

For the first vertical, the engine-side manifest is expected to attest:

    native_query_id
    conversation_id

    exact serialized pMBQL
    exact pMBQL fingerprint

    database_id
    primary_source_table_id
    referenced source/table ids

    aggregation count
    aggregation operator/identity
    referenced field identities where materially required

    breakout count
    material filter count
    observed temporal predicate facts

    explicit join count
    implicit joined source ids

    order-by presence
    limit
    stage/query count

    typed native validation provenance
    typed permission provenance

    authenticated Metabase subject

    runtime identity

Portable query may remain audit/debug material.
Portable query is not trust authority.
Exact resolved pMBQL is the execution trust object.

## 9. Engine patch decision

P13B-0 concluded:

    ENGINE PATCH REQUIRED = YES

But:

    ENGINE PATCH AUTHORIZED NOW = NO

Reason:
- native server-side state already contains the exact query;
- existing public surfaces do not expose the required bounded typed attestation manifest;
- runtime tag/short git hash is not enough for production-grade exact runtime identity.

Future patch must be isolated and observational.

Proposed minimum engine files:

    src/metabase/dima/native_attestation.clj
    src/metabase/dima/api.clj

    test/metabase/dima/native_attestation_test.clj
    test/metabase/dima/api_test.clj

    src/metabase/api_routes/routes.clj
      minimal route registration only

    .dima/docker/Dockerfile.c0
      immutable build identity only

Forbidden engine modifications unless a future classified gap proves necessity:

    run-agent-loop cognition
    profiles
    skills
    tool selection
    construct_notebook_query semantics
    query repair semantics
    Query Processor semantics
    drivers

If implementation discovers that the manifest cannot be produced without changing those owners:

    STOP-THE-LINE

## 10. Runtime identity design

Current runtime tag v0.63.18-dima.0 is not sufficient as exact source identity.

The upstream build surface exposes only a short git hash at runtime.

P12X was safe because CI externally pinned source/image.

P13B requires request-relevant identity:

    engine repository
    exact 40-char engine SHA
    upstream base SHA
    Dima engine release
    immutable build/image identity
    running instance identity
    candidate/request identity
    receipt runtime identity

Chosen P13B-0 design:

    minimal isolated Dima engine identity seam
    GET /api/dima/engine/v1/identity

It may expose immutable build/runtime identity facts only.
No business logic.

Required hard equality:

    candidate engine identity
    ==
    attested running engine
    ==
    runtime executing the query
    ==
    runtime sealed in receipt

Mismatch must fail closed.

## 11. Exact same-artifact execution decision

Selected future execution seam:

    POST /api/dataset

Pinned Metabase source proves:
- endpoint accepts MBQL5 through backend normalization;
- execution uses native Query Processor/userland middleware;
- current-user execution context/permission machinery remains active;
- no Agent API analytical reconstruction is required.

Future invariant:

    native exact pMBQL A
    → attest A
    → authorize A
    → execute A through /api/dataset
    → receipt A

Forbidden:

    authorize A → Agent API constructs B → execute B
    authorize pMBQL → convert to SQL → execute SQL
    native fail → Agent API analytical fallback
    native fail → Wren fallback

QP may add its normal middleware/security/preprocessing.
Dima may not analytically re-author the query between authorization and execution.

## 12. First future live Standard vertical

Selected case:

    PX-01

    question:
    Haziran 2026'da kaç satış siparişi açıldı?

    source:
    satis_siparisleri

    aggregation:
    COUNT(*)

    time field:
    acilis_tarihi

    period:
    [2026-06-01, 2026-07-01)

    independent expected scalar:
    126

Frozen oracle source:
backend/lab/metabase/p12x/corpus_v1.json

Oracle runner:
backend/lab/metabase/p12x/build_oracle.py

The independent oracle runs against Boyahane DuckDB independently of Metabot/query-under-test.

Do not remove the period to simplify the implementation.

## 13. Exact read order for the new developer

Read before any write:

1. DIMA-METABASE-NEW-DEVELOPER-HANDOFF.md
2. tail of DIMA-METABASE-DURUM.md
3. final sections of DIMA-METABASE-HANDOFF.md
4. backend/belgeler/metabase/DIMA_METABASE_DECISION_RECEIPTS.md
   especially DMP-DEC-0031 through DMP-DEC-0037
5. backend/belgeler/metabase/DIMA_METABASE_FAILURE_RECEIPTS.md latest receipts
6. backend/belgeler/metabase/predev/P13_NATIVE_ENGINE_TRUST_BOUNDARY_REVIEW.md
7. backend/belgeler/metabase/predev/P13B_NATIVE_CANDIDATE_ATTESTATION_AND_LIVE_STANDARD_REVIEW.md
8. backend/belgeler/metabase/tickets/P13_NATIVE_ENGINE_STANDARD_VERTICAL.md
9. backend/app/v3/native_execution.py
10. backend/app/v3/security_identity.py
11. backend/app/v3/execution_identity.py
12. backend/app/v3/substrate/metabase/native_engine.py
13. backend/app/v3/substrate/metabase/native_models.py
14. P12X corpus/oracle/bridge files
15. only then exact pinned engine source

Do not start from old Agent-API P13 documents without reading DMP-DEC-0036 and DMP-DEC-0037 first.

## 14. Current code/file ownership map

Dima truth plane:

backend/app/v3/authority.py
- accepted Standard/Research authority contracts.

backend/app/v3/analytics_contract.py
- engine-independent accepted analytics intent.

backend/app/v3/native_execution.py
- P13A native candidate trust contract;
- NativeQueryCandidate;
- AuthorizedExecutionArtifact;
- bounded authorization gate;
- exact-artifact integrity.

backend/app/v3/security_identity.py
- single P10 access snapshot issuer.

backend/app/v3/execution_identity.py
- single P5 query receipt sealer.

backend/app/v3/evidence.py
- evidence promotion owner.

Native engine transport:

backend/app/v3/substrate/metabase/native_engine.py
- thin current-user native engine bridge;
- not analytical planner.

backend/app/v3/substrate/metabase/native_models.py
- native bridge request/observation/identity models.

Future live P13B owner is reserved as:

    backend/app/v3/native_standard/

This path is not live implementation yet.

Governance forbids it from depending on old analytical seams:
- compiler;
- canonicalizer for analytical construction/introspection;
- execution adapter;
- MetabaseAgentClient.

engine/metabase is a submodule/gitlink.
Do not edit engine source inside Platform.

## 15. Engine development protocol

If supervisor authorizes the P13B engine patch:

    exact P13B design
    → isolated feature branch in UpcyTech/dima-metabase-engine
    → implement only isolated Dima attestation/identity seam
    → native unit/API tests
    → full source build
    → P12X native capability regression
    → DIMA_PATCH_SURFACE report
    → exact engine commit SHA
    → STOP
    → supervisor review
    → explicit Platform gitlink bump
    → Platform integration proof

Never:
- edit the submodule working tree as ordinary Platform source;
- consume moving engine main implicitly;
- bump gitlink before engine certification;
- mix engine patch and Platform integration into one uncontrolled change.

## 16. Required future P13B tests

At minimum:

    caller copies expected semantic_ref without native evidence → cannot authorize
    caller copies expected source binding without native evidence → cannot authorize
    fake time_scope_fingerprint → cannot authorize
    hidden filter while caller claims zero → manifest sees filter → BLOCK
    implicit join while caller claims zero → manifest sees joined source → BLOCK
    native query fingerprint != manifest fingerprint → HARD FAIL
    manifest fingerprint != Platform candidate fingerprint → HARD FAIL
    candidate engine SHA != runtime attestation SHA → HARD FAIL
    authorized image digest != runtime image digest → HARD FAIL
    artifact runtime != receipt runtime → HARD FAIL
    authenticated Metabase subject mismatch → HARD FAIL
    authorized pMBQL mutated before execution → HARD FAIL
    second material analytical query → BLOCK
    SQL query producer in first vertical → BLOCK
    explicit join → BLOCK
    implicit joined source → BLOCK
    non-temporal arbitrary filter → BLOCK
    observed time bounds != accepted period → BLOCK
    result != independent oracle → no VERIFIED Evidence
    native prose before receipt/evidence → never official numeric truth

Every RED must be classified before patching.

## 17. Open debt — do not accidentally close

Still open:

    DMP-P13B-BLOCK-001
    native candidate fact provenance
    = DESIGN SEALED / IMPLEMENTATION OPEN

    DMP-P13B-BLOCK-002
    artifact ↔ running runtime identity
    = DESIGN SEALED / IMPLEMENTATION OPEN

    DMP-P5-BLOCK-001
    global production issuance blocker

    DMP-P11-INTEGRATION-005
    P13C owner

    EV-05 / EV-06 / EV-07
    UNCERTIFIED

    P10B2
    RLS / CLS / impersonation / advanced routing / cache-result reauthorization

    P9
    dimension / time / relationship transport gaps

    P7/P8
    relationship / calculated / view semantic gaps

    historical Wren typed gaps

P13B must not solve P13C:
- no textual/entity-value integration;
- no high-cardinality resolver;
- no fuzzy matching;
- no str(value) fallback.

P13B must not solve relationships.
Explicit or implicit relationship use in first vertical = BLOCK.

P13B must not start Research/P14.

## 18. Failure protocol

Never patch immediately because a test is RED.

First classify the owner.

Typical classes:

    NATIVE_CANDIDATE_EXTRACTION
    NATIVE_ATTESTATION
    SEMANTIC_MAPPING
    AUTHORITY_MISMATCH
    TIME_SCOPE_VIOLATION
    RELATIONSHIP_GRAIN_VIOLATION
    EXECUTION_ARTIFACT_MISMATCH
    ACCESS_IDENTITY_MISMATCH
    RESOURCE_PROVENANCE_MISMATCH
    ENGINE_IDENTITY
    RECEIPT_PROVENANCE
    EVAL_ORACLE
    TRANSPORT_RUNTIME
    CI_GOVERNANCE
    FIXTURE

Then record:
- tested SHA;
- failing run/test;
- root cause;
- single owner;
- files allowed to change;
- files forbidden to change;
- focused proof;
- regression proof.

Fast green is not the goal. Correct ownership is the goal.

## 19. Absolute stop conditions

Stop immediately if any implementation would require:
- Python to become the MBQL parser;
- Dima to rewrite/fix native pMBQL after native construction;
- Agent API analytical fallback;
- Wren analytical fallback;
- raw SQL escape;
- a second receipt system;
- a second durable access fingerprint;
- native prose as Evidence;
- implicit source/metric guessing;
- engine cognition/query construction/QP semantics changes merely to expose attestation;
- merge/cherry-pick/rebase from ask-v2 or Fast Track;
- moving engine main consumption without explicit SHA.

## 20. What the next developer should do next

Current state is a supervisor stop.

Before implementation:
1. verify Platform HEAD, engine gitlink and governance;
2. re-read DMP-DEC-0037 and P13B predev;
3. obtain explicit supervisor authorization for P13B implementation.

If authorized, the next milestone is not Platform live orchestration first.

It is:

    P13B-1 ENGINE NATIVE ATTESTATION + IDENTITY SEAM

in the engine repo, on an isolated engine branch.

Expected narrow goal:

    conversation_id + native_query_id
    → retrieve server-side exact native query
    → Metabase Lib/QP bounded observation
    → NativeExecutionManifest
    → exact query fingerprint
    → authenticated Metabase subject
    → typed validation/permission provenance
    → exact engine/build identity

No analytical behavior change.

After that:
- native engine tests;
- source build;
- P12X regression;
- patch-surface audit;
- exact engine SHA;
- supervisor approval;
- Platform gitlink bump;
- only then first live PX-01 Standard vertical.

## 21. Final truth table

    P12X fork/build/bridge/sync              GREEN
    P13A native trust contract               GREEN
    P13B-0 source audit/design               SEALED
    P13B engine attestation implementation   NOT STARTED
    P13B Platform live Standard              NOT STARTED
    P13 Standard                             NOT GREEN
    global production security               NOT GREEN
    native absolute correctness              NOT GREEN
    P13C entity-value integration            NOT STARTED
    P14 Research                              NOT STARTED

The project is not stuck.

The next problem is precisely defined:

    Can Metabase attest what its native agent actually built,
    can Dima map that observed physical execution meaning
    to accepted business truth,
    and can Dima prove that the exact authorized artifact
    ran on the exact certified runtime before promoting Evidence?

That is the next implementation phase once explicitly authorized.


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
