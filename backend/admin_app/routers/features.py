"""/sadmin/features — özellik bayrağı yönetimi (ADR-0009 DB fazı, superadmin-only).

Kural: EN SPESİFİK kazanır (user > role > tenant > sector > global); tanımsız
kapsam miras alır. Buradaki override'lar YAML fabrika ayarlarının üstüne biner.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from control_plane import audit
from control_plane.db import get_session
from control_plane.models import FeatureOverride

router = APIRouter(prefix="/sadmin/features", tags=["sadmin-features"])

_STAGES = ("off", "alpha", "beta", "prod")
_SCOPES = ("global", "sector", "tenant", "role", "user")


class OverrideSet(BaseModel):
    scope_type: str = Field(pattern="^(global|sector|tenant|role|user)$")
    scope_id: str | None = None  # global'de None/boş
    stage: str = Field(pattern="^(off|alpha|beta|prod)$")


def _known_features() -> dict[str, str]:
    """Fabrika ayarları (global ⊕ pack ⊕ company YAML) — bilinen bayrak keşfi."""
    try:
        from app.config import get_settings
        from app.features import factory_defaults

        return factory_defaults(get_settings())
    except Exception:
        return {}


def _registry() -> dict[str, dict[str, str]]:
    """Kanonik bayrak kaydı (etiket/açıklama/kategori) — okunabilir panel için."""
    try:
        from app.features import FLAG_REGISTRY

        return FLAG_REGISTRY
    except Exception:
        return {}


@router.get("")
def list_features(session: Session = Depends(get_session)) -> dict:
    overrides = session.exec(select(FeatureOverride)).all()
    factory = _known_features()
    reg = _registry()
    # Keşif: kanonik kayıt ⊕ YAML ⊕ DB'de override edilmiş anahtarlar.
    keys = sorted(set(reg) | set(factory) | {o.feature_key for o in overrides})
    return {
        "features": [
            {
                "key": k,
                # Registry metadata'sı — kayıtta yoksa anahtar etiket olur (okunur kalır).
                "label": (reg.get(k) or {}).get("label", k),
                "description": (reg.get(k) or {}).get("description", ""),
                "category": (reg.get(k) or {}).get("category", "Diğer"),
                "factory_stage": factory.get(k),  # YAML varsayılanı (None = yalnız DB)
                "overrides": [
                    {
                        "id": str(o.id),
                        "scope_type": o.scope_type,
                        "scope_id": o.scope_id,
                        "stage": o.stage,
                        "updated_at": o.updated_at.isoformat(timespec="seconds"),
                    }
                    for o in overrides
                    if o.feature_key == k
                ],
            }
            for k in keys
        ]
    }


@router.put("/{key}")
def set_override(key: str, body: OverrideSet, request: Request,
                 session: Session = Depends(get_session)) -> dict:
    scope_id = (body.scope_id or "").strip() or None
    if body.scope_type == "global":
        scope_id = None
    elif not scope_id:
        raise HTTPException(status_code=400, detail="Bu kapsam için scope_id gerekli")
    # Sektör kapsamı pack registry'sine karşı doğrulanır (typo → sessiz-etkisiz
    # override yerine açık 400). Kaynak: demo/packs (panel dropdown'ı da oradan).
    if body.scope_type == "sector":
        try:
            from app.config import get_settings
            from app.packs import list_packs

            known = {p["key"] for p in
                     list_packs(get_settings().resolved_project_dir().parent)["sektorler"]}
        except Exception:
            known = set()
        if known and scope_id not in known:
            raise HTTPException(status_code=400,
                                detail=f"Bilinmeyen sektör paketi: {scope_id}")

    row = session.exec(select(FeatureOverride).where(
        FeatureOverride.feature_key == key,
        FeatureOverride.scope_type == body.scope_type,
        FeatureOverride.scope_id == scope_id,
    )).first()
    principal = getattr(request.state, "principal", None)
    actor = uuid.UUID(principal.user_id) if principal else None
    if row:
        row.stage = body.stage
        row.updated_by = actor
        row.updated_at = datetime.utcnow()
    else:
        row = FeatureOverride(feature_key=key, scope_type=body.scope_type,
                              scope_id=scope_id, stage=body.stage, updated_by=actor)
    session.add(row)
    session.commit()
    session.refresh(row)
    audit.record(principal, "feature_set",
                 nl_question=f"{key} @ {body.scope_type}:{scope_id or '*'} → {body.stage}",
                 ip=request.client.host if request.client else None)
    return {"id": str(row.id), "key": key, "scope_type": row.scope_type,
            "scope_id": row.scope_id, "stage": row.stage}


@router.delete("/{key}/overrides/{oid}")
def delete_override(key: str, oid: str, request: Request,
                    session: Session = Depends(get_session)) -> dict:
    try:
        row = session.get(FeatureOverride, uuid.UUID(oid))
    except ValueError:
        raise HTTPException(status_code=400, detail="Geçersiz override id")
    if row is None or row.feature_key != key:
        raise HTTPException(status_code=404, detail="Override bulunamadı")
    session.delete(row)
    session.commit()
    audit.record(getattr(request.state, "principal", None), "feature_set",
                 nl_question=f"{key} @ {row.scope_type}:{row.scope_id or '*'} → (miras)",
                 ip=request.client.host if request.client else None)
    return {"removed": True}
