# DIMA V2 — GELİŞTİRME DURUMU

**Branch:** `feat/ask-v2-mvp`  
**Başlangıç tabanı:** `wren-bağımsız@869280db316d5bf3f76d3253b8b80e5609a000b9`  
**Başlangıç tarihi:** 20 Eylül 2026  
**Durum:** **DAY 0 ACTIVE — SOURCE LOCK + BASELINE + V2 STUB**  
**Kod fazı:** Henüz başlamadı.

---

## 0. OTORİTE HARİTASI

### Aktif ve mühürlü — DEĞİŞTİRME

1. `DIMA_NIHAI_UYGULAMA_YOL_HARITASI.md`
   - uygulama sırası / P fazları / exit gate authority.
2. `DIMA_NIHAI_DENETIM_VE_MIMARI_RAPORU.md`
   - hedef mimari / kök neden / R bölümleri authority.

Bu iki belge branch'e kullanıcı tarafından verilen nihai sürümlerden **birebir** kopyalanmıştır.
Geliştirme ilerlemesi bu dosyalara işlenmez.

### Yaşayan belgeler

- `DIMA_V2_GELISTIRME_DURUM.md` — bu dosya; tek “nerede kaldık?” kaynağı.
- `../../MIMARI.md` — mevcut sistem gerçekleri + V2 authority overlay.
- `../../AGENTS.md` — V2 geliştirici/ajan çalışma sözleşmesi.
- `../../CLAUDE.md` — repo kuralları; V2 branch override üstte olmalıdır.

---

## 1. NORTH STAR — TEK CÜMLE

Eski `/ask` karar ağacını temizlemek değil; yanında izole, conversation-first,
single-semantic-owner bir V2 çekirdek kurmak ve çalışan auth/tenant/Wren/semantic/evidence
altyapısını typed adapter'larla reuse etmek.

---

## 2. PRE-DAY0 HAZIRLIK CHECKLIST

- [x] Yeni branch açıldı: `feat/ask-v2-mvp`.
- [x] Branch tam olarak denetlenen `869280d...` HEAD'inden oluşturuldu.
- [x] Nihai uygulama yol haritası aktif repo belgesi olarak eklendi.
- [x] Nihai mimari/denetim raporu aktif repo belgesi olarak eklendi.
- [x] Belgelerin canonical dosya adları kendi iç referanslarıyla uyumlu tutuldu.
- [x] `backend/AGENTS.md` V2 çalışma sözleşmesi eklendi.
- [x] `backend/CLAUDE.md` V2 aktif-operasyon override ile güncellendi.
- [x] `backend/MIMARI.md` V2 authority overlay ile güncellendi.
- [x] Branch diff yalnız hazırlık/authority belgelerini içeriyor; executable V2 kod değişikliği yok.
- [x] Mühürlü iki belgenin kaynakla içerik eşitliği doğrulandı (4744 / 6379 satır; içerik birebir).

### Erken başlanıp geri alınan iş

İlk branch açılışında `app/v2/__init__.py` ve `app/v2/models.py` iskeletleri erken
oluşturuldu. Kullanıcı kararıyla Day 0 başlamadan önce geri silindi.

**Neden:** branch/platform hazırlığı ile implementation başlangıcının git tarihinde ayrılması.

**Sonuç:** Day 0 temiz sınırdan başlayacak; bu iki dosyanın tasarımı authority sayılmaz.

---

## 3. ŞU ANKİ BORÇ DEFTERİ

### V2-D001 — Eski MIMARI/CLAUDE operasyon metni V2'yi henüz işaret etmiyor — **KAPANDI**

- Kaynak: P1 / R0.2
- Risk: yeni geliştirici eski “aktif operasyon”a gidebilir.
- Blocker: **CLOSED**
- Kapanış kanıtı: root `AGENTS.md` + `backend/AGENTS.md` + `CLAUDE.md` V2 override + `MIMARI.md` V2 authority overlay.
- Hedef: PRE-DAY0 — tamamlandı.

### V2-D002 — V2 executable code henüz yok

- Kaynak: P2
- Risk: yok; bilinçli başlangıç durumu.
- Blocker: NO
- Kapanış: Day 0 V2 island shell boot.
- Hedef: Day 0.

