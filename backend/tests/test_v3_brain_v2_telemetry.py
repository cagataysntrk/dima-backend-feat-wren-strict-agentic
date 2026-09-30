from app.v3.brain_v2.telemetry import BrainRunTelemetry, OwnerProviderUsage


def test_brain_run_telemetry_aggregates_only_non_sensitive_usage() -> None:
    value = BrainRunTelemetry(
        run_ref="provider-free:test",
        product_sha="a" * 40,
        engine_sha="b" * 40,
        engine_release="0.63.18-dima.8",
        model_profile="openai/gpt-5.6-luna",
        native_acquisitions=1,
        provider_usage=(
            OwnerProviderUsage(
                owner="ResearchIntake",
                requests=1,
                prompt_tokens=100,
                completion_tokens=20,
                reasoning_tokens=0,
                cost_usd=0.001,
            ),
            OwnerProviderUsage(
                owner="P19",
                requests=1,
                prompt_tokens=200,
                completion_tokens=40,
                reasoning_tokens=10,
                cost_usd=0.002,
            ),
        ),
        latency_ms=1200,
        cognition_dedup_hits=1,
        native_dedup_hits=2,
        checkpoint_resume_events=1,
        manual_quality=4,
        mechanical_green=True,
    )

    receipt = value.public_receipt()
    assert receipt["total_provider_requests"] == 2
    assert receipt["prompt_tokens"] == 300
    assert receipt["completion_tokens"] == 60
    assert receipt["reasoning_tokens"] == 10
    assert receipt["provider_cost_usd"] == 0.003
    assert receipt["quality_per_provider_call"] == 2
    assert "prompt" not in receipt
    assert "reasoning_content" not in receipt


def test_telemetry_quality_per_dollar_is_absent_when_cost_is_zero() -> None:
    value = BrainRunTelemetry(
        run_ref="provider-free:test-zero-cost",
        product_sha="a" * 40,
        engine_sha="b" * 40,
        engine_release="0.63.18-dima.8",
        model_profile="openai/gpt-5.6-luna",
        native_acquisitions=0,
        latency_ms=10,
        manual_quality=3,
    )
    assert value.quality_per_dollar is None
