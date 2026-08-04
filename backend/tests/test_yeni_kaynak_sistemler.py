"""FAZ 3.5 — **YENİ KAYNAK SİSTEMLER.** [bayraksız: genişleme]

## 🔴 BU MADDE ⊘ ÖLÇÜLEMEDİ OLARAK KAPANDI — ve nedeni yazılı

Maddenin **kapısı** birebir şunu istiyor: *"`db_introspect → mdl_writer → sinonim önerici
→ insan onayı` zinciri **gerçek bir müşteri DB'sinde uçtan uca koşulur** — bugüne kadar
hiç koşulmadı."*

Bu koşum bir **canlı müşteri veri tabanı** ister; `--network none` altında ve müşteri
kimlik bilgileri olmadan **yapılamaz**. Yeşile yuvarlamak, koşulmamış bir zinciri
*"koşuldu"* diye işaretlemek olurdu — bu deponun `⊘ ÖLÇÜLEMEDİ` disiplininin tam olarak
engellediği şey.

*Ölçülemeyeni yeşil saymak, "risk yok" yalanı üretir.*

Burada **ölçülebilen** kısım ölçüldü: konnektör envanteri.
"""

from __future__ import annotations

import pathlib
import pkgutil
import re

KOK = pathlib.Path(__file__).resolve().parents[1]

#: Altyapı modülleri — konnektör **değil**. Sayıma katmak, envanteri iki fazla gösterirdi.
ALTYAPI = {"base", "factory"}


def _envanter() -> tuple[list[str], list[str]]:
    import wren.connector as wc

    hepsi = sorted(m.name for m in pkgutil.iter_modules(wc.__path__)
                   if not m.name.startswith("_") and m.name not in ALTYAPI)
    kod = "".join(p.read_text(encoding="utf-8", errors="ignore")
                  for p in (KOK / "app").rglob("*.py"))
    kullanilan = [c for c in hepsi if re.search(rf'["\']{re.escape(c)}["\']', kod)]
    return hepsi, kullanilan


def test_KULLANILMAYAN_KONNEKTOR_SAYISI_OLCULDU():
    """⚠ **Yol haritasının sayısı da düzeltildi.** Madde *"17 değil, backend'de hiç
    geçmeyen **12** konnektör"* diyor. Ölçüldü (2026-08-04): motor **15** konnektör
    taşıyor (`base`/`factory` altyapıdır, konnektör değil), backend **4**'ünü kullanıyor
    (`duckdb` · `mssql` · `oracle` · `postgres`) → **11** hiç geçmiyor.

    *Bir sayıyı düzeltmek onu küçültmek değildir: 11 konnektör hâlâ "kod yazmadan yeni
    müşteri" demektir.*
    """
    hepsi, kullanilan = _envanter()
    kullanilmayan = sorted(set(hepsi) - set(kullanilan))
    assert len(hepsi) == 15, f"motor konnektör sayısı değişmiş: {len(hepsi)} ({hepsi})"
    assert len(kullanilmayan) == 11, (
        f"kullanılmayan konnektör {len(kullanilmayan)}: {kullanilmayan} — "
        "sayı değiştiyse bu test GÜNCELLENMELİ, sessizce geçilmemeli")
    assert {"bigquery", "snowflake", "databricks", "trino"} <= set(kullanilmayan)


def test_UCTAN_UCA_KOSUM_OLCULEMEDI_ve_YAZILI():
    """🔴 *Ölçülemeyeni yeşil saymak, "risk yok" yalanı üretir.* Maddenin kapısı **canlı
    bir müşteri DB'si** ister; `--network none` altında yapılamaz. Bu test o boşluğu
    **kapı olarak** tutuyor: koşum yapıldığında burası **ters çevrilir**, silinmez."""
    kaynak = pathlib.Path(__file__).read_text(encoding="utf-8")
    assert "⊘ ÖLÇÜLEMEDİ" in kaynak and "canlı müşteri veri tabanı" in kaynak


def test_ZINCIRIN_HALKALARI_VAR():
    """⚠ Zincir **koşulamadı** ama halkaları **var olmalı** — biri silinirse koşum
    imkânsızlaşır ve madde sessizce ölür."""
    assert (KOK / "app" / "db_introspect.py").is_file()
    assert (KOK / "app" / "mdl_writer.py").is_file()
    kaynak = (KOK / "app" / "mdl_writer.py").read_text(encoding="utf-8")
    assert "write_introspected_schema" in kaynak
    # İnsan onayı halkası: sihirbazın confirm ucu.
    uclar = (KOK / "app" / "routers" / "connections.py").read_text(encoding="utf-8")
    assert "/{cid}/confirm" in uclar and "/{cid}/draft" in uclar
