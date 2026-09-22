# DIMA + METABASE — NİHAİ FİZİBİLİTE, HEDEF MİMARİ VE KAYIPSIZ GÖÇ RAPORU

Tarih: 22 Eylül 2026
Repo: cagataysntrk/dima-backend-feat-wren-strict-agentic
Yeni geliştirme dalı: feat/dima-metabase-foundation
Başlangıç SHA: 3774484167f1056d89da0e0609246fb4a05057ec
Belge rolü: Yeni Metabase-temelli Dima mimarisinin normatif teknik raporu.
Eş belge: DIMA_METABASE_NIHAI_UYGULAMA_YOL_HARITASI.md
Önceki Wren-temelli otoriteler: tarihsel referans ve migration oracle; bu dalda yeni hedef mimarinin uygulama otoritesi değildir.
Metabase source audit referansı: metabase/metabase @ 74216b30981d8310c4cf724d63ca282e2e63529d. 22 Eylül 2026 upstream master fff70175e0b5f82dc0eb267593c717c4a6130206 olup aradaki commit çeviri güncellemesidir; bu raporda incelenen agent/query/semantic kaynakları için pinned SHA kullanılır.

---

# MBR0 — RAPORUN AMACI

Bu raporun amacı “Wren’i Metabase ile değiştirelim mi?” sorusuna yüzeysel cevap vermek değildir.

Amaç şudur:

Dima’nın nihai ürün vizyonuna giderken bugüne kadar Wren etrafında geliştirilmiş semantic, security, evidence, conversation, research ve trust-plane yatırımlarını kaybetmeden; Metabase’in query lifecycle, permissions, BI workspace, metrics/dimensions, caching, persistence, Agent API ve exploration altyapısından maksimum fayda sağlayan yeni bir temel mimari kurmak.

Hedef ürün hâlâ aynıdır:

Dima; kullanıcının doğal dildeki talebini anlayan, iş anlamını kanonik semantic katmanda doğrulayan, doğru veriyi güvenli execution boundary üzerinden çalıştıran, her sayısal iddiayı kanıta bağlayan, basit soruları hızlı cevaplayan, kompleks sorularda kanıt gördükçe araştırmasını geliştiren, bulgu/hipotez/kök-neden/rapor/karar üreten denetlenebilir iş analistidir.

Metabase bu vizyonun kendisi değildir.

Metabase, bu vizyonun altında kullanılacak analytics operating system olmaya adaydır.

Dima ise ürün beyni, semantic authority, evidence/research ve decision-intelligence katmanıdır.

---

# MBR1 — NİHAİ KARAR ÖZETİ

Bu fizibilitenin ana sonucu:

1. Metabase kodunu Dima repository’sine kopyalayıp refactor etmek hedef mimari değildir.
2. Metabase ayrı, pinned ve self-hosted bir servis olarak kullanılacaktır.
3. Dima’nın cognition, semantic authority, research, evidence ve decision katmanları korunacaktır.
4. Wren’in sektör-özel semantic zenginliği çöpe atılmayacaktır.
5. Wren semantic pack/MDL içeriği önce Dima-owned Canonical Semantic Specification’a taşınacaktır.
6. Bu semantic specification daha sonra Metabase Measures, Metrics, Dimensions, Segments, Models, AI Context ve ilgili metadata yüzeylerine derlenecektir.
7. Metabase hiçbir zaman Dima’nın kullanıcı niyetinin sahibi olmayacaktır.
8. Metabase hiçbir zaman tek başına “business semantic truth” sahibi olmayacaktır.
9. Metabase Query Processor, query representation/repair/resolution, permission enforcement, result lifecycle ve BI workspace için primary substrate olacaktır.
10. Wren runtime ancak semantic-equivalence ve execution-parity kanıtları tamamlandıktan sonra kaldırılabilir.
11. Göç boyunca Wren reference oracle / parity challenger olarak tutulur; production’da iki eşit truth engine aynı anda çalıştırılmaz.
12. Nihai hedefte Dima’nın analytics substrate portu replaceable kalır. Metabase primary olabilir; Dima kimliği Metabase’e gömülmez.

Kısa form:

    DIMA
    = cognition + semantic authority + evidence + research + decision intelligence

    METABASE
    = analytics/query/permission/result/BI operating system

    DIMA CANONICAL SEMANTIC SPEC
    = sector/customer business truth

    WREN
    = migration oracle + semantic source during transition
      ve ancak parity tamamlanana kadar runtime challenger

---

# MBR2 — NEDEN BU YÖN WREN-TEMELLİ YOLDAN DAHA ÜMİT VAAT EDİYOR?

Wren’in güçlü olduğu yerler:

- MDL ile business semantic modeling
- model/relationship/cube/measure/dimension tanımı
- deterministic cube query generation
- sektör ve müşteri özel semantic pack yaklaşımı
- source-controlled semantic definitions
- Dima’nın mevcut custom WrenService entegrasyonu

Fakat Dima nihai ürünü için ayrıca şu problemleri çözmek zorundaydı:

- query representation
- query validation
- repair
- metadata hydration
- permission-aware execution
- saved analytics objects
- result caching
- cached-result security
- query history
- collections
- dashboards
- chart builder
- revisions
- content verification
- field value indexing
- background execution
- query result persistence
- workspace
- exploration UX
- embedding
- user-specific data lens
- cross-user result visibility
- driver ecosystem
- operational observability

Metabase kod tabanı bunların büyük bölümünü zaten çözüyor.

Bu nedenle Wren-temelli yolun Dima’ya yüklediği iş:

    “bir decision intelligence ürünü yap”
    +
    “aynı zamanda olgun bir BI/query platformunun önemli parçalarını yeniden yap”

iken Metabase-temelli yol:

    “olgun analytics substrate üstünde Dima’nın özgün intelligence katmanını yap”

şeklindedir.

Bu ikinci problem daha dar, daha gerçekçi ve ürün vizyonuna daha doğrudan bağlıdır.

---

# MBR3 — METABASE KOD SEVİYESİ SOURCE AUDIT ÖZETİ

Bu bölümdeki sonuçlar pinned Metabase SHA üzerindeki gerçek kaynak dosyalarından çıkarılmıştır.

## MBR3.1 Agent runtime

İncelenen alanlar:

- src/metabase/metabot/agent/core.clj
- src/metabase/metabot/agent/profiles.clj
- src/metabase/metabot/agent/memory.clj
- src/metabase/metabot/agent/user_context.clj

Temel desen:

    generic agent loop
    → profile-specific prompt
    → profile-specific tools
    → max iteration
    → tool result
    → memory update
    → terminal tool / stop condition

