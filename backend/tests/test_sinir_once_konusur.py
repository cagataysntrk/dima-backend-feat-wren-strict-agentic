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
    """⚠ Genişlemenin sınırı: gerçekten dönemi eksik bir soru **hâlâ dönemi konuşmalı**.
    *Bir kuralı düzeltmek, komşusunu bozma hakkı vermez.*

    ⟳ **POLİTİKA DEVRİ (`D3` → `§TZ`).** Bu satır *«hangi dönem»* metnini arıyordu, yani
    bir **soru** kipini. `varsayilan_donem` açılınca (korpus A/B ile ölçüldü) sistem
    artık soruyor değil **beyan ediyor**: *«⏱ Dönemi çözemedim — verinin son 12 ayı
    alındı … başka bir dönem yazarsan onu uygularım»* + tek-tık chip'ler.

    🔴 Bu testin **korumak istediği şey** kaybolmadı: dönemin eksikliği kullanıcıdan
    gizlenmiyor. Değişen yalnız **kip** — soru yerine beyan. O yüzden ölçüt metinden
    **garantiye** çevrildi: dönem konuşulur **ve** düzeltilebilir.

    *Bir kapıyı bir cümleye bağlamak, cümle değişince kapıyı da kaybetmektir.*
    """
    d = ask(client, "kumaş türlerine göre fire oranı")
    not_metni = (d.get("note") or "").lower()
    assert "dönem" in not_metni, f"🔴 dönemin eksikliği hiç konuşulmuyor: {d.get('note')}"
    assert any(s["label"] == "Tümü" for s in (d.get("suggestions") or [])), (
        f"🔴 `§TZ`: dönem beyanının yanında tek-tık düzeltme yok: {d.get('suggestions')}")


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
