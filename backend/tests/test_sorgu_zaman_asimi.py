"""FAZ B — sorgu ZAMAN AŞIMI: motorun mssql'i unuttuğu yer.

## Ölçülen boşluk (2 Ağustos 2026)

`wren.model.data_source.DataSource.get_connection_info()` `statement_timeout`'u **yalnız
dört** datasource için enjekte ediyor — ölçüldü, `match` dalları şunlar:

    case DataSource.postgres:      # -c statement_timeout=180s
    case DataSource.clickhouse:    # max_execution_time=180
    case DataSource.trino:         # query_max_execution_time=180s
    case DataSource.bigquery:

**`mssql` dalı YOK.** Konnektör onu *onurlandırıyor* —
`connector/mssql.py`: `connection.timeout = statement_timeout` — ama **kimse geçmiyordu**.
Ve üretimdeki tenant'larımız (gitas, atiksan) tam olarak **mssql**.

Sonuç: mssql'de kilitlenmiş bir sorgu **süresiz** asılabilir ve isteği de kendisiyle
birlikte askıya alır. postgres'te 180 sn — bir toplu iş için makul, **etkileşimli bir BI
cevabı için değil**.

## `_db_reachable` YERİNE GEÇMEZ, tamamlar

Plan bu maddeyi *"TCP ping'in yerine gerçek sorgu zaman aşımı"* diye yazmıştı. Ölçünce
ikisinin **farklı şeyleri** yakaladığı görüldü:

| | TCP ping | statement timeout |
|---|---|---|
| Tünel düşmüş (canlı olay 2026-07-25) | ✅ 3 sn'de | ❌ hiç bağlanamaz |
| DB ayakta, sorgu kilitli | ❌ **anında "erişilebilir" der** | ✅ |

Birini ötekinin "yerine" saymak, kapanmamış bir boşluğu kapanmış göstermek olurdu.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.wren_service import WrenService


def _svc(datasource: str, info: dict | None = None) -> WrenService:
    # `info or {...}` YAZILMAZ: BOŞ SÖZLÜK falsy'dir ve `{}` geçen test sessizce varsayılan
    # (host'lu) bağlantıyı alırdı — testin ölçtüğü şeyin tam tersi. `is None` ile ayrılır.
    if info is None:
        info = {"host": "h", "port": "1433", "database": "d", "user": "u"}
    return WrenService(Path("demo/wren-project"), datasource=datasource,
                       connection_info=info)


@pytest.fixture(autouse=True)
def _varsayilan(monkeypatch):
    """Ayarları testin kontrolüne al — `get_settings` önbelleklidir."""
    from app import config

    def _kur(sure: int = 60):
        s = config.get_settings()
        monkeypatch.setattr(s, "db_statement_timeout", sure, raising=False)
        return s
    _kur()
    return _kur


# --- ASIL KAPI: mssql artık zaman aşımı alıyor -----------------------------------

def test_MSSQL_sorgu_zaman_asimi_ALIR():
    """Motorun `get_connection_info`'sunda mssql dalı YOK; bu enjeksiyon olmadan
    kilitlenmiş bir sorgu SÜRESİZ asılırdı."""
    kw = _svc("mssql")._zaman_asimli_baglanti()["kwargs"]
    assert kw["statement_timeout"] == 60


def test_MSSQL_baglanti_zaman_asimi_da_ALIR():
    """Sorgu zaman aşımı yetmez: bir tünel düştüğünde asılma BAĞLANTI kurulurken olur.
    Bilinmeyen kwargs ODBC bağlantı dizesine aynen eklenir (`{key}={value}`)."""
    kw = _svc("mssql")._zaman_asimli_baglanti()["kwargs"]
    assert kw["Connect Timeout"] == "15"


def test_MSSQL_mevcut_kwargs_KORUNUR():
    """`TrustServerCertificate` kayıt defterinden geliyor — üstüne yazmak TLS davranışını
    sessizce değiştirirdi."""
    kw = _svc("mssql", {"host": "h", "kwargs": {"TrustServerCertificate": "yes"}}
              )._zaman_asimli_baglanti()["kwargs"]
    assert kw["TrustServerCertificate"] == "yes" and kw["statement_timeout"] == 60


def test_ACIK_BEYAN_ezilmez():
    """Bağlantıda zaten bir `statement_timeout` varsa o kazanır: bir tenant'a özel
    ayarlanmış değeri global varsayılanla ezmek, ayarı anlamsız kılardı."""
    kw = _svc("mssql", {"host": "h", "kwargs": {"statement_timeout": 5}}
              )._zaman_asimli_baglanti()["kwargs"]
    assert kw["statement_timeout"] == 5


# --- postgres: 180 sn etkileşimli için fazla --------------------------------------

def test_POSTGRES_bizim_degerimiz_MOTORUNKINI_yener():
    """Motor `if "statement_timeout" not in options` diye bakar — options'ı ÖNCEDEN
    doldurursak varsayılan 180 sn devreye girmez."""
    kw = _svc("postgres", {"host": "h"})._zaman_asimli_baglanti()["kwargs"]
    assert "statement_timeout=60s" in kw["options"]
    assert "180" not in kw["options"]


def test_POSTGRES_mevcut_options_KORUNUR():
    kw = _svc("postgres", {"host": "h", "kwargs": {"options": "-c search_path=x"}}
              )._zaman_asimli_baglanti()["kwargs"]
    assert "search_path=x" in kw["options"] and "statement_timeout=60s" in kw["options"]


def test_POSTGRES_options_ICINDE_beyan_varsa_dokunulmaz():
    kw = _svc("postgres", {"host": "h",
                           "kwargs": {"options": "-c statement_timeout=5s"}}
              )._zaman_asimli_baglanti()["kwargs"]
    assert kw["options"] == "-c statement_timeout=5s"


def test_POSTGRES_baglanti_zaman_asimi_kisaltilir():
    """Motorun varsayılanı 120 sn: bir tünel düştüğünde istek o kadar asılırdı."""
    assert _svc("postgres", {"host": "h"})._zaman_asimli_baglanti()["kwargs"][
        "connect_timeout"] == 15


# --- SINIRLAR: sessizce genişletilmez ---------------------------------------------

def test_DUCKDB_dokunulmaz():
    """Gömülü: ağ yok, kilitlenecek uzak sunucu yok. Zaman aşımı enjekte etmek
    anlamsız bir kwargs eklerdi."""
    info = {"url": "demo/data", "format": "duckdb"}
    assert _svc("duckdb", info)._zaman_asimli_baglanti() == info


def test_BILINMEYEN_datasource_a_zaman_asimi_UYDURULMAZ():
    """Konnektörün beklemediği bir anahtarla bağlantıyı KIRMAK, zaman aşımı olmamasından
    kötüdür. Motorun kendi varsayılanı geçerli kalır ve bu SESSİZ DEĞİL (debug log)."""
    info = {"host": "h", "port": "9000"}
    assert _svc("clickhouse", info)._zaman_asimli_baglanti() == info
    assert _svc("snowflake", info)._zaman_asimli_baglanti() == info


def test_SIFIR_ayarla_KAPATILABILIR(_varsayilan):
    """Acil durumda geri alınabilir olmalı: bir müşterinin meşru ağır sorgusu 60 sn'yi
    aşıyorsa, ürünü kırmadan ayarla açılabilmeli."""
    _varsayilan(0)
    info = {"host": "h"}
    assert _svc("mssql", info)._zaman_asimli_baglanti() == info


def test_KAYNAK_SOZLUGU_MUTASYONA_ugramaz():
    """`connection_info` servis ömrü boyunca paylaşılan bir sözlüktür; onu yerinde
    değiştirmek her `_engine()` çağrısında birikirdi."""
    info = {"host": "h", "kwargs": {"TrustServerCertificate": "yes"}}
    svc = _svc("mssql", info)
    svc._zaman_asimli_baglanti()
    svc._zaman_asimli_baglanti()
    assert info == {"host": "h", "kwargs": {"TrustServerCertificate": "yes"}}


# --- HER İKİ YOL: motor VE ham konnektör -----------------------------------------

def test_HAM_KONNEKTOR_de_ayni_bilgiyi_alir():
    """Canlı olayda (2026-07-25) `/schema`'yı asan sorgular tam olarak bu yoldan geçen
    DEĞER İNDEKSİ sorgularıydı. Motor yolunu korurken ham konnektörü korumasız bırakmak,
    kapıyı kilitleyip pencereyi açık unutmak olurdu."""
    import inspect

    govde = inspect.getsource(WrenService._connector)
    assert "_zaman_asimli_baglanti" in govde, "ham konnektör zaman aşımı ALMIYOR"
    assert "dict(self.connection_info)" not in govde, "eski çıplak bağlantı hâlâ geçiliyor"


def test_MOTOR_yolu_da_alir():
    import inspect

    govde = inspect.getsource(WrenService._engine)
    assert "_zaman_asimli_baglanti" in govde


def test_TCP_PING_kaldirilmadi():
    """`_db_reachable` YERİNE geçilmedi, TAMAMLANDI: TCP ping düşmüş bir tüneli 3 sn'de
    yakalar; statement_timeout onu hiç yakalayamaz (bağlantı bile kurulmaz). Kaldırmak,
    kapanmamış bir boşluğu kapanmış göstermek olurdu."""
    assert hasattr(WrenService, "_db_reachable")


def test_BOS_baglantiya_DOKUNULMAZ():
    """`dry_plan` DB'ye HİÇ bağlanmaz ve o yolda `connection_info={}` geçmek meşrudur
    (transpile + model CTE'leri yeter). Böyle bir sözlüğe `kwargs` eklemek onu "eksik bir
    GERÇEK bağlantı"ya çevirir ve motorun pydantic doğrulaması patlar.

    Bu senaryo UYDURMA DEĞİL: ilk sürüm tam olarak burada kırıldı
    (`test_gitas_calculated_ad_kolonlari` — mssql + boş bağlantı + `dry_plan`).
    """
    assert _svc("mssql", {})._zaman_asimli_baglanti() == {}
    assert _svc("postgres", {})._zaman_asimli_baglanti() == {}


def test_URL_ile_verilen_baglanti_da_HEDEFLIDIR():
    """Hedef `host` ile gelmek zorunda değil: `connectionUrl`/`url` de gerçek bir
    bağlantıdır ve zaman aşımını almalı."""
    kw = _svc("postgres", {"connectionUrl": "postgresql://h/db"}
              )._zaman_asimli_baglanti().get("kwargs") or {}
    assert "statement_timeout=60s" in (kw.get("options") or "")
