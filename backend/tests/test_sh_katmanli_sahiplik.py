"""🔴🔴 `§SH` — SAHİPLİK KARARI ARTIK ŞEMAYA ULAŞIYOR, VE YALNIZ DOĞRU TENANT'A.

## Ölçülen kusur (2026-08-11, `§F4` ölçümünün yan ürünü)

    demo/packs/cekirdek/sahiplik_kararlari.yml → 12 tarihli, gerekçeli İNSAN KARARI
    canlı şema  → metrik_kaydi VAR (62 çakışan terim)  ·  SAHİPLİ: 0
    hakem('elektrik') → None

Kayıt şemaya `onerilen_sahip` diye düşüyordu; `hakem()` ise `sahiplenilen_terimler`
okur. Yani hakem **kuruldu, bağlandı, bayrağı açıldı — ve hiç beslenmedi**.
`metrik_kaydi.py`'nin kendi cümlesi: *«Kurulmuş ama beslenemeyen bir hakem, kurulmamış
bir hakemdir.»*

## Ve öneriye indirme BİLİNÇLİYDİ — ölçüm doğruydu, TEŞHİS EKSİKTİ

`FAZ 3.1` kararları uyguladı → korpus **%93,2 → %92,6**, `gitas` erişim **%72 → %69**.
`3.1b` bundan *«pack kararı dayatılamaz»* sonucunu çıkardı. Gerçek sebep daha dardı:

> Sorun kararın *pack'ten* gelmesi değil, **çekirdekten** gelmesiydi. `elektrik`
> çakışması `enerji_makine` ⊕ `surdurulebilirlik` arasında ve **ikisi de boyahane
> sektöründe**; `gitas` (tarım-ticareti) o çakışmayı **hiç yaşamaz**.

Karar doğru katmana taşınınca dayatma bir politika değil bir **dizin yapısı** meselesi
olur — ve `gitas` dosyayı **hiç okumaz**. Bu dosyanın koruduğu şey odur.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

from app.metrik_kaydi import (
    hakem,
    katmanli_kararlar,
    pack_kararlari,
    sahiplikle_birlestir,
    semaya_yaz,
)

_DEMO = pathlib.Path(__file__).parent.parent / "demo"

_TASLAK = [
    {"terim": "elektrik", "adaylar": ["enerji_makine", "surdurulebilirlik"],
     "sahiplenilen_terimler": [], "olusturulma_yontemi": "otomatik_taslak"},
    {"terim": "satis", "adaylar": ["ticaret", "mal"],
     "sahiplenilen_terimler": [], "olusturulma_yontemi": "otomatik_taslak"},
]


# --- KATMAN ÇÖZÜMÜ ---------------------------------------------------------------

def test_BOYAHANE_kendi_kararini_ALIR():
    k = katmanli_kararlar(_DEMO, sektorler=["boyahane"], company="demo-boyahane")
    assert k.get("elektrik") == "enerji_makine"
    assert k.get("dogalgaz") == "enerji_makine"


def test_GITAS_boyahane_kararini_HIC_GORMEZ():
    """🔴 `FAZ 3.1`'in gerilemesinin yapısal panzehiri. Bu bir *filtre* değil: `gitas`
    boyahane paketini yüklemez, dosyayı **açmaz bile**."""
    assert katmanli_kararlar(_DEMO, sektorler=["tarim-ticareti"], company="gitas") == {}


@pytest.mark.parametrize("sektor,slug", [("geri-donusum", "atiksan"),
                                         ("kumas-ticareti", "gulteks")])
def test_DIGER_SEKTORLER_de_etkilenmez(sektor, slug):
    assert katmanli_kararlar(_DEMO, sektorler=[sektor], company=slug) == {}


def test_BAGLAMSIZ_okuma_HICBIR_karar_uygulamaz():
    """*Bağlamı olmayan bir katman kararı, en baştaki dayatmanın ta kendisi olurdu.*"""
    assert katmanli_kararlar(_DEMO) == {}


def test_CEKIRDEK_hala_ONERI_kalir():
    """⚠ Çekirdek bilerek katman listesinin DIŞINDA: oraya yazılan karar her tenant'a
    gider. Bilgi kaybolmaz — `pack_kararlari` onu okumaya devam eder."""
    oneri = pack_kararlari(_DEMO)
    assert oneri.get("elektrik") == "enerji_makine", "çekirdek dosyası silinmemeli"
    assert "elektrik" not in katmanli_kararlar(_DEMO), "çekirdek UYGULANMAMALI"


# --- HAKEME ULAŞIYOR MU ----------------------------------------------------------

def test_KARAR_hakeme_ULASIYOR():
    """Kusurun tam kalbi: karar `sahiplenilen_terimler`'e yazılmalı, `onerilen_sahip`'e
    değil — çünkü `hakem()` yalnız birincisini okur."""
    k = sahiplikle_birlestir(_TASLAK, {"elektrik": "enerji_makine"},
                             yontem="pack_karari")
    assert hakem("elektrik", k) == "enerji_makine"
    assert hakem("satis", k) is None, "kararı olmayan terim bugünkü yolda kalmalı"


def test_KOKEN_kaybolmaz():
    """`insan_karari` (tenant'ın çalışma-zamanı kararı) ile `pack_karari` (paketin
    beyanı) farklı şeylerdir; tek etikete indirmek kararı kimin verdiğini silerdi."""
    k = sahiplikle_birlestir(_TASLAK, {"elektrik": "enerji_makine"},
                             yontem="pack_karari")
    assert k[0]["olusturulma_yontemi"] == "pack_karari"
    v = sahiplikle_birlestir(_TASLAK, {"elektrik": "enerji_makine"})
    assert v[0]["olusturulma_yontemi"] == "insan_karari", "varsayılan DEĞİŞMEMELİ"


def test_ADAY_OLMAYAN_sahip_UYGULANMAZ_ama_GORUNUR():
    """*Sessizce yok saymak, kullanıcının kararını çöpe atıp ona söylememektir.*"""
    k = sahiplikle_birlestir(_TASLAK, {"elektrik": "oee"}, yontem="pack_karari")
    assert k[0]["sahiplenilen_terimler"] == []
    assert k[0]["gecersiz_sahip"] == "oee"


# --- KURAL B ---------------------------------------------------------------------

def test_BAYRAK_KAPALIYKEN_anahtar_HIC_yazilmaz():
    """`KURAL B` — kapalıyken `cube_router` kaydı hiç görmez → davranış birebir bugünkü."""
    s = {"cubes": [], "metrik_kaydi": ["eski"]}
    semaya_yaz(s, acik=False, base=_DEMO, sektorler=["boyahane"],
               company="demo-boyahane")
    assert "metrik_kaydi" not in s


def test_SEMAYA_YAZ_baglamsizken_bugunku_davranis():
    """Bağlam geçilmezse hiçbir sahiplik uygulanmaz — çağıranı güncellenmemiş bir kod
    yolu sessizce davranış değiştirmemeli."""
    s = {"cubes": []}
    semaya_yaz(s, acik=True, base=_DEMO)
    assert all(not k.get("sahiplenilen_terimler") for k in s["metrik_kaydi"])


# --- GÖVDE İDDİALARI (docstring'e DEĞİL) -----------------------------------------

def _govde(dosya: str, ad: str) -> str:
    src = (pathlib.Path(__file__).parent.parent / "app" / dosya).read_text(encoding="utf-8")
    for d in ast.walk(ast.parse(src)):
        if isinstance(d, ast.FunctionDef) and d.name == ad:
            g = d.body[1:] if (d.body and isinstance(d.body[0], ast.Expr)
                               and isinstance(d.body[0].value, ast.Constant)) else d.body
            return "\n".join(ast.dump(x) for x in g)
    raise AssertionError(f"{ad} bulunamadı")


def test_SEMAYA_YAZ_govdesi_katmanli_karari_CAGIRIYOR():
    g = _govde("metrik_kaydi.py", "semaya_yaz")
    assert "katmanli_kararlar" in g
    assert "sahiplikle_birlestir" in g
    assert "onerilerle_birlestir" in g, "çekirdek önerisi düşürülmemeli"


def test_SCHEMA_govdesi_TENANT_baglami_gecirir():
    g = _govde("wren_service.py", "schema")
    assert "_tenant_katmanlari" in g
    assert "sektorler" in g and "company" in g


# --- CANLI KATALOG ---------------------------------------------------------------

def test_CANLI_semada_hakem_ARTIK_karar_veriyor(schema):
    """🔴 Uçtan uca — ölçümden ÖNCE bu `None`'dı ve 264 yanlış-cube vakasının kökü buydu."""
    kayit = schema.get("metrik_kaydi")
    assert kayit, "metrik_kaydi bayrağı kapalı görünüyor"
    assert hakem("elektrik", kayit) == "enerji_makine"
    assert hakem("dogalgaz", kayit) == "enerji_makine"


