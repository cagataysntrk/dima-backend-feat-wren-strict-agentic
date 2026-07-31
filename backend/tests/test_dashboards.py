"""Kullanıcı panoları (§9) — CRUD + widget + /data + ≤10 guard + izolasyon (soft-delete)."""

from __future__ import annotations

from tests.conftest import make_tenant_user
from tests.test_auth import _login_as

_CQ = {"cube": "parti", "measures": ["toplam_ciro"]}


def test_dashboard_crud_widget_and_data(client):
    did = client.post("/dashboards", json={"title": "Satış panosu"}).json()["id"]
    # widget ekle (chat sonucundaki cube_query + view_hint)
    r = client.post(f"/dashboards/{did}/widgets",
                    json={"title": "ciro", "cube_query": _CQ, "view_hint": "bar",
                          "period": "bu yıl"})
    assert r.status_code == 200, r.text
    wid = r.json()["id"]
    # get → widget görünür, cube_query taşınır
    d = client.get(f"/dashboards/{did}").json()
    assert d["own"] is True and len(d["widgets"]) == 1
    assert d["widgets"][0]["cube_query"]["measures"] == ["toplam_ciro"]
    # /data → widget koşulur (göreli dönem çözülür), sonuç döner
    data = client.get(f"/dashboards/{did}/data").json()
    assert len(data["widgets"]) == 1
    assert data["widgets"][0]["error"] is None and data["widgets"][0]["result"] is not None
    # widget soft-delete → get'te kalmaz
    assert client.delete(f"/dashboards/{did}/widgets/{wid}").json()["removed"] is True
    assert client.get(f"/dashboards/{did}").json()["widgets"] == []
    # pano soft-delete → 404
    assert client.delete(f"/dashboards/{did}").json()["removed"] is True
    assert client.get(f"/dashboards/{did}").status_code == 404


def test_dashboard_widget_data_has_viz(client):
    """Pano /data widget'ı backend viz kararını taşır (cross-surface: chat ile aynı, ADR-0024)."""
    did = client.post("/dashboards", json={"title": "viz"}).json()["id"]
    client.post(f"/dashboards/{did}/widgets",
                json={"cube_query": {"cube": "parti", "measures": ["toplam_ciro"],
                                     "dimensions": ["musteri"]}, "period": "bu yıl"})
    data = client.get(f"/dashboards/{did}/data").json()
    w = data["widgets"][0]
    assert w["viz"] is not None and w["viz"]["kind"] in ("bar", "table", "pivot")


def test_dashboard_widget_preserves_yoy_compare(client):
    """"panoya ekle" YoY grafiğini BİRE BİR taşır: compare saklanır + /data geçen-yıl serisini üretir."""
    did = client.post("/dashboards", json={"title": "yoy"}).json()["id"]
    cq = {"cube": "parti", "measures": ["toplam_ciro"], "dimensions": ["musteri"],
          "compare": "yoy",
          "filters": [{"dimension": "tarih", "operator": "gte", "value": "2026-01-01"}]}
    client.post(f"/dashboards/{did}/widgets", json={"cube_query": cq, "view_hint": "bar#__tumu__"})
    d = client.get(f"/dashboards/{did}").json()
    assert d["widgets"][0]["cube_query"].get("compare") == "yoy"  # compare korundu
    assert d["widgets"][0]["view_hint"] == "bar#__tumu__"          # bileşik görünüm korundu
    data = client.get(f"/dashboards/{did}/data").json()
    cols = data["widgets"][0]["result"]["columns"]
    assert any(c.endswith("_gecen") for c in cols)                # geçen-yıl serisi üretildi


def test_dashboard_widget_patch_view_persists(client):
    """Widget görünüm durumu KAYDEDİLİR (view_hint) — panonun o hâli kalıcı (yeniden yükleme)."""
    did = client.post("/dashboards", json={"title": "kaydet"}).json()["id"]
    wid = client.post(f"/dashboards/{did}/widgets",
                      json={"cube_query": _CQ, "view_hint": "bar"}).json()["id"]
    r = client.patch(f"/dashboards/{did}/widgets/{wid}", json={"view_hint": "table"})
    assert r.status_code == 200 and r.json()["updated"] is True
    d = client.get(f"/dashboards/{did}").json()
    assert d["widgets"][0]["view_hint"] == "table"


def test_dashboard_invalid_cube_query_rejected(client):
    did = client.post("/dashboards", json={"title": "x"}).json()["id"]
    r = client.post(f"/dashboards/{did}/widgets",
                    json={"cube_query": {"cube": "parti", "measures": ["uydurma_olcu"]}})
    assert r.status_code == 400


def test_dashboard_max_per_user_guard(client):
    make_tenant_user("dashlimit@dima.local", "dashlimit-parola-1", "owner")
    c = _login_as(client, "dashlimit@dima.local", "dashlimit-parola-1")
    for i in range(10):
        assert c.post("/dashboards", json={"title": f"p{i}"}).status_code == 200
    r = c.post("/dashboards", json={"title": "11."})
    assert r.status_code == 409


def test_dashboard_isolation_other_user_404(client):
    did = client.post("/dashboards", json={"title": "özel"}).json()["id"]
    make_tenant_user("dashother@dima.local", "dashother-parola-1", "owner")
    c = _login_as(client, "dashother@dima.local", "dashother-parola-1")
    # başka kullanıcının (private) panosu — varlığı sızmaz
    assert c.get(f"/dashboards/{did}").status_code == 404
    assert c.post(f"/dashboards/{did}/widgets", json={"cube_query": _CQ}).status_code == 404


def test_dashboard_widget_rejects_other_tenant_cube(client):
    """Cross-tenant sızıntı regresyonu (31 Temmuz 2026): `add_widget`/`dashboard_data`
    `wren_for_request(request)` çağırıyordu ama router `require_company` dependency'sini
    HİÇ tetiklemiyordu — bu yalnız `request.state.wren`'i dolduran tek yer olduğundan,
    `wren_for_request` her zaman SÜREÇ VARSAYILANI (demo-boyahane) servisine düşüyordu.
    Canlı testle kanıtlandı: "atiksan" (sektör: geri-donusum, `oee` cube'u YOK) tenant'ı
    demo-boyahane'ye özel `oee` cube'unu widget'a ekleyebiliyordu — statik regresyon kilidi
    (test_no_default_tenant_leak.py) bunu YAKALAYAMAZ (yalnız `request.app.state.wren`
    doğrudan kullanımını arar, eksik dependency'yi değil). Düzeltme: her iki endpoint'e
    `Depends(require_company)` eklendi — bu test canlı davranışı (yalnız statik deseni değil)
    kilitler."""
    make_tenant_user("atiksan-owner@dima.local", "atiksan-parola-1", "owner",
                     tenant_slug="atiksan")
    c = _login_as(client, "atiksan-owner@dima.local", "atiksan-parola-1")
    did = c.post("/dashboards", json={"title": "atiksan panosu"}).json()["id"]
    # oee yalnız demo-boyahane'de var; atiksan (geri-donusum sektörü) bu cube'u TANIMAZ —
    # kabul edilirse demo-boyahane'nin şeması/DB'si yanlışlıkla kullanılıyor demektir.
    r = c.post(f"/dashboards/{did}/widgets",
              json={"cube_query": {"cube": "oee", "measures": ["ort_oee"]}})
    assert r.status_code == 400, (
        f"atiksan tenant'ı demo-boyahane'nin 'oee' cube'unu kabul etti (cross-tenant sızıntı): {r.text}")
