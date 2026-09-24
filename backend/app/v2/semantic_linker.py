"""Bounded semantic linker for Day 6.5 cognition/authority separation.

The catalog says what semantic concepts exist. A bounded LLM may interpret which opaque
catalog candidate a user surface refers to. Only SemanticBindingGate may turn that
selection into execution authority.

No regex, morphology score, fuzzy ratio, SQL, or raw database identifier selection lives
here.
"""

from __future__ import annotations

import copy
import hashlib
import json
import unicodedata
from dataclasses import dataclass, replace
from typing import Any, Callable, Literal, Protocol

from pydantic import Field, model_validator

from app.sensitivity import classify
from app.v2.manager_models import SemanticHandle
from app.v2.models import (
    BoundedSemanticContextV0,
    FrozenModel,
    ResolvedFilterRef,
    ResolvedSemanticRef,
    SemanticTargetKind,
)
from app.v2.semantic_handles import SemanticHandleRegistry
from app.v2.semantic_retriever import (
    IndexedTokenSemanticCatalogRetriever,
    SemanticCatalogRetriever,
    SemanticDiscoveryDocument,
    SemanticRetrievalContractError,
)


def _exact_key(value: str) -> str:
    """Conservative identity normalization, not natural-language interpretation."""
    normalized = unicodedata.normalize("NFKD", str(value or "").strip().casefold())
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return " ".join(normalized.split())


