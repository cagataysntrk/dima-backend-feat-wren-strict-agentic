#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import time
import uuid
from decimal import Decimal
from pathlib import Path

import httpx
import psycopg

BASE = os.getenv("DIMA_UI_URL", "http://127.0.0.1:3002").rstrip("/")
EMAIL = os.environ["DIMA_E2E_USER_EMAIL"]
PASSWORD = os.environ["DIMA_E2E_USER_PASSWORD"]
OUT = Path(os.environ["NATIVE_UI_E2E_RECEIPT"])

Q1 = "1-22 Haziran 2026 arasında satış siparişlerinin toplam tutarı ne kadar?"
Q2 = "Peki Mayıs 2026?"
Q3 = "Kanallara göre?"


def wait_ui() -> None:
    deadline = time.time() + 180
    while time.time() < deadline:
        try:
            r = httpx.get(BASE + "/login", timeout=5)
            if r.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(2)
    raise RuntimeError("Dima UI startup timeout")


def oracle():
    conn = psycopg.connect(
        host="127.0.0.1",
        port=55442,
        dbname="boyahane",
        user="boyahane_owner",
        password=os.environ["BOYAHANE_OWNER_PASSWORD"],
    )
    with conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT COALESCE(SUM(toplam_tutar), 0)
            FROM satis_siparisleri
            WHERE acilis_tarihi >= DATE '2026-06-01'
              AND acilis_tarihi < DATE '2026-06-23'
            """
        )
        q1 = Decimal(str(cur.fetchone()[0]))
        cur.execute(
            """
            SELECT COALESCE(SUM(toplam_tutar), 0)
            FROM satis_siparisleri
            WHERE acilis_tarihi >= DATE '2026-05-01'
              AND acilis_tarihi < DATE '2026-06-01'
            """
        )
        q2 = Decimal(str(cur.fetchone()[0]))
        cur.execute(
            """
            SELECT kanal, COALESCE(SUM(toplam_tutar), 0)
            FROM satis_siparisleri
            WHERE acilis_tarihi >= DATE '2026-05-01'
              AND acilis_tarihi < DATE '2026-06-01'
            GROUP BY kanal
            ORDER BY kanal
            """
        )
        q3 = {str(k): Decimal(str(v)) for k, v in cur.fetchall()}
    return q1, q2, q3


def sse_events(client: httpx.Client, payload: dict):
    events = []
    with client.stream("POST", BASE + "/api/chat", json=payload, timeout=180) as response:
        response.raise_for_status()
        buffer = ""
        for chunk in response.iter_text():
            buffer += chunk
            while "\n\n" in buffer:
                frame, buffer = buffer.split("\n\n", 1)
                data = "\n".join(
                    line[5:].strip()
                    for line in frame.splitlines()
                    if line.startswith("data:")
                )
                if data:
                    events.append(json.loads(data))
    return events


def scalar(result: dict) -> Decimal:
    rows = result.get("rows") or []
    if len(rows) != 1:
        raise AssertionError(f"expected scalar row, got {rows}")
    nums = [
        Decimal(str(v))
        for v in rows[0].values()
        if isinstance(v, (int, float)) and not isinstance(v, bool)
    ]
    if len(nums) != 1:
        raise AssertionError(f"expected one numeric scalar, got {rows[0]}")
    return nums[0]


def breakdown(result: dict) -> dict[str, Decimal]:
    out: dict[str, Decimal] = {}
    for row in result.get("rows") or []:
        texts = [str(v) for v in row.values() if isinstance(v, str)]
        nums = [
            Decimal(str(v))
            for v in row.values()
            if isinstance(v, (int, float)) and not isinstance(v, bool)
        ]
        if len(texts) == 1 and len(nums) == 1:
            out[texts[0]] = nums[0]
    return out


def close_enough(a: Decimal, b: Decimal) -> bool:
    return abs(a - b) <= Decimal("0.02")


def main() -> int:
    wait_ui()
    expected_q1, expected_q2, expected_q3 = oracle()
    receipt = {
        "status": "RED",
        "pages": {},
        "turns": [],
        "oracle": {
            "q1": str(expected_q1),
            "q2": str(expected_q2),
            "q3": {k: str(v) for k, v in expected_q3.items()},
        },
    }

    with httpx.Client(follow_redirects=True, timeout=60) as client:
        login = client.post(
            BASE + "/api/auth/sign-in/email",
            json={"email": EMAIL, "password": PASSWORD},
        )
        login.raise_for_status()
        if not client.cookies:
            raise AssertionError("login did not establish a session cookie")

        for path in ["/app", "/app/chat", "/app/data", "/app/schema", "/app/model", "/app/settings"]:
            r = client.get(BASE + path)
            receipt["pages"][path] = r.status_code
            if r.status_code != 200:
                raise AssertionError(f"{path} returned {r.status_code}")

        conversation_id = str(uuid.uuid4())
        context = None
        messages = []

        for index, question in enumerate((Q1, Q2, Q3), start=1):
            messages.append({"role": "user", "content": question})
            events = sse_events(
                client,
                {
                    "conversationId": conversation_id,
                    "engineContext": context,
                    "messages": messages,
                },
            )
            errors = [x for x in events if x.get("type") == "error"]
            done = [x for x in events if x.get("type") == "done"]
            if errors or len(done) != 1:
                raise AssertionError(f"turn {index} failed: errors={errors}, done={done}")
            final = done[0]
            if not final.get("engineContext"):
                raise AssertionError(f"turn {index} did not return native context")
            if not final.get("answer"):
                raise AssertionError(f"turn {index} returned no answer")
            if final.get("result") is None:
                raise AssertionError(f"turn {index} returned no executable result")

            if index == 1:
                observed = scalar(final["result"])
                if not close_enough(observed, expected_q1):
                    raise AssertionError(f"Q1 oracle mismatch: {observed} != {expected_q1}")
            elif index == 2:
                observed = scalar(final["result"])
                if not close_enough(observed, expected_q2):
                    raise AssertionError(f"Q2 oracle mismatch: {observed} != {expected_q2}")
            else:
                observed_map = breakdown(final["result"])
                if set(observed_map) != set(expected_q3):
                    raise AssertionError(f"Q3 categories mismatch: {observed_map} != {expected_q3}")
                for key, expected in expected_q3.items():
                    if not close_enough(observed_map[key], expected):
                        raise AssertionError(f"Q3 {key} mismatch: {observed_map[key]} != {expected}")

            steps = [x for x in events if x.get("type") == "step"]
            tokens = [x for x in events if x.get("type") == "token"]
            receipt["turns"].append({
                "turn": index,
                "question": question,
                "step_events": len(steps),
                "token_events": len(tokens),
                "answer": final["answer"],
                "row_count": final["result"].get("row_count"),
                "engine_context_present": True,
            })
            context = final["engineContext"]
            messages.append({"role": "assistant", "content": final["answer"]})

        stop_id = str(uuid.uuid4())
        with client.stream(
            "POST",
            BASE + "/api/chat",
            json={
                "conversationId": stop_id,
                "engineContext": None,
                "messages": [{"role": "user", "content": Q1}],
            },
            timeout=180,
        ) as response:
            response.raise_for_status()
            iterator = response.iter_bytes()
            first = next(iterator, b"")
            receipt["stop"] = {
                "first_bytes_received": bool(first),
                "caller_closed_stream_early": True,
            }

    receipt["status"] = "GREEN"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
