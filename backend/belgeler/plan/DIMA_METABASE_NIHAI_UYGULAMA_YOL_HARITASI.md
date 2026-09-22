# DIMA + METABASE — NİHAİ UYGULAMA YOL HARİTASI

Tarih: 22 Eylül 2026
Dal: feat/dima-metabase-foundation
Başlangıç SHA: 3774484167f1056d89da0e0609246fb4a05057ec
Mimari eş belge: DIMA_METABASE_NIHAI_MIMARI_VE_FIZIBILITE_RAPORU.md
Belge rolü: Uygulama sırası, test/gate disiplini, gün bazlı geliştirme programı ve nihai production seal otoritesi.

---

# MBP0 — OPERASYON PROTOKOLÜ

Bu dalda geliştirme aşağıdaki kurallarla yürütülür.

## MBP0.1 Temel prensip

Vaka geçirerek sistem yapılmaz.

Doğru abstraction kurulur; vakaların geçmesi onun doğal sonucu olur.

## MBP0.2 Geliştirme önceliği

Öncelik:

1. doğru architecture
2. doğru owner
3. çalışan vertical
4. focused gate
5. milestone gate

Test kampanyası geliştirmeyi yönetmez.

Test abstraction’ı doğrular.

## MBP0.3 Failure triage

Fail sonrası product code değişmeden önce sınıf zorunlu:

- MODEL_COGNITION
- CONTRACT_ARCHITECTURE
- RESOLVER_TRUTH
- TEMPORAL_BINDING
- METABASE_QUERY_REPRESENTATION
- METABASE_PERMISSION
- METABASE_METADATA_STALE
- METABASE_PROVIDER
- DATABASE
- EVIDENCE_PERSISTENCE
- TENANT_SECURITY
- EVAL_ORACLE
- TRANSPORT_PROVIDER
- UNSUPPORTED_CAPABILITY

Infra fail semantic fail değildir.

## MBP0.4 Yasaklar

- testcase-specific branch
- Türkçe keyword/regex parser
- fuzzy threshold ile semantic truth
- case-derived system prompt
- raw SQL Manager tool
- Metabot’u ikinci semantic owner yapmak
- Standard fail → silent Research fallback
- Wren fail → Metabase fallback veya tersi
- global superuser execution
- accepted authority sonrası raw prompt’u başka modelde yeniden semantic authority yapmak
- Metabase retrieval score’u truth kabul etmek
- repair edilmiş query’yi semantic equivalence doğrulamadan execute etmek

## MBP0.5 Testing cadence

Normal loop:

    code
    → 3–15 sn focused provider-free
    → continue

Milestone:

    focused family
    → workers=1 live
    → 8–16 canary
    → sentinel

Final release:

    20–25 integrated rehearsal
    → FINAL ENGINEERING FREEZE
    → DEV80 once
    → CODE FREEZE
    → VALIDATION50
    → external HIDDEN50
    → certification seal

## MBP0.6 Commit discipline

Her vertical sonunda living receipt:

- SHA
- amaç
- owner
- files touched
- tests
- live evidence
- failure class
- open debt
- next gate

---

# MBP1 — NİHAİ PROGRAMIN FAZLARI

Program 21 ana güne/faza ayrılır.

Bu “takvim günü” zorunluluğu değildir.

Bir günün exit gate’i geçmeden sonraki gün architecture authority olarak başlamaz.

    M0  Baseline + source freeze
    M1  Metabase infrastructure foundation
    M2  Dima ↔ Metabase adapter contract
    M3  DCSS canonical semantic model
    M4  Wren semantic extraction + migration receipts
    M5  DCSS → Metabase semantic compiler
    M6  Standard query compiler + Metabase query lifecycle
    M7  AcceptedStandardAuthority real execution
    M8  Principal / tenant / permission parity
    M9  Value/entity retrieval + metadata versioning
    M10 Research Manager on Metabase substrate
    M11 Evidence + QueryContract durable chain
    M12 Cross-domain / relationship / grain safety
    M13 Root-cause + hypothesis layer
    M14 ReportDocument + claim gates
    M15 BI workspace + dashboard/save integration
    M16 Persistence / resume / schedule / async runtime
    M17 Security / PII / operational hardening
    M18 Performance / scale / reliability
    M19 Wren parity + removal decision
    M20 Final product integration / certification / pilot

