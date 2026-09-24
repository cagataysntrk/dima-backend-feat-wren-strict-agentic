# DIMA + METABASE — Nihai Uygulama Yol Haritası

**Belge rolü:** Bağlayıcı geliştirme ve sertifikasyon planı.  
**Amaç:** Yeni branch üzerinde Wren+Dima denemesinin doğru abstraction’larını koruyup, Metabase’i analytics/BI substrate yapan nihai Dima ürününe ulaşmak.  
**Tek cümlelik protokol:** Vaka geçirerek sistem yapma; doğru abstraction’ı kur, vakalar onun doğal sonucu olarak geçsin.  
**Final audit notu:** Plan, Metabase source-level cross-check sonrası query-handle lifecycle, access-lens, retrieval states, implicit joins, bridge preflight, front-door ownership ve cutover/rollback adımlarıyla sertleştirilmiştir.


## CURRENT NORMATIVE ARCHITECTURE — DMP-DEC-0031..0036 / P12X C0-C3

> **Precedence notice — 2026-09-23**
>
> DMP-DEC-0031 through DMP-DEC-0036 and the certified P12X C0-C3 evidence **supersede every
> historical assumption in this document that Agent API is the primary production analytical
> execution seam**. Historical P0-P12 sections remain preserved for evidence, migration history and
> regression context; they are not current hot-path implementation authority where they conflict with
> this section.

Current production-engine architecture:

```text
DIMA PRODUCT
→ DIMA CONVERSATION / DECISION INTELLIGENCE
→ DIMA SEMANTIC + SECURITY + PROVENANCE + EVIDENCE CONTROL PLANE
→ TYPED DIMA NATIVE ENGINE BRIDGE
→ PINNED DIMA METABASE ENGINE
   repo: UpcyTech/dima-metabase-engine
   runtime authority:
     Platform engine gitlink
     + certified engine runtime lock
     + immutable registry digest
   exact current SHA/digest:
     living status + decision/release receipt + runtime lock
→ native Metabot / profiles / skills / engine-local state
→ native query construction + repair / MBQL / Query Processor / drivers
→ CUSTOMER DB
```

Binding ownership:

```text
Native Metabot
= analytical cognition / orchestration / query-candidate author

Dima
= business semantic truth
= execution authority
= security / provenance / evidence authority
= durable conversation / research / decision truth

Metabase Query Processor
= executor
```

Historical Agent-API-era certification is **not** current production hot-path architecture.

The following historical assumptions are explicitly overridden for current implementation:
- P2 Agent API readiness as primary analytical runtime;
- P3 Agent API client boundary as primary analytical seam;
- P4 `MetabaseProjectionCompiler` / `CanonicalProjection` as universal production query-authoring identity;
- P5 REST/Agent API as the primary production execution route;
- P26 Agent API availability as the primary runtime-availability contract;
- P41 “Agent API disabled” as the primary analytical-path failure.

Agent API code is retained and may remain useful for measured provisioning, resource persistence,
metadata/search utilities, administrative tooling, historical regression and migration support.
Its analytical execution role is now:

```text
LEGACY / AUXILIARY / NON-PRIMARY
```

It must not become:
- primary Standard query author/executor;
- silent native fallback;
- a second query-authoring authority.

P13 now means **Production Standard over the Dima Metabase Engine**. The core invariant remains:
Dima must authorize exactly the material execution artifact that is actually executed and receipted.

## NATIVE ENGINE INHERITANCE RULE — DMP-DEC-0042

```text
METABASE + METABOT ARE THE PRIMARY NATIVE ANALYTICS ENGINE.

Native capability reuse is the default.

USE_NATIVE
→ COMPOSE_NATIVE
→ WRAP_NATIVE
→ HOOK_NATIVE
→ DIMA_OWNS
```

`DIMA_OWNS` is the last resort, not the default. Compatible capability already present in the pinned
native engine is part of Dima's available analytics substrate even when it is not exposed in product
UX yet. This includes, where the exact pinned runtime supports the required contract:

- Metabot agent loop, profiles, skills and engine-local state/memory;
- search, resource discovery, metrics/measures, field values and indexed entities;
- native query construction/repair, MBQL, Query Processor and drivers;
- breakouts, comparisons, ranking/top-N and temporal analytical patterns;
- native Explorations, variants and interestingness;
- stored results, query lifecycle, cancel/restart and idempotent execution machinery;
- native permissions/derived permissions and caching;
- saved questions, collections, dashboards, query builder, visualization and workspace surfaces.

Reuse does **not** transfer Dima truth ownership. Dima remains owner of business semantic authority,
accepted user obligations, tenant/principal control truth, approved relationships, execution
authorization, QueryReceipt, Evidence state, finding/hypothesis epistemics, durable Research state and
Decision state.

DMP-DEC-0026 `SEMANTIC_NECESSITY_GATE` is therefore scoped narrowly:

```text
before introducing NEW DIMA deterministic cognition / heuristic machinery
```

It is **not** a prerequisite for using an already-native Metabase/Metabot capability under the
established Dima trust boundary.

Normative architecture must not hard-code moving engine candidate identities. Exact current engine
SHA, certification run, registry digest and build identity belong in the Platform gitlink, certified
runtime lock, living status and release/decision receipts.

---

## HISTORICAL / SUPERSEDED FOR PRIMARY HOT PATH — P0–P12

The following P0–P12 material is retained as migration, audit and regression history. It is not
future implementation authority where it conflicts with the current native-engine rule above.

# P0 — Branch, baseline ve source lock

Önerilen branch:

```text
feat/dima-metabase-platform
```

Branch **hareketli branch HEAD’den değil**, focused/provider-free + real Wren sentinel ile yeniden doğrulanmış bir certified checkpoint SHA’dan açılır.

Branch oluşturulurken kaydedilecek:

```text
DIMA_SOURCE_BRANCH
DIMA_AUDIT_HEAD
DIMA_BASE_CERTIFIED_SHA
WREN_REFERENCE_SHA
METABASE_SOURCE_AUDIT_SHA
METABASE_RUNTIME_VERSION       # runtime seçildiğinde
METABASE_RUNTIME_IMAGE_DIGEST  # runtime seçildiğinde
METABASE_UPSTREAM_OBSERVED_SHA
```

