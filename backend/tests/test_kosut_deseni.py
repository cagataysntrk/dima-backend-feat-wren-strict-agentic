"""KOŞUT DESEN KAPISI — *yavaş bir ölçüm, atlanan bir ölçüme dönüşür.*

## Neden bu kapı var

Kullanıcı kuralı (2026-08-05): *"bu tarz desen uygulanmamış yavaş test kalmasın
dikkat et ve bundan sonra da dikkat et."*

Korpusta ölçülmüştü: 13 dk 18 sn → **1 dk 50 sn**, ve sayılar **birebir aynı**.
Yani hız kapsamdan değil **çekirdekten** satın alınır. Ama bu ders bir dosyada
kalırsa, bir sonraki koşucu onu bilmeden seri yazılır ve kimse fark etmez —
ta ki biri *"neden bu kadar sürüyor"* diye sorana kadar.

🔴 Bu dosya dersi **kapıya** çevirir: ağır bir koşucu eklendiğinde, koşut deseni
kullanmıyorsa test kırmızı verir.
"""

from __future__ import annotations

import pathlib
import re

_LAB = pathlib.Path(__file__).resolve().parents[1] / "lab"

#: Koşut desen **gerekmeyen** koşucular ve **neden** gerekmediği.
#: ⚠ Muafiyet listesi gerekçesiz büyümesin: her satır bir sebep taşır, yoksa
#: liste zamanla *"paralelleştirmediklerimiz"* çöplüğüne döner.
_MUAF = {
    "nl_corpus.py": "kendi paralel altyapısı var (ProcessPoolExecutor, 16 dilim)",
    "kosut.py": "deseni TANIMLAYAN modül",
    "kapi.py": "orkestratör — kendisi iş yapmaz, alt koşucuları çağırır",
    "generate_models_duckdb.py": "tek geçişli introspection, saniyeler",
    "generate_models.py": "aynı — introspection",
    "izolasyon.py": "altyapı, koşucu değil",
    "mdl_diff.py": "iki dosya kıyaslar, ağır çağrı yok",
    "snapshot_mssql.py": "dış DB anlık görüntüsü — G/Ç bağımlı, CPU değil",
    "nl_accuracy.py": "🔴 CANLI LLM koşumu — paralelleştirmek KOTA sınırını aşar "
                      "(ölçülen sınır 10 istek/10 sn)",
    "konusma_senaryolari.py": "🔴 CANLI LLM koşumu — aynı kota kısıtı",
    "deneyim.py": "🔴 CANLI LLM koşumu — turlar arası 5 sn bekleme ZORUNLU",
    "golge_spike.py": "gölge kıyas — iki planı yan yana koyar, tek geçiş",
    "sharding.py": "compose/build ağırlıklı — derleme kilidi paralelliği engeller",
}

#: Bir dosyayı "ağır koşucu" yapan eşik: `route()`/`svc.` çağrısı bir DÖNGÜ içinde.
_AGIR_DESEN = re.compile(r"for\s+\w+.*:\s*(\n\s+.*){0,12}?(cube_router\.route\(|svc\.cube_sql\()",
                         re.MULTILINE)


def test_AGIR_KOSUCULAR_kosut_deseni_kullanir():
    """🔴 Döngü içinde `route()` çağıran her koşucu ya `lab.kosut` kullanır, ya da
    `_MUAF`'ta **gerekçesiyle** yazılıdır.

    *Bir muafiyet gerekçesiz yazılırsa, listeye girmek paralelleştirmekten kolay
    olur — ve liste zamanla kuralın kendisini yer.*
    """
    ihlal = []
    for f in sorted(_LAB.glob("*.py")):
        if f.name in _MUAF:
            continue
        src = f.read_text(encoding="utf-8")
        if not _AGIR_DESEN.search(src):
            continue
        if "kosut" in src or "ProcessPoolExecutor" in src:
            continue
        ihlal.append(f.name)
    assert not ihlal, (
        "🔴 döngü içinde route() çağırıp koşut deseni kullanmayan koşucu: "
        + ", ".join(ihlal)
        + " — `lab.kosut.degerlendir()` kullan ya da _MUAF'a GEREKÇESİYLE ekle"
    )


def test_MUAFIYETLER_gerekce_tasir():
    """Her muafiyet bir sebep yazar; boş/kısa gerekçe kabul edilmez."""
    for ad, sebep in _MUAF.items():
        assert len(sebep) >= 20, f"{ad}: gerekçe yetersiz («{sebep}»)"


def test_MUAF_LISTESI_hayalet_dosya_tutmaz():
    """⚠ Silinmiş bir dosya muafiyet listesinde kalırsa, liste **yanlış bir güvence**
    verir: kural uygulanıyor görünür, uygulanmadığı yer artık yoktur."""
    hayalet = [ad for ad in _MUAF if not (_LAB / ad).exists()]
    assert not hayalet, f"muafiyet listesinde olmayan dosyalar: {hayalet}"


def test_KOSUT_ayni_env_ile_geri_alinir():
    """⚠ Geri alma **tek env** olmalı ve korpusla **AYNI** env olmalı: iki ayrı
    değişken, birini kapatıp ötekini açık bırakma tuzağı üretir."""
    src = (_LAB / "kosut.py").read_text(encoding="utf-8")
    assert "DIMA_KORPUS_PARALEL" in src, "korpusla aynı geri-alma env'i kullanılmıyor"


def test_SPAWN_kullanilir_fork_degil():
    """🔴 `fork` ile alt süreçler `tests/conftest.py`'nin import anında kurduğu
    control-plane SQLite'ını miras alır ve dilimler aynı dosyaya girip çöker
    (korpusta ölçüldü: payda 445→255). `spawn` ortamı her süreçte baştan kurar."""
    src = (_LAB / "kosut.py").read_text(encoding="utf-8")
    assert 'get_context("spawn")' in src, "spawn kullanılmıyor — fork tuzağı"
