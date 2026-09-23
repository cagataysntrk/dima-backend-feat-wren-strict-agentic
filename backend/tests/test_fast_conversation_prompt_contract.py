from __future__ import annotations

import json

from app.fast.conversation_models import FastFollowupStatus
from app.fast.followup_cognition import StructuredJsonFastFollowupCognition


class CapturingGenerator:
    def __init__(self) -> None:
        self.system = ""
        self.user = ""
        self.schema = None

    def structured_json(self, system, user, *, schema, schema_name):
        self.system = system
        self.user = user
        self.schema = schema
        assert schema_name == "dima_fast_followup_resolution"
        return json.dumps(
            {
                "status": "CLARIFICATION_REQUIRED",
                "inherited_slots": [],
                "replaced_slots": [],
                "effective_draft": None,
                "reason": "reference is not uniquely resolvable",
            }
        )


def test_followup_prompt_exposes_existing_typed_shape_and_retrieval_contract():
    generator = CapturingGenerator()
    cognition = StructuredJsonFastFollowupCognition(generator)

    resolution = cognition.resolve(
        question="Peki diğeri?",
        accepted_context=None,
        source_questions=(),
        clarification_question=None,
    )

    assert resolution.status == FastFollowupStatus.CLARIFICATION_REQUIRED
    assert "top-level reason MUST be null" in generator.system
    assert "top-level status=UNSUPPORTED" in generator.system
    assert "For supported COUNT, measure_hint MUST be null" in generator.system
    assert "include at least one likely English entity/table lookup term" in generator.system
    assert "Ambiguous references must fail closed" in generator.system
    assert "clarification_question is supplied" in generator.system


def test_followup_prompt_does_not_grant_durable_authority_to_prior_metadata():
    generator = CapturingGenerator()
    cognition = StructuredJsonFastFollowupCognition(generator)

    cognition.resolve(
        question="Peki geçen ay?",
        accepted_context=None,
        source_questions=("Son 30 günde sipariş tutarı ne kadar?",),
        clarification_question=None,
    )

    assert "never execution authority" in generator.system
    assert "Current permissions and metadata will be revalidated" in generator.system
    assert "SQL" in generator.system
