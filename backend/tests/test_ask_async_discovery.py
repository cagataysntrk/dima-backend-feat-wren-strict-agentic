"""Faz 4.1 (31 Temmuz 2026) — Discovery'nin arka-plan iş kuyruğu karşılığı (AskJob).

Bayrak `ask_async_discovery` VARSAYILAN KAPALI (demo/packs/features.yml'e bilerek
eklenmedi) — bu testler flag'i yalnız KENDİ SÜRELERİNCE (monkeypatch, testten sonra
otomatik geri alınır) açar; session-scoped `client` fixture'ını paylaşan DİĞER testler
etkilenmez. "asdf zxcv listele" `test_discovery_execution_failure.py`'de olduğu gibi
`route()`'un DOĞAL olarak None döndüğü (Discovery'ye düşen) bir soru — mock gerekmez.
    ## ⟳ ARAÇ DEĞİŞTİ (2026-08-06) — ölçüt DEĞİL

    Bu test `"sevkiyat durumu"` kullanıyordu ve kural motoru ona
    `SELECT COUNT(*) FROM partiler` → **37 878** üretiyordu. O bir **uydurmaydı**: dört
    farklı anlamsız soru aynı sayıyı veriyordu (`tests/test_uydurma_sayi_yok.py`) ve dal
    `ce5177d`de kapatıldı → bu kapı kırmızıya döndü.

    Yeni araç `"asdf zxcv listele"`: kapsam kapısından düşer, Discovery'ye ulaşır ve
    kural motorunun **satır dökümü** dalından cevaplanır. Döküm bir sayı UYDURMAZ —
    veriyi olduğu gibi gösterir. *Bir kapının ölçtüğü şey doğruysa, o şeyi ölçme biçimi
    değişebilir.*
"""

from __future__ import annotations

import json
import time

import pytest


def _enable_async_discovery(monkeypatch) -> None:
    import app.features as features_mod

    original = features_mod.resolve_for

    def fake(settings, principal=None):
        flags = original(settings, principal)
        flags["ask_async_discovery"] = "beta"
        return flags

    monkeypatch.setattr(features_mod, "resolve_for", fake)
    # VQR'ı devre dışı bırak: "asdf zxcv listele" ÖNCEKİ bir testte (flag-off) BAĞIMSIZ
    # soru olarak başarıyla cevaplanıp otomatik VQR'a yazılmış olabilir (adım 6, ask.py) —
    # sonraki çağrılarda near_exact eşleşmesi Discovery'ye HİÇ uğramadan (ve dolayısıyla
    # bu bayrak kontrolüne hiç uğramadan) VQR'dan cevap dönebilirdi. Testler birbirinden
    # bağımsız olmalı (VQR'ın kendi davranışı AYRI, zaten test_ask_golden.py'de kanıtlı).
    import app.company_registry as registry_mod

    monkeypatch.setattr(registry_mod, "vqr_for_request", lambda request: None)


def _poll_job(client, job_id: str, *, max_tries: int = 100, delay: float = 0.15) -> dict:
    for _ in range(max_tries):
        jr = client.get(f"/ask/jobs/{job_id}")
        assert jr.status_code == 200, jr.text
        jbody = jr.json()
        if jbody["status"] in ("completed", "failed"):
            return jbody
        time.sleep(delay)
    pytest.fail(f"AskJob {job_id} zaman aşımına uğradı (poll)")


