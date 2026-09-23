from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.v3.execution_identity import (
    DimaQueryReceiptSealer,
    ExecutionEventIdentity,
    ExecutionResultSnapshot,
    ReceiptSealError,
    RuntimeIdentity,
)
from app.v3.native_execution import (
    ExecutionResourceBinding,
    NativeCandidateAuthorizationGate,
    NativeCandidateOutcome,
    NativeExecutionTrustError,
    NativeQueryCandidate,
    authorized_artifact_from_canonical_projection,
    period_scope_fingerprint,
)
from app.v3.security_identity import (
    ExecutionAccessSnapshotIssuer,
    SecurityIdentityError,
    VerifiedExecutionSecurityFacts,
)
from app.v3.substrate.metabase.canonical import MetabaseCanonicalizer
from app.v3.substrate.metabase.compiler import MetabaseProjectionCompiler
from app.v3.substrate.metabase.models import ConstructedQuery
from app.v3.substrate.metabase.native_models import NativeEngineIdentity
from app.v3.substrate.metabase.p3a_fixture import build_cases, build_snapshot
from control_plane.authorize import Principal

import base64
import json


def _encode(query):
    return base64.b64encode(
        json.dumps(query, sort_keys=True, separators=(",", ":")).encode()
    ).decode()


class Client:
    def construct_query(self, portable_query):
        return ConstructedQuery(serialized_query=_encode(portable_query))


ENGINE = NativeEngineIdentity(
    engine_sha="c56b71ab23bf2a2d266bac2fba8d165ac059d613",
    upstream_base_sha="2ba2485c78d7e00a9a25f82c00fc201da71590c4",
    runtime_tag="v0.63.18-dima.0",
)


def _metric_intent(period=False):
    return build_cases()[3 if period else 0][1]


def _binding():
    amount = next(
        item
        for item in build_snapshot().current_catalog.objects
        if item.column_name == "amount"
    )
    return ExecutionResourceBinding(
        resource_id=amount.resource_entity_id,
        resource_fingerprint=amount.resource_fingerprint,
    )


def _candidate(*, intent=None, **updates):
    intent = intent or _metric_intent()
    values = {
        "engine_identity": ENGINE,
        "dima_request_id": "req-p13a-1",
        "dima_trace_id": "trace-p13a-1",
        "native_conversation_id": "00000000-0000-4000-8000-000000000013",
        "native_query_id": "native-query-1",
        "resolved_pmbql": {
            "lib/type": "mbql/query",
            "database": 1,
            "stages": [{"source-table": 10, "aggregation": [["count"]]}],
        },
        "portable_query": {"source": "entity:orders"},
        "semantic_refs": tuple(item.semantic_ref for item in intent.metrics),
        "resource_bindings": (_binding(),),
        "native_validation_refs": (
            "native:repair",
            "native:permission-check",
            "native:validate",
            "native:resolve",
            "native:runability",
        ),
        "time_scope_fingerprint": period_scope_fingerprint(intent.period),
    }
    values.update(updates)
    return NativeQueryCandidate.build(**values)


def _authorize(*, intent=None, candidate=None, bindings=None):
    intent = intent or _metric_intent()
    candidate = candidate or _candidate(intent=intent)
    return NativeCandidateAuthorizationGate.authorize(
        intent=intent,
        candidate=candidate,
        authorized_resource_bindings=bindings or (_binding(),),
    )


def _principal(intent):
    return Principal(
        user_id=intent.principal.principal_subject,
        tenant_id=intent.principal.tenant_binding,
        tenant_slug=intent.principal.tenant_binding,
        roles=list(intent.principal.roles),
    )


def _facts(intent, artifact):
    return VerifiedExecutionSecurityFacts(
        tenant_binding=intent.principal.tenant_binding,
        principal_subject=intent.principal.principal_subject,
        roles=intent.principal.roles,
        attribute_policy_digest="a" * 64,
        policy_version="policy-v1",
        rls_versions=(),
        cls_versions=(),
        database_route="analytics-primary",
        database_destination="customer-db-a",
        impersonation_role=None,
        semantic_context_version=intent.semantic_context_version,
        source_object_refs=artifact.resource_entity_ids,
        security_parameter_digest="b" * 64,
        metabase_subject_ref="metabase-user:42",
        attestation_refs=("attestation:p13a:1",),
        evidence_refs=("evidence:session:1",),
    )


