# DIMA + METABASE — Nihai Fizibilite, Mimari ve Geçiş Raporu

**Belge rolü:** Metabase tabanlı yeni Dima denemesinin normatif mimari raporu.  
**Amaç:** Wren+Dima V2 denemesinden kazanılan semantic authority, trust-plane, evidence, research ve güvenlik ilkelerini kaybetmeden Metabase’i analytics/BI operating system olarak konumlandırmak ve Dima’yı onun üzerinde nihai decision-intelligence ürünü hâline getirmek.  
**Kaynak repo:** `cagataysntrk/dima-backend-feat-wren-strict-agentic`  
**Kaynak dal:** `feat/ask-v2-mvp`  
**Metabase kaynak denetim pini:** `74216b30981d8310c4cf724d63ca282e2e63529d`  
**Metabase upstream gözlemi:** `fff70175e0b5f82dc0eb267593c717c4a6130206`  
**Dima source-audit gözlemi:** `feat/ask-v2-mvp` üzerinde audit sırasında görülen son HEAD `a36f1db0b2ff91af6e1cbcde5f34456af2ee116e`. Yeni branch bunun gibi hareketli HEAD’den körlemesine değil, P0’da yeniden doğrulanmış **certified checkpoint SHA**’dan açılacaktır.  
**Revizyon:** Final audit / source-cross-check pass — query identity, access-lens, retrieval lifecycle, implicit-join authority, front-door ownership ve migration cutover hükümleri sertleştirildi.  
**Kapsam notu:** Bu belge teknik/ürün mimarisi fizibilitesidir; lisans/hukuk kararı kullanıcı talebi doğrultusunda bu teknik seçim analizinin dışında tutulmuştur.  
**Karar ilkesi:** Metabase kodu Dima backend’ine kopyalanıp eritilmeyecek. Metabase ayrı servis/substrate olarak kullanılacak. Dima cognition, semantic authority, evidence, research ve decision plane’ini koruyacak.

---

## R0 — Yönetici özeti

Kod seviyesinde yapılan çapraz incelemenin sonucu nettir:

> **Dima’nın nihai hedefi açısından Metabase, Wren’den daha geniş ve daha olgun bir analytics/BI substrate sunuyor.**

Wren bugün özellikle sektör özel semantic modeling, MDL/cubes, measure/dimension/relationship tanımları ve tenant-specific business semantics konusunda güçlü. Fakat Dima’nın bugünkü yükünün büyük kısmı semantic engine’in etrafındaki altyapıyı yeniden üretmekten geliyor: query construction, validation/repair, permissions, DB drivers, cached results, dashboards, collections, field values, saved questions, BI workspace, background query lifecycle, exploration, visualization vb.

Metabase bu çevresel altyapının çok büyük bölümünü halihazırda çözüyor.

Bu nedenle hedef mimari şu olmalıdır:

```text
USER
 ↓
DIMA EXPERIENCE
 ↓
DIMA COGNITION
 ↓
DIMA SEMANTIC AUTHORITY
 ↓
DIMA ANALYTICS CONTRACT
 ↓
METABASE ANALYTICS PLATFORM
 ↓
DATABASE / WAREHOUSE
 ↓
DIMA QUERY RECEIPT / EVIDENCE
 ↓
RESEARCH / FINDINGS / HYPOTHESES
 ↓
REPORT / DECISION
```

Fakat bu geçiş **“Wren’i sil, Metabase’e teslim ol”** şeklinde yapılmamalıdır.

Doğru geçiş:

```text
A. Dima core contract’larını engine-independent yap
B. Metabase’i ikinci substrate olarak ekle
C. Aynı accepted intent üzerinde Wren vs Metabase parity ölç
D. Wren semantic richness için ayrı equivalence gate kur
E. Parity + semantic equivalence + security + performance geçerse Metabase primary yap
F. Wren’i yalnız o zaman kaldır
```

### R0.1 — Bu raporun kesin karar sınırı

Bu rapor iki kararı birbirinden ayırır:

```text
KARAR 1 — GO:
Metabase, yeni Dima branch’inde birincil analytics-platform adayı olarak gerçek implementation ve parity testine alınacaktır.

KARAR 2 — HENÜZ OTOMATİK DEĞİL:
Wren semantic backbone kaldırılacaktır.
```

İkinci karar yalnız aşağıdaki kanıtların tümüyle verilebilir:

```text
semantic expressivity parity
numeric/grain/time parity
relationship/join-authority parity
principal/lens security parity
receipt/evidence provenance parity
operational/runtime feasibility
no release-critical WREN_ONLY_GAP
```

Metabase query execution’ın başarılı olması **Wren semantic layer’ın redundant olduğunu kanıtlamaz**. Bu ayrım bütün migration boyunca bağlayıcıdır.

### R0.2 — Yeni branch’in miras politikası

Yeni branch mevcut V2’den kod taşırken “dosya bazlı” değil “kanıt bazlı” davranır.

Taşınabilir:
- accepted-authority invariants,
- semantic binding sınırı,
- typed temporal normalization,
- Standard/Research family XOR,
- QueryContract/Evidence fikirleri,
- bounded runtime/no-progress,
- failure-triage protokolü,
- provider role separation.

Taşınamaz veya yeniden sertifikalanmadan authority olamaz:
- legacy `SemanticResolver`/regex/fuzzy/morphology authority,
- eski `/api/ask-v2` front-door ownership,
- silent fallback,
- Wren-specific representation’ı Dima canonical contract sanan kod,
- yalnız historical test yeşilliğine dayanan davranış.

---

## R1 — Dima’nın gerçek ürün tanımı

Dima yalnız NL→SQL, chatbot veya dashboard değildir.

Nihai ürün:

> Kullanıcının doğal dil talebini doğru anlayan; belirsizliği sessizce kapatmayan; şirketin gerçek iş kavramlarına bağlayan; standard analizleri hızlı yapan; kompleks taleplerde evidence gördükçe replan yapan; her resmî iddiayı kanıta bağlayan; findings, hypotheses, root-cause, report ve decision üretip bunları denetlenebilir şekilde saklayan iş analisti platformudur.

