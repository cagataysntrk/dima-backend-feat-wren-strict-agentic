# DIMA — NİHAİ DENETİM, KÖK NEDEN VE HEDEF MİMARİ RAPORU

**Tarih:** 20 Eylül 2026
**Repo:** `cagataysntrk/dima-backend-feat-wren-strict-agentic`
**Dal:** `wren-bağımsız`
**Denetlenen HEAD:** `869280db316d5bf3f76d3253b8b80e5609a000b9`
**Belge rolü:** Açıklayıcı ve normatif hedef mimari raporu. Uygulama sırası için eş belge olan `DIMA_NIHAI_UYGULAMA_YOL_HARITASI.md` kullanılır.
**Son kabul-modeli güncellemesi:** 20 Eylül 2026 — her yetenek seviyesi için kullanıcı senaryosu, ölçülebilir KPI, UI/UX kabul ölçütü ve North-Star kompleks analiz deneyimi eklendi.
**Kanonik mevcut-davranış otoritesi:** Repo içindeki `backend/MIMARI.md`. Bu rapor uygulanmamış hedefleri “mevcut gerçek” gibi sunmaz.

---

## R0 — BU RAPOR NEDEN VAR?

Dima için geçmişte çok fazla doğru fikir üretildi; fakat bunlar giderek aynı dev uygulama belgesinin içine yığıldı. Sonuçta iki ayrı ihtiyaç birbirine karıştı:

1. **Sistemin neden bozulduğunu ve nihai mimarinin neden böyle olması gerektiğini anlamak.**
2. **Yarın sabah hangi dosyaya hangi sırayla dokunacağını bilmek.**

Bu rapor birinci ihtiyacı çözer. Yol haritası ikinci ihtiyacı çözer.

Bu ayrım bilgi silmek için değil, **bilgiyi yanlış sırada okutmayı engellemek** için yapılmıştır.

### R0.1 Tek kaynak politikası

Bu rapor mimari gerekçenin, eş yol haritası ise uygulama sırasının kanonik kaynağıdır.

Tarihsel çalışma notları ve arşiv belgeleri nihai geliştirici deneyiminin parçası değildir. Bir kararın nedenini anlamak için gerekli bütün gerekçe bu raporun kendi içinde bulunmalıdır.

### R0.2 Geliştirici için kullanım sırası

Dima’yı hiç bilmeyen geliştirici şu sırayı izlemelidir:

```text
1. Bu raporda R1–R6
2. Bu raporda R7–R15
3. Yol haritasında P0–P4
4. Kod yazarken yalnız ilgili rapor/yol-haritası maddesi
5. Her PR sonunda yol haritasındaki STOP-THE-LINE kapıları
```

Bütün eski belgeleri baştan sona okumak zorunlu değildir.

---


## R0.3 Bu belgede “başardık” ne demek?

Dima'da bir özelliğin kodunun yazılmış olması başarı değildir.

Her capability için beş ayrı kanıt aranır:

```text
1. SEMANTIC
   Kullanıcının ne istediğini doğru temsil ettik mi?

2. ANALYTIC
   Doğru veriyi / doğru grain'i / doğru hesabı çalıştırdık mı?

3. CONVERSATIONAL
   Kullanıcıyla doğru şekilde konuştuk mu?
   Gerekiyorsa sorduk mu; gereksiz query çalıştırdık mı?

4. EVIDENCE
   Söylediğimiz şeyi hangi sonuç/contract kanıtlıyor?

5. EXPERIENCE
   Kullanıcı sonucu anlamlı, hızlı ve kontrol edilebilir biçimde alabildi mi?
```

Bir capability ancak bu beş boyutun ilgili olanları yeşilse “tamam” sayılır.

### KPI sınıfları

Bu raporda ve eş yol haritasında KPI'ler şu sınıflarda yazılır:

```text
P0 SAFETY / CORRECTNESS
→ sıfıra yakın hata değil; release blocker.
  Örnek: silent-wrong, cross-tenant evidence, unsupported causal claim.

P1 PRODUCT QUALITY
→ doğru kullanıcı deneyiminin ölçüsü.
  Örnek: clarification correctness, follow-up correctness, report completeness.

P2 PERFORMANCE
→ deneyimin bekleme maliyeti.
  Örnek: p95 latency, time-to-first-status, research wall time.

P3 EFFICIENCY
→ sistemi gereksiz pahalı/karmaşık yapmama.
  Örnek: unnecessary query rate, LLM turns, research budget.
```

### KPI yorumu

Aşağıdaki hedefler **başlangıç release gate'leridir**; “bugün ölçülmüş başarı” değildir.
Gerçek müşteri datası ve latency profili geldikçe hedefler ölçümle güncellenebilir.

Fakat şu P0'lar pazarlığa açık değildir:

```text
silent-wrong on P0 holdout              = 0
cross-tenant evidence                   = 0
unreferenced numeric claim in report    = 0
unsupported causal claim                = 0
blocking ambiguity silently auto-picked = 0 dedicated set
```

---


## R0.4 Repoyu hiç bilmeyen geliştirici için 20 dakikalık zihinsel model

Bu projeye ilk kez giren geliştiricinin önce bütün repoyu öğrenmesi **istenmez**.

Önce yalnız şu beş cümleyi anlaması yeterlidir:

```text
1. Kullanıcıyla konuşan taraf Dima'dır.
2. İş anlamının doğrulandığı yer semantic modeldir.
3. Gerçek sayıyı LLM değil Wren/DB ve specialized engine hesaplar.
4. Her resmî iddia evidence/contract'a bağlanır.
5. Anlamadığımız yerde tahmin etmek yerine clarify / unsupported / data-gap deriz.
```

### Tek bir kullanıcı mesajı sisteme nasıl girer?

```text
USER MESSAGE
   ↓
Conversation Context
   ↓
TurnInterpreter       # Kullanıcı bu turda ne yapıyor?
   ↓
SemanticResolver      # Söylediği şey şirkette hangi gerçek kavram?
   ↓
DialoguePolicy        # Cevap mı, soru mu, analiz mi, research mü?
   ↓
RequirementLedger     # Kullanıcının maddi taleplerinin hiçbiri düştü mü?
   ↓
Planner / Research / Decision Skill
   ↓
Official Execution Boundary
   ↓
Wren / DB / specialized engine
   ↓
Evidence / Contract
   ↓
ConversationResponse / ReportDocument
```

Geliştiricinin ilk sorusu hiçbir zaman:

> “Bu cümleyi hangi regex ile yakalarım?”

olmamalıdır.

İlk soru:

> “Bu davranışın tek sahibi hangi katmandır?”

olmalıdır.

### Minimum sözlük

| Kavram | Basit anlamı |
|---|---|
| `TurnInterpretation` | Kullanıcının bu mesajla ne yaptığını anlatan typed çıktı |
| `SemanticHypothesis` | Bir ifadenin şirket verisindeki olası gerçek karşılıkları |
| `ClarificationState` | Kullanıcıya sorulmuş ve cevabı beklenen gerçek belirsizlik |
| `TopicFrame` | Konuşmanın aktif analitik konusu |
| `AnalyticsIR` | Çözülmüş standard analitik talep |
| `RequirementLedger` | Kullanıcının talep ettiği maddelerin kaybolmadığını kanıtlayan kayıt |
| `ResearchBrief` | Kompleks araştırmanın hedefleri ve sınırları |
| `ResearchRun` | Sonuçlara göre ilerleyen bounded araştırma koşumu |
| `EvidenceArtifact` | Query/table/chart/model çıktısı gibi kanıt |
| `Finding` | Kanıttan çıkarılan kontrollü bulgu |
| `HypothesisLedger` | Neden adayları ve onları destekleyen/çürüten kanıt |
| `ReportDocument` | Kanıtlı, çok bölümlü nihai rapor |
| `DecisionBrief` | “Ne yapmalıyız?” probleminin objective/constraint/evidence sözleşmesi |
| `AnalysisSpec` | Cross-surface tekrar çalıştırılabilir semantic analiz tanımı |
| `Query Contract` | Bir resmî sayının nasıl üretildiğinin audit kaydı |
| `TenantAnalyticsRuntime` | Tek request boyunca değişmeyen tenant/connection/semantic/context snapshot |

### Hangi dosyayı neden açacağım?

Yeni geliştirici önce:

```text
backend/MIMARI.md
backend/app/wren_service.py
backend/app/company_registry.py
backend/app/context.py
backend/app/schemas.py
backend/eval/cases.yaml
backend/lab/gercek_dunya.py
backend/lab/deneyim.py
```

okur.

Legacy `/ask`i baştan sona okumaz.

Bir davranışı reuse edeceği anda ilgili legacy primitive ve testlerini açar.

---

# R1 — DIMA NEDİR?

Dima yalnız bir chatbot, yalnız bir NL→SQL aracı veya yalnız bir dashboard ürünü değildir.

Nihai ürün sözleşmesi:

> **Dima, kullanıcının her mesajını önce bir konuşma turu olarak anlayan; belirsizliği tahmin ederek kapatmayan; gerektiğinde nokta atışı soru soran; şirketin semantik modelini ve gerçek verisini güvenilir analitik motor üzerinden kullanan; basit soruları hızlıca cevaplayan; karmaşık isteklerde ise sonuçları gördükçe araştırmasını geliştiren; kanıtları, tabloları, grafikleri ve kök-neden adaylarını aynı konuşma ve rapor içinde birleştiren denetlenebilir iş analistidir.**

Bu tanımın dört sonucu vardır:

```text
Conversation correctness > yalnız query correctness
Semantic layer > raw schema guessing
Evidence > ikna edici ama kanıtsız anlatı
Agentic research > tek dev SQL / tek dev prompt
```

---

# R2 — BUGÜNKÜ REPO GERÇEĞİ

Mevcut sistem değersiz veya baştan çöpe atılması gereken bir sistem değildir. Tam tersine, ciddi miktarda çalışan ve test edilmiş altyapı vardır.

Korunacak başlıca yatırımlar:

```text
auth / principal / permission
control-plane
CompanyRegistry
tenant-specific WrenService
compose / packs / MDL
cube metadata
cube SQL compiler
time / comparison primitives
Query Contract
PII / security guard'ları
viz
conversation persistence
dashboard
schedule
report
decision records
VQR / verified query altyapısı
drill / contribution / yoy / root-cause primitive'leri
tool registry
real-world corpus
metamorphic tests
experience/thread scenarios
```

### R2.1 Mevcut semantik front door neden sorunlu?

Current HEAD’de ana ağırlık birkaç dev dosyada toplanmıştır:

```text
routers/ask.py        ≈ 6.2k satır
cube_router.py        ≈ 5.1k satır
uyum.py               ≈ 2.4k satır
wren_service.py       ≈ 2.1k satır
plan_tuketici.py      ≈ 1.8k satır
plan_semasi.py        ≈ 1.0k satır
```

Sorun “dosya uzun” olması değildir.

Sorun, **aynı kullanıcı niyetinin birden fazla katmanda yeniden yorumlanmasıdır.**

Tarihsel akış kabaca:

```text
question
→ route
→ typo
→ route
→ comparison parser
→ route
→ tie breaker
→ prompt enhancer
→ ambiguity gate
→ unknown gate
→ Intent JSON
→ voting / self-consistency
→ whitelist
→ completeness
→ follow-up/refine
→ planner
→ Discovery / fallback
→ answer/presentation
```

Bir yerde doğru anlaşılan bilgi sonraki katmanda düşebildiği için sistem “çok şey biliyor ama bütün olarak güven vermiyor” hâline gelmiştir.

---


## R2.2 Repo neden sıfırdan başlanacak durumda değil?

Current HEAD çapraz denetiminde:

```text
backend/tests/ altında 507 Python test dosyası
```

vardır.

Önemli regression aileleri zaten bulunur:

```text
ask golden
gerçek dünya
metamorfik
comparison/time
entity/typo
follow-up/context
plan schema/consumer
RLS/CLS
contract spool
MCP contract
```

`app/tools.py` içinde yaklaşık 34 kayıtlı analitik/tool capability adı bulunmaktadır; aralarında:

```text
cube_sql
drill
yoy
contribution
viz
report
stats
root-cause
prescription
```

gibi V2 Research için doğrudan yeniden kullanılabilecek gövdeler vardır.

Mevcut frontend de:

```text
ReportPanel
ResultView
ReportView
PlanAdimlari
DurdurDugmesi
ContractDetailPanel
```

gibi conversation/result/report/progress/evidence primitive'lerini taşır.

Bu gerçek şu stratejiyi doğrular:

> **Yeni Dima çekirdeğini greenfield kur; çalışan motorları, testleri ve UX primitive'lerini yeniden yazma.**

---


# R3 — GEÇMİŞTEKİ HATALARIN KÖK SINIFLARI

Tek tek bug’ların arkasında tekrar eden sistemik sebepler vardır.

## R3.1 Aynı semantic kararın birden çok sahibi

Örnekler:

```text
dönem
ranking/limit
metric anlamı
follow-up context
comparison
unknown term handling
presentation intent
```

aynı anda farklı modüller tarafından yorumlanmıştır.

Sonuç:

> Aynı cümle iki farklı katmanda iki farklı anlama dönüşebilir.

V2 ilkesi:

> **Her maddi kararın tek sahibi vardır.**

---

## R3.2 Sistem kullanıcı dilini kalıba sokmaya çalıştı

Deterministik router başlangıçta hızlı ve güvenilir bir yol sağladı; fakat büyüdükçe matcher’dan parser’a dönüştü.

Türkçe:

```text
çekim
argo
eksik cümle
zamir
atıf
topic switch
correction
tenant-specific kelime
```

gibi doğal konuşma özellikleri dictionary/regex büyüterek güvenilir biçimde çözülemez.

Bu yüzden:

```text
“siyah”
“o makine”
“peki geçen sene”
“hayır müşteri değil renk”
“neden böyle”
```

gibi ifadeler sistemin doğal konuşma kapasitesinin sınırlarını ortaya çıkardı.

Kök çözüm:

```text
tek TurnInterpreter
+
deterministic semantic grounding
+
clarification
```

---

## R3.3 LLM’e yanlış görev verildi

Eski sistemde modelin örtük görevi çoğu zaman:

> “Ne pahasına olursa olsun bir sorguya ulaş.”

oldu.

Doğru görev:

> “Bu kullanıcı şu anda ne yapıyor; neyi biliyoruz; neyi bilmiyoruz; query gerçekten gerekli mi?”

Bu fark kritik.

V2’de şu çıktılar tamamen meşrudur:

```text
talk
clarify
explain current result
analyze current result
query
action proposal
unsupported
semantic gap
```

LLM query üretmeye zorlanmaz.

---

## R3.4 Belirsizlik hata gibi görüldü

Gerçek kullanıcı sorusunda bir kelimenin birden çok olası anlamı olabilir.

Örnek:

```text
“Siyah”
```

şunlardan biri olabilir:

```text
renk=Siyah
müşteri=Siyah Tekstil
ürün grubu=Siyah Seri
```

Eski kalıp sistemi birini seçmeye çalıştığında sessiz yanlış üretme riski doğar.

V2:

```text
candidate set
→ material ambiguity?
→ clarification
```

der.

Netleştirme **başarıdır**, hata değildir.

---

## R3.5 Query-first ürün tasarımı conversation’ı boğdu

Gerçek konuşma:

```text
“neden?”
“normal mi?”
“bunu yorumla”
“hayır onu demedim”
“yine OEE’ye dönelim”
“o ayda hangi makine?”
```

gibi turlar içerir.

Bunların tamamını query pipeline’ına sokmak yanlış ürün modeli oluşturdu.

yeni çekirdeğin birincil nesnesi:

```text
Conversation Turn
```

query ise araçtır.

---

## R3.6 Kompleks istekler tek plana veya tek query’ye sıkıştırıldı

Örnek:

> “Son 12 aylık üretilen ürünleri karşılaştır, üretildikleri makineler ve personellerle ilişkisini analiz et, satış performanslarını yorumla ve raporla.”

Bu tek bir query değildir.

İçinde:

```text
production comparison
sales analysis
product-machine relationship
product-personnel relationship
cross-domain grain alignment
finding synthesis
possible root-cause branch
multi-artifact report
```

vardır.

Eski statik planner uzun bir planı en başta tahmin etmeye zorlandığında henüz görmediği sonuçlar hakkında karar vermek zorundaydı.

V2:

```text
plan
→ observe
→ update findings/hypotheses
→ replan
→ observe
```

yapar.

---

## R3.7 Silent-wrong yeterince merkezi bir release blocker değildi

Bir SQL çalışabilir ve yine de kullanıcının istediği şeyin bir parçasını kaybetmiş olabilir.

Örnek:

```text
“en yüksek 5”
```

query’de `LIMIT 5` vardır ama doğru `ORDER BY` yoktur.

Syntax doğrudur.
Dry-plan geçebilir.
Cevap yanlıştır.

V2:

```text
RequirementLedger
```

ile her maddi talebin plan içinde temsil edildiğini kanıtlar.

---

## R3.8 Fallback’ler semantic eksiği gizledi

Bir yol soruyu doğru anlayamadığında başka bir yol SQL üretip sonuç döndürebildi.

Kısa vadede coverage yükselir.
Uzun vadede sistem neden yanlış yaptığını öğrenemez.

V2’de:

```text
V2 fail → legacy /ask
```

ve:

```text
Cube fail → raw Discovery
```

gibi sessiz fallback yoktur.

---

## R3.9 Knowledge/MDL çift sahipliği

Repo denetiminde OEE örneğinde metric ölçeği/aggregation hakkında MDL ile knowledge dosyaları arasında çelişkili ifadeler tespit edilmiştir.

Kök sorun:

> aynı iş kuralının iki bağımsız sahibi.

V2:

```text
metric formula / unit / aggregation → MDL/cube
business instruction                → knowledge/rules
verified NL→SQL                     → verified memory
```

ayrımını uygular.

---

## R3.10 Agentic plan sözleşmesi ile çalışan gövdeler ayrıştı

Mevcut `plan_semasi.py` ve `plan_tuketici.py` önemli bir tarihsel ders taşır:

```text
şema başka şey istiyor
çalışan tool başka input bekliyor
```

durumunda model doğru niyette olsa bile plan çalışmaz.

Ayrıca eski planner’da plan uzunluğu ve type-flow problemleri gerçek testlerle görülmüştür.

Ders:

> Agentic sistem tool listesine sahip olmakla kurulmaz; tool contract, input/output type, authority, cost, evidence ve budget birlikte doğrulanmalıdır.

---

## R3.11 Cross-surface duplication

Dashboard, schedule, report gibi yüzeyler kendi:

```text
period
query
viz
PII
contract
```

zincirlerini ayrı kurdukça aynı semantic bug birden fazla yüzeyde tekrar ortaya çıkabilir.

Bu sorun MVP öncesi refactor nedeni değildir; fakat uzun vadeli platform göçünün sebebidir.

---

## R3.12 Context/version drift

Aynı request içinde:

```text
WrenService = MDL v43
ContextProvider = v42
```

gibi bir durum sessiz yanlış üretir.

V2:

```text
TenantAnalyticsRuntime
mdl_version
context_version
```

ile request-scoped immutable snapshot kullanır.

---


# R3A — ESKİ HATALARI YAPISAL OLARAK KAPATMA MATRİSİ