Bu plan sonunda hedef:

    Dima intelligence plane
    +
    Dima canonical semantic truth
    +
    Metabase analytics operating system
    +
    evidence-backed research
    +
    report / decision intelligence
    +
    production-grade BI workspace

---

# M0 — BASELINE, FREEZE VE YENİ DALIN MÜHÜRLENMESİ

## Amaç

Yeni proje deneyinin neyin üstünden başladığını kesinleştirmek.

## Yapılacaklar

1. feat/dima-metabase-foundation base SHA kaydedilir.
2. Eski feat/ask-v2-mvp reference olarak korunur.
3. Wren current green sentinels yeniden çalıştırılır.
4. Current semantic/reference canary sonuçları snapshot edilir.
5. Metabase pinned SHA kaydedilir.
6. Dima current capabilities inventory çıkarılır.
7. No-touch reference artifacts listelenir.

## Baseline artifacts

- Wren semantic schema snapshot
- Wren cube list
- metrics
- dimensions
- time dimensions
- relationships
- aliases
- units
- lower_is_better
- security/always filters
- sample golden result set
- QueryContract examples

## Test

Provider-free current architecture family.

Wren real sentinel.

No product change.

## Exit

Baseline receipt oluşmuş.
Exact source SHAs kayıtlı.
Migration oracle hazır.

---

# M1 — METABASE INFRASTRUCTURE FOUNDATION

## Amaç

Metabase’i local/dev ortamda güvenilir substrate olarak ayağa kaldırmak.

## Topoloji

    Dima API
      ↓ private network
    Metabase pinned service
      ↓
    Metabase app PostgreSQL
      ↓
    analytical DB

## Yapılacaklar

- pinned Metabase Docker/JAR deployment
- dedicated app PostgreSQL
- health endpoint
- config/secrets
- Dima service discovery
- network isolation
- startup migration check
- backup/restore smoke
- version endpoint capture
- request correlation header
- dev tenant DB registration

## Yeni Dima config

- metabase_base_url
- metabase_version_expected
- metabase_connect_timeout
- metabase_read_timeout
- metabase_enabled
- metabase_execution_mode
- metabase_service_identity

## Yasak

User query için superuser credential product hot path’e bağlanmaz.

## Failure simulations

- Metabase down
- app DB down
- analytical DB down
- wrong version
- migration pending
- timeout

## Expected typed outcomes

- METABASE_PROVIDER
- DATABASE
- VERSION_MISMATCH

Semantic failure yok.

## Exit

Metabase service deterministic şekilde boot/stop/restart ediliyor.
Version pin doğrulanıyor.
Dima health integration green.

---

# M2 — DIMA ↔ METABASE ANALYTICS PORT

## Amaç

Dima domain code’unu Metabase API ayrıntılarından ayırmak.

## Yeni abstraction

MetabaseAnalyticsPort

Örnek capability seti:

- get_version
- list_semantic_resources
- read_resource
- validate_query
- resolve_query
- execute_query
- get_query_result
- get_field_values
- save_question
- save_chart
- get_saved_question

İlk gün yalnız minimum subset uygulanır.

## DTO’lar

- MetabasePortableQuery
- MetabaseCanonicalQueryRef
- MetabaseExecutionReceipt
- MetabaseResultEnvelope
- MetabasePermissionReceipt

## Kurallar

Domain code HTTP route bilmez.
Metabase numeric ID Dima canonical semantic ID olmaz.
Adapter response typed olur.
Unexpected JSON fail-closed olur.

## Provider-free tests

FakeMetabasePort.

Contract tests.

Timeout/error mapping.

## Live smoke

health + harmless metadata read.

## Exit

Dima business code Metabase client kütüphanesine doğrudan bağlanmadan substrate’a erişiyor.

---

# M3 — DCSS: DIMA CANONICAL SEMANTIC SPECIFICATION

## Amaç

Wren semantic değerini kaybetmeden substrate-independent semantic truth oluşturmak.

## Yeni domain model

DimaCanonicalSemanticSpecification.

Minimum entities:

- SemanticSubject
- CanonicalMetric
- CanonicalDimension
- TemporalDimension
- RelationshipEdge
- SemanticAlias
- SecurityPolicy
- EntityValuePolicy
- SpecializedOperator
- SectorPack
- TenantOverlay

## Metric fields