Dima’nın gerçek değer zinciri:

```text
Conversation
→ Intent
→ Semantic Authority
→ Analytics
→ Evidence
→ Research
→ Findings
→ Hypotheses
→ Report
→ Decision
→ Action / Workflow
```

Metabase esas olarak `Analytics + BI Workspace` bölümünde kullanılacaktır.

---

## R2 — Wren+Dima denemesinden korunması zorunlu ilkeler

### R2.1 Exactly-one semantic authority

Bir turn’de birden fazla model denemesi olabilir; ancak downstream semantic authority yalnız bir tanedir:

```text
AcceptedStandardAuthority
veya
AcceptedTurnContract
```

Rejected attempt field’ları merge edilmez.

### R2.2 LLM cognition, deterministic trust plane

```text
LLM:
  doğal dil
  decomposition
  planning
  tool orchestration
  adaptive reasoning
  synthesis

Dima deterministic plane:
  semantic validation
  authority
  capability
  security
  provenance
  evidence
  completion

Metabase:
  query representation
  query validation/repair/resolve
  permission-aware execution
  BI artifacts

DB:
  numeric truth
```

DMP-DEC-0026 binding clarification:

```text
LLM_FIRST_COGNITION
SEMANTIC_CORE_IS_NOT_ANALYTICAL_PLANNER
```

LLM analitik strateji, hipotez, hangi kanıtın inceleneceği, sıradaki governed tool seçimi,
adaptive replanning ve sentezin varsayılan sahibidir. Dima deterministic plane bunun yerine analist
state-machine yazmaz; truth/trust sınırlarını korur.

En hafif yol bile unscoped değildir:

```text
LLM
→ Dima minimum security/execution/provenance envelope
→ Metabase
→ Dima receipt/evidence
```

Progressive governance Level 0-3 semantic derinliği değiştirir; tenant/principal/effective-access
baseline security Level 0'da dahi zorunludur. Etkin seviye tenant, capability ve security minimumlarının
altına indirilemez.

### R2.3 Raw SQL Manager’a default olarak yasak

Metabase raw SQL desteklese bile Dima Manager production contract’ında SQL authority değildir. Metabase/MCP runtime kullanılıyorsa raw-SQL authoring capability explicit olarak kapatılır veya Dima client scope/policy ile erişilemez hâle getirilir; varsayılan upstream setting’e güvenilmez.

### R2.4 Regex/fuzzy/morphology semantic truth yasak

Candidate retrieval yardımcıdır; truth değildir.

### R2.5 Silent requirement loss release blocker

Standard:
`AcceptedStandardAuthority + projection completeness`

Research:
`UserObligationLedger + CompletionGate`

### R2.6 Evidence-bound output

Resmî numeric claim, QueryReceipt/Evidence olmadan publish edilmez.

### R2.7 Post-acceptance freedom accepted authority’yi değiştiremez

Manager yeni AGENT_DERIVED task açabilir fakat USER_MUST değiştiremez.

### R2.8 Material semantic surface completeness

Bir request içinde aynı türden iki maddi surface varsa birinin resolve olması diğerinin unresolved kalmasını gizleyemez.

```text
her material source surface
→ exactly one of:
   BOUND through governed source_ref→handle
   veya
   explicit unresolved/clarification terminal
```

Kind-level “metric var” completeness yeterli değildir.

### R2.9 Standard/Research shared authority XOR

Aynı turn için:

```text
AcceptedStandardAuthority XOR AcceptedTurnContract
```

olmalıdır. Shared authority arbiter cross-family uniqueness’i enforce eder. Standard execution fail olduktan sonra accepted Standard authority sessizce Research’e fallback yapmaz.

### R2.10 Semantic linking ve temporal normalization ayrı cognition rolleri

Catalog candidate decision ile doğal dil time/comparison normalization aynı model contract değildir. Ayrı role/provider policy kullanabilir; biri diğerinin structured client’ını sessizce reuse etmez.

---

## R3 — Metabase kod seviyesinde neden ciddi aday?

### R3.1 Generic agent runtime

Referanslar:

```text
src/metabase/metabot/agent/core.clj
src/metabase/metabot/agent/profiles.clj
src/metabase/metabot/agent/memory.clj
```

Metabase deseninin özü:

```text
profile
→ model
→ allowed tools
→ iteration budget
→ terminal tools
→ loop
→ tool result
→ model observes
→ next step / terminal
```

Bu Dima’nın `BoundedAgentRuntimeKernel + profile` yaklaşımını doğrular.

Alınacak prensip:
- tek generic runtime,
- domain/profile-specific policy,
- tool failure model’e structured observation olarak geri döner,
- explicit terminal action,
- bounded loop.

### R3.2 Agent-authored query pipeline

Referanslar:

```text
src/metabase/agent_lib/representations.clj
src/metabase/agent_lib/representations/repair.clj
src/metabase/agent_lib/representations/resolve.clj
src/metabase/mcp/v2/queries.clj
src/metabase/mcp/session.clj
```

Akış:

```text
portable query
→ validate
→ repair
→ resolve portable refs
→ normalize
→ annotate types
→ validate temporal literals
→ permission-aware resolution
→ runnable/editor gates
→ execution
```

Bu Dima’nın Wren etrafında yeniden yazdığı birçok query correctness işini hazır sunar.

### R3.3 Query handles ve anti-laundering

Metabase query handle:
- user/session’a bağlı,
- tekrar okunurken permission yeniden kontrol edilir,
- native query MBQL-only path’e sızamaz,
- parameterized query save sırasında filter kaybı fail-closed’dur.

Dima karşılığı query handle’ı kalıcı kimlik sanmamalıdır. Metabase MCP tarafında session correlator ayrı, backing session/handle lifecycle ayrı TTL ve ownership kurallarına sahiptir. Bu nedenle handle yalnız **ephemeral execution locator** olabilir.