`METABASE_SOURCE_AUDIT_SHA` ile production runtime pin aynı kavram değildir.

Belge düzeni:

```text
1. mühürlü mimari rapor
2. mühürlü yol haritası
3. living status
4. failure receipts
5. decision receipts
```

Her ticket sonunda:

```text
ticket
owner
goal
SHA
files changed
test results
failure class
open debt
next action
```

---

# P1 — Engine-independent Dima core

## Amaç
Wren/Metabase bağımlılığını core contract’tan ayırmak.

Önerilen modüller:

```text
app/v3/
  semantic_spec.py
  authority.py
  analytics_contract.py
  evidence.py
  substrate/
    base.py
    wren.py
```

Ana modeller:

```text
DimaSemanticSpec
AcceptedStandardAuthority
AcceptedTurnContract           # Research semantic authority; ikinci Research contract tipi YOK
SharedAuthorityArbiter          # same turn Standard XOR Research
SemanticSurfaceCoverage        # every material surface bound or explicitly unresolved
StandardProjection
ResolvedAnalyticsIntent
ResearchTask
DimaQueryReceipt
EvidenceArtifact
```

`AnalyticsSubstrate` minimum contract semantic compiler değildir. Adapter yalnız Dima-owned resolved execution intent tüketir:

```text
inspect_capabilities
validate_execution_intent
execute_execution_intent
inspect_execution
```

Semantic handle çözümü substrate içinde yapılmaz.

İlk adapter mevcut Wren davranışını aynen taşımalı.

Model-role contract:

```text
SEMANTIC_LINKER      = bounded catalog candidate decision
TEMPORAL_NORMALIZER  = typed language→time/comparison intent
RESEARCH_MANAGER     = research cognition/orchestration
```

Bu roller aynı provider/modeli kullanabilir ama architecture’da aynı role değildir.

**Gate:** existing Wren sentinel green, behavior drift = 0, partial semantic surface silent-loss = 0, Standard/Research double authority = 0.

---

# P2 — Metabase lab bootstrap

Topology:

```text
dima-api
metabase
metabase-app-db(Postgres)
analytics-db
```

Yapılacak:
- source-audit SHA’dan ayrı pinned **supported runtime release + immutable image digest**,
- private network,
- persistent app DB; result/cache içerebildiği için sensitive-store policy,
- encryption/backup retention test,
- admin bootstrap,
- test user/group,
- DB connection,
- backup/restore,
- health check.

Test:

```text
startup
restart
persistence
query execution
permission denial
backup/restore
Agent API enabled/capability handshake
raw-SQL policy check
row/pagination capability observation
```

Product code henüz Metabase’e bağlanmaz. Lab servisinin çalışması P3A bridge gate’ini bypass edip production feasibility sonucu sayılmaz.

---

# P3 — Metabase client/adaptor boundary

```text
substrate/metabase/
  client.py
  adapter.py
  models.py
  errors.py
  telemetry.py
```

Primary candidate integration surface versioned REST/Agent API’dir. MCP ayrı optional lab surface’tir; ikisinin identity/lifecycle semantics’i tek abstraction sanılmaz.

İlk yetkiler:
- metadata inspect,
- construct/validate,
- execute,
- read resource,
- execution identity/continuation.

`query_handle` yalnız seçilen surface gerçekten kullanıyorsa opsiyonel locator’dır; Dima durable receipt anahtarı değildir.

Başlangıçta yasak:
- arbitrary admin mutation,
- raw SQL,
- dashboard write,
- semantic mutation.

Adapter startup’ta capability handshake yapar:

```text
agent_api_enabled
required_api_version
required_scopes
construct_query
execute/query
pagination_limit
raw_sql_policy == disabled/unused
```

MCP yüzeyi runtime’da mevcutsa `mcp-execute-sql-enabled` explicit OFF tercih edilir. Agent API native SQL endpointleri Dima adapter tarafından expose edilmez; upstream default’a güvenilmez.

Metabase healthy olup Agent API unavailable ise typed runtime failure; semantic fallback yok.

Error taxonomy:

```text
METABASE_TRANSPORT
METABASE_AUTH
METABASE_PERMISSION
METABASE_QUERY_INVALID
METABASE_RESOURCE_NOT_FOUND
METABASE_TIMEOUT
METABASE_INTERNAL
```

Infra fail semantic fail sayılmaz.

---

# P3A — Bridge preflight: semantic duplication var mı?

Metabase runtime benchmarkından önce design/prototype gate.

Soru:

> Accepted Dima semantic request Metabase structured-query semantics’e **raw language reparse, metric redefinition, relationship redefinition, label guessing veya ikinci semantic owner yaratmadan** çevrilebiliyor mu?

Candidate seams:

```text
A. StandardProjection + opaque semantic handles
B. Dima-owned ResolvedAnalyticsIntent
C. Wren-specific planned representation
```

Başlangıç hipotezi **B**’dir; evidence karar verir.

Sekiz representative Standard family:
1. metric,
2. metric+dimension,
3. metric+filter,
4. metric+period,
5. previous-period comparison,
6. ranking/limit,
7. two compatible dimensions,
8. filter+period+dimension.

Hard P0:

```text
raw_user_language_reinterpretation = 0
manual_metric_redefinition = 0
manual_relationship_redefinition = 0
metabase_label_name_guessing = 0
unapproved_implicit_fk_join = 0
second_semantic_authority = 0
```

Bridge bir semantic sync/compiler ürününe dönüşüyorsa **Metabase structured-execution arm burada reject edilir**. Metabase workspace/reference değeri ayrı kalabilir.

---

# P4 — StandardProjection → Metabase query

Akış:

```text
AcceptedStandardAuthority
→ sealed StandardProjection
→ Dima Semantic Handle Resolution (exactly once)
→ ResolvedAnalyticsIntent
→ MetabaseProjectionCompiler
→ SourceLineage/current catalog snapshot’tan deterministic portable DB/schema/table/field refs
→ portable representation
→ validate / repair / resolve
→ canonical Metabase query
```

Hard invariants:

