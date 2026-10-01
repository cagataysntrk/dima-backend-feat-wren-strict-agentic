from app.v3.brain_v2.telemetry import (
    BoundaryName,
    BoundaryTrace,
    BoundaryTraceEvent,
    BrainRunTelemetry,
    OwnerProviderUsage,
)


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


def test_boundary_trace_reports_first_invalid_fingerprint_boundary() -> None:
    trace = BoundaryTrace(
        events=(
            BoundaryTraceEvent(
                boundary=BoundaryName.SCOPE_RESOLVE,
                owner="ResearchScope",
                thread_id="thread-1",
                scope_version_id="scope_v2",
                scope_fingerprint="a" * 64,
            ),
            BoundaryTraceEvent(
                boundary=BoundaryName.MATERIAL_COMPILE,
                owner="ResearchAnalyticalScope",
                thread_id="thread-1",
                scope_version_id="scope_v2",
                scope_fingerprint="b" * 64,
                error_code="R1_MATERIAL_SCOPE_FINGERPRINT_MISMATCH",
                expected_fingerprint="a" * 64,
                observed_fingerprint="b" * 64,
            ),
        )
    )

    receipt = trace.public_receipt()
    assert receipt["last_valid_boundary"] == "dima.scope.resolve"
    assert receipt["first_invalid_boundary"] == "dima.material.compile"
    assert receipt["expected_fingerprint"] == "a" * 64
    assert receipt["observed_fingerprint"] == "b" * 64
    serialized = str(receipt).lower()
    assert "prompt" not in serialized
    assert "reasoning_content" not in serialized


def test_success_boundary_trace_has_no_invalid_boundary() -> None:
    trace = BoundaryTrace(
        events=(
            BoundaryTraceEvent(
                boundary=BoundaryName.SCOPE_RESOLVE,
                owner="ResearchScope",
                scope_version_id="scope_v1",
                scope_fingerprint="c" * 64,
            ),
            BoundaryTraceEvent(
                boundary=BoundaryName.EVIDENCE_ADMIT,
                owner="Evidence",
                scope_version_id="scope_v1",
                scope_fingerprint="c" * 64,
                native_acquisition_count=1,
            ),
        )
    )
    receipt = trace.public_receipt()
    assert receipt["last_valid_boundary"] == "dima.evidence.admit"
    assert receipt["first_invalid_boundary"] is None
