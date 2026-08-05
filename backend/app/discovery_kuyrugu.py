"""**DISCOVERY KUYRUĞA ALMA** — uzun süren Discovery'yi arka plan işine devretme.
[bayrak: `ask_async_discovery`]

## Neden `ask.py`'den ÇIKTI

`ask.py` **dosya** tavanını 23 satır aşıyordu (2442 / 2419). `ask()` gövdesi bir önceki
adımda `gorsel_ekleme`'ye çıkarak tavanın altına inmişti (1206 → 1150); kalan aşım
**modül düzeyindeydi**.

⚠ Ve aday yine **bağımlılıkla** seçildi: `_ask_drill_govde` 289 satırla üç kat büyüktü ama
`ask.py`'nin **üç yerel fonksiyonuna** dokunuyor (`_service_for` · `_adhoc_service_for` ·
`_drill_record_contract`) — taşımak ya döngüsel import ya da üç çözücü parametresi
demekti. `kuyrukla` ise `ask.py`'nin **hiçbir** yerel fonksiyonuna dokunmuyor: `runner`
zaten **parametre** olarak geliyordu.

🔴 *Bir bloğu taşınabilir yapan şey, bulunduğu dosyayla arasındaki bağların **sayısı**
değil, **yönüdür**: dışarıya bakan bağlar import edilebilir, içeriye bakanlar edilemez.*

⚠ Gövde **birebir** taşındı; tek değişiklik adı (`_queue_discovery_job` → `kuyrukla`,
modül adı zaten bağlamı taşıyor). *Bir taşıma, aynı zamanda bir iyileştirme olmamalıdır —
yoksa hangisinin kırdığı ölçülemez.*
"""

from __future__ import annotations

import json
import threading
import uuid
from datetime import datetime

from fastapi import Request
from sqlmodel import Session

from app import ask_jobs, istek_kimligi
from app.logging_setup import get_logger
from app.schemas import AskRequest, AskResponse
from control_plane.db import engine
from control_plane.models import AskJob

_log = get_logger("ask")  # ⚠ AYNI ağaç: taşınan kodun log satırları yer değiştirmemeli

def kuyrukla(request: Request, body: AskRequest, principal, runner) -> AskResponse:
    """Faz 4.1 (dış yol haritası 0.1'in BullMQ/Redis'siz karşılığı) — Discovery'yi arka-plan
    işine kuyruklar (yalnız `ask_async_discovery` bayrağı açıkken çağrılır). `CloneJob` ile
    AYNI desen (control_plane/models.py::AskJob docstring'i): DB-tablosu tabanlı durum +
    thread — in-memory DEĞİL, süreç yeniden başlasa da iz bırakır.

    `runner` (ask()'in `_run_discovery` kapanışı) zaten `service`/`schema`/`vqr`/`llm`/
    `principal`/`body`'yi KAPANIŞ olarak taşıyor — CloneJob'un aksine bunları TEKRAR DB'den
    türetmeye GEREK YOK: iş aynı süreçte, aynı anda başlıyor (yalnız İSTEMCİYE hemen dönmek
    için arka plana alınıyor), request-bağımsız yeniden-kurulum gerektirmiyor. Süreç bu iş
    bitmeden ÇÖKERSE (`app/main.py` lifespan'daki kurtarma), iş "yarıda kaldı" diye dürüstçe
    `failed`e çevrilir — sessizce kaybolmaz, ama otomatik yeniden-deneme bu ilk sürümde
    kapsam dışı (bilinçli sınır, AskJob docstring'inde gerekçeli)."""
    import json as _json
    import threading
    import uuid as _uuid

    from sqlmodel import Session

    from control_plane.db import engine
    from control_plane.models import AskJob

    tenant_id_raw = getattr(principal, "tenant_id", None)
    try:
        tenant_uuid = _uuid.UUID(str(tenant_id_raw)) if tenant_id_raw else None
    except (ValueError, TypeError):
        tenant_uuid = None

    job = AskJob(
        tenant_id=tenant_uuid, session_id=body.session_id, question=body.question,
        request_json=_json.dumps({"question": body.question, "session_id": body.session_id},
                                 ensure_ascii=False),
    )
    with Session(engine) as s:
        s.add(job)
        s.commit()
        s.refresh(job)
    job_id = job.id

    def _on_step(trace: list[str]) -> None:
        """Faz 4.12 — HER Discovery adımından sonra çağrılır, job satırına ANINDA yazar
        (best-effort: bir yazım başarısız olursa Discovery'yi DURDURMAZ, yalnız o adımın
        canlı görünürlüğü kaybolur — sonuç yine de tamamlanınca result_json'da tam gelir)."""
        try:
            import json as _json
            with Session(engine) as s:
                j = s.get(AskJob, job_id)
                if j is not None:
                    j.trace_json = _json.dumps(trace, ensure_ascii=False)
                    s.add(j)
                    s.commit()
        except Exception:
            _log.warning("AskJob canlı adım yazımı başarısız (best-effort)", exc_info=True)

    def _bg() -> None:
        with Session(engine) as s:
            j = s.get(AskJob, job_id)
            j.status = "running"
            j.started_at = datetime.utcnow()
            s.add(j)
            s.commit()
        try:
            resp = runner(on_step=_on_step)
            with Session(engine) as s:
                j = s.get(AskJob, job_id)
                # FAZ 1.12 (AI Act Md.14) — kullanıcı DURDURDUYSA sonuç YAYIMLANMAZ.
                # İptal işi öldürmez, sonucunu yayımlatmaz (gerekçe: app/ask_jobs.py):
                # yarım bir sonucu yayımlamamak, hızlı öldürmekten daha güvenlidir.
                if ask_jobs.yayimlanabilir_mi(j.status):
                    j.status = "completed"
                    j.result_json = resp.model_dump_json()
                j.finished_at = datetime.utcnow()
                s.add(j)
                s.commit()
        except Exception as exc:  # noqa: BLE001 - arka-plan işi ASLA sessizce kaybolmaz
            _log.warning("AskJob arka-plan çalıştırması başarısız", exc_info=True)
            with Session(engine) as s:
                j = s.get(AskJob, job_id)
                if ask_jobs.yayimlanabilir_mi(j.status):   # durduruldu → `failed` DEMEZ
                    j.status = "failed"
                j.error = str(exc)[:500]                   # tanı yine de yazılır
                j.finished_at = datetime.utcnow()
                s.add(j)
                s.commit()

    # 🔴 **Kimlik thread'e KOPYALANMAZ** — ve bu, `istek_kimligi`'nin belgelediği tam
    # sınırdır. Ölçüldü (`DIMA_MOTOR_CLS=on`): arka-plan Discovery işi kimliksiz koştu,
    # motor planlamada fail-closed patladı ve iz *"dürüst ret"* yerine bir `SQL_PLANNING`
    # hatası taşıdı — yani **kullanıcıya yanlış sebep** gösteriliyordu.
    #
    # ⚠ Sarmalayıcı kimliği **şimdi** yakalar: iş kuyruğa girdikten sonra istek biter ve
    # bağlam sıfırlanır. *Bir kimliği kullanacağın anda aramak, onu kaybetmenin en kolay
    # yoludur.*
    threading.Thread(target=istek_kimligi.kimlik_kopyala(_bg), daemon=True).start()
    return AskResponse(
        question=body.question, source=None, job_id=str(job_id),
        note="Bu soru arka planda hazırlanıyor…",
        trace=["Discovery: arka-plan işine kuyruklandı (ask_async_discovery)"],
    )
