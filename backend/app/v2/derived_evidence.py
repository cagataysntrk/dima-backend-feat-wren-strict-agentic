"""Day7 deterministic derived-analysis adapters.

These adapters turn VERIFIED governed Evidence into VERIFIED derived Evidence without
executing SQL, creating CubeQuery, minting semantic handles, discovering peers, choosing
time axes or making causal claims.

They deliberately reuse only the pure mathematical primitives already present in Dima:
- app.stats.trend
- app.contribution.contributions
- app.ilkeller.hesapla
"""

from __future__ import annotations

import hashlib
import json
from datetime import date, datetime
from typing import Any, Literal

from pydantic import Field

from app import contribution, ilkeller, stats
from app.v2.models import EvidenceArtifact, FrozenModel, ResearchTask


class DerivedEvidenceError(RuntimeError):
    pass


class TrendDerivedArgs(FrozenModel):
    metric_handle: str = Field(min_length=1)
    time_axis_handle: str = Field(min_length=1)
    ordering: Literal["ASCENDING", "DESCENDING"]
    ordering_provenance_ref: str = Field(min_length=1)
    execution_role: str = Field(default="primary", min_length=1)


class ContributionDerivedArgs(FrozenModel):
    metric_handle: str = Field(min_length=1)
    dimension_handle: str = Field(min_length=1)
    additivity_class: Literal["ADDITIVE"] = "ADDITIVE"
    additivity_provenance_ref: str = Field(min_length=1)
    current_role: str = Field(default="primary", min_length=1)
    reference_role: str = Field(default="comparison_reference", min_length=1)


class PeerCompareDerivedArgs(FrozenModel):
    metric_handle: str = Field(min_length=1)
    dimension_handle: str = Field(min_length=1)
    target_value: str = Field(min_length=1)
    target_provenance_ref: str = Field(min_length=1)
    peer_group_provenance_ref: str = Field(min_length=1)
    execution_role: str = Field(default="primary", min_length=1)