```text
execution projection_hash == sealed authority projection_hash
resolved_intent semantic meaning == sealed authority meaning
Metabase adapter semantic handle resolution = 0
Metabase label/name guessing = 0
portable ref LLM invention = 0
rename drift silent rebind = 0
unapproved implicit join = 0
```

Focused test family:
- metric-only,
- breakdown,
- filters,
- time,
- comparison,
- ranking,
- limit,
- multi-filter,
- null,
- categorical,
- numeric.

**Gate:** silent field drop = 0.

---

# P5 — QueryReceipt ve execution identity

Dima receipt:

```text
authority_id
projection_hash
resolved_intent_hash
canonical_query_fingerprint
canonical_query_representation?   # safe/serializable ise
ephemeral_query_handle?           # durable identity DEĞİL
principal_fingerprint
execution_access_fingerprint
semantic_context_version
resource_entity_ids
resource_fingerprints
substrate_runtime_version
substrate_image_digest
result_hash
row_count
warnings
```

REST primary path’te serialized canonical query/hash durable receipt materialidir; pagination continuation ephemeral’dır. MCP query handle ancak optional MCP experimentinde session-bound locator olarak tutulur.

Handle/continuation tekrar kullanılırsa permission + lens yeniden doğrulanır. Handle expire olsa bile receipt audit kimliği yaşamaya devam eder.

**P0:** Authority A + Query B = hard fail.

---

# P6 — Wren vs Metabase Standard parity

Sabit:

```text
same AcceptedStandardAuthority
same StandardProjection
same ResolvedAnalyticsIntent
same semantic refs
same approved relationship paths
same principal/access fingerprint
same database snapshot
```

Değişken:

```text
WrenSubstrateAdapter
MetabaseSubstrateAdapter
```

Corpus minimum:

```text
30 standard
10 time/comparison
10 ranking/top-N
10 filters/entity
10 join/relationship
10 error/edge
```

Ölç:

```text
numeric parity
row parity
aggregation parity
grain parity
time parity
permission parity
access-lens parity
implicit-join parity
query-repair semantic preservation
latency
failure rate
receipt completeness
adapter complexity
manual semantic duplication count
row/pagination budget behavior
connection/runtime operational overhead
```

Burada semantic-layer removal kararı verilmez.

---

# P7 — DimaSemanticSpec V1

Wren MDL’den engine-independent canonical spec oluştur.

```text
MetricSpec
  id
  name
  aliases
  formula
  aggregation
  unit
  format
  grain
  additive_kind
  time_dimension
  provenance
  semantic_version
  compatibility_hash
  source_lineage

DimensionSpec
  id
  aliases
  type
  entity_value_policy
  sensitivity_policy
  cardinality_policy

RelationshipSpec
  from
  to
  cardinality
  join_keys
  allowed_grains
  path_policy
  semantic_version
```

Ayrıca top-level:

```text
ManagedResourcePolicy
SecurityTag
BusinessRule
DisplaySpec
TimeSpec
```

İlk importer:

```text
Wren MDL → DimaSemanticSpec
```

**Gate:** bütün mevcut Wren packs parse.

---

# P8 — Semantic equivalence matrix

Her Wren capability:

```text
Wren feature
→ DimaSemanticSpec
→ Metabase representation
→ parity proof
```

Classification:

```text
NATIVE_METABASE
DIMA_COMPILED
DIMA_RUNTIME
WREN_ONLY_GAP
UNSUPPORTED
```

Test alanları:
- formula,
- relationship,
- cubes,
- measures,
- dimensions,
- time,
- aliases,
- customer overrides,
- grain,
- additivity/semi-additivity,
- distinct-count / ratio / derived metric,
- role-playing time dimensions,
- customer overrides,
- multi-hop relationships,
- approved-vs-physical FK behavior,
- null semantics,
- filter context,
- format/unit/provenance.

`NATIVE_METABASE` yalnız “aynı label var” demek değildir; behavioral equivalence gerekir.

Wren remove için release-critical `WREN_ONLY_GAP = 0`.

---

# P9 — Semantic resource provisioner

`DimaSemanticSpec → Metabase resources`

Candidate resources:
- models,
- metrics,
- measures,
- segments,
- descriptions,
- glossary,
- AI context,
- synonyms/examples.

Properties:
- idempotent,
- versioned,
- tenant-scoped,
- dry-run,
- diff,
- rollback,
- managed-vs-user-created resource ayrımı,
- stable Dima canonical id ↔ Metabase `entity_id`/resource mapping,
- Dima SourceLineage ↔ current DB/schema/table/field mapping,
- rename/drift detection.

Dima-managed resource Metabase UI’dan manuel değişirse reconciliation policy explicit olmalı: overwrite, reject veya import-as-new-version. Silent drift yok.

**Gate:** same spec twice = no drift; unmanaged content Dima semantic authority’ye kendiliğinden yükselmez.

---

# P10 — Tenant/principal/security mapping

Test topology:

```text
tenant A / tenant B
user A1 / A2
admin
restricted
row-restricted
```

P0:

```text
A sees B = 0
cached A result visible B = 0
service account fallback = 0
permission revoked after execution → reread denied
```

Receipt’e `ExecutionAccessFingerprint`:

```text
tenant_binding
principal_subject
role_set_digest
attribute_policy_digest
policy_version
RLS_CLS_versions
database_route
impersonation_role
semantic_context_version
source_object_refs
security_parameter_digest
```

Raw PII yazılmaz.

Connection ownership explicit:
- Standard analytics data-plane connection owner = selected primary substrate,
- Dima direct DB connection yalnız ayrı specialized governed capability varsa,
- duplicate secrets/rotation ownership yasak.

Ek P0:

```text
missing creator/principal → fail closed
permission-sensitive cache cross-user reuse = 0
runtime-only security binding kayıpsız serialize edilemiyorsa persistence = forbidden
```

---

# P11 — Entity values / filter resolution

P11, DMP-DEC-0026 gereği doğrudan büyük bir entity resolver implementasyonu ile başlamaz.

İlk gate:

```text
small frozen value corpus
→ Platform/Metabase + Luna baseline
→ exact same corpus/tools/access lens + Sol ceiling
→ failure classification
→ only then minimum guardrail if materially necessary
```

