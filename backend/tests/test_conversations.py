"""/conversations — resume (kayıtlı AskResponse payload'ları) + viz taze-hesaplama.

Faz 2d+3 (viz.py↔chart.ts birleştirme, 31 Temmuz 2026): `result` (sayılar) resume'de HİÇ
dokunulmaz (ADR ilkesi) ama `viz` (sunum kararı) her resume'de TAZE hesaplanır — donuk/eski
bir `viz`, frontend'i kendi (daha az yetenekli) yerel `chart.ts::analyze()` yedeğine düşürürdü."""

from __future__ import annotations

import json


def _last_conversation_id(client, session_id: str) -> str:
    rows = client.get("/conversations").json()
    hit = next(r for r in rows if r["session_id"] == session_id)
    return hit["id"]


def test_conversation_resume_lists_messages(client):
    sid = "conv-test-resume-1"
    r = client.post("/ask", json={"question": "müşteri bazında ciro bu yıl",
                                  "execute": True, "session_id": sid})
    assert r.status_code == 200, r.text
    cid = _last_conversation_id(client, sid)
    detail = client.get(f"/conversations/{cid}").json()
    assert detail["session_id"] == sid
    assert len(detail["messages"]) >= 1
    msg = detail["messages"][-1]
    assert msg["result"] is not None
    assert msg["viz"] is not None  # taze hesaplandı, boş kalmadı


def test_conversation_resume_recomputes_stale_viz(client):
    """Kayıtlı `viz`'i BİLEREK bayat/yanlış bir değere değiştir, resume'in onu TAZE
    hesapla(y)arak ezdiğini doğrula (result'a dokunmadan)."""
    from sqlmodel import Session, select

    from control_plane.db import engine
    from control_plane.models import Conversation, ConversationMessage

    sid = "conv-test-resume-stale-viz"
    r = client.post("/ask", json={"question": "müşteri bazında ciro bu yıl",
                                  "execute": True, "session_id": sid})
    assert r.status_code == 200, r.text
    cid = _last_conversation_id(client, sid)

    with Session(engine) as s:
        conv = s.get(Conversation, __import__("uuid").UUID(cid))
        msg = s.exec(select(ConversationMessage)
                    .where(ConversationMessage.conversation_id == conv.id)
                    .order_by(ConversationMessage.seq)).all()[-1]
        payload = json.loads(msg.payload_json)
        original_result = payload["result"]
        # Bilerek bozuk/bayat bir viz enjekte et — gerçek recommend() ASLA bu şekli üretmez.
        payload["viz"] = {"kind": "__stale_marker__", "measures": [], "dims": []}
        msg.payload_json = json.dumps(payload, ensure_ascii=False)
        s.add(msg)
        s.commit()

    detail = client.get(f"/conversations/{cid}").json()
    resumed = detail["messages"][-1]
    assert resumed["viz"]["kind"] != "__stale_marker__", (
        "resume kayıtlı bayat viz'i döndürdü — taze hesaplama çalışmadı")
    assert resumed["result"] == original_result  # sayılar dokunulmadı (ADR ilkesi)
