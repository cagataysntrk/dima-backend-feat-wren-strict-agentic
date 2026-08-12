r"""🔴 `§38.2 D7` — PLAN ÇALIŞTIRICISI **SALT-OKUNUR**; yetki boşluğu YOK.

## Raporun vaadi ve ölçüm

`§38.2 D7` şöyle diyordu: *«plan fiilleri `authorize()` GÖRMÜYOR → kayıt birleşince
yetki süzgeci plana bedava gelir»*. Bir denetim ajanı bunu bir **eksik** olarak
bildirdi (`grep authorize app/plan_semasi.py app/plan_kosucu.py` → **0**).

⊙ Ölçüm doğruladı: plan fiilleri `Planlayici.calistir()`'den **geçmiyor**;
`plan_kosucu.kos` onları doğrudan sevk ediyor (`if fiil == "SORGU": …`).

## 🔴 AMA BU BİR YETKİ BOŞLUĞU DEĞİL — ve sebebi yapısal

Ölçüldü (2026-08-12), her fiilin ne yaptığı:

| fiil | ne yapar | yetki riski |
|---|---|---|
| `SORGU` | `sorgu_kos` — isteğin **zaten yetkilendirilmiş** servisi | yok |
| `BAGLA`·`HESAPLA`·`MATRIS`·`SIRALA`·`KIR`·`SUZ`… | **koşmuş satırlar** üstünde saf dönüşüm | yok |
| `PANO` | **YAZMAZ** — `pano_taslagi` döndürür; kalıcılaştırma onayla, dışarıda | yok |
| `RAPOR`·`ANLAT` | metin üretir | yok |

⊙ Yani çalıştırıcı **salt-okunur ve idempotent**; bir plan, kullanıcının kendi
isteğiyle erişemeyeceği hiçbir şeye ulaşamaz. `authorize()` çağrısının yokluğu bir
**boşluk değil**, gereksizlik.

> *Bir kapının yokluğu ancak arkasında bir şey varsa boşluktur.*

## 🔴 GERÇEK DEĞİŞMEZ BUYDU — ve yalnız bir YORUMDA duruyordu

`plan_kosucu.py`'nin `PANO` dalı şunu yazıyor: *«🔴 **YAZMAZ.** Çalıştırıcı salt-okunur
ve idempotent kalıyor; **ilk yan etkili fiil bu değişmezi kırardı** (yarım pano ·
ikilenen pano · geri alınamayan yazma).»*

⚠ O cümle doğru ama **kapısızdı**: yarın yan etkili bir fiil eklenirse `authorize()`
yokluğu **gerçek** bir boşluğa döner ve hiçbir kırmızı konuşmaz.

## 🔴🔴 VE İLK YAZIMIM TAM O KUSURU TEKRARLADI *(denetim ajanı ölçtü, 2026-08-12)*

Bu dosyanın **beş kapısından ikisi**, koruduğunu iddia ettiği değişmezi değil, o
değişmezin **ilanını** ölçüyordu. Ölçüm:

    grep -n "YAZMAZ\|salt-okunur\|idempotent" app/plan_kosucu.py
    → 499:  # 🔴 **YAZMAZ.** Çalıştırıcı salt-okunur ve idempotent kalıyor; ilk yan

Üç dizge de **tek bir satırda**, ve o satır bir **`#` yorumudur**. Yani biri `PANO`
dalını kalıcılaştırmaya çevirse **ama yorumu bıraksa** iki kapı da yeşil kalırdı;
tersine yorumu silmek, davranış hiç değişmeden **kırmızı** verirdi. İkisi de yanlış.

> *Bir değişmezin ilanını ölçmek, değişmezi ölçmek değildir — ilan bir metindir,
> değişmez bir davranıştır; biri ötekine kefil olamaz.*

✅ **Onarım:** yük taşıyan kapı artık `kos()`'un **çağrı yüzeyi**dir (aşağıda,
`test_CALISTIRICI_SALT_OKUNUR_yapisal`). Yorum denetimi **silinmedi** ama
*belgelendirme* kapısı olduğu adıyla yazıldı — yeşilliği bir daha değişmez güvencesi
diye okunmasın.
"""

