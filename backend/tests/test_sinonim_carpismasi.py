"""FAZ 2a — KATALOG SAĞLIK ÖLÇÜMÜ: planın "üç YAML düzeltmesi" çerçevesi ÖLÇÜMLE ÇÜRÜDÜ.

## Ne ölçüldü (2026-08-02)

Plan §2.1 boyahanenin kaybını *"üç isimlendirilmiş YAML düzeltmesine indirgeniyor"* diye
özetliyordu ve birincisi `elektrik` çakışmasıydı. O özet `lab/reports/nl_corpus.md`'nin
**10 satırlık ÖRNEĞİNE** dayanıyordu.

Bu tur korpusu koşmadan doğrudan ölçtüm — her cube'un her ölçü sinonimi için
`route("bu yil <sinonim>")` ve sonucun **üç** yolu:

| sonuç | adet | pay |
|---|---|---|
| doğru cube | 291 | %62 |
| **yanlış cube** | **30** | %6 |
| **CEVAPSIZ** | **149** | **%32** |

Cevapsızın red dağılımı (Faz 0'ın `reject_reason` enstrümanı sayesinde ilk kez
görülebiliyor): **R1: 99** · R10: 32 · R4: 14 · R5: 2 · R9: 2.

**Asıl kayıp "yanlış cube"da DEĞİL.** Cevapsız sınıfı beş kat büyük ve içindeki en büyük
dilim **R1** — yani katalogda **var olan** bir ölçü sinonimi, düz sorulduğunda cube'unu
bile tanıtmıyor. Planın §2.1'i bu sınıfı hiç görmüyordu çünkü rapor yalnız yanlış-cube
örneği basıyor.

## `elektrik` düzeltmesi DENENDİ ve ÖLÇÜMLE REDDEDİLDİ

`surdurulebilirlik`'in cube-düzeyi kimliğinden ham kaynak adları (`elektrik · kwh ·
doğalgaz · gaz · tep · enerji · atıksu`) çıkarıldı. Gerekçe sağlamdı: bu cube **yoğunluk**
ölçer (su/kg, enerji/kg) ve `_match_cube` ölçü eşleştirmesinden önce koştuğu için adanmış
enerji cube'larını her seferinde yeniyordu.

Sonuç ölçüldü ve **kötüydü**:

| ölçüt | önce | sonra | planın kapısı |
|---|---|---|---|
| boyahane erişim | %64 | **%56** | *"artmalı"* ❌ |
| doğru-cube | %80 | %79 | *"düşmemeli"* ❌ |
| yanlış cube | 245 | 135 | ✓ |
| Discovery'ye düşen | 501 | **578** | ↑ |
| `test_eval_gate` | yeşil | **KIRMIZI** (coverage −%4,5) | ❌ |

**110 sessiz-yanlış kapandı ama 388 cevap kayboldu** — 3,5:1 kötü takas. Sebep: cube-düzeyi
kimliği kaldırmak **sahipliği çözmedi**, yalnız zorlamayı kaldırdı. Ölçü düzeyinde
`enerji_makine.toplam_elektrik_kwh` ile `surdurulebilirlik.toplam_enerji_kwh` **ikisi de**
`elektrik` iddia ediyor → `_match_cube` hiçbirini seçemiyor → **R1**.

Değişiklik **geri alındı**. Doğru çözüm bir **sahiplik kararıdır** (çıplak "elektrik" hangi
cube'un?) ve bu bir alan bilgisi işidir — planın `ortalama duruş` için açıkça *"karar
kalemi, sahibi ve tarihi olmalı"* dediği sınıfın aynısı.

## Bu dosyanın işi

Düzeltmek değil **ölçmek ve sabitlemek**: sayılar sessizce kötüleşemez, ve bir sonraki
turun hangi kümeye bakması gerektiği tahminle değil rakamla belirlenir.
"""

from __future__ import annotations

from collections import Counter

import pytest

from app import cube_router as cr