def test_CANLI_KARARSIZ_terimler_bugunku_yolda(schema):
    """Kapsam kontrolü: yalnız iki terim taşındı; gerisi **değişmemeli**."""
    kayit = schema.get("metrik_kaydi") or []
    for t in ("bakiye", "satis", "tep", "borc"):
        assert hakem(t, kayit) is None, f"{t} için karar taşınmadı, uygulanmamalı"


# --- KAT-1: BEYAN, KARARLA ÇELİŞEMEZ ---------------------------------------------

def test_HAKEM_KARARI_ikame_SAYILMAZ(schema):
    """🔴 Canlıda ölçülen kusur (2026-08-11): `bu yıl elektrik tüketimi` doğru küpe
    (`enerji_makine`) gitti **ve yanına** *«…«elektrik» bu katalogda surdurulebilirlik
    konusudur — ama bu cevap enerji_makine küpünden geldi»* beyanı düştü.

    Sistem kendi verdiği kararı, aynı cevabın içinde bir **kusur olarak ilan etti**.
    `KAT-1`'in canlı ihlali: *«bu terim hangi küpün?»* sorusunun iki sahibi oldu."""
    from app.uyum import _kup_ikamesi
    cq = {"cube": "enerji_makine", "measures": ["toplam_elektrik_kwh"]}
    assert _kup_ikamesi("bu yil elektrik tuketimi", cq, schema) is None


def test_HAKEM_YOKSA_beyan_SUSMAZ(schema):
    """⚠ Kapsam kontrolü: susturma yalnız **ilan edilmiş sahip** için. Kararı olmayan bir
    terimde ikame beyanı aynen ateşlenmeli — yoksa düzeltme, bir körlük olurdu."""
    from app.uyum import _hakem_onayli
    assert _hakem_onayli("elektrik", "enerji_makine", schema) is True
    assert _hakem_onayli("elektrik", "surdurulebilirlik", schema) is False
    assert _hakem_onayli("bakiye", "cari", schema) is False, "kararsız terim susturmaz"


def test_IKINCI_ESLESTIRICI_YOK():
    """`KAT-1` — karar `metrik_kaydi.hakem`'den okunur, `uyum` kendi tablosunu kurmaz."""
    g = _govde("uyum.py", "_hakem_onayli")
    assert "hakem" in g and "SEMA_ANAHTARI" in g
