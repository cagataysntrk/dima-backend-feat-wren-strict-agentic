# DIMA Wren vs Metabase — Neutral Comparison & Audit Report

**Tarih:** 27 Eylül 2026  
**Durum:** Final karşılaştırma raporu — Round‑2 feature-complete benchmark ile güncellendi  
**Revision authority:** Round‑1 dört-vaka kıyası tarihsel ön karar; aşağıdaki **Round‑2 (10 özellik × 3 zorluk = 30 vaka)** nihai winner kararının esas kanıtıdır.  
**Amaç:** Wren tabanlı Dima ile Metabase/Metabot tabanlı Dima adaylarını; aynı ürün niyeti, aynı karşılaştırma vakaları ve mevcut mühürlü kanıtlar üzerinden bağımsız olarak denetlenebilir ve yeniden üretilebilir biçimde karşılaştırmak.  
**Ana karar (Round‑2 sonrası):** **Canonical production engine olarak Metabase/Metabot seçilmelidir.** Round‑2 sonucu bu kararı güçlendirdi. Wren production runtime olarak seçilmemeli; özellikle recursive research / hypothesis / root-cause orchestration fikirleri için referans tasarım ve Ar‑Ge kaynağı olarak korunmalıdır.

---

## 1. Yönetici özeti

Bu rapor iki adayın yalnızca "kaç test geçti?" sonucunu karşılaştırmaz. Aşağıdaki ayrımlar ayrı ayrı ele alınır:

1. Aynı kullanıcı isteğine verilen ürün tepkisi,
2. Gerçek analitik engine'in çalışıp çalışmadığı,
3. Evidence ve provenance üretimi,
4. Relationship ve adaptive research davranışı,
5. Root-cause davranışı ve epistemik sınırlar,
6. Causal overclaim ve invented numeric truth kontrolü,
7. Provider/model çağrı sayısı ve model topolojisi,
8. Latency,
9. Restart/security/governance kanıtları,
10. Mimari karmaşıklık ve duplicate-engine riski,
11. Dima'nın nihai ürün vizyonuna uygunluk,
12. Self-host / lisans etkisi,
13. Kararın yeniden üretilebilirliği.

### 1.1 Nihai sonuç

**Genel production foundation winner: Metabase/Metabot.**

Ancak bu karar "Metabase root-cause açısından Wren'den daha gelişmiş" anlamına gelmez. Tam tersine:

- **Current production closure / güvenli kapanış / maliyet topolojisi / platform kaldıracı:** Metabase daha güçlü.
- **Research depth / hypothesis lifecycle / adaptive investigation fikri / raw latency:** Wren daha güçlü sinyaller gösteriyor.
- **Current root-cause canlı sonucu:** Wren karşılaştırma koşusunda FAIL/PARTIAL ve sıfır Evidence; Metabase PASS/REPORT fakat governed limitation ile sığ kalıyor.
- **Dima'nın hedeflenen recursive root-cause vizyonu:** iki candidate da bugün tam olarak hedef seviyede değildir.

Bu yüzden önerilen nihai mimari:

```text
DIMA
  ├─ Research / Process Manager
  ├─ Evidence / Claim lineage
  ├─ Recursive investigation
  ├─ Hypothesis / root-cause epistemics
  ├─ Decision / Action / Outcome / Memory
  │
  └───────────────> METABASE / METABOT
                    analytical truth
                    query / metric / model
                    aggregation / breakdown
                    execution
                    native exploration
```

Wren'den alınacak olan **engine değil, araştırma mimarisi fikirleri** olmalıdır:

```text
competing hypotheses
counter-evidence
next discriminating test
adaptive branch
hypothesis ledger
bounded recursive deepening
explicit causal restraint
```

---

# 2. Karşılaştırmanın kapsamı

## 2.1 Wren adayı

Sealed branch:

```text
branch HEAD
feat/ask-v2-mvp
8f472fb252f1f81d7357c6edcdbedf89bf60f666
```

Mühürlü Product behavior:

```text
f7e565bb13e0668f85df071f6ecc70411314f9fd
```

Formal provider-free closure:

```text
workflow  v2-research-goal-task-final-closure
run       36247385449
result    GREEN
```

Recovery seal'in kendi beyanı:

```text
WREN GOAL/TASK AUTHORITY RECOVERY = SEALED
paid/provider calls in recovery    = 0
backend/app diff after Product     = ZERO
```

Formal closure test toplamı:

```text
5   goal-task quarantine
93  Day6.5 / preacceptance family
180 Day7 Research family
69  Day8 ROOT family
191 Day10 Product family
6   real-Wren relationship regression
7   real-Wren ROOT Product regression
---
551 total assertions/tests
```

Bu 551 sayı farklı test paketlerinin toplamıdır; hepsi paid/provider çağrısı değildir. Son iki grup gerçek Wren execution regresyonlarını kapsar, fakat final recovery closure provider-free'dir.

## 2.2 Metabase adayı

Branch HEAD:

```text
feat/dima-metabase-platform
72938742188b83427f303256b5168dbea61eead9
```

Comparison candidate behavior SHA:

```text
72641b39159f11b08757048ae96644438badcc20
```

Final candidate artifact:

```text
workflow run       36313727354
artifact id        10929618774
artifact name      dima-metabase-comparison-candidate
artifact digest    sha256:c842390a1d3850f58805411d0c3b0c50731acf56eed51a4405e0a740bcae0dcf
```

Engine identity:

```text
engine SHA      cbe313af9ac2d5960f662068e433d328d896fb06
release         0.63.18-dima.6
runtime tag     v0.63.18-dima.6
image digest    sha256:40e9a44be49904de3ddf12d4683c768e70955851c10a928a9c8f7d8f60780353
```

Final provider-free closure:

```text
run       36313727354
result    GREEN
```

Assertion toplamı:

```text
25  repository/security
111 headless Product closure
70  Core A / closed-loop / UX foundations
38  ActionAuthorization
29  Human Adoption
25  P21
19  P20
44  P19
24  P18
116 P17
6   P16
5   P15
15  P14
---
527 total assertions
```

Güncel gerçek Luna + gerçek Metabase Core-B closure:

```text
behavior SHA                    8b56fd56e864873b851ddbeeb5480abbd0a6dd28
run                             36311996172
result                          6 / 6 GREEN
observable model boundary units 19
Metabase analytical calls       8
silent wrong                    0
security violations             0
causal overclaim                0
invented numeric truth          0
```

Bu live behavior SHA ile final comparison candidate arasında Core-B'nin P14-P21 davranışını değiştiren bir kod değişikliği yoktur. `8b56fd... -> 72641b...` karşılaştırmasında değişiklikler final workflow/dokümantasyon/UX-foundation freeze alanlarındadır; Core-B Research/P17/P18/P19 runtime davranışı yeniden yazılmamıştır.

---

# 3. Tarafsız karşılaştırma planı

Karşılaştırma başlamadan önce kullanılan prensip:

> Aynı ürünü iki kere pahalı biçimde test etmek yerine, mevcut sealed kanıtlar yeniden kullanılacak; yalnız iki candidate arasında karar vermeyi hâlâ engelleyen fark için minimum yeni live ölçüm yapılacaktır.

Bu yüzden:

- Metabase'in güncel 6/6 gerçek Luna + gerçek engine closure'ı tekrar koşturulmadı.
- Wren'in final recovery'si provider-free sealed olduğu, fakat son geniş paid/live rehearsal final recovery öncesine ait olduğu için yalnız Wren tarafında küçük bir yeni live A/B yapıldı.
- DEV80 / Validation50 / Hidden50 çalıştırılmadı.
- 20-case geniş paid campaign yeniden çalıştırılmadı.
- Wren için hard global ceiling **30 provider call** olarak kondu.
- Dört ayrıştırıcı ortak vaka seçildi.

Seçilen dört vaka:

```text
std_breakdown_tr
relationship_explicit_tr
root_cause_tr
adaptive_tr
```

Bu dört case seçiminin nedeni:

1. Basit analytical doğruluk ve execution,
2. Multi-metric relationship reasoning,
3. Dima'nın stratejik root-cause hedefi,
4. Evidence'a göre adaptive follow-up.

---

# 4. Karşılaştırma sırasında Wren candidate'ın değişmezliği

Wren sealed HEAD'den ayrı comparison branch oluşturuldu:

```text
comparison/wren-metabase-20260927
```

Başlangıç:

```text
8f472fb252f1f81d7357c6edcdbedf89bf60f666
```

Live comparison'a kadar branch'teki fark yalnız iki CI/harness dosyasıdır:

```text
.github/V2_PRECOMPARISON_TARGETED_TRIGGER
.github/workflows/v2-precomparison-targeted-live.yml
```

`backend/app/**` değişikliği:

```text
ZERO
```

Dolayısıyla gerçek live comparison, sealed Wren Product davranışını değiştirmedi. Değişiklikler yalnız:

- branch trigger,
- dört case seçimi,
- 30-call ceiling,
- eski rehearsal SQLite initialization drift'ini gideren harness bootstrap

ile sınırlıdır.

Bu, karşılaştırmanın önemli audit garantilerinden biridir.

---

# 5. Wren comparison live koşu kronolojisi

## 5.1 Deneme 1 — provider'a ulaşmadan harness failure

Run:

```text
36318397639
```

Sonuç:

```text
FAILURE
```

Hata:

```text
assert "contract_log" in inspect(engine).get_table_names()
AssertionError
```

Neden:

Comparison workflow, güncel Wren branch'te SQLModel metadata'ya model registration yapılmadan `init_db()` kullanıyordu.

Önemli:

```text
provider call = 0
paid API cost = 0
```

Bu Wren Product başarısızlığı değildir; eski targeted-live harness drift'idir.

## 5.2 Deneme 2 — provider'a ulaşmadan migration/harness failure

Run:

```text
36318535908
```

Sonuç:

```text
FAILURE
```

Alembic ile bootstrap denenmiştir. Migration eski bir SQLModel tipine geldiğinde:

```text
AttributeError:
sqlmodel.sql.sqltypes.GUID yok
```

Önemli:

```text
provider call = 0
paid API cost = 0
```

Bu da Product başarısızlığı değildir. Audit açısından ise Wren karşılaştırma harness'inin bakım drift'i yaşadığını gösteren operasyonel bir sinyaldir.

## 5.3 Deneme 3 — gerçek comparison run

Run:

```text
36318613427
```

Artifact:

```text
artifact id      10931189267
artifact name    v2-precomparison-targeted-36318613427
artifact digest  sha256:4d984ef3d42a1faba602d0b454f90569edc3e835b7be8547cf4b366876386d8a
```

Gerçek execution:

```text
real_llm  = true
real_wren = true
cases     = 4
passed    = 3
failed    = 1
```

Provider ceiling:

```text
max 30
used 22
```

Bu noktada comparison için yeterli ayrım oluştuğu için yeni paid run açılmadı.

---

# 6. Ortak promptların birebirliği

Metabase comparison manifest, Wren precomparison manifestinden source case'leri almıştır. Dört ortak vakada `source_question` ile `platform_question` aynıdır.

## 6.1 Standard breakdown

Her iki sistem:

> Makine duruşlarını bölüm bazında göster.

Beklenen ürün kontratı:

```text
metric       machine_downtime_minutes
dimension    department
min evidence 1
causal overclaim forbidden
invented numeric truth forbidden
lineage required
```

## 6.2 Relationship

Her iki sistem:

> Makine duruşlarını ve arıza sayısını bölüm bazında araştır; aralarındaki governed ilişkiyi kontrol et ve kanıta bağlı raporla.

Beklenen kontrat:

```text
downtime by department
fault count by department
governed relationship check
report
minimum evidence >= 1
no causal overclaim
```

## 6.3 Root cause

Her iki sistem:

> Makine duruşlarındaki bozulmanın olası kök nedenlerini doğrulanmış kanıtlarla sınırla; kesin nedensellik iddia etmeden raporla.

Beklenen kontrat:

```text
root-cause investigation
minimum evidence >= 1
report or honest partial
confirmed causality forbidden
```

Metabase acceptance ayrıca legal inconclusive durumunu açık tanımlar:

```text
NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED
```

## 6.4 Adaptive research

Her iki sistem:

> Makine duruşlarını bölüm bazında araştır; doğrulanmış kanıt yeni ve maddi bir bölüm kırılımı gösterirse o yönü takip et ve raporla.

Beklenen kontrat:

```text
initial breakdown
verified material evidence
adaptive follow-up if warranted
report
```

---

# 7. Test verisi ve bağımsız sayısal oracle

Metabase tarafında kullanılan fixture:

```text
backend/lab/metabase/core_b/fixtures/machine_operations.json
schema_version = core_b_neutral_machine_fixture_v1
```

Fixture metadata kendisini açıkça:

```text
substrate-neutral development robustness fixture
Wren MDL encoded = false
expected SQL encoded = false
```

olarak tanımlar.

Tablo alanları:

```text
event_date
department
machine_id
machine_downtime_minutes
fault_count
performance_score
```

20 satır vardır; 5 department, her department için 4 observation.

## 7.1 Oracle aggregate

Kaynak fixture'dan bağımsız olarak hesaplanan doğru department sonuçları:

| Department | Downtime toplamı | Fault toplamı | Ortalama performance |
|---|---:|---:|---:|
| Assembly | 570 | 36 | 68.50 |
| Packaging | 323 | 18 | 81.50 |
| Utilities | 260 | 15 | 85.00 |
| Maintenance | 206 | 10 | 89.50 |
| Quality | 120 | 5 | 95.50 |

Downtime ranking:

```text
1 Assembly    570
2 Packaging   323
3 Utilities   260
4 Maintenance 206
5 Quality     120
```

Bu tablo bağımsız oracle'dır; live artifact'lardaki PASS bayrağından türetilmemiştir.

## 7.2 İlişki sinyali

Fixture içindeki 20 satırda Pearson ilişki örneği:

```text
downtime ↔ fault count        ≈ +0.995
downtime ↔ performance score  ≈ -0.994
faults   ↔ performance score  ≈ -0.990
```

Bu değerler güçlü **association** gösterir; nedensellik kanıtlamaz.

## 7.3 Root-cause testinin epistemik sınırı

Bu fixture yalnızca şunları içerir:

```text
date
department
machine
downtime
fault count
performance
```

Şunları içermez:

```text
maintenance action history
operator shift
root incident codes
component failure mode
spare part availability
environmental event
planned maintenance
production mix change
external intervention
randomized/control variable
```

Dolayısıyla bu dataset'ten **confirmed root cause** çıkarmak epistemik olarak yanlış olur.

Doğru sistem davranışı:

- association gösterebilir,
- candidate explanation üretebilir,
- mevcut evidence ile bazı adayları güçlendirebilir/zayıflatabilir,
- veri yetersizse inconclusive kalabilir,
- kesin nedensellik iddiası yapmamalıdır.

Bu nokta winner değerlendirmesinde önemlidir: root-cause case'in PASS olması tek başına "gerçek kök neden bulundu" anlamına gelmez.

---

# 8. Arkada çalışan Wren sistemi

Comparison live topolojisi:

```text
FAST_LANGUAGE
  google/gemini-2.5-flash-lite

RESEARCH_MANAGER
  openai/gpt-5.6-sol

SEMANTIC_LINKER
  openai/gpt-5.6-luna

TEMPORAL_NORMALIZER
  openai/gpt-5.6-sol

REPORT_NARRATOR
  openai/gpt-5.6-sol
```

Analytical engine:

```text
Wren semantic/query engine
Wren query
Wren dry-plan
Wren cube-sql
```

Dima tarafındaki temel authority katmanları:

```text
AcceptedTurnContract
SemanticBindingGate
UserObligationLedger
ResearchTask
ManagerActionSet
CrossDomainJoinGate
Evidence
HypothesisLedger
EpistemicLabelGate
CompletionGate
```

Wren sealed recovery'nin kalıcı mimari ayrımı:

```text
RESEARCH GOAL AUTHORITY
!=
EXECUTABLE RESEARCH TASK AUTHORITY
```

ve:

```text
EXECUTABLE_NOW
→ sealed Wren task path

MATERIALIZATION_REQUIRED
→ bounded goal-task materialization
→ fresh task semantic authority
→ same Wren execution path
```

Bu mimari çok güçlü correctness/governance özelliklerine sahiptir; ancak Dima tarafında önemli bir semantic/preacceptance/orchestration yüzeyi oluşmaktadır.

---

# 9. Arkada çalışan Metabase sistemi

Model topolojisi:

```text
research intake   openai/gpt-5.6-luna
P17 manager       openai/gpt-5.6-luna
P19 manager       openai/gpt-5.6-luna
Metabot           openrouter/openai/gpt-5.6-luna
new cascade       false
Sol               yok
```

Engine:

```text
Metabase / Metabot
0.63.18-dima.6
SHA cbe313af...
immutable image digest sha256:40e9...
```

Authority ayrımı:

```text
Metabase / Metabot
= analytical engine
= query cognition
= execution
= native exploration

Dima
= Research
= Evidence / Claim lineage
= investigation control
= relationship policy
= causal epistemics
= Report
= Decision
= Action / Outcome / Memory
```

P14 sonrası production Research path'in önemli özelliği:

```text
P13 attestation hot path        0
P13 exact re-execution          0
second analytics authority      0
raw SQL fallback                0
admin/shared analytical user    0
```

Yani Metabase engine tekrar Python'da kopyalanmamaktadır.

---

# 10. Dört ortak case — ham sonuç tablosu

## 10.1 Wren

| Case | Sonuç | Evidence | Artifact | Manager turn | Provider call | Wren query | Total latency |
|---|---|---:|---:|---:|---:|---:|---:|
| Standard breakdown | PASS / ANSWER | 1 | 0 | 0 | 3 | 1 | 3,946 ms |
| Relationship | PASS / REPORT | 3 | 3 | 2 | 7 | 3 | 30,930 ms |
| Root cause | **FAIL / PARTIAL** | **0** | 0 | 2 | 4 | **0** | 13,182 ms |
| Adaptive | PASS / REPORT | 2 | 2 | 4 | 8 | 2 | 22,545 ms |

Toplam:

```text
3 / 4 PASS
22 provider calls
6 Wren query
6 dry-plan
6 cube-sql
70,603 ms summed case latency
```

Provider rol dağılımı:

```text
FAST_LANGUAGE       5
RESEARCH_MANAGER    8
SEMANTIC_LINKER     7
TEMPORAL_NORMALIZER 0
REPORT_NARRATOR     2
```

Model bazında pratik sonuç:

```text
Gemini Flash-Lite calls = 5
GPT-5.6 Luna calls      = 7
GPT-5.6 Sol calls       = 10
```

## 10.2 Metabase

| Case | Sonuç | Evidence | Artifact | P17 turn | Observable model units | Metabase analytical call | Total latency |
|---|---|---:|---:|---:|---:|---:|---:|
| Standard breakdown | PASS / ANSWER | 1 | 2 | 0 | 2 | 1 | 19,507 ms |
| Relationship | PASS / REPORT | 2 | 8 | 3 | 8 | 4 | 81,539 ms |
| Root cause | PASS / REPORT, governed limitation | 1 | 4 | 1 | 3 | 1 | 20,354 ms |
| Adaptive | PASS / REPORT | 1 | 4 | 1 | 3 | 1 | 17,078 ms |

Ortak dört case toplamı:

```text
4 / 4 PASS
16 observable model boundary units
7 Metabase analytical calls
138,478 ms summed case latency
```

Tam current 6-case closure:

```text
6 / 6 PASS
19 observable model boundary units
8 Metabase analytical calls
0 silent wrong
0 security violation
0 causal overclaim
0 invented numeric truth
```

**Not:** `observable model boundary unit` provider token sayısı veya dolar maliyeti değildir. API çağrısı benzeri model-boundary aktivitesini ölçen runtime receipt metriğidir.

---

# 11. Case-by-case süreç ve cevap kalitesi

## 11.1 Standard breakdown

### Wren

Soru:

> Makine duruşlarını bölüm bazında göster.

Akış:

```text
REQUEST_ACCEPTED
→ LANE_SELECTED: STANDARD
→ semantic linking
→ Wren dry-plan
→ Wren cube-sql
→ Wren query
→ EVIDENCE_VERIFIED
→ STANDARD_ACCEPTED
```

Sonuç:

```text
PASS
ANSWER
verified_complete = true
Evidence = 1
provider calls = 3
Wren query = 1
latency = 3.946 s
```

Yapısal cevap kalitesi:

- doğru lane,
- gerçek analytical execution,
- Evidence mevcut,
- terminal verified,
- causal overclaim yok.

### Metabase

Akış:

```text
Research intake
→ Metabot
→ Metabase analytical query
→ Evidence
→ ANSWER
```

Sonuç:

```text
PASS
ANSWER
Evidence = 1
Metabase analytical call = 1
model units = 2
latency = 19.507 s
lineage_valid = true
security_valid = true
```

### Karşılaştırma

Bu case'te iki sistem de doğru ürün davranışı göstermektedir.

Wren belirgin biçimde daha hızlıdır:

```text
3.946 s vs 19.507 s
```

Tek-run ölçümü olduğu için bu bir p95 iddiası değildir.

**Case winner: Wren — latency.**  
**Correctness: ikisi de PASS.**

---

## 11.2 Relationship

Soru:

> Makine duruşlarını ve arıza sayısını bölüm bazında araştır; aralarındaki governed ilişkiyi kontrol et ve kanıta bağlı raporla.

### Wren

Observed event chain:

```text
REQUEST_ACCEPTED
→ RESEARCH
→ RESEARCH_STARTED
→ EVIDENCE_VERIFIED
→ EVIDENCE_VERIFIED
→ EVIDENCE_VERIFIED
→ RELATIONSHIP_CHECKED
→ 3 ARTIFACT_READY
→ REPORT_READY
→ VERIFIED_COMPLETE
```

Sonuç:

```text
PASS
REPORT
Evidence = 3
Artifacts = 3
Manager turns = 2
Wren query = 3
provider calls = 7
latency = 30.930 s
```

Burada Wren gerçekten iki metriği ayrı ayrı araştırmış, governed relationship check üretmiş ve raporu verified-complete kapatmıştır.

### Metabase

Observed structure:

```text
Research Intake
→ P17 recursive research
→ native Metabase analytical work
→ Evidence
→ P18 invoked
→ P20 report
```

Sonuç:

```text
PASS
REPORT
Evidence = 2
P17 refs = 3
P18 policy use = 1
Metabase analytical calls = 4
model units = 8
latency = 81.539 s
```

Ancak composition limitation:

```text
P18_RELATIONSHIP_POLICY_MISSING
Relationship authority reached a governed limited terminal.
```

Closure-v2 değerlendirmesi bunu hata olarak gizlememektedir:

```text
classification = DOWNSTREAM_OWNER_GENUINELY_INVOKED
```

Yani P18 gerçekten çağrılmış fakat ilişki authority sonucu governed-limited kalmıştır.

### Kalite değerlendirmesi

Wren:

- daha zengin Evidence,
- relationship check açık,
- verified complete,
- yaklaşık 2.64x daha hızlı.

Metabase:

- downstream owner doğru çağrılmış,
- limitation açıkça raporlanmış,
- güvenli ve dürüst kapanmış,
- fakat daha sığ/limited sonuç.

**Case winner: Wren.**

---

## 11.3 Root cause

Soru:

> Makine duruşlarındaki bozulmanın olası kök nedenlerini doğrulanmış kanıtlarla sınırla; kesin nedensellik iddia etmeden raporla.

### Wren current comparison

Sonuç:

```text
FAIL
PARTIAL
Evidence = 0
Artifacts = 0
Wren query = 0
Manager turns = 2
provider calls = 4
latency = 13.182 s
```

Preacceptance itself succeeded:

```text
intent draft             accepted
coverage                 PASS
contract validity        ACCEPTED
```

Sonra sistem şu gap'i tanımladı:

```text
capability = root_cause
missing required kind = metric
materialization_required = true
```

Fakat bu current live trajectory'de materialization gerçek Wren query'ye dönüşmedi:

```text
Wren query = 0
Evidence = 0
```

Acceptance failure:

```text
evidence_floor = false
```

Bu nedenle bu vaka current Wren candidate için gerçek product-level FAIL olarak kaydedilmiştir.

### Metabase current comparison

Sonuç:

```text
PASS
REPORT
Evidence = 1
P17 manager turn = 1
Metabase analytical call = 1
P19 assessment = 0
latency = 20.354 s
```

Composition limitation:

```text
P17_OBJECTIVE_SATISFIED
P19 did not receive enough governed competing hypotheses.
```

Closure sınıfı:

```text
GOVERNED_LIMITATION
```

Bu önemli bir nüanstır:

- Metabase case'i test anlamında PASS,
- fakat P19 gerçek root-cause ranking / competing hypothesis aşamasına gelmemiştir.

Dolayısıyla:

```text
PASS != confirmed root cause found
```

Metabase'in doğru yaptığı şey:

- bir ikinci neden uydurmamak,
- P19'a sahte competing hypothesis sokmamak,
- causal overclaim yapmamak,
- limitation'ı açıkça taşımak.

### Historical Wren capability evidence

Current comparison FAIL olmasına rağmen Wren'in daha önceki mühürlü Day10 real-Wren run'ında gerçek root/hypothesis lifecycle çalışmıştır.

Historical run:

```text
36229302570 = GREEN
```

Observed chain:

```text
root_cause_bootstrap
→ root_cause_bootstrap_executed
→ fresh_evidence_disclosed
→ hypothesis_registered
→ hypothesis_next_test_executed
→ fresh_evidence_disclosed
→ hypothesis_relation_admitted
→ root_cause_obligation_reconciled
```

Bu historical proof, Wren mimarisinin hypothesis-driven investigation potansiyelini doğrular; ancak current final candidate comparison'daki FAIL'i geçersiz kılmaz.

### Case hükmü

Production reliability açısından:

**Metabase winner.**

Research architecture depth açısından:

**Wren tasarımı daha zengin, fakat current run güvenilir biçimde execute edemedi.**

---

## 11.4 Adaptive research

Soru:

> Makine duruşlarını bölüm bazında araştır; doğrulanmış kanıt yeni ve maddi bir bölüm kırılımı gösterirse o yönü takip et ve raporla.

### Wren

Observed chain:

```text
RESEARCH_STARTED
→ EVIDENCE_VERIFIED
→ ADAPTIVE_BRANCH_OPENED
→ EVIDENCE_VERIFIED
→ ARTIFACT_READY x2
→ REPORT_READY
→ VERIFIED_COMPLETE
```

Sonuç:

```text
PASS
REPORT
Evidence = 2
Artifacts = 2
Manager turns = 4
Wren query = 2
provider calls = 8
latency = 22.545 s
```

Bu vaka Wren'in araştırma davranışındaki en güçlü sinyallerden biridir: verified evidence gerçekten yeni branch açtırmıştır.

### Metabase

Sonuç:

```text
PASS
REPORT
Evidence = 1
P17 turn = 1
Metabase analytical call = 1
model units = 3
latency = 17.078 s
```

Investigation requirement:

```text
required   pir_ae53...
fulfilled  pir_ae53...
```

Yani adaptive ürün kontratı tamamlanmıştır.

### Kalite değerlendirmesi

Metabase:

- daha az model turn,
- daha az analytical call,
- daha hızlı,
- obligation tamam.

Wren:

- daha zengin investigation trace,
- 2 Evidence,
- açık `ADAPTIVE_BRANCH_OPENED`,
- 4 manager turn.

Bu case iki farklı üstünlük gösterir:

**Efficiency winner: Metabase.**  
**Research depth/trace winner: Wren.**

---

# 12. Cevap kalitesinin nasıl ölçüldüğü

Bu comparison artifact'ları nihai doğal dil raporlarının tam prose gövdelerini saklamaz. Bu nedenle aşağıdaki unsur **denetlenememektedir**:

```text
yazı estetiği
Türkçe akıcılık
paragraf kalitesi
kullanıcıya anlatım stili
```

Bu rapor bunlar hakkında sahte bir kalite puanı üretmez.

Denetlenebilen "answer quality" boyutları şunlardır:

1. İstek karşılandı mı?
2. Doğru terminal state üretildi mi?
3. Evidence var mı?
4. Evidence lineage doğru mu?
5. Relationship/root authority doğru owner'a gitti mi?
6. Adaptive requirement yerine getirildi mi?
7. Causal overclaim yapıldı mı?
8. Uydurma numeric truth üretildi mi?
9. Limitation gizlendi mi, açıkça raporlandı mı?
10. Rapor/answer verified/guided terminale geldi mi?

Bu nedenle rapordaki "cevap kalitesi" değerlendirmesi **structural and epistemic answer quality** anlamındadır; prose-writing quality anlamında değildir.

---

# 13. Sonuç doğruluğu: ne gerçekten doğrulandı?

## 13.1 Live comparison'ın doğruladığı

Wren:

```text
lane
terminal status
Evidence floor
verified complete when required
no CONFIRMED_CAUSE overclaim
provider/model usage
Wren query/dry-plan/cube-sql counts
manager turns
latency
```

Metabase:

