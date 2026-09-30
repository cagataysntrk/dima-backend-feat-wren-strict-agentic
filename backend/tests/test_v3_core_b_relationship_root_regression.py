from __future__ import annotations

from types import SimpleNamespace

from app.v3.product.composition import HeadlessProductComposer
from app.v3.product.process_manager import ProductProcessPurpose
from app.v3.root_cause_candidate_contract import (
    RootCauseCandidateRelation,
    RootCauseCandidateSemantics,
    embed_root_cause_candidate_semantics,
)


class BudgetOwnedInvestigation:
    """Deterministic P17-shaped harness; P17 owns the eight-step budget."""

    def __init__(self, *, claim_turns: tuple[int, ...], obligation_id: str) -> None:
        self.claim_turns = claim_turns
        self.obligation_id = obligation_id
        self.calls = 0
        self.steps: list[str] = []
        self.claims: list[SimpleNamespace] = []

    def snapshot(self, *, session_id, principal):
        del session_id, principal
        return SimpleNamespace(
            completed_reasoning_steps=tuple(self.steps),
            claims=tuple(self.claims),
            terminal_stop_reason=None,
            remaining_reasoning_steps=max(0, 8 - self.calls),
            parent_obligations=(
                SimpleNamespace(
                    obligation_id=self.obligation_id,
                    state="VERIFIED",
                ),
            ),
            action_profile=SimpleNamespace(
                rules=(
                    SimpleNamespace(
                        legal_parent_step_ids=(),
                        allow_parentless=True,
                        intent="FORM_CLAIM",
                    ),
                ),
            ),
        )

    def run_one(
        self,
        *,
        session_id,
        principal,
        manager,
        native_session_token,
        downstream_reentry_intent=None,
        downstream_reentry_obligation_id=None,
    ):
        del (
            session_id,
            principal,
            manager,
            native_session_token,
            downstream_reentry_intent,
            downstream_reentry_obligation_id,
        )
        self.calls += 1
        step_id = "rrs_" + f"{self.calls:024x}"
        self.steps.append(step_id)
        if self.calls in self.claim_turns:
            ordinal = len(self.claims) + 1
            semantics = RootCauseCandidateSemantics(
                explanatory_subject_ref=self.obligation_id,
                relation_kind=RootCauseCandidateRelation.EXPLANATORY_CANDIDATE,
                mechanism_ref=f"mechanism:{ordinal}",
                scope_lineage_id="atl_fixture",
                scope_version_id="scope_v1",
            )
            self.claims.append(
                SimpleNamespace(
                    claim_id="clm_" + f"{ordinal:024x}",
                    obligation_id=self.obligation_id,
                    claim_text=f"governed candidate {ordinal}",
                    proposition=embed_root_cause_candidate_semantics(
                        {"candidate_ordinal": ordinal},
                        semantics,
                    ),
                    evidence_links=(
                        SimpleNamespace(
                            evidence_id="evi_" + f"{ordinal:024x}",
                        ),
                    ),
                )
            )
        return SimpleNamespace(step_id=step_id), None


class ReasoningView:
    def __init__(self, investigation: BudgetOwnedInvestigation) -> None:
        self.investigation = investigation

    def steps(self, session_id):
        del session_id
        return tuple(
            SimpleNamespace(
                step_id=step_id,
                parent_obligation_id=self.investigation.obligation_id,
            )
            for step_id in self.investigation.steps
        )


class ResearchView:
    def resume_state(self, *, session_id, principal):
        del session_id, principal
        return SimpleNamespace(
            lineage_id="atl_fixture",
            accepted_brief=SimpleNamespace(
                scope=SimpleNamespace(
                    scope_version=SimpleNamespace(version_id="scope_v1")
                )
            ),
        )


class ScopedManager:
    call_count = 0

    def __init__(self, obligation_id: str) -> None:
        self.target_parent_obligation = obligation_id

    def propose(self, snapshot):
        self.call_count += 1
        return snapshot


def composer_for(investigation: BudgetOwnedInvestigation):
    composer = object.__new__(HeadlessProductComposer)
    composer._investigation = investigation
    composer._reasoning = ReasoningView(investigation)
    composer._research = ResearchView()
    composer._investigation_manager = ScopedManager(
        investigation.obligation_id
    )
    return composer


def test_relationship_readiness_may_legally_arrive_on_fifth_p17_turn():
    obligation_id = "g_relationship_material"
    investigation = BudgetOwnedInvestigation(
        claim_turns=(5,),
        obligation_id=obligation_id,
    )
    composer = composer_for(investigation)

    snapshot, next_owner, executed, error = composer._run_p17(
        session_id="rs_" + "1" * 24,
        principal=object(),
        native_session_token=None,
        owner_calls=[],
        purpose=ProductProcessPurpose.RELATIONSHIP,
        manager=ScopedManager(obligation_id),
        target_obligation_id=obligation_id,
    )

    assert error is None
    assert next_owner.value == "P18"
    assert executed == 5
    assert investigation.calls == 5
    assert len(snapshot.claims) == 1
    assert snapshot.remaining_reasoning_steps == 3


def test_root_cause_second_candidate_may_legally_arrive_on_fifth_p17_turn():
    obligation_id = "g_root"
    investigation = BudgetOwnedInvestigation(
        claim_turns=(2, 5),
        obligation_id=obligation_id,
    )
    composer = composer_for(investigation)

    snapshot, executed, error = composer._run_p17(
        session_id="rs_" + "2" * 24,
        principal=object(),
        native_session_token=None,
        owner_calls=[],
        purpose=ProductProcessPurpose.ROOT_CAUSE,
        manager=ScopedManager(obligation_id),
        target_obligation_id=obligation_id,
    )

    assert error is None
    assert next_owner.value == "P19"
    assert executed == 5
    assert investigation.calls == 5
    scoped = tuple(
        claim
        for claim in snapshot.claims
        if claim.obligation_id == obligation_id
    )
    assert len(scoped) == 2
    assert snapshot.remaining_reasoning_steps == 3
