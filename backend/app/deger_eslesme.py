"""🔴🔴 `§DK-3` — **ROUTE İLE GARSON AYNI MENÜYE BAKAR: değer eşleşmesinin tek yeri.**

`§DK` kataloğun enum'unu düzeltti; bu modül o enum'u **kullanan** tarafı taşır. Ayrı
bir dosya oluşunun sebebi bir kapı: `cube_router.py` modül büyüme tavanını aştı ve
kapının kendi mesajı *«yeni davranışı modüle çıkar, tavanı yükseltme»* dedi.

⊙ Ayrım yapısal olarak da doğru: `cube_router` *«hangi küp, hangi ölçü»* sorusunu
cevaplar; bu dosya *«kullanıcının söylediği şey bir DEĞER mi, hangisi»* sorusunu.

⚠ `_value_token_hit` bilerek `cube_router`'da kaldı: onu **dört** tüketici çağırıyor
(kapsam kapısı · sinonim taraması · bu modül · takip düzenlemesi) ve taşımak dördünü
birden yeni bir bağımlılığa sokardı. *Bir şeyi taşımak, onu kullananların hepsini
taşımaya razı olmaktır.*
"""

from __future__ import annotations

import re

#: 🔴 Görünen etiketin **açıklama kuyruğu**: `«1. Vardiya (08-16)»` → `«1. vardiya»`.
#: Yalnız **sondaki parantez** atılır — bir şirket adındaki `LTD. ŞTİ.` atılmaz, çünkü
#: o bir açıklama değil adın parçasıdır. *Bir kuralı genişletmek, onu belirsizleştirmenin
#: en kolay yoludur.*
_ETIKET_KUYRUGU = re.compile(r"\s*\([^()]*\)\s*$")


def _deger_cekirdegi(nv: str) -> str | None:
    """Normalize edilmiş bir değerin **çekirdeği** — yoksa `None` (değişiklik yok)."""
    cekirdek = _ETIKET_KUYRUGU.sub("", nv).strip()
    return cekirdek if cekirdek and cekirdek != nv else None


def boyut_degerleri(cube_meta: dict | None, cols: dict, dname: str) -> list[str]:
    """🔴🔴 `§DK-3` — **ROUTE İLE GARSON AYNI MENÜYE BAKAR.**

    ## Ölçülen kusur (canlı, 2026-08-10)

    Route'un değer eşleşmesi değerleri `schema["models"][*]["columns"]`'dan, yani **ham
    model kolonlarından BOYUT ADIYLA** okuyordu — küpün kendi `dimension_values`'ını
    hiç kullanmadan. Sonuç, `§DK`'nın birebir ikizi ve **ikinci kopyası**:

    | boyut | route'un baktığı | küpün gerçeği (derleyicinin kullandığı) |
    |---|---|---|
    | `vardiya` | 🔴 **kolon hiç yok** → süzgeç yapısal olarak imkânsız | `1. Vardiya (08-16)` … |
    | `musteri` | `M1001…` (kullanıcının asla yazmadığı kodlar) | `AKDENİZ ÖRME TEKSTİL A.Ş.` … |
    | `tedarikci` | `T-101…` | `FIRAT İPLİK TİC. LTD.` … |

    ⊙ Bedeli ölçüldü: *«bu yıl **1. vardiyada** fire oranı»* → **üç vardiya birden**,
    ilk satır *«3. Vardiya»*, süzgeç sessizce düştü, beyan **yok**.

    ## Düzeltme

    Kaynak **küpün kendi enum'udur** — kataloğun garsona verdiği liste ve sorgunun
    döndüreceği değerlerle **aynı** liste. Ham kolon yalnız küpün kaydı **hiç yokken**
    yedektir (bugünkü davranış; kırpma değil).

    *İki basamağın farklı menülere bakması bir tutarsızlık değil, iki ayrı üründür.*
    """
    enum = (cube_meta or {}).get("dimension_values") or {}
    v = enum.get(dname)
    if v:
        return [str(x) for x in v]
    col = cols.get(dname) or {}
    return [str(x) for x in (col.get("values") or [])]


def deger_eslesmeleri(q: str, degerler: list[str]) -> list[str]:
    """Sorunun tuttuğu değerler — **tam** eşleşme, yoksa **tekil çekirdek** eşleşmesi.

    🔴 Çekirdek yolu yalnız **tek aday** kalırsa kullanılır: `«ram»` hem `RAM-1` hem
    `RAM 2`'yi çağırır ve orada seçim yapmak yazı-turadır. *Belirsizlikte tahmin etmemek,
    bu deponun tek kuralıdır ve çekirdek eşleşmesi onun istisnası olamaz.*
    """
    from app.cube_router import _norm, _value_token_hit

    tam = [v for v in degerler if (nv := _norm(v)) and _value_token_hit(q, nv)]
    if tam:
        return tam
    aday = [v for v in degerler
            if (ck := _deger_cekirdegi(_norm(v))) and _value_token_hit(q, ck)]
    return aday if len(aday) == 1 else []
