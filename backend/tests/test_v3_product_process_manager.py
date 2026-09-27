from __future__ import annotations
import pytest
from app.v3.product.process_manager import (
    P19EligibilityDecision, ProductProcessNext, ProductProcessObservation,
    ProductProcessPurpose, RootCauseCandidate, decide_next_owner, p19_eligibility,
)

def candidate(cid, mechanism, *, relation="explains", evidence=("e1",)):
    return RootCauseCandidate(
        claim_id=cid,
        relation_ref=relation,
        mechanism_ref=mechanism,
        evidence_refs=tuple(evidence),
    )


def obs(*, claims=(), steps=(), terminal=None, remaining=8, progress=True,
        downstream=False, candidates=()):
    return ProductProcessObservation(
        claim_ids=tuple(claims), completed_step_ids=tuple(steps),
        terminal_stop_reason=terminal, remaining_reasoning_steps=remaining,
        scoped_move_available=progress, downstream_ref_present=downstream,
        root_cause_candidates=tuple(candidates),
    )

@pytest.mark.parametrize(("purpose","state","expected"),[
    (ProductProcessPurpose.RELATIONSHIP, obs(), ProductProcessNext.P17),
    (ProductProcessPurpose.RELATIONSHIP, obs(claims=("c1",)), ProductProcessNext.P17),
    (ProductProcessPurpose.RELATIONSHIP, obs(claims=("c1",),steps=("s1",)), ProductProcessNext.P18),
    (ProductProcessPurpose.RELATIONSHIP, obs(terminal="INCONCLUSIVE"), ProductProcessNext.TERMINAL),
    (ProductProcessPurpose.RELATIONSHIP, obs(remaining=0), ProductProcessNext.TERMINAL),
    (ProductProcessPurpose.RELATIONSHIP, obs(downstream=True), ProductProcessNext.COMPLETE),
    (ProductProcessPurpose.ROOT_CAUSE, obs(), ProductProcessNext.P17),
    (ProductProcessPurpose.ROOT_CAUSE, obs(claims=("c1",)), ProductProcessNext.P17),
    (ProductProcessPurpose.ROOT_CAUSE, obs(
        claims=("c1","c2"),
        candidates=(candidate("c1","m1"), candidate("c2","m2")),
    ), ProductProcessNext.P19),
    (ProductProcessPurpose.ROOT_CAUSE, obs(terminal="INSUFFICIENT_EVIDENCE"), ProductProcessNext.TERMINAL),
    (ProductProcessPurpose.ROOT_CAUSE, obs(claims=("c1",),remaining=0), ProductProcessNext.TERMINAL),
    (ProductProcessPurpose.ROOT_CAUSE, obs(downstream=True), ProductProcessNext.COMPLETE),
])
def test_callability_matrix(purpose,state,expected):
    assert decide_next_owner(purpose,state)==expected

def test_adaptive_completes_after_one_governed_completed_step():
    assert decide_next_owner(ProductProcessPurpose.ADAPTIVE_INVESTIGATION,obs(steps=("s1",)))==ProductProcessNext.COMPLETE

def test_no_scoped_legal_move_is_terminal_not_retry():
    assert decide_next_owner(ProductProcessPurpose.ROOT_CAUSE,obs(claims=("c1",),progress=False))==ProductProcessNext.TERMINAL

def test_ready_owner_is_callable_even_if_p17_also_has_terminal_marker():
    assert decide_next_owner(ProductProcessPurpose.RELATIONSHIP,
        obs(claims=("c1",),steps=("s1",),terminal="OBJECTIVE_SATISFIED"))==ProductProcessNext.P18
    assert decide_next_owner(
        ProductProcessPurpose.ROOT_CAUSE,
        obs(
            claims=("c1","c2"),
            terminal="OBJECTIVE_SATISFIED",
            candidates=(candidate("c1","m1"), candidate("c2","m2")),
        ),
    )==ProductProcessNext.P19

def test_restart_same_durable_state_selects_same_owner_and_existing_owner_completes():
    state=obs(claims=("c1",),steps=("s1",))
    assert decide_next_owner(ProductProcessPurpose.RELATIONSHIP,state)==ProductProcessNext.P18
    assert decide_next_owner(ProductProcessPurpose.RELATIONSHIP,state)==ProductProcessNext.P18
    completed=obs(claims=("c1",),steps=("s1",),downstream=True)
    assert decide_next_owner(ProductProcessPurpose.RELATIONSHIP,completed)==ProductProcessNext.COMPLETE



def test_p6_same_wording_is_irrelevant_but_same_typed_mechanism_is_not_distinct():
    state = obs(
        claims=("c1", "c2"),
        candidates=(
            candidate("c1", "same-mechanism"),
            candidate("c2", "same-mechanism"),
        ),
    )
    assert p19_eligibility(state) == P19EligibilityDecision.NEED_MORE_EVIDENCE
    assert decide_next_owner(
        ProductProcessPurpose.ROOT_CAUSE,
        state,
    ) == ProductProcessNext.P17


def test_p6_without_available_discriminating_path_is_inconclusive():
    state = obs(
        claims=("c1", "c2"),
        progress=False,
        candidates=(
            candidate("c1", "same-mechanism"),
            candidate("c2", "same-mechanism"),
        ),
    )
    assert p19_eligibility(state) == P19EligibilityDecision.INCONCLUSIVE
    assert decide_next_owner(
        ProductProcessPurpose.ROOT_CAUSE,
        state,
    ) == ProductProcessNext.TERMINAL
