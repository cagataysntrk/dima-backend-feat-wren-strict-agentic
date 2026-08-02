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
    )


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
