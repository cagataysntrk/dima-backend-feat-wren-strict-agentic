# MENÜ ÖLÇÜMÜ — `G1`'in dört kanıtı, bugünkü hâli

> Alet: `lab/menu.py` · şirket: `demo-boyahane` · şema: **taze derleme**
> (`demo/wren-project`'ten DEĞİL — o gitignore'lu bir derleme artefaktı)

| kanıt | soru | beklenen | **ölçülen** | durum |
|---|---|---|---|---|
| `X8` | *«mesai ücreti ne kadar»* | `ik` | `ik.toplam_mesai_ucreti` | ✅ **KAPANDI** |
| `AA13` | *«üretim miktarı nedir»* | `parti` \| `oee` | `oee.toplam_uretim_kg` | ✅ **KAPANDI** *(beklenti düzeltildi)* |
| `Y6` | *«tamir süresi ne kadar»* | `bakim` | 🔴🔴 `kalite.toplam_ek_sure_dk` | **AÇIK — ve sınıfı DEĞİŞTİ** |
| `Z12` | *«şikayetleri bölgelere göre ver»* | `sikayet` | 🔴 hiçbir şey | **AÇIK** |

## 🔴🔴 En önemli bulgu: `Y6` artık *cevapsız* değil, **yanlış**

Rapor `Y6`'yı *«menüde adı yok»* diye yazmıştı. Ölçüm bunu çürüttü: soru **cevaplanıyor**
— ama `kalite` cube'undan, `toplam_ek_sure_dk` (üretimdeki *ek süre*) ile. Tamir ise
`bakim`'ın işi.

⊙ Yani `G1` (menüde ad yok) sessizce `G2`'ye (**yokluk ile yarımlık ayırt edilemiyor**)
dönüşmüş. Ve dönüşüm **kötüye** gitmiş: cevapsız bir soru kullanıcıya *"bilmiyorum"*
der, yanlış konudan cevaplanan bir soru **bir sayı** verir.

*Bir boşluğu kapatmanın en sessiz yolu, onu yanlış bir yemekle doldurmaktır.*

## Aletin bu ölçümle kapatılan körlüğü

İlk hâli **yalnız cevapsız** soruları raporluyordu — yani `Y6`'yı yapısal olarak
göremezdi. `beklenen konu` etiketi eklendi (bir yüklem değil, insan etiketi: `§101.1`
uyarınca yanlış-pozitif üretemez) ve dört kanıttan **üçü** artık kendiliğinden listeleniyor;
dördüncüsü (`X8`) gerçekten kapandığı için listelenmiyor.

## `AA13`'ün beklentisi neden düzeltildi

Rapor `parti.toplam_agirlik_kg` bekliyordu; o beklenti `miktar` terimi `parti`ye
**eklenmeden önce** yazılmıştı. Bugün `oee.toplam_uretim_kg` en az onun kadar doğru bir
cevap. Tek beklenti dayatmak, aletin **kendi yanlış-pozitifini** üretmesi olurdu — ve
`§101.1` bunun kusurdan pahalı olduğunu söylüyor.

*Bir ölçüm aracının beklentisi de bayatlar; bayat beklenti, sağlam bir kodu kusurlu
gösterir.*
