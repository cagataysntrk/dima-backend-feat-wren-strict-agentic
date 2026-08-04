"""FAZ 1.5 — **METRİK SERTİFİKASYONU.** Bir sayının arkasında *kim* duruyor?

## Neden

`source=cube` rozeti *"bu sayı deterministik bir yoldan geldi"* der — **doğru ama yetersiz**.
Cevaplamadığı soru: *"bu metriğin tanımını **kim onayladı**, ve o onaydan beri **tanım
değişti mi**?"* Bir metrik doğru hesaplanıp yanlış **tanımlanmış** olabilir; determinizm
onu yakalamaz.

## 🔴 B8 — SERTİFİKA ÇÜRÜR, ve çürümesi ÖLÇÜLEBİLİR olmalı

Bir sertifika iki şeyden birine dokunulduğunda **geçersizleşir**:

1. **Tanım** değişti (`definition_hash`) — ölçünün ifadesi/birimi/toplanabilirliği
2. **Üst-akış kolon kümesi** değişti (`lineage_set_hash`) — `1.6`'nın kolon kökeni

İkincisi **`1.6`'nın ön koşuludur** ve sırayı bu yüzden düzelttik: bugünkü sırayla `1.5`
önce inseydi `lineage_set_hash` ya **uydurulur** ya **hep `None`** olurdu — ikisi de
*"beyan var, karşılığı yok"*.

⚠ **Üçüncü çürüme yolu — TTL (90 gün).** Zaman tek başına bir kusur değildir ama bir
sertifika *"o gün doğruydu"* der; süresiz bir onay, **sorulmamış** bir sorudur.

## 🔴 «yeniden_dogrulama_gerekli» ≠ «geçersiz»

Çürüyen bir sertifika **silinmez**: seviyesi korunur, üstüne bir **bayrak** düşer. Silmek,
*"hiç sertifikalanmamış"* ile *"sertifikalanmış ama tanım değişmiş"*i karıştırırdı — ve
ikincisi kullanıcı için **daha bilgilendiricidir** (biri bu metriğe bakmış, sonra dünya
değişmiş). `otomatik_iptal_nedeni` hangi kapının düştüğünü **adıyla** söyler.

## Neden hash, neden karşılaştırma değil

Tanımın kendisini saklamak, aynı gerçeğin **ikinci bir kopyasını** üretirdi (bu deponun 1
numaralı kusuru). Hash bir **parmak izidir**: değişip değişmediğini söyler, neyin
değiştiğini değil — ve sertifikanın sorduğu soru tam olarak *"değişti mi"*dir.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any

#: Sertifika kademeleri — **artan** güvence. Sıra anlamlıdır (rozet kademesi ondan türer).
SEVIYELER = ("onerilen", "sertifikali", "master_veri")

#: TTL. *"O gün doğruydu"* diyen bir onay, süresiz olamaz.
GECERLILIK_GUN = 90

#: Çürüme nedenleri — **adıyla** yazılır, `True/False` değil: *"neden düştü"* sorusunun
#: cevabı kullanıcıya gösterilecek şeydir.
NEDEN_TANIM = "tanim_degisti"
NEDEN_KOKEN = "ustakis_kolon_kumesi_degisti"
NEDEN_SURE = "gecerlilik_doldu"


def _hash(veri: Any) -> str:
    """Kanonik JSON → SHA-256 (ilk 16 hane).

    Kanonikleştirme **zorunlu**: `sort_keys` olmadan aynı tanım farklı sıralamayla farklı
    hash üretir ve sertifika **kendiliğinden** çürürdü — bir kapı, gürültüyle ateşlerse
    kapatılır, kapatılan bir kapı yoktur.
    """
    ham = json.dumps(veri, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(ham.encode("utf-8")).hexdigest()[:16]


def tanim_hash(olcu: dict[str, Any] | None) -> str:
    """Ölçü tanımının parmak izi.

    ⚠ **Yalnız ANLAMI değiştiren alanlar** girer: ifade · birim · toplanabilirlik ·
    `lowerIsBetter`. `synonyms` **girmez** — bir eşanlamlı eklemek metriğin *tanımını*
    değiştirmez, yalnız **bulunabilirliğini** artırır. Sinonimi hash'e katmak, sertifikayı
    katalog bakımının her turunda düşürürdü.
    """
    o = olcu or {}
    return _hash({
        "expression": o.get("expression"),
        "unit": o.get("unit"),
        "additive": o.get("additive"),
        "lowerIsBetter": o.get("lowerIsBetter"),
    })


def koken_hash(koken: dict[str, Any] | str | None) -> str:
    """Üst-akış **kolon kümesinin** parmak izi — `1.6`'nın çıktısından.

    Yalnız **küme** girer (hangi kaynak.kolon), dönüşüm tipi ya da filtre **değil**: bir
    filtrenin değeri sorudan soruya değişir ve sertifikayı her turda düşürürdü. Sertifikanın
    sorduğu soru *"aynı kolonlardan mı besleniyor"*dur.
    """
    if not isinstance(koken, dict):
        return _hash(str(koken or ""))
    kume = sorted({
        f"{x.get('kaynak')}.{x.get('ad')}"
        for grup in ("olculer", "boyutlar")
        for x in (koken.get(grup) or [])
    })
    return _hash(kume)


def gecerlilik_bitisi(baslangic: datetime) -> datetime:
    return baslangic + timedelta(days=GECERLILIK_GUN)


def durum(sertifika: dict[str, Any] | None, *, tanim: str | None = None,
          koken: str | None = None, simdi: datetime | None = None) -> dict[str, Any] | None:
    """Sertifikanın **bugünkü** durumu — `None` ise metrik hiç sertifikalanmamıştır.

    Döner: `{seviye, gecerli, yeniden_dogrulama_gerekli, otomatik_iptal_nedeni, ...}`

    🔴 **Çürüyen sertifika SİLİNMEZ**: seviyesi korunur, üstüne bayrak düşer. Silmek,
    *"hiç sertifikalanmamış"* ile *"sertifikalanmış ama tanım değişmiş"*i karıştırırdı —
    ve ikincisi kullanıcı için **daha bilgilendiricidir**.

    ⚠ Birden fazla neden varsa **hepsi** yazılır: bir kapının düşmesi ötekini gizlemez.
    """
    if not sertifika:
        return None
    simdi = simdi or datetime.now(timezone.utc)
    nedenler: list[str] = []

    if tanim is not None and sertifika.get("definition_hash") not in (None, tanim):
        nedenler.append(NEDEN_TANIM)
    if koken is not None and sertifika.get("lineage_set_hash") not in (None, koken):
        nedenler.append(NEDEN_KOKEN)

    son = sertifika.get("son_gecerlilik")
    if isinstance(son, str):
        try:
            son = datetime.fromisoformat(son)
        except ValueError:
            son = None
    if isinstance(son, datetime):
        if son.tzinfo is None:
            son = son.replace(tzinfo=timezone.utc)
        if simdi > son:
            nedenler.append(NEDEN_SURE)

    return {
        "seviye": sertifika.get("seviye"),
        "sertifikalayan_id": sertifika.get("sertifikalayan_id"),
        "sertifika_notu": sertifika.get("sertifika_notu"),
        "son_gecerlilik": son.isoformat() if isinstance(son, datetime) else None,
        "gecerli": not nedenler,
        "yeniden_dogrulama_gerekli": bool(nedenler),
        "otomatik_iptal_nedeni": nedenler or None,
    }


def rozet_kademesi(durum_kaydi: dict[str, Any] | None) -> str | None:
    """Sertifika → **güven rozetinin kademesi**. Yeni bir panel değil, var olan rozetin
    kademesi (yol haritası birebir: *"güven rozetinin kademesi (yeni panel DEĞİL)"*).

    🔴 **Çürümüş bir sertifika kademe VERMEZ** — `uyari` döner. Çürük bir onayı
    *"sertifikalı"* diye göstermek, rozeti bir **süse** çevirirdi (MIMARI'nin kalibre
    edilmemiş güven sayısına itirazının aynısı).
    """
    if not durum_kaydi:
        return None
    if durum_kaydi.get("yeniden_dogrulama_gerekli"):
        return "uyari"
    seviye = durum_kaydi.get("seviye")
    return seviye if seviye in SEVIYELER else None
