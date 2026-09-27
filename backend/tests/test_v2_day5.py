"""Focused Day 5 Core MVP presentation/integration contracts.

No demo database literals and no implementation-generated SQL oracle are used here.
The fixtures deliberately use opaque/permuted canonical identifiers.
"""

from __future__ import annotations

import inspect

from app.v2.finalizer import ConversationFinalizerV0
from app.v2.models import (
    AnalyticsIR,
    AskV2Day4Response,
    CandidateSource,
    ClarificationChip,
    ClarificationReason,
    ClarificationState,
    ContextVersionV0,
    ConversationResponseKind,
    ConversationStateV2,
    DialogueAction,
    ExecutionResultV0,
    MinimumQueryContract,
    ResolutionStatus,
    ResolvedFilterRef,
    ResolvedPeriod,
    ResolvedSemanticRef,
    ResultAnchorV0,
    ResultExecutionAnchorV0,
    SemanticCandidate,
    SemanticHypothesis,
    SemanticMentionKind,
    SemanticTargetKind,
    TenantAnalyticsRuntimeV0,
)


def runtime() -> TenantAnalyticsRuntimeV0:
    return TenantAnalyticsRuntimeV0(
        tenant_id="tenant-x",
        tenant_slug="tenant-x",
        principal_user_id="user-x",
        roles=("analyst",),
        mdl_version="mdl-permuted-7",
        db_online=True,
    )


def context_version() -> ContextVersionV0:
    return ContextVersionV0(
        version="ctx-permuted-11",
        mdl_version="mdl-permuted-7",
        compact_catalog_builder_version="test-v1",
        business_rules_hash="0" * 64,
        prompt_context_policy_version="test-v1",
    )


def metric_ref() -> ResolvedSemanticRef:
    return ResolvedSemanticRef(
        candidate_id="cand-metric",
        target_kind=SemanticTargetKind.METRIC,
        canonical_name="metric_z91",
        cube_names=("cube_q17",),
    )


def dimension_ref() -> ResolvedSemanticRef:
    return ResolvedSemanticRef(
        candidate_id="cand-dimension",
        target_kind=SemanticTargetKind.DIMENSION,
        canonical_name="axis_k22",
        cube_names=("cube_q17",),
    )


def hypotheses() -> tuple[SemanticHypothesis, ...]:
    return (
        SemanticHypothesis(
            source_mention="performans",
            mention_kind=SemanticMentionKind.METRIC,
            status=ResolutionStatus.RESOLVED,
            candidates=(
                SemanticCandidate(
                    candidate_id="cand-metric",
                    target_kind=SemanticTargetKind.METRIC,
                    canonical_name="metric_z91",
                    cube_names=("cube_q17",),
                    display_label="Performans",
                    provenance=(CandidateSource.CANONICAL_NAME,),
                    score=1.0,
                ),
            ),
            resolved_candidate_id="cand-metric",
        ),
        SemanticHypothesis(
            source_mention="hat",
            mention_kind=SemanticMentionKind.DIMENSION,
            status=ResolutionStatus.RESOLVED,
            candidates=(
                SemanticCandidate(
                    candidate_id="cand-dimension",
                    target_kind=SemanticTargetKind.DIMENSION,
                    canonical_name="axis_k22",
                    cube_names=("cube_q17",),
                    display_label="Hat",
                    provenance=(CandidateSource.CANONICAL_NAME,),
                    score=1.0,
                ),
            ),
            resolved_candidate_id="cand-dimension",
        ),
    )


def analytics_ir(*, sensitive_filter: bool = False) -> AnalyticsIR:
    return AnalyticsIR(
        cube="cube_q17",
        metrics=(metric_ref(),),
        dimensions=(dimension_ref(),),
        filters=(
            ResolvedFilterRef(
                candidate_id="cand-filter",
                dimension_name="axis_k22",
                value="SECRET-UNIT" if sensitive_filter else "UNIT-Z17",
                cube_names=("cube_q17",),
                sensitive=sensitive_filter,
            ),
        ),
        period=ResolvedPeriod(
            kind="this_month",
            source_text="bu ay",
            time_dimension="time_t8",
            start="2026-09-01",
            end="2026-09-21",
        ),
        context_version="ctx-permuted-11",
    )


def contract() -> MinimumQueryContract:
    return MinimumQueryContract(
        contract_id="contract-1",
        execution_id="exec-1",
        request_ref="req-1",
        planner_id="cube-planner-v2",
        planner_version="day3-v0",
        mdl_version="mdl-permuted-7",
        context_version="ctx-permuted-11",
        executed_sql="SELECT governed_result",
        result_hash="hash-1",
        tenant_id="tenant-x",
        principal_user_id="user-x",
        principal_roles=("analyst",),
        cube_query={"cube": "cube_q17"},
        analytics_ir={"cube": "cube_q17"},
        durability="db",
        sealed=True,
    )


