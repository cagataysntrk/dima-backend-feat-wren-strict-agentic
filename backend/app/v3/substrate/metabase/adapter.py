"""P3 runtime adapter shell.

P3 deliberately stops at the transport/capability boundary. ResolvedAnalyticsIntent →
portable query compilation belongs to P3A/P4 and is not implemented here.
"""

from __future__ import annotations

from typing import Any

from app.v3.substrate.metabase.client import MetabaseAgentClient
from app.v3.substrate.metabase.models import MetabaseCapabilityHandshake


class MetabaseRuntimeAdapter:
    def __init__(self, *, client: MetabaseAgentClient) -> None:
        self._client = client

    def inspect_runtime(
        self,
        *,
        portable_probe_query: dict[str, Any],
    ) -> MetabaseCapabilityHandshake:
        return self._client.startup_handshake(
            portable_probe_query=portable_probe_query,
        )
