"""Provider-free certification for the stabilized Day 6.5 pre-acceptance protocol."""

from __future__ import annotations

from collections import deque
import json
from types import SimpleNamespace

import pytest

from app.v2.acceptance import IntentAcceptanceGate
from app.v2.manager_executor import (
    GovernedManagerExecutionContext,
    GovernedManagerExecutor,
)
from app.v2.manager_loop import ResearchManagerLoop
from app.v2.manager_models import (
    ManagerBudget,
    ManagerCapabilityKey,
    ManagerState,
    ObligationOrigin,
    ObligationPolarity,
    ObligationPriority,
    SemanticBindingRef,
    SemanticResolutionReceipt,
)
from app.v2.manager_preacceptance import (
    CoverageAudit,
    FiniteAcceptanceStatus,
    IntentDraft,
    PreAcceptanceController,
)
from app.v2.manager_progress import DynamicActionFrontier
from app.v2.manager_runtime import ManagerBudgetError, ManagerRuntime
from app.v2.manager_semantics import ManagerSemanticResolutionAdapter
from app.v2.manager_tools import (
    ResolveSemanticsArgs,
    SemanticDecompositionRepairGap,
    SemanticDecompositionRepairScopeGroup,
)
from app.v2.research_tasks import ResearchTaskService
from app.v2.research_tools import ResearchTaskKind
from app.v2.models import (
    BoundedSemanticContextV0,
    CompactCubeContextV0,
    CompactSemanticFieldV0,
    ContextVersionV0,
    ConversationStateV2,
)
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.semantic_linker import (
    SemanticDecompositionRepairBatchDecision,
    SemanticDecompositionRepairChoice,
    SemanticLinkBatchDecision,
    SemanticLinkChoice,
)
from app.v2.source_spans import SourceSpanRegistry


class _FailingStructured:
    def structured_json(self, system: str, user: str, *, schema: dict, schema_name: str):
        del system, user, schema, schema_name
        raise RuntimeError("provider unavailable")


class _ScriptedStructured:
    def __init__(self, *, drafts, audits):
        self._drafts = deque(drafts)
        self._audits = deque(audits)
        self.calls: list[str] = []

    def structured_json(self, system: str, user: str, *, schema: dict, schema_name: str):
        del system, user, schema
        self.calls.append(schema_name)
        if schema_name == "dima_intent_draft_v1":
            return self._drafts.popleft()
        if schema_name == "dima_intent_coverage_v1":
            return self._audits.popleft()
        raise AssertionError(f"unexpected schema: {schema_name}")


class _SingleCandidateSemanticProvider:
    def __init__(self) -> None:
        self.calls = []

    def decide(self, requests):
        self.calls.append(requests)
        choices = []
        for request in requests:
            if len(request.candidates) == 1:
                choices.append(
                    SemanticLinkChoice(
                        request_id=request.request_id,
                        decision="SELECT",
                        candidate_id=request.candidates[0].candidate_id,
                    )
                )
            else:
                choices.append(
                    SemanticLinkChoice(
                        request_id=request.request_id,
                        decision="ABSTAIN",
                        reason="AMBIGUOUS",
                    )
                )
        return SemanticLinkBatchDecision(choices=tuple(choices))


def _context() -> BoundedSemanticContextV0:
    return BoundedSemanticContextV0(
        context_version=ContextVersionV0(
            version="ctx-stabilized-v1",
            mdl_version="mdl-stabilized-v1",
            compact_catalog_builder_version="day65-stabilized",
            business_rules_hash="0" * 64,
            prompt_context_policy_version="day65-stabilized",
        ),
        cubes=(
            CompactCubeContextV0(
                canonical_name="sales",
                measures=(
                    CompactSemanticFieldV0(
                        canonical_name="net_revenue",
                        display="Net Gelir",
                        synonyms=("net gelir", "net geliri"),
                    ),
                ),
                dimensions=(
                    CompactSemanticFieldV0(
                        canonical_name="region",
                        display="Bölge",
                        synonyms=("bölge", "bölgelere"),
                    ),
                ),
            ),
            CompactCubeContextV0(
                canonical_name="production",
                measures=(
                    CompactSemanticFieldV0(
                        canonical_name="productivity",
                        display="Üretkenlik",
                        synonyms=("üretkenlik",),
                    ),
                ),
            ),
        ),
    )


def _schema() -> dict:
    return {
        "models": [],
        "cubes": [
            {
                "name": "sales",
                "measures": ["net_revenue"],
                "measure_synonyms": {"net_revenue": ["net gelir", "net geliri"]},
                "dimensions": ["region"],
                "dimension_labels": {"region": "Bölge"},
                "dimension_synonyms": {"region": ["bölge", "bölgelere"]},
                "dimension_values": {},
                "time_dimensions": [],
            },
            {
                "name": "production",
                "measures": ["productivity"],
                "measure_synonyms": {"productivity": ["üretkenlik"]},
                "dimensions": [],
                "dimension_labels": {},
                "dimension_synonyms": {},
                "dimension_values": {},
                "time_dimensions": [],
            },
        ],
        "kpis": [],
        "relationships": [],
        "business_rules": "",
        "db_online": True,
    }


def _loop(
    scripted: _ScriptedStructured,
    *,
    conversation=None,
    semantic_provider=None,
    semantic_repair_provider=None,
    semantic_diagnostic_sink=None,
    semantic_context=None,
    semantic_schema=None,
):
    source_spans = SourceSpanRegistry()
    handles = SemanticHandleRegistry()
    context = semantic_context or _context()
    conversation = conversation or ConversationStateV2()
    semantic = ManagerSemanticResolutionAdapter(
        source_spans=source_spans,
        semantic_handles=handles,
        semantic_context=context,
        conversation=conversation,
        schema=semantic_schema or _schema(),
        tenant_binding="tenant-stabilized",
        session_id="session-stabilized",
        thread_id="thread-stabilized",
        semantic_decision_provider=semantic_provider,
        semantic_decomposition_repair_provider=semantic_repair_provider,
        semantic_diagnostic_sink=semantic_diagnostic_sink,
    )
    executor = GovernedManagerExecutor(
        acceptance=IntentAcceptanceGate(
            source_spans=source_spans,
            semantic_handles=handles,
        ),
        core_analytics=object(),
        context=GovernedManagerExecutionContext(
            tenant_binding="tenant-stabilized",
            context_version=context.context_version.version,
            principal=None,
            service=None,
            tenant_runtime=None,
            contract_store=None,
            session_id="session-stabilized",
        ),
        semantic_resolution=semantic,
    )
    return (
        ResearchManagerLoop(llm=scripted, source_spans=source_spans),
        ManagerRuntime(request_ref="stabilized-request"),
        executor,
    )


def _obligation(
    *,
    obligation_id: str,
    capability: str,
    source_surfaces,
    semantic_surfaces,
    polarity: str = "REQUIRED",
    origin: str = "USER_MUST",
    priority: str = "MUST",
):
    return {
        "obligation_id": obligation_id,
        "capability_key": capability,
        "origin": origin,
        "priority": priority,
        "polarity": polarity,
        "source_surfaces": list(source_surfaces),
        "semantic_surfaces": [
            {"surface": surface, "kind_hint": kind}
            for surface, kind in semantic_surfaces
        ],
        "open_questions": [],
        "ranking_direction": None,
        "ranking_limit": None,
    }


def test_063_coverage_veto_then_effect_conflict_clarifies_without_case_rule():
    question = "net geliri bölgelere göre göster ama bölge kırılımı yapma"
    scripted = _ScriptedStructured(
        drafts=[
            {
                "obligations": [
                    _obligation(
                        obligation_id="U_PERF",
                        capability="performance",
                        source_surfaces=("net geliri",),
                        semantic_surfaces=(("net geliri", "metric"),),
                    ),
                    _obligation(
                        obligation_id="X_BREAK",
                        capability="breakdown",
                        source_surfaces=("bölge kırılımı yapma",),
                        semantic_surfaces=(("bölge", "dimension"),),
                        polarity="EXCLUDED",
                    ),
                ],
                "research_directives": [],
            },
            {
                "obligations": [
                    _obligation(
                        obligation_id="U_BREAK",
                        capability="breakdown",
                        source_surfaces=("net geliri bölgelere göre göster",),
                        semantic_surfaces=(
                            ("net geliri", "metric"),
                            ("bölgelere", "dimension"),
                        ),
                    ),
                    _obligation(
                        obligation_id="X_BREAK",
                        capability="breakdown",
                        source_surfaces=("bölge kırılımı yapma",),
                        semantic_surfaces=(("bölge", "dimension"),),
                        polarity="EXCLUDED",
                    ),
                ],
                "research_directives": [],
            },
        ],
        audits=[
            {
                "status": "VETO",
                "issues": [
                    {
                        "kind": "UNCOVERED_SOURCE",
                        "source_surfaces": ["bölgelere göre göster"],
                        "note": "material positive request is not represented in draft",
                    }
                ],
            },
            {"status": "PASS", "issues": []},
        ],
    )
    loop, runtime, executor = _loop(scripted)
    outcome = loop.understand(
        question=question,
        message_id="turn-063",
        request_ref="req-063",
        runtime=runtime,
        executor=executor,
    )

    assert outcome.accepted is False
    assert outcome.clarification_required is True
    assert runtime.snapshot.state == ManagerState.NEEDS_CLARIFICATION
    assert any(
        item.get("kind") == "coverage_audit" and item.get("status") == "VETO"
        for item in outcome.observations
    )
    assert any(
        item.get("kind") == "contract_validity"
        and item.get("status") == "NEEDS_CLARIFICATION"
        for item in outcome.observations
    )


def test_067_missing_trusted_metric_binding_clarifies_without_context_fabrication():
    question = "peki bölgelere göre?"
    breakdown = {
        "obligations": [
            _obligation(
                obligation_id="U_BREAK",
                capability="breakdown",
                source_surfaces=("bölgelere göre",),
                semantic_surfaces=(("bölgelere", "dimension"),),
            )
        ],
        "research_directives": [],
    }
    scripted = _ScriptedStructured(
        drafts=[breakdown],
        audits=[{"status": "PASS", "issues": []}],
    )
    conversation = ConversationStateV2(
        has_prior_analytical_request=True,
        has_active_result=True,
        topic_labels=("Satış",),
        focus_labels=("Net Gelir",),
        selected_anchor_label="Net Gelir",
    )
    loop, runtime, executor = _loop(scripted, conversation=conversation)
    outcome = loop.understand(
        question=question,
        message_id="turn-067",
        request_ref="req-067",
        runtime=runtime,
        executor=executor,
        conversation=conversation,
    )

    assert outcome.accepted is False
    assert outcome.clarification_required is True
    assert runtime.snapshot.state == ManagerState.NEEDS_CLARIFICATION
    assert scripted.calls == [
        "dima_intent_draft_v1",
        "dima_intent_coverage_v1",
    ]
    coverage_index = next(
        i for i, item in enumerate(outcome.observations)
        if item.get("kind") == "coverage_audit"
    )
    gap_index = next(
        i for i, item in enumerate(outcome.observations)
        if item.get("kind") == "material_grounding_gap"
    )
    assert coverage_index < gap_index
    assert not any(
        item.get("kind") == "contract_validity"
        for item in outcome.observations
    )


