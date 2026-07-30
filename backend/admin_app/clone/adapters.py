"""Clone kaynak/hedef ADAPTÖRLERİ — datasource-bağımsız clone'un kalbi.

SourceAdapter: kaynaktan tablo/kolon/PK keşfi + satır okuma + watermark.
TargetAdapter: hedefte DB/tablo oluşturma + toplu insert + PK upsert.

İki somut aile:
  - Mssql* (native pyodbc): bulk hız + Türkçe mojibake onarımı (_fix_tr) + collation.
  - SqlAlchemy* (JENERİK): SQLAlchemy dialect'i olan HER DB (postgres/mysql/oracle/
    clickhouse…) driver kurulunca otomatik — Inspector ile evrensel introspection.

registry.source_for / target_for datasource'a göre doğru adaptörü kurar (mssql→native,
diğerleri→sqlalchemy). Böylece yeni bir ERP/DB tipi eklemek = ya driver kur (sqlalchemy
otomatik) ya da bir native adaptör yaz.
"""

from __future__ import annotations

from collections.abc import Iterator

from admin_app.clone import canonical

BATCH = 1000
Row = tuple
Col = tuple[str, str]  # (ad, canonical-tip)


class SelfCloneError(RuntimeError):
    """Kaynak ve hedef aynı DB — self-clone reddedildi."""


# ============================ MSSQL (native pyodbc) ============================

class MssqlSource:
    """Kaynak: canlı/upstream SQL Server (pyodbc). Mevcut, test edilmiş SQL — birebir."""

    datasource = "mssql"

    def __init__(self, conn, fix=None):
        self.conn = conn
        self._fix = fix or (lambda v: v)

    def list_tables(self) -> list[str]:
        cur = self.conn.cursor()
        cur.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES "
                    "WHERE TABLE_TYPE='BASE TABLE' ORDER BY TABLE_NAME")
        return [r[0] for r in cur.fetchall()]

    def columns(self, table: str) -> list[Col]:
        cur = self.conn.cursor()
        cur.execute("SELECT c.name, TYPE_NAME(c.system_type_id) FROM sys.columns c "
                    f"WHERE c.object_id=OBJECT_ID('{table}') ORDER BY c.column_id")
        out = [(n, canonical.mssql_native_to_canon(b)) for n, b in cur.fetchall()]
        return [(n, c) for n, c in out if c]  # eşlenemeyen (binary/xml…) atlanır

    def primary_key(self, table: str) -> list[str]:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT c.name FROM sys.indexes i "
            "JOIN sys.index_columns ic ON ic.object_id=i.object_id AND ic.index_id=i.index_id "
            "JOIN sys.columns c ON c.object_id=ic.object_id AND c.column_id=ic.column_id "
            "WHERE i.object_id=OBJECT_ID(?) AND i.is_primary_key=1 ORDER BY ic.key_ordinal",
            table)
        return [r[0] for r in cur.fetchall()]

    def discover_watermark(self, table: str) -> tuple[str, str] | None:
        from admin_app.clone.discovery import discover_watermark, mssql_columns
        return discover_watermark(mssql_columns(self.conn.cursor(), table))

    def server_identity(self) -> tuple[str, str, str]:
        cur = self.conn.cursor()
        cur.execute("SELECT CONVERT(nvarchar(256), SERVERPROPERTY('ServerName')), DB_NAME()")
        r = cur.fetchone()
        return ("mssql", str(r[0] or "").lower(), str(r[1] or "").lower())

    def read_all(self, table: str, colnames: list[str]) -> Iterator[list[Row]]:
        cur = self.conn.cursor()
        cl = ", ".join(f"[{n}]" for n in colnames)
        cur.execute(f"SELECT {cl} FROM [{table}]")
        yield from _batches(cur)

    def read_since(self, table: str, colnames: list[str], wm: str, val) -> Iterator[list[Row]]:
        cur = self.conn.cursor()
        cl = ", ".join(f"[{n}]" for n in colnames)
        cur.execute(f"SELECT {cl} FROM [{table}] WHERE [{wm}] > ? ORDER BY [{wm}]", val)
        yield from _batches(cur)

    def max_watermark(self, table: str, wm: str):
        cur = self.conn.cursor()
        cur.execute(f"SELECT MAX([{wm}]) FROM [{table}]")
        return cur.fetchone()[0]

    def fix(self, value):
        return self._fix(value)

    def rollback(self):
        try:
            self.conn.rollback()
        except Exception:  # noqa: S110, BLE001 - best-effort
            pass

    def close(self):
        try:
            self.conn.close()
        except Exception:  # noqa: S110, BLE001
            pass


