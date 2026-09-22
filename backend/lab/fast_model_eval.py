"""Eval-only structured-output observability for Fast Track model benchmarks.

Never import this module from production app.fast code.
It records only requested structured-action JSON and transport/validation telemetry.
It does not record chain-of-thought or reasoning text.
"""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any

from pydantic import ValidationError

from app.llm import get_llm_usage, reset_llm_usage


class RecordingStructuredGenerator:
    def __init__(
        self,
        inner,
        *,
        model_role: str,
        exact_model_id: str,
        provider: str,
        validator_model=None,
        reasoning_effort: str = "disabled",
    ) -> None:
        self._inner = inner
        self._model_role = model_role
        self._model_id = exact_model_id
        self._provider = provider
        self._validator_model = validator_model
        self._reasoning_effort = reasoning_effort
        self._case_id = "unassigned"
        self.records: list[dict[str, Any]] = []

    def set_case(self, case_id: str) -> None:
        self._case_id = case_id

    def structured_json(
        self,
        system: str,
        user: str,
        *,
        schema: dict[str, Any],
        schema_name: str,
    ) -> str:
        started = time.monotonic()
        reset_llm_usage()
        record: dict[str, Any] = {
            "case_id": self._case_id,
            "model_role": self._model_role,
            "exact_model_id": self._model_id,
            "provider": self._provider,
            "reasoning_effort": self._reasoning_effort,
            "schema_name": schema_name,
            "transport_success": False,
            "parse_success": False,
            "structured_valid": False,
            "provider_error_type": None,
            "provider_error_message": None,
            "validation_error_type": None,
            "validation_error_paths": [],
            "raw_structured_output": None,
            "raw_output_digest": None,
            "latency_ms": None,
            "input_tokens": None,
            "output_tokens": None,
        }
        try:
            raw = self._inner.structured_json(
                system,
                user,
                schema=schema,
                schema_name=schema_name,
            )
            record["transport_success"] = True
            record["raw_structured_output"] = raw
            record["raw_output_digest"] = hashlib.sha256(
                raw.encode("utf-8")
            ).hexdigest()

            try:
                payload = json.loads(raw)
                record["parse_success"] = True
            except json.JSONDecodeError as exc:
                record["validation_error_type"] = type(exc).__name__
                record["validation_error_paths"] = [
                    f"json:{exc.lineno}:{exc.colno}"
                ]
                return raw

            if self._validator_model is None:
                record["structured_valid"] = True
            else:
                try:
                    self._validator_model.model_validate(payload)
                    record["structured_valid"] = True
                except ValidationError as exc:
                    record["validation_error_type"] = type(exc).__name__
                    record["validation_error_paths"] = [
                        ".".join(str(part) for part in error.get("loc", ()))
                        for error in exc.errors()
                    ]
            return raw
        except Exception as exc:
            record["provider_error_type"] = type(exc).__name__
            record["provider_error_message"] = str(exc)[:500]
            raise
        finally:
            usage = get_llm_usage() or {}
            record["latency_ms"] = int(
                (time.monotonic() - started) * 1000
            )
            record["input_tokens"] = usage.get("input_tokens")
            record["output_tokens"] = usage.get("output_tokens")
            self.records.append(record)
