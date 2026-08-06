"""🔴 KÖK-7d / KÇ-10 — **TÜRETME KATMANI**, fail-closed. (denetim raporu KN-8)

## Ölçülen kusur

Katalog yalnız **İSİM** biçimini biliyor; kullanıcı **FİİL** kuruyor:

| kullanıcının kelimesi | katalog | bugün |
|---|---|---|
| `sattık` | `satış` → `parti.toplam_ciro` | **R10** |
| `ürettik` | `üretim` · `üretilen` | **R10** |
| `alacağımız` | `alacak` → `cari.toplam_alacak` | **R10** |

`_ek_gecerli` **ÇEKİMİ** çözer (satış→satışı); bunlar **TÜRETME**dir (sat‑→satış) —
farklı bir dilbilimsel işlem, depoda karşılığı yoktu.

## 🔴 FAIL-CLOSED — kapsam riski YAPISAL olarak sıfır

Raporun uyarısı: *"türetme anlamı kaydırabilir (`al-`→`alacak` ✓ ama `al-`→`alıcı`
boyut)."* Bu katman **cevap üretmez**, yalnız **chip** üretir; `route()` onu hiç görmez.

⚠ Ve bu, KÖK-7b'nin ölçülmüş dersidir: 7b kapsamı **açarak** benzer bir sınıfı kapatmayı
denedi, ölçütü tutturdu (§4 probu %31,2 → %90+) ama gerçek-dünya **kabul 1150 → 1117**,
**sessiz_yanlis 12 → 30** oldu. *Bir ölçütü tutturmak, ölçütün ölçmediği şeyi bozmama
garantisi vermez.* 7d aynı hatayı **yapamaz**.

## ⊙ İki ölçüm, iki düzeltme

| tur | korpusta chip üreten | neden |
|---|---|---|
| 1 | **191 / 2 116 (%9,0)** — çoğu **SAHTE** | kelimenin **kendisi** de aday sayılıyordu → `may`→`prim`, `ogrnim`→`kar oranı` |
| **2** | 🟢 **0** | kullanıcı tarafı **gerçek bir çekim** soymak zorunda |

🔴 Ve *"fail-closed olduğu için zararsız"* savunması **reddedildi**: *"prim mi demek
istedin?"* diye soran bir chip kullanıcıyı yanlış yere bakmaya davet eder.
**Bir tahminin ucuz olması, yanlış olmasını ucuzlaştırmaz.**

⊘ Korpus bu sınıfı **ölçemez** — soruları katalogdan üretiliyor, hepsi isim biçiminde.
Bu, `CLAUDE.md`'de yazılı *"korpusun bilinen körlüğü"*nün bir başka yüzü.
"""

from __future__ import annotations

import pytest

from app import turetme as t
from tests.conftest import ask

#: Raporun adıyla saydığı üç vaka.
HEDEF = [("bu yil ne kadar sattik", "sattik"),
         ("gecen ay ne kadar urettik", "urettik"),
         ("ne kadar alacagimiz var", "alacagimiz")]


@pytest.mark.parametrize("q,kelime", HEDEF)
def test_HEDEF_TURETME_ADAYI_URETIYOR(q, kelime, schema):
    """🔴 **ASIL KAPI** — raporun ölçütü: `ne kadar sattık` → `satis_tutari` ya da chip."""
    assert t.adaylar([kelime], schema), f"🔴 «{kelime}» için türetme adayı yok"


def test_SAHTE_TURETME_YOK(schema):
    """🔴 **İlk turun 191 sahte adayının kapısı.** Kelimenin kendisi aday olamaz:
    kullanıcı tarafı GERÇEK bir çekim soymak zorunda — çekimsiz bir token zaten
    `_syn_hit`in işidir ve orada eşleşmediyse burada da eşleşmemeli."""
    for kelime in ("iade", "may", "istan", "ogrnim", "vat", "tep"):
        assert not t.adaylar([kelime], schema), \
            f"🔴 «{kelime}» sahte türetme üretiyor: {t.adaylar([kelime], schema)}"


def test_HAFIF_FIIL_DISARIDA(schema):
    """🔴 Ölçülen anlam kayması: `fire verdik` → `verdik` → kök `ver` → katalog `verim`
    → chip **«oee»**. Oysa *"fire vermek"* = fire ÜRETMEK.

    ⚠ `ver-`/`et-`/`ol-`/`yap-` **hafif fiillerdir**: kendi anlamlarını taşımaz,
    yanlarındaki isme bağlanırlar. Kapalı bir dilbilgisi sınıfı — kelime listesi değil."""
    assert not t.adaylar(["verdik"], schema), "🔴 hafif fiilden türetme yapılıyor"
    assert not t.adaylar(["ettik"], schema)
    assert "ver" in t._HAFIF_FIIL and "al" in t._HAFIF_FIIL


