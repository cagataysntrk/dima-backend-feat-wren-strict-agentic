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

import pathlib
from typing import Any

from app.logging_setup import get_logger

_log = get_logger("metrik_kaydi")

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


#: FAZ 3.1 — pack ile gelen **karar kaydı** dosyası (alan bilgisi, tenant'tan bağımsız).
KARAR_DOSYASI = "sahiplik_kararlari.yml"


def pack_kararlari(base: Any) -> dict[str, str | None]:
    """`packs/cekirdek/sahiplik_kararlari.yml` → `{terim: sahip|None}`.

    🔴 **Üç kutu, tek dosya.** `sahip` **yalnız** `kutu: tek_sahip` satırlarında vardır;
    `belirsiz` ve `grain_hatasi` satırları bilinçli olarak sahipsizdir ve **yine de
    kayıtta dururlar**: *"henüz bakılmadı"* ile *"bakıldı, belirsiz olduğuna karar
    verildi"* aynı şey değildir ve bu ayrım kaybolursa aynı terim her turda yeniden
    tartışılır.

    ⚠ Bu **pack** kararıdır (alan bilgisi, her tenant'ta aynı); tenant'ın kendi kararı
    (FAZ 2.2b `MetrikSahipligi`) onu **ezer** — en spesifik kazanır, `compose`'un katman
    sırasıyla aynı ilke.
    """
    return _kararlari_oku(pathlib.Path(str(base)) / "packs" / "cekirdek" / KARAR_DOSYASI)


def _kararlari_oku(yol: pathlib.Path) -> dict[str, str | None]:
    """Tek bir karar dosyası → `{terim: sahip|None}`. Yoksa/bozuksa boş sözlük.

    ⚠ `sahip: None` **bir kayıttır, boşluk değil**: *«bakıldı, belirsiz olduğuna karar
    verildi»*. Üst katman onu bilerek **sahipsiz bırakmak** için de kullanabilir.
    """
    import yaml

    if not yol.is_file():
        return {}
    try:
        d = yaml.safe_load(yol.read_text(encoding="utf-8")) or {}
    except Exception:                                        # noqa: BLE001
        _log.warning("sahiplik karar kaydı okunamadı: %s", yol, exc_info=True)
        return {}
    out: dict[str, str | None] = {}
    for k in d.get("kararlar") or []:
        terim = str((k or {}).get("terim") or "").strip()
        if terim:
            out[terim] = str(k["sahip"]) if k.get("sahip") else None
    return out


def katmanli_kararlar(base: Any, *, sektorler: list[str] | None = None,
                      moduller: list[str] | None = None,
                      company: str | None = None) -> dict[str, str | None]:
    """🔴 `§SH` — **UYGULANAN** kararlar: yalnız TENANT'A ÖZGÜ katmanlardan.

    ## Neden bu fonksiyon var — `FAZ 3.1`'in gerilemesi bir KATMAN hatasıydı

    `3.1` pack kararlarını doğrudan uyguladı ve korpus **%93,2 → %92,6** geriledi
    (`gitas` erişim **%72 → %69**). Teşhis o gün *«pack kararı dayatılamaz»* diye
    yazıldı ve karar **öneriye** indirildi (`3.1b`). Ölçüm doğruydu, **teşhis eksikti**:

    > Sorun kararın *pack'ten gelmesi* değil, **çekirdekten** gelmesiydi.
    > `elektrik → enerji_makine` bir **boyahane** kararıdır (çakışan iki küp de orada);
    > `gitas` (tarım-ticareti) o çakışmayı **hiç yaşamaz**. Çekirdeğe konunca
    > `gitas`'a da dayatıldı — ve gerileme oradan geldi.

    Karar **doğru katmana** taşınınca dayatma **yapısal olarak imkânsız** olur:
    `gitas` boyahane sektör paketini yüklemez, dosyayı **hiç okumaz**.

    ## Katman sırası — `compose` ile AYNI, ve bu bir tesadüf değil

        çekirdek  →  modül  →  sektör  →  şirket
        (öneri)      ────────  uygulanır  ────────

    ⚠ **Çekirdek bilerek DIŞARIDA:** oraya yazılan bir karar her tenant'a gider ve
    `3.1`'in ölçtüğü şey tam olarak budur. Çekirdek katmanı `pack_kararlari()` ile
    **öneri** olarak okunmaya devam eder — *bilgi kaybolmaz, yalnız dayatılmaz.*

    ⚠ **Modül dâhil:** bir modül kararı yalnız o modülü yükleyen tenant'a gider; bu da
    tenant'a özgüdür. Bugün modül karar dosyası yok — sıra **yer tutuyor**, çünkü
    olmayan bir katmanı sonradan araya sıkıştırmak, sırayı ikinci kez düşünmek olur.

    En spesifik kazanır: şirket > sektör > modül. Tenant'ın çalışma-zamanı kararı
    (`MetrikSahipligi`) hepsinin üstündedir ve `sahiplikle_birlestir` onu sonra işler.
    """
    kok = pathlib.Path(str(base))
    out: dict[str, str | None] = {}
    for m in (moduller or []):
        out.update(_kararlari_oku(kok / "packs" / "modul" / str(m) / KARAR_DOSYASI))
    for s in (sektorler or []):
        out.update(_kararlari_oku(kok / "packs" / "sektor" / str(s) / KARAR_DOSYASI))
    if company:
        out.update(_kararlari_oku(kok / "companies" / str(company) / KARAR_DOSYASI))
    return out