Buradan alınacak ders:

Dima’da Standard, Research, ileride Report/Decision gibi farklı cognition görevleri için ayrı bespoke agent-loop yazılmamalı.

Dima generic BoundedAgentRuntime kullanılmalı; semantic authority ve domain kuralları profile seviyesinde kalmalıdır.

Metabase agent loop Dima’ya kopyalanmayacaktır. Mimari desen Dima-native olarak uygulanacaktır.

## MBR3.2 Agent API

İncelenen alanlar:

- src/metabase/agent_api/api.clj
- src/metabase/agent_api/query_guards.clj
- src/metabase/agent_api/validation.clj
- src/metabase/agent_api/settings.clj
- src/metabase/agent_api/reference.md

Önemli özellikler:

- agent-facing query construction/execution yüzeyi
- shape validation
- permission validation
- native SQL guards
- validate-only akışları
- usage accounting
- bounded API surface
- query execution öncesi canonical pipeline

Sonuç:

Dima’nın Metabase entegrasyonu DB’ye doğrudan erişmek yerine Metabase’in resmi query lifecycle yüzeyinden geçmelidir.

## MBR3.3 Representations pipeline

İncelenen alanlar:

- src/metabase/agent_lib/representations.clj
- src/metabase/agent_lib/representations/repair.clj
- src/metabase/agent_lib/representations/resolve.clj
- src/metabase/mcp/v2/queries.clj

Observed pipeline:

    portable/agent query
    → structural validation
    → repair
    → portable FK/content resolution
    → MBQL normalization
    → field/metric/measure type annotation
    → temporal literal validation
    → runnable/editor gates
    → canonical MBQL 5

Bu Dima açısından çok değerlidir.

Dima StandardProjection doğrudan raw SQL’ye çevrilmeyecektir.

Hedef:

    StandardProjection
    → Dima MetabaseCompiler
    → portable bounded query representation
    → Metabase validate/repair/resolve
    → canonical MBQL
    → Query Processor

Bu sayede Metabase’in query-repair kabiliyeti alınır fakat semantic authority Metabase agentına verilmez.

## MBR3.4 Query handles

İncelenen alan:

- src/metabase/mcp/v2/queries.clj

Query handle davranışı:

- query immutable-ish reference olarak mint edilir
- handle user/session’a bağlanır
- handle yeniden okunduğunda permission guard tekrar çalışır
- native/MBQL ayrımı korunur
- expired/missing handle fail-closed olur
- parameter-bound query save edilirken filtre düşme riski varsa save reddedilir

Dima için ders:

AcceptedStandardAuthority ve QueryContract arasında sealed-query identity kurulurken Metabase query handle benzeri mekanizma kullanılabilir.

Fakat Dima kendi authority_id ve projection_hash alanlarını korur.

## MBR3.5 Metrics / Measures / Dimensions

İncelenen alanlar:

- src/metabase/measures/models/measure.clj
- src/metabase/measures/schema.clj
- src/metabase/metrics/core.clj
- src/metabase/metrics/dimension.clj
- src/metabase/lib_metric/core.cljc

Önemli gözlemler:

- Measure tek aggregation expression içeren reusable semantic macro’dur.
- Metric/Measure dimension setleri persisted edilebilir.
- Dimension UUID tabanlı kimlik taşır.
- Mapping target değişse bile curated dimension identity korunabilir.
- Orphaned dimension state vardır.
- FK-reachable dimensions hesaplanabilir.
- default temporal unit gibi semantic metadata taşınabilir.
- dimensions query değişikliklerinden sonra reconcile edilir.

Bu Wren’den gelen measure/dimension semantics’i taşımak için güçlü substrate sağlar.

Ancak Wren cube ve relationship semantics birebir Metabase Measure/Metric modeli değildir. Bu nedenle Dima Canonical Semantic Specification zorunludur.

## MBR3.6 Entity retrieval + AI context

İncelenen alanlar:

