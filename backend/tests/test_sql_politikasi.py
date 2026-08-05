"""FAZ A3 — motor-seviyesi SQL politikası (`WrenConfig` / `wren.policy`).

Denetimde ölçüldü: Dima 69 dosyalık `wren` paketinden **3 sembol** kullanıyor (~%4) ve
kullanılmayanların en değerlisi `wren/policy.py`. `WrenEngine` **`config` parametresi
alıyor** ama Dima hiç geçirmiyordu → `strict_mode=False` → politika motoru **ölü kod**.

`validate_sql_policy` strict modda iki iş yapar:
1. **45 veri-okuyucu tablo fonksiyonunu** (`read_csv`, `read_parquet`, `pg_read_file`,
   `dblink`, `postgres_scan`, …) SQL'in **her** konumunda bloklar (upstream bunu bir
   güvenlik açığı olarak kapattı — issue #2409);
2. MDL'de **tanımlı olmayan** tabloya referansı reddeder.

Dima'nın `guard_sql`'i iki regex'tir (`^(with|select)` + yasak kelime) ve bunların
**hiçbirini** yakalamaz: `SELECT * FROM read_csv('/etc/passwd')` ondan **geçer** (ölçüldü).
Bugün o sorgu yine de patlıyor — ama **DataFusion o fonksiyonu tanımadığı için**, yani
savunma **tesadüfi**, tasarlanmış değil. Fonksiyon kayıt defteri değişirse savunma kaybolur.

## Neden varsayılan `shadow`

Demo katalogunda strict hiçbir meşru yolu kırmıyor (ölçüldü: cube SQL, `always_filter`
sarmalayıcısı, üretilen-boyut join'i — üçü de aynen geçti; 47 tablonun 47'si de MDL'de).
Ama gerçek müşteri şemasında (binlerce tablo, MDL'de bir kısmı) Discovery'nin ham SQL'i
MDL-dışı bir tabloya dokunabilir. Bu **istenen** reddir (semantic-first) ama **ölçülmeden**
açılmamalı. `shadow` reddetmez, *"strict olsaydı reddedilirdi"* diye loglar; telemetri
birikince `on`a alınır. Bu, MIMARI'nin *"ölçülmemiş ihtiyaç için altyapı kurma"*
disiplininin tersten uygulanışıdır: **ölçmeden kısıtlama da getirme.**
"""

from __future__ import annotations

import pytest

SALDIRILAR = [
    ("dosya okuyucu", "SELECT * FROM read_csv('/etc/passwd')"),
    ("parquet okuyucu", "SELECT * FROM read_parquet('/tmp/x.parquet')"),
    ("MDL dışı tablo", "SELECT 1 FROM bilinmeyen_tablo_xyz"),
]


@pytest.fixture(scope="module")
def svc():
    from app.config import get_settings
    from app.wren_service import WrenService

    s = get_settings()
    return WrenService(s.resolved_project_dir(), datasource=s.datasource,
                       connection_info=s.connection_dict())


def _katı_motor(svc):
    from wren.config import WrenConfig
    from wren.engine import WrenEngine

    return WrenEngine(svc._manifest_b64(), svc.datasource, dict(svc.connection_info),
                      config=WrenConfig(strict_mode=True))


# --- guard_sql'in yakalayamadıkları (kusurun kaydı) ------------------------------

@pytest.mark.parametrize("ad,sql", SALDIRILAR, ids=[a[0] for a in SALDIRILAR])
def test_guard_sql_bunlari_YAKALAYAMAZ(ad, sql):
    """`guard_sql` bir SELECT-only kapısıdır, bir politika motoru DEĞİLDİR. Bu test onun
    sınırını kayda geçirir — "guard_sql var, yeterli" varsayımını imkânsız kılar."""
    from app.wren_service import guard_sql

    assert guard_sql(sql), f"{ad}: guard_sql beklenmedik şekilde reddetti"


# --- strict politikanın GERÇEKTEN çalıştığı -------------------------------------

@pytest.mark.parametrize("ad,sql", SALDIRILAR, ids=[a[0] for a in SALDIRILAR])
def test_strict_POLITIKAYLA_reddeder(svc, ad, sql):
    """Red mesajı politikadan gelmeli — DataFusion'ın "fonksiyon bulunamadı"sından değil.
    Fark önemli: biri tasarlanmış bir kontrol, öteki bir tesadüf."""
    with pytest.raises(BaseException) as e:  # noqa: PT011 — Rust PANIC Exception DEĞİL
        _katı_motor(svc).dry_plan(sql)
    mesaj = str(e.value).lower()
    assert ("not allowed" in mesaj or "not defined" in mesaj or "strict" in mesaj), (
        f"{ad}: red politikadan gelmedi, mesaj: {mesaj[:200]}")


