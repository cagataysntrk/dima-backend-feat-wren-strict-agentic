"""FAZ 6.6 kapısı — **eşlemesi olmayan kanal kullanıcısının sorusuna YANIT VERİLMEZ.**
[bayrak: `kanal_kimlik`]

## Araştırmanın en net uyarısı

Hiçbir satıcı sağlam bir *"sohbet-kimliği → BI-kimliği → RLS"* eşlemesi yayımlamamış;
Microsoft'un kendi belgesi Slack e-postasının Teams hesabına güvenilir eşlenemeyeceğini
söylüyor `[DOĞRULANMADI — birincil kaynak okunmadı]`.

> 🔴 *Bir kimliği çıkarımla kurmak, RLS'i çıkarımla kurmaktır.*
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from app import kanal_kimlik as kk

_KAYIT = [{"kanal": "slack", "kanal_kullanici_id": "U123", "dima_user_id": "u-1",
           "onaylayan_admin_id": "admin-9", "deleted_at": None}]


def test_ESLEMESI_OLMAYAN_kullaniciya_YANIT_YOK():
    """🔴 Yol haritasının tek kapısı — ve sertliği bilinçli.

    Alternatif (*"eşleme yoksa sınırlı bir cevap ver"*) bir **kimliksiz** kullanıcıya
    veri göstermek olurdu; ve sınırın ne olduğunu kimse söyleyemezdi, çünkü RLS
    **kimliğe** dayanır.
    """
    with pytest.raises(kk.KimlikYok, match="eşlemesi YOK"):
        kk.cozumle(_KAYIT, "slack", "U999")
    with pytest.raises(kk.KimlikYok):
        kk.cozumle([], "slack", "U123")
    with pytest.raises(kk.KimlikYok):
        kk.cozumle(None, "slack", "U123")


def test_ESLEME_VARSA_kimlik_doner():
    assert kk.cozumle(_KAYIT, "slack", "U123") == "u-1"


def test_ONAYLAYAN_ADMIN_yoksa_ESLEME_SAYILMAZ():
    """🔴 Onaysız bir eşleme, **bir çıkarımdan farksızdır**."""
    bozuk = [{**_KAYIT[0], "onaylayan_admin_id": ""}]
    with pytest.raises(kk.KimlikYok, match="onaylayan_admin_id"):
        kk.cozumle(bozuk, "slack", "U123")


def test_SILINMIS_esleme_ESLESME_DEGILDIR():
    """Soft-delete (ADR-0019): kaldırılmış bir eşleme **de bir kayıttır** ama eşleşmez."""
    silinmis = [{**_KAYIT[0], "deleted_at": "2026-01-01"}]
    with pytest.raises(kk.KimlikYok):
        kk.cozumle(silinmis, "slack", "U123")


def test_BILINMEYEN_kanal_reddedilir():
    with pytest.raises(kk.KimlikYok, match="bilinmeyen kanal"):
        kk.cozumle(_KAYIT, "discord", "U123")


def test_KANAL_ayrimi_KORUNUR():
    """⚠ Aynı kullanıcı kimliği farklı kanallarda **farklı kişiler** olabilir —
    Microsoft'un uyardığı tam olarak bu."""
    with pytest.raises(kk.KimlikYok):
        kk.cozumle(_KAYIT, "teams", "U123")


def test_DONUS_None_DEGIL_ISTISNA():
    """🔴 `None` dönseydi çağıran onu *"anonim kullanıcı"* diye yorumlayabilir ve akış
    **devam ederdi**. *Bir kimlik kararı sessizce başarısız olamaz.*"""
    fn = next(n for n in ast.walk(ast.parse(
        (Path(__file__).resolve().parents[1] / "app/kanal_kimlik.py")
        .read_text(encoding="utf-8")))
        if isinstance(n, ast.FunctionDef) and n.name == "cozumle")
    assert ast.unparse(fn.returns) == "str", (
        "🔴 `cozumle` `str | None` dönüyor — çağıran `None`'ı 'anonim' sanabilir.")


def test_EPOSTA_HIC_OKUNMUYOR():
    """🔴 *Bir kısayolu yasaklamanın en güvenilir yolu, onu mümkün kılan veriyi hiç
    almamaktır.*

    Modül e-posta **okumaz**; parametrelerinde bile yoktur. Bir gün biri
    `eposta_ile_esle()` yazarsa bu kapı kırmızı olur.
    """
    kaynak = (Path(__file__).resolve().parents[1] / "app/kanal_kimlik.py").read_text(
        encoding="utf-8")
    agac = ast.parse(kaynak)
    for fn in (n for n in ast.walk(agac) if isinstance(n, ast.FunctionDef)):
        adlar = [a.arg for a in fn.args.args + fn.args.kwonlyargs]
        for a in adlar:
            assert "eposta" not in a.lower() and "email" not in a.lower(), (
                f"🔴 `{fn.name}` bir e-posta parametresi alıyor (`{a}`) — e-posta bir "
                f"İDDİADIR, kimlik kanıtı değil.")


def test_MODEL_onaylayan_admin_ZORUNLU():
    """⚠ *Bir zorunluluğu belgede tutup şemada tutmamak, onu bir temenniye çevirir.*"""
    from control_plane.models import KanalKimlikEslemesi

    alan = KanalKimlikEslemesi.model_fields["onaylayan_admin_id"]
    assert alan.is_required(), (
        "🔴 `onaylayan_admin_id` opsiyonel — e-postadan çıkarılmış bir eşleme sessizce "
        "yazılabilir ve ŞEMANIN KENDİSİ o kısayolu mümkün kılar.")


def test_GOC_NOT_NULL_yaziyor():
    goc = (Path(__file__).resolve().parents[1]
           / "migrations/versions/e9b2d4a71c58_kanal_kimlik.py").read_text(
        encoding="utf-8")
    assert '"onaylayan_admin_id", sa.String(), nullable=False' in goc


@pytest.mark.parametrize("kanal", list(kk.KANALLAR))
def test_UC_KANAL_tanimli(kanal):
    assert kanal in kk.KANALLAR
