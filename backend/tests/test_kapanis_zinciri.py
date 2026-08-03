"""FAZ A4 — kapanış zinciri **tek yerde**: `app/answer.py::seal`.

Denetimde (2 Ağustos 2026) beş ayrı ihlalin **tek ortak kök nedeni** bulundu: `ask()`
1180 satırlık bir fonksiyondu ve kapanış zinciri onun içinde bir **closure** olarak
yaşıyordu. Closure `body`/`request`/`principal`/`t0`/`is_followup`'a kapandığı için
dışarıdan çağrılamıyordu — ve bu, ihlallerin **sebebiydi**, sonucu değil:

| İhlal | Ne oluyordu |
|---|---|
| `/cube` paralel zincir yazmıştı | `is_new_topic`/`thread_id`/`reply_to_label` **set edilmiyordu** |
| `/cube` contract'ı sessizce yutuyordu | `except Exception: pass` — ADR-0020 ihlali; 20 satır aşağıda audit *bilerek* sarılmamıştı |
| `_try_kpi` zinciri tamamen atlıyordu | contract **yok**, audit **yok**, PII maskesi **yok** |
| Üç ayrı contract kaydedici | closure + `/cube` inline + drill |
| Hiçbiri izole test edilemiyordu | closure'lar `body`'ye kapanıyor |

`_finish`'in kendi yorumu bu kök nedenin daha önce bir üretim hatası ürettiğini zaten
kaydetmişti — ama düzeltme yine closure'ın içine yazılmıştı.

Bu dosya sözleşmeyi kilitler: **bir cevap ancak `seal()`'den geçerse yayımlanabilir.**
Aynı sözleşme Faz F'nin (agentic araç kaydı) taşıyıcısıdır — bir ajan aracının çıktısı,
kullanıcının bir sorusundan daha az denetlenebilir olamaz.
"""

from __future__ import annotations

import pytest
from sqlmodel import Session, col, desc, select

from control_plane.db import engine
from control_plane.models import AuditLog
from tests.conftest import ask


def _son_audit(n: int = 1):
    with Session(engine) as s:
        return s.exec(select(AuditLog).where(AuditLog.action == "query")
                      .order_by(desc(col(AuditLog.id))).limit(n)).all()


def _audit_sayisi() -> int:
    with Session(engine) as s:
        return len(s.exec(select(AuditLog).where(AuditLog.action == "query")).all())


def test_ask_kapanistan_gecer(client):
    once = _audit_sayisi()
    d = ask(client, "bu yıl fire oranı")
    assert d.get("source"), d.get("note")
    assert _audit_sayisi() > once, "/ask audit izi bırakmadı"


def test_cube_artik_THREAD_alanlarini_tasiyor(client):
    """`/cube` kendi zincirini yazdığı için `is_new_topic`/`thread_id` HİÇ set etmiyordu.
    Aynı `seal()`'den geçtiğine göre artık taşımalı."""
    from app.config import get_settings
    from app.wren_service import WrenService

    s = get_settings()
    svc = WrenService(s.resolved_project_dir(), datasource=s.datasource,
                      connection_info=s.connection_dict())
    meta = next(c for c in svc.schema()["cubes"] if c["name"] == "parti")
    cq = {"cube": "parti", "measures": [meta["measures"][0]]}
    r = client.post("/cube", json={"cube_query": cq, "thread_id": "t-42"})
    assert r.status_code == 200, r.text
    d = r.json()
    assert d.get("thread_id") == "t-42", "seal thread_id'yi taşımadı"
    assert d.get("contract_id"), "/cube makbuzsuz döndü"


def test_cube_de_AUDIT_birakir(client):
    from app.config import get_settings
    from app.wren_service import WrenService

    s = get_settings()
    svc = WrenService(s.resolved_project_dir(), datasource=s.datasource,
                      connection_info=s.connection_dict())
    meta = next(c for c in svc.schema()["cubes"] if c["name"] == "parti")
    once = _audit_sayisi()
    r = client.post("/cube", json={"cube_query": {"cube": "parti",
                                                  "measures": [meta["measures"][0]]}})
    assert r.status_code == 200
    assert _audit_sayisi() > once, "/cube audit izi bırakmadı"


