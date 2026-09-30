"""Non-sensitive Brain V2 run telemetry.

Only counts, timings, costs, refs and manual adjudication metadata are stored.
Provider prompts, hidden reasoning and native raw payload bodies are excluded.
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


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
    cognition_dedup_hits: int = Field(ge=0)
    native_dedup_hits: int = Field(ge=0)
    checkpoint_resume_events: int = Field(ge=0)

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
