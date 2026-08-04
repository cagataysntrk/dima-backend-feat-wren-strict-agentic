"""FAZ 2.1 — **ÇEKİRDEK KATMAN: evrensel metrik sözlüğü + GRAIN SÖZLEŞMESİ.**

## Ölçülen kusur

`ticaret` cube'u **üç ERP'de** aynı adı, aynı sinonimi ve aynı ölçü adını (`satis_tutari`)
taşıyor — ama **farklı grain**'de:

| pack | `base_object` | bir satır ne demek |
|---|---|---|
| `mikro-v16` | `stok_hareketleri` | bir stok hareketi |
| `logo-3` | `faturalar` | bir fatura |
| `netsis` | `faturalar` | bir fatura |

Yani *"bu yıl satış"* sorusu üç şirkette **karşılaştırılamaz üç sayı** döndürüyor ve bunu
**hiçbir yerde beyan eden yok**. Cube'un *semantic drift* diye adlandırdığı hata modunun
kendi pack'lerimizin içindeki hâli. *Aynı adı taşıyan iki sayının farklı şeyler olduğunu
söylemeyen bir semantik katman, semantik katman değildir.*

## 🔴 SÖZLÜK ile İFADE AYRI — ve bu ayrım fazın en kritik kararı

Bu modül **ifadeye dokunmaz**. Adım (a) yalnız *anlamı* birleştirir: **sinonim · birim**.
⚠ `additive` bilerek **dışarıda** (gerekçe `cube_birlestir`'de: bir sözlük alanı değil,
**toplama semantiğidir** — ve ölçüm aracı bunu benim yerime buldu). `cari`'nin ölçü **adları** aynı ama **ifadeleri farklı**
(`SUM(CASE WHEN cha_tip=0…)` ↔ `SUM(BORC)`) ve `base_object`'leri dört ayrı tablo — yani
*"saf tekrar"* teşhisi **yanlıştı** (yol haritasının kendi denetim düzeltmesi). *Aynı ada
sahip iki ifadeyi "saf tekrar" sanıp birleştirmek, bu fazın üretebileceği en sessiz
hatadır.*

## ⚠ `base_object` ÇEKİRDEKTE YOK — bilinçli

Fiziksel bağlama ERP'den ERP'ye **gerçekten** değişir; anlam değişmez. `base_object`'i
çekirdeğe koymak, üç ERP'nin birine ayrıcalık tanımak ve ötekilerini *"yanlış"* ilan
etmek olurdu.

## 🔴 GRAIN İHLALİ = COMPOSE REDDİ (fail-closed)

Uyarı **değil ret** — `G5` (harf çakışması) ve `G10` (`always_filter`) kapılarıyla aynı
sınıf. Bir uyarı, derlenmiş ve dağıtılmış bir MDL bırakır; o MDL'yi kimse geri almaz ve
yanlış sayı **üretimde** çıkar. *Build zamanında durmak, üretim zamanında yanlış cevap
vermekten kesinlikle iyidir* (`compose.dogrula`'nın aynı gerekçesi).

## Kademeler — `motor_rls`/`motor_cls` ile AYNI disiplin

| kademe | ne yapar |
|---|---|
| `off` *(varsayılan)* | hiçbir şey — compose çıktısı **birebir bugünkü** |
| `shadow` | sözlük birleşir **ama YAZILMAZ**; grain ihlali **loglanır**, reddetmez |
| `on` | sözlük yazılır; grain ihlali **compose'u REDDEDER** |

⚠ `shadow` bilerek **yazmıyor**: yazan bir gölge, gölge değildir (FAZ 1.1'de ölçülen
kusur — `motor_rls` gölgesi manifeste RLAC yazıyordu ve *"shadow"* adı altında **servis
edilen cevabı** değiştirecekti).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from app.logging_setup import get_logger

_log = get_logger("cekirdek")

#: `motor_rls`/`motor_cls`/`strict_sql_policy` ile **aynı** kademe sözlüğü.
KADEMELER = ("off", "shadow", "on")

#: Çekirdek pack'in dizin adı — `demo/packs/cekirdek/`.
PACK_DIZINI = "cekirdek"
SOZLUK_DOSYASI = "metrik_sozlugu.yml"


class GrainIhlali(RuntimeError):
    """Çekirdek bir grain sözleşmesi ilan etti, ERP katmanı başka grain'e bağladı.

    `ProjectValidationError` **değil**: o motorun yapısal doğrulayıcısının hatasıdır ve
    ikisini aynı tipe bindirmek, hangi kapının reddettiğini **kütükte** belirsizleştirirdi.
    """


def kademe() -> str:
    """`cekirdek_katman` ∈ `off|shadow|on` — `_rls_kademesi` ile **aynı okuma deseni**.

    Config okunamazsa `off`: ölçülemeyen bir yapılandırmada **davranışı değiştirmek**,
    bu maddenin engellemek için var olduğu şeyin ta kendisi olurdu.
    """
    try:
        from app.config import get_settings

        mod = str(getattr(get_settings(), "cekirdek_katman", "off") or "off").lower()
    except Exception:                       # noqa: BLE001 — config yoksa bugünkü davranış
        return "off"
    return mod if mod in KADEMELER else "off"


def sozluk_yukle(base: Path) -> dict[str, Any]:
    """`packs/cekirdek/metrik_sozlugu.yml` → sözlük. Yoksa **boş** (çekirdek katman yok).

    ⚠ Yokluk bir **hata değil bir durumdur**: çekirdek katman opsiyoneldir ve olmayan bir
    katman için uyarı basmak, kurmamayı bir kusur gibi gösterirdi (`eskalasyon`'un aynı
    kararı).
    """
    yol = base / "packs" / PACK_DIZINI / SOZLUK_DOSYASI
    if not yol.is_file():
        return {}
    try:
        return yaml.safe_load(yol.read_text(encoding="utf-8")) or {}
    except Exception:                       # noqa: BLE001
        _log.warning("çekirdek metrik sözlüğü okunamadı: %s", yol, exc_info=True)
        return {}


def grain_adi(sozluk: dict[str, Any], base_object: str | None) -> str | None:
    """`base_object` → sözleşmedeki grain adı. Tanınmıyorsa `None`.

    🔴 `None` *"ihlal"* DEĞİL, *"bilinmiyor"* demektir: sözleşmede sayılmamış bir tabloyu
    ihlal saymak, çekirdek sözlüğü büyümeden **her yeni ERP'yi reddederdi**. Bilinmeyen
    grain **serbest** kalır ve bu **görünür** olur (kütük) — *bilinmeyeni yasak saymak,
    katmanı büyütmeyi cezalandırırdı.*
    """
    if not base_object:
        return None
    bo = str(base_object).strip().lower()
    for ad, spec in (sozluk.get("grain_sozlesmeleri") or {}).items():
        adaylar = {str(x).strip().lower() for x in (spec or {}).get("base_object_adlari") or []}
        if bo in adaylar:
            return str(ad)
    return None


def metrik_haritasi(sozluk: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """`{metrik adı: sözlük girdisi}` — ad çakışması **son yazan kazanır** değil, **ilk**.

    ⚠ Sözlükte aynı metrik iki kez tanımlıysa bu bir **kusurdur** ve sessizce ikincisini
    almak onu gizlerdi; ilkini tutup ikincisini **loglamak** kusuru görünür bırakır.
    """
    out: dict[str, dict[str, Any]] = {}
    for m in sozluk.get("metrikler") or []:
        ad = str((m or {}).get("name") or "").strip()
        if not ad:
            continue
        if ad in out:
            _log.warning("çekirdek sözlükte ÇİFT metrik tanımı: %s (ilki geçerli)", ad)
            continue
        out[ad] = m
    return out


def _ekle(sahip: dict, anahtar: str, yeni: list) -> bool:
    """Listeye **additive** ekleme — var olanı silmez. Değişiklik olduysa `True`."""
    cur = list(sahip.get(anahtar) or [])
    once = len(cur)
    for s in yeni or []:
        if s not in cur:
            cur.append(s)
    if len(cur) == once:
        return False
    sahip[anahtar] = cur
    return True


def cube_birlestir(meta: dict[str, Any], sozluk: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Bir cube metadata'sına çekirdek **sözlüğünü** işler. `(yeni_meta, degisiklikler)`.

    🔴 **İFADEYE DOKUNMAZ.** `expression` · `base_object` · `type` **hiç okunmaz**.
    Birleşen tek şey: `synonyms` (ekleyerek) · `unit` (yalnız **yoksa**).

    ## 🔴 `additive` BİLEREK BİRLEŞTİRİLMİYOR — ve bunu ÖLÇÜM ARACI buldu

    ⚠ **Bu bir düzeltmedir.** İlk sürüm `additive`'i de dolduruyordu (yol haritası onu
    *"sözlük"* diye sayıyor) ve gölge diff **0 fark** diyordu — çünkü aracın kendisi
    `additive`'i *sözlük* kovasına koymuştu. Kova düzeltilir düzeltilmez gerçek çıktı:
    `mal` ve `ticaret` cube'ları `additive` **beyan etmiyor** ve çekirdek onlara
    `additive: full` **yazıyordu**.

    `additive` bir sözlük alanı **değildir**, bir **toplama semantiğidir**: `semi`, motora
    *"dönem boyunca toplama, dönem SONU al"* dedirtir. Ve doğru değeri **ifadeye** bağlıdır
    — `cari.bakiye` üç ERP'de `SUM(borç − alacak)`, yani **hareket toplamı** (`full`
    davranışı doğru olabilir); bir **stok anlık görüntüsü** olsaydı `semi` olurdu. Merkezî
    olarak, ifadeye bakmadan karara bağlamak, bu maddenin engellemek için var olduğu
    *"aynı ada sahip iki şeyi aynı sanmak"* hatasının ta kendisidir.

    → `additive` sözlükte **beyan olarak kalır** (metriğin kanonik semantiği) ama adım
    (a)'da **yazılmaz**; ERP beyanı ile çekirdek beyanının **çelişmesi** adım (c)'nin
    kararıdır (`grain` ile aynı sınıf).

    ⚠ `unit` var olanı **EZMEZ**: ERP bir birimi bilerek farklı yazmış olabilir (miktar
    `kg` ↔ `adet`) ve ezmek **sessizce yanlış birim** demekti. *Çekirdek, EKSİK olanı
    tamamlar; var olanı düzeltmez.*
    """
    metrikler = metrik_haritasi(sozluk)
    degisti: list[str] = []
    for m in meta.get("measures") or []:
        ad = str(m.get("name") or "")
        cekirdek = metrikler.get(ad)
        if not cekirdek:
            continue
        if _ekle(m, "synonyms", cekirdek.get("synonyms") or []):
            degisti.append(f"{ad}.synonyms")
        # 🔴 YALNIZ `unit` — `additive` BİLEREK YOK (gerekçe yukarıda: toplama
        # semantiğidir, sözlük değil; doğru değeri İFADEYE bağlıdır ve karar adım (c)'nin).
        for alan in ("unit",):
            if cekirdek.get(alan) and not m.get(alan):
                m[alan] = cekirdek[alan]
                degisti.append(f"{ad}.{alan}")
    return meta, degisti


