"""Canonical control-plane audit-chain primitives.

The chain detects record mutation/deletion and concurrent forks. It is intentionally
pure and owns no product/runtime dependency.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

GENESIS = "genesis"

ZINCIR_ALANLARI = (
    "tenant_id",
    "ts",
    "actor_user_id",
    "actor_kind",
    "role_key",
    "action",
    "nl_question",
    "generated_sql",
    "touched_models_json",
    "rows_returned",
    "masked_columns_json",
    "ip",
    "contract_id",
)


def _kanonik(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    iso = getattr(value, "isoformat", None)
    return iso() if callable(iso) else str(value)


def kayit_hash(payload: dict[str, Any], onceki: str | None) -> str:
    govde = {alan: _kanonik(payload.get(alan)) for alan in ZINCIR_ALANLARI}
    govde["_onceki"] = onceki or GENESIS
    ham = json.dumps(
        govde,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(ham.encode("utf-8")).hexdigest()


def zinciri_dogrula(kayitlar: list[dict[str, Any]]) -> list[str]:
    """Return explicit mutation/gap/fork findings; empty means internally coherent."""
    bulgular: list[str] = []
    onceki_hash = GENESIS
    goruldu: dict[str, int] = {}
    for index, kayit in enumerate(kayitlar or []):
        beklenen = kayit_hash(kayit, kayit.get("onceki_kayit_hash"))
        if kayit.get("kayit_hash") and kayit["kayit_hash"] != beklenen:
            bulgular.append(
                f"BOZULMUŞ #{index}: kayıt içeriği hash'iyle uyuşmuyor "
                f"(ts={kayit.get('ts')})"
            )
        bagli = kayit.get("onceki_kayit_hash") or GENESIS
        if bagli != onceki_hash:
            bulgular.append(
                f"KOPUK #{index}: onceki_kayit_hash beklenenle tutmuyor"
            )
        if bagli in goruldu and bagli != GENESIS:
            bulgular.append(
                f"ÇATAL #{index}: {bagli[:12]}… hem #{goruldu[bagli]} hem "
                f"#{index} tarafından izleniyor"
            )
        goruldu[bagli] = index
        onceki_hash = kayit.get("kayit_hash") or beklenen
    return bulgular