İlk frozen family en az:
- exact categorical value,
- cross-language entity value,
- ambiguous entity value,
- missing value,
- high-cardinality value,
- stale indexed value,
- permission-hidden value.

Metabase reusable candidates:
- field values,
- indexed entities,
- linked filters.

Dima:
- semantic/security truth,
- current-principal authoritative live re-read requirement where needed,
- typed outcomes,
- bind/clarify/block decision contract only when necessity is proven.

Possible typed retrieval outcomes remain:

```text
INDEX_UNAVAILABLE
NO_MATCH
AMBIGUOUS
MATCH_CANDIDATES
SEMANTIC_GAP   # yalnız semantic gate sonrası
```

No-match = clarify/gap; fuzzy truth yok. Sensitive/high-cardinality candidate current-principal
authoritative live re-read görmeden bind edilmez.

If vanilla Metabase/Fast + Luna and Sol already solve a case family safely, duplicate Dima resolver is
not built. Luna failure alone is not architecture evidence. A deterministic guardrail needs a
material truth/security failure that survives the Semantic Necessity Gate.

---
# P12 — BI workspace feasibility

Değerlendir:
- charts,
- dashboards,
- collections,
- saved questions,
- query builder,
- exploration detail.

Integration option:
- embed,
- link-out,
- headless API,
- Dima shell.

Dima UX primary kalır. Workspace adoption analytics-substrate doğruluğunu bloke etmez; ayrı product track olarak ölçülür. Metabase UI kullanmak Metabase’i semantic authority yapmaz.

---

# P13 — Production Standard path

```text
User
→ Language Runtime
→ Dima semantic authority
→ StandardBuilder
→ AcceptedStandardAuthority
→ MetabaseSubstrate
→ QueryReceipt
→ Evidence
→ Answer/Chart
```

Live scenarios:
1. metric,
2. breakdown,
3. comparison,
4. repair,
5. ambiguity,
6. unsupported,
7. no-progress,
8. permission denied.

Research fallback yalnız typed `RESEARCH_REQUIRED`.

### P13A — Front-door ownership closure

Final freeze’den önce gerçek HTTP owner:

```text
/api/ask-v2
→ STANDARD | RESEARCH dispatcher

STANDARD → new Standard path
RESEARCH → governed Research Manager
```

Release blocker:

```text
authoritative path legacy SemanticResolver import/execute = 0
request-level fallback to old Day4 authority path = 0
shared Standard/Research authority XOR = enforced
```

Legacy code migration/history olarak kalabilir; authority olamaz.

---

# P14 — Native Research integration foundation

Dima Research / Decision Manager analitik motor değildir. Sahip olduğu state:

```text
research obligations
hypotheses
counter-evidence
stopping / budget
Evidence synthesis
finding promotion
decision state
durable research state
```

Analytical work:

```text
ResearchManager
→ governed analytical objective + accepted Dima semantic/security context
→ native Metabot session
→ full compatible native Metabase analytical capability
→ attested material executions
→ Dima QueryReceipts
→ EvidenceArtifacts
→ ResearchManager epistemic reasoning / decision synthesis
```

ResearchManager ham MBQL/SQL/table-id/Metabase numeric resource-id görmez; ancak native agentın güvenli
biçimde yapabildiği analitik işi altı ayrı Python compare/breakdown/rank aracı olarak yeniden kurmaz.
Dima adapter'ı yalnız semantic/security/provenance/Evidence sınırını bağlar. Conversational output
bounded kalır; large extract ayrı governed export/batch capability'dir.

---

# P15 — Native Metabase Explorations Integration

Default architecture:

```text
native Metabase Explorations capability
→ USE IN PLACE
→ bind Dima semantic / security / provenance / Evidence boundary
→ expose through Dima product
```

Native engine'de bulunan metric-dimension applicability, variants, top-N-other, temporal patterns,
interestingness, stored-result machinery, runner, cancel/restart, idempotency and derived permissions
Python'a port edilmez ve "primitive harvest" gerekçesiyle yeniden yazılmaz.

Dima yalnız farklı ownership katmanını ekler:
- business semantic authority;
- accepted user obligation;
- tenant/principal control truth;
- approved relationships;
- execution authorization;
- QueryReceipt;
- Evidence state;
- finding/hypothesis epistemics;
- durable Research and Decision state.

`Metabase interestingness score != Dima verified finding`.
Native interestingness/variants analizi önerebilir veya önceliklendirebilir; official finding
promotion yalnız Dima Evidence/epistemic gates'ten geçer.

DMP-DEC-0026 kapsamı:
`SEMANTIC_NECESSITY_GATE` yalnız **yeni Dima-owned deterministic cognition/heuristic machinery**
önerildiğinde gerekir. Zaten native olan bir Metabase capability'sini established trust boundary
altında kullanmak için "neden harvest edelim?" gate'i çalıştırılmaz.

---

# P16 — Evidence Plane V2

Evidence state:

```text
PENDING
EXECUTED
VERIFIED
INVALIDATED
STALE
```

Stale triggers:
- semantic version changed,
- Metabase resource fingerprint changed,
- permission/lens mismatch,
- source routing/impersonation changed,
- freshness policy exceeded.

Read path current viewer’ı yeniden authorize eder. Creation-time permission kalıcı erişim hakkı değildir.

Security-bound execution faithfully serialize edilemiyorsa evidence snapshot tutulabilir; **replayable query** olarak persist edilmez.

---

# P17 — Research Manager V2

```text
AcceptedTurnContract
→ UserObligationLedger
→ seed tasks
→ execute
→ inspect evidence
→ interestingness
→ derive task
→ replan
→ CompletionGate
```

Budgets:
- turns,
- tool calls,
- queries,
- wall time,
- cost.

No-progress:
- ActionFingerprint,
- StateFingerprint.

Bu akış bir deterministic analytical sequence değildir. LLM/Research Manager:
- observe,
- hypothesize,
- choose next governed analytical tool,
- inspect evidence,
- replan

işlerinin cognition sahibidir.