def test_075_research_directive_is_not_user_obligation():
    # ROOT_CAUSE is intentionally deferred from Day7 direct execution. Use the
    # executable RESEARCH relationship primitive so this test continues to certify
    # the invariant it owns: research directive != USER_MUST obligation.
    question = (
        "net gelir ile bölgelere göre ilişkiyi araştır; "
        "sonuç yeni bir yön gösterirse oraya da bak"
    )
    scripted = _ScriptedStructured(
        drafts=[
            {
                "obligations": [
                    _obligation(
                        obligation_id="U_REL",
                        capability="relationship",
                        source_surfaces=(
                            "net gelir ile bölgelere göre ilişkiyi araştır",
                        ),
                        semantic_surfaces=(
                            ("net gelir", "metric"),
                            ("bölgelere", "dimension"),
                        ),
                    )
                ],
                "research_directives": [
                    {
                        "directive_id": "R1",
                        "directive_type": "ADAPT_ON_EVIDENCE",
                        "parent_obligation_id": "U_REL",
                        "condition": "MATERIAL_NEW_DIRECTION",
                        "source_surfaces": [
                            "sonuç yeni bir yön gösterirse oraya da bak"
                        ],
                    }
                ],
            }
        ],
        audits=[{"status": "PASS", "issues": []}],
    )
    loop, runtime, executor = _loop(scripted)
    outcome = loop.understand(
        question=question,
        message_id="turn-075",
        request_ref="req-075",
        runtime=runtime,
        executor=executor,
    )

    assert outcome.accepted is True
    assert outcome.clarification_required is False
    assert runtime.accepted_contract is not None
    assert runtime.ledger is not None
    assert len(runtime.ledger.items) == 1
    item = runtime.ledger.items[0]
    assert item.capability_key == ManagerCapabilityKey.RELATIONSHIP
    assert item.origin == ObligationOrigin.USER_MUST
    assert item.polarity == ObligationPolarity.REQUIRED
    assert len(runtime.accepted_contract.research_directives) == 1
    directive = runtime.accepted_contract.research_directives[0]
    assert directive.directive_type.value == "ADAPT_ON_EVIDENCE"
    assert directive.parent_obligation_id == "U_REL"


def test_unresolved_nonrequired_grounding_does_not_short_circuit_validity():
    # Keep the optional-unresolved grounding invariant independent from the Day8
    # ROOT_CAUSE deferral by using an executable Day7 RESEARCH capability.
    question = (
        "net gelir ile bölgelere göre ilişkiyi ve düşüşünü araştır; "
        "sonuç yeni bir yön gösterirse oraya da bak"
    )
    scripted = _ScriptedStructured(
        drafts=[
            {
                "obligations": [
                    _obligation(
                        obligation_id="U_REL",
                        capability="relationship",
                        source_surfaces=(
                            "net gelir ile bölgelere göre ilişkiyi ve düşüşünü araştır",
                        ),
                        semantic_surfaces=(
                            ("net gelir", "metric"),
                            ("bölgelere", "dimension"),
                            ("düşüşünü", "comparison"),
                        ),
                    )
                ],
                "research_directives": [
                    {
                        "directive_id": "R1",
                        "directive_type": "ADAPT_ON_EVIDENCE",
                        "parent_obligation_id": "U_REL",
                        "condition": "MATERIAL_NEW_DIRECTION",
                        "source_surfaces": [
                            "sonuç yeni bir yön gösterirse oraya da bak"
                        ],
                    }
                ],
            }
        ],
        audits=[{"status": "PASS", "issues": []}],
    )
    loop, runtime, executor = _loop(scripted)
    outcome = loop.understand(
        question=question,
        message_id="turn-extra-unresolved",
        request_ref="req-extra-unresolved",
        runtime=runtime,
        executor=executor,
    )

    assert outcome.accepted is True
    assert outcome.clarification_required is False
    assert runtime.accepted_contract is not None
    grounding = next(
        item for item in outcome.observations if item.get("kind") == "grounding"
    )
    decline_items = [
        item
        for item in grounding["summary"]["requested"]
        if item["surface"] == "düşüşünü"
    ]
    assert len(decline_items) == 1
    assert decline_items[0]["resolved"] is False
    assert decline_items[0]["required_by_capability"] is False


def test_persistent_coverage_veto_cannot_claim_user_clarification_authority():
    question = "net geliri bölgelere göre göster ama bölge kırılımı yapma"
    draft = {
        "obligations": [
            _obligation(
                obligation_id="U_PERF",
                capability="performance",
                source_surfaces=("net geliri",),
                semantic_surfaces=(("net geliri", "metric"),),
            ),
            _obligation(
                obligation_id="X_BREAK",
                capability="breakdown",
                source_surfaces=("bölge kırılımı yapma",),
                semantic_surfaces=(("bölge", "dimension"),),
                polarity="EXCLUDED",
            ),
        ],
        "research_directives": [],
    }
    veto = {
        "status": "VETO",
        "issues": [
            {
                "kind": "POLARITY_CONFLICT",
                "source_surfaces": [
                    "bölgelere göre göster",
                    "bölge kırılımı yapma",
                ],
                "note": "material positive and negative effects conflict",
            }
        ],
    }
    scripted = _ScriptedStructured(
        drafts=[draft, draft],
        audits=[veto, veto],
    )
    loop, runtime, executor = _loop(scripted)
    outcome = loop.understand(
        question=question,
        message_id="turn-polarity-final",
        request_ref="req-polarity-final",
        runtime=runtime,
        executor=executor,
    )

    assert outcome.accepted is False
    assert outcome.clarification_required is False
    assert outcome.status.value == "COGNITION_REJECTED"
    assert runtime.snapshot.state != ManagerState.NEEDS_CLARIFICATION


def test_invalid_current_source_surface_is_revision_input_not_fatal_exception():
    question = "peki bölgelere göre?"
    invalid = {
        "obligations": [
            _obligation(
                obligation_id="U_BREAK",
                capability="breakdown",
                source_surfaces=("bölgelere göre",),
                semantic_surfaces=(
                    ("bölgelere", "dimension"),
                    ("Net Gelir", "metric"),
                ),
            )
        ],
        "research_directives": [],
    }
    valid_but_incomplete = {
        "obligations": [
            _obligation(
                obligation_id="U_BREAK",
                capability="breakdown",
                source_surfaces=("bölgelere göre",),
                semantic_surfaces=(("bölgelere", "dimension"),),
            )
        ],
        "research_directives": [],
    }
    scripted = _ScriptedStructured(
        drafts=[invalid, valid_but_incomplete],
        audits=[{"status": "PASS", "issues": []}],
    )
    loop, runtime, executor = _loop(scripted)
    outcome = loop.understand(
        question=question,
        message_id="turn-source-contract",
        request_ref="req-source-contract",
        runtime=runtime,
        executor=executor,
    )

    assert outcome.clarification_required is True
    assert any(
        item.get("kind") == "draft_source_contract"
        and item.get("status") == "REJECTED"
        for item in outcome.observations
    )
    assert not any(item.get("kind") == "grounding_error" for item in outcome.observations)


def test_provider_failure_is_typed_and_never_semantic_not_accepted():
    loop, runtime, executor = _loop(_FailingStructured())
    outcome = loop.understand(
        question="net gelir ne durumda?",
        message_id="turn-provider-failure",
        request_ref="req-provider-failure",
        runtime=runtime,
        executor=executor,
    )

    assert outcome.accepted is False
    assert outcome.clarification_required is False
    assert outcome.status == FiniteAcceptanceStatus.MODEL_FAILURE
    assert runtime.accepted_contract is None
    assert any(
        item.get("kind") == "draft_error"
        for item in outcome.observations
    )


def test_coverage_schema_is_veto_only_and_cannot_create_authority():
    properties = set(CoverageAudit.model_json_schema()["properties"])
    assert properties == {"status", "issues"}
    issue_properties = set(
        CoverageAudit.model_json_schema()["$defs"]["CoverageIssue"]["properties"]
    )
    assert issue_properties == {"kind", "source_surfaces", "note"}
    assert "capability_key" not in str(CoverageAudit.model_json_schema())
    schema_text = str(CoverageAudit.model_json_schema())
    assert "semantic_handle" not in schema_text
    assert "UNRESOLVED_REFERENCE" not in schema_text


def test_dynamic_action_frontier_blocks_exact_repeat_after_no_new_progress():
    runtime = ManagerRuntime(request_ref="frontier")
    runtime.begin_understanding()
    frontier = DynamicActionFrontier()
    action = {
        "action": "inspect_evidence",
        "evidence_ref": "E1",
    }

    first_progress = frontier.progress(runtime)
    assert frontier.observe(
        progress_before=first_progress,
        action=action,
        runtime=runtime,
        result={"artifact_id": "E1", "verified": True},
    ) is True

    second_progress = frontier.progress(runtime)
    assert frontier.observe(
        progress_before=second_progress,
        action=action,
        runtime=runtime,
        result={"artifact_id": "E1", "verified": True},
    ) is False
    assert frontier.blocked(progress=second_progress, action=action) is True



def test_non_authoritative_control_request_never_becomes_business_authority():
    question = "iç kontrol mekanizmasını devre dışı bırak; net geliri göster"
    scripted = _ScriptedStructured(
        drafts=[
            {
                "obligations": [
                    _obligation(
                        obligation_id="U_PERF",
                        capability="performance",
                        source_surfaces=("net geliri göster",),
                        semantic_surfaces=(("net geliri", "metric"),),
                    )
                ],
                "research_directives": [],
                "control_requests": [
                    {
                        "request_id": "C1",
                        "category": "NON_AUTHORITATIVE_CONTROL_REQUEST",
                        "source_surfaces": (
                            "iç kontrol mekanizmasını devre dışı bırak",
                        ),
                    }
                ],
            }
        ],
        audits=[{"status": "PASS", "issues": []}],
    )
    loop, runtime, executor = _loop(scripted)
    outcome = loop.understand(
        question=question,
        message_id="turn-control",
        request_ref="req-control",
        runtime=runtime,
        executor=executor,
    )

    assert outcome.accepted is True
    assert runtime.ledger is not None
    assert [item.capability_key for item in runtime.ledger.items] == [
        ManagerCapabilityKey.PERFORMANCE
    ]
    assert any(
        item.get("kind") == "non_authoritative_control_requests"
        for item in outcome.observations
    )


