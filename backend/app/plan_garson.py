"""PLAN GARSONU — garson, **yalnız boşlukta** plan çevirir (FAZ O-4).

## Kullanıcının sorusu, ve ölçümün verdiği cevap

> *"Planlayıcı ile LLM intent — yani garson — aynı kişi olabilir; çünkü LLM'e iki istek
> yerine tek cevapta bunu halledebiliriz."*

Kişi aynı, **an** aynı değil. İlk tasarım bu fikri *"plan `select_cube`'un YERİNE geçer"*
diye okudu (raporun `E6` düzeltmesi). `EE` turunun A/B'si o okumayı **çürüttü**:

| ölçü | A · bayrak kapalı | B · bayrak açık |
|---|---|---|
| 🗣 `cube+llm` (garson) | **%35** | %25 |
| 🥡 Discovery / adhoc | %10 | **%25** |
| 🔴 **arıza oranı** | **%55** | 🔴 **%65** *(+10 puan)* |

⊙ **Mekanizma:** `_select_consistent` `k` örneği **aynı** süreçten çeker ve oylar. Plan
araya girince örneklerin bir kısmı plandan, bir kısmı `select_cube` yedeğinden geliyordu
— yani oy artık **aynı dağılımdan** çekilmiyordu. Bir oylamanın geçerliliği örneklerin
özdeşliğine dayanır; iki farklı süreci aynı sandığa atmak, oylamayı gürültüye çevirir.

🔴 Somut kayıp (`EE6` *«geçen hafta hiç iş kazası oldu mu»*): A'da `isg`/`{kaza_adedi: 0}`,
B'de cevapsız. Ve `EE14` *«ciromuz büyüdü mü»* B'de **İK'ya** düştü.

## ⟳ DÜZELTME — `E3`'ün LAFZINA dönüldü

Plan artık `select_cube` ile **yarışmıyor**. Yalnız **boşlukta** çağrılıyor: route boş,
garsonun tek-cube cevabı da yok — yani bugünkü sonuç Discovery ya da dürüst ret.

* cevaplanan hiçbir soruya **bir çağrı bile** eklenmez → `E6` riski **sıfır**
* cevaplanan hiçbir soru **bozulamaz** → `E3` yapısal olarak sağlanır
* oylama **hiç görmez** → self-consistency bugünküyle birebir

*Bir yeteneği doğru yere koymak, onu doğru yazmaktan önce gelir; yanlış yerde duran
doğru bir kod, yanlış bir koddur.*

⚠ `KURAL B`: bayrak kapalıyken `acik_mi()` `False` döner ve bu modülün hiçbir satırı
koşmaz. Kapalı davranış bayt bayt bugünkü.

## ⚠ Raporun `E6` düzeltmesi neden ölçümle geri alındı — kayıt için

Rapor *"planlayıcı garsonun kendisi, ayrı çağrı değil; riskin yarısı tasarımla iner"*
diyordu. Fikir doğru ama **yeri** yanlıştı: kazanç (çağrı sayısı) küçük, bedel (oylamanın
bozulması) büyüktü. Boşlukta çağırmak ikisini birden veriyor — çünkü boşlukta zaten bir
oylama yok.
"""

from __future__ import annotations

import json
import logging
from typing import Any

_log = logging.getLogger("dima.plan_garson")

#: Bayrak adı. ⚠ Tek yerde yazılı: `sarmala()` dışında kimse bu dizeyi okumaz.
BAYRAK = "orkestrator_plan"


