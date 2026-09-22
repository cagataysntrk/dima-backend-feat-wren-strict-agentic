"""FT-003 final real-model -> real-Metabase end-to-end certification.

This is intentionally small and sequential. It certifies the primary one-table Ask
family plus authority-level fail-closed outcomes. It does not expand product scope.
"""

from __future__ import annotations

import json
import os
from datetime import date
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import httpx

from app.config import Settings
from app.fast.ask_cognition import StructuredJsonFastCognition
from app.fast.ask_models import AskOutcomeStatus, FastAskRequest
from app.fast.ask_service import FastAskService
from app.fast.auth_context import FastMetabaseAuthContext, FastMetabaseAuthMode
from app.fast.metabase_gateway import FastMetabaseGateway
from app.fast.metabase_models import (
    FastMetabaseRuntimePolicy,
    SearchResponse,
)
from app.llm import build_generator


MODEL = os.getenv("DIMA_OPENROUTER_MODEL", "google/gemini-2.5-flash-lite")
OUT = Path(
    os.getenv(
        "DIMA_FAST_ASK_MODEL_E2E_RECEIPT",
        "lab/metabase/artifacts/ft003-model-e2e.json",
    )
)

QUESTION_COUNT = "Son 30 günde kaç sipariş var?"
QUESTION_SUM = "Son 30 gündeki sipariş tutarı ne kadar?"
QUESTION_BREAKDOWN = "Son 30 günde bölgelere göre sipariş tutarı"
QUESTION_AMBIGUOUS = "Siparişleri say."
QUESTION_UNSUPPORTED = "Siparişlerin ortalama tutarı nedir?"


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


def _number(value) -> Decimal:
    return Decimal(str(value))


def _answer_number(answer: str) -> Decimal:
    prefix = "Sonuç: "
    if not answer.startswith(prefix) or not answer.endswith("."):
        raise AssertionError(f"unexpected numeric answer format: {answer!r}")
    return Decimal(answer[len(prefix):-1])


def _principal():
    return SimpleNamespace(
        user_id="ft003-model-e2e",
        tenant_id=None,
        is_superadmin=True,
        roles=["superadmin"],
        tenant_slug=None,
    )


def _assert_common_success(response) -> dict:
    assert response.status == AskOutcomeStatus.SUCCESS, response
    assert response.evidence is not None
    assert response.result is not None
    assert response.answer is not None

    evidence = response.evidence
    assert evidence.exact_time_bounds == {
        "start": "2026-08-09",
        "end_exclusive": "2026-09-08",
        "kind": "LAST_N_DAYS",
    }
    assert evidence.resource_ref.startswith("metabase://table/")
    assert len(evidence.query_fingerprint) == 64
    assert len(evidence.access_fingerprint) == 64
    assert len(evidence.result_digest) == 64
    query_text = json.dumps(evidence.portable_query, sort_keys=True).lower()
    assert "native" not in query_text
    assert "join" not in query_text

    return {
        "answer": response.answer,
        "result": response.result.model_dump(mode="json"),
        "evidence": {
            "evidence_id": evidence.evidence_id,
            "resource_ref": evidence.resource_ref,
            "field_refs": evidence.field_refs,
            "exact_time_bounds": evidence.exact_time_bounds,
            "query_fingerprint": evidence.query_fingerprint,
            "access_fingerprint": evidence.access_fingerprint,
            "result_digest": evidence.result_digest,
            "metabase_runtime_version": evidence.metabase_runtime_version,
            "portable_query": evidence.portable_query,
        },
    }


class _AmbiguousGateway:
    """Two permitted resources; no metadata read/query is allowed after ambiguity."""

    def __init__(self) -> None:
        self.read_calls = 0
        self.construct_calls = 0
        self.execute_calls = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return None

    def search(self, *, term_queries=(), semantic_queries=()):
        return SearchResponse(
            data=(
                {
                    "type": "table",
                    "id": 101,
                    "uri": "metabase://table/101",
                    "name": "dataset_alpha",
                    "display_name": "Order Facts",
                    "description": "Permitted order facts",
                },
                {
                    "type": "table",
                    "id": 102,
                    "uri": "metabase://table/102",
                    "name": "dataset_beta",
                    "display_name": "Order Facts",
                    "description": "Permitted order facts",
                },
            ),
            total_count=2,
        )

    def read_resource(self, uris):
        self.read_calls += 1
        raise AssertionError("ambiguous resource set must block before metadata read")

    def construct_query(self, query):
        self.construct_calls += 1
        raise AssertionError("ambiguous resource set must block before construct")

    def execute_serialized(self, query):
        self.execute_calls += 1
        raise AssertionError("ambiguous resource set must block before execution")


