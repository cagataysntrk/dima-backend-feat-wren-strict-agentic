from __future__ import annotations

import json
from uuid import UUID

import httpx
import pytest

from app.v3.product.contracts import ProductErrorCode
from app.v3.product.errors import ProductError
from app.v3.product.service import HeadlessProductService, ProductSources
from app.v3.research_contracts import (
    ResearchBrief,
    ResearchBriefStatus,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchQuestion,
    ResearchScope,
    ResearchSemanticRef,
    SemanticTargetKind,
)
from app.v3.research_intake import (
    AllowedRelationship,
    ResearchIntakeCatalog,
    ResearchIntakeCompiler,
    ResearchIntakeError,
    ResearchIntakeTerminal,
)
from app.v3.structured_transport import (
    OpenRouterStructuredJSONTransport,
    strict_json_schema,
)
from control_plane.authorize import Principal


TENANT = UUID("00000000-0000-4000-8000-000000006701")
USER = UUID("00000000-0000-4000-8000-000000006702")


def principal(*, user: str | None = None):
    return Principal(
        user_id=str(USER) if user is None else user,
        tenant_id=str(TENANT),
        roles=["analyst"],
        tenant_slug="core-b-live",
    )


def metric(cid: str, name: str) -> ResearchSemanticRef:
    return ResearchSemanticRef(
        source_mention=name,
        candidate_id=cid,
        target_kind=SemanticTargetKind.METRIC,
        canonical_name=name,
        cube_names=("machine_operations",),
    )


def dimension(cid: str, name: str) -> ResearchSemanticRef:
    return ResearchSemanticRef(
        source_mention=name,
        candidate_id=cid,
        target_kind=SemanticTargetKind.DIMENSION,
        canonical_name=name,
        cube_names=("machine_operations",),
    )


def catalog() -> ResearchIntakeCatalog:
    return ResearchIntakeCatalog(
        context_version="ctx-core-b-neutral-v1",
        semantic_refs=(
            metric("metric.downtime", "Machine Downtime Minutes"),
            metric("metric.fault_count", "Fault Count"),
            metric("metric.performance", "Performance Score"),
            dimension("dimension.department", "Department"),
            dimension("dimension.event_date", "Event Date"),
            dimension("dimension.machine_id", "Machine"),
        ),
        allowed_relationships=(
            AllowedRelationship(
                relationship_id="rel.downtime_fault_by_department",
                left_semantic_id="metric.downtime",
                right_semantic_id="metric.fault_count",
                dimension_semantic_id="dimension.department",
            ),
            AllowedRelationship(
                relationship_id="rel.downtime_performance_by_department",
                left_semantic_id="metric.downtime",
                right_semantic_id="metric.performance",
                dimension_semantic_id="dimension.department",
            ),
        ),
        supported_domains=("machine_operations",),
    )


class FakeTransport:
    def __init__(self, payload: dict):
        self.payload = payload
        self.calls: list[dict] = []
        self.call_count = 0

    def structured_json(self, system, user, *, schema, schema_name):
        self.call_count += 1
        self.calls.append(
            {
                "system": system,
                "user": json.loads(user),
                "schema": schema,
                "schema_name": schema_name,
            }
        )
        return json.dumps(self.payload)


def ready_payload(
    *,
    kind="breakdown",
    subject=("metric.downtime",),
    related=("dimension.department",),
):
    return {
        "terminal": "READY",
        "objective": "Inspect the current governed analytical request.",
        "goals": [
            {
                "goal_key": "g-current",
                "kind": kind,
                "source_text": "Inspect the requested governed analytical scope.",
                "subject_semantic_ids": list(subject),
                "related_semantic_ids": list(related),
                "ranking": None,
                "comparison_texts": [],
            }
        ],
        "deliverables": [],
        "time_surfaces": [],
        "required_domains": ["machine_operations"],
        "clarification_question": None,
        "unsupported_reason": None,
    }


