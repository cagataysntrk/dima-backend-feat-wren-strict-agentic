from __future__ import annotations

import hashlib
import inspect
import json
from uuid import UUID

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

import app.v3.research_native_gateway as gateway_module
from app.v2.models import (
    ResearchBrief,
    ResearchBriefStatus,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchQuestion,
    ResearchScope,
    ResearchSemanticRef,
    SemanticTargetKind,
)
from app.v3.native_standard.contracts import NativeAttestationEnvelope
from app.v3.research import ObligationState, ResearchManager
from app.v3.research_native_gateway import (
    BASIC_NATIVE,
    NativeResearchMaterialExecutor,
    NativeResourceBindingProvider,
    NativeSubjectSessionProvider,
)
from app.v3.research_product import ResearchAskOrchestrator, ResearchMaterialLimitation
from app.v3.research_store import ResearchSessionStore
from app.v3.substrate.metabase.native_models import (
    NativeEngineIdentity,
    NativeExactOccurrenceExecutionObservation,
)
from control_plane.authorize import Principal
from control_plane.models import (
    NativeResourceBinding,
    NativeSubjectBinding,
    Tenant,
    User,
)


ENGINE_SHA = "cbe313af9ac2d5960f662068e433d328d896fb06"
UPSTREAM_SHA = "2ba2485c78d7e00a9a25f82c00fc201da71590c4"
TAG = "0.63.18-dima.6"
DIGEST = "sha256:40e9a44be49904de3ddf12d4683c768e70955851c10a928a9c8f7d8f60780353"
BUILD = f"github-actions:36042062775:{ENGINE_SHA}"
IMAGE = f"ghcr.io/upcytech/dima-metabase-engine@{DIGEST}"
INSTANCE = UUID("00000000-0000-4000-8000-000000000777")
TENANT = UUID("00000000-0000-4000-8000-000000000701")
USER = UUID("00000000-0000-4000-8000-000000000702")
CONTEXT = "ctx-p14-native-gateway-v1"


def h(value) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def db_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


def principal() -> Principal:
    return Principal(
        user_id=str(USER),
        tenant_id=str(TENANT),
        roles=["analyst"],
        tenant_slug="native-gateway",
    )


def expected_identity() -> NativeEngineIdentity:
    return NativeEngineIdentity(
        engine_sha=ENGINE_SHA,
        upstream_base_sha=UPSTREAM_SHA,
        runtime_tag=TAG,
        runtime_image_digest=DIGEST,
        build_identity=BUILD,
        runtime_image_identity=IMAGE,
    )


def brief() -> ResearchBrief:
    metric = ResearchSemanticRef(
        source_mention="satış siparişleri",
        candidate_id="cand_sales_order_count",
        target_kind=SemanticTargetKind.METRIC,
        canonical_name="Sales Order Count",
        cube_names=("satis_siparisleri",),
    )
    channel = ResearchSemanticRef(
        source_mention="kanal",
        candidate_id="cand_sales_order_channel",
        target_kind=SemanticTargetKind.DIMENSION,
        canonical_name="Sales Order Channel",
        cube_names=("satis_siparisleri",),
    )
    q = ResearchQuestion(
        goal_id="g1",
        kind=ResearchGoalKind.BREAKDOWN,
        source_text="Haziran 2026 satış performansını kanala göre incele.",
        subject_refs=(metric,),
        related_refs=(channel,),
        status=ResearchGoalStatus.RESOLVED,
    )
    return ResearchBrief(
        brief_id="rb-p14-native-gateway",
        objective=q.source_text,
        scope=ResearchScope(
            semantic_refs=(metric, channel),
            time_surfaces=("Haziran 2026",),
        ),
        questions=(q,),
        must_requirement_ids=("g1",),
        context_version=CONTEXT,
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )


def seed(engine):
    with Session(engine) as db:
        db.add(Tenant(id=TENANT, slug="native-gateway", name="Native Gateway"))
        db.add(
            User(
                id=USER,
                tenant_id=TENANT,
                email="p14-native@example.test",
                password_hash="not-used-by-native-gateway",
            )
        )
        db.commit()
        db.add(
            NativeSubjectBinding(
                tenant_id=TENANT,
                dima_user_id=USER,
                metabase_user_id=7,
                security_profile=BASIC_NATIVE,
                policy_version="p14-basic-native-v1",
                approved_by_user_id=USER,
            )
        )
        db.add_all(
            [
                NativeResourceBinding(
                    tenant_id=TENANT,
                    semantic_context_version=CONTEXT,
                    candidate_id="cand_sales_order_count",
                    candidate_kind="metric",
                    semantic_id="metric.sales_order_count",
                    canonical_name="Sales Order Count",
                    locator_kind="table",
                    metabase_database_id=1,
                    metabase_table_id=10,
                    resource_entity_id="native:table:sales-orders",
                    resource_fingerprint=h({"db": 1, "table": 10, "version": "v1"}),
                    resource_version="v1",
                ),
                NativeResourceBinding(
                    tenant_id=TENANT,
                    semantic_context_version=CONTEXT,
                    candidate_id="cand_sales_order_channel",
                    candidate_kind="dimension",
                    semantic_id="dimension.sales_order_channel",
                    canonical_name="Sales Order Channel",
                    locator_kind="field",
                    metabase_database_id=1,
                    metabase_table_id=10,
                    metabase_field_id=20,
                    resource_entity_id="native:field:sales-channel",
                    resource_fingerprint=h({"db": 1, "table": 10, "field": 20, "version": "v1"}),
                    resource_version="v1",
                ),
            ]
        )
        db.commit()


def research_session(engine):
    product = ResearchAskOrchestrator(store=ResearchSessionStore(engine))
    return product.start_from_brief(
        brief=brief(),
        request_ref="p14-native-gateway-test",
        source_message_hash=hashlib.sha256(b"native gateway").hexdigest(),
        principal=principal(),
    )


def attestation(conversation_id, query_id="native-query-1"):
    pmbql = {
        "database": 1,
        "type": "query",
        "query": {
            "source-table": 10,
            "aggregation": [["count"]],
            "breakout": [["field", 20, None]],
            "filter": [">=", ["field", 30, None], "2026-06-01"],
        },
    }
    fp = h(pmbql)
    return NativeAttestationEnvelope.model_validate(
        {
            "exact_serialized_pmbql": pmbql,
            "manifest": {
                "attestation_id": "att-p14-native-1",
                "native_conversation_id": str(conversation_id),
                "native_assistant_message_id": 101,
                "native_tool_call_id": "tool-p14-1",
                "native_query_id": query_id,
                "producer_tool": "construct_notebook_query",
                "exact_pmbql_fingerprint": fp,
                "database_id": 1,
                "primary_source_table_id": 10,
                "referenced_source_table_ids": [10],
                "aggregation_count": 1,
                "aggregations": [
                    {
                        "operator": "count",
                        "argument_kind": "all",
                        "referenced_field_ids": [],
                        "distinct": False,
                    }
                ],
                "native_metric_references": [],
                "breakout_count": 1,
                "breakouts": [
                    {
                        "stage_number": 0,
                        "breakout_index": 0,
                        "field_id": 20,
                        "field_type": "type/Text",
                        "temporal_unit": None,
                    }
                ],
                "material_filter_count": 1,
                "non_temporal_filter_count": 0,
                "temporal_predicates": [
                    {
                        "time_field_id": 30,
                        "operator": ">=",
                        "lower_bound": "2026-06-01",
                        "upper_bound": "2026-07-01",
                        "lower_inclusive": True,
                        "upper_inclusive": False,
                        "field_temporal_type": "type/DateTime",
                        "temporal_unit": "month",
                    }
                ],
                "textual_equality_predicates": [],
                "explicit_join_count": 0,
                "implicit_join_count": 0,
                "implicit_joined_table_ids": [],
                "order_by_count": 0,
                "order_bys": [],
                "limit": None,
                "stage_count": 1,
                "material_query_count": 1,
                "authenticated_metabase_subject": 7,
                "validation_provenance": {
                    "producer_structured_output": "PASSED",
                    "pmbql_schema": "PASSED",
                    "producer_query_id_match": "PASSED",
                    "producer_state_match": "PASSED",
                },
                "permission_provenance": {
                    "current_metabase_user_id": 7,
                    "permission_check": "PASSED",
                    "checked_source_table_ids": [10],
                },
                "runtime_identity": {
                    "repository": "UpcyTech/dima-metabase-engine",
                    "revision_sha": ENGINE_SHA,
                    "upstream_base_sha": UPSTREAM_SHA,
                    "runtime_tag": TAG,
                    "build_identity": BUILD,
                    "image_identity": IMAGE,
                    "runtime_instance_id": str(INSTANCE),
                },
            },
        }
    )