from __future__ import annotations

import ast
import pathlib

_APP = pathlib.Path(__file__).parent.parent / "app"
_KOSUCU = _APP / "plan_kosucu.py"

#: 🔴 `kos()`'un koşmasına izinli **modül-dışı** çağrıları. Hepsi ya **saf ilkeldir**
#: (`_ilk.*` — koşmuş satırlar üstünde dönüşüm), ya **enjekte edilmiş** ve isteğin
#: kendi yetkisiyle koşan servistir (`sorgu_kos`), ya da **kütük/paralellik**tir.
#: ⚠ Liste `ADR-0008` anlamında **kapalıdır**: yeni bir ad eklemek, salt-okunurluk
#: değişmezini yeniden gerekçelendirmeyi gerektirir.
IZINLI_DIS_CAGRILAR = {
    "sorgu_kos",                                      # enjekte, zaten yetkili
    "_ilk.bagla", "_ilk.hesapla", "_ilk.matris",      # saf ilkeller
    "_ilk.sirala", "_ilk.rapor", "_ilk.pano_taslagi",
    "_ex.submit", "_is.result",                       # paralellik
    "_log.info",                                      # kütük (ADR-0020)
}


def _agac() -> ast.AST:
    return ast.parse(_KOSUCU.read_text(encoding="utf-8"))


def _kos_govdesi() -> ast.FunctionDef:
    """⊘ Ön koşul: `kos()` **bulunmalı**. Bulunamazsa yüklem sessizce boşa düşmesin."""
    for n in ast.walk(_agac()):
        if isinstance(n, ast.FunctionDef) and n.name == "kos":
            return n
    raise AssertionError("⊘ ölçüm tabanı çöktü: `plan_kosucu.kos` bulunamadı")


def _fiil_dali(fiil: str) -> ast.If:
    """`if fiil == "<FİİL>"` dalını **AST'ten** bulur.

    🔴 İlk yazımım bunu `kaynak.index('if fiil == "SORGU"')` ile yapıyordu ve **yanlış
    adrese** düşüyordu: aynı dize `plan_kosucu.py`'de **iki kez** geçiyor — biri
    satır 156'daki ön-geçiş **doğrulama** döngüsünde, gerçek sevk dalı ise satır
    470'te. `index` ilkini bulduğu için *«yalnız SORGU dalında»* iddiası pratikte
    **320 satırlık** bir pencereye izin veriyordu.
    """
    for n in ast.walk(_agac()):
        if (isinstance(n, ast.If) and isinstance(n.test, ast.Compare)
                and isinstance(n.test.left, ast.Name) and n.test.left.id == "fiil"
                and isinstance(n.test.comparators[0], ast.Constant)
                and n.test.comparators[0].value == fiil
                # 🔴 Sevk dalı **`_adim_kos` içindedir**; ön-geçiş döngüsündeki aynı
                # karşılaştırma bir sayaç artırır, bir fiil koşmaz.
                and any(isinstance(x, ast.Return) for x in ast.walk(n))):
            return n
    raise AssertionError(f"⊘ ölçüm tabanı çöktü: `{fiil}` sevk dalı bulunamadı")