def _strict_schema(schema: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(schema)

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            node.pop("default", None)
            if node.get("type") == "object" or "properties" in node:
                properties = node.get("properties") or {}
                node["required"] = list(properties.keys())
                node["additionalProperties"] = False
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(out)
    return out


class SemanticLinkCandidateCard(FrozenModel):
    candidate_id: str = Field(pattern=r"^cand_[a-f0-9]{24}$")
    target_kind: Literal["metric", "kpi", "dimension", "entity_value"]
    label: str = Field(min_length=1, max_length=240)
    verified_aliases: tuple[str, ...] = ()
    cube_labels: tuple[str, ...] = ()


class SemanticLinkRequestCard(FrozenModel):
    request_id: str = Field(min_length=1)
    surface: str = Field(min_length=1, max_length=240)
    source_context: str | None = Field(
        default=None,
        max_length=4000,
        description=(
            "Immutable current-message evidence supplied by runtime. It may disambiguate "
            "only among supplied candidates; it is not semantic authority."
        ),
    )
    kind_hint: Literal["metric", "dimension", "filter", "unknown"]
    candidates: tuple[SemanticLinkCandidateCard, ...] = Field(min_length=1)


class SemanticLinkChoice(FrozenModel):
    request_id: str = Field(min_length=1)
    decision: Literal["SELECT", "ABSTAIN"]
    candidate_id: str | None = None
    reason: Literal[
        "AMBIGUOUS",
        "NO_MATCH",
        "INSUFFICIENT_CONTEXT",
    ] | None = None

    @model_validator(mode="after")
    def _shape(self):
        if self.decision == "SELECT":
            if not self.candidate_id or self.reason is not None:
                raise ValueError("SELECT requires candidate_id and no abstain reason")
        else:
            if self.candidate_id is not None or self.reason is None:
                raise ValueError("ABSTAIN requires reason and no candidate_id")
        return self


class SemanticLinkBatchDecision(FrozenModel):
    choices: tuple[SemanticLinkChoice, ...] = Field(min_length=1)


@dataclass(frozen=True)
class CatalogCandidateBinding:
    card: SemanticLinkCandidateCard
    canonical_target: ResolvedSemanticRef | ResolvedFilterRef
    exact_keys: frozenset[str]
    discovery_context: tuple[str, ...] = ()
    sensitive: bool = False


@dataclass(frozen=True)
class CandidateSet:
    request_id: str
    surface: str
    kind_hint: str
    bindings: tuple[CatalogCandidateBinding, ...]
    too_broad: bool = False
    retrieval_exhaustive: bool = True
    retrieval_backend: str = "deterministic_enumeration_v1"
    retrieval_truncated: bool = False

    @property
    def cards(self) -> tuple[SemanticLinkCandidateCard, ...]:
        return tuple(item.card for item in self.bindings)

    def binding(self, candidate_id: str) -> CatalogCandidateBinding | None:
        return next(
            (item for item in self.bindings if item.card.candidate_id == candidate_id),
            None,
        )


@dataclass(frozen=True)
class BoundedSemanticSelection:
    request_id: str
    surface: str
    status: Literal[
        "BOUND",
        "ABSTAIN",
        "GAP",
        "AMBIGUOUS_EXACT",
        "CANDIDATE_SET_TOO_BROAD",
        "RETRIEVAL_MISS",
        "LINKER_UNAVAILABLE",
    ]
    binding: CatalogCandidateBinding | None = None
    mode: Literal["EXACT", "LINKER", "NONE"] = "NONE"
    reason: str | None = None
    # Discovery receipt only. This is not authority and is used solely to avoid
    # repeating cognition when a recovery stage would expose the same candidate set.
    candidate_ids: tuple[str, ...] = ()


class SemanticLinkAuthorityError(RuntimeError):
    pass


class SemanticCandidateGenerator:
    """Enumerate bounded verified catalog cards without interpreting the user surface."""

    def __init__(
        self,
        *,
        semantic_context: BoundedSemanticContextV0,
        schema: dict,
        max_candidates: int = 48,
        retriever: SemanticCatalogRetriever[CatalogCandidateBinding] | None = None,
    ) -> None:
        self._context = semantic_context
        self._schema = schema
        self._max_candidates = max(4, int(max_candidates))
        self._company_aliases = self._verified_company_aliases()
        self._governed_cache: dict[str, tuple[CatalogCandidateBinding, ...]] = {}
        self._retriever = retriever or IndexedTokenSemanticCatalogRetriever(
            enumerate_candidates=self._governed_candidates,
            document_for=self._discovery_document,
        )

    def _governed_candidates(
        self,
        kind_hint: str,
    ) -> tuple[CatalogCandidateBinding, ...]:
        cached = self._governed_cache.get(kind_hint)
        if cached is None:
            cached = tuple(self._semantic_fields(kind_hint=kind_hint))
            self._governed_cache[kind_hint] = cached
        return cached

    @staticmethod
    def _discovery_document(
        item: CatalogCandidateBinding,
    ) -> SemanticDiscoveryDocument:
        target = item.canonical_target
        canonical = getattr(target, "canonical_name", None)
        if canonical is None:
            canonical = getattr(target, "dimension_name", None)
        primary = tuple(
            dict.fromkeys(
                value
                for value in (
                    canonical,
                    item.card.label,
                    *item.card.verified_aliases,
                )
                if value
            )
        )
        return SemanticDiscoveryDocument(
            stable_id=item.card.candidate_id,
            exact_terms=tuple(item.exact_keys),
            primary_terms=primary,
            context_terms=item.discovery_context,
            discoverable=not item.sensitive,
        )

    def _verified_company_aliases(self) -> dict[tuple[str, str], tuple[str, ...]]:
        out: dict[tuple[str, str], list[str]] = {}
        for item in self._schema.get("company_vocabulary") or ():
            if not isinstance(item, dict) or item.get("verified") is not True:
                continue
            kind = str(item.get("target_kind") or "")
            canonical = str(item.get("canonical_name") or "")
            surface = str(item.get("surface") or "").strip()
            if kind and canonical and surface:
                out.setdefault((kind, canonical), []).append(surface)
        return {
            key: tuple(dict.fromkeys(values))
            for key, values in out.items()
        }

    @staticmethod
    def _candidate_id(
        *,
        context_version: str,
        target_kind: str,
        canonical_name: str,
        dimension_name: str | None = None,
        value: str | None = None,
        cube_names: tuple[str, ...] = (),
    ) -> str:
        payload = json.dumps(
            {
                "context": context_version,
                "kind": target_kind,
                "canonical": canonical_name,
                "dimension": dimension_name,
                "value": value,
                "cubes": list(cube_names),
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return "cand_" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]

    @staticmethod
    def _human_aliases(
        *,
        display: str | None,
        synonyms: tuple[str, ...],
        extra: tuple[str, ...] = (),
    ) -> tuple[str, ...]:
        values = [
            str(value).strip()
            for value in (display or "", *synonyms, *extra)
            if str(value).strip()
        ]
        return tuple(dict.fromkeys(values))

    def _semantic_fields(
        self,
        *,
        kind_hint: str,
    ) -> list[CatalogCandidateBinding]:
        context_version = self._context.context_version.version
        out: list[CatalogCandidateBinding] = []

        if kind_hint in {"metric", "unknown"}:
            for cube in self._context.cubes:
                cube_label = cube.display or cube.canonical_name
                for field in cube.measures:
                    extra = self._company_aliases.get(
                        ("metric", field.canonical_name),
                        (),
                    )
                    aliases = self._human_aliases(
                        display=field.display,
                        synonyms=field.synonyms,
                        extra=extra,
                    )
                    candidate_id = self._candidate_id(
                        context_version=context_version,
                        target_kind="metric",
                        canonical_name=field.canonical_name,
                        cube_names=(cube.canonical_name,),
                    )
                    label = field.display or (aliases[0] if aliases else "metric candidate")
                    out.append(
                        CatalogCandidateBinding(
                            card=SemanticLinkCandidateCard(
                                candidate_id=candidate_id,
                                target_kind="metric",
                                label=label,
                                verified_aliases=aliases,
                                cube_labels=(cube_label,),
                            ),
                            canonical_target=ResolvedSemanticRef(
                                candidate_id=candidate_id,
                                target_kind=SemanticTargetKind.METRIC,
                                canonical_name=field.canonical_name,
                                cube_names=(cube.canonical_name,),
                            ),
                            discovery_context=self._human_aliases(
                                display=cube.display,
                                synonyms=cube.synonyms,
                                extra=(
                                    cube.canonical_name,
                                    cube.description or "",
                                    field.description or "",
                                ),
                            ),
                            exact_keys=frozenset(
                                {
                                    _exact_key(field.canonical_name),
                                    *(_exact_key(alias) for alias in aliases),
                                }
                            ),
                        )
                    )

            for field in self._context.kpis:
                extra = self._company_aliases.get(
                    ("kpi", field.canonical_name),
                    (),
                )
                aliases = self._human_aliases(
                    display=field.display,
                    synonyms=field.synonyms,
                    extra=extra,
                )
                candidate_id = self._candidate_id(
                    context_version=context_version,
                    target_kind="kpi",
                    canonical_name=field.canonical_name,
                )
                label = field.display or (aliases[0] if aliases else "KPI candidate")
                out.append(
                    CatalogCandidateBinding(
                        card=SemanticLinkCandidateCard(
                            candidate_id=candidate_id,
                            target_kind="kpi",
                            label=label,
                            verified_aliases=aliases,
                        ),
                        canonical_target=ResolvedSemanticRef(
                            candidate_id=candidate_id,
                            target_kind=SemanticTargetKind.KPI,
                            canonical_name=field.canonical_name,
                        ),
                        discovery_context=(
                            (field.description,) if field.description else ()
                        ),
                        exact_keys=frozenset(
                            {
                                _exact_key(field.canonical_name),
                                *(_exact_key(alias) for alias in aliases),
                            }
                        ),
                    )
                )

        if kind_hint in {"dimension", "unknown"}:
            for cube in self._context.cubes:
                cube_label = cube.display or cube.canonical_name
                for field in cube.dimensions:
                    extra = self._company_aliases.get(
                        ("dimension", field.canonical_name),
                        (),
                    )
                    aliases = self._human_aliases(
                        display=field.display,
                        synonyms=field.synonyms,
                        extra=extra,
                    )
                    candidate_id = self._candidate_id(
                        context_version=context_version,
                        target_kind="dimension",
                        canonical_name=field.canonical_name,
                        cube_names=(cube.canonical_name,),
                    )
                    label = field.display or (aliases[0] if aliases else "dimension candidate")
                    out.append(
                        CatalogCandidateBinding(
                            card=SemanticLinkCandidateCard(
                                candidate_id=candidate_id,
                                target_kind="dimension",
                                label=label,
                                verified_aliases=aliases,
                                cube_labels=(cube_label,),
                            ),
                            canonical_target=ResolvedSemanticRef(
                                candidate_id=candidate_id,
                                target_kind=SemanticTargetKind.DIMENSION,
                                canonical_name=field.canonical_name,
                                cube_names=(cube.canonical_name,),
                            ),
                            discovery_context=self._human_aliases(
                                display=cube.display,
                                synonyms=cube.synonyms,
                                extra=(
                                    cube.canonical_name,
                                    cube.description or "",
                                    field.description or "",
                                ),
                            ),
                            exact_keys=frozenset(
                                {
                                    _exact_key(field.canonical_name),
                                    *(_exact_key(alias) for alias in aliases),
                                }
                            ),
                        )
                    )

        if kind_hint == "filter":
            dimension_meta: dict[str, tuple[str, tuple[str, ...], tuple[str, ...]]] = {}
            for cube in self._context.cubes:
                for field in cube.dimensions:
                    dimension_meta[field.canonical_name] = (
                        field.display or field.canonical_name,
                        field.synonyms,
                        (cube.canonical_name,),
                    )
            for cube in self._schema.get("cubes") or ():
                cube_name = str(cube.get("name") or "")
                for raw_dimension, raw_values in (cube.get("dimension_values") or {}).items():
                    dimension_name = str(raw_dimension)
                    display, aliases, context_cubes = dimension_meta.get(
                        dimension_name,
                        (dimension_name, (), (cube_name,) if cube_name else ()),
                    )
                    sensitive = self._dimension_sensitive(dimension_name)
                    for raw_value in raw_values or ():
                        value = str(raw_value).strip()
                        if not value:
                            continue
                        candidate_id = self._candidate_id(
                            context_version=context_version,
                            target_kind="entity_value",
                            canonical_name=dimension_name,
                            dimension_name=dimension_name,
                            value=value,
                            cube_names=context_cubes or ((cube_name,) if cube_name else ()),
                        )
                        human_aliases = () if sensitive else (value,)
                        out.append(
                            CatalogCandidateBinding(
                                card=SemanticLinkCandidateCard(
                                    candidate_id=candidate_id,
                                    target_kind="entity_value",
                                    label=(f"{display} value" if sensitive else f"{display} = {value}"),
                                    verified_aliases=human_aliases,
                                    cube_labels=(),
                                ),
                                canonical_target=ResolvedFilterRef(
                                    candidate_id=candidate_id,
                                    dimension_name=dimension_name,
                                    value=value,
                                    cube_names=context_cubes or ((cube_name,) if cube_name else ()),
                                    sensitive=sensitive,
                                ),
                                exact_keys=frozenset({_exact_key(value)}),
                                sensitive=sensitive,
                            )
                        )

        unique: dict[str, CatalogCandidateBinding] = {}
        for item in out:
            unique[item.card.candidate_id] = item
        return list(unique.values())

    def _dimension_sensitive(self, dimension_name: str) -> bool:
        if classify(None, column_name=dimension_name) != "normal":
            return True
        for model in self._schema.get("models") or ():
            for column in model.get("columns") or ():
                if str(column.get("name")) == dimension_name and classify(column) != "normal":
                    return True
        return False

    def generate(
        self,
        *,
        request_id: str,
        surface: str,
        kind_hint: str,
        decision_context: str | None = None,
    ) -> CandidateSet:
        retrieval = self._retriever.retrieve(
            surface=surface,
            kind_hint=kind_hint,
            limit=self._max_candidates,
            decision_context=decision_context,
        )
        governed_by_id = {
            item.card.candidate_id: item
            for item in self._governed_candidates(kind_hint)
        }
        bindings: list[CatalogCandidateBinding] = []
        seen_ids: set[str] = set()
        for retrieved in retrieval.candidates:
            candidate_id = retrieved.card.candidate_id
            governed = governed_by_id.get(candidate_id)
            if governed is None:
                raise SemanticRetrievalContractError(
                    "semantic retriever returned candidate outside current governed catalog"
                )
            if candidate_id in seen_ids:
                continue
            # Never trust indexed/stored candidate bodies as authority; refresh the
            # canonical binding from current tenant/context truth by candidate id.
            bindings.append(governed)
            seen_ids.add(candidate_id)
        key = _exact_key(surface)

        exact = [item for item in bindings if key and key in item.exact_keys]
        if exact:
            # Preserve all exact candidates. Multiple exact verified bindings are a real
            # ambiguity and are never "ranked" by another deterministic heuristic.
            return CandidateSet(
                request_id=request_id,
                surface=surface,
                kind_hint=kind_hint,
                bindings=tuple(exact),
                too_broad=False,
                retrieval_exhaustive=retrieval.exhaustive,
                retrieval_backend=retrieval.backend,
                retrieval_truncated=retrieval.truncated,
            )

        linker_visible = [
            item
            for item in bindings
            if not item.sensitive and bool(item.card.verified_aliases)
        ]
        too_broad = len(linker_visible) > self._max_candidates
        return CandidateSet(
            request_id=request_id,
            surface=surface,
            kind_hint=kind_hint,
            bindings=tuple(linker_visible[: self._max_candidates]),
            too_broad=too_broad,
            retrieval_exhaustive=retrieval.exhaustive,
            retrieval_backend=retrieval.backend,
            retrieval_truncated=retrieval.truncated,
        )




class GovernedSiblingScopeCandidateGenerator:
    """Discovery-only fallback over current governed catalog truth.

    This component deliberately does not interpret the unresolved surface.  It receives
    an already-governed sibling cube scope from the caller, enumerates only current
    catalog candidates inside that scope, and returns a bounded CandidateSet for the
    existing semantic linker.  It never mints authority.
    """

    def __init__(
        self,
        *,
        base: SemanticCandidateGenerator,
        sibling_cube_names: tuple[str, ...],
        max_candidates: int = 48,
    ) -> None:
        self._base = base
        self._scope = frozenset(
            str(value) for value in sibling_cube_names if str(value)
        )
        self._max_candidates = max(1, int(max_candidates))

    @property
    def scope(self) -> tuple[str, ...]:
        """Deterministic governed containment scope; diagnostic only, never authority."""
        return tuple(sorted(self._scope))

    @staticmethod
    def _cube_names(item: CatalogCandidateBinding) -> frozenset[str]:
        return frozenset(
            str(value)
            for value in tuple(
                getattr(item.canonical_target, "cube_names", ()) or ()
            )
            if str(value)
        )

    def scoped_bindings(
        self,
        kind_hint: str,
    ) -> tuple[CatalogCandidateBinding, ...]:
        """Return current governed candidates inside scope before the hard visibility bound."""
        if not self._scope:
            return ()
        out = [
            item
            for item in self._base._governed_candidates(kind_hint)
            if not item.sensitive
            and bool(item.card.verified_aliases)
            and bool(self._scope.intersection(self._cube_names(item)))
        ]
        out.sort(key=lambda item: item.card.candidate_id)
        return tuple(out)

    def generate(
        self,
        *,
        request_id: str,
        surface: str,
        kind_hint: str,
        decision_context: str | None = None,
    ) -> CandidateSet:
        del decision_context  # source context belongs to cognition, never discovery truth.
        if not self._scope:
            return CandidateSet(
                request_id=request_id,
                surface=surface,
                kind_hint=kind_hint,
                bindings=(),
                too_broad=False,
                retrieval_exhaustive=False,
                retrieval_backend="governed_sibling_scope_v1",
                retrieval_truncated=False,
            )

        scoped = self.scoped_bindings(kind_hint)
        too_broad = len(scoped) > self._max_candidates
        return CandidateSet(
            request_id=request_id,
            surface=surface,
            kind_hint=kind_hint,
            bindings=tuple(scoped[: self._max_candidates]),
            too_broad=too_broad,
            # Exhaustive only inside a discovery hint; never evidence of global absence.
            retrieval_exhaustive=False,
            retrieval_backend="governed_sibling_scope_v1",
            retrieval_truncated=too_broad,
        )


class GovernedCurrentTurnCandidateGenerator:
    """Discovery-only candidates from already-governed current-message USER_SOURCE truth.

    The caller supplies current-attempt catalog bindings that were already selected and
    admitted through SemanticBindingGate for another source span. This generator never
    copies a semantic handle and never mints authority. It only re-exposes safe metric or
    dimension candidate cards to the existing bounded linker for a fresh source binding.
    """

    def __init__(
        self,
        *,
        bindings: tuple[CatalogCandidateBinding, ...],
        max_candidates: int = 48,
    ) -> None:
        self._bindings = tuple(
            item
            for item in bindings
            if not item.sensitive
            and item.card.target_kind in {"metric", "kpi", "dimension"}
            and bool(item.card.verified_aliases)
        )
        self._max_candidates = max(1, int(max_candidates))

    def generate(
        self,
        *,
        request_id: str,
        surface: str,
        kind_hint: str,
        decision_context: str | None = None,
    ) -> CandidateSet:
        del decision_context
        allowed_kinds = (
            {"metric", "kpi"}
            if kind_hint == "metric"
            else ({"dimension"} if kind_hint == "dimension" else set())
        )
        scoped = [
            item
            for item in self._bindings
            if item.card.target_kind in allowed_kinds
        ]
        unique = {
            item.card.candidate_id: item
            for item in scoped
        }
        ordered = tuple(unique[key] for key in sorted(unique))
        too_broad = len(ordered) > self._max_candidates
        return CandidateSet(
            request_id=request_id,
            surface=surface,
            kind_hint=kind_hint,
            bindings=ordered[: self._max_candidates],
            too_broad=too_broad,
            # This pool is bounded current-turn applicability context, never proof of
            # global catalog absence.
            retrieval_exhaustive=False,
            retrieval_backend="governed_current_turn_context_v1",
            retrieval_truncated=too_broad,
        )


_LINKER_SYSTEM = """You are Dima's bounded semantic linker.

For each request, interpret USER_SURFACE against the supplied CANDIDATES.
SOURCE_CONTEXT, when present, is immutable exact current-message evidence from runtime.
Use it only to disambiguate among the supplied candidates. The local USER_SURFACE remains
the semantic span being bound. Choose SELECT(candidate_id) only when one supplied candidate
is clearly the intended business concept. Otherwise ABSTAIN.

You have no authority to invent concepts, canonical identifiers, SQL, handles, aliases,
or new candidates. SOURCE_CONTEXT is not authority and cannot create a candidate.
candidate_id must be copied exactly from that request's candidate set.
Do not infer database structure. Do not repair the catalog. Return only strict schema.
"""



class SemanticDecisionProviderError(RuntimeError):
    """Typed provider/transport failure; never interpreted as ABSTAIN."""


class SemanticCandidateDecisionProvider(Protocol):
    """Cognition-only contract: bounded candidate cards -> SELECT | ABSTAIN."""

    def decide(
        self,
        requests: tuple[SemanticLinkRequestCard, ...],
    ) -> SemanticLinkBatchDecision:
        ...


class StructuredSemanticCandidateDecisionProvider:
    """Adapter for strict JSON-schema chat models; owns no semantic authority."""

    def __init__(self, *, structured: Callable[..., Any]) -> None:
        self._structured = structured

    def decide(
        self,
        requests: tuple[SemanticLinkRequestCard, ...],
    ) -> SemanticLinkBatchDecision:
        if not requests:
            raise ValueError("semantic decision provider requires at least one request")
        schema = _strict_schema(SemanticLinkBatchDecision.model_json_schema())
        try:
            raw = self._structured(
                _LINKER_SYSTEM,
                json.dumps(
                    {"requests": [item.model_dump(mode="json") for item in requests]},
                    ensure_ascii=False,
                    separators=(",", ":"),
                ),
                schema=schema,
                schema_name="dima_bounded_semantic_link_v1",
            )
            data = json.loads(raw) if isinstance(raw, str) else raw
            return SemanticLinkBatchDecision.model_validate(data)
        except SemanticDecisionProviderError:
            raise
        except Exception as exc:
            raise SemanticDecisionProviderError(
                f"structured semantic decision provider failed: {type(exc).__name__}: {exc}"
            ) from exc


class SemanticBindingGate:
    """Validate an LLM selection against the exact candidate set and mint authority."""

    def __init__(
        self,
        *,
        semantic_handles: SemanticHandleRegistry,
        tenant_binding: str,
        context_version: str,
    ) -> None:
        self._handles = semantic_handles
        self._tenant = tenant_binding
        self._context = context_version

    def bind(
        self,
        *,
        candidate_set: CandidateSet,
        candidate_id: str,
        provenance_type: str,
        parent_obligation_id: str | None = None,
        trigger_evidence_ref: str | None = None,
    ) -> SemanticHandle:
        binding = candidate_set.binding(candidate_id)
        if binding is None:
            raise SemanticLinkAuthorityError(
                "semantic linker selected candidate outside bounded catalog set"
            )
        return self._handles.mint_from_binding_gate(
            tenant_binding=self._tenant,
            context_version=self._context,
            candidate_id=binding.card.candidate_id,
            target_kind=binding.card.target_kind,
            canonical_target=binding.canonical_target,
            sensitive=binding.sensitive,
            provenance_type=provenance_type,
            parent_obligation_id=parent_obligation_id,
            trigger_evidence_ref=trigger_evidence_ref,
        )


class BoundedSemanticLinker:
    """Exact verified lookup first; otherwise one bounded structured LLM batch."""

    def __init__(
        self,
        *,
        generator: SemanticCandidateGenerator,
        binding_gate: SemanticBindingGate,
        provider: SemanticCandidateDecisionProvider | None,
        diagnostic_sink: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        self._generator = generator
        self._binding_gate = binding_gate
        self._provider = provider
        self._diagnostic_sink = diagnostic_sink

    def resolve(
        self,
        requests: tuple[tuple[str, str, str], ...],
        *,
        provenance_type: str,
        decision_context: str | None = None,
        parent_obligation_id: str | None = None,
        trigger_evidence_ref: str | None = None,
        diagnostic_metadata: dict[str, dict[str, Any]] | None = None,
    ) -> tuple[BoundedSemanticSelection, ...]:
        candidate_sets = [
            self._generator.generate(
                request_id=request_id,
                surface=surface,
                kind_hint=kind_hint,
                decision_context=decision_context,
            )
            for request_id, surface, kind_hint in requests
        ]

        outputs: dict[str, BoundedSemanticSelection] = {}
        llm_cards: list[SemanticLinkRequestCard] = []
        llm_sets: dict[str, CandidateSet] = {}

        for candidate_set in candidate_sets:
            exact = [
                item
                for item in candidate_set.bindings
                if _exact_key(candidate_set.surface) in item.exact_keys
            ]
            if len(exact) == 1:
                outputs[candidate_set.request_id] = BoundedSemanticSelection(
                    request_id=candidate_set.request_id,
                    surface=candidate_set.surface,
                    status="BOUND",
                    binding=exact[0],
                    mode="EXACT",
                )
                continue
            if len(exact) > 1:
                context_key = _exact_key(decision_context or "")
                surface_key = _exact_key(candidate_set.surface)
                has_additional_context = bool(
                    context_key and context_key != surface_key
                )

                if not has_additional_context:
                    outputs[candidate_set.request_id] = BoundedSemanticSelection(
                        request_id=candidate_set.request_id,
                        surface=candidate_set.surface,
                        status="AMBIGUOUS_EXACT",
                        mode="NONE",
                        reason=(
                            "multiple verified catalog candidates share exact surface "
                            "and no additional immutable source context is available"
                        ),
                    )
                    continue

                if self._provider is None:
                    outputs[candidate_set.request_id] = BoundedSemanticSelection(
                        request_id=candidate_set.request_id,
                        surface=candidate_set.surface,
                        status="LINKER_UNAVAILABLE",
                        mode="NONE",
                        reason=(
                            "duplicate exact candidates require bounded contextual "
                            "semantic decision"
                        ),
                    )
                    continue

                # Exact identity remains the candidate boundary. Immutable source
                # context may help cognition choose/abstain only among these exact
                # candidates; it cannot widen discovery or mint authority.
                exact_set = CandidateSet(
                    request_id=candidate_set.request_id,
                    surface=candidate_set.surface,
                    kind_hint=candidate_set.kind_hint,
                    bindings=tuple(exact),
                    too_broad=False,
                    retrieval_exhaustive=candidate_set.retrieval_exhaustive,
                    retrieval_backend=candidate_set.retrieval_backend,
                    retrieval_truncated=candidate_set.retrieval_truncated,
                )
                llm_cards.append(
                    SemanticLinkRequestCard(
                        request_id=exact_set.request_id,
                        surface=exact_set.surface,
                        source_context=decision_context,
                        kind_hint=exact_set.kind_hint,
                        candidates=exact_set.cards,
                    )
                )
                llm_sets[exact_set.request_id] = exact_set
                continue
            if not candidate_set.bindings:
                exhaustive = candidate_set.retrieval_exhaustive
                outputs[candidate_set.request_id] = BoundedSemanticSelection(
                    request_id=candidate_set.request_id,
                    surface=candidate_set.surface,
                    status="GAP" if exhaustive else "RETRIEVAL_MISS",
                    mode="NONE",
                    reason=(
                        "no governed catalog candidates exist for requested kind"
                        if exhaustive
                        else "non-exhaustive retrieval returned no candidates; semantic existence unknown"
                    ),
                )
                continue
            if candidate_set.too_broad:
                outputs[candidate_set.request_id] = BoundedSemanticSelection(
                    request_id=candidate_set.request_id,
                    surface=candidate_set.surface,
                    status="CANDIDATE_SET_TOO_BROAD",
                    mode="NONE",
                    reason="bounded candidate set exceeds configured linker limit",
                )
                continue
            if self._provider is None:
                outputs[candidate_set.request_id] = BoundedSemanticSelection(
                    request_id=candidate_set.request_id,
                    surface=candidate_set.surface,
                    status="LINKER_UNAVAILABLE",
                    mode="NONE",
                    reason="semantic decision provider unavailable for non-exact surface",
                )
                continue
            llm_cards.append(
                SemanticLinkRequestCard(
                    request_id=candidate_set.request_id,
                    surface=candidate_set.surface,
                    source_context=decision_context,
                    kind_hint=candidate_set.kind_hint,
                    candidates=candidate_set.cards,
                )
            )
            llm_sets[candidate_set.request_id] = candidate_set

        if llm_cards:
            assert self._provider is not None
            decision = self._provider.decide(tuple(llm_cards))
            choices = {item.request_id: item for item in decision.choices}
            if set(choices) != set(llm_sets):
                raise SemanticLinkAuthorityError(
                    "semantic linker response request IDs do not match bounded batch"
                )

            for request_id, candidate_set in llm_sets.items():
                choice = choices[request_id]
                if choice.decision == "ABSTAIN":
                    outputs[request_id] = BoundedSemanticSelection(
                        request_id=request_id,
                        surface=candidate_set.surface,
                        status="ABSTAIN",
                        mode="LINKER",
                        reason=choice.reason,
                    )
                    continue
                assert choice.candidate_id is not None
                binding = candidate_set.binding(choice.candidate_id)
                if binding is None:
                    raise SemanticLinkAuthorityError(
                        "semantic linker selected candidate outside its request set"
                    )
                outputs[request_id] = BoundedSemanticSelection(
                    request_id=request_id,
                    surface=candidate_set.surface,
                    status="BOUND",
                    binding=binding,
                    mode="LINKER",
                )

        ordered = tuple(
            replace(
                outputs[item.request_id],
                candidate_ids=tuple(
                    candidate.card.candidate_id
                    for candidate in item.bindings
                ),
            )
            for item in candidate_sets
        )

        if self._diagnostic_sink is not None:
            metadata = diagnostic_metadata or {}
            for candidate_set, selection in zip(candidate_sets, ordered, strict=True):
                extra = dict(metadata.get(candidate_set.request_id) or {})
                self._diagnostic_sink(
                    {
                        **extra,
                        "request_id": candidate_set.request_id,
                        "surface": candidate_set.surface,
                        "kind_hint": candidate_set.kind_hint,
                        "retrieval_backend": candidate_set.retrieval_backend,
                        "retrieval_exhaustive": candidate_set.retrieval_exhaustive,
                        "retrieval_truncated": candidate_set.retrieval_truncated,
                        "candidate_count": len(candidate_set.bindings),
                        "candidate_cards": [
                            {
                                "candidate_id": item.card.candidate_id,
                                "target_kind": item.card.target_kind,
                                # Sensitive entity candidates are excluded from linker-visible
                                # sets; labels here are therefore safe display metadata only.
                                "label": item.card.label,
                            }
                            for item in candidate_set.bindings
                            if not item.sensitive
                        ],
                        "selection": {
                            "status": selection.status,
                            "mode": selection.mode,
                            "candidate_id": (
                                selection.binding.card.candidate_id
                                if selection.binding is not None
                                else None
                            ),
                            "reason": selection.reason,
                        },
                    }
                )

        # Authority is minted only after every model decision has passed candidate-set
        # validation. The caller requests handles through bind_selection().
        return ordered

    def bind_selection(
        self,
        selection: BoundedSemanticSelection,
        *,
        provenance_type: str,
        parent_obligation_id: str | None = None,
        trigger_evidence_ref: str | None = None,
    ) -> SemanticHandle:
        if selection.status != "BOUND" or selection.binding is None:
            raise SemanticLinkAuthorityError("only BOUND selection may mint semantic authority")
        candidate_set = CandidateSet(
            request_id=selection.request_id,
            surface=selection.surface,
            kind_hint=selection.binding.card.target_kind,
            bindings=(selection.binding,),
        )
        return self._binding_gate.bind(
            candidate_set=candidate_set,
            candidate_id=selection.binding.card.candidate_id,
            provenance_type=provenance_type,
            parent_obligation_id=parent_obligation_id,
            trigger_evidence_ref=trigger_evidence_ref,
        )
