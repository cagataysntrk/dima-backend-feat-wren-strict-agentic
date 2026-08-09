"""PLAN GARSONU — planlayıcı ile Intent LLM **aynı kişidir** (FAZ O-4).

## Kullanıcının sorusu, ve cevabı

> *"Planlayıcı ile LLM intent — yani garson — aynı kişi olabilir; çünkü LLM'e iki istek
> yerine tek cevapta bunu halledebiliriz."*

Doğru, ve raporun `E6` riskinin (**gecikme çarpılır**) büyük kısmını **tasarımla** siliyor.
Ayrı bir planlayıcı turu, **her** soruya bir LLM çağrısı daha eklerdi; oysa garson zaten
soruyu okuyor. Ondan istenen şey değişmiyor — **çıktısının biçimi** genişliyor.

⚠ *"Hiç artmaz"* değil, **"tek adımlıda artmaz"**: bu ayrım ölçümle kondu, iyimserlikle
değil (aşağıda `E3` notu).

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

## 🔴🔴 `E3` ÖLÇÜMLE DÜZELTİLDİ — ilk tasarım CEVAP YOK EDİYORDU

İlk hâlde çok adımlı bir plan bugünkü yolda **bir oy düşüşüydü**: *"bu soru zaten tek cube
ile cevaplanamaz"* varsayımıyla boş bir `CubeQuery` dönülüyordu. `EE` turunun A/B'si bunu
çürüttü:

    EE6 «geçen hafta hiç iş kazası oldu mu»
      A (bayrak kapalı): `cube+llm` · `isg` · `{kaza_adedi: 0}`   ✅
      B (bayrak açık)  : plan üretildi, oy düştü → 🔴 CEVAPSIZ

⊙ Yani model bir soruyu *"çok adımlı"* sandığında, **bugün cevaplanabilen** bir soru
cevapsız kalıyordu. `E3`'ün şartı tam tersini söylüyordu ve tam tersi oluyordu:
orkestratör merdivenin **boşluğuna** değil **yerine** geçmişti.

Bugün: çok adımlı planda bugünkü yol **ayrıca** sorulur, plan `planlar`da saklanır ve
yalnız merdiven **gerçekten** boş kaldığında konuşur. Bedeli dürüstçe: o dalda bir çağrı
daha. *Bir maliyeti hiç ödememek için bir cevabı kaybetmek, ucuz değil pahalıdır.*

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
            _log.info("plan: %d ADIM (%s) — bugünkü yol AYRICA soruluyor (E3)",
                      len(plan.get("adimlar") or []),
                      "·".join(a.get("fiil", "?") for a in (plan.get("adimlar") or [])))
            # 🔴🔴 **`E3` BURADA ÖLÇÜMLE DÜZELTİLDİ — ve düzeltmeden önce plan CEVAP YOK
            # EDİYORDU.** İlk tasarım burada `"{}"` döndürüyordu: *"çok adımlı bir soru
            # zaten tek cube ile cevaplanamaz"*. `EE` turunun A/B'si bunu çürüttü:
            #
            #   EE6 «geçen hafta hiç iş kazası oldu mu»
            #     A (kapalı): `cube+llm` · `isg` · `{kaza_adedi: 0}`   ✅
            #     B (açık)  : plan üretildi, oy düştü → 🔴 CEVAPSIZ
            #
            # ⊙ Yani model bir soruyu *"çok adımlı"* sandığında, bugün cevaplanabilen bir
            # soru cevapsız kalıyordu. `E3`'ün şartı buydu ve tam tersi oluyordu:
            # orkestratör merdivenin **boşluğuna** değil **yerine** geçmişti.
            #
            # ⚠ Bedeli dürüstçe yazıyorum: bu dalda **bir çağrı daha** yapılır. Ama yalnız
            # burada — tek adımlı planda (soruların ezici çoğunluğu) sayı **değişmez**.
            # *Bir maliyeti hiç ödememek için bir cevabı kaybetmek, ucuz değil pahalıdır.*
            return self._ic.select_cube(question, catalog, sema)
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
