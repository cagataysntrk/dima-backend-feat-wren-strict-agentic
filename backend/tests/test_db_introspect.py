"""Faz 4.5 (31 Temmuz 2026) — gerçek DB introspection + taslak MDL üretimi. Dış yol
haritasının UC-1.19 ("yeni bir DB bağlanır → en az 5 çalışan metrik önerilir") ve UC-1.20
("yanlış şifre → anlaşılır Türkçe hata, yığın izi sızmaz") kabul testlerinin karşılığı
burada (doğrulama turu düzeltmesi, 1 Ağustos 2026).

`introspect_schema`/`draft_mdl` SQLAlchemy'nin dialect-AGNOSTIK `inspect()` API'sini
kullanır — bu testler SQLite üzerinden çalışır (bu ortamda canlı bir Postgres sunucusu
yok), ama ÇEKİRDEK introspection/sınıflandırma/ilişki-üretim mantığını GERÇEKTEN
egzersiz eder (mock değil — gerçek FK reflection). Yalnız `build_sqlalchemy_url` (URL
string biçimi) Postgres'e özeldir, o ayrı ve bağlantısız test edilir."""

from __future__ import annotations

import pytest

from app.db_introspect import (
    ConnectionTestError,
    _friendly_connection_error,
    build_sqlalchemy_url,
    classify_column,
    draft_mdl,
    introspect_schema,
    check_connection,
)


@pytest.fixture
def sample_db_url(tmp_path):
    from sqlalchemy import create_engine, text

    db_path = tmp_path / "ornek.db"
    engine = create_engine(f"sqlite:///{db_path}")
    with engine.begin() as conn:
        conn.execute(text(
            "CREATE TABLE musteriler (id INTEGER PRIMARY KEY, ad VARCHAR(100))"
        ))
        conn.execute(text(
            "CREATE TABLE siparisler ("
            " id INTEGER PRIMARY KEY, musteri_id INTEGER, tutar NUMERIC,"
            " siparis_tarihi DATE,"
            " FOREIGN KEY (musteri_id) REFERENCES musteriler(id))"
        ))
    engine.dispose()
    return f"sqlite:///{db_path}"


def test_build_sqlalchemy_url_postgres():
    url = build_sqlalchemy_url("postgres", host="db.example.com", port=5432,
                               database="satis", user="dima", password="p@ss/w0rd")
    assert url.startswith("postgresql+psycopg://dima:")
    assert "@db.example.com:5432/satis" in url
    # şifredeki özel karakterler URL-encode edilmiş olmalı (çıplak "/" yok)
    assert "p@ss/w0rd" not in url


def test_build_sqlalchemy_url_rejects_unsupported_datasource():
    with pytest.raises(ValueError, match="Desteklenmeyen"):
        build_sqlalchemy_url("mysql", host="h", port=3306, database="d", user="u", password="p")


def test_check_connection_dry_run_success(sample_db_url):
    check_connection(sample_db_url)  # exception atmazsa başarılı


def test_check_connection_dry_run_failure_is_honest():
    with pytest.raises(ConnectionTestError):
        check_connection("postgresql+psycopg://nouser:nopass@127.0.0.1:1/hicbirsey",
                        timeout=1)


def test_check_connection_failure_message_is_turkish_not_raw_driver_text():
    """UC-1.20 (dış yol haritası, doğrulama turu düzeltmesi 1 Ağustos 2026): "DB
    bağlantısında yanlış şifre girilir → Anlaşılır Türkçe hata mesajı gösterilir; teknik
    yığın izi sızdırılmaz." Bağlanılamayan bir porta (127.0.0.1:1) deneme GERÇEK bir
    SQLAlchemy/psycopg istisnası üretir — mesaj bunun yerine sınıflandırılmış, Türkçe,
    eyleme-geçirilebilir bir metin OLMALI; ham sürücü ayrıntıları (İngilizce driver adı,
    DSN, "Traceback") kullanıcıya HİÇ ulaşmamalı."""
    try:
        check_connection("postgresql+psycopg://nouser:nopass@127.0.0.1:1/hicbirsey", timeout=1)
        pytest.fail("bağlanılamaz porta bağlanma HATA vermeliydi")
    except ConnectionTestError as exc:
        msg = str(exc)
        assert "kontrol" in msg.lower()  # eyleme geçirilebilir Türkçe mesajın imzası
        assert "traceback" not in msg.lower()
        assert "psycopg" not in msg.lower()


@pytest.mark.parametrize(
    "raw,expected_fragment",
    [
        ("FATAL: password authentication failed for user \"dima\"", "şifre yanlış"),
        ("could not translate host name \"bilinmeyen.local\" to address", "adresine ulaşılamadı"),
        ("connection to server at \"1.2.3.4\", port 5432 failed: Connection refused",
         "bağlanılamadı"),
        ("connection timed out", "zaman aşımına"),
        ("FATAL: database \"yoktur\" does not exist", "bulunamadı"),
        ("some totally unrecognized driver internals #4711", "kontrol edin"),
    ],
)
def test_friendly_connection_error_classifies_common_driver_failures(raw, expected_fragment):
    """Her yaygın sürücü-hatası SINIFI, teknik-olmayan bir kullanıcının anlayacağı bir
    Türkçe mesaja eşlenir (UC-1.20) — tanınmayan bir hata bile dürüst, jenerik bir Türkçe
    mesaja düşer (asla ham istisna metni geri dönmez)."""
    friendly = _friendly_connection_error(Exception(raw))
    assert expected_fragment in friendly.lower()
    assert raw.lower() not in friendly.lower()