- canonical_id
- display_name
- description
- formula
- aggregation
- unit
- grain
- additivity
- lower_is_better
- default_time_dimension
- aliases
- dependencies
- visibility
- provenance
- version

## Dimension fields

- canonical_id
- type
- grain
- aliases
- categorical
- value_policy
- sensitivity
- default_temporal_unit
- provenance

## Relationship fields

- source
- target
- cardinality
- join path
- grain alignment
- allowed metrics
- many-to-many rule
- time alignment
- security rule

## Versioning

semantic_version = content hash.

Her request semantic_version’a bağlanır.

## Test

Schema validation.
No duplicate canonical ID.
Dependency cycle detection.
Relationship integrity.
Unit/grain validation.

## Exit

DCSS Wren veya Metabase’a referans vermeden iş anlamını temsil edebiliyor.

---

# M4 — WREN SEMANTIC EXTRACTION VE MIGRATION RECEIPTS

## Amaç

Bugünkü Wren yatırımlarını kayıpsız DCSS’e taşımak.

## Tool

wren_to_dcss_export.py benzeri offline migration utility.

## Extract

- models
- cubes
- measures
- dimensions
- time dimensions
- relationships
- synonyms
- labels
- units
- lower_is_better
- NL exposure
- sensitivity
- default measures
- custom metadata
- always filters
- specialized wrapper semantics

## Her entity için MigrationReceipt

- source Wren path
- source hash
- DCSS ID
- transformation
- unsupported fields
- manual review
- parity tests

## Unsupported handling

Silme yok.

UNMAPPED / BLOCKED.

## Test

100% Wren semantic inventory accounted.

No silent drop.

## Exit

Wren semantic inventory’nin her elemanı:
- mapped
- intentionally deprecated
- blocked

durumlarından birine sahip.

---

# M5 — DCSS → METABASE SEMANTIC COMPILER

## Amaç

DCSS’i Metabase runtime objects’a deterministik derlemek.

## Mapping

CanonicalMetric
→ Measure veya Metric

CanonicalDimension
→ persisted Dimension / mapping

TemporalDimension
→ dimension metadata + temporal unit

Aliases
→ AI Context synonyms + descriptions

Definitions
→ Glossary / descriptions

Segments
→ reusable filters

Subject
→ model/table/collection organization

## Stable identity

Dima canonical IDs saklanır.

Metabase numeric IDs runtime implementation detail.

Portable entity_id / UUID mapping registry kullanılır.

## Registry

SemanticRuntimeMapping:

- semantic_version
- canonical_id
- Metabase entity type
- entity_id
- local numeric id
- UUID
- compiled hash
- status

## Compile modes

PLAN
APPLY
VERIFY

## Drift detection

Metabase manually edited object != compiled hash
→ DRIFTED

Production semantic object silent overwrite yok.

## Test

Compiler idempotency.
Round-trip readback.
Formula hash parity.
Dimension mapping parity.
Alias projection.
Orphan handling.

## Exit

Test tenant için DCSS’den Metabase semantic workspace yeniden üretilebiliyor.

---

# M6 — STANDARD QUERY COMPILER + METABASE REPRESENTATIONS PIPELINE

## Amaç

Accepted StandardProjection’ı Metabase query engine’de deterministic çalıştırmak.

## New flow

    StandardProjection
      ↓
    MetabaseProjectionCompiler
      ↓
    portable bounded query
      ↓
    Metabase validate
      ↓
    repair
      ↓
    resolve
      ↓
    canonical MBQL
      ↓
    semantic equivalence gate

## Compiler inputs

Yalnız:
- semantic handles
- exact resolved filters
- exact periods
- comparison
- ranking
- limit

Raw user prompt yok.

## MetabaseRepairEquivalenceGate

Repair sonrası extract:

- metric refs
- dimension refs
- filters
- time range
- ranking
- limit
- source entities

Accepted projection fingerprint ile karşılaştır.

Mismatch → STOP execution.

## Raw SQL

Disabled.

## Cases

- aggregation
- breakdown
- ranking
- current period
- explicit comparison
- top N
- filter
- empty result
- invalid representation repair
- repair semantic mutation attempt

## Exit

StandardProjection → Metabase result deterministic vertical green.

---

# M7 — ACCEPTED STANDARD AUTHORITY REAL EXECUTION

## Amaç

AcceptedStandardAuthority’yi gerçek security/execution gate yapmak.

## Invariant

