from __future__ import annotations

import base64
import json
from datetime import datetime, timezone

import pytest

from app.v3.execution_identity import (
    DimaQueryReceiptSealer,
    ExecutionAccessSnapshot,
    ExecutionEventIdentity,
    ExecutionResultSnapshot,
    ReceiptSealError,
    RuntimeIdentity,
)
from app.v3.substrate.metabase.canonical import MetabaseCanonicalizer
from app.v3.substrate.metabase.compiler import MetabaseProjectionCompiler
from app.v3.substrate.metabase.models import ConstructedQuery
from app.v3.substrate.metabase.p3a_fixture import build_cases, build_snapshot


def _encode(query):
    return base64.b64encode(
        json.dumps(query, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).decode("ascii")


class DeterministicClient:
    def construct_query(self, portable_query):
        return ConstructedQuery(serialized_query=_encode(portable_query))


def canonical(index=0):
    _, intent = build_cases()[index]
    plan = MetabaseProjectionCompiler.compile(
        intent=intent,
        snapshot=build_snapshot(),
    )
    projection = MetabaseCanonicalizer(
        client=DeterministicClient()
    ).canonicalize(plan)
    return intent, projection


def access_for(intent, projection, **updates):
    values = {
        "tenant_binding": intent.principal.tenant_binding,
        "principal_subject": intent.principal.principal_subject,
        "roles": intent.principal.roles,
        "attribute_policy_digest": "a" * 64,
        "policy_version": "policy-v1",
        "rls_versions": ("rls-v1",),
        "cls_versions": ("cls-v1",),
        "database_route": "analytics-primary",
        "database_destination": "customer-db-a",
        "impersonation_role": None,
        "semantic_context_version": intent.semantic_context_version,
        "source_object_refs": projection.manifest.resource_entity_ids,
        "security_parameter_digest": "b" * 64,
        "attestation_refs": ("attestation:test:1",),
    }
    values.update(updates)
    return ExecutionAccessSnapshot(**values)


def runtime():
    return RuntimeIdentity(
        substrate="metabase",
        runtime_version="v0.63.18",
        image_digest="sha256:" + "1" * 64,
        database_id="database:1",
    )


def result(value=100, *, row_count=1):
    return ExecutionResultSnapshot(
        payload={"rows": [[value]], "cols": [{"name": "metric"}]},
        row_count=row_count,
    )


def event(execution_id):
    return ExecutionEventIdentity(
        execution_id=execution_id,
        executed_at=datetime(2026, 9, 22, 17, 0, tzinfo=timezone.utc),
    )


def seal_one(index=0, *, access_updates=None, result_value=100, execution_id="exec-1"):
    intent, projection = canonical(index)
    access = access_for(intent, projection, **(access_updates or {}))
    receipts = DimaQueryReceiptSealer.seal_execution(
        intent=intent,
        projection=projection,
        access_snapshot=access,
        runtime=runtime(),
        results=(result(result_value),) * len(projection.steps),
        events=tuple(
            event(f"{execution_id}-{i}")
            for i in range(len(projection.steps))
        ),
    )
    return intent, projection, access, receipts


def test_official_receipt_binds_all_p5_identity_surfaces():
    intent, projection, access, receipts = seal_one()
    receipt = receipts[0]
    assert receipt.authority_id == intent.authority_id
    assert receipt.projection_hash == intent.projection_hash
    assert receipt.resolved_intent_hash == intent.resolved_intent_hash
    assert receipt.canonical_query_fingerprint == projection.steps[0].canonical_query_fingerprint
    assert receipt.execution_access_fingerprint == access.execution_access_fingerprint
    assert receipt.principal_fingerprint == intent.principal.fingerprint
    assert receipt.semantic_context_version == intent.semantic_context_version
    assert receipt.resource_entity_ids == projection.manifest.resource_entity_ids
    assert receipt.resource_fingerprints == projection.manifest.resource_fingerprints
    assert receipt.substrate_runtime_version == "v0.63.18"
    assert receipt.substrate_image_digest == "sha256:" + "1" * 64
    assert receipt.receipt_fingerprint is not None
    assert receipt.execution_id == "exec-1-0"
    assert receipt.ephemeral_query_handle is None


def test_missing_runtime_identity_hard_fails():
    intent, projection = canonical()
    with pytest.raises(ReceiptSealError) as exc:
        DimaQueryReceiptSealer.seal_execution(
            intent=intent,
            projection=projection,
            access_snapshot=access_for(intent, projection),
            runtime=None,
            results=(result(),),
            events=(event("exec-1"),),
        )
    assert exc.value.code == "RUNTIME_IDENTITY_REQUIRED"


def test_missing_access_snapshot_hard_fails():
    intent, projection = canonical()
    with pytest.raises(ReceiptSealError) as exc:
        DimaQueryReceiptSealer.seal_execution(
            intent=intent,
            projection=projection,
            access_snapshot=None,
            runtime=runtime(),
            results=(result(),),
            events=(event("exec-1"),),
        )
    assert exc.value.code == "ACCESS_SNAPSHOT_REQUIRED"


@pytest.mark.parametrize(
    ("kind", "mutate", "code"),
    [
        (
            "tenant",
            lambda intent, projection: access_for(
                intent,
                projection,
                tenant_binding="tenant-b",
            ),
            "TENANT_MISMATCH",
        ),
        (
            "principal",
            lambda intent, projection: access_for(
                intent,
                projection,
                principal_subject="user-other",
            ),
            "PRINCIPAL_MISMATCH",
        ),
        (
            "roles",
            lambda intent, projection: access_for(
                intent,
                projection,
                roles=("different-role",),
            ),
            "ROLE_SET_MISMATCH",
        ),
        (
            "semantic-context",
            lambda intent, projection: access_for(
                intent,
                projection,
                semantic_context_version="other-context",
            ),
            "ACCESS_SEMANTIC_CONTEXT_MISMATCH",
        ),
        (
            "resources",
            lambda intent, projection: access_for(
                intent,
                projection,
                source_object_refs=("entity:wrong",),
            ),
            "SOURCE_RESOURCE_MISMATCH",
        ),
    ],
)
def test_access_mismatch_matrix_hard_fails(kind, mutate, code):
    del kind
    intent, projection = canonical()
    with pytest.raises(ReceiptSealError) as exc:
        DimaQueryReceiptSealer.seal_execution(
            intent=intent,
            projection=projection,
            access_snapshot=mutate(intent, projection),
            runtime=runtime(),
            results=(result(),) * len(projection.steps),
            events=tuple(
                event(f"exec-{i}")
                for i in range(len(projection.steps))
            ),
        )
    assert exc.value.code == code


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("authority_id", "authority-other", "AUTHORITY_MISMATCH"),
        ("projection_hash", "c" * 64, "PROJECTION_MISMATCH"),
        ("resolved_intent_hash", "d" * 64, "RESOLVED_INTENT_MISMATCH"),
        ("semantic_context_version", "context-other", "SEMANTIC_CONTEXT_MISMATCH"),
    ],
)
def test_authority_projection_intent_context_mismatch_hard_fails(field, value, code):
    intent, projection = canonical()
    broken = projection.model_copy(update={field: value})
    with pytest.raises(ReceiptSealError) as exc:
        DimaQueryReceiptSealer.seal_execution(
            intent=intent,
            projection=broken,
            access_snapshot=access_for(intent, projection),
            runtime=runtime(),
            results=(result(),) * len(projection.steps),
            events=tuple(
                event(f"exec-{i}")
                for i in range(len(projection.steps))
            ),
        )
    assert exc.value.code == code


