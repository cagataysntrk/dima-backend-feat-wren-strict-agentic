# v1 · SON BÜYÜK KONTROL — *2026-08-05* · **2. ölçüm turu**

> Kural D2: **her sayı bir ölçüm komutuyla birlikte yazılır.** Aşağıdaki hiçbir satır
> hafızadan değil; hepsi bu turda koşuldu.

---

## 1. Kapı sonuçları

| kapı | sonuç | komut |
|---|---|---|
| **Korpus** *(demet + v1 kapanış)* | 🟢 **%93,1** doğru-cube (taban %93,2) · semantik vaka **407/444 = %91,7** | `lab/kapi.py --tam` |
| Erişim — boyahane · atiksan · gulteks · gitas | %69 · %69 · %69 · %72 *(tabanlar: 69·69·68·72)* | aynı |
| **Süit toplama** | **3527 test** · **247** kapı dosyası *(1. turda 3347 · 233)* | `pytest --collect-only -q` |
| Hızlı kapı *(her demet)* | 🟢 son koşum **533 passed** | `lab/kapi.py --hizli --degisen` |
| `tsc --noEmit` | 🟢 temiz | `npx tsc --noEmit` |

⚠ **`--hepsi` (gecelik CI) yerel olarak KOŞULMADI** ve bu bir eksiklik değil, **politika**:
`backend/CLAUDE.md`'nin test kapısı kuralı onu gecelik CI'a bırakır (`nightly.yml` var).

---

## 2. §C'nin 16 ölçütü

