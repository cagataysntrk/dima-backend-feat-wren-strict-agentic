"""FAZ 2.6 — **MALİ TAKVİM.** *"Bu yıl"* her şirkette Ocak'ta başlamaz.

## 🔴 ÖLÇÜLEN SESSİZ-YANLIŞ — bu yüzden BAYRAKSIZ

`cube_router._current_period_filter` *"bu yıl"*ı `today.replace(month=1, day=1)` diye
çözüyordu; `yoy.compute` de `f"{date.today().year}-01-01"`. Yani **mali yılı Ocak'ta
başlamayan her müşteride** cevap yanlış — ama rozet `◆ CUBE`, güven `1.0`, makbuz tam.

*Sessiz-yanlışın tanımı budur: sistem emin, sayı yanlış.* Ve bir bayrağın arkasına
koymak, yanlışı **varsayılan** yapmak olurdu — o yüzden bu madde bayraksızdır.

## ⚠ Tek sahip: `yil_penceresi`

Dönem penceresini iki yerde hesaplamak (router + `yoy`) tam olarak bu kusurun doğuş
biçimiydi. Hesap **burada** yapılır; iki çağıran da onu **çağırır**.

## Neden ContextVar — ve neden yeni bir mekanizma DEĞİL

`date_filters(q, time_dim)`'in imzası beş çağıranı taşıyor; mali ayı parametre olarak
geçirmek hepsini kırardı. Bu deponun **iki kez kanıtlanmış** kalıbı var (`llm.py`'nin
`_llm_usage_var`'ı, `cube_router`'ın `_reddi_var`'ı): derin bir fonksiyon okur, sığ bir
fonksiyon **kurar**, aradaki imzalar sabit kalır. Üçüncü kez **aynı** kalıp; yenisi
icat edilmedi.

FastAPI sync endpoint'i kendi kopya-context'inde koştuğu için istekler izoledir.

> **Karar kaydı: `ADR-0027`** — mali takvim — takvim yılı bir varsayımdır.
> ⚠ Atıf, kararın **yaşadığı yere** yazılır: kayıt ile kod birbirini ancak
> böyle doğrulayabilir (`tests/test_adr_dosyalari.py` iki yönü de kilitler).
"""

from __future__ import annotations

import contextvars
from datetime import date

#: Varsayılan: **takvim yılı**. Yapılandırılmamış bir tenant bugünkü davranışı görür —
#: yani bu madde hiçbir mevcut kurulumu değiştirmez, yalnız yanlışı DÜZELTİLEBİLİR kılar.
VARSAYILAN_BASLANGIC_AY = 1

_ay_var: contextvars.ContextVar[int] = contextvars.ContextVar(
    "dima_mali_yil_baslangic_ay", default=VARSAYILAN_BASLANGIC_AY)


def kur(baslangic_ay: int | None) -> None:
    """İstek başında mali yıl başlangıcını kurar. `None`/geçersiz → takvim yılı.

    ⚠ Geçersiz bir ay (`0`, `13`, `"nisan"`) **sessizce takvim yılına** düşer: bir
    yapılandırma hatası yüzünden *"bu yıl"* sorusunu **cevapsız** bırakmak, kullanıcının
    yanlışını sistemin arızasına çevirirdi. Düşüş görünürdür (`aktif_ay()` okunabilir).
    """
    ay = baslangic_ay if isinstance(baslangic_ay, int) and 1 <= baslangic_ay <= 12 \
        else VARSAYILAN_BASLANGIC_AY
    _ay_var.set(ay)


def aktif_ay() -> int:
    return _ay_var.get()


def takvim_mi() -> bool:
    """Mali yıl takvim yılıyla **aynı mı**? Etiket/uyarı kararları buna bakar."""
    return aktif_ay() == VARSAYILAN_BASLANGIC_AY


def yil_basi(bugun: date, baslangic_ay: int | None = None) -> date:
    """İçinde bulunulan **mali yılın** ilk günü.

    Nisan başlangıçlı bir şirkette `2026-02-10` → `2025-04-01`: takvim yılı değişti ama
    **mali yıl değişmedi**. Bu tek satır, maddenin bütün değeridir.
    """
    ay = baslangic_ay if baslangic_ay is not None else aktif_ay()
    ay = ay if isinstance(ay, int) and 1 <= ay <= 12 else VARSAYILAN_BASLANGIC_AY
    yil = bugun.year if bugun.month >= ay else bugun.year - 1
    return date(yil, ay, 1)


def yil_penceresi(bugun: date, *, kac_yil_once: int = 0,
                  baslangic_ay: int | None = None) -> tuple[date, date]:
    """`(başlangıç, bitiş)` — mali yıl penceresi. `kac_yil_once=1` → **geçen** mali yıl.

    🔴 Bitiş, **bir sonraki mali yılın ilk gününden bir gün öncesidir** — `12-31` sabiti
    yazmak, mali yılı Ocak'ta başlamayan şirkette pencereyi **kaydırırdı**.
    """
    bas = yil_basi(bugun, baslangic_ay)
    bas = date(bas.year - kac_yil_once, bas.month, 1)
    sonraki = date(bas.year + 1, bas.month, 1)
    return bas, date.fromordinal(sonraki.toordinal() - 1)


def etiket(bugun: date, baslangic_ay: int | None = None) -> str:
    """Kullanıcıya gösterilecek dönem eki — mali yıl takvimden **farklıysa** söyler.

    🔴 *Takvim yılından farklı bir pencereyi "bu yıl" diye sunmak, doğru sayıyı yanlış
    soruya cevap yapar.* Kullanıcı hangi pencereyi gördüğünü bilmeli.
    """
    ay = baslangic_ay if baslangic_ay is not None else aktif_ay()
    if ay == VARSAYILAN_BASLANGIC_AY:
        return ""
    bas, son = yil_penceresi(bugun, baslangic_ay=ay)
    return f"mali yıl: {bas.isoformat()} → {son.isoformat()}"