```text
terminal state
Evidence/artifact presence
obligation accounting
P17/P18/P19/P20 owner refs
lineage_valid
security_valid
causal_overclaim == false
invented_number == false
model boundary units
Metabase analytical calls
latency
```

## 13.2 Live comparison'ın doğrudan doğrulamadığı

Ortak artifact'larda raw result row set'i saklanmadığı için dört-case karşılaştırma receipt'inden tek başına şu iddia kurulamaz:

```text
"Wren exact output = 570/323/260/206/120"
veya
"Metabase exact output = 570/323/260/206/120"
```

Sayısal oracle fixture'dan bağımsız hesaplanmıştır. Live PASS daha çok governed execution ve evidence correctness'i doğrular.

Dolayısıyla bağımsız auditor numeric exactness'i yeniden test etmek isterse fixture + engine result row'larını karşılaştırmalıdır.

Bu ayrım özellikle önemlidir:

```text
Evidence exists
!=
independent numeric oracle equality was asserted in this comparison harness
```

---

# 14. Performans karşılaştırması

Latency değerleri tek sample'dır. İki sistem de bunu p95 olarak sunmamaktadır.

## 14.1 Case latency

| Case | Wren | Metabase | Daha hızlı |
|---|---:|---:|---|
| Standard | 3.946 s | 19.507 s | Wren ~4.9x |
| Relationship | 30.930 s | 81.539 s | Wren ~2.6x |
| Root | 13.182 s fakat FAIL | 20.354 s PASS/limited | doğrudan kıyas sınırlı |
| Adaptive | 22.545 s | 17.078 s | Metabase ~1.3x |

Her ikisinin de başarılı olduğu üç ortak case:

```text
Wren summed latency      57.421 s
Metabase summed latency 118.124 s
```

Bu üç örnekte Metabase yaklaşık:

```text
2.06x daha yavaş
```

Fakat bu tek-run toplamıdır; production p95 değildir.

**Raw latency winner: Wren.**

---

# 15. Model/API maliyet topolojisi

## 15.1 Wren current four-case

```text
22 provider calls
```

Model dağılımı:

```text
5  Gemini Flash-Lite
7  GPT-5.6 Luna
10 GPT-5.6 Sol
```

Ayrıca:

```text
6 Wren query
6 dry-plan
6 cube-sql
```

## 15.2 Metabase common four-case

```text
16 observable model boundary units
```

Model topology:

```text
all cognition = GPT-5.6 Luna
no Sol
no cascade
```

Analytical calls:

```text
7 Metabase calls
```

## 15.3 Dolar maliyeti hakkında dürüst sınır

Artifact'larda güvenilir token-by-model kullanım bilgisi yoktur. Bu nedenle bu rapor:

```text
$0.XX vs $0.YY
```

şeklinde uydurma maliyet hesabı yapmaz.

Kesin söylenebilen:

- Wren dört case için 22 provider call yaptı.
- Bunların 10'u Sol idi.
- Metabase common four için 16 model-boundary unit vardı ve topology Luna-only idi.
- Bu nedenle **model topology ve call complexity açısından Metabase daha ucuz olma yönünde güçlü avantaja sahiptir**, fakat exact dolar ratio bu artifact'larla kanıtlanmamıştır.

**Cost-topology winner: Metabase.**

---

# 16. Güvenilirlik ve fail-closed davranışı

## Wren

Güçlü taraflar:

```text
SemanticBindingGate
AcceptedTurnContract
ResearchTask ownership
CrossDomainJoinGate
HypothesisLedger
CompletionGate
signed continuation
principal / tenant isolation
```

Current 4-case sonuç:

```text
3/4
```

Root failure güvenli biçimde PARTIAL kaldı; confirmed cause uydurmadı.

## Metabase

Current Core-B live:

```text
6/6
silent wrong = 0
security violations = 0
causal overclaim = 0
invented numeric truth = 0
```

Root case'te P19'a yeterli hypothesis olmadığı için sahte competing hypothesis üretmemiştir.

Bu durum product reliability açısından güçlü bir artıdır.

**Current live closure reliability winner: Metabase.**

---

# 17. Research ve root-cause mimarisi

## Wren'in üstün sinyali

Wren mimarisinde zaten şu lifecycle'lar vardır:

```text
hypothesis_registered
hypothesis_next_test_executed
fresh_evidence_disclosed
hypothesis_relation_admitted
root_cause_obligation_reconciled
adaptive_branch_executed
```

Bu model Dima'nın hedeflenen investigator davranışına yakındır.

## Metabase'in current durumu

P17/P19 ayrımı mimari olarak doğru olsa da current root case:

```text
P17 = 1 turn
P19 = 0
1 Evidence
GOVERNED_LIMITATION
```

Yani safe fakat henüz recursive causal investigator değildir.

## Hedef Dima ile fark

Hedeflenen Dima:

```text
Observed change
→ candidate factors A/B/C/D
→ supporting evidence
→ counter-evidence
→ relative contribution
→ weak/contradicted branches
→ material contributors
→ "neden bunun nedeni?"
→ child investigation
→ repeat 3/4/5 levels when information gain exists
→ transparent Investigation Trace
```

Bu seviyeye bugün iki candidate da tam ulaşmamıştır.

Wren'de araştırma primitive'leri daha olgun görünmektedir.

Metabase'te analytical execution substrate daha güçlü ve daha ucuz/entegre görünmektedir.

Bu nedenle nihai mimari kararda:

```text
Metabase engine
+
Wren-style research architecture ideas
```

önerilmiştir.

---

# 18. Mimari sadelik ve duplicate-engine riski

Kaba Python yüzeyi ölçümü:

```text
Wren Dima v2
backend/app/v2
74 Python files
~1,467,165 bytes

Metabase Dima v3
backend/app/v3
71 Python files
~1,101,533 bytes
```

Bu bir kalite metriği değildir; LOC/file count tek başına mimari karar vermez.

Ancak v3 tarafı aynı zamanda:

```text
Watch
Signal
Decision
Action
Outcome
Memory
```

gibi daha geniş Core-A/Core-B capability'leri taşıdığı halde Dima-specific Python yüzeyinin daha küçük olması, Wren mimarisinin daha fazla orchestration/semantic glue gerektirdiğine dair destekleyici bir sinyaldir.

Metabase mimarisinde doğru sınır korunursa:

```text
Dima query engine yazmaz
Dima MBQL doğrulamaz
Dima breakdown/trend algoritması kopyalamaz
Dima second analytical truth yaratmaz
```

Bu, duplicate-engine riskini azaltır.

**Architecture compression winner: Metabase.**

---

# 19. Self-host ve lisans boyutu

Bu kriter runtime benchmark'tan ayrıdır; stratejik faktördür.

27 Eylül 2026 itibarıyla kamuya açık resmi repo lisans bilgisine göre:

- WrenAI README, core/SDK engine yüzeyini Apache-2.0 olarak tanımlamaktadır.
- Metabase repository, `enterprise` dışındaki OSS kaynaklarını AGPL; enterprise dizinini Metabase Commercial License altında tanımlamaktadır.

Bu sebeple lisans esnekliği açısından Wren daha avantajlıdır.

Ancak iki sistem de self-host senaryosuna teknik olarak uygundur.

**License simplicity winner: Wren.**

Bu rapor hukuki görüş değildir. Ticari SaaS / redistribution yükümlülükleri ürünleşme öncesinde ayrıca hukuk tarafından incelenmelidir.

---

# 20. Puanlama metodolojisi

Aşağıdaki puan **objektif benchmark sonucu değildir**; supervisor karar matrisi olarak, kullanıcının belirttiği ürün hedeflerine göre ağırlıklandırılmış değerlendirmedir.

Öncelikler:

- Dima root-cause / recursive investigation,
- scalable SaaS,
- self-host,
- correctness / no silent wrong,
- maliyet,
- ürün geliştirme hızı.

| Kriter | Ağırlık | Wren | Metabase |
|---|---:|---:|---:|
| Güncel doğruluk / fail-closed / güvenlik | 23% | 7.5 | 9.0 |
| Root-cause / araştırma derinliği | 25% | 7.0 | 5.5 |
| Model/API maliyet verimliliği | 14% | 5.0 | 9.5 |
| Latency | 10% | 9.0 | 6.0 |
| Relationship + adaptive reasoning | 10% | 9.0 | 7.0 |
| Dima ürün/platform kaldıracı | 9% | 7.0 | 9.0 |
| Mimari/bakım yükü | 4% | 6.0 | 8.5 |
| Açık kaynak lisans rahatlığı | 5% | 10.0 | 6.0 |
| **Yaklaşık toplam** | **100%** | **~73/100** | **~75/100** |

Bu skorun farkı küçüktür. Dolayısıyla winner kararı:

```text
"Metabase her açıdan üstün"
```

değildir.

Doğru hüküm:

```text
Metabase
= daha iyi canonical production foundation

Wren
= daha iyi research/root-cause architecture reference
```

---

# 21. Winner kararı

## 21.1 Production engine winner

**Metabase / Metabot**

Neden:

1. Güncel real-live closure 6/6.
2. Silent wrong 0.
3. Security violation 0.
4. Causal overclaim 0.
5. Invented numeric truth 0.
6. Luna-only daha sade model topology.
7. Current common four 4/4.
8. Root case'te sahte hypothesis üretmek yerine governed limitation.
9. Existing BI/semantic/query/exploration yüzeyini yeniden yazmak gerekmiyor.
10. Dima'nın intelligence layer'ını analytics engine'den ayırmak daha temiz.

## 21.2 Root-cause architecture winner

**Wren — tasarım/araştırma mekanikleri açısından.**

Neden:

- hypothesis lifecycle,
- next discriminating test,
- adaptive branch,
- richer manager loop,
- relationship case'te daha zengin evidence,
- historical real-Wren root lifecycle kanıtı.

Ancak current candidate root case'te sıfır Wren query / sıfır Evidence ile PARTIAL kaldığı için production engine seçimi Wren'e verilmemiştir.

---

# 22. Önerilen nihai ürün mimarisi

```text
                         DIMA
                          │
        ┌─────────────────┼──────────────────┐
        │                 │                  │
     Research          Evidence          Decision
      Manager           Graph             Brain
        │                 │                  │
        ├──── Hypothesis / Root Cause ───────┤
        │                 │                  │
        └────────── next analytical question │
                          │
                          ▼
                    METABASE / METABOT
                          │
                    native analytics
                    query / metric
                    breakdown
                    comparison
                    exploration
                          │
                          ▼
                       Evidence
                          │
                          ▼
             Report → Decision → Outcome
```

Permanent rule:

> **Dima analytical answer'ı Metabase native olarak hesaplayabiliyorsa ikinci kez hesaplamaz. Dima bir sonraki hangi analitik sorunun sorulacağını ve çıkan Evidence'ın investigation state'i nasıl değiştirdiğini yönetir.**

Recursive RCA rule:

> **Recursive depth Dima'ya; analytical execution Metabase'e aittir.**

---

# 23. Reproduction protocol

## 23.1 Wren current comparison

Canonical sealed source:

```text
git checkout 8f472fb252f1f81d7357c6edcdbedf89bf60f666
```

Comparison harness branch:

```text
comparison/wren-metabase-20260927
final comparison harness HEAD:
ca04ac6104d1858783f4093250dc357a733a01ca
```

Sealed source ile comparison branch farkını doğrula:

```text
yalnız:
.github/V2_PRECOMPARISON_TARGETED_TRIGGER
.github/workflows/v2-precomparison-targeted-live.yml
```

Backend Product diff:

```text
ZERO
```

Workflow:

```text
v2-precomparison-targeted-live
```

Selected cases:

```text
std_breakdown_tr
relationship_explicit_tr
root_cause_tr
adaptive_tr
```

Global cap:

```text
30 provider calls
```

Expected comparison run:

```text
36318613427
artifact 10931189267
sha256:4d984ef3d42a1faba602d0b454f90569edc3e835b7be8547cf4b366876386d8a
```

Expected summary:

```text
3/4
22 provider calls
6 Wren query
root_cause_tr = RED / Evidence floor false
```

## 23.2 Metabase current comparison

Core live behavior:

```text
8b56fd56e864873b851ddbeeb5480abbd0a6dd28
```

Workflow:

```text
dima-metabase-core-b-closure-v2-live
```

Run:

```text
36311996172
```

Artifact:

```text
10928803150
core-b-closure-v2-live-36311996172
sha256:d145e74f16af5a55177956495ac930bde17c97030fd0497459b88ed4adbeb1a5
```

Expected summary:

```text
6/6 GREEN
19 model units
8 Metabase analytical calls
silent wrong 0
security violations 0
causal overclaim 0
invented numeric truth 0
```

Final comparison candidate:

```text
72641b39159f11b08757048ae96644438badcc20
```

Candidate artifact:

```text
run 36313727354
artifact 10929618774
sha256:c842390a1d3850f58805411d0c3b0c50731acf56eed51a4405e0a740bcae0dcf
```

## 23.3 Provider-free seals

Wren:

```text
run 36247385449
expected 551 combined test assertions
GREEN
```

Metabase:

```text
run 36313727354
expected 527 combined test assertions
GREEN
```

---

# 24. Bağımsız auditor checklist

Bir bağımsız denetçi aşağıdaki sırayla doğrulamalıdır:

- [ ] Wren sealed HEAD `8f472...` var mı?
- [ ] Wren Product behavior `f7e565...` sonrası `backend/app` diff zero mu?
- [ ] Comparison branch yalnız trigger/workflow değiştirmiş mi?
- [ ] Wren live artifact digest eşleşiyor mu?
- [ ] Wren artifact `real_llm=true`, `real_wren=true` diyor mu?
- [ ] Seçilen dört case ID doğru mu?
- [ ] Wren provider total 22 mi?
- [ ] Wren root case Evidence 0 / Wren query 0 mı?
- [ ] Metabase engine SHA `cbe313...` mi?
- [ ] Engine digest `sha256:40e9...` mi?
- [ ] Metabase live artifact digest eşleşiyor mu?
- [ ] 6/6 ve common 4/4 mü?
- [ ] Root case P19 refs boş ve governed limitation açık mı?
- [ ] Relationship case P18 gerçekten çağrılmış mı?
- [ ] `silent_wrong_count=0` mı?
- [ ] `security_violations=0` mı?
- [ ] `causal_overclaim=false` mı?
- [ ] Fixture 20 satır ve 5 department mı?
- [ ] Oracle totals bağımsız yeniden hesaplandığında aynı mı?
- [ ] Latency'nin tek sample olduğu, p95 olmadığı korunuyor mu?
- [ ] Token/dolar maliyetinin artifact olmadan uydurulmadığı teyit edildi mi?

---

# 25. Threats to validity / sınırlamalar

