from __future__ import annotations

import ast
import inspect

import pytest
from pydantic import ValidationError

from app.v3 import execution_identity as execution_identity_module
from app.v3.execution_identity import ExecutionAccessSnapshot


H = "a" * 64
S = "b" * 64


def access(**updates):
    values = {
        "tenant_binding": "tenant-a",
        "principal_subject": "user-a1",
        "roles": ("analyst", "reader"),
        "attribute_policy_digest": H,
        "policy_version": "policy-v1",
        "rls_versions": ("rls-orders-v1",),
        "cls_versions": ("cls-orders-v1",),
        "database_route": "analytics-primary",
        "database_destination": "customer-db-a",
        "impersonation_role": None,
        "semantic_context_version": "ctx-v1",
        "source_object_refs": ("entity.orders.amount", "entity.orders.region"),
        "security_parameter_digest": S,
        "attestation_refs": ("attestation:test:1",),
    }
    values.update(updates)
    return ExecutionAccessSnapshot(**values)


def test_role_digest_is_deterministic_and_order_invariant():
    first = access()
    second = access(roles=("reader", "analyst"))
    assert first.role_set_digest == second.role_set_digest
    assert first.execution_access_fingerprint == second.execution_access_fingerprint


def test_source_ref_order_is_fingerprint_invariant():
    first = access()
    second = access(
        source_object_refs=("entity.orders.region", "entity.orders.amount")
    )
    assert first.execution_access_fingerprint == second.execution_access_fingerprint


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("attribute_policy_digest", "c" * 64),
        ("policy_version", "policy-v2"),
        ("rls_versions", ("rls-orders-v2",)),
        ("cls_versions", ("cls-orders-v2",)),
        ("database_route", "analytics-replica"),
        ("database_destination", "customer-db-b"),
        ("security_parameter_digest", "d" * 64),
        ("impersonation_role", "restricted_reader"),
        ("semantic_context_version", "ctx-v2"),
    ],
)
def test_security_lens_changes_access_fingerprint(field, value):
    assert (
        access().execution_access_fingerprint
        != access(**{field: value}).execution_access_fingerprint
    )


def test_attestation_record_identity_does_not_redefine_access_lens():
    first = access(attestation_refs=("attestation:a",))
    second = access(attestation_refs=("attestation:b",))
    assert first.execution_access_fingerprint == second.execution_access_fingerprint


def test_required_security_fields_have_no_magic_defaults():
    required = {
        "tenant_binding",
        "principal_subject",
        "roles",
        "attribute_policy_digest",
        "policy_version",
        "rls_versions",
        "cls_versions",
        "database_route",
        "database_destination",
        "impersonation_role",
        "semantic_context_version",
        "source_object_refs",
        "security_parameter_digest",
        "attestation_refs",
    }
    fields = ExecutionAccessSnapshot.model_fields
    assert required <= set(fields)
    assert all(fields[name].is_required() for name in required)


def test_empty_attestation_and_duplicate_source_refs_fail_validation():
    with pytest.raises(ValidationError):
        access(attestation_refs=())
    with pytest.raises(ValidationError):
        access(
            source_object_refs=(
                "entity.orders.amount",
                "entity.orders.amount",
            )
        )


def test_snapshot_contract_has_no_secret_or_session_fields():
    names = {name.lower() for name in ExecutionAccessSnapshot.model_fields}
    assert not any(
        token in name
        for name in names
        for token in ("password", "secret", "session", "token", "credential")
    )


def test_p5_identity_source_has_no_regex_fuzzy_or_external_access_lookup_dependency():
    tree = ast.parse(inspect.getsource(execution_identity_module))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    forbidden = {
        "re",
        "regex",
        "difflib",
        "rapidfuzz",
        "fuzzywuzzy",
        "Levenshtein",
    }
    assert imported.isdisjoint(forbidden)
    source = inspect.getsource(execution_identity_module)
    assert "MetabaseAgentClient" not in source
    assert ".search(" not in source
    assert ".read_resource(" not in source
    assert "fallback" not in source.lower()
