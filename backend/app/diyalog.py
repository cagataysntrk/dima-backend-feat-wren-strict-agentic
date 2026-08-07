"""🔴 `G2` — **DİYALOG BELLEĞİ**: sistem sorduğunu HATIRLAR.

## Ölçülen kusur

JPMorgan (arXiv 2605.26394, Mayıs 2026): çok-turlu text-to-SQL'de **tur-3 durumsuz
koşulduğunda beş modelin beşi de %0** yürütme doğruluğu verdi; **iki turluk** bir
çalışma penceresiyle **%87,6–100**. Durum taşımak bir iyileştirme değil, **var olma
koşuludur**.

DİMA'da bugün netleştirme **durumsuz**: chip tam bir soru metni taşır
(`belirsizlik_chipi.py:106`), sunucu **hiçbir açık slot saklamaz**, tur **sıfırdan**
koşar. Çok adımlı daraltma (*"hangi küp? → hangi ölçü? → hangi dönem?"*) yapısal olarak
imkânsız: her adım öncekini unutuyor.

## ⚠ Planın «taşınıyor» varsayımı ÇÜRÜDÜ

Yol haritası bu maddeyi *"sıfırdan yazmıyoruz — `0.5b`'nin `netlestirme.birlestir` saf
fonksiyonu çekirdek"* diye tarif ediyordu. **O fonksiyon YOK**
(`grep bekleyen_netlestirme` → 0 isabet; `netlestirme.py` yalnız `duzey`/`sorar_mi`/
`govde_notu`/`kanit_sinifi` tanımlıyor). Bu modül **sıfırdan** yazıldı.

## 🔴 TEK TEMSİL — `Niyet`'in boş alanı

*Açık slot* ikinci bir veri yapısı **değildir**: `Niyet`'in **boş alanıdır**.
`app/niyet.py` zaten `olcu_adaylari` · `donemler` · `kirilimlar` · `granulerlik`
taşıyor; ikinci bir slot dataclass'ı yazmak `KAT-1` ihlali olurdu — ve tam olarak bu
deponun adını koyduğu kusur (*"aynı kuralın iki sahibi"*).

## Taşıma: oturum deposu YOK, YANKI var

Sunucu durumu **saklamaz**; `cube_query`'nin bugün taşındığı gibi taşır: cevapta döner,
istemci bir sonraki istekte **geri yollar**. `context.py`'nin felsefesi burada da geçerli
— *"bağlam çözümü bir anlama işi değil bir MUHASEBE işidir"*.

🔴 Bunun bedeli dürüstçe yazılı: istemci yankılamazsa bellek **yoktur**. Sessiz bir
sunucu-yanı oturum deposu, `thread`/UI gruplamasının semantik sınır taşımasına yol
açardı — bu depoda daha önce ölçülmüş bir kusur sınıfı.
"""

from __future__ import annotations

from typing import Any

from app.logging_setup import get_logger

_log = get_logger("diyalog")

#: Bir turun **cevaplanabilmesi için** dolu olması gereken yuvalar.
#: ⚠ Liste kısa ve **kapalı**: her yuva, bugün zaten bir netleştirme dalı tarafından
#: sorulan bir şeydir. Yeni yuva eklemek yeni bir soru sormak demektir ve o, ürün kararı.
SLOT_OLCU = "olcu"
SLOT_DONEM = "donem"
SLOT_CUBE = "cube"

TUM_SLOTLAR = (SLOT_CUBE, SLOT_OLCU, SLOT_DONEM)

_DONEM_ADLARI = ("tarih", "donem", "dönem", "ay", "yil", "yıl", "date", "period")


def acik_slotlar(cube_query: dict | None, *, donem_gerekli: bool = False) -> list[str]:
    """Hangi yuvalar **boş**? Sıra anlamlıdır: cube → ölçü → dönem.

    ⚠ `donem_gerekli` çağırandan gelir çünkü *"dönem şart mı"* kararı bu modülün değil,
    `_period_gate`'in bilgisidir (zaman boyutu var mı · `period_optional` mı). İki yerde
    ayrı ayrı hesaplamak, iki farklı cevap veren iki sahip doğururdu.
    """
    cq = cube_query if isinstance(cube_query, dict) else {}
    acik: list[str] = []
    if not cq.get("cube"):
        acik.append(SLOT_CUBE)
    if not cq.get("measures"):
        acik.append(SLOT_OLCU)
    if donem_gerekli and not _donem_var(cq):
        acik.append(SLOT_DONEM)
    return acik


