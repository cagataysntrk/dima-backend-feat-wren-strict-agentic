"""🔴 `§B12` — ZAMAN GRANÜLERLİĞİ **TEK SAHİPLİ**. (`KAT-1`)

## Ölçülen kusur (2026-08-12) — ajan İKİ dedi, ölçüm DÖRT buldu

Bir denetim ajanı *«`intent_semasi._GRAN_ENUM` ↔ `plan_onarim.GRANULERLIKLER` iki elle
liste»* bildirdi. `grep` ile **sayınca** dört çıktı:

    app/intent_semasi.py:24   _GRAN_ENUM      ["year","quarter","month","week","day"]
    app/plan_onarim.py:59     GRANULERLIKLER  ("day","week","month","quarter","year")
    app/cube_router.py:4574   _GRAN_LADDER    ["year","quarter","month","week","day"]
    app/llm.py:364            istem metni     "year|quarter|month|week|day"

⊙ Ve ikisinin **sırası bile farklıydı** — biri üyelik için (`in`, sıra önemsiz), öteki
bir **merdiven** için (`.index(cur)+1` → daha ince granülerlik). Yani dört kopya, **iki
farklı sözleşme varsayımı**.

> *Aynı kuralın dört sahibi, dört farklı gün ayrışır.*

⚠ Ve bu, bu oturumun **⑲ numaralı dersinin** dördüncü ödemesi: *«tek/iki X var»
iddiasını **sayarak** doğrula*. Ajan iki dedi; sayım dört buldu.

## Sahip nerede — ve neden yeni bir modül DEĞİL

`app/cube_operatorleri.py` zaten *«küp sözleşmesinin kapalı kümesinin tek kaynağı»*
(`§M-6`, operatörler). Granülerlik de bir **küp sözleşmesi alanıdır**
(`timeDimensions[].granularity`), tıpkı `filters[].operator` gibi. Yeni bir modül
açmak sahipliği daha da bölerdi — `KAT-1` bunun tersini ister.

## 🔴 SIRA BİR SÖZLEŞMEDİR

Sahip **kabadan inceye** sıralıdır çünkü `cube_router._GRAN_LADDER` buna dayanır.
Üyelik için kullananlar sıradan etkilenmez — ama sahibin sırası değişirse merdiven
**sessizce** ters çalışır. Bu yüzden sıra da kilitlidir.

## `KURAL B`

Türetim öncesi/sonrası değerler **bayt bayt aynı**: enum ve ladder zaten kabadan
inceydi; `plan_onarim` ters sıradaydı ama yalnız `in` ile kullanılıyor (ölçüldü).
"""

from __future__ import annotations

import pathlib
import re

_APP = pathlib.Path(__file__).parent.parent / "app"

#: 🔴 Bugünkü sözleşme — motorun `timeDimensions.granularity` için tanıdıkları.
#: ⚠ `hour`/`minute` **YOK ve bu bir karardır** — ⟳ gerekçe **08-12'de düzeltildi**
#: (`§40.7 B12`): sebep motorun sözleşmesi **değil**, verinin o çözünürlüğü
#: **taşımaması**. *Kabul eden bir motor, olmayan bir çözünürlüğü ADLANDIRIR.*
BEKLENEN = ("year", "quarter", "month", "week", "day")


def test_SAHIP_TEK_ve_SIRASI_KABADAN_INCEYE():
    """Sahip kabadan inceye sıralı; merdiven buna dayanıyor."""
    from app.cube_operatorleri import GRANULERLIKLER

    assert GRANULERLIKLER == BEKLENEN, (
        f"🔴 granülerlik sözleşmesi değişti: {GRANULERLIKLER}. Bu küme motorun "
        "kabul ettiği değil, **verinin taşıdığı** çözünürlüklerdir (`§40.7 B12`); "
        "büyütmek için önce `day`↔`hour` kovalarının FARKLI satır saydığı ölçülmeli.")


