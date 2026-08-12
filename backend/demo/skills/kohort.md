# KOHORT ANALİZİ — **BUGÜN İFADE EDİLEMEZ**, ve pivot onun yerine geçmez

> Bu bir **metodoloji** dosyasıdır (`§B10` · `§36.1-5`). Bir yeteneği tarif etmiyor;
> bir yeteneğin **sınırını** tarif ediyor — ve sınırı bilmek, sınırı aşmaya çalışmaktan
> daha değerlidir.

## Kohort nedir — ve neden bir pivot DEĞİLDİR

Bir kohort analizi varlıkları **ilk görüldükleri döneme** göre gruplar ve her grubu
**kendi başlangıcına GÖRECE** zamanda izler:

    kohort (ilk ay)   ay+0    ay+1    ay+2    ay+3
    2025-01           100%     62%     48%     41%
    2025-02           100%     58%     45%      —
    2025-03           100%     64%      —       —

⊙ Ayırt edici iki şey: ① satırın anahtarı **varlığın ilk dönemi**dir (takvim dönemi
değil) ② sütun **görece** zamandır (`ay+1`), mutlak takvim değil.

Bir **pivot** (müşteri × ay) bunların **hiçbirini** taşımaz: her müşteri her ayda görünür,
ilk görülme bilgisi yoktur, sütunlar takvim ayıdır. İkisi farklı sorulardır.

## 🔴 Neden bugün üretilemez — ölçüldü (2026-08-12)

Kohort iki şey ister ve küp sözleşmesinde **ikisi de yoktur**:

| gereken | küp sözleşmesinde |
|---|---|
| varlık başına **ilk dönem** (`MIN(tarih) GROUP BY musteri`) | 🔴 yok — türetilmiş bir kolon, ölçü değil |
| **görece** zaman ekseni (`ay - ilk_ay`) | 🔴 yok — `timeDimensions` mutlak takvim kovaları verir |

⊙ Katalogda varlık + zaman ekseni taşıyan **11 küp** var (`cari` · `firsat` · `siparis` ·
`sikayet` · `parti` · `ticaret` …), yani veri **duruyor**; eksik olan veri değil, küp
sözleşmesinin **ifade gücüdür**. Bunu bir SQL ile çözmek `§38.4`'ün dokunulmazını
(*«LLM SQL yazmaz — küp yolunda»*) çiğnerdi.

## 🔴🔴 O HÂLDE NE YAPILACAK — susmak değil, BEYAN ETMEK

Doktrin açık: *«anlamadım» bir son cevap olamaz* (`§0.0`) ama *sessizce başka bir şey
teslim etmek* daha kötüdür (`§YS`). Ölçülen kusur tam buydu:

    «müşteri kohort analizi yap» → müşteri × dönem PİVOTU, 8 satır, 3 adımlık makbuz
                                 → «kohort metodolojisi uygulanmadı» beyanı: YOK

Yapılacak:

1. En yakın **gerçek** cevabı ver (müşteri × dönem kırılımı) — sayı doğru olsun.
2. **`yok_sayilan` alanına `"kohort"` yaz.** Sistem bunu kullanıcıya *«sorunun şu kısmı
   yansımadı»* diye bildirir; sen bir cümle uydurmazsın, alanı doldurursun.
3. Cevabı *«kohort»* diye **adlandırma**. Bir pivotu kohort diye sunmak, farklı bir
   soruyu cevaplayıp aynı soruymuş gibi teslim etmektir.

## Sınıra çok yakın duran, ama İFADE EDİLEBİLEN sorular

Bunlar kohort değildir ve normal yoldan cevaplanır — reddetme:

* *«bu yıl kaç yeni müşteri»* → bir **sayım**, kohort değil (ilk dönem gerekmez).
* *«müşteri bazında aylık ciro»* → bir **pivot**; kullanıcı zaten pivot istemiştir.
* *«en eski müşterimiz»* → `order`+`limit` ile bir **üstünlük** sorusu.

> *Bir yeteneğin yokluğunu, ona benzeyen bir çıktıyla kapatmak, yokluğu gizlemez —
> yalnız keşfini kullanıcıya bırakır.*
