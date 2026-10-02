"""Non-sensitive Brain V2 run telemetry.

Only counts, timings, costs, refs and manual adjudication metadata are stored.
Provider prompts, hidden reasoning and native raw payload bodies are excluded.
"""
from __future__ import annotations

from contextlib import contextmanager
from enum import StrEnum
from typing import Any, Iterator

from opentelemetry import trace
from pydantic import BaseModel, ConfigDict, Field, model_validator


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class BoundaryName(StrEnum):
    INTENT_INTERPRET = "dima.intent.interpret"
    SCOPE_PATCH = "dima.scope.patch"
    SCOPE_RESOLVE = "dima.scope.resolve"
    REQUIREMENTS_PLAN = "dima.requirements.plan"
    MATERIAL_GROUP = "dima.material.group"
    MATERIAL_COMPILE = "dima.material.compile"
    NATIVE_EXECUTE = "dima.native.execute"
    NATIVE_OBSERVE = "dima.native.observe"
    EVIDENCE_ADMIT = "dima.evidence.admit"
    REQUIREMENT_DISPATCH = "dima.requirement.dispatch"
    COMPLETION_EVALUATE = "dima.completion.evaluate"
    DISCOVERY_PROJECT_CANDIDATES = "dima.discovery.project_candidates"
    P17_DISCOVER = "dima.p17.discover"
    P17_NEXT_TEST = "dima.p17.next_test"
    P18_ADJUDICATE = "dima.p18.adjudicate"
    P19_ASSESS = "dima.p19.assess"
    P20_REPORT = "dima.p20.report"


class BoundaryTraceEvent(Frozen):
    boundary: BoundaryName
    owner: str = Field(min_length=1)
    thread_id: str | None = None
    scope_version_id: str | None = Field(
        default=None,
        pattern=r"^scope_v[1-9][0-9]*$",
    )
    scope_fingerprint: str | None = Field(
        default=None,
        pattern=r"^[a-f0-9]{64}$",
    )
    material_fingerprint: str | None = Field(
        default=None,
        pattern=r"^[a-f0-9]{64}$",
    )
    requirement_id: str | None = Field(default=None, min_length=1)
    material_group_id: str | None = Field(
        default=None,
        pattern=r"^mg_[a-f0-9]{24}$",
    )
    expected_owner: str | None = Field(default=None, min_length=1)
    observed_owner: str | None = Field(default=None, min_length=1)
    evidence_revision: int | None = Field(default=None, ge=0)
    hypothesis_revision: int | None = Field(default=None, ge=0)
    candidate_count: int | None = Field(default=None, ge=0)
    provider_call_count: int | None = Field(default=None, ge=0)
    native_acquisition_count: int | None = Field(default=None, ge=0)
    dedup_hit: bool | None = None
    terminal_state: str | None = None
    error_code: str | None = None
    error_type: str | None = None
    expected_fingerprint: str | None = Field(
        default=None,
        pattern=r"^[a-f0-9]{64}$",
    )
    observed_fingerprint: str | None = Field(
        default=None,
        pattern=r"^[a-f0-9]{64}$",
    )


class BoundaryTrace(Frozen):
    events: tuple[BoundaryTraceEvent, ...] = ()

    @property
    def first_invalid_event(self) -> BoundaryTraceEvent | None:
        return next(
            (item for item in self.events if item.error_code is not None),
            None,
        )

    @property
    def first_invalid_boundary(self) -> str | None:
        item = self.first_invalid_event
        return item.boundary.value if item is not None else None

    @property
    def last_valid_boundary(self) -> str | None:
        invalid = self.first_invalid_event
        if invalid is None:
            return self.events[-1].boundary.value if self.events else None
        index = self.events.index(invalid)
        return (
            self.events[index - 1].boundary.value
            if index > 0
            else None
        )

    def public_receipt(self) -> dict:
        invalid = self.first_invalid_event
        return {
            "last_valid_boundary": self.last_valid_boundary,
            "first_invalid_boundary": self.first_invalid_boundary,
            "expected_fingerprint": (
                invalid.expected_fingerprint if invalid is not None else None
            ),
            "observed_fingerprint": (
                invalid.observed_fingerprint if invalid is not None else None
            ),
            "scope_fingerprint": (
                invalid.scope_fingerprint if invalid is not None else None
            ),
            "material_fingerprint": (
                invalid.material_fingerprint if invalid is not None else None
            ),
            "requirement_id": (
                invalid.requirement_id if invalid is not None else None
            ),
            "material_group_id": (
                invalid.material_group_id if invalid is not None else None
            ),
            "expected_owner": (
                invalid.expected_owner if invalid is not None else None
            ),
            "observed_owner": (
                invalid.observed_owner if invalid is not None else None
            ),
            "error_type": (
                (invalid.error_type or invalid.error_code)
                if invalid is not None
                else None
            ),
            "events": [
                item.model_dump(mode="json")
                for item in self.events
            ],
        }


class OwnerProviderUsage(Frozen):
    owner: str = Field(min_length=1)
    requests: int = Field(ge=0)
    prompt_tokens: int = Field(ge=0)
    completion_tokens: int = Field(ge=0)
    reasoning_tokens: int = Field(ge=0)
    cost_usd: float = Field(ge=0)


