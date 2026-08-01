"""Faz 4.14 (1 Ağustos 2026) — PII maskeleme entegrasyonu (dış yol haritası görev 2.19,
kabul testi UC-2.22: "TCKN içeren bir liste sorgulanır → Ekranda, CSV'de ve PNG'de TCKN
maskeli görünür; yetkili rolde maskesiz ve erişim loglanır"). CSV/PNG dışa aktarımı ayrı bir
sunucu-taraflı filtre GEREKTİRMEZ — `dima-frontend-demo-master/src/lib/export.ts` yalnız
BU testlerin doğruladığı, zaten maskelenmiş/HTTP üzerinden gelen `AskResponse.result`
üzerinde çalışır (tek çıkış noktası ilkesi, bkz. app/pii.py modül docstring'i).

Kanıt: `personel_ozluk.tc_kimlik` gerçek şemada var (demo/data/boyahane.duckdb) ama HİÇBİR
cube onu SEÇMİYOR — `/query` (ham SQL, `sql:run`) ise HERHANGİ bir kolonu seçebilir, bu
yüzden gerçek sızıntı YÜZEYİ budur (Discovery/gerçek-LLM de aynı şekilde erişebilir).
Testler gerçek bir personel satırına DOKUNMADAN (literal SELECT) bu yüzeyi kanıtlar.

**Doğrulama turu düzeltmesi (1 Ağustos 2026)**: Faz 4.14 yalnız `/ask`/`/cube`/`/query`'yi
kapsıyordu — `/report`, `/dashboards/{id}/data` ve zamanlanmış rapor TESLİMİ (e-posta)
maskelemiyordu (bkz. `app/pii.py::mask_query_result` docstring'i). Aşağıdaki testler bu
ÜÇ yeni yüzeyi de aynı titizlikle kanıtlar — `WrenService.query`'yi monkeypatch'leyerek
(cube_query GERÇEK bir cube'a bağlı olmalı, ama ÇALIŞTIRMA sonucu kontrollü enjekte edilir)."""

from __future__ import annotations

from tests.conftest import make_tenant_user
from tests.test_auth import _login_as

_VALID_TCKN = "10000000146"
_CQ = {"cube": "parti", "measures": ["toplam_ciro"]}


def _inject_tckn_query(monkeypatch) -> None:
    """`WrenService.query`'yi, GERÇEK SQL'i yok sayıp sabit bir TCKN-taşıyan satır dönecek
    şekilde değiştirir — cube_query yine de gerçek bir cube'a karşı doğrulanır (`cube_sql`
    hâlâ gerçek çalışır), yalnız ÇALIŞTIRMA adımı kontrollü hâle getirilir."""
    from app.wren_service import WrenService

    def fake_query(self, sql, *args, **kwargs):
        return {"columns": ["ad", "tc_kimlik"],
               "rows": [{"ad": "Test", "tc_kimlik": _VALID_TCKN}], "row_count": 1}

    monkeypatch.setattr(WrenService, "query", fake_query)


def test_query_masks_tckn_for_non_privileged_role(client):
    make_tenant_user("analyst-pii@dima.local", "analyst-pii-1", "analyst")
    c = _login_as(client, "analyst-pii@dima.local", "analyst-pii-1")
    r = c.post("/query", json={"sql": f"SELECT '{_VALID_TCKN}' AS tc_kimlik"})
    assert r.status_code == 200, r.text
    row = r.json()["rows"][0]
    assert row["tc_kimlik"] != _VALID_TCKN
    assert "*" in row["tc_kimlik"]
    assert row["tc_kimlik"].startswith("100")  # baş korunur
    assert row["tc_kimlik"].endswith("46")     # son korunur


def test_query_owner_role_sees_unmasked_and_is_audited(client):
    """owner (rank 3) >= pii:view (rank 2) → maskesiz görür; bu erişim audit'e düşer."""
    r = client.post("/query", json={"sql": f"SELECT '{_VALID_TCKN}' AS tc_kimlik"})
    assert r.status_code == 200, r.text
    row = r.json()["rows"][0]
    assert row["tc_kimlik"] == _VALID_TCKN

    from sqlmodel import Session, select

    from control_plane.db import engine
    from control_plane.models import AuditLog

    with Session(engine) as s:
        found = s.exec(select(AuditLog).where(AuditLog.action == "pii_view")).all()
    assert found