def test_DORT_TUKETICI_de_SAHIPTEN_TURUYOR():
    """🔴 `KURAL B`: dördünün ürettiği değer **bayt bayt aynı**."""
    from app.cube_operatorleri import GRANULERLIK_ISTEM, GRANULERLIKLER
    from app.cube_router import _GRAN_LADDER
    from app.intent_semasi import _GRAN_ENUM
    from app.plan_onarim import GRANULERLIKLER as _PG

    assert _GRAN_ENUM == list(GRANULERLIKLER), "Intent şeması ayrıştı"
    assert tuple(_PG) == GRANULERLIKLER, "onarım kümesi ayrıştı"
    assert _GRAN_LADDER == list(GRANULERLIKLER), "merdiven ayrıştı"
    assert GRANULERLIK_ISTEM == "|".join(GRANULERLIKLER)
    # ⊙ Ve istem metni garsona **gerçekten** gidiyor mu — yazılıp bağlanmamış bir
    # türetim, türetilmemiş sayılır.
    from app.llm import _cube_select_system

    assert GRANULERLIK_ISTEM in _cube_select_system("KATALOG"), (
        "🔴 garson isteminde granülerlik listesi yok — türetim bağlanmamış.")


def test_BESINCI_KOPYA_SESSIZCE_DOGAMAZ():
    """🔴🔴 **SAYARAK ölç** — bu dosyanın doğuş sebebi bir SAYIM hatasıydı.

    Ajan iki kopya bildirdi, `grep` dört buldu. Bu test beşincisinin sessizce
    doğmasını engeller: `app/` altında granülerlik değerlerini **elle** sıralayan
    başka bir dizi/tuple kalmamalı.

    ⚠ Yüklem dar ve yapısal: yalnız **beşinin de ardışık** yazıldığı satırlar aranır
    (`"year"…"day"` herhangi bir sırada). Bir metin içinde `month` geçmesi bu kapıyı
    ilgilendirmez — *bir kapı, ölçtüğü şeyin biçimine değil YAPISINA bağlanır.*
    """
    kalip = re.compile(
        # ⟳ 08-12: `{` EKLENDİ ve ayırıcıya `:` girdi. Desen yalnız `[`/`(`
        # arıyordu; `cube_router._GRAN_LABEL = {"year": …, "day": …}` **sözlüğü**
        # beşini de sayıyordu ama kapının kör noktasındaydı.
        r"""[\[({]\s*(?:["'](?:year|quarter|month|week|day)["']\s*(?::[^,}\])]*)?\s*,\s*){4}"""
        r"""["'](?:year|quarter|month|week|day)["']\s*(?::[^,}\])]*)?\s*,?\s*[\])}]""")
    # 🔴🔴 **TARAMA SATIR SATIR DEĞİL, DOSYA BÜTÜNÜNDE** (⟳ 08-12).
    # İlk yazım her satırı ayrı arıyordu ve `cube_router._GRAN_LABEL` **iki satıra**
    # yayıldığı için hiçbir tek satır beşini birden taşımıyordu → kapı onu **hiç
    # göremedi**. Deseni genişletmek yetmedi; kusur **tarama biriminde**ydi.
    # *Bir çok-satırlı gerçeği satır satır aramak, onu hiç aramamaktır.*
    kacak = []
    for f in sorted(_APP.rglob("*.py")):
        if f.name == "cube_operatorleri.py":          # SAHİP — burada olması gerekir
            continue
        metin = f.read_text(encoding="utf-8")
        for m in kalip.finditer(metin):
            if any(muaf in metin[max(0, m.start() - 400):m.start()]
                   for muaf, _gerekce in MUAF_KOPYALAR):
                continue
            kacak.append(f"{f.relative_to(_APP)}:{metin[:m.start()].count(chr(10)) + 1}")
    assert not kacak, (
        "🔴 granülerlik kümesinin İKİNCİ bir elle yazılmış kopyası doğdu:\n  "
        + "\n  ".join(kacak)
        + "\n\nSahip `app/cube_operatorleri.GRANULERLIKLER`'dir; oradan türet.\n"
          "*Aynı kuralın iki sahibi, iki farklı gün ayrışır.*")