def grain_denetle(cube_adi: str, meta: dict[str, Any],
                  sozluk: dict[str, Any]) -> list[str]:
    """Grain sözleşmesi ihlallerini **bulur** — fırlatmaz (karar çağıranın).

    Bir ihlal: çekirdek metrik `grain: X` beyan ediyor, cube'un `base_object`'i ise
    sözleşmede **başka** bir grain'e (`Y`) ait.

    🔴 Saf fonksiyon — DB'siz, dosyasız test edilebilir (`context.py` felsefesi).
    """
    metrikler = metrik_haritasi(sozluk)
    # ⚠ `grain_kaynak` ÖNCE: türev küplerin `base_object`'i türetilmiş görünüm adıdır
    # (`karlilik_src`) ve hiçbir sözleşmede geçmez — yani kapı, kendi "bilinmeyen grain
    # serbest" kuralı yüzünden KÖR kalırdı. `compose` türev küpe kaynağın gerçek
    # `base_model`'ini damgalar (FAZ 2.1(d)); grain kararı ONDAN türer.
    cube_grain = grain_adi(sozluk, meta.get("grain_kaynak") or meta.get("base_object"))
    if cube_grain is None:
        return []                            # bilinmeyen grain SERBEST (yukarıdaki gerekçe)
    ihlaller: list[str] = []
    for m in meta.get("measures") or []:
        ad = str(m.get("name") or "")
        beklenen = (metrikler.get(ad) or {}).get("grain")
        if beklenen and str(beklenen) != cube_grain:
            ihlaller.append(
                f"`{cube_adi}.{ad}`: çekirdek `grain: {beklenen}` beyan ediyor, cube "
                f"`{meta.get('base_object')}` (grain: {cube_grain}) üstünde tanımlı")
    return ihlaller


