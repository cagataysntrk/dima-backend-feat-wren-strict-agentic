# UI/UX YENİDEN YAPILANDIRMA — faz planı ve karar belgesi

> **Kesit:** 2026-08-05 · `@9b2410e` · **Durum:** kararlar alındı, uygulama sırada
> **Girdiler:** 269 işlevlik envanter denetimi · 29 benimse / 25 kaçın araştırma kararı ·
> ölçülmüş tavanlar (**hepsi sıfır paylı**)
>
> ⚠ Bu bir tartışma belgesi değil. Her satır bir **karar**, her kararın bir **ölçüsü**,
> her fazın bir **kapısı** ve bir **geri alma yolu** var.

---

# BÖLÜM A · BAĞLAYICI KISITLAR

Plan bunlardan doğdu; bunlar değişmeden plan değişmez.

| # | kısıt | ölçüm | plana etkisi |
|---|---|---|---|
| **K1** | **Panel tavanı 13/13** | `test_panel_sayisi.py` · `TAVAN = 13` | 🔴 Yeni `export …Panel` **yasak**. Sol çubuk beş çekmeceyi **birleştirir** → panel sayısı **düşer** |
| **K2** | **`page.tsx` payı 0** (534/534) | `test_frontend_buyume.py` | 🔴 Düzen `page.tsx`'ten **çıkarılır**; dosya **küçülür** |
| **K3** | **269 işlev · 25'i tek girişli** | envanter denetimi | 🔴 Erişilebilirlik kapısı **koda dokunmadan önce** yazılır |
| **K4** | `ReportCard` payı 0 (1011/948) | `test_frontend_buyume.py` | 🔴 Grafik makinesi panele **taşınır** → kart **incelir** |
| **K5** | Bayrak tekliği | `test_ui_bayrak_tekligi.py` | Yeni bayrak sistemi **yok**; her `useFeature` adı kayıtta olmalı |
| **K6** | A11Y-4: `window.prompt` yasak | `test_a11y.py` | Yeni yüzeylerde `prompt` **yok**; `useAdSor` kullanılır |

> 🔴 **Altın kural:** *Her faz eklediğinden fazlasını kaldırmalı.* Bu bir yetenek ekleme
> işi değil, bir **sadeleştirme** işi.

---

# BÖLÜM B · KARARLAR

## B.1 · Düzen

```
┌────────┬──────────────────────────┬────────────────┐
│ ÇUBUK  │  SOHBET (asıl unsur)     │ ANALİZ PANELİ  │
│ 256px  │  maks 720px · 16px/1.6   │ 400/480/55vw   │
│ ─ ray ─│                          │ (istenince)    │
│  56px  │  ① cümle + sayı          │ grafik + TÜM   │
│  ✏ ara │  ② temiz grafik          │ makine         │
│  geçmiş│    (kontrolsüz)          │ ‹ 3/5 ›        │
└────────┴──────────────────────────┴────────────────┘
```

### Sol çubuk

| karar | değer | gerekçe |
|---|---|---|
| genişlik | **256px** açık · **56px** ray | 240px altında etiket kırpılır; 48px'te 40px dokunma hedefi sıkışır |
| kapalı hâl | 🔴 **kalıcı ray** · hover-flyout **YASAK** | ölçülmüş kusur: imleç hedefe varmadan flyout kapanıyor, kullanıcı *"listeye bakmak"* yerine **avlanıyor** |
| rayda görünen | **✏ yeni sohbet** (üstte) · ara · geçmiş | ≥40px dokunma hedefi |
| kısayol | **`Ctrl/Cmd+B`** · ⚠ composer odaktayken **devre dışı** | `Ctrl+B` = bold; çakışma ölçülmüş bir kusur |
| keşfedilebilirlik | rayda **görünür** aç/kapa + tooltip'te kısayol | *görünmez bir durum, olmayan bir özelliktir* |
| kalıcılık | **cookie** `sidebar_state` — localStorage **değil** | SSR ilk boyamada okunur → genişlik **zıplamaz** |
| ilk açılış | ≥1440px **açık** · altında **ray** | |
| geçmiş | Bugün / Dün / Son 7 gün / Son 30 gün → **"Ocak 2026"** | göreli yakın, mutlak uzak |
| sıralama | 🔴 **`updated_at`** | `created_at` olsa, bugün devam ettiğin eski sohbet **dibinde** kalır |
| başlık | ilk kullanıcı sorusu · asla *"Yeni sohbet"* | tanıma, hatırlama değil |