def test_flag_off_by_default_discovery_stays_synchronous(client):
    """Regresyon kilidi: bayrak override'sız (varsayılan hal) /ask HİÇBİR ZAMAN job_id
    döndürmez — Discovery senkron çalışır, tam AskResponse ilk çağrıda gelir."""
    r = client.post("/ask", json={"question": "asdf zxcv listele", "execute": True,
                                  "session_id": "eval-sync-default"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("job_id") is None
    # Discovery'ye düştüğü ve normal şekilde cevaplandığı (kural-tabanlı sağlayıcı testte)
    assert body["source"] is not None


def test_ask_queues_background_job_when_flag_on(client, monkeypatch):
    _enable_async_discovery(monkeypatch)
    r = client.post("/ask", json={"question": "asdf zxcv listele", "execute": True,
                                  "session_id": "eval-async-1"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["job_id"], body
    assert body["source"] is None
    assert body["result"] is None
    assert any("arka-plan işine kuyruklandı" in t for t in body["trace"])

    jbody = _poll_job(client, body["job_id"])
    assert jbody["status"] == "completed", jbody
    assert jbody["response"] is not None
    assert jbody["response"]["question"] == "asdf zxcv listele"
    assert jbody["response"].get("job_id") is None  # tamamlanan cevap kendi job_id taşımaz


def test_ask_job_persists_in_db(client, monkeypatch):
    """Kalıcılık: job DB'de durur, TAZE bir Session ile (yanıt nesnesinden bağımsız)
    sorgulanabilir — in-memory değil (dış yol haritası 0.1 'bitti sayılır'ı)."""
    _enable_async_discovery(monkeypatch)
    r = client.post("/ask", json={"question": "asdf zxcv listele", "execute": True,
                                  "session_id": "eval-async-2"})
    job_id = r.json()["job_id"]
    _poll_job(client, job_id)

    import uuid

    from sqlmodel import Session

    from control_plane.db import engine
    from control_plane.models import AskJob

    with Session(engine) as s:
        row = s.get(AskJob, uuid.UUID(job_id))
        assert row is not None
        assert row.status == "completed"
        assert row.result_json


def test_ask_job_failure_is_honest_never_silent(client, monkeypatch):
    """Discovery arka-planda patlarsa (ör. motor hatası) job status='failed' + hata metni
    taşır — ne çıplak 500 ne sessiz kayboluş."""
    _enable_async_discovery(monkeypatch)

    from app.wren_service import WrenService

    def always_fails(self, sql: str, *args, **kwargs):
        raise RuntimeError("simulated background failure")

    monkeypatch.setattr(WrenService, "query", always_fails)

    r = client.post("/ask", json={"question": "asdf zxcv listele", "execute": True,
                                  "session_id": "eval-async-3"})
    assert r.status_code == 200, r.text
    job_id = r.json()["job_id"]
    jbody = _poll_job(client, job_id)
    # _run_discovery kendi self-healing'i başarısız olursa dürüst ret (source=None, note
    # dolu) İLE 'completed' döner (kendi içinde zaten dürüst-ret'e düşüyor, çökmüyor) —
    # tamamen beklenmeyen bir istisna olursa da (bkz. _queue_discovery_job) job 'failed' olur.
    assert jbody["status"] in ("completed", "failed")
    if jbody["status"] == "completed":
        assert jbody["response"]["source"] is None
        assert jbody["response"]["note"]
    else:
        assert jbody["error"]


def test_ask_job_status_unknown_id_404(client, monkeypatch):
    _enable_async_discovery(monkeypatch)
    import uuid

    r = client.get(f"/ask/jobs/{uuid.uuid4()}")
    assert r.status_code == 404


def test_ask_job_status_invalid_id_400(client):
    r = client.get("/ask/jobs/not-a-uuid")
    assert r.status_code == 400


def test_ask_job_trace_accumulates_and_persists(client, monkeypatch):
    """Faz 4.12 (1 Ağustos 2026) — dış yol haritası 2.9 "canlı düşünme adımları": job
    TAMAMLANDIKTAN SONRA bile `trace_json`'ın GERÇEKTEN adım-adım (on_step callback'i
    üzerinden, sonuçtan post-hoc türetilmeden) yazıldığını doğrudan DB'den kontrol eder —
    nihai job.trace ile response.trace'in TUTARLI olduğunu da kanıtlar."""
    _enable_async_discovery(monkeypatch)
    r = client.post("/ask", json={"question": "asdf zxcv listele", "execute": True,
                                  "session_id": "eval-async-trace"})
    job_id = r.json()["job_id"]
    jbody = _poll_job(client, job_id)
    assert jbody["status"] == "completed"
    assert jbody["trace"], jbody
    assert jbody["trace"] == jbody["response"]["trace"]

    import uuid

    from sqlmodel import Session

    from control_plane.db import engine
    from control_plane.models import AskJob

    with Session(engine) as s:
        row = s.get(AskJob, uuid.UUID(job_id))
        assert row.trace_json is not None
        assert json.loads(row.trace_json) == jbody["trace"]