# ── VARYANT ÇÖZÜMLEMESİ — ad göçünün sorgu-zamanı karşılığı ─────────────────
#
# 🔴 **Neden BURADA, `cube_router`'da DEĞİL.** *"Bu iki ölçü aynı kavramın farklı
# grain'i mi"* sorusu **çekirdek katmanın** sorusudur; router'a koymak, sözleşme
# bilgisini iki eve bölerdi. Router **çağırır**, bilmez.

def olcu_eslemesi(prev_measures: list, prev_meta: dict, cm: dict) -> dict | None:
    """`{eski ölçü: hedef cube'daki karşılığı}` — ya da `None` (karşılığı yok).

    ## 🔴 Neden ADA bakmak YETMİYOR — ölçülen kusur (FAZ 2.1 ad göçü)

    Bu fonksiyon eskiden `m not in cm["measures"]` diyordu, yani **ada** bakıyordu. Ad
    göçünden **önce** o ad üç ayrı grain taşıyordu (`ticaret.satis_tutari`@fatura ↔
    `mal.satis_tutari`@stok_hareketi ↔ `karlilik.satis_tutari`@ERP'ye-göre) ve geçiş
    **karşılaştırılamaz iki sayıyı** sessizce aynı raporun içine koyuyordu — üstelik
    `source="cube"` rozetiyle. Ad göçü onu kırdı; bu eşleme onu **doğru** biçimde geri
    getiriyor: eşleşme **kavram** düzeyinde (`cekirdek_metrik`), ve grain değişiyorsa
    çağıran bunu **söylemek zorunda** (`grain_uyarisi`).

    🔴 **`kiyaslanamaz` ölçülere ASLA geçilmez.** `satis_tutari_turev`'in grain'i ERP'ye
    göre değişir; oraya geçmek, kullanıcıya *"aynı şeyin kırılımı"* diye **başka bir şeyi**
    göstermek olurdu.
    """
    hedef = set(cm.get("measures") or [])
    if not hedef:
        return None
    yasak = set(cm.get("kiyaslanamaz") or [])
    kaynak_bag = (prev_meta or {}).get("cekirdek_metrik") or {}
    hedef_bag = cm.get("cekirdek_metrik") or {}
    out: dict[str, str] = {}
    for m in prev_measures:
        if m in hedef and m not in yasak:
            out[m] = m                                   # birebir ad — en güçlü eşleşme
            continue
        kavram = kaynak_bag.get(m) or m                   # bağ yoksa ADIN KENDİSİ kavramdır
        aday = [h for h, k in hedef_bag.items()
                if k == kavram and h in hedef and h not in yasak]
        if len(aday) != 1:
            return None      # 0 → karşılığı yok · >1 → BELİRSİZ; belirsizliği sessizce
        out[m] = aday[0]     # çözmek, bu maddenin engellemek için var olduğu şeydir
    return out