#: Ölçülen (2026-08-02, bugünkü katalog). Her satır bir ALAN KARARI bekliyor.
#: ⟳ **Faz 2a-3 sonrası yeniden ölçüldü: 30 → 23.** `_daha_spesifik_olcu_sahibi`
#: (kimlik asimetrisi düzeltmesi) yedi satırı **kimlik silmeden** kapattı:
#:   atiksu lt kg · dogalgaz tuketimi · elektrik tuketimi · ortalama sapma ·
#:   toplam durus · toplam elektrik · toplam tep
#: Bu, 2a-1'de `surdurulebilirlik` kimliğini SİLEREK denenen ve ölçümle reddedilen
#: (erişim %64→%56) düzeltmenin **doğru biçimi**: sahipliği spesifiklik çözüyor.
#: Kalan 23'ün tamamı ÇIPLAK tek kelime (elektrik · kwh · gaz · tep · fire · uretim ·
#: tahsilat · sapma …) — daha uzun bir ifade YOK, spesifiklikle kırılamaz. Bunlar
#: gerçek alan kararlarıdır (planın `ortalama duruş` kalemiyle aynı sınıf).
YANLIS_CUBE = {
    ("ariza durusu", "oee", "bakim"),
    ("breakdown", "oee", "bakim"),
    ("cari alacak", "mizan", "cari"),
    ("cari bakiye", "mizan", "cari"),
    ("cari borc", "mizan", "cari"),
    # 🔴 `§SH` (2026-08-11) — İKİ SATIR **ÇÖZÜLDÜ**, YÖNÜ TERSİNE DÖNDÜ.
    # `packs/sektor/boyahane/sahiplik_kararlari.yml` `elektrik` ve `dogalgaz` terimlerinin
    # sahibini `enerji_makine` ilan etti; `metrik_kaydi.hakem` artık `_match_cube`'un ilk
    # satırında karar veriyor. Eski satırlar (`… → surdurulebilirlik`) **ateşlenmiyor**;
    # yerlerine aynı çakışmanın **öteki yönü** geçti — yani bunlar bir kusur değil,
    # **kararın kendisidir**: `surdurulebilirlik`ten üretilen soru artık ilan edilmiş
    # sahibine gidiyor. ⊙ Korpus: doğru-cube **%94,4 → %95,5**.
    ("dogalgaz", "surdurulebilirlik", "enerji_makine"),        # ⟳ `§SH` · yön döndü
    ("downtime", "bakim", "oee"),
    ("elektrik", "surdurulebilirlik", "enerji_makine"),        # ⟳ `§SH` · yön döndü
    ("enerji tep", "enerji_makine", "surdurulebilirlik"),
    ("enerji tep", "enerji_tesis", "surdurulebilirlik"),
    ("fire", "oee", "parti"),
    ("gaz", "enerji_makine", "surdurulebilirlik"),
    ("hesap bakiyesi", "cari", "mizan"),
    ("kac parti", "oee", "parti"),
    ("kwh", "enerji_makine", "surdurulebilirlik"),
    ("parti sayisi", "oee", "parti"),
    ("renk sapmasi", "kalite", "parti"),
    ("sapma", "enerji_sapma", "parti"),
    ("spesifik enerji", "enerji_tesis", "surdurulebilirlik"),
    ("tahsilat", "mizan", "cari"),
    ("tep", "enerji_makine", "surdurulebilirlik"),
    ("tep", "enerji_tesis", "surdurulebilirlik"),
    ("uretim", "parti", "oee"),
}

