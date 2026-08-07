"""🔴 `Ö5` — **GUARD DÜŞME ORANI**: kapı sessizce her şeyi düşürmeye başlarsa GÖRÜLÜR.

## Kapının kendi sözü tutulmamıştı

`app/iddia.py`'nin docstring'i şunu yazıyor:

> *"Düşme oranı **ölçülür** — kapı agresifse gevşetilir, ama **ölçüyle**, sezgiyle değil."*

Söz yazıldı, ölçüm kurulmadı: `grep dusme_orani|drop_rate` → **0 isabet**. Tek tek log
satırları vardı, makbuzda **tek cevaplık** sayı vardı — ama **oran** yoktu.

## Ölçülen risk sınıfı — *sessiz soğuma*

`narration_guard` ve `iddia.py` **fail-closed**tır: düşen cümle yayımlanmaz ve sistem
`interpret.summary`'ye (süssüz ama doğru) düşer. Bu **doğru** davranıştır. Ama model
sürümü ya da prompt biçimi değişirse kapılar **tüm** anlatıyı düşürmeye başlayabilir:

* kullanıcı **yanlış sayı görmez** — güvenlik tarafı sağlam;
* sistem sürekli *"soğuk/süssüz"* cevap verir;
* ve **hiçbir alarm çalmaz**, çünkü hiçbir şey hata vermiyor.

🔴 *Bir kapının sessizce her şeyi düşürmesi, hiç olmamasından farksızdır — tek fark,
sistemin kendini güvende sanmasıdır.*

## Neden DB değil, süreç-içi kayan pencere

`InteractionLog`'a kolon eklemek bir migration ister ve bu ölçüm bir **iş kaydı** değil
bir **sağlık sinyalidir**: geçmişe dönük sorgulanması değil, **şimdi** görünmesi gerekir.
Kalıcı analiz gerektiğinde `interaction_log`'un kendi satırları zaten duruyor.

⚠ Ve pencere **süreç başına**dır: çok süreçli bir dağıtımda her süreç kendi oranını
görür. Bu bir eksik değil bir **sınırdır** ve burada yazılıdır — *ölçülen şeyin kapsamını
yazmayan bir metrik, yanlış okunmayı davet eder.*

## Eşik BİR TAHMİNDİR — ve öyle işaretlidir

Dış öneri **%30** dedi. Taban bilinmiyor, dolayısıyla bu bir **karar değil başlangıç
noktasıdır**: `durum()` her zaman **ham sayıları** da döndürür ki eşik ölçümle
düzeltilebilsin. *Bir eşiği ölçmeden koymak, onu ölçmenin önüne geçmektir.*
"""

from __future__ import annotations

import threading
from collections import deque

from app.logging_setup import get_logger

_log = get_logger("guard_alarmi")

#: Kayan pencere boyu — *"son N cevap"*.
PENCERE = 50

#: 🔴 Uyarı eşiği. **Ölçülmüş bir taban değil, bir başlangıç tahminidir** (dış öneri).
#: `durum()` ham sayıları da verir; eşik ölçüldükten sonra buradan düzeltilir.
ESIK = 0.30

#: Alarm **durum değişiminde** bir kez loglanır. Her istekte loglamak, alarmı gürültüye
#: çevirirdi — ve *okunmayan bir alarm, olmayan bir alarmdır.*
_kilit = threading.Lock()
_pencere: deque[tuple[int, int]] = deque(maxlen=PENCERE)
_alarmda = False


def kaydet(dusen: int, toplam: int) -> None:
    """Bir cevabın guard sonucunu pencereye yaz.

    `toplam` = guard'a giren cümle sayısı, `dusen` = düşen. `toplam == 0` olan cevaplar
    (anlatı hiç üretilmedi) **pencereye girmez**: anlatısız bir cevap, düşmüş bir anlatı
    değildir. *Paydaya girmeyen bir vaka, oranı bozmaz.*
    """
    if toplam <= 0:
        return
    global _alarmda
    with _kilit:
        _pencere.append((int(dusen), int(toplam)))
        d = sum(x for x, _ in _pencere)
        t = sum(y for _, y in _pencere)
        oran = (d / t) if t else 0.0
        dolu = len(_pencere) >= PENCERE
        # ⚠ Pencere DOLMADAN alarm verilmez: üç cevaplık bir örneklemde %33 bir sinyal
        # değil bir gürültüdür. *Az veriyle verilen bir alarm, alarmın kendisine olan
        # güveni harcar.*
        yeni = dolu and oran >= ESIK
        if yeni and not _alarmda:
            _log.warning(
                "🔴 GUARD DÜŞME ORANI YÜKSEK: son %d cevapta %d/%d cümle düştü (%%%.1f ≥ "
                "%%%.0f). Anlatı sessizce soğuyor olabilir — model/prompt değişti mi?",
                len(_pencere), d, t, oran * 100, ESIK * 100)
        elif _alarmda and not yeni:
            _log.info("guard düşme oranı normale döndü: %%%.1f", oran * 100)
        _alarmda = yeni


def durum() -> dict:
    """Sağlık yüzeyi için: **oran ve ham sayılar birlikte**.

    Ham sayılar bilinçli: eşik ölçülmemiş bir tahmin olduğu için, onu düzeltecek olan
    kişi **paydayı** görmeden karar veremez.
    """
    with _kilit:
        d = sum(x for x, _ in _pencere)
        t = sum(y for _, y in _pencere)
        return {
            "ornek": len(_pencere),
            "pencere": PENCERE,
            "dusen_cumle": d,
            "toplam_cumle": t,
            "oran": round(d / t, 4) if t else None,
            "esik": ESIK,
            "alarm": _alarmda,
            # ⚠ Kapsam yazılı: bu sayı **bu sürecin** penceresidir.
            "kapsam": "surec-ici",
        }


def sifirla() -> None:
    """Test yalıtımı — üretim yolunda çağrılmaz."""
    global _alarmda
    with _kilit:
        _pencere.clear()
        _alarmda = False