Deterministic sınırlar:
- turns/tool/query/wall-time/cost budget,
- tool schema,
- security,
- evidence validity,
- completion constraints,
- relationship/grain approval,
- no-progress,
- idempotency,
- cancellation.

Fanout policy:
- metadata cardinality deterministic budget,
- high cardinality → bounded Top-K + Other,
- interestingness → priority only,
- evidence absence → causal negative proof değildir.

---

# P18 — Relationship analysis

Relationship truth DimaSemanticSpec’te.

```text
relationship request
→ RelationshipSpec
→ path validation
→ grain validation
→ Metabase execution
→ Evidence
```

No verified path = BLOCKED.

Metabase representation repair fiziksel FK join önerse bile Dima RelationshipSpec onayı yoksa execution yasak:

```text
UNAPPROVED_METABASE_IMPLICIT_JOIN = 0
```

---

# P19 — Root-cause / hypothesis

```text
Hypothesis
EvidenceLink
CounterEvidence
EpistemicKind
```

Kinds:

```text
ASSOCIATION
CONTRIBUTION
CANDIDATE_CAUSE
CONFIRMED_CAUSE
```

Model gate olmadan epistemic promotion yapamaz.

Universal deterministic:
`trend → breakdown → segment → relationship`
sequence'i yoktur. Bu analytical strategy LLM cognition'a aittir. Deterministic code yalnız evidence
truth, relationship/grain/security approval, budget ve completion invariants'ını enforce eder.

---

# P20 — ReportDocument

ReportSynthesizer yalnız:
- findings,
- evidence,
- limitations,
- obligation ledger

görür.

ReportClaimGate:
- numeric claim → evidence,
- analytical claim → Finding,
- causal wording → compatible epistemic kind,
- all USER_MUST represented or explicit limitation.

---

# P21 — Decision intelligence

```text
DecisionBrief
  objective
  constraints
  options
  evidence
  tradeoffs
  recommendation
  limitations
```

Decision factual analytics’ten ayrı nesnedir.

---

# P22 — Persistence / resume

Persist:
- accepted authority,
- research run,
- obligations,
- tasks,
- receipts,
- evidence,
- findings,
- hypotheses,
- report,
- decision.

Resume raw promptu yeni semantic authority olarak yeniden parse etmez.

---

# P23 — Background execution / native lifecycle integration

Default:

```text
USE native Metabase lifecycle / job / cancel / restart / stored-result machinery
```

when the pinned engine already satisfies the required execution contract. Dima must not build a
second generic background analytics runner merely to mirror native Metabase.

Dima-owned durable state is limited to cross-system Research/Decision workflow truth: obligations,
hypotheses, Evidence references, stopping/budget and decision state.

Required invariants remain:
- missing creator/principal → fail closed;
- duplicate delivery → one terminal effect;
- cancel-after-plan race → cleanup;
- terminal work is not re-executed accidentally;
- result persistence and Dima Evidence linkage remain auditable;
- security/lens reauthorization remains Dima-governed where required.

---

# P24 — Observability

Per request:

```text
model_calls
tool_calls
metabase_calls
db_queries
tokens
latency
cost
repairs
authority_id
receipt_ids
evidence_count
execution_access_fingerprint_id
metabase_runtime_version
resource_fingerprint_set
query_repair_count
cache_hit/miss
pagination_pages/rows
metabase_app_db_growth
connection_pool_usage
```

North-star operational metric:

```text
cost_per_verified_success
```

---

# P25 — Failure triage

Top-level failure taxonomy mevcut operasyon protokolüyle **aynı** kalır:

```text
MODEL_COGNITION
CONTRACT/ARCHITECTURE
RESOLVER_TRUTH
EVAL_ORACLE
TRANSPORT/PROVIDER
```

Metabase-specific ikinci boyut `failure_tag` olarak yazılır; yeni top-level owner yaratmaz:

```text
SUBSTRATE_QUERY
PERMISSION
ACCESS_LENS
RESOURCE_DRIFT
IMPLICIT_JOIN
CACHE_ISOLATION
PERSISTENCE_REPLAY
```

RED → classify top-level → single owner → root cause → allowed files → fix → focused family proof.

---

# P26 — Metabase upgrade contract

Her upgrade:
1. source diff + supported runtime release + immutable image digest pin,
2. app DB backup,
3. migration dry-run,
4. adapter contract tests,
5. parity corpus,
6. permission/lens corpus,
7. Agent API setting/scope/capability handshake,
8. query representation/portable-ref compatibility,
9. rollback rehearsal,
10. promote.
Floating latest prod’da yasak.

---

# P27 — Performance / scaling

Ölç:
- p50/p95 Standard,
- p50/p95 Research tool,
- Metabase QP,
- app DB,
- connection pool,
- queue depth,
- cache hit,
- CPU/RAM,
- app DB growth/result retention,
- pagination/row budget,
- network hops.

Concurrency semantic certificationden sonra. Standard/research architecture raw-row volume ile ölçeklenmez; query-side aggregation esastır.

---

# P28 — Wren retirement gate

Wren ancak şunlar green ise kaldırılır:

```text
standard parity
semantic feature equivalence
relationship parity
time/comparison parity
security parity
evidence/provenance parity
performance/operability acceptable
Dima receipt/provenance independent of ephemeral Metabase handles
front-door ownership migrated
WREN_ONLY_GAP release-critical = 0
```

Aksi durumda Wren semantic reference/backbone olarak kalabilir.

---

# P29 — Wren removal migration

Gate geçerse:

```text
Wren runtime OFF behind flag
Metabase primary
shadow compare (user-visible fallback değil)
rollback switch
stability window
cleanup later
```

Switch ve code deletion aynı commit olmaz.

---

# P30 — Product workspace

Dima shell:
- conversation,
- evidence panel,
- research progress,
- reports,
- decisions,
- dashboards,
- saved analytics.

Metabase UI/resource’ları gerektiği ölçüde reuse edilir.

---

# P31 — Sector packs

Pack içeriği:

```text
semantic spec
aliases
glossary
AI context
verified examples
metric formulas
relationship graph
default explorations
dashboard templates
```

İlk gerçek sektör pack’inde migration sınanır.

---

# P32 — Automated onboarding