projection_hash(authority)
=
projection_hash(executed request)

Değilse reject.

## Flow

- seal authority
- compile
- validate/repair/resolve
- equivalence
- permission
- execute
- result validate
- QueryContract
- EvidenceArtifact

## Failure cases

- authority reused for modified projection
- context_version mismatch
- semantic_version mismatch
- expired Metabase query ref
- duplicate execution
- replay

## Idempotency

execution_key:
tenant + authority_id + projection_hash + semantic_version.

## Exit

Seal gerçek enforcement haline gelir.

---

# M8 — PRINCIPAL / TENANT / PERMISSION PARITY

## Amaç

Metabase permission modelini Dima security contract’ıyla bağlamak.

## Principal mapper

DimaPrincipal
→ Metabase execution identity.

## Mandatory

No global admin user execution.

## Tenant mapping

Her tenant:

- allowed database IDs
- collection root
- groups
- semantic namespace
- result scope

## Test matrix

Tenant A user:
- own DB allowed
- tenant B DB denied
- B collection denied
- B query handle denied
- B cached result denied

Same tenant role variants.

Permission revoked after query creation.

Sandbox attribute changed.

Database routing attribute changed.

## Cached result

Viewer lens compatibility enforced.

## Exit

Cross-tenant P0 = 0.

Permission parity green.

---

# M9 — VALUE / ENTITY RESOLUTION + METADATA VERSIONING

## Amaç

Metabase FieldValues / IndexedEntities reuse ederek entity resolution’ı ölçeklemek.

## Flow

Known canonical dimension
→ value candidates
→ Dima bounded binder
→ exact value handle.

## Sensitive fields

exact-only.

No semantic fuzzy auto-pick.

## MetadataVersion

Hash inputs:

- DCSS version
- Metabase semantic compile version
- relevant warehouse schema snapshot
- value-index version/policy

## Drift

Field removed/renamed.
Dimension orphaned.
Index stale.
Value set changed.

## Expected

typed metadata stale / refresh required.

## Exit

Value/entity binding tenant/lens safe ve versioned.

---

# M10 — RESEARCH MANAGER METABASE SUBSTRATE

## Amaç

Research cognition’ı değiştirmeden execution substrate’ı Metabase’a taşımak.

## Tools

- resolve_semantics
- run_standard_analysis
- run_relationship_analysis
- inspect_evidence
- request_clarification
- finish

Raw SQL yok.

## Research flow

AcceptedTurnContract
→ UserObligationLedger
→ task
→ StandardProjection
→ same Metabase path
→ EvidenceArtifact
→ observe
→ replan

## Test families

- multi-MUST
- evidence contradicts hypothesis
- zero rows
- permission blocked branch
- tool failure
- budget exhaustion
- no progress
- derived task
- exclusion
- clarification

## Exit

Research Manager substrate swap sonrası aynı authority semantics’i koruyor.

---

# M11 — QUERYCONTRACT + EVIDENCE DURABLE CHAIN

## Amaç

Metabase query/result lifecycle’ı Dima audit/evidence chain’e bağlamak.

## QueryContract fields

- contract_id
- authority_id
- projection_hash
- semantic_version
- Metabase version
- canonical MBQL hash
- data source
- principal/lens
- result hash
- query start/end
- validation status
- limitations

## EvidenceArtifact

Metabase cached result sadece external ref olabilir.

Dima:
- bounded sample
- schema
- content hash
- durable ref
- access policy
- provenance

tutar.

## Final-report evidence

Required evidence durable snapshot’a promote edilir.

## Test

Metabase cache GC.
Evidence still auditable.

Permission revoke.
Evidence read re-gated.

## Exit

Every official numeric claim has durable trace.

---

# M12 — CROSS-DOMAIN / RELATIONSHIP / GRAIN SAFETY

## Amaç

Wren relationship gücünü kaybetmeden Metabase QP kullanmak.

## DCSS RelationshipRegistry

Mandatory.

## CrossDomainJoinGate

Checks:

- path exists
- cardinality
- grain compatibility
- metric additivity
- time alignment
- bridge rule
- tenant permission

## Execution strategies

1. direct Metabase join
2. governed Metabase model/view
3. prebuilt warehouse view
4. specialized Dima analytics tool

Strategy chosen deterministically.

## Forbidden

LLM invents join.

## Tests

