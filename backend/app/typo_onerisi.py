"""§G/AJ0 · örnek #1 — **bir öneri, ancak CEVAP AÇIYORSA öneridir.**

## Ölçülen kusur

Ölçüldü (12 gerçekçi soru, `lab/deneyim_olc.py`, 2026-08-04): **beşi** yazım-önerisi
dalında ölüyordu ve önerilerin hepsi saçmaydı — çünkü aday, düzeltmenin **işe yarayıp
yaramadığına bakılmadan** üretiliyordu:

| kullanıcı yazdı | sistem önerdi |
|---|---|
| `arttı` | *"«parti» mi demek istedin?"* |
| `veren` | *"«renk» mi demek istedin?"* |
| `işledik` | *"«iplik» mi demek istedin?"* |
| `sattık` | *"«hattı» mi demek istedin?"* |

🔴 **Kök neden:** bir kelimenin **katalogda olmaması**, onun yazım hatası olduğunun kanıtı
**değildir** — bir cümledeki kelimelerin çoğu zaten katalog dışıdır (fiiller, edatlar,
gündelik dil). Bulanık eşleştirici bunu bilmiyor, her bilinmeyen kelimeyi bir *"hata"*
sanıyordu. Ve dal `source=None` ile **dönüyordu**, yani cevap üretebilecek yolun önünü
**kesiyordu** — `KAT-2`'nin ihlali (*"cevapsız bir dal, cevaplı bir yolu KESEMEZ"*).

## Neden AYRI MODÜL

`0.21`'in modül büyüme kapısı bu düzeltmeyi `ask()` içindeyken **yakaladı**: `ask()` kod
satırı 1147 → 1157, tavan aşıldı. Kapının kendi talimatı: *"yeni davranışı **modüle
çıkar**, tavanı yükseltme."* Karar burada saf bir fonksiyon olarak durur — `ask()`'in
kapsamına eklenmiş yirminci bir closure'dan hem **test edilebilir** hem **okunabilir**.

## Ne YAPMIYOR — ve bu sınır ölçülmüş

Bu modül *"öneri doğru mu"* sorusunu **çözmez**, yalnız *"öneri bir yere çıkıyor mu"*
sorusunu sorar. Saçma bir düzeltme de bazen route eder (`"…parti iplik"` katalog
terimlerinden oluşur) — o kalan kusur `tests/test_typo_onerisi_kapisi.py`'de
`xfail(strict=True)` ile **görünür** bırakıldı.

⚠ **Ve bir gerekçe ÇÜRÜTÜLDÜ:** *"benzerlik bantları ayrık, eşiği yükselt"* önerisi
ölçümle reddedildi — saçma **0,600–0,769**, gerçek yazım hatası **0,714–0,923**:
**çakışıyorlar**. Eşiği yükseltmek `fıre→fire` (0,750) gibi **gerçek** hataları
kaybettirirdi. Gerçek ayırıcı sinyal benzerlik oranı değil **Türkçe fiil çekimi**
(saçmaların hepsi fiil→isim) ve o iş AJ0'ın morfoloji kalemine ait.
"""

from __future__ import annotations

from typing import Any

from app.logging_setup import get_logger

_log = get_logger("typo_onerisi")


def cevap_aciyor_mu(aday: dict[str, Any] | None, schema: dict,
                    *, liste_kirilimi: bool = False) -> bool:
    """Öneri uygulanınca soru **gerçekten cevaplanabilir** hâle geliyor mu?

    Doğrulama `cube_router.route()` ile yapılır: **sıfır-LLM ve deterministik**. Bir
    öneriyi doğrulamak için LLM çağırmak, gürültüyü **paralı** hâle getirirdi.

    🔴 **Fail-closed.** `route()` patlarsa `False` döner: doğrulanamayan bir öneri,
    doğrulanmamış bir öneridir. Kullanıcıyı cevapsız bir soruya **ikinci kez** çarptıran
    bir chip, chip olmamasından **kötüdür** — aynı disiplin `olcu_netlestirme`'de yazılı.
    """
    duzeltilmis = (aday or {}).get("corrected_q") or ""
    if not duzeltilmis:
        return False
    from app import cube_router

    try:
        return cube_router.route(cube_router._norm(duzeltilmis), schema,
                                 liste_kirilimi=liste_kirilimi) is not None
    except Exception:                                        # noqa: BLE001 — best-effort
        _log.warning("typo önerisi doğrulaması hata verdi", exc_info=True)
        return False


def gecerli_oneri(typo_fixes: list[dict[str, Any]], schema: dict,
                  *, liste_kirilimi: bool = False) -> dict[str, Any] | None:
    """Sunulmaya **değer** yazım önerisi — yoksa `None`.

    `ask()` tarafında tek satırlık bir çağrıya iner; karar burada, saf ve test edilebilir.
    """
    aday = next((f for f in typo_fixes or [] if f.get("kind") == "suggest"), None)
    if fiil_uydurmasi_mi(aday):
        return None
    if zaten_katalogda_mi(aday, schema):
        return None
    return aday if cevap_aciyor_mu(aday, schema, liste_kirilimi=liste_kirilimi) else None


