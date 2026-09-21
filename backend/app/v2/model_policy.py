"""Small V2 model-role policy boundary.

Model names/providers are configuration. Product/domain code asks for a role. This is
only Day 6 preparation for later escalation; it does not implement a manager, router,
or multi-attempt acceptance loop.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ModelRole(StrEnum):
    FAST_LANGUAGE = "FAST_LANGUAGE"
    REFERENCE_LANGUAGE = "REFERENCE_LANGUAGE"


@dataclass(frozen=True)
class ModelProfile:
    role: ModelRole
    provider: str
    model: str
    native_schema_required: bool = True
    reasoning_enabled: bool = False


class ModelRolePolicy:
    """Resolve configured model roles without leaking model names into domain logic."""

    _MODEL_FIELDS = {
        "openrouter": ("openrouter_model", "openrouter_select_model"),
        "gemini": ("gemini_model", "gemini_select_model"),
        "groq": ("groq_model", "groq_select_model"),
        "xai": ("xai_model", "xai_select_model"),
        "ollama": ("ollama_model", "ollama_select_model"),
        "anthropic": ("llm_model", "anthropic_select_model"),
    }

    def __init__(self, settings):
        self._settings = settings

    def profile(
        self,
        role: ModelRole,
        *,
        model_override: str | None = None,
    ) -> ModelProfile:
        if role == ModelRole.FAST_LANGUAGE:
            provider = str(getattr(self._settings, "v2_fast_language_provider", "") or "openrouter")
            configured = str(getattr(self._settings, "v2_fast_language_model", "") or "")
            model = str(model_override or configured or self._provider_default(provider) or "")
        elif role == ModelRole.REFERENCE_LANGUAGE:
            provider = str(getattr(self._settings, "v2_reference_language_provider", "") or "openrouter")
            configured = str(getattr(self._settings, "v2_reference_language_model", "") or "")
            model = str(model_override or configured or "")
        else:
            raise ValueError(f"unsupported V2 model role: {role}")

        if provider not in self._MODEL_FIELDS:
            raise ValueError(f"unsupported V2 model provider: {provider}")
        if not model:
            raise ValueError(f"model is not configured for role {role.value}")

        return ModelProfile(
            role=role,
            provider=provider,
            model=model,
            native_schema_required=True,
            reasoning_enabled=False,
        )

    def scoped_settings(
        self,
        role: ModelRole,
        *,
        model_override: str | None = None,
    ):
        profile = self.profile(role, model_override=model_override)
        model_field, select_field = self._MODEL_FIELDS[profile.provider]
        updates = {
            "llm_provider": profile.provider,
            model_field: profile.model,
            select_field: profile.model,
        }
        return self._settings.model_copy(update=updates), profile

    def _provider_default(self, provider: str) -> str:
        fields = self._MODEL_FIELDS.get(provider)
        if fields is None:
            return ""
        model_field, select_field = fields
        return str(
            getattr(self._settings, select_field, "")
            or getattr(self._settings, model_field, "")
            or ""
        )
