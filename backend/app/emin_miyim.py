r"""🔴 `FAZ 1` — **«EMİN MİYİM?» SORUSUNUN TEK ŞEKLİ.**

Sistem dört ayrı yerde aynı soruyu soruyordu — *«elimdeki en iyi aday, üstünde işlem
yapacak kadar açık ara önde mi?»* — ve dördü de cevabı **kendi** aritmetiğiyle
kuruyordu. Soru bir taneydi, sahibi dörttü (`KAT-1` borcu).

## Ölçülen dört tanım *(13 Ağustos 2026, kod adıyla arandı ㉙)*

| # | yer | taban | marj | ek ön koşul | sonuç sayısı |
|---|---|---|---|---|---|
| ① | `value_index.auto_fix:137` | `AUTO_SCORE` **0,80** | `AUTO_MARGIN` **0,08** | `len(surface) ≥ MIN_AUTO_LEN` | 2 |
| ② | `cube_router` yazım hatası `:3874` | `_TYPO_HIGH` **0,82** | `_TYPO_GAP` **0,08** | `len ≥ 4` · `len_ratio ≥ 0,65` · çapraz-konu | **3** |
| ③ | `cube_router._match_cube:1190` | *(yok)* | **4 harf** | — | 2 |
| ④ | `cube_router:1109` | *(yok)* | **∞** *(tek aday)* | — | 2 |

② üç sonuçludur (**oto düzelt** / **öner** / **sus**) ve `Karar`'ın üç hâli birebir
odur; ①③④ aynı şeklin **dejenere** hâlleridir. Ortak iskelet şudur ve dördünde de
**aynıdır**:

    en iyi aday yoksa           → SINIR
    skor(en iyi) < taban        → SINIR ya da GÖSTER
    skor(2.) > skor(1.) − marj  → GÖSTER   *(yakın ikinci ⇒ belirsiz)*
    aksi hâlde                  → OTO_ICRA

## 🔴 Planın `1.5`'i **UYGULANMADI** — ve nedeni burada

Plan *«③'ün harf farkını 0–1'e normalize edip `karar()`'a ver»* diyordu. Ölçüldü ve
**reddedildi**: `_longest_syn_hit` bir **harf sayısıdır** (üst sınırı yok; katalogdaki
en uzun ad bugün **30** harf). Onu `[0,1]`'e sıkıştırmak **sabit bir payda uydurmayı**
zorunlu kılar 🅭 — ve o payda bir gün aşıldığında (*biri 33 harflik bir eşanlamlı
ekler*) skor `1`'i geçer, *«normalize değil»* kapısı `ValueError` fırlatır ve **küp
seçimi çöker**. Yani `[0,1]` şartı, davranışı korumak için değil **bir imzayı süslemek
için** alınmış bir risk olurdu 🅒.

**Bunun yerine sözleşme birim-bağımsızdır:** `skor`ların yalnız **tek bir çağrı
içinde** kıyaslanabilir olması yeterlidir, ve `taban`/`marj` **çağıranın birimindedir**.
Böylece ③ harf sayısını **olduğu gibi** geçirir (`marj=4`), davranış **bayt bayt**
korunur ve uydurulmuş hiçbir sabit yoktur ㊱.

⚠ **Bunun bedeli yazılmıştır** 🅖: farklı çağıranların skorları **birbiriyle**
kıyaslanamaz. Bu modül bir *«güven yüzdesi»* **üretmez** — `MIMARI.md`'nin kararı
zaten budur: *kalibre edilmediği sürece o sayı bir güven değil bir süstür.* İleride
kaynaklar arası kıyas gerekirse, çözüm burada bir payda uydurmak değil, **kalibre
edilmiş** bir skor üretmektir.

## KAT-1 sınırı — bu modül neyin sahibi DEĞİL

Yalnız **eşik aritmetiğinin** sahibidir. Her çağıranın kendi **ön koşulları**
(`MIN_AUTO_LEN`, `len_ratio`, çapraz-konu elemesi) ve **kalibre sabitleri**
(`AUTO_SCORE`, `_TYPO_HIGH`, …) **yerinde kalır**: onlar o çağıranın alan bilgisidir,
ortak soru değil. ㊼ *Birleşik bir skor üretmek bir tercih beyan etmektir* — burada
hiçbir tercih beyan edilmiyor.
"""

from __future__ import annotations

import math
from enum import Enum

__all__ = ["Karar", "karar"]


class Karar(str, Enum):
    """*«Emin miyim?»* sorusunun üç cevabı — ikisi değil **üçü**.

    🆑 *Belirsizliği cevapsız bırakmak, onu beyan etmek değildir:* `SINIR` ile `GOSTER`
    ayrı hâllerdir. `SINIR` *«söyleyecek bir şeyim yok»*, `GOSTER` *«adayım var ama
    kararı sana bırakıyorum»* demektir.
    """

    OTO_ICRA = "oto_icra"   # açık ara önde → sistem kendisi uygular
    GOSTER = "goster"       # aday var ama yeterince açık değil → kullanıcıya sorulur
    SINIR = "sinir"         # gösterilecek aday bile yok


def karar(skorlar: list[float], *, marj: float, taban: float = -math.inf,
          taban_goster: float | None = None,
          taban_goster_genis: float | None = None,
          baglam_belirsiz: bool = False) -> Karar:
    """Dört çağıranın **ortak** karar iskeleti. Yeni bir yargı **üretmez**.

    `taban` — `OTO_ICRA` için asgari skor. **Varsayılanı `-inf`**, çünkü ③ ve ④'te
        mutlak bir eşik **yoktur** ve olmayan eşiği yazdırmak onu var sanmaktır 🆑;
        `marj` ise her çağıranda vardır, o yüzden **zorunlu**.
    `marj` — ikinci adaya asgari fark; `math.inf` *«ikinci aday hiç olmasın»* demektir
    `taban_goster` — `GOSTER` için asgari skor. `None` ise **öneri kademesi yoktur**
        ve karar ikiye iner (`OTO_ICRA` / `SINIR`) — ①③④'ün hâli.
    `taban_goster_genis` — `baglam_belirsiz=True` iken `taban_goster` yerine geçen,
        **daha yüksek** baraj. ②'nin *«cube çözülemediyse öneri barajı da yükselir»*
        kuralı buraya taşındı; kaybolmadı.

    ⚠ Marj kıyası **çağıranların ortak biçimidir**: `ikinci ≤ en_iyi − marj`. Üçü de
    (`>` ile reddet / `>=` ile kabul) bu eşitsizliğin aynı yazılışıydı — ve bu
    fonksiyon o **tek** yazılışı kullanır.
    """
    if not skorlar:
        return Karar.SINIR

    sirali = sorted(skorlar, reverse=True)
    en_iyi = sirali[0]
    # ⚠ İkinci aday YOKSA fark sonsuzdur — ④'ün *«tek aday»* kuralı budur, ve bu
    # yüzden ④ ayrı bir dal değil, `marj=inf` ile aynı gövdedir.
    fark = (en_iyi - sirali[1]) if len(sirali) > 1 else math.inf

    if en_iyi >= taban and fark >= marj:
        return Karar.OTO_ICRA

    esik_goster = (taban_goster_genis if (baglam_belirsiz and taban_goster_genis is not None)
                   else taban_goster)
    if esik_goster is not None and en_iyi >= esik_goster:
        return Karar.GOSTER
    return Karar.SINIR
