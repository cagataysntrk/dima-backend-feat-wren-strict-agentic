"""Paralel koşum izolasyonu — her sürece KENDİ derlenmiş proje ağacı.

## Neden var

`compose_and_build()` çıktısını `settings.project_dir`'e yazar ve `build_lock_for()`
yalnız **dizin başına** kilitler. İki süreç aynı `demo/wren-project`'e aynı anda
girerse yarışırlar; bu operasyonun en pahalı kusuru (`gitas` korpustan tamamen
düştü, payda 445→342 indi, doğruluk **yükseldi**) tam olarak bu yarıştı. Eski çözüm
bir YASAKTI — *"iki test konteyneri ASLA paralel koşmaz"* — yani doğruluk, hız
feda edilerek satın alınmıştı.

Bu modül yasağı gereksiz kılar: **ayrı dizin = yarış yok**, kilit beklemesi de yok.

## Neden düz bir `mkdtemp` YETMEZ

Kod `project_dir`'den **yukarı yürüyerek** başka yollar türetiyor (ör.
`<project_dir>/../../eval/cases.yaml`). Düz geçici dizinle bu türetme
`/tmp/eval/cases.yaml`'a çıkar ve 15 test `FileNotFoundError` ile düşer (ölçüldü).
Bu yüzden ayna repo **derinliğini birebir korur**.

## Neden `companies/` KOPYALANIR, bağlanmaz

Ölçü terfisi şirket katmanına **dosya yazar**. Sembolik bağla bu yazım gerçek repoya
sızıp öteki sürece görünüyordu (*"ZATEN vardı, önceki koşum temizlenmemiş"* — ölçüldü).
572 KB; kopyalama maliyeti ölçülemeyecek kadar küçük, sızıntının bedeli değil.
"""

from __future__ import annotations

import os
import shutil
import tempfile

#: Yazılan tek yer — ayna içindeki derleme çıktısı. Ötekiler salt-okunur bağdır.
_CIKTI = "wren-project"
#: Süreç içinde MUTASYONA uğrayan taban katmanı → bağ değil, kopya.
_KOPYALANAN = "companies"


def izole_proje_ayna(etiket: str, backend_kok: str | None = None) -> str:
    """`etiket` için izole bir proje ağacı kurar ve `DIMA_PROJECT_DIR` yolunu döndürür.

    Ortam değişkenini **çağıran** yazar (import sırası kritik olabilir):

        os.environ["DIMA_PROJECT_DIR"] = izole_proje_ayna("gw0")

    Ayna yapısı::

        <tmp>/backend/{app,eval,lab,...}   → gerçek dizinlere sembolik bağ
        <tmp>/backend/demo/{packs,...}     → gerçek dizinlere sembolik bağ
        <tmp>/backend/demo/companies/      → KOPYA (süreç burayı değiştirebilir)
        <tmp>/backend/demo/wren-project    → bu sürece ÖZEL derleme çıktısı
    """
    real_backend = backend_kok or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    real_demo = os.path.join(real_backend, "demo")

    kok = tempfile.mkdtemp(prefix=f"dima-ayna-{etiket}-")
    ayna = os.path.join(kok, "backend")
    ayna_demo = os.path.join(ayna, "demo")
    os.makedirs(ayna_demo)

    for ad in os.listdir(real_backend):
        if ad != "demo":
            os.symlink(os.path.join(real_backend, ad), os.path.join(ayna, ad))

    for ad in os.listdir(real_demo):
        if ad == _CIKTI:
            continue
        kaynak, hedef = os.path.join(real_demo, ad), os.path.join(ayna_demo, ad)
        if ad == _KOPYALANAN:
            shutil.copytree(kaynak, hedef, symlinks=True)
        else:
            os.symlink(kaynak, hedef)

    return os.path.join(ayna_demo, _CIKTI)