def test_introspect_schema_reads_tables_columns_and_fk(sample_db_url):
    tables = introspect_schema(sample_db_url)
    names = {t.name for t in tables}
    assert names == {"musteriler", "siparisler"}

    siparisler = next(t for t in tables if t.name == "siparisler")
    assert {c.name for c in siparisler.columns} == {"id", "musteri_id", "tutar", "siparis_tarihi"}
    assert next(c for c in siparisler.columns if c.name == "id").is_primary_key

    assert len(siparisler.foreign_keys) == 1
    fk = siparisler.foreign_keys[0]
    assert fk.ref_table == "musteriler"
    assert fk.columns == ["musteri_id"]
    assert fk.ref_columns == ["id"]


def test_classify_column_pk_is_dimension_numeric_is_measure_date_is_time():
    from app.db_introspect import IntrospectedColumn

    assert classify_column(IntrospectedColumn("id", "INTEGER", is_primary_key=True)) == "dimension"
    assert classify_column(IntrospectedColumn("tutar", "NUMERIC")) == "measure"
    assert classify_column(IntrospectedColumn("siparis_tarihi", "DATE")) == "time"
    assert classify_column(IntrospectedColumn("ad", "VARCHAR")) == "dimension"


def test_draft_mdl_classifies_and_derives_relationships(sample_db_url):
    tables = introspect_schema(sample_db_url)
    draft = draft_mdl(tables)

    cubes = {c["name"]: c for c in draft["cubes"]}
    assert set(cubes) == {"musteriler", "siparisler"}

    siparisler = cubes["siparisler"]
    assert siparisler["measures"] == ["tutar"]
    assert siparisler["time_dimensions"] == ["siparis_tarihi"]
    # FK kolonu (musteri_id) SAYISAL olmasına rağmen ölçü DEĞİL, boyut olmalı (join anahtarı).
    assert "musteri_id" in siparisler["dimensions"]
    assert "musteri_id" not in siparisler["measures"]
    assert siparisler["primary_key"] == "id"

    assert len(draft["relationships"]) == 1
    rel = draft["relationships"][0]
    assert set(rel["models"]) == {"siparisler", "musteriler"}
    assert rel["join_type"] == "MANY_TO_ONE"
    assert rel["condition"] == "siparisler.musteri_id = musteriler.id"


def test_draft_mdl_skips_fk_pointing_outside_introspected_set():
    from app.db_introspect import IntrospectedColumn, IntrospectedForeignKey, IntrospectedTable

    tables = [
        IntrospectedTable(
            name="siparisler",
            columns=[IntrospectedColumn("id", "INTEGER", is_primary_key=True),
                    IntrospectedColumn("harici_id", "INTEGER")],
            foreign_keys=[IntrospectedForeignKey(["harici_id"], "disaridaki_tablo", ["id"])],
        ),
    ]
    draft = draft_mdl(tables)
    assert draft["relationships"] == []  # bozuk/eksik join tanımlanmaz


def test_draft_mdl_suggests_at_least_five_measures_for_realistic_schema(tmp_path):
    """UC-1.19 (dış yol haritası): "Yeni bir veritabanı bağlanır → 10 dakika içinde EN AZ
    5 ÇALIŞAN METRİK önerilir ve onaylanabilir." `sample_db_url`'in 2-tablolu minik şeması
    (yalnız 1 ölçü: `tutar`) bu ölçütü hiçbir zaman kanıtlayamaz — bu yüzden 3 tablolu,
    gerçekçi bir e-ticaret şemasıyla (ürünler+siparişler+müşteriler) `draft_mdl`'in
    ÜRETTİĞİ TOPLAM ölçü sayısının somut olarak ≥5 olduğu burada doğrudan kanıtlanır."""
    from sqlalchemy import create_engine, text

    db_path = tmp_path / "eticaret.db"
    engine = create_engine(f"sqlite:///{db_path}")
    with engine.begin() as conn:
        conn.execute(text(
            "CREATE TABLE musteriler (id INTEGER PRIMARY KEY, ad VARCHAR(100))"
        ))
        conn.execute(text(
            "CREATE TABLE urunler (id INTEGER PRIMARY KEY, ad VARCHAR(100),"
            " fiyat NUMERIC, stok_adet INTEGER)"
        ))
        conn.execute(text(
            "CREATE TABLE siparisler ("
            " id INTEGER PRIMARY KEY, musteri_id INTEGER, urun_id INTEGER,"
            " adet INTEGER, tutar NUMERIC, kdv_tutari NUMERIC, siparis_tarihi DATE,"
            " FOREIGN KEY (musteri_id) REFERENCES musteriler(id),"
            " FOREIGN KEY (urun_id) REFERENCES urunler(id))"
        ))
    engine.dispose()

    tables = introspect_schema(f"sqlite:///{db_path}")
    draft = draft_mdl(tables)

    total_measures = sum(len(c["measures"]) for c in draft["cubes"])
    assert total_measures >= 5, (
        f"UC-1.19 en az 5 metrik bekliyor, yalnız {total_measures} bulundu: "
        f"{[(c['name'], c['measures']) for c in draft['cubes']]}"
    )
    # İki gerçek FK ilişkisi de (siparişler→müşteriler, siparişler→ürünler) yakalanmalı —
    # "10 dakikada en az 5 metrik ÖNERİLİR" yalnız ölçü sayısı değil, kullanılabilir
    # (ilişkili) bir modeldir.
    assert len(draft["relationships"]) == 2