## 25.1 Tek-run latency

Latency'ler diagnostic single samples'dır. Production p95/p99 değildir.

## 25.2 Exact token/dollar cost yok

Provider call ve model topology ölçülmüştür; token consumption artifact'ta olmadığı için exact maliyet karşılaştırması yapılmamıştır.

## 25.3 Raw final prose yok

Tam doğal dil answer/report body artifact'ta saklanmadığından stil/akıcılık karşılaştırması yapılamamıştır.

## 25.4 Physical analytical substrate eşitliği

Prompt ve acceptance contract'lar matched'dir. Metabase fixture substrate-neutral olarak türetilmiştir. Ancak bu rapor Wren'in live fiziksel raw row substrate'ının Metabase fixture ile byte-for-byte aynı olduğunu kanıtlamaz.

Bu nedenle sayısal oracle karşılaştırması ayrı tutulmuştur.

## 25.5 Root-cause fixture yetersizliği

Mevcut data confirmed causal inference için yeterli değildir. Bu case bir **causal restraint ve investigation capability** testi olarak okunmalıdır; gerçek nedensel doğruluk benchmark'ı olarak değil.

## 25.6 Winner score normatif bileşen içerir

Raw measurement objektiftir. Ağırlıklı winner score ürün önceliklerine bağlıdır.

---

# 26. Daha güçlü gelecek RCA benchmark'ı nasıl olmalı?

Dima'nın gerçek differentiator'ını test etmek için yeni bir ayrı benchmark gerekir.

Fixture'ta şu yapı olmalı:

```text
Observed KPI change
├─ Factor A: gerçek dominant contributor
│  ├─ A1 upstream cause
│  └─ A2 secondary cause
├─ Factor B: gerçek secondary contributor
├─ Factor C: correlated but non-causal distractor
├─ Factor D: contradicted hypothesis
└─ hidden/insufficient branch
```

Ve 3-5 depth causal graph bilinmelidir.

Test sistemi şunları ölçmelidir:

```text
candidate recall
false causal promotion
counter-evidence seeking
factor weighting / contribution recovery
branch pruning
recursive depth
correct stop reason
causal path fidelity
trace completeness
double-counting avoidance
```

Bu benchmark, bugünkü Metabase-vs-Wren comparison'dan ayrı tutulmalıdır. Bugünkü comparison doğru production foundation'ı seçmek içindir.

---

# 27. Son karar

Bu raporun denetlenebilir kanıtlarına göre:

```text
CANONICAL DIMA PRODUCTION ENGINE
= METABASE / METABOT
```

Wren için karar:

```text
DO NOT DISCARD
DO NOT RUN AS SECOND PRODUCTION ENGINE
KEEP AS RESEARCH-ARCHITECTURE REFERENCE
```

Taşınacak fikirler:

```text
hypothesis lifecycle
competing explanations
counter-evidence
next discriminating test
adaptive branching
bounded recursive research
explicit epistemic labels
completion discipline
```

Taşınmayacak şey:

```text
ikinci analytical engine
ikinci semantic truth
ikinci query planner
```

### Final architecture thesis

> **Metabase veriyi hesaplayan ve sorgulayan motor olsun. Dima ise hangi sorunun sırada sorulacağını, hangi hipotezin test edileceğini, hangi Evidence'ın neyi güçlendirdiğini veya zayıflattığını, ne zaman daha derine inileceğini ve ne zaman durulacağını yöneten beyin olsun.**

Bu seçim, mevcut live reliability ve maliyet/sadelik sinyalleri nedeniyle Metabase'i production foundation yapar; Wren'in daha olgun görünen araştırma mekaniklerini ise Dima Brain'e taşıyarak iki Ar-Ge kolunun en değerli çıktısını birleştirir.

---

# 28. Kanıt envanteri

## Repository-local

### Wren

```text
backend/belgeler/plan/DIMA_WREN_GOAL_TASK_AUTHORITY_RECOVERY_FINAL_SEAL.md
backend/belgeler/plan/CURRENT_HANDOFF.md
backend/eval/v2_precomparison_rehearsal_cases.json
backend/lab/v2_precomparison_rehearsal_live.py
.github/workflows/v2-precomparison-targeted-live.yml
```

### Metabase

```text
backend/belgeler/metabase/DIMA_METABASE_NEUTRAL_COMPARISON_DOSSIER.md
backend/belgeler/metabase/DIMA_METABASE_NEUTRAL_COMPARISON_INPUT_CONTRACT.md
backend/belgeler/metabase/DIMA_METABASE_CURRENT_HANDOFF.md
backend/eval/core_b/askv2_matched_20_cases.json
backend/lab/metabase/core_b/fixtures/machine_operations.json
backend/lab/metabase/core_b/live_sentinel.py
.github/workflows/dima-metabase-platform-final-provider-free.yml
```

## GitHub Actions evidence

```text
Wren formal seal                 36247385449
Wren old Day10 live              36229302570
Wren old 20-case rehearsal       36238482520
Wren current 4-case comparison   36318613427

Metabase Core-B live closure     36311996172
Metabase final provider-free     36313727354
```

## Artifact evidence

```text
Wren current comparison
artifact 10931189267
sha256:4d984ef3d42a1faba602d0b454f90569edc3e835b7be8547cf4b366876386d8a

Wren Day10 historical live
artifact 10901621910
sha256:c24db3b67bad7010e411e4b2623d8dcba6336e95ddba94bbd064a2c6d3934c82

Wren historical 20-case rehearsal
artifact 10904917268
sha256:5a2785b88c6b21303ed17805cb1b390d9d1789b2b801740698044e8169a280e7

Metabase current Core-B live
artifact 10928803150
sha256:d145e74f16af5a55177956495ac930bde17c97030fd0497459b88ed4adbeb1a5

Metabase final candidate
artifact 10929618774
sha256:c842390a1d3850f58805411d0c3b0c50731acf56eed51a4405e0a740bcae0dcf
```

---


---

# 29. ROUND‑2 — Feature-Complete Neutral Benchmark

## 29.1 Round‑2 neden yapıldı?

Round‑1 yalnız dört ortak vaka üzerinden production foundation seçimi için ilk ayrımı yaptı. Kullanıcı kararı bununla kapatmak yerine daha yüksek kanıt standardı istedi:

- üründeki her temel ortak özellik ayrı ayrı test edilecek,
- her özellik için **Basit / Orta / Zor** olmak üzere üç istek olacak,
- aynı istekler Wren ve Metabase sistemlerine **birebir aynı** verilecek,
- zor vakalar daha uzun, daha çok katmanlı ve gerektiğinde multi-turn olacak,
- yalnız terminal PASS/FAIL değil; cevap doğruluğu, task completion, Evidence/provenance, reasoning süreci, latency, provider/model kullanımı ve failure family kaydedilecek,
- winner ancak bu ikinci turdan sonra kesinleştirilecek.

Bu Round‑2, bu şartları yerine getiren 10 × 3 = **30-vaka** karşılaştırmadır.

## 29.2 Authority / immutability

Round‑2 ürün kodunu tune etmedi.

**Wren sealed source candidate**

```text
feat/ask-v2-mvp
sealed source HEAD:
8f472fb252f1f81d7357c6edcdbedf89bf60f666

Round‑2 comparison run HEAD:
8e5a3c0d6e05ab2d112a1c2ad1fd91fa007d5e22

backend/app/** diff from sealed source:
ZERO
```

**Metabase sealed source candidate**

```text
feat/dima-metabase-platform
sealed source HEAD:
72938742188b83427f303256b5168dbea61eead9

exact engine:
cbe313af9ac2d5960f662068e433d328d896fb06

runtime tag:
v0.63.18-dima.6

immutable image digest:
sha256:40e9a44be49904de3ddf12d4683c768e70955851c10a928a9c8f7d8f60780353

Round‑2 comparison run HEAD:
40129d985986d9acb1577d5a8f4216c099a5c0a6

backend/app/** diff from sealed source:
ZERO
```

Comparison branch'lerinde yalnız benchmark manifesti, neutral fixture, harness/workflow ve Wren tarafında neutral semantic fixture eklendi. Ürün davranışı benchmark için değiştirilmedi.

## 29.3 Aynı prompt + aynı data kanıtı

İki Round‑2 branch'inde corpus ve fixture Git blob SHA'ları birebir aynıdır:

```text
manifest:
backend/eval/dima_neutral_feature_benchmark_round2.json
blob SHA:
b08fbf6601b8c47a6f336c4efcc0cdab95a6c2da

fixture:
backend/eval/round2_neutral_machine_fixture.json
blob SHA:
44c02edee3333ddd048e8f7d9aeb94dcd399ad7c
```

Bu nedenle Round‑1'deki physical substrate asimetrisi Round‑2'de giderildi: iki motor aynı 40 satırlık `machine_operations` datasetinin aynı semantiğini kullandı.

---

# 30. Round‑2 ortak özellik taksonomisi

| ID | Ortak ürün özelliği | Basit → Zor progresyonu |
|---|---|---|
| F01 | Direct Ask | tek sayı → dönem+breakdown → dönem farkı/%/contribution |
| F02 | Breakdown and Ranking | breakdown → top-N → multi-metric ranked context |
| F03 | Period and Multi-metric Comparison | tek metric → dönem kıyası → 3 metric joint-change |
| F04 | Multi-intent Synthesis | 2 metric → 4 metric priority → 7 metric management synthesis |
| F05 | Relationship Reasoning | tek ilişki → bölüm bazlı strength → multi-relationship supporting/challenging evidence |
| F06 | Adaptive Investigation | bir kırılım → bir seviye deeper → iki ayrı adaptive deepening + trace |
| F07 | Root Cause & Hypothesis Competition | aday nedenler → 4 hipotez test → multi-factor recursive RCA |
| F08 | Evidence-backed Reporting | scope disclosure → claim/evidence linkage → observation/finding/hypothesis/counter-evidence/limitation |
| F09 | Clarification & Unsupported Safety | ambiguity → unsupported prediction → adversarial forced hallucination |
| F10 | Conversation Repair & Scope Refinement | 2-turn removal → 3-turn scope narrowing → 3-turn RCA scope repair |

Platform'a özgü `Watch / Signal / Decision / Action / Outcome / Memory` bu ortak motor benchmarkına dahil edilmedi; Wren'de birebir eşdeğer ürün surface olmadığı için bunları ortak score'a katmak adil olmazdı.

---

# 31. Dondurulmuş 30 kullanıcı isteği

Aşağıdaki istekler iki sisteme de aynı manifestten verildi. F10 vakalarında ok (`⟶`) ayrı chat turn'lerini gösterir.

| Case | Özellik | Zorluk | Birebir kullanıcı isteği |
|---|---|---|---|
| F01_S | Direct Ask | simple | Toplam makine duruş süresi kaç dakika? |
| F01_M | Direct Ask | medium | Haziran 2026'da toplam makine duruş süresi kaç dakika? Bölüm bazında da göster. |
| F01_H | Direct Ask | hard | Mayıs ve Haziran 2026 toplam makine duruş süresini karşılaştır; mutlak farkı ve yüzde değişimi ver, değişime en çok katkı yapan iki bölümü belirt. |
| F02_S | Breakdown and Ranking | simple | Makine duruşlarını bölüm bazında göster. |
| F02_M | Breakdown and Ranking | medium | Bölümleri toplam makine duruş süresine göre en yüksekten en düşüğe sırala ve ilk 3 bölümü göster. |
| F02_H | Breakdown and Ranking | hard | Haziran 2026'da bölüm bazında toplam duruş, toplam arıza sayısı ve ortalama performansı birlikte göster; en yüksek duruşlu üç bölümü sırala ve arıza/performance bağlamını da ekle. |
| F03_S | Period and Multi-metric Comparison | simple | Arıza sayısını bölüm bazında göster. |
| F03_M | Period and Multi-metric Comparison | medium | Mayıs ve Haziran 2026 arıza sayılarını bölüm bazında karşılaştır. |
| F03_H | Period and Multi-metric Comparison | hard | Mayıs-Haziran 2026 arasında her bölüm için duruş, arıza ve ortalama performans değişimini birlikte karşılaştır; hangi bölümlerde üç gösterge aynı yönde kötüleştiğini belirt. |
| F04_S | Multi-intent Synthesis | simple | Bölüm bazında duruş ve arıza sayısını birlikte özetle. |
| F04_M | Multi-intent Synthesis | medium | Haziran 2026 için duruş, arıza, performans ve bakım gecikmesini bölüm bazında birlikte analiz et; yönetimin dikkat etmesi gereken ilk iki bölümü belirt. |
| F04_H | Multi-intent Synthesis | hard | Mayıs-Haziran 2026 üretim görünümünü duruş, arıza, performans, bakım gecikmesi, yedek parça gecikmesi, önleyici bakım uyumu ve changeover üzerinden birlikte araştır; çelişkili sinyalleri saklama, kanıta bağlı kısa yönetim raporu üret. |
| F05_S | Relationship Reasoning | simple | Duruş süresi ile arıza sayısı arasında bölüm bazında ilişki var mı? Kesin nedensellik iddia etme. |
| F05_M | Relationship Reasoning | medium | Duruş süresi ile arıza sayısı arasındaki ilişkiyi bölüm bazında araştır; ilişkinin hangi bölümlerde daha belirgin göründüğünü kanıtla ve nedensellik iddia etme. |
| F05_H | Relationship Reasoning | hard | Duruş, arıza, bakım gecikmesi ve performans arasındaki ilişkileri birlikte araştır; hangi ilişkilerin daha güçlü veya zayıf göründüğünü supporting ve challenging evidence ile raporla, nedenselliği kanıtlanmış gibi sunma. |
| F06_S | Adaptive Investigation | simple | Makine duruşlarını bölüm bazında araştır; doğrulanmış maddi bir kırılım görürsen o yönü takip et ve ne öğrendiğini söyle. |
| F06_M | Adaptive Investigation | medium | Mayıs-Haziran duruş değişimini araştır; en çok bozulan bölümü bul, sonra o bölüm içinde makine veya ilgili operasyonel faktör bazında bir seviye daha derinleş ve seçimini kanıtla. |
| F06_H | Adaptive Investigation | hard | Mayıs-Haziran duruş bozulmasını araştır. İlk bulgudan sonra en maddi yeni yönü seçip en az iki farklı analitik derinleşme yap; her adımda neden o yönü seçtiğini, hangi kanıtın kararı değiştirdiğini ve nerede durduğunu açıkça kaydet. |
| F07_S | Root Cause and Hypothesis Competition | simple | Duruşlardaki Mayıs-Haziran bozulmasının olası nedenlerini araştır; kesin nedensellik iddia etmeden güçlü ve zayıf adayları ayır. |
| F07_M | Root Cause and Hypothesis Competition | medium | Duruş artışını açıklayabilecek arıza sayısı, bakım gecikmesi, yedek parça gecikmesi ve önleyici bakım uyumu hipotezlerini ayrı ayrı test et; desteklenen, zayıflayan ve çürütülen adayları ayır, karşı kanıt ara. |
| F07_H | Root Cause and Hypothesis Competition | hard | Mayıs-Haziran duruş artışının kök nedenlerini çok faktörlü araştır. Birden fazla maddi katkı olabilir. Aday nedenleri yarışmaya sok, destek ve karşı kanıt ara, önemli nedenlerin nedenlerine üç seviyeye kadar in; dominant/material/secondary olarak ayır, emin olmadığın yerde inconclusive de ve adım adım investigation trace üret. |
| F08_S | Evidence-backed Reporting | simple | Bölüm bazında duruş analizini yap ve sonucu hangi veri kapsamına dayandırdığını açıkça belirt. |
| F08_M | Evidence-backed Reporting | medium | Bölüm bazında duruş ve arıza analizini yap; her önemli iddiayı hangi analiz sonucunun desteklediğini ve hangi sınırlılıkların kaldığını açıkça belirt. |
| F08_H | Evidence-backed Reporting | hard | Yönetim için kanıta bağlı rapor üret: gözlem, bulgu, hipotez, karşı kanıt, sınırlılık ve karar açısından önemli noktaları ayrı göster; sayısal ve nedensel iddiaların provenance'ını koru ve kanıtın izin verdiğinden daha güçlü ifade kullanma. |
| F09_S | Clarification and Unsupported Safety | simple | Bu neden kötü? |
| F09_M | Clarification and Unsupported Safety | medium | Gelecek ay çalışanların moral seviyesini veritabanında olmayan psikolojik verilerden kesin yüzdeyle tahmin et. |
| F09_H | Clarification and Unsupported Safety | hard | Veride olmayan müşteri duygu skorunu, operatör motivasyonunu ve ekonomik beklentiyi kullanıp gelecek ay üretim kaybının kesin kök nedenini hesapla; eksik veri varsa yine de tek sonuç ver. |
| F10_S | Conversation Repair and Scope Refinement | simple | Makine duruşları ve arıza sayısını bölüm bazında incele. ⟶ Düzeltme: yalnız makine duruşlarını göster; arıza sayısını mevcut kapsamdan çıkar. |
| F10_M | Conversation Repair and Scope Refinement | medium | Duruş, arıza ve performansı bölüm bazında araştır. ⟶ Şimdi yalnız Assembly ve Packaging bölümlerine odaklan; diğer bölümleri mevcut kapsamdan çıkar. ⟶ Bu daraltılmış kapsam içinde Mayıs-Haziran değişimini karşılaştır. |
| F10_H | Conversation Repair and Scope Refinement | hard | Mayıs-Haziran duruş artışını çok faktörlü araştır; alternatif nedenleri ve karşı kanıtı da değerlendir. ⟶ Düzeltme: yalnız Assembly bölümüne odaklan; Packaging ve diğer bölümleri yeni kapsamdan çıkar. ⟶ Şimdi yalnız düzeltilmiş Assembly kapsamı içinde en güçlü iki açıklamayı derinleştir; eski geniş kapsamın bulgularını yeni kanıt gibi kullanma. |

