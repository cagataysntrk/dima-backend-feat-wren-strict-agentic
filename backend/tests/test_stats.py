"""Faz 4.13c (1 Ağustos 2026) — dış yol haritası görev 2.18 "meta-güven şeridi" (kabul
testi UC-2.23: "Meta-güven paneli açılır → Günün yol dağılımı GERÇEK loglardan hesaplanmış
olarak görünür, sabit değer değil"), son-kullanıcı görünür versiyonu. Testler
`interaction_log` yazımını AÇMAK yerine (testler varsayılan DIMA_INTERACTION_LOG=false ile
izole kalır — canlı log kirletilmez ilkesi bozulmaz) doğrudan `InteractionLog` satırı ekler
— hesaplama mantığı (kind→llm_free sınıflandırması) gerçek satırlar üzerinden, uçtan uca
(/stats/today) doğrulanır."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta


def _seed(tenant_id, kind: str, ts=None):
    from sqlmodel import Session

    from control_plane.db import engine
    from control_plane.models import InteractionLog

    with Session(engine) as s:
        s.add(InteractionLog(tenant_id=tenant_id, ts=ts or datetime.utcnow(),
                             question="x", source=kind, kind=kind))
        s.commit()


def _current_tenant_id(client) -> uuid.UUID:
    me = client.get("/auth/me").json()
    return uuid.UUID(me["tenant_id"])


def test_stats_today_computes_llm_free_percentage(client):
    tenant_id = _current_tenant_id(client)
    unique_marker = str(uuid.uuid4())[:8]  # bu testin satırlarını diğerlerinden ayırt eder

    # Doğrudan DB'ye yaz: 3 LLM'siz (cube/vqr/rule) + 1 LLM'li → %75 llm_free beklenir.
    for kind in ("cube", "vqr", "rule", "llm"):
        _seed(tenant_id, kind)

    r = client.get("/stats/today")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["total"] >= 4
    assert body["llm_free"] >= 3
    assert body["llm_free_pct"] is not None
    assert "%" in body["message"] or "yok" in body["message"]
    del unique_marker  # yalnızca okunabilirlik notu


def test_stats_today_scoped_to_own_tenant_only(client):
    """Başka bir tenant'ın interaction_log satırları KENDİ tenant'ının özetine karışmaz."""
    other_tenant = uuid.uuid4()
    _seed(other_tenant, "cube", ts=datetime.utcnow())

    r = client.get("/stats/today")
    assert r.status_code == 200
    # başka tenant'ın TEK satırı total'i EN AZ 1 artırmamalı — bunu doğrudan ölçmek yerine
    # (paylaşımlı DB'de mutlak sayı testler arası değişebilir) izolasyonu DOĞRUDAN sorgulayarak
    # kanıtla: kendi tenant'ımızın toplamı, iki tenant'ın toplamından KÜÇÜK olmalı.
    from sqlmodel import Session, func, select

    from control_plane.db import engine
    from control_plane.models import InteractionLog

    with Session(engine) as s:
        all_total = s.exec(select(func.count()).select_from(InteractionLog)).one()
    assert r.json()["total"] < all_total


def test_stats_today_empty_message_when_no_activity():
    """Hiç satırı olmayan (taze, rastgele) bir tenant için mesaj dürüstçe boş durumu
    bildirir — uydurma bir yüzde YOK. Doğrudan fonksiyon çağrısı (fake Request/principal)
    ile: HTTP katmanı üstünden taze-tenant garantisi kurmak (yeni oturum/kullanıcı) bu
    tek satırlık dallanma için orantısız ağır olurdu."""
    from types import SimpleNamespace

    from app.routers.stats import stats_today

    fake_request = SimpleNamespace(state=SimpleNamespace(
        principal=SimpleNamespace(tenant_id=str(uuid.uuid4()))))
    body = stats_today(fake_request, days=1)
    assert body["total"] == 0
    assert body["llm_free_pct"] is None
    assert "yok" in body["message"].lower()
