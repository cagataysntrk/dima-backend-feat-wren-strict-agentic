"""FAZ 1.1 — **MOTOR-SEVİYESİ RLS.** `always_filter`'ın yerini motor devralır.

## Neden — ölçülmüş iki baypas

`always_filter` (LookML `sql_always_where`) bir **uygulama katmanı** yamasıdır:
`WrenService._inject_always_filter` onu **yalnız o cube'un kendi SQL'ine** ekler. İki yol
onu atlıyor ve ikisi de ölçüldü:

1. **JOIN** — `compose.py:434` (**G10**) birebir yazıyor: *"filtreli bir modele join'lemek
   `always_filter`'ı **BAYPAS EDER**"*, çünkü join `__source` seviyesinde gerçekleşir.
2. **Discovery ham SQL** — `_inject_always_filter` yalnız `cube_sql()` yolundan çağrılır;
   ham SQL o fonksiyona **hiç uğramaz**. MIMARI §6.3'ün ❌ işaretli maddesi budur.

Motor RLS'i ikisini de **yapısal olarak** kapatır: koşul **her model referansına** iner.
Ölçüldü ve `tests/test_motor_rls_onkosul.py` ile donduruldu (7 test).

## Neden `pii.py` KALIYOR

Bu modül `app/pii.py`'nin yerini **almaz**. RLS **satır** düşürür, PII **hücre** maskeler;
ikisi farklı katman ve MIMARI *"PII son savunma olarak KALIR"* diyor. İki savunmadan birini
ötekinin gerekçesiyle kaldırmak, bu deponun avladığı *"aynı kuralın iki sahibi"* kusurunun
tersi kadar tehlikelidir: **hiç sahibi olmayan bir kural**.

## ⟳ SESSION PROPERTY — `1.1`'de ERTELENDİ, `1.2`'de GELDİ

`1.1`'de `always_filter` **sabit** bir yüklemdi (`CANCELLED = 0`) ve session'a bağlı
değildi; o turda `oturum_ozellikleri()` yazmak **çağıranı olmayan bir yetenek** üretirdi
(`K3` · ters yetim). **`1.2` ile gerçek tüketici doğdu:** kolon düzeyi erişim denetimi
(`columnLevelAccessControl`) **zorunlu** bir session property ister.

* `sql_literal()` — motor değerleri **SQL literali** olarak alır ve tek literal dışındaki
  her şeyi reddeder (ölçüldü: `'x' OR '1'='1'` → *"allow only literal value"*). Bu
  **ikinci** savunmadır; **birinci** savunma tırnak kaçışını yapan bu fonksiyondur —
  motora güvenip kaçışı atlamak, savunmayı **tesadüfe** bırakmak olurdu (MIMARI §5'in
  `guard_sql` eleştirisinin aynısı).
* ⚠ `wren.engine._plan` `frozenset(dict.items())` bekler; düz `dict` `TypeError` verir
  (ölçüldü, `test_motor_rls_onkosul.py::test_5_*` ile kilitli).

## 🔴 FAZ 1.2 — CLS kolonu MASKELEMEZ, PLANDAN DÜŞÜRÜR

Ölçüldü: seviye yetersizken `SELECT *` o kolonu **hiç döndürmüyor**. Bu `pii.py`'den
**kategorik olarak farklı** bir davranıştır: maskeleme kolonu **gösterir** (`123****89`),
CLS onu **yok eder**. Ve yok etme **sessizdir** — kullanıcı sorduğu kırılımın neden
gelmediğini **öğrenemez**.

Bu yüzden `motor_cls` varsayılanı **`off`**'tur (`motor_rls`'ten farklı olarak — orada
gölge davranışı değiştirmiyordu). `on` kademesi, *"hangi kolonlar esirgendi"* yüzeyi
kurulmadan **açılamaz**: sessizce eksik bir tablo, maskeli bir tablodan **daha kötüdür**,
çünkü kullanıcı eksikliği **fark etmez**. Kapı bunu kilitler.

## 🔴 `defaultExpr` YASAK — ölçülmüş bir FAIL-OPEN

Ölçüldü: `required: False` + `defaultExpr` verilirse, property **hiç gönderilmese bile**
sorgu **varsayılanla** koşar (`WHERE tenant = 'HERKES'`). Yani kimlik enjekte edilmeyi
unutulduğu gün sistem **hata vermez**, sessizce **başka bir filtreyle** cevap verir.
`required: True` ise motor **fail-closed** davranır (planlama hatası). Bu modül yalnız
`required: True` üretir ve `defaultExpr`'i **reddeder**.
"""