def test_p13a_exact_metric_source_candidate_is_allowed():
    decision = _authorize()
    assert decision.outcome == NativeCandidateOutcome.ALLOW
    artifact = decision.authorized_artifact
    assert artifact is not None
    assert artifact.engine_identity.substrate == "metabase-native"
    assert artifact.engine_identity.revision_sha == ENGINE.engine_sha
    assert artifact.steps[0].artifact_fingerprint == _candidate().candidate_artifact_fingerprint


def test_p13a_wrong_semantic_or_resource_scope_blocks():
    intent = _metric_intent()
    semantic = _candidate(intent=intent, semantic_refs=("handle-other",))
    decision = _authorize(intent=intent, candidate=semantic)
    assert decision.outcome == NativeCandidateOutcome.BLOCK
    assert decision.code == "SEMANTIC_SCOPE_VIOLATION"

    wrong = ExecutionResourceBinding(
        resource_id="lab:orders.wrong",
        resource_fingerprint="f" * 64,
    )
    resource = _candidate(intent=intent, resource_bindings=(wrong,))
    decision = _authorize(intent=intent, candidate=resource)
    assert decision.outcome == NativeCandidateOutcome.BLOCK
    assert decision.code == "RESOURCE_PROVENANCE_MISMATCH"


def test_p13a_time_overscope_blocks():
    intent = _metric_intent(period=True)
    candidate = _candidate(
        intent=intent,
        time_scope_fingerprint="f" * 64,
    )
    decision = _authorize(intent=intent, candidate=candidate)
    assert decision.outcome == NativeCandidateOutcome.BLOCK
    assert decision.code == "TIME_SCOPE_VIOLATION"


@pytest.mark.parametrize(
    ("updates", "code"),
    [
        ({"material_filter_count": 1}, "SEMANTIC_SCOPE_VIOLATION"),
        ({"material_join_count": 1}, "RELATIONSHIP_GRAIN_VIOLATION"),
        ({"query_count": 2}, "QUERY_COUNT_VIOLATION"),
    ],
)
def test_p13a_extra_material_scope_blocks(updates, code):
    decision = _authorize(candidate=_candidate(**updates))
    assert decision.outcome == NativeCandidateOutcome.BLOCK
    assert decision.code == code


def test_p13a_candidate_mutation_after_authorization_revalidates_to_block():
    candidate = _candidate()
    allowed = _authorize(candidate=candidate)
    assert allowed.outcome == NativeCandidateOutcome.ALLOW
    assert allowed.authorized_artifact is not None

    candidate.resolved_pmbql["stages"][0]["limit"] = 999
    blocked = NativeCandidateAuthorizationGate.revalidate_candidate(
        candidate=candidate,
        authorized_artifact=allowed.authorized_artifact,
    )
    assert blocked.outcome == NativeCandidateOutcome.BLOCK
    assert blocked.code == "NATIVE_CANDIDATE_ARTIFACT_MUTATED"


def test_p13a_authorized_artifact_rejects_different_execution_artifact():
    artifact = _authorize().authorized_artifact
    assert artifact is not None
    with pytest.raises(NativeExecutionTrustError) as exc:
        artifact.assert_execution_matches(
            role="primary",
            artifact_representation={
                "lib/type": "mbql/query",
                "database": 1,
                "stages": [{"source-table": 999}],
            },
        )
    assert exc.value.code == "EXECUTION_ARTIFACT_MISMATCH"