Bu bölüm geliştiricinin en kritik kontrol listesidir.

Amaç:

> “Eski bug’ı hatırlıyor muyuz?” değil, **o bug sınıfının yeni mimaride tekrar doğabileceği kapıyı kapattık mı?**

Aşağıdaki her satır için üç şey birlikte gerekir:

```text
ROOT CAUSE
→ NEW OWNER / MECHANISM
→ REGRESSION / RELEASE GATE
```

| Eski hata sınıfı | Kök sebep | Yeni yapısal çözüm | Yeniden doğmasını engelleyen test/gate |
|---|---|---|---|
| Aynı soru farklı router katmanlarında farklı yorumlandı | raw text birden çok kez parse edildi | **tek TurnInterpreter** | V2 import gate + “raw question only interpreter” architecture test |
| Yeni dil varyantı yeni regex gerektirdi | matcher parser'a dönüştü | LLM surface understanding + deterministic semantic grounding | real-world/paraphrase/metamorphic corpus |
| “Siyah” yanlış kolona bağlandı | entity value ile semantic owner ayrılmadı | `SemanticMention → CandidateSet → SemanticHypothesis` | blocking ambiguity false-resolution = 0 |
| Belirsiz soru yine de SQL'e zorlandı | query-only output contract | `DialoguePolicy: CLARIFY` first-class | clarification SQL count = 0 |
| “Peki ne yapmalıyız?” sosyal mesaj sanıldı | keyword gate semantik authority oldu | safe pre-gate yalnız kapalı sınıflar; geri kalanı TurnInterpreter | social false-positive regression |
| `top 5`te limit korundu ama doğru sıralama düştü | sibling state / completeness eksik | `RequirementLedger` | ranking + direction + limit dedicated = %100 |
| comparison iki dönemi tek range'e düştü | time/compare tek sahipte değildi | typed `ResolvedComparison` | explicit A-vs-B regression = %100 |
| follow-up'ta metric/dimension kayboldu | SQL/text edit ile refinement | prior **IR + slot delta** | follow-up correctness / slot preservation |
| “o makine / o ay” kayboldu | conversation yalnız son query idi | `TopicFrame + FocusState + artifact anchors` | referential flow tests |
| konu değiştirip eski konuya dönülemedi | tek `last_ir` | topic stack | topic switch/resume gate |
| user correction yeni soru sanıldı | repair speech-act yoktu | `USER_REPAIR` + typed diff | repair unrelated-slot preservation = %100 |
| LLM doğru metric'i bulsa sonraki gate reddetti | interpretation birden çok owner | resolver/ledger/planner sınırları | stage trace + gold semantic refs |
| self-consistency k=3 maliyetli ama aynı hatayı çoğalttı | doğruluk yerine oy çoğunluğu | strong model k=1 + structured validation | field accuracy + result correctness |
| Discovery semantic gap'i örttü | fail-open fallback | `SEMANTIC_GAP / UNSUPPORTED` terminal outcomes | no raw-SQL fallback architecture test |
| verified query eski tanımla replay edildi | memory truth ile current semantics ayrıştı | verified examples + `context_version`; canonical spec replay | stale-memory and definition-change tests |
| knowledge rule metric formülüyle çelişti | iki truth owner | metric formula/unit/aggregation yalnız MDL/cube | ContextConsistencyGate |
| context v42, engine v43 kullanıldı | ayrı mutable cache | immutable `TenantAnalyticsRuntime` | version mismatch fault injection |
| stock agent tool principal taşımadan query çalıştırdı | LLM toolset execution authority oldu | official execution yalnız Dima `WrenService` | principal propagation = %100 |
| uzun statik plan yanlış adımlara saplandı | result görülmeden tüm araştırma tahmin edildi | seed plan → observe → replan | adaptive branch eval |
| plan şeması tool inputuyla uyuşmadı | tool contract typed/declarative değildi | Tool Contract + task validator | schema/tool compatibility CI |
| karmaşık soru tek dev SQL'e sıkıştı | query-first architecture | ResearchBrief + ResearchRun | complex goal/evidence coverage |
| grafikte korelasyon görüldü, “sebep” denildi | epistemik etiket yoktu | HypothesisLedger + Finding kind | unsupported causality = 0 |
| “ne yapalım?” LLM tavsiyesine dönüştü | recommendation authority tanımsız | evidence + playbook/model/policy | unsupported recommendation = 0 |
| müşteri ziyaret sırasını model kafadan verdi | optimizasyon LLM'e bırakıldı | scoring + VRP/constraint solver | hard constraint violation = 0 |
| boş sonuç “veri yok” diye genellendi | query outcome ile dataset claim ayrılmadı | epistemic response policy | empty-result wording regression |
| safety row cap `top-N` semantiği sanıldı | semantic limit ile transport cap karıştı | `ranking.limit` ≠ `row_cap` | truncation/ranking tests |
| chart üretildiği için cevap tamam sanıldı | chart-first ürün | text-first ConversationResponse + evidence | content/UX acceptance suite |
| dashboard/report/schedule farklı query mantığı kullandı | cross-surface duplication | MVP sonrası AnalysisSpec/Runner | same-spec cross-surface parity |
| source badge `cube=LLM-free` dedi | planning/interpreter/execution ayrımı telemetry'de yoktu | interpreter/planner/engine ayrı telemetry | frontend source-label regression |
| agent bütün tool'lara erişti | least-authority yok | scoped worker/toolbelt | tool authorization test |
| long run sessiz spinner oldu | run state UI sözleşmesi yok | progress events + cancel/answer-now | progress silence SLO |
| rapor sayı uydurdu | narrative ile evidence ayrılmadı | Finding evidence refs + ReportDocument | unreferenced numeric claim = 0 |

## R3A.1 Bu matris nasıl kullanılacak?

Bir bug geldiğinde doğrudan:

```text
if user_phrase == "..."
```

ekleme.

Önce matriste hangi **hata sınıfına** ait olduğunu belirle.

Örnek:

> “Koyu siyah ürünleri göstermiyor.”

Yanlış yaklaşım:

```text
"koyu siyah" sözlüğe ekle
```

Doğru inceleme:

```text
TurnInterpreter mention doğru mu?
CandidateSet'te gerçek value var mı?
Resolver exact/fuzzy provenance doğru mu?
Blocking ambiguity var mı?
RequirementLedger filter'ı plan içinde görüyor mu?
```

Kök katman düzeltilir.

## R3A.2 Yeni mimaride de aynı anti-pattern nasıl geri dönebilir?

Yeni dosya adı eski hatayı otomatik çözmez.

Şunlar **aynı eski mimarinin yeni isimle geri gelmesidir**:

```text
interpreter.py içinde yüzlerce özel regex
resolver.py'nin raw question parse etmesi
planner'ın “kullanıcı aslında bunu demiştir” diye semantic seçim yapması
ResearchWorker'ın raw user prompt'tan metric seçmesi
finalizer'ın eksik requirement'ı kendi tahminiyle tamamlaması
UI'ın eksik context'i client-side heuristic ile seçmesi
```

Code review bu örüntülere özellikle bakmalıdır.

---

# R4 — NEDEN SIFIRDAN YENİ REPO DEĞİL?

Üç seçenek değerlendirildi.

## A — Tam greenfield repo

Artı:

```text
temiz import graph
bağımlılık özgürlüğü
```

Eksi:

```text
auth yeniden bağlanır
tenant/runtime yeniden bağlanır
Wren/compose/MDL yeniden bağlanır
security/contracts yeniden bağlanır
eval corpus taşınır
frontend sözleşmesi tekrar kurulur
```

İlk haftayı asıl ürün probleminden uzaklaştırır.

## B — Legacy’yi büyük refactor edip sonra V2

Artı:

```text
tek kod tabanı
```

Eksi:

```text
MVP gecikir
regresyon alanı büyür
ask/cube_router/uyum sürekli hareketli hedef olur
```

## C — Mevcut repo içinde greenfield V2 island

**Seçilen yol.**

```text
legacy /ask         → freeze
new /ask-v2         → clean semantic/conversation core
auth/tenant/Wren    → reuse
MDL/packs           → reuse
eval/tests          → reuse
```

Bu:

```text
greenfield brain
+
brownfield reliable infrastructure
```

yaklaşımıdır.

Yeni repo ancak isolation spike gerçekten mevcut uygulama içinde sınır kurulamadığını kanıtlarsa değerlendirilir.

---

# R5 — YENİ ÇEKİRDEKTE KORUNACAK MEVCUT YATIRIMLAR

## R5.1 WrenService

Korunur.

Rol:

```text
tenant-bound semantic engine
cube compile
dry-plan
execute
schema/MDL
principal-aware boundary
```

WrenService:

```text
kullanıcı dilini anlamaz
conversation yönetmez
final anlatı üretmez
```

---

## R5.2 Cube semantic cebri

Korunur.

Özellikle:

```text
metric
dimension
filter
period
order
limit
having
discrete periods
window
derived metric
blend
```

yatırımı çöpe atılmaz.

V2 CubePlanner bu engine’in temiz ön yüzü olur.

---

## R5.3 Time/comparison primitives

`mali_takvim`, comparison algebra ve kanıtlanmış tarih fonksiyonları yeniden yazılmaz.

Gerekirse nokta atışı pure extraction yapılır.

---

## R5.4 Existing analytical tools

Repo’da zaten çalışan önemli araçlar vardır:

```text
yoy
contribution
drill
kok_neden
stats
ilkeller
viz
report
```

Research Mode bunları typed adapter ile yeniden kullanır.

Eski planner authority’si taşınmaz; çalışan tool gövdeleri korunur.

---

## R5.5 Query Contract / evidence

Dima’nın en önemli farklılaştırıcılarından biridir.

Her resmi analitik cevap:

```text
ne soruldu?
hangi semantic model?
hangi plan?
hangi SQL?
hangi sonuç?
hangi sürüm?
```

kanıtını taşımalıdır.

Bu sözleşme pilot hardening'e ertelenmez. İlk gerçek V2 query'nin çalıştığı **Day 3** itibarıyla `MinimumQueryContract` zorunludur:

```text
question / normalized request ref
AnalyticsIR
planner id/version
mdl_version
context_version
execution_id
executed SQL
result_hash
tenant_id
principal / execution identity
```

`QueryContract` query/execution seviyesinde immutable'dır: **bir contract = bir execution**. Bir `ConversationResponse`, `EvidenceArtifact`, `Finding` veya `ReportSection` birden fazla execution'a dayanıyorsa `QueryContract[]` referansları taşır. Bu nedenle sistem “bir cevap = bir SQL” varsayımına sahip değildir; ikinci execution mevcut contract'ı mutate etmez, yeni contract üretir.

Day 12'de yapılan iş contract'ı ilk kez eklemek değil, **hardening**'dir:

```text
research_run_id / task_id
finding refs
artifact refs
telemetry enrichment
durability / spool / sealed-pending-flush
```

Kural:

> `MinimumQueryContract` oluşmadan data-touching cevap `official/verified` statüsüne geçemez.

---

## R5.6 Test/eval yatırımı

Repo zaten:

```text
eval/cases.yaml
gercek_dunya.py
dil_ozellikleri.py
senaryo_uretec.py
metamorfik.py
deneyim.py
binlerce test
```

taşımaktadır.

V2 test sistemi sıfırdan kurulmaz.

---


# R5A — TEK DIMA ÇEKİRDEĞİ, ÇOK SAYIDA GOVERNED DECISION SKILL

İş fikirleri çoğaldıkça yapılabilecek en tehlikeli hata şudur:

```text
AI Teklif Motoru      → ayrı mini ürün
AI Stok Motoru        → ayrı mini ürün
AI Bakım Motoru       → ayrı mini ürün
AI Rota Motoru        → ayrı mini ürün
...
```

Böyle yapılırsa birkaç ay sonra tekrar:

```text
ayrı context
ayrı agent
ayrı metric tanımı
ayrı security
ayrı report
ayrı conversation
```

sahipleri oluşur.

Bu, eski `/ask` probleminin ürün seviyesinde yeniden doğmasıdır.

## R5A.1 Bağlayıcı ürün mimarisi

Tek çekirdek:

```text
DIMA CORE
├─ Conversation
├─ Semantic Grounding
├─ Standard Analytics
├─ Research / Evidence
├─ Security / Tenant
├─ Contracts / Audit
└─ UX / Report
```

Bunun üstüne capability engine'leri:

```text
ENGINE LAYER
├─ AnalyticsEngine       → Wren / deterministic analytics
├─ ForecastEngine        → zaman serisi / prediction
├─ OptimizationEngine    → CP-SAT / routing / LP-MIP
├─ CausalEngine          → uygun olduğunda causal inference
├─ SimulationEngine      → what-if / discrete-event
├─ DocumentEngine        → RFQ / sözleşme / şartname
├─ VisionEngine          → kalite görüntüsü gibi özel CV modelleri
└─ WorkflowEngine        → approval / action
```

Ve en üstte domain skill/solution pack'leri:

```text
SOLUTION SKILLS
├─ Manufacturing Performance
├─ Manufacturing Planning
├─ Maintenance / Quality
├─ Procurement
├─ Commercial / Quotation / Pricing
├─ Inventory
├─ Logistics
├─ CRM / Finance
└─ Sustainability / Compliance
```

> **Skill yeni bir Dima değildir. Skill, mevcut Dima çekirdeğinin kullandığı typed ve denetimli bir kabiliyettir.**

## R5A.2 `DecisionSkillSpec`

İkinci gerçek decision skill ortaya çıktığında ortak bir sözleşme çıkarılır; **ilk skill'den önce generic framework inşa edilmez.**

Hedef sözleşme:

```python
class DecisionSkillSpec(BaseModel):
    id: str
    domain: str
    capability: str

    engine_kind: Literal[
        "analytics",
        "forecast",
        "optimization",
        "causal",
        "simulation",
        "document",
        "vision",
        "workflow",
    ]

    required_semantics: list[str]
    required_data: list[str]
    optional_data: list[str]

    input_schema: str
    output_schema: str
    evidence_policy: str
    permission_policy: str
    budget_policy: str

    artifact_types: list[str]
    eval_suite: str
    readiness_policy: str
```

Bu nesne kullanıcı metnini parse etmez.

Akış:

```text
Conversation / Research / Decision
→ hangi skill gerekli?
→ readiness gate
→ engine adapter
→ evidence / plan / recommendation
→ common finalizer
```

## R5A.3 Skill'lerin ayrı repo/microservice olması gerekmez

İlk aşama:

```text
aynı repo
aynı deploy
typed adapters
lazy optional dependencies
```

olmalıdır.

Microservice ancak:

```text
ayrı ölçek ihtiyacı
ayrı güvenlik sandbox'ı
GPU/vision workload
ayrı release cadence
```

gerçekten kanıtlanırsa düşünülür.

**“Temiz mimari böyle olur” diye erkenden servis parçalama yasaktır.**

## R5A.4 İş fikirlerinin ortak motorlara indirgenmesi

| Çözüm | Esas motorlar |
|---|---|
| Teklif / ihale | document + cost model + capacity + scoring/optimization |
| Üretim planlama / iş emri sıralama | optimization |
| Satın alma | scoring + policy + document intelligence |
| Fiyatlama | cost + demand/elasticity + optimization |
| Kapasite satışı | forecast + capacity + pricing/optimization |
| Stok / yedek parça | forecast + inventory optimization |
| Bakım | research + anomaly/prediction + playbook |
| Kalite | SPC + vision/data + root-cause |
| Rota / yük | routing + packing optimization |
| Vardiya | workforce optimization |
| Enerji | forecast + production optimization |
| Fire / muda | analytics + SPC + research/root-cause |
| Sözleşme riski | document + policy |
| Tahsilat | scoring/prediction + prioritization |
| Talep tahmini | forecast |
| Kampanya | segmentation + causal/uplift when available |
| Müşteri kârlılığı | deterministic cost allocation + analytics |

Bu nedenle 15–25 iş fikri 15–25 ayrı mimari üretmez.

---

# R5B — OPEN-SOURCE / STANDART KULLANIM POLİTİKASI

Dima'nın mimarisi yeni kütüphane listesine göre şekillenmez.

Kural:

> **Önce capability contract, sonra engine seçimi.**

Bir open-source araç ancak:

```text
1. kanonik bir capability'ye hizmet ediyorsa,
2. lisansı uygunsa,
3. deterministic/evidence contract'ı kurulabiliyorsa,
4. mevcut engine'i gereksiz yere çoğaltmıyorsa,
5. gerçek acceptance scenario'yu ileri taşıyorsa
```

ürüne girer.

## R5B.1 Şimdi / çekirdek kurtarma sırasında

### Wren

Zaten ana semantic engine.

Güncel `wren-pydantic` context/recall/dry-plan/query araçları sunuyor; fakat ilk Core MVP bunun kurulmasına bağımlı olmayacaktır.

MVP:

```text
mevcut LLM provider wrapper
+
WrenService.schema()
+
mevcut WrenService execution
```

ile çalışabilir.

Bu hız açısından önemlidir.

### SQLGlot

Repo zaten `wren_service.py` içinde SQLGlot kullanıyor.

Dolayısıyla:

```text
“SQLGlot ekle”
```

yeni dependency işi değildir.

Sonraki kullanımlar:

```text
legacy SQL import/analysis
dialect translation
AST validation
column-lineage cross-check
```

olabilir.

Semantic lineage'ın sahibi yine Dima/MDL'dir.

### Promptfoo

Dev/eval aracı olarak değerlidir; production dependency değildir.

Mevcut Dima'nın zaten:

```text
507 Python test dosyası
real-world corpus
metamorphic tests
experience/thread scenarios
golden eval
```

yatırımı vardır.

Bu nedenle Promptfoo:

```text
mevcut eval'i değiştirmez
→ provider/prompt/agent regression görünürlüğünü artırır
```

rolünde denenebilir.

Core MVP blocker değildir.

### DuckDB

Repo/demo yolunda zaten kullanılıyor.

Dosya/POC onboarding için:

```text
CSV / Parquet / küçük local dataset
```

üzerinde çok değerlidir.

Yeni ana warehouse değildir.

---

## R5B.2 Manufacturing Core kanıtlandıktan hemen sonra

### ISO 22400-2

Manufacturing KPI pack için güçlü referanstır.

Güncel resmi durum:

```text
ISO 22400-2:2014 yayınlanmış sürüm
+
bir amendment
+
Edition 2 taslağı (ISO/DIS 22400-2) geliştirme aşamasında
```

Dima:

```text
ISO-aligned KPI catalog
```

hedefleyebilir.

Fakat:

```text
standart metnini/formüllerini lisanssız topluca kopyalama
```

yapılmaz.

Lisanslı standart incelemesi ve legal/product attribution gerekir.

### SPC + change-point (`ruptures`)

İmalat araştırmasının doğal eklentisi:

```text
control chart
Western Electric rules
EWMA / CUSUM
change-point
```

Kullanıcı dili:

> “Ne zaman bozulmaya başladı?”

sorusuna güçlü deterministic araç sağlar.

Change-point “neden” değildir; Research Worker'ın yeni branch tetikleyicisidir.

### OR-Tools

Dima'nın ilk genel OptimizationEngine adayıdır.

Uygun işler:

```text
job-shop / production sequencing
shift scheduling
vehicle routing / visit planning
capacity assignment
```

