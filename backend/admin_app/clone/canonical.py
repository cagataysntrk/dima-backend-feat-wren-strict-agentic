"""Canonical tip katmanı — clone'u datasource-BAĞIMSIZ yapan köprü.

Her KAYNAK adaptörü native tipini canonical'e indirger; her HEDEF adaptörü canonical'i
kendi DDL'ine çevirir. Böylece postgres→mssql, mysql→mssql, mssql→mssql… hepsi aynı
motordan geçer (WrenAI'nin desteklediği genişlik; yeni datasource = tek adaptör).

Canonical etiketler kasıtlı sade (raporlama verisi için yeterli):
  int16/int32/int64, bool, float32/float64, decimal, string, date, datetime,
  datetime_tz, time, uuid, binary. Eşlenemeyen native tip → None (kolon atlanır).
"""

from __future__ import annotations

# --- MSSQL hedef: canonical → T-SQL DDL ---
CANON_TO_MSSQL = {
    "int16": "smallint", "int32": "int", "int64": "bigint", "bool": "bit",
    "float32": "real", "float64": "float", "decimal": "decimal(38,10)",
    # NVARCHAR şart: kaynak VARCHAR(Latin1) CP1254 (Türkçe) mojibake taşıyabiliyor;
    # _fix_tr Unicode İ/Ş/Ğ üretir, VARCHAR bunları kaybederdi.
    "string": "nvarchar(max)", "date": "date", "datetime": "datetime2",
    "datetime_tz": "datetimeoffset", "time": "time", "uuid": "uniqueidentifier",
    "binary": "varbinary(max)",
}

# --- MSSQL kaynak: native tip → canonical (TYPE_NAME(system_type_id) küçük harf) ---
MSSQL_TO_CANON = {
    "tinyint": "int16", "smallint": "int16", "int": "int32", "bigint": "int64",
    "bit": "bool", "real": "float32", "float": "float64",
    "decimal": "decimal", "numeric": "decimal", "money": "decimal", "smallmoney": "decimal",
    "nvarchar": "string", "varchar": "string", "char": "string", "nchar": "string",
    "text": "string", "ntext": "string", "uniqueidentifier": "uuid",
    "datetime": "datetime", "datetime2": "datetime", "smalldatetime": "datetime",
    "date": "date", "time": "time",
    # datetimeoffset: pyodbc okuması özel converter ister (tip -155) → şimdilik atla.
    # binary/varbinary/image/xml/geography/hierarchyid/sql_variant → atla (nadir, raporda yok).
}


def mssql_native_to_canon(native: str) -> str | None:
    return MSSQL_TO_CANON.get((native or "").lower())


def canon_to_mssql_ddl(canon: str) -> str:
    return CANON_TO_MSSQL.get(canon, "nvarchar(max)")


def sqlalchemy_type_to_canon(sa_type) -> str | None:
    """SQLAlchemy reflected tip → canonical (JENERİK — postgres/mysql/oracle/… hepsi).

    isinstance sırası önemli: BigInteger/SmallInteger Integer'dan ÖNCE; Boolean Integer'dan
    önce (bazı dialect'lerde alt-sınıf değil ama garanti)."""
    from sqlalchemy import types as t

    if isinstance(sa_type, t.Boolean):
        return "bool"
    if isinstance(sa_type, t.SmallInteger):
        return "int16"
    if isinstance(sa_type, t.BigInteger):
        return "int64"
    if isinstance(sa_type, t.Integer):
        return "int32"
    if isinstance(sa_type, t.Numeric) and not isinstance(sa_type, t.Float):
        return "decimal"
    if isinstance(sa_type, t.Float):
        return "float64"
    if isinstance(sa_type, t.LargeBinary):
        return "binary"
    if isinstance(sa_type, t.Uuid):
        return "uuid"
    if isinstance(sa_type, t.Date):
        return "date"
    if isinstance(sa_type, t.Time):
        return "time"
    if isinstance(sa_type, t.DateTime):
        return "datetime_tz" if getattr(sa_type, "timezone", False) else "datetime"
    if isinstance(sa_type, (t.String, t.Text, t.Unicode, t.Enum)):
        return "string"
    # JSON/ARRAY/INET vb. → string'e serialize (raporlama için yeterli, veri kaybı yok).
    return "string"
