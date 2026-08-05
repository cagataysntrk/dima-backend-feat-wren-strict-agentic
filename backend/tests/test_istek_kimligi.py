"""**BORÇ 1 KAPANDI** — *"36 çağrı sitesi kimlik geçmiyor → `motor_cls=on` KİLİTLİ."*
[bayraksız: altyapı · ölçüt 4'ün ön koşulu]

## Borcun kendisi

`OPERASYON-DURUM.md` · açık borç 1 ve `MIMARI.md §6.3c` aynı cümleyi taşıyordu:
`motor_cls` bayrağı **bu yüzden** `off` — kimlik taşımayan bir çağrı, motor-seviyesi
kolon maskesini **sessizce** atlar.

## 🔴 Neden 36 imza DEĞİŞTİRİLMEDİ

| # | Sebep |
|---|---|
| 1 | 🔴 **Fail-open bir düzeltme, düzeltme değildir**: imza değiştirmek bugünkü 36'yı kapatır, yarın yazılan **37.'si** `principal` geçmeyi unutur ve hiçbir şey kırılmaz |
| 2 | 36 imza + çağıranları, **davranış değişikliği olmadan** yüzlerce satır oynatır; her satır bir gerileme yüzeyidir |
| 3 | `principal` o modüllerin **işi değil**: `yoy.py` dönemsel kıyas hesaplar. Bir parametreyi taşımak için var olmak, modülü kimlik katmanına **bağımlı** yapar |

## Neden `ContextVar` — bu depoda üçüncü kez

`mali_takvim._ay_var` · `cube_router._reddi_var` · ve şimdi `istek_kimligi._kimlik`.
Üçü de *"istek boyunca doğru olan ama her imzaya sığmayan"* bağlamı taşır.

## Kilitlenen dört karar

| # | Karar | Olmasaydı |
|---|---|---|
| 1 | **Açık argüman bağlamı EZER** | Arka plan işi (zamanlanmış rapor) kendi kimliğini geçse bile isteği tetikleyenin kimliğiyle koşardı — **çapraz-kullanıcı sızıntı** |
| 2 | İkisi de yoksa **`None`** (fail-safe) | Kimliksiz çağrı **en kısıtlı** değil, en geniş seviyede koşardı |
| 3 | Kimlik **doğduğu yerde** ayarlanır (`get_current_principal`) | İki sahip; ve `wren_service`'in bir `Request` görmesi onu HTTP'ye **bağlardı** |
| 4 | `kimlik_kopyala()` **açıkça** var | `run_in_executor` bağlamı kopyalamaz; iş **sessizce** kimliksiz koşardı |
"""

from __future__ import annotations

import ast
import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import pytest

from app import istek_kimligi

_KOK = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class _Sahte:
    user_id: str
    is_superadmin: bool = False
    roles: tuple = ()


@pytest.fixture(autouse=True)
def _temiz():
    t = istek_kimligi.ayarla(None)
    yield
    istek_kimligi.sifirla(t)


def test_VARSAYILAN_None_ve_bu_FAIL_SAFE():
    """🔴 *Kimliği bilinmeyen bir çağrı, en az yetkili çağrıdır.* Varsayılan bir "sistem"
    kimliği olsaydı, kimlik geçmeyi **unutmak** en geniş erişimi verirdi."""
    assert istek_kimligi.simdiki() is None


def test_AYARLA_ve_SIFIRLA_yigin_gibi_davranir():
    """⚠ `set(None)` **yeterli değildir**: iç içe bir bağlamda dıştaki kimliği `None`'a
    düşürür. `reset` yığını doğru çözer."""
    dis = _Sahte("dis")
    ic = _Sahte("ic")
    t1 = istek_kimligi.ayarla(dis)
    assert istek_kimligi.simdiki() is dis
    t2 = istek_kimligi.ayarla(ic)
    assert istek_kimligi.simdiki() is ic
    istek_kimligi.sifirla(t2)
    assert istek_kimligi.simdiki() is dis, "🔴 iç bağlam çıkınca DIŞTAKİ kimlik kayboldu"
    istek_kimligi.sifirla(t1)
    assert istek_kimligi.simdiki() is None


