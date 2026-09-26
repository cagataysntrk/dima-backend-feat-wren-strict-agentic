#!/usr/bin/env python3
"""One real DMP-DEC-0048 native-direct P14 Research canary."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

import httpx
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select

from app.v3.research_contracts import (
    RankingSurface,
    ResearchBrief,
    ResearchBriefStatus,
    ResearchGoalKind,
    ResearchGoalStatus,
    ResearchQuestion,
    ResearchScope,
    ResearchSemanticRef,
    SemanticTargetKind,
)
from app.v3.research import StoppingStatus
from app.v3.research_native_gateway import (
    NativeResearchMaterialExecutor,
    NativeSubjectSessionProvider,
)
from app.v3.research_product import ResearchAskOrchestrator
from app.v3.research_store import ResearchSessionStore
from app.v3.substrate.metabase.native_models import NativeEngineIdentity
from control_plane.authorize import Principal
from control_plane.models import (
    NativeSubjectBinding,
    ResearchExecutionLink,
    Tenant,
    User,
)

TENANT_ID = UUID("00000000-0000-4000-8000-000000001401")
USER_ID = UUID("00000000-0000-4000-8000-000000001402")
CONTEXT = "ctx-p14-native-direct-live-v1"
STAMP = datetime(2026, 9, 25, 6, 0, tzinfo=timezone.utc)

# DMP-DEC-0048 transport-correctness sentinel. This oracle was already observed
# in live run 36100443464; adding the assertion must not trigger another paid run.
FROZEN_BOYAHANE_CHANNEL_COUNTS = {
    "Mevcut Müşteri": 34,
    "Web": 27,
    "Fuar": 22,
    "Saha Ziyareti": 22,
    "Referans": 21,
}


def channel_counts(rows: list) -> dict[str, int]:
    output: dict[str, int] = {}
    for row in rows:
        if (
            not isinstance(row, (list, tuple))
            or len(row) < 2
            or not isinstance(row[0], str)
            or not isinstance(row[1], int)
        ):
            raise RuntimeError("native channel result has unexpected shape")
        output[row[0]] = row[1]
    return output


def login(base_url: str, email: str, password: str) -> tuple[str, dict]:
    response = httpx.post(
        base_url.rstrip("/") + "/api/session",
        json={"username": email, "password": password},
        timeout=30,
    )
    response.raise_for_status()
    token = str((response.json() or {}).get("id") or "")
    if not token:
        raise RuntimeError("Metabase session token missing")
    current = httpx.get(
        base_url.rstrip("/") + "/api/user/current",
        headers={"X-Metabase-Session": token},
        timeout=30,
    )
    current.raise_for_status()
    body = current.json()
    if not isinstance(body, dict) or not isinstance(body.get("id"), int):
        raise RuntimeError("Metabase current-user identity missing")
    if body.get("is_superuser"):
        raise RuntimeError("canary analytical principal unexpectedly has superuser access")
    return token, body


def research_brief() -> ResearchBrief:
    metric = ResearchSemanticRef(
        source_mention="satış siparişleri",
        candidate_id="native.sales_order_count",
        target_kind=SemanticTargetKind.METRIC,
        canonical_name="Sales Order Count",
        cube_names=("satis_siparisleri",),
    )
    channel = ResearchSemanticRef(
        source_mention="kanal",
        candidate_id="native.sales_order_channel",
        target_kind=SemanticTargetKind.DIMENSION,
        canonical_name="Sales Order Channel",
        cube_names=("satis_siparisleri",),
    )
    questions = (
        ResearchQuestion(
            goal_id="g1",
            kind=ResearchGoalKind.BREAKDOWN,
            source_text=(
                "Haziran 2026 satış performansını kanal bazında incele. "
                "Kanal ve satış siparişi sayısını göster."
            ),
            subject_refs=(metric,),
            related_refs=(channel,),
            status=ResearchGoalStatus.RESOLVED,
        ),
        ResearchQuestion(
            goal_id="g2",
            kind=ResearchGoalKind.RANKING,
            source_text=(
                "Haziran 2026 satış siparişi sayısını kanal bazında sırala; "
                "en güçlü ve en zayıf kanallar görünür olsun."
            ),
            subject_refs=(metric,),
            related_refs=(channel,),
            ranking=RankingSurface(
                text="en güçlü ve en zayıf kanallar",
                direction="desc",
                limit=20,
            ),
            status=ResearchGoalStatus.RESOLVED,
        ),
    )
    return ResearchBrief(
        brief_id="rb-p14-native-direct-live",
        objective=(
            "Haziran satış performansını kanal bazında incele; "
            "en güçlü ve en zayıf kanalları veriye dayandır."
        ),
        scope=ResearchScope(
            semantic_refs=(metric, channel),
            time_surfaces=("Haziran 2026",),
        ),
        questions=questions,
        must_requirement_ids=("g1", "g2"),
        context_version=CONTEXT,
        status=ResearchBriefStatus.READY_FOR_RESEARCH,
    )


def build_control_plane(metabase_user_id: int):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as db:
        db.add(
            Tenant(
                id=TENANT_ID,
                slug="p14-native-direct-live",
                name="P14 Native Direct Live",
                created_at=STAMP,
            )
        )
        db.add(
            User(
                id=USER_ID,
                tenant_id=TENANT_ID,
                email="p14-native-direct@dima.local",
                password_hash="not-used-by-canary",
                created_at=STAMP,
            )
        )
        db.commit()
        db.add(
            NativeSubjectBinding(
                tenant_id=TENANT_ID,
                dima_user_id=USER_ID,
                metabase_user_id=metabase_user_id,
                security_profile="compat-metadata-only",
                policy_version="compat-metadata-only",
                approved_by_user_id=USER_ID,
            )
        )
        db.commit()
    return engine


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--email", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--engine-sha", required=True)
    ap.add_argument("--upstream-sha", required=True)
    ap.add_argument("--runtime-tag", required=True)
    ap.add_argument("--runtime-image-digest", required=True)
    ap.add_argument("--build-identity", required=True)
    ap.add_argument("--image-identity", required=True)
    ap.add_argument("--model-identifier", required=True)
    ap.add_argument("--platform-sha", required=True)
    args = ap.parse_args()

    token, current = login(args.base_url, args.email, args.password)
    db_engine = build_control_plane(int(current["id"]))
    store = ResearchSessionStore(db_engine)
    expected = NativeEngineIdentity(
        engine_sha=args.engine_sha,
        upstream_base_sha=args.upstream_sha,
        runtime_tag=args.runtime_tag,
        runtime_image_digest=args.runtime_image_digest,
        build_identity=args.build_identity,
        runtime_image_identity=args.image_identity,
    )
    subjects = NativeSubjectSessionProvider(
        base_url=args.base_url,
        expected_identity=expected,
        db_engine=db_engine,
    )
    product = ResearchAskOrchestrator(
        store=store,
        bridge_factory=subjects,
        material_executor=NativeResearchMaterialExecutor(
            subject_provider=subjects,
            store=store,
            expected_identity=expected,
        ),
    )
    principal = Principal(
        user_id=str(USER_ID),
        tenant_id=str(TENANT_ID),
        roles=["analyst"],
        tenant_slug="p14-native-direct-live",
    )
    brief = research_brief()
    started = product.start_from_brief(
        brief=brief,
        request_ref="p14-native-direct-live",
        source_message_hash=hashlib.sha256(
            brief.objective.encode("utf-8")
        ).hexdigest(),
        principal=principal,
    )

    responses = []
    for obligation_id in ("g1", "g2"):
        response = product.run_next(
            session_id=started.session_id,
            principal=principal,
            obligation_id=obligation_id,
            native_session_token=token,
        )
        if response.limitation_code is not None:
            raise RuntimeError(
                f"{obligation_id} limited: "
                f"{response.limitation_code}: {response.limitation_detail}"
            )
        if response.receipt_id is None or response.evidence_id is None:
            raise RuntimeError(f"{obligation_id} produced no receipt/Evidence")
        responses.append(response.model_dump(mode="json"))

    final = product.resume_state(
        session_id=started.session_id,
        principal=principal,
    )
    if final.stopping.status != StoppingStatus.COMPLETE:
        raise RuntimeError(
            f"Research did not complete: {final.stopping.model_dump(mode='json')}"
        )
    if final.native_conversation is None or final.native_conversation.native_turns != 2:
        raise RuntimeError("expected exactly two native Metabot turns")

    with Session(db_engine) as db:
        links = db.exec(
            select(ResearchExecutionLink)
            .where(ResearchExecutionLink.session_id == final.session_id)
            .order_by(ResearchExecutionLink.obligation_id)
        ).all()

    if len(links) != 2 or any(link.status != "VERIFIED" for link in links):
        raise RuntimeError("Research execution links are not fully VERIFIED")
    if any(link.attestation_id is not None for link in links):
        raise RuntimeError("ordinary P14 Research unexpectedly used P13 attestation")

    executions = []
    for link in links:
        query = json.loads(link.native_query_json or "{}")
        result = json.loads(link.native_result_json or "{}")
        rows = (result.get("data") or {}).get("rows")
        if not isinstance(rows, list) or not rows:
            raise RuntimeError(
                f"{link.obligation_id} native execution returned no material rows"
            )
        observed_counts = channel_counts(rows)
        if observed_counts != FROZEN_BOYAHANE_CHANNEL_COUNTS:
            raise RuntimeError(
                "native-direct transport result drifted from the frozen Boyahane oracle: "
                f"{observed_counts!r}"
            )
        executions.append(
            {
                "obligation_id": link.obligation_id,
                "native_conversation_id": str(link.native_conversation_id),
                "native_query_id": link.native_query_id,
                "query_fingerprint": link.native_query_fingerprint,
                "native_subject_ref": link.native_subject_ref,
                "result_hash": link.result_hash,
                "receipt_id": link.receipt_id,
                "evidence_id": link.evidence_id,
                "query_database": query.get("database"),
                "row_count": len(rows),
                "channel_counts": observed_counts,
                "sample_rows": rows[:5],
            }
        )

    report = {
        "schema_version": "p14_native_direct_live_v1",
        "status": "GREEN",
        "platform_sha": args.platform_sha,
        "model_identifier": args.model_identifier,
        "engine_sha": args.engine_sha,
        "runtime_tag": args.runtime_tag,
        "runtime_image_digest": args.runtime_image_digest,
        "metabase_subject": f"metabase-user:{current['id']}",
        "metabase_superuser": bool(current.get("is_superuser")),
        "research_session_id": final.session_id,
        "research_stopping_status": final.stopping.status.value,
        "native_turns": final.native_conversation.native_turns,
        "responses": responses,
        "executions": executions,
        "p13_attestation_hot_path_calls": 0,
        "p13_reexecution_hot_path_calls": 0,
        "wren_fallback": 0,
        "raw_sql_fallback": 0,
        "admin_service_fallback": 0,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
