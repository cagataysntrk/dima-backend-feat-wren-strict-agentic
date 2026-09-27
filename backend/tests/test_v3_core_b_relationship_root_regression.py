from __future__ import annotations

from types import SimpleNamespace

from app.v3.product.composition import HeadlessProductComposer
from app.v3.product.contracts import ProductInvestigationOutputNeed


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
        )

    def run_one(
        self,
        *,
        session_id,
        principal,
        manager,
        native_session_token,
    ):
        del session_id, principal, manager, native_session_token
        self.calls += 1
        step_id = "rrs_" + f"{self.calls:024x}"
        self.steps.append(step_id)
        if self.calls in self.claim_turns:
            self.claims.append(
                SimpleNamespace(
                    claim_id="clm_" + f"{len(self.claims)+1:024x}",
                    obligation_id=self.obligation_id,
                    claim_text=f"governed candidate {len(self.claims)+1}",
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

    snapshot, executed, error = composer._run_p17(
        session_id="rs_" + "1" * 24,
        principal=object(),
        native_session_token=None,
        owner_calls=[],
        output_need=ProductInvestigationOutputNeed.RELATIONSHIP_INTERPRETATION_INPUT,
        manager=ScopedManager(obligation_id),
        target_obligation_id=obligation_id,
    )

    assert error is None
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
        output_need=ProductInvestigationOutputNeed.COMPETING_EXPLANATION_INPUTS,
        manager=ScopedManager(obligation_id),
        target_obligation_id=obligation_id,
    )

    assert error is None
    assert executed == 5
    assert investigation.calls == 5
    scoped = tuple(
        claim
        for claim in snapshot.claims
        if claim.obligation_id == obligation_id
    )
    assert len(scoped) == 2
    assert snapshot.remaining_reasoning_steps == 3
