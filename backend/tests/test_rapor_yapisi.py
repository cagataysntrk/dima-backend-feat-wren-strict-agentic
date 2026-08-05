"""FAZ 5.13b kapısı — **rapor yapısı ve `contract_id`.** [bayraksız]

Yol haritasının şartı: sabit yapı (kapak → yönetici özeti → kartlar → kaynak listesi) ve
🔴 **"PDF'e döküldüğünde bile `contract_id` altta kalır."**

## ⊘ ÖLÇÜLEMEYEN: Word · Excel — ama **PDF ÖLÇÜLÜR**

Yol haritası *"dört formatta da `contract_id` var"* diyor. Ölçüldü ve **ilk beyanım
yanlıştı**: `docx`/`openpyxl` gerçekten yok, ama **PDF VAR** — `ReportView`'in
`window.print()` yolu. *Var olan bir yolu "ölçülemez" ilan etmek, ölçmemenin en kolay
yoludur.*

Bu kapı hem **yapının kendisini** ölçer (kaynak listesi `pages`'ten **bağımsız** durduğu
için hangi format eklenirse eklensin onu düşürmek **açık bir tercih** olur, sessiz bir
kayıp değil) hem de **baskı yolunu** (`print:hidden` yasak).

*Bir kanıt, taşındığı kabın şekline bağlıysa kanıt değildir.*
"""

from __future__ import annotations

import json

import pytest

from app.report import yapi


def _blok(i, cid="c-abc", olgu="Fire %12 arttı"):
    return {"title": f"Blok {i}", "cube_query": {"cube": "parti"},
            "contract_id": cid, "result": {"row_count": 3},
            "interpretation": {"facts": [{"type": "trend", "text": olgu}]}}


def test_SABIT_YAPI_dort_bolum():
    r = yapi({"title": "Aylık"}, [_blok(1)])
    for bolum in ("kapak", "yonetici_ozeti", "kaynaklar"):
        assert bolum in r, f"sabit yapının `{bolum}` bölümü yok"
    assert r["kapak"]["baslik"] == "Aylık" and r["kapak"]["tarih"]


def test_KAYNAK_LISTESI_pages_ten_BAGIMSIZ():
    """🔴 *Bir kanıt, taşındığı kabın şekline bağlıysa kanıt değildir.*

    Kaynak listesi `pages`'in **içinde** olsaydı, sayfaları kırpan/atlayan/yeniden
    düzenleyen her dışa aktarıcı onu **sessizce** düşürürdü.
    """
    r = yapi({}, [_blok(1, "c-1"), _blok(2, "c-2")])
    assert [k["contract_id"] for k in r["kaynaklar"]] == ["c-1", "c-2"]
    assert "pages" not in r, "kaynaklar `pages`'e bağlanmış — kap değişince kaybolur"


def test_MAKBUZSUZ_blok_ACIKCA_gorunur():
    """🔴 *Kanıtın yokluğunu gizlemek, kanıtsızlıktan kötüdür.*"""
    r = yapi({}, [_blok(1, cid=None)])
    assert r["kaynaklar"][0]["contract_id"] is None
    assert "contract_id" in r["kaynaklar"][0], "alan tamamen düşürülmüş — yokluk gizlendi"


def test_JSON_yuvarlagindan_gecer():
    """En düşük ortak payda: her dışa aktarım bir serileştirmeden geçer."""
    r = yapi({"title": "X"}, [_blok(1, "c-9")])
    geri = json.loads(json.dumps(r, ensure_ascii=False))
    assert geri["kaynaklar"][0]["contract_id"] == "c-9"


def test_DUZ_METIN_render_inde_de_contract_id_var():
    """⚠ Bir PDF/Word dökümünün **en zayıf** hâli düz metindir.

    Kaynak listesi düz metne dökülünce bile kimlikler **görünmeli** — aksi hâlde şart
    yalnız zengin formatlarda tutar.
    """
    r = yapi({"title": "X"}, [_blok(1, "c-7"), _blok(2, "c-8")])
    duz = "\n".join(f"{k['blok']}: {k['contract_id']}" for k in r["kaynaklar"])
    assert "c-7" in duz and "c-8" in duz


def test_YONETICI_OZETI_olgulardan_DERLENIR_LLM_yok():
    """*Özet bir **derleme**dir, bir yorum değil* — `interpret()`'in zaten hesapladığı
    olgulardan gelir ve yeni bir anlatı motoru yazılmaz."""
    r = yapi({}, [_blok(1, olgu="A arttı"), _blok(2, olgu="B düştü")])
    assert r["yonetici_ozeti"] == ["A arttı", "B düştü"]
    # Tekrar eden olgu iki kez yazılmaz.
    r2 = yapi({}, [_blok(1, olgu="Aynı"), _blok(2, olgu="Aynı")])
    assert r2["yonetici_ozeti"] == ["Aynı"]