def test_query_result_event_cardinality_mismatch_hard_fails():
    intent, projection = canonical(4)
    assert len(projection.steps) == 2
    with pytest.raises(ReceiptSealError) as exc:
        DimaQueryReceiptSealer.seal_execution(
            intent=intent,
            projection=projection,
            access_snapshot=access_for(intent, projection),
            runtime=runtime(),
            results=(result(),),
            events=(event("exec-1"), event("exec-2")),
        )
    assert exc.value.code == "QUERY_RESULT_CARDINALITY_MISMATCH"


def test_receipt_fingerprint_is_stable_across_execution_occurrences_but_receipt_id_is_not():
    _, _, _, first = seal_one(execution_id="occurrence-a")
    _, _, _, second = seal_one(execution_id="occurrence-b")
    assert first[0].receipt_fingerprint == second[0].receipt_fingerprint
    assert first[0].receipt_id != second[0].receipt_id


def test_executed_at_is_event_metadata_not_durable_content_identity():
    intent, projection = canonical()
    access = access_for(intent, projection)
    first = DimaQueryReceiptSealer.seal_execution(
        intent=intent,
        projection=projection,
        access_snapshot=access,
        runtime=runtime(),
        results=(result(),),
        events=(
            ExecutionEventIdentity(
                execution_id="same-event-id",
                executed_at=datetime(2026, 9, 22, 17, 0, tzinfo=timezone.utc),
            ),
        ),
    )[0]
    second = DimaQueryReceiptSealer.seal_execution(
        intent=intent,
        projection=projection,
        access_snapshot=access,
        runtime=runtime(),
        results=(result(),),
        events=(
            ExecutionEventIdentity(
                execution_id="same-event-id",
                executed_at=datetime(2026, 9, 22, 18, 0, tzinfo=timezone.utc),
            ),
        ),
    )[0]
    assert first.receipt_fingerprint == second.receipt_fingerprint
    assert first.receipt_id == second.receipt_id
    assert first.executed_at != second.executed_at