### V2-D003 — Önceki /ask denetim P0'ları legacy açık kaldığı sürece yaşamaya devam ediyor

Bilinen sınıflar:

- post-seal mutation / persisted-vs-HTTP divergence riski,
- parallel plan/request-state race,
- `None` ile failure/not-applicable semantiklerinin karışması,
- router ↔ plan reverse dependency,
- sync dependency → ContextVar principal propagation riski.

- Kaynak: R2/R3/R3A + önceki repo denetimi.
- Risk: V2 pilot öncesinde legacy trafik sürerken yalnız legacy yolu etkileyebilir.
- Blocker: **Day 0 için NO**, pilot/cutover değerlendirmesinde YES olabilir.
- Kapanış: V2'nin bu sınıfları yapısal olarak taşımadığının gate'leri; gerekirse legacy'ye
  küçük güvenlik/P0 patch'i. Legacy refactor kampanyası YOK.

---

## 4. TEST / HIZ POLİTİKASI

Geliştirme sırasında büyük suite her adımda koşulmaz.

- Unit/contract testi: yalnız yeni boundary veya P0 invariant için.
- Daily demo: aktif günün canonical user scenario'su.
- Toplu gate: milestone/demet sonunda.
- Nightly ağır suite: CI.
- Refactor/polish, çalışan dikey dilimi geciktiremez.

Bu politika hem roadmap P0A'nın “en hızlı doğrulanabilir kullanıcı değeri” ilkesine hem
repo `CLAUDE.md` içindeki toplu test kararına uygundur.

---

## 5. DAY 0 — SIRADAKİ TICKET (HENÜZ BAŞLAMADI)

**Roadmap:** P1 + P1B + P2 + P2B  
**Rapor:** R0–R6; özellikle R2, R3, R3A, R4, R5, R6  
**Amaç:** V2 island'ın boot ettiğini, doğru tenant/principal/Wren runtime'a bağlandığını ve
legacy semantic hot path'e girmediğini kanıtlamak.

### Başlamadan önce okunacak

- Roadmap: P0–P2B
- Report: R0–R6
- `MIMARI.md` V2 overlay + auth/Wren/current-runtime ilgili bölümleri
- `app/main.py`
- `app/company_registry.py`
- `app/wren_service.py`
- `app/auth/dependencies.py`
- `app/schemas.py`

### Beklenen Day 0 touch

Yeni:

- `app/v2/__init__.py`
- minimal `app/v2/models.py` veya runtime contract
- `app/v2/orchestrator.py`
- `app/routers/ask_v2.py`

Adapter:

- `app/main.py`
- `app/config.py` yalnız rollback/feature flag gerçekten gerekiyorsa

### Day 0 NO-TOUCH

- `app/routers/ask.py`
- `app/cube_router.py`
- `app/uyum.py`
- `app/plan_tuketici.py`
- `app/plan_semasi.py`

### Day 0 canonical scenario

`/ask-v2` protected route boot eder → principal/tenant çözülür → tenant-bound Wren schema/runtime
alınır → V2 kendi typed shell cevabını verir → legacy `/ask` semantic decision graph çağrılmaz.

### Day 0 exit

- legacy semantic hot-path import = 0
- demo tenant Wren smoke = pass
- feature-flag rollback = pass
- legacy behavior değişikliği = 0 P0

---

## 5A. DAY 0 ACTIVE TICKET — P3 SOURCE LOCK + BASELINE

**ROADMAP:** P0, P0A, P1/P1A/P1B, P2/P2B, **P3**  
**REPORT DAYANAK:** R0–R6; özellikle R2, R3/R3A, R4, R5/R5.6 ve immutable runtime ilkesi  
**NEW OWNER:** V2 bootstrap/runtime boundary + Day0 baseline artifact  
**OLD OWNER:** legacy `/ask` yalnız baseline ölçümünün deneği; V2 authority değildir.

### AMAÇ

Yeni beynin başlangıç noktasını ölçülebilir hâle getir ve aynı repo içinde legacy semantic
karar ağacına girmeyen, rollback edilebilir `/ask-v2` adasını boot ettir.

### USER SCENARIO / ACCEPTANCE

