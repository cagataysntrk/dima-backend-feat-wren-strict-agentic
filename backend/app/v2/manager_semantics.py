"""Semantic-resolution adapter for the Day 6.5 bounded Manager.

Manager supplies only runtime-issued src_* references and optional coarse kind hints.
Existing SemanticResolver remains canonical binding authority and returns sem_* handles;
canonical identifiers never enter Manager-facing contracts.
"""

from __future__ import annotations

from app.v2.manager_models import SemanticHandle
from app.v2.manager_tools import ResolveSemanticsArgs
from app.v2.models import (
    AnalyticalRequest,
    BoundedSemanticContextV0,
    ClarificationState,
    ConversationStateV2,
    FrozenModel,
    ResolvedFilterRef,
    ResolvedSemanticRef,
    SemanticMention,
    SemanticMentionKind,
    SemanticTargetKind,
    TurnAct,
    TurnInterpretation,
    UnresolvedMention,
)
from app.v2.resolver import SemanticResolver
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry


class ManagerResolvedSemantic(FrozenModel):
    source_ref: str
    handle: SemanticHandle


class ManagerSemanticResolutionResult(FrozenModel):
    resolved: tuple[ManagerResolvedSemantic, ...] = ()
    unresolved_source_refs: tuple[str, ...] = ()
    clarification: ClarificationState | None = None

    @property
    def clarification_required(self) -> bool:
        return self.clarification is not None or bool(self.unresolved_source_refs)


class ManagerSemanticResolutionAdapter:
    _KIND_MAP = {
        "metric": SemanticMentionKind.METRIC,
        "dimension": SemanticMentionKind.DIMENSION,
        "filter": SemanticMentionKind.FILTER,
        "unknown": SemanticMentionKind.UNKNOWN,
    }

    def __init__(
        self,
        *,
        resolver: SemanticResolver,
        source_spans: SourceSpanRegistry,
        semantic_handles: SemanticHandleRegistry,
        semantic_context: BoundedSemanticContextV0,
        conversation: ConversationStateV2,
        schema: dict,
        tenant_binding: str,
        session_id: str | None,
        thread_id: str | None,
    ) -> None:
        self._resolver = resolver
        self._source_spans = source_spans
        self._handles = semantic_handles
        self._semantic_context = semantic_context
        self._conversation = conversation
        self._schema = schema
        self._tenant_binding = tenant_binding
        self._session_id = session_id
        self._thread_id = thread_id

    def resolve(self, args: ResolveSemanticsArgs, runtime=None) -> ManagerSemanticResolutionResult:
        del runtime  # protocol compatibility; semantic authority does not depend on Manager state.

        hints = args.target_kind_hints or tuple("unknown" for _ in args.source_refs)
        spans = [self._source_spans.validate(source_ref) for source_ref in args.source_refs]

        metrics: list[SemanticMention] = []
        dimensions: list[SemanticMention] = []
        filters: list[SemanticMention] = []
        unresolved: list[UnresolvedMention] = []
        ordered_refs: list[tuple[str, SemanticMention]] = []

        for source_ref, hint, span in zip(args.source_refs, hints, spans, strict=True):
            kind = self._KIND_MAP[hint]
            mention = SemanticMention(text=span.exact_surface, kind=kind)
            ordered_refs.append((source_ref, mention))
            if kind == SemanticMentionKind.METRIC:
                metrics.append(mention)
            elif kind == SemanticMentionKind.DIMENSION:
                dimensions.append(mention)
            elif kind == SemanticMentionKind.FILTER:
                filters.append(mention)
            else:
                unresolved.append(
                    UnresolvedMention(
                        text=span.exact_surface,
                        reason="Manager requested semantic resolution without a trusted kind hint",
                    )
                )

        turn = TurnInterpretation(
            dialogue_act=TurnAct.ANALYTIC_NEW,
            analytical_request=AnalyticalRequest(
                metric_mentions=tuple(metrics),
                dimension_mentions=tuple(dimensions),
                filter_mentions=tuple(filters),
            ),
            unresolved_mentions=tuple(unresolved),
        )
        bundle = self._resolver.resolve_turn(
            turn=turn,
            schema=self._schema,
            semantic_context=self._semantic_context,
            conversation=self._conversation,
            tenant_binding=self._tenant_binding,
            session_id=self._session_id,
            thread_id=self._thread_id,
        )

        by_surface: dict[tuple[str, SemanticMentionKind], list[str]] = {}
        for source_ref, mention in ordered_refs:
            by_surface.setdefault((mention.text, mention.kind), []).append(source_ref)

        resolved: list[ManagerResolvedSemantic] = []
        unresolved_refs: list[str] = []

        for hypothesis in bundle.hypotheses:
            key = (hypothesis.source_mention, hypothesis.mention_kind)
            refs = by_surface.get(key) or []
            source_ref = refs.pop(0) if refs else None
            if source_ref is None:
                continue

            candidate = next(
                (
                    item
                    for item in hypothesis.candidates
                    if item.candidate_id == hypothesis.resolved_candidate_id
                ),
                None,
            )
            if candidate is None:
                unresolved_refs.append(source_ref)
                continue

            if candidate.target_kind == SemanticTargetKind.ENTITY_VALUE:
                if not candidate.dimension_name or candidate.value is None:
                    unresolved_refs.append(source_ref)
                    continue
                canonical_target = ResolvedFilterRef(
                    candidate_id=candidate.candidate_id,
                    dimension_name=candidate.dimension_name,
                    value=candidate.value,
                    cube_names=candidate.cube_names,
                    sensitive=candidate.sensitive,
                )
            else:
                canonical_target = ResolvedSemanticRef(
                    candidate_id=candidate.candidate_id,
                    target_kind=candidate.target_kind,
                    canonical_name=candidate.canonical_name,
                    cube_names=candidate.cube_names,
                )

            handle = self._handles.mint_from_resolver(
                tenant_binding=self._tenant_binding,
                context_version=self._semantic_context.context_version.version,
                resolver_provenance_id=candidate.candidate_id,
                target_kind=candidate.target_kind.value,
                canonical_target=canonical_target,
                sensitive=candidate.sensitive,
            )
            resolved.append(ManagerResolvedSemantic(source_ref=source_ref, handle=handle))

        for source_ref, _ in ordered_refs:
            if source_ref not in {item.source_ref for item in resolved} and source_ref not in unresolved_refs:
                unresolved_refs.append(source_ref)

        return ManagerSemanticResolutionResult(
            resolved=tuple(resolved),
            unresolved_source_refs=tuple(dict.fromkeys(unresolved_refs)),
            clarification=bundle.clarification,
        )
