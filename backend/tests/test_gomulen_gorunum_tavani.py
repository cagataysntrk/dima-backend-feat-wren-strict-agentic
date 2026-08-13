"""🔴 `§50` — **GÖMÜLEN GÖRÜNÜM TAVANI**: soğuk maliyet sessizce büyümesin.

## Ölçülen kusur (canlı kesinti, 2026-08-13)

`§41` boyut değerlerini aday yaptı — doğru bir işti. Ama görünümler `534 → 1.359`'a
çıktı ve **vektör ayağına** girdi: `/oneri` canlıda **120 sn'de bile dönmedi**, kullanıcı
hiçbir öneri göremedi. Modülün kendi belgesi maliyeti yazmıştı (`534` görünüm ≈ `24,8` sn
soğuk); dört katı dakikalar eder.

*Bir maliyeti belgeye yazmak, onu ödememizi engellemiyor* — engelleyen şey **ilan edilmiş
bir tavandır** 🅜.

## Bu kapının iki yüklemi

| # | savunulan | ölçüm |
|---|---|---|
| 1 | gömülen görünüm sayısı **tavanın altında** | bugün **534** |
| 2 | **değer adayları gömülmez** (`§43`) | `#` taşıyan hiçbir aday matrise girmez 🆃 |

İkincisi birincisinin **sebebidir**: değerler gömülmeye başlarsa tavan zaten patlar. İkisi
ayrı yüklem olarak duruyor ki kırmızı **hangi kuralın** düştüğünü söylesin.

⚠ Tavan bugünkü ölçümün **üstünde** (`600`), altında değil: bir tavanın işi bugünü
kırpmak değil, **yarınki sessiz büyümeyi** yakalamaktır. Katalog meşru biçimde büyürse
tavan **gerekçesiyle** yükseltilir 🅝 — sessizce değil.
"""

from __future__ import annotations

from app import oneri

#: Gömülen görünüm tavanı. ⊙ Ölçüldü (2026-08-13, boyahane kataloğu): **534**.
#: Pay ~%12; katalog büyürse kapı **önce** kırmızı verir, kullanıcı **sonra** beklemez.
TAVAN = 600


def _gomulen_gorunumler(schema: dict) -> int:
    """Vektör ayağının **gerçekten** gömdüğü metin sayısı.

    ⚠ Ölçüt `_vektor_sira`'nın süzgeciyle **aynı** olmalı (`"#" not in kimlik`), yoksa
    kapı ürünün ölçmediği bir sayıyı savunur 🆩.
    """
    return sum(len(a.gorunumler or (a.etiket,))
               for a in oneri.terimler(schema, None) if "#" not in a.kimlik)


def test_GOMULEN_GORUNUM_TAVANI(schema):
    n = _gomulen_gorunumler(schema)
    assert n <= TAVAN, (
        f"🔴 gömülen görünüm {n} — tavan {TAVAN}.\n"
        "YAPILACAK: yeni adayları **leksik** ayakta tut (değer/ad aramaları harf işidir) "
        "ya da tavanı **gerekçesiyle** yükselt. ⚠ Bu sayı doğrudan SOĞUK BAŞLANGIÇtır: "
        "1.359 görünüm canlıda `/oneri`yi 120 sn asılı bıraktı.")


def test_DEGER_ADAYLARI_GOMULMEZ(schema):
    """🆃 `§43`'ün zıt ölçütü — değerler indekste **var**, matriste **yok**."""
    adaylar = oneri.terimler(schema, None)
    degerler = [a for a in adaylar if "#" in a.kimlik]
    assert degerler, "🔴 değer adayı hiç yok — `§41` geri alınmış olabilir"
    gomulen = _gomulen_gorunumler(schema)
    hepsi = sum(len(a.gorunumler or (a.etiket,)) for a in adaylar)
    assert gomulen < hepsi, (
        "🔴 değer adayları da gömülüyor — `§43` düştü ve soğuk maliyet patlayacak")