def main() -> int:
    receipt: dict = {
        "status": "RED",
        "model": MODEL,
        "workers": 1,
        "anchor": "2026-09-07",
        "window": ["2026-08-09", "2026-09-08"],
        "primary_e2e": [],
        "authority_cases": {},
        "failures": [],
    }

    try:
        expected_count = int(os.environ["FT003_EXPECTED_COUNT"])
        expected_sum = Decimal(os.environ["FT003_EXPECTED_SUM"])
        expected_breakdown = {
            key: Decimal(str(value))
            for key, value in json.loads(os.environ["FT003_EXPECTED_BREAKDOWN"]).items()
        }

        cognition = StructuredJsonFastCognition(build_generator(_settings()))
        base_url = f"http://localhost:{os.environ.get('METABASE_PORT', '3300')}"
        metabase_session = _metabase_login(base_url)

        def real_gateway_factory(principal):
            return FastMetabaseGateway(
                base_url=base_url,
                auth=FastMetabaseAuthContext(
                    tenant_id=principal.tenant_id or "__superadmin__",
                    dima_user_id=principal.user_id,
                    principal_id="metabase-lab-admin",
                    mode=FastMetabaseAuthMode.SESSION,
                    secret=metabase_session,
                    role_scope_digest="ft003-model-e2e",
                ),
                policy=FastMetabaseRuntimePolicy(
                    max_page_rows=200,
                    max_total_rows_per_run=1000,
                ),
            )

        service = FastAskService(
            cognition=cognition,
            gateway_factory=real_gateway_factory,
        )
        principal = _principal()

        cases = (
            ("count", QUESTION_COUNT),
            ("sum", QUESTION_SUM),
            ("breakdown", QUESTION_BREAKDOWN),
        )

        observed_responses = {}
        for name, question in cases:
            case_receipt = {"name": name, "question": question, "passed": False}
            try:
                response = service.ask(
                    FastAskRequest(
                        question=question,
                        as_of_date=date(2026, 9, 7),
                    ),
                    principal=principal,
                )
                common = _assert_common_success(response)
                observed_responses[name] = response

                if name == "count":
                    observed_value = _number(response.result.rows[0]["count"])
                    assert observed_value == expected_count
                    assert response.answer == f"Sonuç: {expected_count} kayıt."
                    oracle = {"count": expected_count}
                elif name == "sum":
                    observed_value = _number(response.result.rows[0]["sum"])
                    assert observed_value == expected_sum
                    assert _answer_number(response.answer) == expected_sum
                    oracle = {"sum": str(expected_sum)}
                else:
                    observed = {
                        str(row["region"]): _number(row["sum"])
                        for row in response.result.rows
                    }
                    assert observed == expected_breakdown
                    assert response.answer == f"{len(expected_breakdown)} kırılım döndü."
                    oracle = {
                        "breakdown": {
                            key: str(value)
                            for key, value in expected_breakdown.items()
                        }
                    }

                case_receipt.update(
                    {
                        "passed": True,
                        "oracle": oracle,
                        **common,
                    }
                )
            except Exception as exc:
                case_receipt["error"] = f"{type(exc).__name__}: {exc}"
            receipt["primary_e2e"].append(case_receipt)

        # Hard authority gate: ambiguity must block at service level regardless
        # of whether the model tries to choose one candidate.
        ambiguous_gateway = _AmbiguousGateway()
        ambiguous_service = FastAskService(
            cognition=cognition,
            gateway_factory=lambda principal: ambiguous_gateway,
        )
        ambiguous_response = ambiguous_service.ask(
            FastAskRequest(
                question=QUESTION_AMBIGUOUS,
                as_of_date=date(2026, 9, 7),
            ),
            principal=principal,
        )
        ambiguity_passed = (
            ambiguous_response.status == AskOutcomeStatus.CLARIFICATION_REQUIRED
            and ambiguous_response.error is not None
            and ambiguous_response.error.code == "AMBIGUOUS_RESOURCE"
            and ambiguous_gateway.read_calls == 0
            and ambiguous_gateway.construct_calls == 0
            and ambiguous_gateway.execute_calls == 0
        )
        receipt["authority_cases"]["ambiguous_resource"] = {
            "passed": ambiguity_passed,
            "final_status": ambiguous_response.status.value,
            "error_code": (
                ambiguous_response.error.code
                if ambiguous_response.error is not None
                else None
            ),
            "metadata_read_calls": ambiguous_gateway.read_calls,
            "construct_calls": ambiguous_gateway.construct_calls,
            "execute_calls": ambiguous_gateway.execute_calls,
        }

        # Hard authority gate: typed unsupported must stop before any Gateway exists.
        unsupported_factory_calls = {"count": 0}

        def unsupported_gateway_factory(principal):
            unsupported_factory_calls["count"] += 1
            raise AssertionError("unsupported intent must stop before Gateway creation")

        unsupported_service = FastAskService(
            cognition=cognition,
            gateway_factory=unsupported_gateway_factory,
        )
        unsupported_response = unsupported_service.ask(
            FastAskRequest(
                question=QUESTION_UNSUPPORTED,
                as_of_date=date(2026, 9, 7),
            ),
            principal=principal,
        )
        unsupported_passed = (
            unsupported_response.status == AskOutcomeStatus.UNSUPPORTED
            and unsupported_factory_calls["count"] == 0
        )
        receipt["authority_cases"]["unsupported"] = {
            "passed": unsupported_passed,
            "final_status": unsupported_response.status.value,
            "gateway_factory_calls": unsupported_factory_calls["count"],
            "error_code": (
                unsupported_response.error.code
                if unsupported_response.error is not None
                else None
            ),
        }

        primary_ok = all(item.get("passed") for item in receipt["primary_e2e"])
        authority_ok = all(
            item.get("passed")
            for item in receipt["authority_cases"].values()
        )

        if not primary_ok:
            receipt["failures"].append("primary_real_model_e2e_failure")
        if not ambiguity_passed:
            receipt["failures"].append("ambiguity_authority_failure")
        if not unsupported_passed:
            receipt["failures"].append("unsupported_authority_failure")

        receipt["expected"] = {
            "count": expected_count,
            "sum": str(expected_sum),
            "breakdown": {
                key: str(value)
                for key, value in expected_breakdown.items()
            },
        }
        receipt["status"] = "GREEN" if primary_ok and authority_ok else "RED"

    except Exception as exc:
        receipt["failures"].append(
            f"sentinel_setup:{type(exc).__name__}:{exc}"
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n"
    )
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if receipt["status"] == "GREEN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