```text
connect
→ introspect
→ candidate semantic spec
→ LLM proposal
→ human/verified review
→ Metabase provision
→ smoke
→ parity
→ publish context version
```

LLM proposal authority değildir.

---

# P33 — Final integration rehearsal

20–25 zor vaka:
- Turkish paraphrase,
- ambiguity,
- repair,
- follow-up,
- comparison,
- top-N,
- relationship,
- research,
- empty evidence,
- timeout,
- permission change,
- stale evidence,
- report completeness,
- decision brief,
- query handle/session expiry,
- resource drift,
- index unavailable vs no-match,
- implicit FK join rejection,
- cached evidence viewer lens mismatch,
- background duplicate/cancel race,
- Agent API disabled while Metabase health is green,
- portable table/field rename drift,
- row-cap/pagination boundary.

P0 = 0.

---

# P34 — Broad gates

```text
DEV80 once
→ CODE FREEZE
→ VALIDATION50 no tuning
→ external HIDDEN50 no tuning
```

DEV80 debugging tool değildir.

---

# P35 — Pilot

Feature flags:

```text
DIMA_METABASE_STANDARD
DIMA_METABASE_RESEARCH
DIMA_METABASE_WORKSPACE
WREN_SHADOW_COMPARE
```

Shadow hiçbir zaman silent user fallback değildir.

Rollout:
- internal,
- 1 tenant,
- several tenants,
- staged.

---

# P36 — Release gates

P0:

```text
silent wrong = 0
cross-tenant leak = 0
authority/query mismatch = 0
unverified numeric claim = 0
blocking ambiguity auto-pick = 0
no-path relationship execution = 0
raw SQL bypass = 0
cached incompatible lens leak = 0
unapproved implicit join = 0
semantic reparse inside substrate adapter = 0
security-bound lossy replay = 0
portable-name silent rebind = 0
runtime capability failure semantic fallback = 0
```

P1:

```text
MUST coverage >= 95%
clarification accuracy >= 95%
supported research completion >= 95%
report obligation accounting = 100%
```

---

# P37 — Önerilen engineering-day / gate sırası

Bu sıra **calendar promise değildir**. Her `M*` bir vertical engineering work-unit’tir; exit gate geçmeden sonraki authority-changing güne geçilmez.

```text
M0  certified source checkpoint + new branch + frozen docs
M1  engine-independent Dima contracts + Wren adapter, zero behavior drift
M2  Metabase source/runtime pin policy + self-host lab bootstrap
M3  Metabase client boundary + typed transport/error model
M4  bridge preflight: ResolvedAnalyticsIntent seam, semantic duplication P0
M5  Metabase compiler/validator path for metric-only + breakdown
M6  QueryReceipt + ExecutionAccessFingerprint + durable query identity
M7  Standard family expansion: filters/time/comparison/ranking
M8  Wren-vs-Metabase standard execution parity
M9  DimaSemanticSpec + Wren MDL importer
M10 semantic equivalence matrix / WREN_ONLY_GAP classification
M11 managed Metabase resource provisioner + drift reconciliation
M12 tenant/principal/access-lens mapping
M13 entity values / indexed retrieval / live re-read
M14 full real Standard path + AcceptedStandardAuthority → Metabase → Evidence
M15 front-door STANDARD ownership closure behind flag
M16 Native Research integration foundation: Dima epistemic state → native Metabot analytical work → receipts/Evidence
M17 Native Metabase Explorations integration under Dima semantic/trust/Evidence boundaries
M18 Evidence Plane V2 + current-viewer reauthorization
M19 Research Manager evidence-aware loop + no-progress/budget
M20 relationship graph + implicit-FK veto + grain safety
M21 root-cause / HypothesisLedger / epistemic gates
M22 ReportDocument + ReportClaimGate
M23 DecisionBrief + recommendation/decision record
M24 persistence/resume + semantic/resource staleness
M25 native lifecycle/job/cancel/restart integration + Dima cross-system Research/Decision durability
M26 BI workspace integration feasibility + chosen UX mode
M27 first real sector pack migration
M28 automated onboarding / semantic proposal → verify → provision
M29 performance / cache / pool / multi-tenant security hardening
M30 Metabase runtime necessity + Wren retirement decision gate
M31 chosen substrate cutover behind flags + shadow compare + rollback rehearsal
M32 front-door STANDARD+RESEARCH final ownership + legacy authority zero
M33 20–25 hardest-case final integration rehearsal
M34 FINAL ENGINEERING FREEZE CANDIDATE
M35 DEV80 exactly once → code freeze
M36 Validation50 no tuning
M37 external Hidden50 no tuning → certification seal
M38 pilot activation → staged tenants → post-pilot stability receipt
```

Wren retirement gate geçmezse M31’de Wren semantic/runtime retain kararı açıkça yazılır; kalan Dima Research/Report/Decision çalışması durmaz.

---

# P38 — Her ticket şablonu

```text
TICKET
GOAL
USER SCENARIO
CURRENT OWNER
NEW OWNER
FILES TO TOUCH
FILES NOT TO TOUCH
INVARIANTS
FOCUSED TESTS
REAL LIVE TEST
FAILURE CLASSIFICATION
EXIT GATE
COMMIT SHA
OPEN DEBT
NEXT ACTION
```

---

# P39 — Bağlayıcı geliştirme protokolü

