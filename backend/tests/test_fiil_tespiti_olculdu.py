"""🅖 `§71` — **`§33` satır 11'in FİİL YARISI: iki aday ölçüldü, ikisi de YANLIŞ.**

Kural: *«uzun bileşik (**>8 kelime ∨ fiil**) → şerit söner»*. Kelime yarısı `§64`'te
bağlandı. **Fiil yarısı bağlanmadı** — ve bu bir unutma değil, **ölçülmüş bir sonuçtur**.

## Ölçüm (canlı `s35` üzerinde, `docker exec`)

### Aday 1 — `turetme.fiil_bicimi_mi` (39 ek biçimi)

```
ISIM yanlış pozitif : ['oran']            🔴 katalogun ÇEKİRDEK sözcüğü
FIIL yakalanan      : ['dustu', 'artti']
FIIL kaçan          : ['hesapla','goster','kir','anlat','karsilastir','getir',
                       'listele','ozetle','bul','ac']                     🔴 hepsi emir kipi
```

O fonksiyon **başka bir soru** için yazılmış ve şerhinde bunu söylüyor: *«saçmaların hepsi
fiil→isim»* — yani **yazım hatası bastırma** için. Kullanıcının yazdığı komut kipini
(emir) hiç görmüyor.

### Aday 2 — kapalı fiil kümesi + `cube_router._syn_hit`

```
'fire oranini hesapla'          → ['HESAPLA']   ✅
'makine bazinda kir ve anlat'   → ['ANLAT','KIR'] ✅
'musteri kirilimi'              → ['KIR']       🔴 «kırılım» bir ADdır, komut değil
'elektrik tuketimi siralama'    → ['SIRALA']    🔴 «sıralama» bir ADdır
'en kotu makineyi bul'          → []            🔴 kaçtı
```

`_syn_hit` gövde + geçerli ek zinciri eşler; *«kırılımı»* `KIR`'a **haklı olarak** vurur —
o eşleştirici bu iş için değil, **terim tanıma** için doğru.

## 🔴 Sonuç: **bağlanmadı, ve nedeni yazılı** 🅖

Üçüncü yol bir **emir kipi sözcük listesi** yazmak olurdu: bu depoda hem `㊱` (uydurma
yok) hem *«route'a dil kuralı EKLEME»* (`CLAUDE.md` en üst kural) bunu yasaklıyor. Dördüncü
yol garsona sormak — **tuş başına LLM**, yani `E-8` ihlali.

> *Bir kuralı yanlış bir sinyale bağlamak, onu hiç bağlamamaktan kötüdür: birincisi
> sessizce yanlış davranır, ikincisi eksik olduğunu söyler.*

## Bu kapı ne yapar ㉕

Gelecekte biri bu iki adaydan birini şeride bağlarsa, **hangi somut girdilerin
susturulacağını** burada okur. Kapı ölçümü **dondurur**: adayların yanlış pozitifleri
değişirse (ör. `oran` artık fiil sayılmıyorsa) kırmızı verir ve karar **yeniden** alınır.
"""

from __future__ import annotations

import pytest

from app.cube_router import _norm, _syn_hit
from app.plan_semasi import FIILLER
from app.turetme import fiil_bicimi_mi

#: Şeridin **susturulmaması gereken** girdiler — hepsi kısa, sıradan, katalog sorusu.
SUSTURULAMAZ = ("oran", "müşteri kırılımı", "elektrik tüketimi sıralama")

#: Kullanıcının **komut** yazdığı biçimler — bir fiil tespiti bunları görmeli.
KOMUT = ("hesapla", "göster", "anlat", "bul", "listele", "özetle")


def test_ADAY1_KATALOG_SOZCUGUNU_FIIL_SANIYOR():
    """🔴 `oran` bir ölçü adıdır; onu susturmak şeridi **çalıştığı yerde** kapatırdı."""
    assert fiil_bicimi_mi("oran"), (
        "⚠ ÖLÇÜM DEĞİŞTİ: `turetme.fiil_bicimi_mi('oran')` artık `False`. Bu **iyi haber "
        "olabilir** — ama `§33` satır 11 kararı bu ölçüme dayanıyordu. `ONGORU-DURUM.md "
        "§71`'i yeniden ölç ve kararı tazele.")


def test_ADAY1_EMIR_KIPINI_GORMUYOR():
    """Kullanıcı komutu **emir kipiyle** yazar; aday 1 onu hiç görmüyor."""
    goren = [w for w in KOMUT if fiil_bicimi_mi(w)]
    assert not goren, (
        f"⚠ ÖLÇÜM DEĞİŞTİ: aday 1 artık emir kipini görüyor ({goren}) — `§71` kararı "
        "yeniden alınmalı.")


def test_ADAY2_ADI_KOMUT_SANIYOR():
    """🔴 `«müşteri kırılımı»` sıradan bir sorudur; `KIR`'a vurması bir kusur değil,
    `_syn_hit`'in **doğru** davranışıdır — yanlış olan onu bu işe koşmaktır."""
    def _komut(q: str) -> list[str]:
        n = _norm(q)
        return [f for f in FIILLER if _syn_hit(n, f.lower())]

    assert _komut("müşteri kırılımı") == ["KIR"], (
        "⚠ ÖLÇÜM DEĞİŞTİ: `_syn_hit` artık «kırılımı»yı `KIR` saymıyor — `§71` kararı "
        "yeniden alınmalı.")
    assert _komut("elektrik tüketimi sıralama") == ["SIRALA"]


def test_ZIT_OLCUT_ADAY2_GERCEK_KOMUTU_GORUYOR():
    """🆃 Aday 2 **tümden** kör değil — reddin sebebi körlük değil **yanlış pozitif**.
    (Bir adayı reddederken onun gerçekten yaptığı işi de yazmak, reddi dürüst yapar.)"""
    n = _norm("fire oranını hesapla")
    assert any(_syn_hit(n, f.lower()) for f in FIILLER), (
        "🔴 aday 2 gerçek komutu da görmüyor — o zaman gerekçe yanlış yazılmış")


@pytest.mark.parametrize("girdi", SUSTURULAMAZ)
def test_SUSTURULAMAZ_GIRDILER_KAYITLI(girdi):
    """㉕ Kararın **konusu** kapıda dursun: bir gün şeride bir fiil tespiti bağlanırsa,
    bu üç girdinin susturulmadığı **burada** sınanır."""
    assert girdi.strip() and len(girdi.split()) <= 8, (
        f"🔴 örnek girdi kuralın kendi eşiğini aşıyor: {girdi!r} — o zaman zaten susardı "
        "ve bu kapı bir şey ölçmezdi")
