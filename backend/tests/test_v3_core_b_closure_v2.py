from __future__ import annotations

import pytest

from app.v3.product.process_manager import (
    ProductProcessObservation,
    ProductProcessPurpose,
)
from lab.metabase.core_b.closure_v2 import evaluate_owner_legality


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
