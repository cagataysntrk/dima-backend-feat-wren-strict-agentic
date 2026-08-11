"""🔴🔴 `§KN` — **BİR SAYI, NEDEN DÜŞÜK OLDUĞUNU FORMÜLÜNDE SAKLAR.**

## Kullanıcının şartı (2026-08-11)

> *«Neden sorusu geldiğinde adeta insan zihnini simüle etmeliyiz… o formülde paydaki
> değerler arttıkça değer büyür, payda arttıkça değer düşer… ya payı düşürenleri
> bulmalıyım ya paydayı diğerlerine göre daha yüksek yapan bileşenleri… en dibe indim ve
> gördüm ki vardiya 1'de malzeme bekleme nedeniyle bu makine çok durmuş.»*

## Ve kök kataloğun içinde yazılıydı

`oee` küpü ölçüldü: `ort_oee`'nin ifadesi, üç ayrı ölçünün ifadelerinin **birebir
çarpımıdır**. Yani bileşen keşfi bir SQL cebiri değil, kataloğun kendi metninde bir
**üst-düzey işlenen eşitliğidir**.
"""

import math

import pytest

from app import kok_neden as kn

#: Gerçek `oee` kataloğunun birebir kopyası (ölçüldü, uydurulmadı).
_OEE = {
    "name": "oee",
    "measure_expressions": {
        "ort_oee": ("(1.0*SUM(calisma_suresi_dk)/NULLIF(SUM(planli_uretim_suresi_dk),0))"
                    " * (SUM(performans_PV*planli_uretim_suresi_dk)"
                    "/NULLIF(SUM(planli_uretim_suresi_dk),0))"
                    " * (1.0*SUM(uretim_kg - hatali_kg)/NULLIF(SUM(uretim_kg),0))"),
        "ort_kullanilabilirlik": "1.0*SUM(calisma_suresi_dk)/NULLIF(SUM(planli_uretim_suresi_dk),0)",
        "ort_performans": ("SUM(performans_PV*planli_uretim_suresi_dk)"
                           "/NULLIF(SUM(planli_uretim_suresi_dk),0)"),
        "ort_kalite": "1.0*SUM(uretim_kg - hatali_kg)/NULLIF(SUM(uretim_kg),0)",
        "toplam_uretim_kg": "SUM(uretim_kg)",
    },
    "measure_synonyms_display": {"ort_kullanilabilirlik": "kullanılabilirlik",
                                 "ort_performans": "performans", "ort_kalite": "kalite"},
}


def test_UC_FAKTOR_BULUNUR():
    """🔴 **Kapının kalbi** — formül kataloğun içinde okundu, çözümlenmedi."""
    adlar = [b.ad for b in kn.bilesenler("ort_oee", _OEE)]
    assert adlar == ["ort_kullanilabilirlik", "ort_performans", "ort_kalite"]


def test_ALT_DIZE_YANLIS_POZITIFI_ELENIR():
    """🔴🔴 **İlk koşumda ölçülen kusur.** `toplam_uretim_kg = SUM(uretim_kg)` ve o dizi
    `NULLIF(SUM(uretim_kg),0)`'ın **içinde** geçiyor — yani bir çarpan değil, kalite
    faktörünün **paydası**. İlk yazımım onu `carpan` diye bileşen sayıyordu: kullanıcıya
    *«üretim kg, OEE'nin çarpanıdır»* denecekti.

    *Bir parçayı bir bütünün içinde görmek, onun o bütünü oluşturduğunu göstermez.*"""
    assert "toplam_uretim_kg" not in [b.ad for b in kn.bilesenler("ort_oee", _OEE)]


def test_CARPIMIN_ILK_TERIMI_PAY_DEGIL_CARPANDIR():
    """⚠ Bir çarpımın ilk terimine *«pay»* demek, doğru yönü söyleyip **yanlış adı**
    vermektir — ve kullanıcı adı okur."""
    assert all(b.rol == kn.CARPAN for b in kn.bilesenler("ort_oee", _OEE))


def test_PAYDA_YONU_EKSI():
    """🔴 Kullanıcının cümlesinin birebir karşılığı: *«payda arttıkça değer düşer»*."""
    meta = {"measure_expressions": {"oran": "SUM(a)/SUM(b)", "pay": "SUM(a)",
                                    "payda_olcu": "SUM(b)"}}
    bl = {b.ad: b for b in kn.bilesenler("oran", meta)}
    assert bl["pay"].yon == 1 and bl["payda_olcu"].yon == -1
    assert bl["payda_olcu"].rol == kn.PAYDA


def test_TEK_BILESEN_AYRISTIRMA_DEGILDIR():
    """⚠ Tek bileşen, ölçünün kendisiyle aynı şeydir — bir açıklama üretmez."""
    meta = {"measure_expressions": {"x": "SUM(a)*2", "y": "SUM(a)"}}
    assert kn.bilesenler("x", meta) == []


