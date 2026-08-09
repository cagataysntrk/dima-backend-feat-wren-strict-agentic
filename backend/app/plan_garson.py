"""PLAN GARSONU — planlayıcı ile Intent LLM **aynı kişidir** (FAZ O-4).

## Kullanıcının sorusu, ve cevabı

> *"Planlayıcı ile LLM intent — yani garson — aynı kişi olabilir; çünkü LLM'e iki istek
> yerine tek cevapta bunu halledebiliriz."*

Doğru, ve raporun `E6` riskinin (**gecikme çarpılır**) yarısını **tasarımla** siliyor.
Ayrı bir planlayıcı turu, her soruya bir LLM çağrısı daha eklerdi; oysa garson zaten
soruyu okuyor. Ondan istenen şey değişmiyor — **çıktısının biçimi** genişliyor.

## 🔴 Neden bir SARMALAYICI, neden `_select_consistent` değiştirilmedi

`_select_consistent` bir **oylama** yordamıdır: `k` örnek alır, kanonikleştirir, sayar.
Ne oyladığını bilmesi gerekmez. Bu dosya ona bugünküyle **aynı sözleşmeyi** (`select_cube`
→ `CubeQuery` JSON metni) sunar; altında ne olduğunu bilmez, bilmemelidir.

⊙ Kazanç ölçülebilir: oylamanın kendisi, dönem çözümü, varlık perdesi, uyuşmazlık chip'i,
bütçe — **hiçbiri** bu fazda dokunulmadı. *Bir katmanı değiştirmenin en ucuz yolu, onun
konuştuğu dili konuşmaktır.*

## Denklik — ve neden bu bir davranış değişikliği DEĞİL

Tek `SORGU` adımlı bir plan, `plan_semasi.tek_adimli()` ile **bugünkü `CubeQuery`'ye**
indirgenir ve aynı `parse_cube_query`'den geçer. Yani basit sorularda:

* çağrı sayısı **aynı** (plan `select_cube`'un *yerine* geçer, yanına değil)
* çıktı **aynı** (aynı beyaz liste, aynı ayrıştırıcı)
* oylama **aynı** (kanonik `CubeQuery` üzerinde)

Çok adımlı bir plan bugünkü yolda **bir oy düşüşüdür** — yani merdiven bugünkü gibi
devam eder. Plan kaybolmaz, `planlar` listesinde saklanır: orkestratör merdivenin
**yerine değil boşluğuna** girer (`E3`).

⚠ `KURAL B`: bayrak kapalıyken `sarmala()` sarmalamaz, **nesnenin kendisini** döndürür —
tek satırlık bir kimlik fonksiyonu. Kapalı davranış bayt bayt bugünküdür.
"""

from __future__ import annotations

import json
import logging
from typing import Any

_log = logging.getLogger("dima.plan_garson")

#: Bayrak adı. ⚠ Tek yerde yazılı: `sarmala()` dışında kimse bu dizeyi okumaz.
BAYRAK = "orkestrator_plan"


