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
        payload["tables"].append(
            {
                "name": table,
                "row_count": int(count),
                "columns": [
                    {
                        "name": name,
                        "type": data_type,
                        "nullable": nullable == "YES",
                        "ordinal": int(ordinal),
                    }
                    for name, data_type, nullable, ordinal in columns
                ],
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
