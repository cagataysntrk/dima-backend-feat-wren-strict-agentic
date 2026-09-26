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



def test_manager_lab_builds_semantic_and_temporal_from_distinct_role_scopes(monkeypatch):
    from app.config import Settings
    import app.v2.manager_lab as manager_lab

    settings = Settings(
        v2_research_manager_provider="openrouter",
        v2_research_manager_model="openai/gpt-5.6-sol",
        v2_semantic_linker_provider="openrouter",
        v2_semantic_linker_model="openai/gpt-5.6-luna",
        v2_temporal_normalizer_provider="openrouter",
        v2_temporal_normalizer_model="openai/gpt-5.6-sol",
        v2_research_manager_reasoning=True,
        v2_semantic_linker_reasoning=False,
        v2_temporal_normalizer_reasoning=True,
    )

    built = []

    class _LLM:
        def __init__(self, model):
            self.model = model

        def structured_json(self, *args, **kwargs):
            raise AssertionError("identity-only assembly test")

    def fake_build(scoped):
        model = scoped.openrouter_select_model or scoped.openrouter_model
        built.append(
            (
                model,
                scoped.v2_structured_reasoning_enabled,
            )
        )
        return _LLM(model)

    monkeypatch.setattr(manager_lab, "build_generator", fake_build)
    monkeypatch.setattr(manager_lab, "belki_sar", lambda value: value)

    (
        research_llm,
        research_profile,
        semantic_llm,
        semantic_profile,
        temporal_llm,
        temporal_profile,
    ) = manager_lab._build_role_scoped_manager_models(settings)

    assert research_profile.role == ModelRole.RESEARCH_MANAGER
    assert semantic_profile.role == ModelRole.SEMANTIC_LINKER
    assert temporal_profile.role == ModelRole.TEMPORAL_NORMALIZER

    assert research_llm.model == "openai/gpt-5.6-sol"
    assert semantic_llm.model == "openai/gpt-5.6-luna"
    assert temporal_llm.model == "openai/gpt-5.6-sol"
    assert semantic_llm is not temporal_llm
    assert semantic_profile.model != temporal_profile.model

    assert built == [
        ("openai/gpt-5.6-sol", True),
        ("openai/gpt-5.6-luna", False),
        ("openai/gpt-5.6-sol", True),
    ]


def test_manager_lab_temporal_provider_uses_temporal_structured_client():
    import inspect
    import app.v2.manager_lab as manager_lab

    source = inspect.getsource(manager_lab.ManagerLabHarness.run)
    assert "temporal_structured = getattr(temporal_llm" in source
    assert (
        "StructuredTemporalNormalizationProvider(structured=temporal_structured)"
        in source
    )
    assert "StructuredTemporalNormalizationProvider(structured=semantic_structured)" not in source
