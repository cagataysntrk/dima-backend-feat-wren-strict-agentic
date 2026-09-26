"""Immutable Core-B product-routing correlation store.

This store persists accepted orchestration intent only. It owns no analytical,
Evidence, Claim, P17, P18, P19, P20, or decision truth.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from sqlmodel import Session, select

from app.v3.product.contracts import (
    ProductInvestigationRequirement,
    ProductInvestigationRequirementKind,
)
from control_plane.db import engine as control_plane_engine
from control_plane.models import ProductInvestigationRequirementRecord


class ProductRoutingError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def _canonical(value) -> tuple[str, str]:
    raw = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
        default=str,
    )
    return raw, hashlib.sha256(raw.encode("utf-8")).hexdigest()


class ProductInvestigationRequirementStore:
    def __init__(self, db_engine=None) -> None:
        self._engine = db_engine or control_plane_engine

    def persist(
        self,
        *,
        tenant_binding: str,
        research_session_id: str,
        brief_id: str,
        requirements: tuple[ProductInvestigationRequirement, ...],
        accepted_goal_ids: tuple[str, ...],
        now: datetime | None = None,
    ) -> tuple[ProductInvestigationRequirement, ...]:
        accepted = set(accepted_goal_ids)
        stamp = now or datetime.now(timezone.utc)
        if stamp.tzinfo is None or stamp.utcoffset() is None:
            raise ProductRoutingError(
                "PRODUCT_ROUTING_TIMEZONE_REQUIRED",
                "routing timestamp must be timezone-aware",
            )
        seen: set[str] = set()
        for item in requirements:
            if item.requirement_id in seen:
                raise ProductRoutingError(
                    "PRODUCT_ROUTING_DUPLICATE_REQUIREMENT",
                    item.requirement_id,
                )
            seen.add(item.requirement_id)
            if item.source_goal_id not in accepted:
                raise ProductRoutingError(
                    "PRODUCT_ROUTING_SOURCE_OUT_OF_SCOPE",
                    item.source_goal_id,
                )
            identity = {
                "tenant_binding": tenant_binding,
                "research_session_id": research_session_id,
                "brief_id": brief_id,
                "requirement": item.model_dump(mode="json"),
            }
            _, fingerprint = _canonical(identity)
            record_id = "pirr_" + fingerprint[:24]
            with Session(self._engine) as db:
                existing = db.get(
                    ProductInvestigationRequirementRecord,
                    record_id,
                )
                if existing is not None:
                    if existing.requirement_fingerprint != fingerprint:
                        raise ProductRoutingError(
                            "PRODUCT_ROUTING_IDENTITY_COLLISION",
                            record_id,
                        )
                    continue
                row = ProductInvestigationRequirementRecord(
                    routing_record_id=record_id,
                    tenant_binding=tenant_binding,
                    research_session_id=research_session_id,
                    brief_id=brief_id,
                    requirement_id=item.requirement_id,
                    kind=item.kind.value,
                    source_goal_id=item.source_goal_id,
                    source_text=item.source_text,
                    requirement_fingerprint=fingerprint,
                    created_at=stamp,
                )
                db.add(row)
                db.commit()
        return self.load(
            tenant_binding=tenant_binding,
            research_session_id=research_session_id,
        )

    def load(
        self,
        *,
        tenant_binding: str,
        research_session_id: str,
    ) -> tuple[ProductInvestigationRequirement, ...]:
        with Session(self._engine) as db:
            rows = tuple(
                db.exec(
                    select(ProductInvestigationRequirementRecord)
                    .where(
                        ProductInvestigationRequirementRecord.tenant_binding
                        == tenant_binding
                    )
                    .where(
                        ProductInvestigationRequirementRecord.research_session_id
                        == research_session_id
                    )
                    .order_by(
                        ProductInvestigationRequirementRecord.created_at,
                        ProductInvestigationRequirementRecord.routing_record_id,
                    )
                ).all()
            )
        return tuple(
            ProductInvestigationRequirement(
                requirement_id=row.requirement_id,
                kind=ProductInvestigationRequirementKind(row.kind),
                source_goal_id=row.source_goal_id,
                source_text=row.source_text,
            )
            for row in rows
        )
