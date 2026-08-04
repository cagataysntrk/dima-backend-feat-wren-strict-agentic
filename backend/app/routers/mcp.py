"""FAZ 4.5 — **MCP ucu.** [bayrak: `mcp_yuzeyi`]

🔴 **HTTP yolu ETKİLENMEZ.** Bu router yalnız bir **çeviri yüzeyi** açar; kapalıyken
(`mcp_yuzeyi` yok) uçlar **404** döner ve `/ask` yolunda tek bir bayt değişmez (KURAL B).

🔴 **AYNI DÖRT KAPI.** Çağrı `app.mcp.cagir()` → `Planlayici.calistir()` zincirinden
geçer. Bu router'da araç **çözülmez**, **çağrılmaz**, yetki **kontrol edilmez** — üçü de
zaten kapıların işidir ve burada tekrar etmek, ikinci bir doğruluk kaynağı yaratırdı.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request

from app.auth.dependencies import require, require_company

router = APIRouter(prefix="/mcp", tags=["mcp"])


def _acik_mi(request: Request) -> Any:
    from app.config import get_settings
    from app.features import resolve_for

    p = getattr(request.state, "principal", None)
    if "mcp_yuzeyi" not in resolve_for(get_settings(), p):
        raise HTTPException(status_code=404, detail="MCP yüzeyi bu kurulumda kapalı.")
    return p


@router.get("/tools", dependencies=[Depends(require("query:run")),
                                    Depends(require_company)])
def tools_list(request: Request) -> dict:
    """MCP `tools/list`. **Kullanıcının yetkisiyle süzülür** — ajan kullanıcıyı aşamaz."""
    from app.mcp import araclar

    return {"tools": araclar(_acik_mi(request))}


@router.post("/call", dependencies=[Depends(require("query:run")),
                                    Depends(require_company)])
def tools_call(body: dict, request: Request) -> dict:
    """MCP `tools/call`. Sonuç + **makbuz** döner.

    ⚠ Makbuz opsiyonel değildir: *jenerik MCP sunucularının vermediği fark tam olarak
    budur.* Bir ajan sayıyı alıp nereden geldiğini bilmiyorsa, o sayı kanıtsızdır.
    """
    from app.company_registry import wren_for_request
    from app.mcp import cagir
    from app.planner import Butce, Planlayici

    p = _acik_mi(request)
    ad = str((body or {}).get("name") or "").strip()
    if not ad:
        raise HTTPException(status_code=400, detail="`name` zorunlu.")
    # ⚠ Bütçe VARSAYILAN bırakılır: MCP çağrısı da bir koşumdur ve sınırsız bir koşum,
    # ajanın maliyeti kullanıcıya sormadan harcaması demektir.
    plan = Planlayici(principal=p, butce=Butce(),
                      kaynaklar={"servis:wren": wren_for_request(request)})
    return cagir(plan, ad, (body or {}).get("arguments") or {})
