"""DENEYİM SÜİTİNİN KENDİ DÜRÜSTLÜĞÜ — *"ölçüm aracının kendisi de bir bağımlılıktır"*.

Bu oturumda ölçüm araçları **on ikiden fazla kez** yanlış çıktı; `lab/deneyim.py`'nin
ölçütü yalnız bu fazda **üç kez** düzeltildi. Bu dosya aracın kendi sözleşmesini kilitler:
araç yanlış ölçerse ürün hakkında söylediği her şey değersizdir.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

from lab import deneyim

KAYNAK = pathlib.Path(deneyim.__file__)


def test_SENARYO_SAYISI_PLANDAKI_ARALIKTA():
    """Plan: *"12–15 canlı thread"*. Sessizce 3'e düşen bir süit, yeşil görünüp hiçbir
    şey ölçmezdi."""
    assert 12 <= len(deneyim.SENARYOLAR) <= 15, len(deneyim.SENARYOLAR)


def test_HER_SENARYO_COK_TURLU():
    """Tek turluk bir "senaryo" zaten `konusma_senaryolari`'nın işidir; bu araç
    THREAD ölçer."""
    for s in deneyim.SENARYOLAR:
        assert len(s["turlar"]) >= 2, s["ad"]
        assert s["olculen"], f"{s['ad']}: hiçbir sözleşme satırı ölçmüyor"


def test_YEDI_SATIRIN_HEPSI_EN_AZ_BIR_SENARYODA_OLCULUYOR():
    """Ölçülmeyen bir sözleşme satırı, olmayan bir garantidir."""
    satirlar = {deneyim.S1_CAPA, deneyim.S2_ANLAT, deneyim.S3_SUREKLILIK,
                deneyim.S4_SOSYAL, deneyim.S5_BELIRSIZLIK, deneyim.S6_MAKBUZ,
                deneyim.S7_GERI_DONUS}
    kapsanan = {x for s in deneyim.SENARYOLAR for x in s["olculen"]}
    assert satirlar <= kapsanan, f"ölçülmeyen satır: {satirlar - kapsanan}"


def test_UCUNCU_DURUM_KORUNUYOR():
    """`None` = ⊘ ölçülemedi. İkisinden birine yuvarlamak bilgi yok eder (Faz 9.6)."""
    assert deneyim._isaret(True) == "✅"
    assert deneyim._isaret(False) == "❌"
    assert deneyim._isaret(None) == "⊘"


def test_YAPISAL_MOD_KAPI_OLMADIGINI_SOYLUYOR():
    """LLM'siz koşumda anlatı/Intent satırları hiçbir şey söylemez; araç bunu YAZMALI —
    aksi hâlde yeşil bir tablo sahte güven üretir."""
    kaynak = KAYNAK.read_text(encoding="utf-8")
    assert "KAPI DEĞİL" in kaynak


def test_ANLAT_OLCUTU_SEKILDEN_TURETILIYOR():
    """Eşik tahminle ayarlanamaz: `shape` bir BOYUT, `trend`/`peak` bir ZAMAN EKSENİ
    ister — üçüncü olgu ancak ikisi birden varken doğar. Bu ölçüt üç kez düzeltildi."""
    govde = next(n for n in ast.walk(ast.parse(KAYNAK.read_text(encoding="utf-8")))
                 if isinstance(n, ast.FunctionDef) and n.name == "_olc")
    metin = ast.unparse(govde)
    assert "timeDimensions" in metin and "dimensions" in metin, \
        "anlat ölçütü artık şekle bakmıyor — sabit eşiğe dönmüş"


def test_KALIP_KOPYALANMADI():
    """`--live` bayrağı bir kez zaten yalan söylemişti; o düzeltme TEK yerde durmalı."""
    agac = ast.parse(KAYNAK.read_text(encoding="utf-8"))
    ithal = {a.name for n in ast.walk(agac) if isinstance(n, ast.ImportFrom)
             and (n.module or "").endswith("konusma_senaryolari") for a in n.names}
    assert "_canli_ortami_geri_yukle" in ithal and "LIVE_BEKLE" in ithal, ithal
    assert "DIMA_LLM_PROVIDER" not in KAYNAK.read_text(encoding="utf-8"), \
        "araç kendi ortam kurulumunu yazmış — ikinci sahip doğdu"


@pytest.mark.parametrize("soru,beklenen", [
    ("bunu analiz et", "anlat"), ("bunu yorumla", "anlat"),
    ("merhaba", "sosyal"), ("teşekkürler", "sosyal"),
    ("her pazartesi bu raporu bana yolla", "konusma"),
    ("bunu panoya ekle", "konusma"),
    ("bu yıl makine bazında oee", "veri"),
    (("__CUBE__", 0), "geri_donus"),
])
def test_TUR_TIPI_SINIFLANDIRMASI(soru, beklenen):
    """Yanlış sınıflandırılan bir tur, yanlış sözleşme satırında ölçülür."""
    assert deneyim._tur_tipi(soru) == beklenen


def test_MAKBUZ_UC_TASIYICIDAN_BIRINI_ARIYOR():
    assert deneyim._makbuzlu({"trace": ["x"]})
    assert deneyim._makbuzlu({"contract_id": "c1"})
    assert not deneyim._makbuzlu({"sql": "select 1"})