def test_ready_breakdown_compiles_to_typed_research_brief():
    transport = FakeTransport(ready_payload())
    compiler = ResearchIntakeCompiler(transport=transport)
    result = compiler.compile(
        question="Show machine downtime by department.",
        catalog=catalog(),
    )
    assert result.terminal == ResearchIntakeTerminal.READY
    assert result.model_calls == 1
    assert result.brief is not None
    brief = result.brief
    assert brief.status == ResearchBriefStatus.READY_FOR_RESEARCH
    assert len(brief.questions) == 1
    question = brief.questions[0]
    assert question.kind == ResearchGoalKind.BREAKDOWN
    assert question.subject_refs[0].candidate_id == "metric.downtime"
    assert question.related_refs[0].candidate_id == "dimension.department"
    assert brief.must_requirement_ids == (question.goal_id,)


def test_authorized_relationship_compiles_and_preserves_exact_catalog_refs():
    payload = ready_payload(
        kind="relationship",
        subject=("metric.downtime", "metric.fault_count"),
        related=("dimension.department",),
    )
    result = ResearchIntakeCompiler(
        transport=FakeTransport(payload)
    ).compile(
        question="Inspect downtime and fault count by department.",
        catalog=catalog(),
    )
    assert result.brief is not None
    refs = {
        item.candidate_id
        for item in (
            *result.brief.questions[0].subject_refs,
            *result.brief.questions[0].related_refs,
        )
    }
    assert refs == {
        "metric.downtime",
        "metric.fault_count",
        "dimension.department",
    }


def test_unapproved_relationship_fails_closed():
    payload = ready_payload(
        kind="relationship",
        subject=("metric.fault_count", "metric.performance"),
        related=("dimension.department",),
    )
    with pytest.raises(ResearchIntakeError) as exc:
        ResearchIntakeCompiler(
            transport=FakeTransport(payload)
        ).compile(
            question="Inspect an unapproved relationship.",
            catalog=catalog(),
        )
    assert exc.value.code == "INTAKE_RELATIONSHIP_UNAUTHORIZED"


def test_unknown_semantic_ref_fails_closed():
    payload = ready_payload(subject=("metric.not_in_catalog",))
    with pytest.raises(ResearchIntakeError) as exc:
        ResearchIntakeCompiler(
            transport=FakeTransport(payload)
        ).compile(
            question="Use an unknown metric.",
            catalog=catalog(),
        )
    assert exc.value.code == "INTAKE_UNKNOWN_SEMANTIC_REF"


@pytest.mark.parametrize(
    ("payload", "terminal", "field"),
    [
        (
            {
                "terminal": "CLARIFY",
                "objective": None,
                "goals": [],
                "deliverables": [],
                "time_surfaces": [],
                "required_domains": [],
                "clarification_question": "Which metric do you mean?",
                "unsupported_reason": None,
            },
            ResearchIntakeTerminal.CLARIFY,
            "clarification_question",
        ),
        (
            {
                "terminal": "UNSUPPORTED",
                "objective": None,
                "goals": [],
                "deliverables": [],
                "time_surfaces": [],
                "required_domains": [],
                "clarification_question": None,
                "unsupported_reason": "Requested fact is absent from governed data.",
            },
            ResearchIntakeTerminal.UNSUPPORTED,
            "unsupported_reason",
        ),
    ],
)
def test_bounded_non_executable_terminal_states(payload, terminal, field):
    result = ResearchIntakeCompiler(
        transport=FakeTransport(payload)
    ).compile(
        question="A request that cannot legally enter analytics.",
        catalog=catalog(),
    )
    assert result.terminal == terminal
    assert result.brief is None
    assert getattr(result, field)


def prior_brief() -> ResearchBrief:
    downtime = catalog().semantic_refs[0]
    faults = catalog().semantic_refs[1]
    dept = catalog().semantic_refs[3]
    q1 = ResearchQuestion(
        goal_id="g_prior_downtime",
        kind=ResearchGoalKind.BREAKDOWN,
        source_text="Prior downtime obligation.",
        subject_refs=(downtime,),
        related_refs=(dept,),
        status=ResearchGoalStatus.RESOLVED,
    )
    q2 = ResearchQuestion(
        goal_id="g_prior_faults",
        kind=ResearchGoalKind.BREAKDOWN,
        source_text="Prior fault obligation.",
        subject_refs=(faults,),
        related_refs=(dept,),
        status=ResearchGoalStatus.RESOLVED,
    )
    return ResearchBrief(
        brief_id="rb_prior",
        objective="Prior combined request.",
        scope=ResearchScope(semantic_refs=(downtime, faults, dept)),
        questions=(q1, q2),
        must_requirement_ids=(q1.goal_id, q2.goal_id),
        context_version="ctx-core-b-neutral-v1",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )


def test_explicit_repair_does_not_restore_removed_prior_obligation():
    transport = FakeTransport(ready_payload())
    result = ResearchIntakeCompiler(
        transport=transport
    ).compile(
        question=(
            "Correction: include downtime only; exclude fault count "
            "from the current request."
        ),
        catalog=catalog(),
        prior_brief=prior_brief(),
    )
    assert result.brief is not None
    refs = {
        ref.candidate_id
        for question in result.brief.questions
        for ref in (*question.subject_refs, *question.related_refs)
    }
    assert "metric.downtime" in refs
    assert "metric.fault_count" not in refs
    sent = transport.calls[0]["user"]
    assert sent["prior_brief"]["brief_id"] == "rb_prior"
    assert "CURRENT intent only" in sent["instruction"]


def test_intake_schema_is_strict_for_every_object():
    schema = strict_json_schema(
        __import__(
            "app.v3.research_intake",
            fromlist=["ModelResearchBriefDraft"],
        ).ModelResearchBriefDraft
    )

    def visit(node):
        if isinstance(node, dict):
            if node.get("type") == "object":
                assert node.get("additionalProperties") is False
                props = node.get("properties") or {}
                assert set(node.get("required") or ()) == set(props)
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for value in node:
                visit(value)

    visit(schema)


def test_openrouter_transport_uses_strict_json_schema_without_model_cascade():
    seen = {}

    def handler(request: httpx.Request):
        seen["url"] = str(request.url)
        seen["auth"] = request.headers["Authorization"]
        seen["payload"] = json.loads(request.content)
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(ready_payload())
                        }
                    }
                ]
            },
        )

    transport = OpenRouterStructuredJSONTransport(
        api_key="secret-test-key",
        model="openai/gpt-5.6-luna",
        transport=httpx.MockTransport(handler),
    )
    with transport:
        raw = transport.structured_json(
            "system",
            "user",
            schema={"type": "object", "properties": {}, "additionalProperties": False},
            schema_name="test_schema",
        )
    assert json.loads(raw)["terminal"] == "READY"
    assert transport.call_count == 1
    assert seen["url"] == "https://openrouter.ai/api/v1/chat/completions"
    assert seen["auth"] == "Bearer secret-test-key"
    payload = seen["payload"]
    assert payload["model"] == "openai/gpt-5.6-luna"
    assert payload["provider"] == {"require_parameters": True}
    assert payload["reasoning"] == {"enabled": False}
    assert payload["response_format"]["type"] == "json_schema"
    assert "temperature" not in payload
    assert "secret-test-key" not in json.dumps(payload)


def test_headless_product_checks_principal_before_paid_intake_call():
    transport = FakeTransport(ready_payload())
    compiler = ResearchIntakeCompiler(transport=transport)
    service = HeadlessProductService(
        sources=ProductSources(
            research=object(),  # not used by this bounded product seam
            intake=compiler,
        )
    )
    with pytest.raises(ProductError) as exc:
        service.research_question(
            question="Show downtime.",
            catalog=catalog(),
            principal=principal(user=""),
        )
    assert exc.value.code == ProductErrorCode.FORBIDDEN
    assert transport.call_count == 0


def test_headless_product_delegates_raw_question_to_intake_owner():
    transport = FakeTransport(ready_payload())
    service = HeadlessProductService(
        sources=ProductSources(
            research=object(),
            intake=ResearchIntakeCompiler(transport=transport),
        )
    )
    result = service.research_question(
        question="Show downtime by department.",
        catalog=catalog(),
        principal=principal(),
    )
    assert result.terminal == ResearchIntakeTerminal.READY
    assert result.brief is not None
    assert transport.call_count == 1