LLM objective ve constraint'leri konuşmadan çıkarabilir;
çözümü solver hesaplar.

### StatsForecast

İlk ForecastEngine adayıdır.

Uygun işler:

```text
demand
capacity
spare parts
cash / collection horizon
downtime counts
```

Forecast resmi cevap olmak için:

```text
backtest
error metric
prediction interval
model/version
```

taşımalıdır.

### WeasyPrint

`ReportDocument` stabil olduktan sonra HTML/CSS → PDF için hızlı adaydır.

PDF export, Research MVP'nin önüne geçirilmez.

---

## R5B.3 Sonraki, koşullu motorlar

### SimPy

What-if / discrete-event simulation.

Örnek:

> “Hat hızını %10 artırırsam kuyruk, WIP ve termin ne olur?”

Gerçek proses modeli olmadan kullanılmaz.

### SALib

Simulation/model üstünde sensitivity.

> “Sonucu en çok hangi varsayım oynatıyor?”

sorusuna yarar.

Tek başına karar motoru değildir.

### DoWhy / EconML

Causal analysis için.

Korelasyonu otomatik sebebe dönüştürmez.

Gereken:

```text
causal graph / assumptions
confounder bilgisi
uygun intervention/observational design
```

olmalıdır.

### Node-RED / PLC4X / OPC-UA adapter

OT ingestion için değerlidir.

Tercih edilen mimari:

```text
factory edge connector
→ outbound secure stream
→ Dima ingestion
```

Cloud Dima'nın PLC ağlarına doğrudan inbound erişimi varsayılmaz.

### Process mining

Process mining yüksek değer taşıyabilir.

Ancak PM4Py OSS lisans sınırı sebebiyle proprietary core'a doğrudan dahil edilmeden önce ayrı lisans incelemesi gerekir.

Gerekirse:

```text
harici servis
commercial license
veya
açık literatürden kendi implementation
```

değerlendirilir.

---

## R5B.4 Şimdilik ertelenecek altyapılar

```text
TimescaleDB
Perspective
authentik/Keycloak migration
Arelle/XBRL
PyMC-Marketing
xyflow root-cause canvas
full PLC connector suite
```

Bunlar kötü fikir oldukları için değil, **aktif acceptance scenario henüz bunları zorunlu kılmadığı için** ertelenir.

Özellikle mevcut frontend ve current Postgres/DuckDB/Wren altyapısı MVP için yeterliyse yeni platform dependency eklenmez.

---

# R5C — BUSINESS SOLUTION PACK STRATEJİSİ

Dima pazarda:

```text
“genel AI platformu”
```

diye satılmamalıdır.

Tek çekirdeğin üstünde dar ROI cümleleri olan solution pack'ler satılabilir.

## İlk imalat paketi

**Manufacturing Performance Advisor**

Satış cümlesi:

> “Hangi makine/ürün/vardiyada performans kaybettiğini, muhtemel nedenlerini ve sonraki kontrolü konuşarak bul.”

İçerik:

```text
OEE
fire/muda
downtime
quality
throughput
machine / line / shift
root-cause research
```

Bu Dima'nın mevcut yatırımıyla en hızlı gerçek değer yoludur.

## İkinci imalat skill'i

**Job / Production Sequencer**

Satış cümlesi:

> “Siparişleri hangi makinede hangi sırayla çalıştıracağını termin ve setup maliyetleriyle hesapla.”

Bu skill Dima'nın ilk gerçek genel OptimizationEngine'ini kanıtlayabilir.

## Sonraki para-karar skill'leri

```text
Procurement Decision
Quotation / Bid Decision
Inventory Decision
Energy Optimization
Maintenance Decision
```

sırayla gerçek müşteri verisi ve ROI'ye göre açılır.

**Bunlar ayrı ürün beyinleri değil, aynı Dima'nın solution pack'leridir.**

---

# R5D — SEMANTIC ASSET CONTRACT: KÜPLER, PACK'LER VE ELLE KÜRASYONLU BİLGİ KORUNACAK

Dima'nın mevcut cube/MDL ve pack yatırımı legacy yükü değildir; **ürünün doğrulanmış iş bilgisi ve en kıymetli IP katmanlarından biridir.** V2/agentic geçiş bu yatırımı yeniden üretmez, sessizce silmez ve LLM'e devretmez.

Bağlayıcı zincir:

```text
ELLE KÜRASYONLU SEMANTİK BİLGİ
        ↓
source pack
+ module pack
+ sector pack
+ intersection pack
+ company override
        ↓
compose / validate
        ↓
versioned Tenant Semantic Model
        ↓
Wren MDL / Dima Cube Catalog
        ↓
Conversation / Analytics / Research / Decision
```

`intersection pack`, sektör ile belirli proses/alt-sektör kesişimini taşır; örneğin genel manufacturing bilgisinden daha dar `plastics-manufacturing` semantiği. Mevcut repoda bu katmanın fiziksel dosya adı farklı olabilir; burada anlatılan şey **sahiplik katmanıdır**, zorunlu klasör adı değildir.

## R5D.1 Üç semantic sınıf ve tek sahip ilkesi

### A — Computational Semantics

```text
metric formula
aggregation
additivity / semi-additivity
grain
unit
canonical time
relationships
allowed joins
```

**Authority:** MDL / cube semantic model.

LLM, knowledge rule veya verified example bunları override edemez.

### B — Business Semantics

```text
canonical label
terminology
synonyms
descriptions
business thresholds
company vocabulary
standard provenance
business instructions
```

**Authority:** semantic/domain packs + açık company override politikası.

Örnek:

```text
“zayiat” → verified company synonym of scrap
“siyah hat” → verified company alias of LINE_03
```

### C — Analytical Semantics

Bir metric'in yalnız nasıl hesaplandığını değil, **hangi doğrulanmış analitik yollarla incelenebileceğini** tarif eder:

```text
decomposition
diagnostic_dimensions
meaningful_comparisons
supported_drill_paths
directionality
analysis affordances
```

Örnek OEE metadata'sı:

```text
metric: oee
decomposition:
  - availability
  - performance
  - quality
diagnostic_dimensions:
  - machine
  - product
  - shift
  - operator
  - downtime_reason
direction: higher_is_better
```

Bu metadata Research Agent'e **analytical affordance** verir; rigid plan vermez. Agent sonuçları gördükçe uygun yolu seçer. `OEE düşük → mutlaka sabit 8 adım` gibi yeni bir hard-coded planner kurulmaz.

## R5D.2 Standard metric ile company-adjusted metric ayrımı

Standard veya canonical metric sessizce şirket tanımıyla değiştirilmez.

Örnek:

```text
oee_standard
oee_company_adjusted
```

ayrı semantic kimlikler olabilir.

Company override kolayca şunları değiştirebilir:

```text
label
synonym
display name
approved terminology
presentation
açıkça company-owned threshold/default
```

Fakat şunlar ancak explicit semantic override + yeni version + validation + parity/regression testi ile değişebilir:

```text
formula
aggregation
grain
unit
relationship
canonical time
```

Bir standarda hizalanan metric için provenance en az:

```text
standard_family
semantic definition/version
pack owner
verification status
```

taşır. Standard-aligned ile company-custom hesap aynı isim altında sessizce birleşmez.

## R5D.3 Semantic Preservation Audit — V2'ye geçiş kapısı

V2 yeni semantic truth üretmeden önce mevcut yatırımı envanterler:

```text
existing cubes / MDL
metric metadata
relationships
source/module/sector/intersection packs
knowledge rules
company overrides
verified examples
```

Her asset:

```text
KEEP
FIX
DEPRECATE_WITH_REASON
```

olarak sınıflanır ve canonical owner atanır.

Zorunlu kontroller:

```text
existing certified metric silently lost      = 0
formula/unit/grain unintended change          = 0
unapproved pack composition conflict          = 0
verified company synonym loss                 = 0
critical OEE semantic parity                  = 100%
Research Agent raw DB schema bypass           = 0
same semantic rule with two independent owners = 0
```

Generated runtime (`wren-project*`, composed `mdl.json` vb.) authoring truth değildir. Değişiklik canonical pack/override katmanında yapılır, compose edilir, validate edilir ve immutable runtime olarak publish edilir.

## R5D.4 Cube'ların agentic sistemdeki nihai rolü

Agentic mimari cube'ların rolünü azaltmaz; tersine onları **doğrulanmış hesap aracı** yapar.

```text
LLM / AnalystSupervisor
→ hangi analizin gerekli olduğuna karar verir
→ canonical semantic refs ile typed task üretir
→ CubePlanner / governed tool
→ Wren / DB gerçek hesabı yapar
→ Evidence / Contract
```

Research Worker:

```text
“hangi tabloyu join etsem?”
```

diye fiziksel şema tahmini yapmaz. Şunu sorar:

```text
“Bu canonical metric'i açıklamak için hangi doğrulanmış decomposition,
dimension ve relationship path kullanılabilir?”
```

Bu nedenle nihai ilke:

> **Dil LLM'in; iş ve hesap hakikati semantic katmanın; sayı Wren/DB'nin; karar ise kanıtlı agent + uygun hesap motorunun.**

---

# R6 — NİHAİ HEDEF MİMARİ

```text
USER TURN
   ↓
Conversation Context Assembler
   ↓
TurnInterpreter
   ↓
TurnInterpretation
   ↓
Reference + Semantic Hypothesis Resolver
   ↓
DialoguePolicy
   ├─ TALK
   ├─ CLARIFY
   ├─ EXPLAIN EXISTING
   ├─ ACTION PROPOSAL
   └─ ANALYTIC
         ↓
      AnalyticalRequest
         ↓
      Semantic Resolver
         ↓
      AnalyticsIR
         ↓
      RequirementLedger
         ↓
      Complexity / Capability
      ├─ STANDARD
      │    ↓
      │ CubePlanner
      │    ↓
      │ WrenService
      │
      └─ RESEARCH
           ↓
        ResearchBrief
           ↓
        AnalystSupervisor
           ↓
        small seed plan
           ↓
        execute / observe / replan
           ↓
        EvidenceArtifact
        Finding
        HypothesisLedger
           ↓
        ReportDocument

               ↓
        Query Contract / Evidence
               ↓
        Conversation Finalizer
               ↓
      text-first response
      optional chart/table
               ↓
        Topic/Focus update
```

---



## R6.0 Nihai mimari — katmanlar, tek sahipler ve güven sınırları

Aşağıdaki katmanlar “klasör yapısı” değil, **karar sahipliği** sınırlarıdır.

### Katman 0 — Identity / Tenant Runtime

**Sahibi:**

```text
auth
CompanyRegistry
TenantAnalyticsRuntime
```

**Karar verir:**

```text
hangi tenant?
hangi principal?
hangi connection?
hangi MDL/context version?
hangi fiscal/timezone context?
```

**Asla karar vermez:**

```text
kullanıcı ne demek istedi?
hangi metric?
hangi chart?
```

Çıktı immutable request snapshot'tır.

---

### Katman 1 — Conversation Context

**Sahibi:**

```text
ConversationState
TopicFrame
FocusState
ClarificationState
artifact anchors
```

**Girdi:**

```text
user turn + current thread
```

**Çıktı:**

```text
bounded ConversationContext
```

Burada raw SQL semantic memory değildir.

---

### Katman 2 — Turn Understanding

**Tek sahibi:** `TurnInterpreter`

**Çıktı:**

```text
TurnInterpretation
dialogue_act
references
mentions
analytical_request?
user_repair?
presentation_request?
unresolved
```

Bu katman doğal dili anlar.
Canonical data modelini **seçmez**.

---

### Katman 3 — Semantic Grounding

**Sahibi:** `SemanticResolver`

**Girdi:**

```text
mentions
current schema/context
safe entity index
thread-local confirmed bindings
```

**Çıktı:**

```text
resolved semantic refs
CandidateSet / SemanticHypothesis
ambiguities
semantic gaps
```

Bu katman “hangi gerçek şirket kavramı?” sorusunu cevaplar.

---

### Katman 4 — Dialogue Policy

**Sahibi:** `DialoguePolicy`

Karar ağacı:

```text
TALK
CLARIFY
EXPLAIN_EXISTING
ANALYTIC_STANDARD
ANALYTIC_RESEARCH
DECISION
ACTION
UNSUPPORTED
```

Burada “query gerekli mi?” kararı verilir.

---

### Katman 5 — Analytical Contract

Analitik turda:

```text
AnalyticalRequest
→ AnalyticsIR
→ RequirementLedger
```

Bu katman kullanıcı talebinin **tamlığını** sahiplenir.

Planner yeni requirement ekleyemez veya silemez.

---

### Katman 6A — Standard Analytics

**Sahibi:** `CubePlanner`

```text
AnalyticsIR
→ CubeQuery / AnalysisSpec
→ WrenService
```

Hızlı, deterministic ve mümkün olduğunca tek/az query.

---

### Katman 6B — Research / Analyst

**Sahibi:** `AnalystSupervisor`

```text
ResearchBrief
→ seed tasks
→ governed tools
→ EvidenceArtifact
→ Finding / Hypothesis
→ replan
→ ReportDocument
```

Supervisor semantic owner değildir.
Tool worker final user cevabının sahibi değildir.

---

### Katman 7 — Decision / Recommendation / Optimization

Research evidence üstüne:

```text
DecisionBrief
→ Playbook / Policy / Predictive Model / Optimizer
→ RecommendationSet / OptimizedPlan
```

LLM burada da “hesap motoru” değildir.

---

### Katman 8 — Official Execution Boundary

**Tek resmi authority:** Dima execution boundary.

```text
dry-plan
policy
RLS/CLS
principal
timeout
execute
result validation
```

Stock agent tool'u bu sınırı atlayamaz.

---

### Katman 9 — Evidence

Her data-touching adım:

```text
QueryContract / ExecutionArtifact
```

üretir.

Research:

```text
EvidenceArtifact
Finding
Hypothesis
```

ile bağlanır.

Decision:

```text
evidence refs
```

taşır.

---

### Katman 10 — Conversation Finalizer / UX

Finalizer:

```text
insani cevap
scope / assumptions
chart/table/report artifact
evidence actions
next actions
```

üretir.

Finalizer sayı keşfetmez.
Semantic boşluğu kapatmaz.
Planner düzeltmez.

---

### Katman 11 — Observability / Evaluation

Her turn:

```text
thread
turn
trace
spans/stages
versions
latency
cost
failure taxonomy
feedback
```

ile ölçülür.

Bu katman mimarinin “gerçekten daha iyi” olduğunu kanıtlar.

---

## R6.0.1 Nihai bağımlılık yönü

```text
UI
 ↓
ask-v2 / conversation API
 ↓
Conversation Orchestrator
 ├── Context
 ├── TurnInterpreter
 ├── SemanticResolver
 └── DialoguePolicy
       ↓
       ├── Standard Analytics
       │      ↓
       │   CubePlanner
       │
       ├── Research
       │      ↓
       │   AnalystSupervisor
       │      ↓
       │   read-only tools
       │
       └── Decision
              ↓
           models / solvers / playbooks
              ↓
          Dima Execution Boundary
              ↓
             Wren
              ↓
              DB

All data-touching paths
        ↓
Evidence / Contracts
        ↓
Conversation UI
```

### Yasak ters bağımlılıklar

```text
WrenService → TurnInterpreter             YOK
CubePlanner → raw user question           YOK
ResearchWorker → raw user semantic parse  YOK
Finalizer → DB                            YOK
Frontend → metric ownership rule          YOK
ReportWorker → ungoverned query           YOK
Optimizer → invent objectives             YOK
```

---

## R6.0.2 Turn state machine

```text
RECEIVED
  ↓
CONTEXT_BOUND
  ↓
INTERPRETED
  ↓
GROUNDED
  ↓
┌───────────────┬─────────────┬──────────────┬───────────────┐
│ TALK/EXPLAIN  │ CLARIFY     │ ANALYTIC     │ DECISION      │
│               │             │              │               │
│ FINALIZE      │ WAIT_USER   │ PLAN/RUN     │ RESEARCH first│
└──────┬────────┴──────┬──────┴──────┬───────┴───────┬───────┘
       │               │             │               │
       └───────────────┴─────────────┴───────────────┘
                           ↓
                     RESPONSE_SEALED
```

Bir turn terminal olmayan durumda yalnız:

```text
WAIT_USER
RUNNING_RESEARCH
WAIT_APPROVAL
```

olabilir.

---

## R6.0.3 Research state machine

```text
CREATED
→ BRIEF_VALIDATED
→ SEED_PLANNED
→ RUNNING
   ├─ EVIDENCE_ADDED
   ├─ HYPOTHESIS_UPDATED
   ├─ REPLANNED
   └─ NEEDS_CLARIFICATION
→ SYNTHESIZING
→ REPORT_READY
→ DONE
```

Alternatif terminaller:

```text
PARTIAL_BUDGET
PARTIAL_DATA_GAP
CANCELLED
FAILED_INFRA
UNSUPPORTED
```

“PARTIAL” bir başarısızlık maskesi değildir; kullanıcıya ne tamamlandı/ne eksik açıkça söylenir.

---

## R6.1 Capability ladder — ürünü hangi sırayla gerçekten “çalışır” sayacağız?

### L0 — Boot / isolation

Kullanıcı senaryosu yoktur; geliştirici senaryosu vardır:

> `/ask-v2` ayağa kalkıyor, fakat legacy `/ask`i çağırmadan tenant ve Wren altyapısını kullanabiliyor.

Başarı:

```text
V2 boot
tenant resolve
Wren smoke
legacy untouched
```

### L1 — Conversational Core

Kullanıcı:

> “Bu ay ciro ne?”

> “Siyah için fire.”

> “Hayır, müşteri değil renk.”

> “Bunu yorumla.”

Dima:

```text
doğru turn type
gerekirse clarification
doğru standard query
follow-up/repair
gereksiz query yok
```

### L2 — Reliable Standard Analytics

Kullanıcı:

> “Son üç ay en çok fire veren 5 makineyi önceki üç ayla kıyasla.”

Dima:

```text
metric
population
time A/B
comparison
ranking
limit
```

gereksinimlerinin hiçbirini düşürmeden doğru sonuca gider.

### L3 — Research/Analyst Mode

Kullanıcı:

> “Son 12 ay ürünleri karşılaştır, makineler ve personellerle ilişkisini incele,
> satış performansını yorumla ve raporla.”

Dima:

```text
multi-step
multi-query
result-aware replan
relationship analysis
root-cause candidate investigation
multi-artifact report
```

yapar.

### L4 — Pilot-grade trust

Aynı sistem gerçek tenant'ta:

```text
principal
PII
contract
context version
rollback
persistence
telemetry
```

ile güvenilir çalışır.

### L5 — Full Product / North Star

Dima artık yalnız “doğru cevap veren endpoint” değildir.

Kullanıcı tek chat içinde:

```text
sorar
netleştirir
araştırmayı izler
grafiğe tıklar
aynı bulgu üzerinden derinleşir
raporu revize ettirir
kanıtını açar
raporu kaydeder/paylaşır
sonraki soruya aynı topic context'iyle devam eder
```

ve sistem conversation, research, evidence ve BI yüzeyleri arasında bağlam kaybetmez.

---

## R6.2 North-Star kullanıcı deneyimi — finalde nasıl görünmeli?