def test_CONTEXT_MANAGER_token_unutulamaz():
    """⚠ *Doğru kullanımı hatırlamayı gerektiren bir API, er ya da geç yanlış kullanılır.*"""
    p = _Sahte("u1")
    with istek_kimligi.IstekKimligi(p):
        assert istek_kimligi.simdiki() is p
    assert istek_kimligi.simdiki() is None


def test_ISTISNADA_da_SIFIRLANIYOR():
    """🔴 Sıfırlanmayan bir kimlik, aynı thread'i yeniden kullanan bir sunucuda **başka
    bir kullanıcının** verisini görmek demektir."""
    p = _Sahte("u1")
    with pytest.raises(RuntimeError):
        with istek_kimligi.IstekKimligi(p):
            raise RuntimeError("patla")
    assert istek_kimligi.simdiki() is None


# --- Öncelik: açık argüman bağlamı EZER ------------------------------------------------

def test_ACIK_ARGUMAN_baglami_EZER():
    """🔴 Tersi **çapraz-kullanıcı sızıntıdır**: zamanlanmış bir rapor kendi kimliğini
    geçse bile, isteği tetikleyen kullanıcının kimliğiyle koşardı."""
    src = (_KOK / "app/wren_service.py").read_text(encoding="utf-8")
    agac = ast.parse(src)
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "_oturum_ozellikleri")
    govde = ast.unparse(fn)
    assert "if principal is None:" in govde, (
        "🔴 Bağlam açık argümanı ezebiliyor — arka plan işleri yanlış kimlikle koşar.")
    assert "istek_kimligi.simdiki()" in govde


def test_BAGLAM_ARGUMAN_YOKKEN_devreye_giriyor():
    """Borcun kapanma noktası: `principal` geçmeyen 36 çağrı sitesi artık kimliği
    **bağlamdan** alıyor."""
    from app import rls

    p = _Sahte("u1", is_superadmin=True)
    with istek_kimligi.IstekKimligi(p):
        assert rls.oturum_ozellikleri(istek_kimligi.simdiki()), (
            "🔴 Bağlamdaki kimlik oturum özelliği üretmiyor")


# --- Kimlik DOĞDUĞU yerde ayarlanıyor --------------------------------------------------

def test_KIMLIK_DOGDUGU_YERDE_ayarlaniyor():
    """🔴 İki sahip olsaydı ayrışırlardı. Ve `wren_service`'in bir `Request` görmesi, bir
    SQL derleyicisini **HTTP katmanına** bağlardı: test edilemez ve HTTP-dışı çağrılarda
    (zamanlayıcı, MCP) kullanılamaz olurdu."""
    src = (_KOK / "app/auth/dependencies.py").read_text(encoding="utf-8")
    assert "istek_kimligi.ayarla(principal)" in src
    agac = ast.parse(src)
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "get_current_principal")
    assert "istek_kimligi.ayarla" in ast.unparse(fn)


def test_TEK_AYAR_NOKTASI():
    """⚠ *Aynı kuralın iki sahibi ayrışır.* Kimlik yalnız bir yerde ayarlanmalı."""
    ayar = []
    for p in sorted((_KOK / "app").rglob("*.py")):
        if p.name == "istek_kimligi.py":
            continue
        if "istek_kimligi.ayarla(" in p.read_text(encoding="utf-8"):
            ayar.append(p.relative_to(_KOK).as_posix())
    assert ayar == ["app/auth/dependencies.py"], (
        f"🔴 Kimlik birden çok yerde ayarlanıyor: {ayar}")


# --- ContextVar'ın BİLİNEN sınırı ------------------------------------------------------

