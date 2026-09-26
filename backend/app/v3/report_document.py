"""P20 governed ReportDocument authority.

P20 is a publication-legality layer over already-governed P14-P19 truth.
It performs no analytics, query planning, semantic discovery, causal discovery,
or lower-authority mutation.
"""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlmodel import Session, select
from app.v3.claim_lineage import ClaimEpistemicState, ClaimLineageStore
from app.v3.hypothesis_root_cause import AggregateOutcome, CausalQualification, ContributionClass, EvidenceStrength, GroundingSourceKind, HypothesisDisposition, HypothesisRootCauseStore
from app.v3.research import ObligationState, StoppingStatus
from app.v3.research_store import ResearchPersistenceError, ResearchSessionStore
from control_plane.authorize import Principal
from control_plane.db import engine as control_plane_engine
from control_plane.models import BusinessRelationshipPolicyUseRecord, HypothesisRecord, ReportDocumentRecord, ResearchExecutionLink, ResearchExplorationMaterial, ResearchReasoningStepRecord

class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra='forbid')

class P20ReportError(RuntimeError):

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f'{code}: {detail}')
        self.code = code
        self.detail = detail

class ReportStatementKind(StrEnum):
    NUMERIC = 'NUMERIC'
    ANALYTICAL_FACT = 'ANALYTICAL_FACT'
    CAUSAL = 'CAUSAL'
    ROOT_CAUSE = 'ROOT_CAUSE'
    CONTRIBUTION = 'CONTRIBUTION'
    UNCERTAINTY = 'UNCERTAINTY'
    LIMITATION = 'LIMITATION'
    CONTEXT = 'CONTEXT'

class ReportSourceKind(StrEnum):
    P14_EVIDENCE = 'P14_EVIDENCE'
    P15_MATERIAL = 'P15_MATERIAL'
    P16_CLAIM = 'P16_CLAIM'
    P17_REASONING_STEP = 'P17_REASONING_STEP'
    P18_POLICY_USE = 'P18_POLICY_USE'
    P19_ASSESSMENT = 'P19_ASSESSMENT'

class CoverageStatus(StrEnum):
    REPRESENTED = 'REPRESENTED'
    LIMITED = 'LIMITED'

class ReportCurrentness(StrEnum):
    CURRENT = 'CURRENT'
    STALE_SOURCE_SET = 'STALE_SOURCE_SET'

class SourceReference(Frozen):
    source_kind: ReportSourceKind
    source_ref: str = Field(min_length=1)
    obligation_id: str = Field(min_length=1)
    source_receipt_id: str | None = None
    source_path: str | None = Field(default=None, max_length=512)
    source_unit_path: str | None = Field(default=None, max_length=512)

    @model_validator(mode='after')
    def coherent(self):
        if self.source_kind == ReportSourceKind.P14_EVIDENCE:
            if not self.source_receipt_id:
                raise ValueError('P14 Evidence source requires exact receipt identity')
        elif self.source_receipt_id is not None:
            raise ValueError('receipt identity is legal only for P14 Evidence source')
        if self.source_unit_path is not None and self.source_path is None:
            raise ValueError('unit provenance requires numeric source path')
        return self

class ReportLimitation(Frozen):
    limitation_id: str = Field(pattern='^p20l_[a-f0-9]{24}$')
    obligation_id: str = Field(min_length=1)
    code: str = Field(min_length=1)
    detail: str = Field(min_length=1)
    source_refs: tuple[SourceReference, ...] = ()

class CoverageEntry(Frozen):
    obligation_id: str = Field(min_length=1)
    coverage_status: CoverageStatus
    statement_ids: tuple[str, ...] = ()
    limitation_ids: tuple[str, ...] = ()

    @model_validator(mode='after')
    def coherent(self):
        if len(self.statement_ids) != len(set(self.statement_ids)):
            raise ValueError('coverage statement ids must be unique')
        if len(self.limitation_ids) != len(set(self.limitation_ids)):
            raise ValueError('coverage limitation ids must be unique')
        if self.coverage_status == CoverageStatus.REPRESENTED:
            if not self.statement_ids or self.limitation_ids:
                raise ValueError('REPRESENTED requires statements and no coverage limitation')
        elif not self.limitation_ids or self.statement_ids:
            raise ValueError('LIMITED requires limitations and no represented statements')
        return self

class ReportStatement(Frozen):
    statement_id: str = Field(pattern='^p20s_[a-f0-9]{24}$')
    statement_kind: ReportStatementKind
    source_refs: tuple[SourceReference, ...] = ()
    obligation_refs: tuple[str, ...] = Field(min_length=1)
    limitation_refs: tuple[str, ...] = ()
    upstream_epistemic_ceiling: str = Field(min_length=1)
    payload: dict[str, Any] = Field(default_factory=dict)
    text: str | None = None

    @model_validator(mode='after')
    def coherent(self):
        if len(self.obligation_refs) != len(set(self.obligation_refs)):
            raise ValueError('statement obligation refs must be unique')
        if len(self.limitation_refs) != len(set(self.limitation_refs)):
            raise ValueError('statement limitation refs must be unique')
        if self.text is not None and (not self.text.strip()):
            raise ValueError('statement text cannot be blank')
        return self

class ReportDraft(Frozen):
    research_session_id: str = Field(pattern='^rs_[a-f0-9]{24}$')
    report_key: str = Field(min_length=1, max_length=160)
    coverage: tuple[CoverageEntry, ...] = Field(min_length=1)
    statements: tuple[ReportStatement, ...] = ()
    limitations: tuple[ReportLimitation, ...] = ()