def test_MESRU_yollar_strict_altinda_AYNEN_calisir(svc):
    """Açmanın bedeli ölçüldü: SIFIR. Üç meşru yol da katı motorda aynen geçmeli —
    (1) düz cube SQL, (2) `always_filter` sarmalayıcısı, (3) üretilen-boyut join'i."""
    kati = _katı_motor(svc)
    for ad, cq in (
        ("düz cube", {"cube": "parti", "measures": ["toplam_ciro"], "dimensions": ["makine"]}),
        ("türev boyut (join)", {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["bolum"]}),
        ("çok ölçü", {"cube": "kalite", "measures": ["toplam_rework_kg", "rework_sayisi"]}),
    ):
        sql = svc.cube_sql(cq)
        # ⚠ Ham `WrenEngine` **oturum özelliği taşımaz** — servis onu `_oturum_ozellikleri`
        # ile veriyor. `motor_cls=on` iken özelliksiz bir plan, strict yüzünden değil
        # **CLS yüzünden** patlar ve bu test *"strict meşru sorguyu kırdı"* diye YANLIŞ
        # bir sebep raporlardı. *Bir testin ortamı, taklit ettiği ortamla aynı olmalıdır.*
        assert kati.dry_plan(sql, svc._katalog_ozellikleri()), \
            f"{ad}: strict altında meşru sorgu kırıldı"


def test_demo_katalogunda_MDL_DISI_tablo_yok(svc):
    """Strict'in ikinci yarısı (MDL-dışı tablo reddi) demo'da hiçbir şeyi kırmaz çünkü
    47 tablonun 47'si de MDL'de. Bu, `on`a geçişin demo tarafındaki risksizliğinin kaydı;
    gerçek müşteride aynı şey GEÇERLİ DEĞİLDİR ve gölge modu bu yüzden var."""
    import json

    import duckdb

    from app.config import get_settings

    s = get_settings()
    con = duckdb.connect(str((s.connection_dict() or {}).get("path")
                             or "demo/data/boyahane.duckdb"), read_only=True)
    try:
        tablolar = {r[0] for r in con.execute(
            "select table_name from information_schema.tables where table_schema='main'"
        ).fetchall()}
    finally:
        con.close()
    mdl = json.loads(svc.mdl_path.read_text(encoding="utf-8"))
    tanimli = {m["name"] for m in mdl.get("models", [])} | {v["name"] for v in mdl.get("views", [])}
    assert not (tablolar - tanimli), f"MDL dışında kalan tablo: {sorted(tablolar - tanimli)}"


# --- mod anahtarı ----------------------------------------------------------------

def test_varsayilan_mod_SHADOW(svc):
    """Ölçmeden kısıtlama getirme: varsayılan reddetmez, yalnız kaydeder."""
    assert svc._sql_policy()[1] == "shadow"


def test_shadow_REDDETMEZ_ama_LOGLAR(svc, caplog):
    """Gölge modun sözleşmesi: akış değişmez, kanıt birikir."""
    import logging

    with caplog.at_level(logging.WARNING):
        svc._shadow_policy_check("SELECT * FROM read_csv('/etc/passwd')")
    assert any("gölge" in r.message.lower() or "POLİTİKA" in r.message
               for r in caplog.records), "gölge ihlali loglanmadı"


def test_shadow_MESRU_sorguda_SUSAR(svc, caplog):
    """Gölge modu gürültü yapmamalı — yoksa log'da boğulur ve kanıt değerini kaybeder."""
    import logging

    sql = svc.cube_sql({"cube": "parti", "measures": ["toplam_ciro"]})
    with caplog.at_level(logging.WARNING):
        svc._shadow_policy_check(sql)
    assert not [r for r in caplog.records if "POLİTİKA" in r.message], \
        "meşru sorgu gölge modda uyarı üretti"


def test_mod_ON_iken_motor_KATI_kurulur(svc, monkeypatch):
    """`on`a alındığında normal akış (gölge değil) reddetmeli."""
    from app.config import get_settings

    s = get_settings()
    monkeypatch.setattr(s, "strict_sql_policy", "on", raising=False)
    assert svc._sql_policy()[0].strict_mode is True
    with pytest.raises(BaseException):  # noqa: PT011
        svc.dry_plan("SELECT * FROM read_csv('/etc/passwd')")


def test_gecersiz_mod_SHADOWA_duser(svc, monkeypatch):
    """Yanlış yapılandırma sessizce `off`a düşmemeli — güvenlik ayarında fail-open olmaz."""
    from app.config import get_settings

    monkeypatch.setattr(get_settings(), "strict_sql_policy", "saçmalık", raising=False)
    assert svc._sql_policy()[1] == "shadow"


def test_denied_functions_strict_OLMADAN_da_calisir(svc, monkeypatch):
    """`engine._plan` koşulu `or` — kara liste `off` modunda bile devrede olmalı."""
    from app.config import get_settings

    s = get_settings()
    monkeypatch.setattr(s, "strict_sql_policy", "off", raising=False)
    monkeypatch.setattr(s, "denied_sql_functions", "md5", raising=False)
    cfg, mod = svc._sql_policy()
    assert mod == "off" and cfg.strict_mode is False
    assert "md5" in cfg.denied_functions
