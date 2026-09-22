"""Governed semantic interpretation/binding adapter for the Day 6.5 bounded Manager.

USER_SOURCE proposals must reference runtime-issued src_* spans. AGENT_DERIVED proposals
must be tied to an accepted parent obligation and verified evidence by the executor.

Manager regular semantics do NOT use deterministic fuzzy/morphological language matching:
catalog candidate generation is deterministic, bounded candidate interpretation belongs
to BoundedSemanticLinker, and only SemanticBindingGate may mint sem_* authority.

Legacy SemanticResolver remains available to non-Manager V2 paths. Temporal normalization
is still isolated here and is migrated separately to typed temporal intent.
"""

from __future__ import annotations

from app.v2.manager_models import SemanticHandle
from app.v2.manager_tools import ResolveSemanticsArgs
from app.v2.models import (
    BoundedSemanticContextV0,
    ClarificationState,
    ConversationStateV2,
    FrozenModel,
    ResolvedPeriod,
)
from app.v2.resolver import SemanticResolver
from app.v2.semantic_linker import (
    BoundedSemanticLinker,
    SemanticBindingGate,
    SemanticCandidateGenerator,
)
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry
from app.v2.temporal import TemporalResolutionError
from app.v2.temporal_intent import (
    TemporalBindingEngine,
    TypedTemporalNormalizer,
)


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
    def __init__(
        self,
        *,
        resolver: SemanticResolver | None = None,
        source_spans: SourceSpanRegistry,
        semantic_handles: SemanticHandleRegistry,
        semantic_context: BoundedSemanticContextV0,
        conversation: ConversationStateV2,
        schema: dict,
        tenant_binding: str,
        session_id: str | None,
        thread_id: str | None,
        semantic_linker_structured=None,
    ) -> None:
        self._legacy_resolver = resolver
        self._source_spans = source_spans
        self._handles = semantic_handles
        self._semantic_context = semantic_context
        self._conversation = conversation
        self._schema = schema
        self._tenant_binding = tenant_binding
        self._session_id = session_id
        self._thread_id = thread_id
        self._temporal_normalizer = TypedTemporalNormalizer(
            structured=semantic_linker_structured,
        )
        self._temporal_engine = TemporalBindingEngine()
        self._semantic_linker = BoundedSemanticLinker(
            generator=SemanticCandidateGenerator(
                semantic_context=semantic_context,
                schema=schema,
            ),
            binding_gate=SemanticBindingGate(
                semantic_handles=semantic_handles,
                tenant_binding=tenant_binding,
                context_version=semantic_context.context_version.version,
            ),
            structured=semantic_linker_structured,
        )

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

    def _mint_temporal(
        self,
        *,
        target_kind: str,
        canonical_target,
        temporal_provenance_id: str,
        args: ResolveSemanticsArgs,
    ) -> SemanticHandle:
        return self._handles.mint_from_temporal_engine(
            tenant_binding=self._tenant_binding,
            context_version=self._semantic_context.context_version.version,
            temporal_provenance_id=temporal_provenance_id,
            target_kind=target_kind,
            canonical_target=canonical_target,
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
        target = "PERIOD" if hint == "time" else "COMPARISON"
        choice = self._temporal_normalizer.normalize(
            (("temporal:0", text, target),)
        )[0]
        if choice.decision != "NORMALIZED":
            raise TemporalResolutionError(
                f"typed temporal normalizer abstained: {choice.reason}"
            )

        if hint == "time":
            period = self._temporal_engine.period(
                choice=choice,
                source_text=text,
                time_dimension=time_dimension,
            )
            return self._mint_temporal(
                target_kind="period",
                canonical_target=period,
                temporal_provenance_id=(
                    f"typed-period:{choice.period_kind}:{choice.n or ''}:"
                    f"{period.start}:{period.end or ''}"
                ),
                args=args,
            )

        if hint == "comparison":
            if args.base_period_handle:
                binding = self._handles.binding_for_execution(
                    args.base_period_handle,
                    tenant_binding=self._tenant_binding,
                    context_version=self._semantic_context.context_version.version,
                )
                if not isinstance(binding.canonical_target, ResolvedPeriod):
                    raise TemporalResolutionError("base_period_handle period target değil")
                base_period = binding.canonical_target
            elif choice.implicit_base_period_kind is not None:
                try:
                    base_period = self._temporal_engine.implicit_base_period(
                        choice=choice,
                        source_text=text,
                        time_dimension=time_dimension,
                    )
                except ValueError as exc:
                    raise TemporalResolutionError(str(exc)) from exc
            else:
                raise TemporalResolutionError(
                    "comparison requires governed or typed implicit base period"
                )

            comparison = self._temporal_engine.comparison(
                choice=choice,
                source_text=text,
                time_dimension=time_dimension,
                base_period=base_period,
            )
            return self._mint_temporal(
                target_kind="comparison",
                canonical_target=comparison,
                temporal_provenance_id=(
                    f"typed-comparison:{choice.comparison_kind}:"
                    f"{choice.implicit_base_period_kind or 'explicit-base'}:"
                    f"{choice.implicit_base_n or ''}:"
                    f"{comparison.base_period.start}:"
                    f"{comparison.reference_period.start}"
                ),
                args=args,
            )

        raise TemporalResolutionError(f"unsupported temporal hint: {hint}")

    def _resolve_regular(
        self,
        *,
        entries: list[tuple[str | None, str, str]],
        args: ResolveSemanticsArgs,
    ) -> ManagerSemanticResolutionResult:
        requests = tuple(
            (
                f"link:{index}:{source_ref or 'derived'}",
                text,
                hint,
            )
            for index, (source_ref, text, hint) in enumerate(entries)
        )
        selections = self._semantic_linker.resolve(
            requests,
            provenance_type=args.provenance,
            parent_obligation_id=args.parent_obligation_id,
            trigger_evidence_ref=args.evidence_ref,
        )

        resolved: list[ManagerResolvedSemantic] = []
        unresolved_source_refs: list[str] = []
        unresolved_proposals: list[str] = []

        for (source_ref, proposal_text, _), selection in zip(
            entries,
            selections,
            strict=True,
        ):
            if selection.status != "BOUND":
                if source_ref:
                    unresolved_source_refs.append(source_ref)
                else:
                    unresolved_proposals.append(proposal_text)
                continue

            handle = self._semantic_linker.bind_selection(
                selection,
                provenance_type=args.provenance,
                parent_obligation_id=args.parent_obligation_id,
                trigger_evidence_ref=args.evidence_ref,
            )
            resolved.append(
                ManagerResolvedSemantic(
                    source_ref=source_ref,
                    proposal_text=None if source_ref else proposal_text,
                    provenance=args.provenance,
                    handle=handle,
                )
            )

        return ManagerSemanticResolutionResult(
            resolved=tuple(resolved),
            unresolved_source_refs=tuple(dict.fromkeys(unresolved_source_refs)),
            unresolved_proposals=tuple(dict.fromkeys(unresolved_proposals)),
            clarification=None,
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