def onerilerle_birlestir(kayit: list[dict[str, Any]],
                         oneriler: dict[str, str | None]) -> list[dict[str, Any]]:
    """Pack karar kaydını **ÖNERİ olarak** işler — **uygulamaz**. FAZ 3.1b.

    ## 🔴 NEDEN ÖNERİ — ölçüm bunu ZORLADI

    FAZ 3.1'de pack kararları doğrudan **uygulanıyordu** ve korpus **geriledi**:
    `%93,2 → %92,6`, `gitas` erişim `%72 → %69`. Teşhis: kararlar `boyahane`/`atiksan`'ın
    **ölçülen** kusurları için yazılmıştı ama pack düzeyinde **her şirkete** dayatılıyordu.
    `gitas` (netsis) için `satis → ticaret` yanlış olabilir — orada `mal` da meşru bir sahip.

    *Bir tenant'ın alan bilgisini bütün tenant'lara dayatmak, alan bilgisi olmaktan çıkıp
    **varsayım** olur.*

    → Pack artık yalnız **önerir** (`onerilen_sahip`); **uygulayan** tek şey tenant'ın
    kendi kararıdır (`MetrikSahipligi`, FAZ 2.2b). Öneri ekranda görünür ve **tek tıkla**
    kabul edilir — yani alan bilgisi **kaybolmaz**, yalnız **dayatılmaz**.
    """
    out: list[dict[str, Any]] = []
    for k in kayit:
        yeni = dict(k)
        oneri = oneriler.get(str(k.get("terim")))
        # ⚠ Öneri de yalnız ADAYLAR arasından anlamlıdır; aday olmayan bir öneri
        # gösterilse kullanıcı tıklar ve hiçbir şey olmazdı.
        if oneri and oneri in (k.get("adaylar") or []):
            yeni["onerilen_sahip"] = oneri
        out.append(yeni)
    return out


def sahiplikle_birlestir(kayit: list[dict[str, Any]],
                         sahiplik: dict[str, str | None],
                         *, yontem: str = "insan_karari") -> list[dict[str, Any]]:
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
            # ⚠ `§SH` — KÖKEN KAYBOLMAZ: `insan_karari` (tenant'ın çalışma-zamanı kararı)
            # ile `pack_karari` (sektör/şirket paketinin beyanı) **farklı şeylerdir** ve
            # ekranda farklı okunmalıdırlar. *İkisini tek etikete indirmek, kararı kimin
            # verdiğini silmek olurdu.*
            yeni["olusturulma_yontemi"] = yontem
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


def semaya_yaz(schema: dict[str, Any], *, acik: bool, base: Any = None,
               sektorler: list[str] | None = None, moduller: list[str] | None = None,
               company: str | None = None) -> dict[str, Any]:
    """Bayrak açıksa kaydı **şemaya** koyar. Kapalıysa **hiç dokunmaz**.

    `GERİ AL` mekanizması budur: bayrak `off` → anahtar yok → `cube_router` kaydı hiç
    görmez → davranış **birebir bugünkü**. Bayrak sıcak yola değil, **derleme sınırına**
    konur; `cube_router`'ın saflığı korunur.
    """
    if not acik:
        schema.pop(SEMA_ANAHTARI, None)
        return schema
    kayit = taslak_uret(schema)
    # 🔴 FAZ 3.1 — SAHİPLİK TURU. Pack ile gelen **karar kaydı** (alan bilgisi) taslağa
    # işlenir; tenant'ın kendi kararı (FAZ 2.2b) uçta bunun ÜSTÜNE biner — en spesifik
    # kazanır (`compose`'un katman sırasıyla aynı ilke).
    if base is not None:
        # 🔴 FAZ 3.1b — **ÇEKİRDEK** kararı ÖNERİDİR, uygulama değil. Uygulasaydı korpus
        # gerilerdi (ölçüldü: %93,2 → %92,6) çünkü bir tenant'ın alan bilgisi bütün
        # tenant'lara dayatılmış olurdu.
        kayit = onerilerle_birlestir(kayit, pack_kararlari(base))
        # 🔴 `§SH` — ve TENANT'A ÖZGÜ katmanlar (modül · sektör · şirket) **UYGULANIR**.
        # `3.1`'in ölçümü doğruydu, teşhisi eksikti: sorun kararın *pack'ten* gelmesi
        # değil **çekirdekten** gelmesiydi. Doğru katmandaki bir kararı `gitas` **hiç
        # okumaz** — dosya onun yüklemediği bir pakette yaşar. Dayatma, bir politika
        # değil bir **dizin yapısı** meselesine indi.
        kayit = sahiplikle_birlestir(
            kayit, katmanli_kararlar(base, sektorler=sektorler, moduller=moduller,
                                     company=company),
            yontem="pack_karari")

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
