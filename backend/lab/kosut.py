"""KOŞUT DEĞERLENDİRME — `route()` çağrılarını çekirdeklere dağıtır.

## Neden ayrı bir modül

Aynı paralelleştirme deseni **üç** yerde gerekiyordu: `gercek_dunya` · `metamorfik` ·
ileride gelecek olanlar. Üçüne ayrı ayrı yazmak, bu deponun defterindeki **"aynı
kuralın iki sahibi"** sınıfını üçe katlardı: biri `spawn` kullanır öteki `fork`,
biri şemayı yeniden yükler öteki miras alır, ve ölçümler sessizce ayrışır.

## 🔴 Kapsamdan ödün YOK — payda BÖLÜNÜR, azaltılmaz

Korpusta ölçülmüş ders (`CLAUDE.md`): 13 dk 18 sn → 1 dk 50 sn, ve **sayılar
birebir aynı** çıktı. *Hız kapsamdan değil, çekirdekten satın alınır.* Burada da
öyle: soru listesi dilimlenir, her dilim kendi sürecinde koşar, sonuçlar **giriş
sırasına göre** birleşir — yani çıktı seri koşumla aynıdır.

## ⚠ `spawn`, `fork` DEĞİL

`fork` ile alt süreçler ebeveynin açık nesnelerini miras alır; `tests/conftest.py`
control-plane SQLite'ını **import anında** kuruyor ve dilimler aynı dosyaya girip
çöküyordu (korpusta ölçüldü: payda 445→255, kapı doğru şekilde kırmızı verdi).
`spawn` her süreçte ortamı **baştan** kurar.
"""

from __future__ import annotations

import multiprocessing as mp
import os
from concurrent.futures import ProcessPoolExecutor

#: PC'yi boğmadan kullanılacak süreç sayısı — `nl_corpus` ile **aynı** kural.
#: Çekirdek sayısından 4 eksik: kullanıcı kısıtı *"aşırıya kaçma, PC zarar görmesin"*.
_TAVAN = 16


def surec_sayisi() -> int:
    ayar = os.environ.get("DIMA_KORPUS_PARALEL")            # ⚠ korpusla AYNI env
    if ayar:
        return max(1, int(ayar))
    return max(1, min(_TAVAN, (os.cpu_count() or 4) - 4))


def _dilim_kos(arg):
    """Alt süreçte koşar: şemayı **kendi** yükler, sorularını değerlendirir."""
    sorular, hangi = arg
    from app.config import get_settings
    from app.wren_service import WrenService
    from app import cube_router

    s = get_settings()
    svc = WrenService(project_dir=s.resolved_project_dir(), datasource=s.datasource,
                      connection_info=s.connection_dict())
    schema = svc.schema()
    if hangi == "imza":
        from lab.metamorfik import imza
        cikti = []
        for q in sorular:
            try:
                cikti.append(imza(cube_router.route(q, schema)))
            except Exception:                               # noqa: BLE001
                cikti.append(("HATA",))
        return cikti
    # hangi == "ham": route() çıktısının kendisi (pickle'lanabilir sözlük)
    cikti = []
    for q in sorular:
        try:
            cikti.append(cube_router.route(q, schema))
        except Exception as exc:                            # noqa: BLE001
            cikti.append({"__hata__": str(exc)[:120]})
    return cikti


def degerlendir(sorular: list[str], *, hangi: str = "ham",
                surec: int | None = None) -> list:
    """Soruları paralel değerlendirir; **giriş sırasını korur**.

    ⚠ Sıra korunmazsa aynı koşum farklı sıralı rapor üretir ve iki koşumun farkı
    *"kod değişti"* değil *"sıra değişti"* olur — teşhis imkânsızlaşır.
    """
    n = surec or surec_sayisi()
    if n <= 1 or len(sorular) < 200:
        # ⚠ Küçük kümede süreç kurma maliyeti kazançtan büyük — ölçüldü.
        return _dilim_kos((sorular, hangi))
    # ⚡ DİLİM SAYISI — **ölçülerek** seçildi, varsayılarak değil.
    #
    # Önce "yük dengeleme" gerekçesiyle `n * 4` yazdım (en yavaş dilim ötekileri
    # bekletmesin diye). Ölçtüm: **1:12**. Süreç başına tek dilimle: **1:08**.
    # Yani dört kat dilim, dengelemeden kazandığından fazlasını **pickle turlarında**
    # geri veriyor.
    #
    # > ⚠ *Bir iyileştirme, ölçülmeden iyileştirme değildir.* Makul görünen gerekçe
    # > (yük dengeleme) doğruydu; büyüklüğü yanlıştı. `n * 2` ikisinin ortası ve
    # > ölçümde farksız — dengelemeyi bir miktar korur, maliyeti düşük tutar.
    dilim_sayisi = n * 2
    boy = max(1, (len(sorular) + dilim_sayisi - 1) // dilim_sayisi)
    dilimler = [(sorular[i:i + boy], hangi) for i in range(0, len(sorular), boy)]
    out: list = []
    with ProcessPoolExecutor(max_workers=n,
                             mp_context=mp.get_context("spawn")) as pool:
        for parca in pool.map(_dilim_kos, dilimler):
            out.extend(parca)
    return out
