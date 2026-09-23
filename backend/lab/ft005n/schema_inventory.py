"""FT-005N read-only Boyahane schema inventory.

Metadata only. No model calls, no Metabase calls, no benchmark outcomes.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import duckdb


def main(source: Path, out: Path) -> None:
    con = duckdb.connect(str(source), read_only=True)
    tables = [
        row[0]
        for row in con.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema='main' AND table_type='BASE TABLE'
            ORDER BY table_name
            """
        ).fetchall()
    ]
    payload = {
        "source": source.name,
        "table_count": len(tables),
        "tables": [],
    }
    for table in tables:
        columns = con.execute(
            """
            SELECT column_name, data_type, is_nullable, ordinal_position
            FROM information_schema.columns
            WHERE table_schema='main' AND table_name=?
            ORDER BY ordinal_position
            """,
            [table],
        ).fetchall()
        count = con.execute(
            f'SELECT count(*) FROM main."{table.replace(chr(34), chr(34)*2)}"'
        ).fetchone()[0]
        column_payload = [
            {
                "name": name,
                "type": data_type,
                "nullable": nullable == "YES",
                "ordinal": int(ordinal),
            }
            for name, data_type, nullable, ordinal in columns
        ]
        date_ranges = {}
        for name, data_type, _nullable, _ordinal in columns:
            if data_type == "DATE":
                quoted_table = '"' + table.replace('"', '""') + '"'
                quoted_column = '"' + name.replace('"', '""') + '"'
                minimum, maximum = con.execute(
                    f"SELECT min({quoted_column}), max({quoted_column}) "
                    f"FROM main.{quoted_table}"
                ).fetchone()
                date_ranges[name] = {
                    "min": minimum.isoformat() if minimum is not None else None,
                    "max": maximum.isoformat() if maximum is not None else None,
                }

        payload["tables"].append(
            {
                "name": table,
                "row_count": int(count),
                "columns": column_payload,
                "date_ranges": date_ranges,
            }
        )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    main(args.source, args.out)