def test_verified_answer_finalizes_only_typed_result_and_evidence():
    core = AskV2Day4Response(
        dialogue_action=DialogueAction.ANALYTIC_STANDARD,
        semantic_status="resolved",
        analytics_status="verified",
        official_verified=True,
        runtime=runtime(),
        context_version=context_version(),
        hypotheses=hypotheses(),
        analytics_ir=analytics_ir(),
        executions=(
            ExecutionResultV0(
                execution_id="exec-1",
                role="primary",
                columns=("axis_k22", "metric_z91"),
                rows=({"axis_k22": "UNIT-Z17", "metric_z91": 42.5},),
                row_count=1,
                verified=True,
            ),
        ),
        query_contracts=(contract(),),
        conversation=ConversationStateV2(),
        query_execution_count=1,
    )

    out = ConversationFinalizerV0().finalize(core)

    assert out.stage == "day5_core_mvp"
    assert out.response.kind == ConversationResponseKind.ANSWER
    assert out.response.official_verified is True
    assert "42.5" in out.response.text
    assert [chip.label for chip in out.response.scope_chips[:2]] == ["Performans", "Hat"]
    assert out.response.evidence_refs[0].contract_id == "contract-1"
    assert out.response.tables[0].rows[0]["metric_z91"] == 42.5


def test_sensitive_filter_value_never_becomes_visible_scope_chip():
    core = AskV2Day4Response(
        dialogue_action=DialogueAction.ANALYTIC_STANDARD,
        semantic_status="resolved",
        analytics_status="verified",
        official_verified=True,
        runtime=runtime(),
        context_version=context_version(),
        hypotheses=hypotheses(),
        analytics_ir=analytics_ir(sensitive_filter=True),
        executions=(
            ExecutionResultV0(
                execution_id="exec-1",
                role="primary",
                columns=("metric_z91",),
                rows=({"metric_z91": 7},),
                row_count=1,
                verified=True,
            ),
        ),
        query_contracts=(contract(),),
        conversation=ConversationStateV2(),
        query_execution_count=1,
    )

    out = ConversationFinalizerV0().finalize(core)
    labels = [chip.label for chip in out.response.scope_chips]
    assert "SECRET-UNIT" not in labels
    assert "Filtre uygulandı" in labels


def test_clarification_preserves_signed_chip_and_has_no_query():
    clarification = ClarificationState(
        pending=True,
        clarification_id="clar-1",
        source_mention="premium",
        source_kind=SemanticMentionKind.FILTER,
        reason=ClarificationReason.MATERIAL_AMBIGUITY,
        question="“premium” ile hangisini kastediyorsun?",
        chips=(
            ClarificationChip(candidate_id="c1", label="Segment = Premium", token="signed-token"),
        ),
    )
    core = AskV2Day4Response(
        dialogue_action=DialogueAction.CLARIFY,
        semantic_status="clarification_required",
        analytics_status="not_applicable",
        runtime=runtime(),
        context_version=context_version(),
        clarification=clarification,
        conversation=ConversationStateV2(
            pending_clarification=True,
            clarification_state=clarification,
        ),
        query_execution_count=0,
    )

    out = ConversationFinalizerV0().finalize(core)

    assert out.response.kind == ConversationResponseKind.CLARIFY
    assert out.query_execution_count == 0
    assert out.response.clarification_chips[0].token == "signed-token"
    assert out.response.tables == ()


def test_result_explain_uses_existing_verified_result_without_query():
    anchor = ResultAnchorV0(
        contract_refs=("contract-old",),
        result_hashes=("hash-old",),
        executions=(
            ResultExecutionAnchorV0(
                execution_id="exec-old",
                role="primary",
                columns=("metric_alt",),
                rows=({"metric_alt": 19},),
                row_count=1,
            ),
        ),
        verified=True,
    )
    prior_ir = AnalyticsIR(
        cube="cube_alt",
        metrics=(
            ResolvedSemanticRef(
                candidate_id="m-alt",
                target_kind=SemanticTargetKind.METRIC,
                canonical_name="metric_alt",
                cube_names=("cube_alt",),
            ),
        ),
        context_version="ctx-permuted-11",
    )
    core = AskV2Day4Response(
        dialogue_action=DialogueAction.EXPLAIN_EXISTING,
        semantic_status="not_applicable",
        analytics_status="not_applicable",
        runtime=runtime(),
        context_version=context_version(),
        existing_result=anchor,
        conversation=ConversationStateV2(
            has_prior_analytical_request=True,
            has_active_result=True,
            last_ir=prior_ir,
            last_result=anchor,
        ),
        query_execution_count=0,
        used_existing_result=True,
    )

    out = ConversationFinalizerV0().finalize(core)

    assert out.response.kind == ConversationResponseKind.EXPLAIN
    assert out.query_execution_count == 0
    assert "19" in out.response.text
    assert out.response.evidence_refs[0].contract_id == "contract-old"


def test_social_is_nonempty_and_never_claims_verified_data():
    core = AskV2Day4Response(
        dialogue_action=DialogueAction.TALK,
        semantic_status="not_applicable",
        analytics_status="not_applicable",
        runtime=runtime(),
        context_version=context_version(),
        conversation=ConversationStateV2(),
        query_execution_count=0,
    )
    out = ConversationFinalizerV0().finalize(core)
    assert out.response.kind == ConversationResponseKind.TALK
    assert out.response.text.strip()
    assert out.response.official_verified is False
    assert out.response.evidence_refs == ()


def test_finalizer_has_no_semantic_or_execution_authority_imports():
    source = inspect.getsource(__import__("app.v2.finalizer", fromlist=["*"]))
    for forbidden in (
        "WrenService",
        "SemanticResolver",
        "TurnInterpreter",
        "CubePlanner",
        "dry_plan(",
        ".query(",
    ):
        assert forbidden not in source
