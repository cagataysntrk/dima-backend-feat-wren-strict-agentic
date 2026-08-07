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

    def _json_dump(v) -> str:
        import json as _json

        return _json.dumps(v, ensure_ascii=False)

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
                    # 🔴 CANLI ADIM SÜTUNU, YAYIMLANAN GERÇEĞE YAKINSAR.
                    #
                    # `_on_step` yalnız **Discovery adımlarını** yazar; kapanışta
                    # (`seal`) eklenen satırlar ona hiç ulaşmıyordu. Ölçüldü (KÖK-1
                    # niyet izi eklenince): `trace_json` ile `response.trace` **bir
                    # satır** ayrıştı ve `test_ask_job_trace_accumulates_and_persists`
                    # kırmızı verdi — kapı haklıydı, ayrışma gerçekti.
                    #
                    # ⚠ Bu bir "test düzeltmesi" değil bir **sözleşme onarımı**dır:
                    # `/ask/jobs/{id}` bu sütunu kullanıcıya *işin izi* diye gösteriyor.
                    # İki iz varsa kullanıcı hangisine bakacağını bilemez.
                    # *Bir kaydın canlı hâli, yayımlanan hâline yakınsamalıdır; yoksa
                    # kayıt bir tarih değil bir taslaktır.*
                    if resp.trace:
                        j.trace_json = _json_dump(list(resp.trace))
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
            # 🔴 **BAŞARISIZ İŞ DE BİR CEVAPSIZ SORUDUR — ve telemetriye girer.**
            #
            # Başarılı yol `_finish` üzerinden zaten yazıyor (`answer._log_interaction`).
            # Başarısız yol ona hiç ulaşmıyordu: iş `failed` olur, kullanıcı hata görür,
            # ve *"kaç soru cevaplanamadı"* sayacında **hiç görünmezdi**.
            #
            # ⚠ Bu, bayrak `off`'ken YOKTU: senkron yolda bir istisna da `_finish`'e
            # düşüyordu. Yani `ask_async_discovery`'yi açmak, bir ölçüm kanalını
            # **sessizce daraltıyordu** — bu turda tam olarak bu sınıftan bir kusurun
            # (`nl_corpus`'un süreç yarısı) bedeli ödendi.
            #
            # *Bir taşımayı değiştirmek, ölçümü de değiştirir; ölçüm taşımadan bağımsız
            # olmalıdır, yoksa her hızlanma bir körleşmedir.*
            try:
                from app.answer import _log_interaction
                from app.schemas import AskResponse as _AR

                _log_interaction(
                    getattr(body, "session_id", None), body,
                    _AR(question=body.question, source=None,
                        note=f"arka-plan Discovery başarısız: {str(exc)[:200]}",
                        trace=["AskJob: failed"]),
                    0, principal, request,
                    # ⚠ Gerekçe **burada biliniyor** ve başka hiçbir yerde bilinemez:
                    # kimlik thread'e kopyalanmadığı için `_teshis` şemayı okuyamaz ve
                    # `None` döner. *Gerekçesiz bir cevapsızlık kaydı, sayacı doldurur
                    # ama sorunun kendisini boş bırakır.*
                    red_gerekcesi=f"JOB_FAILED: {type(exc).__name__}")
            except Exception:                              # noqa: BLE001 — iş kaydı DÜŞMEZ
                _log.warning("başarısız iş telemetriye yazılamadı", exc_info=True)

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
