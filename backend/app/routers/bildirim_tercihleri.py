"""FAZ 5.9b — **bildirim tercihleri ucu.** [bayraksız: yetim tablo kapanışı]

## Ölçülen kusur

`NotificationPreference` **yetim bir tabloydu**: 0 satır, **router yok**. Yani kullanıcı
bir kategoriyi kapatabileceğini sanıyordu ama onu **yazacağı hiçbir yüzey yoktu** —
ve hiçbir kod ona bakmıyordu (o yarısı FAZ 5.9a'da kapandı).

> 🔴 *Beyan edilmiş ama yazılamayan bir tercih, verilmemiş bir sözden kötüdür.*

## Üç kural

1. **Tercih SELF'tir.** Bir kullanıcı **yalnız kendi** tercihini yazar; başkasının
   bildirimlerini kapatmak bir yönetim işlemidir ve bu ucun işi değildir.
2. **Silme SOFT** (ADR-0019) — bir tercihi silmek onu *"hiç verilmemiş"* yapar
   (varsayılan **açık**), *"kapalı"* değil. İkisi farklı şeylerdir.
3. **Kayıt yoksa AÇIK.** Opt-out bir **karardır**; kaydın yokluğu bir karar değildir.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, col, select

from app.auth.dependencies import require, require_company
from control_plane.db import engine
from control_plane.models import NotificationPreference

router = APIRouter(prefix="/bildirim-tercihleri", tags=["bildirim"])

#: Bilinen kategoriler. ⚠ **Kapalı liste**: bilinmeyen bir kategori yazmak, hiçbir
#: gönderici tarafından okunmayacak bir tercih üretirdi — kullanıcı onu kapattığını
#: sanır ve bildirim gelmeye devam eder.
KATEGORILER = ("report", "alert", "anomaly", "system")

#: Bilinen kanallar — `app/channels.py`'nin kayıtlı kanallarıyla **aynı** küme olmalı.
KANALLAR = ("inapp", "email", "push", "slack")


def _principal(request: Request):
    p = getattr(request.state, "principal", None)
    if p is None:
        raise HTTPException(status_code=401, detail="Kimlik gerekli")
    return p


def _kimlik(p) -> tuple[str, str | None]:
    uid = str(getattr(p, "user_id", "") or "")
    if not uid:
        raise HTTPException(status_code=403, detail="Kullanıcı kimliği çözülemedi.")
    return uid, str(getattr(p, "tenant_id", "") or "") or None


@router.get("", dependencies=[Depends(require("query:run")), Depends(require_company)])
def listele(request: Request) -> dict:
    """Kullanıcının **kendi** tercihleri.

    ⚠ Yanıt **eksikleri de anlatır**: kayıt olmayan (kategori × kanal) çiftleri
    `varsayilan: true` ile döner. *Bir listede görünmeyen ayar, kullanıcının olmadığını
    sandığı ayardır.*
    """
    uid, tid = _kimlik(_principal(request))
    with Session(engine) as s:
        satirlar = list(s.exec(
            select(NotificationPreference)
            .where(NotificationPreference.user_id == uid)
            .where(col(NotificationPreference.deleted_at).is_(None))))
    kayitli = {(r.category, r.channel): r for r in satirlar}
    out = []
    for kat in KATEGORILER:
        for kan in KANALLAR:
            r = kayitli.get((kat, kan))
            out.append({
                "category": kat, "channel": kan,
                "enabled": bool(r.enabled) if r else True,
                "address": r.address if r else None,
                # 🔴 "Hiç ayarlanmadı" ile "açık bırakıldı" AYRI görünür.
                "varsayilan": r is None,
            })
    del tid
    return {"tercihler": out}


@router.put("", dependencies=[Depends(require("query:run")), Depends(require_company)])
def yaz(body: dict, request: Request) -> dict:
    """Tek bir (kategori × kanal) tercihini yazar. **SELF** — başkası adına yazılamaz.

    🔴 Bilinmeyen kategori/kanal **reddedilir**: hiçbir gönderici tarafından okunmayacak
    bir tercih, kullanıcının kapattığını sandığı ama gelmeye devam eden bir bildirim
    demektir.
    """
    uid, tid = _kimlik(_principal(request))
    kat = str((body or {}).get("category") or "")
    kan = str((body or {}).get("channel") or "")
    if kat not in KATEGORILER:
        raise HTTPException(status_code=400,
                            detail=f"Bilinmeyen kategori: {kat!r}. "
                                   f"Geçerli: {', '.join(KATEGORILER)}")
    if kan not in KANALLAR:
        raise HTTPException(status_code=400,
                            detail=f"Bilinmeyen kanal: {kan!r}. "
                                   f"Geçerli: {', '.join(KANALLAR)}")
    acik = bool((body or {}).get("enabled", True))
    adres = (body or {}).get("address") or None
    simdi = datetime.now(timezone.utc).replace(tzinfo=None)
    with Session(engine) as s:
        mevcut = s.exec(
            select(NotificationPreference)
            .where(NotificationPreference.user_id == uid)
            .where(NotificationPreference.category == kat)
            .where(NotificationPreference.channel == kan)
            .where(col(NotificationPreference.deleted_at).is_(None))).first()
        if mevcut:
            mevcut.enabled, mevcut.address, mevcut.updated_at = acik, adres, simdi
            s.add(mevcut)
        else:
            s.add(NotificationPreference(user_id=uid, tenant_id=tid, category=kat,
                                         channel=kan, enabled=acik, address=adres))
        s.commit()
    return {"category": kat, "channel": kan, "enabled": acik, "address": adres}


@router.delete("/{kategori}/{kanal}",
               dependencies=[Depends(require("query:run")), Depends(require_company)])
def sil(kategori: str, kanal: str, request: Request) -> dict:
    """Tercihi **soft-delete** eder (ADR-0019).

    🔴 Silmek, tercihi *"hiç verilmemiş"* yapar → **varsayılan AÇIK**. *"Kapalı"* demek
    istiyorsa kullanıcı `enabled: false` yazar. İkisi farklı şeylerdir ve silmeyi
    kapatma sanmak, kullanıcıyı **sessize alır**.
    """
    uid, _ = _kimlik(_principal(request))
    with Session(engine) as s:
        r = s.exec(
            select(NotificationPreference)
            .where(NotificationPreference.user_id == uid)
            .where(NotificationPreference.category == kategori)
            .where(NotificationPreference.channel == kanal)
            .where(col(NotificationPreference.deleted_at).is_(None))).first()
        if r is None:
            raise HTTPException(status_code=404, detail="Tercih bulunamadı")
        r.deleted_at = datetime.now(timezone.utc).replace(tzinfo=None)
        s.add(r)
        s.commit()
    return {"silindi": True, "category": kategori, "channel": kanal,
            "not": "Tercih kaldırıldı — bu kategori artık VARSAYILAN (açık) davranır."}
