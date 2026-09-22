#!/usr/bin/env python3
"""Seed the deterministic P6 shared PostgreSQL fixture.

This is lab-only setup. It creates no product routing and owns no semantic resolution.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import psycopg


HERE = Path(__file__).resolve().parent
FIXTURE = json.loads((HERE / "fixture.json").read_text(encoding="utf-8"))


def connection_kwargs() -> dict[str, object]:
    return {
        "host": "127.0.0.1",
        "port": int(os.getenv("P6_ANALYTICS_DB_PORT", "55432")),
        "dbname": os.getenv("ANALYTICS_DB_NAME", "dima_analytics"),
        "user": os.getenv("ANALYTICS_DB_USER", "dima_analytics"),
        "password": os.getenv("ANALYTICS_DB_PASSWORD", "dima-analytics-lab"),
    }


def main() -> None:
    with psycopg.connect(**connection_kwargs()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS p6_customers (
                    id      integer PRIMARY KEY,
                    name    text NOT NULL,
                    segment text NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS p6_orders (
                    id          integer PRIMARY KEY,
                    customer_id integer NOT NULL REFERENCES p6_customers(id),
                    order_date  date NOT NULL,
                    region      text NOT NULL,
                    channel     text NOT NULL,
                    amount      integer NOT NULL
                )
                """
            )
            cur.execute("TRUNCATE p6_orders, p6_customers")
            cur.executemany(
                "INSERT INTO p6_customers (id, name, segment) VALUES (%s, %s, %s)",
                [
                    (row["id"], row["name"], row["segment"])
                    for row in FIXTURE["customers"]
                ],
            )
            cur.executemany(
                """
                INSERT INTO p6_orders
                    (id, customer_id, order_date, region, channel, amount)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                [
                    (
                        row["id"],
                        row["customer_id"],
                        row["order_date"],
                        row["region"],
                        row["channel"],
                        row["amount"],
                    )
                    for row in FIXTURE["orders"]
                ],
            )
        conn.commit()

    print(
        json.dumps(
            {
                "seed": "ok",
                "fixture_version": FIXTURE["fixture_version"],
                "customers": len(FIXTURE["customers"]),
                "orders": len(FIXTURE["orders"]),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
