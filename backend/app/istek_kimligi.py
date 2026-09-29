"""**İSTEK KİMLİĞİ** — *"bu sorguyu kim soruyor"*un tek sahibi. [bayraksız: altyapı]

## Çözdüğü borç

`OPERASYON-DURUM.md` · **açık borç 1**: *"36 çağrı sitesi kimlik geçmiyor →
`motor_cls=on` KİLİTLİ."* `MIMARI.md §6.3c` aynı cümleyi taşıyor ve `motor_cls` bayrağı
**bu yüzden** `off`: kimlik taşımayan bir çağrı, motor-seviyesi kolon maskesini
**sessizce** atlar.

## 🔴 Neden 36 imza DEĞİŞTİRİLMEDİ

Açık seçenek `principal`ı `kpi.py` · `statements.py` · `yoy.py` · `report.py` ·
`schedules.py` · `fanout.py` · dört router üzerinden **tek tek geçirmekti**. Üç sebeple
reddedildi:

| # | Sebep |
|---|---|
| 1 | 🔴 **Bir sonraki çağrı sitesi yine açık doğar.** İmza değiştirmek bugünkü 36'yı kapatır; yarın yazılan 37.'si `principal` geçmeyi **unutabilir** ve hiçbir şey kırılmaz — *fail-open* bir düzeltme, düzeltme değildir |
| 2 | Otuz altı imza + çağıranları, bir **davranış** değişikliği olmadan yüzlerce satır oynatır; her satır bir gerileme yüzeyidir |
| 3 | `principal` bu fonksiyonların **işi değil**: `yoy.py` dönemsel kıyas hesaplar, kimlik taşımaz. Bir parametreyi taşımak için var olmak, o modülü kimlik katmanına **bağımlı** yapar |

## Neden `ContextVar` — ve neden yeni bir mekanizma DEĞİL

Bu depoda aynı desen **üç kez** kullanıldı ve üçünde de aynı sebeple:
`mali_takvim._ay_var` (mali yıl başlangıcı) · `cube_router._reddi_var` (red gerekçesi) ·
`cube_router`'ın kendi ContextVar notu. Hepsi *"istek boyunca doğru olan ama her imzaya
sığmayan"* bir bağlamı taşır. Kimlik **tam olarak** o sınıftır.

⚠ `contextvars` `asyncio` görevleri arasında **kopyalanır**, `threading` havuzunda
**kopyalanmaz**: `run_in_executor`'a giden bir iş, kimliği **görmez**. Bu bir sınırdır ve
aşağıda `kimlik_kopyala()` ile açıkça ele alınır — *bir sınırı bilmeden kullanmak, onu
bir arızaya çevirir.*

## 🔴 Öncelik sırası: AÇIK argüman ContextVar'ı EZER

`svc.query(sql, principal=p)` yazan bir çağrı **p'yi kullanır**, ContextVar'ı değil.
Tersi olsaydı, bir arka plan işi (zamanlanmış rapor) kendi kimliğini geçse bile isteği
tetikleyen kullanıcının kimliğiyle koşardı — **çapraz-kullanıcı sızıntı**.

## ⚠ Ve bu bir GÜVENLİK SINIRI DEĞİLDİR

`authorize()` hâlâ tek yetki otoritesidir; bu modül yalnız *"kim"* sorusunun cevabını
**taşır**. Kimliği taşımak, yetkiyi vermek değildir.
"""

from __future__ import annotations

import contextvars
from typing import Any

#: İstek boyunca geçerli kimlik. Varsayılan `None` — ve bu **fail-safe** yöndür:
#: kimlik yoksa `rls.oturum_ozellikleri()` boş döner, motor *"property yok"* dalına girer
#: ve `motor_cls=on` iken **en kısıtlı** gizlilik seviyesi uygulanır.
_kimlik: contextvars.ContextVar[Any] = contextvars.ContextVar("dima_istek_kimligi",
                                                             default=None)


def ayarla(principal: Any):
    """Kimliği bu bağlam için ayarlar; **geri alma token'ı** döner.

    🔴 Token **kullanılmalı** (`sifirla(token)`): `set()`in dönüşünü atmak, kimliğin
    bir sonraki isteğe **sızmasına** yol açar — aynı thread'i yeniden kullanan bir
    sunucuda bu, **başka bir kullanıcının** verisini görmek demektir.
    """
    return _kimlik.set(principal)


def sifirla(token) -> None:
    """`ayarla()`nın token'ıyla önceki değeri geri koyar.

    ⚠ `_kimlik.set(None)` **yeterli değildir**: iç içe bir bağlamda dıştaki kimliği
    `None`'a düşürür. `reset` yığını doğru çözer.
    """
    _kimlik.reset(token)


def simdiki() -> Any:
    """Bu bağlamda geçerli kimlik ya da `None`."""
    return _kimlik.get()


def kimlik_kopyala(fn):
    """Mevcut kimliği **yakalayıp** başka bir bağlamda (thread havuzu) yeniden kurar.

    🔴 `contextvars` `asyncio` görevlerine kopyalanır ama `ThreadPoolExecutor`'a
    **kopyalanmaz**. `run_in_executor`'a giden bir iş kimliği görmez ve sessizce
    kimliksiz koşar — yani **en kısıtlı** seviyede. Bu *güvenli* yön ama *yanlış*
    sonuçtur: kullanıcı kendi görmeye yetkili olduğu veriyi göremez.

    ⚠ Sarmalayıcı kimliği **çağrıldığı anda değil, sarıldığı anda** yakalar: iş kuyruğa
    girdikten sonra istek biter ve ContextVar sıfırlanır.
    """
    yakalanan = _kimlik.get()

    def sarmal(*a, **kw):
        token = _kimlik.set(yakalanan)
        try:
            return fn(*a, **kw)
        finally:
            _kimlik.reset(token)

    return sarmal


class IstekKimligi:
    """`with IstekKimligi(principal): …` — token'ı unutulamaz hâle getirir.

    ⚠ *Doğru kullanımı hatırlamayı gerektiren bir API, er ya da geç yanlış kullanılır.*
    """

    def __init__(self, principal: Any) -> None:
        self._p = principal
        self._token = None

    def __enter__(self) -> "IstekKimligi":
        self._token = ayarla(self._p)
        return self

    def __exit__(self, *_exc) -> None:
        if self._token is not None:
            sifirla(self._token)
            self._token = None