```text
DimaQueryReceipt
  authority_id
  projection_hash
  substrate = metabase
  ephemeral_query_handle?          # opsiyonel / session-bound
  canonical_query_hash             # kalıcı
  canonical_query_representation?  # güvenli/serialize edilebilir ise
  principal_fingerprint
  execution_access_fingerprint
  semantic_context_version
  resource_fingerprints
  result_hash
```

Kalıcı audit/replay Dima’nın kendi fingerprint ve immutable receipt’i üzerinden yapılır; expired Metabase handle receipt’i geçersiz kılmaz. Handle ile tekrar execution yapılacaksa permission ve lens yeniden doğrulanır.

### R3.4 Permission ve lens-aware cached result güvenliği

Referanslar:

```text
src/metabase/queries/cached_result.clj
src/metabase/explorations/derived_perms.clj
src/metabase/explorations/derived_perms.clj
```

Metabase cached result okurken:
1. current viewer underlying query’yi çalıştırabilir mi?
2. current viewer sandbox/impersonation/routing lens’i creator lens’i ile uyumlu mu?

kontrol ediyor.

Dima EvidenceArtifact için kritik ders:

> Evidence üretildiği anda güvenli olması yetmez; tekrar okunurken current viewer context’i ile tekrar gate edilmelidir.

### R3.5 Semantic/entity retrieval + AI context

Referanslar:

```text
src/metabase/entity_retrieval/
enterprise/backend/src/metabase_enterprise/entity_retrieval/
src/metabase/search/semantic/
src/metabase/osi/
src/metabase/metabot/tools/entity_retrieval.clj
```

Metabase’de:
- retrieval index,
- synonyms,
- examples,
- instructions,
- pgvector/embedding,
- reconcile,
- permission-aware hydration

vardır.

`osi_ai_context` özellikle Dima packs/knowledge/memory yaklaşımına yakındır:

```text
instructions
synonyms[]
examples[]
```

Ancak retrieval result yalnız candidate’tır; Dima BindingGate authority olmaya devam eder.

### R3.6 Glossary

```text
src/metabase/glossary/
```

Business terminology için faydalı; fakat Wren MDL’deki formula/grain/relationship semantics’in eşdeğeri değildir.

### R3.7 Metrics / measures / segments / models

Metabase metric/model/measure/segment primitive’leri Wren semantic layer’ın bir bölümünü karşılayabilir.

Ancak aşağıdaki alanlar ayrı eşdeğerlik testi ister:

```text
formula expressivity
grain
additivity / semi-additivity
unit
relationship path
role-playing dimensions
time semantics
derived metrics
customer override
semantic provenance
Git portability
```

### R3.8 Field values ve indexed entities

Referanslar:

```text
src/metabase/parameters/field_values.clj
src/metabase/indexed_entities/
```

Dima için ciddi kazanım:
- entity/filter suggestion,
- high-cardinality categorical lookup,
- linked-filter values,
- human-readable mapping,
- security-lens-aware cache keys.

### R3.9 Explorations Dima Research için çok önemli

Referanslar:

```text
src/metabase/explorations/
src/metabase/contextual_interestingness/
src/metabase/explorations/query_plan/
src/metabase/explorations/runner.clj
```

Mevcut yetenekler:
- metric-dimension applicability,
- deterministic planning,
- query variants,
- background execution,
- stored results,
- statistical interestingness,
- contextual interestingness,
- thread persistence,
- cancel/restart,
- idempotent processing,
- derived-data permissions.

Bu Research Manager’ın yerine geçmez; fakat research execution substrate’ı ciddi ölçüde hızlandırabilir.

### R3.10 MechanicalPlanner yaklaşımı

Metabase metric×dimension kombinasyonlarından bounded variant üretir:
- default,
- top-N + other,
- temporal patterns,
- time facet.

Dima için ders:

> Metabase deterministic variant generator'ları reusable **execution/research utilities** olabilir;
> otomatik olarak Dima cognition değildir. Bir generator ancak DMP-DEC-0026 Semantic Necessity Gate,
> LLM-first baseline'a karşı maddi correctness/cost/latency değeri kanıtlarsa Dima'nın kalıcı
> execution primitive'i olarak promote edilir.

Top-K + Other, bounded cardinality fanout veya deterministic date comparison gibi bounded utility'ler
izinlidir; statüleri `TOOL / EXECUTION PRIMITIVE`dir, `COGNITION OWNER` değildir.

### R3.11 — Effective access lens birinci sınıf execution girdisidir

Metabase `cached_result` ve Exploration tarafında yalnız role/permission değil, sandbox/impersonation/database-routing etkisini temsil eden data-access lens’i de sonuç görünürlüğüne dahil ediyor.

Dima için kalıcı primitive:

```text
ExecutionAccessFingerprint
  tenant_binding
  principal_subject
  role_set_digest
  attribute_policy_digest
  policy_version
  rls_cls_rule_versions
  database_route
  impersonation_role
  semantic_context_version
  source_object_refs
  security_parameter_digest
```

Raw PII/sensitive attribute fingerprint’e yazılmaz; digest/version tutulur.

### R3.12 — Security-bound persistence refusal

Bazı query’ler runtime-only security parameter/binding taşıyabilir. Bu binding kayıpsız serialize edilemiyorsa:

```text
execute now = mümkün olabilir
persist/replay = YASAK
```

Dima hiçbir zaman “serialize edemedik ama sonra aynı query sayarız” demez.

### R3.13 — Retrieval lifecycle: index hit authority değildir

Metabase entity retrieval ve indexed entity altyapısından alınacak kalıcı ayrım:

```text
INDEX_UNAVAILABLE
!=
NO_MATCH
!=
SEMANTIC_GAP
```

Doğru Dima akışı:

```text
index/search
→ candidate ids
→ current tenant hydration
→ current principal/access check
→ current context/catalog membership
→ CandidateSet
→ SemanticBindingGate
```

Index sadece discovery hızlandırır. Current authority üretmez.

### R3.14 — High-cardinality/sensitive entity value için live re-read