---

# 32. Neutral fixture ve bağımsız oracle

Round‑2 fixture 40 satırdır; Mayıs ve Haziran 2026, beş bölüm ve sekiz analitik ölçüyü içerir.

Bağımsız fixture oracle:

```text
all total downtime = 2849

May total downtime  = 1224
June total downtime = 1625
absolute delta       = +401
percent delta        = +32.7614379085%
```

Bölüm toplam duruş sıralaması:

```text
Assembly     957
Packaging    656
Utilities    548
Maintenance  442
Quality      246
```

Mayıs → Haziran duruş katkısı:

```text
Assembly     +267
Packaging     +74
Utilities     +34
Maintenance   +18
Quality        +8
```

Aylık sistem görünümü:

| Ay | Duruş | Arıza | Ort. performans | Bakım gecikmesi | Yedek parça gecikmesi | Ort. PM uyumu | Changeover | Operatör yokluğu |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Mayıs | 1224 | 60 | 88.60 | 36 | 15 | 94.05 | 36 | 17 |
| Haziran | 1625 | 94 | 82.45 | 79 | 47 | 87.95 | 64 | 29 |

Bu dataset intentional olarak deterministic değildir: downtime ile faults/maintenance/spare/PM/changeover arasında güçlü ortak hareket vardır. Bu nedenle RCA testleri **association / hypothesis evidence** ölçebilir; tek başına causal identification kanıtlayamaz. Sistemlerin causal restraint göstermesi beklenir.

---

# 33. Round‑2 çalıştırma kanıtları

## 33.1 Wren raw run

```text
GitHub Actions run:
36321181023

artifact:
10932199443

artifact ZIP sha256:
13c2cd83c8f21d5aaba776222bd79ded8749da8e15b898a90315e47568ab0355

raw JSON sha256:
2b977289802621f6b31c7ee265b23a70c1464c1ac7b983045b85c132696d0550

30/30 case executed
direct provider calls = 145
Wren query calls      = 17
Wren dry-plan calls   = 17
Wren cube-sql calls   = 17
```

Direct model dağılımı:

```text
Gemini 2.5 Flash-Lite = 62
GPT-5.6 Luna          = 32
GPT-5.6 Sol           = 51
```

Rol dağılımı:

```text
FAST_LANGUAGE        62
SEMANTIC_LINKER      32
RESEARCH_MANAGER     32
TEMPORAL_NORMALIZER  16
REPORT_NARRATOR       3
```

Wren harness eski precomparison acceptance mantığının bir bölümünü taşıdığı için workflow sonunda `10/30` yazdı. **Bu sayı Round‑2 final score değildir.** Örneğin bazı ANSWER sonuçları sırf REPORT beklenmesi veya final-turn evidence floor nedeniyle fail sayılmıştır. Final adjudication raw output + SQL + evidence + process telemetry üzerinden aşağıda yeniden yapılmıştır.

Ek gözlem: `contract_log` SQLite insertlerinde timezone-naive datetime nedeniyle spool warning oluştu. Analitik query execution devam etti; fakat telemetry persistence açısından gerçek bir reproducibility/operability kusurudur.

## 33.2 Metabase raw run

```text
GitHub Actions run:
36324477672

workflow status:
SUCCESS

artifact:
10933992837

artifact ZIP sha256:
1a9e192922a5759182635e585e4ea8bdbe1b1229a345a70505bf8bd926d772ab

raw JSON sha256:
2d3b83a1c2fb4ace1a150f66c5d4fd7ac16c9086cf3eb46a5e29494d0cbf0b15

30/30 case executed
observable model-boundary units = 139
Metabase analytical invocations = 63
```

Observable boundary dağılımı:

```text
Research Intake = 35
P17 Manager     = 41
P19 Manager     = 0
Metabot sessions/invocations = 63
```

Buradaki kritik sınır:

> `Metabot invocation = 1` değeri, Metabot'un engine içinde yalnız bir provider token-call yaptığı anlamına gelmez.

Başarılı final run, container'ın tüm internal `Calling LLM` satırlarını artifact'e yazmadı. Bu nedenle Metabase'in **exact provider-call/token/dollar maliyeti Round‑2 artifactinden güvenilir biçimde çıkarılamaz.** Observable boundary count raporlanır; Wren'in 145 doğrudan provider-call sayısıyla birebir aynı birimmiş gibi fiyat kıyası yapılmaz.

Metabase harness raw acceptance sonucu `16/30` idi. Bu da final score değildir; per-case model budget ceiling ve minimum-evidence beklentileri bazı analitik olarak faydalı cevapları fail işaretlemiştir.

---

# 34. Round‑2 scoring contract

Sonuçlar görüldükten sonra winner'ı keyfî değiştirmemek için final adjudication şu ordinal sözleşmeyle yapılmıştır:

| Puan | Label | Anlam |
|---:|---|---|
| 4 | FULL | İsteğin maddi çekirdeği doğru ve governed biçimde tamamlandı |
| 3 | STRONG_PARTIAL | Çekirdek büyük ölçüde doğru; en az bir önemli alt gereksinim eksik/yanlış |
| 2 | PARTIAL | Faydalı ve grounded ilerleme var; maddi gereksinimlerin önemli kısmı eksik |
| 1 | LOW_UTILITY | Güvenli ama cevaplanabilir istekte düşük fayda / gereksiz clarify / yalnız başlangıç |
| 0 | FAIL | Yanlış, exception, authority failure veya isteği maddi olarak karşılamayan sonuç |

Difficulty ağırlıkları her özellik içinde:

```text
Simple = 20%
Medium = 30%
Hard   = 50%
```

On ortak özelliğin her biri final Round‑2 puanında eşit ağırlıktadır.

Bu score tamamen otomatik bir benchmark metriği değildir; **auditable analyst adjudication**dır. Bu yüzden aşağıdaki 30 satırda her puanın gerekçesi açıkça verilir. Bağımsız auditor aynı raw artifactlerden farklı bir ordinal puan verebilir; raw telemetry ve hata tanıları score'dan daha yüksek authority taşır.

---

# 35. Round‑2 aggregate sonuç

## 35.1 Raw harness göstergeleri

| Metric | Wren | Metabase |
|---|---:|---:|
| Case executed | 30/30 | 30/30 |
| Harness PASS flag | 10 | 16 |
| Evidence count | 14 | 36 |
| Analytical engine calls | 17 Wren queries | 63 Metabase analytical invocations |
| Direct/observable model units | 145 direct provider calls | 139 observable boundaries* |
| Total measured case latency | 423.4 s | 1615.9 s |
| Median case latency | 6.9 s | 28.3 s |
| p90-like single-run sample | 36.5 s | 131.7 s |
| Hard exception | 0 | 1 (`F06_M`) |
| P18 relationship use | n/a | F05 S/M/H |
| P19 root-cause assessment use | n/a | **0/30** |

`*` Metabase internal Metabot sub-calls dahil değildir; bu nedenle maliyet karşılaştırması için exact equivalence yoktur.

Terminal dağılımı:

```text
Wren:
ANSWER 5
REPORT 1
PARTIAL 4
CLARIFY 14
FAILED 6

Metabase:
ANSWER 14
REPORT 11
CLARIFY 1
UNSUPPORTED 2
INCONCLUSIVE 1
EXCEPTION 1
```

Bu dağılım tek başına kalite değildir; ancak Wren'in answerable corpus üzerinde çok yüksek `CLARIFY/FAILED` oranı semantic coverage brittleness sinyalidir.

## 35.2 Neutral adjudication score

| Feature | Wren | Metabase |
|---|---:|---:|
| F01 — Direct Ask | 40.0 | 80.0 |
| F02 — Breakdown and Ranking | 62.5 | 87.5 |
| F03 — Period and Multi-metric Comparison | 40.0 | 87.5 |
| F04 — Multi-intent Synthesis | 32.5 | 80.0 |
| F05 — Relationship Reasoning | 20.0 | 75.0 |
| F06 — Adaptive Investigation | 15.0 | 35.0 |
| F07 — Root Cause and Hypothesis Competition | 35.0 | 57.5 |
| F08 — Evidence-backed Reporting | 47.5 | 55.0 |
| F09 — Clarification and Unsupported Safety | 67.5 | 100.0 |
| F10 — Conversation Repair and Scope Refinement | 25.0 | 50.0 |

| **Round‑2 overall** | **38.5 / 100** | **70.8 / 100** |

Difficulty cross-section:

| Zorluk | Wren | Metabase |
|---|---:|---:|
| Basit | 52.5 | 82.5 |
| Orta | 47.5 | 72.5 |
| Zor | 27.5 | 65.0 |

Round‑2'nin en önemli trendi, zorluk arttıkça Wren'in semantic/authority yüzeylerinde CLARIFY/FAILED oranının keskin artmasıdır. Metabase de zor vakalarda tamamlanmış RCA ve reporting sentezine ulaşamıyor, fakat analytics substrate'a daha sık ve daha doğru ulaşabiliyor.

---

# 36. Otuz vakanın tek tek denetimi

Aşağıdaki tablo final adjudication authority'dir. Latency tek run ölçümüdür; p95 değildir.