def plan_uret(llm: Any, question: str, catalog: str, index: dict,
              *, azami_adim: int = 5) -> dict | None:
    """Garsona **plan** sorar. `None` = kullanılabilir bir plan çıkmadı.

    🔴 Bu fonksiyon **yalnız boşlukta** çağrılır — route boş, garsonun tek-cube cevabı
    da yok. Yani cevaplanan hiçbir soruya bir çağrı eklemez ve cevaplanan hiçbir soruyu
    **bozamaz**. `E3`'ün lafzı buydu ve ölçüm onu haklı çıkardı (yukarıdaki A/B).
    """
    try:
        _sema = None
        if getattr(llm, "sema_kullanir", False):
            from app.plan_semasi import plan_json_schema
            _sema = plan_json_schema(index, azami_adim=azami_adim)
        plan = _plani_oku(llm.plan_kur(question, catalog, _sema))
        if plan is None:
            _log.info("plan: kullanılabilir bir plan çıkmadı → boşluk kapanmadı")
            return None
        _log.info("plan: %d adım (%s)", len(plan["adimlar"]),
                  "·".join(a.get("fiil", "?") for a in plan["adimlar"]))
        return plan
    except Exception:
        _log.warning("plan üretimi düştü → bugünkü yol", exc_info=True)
        return None


def _plani_oku(ham: str) -> dict | None:
    """Ham metni plana çevirir — **kardeşi `parse_cube_query` ile aynı hoşgörüyle**.

    ⚠ Kod bloğu (```) soyma burada YOK ve olmamalı: sağlayıcı katmanı (`llm._FENCE`)
    yanıtı çağırana vermeden **zaten** soyuyor. İkinci bir soyucu yazmak, birincisi
    değiştiğinde sessizce ayrışacak bir kopya olurdu (`KAT-1`).

    🔴 Beyaz liste **burada** uygulanır, çalıştırıcıdan önce — ve **iki katmanlı**:
    fiil adı kapalı kümede mi, **ve** o fiilin zorunlu alanları yerinde mi
    (`plan_semasi.ZORUNLU_ALANLAR`). Uydurma bir alan taşıyan adım da düşer; şemanın
    `additionalProperties: False`ının serbest-JSON'daki karşılığı budur.

    *Bir planı koşarken reddetmek, hiç kurmamaktan pahalıdır — ilk adım o ana kadar
    çoktan koşmuştur.*
    """
    try:
        veri = json.loads(ham or "null")
    except Exception:
        return None
    if not isinstance(veri, dict):
        return None
    adimlar = veri.get("adimlar")
    if not isinstance(adimlar, list) or not adimlar:
        return None
    from app.plan_semasi import FIILLER, ZORUNLU_ALANLAR
    for a in adimlar:
        if not isinstance(a, dict) or a.get("fiil") not in FIILLER:
            return None
        _zorunlu = ZORUNLU_ALANLAR[a["fiil"]]
        # 🔴 **ADI DOĞRU, SÖZLEŞMESİ YANLIŞ.** Ölçüldü (`EE`, canlı): serbest-JSON
        # sağlayıcı fiili doğru yazıp parametrelerini **uyduruyor** —
        # `{"fiil":"SORGU"}` (`cube_query` YOK) · `{"fiil":"AYRISTIR","ozellik":…}`.
        # Yalnız fiil adına bakan doğrulama bunları plan sanıyor, çalıştırıcı
        # `KeyError` ile düşüyordu. *Bir sözleşmenin adını doğrulamak, sözleşmeyi
        # doğrulamak değildir.*
        if any(k not in a for k in _zorunlu):
            return None
        if set(a) - {"fiil", *_zorunlu}:
            return None    # uydurma alan → şemanın `additionalProperties: False`ı
    return {"adimlar": adimlar}


def acik_mi(settings: Any, principal: Any = None, llm: Any = None) -> bool:
    """🔴 `KURAL B`'nin tek satırı: bayrak kapalıysa **hiçbir şey olmaz**.

    ⊙ Bayrak çözümü çağıranda değil burada: `ask()`in gövdesi bir tavan kapısına bağlı
    ve bir bayrak adı ikinci bir yerde tekrarlanmasın diye (`KAT-1`).
    """
    try:
        from app.features import resolve_for
        if BAYRAK not in resolve_for(settings, principal):
            return False
        if llm is not None and not getattr(llm, "plan_kurabilir", False):
            _log.info("plan bayrağı açık ama sağlayıcı plan kuramıyor → bugünkü yol")
            return False
        return True
    except Exception:
        _log.warning("plan bayrağı çözülemedi → kapalı sayıldı", exc_info=True)
        return False
