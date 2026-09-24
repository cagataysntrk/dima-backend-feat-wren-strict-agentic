"""Manual-only D10-G17/G18 integrated Product-MVP paid harness.

IMPORTANT:
- Building/importing this file performs ZERO provider calls.
- The workflow that invokes it is workflow_dispatch-only.
- Exactly one initial Product turn is allowed. A second turn is allowed only as the
  signed section continuation of an initial GREEN report. There is no third turn.
- Role and global call ceilings are enforced BEFORE forwarding each provider request.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Seal the supervised paid topology before constructing settings/providers.
FAST_MODEL = os.environ.get("DIMA_V2_FAST_LANGUAGE_MODEL") or "google/gemini-2.5-flash-lite"
RESEARCH_MODEL = "openai/gpt-5.6-sol"
SEMANTIC_MODEL = "openai/gpt-5.6-luna"
TEMPORAL_MODEL = "openai/gpt-5.6-sol"
NARRATOR_MODEL = "openai/gpt-5.6-sol"

os.environ["DIMA_LLM_PROVIDER"] = "openrouter"
os.environ["DIMA_V2_FAST_LANGUAGE_PROVIDER"] = "openrouter"
os.environ["DIMA_V2_FAST_LANGUAGE_MODEL"] = FAST_MODEL
os.environ["DIMA_V2_RESEARCH_MANAGER_PROVIDER"] = "openrouter"
os.environ["DIMA_V2_RESEARCH_MANAGER_MODEL"] = RESEARCH_MODEL
os.environ["DIMA_V2_SEMANTIC_LINKER_PROVIDER"] = "openrouter"
os.environ["DIMA_V2_SEMANTIC_LINKER_MODEL"] = SEMANTIC_MODEL
os.environ["DIMA_V2_TEMPORAL_NORMALIZER_PROVIDER"] = "openrouter"
os.environ["DIMA_V2_TEMPORAL_NORMALIZER_MODEL"] = TEMPORAL_MODEL
os.environ.setdefault("DIMA_VQR_EMBEDDER", "off")
os.environ.setdefault("DIMA_SCHEDULER_ENABLED", "false")
os.environ.setdefault("DIMA_INTERACTION_LOG", "false")

from app.config import get_settings
from app.contracts import ContractStore
from app.llm import build_generator
from app.v2.context_provider import ContextProviderV0
from app.v2.model_policy import ModelProfile, ModelRole, ModelRolePolicy
from app.v2.models import TenantAnalyticsRuntimeV0
from app.v2.product_coordinator import ProductCoordinator
from app.v2.product_events import ProductEventSink
from app.v2.product_models import (
    ProductAskRequest,
    ProductEventKind,
    ProductLane,
    ProductRequestContext,
    ProductStatus,
    mint_product_turn_ref,
)
from app.v2.research_lane import ResearchCognition, ResearchLaneService
from app.v2.report_builder import ReportBlockKind
from app.v2.report_narration import ReportNarrator
from app.v2.semantic_linker import StructuredSemanticCandidateDecisionProvider
from app.v2.standard_lane import StandardLaneEngine
from app.v2.temporal_intent import StructuredTemporalNormalizationProvider
from app.wren_service import WrenService
from control_plane.authorize import Principal


SCOPE = "CANONICAL_NS4"
MAX_HARNESS_TOTAL_CALLS = 20
ROLE_LIMITS = {
    "FAST_LANGUAGE": 2,
    "RESEARCH_MANAGER": 12,
    "SEMANTIC_LINKER": 3,
    "TEMPORAL_NORMALIZER": 1,
    "REPORT_NARRATOR": 2,
}
MAX_PRODUCT_TURNS = 2

INITIAL_QUESTION = (
    "Makine duruşları, arıza sayısı ve bölüm bazındaki performansı birlikte araştır. "
    "Aralarındaki governed ilişkiyi kontrol et; doğrulanmış sonuçlar yeni bir maddi "
    "kırılıma işaret ederse onu takip et; gözlenen bozulma için olası kök nedenleri "
    "ayrı governed testlerle sınırla ve yönetim için kanıta bağlı bir rapor üret. "
    "Nedensel kesinlik iddia etme."
)
CONTINUATION_QUESTION = (
    "Yalnızca imzalı bu rapor bölümünün governed kapsamını daha derinleştir. "
    "Yeni doğrulanmış kanıt gerekiyorsa mevcut trust plane üzerinden araştır; "
    "önceki raporu mutate etmeden yeni sürüm üret."
)


class PaidHarnessError(RuntimeError):
    def __init__(self, message: str, *, diagnostics: dict[str, Any] | None = None):
        super().__init__(message)
        self.diagnostics = diagnostics or {}


class PaidBudgetExceeded(PaidHarnessError):
    pass


_CAPTURED_DIAGNOSTIC_SCHEMAS = {
    "dima_standard_intent_draft_v1",
    "dima_standard_coverage_v1",
    "dima_intent_draft_v1",
    "dima_intent_coverage_v1",
    "dima_bounded_semantic_link_v1",
}


def _json_safe(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    try:
        json.dumps(value)
        return value
    except TypeError:
        return repr(value)


@dataclass
class RoleCallBudget:
    max_total: int
    role_limits: dict[str, int]
    calls: list[dict[str, Any]] = field(default_factory=list)

    def reserve(
        self,
        *,
        role: str,
        model: str,
        schema_name: str | None,
    ) -> None:
        role_limit = self.role_limits[role]
        role_count = sum(1 for item in self.calls if item["role"] == role)
        if role_count >= role_limit:
            raise PaidBudgetExceeded(
                f"{role} paid-call ceiling exhausted ({role_count}/{role_limit})"
            )
        if len(self.calls) >= self.max_total:
            raise PaidBudgetExceeded(
                f"global paid-call ceiling exhausted ({len(self.calls)}/{self.max_total})"
            )
        self.calls.append(
            {
                "sequence": len(self.calls) + 1,
                "role": role,
                "model": model,
                "schema_name": schema_name,
                "reserved_at_ms": int(time.monotonic() * 1000),
            }
        )

    def receipt(self) -> dict[str, Any]:
        return {
            "total": len(self.calls),
            "max_total": self.max_total,
            "role_limits": dict(self.role_limits),
            "by_role": {
                role: sum(1 for item in self.calls if item["role"] == role)
                for role in self.role_limits
            },
            "calls": list(self.calls),
        }


class CountingStructured:
    """Reserve paid budget before each provider request; never cascade/fallback."""

    def __init__(
        self,
        *,
        inner,
        budget: RoleCallBudget,
        role: str,
        model: str,
        captured_outputs: list[dict[str, Any]] | None = None,
    ) -> None:
        self._inner = inner
        self._budget = budget
        self._role = role
        self._model = model
        self._captured_outputs = captured_outputs

    def __getattr__(self, name: str):
        return getattr(self._inner, name)

    def structured_json(self, *args, **kwargs):
        schema_name = kwargs.get("schema_name")
        self._budget.reserve(
            role=self._role,
            model=self._model,
            schema_name=schema_name,
        )
        result = self._inner.structured_json(*args, **kwargs)
        if (
            self._captured_outputs is not None
            and schema_name in _CAPTURED_DIAGNOSTIC_SCHEMAS
        ):
            self._captured_outputs.append(
                {
                    "sequence": len(self._budget.calls),
                    "role": self._role,
                    "model": self._model,
                    "schema_name": schema_name,
                    "validated_output": _json_safe(result),
                }
            )
        return result


class CapturingStandardLane(StandardLaneEngine):
    """Eval-only Standard outcome capture; delegates all Product behavior unchanged."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_outcome = None

    def run(self, **kwargs):
        outcome = super().run(**kwargs)
        self.last_outcome = outcome
        return outcome