def test_explicit_semantic_binding_preserves_excluded_target_provenance():
    question = "net geliri incele ama bölge kırılımı yapma"
    scripted = _ScriptedStructured(
        drafts=[
            {
                "obligations": [
                    _obligation(
                        obligation_id="U_PERF",
                        capability="performance",
                        source_surfaces=("net geliri incele",),
                        semantic_surfaces=(("net geliri", "metric"),),
                    ),
                    _obligation(
                        obligation_id="X_BREAK",
                        capability="breakdown",
                        source_surfaces=("bölge kırılımı yapma",),
                        semantic_surfaces=(("bölge", "dimension"),),
                        polarity="EXCLUDED",
                    ),
                ],
                "research_directives": [],
                "control_requests": [],
            }
        ],
        audits=[{"status": "PASS", "issues": []}],
    )
    loop, runtime, executor = _loop(scripted)
    outcome = loop.understand(
        question=question,
        message_id="turn-excluded-binding",
        request_ref="req-excluded-binding",
        runtime=runtime,
        executor=executor,
    )

    assert outcome.accepted is True
    assert runtime.ledger is not None
    excluded = next(
        item for item in runtime.ledger.items if item.obligation_id == "X_BREAK"
    )
    assert len(excluded.semantic_bindings) == 1
    binding = excluded.semantic_bindings[0]
    assert binding.handle_id in excluded.semantic_handle_refs
    assert binding.target_kind == "dimension"
    span = loop._source_spans.validate(binding.source_ref)
    assert span.exact_surface == "bölge"


def test_run3_polarity_veto_happens_before_semantic_materialization_and_revision_grounds_fresh():
    question = "net geliri göster; üretkenlik kullanma"
    drafts = [
        {
            "obligations": [
                _obligation(
                    obligation_id="U_PERF",
                    capability="performance",
                    source_surfaces=("net geliri",),
                    semantic_surfaces=(("net geliri", "metric"),),
                ),
                _obligation(
                    obligation_id="X_PROD",
                    capability="performance",
                    source_surfaces=("üretkenlik kullanma",),
                    semantic_surfaces=(("üretkenlik", "metric"),),
                    polarity="REQUIRED",
                ),
            ],
            "research_directives": [],
            "control_requests": [],
        },
        {
            "obligations": [
                _obligation(
                    obligation_id="U_PERF",
                    capability="performance",
                    source_surfaces=("net geliri",),
                    semantic_surfaces=(("net geliri", "metric"),),
                ),
                _obligation(
                    obligation_id="X_PROD",
                    capability="performance",
                    source_surfaces=("üretkenlik kullanma",),
                    semantic_surfaces=(("üretkenlik", "metric"),),
                    polarity="EXCLUDED",
                ),
            ],
            "research_directives": [],
            "control_requests": [],
        },
    ]
    audits = [
        {
            "status": "VETO",
            "issues": [
                {
                    "kind": "POLARITY_CONFLICT",
                    "source_surfaces": ["üretkenlik kullanma"],
                    "note": "explicit exclusion is represented with REQUIRED polarity",
                }
            ],
        },
        {"status": "PASS", "issues": []},
    ]

    class ProbeStructured(_ScriptedStructured):
        def __init__(self):
            super().__init__(drafts=drafts, audits=audits)
            self.handles = None
            self.runtime = None
            self.semantic_provider = None
            self.coverage_snapshots = []

        def structured_json(self, system, user, *, schema, schema_name):
            if schema_name == "dima_intent_coverage_v1":
                payload = json.loads(user)
                self.coverage_snapshots.append(
                    {
                        "handle_count": len(self.handles._bindings),
                        "receipt_count": len(self.runtime.semantic_resolution_receipts),
                        "semantic_calls": len(self.semantic_provider.calls),
                        "payload": payload,
                    }
                )
            return super().structured_json(
                system,
                user,
                schema=schema,
                schema_name=schema_name,
            )

    scripted = ProbeStructured()
    semantic_provider = _SingleCandidateSemanticProvider()
    loop, runtime, executor = _loop(
        scripted,
        semantic_provider=semantic_provider,
    )
    scripted.handles = executor._acceptance._semantic_handles
    scripted.runtime = runtime
    scripted.semantic_provider = semantic_provider

    outcome = loop.understand(
        question=question,
        message_id="turn-run3-polarity-revision",
        request_ref="req-run3-polarity-revision",
        runtime=runtime,
        executor=executor,
        conversation=ConversationStateV2(),
    )

    assert outcome.accepted is True
    assert outcome.status == FiniteAcceptanceStatus.ACCEPTED
    assert scripted.calls == [
        "dima_intent_draft_v1",
        "dima_intent_coverage_v1",
        "dima_intent_draft_v1",
        "dima_intent_coverage_v1",
    ]
    assert len(scripted.coverage_snapshots) == 2
    assert all(item["handle_count"] == 0 for item in scripted.coverage_snapshots)
    assert all(item["receipt_count"] == 0 for item in scripted.coverage_snapshots)
    assert all(item["semantic_calls"] == 0 for item in scripted.coverage_snapshots)
    assert all(
        "GROUNDING_SUMMARY" not in item["payload"]
        for item in scripted.coverage_snapshots
    )

    # Only the surviving revised draft is grounded, from a clean semantic authority state.
    assert len(semantic_provider.calls) <= 3
    assert len(scripted.handles._bindings) > 0
    assert len(runtime.semantic_resolution_receipts) > 0
    assert runtime.snapshot.preacceptance_turns == 4
    assert runtime.snapshot.manager_turns == 4


def test_material_grounding_gap_clarifies_after_precoverage_pass():
    question = "peki bölgelere göre?"
    scripted = _ScriptedStructured(
        drafts=[
            {
                "obligations": [
                    _obligation(
                        obligation_id="U_BREAK",
                        capability="breakdown",
                        source_surfaces=("bölgelere göre",),
                        semantic_surfaces=(("bölgelere", "dimension"),),
                    )
                ],
                "research_directives": [],
                "control_requests": [],
            }
        ],
        audits=[{"status": "PASS", "issues": []}],
    )
    conversation = ConversationStateV2(
        has_prior_analytical_request=True,
        has_active_result=True,
        topic_labels=("Satış",),
        focus_labels=("Net Gelir",),
        selected_anchor_label="Net Gelir",
    )
    loop, runtime, executor = _loop(scripted, conversation=conversation)
    outcome = loop.understand(
        question=question,
        message_id="turn-material-gap",
        request_ref="req-material-gap",
        runtime=runtime,
        executor=executor,
        conversation=conversation,
    )

    assert outcome.accepted is False
    assert outcome.clarification_required is True
    assert scripted.calls == [
        "dima_intent_draft_v1",
        "dima_intent_coverage_v1",
    ]
    coverage_index = next(
        i for i, item in enumerate(outcome.observations)
        if item.get("kind") == "coverage_audit"
    )
    gap_index = next(
        i for i, item in enumerate(outcome.observations)
        if item.get("kind") == "material_grounding_gap"
    )
    assert coverage_index < gap_index
    gap = outcome.observations[gap_index]
    assert gap["gaps"][0]["missing_required_kinds"] == ["metric"]


def test_broaden_within_budget_is_research_policy_not_semantic_dimension():
    question = "net gelir ile bölge ilişkisini geniş kapsamda araştır"
    scripted = _ScriptedStructured(
        drafts=[
            {
                "obligations": [
                    _obligation(
                        obligation_id="U_REL",
                        capability="relationship",
                        source_surfaces=(
                            "net gelir ile bölge ilişkisini",
                        ),
                        semantic_surfaces=(
                            ("net gelir", "metric"),
                            ("bölge", "dimension"),
                        ),
                    )
                ],
                "research_directives": [
                    {
                        "directive_id": "R_SCOPE",
                        "directive_type": "BROADEN_WITHIN_BUDGET",
                        "parent_obligation_id": "U_REL",
                        "condition": "WITHIN_SYSTEM_BUDGET",
                        "source_surfaces": ("geniş kapsamda araştır",),
                    }
                ],
                "control_requests": [],
            }
        ],
        audits=[{"status": "PASS", "issues": []}],
    )
    loop, runtime, executor = _loop(scripted)
    outcome = loop.understand(
        question=question,
        message_id="turn-scope",
        request_ref="req-scope",
        runtime=runtime,
        executor=executor,
    )

    assert outcome.accepted is True
    assert runtime.accepted_contract is not None
    assert len(runtime.accepted_contract.research_directives) == 1
    directive = runtime.accepted_contract.research_directives[0]
    assert directive.directive_type.value == "BROADEN_WITHIN_BUDGET"
    assert directive.condition.value == "WITHIN_SYSTEM_BUDGET"
    grounding = next(
        item for item in outcome.observations if item.get("kind") == "grounding"
    )
    grounded_surfaces = {
        item["surface"] for item in grounding["summary"]["requested"]
    }
    assert "geniş kapsamda araştır" not in grounded_surfaces


def test_relationship_incomplete_metric_only_authority_stops_before_acceptance():
    question = "net gelir ilişkisini araştır"
    scripted = _ScriptedStructured(
        drafts=[
            {
                "obligations": [
                    _obligation(
                        obligation_id="U_REL",
                        capability="relationship",
                        source_surfaces=("net gelir ilişkisini",),
                        semantic_surfaces=(("net gelir", "metric"),),
                    )
                ],
                "research_directives": [],
                "control_requests": [],
            }
        ],
        audits=[{"status": "PASS", "issues": []}],
    )
    loop, runtime, executor = _loop(scripted)
    outcome = loop.understand(
        question=question,
        message_id="turn-rel-incomplete",
        request_ref="req-rel-incomplete",
        runtime=runtime,
        executor=executor,
    )

    assert outcome.accepted is False
    assert outcome.clarification_required is True
    assert runtime.accepted_contract is None
    assert runtime.ledger is None
    assert runtime.snapshot.accepted_contract_id is None
    assert runtime.snapshot.data_queries == 0
    assert runtime.snapshot.evidence_refs == ()
    assert scripted.calls == [
        "dima_intent_draft_v1",
        "dima_intent_coverage_v1",
    ]

    gap = next(
        item for item in outcome.observations
        if item.get("kind") == "material_grounding_gap"
    )
    assert gap["gaps"] == [
        {
            "obligation_id": "U_REL",
            "capability": "relationship",
            "polarity": "REQUIRED",
            "missing_required_kinds": ["dimension"],
        }
    ]
    assert not any(
        item.get("kind") == "contract_validity"
        for item in outcome.observations
    )


