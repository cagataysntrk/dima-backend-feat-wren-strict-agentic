"""FAZ 2.5 — **HEDEF KIYASI** kapısı. [bayrak yok: değişmez]

## Ölçülen durum — ve neyin kusur OLMADIĞI

`viz.py` referans çizgisini `{"kind": "average"}` üretiyor, `chart.ts` onu `Ort.` diye
etiketliyor: **yanlış etiketleme YOK**, sistem bugün dürüst. Eksik olan **mekanizmanın
kendisi** — `target:` beyanı hiçbir cube'da yoktu, yani kullanıcı *"hedefimin altında
mıyım"* diye soramıyor, grafikte gördüğü çizgi her zaman **kendi ortalaması** oluyordu.

## 🔴 DEĞİŞMEZ: HEDEF UYDURULMAZ

*"Hedef yok"* ile *"hedef 0"* asla karıştırılmaz: sıfır hedef **ulaşılmış** bir hedeftir,
hedefsizlik ise **ölçülemezliktir**.
"""

from __future__ import annotations

import pathlib

from app import hedef as H
from app import viz

KOK = pathlib.Path(__file__).resolve().parents[1]
FE = KOK.parent / "dima-frontend-demo-master" / "src"

_SEMA = {"cubes": [{"name": "oee", "hedefler": {"ort_oee": 85.0, "fire_orani": 2.0},
                    "lower_is_better": ["fire_orani"]}]}


# ── 1 · HEDEF UYDURULMAZ ────────────────────────────────────────────────────

def test_BEYAN_YOKSA_HEDEF_YOK():
    """🔴 **Maddenin değişmezi.** Beyan yoksa `None` — ve çağıran bunu *"hedef 0"* diye
    okuyamaz."""
    assert H.beyan(_SEMA, "oee", "olmayan_olcu") is None
    assert H.beyan(_SEMA, "olmayan_cube", "ort_oee") is None
    assert H.blok(_SEMA, {"cube": "oee", "measures": ["olmayan"]},
                  {"rows": [{"olmayan": 5}]}) is None


def test_BOZUK_BEYAN_HEDEF_SAYILMIYOR():
    """⚠ Bozuk bir beyanı `0` kabul etmek, *"hedef yok"* ile *"hedef 0"* ayrımını yok
    ederdi — ve kullanıcı **ulaşılmış** bir hedef görürdü."""
    sema = {"cubes": [{"name": "x", "hedefler": {}}]}
    assert H.beyan(sema, "x", "m") is None


def test_SIFIR_HEDEF_GECERLI_ve_YUZDE_TANIMSIZ():
    """🔴 Sıfır **geçerli bir hedeftir** (ulaşılmış). Ama sapma yüzdesi **tanımsızdır** —
    `inf`/`0` yazmak, bir tanımsızlığı bir ölçüm gibi gösterirdi."""
    sema = {"cubes": [{"name": "x", "hedefler": {"kaza": 0.0},
                       "lower_is_better": ["kaza"]}]}
    b = H.blok(sema, {"cube": "x", "measures": ["kaza"]}, {"rows": [{"kaza": 0}]})
    assert b["hedef"] == 0.0 and b["ulasildi"] is True
    assert b["sapma_yuzde"] is None


# ── 2 · YÖN, İKİNCİ KEZ BEYAN EDİLMİYOR ─────────────────────────────────────

def test_YON_LOWER_IS_BETTER_DAN_TURUYOR():
    """⚠ İkinci bir yön beyanı yazmak, iki yönün **ayrışması** demekti — biri *"85 iyi"*
    derken öteki *"85 kötü"* gösterirdi."""
    assert H.yon(_SEMA, "oee", "fire_orani") == H.YON_DUSUK_IYI
    assert H.yon(_SEMA, "oee", "ort_oee") == H.YON_YUKSEK_IYI
    alt = H.blok(_SEMA, {"cube": "oee", "measures": ["fire_orani"]},
                 {"rows": [{"fire_orani": 1.5}]})
    assert alt["ulasildi"] is True, "düşük-iyi ölçüde hedefin ALTI başarıdır"


def test_HEDEFE_ULASILMADI():
    b = H.blok(_SEMA, {"cube": "oee", "measures": ["ort_oee"]}, {"rows": [{"ort_oee": 78}]})
    assert b["ulasildi"] is False and b["sapma_yuzde"] == -8.24


# ── 3 · BELİRSİZLİK SESSİZCE ÇÖZÜLMÜYOR ────────────────────────────────────

def test_COK_OLCULU_RAPORDA_HEDEF_YOK():
    """🔴 İki ölçülü bir raporda *"hangi hedef"* sorusunun cevabı **yoktur**. Birini
    seçmek, kullanıcının sormadığı bir kıyası cevabın yerine koymak olurdu."""
    assert H.blok(_SEMA, {"cube": "oee", "measures": ["ort_oee", "fire_orani"]},
                  {"rows": [{"ort_oee": 78, "fire_orani": 1}]}) is None


