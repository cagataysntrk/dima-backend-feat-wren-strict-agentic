# İş kuralları — boyahane metrik semantiği

Bu kurallar NL→SQL üretimini yönlendirir; sorgu yazarken UYULMASI zorunludur.
(Sektör paketi: boyahane · konu modülü: OEE/üretim.)

## Oran metrikleri → TOPLAM-üzerinden hesaplanır (ISO 22400) — asla SUM, satır-AVG de YAKLAŞIKTIR
Oranlar (`oee`, `kullanilabilirlik`, `performans`, `kalite`, fire oranı) gruplarken
**SUM(pay)/SUM(payda)** ile hesaplanır — satırdaki hazır oran kolonunun AVG'i
ağırlıksız olduğu için sistematik sapar (tipik 2-5 puan):
- kullanılabilirlik = SUM(calisma_dakika)/NULLIF(SUM(planlanan_dakika),0)
- performans        = SUM(gercek_uretim_kg)/NULLIF(SUM(teorik_uretim_kg),0)
- kalite            = SUM(saglam_kg)/NULLIF(SUM(gercek_uretim_kg),0)
- oee               = yukarıdaki üçünün çarpımı
- fire oranı        = SUM(fire_kg)/NULLIF(SUM(agirlik_kg),0)
- kâr marjı / kâr oranı = SUM(tutar - kimyasal_maliyet)/NULLIF(SUM(tutar),0)
- su yoğunluğu (L/kg)   = SUM(su_tuketim_lt)/NULLIF(SUM(agirlik_kg),0)
- enerji yoğunluğu (kWh/kg, ISO 22400 6.23 deseni) = SUM(enerji_kwh)/NULLIF(SUM(agirlik_kg),0)
`SUM(oee)` gibi oran TOPLAMA asla yapılmaz. Sonuç 0–1 ölçeğinde BIRAKILIR — yüzdeye
çevirmeyi ARAYÜZ yapar; `* 100` ile ÇARPMA (çift yüzde: %5573 gibi absürt değer).

## Miktar metrikleri → TOPLAM (SUM)
Bunlar sayılabilir miktarlardır; toplanır:
`calisma_dakika`, `durus_dakika`, `teorik_uretim_kg`, `gercek_uretim_kg`, `saglam_kg`,
`fire_kg`, `su_lt`, `enerji_kwh`, `tutar`, `kimyasal_maliyet`.
Kural: gruplarken **SUM(...)** kullan.

## Haftanın günü → TÜRKÇE ad
Haftanın gününe göre gruplarken `dayname()` (İngilizce: Monday..) KULLANMA. `isodow(tarih)`
(1=Pzt..7=Paz) ile grupla/sırala ve gün adını CASE ile Türkçe ver:
`CASE isodow(tarih) WHEN 1 THEN 'Pzt' WHEN 2 THEN 'Sal' WHEN 3 THEN 'Çar' WHEN 4 THEN 'Per'
WHEN 5 THEN 'Cum' WHEN 6 THEN 'Cmt' WHEN 7 THEN 'Paz' END`.

## Dönemsel karşılaştırma ("önceki döneme göre")
"aylık/dönemsel karşılaştır", "önceki dönem", "değişim/trend" istenirse:
1. ÖNCE metriği dönem düzeyinde topla (oran→AVG, miktar→SUM). Ham vardiya satırı düzeyinde
   `LAG` KULLANMA — yoksa binlerce satırlık anlamsız döküm çıkar.
2. SONRA `LAG(...) OVER (PARTITION BY <varlık> ORDER BY <dönem>)` ile önceki dönemi getir.
3. Değişim = güncel − önceki.
Raporu az kolonlu tut: `(varlık, dönem, metrik, önceki_dönem, değişim)`. 20 kolonluk geniş
dökümden kaçın — tek net metrik daha okunur ve grafiğe uygun olur.
