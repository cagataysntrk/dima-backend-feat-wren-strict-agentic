"""Faz 4.7a araştırma bulgusunun testi: view fan-out sağlık kontrolü (31 Temmuz/1 Ağustos
2026 — dış yol haritası 1.11c "metrik tuzakları: fan-out").

**4.7a araştırması (kod değişikliği YOK, yalnız kanıt topladı)** somut bir fan-out riski
KANITLADI: `parti` cube'unun `base_object`'i olan `parti_zengin` view'ı `partiler`ı
`personel.ad_soyad` (BENZERSİZLİĞİ VERİTABANI SEVİYESİNDE GARANTİ EDİLMEYEN bir metin
alanı — iki farklı çalışan aynı ada sahip olabilir) üzerinden LEFT JOIN'liyor. Bugünkü
demo verisinde (29 personel, sıfır tekrar eden isim — ampirik olarak doğrulandı) bu
YANLIŞLIKLA güvenli; YAPISAL bir koruma YOKTU. `makine_duruslari` cube'undaki fan-out
yorumunun (bkz. o dosya) ele aldığı risk (İKİ FARKLI GRAIN'İ AYNI cube'da birleştirmek)
BUNDAN FARKLI bir sınıf: burası bir cube'un KENDİ view'ının İÇİNDEKİ bir JOIN riski.

**4.7b (araştırma OLUMLU çıktığı için, en az invaziv düzeltme)**: mevcut `dry_plan`/cube
derleme mekanizmasına DOKUNMADAN, YENİ bir REGRESYON TESTİ eklendi — her view'ın satır
sayısının kendi TEMEL (FROM'daki ilk) tablosunu AŞMADIĞINI doğrular. Bugün YEŞİL (kanıt:
mevcut sistem sağlıklı) — ama biri ileride bir view'a fan-out yaratan bir JOIN eklerse
(ya da demo verisine tesadüfen aynı isimli iki personel eklenirse) bu test KIRILIR ve
sorunu ÜRETİME gitmeden yakalar. `MetricDefinition` gibi daha büyük, YENİ bir katman
GEREKMEDİ — araştırma bunu somut bir ihtiyaçla DOĞRULAYAMADI, bu yüzden bilinçli olarak
yapılmadı (UC-1.14 budur — bu test ONUN karşılığıdır).

**4.7a'nın İKİNCİ araştırma bacağı — mali takvim/kur (UC-1.15), 1 Ağustos 2026 doğrulama
turunda TAMAMLANDI**: `control_plane/models.py::TenantConfig`'te mali-yıl-başlangıcı türünde
HİÇBİR alan YOK (`donem_no` LOGO ERP'nin tablo-önekindeki PERİYOT NUMARASIDIR — ör.
`LG_121_01_STLINE` — mali yılın HANGİ AYDA başladığıyla İLGİSİZ bir kavram, salt şema
isimlendirmesi). `app/cube_router.py`'nin "geçen ay/geçen yıl" çözümleyicisi (`_prev_period_
filters` ve komşuları) HER ZAMAN takvim (Ocak-Aralık) sınırları kullanır. `demo/companies/*`
altındaki (gulteks, demo-boyahane, gitas, atiksan) HİÇBİR şirket fixture'ı takvim-dışı bir
mali yıl BEYAN ETMİYOR — Türk Ticaret Kanunu'nda da varsayılan mali yıl takvim yılıdır,
farklısı (yabancı ana şirkete hizalanmış nadir istisnalar dışında) olağan değildir. Sonuç:
bu ihtiyaç bugün TAMAMEN VARSAYIMSAL — hiçbir gerçek/demo/lab tenant'ında somutlaşmıyor. Bu
yüzden `TenantConfig`'e mali-yıl alanı eklemek/`cube_router`'ı DEĞİŞTİRMEK bilinçli olarak
YAPILMADI (4.7b ilkesi: kanıtlanmamış ihtiyaç için altyapı kurulmaz) — bir müşteri GERÇEKTEN
takvim-dışı bir mali yılla gelirse bu o zaman, somut bir örnekle ele alınmalı."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml


def _view_files(project_dir: Path) -> list[Path]:
    views_dir = project_dir / "views"
    if not views_dir.is_dir():
        return []
    return sorted(views_dir.glob("*/metadata.yml"))


def _first_from_table(statement: str) -> str | None:
    m = re.search(r"\bFROM\s+([A-Za-z_][A-Za-z0-9_]*)", statement, re.IGNORECASE)
    return m.group(1) if m else None


@pytest.fixture(scope="module")
def duckdb_conn():
    """Ham SQL çalıştırmak için gerçek `WrenService` — motorun kendi DuckDB bağlantı
    yönetimini (CSV/parquet dizin bağlama, wren_core) YENİDEN İCAT ETMEDEN kullanır
    (aynı desen: tests/conftest.py::schema fixture'ı)."""
    from app.config import get_settings
    from app.wren_service import WrenService

    get_settings.cache_clear()
    settings = get_settings()
    svc = WrenService(
        project_dir=settings.resolved_project_dir(),
        datasource=settings.datasource,
        connection_info=settings.connection_dict(),
    )

    class _Conn:
        def execute(self, sql: str):
            result = svc.query(sql)
            return _Row(result["rows"][0]) if result["rows"] else _Row({})

    yield _Conn()


class _Row:
    def __init__(self, d: dict):
        self._values = list(d.values())

    def fetchone(self):
        return tuple(self._values)


def test_no_view_fans_out_relative_to_its_base_table(duckdb_conn):
    """HER view, KENDİ temel tablosundan DAHA FAZLA satır DÖNDÜRMEMELİ (LEFT JOIN'lerle
    zenginleştirme satır sayısını korumalı, çoğaltmamalı). Somut kanıtlanmış risk:
    parti_zengin (personel.ad_soyad üzerinden LEFT JOIN — benzersizliği GARANTİ edilmeyen
    bir alan) — bu test o riski GENEL bir kural olarak her view için sınar."""
    from app.config import get_settings

    settings = get_settings()
    views = _view_files(settings.resolved_project_dir())
    assert views, "beklenen en az bir view (parti_zengin/mizan_kaynak) bulunamadı"

    checked = 0
    for vf in views:
        data = yaml.safe_load(vf.read_text(encoding="utf-8")) or {}
        stmt = data.get("statement")
        if not stmt:
            continue
        base_table = _first_from_table(stmt)
        assert base_table, f"{vf}: FROM tablosu ayrıştırılamadı"
        base_count = duckdb_conn.execute(f"SELECT COUNT(*) FROM {base_table}").fetchone()[0]
        view_count = duckdb_conn.execute(f"SELECT COUNT(*) FROM ({stmt}) t").fetchone()[0]
        assert view_count <= base_count, (
            f"FAN-OUT: view '{data.get('name')}' ({vf}) temel tablosu '{base_table}' "
            f"({base_count} satır) yerine {view_count} satır döndürüyor — bir JOIN "
            f"çoğaltıyor olabilir (benzersizliği garanti edilmeyen bir anahtar kolonu ara)."
        )
        checked += 1
    assert checked >= 2  # bugün bilinen 2 view (parti_zengin, mizan_kaynak) mutlaka kapsanmalı


def test_parti_zengin_join_keys_are_currently_unique(duckdb_conn):
    """4.7a'nın SPESİFİK bulgusu: `parti_zengin`in join anahtarları (personel.ad_soyad,
    personel_ozluk.personel_kodu) bugün BENZERSİZ (bu YÜZDEN fan-out olmuyor) — ama bu
    veri-bağımlı bir gerçektir, ŞEMA GARANTİSİ değil. Bu test bunu AÇIKÇA/ayrı ölçer ki
    "neden bugün güvenli" sorusunun kanıtı `test_no_view_fans_out_...`'tan BAĞIMSIZ okunsun."""
    dup_ad_soyad = duckdb_conn.execute(
        "SELECT COUNT(*) FROM (SELECT ad_soyad FROM personel "
        "GROUP BY ad_soyad HAVING COUNT(*) > 1)"
    ).fetchone()[0]
    dup_personel_kodu = duckdb_conn.execute(
        "SELECT COUNT(*) FROM (SELECT personel_kodu FROM personel_ozluk "
        "GROUP BY personel_kodu HAVING COUNT(*) > 1)"
    ).fetchone()[0]
    assert dup_ad_soyad == 0, (
        "personel.ad_soyad'da tekrar eden isim bulundu — parti_zengin'in LEFT JOIN'i "
        "artık fan-out YARATIYOR OLABİLİR (bkz. test_no_view_fans_out_relative_to_its_base_table)."
    )
    assert dup_personel_kodu == 0
