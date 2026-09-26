"""Canonical control-plane model-access decision primitive.

This module deliberately contains no SQL parser, Wren adapter, query executor or
runtime wrapper. It only evaluates an already-resolved model-reference set against
an optional configured allowlist.
"""
from __future__ import annotations


class ModelErisimReddi(Exception):
    """Model allowlist denial, distinct from coarse-grained AuthzError."""


def karar(
    referanslar: set[str],
    izinliler: set[str] | None,
) -> tuple[bool, str]:
    """Return deterministic allow/deny decision.

    None means the tenant has no configured model allowlist and coarse-grained
    authorization remains authoritative. An explicit empty set means deny all.
    """
    if izinliler is None:
        return True, "Katman B bu tenant'ta YAPILANDIRILMAMIŞ — Katman A yönetiyor"
    disarida = sorted(referanslar - izinliler)
    if disarida:
        return False, (
            f"allowlist DIŞI model: {disarida} — "
            f"izinli: {sorted(izinliler) or '(boş)'}"
        )
    return True, "allowlist içinde"
