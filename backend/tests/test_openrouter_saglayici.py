"""OpenRouter sağlayıcısı — ölçüm turları kota duvarına çarpınca eklendi.

## Neden (ölçüldü, 3 Ağustos 2026)

Faz C'nin A/B kazanç ölçümü sırasında Gemini ücretsiz katmanı **HTTP 429**'a çarptı
(kullanıcının uyardığı günlük kota). Ölçüm yarım kaldı ve *"kurtarma 0"* sonucu bir
**kota artefaktı** mı yoksa gerçek mi ayırt edilemez oldu.

OpenRouter bir **LLM hub**'ıdır: tek anahtarla onlarca model (açık kaynak dâhil) →
daha yüksek hacimli A/B ölçümü mümkün.

## Neden YENİ İSTEMCİ YAZILMADI

OpenRouter **OpenAI-uyumlu**dur; `OpenAICompatibleSqlGenerator` aynen kullanılıyor —
`groq`/`xai`/`gemini`/`ollama` ile **aynı** sınıf. Eklenen tek şey config alanları ve
`_make`'te bir dal. Yeni bir istemci yazmak, dört kez ödenmiş bir bedeli beşinci kez
ödemek olurdu.

## Zincirdeki YERİ bilinçli

`anthropic → gemini → groq → xai → **openrouter** → ollama`. Ölçüm için eklenen bir
sağlayıcı, üretimin **varsayılan** sağlayıcısını değiştirmemelidir; yalnız öncekiler
tükendiğinde devreye girer.
"""

from __future__ import annotations

import inspect

from app import llm as llm_mod
from app.config import Settings


def test_ANAHTAR_YOKSA_uretici_YOK():
    """Anahtarsız bir sağlayıcı zincire girmemeli — sessizce başarısız bir dal,
    failover'ı yavaşlatır ve hata mesajını bulanıklaştırır."""
    assert llm_mod._make("openrouter", Settings(openrouter_api_key=""), "duckdb") is None


def test_ANAHTAR_VARSA_OpenAI_UYUMLU_istemci():
    """Yeni istemci YAZILMADI — dört sağlayıcının paylaştığı sınıf kullanılıyor."""
    g = llm_mod._make("openrouter", Settings(openrouter_api_key="x"), "duckdb")
    assert type(g).__name__ == "OpenAICompatibleSqlGenerator"
    for yetenek in ("generate_sql", "select_cube", "refine_cube", "anlat",
                    "prompt_enhance"):
        assert hasattr(g, yetenek), f"{yetenek} yok — zincirde yarım sağlayıcı olur"


def test_VARSAYILAN_base_url_OpenRouter():
    s = Settings(openrouter_api_key="x")
    assert s.openrouter_base_url.rstrip("/").endswith("openrouter.ai/api/v1")


def test_ZINCIRDEKI_YERI_gemini_ve_groqTAN_SONRA():
    """Ölçüm sağlayıcısı üretimin varsayılanını DEĞİŞTİRMEMELİ."""
    govde = inspect.getsource(llm_mod.build_generator)
    i = govde.index('order = [')
    sira = govde[i:i + 160]
    for once in ("gemini", "groq", "xai"):
        assert sira.index(f'"{once}"') < sira.index('"openrouter"'), \
            f"openrouter {once}'dan ÖNCE geliyor — üretim davranışı değişir"
    assert sira.index('"openrouter"') < sira.index('"ollama"')


def test_ACIK_SECIM_de_calisiyor():
    """`DIMA_LLM_PROVIDER=openrouter` ile doğrudan seçilebilmeli (ölçüm turları böyle
    koşuyor — failover'a bırakmak hangi modelin ölçüldüğünü belirsizleştirirdi)."""
    s = Settings(llm_provider="openrouter", openrouter_api_key="x")
    g = llm_mod.build_generator(s)
    assert type(g).__name__ == "OpenAICompatibleSqlGenerator"


def test_SELECT_MODEL_ayri_verilebilir():
    """Intent-JSON için ucuz/ayrı model — diğer dört sağlayıcıyla aynı sözleşme."""
    g = llm_mod._make("openrouter",
                      Settings(openrouter_api_key="x", openrouter_select_model="ucuz/model"),
                      "duckdb")
    assert getattr(g, "_select_model", None) == "ucuz/model"