### Sohbet (merkez)

| karar | değer |
|---|---|
| içerik genişliği | **maks 720px** (~68 karakter) |
| gövde | **16px / 1.6** · **orantılı** yazı tipi |
| mono | 🔴 yalnız **sayı · SQL · kod · tablo hücresi** |
| yoğunluk | **comfortable** |
| balon | 🔴 **YOK** — tam genişlik blok (balon = *"gündelik mesajlaşma"* sinyali) |

### Analiz paneli

| karar | değer | gerekçe |
|---|---|---|
| genişlik | min **400** · varsayılan **480** · maks **%55vw** · **sürüklenebilir** | alt sınırsız yeniden boyutlandırma ölçülmüş kusur: *"metin okunamaz hâle geliyor"* |
| sohbet alt sınırı | **520px** — altında panel **açılmaz** | okunabilirlik tabanı |
| davranış | 🔴 **reflow** — overlay **DEĞİL** | overlay = modal; *"hem bak hem yaz"* vaadini iptal eder |
| tam genişlik modu | 🔴 **YOK** | sohbeti gizler, bağlam kaybolur |
| rol | 🔴 **`role="complementary"`** — `dialog` **DEĞİL** | dialog rolü ekran okuyucuya *"bu bir kesinti"* der |
| odak | açılışta **taşınmaz** (klavyeyle açıldıysa başlığa) · kapanışta **açan düğmeye döner** | kullanıcı yazıyor olabilir |
| focus trap · `inert` · `aria-modal` | 🔴 **YOK** | üçü de paneli modale çevirir |
| Escape | yalnız **odak panel içindeyken** | composer'da yazarken kapanması vaadi kırar |
| ayırıcı | `role="separator"` · `tabindex=0` · `aria-valuenow` · ok/Home/End | klavyesiz bırakmak yaygın hata |
| çoklu analiz | başlıkta **`‹ 3/5 ›`** — sekme şeridi **değil** | 5 analizden sonra şerit taşar |

### Duyarlı davranış

| genişlik | çubuk | sohbet | panel |
|---|---|---|---|
| ≥1600px | 256 | ≥560 | 480 |
| 1280–1599 | 🔴 **otomatik raya düşer** (geçici, pini ezmez) | ≥560 | 440–520 |
| <1280 | 56 | tam | **tam ekran katman** |

## B.2 · 🔴 GRAFİK KARARI — *grafiği makinesinden ayır*

Kullanıcının itirazı ölçümle doğrulandı: bir rapor kartında **~59 katman/işlem** var —
başlıkta 20 düğme, altında `InterpretationBar`'ın 15 kontrolü, drill · katkı · reçete ·
öneri çipleri · sonraki-adım çipleri · dışa aktarma menüsü.

> 🔴 Grafiği *"olduğu gibi"* sohbete koymak, grafiği değil **bütün makinesini** sohbete
> koymaktır. Sohbet o zaman gerçekten boğulur.

Ama çözüm grafiği küçültmek de değil — *okunamayan bir thumbnail, sıfır bilgi taşıyan
ekstra bir etkileşim maliyetidir.* **Doğru ayrım şudur:**

