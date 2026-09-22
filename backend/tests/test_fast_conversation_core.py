from __future__ import annotations

import hashlib
import threading
import time
from datetime import date
from types import SimpleNamespace

import pytest

from app.fast.ask_models import (
    AggregationKind,
    AskDraft,
    AskOutcomeStatus,
    DraftStatus,
    DraftTemporalIntent,
    FastAskErrorPayload,
    FastAskResponse,
    FastEvidence,
    FastQueryResult,
    TemporalKind,
)
from app.fast.conversation_models import (
    FastContextSlot,
    FastFollowupResolution,
    FastFollowupStatus,
    FastTurnCreateRequest,
)
from app.fast.conversation_service import (
    FastConversationConflict,
    FastConversationService,
)
from app.fast.conversation_store import (
    FastConversationNotFound,
    FastConversationStore,
)
from app.fast.run_manager import FastRunManager
from app.fast.run_models import FastRunState
from app.fast.run_store import FastRunOwner


Q1 = "Son 30 günde sipariş tutarı ne kadar?"
Q2 = "Peki geçen ay?"
Q3 = "Bölgelere göre?"
TOPIC = "Son 30 günde kaç müşteri var?"


def principal(
    user_id: str = "user-a",
    tenant_id: str = "tenant-a",
    *,
    is_superadmin: bool = False,
):
    return SimpleNamespace(
        user_id=user_id,
        tenant_id=tenant_id,
        is_superadmin=is_superadmin,
        roles=["superadmin"] if is_superadmin else ["analyst"],
        tenant_slug=tenant_id,
    )


def draft(
    *,
    aggregation: AggregationKind = AggregationKind.SUM,
    temporal: TemporalKind = TemporalKind.LAST_N_DAYS,
    days: int | None = 30,
    breakdown: str | None = None,
    search_terms: tuple[str, ...] = ("orders",),
):
    return AskDraft(
        status=DraftStatus.SUPPORTED,
        unsupported_reason=None,
        search_terms=search_terms,
        aggregation=aggregation,
        measure_hint="amount" if aggregation == AggregationKind.SUM else None,
        breakdown_hint=breakdown,
        temporal=DraftTemporalIntent(
            kind=temporal,
            days=days if temporal == TemporalKind.LAST_N_DAYS else None,
            start_date=None,
            end_date=None,
        ),
    )


def resolution_for(question: str) -> FastFollowupResolution:
    if question == Q1:
        return FastFollowupResolution(
            status=FastFollowupStatus.SELF_CONTAINED,
            effective_draft=draft(),
        )
    if question == Q2:
        return FastFollowupResolution(
            status=FastFollowupStatus.CONTEXTUAL,
            inherited_slots=(
                FastContextSlot.ENTITY,
                FastContextSlot.AGGREGATION,
                FastContextSlot.MEASURE,
            ),
            replaced_slots=(FastContextSlot.TEMPORAL,),
            effective_draft=draft(
                temporal=TemporalKind.PREVIOUS_MONTH,
                days=None,
            ),
        )
    if question == Q3:
        return FastFollowupResolution(
            status=FastFollowupStatus.CONTEXTUAL,
            inherited_slots=(
                FastContextSlot.ENTITY,
                FastContextSlot.AGGREGATION,
                FastContextSlot.MEASURE,
                FastContextSlot.TEMPORAL,
            ),
            replaced_slots=(FastContextSlot.BREAKDOWN,),
            effective_draft=draft(
                temporal=TemporalKind.PREVIOUS_MONTH,
                days=None,
                breakdown="region",
            ),
        )
    if question == TOPIC:
        return FastFollowupResolution(
            status=FastFollowupStatus.SELF_CONTAINED,
            effective_draft=draft(
                aggregation=AggregationKind.COUNT,
                search_terms=("customers",),
            ),
        )
    raise AssertionError(question)


class ScriptedFollowup:
    def __init__(self, mapping=None):
        self.mapping = mapping or {}
        self.calls = []

    def resolve(
        self,
        *,
        question,
        accepted_context,
        source_questions,
        clarification_question,
    ):
        self.calls.append(
            {
                "question": question,
                "accepted_context": accepted_context,
                "source_questions": source_questions,
                "clarification_question": clarification_question,
            }
        )
        if question in self.mapping:
            value = self.mapping[question]
            return value() if callable(value) else value
        return resolution_for(question)


