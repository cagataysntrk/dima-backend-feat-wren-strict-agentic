# UI/UX — ARAŞTIRMA ve DENETİM · v1

**Tarih:** 2026-08-05 · **HEAD:** `2bb190a` · **Kapsam:** `dima-frontend-demo-master/src`
**Bu tur kod değiştirmedi.** Ölçüldü, okundu, `grep`lendi, AST'si çıkarıldı.

---

## §0 · Otorite ve çakışma yasağı

Otorite sırası değişmedi: `OPERASYON.md` → `OPERASYON-DURUM.md` → yol haritası →
`backend/MIMARI.md`. **Bu dosya otorite taşımaz**; bulguları borç defterine geçtiğinde
görevini tamamlar.

🔴 **Tekrar edilmeyenler — kasten.** `belgeler/denetim/2026-08-05_V1-SON-KONTROL.md` §4'ün ölçtüğü **sekiz UI kusuru**
(`opacity-40` çifte anlamı · `focus-trap` yokluğu · `window.prompt` birincil yüzey ·
`max-md:` yokluğu · cevap kartında `<details>` yokluğu · *"Yüksek güven (%100)"* ·
gömülü NUL · `AuthUser.email`) burada **yeniden anlatılmaz**. Hepsi ölçüldü, hepsi
düzeltildi, evi orasıdır. Bu belge yalnız **oraya girmemiş** olanı taşır.

Her sayının yanında onu üreten komut vardır (kural D2). *Sayı çürür, komut çürümez.*

---

## §1 · ÖLÇÜLEN YÜZEY — arayüz bugün neyden ibaret

```bash
cd dima-frontend-demo-master
find src/app -name page.tsx | wc -l                                    # 5 rota
grep -rE "export (default )?function [A-Za-z]+Panel" src/ | wc -l      # 13 panel
ls src/components/*.tsx | wc -l                                        # 42 bileşen
grep -rho "<button" src/ --include=*.tsx | wc -l                       # 165 buton
grep -rho "useMutation" src/ --include=*.tsx | wc -l                   # 51 mutasyon
wc -l src/components/*.tsx src/app/page.tsx | tail -1                  # 10.435 satır
```

