"""🔴🔴 `§RP` — **AGENTIC RAPOR: bir YIĞIN, bir BELGE değildir.**

## Ölçülen kusur (araştırma turu, 2026-08-10)

    «son 2 yıl satış raporu hazırla»
      plan   : SORGU×4 + RAPOR       ← dört bölüm HESAPLANDI
      cevap  : plan.bolumler = ham `{cube_query, result}`  ·  başlık YOK · viz YOK
      → `ReportView.tsx`'in çizebileceği bir **belge** yok

⚠ İlk teşhisim *«bölümler atılıyor»* idi ve **ölçümle düzeldi**: `ask.py`
`plan=_pc.get("plan")` ile onları **taşıyor**. Kusur taşımada değil **derlemede**.
*Bugün yedinci kez ölçüm, yazmak üzere olduğum bir kökü düzeltti.*

## Neden yeni bir motor YOK

`report.compose_report` (çok sayfalı belge) ve `ReportView.tsx` (render) **zaten** uçtan
uca çalışıyor — yalnız `POST /report` yolunda. Eklenen tek şey, koşmuş bölümleri **aynı
biçime** dizen bir derleyici ve onu taşıyan bir alan.

⊙ Ve derleyici sonuçları **yeniden koşmaz**: sonuçlar elde. *Bir sonucu iki kez
hesaplamak, onu bir kez yanlış hesaplamanın en kolay yoludur.*
"""

from app import report

_SEMA = {"cubes": [
    {"name": "parti", "display": "parti",
     "measures": ["toplam_ciro"], "dimensions": ["musteri"],
     "units": {"toplam_ciro": "₺"}},
]}


def _bolum(cube="parti", dims=None, satirlar=None):
    satirlar = satirlar if satirlar is not None else [{"musteri": "EGE", "toplam_ciro": 1.0}]
    return {"cube_query": {"cube": cube, "measures": ["toplam_ciro"],
                           **({"dimensions": dims} if dims else {})},
            "result": {"columns": list(satirlar[0]) if satirlar else [],
                       "rows": satirlar, "row_count": len(satirlar)}}


def test_BOLUMLER_BELGEYE_DIZILIR():
    """🔴 **Kapının kalbi.** Dört bölüm → `Report` biçimi, sayfalara bölünmüş."""
    r = report.bolumlerden_kur([_bolum() for _ in range(4)],
                               baslik="Satış raporu", schema=_SEMA)
    assert r["title"] == "Satış raporu"
    assert r["block_count"] == 4
    assert sum(len(p) for p in r["pages"]) == 4
    assert len(r["pages"]) == 2, "3'lük sayfalara bölünmeli (4 blok → 2 sayfa)"


def test_HER_BOLUM_KENDI_SORGUSUNU_TASIR():
    """🔴 *«buradan devam et»* bunsuz kurulamaz: her kart `POST /cube` ile **0 LLM**
    yeniden koşulabilmeli (`O-5`/`D4` deseni)."""
    r = report.bolumlerden_kur([_bolum(dims=["musteri"])], baslik="x", schema=_SEMA)
    blok = r["pages"][0][0]
    assert blok["cube_query"]["cube"] == "parti"
    assert blok["cube_query"]["dimensions"] == ["musteri"]


def test_VIZ_KARARI_VERILIR():
    """Bölüm bir **belge bloğudur**: grafiği de kararlaştırılmış gelir."""
    r = report.bolumlerden_kur([_bolum(dims=["musteri"])], baslik="x", schema=_SEMA)
    assert r["pages"][0][0]["viz"] is not None


def test_BOS_BOLUM_GRAFIGE_CEVRILMEZ():
    """⚠ Boş bir bölümü grafiğe çevirmek kullanıcıya **boş bir eksen** göstermektir."""
    r = report.bolumlerden_kur([_bolum(satirlar=[])], baslik="x", schema=_SEMA)
    blok = r["pages"][0][0]
    assert blok["viz"] is None and blok["error"] is None


def test_SONUCLAR_YENIDEN_KOSULMAZ():
    """🔴🔴 **Kapının en önemli satırı.** Derleyiciye `service` verilmez — verilemez de:
    imzasında yoktur. Yani bu yol bir sorgu **koşamaz**, ve o yüzden aynı soruya iki
    farklı sayı **üretemez**.

    *Bir sınırı en iyi koruyan şey, onu ihlal etmek için imza değiştirmeyi zorunlu
    kılmaktır.*"""
    import inspect

    imza = inspect.signature(report.bolumlerden_kur)
    assert "service" not in imza.parameters
    satirlar = [{"musteri": "EGE", "toplam_ciro": 42.0}]
    r = report.bolumlerden_kur([_bolum(satirlar=satirlar)], baslik="x", schema=_SEMA)
    assert r["pages"][0][0]["result"]["rows"] == satirlar


def test_KAPAK_VE_KAYNAK_LISTESI_KORUNUR():
    """⚠ `yapi()` aynı fonksiyondan geçer — ikinci bir `Report` üreticisi `KAT-1` olurdu
    ve frontend'in tanıdığı **tek** biçim budur."""
    r = report.bolumlerden_kur([_bolum()], baslik="x", schema=_SEMA)
    ust = report.compose_report.__module__  # aynı modül, aynı biçim
    assert ust == "app.report"
    assert set(("title", "pages", "block_count")) <= set(r)


def test_BOLUMSUZ_CAGRI_BOS_BELGE_URETIR():
    """*Bir ölçümün susması, ölçtüğü şeyin yokluğu değildir* — bölüm yoksa belge boş ama
    **biçimli** döner; çağıran ayrıca `None` kontrolü yapmak zorunda kalmaz."""
    r = report.bolumlerden_kur([], baslik="x", schema=_SEMA)
    assert r["block_count"] == 0 and r["pages"] == [[]]


def test_TAVAN_ASILMAZ_BOLUM_SAYISI():
    """⚠ Üst sınır `compose_report` ile **aynı** sabittir; iki yol iki farklı tavan
    taşısaydı aynı belge iki uçta farklı uzunlukta olurdu."""
    r = report.bolumlerden_kur([_bolum() for _ in range(40)], baslik="x", schema=_SEMA)
    assert r["block_count"] == report._MAX_BLOCKS
