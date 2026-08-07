"""`G0` — sağlayıcı yanıtı **teşhisli** çıkarılır (ADR-0020: sessiz yutma yok).

## Ölçülen kusur

`_chat` yanıtı tek satırda indeksliyordu: `data["choices"][0]["message"]["content"]`.
OpenRouter ücretsiz katmanı kısıtlandığında **HTTP 200 + `{"error": …}`** döndürüyor →
`raise_for_status()` geçiyor → satır **`KeyError: 'choices'`** ile patlıyordu. Kota ön
uçuşu o opak hatayı görüp *"kota tükenmiş **ya da** anahtar geçersiz **olabilir**"* diye
**tahmin** yazdı.

🔴 Bir hata, ne olduğunu söylemiyorsa **yutulmuştur** — kapı budur.
"""

from __future__ import annotations

import pytest

from app.llm import SaglayiciYaniti, _icerik_cikar


def test_normal_icerik_dondurulur():
    d = {"choices": [{"message": {"content": "SELECT 1"}}]}
    assert _icerik_cikar(d, "openrouter", "m") == "SELECT 1"


def test_kod_citi_temizlenir():
    d = {"choices": [{"message": {"content": "```sql\nSELECT 1\n```"}}]}
    assert _icerik_cikar(d, "openrouter", "m") == "SELECT 1"


def test_http200_govdesinde_error_TESHISLI_patlar():
    """🔴 Asıl vaka: sağlayıcı reddetti ama HTTP 200 döndü."""
    d = {"error": {"message": "Rate limit exceeded: free-models-per-day"}}
    with pytest.raises(SaglayiciYaniti) as e:
        _icerik_cikar(d, "openrouter", "nemotron")
    m = str(e.value)
    assert "REDDETTİ" in m
    assert "Rate limit" in m          # sağlayıcının kendi sözü AKTARILIR
    assert "nemotron" in m            # hangi model olduğu görünür


def test_choices_yoksa_gelen_anahtarlar_yazilir():
    d = {"id": "x", "object": "chat.completion", "usage": {}}
    with pytest.raises(SaglayiciYaniti) as e:
        _icerik_cikar(d, "groq", "m")
    assert "`choices` YOK" in str(e.value)
    assert "usage" in str(e.value)    # teşhis için gelen anahtarlar sayılır


def test_akil_yuruten_model_AYRI_teshis_alir():
    """🔴 Ölçüldü: `nemotron-3-ultra` 16 token'ın tamamını `reasoning`'e harcadı.

    Bunu *"boş cevap"* diye raporlamak, kusurun **modelde** olduğunu gizlerdi.
    """
    d = {"choices": [{"finish_reason": "length",
                      "message": {"content": "", "reasoning": "The user wants..."}}]}
    with pytest.raises(SaglayiciYaniti) as e:
        _icerik_cikar(d, "openrouter", "nemotron-3-ultra")
    m = str(e.value)
    assert "AKIL YÜRÜTÜYOR" in m
    assert "sıcak yola uygun değil" in m


def test_bos_icerik_akil_yurutmeden_de_ayrilir():
    d = {"choices": [{"finish_reason": "stop", "message": {"content": "   "}}]}
    with pytest.raises(SaglayiciYaniti) as e:
        _icerik_cikar(d, "ollama", "m")
    assert "BOŞ içerik" in str(e.value)
    assert "AKIL YÜRÜTÜYOR" not in str(e.value)   # yanlış teşhis KOYMAZ


def test_keyerror_ARTIK_SIZMAZ():
    """Kapının özü: hangi bozuk yanıt gelirse gelsin **teşhisli** hata çıkar."""
    for bozuk in ({}, {"choices": []}, {"choices": [{}]}, {"choices": [None]}):
        with pytest.raises(SaglayiciYaniti):
            _icerik_cikar(bozuk, "x", "m")