| | **sohbette (inline)** | **panelde** |
|---|---|---|
| ne var | cevap cümlesi + sayı + **temiz grafik** | **aynı grafik, büyük** + tüm makine |
| kontroller | 🔴 **hiçbiri** — bir tek *"panelde aç"* | tip · ölçü · grafik/tablo/pivot · dışa aktar · drill · katkı · reçete · çipler · yorum çubuğu |
| rolü | **okunur** | **çalışılır** |

**Katmanlı cevap:**
```
① cevap cümlesi + sayı          ← HER ZAMAN · asıl unsur
② temiz grafik (kontrolsüz)     ← HER ZAMAN · cevaptan SONRA · min 200px
③ tablo · SQL · köken · drill   ← PANELDE · istenince
```

**Yerleşim eşiği**

| durum | yer |
|---|---|
| tek sayı / KPI / 1 cümlelik cevap | yalnız metin — **grafik yok** |
| ≤8 nokta, tek seri | **inline**, tam boy |
| 8–50 nokta veya 2–3 seri | **inline** + *"panelde aç"* |
| >50 satır · pivot · **kök-neden dalışı** | **panel** |
| iki analizi **karşılaştırma** | **panel** — inline bunu yapamaz |
| kullanıcı **yazarken bakmak** istiyor | **panel** |

⚠ **Kök-neden şeması ve drill panelin işidir** — onlar bir **çalışma tezgâhı**
faaliyetidir, okuma faaliyeti değil. Bugün kartın altında açılıp kartı metrelerce
uzatıyorlar; panele taşınınca sohbet gerçekten akar.

🔴 **Modal — tam üç yerde:** silme onayı · yıkıcı kaynak kaldırma · oturum/yetki
kesintisi. **Analiz gösterimi için asla.**

## B.3 · Görsel dil — ölçülmüş kusurun karşılığı

| bugün (ölçüldü) | karar |
|---|---|
| **188× 11px · 121× 10px · 6× 9px**, yalnız **3× 15px** | sohbet **16px/1.6** · panel **14px/1.45** · meta **12.5px** |
| **387× `font-mono`** | mono **yalnız** sayı/SQL/kod/tablo hücresi |
| **222 çizgi ↔ 17 gölge** | **4 yüzey seviyesi**, derinlik **parlaklıkla**; 1px kenarlık birincil, gölge yalnız **gerçekten yüzende** |
| yarıçap **maks 4px**, 7 kullanım | panel/kart **12** · düğme/girdi **8** · çip **6** |
| tek `#ffffff` zemin | `--surface-1..4` · nötr rampa **slate/zinc** |
| koyu tema | zemin **`#0F1115`–`#16181D`** · metin **`#E6E8EB`** · 🔴 saf `#000` / saf `#FFF` metin **yasak** (halation) |
| — | 8pt ızgara · geçiş **200ms `cubic-bezier(0.2,0,0,1)`** · `prefers-reduced-motion`'da transform kapalı, 100ms opaklık |

⚠ **İki yoğunluk kasıtlıdır:** sohbet *comfortable*, panel *compact* (40px satır).
Tutarsızlık değil, **bağlam farkı**.

---

# BÖLÜM C · FAZLAR

## Her fazın değişmez kuralları

| kural | ne |
|---|---|
| **C-1** | Faz **tek başına çalışır** hâlde biter — yarım bırakılmış faz commit edilmez |
| **C-2** | Faz sonunda **tek commit**; mesajda *ne değişti · neden · hangi ölçüm* |
| **C-3** | Faz kapısı **yeşil** olmadan sonraki faza geçilmez |
| **C-4** | Belirteçler **eklenir**, mevcut değer **değiştirilmez** (deponun göç usulü) |
| **C-5** | Bir işlev taşınırken **eski yeri silinmeden** yenisi çalışır hâle gelir; silme **aynı fazın sonunda** |
| **C-6** | Geri alma: her faz **tek `git revert`** ile geri alınabilir |
| **C-7** | 🔴 Kapı koşarken **repoya yazılmaz** |

---

## FAZ 0 · ERİŞİLEBİLİRLİK KAPISI — *koda dokunmadan önce*

