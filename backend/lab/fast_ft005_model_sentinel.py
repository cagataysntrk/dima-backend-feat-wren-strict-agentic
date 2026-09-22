"""FT-005 focused real-model follow-up cognition certification.

This sentinel exercises only the typed conversation/follow-up cognition contract.
It does not execute analytics queries and does not expand FT-005 scope.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from app.config import Settings
from app.fast.ask_models import AggregationKind, TemporalKind
from app.fast.conversation_models import (
    FastAcceptedContext,
    FastContextSlot,
    FastFollowupResolution,
    FastFollowupStatus,
)
from app.fast.followup_cognition import StructuredJsonFastFollowupCognition
from app.llm import build_generator
from fast_model_eval import RecordingStructuredGenerator


MODEL = os.getenv("DIMA_OPENROUTER_MODEL", "google/gemini-2.5-flash-lite")
OUT = Path(
    os.getenv(
        "DIMA_FAST_FT005_MODEL_RECEIPT",
        "lab/metabase/artifacts/ft005-model-followup.json",
    )
)

Q1 = "Son 30 günde sipariş tutarı ne kadar?"
Q2 = "Peki geçen ay?"
Q3 = "Bölgelere göre?"
TOPIC = "Son 30 günde kaç müşteri var?"
UNSUPPORTED = "Siparişlerin ortalama tutarı ne kadar?"
AMBIGUOUS = "Peki diğeri?"


def _settings() -> Settings:
    key = os.getenv("DIMA_OPENROUTER_API_KEY", "").strip()
    if not key:
        raise RuntimeError("DIMA_OPENROUTER_API_KEY is unavailable")
    return Settings(
        llm_provider="openrouter",
        openrouter_api_key=key,
        openrouter_api_keys="",
        openrouter_model=MODEL,
        openrouter_select_model=MODEL,
        rule_fallback=False,
        v2_structured_reasoning_enabled=False,
        v2_structured_max_tokens=4096,
    )


def _ctx(
    *,
    source_turns: tuple[str, ...],
    temporal_kind: str,
    start: str,
    end_exclusive: str,
    breakdown: bool = False,
) -> FastAcceptedContext:
    fields = {
        "measure": "amount",
        "temporal": "order_date",
    }
    if breakdown:
        fields["breakdown"] = "region"
    return FastAcceptedContext(
        source_turn_ids=source_turns,
        resource_ref="metabase://table/1",
        accepted_field_refs=fields,
        exact_time_bounds={
            "start": start,
            "end_exclusive": end_exclusive,
            "kind": temporal_kind,
        },
        aggregation=AggregationKind.SUM,
        evidence_ids=("ev_context_source",),
        query_fingerprints=("a" * 64,),
    )


TURN1 = "turn_" + "1" * 32
TURN2 = "turn_" + "2" * 32

CTX_Q1 = _ctx(
    source_turns=(TURN1,),
    temporal_kind=TemporalKind.LAST_N_DAYS.value,
    start="2026-08-09",
    end_exclusive="2026-09-08",
)
CTX_Q2 = _ctx(
    source_turns=(TURN1, TURN2),
    temporal_kind=TemporalKind.PREVIOUS_MONTH.value,
    start="2026-08-01",
    end_exclusive="2026-09-01",
)


def _entity_retrieval_hit(search_terms, expected_entity: str) -> bool:
    target = expected_entity.strip().lower()
    return any(
        term.strip().lower() in target or target in term.strip().lower()
        for term in search_terms
        if term.strip()
    )


def _assert_no_authority_invention(resolution) -> None:
    dumped = resolution.model_dump_json()
    assert "fast_res_" not in dumped
    assert "fast_field_" not in dumped
    assert "metabase://table/" not in dumped
    assert "Sonuç:" not in dumped


def _supported_draft(resolution):
    assert resolution.effective_draft is not None
    draft = resolution.effective_draft
    assert draft.status.value == "SUPPORTED"
    return draft


def main() -> int:
    recorder = RecordingStructuredGenerator(
        build_generator(_settings()),
        model_role="THIRD_MODEL_DIAGNOSTIC",
        exact_model_id=MODEL,
        provider="openrouter",
        validator_model=FastFollowupResolution,
        reasoning_effort="disabled",
    )
    cognition = StructuredJsonFastFollowupCognition(recorder)

    receipt: dict = {
        "status": "RED",
        "model": MODEL,
        "assistant_prose_authority": 0,
        "invented_handle_count": 0,
        "cases": [],
        "failures": [],
        "hard_failures": [],
        "diagnostic_observations": [],
        "structured_calls": [],
        "repeatability_probe": [],
    }

    cases = [
        {
            "name": "q1_self_contained",
            "question": Q1,
            "accepted_context": None,
            "source_questions": (),
            "clarification_question": None,
            "expected_entity": "orders",
        },
        {
            "name": "q2_previous_month",
            "question": Q2,
            "accepted_context": CTX_Q1,
            "source_questions": (Q1,),
            "clarification_question": None,
            "expected_entity": "orders",
        },
        {
            "name": "q3_breakdown",
            "question": Q3,
            "accepted_context": CTX_Q2,
            "source_questions": (Q1, Q2),
            "clarification_question": None,
            "expected_entity": "orders",
        },
        {
            "name": "explicit_reply_older_turn",
            "question": Q3,
            "accepted_context": CTX_Q1,
            "source_questions": (Q1,),
            "clarification_question": None,
            "expected_entity": "orders",
        },
        {
            "name": "self_contained_topic_switch",
            "question": TOPIC,
            "accepted_context": CTX_Q2,
            "source_questions": (Q1, Q2),
            "clarification_question": None,
            "expected_entity": "customers",
        },
        {
            "name": "missing_safe_context",
            "question": Q2,
            "accepted_context": None,
            "source_questions": (),
            "clarification_question": None,
            "expected_entity": None,
        },
        {
            "name": "ambiguous_contextual_followup",
            "question": AMBIGUOUS,
            "accepted_context": CTX_Q2,
            "source_questions": (Q1, Q2),
            "clarification_question": None,
            "expected_entity": None,
        },
        {
            "name": "unsupported_avg",
            "question": UNSUPPORTED,
            "accepted_context": CTX_Q2,
            "source_questions": (Q1, Q2),
            "clarification_question": None,
            "expected_entity": None,
        },
        {
            "name": "clarification_answer",
            "question": "Sipariş tutarı",
            "accepted_context": CTX_Q1,
            "source_questions": (Q1, "Geçen ay ne oldu?"),
            "clarification_question": "Geçen ay ne oldu?",
            "expected_entity": "orders",
        },
    ]

    for case in cases:
        observed = {
            "name": case["name"],
            "question": case["question"],
            "source_user_questions": list(case["source_questions"]),
            "accepted_context_present": case["accepted_context"] is not None,
            "clarification_question": case["clarification_question"],
            "passed": False,
        }
        try:
            recorder.set_case(case["name"])
            resolution = cognition.resolve(
                question=case["question"],
                accepted_context=case["accepted_context"],
                source_questions=case["source_questions"],
                clarification_question=case["clarification_question"],
            )
            _assert_no_authority_invention(resolution)
            observed["resolution"] = resolution.model_dump(mode="json")

            name = case["name"]
            if name == "q1_self_contained":
                assert resolution.status == FastFollowupStatus.SELF_CONTAINED
                assert resolution.inherited_slots == ()
                draft = _supported_draft(resolution)
                assert draft.aggregation == AggregationKind.SUM
                assert draft.measure_hint
                assert draft.temporal.kind == TemporalKind.LAST_N_DAYS
                assert draft.temporal.days == 30

            elif name == "q2_previous_month":
                assert resolution.status == FastFollowupStatus.CONTEXTUAL
                draft = _supported_draft(resolution)
                assert draft.aggregation == AggregationKind.SUM
                assert draft.temporal.kind == TemporalKind.PREVIOUS_MONTH
                observed["diagnostic_slots"] = {
                    "inherited": [slot.value for slot in resolution.inherited_slots],
                    "replaced": [slot.value for slot in resolution.replaced_slots],
                    "expected_inherited_reference": ["ENTITY", "AGGREGATION", "MEASURE"],
                    "expected_replaced_reference": ["TEMPORAL"],
                }

            elif name == "q3_breakdown":
                assert resolution.status == FastFollowupStatus.CONTEXTUAL
                draft = _supported_draft(resolution)
                assert draft.aggregation == AggregationKind.SUM
                assert draft.temporal.kind == TemporalKind.PREVIOUS_MONTH
                assert (draft.breakdown_hint or "").strip()
                observed["diagnostic_slots"] = {
                    "inherited": [slot.value for slot in resolution.inherited_slots],
                    "replaced": [slot.value for slot in resolution.replaced_slots],
                }

            elif name == "explicit_reply_older_turn":
                assert resolution.status == FastFollowupStatus.CONTEXTUAL
                draft = _supported_draft(resolution)
                assert draft.temporal.kind == TemporalKind.LAST_N_DAYS
                assert draft.temporal.days == 30
                assert (draft.breakdown_hint or "").strip()

            elif name == "self_contained_topic_switch":
                assert resolution.status == FastFollowupStatus.SELF_CONTAINED
                assert resolution.inherited_slots == ()
                draft = _supported_draft(resolution)
                assert draft.aggregation == AggregationKind.COUNT
                assert draft.measure_hint is None
                lowered = " ".join(draft.search_terms).lower()
                assert "customer" in lowered or "müşteri" in lowered

            elif name == "missing_safe_context":
                assert resolution.status == FastFollowupStatus.CLARIFICATION_REQUIRED
                assert resolution.effective_draft is None

            elif name == "ambiguous_contextual_followup":
                assert resolution.status == FastFollowupStatus.CLARIFICATION_REQUIRED
                assert resolution.effective_draft is None

            elif name == "unsupported_avg":
                assert resolution.status == FastFollowupStatus.UNSUPPORTED
                assert resolution.effective_draft is None

            elif name == "clarification_answer":
                assert resolution.status == FastFollowupStatus.CONTEXTUAL
                draft = _supported_draft(resolution)
                assert draft.aggregation == AggregationKind.SUM
                assert draft.temporal.kind == TemporalKind.PREVIOUS_MONTH
                observed["diagnostic_slots"] = {
                    "inherited": [slot.value for slot in resolution.inherited_slots],
                    "replaced": [slot.value for slot in resolution.replaced_slots],
                }

            if resolution.effective_draft is not None and case["expected_entity"] is not None:
                terms = list(resolution.effective_draft.search_terms)
                retrieval_hit = _entity_retrieval_hit(
                    terms,
                    case["expected_entity"],
                )
                observed["retrieval_terms"] = terms
                observed["retrieval_entity_hit"] = retrieval_hit
                if not retrieval_hit:
                    raise AssertionError(
                        f"entity-centric retrieval miss for {case['expected_entity']}: {terms}"
                    )

            observed["passed"] = True
        except Exception as exc:
            observed["error"] = f"{type(exc).__name__}: {exc}"
            receipt["failures"].append(case["name"])
            receipt["hard_failures"].append(case["name"])

        receipt["cases"].append(observed)

    # Repeatability classification only: same exact Q3 input/schema/model three times,
    # sequential workers=1. This does not majority-vote or repair product behavior.
    for index in range(1, 4):
        case_id = f"repeat_q3_{index}"
        recorder.set_case(case_id)
        try:
            resolution = cognition.resolve(
                question=Q3,
                accepted_context=CTX_Q2,
                source_questions=(Q1, Q2),
                clarification_question=None,
            )
            receipt["repeatability_probe"].append(
                {
                    "case_id": case_id,
                    "success": True,
                    "status": resolution.status.value,
                    "structured_valid": True,
                }
            )
        except Exception as exc:
            receipt["repeatability_probe"].append(
                {
                    "case_id": case_id,
                    "success": False,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )

    receipt["structured_calls"] = recorder.records
    q2 = next(item for item in receipt["cases"] if item["name"] == "q2_previous_month")
    if q2.get("diagnostic_slots"):
        receipt["diagnostic_observations"].append(
            {
                "case_id": "q2_previous_month",
                "kind": "SLOT_METADATA_ONLY",
                "value": q2["diagnostic_slots"],
            }
        )

    receipt["status"] = "GREEN" if not receipt["hard_failures"] else "RED"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if receipt["status"] == "GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
