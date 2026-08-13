r"""🔴 `FAZ 8` — **HASAT: kullanımdan sözlük**. Ve asıl iş `8.2`'dedir.

Kullanıcı yazarken-ara şeridinden bir aday seçtiğinde, ortaya bir **çeviri kanıtı**
çıkar: *«bu ham ifadeyle bu alanı kastetmiş»*. Bu kanıt, sözlüğü **kullanımdan**
büyütebilir — ama yalnız **doğru okunursa**.

## 🔴🔴 `8.2` — KONUM YANLILIĞI: naif sayım KENDİNİ BESLER

Bir öneri listesinde tıklar **konuma** bağlıdır: birinci sıra en çok tıklanır, çünkü
**birincidir** — daha iyi olduğu için değil. Naif bir sayım bunu *«en iyi aday»* diye
okur, o adayı sözlüğe yazar, aday bir dahaki sefere **yine birinci** çıkar, ve döngü
kendi kuyruğunu yer. *Bir ölçüt kendi ürettiği veriyle beslenirse, ölçtüğü şey artık
dünya değil kendisidir.*

Bu yüzden sinyal **ikiye ayrılır** ve yalnız biri sözlüğe girer:

| olay | sinyal | neden |
|---|---|---|
| **1. sırayı ATLAYAN** tık (`konum ≥ 1`) | 🟢 **GÜÇLÜ** | kullanıcı sıralamaya **rağmen** seçti — konumla açıklanamaz |
| **1. sıraya** tık (`konum == 0`) | ⚪ **ZAYIF** | sıralamayla da açıklanabilir; sözlüğe **girmez** |
| yazdı, **hiçbirini** tıklamadı | 🔴 **NEGATİF** (`8.4`) | gösterilenler **yanlıştı**; üsttekilere karşı kanıt |

⚠ Zayıf sinyal **atılmaz, sayılır**: bir gün konum düzeltmesi (*«position-based
model»*) kalibre edilirse veri orada durur. Ama **bugün** sözlüğe yalnız güçlü sinyal
girer 🅖.

## ⊘ `8.3` (`ε` karıştırma) UYGULANMADI — ve nedeni ölçülebilir ㊸

Plan, konum yanlılığını kırmak için sıralamaya küçük bir rastgelelik önerir. Bu
**doğru** bir fikirdir ama bugün **ölçülemez**: `ε`'nin faydası ancak *«karıştırılmış
turlarda güçlü sinyal oranı ne kadar arttı»* diye ölçülür, ve o ölçüm **tıklama
verisi** ister — yani `8.1`'in **toplamış olmasını**. Ölçmeden konan bir `ε`
kullanıcının listesini bozar ve karşılığında **hiçbir sayı** üretmez 🆕.

⊙ Ön koşul yazılı: yeterli tıklama biriktiğinde `ε` yeniden değerlendirilir. Kapı:
`tests/test_hasat_konum_yanliligi.py`.

## `KAT-1` sınırı

Bu modül **kuyruk yazmaz**: adayı üretir, yazan `sinonim_onerici.kuyruga_koy`'dur ve
orada `approved=False` **sabittir** — onaysız hiçbir şey `compose`'a girmez. İkinci
bir kuyruk hattı **kurulmadı**.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["Tiklama", "SINYAL_GUCLU", "SINYAL_ZAYIF", "SINYAL_NEGATIF",
           "sinyal", "hasat_adaylari", "negatif_kanit", "not_yaz", "not_oku",
           "govdeden"]

SINYAL_GUCLU = "guclu"
SINYAL_ZAYIF = "zayif"
SINYAL_NEGATIF = "negatif"


@dataclass(frozen=True)
class Tiklama:
    """Bir öneri turu. `konum` **0-tabanlı**; `-1` *«hiçbirini seçmedi»* demektir.

    ⚠ `gosterilen` listesi **şarttır**: negatif sinyal *«hangi adaylara karşı»*
    olduğunu ancak onunla söyleyebilir — payda olmadan bir negatif sinyal, kime
    yazılacağı bilinmeyen bir borçtur ㉗.
    """

    ham_ifade: str
    gosterilen: tuple[str, ...]      # aday kimlikleri, ekrandaki SIRAYLA
    konum: int = -1                  # seçilenin sırası; -1 = seçim yok


def sinyal(t: Tiklama) -> str:
    """`8.2` + `8.4` — bir turun sinyal sınıfı. **Saf**; depo/istek bilmez."""
    if not t.gosterilen:
        return SINYAL_ZAYIF          # gösterilen yoksa öğrenilecek bir şey de yok
    if t.konum < 0:
        return SINYAL_NEGATIF        # `8.4` — gösterilenler yanlıştı
    if t.konum == 0:
        return SINYAL_ZAYIF          # 🔴 konumla açıklanabilir → sözlüğe GİRMEZ
    return SINYAL_GUCLU              # 🟢 sıralamaya RAĞMEN seçildi


def hasat_adaylari(kayitlar: list[Tiklama]) -> list[tuple[str, str]]:
    """Sözlüğe **aday** `(ham_ifade, alan_kimligi)` çiftleri — yalnız **güçlü** sinyal.

    ⚠ Negatif sinyaller burada aday **üretmez** ve üretmemeli: *«bu liste yanlıştı»*
    bilgisi bir **çeviri kanıtı** değildir; sıralamayı iyileştirmeye yarar, sözlüğe
    yazılacak bir eşleşme vermez 🆋.

    ⚠ Tekilleştirme **çifte** yapılır: aynı `(ifade, alan)` iki kez tıklandıysa iki
    aday değil bir adaydır — yoksa kuyruk aynı satırı çoğaltır ㉛.
    """
    out: list[tuple[str, str]] = []
    gorulen: set[tuple[str, str]] = set()
    for t in kayitlar:
        if sinyal(t) is not SINYAL_GUCLU:
            continue
        ifade = (t.ham_ifade or "").strip()
        if not ifade or not (0 <= t.konum < len(t.gosterilen)):
            continue
        çift = (ifade, t.gosterilen[t.konum])
        if çift in gorulen:
            continue
        gorulen.add(çift)
        out.append(çift)
    return out


def negatif_kanit(kayitlar: list[Tiklama]) -> dict[str, int]:
    """`8.4` — *«gösterildi ama seçilmedi»* sayacı, **aday kimliği başına**.

    Sözlüğe girmez; sıralama bir gün kalibre edilirse **oradaki** girdidir. Bugün
    yalnız **sayılır** ve sayıldığı görünür 🅖 — *ölçülmeyen bir bileşen
    iyileştirilemez* 🆕.
    """
    sayac: dict[str, int] = {}
    for t in kayitlar:
        if sinyal(t) is not SINYAL_NEGATIF:
            continue
        for k in t.gosterilen:
            sayac[k] = sayac.get(k, 0) + 1
    return sayac


# ── KAYIT BİÇİMİ — **TEK SAHİP** ㊲ ─────────────────────────────────────────
#
# ⚠ Bu iki fonksiyon olmasaydı biçimi **yazan** (HTTP ucu) ve **okuyan** (`lab/`
# koşucusu) ayrı ayrı bilecekti. İki yer bir biçimi bilirse, bir gün biri değişir ve
# öteki **sessizce yanlış** okur — hasat tarafında bu, sözlüğe **yanlış eşleşme**
# yazmak demektir. Biçimin sahibi burasıdır; iki taraf da **çağırır**.
#
# ⊘ `InteractionLog`'a yeni **kolon** eklenmedi 🆝: mevcut `question` + `note` alanları
# taşıyor. Bir kolon eklemek bir göç demekti ve olayın ikinci bir sahibini doğururdu.

_AYRAC = "|"
_ALT_AYRAC = ","


def not_yaz(t: Tiklama) -> str:
    """`InteractionLog.note` gövdesi: `sinif|konum|aday1,aday2,…`."""
    return _AYRAC.join((sinyal(t), str(t.konum), _ALT_AYRAC.join(t.gosterilen)))


def not_oku(question: str | None, note: str | None) -> Tiklama | None:
    """`(question, note)` → `Tiklama`; okunamıyorsa **None** (kayıt sessizce düşer 🅡).

    ⚠ Sinıf alanı **yeniden hesaplanır**, nottan okunmaz: not bir **kayıt**tır, bir
    **karar** değil. Kural değişirse eski kayıtlar **yeni kuralla** okunur — yoksa
    dünkü bir eşik bugünkü sözlüğü belirlerdi ㉓.
    """
    if not note:
        return None
    parcalar = note.split(_AYRAC)
    if len(parcalar) != 3:
        return None
    try:
        konum = int(parcalar[1])
    except ValueError:
        return None
    gosterilen = tuple(x for x in parcalar[2].split(_ALT_AYRAC) if x)
    return Tiklama(ham_ifade=(question or "").strip(), gosterilen=gosterilen,
                   konum=konum)


def govdeden(govde: object) -> Tiklama:
    """HTTP gövdesi → `Tiklama`. **Asla fırlatmaz** 🅡 — bozuk girdi bir **hâl**dir.

    ⊙ Ölçülmüş kusur (denetim ajanı, 2026-08-13): uç `int(govde.get("konum", -1))`'i
    `try` bloğunun **dışında** çağırıyordu. Üçü de ölçüldü:

    * `{"konum": "abc"}` → `ValueError` → işlenmemiş **500**
    * `{"konum": null}`  → `TypeError` → işlenmemiş **500**
    * `{"gosterilen": "abc"}` → dize **karakterlere** açılıyor → `('a','b','c')` üç
      **sahte aday**; hasat kuyruğuna çöp kimlik yolu

    Yani uç kendi docstring'inin *«kayıt başarısız olsa da `{"kaydedildi": false}`
    döner»* vaadini **bozuk gövdede tutmuyordu** 🆅. `§101.1`: öneri katmanı cevabı
    bozmaz — ve **kendi ucunu da** bozmamalı.

    ⚠ Ayrıştırma **burada**, uçta değil (`KAT-1`): not biçiminin sahibi bu modül;
    gövde biçiminin de öyle. İki yerde ayrıştırmak ㊲ *aynı işin iki satırı* olurdu.
    """
    d = govde if isinstance(govde, dict) else {}
    ham = str(d.get("ham_ifade") or "")[:200]

    # ⚠ Dize bir **liste değildir**: `"abc"` üzerinde döngü kurmak onu karakterlere
    # açar. Yalnız gerçek diziler kabul edilir 🅡.
    g = d.get("gosterilen")
    gosterilen = (tuple(str(x)[:80] for x in g[:7])
                  if isinstance(g, (list, tuple)) else ())

    try:
        konum = int(d.get("konum", -1))
    except (TypeError, ValueError):
        konum = -1          # okunamayan konum = *«seçim yok»*; en az iddialı hâl
    return Tiklama(ham_ifade=ham, gosterilen=gosterilen, konum=konum)
