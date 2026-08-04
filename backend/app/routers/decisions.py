"""Karar Kaydı uçları (Faz E-4) — yaz + **DOĞRULA**.

İki uç, ikisinin de frontend tüketicisi var (MIMARI §14.1):

- `POST /decisions` → `PrescriptionLayer`'daki *"kararı kaydet"*
- `GET /decisions/{id}` → aynı yerdeki *"doğrula"* — makbuzun değeri onu
  **kontrol edebilmekte**; kaydedip bir daha bakmadığın bir kayıt bir tutanak değil
  bir temennidir.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlmodel import Session, select

from app import decision
from app.auth.dependencies import require, require_company
from control_plane.db import engine
from control_plane.models import DecisionRecord

router = APIRouter(tags=["decisions"])


class DecisionIn(BaseModel):
    """`chosen` seçilen seçenek, `options` DEĞERLENDİRİLENLERİN tamamı.

    İkincisi zorunlu değil ama **şiddetle beklenir**: *"neden bu?"* sorusu ancak
    *"hangilerine karşı?"* bilinirse cevaplanabilir.
    """

    question: str | None = None
    chosen: dict | None = None
    options: list | None = None
    rationale: str | None = None
    note: str | None = None
    contract_ids: list[str] | None = None
    session_id: str | None = None
    supersedes: str | None = None
    #: 🔴 FAZ 5.8 — **ŞABLON**: `{"cube_query": {...}, "parametreler": [...]}`.
    #: `contract_ids` *"o gün hangi sayıya baktık"* der; şablon *"aynı analizi bugün
    #: koşsak ne çıkar"* der. Biri ötekinin yerine geçmez.
    sablon: dict | None = None


def _principal(request: Request):
    return getattr(request.state, "principal", None)


@router.post("/decisions",
             dependencies=[Depends(require("decision:write")), Depends(require_company)])
def create_decision(request: Request, body: DecisionIn) -> dict:
    """Kararı yazar. **Fail-loud:** yazılamazsa hata döner — kullanıcı kaydettiğini
    sanıp kaydedilmemiş olması en kötü sonuçtur."""
    p = _principal(request)
    return decision.kaydet(
        question=body.question, chosen=body.chosen, options=body.options,
        rationale=body.rationale, note=body.note, contract_ids=body.contract_ids,
        tenant_id=str(getattr(p, "tenant_id", "") or "") or None,
        user_id=str(getattr(p, "user_id", "") or "") or None,
        session_id=body.session_id, supersedes=body.supersedes,
        sablon=body.sablon,
    )


@router.post("/decisions/{did}/kos",
             dependencies=[Depends(require("decision:read")), Depends(require_company)])
def kos_sablon(request: Request, did: str, body: dict | None = None) -> dict:
    """FAZ 5.8 — **ŞABLONU YENİDEN KOŞ.** *"Aynı analizi bugün koşsak ne çıkar?"*

    🔴 **0 LLM.** Şablon `cube_query` taşır ve o sorgu `/cube` yolunun aynısından geçer —
    yeni bir SQL **üretilmez**. ⚠ `sql` **hiç taşınmaz**: donmuş bir SQL, şema değişince
    **sessizce yanlış** çalışır; `cube_query` ise güncel MDL'de derlenir ve uyuşmazlık
    **patlar**.

    ## ⚠ Parametre ezmesi DAR TUTULUR

    Yalnız şablonun **kendi beyan ettiği** parametreler ezilebilir (`parametreler`
    listesi). Serbest ezme, kaydedilmiş bir kararı **başka bir analize** çevirip yine
    o kararın kimliğiyle sunmak olurdu — *bir şablon, bir imzanın altını doldurmaz.*
    """
    import json as _json

    p = _principal(request)
    with Session(engine) as s:
        kayit = s.exec(select(DecisionRecord).where(DecisionRecord.id == did)).first()
    if kayit is None:
        raise HTTPException(status_code=404, detail="Karar kaydı bulunamadı")
    benim = str(getattr(p, "tenant_id", "") or "") or None
    if not getattr(p, "is_superadmin", False) and kayit.tenant_id != benim:
        raise HTTPException(status_code=404, detail="Karar kaydı bulunamadı")
    try:
        sablon = _json.loads(kayit.sablon_json or "null")
    except Exception:                                        # noqa: BLE001
        sablon = None
    if not (sablon or {}).get("cube_query"):
        # ⚠ 404 değil **409**: kayıt VAR ama şablonsuz. Bunu "bulunamadı" demek,
        # kullanıcıya yanlış bir teşhis verirdi.
        raise HTTPException(status_code=409,
                            detail="Bu karar bir şablon taşımıyor — yeniden koşulamaz.")
    cq = dict(sablon["cube_query"])
    izinli = set(sablon.get("parametreler") or ())
    for k, v in (body or {}).items():
        if k in izinli:
            cq[k] = v
    return {"karar_id": did, "cube_query": cq, "parametreler": sorted(izinli)}


@router.get("/decisions/{did}",
            dependencies=[Depends(require("decision:read")), Depends(require_company)])
def get_decision(request: Request, did: str) -> dict:
    """Kaydı okur ve **hash'ini yeniden hesaplar**: `verified` alanı kurcalamayı söyler.

    Tenant-RLS: başka tenant'ın kaydı **bulunamadı** döner (var olduğu bile sızmaz).
    """
    p = _principal(request)
    with Session(engine) as s:
        kayit = s.exec(select(DecisionRecord).where(DecisionRecord.id == did)).first()
    if kayit is None:
        raise HTTPException(status_code=404, detail="Karar kaydı bulunamadı")
    benim = str(getattr(p, "tenant_id", "") or "") or None
    if not getattr(p, "is_superadmin", False) and kayit.tenant_id != benim:
        # 403 DEĞİL 404: "yetkin yok" cevabı, kaydın VAR OLDUĞUNU sızdırır.
        raise HTTPException(status_code=404, detail="Karar kaydı bulunamadı")
    return decision.oku_satir(kayit)
