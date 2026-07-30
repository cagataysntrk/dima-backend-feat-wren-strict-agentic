"""Introspection→model üretici (ADR-0017 Karar 5'in ilk sürümü).

Kaynak pack'inin gereksinim.yml'inde listelenen tabloları lab SQL Server'ından
introspect eder ve model YAML'larını (packs/kaynak/<pack>/models/) üretir.
Cube'lar ve sinonimler ELLE kalır — üretici yalnız fiziksel katmanı türetir.

Kullanım:
    .venv/bin/python lab/generate_models.py demo/packs/kaynak/mikro-v16 ATIKSAN_MIKRO
    # Logo gibi önekli şemalarda firma/dönem kapsamı + şirket katmanına üretim:
    .venv/bin/python lab/generate_models.py demo/packs/kaynak/logo-3 GULTEKS_2021 \
        --firma 121 --donem 1 --out demo/companies/gulteks/models
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import yaml

# SQL Server tipi → MDL tipi (wren build'in beklediği sözlük)
TYPE_MAP = {
    "int": "INTEGER",
    "smallint": "INTEGER",
    "tinyint": "INTEGER",
    "bigint": "BIGINT",
    "bit": "BOOLEAN",
    "float": "DOUBLE",
    "real": "DOUBLE",
    "decimal": "DOUBLE",
    "numeric": "DOUBLE",
    "money": "DOUBLE",
    "nvarchar": "VARCHAR",
    "varchar": "VARCHAR",
    "nchar": "VARCHAR",
    "char": "VARCHAR",
    "ntext": "VARCHAR",
    "text": "VARCHAR",
    "uniqueidentifier": "VARCHAR",
    "datetime": "TIMESTAMP",
    "datetime2": "TIMESTAMP",
    "smalldatetime": "TIMESTAMP",
    "date": "DATE",
}


def sqlcmd(db: str, query: str) -> list[list[str]]:
    out = subprocess.run(
        [
            "docker", "exec", "dima-lab-mssql",
            "/opt/mssql-tools18/bin/sqlcmd", "-C", "-S", "localhost",
            "-U", "sa", "-P", "DimaLab!2026", "-d", db,
            "-W", "-s", "|", "-h", "-1", "-Q", f"SET NOCOUNT ON; {query}",
        ],
        capture_output=True, text=True, check=True,
    ).stdout
    return [line.split("|") for line in out.splitlines() if line.strip()]


def introspect(db: str, table: str) -> list[tuple[str, str, bool]]:
    """(kolon, mdl_tipi, not_null) listesi — fiziksel sıra korunur."""
    # system_type_id ile TEMEL tip çözülür — Netsis gibi kullanıcı-tanımlı tip
    # (TDBCARIKOD=varchar alias'ı vb.) kullanan şemalarda user_type_id yanıltır.
    rows = sqlcmd(db, (
        "SELECT c.name, TYPE_NAME(c.system_type_id), c.is_nullable FROM sys.columns c "
        f"WHERE c.object_id = OBJECT_ID('{table}') ORDER BY c.column_id"
    ))
    if not rows:
        raise SystemExit(f"Tablo bulunamadı: {table}")
    result = []
    for name, sql_type, nullable in rows:
        mdl = TYPE_MAP.get(sql_type.lower())
        if mdl is None:
            continue  # image/varbinary vs. — raporlamada anlamsız, atla
        result.append((name, mdl, nullable == "0"))
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pack_dir", type=Path)
    ap.add_argument("db")
    ap.add_argument("--firma", type=int, help="Logo firma no ({firma} → 3 haneli)")
    ap.add_argument("--donem", type=int, help="Logo dönem no ({donem} → 2 haneli)")
    ap.add_argument("--out", type=Path, help="models çıktı dizini (vars: <pack>/models)")
    args = ap.parse_args()
    pack_dir = args.pack_dir
    db = args.db
    models_dir = args.out if args.out else pack_dir / "models"
    spec = yaml.safe_load((pack_dir / "gereksinim.yml").read_text())

    for model in spec["modeller"]:
        table = model["tablo"]
        if "{firma}" in table or "{donem}" in table:
            if args.firma is None:
                raise SystemExit(f"{table}: şablonlu tablo için --firma (ve gerekiyorsa --donem) verin")
            table = table.replace("{firma}", f"{args.firma:03d}")
            if "{donem}" in table:
                if args.donem is None:
                    raise SystemExit(f"{model['tablo']}: --donem gerekli")
                table = table.replace("{donem}", f"{args.donem:02d}")
        wanted = model.get("kolonlar")  # None = anlamlı tüm kolonlar
        pk = model.get("primary_key")
        live = introspect(db, table)
        if wanted:
            missing = set(wanted) - {c for c, _, _ in live}
            if missing:
                raise SystemExit(f"{table}: gereksinimdeki kolonlar şemada yok: {sorted(missing)}")
            live = [(c, t, nn) for c, t, nn in live if c in wanted]

        columns = []
        for c, t, nn in live:
            col: dict = {"name": c, "type": t}
            if c == pk:
                col["is_primary_key"] = True
            if nn:
                col["not_null"] = True
            columns.append(col)

        # Calculated ad kolonları (ADR-0017 §5 adım 5): handle kolonunun type'ı
        # ilişkili MODELİN ADI olmalıdır (wren lineage kuralı); JOIN'i motor üretir.
        for extra in model.get("hesaplanan") or []:
            if "handle" in extra:
                columns.append({"name": extra["handle"], "type": extra["handle"],
                                "relationship": extra["relationship"]})
            else:
                columns.append({"name": extra["name"], "type": extra["type"],
                                "is_calculated": True,
                                "expression": extra["expression"]})

        doc = {
            "name": model["name"],
            "table_reference": {"schema": "dbo", "table": table},
            "columns": columns,
        }
        if pk:
            doc["primary_key"] = pk

        out = models_dir / model["name"] / "metadata.yml"
        out.parent.mkdir(parents=True, exist_ok=True)
        header = (
            f"# ÜRETİLMİŞTİR: lab/generate_models.py ← {db}.{table} (elle düzenleme,\n"
            "# yeniden üretimde ezilir; kolon seçimi gereksinim.yml'de yaşar.)\n"
        )
        out.write_text(header + yaml.dump(doc, allow_unicode=True, sort_keys=False))
        print(f"{out}: {len(columns)} kolon")


if __name__ == "__main__":
    main()