def test_SONUC_YOKSA_HEDEF_YOK():
    """`gerceklesen` **sonuçtan** okunur, hedeften türetilmez: hedefe göre normalize
    edilmiş bir *"gerçekleşen"* uydurmak, kullanıcının sayısını sistemin sayısıyla
    değiştirmek olurdu."""
    assert H.blok(_SEMA, {"cube": "oee", "measures": ["ort_oee"]}, {"rows": []}) is None


# ── 4 · GRAFİK: hedef yoksa çizgi HÂLÂ ORTALAMA ve ÖYLE ETİKETLİ ───────────

def test_HEDEFSIZ_OLCUDE_CIZGI_ORTALAMA_KALIYOR():
    """🔴 **Maddenin kapısı, birebir:** *"hedefi olmayan metrikte referans çizgisi hâlâ
    ortalama ve öyle etiketleniyor"*."""
    sonuc = {"columns": ["makine", "uretim"],
             "rows": [{"makine": f"M{i}", "uretim": 10 + i} for i in range(6)]}
    spec = viz.recommend(sonuc, cube_query={"cube": "x", "measures": ["uretim"],
                                            "dimensions": ["makine"]},
                         hedefler={})
    ref = (spec or {}).get("reference_line")
    assert ref and ref["kind"] == "average", f"hedefsiz ölçüde çizgi hedef sanılmış: {ref}"


def test_HEDEFLI_OLCUDE_CIZGI_HEDEF():
    sonuc = {"columns": ["makine", "uretim"],
             "rows": [{"makine": f"M{i}", "uretim": 10 + i} for i in range(6)]}
    spec = viz.recommend(sonuc, cube_query={"cube": "x", "measures": ["uretim"],
                                            "dimensions": ["makine"]},
                         hedefler={"uretim": 20.0})
    ref = (spec or {}).get("reference_line")
    assert ref["kind"] == "target" and ref["value"] == 20.0


def test_META_ARGS_TEK_KAYNAK():
    """⚠ Hedefler `meta_args`'a eklendi: **altı** çağrı yerinin hiçbirine dokunmadan
    hepsi hedefi görür. Bu fonksiyonun var olma sebebi tam olarak budur — bir alanın
    beşinci çağıranını unutmak imkânsız olsun diye."""
    assert viz.meta_args({"hedefler": {"m": 1.0}})["hedefler"] == {"m": 1.0}
    assert viz.meta_args(None)["hedefler"] == {}


# ── 5 · KAPSAM SINIRI YAZILI ────────────────────────────────────────────────

def test_KAPSAM_SINIRI_YAZILI():
    """⚠ Yol haritası `MetricTarget`'ı SCD-2 olarak tanımlıyor (kapsam · tarih ·
    `as_of` yeniden oynatma). Bu dilim **yalnız beyan yolunu** açar; sınırı yazmamak,
    *yarım inmiş bir mekanizmayı tam gibi göstermek* olurdu."""
    kaynak = (KOK / "app" / "hedef.py").read_text(encoding="utf-8")
    assert "SCD-2" in kaynak and "ayrı bir dilimdir" in kaynak


def test_SOZLESME_ALANI_VAR():
    from app.schemas import AskResponse

    assert AskResponse(question="x").hedef is None, "varsayılan DOLU — hedef uydurulmuş"


# ── 6 · K2 · EKRAN: etiket `kind`'a bağlı, ikinci karar YOK ────────────────

def test_GRAFIK_ETIKETI_KIND_A_BAGLI():
    """🔴 Bir hedef çizgisini *"Ort."* diye etiketlemek (ya da tersi) kullanıcıya **yanlış
    bir kıyas** yaptırırdı: kendi ortalamasının üstünde olmakla **hedefinin** üstünde olmak
    aynı şey değildir."""
    import pytest

    if not FE.exists():
        pytest.skip("frontend bu koşumda mount edilmemiş")
    ch = (FE / "lib" / "chart.ts").read_text(encoding="utf-8")
    assert 'ref.kind === "target" ? "Hedef" : "Ort."' in ch, "etiket hâlâ SABİT"


def test_UI_IKINCI_HEDEF_KARARI_VERMIYOR():
    """⚠ Karar backend'de (`app/hedef.py`). UI'da ikinci bir eşik/yön hesabı, iki kararın
    **ayrışması** demekti — biri *"ulaşıldı"* derken öteki kırmızı gösterirdi."""
    import pytest

    if not FE.exists():
        pytest.skip("frontend mount edilmemiş")
    kart = (FE / "components" / "ReportCard.tsx").read_text(encoding="utf-8")
    assert "item.hedef" in kart, "hedef hiçbir yerde GÖSTERİLMİYOR"
    for sizinti in ("lower_is_better", "yuksek_iyi ?", "> hedef", "< hedef"):
        assert sizinti not in kart, f"hedef kararı UI'a KOPYALANMIŞ ({sizinti!r})"