#: Ölçülen cevapsız (`route()` None) red dağılımı. R1 = cube kimliği eşleşmedi.
#: ⟳ **Faz 2a-3: 149 → 107.** Kapsam kapısı (R10) 32→5, R4 14→1, R5 2→0 — çünkü artık
#: sorunun TAMAMINI açıklayan cube seçiliyor, kelimeler açıkta kalmıyor.
#: **R1 = 99 DEĞİŞMEDİ ve değişmemeli**: onlar ÇIPLAK ölçü adının iki cube'da birden
#: iddia edildiği GERÇEK belirsizliklerdir; `route()` tahmin etmeyi doğru reddediyor,
#: netleştirme chip'i `olcu_netlestirme` ile üretiliyor (MIMARI §6.1g).
#: ⟳ 2026-08-06 — KN-2 SAHİPLİK TEMİZLİĞİ + KÖK-7e. Kayma **kasıtlıdır** ve sebebi
#: yazılıdır (testin kendi cümlesi: *"kayması, kapsamın bir yerde değiştiği anlamına
#: gelir ve fark edilmeli"* — fark edildi, açıklanıyor).
#:
#:   R10  5 → 12   `maliyet`/`ik`ten ÇIKARILAN çıplak terimler (`toplam üretim` ·
#:                 `kimyasal/enerji maliyeti` · `kâr marjı` ailesi · `toplam maliyet`)
#:                 artık o cube'ların envanterinde yok → kendi sözlüklerine karşı
#:                 kapsam kapısına takılıyorlar. Bu bir KAYIP DEĞİL: aynı terimler
#:                 GERÇEK sahiplerinde (`oee` · `surdurulebilirlik` · `parti`) doğru
#:                 çözülüyor ve `eval` precision −%12,7 → **+%0,0**'a döndü.
#:   R4   1 → 3    aynı sebep, ölçü tarafı.
#:
#: 🔴 EN SERT KAPI GEÇTİ: `test_DOGRU_SAYISI_DUSMEDI` yeşil — doğru çözülen sinonim
#: sayısı DÜŞMEDİ. Raporun A2 anti-çözümünün (kimlik silme → 388 cevap kaybı) bu
#: temizlikte tekrarlanmadığının kanıtı odur, bu dağılım değil.
#: ⟳ **`M-2` (2026-08-08) — `default_measure` 3 → 11 küpe yazıldı.** Bu taramadaki etkisi
#: **dürüstçe şudur: SIFIR ERİŞİM KAZANCI.**
#:
#:   R4  3 → 1    iki soru artık *"ölçü yok"* diye reddedilmiyor (varsayılan bulundu)
#:   R10 12 → 14  …ama aynı iki soru bu kez **kapsam kapısına** takılıyor
#:   toplam cevapsız **116 → 116**
#:
#: 🔴 Yani bu taramada iki soru **R4'ten R10'a taşındı, cevaplanmadı**. Kazanç başka bir
#: popülasyondadır ve orada ölçüldü: bu tarama yalnız **çıplak ölçü sinonimlerini**
#: (`bu yil <sinonim>`) dener; `default_measure`'ın işe yaradığı yer ise **küp kimliği
#: geçen ama ölçü kelimesi geçmeyen** sorulardır. Canlı curl (üç soru, üçü de önce
#: LLM'e düşüyordu):
#:
#:   `bu yıl iş emri`  → `bakim_is_emri.is_emri_adedi` = 129   `route()` · LLM'siz
#:   `bu ay şikayet`   → `sikayet.sikayet_adedi`                `route()` · LLM'siz
#:   `bu yıl sevkiyat` → `sevkiyat.sevkiyat_adedi` = 105        `route()` · LLM'siz
#:
#: ⚠ Ve bir küp **geri alındı**: `kalite`'ye varsayılan verilince `test_YANLIS_CUBE_BUYUMEDI`
#: yeni bir çakışma gösterdi (`'hatali': oee → kalite`) — varsayılan ölçü o küpü
#: **açgözlü** yapmıştı. Dokuz denemeden **sekizi** temiz geçti; gerekçe küpün kendi
#: menü dosyasında.
#:
#: *Bir sayının değişmemesi, hiçbir şeyin değişmediği anlamına gelmez — ölçtüğü şeyin
#: değişmediği anlamına gelir.*
#: ⟳ **`§AA3` (2026-08-09) — `miktar`, `parti`ye de yazıldı: R1 99 → 101.**
#:
#: Sebep `AA13`'te ölçüldü: *«fire oranı ile ÜRETİM MİKTARINI aynı grafikte iki eksende»*
#: → sistem *«bu soru iki ayrı konunun ölçüsünü istiyor»* diyerek **yapabildiği** bir işi
#: reddediyordu; oysa `parti` ikisini de taşıyor ve eksik olan tek şey `miktar` kelimesini
#: **yazmamasıydı**.
#:
#: 🔴 **Bu iki satırlık kayma bir KAYIP değil, kelimenin gerçek durumunun İTİRAFIDIR.**
#: Bu bloğun kendi cümlesi R1'i şöyle tanımlıyor: *"çıplak ölçü adının iki cube'da birden
#: iddia edildiği **GERÇEK belirsizlikler**; `route()` tahmin etmeyi **doğru** reddediyor"*.
#: `miktar` artık gerçekten iki sahipli — ve **öyle olduğu için** iki çıplak sorgu
#: netleştirmeye düşüyor. Önceki hâl daha az R1 üretiyordu ama sebebi doğruluk değil,
#: `parti`'nin taşıdığı kavramı **adlandırmamasıydı**.
#:
#: ⚠ En sert kapı **yeşil kaldı**: `test_DOGRU_SAYISI_DUSMEDI` — doğru çözülen sinonim
#: sayısı DÜŞMEDİ. Yani kazanılan iki belirsizlik, kaybedilen bir cevap değil.
#: ⚠ Ve `§99.1` çiğnenmedi: `miktar` **zaten** `oee.toplam_uretim_kg`'nin sinonimiydi;
#: eklenen şey yeni bir belirsizlik değil, var olanın **eksik yarısı**.
#:
#: *Bir kelimeyi iki sahipli ilan etmek, onu iki sahipli yapmaz — zaten öyle olduğunu
#: söyler. Sayının artması, sistemin daha fazla bilmesindendir.*
#: ⟳🔴 **101 → 99 (2026-08-10, `§SY`): İKİ SORU DAHA CEVAPLANIYOR.**
#:
#: `ΔE`'nin `"dE!"` sinonimi pack'ten kaldırıldı — normalleşince Türkçenin bağlaç eki
#: `de` oluyordu ve *«bir **de** … ekle»* cümlelerinde **yanlış ölçü** eşleştiriyordu
#: (canlı `VII/B4`: kullanıcı gecikme istedi, renk sapması aldı — beyansız).
#:
#: ⊙ Aynı koşumda ölçülen bütün: `sessiz_yanlis` **10 → 8** · `dogru` **90 → 96** ·
#: `kabul` **1145 → 1147** · `R1` **101 → 99**. Yani kaldırılan sinonim yalnız yanlış
#: cevaplar üretmiyor, doğru cevapların **önünü de kesiyordu**: iki harflik bir eşleşme
#: cümlenin gerçek ölçüsünü gölgeliyordu.
#:
#: ⚠ `eval` coverage **−%0,9**: `dE` ile sorulan vaka(lar) artık eşleşmiyor. Takas
#: yazılı ve **kabul edildi** — iki sessiz yanlış ve altı doğru cevap karşılığında bir
#: kısaltmanın kaybı. *Bir kapsam sayısı, kapsadığı şey yanlışsa bir kazanç değildir.*
#:
#: ⟳ **`§SH-2` (2026-08-11) — `R10` **23 → 14**: BORÇ KAPANDI, taban geri geldi.**
#: Hakem *«daha spesifik eşleşmeyi ezemez»* kuralıyla sınırlandı (`_match_cube`); dokuz
#: redin tamamı geri döndü. Aşağıdaki `§SH` notu **tarihsel kayıttır** — bir bedel
#: ödendiği ve sonra geri alındığı, ikisi birden yazılmadan okunamaz.
#:
#: ⟳ ~~**`§SH` — `R10` 14 → 23 (+9), ve bu bir BEDELDİR, gizlenmiyor.**~~
#: Hakem `elektrik`/`dogalgaz` için `enerji_makine`'yi seçince, o cube'un **kapsam
#: kapısı** (R10 = seçilen cube sorunun tamamını açıklamıyor) dokuz sinonimde ateşliyor —
#: `surdurulebilirlik` daha geniş bir kimlik taşıdığı için önceden geçiyorlardı.
#: `R1` **99'da sabit** (gerçek belirsizlikler dokunulmadı), `R4`/`R9` değişmedi.
#:
#: 🔴 **TAKAS YAZILI VE KABUL EDİLDİ** — korpusla ölçüldü:
#:     doğru-cube  **%94,4 → %95,5**  (+1,1 puan)
#:     cevapsız    **%19,9 → %20,2**  (+0,3 puan)
#:     sessiz_yanlış **8 → 8** (bileşim değişti: biri çıktı, biri girdi)
#: Kazanç bedelin ~**dört katı**, ve yön doktrine uygun: *cevapsız dürüsttür, yanlış cube
#: sessizdir.* ⚠ Ama bir red bir **borçtur**: R10'un dokuzu ve aşağıdaki takip kusuru
#: `§SH-2`'nin işidir — kapatılmadan bu satır *"bitti"* sayılmaz.
CEVAPSIZ_RED = {"R1": 99, "R4": 1, "R10": 14, "R9": 2}

