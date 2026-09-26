# Canonical Dima Metabase Platform backend.
# Metabase/Metabot is an external/frozen analytical runtime; no Wren source or demo data is baked in.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /app/pyproject.toml
COPY app /app/app
COPY control_plane /app/control_plane
COPY migrations /app/migrations
COPY alembic.ini /app/alembic.ini
COPY product_contracts /app/product_contracts

RUN pip install .

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
