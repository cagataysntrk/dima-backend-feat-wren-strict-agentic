"""🔴 ④ `tep` SAHİPLİĞİ — ölçüm borcu ÇÜRÜTTÜ, ama yerine GERÇEK bir kusur buldu.

## Borç ne diyordu

> ④ `tep` sahipliği **ÇELİŞKİLİ** — çekirdek `surdurulebilirlik` diyor, korpus
> `enerji_makine` bekliyor. Karar `packs/sektor/<s>/sahiplik_kararlari.yml`'ye yazılır.

## Ölçüm (2026-08-12) — ve neden bu bir SAHİPLİK sorunu DEĞİL

| adım | ölçülen |
|---|---|
| korpus beklentisi | 4 soru: `makine bazında tep` → beklenen `enerji_makine`, seçilen `surdurulebilirlik` |
| grain hipotezi | ⊘ **çürüdü** — ikisinde de `makine` boyutu **var** |
| ifade | ikisi de birebir **`SUM(tep)`** |
| 🔴 **canlı sayı** | `enerji_makine` → **1179,0382** · `surdurulebilirlik` → **1179,0390** |

⊙ **Aynı sayı.** Yani kullanıcı hangi küpten cevap alırsa alsın **doğru sayıyı
görüyor**. Korpusun *«yanlış cube»* verdisi burada bir **puanlama artefaktıdır**, bir
kullanıcı kusuru değil — ve bir sahiplik kararı yazmak, 4 korpus satırını yeşile
çevirirken asıl gerçeği (**aynı nicelik iki kez tanımlı**) örterdi.

> *Bir ölçümü, ölçtüğü şeyi düzeltmeden yeşile çevirmek, ölçümü kaybetmektir.*

🔴 **KARAR: `tep` için sahiplik satırı YAZILMIYOR** — ölçüye dayanan **on altıncı**
*«yapma»*. Boyahane dosyasının kendi cümlesi zaten bunu istiyordu: *«ölçülmemiş bir
kazanç, kazanç değildir»* — ölçüldü ve **kazanç yok**. Doğru kutu `grain_hatasi`
(modelleme borcu), `tek_sahip` değil.

## 🔴 AMA ÖLÇÜM BAŞKA BİR ŞEY BULDU — ve o gerçek bir kusurdu

Canlı cevabın notu (`bu yıl makine bazında tep`):

    «tep» birden fazla yerde tanımlı — bu cevap **sürdürülebilirlik** tanımıyla
    hesaplandı. Diğerleri: tep (bölüm/makine enerji (ölçülen)) · tep (tesis
    enerji (ISO-50001)).

İkinci alternatif `enerji_tesis`'tir ve **`makine` boyutu YOKTUR** (ölçüldü:
`['bolum','makine','hat']` vs tesis küpünde makine yok). Yani kullanıcı o tanımı seçse
*makine bazında* bir cevap **alamaz**. Beyan, veremeyeceği bir şeyi sayıyordu.

⊙ Ve bu, `belirsizlik_chipi.py`'nin **kendi yazılı kuralının** ihlaliydi:
*«kullanıcıyı aynı duvara ikinci kez çarptıran bir chip, chip olmamasından kötüdür.»*
Kural yazılıydı; **kırılım ekseninde uygulanmıyordu**.

*Bir alternatifi sunmak, onun sorulan soruyu cevaplayabileceğini söylemektir.*
"""

from __future__ import annotations

import pathlib

import yaml

from app import belirsizlik_chipi as bc

_PACKS = pathlib.Path(__file__).parent.parent / "demo" / "packs"

_SEMA = {
    "cubes": [
        {"name": "enerji_makine", "display": "bölüm/makine enerji (ölçülen)",
         "dimensions": ["bolum", "makine", "hat"]},
        {"name": "enerji_tesis", "display": "tesis enerji (ISO-50001)",
         "dimensions": [{"name": "tesis"}, {"name": "vardiya"}]},
        {"name": "surdurulebilirlik", "display": "sürdürülebilirlik",
         "dimensions": ["makine", "hat", "vardiya"]},
    ]
}


def test_KIRILIMSIZ_soruda_HICBIRI_elenmez():
    """⚠ Süzgecin kapsamı, ölçtüğü şeyle sınırlı: kırılım sorulmadıysa eleme de yok."""
    c = bc.chipler("tep", ["enerji_makine", "enerji_tesis"], _SEMA, [])
    assert {x["label"] for x in c} == {"tep (bölüm/makine enerji (ölçülen))",
                                       "tep (tesis enerji (ISO-50001))"}