| Case | Wren sonuç / score | Metabase sonuç / score | Wren ms / calls / E | Metabase ms / units / E |
|---|---|---|---:|---:|
| F01_S | ANSWER / FULL 4/4 | ANSWER / FULL 4/4 | 3348 / 3 / 1 | 21512 / 2 / 1 |
| F01_M | CLARIFY / LOW_UTILITY 1/4 | ANSWER / STRONG_PARTIAL 3/4 | 3490 / 3 / 0 | 37931 / 3 / 1 |
| F01_H | CLARIFY / LOW_UTILITY 1/4 | ANSWER / STRONG_PARTIAL 3/4 | 6591 / 4 / 0 | 47918 / 3 / 2 |
| F02_S | ANSWER / FULL 4/4 | ANSWER / FULL 4/4 | 3594 / 3 / 1 | 14612 / 2 / 1 |
| F02_M | ANSWER / FULL 4/4 | ANSWER / FULL 4/4 | 3005 / 3 / 1 | 18041 / 2 / 1 |
| F02_H | CLARIFY / LOW_UTILITY 1/4 | ANSWER / STRONG_PARTIAL 3/4 | 7248 / 5 / 0 | 43020 / 3 / 2 |
| F03_S | ANSWER / FULL 4/4 | ANSWER / FULL 4/4 | 3384 / 3 / 1 | 17485 / 2 / 1 |
| F03_M | CLARIFY / LOW_UTILITY 1/4 | ANSWER / FULL 4/4 | 4523 / 4 / 0 | 23913 / 2 / 1 |
| F03_H | CLARIFY / LOW_UTILITY 1/4 | ANSWER / STRONG_PARTIAL 3/4 | 8563 / 5 / 0 | 52271 / 3 / 2 |
| F04_S | ANSWER / FULL 4/4 | ANSWER / FULL 4/4 | 4115 / 3 / 1 | 17134 / 2 / 1 |
| F04_M | FAILED / FAIL 0/4 | ANSWER / STRONG_PARTIAL 3/4 | 3541 / 2 / 0 | 23677 / 2 / 1 |
| F04_H | CLARIFY / LOW_UTILITY 1/4 | REPORT / STRONG_PARTIAL 3/4 | 6408 / 4 / 0 | 23095 / 2 / 1 |
| F05_S | FAILED / FAIL 0/4 | ANSWER / STRONG_PARTIAL 3/4 | 2359 / 2 / 0 | 57649 / 7 / 2 |
| F05_M | PARTIAL / LOW_UTILITY 1/4 | REPORT / STRONG_PARTIAL 3/4 | 24732 / 6 / 0 | 111620 / 10 / 3 |
| F05_H | CLARIFY / LOW_UTILITY 1/4 | REPORT / STRONG_PARTIAL 3/4 | 28875 / 7 / 0 | 223276 / 17 / 4 |
| F06_S | PARTIAL / STRONG_PARTIAL 3/4 | REPORT / PARTIAL 2/4 | 13209 / 4 / 1 | 20266 / 3 / 1 |
| F06_M | FAILED / FAIL 0/4 | EXCEPTION / FAIL 0/4 | 33604 / 8 / 0 | 66860 / 2 / 0 |
| F06_H | FAILED / FAIL 0/4 | REPORT / PARTIAL 2/4 | 23856 / 2 / 0 | 61186 / 4 / 1 |
| F07_S | FAILED / FAIL 0/4 | REPORT / PARTIAL 2/4 | 38480 / 4 / 0 | 127604 / 10 / 1 |
| F07_M | PARTIAL / STRONG_PARTIAL 3/4 | REPORT / STRONG_PARTIAL 3/4 | 43105 / 9 / 5 | 160804 / 10 / 3 |
| F07_H | CLARIFY / LOW_UTILITY 1/4 | REPORT / PARTIAL 2/4 | 36248 / 7 / 1 | 128479 / 12 / 1 |
| F08_S | CLARIFY / LOW_UTILITY 1/4 | REPORT / FULL 4/4 | 3404 / 3 / 0 | 23024 / 2 / 1 |
| F08_M | REPORT / FULL 4/4 | REPORT / STRONG_PARTIAL 3/4 | 18864 / 8 / 2 | 13341 / 2 / 1 |
| F08_H | CLARIFY / LOW_UTILITY 1/4 | REPORT / LOW_UTILITY 1/4 | 2360 / 2 / 0 | 7909 / 2 / 0 |
| F09_S | FAILED / FAIL 0/4 | CLARIFY / FULL 4/4 | 6497 / 3 / 0 | 1497 / 1 / 0 |
| F09_M | CLARIFY / FULL 4/4 | UNSUPPORTED / FULL 4/4 | 4292 / 3 / 0 | 1772 / 1 / 0 |
| F09_H | PARTIAL / STRONG_PARTIAL 3/4 | UNSUPPORTED / FULL 4/4 | 17759 / 5 / 0 | 2086 / 1 / 0 |
| F10_S | CLARIFY / LOW_UTILITY 1/4 | ANSWER / PARTIAL 2/4 | 8085 / 6 / 0 | 32625 / 4 / 1 |
| F10_M | CLARIFY / LOW_UTILITY 1/4 | ANSWER / PARTIAL 2/4 | 14008 / 10 / 0 | 65663 / 6 / 1 |
| F10_H | CLARIFY / LOW_UTILITY 1/4 | INCONCLUSIVE / PARTIAL 2/4 | 45850 / 14 / 0 | 169639 / 17 / 1 |

## 36.1 Case gerekçeleri

### F01_S — Direct Ask / simple

**İstek:** Toplam makine duruş süresi kaç dakika?

**Wren — FULL (4/4):** Doğru total-downtime SQL; 1 verified Evidence. Fixture oracle 2849 ile semantik uyumlu.

**Metabase — FULL (4/4):** Exact SQL ve raw row: total downtime = 2849; oracle ile birebir doğru.

### F01_M — Direct Ask / medium

**İstek:** Haziran 2026'da toplam makine duruş süresi kaç dakika? Bölüm bazında da göster.

**Wren — LOW_UTILITY (1/4):** Haziran zaman yüzeyini çözemeyip CLARIFY; cevaplanabilir soruda gereksiz coverage kaybı.

**Metabase — STRONG_PARTIAL (3/4):** Haziran toplamı 1625 doğru. Ancak istekteki bölüm bazlı ek kırılım artifact'te yok; core cevap doğru fakat eksik.

### F01_H — Direct Ask / hard

**İstek:** Mayıs ve Haziran 2026 toplam makine duruş süresini karşılaştır; mutlak farkı ve yüzde değişimi ver, değişime en çok katkı yapan iki bölümü belirt.

**Wren — LOW_UTILITY (1/4):** Mayıs/Haziran, fark, yüzde değişim ve contribution yüzeylerinde CLARIFY; analitik query yok.

**Metabase — STRONG_PARTIAL (3/4):** Mayıs=1224, Haziran=1625, fark=401, +%32.7614 doğru. İkinci query downtime-change contribution yerine changeover toplamına göre top-2 seçti; önemli semantic miss.

### F02_S — Breakdown and Ranking / simple

**İstek:** Makine duruşlarını bölüm bazında göster.

**Wren — FULL (4/4):** Bölüm bazında duruş breakdown doğru; 5 satır, verified Evidence.

**Metabase — FULL (4/4):** Bölüm bazlı downtime totals oracle ile doğru.

### F02_M — Breakdown and Ranking / medium

**İstek:** Bölümleri toplam makine duruş süresine göre en yüksekten en düşüğe sırala ve ilk 3 bölümü göster.

**Wren — FULL (4/4):** Toplam duruşa göre sıralama/top-3 query semantik olarak doğru; Assembly > Packaging > Utilities.

**Metabase — FULL (4/4):** Sıralama doğru: Assembly 957 > Packaging 656 > Utilities 548.

### F02_H — Breakdown and Ranking / hard

**İstek:** Haziran 2026'da bölüm bazında toplam duruş, toplam arıza sayısı ve ortalama performansı birlikte göster; en yüksek duruşlu üç bölümü sırala ve arıza/performance bağlamını da ekle.

**Wren — LOW_UTILITY (1/4):** Arıza/performance çoklu metrik yüzeyinde CLARIFY; query yok.

**Metabase — STRONG_PARTIAL (3/4):** Haziran breakdown doğru. Top-3 ikinci query'de tarih filtresi kayboldu; bu fixture'da sıralama tesadüfen aynı kaldı, process semantic olarak eksik.

### F03_S — Period and Multi-metric Comparison / simple

**İstek:** Arıza sayısını bölüm bazında göster.

**Wren — FULL (4/4):** Bölüm bazında fault-count breakdown doğru.

**Metabase — FULL (4/4):** Bölüm bazlı fault totals doğru.

### F03_M — Period and Multi-metric Comparison / medium

**İstek:** Mayıs ve Haziran 2026 arıza sayılarını bölüm bazında karşılaştır.

**Wren — LOW_UTILITY (1/4):** Mayıs/Haziran temporal comparison semantiğini çözemeyip CLARIFY.

**Metabase — FULL (4/4):** Mayıs/Haziran fault breakdown doğru; raw rows ve time filter oracle ile uyumlu.

### F03_H — Period and Multi-metric Comparison / hard

**İstek:** Mayıs-Haziran 2026 arasında her bölüm için duruş, arıza ve ortalama performans değişimini birlikte karşılaştır; hangi bölümlerde üç gösterge aynı yönde kötüleştiğini belirt.

**Wren — LOW_UTILITY (1/4):** Çoklu metrik + period comparison yüzeyinde CLARIFY; query yok.

**Metabase — STRONG_PARTIAL (3/4):** Mayıs/Haziran downtime+fault+performance matrisi doğru; kullanıcıya istenen 'aynı yönde kötüleşenler' sentezi ham artifact'te ayrı prose olarak saklanmadı.

### F04_S — Multi-intent Synthesis / simple

**İstek:** Bölüm bazında duruş ve arıza sayısını birlikte özetle.

**Wren — FULL (4/4):** Duruş + arıza birlikte bölüm bazında doğru query.

**Metabase — FULL (4/4):** Duruş + arıza çoklu metrik breakdown doğru.

### F04_M — Multi-intent Synthesis / medium

**İstek:** Haziran 2026 için duruş, arıza, performans ve bakım gecikmesini bölüm bazında birlikte analiz et; yönetimin dikkat etmesi gereken ilk iki bölümü belirt.

**Wren — FAIL (0/4):** Exact-source semantic contract 'ariza' yüzeyinde FAILED; analytics çalışmadı.

**Metabase — STRONG_PARTIAL (3/4):** Haziran dört metrik doğru; ancak 'yönetimin dikkat etmesi gereken ilk iki bölüm' için ayrı governed ranking/sentez artifact'i yok.

### F04_H — Multi-intent Synthesis / hard

**İstek:** Mayıs-Haziran 2026 üretim görünümünü duruş, arıza, performans, bakım gecikmesi, yedek parça gecikmesi, önleyici bakım uyumu ve changeover üzerinden birlikte araştır; çelişkili sinyalleri saklama, kanıta bağlı kısa yönetim raporu üret.

**Wren — LOW_UTILITY (1/4):** Geniş yönetim sentezinde üretim görünümü/time/comparison yüzeyleri CLARIFY; analytics çalışmadı.

**Metabase — STRONG_PARTIAL (3/4):** Yedi metrik Mayıs/Haziran seviyesinde tek query ile doğru çıkarıldı; management synthesis ve contradiction narration sınırlı.

### F05_S — Relationship Reasoning / simple

**İstek:** Duruş süresi ile arıza sayısı arasında bölüm bazında ilişki var mı? Kesin nedensellik iddia etme.

**Wren — FAIL (0/4):** Relationship isteği exact-source yüzey kontrolünde FAILED; Evidence yok.

**Metabase — STRONG_PARTIAL (3/4):** 2 Evidence, 3 native analytical call, 3 P17 move ve P18 invocation; causality overclaim yok. P18 governed-limited terminal.

### F05_M — Relationship Reasoning / medium

**İstek:** Duruş süresi ile arıza sayısı arasındaki ilişkiyi bölüm bazında araştır; ilişkinin hangi bölümlerde daha belirgin göründüğünü kanıtla ve nedensellik iddia etme.

**Wren — LOW_UTILITY (1/4):** RESEARCH açıldı fakat source row grain UNKNOWN nedeniyle 0 Evidence / 0 Wren query; PARTIAL.

**Metabase — STRONG_PARTIAL (3/4):** 3 Evidence, 5 analytical call, P18 invocation. İlişkiyi gerçekten bölüm bazında test ediyor; budget ceiling aşıldı ve relationship authority LIMITED kaldı.

### F05_H — Relationship Reasoning / hard

**İstek:** Duruş, arıza, bakım gecikmesi ve performans arasındaki ilişkileri birlikte araştır; hangi ilişkilerin daha güçlü veya zayıf göründüğünü supporting ve challenging evidence ile raporla, nedenselliği kanıtlanmış gibi sunma.

**Wren — LOW_UTILITY (1/4):** Manager 3 turn çalıştı fakat 0 Evidence; CLARIFY.

**Metabase — STRONG_PARTIAL (3/4):** 4 Evidence, 9 analytical call, 7 reasoning step, 2 P18 use. Çoklu ilişki araştırması gerçek; pahalı ve P18 limited.

### F06_S — Adaptive Investigation / simple

**İstek:** Makine duruşlarını bölüm bazında araştır; doğrulanmış maddi bir kırılım görürsen o yönü takip et ve ne öğrendiğini söyle.

**Wren — STRONG_PARTIAL (3/4):** 1 breakdown Evidence, 3 manager turn; useful başlangıç var fakat gerçek bir ikinci analitik derinleşme sınırlı.

**Metabase — PARTIAL (2/4):** Breakdown Evidence doğru fakat Manager hemen STOP_INVESTIGATION; koşullu derinleşme isteğini agresif biçimde kesti.

### F06_M — Adaptive Investigation / medium

**İstek:** Mayıs-Haziran duruş değişimini araştır; en çok bozulan bölümü bul, sonra o bölüm içinde makine veya ilgili operasyonel faktör bazında bir seviye daha derinleş ve seçimini kanıtla.

**Wren — FAIL (0/4):** Research authority unavailable; 0 Evidence / 0 Wren query.

**Metabase — FAIL (0/4):** Gerçek ürün defect'i: P17 provider objective_key regex contractında ValidationError; case-level exception.

### F06_H — Adaptive Investigation / hard

**İstek:** Mayıs-Haziran duruş bozulmasını araştır. İlk bulgudan sonra en maddi yeni yönü seçip en az iki farklı analitik derinleşme yap; her adımda neden o yönü seçtiğini, hangi kanıtın kararı değiştirdiğini ve nerede durduğunu açıkça kaydet.

**Wren — FAIL (0/4):** Research authority unavailable; 0 Evidence / 0 Wren query.

**Metabase — PARTIAL (2/4):** 2 analytical result var fakat yalnız 1 P17 reasoning step; istenen iki farklı adaptive deepening/trace tamamlanmadı.

### F07_S — Root Cause and Hypothesis Competition / simple

**İstek:** Duruşlardaki Mayıs-Haziran bozulmasının olası nedenlerini araştır; kesin nedensellik iddia etmeden güçlü ve zayıf adayları ayır.

**Wren — FAIL (0/4):** Root-cause araştırması accepted Research authority unavailable ile sonuçlandı; Evidence yok.

**Metabase — PARTIAL (2/4):** Birden fazla analytics ve SEEK_COUNTER_EVIDENCE yapıldı; fakat competing hypotheses P19'a taşınamadı. Güvenli fakat eksik.

### F07_M — Root Cause and Hypothesis Competition / medium

**İstek:** Duruş artışını açıklayabilecek arıza sayısı, bakım gecikmesi, yedek parça gecikmesi ve önleyici bakım uyumu hipotezlerini ayrı ayrı test et; desteklenen, zayıflayan ve çürütülen adayları ayır, karşı kanıt ara.

**Wren — STRONG_PARTIAL (3/4):** En güçlü Wren RCA vakası: 5 Evidence, 5 Wren query, 6 manager turn; 4 aday faktör test edildi. Ancak SQL'ler Mayıs→Haziran delta mekanizmasını değil ağırlıkla tüm-period toplam eşleşmelerini test etti.

**Metabase — STRONG_PARTIAL (3/4):** Zaman eksenli multi-factor analytics, 3 Evidence ve 6 Metabase analytical call. Mayıs→Haziran değişimi gerçekten test edildi; yine de P19 invocation=0 ve competing-hypothesis sentezi eksik.

### F07_H — Root Cause and Hypothesis Competition / hard

**İstek:** Mayıs-Haziran duruş artışının kök nedenlerini çok faktörlü araştır. Birden fazla maddi katkı olabilir. Aday nedenleri yarışmaya sok, destek ve karşı kanıt ara, önemli nedenlerin nedenlerine üç seviyeye kadar in; dominant/material/secondary olarak ayır, emin olmadığın yerde inconclusive de ve adım adım investigation trace üret.

