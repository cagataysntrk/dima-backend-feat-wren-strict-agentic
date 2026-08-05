"""FAZ 6.0 kapısı — 🔴 **D9 BUGÜN TERS UYGULANMIŞTI: «yapılanı geri al».**

> Bu, belgedeki hiçbir maddenin taşımadığı bir türdür: **yeni iş değil, İNMİŞ İŞİN GERİ
> ALINMASI**.

`D9`: *"kapsam **içi** ve **geri alınabilir** bir eylem **İSTEMSİZ** koşar; varsayılan
**SINIR**'dır, **istem** değil."* Yürüyen planın `H` fazı bunun **tersini** uyguladı.

| Eylem | `geri_alinabilir` | D9'un hükmü | önceki kod |
|---|---|---|---|
| `pano.ekle` | **True** (soft-delete) · kullanıcının **kendi** panosu | istemsiz koşmalı | 🔴 hep istem |
| `tercih.kaydet` | **True** · tek uçla silinir | istemsiz koşmalı | 🔴 hep istem |
| `zamanla.olustur` | **False** · dışarıya e-posta çıkar | senkron istem | ✅ doğru |

## 🔴 YAZMA YÜZEYİ BÜYÜMÜYOR

Ajan hâlâ yazma aracı **çağırmıyor**; değişen tek şey **kullanıcının KENDİ eyleminin kaç
tıkla tamamlandığı**. Bu dosya onu ayrıca ölçer.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from app import eylem


class _P:
    """Kendi yetkisi olan bir kullanıcı."""

    user_id = "u1"
    tenant_id = "t1"
    is_superadmin = False
    permissions = ("query:run", "schedule:create")


def _can_yamasi(monkeypatch, izinli=True):
    import control_plane.authorize as az

    monkeypatch.setattr(az, "can", lambda p, izin: izinli)


def test_GERI_ALINABILIR_eylemler_ISTEMSIZ(monkeypatch):
    """🔴 D9'un hükmü: `pano.ekle` ve `tercih.kaydet` **istem üretmez**."""
    _can_yamasi(monkeypatch)
    assert eylem.d9_istemsiz_mi(eylem.PANO_EKLE, _P()) is True
    assert eylem.d9_istemsiz_mi(eylem.TERCIH_KAYDET, _P()) is True


def test_GERI_ALINAMAZ_eylem_ISTEM_uretir(monkeypatch):
    """🔴 `zamanla.olustur` **dışarıya e-posta çıkarır** ve kurulmuş bir gönderim geçmişe
    dönük silinemez. Bu doğru davranıştı ve **korunuyor**."""
    _can_yamasi(monkeypatch)
    assert eylem.d9_istemsiz_mi(eylem.ZAMANLA, _P()) is False
    assert eylem.beyan(eylem.ZAMANLA).geri_alinabilir is False


def test_KIMLIKSIZ_eylem_ISTEMSIZ_KOSMAZ():
    """⚠ **Fail-closed**: kimliği bilinmeyen bir eylem **kapsam içi sayılamaz**.

    Geri alınabilirlik tek başına yetmez — *geri alınabilirlik, geri alacak kişinin
    elinde olmalıdır.*
    """
    assert eylem.d9_istemsiz_mi(eylem.PANO_EKLE, None) is False


def test_YETKISIZ_kullanici_ISTEMSIZ_KOSMAZ(monkeypatch):
    """Kapsam = kullanıcının **kendi yetkisi**; `authorize.can()` tek kaynak."""
    _can_yamasi(monkeypatch, izinli=False)
    assert eylem.d9_istemsiz_mi(eylem.PANO_EKLE, _P()) is False


def test_KAYITSIZ_eylem_ISTEMSIZ_KOSMAZ():
    assert eylem.d9_istemsiz_mi("uydurma.eylem", _P()) is False


def test_YETKI_IKINCI_KEZ_yazilmadi():
    """⚠ Belirteç **AST**: `d9_istemsiz_mi` `authorize.can`'i **çağırmalı**, kendi izin
    listesini kurmamalı — matrisin iki sahibi olursa ikisi ayrışır."""
    agac = ast.parse((Path(__file__).resolve().parents[1] / "app/eylem.py")
                     .read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "d9_istemsiz_mi")
    cagrilar = {getattr(c.func, "id", getattr(c.func, "attr", ""))
                for c in ast.walk(fn) if isinstance(c, ast.Call)}
    assert "can" in cagrilar, "🔴 yetki `authorize.can()`'den okunmuyor"
    # `permissions` listesini elle okumak = ikinci kopya.
    assert "permissions" not in ast.unparse(fn), (
        "🔴 İzin listesi ELLE okunuyor — `authorize()` matrisinin ikinci kopyası doğmuş.")


