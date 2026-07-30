"""Yüklenen Excel/CSV → oturum-scoped DuckDB + oto-MDL/cube (chat-scoped base modu, ADR-0017 K9').

Akış: dosya → DuckDB tablo (session .duckdb) → DESCRIBE ile şema → kolon rolleri (sayısal=ölçü,
tarih=zaman, diğer=boyut) → minimal MDL (model + cube) → WrenService. Böylece yüklenen veri
MEVCUT cube/NL pipeline'ından geçer (route + yorum + KPI bedava). EPHEMERAL: oturum dizininde
yaşar, kalıcılık yok (kullanıcı-scoped persist ayrı iş).

GÜVENLİK: read_csv/read_xlsx LLM SQL'ine GÖMÜLMEZ — burada sunucuda ingest edilip düzgün
file-datasource olur (strict_mode/injection dışı). Kolonlar SLUG'lanır → tırnak/enjeksiyon derdi yok;
orijinal ad synonym+label olarak korunur (NL eşleşmesi). Veri LAN'da kalır (KVKK)."""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any

# DuckDB tipi → (MDL tipi, rol). rol: measure | time | dimension.
_NUM = {"BIGINT", "INTEGER", "SMALLINT", "TINYINT", "HUGEINT", "UBIGINT", "UINTEGER",
        "DOUBLE", "FLOAT", "REAL", "DECIMAL"}
_TIME = {"DATE", "TIMESTAMP", "TIMESTAMP_S", "TIMESTAMP_MS", "TIMESTAMP_NS",
         "TIMESTAMP WITH TIME ZONE", "TIME", "DATETIME"}


def _base_type(duck: str) -> str:
    return re.sub(r"\(.*\)", "", (duck or "").upper()).strip()


def _role(duck: str) -> str:
    b = _base_type(duck)
    if b in _NUM:
        return "measure"
    if b in _TIME:
        return "time"
    return "dimension"


def _mdl_type(duck: str) -> str:
    b = _base_type(duck)
    if b in _TIME:
        return "TIMESTAMP" if "TIME" in b and b != "TIME" else ("DATE" if b == "DATE" else "TIMESTAMP")
    if b in _NUM:
        return "DOUBLE" if b in ("DOUBLE", "FLOAT", "REAL", "DECIMAL") else "BIGINT"
    return "VARCHAR"


_TR = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosucgiosu")


def _slug(name: str, taken: set[str]) -> str:
    """Kolon adı → güvenli tekil identifier (tırnak/enjeksiyon derdini kökten keser)."""
    s = unicodedata.normalize("NFKC", str(name)).translate(_TR).lower()
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_") or "kolon"
    if s[0].isdigit():
        s = "k_" + s
    base, i = s, 2
    while s in taken:
        s = f"{base}_{i}"; i += 1
    taken.add(s)
    return s


def _syns(orig: str, slug: str) -> list[str]:
    """NL eşleşmesi için synonym'ler — orijinal ad (Türkçe dahil) + slug varyantları."""
    o = str(orig).strip().lower()
    out = {o, slug, slug.replace("_", " ")}
    out.discard("")
    return sorted(out)


def _connect(session_dir: Path):
    import duckdb

    session_dir.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(session_dir / "data.duckdb"))


