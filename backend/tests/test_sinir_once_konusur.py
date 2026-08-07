"""🔴 **SINIRI ÖNCE SÖYLE** — canlı curl bulgusu (§17.4).

## Ölçülen

    "gelecek ay ciro tahmini"  →  "toplam ciro çıkarabilirim — hangi dönem için?"

Kullanıcı **gelecek** sordu, sistem **geçmiş** için dönem soruyor. Ve bir dönem söylerse
sistem **yapamadığı şeyi yapmış gibi** bir sayı dönecek.

⊙ Sınır **vardı**: `yetenek.kapsam_disi("gelecek ay ciro tahmini")` → `forecast`.
Konuşmadı çünkü kapısı dönem netleştirmesinden **çok sonra** duruyordu.

*Bir sınırı bilmek, onu doğru anda söylemekten farklıdır; geç söylenen sınır,
söylenmemiş sınırdır.*

## ⚠ Kapsam DAR tutuldu

Kapı yukarı **taşınmadı** — yalnız dönem netleştirmesi ona soruyor. Taşımak,
`route()`/Intent-JSON'un cevapladığı soruları da sınır beyanına çevirebilirdi ve o takas
**ölçülmedi**. *Bir sırayı düzeltmek, sırayı baştan yazmak değildir.*
"""

from __future__ import annotations

import pytest

from app import cube_router as cr
from app import yetenek
from tests.conftest import ask


@pytest.mark.parametrize("soru", ["gelecek ay ciro tahmini",
                                  "önümüzdeki ay ciro tahmini"])
def test_TAHMIN_SORUSU_DONEM_SORMUYOR(client, schema, soru):
    """🔴 Kapının asıl iddiası: yapamadığımız şey **önce** söylenir."""
    assert yetenek.kapsam_disi(cr._norm(soru), schema) is not None, (
        "⊘ ölçüm önkoşulu: bu soru bir yetenek sınırı olmalı — vaka bayat")
    d = ask(client, soru)
    not_ = (d.get("note") or "").lower()
    assert "hangi dönem" not in not_, (
        f"🔴 sınır yerine dönem soruldu: {d.get('note')!r} — kullanıcı bir dönem "
        f"söylerse sistem YAPAMADIĞI ŞEYİ yapmış gibi sayı döner")


def test_MESRU_DONEM_SORUSU_BOZULMADI(client):
    """⚠ Genişlemenin sınırı: gerçekten dönemi eksik bir soru **hâlâ** dönem sormalı.
    *Bir kuralı düzeltmek, komşusunu bozma hakkı vermez.*"""
    d = ask(client, "kumaş türlerine göre fire oranı")
    assert "hangi dönem" in (d.get("note") or "").lower(), d.get("note")


def test_TEK_SOZLESME_IKI_CAGIRAN():
    """🔴 `KAT-1`: *"sınır varsa söyle, yoksa devam et"* sözleşmesi **tek** yerde.
    Aynı `try/except`'i iki kez yazmak, bir gün yalnız birinde yazmak demekti."""
    import inspect

    from app.routers import ask as ask_mod

    src = inspect.getsource(ask_mod)
    assert src.count("_yetenek.kapsam_disi(") == 1, (
        "🔴 `kapsam_disi` birden çok yerden doğrudan çağrılıyor — sarmalayıcı atlanmış")
    assert src.count("_guvenli_kapsam_disi(") >= 3, (
        "🔴 çağıranlar sarmalayıcıdan geçmiyor (tanım + en az iki çağrı beklenir)")