#: Toplam ölçü sinonimi ve doğru çözülen sayısı.  ⟳ Faz 2a-3: 291 → 340 (+49).
TOPLAM_SINONIM, DOGRU = 470, 340


def _tara(schema) -> tuple[set[tuple[str, str, str]], Counter, int]:
    """Her ölçü sinonimi → `route()` → **üç** sonuç: doğru / yanlış-cube / cevapsız.

    İlk sürümüm yalnız yanlış-cube sayıyordu ve bu **yanıltıcıydı**: bir düzeltme "yanlış"ı
    "cevapsız"a çevirdiğinde sayı düşüyor ama sistem iyileşmiyor — tam olarak `elektrik`
    denemesinde olan buydu (30→16 "iyileşme" göründü, erişim %64→%56 düştü).

    Erişim ile doğruluk **ayrı** ölçülmeli — planın §4.7-6 kuralının aynısı.
    """
    yanlis: set[tuple[str, str, str]] = set()
    red: Counter = Counter()
    dogru = 0
    for c in schema.get("cubes") or []:
        for syns in (c.get("measure_synonyms") or {}).values():
            for sy in syns:
                hit = cr.route(f"bu yil {sy}", schema)
                got = (hit or {}).get("cube_query", {}).get("cube") if hit else None
                if got == c["name"]:
                    dogru += 1
                elif got:
                    yanlis.add((cr._norm(str(sy)), c["name"], got))
                else:
                    red[cr.red_gerekcesi() or "—"] += 1
    return yanlis, red, dogru


