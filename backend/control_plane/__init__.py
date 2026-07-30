"""dima control-plane — shared identity/authz core.

ADR-0014 (kimlik/yetki) + ADR-0015 (admin plane). Bu paket **route yaymaz**; yalnız
model + güvenlik + yetki mantığı sunar. Hem public ``app`` hem admin ``admin_app`` bunu
import eder → tek kaynak, drift yok (ADR-0015 Karar 1 değişmezi).

Şema ve izolasyon değişmezleri: ``docs/auth/control-plane-sema.md``.
"""

__all__ = ["__version__"]

__version__ = "0.1.0"