def test_CALISTIRICI_ROUTER_ITHAL_ETMIYOR():
    """🔴 Yazma yüzeyi `app/routers/*`tadır. Çalıştırıcı oraya **dokunmaz**.

    ⚠ Yüklem `ast` ile kurulu (kaba `grep` docstring'leri de yakalardı — bu deponun
    ölçülmüş dersi)."""
    ithal = set()
    for n in ast.walk(_agac()):
        if isinstance(n, ast.Import):
            ithal |= {a.name for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.module:
            ithal.add(n.module)
    kacak = sorted(x for x in ithal if x.startswith("app.routers"))
    assert not kacak, (
        f"🔴 `plan_kosucu` bir ROUTER ithal ediyor: {kacak}. Çalıştırıcı salt-okunur "
        "olmalı; yazma yüzeyi onay akışının (`POST /ask/eylem`) arkasındadır.")


def test_YAZMA_ARACLARI_CALISTIRICIDA_ANILMIYOR():
    """Yazma araçlarının adı bile çalıştırıcıda geçmemeli — geçiyorsa bir gün çağrılır."""
    kaynak = _KOSUCU.read_text(encoding="utf-8")
    from app import eylem as _e

    yazma_adlari = {b.uc.split(".")[-1] for b in _e.EYLEM_KAYIT}
    kacak = sorted(a for a in yazma_adlari if a and a in kaynak)
    assert not kacak, (
        f"🔴 çalıştırıcıda yazma fonksiyonu adı geçiyor: {kacak}. "
        "*İlk yan etkili fiil, salt-okunurluk değişmezini kırar.*")


def test_CALISTIRICI_SALT_OKUNUR_yapisal():
    """🔴🔴 **ASIL KAPI** — salt-okunurluk artık bir **yorumdan** değil, `kos()`'un
    **çağrı yüzeyinden** okunuyor.

    Değişmez şudur: çalıştırıcı dışarıya yalnız üç şey yapabilir — enjekte edilmiş ve
    **zaten yetkilendirilmiş** sorguyu koşmak, **saf ilkeller** üstünde dönüşüm, kütük.
    Bir gün yan etkili bir fiil eklenirse (`dashboards.add_widget`, bir `session.commit`,
    bir HTTP istemcisi…) o çağrı bu kümenin **dışında** olacaktır ve bu kapı konuşur.

    ⚠ Yüklem `ast` üstünde: `grep` docstring'i ve yorumu da yakalar — bu deponun
    ölçülmüş dersi, ve bu dosyanın **kendi** kusuruydu.
    """
    disari: dict[str, int] = {}
    for n in ast.walk(_kos_govdesi()):
        if not isinstance(n, ast.Call):
            continue
        f = n.func
        if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name):
            ad = f"{f.value.id}.{f.attr}"
        elif isinstance(f, ast.Name):
            ad = f.id
        else:
            continue
        # yerel yardımcılar (`_coz`, `_adim_kos`…) ve gömülüler kapsam dışı: modül
        # sınırını geçmezler.
        if ad.startswith("_") and "." not in ad:
            continue
        if ad in {"isinstance", "len", "list", "min", "set", "sum", "sorted", "dict",
                  "enumerate", "range", "PlanHatasi", "ThreadPoolExecutor", "dogrula"}:
            continue
        if ad.split(".")[0] in {"adim", "hatalar", "_isler", "ciktilar", "adimlar"}:
            continue          # yerel veri yapıları üstünde metot
        disari[ad] = n.lineno

    kacak = {a: s for a, s in disari.items() if a not in IZINLI_DIS_CAGRILAR}
    assert not kacak, (
        f"🔴 `plan_kosucu.kos` izinsiz bir dış çağrı yapıyor: {kacak}. "
        "*Çalıştırıcı salt-okunur ve idempotent olmalı; ilk yan etkili fiil bu "
        "değişmezi kırar.* Çağrı meşruysa `IZINLI_DIS_CAGRILAR`'a eklenir — ama "
        "eklemek, salt-okunurluğu YENİDEN GEREKÇELENDİRMEK demektir.")
    assert "sorgu_kos" in disari, (
        "⊘ ölçüm tabanı çöktü: `kos()` artık `sorgu_kos`'u hiç çağırmıyor — yüklem "
        "boşa düşmüş olabilir.")


