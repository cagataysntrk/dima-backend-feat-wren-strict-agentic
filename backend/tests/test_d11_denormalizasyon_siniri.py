r"""🔴 `§14.14 D11` — **DENORMALİZASYON YÜZEYİ: hipotez doğrulandı, ARTIK SAYISI VAR.**

## Kartın açık soruları ve ölçülen cevapları (⟳ 2026-08-12, kendi koşumum)

> *«Kaç küpümüz 3+ model üstünde?»* · *«`dimension_origin[*].certified` kaçında
> `olculmedi`?»*

    küp sayısı        : 23
    tablo dağılımı    : {1 tablo: 16, 2 tablo: 6, 3 tablo: 1}
    3+ tabloya çıkan  : yalnız `kalite` (tamir_rework + makineler + partiler)
    ilişki-türevi köken: 9
    hops              : 9/9 → **1**            (hiçbiri 1'i geçmiyor)
    certified         : 9/9 → `olculdu:saglikli`  (sertifikasız köken YOK)

Kartın hipotezi — *«JOIN'i cube derleyicisi kurar (planlayıcı değil), risk yapısal
olarak düşük»* — **doğrulandı**: literatürdeki `%20`'lik dış hata oranı **çok atlamalı**
zincirlerde ölçülmüştür; bizim maruziyetimiz **tek atlama**.

⚠ **DENETİM AJANININ SAYISI DÜZELTİLDİ.** Ajan *«3+ tablo **7/23 (%30)**, `kalite`
**4 tablo**, dağılım `{1:16, 3:6, 4:1}`»* demişti. Küp **kimlikleri** doğru, **sayılar
tam bir tablo kaymış** — taban `base_object`'tir (`kalite` → `tamir_rework`) ve
ilişkinin kendisi (`tamir_rework_makineler`) bir **tablo değil bir kenardır**. Ajanın
*«7»*'si aslında **2+ tabloya** çıkan küp sayısıdır. *Bir ajan iddiasını ölçmeden almak,
raporun içine yanlış bir sayıyı kalıcı yazmaktır* (bu turda **ikinci** kez).

> *«Risk yapısal olarak düşük» ölçüsü yazılmadan bir güvencedir, bir ölçüm değil.*

## Bu kapı ne zaman kırmızı olmalı

Kartın alıntıladığı risk tam üç yerde başlar; kapı **bugün yeşil doğar** ve o üç yerin
birine varıldığı gün kırmızıya döner.
"""

from __future__ import annotations

#: 🔴 Bugün **3**; tavan **5**'te. Aradaki iki basamak bilinçli bir **pay**dır: kartın
#: kararı *«bugünkü maruziyet düşük»* üstüne kurulu, *«asla büyümesin»* üstüne değil.
#: Tavana varıldığı gün karar **yeniden okunmalı**, sessizce aşılmamalı.
AZAMI_TABLO = 5

#: `hops > 1` = **çok atlamalı** zincir. Literatürdeki hata oranı orada ölçülmüştür;
#: `§14.14 D11`'in ⊘ gerekçesi tam olarak *«bizde tek atlama var»*dır.
AZAMI_HOP = 1

#: Sertifikasız bir köken, fan-out'u **ölçülmemiş** bir JOIN demektir — sayılar sessizce
#: şişebilir. Bugün böyle bir köken **yok**; doğduğu gün görünmeli.
SERTIFIKA_ONEKI = "olculdu:"


def _kubeler(schema) -> list[dict]:
    return list((schema or {}).get("cubes") or [])


def _tablolar(c: dict) -> set[str]:
    """Bir küpün yayıldığı **tablo** kümesi.

    ⚠ Taban `base_object`'tir — küpün **adı değil** (`kalite` → `tamir_rework`).
    ⚠ `relationship` bir **kenardır**, bir tablo değil; onu saymak her küpü bir fazla
    gösterir (denetim ajanının düştüğü yer).
    """
    t = {c.get("base_object") or c.get("name")}
    for ad, o in (c.get("dimension_origin") or {}).items():
        t.add((o or {}).get("model") or ad)
    return {x for x in t if x}


