"""**§C ÖLÇÜT 6'NIN ÜÇÜNCÜ ŞARTI: SÜRE AŞIMI 30 DK.** [bayraksız: değişmez]

## 🔴 Ölçüt 🟢 işaretliydi ve şartın üçte biri YOKTU

§C ölçüt 6: *"Onaysız yazma → **imkânsız** + onay başına **audit satırı** + **süre aşımı
30 dk**"*. İlk ikisi kuruluydu. Üçüncüsü **okunarak** ölçüldü ve yoktu:

* `app/routers/eylem.py::eylem_onayla` — **hiçbir** süre kontrolü. Üç saat önceki bir
  öneri onaylanıp koşabiliyordu.
* `VARSAYILAN_OMUR_SN = 30 * 60` yalnız `app/onay_akisi.py`'de duruyordu — ve o modülün
  **hiçbir üretim tüketicisi yoktu** (denetimin *"12 yetim modül"* bulgusunun ikinci
  kalemi).

> 🔴 *Bir ölçütün üçte biri eksikse, ölçüt yeşil değildir.*

## Neden imzalı bilet — ve neden düz zaman damgası DEĞİL

İstemciden gelen bir zaman damgası **taklit edilebilir**: istemci her seferinde *"şimdi"*
gönderir ve kapı bir **törene** dönüşür. Bilet HMAC ile imzalanır.

⚠ İkinci bir secret **üretilmedi**: `paylasim.py`'nin gerekçesi burada da geçerli —
rotasyonu, saklanması ve sızma davranışı olan **bir** anahtar vardır.
*İki anahtar, iki kez yanlış yönetilir.*

## ⚠ İki tasarım kararı testlerle DÜZELTİLDİ

1. Süre kapısını **yetkiden önce** koymuştum; gerekçem *"süresi dolmuş bir öneri, yetkisi
   olsa bile koşmamalı"*ydı ve **yanlıştı**: yetki önce koşarsa yetkili kullanıcı yine bu
   kapıya çarpar, yetkisiz olan **daha güçlü** bir kapıda durur. Ters sıra yalnız
   yetkisiz bir çağrının **403 sinyalini gizliyordu**.
   *Bir kapıyı öne almak, onu güçlendirmez; yalnız arkasındakinin sesini kısar.*
2. Bileti **öneriyi kuran** yerlere eklemiştim — öneri **üç ayrı yerde** kuruluyor ve bu
   **üç sahip** demekti. Tek sahip: `answer.seal()`.
"""

from __future__ import annotations

import ast
import time
from pathlib import Path

import pytest

from app import onay_akisi

_KOK = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def _anahtar(monkeypatch):
    """İmza anahtarı — testte sabit."""
    from control_plane.config import get_auth_settings

    s = get_auth_settings()
    if not getattr(s, "jwt_secret", ""):
        monkeypatch.setattr(s, "jwt_secret", "test-secret-0123456789", raising=False)


def test_SURE_SABITI_30_DAKIKA():
    """§C'nin sayısı: **30 dk**."""
    assert onay_akisi.VARSAYILAN_OMUR_SN == 30 * 60


def test_GECERLI_BILET_kabul():
    t = onay_akisi.bilet("eylem.zamanla")
    onay_akisi.bilet_dogrula(t, "eylem.zamanla")


def test_SURE_DOLUNCA_RET():
    """🔴 Asıl şart."""
    t = onay_akisi.bilet("eylem.zamanla", simdi=time.time() - 3600)
    with pytest.raises(onay_akisi.OnayHatasi, match="süre"):
        onay_akisi.bilet_dogrula(t, "eylem.zamanla")


def test_RET_MESAJI_NE_YAPILACAGINI_soyluyor():
    """⚠ *Süresi dolduğu söylenmeyen bir ret, bir arıza gibi okunur.*"""
    t = onay_akisi.bilet("eylem.zamanla", simdi=time.time() - 3600)
    with pytest.raises(onay_akisi.OnayHatasi) as e:
        onay_akisi.bilet_dogrula(t, "eylem.zamanla")
    assert "yeniden" in str(e.value) and "30" in str(e.value)


def test_BASKA_EYLEMIN_BILETI_reddedilir():
    """🔴 Bir *"tercih kaydet"* bileti bir *"zamanla"* onayına iliştirilebilseydi, süre
    kapısı **yanlış eylemi** korurdu."""
    t = onay_akisi.bilet("tercih.kaydet")
    with pytest.raises(onay_akisi.OnayHatasi, match="BAŞKA"):
        onay_akisi.bilet_dogrula(t, "zamanla.olustur")


def test_IMZA_KURCALANIRSA_ret():
    """🔴 Taklit edilebilir bir zaman damgası, kapıyı bir **törene** çevirirdi."""
    t = onay_akisi.bilet("eylem.zamanla")
    govde, _, imza = t.partition(".")
    with pytest.raises(onay_akisi.OnayHatasi, match="imza"):
        onay_akisi.bilet_dogrula(f"{govde}.{imza[:-2]}xy", "eylem.zamanla")


def test_BOZUK_BILET_ret():
    with pytest.raises(onay_akisi.OnayHatasi):
        onay_akisi.bilet_dogrula("saçma", "eylem.zamanla")
    with pytest.raises(onay_akisi.OnayHatasi):
        onay_akisi.bilet_dogrula("", "eylem.zamanla")


