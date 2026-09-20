# DIMA V2 — GELİŞTİRME DURUMU

**Branch:** `feat/ask-v2-mvp`  
**Başlangıç tabanı:** `wren-bağımsız@869280db316d5bf3f76d3253b8b80e5609a000b9`  
**Başlangıç tarihi:** 20 Eylül 2026  
**Durum:** **PRE-DAY0 — GELİŞTİRME PLATFORMU HAZIRLANIYOR**  
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
- [ ] `backend/AGENTS.md` V2 çalışma sözleşmesi eklendi.
- [ ] `backend/CLAUDE.md` V2 aktif-operasyon override ile güncellendi.
- [ ] `backend/MIMARI.md` V2 authority overlay ile güncellendi.
- [ ] Branch diff yalnız hazırlık belgelerini içeriyor doğrulandı.
- [ ] PRE-DAY0 commit durumu son kez kaydedildi.

### Erken başlanıp geri alınan iş

İlk branch açılışında `app/v2/__init__.py` ve `app/v2/models.py` iskeletleri erken
oluşturuldu. Kullanıcı kararıyla Day 0 başlamadan önce geri silindi.

**Neden:** branch/platform hazırlığı ile implementation başlangıcının git tarihinde ayrılması.

**Sonuç:** Day 0 temiz sınırdan başlayacak; bu iki dosyanın tasarımı authority sayılmaz.

---

## 3. ŞU ANKİ BORÇ DEFTERİ

### V2-D001 — Eski MIMARI/CLAUDE operasyon metni V2'yi henüz işaret etmiyor

- Kaynak: P1 / R0.2
- Risk: yeni geliştirici eski “aktif operasyon”a gidebilir.
- Blocker: **YES — Day 0 öncesi**
- Kapanış: MIMARI authority overlay + CLAUDE V2 override + AGENTS kurulumu.
- Hedef: PRE-DAY0.

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

## 6. İLERLEME GÜNLÜĞÜ

### 2026-09-20 — PRE-DAY0 / branch bootstrap

**Yapılan**
- `feat/ask-v2-mvp` açıldı.
- Nihai roadmap ve rapor branch'e aktif mühürlü belgeler olarak alındı.
- Premature V2 kod iskeleti geri alındı; Day 0 sınırı temizlendi.

**Karar**
- Geliştirme rapor + roadmap çapraz okunarak yapılacak.
- İlerleme mühürlü belgelere değil yalnız bu durum dosyasına yazılacak.
- Büyük testler her küçük değişiklikte değil milestone/demet sonunda çalışacak.

**Sıradaki**
- AGENTS/CLAUDE/MIMARI V2 çalışma katmanını tamamla.
- Branch diff'i doğrula.
- Sonra ayrı adım olarak Day 0 ticket'ını aç.

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
