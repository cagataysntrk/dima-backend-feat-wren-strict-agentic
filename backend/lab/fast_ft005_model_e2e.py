"""FT-005 final real-model + real-Metabase three-turn follow-up certification."""

from __future__ import annotations

import json
import os
import time
from datetime import date
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import httpx

from app.config import Settings
from app.fast.ask_cognition import StructuredJsonFastCognition
from app.fast.ask_service import FastAskService
from app.fast.auth_context import FastMetabaseAuthContext, FastMetabaseAuthMode
from app.fast.conversation_models import FastTurnCreateRequest
from app.fast.conversation_service import (
    FastConversationAskFactory,
    FastConversationService,
)
from app.fast.conversation_store import FastConversationStore
from app.fast.followup_cognition import StructuredJsonFastFollowupCognition
from app.fast.metabase_gateway import FastMetabaseGateway
from app.fast.metabase_models import FastMetabaseRuntimePolicy
from app.fast.run_manager import FastRunManager
from app.fast.run_models import FastRunState
from app.llm import build_generator


MODEL = os.getenv("DIMA_OPENROUTER_MODEL", "google/gemini-2.5-flash-lite")
OUT = Path(
    os.getenv(
        "DIMA_FAST_FT005_E2E_RECEIPT",
        "lab/metabase/artifacts/ft005-followup-e2e.json",
    )
)

Q1 = "Son 30 günde sipariş tutarı ne kadar?"
Q2 = "Peki geçen ay?"
Q3 = "Bölgelere göre?"


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


def _metabase_login(base_url: str) -> str:
    response = httpx.post(
        base_url + "/api/session",
        json={
            "username": os.environ["MB_ADMIN_EMAIL"],
            "password": os.environ["MB_ADMIN_PASSWORD"],
        },
        timeout=30,
    )
    response.raise_for_status()
    token = response.json().get("id")
    if not token:
        raise RuntimeError("Metabase login returned no session")
    return str(token)


class RecordingGateway:
    def __init__(self, inner: FastMetabaseGateway, ledger: list[dict]) -> None:
        self._inner = inner
        self.record = {
            "search_calls": 0,
            "read_resource_calls": 0,
            "construct_calls": 0,
            "execute_calls": 0,
        }
        ledger.append(self.record)

    def __enter__(self):
        self._inner.__enter__()
        return self

    def __exit__(self, exc_type, exc, tb):
        return self._inner.__exit__(exc_type, exc, tb)

    def __getattr__(self, name):
        return getattr(self._inner, name)

    def search(self, **kwargs):
        self.record["search_calls"] += 1
        return self._inner.search(**kwargs)

    def read_resource(self, uris):
        self.record["read_resource_calls"] += 1
        return self._inner.read_resource(uris)

    def construct_query(self, portable_query):
        self.record["construct_calls"] += 1
        return self._inner.construct_query(portable_query)

    def execute_serialized(self, query):
        self.record["execute_calls"] += 1
        return self._inner.execute_serialized(query)


class RecordingFollowup:
    def __init__(self, inner) -> None:
        self._inner = inner
        self.calls: list[dict] = []

    def resolve(
        self,
        *,
        question,
        accepted_context,
        source_questions,
        clarification_question,
    ):
        resolution = self._inner.resolve(
            question=question,
            accepted_context=accepted_context,
            source_questions=source_questions,
            clarification_question=clarification_question,
        )
        self.calls.append(
            {
                "question": question,
                "accepted_context": (
                    accepted_context.model_dump(mode="json")
                    if accepted_context is not None
                    else None
                ),
                "source_user_questions": list(source_questions),
                "clarification_question": clarification_question,
                "resolution": resolution.model_dump(mode="json"),
            }
        )
        return resolution


def _principal():
    return SimpleNamespace(
        user_id="ft005-model-e2e",
        tenant_id=None,
        is_superadmin=True,
        roles=["superadmin"],
        tenant_slug=None,
    )