**Neden ilk:** 25 işlev tek girişli. Taşıma sırasında biri düşerse, **hiçbir test
kırmızı vermez** ve kimse ne zaman kaybolduğunu bilemez.

> *Taşınmayan bir özellik silinmiş bir özelliktir — ve bunu yakalayan tek şey,
> taşımadan önce yazılmış bir kapıdır.*

### Adımlar
1. `backend/tests/test_ui_erisim.py` yaz.
2. İçine **25 tek-girişli işlevin** her biri için bir **erişilebilirlik iddiası**:
   bileşen bir yerden **import ediliyor ve render ediliyor** mu; etiket metni kodda
   duruyor mu.
3. **13 panelin** her biri için aynı iddia.
4. 🔴 **En sinsi dördü ayrı ayrı adlandırılır** (rail'de **değiller**, `layout.tsx`'te):
   tema anahtarı · çıkış · bağlantı rozeti · kimlik şeridi.
5. **Zaten kırık üçü** `BEKLENEN_KIRIK` listesine **gerekçesiyle** yazılır —
   ⚠ *bir kusuru kapıya "geçti" diye yazmak, onu kapatmakla aynı görünür ama
   kapatmaz.* Liste ayrı tutulur ki düzeltilince kapı **kendiliğinden** sıkılaşsın.

### Kapı
`pytest tests/test_ui_erisim.py` → **yeşil** (bugünkü hâliyle, hiçbir şey değişmeden).
⚠ Kapı **bugün** yeşil vermiyorsa, iddiası yanlıştır — **kapıyı** düzelt, kodu değil.

### Geri alma
Yalnız test dosyası eklenir; ürün kodu değişmez → risk **sıfır**.

---

## FAZ 1 · GÖRSEL BELİRTEÇLER — *eklenir, hiçbir şey değişmez*

**Neden ikinci:** sonraki her faz bu belirteçleri kullanacak. Önce sözlük, sonra cümle.

### Adımlar
1. `globals.css`'e **ekle** (mevcut hiçbir değeri **değiştirme**):
   - `--surface-1..4` (açık + koyu tema)
   - `--radius-lg: 12px` · `--radius-md: 8px` *(mevcut 4px `--radius-sm` kalır)* · `--radius-xs: 6px`
   - `--text-body: 16px` · `--lh-body: 1.6` · `--text-panel: 14px` · `--text-meta: 12.5px`
   - `--measure: 68ch` · `--motion-md: 200ms` · `--ease-standard: cubic-bezier(0.2,0,0,1)`
   - koyu tema zemini `#0F1115`–`#16181D` bandına **taşınır** *(saf siyaha asla)*
2. `prefers-reduced-motion` bloğu: transform kapalı, 100ms opaklık.

### Kapı
`test_ui_gorsel_dil.py` — belirteçlerin **varlığı** + saf `#000`/`#fff` metin **yokluğu**.
⚠ Bu fazda **hiçbir bileşen değişmez** → görsel çıktı **birebir aynı** kalmalı.

### Geri alma
`globals.css` tek dosya · tek revert.

---

## FAZ 2 · SOL ÇUBUK — *beş çekmece → bir çubuk*

**Neden üçüncü:** kullanıcının belirlediği sıra ("önce sol").

### Adımlar
1. `src/components/YanCubuk.tsx` **oluştur** — 🔴 adı `…Panel` **değil** (K1).
2. İçine taşı: **✏ yeni sohbet** · **ara** · **geçmiş** (gruplu, `updated_at` sıralı) ·
   **tema anahtarı** · **kimlik şeridi** · **bağlantı rozeti** · **çıkış** ·
   ayarlar girişleri (şema · veri kaynağı · zamanlamalar · tercihler) · panolar ·
   bildirimler · yardım · ölçü inceleme.