| Ölçü | Değer |
|---|---|
| Rota | **5** *(`/` · `/login` · `/review` · `/brand` · `/paylasim/[token]`)* |
| Panel | **13** — 🔴 **v1 tavanı DOLU** (`PK-22`/`PK-23`) |
| Bileşen | **42** · **10.435 satır** |
| Buton | **165** *(63'ü tek dosyada: `ReportCard` 25 · `InterpretationBar` 19 · `ResultView` 11)* |
| Sunucu mutasyonu | **51** |
| Panelde durum kapsaması | yükleniyor **10/42** · hata **12/42** · boş durum **19/42** |

### 1.1 · Mimarî model — *tek sayfa, üç bölge, bir şerit*

Arayüz **klasik bir menü ağacı değildir**. Yapı şu:

```
┌──────────────────────────────────────────────────────────┬────┐
│  SOL: sohbet (ChatPanel)     │  SAĞ: rapor (ReportPanel)  │ ŞE │
│  · soru yazılır              │  · cevap kartları          │ Rİ │
│  · thread listesi            │  · thread'e göre gruplanır │ T  │
│  · kapsam/mod/yol şeritleri  │  · her kart kendi eylemleri│    │
└──────────────────────────────────────────────────────────┴────┘
                                             ↑ Analiz Tuvali (opsiyonel)
```

**Şerit (rail)** sağ kenarda yüzen 6 ikon: sohbet geçmişi · bildirim · panolar ·
ölçü inceleme · yardım · ayarlar *(+ çıkış)*. **Mobilde (<768px) alt çubuğa döner** —
`FloatingControls.tsx`'in kendi yorumunda gerekçesi yazılı: *"3rem'lik dikey şerit 375px
ekranın %13'ünü yer ve başparmakla en zor ulaşılan köşededir."*

**Panolar** ve **Ölçü inceleme** ikonları **koşullu**: biri `dashboards` bayrağına, öteki
`measure:read` iznine bağlı. Yani **kullanıcının gördüğü şerit, rolüne göre kısalır** —
bu doğru bir tasarım ve belgede yazılı olmalı, çünkü *"bende o ikon yok"* bir kusur
raporu olarak gelebilir.

---

## §2 · KAPILAR NE YAPIYOR — *önce hakkını teslim et*

Bir denetimin ilk görevi **var olanı doğru anlatmaktır**. Bu arayüzün a11y ve panel
disiplini **gerçekten kapılı** ve kapılar **gevşek değil**:

| Kapı | Ne kilitliyor |
|---|---|
| `test_a11y.py` | **A11Y-1** işlevsel kontrol yalnız emoji olamaz *(yazı glifleri adıyla dışlanmış — `✕`/`?` serbest)* · **A11Y-3** modal odak tuzağı + odağın geri verilmesi · **A11Y-4** `window.prompt` birincil yüzey değil · **A11Y-5** ESC/ENTER fareye bağımlı değil · **A11Y-7** görünür metni olmayan buton `aria-label` **zorunlu** · **A11Y-8** şerit ikonları etiket+tooltip · **A11Y-9** *"devre dışı"* ile *"soluk"* **aynı token'ı paylaşamaz** + ikinci kanal + hata metni |
| `test_panel_sayisi.py` | panel tavanı **13** — `export` sayımıyla, dosya değil |
| `test_panel_kurallari.py` | **PK-1** *yeni özellik yeni panel doğurmaz* · **PK-24** yüzey kırpması yasağı |
| `test_responsive.py` | 375 / 768 / 1024 — yatay taşma yok, birincil eylem erişilebilir |
| `test_tasarim_sistemi.py` | token disiplini + karanlık mod |

> 🔴 **A11Y-7'nin kendi cümlesi, bu deponun kalitesini gösteriyor:** *"`title` bir
> `aria-label` **değildir**: dokunmatik cihazda hover yoktur. Bir etiketi hover'a
> bağlamak, onu fareye bağlamaktır."* — Denetim bu kuralı **kırmaya çalıştı** ve
> kıramadı: `title`-only buton arayışı **yanlış-pozitif** verdi, kapı doğru ölçüyor.

**Yargı:** erişilebilirlik ve panel disiplini **v1 için yeterli**. Aşağıdaki bulgular
bunların **kapsamadığı** eksende.

---

## §3 · 🔴 YENİ BULGULAR — kapıların görmediği eksen

Beş kapının ortak kör noktası şu: hepsi **bir ögenin nasıl göründüğünü ve
erişilebilirliğini** ölçüyor. Hiçbiri **bir eylemin sonucunun ne olduğunu** sormuyor.

### F1 · 🔴 **Yedi yıkıcı buton, sıfır onay, sıfır geri alma**

```bash
grep -rn "del\.mutate(\|sil\.mutate(\|deleteMut\.mutate(" src/ --include=*.tsx
grep -rn "window.confirm\|confirm(" src/ --include=*.tsx      # → 0
```

| # | Buton | Dosya | Sildiği şey | Sunucu davranışı |
|---|---|---|---|---|
| 1 | *"Sohbeti sil"* | `HistoryPanel.tsx:71` | tüm konuşma | soft-delete |
| 2 | *"Panoyu sil"* | `DashboardsPanel.tsx:101` | pano + widget'ları | soft-delete |
| 3 | *"Widget'ı kaldır"* | `DashboardView.tsx:196` | pano widget'ı | soft-delete |
| 4 | *(tercih sil)* | `TercihlerPanel.tsx:75` | sunum tercihi | soft-delete |
| 5 | *(bildirim tercihi sil)* | `TercihlerPanel.tsx:156` | kanal tercihi | soft-delete |
| 6 | *"Zamanlamayı sil"* | `SchedulesPanel.tsx:105` | zamanlanmış rapor | ⟳ **soft-delete** — düzeltme aşağıda |
| 7 | 🔴 *"sil"* | `ConnectionReviewPanel.tsx:321` | **veri kaynağı bağlantısı** | ~~HARD~~ → ✅ **soft-delete** (`f1a7c92d4b60`) |

> ⟳ **DENETİM DÜZELTMESİ (2026-08-05, aynı gün).** Bu tablo **iki** hard-delete sayıyordu;
> ölçüm **bir** buldu. `schedules.remove()` **zaten soft-delete**'tir ve kodun kendi
> satırı bunu yazıyor: `row.deleted_at = datetime.utcnow()` · *"Soft-delete (deleted_at
> damgası; fiziksel silinmez — ADR-0019)"*.
>
> 🔴 **Denetimin kendi kuralı burada da geçerli:** *bir iddia, kodun okunmasıyla
> doğrulanmadıysa bir iddiadır.* Tek gerçek ihlal `connections`'tı ve **kapandı**;
> depoda başka hard-delete **yok** (`test_hard_delete_yok.py`, AST taraması).

**Üç ayrı ilkeyle çelişiyor — ve üçü de bu deponun kendi yazısı:**

