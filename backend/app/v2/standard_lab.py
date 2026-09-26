"""Manual-only pure Standard composition harness for Day 6.5.

This is NOT the /ask-v2 front door. It assembles the selected role topology explicitly
for SI certification:

STANDARD_COGNITION  = REFERENCE_LANGUAGE role (current engineering model: Sol)
SEMANTIC_LINKER     = dedicated SEMANTIC_LINKER role (Luna)
TEMPORAL_NORMALIZER = dedicated TEMPORAL_NORMALIZER role (Sol)

The harness delegates all domain authority to StandardLaneEngine and the deterministic
binding/authority/execution boundaries.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.kaset import belki_sar
from app.llm import build_generator
from app.v2.model_policy import ModelProfile, ModelRole, ModelRolePolicy
from app.v2.semantic_linker import StructuredSemanticCandidateDecisionProvider
from app.v2.standard_authority import AcceptedAuthorityRegistry
from app.v2.standard_lane import StandardLaneEngine, StandardLaneOutcome
from app.v2.temporal_intent import StructuredTemporalNormalizationProvider


@dataclass(frozen=True)
class StandardRoleAssembly:
    cognition_llm: Any
    cognition_profile: ModelProfile
    semantic_llm: Any
    semantic_profile: ModelProfile
    temporal_llm: Any
    temporal_profile: ModelProfile

    @property
    def telemetry(self) -> dict[str, dict[str, object]]:
        return {
            "standard_cognition": {
                "role": self.cognition_profile.role.value,
                "provider": self.cognition_profile.provider,
                "model": self.cognition_profile.model,
                "reasoning": self.cognition_profile.reasoning_enabled,
            },
            "semantic_linker": {
                "role": self.semantic_profile.role.value,
                "provider": self.semantic_profile.provider,
                "model": self.semantic_profile.model,
                "reasoning": self.semantic_profile.reasoning_enabled,
            },
            "temporal_normalizer": {
                "role": self.temporal_profile.role.value,
                "provider": self.temporal_profile.provider,
                "model": self.temporal_profile.model,
                "reasoning": self.temporal_profile.reasoning_enabled,
            },
        }


def build_standard_role_assembly(settings) -> StandardRoleAssembly:
    """Build each Standard cognition contract from an explicit role scope."""
    policy = ModelRolePolicy(settings)

    cognition_settings, cognition_profile = policy.scoped_settings(
        ModelRole.REFERENCE_LANGUAGE
    )
    semantic_settings, semantic_profile = policy.scoped_settings(
        ModelRole.SEMANTIC_LINKER
    )
    temporal_settings, temporal_profile = policy.scoped_settings(
        ModelRole.TEMPORAL_NORMALIZER
    )

    cognition_llm = belki_sar(build_generator(cognition_settings))
    semantic_llm = belki_sar(build_generator(semantic_settings))
    temporal_llm = belki_sar(build_generator(temporal_settings))

    return StandardRoleAssembly(
        cognition_llm=cognition_llm,
        cognition_profile=cognition_profile,
        semantic_llm=semantic_llm,
        semantic_profile=semantic_profile,
        temporal_llm=temporal_llm,
        temporal_profile=temporal_profile,
    )


class StandardLabHarness:
    """Explicit Standard composition owner for manual/live SI proof only."""

    def __init__(
        self,
        *,
        settings,
        authority_registry: AcceptedAuthorityRegistry | None = None,
    ) -> None:
        self._assembly = build_standard_role_assembly(settings)
        self._authorities = authority_registry or AcceptedAuthorityRegistry()

        cognition_structured = getattr(
            self._assembly.cognition_llm,
            "structured_json",
            None,
        )
        semantic_structured = getattr(
            self._assembly.semantic_llm,
            "structured_json",
            None,
        )
        temporal_structured = getattr(
            self._assembly.temporal_llm,
            "structured_json",
            None,
        )
        if not callable(cognition_structured):
            raise RuntimeError(
                "REFERENCE_LANGUAGE structured_json is required for Standard cognition"
            )
        if not callable(semantic_structured):
            raise RuntimeError(
                "SEMANTIC_LINKER structured_json is required for Standard semantic cognition"
            )
        if not callable(temporal_structured):
            raise RuntimeError(
                "TEMPORAL_NORMALIZER structured_json is required for Standard temporal cognition"
            )

        self._engine = StandardLaneEngine(
            intent_structured=cognition_structured,
            coverage_structured=cognition_structured,
            semantic_provider=StructuredSemanticCandidateDecisionProvider(
                structured=semantic_structured
            ),
            temporal_provider=StructuredTemporalNormalizationProvider(
                structured=temporal_structured
            ),
            authority_registry=self._authorities,
        )

    @property
    def telemetry(self) -> dict[str, dict[str, object]]:
        return self._assembly.telemetry

    @property
    def authority_registry(self) -> AcceptedAuthorityRegistry:
        return self._authorities

    def run(self, **kwargs) -> StandardLaneOutcome:
        kwargs.setdefault(
            "cognition_model_role",
            self._assembly.cognition_profile.role.value,
        )
        return self._engine.run(**kwargs)
