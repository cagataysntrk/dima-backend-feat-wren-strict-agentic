# syntax=docker/dockerfile:1
#
# dima-backend — FastAPI + Wren semantic SQL engine (demo phase: DuckDB, no auth)
#
# IMPORTANT: build context MUST be the parent `dima` repo root (not dima-backend/),
# because the Wren Python package is installed from the sibling submodule
# `dima-wrenai/core/wren`. See railway.json (`dockerfilePath: dima-backend/Dockerfile`).
#
# Why not `pip install wrenai` from PyPI: verified via diff that PyPI wrenai==0.13.0
# differs from the local mirror (21 .py files: connectors, type_mapping, sql_classify).
# The mirror is the tested code, so we install `core/wren` from source. The Rust engine
# binding (`wren_core`) is the prebuilt PyPI wheel `wren-core-py` (no Rust build needed).

# amd64'e SABİTLE: wren-core-py 0.7.2'nin manylinux x86_64 abi3 wheel'i var ama linux-arm64
# wheel'i YOK (arm64'te kaynaktan Rust/maturin derlemesi gerekir, kırılgan ve yavaş). Railway
# zaten amd64 çalışır; sabitleyince hem lokal (Apple Silicon → emülasyon) hem Railway AYNI
# artefaktı üretir, wheel kullanılır, Rust derlemesi olmaz.
FROM --platform=linux/amd64 python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# 1) Pin the Rust engine binding first (prebuilt abi3 Linux wheel — no compiler needed).
#    Doing this before installing `core/wren` means pip sees `wren-core-py>=0.7.1`
#    already satisfied by 0.7.2 and will NOT silently pull a newer build.
RUN pip install "wren-core-py==0.7.2"

# 2) Install wrenai from PyPI since local mirror is not available
RUN pip install "wrenai>=0.13,<0.14"

# 3) Backend runtime deps
RUN pip install \
      "fastapi==0.139.2" \
      "uvicorn[standard]==0.51.0" \
      "anthropic==0.117.0" \
      "openai>=1.0.0" \
      "pydantic-settings==2.14.2" \
      "fastembed==0.8.0" \
      "sqlmodel>=0.0.22" \
      "argon2-cffi>=23.1" \
      "pyjwt>=2.9" \
      "psycopg[binary]>=3.2"

# 4) Application code + control-plane (auth) + bundled demo.
COPY app           /app/app
COPY control_plane /app/control_plane
COPY demo          /app/demo
COPY pyproject.toml /app/pyproject.toml

# Writable dir for scheduler state / contracts / interaction logs (see config.py).
RUN mkdir -p /app/logs

EXPOSE 8000

# Railway injects $PORT. Shell form so it expands; falls back to 8000 locally.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
