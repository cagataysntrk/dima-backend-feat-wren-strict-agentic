from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.v3.product.process_manager import (
    ProductProcessObservation,
    ProductProcessPurpose,
)
from lab.metabase.core_b.closure_v2 import evaluate_owner_legality
from lab.metabase.core_b.live_sentinel_v2 import (
    _reasoning_steps_for_sessions,
    _terminal_execution_lineage_valid,
)


def state(*, claims=(), steps=(), terminal=None, remaining=8, progress=True):
    return ProductProcessObservation(
        claim_ids=tuple(claims),
        completed_step_ids=tuple(steps),
        terminal_stop_reason=terminal,
        remaining_reasoning_steps=remaining,
        scoped_move_available=progress,
    )


@pytest.mark.parametrize(
    ("purpose", "observation", "present", "passed", "classification"),
    [
        (
            ProductProcessPurpose.RELATIONSHIP,
            state(claims=("c1",), steps=("s1",)),
            True,
            True,
            "DOWNSTREAM_OWNER_GENUINELY_INVOKED",
        ),
        (
            ProductProcessPurpose.RELATIONSHIP,
            state(claims=("c1",), steps=("s1",)),
            False,
            False,
            "CALLABLE_OWNER_NOT_INVOKED",
        ),
        (
            ProductProcessPurpose.RELATIONSHIP,
            state(terminal="INSUFFICIENT_EVIDENCE"),
            False,
            True,
            "GOVERNED_LIMITATION",
        ),
        (
            ProductProcessPurpose.RELATIONSHIP,
            state(remaining=0),
            False,
            True,
            "GOVERNED_LIMITATION",
        ),
        (
            ProductProcessPurpose.ROOT_CAUSE,
            state(claims=("c1", "c2")),
            True,
            True,
            "DOWNSTREAM_OWNER_GENUINELY_INVOKED",
        ),
        (
            ProductProcessPurpose.ROOT_CAUSE,
            state(claims=("c1", "c2")),
            False,
            False,
            "CALLABLE_OWNER_NOT_INVOKED",
        ),
        (
            ProductProcessPurpose.ROOT_CAUSE,
            state(claims=("c1",), terminal="INSUFFICIENT_EVIDENCE"),
            False,
            True,
            "GOVERNED_LIMITATION",
        ),
        (
            ProductProcessPurpose.ROOT_CAUSE,
            state(claims=("c1",), remaining=0),
            False,
            True,
            "GOVERNED_LIMITATION",
        ),
    ],
)
def test_v2_owner_legality_matrix(
    purpose, observation, present, passed, classification
):
    result=evaluate_owner_legality(
        purpose=purpose,
        observation=observation,
        downstream_owner_present=present,
    )
    assert result.passed is passed
    assert result.classification==classification


def test_v2_rejects_fake_owner_invocation_when_state_never_made_it_callable():
    result=evaluate_owner_legality(
        purpose=ProductProcessPurpose.ROOT_CAUSE,
        observation=state(claims=("c1",), terminal="INSUFFICIENT_EVIDENCE"),
        downstream_owner_present=True,
    )
    assert not result.passed
    assert result.classification=="DOWNSTREAM_OWNER_INVOKED_WHILE_UNCALLABLE"


@pytest.mark.parametrize(
    ("kwargs", "classification"),
    [
        ({"security_valid": False}, "SECURITY_VIOLATION"),
        ({"silent_wrong": True}, "SILENT_WRONG"),
        ({"causal_overclaim": True}, "UNSUPPORTED_CAUSAL_PROMOTION"),
        ({"fabricated_claim": True}, "FABRICATED_CLAIM"),
    ],
)
def test_v2_keeps_p0_failures_red(kwargs, classification):
    result=evaluate_owner_legality(
        purpose=ProductProcessPurpose.ROOT_CAUSE,
        observation=state(claims=("c1","c2")),
        downstream_owner_present=True,
        **kwargs,
    )
    assert not result.passed
    assert result.classification==classification



def _execution_link(
    *,
    status,
    receipt_id=None,
    evidence_id=None,
    limitation_code=None,
    limitation_detail=None,
):
    return SimpleNamespace(
        status=status,
        receipt_id=receipt_id,
        evidence_id=evidence_id,
        limitation_code=limitation_code,
        limitation_detail=limitation_detail,
    )


def test_v2_lineage_accepts_verified_evidence_plus_governed_limited_occurrence():
    links = (
        _execution_link(
            status="VERIFIED",
            receipt_id="rcpt_1",
            evidence_id="evi_1",
        ),
        _execution_link(
            status="LIMITED",
            limitation_code="P14_NATIVE_LIMITED",
            limitation_detail="Governed native limitation.",
        ),
    )
    assert _terminal_execution_lineage_valid(
        links=links,
        evidence_refs=("evi_1",),
    )


@pytest.mark.parametrize(
    "links",
    [
        (_execution_link(status="DELEGATED"),),
        (_execution_link(status="CANDIDATE_CAPTURED"),),
        (_execution_link(status="EXECUTION_STARTED"),),
        (_execution_link(status="EXECUTED"),),
        (_execution_link(status="VERIFIED", evidence_id="evi_1"),),
        (_execution_link(status="LIMITED", limitation_code="LIMITED"),),
    ],
)
def test_v2_lineage_rejects_nonterminal_or_incomplete_execution_lineage(links):
    assert not _terminal_execution_lineage_valid(
        links=links,
        evidence_refs=(),
    )


def test_v2_lineage_requires_every_exposed_evidence_to_have_verified_occurrence():
    links = (
        _execution_link(
            status="VERIFIED",
            receipt_id="rcpt_1",
            evidence_id="evi_1",
        ),
    )
    assert not _terminal_execution_lineage_valid(
        links=links,
        evidence_refs=("evi_1", "evi_foreign"),
    )


def test_v2_relationship_reasoning_projection_includes_child_session_steps():
    by_session = {
        "rs_parent": (SimpleNamespace(step_id="rrs_parent"),),
        "rs_child": (SimpleNamespace(step_id="rrs_child"),),
    }

    class Reasoning:
        def steps(self, session_id):
            return by_session[session_id]

    projected = _reasoning_steps_for_sessions(
        Reasoning(),
        ("rs_parent", "rs_child"),
    )
    assert tuple(step.step_id for step in projected) == (
        "rrs_parent",
        "rrs_child",
    )