def test_ASYNC_GOREVLER_birbirini_GORMUYOR():
    """🔴 **Kapının en önemli iddiası.** Her istek kendi `asyncio.Task`'ındadır ve
    `contextvars` her Task'a **kopyalanır** — bu yüzden `get_current_principal`'da
    sıfırlama gerekmiyor.

    Bu test o iddiayı **ölçer**: iki eşzamanlı görev birbirinin kimliğini görmemeli.
    """
    async def gorev(ad, gecikme):
        istek_kimligi.ayarla(_Sahte(ad))
        await asyncio.sleep(gecikme)
        return istek_kimligi.simdiki().user_id

    async def kos():
        return await asyncio.gather(gorev("a", 0.02), gorev("b", 0.01))

    assert asyncio.run(kos()) == ["a", "b"], (
        "🔴 İki eşzamanlı istek birbirinin kimliğini gördü — çapraz-kullanıcı sızıntı.")


def test_THREAD_HAVUZU_baglami_KOPYALAMIYOR_ve_bu_YAZILI():
    """🔴 Bilinen sınır: `run_in_executor` bağlamı **kopyalamaz**. İş kimliği görmez ve
    **sessizce** kimliksiz koşar — *güvenli* yön ama *yanlış* sonuç: kullanıcı kendi
    görmeye yetkili olduğu veriyi göremez."""
    p = _Sahte("u1")
    with istek_kimligi.IstekKimligi(p):
        with ThreadPoolExecutor(max_workers=1) as ex:
            ciplak = ex.submit(istek_kimligi.simdiki).result()
    assert ciplak is None, (
        "⚠ Beklenmedik: thread havuzu bağlamı kopyaladı. Sınır değiştiyse "
        "`kimlik_kopyala()`nın gerekçesi güncellenmeli.")


def test_KIMLIK_KOPYALA_o_SINIRI_kapatiyor():
    """`kimlik_kopyala()` kimliği **sarıldığı anda** yakalar: iş kuyruğa girdikten sonra
    istek biter ve ContextVar sıfırlanır."""
    p = _Sahte("u1")
    with istek_kimligi.IstekKimligi(p):
        sarili = istek_kimligi.kimlik_kopyala(lambda: istek_kimligi.simdiki())
    # İstek bitti — ama sarmalayıcı kimliği taşıyor.
    assert istek_kimligi.simdiki() is None
    with ThreadPoolExecutor(max_workers=1) as ex:
        assert ex.submit(sarili).result() is p


def test_KOPYALAYAN_sarmal_da_SIFIRLIYOR():
    """⚠ Havuzdaki bir thread **yeniden kullanılır**: sarmalayıcı kimliği bırakmazsa,
    aynı thread'e düşen bir sonraki iş onu **miras alır**."""
    p = _Sahte("u1")
    with istek_kimligi.IstekKimligi(p):
        sarili = istek_kimligi.kimlik_kopyala(lambda: None)
    with ThreadPoolExecutor(max_workers=1) as ex:
        ex.submit(sarili).result()
        assert ex.submit(istek_kimligi.simdiki).result() is None, (
            "🔴 Sarmalayıcı kimliği bıraktı — aynı thread'e düşen sonraki iş onu miras aldı.")


# --- Bu bir GÜVENLİK SINIRI değil ------------------------------------------------------

def test_YETKI_OTORITESI_hala_authorize():
    """⚠ *Kimliği taşımak, yetkiyi vermek değildir.* Bu modül `can`/`authorize`
    çağırmaz."""
    src = (_KOK / "app/istek_kimligi.py").read_text(encoding="utf-8")
    agac = ast.parse(src)
    cagrilar = {n.func.id for n in ast.walk(agac)
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert not ({"authorize", "can", "permissions_for"} & cagrilar), (
        "🔴 Kimlik taşıyıcısı yetki kararı veriyor — iki sorumluluk tek modülde.")
