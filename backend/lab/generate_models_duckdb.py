"""DuckDB introspection→model üretici (generate_models.py'nin duckdb kardeşi).

boyahane.duckdb'nin tüm tablolarını introspect eder ve WrenAI model YAML'larını
(demo/companies/demo-boyahane/models/<t>/metadata.yml) üretir. Cube'lar + sinonimler
ELLE kalır — üretici yalnız FİZİKSEL katmanı (table_reference + columns + PK) türetir.

Kullanım:
    .venv/bin/python lab/generate_models_duckdb.py
    .venv/bin/python lab/generate_models_duckdb.py --db demo/data/boyahane.duckdb \
        --catalog boyahane --out demo/companies/demo-boyahane/models
"""

from __future__ import annotations

import argparse
from pathlib import Path

import duckdb
import yaml

# DuckDB tipi → MDL tipi (wren build'in beklediği sözlük)
TYPE_MAP = {
    "TINYINT": "INTEGER", "SMALLINT": "INTEGER", "INTEGER": "INTEGER",
    "BIGINT": "BIGINT", "HUGEINT": "BIGINT",
    "BOOLEAN": "BOOLEAN",
    "FLOAT": "DOUBLE", "DOUBLE": "DOUBLE", "REAL": "DOUBLE",
    "DATE": "DATE", "TIMESTAMP": "TIMESTAMP", "TIMESTAMP_NS": "TIMESTAMP",
    "VARCHAR": "VARCHAR", "TEXT": "VARCHAR",
}

# Join-hedefi tablolar için birincil anahtar (WrenAI MANY_TO_ONE'ın "one" tarafı PK ister).
# Bileşik-anahtarlı aylık özet tabloları (makine_enerji_aylik=makine+ay vb.) join-hedefi
# DEĞİL → PK'sız kalır (aggregate cube base'i; sorun değil).
PK_MAP = {
    "makineler": "makine", "musteriler": "musteri_kodu", "tedarikciler": "tedarikci_kodu",
    "personel": "personel_kodu", "personel_ozluk": "personel_kodu",
    "ham_kartlari": "ham_kodu", "kimyasallar": "kimyasal_kodu",
    "stok_kartlari": "stok_kodu", "depolar": "depo_kodu", "hesap_plani": "hesap_kodu",
    "banka_hesaplari": "banka_kodu", "partiler": "parti_no", "faturalar": "fatura_no",
    "irsaliyeler": "irsaliye_no", "yevmiye_fisleri": "fis_no", "iplik_lotlari": "lot_no",
    "top_stok": "top_no", "teklifler": "teklif_no", "satinalma_siparisleri": "sas_no",
    "sertifikalar": "sertifika_kodu", "ariza_kayitlari": "ariza_no",
    "fiyat_listesi": "id",
}


def introspect(con, table: str) -> list[tuple[str, str]]:
    """(kolon, mdl_tipi) — fiziksel sıra korunur."""
    rows = con.execute(
        "SELECT column_name, data_type FROM information_schema.columns "
        "WHERE table_name = ? AND table_schema = 'main' ORDER BY ordinal_position",
        [table],
    ).fetchall()
    out = []
    for name, dtype in rows:
        base = dtype.split("(")[0].upper()  # DECIMAL(18,2) → DECIMAL
        mdl = TYPE_MAP.get(base, "VARCHAR")
        out.append((name, mdl))
    return out


def pk_for(table: str, cols: list[str]) -> str | None:
    if table in PK_MAP:
        return PK_MAP[table]
    if "id" in cols:
        return "id"
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="demo/data/boyahane.duckdb")
    ap.add_argument("--catalog", default="boyahane")
    ap.add_argument("--out", type=Path, default=Path("demo/companies/demo-boyahane/models"))
    ap.add_argument("--enrich", type=Path,
                    default=Path("demo/companies/demo-boyahane/models_enrich.yml"),
                    help="cross-model calculated/relationship kolonları (yeniden üretimde korunur)")
    args = ap.parse_args()

    enrich: dict = {}
    if args.enrich and args.enrich.exists():
        enrich = yaml.safe_load(args.enrich.read_text()) or {}

    con = duckdb.connect(args.db, read_only=True)
    tables = [r[0] for r in con.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'main' ORDER BY table_name").fetchall()]

    # Eski/bayat modelleri temizle (yeniden üretim = tam ayna): out altındaki tüm
    # model dizinlerini kaldır, sonra güncel tablolardan yeniden yaz.
    if args.out.is_dir():
        for d in args.out.iterdir():
            if d.is_dir() and (d / "metadata.yml").exists():
                (d / "metadata.yml").unlink()
                d.rmdir()

    for table in tables:
        live = introspect(con, table)
        colnames = [c for c, _ in live]
        pk = pk_for(table, colnames)
        columns = []
        for c, t in live:
            col: dict = {"name": c, "type": t}
            if c == pk:
                col["is_primary_key"] = True
                col["not_null"] = True
            columns.append(col)
        # Cross-model calculated/relationship kolonları (models_enrich.yml) — ADR-0017 §5:
        # `handle` → ilişki kolonu (type = hedef MODEL adı); diğerleri is_calculated ifade.
        for extra in enrich.get(table) or []:
            if "handle" in extra:
                # handle = hedef MODEL adı (type = ad; netsis konvansiyonu). JOIN'i motor üretir.
                columns.append({"name": extra["handle"], "type": extra["handle"],
                                "relationship": extra["relationship"]})
            else:
                columns.append({"name": extra["name"], "type": extra["type"],
                                "is_calculated": True, "expression": extra["expression"]})
        doc = {
            "name": table,
            "table_reference": {"catalog": args.catalog, "schema": "main", "table": table},
            "columns": columns,
        }
        if pk:
            doc["primary_key"] = pk
        out = args.out / table / "metadata.yml"
        out.parent.mkdir(parents=True, exist_ok=True)
        header = (
            f"# ÜRETİLMİŞTİR: lab/generate_models_duckdb.py ← {args.catalog}.{table}\n"
            "# (elle düzenleme yeniden üretimde ezilir; cube'lar/sinonimler packs'te yaşar.)\n"
        )
        out.write_text(header + yaml.dump(doc, allow_unicode=True, sort_keys=False))
        print(f"{out}: {len(columns)} kolon" + (f" (pk={pk})" if pk else ""))

    con.close()
    print(f"\n{len(tables)} model üretildi → {args.out}")


if __name__ == "__main__":
    main()