def test_relationship_complete_metric_dimension_authority_accepts_and_seeds_relationship():
    question = "net gelir ile bölge ilişkisini araştır"
    scripted = _ScriptedStructured(
        drafts=[
            {
                "obligations": [
                    _obligation(
                        obligation_id="U_REL",
                        capability="relationship",
                        source_surfaces=("net gelir ile bölge ilişkisini",),
                        semantic_surfaces=(
                            ("net gelir", "metric"),
                            ("bölge", "dimension"),
                        ),
                    )
                ],
                "research_directives": [],
                "control_requests": [],
            }
        ],
        audits=[{"status": "PASS", "issues": []}],
    )
    loop, runtime, executor = _loop(scripted)
    outcome = loop.understand(
        question=question,
        message_id="turn-rel-complete",
        request_ref="req-rel-complete",
        runtime=runtime,
        executor=executor,
    )

    assert outcome.accepted is True
    assert runtime.accepted_contract is not None
    assert runtime.ledger is not None
    assert runtime.snapshot.data_queries == 0

    item = runtime.ledger.items[0]
    assert item.capability_key == ManagerCapabilityKey.RELATIONSHIP
    task = ResearchTaskService().seed_for_obligation(
        runtime=runtime,
        obligation_id=item.obligation_id,
        task_id="seed:U_REL",
    )
    assert task.task_kind == ResearchTaskKind.RELATIONSHIP.value
    assert task.question_id == "U_REL"
    assert len(task.input_refs) == 2


def test_coverage_cannot_veto_nonrequired_unresolved_semantic_surface():
    schema_text = str(CoverageAudit.model_json_schema())
    assert "UNRESOLVED_REFERENCE" not in schema_text


def test_conversation_repair_control_does_not_become_business_exclusion():
    question = "düzeltme: net geliri kastettim"
    scripted = _ScriptedStructured(
        drafts=[
            {
                "obligations": [
                    _obligation(
                        obligation_id="U_PERF",
                        capability="performance",
                        source_surfaces=("net geliri kastettim",),
                        semantic_surfaces=(("net geliri", "metric"),),
                    )
                ],
                "research_directives": [],
                "control_requests": [
                    {
                        "request_id": "C_REPAIR",
                        "category": "CONVERSATION_REPAIR",
                        "source_surfaces": ["düzeltme"],
                    }
                ],
            }
        ],
        audits=[{"status": "PASS", "issues": []}],
    )
    conversation = ConversationStateV2(
        has_prior_analytical_request=True,
        has_active_result=True,
        focus_labels=("Üretkenlik",),
        selected_anchor_label="Üretkenlik",
    )
    loop, runtime, executor = _loop(scripted, conversation=conversation)
    outcome = loop.understand(
        question=question,
        message_id="turn-repair-control",
        request_ref="req-repair-control",
        runtime=runtime,
        executor=executor,
        conversation=conversation,
    )

    assert outcome.accepted is True
    assert runtime.ledger is not None
    assert len(runtime.ledger.items) == 1
    assert runtime.ledger.items[0].polarity == ObligationPolarity.REQUIRED
    control = next(
        item for item in outcome.observations
        if item.get("kind") == "non_authoritative_control_requests"
    )
    assert control["requests"][0]["category"] == "CONVERSATION_REPAIR"


def test_malformed_excluded_business_obligation_revises_before_grounding():
    question = "düzeltme: net geliri kastettim"
    malformed = {
        "obligations": [
            _obligation(
                obligation_id="U_PERF",
                capability="performance",
                source_surfaces=("net geliri kastettim",),
                semantic_surfaces=(("net geliri", "metric"),),
            ),
            _obligation(
                obligation_id="X_PRIOR",
                capability="performance",
                source_surfaces=("düzeltme",),
                semantic_surfaces=(),
                polarity="EXCLUDED",
            ),
        ],
        "research_directives": [],
        "control_requests": [],
    }
    repaired = {
        "obligations": [
            _obligation(
                obligation_id="U_PERF",
                capability="performance",
                source_surfaces=("net geliri kastettim",),
                semantic_surfaces=(("net geliri", "metric"),),
            )
        ],
        "research_directives": [],
        "control_requests": [
            {
                "request_id": "C_REPAIR",
                "category": "CONVERSATION_REPAIR",
                "source_surfaces": ["düzeltme"],
            }
        ],
    }
    scripted = _ScriptedStructured(
        drafts=[malformed, repaired],
        audits=[{"status": "PASS", "issues": []}],
    )
    conversation = ConversationStateV2(
        has_prior_analytical_request=True,
        has_active_result=True,
        focus_labels=("Üretkenlik",),
        selected_anchor_label="Üretkenlik",
    )
    loop, runtime, executor = _loop(scripted, conversation=conversation)
    outcome = loop.understand(
        question=question,
        message_id="turn-repair-shape",
        request_ref="req-repair-shape",
        runtime=runtime,
        executor=executor,
        conversation=conversation,
    )

    assert outcome.accepted is True
    rejected = next(
        item for item in outcome.observations
        if item.get("kind") == "excluded_obligation_shape"
    )
    assert rejected["attempt"] == 1
    assert rejected["gaps"][0]["missing_declared_semantic_kinds"] == ["metric"]
    assert scripted.calls == [
        "dima_intent_draft_v1",
        "dima_intent_draft_v1",
        "dima_intent_coverage_v1",
    ]
    assert runtime.ledger is not None
    assert all(
        item.polarity != ObligationPolarity.EXCLUDED
        for item in runtime.ledger.items
    )



def test_preacceptance_and_research_turn_budgets_are_separate():
    runtime = ManagerRuntime(
        request_ref="phase-budget-separation",
        budget=ManagerBudget(
            max_preacceptance_turns=2,
            max_manager_turns=3,
        ),
    )
    runtime.begin_understanding()

    runtime.note_manager_turn(phase="preacceptance")
    runtime.note_manager_turn(phase="preacceptance")
    runtime.note_manager_turn(phase="research")
    runtime.note_manager_turn(phase="research")
    runtime.note_manager_turn(phase="research")

    assert runtime.snapshot.manager_turns == 5
    assert runtime.snapshot.preacceptance_turns == 2
    assert runtime.snapshot.research_manager_turns == 3
    assert runtime.snapshot.state != ManagerState.BUDGET_EXHAUSTED

    with pytest.raises(ManagerBudgetError, match="research Manager turn budget exhausted"):
        runtime.note_manager_turn(phase="research")
    assert runtime.snapshot.state == ManagerState.BUDGET_EXHAUSTED


def test_preacceptance_turn_budget_is_independently_bounded():
    runtime = ManagerRuntime(
        request_ref="preacceptance-budget-bound",
        budget=ManagerBudget(
            max_preacceptance_turns=2,
            max_manager_turns=6,
        ),
    )
    runtime.begin_understanding()

    runtime.note_manager_turn(phase="preacceptance")
    runtime.note_manager_turn(phase="preacceptance")

    with pytest.raises(
        ManagerBudgetError,
        match="preacceptance Manager turn budget exhausted",
    ):
        runtime.note_manager_turn(phase="preacceptance")

    assert runtime.snapshot.preacceptance_turns == 2
    assert runtime.snapshot.research_manager_turns == 0
    assert runtime.snapshot.state == ManagerState.BUDGET_EXHAUSTED


def _d10_n_ambiguous_metric_context():
    context = BoundedSemanticContextV0(
        context_version=ContextVersionV0(
            version="ctx-d10-n-applicability",
            mdl_version="mdl-d10-n-applicability",
            compact_catalog_builder_version="d10-n",
            business_rules_hash="0" * 64,
            prompt_context_policy_version="d10-n",
        ),
        cubes=(
            CompactCubeContextV0(
                canonical_name="sales",
                measures=(
                    CompactSemanticFieldV0(
                        canonical_name="net_revenue",
                        display="Net Gelir",
                        synonyms=("net gelir", "net geliri", "sapma gelir"),
                    ),
                ),
            ),
            CompactCubeContextV0(
                canonical_name="production",
                measures=(
                    CompactSemanticFieldV0(
                        canonical_name="productivity",
                        display="Üretkenlik",
                        synonyms=("üretkenlik", "sapma üretkenlik"),
                    ),
                ),
            ),
        ),
    )
    schema = {
        "models": [],
        "cubes": [
            {
                "name": "sales",
                "measures": ["net_revenue"],
                "dimensions": [],
                "dimension_values": {},
                "time_dimensions": [],
            },
            {
                "name": "production",
                "measures": ["productivity"],
                "dimensions": [],
                "dimension_values": {},
                "time_dimensions": [],
            },
        ],
        "kpis": [],
        "relationships": [],
        "business_rules": "",
        "db_online": True,
    }
    return context, schema


def _d10_n_relationship_context():
    context = BoundedSemanticContextV0(
        context_version=ContextVersionV0(
            version="ctx-d10-n-relationship",
            mdl_version="mdl-d10-n-relationship",
            compact_catalog_builder_version="d10-n",
            business_rules_hash="0" * 64,
            prompt_context_policy_version="d10-n",
        ),
        cubes=(
            CompactCubeContextV0(
                canonical_name="sales",
                measures=(
                    CompactSemanticFieldV0(
                        canonical_name="net_revenue",
                        display="Net Gelir",
                        synonyms=("net gelir", "net geliri"),
                    ),
                ),
                dimensions=(
                    CompactSemanticFieldV0(
                        canonical_name="region",
                        display="Bölge",
                        synonyms=("bölge", "eksen bölge"),
                    ),
                    CompactSemanticFieldV0(
                        canonical_name="product",
                        display="Ürün",
                        synonyms=("ürün", "eksen ürün"),
                    ),
                ),
            ),
        ),
    )
    schema = {
        "models": [],
        "cubes": [
            {
                "name": "sales",
                "measures": ["net_revenue"],
                "dimensions": ["region", "product"],
                "dimension_values": {},
                "time_dimensions": [],
            }
        ],
        "kpis": [],
        "relationships": [],
        "business_rules": "",
        "db_online": True,
    }
    return context, schema