class ResultOperation:
    def __init__(self, *, resolution, started=None, release=None):
        self.resolution = resolution
        self.started = started
        self.release = release
        self.calls = 0

    def ask(self, request, *, principal):
        self.calls += 1
        if self.started is not None:
            self.started.set()
        if self.release is not None:
            assert self.release.wait(timeout=3)

        draft_value = self.resolution.effective_draft
        assert draft_value is not None
        aggregation = draft_value.aggregation
        breakdown = draft_value.breakdown_hint

        if aggregation == AggregationKind.COUNT:
            result = FastQueryResult(
                columns=("count",),
                rows=({"count": 20},),
                row_count=1,
            )
            answer = "Sonuç: 20 kayıt."
            field_refs = {"temporal": "order_date"}
        elif breakdown:
            result = FastQueryResult(
                columns=("region", "sum"),
                rows=(
                    {"region": "East", "sum": 10},
                    {"region": "West", "sum": 12},
                ),
                row_count=2,
            )
            answer = "2 kırılım döndü."
            field_refs = {
                "measure": "amount",
                "temporal": "order_date",
                "breakdown": "region",
            }
        else:
            result = FastQueryResult(
                columns=("sum",),
                rows=({"sum": 22},),
                row_count=1,
            )
            answer = "Sonuç: 22."
            field_refs = {
                "measure": "amount",
                "temporal": "order_date",
            }

        query = {
            "lib/type": "mbql/query",
            "stages": [
                {
                    "aggregation": [[aggregation.value.lower(), {}]],
                    "breakout": [] if not breakdown else [["field", {}, ["region"]]],
                }
            ],
        }
        digest_source = f"{request.question}|{aggregation.value}|{breakdown}"
        digest = hashlib.sha256(digest_source.encode()).hexdigest()
        evidence = FastEvidence(
            evidence_id="ev_" + digest[:20],
            question=request.question,
            resource_handle="fast_res_001",
            resource_ref="metabase://table/1",
            field_refs=field_refs,
            exact_time_bounds={
                "start": "2026-08-01",
                "end_exclusive": "2026-09-01",
                "kind": draft_value.temporal.kind.value,
            },
            portable_query=query,
            query_fingerprint=digest,
            access_fingerprint="a" * 64,
            metabase_runtime_version="v0.63.18",
            result=result,
            result_digest=hashlib.sha256((digest + "result").encode()).hexdigest(),
        )
        return FastAskResponse(
            status=AskOutcomeStatus.SUCCESS,
            question=request.question,
            answer=answer,
            result=result,
            evidence=evidence,
        )


class RecordingOperationFactory:
    def __init__(self, *, started=None, release=None):
        self.calls = []
        self.operations = []
        self.started = started
        self.release = release

    def build(
        self,
        *,
        resolution,
        accepted_context,
        source_questions,
        clarification_question,
    ):
        self.calls.append(
            {
                "resolution": resolution,
                "accepted_context": accepted_context,
                "source_questions": source_questions,
                "clarification_question": clarification_question,
            }
        )
        operation = ResultOperation(
            resolution=resolution,
            started=self.started,
            release=self.release,
        )
        self.operations.append(operation)
        return operation


class DefaultUnusedService:
    def __init__(self):
        self.calls = 0

    def ask(self, request, *, principal):
        self.calls += 1
        return FastAskResponse(
            status=AskOutcomeStatus.FAILED,
            question=request.question,
            error=FastAskErrorPayload(code="DEFAULT_USED", message="unexpected"),
        )


def make_service(*, followup=None, factory=None):
    default = DefaultUnusedService()
    runs = FastRunManager(service=default, max_workers=1)
    store = FastConversationStore()
    followup = followup or ScriptedFollowup()
    factory = factory or RecordingOperationFactory()
    service = FastConversationService(
        store=store,
        run_manager=runs,
        followup_cognition=followup,
        operation_factory=factory,
    )
    return service, store, runs, followup, factory, default


def wait_turn(service, turn_id, expected, *, p=None, timeout=3):
    p = p or principal()
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        turn = service.turn(turn_id, principal=p)
        if turn.status in expected:
            return turn
        time.sleep(0.01)
    raise AssertionError(service.turn(turn_id, principal=p))


def submit_and_complete(service, conversation_id, question, *, p=None, **kwargs):
    p = p or principal()
    turn = service.submit_turn(
        conversation_id,
        FastTurnCreateRequest(question=question, **kwargs),
        principal=p,
    )
    return wait_turn(service, turn.turn_id, {FastRunState.COMPLETED}, p=p)