def test_KOK_UZUNLUGU_RISKI_ERITIYOR():
    """🔴 Raporun adıyla uyardığı vaka (`al-`→`alacak` ✓ ama `al-`→`alıcı` BOYUT) iki
    ayrı şartla eleniyor: `al` iki harf (< `EN_AZ_KOK`) **ve** hafif fiil.
    *Bir riski kural içinde eritmek, ona ayrı bir istisna yazmaktan sağlamdır.*"""
    assert t.EN_AZ_KOK >= 3
    assert not t._kokler("aldik", t._FIIL_CEKIMI, kendisi=False)


def test_YUMUSAMA_GERI_ALINIYOR():
    """`alacağ`+`ımız` → `alacak`. Türkçede son-ünsüz yumuşaması ünlüyle başlayan ek
    geldiğinde **zorunludur**; geri alması da o kadar kuralldır."""
    assert "alacak" in t._kokler("alacagimiz", t._FIIL_CEKIMI, kendisi=False)


def test_COK_KELIMELI_SINONIM_ATLANIYOR(schema):
    """⚠ *"satış tutarı"* hangi kelimeden türedi? Belirsiz — ve **fail-closed** bir
    katmanda belirsizlik eklemek, katmanın var olma sebebine aykırıdır."""
    for a in t.adaylar(["sattik"], schema):
        assert a["kind"] == t.TUR_TURETME


def test_AYNI_ETIKET_IKI_KEZ_GELMIYOR(schema):
    """⚠ Ölçüldü: `alacağımız` iki cube'un (`cari` · `mizan`) aynı adlı ölçüsüne iniyor
    ve kullanıcı **aynı chip'i iki kez** görüyordu. *Aynı seçeneği iki kez göstermek,
    seçeneği bir karara değil bir gürültüye çevirir.*"""
    ad = t.adaylar(["alacagimiz"], schema)
    assert len(ad) == len({a["label"] for a in ad})


def test_BOS_GIRDI_SESSIZ(schema):
    assert t.adaylar([], schema) == [] and t.adaylar(["x"], {}) == []
    assert t.not_metni([], 0) == ""
    assert "«»" not in t.not_metni([], 2), "🔴 boş tırnak basılıyor"


# ═══════════════════════════════════════════════════════════════════════════════
# UÇTAN UCA — ve FAIL-CLOSED sözleşmesi
# ═══════════════════════════════════════════════════════════════════════════════

def test_UCTAN_UCA_CHIP_GORUNUYOR(client):
    """🔴 Chip **kullanıcıya ulaşıyor** mu — ve `kind="turetme"` ile mi?

    ⚠ İlk kanca yalnız *kısmi-anlama* dalına takılmıştı ve ölçüldü: `ne kadar sattık`
    o daldan geçmiyor (katalog-dökümü dalına düşüyor) → chip hiç görünmüyordu.
    *Bir kancayı doğru yere takmak, doğru kancayı yazmak kadar iştir.*"""
    d = ask(client, "bu yıl ne kadar sattık")
    assert d.get("source") is None, "⊘ vaka bayatlamış — soru artık cevaplanıyor"
    turler = [s.get("kind") for s in (d.get("suggestions") or [])]
    assert t.TUR_TURETME in turler, f"🔴 türetme chip'i ekrana gitmiyor: {turler}"


def test_FAIL_CLOSED_CEVAP_URETMIYOR(client):
    """🔴 **Sözleşmenin kendisi**: türetme bir CEVAP üretmemeli. `source` `None` kalmalı,
    satır dönmemeli. *En kötü senaryo bir fazla chip'tir, bir yanlış sayı değil.*"""
    for q in ("bu yıl ne kadar sattık", "ne kadar alacağımız var"):
        d = ask(client, q)
        assert d.get("source") is None, f"🔴 «{q}» türetmeden CEVAP üretti"
        assert not (d.get("result") or {}).get("row_count"), f"🔴 «{q}» satır döndürdü"


def test_ROUTE_TURETMEYI_GORMUYOR():
    """🔴 Kapsam riskinin **yapısal** güvencesi: `cube_router` bu modülü import ETMEMELİ.
    Bir gün ederse, fail-closed sözleşmesi sessizce delinmiş olur."""
    import pathlib

    from app import cube_router as cr

    src = pathlib.Path(cr.__file__).read_text(encoding="utf-8")
    assert "turetme" not in src, "🔴 route() türetme katmanını görüyor — fail-closed delindi"
