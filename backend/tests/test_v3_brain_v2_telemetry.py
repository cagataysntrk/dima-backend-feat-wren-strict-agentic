import pytest

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


class _RecordingSpan:
    def __init__(self, name, attributes):
        self.name = name
        self.attributes = dict(attributes or {})

    def set_attribute(self, key, value):
        self.attributes[key] = value


class _RecordingContext:
    def __init__(self, span):
        self.span = span

    def __enter__(self):
        return self.span

    def __exit__(self, exc_type, exc, tb):
        return False


class _RecordingTracer:
    def __init__(self):
        self.spans = []

    def start_as_current_span(self, name, attributes=None):
        span = _RecordingSpan(name, attributes)
        self.spans.append(span)
        return _RecordingContext(span)


def test_opentelemetry_bridge_exports_only_allowlisted_metadata() -> None:
    from app.v3.brain_v2.state import BrainGraphState
    from app.v3.brain_v2.telemetry import OpenTelemetryBridge

    tracer = _RecordingTracer()
    bridge = OpenTelemetryBridge(tracer=tracer)
    state = BrainGraphState(
        thread_id="thread-otel",
        tenant_binding="tenant:test",
        principal_ref="user:test",
        current_user_input="non-exported input",
        scope_version_id="scope_v1",
        evidence_revision=2,
        hypothesis_revision=1,
    )

    with bridge.operation(
        BoundaryName.DISCOVERY_PROJECT_CANDIDATES,
        state=state,
        scope_fingerprint="a" * 64,
        material_fingerprint="b" * 64,
    ) as span:
        span.set_attributes(candidate_count=3, not_allowlisted="drop-me")

    recorded = tracer.spans[0]
    assert recorded.name == "dima.discovery.project_candidates"
    assert recorded.attributes["scope_version_id"] == "scope_v1"
    assert recorded.attributes["scope_fingerprint"] == "a" * 64
    assert recorded.attributes["material_fingerprint"] == "b" * 64
    assert recorded.attributes["candidate_count"] == 3
    serialized = str(recorded.attributes)
    assert "non-exported input" not in serialized
    assert "tenant:test" not in serialized
    assert "user:test" not in serialized
    assert "not_allowlisted" not in recorded.attributes


def test_opentelemetry_bridge_records_stable_error_type_without_message() -> None:
    from app.v3.brain_v2.telemetry import OpenTelemetryBridge

    class DomainError(RuntimeError):
        code = "BRAIN_TEST_STABLE_ERROR"

    tracer = _RecordingTracer()
    bridge = OpenTelemetryBridge(tracer=tracer)

    with pytest.raises(DomainError):
        with bridge.operation(BoundaryName.P19_ASSESS):
            raise DomainError("detail must not be exported")

    recorded = tracer.spans[0]
    assert recorded.attributes["error.type"] == "BRAIN_TEST_STABLE_ERROR"
    assert "detail must not be exported" not in str(recorded.attributes)


def test_required_brain_v21_otel_boundary_names_are_canonical() -> None:
    assert {
        BoundaryName.INTENT_INTERPRET.value,
        BoundaryName.SCOPE_RESOLVE.value,
        BoundaryName.MATERIAL_COMPILE.value,
        BoundaryName.NATIVE_EXECUTE.value,
        BoundaryName.EVIDENCE_ADMIT.value,
        BoundaryName.DISCOVERY_PROJECT_CANDIDATES.value,
        BoundaryName.P19_ASSESS.value,
        BoundaryName.P17_NEXT_TEST.value,
        BoundaryName.P18_ADJUDICATE.value,
        BoundaryName.P20_REPORT.value,
    } == {
        "dima.intent.interpret",
        "dima.scope.resolve",
        "dima.material.compile",
        "dima.native.execute",
        "dima.evidence.admit",
        "dima.discovery.project_candidates",
        "dima.p19.assess",
        "dima.p17.next_test",
        "dima.p18.adjudicate",
        "dima.p20.report",
    }


def test_first_wrong_boundary_receipt_carries_owner_and_execution_refs():
    trace = BoundaryTrace(
        events=(
            BoundaryTraceEvent(
                boundary=BoundaryName.MATERIAL_GROUP,
                owner="MaterialGroup",
                thread_id="t",
                scope_version_id="scope_v1",
                material_group_id="mg_" + "1" * 24,
            ),
            BoundaryTraceEvent(
                boundary=BoundaryName.P18_ADJUDICATE,
                owner="P18",
                thread_id="t",
                scope_version_id="scope_v1",
                requirement_id="g_relationship",
                material_group_id="mg_" + "1" * 24,
                scope_fingerprint="a" * 64,
                material_fingerprint="b" * 64,
                expected_owner="P18",
                observed_owner="P18",
                error_code="P18_TEST_RED",
                error_type="P18_TEST_RED",
            ),
        )
    )
    receipt = trace.public_receipt()
    assert receipt["last_valid_boundary"] == "dima.material.group"
    assert receipt["first_invalid_boundary"] == "dima.p18.adjudicate"
    assert receipt["requirement_id"] == "g_relationship"
    assert receipt["material_group_id"] == "mg_" + "1" * 24
    assert receipt["scope_fingerprint"] == "a" * 64
    assert receipt["material_fingerprint"] == "b" * 64
    assert receipt["expected_owner"] == "P18"
    assert receipt["observed_owner"] == "P18"
    assert receipt["error_type"] == "P18_TEST_RED"


def test_required_runtime_convergence_boundaries_are_all_observable() -> None:
    required = {
        "dima.intent.interpret",
        "dima.scope.resolve",
        "dima.requirements.plan",
        "dima.material.group",
        "dima.native.execute",
        "dima.evidence.admit",
        "dima.requirement.dispatch",
        "dima.p18.adjudicate",
        "dima.p19.assess",
        "dima.completion.evaluate",
        "dima.p20.report",
    }
    assert required.issubset({item.value for item in BoundaryName})