Metabase indexed entity kodu index’i candidate discovery için kullanırken gerçek value’yu current user lens’i altında QP üzerinden yeniden okuyabilen bir desen taşıyor.

Dima’da özellikle:
- müşteri,
- personel,
- ürün seri/kod,
- sensitive business entity

gibi değerlerde index sonucu tek başına evidence/authority olamaz. Candidate seçildikten sonra current-principal live read gerekir.

### R3.15 — Client capability authorization değildir

Metabase MCP session kodu client capability hint’lerini imzalıyor fakat bunları auth state ile eşitlemiyor. Dima için genel invariant:

```text
client says “I support/can X”
!=
server authorizes X
```

UI/MCP/client feature capability ile principal permission ayrı kanallardır.

### R3.16 — REST serialized query ile MCP query_handle aynı şey değildir

Metabase’de:
- REST/Agent API serialized query/continuation,
- MCP server-side `query_handle`

farklı lifecycle/identity mekanizmalarıdır.

Yeni Dima adapter’ı bunları tek “Metabase handle” abstraction’ına zorla sıkıştırmayacaktır. Primary production integration surface seçildikten sonra receipt contract o surface’e özel ama Dima-owned kalacaktır.

### R3.17 — Implicit FK repair ikinci join authority olabilir

Metabase representation repair/resolve fiziksel FK metadata’sından join yolu çıkarabilir. Dima için bu yalnız query repair değildir; semantic relationship authority’ye temas eder.

Kalıcı P0:

```text
UNAPPROVED_METABASE_IMPLICIT_JOIN = 0
```

Her implicit join Dima `RelationshipSpec` / approved semantic graph ile uyumlu olmalıdır. Aksi halde query fail-closed olur.

### R3.18 — Representation repair idempotent ve bounded olmalıdır

Metabase query representation pipeline’ının önemli avantajı LLM çıktısını normalize/repair etmesidir. Dima bunu kullanırken repair’in semantic meaning’i değiştirmediğini kanıtlamalıdır.

```text
repair(repair(q)) == repair(q)
```

ve:

```text
repair before/after semantic projection meaning = same
```

family testleri gerekir.

### R3.19 — Async research: idempotency, cancel ve race safety

Metabase Explorations runner’ın güçlü taraflarından biri plan/query işlerindeki:
- duplicate delivery handling,
- terminal state,
- cancel race cleanup,
- restart,
- persisted failure

desenidir.

Dima Research background execution’da bu sınıflar MVP sonrası “ops polish” değil correctness’tir.

### R3.20 — Interestingness yalnız attention policy’dir

Statistical/contextual interestingness:
- hangi evidence’a önce bakılacağını,
- hangi chart’ın raporda öne alınacağını
etkileyebilir.

Fakat:

```text
interestingness score != truth
interestingness score != Finding
interestingness score != cause
```

Epistemic promotion yine Dima Evidence/Finding/Hypothesis gate’lerindedir.

### R3.21 — Content verification / official content metadata

Metabase content-verification primitive’leri curated/official analytics resource işaretleme için faydalıdır. Dima’da bunun karşılığı:

```text
managed semantic resource
verified analytical artifact
user-created exploratory artifact
```

ayrımı olmalıdır. “Official” etiketi semantic truth üretmez fakat retrieval ranking, UX trust ve onboarding governance için kullanılabilir.

### R3.22 — Metabase source pin ile runtime pin ayrıdır

Kaynak audit için bir Git SHA pinlemek başka, production runtime image/release pinlemek başkadır.

```text
SOURCE_AUDIT_PIN = exact Git SHA
RUNTIME_PIN      = exact supported release + immutable image digest
```

Production test receipt ikisini de kaydetmelidir.

### R3.23 — Agent API availability kendi runtime capability’sidir

Audited Metabase source’da `agent-api-enabled?`, global `ai-features-enabled?` ile birlikte gate ediliyor. Dima için sonuç:

```text
Metabase process healthy
!=
Agent API usable
```

Startup/capability handshake:
- `/v1/ping`,
- required endpoint/version,
- required scopes,
- query construct/execute capability,
- raw-SQL policy,
- pagination/row budget
ayrı ayrı doğrulanır.

Agent API kapalıysa outcome `TRANSPORT/PROVIDER`/runtime capability failure’dır; semantic wrong değildir.

### R3.24 — REST query identity ile pagination state ayrıdır

Audited Agent API REST akışında `construct-query` resolved MBQL’nin serialized/base64 temsilini döndürebilir; combined query endpoint continuation token içinde query + pagination state taşır. MCP katmanı bunu server-side query handle’a çevirebilir.

Dima primary REST adapter’ında:

```text
canonical query representation/hash = durable receipt material
continuation token                  = ephemeral pagination state
MCP query handle                    = optional session-bound locator
```

Bu üçü birbirinin yerine kullanılmaz.

### R3.25 — Agent API row budget Dima architecture’ını şekillendirir

Audited source’da combined query endpoint page-size ve toplam row cap ile bounded çalışıyor. Exact değer runtime version’a göre capability olarak ölçülmelidir; hard-code product contract yapılmaz.

Dima prensibi:

> Research Manager warehouse’dan ham milyonlarca row çekmez; aggregate/breakdown/statistical query’leri data engine’de çalıştırır, bounded evidence döndürür.

Large extract gerçekten gerekiyorsa ayrı governed export/batch capability olur; conversational analytics path’e gizlice eklenmez.

### R3.26 — Metabase app DB yalnız metadata deposu sayılmamalıdır

Metabase cache/stored-result/exploration mekanizmaları warehouse’dan türetilmiş sonuç değerlerini persistence katmanına yazabilir. Bu nedenle Metabase app DB ve backup’ları:
- sensitive analytical data içerebilir,
- encryption/retention/access-control gerektirir,
- tenant isolation threat modeline dahildir.

“Warehouse ayrı, Metabase app DB zararsız metadata” varsayımı yasaktır.

---

## R4 — Metabase’in Dima için riskleri

### R4.1 İkinci semantic owner

Yasak:

```text
Dima semantic says A
Metabase metric says B
→ hangisi çalışırsa
```

Tek owner:

```text
DimaSemanticSpec = canonical business meaning
Metabase object = executable BI representation
```

### R4.2 Raw schema bypass

Accepted semantic ref yoksa Metabase table/field discovery ile query üretmek production’da yasak.

### R4.3 Tenant/principal mapping

Çözülmesi şart:
- Dima tenant → Metabase user/group,
- user-scoped execution,
- sandboxing,
- DB routing,
- connection impersonation,
- background jobs,
- cached artifacts.

### R4.4 Query identity

Authority ile query immutable bağlanmalı.

### R4.5 Resource drift

Metabase metric/model/question değişirse eski evidence replay semantiği bozulabilir.

Gerekli:
- resource fingerprint/version,
- context_version,
- immutable receipt,
- stored result hash.

### R4.6 Upgrade risk

Metabase pinned version + app DB backup + migration rehearsal + rollback şart.

### R4.7 Session/handle lifecycle’i durable provenance sanmak

MCP/agent handle’ları session-bound/expirable olabilir. Dima audit zincirinin kalıcı anahtarı Metabase handle değildir; Dima receipt + canonical query fingerprint’tir.

### R4.8 Permission-sensitive cache contamination

Cache key tenant/principal/lens farklarını içermiyorsa bir kullanıcının discovery/result cache’i diğerine sızabilir. Cache correctness security correctness’in parçasıdır.

### R4.9 Implicit join drift

Metabase fiziksel FK ile çalışabilse bile Dima sektör semantic graph’ında yasak/yanlış bir ilişkiyi otomatik kullanabilir. Join path execution’dan önce Dima relationship authority’ye karşı doğrulanmalıdır.

### R4.10 App-DB state’in gizli product dependency’ye dönüşmesi

Metabase app DB’deki resource ID’leri Dima domain kimliği olamaz. Dima canonical ID/entity-id/fingerprint saklar; numeric Metabase IDs adapter-local kalır.

### R4.11 Experimental/fast-moving upstream feature bağımlılığı

Explorations/Agent API/MCP gibi hızlı gelişen alanlarda source master’daki davranış production sözleşmesi sanılmamalıdır. Her kullanılan capability exact runtime version’da behavioral contract test ile sertifikalanır.

### R4.12 Portable-name resolution / rename drift

Agent API portable query representation database/schema/table/column isimleriyle resolve olabilir. Dima adapter bu isimleri modelden/LLM’den tahmin etmez; `DimaSemanticSpec.SourceLineage` + current pinned catalog snapshot’tan deterministik derler.

Rename sonrası:
- resource/source fingerprint değişir,
- old evidence replay/staleness değerlendirilir,
- silent “benzer isimli başka kolon” bind edilmez.

### R4.13 Çift connection owner

Wren döneminden kalan Dima DB credentials ile Metabase DB credentials aynı anda gereksizce kalırsa secret rotation, routing ve audit ikiye bölünür.

Nihai topology’de connection owner explicit olmalıdır:
- standard BI/query plane için Metabase,
- yalnız Metabase’in karşılamadığı specialized governed engine varsa Dima’da ayrı read-only connection.

Aynı capability için iki bağımsız live connection owner yoktur.

---

## R5 — Wren’den korunacak semantic yetenekler

Migration checklist:

```text
models
columns
relationships
calculated fields
views
cubes
measures
dimensions
time dimensions
metric formula
aggregation
unit
grain
join path
aliases
customer overrides
semantic versioning
Git-managed packs
tenant runtime
```

Wren removal için eşitlik yalnız aynı sayı değil:

```text
same meaning
same aggregation
same grain
same joins
same time behavior
same filters
same numeric result
same permission boundary
same provenance
```

---

## R6 — Dima-owned canonical semantic spec

Uzun vadede ürün kimliği Wren veya Metabase object model olmamalı.

Önerilen:

```text
DimaSemanticSpec
  SemanticEntity
  MetricSpec
  DimensionSpec
  RelationshipSpec
  TimeSpec
  BusinessRule
  DisplaySpec
  SecurityTag
  Alias/Synonym
  Example
  Provenance
  Version
  CompatibilityHash
  ManagedResourcePolicy
  SourceLineage
```

Adapter:

```text
DimaSemanticSpec
  ├─ WrenAdapter
  └─ MetabaseAdapter
```

Bu, substrate değişimini gelecekte de mümkün kılar.

### R6.0 — Semantic core truth'tür; analitik planner değildir

`DimaSemanticSpec` canonical business truth sahibidir; analitik araştırma stratejisinin sahibi
değildir. Yeni deterministic research-plan/root-cause-sequence alanları ancak
`SEMANTIC_NECESSITY_GATE` ile kanıtlanmış generic correctness ihtiyacı varsa eklenebilir.

Progressive semantic governance:

```text
Level 0  native analytics + mandatory security/execution/provenance envelope
Level 1  canonical metric/dimension/time/lineage/version
Level 2  relationship/grain/additivity/advanced time + governed security/business lens
Level 3  sector/decision semantics + specialized governed workflows
```

LLM bütün seviyelerde cognition sahibi kalır. Governance seviyesi yalnız ne kadar truth/trust
guardrail'i gerektiğini belirler.

### R6.1 — Semantic spec ile execution intent ayrıdır

Metabase adapter’ının semantic handle çözmesi veya label/name üzerinden anlam çıkarması yasaktır.

Dima semantic plane accepted authority’den sonra handle’ları **bir kez** çözer ve engine-independent execution nesnesi üretir:

```text
ResolvedAnalyticsIntent
  metric refs
  dimension refs
  filters
  time window
  comparison
  ranking/limit
  approved relationship paths
  grain constraints
  principal/security context refs
```

Sonra:

```text
ResolvedAnalyticsIntent
   ├→ WrenExecutionAdapter
   └→ MetabaseExecutionAdapter
```

Bu seam kritik çünkü iki substrate A/B’sinde aynı semantic anlamı gerçekten sabit tutar ve adapter’ların ikinci semantic compiler’a dönüşmesini engeller.

