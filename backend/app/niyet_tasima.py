"""🔴 **NİYET PARÇALARI NETLEŞTİRMEDEN SAĞ ÇIKMALI.**

## Sınıf — ve neden ayrı bir modül

Bu depoda **iki kez** aynı kusur ölçüldü:

| tur | soru | netleştirmeden sonra |
|---|---|---|
| `§34.2` | `ciromun en büyük **3** kaynağı…` → *"hangi dönem?"* → `bu yıl` | **sırasız** 8 satır |
| `§40` | `fire oranı **yüzde 5 üzerindeki**…` → *"hangi dönem?"* → `bu yıl` | tek sayı: **19.79** |

İkisinde de ayrıştırıcı **kusursuz** çalışıyordu; kaybolan şey netleştirme turuydu:
uyum kapısı **o turun** sorusuna bakar ve o tur *"bu yıl"*dır — içinde ne üstünlük vardır
ne eşik. Kullanıcının niyeti bir önceki cümlede kalır ve `cq` onu taşımaz.

🔴 **`§34` bu sınıfı bir örneğinde kapatmıştı ve sınıf kapanmadı.**

> *Bir sınıfı bir örneğinde kapatmak, sınıfı kapatmaz — yalnız bir sonraki örneğini
> daha şaşırtıcı yapar.*

## ⚠ KAYITLI BORÇ — bu modül ile `app/siralama.py` AYNI SINIFTIR

`siralama.tamamla` ile buradaki `esik` aynı şeyi yapar: *"soruda tanınan ama `cq`'ya
girememiş bir niyet parçasını yerleştir"*. Bugün ikisi ayrı duruyor çünkü `siralama`
`§34`'te tek başına doğdu ve o gün sınıf henüz görünmemişti.

**Kural:** **üçüncü** parça geldiğinde ikisi tek bir `parcalar` kaydında birleşir
(`(ad, tanı, yerleştir)` üçlüsü) ve çağıran tek bir döngü koşar. Üç kopyaya izin yoktur.

*Bir borcu görünür bırakmak onu ödemek değildir; ama gizlemek onu ikiye katlamaktır.*
"""

from __future__ import annotations


def _cr():
    from app import cube_router
    return cube_router


def esik(cq: dict, q: str) -> bool:
    """🔴 **`§40` — TANINAN EŞİK, NETLEŞTİRME TURUNDAN SAĞ ÇIKMALI.** Döner: değişti mi.

    ## Ölçülen sessiz yanlış

    `fire oranı yüzde 5 üzerindeki partileri listele` → *"hangi dönem için?"* → kullanıcı
    *"bu yıl"* dedi → cevap **tek bir sayı: 19.79**. Ne eşik uygulandı, ne liste geldi,
    **ne de bir şey beyan edildi**. Kullanıcı 19.79'u cevap sanabilir.

    ⊙ Ayrıştırıcı **kusursuz** çalışıyordu: `_measure_threshold("… yuzde 5 uzerindeki …")`
    → `{'op': '>', 'value': 5.0}`. Ve `Niyet` de onu **sayıyordu**. Kaybolduğu yer
    netleştirme turuydu: uyum kapısı **o turun** sorusuna bakar ve o tur *"bu yıl"*dır —
    içinde hiçbir eşik yoktur.

    🔴 Bu, `§34.2`'nin (üstünlük niyeti netleştirmede düşüyordu) **birebir aynı sınıfı**.
    O zaman `order` için çözülmüştü; sınıf o gün kapanmadı çünkü çözüm **tek parçaya**
    uygulandı. *Bir sınıfı bir örneğinde kapatmak, sınıfı kapatmaz.*

    ## Sınır

    ⚠ Zaten bir `measure_having` varsa dokunulmaz; ölçü yoksa hiçbir şey yapılmaz —
    eşik neyin eşiği olduğu bilinmeden uygulanamaz.
    """
    if not isinstance(cq, dict) or cq.get("measure_having"):
        return False
    olculer = [m for m in (cq.get("measures") or []) if m]
    if not olculer:
        return False
    esik = _cr()._measure_threshold(_cr()._norm(q or ""))
    if not esik:
        return False
    cq["measure_having"] = {"measure": olculer[0], **esik}
    return True