- one-to-many safe
- many-to-many unsafe
- duplicated measure
- incompatible grain
- missing relationship
- time misalignment

## Exit

Silent duplicated aggregate = 0.

No-path join = 0.

---

# M13 — ROOT CAUSE + HYPOTHESIS

## Amaç

Dima’yı BI chatbot’tan decision intelligence ürününe taşıyan ana katman.

## Objects

Hypothesis:
- id
- statement
- origin
- evidence_for
- evidence_against
- status
- confidence class

Epistemic statuses:

- ASSOCIATION
- CONTRIBUTION
- CANDIDATE_CAUSE
- CONFIRMED_CAUSE

CONFIRMED_CAUSE yalnız explicit causal evidence policy ile.

## Manager behavior

Evidence gördükçe:
- hypothesis add
- hypothesis weaken
- branch stop
- next query

## Test

Correlation cannot auto-promote cause.

Contradictory evidence visible.

No evidence claim blocked.

## Exit

Root-cause report epistemically gated.

---

# M14 — REPORTDOCUMENT + REPORTCLAIMGATE

## Amaç

Araştırma sonucunu kanıtlı rapora dönüştürmek.

## ReportDocument

- executive summary
- scope
- findings
- charts
- tables
- root-cause candidates
- limitations
- recommendations
- evidence refs
- methodology

## ReportClaimGate

Numeric claim:
→ QueryContract/Evidence required.

Analytical claim:
→ Finding ref required.

Causal wording:
→ compatible epistemic status required.

Every USER_MUST:
→ report section veya explicit limitation.

## Test

invented number
unsupported cause
missing obligation
stale evidence
permission-hidden evidence

## Exit

Evidence-free report claim = 0.

---

# M15 — BI WORKSPACE + DASHBOARDS + SAVED ANALYSES

## Amaç

Metabase’in olgun BI workspace’ini Dima’ya bağlamak.

## Features

- save Dima result as Metabase question
- generate chart
- add to dashboard
- collection placement
- user opens in Metabase embedded/workspace view
- Dima provenance retained

## Provenance metadata

- Dima authority ID
- QueryContract
- semantic version
- report/run ID

## Manual BI content

Metabase user-created content Dima verified evidence değildir.

Promotion flow:

DRAFT
→ REVIEWED
→ VERIFIED
→ eligible for Dima knowledge/reuse.

## Exit

Conversation ↔ BI workspace round-trip çalışıyor.

---

# M16 — PERSISTENCE / RESUME / SCHEDULE / ASYNC RUNTIME

## Amaç

Uzun research işleri güvenilir çalıştırmak.

## Persistent ResearchRun

- state
- accepted contract
- ledger
- tasks
- evidence refs
- manager turn
- budgets
- timestamps

## Idempotency

Queue redelivery safe.

Duplicate query result does not duplicate evidence.

## Cancellation

User cancel:
- pending tasks canceled
- running query cancellation attempted
- final state CANCELED

## Resume

Restart after process crash.

## Schedules

Saved AnalysisSpec can run scheduled.

## Alerts

Evidence/result threshold trigger can generate event.

## Exit

Process restart research kaybettirmiyor.

---

# M17 — SECURITY / PII / OPERATIONAL HARDENING

## Scope

- principal
- tenant
- PII
- logs
- secrets
- query limits
- statement timeout
- export/download
- cached result access
- embedded workspace
- service auth
- audit log

## PII

Sensitive values model context’e gereksiz girmez.

Evidence sample masks policy.

## Abuse

- giant query
- huge cardinality
- expensive nested joins
- malicious metadata text
- prompt injection in descriptions
- semantic alias poisoning

Metadata is data, not instruction.

## Exit

Security attack table green.

---

# M18 — PERFORMANCE / SCALE / RELIABILITY

## Workers=1 certification first

Then concurrency.

## Load dimensions

- multiple tenants
- multiple DBs
- standard QPS
- research concurrent runs
- dashboard traffic
- result cache
- semantic compile/reconcile

## Measure

- p50/p95/p99
- DB time
- Metabase QP time
- Dima time
- LLM time
- cache hit
- app DB load
- queue depth
- evidence write
- cost per verified success

## Circuit breakers

Metabase down:
No raw DB fallback.

DB slow:
bounded timeout.

LLM slow:
typed timeout.

## Exit

SLO defined and met for pilot load.

---

# M19 — WREN PARITY VE RUNTIME REMOVAL KARARI

