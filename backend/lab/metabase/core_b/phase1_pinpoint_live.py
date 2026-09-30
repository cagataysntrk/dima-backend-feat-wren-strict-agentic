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
METABOT_MODEL = "openrouter/openai/gpt-5.6-luna"
CONTEXT = "phase1-final-pinpoint-v1"
MAX_ORCHESTRATION_BOUNDARY_UNITS = 12

HISTORICAL_MANUAL_SCORE_SCALE = {
    "FAIL": 0,
    "LOW_UTILITY": 1,
    "PARTIAL": 2,
    "STRONG_PARTIAL": 3,
    "FULL": 4,
}

PROBES = {
    "R_LIVE_1_ONE_PASS": {
        "historical_round2_case_id": None,
        "turns": (
            "Packaging bölümünde Mayıs-Haziran 2026 machine downtime artışını açıklarken maintenance delay ile spare-part delay adaylarını değerlendir. İki adayın destekleyen ve zayıflatan kanıtlarını ayrı tut. Mevcut governed Evidence adayları yeterince değerlendiriyorsa sırf derinlik göstermek için ek analitik sorgu açma; P19 ile en savunulabilir terminal sonuca ulaş ve nedensellik sınırını koru.",
        ),
        "manual_contract": (
            "accepted user candidate identities are preserved exactly",
            "initial native material produces governed Evidence",
            "user-seeded hypotheses reach P19 without redundant P17 synthesis or analytical re-entry",
            "P19 assessment exists",
            "root_cause_mode = ONE_PASS and analytical_reentry_count = 0",
            "support/challenge and causal limitations are useful and legally preserved",
        ),
    },
    "R_LIVE_2_ADAPTIVE": {
        "historical_round2_case_id": None,
        "turns": (
            "Assembly bölümünde Mayıs-Haziran 2026 machine downtime artışını maintenance delay ile spare-part delay adayları arasında araştır. İlk governed Evidence iki adayı güvenli biçimde ayıramıyorsa yalnız bir yüksek bilgi değerli discriminating analitik test yap, yeni Evidence ile P19 değerlendirmesini yenile ve sonra dur. Destek, karşı kanıt ve nedensellik sınırını koru.",
        ),
        "manual_contract": (
            "accepted user candidate identities are preserved exactly",
            "initial P19 assessment identifies a real unresolved discrimination need",
            "exactly one materially useful analytical re-entry occurs when needed",
            "new Evidence is grounded before P19 reassessment",
            "root_cause_mode = ADAPTIVE with one analytical re-entry",
            "no retry-until-lucky, duplicate analytics, or causal overclaim",
        ),
    },
    "R_LIVE_3_DISCOVERY": {
        "historical_round2_case_id": None,
        "turns": (
            "Assembly bölümünde Mayıs-Haziran 2026 machine downtime artışını açıkla. Aday neden vermiyorum: governed operasyon metrikleri içinden kanıtla desteklenebilen birden fazla aday mekanizmayı keşfet, destek ve karşı kanıtlarını değerlendir, sonra P19 ile savunulabilir sonuca ulaş. Gereksiz analitik tekrar yapma ve nedensellik sınırını koru.",
        ),
        "manual_contract": (
            "causal_competition contains no user-seeded candidate identities",
            "P17 discovery path creates governed typed mechanism candidates from accepted refs",
            "at least two evidence-backed distinct candidates reach P19 when supported",
            "P19 assessment exists",
            "no fabricated semantic identity or free-text mechanism authority",
            "no redundant analytics or causal overclaim",
        ),
    },
    "SCOPE_CURRENTNESS_HARD_V4": {
        "historical_round2_case_id": None,
        "turns": (
            "Mayıs ve Haziran 2026’da bölüm bazında machine downtime ve fault count değişimini karşılaştır. Kötüleşmeyi sıralayıp hangi bölümlerin dikkat istediğini göster.",
            "Şimdi yalnız Haziran 2026’ya daralt. En yüksek downtime olan iki bölümü fault count ile birlikte incele. Önceki analizi tarihsel bağlam olarak koru ama yeni kapsam için eski Evidence’ı current truth sayma; yeni veriye dayan.",
        ),
        "manual_contract": (
            "both turns READY",
            "native execution and material observation produce governed Evidence",
            "scope lineage continuity and scope version advance",
            "old Research becomes SUPERSEDED and old Evidence HISTORICAL",
            "new Research and new Evidence are CURRENT",
            "June narrowing, department scope, and ranking target are preserved",
            "exception=0 and silent semantic drift=0",
        ),
    },
    "RCA_P19_HARD_V2": {
        "historical_round2_case_id": None,
        "turns": (
            "Haziran’daki machine downtime artışının ana açıklaması maintenance delay mi yoksa spare-part delay mi?\n\nMayıs-Haziran verisini incele.\n\nİki açıklamayı destekleyen ve zayıflatan kanıtları ayrı göster.\n\nGerekirse ikisini ayırmak için tek bir ek analitik test yap.\n\nVeri nedensellik için yeterli değilse bunu açıkça koru.",
        ),
        "manual_contract": (
            "accepted explicit candidate identities remain governed",
            "P17 synthesis may interpret existing Evidence without mandatory analytical re-entry",
            "P19 eligibility is evaluated and P19 is invoked when eligible",
            "supporting and challenging Evidence are retained",
            "the selected ONE_PASS / ADAPTIVE / GOVERNED_INCONCLUSIVE mode fits the Evidence",
            "no fabricated competitor, fake winner, unsupported root cause, or causal overclaim",
        ),
    },
    "RELATIONSHIP_F05_H_RECOVERY": {
        "historical_round2_case_id": "F05_H",
        "turns": (
            "Duruş, arıza, bakım gecikmesi ve performans arasındaki ilişkileri birlikte araştır; hangi ilişkilerin daha güçlü veya zayıf göründüğünü supporting ve challenging evidence ile raporla, nedenselliği kanıtlanmış gibi sunma.",
        ),
        "manual_contract": (
            "native analytical work > 0",
            "P18 invoked > 0 and no unexplained BLOCKED ending",
            "multiple relevant relationship analyses exist",
            "supporting Evidence and challenging Evidence exist",
            "material relationship interpretation and evidence-governed strength differences exist",
            "association is not promoted to causation",
            "causal overclaim=0, exception=0, silent wrong=0",
        ),
    },
    "REPORT_F08_H_RECOVERY": {
        "historical_round2_case_id": "F08_H",
        "turns": (
            "Yönetim için kanıta bağlı rapor üret: gözlem, bulgu, hipotez, karşı kanıt, sınırlılık ve karar açısından önemli noktaları ayrı göster; sayısal ve nedensel iddiaların provenance'ını koru ve kanıtın izin verdiğinden daha güçlü ifade kullanma.",
        ),
        "manual_contract": (
            "exception=0 and P20 REPORT or legitimately LIMITED REPORT",
            "material claims > 0 and governed Evidence > 0",
            "Claim -> Evidence -> native receipt lineage is intact",
            "Research/scope lineage and currentness are correct",
            "observations, findings, hypotheses, counter-Evidence, and limitations remain distinguishable",
            "numeric provenance is preserved and invented numeric truth=0",
            "causal promotion beyond P19=0",
        ),
    },
    "ADAPTIVE_F06_H_RETENTION": {
        "historical_round2_case_id": "F06_H",
        "turns": (
            "Mayıs-Haziran duruş bozulmasını araştır. İlk bulgudan sonra en maddi yeni yönü seçip en az iki farklı analitik derinleşme yap; her adımda neden o yönü seçtiğini, hangi kanıtın kararı değiştirdiğini ve nerede durduğunu açıkça kaydet.",
        ),
        "manual_contract": (
            "initial analytical finding exists",
            "at least two genuinely distinct discriminating follow-up moves when Evidence supports depth",
            "follow-up direction is Evidence-selected and has typed identity",
            "P17 reasoning trace exists and new Evidence changes or narrows investigation state",
            "no pointless breadth expansion or repeated equivalent query disguised as depth",
            "termination is explicit/governed and budget is respected",
            "exception=0 and silent wrong=0",
        ),
    },
    "CONVERSATION_F10_H_RECOVERY": {
        "historical_round2_case_id": "F10_H",
        "turns": (
            "Mayıs-Haziran duruş artışını çok faktörlü araştır; alternatif nedenleri ve karşı kanıtı da değerlendir.",
            "Düzeltme: yalnız Assembly bölümüne odaklan; Packaging ve diğer bölümleri yeni kapsamdan çıkar.",
            "Şimdi yalnız düzeltilmiş Assembly kapsamı içinde en güçlü iki açıklamayı derinleştir; eski geniş kapsamın bulgularını yeni kanıt gibi kullanma.",
        ),
        "manual_contract": (
            "multiple turns execute under one governed conversation lineage",
            "scope correction narrows to Assembly and advances scope version",
            "prior wider Research/Evidence remains historical rather than current truth",
            "investigation continues only inside the corrected scope",
            "no stale Evidence reuse and no re-expansion to removed departments",
            "manual usefulness is FULL-preferred for 80+ readiness",
            "exception=0, silent wrong=0, and blocked provider requests=0",
        ),
    },
    "RCA_F07_H_RECOVERY": {
        "historical_round2_case_id": "F07_H",
        "turns": (
            "Mayıs-Haziran duruş artışının kök nedenlerini çok faktörlü araştır. Birden fazla maddi katkı olabilir. Aday nedenleri yarışmaya sok, destek ve karşı kanıt ara, önemli nedenlerin nedenlerine üç seviyeye kadar in; dominant/material/secondary olarak ayır, emin olmadığın yerde inconclusive de ve adım adım investigation trace üret.",
        ),
        "manual_contract": (
            "multiple plausible root-cause candidates remain available when supported",
            "supporting and challenging Evidence are explicit and same-scope",
            "discriminating analyses genuinely separate competing candidates",
            "P17 investigation reaches P19 only when epistemically eligible",
            "no fabricated winner, unsupported dominant cause, or causal overclaim",
            "stepwise investigation trace and governed inconclusive behavior are preserved",
            "exception=0, silent wrong=0, and blocked provider requests=0",
        ),
    },
    "MULTI_INTENT_F04_H_RECOVERY": {
        "historical_round2_case_id": "F04_H",
        "turns": (
            "Mayıs-Haziran 2026 üretim görünümünü duruş, arıza, performans, bakım gecikmesi, yedek parça gecikmesi, önleyici bakım uyumu ve changeover üzerinden birlikte araştır; çelişkili sinyalleri saklama, kanıta bağlı kısa yönetim raporu üret.",
        ),
        "manual_contract": (
            "all accepted material signals are retained without silent metric loss",
            "conflicting findings remain visible rather than collapsed into one narrative",
            "synthesis is Evidence-backed with preserved Claim/Evidence/receipt lineage",
            "no invented priority score or unsupported causal promotion",
            "P20 output is a concise management-useful synthesis rather than a raw-data shell",
            "exception=0, silent wrong=0, and blocked provider requests=0",
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
    entity_values = body.get("entity_values")
    if not isinstance(entity_values, list):
        raise RuntimeError("pinpoint governed entity-value bindings missing")
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


def _native_resource_binding_rows(
    binding_manifest: dict[str, Any],
) -> list[NativeResourceBinding]:
    """Build exact governed runtime bindings from the sealed live manifest."""
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

    entity_values = binding_manifest.get("entity_values")
    if not isinstance(entity_values, list):
        raise RuntimeError("pinpoint entity-value bindings missing")
    for item in entity_values:
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
                candidate_kind=SemanticTargetKind.ENTITY_VALUE.value,
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
    return rows


def seed_native_resource_bindings(
    db_engine,
    binding_manifest: dict[str, Any],
) -> None:
    """Persist exact runtime locators; never derive business semantics here."""
    rows = _native_resource_binding_rows(binding_manifest)
    with Session(db_engine) as db:
        for row in rows:
            db.add(row)
        db.commit()



def build_catalog(binding_manifest: dict[str, Any]) -> ResearchIntakeCatalog:
    base_refs = (
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
    entity_refs = tuple(
        ResearchSemanticRef(
            source_mention=str(item["source_mention"]),
            candidate_id=str(item["candidate_id"]),
            target_kind=SemanticTargetKind.ENTITY_VALUE,
            canonical_name=str(item["canonical_name"]),
            dimension_name=str(item["dimension_name"]),
            value=str(item["value"]),
            cube_names=("machine_operations",),
        )
        for item in binding_manifest["entity_values"]
    )
    refs = (*base_refs, *entity_refs)
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
    for item in binding_manifest["entity_values"]:
        candidate_id = str(item.get("candidate_id") or "").strip()
        column = str(item.get("column_name") or "").strip()
        value = item.get("value")
        dimension_name = str(item.get("dimension_name") or "").strip()
        if not candidate_id or not column or not dimension_name or not isinstance(value, str):
            raise RuntimeError("invalid governed entity-value binding")
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


_MODEL_CEILING_CODES = frozenset(
    {
        "COGNITION_OUTPUT_BUDGET_EXHAUSTED",
        "PROVIDER_PROMPT_TOKEN_CEILING_REACHED",
        "PROVIDER_COMPLETION_TOKEN_CEILING_REACHED",
        "PROVIDER_REASONING_TOKEN_CEILING_REACHED",
        "PROVIDER_COST_CEILING_REACHED",
    }
)


def _model_ceiling_events(report: dict[str, Any]) -> list[dict[str, Any]]:
    """Return privacy-safe model/budget ceiling telemetry only.

    Never copy prompts, response text, exception detail, headers, or reasoning.
    This is diagnostic routing metadata, not Product semantic authority.
    """
    events: list[dict[str, Any]] = []
    seen: set[tuple[Any, ...]] = set()

    def add(
        code: str,
        source: str,
        *,
        ordinal: int | None = None,
        model: str | None = None,
        max_completion_tokens: int | None = None,
    ) -> None:
        key = (code, source, ordinal, model, max_completion_tokens)
        if key in seen:
            return
        seen.add(key)
        item: dict[str, Any] = {"code": code, "source": source}
        if ordinal is not None:
            item["ordinal"] = ordinal
        if model is not None:
            item["model"] = model
        if max_completion_tokens is not None:
            item["max_completion_tokens"] = max_completion_tokens
        events.append(item)

    exception = report.get("exception")
    if isinstance(exception, dict):
        for field in ("error_code", "cause_code"):
            code = exception.get(field)
            if isinstance(code, str) and code in _MODEL_CEILING_CODES:
                add(code, "product_exception")

    provider = report.get("provider_receipt")
    if isinstance(provider, dict):
        raw_events = provider.get("events")
        if isinstance(raw_events, list):
            for event in raw_events:
                if not isinstance(event, dict):
                    continue
                code = event.get("blocked_reason")
                if not isinstance(code, str) or code not in _MODEL_CEILING_CODES:
                    continue
                ordinal = event.get("ordinal")
                add(
                    code,
                    str(event.get("source") or "provider_proxy"),
                    ordinal=ordinal if isinstance(ordinal, int) else None,
                )

    traces = report.get("transport_traces")
    if isinstance(traces, dict):
        for owner, raw_traces in traces.items():
            if not isinstance(raw_traces, list):
                continue
            for trace in raw_traces:
                if not isinstance(trace, dict):
                    continue
                finish = trace.get("finish_reason")
                native = trace.get("native_finish_reason")
                if finish != "length" and native not in {
                    "length",
                    "max_output_tokens",
                    "max_completion_tokens",
                }:
                    continue
                ordinal = trace.get("call_ordinal_by_role")
                max_tokens = trace.get("max_completion_tokens")
                model = trace.get("model")
                add(
                    "MODEL_OUTPUT_LENGTH_LIMIT",
                    str(owner),
                    ordinal=ordinal if isinstance(ordinal, int) else None,
                    model=model if isinstance(model, str) else None,
                    max_completion_tokens=(
                        max_tokens if isinstance(max_tokens, int) else None
                    ),
                )
    return events


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
    reports,
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
    try:
        composition = composer.compose(
            brief=brief,
            principal=sealed._principal(),
            request_ref=f"phase1-pinpoint:{probe_id}:{turn_no}",
            source_message_hash=hashlib.sha256(question.encode("utf-8")).hexdigest(),
            native_session_token=native_token,
            investigation_requirements=intake_result.investigation_requirements,
            prior_research_session_id=prior_session_id,
        )
    except Exception as exc:
        return {
            "turn": turn_no,
            "question": question,
            "terminal_state": "COMPOSITION_ERROR",
            "ready": False,
            "intake_payload": _safe_dump(intake_result),
            "brief_payload": _safe_dump(brief),
            "composition_exception": _exception_payload(exc),
            "total_latency_ms": int((time.monotonic() - started) * 1000),
            "transport_traces": {
                name: _trace_slice(transport, trace_starts[name])
                for name, transport in transports.items()
            },
        }, brief, prior_session_id
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

    report_payload = None
    if composition.p20_report_ref:
        try:
            report_doc = reports.load(
                report_id=composition.p20_report_ref,
                principal=sealed._principal(),
            )
            report_payload = {
                "document": report_doc.model_dump(mode="json"),
                "currentness": reports.currentness(
                    report_id=composition.p20_report_ref,
                    principal=sealed._principal(),
                ).value,
            }
        except Exception as exc:
            report_payload = {
                "report_id": composition.p20_report_ref,
                "load_error": type(exc).__name__,
                "detail": str(exc),
            }

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
        "p20_report": report_payload,
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


def _root_mode_payload(turn: dict[str, Any]) -> dict[str, Any] | None:
    composition = turn.get("composition_payload") or {}
    modes = composition.get("root_cause_mode_results") or []
    if len(modes) != 1:
        return None
    return modes[0]


def _mechanical_r_live(
    probe_id: str,
    turn: dict[str, Any],
) -> dict[str, Any]:
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
    mode = _root_mode_payload(turn)
    p19_count = len(turn.get("p19_assessment_refs") or [])
    reasoning = turn.get("reasoning_records") or []
    brief = turn.get("brief_payload") or {}
    composition = turn.get("composition_payload") or {}
    completion = composition.get("completion_ledger") or {}
    owner_calls = composition.get("owner_calls") or []
    base = {
        "ready": bool(turn.get("ready")),
        "analytical_goal_count": len(brief.get("questions") or []),
        "native_acquisition_count": len(turn.get("native_results") or []),
        "p17_owner_call_count": sum(1 for item in owner_calls if item == "P17"),
        "requirement_complete": completion.get("requirement_complete") is True,
        "governed_evidence_exists": any(
            turn.get("evidence_by_session", {}).values()
        ),
        "evidence_backed_candidate_count": len(evidence_backed),
        "distinct_governed_mechanism_count": len(distinct),
        "p19_assessment_exists": p19_count > 0,
        "single_root_mode_result": mode is not None,
    }
    if mode is None:
        return base
    base.update(
        {
            "mode": mode.get("mode"),
            "user_seeded_candidates": bool(
                mode.get("user_seeded_candidates")
            ),
            "analytical_reentry_count": int(
                mode.get("analytical_reentry_count") or 0
            ),
        }
    )
    if probe_id == "R_LIVE_1_ONE_PASS":
        base.update(
            {
                "expected_one_pass": mode.get("mode") == "ONE_PASS",
                "no_analytical_reentry": int(
                    mode.get("analytical_reentry_count") or 0
                )
                == 0,
                "user_candidates_preserved": bool(
                    mode.get("user_seeded_candidates")
                ),
                "multiple_candidates_reach_epistemics": len(distinct) >= 2,
                "one_analytical_obligation": len(
                    brief.get("questions") or []
                ) == 1,
                "one_initial_native_acquisition": len(
                    turn.get("native_results") or []
                ) == 1,
                "no_redundant_p17_cognition": sum(
                    1 for item in owner_calls if item == "P17"
                ) == 0,
                "all_user_must_requirements_complete": (
                    completion.get("requirement_complete") is True
                ),
            }
        )
    elif probe_id == "R_LIVE_2_ADAPTIVE":
        base.update(
            {
                "expected_adaptive": mode.get("mode") == "ADAPTIVE",
                "exactly_one_analytical_reentry": int(
                    mode.get("analytical_reentry_count") or 0
                )
                == 1,
                "user_candidates_preserved": bool(
                    mode.get("user_seeded_candidates")
                ),
                "multiple_candidates_reach_epistemics": len(distinct) >= 2,
                "one_analytical_obligation": len(
                    brief.get("questions") or []
                ) == 1,
                "initial_plus_one_discriminating_acquisition": len(
                    turn.get("native_results") or []
                ) == 2,
                "one_p17_discriminating_owner_call": sum(
                    1 for item in owner_calls if item == "P17"
                ) == 1,
                "all_user_must_requirements_complete": (
                    completion.get("requirement_complete") is True
                ),
            }
        )
    elif probe_id == "R_LIVE_3_DISCOVERY":
        base.update(
            {
                "no_user_seeded_candidates": not bool(
                    mode.get("user_seeded_candidates")
                ),
                "p17_discovery_trace_exists": bool(reasoning),
                "multiple_discovered_candidates": len(distinct) >= 2,
            }
        )
    return base


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


def _mechanical_verdict(report: dict[str, Any]) -> str:
    if report.get("exception") is not None:
        return "FAIL"
    if report.get("provider_receipt_error") is not None:
        return "FAIL"
    if report.get("within_orchestration_boundary_budget") is not True:
        return "FAIL"
    turns = report.get("turns") or []
    if (
        report.get("turn_count_executed") != report.get("turn_count_expected")
        or not turns
        or not all(item.get("ready") is True for item in turns)
    ):
        return "FAIL"
    provider = report.get("provider_receipt") or {}
    if provider:
        if int(provider.get("blocked_request_count") or 0) != 0:
            return "FAIL"
        actual = int(report.get("actual_provider_request_count") or 0)
        ceiling = int(report.get("hard_provider_request_ceiling") or 0)
        if actual > ceiling:
            return "FAIL"
        if report.get("probe_id") == "R_LIVE_1_ONE_PASS" and actual >= ceiling:
            return "FAIL"
    observations = report.get("mechanical_observations") or {}
    boolean_checks = [
        value
        for value in observations.values()
        if isinstance(value, bool)
    ]
    if boolean_checks and not all(boolean_checks):
        return "FAIL"
    return "PASS"


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
    ap.add_argument("--checkout-sha", required=True)
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
        "checkout_sha": args.checkout_sha,
        "candidate_product_sha": args.candidate_product_sha,
        "engine_sha": args.engine_sha,
        "engine_runtime_tag": args.runtime_tag,
        "model_topology": {
            "dima_cognition": MODEL,
            "metabot": METABOT_MODEL,
            "policy": "phase1-luna-default-no-cascade",
        },
        "max_orchestration_boundary_units": MAX_ORCHESTRATION_BOUNDARY_UNITS,
        "binding_manifest": binding_manifest,
        "probe_contract": {
            "historical_round2_case_id": PROBES[args.probe_id][
                "historical_round2_case_id"
            ],
            "manual_contract": list(PROBES[args.probe_id]["manual_contract"]),
            "historical_manual_score_scale": HISTORICAL_MANUAL_SCORE_SCALE,
            "scoring_authority": "MANUAL_ARTIFACT_ADJUDICATION_ONLY",
        },
        "turn_count_expected": len(PROBES[args.probe_id]["turns"]),
        "turns": [],
        "manual_adjudication_required": True,
        "mechanical_verdict": "PENDING",
        "manual_quality_status": "PENDING",
        "manual_quality_score": None,
        # Historical compatibility field; never populated automatically.
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
                reports=p20,
                reasoning=reasoning,
                orchestrator=orchestrator,
                db_engine=db_engine,
                native_token=token,
                transports=transports,
            )
            report["turns"].append(record)
            if record.get("composition_exception") is not None:
                report["exception"] = record["composition_exception"]
            if not record.get("ready"):
                break

        if (
            args.probe_id == "SCOPE_CURRENTNESS_HARD_V4"
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
            args.probe_id
            in {
                "R_LIVE_1_ONE_PASS",
                "R_LIVE_2_ADAPTIVE",
                "R_LIVE_3_DISCOVERY",
            }
            and report["turns"]
        ):
            report["mechanical_observations"] = _mechanical_r_live(
                args.probe_id,
                report["turns"][0],
            )
        elif (
            args.probe_id == "RCA_P19_HARD_V2"
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
        report["model_ceiling_events"] = _model_ceiling_events(report)

    report["mechanical_verdict"] = _mechanical_verdict(report)
    # Product quality remains human authority even when mechanics pass.
    report["manual_quality_status"] = "PENDING"
    report["manual_quality_score"] = None

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
                "model_ceiling_event_count": len(
                    report.get("model_ceiling_events") or []
                ),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