class MaterialBridge:
    def __init__(self, envelope, *, mutate_execution=False):
        self.envelope = envelope
        self.mutate_execution = mutate_execution

    def attest_native_query(self, *, conversation_id, native_query_id):
        assert conversation_id == self.envelope.manifest.native_conversation_id
        assert native_query_id == self.envelope.manifest.native_query_id
        return self.envelope.model_dump(mode="json")

    def execute_native_query(
        self,
        *,
        conversation_id,
        native_query_id,
        expected_pmbql_fingerprint,
        expected_attestation_id,
    ):
        manifest = self.envelope.manifest
        return NativeExactOccurrenceExecutionObservation(
            status_code=200,
            latency_ms=3,
            native_conversation_id=conversation_id,
            native_query_id=native_query_id,
            attestation_id=expected_attestation_id,
            executed_pmbql_fingerprint=(
                "0" * 64 if self.mutate_execution else expected_pmbql_fingerprint
            ),
            runtime_identity=manifest.runtime_identity.model_dump(mode="json"),
            payload={"data": {"rows": [["Web", 4]], "cols": []}},
            attestation=self.envelope.model_dump(mode="json"),
        )


def test_subject_provider_binds_explicit_user_and_rejects_wrong_or_admin_session(monkeypatch):
    engine = db_engine()
    seed(engine)
    session = research_session(engine)
    state = {"id": 7, "is_superuser": False}

    class FakeBridge:
        def __init__(self, **kwargs):
            assert kwargs["session_token"] == "principal-session"

        def current_user(self):
            return dict(state)

        def engine_identity(self):
            return {
                "repository": "UpcyTech/dima-metabase-engine",
                "revision_sha": ENGINE_SHA,
                "upstream_base_sha": UPSTREAM_SHA,
                "runtime_tag": TAG,
                "build_identity": BUILD,
                "image_identity": IMAGE,
                "runtime_instance_id": str(INSTANCE),
            }

        def close(self):
            pass

    monkeypatch.setattr(gateway_module, "NativeEngineBridge", FakeBridge)
    provider = NativeSubjectSessionProvider(
        base_url="http://native.test",
        expected_identity=expected_identity(),
        db_engine=engine,
    )

    with provider.open(
        principal=principal(),
        session=session,
        native_session_token="principal-session",
    ):
        pass

    state["id"] = 8
    with pytest.raises(ResearchMaterialLimitation) as wrong:
        with provider.open(
            principal=principal(),
            session=session,
            native_session_token="principal-session",
        ):
            pass
    assert wrong.value.code == "P14_NATIVE_SUBJECT_MISMATCH"

    state.update(id=7, is_superuser=True)
    with pytest.raises(ResearchMaterialLimitation) as admin:
        with provider.open(
            principal=principal(),
            session=session,
            native_session_token="principal-session",
        ):
            pass
    assert admin.value.code == "P14_NATIVE_ADMIN_SESSION_FORBIDDEN"


def test_missing_binding_or_pass_through_session_fails_closed(monkeypatch):
    engine = db_engine()
    seed(engine)
    session = research_session(engine)
    provider = NativeSubjectSessionProvider(
        base_url="http://native.test",
        expected_identity=expected_identity(),
        db_engine=engine,
    )
    with Session(engine) as db:
        row = db.exec(select(NativeSubjectBinding)).first()
        assert row is not None
        row.enabled = False
        db.add(row)
        db.commit()
    with pytest.raises(ResearchMaterialLimitation) as missing:
        provider.binding_for(principal=principal(), session=session)
    assert missing.value.code == "P14_NATIVE_SUBJECT_BINDING_MISSING"