## Amaç

Wren semantic/execution yatırımını gerçekten kayıpsız taşıdığımızı kanıtlamak.

## Frozen parity corpus

Her capability:

- exact same semantic intent
- Wren result
- Metabase result
- normalized comparison

## Compare

- schema
- values
- aggregation
- grouping
- period
- ranking
- null behavior
- relationship
- security
- units

## Numeric tolerance

Metric classına göre explicit.

Silent mismatch = fail.

## Semantic parity

MigrationReceipt coverage 100%.

## Decision outcomes

A. Full parity:
Wren runtime removal authorized.

B. Metabase execution good, semantic gap remains:
Wren semantic reference retained; runtime not removed.

C. capability gap:
specialized Dima tool or warehouse view.

## Wren removal steps

- production route disabled
- shadow retained one release
- rollback switch
- old Wren code marked legacy
- deletion only after rollback window

## Exit

One production analytics substrate.

---

# M20 — FINAL PRODUCT INTEGRATION VE CERTIFICATION

## Final product flow

Standard:
User → Dima → authority → Metabase → evidence → answer.

Research:
User → contract → manager → Metabase tools → evidence → findings → report.

BI:
Evidence/query → Metabase saved question/dashboard.

Decision:
Report/findings → DecisionBrief → recommendation/decision record.

## Final 20–25 scenario rehearsal

Must include:

- simple standard
- ranking
- comparison
- temporal
- ambiguity
- correction
- follow-up
- topic switch
- research
- evidence contradiction
- root cause
- report
- cross-domain
- permission revoke
- tenant isolation
- cached result
- metadata drift
- Metabase restart
- DB timeout
- high cardinality
- schedule
- resume
- dashboard save
- stale authority
- no-progress

## Freeze

All green:
FINAL ENGINEERING FREEZE CANDIDATE.

Then:

DEV80 exactly once.

No tuning after DEV80 except P0 architecture fix requiring explicit unfreeze.

Then:

Validation50.

No tuning.

Then:

fresh external Hidden50.

No tuning.

Then:

Certification Seal.

Then pilot flag activation.

---

# MBP2 — DOSYA / MODÜL HEDEF HARİTASI

Önerilen Dima yeni modülleri:

    app/v2/metabase/
      client.py
      port.py
      schemas.py
      compiler.py
      equivalence.py
      principal.py
      metadata.py
      result_adapter.py
      versioning.py

    app/v2/semantics/
      canonical_spec.py
      compiler.py
      migration.py
      registry.py
      relationships.py

    app/v2/evidence/
      contracts.py
      store.py
      access.py

Mevcut korunacak:

- manager runtime
- preacceptance
- semantic retriever/binder
- temporal intent/binding
- standard projection
- accepted authority
- research models
- completion gates

Wren code migration boyunca no-touch reference olabilir.

---

# MBP3 — CI / WORKFLOW STRATEJİSİ

Push başına:

- provider-free focused only
- no paid LLM
- no full Metabase integration suite unless touched family

Manual workflows:

- Metabase live smoke
- Wren parity
- workers=1 reference model
- canary
- security sentinel

Milestone workflow:

- pinned Metabase service
- seeded DB
- real QP
- permissions
- result parity

Paid LLM manual-only.

---

# MBP4 — METABASE UPGRADE PROTOKOLÜ

Upgrade request:

1. current pinned SHA/version
2. candidate version
3. changelog/source audit
4. Agent API contract diff
5. representations diff
6. permission diff
7. metric/dimension diff
8. migration dry-run
9. adapter tests
10. canary
11. rollback image ready

No floating latest.

---

# MBP5 — SEMANTIC CHANGE PROTOKOLÜ

Tenant/sector semantic change:

1. DCSS change
2. semantic_version bump/hash
3. compile PLAN
4. diff receipt
5. APPLY
6. readback
7. parity focused test
8. activate context version

Old in-flight request old immutable semantic_version ile tamamlanır veya explicitly aborted olur.

Silent mid-request semantic swap yasak.

---

# MBP6 — PRODUCT SUCCESS KRİTERLERİ

P0:

- silent wrong = 0 on certified P0 set
- tenant leak = 0
- ambiguity auto-pick = 0
- evidence-free numeric claim = 0
- unsupported causal claim = 0
- no-path join = 0
- semantic repair mutation accepted = 0
- accepted authority count / turn = exactly 1