def test_first_turn_and_followups_create_distinct_runs_and_evidence():
    service, store, runs, followup, factory, default = make_service()
    try:
        conversation = service.create_conversation(principal=principal())
        first = submit_and_complete(service, conversation.conversation_id, Q1)
        second = submit_and_complete(service, conversation.conversation_id, Q2)
        third = submit_and_complete(service, conversation.conversation_id, Q3)

        assert (first.seq, second.seq, third.seq) == (1, 2, 3)
        assert len({first.run_id, second.run_id, third.run_id}) == 3
        assert first.accepted_context is not None
        assert second.accepted_context is not None
        assert third.accepted_context is not None
        assert len({
            first.accepted_context.evidence_ids[0],
            second.accepted_context.evidence_ids[0],
            third.accepted_context.evidence_ids[0],
        }) == 3

        assert second.context_source_turn_ids == (first.turn_id,)
        assert third.context_source_turn_ids == (second.turn_id,)
        assert followup.calls[1]["accepted_context"].evidence_ids == first.accepted_context.evidence_ids
        assert followup.calls[2]["accepted_context"].evidence_ids == second.accepted_context.evidence_ids

        assert factory.calls[1]["resolution"].effective_draft.temporal.kind == TemporalKind.PREVIOUS_MONTH
        assert factory.calls[2]["resolution"].effective_draft.breakdown_hint == "region"
        assert default.calls == 0

        detail = service.conversation(conversation.conversation_id, principal=principal())
        assert [turn.seq for turn in detail.turns] == [1, 2, 3]
        assert detail.conversation.turn_count == 3
    finally:
        runs.shutdown(interrupt=False)


def test_explicit_reply_to_older_turn_uses_that_turn_not_latest():
    service, _, runs, followup, _, _ = make_service()
    try:
        conversation = service.create_conversation(principal=principal())
        first = submit_and_complete(service, conversation.conversation_id, Q1)
        second = submit_and_complete(service, conversation.conversation_id, Q2)
        assert second.turn_id != first.turn_id

        reply = submit_and_complete(
            service,
            conversation.conversation_id,
            Q3,
            reply_to_turn_id=first.turn_id,
        )
        assert reply.reply_to_turn_id == first.turn_id
        assert reply.context_source_turn_ids == (first.turn_id,)
        assert followup.calls[-1]["source_questions"] == (Q1,)
    finally:
        runs.shutdown(interrupt=False)


def test_self_contained_topic_switch_does_not_pass_prior_context_to_execution_factory():
    service, _, runs, _, factory, _ = make_service()
    try:
        conversation = service.create_conversation(principal=principal())
        first = submit_and_complete(service, conversation.conversation_id, Q1)
        assert first.accepted_context is not None

        switched = submit_and_complete(
            service,
            conversation.conversation_id,
            TOPIC,
        )
        assert switched.context_source_turn_ids == ()
        assert factory.calls[-1]["resolution"].status == FastFollowupStatus.SELF_CONTAINED
        assert factory.calls[-1]["accepted_context"] is None
        assert factory.calls[-1]["source_questions"] == ()
    finally:
        runs.shutdown(interrupt=False)


def test_missing_context_can_create_typed_waiting_clarification_run():
    resolution = FastFollowupResolution(
        status=FastFollowupStatus.CLARIFICATION_REQUIRED,
        reason="prior metric context required",
    )
    followup = ScriptedFollowup({"Peki geçen ay?": resolution})
    service, _, runs, _, _, _ = make_service(followup=followup)
    try:
        conversation = service.create_conversation(principal=principal())
        turn = service.submit_turn(
            conversation.conversation_id,
            FastTurnCreateRequest(question="Peki geçen ay?"),
            principal=principal(),
        )
        waiting = wait_turn(
            service,
            turn.turn_id,
            {FastRunState.WAITING_CLARIFICATION},
        )
        assert waiting.accepted_context is None
        run = runs.get_run(waiting.run_id, principal=principal())
        assert run.response is not None
        assert run.response.status == AskOutcomeStatus.CLARIFICATION_REQUIRED
        assert run.response.error.code == "FOLLOWUP_CONTEXT_REQUIRED"
    finally:
        runs.shutdown(interrupt=False)


def test_foreign_user_and_tenant_are_non_enumerating():
    service, _, runs, _, _, _ = make_service()
    try:
        conversation = service.create_conversation(principal=principal())
        for foreign in (
            principal("user-b", "tenant-a"),
            principal("user-a", "tenant-b"),
        ):
            with pytest.raises(FastConversationNotFound):
                service.conversation(
                    conversation.conversation_id,
                    principal=foreign,
                )

        elevated = principal("user-a", "tenant-a", is_superadmin=True)
        own = service.conversation(
            conversation.conversation_id,
            principal=elevated,
        )
        assert own.conversation.conversation_id == conversation.conversation_id
    finally:
        runs.shutdown(interrupt=False)


