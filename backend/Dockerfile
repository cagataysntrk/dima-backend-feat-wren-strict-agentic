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

# amd64'e SABİTLE: wren-core-py'nin manylinux x86_64 abi3 wheel'i var ama linux-arm64
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
# 2 Ağustos 2026 DÜZELTMESİ: pin `==0.7.2` idi ama KURULU sürüm 0.7.3 çıkıyordu —
# `wrenai 0.13.2` metadata'sı `wren-core-py>=0.7.3` istiyor ve adım 2 bu pin'i
# YÜKSELTİYORDU. Yani pin tutmuyor, altındaki gerekçe yorumu da bayattı. Aralık
# olarak yazıldı: wrenai'nin istediği alt sınır karşılanır, ana sürüm sıçraması engellenir.
RUN pip install "wren-core-py>=0.7.3,<0.8"

# 2) Install wrenai from PyPI since local mirror is not available
RUN pip install "wrenai>=0.13,<0.14"

# 3) Backend runtime deps
#
# ⚠️ Bu liste `pyproject.toml [project].dependencies`'in ELLE tutulan bir kopyasıdır ve
#    2 Ağustos 2026'da SAPMIŞ olduğu tespit edildi: `mrml`, `jinja2` ve `ruamel.yaml`
#    pyproject'te ZORUNLU bildirildiği halde burada yoktu. Sonucu çalışan üründe sessiz
#    çökmelerdi — `app/email_render.py:48` (her zamanlanmış rapor e-postası, ADR-0011) ve
#    `app/mdl_writer.py:19` (ölçü terfisi + bağlantı sihirbazının şema yazımı).
#    Sapmayı bir daha SESSİZCE gönderemeyelim diye iki koruma eklendi: (a) aşağıdaki
#    import duman testi build'i kırar, (b) `tests/test_dependencies.py` pyproject'teki her
#    bağımlılığın import edilebildiğini iddia eder (CI'da koşar, Docker'dan bağımsız).
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
      "psycopg[binary]>=3.2" \
      "mrml>=0.2" \
      "jinja2>=3.1" \
      "ruamel.yaml>=0.18" \
      "py-rust-stemmers>=0.1.8,<0.2" \
      "alembic>=1.13"

# 3b) Duman testi: bildirilen her runtime bağımlılığı GERÇEKTEN import edilebilmeli.
#     Eksikse build BURADA kırılır, üretimde ilk e-posta/terfi denemesinde değil.
RUN python -c "import fastapi, uvicorn, anthropic, openai, pydantic_settings, fastembed, \
sqlmodel, argon2, jwt, psycopg, mrml, jinja2, ruamel.yaml, alembic, wren, wren_core, py_rust_stemmers; \
print('deps OK')"

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