P1:

- standard supported completion >= 95%
- research USER_MUST accounted = 100%
- clarification correctness >= 95%
- result-aware replan >= 90%
- report obligation coverage = 100%

P2:

Targets pilot telemetry ile finalized.

Measure:
- standard p95
- research wall time
- TTFS
- Metabase QP p95

P3:

- unnecessary manager admission
- tool calls / verified task
- queries / verified task
- cost / verified success
- repair rate

---

# MBP7 — NİHAİ KOD İNCELEME CHECKLIST

Her PR:

Authority:
- yeni semantic owner var mı?
- raw prompt tekrar parse ediliyor mu?

Semantics:
- canonical ID nereden geliyor?
- retrieval truth oldu mu?

Metabase:
- public adapter boundary mi?
- numeric IDs leak ediyor mu?
- repair equivalence var mı?

Security:
- principal bound mı?
- tenant bound mı?
- cached result lens safe mi?

Evidence:
- QueryContract var mı?
- result hash var mı?

Failure:
- typed outcome mı?
- fallback var mı?

Tests:
- focused family?
- failure receipt?

---

# MBP8 — İLK 5 GELİŞTİRME TICKET’İ

Bu branch üzerinde ilk gerçek kod sırası:

## Ticket 1 — M1 Bootstrap

Metabase pinned dev stack + health.

Exit:
Dima can identify exact Metabase version.

## Ticket 2 — M2 Port

Typed MetabaseAnalyticsPort + fake + HTTP implementation.

Exit:
metadata smoke.

## Ticket 3 — M3 DCSS Core

Canonical semantic data model + validator.

Exit:
sample OEE/revenue domain represented without Wren/Metabase types.

## Ticket 4 — M4 Wren Export

Current semantic pack → DCSS inventory + receipts.

Exit:
silent loss = 0.

## Ticket 5 — M5 Compiler Spike

One metric + one dimension + one temporal field compile into Metabase.

Exit:
Metabase readback matches DCSS.

Bu beş ticket bitmeden Research veya UI entegrasyonuna başlanmaz.

---

# MBP9 — İLK MİMARİ DENEY

Canonical question:

“Bu ay net geliri bölgelere göre göster.”

Same accepted semantic input:

A:
current Wren path

B:
DCSS → Metabase path

Compare:

- semantic refs
- result rows
- aggregation
- group
- time period
- permission
- latency
- QueryContract
- trace

Bu deney Wren vs Metabase agent zekâsını değil execution parity’yi ölçer.

---

# MBP10 — İKİNCİ MİMARİ DENEY

Canonical complex:

“Son 12 ay ürünleri karşılaştır, makineler ve personellerle ilişkisini analiz et, satış performansını yorumla ve raporla.”

Research Manager aynı.

Yalnız analytics execution port değişir.

Compare:

- tasks
- evidence
- query count
- parity
- completion
- report claims
- latency
- failure behavior

Metabase research cognition sahibi değildir.

---

# MBP11 — ROLLBACK STRATEJİSİ

Her substrate cutover’da feature flag:

analytics_substrate =
- wren
- metabase_shadow
- metabase

Shadow mode response user’a yalnız primary’den.

Mismatch telemetry’ye.

Metabase primary cutover sonrası Wren read-only fallback değildir.

Emergency rollback explicit operator action ile olur.

Silent per-request fallback yasak.

---

# MBP12 — NİHAİ “MÜKEMMEL DIMA” TANIMI

Program tamamlandığında Dima:

- Türkçe doğal dili robust anlayan
- business semantic truth’u DCSS ile yöneten
- Metabase üzerinden güvenli analytics yapan
- basit soruda hızlı
- kompleks soruda evidence-aware araştıran
- relationship/grain güvenliği olan
- sayısal iddiayı contract/evidence’a bağlayan
- root-cause iddiasını epistemically sınırlayan
- rapor ve karar üreten
- dashboard/workspace sunan
- tenant/security sınırları sert
- restart/resume destekli
- observable
- versioned
- audit edilebilir
- analytics substrate’a bağımlı olmayan

bir decision-intelligence platformu olur.

Bu yol haritasının son ilkesi:

“Metabase Dima’nın altındaki analytics işletim sistemi olur; Dima’nın semantic hakikati, muhakemesi ve karar zekâsı Dima’da kalır.”

