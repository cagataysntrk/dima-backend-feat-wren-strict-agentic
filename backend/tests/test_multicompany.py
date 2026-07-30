"""Çok-şirketli runtime v1 testleri (ADR-0016 evrimi).

Varsayılan şirket (settings.company = demo-boyahane) startup'ta yüklü; başka
tenant'ın kullanıcısı gelince require_company şirket projesini registry'den
derleyip isteğe bağlar. Lab SQL Server'ına BAĞLANMAZ: /schema yalnız mdl okur
(kategorik değer zenginleştirme DB'ye ulaşamayınca sessizce boş kalır).
"""

from __future__ import annotations

from tests.conftest import TEST_USER, make_tenant_user


def _login(client, email: str, password: str) -> dict:
    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_varsayilan_sirket_kullanicisi_ayni_kalir(client):
    h = _login(client, TEST_USER["email"], TEST_USER["password"])
    r = client.get("/schema", headers=h)
    assert r.status_code == 200
    models = {m["name"] for m in r.json()["models"]}
    assert "partiler" in models  # boyahane veri düzlemi


def test_baska_tenant_kullanicisi_kendi_sirketini_gorur(client):
    """gitas senaryosu: 'Bu firma için veri düzlemi bu sunucuda yüklü değil' yerine
    tenant'ın kendi şirket projesi derlenir ve şeması döner."""
    make_tenant_user("owner@atiksan.test", "atiksan-parola-1", tenant_slug="atiksan")
    h = _login(client, "owner@atiksan.test", "atiksan-parola-1")
    r = client.get("/schema", headers=h)
    assert r.status_code == 200, r.text
    models = {m["name"] for m in r.json()["models"]}
    assert "stoklar" in models and "cari_hesap_hareketleri" in models  # mikro-v16
    assert "partiler" not in models  # boyahane şeması SIZMAZ
    cubes = {c["name"] for c in r.json()["cubes"]}
    # karlilik: jenerik türev-metrik (mikro turev.yml binding'inden üretilir — DB-bağımsız)
    assert cubes == {"cari", "ticaret", "karlilik", "cari_finans"}


def test_sirketsiz_tenant_403(client):
    """company.yml'i olmayan tenant: kibar 403 (varlık sızdırmayan mesaj)."""
    make_tenant_user("owner@hayalet.test", "hayalet-parola-1", tenant_slug="hayalet-ltd")
    h = _login(client, "owner@hayalet.test", "hayalet-parola-1")
    r = client.get("/schema", headers=h)
    assert r.status_code == 403
    assert "yüklü değil" in r.json()["detail"]
