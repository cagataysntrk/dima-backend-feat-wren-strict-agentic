"""DbConnection yönetimi + fingerprint testleri (ADR-0017 Faz 2).

Canlı SQL Server'a BAĞLANMAZ: CRUD sqlite control-plane'de, şifreleme birim
düzeyinde, fingerprint saf eşleştirici üzerinden test edilir. (Canlı test/
introspection lab smoke'unda elle doğrulanır.)
"""

from __future__ import annotations

import pytest

from tests.conftest import TEST_SUPERADMIN
from tests.test_auth import _ensure_test_users


@pytest.fixture(scope="module")
def admin_client():
    from fastapi.testclient import TestClient

    from admin_app.main import create_app

    with TestClient(create_app()) as c:
        _ensure_test_users()
        yield c


def _admin_headers(admin_client):
    r = admin_client.post("/auth/login", json=TEST_SUPERADMIN)
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_crypto_roundtrip_ve_fail_closed():
    import base64

    from control_plane.crypto import CredKeyError, decrypt_secret, encrypt_secret

    kek = base64.b64encode(b"A" * 32).decode()
    blob = encrypt_secret("çok-gizli-parola", kek)
    assert b"gizli" not in blob  # düz metin sızmaz
    assert decrypt_secret(blob, kek) == "çok-gizli-parola"

    with pytest.raises(CredKeyError):
        encrypt_secret("x", "")  # KEK yok → yazılamaz (fail-closed)
    with pytest.raises(CredKeyError):
        decrypt_secret(blob, base64.b64encode(b"B" * 32).decode())  # yanlış anahtar
    with pytest.raises(CredKeyError):
        encrypt_secret("x", base64.b64encode(b"kisa").decode())  # 32 bayt değil


def test_fingerprint_eslestirici():
    from admin_app.fingerprint import logo_kapsamlari, match_packs

    packs = [
        {"key": "mikro-v16", "fingerprint": {
            "tablolar": ["CARI_HESAPLAR", "STOKLAR", "STOK_HAREKETLERI",
                         "CARI_HESAP_HAREKETLERI"]}},
        {"key": "logo-3", "fingerprint": {
            "tablolar": ["L_CAPIFIRM", "L_CAPIPERIOD"],
            "tablo_desenleri": ["LG[_]%[_]%"]}},
    ]
    mikro_tablolar = ["CARI_HESAPLAR", "STOKLAR", "STOK_HAREKETLERI",
                      "CARI_HESAP_HAREKETLERI", "BANKALAR"]
    m = match_packs(mikro_tablolar, packs)
    assert m and m[0]["key"] == "mikro-v16" and m[0]["skor"] == 1.0
    assert all(r["key"] != "logo-3" for r in m)  # çapraz eşleşme yok

    logo_tablolar = ["L_CAPIFIRM", "L_CAPIPERIOD", "LG_121_01_INVOICE",
                     "LG_121_01_STLINE", "LG_121_CLCARD", "LG_221_01_INVOICE"]
    l = match_packs(logo_tablolar, packs)
    assert l and l[0]["key"] == "logo-3" and l[0]["skor"] == 1.0

    kapsamlar = logo_kapsamlari(logo_tablolar)
    assert {(k["firma_no"], k["donem_no"]) for k in kapsamlar} == {(121, 1), (221, 1)}


def test_connection_crud_sir_saklama(client, admin_client):
    h = _admin_headers(admin_client)
    r = admin_client.post("/sadmin/tenants", headers=h,
                          json={"slug": "conn-test", "name": "Conn Test"})
    assert r.status_code == 201
    tid = r.json()["id"]

    # Desteklenmeyen datasource reddedilir.
    r = admin_client.post("/sadmin/connections", headers=h, json={
        "tenant_id": tid, "datasource": "postgres", "host": "h", "database": "d",
        "user": "u", "password": "p"})
    assert r.status_code == 400

    r = admin_client.post("/sadmin/connections", headers=h, json={
        "tenant_id": tid, "datasource": "mssql", "host": "127.0.0.1",
        "port": 14333, "database": "ATIKSAN_MIKRO", "user": "sa",
        "password": "cok-gizli-parola"})
    assert r.status_code == 201
    body = r.json()
    assert body["has_secret"] is True and body["tenant"] == "conn-test"
    assert "cok-gizli-parola" not in r.text  # parola yanıtta yok

    # Listede görünür; sır asla dönmez.
    r = admin_client.get("/sadmin/connections", headers=h)
    assert any(c["database"] == "ATIKSAN_MIKRO" for c in r.json())
    assert "cok-gizli-parola" not in r.text

    # DB'de düz metin YOKTUR (şifreli bayt).
    import uuid as _uuid

    from sqlmodel import Session

    from control_plane.db import engine
    from control_plane.models import DbConnection

    with Session(engine) as s:
        conn = s.get(DbConnection, _uuid.UUID(body["id"]))
        assert conn.secret_ciphertext and b"cok-gizli-parola" not in conn.secret_ciphertext

    # Sil → listeden düşer.
    r = admin_client.delete(f"/sadmin/connections/{body['id']}", headers=h)
    assert r.status_code == 204
    assert all(c["id"] != body["id"]
               for c in admin_client.get("/sadmin/connections", headers=h).json())


def test_connection_public_planeden_erisilemez(client):
    # Public token'la admin ucu: admin plane ayrı secret → 401.
    r = client.get("/sadmin/connections")
    assert r.status_code in (401, 403, 404)
