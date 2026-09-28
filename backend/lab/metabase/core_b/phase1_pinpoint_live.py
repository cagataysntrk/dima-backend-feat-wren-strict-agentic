#!/usr/bin/env python3
"""Exact Phase-1 final pinpoint live probes.

This is a live validation harness, not a benchmark scorer. It runs exactly one
closed probe per invocation and records durable product/authority observations
for manual adjudication.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any

from sqlmodel import Session

from app.v3.product.contracts import ArtifactKind, ArtifactRef
from app.v3.product.composition import HeadlessProductComposer
from app.v3.product.service import HeadlessProductService, ProductSources
from app.v3.product_routing_store import ProductInvestigationRequirementStore
from app.v3.research_contracts import (
    ResearchNativeVerificationBinding,
    ResearchSemanticRef,
    SemanticTargetKind,
)
from app.v3.research_intake import (
    AllowedRelationship,
    ResearchIntakeCatalog,
    ResearchIntakeCompiler,
    ResearchIntakeTerminal,
)
from app.v3.root_cause_candidate_contract import (
    decode_root_cause_candidate_semantics,
)
from control_plane.models import NativeResourceBinding
from lab.metabase.core_b import live_sentinel as sealed

MODEL = "openai/gpt-5.6-luna"
CONTEXT = "phase1-final-pinpoint-v1"
MAX_ORCHESTRATION_BOUNDARY_UNITS = 12

PROBES = {
    "SCOPE_CURRENTNESS_HARD_V2": {
        "turns": (
            "Mayıs ve Haziran 2026’da bölüm bazında machine downtime ve fault count değişimini karşılaştır. Kötüleşmeyi sıralayıp hangi bölümlerin dikkat istediğini göster.",
            "Şimdi yalnız Haziran 2026’ya daralt. En yüksek downtime olan iki bölümü fault count ile birlikte incele. Önceki analizi tarihsel bağlam olarak koru ama yeni kapsam için eski Evidence’ı current truth sayma; yeni veriye dayan.",
        ),
    },
    "RCA_P19_HARD": {
        "turns": (
            "Haziran’daki machine downtime artışının ana açıklaması maintenance delay mi yoksa spare-part delay mi?\n\nMayıs-Haziran verisini incele.\n\nİki açıklamayı destekleyen ve zayıflatan kanıtları ayrı göster.\n\nGerekirse ikisini ayırmak için tek bir ek analitik test yap.\n\nVeri nedensellik için yeterli değilse bunu açıkça koru.",
        ),
    },
}


class PinpointBudgetExceeded(RuntimeError):
    code = "PINPOINT_ORCHESTRATION_BOUNDARY_BUDGET_EXHAUSTED"

    def __init__(self, owner: str, limit: int) -> None:
        super().__init__(
            f"{self.code}: {owner} would exceed the {limit}-unit live ceiling"
        )
        self.owner = owner
        self.limit = limit


class OrchestrationBudget:
    def __init__(self, limit: int) -> None:
        if limit < 1 or limit > MAX_ORCHESTRATION_BOUNDARY_UNITS:
            raise ValueError("pinpoint model budget must be between 1 and 12")
        self.limit = limit
        self.used = 0
        self.by_owner: dict[str, int] = {}

    def consume(self, owner: str) -> None:
        if self.used >= self.limit:
            raise PinpointBudgetExceeded(owner, self.limit)
        self.used += 1
        self.by_owner[owner] = self.by_owner.get(owner, 0) + 1


class BoundedStructuredTransport:
    def __init__(self, inner, *, budget: OrchestrationBudget, owner: str) -> None:
        self._inner = inner
        self._budget = budget
        self._owner = owner

    @property
    def call_count(self) -> int:
        return int(self._inner.call_count)

    @property
    def trace_log(self):
        return self._inner.trace_log

    def structured_json(self, system, user, *, schema, schema_name):
        self._budget.consume(self._owner)
        return self._inner.structured_json(
            system,
            user,
            schema=schema,
            schema_name=schema_name,
        )

    def close(self) -> None:
        self._inner.close()


class BoundedMaterialExecutor:
    def __init__(self, inner, *, budget: OrchestrationBudget) -> None:
        self._inner = inner
        self._budget = budget

    def execute(self, *args, **kwargs):
        self._budget.consume("metabot")
        return self._inner.execute(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._inner, name)


def _metric(cid: str, name: str, mention: str) -> ResearchSemanticRef:
    return ResearchSemanticRef(
        source_mention=mention,
        candidate_id=cid,
        target_kind=SemanticTargetKind.METRIC,
        canonical_name=name,
        cube_names=("machine_operations",),
    )


def _dim(cid: str, name: str, mention: str) -> ResearchSemanticRef:
    return ResearchSemanticRef(
        source_mention=mention,
        candidate_id=cid,
        target_kind=SemanticTargetKind.DIMENSION,
        canonical_name=name,
        cube_names=("machine_operations",),
    )


def load_binding_manifest(path: Path) -> dict[str, Any]:
    body = json.loads(path.read_text(encoding="utf-8"))
    if body.get("schema_version") != "phase1_pinpoint_native_bindings_v1":
        raise RuntimeError("unexpected pinpoint native binding manifest")
    if body.get("table_name") != "machine_operations":
        raise RuntimeError("unexpected pinpoint native table")
    metrics = body.get("metrics")
    if not isinstance(metrics, list):
        raise RuntimeError("pinpoint metric bindings missing")
    return body

def _native_resource_fingerprint(payload: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def seed_native_resource_bindings(
    db_engine,
    binding_manifest: dict[str, Any],
) -> None:
    """Persist exact runtime locators; never derive business semantics here."""
    database_id = int(binding_manifest["database_id"])
    table_id = int(binding_manifest["table_id"])
    rows: list[NativeResourceBinding] = []

    for item in binding_manifest["metrics"]:
        candidate_id = str(item["candidate_id"])
        entity_id = str(item["native_metric_entity_id"])
        field_id = int(item["fixture_definition"]["field_id"])
        locator = {
            "database_id": database_id,
            "table_id": table_id,
            "field_id": field_id,
            "metric_id": int(item["metabase_metric_id"]),
            "entity_id": entity_id,
        }
        rows.append(
            NativeResourceBinding(
                tenant_id=sealed.TENANT_ID,
                semantic_context_version=CONTEXT,
                candidate_id=candidate_id,
                candidate_kind=SemanticTargetKind.METRIC.value,
                semantic_id=candidate_id,
                canonical_name=str(item["canonical_name"]),
                locator_kind="metric",
                metabase_database_id=database_id,
                metabase_table_id=table_id,
                metabase_field_id=field_id,
                metabase_metric_id=int(item["metabase_metric_id"]),
                metabase_entity_id=entity_id,
                resource_entity_id=f"metabase:metric:{entity_id}",
                resource_fingerprint=_native_resource_fingerprint(locator),
                resource_version=str(binding_manifest["schema_version"]),
            )
        )

    dimensions = binding_manifest.get("dimensions")
    if not isinstance(dimensions, list):
        raise RuntimeError("pinpoint dimension bindings missing")
    for item in dimensions:
        candidate_id = str(item["candidate_id"])
        field_id = int(item["field_id"])
        locator = {
            "database_id": database_id,
            "table_id": table_id,
            "field_id": field_id,
        }
        rows.append(
            NativeResourceBinding(
                tenant_id=sealed.TENANT_ID,
                semantic_context_version=CONTEXT,
                candidate_id=candidate_id,
                candidate_kind=SemanticTargetKind.DIMENSION.value,
                semantic_id=candidate_id,
                canonical_name=str(item["canonical_name"]),
                locator_kind="field",
                metabase_database_id=database_id,
                metabase_table_id=table_id,
                metabase_field_id=field_id,
                resource_entity_id=f"metabase:field:{field_id}",
                resource_fingerprint=_native_resource_fingerprint(locator),
                resource_version=str(binding_manifest["schema_version"]),
            )
        )

    with Session(db_engine) as db:
        for row in rows:
            db.add(row)
        db.commit()



def build_catalog(binding_manifest: dict[str, Any]) -> ResearchIntakeCatalog:
    refs = (
        _metric(
            "metric.machine_downtime_minutes",
            "Machine Downtime Minutes",
            "makine duruşları / duruş süresi / machine downtime",
        ),
        _metric("metric.fault_count", "Fault Count", "arıza sayısı / fault count"),
        _metric("metric.performance_score", "Performance Score", "performans / performance"),
        _metric(
            "metric.maintenance_delay_hours",
            "Maintenance Delay Hours",
            "bakım gecikmesi / maintenance delay",
        ),
        _metric(
            "metric.spare_part_delay_hours",
            "Spare Part Delay Hours",
            "yedek parça gecikmesi / spare part delay",
        ),
        _metric(
            "metric.pm_compliance_pct",
            "Preventive Maintenance Compliance",
            "önleyici bakım uyumu / preventive maintenance compliance",
        ),
        _metric(
            "metric.changeover_count",
            "Changeover Count",
            "changeover / değişim sayısı",
        ),
        _metric(
            "metric.operator_absence_hours",
            "Operator Absence Hours",
            "operatör devamsızlığı / operator absence",
        ),
        _dim("dimension.department", "Department", "bölüm / departman / department"),
        _dim("dimension.event_date", "Event Date", "tarih / date / Mayıs / Haziran"),
        _dim("dimension.machine_id", "Machine", "makine / machine"),
    )
    relationships = (
        AllowedRelationship(
            relationship_id="rel.downtime_fault.department",
            left_semantic_id="metric.machine_downtime_minutes",
            right_semantic_id="metric.fault_count",
            dimension_semantic_id="dimension.department",
        ),
        AllowedRelationship(
            relationship_id="rel.downtime_performance.department",
            left_semantic_id="metric.machine_downtime_minutes",
            right_semantic_id="metric.performance_score",
            dimension_semantic_id="dimension.department",
        ),
        AllowedRelationship(
            relationship_id="rel.downtime_maintenance.department",
            left_semantic_id="metric.machine_downtime_minutes",
            right_semantic_id="metric.maintenance_delay_hours",
            dimension_semantic_id="dimension.department",
        ),
        AllowedRelationship(
            relationship_id="rel.downtime_spare.department",
            left_semantic_id="metric.machine_downtime_minutes",
            right_semantic_id="metric.spare_part_delay_hours",
            dimension_semantic_id="dimension.department",
        ),
    )
    metric_bindings = {
        str(item["candidate_id"]): item
        for item in binding_manifest["metrics"]
        if isinstance(item, dict)
    }
    bindings: list[ResearchNativeVerificationBinding] = []
    metric_ids = {
        item.candidate_id
        for item in refs
        if item.target_kind == SemanticTargetKind.METRIC
    }
    missing = sorted(metric_ids - metric_bindings.keys())
    if missing:
        raise RuntimeError(
            "governed native metric bindings missing: " + ",".join(missing)
        )
    for candidate_id in sorted(metric_ids):
        item = metric_bindings[candidate_id]
        native_id = str(item.get("native_metric_entity_id") or "").strip()
        column = str(item.get("column_name") or "").strip()
        if not native_id or not column:
            raise RuntimeError(f"invalid native metric binding: {candidate_id}")
        bindings.append(
            ResearchNativeVerificationBinding(
                candidate_id=candidate_id,
                table_name="machine_operations",
                column_name=column,
                native_metric_entity_id=native_id,
            )
        )
    for candidate_id, column in (
        ("dimension.department", "department"),
        ("dimension.event_date", "event_date"),
        ("dimension.machine_id", "machine_id"),
    ):
        bindings.append(
            ResearchNativeVerificationBinding(
                candidate_id=candidate_id,
                table_name="machine_operations",
                column_name=column,
            )
        )
    return ResearchIntakeCatalog(
        context_version=CONTEXT,
        semantic_refs=refs,
        allowed_relationships=relationships,
        supported_domains=("machine_operations",),
        temporal_dimension_ids=("dimension.event_date",),
        native_verification_bindings=tuple(bindings),
    )


def _safe_dump(value: Any) -> Any:
    if value is None:
        return None
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    return value


def _links(db_engine, session_ids: tuple[str, ...]):
    out = []
    for session_id in session_ids:
        out.extend(sealed._links(db_engine, session_id))
    return tuple(out)


def _result_payload(link):
    raw = getattr(link, "native_result_json", None)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception:
        return {"_invalid_native_result_json": True}


def _exception_payload(exc: Exception) -> dict[str, Any]:
    diagnostic = getattr(exc, "diagnostic", None)
    cause = getattr(exc, "__cause__", None)
    return {
        "error_type": type(exc).__name__,
        "error": str(exc),
        "error_code": getattr(
            getattr(exc, "code", None),
            "value",
            getattr(exc, "code", None),
        ),
        "owner_diagnostic": _safe_dump(diagnostic),
        "cause_type": type(cause).__name__ if cause is not None else None,
        "cause_code": getattr(cause, "code", None) if cause is not None else None,
        "cause_detail": getattr(cause, "detail", None) if cause is not None else None,
        "cause_diagnostic": (
            _safe_dump(getattr(cause, "diagnostic", None))
            if cause is not None
            else None
        ),
    }


def _trace_slice(transport, start: int) -> list[dict[str, Any]]:
    return [
        item.model_dump(mode="json")
        for item in tuple(transport.trace_log)[start:]
    ]


def _evidence_by_session(orchestrator, session_ids, principal) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for session_id in session_ids:
        state = orchestrator.resume_state(
            session_id=session_id,
            principal=principal,
        )
        out[session_id] = [item.evidence_id for item in state.evidence_refs]
    return out


def _root_candidate_snapshot(p17, session_id: str, principal) -> dict[str, Any]:
    snapshot = p17.snapshot(session_id=session_id, principal=principal)
    candidates = []
    for claim in snapshot.claims:
        semantics = decode_root_cause_candidate_semantics(claim.proposition)
        if semantics is None:
            continue
        candidates.append(
            {
                "claim_id": claim.claim_id,
                "claim_text": claim.claim_text,
                "mechanism_identity": list(semantics.mechanism_identity),
                "mechanism_ref": semantics.mechanism_ref,
                "relation_kind": semantics.relation_kind.value,
                "scope_lineage_id": semantics.scope_lineage_id,
                "scope_version_id": semantics.scope_version_id,
                "evidence_refs": [
                    item.evidence_id for item in claim.evidence_links
                ],
                "evidence_relations": list(claim.evidence_relations),
                "limitations": list(claim.limitations),
            }
        )
    return {
        "snapshot": snapshot.model_dump(mode="json"),
        "root_cause_candidates": candidates,
    }


def _execute_turn(
    *,
    probe_id: str,
    turn_no: int,
    question: str,
    prior_brief,
    prior_session_id: str | None,
    catalog: ResearchIntakeCatalog,
    intake,
    product,
    composer,
    p17,
    p17_manager,
    p19_manager,
    reasoning,
    orchestrator,
    db_engine,
    native_token: str,
    transports: dict[str, Any],
):
    started = time.monotonic()
    trace_starts = {
        name: len(tuple(transport.trace_log))
        for name, transport in transports.items()
    }
    intake_result = product.research_question(
        question=question,
        catalog=catalog,
        principal=sealed._principal(),
        prior_brief=prior_brief,
    )
    if intake_result.terminal != ResearchIntakeTerminal.READY:
        return {
            "turn": turn_no,
            "question": question,
            "terminal_state": intake_result.terminal.value,
            "ready": False,
            "intake_payload": _safe_dump(intake_result),
            "total_latency_ms": int((time.monotonic() - started) * 1000),
            "transport_traces": {
                name: _trace_slice(transport, trace_starts[name])
                for name, transport in transports.items()
            },
        }, None, None

    brief = intake_result.brief
    assert brief is not None
    composition = composer.compose(
        brief=brief,
        principal=sealed._principal(),
        request_ref=f"phase1-pinpoint:{probe_id}:{turn_no}",
        source_message_hash=hashlib.sha256(question.encode("utf-8")).hexdigest(),
        native_session_token=native_token,
        investigation_requirements=intake_result.investigation_requirements,
        prior_research_session_id=prior_session_id,
    )
    final = orchestrator.resume_state(
        session_id=composition.research_session_id,
        principal=sealed._principal(),
    )
    session_ids = (
        composition.research_session_id,
        *composition.child_research_session_ids,
    )
    all_links = _links(db_engine, session_ids)
    reasoning_records = []
    for session_id in session_ids:
        for step in reasoning.steps(session_id):
            item = {
                "step": step.model_dump(mode="json"),
                "proposal": None,
            }
            try:
                item["proposal"] = reasoning.proposal(
                    step.step_id
                ).model_dump(mode="json")
            except Exception as exc:
                item["proposal_load_error"] = type(exc).__name__
            reasoning_records.append(item)
    epistemic_payloads = []
    for ref in composition.p19_assessment_refs:
        try:
            epistemic_payloads.append(
                _safe_dump(
                    composer._epistemics.load_assessment(
                        assessment_id=ref,
                        principal=sealed._principal(),
                    )
                )
            )
        except Exception as exc:
            epistemic_payloads.append(
                {"assessment_id": ref, "load_error": type(exc).__name__}
            )
    root_snapshot = None
    try:
        root_snapshot = _root_candidate_snapshot(
            p17,
            composition.research_session_id,
            sealed._principal(),
        )
    except Exception as exc:
        root_snapshot = {"load_error": type(exc).__name__, "detail": str(exc)}

    return {
        "turn": turn_no,
        "question": question,
        "terminal_state": composition.terminal_state.value,
        "ready": True,
        "intake_payload": _safe_dump(intake_result),
        "brief_payload": _safe_dump(brief),
        "composition_payload": _safe_dump(composition),
        "research_payload": _safe_dump(final),
        "research_session_id": composition.research_session_id,
        "child_research_session_ids": list(composition.child_research_session_ids),
        "session_ids": list(session_ids),
        "scope_lineage_id": final.lineage_id,
        "scope_version_id": final.accepted_brief.scope.scope_version.version_id,
        "evidence_by_session": _evidence_by_session(
            orchestrator,
            session_ids,
            sealed._principal(),
        ),
        "reasoning_records": reasoning_records,
        "root_cause_state": root_snapshot,
        "native_results": [
            _result_payload(link)
            for link in all_links
            if _result_payload(link) is not None
        ],
        "p18_policy_use_refs": list(composition.p18_policy_use_refs),
        "p19_assessment_refs": list(composition.p19_assessment_refs),
        "epistemic_payloads": epistemic_payloads,
        "limitations": [_safe_dump(item) for item in composition.limitations],
        "transport_traces": {
            name: _trace_slice(transport, trace_starts[name])
            for name, transport in transports.items()
        },
        "total_latency_ms": int((time.monotonic() - started) * 1000),
    }, brief, composition.research_session_id


def _currentness(
    *,
    product,
    turn: dict[str, Any],
) -> dict[str, Any]:
    principal = sealed._principal()
    session_id = turn["research_session_id"]
    research = product.resume(
        ref=ArtifactRef(kind=ArtifactKind.RESEARCH, artifact_id=session_id),
        principal=principal,
    )
    evidence = []
    for scope_id, evidence_ids in turn["evidence_by_session"].items():
        for evidence_id in evidence_ids:
            artifact = product.resume(
                ref=ArtifactRef(
                    kind=ArtifactKind.EVIDENCE,
                    artifact_id=evidence_id,
                    scope_id=scope_id,
                ),
                principal=principal,
            )
            evidence.append(
                {
                    "evidence_id": evidence_id,
                    "scope_id": scope_id,
                    "currentness": artifact.header.currentness.value,
                }
            )
    return {
        "research_session_id": session_id,
        "research_currentness": research.header.currentness.value,
        "evidence": evidence,
    }


def _mechanical_a(turns: list[dict[str, Any]], currentness: dict[str, Any]) -> dict[str, bool]:
    if len(turns) != 2:
        return {"two_turns_executed": False}
    first, second = turns
    old = currentness["old"]
    new = currentness["new"]
    old_primary = [
        item
        for item in old["evidence"]
        if item["scope_id"] == first["research_session_id"]
    ]
    new_primary = [
        item
        for item in new["evidence"]
        if item["scope_id"] == second["research_session_id"]
    ]
    return {
        "two_turns_executed": True,
        "both_turns_ready": bool(first["ready"] and second["ready"]),
        "scope_lineage_continuity": (
            first["scope_lineage_id"] == second["scope_lineage_id"]
        ),
        "scope_version_advanced": (
            first["scope_version_id"] != second["scope_version_id"]
        ),
        "old_research_superseded": (
            old["research_currentness"] == "SUPERSEDED"
        ),
        "new_research_current": (
            new["research_currentness"] == "CURRENT"
        ),
        "old_primary_evidence_historical": (
            bool(old_primary)
            and all(item["currentness"] == "HISTORICAL" for item in old_primary)
        ),
        "new_primary_evidence_current": (
            bool(new_primary)
            and all(item["currentness"] == "CURRENT" for item in new_primary)
        ),
    }


def _mechanical_b(turn: dict[str, Any]) -> dict[str, Any]:
    state = turn.get("root_cause_state") or {}
    candidates = state.get("root_cause_candidates") or []
    evidence_backed = [
        item for item in candidates if item.get("evidence_refs")
    ]
    distinct = {
        tuple(item["mechanism_identity"])
        for item in evidence_backed
        if isinstance(item.get("mechanism_identity"), list)
        and len(item["mechanism_identity"]) == 2
    }
    p19_calls = len(turn.get("p19_assessment_refs") or [])
    requires_p19 = len(distinct) >= 2
    return {
        "ready": bool(turn.get("ready")),
        "evidence_backed_candidate_count": len(evidence_backed),
        "distinct_governed_mechanism_count": len(distinct),
        "p19_required_by_observed_candidate_state": requires_p19,
        "p19_assessment_count": p19_calls,
        "p19_called_when_required": (not requires_p19) or p19_calls > 0,
        "max_reasoning_depth": max(
            (
                int((item.get("step") or {}).get("depth") or 0) + 1
                for item in turn.get("reasoning_records") or []
            ),
            default=0,
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--probe-id",
        required=True,
        choices=tuple(PROBES),
    )
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--email", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--binding-manifest", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--control-db", type=Path, required=True)
    ap.add_argument("--engine-sha", required=True)
    ap.add_argument("--upstream-sha", required=True)
    ap.add_argument("--runtime-tag", required=True)
    ap.add_argument("--runtime-image-digest", required=True)
    ap.add_argument("--build-identity", required=True)
    ap.add_argument("--image-identity", required=True)
    ap.add_argument("--candidate-product-sha", required=True)
    ap.add_argument("--provider-proxy-base-url", required=True)
    ap.add_argument("--provider-receipt", type=Path, required=True)
    ap.add_argument(
        "--max-orchestration-boundary-units",
        type=int,
        default=MAX_ORCHESTRATION_BOUNDARY_UNITS,
    )
    args = ap.parse_args()

    if (
        args.max_orchestration_boundary_units
        != MAX_ORCHESTRATION_BOUNDARY_UNITS
    ):
        raise RuntimeError(
            "Phase-1 orchestration boundary ceiling is exactly 12 units"
        )
    api_key = os.environ.get("DIMA_OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("DIMA_OPENROUTER_API_KEY required")

    binding_manifest = load_binding_manifest(args.binding_manifest)
    catalog = build_catalog(binding_manifest)
    token, current = sealed._login(args.base_url, args.email, args.password)
    db_engine = sealed._build_control_plane(
        args.control_db,
        int(current["id"]),
    )
    seed_native_resource_bindings(db_engine, binding_manifest)
    session_store = sealed.ResearchSessionStore(db_engine)
    expected = sealed.NativeEngineIdentity(
        engine_sha=args.engine_sha,
        upstream_base_sha=args.upstream_sha,
        runtime_tag=args.runtime_tag,
        runtime_image_digest=args.runtime_image_digest,
        build_identity=args.build_identity,
        runtime_image_identity=args.image_identity,
    )
    subjects = sealed.NativeSubjectSessionProvider(
        base_url=args.base_url,
        expected_identity=expected,
        db_engine=db_engine,
    )
    raw_material = sealed.NativeResearchMaterialExecutor(
        subject_provider=subjects,
        store=session_store,
        expected_identity=expected,
    )
    budget = OrchestrationBudget(args.max_orchestration_boundary_units)
    material_executor = BoundedMaterialExecutor(raw_material, budget=budget)
    orchestrator = sealed.ResearchAskOrchestrator(
        store=session_store,
        bridge_factory=subjects,
        material_executor=material_executor,
    )

    proxy_base = args.provider_proxy_base_url.rstrip("/")
    raw_intake = sealed.OpenRouterStructuredJSONTransport(
        api_key=api_key,
        model=MODEL,
        base_url=proxy_base + "/source/research_intake/v1",
        owner="research_intake",
    )
    raw_p17 = sealed.OpenRouterStructuredJSONTransport(
        api_key=api_key,
        model=MODEL,
        base_url=proxy_base + "/source/p17_manager/v1",
        owner="p17_manager",
    )
    raw_p19 = sealed.OpenRouterStructuredJSONTransport(
        api_key=api_key,
        model=MODEL,
        base_url=proxy_base + "/source/p19_manager/v1",
        owner="p19_manager",
    )
    intake_transport = BoundedStructuredTransport(
        raw_intake,
        budget=budget,
        owner="research_intake",
    )
    p17_transport = BoundedStructuredTransport(
        raw_p17,
        budget=budget,
        owner="p17_manager",
    )
    p19_transport = BoundedStructuredTransport(
        raw_p19,
        budget=budget,
        owner="p19_manager",
    )
    intake = ResearchIntakeCompiler(transport=intake_transport)
    product = HeadlessProductService(
        sources=ProductSources(
            research=orchestrator,
            intake=intake,
        )
    )
    reasoning = sealed.ResearchReasoningStore(db_engine)
    claim_store = sealed.ClaimLineageStore(
        research_store=session_store,
        db_engine=db_engine,
    )
    occurrence_runner = sealed.NativeResearchOccurrenceRunner(
        store=session_store,
        bridge_factory=subjects,
        material_executor=material_executor,
    )
    exploration = sealed.NativeResearchExploration(
        research_store=session_store,
        subject_provider=subjects,
    )
    p17 = sealed.ResearchInvestigationManager(
        research_store=session_store,
        claim_store=claim_store,
        reasoning_store=reasoning,
        followup_executor=sealed.NativeResearchFollowupExecutor(
            store=session_store,
            occurrence_runner=occurrence_runner,
            exploration=exploration,
        ),
        db_engine=db_engine,
    )
    p17_manager = sealed.StructuredResearchProposalManager(
        transport=p17_transport
    )
    p18 = sealed.BusinessRelationshipPolicyStore(
        research_store=session_store,
        db_engine=db_engine,
    )
    p19 = sealed.HypothesisRootCauseStore(
        research_store=session_store,
        db_engine=db_engine,
    )
    p19_manager = sealed.StructuredP19AssessmentManager(
        transport=p19_transport
    )
    p20 = sealed.ReportDocumentStore(
        research_store=session_store,
        db_engine=db_engine,
    )
    routing = sealed.ProductInvestigationRequirementStore(db_engine)
    composer = HeadlessProductComposer(
        research=orchestrator,
        investigation=p17,
        investigation_manager=p17_manager,
        reasoning=reasoning,
        relationships=p18,
        epistemics=p19,
        epistemic_manager=p19_manager,
        reports=p20,
        investigation_requirements=routing,
    )
    product = HeadlessProductService(
        sources=ProductSources(
            research=orchestrator,
            intake=intake,
            reasoning=reasoning,
            claims=claim_store,
            epistemics=p19,
            reports=p20,
        )
    )
    transports = {
        "research_intake": intake_transport,
        "p17_manager": p17_transport,
        "p19_manager": p19_transport,
    }

    report: dict[str, Any] = {
        "schema_version": "dima_v1_phase1_final_pinpoint_live_v1",
        "probe_id": args.probe_id,
        "candidate_product_sha": args.candidate_product_sha,
        "engine_sha": args.engine_sha,
        "engine_runtime_tag": args.runtime_tag,
        "max_orchestration_boundary_units": MAX_ORCHESTRATION_BOUNDARY_UNITS,
        "binding_manifest": binding_manifest,
        "turn_count_expected": len(PROBES[args.probe_id]["turns"]),
        "turns": [],
        "manual_adjudication_required": True,
        "quality_score": None,
    }
    started = time.monotonic()
    prior_brief = None
    prior_session_id = None
    try:
        for turn_no, question in enumerate(
            PROBES[args.probe_id]["turns"],
            start=1,
        ):
            record, prior_brief, prior_session_id = _execute_turn(
                probe_id=args.probe_id,
                turn_no=turn_no,
                question=question,
                prior_brief=prior_brief,
                prior_session_id=prior_session_id,
                catalog=catalog,
                intake=intake,
                product=product,
                composer=composer,
                p17=p17,
                p17_manager=p17_manager,
                p19_manager=p19_manager,
                reasoning=reasoning,
                orchestrator=orchestrator,
                db_engine=db_engine,
                native_token=token,
                transports=transports,
            )
            report["turns"].append(record)
            if not record.get("ready"):
                break

        if (
            args.probe_id == "SCOPE_CURRENTNESS_HARD_V2"
            and len(report["turns"]) == 2
            and all(item.get("ready") for item in report["turns"])
        ):
            currentness = {
                "old": _currentness(
                    product=product,
                    turn=report["turns"][0],
                ),
                "new": _currentness(
                    product=product,
                    turn=report["turns"][1],
                ),
            }
            report["currentness"] = currentness
            report["mechanical_observations"] = _mechanical_a(
                report["turns"],
                currentness,
            )
        elif (
            args.probe_id == "RCA_P19_HARD"
            and report["turns"]
        ):
            report["mechanical_observations"] = _mechanical_b(
                report["turns"][0]
            )
    except Exception as exc:
        report["exception"] = _exception_payload(exc)
    finally:
        report["orchestration_boundary_units"] = budget.used
        report["orchestration_boundary_units_by_owner"] = dict(
            sorted(budget.by_owner.items())
        )
        report["within_orchestration_boundary_budget"] = (
            budget.used <= MAX_ORCHESTRATION_BOUNDARY_UNITS
        )
        report["turn_count_executed"] = len(report["turns"])
        report["total_latency_ms"] = int((time.monotonic() - started) * 1000)
        report["transport_traces"] = {
            name: [
                trace.model_dump(mode="json")
                for trace in transport.trace_log
            ]
            for name, transport in transports.items()
        }
        raw_intake.close()
        raw_p17.close()
        raw_p19.close()
        try:
            provider = json.loads(
                args.provider_receipt.read_text(encoding="utf-8")
            )
            if provider.get("schema_version") != "dima_openrouter_counting_proxy_v1":
                raise RuntimeError("unexpected provider counting receipt schema")
            report["provider_receipt"] = provider
            report["actual_provider_request_count"] = int(
                provider["actual_provider_request_count"]
            )
            report["provider_requests_by_source"] = dict(
                provider["provider_requests_by_source"]
            )
            report["hard_provider_request_ceiling"] = int(
                provider["hard_provider_request_ceiling"]
            )
            report["prompt_tokens"] = provider.get("prompt_tokens")
            report["completion_tokens"] = provider.get("completion_tokens")
            report["reasoning_tokens"] = provider.get("reasoning_tokens")
            report["provider_reported_cost"] = provider.get(
                "provider_reported_cost"
            )
        except Exception as exc:
            report["provider_receipt_error"] = {
                "error_type": type(exc).__name__,
                "error": str(exc),
            }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "probe_id": args.probe_id,
                "turns": report["turn_count_executed"],
                "orchestration_units": report["orchestration_boundary_units"],
                "within_orchestration_budget": report[
                    "within_orchestration_boundary_budget"
                ],
                "actual_provider_requests": report.get(
                    "actual_provider_request_count"
                ),
                "exception": (report.get("exception") or {}).get("error_code"),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