- doğru abstraction önce,
- focused/provider-free test sonra,
- paid LLM manual,
- workers=1 önce,
- failure classify edilmeden patch yok,
- case-derived prompt yok,
- semantic regex/fuzzy yok,
- one semantic authority,
- no silent fallback,
- raw SQL Manager’a yok,
- exact-same-SHA A/B,
- every result recorded,
- hidden development blocker değil,
- broad suites milestone/final gate,
- coverage veto-only; semantic authority üretmez,
- receipt provenance-only; intent completeness parser’ı değildir,
- retrieval score truth değildir,
- query repair semantic meaning’i değiştiremez,
- Metabase physical FK join Dima relationship authority’yi bypass edemez,
- ephemeral handle durable Dima identity değildir,
- missing principal background execution admin’a düşmez,
- same frozen SHA model-floor A/B yapılır,
- production switch ve code deletion aynı commit olmaz,
- semantic surface completeness surface-level’dır; kind-level green unresolved sibling’i gizleyemez,
- Standard/Research same-turn accepted authority XOR shared arbiter ile enforced,
- semantic linker ve temporal normalizer ayrı model-role contract’larıdır,
- LLM_FIRST_COGNITION; deterministic code analytical strategy sahibi olmaz,
- SEMANTIC_CORE_IS_NOT_ANALYTICAL_PLANNER,
- yeni Dima-owned deterministic cognition/heuristic mechanism önce SEMANTIC_NECESSITY_GATE; native Metabase capability reuse'ı bu gate'i gerektirmez,
- Luna default/economic baseline; Sol ceiling/headroom,
- same frozen data/tools/prompt/context/permissions/oracle model A/B şartı,
- Luna fail tek başına deterministic mechanism gerekçesi değildir,
- Sol-only success açıkça SOL_ESCALATION_CAPABILITY olarak sınıflanır,
- ADAPTIVE_GOVERNANCE; effective level mandatory tenant/capability/security minimumlarının altına düşmez,
- Level 0 dahil principal/tenant/effective-access/provenance envelope zorunludur,
- Fast Track/ask-v2 yalnız CONTROLLED HARVEST; bulk merge/cherry-pick yok,
- architecture value delta kanıtı olmayan cognition mechanism eklenmez.

---

# P40 — Nihai tamamlanma tanımı

```text
Dima semantic/research/evidence/decision authority = complete
Native Metabot analytical cognition integration = complete
DimaSemanticSpec = canonical
Metabase primary analytics substrate = certified
Wren removed OR explicitly retained for proven semantic gap
Standard = certified
Research = certified
Evidence = certified
Root cause = certified
Report = certified
Decision = certified
Tenant security = certified
Persistence/resume = certified
BI workspace = integrated
Sector onboarding = operational
DEV80 / Validation50 / Hidden50 = sealed
pilot rollback = tested
front-door legacy authority = 0
semantic duplicate owner = 0
unapproved implicit join = 0
security-bound lossy replay = 0
Metabase upgrade rollback = rehearsed
```

Nihai ürün:

> **Dima, Metabase üzerinde çalışan bir chatbot değil; Metabase’i analytics operating system olarak kullanan, kendi semantic authority, research, evidence ve decision-intelligence katmanına sahip tam iş analisti platformudur.**


---

# P41 — Zorunlu end-to-end simülasyon matrisi

Aşağıdaki senaryolar doküman örneği değil, implementation acceptance senaryosudur.

| Senaryo | Beklenen authority/path | Yasak davranış |
|---|---|---|
| simple Level-0 native analytical request | LLM → minimum Dima envelope → Metabase → receipt/evidence | security/provenance bypass |
| Level-1 canonical semantic request | LLM → canonical metric/dimension/time identity → Metabase | label/name as semantic truth |
| Level-2 governed relationship request | LLM → approved RelationshipSpec/grain/security gates → Metabase | physical FK auto-authority |
| frozen cognition necessity case | exact same corpus/tools/context: Luna baseline then Sol ceiling | model-specific prompt/example/tool changes |
| “Bu ay net gelir” | Standard → metric → Metabase → receipt | Research açmak |
| “Ürün bazında net gelir” | Standard breakdown | raw table/name guess |
| “Geçen ayla karşılaştır” | typed temporal intent → deterministic dates | Türkçe keyword branch |
| “En yüksek 5 ürün” | ranking+direction+limit ledger | sadece LIMIT |
| ambiguous “siyah” | clarification, query=0 | auto-pick |
| no semantic candidate | typed semantic gap | raw schema fallback |
| product-machine relationship | approved RelationshipSpec | physical FK auto-authority |
| relationship path yok | BLOCKED | Metabase implicit join |
| research: “neden düştü?” | Research → evidence → replan | tek dev SQL |
| first hypothesis falsified | Manager changes derived task | user MUST mutate |
| empty result | limitation/alternate evidence | “etkisiz” claim |
| result cached then permission revoked | read denied | creator-time permission reuse |
| Metabase index down | INDEX_UNAVAILABLE | NO_MATCH/semantic-gap saymak |
| handle expired | durable receipt still audit-valid; replay revalidate | receipt’i kaybetmek |
| runtime-only security params | execute maybe; replay persistence forbidden | lossy save |
| duplicate background delivery | one terminal effect | double query/result |
| cancel during planning | cleanup + terminal cancel | orphan pending jobs |
| resource formula changed | evidence stale/version mismatch | old claim silently current |
| Wren vs Metabase mismatch | triage + stop | whichever result “looks right” |
| tenant A result viewed by B | deny | cross-tenant evidence |
| Metabase health green, Agent API disabled | typed runtime capability failure | semantic fallback |
| source column renamed | stale/reprovision/clarify as appropriate | similar-name silent bind |
| result exceeds conversational row budget | aggregate/refine/export capability | huge raw payload to Manager |

Her senaryoda:
- authority id,
- semantic version,
- access fingerprint,
- query receipt,
- evidence refs,
- outcome class
kaydedilir.

---

# P42 — Phase-level hard gates

## Gate G0 — Migration-safe branch

```text
certified base SHA known
sealed docs committed
legacy authority imports identified
Wren sentinel green
```

## Gate G1 — Thin Metabase bridge

```text
semantic reparse = 0
manual dual metric definitions = 0
manual dual relationship definitions = 0
implicit join bypass = 0
```

Fail → Metabase structured execution rejected; workspace/reference track can continue.

## Gate G2 — Standard substrate

```text
numeric/grain/time parity acceptable
permission/access parity exact
receipt bindable
repair meaning-preserving
```

## Gate G3 — Semantic migration

```text
all used Wren semantics represented
WREN_ONLY_GAP release-critical = 0 OR explicit retain decision
```

## Gate G4 — Research

```text
USER_MUST silent loss = 0
unverified numeric claim = 0
no-progress bounded
relationship authority intact
```

## Gate G5 — Product integration

```text
front-door legacy authority = 0
Standard/Research XOR enforced
no silent fallback
rollback flag works
```