def test_YAZAR_UYDURULMAZ():
    """*Bir raporun altına olmayan bir ad yazmak, onu kimsenin savunmadığı bir belge
    yapar.*"""
    assert yapi({}, [_blok(1)])["kapak"]["yazar"] is None
    assert yapi({"yazar": "Ayşe"}, [_blok(1)])["kapak"]["yazar"] == "Ayşe"


def test_OLCULEMEYEN_FORMATLAR_ILAN_edilir():
    """⊘ *Sebepsiz bir `⊘` bir ölçüm değildir* — hangi formatın ölçülemediği **yazılı**."""
    r = yapi({}, [_blok(1)])
    # ⚠ **PDF listede DEĞİL — ilk beyanım YANLIŞTI.** `ReportView`'in `window.print()`
    # yolu var ve kaynak listesi o baskıda görünüyor. *Var olan bir yolu "ölçülemez"
    # ilan etmek, ölçmemenin en kolay yoludur.*
    assert set(r["olculemeyen_formatlar"]) == {"word", "excel"}


def test_PDF_yolu_BASKIDA_kaynak_listesini_TASIR():
    """🔴 *"PDF'e döküldüğünde bile `contract_id` altta kalır."*

    Buradaki PDF yolu `ReportView`'in `window.print()`'idir. Kaynak listesi
    **`print:hidden` TAŞIMAMALI** — aksi hâlde şart tam da PDF'te tutmaz.
    """
    from pathlib import Path

    fe = (Path(__file__).resolve().parents[2] / "dima-frontend-demo-master"
          / "src/components/ReportView.tsx")
    if not fe.exists():
        import pytest as _p

        _p.skip("⊘ frontend ağacı yok")
    metin = fe.read_text(encoding="utf-8")
    assert "kaynaklar" in metin, "🔴 Kaynak listesi hiç render edilmiyor — yetim alan."
    i = metin.index("report.kaynaklar")
    bolum = metin[i:i + 1200]
    assert "print:hidden" not in bolum, (
        "🔴 Kaynak listesi `print:hidden` taşıyor — `contract_id` PDF'te KAYBOLUR ve "
        "şart tam da ölçülmesi gereken formatta tutmaz.")
    assert "makbuzsuz" in bolum, (
        "🔴 `contract_id: null` sessizce atlanıyor — kanıtın yokluğunu gizlemek, "
        "kanıtsızlıktan kötüdür.")


def test_IKI_FORMAT_gercekten_YOK():
    """⚠ Beyanın kendisi de doğrulanır: bir gün biri `docx` eklerse ve listeyi
    güncellemezse, rapor **olmayan bir sınırı** ilan ediyor olurdu.

    ⚠ Belirteç **AST**: alt-dize taraması `report.py`'nin **kendi docstring'ini**
    yakalayıp yanlış-kırmızı verdi — o docstring paket adlarını *"bunlar YOK"* demek
    için sayıyor. Bu deponun **on birinci kez** ödediği ders: *beyan ile beyanın
    anlatımı farklı şeylerdir.*
    """
    import ast
    from pathlib import Path

    yasak = {"docx", "openpyxl", "reportlab", "weasyprint", "fpdf", "xlsxwriter"}
    kok = Path(__file__).resolve().parents[1]
    for dosya in (kok / "app").rglob("*.py"):
        agac = ast.parse(dosya.read_text(encoding="utf-8", errors="ignore"))
        for n in ast.walk(agac):
            adlar: list[str] = []
            if isinstance(n, ast.Import):
                adlar = [a.name.split(".")[0] for a in n.names]
            elif isinstance(n, ast.ImportFrom):
                adlar = [(n.module or "").split(".")[0]]
            for ad in adlar:
                assert ad not in yasak, (
                    f"🔴 `{dosya.name}` artık `{ad}` import ediyor — "
                    f"`olculemeyen_formatlar` beyanı BAYATLADI ve kapı o formatı "
                    f"ölçmeye başlamalı.")


@pytest.mark.parametrize("n", [0, 1, 5])
def test_BOS_ve_COKLU_blok(n):
    r = yapi({}, [_blok(i) for i in range(n)])
    assert len(r["kaynaklar"]) == n