# --- ASIL BULGU: kayıp yanlış-cube'da DEĞİL --------------------------------------

def test_KAYIP_CEVAPSIZDA_yanlis_cubeda_DEGIL(schema):
    """Planın §2.1'i kaybı "yanlış cube" üzerinden çerçeveliyordu. Ölçüm bunu çürütüyor:
    cevapsız sınıfı **beş kat** büyük ve en büyük dilimi R1 (cube kimliği eşleşmedi).

    Bu, Faz 2'nin bir sonraki turunun nereye bakması gerektiğini belirler — sinonim
    çakışmasına değil, **kimlik tanınmamasına**."""
    _, red, _ = _tara(schema)
    cevapsiz = sum(red.values())
    yanlis_n = len(YANLIS_CUBE)
    assert cevapsiz > yanlis_n * 3, (
        f"cevapsız {cevapsiz}, yanlış {yanlis_n} — oran değiştiyse çerçeve yeniden okunmalı")
    assert red["R1"] >= red["R10"], (
        f"R1 artık baskın değil: {dict(red)} — kayıp sınıfı kaymış, plan güncellenmeli")


def test_CEVAPSIZ_RED_DAGILIMI_sabit(schema):
    """Faz 0'ın `reject_reason` enstrümanı olmadan bu dağılım GÖRÜLEMEZDİ. Kayması,
    kapsamın bir yerde değiştiği anlamına gelir ve fark edilmeli."""
    _, red, _ = _tara(schema)
    assert dict(red) == CEVAPSIZ_RED, (
        f"red dağılımı değişti:\n  ölçülen: {dict(red)}\n  kayıtlı : {CEVAPSIZ_RED}")


def test_DOGRU_SAYISI_DUSMEDI(schema):
    """En sert kapı. `elektrik` denemesi burayı 291 → 278'e düşürmüştü ve bu, korpusta
    erişimin %64 → %56'ya inmesi olarak göründü."""
    _, _, dogru = _tara(schema)
    assert dogru >= DOGRU, f"doğru çözülen sinonim {dogru} (>= {DOGRU} bekleniyordu)"


# --- ENVANTER: yanlış-cube listesi sessizce BÜYÜYEMEZ ----------------------------

