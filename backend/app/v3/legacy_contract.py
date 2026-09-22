"""Dima-owned legacy QueryContract compatibility writer for M1.

This writer preserves the certified v2 persistence side effect without giving raw user
language to the analytics substrate. The question is immutable audit context only; it is
never parsed, interpreted, or used to construct analytics semantics.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from app.v2.models import TenantAnalyticsRuntimeV0
from app.v3.analytics_contract import ResolvedAnalyticsIntent
from app.v3.evidence import DimaQueryReceipt


class LegacyQueryContractError(RuntimeError):
    pass


class LegacyV2QueryReceiptWriter:
    """Write the certified v2 QueryContract side effect outside the substrate."""

    def __init__(
        self,
        *,
        contract_store,
        runtime: TenantAnalyticsRuntimeV0,
        session_id: str | None,
        question: str,
    ) -> None:
        if contract_store is None or not callable(
            getattr(contract_store, "record_v2_minimum", None)
        ):
            raise LegacyQueryContractError("strict ContractStore unavailable")
        self._contract_store = contract_store
        self._runtime = runtime
        self._session_id = session_id
        self._question = question

    @staticmethod
    def _query_fingerprint(*, cube_query: dict, sql: str) -> str:
        raw = json.dumps(
            {"cube_query": cube_query, "sql": " ".join(sql.split())},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def _receipt_id(
        *,
        authority_id: str,
        intent_hash: str,
        query_fingerprint: str,
        execution_id: str,
    ) -> str:
        raw = f"{authority_id}\x1f{intent_hash}\x1f{query_fingerprint}\x1f{execution_id}"
        return "dqr_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]

    def record(
        self,
        *,
        intent: ResolvedAnalyticsIntent,
        execution_id: str,
        cube_query: dict,
        sql: str,
        result: dict[str, Any],
        provenance: dict[str, Any],
        substrate: str,
        substrate_runtime_version: str | None,
    ) -> DimaQueryReceipt:
        sealed = self._contract_store.record_v2_minimum(
            session_id=self._session_id,
            question=self._question,
            cube_query=cube_query,
            sql=sql,
            result=result,
            schema_version=self._runtime.mdl_version,
            tenant_id=self._runtime.tenant_id,
            provenance=provenance,
        )
        if not bool(sealed.get("sealed")):
            raise LegacyQueryContractError("QueryContract seal failed")

        query_fingerprint = self._query_fingerprint(
            cube_query=cube_query,
            sql=sql,
        )
        intent_hash = intent.resolved_intent_hash
        return DimaQueryReceipt(
            receipt_id=self._receipt_id(
                authority_id=intent.authority_id,
                intent_hash=intent_hash,
                query_fingerprint=query_fingerprint,
                execution_id=execution_id,
            ),
            authority_id=intent.authority_id,
            projection_hash=intent.projection_hash,
            resolved_intent_hash=intent_hash,
            canonical_query_fingerprint=query_fingerprint,
            canonical_query_representation={
                "cube_query": cube_query,
                "sql": sql,
            },
            principal_fingerprint=intent.principal.fingerprint,
            execution_access_fingerprint=intent.principal.fingerprint,
            semantic_context_version=intent.semantic_context_version,
            substrate=substrate,
            substrate_runtime_version=substrate_runtime_version,
            legacy_query_contract_ref=str(sealed["id"]),
            result_hash=sealed.get("result_hash"),
            row_count=int(result.get("row_count") or 0),
        )
