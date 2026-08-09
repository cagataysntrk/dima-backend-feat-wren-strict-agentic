"""PLAN ÇALIŞTIRICISI — adımları sırayla koşar, değerleri birbirine geçirir (FAZ O-2).

## Ne yapar, ne YAPMAZ

| yapar | **yapmaz** |
|---|---|
| adımları sırayla koşar | ❌ LLM çağırmaz |
| `$1` referanslarını çözer | ❌ SQL **yazmaz** |
| her adımın makbuzunu tutar | ❌ aritmetik yapmaz |
| bütçeyi sayar | ❌ katalog dışına çıkamaz |

🔴 **Sayıyı her zaman küp koyar.** Bu dosya bir sayı **hesaplamaz**; hesaplayan
`ilkeller`dir ve o da yalnız **koşmuş satırlar** üzerinde çalışır. Orkestratörün
Discovery'den farkı tam burada: *Discovery'de LLM **cevabı** üretir; burada LLM **soruyu
böler**, cevabı her parçada **küp** verir.*

## Neden `planner.Planlayici`'nin içine değil

`Planlayici` bir **yönetişim** katmanıdır: dört kapı (kayıt · yetki · deterministik-önce ·
bütçe) ve adım makbuzu. Bu dosya bir **yorumlayıcıdır**: referans çözer, sıra kurar.
İkisini aynı sınıfa koymak, *"aynı sınıfa iki farklı soru sordurmak"*tı — bu deponun
`toplanabilirlik()` docstring'inde adıyla kayıtlı desen.

⚠ `KURAL B`: bugün **hiçbir yol** bu dosyayı çağırmıyor. Bağlanması `O-4`'ün işi ve o
faz kendi bayrağıyla gelir. *Bir yorumlayıcıyı önce yazıp sonra bağlamak, ikisini birden
yapmaktan daha az risklidir.*
"""

from __future__ import annotations

import re
from typing import Any

from app.logging_setup import get_logger

_log = get_logger("plan_kosucu")

_REF = re.compile(r"^\$([1-9][0-9]?)$")


class PlanHatasi(Exception):
    """Bir adım koşulamadı — **fail-closed**. Sessizce atlanmaz, tur düşürülür.

    ⚠ Neden istisna: bir adımın sessizce düşmesi, sonraki adımların **eksik bir girdiyle**
    koşması demektir ve sonuç `source=cube` rozetiyle döner. Bu deponun en tehlikeli
    sınıfı. *Derlenmeyen bir plan, sessizce yanlış bir plandan iyidir.*
    """


def _coz(deger: Any, ciktilar: list[Any]) -> Any:
    """`$1` gibi bir referansı önceki adımın çıktısına çevirir; değilse aynen döner.

    ⚠ **İleri referans yasak**: `$3` üçüncü adımdayken henüz yoktur. Şema bunu
    engellemiyor (JSON Schema sıra bilmez), o yüzden kapı **burada**.
    """
    if not isinstance(deger, str):
        return deger
    m = _REF.match(deger)
    if not m:
        return deger
    i = int(m.group(1))
    if i < 1 or i > len(ciktilar):
        raise PlanHatasi(f"`${i}` henüz koşmamış bir adıma işaret ediyor "
                         f"(o anda {len(ciktilar)} adım tamamlanmıştı)")
    return ciktilar[i - 1]


def kos(plan: dict, *, sorgu_kos, cube_meta: dict | None = None,
        azami_sorgu: int = 8) -> dict:
    """Planı koşar ve `{"ciktilar": [...], "makbuz": [...]}` döndürür.

    `sorgu_kos(cube_query) -> rows`: **tek** dış bağımlılık ve bilerek bir **parametre** —
    bu dosya `wren_service`'i tanımaz. Böylece testte sahte bir koşucuyla, üründe gerçek
    motorla aynı yorumlayıcı çalışır.

    ⚠ `azami_sorgu`: `Butce`'nin sorgu ayağının bu katmandaki karşılığı. Aşımda
    `PlanHatasi` — çünkü bir planın yarısını koşup *"işte kısmi cevap"* demek, hangi
    adımın eksik olduğunu **kullanıcının** bulmasını istemektir.
    """
    from app import ilkeller as _ilk

    adimlar = (plan or {}).get("adimlar") or []
    if not adimlar:
        raise PlanHatasi("plan boş — koşulacak adım yok")
    _lower = set((cube_meta or {}).get("lower_is_better") or [])
    ciktilar: list[Any] = []
    makbuz: list[dict] = []
    sorgu_sayisi = 0

    for sira, adim in enumerate(adimlar, 1):
        fiil = adim.get("fiil")
        try:
            if fiil == "SORGU":
                sorgu_sayisi += 1
                if sorgu_sayisi > azami_sorgu:
                    raise PlanHatasi(
                        f"plan {sorgu_sayisi} sorgu istiyor, bütçe {azami_sorgu}")
                cikti = sorgu_kos(adim["cube_query"])
            elif fiil == "BAGLA":
                olcu = adim["olcu"]
                cikti = _ilk.bagla(_coz(adim["kaynak"], ciktilar), adim["boyut"], olcu,
                                   en_iyi_az=olcu in _lower)
            elif fiil == "HESAPLA":
                hedef = _coz(adim["hedef"], ciktilar)
                # `BAGLA`'nın çıktısı `(varlık, değer)` — `HESAPLA` yalnız **varlığı**
                # ister. Bu dönüşüm burada, çünkü iki ilkelin sözleşmesini bilen tek yer
                # burası; `ilkeller` birbirini tanımaz ve tanımamalı (saf kalsın).
                if isinstance(hedef, tuple):
                    hedef = hedef[0]
                cikti = _ilk.hesapla(_coz(adim["kaynak"], ciktilar), adim["boyut"],
                                     adim["olcu"], hedef)
            else:
                # 🔴 Kalan fiiller (`KIYASLA` · `AYRISTIR` · `TREND` · `ANLAT`) gövdelerini
                # `contribution`/`yoy`/`answer`'dan alacak ve **bağlanması `O-4`'ün işi**.
                # Burada sessizce atlanmıyorlar: bir plan onları isterse tur **düşer** ve
                # sebebi yazılır. *Bir fiili şemaya koyup çalıştırıcıda unutmak, onu
                # sessizce yalan yapmaktır.*
                raise PlanHatasi(f"`{fiil}` fiilinin çalıştırıcısı henüz bağlanmadı (O-4)")
        except PlanHatasi:
            raise
        except (KeyError, TypeError, ValueError) as e:
            raise PlanHatasi(f"adım {sira} (`{fiil}`) koşulamadı: {e}") from e
        ciktilar.append(cikti)
        makbuz.append({"sira": sira, "fiil": fiil,
                       "satir": len(cikti) if isinstance(cikti, list) else None})

    _log.info("plan koştu: %d adım · %d sorgu", len(adimlar), sorgu_sayisi)
    return {"ciktilar": ciktilar, "makbuz": makbuz, "sorgu_sayisi": sorgu_sayisi}