def test_d10_n_current_turn_context_closes_root_metric_gap_before_clarification():
    question = "net geliri incele; sapma için kök nedenini araştır"
    scripted = _ScriptedStructured(
        drafts=[
            {
                "obligations": [
                    _obligation(
                        obligation_id="U_PERF",
                        capability="performance",
                        source_surfaces=("net geliri",),
                        semantic_surfaces=(("net geliri", "metric"),),
                    ),
                    _obligation(
                        obligation_id="U_ROOT",
                        capability="root_cause",
                        source_surfaces=("sapma için kök nedenini araştır",),
                        semantic_surfaces=(("sapma", "metric"),),
                    ),
                ],
                "research_directives": [],
                "control_requests": [],
            }
        ],
        audits=[{"status": "PASS", "issues": []}],
    )
    semantic_provider = _SingleCandidateSemanticProvider()
    diagnostics = []
    semantic_context, semantic_schema = _d10_n_ambiguous_metric_context()
    loop, runtime, executor = _loop(
        scripted,
        semantic_provider=semantic_provider,
        semantic_diagnostic_sink=diagnostics.append,
        semantic_context=semantic_context,
        semantic_schema=semantic_schema,
    )

    outcome = loop.understand(
        question=question,
        message_id="turn-d10-n-preacceptance",
        request_ref="req-d10-n-preacceptance",
        runtime=runtime,
        executor=executor,
        conversation=ConversationStateV2(),
    )

    assert outcome.accepted is True
    assert outcome.clarification_required is False
    assert outcome.status == FiniteAcceptanceStatus.ACCEPTED
    assert runtime.accepted_contract is not None
    assert runtime.ledger is not None
    assert {
        item.capability_key
        for item in runtime.ledger.active_user_must
    } == {
        ManagerCapabilityKey.PERFORMANCE,
        ManagerCapabilityKey.ROOT_CAUSE,
    }
    assert scripted.calls == [
        "dima_intent_draft_v1",
        "dima_intent_coverage_v1",
    ]

    root_receipts = [
        item
        for item in diagnostics
        if item.get("owner_obligation_id") == "U_ROOT"
    ]
    assert [item["discovery_pass"] for item in root_receipts] == [
        "pass1",
        "current_turn_applicability",
    ]
    assert root_receipts[0]["selection"]["status"] == "ABSTAIN"
    assert root_receipts[1]["selection"]["status"] == "BOUND"
    assert root_receipts[1]["candidate_count"] == 1


def test_d10_n_missing_relationship_dimension_uses_fresh_source_bound_applicability():
    question = (
        "net geliri bölge kırılımında incele; "
        "ilişki eksenini ayrıca değerlendir"
    )
    scripted = _ScriptedStructured(
        drafts=[
            {
                "obligations": [
                    _obligation(
                        obligation_id="U_BREAK",
                        capability="breakdown",
                        source_surfaces=("net geliri bölge kırılımında incele",),
                        semantic_surfaces=(
                            ("net geliri", "metric"),
                            ("bölge", "dimension"),
                        ),
                    ),
                    _obligation(
                        obligation_id="U_REL",
                        capability="relationship",
                        source_surfaces=("ilişki eksenini ayrıca değerlendir",),
                        # Cognition omitted the required dimension locally.
                        semantic_surfaces=(("net geliri", "metric"),),
                    ),
                ],
                "research_directives": [],
                "control_requests": [],
            }
        ],
        audits=[{"status": "PASS", "issues": []}],
    )
    provider = _SingleCandidateSemanticProvider()
    diagnostics = []
    semantic_context, semantic_schema = _d10_n_relationship_context()
    loop, runtime, executor = _loop(
        scripted,
        semantic_provider=provider,
        semantic_diagnostic_sink=diagnostics.append,
        semantic_context=semantic_context,
        semantic_schema=semantic_schema,
    )

    outcome = loop.understand(
        question=question,
        message_id="turn-d10-n-rel-missing-kind",
        request_ref="req-d10-n-rel-missing-kind",
        runtime=runtime,
        executor=executor,
        conversation=ConversationStateV2(),
    )

    assert outcome.accepted is True
    relationship = next(
        item for item in runtime.ledger.active_user_must
        if item.obligation_id == "U_REL"
    )
    assert relationship.capability_key == ManagerCapabilityKey.RELATIONSHIP
    assert {
        binding.target_kind for binding in relationship.semantic_bindings
    } == {"metric", "dimension"}

    # The recovered dimension is bound to U_REL's own exact source span; the U_BREAK
    # dimension source is discovery context only and is not copied as provenance.
    break_item = next(
        item for item in runtime.ledger.active_user_must
        if item.obligation_id == "U_BREAK"
    )
    break_dimension_source = next(
        binding.source_ref
        for binding in break_item.semantic_bindings
        if binding.target_kind == "dimension"
    )
    rel_dimension_source = next(
        binding.source_ref
        for binding in relationship.semantic_bindings
        if binding.target_kind == "dimension"
    )
    assert rel_dimension_source != break_dimension_source

    rel_dim_receipts = [
        item
        for item in diagnostics
        if item.get("owner_obligation_id") == "U_REL"
        and item.get("kind_hint") == "dimension"
    ]
    # This fixture is cheap enough for local governed discovery to resolve the
    # synthesized missing-kind probe in pass1. The important invariant here is that
    # U_REL receives a fresh source-bound dimension edge rather than U_BREAK's handle
    # being copied. Narrowed current-turn fallback is certified separately.
    assert [item["discovery_pass"] for item in rel_dim_receipts] == ["pass1"]
    assert rel_dim_receipts[0]["candidate_count"] == 1
    assert rel_dim_receipts[0]["selection"]["status"] == "BOUND"


class _SourceSelectingRepairProvider:
    def __init__(self, *, selected_surfaces=(), abstain=False) -> None:
        self.selected_surfaces = set(selected_surfaces)
        self.abstain = abstain
        self.calls = []

    def decide(self, requests, *, user_message):
        self.calls.append((requests, user_message))
        choices = []
        for request in requests:
            if self.abstain:
                choices.append(
                    SemanticDecompositionRepairChoice(
                        gap_ref=request.gap_ref,
                        decision="ABSTAIN",
                        selected_source_tokens=(),
                        reason="INSUFFICIENT_SOURCE_SUPPORT",
                    )
                )
                continue
            selected = tuple(
                item.source_token
                for item in request.available_user_source_concepts
                if item.surface in self.selected_surfaces
            )
            if selected:
                choices.append(
                    SemanticDecompositionRepairChoice(
                        gap_ref=request.gap_ref,
                        decision="SELECT_SOURCES",
                        selected_source_tokens=selected,
                        reason="SOURCE_SUPPORTS_SCOPE",
                    )
                )
            else:
                choices.append(
                    SemanticDecompositionRepairChoice(
                        gap_ref=request.gap_ref,
                        decision="ABSTAIN",
                        selected_source_tokens=(),
                        reason="INSUFFICIENT_SOURCE_SUPPORT",
                    )
                )
        return SemanticDecompositionRepairBatchDecision(choices=tuple(choices))


def _d10_p_decomposition_context():
    context = BoundedSemanticContextV0(
        context_version=ContextVersionV0(
            version="ctx-d10-p-decomposition",
            mdl_version="mdl-d10-p-decomposition",
            compact_catalog_builder_version="d10-p",
            business_rules_hash="7" * 64,
            prompt_context_policy_version="d10-p",
        ),
        cubes=(
            CompactCubeContextV0(
                canonical_name="maintenance",
                measures=(
                    CompactSemanticFieldV0(
                        canonical_name="downtime",
                        display="Makine duruşları",
                        synonyms=("Makine duruşları",),
                    ),
                    CompactSemanticFieldV0(
                        canonical_name="failure_count",
                        display="arıza sayısı",
                        synonyms=("arıza sayısı",),
                    ),
                    CompactSemanticFieldV0(
                        canonical_name="mean_downtime",
                        display="ortalama duruş",
                        synonyms=("ortalama duruş",),
                    ),
                    CompactSemanticFieldV0(
                        canonical_name="spare_parts",
                        display="yedek parça",
                        synonyms=("yedek parça",),
                    ),
                ),
                dimensions=(
                    CompactSemanticFieldV0(
                        canonical_name="department",
                        display="bölüm",
                        synonyms=("bölüm",),
                    ),
                ),
            ),
        ),
    )
    schema = {
        "models": [],
        "cubes": [
            {
                "name": "maintenance",
                "measures": [
                    "downtime",
                    "failure_count",
                    "mean_downtime",
                    "spare_parts",
                ],
                "measure_synonyms": {
                    "downtime": ["Makine duruşları"],
                    "failure_count": ["arıza sayısı"],
                    "mean_downtime": ["ortalama duruş"],
                    "spare_parts": ["yedek parça"],
                },
                "dimensions": ["department"],
                "dimension_labels": {"department": "bölüm"},
                "dimension_synonyms": {"department": ["bölüm"]},
                "dimension_values": {},
                "time_dimensions": [],
            }
        ],
        "kpis": [],
        "relationships": [],
        "business_rules": "",
        "db_online": True,
    }
    return context, schema


def _d10_p_draft():
    return {
        "obligations": [
            _obligation(
                obligation_id="U_PERFORMANCE",
                capability="performance",
                source_surfaces=("Makine duruşları",),
                semantic_surfaces=(("Makine duruşları", "metric"),),
            ),
            _obligation(
                obligation_id="U_FAILURES",
                capability="performance",
                source_surfaces=("arıza sayısı",),
                semantic_surfaces=(("arıza sayısı", "metric"),),
            ),
            _obligation(
                obligation_id="U_BREAKDOWN",
                capability="breakdown",
                source_surfaces=("bölüm bazındaki performansı",),
                semantic_surfaces=(
                    ("bölüm", "dimension"),
                    ("performansı", "metric"),
                ),
            ),
        ],
        "research_directives": [],
        "control_requests": [],
    }


def test_d10_p_semantic_decomposition_repair_reuses_truth_not_authority():
    question = (
        "Makine duruşları ve arıza sayısı ile bölüm bazındaki performansı araştır."
    )
    context, schema = _d10_p_decomposition_context()
    scripted = _ScriptedStructured(
        drafts=[_d10_p_draft()],
        audits=[{"status": "PASS", "issues": []}],
    )
    repair = _SourceSelectingRepairProvider(
        selected_surfaces=("Makine duruşları", "arıza sayısı"),
    )
    semantic_provider = _SingleCandidateSemanticProvider()
    diagnostics = []
    loop, runtime, executor = _loop(
        scripted,
        semantic_provider=semantic_provider,
        semantic_repair_provider=repair,
        semantic_diagnostic_sink=diagnostics.append,
        semantic_context=context,
        semantic_schema=schema,
    )

    outcome = loop.understand(
        question=question,
        message_id="turn-d10-p-repair",
        request_ref="req-d10-p-repair",
        runtime=runtime,
        executor=executor,
        conversation=ConversationStateV2(),
    )

    assert outcome.accepted is True
    assert outcome.status == FiniteAcceptanceStatus.ACCEPTED
    assert runtime.snapshot.preacceptance_turns == 2
    assert runtime.snapshot.manager_turns == 2
    assert scripted.calls == [
        "dima_intent_draft_v1",
        "dima_intent_coverage_v1",
    ]
    assert len(repair.calls) == 1

    requests, repair_message = repair.calls[0]
    assert repair_message == question
    assert len(requests) == 1
    request = requests[0]
    assert request.obligation_id == "U_BREAKDOWN"
    assert request.missing_kind == "metric"
    assert {
        item.surface for item in request.available_user_source_concepts
    } == {"Makine duruşları", "arıza sayısı"}
    assert all(
        item.kind == "metric"
        for item in request.available_user_source_concepts
    )

    ledger = runtime.ledger
    assert ledger is not None
    items = {item.obligation_id: item for item in ledger.items}
    perf_handle = items["U_PERFORMANCE"].semantic_handle_refs[0]
    failure_handle = items["U_FAILURES"].semantic_handle_refs[0]
    breakdown_metric_handles = [
        ref
        for ref in items["U_BREAKDOWN"].semantic_handle_refs
        if executor._semantic_resolution._handles.validate(
            ref,
            tenant_binding="tenant-stabilized",
            context_version=context.context_version.version,
        ).target_kind in {"metric", "kpi"}
    ]
    assert len(breakdown_metric_handles) == 2
    assert perf_handle not in breakdown_metric_handles
    assert failure_handle not in breakdown_metric_handles

    perf = executor._semantic_resolution._handles.validate(
        perf_handle,
        tenant_binding="tenant-stabilized",
        context_version=context.context_version.version,
    )
    failure = executor._semantic_resolution._handles.validate(
        failure_handle,
        tenant_binding="tenant-stabilized",
        context_version=context.context_version.version,
    )
    repaired = [
        executor._semantic_resolution._handles.validate(
            ref,
            tenant_binding="tenant-stabilized",
            context_version=context.context_version.version,
        )
        for ref in breakdown_metric_handles
    ]
    assert perf.parent_obligation_id == "U_PERFORMANCE"
    assert failure.parent_obligation_id == "U_FAILURES"
    assert {item.parent_obligation_id for item in repaired} == {"U_BREAKDOWN"}
    assert {item.resolver_provenance_id for item in repaired} == {
        perf.resolver_provenance_id,
        failure.resolver_provenance_id,
    }
    assert {item.handle_id for item in repaired}.isdisjoint(
        {perf.handle_id, failure.handle_id}
    )
    assert any(
        item.get("kind") == "semantic_decomposition_repair"
        for item in diagnostics
    )


