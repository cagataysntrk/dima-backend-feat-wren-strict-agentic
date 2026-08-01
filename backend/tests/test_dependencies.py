"""Bağımlılık sapması regresyon kilidi.

NEDEN VAR (canlı bulgu, 2 Ağustos 2026): `backend/Dockerfile` runtime bağımlılıklarını
`pyproject.toml`'dan türetmiyor, ELLE sayıyor. Bu kopya sapmıştı — `mrml`, `jinja2` ve
`ruamel.yaml` pyproject'te ZORUNLU bildirildiği halde imajda yoktu. Sonucu üründe sessiz
çökmelerdi:

  * `app/email_render.py:48`  → `import mrml`        → HER zamanlanmış rapor e-postası (ADR-0011)
  * `app/mdl_writer.py:19`    → `from ruamel.yaml`   → ölçü terfisi (Faz 2d) + bağlantı
                                                       sihirbazının şema yazımı (ADR-0017)

Hiçbir test bunu yakalamıyordu çünkü bu modülleri kullanan testler zaten koşmuyordu
(test paketi ağ-bağımlı bir embedder indirmesinde asılı kalıyordu — bkz. tests/conftest.py
`DIMA_VQR_EMBEDDER`).

Bu test Docker'dan BAĞIMSIZDIR: pyproject'i tek gerçek kaynak sayar ve her bildirilen
bağımlılığın import edilebildiğini iddia eder. Yeni bir bağımlılık eklenip dağıtım
tarafına yansıtılmazsa CI burada kırılır.
"""

from __future__ import annotations

import importlib
import re
import tomllib
from pathlib import Path

import pytest

_PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"

# Dağıtım adı → import adı (yalnız FARKLI olanlar). Aynı olanlar için eşleme gerekmez.
_IMPORT_NAME = {
    "wrenai": "wren",
    "uvicorn[standard]": "uvicorn",
    "pydantic-settings": "pydantic_settings",
    "argon2-cffi": "argon2",
    "pyjwt": "jwt",
    "psycopg[binary]": "psycopg",
    "ruamel.yaml": "ruamel.yaml",
    "python-multipart": "multipart",
}


def _declared_runtime_deps() -> list[str]:
    data = tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))
    out: list[str] = []
    for spec in data["project"]["dependencies"]:
        # "paket[extra]>=1.2,<2" → "paket[extra]"
        name = re.split(r"[<>=!~;]", spec, maxsplit=1)[0].strip()
        if name:
            out.append(name)
    return out


def test_pyproject_declares_the_deps_the_code_actually_imports() -> None:
    """Kod bu üçünü doğrudan import ediyor; pyproject onları bildirmezse dağıtım tarafı
    (Dockerfile/CI) da bilemez. Sapmanın kök nedeni buydu."""
    declared = {d.lower() for d in _declared_runtime_deps()}
    for needed in ("mrml", "jinja2", "ruamel.yaml"):
        assert needed in declared, (
            f"{needed} pyproject.toml'da bildirilmemiş ama kod onu import ediyor "
            "(app/email_render.py, app/mdl_writer.py)"
        )


@pytest.mark.parametrize("dist", _declared_runtime_deps())
def test_declared_dependency_is_importable(dist: str) -> None:
    """Bildirilen her runtime bağımlılığı bu ortamda GERÇEKTEN kurulu olmalı.

    Bu, Dockerfile'ın elle tutulan listesinin ve CI'ın `pip install -e .[dev]` adımının
    pyproject ile aynı kümeyi kurduğunun tek otomatik kanıtıdır.
    """
    module = _IMPORT_NAME.get(dist.lower(), dist.lower().replace("-", "_"))
    try:
        importlib.import_module(module)
    except ImportError as exc:  # pragma: no cover - hata mesajı asıl değer
        pytest.fail(
            f"pyproject '{dist}' bildiriyor ama '{module}' import edilemiyor: {exc}. "
            "Dağıtım tarafı (backend/Dockerfile 3. adım) pyproject ile sapmış olabilir."
        )
