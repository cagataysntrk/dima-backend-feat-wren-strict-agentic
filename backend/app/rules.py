"""FAZ 5.13b — **KURAL MOTORU: bilgi, SQL'e DEĞİL ANLATIYA girer.** [bayrak: `ui_knowledge_center`]

> **Karar kaydı: `ADR-0008` sınırı** — *"anlamadığını bil"*. Bir kural, anlamadığımız bir
> soruyu anlaşılır **yapmaz**; anladığımız bir cevabı **zenginleştirir**.

## 🔴 EN ÖNEMLİ CÜMLE: KURAL SQL'İ ASLA DEĞİŞTİRMEZ

Bir "bilgi merkezi" en kolay şöyle yanlış yapılır: kullanıcı *"fire %5'in üstü kötüdür"*
yazar, sistem bunu bir **filtreye** çevirir ve o günden sonra sorular sessizce farklı
sayılar döndürür. O an ürün, kullanıcının **hiç sormadığı** bir soruya cevap vermeye
başlar — ve kimse fark etmez.

Bu yüzden kural:

| girer | girmez |
|---|---|
| `narration` — anlatının **ek bağlamı** | ❌ `route()` — hangi cube/ölçü seçilecek |
| `prescribe` — reçetenin **gerekçesi** | ❌ `cube_query` — hangi filtre/kırılım |
| | ❌ SQL'in **kendisi** |

⚠ Ve bu bir **temenni değil, kapıdır**: `tests/test_rules.py` hem kaynak taramasıyla hem
davranışla ölçer.

## Kuralın şekli

    - id: fire-esigi
      kapsam: {cube: parti, olcu: fire_orani_yuzde}
      metin: "Fire oranında %5 üstü, vardiya şefine bildirilmesi gereken bir eşiktir."

`kapsam` **daraltıcıdır**: boş bir kapsam her cevaba yapışır ve bir bilgi merkezi,
her cevaba yapışan bir dipnot değildir.
"""

from __future__ import annotations

from typing import Any

#: Bir cevaba iliştirilecek azami kural. ⚠ Üçten fazlası anlatıyı **boğar**: kullanıcı
#: sayıya değil dipnotlara bakmaya başlar.
AZAMI_KURAL = 3

#: 🔴 Bir kuralın **taşıyamayacağı** alanlar. Bunlardan biri bir kural YAML'ında
#: görünürse, o kural SQL'i etkilemeye çalışıyordur ve **reddedilir** — sessizce
#: yok sayılmaz, çünkü sessizce yok sayılan bir kural yazan kişi onun çalıştığını sanır.
YASAK_ALANLAR = ("filters", "filter", "where", "sql", "cube_query", "measures",
                 "dimensions", "order", "limit", "timeDimensions")


class KuralIhlali(ValueError):
    """Kural SQL'i etkilemeye çalışıyor. **Fail-closed**: yükleme durur.

    *Sessizce yok sayılan bir kural, yazan kişiye çalıştığını düşündürür — ve o kişi
    bir gün ona güvenerek karar verir.*
    """


def dogrula(kural: dict[str, Any]) -> None:
    """Kuralın **sınır içinde** olduğunu doğrular. İhlalde `KuralIhlali`."""
    if not str(kural.get("id") or "").strip():
        raise KuralIhlali("kimliksiz kural — kaynağı gösterilemeyen bir bilgi, bilgi değil")
    if not str(kural.get("metin") or "").strip():
        raise KuralIhlali(f"`{kural.get('id')}`: metinsiz kural")
    for alan in YASAK_ALANLAR:
        if alan in kural or alan in (kural.get("kapsam") or {}):
            raise KuralIhlali(
                f"`{kural.get('id')}`: `{alan}` bir SORGU alanıdır ve bir kural SQL'i "
                f"ASLA değiştirmez. Kural anlatıya girer, sorguya değil (ADR-0008 sınırı).")


def yukle(ham: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    """Kural listesi → doğrulanmış liste. **Fail-closed**: bir ihlal tümünü durdurur.

    ⚠ *"Bozuk olanı atla, kalanı yükle"* daha nazik görünür ve **daha tehlikelidir**:
    yarım yüklenmiş bir bilgi kümesi, kullanıcının yazdığı kuralın çalıştığını sanmasına
    yol açar.
    """
    out: list[dict[str, Any]] = []
    for k in ham or []:
        dogrula(k)
        out.append({"id": str(k["id"]), "metin": str(k["metin"]),
                    "kapsam": dict(k.get("kapsam") or {})})
    return out


def eslesen(kurallar: list[dict[str, Any]], cube_query: dict | None) -> list[dict[str, Any]]:
    """Bu cevaba **hangi kurallar** iliştirilir.

    Eşleşme `kapsam` üstünden ve **daraltıcıdır**: `{cube: parti}` yalnız `parti`
    cevaplarına, `{cube: parti, olcu: fire}` yalnız o ölçüyü taşıyanlara.

    🔴 **Boş kapsam eşleşmez.** Bir bilgi merkezi, **her cevaba yapışan bir dipnot**
    değildir; kapsamsız bir kural yazan kişi onu bir duyuru sanmıştır ve duyurunun yeri
    burası değildir.
    """
    cq = cube_query or {}
    out = []
    for k in kurallar or []:
        kapsam = k.get("kapsam") or {}
        if not kapsam:
            continue
        if kapsam.get("cube") and kapsam["cube"] != cq.get("cube"):
            continue
        olcu = kapsam.get("olcu")
        if olcu and olcu not in (cq.get("measures") or []):
            continue
        boyut = kapsam.get("boyut")
        if boyut and boyut not in (cq.get("dimensions") or []):
            continue
        out.append(k)
    return out[:AZAMI_KURAL]


def ek_baglam(kurallar: list[dict[str, Any]], cube_query: dict | None) -> str | None:
    """Anlatıya girecek **ek bağlam metni** — ya da `None`.

    ⚠ Bu metin `narration_guard`'ın **önüne geçmez**: guard eşleşmeyen **sayı** taşıyan
    cümleyi düşürmeye devam eder. Kural metni bir **bağlamdır**, bir sayı kaynağı değil —
    ve içinde bir sayı varsa o sayı **kullanıcının kendi yazdığı** sayıdır, sistemin
    hesapladığı değil.
    """
    es = eslesen(kurallar, cube_query)
    if not es:
        return None
    return " ".join(k["metin"].strip().rstrip(".") + "." for k in es)
