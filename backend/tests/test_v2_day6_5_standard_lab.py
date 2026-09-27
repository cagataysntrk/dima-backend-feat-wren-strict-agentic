from app.config import Settings
from app.v2.model_policy import ModelRole
import app.v2.standard_lab as standard_lab


def test_standard_lab_role_assembly_is_explicit_and_split(monkeypatch):
    settings = Settings(
        v2_reference_language_provider="openrouter",
        v2_reference_language_model="openai/gpt-5.6-sol",
        v2_semantic_linker_provider="openrouter",
        v2_semantic_linker_model="openai/gpt-5.6-luna",
        v2_temporal_normalizer_provider="openrouter",
        v2_temporal_normalizer_model="openai/gpt-5.6-sol",
        v2_reference_language_reasoning=True,
        v2_semantic_linker_reasoning=False,
        v2_temporal_normalizer_reasoning=True,
    )

    built = []

    class _LLM:
        def __init__(self, model):
            self.model = model

        def structured_json(self, *args, **kwargs):
            raise AssertionError("assembly-only test")

    def fake_build(scoped):
        model = scoped.openrouter_select_model or scoped.openrouter_model
        built.append((model, scoped.v2_structured_reasoning_enabled))
        return _LLM(model)

    monkeypatch.setattr(standard_lab, "build_generator", fake_build)
    monkeypatch.setattr(standard_lab, "belki_sar", lambda x: x)

    assembly = standard_lab.build_standard_role_assembly(settings)

    assert assembly.cognition_profile.role == ModelRole.REFERENCE_LANGUAGE
    assert assembly.semantic_profile.role == ModelRole.SEMANTIC_LINKER
    assert assembly.temporal_profile.role == ModelRole.TEMPORAL_NORMALIZER
    assert assembly.cognition_profile.model == "openai/gpt-5.6-sol"
    assert assembly.semantic_profile.model == "openai/gpt-5.6-luna"
    assert assembly.temporal_profile.model == "openai/gpt-5.6-sol"
    assert assembly.semantic_llm is not assembly.temporal_llm
    assert built == [
        ("openai/gpt-5.6-sol", True),
        ("openai/gpt-5.6-luna", False),
        ("openai/gpt-5.6-sol", True),
    ]
