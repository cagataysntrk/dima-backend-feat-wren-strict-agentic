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

#: 🔴🔴 `§38.3 D13` — **BU UCUN SAĞLAYABİLDİĞİ KAYNAKLAR** (⟳ 2026-08-12).
#: Tek yerde yazılı: `tools/list` bunu **süzgeç**, `tools/call` sözlüğün
#: **anahtarı** olarak kullanır. Ayrışırlarsa ilan edilen bir araç çağrılamaz
#: hâle gelir — ölçüldü: üç `llm.*` aracı listede görünüyor ama
#: `baglanma="servis:llm"` olduğu için çağrıda `ValueError` ile düşüyordu.
#: ⊘ `servis:llm` **bilerek yok**: dış bir çağıranın LLM bütçesi harcaması ayrı
#: bir **yönetişim** kararıdır ve ilan edilmeden verilemez. Verildiği gün bu
#: kümeye bir ad eklenir; başka hiçbir satır değişmez.
_KAYNAK_ADLARI = {"servis:wren"}


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

    # 🔴 `§38.3 D13` — liste, bu ucun **gerçekten sağladığı** kaynaklardan türetilir.
    return {"tools": araclar(_acik_mi(request), kaynaklar=_KAYNAK_ADLARI)}


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
    # ⚠ İki yüzeyin **aynı** kümeden beslendiğini burada da doğrula: bir gün biri
    # değişip öteki kalırsa, yayımlanan sözleşme sessizce yalan söylemeye başlar.
    assert set(plan.kaynaklar) == _KAYNAK_ADLARI, (
        "🔴 `tools/list` ile `tools/call` farklı kaynak kümesi kuruyor — "
        "yayımlanan sözleşme çağrılabilirlikle ayrıştı.")
    return cagir(plan, ad, (body or {}).get("arguments") or {})
