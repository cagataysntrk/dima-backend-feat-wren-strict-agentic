"""/sadmin/packs — sektör/modül pack keşfi (superadmin-only).

Panel, tenant açarken bu listeden SEÇER; "bu sektörü seçersen şu cube'lar gelir"
önizlemesi cube listelerinden gelir. Eşleşmenin kaynağı pack dosyalarıdır (ADR-0005).
"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/sadmin/packs", tags=["sadmin-packs"])


@router.get("")
def list_packs() -> dict:
    from app.config import get_settings
    from app.packs import list_packs as _list

    return _list(get_settings().resolved_project_dir().parent)