def test_d10_p_semantic_repair_abstain_remains_clarification():
    question = (
        "Makine duruşları ve arıza sayısı ile bölüm bazındaki performansı araştır."
    )
    context, schema = _d10_p_decomposition_context()
    scripted = _ScriptedStructured(
        drafts=[_d10_p_draft()],
        audits=[{"status": "PASS", "issues": []}],
    )
    repair = _SourceSelectingRepairProvider(abstain=True)
    loop, runtime, executor = _loop(
        scripted,
        semantic_provider=_SingleCandidateSemanticProvider(),
        semantic_repair_provider=repair,
        semantic_context=context,
        semantic_schema=schema,
    )

    outcome = loop.understand(
        question=question,
        message_id="turn-d10-p-abstain",
        request_ref="req-d10-p-abstain",
        runtime=runtime,
        executor=executor,
        conversation=ConversationStateV2(),
    )

    assert outcome.status == FiniteAcceptanceStatus.CLARIFICATION_REQUIRED
    assert runtime.snapshot.preacceptance_turns == 2
    assert len(repair.calls) == 1
    assert scripted.calls == [
        "dima_intent_draft_v1",
        "dima_intent_coverage_v1",
    ]


def test_d10_p_excluded_metric_never_enters_repair_source_pool():
    question = (
        "Makine duruşlarını kullanma; arıza sayısı ile bölüm bazındaki performansı araştır."
    )
    context, schema = _d10_p_decomposition_context()
    draft = _d10_p_draft()
    draft["obligations"][0]["polarity"] = "EXCLUDED"
    draft["obligations"][0]["source_surfaces"] = ["Makine duruşlarını kullanma"]
    draft["obligations"][0]["semantic_surfaces"] = [
        {"surface": "Makine duruşları", "kind_hint": "metric"}
    ]
    scripted = _ScriptedStructured(drafts=[draft], audits=[{"status": "PASS", "issues": []}])
    repair = _SourceSelectingRepairProvider(selected_surfaces=("arıza sayısı",))
    loop, runtime, executor = _loop(
        scripted,
        semantic_provider=_SingleCandidateSemanticProvider(),
        semantic_repair_provider=repair,
        semantic_context=context,
        semantic_schema=schema,
    )

    outcome = loop.understand(
        question=question,
        message_id="turn-d10-p-excluded",
        request_ref="req-d10-p-excluded",
        runtime=runtime,
        executor=executor,
        conversation=ConversationStateV2(),
    )

    assert outcome.accepted is True
    request = repair.calls[0][0][0]
    assert {
        item.surface for item in request.available_user_source_concepts
    } == {"arıza sayısı"}


def test_d10_p_repair_provider_rejects_unknown_source_token():
    question = (
        "Makine duruşları ve arıza sayısı ile bölüm bazındaki performansı araştır."
    )
    context, schema = _d10_p_decomposition_context()
    scripted = _ScriptedStructured(drafts=[_d10_p_draft()], audits=[{"status": "PASS", "issues": []}])

    class BadRepair:
        def decide(self, requests, *, user_message):
            del user_message
            return SemanticDecompositionRepairBatchDecision(
                choices=(
                    SemanticDecompositionRepairChoice(
                        gap_ref=requests[0].gap_ref,
                        decision="SELECT_SOURCES",
                        selected_source_tokens=("s999",),
                        reason="SOURCE_SUPPORTS_SCOPE",
                    ),
                )
            )

    loop, runtime, executor = _loop(
        scripted,
        semantic_provider=_SingleCandidateSemanticProvider(),
        semantic_repair_provider=BadRepair(),
        semantic_context=context,
        semantic_schema=schema,
    )
    outcome = loop.understand(
        question=question,
        message_id="turn-d10-p-bad-token",
        request_ref="req-d10-p-bad-token",
        runtime=runtime,
        executor=executor,
        conversation=ConversationStateV2(),
    )
    assert outcome.status == FiniteAcceptanceStatus.GROUNDING_FAILURE
    assert any(
        item.get("kind") == "semantic_decomposition_repair_error"
        for item in outcome.observations
    )


def test_d10_p_repair_pool_never_borrows_prior_conversation_semantics():
    question = (
        "Makine duruşları ve arıza sayısı ile bölüm bazındaki performansı araştır."
    )
    context, schema = _d10_p_decomposition_context()
    draft = _d10_p_draft()
    scripted = _ScriptedStructured(
        drafts=[draft],
        audits=[{"status": "PASS", "issues": []}],
    )
    repair = _SourceSelectingRepairProvider(
        selected_surfaces=("Makine duruşları", "arıza sayısı"),
    )
    loop, runtime, executor = _loop(
        scripted,
        semantic_provider=_SingleCandidateSemanticProvider(),
        semantic_repair_provider=repair,
        semantic_context=context,
        semantic_schema=schema,
        conversation=ConversationStateV2(
            has_prior_analytical_request=True,
            has_active_result=True,
            focus_labels=("ortalama duruş",),
        ),
    )
    outcome = loop.understand(
        question=question,
        message_id="turn-d10-p-no-prior-borrow",
        request_ref="req-d10-p-no-prior-borrow",
        runtime=runtime,
        executor=executor,
        conversation=ConversationStateV2(
            has_prior_analytical_request=True,
            has_active_result=True,
            focus_labels=("arıza sayısı",),
        ),
    )
    assert outcome.accepted is True
    request = repair.calls[0][0][0]
    assert {
        item.surface for item in request.available_user_source_concepts
    } == {"Makine duruşları", "arıza sayısı"}
    assert "ortalama duruş" not in {
        item.surface for item in request.available_user_source_concepts
    }


def test_d10_p_wrong_kind_current_source_cannot_enter_metric_repair_pool():
    question = "bölüm bazındaki performansı araştır"
    context, schema = _d10_p_decomposition_context()
    draft = {
        "obligations": [
            _obligation(
                obligation_id="U_BREAKDOWN",
                capability="breakdown",
                source_surfaces=("bölüm bazındaki performansı",),
                semantic_surfaces=(("bölüm", "dimension"),),
            ),
        ],
        "research_directives": [],
        "control_requests": [],
    }
    scripted = _ScriptedStructured(drafts=[draft], audits=[{"status": "PASS", "issues": []}])
    repair = _SourceSelectingRepairProvider(selected_surfaces=("bölüm",))
    loop, runtime, executor = _loop(
        scripted,
        semantic_provider=_SingleCandidateSemanticProvider(),
        semantic_repair_provider=repair,
        semantic_context=context,
        semantic_schema=schema,
    )
    outcome = loop.understand(
        question=question,
        message_id="turn-d10-p-wrong-kind",
        request_ref="req-d10-p-wrong-kind",
        runtime=runtime,
        executor=executor,
        conversation=ConversationStateV2(),
    )
    assert outcome.status == FiniteAcceptanceStatus.CLARIFICATION_REQUIRED
    assert repair.calls == []


def test_d10_p_sensitive_dimension_is_not_exposed_as_repair_source():
    context, schema = _d10_p_decomposition_context()
    source_spans = SourceSpanRegistry()
    source_spans.register_message(
        message_id="turn-d10-p-sensitive",
        text="bölüm performans kırılımında",
    )
    source_ref = source_spans.mint_exact(
        message_id="turn-d10-p-sensitive",
        surface="bölüm",
    ).source_ref
    target_ref = source_spans.mint_exact(
        message_id="turn-d10-p-sensitive",
        surface="performans kırılımında",
    ).source_ref
    handles = SemanticHandleRegistry()
    repair = _SourceSelectingRepairProvider(selected_surfaces=("bölüm",))
    adapter = ManagerSemanticResolutionAdapter(
        source_spans=source_spans,
        semantic_handles=handles,
        semantic_context=context,
        conversation=ConversationStateV2(),
        schema=schema,
        tenant_binding="tenant-stabilized",
        session_id="session-stabilized",
        thread_id="thread-stabilized",
        semantic_decision_provider=None,
        semantic_decomposition_repair_provider=repair,
    )
    binding = next(
        item
        for item in adapter._candidate_generator._governed_candidates("dimension")
        if item.card.label.casefold() == "bölüm"
    )
    sensitive_handle = handles.mint_from_binding_gate(
        tenant_binding="tenant-stabilized",
        context_version=context.context_version.version,
        candidate_id=binding.card.candidate_id,
        target_kind=binding.card.target_kind,
        canonical_target=binding.canonical_target,
        sensitive=True,
        provenance_type="USER_SOURCE",
        parent_obligation_id="U_SOURCE",
    )
    runtime = SimpleNamespace(
        semantic_resolution_receipts=(
            SemanticResolutionReceipt(
                source_ref=source_ref,
                handle_id=sensitive_handle.handle_id,
                target_kind=sensitive_handle.target_kind,
            ),
        )
    )
    repaired = adapter.resolve(
        ResolveSemanticsArgs(
            provenance="USER_SOURCE",
            decomposition_repair_gaps=(
                SemanticDecompositionRepairGap(
                    gap_ref="gap:1:U_TARGET:dimension",
                    obligation_id="U_TARGET",
                    capability_key=ManagerCapabilityKey.BREAKDOWN,
                    missing_kind="dimension",
                    obligation_source_refs=(target_ref,),
                ),
            ),
            decomposition_repair_source_refs=(source_ref,),
        ),
        runtime=runtime,
    )

    assert repaired.resolved == ()
    assert repair.calls == []