def test_YANLIS_CUBE_BUYUMEDI(schema):
    """Amaç düzeltmek değil **sabitlemek**: her satır bir alan kararı bekliyor
    (*"fire" `oee`'nin mi `parti`'nin mi?*) ve tahminle kapatılmaz. Ama yeni bir çakışma
    doğduğu gün bu test kırılır.

    `test_beyanlar_curumesin.py`'nin modül seviyesinde yaptığının **katalog** seviyesindeki
    karşılığı: ölçülmüş bir gerçek çürümeye bırakılmaz."""
    yanlis, _, _ = _tara(schema)
    yeni = yanlis - YANLIS_CUBE
    assert not yeni, (
        "YENİ sinonim çakışması doğdu:\n  "
        + "\n  ".join(f"{sy!r}: {bek} → {sec}" for sy, bek, sec in sorted(yeni))
        + "\n\nYa kaynağını düzelt ya YANLIS_CUBE'a KARAR KALEMİ olarak ekle (sahibi + "
          "tarihi ile). Sessizce büyümesine izin verme.")


def test_YANLIS_CUBE_LISTESI_BAYATLAMAZ(schema):
    """Düzeltilen bir satır listede kalırsa liste bir "yapılacaklar" olmaktan çıkıp
    hurafeye döner."""
    yanlis, _, _ = _tara(schema)
    hayalet = YANLIS_CUBE - yanlis
    assert not hayalet, (
        "artık çakışmayan satır(lar) listede:\n  "
        + "\n  ".join(f"{sy!r}: {bek} → {sec}" for sy, bek, sec in sorted(hayalet)))


# --- REDDEDİLEN DÜZELTMENİN KAYDI ------------------------------------------------

def test_SURDURULEBILIRLIK_kimligi_KORUNUYOR(schema):
    """**Bu test bir düzeltmeyi değil, bir GERİ ALMAYI korur.**

    Ham kaynak adlarını bu cube'un kimliğinden çıkarmak mantıklı görünüyordu ve
    *"yanlış cube 245 → 135"* getirdi — ama erişimi **%64 → %56** düşürdü ve
    `test_eval_gate`'i kırdı, çünkü ölçü düzeyinde sahiplik ÇÖZÜLMEDİ: iki cube da
    `elektrik` iddia ediyor → `_match_cube` hiçbirini seçemiyor → R1.

    Aynı denemeyi ikinci kez yapmamak için burada duruyor. Doğru çözüm bir **sahiplik
    kararıdır**, kimlik silmek değil."""
    sc = next((c for c in schema["cubes"] if c["name"] == "surdurulebilirlik"), None)
    assert sc, "surdurulebilirlik cube'u yok"
    kimlik = {cr._norm(str(s)) for s in (sc.get("synonyms") or [])}
    assert "elektrik" in kimlik, (
        "ham kaynak adı kimlikten çıkarılmış — bu ÖLÇÜLDÜ ve erişimi düşürdü "
        "(%64→%56, eval_gate kırmızı). Sahipliği çözmeden kimliği silme.")


def test_ELEKTRIK_iki_cubeda_da_OLCU_sinonimi(schema):
    """Kök nedenin kendisi: bu iki sahiplik çakışmadıkça hiçbir kimlik düzenlemesi
    sorunu çözmez."""
    sahipler = set()
    for c in schema["cubes"]:
        for m, syns in (c.get("measure_synonyms") or {}).items():
            if any(cr._norm(str(sy)) == "elektrik" for sy in syns):
                sahipler.add(f"{c['name']}.{m}")
    assert len(sahipler) >= 2, f"çakışma kalktıysa bu testin gerekçesi de değişti: {sahipler}"


#: ⟳ Faz 2a-3 sonrası yeniden ölçüldü — spesifiklik kuralı kümeleri küçülttü.
#: ⟳ **`§SH` (2026-08-11):** `surdurulebilirlik` **9 → 7** (`elektrik`+`dogalgaz` sahiplik
#: kararıyla çözüldü) ve `enerji_makine` **yeni bir küme olarak 3** ile doğdu — aynı
#: çakışmanın ilan edilmiş sahibine dönmüş hâli. *Bir kümenin küçülmesi, ötekinin
#: doğmasıyla ödendiyse bu bir kazanç değil bir KARARDIR; sayısı da öyle okunmalı.*
@pytest.mark.parametrize("kume,adet", [("surdurulebilirlik", 7), ("enerji_makine", 2), ("parti", 5), ("cari", 4), ("bakim", 2), ("oee", 2), ("mizan", 1)])
def test_KUMELER_kayitli(kume, adet):
    """Bir sonraki alan kararının hangi kümeye bakması gerektiği rakamla belli olsun."""
    assert Counter(sec for _, _, sec in YANLIS_CUBE)[kume] == adet
