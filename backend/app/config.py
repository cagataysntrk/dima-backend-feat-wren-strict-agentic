"""Canonical Dima Metabase Platform settings.

Only settings owned by the pre-UI canonical Platform live here. Historical
Wren/demo/Ask-v2 configuration is intentionally absent.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_prefix="DIMA_",
        extra="ignore",
    )

    # Canonical analytical engine: frozen Metabase / Metabot runtime.
    metabase_native_base_url: str = ""
    metabase_engine_sha: str = "cbe313af9ac2d5960f662068e433d328d896fb06"
    metabase_engine_upstream_sha: str = "2ba2485c78d7e00a9a25f82c00fc201da71590c4"
    metabase_engine_runtime_tag: str = "v0.63.18-dima.6"
    metabase_engine_image_digest: str = (
        "sha256:40e9a44be49904de3ddf12d4683c768e70955851c10a928a9c8f7d8f60780353"
    )
    metabase_engine_build_identity: str = (
        "github-actions:36042062775:cbe313af9ac2d5960f662068e433d328d896fb06"
    )
    metabase_engine_image_identity: str = (
        "sha256:40e9a44be49904de3ddf12d4683c768e70955851c10a928a9c8f7d8f60780353"
    )

    # Canonical cognition transport. The product has one sealed default role/model;
    # individual features may not create an ad-hoc model cascade.
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    cognition_model: str = "openai/gpt-5.6-luna"

    # Classified productization debt only. No real-recipient execution is active.
    resend_api_key: str = ""
    resend_from: str = "dima <dima@upcytech.com>"

    # Pre-UI HTTP shell. UI implementation is not present.
    cors_origins: str = "http://localhost:3000"

    def cors_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