def _wait_turn(service, turn_id: str, principal, *, timeout: float = 20.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        turn = service.turn(turn_id, principal=principal)
        if turn.status in {
            FastRunState.COMPLETED,
            FastRunState.FAILED,
            FastRunState.WAITING_CLARIFICATION,
            FastRunState.CANCELLED,
            FastRunState.INTERRUPTED,
        }:
            return turn
        time.sleep(0.05)
    raise AssertionError(f"turn did not settle: {turn_id}")


def _number(value) -> Decimal:
    return Decimal(str(value))


def _accepted_dump(turn) -> str:
    assert turn.accepted_context is not None
    return turn.accepted_context.model_dump_json()


def main() -> int:
    receipt: dict = {
        "status": "RED",
        "model": MODEL,
        "anchor": "2026-09-07",
        "turns": [],
        "followup_calls": [],
        "gateway_revalidation": [],
        "failures": [],
    }

    runs: FastRunManager | None = None
    try:
        expected_q1 = Decimal(os.environ["FT005_EXPECTED_Q1_SUM"])
        expected_q2 = Decimal(os.environ["FT005_EXPECTED_Q2_SUM"])
        expected_q3 = {
            key: Decimal(str(value))
            for key, value in json.loads(os.environ["FT005_EXPECTED_Q3_BREAKDOWN"]).items()
        }

        generator = build_generator(_settings())
        selector = StructuredJsonFastCognition(generator)
        followup = RecordingFollowup(
            StructuredJsonFastFollowupCognition(generator)
        )

        base_url = f"http://localhost:{os.environ.get('METABASE_PORT', '3300')}"
        session = _metabase_login(base_url)
        gateway_ledger: list[dict] = []

        def gateway_factory(principal):
            inner = FastMetabaseGateway(
                base_url=base_url,
                auth=FastMetabaseAuthContext(
                    tenant_id=principal.tenant_id or "__superadmin__",
                    dima_user_id=principal.user_id,
                    principal_id="metabase-lab-admin",
                    mode=FastMetabaseAuthMode.SESSION,
                    secret=session,
                    role_scope_digest="ft005-model-followup",
                ),
                policy=FastMetabaseRuntimePolicy(
                    max_page_rows=200,
                    max_total_rows_per_run=1000,
                ),
            )
            return RecordingGateway(inner, gateway_ledger)

        default_ask = FastAskService(
            cognition=selector,
            gateway_factory=gateway_factory,
        )
        runs = FastRunManager(service=default_ask, max_workers=1)
        conversations = FastConversationService(
            store=FastConversationStore(),
            run_manager=runs,
            followup_cognition=followup,
            operation_factory=FastConversationAskFactory(
                selector_cognition=selector,
                gateway_factory=gateway_factory,
            ),
        )
        principal = _principal()
        conversation = conversations.create_conversation(
            principal=principal,
            title="FT-005 real model follow-up",
        )

        settled = []
        for question in (Q1, Q2, Q3):
            created = conversations.submit_turn(
                conversation.conversation_id,
                FastTurnCreateRequest(
                    question=question,
                    as_of_date=date(2026, 9, 7),
                ),
                principal=principal,
            )
            turn = _wait_turn(conversations, created.turn_id, principal)
            assert turn.status == FastRunState.COMPLETED, turn
            assert turn.accepted_context is not None
            settled.append(turn)

        first, second, third = settled

        assert len({first.run_id, second.run_id, third.run_id}) == 3
        evidence_ids = [
            first.accepted_context.evidence_ids[0],
            second.accepted_context.evidence_ids[0],
            third.accepted_context.evidence_ids[0],
        ]
        assert len(set(evidence_ids)) == 3

        assert first.context_source_turn_ids == ()
        assert second.context_source_turn_ids == (first.turn_id,)
        assert third.context_source_turn_ids == (second.turn_id,)

        assert first.accepted_context.source_turn_ids == (first.turn_id,)
        assert second.accepted_context.source_turn_ids == (
            first.turn_id,
            second.turn_id,
        )
        assert third.accepted_context.source_turn_ids == (
            first.turn_id,
            second.turn_id,
            third.turn_id,
        )

        for turn in settled:
            dumped = _accepted_dump(turn)
            assert "fast_res_" not in dumped
            assert "fast_field_" not in dumped
            assert "Sonuç:" not in dumped

        assert len(followup.calls) == 3
        assert followup.calls[0]["source_user_questions"] == []
        assert followup.calls[1]["source_user_questions"] == [Q1]
        assert followup.calls[2]["source_user_questions"] == [Q1, Q2]
        assert "Sonuç:" not in json.dumps(
            followup.calls,
            ensure_ascii=False,
        )

        assert len(gateway_ledger) == 3
        for record in gateway_ledger:
            assert record["search_calls"] >= 1
            assert record["read_resource_calls"] >= 1
            assert record["construct_calls"] == 1
            assert record["execute_calls"] == 1

        run1 = runs.get_run(first.run_id, principal=principal)
        run2 = runs.get_run(second.run_id, principal=principal)
        run3 = runs.get_run(third.run_id, principal=principal)
        assert run1.state == run2.state == run3.state == FastRunState.COMPLETED
        assert run1.retry_of_run_id is None
        assert run2.retry_of_run_id is None
        assert run3.retry_of_run_id is None
        assert run1.root_run_id == run1.run_id
        assert run2.root_run_id == run2.run_id
        assert run3.root_run_id == run3.run_id

        assert run1.response is not None
        assert run2.response is not None
        assert run3.response is not None

        q1_value = _number(run1.response.result.rows[0]["sum"])
        q2_value = _number(run2.response.result.rows[0]["sum"])
        q3_value = {
            str(row["region"]): _number(row["sum"])
            for row in run3.response.result.rows
        }
        assert q1_value == expected_q1
        assert q2_value == expected_q2
        assert q3_value == expected_q3

        assert run1.response.evidence is not None
        assert run2.response.evidence is not None
        assert run3.response.evidence is not None
        assert run1.response.evidence.exact_time_bounds == {
            "start": "2026-08-09",
            "end_exclusive": "2026-09-08",
            "kind": "LAST_N_DAYS",
        }
        assert run2.response.evidence.exact_time_bounds == {
            "start": "2026-08-01",
            "end_exclusive": "2026-09-01",
            "kind": "PREVIOUS_MONTH",
        }
        assert run3.response.evidence.exact_time_bounds == {
            "start": "2026-08-01",
            "end_exclusive": "2026-09-01",
            "kind": "PREVIOUS_MONTH",
        }
        assert "breakdown" in run3.response.evidence.field_refs

        for idx, (turn, run) in enumerate(zip(settled, (run1, run2, run3)), start=1):
            receipt["turns"].append(
                {
                    "seq": idx,
                    "turn_id": turn.turn_id,
                    "run_id": turn.run_id,
                    "question": turn.user_question,
                    "context_source_turn_ids": list(turn.context_source_turn_ids),
                    "accepted_source_turn_ids": list(
                        turn.accepted_context.source_turn_ids
                    ),
                    "evidence_id": turn.accepted_context.evidence_ids[0],
                    "query_fingerprint": turn.accepted_context.query_fingerprints[0],
                    "answer": run.response.answer,
                    "result": run.response.result.model_dump(mode="json"),
                    "exact_time_bounds": run.response.evidence.exact_time_bounds,
                    "field_refs": run.response.evidence.field_refs,
                    "resource_ref": run.response.evidence.resource_ref,
                }
            )

        receipt["followup_calls"] = followup.calls
        receipt["gateway_revalidation"] = gateway_ledger
        receipt["oracle"] = {
            "q1_sum": str(expected_q1),
            "q2_previous_month_sum": str(expected_q2),
            "q3_previous_month_breakdown": {
                key: str(value)
                for key, value in expected_q3.items()
            },
        }
        receipt["assertions"] = {
            "distinct_runs": True,
            "distinct_evidence": True,
            "old_run_reopened": False,
            "request_local_handle_as_durable_authority": False,
            "current_resource_revalidation_each_turn": True,
            "assistant_prose_authority": 0,
            "context_lineage_exact": True,
        }
        receipt["status"] = "GREEN"

    except Exception as exc:
        receipt["failures"].append(
            f"{type(exc).__name__}: {exc}"
        )
    finally:
        if runs is not None:
            runs.shutdown(interrupt=False)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if receipt["status"] == "GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