def test_IMZA_SABIT_ZAMANLI():
    """🔴 Normal `==`, bileti bayt bayt tahmin etmeye açık bir **zamanlama kanalı**
    bırakırdı."""
    src = (_KOK / "app/onay_akisi.py").read_text(encoding="utf-8")
    assert "hmac.compare_digest" in src


def test_IKINCI_SECRET_URETILMEDI():
    """⚠ *İki anahtar, iki kez yanlış yönetilir.*"""
    src = (_KOK / "app/onay_akisi.py").read_text(encoding="utf-8")
    assert "get_auth_settings" in src and "jwt_secret" in src


def test_ANAHTARSIZ_IMZA_URETILMEZ():
    """🔴 *Anahtarsız bir imza, imza değildir.*"""
    src = (_KOK / "app/onay_akisi.py").read_text(encoding="utf-8")
    i = src.index("def _gizli(")
    assert "raise OnayHatasi" in src[i:i + 600]


def test_BILET_ARGUMAN_TASIMIYOR():
    """⚠ Argümanlar bileti girseydi bilet onları da **doğrulanmış** gösterirdi; oysa
    `eylem_onayla` onları zaten kendi kapılarından geçiriyor ve **iki doğrulama, ikisi de
    eksik** olurdu."""
    src = (_KOK / "app/onay_akisi.py").read_text(encoding="utf-8")
    agac = ast.parse(src)
    fn = next(n for n in agac.body if isinstance(n, ast.FunctionDef) and n.name == "bilet")
    assert "argumanlar" not in ast.unparse(fn)


# --- Uç: fail-closed ve DOĞRU SIRA ----------------------------------------------------

def test_UC_BILETSIZ_ONAYI_reddediyor():
    """*Bir süre kapısı, atlanabildiği anda bir tören olur.*"""
    src = (_KOK / "app/routers/eylem.py").read_text(encoding="utf-8")
    assert "onay_akisi.bilet_dogrula(body.bilet, beyan.ad)" in src


def test_SIRA_YETKI_ONCE_SURE_SONRA():
    """🔴 **Bir tasarım kararı testle düzeltildi.** Süre kapısını yetkiden önce
    koymuştum; ters sıra yetkisiz bir çağrının **403 sinyalini gizliyordu**.
    *Bir kapıyı öne almak, onu güçlendirmez; yalnız arkasındakinin sesini kısar.*"""
    src = (_KOK / "app/routers/eylem.py").read_text(encoding="utf-8")
    i_yetki = src.index("if not can(principal, beyan.izin):")
    i_sure = src.index("onay_akisi.bilet_dogrula(")
    assert i_yetki < i_sure, "🔴 süre kapısı yetkiden ÖNCE — 403 sinyali gizlenir"


def test_RET_400_DEGIL_410():
    """⚠ 410 (Gone) bir kaynağın *"vardı, artık yok"* hâlidir; burada kaynak duruyor,
    **onay** bayatladı."""
    src = (_KOK / "app/routers/eylem.py").read_text(encoding="utf-8")
    i = src.index("onay_akisi.bilet_dogrula(")
    assert "status_code=400" in src[i:i + 700]


def test_BILET_TEK_SAHIPTEN_ilistiriliyor():
    """🔴 Öneri **üç ayrı yerde** kuruluyor; üçüne ayrı bilet eklemek üç sahip demekti ve
    dördüncüsü bir gün unuturdu. Tek sahip: `answer.seal()`."""
    ans = (_KOK / "app/answer.py").read_text(encoding="utf-8")
    assert "onay_akisi.bilet(resp.eylem_onerisi[\"eylem\"])" in ans
    for baska in ("app/eylem.py", "app/routers/ask.py"):
        assert "onay_akisi.bilet(" not in (_KOK / baska).read_text(encoding="utf-8"), (
            f"🔴 {baska} da bilet üretiyor — ikinci sahip.")


def test_ANAHTAR_YOKSA_BILETSIZ_doner_SESSIZ_DEGIL():
    """🔴 Sessizce **süresiz** bir öneri üretmek yerine biletsiz dönülür ve uç onu
    reddeder; ve olay **loglanır**."""
    ans = (_KOK / "app/answer.py").read_text(encoding="utf-8")
    i = ans.index("onay_akisi.bilet(resp.eylem_onerisi")
    assert "_log.warning" in ans[i:i + 900]


def test_FRONTEND_BILETI_TASIYOR():
    """K2: yeni bir sözleşme alanı **frontend tüketicisi olmadan** eklenemez."""
    from tests.kapi_ortak import fe_dosyalari

    assert "bilet: string," in fe_dosyalari()["lib/api-client.ts"]
    assert "String(oneri.bilet ?? \"\")" in fe_dosyalari()["components/ReportCard.tsx"]


def test_FRONTEND_SURE_ASIMINI_AYRI_soyluyor():
    """⚠ *"Tekrar dener misin"* bayat bir öneride kullanıcıyı aynı duvara **ikinci kez**
    çarptırır."""
    from tests.kapi_ortak import fe_dosyalari

    src = fe_dosyalari()["components/ReportCard.tsx"]
    assert "zaman aşımına uğradı" in src and "tazeleyin" in src


def test_MODUL_ARTIK_YETIM_DEGIL():
    """🔴 Denetimin *"12 yetim modül"* bulgusunun **ikinci** kalemi kapandı."""
    ans = (_KOK / "app/answer.py").read_text(encoding="utf-8")
    ey = (_KOK / "app/routers/eylem.py").read_text(encoding="utf-8")
    assert "from app import onay_akisi" in ans or "from app import onay_akisi" in ey
