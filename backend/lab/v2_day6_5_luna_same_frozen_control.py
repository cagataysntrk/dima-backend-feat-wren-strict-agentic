"""D65 post-J1B Luna same-frozen real-flow control.

Uses the unchanged J1B frozen corpus and the real product provider contracts:
StructuredSemanticCandidateDecisionProvider + StructuredTemporalNormalizationProvider
inside ManagerSemanticResolutionAdapter.

LAB/EVAL ONLY. No production routing, fallback, cascade or confidence threshold.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

import httpx

from app.v2.manager_semantics import ManagerSemanticResolutionAdapter
from app.v2.manager_tools import ResolveSemanticsArgs
from app.v2.models import BoundedSemanticContextV0, ConversationStateV2
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.semantic_linker import (
    SemanticDecisionProviderError,
    SemanticLinkAuthorityError,
    StructuredSemanticCandidateDecisionProvider,
)
from app.v2.source_spans import SourceSpanRegistry
from app.v2.temporal_intent import (
    StructuredTemporalNormalizationProvider,
    TemporalNormalizationProviderError,
)

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "eval" / "v2_day6_5_j1b_real_flow_frozen.json"
REPORTS = Path(__file__).resolve().parent / "reports"

MODEL = "openai/gpt-5.6-luna"
CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
MAX_TOKENS = 512


def _load() -> dict[str, Any]:
    return json.loads(CORPUS.read_text(encoding="utf-8"))


def _api_key() -> str:
    key = (
        os.getenv("DIMA_OPENROUTER_API_KEY")
        or os.getenv("OPENROUTER_API_KEY")
        or ""
    ).strip()
    if not key:
        raise RuntimeError("OpenRouter API key is required")
    return key


class OpenRouterStructured:
    def __init__(self, *, api_key: str, model: str = MODEL, timeout_s: float = 60.0) -> None:
        self.api_key = api_key
        self.model = model
        self.timeout_s = float(timeout_s)
        self.calls = 0
        self.costs: list[float] = []
        self.latencies: list[float] = []
        self.response_ids: list[str] = []

    def __call__(self, system, user, *, schema, schema_name):
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": schema_name,
                    "strict": True,
                    "schema": schema,
                },
            },
            "provider": {"allow_fallbacks": False},
            "reasoning": {"enabled": False},
            "max_tokens": MAX_TOKENS,
        }
        started = time.perf_counter()
        try:
            with httpx.Client(timeout=self.timeout_s) as client:
                response = client.post(
                    CHAT_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
        except Exception as exc:
            raise RuntimeError(f"transport failed: {type(exc).__name__}: {exc}") from exc

        latency = time.perf_counter() - started
        self.latencies.append(latency)
        if response.status_code != 200:
            raise RuntimeError(
                f"provider HTTP {response.status_code}: {response.text[:500]}"
            )

        raw = response.json()
        usage = raw.get("usage") or {}
        if isinstance(usage.get("cost"), (int, float)):
            self.costs.append(float(usage["cost"]))
        if raw.get("id"):
            self.response_ids.append(str(raw["id"]))
        self.calls += 1
        return raw["choices"][0]["message"]["content"]


def _adapter(*, doc, semantic_provider, temporal_provider, spans, handles):
    return ManagerSemanticResolutionAdapter(
        source_spans=spans,
        semantic_handles=handles,
        semantic_context=BoundedSemanticContextV0.model_validate(doc["context"]),
        conversation=ConversationStateV2(),
        schema=doc["schema"],
        tenant_binding="tenant-luna-control",
        session_id=None,
        thread_id=None,
        semantic_decision_provider=semantic_provider,
        temporal_normalization_provider=temporal_provider,
    )


def _is_invalid_typed(exc: Exception) -> bool:
    text = f"{type(exc).__name__}: {exc}"
    return (
        "ValidationError" in text
        or "JSONDecodeError" in text
        or "response contract" in text.lower()
        or "response IDs do not match" in text
    )


def run_semantic(doc: dict[str, Any], *, api_key: str) -> dict[str, Any]:
    structured = OpenRouterStructured(api_key=api_key)
    provider = StructuredSemanticCandidateDecisionProvider(structured=structured)

    records: list[dict[str, Any]] = []
    silent_wrong = 0
    unsafe_ambiguity = 0
    candidate_escape = 0
    cross_tenant_leak = 0
    provider_failure = 0
    invalid_typed = 0

    for case in doc["cases"]:
        spans = SourceSpanRegistry()
        handles = SemanticHandleRegistry()
        message_id = f"luna-sem:{case['id']}"
        spans.register_message(message_id=message_id, text=case["surface"])
        span = spans.mint_exact(message_id=message_id, surface=case["surface"])
        adapter = _adapter(
            doc=doc,
            semantic_provider=provider,
            temporal_provider=None,
            spans=spans,
            handles=handles,
        )

        try:
            result = adapter.resolve(
                ResolveSemanticsArgs(
                    provenance="USER_SOURCE",
                    source_refs=(span.source_ref,),
                    target_kind_hints=(case["kind_hint"],),
                )
            )
        except SemanticLinkAuthorityError as exc:
            candidate_escape += 1
            records.append(
                {
                    "id": case["id"],
                    "family": case["family"],
                    "surface": case["surface"],
                    "expected": case["expected"],
                    "status": "CANDIDATE_ESCAPE",
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
            continue
        except SemanticDecisionProviderError as exc:
            if _is_invalid_typed(exc):
                invalid_typed += 1
                status = "INVALID_TYPED_CONTRACT"
            else:
                provider_failure += 1
                status = "PROVIDER_FAILURE"
            records.append(
                {
                    "id": case["id"],
                    "family": case["family"],
                    "surface": case["surface"],
                    "expected": case["expected"],
                    "status": status,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
            continue
        except Exception as exc:
            provider_failure += 1
            records.append(
                {
                    "id": case["id"],
                    "family": case["family"],
                    "surface": case["surface"],
                    "expected": case["expected"],
                    "status": "UNEXPECTED_FAILURE",
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
            continue

        actual = "ABSTAIN"
        handle_id = None
        if result.resolved:
            handle = result.resolved[0].handle
            handle_id = handle.handle_id
            binding = handles.binding_for_execution(
                handle.handle_id,
                tenant_binding="tenant-luna-control",
                context_version=doc["context"]["context_version"]["version"],
            )
            actual = getattr(binding.canonical_target, "canonical_name", None) or "UNKNOWN"
            try:
                handles.validate(
                    handle.handle_id,
                    tenant_binding="tenant-foreign",
                    context_version=doc["context"]["context_version"]["version"],
                )
                cross_tenant_leak += 1
            except ValueError:
                pass

        correct = actual == case["expected"]
        if not correct:
            silent_wrong += 1
            if case["expected"] == "ABSTAIN" and actual != "ABSTAIN":
                unsafe_ambiguity += 1

        records.append(
            {
                "id": case["id"],
                "family": case["family"],
                "surface": case["surface"],
                "expected": case["expected"],
                "actual": actual,
                "correct": correct,
                "handle_id": handle_id,
                "unresolved_count": len(result.unresolved_source_refs),
            }
        )

    family: dict[str, dict[str, int]] = {}
    for row in records:
        bucket = family.setdefault(row["family"], {"count": 0, "correct": 0})
        bucket["count"] += 1
        bucket["correct"] += int(bool(row.get("correct")))

    return {
        "case_count": len(doc["cases"]),
        "correct": sum(int(bool(row.get("correct"))) for row in records),
        "silent_semantic_wrong": silent_wrong,
        "unsafe_ambiguity_auto_pick": unsafe_ambiguity,
        "candidate_escape": candidate_escape,
        "cross_tenant_leak": cross_tenant_leak,
        "provider_failure_count": provider_failure,
        "invalid_typed_contract": invalid_typed,
        "hidden_fallback_count": 0,
        "calls": structured.calls,
        "cost": sum(structured.costs) if structured.costs else None,
        "p50_latency_s": (
            sorted(structured.latencies)[len(structured.latencies) // 2]
            if structured.latencies
            else None
        ),
        "family_accuracy": {
            key: value["correct"] / value["count"] for key, value in family.items()
        },
        "records": records,
    }


def run_temporal(doc: dict[str, Any], *, api_key: str) -> dict[str, Any]:
    structured = OpenRouterStructured(api_key=api_key)
    provider = StructuredTemporalNormalizationProvider(structured=structured)

    records: list[dict[str, Any]] = []
    wrong = 0
    provider_failure = 0
    invalid_typed = 0

    for scenario in doc["temporal_scenarios"]:
        spans = SourceSpanRegistry()
        handles = SemanticHandleRegistry()
        spans.register_message(message_id=scenario["id"], text=scenario["message"])
        refs = []
        hints = []
        for surface, hint in scenario["spans"]:
            span = spans.mint_exact(message_id=scenario["id"], surface=surface)
            refs.append(span.source_ref)
            hints.append(hint)

        adapter = _adapter(
            doc=doc,
            semantic_provider=None,
            temporal_provider=provider,
            spans=spans,
            handles=handles,
        )

        try:
            result = adapter.resolve(
                ResolveSemanticsArgs(
                    provenance="USER_SOURCE",
                    source_refs=tuple(refs),
                    target_kind_hints=tuple(hints),
                )
            )
        except TemporalNormalizationProviderError as exc:
            if _is_invalid_typed(exc):
                invalid_typed += 1
                status = "INVALID_TYPED_CONTRACT"
            else:
                provider_failure += 1
                status = "PROVIDER_FAILURE"
            records.append(
                {
                    "id": scenario["id"],
                    "message": scenario["message"],
                    "status": status,
                    "error": f"{type(exc).__name__}: {exc}",
                    "expected_resolved": scenario["expect_resolved"],
                }
            )
            continue
        except Exception as exc:
            provider_failure += 1
            records.append(
                {
                    "id": scenario["id"],
                    "message": scenario["message"],
                    "status": "UNEXPECTED_FAILURE",
                    "error": f"{type(exc).__name__}: {exc}",
                    "expected_resolved": scenario["expect_resolved"],
                }
            )
            continue

        resolved = len(result.resolved)
        correct = resolved == scenario["expect_resolved"]
        kinds = []
        date_shapes_ok = True
        for item in result.resolved:
            binding = handles.binding_for_execution(
                item.handle.handle_id,
                tenant_binding="tenant-luna-control",
                context_version=doc["context"]["context_version"]["version"],
            )
            kinds.append(item.handle.target_kind)
            target = binding.canonical_target
            if item.handle.target_kind == "period":
                date_shapes_ok = date_shapes_ok and bool(getattr(target, "start", None))
            elif item.handle.target_kind == "comparison":
                date_shapes_ok = date_shapes_ok and bool(
                    getattr(getattr(target, "base_period", None), "start", None)
                    and getattr(getattr(target, "reference_period", None), "start", None)
                )
        if not date_shapes_ok:
            correct = False

        if not correct:
            wrong += 1

        records.append(
            {
                "id": scenario["id"],
                "message": scenario["message"],
                "expected_resolved": scenario["expect_resolved"],
                "actual_resolved": resolved,
                "resolved_kinds": kinds,
                "correct": correct,
                "unresolved_count": len(result.unresolved_source_refs),
                "date_shapes_ok": date_shapes_ok,
            }
        )

    return {
        "scenario_count": len(doc["temporal_scenarios"]),
        "correct": sum(int(bool(row.get("correct"))) for row in records),
        "real_flow_temporal_wrong": wrong,
        "invalid_typed_contract": invalid_typed,
        "provider_failure_count": provider_failure,
        "hidden_fallback_count": 0,
        "calls": structured.calls,
        "cost": sum(structured.costs) if structured.costs else None,
        "p50_latency_s": (
            sorted(structured.latencies)[len(structured.latencies) // 2]
            if structured.latencies
            else None
        ),
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    doc = _load()
    api_key = _api_key()
    semantic = run_semantic(doc, api_key=api_key)
    temporal = run_temporal(doc, api_key=api_key)

    p0 = {
        "silent_semantic_wrong": semantic["silent_semantic_wrong"],
        "unsafe_ambiguity_auto_pick": semantic["unsafe_ambiguity_auto_pick"],
        "candidate_escape": semantic["candidate_escape"],
        "cross_tenant_leak": semantic["cross_tenant_leak"],
        "semantic_provider_failure": semantic["provider_failure_count"],
        "semantic_invalid_typed_contract": semantic["invalid_typed_contract"],
        "real_flow_temporal_wrong": temporal["real_flow_temporal_wrong"],
        "temporal_invalid_typed_contract": temporal["invalid_typed_contract"],
        "temporal_provider_failure": temporal["provider_failure_count"],
        "hidden_fallback": (
            semantic["hidden_fallback_count"] + temporal["hidden_fallback_count"]
        ),
    }
    payload = {
        "kind": "d65_post_j1b_luna_same_frozen_control",
        "model": MODEL,
        "corpus_version": doc["version"],
        "corpus_path": str(CORPUS.relative_to(ROOT)),
        "workers": 1,
        "fallback": False,
        "cascade": False,
        "confidence_threshold": False,
        "semantic": semantic,
        "temporal": temporal,
        "p0": p0,
        "green": all(value == 0 for value in p0.values()),
    }

    output = args.output or REPORTS / "v2_day6_5_luna_same_frozen_control.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "kind": payload["kind"],
                "model": MODEL,
                "corpus_version": payload["corpus_version"],
                "workers": 1,
                "p0": p0,
                "green": payload["green"],
            },
            ensure_ascii=False,
        )
    )
    print(
        json.dumps(
            {"semantic_summary": {k: v for k, v in semantic.items() if k != "records"}},
            ensure_ascii=False,
        )
    )
    print(
        json.dumps(
            {"temporal_summary": {k: v for k, v in temporal.items() if k != "records"}},
            ensure_ascii=False,
        )
    )
    return 0 if payload["green"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