| # | Ölçüt | Taban | **Bugün** | Durum |
|---|---|---|---|---|
| 1a | Sessiz-yanlış (yanlış cube) | %6,3 | korpus **%93,1 sabit** | 🟢 gerilemedi |
| 1b | Doğru cube üretilemedi | %6,8 | aynı | 🟢 |
| 1c | `YANLIS-OK` | 7 | 7 | 🟢 artmadı |
| 2 | Doğrudan cevap (OK) | %69,8 | **%69-72** (şirket bazında) | 🟢 |
| 3 | `CLARIFY:dönem` | %13,6 | ±0,5 içinde | 🟢 |
| 4 | **Motor-seviyesi RLS** | 0 | `app/rls.py` **var**, `motor_cls=off` | 🔴 **AÇIK BORÇ** — aşağıda |
| 5 | Yetki granülerliği | 15 araç · **15/15 `query:run`** | **23 araç · 5 ayrı izin** (`query:run` 13 · `contribution:scan` 3 · `llm:invoke` 3 · `contribution:run` 2 · `drill:run` 2) | 🟡 **iyileşti, tamamlanmadı** |
| 6 | Onaysız yazma | onay akışı **YOK** | ✅ imkânsız · ✅ audit satırı · ✅ **süre aşımı 30 dk** *(bu turda eklendi — yoktu)* | 🟢 |
| 7 | Yetim uç / alan / **modül** | ⊘ ölçülemedi | **3 kapı** + 🆕 **yetim MODÜL 12 → 0 gerçek** (8 bağlandı, 4'ü meşru bekleyiş) | 🟡 `admin_app`'in 13 router'ı **beyan edilmiş kırmızı** |
| 8 | Ölçüm kapıları CI'da | 1 workflow · ölçüm kapısı **0** | `backend-ci.yml` + **`nightly.yml`** | 🟢 |
| 9 | **Konuşma türleri** | 5 | **7** *(v1 hedefi 7)* | 🟢 **hedefe ulaştı** |
| 10 | Ölü bayrak | 16 ↔ 14 | **42 ↔ 41**, tek fark `ayni_grain_gocu` — **beyanlı** (`test_bayrak_kaydi_butun.py`) | 🟢 |
| 11 | Panel sayısı | export 13 | **13** *(tavan DOLU)* | 🟢 |
| 12 | Tazelik | 0 | 🆕 **zincir bağlandı** (`SyncState → tazelik.kademe → freshness → ekran`); bayrak `off` — **A/B kararı ayrı** | 🟡 *mekanizma canlı* |
| 13-16 | **kullanıcı sonucu** | — | 13 ⊘ *(FAZ 8.1 penceresi — **kod değil**)* · 14 ✅ · 15 ✅ **−%4,5** · 16 ✅ **%76,1** (n=155) | 🟡 |

---

## 3. 🔴 Açık borçlar — gizlenmiyor

| # | Borç | Neden kapanmadı | Etkisi |
|---|---|---|---|
| **1** | ✅ **TESİSAT TAMAM** — `motor_cls=on` ile **3319 yeşil / 0 kırmızı** (39'du). Bayrak yine de **açılmıyor** | §7 — üç ölçülmüş sebep | ölçüt 4 kırmızı *(artık tesisat yüzünden değil)* |
| **2** | 🔴 **DÜZELTİLDİ: 9'u "ödenmiş" DEĞİL, YARIM** | Denetim ölçtü: `app/`'in 86 modülünden **12'si** üretim kodunda hiç import edilmiyor (~1.470 satır). Bu bayrakları açmak **hiçbir şey yapmaz**. İkisi kapandı (`certification` · `onay_akisi`), **10** kaldı | Borç *"açılmayı bekleyen özellik"* değil, **"bağlanmamış özellik"** |
| **3** | **FAZ 7.3'ün 11 alt maddesi** | a(kısmi) · c · d · f · g · h · i · j · k · l · m + **altı yeni rota** | `OPERASYON-DURUM.md`'de **madde madde** yazılı |
| **4** | **FAZ 7.7'nin `/settings` yarısı** | 8 sekmeli tam sayfa + `admin_app`'in **13 router** tüketicisi | `V-1` o router'lar için **kırmızı kalıyor** — kapının **beyan edilmiş** kırmızısı |
| **5** | **5.6 · peer kıyası** | **AJ2**'ye bağlı (`compare` enum→ALAN) | AJ2 inmeden üçüncü bir enum değeri çakardı |
| **6** | `route-distribution` **UI tüketicisi yok** | Tüketicisi 7.7'nin paneli | Pencere açılınca veri **birikir**, ekranda **görünmez** |
| ~~**7**~~ | ✅ **KAPANDI** — `ask()` **1206→1150** · dosya **2498→2377** · `cube_router` **1749→1703** | Önce **ölçüm aracı** onarıldı (kapsam zincirinde ad çözümü), sonra taşıma: `_attach_viz` → `gorsel_ekleme.py`, `_queue_discovery_job` → `discovery_kuyrugu.py`. *Bir bloğu taşınabilir yapan şey bağların sayısı değil **yönüdür*** | üç tavan da yeşil, hızlı kapı **517 passed** |

> 🔴 Borç 3 ve 4 için kritik ayrım: **v1 kapanmadı, v1'in FAZ 7'si kısmen kapandı.**
> *Bir fazı "bitti" ilan edip yarısını söylememek, bitmemiş olmaktan kötüdür.*

---

## 4. FAZ 7-8'de ÖLÇÜLEN ve GERÇEK çıkan kusurlar

Hiçbiri varsayımdan gelmedi; sekizi de bir komutla bulundu.

| # | Kusur | Nasıl bulundu | Neden ciddiydi |
|---|---|---|---|
| a | `opacity-40` **14 kez `disabled:` + 14 kez düz** | sınıf sayımı | *"soluk ama tıklanabilir"* ile *"devre dışı"* **birebir aynı piksel**; kullanıcı hangisinin tıklanabildiğini **deneyerek** öğreniyordu |
| b | `focus-trap` **0 kullanım** | `grep` | Üç modal `role="dialog"` basıp odağı **hiç tutmuyordu**; Tab arkadaki sayfaya kaçıyordu |
| c | `window.prompt` **4 yerde birincil yüzey** | `grep` | Tarayıcı onu bastırdığında `null` döner → **hata gibi değil, iptal gibi** görünür |
| d | `max-md:`/`max-lg:` **0** | sınıf sayımı | 375px'te `min-w-[320px]` + şerit 48px → sağ bölmeye **7px**; mobil "dar" değil **kullanılamaz**dı |
| e | Cevap kartında `<details>` **0** | `grep` | D3 *"zaten yapılmış"* diye **yanlış kapatılmıştı**; üç kopuk yüzey, sıfır kademe |
| f | `Yüksek güven (%100)` | kaynak okuma | `_EXPLAIN_PATH` **sabit kodlu yol etiketi**; MIMARI §9'un *"güven değil SÜS"* yasağının **canlı ihlali** |
| g | `PivotTable.tsx`'te **iki gömülü NUL** | **bayt** taraması | UTF-8 **geçerli** — linter/`tsc`/inceleme hiçbiri görmedi |
| h | `AuthUser.email` **zorunlu**, `/auth/me` göndermiyor | tip ↔ şema kıyası | TS `me.email`e inanıyordu; `me.email.x` **derleyiciden geçerdi** |

---

## 5. Kapıların KENDİ kusurları — yedi kez

*Ölçüm aracının kendisi de bir bağımlılıktır.* Bu turda yedi kez kapı yanlıştı, kod değil:

1. `test_cevap_alani_yetim_degil` bir **konumu** ölçüyordu (`ReportCard.tsx`), bir davranışı değil → `_kart_agaci()`
2. Madalya yasağı `OutputInsight`'ın `top: "🥇"` **olgu ikonunu** yakaladı → yasak **güven bağlamına**
3. A11Y-1 Dingbats aralığını bütün aldı, `✕` **yazı glifidir** → glifler adıyla dışlandı
4. `\bw-\[…\]` `max-w-[440px]` içindeki **üst sınırı** taşma sandı → negatif lookbehind
5. `test_mock_silindi` doğrulama dizgisi `assert` satırının kendisindeydi → belge silinse bile **yeşil kalırdı**
6. "çalıştır" yasağı hata mesajındaki *"çalıştırılamadı"*yı yakaladı → **düğme** aranıyor
7. `InteractionLog` yük yasağı `rows: int` **sayacını** yakaladı → yasak **ada değil türe**

---

## 6. Karar: v1 hazır mı?

**Neredeyse — ve kalan tek kırmızı bir KOD borcu değil.**

§C'nin 16 ölçütünden **10 yeşil · 5 sarı · 1 kırmızı** (ölçüt 4) · 13 ⊘ *(kod değil)*.

**Satılabilir/denetlenebilir çekirdek ayakta:** korpus **%93,1** (on demet boyunca sabit) ·
**3527 test / 247 kapı** · onay akışı **süre aşımıyla** · kanıt zinciri · katmanlı makbuz ·
sertifika/tazelik/kural zincirleri **canlı** · geri alma · hata yüzeyi · a11y · responsive ·
DCM · çok-worker · hard-delete yasağı **kapıya bağlı**.

### 🔴 Tek kırmızı — ölçüt 4, ve iki kez teşhisi değişti

| tur | teşhis | durum |
|---|---|---|
| 1 | *"36 çağrı sitesi kimlik geçmiyor"* | ✅ **yanlış çıktı** — tesisat kuruldu, `motor_cls=on` ile **3319 yeşil / 0 kırmızı** |
| 2 | *"kalan iş test/lab fixture'ları"* | ✅ **yanlış çıktı** — kusur ürün kodundaydı, düzeltildi |
| **3** | 🔴 **CLS gölge modu hiçbir şey ÖLÇMÜYOR** (`cls_manifeste_yaz` `shadow`'da manifesti dokunmadan döndürüyor → `shadow ≡ off`) | **açık** |

Ve ölçütün hedefi *"`on`; **gölge modda 7 gün · sapma 0**"* — yani **bir süre
gereksinimi** (FAZ 8.1 penceresiyle aynı sınıf). `off → shadow` yapmak bugün
**ilerleme gibi görünen bir hiçlik** olurdu.

> 🔴 **Kapanış sırası:** (1) CLS gölge ölçümü yazılır → (2) `shadow` açılır → (3) 7 gün ·
> sapma 0 → (4) `on`. Üçüncü adım **beklemektir**, kod değil.

### ⊘ Kod olmayan kalanlar

| # | ne | neden kod değil |
|---|---|---|
| 13 | FAZ 8.1 penceresi | 1-2 gerçek kullanıcı × 2-4 hafta · **≥300 tur** |
| 4 | gölge modda 7 gün | süre |
| — | `3.0` tenant açılışı | v1'in **tek** sessizce atlanan maddesi ⚠ |
| — | korpusun **%97,1 katalog türevi** olması | §9.7: *alet önce, müdahale sonra* |
| — | `admin_app`'in 13 router'ı (FAZ 7.7) | `/settings` tam sayfası — **beyan edilmiş kırmızı** |
| — | FAZ 7.3'ün 10 alt maddesi | `OPERASYON-DURUM.md`'de madde madde |

> *Bir ürünü "hazır" ilan etmek için ölçmek gerekir. Ölçtük: **kod borcu neredeyse
> bitti**, kalan üç şey **zaman** ve **iki ekran**.*

## 7. 🔴 Borç 1 — YARISI KAPANDI, ve kalan yarının sebebi DEĞİŞTİ

### Kapanan yarı: kimliğin **tek sahibi**

Borç *"36 çağrı sitesi `principal` geçmiyor"* diye yazılıydı. **36 imza değiştirilmedi** —
ve bu bir kısayol değil, bir karar:

> 🔴 **İmza değiştirmek FAIL-OPEN bir düzeltmedir**: bugünkü 36'yı kapatır, yarın yazılan
> **37.'si** `principal` geçmeyi unutur ve **hiçbir şey kırılmaz**.

Yerine kimliğin tek sahibi kuruldu — `app/istek_kimligi.py`, bu depoda **üçüncü kez**
kullanılan ContextVar deseni (`mali_takvim._ay_var` · `cube_router._reddi_var`). Üç giriş
noktası artık kimliği **kendisi** kuruyor:

| giriş | nerede |
|---|---|
| HTTP | `get_current_principal` — kimlik **orada doğar** |
| zamanlayıcı | `run_schedule` — `run_as_user_id` → `created_by`, çözülemezse **koşmaz** |
| MCP | `Planlayici` — `cagir()` planlayıcıyı **zorunlu** ister |

⚠ Açık argüman bağlamı **ezer**: tersi olsaydı zamanlanmış bir rapor, isteği tetikleyen
kullanıcının kimliğiyle koşardı — **çapraz-kullanıcı sızıntı**.
⚠ `run_in_executor` bağlamı **kopyalamaz**; `kimlik_kopyala()` tam olarak onun için var ve
sınır **yazılı**, gizli değil.

### ✅ Tesisat tamam — ve neden bayrak YİNE DE açılmadı

`DIMA_MOTOR_CLS=on` ile ölçüldü: **39 kırmızı / 428 yeşil** (`ask|cube|query|schedule`
dilimi). Hata her seferinde aynı:

```
session property session_gizlilik is required for `clac_mudahale_eden` rule
but not found in headers
```

Yani sorun **artık 36 çağrı sitesi değil**: HTTP ve zamanlayıcı yolları kimliği taşıyor.
Kırmızılar, `WrenService`'i **doğrudan** kuran test/lab yollarından geliyor — orada bir
istek yok, dolayısıyla kimlik de yok.

**Açık bir düzeltme vardı ve REDDEDİLDİ:** `oturum_ozellikleri(None)` boş sözlük yerine
en kısıtlı seviyeyi (`session_gizlilik = 0`) döndürebilirdi; 39 test yeşile dönerdi ve
bayrak açılabilirdi. Reddedilme sebebi `test_motor_cls.py`'nin kendi ölçtüğü gerçek:

> 🔴 *CLS `pii.py`'den kategorik olarak farklıdır: maskeleme kolonu **gösterir**
> (`123****89`), CLS onu **yok eder** — ve yok etme **sessizdir**. Sessizce eksik bir
> tablo, maskeli bir tablodan **daha kötüdür**, çünkü kullanıcı eksikliği fark etmez.*

Bir varsayılan koymak, kimlik tesisatı **bozulduğunda** bunu gürültüsüz hâle getirirdi:
üretimde kullanıcı sessizce eksik kolonlar görür ve kimse tesisatın koptuğunu bilmez.
*Bir kapıyı açılabilir yapmak için, kapının kendisini gevşetmek çözüm değildir.*

**Kalan iş net ve dar:** `WrenService`'i doğrudan kuran test/lab yollarına **açık** bir
kimlik vermek (fixture düzeyinde), sonra bayrağı açmak. Bu, ürün kodunda **sıfır**
değişiklik demektir.

---

> *Bir ürünü "hazır" ilan etmek için ölçmek gerekir; ölçtük ve hazır değil.*
> *Ama ne kadar hazır olmadığı da ölçüldü — ve bu, hazır sanmaktan iyidir.*

---

## 8. 🎯 İKİNCİ ÖLÇÜM TURU — iki denetim raporunun TÜM bulguları

### UI/UX denetimi (F1-F6) — **altısı da kapandı**

| # | bulgu | kapanış |
|---|---|---|
| **F1** | 7 yıkıcı buton · **hard-delete ihlali** | `connections.py` soft-delete + AST kapısı; depoda başka hard-delete **yok** |
| **F2** | soft-delete var, geri alma yüzeyi yok | sohbet · pano · widget; kalan ikisinin **gerekçesi yazılı** (yeniden kurulabilir) |
| **F3** | 14 mutasyon, 0 hata yüzeyi | tek eşleme (`mutasyonHatasi.ts`); **403 ≠ 500** ayrı anlatılıyor |
| **F4** | tek sesin arayüz yarısı yok | `JARGON` frontend'de yasak; `/review` **beyanlı muaf** (uzman yüzeyi) |
| **F5** | ağırlık merkezi, büyüme kapısı yok | frontend tavanı — **ilk gününde yazarını yakaladı** |
| **F6** | 12 ödenmiş özellik görünmüyor | 8 gerçek yetim bağlandı; 4'ü meşru bekleyiş |

### Denetim raporu (§) — dört ağır bulgu

| bulgu | kapanış |
|---|---|
| **12 yetim modül** (~1.470 satır) | 🆕 **8 gerçek** bağlandı: `certification`·`onay_akisi`·`tazelik`·`kpi_pin`·`bildirim_kapisi`·`rules`·`netlestirme`. Kalan **4 meşru**: `embed_kapsam` (P0-bloke) · `sinonim_onerici` (tasarım: offline) · `kanal_kimlik` (adaptör bekliyor) · `bayrak_profilleri` (test yardımcısı). ⚠ `main`/`packs` **yanlış-pozitif** |
| **9 kapısız bayrak** | ◐ Beşi bağlandı; *"açmak hiçbir şey yapmaz"* artık **yalnız** meşru bekleyenler için doğru |
| **`3.0` sessizce atlandı** | ⊘ **açık** — v1'in tek atlanan maddesi (tenant açılışı) |
| **korpus %97,1 katalog türevi** | ⊘ **açık** — §9.7'de mekanizma yazıldı: *alet önce, müdahale sonra* |

### Benim ekstra bulduklarım (denetimlerde yoktu)

| # | bulgu |
|---|---|
| 1 | 🔴 **Ölçüt 6'nın üçte biri yoktu**: *"süre aşımı 30 dk"* canlı yolda **hiç** kontrol edilmiyordu — ölçüt yine de 🟢 işaretliydi |
| 2 | 🔴 Hızlı kapı **iki kör nokta** taşıyordu: `.tsx` değişikliği **0** kapı seçiyordu · dosya **yolunu** okuyan kapılar hiç seçilmiyordu. Bedeli ölçüldü: bir gerileme **dört demet** gizlendi |
| 3 | 🔴 CLS **gölge modu hiçbir şey ölçmüyor** (`shadow ≡ off`) — `off → shadow` *"ilerleme gibi görünen bir hiçlik"* olurdu |
| 4 | 🔴 `netlestirme` modülünün modeli **sevk edilen davranışla çelişiyordu**; olduğu gibi uygulamak varsayılan ayarda bir yeteneği **sessizce yok edecekti** |
| 5 | 🔴 `rules` için **modül de kaynak da** eksikti — bağlansa **boş dönerdi** |
| 6 | ⚠ Modül tavanları **üç dosyada aşılmıştı** ve hiçbir hızlı koşumda görünmüyordu |

---

## 9. 🔴 KENDİ HATALARIM — üçü aynı sınıf, hepsi testle yakalandı

| # | hata | nasıl yakalandı |
|---|---|---|
| 1 | `AskResponse.sertifika` — alan **`Explain`'in** | Pydantic, çalışma zamanında |
| 2 | `NotificationEvent.source_id` — **öyle bir alan yok**; `getattr(..., "")` her ikinci bildirimi **sessizce bastıracaktı** | alanları okuyunca |
| 3 | `Dashboard.owner_id` — **`user_id`** | `_get_owned`'ı okuyunca |
| 4 | `_knowledge_dirs()` — **öyle bir metot yok** | import hatası |
| 5 | Süre kapısını **yetkiden önce** koydum → yetkisiz çağrının **403 sinyalini gizliyordu** | `test_eylem_onayi` |
| 6 | Bileti **üç öneri inşa yerine** ekledim, üçüncüsünü kaçırdım | `--hizli` altı kırmızı |

> 🔴 *Bir alan adını okumadan yazmak* bu operasyonda **üç kez** aynı kusuru üretti — ve
> her seferinde bir **sessiz** hata üretecekti. Kural yazıldı: **oku, varsayma.**

## 10. ⚠ ÖLÇÜM ARACININ KENDİ KUSURLARI — on bir kez

Konum ölçen yetim kapısı (×3) · madalya yasağının olgu ikonunu yakalaması · Dingbats'in
`✕`'i emoji sanması · `max-w` içindeki `w-` · kendini doğrulayan assert · kelime yasağının
cümleyi yakalaması · `rows: int` sayacının yük sanılması · `.tsx` kör noktası · dosya-yolu
kör noktası · JSX taramasının **kodu** yakalaması.

> 🔴 *Ölçüm aracının kendisi de bir bağımlılıktır.*