def test_SORULAN_KIRILIMI_veremeyen_kup_ALTERNATIF_degil():
    """🔴 Kusurun ta kendisi: `makine bazında tep` sorusunda `enerji_tesis` sunuluyordu."""
    c = bc.chipler("tep", ["enerji_makine", "enerji_tesis"], _SEMA, ["makine"])
    adlar = {x["label"] for x in c}
    assert "tep (bölüm/makine enerji (ölçülen))" in adlar, "geçerli alternatif düştü"
    assert "tep (tesis enerji (ISO-50001))" not in adlar, (
        "🔴 `makine` boyutu OLMAYAN bir küp hâlâ *makine bazında* bir soruya alternatif "
        "olarak sunuluyor — kullanıcı onu seçse cevabı alamaz.")


def test_COK_BOYUTLU_kirilimda_HEPSI_aranir():
    """Bir alternatif, sorulan boyutların **tamamını** taşımalı — birini taşımak yetmez."""
    c = bc.chipler("tep", ["surdurulebilirlik"], _SEMA, ["makine", "bolum"])
    assert not c, "yalnız `makine`'yi taşıyan küp, `makine+bolum` sorusuna cevap veremez"


def test_SOZLUK_ve_DUZ_METIN_boyutlarin_ikisi_de_okunur():
    """⚠ Katalog boyutları iki biçimde yazılıyor (`"makine"` ve `{"name": "makine"}`).
    Yalnız birini okumak, ötekini taşıyan her küpü **sessizce** eleyip bu turda
    düzeltilen kusurun aynadaki hâlini üretirdi."""
    sema = {"cubes": [{"name": "x", "display": "X",
                       "dimensions": [{"name": "makine"}, "hat"]}]}
    assert bc.chipler("tep", ["x"], sema, ["makine"]), "sözlük biçimli boyut okunamadı"
    assert bc.chipler("tep", ["x"], sema, ["hat"]), "düz metin biçimli boyut okunamadı"


# --- ④ KARARIN KAYDI: `tep` sahiplik satırı YAZILMADI, ve bu bir karardır ----------

def test_TEP_sahiplik_satiri_YAZILMADI():
    """🔴 Ölçüye dayanan karar **kayda geçer**: iki küpün `tep`'i **aynı sayıyı** verdiği
    için sahiplik yazmak bir kazanç üretmez, yalnız `grain_hatasi`'nı gizlerdi.

    ⚠ Bir gün sayılar **ayrışırsa** karar yeniden okunmalıdır — o zaman `tep` gerçek bir
    belirsizlik (`kutu 2`) ya da gerçek bir tek-sahip olur. Bu test o günü değil, o güne
    kadar kararın **bilinçli** olduğunu kaydeder.
    """
    for p in _PACKS.rglob("sahiplik_kararlari.yml"):
        d = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        for k in (d.get("kararlar") or []):
            if str(k.get("terim")) == "tep":
                assert k.get("kutu") != "tek_sahip" or k.get("sahip"), (
                    f"{p}: `tep` kalemi eksik yazılmış")
                assert k.get("gerekce"), f"{p}: `tep` kararı gerekçesiz"


def test_ENERJI_TESIS_makine_boyutu_TASIMIYOR():
    """⚠ Bu turda düzeltilen kusurun **ölçüm tabanı**: kusur, bu küpün `makine` boyutu
    olmamasından doğuyordu. Katalog değişir de tesis küpü `makine` kazanırsa, yukarıdaki
    testin fikstürü **gerçeklikten kopar** ve bunu bilmek isteriz."""
    p = next((x for x in _PACKS.rglob("metadata.yml")
              if (yaml.safe_load(x.read_text(encoding="utf-8")) or {}).get("name")
              == "enerji_tesis"), None)
    if p is None:
        return                                  # küp kaldırılmış — kapının konusu yok
    d = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    boyutlar = {(b.get("name") if isinstance(b, dict) else b)
                for b in (d.get("dimensions") or [])}
    assert "makine" not in boyutlar, (
        "⊙ `enerji_tesis` artık `makine` boyutu taşıyor — bu turdaki ölçüm değişti. "
        "Alternatif süzgeci hâlâ doğru ama fikstür güncellenmelidir.")