3. Ray davranışı: 56px · üç ikon görünür · aç/kapa düğmesi + tooltip.
4. `Ctrl/Cmd+B` — composer odaktayken **devre dışı**.
5. Cookie `sidebar_state`; ≥1440px açık.
6. `page.tsx`'ten `FloatingControls` + `SettingsDrawer` çağrılarını **kaldır**;
   `layout.tsx`'ten dört sabit ögeyi **kaldır** *(çubuğa taşındıktan sonra)*.
7. 🔴 Panel sayısı **düşmeli**: `HistoryPanel` · `HelpPanel` · `NotificationsPanel` ·
   `DashboardsPanel` · `TercihlerPanel` çubuğun içine **bölüm** olarak girer,
   ayrı `export …Panel` olmaktan **çıkar**.

### Kapı
- `test_ui_erisim.py` **yeşil** (FAZ 0'da yazıldı — hiçbir işlev düşmemiş olmalı)
- `test_panel_sayisi.py` → panel sayısı **≤13**, hedef **10**
- `test_frontend_buyume.py` → `page.tsx` **küçülmüş** olmalı
- `test_a11y.py` yeşil

### Geri alma
`YanCubuk.tsx` silinir, `FloatingControls`/`SettingsDrawer` çağrıları geri gelir.

---

## FAZ 3 · SOHBET MERKEZE — *düzen `page.tsx`'ten çıkar*

### Adımlar
1. `src/components/Duzen.tsx` oluştur — üç sütunlu kabuk (çubuk · sohbet · panel yuvası).
2. `page.tsx`'ten düzen JSX'ini **buraya taşı**; `page.tsx` yalnız **durum ve veri**
   yönetir (K2 → dosya **küçülür**).
3. Sohbet sütunu: **maks 720px**, ortalanmış, `16px/1.6`.
4. Tek komposer — 🔴 **asimetri kapanır**: `kapsam` · `yol sınırı` · `hızlı/derin` ·
   `📎 yükleme` artık **takip sorusunda da** var.
5. Dar ekran sekme çubuğu korunur (<1024px).

### Kapı
- `test_ui_erisim.py` yeşil
- `test_frontend_buyume.py` → `page.tsx` payı **pozitif**
- Genişlik/tipografi testi: sohbet sütunu ≤720px, gövde ≥15px

---

## FAZ 4 · ANALİZ PANELİ — *grafiği makinesinden ayır*

**Bu fazın kalbi B.2.**

### Adımlar
1. `src/components/AnalizPaneli.tsx` oluştur — 🔴 `…Panel` **değil** (K1).
   `role="complementary"` · `aria-labelledby` · focus trap **yok**.
2. Sürüklenebilir ayırıcı: `role="separator"` · `tabindex=0` · `aria-valuenow` ·
   ok/Home/End · min 400 / varsayılan 480 / maks %55vw.
3. `ReportCard`'dan **panele taşı**: tip seçici · ölçü seçici · grafik/tablo/pivot ·
   dışa aktarma · `InterpretationBar` · `DrillDownPanel` · `ContributionLayer` ·
   `PrescriptionLayer` · makbuz katman 3.
4. `ReportCard` **sohbette** kalanı: cevap cümlesi + sayı + **temiz grafik** +
   *"panelde aç"* + öneri çipleri *(en fazla 3)*.
5. Çoklu analiz: panel başlığında `‹ 3/5 ›`.
6. Escape yalnız odak panel içindeyken; kapanışta odak **açan düğmeye**.

### Kapı
- `test_ui_erisim.py` yeşil — **taşınan her kontrol hâlâ erişilebilir**
- `test_frontend_buyume.py` → `ReportCard` **küçülmüş**
- Panel rolü/odak testi: `role="complementary"` var, `aria-modal` **yok**,
  focus trap **yok**
- `test_panel_sayisi.py` ≤13

---

## FAZ 4B · 🌳 KÖK-NEDEN HARİTASI — *sayıda boğulma, ilişkiye tıkla*

> **Bugünkü kusur (kullanıcının kendi ifadesi):** *"çok karışık, kullanıcılar kolay kolay
> anlamıyor çözemiyor."* `DrillDownPanel` bir **tablo yığını**: hangi yolun bakmaya
> değer olduğunu söylemiyor, kullanıcı sayıların içinde kayboluyor.

### 🔴 TASARIM KARARI: şema **panelde**, vaka kaydı **sohbette**

⚠ Kullanıcı *"cevabın altında açılsın"* dedi. **Panelde açıyorum** ve gerekçesi
kullanıcının **kendi** şikâyeti:

| gerekçe | |
|---|---|
| *"altına doğru açılıyor, boğuluyor"* | ağaç sohbette açılırsa kartı yine metrelerce uzatır — şikâyet edilen şeyin ta kendisi |
| ağaç **genişlik** ister | sohbet sütunu 720px'e kapalı; panel sürüklenerek **%55vw**'ye açılır |
| *"not alırken bakabilmeli"* | panel açıkken sohbet görünür kalır — zaten panelin varlık sebebi |
| *"modal olmasın"* | ✅ **panel modal değildir** — şart karşılanıyor |

**Araştırma tezgâhta yapılır, sonucu konuşmaya yazılır.**

### D.1 · Düğüm = bir **hipotez**, veri yığını değil

Her düğüm bir **aday açıklama**: *"fire artışı **makine** kırılımında mı?"*
Düğümün **görsel ağırlığı = veriden gelen sinyal** — ve bu, kullanıcı **tıklamadan
önce** hesaplanıp gösterilir.

| durum | görünüm | anlamı |
|---|---|---|
| **kanıtlı** | koyu · dolu · kalın kenar | veri **var**, sinyal eşiğin **üstünde** |
| **zayıf** | orta ton | veri var, sinyal **düşük** |
| **⊘ ölçülemedi** | silik · **kesikli** kenar | boyut var ama veri **yok** / taranmadı |
| **kapsam dışı** | hayalet (en silik) | cube bu boyutu **taşımıyor** |

> 🔴 **Silik düğümler bu tasarımın en dürüst parçasıdır.** *Yalnız bulduğunu gösteren
> bir ağaç, bakmadığını gizler.* Bu, deponun kendi **⊘ ÖLÇÜLEMEDİ** üçüncü hâlinin
> görsel karşılığı: ölçülemeyen paydadan çıkar ama **sayılır ve görünür**.

⚠ **Silik ≠ kapalı.** Hiçbir düğüm **devre dışı bırakılmaz**, yalnız önceliksizleşir —
çünkü bazen **verinin yokluğu bulgunun kendisidir** (*"o vardiyada hiç kayıt yok"*).

### D.2 · 🔴 BOĞULMAMA KURALI — *yol + bir kat*

Her an ekranda **yalnız iki şey** olur:
1. **kat edilen yol** (kök → dal → dal) — daima görünür, geri dönülebilir
2. **açık olan tek kat** — kardeş dallar **katlanır**

*Bir ağaç, tüm dallarını aynı anda gösterdiğinde ağaç olmaktan çıkar, yığın olur.*

Her genişletme adımı **kendi küçük grafiğini** üretir — çıplak tablo **asla**.
⚠ Tablo yalnız *"ham satırları göster"* dendiğinde açılır.

### D.3 · Grafik tıklaması = bir drill adımı (**ayrı mekanizma değil**)

Kullanıcı bir grafikte **düşük** bir noktaya tıklar → o nokta **filtreli bir düğüme**
dönüşür ve **aynı ağaçta** dallanır.

🔴 Bugünkü kısıt kalkar: `ResultView` bugün facet/scatter/ısı haritasında tıklamayı
**kapatıyor**. Yeni kuralda **her grafik türü** giriş noktasıdır — çizgi · sütun ·
pasta · ısı · serpme · panelli.

*İki giriş noktası, tek model:* ağaçtan tıkla ya da grafikten tıkla — ikisi de aynı
düğüm ağacını büyütür.

### D.4 · Not = **kökeniyle** kaydedilir

Kullanıcı **herhangi bir düğümde** not alabilir. Not sohbete kaydedilirken **yolun
kendisi de** kaydedilir — kart, mini bir yol diyagramı gösterir:

```
fire ↑ ── makine: RAM-2 ── vardiya: Gece ── ✎ "kalibrasyon şüphesi"
```

> 🔴 *Bir not, kökeni olmadan bir kanaattir.* Bu deponun makbuz kültürünün birebir
> karşılığı: yol kaydedilmezse not yeniden üretilemez, doğrulanamaz, tartışılamaz.

Sohbetteki kayıt bir **vaka kaydı**dır: tek başına okunabilir, tıklanınca **aynı
düğümde** araştırma yeniden açılır.

### D.5 · Responsive-first — ağaç küçük ekranda **ağaç değildir**

| genişlik | izdüşüm |
|---|---|
| ≥1280px | **yatay ağaç** (kök solda → dallar sağa), yol üstte |
| 768–1279 | **dikey ağaç**, yol yukarıda |
| <768px | 🔴 **yol = kaydırılabilir çip şeridi** + **açık kat = kart listesi** |

375px'lik bir ekranda ağaç çizmek okunamaz. Aynı veri, **farklı izdüşüm** — ve yol
her üç izdüşümde de daima görünür.

### D.6 · 🔴 AJANİK OLMAYA HAZIR — *asıl uzun vadeli kazanç*

İnsanın tıklayarak verdiği karar (*"hangi boyutta dallanayım"*) ile bir ajanın vereceği
karar **aynı karardır**. O yüzden düğüm **şeması** ve **puanlama** arayüzde değil,
**backend sözleşmesinde** tanımlanır:

```
dugum: { boyut, deger?, olcu, sinyal, durum, cocuklar[], makbuz }
```

- `sinyal` — dallanmanın **değerini** veren skor (varyans/katkı); **arayüz onu
  hesaplamaz, gösterir**
- `durum` — `kanitli | zayif | olculemedi | kapsam_disi`
- `makbuz` — her düğüm kendi kanıtını taşır *(bu depoda kanıtsız sayı yayımlanmaz)*

⚠ **Bu ayrım şart:** puanlama arayüzde kalırsa, ajan aynı araştırmayı yapamaz —
frontend'e gömülü bir mantık **çağrılamaz**. Böylece ileride *"kök neden analizi yap"*
denildiğinde ajan **aynı ağacı** üretip sohbete rapor olarak koyabilir.

### Adımlar
1. Düğüm şeması + `sinyal`/`durum` hesabı **backend'de** (ajan çağrılabilir uç).
2. `src/components/KokNedenHaritasi.tsx` — 🔴 `…Panel` **değil** (K1).
3. Panelde açılır; yol + bir kat; kardeşler katlanır.
4. Her düğüm kendi **küçük grafiğini** çizer.
5. `ResultView`'da facet/scatter/ısı tıklama kısıtı **kaldırılır**.
6. Düğümde not → sohbete **yol diyagramıyla** vaka kaydı.
7. Üç izdüşüm (yatay · dikey · çip+liste).

### Kapı
- `test_ui_erisim.py` yeşil — `DrillDownPanel`'in **her** işlevi taşınmış olmalı
- Düğüm durumu testi: dört durumun dördü de üretilebiliyor; **silik olan tıklanabilir**
- Not testi: kaydedilen notta **yol** var
- Responsive testi: <768px'te ağaç **çizilmiyor**, çip+liste çiziliyor
- `test_panel_sayisi.py` ≤13

---

## FAZ 5 · GÖRSEL DİLİN UYGULANMASI

### Adımlar
1. Sohbet yüzeyindeki **prose**: `font-mono` → orantılı; 10-11px → 15-16px.
   ⚠ **Sayı · SQL · kod · tablo hücresi mono KALIR.**
2. Yüzey katmanları: kart `--surface-2`, panel `--surface-1`, yükseltilmiş `--surface-3`.
3. Yarıçap: kart/panel 12 · düğme/girdi 8 · çip 6.
4. Çizgi sayısını düşür — ayrımı **yüzey + boşlukla** kur.
5. Geçişler `--motion-md` + `--ease-standard`.

### Kapı
`test_ui_gorsel_dil.py` genişler:
- sohbet yüzeyinde `text-[9px]`/`text-[10px]` **yok**
- `font-mono` yalnız izinli bağlamlarda *(muafiyet listesi **gerekçeli**)*
- saf `#000`/`#fff` metin yok

---

## FAZ 6 · KAPANIŞ DENETİMİ

1. `lab/kapi.py --tam` — iki korpus (**~2 dk 10 sn**)
2. Envanterin **yeniden** koşulması: 269 işlev hâlâ sayılıyor mu
3. **Zaten kırık üç yüzey** ele alınır *(ayrı bir iş — bu planın kapsamında değil,
   ama kapatılmadan v1 "tamam" denmez)*
4. `belgeler/kilavuz/` altına **kullanıcı bakışlı** kısa bir "yenilikler" notu

---

# BÖLÜM D · RİSK KAYDI

| # | risk | önlem |
|---|---|---|
| **R1** | Taşımada işlev düşer | FAZ 0 kapısı — **her fazın sonunda** koşar |
| **R2** | `layout.tsx`'teki dört öge unutulur *(rail'de değiller)* | FAZ 0'da **ayrı ayrı** adlandırıldı |
| **R3** | Panel tavanı aşılır | Yeni bileşenler `…Panel` **değil**; çekmeceler bölüme dönüşür |
| **R4** | `page.tsx` tavanı aşılır | Düzen **çıkarılır** (FAZ 3), eklenmez |
| **R5** | Görsel dil değişmez, aynı çirkinlik yeni düzende | FAZ 5 kapısı: mono/boyut **ölçülür** |
| **R6** | Panel modale dönüşür | Rol/odak/Escape testi; `aria-modal` **yasak** |
| **R7** | Kök-neden şeması panele sığmaz | Panel **sürüklenebilir** %55vw'ye kadar; <1280px tam ekran katman |
| **R8** | İki geliştirici çakışması | Her fazın başında `git status`; **ana dizinde checkout/stash yok** |