class ReportDocument(Frozen):
    report_id: str = Field(pattern='^p20r_[a-f0-9]{24}$')
    research_session_id: str = Field(pattern='^rs_[a-f0-9]{24}$')
    tenant_binding: str = Field(min_length=1)
    semantic_context_version: str = Field(min_length=1)
    report_key: str = Field(min_length=1)
    revision: int = Field(ge=1)
    parent_report_id: str | None = Field(default=None, pattern='^p20r_[a-f0-9]{24}$')
    coverage: tuple[CoverageEntry, ...]
    statements: tuple[ReportStatement, ...]
    source_refs: tuple[SourceReference, ...]
    limitations: tuple[ReportLimitation, ...]
    source_set_fingerprint: str = Field(pattern='^[a-f0-9]{64}$')
    report_fingerprint: str = Field(pattern='^[a-f0-9]{64}$')
    created_at: datetime

def _canonical_json(value: Any, *, code: str) -> tuple[str, str]:
    try:
        raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False, default=str)
    except (TypeError, ValueError) as exc:
        raise P20ReportError(code, 'value is not deterministic JSON') from exc
    return (raw, hashlib.sha256(raw.encode('utf-8')).hexdigest())

def _aware(value: datetime | None) -> datetime:
    stamp = value or datetime.now(timezone.utc)
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise P20ReportError('P20_TIMEZONE_REQUIRED', 'timestamps must be timezone-aware')
    return stamp

def _tenant(principal: Principal) -> str:
    if principal.tenant_id is not None:
        return f'id:{principal.tenant_id}'
    if principal.tenant_slug:
        return f'slug:{principal.tenant_slug}'
    raise P20ReportError('P20_TENANT_REQUIRED', 'P20 requires explicit tenant binding')

def _subject(principal: Principal) -> str:
    value = str(principal.user_id).strip()
    if not value:
        raise P20ReportError('P20_PRINCIPAL_REQUIRED', 'P20 requires explicit principal')
    return value

def _analytical_requirement_ids(brief) -> tuple[str, ...]:
    return tuple(item.goal_id for item in brief.questions)

def _numeric_row_values(payload: Any) -> tuple[tuple[str, int | float], ...]:
    if not isinstance(payload, dict):
        return ()
    data = payload.get('data')
    if not isinstance(data, dict):
        return ()
    rows = data.get('rows')
    if not isinstance(rows, list):
        return ()
    found: list[tuple[str, int | float]] = []
    for row_index, row in enumerate(rows):
        if not isinstance(row, list):
            continue
        for column_index, value in enumerate(row):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                continue
            found.append((f'data.rows.{row_index}.{column_index}', value))
    return tuple(found)

def _path_value(value: Any, path: str, *, code: str) -> Any:
    current = value
    for token in path.split('.'):
        if not token:
            raise P20ReportError(code, path)
        if isinstance(current, list):
            if not token.isdigit():
                raise P20ReportError(code, path)
            index = int(token)
            if index >= len(current):
                raise P20ReportError(code, path)
            current = current[index]
        elif isinstance(current, dict):
            if token not in current:
                raise P20ReportError(code, path)
            current = current[token]
        else:
            raise P20ReportError(code, path)
    return current

def _json_object(raw: str | None, *, code: str) -> Any:
    if raw is None:
        raise P20ReportError(code, 'source payload is absent')
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise P20ReportError(code, 'source payload is invalid JSON') from exc

def _render_scalar(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False)

def stable_statement_id(value: Any) -> str:
    return 'p20s_' + _canonical_json(value, code='P20_STATEMENT_ID_NOT_CANONICAL')[1][:24]

def stable_limitation_id(value: Any) -> str:
    return 'p20l_' + _canonical_json(value, code='P20_LIMITATION_ID_NOT_CANONICAL')[1][:24]

