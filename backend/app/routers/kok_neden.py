"""🌳 **KÖK-NEDEN HARİTASI UCU** — `POST /ask/kok-neden`.

## Neden `ask.py`de değil, ayrı bir router

`ask.py` bir **büyüme kapısı** taşıyor (`test_modul_buyume.py`) ve bu uç eklendiğinde
kapı kırmızı verdi: 2395 → 2425. Kapının kendi talimatı açık — *"artıyorsa gerçekten
YENİ kod eklenmiş demektir → ayrı bir modüle çıkar."*

⚠ Ve doğru olan buydu: bu **yeni bir yetenektir**, `ask()` akışının bir parçası değil.
`ask.py`nin şişmesi bir ölçü değil bir **belirtidir**; tavanı yükseltmek belirtiyi
susturur, kaynağı değil. *Bir kapıyı susturmak, onun ölçtüğü şeyi düzeltmez.*

Gövde zaten `app/kok_neden.py`de (HTTP bilmez, `tools.KAYIT`'a girer, arka plan işleri
de çağırabilir). Bu dosya yalnız üç HTTP kaygısını çözer: **servis çözümü** · **makbuz
yazıcısı** · **gizlilik mührü**.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.auth.dependencies import require, require_company
from app.logging_setup import get_logger
from app.routers.ask import _drill_record_contract, _service_for
from app.schemas import KokNedenDugum, KokNedenRequest, KokNedenResponse

_log = get_logger("kok_neden")

router = APIRouter(tags=["ask"])


@router.post("/ask/kok-neden", response_model=KokNedenResponse,
             dependencies=[Depends(require("query:run")), Depends(require_company)])
def ask_kok_neden(request: Request, body: KokNedenRequest) -> KokNedenResponse:
    """🌳 Kök-neden haritasının ilk katı: **hangi yola bakmaya değer.**

    Kullanıcının ölçülmüş şikâyeti: *"çok karışık, kullanıcılar kolay kolay anlamıyor
    çözemiyor."* Eksik olan veri değil **önceliktir** — ve bakılmayanın **görünmesidir**.

    FAZ 9.1 GİZLİLİK MÜHRÜ (bkz. `ask_drill`): `gerekce` metni bir segment DEĞERİ
    taşıyabilir (`musteri`/`operator` kırılımında doğrudan kişi adı). Mühür bu yüzden
    burada da uygulanır — *bir metin alanı, sayı taşımıyor diye masum değildir.*
    """
    from app import kok_neden as _kn

    cq = dict(body.cube_query or {})
    service = _service_for(request, body.session_id)
    out = _kn.harita(
        service, service.schema(), cq, mode=body.mode,
        max_dimensions=body.max_dimensions,
        kaydet=lambda baslik, acq, sql, res: _drill_record_contract(
            request, service, body.session_id, baslik, acq, sql, res))
    resp = KokNedenResponse(
        cube=out.get("cube"), olcu=out.get("olcu"), mode=out.get("mode") or body.mode,
        note=out.get("note"), taranmayan_adlar=out.get("taranmayan_adlar") or [],
        dugumler=[KokNedenDugum(**d) for d in (out.get("dugumler") or [])])
    try:
        from app.pii import muhurle

        muhurle(resp, request, getattr(request.state, "principal", None),
                ad=f"kok-neden:{cq.get('cube') or '-'}")
    except Exception:  # noqa: BLE001
        _log.warning("kök-neden gizlilik mührü uygulanamadı", exc_info=True)
    return resp