### A — Basit soru

Kullanıcı:

> “Bu ay ciro?”

UI:

```text
[Doğrudan cevap cümlesi]
₺X,XX M

Dönem: Eylül 2026
Metrik: Ciro

[opsiyonel küçük trend]
[Neden böyle?] [Müşteri bazında aç] [Geçen ayla kıyasla]
```

Chart zorunlu değildir.

### B — Belirsizlik

Kullanıcı:

> “Siyah için fire.”

UI:

```text
“Siyah” ile hangisini kastediyorsun?

[ Renk = Siyah ]
[ Müşteri = Siyah Tekstil ]
[ Başka bir şey ]
```

Bu ekranda:

```text
SQL/query = 0
```

olmalıdır.

### C — Standard analitik cevap

Kullanıcı:

> “Son 3 ay en çok fire veren 5 makineyi önceki 3 ayla kıyasla.”

UI:

```text
1–2 cümle doğrudan bulgu
↓
comparison chart/table
↓
semantic chips:
  Fire · Makine · Son 3 ay · Önceki 3 ay · Top 5
↓
“Nasıl hesaplandı?” / “RAM-3’e in” / “Neden?”
```

### D — Research Mode

Kullanıcı kompleks bir istek verdiğinde boş spinner gösterilmez.

UI'da yalnız **yüksek seviyeli görev ilerlemesi** gösterilir; modelin gizli chain-of-thought'u gösterilmez:

```text
Araştırma hazırlanıyor
✓ Ürün performansı incelendi
✓ Satış performansı karşılaştırıldı
● Makine ilişkisi inceleniyor
○ Personel/vardiya analizi
○ Bulgular birleştiriliyor
```

İlk progress event hedefi:

```text
p95 ≤ 2 saniye
```

Kullanıcı:

```text
[Şimdi cevapla]
[Durdur]
[Makine tarafına daha derin bak]
```

kontrolüne sahip olmalıdır.

### E — Research sonucu

Final rapor tek metin duvarı değildir.

```text
Rapor
├─ Yönetici özeti
├─ 1. Ürün performansı
│   ├─ grafik
│   ├─ 2–4 cümle yorum
│   └─ kanıt
├─ 2. Satış performansı
├─ 3. Ürün × makine
├─ 4. M3 neden zayıf?
│   ├─ hipotezler
│   ├─ destekleyen/çürüten kanıt
│   └─ candidate-cause etiketi
├─ 5. Personel/vardiya
├─ 6. Birleşik yorum
└─ Sınırlar / açık sorular
```

Her section üzerinde:

```text
[Bu bölümü aç]
[Bunu karşılaştır]
[Neden?]
[Rapora ekle/çıkar]
```

gibi bağlama bağlı aksiyonlar bulunabilir.

### F — Evidence UX

Kullanıcıya hidden reasoning gösterilmez.

Gösterilen provenance:

```text
hangi metrik?
hangi dönem?
hangi filtre?
hangi veri kaynağı/semantic model?
hangi contract?
hangi araştırma adımı?
```

olur.

“Bu sayı nereden geldi?” birinci sınıf UI aksiyonudur.

### G — Report follow-up

Kullanıcı:

> “M3 bölümünü vardiyalara göre biraz daha derinleştir ve raporu güncelle.”

Dima yeni konuşma açmaz.

```text
existing ResearchRun
+ report section anchor
→ bounded new investigation
→ new evidence
→ report version +1
```

üretir.

Bu, North-Star deneyimin kritik kabul senaryosudur.

---

## R6.3 UI/UX değişmezleri

1. **Text-first:** Kullanıcı önce sonucu okur; grafik destekler.
2. **No dead air:** Uzun araştırmada progress göster.
3. **No fake reasoning:** Gizli düşünce zinciri değil, görev/evidence progression göster.
4. **Clarify in place:** Belirsizlik aynı conversation içinde çözülür.
5. **Artifact anchoring:** Chart/table/report section sonraki mesaj için referans olabilir.
6. **Visible scope:** Dönem, metric, filtre ve assumption görünür.
7. **Evidence one click away:** Güven katmanı UI’dan erişilebilir.
8. **Graceful partial:** Budget/eksik veri durumunda ne tamamlandı/ne eksik açıkça söylenir.
9. **Conversation continuity:** Report üretmek chat bağlamını sıfırlamaz.
10. **User control:** Uzun agent run durdurulabilir veya “şimdi cevapla” ile kısaltılabilir.

---


## R6.4 Mevcut frontend neden yeniden yazılmak zorunda değil?

Repo denetiminde mevcut frontend zaten hedef deneyimin önemli primitive'lerini taşıyor:

| Mevcut bileşen | Bugünkü değer | Hedef kullanım |
|---|---|---|
| `ChatPanel` | thread navigation / pending run | conversation history ve run durumu |
| `ReportPanel` | ana conversation/report surface | V2 response host |
| `ResultView` | chart/table/pivot + chart click | evidence artifact renderer |
| `ReportView` | çok bloklu rapor + kaynak/contract | `ReportDocument` adapter hedefi |
| `PlanAdimlari` | plan/adım görünümü | high-level Research progress'e evrilebilir |
| `DurdurDugmesi` | background job cancel | Research cancel |
| `NextStepChips` | next-step suggestions | contextual follow-up actions |
| `ContractDetailPanel` | Query Contract inceleme/replay | evidence drawer |
| `ContributionLayer` / `DrillDownPanel` | analitik derinleşme | Research artifact/detail |
| `InterpretationBar` | yorum yüzeyi | text-first finding summary |

Bu nedenle hızlı yol:

> **Frontend rewrite değil; mevcut conversation/report shell'ine yeni typed V2 state ve Research events bağlamak.**

## R6.4.1 Frontend'de düzeltilmesi gereken eski varsayımlar

Mevcut UI'da bazı tarihsel kavramlar yeni sistemle değişmelidir.

Örnek:

```text
source="cube" → “LLM kullanılmadı”
```

artık doğru değildir; TurnInterpreter LLM kullanmış olabilir.

Yeni görünür provenance:

```text
Hesap: Cube/Wren
Yorum: AI
Kanıt: Contract
Tanım: Certified / Proposed
```

gibi **farklı soruları farklı etiketlerle** anlatmalıdır.

Başka örnek:

```text
PlanAdimlari
```

gizli chain-of-thought gösterme yüzeyi olmamalıdır.
Yalnız:

```text
yüksek seviyeli task
status
artifact produced
```

gösterir.

---

# R7 — TURNINTERPRETER: LLM’İN GERÇEK GÖREVİ

Tek structured language owner.

Girdi:

```text
current user message
bounded semantic context
topic/focus
pending clarification
selected card/anchor
```

Çıktı:

```text
dialogue_act
references
semantic mentions
analytical request?
presentation request?
user repair?
unresolved mentions
```

LLM:

```text
SQL yazmaz
canonical metric ID uydurmaz
physical table seçmez
tarih aritmetiği yapmaz
tenant entity value'yu kanıtsız bağlamaz
```

---

# R8 — SEMANTIC HYPOTHESIS VE CLARIFICATION

Her belirsiz yüzey:

```text
“siyah”
“premium”
“RAM-3”
“gece”
```

için candidate set oluşturulur.

Aday provenance:

```text
explicit anchor
current focus
canonical name
verified synonym
exact entity value
verified company vocabulary
fuzzy suggestion
```

Kural:

```text
tek güçlü aday → resolve
birden fazla material aday → clarify
yalnız fuzzy aday → öneri olarak sor
aday yok → semantic gap / açık soru
```

Sistem “daha net yaz” demek yerine mümkünse nokta atışı sorar.

---

# R9 — CONVERSATION STATE

Tek `last_query` veya `prev_sql` yeterli değildir.

Canonical state:

```text
TopicFrame
FocusState
ClarificationState
last contract
last IR
active ResearchRun
```

Desteklenen doğal konuşma örnekleri:

```text
“o makine”
“o ay”
“ilk karta dön”
“az önce dediğin gibi”
“yine OEE’ye dönelim”
“hayır müşteri değil renk”
```

Raw SQL canonical conversation memory değildir.

---

# R10 — STANDARD ANALYTICS YOLU

Basit/kompozisyonel istek:

```text
TurnInterpretation
→ AnalyticalRequest
→ AnalyticsIR
→ RequirementLedger
→ CubePlanner
→ existing WrenService
→ ResultValidator
→ Query Contract
→ ConversationResponse
```

MVP’de ana yol budur.

WrenSqlPlanner ilk MVP’nin blocker’ı değildir.

---

# R11 — RESEARCH / ANALYST MODE

Gerçek ürünün kritik parçasıdır.

## R11.1 ResearchBrief

Kullanıcı dili yalnız bir kez çözüldükten sonra:

```text
objective
scope
required domains
research questions
deliverables
must requirements
```

taşır.

Research agent ham cümleyi yeniden semantic olarak yorumlamaz.

## R11.2 Result-aware loop

```text
brief
→ seed tasks
→ execute
→ inspect evidence
→ finding/hypothesis
→ decide next task
→ execute
→ ...
→ stop/report
```

En başta dev statik plan yoktur.

## R11.3 Supervisor + scoped workers

İlk model:

```text
AnalystSupervisor
├─ QueryWorker
├─ RelationshipWorker
├─ RootCauseWorker
└─ ReportWorker
```

Worker:

```text
raw user prompt almaz
typed task alır
bounded read-only tools görür
kanıt üretir
final kullanıcı cevabını sahiplenmez
```

MVP’de bunların ayrı process olması gerekmez.

---

## R11.4 Typed `ResearchToolContract` — planner/tool ayrışmasını tekrar etme

Her research tool/adapter declarative bir sözleşme taşır:

```python
class ResearchToolContract(BaseModel):
    tool_id: str
    accepted_task_kinds: set[str]
    input_schema: str
    output_schema: str
    authority: str
    evidence_kind: str
    max_rows: int | None
    timeout_ms: int
    cost_class: str
    required_permissions: list[str]
```

Execution sırası:

```text
ResearchTask
→ ToolContract lookup
→ task-kind + input schema validation
→ authority / permission / budget validation
→ OfficialExecutionBoundary
→ output schema validation
→ EvidenceArtifact
```

Kurallar:

```text
contract'ta ilan edilmemiş tool çağrısı = 0
schema mismatch → execute etme
worker raw user prompt'tan tool input uydurmaz
adapter authority execution boundary'yi bypass etmez
max_rows / timeout / cost görünür policy'dir
```

Bu kapı eski `plan_semasi ↔ plan_tuketici` sınıfının yeni isimlerle geri dönmesini engeller.

---

# R12 — CROSS-DOMAIN ANALİZ

Üretim, satış ve personel farklı grain’lerde olabilir.

Naive join yasak.

Önce:

```text
semantic relationship path
canonical entity
time alignment
analysis grain
```

doğrulanır.

İlk ilişki yöntemleri:

```text
group comparison
peer deviation
trend co-movement
rank concordance
Pearson/Spearman — uygun olduğunda
lagged association
contribution decomposition
segment delta/lift
```

İleri yöntemler daha sonra eklenebilir.

---

## R12.1 `CrossDomainJoinGate`

Cross-domain task execute edilmeden önce aşağıdaki sözleşme kanıtlanır:

```text
canonical entity / join key
source grain
target analysis grain
relationship path
cardinality
required bridge/aggregation
time alignment
unit/currency alignment when relevant
fanout / double-count risk
```

Karar:

```text
grain compatibility proven
→ execute

grain compatibility unproven
→ execute ETME
→ LIMITATION / DATA_GAP / NEEDS_SEMANTIC_MODEL
```

Özellikle üretim × makine × personel × satış gibi North-Star senaryolarda bir ilişkinin MDL'de bulunması tek başına yeterli değildir; **analiz grain'inde sayısal olarak güvenli olduğu** kanıtlanmalıdır.

Release gate:

```text
silent many-to-many fanout      = 0
double-count on dedicated set   = 0
unproven cross-domain join      = 0 executed
```

---

# R13 — ROOT CAUSE VE CAUSALITY DİSİPLİNİ

İki eğrinin birlikte düşmesi neden-sonuç değildir.

Her finding epistemik tür taşır:

```text
OBSERVATION
COMPARISON
ASSOCIATION
CONTRIBUTION
CANDIDATE_CAUSE
CONFIRMED_CAUSE
```

`CONFIRMED_CAUSE` nadir olmalıdır.

HypothesisLedger:

```text
hipotez
evidence for
evidence against
next test
status
```

taşır.

Agent:

```text
“güçlü aday neden”
```

diyebilir.

Kanıt yoksa:

```text
“sebep budur”
```

diyemez.

---

# R14 — REPORTDOCUMENT

Kullanıcı “raporla” dediğinde tek bir markdown özet değil, kanıta bağlı doküman üretilir.

```text
ReportDocument
├─ executive summary
├─ section 1
│  ├─ narrative
│  ├─ chart/table/KPI
│  ├─ findings
│  └─ evidence refs
├─ section 2
├─ root-cause section
├─ combined interpretation
├─ limitations
└─ evidence index
```

Kural:

> Evidence referansı olmayan sayısal/analitik iddia rapora giremez.

ReportWorker kanıt eksikliği görürse Supervisor’a `NeedEvidence` döner.

---

## R14.1 Typed report-section anchor

Section-specific follow-up ancak section'ın gerçek semantic/evidence kimliği varsa desteklenir:

```text
ReportSection.id
EvidenceRef[]
semantic_scope
followup_context_ref
```

Akış:

```text
“bu bölümde M3'ü aç”
→ ReportSection.id
→ signed/typed artifact anchor
→ semantic_scope + evidence refs
→ ConversationState
→ TurnInterpreter / Resolver
```

UI section başlığını veya markdown metnini semantic authority olarak geri göndermez. Anchor stale/version-mismatch ise açıkça rebind/re-run gerekir; sessizce başka section'a bağlanmaz.

---

# R15 — WREN’İN NİHAİ ROLÜ

Wren:

```text
semantic model
context
cube/query planning
dry-plan
execution
```

katmanıdır.

Dima:

```text
conversation
semantic grounding policy
research orchestration
hypothesis/evidence
report
decision layer
```

katmanıdır.

Stock Wren LLM-facing query tool’ları production security authority değildir.

Principal-aware official execution Dima `WrenService` sınırında kalır.

---


# R15A — “ŞİRKET BEYNİ” FİZİBİLİTE HÜKMÜ

Bu ürün vizyonu teknik olarak **fizibldir**, fakat tek bir LLM'e “şirketi yönet” demek şeklinde fizibl değildir.

Doğru mimari:

```text
LLM / Conversation
        ↓
Semantic grounding
        ↓
Analytical / Research tools
        ↓
Prediction / Scoring models      # gerektiğinde
        ↓
Optimization solvers             # gerektiğinde
        ↓
Playbooks / Policies
        ↓
Human-approved Actions
```

Yani Dima her şeyi **konuşma üzerinden orkestre edebilir**; fakat her problemi LLM çözmez.

Bu ayrım ürünün başarı şansını belirler.

---

## R15A.1 Fizibilite seviyeleri

| Yetenek | Fizibilite | Asıl motor | Kritik önkoşul |
|---|---|---|---|
| KPI / trend / breakdown | yüksek | Wren + deterministic analytics | doğru MDL |
| çok-adımlı araştırma / rapor | yüksek | Research Agent + tools | semantic coverage + evidence |
| OEE neden analizi | yüksek/orta | decomposition + drill + maintenance/quality data | kayıp ve olay verisi |
| müşteri segmentasyonu | yüksek | analytics/scoring | CRM + satış geçmişi |
| müşteri önceliklendirme | yüksek | scoring/rules/ML | hedef ve kriter |
| müşteri ziyaret sırası | yüksek | priority scoring + route optimization | koordinat/zaman/rota verisi |
| kampanya adayı önerme | yüksek | segmentation + product affinity + playbook | CRM/order data |
| “en iyi kampanya” etkisi | orta | uplift/propensity + experiment | geçmiş kampanya/deney verisi |
| predictive maintenance | orta/yüksek | ML/anomaly model | sensör + failure history |
| kesin kök neden | koşullu | causal/mechanistic evidence | yeterli gözlem / deney / mekanizma |
| tamamen otonom aksiyon | teknik olarak mümkün, ürün riski yüksek | workflow tools | approval, audit, policy |

Sonuç:

> **“Şirket beyni” vizyonu yapılabilir; fakat doğru ürün, LLM'in tahminlerini değil farklı hesap/optimizasyon motorlarını tek konuşma ve kanıt katmanında birleştiren sistemdir.**

---

# R15B — YETENEK MERDİVENİ: OKU → ANALİZ ET → ÖNER → OPTİMİZE ET → AKSİYON AL

## Seviye 1 — Read / Understand

```text
“Bu ay OEE?”
“En çok fire nerede?”
```

Semantic analytics.

## Seviye 2 — Diagnose / Research

```text
“M3 neden diğerlerinden düşük?”
“Bu ürünün performansı neden düştü?”
```

ResearchRun + hypothesis + evidence.

## Seviye 3 — Recommend

```text
“Ne yapmalıyız?”
“Hangi müşterilere kampanya yapmalıyım?”
```

Burada yalnız LLM görüşü yetmez.

Recommendation:

```python
class Recommendation(BaseModel):
    action: str
    rationale: str
    evidence_refs: list[str]
    source: Literal["playbook","policy","model","optimization","analyst"]
    expected_effect: str | None
    confidence_class: str
    prerequisites: list[str]
    risks: list[str]
    approval_required: bool
```

Şirket playbook/SOP/policy yoksa Dima:

```text
“önerilen aksiyon”
```

yerine çoğu durumda:

```text
“kanıta göre sonraki kontrol/adım”
```

dilini kullanmalıdır.

## Seviye 4 — Optimize

```text
“Hangi sırayla müşterileri ziyaret edeyim?”
“Hangi kampanya bütçesini hangi segmente dağıtayım?”
“Bakım pencerelerini nasıl planlayalım?”
```

Bu, generative text problemi değildir.

Dima:

```text
objective
constraints
candidates
scores
```

çıkarır; ardından optimizer/solver kullanır.

## Seviye 5 — Act

```text
CRM task oluştur
ziyaret planını takvime yaz
bakım iş emri aç
kampanya draft'ı oluştur
```

Bu katman:

```text
preview
→ approval
→ execute
→ audit
```

şeklinde ilerler.

İlk üretim sürümlerinde kritik write action'lar autonomous değildir.

---

# R15C — İMALAT-FIRST “ŞİRKET BEYNİ” KAPSAMI

Dima'nın birinci dikeyi imalattır.

Öncelik sırası:

```text
1. Üretim / OEE / throughput
2. Fire / kalite
3. Duruş / bakım
4. Makine / hat / vardiya
5. Ürün / reçete / changeover
6. Personel / vardiya ilişkisi
7. Stok / malzeme / tedarik
8. Satış ile üretim performansının bağlanması
```

## R15C.1 Canonical imalat senaryosu

Kullanıcı:

> “M3'ün OEE'si diğer makinelerden düşük. Neden daha düşük ve ne yapmalıyız?”

Dima'nın doğru çalışma sırası:

