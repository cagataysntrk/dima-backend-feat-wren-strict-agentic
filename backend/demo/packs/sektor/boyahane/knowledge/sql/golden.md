# Doğrulanmış örnek sorgular (golden SQL)

Benzer soru gelirse bu desenleri birebir izle. Hepsi DuckDB lehçesinde ve doğrulanmıştır.

## Vardiya × haftanın günü verimliliği (ısı haritası)
Soru: "vardiya × haftanın günü verimliliği (son 3 ay)" / "hangi vardiya hangi gün daha verimli"
Sonuç: tam 3 vardiya × 7 gün = 21 satır. Kolonlar: (vardiya, gun, ort_oee). Gün Pzt→Paz sıralı.
Gün adları TÜRKÇE olmalı — `dayname()` İngilizce (Monday..) döner, KULLANMA; `isodow` + CASE kullan.
```sql
SELECT vardiya,
       CASE isodow(tarih)
         WHEN 1 THEN 'Pzt' WHEN 2 THEN 'Sal' WHEN 3 THEN 'Çar' WHEN 4 THEN 'Per'
         WHEN 5 THEN 'Cum' WHEN 6 THEN 'Cmt' WHEN 7 THEN 'Paz' END AS gun,
       AVG(oee) AS ort_oee
FROM vardiya_kayitlari
WHERE tarih >= CURRENT_DATE - INTERVAL '3 months'
GROUP BY vardiya, isodow(tarih)
ORDER BY isodow(tarih), vardiya;
```
Notlar: `oee` orandır → **AVG**. Değeri 0–1 ölçeğinde BIRAK (`*100` YAPMA); yüzdeye çevirmeyi
arayüz yapar — `*100` çift yüzdeye yol açar (%5573 gibi). Gün sırası için `isodow(tarih)`
(1=Pzt..7=Paz) ile ORDER BY. Sadece 3 kolon döndür (vardiya, gun, ort_oee).

## Kişilerin aylık verimliliği + önceki dönem karşılaştırması
Soru: "kişilerin aylık verimlilik performanslarını karşılaştır, önceki dönemle de karşılaştır"
Sonuç: personel × ay, az kolonlu. Kolonlar: (ay, ad_soyad, ort_oee, onceki_ay_oee, degisim).
```sql
WITH aylik AS (
  SELECT p.personel_kodu, p.ad_soyad,
         date_trunc('month', vk.tarih) AS ay,
         AVG(vk.oee) AS ort_oee
  FROM vardiya_kayitlari vk
  JOIN personel p ON vk.personel_kodu = p.personel_kodu
  GROUP BY p.personel_kodu, p.ad_soyad, date_trunc('month', vk.tarih)
)
SELECT ay, ad_soyad, ort_oee,
       LAG(ort_oee) OVER (PARTITION BY personel_kodu ORDER BY ay) AS onceki_ay_oee,
       ort_oee - LAG(ort_oee) OVER (PARTITION BY personel_kodu ORDER BY ay) AS oee_degisim
FROM aylik
ORDER BY personel_kodu, ay;
```
Notlar: ÖNCE aya topla (AVG oee), SONRA LAG. Ham vardiya satırında LAG kullanma. `oee`'yi 0–1
BIRAK (`*100` yok). Fark kolonunu `oee_degisim` adlandır ki arayüz onu da % olarak göstersin.
