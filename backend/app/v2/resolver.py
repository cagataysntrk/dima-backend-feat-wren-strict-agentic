"""P5 SemanticResolver — deterministic grounding and clarification.

Input is typed TurnInterpretation, never the raw user question. The resolver maps
surface mentions to tenant semantic/data candidates, preserves provenance, and asks
when material ambiguity exists. It does not plan or execute analytics.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Iterable

from py_rust_stemmers import SnowballStemmer

from app.llm import _norm as _legacy_norm
from app.sensitivity import classify
from app.v2.models import (
    BoundedSemanticContextV0,
    CandidateSource,
    ClarificationChip,
    ClarificationReason,
    ClarificationState,
    ConversationStateV2,
    ResolutionStatus,
    SemanticAnchor,
    SemanticCandidate,
    SemanticHypothesis,
    SemanticMention,
    SemanticMentionKind,
    SemanticResolutionBundle,
    SemanticTargetKind,
    TurnInterpretation,
)

_FUZZY_MIN = 0.78
_FUZZY_MATERIAL = 0.92
_TOKEN_MATERIAL_MIN = 4
_TOKEN_VERSION = 1
_TURKISH_STEMMER = SnowballStemmer("turkish")


def _norm(value: str) -> str:
    """Generic semantic-surface normalization; no domain literals or parsing rules."""
    text = _legacy_norm(str(value or ""))
    return " ".join(re.sub(r"[^a-z0-9]+", " ", text).split())


def _morph_token_forms(value: str) -> tuple[frozenset[str], ...]:
    """Return conservative token forms for Turkish inflection comparison.

    Snowball can stem a bare noun more aggressively than an inflected form (for example
    bare-X -> shorter-root while inflected-X -> bare-X). Treat both the observed token and
    its Snowball stem as admissible forms. This remains a comparison mechanism only:
    canonical targets still come exclusively from verified semantic aliases.
    """
    lowered = str(value or "").lower().replace("̇", "")
    tokens = re.findall(r"[a-zçğıöşü]+", lowered)
    forms: list[frozenset[str]] = []
    for token in tokens:
        stem = _TURKISH_STEMMER.stem_word(token)
        forms.append(frozenset((token, stem)))
    return tuple(forms)


def _morph_equivalent(left: str, right: str) -> bool:
    left_forms = _morph_token_forms(left)
    right_forms = _morph_token_forms(right)
    return (
        bool(left_forms)
        and len(left_forms) == len(right_forms)
        and all(a & b for a, b in zip(left_forms, right_forms, strict=True))
    )


def _morph_contains(surface: str, verified_alias: str) -> bool:
    """Whether a verified alias occurs as a morphologically-equivalent token window.

    The interpreter may preserve a grammatical phrase ("<dimension> + grouping marker")
    rather than only the noun. Resolver may ground the verified semantic noun inside that
    typed DIMENSION/METRIC mention, but never skips tokens *inside* the alias and never
    applies this to entity-value discovery. Multiple matching semantic aliases still become
    multiple material candidates and therefore clarify.
    """
    surface_forms = _morph_token_forms(surface)
    alias_forms = _morph_token_forms(verified_alias)
    if not alias_forms or len(alias_forms) > len(surface_forms):
        return False
    width = len(alias_forms)
    for start in range(len(surface_forms) - width + 1):
        window = surface_forms[start : start + width]
        if all(a & b for a, b in zip(window, alias_forms, strict=True)):
            return True
    return False


def _uniq(values: Iterable[str]) -> tuple[str, ...]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        raw = str(value or "").strip()
        key = _norm(raw)
        if raw and key and key not in seen:
            seen.add(key)
            out.append(raw)
    return tuple(out)


def _candidate_id(
    *,
    target_kind: SemanticTargetKind,
    canonical_name: str,
    dimension_name: str | None,
    identity_value: str | None,
) -> str:
    payload = json.dumps(
        {
            "kind": target_kind.value,
            "canonical": canonical_name,
            "dimension": dimension_name,
            "value": identity_value,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]


def _binding(session_id: str | None, thread_id: str | None) -> str:
    return f"{session_id or ''}\x1f{thread_id or ''}"


def _b64e(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64d(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


@dataclass
class _Draft:
    candidate_id: str
    target_kind: SemanticTargetKind
    canonical_name: str
    dimension_name: str | None
    value: str | None
    identity_value: str | None
    cube_names: set[str] = field(default_factory=set)
    display_label: str = ""
    provenance: set[CandidateSource] = field(default_factory=set)
    score: float = 0.0
    material: bool = False
    sensitive: bool = False
    selection_aliases: set[str] = field(default_factory=set)

    def freeze(self) -> SemanticCandidate:
        order = {
            CandidateSource.EXPLICIT_ANCHOR: 0,
            CandidateSource.CURRENT_FOCUS: 1,
            CandidateSource.CANONICAL_NAME: 2,
            CandidateSource.VERIFIED_SYNONYM: 3,
            CandidateSource.MORPHOLOGICAL_MATCH: 4,
            CandidateSource.EXACT_ENTITY_VALUE: 5,
            CandidateSource.COMPANY_VOCABULARY: 6,
            CandidateSource.FUZZY_SUGGESTION: 7,
        }
        return SemanticCandidate(
            candidate_id=self.candidate_id,
            target_kind=self.target_kind,
            canonical_name=self.canonical_name,
            dimension_name=self.dimension_name,
            value=self.value,
            cube_names=tuple(sorted(self.cube_names)),
            display_label=self.display_label,
            provenance=tuple(sorted(self.provenance, key=lambda x: order[x])),
            score=max(0.0, min(1.0, self.score)),
            material=self.material,
            sensitive=self.sensitive,
            selection_aliases=_uniq(sorted(self.selection_aliases)),
        )


class ClarificationTokenError(ValueError):
    pass


class SemanticResolver:
    """Deterministic Day 2 semantic grounding.

    A single strong candidate resolves. Multiple material candidates clarify. Fuzzy-only
    candidates are suggestions and never silently become semantic truth.
    """

    def __init__(self, *, signing_key: bytes):
        if not signing_key:
            raise ValueError("clarification signing key boş olamaz")
        self._signing_key = bytes(signing_key)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def resolve_turn(
        self,
        *,
        turn: TurnInterpretation,
        schema: dict,
        semantic_context: BoundedSemanticContextV0,
        conversation: ConversationStateV2,
        tenant_binding: str,
        session_id: str | None,
        thread_id: str | None,
    ) -> SemanticResolutionBundle:
        mentions = self._semantic_mentions(turn)
        hypotheses: list[SemanticHypothesis] = []
        blocking: tuple[
            SemanticMention,
            ClarificationReason,
            tuple[SemanticCandidate, ...],
        ] | None = None

        for mention in mentions:
            candidates = self._candidates_for(
                mention=mention,
                schema=schema,
                semantic_context=semantic_context,
                conversation=conversation,
            )
            status, resolved_id, resolved_surface, reason = self._decide(
                mention=mention,
                candidates=candidates,
            )
            hypotheses.append(
                SemanticHypothesis(
                    source_mention=mention.text,
                    mention_kind=mention.kind,
                    status=status,
                    candidates=candidates,
                    resolved_candidate_id=resolved_id,
                    resolved_surface_value=resolved_surface,
                )
            )
            if blocking is None and status != ResolutionStatus.RESOLVED:
                blocking = (
                    mention,
                    reason or ClarificationReason.SEMANTIC_GAP,
                    candidates,
                )

        clarification = None
        if blocking is not None:
            mention, reason, candidates = blocking
            clarification = self._clarification(
                mention=mention,
                reason=reason,
                candidates=candidates,
                context_version=semantic_context.context_version.version,
                tenant_binding=tenant_binding,
                session_id=session_id,
                thread_id=thread_id,
            )

        return SemanticResolutionBundle(
            hypotheses=tuple(hypotheses),
            clarification=clarification,
        )

    def resume_signed(
        self,
        *,
        token: str,
        schema: dict,
        semantic_context: BoundedSemanticContextV0,
        conversation: ConversationStateV2,
        tenant_binding: str,
        session_id: str | None,
        thread_id: str | None,
    ) -> SemanticResolutionBundle:
        payload = self._verify_token(
            token,
            context_version=semantic_context.context_version.version,
            tenant_binding=tenant_binding,
            session_id=session_id,
            thread_id=thread_id,
        )
        try:
            mention = SemanticMention(
                text=str(payload["mention"]),
                kind=SemanticMentionKind(str(payload["kind"])),
            )
        except Exception as exc:
            raise ClarificationTokenError("clarification token mention geçersiz") from exc

        candidates = self._candidates_for(
            mention=mention,
            schema=schema,
            semantic_context=semantic_context,
            conversation=conversation,
        )
        _, _, _, reason = self._decide(mention=mention, candidates=candidates)
        if reason is None:
            raise ClarificationTokenError("clarification artık blocking değil")

        expected = self._clarification(
            mention=mention,
            reason=reason,
            candidates=candidates,
            context_version=semantic_context.context_version.version,
            tenant_binding=tenant_binding,
            session_id=session_id,
            thread_id=thread_id,
        )
        if payload.get("qid") != expected.clarification_id:
            raise ClarificationTokenError("clarification state/context değişmiş")

        selected = next(
            (candidate for candidate in candidates if candidate.candidate_id == payload.get("cid")),
            None,
        )
        if selected is None:
            raise ClarificationTokenError("candidate current semantic context'te yok")

        return SemanticResolutionBundle(
            hypotheses=(
                self._resolved_hypothesis(mention, selected),
            ),
            clarification=None,
        )

    def resume_free_text(
        self,
        *,
        turn: TurnInterpretation,
        pending: ClarificationState,
        schema: dict,
        semantic_context: BoundedSemanticContextV0,
        conversation: ConversationStateV2,
        tenant_binding: str,
        session_id: str | None,
        thread_id: str | None,
    ) -> SemanticResolutionBundle:
        if not pending.pending or not pending.source_mention or pending.source_kind is None:
            return self.resolve_turn(
                turn=turn,
                schema=schema,
                semantic_context=semantic_context,
                conversation=conversation,
                tenant_binding=tenant_binding,
                session_id=session_id,
                thread_id=thread_id,
            )

        source = SemanticMention(text=pending.source_mention, kind=pending.source_kind)
        candidates = self._candidates_for(
            mention=source,
            schema=schema,
            semantic_context=semantic_context,
            conversation=conversation,
        )
        _, _, _, reason = self._decide(mention=source, candidates=candidates)
        reason = reason or ClarificationReason.SEMANTIC_GAP
        expected = self._clarification(
            mention=source,
            reason=reason,
            candidates=candidates,
            context_version=semantic_context.context_version.version,
            tenant_binding=tenant_binding,
            session_id=session_id,
            thread_id=thread_id,
        )
        if not pending.clarification_id or pending.clarification_id != expected.clarification_id:
            return SemanticResolutionBundle(
                hypotheses=(
                    SemanticHypothesis(
                        source_mention=source.text,
                        mention_kind=source.kind,
                        status=ResolutionStatus.CLARIFY,
                        candidates=candidates,
                    ),
                ),
                clarification=expected,
            )

        answer_mentions = self._semantic_mentions(turn)
        selected = self._select_from_answer(candidates, answer_mentions)
        if selected is None:
            return SemanticResolutionBundle(
                hypotheses=(
                    SemanticHypothesis(
                        source_mention=source.text,
                        mention_kind=source.kind,
                        status=ResolutionStatus.CLARIFY,
                        candidates=candidates,
                    ),
                ),
                clarification=expected,
            )

        return SemanticResolutionBundle(
            hypotheses=(self._resolved_hypothesis(source, selected),),
            clarification=None,
        )

    # ------------------------------------------------------------------
    # Candidate generation
    # ------------------------------------------------------------------

    def _semantic_mentions(self, turn: TurnInterpretation) -> tuple[SemanticMention, ...]:
        req = turn.analytical_request
        ordered: list[SemanticMention] = []
        if req is not None:
            ordered.extend(req.metric_mentions)
            ordered.extend(req.dimension_mentions)
            ordered.extend(req.filter_mentions)

        research = turn.research_request
        if research is not None:
            for goal in research.goals:
                ordered.extend(goal.subject_mentions)
                ordered.extend(goal.related_mentions)

        represented = {_norm(m.text) for m in ordered}
        for unresolved in turn.unresolved_mentions:
            if _norm(unresolved.text) not in represented:
                ordered.append(
                    SemanticMention(
                        text=unresolved.text,
                        kind=SemanticMentionKind.UNKNOWN,
                    )
                )

        out: list[SemanticMention] = []
        seen: set[tuple[str, SemanticMentionKind]] = set()
        for mention in ordered:
            key = (_norm(mention.text), mention.kind)
            if key[0] and key not in seen:
                seen.add(key)
                out.append(mention)
        return tuple(out)

    def _allowed_target(self, mention_kind: SemanticMentionKind, target: SemanticTargetKind) -> bool:
        if mention_kind == SemanticMentionKind.METRIC:
            return target in {SemanticTargetKind.METRIC, SemanticTargetKind.KPI}
        if mention_kind == SemanticMentionKind.DIMENSION:
            return target == SemanticTargetKind.DIMENSION
        if mention_kind == SemanticMentionKind.FILTER:
            return target in {SemanticTargetKind.ENTITY_VALUE, SemanticTargetKind.DIMENSION}
        if mention_kind == SemanticMentionKind.UNKNOWN:
            return True
        return False

    def _candidates_for(
        self,
        *,
        mention: SemanticMention,
        schema: dict,
        semantic_context: BoundedSemanticContextV0,
        conversation: ConversationStateV2,
    ) -> tuple[SemanticCandidate, ...]:
        needle = _norm(mention.text)
        if not needle:
            return ()

        drafts: dict[str, _Draft] = {}

        for anchor, source in self._anchors(conversation):
            if not self._allowed_target(mention.kind, anchor.target_kind):
                continue
            aliases = _uniq(
                (
                    anchor.canonical_name,
                    anchor.display_label or "",
                    anchor.value or "",
                    *anchor.aliases,
                )
            )
            if any(_norm(alias) == needle for alias in aliases):
                self._add(
                    drafts,
                    target_kind=anchor.target_kind,
                    canonical_name=anchor.canonical_name,
                    dimension_name=anchor.dimension_name,
                    value=None if anchor.sensitive else anchor.value,
                    identity_value=anchor.value,
                    cube_names=(),
                    display_label=anchor.display_label or anchor.canonical_name,
                    provenance=source,
                    score=1.0,
                    material=True,
                    sensitive=anchor.sensitive,
                    aliases=aliases,
                )

        self._catalog_candidates(
            drafts=drafts,
            mention=mention,
            needle=needle,
            semantic_context=semantic_context,
        )
        self._entity_candidates(
            drafts=drafts,
            mention=mention,
            needle=needle,
            schema=schema,
            semantic_context=semantic_context,
        )
        self._company_vocabulary_candidates(
            drafts=drafts,
            mention=mention,
            needle=needle,
            schema=schema,
        )

        frozen = [draft.freeze() for draft in drafts.values()]
        return tuple(sorted(frozen, key=self._sort_key))

    def _anchors(
        self, conversation: ConversationStateV2
    ) -> tuple[tuple[SemanticAnchor, CandidateSource], ...]:
        out: list[tuple[SemanticAnchor, CandidateSource]] = []
        if conversation.selected_anchor is not None:
            out.append((conversation.selected_anchor, CandidateSource.EXPLICIT_ANCHOR))
        out.extend(
            (anchor, CandidateSource.CURRENT_FOCUS)
            for anchor in conversation.focus_anchors
        )
        return tuple(out)

    def _catalog_candidates(
        self,
        *,
        drafts: dict[str, _Draft],
        mention: SemanticMention,
        needle: str,
        semantic_context: BoundedSemanticContextV0,
    ) -> None:
        for cube in semantic_context.cubes:
            if self._allowed_target(mention.kind, SemanticTargetKind.CUBE):
                self._match_semantic_surface(
                    drafts,
                    needle=needle,
                    surface=mention.text,
                    target_kind=SemanticTargetKind.CUBE,
                    canonical_name=cube.canonical_name,
                    display=cube.display,
                    synonyms=cube.synonyms,
                    cube_names=(cube.canonical_name,),
                )

            for metric in cube.measures:
                if not self._allowed_target(mention.kind, SemanticTargetKind.METRIC):
                    continue
                self._match_semantic_surface(
                    drafts,
                    needle=needle,
                    surface=mention.text,
                    target_kind=SemanticTargetKind.METRIC,
                    canonical_name=metric.canonical_name,
                    display=metric.display,
                    synonyms=metric.synonyms,
                    cube_names=(cube.canonical_name,),
                )

            for dimension in cube.dimensions:
                if not self._allowed_target(mention.kind, SemanticTargetKind.DIMENSION):
                    continue
                self._match_semantic_surface(
                    drafts,
                    needle=needle,
                    surface=mention.text,
                    target_kind=SemanticTargetKind.DIMENSION,
                    canonical_name=dimension.canonical_name,
                    display=dimension.display,
                    synonyms=dimension.synonyms,
                    cube_names=(cube.canonical_name,),
                )

        for kpi in semantic_context.kpis:
            if not self._allowed_target(mention.kind, SemanticTargetKind.KPI):
                continue
            self._match_semantic_surface(
                drafts,
                needle=needle,
                surface=mention.text,
                target_kind=SemanticTargetKind.KPI,
                canonical_name=kpi.canonical_name,
                display=kpi.display,
                synonyms=kpi.synonyms,
                cube_names=(),
            )

    def _match_semantic_surface(
        self,
        drafts: dict[str, _Draft],
        *,
        needle: str,
        surface: str,
        target_kind: SemanticTargetKind,
        canonical_name: str,
        display: str | None,
        synonyms: tuple[str, ...],
        cube_names: tuple[str, ...],
    ) -> None:
        canonical_norm = _norm(canonical_name)
        aliases = _uniq((canonical_name, display or "", *synonyms))

        if needle == canonical_norm:
            self._add(
                drafts,
                target_kind=target_kind,
                canonical_name=canonical_name,
                dimension_name=None,
                value=None,
                identity_value=None,
                cube_names=cube_names,
                display_label=self._semantic_label(target_kind, display or canonical_name),
                provenance=CandidateSource.CANONICAL_NAME,
                score=1.0,
                material=True,
                sensitive=False,
                aliases=aliases,
            )

        synonym_norms = {_norm(x) for x in (*synonyms, display or "") if _norm(x)}
        if needle in synonym_norms:
            self._add(
                drafts,
                target_kind=target_kind,
                canonical_name=canonical_name,
                dimension_name=None,
                value=None,
                identity_value=None,
                cube_names=cube_names,
                display_label=self._semantic_label(target_kind, display or canonical_name),
                provenance=CandidateSource.VERIFIED_SYNONYM,
                score=1.0,
                material=True,
                sensitive=False,
                aliases=aliases,
            )

        morph_aliases = _uniq((display or "", *synonyms))
        if (
            needle not in synonym_norms
            and any(_morph_contains(surface, alias) for alias in morph_aliases)
        ):
            self._add(
                drafts,
                target_kind=target_kind,
                canonical_name=canonical_name,
                dimension_name=None,
                value=None,
                identity_value=None,
                cube_names=cube_names,
                display_label=self._semantic_label(target_kind, display or canonical_name),
                provenance=CandidateSource.MORPHOLOGICAL_MATCH,
                score=0.98,
                material=True,
                sensitive=False,
                aliases=aliases,
            )

        score, token_material = self._best_fuzzy(needle, aliases)
        if score >= _FUZZY_MIN and needle not in ({canonical_norm} | synonym_norms):
            self._add(
                drafts,
                target_kind=target_kind,
                canonical_name=canonical_name,
                dimension_name=None,
                value=None,
                identity_value=None,
                cube_names=cube_names,
                display_label=self._semantic_label(target_kind, display or canonical_name),
                provenance=CandidateSource.FUZZY_SUGGESTION,
                score=score,
                material=score >= _FUZZY_MATERIAL or token_material,
                sensitive=False,
                aliases=aliases,
            )

    def _entity_candidates(
        self,
        *,
        drafts: dict[str, _Draft],
        mention: SemanticMention,
        needle: str,
        schema: dict,
        semantic_context: BoundedSemanticContextV0,
    ) -> None:
        if not self._allowed_target(mention.kind, SemanticTargetKind.ENTITY_VALUE):
            return

        dimension_meta: dict[str, tuple[str, tuple[str, ...]]] = {}
        for cube in semantic_context.cubes:
            for dimension in cube.dimensions:
                dimension_meta.setdefault(
                    dimension.canonical_name,
                    (
                        dimension.display or dimension.canonical_name,
                        _uniq(
                            (
                                dimension.canonical_name,
                                dimension.display or "",
                                *dimension.synonyms,
                            )
                        ),
                    ),
                )

        for cube in schema.get("cubes") or []:
            cube_name = str(cube.get("name") or "")
            for dimension_name, values in (cube.get("dimension_values") or {}).items():
                dimension_name = str(dimension_name)
                display, dim_aliases = dimension_meta.get(
                    dimension_name,
                    (dimension_name, (dimension_name,)),
                )
                sensitive = self._dimension_sensitive(schema, dimension_name)

                for raw in values or ():
                    value = str(raw).strip()
                    value_norm = _norm(value)
                    if not value_norm:
                        continue

                    if needle == value_norm:
                        self._add(
                            drafts,
                            target_kind=SemanticTargetKind.ENTITY_VALUE,
                            canonical_name=dimension_name,
                            dimension_name=dimension_name,
                            value=None if sensitive else value,
                            identity_value=value,
                            cube_names=(cube_name,) if cube_name else (),
                            display_label=(
                                f"{display} değeri"
                                if sensitive
                                else f"{display} = {value}"
                            ),
                            provenance=CandidateSource.EXACT_ENTITY_VALUE,
                            score=1.0,
                            material=True,
                            sensitive=sensitive,
                            aliases=(
                                dim_aliases
                                if sensitive
                                else _uniq((*dim_aliases, value))
                            ),
                        )
                        continue

                    # Sensitive values are never discovered by fuzzy search: that would
                    # reveal tenant data the user did not already provide exactly.
                    if sensitive:
                        continue

                    score, token_material = self._best_fuzzy(needle, (value,))
                    if score >= _FUZZY_MIN:
                        self._add(
                            drafts,
                            target_kind=SemanticTargetKind.ENTITY_VALUE,
                            canonical_name=dimension_name,
                            dimension_name=dimension_name,
                            value=value,
                            identity_value=value,
                            cube_names=(cube_name,) if cube_name else (),
                            display_label=f"{display} = {value}",
                            provenance=CandidateSource.FUZZY_SUGGESTION,
                            score=score,
                            material=score >= _FUZZY_MATERIAL or token_material,
                            sensitive=False,
                            aliases=_uniq((*dim_aliases, value)),
                        )

    def _company_vocabulary_candidates(
        self,
        *,
        drafts: dict[str, _Draft],
        mention: SemanticMention,
        needle: str,
        schema: dict,
    ) -> None:
        """Consume only explicitly verified vocabulary provenance when a runtime exposes it."""
        for item in schema.get("company_vocabulary") or ():
            if not isinstance(item, dict) or item.get("verified") is not True:
                continue
            try:
                target_kind = SemanticTargetKind(str(item["target_kind"]))
            except Exception:
                continue
            if not self._allowed_target(mention.kind, target_kind):
                continue
            surface = str(item.get("surface") or "").strip()
            if not surface or _norm(surface) != needle:
                continue
            canonical = str(item.get("canonical_name") or "").strip()
            if not canonical:
                continue
            dimension_name = (
                str(item.get("dimension_name"))
                if item.get("dimension_name") is not None
                else None
            )
            value = (
                str(item.get("value"))
                if item.get("value") is not None
                else None
            )
            sensitive = bool(item.get("sensitive", False))
            aliases = _uniq(
                (
                    surface,
                    canonical,
                    str(item.get("display_label") or ""),
                )
            )
            self._add(
                drafts,
                target_kind=target_kind,
                canonical_name=canonical,
                dimension_name=dimension_name,
                value=None if sensitive else value,
                identity_value=value,
                cube_names=tuple(str(x) for x in (item.get("cube_names") or ())),
                display_label=str(item.get("display_label") or canonical),
                provenance=CandidateSource.COMPANY_VOCABULARY,
                score=1.0,
                material=True,
                sensitive=sensitive,
                aliases=aliases,
            )

    def _dimension_sensitive(self, schema: dict, dimension_name: str) -> bool:
        if classify(None, column_name=dimension_name) != "normal":
            return True
        for model in schema.get("models") or ():
            for column in model.get("columns") or ():
                if str(column.get("name")) == dimension_name and classify(column) != "normal":
                    return True
        return False

    def _best_fuzzy(self, needle: str, aliases: Iterable[str]) -> tuple[float, bool]:
        best = 0.0
        token_material = False
        needle_tokens = set(needle.split())
        for alias in aliases:
            candidate = _norm(alias)
            if not candidate or candidate == needle:
                continue
            score = SequenceMatcher(None, needle, candidate).ratio()
            candidate_tokens = set(candidate.split())
            token_hit = (
                len(needle) >= _TOKEN_MATERIAL_MIN
                and (
                    needle in candidate_tokens
                    or candidate in needle_tokens
                    or needle.startswith(candidate + " ")
                    or candidate.startswith(needle + " ")
                )
            )
            if token_hit:
                score = max(score, 0.93)
                token_material = True
            best = max(best, score)
        return best, token_material

    def _add(
        self,
        drafts: dict[str, _Draft],
        *,
        target_kind: SemanticTargetKind,
        canonical_name: str,
        dimension_name: str | None,
        value: str | None,
        identity_value: str | None,
        cube_names: Iterable[str],
        display_label: str,
        provenance: CandidateSource,
        score: float,
        material: bool,
        sensitive: bool,
        aliases: Iterable[str],
    ) -> None:
        cid = _candidate_id(
            target_kind=target_kind,
            canonical_name=canonical_name,
            dimension_name=dimension_name,
            identity_value=identity_value,
        )
        draft = drafts.get(cid)
        if draft is None:
            draft = _Draft(
                candidate_id=cid,
                target_kind=target_kind,
                canonical_name=canonical_name,
                dimension_name=dimension_name,
                value=value,
                identity_value=identity_value,
                display_label=display_label,
                sensitive=sensitive,
            )
            drafts[cid] = draft
        draft.cube_names.update(str(x) for x in cube_names if x)
        draft.provenance.add(provenance)
        draft.score = max(draft.score, float(score))
        draft.material = draft.material or material
        draft.sensitive = draft.sensitive or sensitive
        draft.selection_aliases.update(str(x) for x in aliases if x)

    # ------------------------------------------------------------------
    # Decision / clarification
    # ------------------------------------------------------------------

    def _decide(
        self,
        *,
        mention: SemanticMention,
        candidates: tuple[SemanticCandidate, ...],
    ) -> tuple[ResolutionStatus, str | None, str | None, ClarificationReason | None]:
        material = [candidate for candidate in candidates if candidate.material]
        if len(material) > 1:
            return (
                ResolutionStatus.CLARIFY,
                None,
                None,
                ClarificationReason.MATERIAL_AMBIGUITY,
            )
        if len(material) == 1:
            candidate = material[0]
            only_fuzzy = set(candidate.provenance) == {CandidateSource.FUZZY_SUGGESTION}
            if only_fuzzy:
                return (
                    ResolutionStatus.CLARIFY,
                    None,
                    None,
                    ClarificationReason.FUZZY_ONLY,
                )
            return (
                ResolutionStatus.RESOLVED,
                candidate.candidate_id,
                (
                    mention.text
                    if candidate.target_kind == SemanticTargetKind.ENTITY_VALUE
                    and candidate.sensitive
                    else candidate.value
                ),
                None,
            )
        if candidates:
            return (
                ResolutionStatus.CLARIFY,
                None,
                None,
                ClarificationReason.FUZZY_ONLY,
            )
        return (
            ResolutionStatus.SEMANTIC_GAP,
            None,
            None,
            ClarificationReason.SEMANTIC_GAP,
        )

    def _resolved_hypothesis(
        self,
        mention: SemanticMention,
        candidate: SemanticCandidate,
    ) -> SemanticHypothesis:
        return SemanticHypothesis(
            source_mention=mention.text,
            mention_kind=mention.kind,
            status=ResolutionStatus.RESOLVED,
            candidates=(candidate,),
            resolved_candidate_id=candidate.candidate_id,
            resolved_surface_value=(
                mention.text
                if candidate.target_kind == SemanticTargetKind.ENTITY_VALUE
                and candidate.sensitive
                else candidate.value
            ),
        )

    def _clarification(
        self,
        *,
        mention: SemanticMention,
        reason: ClarificationReason,
        candidates: tuple[SemanticCandidate, ...],
        context_version: str,
        tenant_binding: str,
        session_id: str | None,
        thread_id: str | None,
    ) -> ClarificationState:
        qid_payload = json.dumps(
            {
                "tenant": tenant_binding,
                "ctx": context_version,
                "flow": _binding(session_id, thread_id),
                "mention": mention.text,
                "kind": mention.kind.value,
                "reason": reason.value,
                "candidates": [candidate.candidate_id for candidate in candidates],
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        qid = hashlib.sha256(qid_payload.encode("utf-8")).hexdigest()[:24]

        if reason == ClarificationReason.MATERIAL_AMBIGUITY:
            question = f"“{mention.text}” ile hangisini kastediyorsunuz?"
        elif reason == ClarificationReason.FUZZY_ONLY:
            question = (
                f"“{mention.text}” için doğrulanmış birebir eşleşme bulamadım. "
                "Şunlardan biri mi?"
            )
        else:
            question = (
                f"“{mention.text}” için doğrulanmış bir semantic karşılık bulamadım. "
                "Hangi iş kavramını kastettiğinizi belirtir misiniz?"
            )

        chips = tuple(
            ClarificationChip(
                candidate_id=candidate.candidate_id,
                label=candidate.display_label,
                token=self._sign_token(
                    {
                        "v": _TOKEN_VERSION,
                        "tenant": tenant_binding,
                        "ctx": context_version,
                        "flow": _binding(session_id, thread_id),
                        "qid": qid,
                        "cid": candidate.candidate_id,
                        "mention": mention.text,
                        "kind": mention.kind.value,
                    }
                ),
            )
            for candidate in candidates
        )

        return ClarificationState(
            pending=True,
            clarification_id=qid,
            source_mention=mention.text,
            source_kind=mention.kind,
            reason=reason,
            question=question,
            candidates=candidates,
            chips=chips,
        )

    def _select_from_answer(
        self,
        candidates: tuple[SemanticCandidate, ...],
        answer_mentions: tuple[SemanticMention, ...],
    ) -> SemanticCandidate | None:
        if not candidates or not answer_mentions:
            return None
        answer = {_norm(mention.text) for mention in answer_mentions if _norm(mention.text)}
        scored: list[tuple[int, SemanticCandidate]] = []
        for candidate in candidates:
            aliases = {_norm(alias) for alias in candidate.selection_aliases if _norm(alias)}
            score = len(answer & aliases)
            if score:
                scored.append((score, candidate))
        if not scored:
            return None
        scored.sort(key=lambda item: (-item[0], self._sort_key(item[1])))
        best = scored[0][0]
        winners = [candidate for score, candidate in scored if score == best]
        return winners[0] if len(winners) == 1 else None

    def _semantic_label(self, target_kind: SemanticTargetKind, display: str) -> str:
        suffix = {
            SemanticTargetKind.METRIC: "metrik",
            SemanticTargetKind.DIMENSION: "boyut",
            SemanticTargetKind.KPI: "KPI",
            SemanticTargetKind.CUBE: "konu",
            SemanticTargetKind.ENTITY_VALUE: "değer",
        }[target_kind]
        return f"{display} · {suffix}"

    def _sort_key(self, candidate: SemanticCandidate):
        rank = {
            CandidateSource.EXPLICIT_ANCHOR: 0,
            CandidateSource.CURRENT_FOCUS: 1,
            CandidateSource.CANONICAL_NAME: 2,
            CandidateSource.VERIFIED_SYNONYM: 3,
            CandidateSource.MORPHOLOGICAL_MATCH: 4,
            CandidateSource.EXACT_ENTITY_VALUE: 5,
            CandidateSource.COMPANY_VOCABULARY: 6,
            CandidateSource.FUZZY_SUGGESTION: 7,
        }
        best = min(rank[source] for source in candidate.provenance)
        return (best, -candidate.score, candidate.display_label.casefold(), candidate.candidate_id)

    # ------------------------------------------------------------------
    # Signed chip integrity
    # ------------------------------------------------------------------

    def _sign_token(self, payload: dict) -> str:
        body = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        encoded = _b64e(body)
        signature = hmac.new(
            self._signing_key,
            encoded.encode("ascii"),
            hashlib.sha256,
        ).digest()
        return f"{encoded}.{_b64e(signature)}"

    def _verify_token(
        self,
        token: str,
        *,
        context_version: str,
        tenant_binding: str,
        session_id: str | None,
        thread_id: str | None,
    ) -> dict:
        try:
            encoded, signature_text = token.split(".", 1)
            expected = hmac.new(
                self._signing_key,
                encoded.encode("ascii"),
                hashlib.sha256,
            ).digest()
            actual = _b64d(signature_text)
            if not hmac.compare_digest(expected, actual):
                raise ClarificationTokenError("clarification token imzası geçersiz")
            payload = json.loads(_b64d(encoded))
        except ClarificationTokenError:
            raise
        except Exception as exc:
            raise ClarificationTokenError("clarification token biçimi geçersiz") from exc

        if payload.get("v") != _TOKEN_VERSION:
            raise ClarificationTokenError("clarification token sürümü geçersiz")
        if payload.get("tenant") != tenant_binding:
            raise ClarificationTokenError("clarification token tenant uyuşmuyor")
        if payload.get("ctx") != context_version:
            raise ClarificationTokenError("clarification token context version bayat")
        if payload.get("flow") != _binding(session_id, thread_id):
            raise ClarificationTokenError("clarification token flow uyuşmuyor")
        return payload
