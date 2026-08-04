"""FAZ 0.18 — **METRİK KAYDI = HAKEM.** Bir iş terimi kaç cube'a aitse, hakem birdir.

## Neden — bu belgenin tek en büyük ölçülmüş kazancı

`CLARIFY:konu` **%11,5** + yanlış-cube **%6,8** ≈ **turların ~%18'i**, ve ikisinin de
**kanıtlanmış baskın kökü aynı**: bir iş terimi **iki cube tarafından sahiplenilmiş ve
hakem yok**. Korpus raporu birebir gösteriyor:

* boyahane yanlış-cube listesinin **ilk 10'unun 10'u** → `elektrik`
* atiksan'ın (**%98, en iyi şirket**) **ilk 9'unun 9'u** → `satış`

Canlı bir kullanıcı turu da aynı sınıfı bağımsız olarak buldu: *"bu yıl bakiye"*
`cari`'ye gitti (**₺11,86 milyon**), aynı soru `mizan`'da **₺0** verdi — sistem birini
**kura ile** seçti, sormadı, seçtiğini de yazmadı.

## Neden bu tasarım — `cube_router` SAF kalır

`cube_router` **hiçbir bayrak okumaz**; deterministik olması bilinçli bir karardır.
Bu yüzden kayıt **şemaya yazılır** (`schema["metrik_kaydi"]`) ve `_match_cube` onu
oradan okur. Sonuç:

* **Kayıt yoksa ya da boşsa davranış BİREBİR bugünkü** — madde **kendi kendine güvenli**.
* Bayrak, kaydın şemaya **yazılıp yazılmayacağını** belirler; yani bayrak, ayarların
  erişilebilir olduğu **derleme sınırında** durur, sıcak yolda değil.

## Neden ikinci bir eşleştirici YOK

Kayıt, `_match_cube`'un **ilk satırıdır** — paralel bir yol değil. Paralel bir yol
açmak, aynı sorunun iki sahibini yaratmak olurdu ve bu deponun **1 numaralı kusuru**
tam olarak budur.

## Boş kayıt neden anlamlı

Taslak katalogdan üretilir ve `sahiplenilen_terimler` **boş başlar**: kayıt *"bu terim
çakışıyor"* der ama *"sahibi şudur"* **demez**. Doldurma işi **FAZ 3.1'in sahiplik
turudur**. Yani bu madde **çakışmayı görünür kılar**, kararı vermez — ve görünmeyen bir
çakışma düzeltilemez.
"""

from __future__ import annotations

from typing import Any

#: Şemadaki anahtar. `cube_router` bunu okur; yoksa bugünkü davranış aynen sürer.
SEMA_ANAHTARI = "metrik_kaydi"


def cakisan_terimler(schema: dict[str, Any]) -> dict[str, list[str]]:
    """`terim → [sahiplenen cube'lar]`, **yalnız birden fazla sahibi olanlar**.

    Terim = **ölçü sinonimi** (cube sinonimi değil): kullanıcının yazdığı iş kelimesi
    budur. `elektrik` üç cube'un ölçü sözlüğünde geçiyorsa üçü de aday demektir ve
    `_match_cube` bugün onu **ölçü-kanıtı uzunluğuyla** kırmaya çalışır — deterministik
    ama **keyfi** bir kural, çünkü hangi cube'un "doğru" olduğu bir **iş kararıdır**.
    """
    sahip: dict[str, set[str]] = {}
    for c in schema.get("cubes") or []:
        ad = c.get("name")
        for _olcu, sinonimler in (c.get("measure_synonyms") or {}).items():
            for s in sinonimler or []:
                if s:
                    sahip.setdefault(str(s), set()).add(ad)
    return {t: sorted(v) for t, v in sorted(sahip.items()) if len(v) > 1}


def taslak_uret(schema: dict[str, Any]) -> list[dict[str, Any]]:
    """Katalogdan **taslak** kayıt. `sahiplenilen_terimler` BOŞ başlar.

    ⚠ Taslak bir **karar değildir**: yalnız *"bu terim çakışıyor, adaylar şunlar"* der.
    Boş `sahiplenilen_terimler` → `hakem()` `None` döner → `_match_cube` bugünkü yolunu
    izler. Bu, maddenin **kendi kendine güvenli** olmasının mekanizmasıdır.
    """
    return [
        {
            "terim": terim,
            "adaylar": adaylar,
            "sahiplenilen_terimler": [],          # FAZ 3.1'in sahiplik turu doldurur
            "olusturulma_yontemi": "otomatik_taslak",
        }
        for terim, adaylar in cakisan_terimler(schema).items()
    ]