1. **Proje kuralı ihlali.** `app/routers/conversations.py:121` şunu yazıyor:
   *"SOFT DELETE (**proje kuralı: hard-delete YOK**)"*. `connections.py:171`'deki
   `s.delete(conn)` bu kuralın **düz ihlalidir** — ve sildiği şey en pahalı nesne:
   müşterinin veri kaynağı bağlantısı.
2. **Kendi risk sınıflandırmasını atlıyor.** `app/eylem.py:77` `geri_alinabilir: bool`
   alanını taşıyor ve yorumu net: *"`False` → **senkron onay ŞART** (plan: «geri
   alınamaz iş»)"*. `eylem.py:98` `zamanla.olustur`'u `geri_alinabilir=False`
   işaretliyor. Yani **sistem zamanlamanın geri alınamaz olduğunu BİLİYOR** —
   ama o bilgi yalnız `/ask` yolunda kullanılıyor; **panelin kendi sil düğmesi o
   yoldan geçmiyor.**
3. **D9'un kendi sınırı.** D9 *"kapsam içi **ve GERİ ALINABİLİR** iş istemsiz koşar"*
   der. İstemsizlik **geri alınabilirlik şartına bağlıdır**; 6 ve 7 numaralı butonlar
   geri alınamaz **ve** istemsiz.

> 🔴 **Sınıfın adı: «politika bir yolda var, öteki yolda yok».** Bu, `OPERASYON.md`
> **KAT-5**'in (*sayma, kapat*) kardeşidir: bir kural **tek çağrı yolunda** uygulanırsa,
> ikinci yol onu **sessizce** delip geçer. Onay akışı `/ask` için tasarlandı; panel
> düğmeleri REST'e doğrudan gidiyor.

⚠ **Karşı argümanı da yazalım, çünkü haklı payı var:** `onay_akisi.py`'nin kendi
araştırma notu *"kullanıcılar izin isteklerinin ~%93'ünü onaylıyor; ne kadar çok onay
görürse her birine o kadar az dikkat eder"* diyor — yani **her silmeye modal koymak
çözüm değil**. Doğru ayrım maddenin kendi cümlesinde: *"izolasyon gücünü kullanıcının
gözetim kapasitesine göre ayarla."* Pratikte:

- **soft-delete olan 5 buton** → onay **gerekmez**; gereken **geri alma yüzeyi** (F2).
- **hard-delete olan 2 buton** → **yazılı onay** gerekir *(`useAdSor` deseni zaten var:
  adı yaz → onayla)*. Modal değil, **tek satırlık bir doğrulama** yeter.

### F2 · 🔴 **Soft-delete var, GERİ ALMA YÜZEYİ yok** — *"geri alınabilir" yalnız kâğıtta*

```bash
grep -rn "deleted_at" backend/app/routers/*.py | wc -l     # sunucu soft-delete yapıyor
grep -rni "geri al\|undo\|kurtar\|geri yükle" src/ --include=*.tsx   # → yalnız `doVerify({undo})`
```

Sunucu 5 nesneyi **silmiyor, damgalıyor** (`deleted_at`) — kayıt **duruyor**. Ama
arayüzde **silinmiş bir şeyi geri getiren tek bir düğme yok**. Tek istisna:
`ReportCard.tsx:251`'in `doVerify({ undo })`'su — ✓/✗ oyunu geri alınabiliyor.

**Sonuç:** kullanıcı açısından soft-delete ile hard-delete **birebir aynı deneyimdir**.
Ödenmiş bir güvenlik ağı (`deleted_at` altyapısı, ADR-0019) **kullanıcıya ulaşmıyor** —
bu, denetim raporunun §3A'da adlandırdığı *"bedeli ödenmiş ama teslim edilmemiş yetenek"*
sınıfının **arayüzdeki örneğidir**.

> 💡 En ucuz çözüm bir modal değil, bir **çizgi**: silinen satır 5 saniye
> *"silindi · geri al"* şeridi bıraksın. `KayitBildirimi.tsx` **zaten böyle bir
> bileşen** — deseni var, ikinci kullanıcısı yok.

### F3 · 🔴 **On dört mutasyon, sıfır hata yüzeyi** — *sessiz başarısızlık*

```bash
for f in src/components/*.tsx; do m=$(grep -c useMutation "$f");
  e=$(grep -c 'onError\|isError\|\.error\|hata' "$f");
  [ "$m" -gt 0 ] && [ "$e" -eq 0 ] && echo "$f: $m mutasyon · 0 hata yüzeyi"; done
```