```text
1. Scope'u doğrula:
   dönem, makine, peer grubu.

2. OEE'yi decomposition yap:
   Availability
   Performance
   Quality

3. Hangi bileşen sapıyor?
   peer / baseline / previous-period compare.

4. Sapmayı kır:
   ürün
   vardiya
   operatör/personel
   gün/saat
   changeover
   duruş nedeni
   kalite/fire
   hız/performance loss

5. Varsa maintenance/work-order ve olay verisini bağla.

6. HypothesisLedger oluştur.

7. Hipotezleri evidence ile test et.

8. Finding'leri epistemik sınıfla etiketle.

9. Playbook/SOP varsa action candidate üret.

10. Conversation + chart/table + report ile anlat.
```

### Beklenen konuşma

Dima yalnız:

> “M3 düşük.”

demez.

Örneğin:

> “M3'ün son 30 gündeki OEE'si peer grubundan 7,4 puan düşük. Farkın büyük kısmı kalite değil performans bileşeninden geliyor. Düşüş gece vardiyasında ve Ürün A üretimlerinde yoğunlaşıyor. Planlı duruş bu farkı açıklamıyor; hız kaybı güçlü aday neden. Bakım kayıtlarında aynı dönemde motor/hat hızıyla ilişkili tekrar eden bir olay varsa bunu bir sonraki kontrol olarak bağlayabilirim.”

Ardından:

```text
[OEE peer chart]
[Availability / Performance / Quality decomposition]
[shift × product table]
[downtime / maintenance evidence]
```

gösterilir.

### “Ne yapmalıyız?” davranışı

Şirket bakım/operasyon playbook'u bağlıysa:

```text
kanıt
+ playbook rule
→ öneri
```

Örneğin:

```text
“Performance kaybı > X ve speed-loss reason Y ise hız kalibrasyonu / bakım kontrolü”
```

gibi doğrulanmış operasyon kuralı kullanılabilir.

Playbook yoksa Dima kesin iş emri önerisi uydurmaz; kanıta dayalı **next diagnostic step** üretir.

---

# R15D — CRM / SATIŞ: ŞİRKET BEYNİNİN GENİŞLEME SENARYOLARI

İmalat ana dikeydir; fakat aynı çekirdek CRM verisine bağlandığında satış karar desteği de fizibldir.

## R15D.1 “Müşterilerime nasıl kampanya yapmalıyım?”

Gerekli veri:

```text
customer/account
order history
product/category
margin
recency/frequency/value
sales rep/activity
campaign history
response/conversion
channel
inventory/availability
```

İlk güvenilir seviye:

```text
segmentasyon
RFM / lifecycle
product affinity
margin
churn/risk signals
historical campaign response
```

Dima şunu üretebilir:

```text
segment
candidate offer
candidate channel
rationale
expected/observed historical evidence
measurement plan
```

### Kritik sınır

Sadece gözlemsel geçmişle:

> “Bu kampanya kesin en çok satış getirir.”

denmez.

Gerçek **incremental campaign effect** için:

```text
A/B test
randomized holdout
veya
uplift / causal response model
```

gerekir.

Dolayısıyla ilk ürün:

```text
evidence-backed campaign candidates
```

üretir.

Daha ileri sürüm:

```text
uplift model
→ treatment prioritization
```

kullanabilir.

## R15D.2 “Hangi müşterileri hangi sırayla ziyaret etmeliyim?”

Bu iki ayrı problemdir.

### A — Önceliklendirme

Customer priority score:

```text
opportunity value
conversion likelihood
urgency
last contact
churn/risk
service issue
strategic tier
margin
campaign/event
user-defined priorities
```

LLM kriterleri konuşmayla toplar.
Scoring motoru sıralar.

### B — Rota optimizasyonu

Sonra:

```text
customer coordinates
working hours
appointment windows
travel-time matrix
visit duration
rep start/end location
must-visit constraints
```

ile route solver çalışır.

Bu problem klasik:

```text
Vehicle Routing Problem / TSP with Time Windows
```

sınıfındadır.

OR-Tools gibi solver'lar bunu doğrudan çözebilir.

Dima'nın rolü:

```text
kriteri anlamak
önceliği hesaplatmak
constraint'i toplamak
optimizer'ı çağırmak
sonucu insani biçimde anlatmak
```

olur.

LLM'in kafadan rota sıralaması yapması **yasaktır**.

---

# R15E — KARAR / PLANLAMA MİMARİSİ

Research Mode bulgu üretir.
Decision Mode seçenek üretir.

```text
ResearchRun
   ↓
Findings / Evidence
   ↓
DecisionBrief
   ↓
CandidateActions
   ↓
Policy / Playbook / Model / Solver
   ↓
RecommendationSet / OptimizedPlan
   ↓
User conversation
   ↓
Approval
   ↓
Workflow execution
```

Minimum domain:

```python
class DecisionBrief(BaseModel):
    objective: str
    constraints: list[str]
    candidate_scope: list[str]
    evidence_refs: list[str]

class RecommendationSet(BaseModel):
    recommendations: list[Recommendation]
    assumptions: list[str]
    tradeoffs: list[str]

class OptimizedPlan(BaseModel):
    objective_value: float | None
    ordered_actions: list[str]
    constraints_satisfied: list[str]
    constraints_relaxed: list[str]
```

---

# R15F — FİZİBİLİTE SINIRLARI: NEYİ MİMARİYLE ÇÖZEMEYİZ?

Doğru mimari çok şeyi çözer; **her problemi ortadan kaldırmaz**.

## 1. Veri yoksa bilgi yok

Makinenin duruş nedeni tutulmuyorsa Dima bunu semantik zekâyla üretemez.

## 2. Yanlış veri doğru reasoning üretmez

Sensor/data quality ve master-data sorunları açıkça görünür olmalıdır.

## 3. Semantic model bilinmeyen business rule'u keşfedemez

Şirket “aktif müşteri”yi özel bir kuralla tanımlıyorsa bu tanım sisteme öğretilmelidir.

## 4. Correlation causation değildir

Gözlemsel veride çoğu root-cause çıktısı:

```text
candidate cause
```

olarak kalacaktır.

## 5. “En iyi aksiyon” objective olmadan tanımsızdır

Örneğin müşteri ziyareti:

```text
maksimum ciro?
maksimum conversion?
minimum yol?
stratejik müşteri?
risk azaltma?
```

hangi hedefe göre optimize edildiği bilinmeden “en iyi sıra” yoktur.

## 6. Gelecek tahmini ayrı model gerektirebilir

Forecast/propensity/predictive-maintenance gibi işler:
LLM değil, doğrulanmış predictive model gerektirir.

## 7. Büyük optimizasyonlar yaklaşık çözüm üretebilir

Routing gibi kombinatoryal problemler büyük ölçeklerde her zaman mutlak optimal çözüm vermez; “iyi/uygulanabilir” plan kabul edilebilir.

## 8. Agent hatası sıfırlanamaz

Ama:

```text
typed contracts
bounded tools
evidence
eval
clarification
human approval
```

ile hatayı lokalize ve yönetilebilir hâle getiririz.

---

# R15G — “MÜKEMMEL”İN TEKNİK TANIMI

Dima için “mükemmel” şu değildir:

> Her şirket sorusuna sıfır hatayla sihirli cevap.

Gerçek teknik hedef:

```text
Doğru anla veya sor.
Doğru engine'i seç.
Kanıt olmadan iddia etme.
Eksik veriyi saklama.
Korelasyonu sebep diye satma.
Optimizasyonu LLM'e bırakma.
Aksiyon öncesi approval uygula.
Her sonucu yeniden üretilebilir ve denetlenebilir yap.
```

Bu hedef fizibldir ve ölçülebilir.

---


# R15H — NİHAİ SİSTEM MASAÜSTÜ SİMÜLASYONU VE FİZİBİLİTE DENETİMİ

Bu bölüm “mimari güzel görünüyor” kontrolü değildir.

Her senaryo için:

```text
gerekli veri
çalışacak katmanlar
UI davranışı
beklenen sonuç
teknik fizibilite
koşullu sınır
```

adım adım yürütülür.

---

## S1 — Basit KPI: “Bu ay ciro?”

### Gerekli veri

```text
canonical ciro metric
canonical time dimension
current tenant DB
```

### Akış

```text
TurnInterpreter → ANALYTIC_STANDARD
Resolver → metric:ciro
TimeResolver → this_month
RequirementLedger → metric + period
CubePlanner
Wren
Contract
Finalizer
```

### UI

```text
“Bu ay ciro X TL.”
[scope: Eylül · Ciro]
[Geçen ayla kıyasla] [Müşteri bazında aç]
```

### Fizibilite

**YÜKSEK / DOĞRUDAN.**

Mevcut repo motorlarının büyük kısmı zaten vardır.
Yeni risk dil/grounding/contract wiring'dir.

---

## S2 — Belirsiz entity: “Siyah için fire.”

### Veri

Tenant entity-value index.

### Akış

```text
TurnInterpreter
→ mention "siyah"
Resolver
→ candidate set
```

İki aday varsa:

```text
CLARIFY
```

### UI

Candidate chips.

### Fizibilite

**YÜKSEK.**

Bu bir NLP + catalog grounding problemidir.
Özel “siyah” kuralı gerektirmez.

---

## S3 — Standard kompleks query: “Son 3 ay en çok fire veren 5 makineyi önceki 3 ayla kıyasla.”

### Gereksinim

```text
fire
machine
period A
period B
comparison
sort desc
limit 5
```

### Akış

Tek IR + ledger.

### Fizibilite

**YÜKSEK.**

Ana teknik risk:
time/comparison/ranking semantics'in plan sırasında düşmesi.

Ledger + tested cube compiler bunu kapatır.

---

## S4 — Kompleks araştırma/rapor: ürün × makine × personel × satış

Kullanıcı:

> “Son 12 ay ürünleri karşılaştır; makineler ve personellerle ilişkisini analiz et;
> satış performansını yorumla, önemli düşüşlerin nedenlerini araştır ve raporla.”

### Gerekli veri

```text
production fact
product
machine
time
shift/personnel mapping
sales fact
semantic relationship path
```

Personel verisi yoksa ilgili bölüm `DATA_GAP` olur; bütün run yalan veriyle tamamlanmaz.

### Adım 1 — Conversation

`ResearchBrief` bütün deliverable'ları taşır.

### Adım 2 — Seed

```text
production by product × month
sales by product × month
production by product × machine
production by product × shift/personnel
```

### Adım 3 — Evidence

Her query Contract/Evidence üretir.

### Adım 4 — Adaptive branch

M3 anomalisi görülürse:

```text
M3 OEE
M3 performance/quality/availability
M3 downtime
M3 shift
```

araştırması açılır.

### Adım 5 — Synthesis

Cross-domain grain bilinçli hizalanır.

### Adım 6 — Report

Multi-artifact report.

### UI

Progress + inline artifacts + final report + evidence drawer.

### Fizibilite

**YÜKSEK, VERİ KAPSAMINA BAĞLI.**

Mevcut repo:

```text
multi-block report
chart/table renderer
contract viewer
drill/contribution/root-cause primitive
```

taşıdığı için sıfırdan ürün inşa edilmiyor.

### Kalan zorluk

```text
robust cross-domain grain alignment
result-aware orchestration
long-run state
report grounding
```

Bunlar çözülebilir mühendislik problemleridir.

---

## S5 — İmalat: “M3 OEE düşük. Neden ve ne yapmalıyız?”

### Veri

Minimum:

```text
OEE components
machine
time
production
```

Daha kaliteli diagnosis için:

```text
downtime reasons
product
shift/personnel
maintenance/work orders
quality/scrap
speed/setpoint/events
```

### Simülasyon

1. Peer group belirle.
2. Gap ölç.
3. A/P/Q decomposition.
4. Performance düşükse:
   - product mix
   - shift
   - speed loss
   - downtime
5. Hypothesis:
   - planned downtime?
   - quality?
   - speed loss?
   - shift effect?
6. Evidence for/against.
7. Candidate cause.
8. Playbook varsa recommendation.
9. Yoksa next diagnostic step.

### UI

```text
Executive answer
OEE gap
component waterfall
candidate causes
evidence
recommended next step
```

### Fizibilite

**DIAGNOSIS: YÜKSEK/ORTA.**
**CONFIRMED ROOT CAUSE: KOŞULLU.**
**RECOMMENDATION: PLAYBOOK/DATA'YA BAĞLI.**

Mimari “neden”i sihirle çözmez; kanıt derecesini dürüst tutar.

---

## S6 — CRM: “Müşterilerime nasıl kampanya yapmalıyım?”

### Veri

```text
orders
customer
product/category
margin
recency/frequency
campaign history
channel
inventory
```

### İlk seviye

Segmentation + affinity + observed response.

### UI

```text
Segment A
neden?
önerilen teklif
önerilen kanal
kanıt
nasıl ölçeceğiz?
```

### Fizibilite

**CAMPAIGN CANDIDATE: YÜKSEK.**
**INCREMENTAL ‘EN İYİ’ KAMPANYA: KOŞULLU.**

Causal/uplift için experiment/holdout gerekir.

---

## S7 — CRM: “Bu hafta hangi müşterileri hangi sırayla ziyaret etmeliyim?”

### Girdi

Kullanıcı hedefi:

```text
maksimum satış fırsatı?
risk azaltma?
stratejik müşteri?
minimum yol?
```

Belirsizse Dima sorar.

### Sistem

```text
PriorityScore
→ top candidate visits
→ constraints
→ travel matrix
→ VRP/VRPTW solver
```

### UI

```text
ordered list
map
recommended times
priority rationale
dropped/relaxed constraints
```

### Fizibilite

**YÜKSEK, GEREKLİ LOKASYON/ZAMAN VERİSİ VARSA.**

LLM yalnız conversation/orchestration.
Optimizasyon solver.

---

## S8 — Rapor refinement

Kullanıcı:

> “M3 bölümünü gece vardiyasına göre derinleştir ve raporu güncelle.”

### Akış

```text
report section anchor
→ existing ResearchRun
→ scoped new task
→ new evidence
→ affected findings update
→ report version +1
```

### Fizibilite

**YÜKSEK.**

Mevcut report/thread frontend altyapısı bunu destekleyecek güçlü bir taban taşır.

---

## S9 — Veri eksik

Kullanıcı personel ilişkisi istiyor.
Tenant DB'de personel/shift mapping yok.

Doğru cevap:

```text
Üretim ve makine analizini tamamladım.
Personel ilişkisini değerlendirmek için güvenilir
personel-vardiya eşlemesi bulunmuyor.
```

### Fizibilite

**YÜKSEK.**

Bu özellikle mimarinin başarısıdır; fake answer üretmemek gerekir.

---

## S10 — Contradictory evidence

Bir query M3'ü kötü gösteriyor; başka dönem farklı.

Agent:

```text
tek hikâyeye zorlamaz
```

Finding:

```text
period-specific
inconclusive
```

olabilir.

### Fizibilite

**YÜKSEK.**

Report cross-section consistency validator gerekir.

---

## S11 — Cross-tenant güvenlik

Yanlış runtime/context candidate dönerse:

```text
tenant assertion fail
→ no prompt
→ no query
→ security event
```

### Fizibilite

**YÜKSEK**, fakat release P0 testidir.

---

## S12 — Uzun araştırma + kullanıcı kontrolü

Research 45 saniye sürüyor.

UI:

```text
progress
artifacts arriving
[Şimdi cevapla]
[Durdur]
```

“Şimdi cevapla”:

```text
current evidence
→ partial report
→ açık eksikler
```

### Fizibilite

**YÜKSEK.**

Mevcut repo job/cancel/progress yüzeyleri reuse edilebilir.

---

# R15I — FİZİBİLİTE SONUCU: İSTEDİĞİMİZ ÜRÜN GERÇEKTEN ÇIKAR MI?

## Teknik hüküm

Evet, hedeflenen ürün **fizibldir**.

Fakat başarı formülü:

```text
iyi LLM
```

değildir.

```text
iyi LLM
× doğru semantic layer
× deterministic analytics
× agent tool contracts
× evidence
× domain data
× eval
× UX
```

çarpımıdır.

Bunlardan biri sıfırsa toplam kalite çöker.

## Bugünkü repo açısından hüküm

Sıfırdan başlamıyoruz.

Bugün zaten:

```text
Wren semantic/execution
cube compiler
conversation/thread UI
chart/table/pivot
multi-block report
contract/evidence UI
drill/contribution/root-cause primitives
jobs/cancel
decision records
dashboard/schedule
large eval/test corpus
```

bulunduğu için teknik risk “bütün sistemi yapabilir miyiz?” değil.

Asıl risk:

> **doğru sahiplik sınırlarını kurup eski karmaşıklığı yeni çekirdeğe tekrar ithal etmeden bunları birleştirebilir miyiz?**

Bu raporun ve yol haritasının ana amacı tam olarak budur.

## Fizibilite koşulları

North-Star için şu dört koşul gereklidir:

```text
1. Manufacturing semantic/data readiness
2. Conversation + standard analytics gates
3. Research/evidence gates
4. Decision skill için playbook/model/solver readiness
```

CRM veya başka sektör yetenekleri çekirdeğin çalışmasını bekler; çekirdeği karmaşıklaştırarak aynı anda yapılmaz.

---


# R15J — UYGULAMA ÖNCESİ PRE-MORTEM: NEREDE TAKILABİLİRİZ?

Aşağıdaki riskler mimarinin uygulanabilirliğini bozmaz; fakat önceden sahiplenilmezse süreyi uzatır.

| Risk | Olası belirti | Kök çözüm | MVP'yi durdurur mu? |
|---|---|---|---|
| Türkçe structured parse dalgalı | yanlış dialogue act / missing slot | güçlü model + schema + eval; regex değil | yalnız P0 ise |
| Wren context yetersiz | doğru metric prompt'a gelmiyor | schema provider → Wren memory later; Recall@K | hayır |
| entity value kataloğu büyük/hassas | prompt taşması / PII | safe index + placeholders | hayır |
| mevcut time logic monolite gömülü | V2 import chain büyüyor | yalnız pure primitive extraction | kısa spike |
| CubeQuery bazı complex işi ifade etmiyor | capability gap | explicit unsupported; WrenSql later | hayır |
| eski root-cause tool inputları uyumsuz | Research task çalışmıyor | typed adapter; tool gövdesini koru | hayır |
| Research yavaş | kullanıcı bekliyor | progress + budget + answer-now | hayır |
| rapor hallucinate ediyor | sayı contract'sız | Finding/evidence gate | **evet P0** |
| cross-domain grain hatası | double count | grain compatibility gate | **evet P0** |
| security shadow false positives | `on` geçişi zor | telemetry + targeted fixes | pilot blocker |
| multi-connection belirsiz | yanlış DB | active connection / single-pilot rule | pilot blocker |
| provider outage | interpreter 5xx | infra failover; semantic fallback yok | hayır |
| maliyet yükseliyor | çok LLM/tool turu | strong model yalnız language/research planning; deterministic tools | hayır |
| manufacturing data eksik | “neden?” yarım | readiness + PARTIAL_BY_DESIGN | hayır |
| generic onboarding uzuyor | pilot gecikiyor | ilk pilot manual/known pack | hayır |
| optimizasyon kötü sonuç | infeasible/slow model | constraint validator + solver metrics | ilgili skill blocker |
| “şirket beyni” scope patlıyor | 10 skill aynı sprint | manufacturing-first capability cutline | **evet yönetim riski** |

