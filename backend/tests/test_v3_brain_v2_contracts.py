from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.v3.brain_v2.keys import (
    CognitionPurpose,
    CognitionRequestKey,
    NativeMaterialRequestKey,
)
from app.v3.brain_v2.state import BrainGraphState
from app.v3.brain_v2.views import evidence_digest
from app.v3.evidence import EvidenceArtifact, EvidenceState
from app.v3.research_contracts import ResearchSemanticRef, SemanticTargetKind


def _semantic(candidate_id: str, kind: SemanticTargetKind) -> ResearchSemanticRef:
    return ResearchSemanticRef(
        source_mention=candidate_id,
        candidate_id=candidate_id,
        target_kind=kind,
        canonical_name=candidate_id,
    )


def test_brain_graph_state_rejects_duplicate_domain_refs() -> None:
    with pytest.raises(ValidationError):
        BrainGraphState(
            thread_id="thread-1",
            tenant_binding="id:tenant",
            principal_ref="user-1",
            scope_version_id="scope_v1",
            evidence_ids=("evi_" + "a" * 24, "evi_" + "a" * 24),
        )


def test_cognition_key_is_stable_and_revision_sensitive() -> None:
    base = CognitionRequestKey(
        owner="P19",
        purpose=CognitionPurpose.ASSESS_NEW_EVIDENCE,
        objective_id="goal-1",
        scope_version_id="scope_v1",
        evidence_revision=1,
        hypothesis_revision=2,
        legal_action_profile_hash="a" * 64,
        model_profile="openai/gpt-5.6-luna",
    )
    same = CognitionRequestKey.model_validate(base.model_dump())
    changed = base.model_copy(update={"evidence_revision": 2})

    assert base.fingerprint == same.fingerprint
    assert base.fingerprint != changed.fingerprint


def test_native_material_key_is_scope_and_engine_sensitive() -> None:
    base = NativeMaterialRequestKey(
        tenant="id:tenant",
        principal="user-1",
        scope_version_id="scope_v1",
        material_requirement_fingerprint="b" * 64,
        engine_identity="0.63.18-dima.8@0f16f2b5",
    )
    changed = base.model_copy(update={"scope_version_id": "scope_v2"})

    assert base.fingerprint != changed.fingerprint


def test_evidence_digest_is_deterministic_and_reference_only_when_large() -> None:
    evidence = EvidenceArtifact(
        artifact_id="evi_" + "c" * 24,
        authority_id="auth-1",
        evidence_kind="native_result",
        state=EvidenceState.VERIFIED,
        payload={"rows": [[1, 2], [3, 4]], "label": "exact"},
    )
    refs = (
        _semantic("metric.downtime", SemanticTargetKind.METRIC),
        _semantic("dimension.department", SemanticTargetKind.DIMENSION),
        _semantic("entity.paint", SemanticTargetKind.ENTITY_VALUE),
    )

    first = evidence_digest(
        evidence=evidence,
        scope_version_id="scope_v1",
        semantic_refs=refs,
        max_exact_json_chars=4096,
    )
    second = evidence_digest(
        evidence=evidence,
        scope_version_id="scope_v1",
        semantic_refs=refs,
        max_exact_json_chars=4096,
    )
    bounded = evidence_digest(
        evidence=evidence,
        scope_version_id="scope_v1",
        semantic_refs=refs,
        max_exact_json_chars=2,
    )

    assert first == second
    assert first.metric_ids == ("metric.downtime",)
    assert first.dimension_ids == ("dimension.department",)
    assert first.entity_ids == ("entity.paint",)
    assert first.exact_material_json is not None
    assert bounded.exact_material_json is None
    assert bounded.payload_hash == first.payload_hash