def test_p13a_p10_uses_common_artifact_without_weakening_source_scope():
    intent = _metric_intent()
    artifact = _authorize(intent=intent).authorized_artifact
    assert artifact is not None
    facts = _facts(intent, artifact)

    snapshot = ExecutionAccessSnapshotIssuer.issue(
        current_principal=_principal(intent),
        accepted_intent=intent,
        execution_artifact=artifact,
        verified_security_facts=facts,
    )
    assert snapshot.source_object_refs == artifact.resource_entity_ids

    wrong = facts.model_copy(update={"source_object_refs": ("entity:wrong",)})
    with pytest.raises(SecurityIdentityError) as exc:
        ExecutionAccessSnapshotIssuer.issue(
            current_principal=_principal(intent),
            accepted_intent=intent,
            execution_artifact=artifact,
            verified_security_facts=wrong,
        )
    assert exc.value.code == "P10_SOURCE_OBJECT_MISMATCH"


def test_p13a_p5_receipt_seals_exact_authorized_native_artifact():
    intent = _metric_intent()
    artifact = _authorize(intent=intent).authorized_artifact
    assert artifact is not None
    access = ExecutionAccessSnapshotIssuer.issue(
        current_principal=_principal(intent),
        accepted_intent=intent,
        execution_artifact=artifact,
        verified_security_facts=_facts(intent, artifact),
    )
    result = ExecutionResultSnapshot(payload={"rows": [[126]]}, row_count=1)
    event = ExecutionEventIdentity(
        execution_id="native-exec-1",
        executed_at=datetime(2026, 9, 23, 10, 0, tzinfo=timezone.utc),
    )
    receipt = DimaQueryReceiptSealer.seal_execution(
        intent=intent,
        execution_artifact=artifact,
        access_snapshot=access,
        runtime=RuntimeIdentity(
            substrate="metabase-native",
            runtime_version=ENGINE.runtime_tag,
            image_digest="sha256:" + "1" * 64,
            database_id="database:1",
        ),
        results=(result,),
        events=(event,),
    )[0]
    assert receipt.canonical_query_fingerprint == artifact.steps[0].artifact_fingerprint
    assert receipt.canonical_query_representation == artifact.steps[0].artifact_representation
    assert receipt.execution_access_fingerprint == access.execution_access_fingerprint
    assert receipt.resource_entity_ids == artifact.resource_entity_ids


def test_p13a_common_artifact_identity_mismatch_fails_p10_and_p5():
    intent = _metric_intent()
    artifact = _authorize(intent=intent).authorized_artifact
    assert artifact is not None
    broken = artifact.model_copy(update={"authority_id": "auth-other"})
    facts = _facts(intent, artifact)

    with pytest.raises(SecurityIdentityError) as exc:
        ExecutionAccessSnapshotIssuer.issue(
            current_principal=_principal(intent),
            accepted_intent=intent,
            execution_artifact=broken,
            verified_security_facts=facts,
        )
    assert exc.value.code == "P10_AUTHORITY_MISMATCH"

    good_access = ExecutionAccessSnapshotIssuer.issue(
        current_principal=_principal(intent),
        accepted_intent=intent,
        execution_artifact=artifact,
        verified_security_facts=facts,
    )
    with pytest.raises(ReceiptSealError) as exc:
        DimaQueryReceiptSealer.seal_execution(
            intent=intent,
            execution_artifact=broken,
            access_snapshot=good_access,
            runtime=RuntimeIdentity(
                substrate="metabase-native",
                runtime_version=ENGINE.runtime_tag,
                image_digest="sha256:" + "1" * 64,
                database_id="database:1",
            ),
            results=(ExecutionResultSnapshot(payload={"rows": [[1]]}, row_count=1),),
            events=(
                ExecutionEventIdentity(
                    execution_id="exec",
                    executed_at=datetime.now(timezone.utc),
                ),
            ),
        )
    assert exc.value.code == "AUTHORITY_MISMATCH"


def test_p13a_historical_canonical_projection_adapts_without_second_receipt_system():
    intent = _metric_intent()
    plan = MetabaseProjectionCompiler.compile(
        intent=intent,
        snapshot=build_snapshot(),
    )
    projection = MetabaseCanonicalizer(client=Client()).canonicalize(plan)
    artifact = authorized_artifact_from_canonical_projection(projection)
    assert artifact.authority_id == projection.authority_id
    assert artifact.steps[0].artifact_fingerprint == projection.steps[0].canonical_query_fingerprint
    assert artifact.steps[0].artifact_representation == projection.steps[0].decoded_query