## R15J.1 En kritik üç mühendislik riski

### 1. Semantic ownership'un yeniden dağılması

Teknik olarak en büyük risk budur.

Yeni feature ekleyen geliştirici:

```text
“bu skill için küçük özel parser yazayım”
```

dediği anda mimari çürümeye başlar.

### 2. Research'in tekrar statik planner'a dönüşmesi

Research gerçek result-aware loop olmalıdır.

En başta 15 adım yazdırıp sırayla koşmak, eski plan problemini geri getirir.

### 3. Decision skill'lerin LLM tarafından hesaplanması

Prediction/optimization/causal işler:

```text
LLM text reasoning
```

ile taklit edilirse ürün demo verir ama güvenilir “company brain” olmaz.

Bu yüzden engine boundary zorunludur.

---

# R15K — YOL HARİTASI FİZİBİLİTE SİMÜLASYONU

Current repo ve hedef mimari birlikte düşünüldüğünde adım adım sonuç:

| Aşama | Mevcut dayanak | Yeni yapılacak | Fizibilite hükmü |
|---|---|---|---|
| `/ask-v2` island | FastAPI, auth, CompanyRegistry | yeni route/package | **yüksek** |
| TurnInterpreter | mevcut Anthropic/OpenAI provider wrapper ve structured/tool-use altyapısı | yeni schema/prompt | **yüksek** |
| Resolver/clarify | schema, context, entity/varlık yatırımı | CandidateSet + policy | **yüksek** |
| CubePlanner | CubeQuery + WrenService | temiz IR adapter | **yüksek** |
| Conversation | context/reply/thread DB + UI | typed state/delta | **yüksek** |
| Research | 34 tool primitive + root-cause/contribution/drill | supervisor/evidence contract | **orta-yüksek** |
| Report | existing ReportView/report.compose | ReportDocument adapter/grounding | **yüksek** |
| Pilot security | principal/RLS/CLS hooks | enforcement hardening | **orta** |
| Manufacturing Advisor | OEE/cube/root-cause primitives | readiness + playbook layer | **orta-yüksek** |
| Job Sequencer | no general solver today | OR-Tools adapter + domain constraints | **yüksek ama yeni domain model** |
| Generic onboarding | existing Postgres introspection/packs | connector/snapshot/bootstrap | **orta** |
| CRM campaign | core reusable | CRM semantics/model | **orta-yüksek veri bağımlı** |
| Visit optimization | core reusable | scoring + travel matrix + VRPTW | **yüksek veri/constraint varsa** |
| Causal inference | Research/evidence | causal readiness/model | **koşullu** |
| Full autonomous action | action/decision records mevcut | approvals/idempotency/connectors | **sonraki faz** |

### Sonuç

Mimari açıdan:

```text
NO FUNDAMENTAL BLOCKER
```

görülmektedir.

Fakat şu üç koşul sağlanmazsa North-Star iddiası yapılmaz:

```text
1. semantic/data readiness
2. evidence + security gates
3. skill-specific engine readiness
```

Bu nedenle plan fizibldir; **scope discipline ve veri gerçekliği** ana sınırlardır.

---

# R16 — CONTEXT / MEMORY / VERSIONING

Context bir prompt string’i değildir.

Canonical version:

```text
mdl_version
context_version
prompt_version
interpreter_version
model_id
```

taşır.

`context_version` MVP'nin ilk gününden itibaren gerçek ve hesaplanabilir olmalıdır; Memory gelene kadar `null`/sahte değer kullanılmaz.

**ContextVersionV0 — Memory öncesi MVP:**

```text
hash(
  mdl_version
  + compact_catalog_builder_version
  + business_rules_hash
  + prompt_context_policy_version
)
```

V0'daki `business_rules_hash`, yalnız ilgili tenant/runtime için **approved** ve prompt-context policy tarafından gerçekten runtime context'e alınan business rule setinin canonical hash'idir. Context'e verilmeyen bir kural yalnız dosyada mevcut diye version hash'ine girmez.

**ContextVersionV1 — verified retrieval/memory aktif olduğunda:**

```text
V0 inputs
+ verified_example_hashes
+ embedding_model_id/version
+ retrieval_policy_version
+ index/build manifest
```

Dolayısıyla `context_version` en az MDL, rules, verified examples, embedding model ve retrieval policy değişimlerini; ilgili aşamada gerçekten kullanılan context bileşenleri üzerinden kapsar. V0→V1 geçişi explicit version transition'dır.

Memory stale ise fail-open kullanılmaz.

---


## R16.1 Context subsystem — eski context hatalarını tekrar etmeme kuralları

Context:

```text
“prompt'a birkaç schema adı basalım”
```

değildir.

Production context pipeline:

```text
canonical source packs
→ compose/build
→ target MDL
→ business rules
→ trusted verified examples
→ retrieval index
→ ContextVersion manifest
→ immutable TenantAnalyticsRuntime
```

olmalıdır.

### A — Canonical source vs generated runtime

Repo'da:

```text
demo/packs/...             # canonical authoring
demo/companies/...         # company override
demo/wren-project*         # generated runtime
```

ayrımı korunur.

Generated runtime elle truth source gibi edit edilmez.

### B — Context consistency

Publish öncesi:

```text
metric formula conflict?
unit conflict?
aggregation conflict?
retired semantic ref?
verified example dry-plan oluyor mu?
physical DB SQL memory'ye sızmış mı?
```

kontrol edilir.

Context consistency fail:

```text
new context publish YOK
old valid runtime active kalır
```

### C — Verified memory

Verified example:

```text
candidate
→ human/golden verification
→ current semantic version validation
→ dry-plan
→ runtime memory projection
```

olmadan memory truth olmaz.

Runtime başarılı oldu diye otomatik `store_query` yoktur.

### D — Holdout leakage

Eval HOLDOUT:

```text
memory
few-shot
prompt examples
```

içine giremez.

Aksi hâlde eval retrieval ezberini ölçer.

### E — Retrieval ayrıca ölçülür

Interpreter başarısızlığından ayrı:

```text
Context Recall@K
```

ölçülür.

Doğru metric context'e hiç gelmediyse prompt tuning yapılmaz; retrieval düzeltilir.

### F — Memory rebuild

Live memory index in-place rebuild edilmez.

```text
build candidate
→ validate
→ create ContextVersion
→ new provider instance
→ atomic runtime swap
```

Request hot path index build etmez.

### G — Embedding model bir index version'ıdır

Embedding değişirse:

```text
context_version değişir
full index rebuild
```

gerekir.

Eski ve yeni vector dimension/index karıştırılmaz.

### H — Knowledge file collision

Pack compose'da aynı relative knowledge filename iki layer tarafından sahipleniliyorsa:

```text
explicit override yok
→ build fail
```

olmalıdır.

“Son kopyalanan kazanır” semantic truth için sessiz davranış olamaz.

### I — Runtime identity

Request boyunca:

```text
tenant_id
connection_id/version
mdl_version
context_version
fiscal/time context
```

aynı snapshot'a bağlıdır.

Bu sözleşmenin kavramsal adı:

```text
ContextVersion
```

ve request runtime'ın bir parçasıdır.

---

## R16.2 Dependency / Wren upgrade disiplini

Bugünkü backend Wren bağımlılığı 0.13 hattında pinlidir.

Kurtarma sırasında:

```text
conversation migration
+
semantic-core migration
+
Wren major/minor architecture upgrade
```

aynı PR'a konmaz.

Kural:

```text
önce current engine üstünde V2 proof
sonra ayrı compatibility matrix
sonra gerekiyorsa engine upgrade
```

Çünkü aynı anda iki ekseni değiştirirsek regression'ın:

```text
bizim V2 kodumuzdan mı?
Wren upgrade'den mi?
```

geldiği bilinmez.

---

# R16A — PILOT CAPABILITY ENVELOPE

Pilotun V2'ye alınması yalnız “V2 genel olarak doğru çalışıyor” koşuluna bağlı değildir. O tenant'ın gerçek kritik workload'u da V2 scope'u içinde olmalıdır.

Tenant bazında publish edilen envelope:

```text
supported metrics / domains
supported analytical operators
supported time/comparison families
supported research capabilities
known unsupported legacy capabilities
critical journey corpus
```

Pilot feature flag ancak:

```text
pilot tenant critical journeys          = 100% supported
P0 silent-wrong                          = 0
known unsupported capability list        = explicit/visible
historical workload coverage             ≥ pilotta önceden kabul edilen eşik
unsupported request                      → explicit UNSUPPORTED / capability gap
```

ise açılır.

Moving average, cumulative, HAVING, discrete months, blend, fiscal edge case gibi legacy capability V2'de henüz yoksa sessiz downgrade edilmez. Pilot scope'u buna göre daraltılır veya parity tamamlanır.

---

# R17 — SECURITY / TENANT SINIRI

yeni çekirdeğin konuşma veya agentic olması security sınırını değiştirmez.

Zorunlu:

```text
tenant runtime isolation
principal propagation
MDL-governed execution
PII/prompt safety
output masking
RLS/CLS policy
read-only research tools
write actions separate approval workflow
```

Agent kullanıcıdan daha yetkili olamaz.

## R17.1 Current security gerçeği ve production cutover

Current repo config denetiminde:

```text
strict_sql_policy = shadow
motor_rls         = shadow
motor_cls         = off
```

bulunmaktadır.

Bu durum şu demektir:

> Yeni orchestration doğru boundary'yi kullansa bile “production security tamam” denemez.

Pilot öncesi ayrı security gate:

```text
shadow deny telemetry
principal propagation
cross-tenant context tests
RLAC session properties
strict SQL bypass inventory
CLS hidden-column UX
```

gerektirir.

`on` geçişi ölçümle yapılır.

### CLS özel uyarı

Kolon erişimi:

```text
sessizce drop
```

ediliyorsa kullanıcı yanlışlıkla “bu veri yok” sanabilir.

Bu nedenle CLS enforcement öncesi:

```text
“Bu alan yetkin nedeniyle gösterilmiyor.”
```

gibi user-visible withheld-field davranışı gerekir.

---

## R17.2 Tenant connection authority

Current `CompanyRegistry` bağlantı seçimi:

```text
api_sync varsa onu
yoksa conns[0]
```

mantığı taşır.

MVP'de tek connection varsayımında çalışabilir; fakat nihai SaaS için “ilk bağlantı” production authority olamaz.

Hedef control-plane state:

```text
active_connection_id
connection_version
```

olmalıdır.

Runtime:

```text
TenantAnalyticsRuntime.connection_version
```

ile bunu taşır.

Bağlantı değiştiğinde:

```text
WrenService
ContextProvider
cached schema
```

birlikte invalidate edilir.

---

## R17.3 Mali takvim ve temporal context

Bugünkü `wren_for_request()` tenant mali takvimini kurarak önemli bir sessiz-yanlış sınıfını önlüyor.

Bu davranış V2'de kaybolmamalıdır.

Uzun vadede request-global yan etki yerine explicit runtime dependency tercih edilir:

```text
TemporalContext(
  timezone,
  fiscal_year_start,
  as_of
)
```

ve hem standard hem background/research task bunu explicit alır.

---


# R17A — SAAS ONBOARDING: ŞİRKET BEYNİNİN VERİYE BAĞLANMA KAPISI

Şirket beyni ancak müşterinin verisini doğru modele bağlayabiliyorsa ürünleşebilir.

Ancak generic onboarding **Core MVP blocker değildir**.

İlk pilot:

```text
tek doğrulanmış datasource
manual/known pack
explicit active connection
```

ile yürüyebilir.

Generic onboarding daha sonra ürünleştirilir.

## R17A.1 Current repo'da ölçülen onboarding sınırlamaları

`db_introspect.py` current HEAD'de:

```text
_SUPPORTED_DATASOURCES = ("postgres",)
```

kullanıyor.

Ayrıca:

```python
introspect_schema(..., max_tables=50)
```

ilk 50 tabloyu alıyor.

Şu davranışlar da current implementation'da bilinçlidir:

```text
yalnız get_table_names()
view discovery yok
self-referential FK ilk sürümde atlanıyor
composite FK relationship condition'ında ilk kolon çifti kullanılıyor
```

Dolayısıyla bu codepath:

> “Her müşteri DB'sini güvenilir biçimde otomatik modeller.”

diye sunulamaz.

## R17A.2 Nihai onboarding lifecycle

```text
CONNECT
→ READ-ONLY VERIFY
→ INTROSPECT
→ PROFILE
→ SCHEMA SNAPSHOT
→ SOURCE RECOGNITION
→ SEMANTIC BOOTSTRAP
→ HUMAN CONFIRMATION
→ COMPOSE / BUILD
→ CONTEXT BUILD
→ CONSISTENCY VALIDATION
→ ACTIVATE RUNTIME
```

### `Connector`

```text
test_connection()
verify_read_only()
introspect()
profile()
```

İlk ürün desteği:

```text
Postgres
```

ile başlayabilir.

MSSQL/MySQL gerçek müşteri talebi geldiğinde aynı connector contract üzerinden eklenir.

## R17A.3 `SchemaSnapshot`

Canonical snapshot:

```text
connection_id/version
schema/table/view identity
column/type
PK/FK
row-count estimate
safe cardinality
null ratio
date range
bounded enum samples
bounded numeric profile
```

taşır.

Nihai identity:

```text
datasource.schema.table
```

olmalıdır; yalnız table name büyük kurumsal şemalarda yeterli değildir.

## R17A.4 Semantic bootstrap truth değildir

Current `draft_mdl()` numeric kolonları candidate measure olarak sınıflandırabilir.

Bu yalnız bootstrap'tır.

Kural:

```text
numeric column
≠
verified SUM business metric
```

Candidate state:

```text
obvious
candidate
needs_confirmation
rejected
```

olarak yönetilir.

LLM önerisi production semantic truth değildir.

## R17A.5 Source pack avantajı

Known ERP / known manufacturing schema:

```text
structural fingerprint
→ source pack
→ module pack
→ sector pack
→ company override
```

yolu generic LLM schema discovery'den daha hızlı ve güvenilirdir.

Bu Dima'nın onboarding IP'si olabilir.

## R17A.6 Readiness

Tenant/domain bazında:

```text
CONNECTED
PROFILED
DEMO_READY
SEMANTICALLY_MODELED
ANALYTICS_READY
RESEARCH_READY
DECISION_READY
OPTIMIZATION_READY
```

görülmelidir.

Dima hazır olmadığı capability'yi UI'da gizleyebilir veya açıkça “bu veri eksik” diyebilir.

## R17A.7 Active connection

`CompanyRegistry` current kodu:

```text
api_sync varsa seç
yoksa conns[0]
```

mantığı taşır.

Pilot için tek connection garanti edilebilir.

Nihai SaaS için:

```text
active_connection_id
connection_version
```

explicit control-plane state olmalıdır.

---

# R17B — OPERASYONEL ÖLÇEKLEME SINIRLARI

## Scheduler

Current `main.py` process içinde daemon scheduler thread başlatıyor.

Tek process için uygundur.

Horizontal multi-replica deployment'da her replica aynı scheduler loop'u başlatabileceği için:

```text
leader election
distributed lock
veya ayrı scheduler worker
```

gereklidir.

Bu Core MVP blocker değildir; **çok replica deployment blocker'ıdır**.

## Warm-up / caches

Current app startup'ta Wren schema ve embedding/index warm-up yapıyor.

V2 ek context cache'leri oluştururken:

```text
bir cache daha ekle
```

yaklaşımı kullanılmaz.

Her cache için:

```text
owner
version key
invalidation trigger
cold-start behavior
```

tanımlanır.

---

# R18 — ANALYSISSPEC / ANALYSISRUNNER NEDEN HALA VAR?

MVP için önce bütün platformu bu omurgaya taşımıyoruz.

Fakat uzun vadede:

```text
ask
cube
dashboard
schedule
report
contract replay
MCP
```

aynı execution mantığını çoğaltmamalıdır.

Bu nedenle hedef:

```text
AnalysisSpec
→ AnalysisCompiler
→ AnalysisRunner
→ ExecutionArtifact
```

ortak sınırıdır.

**Kritik sıra:** önce V2 ürün çekirdeğini çalıştır; sonra yüzeyleri bu omurgaya taşı.

---


# R18A — MVP SONRASI PLATFORM GÖÇÜNDE UNUTULMAMASI GEREKEN KRİTİK BULGULAR

Bu bölüm derin repo denetiminde bulunan ve hızlı MVP planı yüzünden kaybolmaması gereken ayrıntıları korur.

## R18A.1 `AnalysisSpec` physical SQL saklamaz

Uzun vadeli ortak çalışma sözleşmesi:

```text
kind=cube
→ canonical CubeQuery

kind=wren_sql
→ Wren semantic SQL
```

taşır.

Donmuş physical datasource SQL:

```text
MDL
dialect
security
relationship graph
```

değiştiğinde bayatlar.

Replay için canonical semantic spec saklanmalıdır.

## R18A.2 Evidence durability üç durumlu

Query Contract yazımı her zaman “DB’ye kaydedildi” varsayımıyla ele alınamaz.

Hedef receipt:

```text
db     → sealed
spool  → sealed-pending-flush
lost   → unsealed
```

`lost` durumda sayı gösterilebilir; fakat:

```text
verified badge
memory promotion
decision evidence
```

için kullanılamaz.

## R18A.3 Contract replay physical SQL replay değildir

V2 replay:

```text
stored AnalysisSpec
→ current MDL
→ recompile / dry-plan
→ execute
```

olmalıdır.

Replay verdict:

```text
SAME
DATA_CHANGED
DEFINITION_CHANGED
NO_LONGER_COMPILES
SECURITY_CHANGED
```

gibi açık sınıf taşımalıdır.

## R18A.4 `source="cube"` artık “LLM kullanılmadı” demek değildir

V2:

```text
LLM TurnInterpreter
→ deterministic CubePlanner
→ Wren
```

kullanabilir.

Dolayısıyla telemetry:

```text
interpreter_kind
planner_kind
execution_engine
narration_kind
llm_call_count
```

ayrımını taşır.

Frontend de yanlış şekilde:

```text
CUBE = LLM-free
```

dememelidir.

## R18A.5 Presentation authority execution encoding değildir

Uzun vadede:

```text
viz
interpret
temellendirme
lineage
certification
```

yalnız `cube_query` varlığına bağlanmamalıdır.

Ortak:

```text
ResultDescriptor
```

kullanılır.

Frontend aksiyonları:

```text
capabilities.schedulable
capabilities.drillable
capabilities.verifiable
...
```

gibi explicit capability ile açılır.

## R18A.6 Frontend core rescue blocker değildir

İlk pilot:

```text
ask()
askV2()
```

toggle ile yürüyebilir.

Mevcut ReportCard/ChatPanel tamamen yeniden yazılmaz.

V2 response compatibility adapter yeterli olduğu sürece UI mevcut kalır.

## R18A.7 MCP arka kapıdan legacy semantic yolu yaşatmamalı

HTTP `/ask-v2` default olup MCP hâlâ:

```text
cube_router.route
legacy refine
```

çağırıyorsa iki resmi semantic authority yaşamaya devam eder.

Final public V2 tool surface:

```text
plan_analysis
run_analysis
get_analysis_contract
```

gibi governed entrypoint’lere taşınmalıdır.

