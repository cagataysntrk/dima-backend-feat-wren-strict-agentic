"""FAZ 4.8 kapısı — **§C/16'nın ölçüm aracının kendisi ölçülür.**

Bu dosya **sonucu** kilitlemez (sonuç değişir, değişmeli); **ölçüm disiplinini** kilitler:

1. **Puanlama kuralı TEK YERDE** — ikinci bir yol, kuralı sonuca uydurmanın kapısıdır.
2. **Üç şart da aranır** — dönen değer · varlık kapsamı · zaman/filtre semantiği.
3. **Netleştirme AYRI SATIR**, paydadan **gizlice çıkarılmaz**.
4. **Tutulmuş küme kilitli** — kirlenme sessiz olamaz.
5. **`n ≥ 100`** ve altında ana sayı `⊘`.
6. **Gürültü tabanı yazılı** — 10 puan altı fark yorumlanmaz.
7. **Sebepsiz `⊘` yok** — ölçülemeyen vaka sayılır ve sebebi yazılır.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from lab.uctan_uca import (
    ASGARI_N,
    GURULTU_ESIGI,
    PAY,
    TOHUM,
    _deger_esit,
    kilit_hash,
    puanla,
    rapor_metni,
    tutulmus_mu,
)

_KAYNAK = Path(__file__).resolve().parents[1] / "lab/uctan_uca.py"

_ALTIN = {"deger": 100.0, "satir": 3, "boyutlar": ["il"], "zaman": ["month"]}


def test_PUANLAMA_KURALI_TEK_YERDE():
    """🔴 İkinci bir puanlama yolu, **sonucu kurala değil kuralı sonuca** uydurmanın kapısı.

    ⚠ Belirteç **AST**: modülün docstring'i kuralı **anlatıyor** ve bir alt-dize taraması
    kendi belgesini ölçerdi (bu deponun on kez ödediği ders).
    """
    agac = ast.parse(_KAYNAK.read_text(encoding="utf-8"))
    puanlayanlar = [n.name for n in ast.walk(agac)
                    if isinstance(n, ast.FunctionDef)
                    and ("puanla" in n.name or "skor" in n.name or "score" in n.name)]
    assert puanlayanlar == ["puanla"], (
        f"🔴 Birden fazla puanlama fonksiyonu: {puanlayanlar}. Kural TEK YERDE olmalı.")
    # `kos()` puanlamayı KENDİ yapmamalı — `puanla()` çağırmalı.
    kos = next(n for n in ast.walk(agac)
               if isinstance(n, ast.FunctionDef) and n.name == "kos")
    cagrilar = {getattr(c.func, "id", getattr(c.func, "attr", ""))
                for c in ast.walk(kos) if isinstance(c, ast.Call)}
    assert "puanla" in cagrilar, "🔴 `kos()` `puanla()` çağırmıyor — ikinci bir yol açılmış."


def test_UC_SART_da_ARANIR():
    """*Dönen değer · varlık kapsamı · zaman/filtre semantiği* — **aynı anda**."""
    assert puanla(_ALTIN, dict(_ALTIN))["dogru"] is True

    assert puanla(_ALTIN, {**_ALTIN, "deger": 101.0})["sinif"] == "deger"
    assert puanla(_ALTIN, {**_ALTIN, "satir": 4})["sinif"] == "kapsam"
    assert puanla(_ALTIN, {**_ALTIN, "boyutlar": ["ilce"]})["sinif"] == "kapsam"
    assert puanla(_ALTIN, {**_ALTIN, "zaman": ["year"]})["sinif"] == "zaman"
    assert puanla(_ALTIN, None)["sinif"] == "netlestirme"
    assert puanla(_ALTIN, {"hata": "x"})["sinif"] == "hata"


def test_YAKIN_sayi_DOGRU_sayilmaz():
    """🔴 Tolerans yalnız **kayan nokta** yuvarlamasınadır, semantik değil.

    *%2 sapmayı doğru saymak, doğruluğu ölçmeyi bırakıp yakınlığı ölçmektir.* Ve bu
    aletin bulduğu gerçek kusur tam da o sınıfta: `8002972.8 ≠ 8002962.85` — insan
    gözüyle aynı, **ama başka bir cube'dan**.
    """
    assert _deger_esit(1.0, 1.0 + 1e-15)
    assert not _deger_esit(8002972.8, 8002962.85), (
        "🔴 On milyonda birlik sapma DOĞRU sayılırsa, sessiz-yanlışın tam da ölçülmek "
        "istenen sınıfı görünmez olur.")
    assert not _deger_esit(100.0, 102.0)
    assert _deger_esit(None, None)
    assert not _deger_esit(None, 0.0)


def test_NETLESTIRME_paydadan_GIZLICE_cikarilmaz():
    """🔴 *Rakiplerin manşet sayılarını kıyaslanamaz yapan şey tam olarak budur.*"""
    metin = rapor_metni([{"sirket": "x", "n": 100, "vaka": 100, "atlanan": 0,
                          "kilit": "abc", "dogru": 60, "oran": 0.60,
                          "netlestirme": 25, "netlestirme_orani": 0.25,
                          "cevaplanan_ici": 0.80, "dagilim": {}, "ornekler": []}])
    assert "%60.0" in metin, "ana sayı (netleştirme PAYDADA) rapordan düşürülemez"
    assert "%25.0" in metin, "netleştirme AYRI SATIR olarak görünmeli"
    assert "%80.0" in metin, "'cevaplanan içinde' ikincil sayı da yazılmalı"
    assert "GİZLİCE ÇIKARILMAZ" in metin


def test_TUTULMUS_kume_DETERMINISTIK_ve_kilitli():
    """Aynı tohum → aynı dilim; küme değişirse **hash değişir**."""
    ornek = [f"soru {i}" for i in range(500)]
    d1 = [q for q in ornek if tutulmus_mu(q)]
    d2 = [q for q in ornek if tutulmus_mu(q)]
    assert d1 == d2, "dilim deterministik değil"
    # Pay makul aralıkta — çok büyük bir "tutulmuş" küme, kelimeyi anlamsızlaştırır.
    assert 0.02 <= PAY <= 0.25
    assert 0.5 * PAY < len(d1) / len(ornek) < 2.0 * PAY

    # Kilit: küme değişirse hash DEĞİŞİR.
    a = kilit_hash([{"soru": "a"}, {"soru": "b"}])
    assert a == kilit_hash([{"soru": "b"}, {"soru": "a"}]), "kilit sıraya bağlı olmamalı"
    assert a != kilit_hash([{"soru": "a"}, {"soru": "c"}]), (
        "🔴 Küme değişti ama kilit AYNI — kirlenme sessiz olur.")


def test_TOHUM_ve_ASGARI_N_sozlesmesi():
    """§C/16'nın sayısal şartları koda **yazılı**."""
    assert ASGARI_N >= 100, "§C/16 en az 100 vaka istiyor"
    assert isinstance(TOHUM, int)
    assert GURULTU_ESIGI == 0.10, (
        "BIRD/Spider anotasyon hata oranı (%52,8 / %62,8) → 10 puan altı fark GÜRÜLTÜDÜR")


