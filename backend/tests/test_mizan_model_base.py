"""FAZ 2.1 — `mizan` cube'u VIEW yerine MODEL tabanlı.

`mizan_kaynak` view'ı `yevmiye_satirlari ⟕ hesap_plani ⟕ yevmiye_fisleri`'ni elle
düzleştiriyordu. Her iki ilişki de ZATEN beyan edilmişti ve ikisi de hedef tarafın
PRIMARY KEY'i üzerinden gidiyor (`hesap_plani.hesap_kodu`, `yevmiye_fisleri.fis_no`),
yani üretecin G1 kapısından sorunsuz geçiyorlar.

Kazanç yalnız bakım değil, **performans**: `statements.py` (gelir tablosu / bilanço)
yalnız `hesap_kodu` + `bakiye` istiyor ve ikisi de `yevmiye_satirlari`'nda YEREL.
Join pruning sayesinde o sorgu artık **2 join yerine 0 join** — üç tablo yerine tek tablo.

Göç iki ince noktayla karşılaştı ve ikisi de üretecin `dimension: false` seçeneğini
doğurdu (bkz. `app/compose.py`): `hesap_adi` düz bir kolon değil, cube onu COALESCE ile
sarmalıyor (boş ad → hesap kodu); `tarih` ise satırda yok, fişten geliyor ve bir ZAMAN
boyutu — üreteç `time_dimensions`'a ekleme yapmıyor, bağ elle kuruluyor.
"""

from __future__ import annotations

import pytest

from tests.conftest import ask


@pytest.fixture(scope="module")
def svc_ve_db():
    """Servis + salt-okunur DuckDB — veri davranışını yönlendirmeden BAĞIMSIZ sınamak için."""
    import duckdb

    from app.config import get_settings
    from app.wren_service import WrenService

    s = get_settings()
    svc = WrenService(s.resolved_project_dir(), datasource=s.datasource,
                      connection_info=s.connection_dict())
    con = duckdb.connect(str((s.connection_dict() or {}).get("path")
                             or "demo/data/boyahane.duckdb"), read_only=True)
    try:
        yield svc, con
    finally:
        con.close()


@pytest.fixture(scope="module")
def mizan(schema):
    c = next((x for x in schema["cubes"] if x["name"] == "mizan"), None)
    assert c, "mizan cube'u katalogda yok"
    return c


def test_base_object_MODEL_olmali(mizan, schema):
    assert mizan["base_object"] == "yevmiye_satirlari", (
        f"geçiş geri alınmış: {mizan['base_object']!r}")
    assert mizan["base_object"] in {m["name"] for m in schema.get("models", [])}


def test_gereksiz_boyut_YAYINLANMADI(mizan):
    """`tarih` ve `hesap_adi` için `dimension: false` kullanıldı — üreteç yalnız calc
    kolonu üretti. Aksi halde aynı kolon hem boyut hem zaman-boyutu olarak görünür ve
    router yüzeyi gereksiz büyürdü.

    Testin koruduğu şey **`dimension: false` mekanizmasıdır**, katalog büyüklüğü değil:
    `tarih` boyut listesine SIZMAMALI (zaman-boyutu olarak ayrıca var) ve `hesap_adi`
    ÇİFTLENMEMELİ (cube'un elle tanımı kazanır, üreteç atlar). Faz D1'de bilinçli olarak
    iki gerçek kırılım eklendi (`hesap_tipi`, `ana_grup`) — o yüzden liste ARTAR, ama
    yasak iki durum yine yasaktır."""
    dims = mizan["dimensions"]
    assert "tarih" not in dims, "zaman boyutu ayrıca boyut olarak da yayımlanmış"
    assert len(dims) == len(set(dims)), f"boyut çiftlendi: {dims}"
    assert {"hesap_kodu", "hesap_adi"} <= set(dims)
    assert mizan["time_dimensions"] == ["tarih"]


def test_statements_sorgusu_SIFIR_JOIN_uretir():
    """Performans kilidi: gelir tablosu/bilanço yolunun join'siz kalması.

    `statements.py:134` tam olarak bu cube_query'yi kuruyor. View tabanlıyken 2 join
    üretiyordu (hesap_plani + yevmiye_fisleri gereksiz yere), şimdi 0.
    """
    from app.config import get_settings
    from app.wren_service import WrenService

    s = get_settings()
    svc = WrenService(s.resolved_project_dir(), datasource=s.datasource,
                      connection_info=s.connection_dict())
    plan = svc.dry_plan(svc.cube_sql(
        {"cube": "mizan", "measures": ["bakiye"], "dimensions": ["hesap_kodu"]}))
    assert plan.upper().count(" JOIN ") == 0, "yerel kolonlar için gereksiz JOIN üretildi"


def test_hesap_adi_COALESCE_davranisi_KORUNDU(svc_ve_db):
    """Hesap planında ad boşsa hesap KODU gösterilir — view'daki
    `COALESCE(NULLIF(h.hesap_adi,''), y.hesap_kodu)` davranışı cube ifadesine taşındı.

    Bilinçli olarak `/ask` yerine SERVİS katmanında sınanır: burada ölçülen şey VERİ
    davranışıdır, yönlendirme değil. (Bare "bakiye" zaten ayırt edici değil — hem `mizan`
    hem `cari` o ölçüyü taşıyor, bkz. Faz 3.1.)
    """
    svc, con = svc_ve_db
    sql = svc.dry_plan(svc.cube_sql(
        {"cube": "mizan", "measures": ["bakiye"], "dimensions": ["hesap_adi"]}))
    rows = con.execute(sql.replace('boyahane."main".', "main.")).fetchall()
    assert rows, "hesap adı kırılımı boş döndü"
    assert all(r[0] for r in rows), "boş hesap adı sızdı — COALESCE kaybolmuş olabilir"


def test_tarih_zaman_boyutu_FISTEN_gelir_ve_JOIN_kurar(svc_ve_db):
    """`tarih` `yevmiye_satirlari`'nda YOK; `yevmiye_fisleri`'nden ilişki üzerinden gelir.
    Zaman kovası çalışıyorsa join gerçekten kuruluyor demektir."""
    svc, con = svc_ve_db
    plan = svc.dry_plan(svc.cube_sql(
        {"cube": "mizan", "measures": ["bakiye"],
         "timeDimensions": [{"dimension": "tarih", "granularity": "month"}]}))
    assert plan.upper().count(" JOIN ") >= 1, "fiş tarihi için JOIN kurulmadı"
    rows = con.execute(plan.replace('boyahane."main".', "main.")).fetchall()
    assert len(rows) > 1, f"aylık kova tek satır döndü: {rows}"


def test_gelir_tablosu_HALA_calisiyor(client):
    """`statements.py` bu cube'a bağlı — göç onu bozmamalı (en yüksek riskli tüketici)."""
    d = ask(client, "gelir tablosu")
    assert d.get("source") == "statement", f"gelir tablosu bozuldu: {d.get('note')}"
    assert d.get("result") and d["result"]["rows"]