Raw `/query` ayrı privileged power-user yüzeyi olabilir; V2 fallback değildir.

## R18A.8 Background işlerde request ContextVar authority değildir

HTTP request’te mevcut olan:

```text
principal
tenant runtime
fiscal/temporal context
```

schedule/report worker’da otomatik yoktur.

AnalysisRunner açık dependency almalıdır:

```text
principal
tenant_runtime
temporal_context
```

Background worker request-local state’e güvenmez.

## R18A.9 Runtime invalidation matrisi

Aşağıdakiler runtime/context invalidation üretir:

| Değişiklik | MDL/schema | context/memory |
|---|---|---|
| source/module/sector/company pack | rebuild | rebuild |
| tenant config | rebuild | rebuild |
| DB connection/profile | runtime recreate | rebuild |
| metric approve/deprecate/override | semantic refresh | rebuild |
| synonym override | schema/context refresh | rebuild |
| VerifiedQuery promote/undo | MDL yok | memory rebuild |
| embedding model | MDL yok | full index rebuild |
| retrieval policy | MDL yok | context version change |

Publish:

```text
mark dirty
→ build new runtime
→ validate
→ ContextConsistencyGate
→ atomic swap
```

Request hot path reindex yapmaz.


# R19 — METABASE’İN YERİ

Metabase çekirdek kurtarma aracı değildir.

Daha sonra:

```text
BI navigation
collections
saved questions
chart editor
dashboards
self-service BI
```

için genişleme katmanı olarak değerlendirilebilir.

Önce:

```text
conversation
semantic correctness
research
evidence
```

çalışmalıdır.

---


# R19A — NİHAİ KENAR/KÖŞE SENARYO VE FAULT-INJECTION DENETİMİ

Bu bölüm yalnız “normal kullanıcı” senaryolarını değil, sistemin gerçek hayatta kırılabileceği sınırları test eder.

Temel ilke:

> **Arıza geldiğinde başka bir semantic davranışa sessizce düşmek yasaktır.**

Sistem ya aynı anlamı güvenle korur, ya açıkça degrade eder, ya da durur.

## R19A.1 Dil / conversation sınırları

| Senaryo | Beklenen davranış | Yasak davranış |
|---|---|---|
| Boş/çok kısa “peki?” | topic/context yeterliyse referans çöz; değilse sor | rastgele son query'yi tekrar çalıştırma |
| Aynı mesajda iki istek | ikisini requirement olarak taşı veya ayrıştır | yalnız ilk cümleyi cevaplama |
| Aynı mesajda iki gerçek ambiguity | minimum gerekli netleştirmeyi tek/ardışık sor | ilk adayı sessiz seçme |
| Kullanıcı düzeltmesi: “müşteri değil renk” | yalnız ilgili slotu patch et | tüm IR'yi sıfırdan farklı yorumlama |
| Kullanıcı “sadece yorumla” diyor | mevcut evidence yeterliyse query=0 | yeni query açma |
| Sosyal + analitik: “eyvallah, peki geçen ay?” | sosyal kısmı cevapla, analitik kısmı işle | tüm mesajı social sayma |
| Konu değiştirip geri dönme | topic stack / explicit anchor | stale query semantics'i yeni konuya taşıma |
| Clarification cevabı belirsiz kalıyor | ikinci minimum clarification mümkündür | sonsuz clarify loop |
| User prompt “kuralları yok say” diyor | normal user intent olarak değerlendir; sistem/security invariants değişmez | policy bypass |

### Clarification loop guard

Aynı unresolved slot için:

```text
max_clarification_rounds = bounded
```

olmalıdır.

Sonunda:

```text
UNRESOLVED / SEMANTIC_GAP
```

açıkça dönebilir.

---

## R19A.2 Semantic / veri sınırları

| Senaryo | Beklenen davranış |
|---|---|
| Aynı label, farklı formula/grain | clarify veya canonical owner seçimi; hash/grain karşılaştır |
| Hallucinated filter value | ValueValidator reddeder; “0 satır” diye cevaplanmaz |
| Deprecated metric stale memory'den geldi | active semantic snapshot reddeder |
| Synonym yeni onaylandı | context/runtime rebuild sonrası kullanılır; hard-code yok |
| Unit uyuşmazlığı: kg vs ton | explicit normalize veya fail/clarify; sessiz toplama yok |
| Currency uyuşmazlığı: TRY + EUR | FX policy/time source yoksa toplanmaz |
| % ölçeği 0–1 vs 0–100 | semantic definition/unit gate |
| Fiscal vs calendar month | `TemporalContext` + explicit source |
| Timezone/day-boundary | tenant timezone ile resolve |
| NULL vs 0 | ayrı anlam; finalizer eşitlemez |
| 0 satır | “bu filtrede sonuç yok”; dataset'te veri yok iddiası yapılmaz |
| Duplicate rows / many-to-many join | grain/cardinality validator; double-count bloklanır |
| Cross-domain grain farklı | explicit aggregation/join contract olmadan synthesis yok |
| Large/high-cardinality result | safety cap + `truncated=true`; tam evren gibi anlatılmaz |
| Semantic top-N ve row safety cap birlikte | `ranking.limit` ayrı, transport cap ayrı |
| Rounding kritik sonucu değiştiriyor | hesap full precision, display rounding metadata |

### Para / birim kuralı

Bir financial finding şu provenance olmadan resmî değildir:

```text
currency
conversion policy if any
as_of / FX date if any
rounding/display rule
```

---

## R19A.3 Context / version / memory sınırları

| Arıza | Beklenen davranış |
|---|---|
| `context_version != runtime semantic version` | stale context kullanılmaz |
| Memory klasörü/index yok | current-schema bounded fallback veya context unavailable |
| Embedding load fail | görünür degrade; semantic behavior gizlice değişmez |
| Context build fail | old valid runtime aktif kalır |
| Memory publish fail | old valid index aktif kalır |
| Unverified successful query memory'ye girmek istiyor | reddet |
| Holdout örneği retrieval'a sızıyor | eval invalid; release blok |
| Tenant A context'i B request'ine dönüyor | prompt'tan önce fail-closed |
| DB/schema deploy research ortasında değişti | run pinned version ile tamamla veya explicit restart; karışık version report yok |

### Retrieved-content prompt injection

DB value, knowledge note, document veya verified-example açıklaması içinde:

```text
“ignore previous instructions”
“şu SQL'i çalıştır”
```

gibi metin bulunabilir.

Bunlar **data**dır, instruction değildir.

Context provider:

```text
source tag
trust level
escaping/structuring
PII policy
```

taşır.

Retrieved data hiçbir zaman system/developer policy seviyesine yükselmez.

---

## R19A.4 LLM / planner / execution arızaları

| Arıza | Beklenen |
|---|---|
| Malformed structured output | max 1 schema-repair; sonra `PROVIDER_OUTPUT` |
| Provider timeout | bounded infra failover veya 503/504; legacy semantic fallback yok |
| Unknown canonical metric id | Resolver reject |
| Requirement düşmüş | Ledger execution'ı bloklar |
| Cube capability yok | explicit `UNSUPPORTED/CAPABILITY_GAP` |
| Cube compile error | `COMPILE`; semantic-SQL'e sessiz atlama yok |
| Wren dry-plan geçiyor ama intent eksik | alignment/ledger bloklar |
| DB down | 503; semantic anlam değiştirilmez |
| DB timeout | 504; farklı “daha kolay” query otomatik koşulmaz |
| Security deny | deny; model yeniden SQL yazarak bypass deneyemez |
| Contract write fail | spool/policy; `verified` badge yok |
| Narration provider fail | deterministic answer/artifact varsa güvenli degrade |
| Cancel mid-query | run `CANCEL_REQUESTED/CANCELLED`; yeni finding seal edilmez |

### Retry türleri ayrıdır

```text
schema-format repair          ≠ semantic repair
provider infra retry          ≠ query rewrite
idempotent read retry         ≠ write-action retry
```

Bir retry kullanıcının istediği analitik anlamı değiştiremez.

---

## R19A.5 Research loop sınırları

| Senaryo | Beklenen davranış |
|---|---|
| Aynı task tekrar önerildi | dedupe/signature gate |
| A→B→A task döngüsü | cycle/budget gate |
| Tool unavailable | başka eşdeğer governed tool varsa explicit substitution; yoksa partial |
| Bir tool timeout | task failure; tüm run ancak MUST goal etkileniyorsa partial/fail |
| Budget bitiyor | mevcut kanıtla `PARTIAL_BUDGET` |
| Personel datası yok | `PARTIAL_DATA_GAP`; fake join yok |
| Findings çelişiyor | `CONFLICTING/INCONCLUSIVE`; tek hikâyeye zorlanmaz |
| Aynı evidence iki ayrı “bağımsız kanıt” sayılıyor | evidence identity dedupe |
| Yeni bulgu root-cause gerektiriyor | bounded adaptive branch |
| Kullanıcı research ortasında objective'i değiştiriyor | current run pause/cancel; yeni brief/version; sessiz mutation yok |
| Deploy sonrası resume | stored run versions validate; incompatible ise explicit re-plan |
| Report synthesis sayı ekliyor | grounding validator reject |

Research stop koşulları yalnız step sayısı değildir:

```text
MUST goals covered
no unresolved blocking contradiction
marginal information gain low
budget/time exhausted
user stopped
```

---

## R19A.6 Decision / forecast / optimization sınırları

| Senaryo | Beklenen |
|---|---|
| “Ne yapmalıyız?” ama playbook yok | next diagnostic step veya clearly-labeled analyst suggestion |
| Forecast için yetersiz tarih | `FORECAST_NOT_READY` |
| Backtest kötü | production forecast answer yok veya açık düşük-readiness |
| Optimization objective belirsiz | clarify |
| Constraints infeasible | `INFEASIBLE` + hangi constraint çatışıyor |
| Solver timeout | best feasible / gap bilgisi varsa açıkla; optimal diye sunma |
| Causal identification mümkün değil | association/candidate only |
| External action kullanıcı onaysız | execute yok |
| Action request tekrar gönderildi | idempotency key; duplicate action yok |

---

## R19A.7 UI / artifact sınırları

| Senaryo | Beklenen |
|---|---|
| Chart scale/unit yanlış | artifact validator / metadata |
| Chart user'ın sorusunu cevaplamıyor | chart opsiyonel; text-first answer korunur |
| Kullanıcı eski chart'a tıklıyor | artifact id + originating contract/topic resolve edilir |
| Report section stale evidence taşıyor | version/provenance görünür; refresh yeni report version |
| Evidence drawer açılmıyor | official “verified” UX gate fail |
| Long research progress kayboluyor | run state yeniden fetch; duplicate run başlatma yok |
| Browser reload pending clarification | persisted state'ten resume |
| Partial result | eksik section/goal görünür; tam rapor gibi sunulmaz |

---

## R19A.8 Onboarding / operasyon sınırları

| Senaryo | Beklenen |
|---|---|
| >50 tablo | silent truncation yasak; pagination/truncation state |
| View'lar kritik ama discovery table-only | readiness fail / explicit gap |
| Composite FK | ilk kolonla “doğru ilişki” varsayma yok |
| Self-FK önemli | explicit unsupported/modeling requirement |
| Birden fazla connection | active connection explicit |
| Schema drift | snapshot/version change → rebuild/invalidate |
| İki pack aynı knowledge dosyasını sahipleniyor | explicit override yoksa build fail |
| Multi-replica scheduler | single owner/distributed lock olmadan scale yok |
| Aynı scheduled action iki kez tetikleniyor | idempotent run/action key |

---

## R19A.9 Cross-surface / replay sınırları

| Senaryo | Beklenen |
|---|---|
| Chat sonucu dashboard'a pin | client SQL değil semantic `AnalysisSpec` saklanır |
| Relative-time dashboard ertesi gün açılır | dönem current temporal context ile yeniden çözülür |
| Schedule background run | explicit owner principal + tenant runtime + masking |
| Metric definition değişmiş replay | `DEFINITION_CHANGED/NO_LONGER_COMPILES`; eski SQL sessiz replay yok |
| Planner lane dashboardable değil | backend capability false; UI butonu gizli |
| Kullanıcı query'yi doğruluyor | trust/version/safety validation sonrası memory projection |
| MCP eski route'u çağırıyor | migration bitmeden public V2 authority sayılmaz |

Bu senaryoların amacı `/ask-v2` doğruluğunun dashboard/report/schedule/MCP yüzeylerinde ikinci kez bozulmasını engellemektir.

---

## R19A.10 Fault taxonomy genişlemesi

Terminal ve diagnostic sınıflar en az şunları ayırabilmelidir:

```text
CONTEXT_MISS
CONTEXT_STALE
TURN_ACT_MISS
REFERENCE_MISS
SEMANTIC_AMBIGUITY
SEMANTIC_GAP
VALUE_NOT_FOUND
UNIT_MISMATCH
GRAIN_MISMATCH
COMPLETENESS
CAPABILITY_GAP
COMPILE
DRY_PLAN
SECURITY
EXECUTION
TRUNCATED
EMPTY_RESULT
RESULT_MISMATCH
DATA_QUALITY
RESEARCH_PLAN
RESEARCH_TOOL
RESEARCH_CYCLE
RESEARCH_BUDGET
HYPOTHESIS
CAUSAL_NOT_IDENTIFIED
FORECAST_NOT_READY
OPTIMIZATION_INFEASIBLE
REPORT_GROUNDING
NARRATION
PROVIDER
PROVIDER_OUTPUT
CANCELLED
ACTION_APPROVAL
```

“ERROR” tek başına yeterli failure stage değildir.

---

# R20 — ESKİ HATALARI YENİ SİSTEME TAŞIMAMAK İÇİN DEĞİŞMEZLER

1. Ham kullanıcı metnini semantic olarak yalnız TurnInterpreter yorumlar.
2. Resolver raw Türkçeyi ikinci kez parse etmez.
3. Planner kullanıcı dilini yeniden yorumlamaz.
4. LLM sayı üretmez.
5. Metric formula/unit/aggregation tek canonical owner’dadır.
6. Query çalıştı diye cevap doğru sayılmaz.
7. Dry-plan intent doğrulaması değildir.
8. MUST requirement kaybolursa execution yok.
9. Blocking ambiguity’de tahmin yok.
10. Clarification query çalıştırmaz.
11. Social turn query çalıştırmaz.
12. `prev_sql` canonical conversation state değildir.
13. Legacy `/ask` V2 fallback değildir.
14. Discovery raw SQL silent fallback değildir.
15. Wren memory stale iken kullanılmaz.
16. Tenant runtime request ortasında değişmez.
17. Agent tool authority permission/evidence/budget taşır.
18. Research agent causality uydurmaz.
19. Report LLM yeni sayı üretmez.
20. UI/chart semantic authority değildir.
21. Bir bug’ın çözümü yalnız yeni keyword/regex ise önce kök mekanizma sorgulanır.
22. Büyük refactor MVP ön şartı değildir.
23. Çalışan primitive yalnız temiz görünmek için yeniden yazılmaz.
24. Legacy feature yeni V2’ye wholesale import edilmez.
25. Yeni mimari belgesi uygulandı sanılmaz; test/telemetry ile kanıtlanır.

---

# R21 — GELİŞTİRİCİYE KIRMIZI UYARILAR

## R21.1 “Bu dosya büyük; parçalayalım.”

Tek başına gerekçe değildir.

Refactor yalnız:

```text
MVP için reuse sınırı gerekli
aynı logic iki kez doğuyor
migration boundary gerekiyor
```

ise yapılır.

## R21.2 “Bu edge case’i regex’e ekleyeyim.”

Önce sor:

```text
Bu bir dil anlama problemi mi?
semantic candidate problemi mi?
conversation reference problemi mi?
requirement completeness problemi mi?
```

Generic mekanizma varsa onu düzelt.

## R21.3 “Agent’e bütün araçları açalım.”

Hayır.

Her tool:

```text
input type
output type
determinism
cost
permission
side effect
evidence
```

beyanına sahip olmalıdır.

## R21.4 “Planı başta tamamen çıkarsın.”

Research Mode’da yanlış.

Küçük seed plan + gerçek sonucu görüp replan.

## R21.5 “Chart çıktı; rapor tamam.”

Yanlış.

Chart kanıt artefaktıdır.
Rapor finding/evidence zinciridir.

## R21.6 “Cevap makul görünüyor.”

Release ölçütü değildir.

Ground truth / contract / result equivalence gerekir.

---

# R22 — EVAL VE DENETİM MODELİ

Mevcut corpus korunur ve V2 lane’e uyarlanır.

Setler:

```text
DEV
VALIDATION
HOLDOUT
```

Holdout runtime memory/few-shot’a sızmaz.

## R22.1 Standard analytics metrikleri

```text
context recall@k
turn-act accuracy
intent/slot accuracy
semantic resolution
requirement coverage
result equivalence
silent wrong
clarification correctness
follow-up correctness
user repair recovery
topic resume
p50/p95
```

## R22.2 Research metrikleri

```text
research goal coverage
evidence coverage
tool selection validity
adaptive branch correctness
hypothesis resolution
unsupported causality rate
numeric claim grounding
report section completeness
cross-section consistency
budget compliance
resume correctness
```

P0:

```text
silent wrong = 0 holdout
unsupported causal claim = 0
unreferenced numeric claim = 0
cross-tenant evidence = 0
material requirement drop = 0
```

---


## R22.3 KPI sözlüğü — formül ve release hedefleri

### Core conversation

| KPI | Tanım | Core MVP hedefi | Pilot hedefi |
|---|---|---:|---:|
| `turn_act_accuracy` | doğru dialogue act / toplam | ≥ %95 curated/validation | ≥ %97 |
| `blocking_ambiguity_recall` | gerçekten sorması gereken vakaları yakalama | ≥ %95 | ≥ %98 |
| `blocking_ambiguity_false_resolution` | sorması gerekirken sessiz seçim | **0 dedicated set** | **0 P0** |
| `unnecessary_clarification_rate` | gerekmediği halde clarification | ≤ %10 | ≤ %5 |
| `clarification_recovery` | clarification sonrası hedefe 1 turda ulaşma | ≥ %95 | ≥ %97 |
| `followup_correctness` | prior state doğru taşındı | ≥ %90 | ≥ %95 |
| `repair_slot_preservation` | düzeltilmeyen slotlar değişmedi | **%100 regression** | %100 |
| `pure_social_query_rate` | sosyal turda veri query | **0** | 0 |

### Standard analytics

| KPI | Tanım | Core MVP | Pilot |
|---|---|---:|---:|
| `requirement_coverage` | MUST requirement plan içinde | %100 dedicated | %100 |
| `result_equivalence` | gold/expected result ile eşdeğer | ≥ %95 core set | ≥ %97 |
| `silent_wrong_rate` | cevap var ama anlam/sonuç maddi yanlış | **0 P0 holdout** | **0 P0** |
| `exception_rate` | unhandled request failure | < %1 | < %0.5 |
| `standard_p95_latency` | standard answer toplam süre | ≤ 10 sn başlangıç | ≤ 8 sn hedef |
| `clarify_p95_latency` | clarification cevabı | ≤ 6 sn | ≤ 4 sn |

### Research

