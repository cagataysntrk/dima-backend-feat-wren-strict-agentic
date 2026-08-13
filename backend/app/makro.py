r"""🔴 `§7 ②` — **ADLANDIRILMIŞ MAKRO**: tek öneri, arkasında N deterministik adım.

Planın kademe tablosu üç satırdır ve **ortadaki** bu dosyadır:

| # | ne | nasıl sunulur | LLM |
|---|---|---|---|
| ① | tek adım | doğrudan öneri (bugünkü `CubeQuery`) | ⊘ |
| **②** | **adlandırılmış makro** | **tek öneri**, arkasında N deterministik adım | **⊘** |
| ③ | özgün besteleme | garson taslak çizer, kullanıcı onaylar | ✅ |

> *«Asıl cevap ②. Kök-neden zaten böyle: `ayrıştır → akran → sürükleyen → derinleş` —
> dört adım, **tek** kullanıcı eylemi. Kapsamlı işlerin çoğu sonsuz kombinasyon değil,
> **sayılı reçete**.»*

## 🔴 Neden bu dosya YENİ KOD DEĞİL — bir BAĞLAMADIR

Üç parça **zaten** vardı ve hiçbiri ötekine bağlı değildi:

* **kapalı fiil grameri** — `plan_semasi` (15 fiil · `ZORUNLU_ALANLAR` · `CIKTI_TIPI`)
* **LLM'siz koşucu** — `plan_tuketici.calistir(plan, …)`, imzasında LLM **yok**
* **deterministik gezinti** — `drill.expand_cube_query` / `available_dimensions`

Eksik olan tek şey, bir **adın** bir plana karşılık gelmesiydi. Bugün çok adımlı plan
yalnız **garsondan** geliyor (`ask.py:4131 → plan_garson.sarmala`) — yani `②` kademesi
üründe **hiç yoktu**, her bileşik iş `③`'e (LLM) düşüyordu. Bu dosya `②`'yi açar.

⚠ **`E-8`:** bu modül sıcak yolda **ikinci bir LLM turu açmaz** — hiç LLM çağırmaz.
⚠ **Saf:** IO yok, sorgu koşmaz, durum tutmaz. Aynı girdi → aynı plan (`㉝`'in panzehiri).

## ⚠ MAKRO ENFLASYONU — planın kendi uyarısı

> *«Her kombinasyon adlandırılırsa uzayı **saymış** olursun. Kural: bir makro adını
> olasılıkla değil **SIKLIKLA** kazanır — kullanım kaydından ölçülür.»*

Bu yüzden burada **üç** makro var, otuz değil. Yeni bir makro eklemenin ön koşulu bir
**ölçüm**dür (`InteractionLog`'daki sıklık), bir sezgi değil 🅗. Liste uzatmak 🆞 bir
çözüm değil bir borçtur.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

__all__ = ["Makro", "MAKROLAR", "makrolar_icin", "plan_uret"]


@dataclass(frozen=True)
class Makro:
    """Bir reçete. `cumle` kullanıcıya **görünen** ad, `kur` planı üretir.

    ⚠ `gereken_boyut`: reçete bir kırılım boyutu istiyorsa `True`. Boyut **çağırandan**
    gelir (katalogdan), çünkü bu modül şema okumaz — saf kalır. Boyut yoksa makro
    **önerilmez**: ⊘ bir reçeteyi eksik argümanla önermek, tıklandığında düşen bir
    öneri sunmaktır 🆘.
    """

    ad: str
    cumle: str                      # `{olcu}` yer tutucusu ile
    kur: Callable[..., dict] = field(repr=False)
    gereken_boyut: bool = False


# ── ÜÇ REÇETE ──────────────────────────────────────────────────────────────
#
# ⚠ Adım referansları **1-tabanlı `$N`** (`plan_semasi`'nin sözleşmesi) ve `KIR`'ın
# çıktısı **satır değil SORGU**'dur — bu ayrım kök-neden inişinin tüm mekanizmasıdır:
# bir adım sorgu üretir, sonraki adım onu **koşar**.


def _neden_bu_seviyede(cube_query: dict, *, boyut: str) -> dict:
    """*«… neden bu seviyede?»* — planın literal örneği: `ayrıştır → akran → derinleş`.

    ⊙ `KIYASLA` akran sapmasını verir (*«ortalamadan ne kadar uzak»*), `KIR`+`SORGU`
    ikilisi de sürükleyen kırılımı gösterir. `ANLAT` **yalnız son adım** olabilir.
    """
    return {"adimlar": [
        {"fiil": "SORGU", "cube_query": cube_query},
        {"fiil": "KIYASLA", "cube_query": cube_query},
        {"fiil": "KIR", "cube_query": cube_query, "boyut": boyut},
        {"fiil": "SORGU", "cube_query": "$3"},
        {"fiil": "ANLAT", "kaynaklar": ["$1", "$2", "$4"]},
    ]}


def _gecen_yila_gore(cube_query: dict) -> dict:
    """*«geçen yıla göre nasıl?»* — `TREND` dönem kaydırır, çıktısı **hâlâ satırdır**."""
    return {"adimlar": [
        {"fiil": "SORGU", "cube_query": cube_query},
        {"fiil": "TREND", "cube_query": cube_query},
        {"fiil": "ANLAT", "kaynaklar": ["$1", "$2"]},
    ]}


def _en_kotu_ucu(cube_query: dict, *, boyut: str) -> dict:
    """*«en kötü üçü hangileri?»* — kırılım + sıralama, **tek** kullanıcı eylemi.

    ⚠ Sıralama `cube_query`'ye **burada** yazılmaz: `SIRALA` kapalı gramerin fiilidir
    ve `olculer` alanını ister. İkinci bir sıralama kuralı yazmak ㊲ aynı işin iki
    satırı olurdu.
    """
    olculer = list(cube_query.get("measures") or [])
    return {"adimlar": [
        {"fiil": "KIR", "cube_query": cube_query, "boyut": boyut},
        {"fiil": "SORGU", "cube_query": "$1"},
        {"fiil": "SIRALA", "kaynak": "$2", "boyut": boyut, "olculer": olculer},
        {"fiil": "ANLAT", "kaynaklar": ["$3"]},
    ]}


MAKROLAR: tuple[Makro, ...] = (
    Makro("neden", "{olcu} neden bu seviyede?", _neden_bu_seviyede, gereken_boyut=True),
    Makro("gecen_yil", "{olcu} geçen yıla göre nasıl?", _gecen_yila_gore),
    Makro("en_kotu", "en kötü üç {boyut} hangileri?", _en_kotu_ucu, gereken_boyut=True),
)


def makrolar_icin(cube_query: dict | None, *, boyutlar: list[str] | None = None,
                  olcu_etiketi: str = "", boyut_etiketi: str = "") -> list[dict]:
    """Bir çapa için **önerilebilir** makrolar — cümlesi kurulmuş hâlde.

    ⚠ Çapa yoksa **boş** döner: makro bir çapanın üstünde çalışır; çapasız bir
    *«neden bu seviyede?»*'nin öznesi yoktur ve tıklandığında düşer 🆘.

    ⚠ Boyut gerektiren reçete, boyut yoksa **listelenmez** — eksik argümanlı bir öneri
    sunmak, kullanıcıya çalışmayan bir düğme göstermektir.
    """
    if not cube_query:
        return []
    bl = [b for b in (boyutlar or []) if b]
    out: list[dict] = []
    for m in MAKROLAR:
        if m.gereken_boyut and not bl:
            continue
        metin = m.cumle.format(olcu=olcu_etiketi or "bu ölçü",
                               boyut=boyut_etiketi or (bl[0] if bl else ""))
        out.append({"ad": m.ad, "metin": metin.strip(), "tur": "makro",
                    "adim_sayisi": len(plan_uret(m.ad, cube_query,
                                                 boyut=bl[0] if bl else "")["adimlar"])})
    return out


def plan_uret(ad: str, cube_query: dict, *, boyut: str = "") -> dict:
    """Makro adı → **plan**. `plan_tuketici.calistir` ile LLM'siz koşulur.

    🔴 Bilinmeyen ad bir **hata**dır, sessiz bir boş plan değil 🅤: sessiz boş plan,
    kullanıcının tıkladığı düğmenin hiçbir şey yapmamasıdır ve hiçbir yerde iz bırakmaz.
    """
    for m in MAKROLAR:
        if m.ad != ad:
            continue
        if m.gereken_boyut:
            if not boyut:
                raise ValueError(f"`{ad}` makrosu bir kırılım boyutu ister — verilmedi.")
            return m.kur(cube_query, boyut=boyut)
        return m.kur(cube_query)
    raise ValueError(f"bilinmeyen makro: {ad!r} (tanımlılar: "
                     f"{', '.join(x.ad for x in MAKROLAR)})")
