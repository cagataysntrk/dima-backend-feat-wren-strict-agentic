"""Production checkpoint boundary for Dima Brain V2.

Checkpoint storage is orchestration progress only. It is isolated in its own
Postgres schema and uses strict LangGraph serialization.
"""
from __future__ import annotations

import re
from contextlib import contextmanager
from collections.abc import Iterator

from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from psycopg import connect, sql
from psycopg.rows import dict_row

DEFAULT_ORCHESTRATION_SCHEMA = "dima_brain_v2_orchestration"
_SCHEMA_RE = re.compile(r"^[a-z][a-z0-9_]{0,62}$")


def validate_orchestration_schema(value: str) -> str:
    schema = str(value or "").strip()
    if not _SCHEMA_RE.fullmatch(schema):
        raise ValueError("Brain V2 orchestration schema name is invalid")
    return schema


@contextmanager
def postgres_checkpoint_saver(
    conn_string: str,
    *,
    schema: str = DEFAULT_ORCHESTRATION_SCHEMA,
    setup: bool = False,
) -> Iterator[PostgresSaver]:
    """Yield a strict PostgresSaver isolated from canonical Dima truth tables."""

    if not str(conn_string or "").strip():
        raise ValueError("Brain V2 Postgres checkpoint connection is required")
    schema_name = validate_orchestration_schema(schema)
    serde = JsonPlusSerializer(allowed_msgpack_modules=None)

    with connect(
        conn_string,
        autocommit=True,
        prepare_threshold=0,
        row_factory=dict_row,
    ) as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(
                    sql.Identifier(schema_name)
                )
            )
            cur.execute(
                sql.SQL("SET search_path TO {}").format(
                    sql.Identifier(schema_name)
                )
            )

        saver = PostgresSaver(conn, serde=serde)
        if setup:
            saver.setup()
        yield saver
