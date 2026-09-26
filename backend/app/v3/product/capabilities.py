"""Deterministic CompanyContext and capability discovery for Core B."""
from __future__ import annotations

import hashlib
import json

from control_plane.authorize import Principal

from .contracts import (
    CapabilityDescriptor,
    CapabilityDiscovery,
    CapabilityStatus,
    CompanyContext,
)


def _tenant_binding(principal: Principal) -> str:
    if principal.tenant_id is not None:
        return f"id:{principal.tenant_id}"
    if principal.tenant_slug:
        return f"slug:{principal.tenant_slug}"
    raise ValueError("Product CompanyContext requires an explicit tenant binding")


def _canonical(value: object) -> tuple[str, str]:
    raw=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False,default=str)
    return raw,hashlib.sha256(raw.encode("utf-8")).hexdigest()


_BASE_CAPABILITIES: tuple[tuple[str, CapabilityStatus, str, tuple[str, ...], tuple[str, ...]], ...] = (
    ("research.ask", CapabilityStatus.DATA_DEPENDENT, "Research is available when native governed analytical context is connected.", ("governed analytical context",), ("Metabase/Metabot",)),
    ("watch.signal", CapabilityStatus.SUPPORTED, "Governed Watch and Signal lifecycle is sealed.", (), ("Core A Watch/Signal",)),
    ("investigation", CapabilityStatus.SUPPORTED, "Bounded Investigation projection is sealed over Research reasoning.", (), ("P17",)),
    ("evidence", CapabilityStatus.SUPPORTED, "Evidence and claim lineage are sealed authorities.", (), ("P14","P16")),
    ("epistemic.root_cause", CapabilityStatus.SUPPORTED, "Root-cause epistemic authority is sealed.", (), ("P19",)),
    ("report", CapabilityStatus.SUPPORTED, "Governed ReportDocument authority is sealed.", (), ("P20",)),
    ("decision", CapabilityStatus.SUPPORTED, "DecisionBrief advisory authority is sealed.", (), ("P21",)),
    ("adoption", CapabilityStatus.SUPPORTED, "Authenticated Human Adoption authority is sealed.", (), ("Human Adoption",)),
    ("action_work", CapabilityStatus.SUPPORTED, "Internal ActionWork lifecycle is sealed.", (), ("Core A ActionWork",)),
    ("outcome", CapabilityStatus.SUPPORTED, "Governed OutcomeObservation authority is sealed.", (), ("Core A Outcome",)),
    ("memory", CapabilityStatus.SUPPORTED, "Institutional Memory precedent/reference authority is sealed.", (), ("Core A Memory",)),
    ("company_map", CapabilityStatus.FOUNDATION_ONLY, "Stable context/entity references exist; connector onboarding and a generic graph are not implemented.", (), ("CompanyContext","Entity refs")),
    ("data_onboarding", CapabilityStatus.FOUNDATION_ONLY, "Backend foundation exists but connector onboarding is intentionally not implemented.", (), ("CompanyContext",)),
    ("cash_forecast", CapabilityStatus.SPECIAL_ENGINE_DEFERRED, "Forecasting requires a separately authorized specialized engine.", ("forecast-ready time series",), ()),
    ("optimizer", CapabilityStatus.SPECIAL_ENGINE_DEFERRED, "Optimization is outside the canonical shared intelligence engine.", ("objective and constraint model",), ()),
    ("causal_decomposition", CapabilityStatus.SPECIAL_ENGINE_DEFERRED, "Causal decomposition is not inferred by the product layer.", ("identified causal design",), ("P19 epistemic gate",)),
    ("predictive_maintenance", CapabilityStatus.SPECIAL_ENGINE_DEFERRED, "Predictive maintenance requires a specialized predictive engine.", ("machine telemetry",), ()),
    ("recipe_optimization", CapabilityStatus.SPECIAL_ENGINE_DEFERRED, "Recipe optimization requires a specialized process engine.", ("process recipe data",), ()),
    ("scheduler", CapabilityStatus.PRODUCTIZATION_DEFERRED, "Scheduling/product delivery is not part of the sealed headless candidate.", (), ()),
    ("external_action_execution", CapabilityStatus.PRODUCTIZATION_DEFERRED, "External side effects remain explicitly deferred.", (), ("ActionAuthorization only",)),
)


def capability_discovery(
    *,
    principal: Principal,
    analytical_context_available: bool,
    sector_pack_refs: tuple[str, ...] = (),
    entity_refs: tuple[str, ...] = (),
) -> CapabilityDiscovery:
    tenant=_tenant_binding(principal)
    identity={
        "tenant_binding":tenant,
        "sector_pack_refs":sorted(set(sector_pack_refs)),
        "entity_refs":sorted(set(entity_refs)),
    }
    context_id="ctx_"+_canonical(identity)[1][:24]
    rows=[]
    for capability_id,status,reason,required_data,dependencies in _BASE_CAPABILITIES:
        effective=status
        effective_reason=reason
        if capability_id=="research.ask" and analytical_context_available:
            effective=CapabilityStatus.SUPPORTED
            effective_reason="Native governed Metabase/Metabot analytical context is available."
        rows.append(
            CapabilityDescriptor(
                capability_id=capability_id,
                status=effective,
                reason=effective_reason,
                required_data=required_data,
                dependencies=dependencies,
            )
        )
    payload=[item.model_dump(mode="json") for item in rows]
    fingerprint=_canonical(payload)[1]
    return CapabilityDiscovery(
        context_id=context_id,
        capabilities=tuple(rows),
        catalog_fingerprint=fingerprint,
    )


def company_context(
    *,
    principal: Principal,
    analytical_context_available: bool,
    sector_pack_refs: tuple[str, ...] = (),
    entity_refs: tuple[str, ...] = (),
) -> CompanyContext:
    discovery=capability_discovery(
        principal=principal,
        analytical_context_available=analytical_context_available,
        sector_pack_refs=sector_pack_refs,
        entity_refs=entity_refs,
    )
    tenant=_tenant_binding(principal)
    return CompanyContext(
        context_id=discovery.context_id,
        tenant_binding=tenant,
        company_identity=tenant,
        analytical_context_available=analytical_context_available,
        sector_pack_refs=tuple(dict.fromkeys(sector_pack_refs)),
        entity_refs=tuple(dict.fromkeys(entity_refs)),
        capability_discovery=discovery,
        deep_link_id=f"context:{discovery.context_id}",
    )