class DerivedEvidenceService:
    """Pure zero-query transformations over governed parent Evidence."""

    @staticmethod
    def _validate_parent(
        *,
        task: ResearchTask,
        parent: EvidenceArtifact,
        required_handles: tuple[str, ...],
    ) -> None:
        if task.origin != "AGENT_DERIVED":
            raise DerivedEvidenceError(
                "derived analytical Evidence requires AGENT_DERIVED ResearchTask"
            )
        if task.parent_task_id != parent.task_id:
            raise DerivedEvidenceError(
                "derived task parent_task_id does not match parent Evidence task"
            )
        if task.trigger_evidence_ref != parent.artifact_id:
            raise DerivedEvidenceError(
                "derived task trigger_evidence_ref does not match parent Evidence"
            )
        if not parent.verified:
            raise DerivedEvidenceError("parent Evidence is not verified")
        if not parent.query_contract_refs:
            raise DerivedEvidenceError(
                "parent Evidence lacks sealed QueryContract provenance"
            )
        undeclared = set(required_handles) - set(task.input_refs)
        if undeclared:
            raise DerivedEvidenceError(
                "derived task did not declare required semantic inputs: "
                + ", ".join(sorted(undeclared))
            )

    @staticmethod
    def _execution(parent: EvidenceArtifact, role: str) -> dict[str, Any]:
        matches = [
            item
            for item in tuple((parent.payload or {}).get("executions") or ())
            if str(item.get("role") or "") == role
        ]
        if len(matches) != 1:
            raise DerivedEvidenceError(
                f"parent Evidence requires exactly one execution role={role!r}; "
                f"found={len(matches)}"
            )
        return matches[0]

    @staticmethod
    def _rows(execution: dict[str, Any]) -> tuple[dict[str, Any], ...]:
        rows = tuple(execution.get("rows") or ())
        if not rows:
            raise DerivedEvidenceError("parent Evidence execution contains no rows")
        if not all(isinstance(row, dict) for row in rows):
            raise DerivedEvidenceError("parent Evidence rows must be mappings")
        return tuple(dict(row) for row in rows)

    @staticmethod
    def _numeric(value: Any, *, field: str) -> float:
        if isinstance(value, bool):
            raise DerivedEvidenceError(f"{field} is not numeric")
        try:
            return float(value)
        except (TypeError, ValueError) as exc:
            raise DerivedEvidenceError(f"{field} is not numeric") from exc

    @staticmethod
    def _order_key(value: Any) -> tuple[str, Any]:
        if isinstance(value, datetime):
            return ("datetime", value.isoformat())
        if isinstance(value, date):
            return ("date", value.isoformat())
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return ("number", float(value))
        if isinstance(value, str) and value.strip():
            # The adapter does not parse natural-language time. A governed execution
            # may expose an already-canonical sortable string such as ISO date/month.
            return ("string", value)
        raise DerivedEvidenceError("time-axis value is not a governed sortable scalar")

    @staticmethod
    def _artifact_id(
        *,
        task: ResearchTask,
        parent: EvidenceArtifact,
        transformation: str,
        args: FrozenModel,
    ) -> str:
        payload = {
            "task_id": task.task_id,
            "parent": parent.artifact_id,
            "transformation": transformation,
            "args": args.model_dump(mode="json"),
        }
        raw = json.dumps(
            payload,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        )
        return "evi_der_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]

    @classmethod
    def _derived(
        cls,
        *,
        task: ResearchTask,
        parent: EvidenceArtifact,
        transformation: Literal["TREND", "CONTRIBUTION", "PEER_COMPARE"],
        args: FrozenModel,
        payload: dict[str, Any],
        limitations: tuple[str, ...] = (),
    ) -> EvidenceArtifact:
        qrefs = tuple(dict.fromkeys(parent.query_contract_refs))
        return EvidenceArtifact(
            artifact_id=cls._artifact_id(
                task=task,
                parent=parent,
                transformation=transformation,
                args=args,
            ),
            task_id=task.task_id,
            obligation_ids=tuple(dict.fromkeys(parent.obligation_ids)),
            query_contract_refs=qrefs,
            evidence_kind="derived_analytical",
            verified=True,
            payload=payload,
            limitations=limitations,
            source_kind="DERIVED_ANALYTICAL",
            parent_evidence_refs=(parent.artifact_id,),
            parent_query_contract_refs=qrefs,
            transformation=transformation,
        )

    def trend(
        self,
        *,
        task: ResearchTask,
        parent: EvidenceArtifact,
        args: TrendDerivedArgs,
    ) -> EvidenceArtifact:
        self._validate_parent(
            task=task,
            parent=parent,
            required_handles=(args.metric_handle, args.time_axis_handle),
        )
        execution = self._execution(parent, args.execution_role)
        rows = self._rows(execution)

        ordered_pairs: list[tuple[tuple[str, Any], float]] = []
        for row in rows:
            if args.time_axis_handle not in row or args.metric_handle not in row:
                raise DerivedEvidenceError(
                    "trend parent row missing governed time-axis or metric column"
                )
            ordered_pairs.append(
                (
                    self._order_key(row[args.time_axis_handle]),
                    self._numeric(
                        row[args.metric_handle],
                        field=args.metric_handle,
                    ),
                )
            )

        time_kinds = {item[0][0] for item in ordered_pairs}
        if len(time_kinds) != 1:
            raise DerivedEvidenceError("trend time-axis values use mixed scalar types")
        times = [item[0][1] for item in ordered_pairs]
        if len(set(times)) != len(times):
            raise DerivedEvidenceError("trend time axis contains duplicate positions")

        if args.ordering == "ASCENDING":
            valid_order = all(a < b for a, b in zip(times, times[1:]))
        else:
            valid_order = all(a > b for a, b in zip(times, times[1:]))
        if not valid_order:
            raise DerivedEvidenceError(
                "trend parent rows do not satisfy declared governed ordering"
            )

        values = [item[1] for item in ordered_pairs]
        result = stats.trend(values)
        if result is None:
            raise DerivedEvidenceError(
                f"trend requires at least {stats.ASGARI_TREND} usable ordered samples"
            )

        return self._derived(
            task=task,
            parent=parent,
            transformation="TREND",
            args=args,
            payload={
                "metric_handle": args.metric_handle,
                "time_axis_handle": args.time_axis_handle,
                "ordering": args.ordering,
                "ordering_provenance_ref": args.ordering_provenance_ref,
                "sample_count": len(values),
                "trend": result,
            },
            limitations=(
                "r2 is goodness-of-fit only; it is not statistical significance or truth confidence",
            ),
        )

    def contribution(
        self,
        *,
        task: ResearchTask,
        parent: EvidenceArtifact,
        args: ContributionDerivedArgs,
    ) -> EvidenceArtifact:
        self._validate_parent(
            task=task,
            parent=parent,
            required_handles=(args.metric_handle, args.dimension_handle),
        )
        current = self._rows(self._execution(parent, args.current_role))
        previous = self._rows(self._execution(parent, args.reference_role))

        def index(rows: tuple[dict[str, Any], ...], label: str) -> dict[str, float]:
            out: dict[str, float] = {}
            for row in rows:
                if args.dimension_handle not in row or args.metric_handle not in row:
                    raise DerivedEvidenceError(
                        f"contribution {label} row missing required dimension/metric column"
                    )
                key = str(row[args.dimension_handle])
                if key in out:
                    raise DerivedEvidenceError(
                        f"contribution {label} rows contain duplicate dimension key: {key}"
                    )
                out[key] = self._numeric(
                    row[args.metric_handle],
                    field=args.metric_handle,
                )
            return out

        cur = index(current, "current")
        prev = index(previous, "reference")
        if set(cur) != set(prev):
            raise DerivedEvidenceError(
                "contribution current/reference dimension sets are not aligned"
            )

        aligned = [
            {
                args.dimension_handle: key,
                args.metric_handle: cur[key],
                f"{args.metric_handle}_gecen": prev[key],
            }
            for key in cur
        ]
        segments = contribution.contributions(
            aligned,
            args.dimension_handle,
            args.metric_handle,
        )
        if not segments:
            raise DerivedEvidenceError("contribution transform produced no segments")

        return self._derived(
            task=task,
            parent=parent,
            transformation="CONTRIBUTION",
            args=args,
            payload={
                "metric_handle": args.metric_handle,
                "dimension_handle": args.dimension_handle,
                "additivity_class": args.additivity_class,
                "additivity_provenance_ref": args.additivity_provenance_ref,
                "segment_count": len(segments),
                "segments": segments,
                "trimmed_segment_count": 0,
                "trimmed_mass_share": 0.0,
                "claim_semantics": "observed_change_decomposition_noncausal",
            },
            limitations=(
                "Contribution decomposes observed change; it does not establish causality",
                "No segments were silently trimmed by the V2 derived transform",
            ),
        )

    def peer_compare(
        self,
        *,
        task: ResearchTask,
        parent: EvidenceArtifact,
        args: PeerCompareDerivedArgs,
    ) -> EvidenceArtifact:
        self._validate_parent(
            task=task,
            parent=parent,
            required_handles=(args.metric_handle, args.dimension_handle),
        )
        rows = self._rows(self._execution(parent, args.execution_role))
        for row in rows:
            if args.dimension_handle not in row or args.metric_handle not in row:
                raise DerivedEvidenceError(
                    "peer comparison parent row missing required dimension/metric column"
                )

        result = ilkeller.hesapla(
            list(rows),
            args.dimension_handle,
            args.metric_handle,
            args.target_value,
        )
        if result is None:
            raise DerivedEvidenceError(
                "peer comparison requires target plus at least two usable governed peers"
            )

        return self._derived(
            task=task,
            parent=parent,
            transformation="PEER_COMPARE",
            args=args,
            payload={
                "metric_handle": args.metric_handle,
                "dimension_handle": args.dimension_handle,
                "target_value": args.target_value,
                "target_provenance_ref": args.target_provenance_ref,
                "peer_group_provenance_ref": args.peer_group_provenance_ref,
                "comparison": result,
                "claim_semantics": "descriptive_peer_comparison_noncausal",
            },
            limitations=(
                "Peer membership is upstream governed input; this transform does not discover peers",
            ),
        )