| Bileşen | Mutasyon | Hata yüzeyi |
|---|---|---|
| `DashboardView.tsx` | **6** | **0** |
| `DashboardsPanel.tsx` | **4** | **0** |
| `HistoryPanel.tsx` | **2** | **0** |
| `AnalysisCanvas.tsx` | **2** | **0** |

Toplam **51 mutasyonun 14'ü** hiçbir hata durumu göstermiyor.

> ⟳ **YENİDEN ÖLÇÜLDÜ (aynı gün):** sayı **14'ten büyük**. Dört bileşen değil, **dokuz**
> bileşende mutasyon sayısı `onError` sayısını aşıyor (`ConnectionReviewPanel` 7/1 ·
> `DashboardView` 7/2 · `ReviewPanel` 4/2 · `PrescriptionLayer` 3/0 ·
> `ContractDetailPanel` 2/0 · `AnalysisCanvas` · `ContributionLayer` · `DcmAkisi` ·
> `SchemaPanel` 1/0). Üçü kapatıldı (`DashboardsPanel` · `HistoryPanel` ·
> `TercihlerPanel`) ve altyapı **tek sahipli** kuruldu (`lib/mutasyonHatasi.ts` +
> `HataSeridi.tsx`); kalanlar aynı deseni **bağlamayı** bekliyor.
> ⚠ *Bir sayıyı düzeltmek onu büyütebilir; ölçmemek küçültmez.* Pratikte: yetkisi olmayan
bir kullanıcı *"Panoyu sil"*e basar → sunucu **403** döner → **ekranda hiçbir şey olmaz**.
Satır yerinde durur. Kullanıcı ya tekrar basar ya *"arayüz donmuş"* der.

🔴 **F1 ile birleşince zincir şu oluyor:** *onay yok → başarısızlık bildirimi yok →
geri alma yok.* Üçünün kesişimi, tek bir kusurun toplamından **daha kötüdür**: kullanıcı
ne olduğunu **hiçbir aşamada** öğrenemiyor.

### F4 · ⚠ **Tek ses kuralının arayüz yarısı yok**

Backend'de `app/soz.py` var — FAZ 5.17, *"tek ses: metin katalogu"*, kök-neden maddesi
olarak inmiş. Frontend'de karşılığı **yok**:

```bash
ls src/lib/    # api-client · chart · export · format · odakTuzagi · providers ·
               # tema · threads · types · useClickOutside · useFeature · usePermission
               # → soz.ts / metinler.ts YOK
```

Yani kullanıcıya görünen Türkçe metnin **yarısı** tek sahipli (backend `soz.py`),
**yarısı** 42 bileşene dağılmış hâlde. Bu bugün bir hata değil, bir **çürüme yüzeyi**:
aynı kavram iki yerde iki farklı kelimeyle anılabilir ve hiçbir kapı bunu görmez.
*(Deponun 1 numaralı kusur sınıfı olan **"aynı kural iki sahip"**in metin hâli.)*

### F5 · ⚠ **Ağırlık merkezi tek dosyada**

`ReportCard.tsx` **1.107 satır · 25 buton** — arayüzün tüm cevap-sonrası etkileşimi
burada: zamanla · panoya ekle · doğrula · yanlış bildir · drill · iz göster · karta yanıt
ver · onay kartı · SQL göster · sözleşme · sohbet çapası · hücre altı kırılım. Backend'de
`ask.py` için kurulan **modül büyüme kapısı** (`0.21`) frontend'de **yok**:

```bash
ls backend/tests/test_modul_buyume.py     # var — yalnız backend modülleri
grep -rn "ReportCard" backend/tests/test_modul_buyume.py    # → 0
```

Bu bir kusur değil **bir risktir**: `ask.py` tam bu şekilde 2.498 satıra çıktı ve
borç 7'yi doğurdu. **Aynı hastalığın frontend'de ölçülmeyen hâli.**

### F6 · 🔴 **Kullanıcının «yok» sanacağı 12 ödenmiş özellik** *(denetim raporu §10.8'e bağlı)*

Bugün arayüzde **görünmeyen** ama **yazılmış ve testli** olanlar — biri arayüzü test
ederken *"bu ürün bunu yapmıyor"* diye rapor edecektir:

**tazelik** · **metrik sertifikası** · **KPI pin** · *"bunu takip et"* · *"paylaş"* ·
**hedef kıyası** · **içgörü paketi** · **bilgi merkezi** · **DCM modu** · **kapsam
merceği** · **hızlı↔derin anahtarı** · **onay talebi/süre aşımı**.