class MssqlTarget:
    """Hedef: lab/mirror SQL Server (autocommit pyodbc)."""

    datasource = "mssql"

    def __init__(self, conn):
        self.conn = conn

    def server_identity(self) -> tuple[str, str, str]:
        cur = self.conn.cursor()
        cur.execute("SELECT CONVERT(nvarchar(256), SERVERPROPERTY('ServerName')), DB_NAME()")
        r = cur.fetchone()
        return ("mssql", str(r[0] or "").lower(), str(r[1] or "").lower())

    def ensure_db(self, db: str):
        self.conn.execute(f"IF DB_ID('{db}') IS NULL CREATE DATABASE [{db}]")

    def table_exists(self, db: str, table: str) -> bool:
        cur = self.conn.cursor()
        cur.execute(f"SELECT OBJECT_ID('[{db}].dbo.[{table}]')")
        return cur.fetchone()[0] is not None

    def create_table(self, db: str, table: str, cols: list[Col]):
        ddl = ", ".join(f"[{n}] {canonical.canon_to_mssql_ddl(c)} NULL" for n, c in cols)
        self.conn.cursor().execute(
            f"USE [{db}]; IF OBJECT_ID('{table}','U') IS NOT NULL DROP TABLE [{table}]; "
            f"CREATE TABLE [{table}] ({ddl})")

    def insert(self, db: str, table: str, colnames: list[str], batch: list[Row]):
        cur = self.conn.cursor()
        cl = ", ".join(f"[{n}]" for n in colnames)
        ph = ", ".join("?" for _ in colnames)
        cur.fast_executemany = False  # Decimal hassasiyeti fast_executemany'de bozuluyor
        cur.executemany(f"INSERT INTO [{db}].dbo.[{table}] ({cl}) VALUES ({ph})", batch)

    def delete_pk(self, db: str, table: str, pk: list[str], values: list):
        cond = " AND ".join(f"[{k}] = ?" for k in pk)
        self.conn.cursor().execute(f"USE [{db}]; DELETE FROM [{table}] WHERE {cond}", *values)

    def rollback(self):
        try:
            self.conn.rollback()
        except Exception:  # noqa: S110, BLE001
            pass

    def close(self):
        try:
            self.conn.close()
        except Exception:  # noqa: S110, BLE001
            pass


# ===================== JENERİK (SQLAlchemy, her dialect) =====================

