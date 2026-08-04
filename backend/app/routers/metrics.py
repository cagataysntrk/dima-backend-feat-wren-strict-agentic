"""FAZ 0.18 — `GET /metrics`: metrik kaydının **okunabilir** yüzeyi.

Sahiplik **ekranı** 2.2b'de kalır; burada yalnız sözleşme var. Kaydın görünür olması
kararın kendisinden önce gelir: **görünmeyen bir çakışma düzeltilemez.**
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.auth.dependencies import require_company
from app.metrik_kaydi import SEMA_ANAHTARI, cakisan_terimler

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
    return {
        "kayit": schema.get(SEMA_ANAHTARI) or [],
        "aktif": SEMA_ANAHTARI in schema,
        "cakisan_terim_sayisi": len(cakisan),
        "cakisanlar": [{"terim": t, "adaylar": a} for t, a in cakisan.items()],
    }