def test_KAPILAR_ATLANMIYOR_ayni_uc_cagriliyor():
    """🔴 *"İstemsiz koşmak", kapıları atlamak değil **ikinci kez tıklamayı** atlamaktır.*

    `_uygula_dogrudan` **kendi uygulamasını yazmaz**: `eylem_onayla`'yı çağırır. Böylece
    kayıt kapısı, `authorize()` yeniden doğrulaması, çapa şartı ve `eylem_onay` audit
    satırı **aynen** işler.
    """
    agac = ast.parse((Path(__file__).resolve().parents[1] / "app/routers/eylem.py")
                     .read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "_uygula_dogrudan")
    cagrilar = {getattr(c.func, "id", getattr(c.func, "attr", ""))
                for c in ast.walk(fn) if isinstance(c, ast.Call)}
    assert "eylem_onayla" in cagrilar, (
        "🔴 İstemsiz koşum KENDİ uygulamasını yazmış — kapılar bir gün ayrışır ve "
        "ayrışan taraf her zaman daha GEVŞEK olanıdır.")
    for yasak in ("add_widget", "tercih_yaz", "create_schedule"):
        assert yasak not in cagrilar, (
            f"🔴 `{yasak}` DOĞRUDAN çağrılıyor — onay ucunun kapıları atlanmış.")


def test_YAZMA_YUZEYI_BUYUMEDI():
    """🔴 *Ajan hâlâ yazma aracı ÇAĞIRMIYOR.* Değişen tek şey kullanıcının kendi
    eyleminin kaç tıkla tamamlandığı."""
    from app import tools

    yazanlar = [a.ad for a in tools.hepsi() if a.yan_etki == "yazar"]
    assert not yazanlar, (
        f"🔴 Araç kaydına yazan araç girmiş: {yazanlar}. D9 bir KOLAYLIKTIR, bir yetki "
        f"genişlemesi değil.")


def test_IKISI_AYNI_ANDA_DOLAMAZ():
    """🔴 Bir iş ya **yapıldı** ya **onay bekliyor**.

    İkisini birden göstermek, kullanıcıya *"hem oldu hem olmadı"* demektir. Kapı
    `ask.py`'nin bu iki alanı birbirini dışlayacak şekilde doldurduğunu ölçer.
    """
    kaynak = (Path(__file__).resolve().parents[1] / "app/routers/ask.py").read_text(
        encoding="utf-8")
    assert "_oneri = None" in kaynak, (
        "🔴 İstemsiz koşum sonrası öneri TEMİZLENMİYOR — kullanıcı hem 'yapıldı' hem "
        "'onayla' görür.")
    assert "eylem_onerisi=_oneri, eylem_sonucu=_sonuc" in kaynak


def test_BASARISIZ_kosum_ONERIYE_duser():
    """⚠ *Bir kolaylık, yeteneği yok etmez.* Doğrudan koşum patlarsa kullanıcı yine
    onaylayıp yapabilmeli — sessizce kaybolmamalı."""
    kaynak = (Path(__file__).resolve().parents[1] / "app/routers/ask.py").read_text(
        encoding="utf-8")
    assert "öneriye düşüldü" in kaynak


def test_BAYRAK_kapaliyken_BIREBIR_eski_davranis():
    """GERİ AL: `onay_akisi=off` → bugünkü *"her yazmaya istem"* davranışı."""
    from pathlib import Path as _P2

    import yaml

    from app.features import FLAG_REGISTRY

    assert "onay_akisi" in FLAG_REGISTRY
    d = yaml.safe_load((_P2(__file__).resolve().parents[1] / "demo/packs/features.yml")
                       .read_text(encoding="utf-8"))
    assert d["features"]["onay_akisi"] == "off"
    kaynak = (_P2(__file__).resolve().parents[1] / "app/routers/ask.py").read_text(
        encoding="utf-8")
    assert '"onay_akisi" in resolve_for(settings, principal)' in kaynak, (
        "🔴 D9 dalı bayraktan bağımsız çalışıyor olabilir — GERİ AL yolu kırık.")


@pytest.mark.parametrize("ad", [eylem.PANO_EKLE, eylem.TERCIH_KAYDET])
def test_geri_alinabilir_eylemler_KAYITTA_dogru_isaretli(ad):
    assert eylem.beyan(ad).geri_alinabilir is True
