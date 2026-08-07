"""🔴 `G1` — **TEMELLENDİRME**: sistem *ne anladığını* SÖYLER. 0 LLM · 0 token.

## Ölçülen kusur

Üretimdeki başarısızlığın **%69'u** (`WRONG_FILTER` %54,6 + `WRONG_SCOPE` %14,4)
*"SQL çalıştı, makul bir sayı döndü, ama **başka bir sorunun** cevabıydı"* sınıfıdır.
Power BI'ın kendi belgeleri bunu örnekliyor: kullanıcı 2024 sorar, sistem yanlış tarih
tablosuna filtreleyip *"2024 verisi yok"* der.

Bir garson bunu **ilk saniyede** görünür kılar: *siparişi tekrarlar.*

## Kural ZATEN YAZILI — uygulaması dardı

`app/soz.py:19` birebir: **«Kural: ÖNCE NE ANLADIĞINI SÖYLE, SONRA SOR.»** ve
`KATALOG["netlestirme.donem"]` bir **`{ne}` yuvası** taşıyor — *"çağıranın anladığı
şey"*. 🔴 Ama ilke yalnız **netleştirmede** kullanılıyor; **başarılı bir turda sistem
ne anladığını hiç söylemiyor**.

Aynı yarımlık `uyum.py`'de de var: kapı yedi değişmezi denetleyip ihlal bulduğunda
`kismi_cevap_notu()` ile **söylüyor** (`beyanli_kismi: 58`) — yani sistem
**yanıldığını** söylüyor, **anladığını** söylemiyor.

    bugün        ihlal varsa  → "kıyas istendi ama…"      ✅
                 her turda    → (sessizlik)                🔴
    G1'den sonra her turda    → "anladığım şu: …"          ✅

## Ne YAPMAZ — sınır dürüstçe yazılı

Temellendirme hatayı **görünür** kılar, **engellemez**. Etiketi okumayan kullanıcı
yanlış sayıyı yine taşır. Bu bir **garanti değil**, bir **görünürlük** kazanımıdır.
*(Danışman belgesi bunu bir garanti gibi sunuyordu — §9/Y-2.)*

## Neden 0 token — ve bu bir tasarım özelliği

Kaynağı **yalnız `CubeQuery`**: anlatı değil **muhasebe**. Bunun sonucu bozulma
merdiveninde görünür: LLM tamamen düşse bile (kota · ağ · 429) sistem *"ne anladığını"*
söylemeye **devam eder**. *Garson hastalanırsa mutfak yine de siparişi tekrar eder.*
"""

from __future__ import annotations

from typing import Any

from app.logging_setup import get_logger

_log = get_logger("temellendirme")

#: Dönem filtresi taşıyan boyut adları — `_period_gate` ile **aynı** kavram.
_DONEM_ADLARI = ("tarih", "donem", "dönem", "ay", "yil", "yıl", "date", "period")


def _ad(teknik: str, katalog: dict[str, str] | None) -> str:
    """Görünen ad — yoksa teknik ad. 🔴 Ham kolon adı basmak yasaktır (`G1.8`)."""
    if not teknik:
        return ""
    if katalog:
        for anahtar in (teknik, teknik.split(".")[-1]):
            if anahtar in katalog:
                return katalog[anahtar]
    return teknik.split(".")[-1].replace("_", " ")


def kur(cube_query: dict | None, *, katalog: dict[str, str] | None = None,
        cube_etiketi: str | None = None) -> dict[str, Any] | None:
    """`CubeQuery` → *"ne anladım"* muhasebesi. LLM YOK, sayı YOK.

    Döner: `{cube, olcu, donem, kirilim[], filtreler[]}` — ya da `None` (basılacak bir
    şey yoksa).

    ⚠ **Boş sözlük dönmez.** *"Anladığım şu: (boş)"* bir beyan değil, bir gürültüdür;
    en az bir ölçü ya da dönem adlandırılabiliyorsa basılır.
    """
    if not isinstance(cube_query, dict):
        return None

    olculer = [_ad(str(m), katalog) for m in (cube_query.get("measures") or [])]
    boyutlar = [str(d) for d in (cube_query.get("dimensions") or [])]

    donem: str | None = None
    filtreler: list[str] = []
    for f in cube_query.get("filters") or []:
        if not isinstance(f, dict):
            continue
        boyut = str(f.get("dimension") or "")
        deger = f.get("value")
        if deger is None or deger == "":
            continue
        metin = f"{_ad(boyut, katalog)}: {deger}"
        if any(p in boyut.lower() for p in _DONEM_ADLARI):
            donem = donem or str(deger)
        else:
            filtreler.append(metin)

    # `timeDimensions` granülerliği de bir DÖNEM beyanıdır — kullanıcı "aylık" dediyse
    # onu duyduğumuzu söylemeliyiz.
    granul = None
    for td in cube_query.get("timeDimensions") or []:
        if isinstance(td, dict) and td.get("granularity"):
            granul = str(td["granularity"])
            break

    kirilimlar = [_ad(b, katalog) for b in boyutlar
                  if not any(p in b.lower() for p in _DONEM_ADLARI)]

    if not (olculer or donem or granul or kirilimlar):
        return None

    out: dict[str, Any] = {}
    if cube_etiketi:
        out["cube"] = cube_etiketi
    if olculer:
        out["olcu"] = ", ".join(dict.fromkeys(olculer))
    if donem:
        out["donem"] = donem
    if granul:
        out["granulerlik"] = granul
    if kirilimlar:
        out["kirilim"] = list(dict.fromkeys(kirilimlar))
    if filtreler:
        out["filtreler"] = filtreler
    _log.debug("temellendirme: %s", ", ".join(out))
    return out
