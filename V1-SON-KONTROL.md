# v1 · SON BÜYÜK KONTROL — *2026-08-05*

> Kural D2: **her sayı bir ölçüm komutuyla birlikte yazılır.** Aşağıdaki hiçbir satır
> hafızadan değil; hepsi bu turda koşuldu.

---

## 1. Kapı sonuçları

| kapı | sonuç | komut |
|---|---|---|
| **Korpus** *(demet + v1 kapanış)* | 🟢 **%93,1** doğru-cube (taban %93,2) · semantik vaka **407/444 = %91,7** | `lab/kapi.py --tam` |
| Erişim — boyahane · atiksan · gulteks · gitas | %69 · %69 · %69 · %72 *(tabanlar: 69·69·68·72)* | aynı |
| **Süit toplama** | **3347 test** · 233 dosya | `pytest --collect-only -q` |
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
| 6 | Onaysız yazma | onay akışı **YOK** | `onay_akisi` + `test_onay_akisi.py` (22) | 🟢 |
| 7 | Yetim uç / alan | ⊘ ölçülemedi | **3 kapı** (`uc_yetim` · `cevap_alani_yetim` · `ters_yetim`) | 🟡 `admin_app`'in 13 router'ı **beyan edilmiş kırmızı** |
| 8 | Ölçüm kapıları CI'da | 1 workflow · ölçüm kapısı **0** | `backend-ci.yml` + **`nightly.yml`** | 🟢 |
| 9 | **Konuşma türleri** | 5 | **7** *(v1 hedefi 7)* | 🟢 **hedefe ulaştı** |
| 10 | Ölü bayrak | 16 ↔ 14 | **42 ↔ 41**, tek fark `ayni_grain_gocu` — **beyanlı** (`test_bayrak_kaydi_butun.py`) | 🟢 |
| 11 | Panel sayısı | export 13 | **13** *(tavan DOLU)* | 🟢 |
| 12 | Tazelik | 0 | `test_tazelik.py` var, bayrak **`off`** | 🟡 |
| 13-16 | **kullanıcı sonucu** | — | 13 ⊘ *(FAZ 8.1 penceresi — **kod değil**)* · 14 ✅ · 15 ✅ **−%4,5** · 16 ✅ **%76,1** (n=155) | 🟡 |

---

## 3. 🔴 Açık borçlar — gizlenmiyor

| # | Borç | Neden kapanmadı | Etkisi |
|---|---|---|---|
| **1** | **36 çağrı sitesi `principal` geçmiyor** | Kimlik taşımayan bir çağrı, RLS'i **sessizce** atlar | `motor_cls=on` **kilitli** → ölçüt 4 kırmızı, `6.5/embed` bloke |
| **2** | **26 bayrak `off`** | Ödenmiş, testli, kullanıcıya **kapalı**. Üçü FAZ 1'in ana teslimatı (`tazelik` · `lineage` · `metrik_sertifikasi`) | Ölçüt 12 sarı; *bedeli ödenmiş ama teslim edilmemiş* yetenek |
| **3** | **FAZ 7.3'ün 11 alt maddesi** | a(kısmi) · c · d · f · g · h · i · j · k · l · m + **altı yeni rota** | `OPERASYON-DURUM.md`'de **madde madde** yazılı |
| **4** | **FAZ 7.7'nin `/settings` yarısı** | 8 sekmeli tam sayfa + `admin_app`'in **13 router** tüketicisi | `V-1` o router'lar için **kırmızı kalıyor** — kapının **beyan edilmiş** kırmızısı |
| **5** | **5.6 · peer kıyası** | **AJ2**'ye bağlı (`compare` enum→ALAN) | AJ2 inmeden üçüncü bir enum değeri çakardı |
| **6** | `route-distribution` **UI tüketicisi yok** | Tüketicisi 7.7'nin paneli | Pencere açılınca veri **birikir**, ekranda **görünmez** |

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

**Hayır — ve bunu bir sayıyla söyleyebiliyoruz.** §C'nin 16 ölçütünden **9'u yeşil**,
**5'i sarı**, **1'i kırmızı** (ölçüt 4), 13 ⊘ *(kod değil)*.

**Satılabilir/denetlenebilir çekirdek ayakta:** korpus %93,1 sabit · 3347 test · onay akışı ·
kanıt zinciri · katmanlı makbuz · a11y · responsive · DCM · çok-worker.

**Kapanması gereken tek kırmızı:** ölçüt 4 — ve o, **borç 1'e** (36 çağrı sitesi) bağlı.
Onun ardından borç 3-4 (FAZ 7.3/7.7'nin kalanı) v1'in **arayüz yüzeyini** tamamlar.

> *Bir ürünü "hazır" ilan etmek için ölçmek gerekir; ölçtük ve hazır değil.*
> *Ama ne kadar hazır olmadığı da ölçüldü — ve bu, hazır sanmaktan iyidir.*