def test_query_leaves_non_pii_numeric_columns_untouched(client):
    """Sayısal/rastgele-görünen ama checksum'ı GEÇERSİZ bir 11 haneli değer (ör. bir
    sipariş numarası) YANLIŞLIKLA maskelenmemeli (false-positive önleme, aynı zamanda
    pii:view rolü İÇİN de zaten dokunulmuyor test edilmiş oluyor)."""
    make_tenant_user("analyst-pii2@dima.local", "analyst-pii2-1", "analyst")
    c = _login_as(client, "analyst-pii2@dima.local", "analyst-pii2-1")
    r = c.post("/query", json={"sql": "SELECT 12345678901 AS siparis_no, 45000.5 AS tutar"})
    assert r.status_code == 200, r.text
    row = r.json()["rows"][0]
    assert str(row["siparis_no"]) == "12345678901"
    assert float(row["tutar"]) == 45000.5


def test_apply_to_ask_response_masks_result_and_interpretation_text():
    """Birim seviyesinde: app/pii.py::apply_to_ask_response doğrudan bir AskResponse
    üzerinde (cube veri yolu olmadan) çalışır — /ask'in gerçek cube'ları bugün tc_kimlik
    SEÇMESE de gelecekte bir cube bunu yanlışlıkla açığa çıkarırsa BU KATMAN yakalar."""
    import uuid

    from control_plane.authorize import Principal

    from app.pii import apply_to_ask_response
    from app.schemas import AskResponse, QueryResult

    def _principal(role: str) -> Principal:
        return Principal(user_id=str(uuid.uuid4()), tenant_id=str(uuid.uuid4()), roles=[role])

    resp = AskResponse(
        question="x", source="cube",
        result=QueryResult(columns=["ad", "tc_kimlik"],
                           rows=[{"ad": "Test", "tc_kimlik": _VALID_TCKN}], row_count=1),
        interpretation={"facts": [{"type": "x", "text": f"TCKN {_VALID_TCKN} bulundu"}],
                       "summary": f"Kimlik: {_VALID_TCKN}"},
    )
    shown = apply_to_ask_response(resp, _principal("viewer"))
    assert shown is False
    assert resp.result.rows[0]["tc_kimlik"] != _VALID_TCKN
    assert _VALID_TCKN not in resp.interpretation["summary"]
    assert _VALID_TCKN not in resp.interpretation["facts"][0]["text"]

    resp2 = AskResponse(
        question="x", source="cube",
        result=QueryResult(columns=["tc_kimlik"], rows=[{"tc_kimlik": _VALID_TCKN}], row_count=1),
    )
    shown2 = apply_to_ask_response(resp2, _principal("owner"))
    assert shown2 is True
    assert resp2.result.rows[0]["tc_kimlik"] == _VALID_TCKN


def test_report_masks_tckn_for_non_privileged_role(client, monkeypatch):
    """Yüzey 1/3: `/report` (çok-blok rapor derleme) — doğrulama turundan ÖNCE hiç
    maskelemiyordu."""
    _inject_tckn_query(monkeypatch)
    make_tenant_user("analyst-pii-report@dima.local", "analyst-pii-report-1", "analyst")
    c = _login_as(client, "analyst-pii-report@dima.local", "analyst-pii-report-1")
    r = c.post("/report", json={"title": "PII testi", "blocks": [{"cube_query": _CQ}]})
    assert r.status_code == 200, r.text
    row = r.json()["pages"][0][0]["result"]["rows"][0]
    assert row["tc_kimlik"] != _VALID_TCKN
    assert "*" in row["tc_kimlik"]