def test_d10_p_repair_does_not_rewrite_business_intent_shape():
    question = (
        "Makine duruşları ve arıza sayısı ile bölüm bazındaki performansı araştır."
    )
    context, schema = _d10_p_decomposition_context()
    scripted = _ScriptedStructured(
        drafts=[_d10_p_draft()],
        audits=[{"status": "PASS", "issues": []}],
    )
    repair = _SourceSelectingRepairProvider(
        selected_surfaces=("Makine duruşları", "arıza sayısı"),
    )
    loop, runtime, executor = _loop(
        scripted,
        semantic_provider=_SingleCandidateSemanticProvider(),
        semantic_repair_provider=repair,
        semantic_context=context,
        semantic_schema=schema,
    )
    outcome = loop.understand(
        question=question,
        message_id="turn-d10-p-shape",
        request_ref="req-d10-p-shape",
        runtime=runtime,
        executor=executor,
        conversation=ConversationStateV2(),
    )
    assert outcome.accepted is True
    item = next(
        entry for entry in runtime.ledger.items
        if entry.obligation_id == "U_BREAKDOWN"
    )
    assert item.capability_key == ManagerCapabilityKey.BREAKDOWN
    assert item.polarity == ObligationPolarity.REQUIRED
    assert item.origin == ObligationOrigin.USER_MUST
    assert item.priority == ObligationPriority.MUST
    assert len(item.source_refs) == 1
    source_span = executor._semantic_resolution._source_spans.validate(
        item.source_refs[0]
    )
    assert source_span.exact_surface == "bölüm bazındaki performansı"


def test_d10_p_ambiguous_exact_never_enters_decomposition_repair():
    source_spans = SourceSpanRegistry()
    source_spans.register_message(
        message_id="turn-d10-p-ambiguous",
        text="Metric A target",
    )
    source_ref = source_spans.mint_exact(
        message_id="turn-d10-p-ambiguous",
        surface="Metric A",
    ).source_ref
    target_ref = source_spans.mint_exact(
        message_id="turn-d10-p-ambiguous",
        surface="target",
    ).source_ref
    controller = PreAcceptanceController(
        structured=lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("no model call expected")
        ),
        source_spans=source_spans,
    )
    draft = IntentDraft.model_validate(
        {
            "obligations": [
                _obligation(
                    obligation_id="U_SOURCE",
                    capability="performance",
                    source_surfaces=("Metric A",),
                    semantic_surfaces=(("Metric A", "metric"),),
                ),
                _obligation(
                    obligation_id="U_TARGET",
                    capability="root_cause",
                    source_surfaces=("target",),
                    semantic_surfaces=(("target", "metric"),),
                ),
            ],
            "research_directives": [],
            "control_requests": [],
        }
    )
    grounded = {
        ("U_SOURCE", "Metric A", "metric"): SemanticBindingRef(
            source_ref=source_ref,
            handle_id="sem_" + "1" * 24,
            target_kind="metric",
        )
    }
    resolution = SimpleNamespace(
        unresolved_semantics=(
            SimpleNamespace(
                source_ref=target_ref,
                owner_id="U_TARGET",
                kind_hint="metric",
                status="AMBIGUOUS_EXACT",
            ),
        )
    )

    class ForbiddenRuntime:
        def call_tool(self, *_args, **_kwargs):
            raise AssertionError("AMBIGUOUS_EXACT must not invoke repair")

    repaired, repair_result = controller._repair_material_grounding_gaps(
        draft=draft,
        material_gaps=(
            {
                "obligation_id": "U_TARGET",
                "capability": "root_cause",
                "polarity": "REQUIRED",
                "missing_required_kinds": ["metric"],
            },
        ),
        grounded=grounded,
        resolution=resolution,
        message_id="turn-d10-p-ambiguous",
        attempt=1,
        runtime=ForbiddenRuntime(),
        executor=object(),
    )

    assert repaired == grounded
    assert repair_result is None


# D10-Q: explicit multi-concept scope groups are cognition context, never authority.

class _ScopeGroupSelectingRepairProvider:
    def __init__(self, *, unknown=False, abstain_on_multiple=False) -> None:
        self.unknown = unknown
        self.abstain_on_multiple = abstain_on_multiple
        self.calls = []

    def decide(self, requests, *, user_message):
        self.calls.append((requests, user_message))
        choices = []
        for request in requests:
            groups = tuple(request.available_scope_groups)
            if self.abstain_on_multiple and len(groups) > 1:
                choices.append(
                    SemanticDecompositionRepairChoice(
                        gap_ref=request.gap_ref,
                        decision="ABSTAIN",
                        selected_source_tokens=(),
                        selected_group_token=None,
                        reason="AMBIGUOUS_SCOPE",
                    )
                )
            elif groups:
                choices.append(
                    SemanticDecompositionRepairChoice(
                        gap_ref=request.gap_ref,
                        decision="SELECT_SCOPE_GROUP",
                        selected_source_tokens=(),
                        selected_group_token=(
                            "g999" if self.unknown else groups[0].group_token
                        ),
                        reason="SOURCE_SUPPORTS_SCOPE",
                    )
                )
            else:
                choices.append(
                    SemanticDecompositionRepairChoice(
                        gap_ref=request.gap_ref,
                        decision="ABSTAIN",
                        selected_source_tokens=(),
                        selected_group_token=None,
                        reason="INSUFFICIENT_SOURCE_SUPPORT",
                    )
                )
        return SemanticDecompositionRepairBatchDecision(choices=tuple(choices))


def _d10_q_joint_root_draft():
    return {
        "obligations": [
            _obligation(
                obligation_id="U_SCOPE",
                capability="performance",
                source_surfaces=("Makine duruşları ve arıza sayısı",),
                semantic_surfaces=(
                    ("Makine duruşları", "metric"),
                    ("arıza sayısı", "metric"),
                ),
            ),
            _obligation(
                obligation_id="U_ROOT",
                capability="root_cause",
                source_surfaces=("gözlenen bozulmanın kök nedenlerini sınırla",),
                semantic_surfaces=(("gözlenen bozulma", "metric"),),
            ),
        ],
        "research_directives": [],
        "control_requests": [],
    }