class SqlAlchemySource:
    """Kaynak: SQLAlchemy dialect'i olan HER DB (postgres/mysql/oracle/clickhouse…).

    Introspection Inspector ile evrensel; okuma dialect'in identifier-preparer'ıyla
    doğru tırnaklanır. Türkçe mojibake YOK (bu DB'ler UTF-8) → fix identity."""

    def __init__(self, engine, datasource: str, host: str, database: str):
        self.engine = engine
        self.datasource = datasource
        self._host = (host or "").lower()
        self._database = (database or "").lower()
        self.conn = engine.connect()
        self._insp = None

    @property
    def insp(self):
        if self._insp is None:
            from sqlalchemy import inspect
            self._insp = inspect(self.engine)
        return self._insp

    def _q(self, ident: str) -> str:
        return self.engine.dialect.identifier_preparer.quote(ident)

    def list_tables(self) -> list[str]:
        return sorted(self.insp.get_table_names())

    def columns(self, table: str) -> list[Col]:
        out = [(c["name"], canonical.sqlalchemy_type_to_canon(c["type"]))
               for c in self.insp.get_columns(table)]
        return [(n, c) for n, c in out if c]

    def primary_key(self, table: str) -> list[str]:
        return list(self.insp.get_pk_constraint(table).get("constrained_columns") or [])

    def discover_watermark(self, table: str) -> tuple[str, str] | None:
        from admin_app.clone.discovery import discover_watermark
        cols = [(c["name"], type(c["type"]).__name__) for c in self.insp.get_columns(table)]
        return discover_watermark(cols)

    def server_identity(self) -> tuple[str, str, str]:
        return (self.datasource, self._host, self._database)

    def read_all(self, table: str, colnames: list[str]) -> Iterator[list[Row]]:
        cl = ", ".join(self._q(n) for n in colnames)
        res = self.conn.exec_driver_sql(f"SELECT {cl} FROM {self._q(table)}")
        yield from _sa_batches(res)

    def read_since(self, table: str, colnames: list[str], wm: str, val) -> Iterator[list[Row]]:
        from sqlalchemy import text
        cl = ", ".join(self._q(n) for n in colnames)
        res = self.conn.execute(
            text(f"SELECT {cl} FROM {self._q(table)} WHERE {self._q(wm)} > :v "
                 f"ORDER BY {self._q(wm)}"), {"v": val})
        yield from _sa_batches(res)

    def max_watermark(self, table: str, wm: str):
        res = self.conn.exec_driver_sql(f"SELECT MAX({self._q(wm)}) FROM {self._q(table)}")
        return res.fetchone()[0]

    def fix(self, value):
        return value

    def rollback(self):
        try:
            self.conn.rollback()
        except Exception:  # noqa: S110, BLE001
            pass

    def close(self):
        try:
            self.conn.close()
            self.engine.dispose()
        except Exception:  # noqa: S110, BLE001
            pass


def _batches(cur) -> Iterator[list[Row]]:
    while True:
        b = cur.fetchmany(BATCH)
        if not b:
            break
        yield [tuple(r) for r in b]


def _sa_batches(res) -> Iterator[list[Row]]:
    while True:
        b = res.fetchmany(BATCH)
        if not b:
            break
        yield [tuple(r) for r in b]


# ============================ registry ============================

_SA_DRIVER = {  # datasource → SQLAlchemy sürücü öneki (driver kuruluysa çalışır)
    "postgres": "postgresql+psycopg", "postgresql": "postgresql+psycopg",
    "mysql": "mysql+pymysql", "mariadb": "mysql+pymysql",
    "oracle": "oracle+oracledb", "clickhouse": "clickhouse+native",
}


def _sa_url(datasource: str, meta: dict, password: str | None) -> str:
    from urllib.parse import quote_plus
    drv = _SA_DRIVER.get(datasource.lower())
    if not drv:
        raise SelfCloneError(f"Desteklenmeyen datasource (SQLAlchemy sürücüsü yok): {datasource}")
    user = quote_plus(str(meta.get("user") or ""))
    pw = quote_plus(str(password or ""))
    host = meta.get("host") or "localhost"
    port = meta.get("port") or ""
    db = meta.get("database") or ""
    auth = f"{user}:{pw}@" if user else ""
    hostport = f"{host}:{port}" if port else str(host)
    return f"{drv}://{auth}{hostport}/{db}"


def source_for(datasource: str, meta: dict, password: str | None, pyodbc_conn=None, fix=None):
    """Kaynak adaptörü kur. mssql → native (verilen pyodbc_conn); diğerleri → SQLAlchemy."""
    ds = datasource.lower()
    if ds in ("mssql", "sqlserver"):
        if pyodbc_conn is None:
            raise SelfCloneError("mssql kaynağı için pyodbc bağlantısı gerekli")
        return MssqlSource(pyodbc_conn, fix)
    from sqlalchemy import create_engine
    eng = create_engine(_sa_url(ds, meta, password), pool_pre_ping=True)
    return SqlAlchemySource(eng, ds, str(meta.get("host") or ""), str(meta.get("database") or ""))


def target_for(datasource: str, pyodbc_conn):
    """Hedef adaptörü. Şimdilik mirror = mssql lab (autocommit pyodbc). SqlAlchemyTarget
    ileride eklenebilir (postgres/duckdb ayna); şu an mirror datasource'unu biz kontrol
    ediyoruz (mssql)."""
    return MssqlTarget(pyodbc_conn)
