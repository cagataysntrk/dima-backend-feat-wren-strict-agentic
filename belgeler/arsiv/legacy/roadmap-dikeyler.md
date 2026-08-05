# Yol haritası — dikeyler, konu modülleri ve kritik adımlar

> Kaynak: mimari denetim (docs/research/mimari-denetim-2026-07.md) + ADR-0005.
> İlke: **bir dikey = yeni YAML paketi, yeni Python değil.** Ürün adımlarının bir kısmı
> bu yüzden dikey açmanın önkoşuludur.

## Müşteri gerçeği (düzeltme)

- Müşterimiz: **Nuryıldız Tekstil (boyahane)**.
- **Egemen = müşterimizin kullandığı ERP** (sektördeki en yaygın boyahane ERP'si;
  ASP.NET + SQL Server/Oracle). Egemen bir müşteri DEĞİL, entegrasyon hedefi olan
  kaynak sistemdir. dima'nın işi Egemen DB'sine bağlanıp Nuryıldız'a raporlama yapmak.

## A. dima ürünü — kritik adımlar (öncelik sırasıyla)

| # | Adım | Neden | Durum |
|---|---|---|---|
| 1 | Sinonimleri cube metadata'sına taşı (`synonyms:` → generic router) | "Çok manuel" borcunun ~%70'i; dikey önkoşulu | **başladı** |
| 2 | ADR-0005 kompozisyonu: `packs/sektor/` + `packs/modul/` + `companies/` + composer, çoklu proje | Dikeylerin yaşayacağı yer | sırada |
| 3 | Gerçek DB kanıtı: Egemen-benzeri MSSQL ikinci wren-project (gerçek kolon adları) | Demo→ürün eşiği | sırada |
| 4 | Wren memory recall + store (few-shot + öğrenme döngüsü) | ADR-0001 K4; motor hazır, entegrasyon dima-backend'de | sırada |
| 5 | `"tarih"` → `time_dimensions[0]`; RuleBasedSqlGenerator demo-only izolasyon | Sessiz kırılma/yanlış riski | sırada |
| 6 | Güven katmanı: sistem-hesaplı confidence + uygulanan dönem chip'i | Provenance'ın tamamlanması | bekliyor |
| 7 | Fork'a özellik: `relativeDateRange` + ölçüye-göre-order | Backend incelir | bekliyor |
| 8 | Dashboard + zamanlanmış worker (cron+eşik+bildirim) | "agentic" vaadi | bekliyor |
| 9 | Eval'i yaşayan süreç yap (log→golden vaka) | Sürekli doğruluk güvencesi | 32 vaka tohum ✅ |

## B. Boyahane dikeyi (TEK aktif dikey — derinleşme)

1. Boyahane'yi gerçek pakete dönüştür: `packs/sektor/boyahane/` (fire cube + glossary +
   kurallar + golden SQL). A#1-2'nin ilk somut uygulaması.
2. OEE'yi sektörden bağımsız konu modülüne ayır: `packs/modul/oee/`.
3. **Nuryıldız/Egemen gerçek şema hizalaması**: MSSQL/Oracle bağlantısı, gerçek
   kolon/tablo adları, şema anotasyonu.
4. Eksik konu alanları (boyahane değer önerisi): reçete/kimyasal maliyet · sipariş/
   termin/sevkiyat · su-enerji/sürdürülebilirlik · kalite/renk sapması (ΔE, red).
5. Nuryıldız demo playbook'u: görüşme soru seti → eval'e bağlı golden senaryolar.

## C. Dikey stratejisi

- **Aktif:** Boyahane/tekstil terbiye — tek dikey; genişleme değil derinleşme.
- **Sıradaki aday (A#1-3 bitince):** Örme/dokuma kumaş üretimi — boyahanenin bitişiği:
  aynı müşteri ekosistemi (boyahanenin tedarikçi/müşterileri), aynı satış kanalı;
  OEE+kalite+termin modülleri aynen kalıtlanır, fark yalnız sözlük (iplik/gramaj/en).
- Başka dikey (genel imalat, gıda vb.) ŞİMDİLİK YOK — modül kütüphanesi "yeni dikey =
  yeni YAML" verdiğini kanıtlamadan dikey açılmaz (denetim uyarısı: elle kopya riski).

## D. Konu modülleri (yatay — bir kez yaz, her dikeye kalıt)

| Modül | Kapsam çekirdeği |
|---|---|
| `oee/üretim` (VAR) | OEE, kullanılabilirlik/performans/kalite, üretim kg, duruş |
| `kalite` | red/tekrar oranı, renk sapması (ΔE), ilk-seferde-doğru (FTR/RFT) |
| `bakım-arıza` | duruş nedenleri, MTBF/MTTR, planlı/plansız bakım |
| `sipariş-termin` | termin uyumu (OTD), gecikme, sipariş yaşlandırma, sevkiyat |
| `maliyet/muhasebe` | birim maliyet, kimyasal/enerji maliyeti, kârlılık, fire maliyeti |
| `sürdürülebilirlik` | su lt/kg, enerji kWh/kg, karbon, atık su |
| `vardiya/İK` | vardiya performansı, personel verimliliği, devamsızlık |

**Kritik gereksinim — TR/EN karışık terminoloji:** Türk fabrikalarında terimler karışık
kullanılır (OEE/verimlilik, downtime/duruş, RFT/ilk seferde doğru, ΔE/renk farkı...).
Her modülün glossary'si iki dili ve saha jargonunu kapsamalı; derin terminoloji
araştırması yapılıp `synonyms:` metadata'sına ve modül glossary'lerine işlenecek.
