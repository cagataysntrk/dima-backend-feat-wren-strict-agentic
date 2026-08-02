# Görsel Dilbilgisi — bağlayıcı standartlar

> **Bu belgenin kuralı:** her madde ya bir **TESTLE zorlanır** ya da açıkça
> **"henüz zorlanmıyor"** diye işaretlenir. Denetlenmeyen bir standart bir standart
> değil bir temennidir — ve bu depoda o desen (*beyan var, kod tanımaz*) **sekiz kez**
> ölçüldü: `consistency_k` · `expose:` üreteci · fan-out ölçümü · `_select_consistent` ·
> `semi_additive` · `validate_project` · telemetri yazma yolu · `nl_corpus`'un kendisi.
>
> Mimari otorite `MIMARI.md`'dir (§13). Bu belge onun ayrıntısıdır; çelişkide MIMARI kazanır.

---

## 0. Temel karar: grafik kararı LLM'e VERİLMEZ (ADR-0024)

`viz.py`'nin iki katmanlı deterministik `analyze()`/`recommend()` tasarımı bilinçli bir
karardır (Show-Me / Cleveland–McGill temelli) ve **korunur**. Motor/kütüphane eklemek
serbesttir; **kararı LLM'e devretmek değil.**

İyileştirme LLM'den değil **daha zengin girdiden** gelir — ve o girdi zaten elimizdedir
(cube metadata'sı). Faz I1'in bulgusu tam buydu: `additive: semi` **beyan edilmişti** ve
`recommend()` onu **hiç almıyordu**.

---

## 1. Her yeni grafik türü bir SEÇİM KURALIYLA gelir

Yeni tür eklemenin şartı: *"ne zaman **DOĞRU** seçimdir"* sorusunun **deterministik**
cevabı. Aksi halde dağarcık büyür, kalite düşer.

Kural bir **tercih değil bir KAPIDIR**: koşul sağlanmıyorsa grafik **üretilmez** ve
çağıran tabloya düşer.

| Tür | Ne zaman doğru | Kapı | Zorlanıyor mu |
|---|---|---|---|
| **waterfall** | Bileşenler toplamı bitişe **birebir** varıyorsa (artıksız ayrışma) | `viz.waterfall_spec()` toplamı denetler, tutmazsa `None` | ✅ `test_waterfall.py` (11) |
| **stacked / pie / treemap** | Ölçü **toplanabilir** ise | `additive: semi\|non` beyanı yığmayı **yasaklar** | ✅ `test_viz_beyan_farkindaligi.py` (9) |
| bar · line · scatter · heatmap · facet · pivot | `analyze()`/`recommend()`'in mevcut kuralları | — | ✅ mevcut viz testleri |
| pareto · bullet · slope · boxplot · sankey · combo | — | — | ❌ **henüz yok** (bkz. §7) |

**Şelalenin kuralı neden bu kadar sert:** görselin tüm anlamı *"bu çubukları üst üste
koyarsan sondaki değere varırsın"*dır. Toplam tutmuyorsa **grafik yalan söyler** —
çubuklar bir yere çıkar, eksen başka bir yeri gösterir ve okuyan farkı **göremez**.

---

## 2. Renk SEMANTİKTİR, dekoratif değil

**Yön beyandan gelir, ad tahmininden değil.** `lower_is_better` cube metadata'sında
bildirilir: fire artışı **kötü**, ciro artışı **iyi**.

| Kural | Durum |
|---|---|
| Isı paleti yönü `lower_is_better`'a göre ters çevrilir | ✅ `chart.ts::heatPalette` |
| Yön kaynağı **cube kapsamlı** `VizSpec.lower_set`'tir, şema birleşimi değil | ✅ `ResultView` (ölçülen kusur, aşağıda) |
| Reçetede segment yönü renklenir (`▲ kötüleşti` kırmızı) | ✅ `PrescriptionLayer` |
| Genel bar/line serilerinde artış/azalış renk semantiği | ❌ **henüz zorlanmıyor** |
| Renk körlüğüne güvenli palet | ❌ **henüz denetlenmiyor** |

**Ölçülen kusur (2026-08-02):** frontend `lower_is_better`'ı **tüm cube'ların birleşimi**
olarak okuyordu. `toplam_dogalgaz_sm3` `surdurulebilirlik`'te düşük-iyi,
`enerji_makine`'de **değil** — birleşim ikisinde de ısı paletini ters çeviriyordu. Yani
aynı sayı, yanlış cube'da **yanlış renkle** okunuyordu. Artık VizSpec'in cube-kapsamlı
`lower_set`'i otoritedir; şema birleşimi yalnız **yedektir** (grafik kararı FE'nin yerel
`analyze()`'ından geldiğinde).

---

## 3. Sayı ve tarih biçimi TEK KAYNAKTAN

`app/fmt.py`. Grafik · tablo · rapor · e-posta · anlatım **hepsi** onu kullanır.

**Neden:** ölçüldü — aynı sayı iki yüzeyde farklı görünüyordu (`150,5` sohbette `151`,
e-postada `150,50`). Bir BI ürününde aynı raporun iki yüzeyde farklı okunması, sayıya
duyulan güveni doğrudan aşındırır.

Kural: **tam sayı → 0 ondalık; değilse → 2 ondalık.** Kesirli kısım **asla sessizce
atılmaz** — *"gösterilen sayı gerçek sayıdır"* garantisi, büyük tutarlarda iki hanenin
ayrıntılı görünmesinden önemlidir.

✅ `test_fmt_stats.py` (13) — sohbet ile e-postanın **aynı** sayıyı gösterdiğini kilitler.

---

## 4. Yüzeyler arası SADAKAT: tek VizSpec, N oluşturucu

> Aynı `cube_query` için **ekran · e-posta · rapor · pano · resume** aynı VizSpec
> kararlarını üretir. `recommend()` **tek** karar verir; yüzeyler **render eder**.

| Kural | Durum |
|---|---|
| Aynı girdi → aynı karar | ✅ `test_viz_sadakat.py` |
| Her çağıran `viz.meta_args()` **ve** `cube_query` geçirir | ✅ kaynak taramalı test |
| `viz_email` / `report` kendi `recommend`/`analyze`'ını **yazmaz** | ✅ kaynak taramalı test |

**Neden test var:** sözleşme kodda iddia ediliyordu ama **iki kez kırılmıştı** — bir
çağıran birim sözlüğünü `measure_units` diye **yanlış anahtarla** geçiyordu;
`semi_additive` ise **hiçbir çağıran** tarafından geçirilmiyordu.

Sapma **sessizdir**: kullanıcı ekranda çizgi grafiği görür, e-postada aynı sorunun bar
grafiğini alır ve hangisinin doğru olduğunu bilemez.

---

## 5. Kolon rolü kararı TEK KAYNAKTAN

`app/result_shape.py`. `interpret` · `viz` · `viz_email` · `contribution` **aynı**
sınıflandırmayı kullanır ve `cube_query` **boyut otoritesidir**.

**Neden:** iki motor kolon rollerini bağımsız çıkarıyordu ve zaman-adı sözlükleri
farklıydı (11 ad vs 10). Aynı cevapta **grafik zaman serisi çizerken cümle onu kategori
sanabiliyordu** — ve ikisi de *"deterministik"* rozetliydi.

`gun`/`gün`/`day` bilinçle **zaman sayılmaz**: haftanın günü döngüsel bir kategoridir,
zaman çizgisi değil.

✅ `test_result_shape.py` (9)

---

## 6. Belirsizlik BİRİNCİ SINIF — görselde de görünür

| Durum | Nasıl görünür | Zorlanıyor mu |
|---|---|---|
| **Kırpılan segment** | *"N segment eşiğin altında kaldı — gösterilmedi, **yok sayılmadı**"* | ✅ `ContributionLayer` |
| **Taranmayan boyut** | *"N boyut üst sınır nedeniyle taranmadı"* | ✅ `ContributionLayer` |
| **Pay tanımsız** (`net ~0`) | `—` gösterilir, **`%0` DEĞİL** (`%0` = *"katkısı yok"*, yanlış olur) | ✅ `ContributionLayer` · `PrescriptionLayer` |
| **Dağınık değişim** | Öneri **üretilmez**, *neden* üretilmediği söylenir | ✅ `PrescriptionLayer` · `test_recete.py` |
| **Fan-out ölçülmedi** | `⇱?` rozeti — *"ölçülmedi"* ≠ *"temiz"* | ✅ `InterpretationBar` |
| **Ajan koşusu kısıldı** | *"Ajan koşusu: N adım · KISILDI (gerekçe)"* | ✅ `_plan_izi` |
| **Eksik dönem çizgide boşluk** (birleştirilmez) | — | ❌ **henüz zorlanmıyor** |
| Bar'da sıfır tabanı zorunlu, line'da değil | — | ❌ **henüz zorlanmıyor** |

**"Veri yok" ile "kırpıldı" AYRI şeylerdir.** Birincisi bir olgu, ikincisi bizim
kararımız — ve kararımızı gizlemek kapsamı olduğundan geniş göstermektir.

---

## 7. Kanıt her görselde bir tık uzakta

Makbuz (`contract_id`) · köken + fan-out sertifikası (`⇱✓/⇱⚠/⇱?`) · ajan koşusu izi ·
karar kaydı doğrulaması. Hepsi **cevabın kendi kartında** — ayrı bir panele gitmeden.

`ContractDetailPanel` bir **derinleşmedir**, giriş noktası değil.

---

## 8. Henüz YOK — açıkça

- **Kalan dağarcık:** pareto · bullet · slope · boxplot · sankey · combo. Her biri
  **kendi seçim kuralıyla** gelmelidir.
  *Pareto özel not:* `interpret._signals` yoğunlaşmayı **zaten tespit ediyor** ve
  `prescribe.py` onu **ölçüyor** — ama frontend'in `ChartKind`'ında pareto **yok**.
  Eklemek backend kuralı + ECharts oluşturucusu + toggle demektir; yarısını yapmak
  **yetim bir alternatif** üretirdi (MIMARI §14.1).
- **Renk körlüğü paleti** ve **koyu/açık tema** denetimi.
- **Eksen kuralları:** kesme · sıralama · sıfır tabanı · eksik dönem boşluğu.
- **PDF/dışa aktarım** aynı VizSpec'ten.
- Rapor katmanının **anlatı + kanıt** zinciri (soru → bulgu → neden → öneri → makbuz).
