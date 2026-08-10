"""🔴🔴 `§YB` — **ADI OLUMSUZ OLAN BİR ÖLÇÜ, YÖN BEYANI OLMADAN KALAMAZ.**

## Ölçülen kusur (canlı, 2026-08-10)

    «bu yıl en kötü bakım maliyeti olan makine»
      → order = {"measure": "bakim_maliyeti", "direction": "asc"}
      → ilk   = ROTASYON BASKI · 15.161 ₺        ← EN UCUZ makine
      → source=cube · **beyan yok**

Sistem *«en kötü»*yü **en düşük** diye okudu — yani bir **maliyet** için *«çok olan
iyidir»* varsaydı ve cevabı **tersine çevirdi**. Ve bunu `source=cube` rozetiyle,
yani en güvendiğimiz basamakta yaptı.

⊙ Pack'in kendi yorumu kusuru zaten adlandırmış (`isg/metadata.yml`):
*«beyan yoksa `bagla` «çok olan iyi» varsayar»* — ama yalnız bir modülde uygulanmış.

## Kural — kelime listesi değil, **adın kendisi**

Bir ölçünün adı `maliyet` · `fire` · `iade` · `şikayet` · `kaza` · `gecikme` · `duruş` ·
`hata` · `sapma` gibi **olumsuz bir kavram** taşıyorsa, o ölçüde çoğun iyi olması
**mümkün değildir**. Beyan bir tercih değil bir **olgudur** ve eksikse cevap sessizce
ters döner.

⚠ Kapı **adın kendisine** bakar, kullanıcının cümlesine değil: bu bir dil kuralı değil
bir **katalog bütünlüğü** kuralıdır (ADR-0008 kapsamı dışında).

*Bir yönü beyan etmemek, tersini beyan etmektir — çünkü varsayılan bir yön zaten var.*
"""

from __future__ import annotations

#: Adı tek başına yönü belirleyen kavramlar. ⚠ Kısa parçalar **yok**: ilk yazımımda
#: `ret` deseni *«u**ret**im»*in içinde eşleşti ve üç yanlış-pozitif üretti (`§101.1`
#: kendi yüklemimde). Her desen **kelime sınırıyla** aranır.
#: 🔴 **YÜKLEM ÜÇ KEZ YANLIŞ YAZILDI — ve üçünü de kapı yakaladı.**
#:
#: 1. `ret` deseni *«u**ret**im»*in içinde eşleşti → üç yanlış pozitif.
#: 2. Sıkı sınır (`$|_`) `bakim_maliyet**i**`'yi (iyelik eki) **kaçırdı** — yani kapı
#:    yeni bir *«…maliyeti»* adını göremezdi.
#: 3. *«en fazla üç harf ek»* gevşetmesi `kaza` kökünü *«**kaza**nma»*ya bağladı.
#:
#: ⊙ Ders: Türkçe ek kuralı **uydurulmaz, çağrılır**. `cube_router._ek_gecerli` bu
#: deponun tek ek doğrulayıcısıdır ve üç yazımın da düzeltmeye çalıştığı şey odur.
#: *Bir dilin kurallarını üçüncü kez yeniden yazmaya başladığında, aslında var olan
#: birini aramıyorsun demektir.*
KOKLER = ("maliyet", "gider", "fire", "iade", "sikayet", "kaza", "hata", "rework",
          "gecikme", "durus", "kayip", "sapma", "iskarta", "atik", "devamsizlik",
          "ariza", "ceza", "zarar")


#: 🔴 **DÖRDÜNCÜ YAZIM — ve bu kez morfoloji YAZILMIYOR.**
#: `_ek_gecerli` genel bir ek doğrulayıcıdır ve *«kazan-ma»*yı *«kaza+nma»*dan ayıramaz;
#: ayırması da beklenemez — o bir **çekim** doğrulayıcısı, bir kök çözümleyici değil.
#: Bir katalog bütünlüğü kapısının morfolojiye ihtiyacı yoktur: **ad ekleri** kapalı ve
#: küçük bir kümedir (`i` · `si` · `leri` · `lari` · `im` · `imiz`) ve fiilden isim
#: yapan `-ma/-me` **kasten dışarıdadır** — çünkü bir kökü başka bir köke bağlayan
#: tek ek odur (`kaza` → `kazanma`).
#: *Bir dilin tamamını modellemek gerekmiyorsa, modellememek gerekir.*
AD_EKLERI = ("", "i", "si", "leri", "lari", "im", "imiz", "u", "su")


def olumsuz_mu(ad: str) -> bool:
    """Ölçü adı **olumsuz bir kavram** taşıyor mu? Kök + kapalı ad-eki kümesi."""
    for parca in str(ad).split("_"):
        for kok in KOKLER:
            if parca.startswith(kok) and parca[len(kok):] in AD_EKLERI:
                return True
    return False


def test_OLUMSUZ_OLCU_YON_BEYANSIZ_KALAMAZ(schema):
    """🔴 Ölçüldü: `bakim_maliyeti` beyansızdı ve *«en kötü»* **en ucuzu** seçti."""
    eksik = []
    for c in (schema.get("cubes") or []):
        az = set(c.get("lower_is_better") or [])
        for m in (c.get("measures") or []):
            if m in az:
                continue
            if olumsuz_mu(str(m)):
                eksik.append(f"{c['name']}.{m}")
    assert not eksik, (
        "🔴 Adı olumsuz olan şu ölçülerde yön beyanı YOK — *«en kötü»* onlarda "
        "**tersine** cevaplanır (ölçüldü: `bakim_maliyeti` → en ucuz makine):\n  "
        + "\n  ".join(eksik)
        + "\n\nPack'te `lower_is_better: true` ekle. Ad gerçekten olumsuz değilse "
          "(ör. bir kazanç oranı) deseni daralt — ama gerekçesini yaz.")


def test_YUKLEM_KELIME_SINIRINA_BAKAR():
    """⚠ `§101.1` — ilk yazımım `ret` deseniyle *«u**ret**im»*i yakaladı ve üç yanlış
    pozitif üretti. Desen artık kelime sınırıyla aranıyor.

    *Bir kusuru arayan yüklem, kendi yanlış-pozitifini üretirse aradığından pahalıdır.*
    """
    for temiz in ("toplam_uretim_kg", "kazanma_orani_yuzde", "ges_uretimi_kwh",
                  "sevkiyat_adedi", "ort_oee"):
        assert not olumsuz_mu(temiz), f"yanlış pozitif: {temiz}"
    # ⊙ İkisi de **ek almış** hâller: kapı bunları kaçırırsa yeni bir `…maliyeti`
    # ölçüsü sessizce beyansız kalabilir.
    for kirli in ("bakim_maliyeti", "toplam_fire_kg", "ort_gecikme_gun",
                  "agir_sikayet_yuzde", "plansiz_durus_dakika", "nakliye_maliyeti",
                  "toplam_sikayeti"):
        assert olumsuz_mu(kirli), f"kaçırıldı: {kirli}"