def test_PANO_TASLAK_DONDURUYOR_KALICILASTIRMIYOR():
    """`PANO` bir **taslaktır**; kalıcılaştırma onay akışının işidir.

    ⊙ Bu, `§F13`'ün kararıyla aynı: ajan **önerir**, kullanıcı **onaylar**.

    ⚠ Yüklem artık **dalın döndürdüğü çağrıdır**, bir metin dilimi değil: ilk yazımım
    `kaynak[i:i+500]` içinde `"YAZMAZ"` arıyordu — yani dalın **yorumunu**.
    """
    dal = _fiil_dali("PANO")
    donenler = [n.value for n in ast.walk(dal) if isinstance(n, ast.Return) and n.value]
    adlar = {n.func.attr for n in donenler
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    assert adlar == {"pano_taslagi"}, (
        f"🔴 `PANO` dalı artık `pano_taslagi` DIŞINDA bir şey döndürüyor: {adlar}. "
        "Kalıcılaştırma onay akışının (`POST /ask/eylem`) arkasındadır.")


def test_DEGISMEZ_YAZILI_ve_GEREKCELI__yalnizca_BELGELENDIRME():
    """⚠ **Bu bir değişmez kapısı DEĞİLDİR** — adı bunu söylesin diye uzun.

    Ölçtüğü tek şey, salt-okunurluk gerekçesinin kaynakta **yazılı kaldığı**dır
    (beyan kültürü). Değişmezin kendisini `test_CALISTIRICI_SALT_OKUNUR_yapisal`
    ölçer. İkisini ayırmak zorunluydu: bu kapı tek başınayken, bir yorumun varlığı
    salt-okunurluk güvencesi diye okunuyordu.

    > *Bir yorumu korumak, yorumun anlattığı davranışı korumaz.*
    """
    kaynak = _KOSUCU.read_text(encoding="utf-8")
    assert "salt-okunur" in kaynak and "idempotent" in kaynak, (
        "🔴 salt-okunurluk GEREKÇESİ metinden silinmiş — davranış hâlâ doğru olabilir "
        "(yapısal kapı ayrı ölçüyor) ama bir sonraki okuyucu nedenini bilemez.")


def test_SORGU_DISINDA_HICBIR_FIIL_YENI_SORGU_ACMIYOR():
    """⚠ Paralelleştirme yalnız `SORGU` için; ötekiler **koşmuş satırlar** üstünde
    çalışır. Bir dönüşüm fiili yeni sorgu açarsa hem bütçe hem yetki varsayımı bozulur.

    🔴 **İlk yazımımda üç kusur birdeydi** (denetim ajanı ölçtü):
    ① `.index` **yanlış adrese** düştü (satır 156 = ön-geçiş sayacı, gerçek dal 470) →
    *«yalnız SORGU dalında»* iddiası **320 satırlık** pencereye izin veriyordu;
    ② saydığı iki *«çağrı»*dan biri `kos()`'un **docstring'iydi**
    (`` `sorgu_kos(cube_query) -> rows` ``);
    ③ bu yüzden **taban çökemezdi**: bütün gerçek çağrılar silinse bile docstring
    kalacağı için `assert cagrilar` **asla** konuşmazdı.

    ⊙ İronisi, aynı testin yorumu *«sayarak doğrula»* dersini alıntılıyordu — sayım
    yapılmıştı, **pencere** yanlış kurulmuştu. *Doğru sayıyı yanlış aralıkta saymak,
    saymamaktan daha ikna edicidir.*
    """
    dal = _fiil_dali("SORGU")
    dal_araligi = range(dal.lineno, max(getattr(x, "lineno", 0)
                                        for x in ast.walk(dal)) + 1)
    cagrilar = [n.lineno for n in ast.walk(_kos_govdesi())
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                and n.func.id == "sorgu_kos"]
    assert cagrilar, (
        "⊘ ölçüm tabanı çöktü: `kos()` içinde hiç `sorgu_kos` ÇAĞRISI yok — yüklem "
        "boşa düşmüş demektir. (Docstring'deki imza artık sayılmıyor.)")
    disarida = [c for c in cagrilar if c not in dal_araligi]
    assert not disarida, (
        f"🔴 `sorgu_kos` `SORGU` dalının DIŞINDA çağrılıyor (satır {disarida}) — "
        "bir dönüşüm fiili yeni sorgu açıyor demektir; bütçe ve yetki varsayımı bozulur.")