def test_active_run_conflict_is_explicit_409_semantic():
    started = threading.Event()
    release = threading.Event()
    factory = RecordingOperationFactory(started=started, release=release)
    service, _, runs, _, _, _ = make_service(factory=factory)
    try:
        conversation = service.create_conversation(principal=principal())
        first = service.submit_turn(
            conversation.conversation_id,
            FastTurnCreateRequest(question=Q1),
            principal=principal(),
        )
        assert started.wait(timeout=2)

        with pytest.raises(FastConversationConflict) as error:
            service.submit_turn(
                conversation.conversation_id,
                FastTurnCreateRequest(question=Q2),
                principal=principal(),
            )
        assert error.value.code == "ACTIVE_RUN_EXISTS"
        release.set()
        wait_turn(service, first.turn_id, {FastRunState.COMPLETED})
    finally:
        release.set()
        runs.shutdown(interrupt=False)


def test_clarification_answer_finalizes_old_waiting_run_and_creates_new_turn_and_run():
    clarification = FastFollowupResolution(
        status=FastFollowupStatus.CLARIFICATION_REQUIRED,
        reason="which metric?",
    )
    answered = FastFollowupResolution(
        status=FastFollowupStatus.SELF_CONTAINED,
        effective_draft=draft(),
    )
    followup = ScriptedFollowup(
        {
            "Geçen ay ne oldu?": clarification,
            "Sipariş tutarı": answered,
        }
    )
    service, _, runs, _, _, _ = make_service(followup=followup)
    try:
        conversation = service.create_conversation(principal=principal())
        waiting_turn = service.submit_turn(
            conversation.conversation_id,
            FastTurnCreateRequest(question="Geçen ay ne oldu?"),
            principal=principal(),
        )
        waiting_turn = wait_turn(
            service,
            waiting_turn.turn_id,
            {FastRunState.WAITING_CLARIFICATION},
        )
        old_run_id = waiting_turn.run_id

        answered_turn = service.submit_turn(
            conversation.conversation_id,
            FastTurnCreateRequest(
                question="Sipariş tutarı",
                clarifies_run_id=old_run_id,
            ),
            principal=principal(),
        )
        answered_turn = wait_turn(
            service,
            answered_turn.turn_id,
            {FastRunState.COMPLETED},
        )
        old_run = runs.get_run(old_run_id, principal=principal())
        assert old_run.state == FastRunState.CANCELLED
        assert answered_turn.run_id != old_run_id
        assert answered_turn.clarifies_run_id == old_run_id
        assert answered_turn.seq == waiting_turn.seq + 1
        assert answered_turn.parent_turn_id == waiting_turn.turn_id
        assert old_run.retry_of_run_id is None
    finally:
        runs.shutdown(interrupt=False)


def test_retry_remains_separate_from_followup_runs():
    service, _, runs, _, _, _ = make_service()
    try:
        conversation = service.create_conversation(principal=principal())
        first = submit_and_complete(service, conversation.conversation_id, Q1)
        second = submit_and_complete(service, conversation.conversation_id, Q2)

        first_run = runs.get_run(first.run_id, principal=principal())
        second_run = runs.get_run(second.run_id, principal=principal())
        assert first_run.retry_of_run_id is None
        assert second_run.retry_of_run_id is None
        assert second_run.root_run_id == second_run.run_id
        assert second_run.attempt == 1
    finally:
        runs.shutdown(interrupt=False)


def test_accepted_context_persists_no_request_local_opaque_handles_or_assistant_prose():
    service, _, runs, _, _, _ = make_service()
    try:
        conversation = service.create_conversation(principal=principal())
        first = submit_and_complete(service, conversation.conversation_id, Q1)
        context = first.accepted_context
        assert context is not None
        dumped = context.model_dump_json()
        assert "fast_res_" not in dumped
        assert "fast_field_" not in dumped
        assert "Sonuç:" not in dumped
        assert context.resource_ref == "metabase://table/1"
        assert context.accepted_field_refs["measure"] == "amount"
    finally:
        runs.shutdown(interrupt=False)



def test_contextual_chain_supplies_accepted_user_question_lineage_not_only_last_fragment():
    service, _, runs, followup, _, _ = make_service()
    try:
        conversation = service.create_conversation(principal=principal())
        first = submit_and_complete(service, conversation.conversation_id, Q1)
        second = submit_and_complete(service, conversation.conversation_id, Q2)
        third = submit_and_complete(service, conversation.conversation_id, Q3)

        assert first.accepted_context is not None
        assert second.accepted_context is not None
        assert third.accepted_context is not None

        third_call = followup.calls[2]
        assert third_call["source_questions"] == (Q1, Q2)
        assert second.accepted_context.source_turn_ids == (
            first.turn_id,
            second.turn_id,
        )
        assert "Sonuç:" not in " ".join(third_call["source_questions"])
    finally:
        runs.shutdown(interrupt=False)