#: 🔴 **GEREKÇELİ MUAFİYET** — kümeyi değil, kümenin **ETİKETİNİ** taşıyan yapılar.
#: ⚠ Kapalı liste: her kalem tek tek okunup yargılandı, ve muafiyet **etiketin sahiple
#: birlikte büyüdüğünü** ölçen ayrı bir kapıyla dengeleniyor (aşağıda) — yani muafiyet
#: bir af değil, bir **görev devri**dir.
MUAF_KOPYALAR = (
    ("_GRAN_LABEL", "kümenin kendisi değil TÜRKÇE ETİKETLERİ (chip başlığı, BÜYÜK harfli); "
                    "sahip kümeyi, bu sözlük adı taşır"),
    ("_GRAN_ADI", "rapor bölüm başlığının küçük harfli etiketi (`app/report.py`)"),
    ("_GRAN_ETIKET", "tercih onayının küçük harfli etiketi (`app/tercih.py`)"),
)

#: 🔴🔴 **ÜÇ ETİKET SÖZLÜĞÜ VAR VE İKİSİ BİREBİR AYNI** (ölçüldü 2026-08-12).
#: `report._GRAN_ADI` ile `tercih._GRAN_ETIKET` aynı beş çifti taşıyor — gerçek bir
#: `KAT-1` ikizi. ⚠ Bugün **birleştirilmiyor**: `tercih` → `report` bağımlılığı yeni bir
#: modül kenarı açar ve ikisinin tüketicisi ayrı (rapor başlığı ↔ onay metni). Onun
#: yerine **ayrışmaları yasak**: aşağıdaki kapı ikisinin eşit kalmasını şart koşuyor.
#: *Bir kopyayı kaldıramıyorsan, en azından sessizce ayrışmasını engelle.*


def test_ETIKETLER_SAHIPLE_BIRLIKTE_BUYUR():
    """🔴 `_GRAN_LABEL` sahibin **tam** kümesini etiketlemeli — muafiyetin bedeli budur.

    Ölçüldü (08-12): erişim `_GRAN_LABEL[finer]` ile **doğrudan** yapılıyordu; sahip
    bir gün `hour` ile büyüse chip üretimi **`KeyError`** ile çökerdi. Erişim
    `.get(finer, finer)`'a çevrildi (çökme yerine teknik ad) ve bu kapı eksikliği
    **duyurur** — yastık, onarımın yerine geçmesin.
    """
    from app.cube_operatorleri import GRANULERLIKLER
    from app.cube_router import _GRAN_LABEL

    eksik = set(GRANULERLIKLER) - set(_GRAN_LABEL)
    fazla = set(_GRAN_LABEL) - set(GRANULERLIKLER)
    assert not eksik, (
        f"🔴 sahip büyüdü ama ETİKET yazılmadı: {sorted(eksik)} — kullanıcı chip'te "
        "teknik adı görür. `.get` çökmeyi önler ama bu bir onarım değil bir yastıktır.")
    assert not fazla, (
        f"🔴 etiketi olan ama sahipte OLMAYAN granülerlik: {sorted(fazla)} — *bir "
        "etiket, adlandırdığı şey kalkınca da kalırsa, olmayan bir yeteneği ADLANDIRIR.*")