🔴 **UX açısından kritik ayrım** *(`belgeler/denetim/2026-08-05_DENETIM.md` §11'de ölçüldü)*:
bunların bir kısmı **kapalı** (bayrağı çevirince gelir), bir kısmı **bağlanmamış**
(bayrağı çevirmek hiçbir şey yapmaz). Arayüz testinde ikisi **birebir aynı görünür** —
ve bu ayrımı bilmeden test eden kişi yanlış bir *"özellik çalışmıyor"* yargısı üretir.

---

## §4 · ARAŞTIRMA ZEMİNİ — bulgular hangi ilkeye dayanıyor

Bu bölüm bulguları **keyfi tercih** olmaktan çıkarır; her biri yerleşik bir etkileşim
ilkesine bağlanır ve deponun **kendi ölçümüyle** kesişir.

| İlke | Karşılığı | Bu depodaki kanıt |
|---|---|---|
| **Kullanıcı denetimi ve özgürlüğü** — *"acil çıkış" her zaman olmalı* | **F1 · F2** | `eylem.py`'nin `geri_alinabilir` alanı bu ilkenin **kodlanmış hâli**; panel yolu onu atlıyor |
| **Sistem durumunun görünürlüğü** — *sistem ne yaptığını söylemeli* | **F3** | 14 mutasyon sessiz; `KayitBildirimi.tsx` deseni var, kullanılmıyor |
| **Hata önleme > hata mesajı** — *yıkıcı eylemde sürtünme ekle* | **F1** | `useAdSor` (yazılı doğrulama) **zaten var**, silmede kullanılmıyor |
| **Onay yorgunluğu** — *çok istem = az dikkat* | **F1'in sınırı** | `onay_akisi.py`: *"izin isteklerinin ~%93'ü onaylanıyor"*, *"izolasyon gücünü gözetim kapasitesine göre ayarla"* → **her silmeye modal YANLIŞ olurdu** |
| **Tanıma > hatırlama** | **F6** | kapalı özellik ile bağlanmamış özellik ekranda ayırt edilemiyor |
| **Tutarlılık ve standartlar** | **F4** | metin iki sahipli |
| **Dokunmatikte hover yoktur** | ✅ **kapalı** | `A11Y-7` bunu zaten kilitliyor |
| **Renk tek kanal olamaz** | ✅ **kapalı** | `A11Y-9` üç ayrı testle kilitliyor |

> 🔴 **Bu denetimin en dürüst cümlesi:** arayüzün **görsel ve erişilebilirlik disiplini
> güçlü**; zayıf olan **eylem sonrası sözleşme** — *ne olacak, oldu mu, geri alabilir
> miyim*. Kapılar ilkini ölçüyor, ikincisini hiç sormuyor.

---

## §5 · SIRA ÖNERİSİ — *ucuzdan pahalıya, etkisi ölçülür*

1. 🔴 **İki hard-delete'e yazılı onay** (`connections` · `schedules`). `useAdSor`
   deseni hazır; yeni bileşen gerekmez. **Kapısı:** `test_a11y`'nin yanına
   *"hard-delete çağrı yeri onaysız olamaz"* taraması.
2. 🔴 **`connections` hard-delete → soft-delete.** Proje kuralının ihlali; düzeltmesi
   `deleted_at` damgası, üç satır. *Bir kuralı yazıp bir yerde uygulamamak, kuralı
   yazmamaktan kötüdür — çünkü uygulandığı sanılır.*
3. **Geri alma şeridi** — `KayitBildirimi` desenini silme akışına bağla. 5 soft-delete
   **bir anda** kullanıcıya geri alınabilir olur.
4. **14 sessiz mutasyona hata yüzeyi.** `apiErrorMessage` **zaten var**
   (`page.tsx` kullanıyor); dört bileşene bağlanacak.
5. **Frontend metin katalogu** (`src/lib/soz.ts`) — `soz.py`'nin aynası. Ucuz değil,
   ama **çürüme yüzeyini kapatan tek şey**.
6. **Frontend modül büyüme kapısı** — `ReportCard.tsx` bugünkü satırında dondurulur;
   büyürse kırmızı. `ask.py` dersinin tekrarını önler.

⚠ **Hiçbiri panel açmıyor.** Tavan **13/13 dolu** (`PK-22`) ve altısının da yeni panel
gerektirmemesi **kasıtlıdır**: `PK-1` *"yeni özellik yeni panel doğurmaz"* der.

---

> *Bir arayüzün kalitesi, hiçbir şeyin yanlış gitmediği turda ölçülemez.*
> *Bu denetimin dördü de yanlış giden turu sordu: onay yok, bildirim yok, geri dönüş yok.*
