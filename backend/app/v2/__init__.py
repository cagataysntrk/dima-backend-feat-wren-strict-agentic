"""Dima V2 conversation/semantic core.

This package is intentionally isolated from the legacy /ask decision graph.
Reusable execution infrastructure may be adapted in, but semantic ownership
must remain inside the V2 contracts.
"""

from app.v2.models import TurnAct, TurnInterpretation

__all__ = ["TurnAct", "TurnInterpretation"]
