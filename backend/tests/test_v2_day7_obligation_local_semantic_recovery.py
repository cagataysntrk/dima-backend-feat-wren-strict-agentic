"""Day7 provider-free attacks for obligation-local semantic retrieval recovery.

These tests certify architecture, not Turkish morphology:
- baseline retrieval stays primary;
- sibling scope is same-obligation containment only;
- recovery runs only after RETRIEVAL_MISS;
- discovery never mints authority;
- BindingGate remains the only minting boundary;
- cross-obligation/cross-domain leakage is impossible;
- hard bounds/sensitivity/current-catalog truth remain enforced.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest

import app.v2.manager_semantics as manager_semantics_module
from app.v2.manager_semantics import ManagerSemanticResolutionAdapter
from app.v2.manager_tools import ResolveSemanticsArgs
from app.v2.models import (
    BoundedSemanticContextV0,
    CompactCubeContextV0,
    CompactSemanticFieldV0,
    ContextVersionV0,
    ConversationStateV2,
)
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.semantic_linker import (
    BoundedSemanticLinker,
    GovernedCurrentTurnCandidateGenerator,
    GovernedSiblingScopeCandidateGenerator,
    SemanticBindingGate,
    SemanticCandidateGenerator,
    SemanticLinkBatchDecision,
    SemanticLinkChoice,
)
from app.v2.source_spans import SourceSpanRegistry
from lab.v2_day7_governed_sibling_scope_discovery import _context


TENANT = "id:day7-owner-local"


def _canonical(binding) -> str:
    target = binding.canonical_target
    return str(
        getattr(target, "canonical_name", None)
        or getattr(target, "dimension_name", None)
        or ""
    )


def _catalog_index(context, schema):
    generator = SemanticCandidateGenerator(
        semantic_context=context,
        schema=schema,
    )
    index = {}
    for kind in ("metric", "dimension", "filter"):
        for item in generator._governed_candidates(kind):
            index[item.card.candidate_id] = _canonical(item)
    return index


class _RecordingProvider:
    def __init__(self, *, id_to_canonical, selections=None):
        self._id_to_canonical = dict(id_to_canonical)
        self._selections = dict(selections or {})
        self.calls = []

    def decide(self, requests):
        records = []
        choices = []
        for request in requests:
            visible = tuple(
                self._id_to_canonical.get(item.candidate_id, item.label)
                for item in request.candidates
            )
            records.append(
                {
                    "surface": request.surface,
                    "request_id": request.request_id,
                    "visible": visible,
                }
            )
            wanted = self._selections.get(request.surface)
            candidate_id = next(
                (
                    item.candidate_id
                    for item in request.candidates
                    if self._id_to_canonical.get(item.candidate_id) == wanted
                ),
                None,
            )
            if wanted is not None and candidate_id is not None:
                choices.append(
                    SemanticLinkChoice(
                        request_id=request.request_id,
                        decision="SELECT",
                        candidate_id=candidate_id,
                    )
                )
            else:
                choices.append(
                    SemanticLinkChoice(
                        request_id=request.request_id,
                        decision="ABSTAIN",
                        reason="NO_MATCH",
                    )
                )
        self.calls.append(tuple(records))
        return SemanticLinkBatchDecision(choices=tuple(choices))


class _SingleCandidateRecordingProvider(_RecordingProvider):
    """Select only when applicability has narrowed to exactly one governed card."""

    def decide(self, requests):
        records = []
        choices = []
        for request in requests:
            visible = tuple(
                self._id_to_canonical.get(item.candidate_id, item.label)
                for item in request.candidates
            )
            records.append(
                {
                    "surface": request.surface,
                    "request_id": request.request_id,
                    "visible": visible,
                }
            )
            if len(request.candidates) == 1:
                choices.append(
                    SemanticLinkChoice(
                        request_id=request.request_id,
                        decision="SELECT",
                        candidate_id=request.candidates[0].candidate_id,
                    )
                )
            else:
                choices.append(
                    SemanticLinkChoice(
                        request_id=request.request_id,
                        decision="ABSTAIN",
                        reason="AMBIGUOUS",
                    )
                )
        self.calls.append(tuple(records))
        return SemanticLinkBatchDecision(choices=tuple(choices))


class _SecondAttemptSelectionProvider(_RecordingProvider):
    """Provider-free stand-in: baseline abstains, narrowed recovery may select."""

    def __init__(self, *, id_to_canonical, selections):
        super().__init__(id_to_canonical=id_to_canonical, selections=selections)
        self._surface_attempts = {}

    def decide(self, requests):
        records = []
        choices = []
        for request in requests:
            visible = tuple(
                self._id_to_canonical.get(item.candidate_id, item.label)
                for item in request.candidates
            )
            records.append(
                {
                    "surface": request.surface,
                    "request_id": request.request_id,
                    "visible": visible,
                }
            )
            attempt = self._surface_attempts.get(request.surface, 0) + 1
            self._surface_attempts[request.surface] = attempt
            wanted = self._selections.get(request.surface)
            candidate_id = next(
                (
                    item.candidate_id
                    for item in request.candidates
                    if self._id_to_canonical.get(item.candidate_id) == wanted
                ),
                None,
            )
            if attempt >= 2 and wanted is not None and candidate_id is not None:
                choices.append(
                    SemanticLinkChoice(
                        request_id=request.request_id,
                        decision="SELECT",
                        candidate_id=candidate_id,
                    )
                )
            else:
                choices.append(
                    SemanticLinkChoice(
                        request_id=request.request_id,
                        decision="ABSTAIN",
                        reason="AMBIGUOUS",
                    )
                )
        self.calls.append(tuple(records))
        return SemanticLinkBatchDecision(choices=tuple(choices))


class _ForbiddenProvider:
    def __init__(self):
        self.calls = 0

    def decide(self, requests):
        self.calls += 1
        raise AssertionError("cognition must not be reached for this attack")


@dataclass(frozen=True)
class _Fixture:
    spans: SourceSpanRegistry
    handles: SemanticHandleRegistry
    adapter: ManagerSemanticResolutionAdapter
    provider: object
    context: BoundedSemanticContextV0
    schema: dict


def _fixture(*, context=None, schema=None, provider=None, diagnostic_sink=None) -> _Fixture:
    if context is None or schema is None:
        service, default_context = _context()
        context = context or default_context
        schema = schema or service.schema()
    spans = SourceSpanRegistry()
    handles = SemanticHandleRegistry()
    provider = provider or _RecordingProvider(
        id_to_canonical=_catalog_index(context, schema),
    )
    adapter = ManagerSemanticResolutionAdapter(
        source_spans=spans,
        semantic_handles=handles,
        semantic_context=context,
        conversation=ConversationStateV2(),
        schema=schema,
        tenant_binding=TENANT,
        session_id="day7-owner-local",
        thread_id="day7-owner-local",
        semantic_decision_provider=provider,
        semantic_diagnostic_sink=diagnostic_sink,
    )
    return _Fixture(
        spans=spans,
        handles=handles,
        adapter=adapter,
        provider=provider,
        context=context,
        schema=schema,
    )


def _resolve(
    fx: _Fixture,
    *,
    text: str,
    entries: tuple[tuple[str, str, str], ...],
    message_id: str = "turn-owner-local",
):
    """entries = (owner_id, exact_surface, kind_hint)."""
    fx.spans.register_message(message_id=message_id, text=text)
    refs = tuple(
        fx.spans.mint_exact(
            message_id=message_id,
            surface=surface,
        ).source_ref
        for _, surface, _ in entries
    )
    return fx.adapter.resolve(
        ResolveSemanticsArgs(
            provenance="USER_SOURCE",
            source_refs=refs,
            source_obligation_ids=tuple(owner for owner, _, _ in entries),
            target_kind_hints=tuple(kind for _, _, kind in entries),
        )
    ), refs


def _resolved_canonicals(fx: _Fixture, result):
    out = {}
    for item in result.resolved:
        binding = fx.handles.binding_for_execution(
            item.handle.handle_id,
            tenant_binding=TENANT,
            context_version=fx.context.context_version.version,
        )
        out[(item.owner_id, item.source_ref)] = _canonical(binding)
    return out


def test_same_obligation_retrieval_miss_recovers_then_binding_gate_mints():
    service, context = _context()
    schema = service.schema()
    provider = _RecordingProvider(
        id_to_canonical=_catalog_index(context, schema),
        selections={"bölgelere": "region_axis_m"},
    )
    fx = _fixture(context=context, schema=schema, provider=provider)

    before = set(fx.handles._bindings)
    result, refs = _resolve(
        fx,
        text="Net gelir ile bölgelere göre incele.",
        entries=(
            ("U1", "Net gelir", "metric"),
            ("U1", "bölgelere", "dimension"),
        ),
    )

    resolved = _resolved_canonicals(fx, result)
    assert resolved[("U1", refs[0])] == "net_value_x"
    assert resolved[("U1", refs[1])] == "region_axis_m"
    assert result.unresolved_source_refs == ()
    assert len(set(fx.handles._bindings) - before) == 2

    fallback_calls = [
        record
        for call in provider.calls
        for record in call
        if record["surface"] == "bölgelere"
    ]
    assert len(fallback_calls) == 1
    assert set(fallback_calls[0]["visible"]) == {
        "region_axis_m",
        "product_axis_n",
        "channel_axis_c",
    }


def test_same_obligation_unknown_dimension_abstains_and_mints_no_dimension_authority():
    service, context = _context()
    schema = service.schema()
    provider = _RecordingProvider(
        id_to_canonical=_catalog_index(context, schema),
        selections={},
    )
    fx = _fixture(context=context, schema=schema, provider=provider)

    result, refs = _resolve(
        fx,
        text="Net gelir ile tamamen bilinmeyen ekseni incele.",
        entries=(
            ("U1", "Net gelir", "metric"),
            ("U1", "tamamen bilinmeyen eksen", "dimension"),
        ),
    )

    resolved = _resolved_canonicals(fx, result)
    assert resolved[("U1", refs[0])] == "net_value_x"
    assert ("U1", refs[1]) not in resolved
    assert refs[1] in result.unresolved_source_refs
    assert len(fx.handles._bindings) == 1
    assert any(
        record["surface"] == "tamamen bilinmeyen eksen"
        for call in provider.calls
        for record in call
    )


def test_wrong_sibling_domain_never_exposes_cross_domain_candidate():
    service, context = _context()
    schema = service.schema()
    provider = _RecordingProvider(
        id_to_canonical=_catalog_index(context, schema),
        selections={},
    )
    fx = _fixture(context=context, schema=schema, provider=provider)

    result, refs = _resolve(
        fx,
        text="Net gelir ile bölümlerle ilişkiyi incele.",
        entries=(
            ("U1", "Net gelir", "metric"),
            ("U1", "bölümlerle", "dimension"),
        ),
    )

    record = next(
        record
        for call in provider.calls
        for record in call
        if record["surface"] == "bölümlerle"
    )
    assert "department_axis_d" not in record["visible"]
    assert set(record["visible"]) == {
        "region_axis_m",
        "product_axis_n",
        "channel_axis_c",
    }
    assert refs[1] in result.unresolved_source_refs
    assert len(fx.handles._bindings) == 1


def test_two_obligations_cannot_share_sibling_scope_or_grounded_authority():
    service, context = _context()
    schema = service.schema()
    provider = _RecordingProvider(
        id_to_canonical=_catalog_index(context, schema),
        selections={
            "bölgelere": "region_axis_m",
            "bölümlerle": "department_axis_d",
        },
    )
    fx = _fixture(context=context, schema=schema, provider=provider)

    result, refs = _resolve(
        fx,
        text=(
            "Net gelir bölgelere göre; "
            "duruş süresi bölümlerle incelensin."
        ),
        entries=(
            ("U_SALES", "Net gelir", "metric"),
            ("U_SALES", "bölgelere", "dimension"),
            ("U_OPS", "duruş süresi", "metric"),
            ("U_OPS", "bölümlerle", "dimension"),
        ),
    )

    resolved = _resolved_canonicals(fx, result)
    assert resolved[("U_SALES", refs[0])] == "net_value_x"
    assert resolved[("U_SALES", refs[1])] == "region_axis_m"
    assert resolved[("U_OPS", refs[2])] == "downtime_min_d"
    assert resolved[("U_OPS", refs[3])] == "department_axis_d"

    records = {
        record["surface"]: record
        for call in provider.calls
        for record in call
        if record["surface"] in {"bölgelere", "bölümlerle"}
    }
    assert set(records["bölgelere"]["visible"]) == {
        "region_axis_m",
        "product_axis_n",
        "channel_axis_c",
    }
    assert "department_axis_d" not in records["bölgelere"]["visible"]

    assert set(records["bölümlerle"]["visible"]) == {
        "department_axis_d",
        "line_axis_p",
    }
    assert "region_axis_m" not in records["bölümlerle"]["visible"]


def test_no_bound_sibling_means_no_fallback_and_no_cognition():
    service, context = _context()
    schema = service.schema()
    provider = _ForbiddenProvider()
    fx = _fixture(context=context, schema=schema, provider=provider)

    result, refs = _resolve(
        fx,
        text="Bölgelere göre incele.",
        entries=(("U1", "Bölgelere", "dimension"),),
    )

    assert result.resolved == ()
    assert result.unresolved_source_refs == (refs[0],)
    assert provider.calls == 0
    assert len(fx.handles._bindings) == 0


def _wide_context(*, unrelated_dimensions: int = 0):
    wide_dimensions = tuple(
        CompactSemanticFieldV0(
            canonical_name=f"axis_{index:02d}",
            display=f"Axis {index:02d}",
            synonyms=(f"axis {index:02d}",),
        )
        for index in range(60)
    )
    cubes = [
        CompactCubeContextV0(
            canonical_name="wide_cube",
            measures=(
                CompactSemanticFieldV0(
                    canonical_name="revenue",
                    display="Revenue",
                    synonyms=("revenue",),
                ),
            ),
            dimensions=wide_dimensions,
        )
    ]
    if unrelated_dimensions:
        cubes.append(
            CompactCubeContextV0(
                canonical_name="unrelated_cube",
                dimensions=tuple(
                    CompactSemanticFieldV0(
                        canonical_name=f"unrelated_{index:02d}",
                        display=f"Unrelated {index:02d}",
                        synonyms=(f"unrelated {index:02d}",),
                    )
                    for index in range(unrelated_dimensions)
                ),
            )
        )
    context = BoundedSemanticContextV0(
        context_version=ContextVersionV0(
            version="ctx-owner-local-wide",
            mdl_version="mdl-owner-local-wide",
            compact_catalog_builder_version="day7",
            business_rules_hash="0" * 64,
            prompt_context_policy_version="day7",
        ),
        cubes=tuple(cubes),
    )
    schema = {
        "models": [],
        "cubes": [
            {
                "name": cube.canonical_name,
                "measures": [field.canonical_name for field in cube.measures],
                "dimensions": [
                    field.canonical_name for field in cube.dimensions
                ],
                "dimension_values": {},
            }
            for cube in cubes
        ],
        "company_vocabulary": [],
    }
    return context, schema


def test_scope_above_48_stays_too_broad_and_never_reaches_cognition():
    context, schema = _wide_context()
    provider = _ForbiddenProvider()
    fx = _fixture(context=context, schema=schema, provider=provider)

    result, refs = _resolve(
        fx,
        text="Revenue ile unmatched dimension incele.",
        entries=(
            ("U1", "Revenue", "metric"),
            ("U1", "unmatched dimension", "dimension"),
        ),
    )
    assert refs[1] in result.unresolved_source_refs
    assert provider.calls == 0

    base = SemanticCandidateGenerator(
        semantic_context=context,
        schema=schema,
    )
    scoped = GovernedSiblingScopeCandidateGenerator(
        base=base,
        sibling_cube_names=("wide_cube",),
    )
    linker = BoundedSemanticLinker(
        generator=scoped,
        binding_gate=SemanticBindingGate(
            semantic_handles=SemanticHandleRegistry(),
            tenant_binding=TENANT,
            context_version=context.context_version.version,
        ),
        provider=provider,
    )
    selection = linker.resolve(
        (("broad", "unmatched dimension", "dimension"),),
        provenance_type="USER_SOURCE",
    )[0]
    assert selection.status == "CANDIDATE_SET_TOO_BROAD"
    assert provider.calls == 0


def _sensitive_context():
    context = BoundedSemanticContextV0(
        context_version=ContextVersionV0(
            version="ctx-owner-local-sensitive",
            mdl_version="mdl-owner-local-sensitive",
            compact_catalog_builder_version="day7",
            business_rules_hash="0" * 64,
            prompt_context_policy_version="day7",
        ),
        cubes=(
            CompactCubeContextV0(
                canonical_name="safe_cube",
                measures=(
                    CompactSemanticFieldV0(
                        canonical_name="revenue",
                        display="Revenue",
                        synonyms=("revenue",),
                    ),
                ),
                dimensions=(
                    CompactSemanticFieldV0(
                        canonical_name="customer_email",
                        display="Customer Email",
                        synonyms=("customer email",),
                    ),
                ),
            ),
        ),
    )
    schema = {
        "models": [
            {
                "name": "safe_model",
                "columns": [
                    {
                        "name": "customer_email",
                        "type": "VARCHAR",
                        "sensitivity": "person",
                    }
                ],
            }
        ],
        "cubes": [
            {
                "name": "safe_cube",
                "measures": ["revenue"],
                "dimensions": ["customer_email"],
                "dimension_values": {
                    "customer_email": ["private@example.com"],
                },
            }
        ],
        "company_vocabulary": [],
    }
    return context, schema


def test_sensitive_filter_candidate_is_never_exposed_by_scope_recovery():
    context, schema = _sensitive_context()
    provider = _ForbiddenProvider()
    fx = _fixture(context=context, schema=schema, provider=provider)

    result, refs = _resolve(
        fx,
        text="Revenue için private@example.com filtresini incele.",
        entries=(
            ("U1", "Revenue", "metric"),
            ("U1", "private@example.com", "filter"),
        ),
    )

    # The user's own exact sensitive value may bind locally without being sent
    # to cognition. The privacy invariant is candidate exposure, not prohibition of
    # governed exact USER_SOURCE authority.
    sensitive_item = next(
        item for item in result.resolved
        if item.source_ref == refs[1]
    )
    assert sensitive_item.handle.sensitive is True
    assert result.unresolved_source_refs == ()
    assert provider.calls == 0
    assert len(fx.handles._bindings) == 2

    base = SemanticCandidateGenerator(
        semantic_context=context,
        schema=schema,
    )
    scoped = GovernedSiblingScopeCandidateGenerator(
        base=base,
        sibling_cube_names=("safe_cube",),
    )
    candidate_set = scoped.generate(
        request_id="sensitive",
        surface="private@example.com",
        kind_hint="filter",
    )
    assert candidate_set.bindings == ()


def test_unrelated_catalog_growth_does_not_change_scoped_candidates():
    base_context, base_schema = _wide_context(unrelated_dimensions=0)
    grown_context, grown_schema = _wide_context(unrelated_dimensions=80)

    base = GovernedSiblingScopeCandidateGenerator(
        base=SemanticCandidateGenerator(
            semantic_context=base_context,
            schema=base_schema,
        ),
        sibling_cube_names=("wide_cube",),
        max_candidates=100,
    )
    grown = GovernedSiblingScopeCandidateGenerator(
        base=SemanticCandidateGenerator(
            semantic_context=grown_context,
            schema=grown_schema,
        ),
        sibling_cube_names=("wide_cube",),
        max_candidates=100,
    )
    base_names = {
        _canonical(item)
        for item in base.scoped_bindings("dimension")
    }
    grown_names = {
        _canonical(item)
        for item in grown.scoped_bindings("dimension")
    }

    assert len(base_names) == 60
    assert grown_names == base_names


def test_existing_baseline_candidate_remains_owner_and_skips_sibling_fallback(monkeypatch):
    service, context = _context()
    schema = service.schema()
    provider = _RecordingProvider(
        id_to_canonical=_catalog_index(context, schema),
        selections={},
    )
    fx = _fixture(context=context, schema=schema, provider=provider)

    class _ForbiddenSiblingGenerator:
        def __init__(self, *args, **kwargs):
            raise AssertionError(
                "sibling fallback must not instantiate when baseline already resolves"
            )

    monkeypatch.setattr(
        manager_semantics_module,
        "GovernedSiblingScopeCandidateGenerator",
        _ForbiddenSiblingGenerator,
    )

    result, refs = _resolve(
        fx,
        text="Net gelir ile bölgeler bazında incele.",
        entries=(
            ("U1", "Net gelir", "metric"),
            ("U1", "bölgeler", "dimension"),
        ),
    )
    resolved = _resolved_canonicals(fx, result)
    assert resolved[("U1", refs[0])] == "net_value_x"
    assert resolved[("U1", refs[1])] == "region_axis_m"
    assert result.unresolved_source_refs == ()


# D10-N: cross-obligation current-turn applicability recovery.
# Existing authority is discovery context only; BindingGate still mints the new source edge.

def test_current_turn_metric_context_recovers_generic_root_surface_without_handle_copy():
    service, context = _context()
    schema = service.schema()
    diagnostics = []
    provider = _SecondAttemptSelectionProvider(
        id_to_canonical=_catalog_index(context, schema),
        selections={"gözlenen analitik sapma": "net_value_x"},
    )
    fx = _fixture(
        context=context,
        schema=schema,
        provider=provider,
        diagnostic_sink=diagnostics.append,
    )

    result, refs = _resolve(
        fx,
        text=(
            "Net gelir ana hedeftir; duruş süresi yalnız bağlam bilgisidir; "
            "gözlenen analitik sapmayı araştır."
        ),
        entries=(
            ("U_PERF", "Net gelir", "metric"),
            ("U_ROOT", "gözlenen analitik sapma", "metric"),
        ),
        message_id="turn-d10-n-current-metric",
    )

    resolved = _resolved_canonicals(fx, result)
    assert resolved[("U_PERF", refs[0])] == "net_value_x"
    assert resolved[("U_ROOT", refs[1])] == "net_value_x"
    assert result.unresolved_source_refs == ()

    root_receipts = [
        item for item in diagnostics
        if item.get("owner_obligation_id") == "U_ROOT"
    ]
    assert [item["discovery_pass"] for item in root_receipts] == [
        "pass1",
        "current_turn_applicability",
    ]
    assert root_receipts[0]["selection"]["status"] == "ABSTAIN"
    assert root_receipts[1]["retrieval_backend"] == "governed_current_turn_context_v1"
    assert root_receipts[1]["candidate_count"] >= 1
    assert root_receipts[1]["selection"]["status"] == "BOUND"

    # Same canonical sem_* may be idempotent, but the source-bound authority edge is new.
    assert refs[0] != refs[1]
    assert len(result.resolved) == 2
    assert {item.source_ref for item in result.resolved} == set(refs)


def test_current_turn_multiple_metric_candidates_require_linker_and_may_abstain():
    service, context = _context()
    schema = service.schema()
    diagnostics = []
    provider = _RecordingProvider(
        id_to_canonical=_catalog_index(context, schema),
        selections={},
    )
    fx = _fixture(
        context=context,
        schema=schema,
        provider=provider,
        diagnostic_sink=diagnostics.append,
    )

    result, refs = _resolve(
        fx,
        text=(
            "Net gelir ve duruş süresi incelensin; "
            "gözlenen analitik sapma ayrıca araştırılsın."
        ),
        entries=(
            ("U_SALES", "Net gelir", "metric"),
            ("U_OPS", "duruş süresi", "metric"),
            ("U_ROOT", "gözlenen analitik sapma", "metric"),
        ),
        message_id="turn-d10-n-many-metrics",
    )

    resolved = _resolved_canonicals(fx, result)
    assert resolved[("U_SALES", refs[0])] == "net_value_x"
    assert resolved[("U_OPS", refs[1])] == "downtime_min_d"
    assert ("U_ROOT", refs[2]) not in resolved
    assert refs[2] in result.unresolved_source_refs

    root_receipts = [
        item for item in diagnostics
        if item.get("owner_obligation_id") == "U_ROOT"
    ]
    assert [item["discovery_pass"] for item in root_receipts] == [
        "pass1",
        "current_turn_applicability",
    ]
    assert root_receipts[0]["selection"]["status"] == "ABSTAIN"
    assert root_receipts[1]["candidate_count"] == 2
    assert root_receipts[1]["selection"]["status"] == "ABSTAIN"
    # The second call is permitted only because the governed current-turn pool
    # materially narrows the pass1 set; abstention still mints no authority.


def test_prior_turn_governed_handle_is_not_current_turn_candidate_context():
    service, context = _context()
    schema = service.schema()
    provider = _RecordingProvider(
        id_to_canonical=_catalog_index(context, schema),
        selections={"gözlenen analitik sapma": "net_value_x"},
    )
    fx = _fixture(context=context, schema=schema, provider=provider)

    first, _ = _resolve(
        fx,
        text="Net gelir incelensin.",
        entries=(("U_PERF", "Net gelir", "metric"),),
        message_id="turn-d10-n-prior",
    )
    assert len(first.resolved) == 1

    before_calls = len(provider.calls)
    second, refs = _resolve(
        fx,
        text="Gözlenen analitik sapmayı araştır.",
        entries=(("U_ROOT", "Gözlenen analitik sapma", "metric"),),
        message_id="turn-d10-n-current",
    )

    assert second.resolved == ()
    assert second.unresolved_source_refs == (refs[0],)
    # No current-call governed sibling exists, so old registry truth cannot trigger
    # current-turn applicability cognition.
    assert len(provider.calls) == before_calls


def test_current_turn_dimension_context_can_support_relationship_counterpart_discovery():
    service, context = _context()
    schema = service.schema()
    diagnostics = []
    provider = _SecondAttemptSelectionProvider(
        id_to_canonical=_catalog_index(context, schema),
        selections={"ilişki için analitik eksen": "department_axis_d"},
    )
    fx = _fixture(
        context=context,
        schema=schema,
        provider=provider,
        diagnostic_sink=diagnostics.append,
    )

    result, refs = _resolve(
        fx,
        text=(
            "Bölüm kırılımını çıkar; bölge yalnız bağlam bilgisidir; "
            "ilişki için analitik ekseni değerlendir."
        ),
        entries=(
            ("U_BREAK", "Bölüm", "dimension"),
            ("U_REL", "ilişki için analitik eksen", "dimension"),
        ),
        message_id="turn-d10-n-current-dimension",
    )

    resolved = _resolved_canonicals(fx, result)
    assert resolved[("U_BREAK", refs[0])] == "department_axis_d"
    assert resolved[("U_REL", refs[1])] == "department_axis_d"
    recovery = next(
        item for item in diagnostics
        if item.get("owner_obligation_id") == "U_REL"
        and item.get("discovery_pass") == "current_turn_applicability"
    )
    assert recovery["candidate_count"] >= 1
    assert recovery["selection"]["status"] == "BOUND"


def test_current_turn_recovery_never_expands_to_filter_kind():
    service, context = _context()
    schema = service.schema()
    provider = _RecordingProvider(
        id_to_canonical=_catalog_index(context, schema),
        selections={},
    )
    diagnostics = []
    fx = _fixture(
        context=context,
        schema=schema,
        provider=provider,
        diagnostic_sink=diagnostics.append,
    )

    result, refs = _resolve(
        fx,
        text="Kuzey ve belirsiz kapsam.",
        entries=(
            ("U_FILTER", "Kuzey", "filter"),
            ("U_OTHER", "belirsiz kapsam", "filter"),
        ),
        message_id="turn-d10-n-filter",
    )

    # Current-turn recovery is intentionally metric/dimension only.
    assert refs[1] in result.unresolved_source_refs
    assert not any(
        item.get("discovery_pass") == "current_turn_applicability"
        for item in diagnostics
        if item.get("owner_obligation_id") == "U_OTHER"
    )


def test_current_turn_metric_metadata_hydrates_cross_owner_dimension_applicability():
    service, context = _context()
    schema = service.schema()
    fx = _fixture(context=context, schema=schema, provider=_ForbiddenProvider())

    resolved, _ = _resolve(
        fx,
        text="Duruş süresi incelensin.",
        entries=(("U_METRIC", "Duruş süresi", "metric"),),
        message_id="turn-d10-o-scope-source",
    )
    assert len(resolved.resolved) == 1

    applicable = fx.adapter._current_turn_candidate_bindings(
        resolved=resolved.resolved,
        kind_hint="dimension",
    )
    assert {_canonical(item) for item in applicable} == {
        "department_axis_d",
        "line_axis_p",
    }


def test_cross_domain_current_turn_context_has_no_coherent_applicability_scope():
    service, context = _context()
    schema = service.schema()
    fx = _fixture(context=context, schema=schema, provider=_ForbiddenProvider())

    resolved, _ = _resolve(
        fx,
        text="Net gelir ve duruş süresi birlikte incelensin.",
        entries=(
            ("U_SALES", "Net gelir", "metric"),
            ("U_OPS", "duruş süresi", "metric"),
        ),
        message_id="turn-d10-o-cross-domain",
    )
    assert len(resolved.resolved) == 2

    applicable = fx.adapter._current_turn_candidate_bindings(
        resolved=resolved.resolved,
        kind_hint="dimension",
    )
    assert applicable == ()


def test_current_turn_scope_candidates_remain_discovery_until_fresh_binding_gate_edge():
    service, context = _context()
    schema = service.schema()
    diagnostics = []

    class ScopeSelectProvider(_RecordingProvider):
        def decide(self, requests):
            records = []
            choices = []
            for request in requests:
                visible = tuple(
                    self._id_to_canonical.get(item.candidate_id, item.label)
                    for item in request.candidates
                )
                records.append(
                    {
                        "surface": request.surface,
                        "request_id": request.request_id,
                        "visible": visible,
                    }
                )
                # Broad baseline abstains; narrowed governed scope may select.
                if (
                    request.surface == "bölümlerle"
                    and set(visible) == {"department_axis_d", "line_axis_p"}
                ):
                    selected = next(
                        item.candidate_id
                        for item in request.candidates
                        if self._id_to_canonical.get(item.candidate_id)
                        == "department_axis_d"
                    )
                    choices.append(
                        SemanticLinkChoice(
                            request_id=request.request_id,
                            decision="SELECT",
                            candidate_id=selected,
                        )
                    )
                else:
                    choices.append(
                        SemanticLinkChoice(
                            request_id=request.request_id,
                            decision="ABSTAIN",
                            reason="AMBIGUOUS",
                        )
                    )
            self.calls.append(tuple(records))
            return SemanticLinkBatchDecision(choices=tuple(choices))

    provider = ScopeSelectProvider(id_to_canonical=_catalog_index(context, schema))
    fx = _fixture(
        context=context,
        schema=schema,
        provider=provider,
        diagnostic_sink=diagnostics.append,
    )

    result, refs = _resolve(
        fx,
        text="Duruş süresi ana metriktir; bölümlerle governed ilişkiyi incele.",
        entries=(
            ("U_METRIC", "Duruş süresi", "metric"),
            ("U_REL", "bölümlerle", "dimension"),
        ),
        message_id="turn-d10-o-cross-owner-fresh-edge",
    )

    resolved = _resolved_canonicals(fx, result)
    assert resolved[("U_METRIC", refs[0])] == "downtime_min_d"
    assert resolved[("U_REL", refs[1])] == "department_axis_d"
    assert refs[0] != refs[1]

    recovery = next(
        item for item in diagnostics
        if item.get("owner_obligation_id") == "U_REL"
        and item.get("discovery_pass") == "current_turn_applicability"
    )
    assert recovery["selection"]["status"] == "BOUND"
    assert recovery["candidate_count"] == 2


# D10-V: one exact current-message source truth, multiple fresh owner authorities.

def _source_truth_context():
    context = BoundedSemanticContextV0(
        context_version=ContextVersionV0(
            version="ctx-source-truth",
            mdl_version="mdl-source-truth",
            compact_catalog_builder_version="d10-v",
            business_rules_hash="1" * 64,
            prompt_context_policy_version="d10-v",
        ),
        cubes=(
            CompactCubeContextV0(
                canonical_name="alpha_cube",
                measures=(
                    CompactSemanticFieldV0(
                        canonical_name="dual_metric_a",
                        display="Dual Concept",
                        synonyms=("Dual Concept",),
                    ),
                ),
                dimensions=(
                    CompactSemanticFieldV0(
                        canonical_name="shared_axis_a",
                        display="Shared Axis",
                        synonyms=("Shared Axis",),
                    ),
                    CompactSemanticFieldV0(
                        canonical_name="dual_dimension_a",
                        display="Dual Concept",
                        synonyms=("Dual Concept",),
                    ),
                ),
            ),
            CompactCubeContextV0(
                canonical_name="beta_cube",
                dimensions=(
                    CompactSemanticFieldV0(
                        canonical_name="shared_axis_b",
                        display="Shared Axis",
                        synonyms=("Shared Axis",),
                    ),
                ),
            ),
        ),
    )
    schema = {
        "models": [],
        "cubes": [
            {
                "name": "alpha_cube",
                "measures": ["dual_metric_a"],
                "measure_synonyms": {"dual_metric_a": ["Dual Concept"]},
                "dimensions": ["shared_axis_a", "dual_dimension_a"],
                "dimension_labels": {
                    "shared_axis_a": "Shared Axis",
                    "dual_dimension_a": "Dual Concept",
                },
                "dimension_synonyms": {
                    "shared_axis_a": ["Shared Axis"],
                    "dual_dimension_a": ["Dual Concept"],
                },
                "dimension_values": {},
            },
            {
                "name": "beta_cube",
                "measures": [],
                "dimensions": ["shared_axis_b"],
                "dimension_labels": {"shared_axis_b": "Shared Axis"},
                "dimension_synonyms": {"shared_axis_b": ["Shared Axis"]},
                "dimension_values": {},
            },
        ],
        "company_vocabulary": [],
    }
    return context, schema


class _DivergesIfAskedAgain:
    """Would choose a different canonical candidate on a second identical request."""

    def __init__(self):
        self.requests = []

    def decide(self, requests):
        choices = []
        for request in requests:
            self.requests.append(request)
            index = len(self.requests) - 1
            candidate = request.candidates[0 if index == 0 else -1]
            choices.append(
                SemanticLinkChoice(
                    request_id=request.request_id,
                    decision="SELECT",
                    candidate_id=candidate.candidate_id,
                )
            )
        return SemanticLinkBatchDecision(choices=tuple(choices))


class _SelectCandidate:
    def __init__(self, candidate_id: str):
        self.candidate_id = candidate_id
        self.calls = 0

    def decide(self, requests):
        self.calls += 1
        return SemanticLinkBatchDecision(
            choices=tuple(
                SemanticLinkChoice(
                    request_id=request.request_id,
                    decision="SELECT",
                    candidate_id=self.candidate_id,
                )
                for request in requests
            )
        )


def _source_truth_fixture(provider):
    context, schema = _source_truth_context()
    return _fixture(
        context=context,
        schema=schema,
        provider=provider,
    )


def test_source_truth_same_exact_source_two_owners_uses_one_cognition_and_fresh_edges():
    provider = _DivergesIfAskedAgain()
    fx = _source_truth_fixture(provider)

    result, refs = _resolve(
        fx,
        text="Shared Axis is the governed axis for both analyses.",
        entries=(
            ("U_BREAKDOWN", "Shared Axis", "dimension"),
            ("U_RELATIONSHIP", "Shared Axis", "dimension"),
        ),
        message_id="turn-source-truth-two-owner",
    )

    assert refs[0] == refs[1]
    assert len(provider.requests) == 1
    resolved = _resolved_canonicals(fx, result)
    assert resolved[("U_BREAKDOWN", refs[0])] == resolved[
        ("U_RELATIONSHIP", refs[1])
    ]
    handles = {item.owner_id: item.handle for item in result.resolved}
    assert handles["U_BREAKDOWN"].parent_obligation_id == "U_BREAKDOWN"
    assert handles["U_RELATIONSHIP"].parent_obligation_id == "U_RELATIONSHIP"
    assert handles["U_BREAKDOWN"].handle_id != handles["U_RELATIONSHIP"].handle_id


def test_source_truth_three_owners_share_truth_not_authority():
    provider = _DivergesIfAskedAgain()
    fx = _source_truth_fixture(provider)

    result, refs = _resolve(
        fx,
        text="Shared Axis drives performance breakdown and relationship analyses.",
        entries=(
            ("U_PERFORMANCE", "Shared Axis", "dimension"),
            ("U_BREAKDOWN", "Shared Axis", "dimension"),
            ("U_RELATIONSHIP", "Shared Axis", "dimension"),
        ),
        message_id="turn-source-truth-three-owner",
    )

    assert len(set(refs)) == 1
    assert len(provider.requests) == 1
    resolved = _resolved_canonicals(fx, result)
    assert len(set(resolved.values())) == 1
    assert {
        item.handle.parent_obligation_id for item in result.resolved
    } == {"U_PERFORMANCE", "U_BREAKDOWN", "U_RELATIONSHIP"}
    assert len({item.handle.handle_id for item in result.resolved}) == 3


def test_source_truth_owner_order_permutation_does_not_change_canonical_truth():
    outputs = []
    for owners in (
        ("U_BREAKDOWN", "U_RELATIONSHIP"),
        ("U_RELATIONSHIP", "U_BREAKDOWN"),
    ):
        provider = _DivergesIfAskedAgain()
        fx = _source_truth_fixture(provider)
        result, refs = _resolve(
            fx,
            text="Shared Axis is reused by both owner obligations.",
            entries=tuple((owner, "Shared Axis", "dimension") for owner in owners),
            message_id=f"turn-source-order-{owners[0]}",
        )
        outputs.append(
            {
                _resolved_canonicals(fx, result)[(owner, refs[index])]
                for index, owner in enumerate(owners)
            }
        )
        assert len(provider.requests) == 1
    assert outputs[0] == outputs[1]
    assert len(outputs[0]) == 1


def test_source_truth_same_label_different_source_refs_do_not_share_decision():
    provider = _DivergesIfAskedAgain()
    fx = _source_truth_fixture(provider)
    message_id = "turn-source-label-not-identity"
    text = "Shared Axis then Shared Axis."
    fx.spans.register_message(message_id=message_id, text=text)
    first = fx.spans.mint_exact(
        message_id=message_id, surface="Shared Axis", occurrence=0
    ).source_ref
    second = fx.spans.mint_exact(
        message_id=message_id, surface="Shared Axis", occurrence=1
    ).source_ref
    assert first != second

    result = fx.adapter.resolve(
        ResolveSemanticsArgs(
            provenance="USER_SOURCE",
            source_refs=(first, second),
            source_obligation_ids=("U1", "U2"),
            target_kind_hints=("dimension", "dimension"),
        )
    )

    assert len(provider.requests) == 2
    assert len(result.resolved) == 2


def test_source_truth_same_source_different_kind_does_not_share_decision():
    provider = _DivergesIfAskedAgain()
    fx = _source_truth_fixture(provider)

    result, refs = _resolve(
        fx,
        text="Dual Concept is intentionally typed two different ways.",
        entries=(
            ("U_METRIC", "Dual Concept", "metric"),
            ("U_DIMENSION", "Dual Concept", "dimension"),
        ),
        message_id="turn-source-kind-separation",
    )

    assert refs[0] == refs[1]
    assert len(result.resolved) == 2
    assert {item.handle.target_kind for item in result.resolved} == {
        "metric",
        "dimension",
    }
    assert len({item.handle.resolver_provenance_id for item in result.resolved}) == 2


def test_source_truth_narrowed_candidate_set_including_truth_reuses_without_cognition():
    provider = _DivergesIfAskedAgain()
    fx = _source_truth_fixture(provider)
    message_id = "turn-source-truth-narrow-include"
    text = "Shared Axis is the current source."
    fx.spans.register_message(message_id=message_id, text=text)
    source_ref = fx.spans.mint_exact(
        message_id=message_id, surface="Shared Axis"
    ).source_ref
    entries = [(source_ref, "Shared Axis", "dimension", "U1")]
    source_truth = {}

    broad, _ = fx.adapter._resolve_regular_once(
        entries=entries,
        args=ResolveSemanticsArgs(
            provenance="USER_SOURCE",
            source_refs=(source_ref,),
            source_obligation_ids=("U1",),
            target_kind_hints=("dimension",),
        ),
        source_truth_by_key=source_truth,
    )
    assert len(broad.resolved) == 1
    assert len(provider.requests) == 1
    canonical_id = broad.resolved[0].handle.resolver_provenance_id
    governed = fx.adapter._candidate_generator._governed_candidates("dimension")
    chosen = next(
        item for item in governed if item.card.candidate_id == canonical_id
    )
    forbidden = _ForbiddenProvider()
    narrowed = BoundedSemanticLinker(
        generator=GovernedCurrentTurnCandidateGenerator(bindings=(chosen,)),
        binding_gate=fx.adapter._binding_gate,
        provider=forbidden,
    )

    second, selections = fx.adapter._resolve_regular_once(
        entries=[(source_ref, "Shared Axis", "dimension", "U2")],
        args=ResolveSemanticsArgs(provenance="USER_SOURCE"),
        linker=narrowed,
        discovery_pass="test_narrowed_include",
        source_truth_by_key=source_truth,
    )

    assert selections[0].status == "BOUND"
    assert selections[0].reason == "SOURCE_TRUTH_REUSED"
    assert len(second.resolved) == 1
    assert forbidden.calls == 0
    assert second.resolved[0].handle.resolver_provenance_id == canonical_id
    assert second.resolved[0].handle.parent_obligation_id == "U2"


def test_source_truth_narrowed_candidate_set_excluding_truth_fails_closed_without_remap():
    provider = _DivergesIfAskedAgain()
    fx = _source_truth_fixture(provider)
    message_id = "turn-source-truth-narrow-exclude"
    text = "Shared Axis is the current source."
    fx.spans.register_message(message_id=message_id, text=text)
    source_ref = fx.spans.mint_exact(
        message_id=message_id, surface="Shared Axis"
    ).source_ref
    source_truth = {}

    broad, _ = fx.adapter._resolve_regular_once(
        entries=[(source_ref, "Shared Axis", "dimension", "U1")],
        args=ResolveSemanticsArgs(
            provenance="USER_SOURCE",
            source_refs=(source_ref,),
            source_obligation_ids=("U1",),
            target_kind_hints=("dimension",),
        ),
        source_truth_by_key=source_truth,
    )
    canonical_id = broad.resolved[0].handle.resolver_provenance_id
    governed = fx.adapter._candidate_generator._governed_candidates("dimension")
    other = next(
        item for item in governed
        if item.card.candidate_id != canonical_id
        and item.card.label == "Shared Axis"
    )
    forbidden = _ForbiddenProvider()
    narrowed = BoundedSemanticLinker(
        generator=GovernedCurrentTurnCandidateGenerator(bindings=(other,)),
        binding_gate=fx.adapter._binding_gate,
        provider=forbidden,
    )

    second, selections = fx.adapter._resolve_regular_once(
        entries=[(source_ref, "Shared Axis", "dimension", "U2")],
        args=ResolveSemanticsArgs(provenance="USER_SOURCE"),
        linker=narrowed,
        discovery_pass="test_narrowed_exclude",
        source_truth_by_key=source_truth,
    )

    assert selections[0].status == "SOURCE_TRUTH_CONTEXT_CONFLICT"
    assert second.resolved == ()
    assert second.unresolved_source_refs == (source_ref,)
    assert forbidden.calls == 0


def test_source_truth_candidate_order_permutation_keeps_selected_identity():
    context, schema = _source_truth_context()
    generator = SemanticCandidateGenerator(
        semantic_context=context,
        schema=schema,
    )
    candidates = tuple(
        item
        for item in generator._governed_candidates("dimension")
        if item.card.label == "Shared Axis"
    )
    assert len(candidates) == 2
    selected_id = min(item.card.candidate_id for item in candidates)

    outcomes = []
    for bindings in (candidates, tuple(reversed(candidates))):
        handles = SemanticHandleRegistry()
        provider = _SelectCandidate(selected_id)
        linker = BoundedSemanticLinker(
            generator=GovernedCurrentTurnCandidateGenerator(bindings=bindings),
            binding_gate=SemanticBindingGate(
                semantic_handles=handles,
                tenant_binding=TENANT,
                context_version=context.context_version.version,
            ),
            provider=provider,
        )
        selection = linker.resolve(
            (("source-order", "Shared Axis", "dimension"),),
            provenance_type="USER_SOURCE",
            decision_context="Shared Axis with immutable surrounding context",
        )[0]
        outcomes.append(selection.binding.card.candidate_id)
    assert outcomes == [selected_id, selected_id]