def grain_uyarisi(prev: dict, yeni: dict, schema: dict) -> str:
    """Geçişte ölçü **varyantı değiştiyse** kullanıcıya söylenecek ek — yoksa boş dize.

    🔴 *Sessiz bir grain değişimi, sessiz bir yanlıştır.* Kullanıcı *"ürün bazlı satış"*
    dediğinde cevabı alabilmeli, ama aldığı sayının **başka bir taneliğe** ait olduğunu da
    görmeli: fatura başına satış ile fatura KALEMİ başına satış aynı şey değildir.
    """
    eski = list(prev.get("measures") or [])
    yeni_m = list(yeni.get("measures") or [])
    degisen = [(a, b) for a, b in zip(eski, yeni_m) if a != b]
    if not degisen:
        return ""
    # ⚠ `cube_router._cube_meta` ÇAĞRILMIYOR ve bu bilinçli: `cube_router` bu modülü
    # import ediyor (varyant bilgisi çekirdeğin işi) — tersi **döngüsel import** olurdu.
    # Aranan şey tek satırlık bir sözlük taraması; ikinci bir "meta bulucu" değil.
    yeni_meta = next((c for c in (schema.get("cubes") or [])
                      if c.get("name") == yeni.get("cube")), {}) or {}
    etiket = (yeni_meta.get("measure_synonyms_display") or {})
    parca = " · ".join(f"{a} → {etiket.get(b, b)}" for a, b in degisen)
    return f" — ⚠ ölçünün TANELİĞİ değişti ({parca}); iki sayı doğrudan kıyaslanamaz"