def _donem_var(cq: dict) -> bool:
    for f in cq.get("filters") or []:
        if isinstance(f, dict) and any(p in str(f.get("dimension", "")).lower()
                                       for p in _DONEM_ADLARI):
            return True
    return bool(cq.get("timeDimensions"))


def durum(cube_query: dict | None, *, sorulan: str | None = None,
          onceki: dict | None = None, donem_gerekli: bool = False) -> dict | None:
    """Bir turun diyalog durumu — cevapta döner, istemci **yankılar**.

    `sorulan` — bu turda kullanıcıya sorulan yuva (netleştirme dalı bunu bildirir).
    `onceki` — istemcinin yankıladığı bir önceki durum.

    Döner: `{acik_slotlar, sorulan, dolu, tur_no}` — ya da `None` (taşınacak bir şey yok).
    """
    acik = acik_slotlar(cube_query, donem_gerekli=donem_gerekli)
    tur_no = int((onceki or {}).get("tur_no") or 0) + 1
    onceki_acik = list((onceki or {}).get("acik_slotlar") or [])
    dolu = [s for s in onceki_acik if s not in acik]

    if not (acik or sorulan or dolu):
        return None
    out: dict[str, Any] = {"acik_slotlar": acik, "tur_no": tur_no}
    if sorulan:
        out["sorulan"] = sorulan
    if dolu:
        out["dolu"] = dolu
    return out


def bekleyen_yanit_mi(onceki: dict | None) -> str | None:
    """Bir önceki tur bir yuva **sordu** ve cevabı bekliyor mu? → sorulan yuva adı.

    🔴 Bu, `devam` davranışının **tetikleyicisidir**: bekleyen bir soru varken gelen
    kısa bir ifade (*"geçen ay"*) **yeni bir soru değildir**, bir **cevaptır** —
    `KURAL_TAZE` orada ateşlenmemelidir.
    """
    if not isinstance(onceki, dict):
        return None
    sorulan = onceki.get("sorulan")
    return str(sorulan) if sorulan and sorulan in TUM_SLOTLAR else None


def onarim_hedefi(onceki: dict | None, yeni_cq: dict | None,
                  eski_cq: dict | None) -> str | None:
    """*"Yok ya mart demiştim"* — **hangi tek yuva** değişti?

    Döner: değişen yuva adı; birden çok yuva değiştiyse `None` (bu bir onarım değil,
    yeni bir sorudur).

    ⚠ Ölçüm burada **geriye doğru** yapılır çünkü onarımı *"anlamak"* bir dil işidir ve
    `followup.sinifla`'nın sahasıdır. Bu modül yalnız *"sonuç bir onarıma benziyor mu"*
    sorusunu yanıtlar — ikinci bir dil sınıflandırıcısı yazmaz (`ADR-0008`).
    """
    if not isinstance(yeni_cq, dict) or not isinstance(eski_cq, dict):
        return None
    degisen: list[str] = []
    if eski_cq.get("cube") != yeni_cq.get("cube"):
        degisen.append(SLOT_CUBE)
    if (eski_cq.get("measures") or []) != (yeni_cq.get("measures") or []):
        degisen.append(SLOT_OLCU)
    if _donem_imzasi(eski_cq) != _donem_imzasi(yeni_cq):
        degisen.append(SLOT_DONEM)
    return degisen[0] if len(degisen) == 1 else None


def _donem_imzasi(cq: dict) -> str:
    parca = [f"{f.get('dimension')}={f.get('value')}"
             for f in (cq.get("filters") or [])
             if isinstance(f, dict)
             and any(p in str(f.get("dimension", "")).lower() for p in _DONEM_ADLARI)]
    parca += [str(td.get("granularity")) for td in (cq.get("timeDimensions") or [])
              if isinstance(td, dict)]
    return "|".join(sorted(parca))