class ReportClaimGate:
    """Deterministic publication legality over exact upstream authority."""

    def __init__(self, *, research_store: ResearchSessionStore, db_engine=None) -> None:
        self._research = research_store
        self._engine = db_engine or control_plane_engine
        self._claims = ClaimLineageStore(research_store=research_store, db_engine=self._engine)
        self._p19 = HypothesisRootCauseStore(research_store=research_store, db_engine=self._engine)

    def _session(self, session_id: str, principal: Principal):
        try:
            session = self._research.load(session_id, tenant=_tenant(principal), principal=_subject(principal))
        except ResearchPersistenceError as exc:
            raise P20ReportError('P20_RESEARCH_SESSION_SCOPE_INVALID', exc.code) from exc
        if session.accepted_brief is None:
            raise P20ReportError('P20_ACCEPTED_BRIEF_REQUIRED', 'P20 never reparses the original user prompt')
        mandatory = _analytical_requirement_ids(session.accepted_brief)
        obligation_map = {item.obligation_id: item for item in session.obligations}
        if not mandatory or tuple(obligation_map) != mandatory:
            raise P20ReportError('P20_MANDATORY_OBLIGATION_AUTHORITY_MISMATCH', 'P14 execution obligations must exactly equal accepted analytical Research question ids')
        if not set(mandatory).issubset(set(session.accepted_brief.must_requirement_ids)):
            raise P20ReportError('P20_MANDATORY_OBLIGATION_AUTHORITY_MISMATCH', 'analytical Research requirements left accepted USER_MUST authority')
        if any((obligation_map[oid].state not in {ObligationState.VERIFIED, ObligationState.LIMITED} for oid in mandatory)):
            raise P20ReportError('P20_RESEARCH_SESSION_NOT_SEALED', 'analytical Research obligation remains non-terminal')
        if session.stopping.status not in {StoppingStatus.COMPLETE, StoppingStatus.PARTIAL}:
            raise P20ReportError('P20_RESEARCH_SESSION_NOT_SEALED', session.stopping.status.value)
        return (session, mandatory)

    @staticmethod
    def _source_key(ref: SourceReference) -> str:
        return _canonical_json(ref.model_dump(mode='json'), code='P20_SOURCE_REF_NOT_CANONICAL')[0]

    def _source_snapshot(self, *, session, ref: SourceReference, principal: Principal) -> dict[str, Any]:
        if ref.obligation_id not in {item.obligation_id for item in session.obligations}:
            raise P20ReportError('P20_SOURCE_OBLIGATION_INVALID', ref.obligation_id)
        authority_fingerprint: str
        with Session(self._engine) as db:
            if ref.source_kind == ReportSourceKind.P14_EVIDENCE:
                rows = tuple(db.exec(select(ResearchExecutionLink).where(ResearchExecutionLink.session_id == session.session_id).where(ResearchExecutionLink.obligation_id == ref.obligation_id).where(ResearchExecutionLink.evidence_id == ref.source_ref).where(ResearchExecutionLink.status == 'VERIFIED')).all())
                if len(rows) != 1:
                    raise P20ReportError('P20_EVIDENCE_SOURCE_NOT_FOUND', ref.source_ref)
                row = rows[0]
                if row.receipt_id != ref.source_receipt_id:
                    raise P20ReportError('P20_EVIDENCE_RECEIPT_MISMATCH', ref.source_ref)
                if not any((item.evidence_id == ref.source_ref and item.receipt_id == ref.source_receipt_id and (item.obligation_id == ref.obligation_id) for item in session.evidence_refs)):
                    raise P20ReportError('P20_EVIDENCE_NOT_IN_RESEARCH_AUTHORITY', ref.source_ref)
                authority_fingerprint = _canonical_json({'evidence_id': row.evidence_id, 'receipt_id': row.receipt_id, 'query_fingerprint': row.native_query_fingerprint, 'result_hash': row.result_hash, 'status': row.status}, code='P20_EVIDENCE_SOURCE_NOT_CANONICAL')[1]
            elif ref.source_kind == ReportSourceKind.P15_MATERIAL:
                row = db.get(ResearchExplorationMaterial, ref.source_ref)
                if row is None:
                    raise P20ReportError('P20_MATERIAL_SOURCE_NOT_FOUND', ref.source_ref)
                if row.session_id != session.session_id or row.obligation_id != ref.obligation_id or row.epistemic_state != 'RESEARCH_MATERIAL':
                    raise P20ReportError('P20_MATERIAL_SOURCE_SCOPE_MISMATCH', ref.source_ref)
                authority_fingerprint = _canonical_json({'lead_id': row.lead_id, 'query_fingerprint': row.query_fingerprint, 'payload_fingerprint': row.payload_fingerprint, 'epistemic_state': row.epistemic_state}, code='P20_MATERIAL_SOURCE_NOT_CANONICAL')[1]
            elif ref.source_kind == ReportSourceKind.P17_REASONING_STEP:
                row = db.get(ResearchReasoningStepRecord, ref.source_ref)
                if row is None:
                    raise P20ReportError('P20_P17_SOURCE_NOT_FOUND', ref.source_ref)
                if row.session_id != session.session_id or row.parent_obligation_id != ref.obligation_id:
                    raise P20ReportError('P20_P17_SOURCE_SCOPE_MISMATCH', ref.source_ref)
                authority_fingerprint = _canonical_json({'step_id': row.step_id, 'proposal_fingerprint': row.proposal_fingerprint, 'status': row.status, 'result_refs_json': row.result_refs_json}, code='P20_P17_SOURCE_NOT_CANONICAL')[1]
            elif ref.source_kind == ReportSourceKind.P18_POLICY_USE:
                row = db.get(BusinessRelationshipPolicyUseRecord, ref.source_ref)
                if row is None:
                    raise P20ReportError('P20_P18_SOURCE_NOT_FOUND', ref.source_ref)
                if row.research_session_id != session.session_id or row.obligation_id != ref.obligation_id:
                    raise P20ReportError('P20_P18_SOURCE_SCOPE_MISMATCH', ref.source_ref)
                authority_fingerprint = _canonical_json({'policy_use_id': row.policy_use_id, 'requirement_fingerprint': row.requirement_fingerprint, 'policy_id': row.policy_id, 'policy_fingerprint': row.policy_fingerprint, 'resolution_status': row.resolution_status, 'limitation_code': row.limitation_code}, code='P20_P18_SOURCE_NOT_CANONICAL')[1]
            elif ref.source_kind == ReportSourceKind.P16_CLAIM:
                claim = self._claims.load_claim(session_id=session.session_id, claim_id=ref.source_ref, principal=principal)
                if claim.obligation_id != ref.obligation_id:
                    raise P20ReportError('P20_CLAIM_SOURCE_SCOPE_MISMATCH', ref.source_ref)
                authority_fingerprint = _canonical_json({'claim_fingerprint': claim.claim_fingerprint, 'epistemic_state': claim.epistemic_state.value, 'links': [item.model_dump(mode='json') for item in claim.evidence_links]}, code='P20_CLAIM_SOURCE_NOT_CANONICAL')[1]
            elif ref.source_kind == ReportSourceKind.P19_ASSESSMENT:
                assessment = self._p19.load_assessment(assessment_id=ref.source_ref, principal=principal)
                if assessment.research_session_id != session.session_id or assessment.obligation_id != ref.obligation_id:
                    raise P20ReportError('P20_P19_SOURCE_SCOPE_MISMATCH', ref.source_ref)
                authority_fingerprint = assessment.assessment_fingerprint
            else:
                raise P20ReportError('P20_SOURCE_KIND_UNSUPPORTED', ref.source_kind.value)
        return {'source': ref.model_dump(mode='json'), 'authority_fingerprint': authority_fingerprint}

    def _payload_for_numeric_source(self, *, session, ref: SourceReference) -> Any:
        with Session(self._engine) as db:
            if ref.source_kind == ReportSourceKind.P14_EVIDENCE:
                rows = tuple(db.exec(select(ResearchExecutionLink).where(ResearchExecutionLink.session_id == session.session_id).where(ResearchExecutionLink.obligation_id == ref.obligation_id).where(ResearchExecutionLink.evidence_id == ref.source_ref).where(ResearchExecutionLink.status == 'VERIFIED')).all())
                if len(rows) != 1 or rows[0].receipt_id != ref.source_receipt_id:
                    raise P20ReportError('P20_NUMERIC_SOURCE_NOT_FOUND', ref.source_ref)
                return _json_object(rows[0].native_result_json, code='P20_NUMERIC_SOURCE_PAYLOAD_INVALID')
            if ref.source_kind == ReportSourceKind.P15_MATERIAL:
                row = db.get(ResearchExplorationMaterial, ref.source_ref)
                if row is None or row.session_id != session.session_id or row.obligation_id != ref.obligation_id:
                    raise P20ReportError('P20_NUMERIC_SOURCE_NOT_FOUND', ref.source_ref)
                return _json_object(row.native_payload_json, code='P20_NUMERIC_SOURCE_PAYLOAD_INVALID')
        raise P20ReportError('P20_NUMERIC_SOURCE_KIND_INVALID', ref.source_kind.value)

    @staticmethod
    def _find_one(statement: ReportStatement, kind: ReportSourceKind) -> SourceReference:
        refs = tuple((ref for ref in statement.source_refs if ref.source_kind == kind))
        if len(refs) != 1:
            raise P20ReportError('P20_STATEMENT_SOURCE_CARDINALITY_INVALID', f'{statement.statement_kind.value}:{kind.value}')
        return refs[0]

    def _load_hypothesis(self, *, session, obligation_id: str, hypothesis_id: str):
        with Session(self._engine) as db:
            row = db.get(HypothesisRecord, hypothesis_id)
            if row is None:
                raise P20ReportError('P20_HYPOTHESIS_NOT_FOUND', hypothesis_id)
            if row.research_session_id != session.session_id or row.obligation_id != obligation_id or row.tenant_binding != session.tenant_binding or (row.semantic_context_version != session.context_version):
                raise P20ReportError('P20_HYPOTHESIS_SCOPE_MISMATCH', hypothesis_id)
            return row

    @staticmethod
    def _canonical_statement(statement: ReportStatement, text: str) -> ReportStatement:
        if statement.text is not None and statement.text != text:
            raise P20ReportError('P20_TEXT_NOT_CANONICAL', statement.statement_id)
        return statement.model_copy(update={'text': text})

    def _numeric_statement(self, *, session, statement: ReportStatement, principal: Principal) -> ReportStatement:
        numeric_refs = tuple((ref for ref in statement.source_refs if ref.source_kind in {ReportSourceKind.P14_EVIDENCE, ReportSourceKind.P15_MATERIAL} and ref.source_path is not None))
        if len(numeric_refs) != 1:
            raise P20ReportError('P20_NUMERIC_PROVENANCE_REQUIRED', statement.statement_id)
        ref = numeric_refs[0]
        payload = self._payload_for_numeric_source(session=session, ref=ref)
        assert ref.source_path is not None
        value = _path_value(payload, ref.source_path, code='P20_NUMERIC_SOURCE_PATH_INVALID')
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise P20ReportError('P20_NUMERIC_SOURCE_NOT_NUMERIC', ref.source_path)
        allowed = {'value', 'unit'}
        if set(statement.payload) - allowed or statement.payload.get('value') != value:
            raise P20ReportError('P20_NUMERIC_VALUE_MISMATCH', statement.statement_id)
        unit = None
        if ref.source_unit_path is not None:
            unit = _path_value(payload, ref.source_unit_path, code='P20_NUMERIC_UNIT_PATH_INVALID')
            if not isinstance(unit, str) or not unit:
                raise P20ReportError('P20_NUMERIC_UNIT_INVALID', ref.source_unit_path)
            if statement.payload.get('unit') != unit:
                raise P20ReportError('P20_NUMERIC_UNIT_MISMATCH', statement.statement_id)
        elif 'unit' in statement.payload:
            raise P20ReportError('P20_NUMERIC_UNIT_PROVENANCE_REQUIRED', statement.statement_id)
        if ref.source_kind == ReportSourceKind.P15_MATERIAL:
            p19_ref = self._find_one(statement, ReportSourceKind.P19_ASSESSMENT)
            assessment = self._p19.load_assessment(assessment_id=p19_ref.source_ref, principal=principal)
            retained = False
            for candidate in assessment.candidates:
                for provenance in candidate.numeric_provenance:
                    if provenance.source_kind == GroundingSourceKind.P15_MATERIAL and provenance.source_ref == ref.source_ref and (provenance.source_path == ref.source_path):
                        retained = True
                        break
                if retained:
                    break
            if not retained:
                raise P20ReportError('P20_P15_NUMERIC_NOT_GOVERNED_BY_P19', ref.source_ref)
        if statement.upstream_epistemic_ceiling != 'EXACT_GOVERNED_NUMERIC':
            raise P20ReportError('P20_NUMERIC_CEILING_MISMATCH', statement.statement_id)
        text = f'Numeric result: {_render_scalar(value)}'
        if unit is not None:
            text += f' {unit}'
        return self._canonical_statement(statement, text)

    def _analytical_fact(self, *, session, statement: ReportStatement, principal: Principal) -> ReportStatement:
        ref = self._find_one(statement, ReportSourceKind.P16_CLAIM)
        claim = self._claims.load_claim(session_id=session.session_id, claim_id=ref.source_ref, principal=principal)
        expected_payload = {'claim_id': claim.claim_id, 'epistemic_state': claim.epistemic_state.value}
        if statement.payload != expected_payload:
            raise P20ReportError('P20_CLAIM_PAYLOAD_MISMATCH', statement.statement_id)
        if statement.upstream_epistemic_ceiling != claim.epistemic_state.value:
            raise P20ReportError('P20_CLAIM_CEILING_MISMATCH', statement.statement_id)
        if claim.epistemic_state == ClaimEpistemicState.SUPPORTED:
            text = claim.claim_text
        else:
            text = f'{claim.epistemic_state.value}: {claim.claim_text}'
        return self._canonical_statement(statement, text)

    def _p19_statement(self, *, session, statement: ReportStatement, principal: Principal) -> ReportStatement:
        ref = self._find_one(statement, ReportSourceKind.P19_ASSESSMENT)
        assessment = self._p19.load_assessment(assessment_id=ref.source_ref, principal=principal)
        candidate_map = {item.hypothesis_id: item for item in assessment.candidates}
        if statement.statement_kind in {ReportStatementKind.CAUSAL, ReportStatementKind.ROOT_CAUSE}:
            if set(statement.payload) != {'hypothesis_id'}:
                raise P20ReportError('P20_P19_PAYLOAD_INVALID', statement.statement_id)
            hid = statement.payload['hypothesis_id']
            if not isinstance(hid, str) or hid not in candidate_map:
                raise P20ReportError('P20_P19_HYPOTHESIS_INVALID', statement.statement_id)
            candidate = candidate_map[hid]
            hypothesis = self._load_hypothesis(session=session, obligation_id=ref.obligation_id, hypothesis_id=hid)
            if statement.statement_kind == ReportStatementKind.CAUSAL:
                if candidate.disposition != HypothesisDisposition.RETAINED or candidate.causal_qualification != CausalQualification.DEFENSIBLE_CAUSAL_CONCLUSION or candidate.evidence_strength not in {EvidenceStrength.STRONG, EvidenceStrength.MODERATE} or candidate.identification_limitations or (not candidate.causal_identification_refs):
                    raise P20ReportError('P20_CAUSAL_AUTHORITY_INSUFFICIENT', hid)
                if statement.upstream_epistemic_ceiling != CausalQualification.DEFENSIBLE_CAUSAL_CONCLUSION.value:
                    raise P20ReportError('P20_CAUSAL_CEILING_MISMATCH', statement.statement_id)
                return self._canonical_statement(statement, f'Causal conclusion: {hypothesis.statement}')
            if assessment.aggregate_outcome != AggregateOutcome.ROOT_CAUSE_ESTABLISHED or hid not in assessment.root_cause_hypothesis_ids:
                raise P20ReportError('P20_ROOT_CAUSE_NOT_ESTABLISHED', hid)
            if statement.upstream_epistemic_ceiling != AggregateOutcome.ROOT_CAUSE_ESTABLISHED.value:
                raise P20ReportError('P20_ROOT_CAUSE_CEILING_MISMATCH', statement.statement_id)
            return self._canonical_statement(statement, f'Root cause established: {hypothesis.statement}')
        if statement.statement_kind == ReportStatementKind.CONTRIBUTION:
            if set(statement.payload) != {'candidate_hypothesis_ids'}:
                raise P20ReportError('P20_CONTRIBUTION_PAYLOAD_INVALID', statement.statement_id)
            raw_ids = statement.payload['candidate_hypothesis_ids']
            if not isinstance(raw_ids, list) or any((not isinstance(x, str) for x in raw_ids)):
                raise P20ReportError('P20_CONTRIBUTION_IDS_INVALID', statement.statement_id)
            governed = tuple((item.hypothesis_id for item in assessment.candidates if item.disposition == HypothesisDisposition.RETAINED and item.contribution_class in {ContributionClass.DOMINANT, ContributionClass.MATERIAL}))
            if tuple(raw_ids) != governed or not governed:
                raise P20ReportError('P20_CONTRIBUTION_SET_MISMATCH', statement.statement_id)
            if assessment.aggregate_outcome == AggregateOutcome.MULTIPLE_MATERIAL_CONTRIBUTORS and len(governed) < 2:
                raise P20ReportError('P20_MULTIPLE_CONTRIBUTORS_COLLAPSED', statement.statement_id)
            if statement.upstream_epistemic_ceiling != assessment.aggregate_outcome.value:
                raise P20ReportError('P20_CONTRIBUTION_CEILING_MISMATCH', statement.statement_id)
            parts = []
            for hid in governed:
                candidate = candidate_map[hid]
                hypothesis = self._load_hypothesis(session=session, obligation_id=ref.obligation_id, hypothesis_id=hid)
                parts.append(f'{hypothesis.statement} [{candidate.contribution_class.value}; evidence={candidate.evidence_strength.value}]')
            return self._canonical_statement(statement, 'Contributors: ' + '; '.join(parts))
        if statement.statement_kind == ReportStatementKind.UNCERTAINTY:
            if statement.payload:
                raise P20ReportError('P20_UNCERTAINTY_PAYLOAD_INVALID', statement.statement_id)
            if assessment.aggregate_outcome != AggregateOutcome.NO_DEFENSIBLE_ROOT_CAUSE_ESTABLISHED:
                raise P20ReportError('P20_UNCERTAINTY_OUTCOME_MISMATCH', statement.statement_id)
            if statement.upstream_epistemic_ceiling != assessment.aggregate_outcome.value:
                raise P20ReportError('P20_UNCERTAINTY_CEILING_MISMATCH', statement.statement_id)
            return self._canonical_statement(statement, 'No defensible root cause established.')
        raise P20ReportError('P20_P19_STATEMENT_KIND_INVALID', statement.statement_kind.value)

    def _validate_statement(self, *, session, statement: ReportStatement, limitations: dict[str, ReportLimitation], principal: Principal) -> ReportStatement:
        mandatory = set(_analytical_requirement_ids(session.accepted_brief))
        if not set(statement.obligation_refs).issubset(mandatory):
            raise P20ReportError('P20_STATEMENT_OBLIGATION_INVALID', statement.statement_id)
        if any((ref.obligation_id not in statement.obligation_refs for ref in statement.source_refs)):
            raise P20ReportError('P20_STATEMENT_SOURCE_SCOPE_INVALID', statement.statement_id)
        if not set(statement.limitation_refs).issubset(limitations):
            raise P20ReportError('P20_STATEMENT_LIMITATION_UNKNOWN', statement.statement_id)
        for ref in statement.source_refs:
            self._source_snapshot(session=session, ref=ref, principal=principal)
        if statement.statement_kind == ReportStatementKind.NUMERIC:
            return self._numeric_statement(session=session, statement=statement, principal=principal)
        if statement.statement_kind == ReportStatementKind.ANALYTICAL_FACT:
            return self._analytical_fact(session=session, statement=statement, principal=principal)
        if statement.statement_kind in {ReportStatementKind.CAUSAL, ReportStatementKind.ROOT_CAUSE, ReportStatementKind.CONTRIBUTION, ReportStatementKind.UNCERTAINTY}:
            return self._p19_statement(session=session, statement=statement, principal=principal)
        if statement.statement_kind == ReportStatementKind.LIMITATION:
            if set(statement.payload) != {'limitation_id'}:
                raise P20ReportError('P20_LIMITATION_PAYLOAD_INVALID', statement.statement_id)
            lid = statement.payload['limitation_id']
            limitation = limitations.get(lid)
            if limitation is None or limitation.obligation_id not in statement.obligation_refs:
                raise P20ReportError('P20_LIMITATION_REF_INVALID', statement.statement_id)
            if statement.upstream_epistemic_ceiling != 'LIMITATION':
                raise P20ReportError('P20_LIMITATION_CEILING_MISMATCH', statement.statement_id)
            return self._canonical_statement(statement, f'Limitation: {limitation.detail}')
        if statement.statement_kind == ReportStatementKind.CONTEXT:
            if statement.source_refs:
                raise P20ReportError('P20_CONTEXT_SOURCE_FORBIDDEN', statement.statement_id)
            if set(statement.payload) != {'text'} or not isinstance(statement.payload['text'], str):
                raise P20ReportError('P20_CONTEXT_PAYLOAD_INVALID', statement.statement_id)
            if statement.upstream_epistemic_ceiling != 'CONTEXT_ONLY':
                raise P20ReportError('P20_CONTEXT_CEILING_MISMATCH', statement.statement_id)
            return self._canonical_statement(statement, statement.payload['text'])
        raise P20ReportError('P20_STATEMENT_KIND_UNSUPPORTED', statement.statement_kind.value)

    def validate(self, *, draft: ReportDraft, principal: Principal):
        session, mandatory = self._session(draft.research_session_id, principal)
        coverage_map = {item.obligation_id: item for item in draft.coverage}
        if len(coverage_map) != len(draft.coverage) or set(coverage_map) != set(mandatory):
            raise P20ReportError('P20_USER_MUST_COVERAGE_INCOMPLETE', 'every accepted analytical Research requirement must have exactly one report-content coverage entry')
        limitation_map = {item.limitation_id: item for item in draft.limitations}
        if len(limitation_map) != len(draft.limitations):
            raise P20ReportError('P20_LIMITATION_ID_DUPLICATE', draft.report_key)
        for limitation in draft.limitations:
            if limitation.obligation_id not in set(mandatory):
                raise P20ReportError('P20_LIMITATION_OBLIGATION_INVALID', limitation.limitation_id)
            for ref in limitation.source_refs:
                if ref.obligation_id != limitation.obligation_id:
                    raise P20ReportError('P20_LIMITATION_SOURCE_SCOPE_INVALID', limitation.limitation_id)
                self._source_snapshot(session=session, ref=ref, principal=principal)
        statement_map = {item.statement_id: item for item in draft.statements}
        if len(statement_map) != len(draft.statements):
            raise P20ReportError('P20_STATEMENT_ID_DUPLICATE', draft.report_key)
        approved = tuple((self._validate_statement(session=session, statement=item, limitations=limitation_map, principal=principal) for item in draft.statements))
        approved_map = {item.statement_id: item for item in approved}
        covered_limitation_ids: set[str] = set()
        for oid in mandatory:
            entry = coverage_map[oid]
            if entry.coverage_status == CoverageStatus.REPRESENTED:
                for sid in entry.statement_ids:
                    statement = approved_map.get(sid)
                    if statement is None or oid not in statement.obligation_refs:
                        raise P20ReportError('P20_USER_MUST_STATEMENT_INVALID', f'{oid}:{sid}')
            else:
                for lid in entry.limitation_ids:
                    limitation = limitation_map.get(lid)
                    if limitation is None or limitation.obligation_id != oid:
                        raise P20ReportError('P20_USER_MUST_LIMITATION_INVALID', f'{oid}:{lid}')
                    covered_limitation_ids.add(lid)
        for statement in approved:
            for oid in statement.obligation_refs:
                entry = coverage_map[oid]
                if entry.coverage_status != CoverageStatus.REPRESENTED or statement.statement_id not in entry.statement_ids:
                    raise P20ReportError('P20_STATEMENT_NOT_ACCOUNTED', statement.statement_id)
        referenced_limitations = covered_limitation_ids | {lid for statement in approved for lid in statement.limitation_refs}
        if referenced_limitations != set(limitation_map):
            raise P20ReportError('P20_LIMITATION_NOT_ACCOUNTED', draft.report_key)
        source_by_key: dict[str, SourceReference] = {}
        for statement in approved:
            for ref in statement.source_refs:
                source_by_key[self._source_key(ref)] = ref
        for limitation in draft.limitations:
            for ref in limitation.source_refs:
                source_by_key[self._source_key(ref)] = ref
        sources = tuple((source_by_key[key] for key in sorted(source_by_key)))
        snapshots = tuple((self._source_snapshot(session=session, ref=ref, principal=principal) for ref in sources))
        source_set_identity = {'research_authority_id': session.authority_id, 'research_session_id': session.session_id, 'semantic_context_version': session.context_version, 'mandatory_obligation_ids': list(mandatory), 'sources': list(snapshots)}
        source_set_fingerprint = _canonical_json(source_set_identity, code='P20_SOURCE_SET_NOT_CANONICAL')[1]
        return (session, mandatory, approved, sources, source_set_fingerprint)