class CapturingResearchLane(ResearchLaneService):
    """Eval-only observation seam; does not alter Research authority."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_result = None

    def run(self, **kwargs):
        result = super().run(**kwargs)
        self.last_result = result
        return result

    def continue_run(self, **kwargs):
        result = super().continue_run(**kwargs)
        self.last_result = result
        return result


class CountingWren:
    def __init__(self, inner) -> None:
        self._inner = inner
        self.query_calls = 0
        self.dry_plan_calls = 0
        self.cube_sql_calls = 0

    def __getattr__(self, name: str):
        return getattr(self._inner, name)

    def schema(self):
        return self._inner.schema()

    def cube_sql(self, cube_query: dict) -> str:
        self.cube_sql_calls += 1
        return self._inner.cube_sql(cube_query)

    def dry_plan(self, sql: str, *, principal=None):
        self.dry_plan_calls += 1
        return self._inner.dry_plan(sql, principal=principal)

    def query(self, sql: str, limit=None, *, principal=None):
        self.query_calls += 1
        return self._inner.query(sql, limit=limit, principal=principal)


def _profile(policy: ModelRolePolicy, role: ModelRole, expected_model: str):
    scoped, profile = policy.scoped_settings(role, model_override=expected_model)
    if profile.provider != "openrouter" or profile.model != expected_model:
        raise PaidHarnessError(
            f"unexpected {role.value} topology: {profile.provider}/{profile.model}"
        )
    return scoped, profile


def _build_product(
    *,
    settings,
    budget: RoleCallBudget,
    service: CountingWren,
    principal: Principal,
):
    policy = ModelRolePolicy(settings)
    structured_outputs: list[dict[str, Any]] = []

    fast_settings, fast_profile = _profile(
        policy,
        ModelRole.FAST_LANGUAGE,
        FAST_MODEL,
    )
    research_settings, research_profile = _profile(
        policy,
        ModelRole.RESEARCH_MANAGER,
        RESEARCH_MODEL,
    )
    semantic_settings, semantic_profile = _profile(
        policy,
        ModelRole.SEMANTIC_LINKER,
        SEMANTIC_MODEL,
    )
    temporal_settings, temporal_profile = _profile(
        policy,
        ModelRole.TEMPORAL_NORMALIZER,
        TEMPORAL_MODEL,
    )

    fast = CountingStructured(
        inner=build_generator(fast_settings),
        budget=budget,
        role="FAST_LANGUAGE",
        model=fast_profile.model,
        captured_outputs=structured_outputs,
    )
    manager = CountingStructured(
        inner=build_generator(research_settings),
        budget=budget,
        role="RESEARCH_MANAGER",
        model=research_profile.model,
        captured_outputs=structured_outputs,
    )
    semantic = CountingStructured(
        inner=build_generator(semantic_settings),
        budget=budget,
        role="SEMANTIC_LINKER",
        model=semantic_profile.model,
        captured_outputs=structured_outputs,
    )
    temporal = CountingStructured(
        inner=build_generator(temporal_settings),
        budget=budget,
        role="TEMPORAL_NORMALIZER",
        model=temporal_profile.model,
    )
    narrator = CountingStructured(
        inner=build_generator(research_settings),
        budget=budget,
        role="REPORT_NARRATOR",
        model=NARRATOR_MODEL,
    )

    semantic_provider = StructuredSemanticCandidateDecisionProvider(
        structured=semantic.structured_json
    )
    temporal_provider = StructuredTemporalNormalizationProvider(
        structured=temporal.structured_json
    )
    standard_lane = CapturingStandardLane(
        intent_structured=fast.structured_json,
        coverage_structured=fast.structured_json,
        semantic_provider=semantic_provider,
        temporal_provider=temporal_provider,
    )
    research_lane = CapturingResearchLane(
        cognition=ResearchCognition(
            manager_llm=manager,
            manager_profile=research_profile,
            semantic_provider=semantic_provider,
            semantic_profile=semantic_profile,
            temporal_provider=temporal_provider,
            temporal_profile=temporal_profile,
        )
    )
    coordinator = ProductCoordinator(
        standard_lane=standard_lane,
        standard_model_role=fast_profile.role.value,
        research_lane=research_lane,
        report_narrator=ReportNarrator(
            llm=narrator,
            provider="openrouter",
            model=NARRATOR_MODEL,
        ),
    )

    schema = service.schema()
    runtime = TenantAnalyticsRuntimeV0(
        tenant_id=str(principal.tenant_id),
        tenant_slug=principal.tenant_slug,
        principal_user_id=str(principal.user_id),
        roles=tuple(str(role) for role in principal.roles),
        mdl_version=str(service.mdl_version),
        catalog=str(schema.get("catalog") or "wren"),
        schema_name=str(schema.get("schema_name") or schema.get("schema") or "public"),
        db_online=bool(schema.get("db_online", True)),
    )
    semantic_context = ContextProviderV0().build(service, runtime)
    contract_store = ContractStore()

    def bind_context(*, request, body, principal, turn_ref=None):
        return ProductRequestContext(
            request_ref="r-live-" + str(time.time_ns()),
            tenant_binding=f"id:{runtime.tenant_id}",
            principal=principal,
            tenant_runtime=runtime,
            service=service,
            schema=schema,
            semantic_context=semantic_context,
            contract_store=contract_store,
            session_id=body.session_id,
            thread_id=body.thread_id,
            turn_ref=turn_ref or mint_product_turn_ref(),
        )

    coordinator._bind_context = bind_context
    return coordinator, research_lane, standard_lane, structured_outputs


def _value(value: Any) -> Any:
    return getattr(value, "value", value)


def _diagnostic_snapshot(
    *,
    product,
    standard_lane: CapturingStandardLane,
    research_lane: CapturingResearchLane,
    budget: RoleCallBudget,
    service: CountingWren,
    structured_outputs: list[dict[str, Any]],
) -> dict[str, Any]:
    standard = standard_lane.last_outcome
    product_receipt = getattr(product, "terminal_receipt", None)
    product_data = None
    if product is not None:
        product_data = {
            "lane": _value(getattr(product, "lane", None)),
            "status": _value(getattr(product, "status", None)),
            "turn_ref": getattr(product, "turn_ref", None),
            "terminal_status": getattr(product_receipt, "terminal_status", None),
            "terminal_reasons": list(getattr(product_receipt, "reasons", ()) or ()),
            "events": [
                _json_safe(item)
                for item in (getattr(product, "events", ()) or ())
            ],
        }

    standard_data = None
    if standard is not None:
        standard_data = {
            "status": _value(standard.status),
            "reasons": list(standard.reasons),
            "attempts": standard.attempts,
            "coverage_status": standard.coverage_status,
            "work_mode": _value(standard.work_mode) if standard.work_mode is not None else None,
            "obligation_capability_keys": [
                _value(item.capability_key)
                for item in standard.obligations
            ],
            "obligation_polarities": [
                _value(item.polarity)
                for item in standard.obligations
            ],
        }

    research = research_lane.last_result
    research_data = None
    if research is not None:
        research_data = {
            "preacceptance_status": _value(research.outcome.preacceptance_status),
            "observations": [
                _json_safe(item)
                for item in (research.outcome.observations or ())
                if isinstance(item, dict)
                and item.get("kind")
                in {
                    "intent_draft",
                    "grounding",
                    "material_grounding_gap",
                    "coverage_audit",
                    "contract_validity",
                    "draft_source_contract",
                    "grounding_error",
                }
            ],
            "accepted_contract": _json_safe(research.accepted_contract),
            "ledger": _json_safe(research.ledger),
            "semantic_resolution_receipts": [
                _json_safe(item)
                for item in research.runtime.semantic_resolution_receipts
            ],
        }

    return {
        "product": product_data,
        "standard": standard_data,
        "research": research_data,
        "model_calls": budget.receipt(),
        "structured_outputs": list(structured_outputs),
        "wren": {
            "query_calls": service.query_calls,
            "dry_plan_calls": service.dry_plan_calls,
            "cube_sql_calls": service.cube_sql_calls,
        },
    }


def _event_metrics(events) -> dict[str, int | None]:
    elapsed = [item.elapsed_ms for item in events]
    first_status = next(
        (item.elapsed_ms for item in events if item.kind == ProductEventKind.REQUEST_ACCEPTED),
        None,
    )
    first_evidence = next(
        (item.elapsed_ms for item in events if item.kind == ProductEventKind.EVIDENCE_VERIFIED),
        None,
    )
    report_ready = next(
        (item.elapsed_ms for item in events if item.kind == ProductEventKind.REPORT_READY),
        None,
    )
    gaps = [
        later - earlier
        for earlier, later in zip(elapsed, elapsed[1:])
    ]
    return {
        "first_status_ms": first_status,
        "first_verified_evidence_ms": first_evidence,
        "max_progress_silence_ms": max(gaps, default=0),
        "report_ready_ms": report_ready,
    }


def _candidate_section_token(response) -> str:
    if response.report is None:
        raise PaidHarnessError("initial Product turn produced no report")
    candidate_sections = {
        section.section_id
        for section in response.report.report.sections
        if any(
            block.block_kind == ReportBlockKind.ROOT_CAUSE
            for block in section.blocks
        )
    }
    if len(candidate_sections) != 1:
        raise PaidHarnessError(
            "signed continuation requires exactly one typed ROOT_CAUSE report section"
        )
    target = next(iter(candidate_sections))
    tokens = [
        item.token
        for item in response.section_continuations
        if item.section_ref == target
    ]
    if len(tokens) != 1:
        raise PaidHarnessError(
            "ROOT_CAUSE section must expose exactly one signed continuation token"
        )
    return tokens[0]


def run_paid(*, scope: str, max_total_model_calls: int) -> dict[str, Any]:
    if scope != SCOPE:
        raise PaidHarnessError(
            f"explicit scope must be {SCOPE}; blank/unknown scope never expands to all"
        )
    if not (1 <= max_total_model_calls <= MAX_HARNESS_TOTAL_CALLS):
        raise PaidHarnessError(
            f"max_total_model_calls must be 1..{MAX_HARNESS_TOTAL_CALLS}"
        )

    settings = get_settings()
    inner = WrenService(
        project_dir=settings.resolved_project_dir(),
        datasource=settings.datasource,
        connection_info=settings.connection_dict(),
    )
    service = CountingWren(inner)
    budget = RoleCallBudget(
        max_total=max_total_model_calls,
        role_limits=ROLE_LIMITS,
    )
    principal = Principal(
        user_id="day10-paid-user",
        tenant_id="day10-paid-tenant",
        roles=["owner"],
        tenant_slug="demo-boyahane",
    )
    coordinator, research_lane, standard_lane, structured_outputs = _build_product(
        settings=settings,
        budget=budget,
        service=service,
        principal=principal,
    )

    current_response = None

    def _fail(message: str) -> None:
        raise PaidHarnessError(
            message,
            diagnostics=_diagnostic_snapshot(
                product=current_response,
                standard_lane=standard_lane,
                research_lane=research_lane,
                budget=budget,
                service=service,
                structured_outputs=structured_outputs,
            ),
        )

    session_id = "day10-paid-product"
    thread_id = "day10-paid-product"
    turn_count = 0
    started = time.monotonic()

    initial_turn_ref = mint_product_turn_ref()
    try:
        initial = coordinator.handle(
            request=object(),
            body=ProductAskRequest(
                question=INITIAL_QUESTION,
                session_id=session_id,
                thread_id=thread_id,
            ),
            principal=principal,
            event_sink=ProductEventSink(
                request_ref="paid-initial",
                turn_ref=initial_turn_ref,
            ),
            turn_ref=initial_turn_ref,
        )
    except Exception as exc:
        current_response = None
        _fail(f"initial Product execution failed: {type(exc).__name__}: {exc}")
        raise AssertionError("unreachable")
    current_response = initial
    turn_count += 1

    if initial.lane != ProductLane.RESEARCH:
        _fail(
            f"canonical Product scenario must route to RESEARCH, got {initial.lane.value}"
        )
    if initial.status != ProductStatus.REPORT:
        _fail(
            f"initial Product turn is not GREEN REPORT: {initial.status.value}"
        )
    if not initial.terminal_receipt.verified_complete:
        _fail("initial Product report is not CompletionGate-verified")
    if initial.report is None or initial.narration is None:
        _fail("initial Product report/narration missing")
    initial_research = research_lane.last_result
    if initial_research is None:
        _fail("initial Research authority receipt missing")

    initial_evidence = len(initial.evidence_refs)
    initial_artifacts = len(initial.artifact_refs)
    if initial_evidence < 4:
        _fail(
            f"canonical scenario requires >=4 Evidence-producing analytical steps; got {initial_evidence}"
        )
    if initial_artifacts < 3:
        _fail(
            f"canonical scenario requires >=3 meaningful artifacts; got {initial_artifacts}"
        )
    if not any(
        block.block_kind == ReportBlockKind.ROOT_CAUSE
        for section in initial.report.report.sections
        for block in section.blocks
    ):
        _fail("canonical report contains no ROOT_CAUSE block")

    observations = tuple(initial_research.outcome.observations)
    observation_kinds = {
        str(item.get("kind"))
        for item in observations
        if isinstance(item, dict)
    }
    required_root_chain = {
        "adaptive_branch_executed",
        "hypothesis_registered",
        "hypothesis_next_test_executed",
        "hypothesis_relation_admitted",
        "root_cause_obligation_reconciled",
    }
    missing_root_chain = required_root_chain - observation_kinds
    if missing_root_chain:
        _fail(
            "integrated Day8 root debt was not genuinely exercised: "
            + ", ".join(sorted(missing_root_chain))
        )
    if not initial_research.findings:
        _fail("integrated root path produced no canonical Finding")
    if not any(
        finding.epistemic_label.value == "CANDIDATE_CAUSE"
        for finding in initial_research.findings
    ):
        _fail("integrated root path produced no CANDIDATE_CAUSE Finding")
    root_items = [
        item
        for item in initial_research.ledger.active_user_must
        if item.capability_key.value == "root_cause"
    ]
    if len(root_items) != 1 or root_items[0].status.value != "VERIFIED":
        _fail(
            "ROOT_CAUSE USER_MUST is not terminal/accounted as bounded investigation"
        )

    event_kinds = {item.kind for item in initial.events}
    if ProductEventKind.ADAPTIVE_BRANCH_OPENED not in event_kinds:
        _fail("canonical paid scenario did not execute adaptive branch")
    if ProductEventKind.RELATIONSHIP_CHECKED not in event_kinds:
        _fail("canonical paid scenario did not execute relationship analysis")

    accepted_adapt = [
        item
        for item in initial_research.accepted_contract.research_directives
        if item.directive_type.value == "ADAPT_ON_EVIDENCE"
    ]
    dispositions = {
        item.directive_id: item
        for item in initial_research.runtime.directive_dispositions
    }
    if len(accepted_adapt) != 1:
        _fail(
            f"canonical paid scenario requires exactly one ADAPT_ON_EVIDENCE directive; "
            f"got {len(accepted_adapt)}"
        )
    adapt_disposition = dispositions.get(accepted_adapt[0].directive_id)
    if adapt_disposition is None or adapt_disposition.status.value != "APPLIED":
        _fail(
            "canonical paid adaptive directive was not accounted by governed branch"
        )
    if not adapt_disposition.evidence_ref or not adapt_disposition.branch_task_refs:
        _fail(
            "canonical paid adaptive directive lacks Evidence/branch accounting proof"
        )

    try:
        token = _candidate_section_token(initial)
    except PaidHarnessError as exc:
        _fail(str(exc))
        raise AssertionError("unreachable")

    continuation_turn_ref = mint_product_turn_ref()
    try:
        continuation = coordinator.handle(
            request=object(),
            body=ProductAskRequest(
                question=CONTINUATION_QUESTION,
                session_id=session_id,
                thread_id=thread_id,
                report_section_token=token,
            ),
            principal=principal,
            event_sink=ProductEventSink(
                request_ref="paid-continuation",
                turn_ref=continuation_turn_ref,
            ),
            turn_ref=continuation_turn_ref,
        )
    except Exception as exc:
        _fail(f"signed continuation execution failed: {type(exc).__name__}: {exc}")
        raise AssertionError("unreachable")
    current_response = continuation
    turn_count += 1
    if turn_count != MAX_PRODUCT_TURNS:
        _fail("paid harness must execute exactly two Product turns")
    if continuation.lane != ProductLane.RESEARCH:
        _fail("signed continuation left RESEARCH lane")
    if continuation.status != ProductStatus.REPORT:
        _fail(
            f"signed continuation did not produce report: {continuation.status.value}"
        )
    if continuation.report is None:
        _fail("signed continuation report missing")
    if continuation.report.version != initial.report.version + 1:
        _fail("continuation did not create version +1 report")
    if continuation.report.supersedes_report_ref != initial.report.report.report_id:
        _fail("continuation does not supersede initial immutable report")

    total_ms = int((time.monotonic() - started) * 1000)
    all_events = (*initial.events, *continuation.events)
    metrics = _event_metrics(all_events)
    role_receipt = budget.receipt()

    # G17/G18: no hidden third turn and no role/model drift.
    expected_models = {
        "FAST_LANGUAGE": FAST_MODEL,
        "RESEARCH_MANAGER": RESEARCH_MODEL,
        "SEMANTIC_LINKER": SEMANTIC_MODEL,
        "TEMPORAL_NORMALIZER": TEMPORAL_MODEL,
        "REPORT_NARRATOR": NARRATOR_MODEL,
    }
    for item in role_receipt["calls"]:
        if item["model"] != expected_models[item["role"]]:
            _fail(
                f"role/model drift: {item['role']} -> {item['model']}"
            )

    confirmed_cause_count = sum(
        1
        for section in initial.report.report.sections
        for block in section.blocks
        if getattr(block, "epistemic_label", None) is not None
        and block.epistemic_label.value == "CONFIRMED_CAUSE"
    )
    if confirmed_cause_count != 0:
        _fail("CONFIRMED_CAUSE remains forbidden")

    return {
        "status": "pass",
        "scope": scope,
        "product_turns": turn_count,
        "initial_status": initial.status.value,
        "continuation_status": continuation.status.value,
        "initial_turn_ref": initial.turn_ref,
        "continuation_turn_ref": continuation.turn_ref,
        "directive_id": accepted_adapt[0].directive_id,
        "directive_type": accepted_adapt[0].directive_type.value,
        "directive_final_status": adapt_disposition.status.value,
        "directive_accounting_evidence_ref": adapt_disposition.evidence_ref,
        "directive_branch_task_refs": list(adapt_disposition.branch_task_refs),
        "initial_evidence_count": initial_evidence,
        "initial_artifact_count": initial_artifacts,
        "initial_report_ref": initial.report.report.report_id,
        "continuation_report_ref": continuation.report.report.report_id,
        "initial_report_version": initial.report.version,
        "continuation_report_version": continuation.report.version,
        "manager_turns_initial": initial.terminal_receipt.manager_turns,
        "manager_turns_continuation": continuation.terminal_receipt.manager_turns,
        "tool_executions": sum(
            1 for item in all_events if item.kind == ProductEventKind.EVIDENCE_VERIFIED
        ),
        "wren_queries": service.query_calls,
        "wren_dry_plans": service.dry_plan_calls,
        "wren_cube_sql_calls": service.cube_sql_calls,
        "model_calls": role_receipt,
        "slo_sample": {
            **metrics,
            "total_ms": total_ms,
        },
        "slo_note": "single observed sample; not a p95 estimate",
        "day8_live_debt_exercised": True,
        "root_chain_observations": sorted(required_root_chain),
        "confirmed_cause_count": confirmed_cause_count,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", required=True)
    parser.add_argument("--max-total-model-calls", required=True, type=int)
    args = parser.parse_args()

    report_path = Path("lab/reports/v2_day10_product_mvp_live.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        result = run_paid(
            scope=args.scope,
            max_total_model_calls=args.max_total_model_calls,
        )
    except Exception as exc:
        result = {
            "status": "fail",
            "scope": args.scope,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "paid_harness_max_total_calls": MAX_HARNESS_TOTAL_CALLS,
            "diagnostics": getattr(exc, "diagnostics", {}),
        }
        report_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 1

    if result["confirmed_cause_count"] != 0:
        raise SystemExit("CONFIRMED_CAUSE remains forbidden in paid Product gate")

    report_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