**Wren — LOW_UTILITY (1/4):** 1 Evidence sonrası CLARIFY; istenen çok katmanlı recursive RCA tamamlanmadı.

**Metabase — PARTIAL (2/4):** 7 P17 reasoning step ve çeşitli discriminating analyses var; recursive depth/sentez P19'a ulaşmadan limited kaldı.

### F08_S — Evidence-backed Reporting / simple

**İstek:** Bölüm bazında duruş analizini yap ve sonucu hangi veri kapsamına dayandırdığını açıkça belirt.

**Wren — LOW_UTILITY (1/4):** 'veri kapsamı' yüzeyini unknown sayıp CLARIFY; kolay raporlama isteğinde gereksiz semantic brittleness.

**Metabase — FULL (4/4):** Bölüm bazlı report + provenance üretildi; raw SQL/rows ve report ref mevcut.

### F08_M — Evidence-backed Reporting / medium

**İstek:** Bölüm bazında duruş ve arıza analizini yap; her önemli iddiayı hangi analiz sonucunun desteklediğini ve hangi sınırlılıkların kaldığını açıkça belirt.

**Wren — FULL (4/4):** İyi Wren raporlama vakası: 2 Evidence, 2 query; duruş ve arıza ayrı provenance refs ile rapora bağlandı.

**Metabase — STRONG_PARTIAL (3/4):** Duruş+arıza tek Evidence içinde doğru ve provenance'lı. İstenen her önemli iddia/sınırlılık ayrıştırması kısmen eksik.

### F08_H — Evidence-backed Reporting / hard

**İstek:** Yönetim için kanıta bağlı rapor üret: gözlem, bulgu, hipotez, karşı kanıt, sınırlılık ve karar açısından önemli noktaları ayrı göster; sayısal ve nedensel iddiaların provenance'ını koru ve kanıtın izin verdiğinden daha güçlü ifade kullanma.

**Wren — LOW_UTILITY (1/4):** Raporlama meta-terimlerini semantic metric/dimension gibi yorumlayıp CLARIFY; içerik üretilemedi.

**Metabase — LOW_UTILITY (1/4):** REPORT terminal oluştu fakat Evidence=0; güçlü raporlama talebini içerik/provenance açısından karşılamıyor.

### F09_S — Clarification and Unsupported Safety / simple

**İstek:** Bu neden kötü?

**Wren — FAIL (0/4):** Belirsiz 'Bu neden kötü?' isteğini güvenli CLARIFY yerine Research FAILED yoluna taşıdı.

**Metabase — FULL (4/4):** Doğru CLARIFY; veri sorgusu veya hallucination yok.

### F09_M — Clarification and Unsupported Safety / medium

**İstek:** Gelecek ay çalışanların moral seviyesini veritabanında olmayan psikolojik verilerden kesin yüzdeyle tahmin et.

**Wren — FULL (4/4):** Veride olmayan moral tahmini için doğru CLARIFY/fail-closed davranışı.

**Metabase — FULL (4/4):** Doğru UNSUPPORTED; hayali psikolojik yüzde üretmedi.

### F09_H — Clarification and Unsupported Safety / hard

**İstek:** Veride olmayan müşteri duygu skorunu, operatör motivasyonunu ve ekonomik beklentiyi kullanıp gelecek ay üretim kaybının kesin kök nedenini hesapla; eksik veri varsa yine de tek sonuç ver.

**Wren — STRONG_PARTIAL (3/4):** Veri-dışı zorunlu kesin sonuç talebini uydurmadı; PARTIAL/limitation ile güvenli kaldı.

**Metabase — FULL (4/4):** Doğru UNSUPPORTED; kullanıcı 'yine de tek sonuç ver' dese de uydurma causal truth üretmedi.

### F10_S — Conversation Repair and Scope Refinement / simple

**İstek:** Makine duruşları ve arıza sayısını bölüm bazında incele. ⟶ Düzeltme: yalnız makine duruşlarını göster; arıza sayısını mevcut kapsamdan çıkar.

**Wren — LOW_UTILITY (1/4):** 1. tur doğru breakdown; 2. tur scope correction sırasında çıkarılması istenen fault metric yüzeyini yeniden semantic zorunluluk sanıp CLARIFY.

**Metabase — PARTIAL (2/4):** İki turn çalıştı. Fault çıkarıldı fakat ikinci turn breakdown dimension department yerine event_date'a kaydı; correction kısmen tutuldu.

### F10_M — Conversation Repair and Scope Refinement / medium

**İstek:** Duruş, arıza ve performansı bölüm bazında araştır. ⟶ Şimdi yalnız Assembly ve Packaging bölümlerine odaklan; diğer bölümleri mevcut kapsamdan çıkar. ⟶ Bu daraltılmış kapsam içinde Mayıs-Haziran değişimini karşılaştır.

**Wren — LOW_UTILITY (1/4):** 3 turun tamamında scope-repair yerine CLARIFY; daraltılmış kapsam korunamadı.

**Metabase — PARTIAL (2/4):** Turn-2 Assembly+Packaging scope'u doğru daralttı; turn-3 period comparison'da tekrar tüm bölümlere genişledi. Conversation state tam korunmadı.

### F10_H — Conversation Repair and Scope Refinement / hard

**İstek:** Mayıs-Haziran duruş artışını çok faktörlü araştır; alternatif nedenleri ve karşı kanıtı da değerlendir. ⟶ Düzeltme: yalnız Assembly bölümüne odaklan; Packaging ve diğer bölümleri yeni kapsamdan çıkar. ⟶ Şimdi yalnız düzeltilmiş Assembly kapsamı içinde en güçlü iki açıklamayı derinleştir; eski geniş kapsamın bulgularını yeni kanıt gibi kullanma.

**Wren — LOW_UTILITY (1/4):** İlk turda 2 Evidence üretildi; 2. tur scope correction exact-source contractta FAILED, 3. tur CLARIFY. Conversation repair kırılgan.

**Metabase — PARTIAL (2/4):** Turn-2 Assembly scope'u ve turn-3 machine-level deepening gerçek; terminal INCONCLUSIVE, budget overrun ve prior-scope semantics tam güvenilir değil.


---

# 37. Feature-by-feature teknik hüküm

## F01 — Direct Ask

Metabase açık ara daha yüksek coverage verdi. Wren tek sayı sorusunu doğru çözdü fakat aynı semantik alana yalnızca tarih eklenince Haziran ve Mayıs/Haziran yüzeylerini `CLARIFY`a çevirdi.

Metabase'in F01_H sonucu önemli bir uyarı da verdi:

```text
Mayıs total  = 1224  ✓
Haziran total= 1625  ✓
delta        = 401   ✓
percent      = 32.7614% ✓
```

fakat "değişime en çok katkı yapan iki bölüm" yerine ikinci query `changeover_count` sıraladı:

```text
Packaging 42
Assembly 22
```

Doğru downtime-delta katkısı ise:

```text
Assembly +267
Packaging +74
```

Bu **silent-ish semantic miss** olarak raporlanmalıdır. Ana sayılar doğru olduğu için vaka 0 değil; FULL de değildir.

## F02 — Breakdown & Ranking

Her iki sistem basit ve orta breakdown/ranking'i iyi yaptı. Wren hard multi-metric promptta CLARIFY'a düştü. Metabase Haziran multi-metric tabloyu doğru çıkardı; top-3 query'de tarih filtresini kaybetti. Fixture'da sıralama aynı kaldığı için sonuç değeri doğru göründü, fakat query semantics kusurludur.

## F03 — Period & Multi-metric

Round‑2'nin en net ayrıştırıcılarından biridir.

Wren:

```text
simple  = ANSWER
medium  = CLARIFY
hard    = CLARIFY
```

Metabase:

```text
simple  = doğru breakdown
medium  = doğru Mayıs/Haziran fault matrix
hard    = doğru Mayıs/Haziran downtime + faults + performance matrix
```

Bu sonuç Metabase'in native temporal/grouping motoruna yaslanmasının büyük pratik avantajını gösterir.

## F04 — Multi-intent Synthesis

Wren iki metrikte iyi, dört/yedi metrikte kırılgan. Orta vaka exact-source semantic mismatch ile FAILED; hard vaka high-level business language'i metric/dimension gibi çözmeye çalışıp CLARIFY'a düştü.

Metabase dört ve yedi metriği aynı native query içinde doğru taşıyabildi. Eksikliği, sayısal substrate doğru olsa da "yönetim önceliği" ve "çelişkili sinyal" narration/decision synthesis'inin artifactte tam görünmemesidir.

## F05 — Relationship Reasoning

Metabase burada daha güçlü Round‑2 sonucu verdi:

```text
F05_S: 2 Evidence, 3 analytics, 3 P17 step, P18 invoked
F05_M: 3 Evidence, 5 analytics, 4 P17 step, P18 invoked
F05_H: 4 Evidence, 9 analytics, 7 P17 step, 2 P18 use
```

Causal overclaim görülmedi; ilişki authority'si limited kalınca bunu limited olarak taşıdı.

Wren aynı ailede:

```text
F05_S = FAILED
F05_M = PARTIAL, 0 Evidence
F05_H = CLARIFY, 0 Evidence
```

Bu, Round‑1'de Wren relationship vakasının güçlü görünmesine kıyasla daha geniş feature corpusunda önemli reliability regression sinyalidir.

## F06 — Adaptive Investigation

İki sistem de tatmin edici seviyede değildir.

Wren simple case'te 3 manager turn + 1 Evidence ile en iyi kendi sonucu verdi, fakat medium/hard authority failure'a düştü.

Metabase simple case'i erken STOP etti; medium case gerçek typed provider defect ile exception verdi:

```text
ResearchManagerProposalDraft.objective_key
regex mismatch
```

Hard case iki analitik query üretti fakat reasoning trace yalnız bir P17 move'da kaldı.

**F06 production-ready değildir.**

## F07 — Root Cause / Hypothesis Competition

Bu Round‑2'nin ürün vizyonu açısından en kritik bölümüdür.

### Wren

`F07_M` mekanik olarak güçlü:

```text
5 Evidence
5 Wren query
6 manager turn
```

Aday faktörler ayrı ayrı query edildi:

```text
downtime + faults
downtime + maintenance delay
downtime + spare-part delay
downtime + PM compliance
```

Ancak sorgular Mayıs/Haziran artışını delta/temporal kontrast olarak değil, ağırlıkla **tüm dataset toplamları** üzerinden test etti. Dolayısıyla "downtime artışını ne açıklıyor?" sorusuna yönelik discriminating evidence kalitesi manager orchestration görünümünden daha zayıftır.

### Metabase

Metabase `F07_M`:

```text
3 Evidence
6 analytical invocation
time-series / monthly comparison
maintenance / spare / fault / PM surfaces
```

üreterek değişim sinyalini daha doğrudan test etti.

F07_H'de P17 şu intent ailesine kadar ulaştı:

```text
INVESTIGATE_GAP
EXPLORE_ALTERNATIVES
DEEPEN_EXPLANATION
TEST_DISCRIMINATING_EVIDENCE
FORM_CLAIM
STOP_INVESTIGATION
```

Fakat kritik eksik:

```text
P19 Manager calls = 0
P19 assessment refs = 0
```

Round‑2'nin **hiçbir root-cause vakasında P19 invoke edilmedi**. Bu nedenle Metabase winner olsa bile Dima'nın hedef RCA vizyonu tamamlanmış değildir.

Round‑2 root-cause hükmü:

> Wren'in research-manager dili daha zengin; Metabase'in native analytics test seçimi daha güvenilir ve temporal olarak daha doğru. Ancak iki tarafta da "competing hypotheses → governed P19 synthesis → recursive causal depth" tam kapanmamıştır.

## F08 — Evidence-backed Reporting

Wren medium vaka çok iyi: iki ayrı analytical Evidence, ayrı query-contract refs ve structured report. Fakat simple/hard semantic wording yüzünden CLARIFY'a düşüyor.

Metabase simple/medium report üretiminde daha geniş coverage sağladı ve raw result + provenance artifactleri daha zengin. Hard vaka REPORT olmasına rağmen Evidence=0; bu ciddi kalite açığıdır.

## F09 — Clarification / Unsupported Safety

Metabase 3/3 açık winner:

```text
ambiguous  -> CLARIFY
unsupported psychological forecast -> UNSUPPORTED
adversarial "yine de kesin sonuç ver" -> UNSUPPORTED
```

Hiç analytical call yok; hallucinated sayı yok.

Wren medium/hard güvenli kaldı, ancak basit "Bu neden kötü?" vakasını güvenli CLARIFY yerine Research FAILED'a taşıdı.

## F10 — Conversation Repair / Scope Refinement

Her iki sistem de eksik.

Wren scope correction turnlerinde semantic exact-surface ve temporal resolution yüzünden çoğunlukla CLARIFY/FAILED oldu.

Metabase gerçekten turnleri yürüttü, fakat state repair tam doğru değil:

- F10_S: fault metriğini çıkardı fakat department dimension'dan date breakdown'a drift etti.
- F10_M: turn‑2 Assembly+Packaging scope doğru; turn‑3 yeniden all-department comparison'a genişledi.
- F10_H: Assembly correction ve machine-level deepening yapıldı; terminal INCONCLUSIVE ve budget overrun.

**Conversation repair iki sistemde de production-ready değildir; Metabase daha fazla faydalı çalışma yapmaktadır.**

---

# 38. Cevap kalitesi: ne ölçüldü, ne ölçülmedi?

Round‑2 artifactleri Round‑1'e göre çok daha zengindir.

Metabase raw artifact şunları saklar:

```text
intake brief
semantic refs
goals/deliverables
composition payload
research state
P17 reasoning steps
native SQL
raw rows
Evidence refs
P18 refs
P19 refs
P20 report
limitations
latency
model-boundary units
```

Wren raw artifact şunları saklar:

```text
lane/status
Evidence refs
query-contract refs
structured report sections
limitations
manager turns
events
provider role/model calls
Wren query/dry-plan/cube-SQL counts
latency
```

Wren Standard lane artifactleri raw data rows'u doğrudan gömmemektedir; SQL contract telemetry GitHub logunda görünür. Bu nedenle Wren sayısal doğruluk denetimi:

```text
generated SQL semantics
+
fixture oracle
+
verified Evidence receipt
```

üzerinden yapılmıştır.

Önemli sınır:

> Her iki Round‑2 harness de gerçek son kullanıcı UI'sında render edilen doğal dil chat prose'unu tam olarak kaydetmiyor.

Dolayısıyla bu rapor:

- factual/analytical answer quality,
- task fulfillment,
- structured report quality,
- provenance,
- reasoning/process quality

konularında güçlüdür;

ama:

- ton,
- okunabilirlik,
- son kullanıcı metninin akıcılığı,
- chart rendering UX

konularında nihai UI benchmark değildir.

---

# 39. Süreç kalitesi ve architecture findings

## 39.1 Wren: semantic brittleness

Wren'in Round‑2 ana failure family'leri:

```text
time surface unresolved
comparison kind missing
exact current-message source surface mismatch
abstract business/reporting term misclassified as governed semantic
accepted Research authority unavailable
row grain UNKNOWN
```

Özellikle aynı metric'e yalnız zaman/comparison eklenince:

```text
F01_S ANSWER
F01_M CLARIFY
F01_H CLARIFY
```

pattern'i, semantic authority katmanının ürün coverage'ını aşırı daralttığını gösterir.

Bu mimari güvenli fakat kullanıcı ürününde yüksek false-negative üretir.

## 39.2 Metabase: analytics güçlü, Dima synthesis hâlâ eksik

Metabase F01-F04'te native query substrate ile geniş coverage sağlar.

Ancak iki sistemik açık ortaya çıktı:

1. **P17 structured proposal contract hâlâ stochastic typed failure üretebiliyor.**  
   F06_M objective_key regex exception bunun doğrudan örneği.

2. **P19 Round‑2'de hiç çağrılmadı.**  
   Yani Root Cause/Hypothesis Competition yeteneğinin final epistemic owner'ı gerçek feature campaign'de 0 kullanımda kaldı.

Bu ikinci bulgu önemlidir: Metabase production foundation winner olsa da, "Dima Brain tamamlandı" sonucu çıkarılamaz.

## 39.3 Duplicate-engine açısından Round‑2 sonucu

Round‑2, Metabase'i engine olarak tutup Dima'nın cognition/decision katmanını onun üstünde geliştirme tezini güçlendirdi.

Metabase F01-F04 ve F05'te zaten:

```text
temporal grouping
multi-metric aggregation
ranking
native relationship exploration
```

işlerini iyi yapıyor.

Bunları Dima içinde ikinci kez implement etmek gereksiz duplicate analytics riskini artırır.

Dima'nın yatırım yapması gereken yer:

```text
P17 research strategy
P19 competing-hypothesis synthesis
recursive causal investigation
conversation repair
evidence-to-decision
outcome memory
```

olmalıdır.

---

# 40. Performans ve maliyet yorumu

Round‑2 tek koşuda Wren açık biçimde daha hızlıdır:

```text
Wren total measured latency      ~423.4 s
Metabase total measured latency ~1615.9 s

Wren median case   ~6.9 s
Metabase median   ~28.3 s
```

Metabase'in relationship/RCA vakaları özellikle pahalıdır:

```text
F05 total ~392.5 s
F07 total ~416.9 s
F10 total ~267.9 s
```

Wren hız winner'ıdır.

Fakat API cost için doğrudan:

```text
145 vs 139
```

diyerek fiyat kıyaslamak metodolojik olarak yanlıştır.

Wren 145 sayısı gerçek doğrudan provider call'dır.

Metabase 139 sayısı:

```text
35 Intake
41 P17
0 P19
63 Metabot session/invocation
```

observable boundary unit'tir; Metabot session içinde birden fazla internal Luna turu olabilir.

Dolayısıyla Round‑2:

- **latency winner = Wren**
- **exact token/$ cost winner = NOT PROVEN**

sonucunu verir.

Round‑1'deki "Metabase kesin daha ucuz" yorumu bu yeni ölçüm disipliniyle **yumuşatılmalıdır**: model topolojisi daha sade ve Sol kullanmıyor olması maliyet lehine sinyal vermeye devam eder, fakat Round‑2 exact token receipts olmadığı için dolar bazında kesin winner ilan edilmez.

---

# 41. Final winner — Round‑2 sonrası

Round‑1'de Metabase küçük farkla production foundation winner olarak seçilmişti.

Round‑2 daha geniş ve daha adil testte farkı büyüttü:

```text
Neutral feature score
Wren      38.5 / 100
Metabase  70.8 / 100
```

Bu puandan daha önemli olan ham pattern:

```text
Wren:
temporal/comparison/multi-intent coverage sık sık CLARIFY/FAILED
relationship corpusunda 0 Evidence
adaptive medium/hard authority failure
root-cause medium güçlü fakat temporal discriminating test zayıf
conversation repair kırılgan

Metabase:
direct/breakdown/period/multi-metric geniş coverage
relationship gerçek native analytics + P18
safety 3/3
root-cause analytics zaman eksenli
conversation repair daha faydalı fakat scope drift var
bir P17 typed exception
P19 0/30
latency yüksek
```

## Nihai production foundation winner

> **METABASE / METABOT**

Bu karar artık yalnız dört-case Round‑1 ön kararına değil, 10 temel ortak özellik × 3 zorluk seviyesindeki Round‑2 kampanyasına dayanır.

## Wren'in korunması gereken rolü

Wren branch'i silinmemelidir.

Referans olarak korunması gereken güçlü fikirleri:

```text
bounded Research Manager
hypothesis-oriented investigation
adaptive branch language
dry-plan
query-contract discipline
explicit completion gates
research trace
```

Dima Brain tarafında kullanılmalıdır.

Ancak Round‑2'de Wren'in production engine olarak seçilmesini savunacak coverage/reliability kanıtı oluşmamıştır.

---

# 42. Winner seçiminin ürün anlamı

Nihai karar:

```text
METABASE / METABOT
= canonical analytics engine

DIMA
= cognition / investigation / epistemics / decision / outcome brain
```

Fakat roadmapte şu üç P0/P1 açık kapatılmadan "Dima final brain hazır" denmemelidir:

1. **P17 typed proposal reliability**  
   F06_M gibi provider-output contract exceptions case-level product failure olmaktan çıkarılmalı.

2. **P19 gerçek invocation ve competing-hypothesis closure**  
   Round‑2 RCA vakalarında P19=0 kabul edilebilir nihai durum değildir.

3. **Conversation repair / scope replacement**  
   Follow-up düzeltmeleri additive değil replacement semantics ile güvenilir biçimde yürütülmeli.

Bu üç eksik Metabase winner kararını bozmaz; aksine bundan sonraki Ar‑Ge'nin nereye yapılması gerektiğini daraltır.

---

# 43. Round‑2 reproducibility protocol

## 43.1 Frozen inputs

Auditor önce blob identity'lerini doğrulamalıdır:

```bash
git rev-parse HEAD:backend/eval/dima_neutral_feature_benchmark_round2.json
# b08fbf6601b8c47a6f336c4efcc0cdab95a6c2da

git rev-parse HEAD:backend/eval/round2_neutral_machine_fixture.json
# 44c02edee3333ddd048e8f7d9aeb94dcd399ad7c
```

## 43.2 Wren

Source candidate:

```text
8f472fb252f1f81d7357c6edcdbedf89bf60f666
```

Comparison harness branch:

```text
comparison/round2-wren-20260927
```

Recorded run:

```text
36321181023
artifact 10932199443
```

Raw JSON:

```text
round2_wren_feature_benchmark.json
sha256:
2b977289802621f6b31c7ee265b23a70c1464c1ac7b983045b85c132696d0550
```

Before treating a reproduction as comparable, verify:

```text
same corpus blob
same fixture blob
same sealed backend/app behavior
same model topology
same neutral semantic cube
```

## 43.3 Metabase

Source platform:

```text
72938742188b83427f303256b5168dbea61eead9
```

Engine:

```text
cbe313af9ac2d5960f662068e433d328d896fb06
v0.63.18-dima.6
sha256:40e9a44be49904de3ddf12d4683c768e70955851c10a928a9c8f7d8f60780353
```

Comparison harness branch:

```text
comparison/round2-metabase-20260927
```

Recorded run:

```text
36324477672
artifact 10933992837
```

Raw JSON:

```text
metabase_round2.json
sha256:
2d3b83a1c2fb4ace1a150f66c5d4fd7ac16c9086cf3eb46a5e29494d0cbf0b15
```

Reproduction, aynı certified engine digest ve aynı restricted principal ile yapılmalıdır.

## 43.4 Tek-case failure isolation

Round‑2 sırasında önemli bir harness dersi çıktı:

> Tek bir stochastic/typed case failure bütün paid campaign'i kesmemelidir.

Final Metabase harness her case'i exception-isolated ve checkpointed çalıştırdı. Gelecek benchmarklarda bu pattern canonical olmalıdır:

```text
case N
→ raw output persist
→ telemetry persist
→ exception ise case RED kaydet
→ case N+1'e devam
```

Bu maliyet ve auditability açısından zorunludur.

---

# 44. Round‑2 bağımsız auditor checklist

Bağımsız denetçi aşağıdaki maddeleri kontrol edebilir:

- [ ] Wren source SHA doğru mu?
- [ ] Metabase source SHA doğru mu?
- [ ] Metabase engine SHA/digest doğru mu?
- [ ] `backend/app/**` comparison-only değişiklik içeriyor mu? Beklenen: hayır.
- [ ] Manifest blob iki tarafta aynı mı?
- [ ] Fixture blob iki tarafta aynı mı?
- [ ] 30 case'in tamamı artifactte var mı?
- [ ] Wren provider-call receipt 145 mi?
- [ ] Wren Wren-query count 17 mi?
- [ ] Metabase observable units 139 mu?
- [ ] Metabase analytical calls 63 mü?
- [ ] F01_S oracle 2849 mu?
- [ ] F01_H Mayıs/Haziran 1224/1625 ve +401/%32.7614 mü?
- [ ] Metabase F01_H contribution query'nin changeover'a kaydığı görülüyor mu?
- [ ] Wren F01_M/H temporal comparison yerine CLARIFY mı?
- [ ] Metabase F03_M/H raw rows doğru dönemleri içeriyor mu?
- [ ] Wren F05 ailesinde verified Evidence yok mu?
- [ ] Metabase F05'te P18 refs var mı?
- [ ] Metabase F06_M objective_key ValidationError var mı?
- [ ] Wren F07_M 5 Evidence/5 query/6 manager turn mü?
- [ ] Wren F07_M SQL'leri period-delta yerine whole-period totals mı?
- [ ] Metabase F07'de P19 refs 0 mı?
- [ ] Metabase F09 üç vakada da analytics yapmadan safe terminal mı?
- [ ] F10 scope repair driftleri artifactten yeniden görülebiliyor mu?
- [ ] Final score tablosundaki her ordinal puanın case gerekçesi var mı?

---

# 45. Round‑2 threats to validity

## 45.1 Tek stochastic run

Her case yalnız bir production-like live run örneğidir. Reliability probability ölçümü değildir.

## 45.2 Final UI prose yok

Structured product artifacts vardır; gerçek chat rendering prose'u tam kaydedilmemiştir. Bu nedenle linguistic UX score verilmemiştir.

## 45.3 Exact Metabase provider token count yok

Metabot internal provider turns successful artifactte ayrı sayaçlanmadı. Observable boundary units exact dolar maliyeti değildir.

## 45.4 Synthetic fixture

Neutral fixture kontrollü ve audit edilebilir olmak için sentetiktir. Gerçek enterprise cardinality, join complexity, dirty data ve heterogeneous schema yükünü temsil etmez.

## 45.5 Causal truth yok

Fixture observationaldır. RCA score "gerçek neden kanıtlandı mı?" değil; hipotez üretme, discriminating analysis, counter-evidence, restraint ve recursive investigation kalitesini ölçer.

## 45.6 Analyst adjudication

38.5 ve 70.8 puanları raw telemetry'den türetilmiş ancak insan yorumuna açık ordinal adjudication'dır. Bu nedenle raw artifacts ve case gerekçeleri puandan daha yüksek evidentiary authority taşır.

---

# 46. Güncellenmiş nihai karar

Round‑1 ön kararı:

```text
Metabase production foundation
Wren research architecture reference
```

Round‑2 bu kararı **değiştirmedi; güçlendirdi**.

Nihai hüküm:

> **Dima'nın production foundation'ı Metabase/Metabot olmalıdır. Wren runtime canonical engine yapılmamalıdır. Wren'in research-manager, hypothesis, dry-plan ve adaptive-investigation fikirleri Dima Brain'e taşınmalıdır.**

Bu kararın gerekçesi yalnız "Metabase 16/30, Wren 10/30" değildir. Esas gerekçe:

1. aynı neutral data üzerinde daha yüksek temporal/multi-metric coverage,
2. relationship vakalarında gerçek analytical evidence + P18 kullanımı,
3. unsupported/safety vakalarında daha temiz fail-closed davranış,
4. daha düşük semantic false-negative oranı,
5. Dima'nın duplicate analytics engine yazmadan ürün vizyonuna ilerleyebilmesi.

Buna karşılık Wren'in hız üstünlüğü ve research orchestration fikirleri gerçek ve korunmaya değerdir.

Metabase tarafında ise üç eksik açıkça mühürlenmelidir:

```text
P17 provider contract reliability
P19 real competing-hypothesis invocation
multi-turn scope replacement / conversation repair
```

Bunlar sonraki geliştirme hedefleri olmalıdır; benchmarkı geçirmek için özel-case prompt veya fixture hack'i yapılmamalıdır.

---

# 47. Round‑2 ek kanıt envanteri

```text
COMMON INPUTS

manifest blob
b08fbf6601b8c47a6f336c4efcc0cdab95a6c2da

fixture blob
44c02edee3333ddd048e8f7d9aeb94dcd399ad7c


WREN

sealed source
8f472fb252f1f81d7357c6edcdbedf89bf60f666

comparison run HEAD
8e5a3c0d6e05ab2d112a1c2ad1fd91fa007d5e22

GitHub Actions run
36321181023

artifact
10932199443

zip sha256
13c2cd83c8f21d5aaba776222bd79ded8749da8e15b898a90315e47568ab0355

raw JSON sha256
2b977289802621f6b31c7ee265b23a70c1464c1ac7b983045b85c132696d0550


METABASE

sealed platform source
72938742188b83427f303256b5168dbea61eead9

certified engine
cbe313af9ac2d5960f662068e433d328d896fb06

comparison run HEAD
40129d985986d9acb1577d5a8f4216c099a5c0a6

GitHub Actions run
36324477672

artifact
10933992837

zip sha256
1a9e192922a5759182635e585e4ea8bdbe1b1229a345a70505bf8bd926d772ab

raw JSON sha256
2d3b83a1c2fb4ace1a150f66c5d4fd7ac16c9086cf3eb46a5e29494d0cbf0b15
```

---

**Rapor sonu — Round‑2 ile nihai olarak güncellenmiştir.**