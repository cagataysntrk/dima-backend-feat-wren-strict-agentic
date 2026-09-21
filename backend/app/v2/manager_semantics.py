"""Governed semantic-resolution adapter for the Day 6.5 bounded Manager.

USER_SOURCE proposals must reference runtime-issued src_* spans. AGENT_DERIVED proposals
must be tied to an accepted parent obligation and verified evidence by the executor.
Existing SemanticResolver remains canonical entity/metric/dimension authority; temporal
normalization reuses the closed-family Day 3 temporal primitives.
"""

from __future__ import annotations

from app.v2.manager_models import SemanticHandle
from app.v2.manager_tools import ResolveSemanticsArgs
from app.v2.models import (
    AnalyticalRequest,
    BoundedSemanticContextV0,
    ClarificationState,
    ComparisonSurface,
    ConversationStateV2,
    FrozenModel,
    ResolvedComparison,
    ResolvedFilterRef,
    ResolvedPeriod,
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
from app.v2.temporal import TemporalResolutionError, resolve_comparison, resolve_period


class ManagerResolvedSemantic(FrozenModel):
    source_ref: str | None = None
    proposal_text: str | None = None
    provenance: str
    handle: SemanticHandle


class ManagerSemanticResolutionResult(FrozenModel):
    resolved: tuple[ManagerResolvedSemantic, ...] = ()
    unresolved_source_refs: tuple[str, ...] = ()
    unresolved_proposals: tuple[str, ...] = ()
    clarification: ClarificationState | None = None

    @property
    def clarification_required(self) -> bool:
        return (
            self.clarification is not None
            or bool(self.unresolved_source_refs)
            or bool(self.unresolved_proposals)
        )


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

    def _time_dimension(self, anchor_handle: str | None) -> str:
        cube_names: set[str] = set()
        if anchor_handle:
            binding = self._handles.binding_for_execution(
                anchor_handle,
                tenant_binding=self._tenant_binding,
                context_version=self._semantic_context.context_version.version,
            )
            target = binding.canonical_target
            cube_names.update(getattr(target, "cube_names", ()) or ())

        candidates: set[str] = set()
        for cube in self._semantic_context.cubes:
            if cube_names and cube.canonical_name not in cube_names:
                continue
            candidates.update(cube.time_dimensions)

        if len(candidates) != 1:
            raise TemporalResolutionError(
                "temporal resolution exactly one governed time dimension requires"
            )
        return next(iter(candidates))

    def _mint(
        self,
        *,
        target_kind: str,
        canonical_target,
        resolver_provenance_id: str,
        sensitive: bool,
        args: ResolveSemanticsArgs,
    ) -> SemanticHandle:
        return self._handles.mint_from_resolver(
            tenant_binding=self._tenant_binding,
            context_version=self._semantic_context.context_version.version,
            resolver_provenance_id=resolver_provenance_id,
            target_kind=target_kind,
            canonical_target=canonical_target,
            sensitive=sensitive,
            provenance_type=args.provenance,
            parent_obligation_id=args.parent_obligation_id,
            trigger_evidence_ref=args.evidence_ref,
        )

    def _resolve_temporal(
        self,
        *,
        text: str,
        hint: str,
        args: ResolveSemanticsArgs,
    ) -> SemanticHandle:
        time_dimension = self._time_dimension(args.temporal_anchor_handle)
        if hint == "time":
            period = resolve_period(
                (SemanticMention(text=text, kind=SemanticMentionKind.TIME),),
                time_dimension=time_dimension,
            )
            if period is None:
                raise TemporalResolutionError("time period could not be resolved")
            return self._mint(
                target_kind="period",
                canonical_target=period,
                resolver_provenance_id=f"temporal:{period.kind.value}:{period.start}:{period.end}",
                sensitive=False,
                args=args,
            )

        if hint == "comparison":
            base_period = None
            if args.base_period_handle:
                binding = self._handles.binding_for_execution(
                    args.base_period_handle,
                    tenant_binding=self._tenant_binding,
                    context_version=self._semantic_context.context_version.version,
                )
                if not isinstance(binding.canonical_target, ResolvedPeriod):
                    raise TemporalResolutionError("base_period_handle period target değil")
                base_period = binding.canonical_target
            comparison = resolve_comparison(
                (ComparisonSurface(text=text),),
                base_period=base_period,
                time_dimension=time_dimension,
            )
            if comparison is None:
                raise TemporalResolutionError("comparison could not be resolved")
            return self._mint(
                target_kind="comparison",
                canonical_target=comparison,
                resolver_provenance_id=(
                    f"comparison:{comparison.mode}:{comparison.base_period.start}:"
                    f"{comparison.reference_period.start}"
                ),
                sensitive=False,
                args=args,
            )

        raise TemporalResolutionError(f"unsupported temporal hint: {hint}")

    def _resolve_regular(
        self,
        *,
        entries: list[tuple[str | None, str, str]],
        args: ResolveSemanticsArgs,
    ) -> ManagerSemanticResolutionResult:
        metrics: list[SemanticMention] = []
        dimensions: list[SemanticMention] = []
        filters: list[SemanticMention] = []
        unresolved_mentions: list[UnresolvedMention] = []
        ordered: list[tuple[str | None, str, SemanticMention]] = []

        for source_ref, text, hint in entries:
            kind = self._KIND_MAP[hint]
            mention = SemanticMention(text=text, kind=kind)
            ordered.append((source_ref, text, mention))
            if kind == SemanticMentionKind.METRIC:
                metrics.append(mention)
            elif kind == SemanticMentionKind.DIMENSION:
                dimensions.append(mention)
            elif kind == SemanticMentionKind.FILTER:
                filters.append(mention)
            else:
                unresolved_mentions.append(
                    UnresolvedMention(
                        text=text,
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
            unresolved_mentions=tuple(unresolved_mentions),
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

        by_surface: dict[tuple[str, SemanticMentionKind], list[tuple[str | None, str]]] = {}
        for source_ref, text, mention in ordered:
            by_surface.setdefault((mention.text, mention.kind), []).append((source_ref, text))

        resolved: list[ManagerResolvedSemantic] = []
        unresolved_source_refs: list[str] = []
        unresolved_proposals: list[str] = []

        for hypothesis in bundle.hypotheses:
            slots = by_surface.get((hypothesis.source_mention, hypothesis.mention_kind)) or []
            slot = slots.pop(0) if slots else None
            if slot is None:
                continue
            source_ref, proposal_text = slot
            candidate = next(
                (
                    item
                    for item in hypothesis.candidates
                    if item.candidate_id == hypothesis.resolved_candidate_id
                ),
                None,
            )
            if candidate is None:
                if source_ref:
                    unresolved_source_refs.append(source_ref)
                else:
                    unresolved_proposals.append(proposal_text)
                continue

            if candidate.target_kind == SemanticTargetKind.ENTITY_VALUE:
                if not candidate.dimension_name or candidate.value is None:
                    if source_ref:
                        unresolved_source_refs.append(source_ref)
                    else:
                        unresolved_proposals.append(proposal_text)
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

            handle = self._mint(
                target_kind=candidate.target_kind.value,
                canonical_target=canonical_target,
                resolver_provenance_id=candidate.candidate_id,
                sensitive=candidate.sensitive,
                args=args,
            )
            resolved.append(
                ManagerResolvedSemantic(
                    source_ref=source_ref,
                    proposal_text=None if source_ref else proposal_text,
                    provenance=args.provenance,
                    handle=handle,
                )
            )

        resolved_user_refs = {item.source_ref for item in resolved if item.source_ref}
        for source_ref, _, _ in ordered:
            if source_ref and source_ref not in resolved_user_refs and source_ref not in unresolved_source_refs:
                unresolved_source_refs.append(source_ref)

        if args.provenance == "AGENT_DERIVED" and not resolved and args.natural_language_proposal:
            if args.natural_language_proposal not in unresolved_proposals:
                unresolved_proposals.append(args.natural_language_proposal)

        return ManagerSemanticResolutionResult(
            resolved=tuple(resolved),
            unresolved_source_refs=tuple(dict.fromkeys(unresolved_source_refs)),
            unresolved_proposals=tuple(dict.fromkeys(unresolved_proposals)),
            clarification=bundle.clarification,
        )

    def resolve(self, args: ResolveSemanticsArgs, runtime=None) -> ManagerSemanticResolutionResult:
        del runtime  # provenance authority is validated by GovernedManagerExecutor.

        if args.provenance == "USER_SOURCE":
            spans = [self._source_spans.validate(source_ref) for source_ref in args.source_refs]
            hints = args.target_kind_hints or tuple("unknown" for _ in args.source_refs)

            regular: list[tuple[str | None, str, str]] = []
            time_entries: list[tuple[str, str]] = []
            comparison_entries: list[tuple[str, str]] = []
            for source_ref, hint, span in zip(args.source_refs, hints, spans, strict=True):
                if hint == "time":
                    time_entries.append((source_ref, span.exact_surface))
                elif hint == "comparison":
                    comparison_entries.append((source_ref, span.exact_surface))
                else:
                    regular.append((source_ref, span.exact_surface, hint))

            # Resolve tenant semantics first. A metric/dimension handle from this SAME
            # governed call may safely anchor temporal normalization, avoiding an
            # unnecessary extra Manager round-trip.
            regular_result = (
                self._resolve_regular(entries=regular, args=args)
                if regular
                else ManagerSemanticResolutionResult()
            )
            resolved: list[ManagerResolvedSemantic] = list(regular_result.resolved)
            unresolved_refs: list[str] = list(regular_result.unresolved_source_refs)

            effective_anchor = args.temporal_anchor_handle
            if effective_anchor is None:
                anchored = [
                    item.handle.handle_id
                    for item in regular_result.resolved
                    if item.handle.target_kind in {"metric", "kpi", "dimension"}
                ]
                if anchored:
                    effective_anchor = anchored[0]

            temporal_args = args.model_copy(
                update={"temporal_anchor_handle": effective_anchor}
            )

            period_handles: list[str] = []
            for source_ref, text in time_entries:
                try:
                    handle = self._resolve_temporal(
                        text=text,
                        hint="time",
                        args=temporal_args,
                    )
                    period_handles.append(handle.handle_id)
                    resolved.append(
                        ManagerResolvedSemantic(
                            source_ref=source_ref,
                            provenance="USER_SOURCE",
                            handle=handle,
                        )
                    )
                except (TemporalResolutionError, KeyError, ValueError):
                    unresolved_refs.append(source_ref)

            effective_base = args.base_period_handle
            if effective_base is None and len(period_handles) == 1:
                effective_base = period_handles[0]
            comparison_args = temporal_args.model_copy(
                update={"base_period_handle": effective_base}
            )
            for source_ref, text in comparison_entries:
                try:
                    handle = self._resolve_temporal(
                        text=text,
                        hint="comparison",
                        args=comparison_args,
                    )
                    resolved.append(
                        ManagerResolvedSemantic(
                            source_ref=source_ref,
                            provenance="USER_SOURCE",
                            handle=handle,
                        )
                    )
                except (TemporalResolutionError, KeyError, ValueError):
                    unresolved_refs.append(source_ref)

            return ManagerSemanticResolutionResult(
                resolved=tuple(resolved),
                unresolved_source_refs=tuple(dict.fromkeys(unresolved_refs)),
                unresolved_proposals=regular_result.unresolved_proposals,
                clarification=regular_result.clarification,
            )

        assert args.natural_language_proposal is not None
        hint = args.target_kind_hints[0]
        if hint in {"time", "comparison"}:
            try:
                handle = self._resolve_temporal(
                    text=args.natural_language_proposal,
                    hint=hint,
                    args=args,
                )
                return ManagerSemanticResolutionResult(
                    resolved=(
                        ManagerResolvedSemantic(
                            proposal_text=args.natural_language_proposal,
                            provenance="AGENT_DERIVED",
                            handle=handle,
                        ),
                    ),
                )
            except (TemporalResolutionError, KeyError, ValueError):
                return ManagerSemanticResolutionResult(
                    unresolved_proposals=(args.natural_language_proposal,)
                )

        return self._resolve_regular(
            entries=[(None, args.natural_language_proposal, hint)],
            args=args,
        )