- src/metabase/entity_retrieval/*
- enterprise/backend/src/metabase_enterprise/entity_retrieval/*
- src/metabase/osi/ai_context/api.clj
- src/metabase/osi/models/osi_ai_context.clj
- src/metabase/metabot/tools/entity_retrieval.clj

Metabase OSI ai_context şu tür alanları saklayabilir:

- instructions
- synonyms
- examples

Entity retrieval index bu curated metadata’yı semantic retrieval için kullanabilir.

Dima açısından:

- synonym/example/instruction bilgisi Metabase retrieval’i zenginleştirebilir
- retrieval candidate discovery olarak kullanılabilir
- retrieval score hiçbir zaman canonical truth değildir
- Dima SemanticBindingGate authority sahibi kalır

## MBR3.7 Glossary

İncelenen alan:

- src/metabase/glossary/*

Glossary business term definition için faydalıdır fakat Dima semantic authority yerine geçmez.

Dima semantic spec’ten glossary projection üretilebilir.

## MBR3.8 Query permissions ve user lens

İncelenen alanlar:

- src/metabase/query_permissions/*
- src/metabase/query_processor/*
- enterprise sandbox middleware
- database routing
- field value permission paths

Metabase Query Processor yalnız “SQL çalıştıran” bir motor değildir.

Execution context içine:

- data permissions
- sandboxing
- impersonation
- database routing
- source-card permission
- user-specific metadata

gibi katmanlar girebilir.

Bu nedenle Dima’nın primary data execution path’ini Metabase QP üzerinden geçirmek güvenlik ve ürün olgunluğu açısından anlamlıdır.

## MBR3.9 Cached result security

İncelenen alan:

- src/metabase/queries/cached_result.clj

Metabase cached result sadece creator’ın ürettiği blob’u herkese döndürmez.

Viewer için tekrar:

- underlying query permission
- sandbox/impersonation/routing lens compatibility

kontrol edilir.

Bu Dima EvidenceArtifact tasarımı için çok önemli bir referanstır.

Dima şu hatayı yapmamalıdır:

    “bir kullanıcı sonucu üretti, artifact artık global olarak okunabilir”

Evidence visibility her read sırasında viewer lens ile doğrulanmalıdır veya evidence tenant/principal scope’una immutable bağlanmalıdır.

## MBR3.10 Field values ve indexing

İncelenen alanlar:

- src/metabase/parameters/field_values.clj
- src/metabase/indexed_entities/models/model_index.clj
- src/metabase/indexed_entities/task/index_values.clj

Metabase:

- field values cache
- sandbox-aware values
- impersonation-aware values
- linked filter constraints
- database-routing-aware cache key
- indexed entity values
- scheduled refresh
- overflow states

gibi ürünleşmiş mekanizmalar içerir.

Dima’nın entity/value resolution için sıfırdan value-index servisi yazması gerekmeyebilir.

Fakat sensitive-value exact-only ve Dima-specific semantic policies ayrıca korunacaktır.

## MBR3.11 Explorations

İncelenen alanlar:

- src/metabase/explorations/*
- query_plan/planner.clj
- query_plan/mechanical.clj
- query_plan/variants.clj
- query_plan/context.clj
- runner.clj
- derived_perms.clj
- interestingness.clj
- contextual_interestingness/*

Bu alan Dima için özellikle değerlidir.

Metabase Explorations:

- metric/dimension candidate catalog
- dimension applicability
- cardinality-aware chart variants
- background query plan
- idempotent execution
- cancellation
- persisted results
- query-level errors
- statistical interestingness
- contextual LLM interestingness
- permission/lens aware derived-result visibility
- exploration thread persistence

gibi primitive’ler içerir.

Fakat bugün planner esasen mechanical’dır ve Dima Research Manager’ın evidence-driven reasoning, UserObligationLedger, HypothesisLedger ve epistemic gates ihtiyaçlarının yerine geçmez.

Sonuç:

Explorations doğrudan Dima Research yerine kullanılmayacak.

Reuse adayları:

- background execution patterns
- persisted result lifecycle
- chart variants
- interestingness
- cancellation/idempotency
- lens-safe derived data access

## MBR3.12 BI workspace

Metabase ayrıca şu olgun katmanlara sahiptir:

- dashboards
- collections
- saved questions
- models
- metrics
- measures
- revisions
- content verification
- comments/documents
- notifications
- embedding
- transforms
- remote sync
- data studio

Dima’nın bunları yeniden yapması stratejik olarak gereksizdir.

---

# MBR4 — METABASE’İN DOĞRUDAN ALAMAYACAĞI DIMA ÖZGÜNLÜKLERİ

Aşağıdaki primitive’ler Dima’ya aittir ve Metabase ile değiştirilmez:

- AcceptedStandardAuthority
- AcceptedTurnContract
- UserObligationLedger
- RequirementLedger
- ResearchDirective
- SemanticBindingGate
- Dima SemanticHandle
- Dima Canonical Semantic Specification
- QueryContract
- EvidenceArtifact
- Finding
- HypothesisLedger
- epistemic status
- CompletionGate
- ReportClaimGate
- DecisionBrief
- DecisionRecord
- conversation TopicFrame / repair semantics
- model-role policy
- failure triage receipts
- model capability floor discipline
- STOP-THE-LINE rules

Metabase bunların bazılarının yakın analoglarına sahip olabilir.

Yakın analog olması owner değişikliği anlamına gelmez.

---

# MBR5 — WREN SEMANTİĞİNİ KAYIPSIZ KORUMA STRATEJİSİ

En büyük risk Wren’i çıkarırken sektör/müşteri business semantics’ini kaybetmektir.

Bu nedenle Wren → Metabase direct migration yapılmayacaktır.

Araya Dima-owned canonical semantic source konacaktır.

Adı:

Dima Canonical Semantic Specification
kısaltma: DCSS

DCSS şu kavramları taşır:

- subject/domain
- canonical metric
- formula
- aggregation
- additivity
- unit
- grain
- lower_is_better
- default time dimension
- allowed temporal grain
- canonical dimension
- categorical/value policy
- relationship
- relationship cardinality
- join eligibility
- cross-domain path
- semantic aliases
- Turkish sector terminology
- entity/value handling policy
- sensitivity
- visibility
- NL exposure flag
- business definition
- provenance
- version
- tenant/sector ownership
- derived metric dependencies
- capability requirements

Wren MDL/pack bu DCSS için migration source olacaktır.

Metabase DCSS’in execution projection’ı olacaktır.

Bu ayrım kritik:

    DCSS = business truth
    Metabase objects = runtime projection

Böylece Metabase’te bir object silinse, yeniden ID alsa veya internal schema değişse bile Dima’nın canonical business kimliği kaybolmaz.

---

# MBR6 — WREN → DCSS → METABASE EŞLEME MATRİSİ

Wren Model:
- DCSS subject/model
- Metabase table/model veya governed source query

Wren Cube:
- DCSS analytical subject
- Metabase metric/model group + Dima capability metadata
- birebir “cube object” zorlanmaz

Wren Measure:
- DCSS metric
- Metabase Measure veya Metric aggregation
- formula parity testi zorunlu

Wren Dimension:
- DCSS dimension
- Metabase persisted dimension UUID
- mapping parity testi zorunlu

Wren TimeDimension:
- DCSS temporal dimension
- Metabase dimension + default temporal unit
- date engine semantiği Dima’da kalır

Wren Relationship:
- DCSS relationship edge
- Metabase metadata/join path veya governed view
- Dima CrossDomainJoinGate owner kalır

Wren synonym/label:
- DCSS aliases/display labels
- Metabase AI Context synonyms / descriptions / glossary projection
- Dima retriever/binder yine authority

Wren always-filter/security:
- DCSS security metadata
- Metabase permission/sandbox/routing layer
- parity test olmadan taşınmış sayılmaz

Wren custom wrapper capability:
- DCSS specialized operator
- Metabase MBQL if representable
- değilse Dima specialized analytics tool

---

# MBR7 — HEDEF ÜRÜN MİMARİSİ

Nihai logical architecture:

    USER
      ↓
    Dima Conversation Runtime
      ↓
    Language / Manager cognition
      ↓
    finite typed draft
      ↓
    SemanticCatalogRetriever
      ↓
    SemanticBindingGate
      ↓
    exactly one accepted authority
      ├───────────────────────┐
      │                       │
    STANDARD               RESEARCH
      │                       │
    StandardProjection      UserObligationLedger
      │                    + ResearchDirective
      │                       │
      │                    Research Manager
      │                       │
      └──────────────┬────────┘
                     ↓
              Dima Analytics Port
                     ↓
             MetabaseCompiler
                     ↓
         portable bounded query
                     ↓
          Metabase representation
       validate → repair → resolve
                     ↓
              canonical MBQL
                     ↓
          Metabase Query Processor
         permissions / lens / routing
                     ↓
                  DATABASE
                     ↓
          Metabase execution result
                     ↓
              Dima QueryContract
                     ↓
              EvidenceArtifact
                     ↓
       Finding / Hypothesis / Report
                     ↓
             Decision Intelligence

Metabase dashboards/workspace paralel product surface olabilir ancak Dima answer authority değildir.

---

# MBR8 — STANDARD PATH

Standard path basit veya tek analitik hedefli sorular içindir.

Örnek:

“Bu ay net geliri bölgelere göre göster.”

Akış:

1. Dima language runtime typed obligation üretir.
2. Semantic retriever candidate set üretir.
3. BindingGate canonical metric ve dimension’ı doğrular.
4. StandardProjection oluşur.
5. AcceptedStandardAuthority projection hash ile seal edilir.
6. MetabaseCompiler portable query üretir.
7. Metabase validate/repair/resolve canonical MBQL’ye dönüştürür.
8. permission-aware Query Processor çalıştırır.
9. Dima ResultValidator semantics/grain/result shape doğrular.
10. QueryContract seal edilir.
11. EvidenceArtifact üretilir.
12. cevap/chart döner.

Metabase Metabot burada raw kullanıcı mesajını tekrar parse etmez.

Bu kural ikinci semantic owner oluşmasını engeller.

---

# MBR9 — RESEARCH PATH

Kompleks istek:

“Son 12 ay ürünleri karşılaştır, makineler ve personellerle ilişkisini analiz et, satış performansını yorumla ve raporla.”

Akış:

1. AcceptedTurnContract user MUST’ları dondurur.
2. UserObligationLedger oluşturulur.
3. Research Manager typed task üretir.
4. Her analytics task yine aynı MetabaseAnalyticsPort üzerinden çalışır.
5. Her query sonucu QueryContract + EvidenceArtifact olur.
6. Manager evidence görür.
7. Derived task açabilir.
8. User MUST değişmez.
9. HypothesisLedger destek/çürütme kanıtlarını taşır.
10. CompletionGate tüm MUST’ların VERIFIED/BLOCKED/LIMITED olmasını ister.
11. ReportSynthesizer yalnız evidence/finding üzerinden yazar.
12. ReportClaimGate evidence’sız numeric veya causal claim’i reddeder.

Metabase burada execution ve analytical workspace sağlar.

Research cognition Dima’da kalır.

---

# MBR10 — METABASE AGENTIC KABİLİYETLERİNİ NASIL KULLANACAĞIZ?

Doğrudan Metabot’u Dima brain’i yapmayacağız.

Üç katman vardır:

1. Metabase representations/query repair
   Primary reuse. Dima query lifecycle içine alınabilir.

2. Agent API / MCP typed execution primitives
   Dima MetabaseAnalyticsPort adapter’ının backend’i olabilir.

3. Metabot conversational agent
   Dima production semantic authority için kullanılmaz.
   BI workspace içinde yardımcı user feature olarak ayrı sunulabilir.

Neden?

Çünkü Dima:
- exactly-one accepted authority
- immutable user obligations
- evidence
- epistemic status
- research completion
- decision record

gibi daha güçlü ürün sözleşmelerine sahiptir.

Metabot’u ikinci brain yapmak bu sözleşmeleri zayıflatır.

---

# MBR11 — QUERY REPRESENTATION KARARI

Dima raw SQL üretmeyecektir.

Primary target:

StandardProjection → portable MBQL-compatible representation.

Compiler özellikleri:

- deterministic
- typed
- canonical semantic refs input
- no raw user text interpretation
- no model-specific branches
- unsupported construct fail-closed
- context_version aware
- tenant/principal aware
- projection_hash preserved

Metabase repair yalnız representation hatasını düzeltebilir.

Şunları yapamaz:

- metric değiştirmek
- dimension değiştirmek
- user obligation eklemek
- semantic candidate seçmek
- time intent yeniden yorumlamak
- research scope değiştirmek

Repair sonrası semantic-equivalence check zorunludur.

Bu çok önemli yeni gate:

MetabaseRepairEquivalenceGate.

Repair edilmiş MBQL’nin semantic projection fingerprint’i AcceptedStandardAuthority ile uyuşmuyorsa execution reddedilir.

---

# MBR12 — PRINCIPAL / TENANT MİMARİSİ

Dima auth primary kalır.

Her Dima request:

- tenant_id
- principal_user_id
- roles
- allowed data domains
- context_version
- semantic_version

taşır.

Metabase tarafında production için global superuser token ile user query çalıştırmak yasaktır.

Hedef:

Dima principal → Metabase principal/session mapping.

Minimum production gate:

- tenant A principal tenant B database/collection göremez
- tenant A query tenant B DB’ye route edilemez
- cached/stored result başka lens’te okunamaz
- permission değişince stale query handle/evidence read tekrar doğrulanır
- Dima artifact visibility ile Metabase lens policy çelişirse deny

Pilot öncesi principal parity testi zorunludur.

---

# MBR13 — EVIDENCE VE RESULT PERSISTENCE

Metabase stored/cached results faydalıdır ancak Dima evidence truth yalnız Metabase cache’e bırakılamaz.

Neden:

- cache retention değişebilir
- GC olabilir
- user lens değişebilir
- report audit daha uzun ömür isteyebilir
- Dima decision records Metabase lifecycle’dan bağımsız olmalıdır

EvidenceArtifact en az:

- artifact_id
- authority_id
- task_id
- obligation_ids
- query_contract_refs
- metabase_query_handle/ref
- query_hash
- projection_hash
- semantic_version
- principal/lens fingerprint
- result schema hash
- result content hash
- row_count
- bounded sample
- storage_ref
- created_at
- limitations

taşır.

Final report/decision için gerekli evidence snapshotları Dima-controlled durable storage’a alınabilir.

Her read principal-aware olmalıdır.

---

# MBR14 — QUERY CONTRACT

Metabase query handle QueryContract yerine geçmez.

Dima QueryContract şunları seal eder:

- accepted authority
- StandardProjection
- semantic refs
- semantic version
- generated portable query
- repaired canonical MBQL fingerprint
- database id
- principal/lens
- execution timestamp
- result hash
- planner/compiler version
- Metabase version
- context version

Bu audit chain nihai ürünün önemli farklılaştırıcısıdır.

---

# MBR15 — CROSS-DOMAIN VE RELATIONSHIP

Wren’de güçlü olan alanlardan biri explicit semantic relationships’tir.

Metabase’a geçişte en tehlikeli hata:

“Metabase implicit join yapabiliyor, o halde relationship problemimiz çözüldü.”

Hayır.

DB FK path’i business-valid analytical relationship ile aynı şey değildir.

Dima DCSS Relationship Registry:

- source subject
- target subject
- join path
- cardinality
- grain
- time alignment
- allowed metrics
- additive/non-additive constraints
- many-to-many risk
- bridge rule
- null policy
- evidence requirement

taşır.

CrossDomainJoinGate bu registry’yi kullanır.

Metabase QP yalnız approved relationship plan’ını execute eder.

No-path join fail-closed kalır.

---

# MBR16 — TEMPORAL SEMANTICS

Metabase temporal filtering güçlüdür fakat kullanıcı dilindeki temporal meaning owner değildir.

Dima:

language → TypedTemporalIntent.

Deterministic TemporalBindingEngine:

TypedTemporalIntent + timezone + now + business calendar → exact date range.

Metabase yalnız exact temporal constraint’ı execute eder.

“geçen ay”, “önceki çeyrek”, “aynı dönem geçen yıl” gibi business semantics Metabase agentına devredilmez.

---

# MBR17 — VALUE / ENTITY RESOLUTION

Metabase FieldValues ve IndexedEntities altyapısı ciddi reuse fırsatıdır.

Target:

- Dima canonical dimension bilinir.
- allowed value candidates Metabase value-index API’den alınabilir.
- candidate set Dima binder’a verilir.
- sensitive dimensions exact-only kalabilir.
- retrieval score truth olmaz.
- high-cardinality value search bounded olur.
- sandbox/lens aware value search zorunludur.

Bu sayede Dima’nın custom tenant-value indexing yükü azalabilir.

---

# MBR18 — BI WORKSPACE

Nihai Dima’da kullanıcı iki yüzey kullanabilir:

1. Dima intelligence surface
   conversation, research, report, decision

2. Metabase workspace
   dashboards, saved questions, charts, collections, exploration

Bu iki yüzey aynı analytics substrate’a bağlanır.

Ancak semantic drift engellenmelidir.

Dima tarafından üretilen canonical analyses save edilirken:

- authority_ref
- query_contract_ref
- semantic_version
- Dima provenance metadata

saklanmalıdır.

Metabase kullanıcılarının elle oluşturduğu BI content Dima evidence truth’a otomatik terfi etmez.

Verified/curated promotion flow gerekir.

---

# MBR19 — METABASE EXPLORATIONS’TAN ALINACAKLAR

Explorations doğrudan Research Manager yerine geçmez.

Reuse candidates:

- queue/idempotency pattern
- thread cancellation
- persisted query rows
- stored result lifecycle
- chart variants
- statistical interestingness
- contextual interestingness
- data-access lens stamping
- derived-result read gate
- query status model

Dima research’e taşınmaması gerekenler:

- mechanical planner’ın research authority olması
- chart interestingness = business finding varsayımı
- exploration candidate score = semantic truth
- Metabase thread = Dima accepted contract

---

# MBR20 — FAILURE SEMANTICS

Bütün external/substrate failures typed outcome olmalıdır.

Minimum taxonomy:

- MODEL_COGNITION
- CONTRACT_ARCHITECTURE
- RESOLVER_TRUTH
- TEMPORAL_BINDING
- METABASE_QUERY_REPRESENTATION
- METABASE_PERMISSION
- METABASE_PROVIDER
- METABASE_METADATA_STALE
- DATABASE
- EVAL_ORACLE
- TRANSPORT_PROVIDER
- EVIDENCE_PERSISTENCE
- TENANT_SECURITY
- UNSUPPORTED_CAPABILITY

Infra fail semantic fail sayılmaz.

Metabase 500, timeout veya DB down nedeniyle user intent başarısız sayılmaz.

Failure receipt disiplini korunur.

---

# MBR21 — STOP-THE-LINE KURALLARI

Aşağıdakiler görülürse geliştirme durur:

- ikinci semantic owner
- Metabot raw user prompt’u authoritative şekilde yeniden parse ediyor
- Metabase repair semantic target değiştiriyor
- accepted projection ile executed MBQL semantic fingerprint uyuşmuyor
- raw SQL Standard/Research hot path’e giriyor
- no-path cross-domain join execute ediliyor
- global superuser token user query’lerinde kullanılıyor
- tenant crossing
- stale semantic compile silently accepted
- cached result incompatible lens’e gösteriliyor
- USER_MUST silent loss
- evidence’sız numeric claim
- unsupported causal claim
- Wren ve Metabase iki eşit production truth engine haline geliyor
- provider/model name domain business logic içine giriyor
- testcase-derived prompt/regex/heuristic ekleniyor

---

# MBR22 — METABASE VERSIONING VE ADAPTER SINIRI

Metabase internal Clojure namespace’lerine doğrudan runtime dependency yok.

Dima yalnız:

- documented REST/Agent API
- supported auth/session
- supported query/metadata endpoints

üzerinden konuşur.

Metabase version pinned olmalıdır.

Her upgrade:

- adapter contract test
- semantic projection parity
- permission parity
- query-handle behavior
- cached result visibility
- migration smoke
- rollback readiness

gerektirir.

Metabase source audit yapılabilir fakat Dima code internal namespace’e bind edilmez.

---

# MBR23 — OPERASYON TOPOLOJİSİ

Pilot hedefi:

    Dima API / workers
       ↓ private network
    self-hosted pinned Metabase
       ↓
    Metabase application PostgreSQL
       ↓
    tenant analytical databases

Gerekli operasyonlar:

- Metabase app DB backup
- DB migration strategy
- health probes
- logs/metrics
- version pin
- rolling/blue-green upgrade
- secret management
- tenant DB connection rotation
- queue/result storage monitoring
- query timeout policy
- request correlation id
- Dima authority id → Metabase request trace mapping

Metabase aynı Python process içine library olarak gömülmez.

---

# MBR24 — PERFORMANS VE MALİYET

Optimization hedefi sadece LLM token maliyeti değildir.

Ölçümler:

- p50/p95 end-to-end
- Dima model calls
- semantic linker calls
- Metabase API calls
- QP execution time
- DB time
- result serialization time
- query repair count
- query retry count
- cache hit rate
- evidence persistence time
- cost per verified success
- unnecessary research admission
- unnecessary manager turns

Standard path mümkün olduğunca kısa kalır.

Research path bounded budget kullanır.

---

# MBR25 — OBSERVABILITY

Her request tek trace altında şu eventleri üretmeli:

- request_received
- model_attempt
- candidate_retrieval
- semantic_binding
- authority_sealed
- projection_compiled
- metabase_validate
- metabase_repair
- metabase_resolve
- permission_checked
- query_executed
- result_validated
- query_contract_sealed
- evidence_persisted
- research_replan
- completion_gate
- report_claim_gate
- response_sent

Her event:

- tenant
- principal
- request_id
- authority_id
- context_version
- semantic_version
- Metabase version
- model role
- latency
- outcome

taşır.

PII payload loglanmaz.

---

# MBR26 — GÖÇ STRATEJİSİ

Big-bang yasaktır.

Aşamalar:

1. Wren path frozen reference.
2. DCSS çıkarılır.
3. DCSS Metabase projection üretilir.
4. same-query shadow parity.
5. Standard path Metabase shadow.
6. selected standard canary.
7. Research tool substrate Metabase shadow.
8. evidence parity.
9. security parity.
10. BI workspace activation.
11. Wren read-only oracle.
12. Wren runtime removal gate.
13. final production cutover.

Wren ancak aşağıdakiler sağlanınca runtime’dan çıkabilir:

- metric parity = 100% certified set
- dimension mapping parity
- temporal parity
- relationship/grain parity
- security parity
- query result parity within defined tolerances
- no silent unsupported capability
- rollback tested

---

# MBR27 — KAYIPSIZLIK KANIT PAKETİ

Her migrated semantic entity için MigrationReceipt:

- wren_source_ref
- dcss_canonical_id
- metabase_entity_refs
- formula_hash
- dimension mapping
- relationship refs
- time dimension
- aliases
- unit
- grain
- security policy
- test cases
- parity result
- status

Status:

- DISCOVERED
- MAPPED
- COMPILED
- PARITY_GREEN
- BLOCKED
- DEPRECATED

PARITY_GREEN olmayan semantic production primary olamaz.

---

# MBR28 — KABİLİYET MATRİSİ

Standard aggregation:
Metabase primary candidate — strong.

Breakdown:
Metabase strong.

Ranking/top-N:
Metabase strong.

Comparison:
Metabase execution strong; Dima temporal/comparison intent owner.

Saved analytics:
Metabase strong.

Dashboard/chart:
Metabase strong.

Permissions:
Metabase strong, principal mapping certification required.

Entity/value indexing:
Metabase useful, Dima binding owner.

Sector-specific semantic packs:
Dima DCSS inherits Wren strength.

Cross-domain governed relationships:
Dima remains owner.

Research manager:
Dima owner.

Root cause:
Dima owner.

Evidence:
Dima owner, Metabase result substrate.

Report:
Dima owner.

Decision intelligence:
Dima owner.

---

# MBR29 — KULLANICI SENARYOSU SİMÜLASYONLARI

## Senaryo A — Basit Standard

User:
“Bu ay net geliri bölgelere göre göster.”

Expected:

- typed metric = net_gelir
- dimension = bolge
- period = current month
- one AcceptedStandardAuthority
- no Research
- Metabase query canonical
- permission scoped
- one QueryContract
- one EvidenceArtifact
- chart + concise answer

Forbidden:
Metabot reinterpretation, raw SQL, hidden fallback.

## Senaryo B — Ambiguity

User:
“Siyahın satışını göster.”

Candidate meanings:
- color=Siyah
- customer=Siyah Tekstil
- product series=Siyah

Expected:
CLARIFY.
Query count = 0.
Accepted authority = 0.

## Senaryo C — Research

User:
“Son 12 ay ürünleri karşılaştır, makineler ve personellerle ilişkisini analiz et, satış performansını yorumla ve raporla.”

Expected:
4 analytical USER_MUST + report deliverable.
Multiple evidence queries.
Result-aware replan.
No silent dropped obligation.
CompletionGate before report.

## Senaryo D — Permission change

Query built under user lens A.
Permission revoked before cached read.

Expected:
read denied or revalidated under new lens.
No stale evidence disclosure.

## Senaryo E — Metabase repair changes semantics

Dima asks revenue by region.
Repair changes metric ref to gross_sales.

Expected:
MetabaseRepairEquivalenceGate rejects.
No execution.

## Senaryo F — DB/Metabase unavailable

Expected:
typed infrastructure outcome.
No semantic failure count.
No fallback raw SQL.
Retry policy bounded.

## Senaryo G — stale semantic compile

DCSS v44 but Metabase projection still v43.

Expected:
context/version gate blocks query.
No silent execution.

## Senaryo H — cross-domain no path

User asks product vs employee relation but DCSS has no approved relationship.

Expected:
BLOCKED/UNSUPPORTED.
No inferred join.

---

# MBR30 — TEST STRATEJİSİ

Normal loop:

code
→ 3–15 sec focused provider-free
→ vertical continue

Milestone:

provider-free family
→ workers=1 real live
→ small canary
→ sentinel

Final:

20–25 integrated rehearsal
→ final engineering freeze
→ DEV80 once
→ Validation50 no tuning
→ external Hidden50 no tuning
→ certification seal

Metabase-specific test families:

- adapter contract
- MBQL compile
- repair equivalence
- query handle identity
- permission parity
- lens parity
- cached result gate
- semantic projection migration
- Wren-vs-Metabase result parity
- field value visibility
- metadata version drift
- Metabase upgrade compatibility
- tenant isolation
- restart/idempotency
- cancellation
- timeout
- high cardinality
- cross-domain gate

---

# MBR31 — NİHAİ ÜRÜN SINIRI

Dima’nın değeri “Metabase’a chat eklemek” değildir.

Nihai ürün:

- business-semantic understanding
- evidence-backed research
- root-cause investigation
- hypothesis management
- report generation
- decision support
- workflow/action proposals
- auditability

Metabase’ın değeri:

- reliable analytics substrate
- permissions
- query engine
- BI objects
- result lifecycle
- workspace

Bu iki katman birbirine karıştırılmadığında ürün hem daha hızlı hem daha sağlam gelişir.

---

# MBR32 — BU DALDA OTORİTE KURALI

Bu branch için:

1. Bu rapor mimari gerekçe otoritesidir.
2. DIMA_METABASE_NIHAI_UYGULAMA_YOL_HARITASI.md uygulama sırası otoritesidir.
3. Önceki Wren-temelli nihai rapor/yol haritası migration/reference source’dur.
4. Living status ayrıca oluşturulabilir fakat bu iki mühürlü belge sessizce değiştirilmez.
5. Yeni bulgu mimariyi değiştirecekse STOP/CONSULT gerekir.
6. Failure sonrası case patch yapılmaz.
7. Her gate exact SHA ile kayıt altına alınır.

Tek cümlelik prensip:

“Dima’nın zekâsını ve semantic hakikatini koru; Metabase’in olgun analytics altyapısını kullan; hiçbir katmanı diğerinin authority alanına sokma.”


---

# MBR33 — RİSK REGISTER

Bu bölüm teknik fizibilitenin release-blocking risk envanteridir.

## R1 — Wren cube semantics’in sessiz kaybı

Severity: P0.

Risk:
Metabase objects Wren Cube/MDL kavramlarının tümünü birebir taşımayabilir.

Mitigation:
DCSS canonical source.
MigrationReceipt.
Wren parity oracle.
No direct Wren→Metabase ad-hoc migration.

Gate:
100% semantic inventory accounted.

## R2 — Metric formula drift

Severity: P0.

Risk:
Wren measure ile Metabase Measure/Metric aynı isimde fakat farklı aggregation/formula üretir.

Mitigation:
formula_hash + canonical result parity.

Gate:
Certified metric set = 100% parity.

## R3 — Grain duplication

Severity: P0.

Risk:
Join sonrası measure çoğalır.

Mitigation:
DCSS grain/additivity + CrossDomainJoinGate.

Gate:
dedicated many-to-many / one-to-many corpus.

## R4 — Metabase repair semantic mutation

Severity: P0.

Risk:
Representation repair teknik hatayı düzeltirken metric/filter/time meaning değiştirir.

Mitigation:
MetabaseRepairEquivalenceGate.

Gate:
semantic fingerprint exact match.

## R5 — Metabot second semantic owner

Severity: P0.

Risk:
Dima accepted authority sonrası Metabot raw prompt’tan başka query kurar.

Mitigation:
Metabot authoritative path dışında.
Only typed MetabaseAnalyticsPort.

Gate:
architecture import/call graph test.

## R6 — Numeric Metabase IDs canonical sanılır

Severity: P0/P1.

Risk:
Environment migration sonrası ID değişir.

Mitigation:
Dima canonical ID + portable entity_id/UUID mapping.

Gate:
fresh-instance recompile test.

## R7 — Semantic index lag

Severity: P1.

Risk:
AI Context/synonym update ile retrieval index eşzamanlı değil.

Mitigation:
semantic_version + reconcile receipt + activation barrier.

Gate:
new version ACTIVE olmadan index compile/reconcile complete.

## R8 — Warehouse schema drift

Severity: P0/P1.

Risk:
Field removed/renamed but accepted semantic remains active.

Mitigation:
metadata_version and orphan detection.

Gate:
stale mapping query blocked.

## R9 — Cached result data leak

Severity: P0.

Risk:
Creator lens altında üretilen result başka viewer’a gösterilir.

Mitigation:
Metabase lens token + Dima evidence access gate.

Gate:
permission revoke / sandbox change / tenant crossing tests.

## R10 — Dima evidence Metabase GC’ye bağımlı

Severity: P1.

Risk:
Report audit sırasında Metabase cache yok.

Mitigation:
durable Dima evidence snapshot for promoted evidence.

Gate:
cache deletion simulation.

## R11 — Global service account privilege

Severity: P0.

Risk:
Dima backend superuser olarak query çalıştırır.

Mitigation:
principal mapping and least privilege.

Gate:
superuser execution hot path = 0.

## R12 — Query handle authority laundering

Severity: P0.

Risk:
Başka projection/query aynı handle veya authority ile execute edilir.

Mitigation:
authority_id + projection_hash + canonical query hash bind.

Gate:
tamper tests.

## R13 — Native SQL escape

Severity: P0.

Risk:
Manager veya Metabase tool raw SQL path açar.

Mitigation:
native SQL disabled in Dima hot path.
Agent authored SQL kill switch.

Gate:
architecture and endpoint tests.

## R14 — Permission mismatch between Dima and Metabase

Severity: P0.

Risk:
Dima “allowed” der, Metabase “denied” veya tersi; daha kötüsü Dima evidence gösterir.

Mitigation:
deny-wins.
Metabase execution permission is mandatory.
Dima artifact gate additionally enforced.

Gate:
principal parity matrix.

## R15 — Metabase upgrade breaks query dialect

Severity: P1.

Mitigation:
pinned version + upgrade protocol + adapter contract tests.

## R16 — Internal Metabase source coupling

Severity: P1.

Risk:
Dima internal Clojure namespace davranışına runtime bağımlı hale gelir.

Mitigation:
HTTP/public supported contract only.

## R17 — High cardinality explosion

Severity: P1/P2.

Mitigation:
bounded result limits, field-value caps, top-N policy, research budgets.

## R18 — Metadata prompt injection

Severity: P0/P1.

Risk:
Table/description/AI context içinde instruction-like malicious text.

Mitigation:
metadata treated as untrusted data.
System tool contract outranks metadata.
No metadata can mint authority.

## R19 — Semantic alias poisoning

Severity: P0.

Mitigation:
DCSS change review + source provenance + tenant scope.

## R20 — Research result fanout cost

Severity: P2/P3.

Mitigation:
task budget, query budget, interestingness pruning, no-progress fingerprint.

## R21 — Cross-domain temporal misalignment

Severity: P0/P1.

Mitigation:
RelationshipEdge time-alignment policy.

## R22 — Metric dimension orphaning

Severity: P1.

Mitigation:
Metabase orphaned dimension status + DCSS compile verification.

## R23 — Metabase application DB corruption/outage

Severity: P1 operational.

Mitigation:
production PostgreSQL, backup, restore rehearsal, HA plan.

## R24 — Duplicate execution on retry

Severity: P1.

Mitigation:
execution idempotency key and persisted task state.

## R25 — Two production truth engines

Severity: P0 architecture.

Mitigation:
shadow-only challenger.
One primary substrate at a time.
Explicit operator rollback only.

---

# MBR34 — METABASE CAPABILITY ADOPTION MATRIX

Capability: Generic agent loop
Source: metabot/agent/core.clj, profiles.clj
Decision: PATTERN ADOPT
Reason: reusable bounded loop; do not copy code.

Capability: Agent API
Source: agent_api/*
Decision: ADAPTER TARGET
Reason: typed agent/query surface.

Capability: Representations validation/repair/resolve
Source: agent_lib/representations/*
Decision: PRIMARY REUSE
Reason: mature query lifecycle.

Capability: Query handles
Source: mcp/v2/queries.clj
Decision: REUSE CONCEPT / API WHERE AVAILABLE
Reason: query identity + recheck permissions.

Capability: Measures/Metrics/Dimensions
Source: measures/*, metrics/*, lib_metric/*
Decision: RUNTIME PROJECTION TARGET
Reason: semantic execution substrate; not canonical Dima truth.

Capability: AI Context
Source: osi/ai_context/*
Decision: SECONDARY RETRIEVAL PROJECTION
Reason: synonyms/examples/instructions; not authority.

Capability: Entity retrieval
Source: entity_retrieval/*
Decision: CANDIDATE DISCOVERY
Reason: retrieval only.

Capability: Field values
Source: parameters/field_values.clj
Decision: REUSE
Reason: permission-aware value discovery.

Capability: Indexed entities
Source: indexed_entities/*
Decision: EVALUATE / REUSE
Reason: high-cardinality entity-value search.

Capability: Query Processor
Source: query_processor/*
Decision: PRIMARY EXECUTION ENGINE
Reason: permissions, drivers, preprocessing, execution.

Capability: Query permissions
Source: query_permissions/*
Decision: PRIMARY EXECUTION GUARD
Reason: required but Dima tenant/evidence guard remains.

Capability: Cached result lens
Source: queries/cached_result.clj
Decision: PATTERN + REUSE
Reason: prevents derived-data leaks.

Capability: Explorations
Source: explorations/*
Decision: SELECTIVE REUSE
Reason: persistence/queue/chart/interestingness; not Dima research authority.

Capability: Contextual interestingness
Source: contextual_interestingness/*
Decision: OPTIONAL SIGNAL
Reason: ranking/surfacing only; never finding truth.

Capability: Dashboards / collections / charts
Decision: DIRECT PRODUCT REUSE.

Capability: Revisions / content verification
Decision: REUSE for BI governance.

Capability: Glossary
Decision: PROJECTION from DCSS.

Capability: Remote sync
Decision: EVALUATE for semantic/BI promotion workflow.

Capability: Raw SQL authoring
Decision: DISABLED in Dima Standard/Research hot path.

---

# MBR35 — METABASE SEMANTIC MODELİNİN WREN’DEN FARKI

Wren’in semantic model yaklaşımı “business model first” karakterindedir.

Metabase ise query platformu + reusable metric/dimension/content modelini birlikte taşır.

Bu yüzden aşağıdaki yanlış çıkarım yasaktır:

    “Metabase’de Metric var”
    ⇒ “Wren MDL artık gereksiz”

Doğru çıkarım:

    “Metabase Metric/Measure/Dimension runtime execution için yeterince zengin olabilir”
    +
    “Dima business semantics substrate-independent DCSS’te korunmalıdır”

Özellikle DCSS içinde Metabase’in natural olarak taşımadığı veya farklı temsil ettiği alanlar korunur:

- domain/cube grouping
- grain contract
- additivity
- relationship eligibility
- business join constraints
- lower_is_better
- semantic exposure policy
- specialized analytical operators
- sector overlay inheritance
- metric dependency graph
- cross-domain time alignment

Metabase’e sadece representable projection yapılır.

---

# MBR36 — QUERY COMPILATION İÇİN İKİ ALTERNATİF VE KARAR

Alternatif A:
Dima accepted semantics → free-form NL → Metabase Metabot → query.

Red.
Neden:
ikinci semantic owner ve raw prompt reparse.

Alternatif B:
Dima AcceptedStandardAuthority → deterministic StandardProjection → portable query → Metabase representations pipeline.

Selected.

Alternatif C:
Dima StandardProjection → direct raw SQL.

Red.
Neden:
permission/query lifecycle/repair/semantic safety kaybı.

Dolayısıyla target compilation:

    AcceptedStandardAuthority
    → StandardProjection
    → MetabaseProjectionCompiler
    → portable query representation
    → validate
    → repair
    → resolve
    → equivalence
    → Query Processor

---

# MBR37 — OPERATIONAL FEASIBILITY

Ek servis maliyeti gerçektir.

Production minimum:

- Metabase JVM container/service
- PostgreSQL application DB
- backups
- migrations
- monitoring
- secrets
- DB connection pool
- service networking
- pinned image
- rolling upgrade strategy

Fakat bu maliyet karşılığında Dima’nın yeniden yapmak zorunda kalmayacağı platform maliyetleri çok daha büyüktür:

- dashboard engine
- saved query model
- query editor
- visualization workspace
- driver handling
- cached results
- query lifecycle
- permission-aware metadata
- revisions
- BI collections
- field values
- result rendering

Bu nedenle infrastructure TCO artar; product-development TCO belirgin azalır.

Pilot fizibilite metriği yalnız latency değildir.

    engineering LOC avoided
    custom subsystem count removed
    operational components added
    incident surface
    upgrade effort
    p95
    cost per verified success

birlikte ölçülür.

---

# MBR38 — SOURCE REFERENCE INDEX

Metabase pinned source references:

Agent runtime:
- src/metabase/metabot/agent/core.clj
- src/metabase/metabot/agent/profiles.clj
- src/metabase/metabot/agent/memory.clj

Agent API:
- src/metabase/agent_api/api.clj
- src/metabase/agent_api/query_guards.clj
- src/metabase/agent_api/validation.clj
- src/metabase/agent_api/reference.md

Query representation:
- src/metabase/agent_lib/representations.clj
- src/metabase/agent_lib/representations/repair.clj
- src/metabase/agent_lib/representations/resolve.clj
- src/metabase/mcp/v2/queries.clj

Semantic objects:
- src/metabase/measures/models/measure.clj
- src/metabase/metrics/core.clj
- src/metabase/lib_metric/core.cljc
- src/metabase/lib_metric/dimension.cljc

Retrieval/context:
- src/metabase/entity_retrieval/*
- src/metabase/osi/ai_context/*
- src/metabase/glossary/*

Execution/security:
- src/metabase/query_processor/*
- src/metabase/query_permissions/*
- src/metabase/queries/cached_result.clj
- enterprise/backend/src/metabase_enterprise/sandbox/query_processor/middleware/sandboxing.clj

Values:
- src/metabase/parameters/field_values.clj
- src/metabase/indexed_entities/*

Research/workspace:
- src/metabase/explorations/*
- src/metabase/contextual_interestingness/*
- src/metabase/dashboards/*
- src/metabase/collections/*
- src/metabase/revisions/*

Dima reference:
- existing v2 authority/preacceptance/runtime modules
- existing StandardProjection / AcceptedStandardAuthority
- current WrenService / CubePlanner / QueryContract / Evidence
- existing final V2 report and roadmap
- Day6.5 failure triage and Metabase audit artifacts

---

# MBR39 — CONSULTATION GATES

Geliştirici aşağıdaki kararlarda otomatik ilerlemez:

1. DCSS canonical schema değişikliği semantic ownership’i etkiliyorsa.
2. Metabase API yerine internal source coupling öneriliyorsa.
3. Raw SQL hot path isteniyorsa.
4. Metabot cognition Dima Manager’ın yerine geçirilecekse.
5. Wren runtime kaldırılacaksa.
6. Cross-domain relationship owner değişecekse.
7. Principal mapping superuser/service-account shortcut’a dönüyorsa.
8. Evidence storage Metabase cache’e tamamen devredilecekse.
9. Accepted authority contract değişecekse.
10. Final freeze / DEV80 başlatılacaksa.

Bu rapor teknik fizibilite belgesidir. Önceki talebe uygun olarak lisans/hukuk değerlendirmesi bu teknik kararın dışında tutulmuştur; production ticari karar aşamasında ayrıca ele alınabilir.