---

## R7 — Standard Engine hedefi

```text
USER
 ↓
Language Runtime
 ↓
SemanticCatalogRetriever
 ↓
BoundedSemanticLinker
 ↓
SemanticBindingGate
 ↓
TemporalNormalizer
 ↓
StandardBuilder
 ↓
RepresentabilityGate
 ↓
CoverageVeto
 ↓
AcceptedStandardAuthority
 ↓
ResolvedAnalyticsIntent        # Dima-owned, handles resolved exactly once
 ↓
MetabaseExecutionAdapter
 ↓
Metabase validation/repair/resolve
 ↓
Query Processor
 ↓
DimaQueryReceipt
 ↓
EvidenceArtifact
 ↓
Answer / Chart
```

`STANDARD_DIRECT` ayrı engine değildir; tek turda seal olan Standard telemetry’sidir.

---

## R8 — Research Engine hedefi

```text
USER
 ↓
AcceptedTurnContract
 ↓
UserObligationLedger
 ↓
ResearchManager
 ↓
Governed typed tools
 ↓
Dima Analytics Gateway / ResolvedAnalyticsIntent
 ↓
Metabase analytics substrate
 ↓
EvidenceArtifact
 ↓
Interestingness / stats
 ↓
Manager observe/replan
 ↓
Finding / Hypothesis
 ↓
CompletionGate
 ↓
ReportDocument
 ↓
DecisionBrief
```

Manager/LLM:
- observe eder,
- hipotez üretir,
- sıradaki governed analytical tool'u seçer,
- evidence gördükçe replanning yapar,
- sentez ve rapor reasoning'ini yürütür,
- SQL yazmaz,
- semantic mint etmez,
- permission bypass etmez,
- numeric truth üretmez.

Deterministic Dima tarafı:
- budget/fanout/tool schema,
- security,
- relationship/grain approval,
- evidence validity,
- no-progress/idempotency/cancellation,
- completion obligations

gibi trust ve execution sınırlarını yönetir; universal analytical sequence belirlemez.

---

## R9 — Dima Query Receipt

```text
DimaQueryReceipt
  receipt_id
  authority_id
  obligation_ids
  tenant_id
  principal_id
  semantic_context_version
  semantic_refs
  projection_hash
  resolved_intent_hash
  substrate
  substrate_runtime_version
  substrate_image_digest
  ephemeral_metabase_query_handle?     # durable identity DEĞİL
  canonical_query_fingerprint
  canonical_query_representation?      # güvenli/serializable ise
  database_id
  execution_access_fingerprint
  resource_entity_ids
  resource_fingerprints
  executed_at
  row_count
  result_hash
  warnings
  limitations
```

Evidence:

```text
EvidenceArtifact
  evidence_id
  receipt_id
  kind
  verified
  structured_payload
  display_payload
  limitations
```

---

## R10 — Security invariants

```text
cross-tenant semantic leak = 0
cross-tenant result leak = 0
cached incompatible-lens read = 0
missing principal execution = 0
service/admin implicit fallback = 0
raw SQL silent bypass = 0
authority/query mismatch = 0
unapproved implicit join = 0
permission-sensitive cache cross-user reuse = 0
security-bound replay without faithful serialization = 0
```

### R10.1 ExecutionAccessFingerprint

Her resmi execution/evidence receipt’i non-secret bir access fingerprint taşımalıdır:

```text
tenant_binding
principal_subject
role_set_digest
attribute_policy_digest
policy_version
RLS/CLS versions
database route / destination
impersonation role
semantic context version
source object refs
security parameter digest
```

### R10.2 Read-time reauthorization

Evidence/report/dashboard snapshotı başka kullanıcıya veya daha sonra aynı kullanıcıya gösterilirken yalnız creation-time permission’a güvenilmez. Current principal query permission + lens compatibility yeniden gate edilir.

### R10.3 Missing creator/principal fail closed

Background worker creator/principal context’i kaybetmişse admin/service-user ile “devam etmek” yasaktır.

---

## R11 — Deployment topology

Öneri:

```text
dima-api
dima-worker
dima-db
queue/redis
metabase
metabase-app-db
customer-db(s)
```

Metabase:
- separate service; aynı Python process/library içine embed edilmeye çalışılmaz,
- private network,
- **runtime release + immutable image digest** pinlenir,
- source-audit Git SHA ayrıca kaydedilir,
- persistent production app DB; cached/stored analytical values içerebileceği için sensitive data store kabul edilir,
- encrypted/controlled backup + retention/restore,
- migration rehearsal,
- health/readiness,
- bounded connection pool,
- explicit principal/auth mapping.

Tenant deployment iki profile sahip olabilir:

```text
SHARED PLATFORM
  tek Metabase cluster
  tenant başına ayrı DB/resource namespace/group/policy
  yalnız cross-tenant P0 corpus green ise

DEDICATED TENANT
  hassas/regüle müşteri için ayrı Metabase deployment/app DB
  daha pahalı fakat blast radius daha küçük
```

Yeni ürün önce tek-tenant/pilot topology’de sertifikalanır; multi-tenant scale semantics sonradan açılır.

---

## R12 — Tenant onboarding

```text
1. DB connection
2. schema introspection
3. candidate DimaSemanticSpec
4. verification
5. Metabase resource provisioning
6. permission mapping
7. smoke queries
8. semantic parity
9. pilot
```

---

## R13 — Build vs buy

### Dima build

```text
conversation cognition
semantic authority
DimaSemanticSpec
AcceptedStandardAuthority
AcceptedTurnContract
UserObligationLedger
ResearchManager
EvidenceArtifact
Finding
HypothesisLedger
CompletionGate
ReportDocument
DecisionBrief
decision record
workflow governance
sector packs
```

### Metabase reuse

```text
DB connectivity
metadata
query representation
validation/repair/resolve
query processor
permissions/lens
saved questions
models
metrics/measures/segments
dashboards
collections
visualizations
field values
result cache
stored results
BI workspace
exploration infrastructure
```

