"""FAZ 5.2 — **paylaşım ucu.** [bayrak: `tur_paylas`]

## 🔴 İLK TASARIMIM YANLIŞTI — ve iki yerden yanlıştı

İlk yazımda bu uç *"kimliksiz açılır"* diyordu. İkisi de kusurdu:

1. **Depo değişmezi:** *"Auth HER ZAMAN zorunlu — kapatma bayrağı YOKTUR."* Kimliksiz bir
   uç açmak, bir maddeyi teslim etmek için mimarinin değişmezini delmekti.
2. **Çapraz-tenant sızıntısı:** A tenant'ı için imzalanmış bir token'ı B tenant'ından biri
   açabilirdi. İmza **token'ın gerçekliğini** kanıtlar, **okuyanın hakkını** değil.

**Düzeltilmiş şekil: kurum-içi paylaşım.** Link giriş yapmış bir kullanıcı tarafından
açılır ve **token'daki tenant, okuyanın tenant'ıyla eşleşmek zorundadır**.
*"Müdüre 3 cümle"* zaten kurum içi bir cümledir — kimliksizlik hiç gerekmiyordu.

## Dört değişmez

| değişmez | olmasaydı |
|---|---|
| **İmzalı** (HMAC) | token uydurulur |
| **Süreli** (7 gün, azami 30) | sızan link **süresiz** bir veri kapısı olur |
| **Maskeli** (`pii.py`) | paylaşılan yük ham PII taşır |
| **Tenant-eşleşmeli** | başka bir şirketin raporu okunur |

⚠ Yük **çalıştırılabilir bir sorgu taşımaz** (`cube_query`/`sql` yok): paylaşılan şey bir
**rapor görüntüsüdür**. *Bir paylaşım linki bir oturum değildir.*
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from app.auth.dependencies import require, require_company

router = APIRouter(tags=["paylasim"])


def _acik_mi(request: Request):
    from app.config import get_settings
    from app.features import resolve_for

    p = getattr(request.state, "principal", None)
    if "tur_paylas" not in resolve_for(get_settings(), p):
        raise HTTPException(status_code=404, detail="Paylaşım bu kurulumda kapalı.")
    return p


def _tenant(principal) -> str:
    """Okuyanın tenant'ı — **token'dan**, gövdeden değil (ADR-0014)."""
    for alan in ("tenant_slug", "tsl", "tenant"):
        v = getattr(principal, alan, None) or (
            principal.get(alan) if isinstance(principal, dict) else None)
        if v:
            return str(v)
    raise HTTPException(status_code=403, detail="Tenant kimliği çözülemedi.")


@router.post("/share", dependencies=[Depends(require("query:run")),
                                     Depends(require_company)])
def share_create(body: dict, request: Request) -> dict:
    """Bir cevabı paylaşılabilir hâle getirir. Yük **maskelenir**, token **imzalanır**.

    ⚠ İstemcinin gönderdiği yük güvenilmez kabul edilir ama zarar üretmez: yük zaten
    **kullanıcının kendi gördüğü** cevaptır ve maskeleme **sunucuda** yapılır.
    """
    from app.paylasim import AZAMI_TTL, VARSAYILAN_TTL, PaylasimHatasi, paylasim_yuku, uret

    p = _acik_mi(request)
    try:
        ttl = int((body or {}).get("ttl") or 0) or None
        yuk = paylasim_yuku((body or {}).get("cevap") or {})
        # 🔴 TENANT DAMGASI — okuma tarafındaki eşleşme kapısının dayanağı.
        yuk["tenant"] = _tenant(p)
        token = uret(yuk, ttl=ttl)
    except PaylasimHatasi as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"share_url": f"/share/{token}",
            "ttl": min(ttl or VARSAYILAN_TTL, AZAMI_TTL)}


@router.get("/share/{token}", dependencies=[Depends(require("query:run"))])
def share_read(token: str, request: Request) -> dict:
    """Paylaşılan raporu okur — **kurum içi**.

    Fail-closed ve **404**: imza bozuksa, süre dolmuşsa **ya da tenant eşleşmiyorsa**
    aynı cevap döner. *403 vermek, o token'ın VAR OLDUĞUNU söylerdi* — ve bir token'ın
    varlığını sızdırmak, tahmini kolaylaştırır.
    """
    from app.paylasim import PaylasimHatasi, coz

    p = _acik_mi(request)
    try:
        yuk = coz(token)
    except PaylasimHatasi as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if str(yuk.get("tenant") or "") != _tenant(p):
        # 🔴 ÇAPRAZ-TENANT KAPISI. İmza token'ın GERÇEKLİĞİNİ kanıtlar, okuyanın
        # HAKKINI değil — ikisini karıştırmak bu maddenin en pahalı hatası olurdu.
        raise HTTPException(status_code=404, detail="Paylaşım linki bulunamadı.")
    yuk.pop("exp", None)
    yuk.pop("tenant", None)
    return yuk