1. Basit KPI, top-N, comparison, ambiguity, follow-up, repair, social, explain-existing ve
   kompleks multi-domain ailelerinden en az 30 legacy vaka source/correctness/failure-stage/
   latency ile dondurulabilir bir baseline koşumuna girer.
2. Feature flag açıkken kimlikli kullanıcı `/ask-v2` stub'ına gider; principal/tenant
   çözülür; doğru tenant-bound Wren schema + mdl_version snapshot alınır; legacy semantic
   router/planner çağrılmaz; query çalışmaz.
3. Feature flag kapalıyken V2 görünmez/404; legacy davranış değişmez.

### INPUT / OUTPUT

**Input:** authenticated HTTP request + explicit `Principal` + tenant-bound `WrenService`.  
**Output Day0:** typed `TenantAnalyticsRuntimeV0` + V2 bootstrap response; query yok.

### FILES TO TOUCH

Yeni:
- `app/v2/__init__.py`
- `app/v2/models.py`
- `app/v2/orchestrator.py`
- `app/routers/ask_v2.py`
- `lab/v2_day0_baseline.py`
- `eval/v2_day0_cases.yaml`
- gerekli küçük V2 architecture/bootstrap testleri

Adapter:
- `app/main.py`
- `app/config.py`

### FILES NOT TO TOUCH

- `app/routers/ask.py`
- `app/cube_router.py`
- `app/uyum.py`
- `app/plan_tuketici.py`
- `app/plan_semasi.py`
- `app/wren_service.py` (Day0 için adapter ihtiyacı yoksa)

### TEST / DEMO — HIZ POLİTİKASI

Büyük suite yok. Yalnız:
- architecture import-ban testi,
- flag off/on bootstrap testi,
- explicit runtime identity/snapshot testi,
- baseline runner'ın case-selection/record schema testi.

Baseline koşumu ayrı artefakt üretir; ağır full gate Day0 demetinin sonuna bırakılır.

### KPI / EXIT

- representative baseline case >= 30
- known silent-wrong family coverage = 100% **envanterde tanımlanan set için**
- every baseline record failure_stage field = 100%
- `/ask-v2` stub boot = pass
- legacy semantic hot-path import = 0
- demo tenant Wren schema/mdl smoke = pass
- feature-flag rollback = pass
- legacy `/ask` code change = 0

### STOP-THE-LINE

- V2 bootstrap legacy semantic owner import ederse,
- principal/runtime identity implicit ContextVar'a bırakılırsa,
- Day0 stub query/LLM çalıştırmaya başlarsa,
- baseline vakaları mevcut corpus yerine uydurulursa,
- source lock sırasında legacy refactor açılırsa.

### DAY 0 NOTU

İlk PRE-DAY0 notundaki “Day0 sadece stub” kapsamı **P3 yeniden okununca düzeltildi**.
Roadmap açıkça Source Lock + Baseline ister. Bu düzeltme plan sapması değil, plan authority'sine
geri dönüştür.


## 6. İLERLEME GÜNLÜĞÜ

### 2026-09-20 — PRE-DAY0 / branch bootstrap

**Yapılan**
- `feat/ask-v2-mvp` açıldı.
- Nihai roadmap ve rapor branch'e aktif mühürlü belgeler olarak alındı.
- Her iki mühürlü belgenin kaynak içerikle birebir eşitliği doğrulandı.
- Root `AGENTS.md` ve `backend/AGENTS.md` kuruldu.
- `backend/CLAUDE.md` V2 aktif-operasyon override aldı.
- `backend/MIMARI.md` V2 authority overlay aldı; eski current-state gövdesi korunarak bırakıldı.
- Premature V2 kod iskeleti geri alındı; Day 0 sınırı temizlendi.
- Branch diff'i yalnız hazırlık/authority belgelerinden oluşuyor; executable V2 kodu henüz yok.

**Karar**
- Geliştirme rapor + roadmap çapraz okunarak yapılacak.
- İlerleme mühürlü belgelere değil yalnız bu durum dosyasına yazılacak.
- Büyük testler her küçük değişiklikte değil milestone/demet sonunda çalışacak.