def ingest_file(raw: bytes, filename: str, session_dir: Path,
                table: str = "veri") -> dict[str, Any]:
    """Dosyayı oturum DuckDB'sine tablo olarak yükler; şema/kolon rollerini döner.

    Dönüş: {table, catalog, columns:[{orig, name(slug), type, role}], row_count}."""
    ext = Path(filename).suffix.lower()
    session_dir.mkdir(parents=True, exist_ok=True)
    src = session_dir / f"upload{ext or '.csv'}"
    src.write_bytes(raw)

    con = _connect(session_dir)
    try:
        con.execute(f"DROP TABLE IF EXISTS {table}")
        if ext in (".xlsx", ".xls"):
            con.execute("INSTALL excel"); con.execute("LOAD excel")
            reader = f"read_xlsx('{src}', all_varchar=false)"
        else:  # csv/txt/tsv → auto-algıla (ayraç/başlık/tip)
            reader = f"read_csv_auto('{src}', header=true, sample_size=-1)"
        raw_cols = [r[0] for r in con.execute(
            f"DESCRIBE SELECT * FROM {reader}").fetchall()]  # orijinal başlıklar
        taken: set[str] = set()
        cols = []
        select_parts = []
        for orig in raw_cols:
            slug = _slug(orig, taken)
            select_parts.append(f'"{orig}" AS "{slug}"')
            cols.append({"orig": str(orig), "name": slug})
        con.execute(f"CREATE TABLE {table} AS SELECT {', '.join(select_parts)} FROM {reader}")
        # slug'lı tablodan kesin tipler
        typemap = {r[0]: r[1] for r in con.execute(f"DESCRIBE {table}").fetchall()}
        for c in cols:
            duck = typemap.get(c["name"], "VARCHAR")
            c["type"] = _mdl_type(duck)
            c["role"] = _role(duck)
        n = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    finally:
        con.close()
    try:
        src.unlink()  # ham dosyayı bırakma (yalnız DuckDB tablosu kalsın)
    except OSError:
        pass
    return {"table": table, "catalog": "data", "columns": cols, "row_count": int(n)}


def build_mdl(info: dict[str, Any], cube_name: str = "veri",
              label: str = "yüklenen veri") -> dict[str, Any]:
    """Şema bilgisinden minimal MDL (model + tek cube). Sayısal→ölçü(SUM), tarih→zaman, diğer→boyut."""
    table, catalog, cols = info["table"], info["catalog"], info["columns"]
    model_cols = [{"name": c["name"], "type": c["type"]} for c in cols]
    measures, dimensions, time_dims = [], [], []
    for c in cols:
        if c["role"] == "measure":
            measures.append({"name": f"toplam_{c['name']}", "expression": f"SUM(\"{c['name']}\")",
                             "type": "DOUBLE", "additive": "full",
                             "synonyms": _syns(c["orig"], c["name"])})
        elif c["role"] == "time":
            time_dims.append({"name": c["name"], "expression": c["name"], "type": c["type"]})
        else:
            dimensions.append({"name": c["name"], "expression": c["name"], "type": c["type"],
                               "label": c["orig"], "synonyms": _syns(c["orig"], c["name"])})
    # Ölçü yoksa (hepsi metin) satır-sayımı ölçüsü ekle — cube boş kalmasın.
    if not measures:
        measures.append({"name": "kayit_sayisi", "expression": "COUNT(*)", "type": "DOUBLE",
                         "additive": "full", "synonyms": ["kayıt", "adet", "sayı", "satır"]})
    cube = {"name": cube_name, "label": label, "baseObject": table,
            "synonyms": [cube_name, "veri", "tablo", "dosya", "yükleme", "yukleme", label],
            "measures": measures, "dimensions": dimensions, "timeDimensions": time_dims}
    return {"catalog": "wren", "schema": "main", "dataSource": "duckdb", "layoutVersion": 3,
            "models": [{"name": table, "tableReference":
                        {"catalog": catalog, "schema": "main", "table": table},
                        "columns": model_cols}],
            "relationships": [], "views": [], "cubes": [cube]}


def build_service(session_dir: Path, mdl: dict[str, Any]):
    """MDL'i yazar ve oturum DuckDB'sine bağlı WrenService döner (mevcut pipeline'a takılır)."""
    from app.wren_service import WrenService

    target = session_dir / "target"
    target.mkdir(parents=True, exist_ok=True)
    (target / "mdl.json").write_text(json.dumps(mdl, ensure_ascii=False))
    return WrenService(session_dir, "duckdb", {"url": str(session_dir), "format": "duckdb"})