def test_LOG_AYRISTIRMASI_TAM_TOPLANIR():
    """🔴🔴 **Bu bir sezgi değil bir ÖZDEŞLİK.** Çarpımsal bir ölçüde faktör katkıları
    log uzayında **artıksız** toplanır:

        ln(v_hedef) − ln(v_akran) = Σ [ ln(f_i,hedef) − ln(f_i,akran) ]

    Bu test o eşitliği sayıyla doğrular; tutmazsa yüzdeler bir **uydurma** olurdu."""
    hedef = {"ort_oee": 0.9 * 0.8 * 0.95, "ort_kullanilabilirlik": 0.9,
             "ort_performans": 0.8, "ort_kalite": 0.95}
    akran = {"ort_oee": 0.95 * 0.85 * 0.97, "ort_kullanilabilirlik": 0.95,
             "ort_performans": 0.85, "ort_kalite": 0.97}
    ayr = kn.ayristir("ort_oee", hedef, akran, _OEE)
    assert ayr is not None
    toplam = sum(k.katki for k in ayr.katkilar)
    beklenen = math.log(hedef["ort_oee"]) - math.log(akran["ort_oee"])
    assert abs(toplam - beklenen) < 1e-9, "🔴 ayrıştırma ARTIK bırakıyor"


def test_EN_COK_DUSUREN_SUCLU_SECILIR():
    """⚠ Derinleşmenin bir sonraki adımı **ölçülmüş** en büyük düşürücüdür."""
    hedef = {"ort_oee": 0.5, "ort_kullanilabilirlik": 0.60,
             "ort_performans": 0.95, "ort_kalite": 0.99}
    akran = {"ort_oee": 0.8, "ort_kullanilabilirlik": 0.90,
             "ort_performans": 0.96, "ort_kalite": 0.99}
    ayr = kn.ayristir("ort_oee", hedef, akran, _OEE)
    assert ayr.sucllu.ad == "ort_kullanilabilirlik"
    assert ayr.katkilar[0].pay_yuzde > 80


def test_TANIMSIZ_YERDE_ZORLANMAZ():
    """*Bir yöntemi tanımsız olduğu yerde zorlamak, bir sayı üretir ama bir bilgi
    üretmez* — sıfır/negatif bileşende ayrıştırma YOK."""
    hedef = {"ort_oee": 0, "ort_kullanilabilirlik": 0.0,
             "ort_performans": 0.9, "ort_kalite": 0.9}
    akran = {"ort_oee": 0.8, "ort_kullanilabilirlik": 0.9,
             "ort_performans": 0.9, "ort_kalite": 0.9}
    assert kn.ayristir("ort_oee", hedef, akran, _OEE) is None


def test_ANLATI_YOLU_ANLATIR():
    """🔴 Kullanıcının şartı: *«şuna baktım, şuraya gittim, şöyle olduğunu gördüm»*."""
    hedef = {"ort_oee": 0.5, "ort_kullanilabilirlik": 0.60,
             "ort_performans": 0.95, "ort_kalite": 0.99}
    akran = {"ort_oee": 0.8, "ort_kullanilabilirlik": 0.90,
             "ort_performans": 0.96, "ort_kalite": 0.99}
    metin = kn.anlati(kn.ayristir("ort_oee", hedef, akran, _OEE),
                      segment="RAM-3", boyut="makine")
    assert "RAM-3" in metin and "kullanılabilirlik" in metin and "%" in metin
    assert "akran" in metin


def test_ANLATI_DEGER_YARGISI_VERMEZ():
    """🔴 `GG8` — bir değer yargısı, ölçünün **yönü beyan edilmeden** verilemez. Bu
    modül *«kötü»* demez, *«daha düşük»* der."""
    hedef = {"ort_oee": 0.5, "ort_kullanilabilirlik": 0.60,
             "ort_performans": 0.95, "ort_kalite": 0.99}
    akran = {"ort_oee": 0.8, "ort_kullanilabilirlik": 0.90,
             "ort_performans": 0.96, "ort_kalite": 0.99}
    metin = kn.anlati(kn.ayristir("ort_oee", hedef, akran, _OEE),
                      segment="RAM-3", boyut="makine")
    for yargi in ("kötü", "berbat", "başarısız", "iyi değil"):
        assert yargi not in metin.lower()


@pytest.mark.parametrize("olcu", ["yok_olcu", "toplam_uretim_kg"])
def test_BILESENSIZ_OLCU_SESSIZ(olcu):
    assert kn.bilesenler(olcu, _OEE) == []
    assert kn.ayristir(olcu, {}, {}, _OEE) is None