---

# BÖLÜM E · TAŞIMADA EN SİNSİ DÖRTLÜ

Bunlar rail'in **içinde değil** — `layout.tsx`'te sabit duruyorlar. *"Rail'i taşıdım"*
diyen biri dördünü de atlar:

| # | işlev | yeri |
|---|---|---|
| 1 | **Tema anahtarı** (3 durumlu) | `FloatingControls.tsx:77` |
| 2 | **Çıkış** | `layout.tsx:44` → `LogoutButton.tsx:27` |
| 3 | **Bağlantı rozeti** (çevrimdışı · yedek LLM · kural-tabanlı · çevrimiçi) | `layout.tsx:42` → `ConnectionBadge.tsx:50` |
| 4 | **Kimlik şeridi** (e-posta · rol · süperadmin) | `layout.tsx:43` → `KimlikSeridi.tsx:72` |

## Zaten kırık üç yüzey — *taşımanın değil, mevcut borcun*

| işlev | neden erişilemez |
|---|---|
| ⇩ Denetim kaydı JSON-LD ihracı | `ContractDetailPanel` onu yalnız `contractId=""` iken çizer; **hiçbir çağıran** boş dize geçmiyor |
| Kanıt geçmişi (son 20 makbuz) | aynı sebep; `onSelect` de hiç geçilmiyor |
| "portföy" kapsam seçeneği | `ChatPanel` `superadmin` prop'u bekler, `page.tsx` **hiç göndermez** |