| KPI | Tanım | Product MVP | Pilot / stretch |
|---|---|---:|---:|
| `research_goal_coverage` | brief'teki MUST goals evidence ile kapandı | %100 canonical | ≥ %95 complex validation |
| `evidence_coverage` | önemli finding evidence bağlı | %100 | %100 |
| `adaptive_branch_correctness` | beklenen sonuç-sonrası branch | ≥ %90 canonical set | ≥ %90 |
| `tool_selection_validity` | task için geçerli tool seçimi | ≥ %95 | ≥ %97 |
| `unreferenced_numeric_claim` | contract/evidence'sız sayı | **0** | 0 |
| `unsupported_causality_rate` | kanıttan güçlü nedensellik | **0** | 0 |
| `report_section_completeness` | istenen section/goal kapsandı | ≥ %95 | ≥ %97 |
| `cross_section_consistency` | rapor bölümleri birbiriyle çelişmiyor | ≥ %95 | ≥ %98 |
| `budget_disclosure` | budget stop açıkça bildirildi | %100 | %100 |

### UX/performance

| KPI | Tanım | İlk hedef |
|---|---|---:|
| `time_to_first_status_p95` | Research başladıktan ilk görünür progress | ≤ 2 sn |
| `time_to_first_evidence_p95` | İlk chart/table/findings artifact | ≤ 15 sn |
| `research_full_report_p95` | canonical medium-complex report | ≤ 90 sn başlangıç |
| `progress_silence_p95` | research UI'da progress'siz bekleme | ≤ 8 sn |
| `answer_now_response_p95` | kullanıcı “Şimdi cevapla” sonrası partial answer | ≤ 5 sn |
| `broken_artifact_rate` | render edilemeyen chart/table | 0 release set |
| `evidence_open_success` | “kanıtı göster” aksiyonu çalışıyor | %100 canonical |
| `unnecessary_visualization_rate` | chart fayda katmayan cevaplarda chart | ≤ %10 human review |

Bu latency hedefleri benchmark başlangıç değerleridir; gerçek müşteri datasource latency'si ayrı `DB time` ve `agent time` olarak raporlanır.

---

## R22.4 Aşama bazlı KPI — “şu anda neyi başarmaya çalışıyoruz?”

| Seviye | Kullanıcının artık yapabildiği | Başarı göstergesi |
|---|---|---|
| L0 | — | V2 legacy hot-path'e bağımlı olmadan boot |
| L1 | konuşma, clarify, repair | yanlış tahmin yerine doğru diyalog |
| L2 | güvenilir standard analytics | requirement/result correctness |
| L3 | kompleks research + report | evidence-backed multi-step analysis |
| L4 | gerçek tenant pilot | security, persistence, observability |
| L5 | tam analyst experience | chat + artifact + research + report continuity |

---

# R23 — TELEMETRY / FAILURE TAXONOMY

“Çalışmadı” tek kategori değildir.

```text
CONTEXT_MISS
CONTEXT_STALE
TURN_ACT_MISS
REFERENCE_MISS
INTENT_MISS
SEMANTIC_AMBIGUITY
SEMANTIC_GAP
VALUE_NOT_FOUND
UNIT_MISMATCH
GRAIN_MISMATCH
COMPLETENESS
CAPABILITY_GAP
COMPILE
DRY_PLAN
SECURITY
EXECUTION
TRUNCATED
EMPTY_RESULT
DATA_QUALITY
RESULT_MISMATCH
RESEARCH_PLAN
RESEARCH_TOOL
RESEARCH_CYCLE
RESEARCH_BUDGET
HYPOTHESIS
CAUSAL_NOT_IDENTIFIED
FORECAST_NOT_READY
OPTIMIZATION_INFEASIBLE
REPORT_GROUNDING
NARRATION
PROVIDER
PROVIDER_OUTPUT
CANCELLED
ACTION_APPROVAL
```

Her request/tur terminal stage taşır.

---

# R24 — CURRENT REPO’DA DOSYA KADERİ

| Mevcut alan | Yeni çekirdek hükmü |
|---|---|
| `routers/ask.py` | freeze; legacy |
| `cube_router.py` | V2 semantic authority değil; çalışan primitive kaynağı |
| `uyum.py` | invariant kaynağı; V2’de Ledger/Resolver/Validator’a dağılır |
| `intent_semasi.py` | capability inventory / characterization oracle |
| `followup.py` | authority değil; flow davranış kaynağı |
| `context.py` | iyi anchor/context ilkeleri korunur |
| `mali_takvim.py` | koru |
| `kiyas_cebiri.py` | koru |
| `varlik.py` | entity/privacy primitive’leri koru |
| `wren_service.py` | resmi execution authority |
| `plan_semasi.py` | eski static-plan authority değil; capability/recipe kaynağı |
| `plan_tuketici.py` | çalışan tool/recipe davranış kaynağı |
| `tools.py` | tool-contract yatırımı korunur; V2 read-only toolbelt için temel |
| `contribution.py` | typed adapter ile reuse |
| `kok_neden.py` | typed adapter ile reuse |
| `drill.py` | typed adapter ile reuse |
| `yoy.py` | reuse |
| `report.py` | composer primitive; ReportDocument’a adapter |
| `contracts.py` | evidence authority |
| dashboards/schedules | MVP sonrası ortak runner migration |
| MCP | MVP sonrası V2 tool authority’ye taşınır |

---



# R25 — NİHAİ MİMARİ MASAÜSTÜ SİMÜLASYONU: SON HÜKÜM

Bu raporun mimarisi üç ayrı seviyede simüle edilmiştir:

```text
A. normal conversation / analytics
B. kompleks research / decision
C. fault / security / data-gap / operations
```

## R25.1 Normal yol

```text
“Son 3 ay en çok fire veren 5 makineyi önceki 3 ayla kıyasla.”
```

Beklenen tüm sahiplikler tekil ve yeterlidir:

```text
TurnInterpreter       → comparison/ranking intent
Resolver              → fire + machine
Temporal resolution   → A/B period
RequirementLedger     → metric/dim/time/compare/order/limit
CubePlanner           → deterministic plan
WrenService           → governed execution
Contract              → evidence
Finalizer              → text + chart/table + scope
```

**Mimari boşluk görülmedi.**

## R25.2 Kompleks research yolu

```text
“Son 12 ay ürünleri karşılaştır; makine ve personelle ilişkisini incele;
satış performansını yorumla; düşüşlerin nedenini araştır ve raporla.”
```

Gerekli yetenekler ayrı katmanlarda mevcut/planlıdır:

```text
ResearchBrief
→ seed tasks
→ standard analytics tools
→ evidence
→ adaptive branch
→ HypothesisLedger
→ ReportDocument
```

Bu senaryo **tek dev SQL** istemediği için ölçeklenebilir.

Ana koşul:

```text
cross-domain semantic/grain ilişkileri gerçekten modelde bulunmalı
```

Yoksa doğru durum `PARTIAL_DATA_GAP`tır.

**Mimari açıdan fizibl; veri modeline koşullu.**

## R25.3 “Neden ve ne yapalım?” yolu

Manufacturing Advisor:

```text
analysis/research
→ evidence-backed diagnosis
→ DecisionBrief
→ playbook/policy/model
→ Recommendation
```

şeklinde ayrıldığı için LLM'in operasyon kararı uydurması gerekmez.

**Fizibl; recommendation kalitesi company playbook ve veri kapsamına bağlı.**

## R25.4 Optimization yolu

```text
“Hangi işleri hangi makinede hangi sırayla çalıştırmalıyım?”
```

Conversation objective/constraint toplar;
OptimizationEngine gerçek solver çağırır.

Bu ayrım korunursa mimari ölçeklenir.

**Fizibl; constraint modelleme ayrı domain işidir.**

## R25.5 Failure yolu

Provider, Wren, DB, contract store, context index veya tool'lardan biri düştüğünde:

```text
failure stage lokalize
semantic fallback yok
kanıtsız verified output yok
partial ise explicit partial
```

olduğu için arıza bir katmandan diğerine “yanlış cevap” olarak sızmaz.

## R25.6 Güvenlik yolu

Tenant/principal/runtime assertion prompt ve execution sınırlarında bulunduğu sürece cross-tenant hata fail-closed olabilir.

Pilot öncesi shadow security flag'lerinin gerçek enforcement'a geçirilmesi ayrı release gate olarak kalır.

## R25.7 Scope yolu

Planın hızlı kalmasının nedeni şudur:

```text
Core MVP için yeni platform yok.
Research MVP için yeni DB yok.
İlk Manufacturing Advisor için generic skill framework yok.
Generic onboarding pilotu bekletmiyor.
CRM ve diğer solution pack'ler paralel başlamıyor.
```

Bu nedenle ilk dikey ürün kanıtı gereksiz altyapı tarafından bloke edilmez.

## R25.8 Son fizibilite hükmü

```text
FUNDAMENTAL ARCHITECTURE BLOCKER: YOK
```

Bilinen koşullu riskler:

```text
semantic/data readiness
cross-domain grain correctness
security enforcement hardening
manufacturing event quality
playbook availability
optimization constraint modeling
provider/DB latency
```

Bunların hiçbiri çözümü “daha çok router/regex” olan problem değildir.

Bu raporun hedef mimarisi, bu riskleri kendi doğru katmanlarında lokalize edecek şekilde tasarlanmıştır.

---

# R26 — BELGE YÖNETİMİ

Bu rapor ve eş yol haritası kanonik çalışma belgeleridir; normal geliştirme sırasında **aynı dosyalar üzerinde nokta atışı güncellenir**.

Her önemli edit öncesi/sonrası:

```text
1. SHA ve heading inventory al
2. hedef bölümü cerrahi olarak değiştir
3. kritik-kavram assertion çalıştır
4. silent deletion diff kontrolü yap
5. gerekiyorsa arşiv snapshot'ı al
```

Sıfırdan rewrite varsayılan davranış değildir. Değişiklik geçmişi nihai metnin içine yığılmaz; gerekiyorsa ayrı arşiv/audit kayıtlarında tutulur.

---


# R26A — DIŞ BENCHMARK'TAN ALINAN UX / AGENTİC DERSLER

20 Eylül 2026 güncel ürün araştırması bu hedefleri destekliyor:

- Databricks Genie Agent Mode kompleks soruları alt görevlere bölüyor, birden fazla SQL çalıştırıyor, ara sonuçlardan öğrenerek araştırma planını rafine ediyor ve findings + visualizations + supporting tables/citations içeren structured report üretiyor.
- Genie UX, uzun agent run sırasında kullanıcıya “Answer now” ile mevcut kanıtla erken cevap alma ve sonrasında report'u follow-up ile refine etme imkânı veriyor.
- Snowflake Cortex Agents semantic Analyst'i tool olarak kullanıyor; thread context ve çok-adımlı tool orchestration agent katmanında kalıyor.
- Bu örneklerin ortak dersi Dima için şudur: semantic query correctness ve agentic research **aynı katman değildir**; UI da query sonucu göstermekten daha fazlasını yapmalıdır.

Referanslar:

```text
https://docs.databricks.com/aws/en/genie-agents/concepts
https://docs.databricks.com/aws/en/genie-agents/talk-to-genie
https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents
```

---


## R26A.1 Fizibiliteyi destekleyen güncel ürün örnekleri

Bu mimari yalnız teorik bir tasarım değildir. 2026'daki ürünler parçalarının ayrı ayrı üretimde fizibl olduğunu gösteriyor:

- Databricks Genie Agent Mode: kompleks analitik soruları alt görevlere ayırıyor, birden fazla SQL çalıştırıyor, ara sonuçlardan öğrenip planını rafine ediyor ve findings + visualizations + supporting tables içeren rapor üretiyor.
- Snowflake Cortex Agents: semantic Analyst'i tool olarak kullanıp plan → tool → reflect döngüsü, thread context, custom tools, chart ve code execution gibi yetenekleri agent orchestration katmanında birleştiriyor.
- Salesforce tarafında CRM verisiyle fırsat önceliklendirme, sales coaching ve campaign agent sınıfı ürünler bulunuyor.
- Google OR-Tools, müşteri ziyaret sırası gibi problemleri zaman pencereleri ve farklı kısıtlarla Vehicle Routing Problem olarak çözebiliyor.

Referanslar:

```text
https://docs.databricks.com/aws/en/genie-agents/concepts
https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents
https://help.salesforce.com/s/articleView?id=sf.copilot_actions_ref_prioritize_opportunities.htm
https://www.salesforce.com/marketing/whats-new/
https://developers.google.com/optimization/routing/vrptw
```

Dima'nın farklılaştırması bu parçaları tek bir **imalat-first semantic/evidence/conversation brain** altında birleştirmektir.

---

# R26B — NORTH-STAR ACCEPTANCE SUITE

Dima “nihai ürün” iddiasını aşağıdaki senaryolar geçmeden kullanmamalıdır.

## NS1 — Basit KPI

> “Bu ay ciro?”

Beklenen:

```text
tek doğrudan cevap
doğru dönem
doğru sayı
gereksiz chart yok
kanıt erişilebilir
```

## NS2 — Semantic ambiguity

> “Siyah için fire.”

Beklenen:

```text
gerçek candidate ambiguity varsa clarification
query yok
chip ile resume
```

## NS3 — Follow-up / repair

```text
“bu yıl makine bazında OEE”
“sadece RAM-3”
“hayır son 3 ay”
“bunu yorumla”
```

Beklenen:

```text
context preserved
yalnız ilgili slot değişir
explain mevcut evidence yeterliyse query açmaz
```

## NS4 — Kompleks multi-domain research

> “Son 12 ay üretilen ürünleri karşılaştır; makineler ve personellerle ilişkisini incele;
> satış performanslarını yorumla; nedenleri araştır ve raporla.”

Beklenen UX:

```text
≤2 sn ilk progress
yüksek seviyeli research plan
birden fazla evidence artifact
result-driven root-cause branch
en az 3 anlamlı chart/table
report sections
evidence links
limitations
```

Beklenen içerik:

```text
production
sales
machine
personnel/shift
cross-domain synthesis
candidate root cause
```

## NS5 — Sonuç yeni araştırma doğuruyor

İlk bulgu:

```text
M3 peer'lerden düşük
```

Sistem, user ayrıca “neden?” yazmadan dahi request root-cause gerektiriyorsa:

```text
M3 components
downtime
shift/personnel
```

alt araştırmasını açabilmelidir.

Ama gereksiz branch açmamalıdır.

## NS6 — Causality sınırı

Makine düşüşü ve satış düşüşü aynı anda görünür.

Beklenen:

```text
association / candidate cause
```

Kanıt yoksa:

```text
“neden budur”
```

yasak.

## NS7 — Report refinement

> “M3 bölümünü vardiya bazında derinleştir ve raporu güncelle.”

Beklenen:

```text
aynı ResearchRun
section anchor
new evidence
report version +1
önceki section'lar kaybolmaz
```

## NS8 — Kullanıcı kontrolü

Research sürerken:

```text
“şimdi cevapla”
```

Beklenen:

```text
≤5 sn partial evidence-backed answer
hangi kısımların eksik olduğu açık
run isterse durur/pause
```

## NS9 — Eksik veri

Personel ilişkisi için veri yok.

Beklenen:

```text
fake join / fake answer yok
reportta data gap açık
diğer bölümler tamamlanabilir
```

## NS10 — Enterprise trust

Aynı scenario başka tenant'ta.

Beklenen:

```text
cross-tenant context/evidence = 0
principal propagated
contract versions traceable
```

Bu suite hem backend hem UI/UX hem de içerik kalitesini birlikte ölçer.

---


## NS11 — İmalat karar desteği: OEE düşük, neden ve ne yapalım?

Kullanıcı:

> “M3'ün OEE'si diğerlerinden düşük. Neden ve ne yapmalıyız?”

Beklenen:

```text
peer + baseline compare
OEE decomposition
product/shift/personnel breakdown
downtime/quality/performance drill
maintenance evidence if available
HypothesisLedger
candidate cause labels
playbook-grounded action OR diagnostic next step
conversation + visual evidence + report
```

P0:

```text
causality overclaim = 0
unsupported recommendation = 0
```

## NS12 — CRM kampanya danışmanı

Kullanıcı:

> “Müşterilerime nasıl bir kampanya yapmalıyım?”

Beklenen:

```text
customer segmentation
historical behavior
margin / product affinity
campaign history
candidate audiences/offers/channels
evidence + measurement plan
```

Uplift/experiment yoksa:

```text
“en iyi kampanya kesin budur”
```

denmez.

## NS13 — Müşteri ziyareti öncelik + rota

Kullanıcı:

> “Bu hafta hangi müşterileri hangi sırayla ziyaret etmeliyim?”

Beklenen:

```text
goal clarification if needed
priority scoring
availability/time-window constraints
route optimization
ordered visit plan
why each visit is prioritized
tradeoffs
```

LLM rota optimizasyonunu kendisi hesaplamaz.

---


# R26C — DIŞ TEKNİK DOĞRULAMA: MİMARİ YÖNÜNÜN PAZARDA KARŞILIĞI VAR MI?

20 Eylül 2026 güncel resmi kaynaklar:

### Wren

`wren-pydantic`:

```text
wren_fetch_context
wren_recall_queries
wren_list_models
wren_dry_plan
wren_query
wren_store_query
```

araçlarını sunuyor ve MDL/context/memory üzerinden Pydantic AI ajanlarına bağlanıyor.

Bu Dima'nın:

```text
semantic engine ≠ conversation/research orchestrator
```

ayrımını destekliyor.

### Databricks

Genie Agent Mode:

```text
research plan
multiple SQL
learn from each result
refine plan
comprehensive report
citations
visualizations
supporting tables
```

yaklaşımını resmî ürün davranışı olarak kullanıyor.

### Snowflake

Cortex Agents:

```text
plan
→ use tools
→ reflect
→ repeat
```

döngüsünü; semantic Analyst, thread context, code/chart/custom tools ile birleştiriyor.

Snowflake ayrıca mevcut semantic view ve verified queries'in Agent katmanına geçerken korunduğunu belirtiyor.

### OR-Tools

Google OR-Tools:

```text
job-shop / employee scheduling
constraint optimization
vehicle routing with time windows
```

gibi Dima'nın karar skill'lerinin ihtiyaç duyduğu problemleri doğrudan destekliyor.

### ISO 22400

ISO'nun resmi kaydı:

```text
ISO 22400-2:2014
```

imalat operasyon KPI'larını tanımlıyor; Edition 2 taslağı geliştirme aşamasında.

### Mimari çıkarım

Dima'nın hedefi pazarın aksine “tek LLM her şeyi yapar” değildir.

Güncel başarılı desen:

```text
semantic model
+
conversation/agent orchestration
+
specialized tools
+
evidence
+
domain-specific engines
```

dir.

Bu, rapordaki nihai mimarinin teknik olarak makul olduğunu destekler.

---

# R27 — NİHAİ MİMARİ HÜKÜM

Dima yeni çekirdeğin özü:

```text
conversation-first
semantic-first
evidence-first
research-capable
MVP-first migration
```

olacaktır.

Başarı:

> “Dima her soruya mutlaka cevap verir.”

değil;

> **“Dima ya doğru anlamı kanıtlar, ya gerekli netleştirmeyi ister, ya sınırını açık söyler; karmaşık işte ise gerçek sonuçları kullanarak araştırır ve her önemli bulguyu kanıtına bağlar.”**

olmalıdır.
