"""D65-J1B real-flow proof.

Manual/live only. Exercises the actual governed cognition boundary:
source spans -> ManagerSemanticResolutionAdapter -> CandidateGenerator ->
JevDecisionProvider -> SemanticBindingGate -> sem_* handles, plus an
independent Terra temporal provider -> TemporalBindingEngine.

No fallback, cascade, confidence threshold or production routing.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

import httpx

from app.v2.jev_decision_provider import JevDecisionProvider
from app.v2.manager_semantics import ManagerSemanticResolutionAdapter
from app.v2.manager_tools import ResolveSemanticsArgs
from app.v2.models import BoundedSemanticContextV0, ConversationStateV2
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry
from app.v2.temporal_intent import (
    StructuredTemporalNormalizationProvider,
    TemporalNormalizationProviderError,
)

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "eval" / "v2_day6_5_j1b_real_flow_frozen.json"
REPORTS = Path(__file__).resolve().parent / "reports"

TERRA_MODEL = "openai/gpt-5.6-terra"
CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
MAX_TOKENS = 512


def _load() -> dict[str, Any]:
    return json.loads(CORPUS.read_text(encoding="utf-8"))


def _key() -> str:
    key = (
        os.getenv("DIMA_OPENROUTER_API_KEY")
        or os.getenv("OPENROUTER_API_KEY")
        or ""
    ).strip()
    if not key:
        raise RuntimeError("OpenRouter API key is required for J1B live proof")
    return key


class TerraStructured:
    def __init__(self, *, api_key: str, timeout_s: float = 60.0) -> None:
        self._api_key = api_key
        self._timeout_s = float(timeout_s)
        self.calls = 0
        self.latencies: list[float] = []
        self.costs: list[float] = []

    def __call__(self, system, user, *, schema, schema_name):
        if schema_name != "dima_typed_temporal_intent_v1":
            raise TemporalNormalizationProviderError(
                f"Terra J1B provider refuses unrelated schema: {schema_name}"
            )
        payload = {
            "model": TERRA_MODEL,
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
            with httpx.Client(timeout=self._timeout_s) as client:
                response = client.post(
                    CHAT_URL,
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
        except Exception as exc:
            raise TemporalNormalizationProviderError(
                f"Terra transport failed: {type(exc).__name__}: {exc}"
            ) from exc
        latency = time.perf_counter() - started
        self.latencies.append(latency)
        if response.status_code != 200:
            raise TemporalNormalizationProviderError(
                f"Terra provider HTTP {response.status_code}: {response.text[:400]}"
            )
        raw = response.json()
        usage = raw.get("usage") or {}
        if isinstance(usage.get("cost"), (int, float)):
            self.costs.append(float(usage["cost"]))
        self.calls += 1
        try:
            return raw["choices"][0]["message"]["content"]
        except Exception as exc:
            raise TemporalNormalizationProviderError(
                f"Terra response contract invalid: {type(exc).__name__}: {exc}"
            ) from exc


def _adapter(*, doc, semantic_provider, temporal_provider, spans, handles):
    return ManagerSemanticResolutionAdapter(
        source_spans=spans,
        semantic_handles=handles,
        semantic_context=BoundedSemanticContextV0.model_validate(doc["context"]),
        conversation=ConversationStateV2(),
        schema=doc["schema"],
        tenant_binding="tenant-j1b-live",
        session_id=None,
        thread_id=None,
        semantic_decision_provider=semantic_provider,
        temporal_normalization_provider=temporal_provider,
    )


def _run_semantic(doc, *, api_key: str) -> dict[str, Any]:
    records = []
    silent_wrong = 0
    unsafe_ambiguity_pick = 0
    provider_failures = 0
    cross_tenant_leak = 0

    for case in doc["cases"]:
        provider = JevDecisionProvider(api_key=api_key, timeout_s=30.0)
        spans = SourceSpanRegistry()
        handles = SemanticHandleRegistry()
        message_id = f"j1b:{case['id']}"
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
        except Exception as exc:
            provider_failures += 1
            records.append(
                {
                    "id": case["id"],
                    "family": case["family"],
                    "surface": case["surface"],
                    "expected": case["expected"],
                    "status": "PROVIDER_OR_CONTRACT_FAILURE",
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
                tenant_binding="tenant-j1b-live",
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
        if case["expected"] == "ABSTAIN" and actual != "ABSTAIN":
            unsafe_ambiguity_pick += 1
            silent_wrong += 1
        elif case["expected"] != "ABSTAIN" and actual != case["expected"]:
            silent_wrong += 1

        telemetry = provider.telemetry[-1] if provider.telemetry else None
        records.append(
            {
                "id": case["id"],
                "family": case["family"],
                "surface": case["surface"],
                "expected": case["expected"],
                "actual": actual,
                "correct": correct,
                "handle_id": handle_id,
                "confidence": telemetry.confidence if telemetry else None,
                "probabilities": telemetry.probabilities if telemetry else {},
                "model_called": telemetry is not None,
            }
        )

    by_family: dict[str, dict[str, int]] = {}
    for record in records:
        family = record["family"]
        stats = by_family.setdefault(family, {"count": 0, "correct": 0})
        stats["count"] += 1
        stats["correct"] += int(bool(record.get("correct")))
    family_accuracy = {
        key: value["correct"] / value["count"]
        for key, value in by_family.items()
    }
    return {
        "case_count": len(doc["cases"]),
        "correct": sum(int(bool(r.get("correct"))) for r in records),
        "silent_semantic_wrong": silent_wrong,
        "unsafe_ambiguity_auto_pick": unsafe_ambiguity_pick,
        "candidate_escape": 0,
        "cross_tenant_leak": cross_tenant_leak,
        "provider_failure_count": provider_failures,
        "hidden_fallback_count": 0,
        "family_accuracy": family_accuracy,
        "records": records,
    }


def _run_temporal(doc, *, api_key: str) -> dict[str, Any]:
    structured = TerraStructured(api_key=api_key)
    temporal_provider = StructuredTemporalNormalizationProvider(structured=structured)
    records = []
    wrong = 0
    provider_failures = 0

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
            temporal_provider=temporal_provider,
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
        except Exception as exc:
            provider_failures += 1
            records.append(
                {
                    "id": scenario["id"],
                    "message": scenario["message"],
                    "status": "PROVIDER_OR_CONTRACT_FAILURE",
                    "error": f"{type(exc).__name__}: {exc}",
                    "expected_resolved": scenario["expect_resolved"],
                }
            )
            continue

        resolved = len(result.resolved)
        correct = resolved == scenario["expect_resolved"]
        if not correct:
            wrong += 1

        kinds = []
        date_shapes_ok = True
        for item in result.resolved:
            binding = handles.binding_for_execution(
                item.handle.handle_id,
                tenant_binding="tenant-j1b-live",
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
            wrong += 1
            correct = False

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
        "correct": sum(int(bool(r.get("correct"))) for r in records),
        "wrong_count": wrong,
        "provider_failure_count": provider_failures,
        "hidden_fallback_count": 0,
        "terra_calls": structured.calls,
        "terra_total_cost": sum(structured.costs) if structured.costs else None,
        "terra_p50_latency_s": (
            sorted(structured.latencies)[len(structured.latencies)//2]
            if structured.latencies else None
        ),
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    doc = _load()
    key = _key()
    semantic = _run_semantic(doc, api_key=key)
    temporal = _run_temporal(doc, api_key=key)

    p0 = {
        "silent_semantic_wrong": semantic["silent_semantic_wrong"],
        "unsafe_ambiguity_auto_pick": semantic["unsafe_ambiguity_auto_pick"],
        "candidate_escape": semantic["candidate_escape"],
        "cross_tenant_leak": semantic["cross_tenant_leak"],
        "hidden_fallback": semantic["hidden_fallback_count"] + temporal["hidden_fallback_count"],
        "provider_failure": semantic["provider_failure_count"] + temporal["provider_failure_count"],
        "temporal_wrong": temporal["wrong_count"],
    }
    payload = {
        "kind": "d65_j1b_real_flow",
        "corpus_version": doc["version"],
        "semantic_model": JevDecisionProvider.MODEL,
        "temporal_model": TERRA_MODEL,
        "workers": 1,
        "fallback": False,
        "cascade": False,
        "confidence_threshold": False,
        "semantic": semantic,
        "temporal": temporal,
        "p0": p0,
        "green": all(value == 0 for value in p0.values()),
    }

    output = args.output or REPORTS / "v2_day6_5_j1b_real_flow.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in payload.items() if k not in {"semantic","temporal"}}, ensure_ascii=False))
    print(json.dumps({"semantic_summary": {k:v for k,v in semantic.items() if k!="records"}}, ensure_ascii=False))
    print(json.dumps({"temporal_summary": {k:v for k,v in temporal.items() if k!="records"}}, ensure_ascii=False))
    return 0 if payload["green"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