def test_N_100_ALTINDA_ana_sayi_UCUNCU_HALDIR():
    """*Örneklem kazasını sonuç diye satmak* — kapı bunu yasaklar."""
    metin = rapor_metni([{"sirket": "kucuk", "n": 12, "vaka": 12, "atlanan": 0,
                          "kilit": "k", "dogru": 12, "oran": 1.0, "netlestirme": 0,
                          "netlestirme_orani": 0.0, "cevaplanan_ici": 1.0,
                          "dagilim": {}, "ornekler": []}])
    assert f"n < {ASGARI_N}" in metin and "ÖLÇÜLEMEDİ" in metin


def test_SEBEPSIZ_olculemedi_YOK():
    """⊘ bir sonuç değil bir **beyandır** — sebebi yazılmadan yayımlanamaz."""
    metin = rapor_metni([{"sirket": "y", "n": 0, "vaka": 40, "atlanan": 40,
                          "kilit": "k", "atlanma_sebebi": "Catalog Error: tablo yok",
                          "dogru": 0, "oran": None, "netlestirme": 0,
                          "netlestirme_orani": None, "cevaplanan_ici": None,
                          "dagilim": {}, "ornekler": []}])
    assert "40/40 vaka ÖLÇÜLEMEDİ" in metin
    assert "Catalog Error" in metin, "sebep yazılmadan ⊘ yayımlanamaz"


def test_ALETIN_OLCMEDIGI_sey_YAZILI():
    """🔴 *Bu alet motorun kendi doğruluğunu ölçtüğünü İDDİA ETMEZ* — sınır yazılı olmalı."""
    metin = rapor_metni([])
    assert "ÖLÇMEDİĞİ" in metin
    assert "aynı motoru" in metin, (
        "Altın cevap ile sistemin cevabı aynı motoru kullanır; bu sınır gizlenirse "
        "sayı, olmayan bir garantiyi rozetler.")


def test_TUTULMUS_kume_AYAR_icin_kullanilmaz():
    """⚠ *Tutulmuş bir küme, bir kez bakıldıktan sonra tutulmuş değildir.*

    Kapı bunu **davranışsal** olarak ölçemez (kimin neye baktığını bilemez) — ama kuralın
    **yazılı** olduğunu ölçebilir. Sınırın kaydedilmesi, olmayan bir garantiyi
    rozetlememek içindir.
    """
    metin = rapor_metni([])
    assert "tutulmuş değildir" in metin
    # Ve `nl_corpus` bu modülü İTHAL ETMEMELİ: ayar döngüsüne girmesinin en kolay yolu odur.
    korpus = (Path(__file__).resolve().parents[1] / "lab/nl_corpus.py")
    if korpus.exists():
        agac = ast.parse(korpus.read_text(encoding="utf-8"))
        for n in ast.walk(agac):
            adlar = ([a.name for a in n.names] if isinstance(n, ast.Import)
                     else [n.module or ""] if isinstance(n, ast.ImportFrom) else [])
            assert not any("uctan_uca" in str(a) for a in adlar), (
                "🔴 `nl_corpus` tutulmuş kümeyi İTHAL EDİYOR — küme ayar döngüsüne girdi "
                "ve artık tutulmuş DEĞİL. Yenisi ayrılmalı, eskisi `eval`'e devredilmeli.")


@pytest.mark.parametrize("bozuk", [
    {"deger": 100.0, "satir": 3, "boyutlar": ["il"], "zaman": ["year"]},
    {"deger": 100.0, "satir": 3, "boyutlar": [], "zaman": ["month"]},
])
def test_zaman_ve_kapsam_sessizce_gecmez(bozuk):
    assert puanla(_ALTIN, bozuk)["dogru"] is False
