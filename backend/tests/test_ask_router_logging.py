"""1 Ağustos 2026 — /ask ve /cube uçlarının HER isteği/cevabı `dima.ask` logger'ına
INFO seviyesinde düşürdüğünü kanıtlar (kullanıcı talebi: "her soru cevapta net şekilde
loglayalım"). `_finish()` TEK choke-point olduğundan bu iki log satırı tüm başarılı
`/ask` yollarını (meta/VQR/yapısal/Discovery) kapsar — burada temsili bir soru yeterli."""

from __future__ import annotations

import logging

from tests.conftest import ask


def test_ask_logs_request_and_response(client, caplog):
    with caplog.at_level(logging.INFO, logger="dima.ask"):
        ask(client, "neler sorabilirim")
    messages = [r.message for r in caplog.records]
    assert any(m.startswith("İSTEK /ask:") for m in messages)
    assert any(m.startswith("CEVAP /ask:") for m in messages)


def test_cube_logs_request_and_response(client, caplog):
    cq = {"cube": "parti", "measures": ["toplam_ciro"]}
    with caplog.at_level(logging.INFO, logger="dima.ask"):
        r = client.post("/cube", json={"session_id": "eval", "cube_query": cq,
                                       "label": "test chip"})
    assert r.status_code == 200, r.text
    messages = [rec.message for rec in caplog.records]
    assert any(m.startswith("İSTEK /cube:") for m in messages)
    assert any(m.startswith("CEVAP /cube:") for m in messages)