# --- TAM TUR · «şuna baktım, şuraya gittim, gördüm ki…» ------------------------------

_SATIRLAR = [
    {"makine": "RAM-1", "ort_oee": 0.60, "ort_kullanilabilirlik": 0.90,
     "ort_performans": 0.70, "ort_kalite": 0.95},
    {"makine": "RAM-2", "ort_oee": 0.62, "ort_kullanilabilirlik": 0.91,
     "ort_performans": 0.72, "ort_kalite": 0.95},
    {"makine": "RAM-3", "ort_oee": 0.45, "ort_kullanilabilirlik": 0.89,
     "ort_performans": 0.53, "ort_kalite": 0.95},
]
_ALT = {  # RAM-3 içinde: `hat` SABİT (tek satır), `vardiya` ayrışıyor
    "hat": [{"hat": "RAM 3", "ort_performans": 0.53}],
    "vardiya": [{"vardiya": "1. Vardiya", "ort_performans": 0.38},
                {"vardiya": "2. Vardiya", "ort_performans": 0.61},
                {"vardiya": "3. Vardiya", "ort_performans": 0.60}],
}
_META = {**_OEE, "dimensions": ["hat", "vardiya"], "lower_is_better": [],
         "dimension_labels": {"vardiya": "vardiya", "hat": "hat"}}


def _kos(cq):
    """Sahte koşucu — modül **sorgu koşmadığı** için testte gerçek motor gerekmez."""
    dims = cq.get("dimensions") or []
    if dims == ["makine"]:
        return _SATIRLAR
    return _ALT.get(dims[0] if dims else "", [])


def test_TAM_TUR_EN_DIBE_INER():
    """🔴🔴 **Kullanıcının şartının kendisi**: formülü oku → akranla kıyasla → suçluyu
    bul → onun içinde en dibe in.

        «en dibe indim ve gördüm ki vardiya 1'de … bu makine çok durmuş»"""
    prev = {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["makine"],
            "filters": [{"dimension": "tarih", "operator": "gte", "value": "2026-01-01"}]}
    out = kn.arastir(prev, _META, kos=_kos)
    assert out is not None
    assert "RAM-3" in out["anlati"]
    assert "performans" in out["anlati"]
    assert "1. Vardiya" in out["anlati"], "🔴 derinleşme yok"
    assert any("formül okundu" in a for a in out["adimlar"])
    assert any("vardiya" in a for a in out["adimlar"])


def test_SABIT_KIRILIM_SECILMEZ():
    """🔴🔴 **Gerçek katalogda ölçülen kusur.** İlk yazımda derinleşme `adaylar[0]`'ı
    alıyordu ve o `hat` çıktı — `hat` bir makinenin **içinde sabittir** (makine bir
    hatta aittir), tek satır döner ve derinleşme **hiç üretilmedi**.

    Sıra listesi bunu bilemez: `available_dimensions` maliyet/güven sıralar, hiyerarşi
    bilmez. *Bir kırılımı denemeden seçmek, hiyerarşiyi bildiğini varsaymaktır.*"""
    prev = {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["makine"], "filters": []}
    out = kn.arastir(prev, _META, kos=_kos)
    assert "1. Vardiya" in out["anlati"] and "RAM 3" not in out["anlati"].split("içinde")[-1]


def test_DERINLESILINCE_GENEL_KUYRUK_YAZILMAZ():
    """⚠ Derinleşme **gerçekten** yapıldıysa *«bir sonraki adım onu açmak»* demek,
    yapılan işi bir plan gibi sunmaktır."""
    prev = {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["makine"], "filters": []}
    out = kn.arastir(prev, _META, kos=_kos)
    assert "Bir sonraki adım" not in out["anlati"]


def test_KULLANICININ_SECTIGI_SEGMENT_ONCELIKLI():
    """⚠ Kullanıcı bir segment adı verdiyse **o** incelenir; sistemin seçtiği en aykırı
    değil. *Sorulmayan soruyu cevaplamak, cevap vermemekten farklı bir kusurdur.*"""
    prev = {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["makine"], "filters": []}
    out = kn.arastir(prev, _META, kos=_kos, segment="RAM-1")
    assert out["segment"] == "RAM-1"


def test_TEK_SEGMENTTE_KIYAS_YOK():
    """*Bir akran kıyası, akran olmadan kurulamaz.*"""
    prev = {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["makine"], "filters": []}
    assert kn.arastir(prev, _META, kos=lambda cq: _SATIRLAR[:1]) is None


def test_BOYUTSUZ_SORUDA_SESSIZ():
    """⚠ Kesitsel *«neden»* bir **kırılım** ister: tek bir toplamın akranı yoktur."""
    prev = {"cube": "oee", "measures": ["ort_oee"], "filters": []}
    assert kn.arastir(prev, _META, kos=_kos) is None
