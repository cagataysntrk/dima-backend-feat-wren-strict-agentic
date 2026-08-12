# SATIŞ HUNİSİ (**pipeline**) — ve neden bu bir DÖNÜŞÜM hunisi DEĞİLDİR

> Bu bir **metodoloji** dosyasıdır (`§B10` · `§36.1-5`): garsona *«bu isteği hangi VAR
> OLAN yapıyla karşıla»* der. Yeni bir fiil, yeni bir ölçü, yeni bir kelime listesi
> tanımlamaz.

## Huni sorusu hangi küple karşılanır

Ölçüldü (2026-08-12, canlı katalog): `firsat` küpü **zaten bir satış hunisidir**.

    küp        : firsat   (sinonimleri: «huni» · «satis hunisi» · «pipeline» · «potansiyel»)
    aşama      : asama    (boyut)
    ölçüler    : firsat_adedi · firsat_tutari · agirlikli_tutar
                 kazanma_orani_yuzde · kaybedilen_tutar
    öteki boyut: musteri_kod · satis_temsilcisi · kayip_nedeni

*«Huni»*, *«pipeline»*, *«hangi aşamadayız»* türü bir soruda yapılacak: `firsat` küpünü
seç, `asama` kırılımını ver, ölçü olarak `firsat_adedi` (adet) ya da `firsat_tutari`
(tutar) kullan. **Yeni bir şey hesaplanmaz.**

## 🔴 AŞAMA SIRASI BİR İŞ BEYANIDIR — katalog onu alfabetik verir

Katalogdaki değerler alfabetiktir (`Kaybedildi · Kazanıldı · Numune · Pazarlık · Teklif ·
İlk Temas`) ve bu **iş sırası değildir**. Gerçek sıra:

    İlk Temas → Numune → Teklif → Pazarlık → Kazanıldı | Kaybedildi

⚠ `Kazanıldı` ve `Kaybedildi` **aynı basamağın iki sonucudur**, ardışık iki aşama değil.
Onları huninin son iki kademesi gibi dizmek, kaybı bir *«ilerleme»* gibi gösterir.

Sistem bu sırayı `order` ile **uygulayamaz** (`order` bir ölçüye göre sıralar, bir
kategori dizisine göre değil). Bu yüzden sıralama **anlatıda** kurulur; sayı küpten
gelir, sıra bu beyandan.

## 🔴🔴 SINIR: bu bir ANLIK DAĞILIM, bir DÖNÜŞÜM ORANI DEĞİL

`asama` her fırsatın **bugünkü** aşamasını taşır. Yani elde edilen şey:

    ✅ «şu an hangi aşamada kaç fırsat / ne kadar tutar var»      → ANLIK DAĞILIM
    🔴 «İlk Temas'tan Teklif'e kaçı geçti»                        → DÖNÜŞÜM — YOK

Dönüşüm oranı, her fırsatın **aşama geçmişini** (hangi tarihte hangi aşamaya geçtiği)
ister; küpte böyle bir olay tablosu **yoktur** (ölçüldü). Bir anlık dağılımı dönüşüm
oranı diye sunmak, farklı bir soruyu cevaplayıp aynı soruymuş gibi teslim etmektir.

⊙ Kullanıcı **dönüşüm** sorduysa: cevabı ver (anlık dağılım) ama *«dönüşüm»* kısmını
`yok_sayilan` olarak **bildir** — sistem onu kullanıcıya *«bu kısım yansımadı»* diye
yazar (`§YS`).

⊙ Tek istisna **`kazanma_orani_yuzde`**: bu ölçü katalogda **vardır** ve kazanılan
fırsatların payını verir. *«Kazanma oranı»* sorulduğunda dönüşüm geçmişine gerek yoktur —
o sayı zaten hesaplanmıştır.

## Üretim hunisi ayrıdır

`parti.asama` (`ÖN FİKSE → KASAR → YIKAMA → HT BOYAMA → KURUTMA → SANFOR`) bir **süreç
akışıdır**, satış hunisi değil. *«Hangi aşamada fire yüksek»* türü bir soru oraya gider.
İkisini karıştırmak, ölçüyü doğru ama konuyu yanlış seçmektir.

> *Bir hunide sayılan şey, aşamaların kendisi değil aralarındaki GEÇİŞTİR; geçiş kaydı
> yoksa elde kalan bir huni değil, bir enstantanedir.*
