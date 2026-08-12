# DÖNEM KIYASI VE **DEĞİŞİM ORANI**

> Bu bir **metodoloji** dosyasıdır (`§B10` · `§36.1-5`): garsona *«bu isteği hangi
> yapıyla karşıla»* der. Bir kelime listesi değildir — sistemin **zaten ürettiği** bir
> çıktının adını söyler.

## Sistem dönem kıyasını NASIL üretir

Kullanıcı iki dönemi kıyaslamak istediğinde **ayrı bir ölçü seçilmez**. Kıyas bir
**kip**tir: aynı ölçü, iki dönem için hesaplanır ve sistem üç kolon birden döndürür:

    <ölçü>                  → cari dönem
    <ölçü>_gecen            → kıyas dönemi
    <ölçü>_degisim_yuzde    → aradaki DEĞİŞİM ORANI (%)

Örnek (canlı, ölçülmüş): *«geçen yıla göre ciro»* →
`toplam_ciro` · `toplam_ciro_gecen` · `toplam_ciro_degisim_yuzde: 9.7`

## 🔴 KURAL: «büyüme oranı» BİR ÖLÇÜ ADI DEĞİLDİR

*«büyüme oranı»* · *«artış oranı»* · *«değişim oranı»* · *«ne kadar arttı»* · *«yüzde kaç
büyüdük»* — bunların hiçbiri katalogda bir **ölçü** değildir ve **aranmamalıdır**.
Hepsi yukarıdaki `_degisim_yuzde` kolonunun **konuşma dilindeki adıdır**.

Böyle bir soruda yapılacak:

1. Sorunun **ölçüsünü** seç (*«ciro büyüme oranı»* → ölçü `toplam_ciro`).
2. Dönem kıyasını kur (*«geçen yıla göre»* → önceki yıl).
3. Oranı **ayrıca isteme** — kıyas kipi onu zaten üretir.

⚠ *«büyüme oranı»*nı bir ölçü sanıp katalogda arama, **bulamama** ve *«hangi ölçüyü
istiyorsun?»* diye sorma. Ölçüldü (2026-08-12): *«geçen yıla göre ciro büyüme oranı»*
tam olarak böyle **cevapsız** kaldı — oysa *«geçen yıla göre ciro»* aynı sayıyı
oranıyla birlikte veriyordu.

> *Kullanıcının sorduğu şeyi sistem zaten üretiyorsa, sorulmayan şey bir ölçü değil bir
> addır.*

## Kıyas dönemi belirtilmemişse

*«ciro ne kadar arttı»* gibi bir soruda kıyas dönemi yoksa **uydurma**: dönem varsayımı
sistemin kendi kuralıdır (`M-4`) ve beyanla yapılır. Sen yalnız ölçüyü ve kıyas
**niyetini** bildir.

## Sınır — bu skill'in KAPSAMADIĞI

* **Gelecek** dönem (*«seneye ne olur»*): forecast **v1'de yok**, bilinçli kapsam dışı.
* **Hedefe göre** gerçekleşme (*«bütçe gerçekleşme oranı»*): bu bir dönem kıyası
  **değildir**, çapraz-küp bir eşleme ister ve o eşleme **iş tarafının beyanıdır**
  (bkz. `demo/packs/modul/butce/cubes/butce/metadata.yml`).
