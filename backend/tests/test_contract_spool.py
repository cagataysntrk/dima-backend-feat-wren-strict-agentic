"""Contract durable spool (audit deseni, 2026-07-29) — DB-down'da kanıt kaybolmaz:
record() spool'a alır → replay_spool() DB'ye boşaltır → merge() ile idempotent (çift-kayıt yok)."""

from __future__ import annotations

from app import contracts
from app.contracts import ContractStore
from control_plane.models import ContractLog


def _cq():
    return {"cube": "parti", "measures": ["toplam_ciro"]}


def test_contract_spools_on_db_down_then_replays(tmp_path, monkeypatch):
    from control_plane.db import init_db
    init_db()
    monkeypatch.setattr(contracts, "_SPOOL_PATH", tmp_path / "contract-spool.jsonl")

    # DB down simülasyonu → record() spool'a almalı (cid yine döner, rapor akmaya devam).
    monkeypatch.setattr(contracts, "_persist", lambda row: (_ for _ in ()).throw(RuntimeError("db down")))
    store = ContractStore()
    cid = store.record(session_id="s1", question="bu ay ciro", cube_query=_cq(),
                       sql="SELECT 1", result={"rows": [{"x": 1}], "row_count": 1},
                       source="cube", schema_version="v1", tenant_id=None)
    assert cid.startswith("c-")
    assert (tmp_path / "contract-spool.jsonl").exists()  # kanıt spool'da, kaybolmadı
    assert store.get(cid) is None  # henüz DB'de yok (DB down'du)

    # DB geri geldi → replay_spool() spool'u DB'ye boşaltır (gerçek _persist geri).
    monkeypatch.undo()
    monkeypatch.setattr(contracts, "_SPOOL_PATH", tmp_path / "contract-spool.jsonl")
    flushed = contracts.replay_spool()
    assert flushed == 1
    row = store.get(cid)
    assert row is not None and row["question"] == "bu ay ciro"  # kanıt DB'de, ts/hash korundu
    assert not (tmp_path / "contract-spool.jsonl").exists()  # boşalınca dosya silinir


def test_replay_is_idempotent(tmp_path, monkeypatch):
    from control_plane.db import init_db
    init_db()
    spool = tmp_path / "contract-spool.jsonl"
    monkeypatch.setattr(contracts, "_SPOOL_PATH", spool)
    # Aynı contract satırını iki kez spool'a yaz (crash-sonrası çift-replay senaryosu).
    payload = {"id": "c-idem12345", "question": "q", "sql": "SELECT 1", "source": "cube",
               "schema_version": "v1", "ts": "2026-07-29T10:00:00"}
    contracts._spool_append(payload)
    contracts._spool_append(payload)
    contracts.replay_spool()
    # merge() (upsert) sayesinde tek satır — PK çakışması/çift-kayıt yok.
    from sqlmodel import Session, func, select

    from control_plane.db import engine
    with Session(engine) as s:
        n = s.exec(select(func.count()).select_from(ContractLog)
                   .where(ContractLog.id == "c-idem12345")).one()
    assert n == 1
