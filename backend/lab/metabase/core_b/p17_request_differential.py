#!/usr/bin/env python3
"""Provider-free P17 request-envelope differential proof.

No provider/network calls. The harness stops at the exact structured cognition
boundary and compares historical isolated-diagnostic identity with the frozen
sentinel namespace, then proves the corrected diagnostic namespace yields the
same provider-bound envelope independent of prior role-call ordinal.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from app.v3.research_contracts import (
    PresentationKind,
    ResearchBrief,
    ResearchBriefStatus,
    ResearchDeliverableRequirement,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchQuestion,
    ResearchScope,
    ResearchSemanticRef,
    SemanticTargetKind,
)
from app.v3.research_manager import (
    InvestigationActionProfile,
    InvestigationActionRule,
    InvestigationBranchBehavior,
    InvestigationBranchKeyPolicy,
    InvestigationGraph,
    InvestigationIntent,
    InvestigationTargetKind,
    ParentObligationView,
    ResearchManagerSnapshot,
)
from app.v3.research_manager_provider import StructuredResearchProposalManager
from app.v3.research_product import ResearchAskOrchestrator, ResearchBriefAuthoritySealer
from app.v3.structured_trace import (
    StructuredRequestIdentity,
    build_provider_bound_payload,
    json_fingerprint,
    request_identity,
)


MODEL = "openai/gpt-5.6-luna"
OWNER = "p17_research_manager"
ROOT_CASE_ID = "root_cause_tr"
SENTINEL_REQUEST_REF = f"sentinel:{ROOT_CASE_ID}"
HISTORICAL_DIAGNOSTIC_REQUEST_REF = f"diagnostic:{ROOT_CASE_ID}"
TENANT = "id:00000000-0000-4000-8000-000000006801"
PRINCIPAL = "00000000-0000-4000-8000-000000006802"
SOURCE_MESSAGE = (
    "Makine duruşlarındaki bozulmanın olası kök nedenlerini doğrulanmış "
    "kanıtlarla sınırla; kesin nedensellik iddia etmeden raporla."
)
SOURCE_HASH = hashlib.sha256(SOURCE_MESSAGE.encode("utf-8")).hexdigest()


class EnvelopeCaptured(RuntimeError):
    def __init__(self, identity: StructuredRequestIdentity) -> None:
        super().__init__(identity.request_envelope_fingerprint)
        self.identity = identity


class CaptureTransport:
    """Exact payload builder with no HTTP call."""

    def __init__(self, *, prior_role_calls: int = 0) -> None:
        self.call_count = prior_role_calls

    def structured_json(
        self,
        system: str,
        user: str,
        *,
        schema: dict[str, Any],
        schema_name: str,
    ) -> str:
        ordinal = self.call_count + 1
        payload = build_provider_bound_payload(
            model=MODEL,
            system=system,
            user=user,
            schema=schema,
            schema_name=schema_name,
            max_tokens=4096,
            provider_routing_policy={"require_parameters": True},
        )
        identity = request_identity(
            owner=OWNER,
            payload=payload,
            schema_name=schema_name,
            schema=schema,
            system=system,
            user=user,
            call_ordinal_by_role=ordinal,
        )
        self.call_count = ordinal
        raise EnvelopeCaptured(identity)


def _brief() -> ResearchBrief:
    metric = ResearchSemanticRef(
        source_mention="makine duruşları",
        candidate_id="metric.machine_downtime_minutes",
        target_kind=SemanticTargetKind.METRIC,
        canonical_name="Machine Downtime Minutes",
        cube_names=("machine_operations",),
    )
    dimension = ResearchSemanticRef(
        source_mention="bölüm",
        candidate_id="dimension.department",
        target_kind=SemanticTargetKind.DIMENSION,
        canonical_name="Department",
        cube_names=("machine_operations",),
    )
    question = ResearchQuestion(
        goal_id="g_root_cause_downtime",
        kind=ResearchGoalKind.ROOT_CAUSE,
        source_text=SOURCE_MESSAGE,
        subject_refs=(metric,),
        related_refs=(dimension,),
        status=ResearchGoalStatus.RESOLVED,
    )
    deliverable = ResearchDeliverableRequirement(
        requirement_id="d_root_cause_report",
        kind=PresentationKind.REPORT,
        source_text="kanıta bağlı raporla",
    )
    return ResearchBrief(
        brief_id="rb_core_b_root_cause_diff",
        objective=SOURCE_MESSAGE,
        scope=ResearchScope(semantic_refs=(metric, dimension)),
        questions=(question,),
        deliverables=(deliverable,),
        must_requirement_ids=(question.goal_id, deliverable.requirement_id),
        context_version="ctx-core-b-neutral-v1",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )


def _authority(request_ref: str):
    brief = _brief()
    authority = ResearchBriefAuthoritySealer.seal(
        brief=brief,
        request_ref=request_ref,
        source_message_hash=SOURCE_HASH,
    )
    session_id = ResearchAskOrchestrator._session_id(
        authority.contract_id,
        TENANT,
        PRINCIPAL,
    )
    return brief, authority, session_id


def _action_profile() -> InvestigationActionProfile:
    return InvestigationActionProfile(
        rules=(
            InvestigationActionRule(
                intent=InvestigationIntent.INVESTIGATE_GAP,
                legal_parent_step_ids=(),
                allow_parentless=True,
                branch_behavior=InvestigationBranchBehavior.ROOT_OR_INHERIT,
                branch_key_policy=InvestigationBranchKeyPolicy.FORBIDDEN,
                depth_delta=0,
            ),
            InvestigationActionRule(
                intent=InvestigationIntent.STOP_INVESTIGATION,
                legal_parent_step_ids=(),
                allow_parentless=True,
                branch_behavior=InvestigationBranchBehavior.GLOBAL_CONTROL,
                branch_key_policy=InvestigationBranchKeyPolicy.FORBIDDEN,
                depth_delta=0,
            ),
        ),
        max_depth=5,
    )


def _snapshot(request_ref: str) -> ResearchManagerSnapshot:
    brief, authority, session_id = _authority(request_ref)
    question = brief.questions[0]
    profile = _action_profile()
    return ResearchManagerSnapshot(
        research_session_id=session_id,
        research_authority_id=authority.contract_id,
        source_revision=2,
        objective=brief.objective,
        parent_obligations=(
            ParentObligationView(
                obligation_id=question.goal_id,
                objective=question.source_text,
                state="VERIFIED",
            ),
        ),
        evidence_refs=("evi_" + "1" * 24,),
        material_refs=(),
        materials=(),
        action_profile=profile,
        claims=(),
        investigation=InvestigationGraph(
            nodes=(),
            root_step_ids=(),
            open_branch_ids=(),
            stopped_branch_ids=(),
            max_observed_depth=0,
        ),
        limitation_refs=(),
        completed_reasoning_steps=(),
        pending_reasoning_steps=(),
        remaining_reasoning_steps=8,
        remaining_followup_native_turns=4,
        remaining_counter_evidence_attempts=2,
        terminal_stop_reason=None,
    )


def _state_identity(snapshot: ResearchManagerSnapshot) -> dict[str, str]:
    profile = snapshot.action_profile.model_dump(mode="json")
    return {
        "snapshot_fingerprint": snapshot.fingerprint,
        "action_profile_fingerprint": json_fingerprint(profile),
        "state_action_profile_fingerprint": json_fingerprint(
            {
                "snapshot_fingerprint": snapshot.fingerprint,
                "action_profile": profile,
            }
        ),
    }


def _capture(
    snapshot: ResearchManagerSnapshot,
    *,
    prior_role_calls: int,
) -> StructuredRequestIdentity:
    transport = CaptureTransport(prior_role_calls=prior_role_calls)
    manager = StructuredResearchProposalManager(transport=transport)
    try:
        manager.propose(snapshot)
    except EnvelopeCaptured as captured:
        return captured.identity
    raise AssertionError("P17 differential must stop before provider execution")


def _trace_fields(value: StructuredRequestIdentity) -> dict[str, Any]:
    return value.model_dump(mode="json")


def run_differential() -> dict[str, Any]:
    historical_snapshot = _snapshot(HISTORICAL_DIAGNOSTIC_REQUEST_REF)
    sentinel_snapshot = _snapshot(SENTINEL_REQUEST_REF)
    pre_root_snapshot = _snapshot(SENTINEL_REQUEST_REF)

    historical_trace = _capture(historical_snapshot, prior_role_calls=0)
    sentinel_isolated_trace = _capture(sentinel_snapshot, prior_role_calls=0)

    # Full sentinel executes std_breakdown_tr and relationship_explicit_tr first.
    # Role-call history is represented separately from the provider-bound JSON;
    # the root session state itself remains isolated by ResearchSession identity.
    sentinel_pre_root_trace = _capture(
        pre_root_snapshot,
        prior_role_calls=7,
    )

    historical_state = _state_identity(historical_snapshot)
    sentinel_state = _state_identity(sentinel_snapshot)

    historical_vs_sentinel = {
        "authority_id_equal": (
            historical_snapshot.research_authority_id
            == sentinel_snapshot.research_authority_id
        ),
        "session_id_equal": (
            historical_snapshot.research_session_id
            == sentinel_snapshot.research_session_id
        ),
        "schema_fingerprint_equal": (
            historical_trace.schema_fingerprint
            == sentinel_isolated_trace.schema_fingerprint
        ),
        "system_prompt_hash_equal": (
            historical_trace.system_prompt_hash
            == sentinel_isolated_trace.system_prompt_hash
        ),
        "user_prompt_hash_equal": (
            historical_trace.user_prompt_hash
            == sentinel_isolated_trace.user_prompt_hash
        ),
        "request_envelope_fingerprint_equal": (
            historical_trace.request_envelope_fingerprint
            == sentinel_isolated_trace.request_envelope_fingerprint
        ),
        "state_action_profile_fingerprint_equal": (
            historical_state["state_action_profile_fingerprint"]
            == sentinel_state["state_action_profile_fingerprint"]
        ),
    }

    fixed_identity_fields = (
        "schema_fingerprint",
        "system_prompt_hash",
        "user_prompt_hash",
        "request_envelope_fingerprint",
        "response_format_family",
        "max_tokens",
        "provider_routing_policy_fingerprint",
    )
    fixed_equal = all(
        getattr(sentinel_isolated_trace, field)
        == getattr(sentinel_pre_root_trace, field)
        for field in fixed_identity_fields
    )
    state_equal = (
        _state_identity(sentinel_snapshot)["state_action_profile_fingerprint"]
        == _state_identity(pre_root_snapshot)["state_action_profile_fingerprint"]
    )

    classification = (
        "IDENTICAL"
        if fixed_equal and state_equal
        else "DIVERGENT"
    )
    return {
        "schema_version": "core_b_p17_request_differential_v1",
        "case_id": ROOT_CASE_ID,
        "model": MODEL,
        "historical_first_divergence_owner": "diagnostic_request_ref_namespace",
        "historical_request_ref": HISTORICAL_DIAGNOSTIC_REQUEST_REF,
        "frozen_sentinel_request_ref": SENTINEL_REQUEST_REF,
        "historical_vs_frozen_sentinel": historical_vs_sentinel,
        "corrected_isolated": {
            "request_ref": SENTINEL_REQUEST_REF,
            "state_identity": _state_identity(sentinel_snapshot),
            "trace": _trace_fields(sentinel_isolated_trace),
        },
        "pre_root_topology": {
            "prior_case_ids": [
                "std_breakdown_tr",
                "relationship_explicit_tr",
            ],
            "simulated_prior_p17_role_calls": 7,
            "state_identity": _state_identity(pre_root_snapshot),
            "trace": _trace_fields(sentinel_pre_root_trace),
        },
        "comparison_fields": list(fixed_identity_fields),
        "classification": classification,
        "product_semantics_changed": False,
        "provider_calls": 0,
        "full_sentinel_rerun": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    receipt = run_differential()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if receipt["classification"] == "IDENTICAL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