from __future__ import annotations

import json
from typing import Any

#: Manifest'teki anahtar — motorun beklediği ad.
MODEL_ANAHTARI = "rowLevelAccessControls"

#: Geçerli bayrak kademeleri. `shadow` **varsayılandır**: `strict_sql_policy`'nin aynı
#: disiplini — bir güvenlik katmanı önce **ölçülür**, sonra açılır.
KADEMELER = ("off", "shadow", "on")

#: Kolon düzeyi erişim seviyesini taşıyan session property.
OTURUM_GIZLILIK = "session_gizlilik"

#: `sensitivity` sınıfı → CLAC **eşiği**. Motor `operator`+`threshold` istiyor (etiket
#: değil), yani eşleme **beyan edilmesi gereken yeni bir iştir** — yol haritası D13a
#: düzeltmesi bunu açıkça söylüyor.
#:
#: 🔴 **SEVİYELER UYDURULMADI, VAR OLAN KARARDAN TÜRETİLDİ.** `authorize.py` zaten
#: `"pii:view": 2` (admin+) diyor ve gerekçesi yazılı: *"bu aksiyona sahip rol maskesiz
#: görür"*. Yeni bir gizlilik merdiveni icat etmek, aynı kuralın **ikinci sahibini**
#: doğururdu. Bugün iki seviye var (**0** = `pii:view` yok · **2** = var); ara seviye
#: **1** eşik yapısında **yer tutuyor** ama kimseye atanmıyor — ihtiyaç doğduğunda
#: eşleme değil yalnız `gizlilik_seviyesi()` değişir.
SENSITIVITY_ESIGI: dict[str, str] = {
    "person": "0",     # seviye > 0 gerekir
    "special": "1",    # seviye > 1 gerekir
    # "normal" → CLAC YOK (herkese görünür); sözlükte olmaması bilinçli.
}


def _kural(ad: str, kosul: str) -> dict[str, Any]:
    """Sabit yüklemli RLAC — `requiredProperties` **boş**.

    Ölçüldü: motor sabit koşullu kuralı `requiredProperties` olmadan da uyguluyor.
    `always_filter` session'a bağlı **değildir** (`CANCELLED = 0`), o yüzden ona session
    property iliştirmek uydurma bir bağımlılık yaratırdı.
    """
    return {"name": ad, "requiredProperties": [], "condition": str(kosul)}


