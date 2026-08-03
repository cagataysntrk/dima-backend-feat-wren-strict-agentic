"""KALICI SUNUM TERCİHLERİ — okuma / silme ucu (FAZ E).

YAZMA burada bir HTTP ucu DEĞİLDİR: tercih yazmak `POST /ask/eylem` onay kademesinden
geçer (Faz H). Bu dosyadaki `tercih_yaz`, o ucun çağırdığı **gövdedir** — `dashboards.
add_widget` / `schedules.create_schedule` ile aynı rol.

Neden ayrı bir okuma/silme ucu: bir tercih **görünmez ve kaldırılamazsa** bir hafızadan
çok bir hataya benzer. Kullanıcı ne sakladığımızı görebilmeli ve tek tıkla silebilmeli;
cevapların içindeki *"tercihiniz uygulandı"* notu da buraya işaret eder.
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, col, select

from app import tercih as _tercih
from control_plane.db import get_session
from control_plane.models import SunumTercihi

router = APIRouter(tags=["tercihler"])


def _principal(request: Request):
    p = getattr(request.state, "principal", None)
    if p is None:
        raise HTTPException(status_code=401, detail="Kimlik gerekli")
    return p


def oku(session: Session, principal) -> dict[str, str]:
    """Kullanıcının aktif tercihleri: {anahtar: deger}. Hata durumunda BOŞ döner —
    tercih bir kolaylıktır, cevabın önkoşulu değil (depo düşerse rapor yine gelmeli)."""
    try:
        satirlar = session.exec(
            select(SunumTercihi)
            .where(SunumTercihi.user_id == principal.user_id)
            .where(col(SunumTercihi.deleted_at).is_(None))
        ).all()
    except Exception:
        return {}
    return {s.anahtar: s.deger for s in satirlar}


def tercih_yaz(request: Request, session: Session, anahtar: str, deger: str,
               kaynak_ifade: str | None = None) -> dict:
    """Tercihi yazar (upsert). `POST /ask/eylem` onayından çağrılır — doğrudan HTTP ucu
    DEĞİL, çünkü onaysız yazma bu depoda yasaktır (Faz H değişmezi)."""
    if anahtar not in _tercih.ANAHTARLAR:
        raise HTTPException(status_code=400,
                            detail=f"Bilinmeyen tercih anahtarı: {anahtar!r}")
    if not str(deger or "").strip():
        raise HTTPException(status_code=400, detail="Tercih değeri boş olamaz.")
    principal = _principal(request)
    mevcut = session.exec(
        select(SunumTercihi)
        .where(SunumTercihi.user_id == principal.user_id)
        .where(SunumTercihi.anahtar == anahtar)
        .where(col(SunumTercihi.deleted_at).is_(None))
    ).first()
    if mevcut is not None:
        mevcut.deger = deger
        mevcut.kaynak_ifade = kaynak_ifade
        mevcut.updated_at = datetime.utcnow()
        satir = mevcut
    else:
        satir = SunumTercihi(user_id=principal.user_id, tenant_id=principal.tenant_id,
                             anahtar=anahtar, deger=deger, kaynak_ifade=kaynak_ifade)
    session.add(satir)
    session.commit()
    session.refresh(satir)
    return {"id": str(satir.id), "anahtar": anahtar, "deger": deger}


@router.get("/tercihler")
def listele(request: Request, session: Session = Depends(get_session)) -> dict:
    principal = _principal(request)
    satirlar = session.exec(
        select(SunumTercihi)
        .where(SunumTercihi.user_id == principal.user_id)
        .where(col(SunumTercihi.deleted_at).is_(None))
        .order_by(col(SunumTercihi.anahtar))
    ).all()
    return {"tercihler": [
        {"anahtar": s.anahtar, "deger": s.deger,
         "etiket": _tercih.etiketle(s.anahtar, s.deger),
         "kaynak_ifade": s.kaynak_ifade,
         "updated_at": s.updated_at.isoformat() if s.updated_at else None}
        for s in satirlar]}


@router.delete("/tercihler/{anahtar}")
def sil(request: Request, anahtar: str, session: Session = Depends(get_session)) -> dict:
    """Soft-delete (ADR-0019). Olmayan tercihi silmek 200 döner — silme İDEMPOTENTTİR;
    404, kullanıcının zaten istediği son duruma ulaşmışken hata görmesi olurdu."""
    principal = _principal(request)
    satir = session.exec(
        select(SunumTercihi)
        .where(SunumTercihi.user_id == principal.user_id)
        .where(SunumTercihi.anahtar == anahtar)
        .where(col(SunumTercihi.deleted_at).is_(None))
    ).first()
    if satir is not None:
        satir.deleted_at = datetime.utcnow()
        session.add(satir)
        session.commit()
    return {"ok": True, "anahtar": anahtar}