class ReportDocumentStore:
    """Single durable P20 owner for immutable ReportDocument snapshots."""

    def __init__(self, *, research_store: ResearchSessionStore, db_engine=None) -> None:
        self._research = research_store
        self._engine = db_engine or control_plane_engine
        self._gate = ReportClaimGate(research_store=research_store, db_engine=self._engine)

    def draft_from_governed_research(
        self,
        *,
        research_session_id: str,
        report_key: str,
        principal: Principal,
        explicit_limitations: tuple[ReportLimitation, ...] = (),
    ) -> ReportDraft:
        """Project report content from terminal analytical authority only.

        Presentation deliverables are fulfilled by the sealed report at Product Composition;
        they are never P20 content-coverage obligations.
        """
        session, mandatory = self._gate._session(research_session_id, principal)
        explicit_by_obligation: dict[str, ReportLimitation] = {}
        for limitation in explicit_limitations:
            if limitation.obligation_id not in set(mandatory):
                raise P20ReportError('P20_LIMITATION_OBLIGATION_INVALID', limitation.limitation_id)
            if limitation.obligation_id in explicit_by_obligation:
                raise P20ReportError('P20_LIMITATION_OBLIGATION_DUPLICATE', limitation.obligation_id)
            explicit_by_obligation[limitation.obligation_id] = limitation

        obligation_map = {item.obligation_id: item for item in session.obligations}
        research_limitations = {
            item.limitation_id: item
            for item in session.limitations
        }
        coverage: list[CoverageEntry] = []
        statements: list[ReportStatement] = []
        limitations: list[ReportLimitation] = []

        for obligation_id in mandatory:
            explicit = explicit_by_obligation.get(obligation_id)
            if explicit is not None:
                limitations.append(explicit)
                coverage.append(
                    CoverageEntry(
                        obligation_id=obligation_id,
                        coverage_status=CoverageStatus.LIMITED,
                        limitation_ids=(explicit.limitation_id,),
                    )
                )
                continue

            obligation = obligation_map[obligation_id]
            if obligation.state == ObligationState.LIMITED:
                owned = tuple(
                    research_limitations[lid]
                    for lid in obligation.limitation_refs
                    if lid in research_limitations
                )
                if not owned:
                    raise P20ReportError(
                        'P20_LIMITED_OBLIGATION_DETAIL_REQUIRED',
                        obligation_id,
                    )
                ids: list[str] = []
                for item in owned:
                    limitation_id = stable_limitation_id(
                        {
                            'session_id': session.session_id,
                            'obligation_id': obligation_id,
                            'research_limitation_id': item.limitation_id,
                            'code': item.code,
                            'detail': item.detail,
                        }
                    )
                    limitation = ReportLimitation(
                        limitation_id=limitation_id,
                        obligation_id=obligation_id,
                        code=item.code,
                        detail=item.detail,
                    )
                    limitations.append(limitation)
                    ids.append(limitation_id)
                coverage.append(
                    CoverageEntry(
                        obligation_id=obligation_id,
                        coverage_status=CoverageStatus.LIMITED,
                        limitation_ids=tuple(ids),
                    )
                )
                continue

            approved_ids: list[str] = []
            for evidence in (
                item for item in session.evidence_refs
                if item.obligation_id == obligation_id
            ):
                with Session(self._engine) as db:
                    rows = tuple(
                        db.exec(
                            select(ResearchExecutionLink)
                            .where(ResearchExecutionLink.session_id == session.session_id)
                            .where(ResearchExecutionLink.obligation_id == obligation_id)
                            .where(ResearchExecutionLink.evidence_id == evidence.evidence_id)
                            .where(ResearchExecutionLink.receipt_id == evidence.receipt_id)
                            .where(ResearchExecutionLink.status == 'VERIFIED')
                        ).all()
                    )
                if len(rows) != 1:
                    continue
                payload = _json_object(
                    rows[0].native_result_json,
                    code='P20_NUMERIC_SOURCE_PAYLOAD_INVALID',
                )
                for source_path, value in _numeric_row_values(payload):
                    source = SourceReference(
                        source_kind=ReportSourceKind.P14_EVIDENCE,
                        source_ref=evidence.evidence_id,
                        source_receipt_id=evidence.receipt_id,
                        obligation_id=obligation_id,
                        source_path=source_path,
                    )
                    statement_id = stable_statement_id(
                        {
                            'kind': ReportStatementKind.NUMERIC.value,
                            'source': source.model_dump(mode='json'),
                            'value': value,
                        }
                    )
                    statements.append(
                        ReportStatement(
                            statement_id=statement_id,
                            statement_kind=ReportStatementKind.NUMERIC,
                            source_refs=(source,),
                            obligation_refs=(obligation_id,),
                            upstream_epistemic_ceiling='EXACT_GOVERNED_NUMERIC',
                            payload={'value': value},
                        )
                    )
                    approved_ids.append(statement_id)

            if approved_ids:
                coverage.append(
                    CoverageEntry(
                        obligation_id=obligation_id,
                        coverage_status=CoverageStatus.REPRESENTED,
                        statement_ids=tuple(dict.fromkeys(approved_ids)),
                    )
                )
                continue

            limitation_id = stable_limitation_id(
                {
                    'session_id': session.session_id,
                    'obligation_id': obligation_id,
                    'code': 'P20_NO_GOVERNED_PUBLISHABLE_FACT',
                }
            )
            limitation = ReportLimitation(
                limitation_id=limitation_id,
                obligation_id=obligation_id,
                code='P20_NO_GOVERNED_PUBLISHABLE_FACT',
                detail=(
                    'The analytical requirement is terminal, but its governed upstream '
                    'artifacts contain no exact fact eligible under the existing P20 '
                    'publication contracts.'
                ),
            )
            limitations.append(limitation)
            coverage.append(
                CoverageEntry(
                    obligation_id=obligation_id,
                    coverage_status=CoverageStatus.LIMITED,
                    limitation_ids=(limitation_id,),
                )
            )

        return ReportDraft(
            research_session_id=research_session_id,
            report_key=report_key,
            coverage=tuple(coverage),
            statements=tuple(statements),
            limitations=tuple(limitations),
        )

    @staticmethod
    def _hydrate(row: ReportDocumentRecord) -> ReportDocument:
        try:
            coverage = json.loads(row.coverage_json)
            statements = json.loads(row.statements_json)
            sources = json.loads(row.source_refs_json)
            limitations = json.loads(row.limitations_json)
        except json.JSONDecodeError as exc:
            raise P20ReportError('P20_REPORT_PERSISTENCE_INVALID', row.report_id) from exc
        if not all((isinstance(item, list) for item in (coverage, statements, sources, limitations))):
            raise P20ReportError('P20_REPORT_PERSISTENCE_INVALID', row.report_id)
        return ReportDocument(report_id=row.report_id, research_session_id=row.research_session_id, tenant_binding=row.tenant_binding, semantic_context_version=row.semantic_context_version, report_key=row.report_key, revision=row.revision, parent_report_id=row.parent_report_id, coverage=tuple((CoverageEntry.model_validate(item) for item in coverage)), statements=tuple((ReportStatement.model_validate(item) for item in statements)), source_refs=tuple((SourceReference.model_validate(item) for item in sources)), limitations=tuple((ReportLimitation.model_validate(item) for item in limitations)), source_set_fingerprint=row.source_set_fingerprint, report_fingerprint=row.report_fingerprint, created_at=row.created_at)

    def seal(self, *, draft: ReportDraft, principal: Principal, now: datetime | None=None) -> ReportDocument:
        session, mandatory, statements, sources, source_set_fingerprint = self._gate.validate(draft=draft, principal=principal)
        identity = {'research_authority_id': session.authority_id, 'research_session_id': session.session_id, 'tenant_binding': session.tenant_binding, 'semantic_context_version': session.context_version, 'report_key': draft.report_key, 'mandatory_obligation_ids': list(mandatory), 'coverage': [item.model_dump(mode='json') for item in draft.coverage], 'statements': [item.model_dump(mode='json') for item in statements], 'source_refs': [item.model_dump(mode='json') for item in sources], 'limitations': [item.model_dump(mode='json') for item in draft.limitations], 'source_set_fingerprint': source_set_fingerprint}
        _, report_fingerprint = _canonical_json(identity, code='P20_REPORT_NOT_CANONICAL')
        report_id = 'p20r_' + report_fingerprint[:24]
        coverage_json = _canonical_json([item.model_dump(mode='json') for item in draft.coverage], code='P20_COVERAGE_NOT_CANONICAL')[0]
        statements_json = _canonical_json([item.model_dump(mode='json') for item in statements], code='P20_STATEMENTS_NOT_CANONICAL')[0]
        source_refs_json = _canonical_json([item.model_dump(mode='json') for item in sources], code='P20_SOURCES_NOT_CANONICAL')[0]
        limitations_json = _canonical_json([item.model_dump(mode='json') for item in draft.limitations], code='P20_LIMITATIONS_NOT_CANONICAL')[0]
        with Session(self._engine) as db:
            existing = db.get(ReportDocumentRecord, report_id)
            if existing is not None:
                if existing.report_fingerprint != report_fingerprint:
                    raise P20ReportError('P20_REPORT_IDENTITY_CONFLICT', report_id)
                return self._hydrate(existing)
            previous = db.exec(select(ReportDocumentRecord).where(ReportDocumentRecord.research_session_id == session.session_id).where(ReportDocumentRecord.report_key == draft.report_key).order_by(ReportDocumentRecord.revision.desc())).first()
            revision = 1 if previous is None else previous.revision + 1
            parent_report_id = None if previous is None else previous.report_id
            row = ReportDocumentRecord(report_id=report_id, research_session_id=session.session_id, tenant_binding=session.tenant_binding, semantic_context_version=session.context_version, report_key=draft.report_key, revision=revision, parent_report_id=parent_report_id, coverage_json=coverage_json, statements_json=statements_json, source_refs_json=source_refs_json, limitations_json=limitations_json, source_set_fingerprint=source_set_fingerprint, report_fingerprint=report_fingerprint, created_at=_aware(now))
            db.add(row)
            db.commit()
            db.refresh(row)
            return self._hydrate(row)

    def load(self, *, report_id: str, principal: Principal) -> ReportDocument:
        with Session(self._engine) as db:
            row = db.get(ReportDocumentRecord, report_id)
            if row is None:
                raise P20ReportError('P20_REPORT_NOT_FOUND', report_id)
            report = self._hydrate(row)
        try:
            session = self._research.load(report.research_session_id, tenant=_tenant(principal), principal=_subject(principal))
        except ResearchPersistenceError as exc:
            raise P20ReportError('P20_REPORT_SCOPE_INVALID', report_id) from exc
        if session.tenant_binding != report.tenant_binding or session.context_version != report.semantic_context_version:
            raise P20ReportError('P20_REPORT_SCOPE_INVALID', report_id)
        return report

    def currentness(self, *, report_id: str, principal: Principal) -> ReportCurrentness:
        report = self.load(report_id=report_id, principal=principal)
        try:
            session, mandatory = self._gate._session(report.research_session_id, principal)
            snapshots = tuple((self._gate._source_snapshot(session=session, ref=ref, principal=principal) for ref in report.source_refs))
            current = _canonical_json({'research_authority_id': session.authority_id, 'research_session_id': session.session_id, 'semantic_context_version': session.context_version, 'mandatory_obligation_ids': list(mandatory), 'sources': list(snapshots)}, code='P20_SOURCE_SET_NOT_CANONICAL')[1]
        except P20ReportError:
            return ReportCurrentness.STALE_SOURCE_SET
        if current == report.source_set_fingerprint:
            return ReportCurrentness.CURRENT
        return ReportCurrentness.STALE_SOURCE_SET
