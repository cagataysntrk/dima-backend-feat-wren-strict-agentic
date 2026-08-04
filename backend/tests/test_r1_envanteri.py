"""FAZ 3.2 — **R1 ENVANTERİ** kapısı. [bayraksız: kapsam]

*"Katalogda **var olan** bir ölçü sinonimi, düz sorulduğunda cube'unu bile tanıtmıyor."*
Bu, bu depoda ölçülmüş **tek en büyük kaldıraç** ve hiç çalışılmamıştı.

## 🔴 ÖLÇÜM, YOL HARİTASININ TEŞHİSİNİ DÜZELTTİ

§6.1h *"R1'in **TAMAMI** gerçek ölçü-düzeyi belirsizliğidir"* diyor. Envanter (2026-08-04,
`python lab/r1_envanteri.py`) **170 R1** buldu ve dağılım bunu **çürütüyor**:

| aday kümesi | n | gerçekte ne? |
|---|---|---|
| `cari` ↔ `mizan` | **42** | 🔴 **gerçek belirsizlik** → chip (3.1'in `bakiye` kararı) |
| `mal` ↔ `ticaret` | **30** | **grain ikizi** (fatura ↔ stok hareketi, 2.1c) |
| `oee` ↔ `parti` | **20** | grain/kapsam ikizi |
| `cari` ↔ `cari_finans` | **16** | **türev ikiz** — aynı kavram, türetilmiş görünüm |
| `cari`+`cari_finans`+`mizan` | **12** | karışık |
| `enerji_makine` ↔ `surdurulebilirlik` | **6** | 3.1'in `elektrik` kararı → tek sahip |

Yani R1'in gövdesi **kullanıcı belirsizliği değil, KATALOG İKİZLİĞİDİR**: `mal`/`ticaret`
ve `cari`/`cari_finans` aynı kavramı iki kimlikte taşıyor. *Bir kullanıcı "debt" derken
iki şey arasında kalmıyor — katalog iki kez aynı şeyi söylüyor.*

**Sonuç:** hedefe (≤30) **sahiplik kararlarıyla** ulaşılamaz — yalnız **18'i** tek sahipli.
Kalanın büyük kısmı **modelleme borcudur** (2.4 sınıfı) ve o iş ayrı bir turdur.
*Ölçüm, hedefin yolunu değiştirdi; hedefi düşürmedi.*
"""

from __future__ import annotations

import pathlib
import sys

KOK = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK / "lab"))


def test_ARAC_KARAR_VERMIYOR_RAPOR_URETIYOR():
    """🔴 **FAZ 3.1'in dersi taze:** kararı **araç** verirse bir tenant'ın alan bilgisi
    bütün tenant'lara dayatılır ve korpus geriler (%93,2→%92,6, ölçüldü). Bu araç bir
    **iş listesi** üretir; kararı insan verir ve karar **tenant kapsamlı** girer."""
    kaynak = (KOK / "lab" / "r1_envanteri.py").read_text(encoding="utf-8")
    assert "KARAR VERMEZ, RAPOR ÜRETİR" in kaynak
    for yazma in ("sahiplenilen_terimler] =", "write_text", "MetrikSahipligi"):
        assert yazma not in kaynak, f"envanter aracı KARAR YAZIYOR ({yazma!r})"


def test_KUTU_AYRIMI_ADAY_SAYISINDAN_TURUYOR():
    """`tek_sahip` ↔ `belirsiz` ayrımı **ölçülür**, beyan edilmez: tek adaylı terim
    kapatılabilir, çok adaylı terim bir **karar** ister."""
    from r1_envanteri import envanter                        # noqa: PLC0415

    sema = {"cubes": [
        {"name": "a", "measure_synonyms": {"m1": ["tekil"]}},
        {"name": "b", "measure_synonyms": {"m2": ["ortak"]}},
        {"name": "c", "measure_synonyms": {"m3": ["ortak"]}},
    ]}
    d = envanter(sema)
    kutular = {x["terim"]: x["kutu"] for x in d["r1"]}
    if "tekil" in kutular:
        assert kutular["tekil"] == "tek_sahip"
    if "ortak" in kutular:
        assert kutular["ortak"] == "belirsiz"


def test_OLCULEMEYEN_YESIL_SAYILMIYOR():
    """⊘ üçüncü durum: derlenemeyen bir şirketi *"R1 yok"* diye raporlamak, **risk yok
    yalanı** üretirdi."""
    kaynak = (KOK / "lab" / "r1_envanteri.py").read_text(encoding="utf-8")
    assert "ÖLÇÜLEMEDİ" in kaynak and "YALANI" in kaynak


def test_HEDEF_SIFIR_DEGIL():
    """🔴 Hedef **≤30**, sıfır değil: kalanlar *gerçek* belirsizliktir ve **chip'e** gider.
    Sıfır hedefi koymak, gerçek belirsizliği **tahminle** kapatmayı zorlardı."""
    from r1_envanteri import HEDEF                           # noqa: PLC0415

    assert HEDEF == 30


def test_OLCUM_TESHISI_DUZELTTI_ve_YAZILI():
    """🔴 §6.1h *"R1'in TAMAMI gerçek ölçü-düzeyi belirsizliğidir"* diyor; envanter bunu
    **çürüttü**: 170 R1'in yalnız **42**'si (`cari`↔`mizan`) gerçek belirsizlik; **46**'sı
    katalog ikizliği (`mal`↔`ticaret`, `cari`↔`cari_finans`), **18**'i tek sahipli.

    *Bir kullanıcı "debt" derken iki şey arasında kalmıyor — katalog iki kez aynı şeyi
    söylüyor.* Düzeltmeyi yazmamak, bir sonraki turun aynı yanlış teşhisle çalışması olurdu.
    """
    kaynak = pathlib.Path(__file__).read_text(encoding="utf-8")
    assert "KATALOG İKİZLİĞİDİR" in kaynak and "çürütüyor" in kaynak
    assert "sahiplik kararlarıyla** ulaşılamaz" in kaynak, "yolun değiştiği YAZILI DEĞİL"


def test_SAHIPSIZ_TERIM_EKRANDA_IS_KALEMI():
    """🔴 Yol haritasının şartı: *"kalan sahipsiz terimler bir **LİSTE** olur — 'bilinmeyen'
    olmaktan çıkıp **İŞ KALEMİ** hâline gelir."* Bir sayıyı göstermek, onu **görünmez bir
    borç** olmaktan çıkarır."""
    import pytest

    fe = KOK.parent / "dima-frontend-demo-master" / "src"
    if not fe.exists():
        pytest.skip("frontend mount edilmemiş")
    panel = (fe / "components" / "SchemaPanel.tsx").read_text(encoding="utf-8")
    assert "sahibi yok" in panel, "sahipsiz terim sayısı EKRANDA GÖRÜNMÜYOR"
    assert "tahmin" in panel, "sahipsizliğin BEDELİ yazılı değil"