class PlanGarsonu:
    """Bugünkü `select_cube` sözleşmesini konuşan, ama **altında plan üreten** sarmalayıcı.

    ⚠ Sarmalayıcı **saydamdır**: tanımadığı her çağrı içerideki sağlayıcıya gider
    (`__getattr__`). Bir sarmalayıcının en sinsi kusuru, sarmaladığı nesnenin
    yüzeyini **daraltmasıdır** — çağıran o zaman var olan bir yeteneği kaybeder.
    """

    def __init__(self, ic: Any, index: dict, *, azami_adim: int = 5) -> None:
        self._ic = ic
        self._index = index or {}
        self._azami = azami_adim
        #: Üretilen **çok adımlı** planlar. Tek adımlılar buraya yazılmaz — onlar zaten
        #: `CubeQuery` olarak çağırana döndü, ikinci bir kopya `KAT-1` olurdu.
        self.planlar: list[dict] = []

    def __getattr__(self, ad: str) -> Any:      # pragma: no cover - saydamlık
        return getattr(self._ic, ad)

    def select_cube(self, question: str, catalog: str, sema: dict | None = None) -> str:
        """Bugünkü imza, bugünkü dönüş — **altında** plan.

        🔴 Fail-open ve bu bilinçli: plan yolunun **her** arızasında bugünkü
        `select_cube`'a inilir. Bir genişlemenin, genişlettiği şeyi bozması kabul
        edilemez. *Yeni bir yol, eskisinin üstüne kurulur; yerine değil.*
        """
        try:
            _sema = None
            if getattr(self._ic, "sema_kullanir", False):
                from app.plan_semasi import plan_json_schema
                _sema = plan_json_schema(self._index, azami_adim=self._azami)
            ham = self._ic.plan_kur(question, catalog, _sema)
            plan = _plani_oku(ham)
            if plan is None:
                _log.info("plan: AYRIŞTIRILAMADI → bugünkü yola inildi — ham=%.200s", ham)
                return self._ic.select_cube(question, catalog, sema)
            from app.plan_semasi import tek_adimli
            cq = tek_adimli(plan)
            if cq is not None:
                _log.info("plan: TEK ADIM → bugünkü CubeQuery ile denk")
                return json.dumps(cq, ensure_ascii=False)
            self.planlar.append(plan)
            _log.info("plan: %d ADIM (%s) — merdiven bugünkü gibi sürüyor, plan saklandı",
                      len(plan.get("adimlar") or []),
                      "·".join(a.get("fiil", "?") for a in (plan.get("adimlar") or [])))
            # ⚠ Çok adımlı planda **boş** bir CubeQuery dönmek, oyu düşürmektir — ve bu
            # doğrudur: bu soru zaten tek bir cube sorgusuyla cevaplanamıyor. Uydurma bir
            # tek-cube cevabı üretmek, `E3`'ün (doğruluk vetosu) tam olarak yasakladığı şey.
            return "{}"
        except Exception:
            _log.warning("plan yolu düştü → bugünkü select_cube", exc_info=True)
            return self._ic.select_cube(question, catalog, sema)

    def cok_adimli_plan(self) -> dict | None:
        """Toplanan planlardan **en kısasını** döndürür — ya da hiç yoksa `None`.

        ⚠ En kısa, en çok oy alan değil: `k` örnek üç **farklı** plan üretebilir ve bir
        planı kanonikleştirip oylamak ayrı bir iştir (`E9`'un ölçüsü hazır değil). En
        kısa olan, `E9`'un tarafını tutar: *plan uzunluğu bir maliyettir.*
        """
        if not self.planlar:
            return None
        return min(self.planlar, key=lambda p: len(p.get("adimlar") or []))


def _plani_oku(ham: str) -> dict | None:
    """Ham metni plana çevirir — **kardeşi `parse_cube_query` ile aynı hoşgörüyle**.

    ⚠ Kod bloğu (```) soyma burada YOK ve olmamalı: sağlayıcı katmanı (`llm._FENCE`)
    yanıtı çağırana vermeden **zaten** soyuyor. İkinci bir soyucu yazmak, birincisi
    değiştiğinde sessizce ayrışacak bir kopya olurdu (`KAT-1`).

    🔴 Fiil beyaz listesi **burada** uygulanır, çalıştırıcıdan önce: bilinmeyen bir fiil
    taşıyan plan hiç doğmaz. *Bir planı koşarken reddetmek, hiç kurmamaktan pahalıdır —
    ilk adım o ana kadar çoktan koşmuştur.*
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
    from app.plan_semasi import FIILLER
    for a in adimlar:
        if not isinstance(a, dict) or a.get("fiil") not in FIILLER:
            return None
    return {"adimlar": adimlar}


def sarmala(llm: Any, index: dict, settings: Any, principal: Any = None) -> Any:
    """🔴 `KURAL B`'nin tek satırı: bayrak kapalıysa **nesnenin kendisi** döner.

    ⊙ Bayrak çözümü çağıranda değil burada: `ask.py`'nin `ask()` gövdesi bir tavan
    kapısına bağlı (`test_ASK_FONKSIYONU_TAVANI_ASMIYOR`) ve bir bayrak çözümü oraya
    yazılsaydı hem tavandan yer yerdi hem de bayrak adı ikinci bir yerde tekrarlanırdı.
    """
    try:
        from app.features import resolve_for
        if BAYRAK not in resolve_for(settings, principal):
            return llm
        if not getattr(llm, "plan_kurabilir", False):
            _log.info("plan bayrağı açık ama sağlayıcı plan kuramıyor → bugünkü yol")
            return llm
        return PlanGarsonu(llm, index)
    except Exception:
        _log.warning("plan garsonu kurulamadı → bugünkü yol", exc_info=True)
        return llm