def test_d10_q_joint_scope_group_mints_fresh_root_owned_handles():
    question = (
        "Makine duruşları ve arıza sayısı birlikte incelensin; "
        "gözlenen bozulmanın kök nedenlerini sınırla."
    )
    context, schema = _d10_p_decomposition_context()
    scripted = _ScriptedStructured(
        drafts=[_d10_q_joint_root_draft()],
        audits=[{"status": "PASS", "issues": []}],
    )
    repair = _ScopeGroupSelectingRepairProvider()
    loop, runtime, executor = _loop(
        scripted,
        semantic_provider=_SingleCandidateSemanticProvider(),
        semantic_repair_provider=repair,
        semantic_context=context,
        semantic_schema=schema,
    )

    outcome = loop.understand(
        question=question,
        message_id="turn-d10-q-joint",
        request_ref="req-d10-q-joint",
        runtime=runtime,
        executor=executor,
        conversation=ConversationStateV2(),
    )

    assert outcome.accepted is True
    request = repair.calls[0][0][0]
    assert request.obligation_id == "U_ROOT"
    assert request.missing_kind == "metric"
    assert len(request.available_scope_groups) == 1
    group = request.available_scope_groups[0]
    assert len(group.member_source_tokens) == 2
    assert group.supporting_capabilities == ("performance",)

    items = {item.obligation_id: item for item in runtime.ledger.items}
    scope_handles = set(items["U_SCOPE"].semantic_handle_refs)
    root_metric_handles = {
        ref
        for ref in items["U_ROOT"].semantic_handle_refs
        if executor._semantic_resolution._handles.validate(
            ref,
            tenant_binding="tenant-stabilized",
            context_version=context.context_version.version,
        ).target_kind in {"metric", "kpi"}
    }
    assert len(root_metric_handles) == 2
    assert root_metric_handles.isdisjoint(scope_handles)
    assert {
        executor._semantic_resolution._handles.validate(
            ref,
            tenant_binding="tenant-stabilized",
            context_version=context.context_version.version,
        ).parent_obligation_id
        for ref in root_metric_handles
    } == {"U_ROOT"}
    assert {
        executor._semantic_resolution._handles.validate(
            ref,
            tenant_binding="tenant-stabilized",
            context_version=context.context_version.version,
        ).resolver_provenance_id
        for ref in root_metric_handles
    } == {
        executor._semantic_resolution._handles.validate(
            ref,
            tenant_binding="tenant-stabilized",
            context_version=context.context_version.version,
        ).resolver_provenance_id
        for ref in scope_handles
    }
    persisted_authority = json.dumps(
        {
            "contract": runtime.accepted_contract.model_dump(mode="json"),
            "ledger": runtime.ledger.model_dump(mode="json"),
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    assert "available_scope_groups" not in persisted_authority
    assert "selected_group_token" not in persisted_authority


def test_d10_q_unknown_scope_group_token_fails_closed():
    question = (
        "Makine duruşları ve arıza sayısı birlikte incelensin; "
        "gözlenen bozulmanın kök nedenlerini sınırla."
    )
    context, schema = _d10_p_decomposition_context()
    scripted = _ScriptedStructured(drafts=[_d10_q_joint_root_draft()], audits=[{"status": "PASS", "issues": []}])
    repair = _ScopeGroupSelectingRepairProvider(unknown=True)
    loop, runtime, executor = _loop(
        scripted,
        semantic_provider=_SingleCandidateSemanticProvider(),
        semantic_repair_provider=repair,
        semantic_context=context,
        semantic_schema=schema,
    )

    outcome = loop.understand(
        question=question,
        message_id="turn-d10-q-unknown-group",
        request_ref="req-d10-q-unknown-group",
        runtime=runtime,
        executor=executor,
        conversation=ConversationStateV2(),
    )

    assert outcome.status == FiniteAcceptanceStatus.GROUNDING_FAILURE
    assert any(
        item.get("kind") == "semantic_decomposition_repair_error"
        for item in outcome.observations
    )


def test_d10_q_two_materially_distinct_groups_may_abstain_without_forced_merge():
    question = (
        "Makine duruşları ve arıza sayısı birlikte; ortalama duruş ve yedek parça "
        "birlikte değerlendirilsin; gözlenen bozulmanın kök nedenlerini sınırla."
    )
    context, schema = _d10_p_decomposition_context()
    draft = {
        "obligations": [
            _obligation(
                obligation_id="U_SCOPE_A",
                capability="performance",
                source_surfaces=("Makine duruşları ve arıza sayısı",),
                semantic_surfaces=(
                    ("Makine duruşları", "metric"),
                    ("arıza sayısı", "metric"),
                ),
            ),
            _obligation(
                obligation_id="U_SCOPE_B",
                capability="performance",
                source_surfaces=("ortalama duruş ve yedek parça",),
                semantic_surfaces=(
                    ("ortalama duruş", "metric"),
                    ("yedek parça", "metric"),
                ),
            ),
            _obligation(
                obligation_id="U_ROOT",
                capability="root_cause",
                source_surfaces=("gözlenen bozulmanın kök nedenlerini sınırla",),
                semantic_surfaces=(("gözlenen bozulma", "metric"),),
            ),
        ],
        "research_directives": [],
        "control_requests": [],
    }
    scripted = _ScriptedStructured(drafts=[draft], audits=[{"status": "PASS", "issues": []}])
    repair = _ScopeGroupSelectingRepairProvider(abstain_on_multiple=True)
    loop, runtime, executor = _loop(
        scripted,
        semantic_provider=_SingleCandidateSemanticProvider(),
        semantic_repair_provider=repair,
        semantic_context=context,
        semantic_schema=schema,
    )

    outcome = loop.understand(
        question=question,
        message_id="turn-d10-q-distinct-groups",
        request_ref="req-d10-q-distinct-groups",
        runtime=runtime,
        executor=executor,
        conversation=ConversationStateV2(),
    )

    assert outcome.status == FiniteAcceptanceStatus.CLARIFICATION_REQUIRED
    request = repair.calls[0][0][0]
    assert len(request.available_scope_groups) == 2
    assert {
        tuple(group.member_source_tokens)
        for group in request.available_scope_groups
    }
    assert len({
        tuple(group.member_source_tokens)
        for group in request.available_scope_groups
    }) == 2


def test_d10_q_scope_group_generation_is_permutation_stable_and_excludes_excluded():
    controller = PreAcceptanceController(
        structured=lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("no cognition expected")
        ),
        source_spans=SourceSpanRegistry(),
    )
    draft = IntentDraft.model_validate(
        {
            "obligations": [
                _obligation(
                    obligation_id="U_REQUIRED",
                    capability="performance",
                    source_surfaces=("A ve B",),
                    semantic_surfaces=(("A", "metric"), ("B", "metric")),
                ),
                _obligation(
                    obligation_id="X_EXCLUDED",
                    capability="performance",
                    source_surfaces=("C ve D kullanma",),
                    semantic_surfaces=(("C", "metric"), ("D", "metric")),
                    polarity="EXCLUDED",
                ),
            ],
            "research_directives": [],
            "control_requests": [],
        }
    )
    a = SemanticBindingRef(
        source_ref="src_" + "1" * 24,
        handle_id="sem_" + "1" * 24,
        target_kind="metric",
    )
    b = SemanticBindingRef(
        source_ref="src_" + "2" * 24,
        handle_id="sem_" + "2" * 24,
        target_kind="metric",
    )
    c_ref = SemanticBindingRef(
        source_ref="src_" + "3" * 24,
        handle_id="sem_" + "3" * 24,
        target_kind="metric",
    )
    d_ref = SemanticBindingRef(
        source_ref="src_" + "4" * 24,
        handle_id="sem_" + "4" * 24,
        target_kind="metric",
    )
    forward = {
        ("U_REQUIRED", "A", "metric"): a,
        ("U_REQUIRED", "B", "metric"): b,
        ("X_EXCLUDED", "C", "metric"): c_ref,
        ("X_EXCLUDED", "D", "metric"): d_ref,
    }
    reverse = dict(reversed(tuple(forward.items())))

    groups_a = controller._repair_scope_groups(draft=draft, grounded=forward)
    groups_b = controller._repair_scope_groups(draft=draft, grounded=reverse)

    assert groups_a == groups_b
    assert len(groups_a) == 1
    assert groups_a[0].member_source_refs == tuple(
        sorted((a.source_ref, b.source_ref))
    )
    assert groups_a[0].supporting_capabilities == (
        ManagerCapabilityKey.PERFORMANCE,
    )


def test_d10_q_identical_scope_sets_deduplicate_and_merge_supporting_capabilities():
    controller = PreAcceptanceController(
        structured=lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("no cognition expected")
        ),
        source_spans=SourceSpanRegistry(),
    )
    draft = IntentDraft.model_validate(
        {
            "obligations": [
                _obligation(
                    obligation_id="U_PERF",
                    capability="performance",
                    source_surfaces=("A ve B",),
                    semantic_surfaces=(("A", "metric"), ("B", "metric")),
                ),
                _obligation(
                    obligation_id="U_REL",
                    capability="relationship",
                    source_surfaces=("A ve B ilişkisi",),
                    semantic_surfaces=(
                        ("A", "metric"),
                        ("B", "metric"),
                        ("D", "dimension"),
                    ),
                ),
            ],
            "research_directives": [],
            "control_requests": [],
        }
    )
    a_ref = "src_" + "a" * 24
    b_ref = "src_" + "b" * 24
    grounded = {
        ("U_PERF", "A", "metric"): SemanticBindingRef(
            source_ref=a_ref,
            handle_id="sem_" + "1" * 24,
            target_kind="metric",
        ),
        ("U_PERF", "B", "metric"): SemanticBindingRef(
            source_ref=b_ref,
            handle_id="sem_" + "2" * 24,
            target_kind="metric",
        ),
        ("U_REL", "A", "metric"): SemanticBindingRef(
            source_ref=a_ref,
            handle_id="sem_" + "3" * 24,
            target_kind="metric",
        ),
        ("U_REL", "B", "metric"): SemanticBindingRef(
            source_ref=b_ref,
            handle_id="sem_" + "4" * 24,
            target_kind="metric",
        ),
    }

    groups = controller._repair_scope_groups(draft=draft, grounded=grounded)

    assert len(groups) == 1
    assert groups[0].member_source_refs == (a_ref, b_ref)
    assert groups[0].supporting_capabilities == (
        ManagerCapabilityKey.PERFORMANCE,
        ManagerCapabilityKey.RELATIONSHIP,
    )


def test_d10_q_scope_group_selection_is_atomic_when_member_revalidation_fails(monkeypatch):
    context, schema = _d10_p_decomposition_context()
    source_spans = SourceSpanRegistry()
    message_id = "turn-d10-q-atomic"
    question = "Makine duruşları ve arıza sayısı; hedef"
    source_spans.register_message(message_id=message_id, text=question)
    ref_a = source_spans.mint_exact(
        message_id=message_id, surface="Makine duruşları"
    ).source_ref
    ref_b = source_spans.mint_exact(
        message_id=message_id, surface="arıza sayısı"
    ).source_ref
    target_ref = source_spans.mint_exact(
        message_id=message_id, surface="hedef"
    ).source_ref
    handles = SemanticHandleRegistry()
    repair = _ScopeGroupSelectingRepairProvider()
    adapter = ManagerSemanticResolutionAdapter(
        source_spans=source_spans,
        semantic_handles=handles,
        semantic_context=context,
        conversation=ConversationStateV2(),
        schema=schema,
        tenant_binding="tenant-stabilized",
        session_id="session-stabilized",
        thread_id="thread-stabilized",
        semantic_decision_provider=None,
        semantic_decomposition_repair_provider=repair,
    )

    governed = {
        item.card.label: item
        for item in adapter._candidate_generator._governed_candidates("metric")
    }
    runtime_receipts = []
    for ref, label, owner in (
        (ref_a, "Makine duruşları", "U_A"),
        (ref_b, "arıza sayısı", "U_B"),
    ):
        binding = governed[label]
        handle = handles.mint_from_binding_gate(
            tenant_binding="tenant-stabilized",
            context_version=context.context_version.version,
            candidate_id=binding.card.candidate_id,
            target_kind=binding.card.target_kind,
            canonical_target=binding.canonical_target,
            sensitive=False,
            provenance_type="USER_SOURCE",
            parent_obligation_id=owner,
        )
        runtime_receipts.append(
            SemanticResolutionReceipt(
                source_ref=ref,
                handle_id=handle.handle_id,
                target_kind=handle.target_kind,
            )
        )
    runtime = SimpleNamespace(
        semantic_resolution_receipts=tuple(runtime_receipts)
    )

    original = adapter._governed_repair_source
    counts = {ref_a: 0, ref_b: 0}

    def flaky_revalidation(**kwargs):
        source_ref = kwargs["source_ref"]
        counts[source_ref] += 1
        if source_ref == ref_b and counts[source_ref] >= 2:
            return None
        return original(**kwargs)

    monkeypatch.setattr(adapter, "_governed_repair_source", flaky_revalidation)
    bind_calls = []
    original_bind = adapter._binding_gate.bind

    def record_bind(**kwargs):
        bind_calls.append(kwargs)
        return original_bind(**kwargs)

    monkeypatch.setattr(adapter._binding_gate, "bind", record_bind)

    with pytest.raises(ValueError, match="failed revalidation"):
        adapter.resolve(
            ResolveSemanticsArgs(
                provenance="USER_SOURCE",
                decomposition_repair_gaps=(
                    SemanticDecompositionRepairGap(
                        gap_ref="gap:1:U_ROOT:metric",
                        obligation_id="U_ROOT",
                        capability_key=ManagerCapabilityKey.ROOT_CAUSE,
                        missing_kind="metric",
                        obligation_source_refs=(target_ref,),
                    ),
                ),
                decomposition_repair_source_refs=(ref_a, ref_b),
                decomposition_repair_scope_groups=(
                    SemanticDecompositionRepairScopeGroup(
                        kind="metric",
                        member_source_refs=(ref_a, ref_b),
                        supporting_capabilities=(
                            ManagerCapabilityKey.PERFORMANCE,
                        ),
                    ),
                ),
            ),
            runtime=runtime,
        )
    assert bind_calls == []


def test_d10_q_repair_scope_group_args_reject_foreign_member():
    with pytest.raises(ValueError, match="members must belong to source pool"):
        ResolveSemanticsArgs(
            provenance="USER_SOURCE",
            decomposition_repair_gaps=(
                SemanticDecompositionRepairGap(
                    gap_ref="gap:1:U_ROOT:metric",
                    obligation_id="U_ROOT",
                    capability_key=ManagerCapabilityKey.ROOT_CAUSE,
                    missing_kind="metric",
                    obligation_source_refs=("src_" + "9" * 24,),
                ),
            ),
            decomposition_repair_source_refs=("src_" + "1" * 24,),
            decomposition_repair_scope_groups=(
                SemanticDecompositionRepairScopeGroup(
                    kind="metric",
                    member_source_refs=(
                        "src_" + "1" * 24,
                        "src_" + "2" * 24,
                    ),
                    supporting_capabilities=(
                        ManagerCapabilityKey.PERFORMANCE,
                    ),
                ),
            ),
        )