def test_result_mutation_changes_result_and_receipt_fingerprints():
    _, _, _, first = seal_one(result_value=100)
    _, _, _, second = seal_one(result_value=101)
    assert first[0].result_hash != second[0].result_hash
    assert first[0].receipt_fingerprint != second[0].receipt_fingerprint


def test_result_hash_preserves_row_order_but_ignores_object_key_order():
    first = ExecutionResultSnapshot(
        payload={"meta": {"b": 2, "a": 1}, "rows": [[1], [2]]},
        row_count=2,
    )
    same = ExecutionResultSnapshot(
        payload={"rows": [[1], [2]], "meta": {"a": 1, "b": 2}},
        row_count=2,
    )
    reordered_rows = ExecutionResultSnapshot(
        payload={"meta": {"a": 1, "b": 2}, "rows": [[2], [1]]},
        row_count=2,
    )
    assert first.result_hash == same.result_hash
    assert first.result_hash != reordered_rows.result_hash


def test_comparison_base_reference_produce_independent_receipts():
    intent, projection = canonical(4)
    access = access_for(intent, projection)
    receipts = DimaQueryReceiptSealer.seal_execution(
        intent=intent,
        projection=projection,
        access_snapshot=access,
        runtime=runtime(),
        results=(result(100), result(90)),
        events=(event("exec-base"), event("exec-reference")),
    )
    assert [item.step_role for item in receipts] == ["base", "reference"]
    assert len({item.receipt_id for item in receipts}) == 2
    assert len({item.receipt_fingerprint for item in receipts}) == 2


def test_ephemeral_session_or_handle_is_not_a_sealer_input_or_durable_identity():
    import inspect
    parameters = inspect.signature(
        DimaQueryReceiptSealer.seal_execution
    ).parameters
    assert "session_token" not in parameters
    assert "continuation_token" not in parameters
    assert "query_handle" not in parameters
    _, _, _, receipts = seal_one()
    assert receipts[0].ephemeral_query_handle is None



def _seal_exact(
    *,
    intent,
    projection,
    access,
    execution_result,
    execution_id="exec-exact",
):
    return DimaQueryReceiptSealer.seal_execution(
        intent=intent,
        projection=projection,
        access_snapshot=access,
        runtime=runtime(),
        results=(execution_result,) * len(projection.steps),
        events=tuple(
            event(f"{execution_id}-{index}")
            for index in range(len(projection.steps))
        ),
    )