def test_KPI_cevabi_artik_kapanistan_gecer(client):
    """`_try_kpi` `AskResponse`'u DOĞRUDAN `return` ediyordu → contract yok, audit yok,
    PII maskesi yok. MIMARI §2 bunu "bilinen sapma" diye kaydetmişti ama kapsamı belgede
    yazandan genişti (yalnız "yorum" değil, üç garanti birden)."""
    from app.config import get_settings
    from app.wren_service import WrenService

    s = get_settings()
    svc = WrenService(s.resolved_project_dir(), datasource=s.datasource,
                      connection_info=s.connection_dict())
    kpis = svc.schema().get("kpis") or []
    if kpis:
        once = _audit_sayisi()
        d = ask(client, str(kpis[0].get("label") or kpis[0].get("name")))
        if d.get("kpi"):
            assert _audit_sayisi() > once, "KPI cevabı audit izi bırakmadı"
            return

    # demo-boyahane'de KPI tanımı YOK (ölçüldü: 0) → uçtan uca gösterilemiyor. Atlanmış bir
    # testle yetinmek yerine BAĞLANTI doğrulanır: `_try_kpi`'nin dönüşü `_finish`'ten
    # geçiyor mu? Eksik olan tam olarak buydu — `return AskResponse(...)` doğrudandı.
    import ast
    import re
    from pathlib import Path

    import app.routers.ask as ask_mod

    kaynak = Path(ask_mod.__file__).read_text(encoding="utf-8")
    # ⚠️ DİLİM SINIRI KIRILGANDI: eski sürüm `_try_kpi` ile `_try_fresh_intent`
    # ARASINI tarıyordu; araya yeni bir yardımcı eklendiği an onun (meşru) mühürsüz
    # dönüşünü `_try_kpi`'ninmiş gibi gösteriyordu. Faz F'de tam bu oldu.
    # Ölçülmesi gereken şey `_try_kpi`'NİN KENDİ gövdesidir → AST.
    _fn = next(d for d in ast.walk(ast.parse(kaynak))
               if isinstance(d, ast.FunctionDef) and d.name == "_try_kpi")
    govde = ast.unparse(ast.Module(body=_fn.body, type_ignores=[]))
    ciplak = re.findall(r"return AskResponse\(", govde)
    assert not ciplak, (
        "`_try_kpi` `AskResponse`'u DOĞRUDAN döndürüyor — kapanış zincirini atlıyor "
        "(contract yok, audit yok, PII maskesi yok). `_finish(...)` ile sarmalanmalı.")
    assert "_finish(AskResponse(" in govde, "`_try_kpi` kapanıştan geçmiyor"


def test_contract_kaydi_SESSIZCE_yutulmaz(client, caplog, monkeypatch):
    """`/cube` eskiden `except Exception: pass` yazıyordu. Kayıt başarısız olursa akış
    düşmemeli ama **görünmez de kalmamalı** (ADR-0020)."""
    import logging

    from app import answer

    class _PatlayanStore:
        def record(self, **kw):
            raise RuntimeError("kasıtlı hata")

    from app.config import get_settings
    from app.wren_service import WrenService

    s = get_settings()
    svc = WrenService(s.resolved_project_dir(), datasource=s.datasource,
                      connection_info=s.connection_dict())
    monkeypatch.setattr(client.app.state, "contracts", _PatlayanStore(), raising=False)
    with caplog.at_level(logging.WARNING):
        cid = answer.record_contract(
            type("R", (), {"app": client.app, "state": type("S", (), {})()})(),
            service=svc, session_id=None, question="x", cube_query={}, sql="SELECT 1",
            result=None, source="cube")
    assert cid is None
    assert any("Contract" in r.message for r in caplog.records), \
        "contract hatası sessizce yutuldu"


def test_seal_TEK_uygulama():
    """Kapanış zincirinin ikinci bir kopyası doğmasın: `/cube`'un eski satır-içi zinciri
    (`_maybe_interpret` + `_attach_next_steps` + … elle sıralanmış) geri gelmemeli."""
    from pathlib import Path

    import app.routers.ask as ask_mod

    kaynak = Path(ask_mod.__file__).read_text(encoding="utf-8")
    # Zenginleştirme yardımcıları artık YALNIZ answer.py'de çağrılır.
    for ad in ("_maybe_interpret(", "_attach_recommendations(", "_persist_message("):
        assert kaynak.count(ad) <= 1, (
            f"{ad} `ask.py`'de {kaynak.count(ad)} kez çağrılıyor — kapanış zinciri yeniden "
            "kopyalanmış olabilir; tek gövde `app/answer.py::seal`'dedir")
    assert "except Exception:\n        pass" not in kaynak, \
        "sessiz yutma deseni geri gelmiş (ADR-0020)"


def test_answer_modulu_ROUTER_import_etmez():
    """Katman yönü: `answer.py` bir kütüphanedir, router'a bağımlı olamaz — aksi halde
    Faz F'de bir ajan aracı onu kullanamaz (döngüsel import)."""
    from pathlib import Path

    import app.answer as answer_mod

    kaynak = Path(answer_mod.__file__).read_text(encoding="utf-8")
    assert "from app.routers" not in kaynak and "import app.routers" not in kaynak, \
        "answer.py router'a bağımlı — katman yönü ters"
