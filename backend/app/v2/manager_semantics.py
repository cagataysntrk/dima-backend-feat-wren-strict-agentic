"""Governed semantic interpretation/binding adapter for the Day 6.5 bounded Manager.

USER_SOURCE proposals must reference runtime-issued src_* spans. AGENT_DERIVED proposals
must be tied to an accepted parent obligation and verified evidence by the executor.

Manager regular semantics do NOT use deterministic fuzzy/morphological language matching:
catalog candidate generation is deterministic, bounded candidate interpretation belongs
to BoundedSemanticLinker, and only SemanticBindingGate may mint sem_* authority.

Legacy SemanticResolver may remain for non-Manager compatibility paths, but this Manager semantic hot path has no import, constructor dependency, field, or fallback seam to it. Temporal normalization remains isolated in the typed temporal boundary.
"""

from __future__ import annotations

from typing import Any, Callable

from app.v2.manager_models import SemanticHandle
from app.v2.manager_tools import ResolveSemanticsArgs
from app.v2.models import (
    BoundedSemanticContextV0,
    ClarificationState,
    ConversationStateV2,
    FrozenModel,
    ResolvedPeriod,
)
from app.v2.semantic_linker import (
    BoundedSemanticLinker,
    GovernedCurrentTurnCandidateGenerator,
    GovernedSiblingScopeCandidateGenerator,
    CandidateSet,
    SemanticBindingGate,
    SemanticCandidateDecisionProvider,
    SemanticCandidateGenerator,
    SemanticDecompositionRepairProvider,
    SemanticDecompositionRepairRequest,
    SemanticRepairSourceCard,
)
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.source_spans import SourceSpanRegistry
from app.v2.temporal import TemporalResolutionError
from app.v2.temporal_intent import (
    TemporalBindingEngine,
    TemporalNormalizationProvider,
    TypedTemporalNormalizer,
)