def always_filter_kurallari(manifest: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Cube `always_filter`'larını **model** RLAC'larına çevirir → `{model: [kural]}`.

    ## Neden cube değil MODEL

    `always_filter` bir **cube** özelliğidir ama baypasların ikisi de **model** düzeyinde
    olur (join `__source`'ta, ham SQL modele doğrudan). Koşulu modele koymak, onu her
    referansta uygulatır — kapatılmak istenen tam bu.

    ## Aynı modele iki cube bakıyorsa

    Koşullar **tekilleştirilir**; aynı yüklem iki kez yazılmaz. Farklı iki yüklem varsa
    **ikisi de** yazılır ve motor onları `AND`'ler (ölçüldü). Bu **bilinçli**: iki cube
    farklı daraltma istiyorsa, ortak modelin görmesi gereken şey **kesişimdir** — birini
    seçmek, ötekinin kullanıcısına sessizce fazla satır göstermek olurdu.
    """
    modeller = {m.get("name") for m in manifest.get("models") or []}
    out: dict[str, list[dict[str, Any]]] = {}
    for cube in manifest.get("cubes") or []:
        pred = cube.get("always_filter") or cube.get("alwaysFilter")
        hedef = cube.get("base_object") or cube.get("baseObject")
        if not pred or not hedef or hedef not in modeller:
            continue
        kurallar = out.setdefault(str(hedef), [])
        if any(k["condition"] == str(pred) for k in kurallar):
            continue                      # aynı yüklem iki cube'dan geldi — tekilleştir
        kurallar.append(_kural(f"af_{hedef}_{len(kurallar)}", str(pred)))
    return out


def kurallari_denetle(kurallar: list[dict[str, Any]]) -> list[str]:
    """İhlalleri döndürür — **fail-open desenleri**.

    🔴 Tek ihlal sınıfı ölçülmüş bir gerçektir: `required: False` + `defaultExpr` verilirse
    property **hiç gönderilmese bile** sorgu varsayılanla koşar. Kimlik enjeksiyonunu
    unuttuğumuz gün sistem hata vermez, **başka bir filtreyle** cevap verir — ve bu,
    filtresiz cevaptan daha sinsidir çünkü sonuç **makul görünür**.
    """
    ihlaller: list[str] = []
    for k in kurallar:
        for p in k.get("requiredProperties") or []:
            if p.get("defaultExpr") is not None:
                ihlaller.append(
                    f"`{k.get('name')}` → `{p.get('name')}`: **defaultExpr YASAK** "
                    "(property gönderilmezse sorgu varsayılanla koşar = fail-open)")
            elif not p.get("required"):
                ihlaller.append(
                    f"`{k.get('name')}` → `{p.get('name')}`: `required=False` — motor "
                    "fail-closed davranmaz, kimliksiz sorgu SESSİZCE geçer")
    return ihlaller


def manifeste_yaz(manifest_json: bytes | str, *, kademe: str) -> tuple[bytes, int]:
    """**Servis edilen** manifest. Döner: `(baytlar, yazılan_kural_sayısı)`.

    | kademe | manifest | servis edilen cevap |
    |---|---|---|
    | `off` | dokunulmaz | bugünkü |
    | `shadow` | **dokunulmaz** | **bugünkü** — gölge yalnız ÖLÇER |
    | `on` | RLAC yazılır | motor filtreliyor |

    🔴 **`shadow` MANİFESTE YAZMAZ — ve bu bir DÜZELTMEDİR.** İlk sürüm `shadow`'da da
    yazıyordu; o hâlde motor filtreyi **uygular** ve ham-SQL yolundaki cevap **değişirdi**.
    Yani "gölge" adı altında **canlı bir davranış değişikliği** sevk edilirdi — bu deponun
    avladığı *"beyan var, kod başka şey yapıyor"* sınıfının güvenlik katmanındaki hâli.
    Doğru desen **zaten bu dosyanın komşusunda yazılı**: `_sql_policy`'nin gölgesi motoru
    gevşek kurar ve katı politikayı **AYRI bir motorla PARALEL** dener. `golge_manifesti()`
    o ayrı motorun manifestini verir.

    ⚠ **801 yeşil test bunu YAKALAMADI** ve nedeni kayda değer: `alwaysFilter` yalnız
    **gulteks**'te var (logo-3 tenant'ı) ve süit o tenant'ın **ham SQL** yolunu ölçmüyor.
    Yeşil bir süit, ölçmediği bir davranış hakkında hiçbir şey söylemez.

    🔴 **GERİ AL mekanizması budur** ve bayrak **derleme sınırında** durur, sıcak yolda
    değil — `metrik_kaydi.semaya_yaz` ile **aynı desen**. Sıcak yola bayrak koymak, her
    sorguda bir yapılandırma okuması ve iki kod yolu demektir.
    """
    if kademe not in KADEMELER:
        raise ValueError(f"`motor_rls` kademesi geçersiz: {kademe!r} — {KADEMELER}")
    ham = manifest_json if isinstance(manifest_json, bytes) else manifest_json.encode()
    if kademe != "on":
        return ham, 0
    return rlac_manifesti(ham)


def rlac_manifesti(manifest_json: bytes | str) -> tuple[bytes, int]:
    """RLAC **yazılmış** manifest — kademeden bağımsız.

    İki çağıranı var ve ikisi de bilinçli: `manifeste_yaz` (`on`'da servis için) ve
    **gölge denetimi** (`shadow`'da yalnız kıyas için). Kademe kararı burada **verilmez**;
    bir dönüşümün kendi anahtarını okuması, aynı kuralın iki sahibini doğurur.
    """
    ham = manifest_json if isinstance(manifest_json, bytes) else manifest_json.encode()
    manifest = json.loads(ham)
    kurallar = always_filter_kurallari(manifest)
    if not kurallar:
        return ham, 0

    toplam = 0
    for model in manifest.get("models") or []:
        yeni = kurallar.get(model.get("name"))
        if not yeni:
            continue
        ihlaller = kurallari_denetle(yeni)
        if ihlaller:
            raise ValueError(
                "RLS KURAL İHLALİ — manifest YAZILMADI (fail-closed):\n  "
                + "\n  ".join(ihlaller))
        model[MODEL_ANAHTARI] = yeni
        toplam += len(yeni)
    return json.dumps(manifest, ensure_ascii=False).encode(), toplam


def motorun_devraldigi_cubelar(manifest_json: bytes | str, *, kademe: str) -> set[str]:
    """`on` kademesinde `_inject_always_filter`'ın **ELİNİ ÇEKECEĞİ** cube'lar.

    🔴 **İki sahip olmaz.** `on` iken koşulu hem motor hem uygulama katmanı uygularsa
    yüklem iki kez yazılır; `CANCELLED = 0` için bu zararsızdır ama kural genel olmalı —
    bu depoda *"aynı kuralın iki sahibi"* birinci kusur sınıfıdır.

    `shadow`'da **uygulama katmanı sahibi KALIR**: gölge, servis edilen cevabı
    değiştirmemelidir. Gölgenin işi ölçmek, davranmak değil.
    """
    if kademe != "on":
        return set()
    manifest = json.loads(manifest_json if isinstance(manifest_json, bytes)
                          else manifest_json.encode())
    modeller = {m.get("name") for m in manifest.get("models") or []}
    return {
        str(c.get("name")) for c in manifest.get("cubes") or []
        if (c.get("always_filter") or c.get("alwaysFilter"))
        and (c.get("base_object") or c.get("baseObject")) in modeller
    }


# ══ FAZ 1.2 · SESSION PROPERTY + KOLON DÜZEYİ ERİŞİM ═════════════════════════

def sql_literal(deger: Any) -> str:
    """Değeri **SQL string literaline** çevirir — tırnak kaçışıyla.

    🔴 **Birinci savunma budur.** Motor ikinci savunmayı koyuyor (tek literal dışındakini
    reddediyor, ölçüldü) ama ona güvenip kaçışı atlamak, savunmayı **tesadüfe**
    bırakmaktır — MIMARI §5'in `guard_sql` eleştirisinin aynısı.

    `None`/boş → `NULL` **DEĞİL**: `ValueError`. Bir kimlik alanının boş olması bir değer
    değil bir **hatadır**; `NULL` üretmek `x = NULL` gibi **hiçbir satırla eşleşmeyen ama
    hata da vermeyen** bir koşul doğururdu — sessiz bir boş sonuç, sessiz bir sızıntı
    kadar kötüdür çünkü ikisi de fark edilmez.
    """
    if deger is None or deger == "":
        raise ValueError(
            "session property değeri BOŞ — bir kimlik alanı boşsa bu bir değer değil bir "
            "HATADIR. `NULL` üretmek, hiçbir satırla eşleşmeyen ama hata da vermeyen bir "
            "koşul doğururdu (sessiz boş sonuç).")
    if isinstance(deger, bool) or not isinstance(deger, (str, int)):
        raise TypeError(
            f"session property değeri `str` ya da `int` olmalı, {type(deger).__name__} "
            "geldi. Yapılandırılmış bir değeri literale çevirmek, kaçışın nerede "
            "yapıldığını belirsizleştirir.")
    if isinstance(deger, int):
        return str(deger)
    return "'" + str(deger).replace("'", "''") + "'"


def gizlilik_seviyesi(principal: Any) -> int:
    """Principal'ın kolon gizlilik seviyesi. **Var olan karardan türetilir.**

    `authorize.py` zaten *"`pii:view` (admin+) maskesiz görür"* diyor; bu fonksiyon o
    kararı **okur**, yeni bir merdiven **icat etmez**. İkinci bir gizlilik kuralı yazmak,
    bu deponun 1 numaralı kusuru olurdu.
    """
    if getattr(principal, "is_superadmin", False):
        return 2
    try:
        from control_plane.authorize import can
    except ImportError:                                      # pragma: no cover
        return 0
    return 2 if can(principal, "pii:view") else 0


def oturum_ozellikleri(principal: Any) -> dict[str, str]:
    """`Principal` → motor session property'leri (**SQL literali** olarak).

    ⚠ `frozenset(dict.items())`'e çevirmek **çağıranın** işidir (`wren.engine._plan` onu
    öyle bekliyor); burada sözlük döner ki test edilebilir ve loglanabilir olsun.

    `principal` yoksa **boş sözlük** döner — ve bu bilinçli: eksik bir property motorun
    **fail-closed** dalını ateşler (ölçüldü). Uydurma bir varsayılan koymak, o kapıyı
    sessizce açardı.
    """
    if principal is None:
        return {}
    return {OTURUM_GIZLILIK: sql_literal(gizlilik_seviyesi(principal))}


def _clac(kolon_adi: str, sinif: str) -> dict[str, Any]:
    """Bir kolon için CLAC kuralı. `requiredProperties` **`required=True`** — `1.1`'de
    ölçülen `defaultExpr`/`required=False` fail-open deseni burada da yasak."""
    return {
        "name": f"clac_{kolon_adi}",
        "requiredProperties": [{"name": OTURUM_GIZLILIK, "required": True}],
        "operator": "GREATER_THAN",
        "threshold": SENSITIVITY_ESIGI[sinif],
    }


def clac_manifesti(manifest_json: bytes | str) -> tuple[bytes, int]:
    """Hassas kolonlara CLAC yazar. Döner: `(baytlar, yazılan_kural_sayısı)`.

    Sınıflandırma `app/sensitivity.py::classify`'dan gelir — **tek sahip**. İkinci bir
    hassasiyet kuralı yazmak, `pii.py` ile CLS'in **ayrışması** demekti: aynı kolon bir
    katmanda maskeli, ötekinde görünür olurdu.
    """
    from app.sensitivity import classify

    ham = manifest_json if isinstance(manifest_json, bytes) else manifest_json.encode()
    manifest = json.loads(ham)
    toplam = 0
    for model in manifest.get("models") or []:
        for kolon in model.get("columns") or []:
            sinif = classify(kolon)
            if sinif not in SENSITIVITY_ESIGI:
                continue
            kolon["columnLevelAccessControl"] = _clac(str(kolon.get("name")), sinif)
            toplam += 1
    if not toplam:
        return ham, 0
    return json.dumps(manifest, ensure_ascii=False).encode(), toplam


def cls_manifeste_yaz(manifest_json: bytes | str, *, kademe: str) -> tuple[bytes, int]:
    """**Servis edilen** manifest — `on` dışında **dokunulmaz**.

    🔴 `motor_rls` ile **aynı gölge disiplini**: gölge ölçer, davranmaz. Ama varsayılan
    farklı ve nedeni ölçülmüş: CLS kolonu **maskelemez, plandan DÜŞÜRÜR** ve düşme
    **sessizdir**. Kullanıcı sorduğu kırılımın neden gelmediğini öğrenemez → varsayılan
    **`off`** (bkz. modül belgesi).
    """
    if kademe not in KADEMELER:
        raise ValueError(f"`motor_cls` kademesi geçersiz: {kademe!r} — {KADEMELER}")
    ham = manifest_json if isinstance(manifest_json, bytes) else manifest_json.encode()
    if kademe != "on":
        return ham, 0
    return clac_manifesti(ham)
