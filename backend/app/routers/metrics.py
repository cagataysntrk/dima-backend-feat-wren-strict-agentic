"""FAZ 0.18 — `GET /metrics`: metrik kaydının **okunabilir** yüzeyi.

Sahiplik **ekranı** 2.2b'de kalır; burada yalnız sözleşme var. Kaydın görünür olması
kararın kendisinden önce gelir: **görünmeyen bir çakışma düzeltilemez.**
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request

from pydantic import BaseModel

from app.auth.dependencies import require, require_company
from app.metrik_kaydi import (
    SEMA_ANAHTARI, cakisan_terimler, sahiplikle_birlestir, taslak_uret,
)

router = APIRouter(tags=["metrics"])


@router.get("/metrics", dependencies=[Depends(require_company)])
def metrikler(request: Request) -> dict:
    """Metrik kaydı + **çakışan terim envanteri**.

    `kayit` bayrak kapalıyken **boş** döner (şemaya hiç yazılmaz) — ama `cakisanlar`
    HER ZAMAN hesaplanır: çakışmanın kendisi bir **olgudur**, bayrağa bağlı değildir.
    Bayrak yalnız *"hakem karar versin mi"*yi belirler, *"çakışma var mı"*yı değil.
    """
    from app.company_registry import wren_for_request

    schema = wren_for_request(request).schema()
    cakisan = cakisan_terimler(schema)
    # 🔴 FAZ 2.2b — kayıt artık KALICI sahiplik kararlarıyla birleşiyor. Bayrak kapalıyken
    # şemada `metrik_kaydi` anahtarı yoktur; ekran yine de taslağı görebilmeli, yoksa
    # kullanıcı **kararı veremeden** kararın sonucunu görmek zorunda kalırdı.
    kayit = list(schema.get(SEMA_ANAHTARI) or taslak_uret(schema))
    return {
        "kayit": sahiplikle_birlestir(kayit, _sahiplik_oku(request)),
        "aktif": SEMA_ANAHTARI in schema,
        "cakisan_terim_sayisi": len(cakisan),
        "cakisanlar": [{"terim": t, "adaylar": a} for t, a in cakisan.items()],
    }


class SahiplikGirdisi(BaseModel):
    """`sahip_cube=None` → sahiplik **kaldırılır** (kayıt silinmez)."""

    sahip_cube: str | None = None


@router.patch("/metrics/{terim}", dependencies=[Depends(require("metric:certify")),
                                                Depends(require_company)])
def sahiplik_ata(terim: str, body: SahiplikGirdisi, request: Request) -> dict:
    """Çakışan bir terimin **sahibini** belirler — hakemin tek besleme yolu.

    ⚠ Yetki `metric:certify`: bir terimin sahibini seçmek, o metriğin **tanımını**
    onaylamakla aynı sınıf bir karardır (`1.5`'in sertifika yetkisiyle aynı gerekçe).
    Ayrı bir izin adı uydurmak, yetki matrisini kararın kendisinden **koparırdı**.

    🔴 Karar **audit'e** yazılır: uygulanmayan bir karar bile görünür olmalıydı (`1.10`),
    uygulanan bir karar **evleviyetle**.
    """
    from control_plane import audit
    from control_plane.db import get_session
    from control_plane.models import MetrikSahipligi
    from sqlmodel import select

    p = getattr(request.state, "principal", None)
    tenant = getattr(p, "tenant_id", None)
    if not tenant:
        raise HTTPException(status_code=400, detail="Şirket bağlamı yok.")
    with next(get_session()) as oturum:
        satir = oturum.exec(select(MetrikSahipligi).where(
            MetrikSahipligi.tenant_id == tenant,
            MetrikSahipligi.terim == terim)).first()
        if satir is None:
            satir = MetrikSahipligi(tenant_id=tenant, terim=terim)
        satir.sahip_cube = body.sahip_cube
        satir.karar_veren_user_id = getattr(p, "user_id", None)
        satir.guncellendi = datetime.now(timezone.utc)
        oturum.add(satir)
        oturum.commit()
    audit.record(p, "metrik_sahipligi",
                 generated_sql=f"{terim} → {body.sahip_cube or '(kaldırıldı)'}")
    return {"terim": terim, "sahip_cube": body.sahip_cube}


def _sahiplik_oku(request: Request) -> dict[str, str | None]:
    """`{terim: sahip_cube}` — DB yoksa **boş** (bugünkü davranış birebir).

    ⚠ Ulaşılamayan bir karar deposunu *"karar yok"* saymak burada **doğru** olandır:
    `katman_b.allowlist`'in tersi bir durum — orada yokluk bir güvenlik kararıydı,
    burada yalnız bir **yönlendirme tercihidir** ve yokluğu bugünkü yolu bırakır.
    """
    try:
        from control_plane.db import get_session
        from control_plane.models import MetrikSahipligi
        from sqlmodel import select

        p = getattr(request.state, "principal", None)
        tenant = getattr(p, "tenant_id", None)
        if not tenant:
            return {}
        with next(get_session()) as oturum:
            return {r.terim: r.sahip_cube for r in oturum.exec(
                select(MetrikSahipligi).where(MetrikSahipligi.tenant_id == tenant))}
    except Exception:                                        # noqa: BLE001
        return {}