**Sıradaki**
- **Day 0 ticket'ını aç.**
- P0–P2B ile R0–R6'yı tekrar aktif ticket bağlamında çapraz oku.
- V2 island boot/runtime boundary'yi en küçük dikey dilimle uygula.
- Day 0 bitene kadar TurnInterpreter/Resolver gibi Day 1+ capability'lere geçme.

---

## 7. DEĞİŞMEZ DEVİR FORMATI

Bir sonraki geliştirici yalnız şu sırayla devam eder:

1. Bu dosyada **Durum**, **Borç Defteri**, **Sıradaki Ticket** bölümlerini oku.
2. Aktif ticket'ın roadmap P bölümünü oku.
3. Roadmap'in atıf yaptığı report R bölümünü oku.
4. Touch/no-touch listesini yaz.
5. Kodla.
6. Hedefli test/daily demo gerekiyorsa çalıştır.
7. Bu dosyayı commit SHA, sonuç, borç ve sıradaki adımla güncelle.
8. Ancak exit yeşilse sonraki ticket'a geç.


### 2026-09-20 — DAY 0 / implementation batch 1

**Roadmap/Report çaprazı**
- P3 Source Lock + Baseline okundu.
- P2/P2B isolation/touch-no-touch ile R2–R5 reuse-first sınırı çaprazlandı.
- R3/R3A eski hata sınıfları için import-ban + explicit runtime + no-fallback/no-query Day0 sınırı seçildi.

**Yapılan**
- `app/v2/` greenfield package yeniden, bu kez Day0 kapsamıyla kuruldu.
- `TenantAnalyticsRuntimeV0` yalnız principal/tenant + MDL/schema snapshot taşır; semantic yorum yok.
- `POST /ask-v2` eklendi; `query:run` + `require_company` ile mevcut auth/tenant yatırımı reuse edildi.
- `ask_v2_enabled=False` default-off rollback flag eklendi.
- Stub yalnız Wren `schema()` + `mdl_version` okur; query/dry-plan/LLM/legacy semantic path yok.
- 32 mevcut eval case + 5 mevcut experience scenario = 37 unit Day0 baseline manifesti kilitlendi.
- Known silent-wrong envanteri ranking/period/comparison/typo/repair/follow-up/ambiguity aileleriyle manifestte coverage gate'e bağlandı.
- `lab/v2_day0_baseline.py` mevcut `/ask` üzerinden outcome/source/correctness/failure_stage/latency kaydı üretecek şekilde eklendi.
- `tests/test_v2_day0.py` yalnız hedefli Day0 gate'leri içeriyor.
- Bir kerelik `v2-day0-baseline` workflow'u draft PR açılışında baseline JSON artefaktı üretecek; sonraki pushlarda otomatik tekrar etmeyecek.

**Legacy no-touch doğrulaması**
- `app/routers/ask.py`: değişmedi.
- `app/cube_router.py`: değişmedi.
- `app/uyum.py`: değişmedi.
- `app/plan_tuketici.py`: değişmedi.
- `app/plan_semasi.py`: değişmedi.
- `app/wren_service.py`: değişmedi.

**Açık borç**

### V2-D004 — Live-provider Day0 baseline yok
- Kaynak: P3 baseline + P0A hız politikası.
- Mevcut ölçüm: `rule_offline` reproducible before-picture.
- Risk: Intent-LLM/Discovery canlı sağlayıcı davranışı Day0 artefaktında temsil edilmeyecek.
- Blocker: **Day0/Core geliştirme için NO**; pilot/default-ready öncesi YES.
- Neden şimdi değil: API/kota/belirlenimsizlik Day0 hızlı mimari kanıtını bloke etmemeli; mevcut repo da live ölçümü faz-sonu sınıfında tutuyor.
- Kapanış: gerçek sağlayıcıyla aynı source-locked manifest üzerinde ayrı ölçüm + provenance.
- Hedef: pilot hardening.

**Bekleyen ölçüm**
- Draft PR aç → one-shot Day0 workflow.
- Hedefli test + 37-unit baseline artefaktını oku.
- Sonucu ve artefakt özeti bu dosyaya yaz.
- Exit yeşilse Day0 kapat; Day1 TurnInterpreter ticket'ını ancak ondan sonra aç.