### Wren migrate/retain

```text
MDL richness
cubes
metric formulas
grain
relationships
tenant packs
business definitions
verified examples
semantic version discipline
```

---

## R14 — En büyük riskler

| Risk | Önlem |
|---|---|
| Metabase ikinci semantic owner | DimaSemanticSpec + BindingGate |
| Wren semantic richness kaybolur | semantic equivalence gate |
| resource drift | fingerprints/versioned receipts |
| authority/query mismatch | immutable QueryReceipt |
| cached data lens leak | read-time lens gate |
| service account aşırı yetki | user-scoped execution |
| raw SQL bypass | disabled/default governed capability |
| upgrade kırılması | pinned version + rehearsal |
| dual research brain | Dima Research authority primary |
| false semantic parity | Wren-vs-Metabase golden corpus |
| hidden query shape drift | adapter contract tests |
| background duplicate | idempotency keys |
| query handle expiry/session drift | durable Dima receipt + optional ephemeral handle |
| index unavailable = no-match sanılması | typed retrieval outcomes |
| implicit FK join semantic graphı bypass eder | RelationshipSpec join gate |
| permission-sensitive cache contamination | access-fingerprint cache partition + current-principal hydrate |
| runtime-only security binding replayde kaybolur | persistence refusal |
| app DB numeric IDs Dima identity olur | Dima canonical IDs/entity IDs/fingerprints |
| experimental Metabase feature upgrade kırar | exact runtime pin + behavioral contract suite |
| Agent API global AI setting yüzünden unavailable | startup capability handshake + typed runtime failure |
| portable name rename drift | SourceLineage + catalog fingerprint + fail-closed resolve |
| Metabase app DB backup analytical data taşır | sensitive-store encryption/retention/access policy |
| aynı DB connection iki farklı owner’da | explicit connection ownership + secret rotation policy |
| unbounded row fetch | aggregate-first tools + explicit row/export budgets |
| runaway research | bounded runtime |

---

## R15 — STOP-THE-LINE

Aşağıdakilerden biri görülürse geçiş durur:

```text
ikinci semantic owner
silent requirement loss
ambiguity auto-pick
authority/query mismatch
unverified numeric claim
cross-domain no-path join
principal/security bypass
cached evidence incompatible viewer leak
model-specific business branch
raw-schema semantic bypass
unapproved Metabase implicit FK join
session/query handle’ın durable provenance sanılması
INDEX_UNAVAILABLE ile NO_MATCH/SEMANTIC_GAP’in birleştirilmesi
security-bound query’nin kayıplı persist/replay edilmesi
portable-name rename sonrası silent rebind
Agent API capability unavailable iken semantic fallback
unbounded conversational raw-row extraction
Wren/Metabase unexplained numeric parity mismatch
silent fallback
```

---

## R16 — Nihai mimari

```text
┌────────────────────────────────────────────┐
│ USER                                       │
└────────────────────┬───────────────────────┘
                     ↓
┌────────────────────────────────────────────┐
│ DIMA EXPERIENCE                            │
│ conversation / dashboards / reports        │
└────────────────────┬───────────────────────┘
                     ↓
┌────────────────────────────────────────────┐
│ DIMA COGNITION                             │
│ language / planning / research / synthesis │
└────────────────────┬───────────────────────┘
                     ↓
┌────────────────────────────────────────────┐
│ DIMA SEMANTIC AUTHORITY                    │
│ semantic spec / binding / accepted auth    │
└────────────────────┬───────────────────────┘
                     ↓
┌────────────────────────────────────────────┐
│ DIMA ANALYTICS CONTRACT                    │
│ StandardProjection / ResearchTask          │
└────────────────────┬───────────────────────┘
                     ↓
┌────────────────────────────────────────────┐
│ DIMA RESOLVED EXECUTION INTENT             │
│ semantic refs resolved once / join policy  │
└────────────────────┬───────────────────────┘
                     ↓
┌────────────────────────────────────────────┐
│ METABASE ANALYTICS PLATFORM                │
│ Lib / MBQL / QP / perms / cache / BI       │
└────────────────────┬───────────────────────┘
                     ↓
┌────────────────────────────────────────────┐
│ DATABASES                                  │
└────────────────────┬───────────────────────┘
                     ↓
┌────────────────────────────────────────────┐
│ DIMA EVIDENCE                              │
│ receipt / evidence / findings              │
└────────────────────┬───────────────────────┘
                     ↓
┌────────────────────────────────────────────┐
│ DIMA DECISION                              │
│ hypotheses / reports / recommendation      │
└────────────────────────────────────────────┘
```

---

## R17 — Nihai fizibilite hükmü

**GO.** Yeni Metabase+Dima branch’i açılmalı.

Fakat iki ayrı gate vardır:

```text
GATE A — METABASE PLATFORM ADOPTION
Metabase query lifecycle / permissions / BI / workspace’in Dima için kalıcı runtime değeri var mı?

GATE B — WREN RETIREMENT
DimaSemanticSpec + Metabase, Wren’in kullanılan semantic gücünü kayıpsız taşıyor mu?
```

Kurallar:

```text
1. Dima intelligence/authority contracts engine-independent olur.
2. Accepted authority semantic handle’ları bir kez Dima-owned ResolvedAnalyticsIntent’a çözer.
3. Metabase adapter yalnız execution/query-lifecycle işi yapar; raw label’dan anlam çıkarmaz.
4. Aynı resolved intent Wren ve Metabase’te A/B edilir.
5. Semantic equivalence execution parity’den ayrı kanıtlanır.
6. Metabase analytics substrate olarak sertifikalanırsa primary olabilir.
7. Wren semantic özellikleri DimaSemanticSpec’e taşınır/compile edilir.
8. Wren ancak parity + semantic equivalence + security + provenance + performance sonrası çıkarılır.
9. Metabase beklenen residual engineering value’yu sağlamazsa Wren primary kalabilir; bu deney başarısızlık değildir.
10. LLM analytical cognition'ın default sahibidir; Dima semantic core truth/trust sahibidir.
11. Level 0 bile authenticated tenant/principal/effective-access/provenance envelope'ını bypass edemez.
12. Governance seviyesi model tarafından mandatory minimumların altına indirilemez.
13. Yeni deterministic cognition/semantic mechanism önce Semantic Necessity Gate'ten geçer.
14. Luna default/economic baseline, Sol ceiling/headroom ölçümüdür; aynı frozen corpus/tool/context kullanılır.
15. Fast Track/ask-v2 code wholesale merge edilmez; milestone-owner altında controlled harvest yapılır.
```