## Gate G6 — Release

```text
20–25 rehearsal green
DEV80 once
Validation50 no tuning
Hidden50 no tuning
```

---

# P43 — Cutover ve rollback planı

Production switch tek seferlik “big bang” değildir.

```text
Stage 0  Wren primary / Metabase lab
Stage 1  Wren primary / Metabase shadow execution
Stage 2  Metabase Standard primary for allowlisted tenants; Wren shadow
Stage 3  Metabase Standard primary / Research selected path
Stage 4  Wren runtime disabled behind reversible flag
Stage 5  stability window
Stage 6  Wren code/deployment cleanup in separate change
```

Rollback trigger:
- P0 security event,
- unexplained semantic/numeric mismatch,
- receipt/provenance loss,
- material p95/runtime instability,
- resource drift not reconciled.

Rollback must switch substrate without changing accepted Dima semantic authority schema.

---

# P44 — Dima/Metabase ownership matrix

```text
Dima owns:
  user language understanding
  semantic authority
  semantic version
  approved relationships
  accepted obligations
  research state
  evidence truth status
  findings/hypotheses
  reports/decisions
  tenant business semantics

Metabase owns:
  metadata access
  query representation machinery
  query validation/repair mechanics
  query processor
  driver connectivity
  BI resource execution
  visualization/dashboard substrate
  selected cache/result mechanics

Shared only through explicit contracts:
  resource mapping
  query execution
  permission identity
  result/evidence handoff
```

Hiçbir shared responsibility “iki owner” anlamına gelmez.

---

# P45 — Yasak kısayollar

```text
Metabase çalışıyor → Wren’i hemen sil
Metabase metric var → Dima metric definition gereksiz
Agent API query döndürdü → query semantically correct
query_handle var → durable provenance hazır
embedding hit → canonical semantic bulundu
physical FK var → business relationship approved
cached result var → her viewer görebilir
service account çalıştırıyor → user permission eşdeğer
repair geçti → semantic meaning korunmuştur
workspace güzel → Metabase cognition owner olsun
hidden fail → prompta hidden örnek öğret
```

Bunlardan biri implementation’da görülürse STOP-THE-LINE.

---

# P46 — Metabase source watchlist

Her runtime upgrade öncesi özellikle diff edilecek source families:

```text
src/metabase/agent_api/                # settings + API availability included
src/metabase/agent_lib/representations/
src/metabase/mcp/v2/
src/metabase/mcp/session.clj
src/metabase/query_permissions/
src/metabase/query_processor/
src/metabase/queries/cached_result.clj
src/metabase/entity_retrieval/
src/metabase/indexed_entities/
src/metabase/parameters/field_values.clj
src/metabase/explorations/
src/metabase/content_verification/
src/metabase/glossary/
src/metabase/metrics/
src/metabase/measures/
```

Source değişikliği otomatik product change değildir; impacted Dima contract testleri seçilir.

---

# P47 — Yeni branch’e başlama komutu / ilk 5 operasyon

Developer bağlamı sıfırlansa bile başlangıç sırası:

```text
1. certified Dima source SHA’yı yeniden doğrula; moving HEAD’den branch açma.
2. feat/dima-metabase-platform branch’ini o SHA’dan oluştur; bu iki belgeyi mühürle.
3. AnalyticsSubstrate + WrenAdapter seam’ini zero-behavior-change olarak çıkar.
4. Metabase lab runtime’ı exact release/image digest ile kur; product routing bağlama.
5. P3A bridge preflight’i yap; semantic duplication olmadan ResolvedAnalyticsIntent → Metabase mümkün değilse structured-execution kolunu erken reject et.
```

Bu beş adım bitmeden Metabase’i production request path’ine koyma.


---

# ROADMAP EK — P12X-C / DIMA METABASE ENGINE

DMP-DEC-0031 ile tam V0+A+B Agent-API bake-off fork bootstrap için prerequisite olmaktan çıkarılmıştır. Frozen 16-case corpus korunur ve daha sonra native capability regression/stabilization gate'i olarak kullanılır. Sealed tarihsel milestone'lar yeniden numaralandırılmaz.

## P12X-C0 — FORK BOOTSTRAP

```text
metabase/metabase v0.63.18 / 2ba2485...
→ UpcyTech/dima-metabase-engine
→ upstream history preserved
→ fork-source build 0.63.18-dima.0
→ modified existing upstream source files = 0
→ initial DIMA_PATCH_SURFACE
```

## P12X-C1 — STOCK-VS-FORK CAPABILITY PARITY

Aynı Boyahane snapshot, bootstrap, restricted user, permissions ve Luna ile frozen corpus'tan 4–6 yüksek-bilgi vakası. Exit:
```text
FORK_CAPABILITY_RETENTION = 100% of stock-PASS tasks
new silent wrong = 0
permission regression = 0
dataset-scope drift = 0
```

## P12X-C2 — STABLE DIMA BRIDGE + NATIVE PARITY

İzole Dima engine namespace/route; yalnız engine identity, correlation/trace identity, native request delegation ve native stream/result observation. Native Metabot preflight/orchestration tekrar yazılmaz. Exit: bridge capability retention = 100% of fork-native PASS tasks; permission behavior no weaker.

## P12X-C3 — UPSTREAM SYNC / PATCH-SURFACE CERTIFICATION

```text
detect stable upstream
→ sync candidate
→ conflict report
→ compile/upstream tests
→ Dima tests
→ native capability sentinel
→ candidate image
→ DIMA_PATCH_SURFACE
→ manual promotion only
```

## P13 — PRODUCTION STANDARD OVER DIMA METABASE ENGINE

P13 yalnız C1 capability parity ve C2 stable bridge parity sonrasında başlar. `ResolvedAnalyticsIntent`, `ExecutionAccessSnapshot`, `CanonicalProjection`, `QueryReceipt`, `EvidenceArtifact`, `DimaSemanticSpec`, `EntityValueAdoptionGate` korunur; native Metabot/query execution içinde hangi trust transition'a bağlanacakları P13'te yeniden değerlendirilir.

C0/C1/C2 sırasında P13 governance hook'ları başlatılmaz.
