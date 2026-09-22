from types import SimpleNamespace

from app.v2.model_policy import ModelRole, ModelRolePolicy


def _settings():
    return SimpleNamespace(
        v2_fast_language_provider="openrouter",
        v2_fast_language_model="google/gemini-2.5-flash-lite",
        v2_reference_language_provider="openrouter",
        v2_reference_language_model="openai/gpt-5.6-sol",
        v2_research_manager_provider="openrouter",
        v2_research_manager_model="openai/gpt-5.6-sol",
        v2_semantic_linker_provider="openrouter",
        v2_semantic_linker_model="openai/gpt-5.6-luna",
        v2_temporal_normalizer_provider="openrouter",
        v2_temporal_normalizer_model="openai/gpt-5.6-sol",
        v2_fast_language_reasoning=False,
        v2_reference_language_reasoning=True,
        v2_research_manager_reasoning=True,
        v2_semantic_linker_reasoning=False,
        v2_temporal_normalizer_reasoning=True,
        openrouter_model="google/gemini-2.5-flash-lite",
        openrouter_select_model="",
    )


def test_temporal_normalizer_is_a_distinct_model_role():
    profile = ModelRolePolicy(_settings()).profile(ModelRole.TEMPORAL_NORMALIZER)
    assert profile.model == "openai/gpt-5.6-sol"
    assert profile.provider == "openrouter"
    assert profile.reasoning_enabled is True


def test_semantic_and_temporal_roles_do_not_collapse_to_one_setting():
    policy = ModelRolePolicy(_settings())
    semantic = policy.profile(ModelRole.SEMANTIC_LINKER)
    temporal = policy.profile(ModelRole.TEMPORAL_NORMALIZER)
    assert semantic.model == "openai/gpt-5.6-luna"
    assert temporal.model == "openai/gpt-5.6-sol"
    assert semantic.model != temporal.model


def test_temporal_role_falls_back_to_reference_when_unset():
    settings = _settings()
    settings.v2_temporal_normalizer_provider = ""
    settings.v2_temporal_normalizer_model = ""
    profile = ModelRolePolicy(settings).profile(ModelRole.TEMPORAL_NORMALIZER)
    assert profile.provider == "openrouter"
    assert profile.model == "openai/gpt-5.6-sol"
