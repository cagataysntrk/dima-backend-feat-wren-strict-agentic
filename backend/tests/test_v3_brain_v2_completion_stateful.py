from __future__ import annotations

from types import SimpleNamespace

from hypothesis import settings
from hypothesis.stateful import RuleBasedStateMachine, invariant, precondition, rule

from app.v3.brain_v2.material_groups import project_material_groups
from app.v3.brain_v2.owner_adapter import DimaBrainV2Activities
from app.v3.brain_v2.state import BrainGraphState
from app.v3.business_relationship_policy import RelationshipPolicyResolutionStatus
from control_plane.authorize import Principal

from app.v3.research_contracts import (
    PresentationKind,
    RankingSurface,
    RelationshipIntent,
    ResearchBrief,
    ResearchBriefStatus,
    ResearchDeliverableRequirement,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchQuestion,
    ResearchScope,
    ResearchSemanticRef,
    ScopeVersion,
    SemanticTargetKind,
)


def metric(cid: str):
    return ResearchSemanticRef(
        source_mention=cid,
        candidate_id=cid,
        target_kind=SemanticTargetKind.METRIC,
        canonical_name=cid,
        cube_names=("machine_operations",),
    )


def dimension(cid: str):
    return ResearchSemanticRef(
        source_mention=cid,
        candidate_id=cid,
        target_kind=SemanticTargetKind.DIMENSION,
        canonical_name=cid,
        cube_names=("machine_operations",),
    )


DOWN = metric("metric.downtime")
FAULT = metric("metric.faults")
DEPT = dimension("dimension.department")


def accepted_brief() -> ResearchBrief:
    ranking = ResearchQuestion(
        goal_id="g_rank",
        kind=ResearchGoalKind.RANKING,
        source_text="Rank downtime by department.",
        source_fragment_identity="fragment-sha256:" + "1" * 64,
        subject_refs=(DEPT, DOWN),
        ranking=RankingSurface(
            text="rank downtime",
            direction="desc",
            measure_semantic_id=DOWN.candidate_id,
        ),
        status=ResearchGoalStatus.RESOLVED,
    )
    relationship = ResearchQuestion(
        goal_id="g_rel",
        kind=ResearchGoalKind.RELATIONSHIP,
        source_text="Assess downtime with faults by department.",
        source_fragment_identity="fragment-sha256:" + "2" * 64,
        subject_refs=(DOWN, FAULT),
        related_refs=(DEPT,),
        relationship_intent=RelationshipIntent.OBSERVATIONAL,
        status=ResearchGoalStatus.RESOLVED,
    )
    report = ResearchDeliverableRequirement(
        requirement_id="d_report",
        kind=PresentationKind.REPORT,
        source_text="Present governed outcomes.",
    )
    return ResearchBrief(
        brief_id="rb_completion_stateful",
        objective="Stateful completion authority.",
        scope=ResearchScope(
            semantic_refs=(DOWN, FAULT, DEPT),
            scope_version=ScopeVersion(version_id="scope_v1", ordinal=1),
        ),
        questions=(ranking, relationship),
        deliverables=(report,),
        must_requirement_ids=("g_rank", "g_rel", "d_report"),
        context_version="ctx_completion_stateful",
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )


class CompletionOwnerHarness(DimaBrainV2Activities):
    def __init__(self):
        self._principal = Principal(
            user_id="00000000-0000-4000-8000-000000009901",
            tenant_id="00000000-0000-4000-8000-000000009902",
            tenant_slug="completion-stateful",
            roles=["analyst"],
        )
        self.session = SimpleNamespace(
            accepted_brief=accepted_brief(),
            session_id="rs_" + "1" * 24,
            context_version="ctx_completion_stateful",
            authority_id="atc_completion_stateful",
            lineage_id="atl_completion_stateful",
        )
        self._relationships = SimpleNamespace(
            load_use=lambda **kwargs: SimpleNamespace(
                resolution_status=RelationshipPolicyResolutionStatus.NOT_REQUIRED,
                policy_use_id=kwargs["policy_use_id"],
                policy_id=None,
                limitation_code=None,
            )
        )

    def _session(self, state):
        return self.session

    def _evidence_pairs(self, session, obligation_id):
        del session, obligation_id
        return (("evi_" + "2" * 24, "dqr_" + "3" * 24),)


class CompletionOwnerStateMachine(RuleBasedStateMachine):
    """Integrated production completion-owner sequencing over typed authorities."""

    def __init__(self):
        super().__init__()
        self.owner = CompletionOwnerHarness()
        groups = project_material_groups(self.owner.session)
        assert len(groups) == 1
        self.group_id = groups[0].material_group_id
        self.material_done = False
        self.p18_done = False
        self.report_done = False
        self.revision = 0
        self.last = None

    def state(self) -> BrainGraphState:
        p18 = self.p18_done
        report = self.report_done
        return BrainGraphState(
            thread_id="completion-stateful",
            tenant_binding="id:00000000-0000-4000-8000-000000009902",
            principal_ref="00000000-0000-4000-8000-000000009901",
            research_session_id=self.owner.session.session_id,
            accepted_brief_ref=self.owner.session.accepted_brief.brief_id,
            scope_version_id="scope_v1",
            open_requirement_ids=("g_rank", "g_rel", "d_report"),
            material_requirement_ids=("g_rank", "g_rel"),
            material_group_ids=(self.group_id,),
            completed_material_group_ids=(
                (self.group_id,) if self.material_done else ()
            ),
            direct_requirement_ids=("g_rank",),
            relationship_requirement_ids=("g_rel",),
            report_requirement_ids=("d_report",),
            evidence_revision=1 if self.material_done else 0,
            evidence_ids=(("evi_" + "2" * 24,) if self.material_done else ()),
            p18_requirement_ids=(("g_rel",) if p18 else ()),
            p18_claim_refs=(("clm_" + "4" * 24,) if p18 else ()),
            p18_policy_use_refs=(("bru_" + "5" * 24,) if p18 else ()),
            completion_revision=self.revision,
            report_ref=("p20r_" + "6" * 24 if report else None),
        )

    def evaluate(self):
        self.last = self.owner.evaluate_completion(self.state())
        self.revision = self.last.completion_revision

    @rule()
    def evaluate_any_state(self):
        self.evaluate()

    @rule()
    @precondition(lambda self: not self.material_done)
    def complete_material(self):
        self.material_done = True
        self.evaluate()

    @rule()
    @precondition(lambda self: self.material_done and not self.p18_done)
    def complete_relationship(self):
        self.p18_done = True
        self.evaluate()

    @rule()
    @precondition(
        lambda self: self.material_done and self.p18_done and not self.report_done
    )
    def seal_report(self):
        self.report_done = True
        self.evaluate()

    @invariant()
    def terminal_accounting_never_impersonates_fulfillment(self):
        if self.last is None:
            return
        if not self.report_done:
            assert self.last.requirement_complete is False
        if self.material_done and self.p18_done and self.report_done:
            assert self.last.all_requirements_terminal is True
            assert self.last.requirement_complete is True
            assert set(self.last.terminal_requirement_ids) == {
                "g_rank",
                "g_rel",
                "d_report",
            }

    @invariant()
    def report_never_terminalizes_open_analytics_by_itself(self):
        if self.last is None:
            return
        if self.report_done and not (self.material_done and self.p18_done):
            assert self.last.analytical_complete is False
            assert self.last.requirement_complete is False


TestCompletionOwnerStateMachine = CompletionOwnerStateMachine.TestCase
TestCompletionOwnerStateMachine.settings = settings(
    max_examples=200,
    stateful_step_count=12,
    deadline=None,
)