def zaten_katalogda_mi(aday: dict[str, Any] | None, schema: dict) -> bool:
    """🔴 **`§61` — GEÇERLİ BİR TERİMİ «DÜZELTMEK» EN KÖTÜ ÖNERİDİR.**

    ## Ölçülen kusur

    | soru | öneri |
    |---|---|
    | `bu yıl **vardiyalara** göre fire oranı` | *"«vardiyalara gore» yerine «calisanlara gore» mi?"* |
    | `bu yıl **kaç farklı** müşteriye satış yaptık` | *"«kac farkli» yerine «kac yas» mi?"* |
    | `renk bazında ciro **dağılımı**` | *"«dagilimi» yerine «agirlik» mi?"* |

    🔴 Birincisi en ağırı: **`vardiya` katalogda var** ve onlarca soruda doğru çalışıyor.
    Sistem, kendi bildiği bir terimi *"acaba başka bir şey mi demek istedin"* diye
    sorguluyor — yani kullanıcıya **kendi kataloğunu** yanlış tanıtıyor.

    ## Kural

    > Bir sözcük katalogda **karşılığı olan** bir terimi kapsıyorsa, o sözcük bir yazım
    > hatası **değildir**. Öneri düşer.

    ⚠ Ölçüt `_covers`'tır — yani `vardiyalara` → `vardiya` çekimini de yakalar. İkinci bir
    eşleştirici yazılmaz (`KAT-1`): `cube_router` bu işin sahibidir.

    *Bir sözlüğün kendi kelimesini yanlış sayması, sözlüğe duyulan güveni bitirir.*
    """
    span = str((aday or {}).get("from") or "").strip()
    if not span:
        return False
    try:
        from app.cube_router import _catalog_vocabulary, _covers, _norm
        sn = _norm(span)
        _kat = _catalog_vocabulary(schema)
        return any(_covers(t, w) for t in _kat
                   for w in sn.split() if len(w) > 2)
    except Exception:                                  # noqa: BLE001 — öneri kararı düşmez
        return False


def fiil_uydurmasi_mi(aday: dict[str, Any] | None) -> bool:
    """🔴 **AYIRICI SİNYAL — bu modülün kendi belgesinin istediği şey.**

    Bu dosyanın açılış notu şunu yazıyordu ve bir çözüm değil bir **teşhis**ti:

    > *"Gerçek ayırıcı sinyal benzerlik oranı değil **Türkçe fiil çekimi** (saçmaların
    > hepsi fiil→isim) ve o iş AJ0'ın morfoloji kalemine ait."*

    Morfoloji kalemi indi (`app/turetme.py`, KÖK-7d) ve ayırıcı artık **var**:

    | kullanıcı yazdı | önerilen | karar |
    |---|---|---|
    | `arttı` *(fiil)* | `parti` | 🔴 **bastırılır** |
    | `veren` *(fiil)* | `renk` | 🔴 **bastırılır** |
    | `işledik` *(fiil)* | `iplik` | 🔴 **bastırılır** |
    | `sattık` *(fiil)* | `hattı` | 🔴 **bastırılır** |
    | `muterileri` *(isim)* | `müşteri` | 🟢 **kalır** |

    🔴 Bir fiilin katalogda olmaması bir yazım hatası **değildir** — bir cümledeki
    kelimelerin çoğu zaten katalog dışıdır. Bulanık eşleştirici bunu bilemez; **dilbilgisi
    bilir**.

    ⚠ Neden **eşik değil**: ölçüldü ve çürütüldü — saçma **0,600–0,769**, gerçek yazım
    hatası **0,714–0,923**, **çakışıyorlar**. Eşiği yükseltmek `fıre→fire` (0,750) gibi
    gerçek hataları kaybettirirdi. *Bir sınıfı ayıran şey bir sayı değilse, hiçbir eşik
    onu ayırmaz.*

    ⚠ Ve karar **fail-open değil**: şüphede öneri **bastırılır**. Bastırılan bir öneri
    kullanıcıya bir chip eksik gösterir; yanlış bir öneri onu **yanlış yere** bakmaya
    davet eder. *İkisi aynı ağırlıkta değildir.*
    """
    from app.turetme import fiil_bicimi_mi

    kaynak = str((aday or {}).get("from") or "")
    if not kaynak:
        return False
    if fiil_bicimi_mi(kaynak):
        _log.info("yazım önerisi BASTIRILDI (fiil biçimi): %r → %r",
                  kaynak, (aday or {}).get("to"))
        return True
    return False