def test_material_executor_seals_same_occurrence_receipt_and_verified_evidence_without_month_parser():
    engine = db_engine()
    seed(engine)
    session = research_session(engine)
    subjects = NativeSubjectSessionProvider(
        base_url="http://native.test",
        expected_identity=expected_identity(),
        db_engine=engine,
    )
    executor = NativeResearchMaterialExecutor(
        subject_provider=subjects,
        resource_provider=NativeResourceBindingProvider(db_engine=engine),
        expected_identity=expected_identity(),
    )
    conversation = UUID("00000000-0000-4000-8000-000000000799")
    envelope = attestation(conversation)
    outcome = executor.execute(
        principal=principal(),
        session=session,
        obligation_id="g1",
        bridge=MaterialBridge(envelope),
        native_conversation_id=conversation,
        native_query_id=envelope.manifest.native_query_id,
    )

    assert outcome.receipt.authority_kind == "research_material"
    assert outcome.receipt.canonical_query_fingerprint == envelope.manifest.exact_pmbql_fingerprint
    assert outcome.receipt.execution_access_fingerprint
    assert set(outcome.receipt.resource_entity_ids) == {
        "native:table:sales-orders",
        "native:field:sales-channel",
    }
    assert outcome.evidence.verified
    updated = ResearchManager.admit_receipted_evidence(
        session,
        obligation_id="g1",
        receipt=outcome.receipt,
        evidence=outcome.evidence,
        satisfies_obligation=True,
    )
    assert updated.obligations[0].state == ObligationState.VERIFIED

    source = inspect.getsource(gateway_module)
    for forbidden in (
        "TemporalBindingEngine",
        "resolve_period",
        "ResolvedAnalyticsIntent",
        "import re",
        "MetabaseProjectionCompiler",
        "MetabaseCanonicalizer",
    ):
        assert forbidden not in source
    assert session.accepted_brief is not None
    assert session.accepted_brief.scope.time_surfaces == ("Haziran 2026",)


def test_wrong_or_stale_resource_binding_fails_before_execution():
    engine = db_engine()
    seed(engine)
    session = research_session(engine)
    envelope = attestation(UUID("00000000-0000-4000-8000-000000000798"))
    with Session(engine) as db:
        row = db.exec(
            select(NativeResourceBinding).where(
                NativeResourceBinding.candidate_id == "cand_sales_order_channel"
            )
        ).first()
        assert row is not None
        row.metabase_field_id = 999
        db.add(row)
        db.commit()
    provider = NativeResourceBindingProvider(db_engine=engine)
    with pytest.raises(ResearchMaterialLimitation) as exc:
        provider.resolve(
            principal=principal(),
            session=session,
            obligation_id="g1",
            manifest=envelope.manifest,
        )
    assert exc.value.code == "P14_NATIVE_RESOURCE_LOCATOR_MISMATCH"


def test_native_occurrence_mutation_hard_fails_and_unsealed_receipt_cannot_promote_evidence():
    engine = db_engine()
    seed(engine)
    session = research_session(engine)
    subjects = NativeSubjectSessionProvider(
        base_url="http://native.test",
        expected_identity=expected_identity(),
        db_engine=engine,
    )
    executor = NativeResearchMaterialExecutor(
        subject_provider=subjects,
        resource_provider=NativeResourceBindingProvider(db_engine=engine),
        expected_identity=expected_identity(),
    )
    conversation = UUID("00000000-0000-4000-8000-000000000797")
    envelope = attestation(conversation)
    with pytest.raises(ResearchMaterialLimitation) as mutated:
        executor.execute(
            principal=principal(),
            session=session,
            obligation_id="g1",
            bridge=MaterialBridge(envelope, mutate_execution=True),
            native_conversation_id=conversation,
            native_query_id=envelope.manifest.native_query_id,
        )
    assert mutated.value.code == "P14_NATIVE_EXECUTION_FINGERPRINT_MISMATCH"

    outcome = executor.execute(
        principal=principal(),
        session=session,
        obligation_id="g1",
        bridge=MaterialBridge(envelope),
        native_conversation_id=conversation,
        native_query_id=envelope.manifest.native_query_id,
    )
    unsealed = outcome.receipt.model_copy(update={"receipt_fingerprint": None})
    with pytest.raises(Exception, match="P14_RECEIPT_EXECUTION_IDENTITY_INCOMPLETE"):
        ResearchManager.admit_receipted_evidence(
            session,
            obligation_id="g1",
            receipt=unsealed,
            evidence=outcome.evidence,
            satisfies_obligation=True,
        )