def test_OLCUM_TABANI_KATALOG_DOLU(schema):
    """⊘ **Boş yeşil avı.** Katalog boşalırsa aşağıdaki üç yüklem de *«kusur yok»* diye
    okunur."""
    k = _kubeler(schema)
    assert len(k) >= 20, f"⊘ ölçüm tabanı çöktü: {len(k)} küp (beklenen ≥20)"
    kokenli = [c for c in k if c.get("dimension_origin")]
    assert kokenli, (
        "⊘ ölçüm tabanı çöktü: hiçbir küpte `dimension_origin` yok — bu kapı ilişki "
        "türevi boyutları ölçer, ölçecek bir şey kalmamış.")


def test_HICBIR_KUP_TABLO_TAVANINI_ASMIYOR(schema):
    """🔴 **Denormalizasyon genişliği.** Bugün en geniş küp **3** tabloda (`kalite`)."""
    asan = {c.get("name"): sorted(_tablolar(c)) for c in _kubeler(schema)
            if len(_tablolar(c)) > AZAMI_TABLO}
    assert not asan, (
        f"🔴 küp(ler) {AZAMI_TABLO}+ tabloya yayıldı: {asan}. `§14.14 D11`'in ⊘ kararı "
        "*«maruziyetimiz tek atlama ve dar»* ölçümüne dayanıyordu — o ölçüm artık "
        "geçerli değil, kart yeniden okunmalı.")


def test_HICBIR_KOKEN_COK_ATLAMALI_DEGIL(schema):
    """🔴🔴 **ASIL YÜKLEM.** ⊘ kararının bütün dayanağı budur: literatürdeki `%20`'lik
    hata oranı **çok atlamalı** zincirlerde ölçülmüştür."""
    derin = [(c.get("name"), b, (o or {}).get("hops"))
             for c in _kubeler(schema)
             for b, o in (c.get("dimension_origin") or {}).items()
             if ((o or {}).get("hops") or 1) > AZAMI_HOP]
    assert not derin, (
        f"🔴 ÇOK ATLAMALI köken doğdu: {derin}. `§14.14 D11` *«hops hiçbir yerde 1'i "
        "geçmiyor»* ölçümüyle kapanmıştı.")


def test_SERTIFIKASIZ_KOKEN_YOK(schema):
    """🔴 Sertifikasız bir köken = fan-out'u **ölçülmemiş** bir JOIN. `§F16`'nın kapattığı
    kusurun kaynağı tam buydu: ölçülmemiş bir ilişki sayıları sessizce şişirir."""
    kotu = [(c.get("name"), b, (o or {}).get("certified"))
            for c in _kubeler(schema)
            for b, o in (c.get("dimension_origin") or {}).items()
            if not str((o or {}).get("certified") or "").startswith(SERTIFIKA_ONEKI)]
    assert not kotu, (
        f"🔴 SERTİFİKASIZ köken: {kotu} — fan-out ölçülmemiş; `dimension_origin` bir "
        "beyandır ve beyansız bir JOIN, ölçülmemiş bir risktir.")


def test_OLCULEN_SAYILAR_RAPORDAKIYLE_AYNI(schema):
    """⚠ `§14.14 D11`'e **yazılan** sayılar bunlar. Kod değişip sayı değiştiğinde bu
    yüklem kırmızı olur ve rapor **kod ile birlikte** güncellenir.

    ⊙ *Bir raporun sayısını kapıya bağlamazsan, o sayı bir sonraki turda bir ölçüm
    değil bir hatıra olur.*
    """
    k = _kubeler(schema)
    kokenler = [(o or {}) for c in k for o in (c.get("dimension_origin") or {}).values()]
    assert len(kokenler) >= 9, (
        f"🔴 ilişki-türevi köken sayısı {len(kokenler)} — rapora **9** yazıldı; küçüldüyse "
        "bir beyan kaybolmuş olabilir.")
    en_genis = max((len(_tablolar(c)) for c in k), default=0)
    assert en_genis <= 3, (
        f"🔴 en geniş küp artık {en_genis} tabloda — rapora **3** (`kalite`) yazıldı. "
        f"Tavan ({AZAMI_TABLO}) aşılmadı ama **ölçüm bayatladı**: kart güncellenmeli.")