def test_AYNI_ETIKETIN_IKI_SOZLUGU_AYRISMIYOR():
    """🔴 `report._GRAN_ADI` ≡ `tercih._GRAN_ETIKET` — ikisi **birebir** kalmalı.

    Ölçüldü: iki sözlük aynı beş çifti taşıyor ve **ayrı ayrı elle yazılmış**. Biri
    düzeltilip öteki unutulursa kullanıcı **aynı granülerliği** rapor başlığında bir,
    onay metninde başka türlü okur — ve hangisinin doğru olduğunu bilemez.

    ⊙ Bu kapı `§B12`'nin kendi ilkesinin etiket düzeyindeki hâli: sahip tek olamıyorsa
    **ayrışma** yasaktır.
    """
    from app.report import _GRAN_ADI
    from app.tercih import _GRAN_ETIKET

    assert _GRAN_ADI == _GRAN_ETIKET, (
        f"🔴 iki etiket sözlüğü AYRIŞTI:\n  report._GRAN_ADI    = {_GRAN_ADI}\n"
        f"  tercih._GRAN_ETIKET = {_GRAN_ETIKET}\n"
        "*Aynı kuralın iki sahibi, iki farklı gün ayrışır* — ve o gün bugündür.")


def test_MERDIVEN_SIRASI_GERCEKTEN_INCELIYOR():
    """`.index(cur)+1` bir sonraki **daha ince** granülerliği vermeli — sıra ters
    çevrilirse bu sessizce bozulur ve kullanıcı *«aylık»* isterken *«yıllık»* alır."""
    from app.cube_router import _GRAN_LADDER

    assert _GRAN_LADDER[_GRAN_LADDER.index("year") + 1] == "quarter"
    assert _GRAN_LADDER[_GRAN_LADDER.index("month") + 1] == "week"
    assert _GRAN_LADDER[-1] == "day", "en ince granülerlik `day` olmalı"


def test_HOUR_MINUTE_YOK_ve_bu_bir_KARAR():
    """⊘ Rapor `§B12` *«`hour`/`minute` açılacak»* diyordu. Açılmadı.

    ## 🔴🔴 ⟳ **GEREKÇE DÜZELTİLDİ (2026-08-12) — ESKİSİ YANLIŞTI**

    Bu test *«motorun sözleşmesi bu beşini tanıyor»* diyordu. **Ölçüldü ve çürüdü:**
    motor `hour`/`minute` için **sorunsuz SQL üretiyor** (330/334 karakter) ve sorgu
    **koşuyor**. Yani engel motorda değil.

    🔴 **Gerçek engel VERİDE ve ölçüldü:**

        granularity=day   → 782 satır · ilk kova 2024-01-01 00:00
        granularity=hour  → 782 satır · ilk kova 2024-01-01 00:00   ← BİREBİR AYNI

    `tarih` bir **DATE** kolonudur; gün altı çözünürlük **yoktur**. `hour` açılsaydı
    kullanıcı *«saatlik»* isteyip **günlük** sayı alırdı — ve etiket *«saatlik»*
    yazardı. Bu bir eksiklik değil bir **sessiz-yanlıştır**.

    > *Bir granülerliği motorun kabul etmesi, verinin onu taşıdığı anlamına gelmez;
    > kabul eden bir motor, olmayan bir çözünürlüğü ADLANDIRIR.*

    ⚠ Ve bu, bu deponun kendi dersinin (`㉔`) kendi belgesine uygulanmasıdır: yazılı
    gerekçe **ölçülmeden** kabul edilmişti.

    ## Açılış şartı — artık gözlenebilir

    `hour` ancak bir küpün zaman ekseni **TIMESTAMP** olduğunda ve `day` ile `hour`
    kovaları **farklı satır sayısı** verdiğinde açılır.
    """
    from app.cube_operatorleri import GRANULERLIKLER

    assert "hour" not in GRANULERLIKLER and "minute" not in GRANULERLIKLER, (
        "✅ `hour`/`minute` eklenmiş — VERİNİN gün altı çözünürlük taşıdığı ölçüldü mü? "
        "Şart: bir küpün zaman ekseni TIMESTAMP olmalı ve `day` ile `hour` kovaları "
        "FARKLI satır sayısı vermeli (bugün ikisi de 782).")