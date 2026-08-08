"""🔴 **DUVAR-SAATİ BÜTÇESİ — tek sahip.**

## Ölçülen kusur: bütçe yazılıydı, çalışmıyordu

İki ayrı yerde bir duvar-saati bütçesi vardı ve **ikisi de aynı sebeple kâğıt
üstündeydi**:

| yer | bütçe | canlı ölçüm | log |
|---|---|---|---|
| `ask.py::_select_consistent` (Intent oyları) | 20 sn | **39.115 ms** | *«oy düştü»* |
| `answer.py::_anlati_ekle` (T2 anlatısı) | 8 sn | **81.656 ms** | *«süssüz ama doğru cevap»* |

⊙ İkisi de aşımı **doğru tespit etti ve logladı** — sonra yine sonuna kadar bekledi.

Sebep tek satırdı ve ikisinde de aynıydı:

```python
with cf.ThreadPoolExecutor(...) as ex:      # ← çıkışta shutdown(wait=True)
    ...
    fut.result(timeout=kalan)               # ← TimeoutError atar, oy düşer
# ← ve BURADA yavaş iş parçacığı beklenir
```

`future.result(timeout=…)` **beklemeyi** keser, **işi** değil. `with` bloğundan çıkarken
`ThreadPoolExecutor.__exit__` → `shutdown(wait=True)` çağrılır ve süreç orada, tam da
bütçenin bittiğini ilan ettiği yerde, işin bitmesini bekler.

🔴 **`answer.py`'de bu, kodun kendi yorumuyla çelişiyordu:**

> *«⚠ İş arka planda bitmeye devam eder (thread öldürülemez) — ama cevabı bekletmez.»*

Niyet doğruydu; `with` onu sessizce iptal ediyordu.

*Bir bütçe, çıkışında bekleyen bir bağlam yöneticisinin içindeyse bütçe değildir —
yalnız bir log satırıdır.*

## En pahalı tek ölçüm

`b5` turu (`personel çalışma süreleri…`): iki oy **6.775 ms**'de aynı cevapta uzlaştı
(`{"cube":null}` — dürüst red). Üçüncü oy **37.840 ms** sürdü ve **aynı cevabı** verdi.
Kullanıcı, sistemin **6,7 saniyede bildiği** bir cevap için **39 saniye** bekledi.

## Neden AYRI BİR MODÜL (ve neden `KAT-1`)

*"Bir bütçe nasıl uygulanır"* sorusunun **tek** bir cevabı olmalı. İki çağrı yerinde iki
kopya vardı ve **ikisi de aynı hatayı** taşıyordu — `KAT-1`'in ders kitabı örneği:
aynı kuralın iki sahibi, aynı kusuru iki kez.

## Sınır: bu modül işi ÖLDÜRMEZ

Python'da bir iş parçacığı dışarıdan sonlandırılamaz. Bu modülün yaptığı **beklemeyi**
kesmektir; iş arka planda biter ve sonucu atılır. Yani bütçe bir **iptal** değil, bir
**vazgeçiş**tir — ve tam olarak kullanıcının hissettiği şey budur.
"""

from __future__ import annotations

import concurrent.futures as _cf
import time as _time
from collections.abc import Callable
from typing import Any

#: Bütçe aşımının işareti. 🔴 **`None` KULLANILAMAZ**: `None` meşru bir sonuçtur
#: (`select_cube` çekimser kalabilir, `llm.anlat` boş dönebilir) ve aşımla karıştırılırsa
#: çağıran *"model bilmiyor"* ile *"model geç kaldı"*yı ayırt edemez.
#: *İki farklı sebebi tek bir değerle temsil etmek, ikisini de kaybetmektir.*
ASIM = object()


def kos(isler: list[Callable[[], Any]], *, saniye: float,
        ad: str = "iş", log=None) -> list[Any]:
    """`isler`'i paralel koşar, **toplam** `saniye` bütçesiyle sonuçları toplar.

    Bütçesi biten her iş için `ASIM` döner (sırayla, girdiyle **birebir hizalı**).

    ⚠ Son tarih **gönderimden önce** hesaplanır: `submit`'ten sonra hesaplamak, iş
    kuyrukta beklerken geçen süreyi bütçenin dışında bırakırdı — ve havuz `max_workers`
    ile sınırlı olduğu için o bekleme **gerçektir**.

    ⚠ Bütçe **toplamdır, iş başına değil**: her işe ayrı `timeout` vermek, bütçeyi iş
    sayısıyla çarpar (ölçüldü, `§27.2`).

    ⚠ Aşım dışındaki istisnalar **yükseltilir** — bugünkü iki çağrı yerinin davranışı
    budur ve bir hatayı bütçe aşımı gibi göstermek onu gizlemek olurdu.
    """
    if not isler:
        return []
    bitis = _time.monotonic() + max(0.0, saniye)
    ex = _cf.ThreadPoolExecutor(max_workers=len(isler))
    try:
        gonderilen = [ex.submit(f) for f in isler]
        cikti: list[Any] = []
        for fu in gonderilen:
            try:
                cikti.append(fu.result(timeout=max(0.0, bitis - _time.monotonic())))
            except _cf.TimeoutError:
                if log is not None:
                    log.warning("%s BÜTÇEYİ AŞTI (%.1f sn) — BEKLENMİYOR", ad, saniye)
                cikti.append(ASIM)
        return cikti
    finally:
        # 🔴 **Bu satır kusurun tamamıdır.** `wait=False` beklemeyi keser;
        # `cancel_futures=True` henüz **başlamamış** işleri iptal eder (başlamış olanlar
        # sürer — thread öldürülemez). `with` bloğu bunun yerine `wait=True` çağırıyordu.
        ex.shutdown(wait=False, cancel_futures=True)
