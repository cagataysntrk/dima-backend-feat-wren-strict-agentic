from __future__ import annotations

import base64
import copy
import json

import pytest
from pydantic import ValidationError

from app.v3.security_identity import (
    ExecutionAccessSnapshotIssuer,
    SecurityIdentityError,
    VerifiedExecutionSecurityFacts,
)
from app.v3.substrate.metabase.canonical import MetabaseCanonicalizer
from app.v3.substrate.metabase.compiler import MetabaseProjectionCompiler
from app.v3.substrate.metabase.models import ConstructedQuery
from app.v3.substrate.metabase.p3a_fixture import build_cases, build_snapshot
from control_plane.authorize import Principal


A = "a" * 64
B = "b" * 64


class DeterministicClient:
    def construct_query(self, portable_query):
        raw = json.dumps(
            portable_query,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return ConstructedQuery(
            serialized_query=base64.b64encode(raw).decode("ascii")
        )


def _fixture(case_index=0):
    snapshot = build_snapshot()
    _, intent = build_cases()[case_index]
    projection = MetabaseCanonicalizer(
        client=DeterministicClient()
    ).canonicalize(
        MetabaseProjectionCompiler.compile(
            intent=intent,
            snapshot=snapshot,
        )
    )
    principal = Principal(
        user_id=intent.principal.principal_subject,
        tenant_id=intent.principal.tenant_binding,
        roles=list(intent.principal.roles),
        tenant_slug=intent.principal.tenant_binding,
    )
    facts = VerifiedExecutionSecurityFacts(
        tenant_binding=intent.principal.tenant_binding,
        principal_subject=intent.principal.principal_subject,
        roles=intent.principal.roles,
        attribute_policy_digest=A,
        policy_version="policy-v1",
        rls_versions=("rls-v1",),
        cls_versions=("cls-v1",),
        database_route="analytics-primary",
        database_destination="customer-db-a",
        impersonation_role=None,
        semantic_context_version=intent.semantic_context_version,
        source_object_refs=projection.manifest.resource_entity_ids,
        security_parameter_digest=B,
        metabase_subject_ref="metabase-user:42",
        attestation_refs=("attestation:policy:1",),
        evidence_refs=("evidence:metabase-session:1",),
    )
    return principal, intent, projection, facts


def _issue(**updates):
    principal, intent, projection, facts = _fixture()
    return ExecutionAccessSnapshotIssuer.issue(
        current_principal=updates.get("principal", principal),
        accepted_intent=updates.get("intent", intent),
        canonical_projection=updates.get("projection", projection),
        verified_security_facts=updates.get("facts", facts),
    )


def test_p10a_exact_verified_identity_issues_existing_p5_snapshot():
    principal, intent, projection, facts = _fixture()
    snapshot = ExecutionAccessSnapshotIssuer.issue(
        current_principal=principal,
        accepted_intent=intent,
        canonical_projection=projection,
        verified_security_facts=facts,
    )

    assert snapshot.tenant_binding == intent.principal.tenant_binding
    assert snapshot.principal_subject == intent.principal.principal_subject
    assert snapshot.roles == tuple(sorted(intent.principal.roles))
    assert snapshot.source_object_refs == tuple(
        sorted(projection.manifest.resource_entity_ids)
    )
    assert snapshot.policy_version == "policy-v1"
    assert snapshot.database_route == "analytics-primary"
    assert "metabase-user:42" in snapshot.attestation_refs
    assert len(snapshot.execution_access_fingerprint) == 64


def test_p10a_same_facts_are_deterministic_across_set_like_order():
    principal, intent, projection, facts = _fixture()
    first = ExecutionAccessSnapshotIssuer.issue(
        current_principal=principal,
        accepted_intent=intent,
        canonical_projection=projection,
        verified_security_facts=facts,
    )
    reordered = facts.model_copy(
        update={
            "roles": tuple(reversed(facts.roles)),
            "source_object_refs": tuple(reversed(facts.source_object_refs)),
            "attestation_refs": ("attestation:policy:1",),
            "evidence_refs": ("evidence:metabase-session:1",),
        }
    )
    second = ExecutionAccessSnapshotIssuer.issue(
        current_principal=principal,
        accepted_intent=intent,
        canonical_projection=projection,
        verified_security_facts=reordered,
    )
    assert first == second
    assert (
        first.execution_access_fingerprint
        == second.execution_access_fingerprint
    )


def test_p10a_missing_current_principal_hard_fails():
    _, intent, projection, facts = _fixture()
    with pytest.raises(SecurityIdentityError) as exc:
        ExecutionAccessSnapshotIssuer.issue(
            current_principal=None,
            accepted_intent=intent,
            canonical_projection=projection,
            verified_security_facts=facts,
        )
    assert exc.value.code == "P10_CURRENT_PRINCIPAL_REQUIRED"


def test_p10a_current_user_mismatch_hard_fails():
    principal, intent, projection, facts = _fixture()
    principal = Principal(
        user_id="different-user",
        tenant_id=principal.tenant_id,
        roles=principal.roles,
    )
    with pytest.raises(SecurityIdentityError) as exc:
        ExecutionAccessSnapshotIssuer.issue(
            current_principal=principal,
            accepted_intent=intent,
            canonical_projection=projection,
            verified_security_facts=facts,
        )
    assert exc.value.code == "P10_CURRENT_ACCEPTED_PRINCIPAL_MISMATCH"


def test_p10a_tenant_mismatch_hard_fails():
    principal, intent, projection, facts = _fixture()
    principal = Principal(
        user_id=principal.user_id,
        tenant_id="tenant-other",
        roles=principal.roles,
    )
    with pytest.raises(SecurityIdentityError) as exc:
        ExecutionAccessSnapshotIssuer.issue(
            current_principal=principal,
            accepted_intent=intent,
            canonical_projection=projection,
            verified_security_facts=facts,
        )
    assert exc.value.code == "P10_CURRENT_ACCEPTED_TENANT_MISMATCH"


def test_p10a_role_set_mismatch_hard_fails():
    principal, intent, projection, facts = _fixture()
    bad_facts = facts.model_copy(update={"roles": ("other-role",)})
    with pytest.raises(SecurityIdentityError) as exc:
        ExecutionAccessSnapshotIssuer.issue(
            current_principal=principal,
            accepted_intent=intent,
            canonical_projection=projection,
            verified_security_facts=bad_facts,
        )
    assert exc.value.code == "P10_FACTS_ROLE_MISMATCH"


def test_p10a_source_object_mismatch_hard_fails():
    principal, intent, projection, facts = _fixture()
    bad_facts = facts.model_copy(
        update={"source_object_refs": ("entity:wrong",)}
    )
    with pytest.raises(SecurityIdentityError) as exc:
        ExecutionAccessSnapshotIssuer.issue(
            current_principal=principal,
            accepted_intent=intent,
            canonical_projection=projection,
            verified_security_facts=bad_facts,
        )
    assert exc.value.code == "P10_SOURCE_OBJECT_MISMATCH"


def test_p10a_semantic_context_mismatch_hard_fails():
    principal, intent, projection, facts = _fixture()
    bad_facts = facts.model_copy(
        update={"semantic_context_version": "ctx-other"}
    )
    with pytest.raises(SecurityIdentityError) as exc:
        ExecutionAccessSnapshotIssuer.issue(
            current_principal=principal,
            accepted_intent=intent,
            canonical_projection=projection,
            verified_security_facts=bad_facts,
        )
    assert exc.value.code == "P10_FACTS_SEMANTIC_CONTEXT_MISMATCH"


def test_p10a_missing_metabase_or_evidence_identity_fails_validation():
    _, _, _, facts = _fixture()
    with pytest.raises(ValidationError):
        VerifiedExecutionSecurityFacts(
            **{
                **facts.model_dump(),
                "metabase_subject_ref": "",
            }
        )
    with pytest.raises(ValidationError):
        VerifiedExecutionSecurityFacts(
            **{
                **facts.model_dump(),
                "evidence_refs": (),
            }
        )


def test_p10a_superadmin_without_explicit_effective_tenant_does_not_infer_one():
    _, intent, projection, facts = _fixture()
    principal = Principal(
        user_id=intent.principal.principal_subject,
        tenant_id=None,
        is_superadmin=True,
        roles=list(intent.principal.roles),
    )
    # Explicit tenant lens is supplied only by accepted intent + verified facts.
    snapshot = ExecutionAccessSnapshotIssuer.issue(
        current_principal=principal,
        accepted_intent=intent,
        canonical_projection=projection,
        verified_security_facts=facts,
    )
    assert snapshot.tenant_binding == intent.principal.tenant_binding

    wrong = facts.model_copy(update={"tenant_binding": "tenant-other"})
    with pytest.raises(SecurityIdentityError) as exc:
        ExecutionAccessSnapshotIssuer.issue(
            current_principal=principal,
            accepted_intent=intent,
            canonical_projection=projection,
            verified_security_facts=wrong,
        )
    assert exc.value.code == "P10_FACTS_TENANT_MISMATCH"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("attribute_policy_digest", "c" * 64),
        ("policy_version", "policy-v2"),
        ("rls_versions", ("rls-v2",)),
        ("cls_versions", ("cls-v2",)),
        ("database_route", "analytics-replica"),
        ("database_destination", "customer-db-b"),
        ("security_parameter_digest", "d" * 64),
        ("impersonation_role", "restricted-reader"),
    ],
)
def test_p10a_security_lens_changes_access_fingerprint(field, value):
    principal, intent, projection, facts = _fixture()
    first = ExecutionAccessSnapshotIssuer.issue(
        current_principal=principal,
        accepted_intent=intent,
        canonical_projection=projection,
        verified_security_facts=facts,
    )
    changed = facts.model_copy(update={field: value})
    second = ExecutionAccessSnapshotIssuer.issue(
        current_principal=principal,
        accepted_intent=intent,
        canonical_projection=projection,
        verified_security_facts=changed,
    )
    assert (
        first.execution_access_fingerprint
        != second.execution_access_fingerprint
    )


def test_p10a_projection_identity_mismatch_hard_fails():
    principal, intent, projection, facts = _fixture()
    broken = projection.model_copy(update={"projection_hash": "e" * 64})
    with pytest.raises(SecurityIdentityError) as exc:
        ExecutionAccessSnapshotIssuer.issue(
            current_principal=principal,
            accepted_intent=intent,
            canonical_projection=broken,
            verified_security_facts=facts,
        )
    assert exc.value.code == "P10_PROJECTION_MISMATCH"


def test_p10a_facts_have_no_session_token_or_competing_fingerprint_surface():
    fields = set(VerifiedExecutionSecurityFacts.model_fields)
    assert "session_token" not in fields
    assert "password" not in fields
    assert "secret" not in fields
    assert "execution_access_fingerprint" not in fields
    assert not hasattr(
        VerifiedExecutionSecurityFacts,
        "execution_access_fingerprint",
    )