Bu rota Dima’yı “BI motoru yazma” işinden çıkarıp semantic/research/evidence/decision katmanına yoğunlaştırdığı için vizyona ulaşma açısından en güçlü adaydır; fakat Wren removal ideolojik hedef değil, ölçülen sonuçtur.

---

## R18 — Metabase kaynak referans haritası

```text
# Agent runtime
src/metabase/metabot/agent/core.clj
src/metabase/metabot/agent/profiles.clj
src/metabase/metabot/agent/memory.clj

# Agent API / query lifecycle
src/metabase/agent_api/api.clj
src/metabase/agent_api/query_guards.clj
src/metabase/agent_api/validation.clj
src/metabase/mcp/v2/queries.clj
src/metabase/mcp/session.clj

# Query representation
src/metabase/agent_lib/representations.clj
src/metabase/agent_lib/representations/repair.clj
src/metabase/agent_lib/representations/resolve.clj

# Security
src/metabase/query_permissions/
src/metabase/query_processor/
src/metabase/queries/cached_result.clj
src/metabase/explorations/derived_perms.clj

# Retrieval / AI context
src/metabase/entity_retrieval/
src/metabase/search/semantic/
src/metabase/osi/
src/metabase/glossary/

# Values
src/metabase/indexed_entities/
src/metabase/parameters/field_values.clj
src/metabase/content_verification/

# Explorations
src/metabase/explorations/
src/metabase/contextual_interestingness/
src/metabase/explorations/query_plan/
src/metabase/explorations/runner.clj

# BI
src/metabase/dashboard/
src/metabase/collection/
src/metabase/revisions/
```


---

## R19 — Final audit checklist

Bu belge “nihai” kabul edilmeden önce yapılan çapraz kontrolün bağlayıcı sonucu:

```text
[YES] Dima cognition ile semantic truth ayrılmış.
[YES] Standard ve Research authority family XOR korunmuş.
[YES] Metabase ikinci semantic owner yapılmamış.
[YES] Wren execution parity ile semantic retirement kararı ayrılmış.
[YES] query_handle durable receipt kimliği olmaktan çıkarılmış.
[YES] current-viewer/lens reauthorization evidence modeline taşınmış.
[YES] permission-sensitive retrieval/cache riskleri kapsanmış.
[YES] implicit FK join semantic authority riski açık P0 olmuş.
[YES] index unavailable / no-match / semantic-gap ayrılmış.
[YES] runtime-only security binding persistence refusal tanımlanmış.
[YES] Metabase Explorations’tan idempotency/cancel/race ve interestingness dersleri alınmış.
[YES] source audit pin ile runtime deployment pin ayrılmış.
[YES] REST serialized query / continuation / MCP handle lifecycle ayrılmış.
[YES] Agent API capability availability runtime handshake’e bağlanmış.
[YES] Metabase app DB sensitive analytical store olarak threat model’e alınmış.
[YES] portable-name/rename drift ve connection ownership ele alınmış.
[YES] front-door ve legacy semantic authority migrationı yol haritasında release blocker yapılmış.
[YES] Metabase runtime adoption ve Wren retirement iki ayrı karar gate’i olmuş.
```

Bu rapor bundan sonra gerekçesiz biçimde yeniden yazılmaz. Yeni source bulgusu çıkarsa living audit/decision receipt açılır; normatif mimari ancak kanıtlı architecture decision ile nokta atışı revize edilir.


---

# NORMATİF MİMARİ EK — DMP-DEC-0031 / DIMA METABASE ENGINE

Bu ek önceki karar geçmişini silmez; Agent API'nin birincil production-engine seam olduğu varsayımını nokta atışı revize eder.

```text
DIMA EXPERIENCE
→ DIMA COGNITION / DECISION
→ DIMA SEMANTIC + SECURITY + EVIDENCE CONTROL PLANE
→ DIMA ENGINE BRIDGE
→ DIMA METABASE ENGINE
→ METABASE NATIVE ANALYTICS / AGENT ENGINE
→ DATABASE
```

`Dima Metabase Engine`, upstream `metabase/metabase` geçmişini koruyan ince fork'tur. İlk base `v0.63.18 / 2ba2485c78d7e00a9a25f82c00fc201da71590c4` olur. Native Metabot loop, profiles, skills, memory/state, MBQL, Query Processor ve drivers yeniden yazılmaz. Agent API bir utility surface olabilir; birincil engine boundary olarak varsayılmaz.

Authority ayrımı değişmez:
```text
Metabase native engine = analytical orchestration/execution substrate
Dima = business semantic truth + tenant/principal control truth + ExecutionAccessSnapshot + QueryReceipt + Evidence + durable research/decision intelligence
```

Native Metabase permissions aktif kalır fakat Dima access truth'ünün yerine geçmez. P13 trust boundary reimplementation yerine material trust transition hook'larıyla kurulacaktır. `CanonicalProjection` silinmez; native-engine içindeki rolü P13'te kanıtla belirlenir.

Fork/release disiplini:
- tek engine artifact SaaS + self-host;
- customer/sector source fork yasak;
- build fork source'dan ve upstream-supported build yoluyla;
- C0'da modified existing upstream source files = 0;
- `DIMA_PATCH_SURFACE` her engine build/release'te zorunlu;
- upstream sync candidate-only + manual promotion;
- production `metabase:latest` takip etmez;
- published engine history otomatik rebase edilmez.

Bağlayıcı karar kaydı: `DMP-DEC-0031`.