class ManagerResolvedSemantic(FrozenModel):
    source_ref: str | None = None
    proposal_text: str | None = None
    owner_id: str | None = None
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
        source_spans: SourceSpanRegistry,
        semantic_handles: SemanticHandleRegistry,
        semantic_context: BoundedSemanticContextV0,
        conversation: ConversationStateV2,
        schema: dict,
        tenant_binding: str,
        session_id: str | None,
        thread_id: str | None,
        semantic_decision_provider: SemanticCandidateDecisionProvider | None = None,
        semantic_decomposition_repair_provider: SemanticDecompositionRepairProvider | None = None,
        temporal_normalization_provider: TemporalNormalizationProvider | None = None,
        semantic_diagnostic_sink: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        self._source_spans = source_spans
        self._handles = semantic_handles
        self._semantic_context = semantic_context
        self._conversation = conversation
        self._schema = schema
        self._tenant_binding = tenant_binding
        self._session_id = session_id
        self._thread_id = thread_id
        self._temporal_normalizer = TypedTemporalNormalizer(
            provider=temporal_normalization_provider,
        )
        self._temporal_engine = TemporalBindingEngine()
        self._candidate_generator = SemanticCandidateGenerator(
            semantic_context=semantic_context,
            schema=schema,
        )
        self._binding_gate = SemanticBindingGate(
            semantic_handles=semantic_handles,
            tenant_binding=tenant_binding,
            context_version=semantic_context.context_version.version,
        )
        self._semantic_decision_provider = semantic_decision_provider
        self._semantic_decomposition_repair_provider = semantic_decomposition_repair_provider
        self._semantic_diagnostic_sink = semantic_diagnostic_sink
        self._semantic_linker = BoundedSemanticLinker(
            generator=self._candidate_generator,
            binding_gate=self._binding_gate,
            provider=self._semantic_decision_provider,
            diagnostic_sink=self._semantic_diagnostic_sink,
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

    def _coherent_temporal_anchor(
        self,
        *,
        resolved: tuple[ManagerResolvedSemantic, ...],
        owner_id: str,
    ) -> str | None:
        """Choose an owner-local anchor only when its governed time dimension is coherent.

        The handle itself remains semantic authority. This helper only prevents one
        USER_MUST obligation from borrowing another obligation's semantic/time scope.
        """
        by_time_dimension: dict[str, list[str]] = {}
        for item in resolved:
            if item.owner_id != owner_id:
                continue
            if item.handle.target_kind not in {"metric", "kpi", "dimension"}:
                continue
            try:
                time_dimension = self._time_dimension(item.handle.handle_id)
            except (TemporalResolutionError, KeyError, ValueError):
                continue
            by_time_dimension.setdefault(time_dimension, []).append(
                item.handle.handle_id
            )

        if len(by_time_dimension) != 1:
            return None
        handles = next(iter(by_time_dimension.values()))
        return handles[0] if handles else None


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

    def _resolve_regular_once(
        self,
        *,
        entries: list[tuple[str | None, str, str, str | None]],
        args: ResolveSemanticsArgs,
        linker: BoundedSemanticLinker | None = None,
        discovery_pass: str = "pass1",
    ) -> tuple[ManagerSemanticResolutionResult, tuple]:
        active_linker = linker or self._semantic_linker
        requests = tuple(
            (
                f"link:{index}:{owner_id or 'ungrouped'}:{source_ref or 'derived'}",
                text,
                hint,
            )
            for index, (source_ref, text, hint, owner_id) in enumerate(entries)
        )
        diagnostic_metadata = {
            request_id: {
                "owner_obligation_id": owner_id,
                "source_ref": source_ref,
                "discovery_pass": discovery_pass,
            }
            for request_id, (source_ref, _, _, owner_id) in zip(
                (item[0] for item in requests),
                entries,
                strict=True,
            )
        }
        decision_context: str | None = None
        source_contexts = {
            self._source_spans.message_text_for(source_ref)
            for source_ref, _, _, _ in entries
            if source_ref is not None
        }
        if len(source_contexts) == 1:
            decision_context = next(iter(source_contexts))

        selections = active_linker.resolve(
            requests,
            provenance_type=args.provenance,
            decision_context=decision_context,
            parent_obligation_id=args.parent_obligation_id,
            trigger_evidence_ref=args.evidence_ref,
            diagnostic_metadata=diagnostic_metadata,
        )

        resolved: list[ManagerResolvedSemantic] = []
        unresolved_source_refs: list[str] = []
        unresolved_proposals: list[str] = []

        for (source_ref, proposal_text, _, owner_id), selection in zip(
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

            handle = active_linker.bind_selection(
                selection,
                provenance_type=args.provenance,
                parent_obligation_id=(
                    owner_id
                    if args.provenance == "USER_SOURCE" and owner_id is not None
                    else args.parent_obligation_id
                ),
                trigger_evidence_ref=args.evidence_ref,
            )
            resolved.append(
                ManagerResolvedSemantic(
                    source_ref=source_ref,
                    proposal_text=None if source_ref else proposal_text,
                    owner_id=owner_id,
                    provenance=args.provenance,
                    handle=handle,
                )
            )

        return (
            ManagerSemanticResolutionResult(
                resolved=tuple(resolved),
                unresolved_source_refs=tuple(dict.fromkeys(unresolved_source_refs)),
                unresolved_proposals=tuple(dict.fromkeys(unresolved_proposals)),
                clarification=None,
            ),
            tuple(selections),
        )

    def _resolve_regular(
        self,
        *,
        entries: list[tuple[str | None, str, str, str | None]],
        args: ResolveSemanticsArgs,
    ) -> ManagerSemanticResolutionResult:
        result, _ = self._resolve_regular_once(entries=entries, args=args)
        return result

    @staticmethod
    def _normalized_target_kind(kind: str) -> str:
        return {
            "kpi": "metric",
            "entity_value": "filter",
            "time": "period",
        }.get(kind, kind)

    def _current_turn_candidate_bindings(
        self,
        *,
        resolved: tuple[ManagerResolvedSemantic, ...] | list[ManagerResolvedSemantic],
        kind_hint: str,
    ) -> tuple:
        """Build bounded current-message applicability candidates.

        Existing USER_SOURCE bindings remain context only. Candidate construction may
        reuse their current governed cube metadata, but every unresolved source still
        requires a fresh linker decision and BindingGate admission.
        """
        if kind_hint not in {"metric", "dimension"}:
            return ()

        direct_candidate_ids: set[str] = set()
        cube_sets: list[frozenset[str]] = []
        for item in resolved:
            if item.source_ref is None or item.provenance != "USER_SOURCE":
                continue
            handle = item.handle
            if handle.sensitive:
                continue

            binding = self._handles.binding_for_execution(
                handle.handle_id,
                tenant_binding=self._tenant_binding,
                context_version=self._semantic_context.context_version.version,
            )
            cubes = frozenset(
                str(value)
                for value in tuple(
                    getattr(binding.canonical_target, "cube_names", ()) or ()
                )
                if str(value)
            )
            if cubes:
                cube_sets.append(cubes)

            if self._normalized_target_kind(handle.target_kind) == kind_hint:
                candidate_id = str(handle.resolver_provenance_id or "")
                if candidate_id.startswith("cand_"):
                    direct_candidate_ids.add(candidate_id)

        coherent_scope: set[str] = set()
        if cube_sets:
            coherent_scope = set(cube_sets[0])
            for cubes in cube_sets[1:]:
                coherent_scope.intersection_update(cubes)
                if not coherent_scope:
                    break

        out = []
        for item in self._candidate_generator._governed_candidates(kind_hint):
            if item.sensitive or not item.card.verified_aliases:
                continue
            candidate_cubes = {
                str(value)
                for value in tuple(
                    getattr(item.canonical_target, "cube_names", ()) or ()
                )
                if str(value)
            }
            if (
                item.card.candidate_id in direct_candidate_ids
                or bool(coherent_scope.intersection(candidate_cubes))
            ):
                out.append(item)

        out.sort(key=lambda item: item.card.candidate_id)
        return tuple(out)

    def _coherent_sibling_scope(
        self,
        *,
        resolved: tuple[ManagerResolvedSemantic, ...],
        owner_id: str,
    ) -> tuple[str, ...]:
        """Conservative same-obligation discovery scope from current governed handles."""
        cube_sets: list[frozenset[str]] = []
        for item in resolved:
            if item.owner_id != owner_id:
                continue
            if item.handle.target_kind not in {
                "metric",
                "kpi",
                "dimension",
                "entity_value",
            }:
                continue
            binding = self._handles.binding_for_execution(
                item.handle.handle_id,
                tenant_binding=self._tenant_binding,
                context_version=self._semantic_context.context_version.version,
            )
            cubes = frozenset(
                str(value)
                for value in tuple(
                    getattr(binding.canonical_target, "cube_names", ()) or ()
                )
                if str(value)
            )
            if cubes:
                cube_sets.append(cubes)

        if not cube_sets:
            return ()
        scope = set(cube_sets[0])
        for cubes in cube_sets[1:]:
            scope.intersection_update(cubes)
            if not scope:
                return ()
        return tuple(sorted(scope))


    def _governed_repair_source(
        self,
        *,
        source_ref: str,
        missing_kind: str,
        runtime,
        expected_message_hash: str,
    ):
        """Return one revalidated current governed source identity or None.

        Runtime receipt proves this exact current source crossed the normal semantic path.
        Current registry + catalog revalidation prevents stale handle/candidate reuse.
        """
        span = self._source_spans.validate(
            source_ref,
            expected_message_hash=expected_message_hash,
        )
        matches = []
        for receipt in runtime.semantic_resolution_receipts:
            if receipt.source_ref != source_ref:
                continue
            if self._normalized_target_kind(receipt.target_kind) != missing_kind:
                continue
            handle = self._handles.validate(
                receipt.handle_id,
                tenant_binding=self._tenant_binding,
                context_version=self._semantic_context.context_version.version,
            )
            if handle.provenance_type != "USER_SOURCE" or handle.sensitive:
                continue
            candidate_id = str(handle.resolver_provenance_id or "")
            if not candidate_id.startswith("cand_"):
                continue
            current = [
                item
                for item in self._candidate_generator._governed_candidates(missing_kind)
                if item.card.candidate_id == candidate_id
                and not item.sensitive
                and self._normalized_target_kind(item.card.target_kind) == missing_kind
            ]
            if len(current) == 1:
                matches.append((handle, current[0]))

        unique = {
            item.card.candidate_id: (handle, item)
            for handle, item in matches
        }
        if len(unique) != 1:
            return None
        handle, binding = next(iter(unique.values()))
        return span, handle, binding

    def _resolve_decomposition_repair(
        self,
        args: ResolveSemanticsArgs,
        runtime,
    ) -> ManagerSemanticResolutionResult:
        if runtime is None:
            raise ValueError("semantic decomposition repair requires ManagerRuntime")
        if self._semantic_decomposition_repair_provider is None:
            return ManagerSemanticResolutionResult()

        gap_spans = [
            self._source_spans.validate(ref)
            for gap in args.decomposition_repair_gaps
            for ref in gap.obligation_source_refs
        ]
        if not gap_spans:
            return ManagerSemanticResolutionResult()
        message_hashes = {item.message_hash for item in gap_spans}
        message_ids = {item.message_id for item in gap_spans}
        if len(message_hashes) != 1 or len(message_ids) != 1:
            raise ValueError("semantic repair gaps must belong to one current message")
        message_hash = next(iter(message_hashes))
        user_message = self._source_spans.message_text_for(
            args.decomposition_repair_gaps[0].obligation_source_refs[0]
        )

        source_refs = tuple(dict.fromkeys(args.decomposition_repair_source_refs))
        token_by_ref_kind: dict[tuple[str, str], str] = {}
        proof_by_token: dict[str, tuple[str, Any]] = {}
        next_token = 1

        requests: list[SemanticDecompositionRepairRequest] = []
        allowed_tokens_by_gap: dict[str, set[str]] = {}

        for gap in args.decomposition_repair_gaps:
            cards: list[SemanticRepairSourceCard] = []
            allowed: set[str] = set()
            for source_ref in source_refs:
                proof = self._governed_repair_source(
                    source_ref=source_ref,
                    missing_kind=gap.missing_kind,
                    runtime=runtime,
                    expected_message_hash=message_hash,
                )
                if proof is None:
                    continue
                span, _source_handle, binding = proof
                key = (source_ref, gap.missing_kind)
                token = token_by_ref_kind.get(key)
                if token is None:
                    token = f"s{next_token}"
                    next_token += 1
                    token_by_ref_kind[key] = token
                    proof_by_token[token] = (source_ref, binding)
                cards.append(
                    SemanticRepairSourceCard(
                        source_token=token,
                        surface=span.exact_surface,
                        kind=gap.missing_kind,
                        safe_label=binding.card.label,
                    )
                )
                allowed.add(token)

            if not cards:
                continue
            target_surfaces = tuple(
                self._source_spans.validate(
                    ref,
                    expected_message_hash=message_hash,
                ).exact_surface
                for ref in gap.obligation_source_refs
            )
            requests.append(
                SemanticDecompositionRepairRequest(
                    gap_ref=gap.gap_ref,
                    obligation_id=gap.obligation_id,
                    capability_key=gap.capability_key.value,
                    missing_kind=gap.missing_kind,
                    obligation_source_surfaces=target_surfaces,
                    available_user_source_concepts=tuple(cards),
                )
            )
            allowed_tokens_by_gap[gap.gap_ref] = allowed

        if not requests:
            return ManagerSemanticResolutionResult()

        decision = self._semantic_decomposition_repair_provider.decide(
            tuple(requests),
            user_message=user_message,
        )
        choices = {item.gap_ref: item for item in decision.choices}
        expected = {item.gap_ref for item in requests}
        if set(choices) != expected:
            raise ValueError(
                "semantic decomposition repair response gap refs do not match batch"
            )

        gap_by_ref = {
            gap.gap_ref: gap for gap in args.decomposition_repair_gaps
        }
        resolved: list[ManagerResolvedSemantic] = []
        diagnostic_choices: list[dict[str, Any]] = []

        for request in requests:
            choice = choices[request.gap_ref]
            selected = tuple(dict.fromkeys(choice.selected_source_tokens))
            if choice.decision == "ABSTAIN":
                selected = ()
            elif not set(selected).issubset(allowed_tokens_by_gap[request.gap_ref]):
                raise ValueError(
                    "semantic decomposition repair selected unknown/wrong-kind source token"
                )

            gap = gap_by_ref[request.gap_ref]
            diagnostic_choices.append(
                {
                    "gap_ref": request.gap_ref,
                    "obligation_id": request.obligation_id,
                    "missing_kind": request.missing_kind,
                    "available_source_tokens": [
                        item.source_token
                        for item in request.available_user_source_concepts
                    ],
                    "decision": choice.decision,
                    "selected_source_tokens": list(selected),
                    "reason": choice.reason,
                }
            )

            for token in selected:
                source_ref, binding = proof_by_token[token]
                candidate_set = CandidateSet(
                    request_id=f"repair:{request.gap_ref}:{token}",
                    surface=self._source_spans.validate(source_ref).exact_surface,
                    kind_hint=request.missing_kind,
                    bindings=(binding,),
                    too_broad=False,
                    retrieval_exhaustive=True,
                    retrieval_backend="governed_decomposition_source_reuse_v1",
                    retrieval_truncated=False,
                )
                handle = self._binding_gate.bind(
                    candidate_set=candidate_set,
                    candidate_id=binding.card.candidate_id,
                    provenance_type="USER_SOURCE",
                    parent_obligation_id=gap.obligation_id,
                )
                resolved.append(
                    ManagerResolvedSemantic(
                        source_ref=source_ref,
                        proposal_text=None,
                        owner_id=gap.obligation_id,
                        provenance="USER_SOURCE",
                        handle=handle,
                    )
                )

        if self._semantic_diagnostic_sink is not None:
            self._semantic_diagnostic_sink(
                {
                    "kind": "semantic_decomposition_repair",
                    "schema_name": "dima_semantic_decomposition_repair_v1",
                    "gap_count": len(requests),
                    "choices": diagnostic_choices,
                }
            )

        return ManagerSemanticResolutionResult(resolved=tuple(resolved))

    def resolve(self, args: ResolveSemanticsArgs, runtime=None) -> ManagerSemanticResolutionResult:
        if args.provenance == "USER_SOURCE" and args.decomposition_repair_gaps:
            return self._resolve_decomposition_repair(args, runtime)

        if args.provenance == "USER_SOURCE":
            spans = [
                self._source_spans.validate(source_ref)
                for source_ref in args.source_refs
            ]
            hints = (
                args.target_kind_hints
                or tuple("unknown" for _ in args.source_refs)
            )
            owners: tuple[str | None, ...] = (
                tuple(args.source_obligation_ids)
                if args.source_obligation_ids
                else tuple(None for _ in args.source_refs)
            )

            regular: list[tuple[str | None, str, str, str | None]] = []
            time_entries: list[tuple[str, str, str | None]] = []
            comparison_entries: list[tuple[str, str, str | None]] = []
            for source_ref, hint, owner_id, span in zip(
                args.source_refs,
                hints,
                owners,
                spans,
                strict=True,
            ):
                if hint == "time":
                    time_entries.append(
                        (source_ref, span.exact_surface, owner_id)
                    )
                elif hint == "comparison":
                    comparison_entries.append(
                        (source_ref, span.exact_surface, owner_id)
                    )
                else:
                    regular.append(
                        (source_ref, span.exact_surface, hint, owner_id)
                    )

            # Pass 1 is the existing bounded semantic path. It remains the owner whenever
            # it has candidates, ambiguity, linker abstention/unavailability, or a
            # globally exhaustive gap. Sibling-scope recovery is RETRIEVAL_MISS only.
            if regular:
                pass1_result, pass1_selections = self._resolve_regular_once(
                    entries=regular,
                    args=args,
                )
                recovered: list[ManagerResolvedSemantic] = list(
                    pass1_result.resolved
                )

                if args.source_obligation_ids:
                    misses_by_owner: dict[
                        str,
                        list[tuple[str | None, str, str, str | None]],
                    ] = {}
                    for entry, selection in zip(
                        regular,
                        pass1_selections,
                        strict=True,
                    ):
                        owner_id = entry[3]
                        if (
                            owner_id is not None
                            and selection.status == "RETRIEVAL_MISS"
                        ):
                            misses_by_owner.setdefault(owner_id, []).append(
                                entry
                            )

                    for owner_id, missed_entries in misses_by_owner.items():
                        scope = self._coherent_sibling_scope(
                            resolved=pass1_result.resolved,
                            owner_id=owner_id,
                        )
                        if not scope:
                            continue

                        scoped_linker = BoundedSemanticLinker(
                            generator=GovernedSiblingScopeCandidateGenerator(
                                base=self._candidate_generator,
                                sibling_cube_names=scope,
                            ),
                            binding_gate=self._binding_gate,
                            provider=self._semantic_decision_provider,
                            diagnostic_sink=self._semantic_diagnostic_sink,
                        )
                        fallback_result, _ = self._resolve_regular_once(
                            entries=missed_entries,
                            args=args,
                            linker=scoped_linker,
                            discovery_pass="same_owner_sibling_scope",
                        )
                        recovered.extend(fallback_result.resolved)

                # D10-N: if baseline discovery truly missed, a still-unresolved
                # metric/dimension may see already-governed USER_SOURCE truth from this
                # exact current batch as candidate applicability context. No handle is
                # copied across obligations; the existing linker + BindingGate must make
                # a fresh source->candidate admission.
                already_resolved = {
                    (item.owner_id, item.source_ref)
                    for item in recovered
                    if item.source_ref is not None
                }
                pass1_by_key = {
                    (entry[3], entry[0]): selection
                    for entry, selection in zip(
                        regular,
                        pass1_selections,
                        strict=True,
                    )
                }
                recovery_by_kind: dict[
                    str,
                    list[tuple[str | None, str, str, str | None]],
                ] = {}
                for entry in regular:
                    source_ref, _, kind_hint, owner_id = entry
                    if source_ref is None or (owner_id, source_ref) in already_resolved:
                        continue
                    selection = pass1_by_key.get((owner_id, source_ref))
                    if (
                        selection is None
                        or selection.status not in {"RETRIEVAL_MISS", "ABSTAIN"}
                        or kind_hint not in {"metric", "dimension"}
                    ):
                        continue
                    recovery_by_kind.setdefault(kind_hint, []).append(entry)

                for kind_hint, candidate_entries in recovery_by_kind.items():
                    current_turn_bindings = self._current_turn_candidate_bindings(
                        resolved=recovered,
                        kind_hint=kind_hint,
                    )
                    if not current_turn_bindings:
                        continue
                    current_candidate_ids = {
                        item.card.candidate_id for item in current_turn_bindings
                    }
                    missed_entries = [
                        entry
                        for entry in candidate_entries
                        if (
                            pass1_by_key[(entry[3], entry[0])].status
                            == "RETRIEVAL_MISS"
                            or set(
                                pass1_by_key[(entry[3], entry[0])].candidate_ids
                            )
                            != current_candidate_ids
                        )
                    ]
                    if not missed_entries:
                        # An ABSTAIN over the exact same bounded candidate set is final;
                        # repeating cognition would add cost without new information.
                        continue
                    current_turn_linker = BoundedSemanticLinker(
                        generator=GovernedCurrentTurnCandidateGenerator(
                            bindings=current_turn_bindings,
                        ),
                        binding_gate=self._binding_gate,
                        provider=self._semantic_decision_provider,
                        diagnostic_sink=self._semantic_diagnostic_sink,
                    )
                    current_turn_result, _ = self._resolve_regular_once(
                        entries=missed_entries,
                        args=args,
                        linker=current_turn_linker,
                        discovery_pass="current_turn_applicability",
                    )
                    recovered.extend(current_turn_result.resolved)

                resolved_keys = {
                    (item.owner_id, item.source_ref)
                    for item in recovered
                    if item.source_ref is not None
                }
                unresolved_regular_refs = tuple(
                    dict.fromkeys(
                        source_ref
                        for source_ref, _, _, owner_id in regular
                        if (
                            source_ref is not None
                            and (owner_id, source_ref) not in resolved_keys
                        )
                    )
                )
                regular_result = ManagerSemanticResolutionResult(
                    resolved=tuple(recovered),
                    unresolved_source_refs=unresolved_regular_refs,
                    unresolved_proposals=pass1_result.unresolved_proposals,
                    clarification=pass1_result.clarification,
                )
            else:
                regular_result = ManagerSemanticResolutionResult()

            resolved: list[ManagerResolvedSemantic] = list(
                regular_result.resolved
            )
            unresolved_refs: list[str] = list(
                regular_result.unresolved_source_refs
            )

            # Temporal normalization is typed cognition, but temporal authority must
            # remain obligation-local. Grouped USER_SOURCE batches may never borrow a
            # semantic anchor or explicit base period from another USER_MUST.
            grouped_temporal_owners = {
                owner_id
                for _, _, owner_id in (*time_entries, *comparison_entries)
                if owner_id is not None
            }
            grouped = bool(args.source_obligation_ids)

            global_anchor = args.temporal_anchor_handle
            if not grouped and global_anchor is None:
                anchored = [
                    item.handle.handle_id
                    for item in regular_result.resolved
                    if item.handle.target_kind
                    in {"metric", "kpi", "dimension"}
                ]
                if anchored:
                    global_anchor = anchored[0]

            def anchor_for(owner_id: str | None) -> str | None:
                if not grouped or owner_id is None:
                    return global_anchor
                local = self._coherent_temporal_anchor(
                    resolved=regular_result.resolved,
                    owner_id=owner_id,
                )
                if local is not None:
                    return local
                # Preserve an explicit caller-supplied anchor only when the batch has a
                # single owner; it cannot be safely attributed in a multi-owner batch.
                if len(grouped_temporal_owners) == 1:
                    return args.temporal_anchor_handle
                return None

            period_handles_by_owner: dict[str | None, list[str]] = {}
            for source_ref, text, owner_id in time_entries:
                temporal_args = args.model_copy(
                    update={"temporal_anchor_handle": anchor_for(owner_id)}
                )
                try:
                    handle = self._resolve_temporal(
                        text=text,
                        hint="time",
                        args=temporal_args,
                    )
                    period_handles_by_owner.setdefault(owner_id, []).append(
                        handle.handle_id
                    )
                    resolved.append(
                        ManagerResolvedSemantic(
                            source_ref=source_ref,
                            owner_id=owner_id,
                            provenance="USER_SOURCE",
                            handle=handle,
                        )
                    )
                except (TemporalResolutionError, KeyError, ValueError):
                    unresolved_refs.append(source_ref)

            for source_ref, text, owner_id in comparison_entries:
                local_periods = period_handles_by_owner.get(owner_id, [])
                effective_base = args.base_period_handle
                if grouped and owner_id is not None:
                    if len(local_periods) == 1:
                        effective_base = local_periods[0]
                    elif len(grouped_temporal_owners) != 1:
                        effective_base = None
                elif effective_base is None:
                    all_periods = [
                        handle_id
                        for values in period_handles_by_owner.values()
                        for handle_id in values
                    ]
                    if len(all_periods) == 1:
                        effective_base = all_periods[0]

                comparison_args = args.model_copy(
                    update={
                        "temporal_anchor_handle": anchor_for(owner_id),
                        "base_period_handle": effective_base,
                    }
                )
                try:
                    handle = self._resolve_temporal(
                        text=text,
                        hint="comparison",
                        args=comparison_args,
                    )
                    resolved.append(
                        ManagerResolvedSemantic(
                            source_ref=source_ref,
                            owner_id=owner_id,
                            provenance="USER_SOURCE",
                            handle=handle,
                        )
                    )
                except (TemporalResolutionError, KeyError, ValueError):
                    unresolved_refs.append(source_ref)

            return ManagerSemanticResolutionResult(
                resolved=tuple(resolved),
                unresolved_source_refs=tuple(
                    dict.fromkeys(unresolved_refs)
                ),
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
            entries=[(None, args.natural_language_proposal, hint, None)],
            args=args,
        )