def test_resource_entity_fingerprint_pairing_changes_receipt_fingerprint():
    intent, projection = canonical(7)
    assert len(projection.manifest.resource_entity_ids) >= 2
    fingerprints = list(projection.manifest.resource_fingerprints)
    fingerprints[0], fingerprints[1] = fingerprints[1], fingerprints[0]
    swapped = projection.model_copy(
        update={
            "manifest": projection.manifest.model_copy(
                update={"resource_fingerprints": tuple(fingerprints)}
            )
        }
    )
    access = access_for(intent, projection)

    original_receipt = _seal_exact(
        intent=intent,
        projection=projection,
        access=access,
        execution_result=result(),
    )[0]
    swapped_receipt = _seal_exact(
        intent=intent,
        projection=swapped,
        access=access,
        execution_result=result(),
    )[0]

    assert original_receipt.receipt_fingerprint != swapped_receipt.receipt_fingerprint


@pytest.mark.parametrize("drop_field", ["entity_ids", "fingerprints"])
def test_partial_resource_identity_cardinality_hard_fails(drop_field):
    intent, projection = canonical(7)
    ids = projection.manifest.resource_entity_ids
    fingerprints = projection.manifest.resource_fingerprints
    update = (
        {"resource_entity_ids": ids[:-1]}
        if drop_field == "entity_ids"
        else {"resource_fingerprints": fingerprints[:-1]}
    )
    broken = projection.model_copy(
        update={
            "manifest": projection.manifest.model_copy(update=update)
        }
    )

    with pytest.raises(ReceiptSealError) as exc:
        _seal_exact(
            intent=intent,
            projection=broken,
            access=access_for(intent, projection),
            execution_result=result(),
        )
    assert exc.value.code == "RESOURCE_IDENTITY_CARDINALITY_MISMATCH"


def test_warning_mutation_changes_receipt_fingerprint_and_occurrence_id():
    intent, projection = canonical()
    access = access_for(intent, projection)
    first = _seal_exact(
        intent=intent,
        projection=projection,
        access=access,
        execution_result=ExecutionResultSnapshot(
            payload={"rows": [[100]]},
            row_count=1,
            warnings=("warning-a",),
        ),
        execution_id="same-execution",
    )[0]
    second = _seal_exact(
        intent=intent,
        projection=projection,
        access=access,
        execution_result=ExecutionResultSnapshot(
            payload={"rows": [[100]]},
            row_count=1,
            warnings=("warning-b",),
        ),
        execution_id="same-execution",
    )[0]

    assert first.receipt_fingerprint != second.receipt_fingerprint
    assert first.receipt_id != second.receipt_id


def test_limitation_mutation_changes_receipt_fingerprint_and_occurrence_id():
    intent, projection = canonical()
    access = access_for(intent, projection)
    first = _seal_exact(
        intent=intent,
        projection=projection,
        access=access,
        execution_result=ExecutionResultSnapshot(
            payload={"rows": [[100]]},
            row_count=1,
            limitations=("limit-a",),
        ),
        execution_id="same-execution",
    )[0]
    second = _seal_exact(
        intent=intent,
        projection=projection,
        access=access,
        execution_result=ExecutionResultSnapshot(
            payload={"rows": [[100]]},
            row_count=1,
            limitations=("limit-b",),
        ),
        execution_id="same-execution",
    )[0]

    assert first.receipt_fingerprint != second.receipt_fingerprint
    assert first.receipt_id != second.receipt_id


def test_attestation_ref_changes_proof_identity_not_access_lens_identity():
    intent, projection = canonical()
    first_access = access_for(
        intent,
        projection,
        attestation_refs=("attestation:a",),
    )
    second_access = access_for(
        intent,
        projection,
        attestation_refs=("attestation:b",),
    )
    assert (
        first_access.execution_access_fingerprint
        == second_access.execution_access_fingerprint
    )

    first = _seal_exact(
        intent=intent,
        projection=projection,
        access=first_access,
        execution_result=result(),
        execution_id="same-execution",
    )[0]
    second = _seal_exact(
        intent=intent,
        projection=projection,
        access=second_access,
        execution_result=result(),
        execution_id="same-execution",
    )[0]

    assert first.receipt_fingerprint != second.receipt_fingerprint
    assert first.receipt_id != second.receipt_id
