"""FAZ 3.6 — **COLD-START METRİK ÖNERİSİ** + **GÖRÜNMEZ KOLON.** [bayrak: `coldstart_metrik`]

## Ölçülen boşluk

`db_introspect.draft_mdl()` **zaten** model çıkarıyor; eksik olan **önem sıralamasıydı**:
yeni bir müşteri 200 tablo görüyor ve hangisinden başlayacağını **bilmiyor**. Bir liste,
sıralanmadığı sürece bir **yük**tür.

## 🔴 GÖRÜNMEZ KOLON — Plane Enforcer'ın UI karşılığı

Kapatılan bir kolon **MDL'ye hiç yazılmaz**, dolayısıyla **LLM onu asla göremez**.
*"Gösterme" ile "yazma" arasındaki fark, bu maddenin bütün değeridir:* gizlenen ama
yazılan bir kolon, bir prompt sızıntısında ya da bir Discovery sorgusunda **geri gelir**.

⚠ Bu bir **görünürlük ayarı değil, bir kapıdır**: `pii.py` maskeler (veri çıkışında),
burası **hiç üretmez** (şema girişinde). İkisi farklı katmandır ve
**biri ötekinin yerine geçmez** — maskelenen bir kolon hâlâ MDL'de durur ve LLM onu
**görür**.

## ⚠ Sıralama TAHMİN DEĞİL, SİNYAL

İki sinyal toplanır: **satır sayısı** (büyük tablo = iş hacmi) ve **kolon-adı sinyali**
(`tutar`/`miktar`/`adet` gibi ölçü adayları). ⚠ Bir tabloyu *"önemsiz"* diye **gizlemez**
— yalnız sıralar. *Sıralama bir öneridir; gizleme bir karardır ve kararı kullanıcı verir.*
"""

from __future__ import annotations

import re
from typing import Any

#: Ölçü adayı kolon-adı sinyalleri. ⚠ ADR-0008 kapsamında **bir sözlük değil**: burada
#: eşleşme bir **sıralama** üretir, bir cevap değil — yanlış sıralama bir soruyu
#: cevapsız bırakmaz, yalnız listede aşağı iter.
_OLCU_SINYALI = re.compile(
    r"(tutar|miktar|adet|sayi|fiyat|maliyet|bakiye|borc|alacak|kg|ton|sure|dakika"
    r"|amount|total|qty|quantity|price|cost|count|duration)", re.I)

#: Bir tablonun *"iş hacmi"* sinyali için satır eşiği — üstü **1.0**, altı orantılı.
#: ⚠ Eşik bir **normalizasyon** sabitidir, bir kalite yargısı değil.
SATIR_DOYMA = 100_000


def olcu_sinyali(kolonlar: list[str] | None) -> float:
    """Kolon adlarında ölçü sinyali oranı — `0.0…1.0`."""
    k = [str(x) for x in (kolonlar or []) if x]
    if not k:
        return 0.0
    return sum(1 for x in k if _OLCU_SINYALI.search(x)) / len(k)


def onem_puani(tablo: dict[str, Any]) -> float:
    """`0.0…1.0` — **iki sinyalin ortalaması**, uydurma bir ağırlık yok.

    🔴 Ağırlıkları (ör. `0.7 × satır + 0.3 × sinyal`) **kalibre etmeden** yazmak, bu
    deponun *"kalibre edilmemiş bir sayı güven değil süstür"* kuralının sıralama
    tarafındaki hâli olurdu. Eşit ağırlık, **bilmediğimizi beyan eden** ağırlıktır.
    """
    satir = min(float(tablo.get("row_count") or 0), SATIR_DOYMA) / SATIR_DOYMA
    return round((satir + olcu_sinyali(tablo.get("columns"))) / 2, 4)


def sirala(tablolar: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Tabloları **önem puanına** göre sıralar — hiçbirini **elemez**.

    ⚠ *Sıralama bir öneridir; gizleme bir karardır ve kararı kullanıcı verir.* Düşük
    puanlı bir tabloyu listeden düşürmek, müşterinin kendi verisini **göremediği** bir
    onboarding üretirdi.
    """
    return sorted(
        [{**t, "onem": onem_puani(t)} for t in tablolar or []],
        key=lambda t: (-t["onem"], str(t.get("name") or "")))


def gorunur_kolonlar(kolonlar: list[Any], gizli: set[str] | list[str] | None) -> list[Any]:
    """🔴 **GÖRÜNMEZ KOLON — MDL'ye hiç yazılmaz.**

    *"Gösterme" ile "yazma" arasındaki fark bu maddenin bütün değeridir:* gizlenen ama
    yazılan bir kolon, bir prompt sızıntısında ya da bir Discovery sorgusunda **geri
    gelir**. Burada kolon **üretilmez** — LLM onu **asla göremez**.

    ⚠ Karşılaştırma **ada göre ve büyük/küçük harf duyarsız**: kullanıcı `TCKN` yazıp
    kolon `tckn` olduğunda gizleme **sessizce çalışmazsa**, kullanıcı gizlediğini sanır.
    *Çalıştığı sanılan bir kapı, olmayan bir kapıdan tehlikelidir.*
    """
    g = {str(x).strip().lower() for x in (gizli or set())}
    if not g:
        return list(kolonlar or [])
    out = []
    for k in kolonlar or []:
        # 🔴 **Kapı bunu yakaladı.** İlk sürüm `else k` yazıyordu: kolon bir NESNE ise
        # (`IntrospectedColumn` — yazıcının gerçekte aldığı tip) `str(nesne)` bir ad
        # değil bir repr üretiyor, hiçbir zaman eşleşmiyor ve **gizleme sessizce
        # çalışmıyordu**. *Çalıştığı sanılan bir kapı, olmayan bir kapıdan tehlikelidir* —
        # ve bu satır tam olarak o cümlenin kendi koduna düşmüş hâliydi.
        ad = k.get("name") if isinstance(k, dict) else getattr(k, "name", k)
        if str(ad or "").strip().lower() in g:
            continue
        out.append(k)
    return out