class BrainRunTelemetry(Frozen):
    run_ref: str = Field(min_length=1)
    product_sha: str = Field(pattern=r"^[0-9a-f]{40}$")
    engine_sha: str = Field(pattern=r"^[0-9a-f]{40}$")
    engine_release: str = Field(min_length=1)
    model_profile: str = Field(min_length=1)

    native_acquisitions: int = Field(ge=0)
    provider_usage: tuple[OwnerProviderUsage, ...] = ()
    latency_ms: int = Field(ge=0)
    cognition_dedup_hits: int = Field(default=0, ge=0)
    native_dedup_hits: int = Field(default=0, ge=0)
    checkpoint_resume_events: int = Field(default=0, ge=0)

    manual_quality: int | None = Field(default=None, ge=0, le=4)
    mechanical_green: bool | None = None

    @property
    def total_provider_requests(self) -> int:
        return sum(item.requests for item in self.provider_usage)

    @property
    def prompt_tokens(self) -> int:
        return sum(item.prompt_tokens for item in self.provider_usage)

    @property
    def completion_tokens(self) -> int:
        return sum(item.completion_tokens for item in self.provider_usage)

    @property
    def reasoning_tokens(self) -> int:
        return sum(item.reasoning_tokens for item in self.provider_usage)

    @property
    def provider_cost_usd(self) -> float:
        return sum(item.cost_usd for item in self.provider_usage)

    @property
    def quality_per_provider_call(self) -> float | None:
        if self.manual_quality is None:
            return None
        if self.total_provider_requests == 0:
            return float(self.manual_quality)
        return self.manual_quality / self.total_provider_requests

    @property
    def quality_per_dollar(self) -> float | None:
        if self.manual_quality is None:
            return None
        if self.provider_cost_usd == 0:
            return None
        return self.manual_quality / self.provider_cost_usd

    @model_validator(mode="after")
    def unique_owners(self):
        owners = tuple(item.owner for item in self.provider_usage)
        if len(owners) != len(set(owners)):
            raise ValueError("provider telemetry owner rows must be unique")
        return self

    def public_receipt(self) -> dict:
        return {
            "run_ref": self.run_ref,
            "product_sha": self.product_sha,
            "engine_sha": self.engine_sha,
            "engine_release": self.engine_release,
            "model_profile": self.model_profile,
            "native_acquisitions": self.native_acquisitions,
            "provider_requests_by_owner": {
                item.owner: item.requests for item in self.provider_usage
            },
            "total_provider_requests": self.total_provider_requests,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "reasoning_tokens": self.reasoning_tokens,
            "latency_ms": self.latency_ms,
            "provider_cost_usd": self.provider_cost_usd,
            "cognition_dedup_hits": self.cognition_dedup_hits,
            "native_dedup_hits": self.native_dedup_hits,
            "checkpoint_resume_events": self.checkpoint_resume_events,
            "manual_quality": self.manual_quality,
            "mechanical_green": self.mechanical_green,
            "quality_per_provider_call": self.quality_per_provider_call,
            "quality_per_dollar": self.quality_per_dollar,
        }


_OTEL_SAFE_ATTRIBUTES = frozenset(
    {
        "scope_version_id",
        "scope_fingerprint",
        "material_fingerprint",
        "requirement_id",
        "material_group_id",
        "expected_owner",
        "observed_owner",
        "evidence_revision",
        "hypothesis_revision",
        "candidate_count",
        "native_acquisition_count",
        "provider_call_count",
        "dedup_hit",
        "terminal_state",
        "error.type",
    }
)


class _SafeSpan:
    def __init__(self, span) -> None:
        self._span = span

    def set_attributes(self, **values: Any) -> None:
        for key, value in values.items():
            if key in _OTEL_SAFE_ATTRIBUTES and value is not None:
                self._span.set_attribute(key, value)


class OpenTelemetryBridge:
    """Observation-only OpenTelemetry bridge for governed Dima boundaries."""

    def __init__(self, *, tracer=None) -> None:
        self._tracer = tracer or trace.get_tracer("dima.brain_v2")

    @staticmethod
    def _state_attributes(state) -> dict[str, Any]:
        if state is None:
            return {}
        terminal = getattr(state, "workflow_status", None)
        terminal_value = getattr(terminal, "value", terminal)
        return {
            "scope_version_id": getattr(state, "scope_version_id", None),
            "requirement_id": getattr(state, "active_requirement_id", None),
            "material_group_id": getattr(
                state, "active_material_group_id", None
            ),
            "evidence_revision": getattr(state, "evidence_revision", None),
            "hypothesis_revision": getattr(state, "hypothesis_revision", None),
            "terminal_state": (
                str(terminal_value) if terminal_value is not None else None
            ),
        }

    @staticmethod
    def _error_type(exc: BaseException) -> str:
        code = getattr(exc, "code", None)
        if isinstance(code, str) and code.strip():
            return code.strip()
        return exc.__class__.__name__

    @contextmanager
    def operation(
        self,
        boundary: BoundaryName | str,
        *,
        state=None,
        **attributes: Any,
    ) -> Iterator[_SafeSpan]:
        name = boundary.value if isinstance(boundary, BoundaryName) else str(boundary)
        safe = self._state_attributes(state)
        safe.update(attributes)
        safe = {
            key: value
            for key, value in safe.items()
            if key in _OTEL_SAFE_ATTRIBUTES and value is not None
        }
        with self._tracer.start_as_current_span(name, attributes=safe) as raw_span:
            span = _SafeSpan(raw_span)
            try:
                yield span
            except BaseException as exc:
                span.set_attributes(**{"error.type": self._error_type(exc)})
                raise
