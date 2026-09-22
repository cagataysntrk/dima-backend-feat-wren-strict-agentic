"""Thread-safe Fast-owned in-memory conversation/turn store for FT-005."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from threading import RLock
from uuid import uuid4

from app.fast.conversation_models import (
    FastAcceptedContext,
    FastConversationDetail,
    FastConversationSnapshot,
    FastTurnSnapshot,
)
from app.fast.run_models import FastRunState, TERMINAL_RUN_STATES
from app.fast.run_store import FastRunOwner


class FastConversationNotFound(LookupError):
    pass


class FastConversationInvariantError(RuntimeError):
    pass


@dataclass
class _ConversationRecord:
    conversation_id: str
    owner: FastRunOwner
    title: str
    created_at: datetime
    updated_at: datetime
    turn_ids: list[str] = field(default_factory=list)
    latest_turn_id: str | None = None
    active_turn_id: str | None = None


@dataclass
class _TurnRecord:
    turn_id: str
    conversation_id: str
    seq: int
    parent_turn_id: str | None
    reply_to_turn_id: str | None
    clarifies_run_id: str | None
    user_question: str
    as_of_date: date | None
    run_id: str
    status: FastRunState
    context_source_turn_ids: tuple[str, ...]
    accepted_context: FastAcceptedContext | None
    created_at: datetime
    updated_at: datetime


class FastConversationStore:
    """Initial FT-005 store. Process restart durability is intentionally not certified."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._conversations: dict[str, _ConversationRecord] = {}
        self._turns: dict[str, _TurnRecord] = {}

    def _conversation_locked(
        self,
        conversation_id: str,
        owner: FastRunOwner,
    ) -> _ConversationRecord:
        record = self._conversations.get(conversation_id)
        if record is None or record.owner != owner:
            raise FastConversationNotFound("conversation not found")
        return record

    def _turn_locked(
        self,
        turn_id: str,
        owner: FastRunOwner,
    ) -> _TurnRecord:
        record = self._turns.get(turn_id)
        if record is None:
            raise FastConversationNotFound("turn not found")
        self._conversation_locked(record.conversation_id, owner)
        return record

    def _conversation_snapshot_locked(
        self,
        record: _ConversationRecord,
    ) -> FastConversationSnapshot:
        return FastConversationSnapshot(
            conversation_id=record.conversation_id,
            title=record.title,
            created_at=record.created_at,
            updated_at=record.updated_at,
            latest_turn_id=record.latest_turn_id,
            active_turn_id=record.active_turn_id,
            turn_count=len(record.turn_ids),
        )

    def _turn_snapshot_locked(self, record: _TurnRecord) -> FastTurnSnapshot:
        return FastTurnSnapshot(
            turn_id=record.turn_id,
            conversation_id=record.conversation_id,
            seq=record.seq,
            parent_turn_id=record.parent_turn_id,
            reply_to_turn_id=record.reply_to_turn_id,
            clarifies_run_id=record.clarifies_run_id,
            user_question=record.user_question,
            run_id=record.run_id,
            status=record.status,
            context_source_turn_ids=record.context_source_turn_ids,
            accepted_context=record.accepted_context,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )

    def create_conversation(
        self,
        *,
        owner: FastRunOwner,
        title: str | None = None,
    ) -> FastConversationSnapshot:
        with self._lock:
            now = datetime.now(timezone.utc)
            conversation_id = "conv_" + uuid4().hex
            record = _ConversationRecord(
                conversation_id=conversation_id,
                owner=owner,
                title=(title or "").strip(),
                created_at=now,
                updated_at=now,
            )
            self._conversations[conversation_id] = record
            return self._conversation_snapshot_locked(record)

    def conversation(
        self,
        conversation_id: str,
        owner: FastRunOwner,
    ) -> FastConversationSnapshot:
        with self._lock:
            return self._conversation_snapshot_locked(
                self._conversation_locked(conversation_id, owner)
            )

    def detail(
        self,
        conversation_id: str,
        owner: FastRunOwner,
    ) -> FastConversationDetail:
        with self._lock:
            record = self._conversation_locked(conversation_id, owner)
            turns = tuple(
                self._turn_snapshot_locked(self._turns[turn_id])
                for turn_id in record.turn_ids
            )
            return FastConversationDetail(
                conversation=self._conversation_snapshot_locked(record),
                turns=turns,
            )

    def turn(
        self,
        turn_id: str,
        owner: FastRunOwner,
    ) -> FastTurnSnapshot:
        with self._lock:
            return self._turn_snapshot_locked(self._turn_locked(turn_id, owner))

    def latest_turn(
        self,
        conversation_id: str,
        owner: FastRunOwner,
    ) -> FastTurnSnapshot | None:
        with self._lock:
            conversation = self._conversation_locked(conversation_id, owner)
            if conversation.latest_turn_id is None:
                return None
            return self._turn_snapshot_locked(
                self._turns[conversation.latest_turn_id]
            )

    def active_turn(
        self,
        conversation_id: str,
        owner: FastRunOwner,
    ) -> FastTurnSnapshot | None:
        with self._lock:
            conversation = self._conversation_locked(conversation_id, owner)
            if conversation.active_turn_id is None:
                return None
            return self._turn_snapshot_locked(
                self._turns[conversation.active_turn_id]
            )

    def latest_accepted_turn(
        self,
        conversation_id: str,
        owner: FastRunOwner,
    ) -> FastTurnSnapshot | None:
        with self._lock:
            conversation = self._conversation_locked(conversation_id, owner)
            for turn_id in reversed(conversation.turn_ids):
                turn = self._turns[turn_id]
                if turn.accepted_context is not None:
                    return self._turn_snapshot_locked(turn)
            return None

    def turn_by_run_id(
        self,
        conversation_id: str,
        run_id: str,
        owner: FastRunOwner,
    ) -> FastTurnSnapshot:
        with self._lock:
            conversation = self._conversation_locked(conversation_id, owner)
            for turn_id in conversation.turn_ids:
                turn = self._turns[turn_id]
                if turn.run_id == run_id:
                    return self._turn_snapshot_locked(turn)
            raise FastConversationNotFound("turn not found")

    def append_turn(
        self,
        *,
        conversation_id: str,
        owner: FastRunOwner,
        user_question: str,
        as_of_date: date | None,
        run_id: str,
        status: FastRunState,
        parent_turn_id: str | None,
        reply_to_turn_id: str | None,
        clarifies_run_id: str | None,
        context_source_turn_ids: tuple[str, ...],
    ) -> FastTurnSnapshot:
        with self._lock:
            conversation = self._conversation_locked(conversation_id, owner)
            for related in (
                parent_turn_id,
                reply_to_turn_id,
                *context_source_turn_ids,
            ):
                if related is None:
                    continue
                turn = self._turn_locked(related, owner)
                if turn.conversation_id != conversation_id:
                    raise FastConversationInvariantError(
                        "turn relation must stay inside one conversation"
                    )

            now = datetime.now(timezone.utc)
            turn_id = "turn_" + uuid4().hex
            seq = len(conversation.turn_ids) + 1
            record = _TurnRecord(
                turn_id=turn_id,
                conversation_id=conversation_id,
                seq=seq,
                parent_turn_id=parent_turn_id,
                reply_to_turn_id=reply_to_turn_id,
                clarifies_run_id=clarifies_run_id,
                user_question=user_question,
                as_of_date=as_of_date,
                run_id=run_id,
                status=status,
                context_source_turn_ids=context_source_turn_ids,
                accepted_context=None,
                created_at=now,
                updated_at=now,
            )
            self._turns[turn_id] = record
            conversation.turn_ids.append(turn_id)
            conversation.latest_turn_id = turn_id
            if status not in TERMINAL_RUN_STATES:
                conversation.active_turn_id = turn_id
            if not conversation.title:
                conversation.title = user_question.strip()[:120]
            conversation.updated_at = now
            return self._turn_snapshot_locked(record)

    def update_turn_from_run(
        self,
        *,
        turn_id: str,
        owner: FastRunOwner,
        status: FastRunState,
        accepted_context: FastAcceptedContext | None,
    ) -> FastTurnSnapshot:
        with self._lock:
            turn = self._turn_locked(turn_id, owner)
            conversation = self._conversation_locked(turn.conversation_id, owner)
            now = datetime.now(timezone.utc)
            turn.status = status
            turn.accepted_context = accepted_context
            turn.updated_at = now
            conversation.updated_at = now
            if (
                status in TERMINAL_RUN_STATES
                and conversation.active_turn_id == turn_id
            ):
                conversation.active_turn_id = None
            elif status not in TERMINAL_RUN_STATES:
                conversation.active_turn_id = turn_id
            return self._turn_snapshot_locked(turn)
