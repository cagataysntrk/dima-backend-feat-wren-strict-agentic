"""In-process login brute-force sınırı (ADR-0015 Karar 5: "JWT auth + rate limit").

Day-1 tek instance → bellek içi kayan pencere yeterli (Redis'e geçiş, refresh
store'la aynı anda düşünülür). Anahtar çağırandan gelir (e-posta ve IP ayrı ayrı
sınırlanır); başarılı girişte sayaç sıfırlanır.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque

from control_plane.config import get_auth_settings


class SlidingWindowLimiter:
    def __init__(self) -> None:
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def _prune(self, key: str, now: float, window: float) -> None:
        q = self._events[key]
        while q and now - q[0] > window:
            q.popleft()

    def blocked(self, key: str) -> bool:
        s = get_auth_settings()
        now = time.monotonic()
        with self._lock:
            self._prune(key, now, s.login_window_seconds)
            return len(self._events[key]) >= s.login_max_attempts

    def failure(self, key: str) -> None:
        s = get_auth_settings()
        now = time.monotonic()
        with self._lock:
            self._prune(key, now, s.login_window_seconds)
            self._events[key].append(now)

    def reset(self, key: str) -> None:
        with self._lock:
            self._events.pop(key, None)

    def clear(self) -> None:
        """Test yardımcıları için tüm durumu sıfırlar."""
        with self._lock:
            self._events.clear()


login_limiter = SlidingWindowLimiter()