def sahiplikle_birlestir(kayit: list[dict[str, Any]],
                         sahiplik: dict[str, str | None]) -> list[dict[str, Any]]:
    """Taslak kayda **kalıcı sahiplik kararlarını** işler. FAZ 2.2b.

    🔴 **0.18 KENDİ KENDİNE ATILDI ve bu fonksiyon onu besliyor.** Taslak katalogdan
    üretiliyordu ve `sahiplenilen_terimler` **boş** başlıyordu; boşu dolduracak bir yol
    olmadığı için `hakem()` **hiçbir zaman** karar veremezdi. *Kurulmuş ama beslenemeyen
    bir hakem, kurulmamış bir hakemdir.*

    ⚠ **Sahiplik yalnız ADAYLAR arasından seçilebilir.** Kayıtta aday olmayan bir cube'u
    sahip yazmak, katalogda olmayan bir kararı kataloğa dayatmak olurdu — ve o karar
    sessizce **hiçbir şey yapmazdı** (hakem adayı olmayan cube'u döndürse `_match_cube`
    onu bulamazdı). Aday dışı sahiplik **yok sayılır**, kayda `gecersiz_sahip` düşülür:
    *sessizce yok saymak, kullanıcının kararını çöpe atıp ona söylememektir.*
    """
    out: list[dict[str, Any]] = []
    for k in kayit:
        yeni = dict(k)
        sahip = sahiplik.get(str(k.get("terim")))
        if sahip and sahip in (k.get("adaylar") or []):
            yeni["sahiplenilen_terimler"] = [sahip]
            yeni["olusturulma_yontemi"] = "insan_karari"
        elif sahip:
            yeni["gecersiz_sahip"] = sahip     # aday değil → görünür kalır, uygulanmaz
        out.append(yeni)
    return out


def cift_sahiplik_denetle(kayit: list[dict[str, Any]]) -> list[str]:
    """**Çift sahiplik ihlalleri** — bir terimi birden fazla cube *sahiplenmişse*.

    Adaylık çakışması normaldir (kayıt tam bunun için var). İhlal, **iki cube'un aynı
    terimi SAHİPLENMESİDİR**: o zaman hakem yine yoktur, ama artık bir de *"hakem var"*
    beyanı vardır — beyan ile kodun ayrıştığı hâl, bu deponun avladığı sınıf.
    """
    sahiplenen: dict[str, list[str]] = {}
    for k in kayit:
        for cube in k.get("sahiplenilen_terimler") or []:
            sahiplenen.setdefault(str(k.get("terim")), []).append(str(cube))
    return [f"`{t}` terimini {len(v)} cube sahiplenmiş: {sorted(v)}"
            for t, v in sorted(sahiplenen.items()) if len(v) > 1]


def hakem(terim: str, kayit: list[dict[str, Any]] | None) -> str | None:
    """Terimin **sahibi** cube — yoksa `None` (bugünkü yol izlenir).

    🔴 **Tek sahip.** `_match_cube` bunu **ilk satırında** çağırır; paralel bir
    eşleştirme yolu **yoktur**.
    """
    if not kayit or not terim:
        return None
    for k in kayit:
        if k.get("terim") != terim:
            continue
        sahipler = k.get("sahiplenilen_terimler") or []
        if len(sahipler) == 1:                    # tam olarak BİR sahip → hakem kararı
            return str(sahipler[0])
        return None                               # 0 sahip = karar yok · >1 = ihlal
    return None


def semaya_yaz(schema: dict[str, Any], *, acik: bool) -> dict[str, Any]:
    """Bayrak açıksa kaydı **şemaya** koyar. Kapalıysa **hiç dokunmaz**.

    `GERİ AL` mekanizması budur: bayrak `off` → anahtar yok → `cube_router` kaydı hiç
    görmez → davranış **birebir bugünkü**. Bayrak sıcak yola değil, **derleme sınırına**
    konur; `cube_router`'ın saflığı korunur.
    """
    if not acik:
        schema.pop(SEMA_ANAHTARI, None)
        return schema
    kayit = taslak_uret(schema)

    # 🔴 ÇİFT SAHİPLİK REDDİ — **fail-closed**. Bir terimi iki cube birden sahiplenmişse
    # hakem yine YOKTUR, ama artık bir de *"hakem var"* beyanı vardır. Beyan ile kodun
    # ayrıştığı hâl bu deponun avladığı sınıftır; kendini çelişen bir kayıt **yazılmaz**.
    # Taslak bugün boş sahiplikle geldiği için bu dal ateşlenmez — koruma **FAZ 3.1'in
    # sahiplik turu için** kurulur, o tur bir terimi iki kez sahiplendirmeye kalkarsa.
    ihlaller = cift_sahiplik_denetle(kayit)
    if ihlaller:
        raise ValueError(
            "METRİK KAYDI ÇİFT SAHİPLİK İHLALİ — kayıt YAZILMADI (fail-closed):\n  "
            + "\n  ".join(ihlaller)
            + "\nHakem tek olmalı: iki sahip, hakemsizlikten daha kötüdür çünkü üstüne "
              "bir de 'hakem var' beyanı ekler.")

    schema[SEMA_ANAHTARI] = kayit
    return schema
