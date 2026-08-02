"""Gerçek müşteri veritabanı introspection'ı + taslak MDL üretimi (Faz 4.5, 31 Temmuz 2026
— dış yol haritası 1.1/1.2/1.4/1.8/kısmen 1.11a-e'nin GERÇEK-DB-ODAKLI karşılığı).

`app/dataset.py::build_mdl`'in Excel/CSV için yaptığının (tek tablo, TAHMİNİ sezgisel)
ÇOK-TABLOLU, GERÇEK ilişki-farkında karşılığı: burada ilişkiler FK'lerden İNTROSPECT
EDİLİR (tahmin değil, gerçek şema bilgisi) — bu yüzden Excel akışında (4.3, bilerek
DOKUNULMAYAN) yapılmayan ilişki-önerisi burada güvenilir ve değerlidir.

Kapsam (bu ilk sürüm): yalnız Postgres (`psycopg` zaten bağımlı — bkz. pyproject.toml).
MySQL dış yol haritasında anılıyor ama sürücüsü (`pymysql` ya da eşdeğeri) bu ortamda
KURULU DEĞİL — yeni bir üretim bağımlılığı eklemek ayrı, bilinçli bir karar olmalı, bu
yüzden BİLEREK ertelendi (sessizce yarım bırakılmadı — bu docstring'te açıkça belirtiliyor).
İntrospection'ın kendisi SQLAlchemy'nin `inspect()` API'siyle dialect-AGNOSTIK yazıldığı
için MySQL sürücüsü eklendiğinde yalnız `build_sqlalchemy_url` genişletilmesi yeterli olur.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# KANONİK tip kümeleri — motorun `wren.type_mapping.parse_type` çıktısı üstünde tanımlı.
#
# ÖNCEDEN ham DB yazımları elle listeleniyordu ve ölçüldü (2 Ağustos 2026): 17 gerçek tip
# yazımının **13'ü yanlış sınıflanıyordu**. Hepsi sessizce "dimension"a düşüyordu — yani
# `numeric(18,2)` (bir PARA TUTARI) kategorik boyut, `timestamptz` ise zaman DEĞİL
# sayılıyordu. Bir müşteri DB'sini introspect ettiğimizde taslak MDL, tutarları gruplama
# anahtarı yapıp tarihleri zaman ekseninden düşürürdü.
#
# Elle liste tutmak kaybedilen bir yarıştır: her lehçenin kendi yazımı var
# (`int8`/`int4`/`float8` postgres, `datetime2`/`smallmoney`/`tinyint` tsql,
# `HUGEINT`/`UBIGINT` duckdb) ve liste ancak biri kırılınca büyür. Motor bunu ZATEN
# çözüyor — MIMARI §5: **motor zaten yapıyorsa yazma.**
_NUMERIC_TYPES = {
    "INT", "INTEGER", "BIGINT", "SMALLINT", "TINYINT", "INT128", "INT256",
    "UTINYINT", "USMALLINT", "UINT", "UBIGINT",
    "DECIMAL", "FLOAT", "DOUBLE", "REAL", "MONEY", "SMALLMONEY",
}
# GERİYE UYUM kuyruğu — kanonik ADLAR DEĞİL, ham lehçe yazımları. Kanonikleştirici
# erişilemediğinde (import hatası) bugünkü davranış korunsun diye tutulur ve bilinçli
# olarak AYRI durur: karışık bir küme, hangi adın kanonik hangisinin yama olduğunu
# gizler ve zamanla "kanonik küme" iddiası çürür.
_ESKI_YAZIMLAR = {"NUMERIC", "DOUBLE PRECISION", "DATETIME2", "TIMESTAMP WITHOUT TIME ZONE",
                  "TIMESTAMP WITH TIME ZONE"}
_ESKI_SAYISAL = {"NUMERIC", "DOUBLE PRECISION"}
_ESKI_TARIH = {"DATETIME2", "TIMESTAMP WITHOUT TIME ZONE", "TIMESTAMP WITH TIME ZONE"}
# `BIT`/`BOOLEAN` bilinçli olarak DIŞARIDA: teknik olarak sayısaldır ama toplanması
# anlamsızdır (bayrakların toplamı bir ölçü değildir) → boyut kalır.
_DATE_TYPES = {"DATE", "DATETIME", "TIMESTAMP", "TIMESTAMPTZ", "TIMESTAMPLTZ",
               "TIMESTAMPNTZ", "TIME", "TIMETZ"}


def _kanonik_tip(ham: str, dialect: str = "postgres") -> str:
    """Ham DB tipini motorun kanonik adına çevirir (`int8` → `BIGINT`).

    Parametre kısmı atılır: `DECIMAL(18, 2)` → `DECIMAL`. Sınıflandırma ölçek/hassasiyete
    bakmaz; `DECIMAL(18,2)` ile `DECIMAL(4,0)` ikisi de ölçüdür.

    Motor çeviremezse **ham değere düşülür** — bugünkü davranış korunur. Fail-closed
    yapmak, tanımadığı bir tip yüzünden tüm introspection'ı durdurmak olurdu; oysa
    bilinmeyen tip için doğru varsayılan zaten "boyut"tur (en az iddialı sınıf).
    """
    try:
        from wren.type_mapping import parse_type

        kanon = parse_type(ham, dialect)
    except Exception:
        kanon = ham
    return str(kanon or "").split("(")[0].strip().upper()
_SUPPORTED_DATASOURCES = ("postgres",)


@dataclass
class IntrospectedColumn:
    name: str
    type: str
    nullable: bool = True
    is_primary_key: bool = False


@dataclass
class IntrospectedForeignKey:
    columns: list[str]
    ref_table: str
    ref_columns: list[str]


@dataclass
class IntrospectedTable:
    name: str
    columns: list[IntrospectedColumn] = field(default_factory=list)
    foreign_keys: list[IntrospectedForeignKey] = field(default_factory=list)


class ConnectionTestError(Exception):
    """Dry-run bağlantı denemesi başarısız (host/kimlik bilgisi/ağ) — dürüst mesaj taşır."""


def _friendly_connection_error(exc: Exception) -> str:
    """Ham sürücü/SQLAlchemy istisnasını (İNGİLİZCE, teknik jargonlu, bazen sunucu/DSN
    ayrıntısı taşıyan) teknik-olmayan bir kullanıcının anlayacağı, EYLEME GEÇİRİLEBİLİR bir
    TÜRKÇE mesaja çevirir (dış yol haritası UC-1.20: "Anlaşılır Türkçe hata mesajı
    gösterilir; teknik yığın izi sızdırılmaz"). Ham istisna metni BURADAN SONRA hiçbir
    yere taşınmaz — `check_connection` yalnız bu SINIFLANDIRILMIŞ mesajı döner."""
    text = str(exc).lower()
    if "password authentication failed" in text or "authentication failed" in text:
        return "Kullanıcı adı veya şifre yanlış — bilgileri kontrol edip tekrar deneyin."
    if ("could not translate host name" in text or "name or service not known" in text
            or "nodename nor servname" in text or "getaddrinfo failed" in text):
        return "Sunucu adresine ulaşılamadı — host adını kontrol edin."
    if "connection refused" in text or "could not connect to server" in text:
        return ("Sunucuya bağlanılamadı — adres/port doğru mu ve sunucu bu ağdan "
               "erişilebilir mi kontrol edin.")
    if "timeout" in text or "timed out" in text:
        return "Bağlantı zaman aşımına uğradı — sunucu adresini ve ağ erişimini kontrol edin."
    if "does not exist" in text or "unknown database" in text:
        return "Belirtilen veritabanı bulunamadı — veritabanı adını kontrol edin."
    return "Bağlantı kurulamadı — sunucu adresi, port, kullanıcı adı ve şifreyi kontrol edin."


def build_sqlalchemy_url(datasource: str, *, host: str, port: int, database: str,
                         user: str, password: str) -> str:
    """Yalnız Postgres desteklenir bu sürümde (bkz. modül docstring'i — MySQL bilerek
    ertelendi, yeni bağımlılık eklemeden desteklenemez)."""
    if datasource not in _SUPPORTED_DATASOURCES:
        raise ValueError(
            f"Desteklenmeyen datasource: {datasource!r} (bu sürümde yalnız "
            f"{', '.join(_SUPPORTED_DATASOURCES)} destekleniyor)"
        )
    from urllib.parse import quote_plus

    return (f"postgresql+psycopg://{quote_plus(user)}:{quote_plus(password)}"
           f"@{host}:{port}/{database}")


def check_connection(url: str, *, timeout: int = 5) -> None:
    """`SELECT 1` dry-run — yalnız bağlanabilirliği doğrular (introspection YAPMAZ).
    Başarısızsa `ConnectionTestError` (dürüst mesaj, ham sürücü hatası kırpılmış).
    `connect_timeout` yalnız Postgres'te anlamlı (psycopg) — testlerde kullanılan
    SQLite bu anahtar kelimeyi TANIMAZ, bu yüzden dialect'e göre koşullu eklenir."""
    from sqlalchemy import create_engine, text
    from sqlalchemy.exc import SQLAlchemyError

    connect_args = {"connect_timeout": timeout} if url.startswith("postgresql") else {}
    engine = create_engine(url, connect_args=connect_args)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise ConnectionTestError(_friendly_connection_error(exc)) from exc
    finally:
        engine.dispose()


def introspect_schema(url: str, *, max_tables: int = 50) -> list[IntrospectedTable]:
    """Gerçek şema introspection'ı — tablo/kolon/PK/FK (SQLAlchemy `inspect()`, dialect-
    agnostik: aynı kod Postgres/MySQL/SQLite'ta çalışır — yalnız `build_sqlalchemy_url`
    datasource'a özeldir). Sistem şeması (information_schema/pg_catalog) `inspect()`
    tarafından zaten hariç tutulur."""
    from sqlalchemy import create_engine, inspect

    engine = create_engine(url)
    try:
        insp = inspect(engine)
        tables: list[IntrospectedTable] = []
        for name in insp.get_table_names()[:max_tables]:
            pk_cols = set(insp.get_pk_constraint(name).get("constrained_columns") or [])
            columns = [
                IntrospectedColumn(
                    name=c["name"],
                    type=str(c["type"]).upper().split("(")[0].strip(),
                    nullable=bool(c.get("nullable", True)),
                    is_primary_key=c["name"] in pk_cols,
                )
                for c in insp.get_columns(name)
            ]
            foreign_keys = [
                IntrospectedForeignKey(
                    columns=list(fk["constrained_columns"]),
                    ref_table=fk["referred_table"],
                    ref_columns=list(fk["referred_columns"]),
                )
                for fk in insp.get_foreign_keys(name)
                if fk.get("referred_table")
            ]
            tables.append(IntrospectedTable(name=name, columns=columns, foreign_keys=foreign_keys))
        return tables
    finally:
        engine.dispose()


def classify_column(col: IntrospectedColumn, *, dialect: str = "postgres") -> str:
    """Ölçü mü / boyut mu / zaman mı — `app/dataset.py::build_mdl`'in tip-tabanlı
    sezgiseliyle TUTARLI: PK'ler kimlik/gruplama amaçlıdır (toplanmaz) → boyut; tarih/
    zaman damgası → zaman; sayısal (PK DEĞİLSE) → ölçü; geri kalan her şey → boyut.

    Tip adı **motorun kanonikleştiricisinden** geçer (Faz B): ham DB yazımlarını elle
    listelemek kaybedilen bir yarıştı — ölçüldü, 17 gerçek yazımın 13'ü kaçıyordu.
    """
    if col.is_primary_key:
        return "dimension"
    kanon = _kanonik_tip(col.type, dialect)
    if kanon in _DATE_TYPES or kanon in _ESKI_TARIH:
        return "time"
    if kanon in _NUMERIC_TYPES or kanon in _ESKI_SAYISAL:
        return "measure"
    return "dimension"


def draft_mdl(tables: list[IntrospectedTable]) -> dict:
    """Introspect edilmiş şemadan bir TASLAK üretir — hiçbir dosyaya YAZMAZ (yalnız
    kullanıcı onayından SONRA `app/mdl_writer.py::write_introspected_cubes` gerçek
    YAML'a döker). Şekil: {"cubes": [{name, measures, dimensions, time_dimensions,
    primary_key}], "relationships": [{name, join_type, models, condition}]}.

    Her tablo bir cube ADAYIDIR (kullanıcı onay ekranında hariç bırakabilir). İlişkiler
    yalnız HER İKİ ucu da introspect edilen tablo kümesinde olan FK'lerden üretilir
    (dışarıdaki bir tabloya işaret eden FK, o tablo dahil edilmediyse ATLANIR — bozuk
    bir join tanımlanmaz)."""
    by_name = {t.name for t in tables}
    cubes: list[dict] = []
    relationships: list[dict] = []
    for t in tables:
        # FK-kısıtlı kolonlar (sayısal tipte olsalar bile) JOIN ANAHTARIDIR, ölçü DEĞİL —
        # `classify_column` yalnız PK/tip bakar, FK bağlamını bilmez; bu yüzden burada
        # AYRICA ele alınır (ör. "siparisler.musteri_id" INTEGER'dır ama toplanmaz).
        fk_cols = {col for fk in t.foreign_keys for col in fk.columns}
        measures, dimensions, time_dims = [], [], []
        pk = None
        for c in t.columns:
            if c.is_primary_key and pk is None:
                pk = c.name
            if c.name in fk_cols:
                dimensions.append(c.name)
                continue
            kind = classify_column(c)
            if kind == "measure":
                measures.append(c.name)
            elif kind == "time":
                time_dims.append(c.name)
            else:
                dimensions.append(c.name)
        cubes.append({
            "name": t.name, "measures": measures, "dimensions": dimensions,
            "time_dimensions": time_dims, "primary_key": pk,
        })
        for fk in t.foreign_keys:
            if fk.ref_table not in by_name or fk.ref_table == t.name:
                continue  # dışarıdaki tablo ya da öz-referans (bilerek atlanır, ilk sürüm)
            if not fk.columns or not fk.ref_columns:
                continue
            relationships.append({
                "name": f"{t.name}_{fk.ref_table}",
                "join_type": "MANY_TO_ONE",
                "models": [t.name, fk.ref_table],
                "condition": f"{t.name}.{fk.columns[0]} = {fk.ref_table}.{fk.ref_columns[0]}",
            })
    return {"cubes": cubes, "relationships": relationships}
