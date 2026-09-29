from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine

from app.v3.product.contracts import (
    ProductInvestigationRequirement,
    ProductInvestigationRequirementKind,
)
from app.v3.product_routing_store import (
    ProductInvestigationRequirementStore,
)


STAMP = datetime(2026, 9, 27, 2, 30, tzinfo=timezone.utc)


def db_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def requirement():
    return ProductInvestigationRequirement(
        requirement_id="pir_" + "a" * 20,
        kind=ProductInvestigationRequirementKind.FOLLOW_VERIFIED_MATERIAL,
        source_goal_id="g_source",
        source_text="Follow verified material if it opens a new material direction.",
    )


def test_product_routing_requirement_survives_restart_without_raw_prompt_reparse():
    engine = db_engine()
    SQLModel.metadata.create_all(engine)
    store = ProductInvestigationRequirementStore(engine)
    first = store.persist(
        tenant_binding="id:tenant-a",
        research_session_id="rs_" + "1" * 24,
        brief_id="rb_source",
        requirements=(requirement(),),
        accepted_goal_ids=("g_source",),
        now=STAMP,
    )
    restarted = ProductInvestigationRequirementStore(engine)
    loaded = restarted.load(
        tenant_binding="id:tenant-a",
        research_session_id="rs_" + "1" * 24,
    )
    assert loaded == first == (requirement(),)


def test_product_routing_is_idempotent_and_tenant_scoped():
    engine = db_engine()
    SQLModel.metadata.create_all(engine)
    store = ProductInvestigationRequirementStore(engine)
    kwargs = dict(
        tenant_binding="id:tenant-a",
        research_session_id="rs_" + "2" * 24,
        brief_id="rb_source",
        requirements=(requirement(),),
        accepted_goal_ids=("g_source",),
        now=STAMP,
    )
    assert store.persist(**kwargs) == (requirement(),)
    assert store.persist(**kwargs) == (requirement(),)
    assert store.load(
        tenant_binding="id:tenant-b",
        research_session_id="rs_" + "2" * 24,
    ) == ()


def test_product_routing_rejects_dependency_outside_accepted_goal_ids():
    engine = db_engine()
    SQLModel.metadata.create_all(engine)
    store = ProductInvestigationRequirementStore(engine)
    from app.v3.product_routing_store import ProductRoutingError

    try:
        store.persist(
            tenant_binding="id:tenant-a",
            research_session_id="rs_" + "3" * 24,
            brief_id="rb_source",
            requirements=(requirement(),),
            accepted_goal_ids=("g_other",),
            now=STAMP,
        )
    except ProductRoutingError as exc:
        assert exc.code == "PRODUCT_ROUTING_SOURCE_OUT_OF_SCOPE"
    else:
        raise AssertionError("out-of-scope routing dependency must fail closed")