def test_report_owner_sees_unmasked_and_is_audited(client, monkeypatch):
    _inject_tckn_query(monkeypatch)
    r = client.post("/report", json={"title": "PII testi", "blocks": [{"cube_query": _CQ}]})
    assert r.status_code == 200, r.text
    row = r.json()["pages"][0][0]["result"]["rows"][0]
    assert row["tc_kimlik"] == _VALID_TCKN

    from sqlmodel import Session, select

    from control_plane.db import engine
    from control_plane.models import AuditLog

    with Session(engine) as s:
        found = s.exec(
            select(AuditLog).where(AuditLog.action == "pii_view",
                                   AuditLog.nl_question.contains("rapor"))
        ).all()
    assert found


def test_dashboard_data_masks_tckn_for_non_privileged_role(client, monkeypatch):
    """Yüzey 2/3: `GET /dashboards/{id}/data` (panonun CANLI veri ucu) — doğrulama
    turundan ÖNCE hiç maskelemiyordu."""
    _inject_tckn_query(monkeypatch)
    make_tenant_user("analyst-pii-dash@dima.local", "analyst-pii-dash-1", "analyst")
    c = _login_as(client, "analyst-pii-dash@dima.local", "analyst-pii-dash-1")
    did = c.post("/dashboards", json={"title": "pii testi"}).json()["id"]
    c.post(f"/dashboards/{did}/widgets", json={"cube_query": _CQ, "period": "bu yıl"})
    data = c.get(f"/dashboards/{did}/data").json()
    row = data["widgets"][0]["result"]["rows"][0]
    assert row["tc_kimlik"] != _VALID_TCKN
    assert "*" in row["tc_kimlik"]


def test_dashboard_data_owner_sees_unmasked_and_is_audited(client, monkeypatch):
    _inject_tckn_query(monkeypatch)
    did = client.post("/dashboards", json={"title": "pii testi owner"}).json()["id"]
    client.post(f"/dashboards/{did}/widgets", json={"cube_query": _CQ, "period": "bu yıl"})
    data = client.get(f"/dashboards/{did}/data").json()
    row = data["widgets"][0]["result"]["rows"][0]
    assert row["tc_kimlik"] == _VALID_TCKN

    from sqlmodel import Session, select

    from control_plane.db import engine
    from control_plane.models import AuditLog

    with Session(engine) as s:
        found = s.exec(
            select(AuditLog).where(AuditLog.action == "pii_view",
                                   AuditLog.nl_question.contains("pano widget"))
        ).all()
    assert found


def test_schedule_delivery_always_masks_tckn_even_for_owner(client, monkeypatch):
    """Yüzey 3/3: zamanlanmış rapor TESLİMİ (`run_schedule` → `channels.NotificationEvent.
    rows` → `app/email_render.py::render_email`'in GERÇEKTEN e-posta gövdesine gömdüğü veri,
    bkz. email_render.py:64 `rows=event.rows[:20]`) — doğrulama turundan ÖNCE hiç
    maskelemiyordu. Diğer iki yüzeyden FARKLI olarak bu yol `principal=None` ile HER ZAMAN
    maskeler (fail-closed) — otomatik/arka-plan bir işte hangi e-posta ALICISININ
    `pii:view` yetkisi olduğu ÖNCEDEN bilinemez, bu yüzden koşan kullanıcı (aşağıda owner,
    pii:view sahibi) sonucu BİLE maskeli çıkar."""
    _inject_tckn_query(monkeypatch)

    from app import channels as channels_mod

    captured: dict = {}
    original_dispatch = channels_mod.dispatch

    def capture_dispatch(event, targets, ctx):
        captured["event"] = event
        return original_dispatch(event, targets, ctx)

    monkeypatch.setattr(channels_mod, "dispatch", capture_dispatch)

    sid = client.post("/schedules", json={
        "label": "pii-testi", "cube_query": _CQ, "period": "bu yıl",
    }).json()["schedule"]["id"]
    try:
        r = client.post(f"/schedules/{sid}/run")
        assert r.status_code == 200, r.text
        assert "event" in captured, "channels.dispatch hiç çağrılmadı"
        rows = captured["event"].rows
        assert rows, "test kurulumunda satır bekleniyordu"
        assert rows[0]["tc_kimlik"] != _VALID_TCKN
        assert "*" in rows[0]["tc_kimlik"]
    finally:
        client.delete(f"/schedules/{sid}")
