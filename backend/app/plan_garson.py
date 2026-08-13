"""PLAN GARSONU — garson, **yalnız boşlukta** plan çevirir (FAZ O-4).

## Kullanıcının sorusu, ve ölçümün verdiği cevap

> *"Planlayıcı ile LLM intent — yani garson — aynı kişi olabilir; çünkü LLM'e iki istek
> yerine tek cevapta bunu halledebiliriz."*

Kişi aynı, **an** aynı değil. İlk tasarım bu fikri *"plan `select_cube`'un YERİNE geçer"*
diye okudu (raporun `E6` düzeltmesi). `EE` turunun A/B'si o okumayı **çürüttü**:

| ölçü | A · bayrak kapalı | B · bayrak açık |
|---|---|---|
| 🗣 `cube+llm` (garson) | **%35** | %25 |
| 🥡 Discovery / adhoc | %10 | **%25** |
| 🔴 **arıza oranı** | **%55** | 🔴 **%65** *(+10 puan)* |

⊙ **Mekanizma:** `_select_consistent` `k` örneği **aynı** süreçten çeker ve oylar. Plan
araya girince örneklerin bir kısmı plandan, bir kısmı `select_cube` yedeğinden geliyordu
— yani oy artık **aynı dağılımdan** çekilmiyordu. Bir oylamanın geçerliliği örneklerin
özdeşliğine dayanır; iki farklı süreci aynı sandığa atmak, oylamayı gürültüye çevirir.

🔴 Somut kayıp (`EE6` *«geçen hafta hiç iş kazası oldu mu»*): A'da `isg`/`{kaza_adedi: 0}`,
B'de cevapsız. Ve `EE14` *«ciromuz büyüdü mü»* B'de **İK'ya** düştü.

## ⟳ DÜZELTME — `E3`'ün LAFZINA dönüldü

Plan artık `select_cube` ile **yarışmıyor**. Yalnız **boşlukta** çağrılıyor: route boş,
garsonun tek-cube cevabı da yok — yani bugünkü sonuç Discovery ya da dürüst ret.

* cevaplanan hiçbir soruya **bir çağrı bile** eklenmez → `E6` riski **sıfır**
* cevaplanan hiçbir soru **bozulamaz** → `E3` yapısal olarak sağlanır
* oylama **hiç görmez** → self-consistency bugünküyle birebir

*Bir yeteneği doğru yere koymak, onu doğru yazmaktan önce gelir; yanlış yerde duran
doğru bir kod, yanlış bir koddur.*

⚠ `KURAL B`: bayrak kapalıyken `acik_mi()` `False` döner ve bu modülün hiçbir satırı
koşmaz. Kapalı davranış bayt bayt bugünkü.

## ⚠ Raporun `E6` düzeltmesi neden ölçümle geri alındı — kayıt için

Rapor *"planlayıcı garsonun kendisi, ayrı çağrı değil; riskin yarısı tasarımla iner"*
diyordu. Fikir doğru ama **yeri** yanlıştı: kazanç (çağrı sayısı) küçük, bedel (oylamanın
bozulması) büyüktü. Boşlukta çağırmak ikisini birden veriyor — çünkü boşlukta zaten bir
oylama yok.
"""

from __future__ import annotations

import json
import logging
from typing import Any

_log = logging.getLogger("dima.plan_garson")

#: Bayrak adı. ⚠ Tek yerde yazılı: `acik_mi()` dışında kimse bu dizeyi okumaz.
BAYRAK = "orkestrator_plan"

#: 🔴 **`O-12` — PLAN TELEMETRİSİ.** Bu katmanda **tek bir sayaç yoktu**: bayrak
#: açıldığında *«kaç plan denendi, kaçı reddedildi, hangi sebeple, kaç adımlıydı»*
#: sorusunun cevabı yoktu ve `EE` turunun A/B'si bunu **konteyner logundan elle**
#: çıkarmak zorunda kaldı.
#:
#: ⚠ `payda kutsaldır` kuralının bu katmandaki karşılığı: `denendi` payda, geri kalanı
#: paydır. Biri olmadan öteki okunamaz. *Sayamadığın şeyi geliştiremezsin; ve
#: sayamadığın bir şeyin iyileştiğini iddia etmek, ölçmemenin en pahalı hâlidir.*
#:
#: ⊙ Süreç ömürlü ve **kilitsiz**: bu sayaçlar bir karar vermez, bir ölçüm verir. Bir
#: yarışta bir sayının kaybolması, kilit maliyetinden ucuzdur.
SAYAC: dict[str, int] = {
    "denendi": 0,          # `plan_kur` çağrıldı
    "gecerli": 0,          # ilk denemede şema-geçerli
    "onarildi": 0,         # tek düzeltme turu kurtardı
    "dustu": 0,            # ikisinde de olmadı
    "tek_adimli": 0,       # 🔴 `R2`'nin ölçüsü: basit soru basit kaldı mı
    "cok_adimli": 0,
    "adim_toplami": 0,     # ortalama adım = adim_toplami / (tek+cok)
    "yedege_dondu": 0,     # `O-18/Y` — ad reddi sonrası yapısal plana dönüldü
}

#: 🔴🔴 `A9` — **RED ORANI BİR İZLENİM DEĞİL, BİR SAYI OLMALI.**
#:
#: ⊙ Ölçüldü (rapor `§B-9`): `SAYAC` **vardı**, `sayaclar()` **vardı** — ve **hiçbir
#: tüketicisi yoktu**. Red oranı loglara gözle bakılarak tespit ediliyordu; sebep
#: dağılımı olmadan hangi düzeltmenin kaç redde dokunduğu **bilinemez**.
#:
#: ⚠ Sınıflar **kendi mesajlarımızdan** türer — kapalı bir küme, çünkü o mesajları
#: biz yazıyoruz (`_plani_oku` · `dogrula` · `plan_onarim.gerekce`). Bir dış metni
#: sınıflandırmıyoruz; **kendi sözleşmemizi** sayıyoruz.
#:
#: *Sebebi sayılmayan bir red, düzeltildiğinde de sayılamaz.*
RED_SINIFLARI: tuple[tuple[str, str], ...] = (
    ("json",           "geçerli bir JSON değil"),
    ("kok_nesne",      "kök bir nesne olmalı"),
    ("adimlar",        "`adimlar` boş"),
    ("bilinmeyen_fiil", "tanımlı bir fiil değil"),
    ("eksik_alan",     "zorunlu alan(lar) eksik"),
    ("fazla_alan",     "tanımsız alan(lar)"),
    ("tip",            "üretiyor"),
    ("ulasilmaz",      "hiçbir adım tarafından kullanılmıyor"),
    ("tavan",          "tavan"),
    ("ileri_referans", "ileri referans"),
    ("butce",          "bütçe"),
    ("operator",       "süzgeç operatörü"),
    ("ad_yok",         "diye bir cube YOK"),
    ("olcu_yok",       "ölçü(ler) yok"),
    ("boyut_yok",      "boyut(lar) yok"),
    ("suzgec_alani",   "`dimension` alanı hiç yazılmamış"),
    # 🔴 `R1` — çözülmemiş adım referansı. Canlıda **0 satır + 5 adımlık makbuz**
    # üretiyordu; sınıfı olmadan bir daha görünmezdi.
    # *Sayılmayan bir red, olmayan bir red gibi davranır.*
    ("cozulmemis_referans", "çözülmemiş referans"),
)

#: Sebep sayacı — `RED_SINIFLARI`'nın anahtarlarıyla + `bilinmeyen`.
RED_NEDENLERI: dict[str, int] = {}

#: 🔴 `§B4` — ONARIM TAVANI. Snowflake **Error Correction** ajanı, Wren `retry&repair`,
#: Genie öz-düzeltme ve Anthropic'in **evaluator-optimizer** deseni aynı şeyi söylüyor;
#: Magentic-One'ın **stall sayacı ≤2**'si de tavanı buraya koyuyor. ⊙ Ve raporun kendi
#: uyarısı: *«bu ajanlık değil WORKFLOW»* — döngü serbest değil, **sayılı**.
ONARIM_TAVANI = 2

#: 🔴 `§B4` — SINIF → **ÇARE**. Red mesajı kusuru *söyler*; bu tablo **ne yapılacağını**
#: söyler.
#:
#: ## Neden gerekli — ölçüldü (2026-08-11, canlı `/stats/plan`)
#:
#:     denendi=16 · geçerli=12 · onarildi=1 · dustu=3
#:     red_orani_yuzde=25 · 🔴 onarim_tutma_yuzde=25
#:     red_nedenleri = {"ulasilmaz": 4}
#:
#: Onarım turu **vardı ve ateşliyordu** — ama **4'te 1** tutuyordu. Ve dört reddin
#: **dördü de aynı sınıftı**. Yani sorun modelin anlamaması değil, **ne yapacağının
#: söylenmemesiydi**: istem yalnız *«sözleşmeye UYARAK yeniden planla»* diyordu.
#:
#: ⚠ Yeni bir sözlük değil: anahtarlar `RED_SINIFLARI`'nın **kendi kapalı kümesinden**
#: gelir (`KAT-1` — sınıfların tek sahibi orası). Bir sınıfın çaresi yoksa satır
#: yazılmaz; istem yine yalnız kusuru taşır.
ONARIM_YONERGESI: dict[str, str] = {
    "ulasilmaz": ("Kullanılmayan adımı ya SİL ya da sonraki bir adımın alanında `$n` "
                  "ile REFERANS ver. Her adım ya bir sonrakinin girdisi olmalı ya da "
                  "planın son adımı."),
    "cozulmemis_referans": ("Bir adım referansı bir alanın TAMAMI olmalıdır "
                            '(`"cube_query": "$1"`); süzgeç değerinin içine yazılamaz. '
                            "Önceki adımın seçtiği varlığı süzgeç yapmak için `BAGLA` "
                            "çıktısını sonraki adımın `hedef` alanında kullan."),
    "ileri_referans": "Bir adım yalnız KENDİNDEN ÖNCEKİ adımlara referans verebilir.",
    "bilinmeyen_fiil": "Yalnız sözleşmede tanımlı fiilleri kullan; yeni fiil İCAT ETME.",
    "eksik_alan": "Eksik zorunlu alanları doldur; alan adlarını sözleşmeden birebir al.",
    "fazla_alan": "Sözleşmede olmayan alanları KALDIR.",
    "ad_yok": "Yalnız katalogda YAZILI cube adlarını kullan.",
    "olcu_yok": "Yalnız o cube'un ölçü listesindeki adları kullan.",
    "boyut_yok": "Yalnız o cube'un boyut listesindeki adları kullan.",
    "tavan": "Planı KISALT — adım sayısı tavanı aşıyor.",
    "json": "Yanıtın TAMAMI tek bir geçerli JSON nesnesi olsun; açıklama metni ekleme.",
}


def red_sinifi(mesaj: str) -> str:
    """Bir red mesajını **kapalı** bir sınıfa indirger (`A9`).

    ⚠ İlk eşleşen sınıf kazanır ve sıra **bilinçli**: yapısal redler (`json`, `fiil`)
    alan redlerinden önce gelir, çünkü bir plan hiç okunamadıysa alanları da yoktur.
    """
    m = str(mesaj or "")
    for ad, iz in RED_SINIFLARI:
        if iz in m:
            return ad
    return "bilinmeyen"


def _onarim_dongusu_acik() -> bool:
    """`§B4` — ikinci onarım turu açık mı. Kapalıysa tavan **1** (`KURAL B`).

    ⚠ İmza **argümansızdır** ve bu bilinçli: `plan_uret` bir `principal` taşımıyor ve
    ona bir parametre eklemek iki çağıranı da değiştirirdi. `metin_ve_indeks`'in dersi
    burada da geçerli — *bir yardımcının imzası, çağıranların **en dar** kapsamına göre
    çizilir*. Bayrak kiracı düzeyinde daraltılmak istenirse `principal` o gün eklenir;
    bugün küresel/sektör düzeyi yeterlidir ve yanlış bir bağımlılık üretmez.
    """
    try:
        from app.config import get_settings
        from app.features import resolve_for

        return "onarim_dongusu" in resolve_for(get_settings(), None)
    except Exception:                    # noqa: BLE001 — bayrak çözülemezse bugünkü yol
        _log.warning("§B4: onarım bayrağı çözülemedi → tavan 1", exc_info=True)
        return False


def _redi_say(mesajlar) -> None:
    """Bir redde geçen **her** sınıfı sayar (tek mesajda iki kusur olabilir)."""
    for m in (mesajlar or []):
        RED_NEDENLERI[red_sinifi(m)] = RED_NEDENLERI.get(red_sinifi(m), 0) + 1


def sayaclar() -> dict[str, int]:
    """Ölçüm okuyucusu — **kopyasını** verir. Doğrudan sözlüğü vermek, okuyanın
    yazabilmesi demekti."""
    # 🔴🔴 **ANAHTAR UZAYI KAPALI TUTULUR** ㊶ (2026-08-13, tam kapı ölçümü).
    #
    # ⊙ Ölçülen kusur: `:343` onarım turunu **dinamik anahtarla** sayıyor
    # (`SAYAC[f"onarildi_tur{_tur}"]`). `out = dict(SAYAC)` onu **üst düzeye**
    # taşıyınca yayımlanan sözleşme **çalışma zamanında büyüyordu**: izole koşumda
    # o yol hiç çalışmadığı için kapı yeşil, tam süitte bir test onarım tetikleyince
    # `onarildi_tur1` beliriyor ve `test_a13` *«ilan edilmemiş alan»* diye kırmızı
    # veriyordu 🅢. Kapı **haklıydı**: *sessizce büyüyen bir sözleşme, denetlenemeyen
    # bir sözleşmedir.*
    #
    # ⊙ Çözüm deponun **kendi deseni**: kırılımlar üst düzeye serilmez, **iç içe**
    # yayımlanır — tıpkı `red_nedenleri` gibi ㊲. Böylece hiçbir bilgi kaybolmaz,
    # üst düzey alan kümesi **sabit** kalır ve `test_a13` onu **tam** sayabilir.
    out = {k: v for k, v in SAYAC.items() if not k.startswith("onarildi_tur")}
    out["onarildi_turlere_gore"] = {                     # type: ignore[assignment]
        k.removeprefix("onarildi_tur"): v
        for k, v in SAYAC.items() if k.startswith("onarildi_tur")
    }
    # 🔴 `A9` — sebep dağılımı **aynı okuyucudan** çıkar: iki ayrı okuyucu, bir gün
    # yalnız birinin okunması demekti.
    out["red_nedenleri"] = dict(RED_NEDENLERI)          # type: ignore[assignment]
    _d, _o, _du = SAYAC["denendi"], SAYAC["onarildi"], SAYAC["dustu"]
    out["red_orani_yuzde"] = round(100 * (_o + _du) / _d) if _d else 0
    out["onarim_tutma_yuzde"] = round(100 * _o / (_o + _du)) if (_o + _du) else 0
    return out


def baglamli(soru: str, onceki: dict | None,
             bolumler: list[dict] | None = None) -> str:
    """Takip turunda soruya **önceki sorguyu** iliştirir (`O-22`) — **TEK SAHİP**.

    🔴 İki çağıranı var ve ikisi de aynı cümleyi kurmalı: `PlanGarsonu.select_cube`
    (oylama yolu) ve `plan_tuketici.cevap` (boşluk yolu). ⊙ Ve bu ders **ölçülerek**
    alındı: ilk yazımda yalnız birincisi bağlandı, canlıda hiçbir şey değişmedi —
    çünkü o turda planı **ikincisi** üretiyordu. *Bir yolu düzeltip ötekini unutmak,
    düzeltmeyi yapmamakla aynı sonucu verir; yalnız yapıldığını sanmakla farklıdır.*

    ⚠ Soru **değiştirilmez**, üstüne bir bağlam satırı eklenir: kullanıcının cümlesini
    yeniden yazmak onu yorumlamaktır ve yorum garsonun işidir.
    ⚠ Önceki sorgu yoksa dize **bayt bayt aynı** döner (`KURAL B` disiplini).
    """
    # 🔴🔴 `§RD` — **BİR BELGEYİ DÜZENLEMEK, TEK BİR FİŞİ DÜZENLEMEK DEĞİLDİR.**
    #
    # ⊙ Ölçüldü (curl, 2026-08-10): *«rapora kârlılık da ekle»* → `source=cube`, **tek
    # satır**, `rapor` **yok**. Kullanıcı bir **belgeyi** düzenlemek istedi; sistem onu
    # sıradan bir sorgu sandı — çünkü bağlam olarak yalnız **son fiş** iliştiriliyordu ve
    # bir raporun son fişi, raporun kendisi değildir.
    #
    # ⊙ Kullanıcının şartı açıktı: *«sonra düzenleme isteyebilir»*. Bir belge, üstüne
    # konuşulabilen bir şeydir; konuşulamıyorsa bir çıktıdır, bir **canvas** değil.
    #
    # ⚠ **SATIR GÖNDERİLMEZ.** Bölümler yalnız **kimlikleriyle** anlatılır (küp · ölçü ·
    # kırılım): planlayıcının belgeyi yeniden kurmak için verilere ihtiyacı yok, ve
    # gerçek değerleri sağlayıcıya yollamak `G0b`'nin (korunan yayılım) kapattığı
    # kapıyı yeniden açardı. *Bir planı kurmak için sonuçları bilmek gerekmez.*
    #
    # ⚠ Tek sahip korunuyor: iki çağıran da (`PlanGarsonu` · `plan_tuketici`) bu
    # fonksiyondan geçer. Bu dersin bedeli **ölçülerek** ödendi (üstteki şerh).
    if isinstance(bolumler, list) and bolumler:
        _satir = []
        for i, b in enumerate(bolumler, 1):
            cq = (b or {}).get("cube_query") or {}
            if not cq.get("cube"):
                continue
            _satir.append("  %d. küp=%s · ölçü=%s%s" % (
                i, cq.get("cube"), ",".join(cq.get("measures") or []) or "-",
                (" · kırılım=" + ",".join(cq.get("dimensions") or []))
                if cq.get("dimensions") else ""))
        if _satir:
            # 🔴 **CÜMLE İKİ KİPİ DE ANLATMALI — ve bunu bir ölçüm öğretti.**
            # İlk yazım yalnız *«VAR OLAN bölümleri AYNEN yeniden üret»* diyordu ve
            # canlıda ölçüldü: *«rapora kârlılık ekle»* ✅ çalıştı, *«rapordan müşteri
            # kırılımını ÇIKAR»* 🔴 çalışmadı — istenen bölüm yine üretildi. Talimat
            # kendisiyle çelişiyordu: *«hepsini koru»* ile *«birini çıkar»* aynı cümlede
            # yarışıyordu ve koruma kazanıyordu.
            # *Bir talimat yalnız bir kipi anlatıyorsa, ötekini yasaklıyor demektir.*
            return (soru + "\n\n⊙ ÖNCEKİ BELGENİN BÖLÜMLERİ (kullanıcı bu **belgeyi** "
                    "düzenliyor):\n" + "\n".join(_satir)
                    + "\n\nKURAL: kullanıcı bir bölümün ÇIKARILMASINI istiyorsa onu "
                    "ÜRETME; ötekileri aynen yeniden üret. Bir EKLEME istiyorsa hepsini "
                    "koru ve yenisini ekle. Son adım yine RAPOR/PANO olsun.")
    if not (isinstance(onceki, dict) and onceki.get("cube")):
        return soru
    return (soru + "\n\n⊙ ÖNCEKİ CEVABIN SORGUSU (kullanıcı bunun ÜSTÜNE konuşuyor — "
            "dönemi, kırılımı ve sıralamayı KORU, yalnız istenen değişikliği uygula):\n"
            + json.dumps(onceki, ensure_ascii=False))


def plan_uret(llm: Any, question: str, catalog: str, index: dict,
              *, azami_adim: int = 5) -> dict | None:
    """Garsona **plan** sorar. `None` = kullanılabilir bir plan çıkmadı.

    🔴 Bu fonksiyon **yalnız boşlukta** çağrılır — route boş, garsonun tek-cube cevabı
    da yok. Yani cevaplanan hiçbir soruya bir çağrı eklemez ve cevaplanan hiçbir soruyu
    **bozamaz**. `E3`'ün lafzı buydu ve ölçüm onu haklı çıkardı (yukarıdaki A/B).
    """
    try:
        _sema = None
        if getattr(llm, "sema_kullanir", False):
            from app.plan_semasi import plan_json_schema
            _sema = plan_json_schema(index, azami_adim=azami_adim)
        SAYAC["denendi"] += 1
        _neden: list[str] = []
        _ham = llm.plan_kur(question, catalog, _sema)
        plan = _plani_oku(_ham, neden=_neden, index=index)
        # 🔴🔴 `O-18/Y` — **AD REDDİ YUMUŞAKTIR: onarım turunu tetikler, planı ATMAZ.**
        #
        # Ad denetimi (`dogrula(index=…)`) yapısal redden **farklı** bir sınıftır:
        # yapısal red edilmiş bir plan **koşulamaz** (ileri referans, tip uyuşmazlığı,
        # ulaşılamaz adım); ad reddi edilmiş bir plan **koşabilir** — yalnız bir adımda
        # dürüstçe durur ve kullanıcı *"hangi adımda ne eksikti"* öğrenir. O da bir
        # üründür (`O-4`'ün ikinci başarı ölçütü).
        #
        # ⚠ Bu ayrım olmasaydı `O-18` bir kazanç değil bir **takas** olurdu: onarım
        # turunu kazanıp adım-adım dürüstlüğü kaybederdik — ve onarım tutmazsa soru
        # Discovery'ye düşerdi. `KAT-2`: *cevapsız bir dal, cevaplı bir yolu kesemez.*
        #
        # *Bir reddi sertleştirmeden önce, reddedilenin ne kadarının yine de bir cevap
        # olduğunu sormak gerekir.*
        _yedek = _plani_oku(_ham) if plan is None and index else None
        if plan is None:
            # 🔴 **ONARIM DÖNGÜSÜ — SAYILI (`ONARIM_TAVANI`), serbest DEĞİL.**
            #
            # Red bugüne kadar **sessizdi**: hangi adımda hangi alanın eksik olduğu o
            # anda **biliniyordu** ve atılıyordu. Buraya yalnız **boşlukta** gelinir
            # (bugünkü cevap zaten yok), yani bir turun davranışsal maliyeti sıfır.
            #
            # ⟳ `§B4` — **İKİNCİ TUR AÇILDI, ve bir ölçüme dayanıyor.** Yukarıdaki
            # *«ikincisi YOK»* kararı bir ilkeydi ve ilke doğruydu (*«üç kez söylemek
            # yalvarmaktır»*) — ama **tavanı bir** yapması ölçülmemişti. `/stats/plan`:
            #
            #     denendi=16 · onarildi=1 · dustu=3 → 🔴 onarim_tutma_yuzde=**25**
            #     red_nedenleri = {"ulasilmaz": 4}   ← dördü de AYNI sınıf
            #
            # Yani tek tur **4'te 1** tutuyordu ve reddin tamamı tek bir sınıftı.
            # İki değişiklik: tavan **2** (`ONARIM_TAVANI`, Magentic-One stall ≤2) ve
            # red mesajının yanına **ÇARE** (`ONARIM_YONERGESI`) — istem eskiden yalnız
            # *«sözleşmeye UYARAK yeniden planla»* diyordu, yani kusuru söyleyip
            # çözümü söylemiyordu.
            #
            # ⚠ Tavan bir **sayıdır**, bir sezgi değil: `KURAL B` gereği bayrak
            # kapalıyken tavan **1**'dir ve davranış bugünküyle birebir kalır.
            _redi_say(_neden)          # `A9` — sebep dağılımı
            _tavan = ONARIM_TAVANI if _onarim_dongusu_acik() else 1
            for _tur in range(1, _tavan + 1):
                _siniflar = sorted({red_sinifi(m) for m in _neden})
                _log.info("plan REDDEDİLDİ [%s] (%s) → onarım turu %d/%d",
                          ",".join(_siniflar) or "-",
                          "; ".join(_neden) or "sebep yok", _tur, _tavan)
                _care = [ONARIM_YONERGESI[s] for s in _siniflar if s in ONARIM_YONERGESI]
                _duzelt = (question + "\n\n🔴 ÖNCEKİ DENEMEN REDDEDİLDİ: "
                           + "; ".join(_neden)
                           + ("\n\n🟢 NASIL DÜZELTİLİR:\n- " + "\n- ".join(_care)
                              if _care else "")
                           + "\nAynı soruyu, bu kez sözleşmeye UYARAK yeniden planla.")
                _neden = []
                plan = _plani_oku(llm.plan_kur(_duzelt, catalog, _sema),
                                  neden=_neden, index=index)
                if plan is not None:
                    SAYAC[f"onarildi_tur{_tur}"] = SAYAC.get(f"onarildi_tur{_tur}", 0) + 1
                    break
                if not _neden:
                    break              # sebep okunamadıysa ikinci tur körlemesine olur
            if plan is None and _yedek is not None:
                SAYAC["yedege_dondu"] = SAYAC.get("yedege_dondu", 0) + 1
                _log.info("plan: onarım tutmadı → YAPISAL olarak geçerli ilk plana "
                          "dönüldü (adım adım dürüst ret üretilecek)")
                plan = _yedek
            elif plan is None:
                SAYAC["dustu"] += 1
                _log.info("plan: düzeltme turundan sonra da kullanılabilir plan yok")
                return None
            else:
                SAYAC["onarildi"] += 1
                _log.info("plan: DÜZELTME TURU işe yaradı")
        else:
            SAYAC["gecerli"] += 1
        _n = len(plan["adimlar"])
        SAYAC["adim_toplami"] += _n
        SAYAC["tek_adimli" if _n == 1 else "cok_adimli"] += 1
        _log.info("plan: %d adım (%s)", _n,
                  "·".join(a.get("fiil", "?") for a in plan["adimlar"]))
        return plan
    except Exception:
        _log.warning("plan üretimi düştü → bugünkü yol", exc_info=True)
        return None


def _plani_oku(ham: str, *, neden: list[str] | None = None,
               index: dict | None = None) -> dict | None:
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
    def _de(m: str) -> None:
        if neden is not None:
            neden.append(m)

    try:
        veri = json.loads(ham or "null")
    except Exception:
        _de("çıktı geçerli bir JSON değil")
        return None
    if not isinstance(veri, dict):
        _de("kök bir nesne olmalı")
        return None
    adimlar = veri.get("adimlar")
    if not isinstance(adimlar, list) or not adimlar:
        _de("`adimlar` boş ya da bir dizi değil")
        return None
    from app.plan_semasi import FIILLER, ISTEGE_BAGLI_ALANLAR, ZORUNLU_ALANLAR
    for i, a in enumerate(adimlar, 1):
        if not isinstance(a, dict) or a.get("fiil") not in FIILLER:
            _de(f"adım {i}: `{(a or {}).get('fiil') if isinstance(a, dict) else a}` "
                "tanımlı bir fiil değil")
            return None
        _zorunlu = ZORUNLU_ALANLAR[a["fiil"]]
        # 🔴 **ADI DOĞRU, SÖZLEŞMESİ YANLIŞ.** Ölçüldü (`EE`, canlı): serbest-JSON
        # sağlayıcı fiili doğru yazıp parametrelerini **uyduruyor** —
        # `{"fiil":"SORGU"}` (`cube_query` YOK) · `{"fiil":"AYRISTIR","ozellik":…}`.
        # Yalnız fiil adına bakan doğrulama bunları plan sanıyor, çalıştırıcı
        # `KeyError` ile düşüyordu. *Bir sözleşmenin adını doğrulamak, sözleşmeyi
        # doğrulamak değildir.*
        _eksik = [k for k in _zorunlu if k not in a]
        if _eksik:
            _de(f"adım {i} (`{a['fiil']}`): şu zorunlu alan(lar) eksik: "
                + ", ".join(_eksik))
            return None
        # ⚠ İsteğe bağlı alanlar **aynı** sözlükten okunuyor; ayrı bir liste tutmak
        # şemanın izin verdiği bir planı doğrulayıcının reddetmesi demekti.
        _serbest = {"fiil", *_zorunlu, *ISTEGE_BAGLI_ALANLAR.get(a["fiil"], ())}
        _fazla = sorted(set(a) - _serbest)
        if _fazla:
            _de(f"adım {i} (`{a['fiil']}`): tanımsız alan(lar): " + ", ".join(_fazla)
                + f" — yalnız şunlar yazılabilir: {', '.join(sorted(_serbest - {'fiil'}))}")
            return None

    # 🔴🔴 **YAPISAL DOĞRULAMA DA BURADA — ve bu bir birleştirme, bir ekleme değil.**
    #
    # `dogrula()` (ileri referans · tip · `ANLAT` konumu · bütçe · **ulaşılamaz adım**)
    # koşum anında çalışıyordu. Sonuç: model bu hataları **hiç öğrenemiyordu**, çünkü
    # onarım turu yalnız alan hatalarını görüyordu.
    #
    # Ölçüldü (canlı, `FF4` — *«en çok fire veren makineyi bul sonra o makinede hangi
    # vardiyada olduğunu göster»*): model en kötü makineyi `BAGLA` ile **buldu** ama
    # sonra **kullanmadı** — üçüncü adımda vardiyaya *global* sorgu attı. `dogrula()`
    # bunu doğru reddetti (*«koşulup atılırdı»*) ama red **öğretici olmadı**.
    #
    # ⊙ Tek kapı, tek onarım turu: iki doğrulayıcının aynı yerde durması, modele
    # *"neyi düzelteceğini"* tek seferde söyler. *Bir hatayı geç söylemek, onu hiç
    # söylememenin pahalı hâlidir.*
    _plan = {"adimlar": adimlar}
    try:
        from app.plan_kosucu import dogrula
        # ⚠ `index` geçilmezse ad denetimi hiç koşmaz — `O-18`'in kill-switch'i budur.
        dogrula(_plan, index=index)
    except Exception as e:            # noqa: BLE001 — `PlanHatasi` dâhil her yapısal red
        _de(str(e))
        return None
    return _plan


class PlanGarsonu:
    """🔴🔴 **`O-14` — GARSON = ORKESTRATÖR.** Bugünkü `select_cube` sözleşmesini konuşur,
    altında **plan** üretir.

    ## Neden bir basamak DEĞİL, bir çıktı biçimi

        bugünkü tasarım : route → garson → [orkestratör]   ← 3 yollu karar, YENİ sınırlar
        KARAR           : route → garson(= orkestratör)     ← 2 yollu, sınır AYNI
                                    └ çıktı 1 adım ya da N adım

    ⊙ Değişen şey *hangi yola gidilir* değil, **garsonun çıktısının şekli**. route↔garson
    ayrımı — ~100 testin koruduğu sınır — **dokunulmadan** kalır. *Bir yeteneği bir basamak
    olarak eklemek karar yüzeyini büyütür; bir çıktı biçimi olarak eklemek büyütmez.*

    🔴 **Ve LLM çağrı sayısı DEĞİŞMEZ** — ölçülmüş bir gerçek, bir umut değil: garson zaten
    yalnız `route_hit is None` dalında çağrılıyor (`ask.py:3579`). Göç *ne zaman* çağrıldığını
    değil *ne döndürdüğünü* değiştiriyor. `E6`'nın (gecikme çarpılır) riski azaltılmıyor,
    **yapısal olarak sıfırlanıyor**.

    ## ⟳ `B` koşumunun `-10` puanı bu tasarımı çürütmüyor — YARIM hâlini çürüttü

    `_select_consistent` `k` örneği **tek** kaynaktan çeker ve oylar. `B`'de plan araya
    girince örneklerin bir kısmı plandan, bir kısmı `select_cube` **yedeğinden** geliyordu:
    iki farklı dağılım aynı sandıkta. *Bir oylamanın geçerliliği örneklerin özdeşliğine
    dayanır.*

    🔴 Bu yüzden burada **`select_cube` yedeği YOKTUR**: model çok adımlı dediyse çok
    adımlıdır ve plan **koşulur** — ikinci bir görüş sorulmaz. Karışımı kaldıran şey budur.
    ⚠ Yedek yalnız **arıza** hâlinde var (`except`): bir genişleme, genişlettiği şeyi bozamaz.

    ## Çok adımlı plan bir oy DÜŞÜŞÜ değil, bir CEVAPTIR

    `B`'de çok adımlı plan cevabı yok ediyordu çünkü fiillerin dördü **ölüydü** (`O-10`) ve
    sözleşme modele **öğretilmemişti** (`O-11`). İkisi kapandı; artık plan **koşabiliyor** ve
    `plan_tuketici` onu bir cevaba çeviriyor. Plan `request.state`'e bırakılır — çağıranın
    yereline değil, çünkü bu kancaya **yukarıdaki her yoldan** gelinir (`EE19`'un dersi).
    """

    def __init__(self, ic: Any, index: dict, istek: Any = None,
                 varliklar: dict | None = None, onceki: dict | None = None,
                 bolumler: list[dict] | None = None) -> None:
        self._ic, self._index, self._istek = ic, index or {}, istek
        #: 🔴🔴 `O-22` — **GARSON TAKİP BAĞLAMINI HİÇ GÖRMÜYORDU.**
        #:
        #: ⊙ Ölçüldü (canlı `VII/B4`): thread'in dördüncü turunda `followup=True
        #: (yapısal=True)` — sistem takip olduğunu **biliyordu** — ama garsona yalnız
        #: *«bir de gecikme ekle»* gitti ve cevap bağlamsız bir toplam oldu: dönem yok,
        #: `musteri` kırılımı yok, ilk-3 yok. Üç turda kurulan bağlam **sessizce**
        #: düştü.
        #:
        #: ⚠ Deterministik takip yolu (`deterministic_refine`) bağlamı **taşıyor**;
        #: garson yolu taşımıyordu. Yani aynı thread, hangi basamağa düştüğüne göre
        #: bağlamlı ya da bağlamsız cevap veriyordu — kullanıcının göremeyeceği bir
        #: ayrım. *Bir bağlamı bir yolda taşıyıp ötekinde bırakmak, onu rastgele
        #: taşımaktır.*
        self._onceki = onceki if isinstance(onceki, dict) and onceki.get("cube") else None
        # 🔴🔴 `§RD` — **İKİNCİ ÇAĞIRAN.** `baglamli`'nin kendi şerhi bu hatayı zaten
        # kaydetmişti: *«ilk yazımda yalnız birincisi bağlandı, canlıda hiçbir şey
        # değişmedi — çünkü o turda planı İKİNCİSİ üretiyordu»*. Ve aynı hata bu turda
        # **tekrarlandı**: `plan_tuketici` bağlandı, burası unutuldu ve canlıda ölçüldü —
        # *«rapora aylık trend de ekle»* → önceki bölümler kayboldu, plan `oee` küpüne
        # gitti. Sebep: bu sınıfın sakladığı `plan_taslagi`, `plan_tuketici`'nin
        # ürettiği plandan **önce** gelir.
        # *Bir yolu düzeltip ötekini unutmak, düzeltmeyi yapmamakla aynı sonucu verir;
        # yalnız yapıldığını sanmakla farklıdır.*
        self._bolumler = bolumler if isinstance(bolumler, list) and bolumler else None
        #: ⚠ Bağlam **istek durumuna** da yazılır: planı bu nesne değil, boşlukta
        #: `plan_tuketici` üretiyor olabilir ve o `body`'yi görmez. Tek kaynak, iki
        #: okuyucu.
        _s0 = getattr(istek, "state", None)
        if _s0 is not None and self._onceki is not None:
            _s0.plan_onceki = self._onceki
        #: 🔴 `G0b.6` — VARLIK PERDESİ. Sorudaki katalog **değerleri** `{{ENT_i}}`'ye
        #: çevrilip modele öyle gidiyor; `ask.py` dönen `CubeQuery`'ye `varlik.geri_koy`
        #: uyguluyor. Ama **plana uygulamıyordu**: ölçüldü (canlı `FF10`),
        #: `SUZ.deger = "{{ENT_1}}"` olarak kaldı ve süzgeç hiçbir şeyle eşleşmedi.
        #: *Bir perdeyi kaldırmayı bir yolda unutmak, o yolu perdenin arkasında
        #: bırakmaktır.*
        self._varliklar = varliklar or {}

    def __getattr__(self, ad: str) -> Any:      # pragma: no cover - saydamlık
        return getattr(self._ic, ad)

    def _baglamli(self, question: str) -> str:
        """`baglamli`'nin nesne yüzü — mantık modül düzeyinde, **tek sahipli**."""
        return baglamli(question, self._onceki, self._bolumler)

    def select_cube(self, question: str, catalog: str, sema: dict | None = None) -> str:
        try:
            plan = plan_uret(self._ic, self._baglamli(question), catalog, self._index)
            if plan is None:
                return self._ic.select_cube(question, catalog, sema)
            from app.plan_semasi import tek_adimli
            cq = tek_adimli(plan)
            # 🔴🔴 `O-21` — **ŞEKİL SAYIMI: «tek fiş yeter mi?» sorusu OYLANABİLİR.**
            #
            # ⊙ Ölçüldü (canlı `VI`, log damgalarıyla — *«iade oranı en yüksek 3 müşteri
            # **ve** ciro payları»*):
            #
            #     22:33:14  plan: 1 adım (SORGU)                  ← bir örnek «tek fiş»
            #     22:33:15  plan: 3 adım (SORGU·SORGU·MATRIS)     ← öteki «orkestre»
            #     22:33:23  orkestratör: route zaten cevapladı → hiç konuşmuyorum
            #
            # Çok adımlı örnek `"{}"` döndürüyor; beyaz liste onu `None` yapıyor ve oy
            # **çekimser** sayılıyor. Yani bir *«basit okuma»* örneği, iki *«orkestre
            # gerekli»* örneğini **görünmez** kılarak eziyor — `§V2`'nin *"en yalın
            # okuma kazanır"* eğriliğinin bir seviye yukarısı.
            #
            # 🔴 Çok adımlı planın **içeriği** oylanamaz (`R1`: kanonik biçimi yok) —
            # ama **şekli** oylanabilir: *"tek fiş yeter mi?"* ikili bir sorudur ve
            # kanonik biçimi kendisidir. Sayaç burada tutulur çünkü örnekleri **yalnız
            # bu nesne** görür.
            #
            # *Bir kararı oylanamaz ilan etmek, onu tek bir örneğe bırakmaktır.*
            _st = getattr(self._istek, "state", None) if self._istek is not None else None
            if _st is not None:
                _sekil = getattr(_st, "plan_sekil", None) or {"tek": 0, "cok": 0}
                _sekil["tek" if cq is not None else "cok"] += 1
                _st.plan_sekil = _sekil
                if cq is not None:
                    _st.plan_tek_cq = cq
            if cq is not None:
                return json.dumps(cq, ensure_ascii=False)
            # ⚠ Çok adımlı: oy düşer (kanonik bir `CubeQuery` yok — `R1`) ve karar
            # `plan_kosucu.dogrula()`'ya geçer: tip·DAG·bütçe denetimi oylamadan **sert**.
            # ⚠ Plan **istek durumuna** bırakılır: `_select_consistent` `k` kez örnekler
            # ve her örnek kendi planını üretir; sonuncusu kalır. Bir oylama yapmıyoruz
            # çünkü çok adımlı planın kanonik biçimi yok (`R1`) — karar `dogrula()`'nın.
            if self._varliklar:
                from app import varlik
                _acik = varlik.geri_koy(plan, self._varliklar)
                if _acik is None:
                    # ⚠ `geri_koy` **fail-closed**: çözülemeyen bir yuva varsa `None`
                    # döner. Yarım geri konmuş bir süzgeç `{{ENT_1}}` arar, hiç satır
                    # dönmez ve cevap *"veri yok"* olur — kullanıcı bunu bir **bulgu**
                    # sanar. O yüzden plan **düşer**, yarım koşmaz.
                    _log.info("plan: varlık perdesi kaldırılamadı → plan düştü")
                    return self._ic.select_cube(question, catalog, sema)
                plan = _acik
            _var = getattr(self._istek, "state", None) if self._istek is not None else None
            if _var is not None:
                _var.plan_taslagi = plan
                _log.info("plan: %d adım SAKLANDI (çok adımlı → tüketici koşacak)",
                          len(plan["adimlar"]))
            else:
                _log.warning("plan üretildi ama SAKLANAMADI (istek yok) — tüketici "
                             "onu yeniden üretmek zorunda kalacak")
            return "{}"
        except Exception:
            _log.warning("plan garsonu düştü → bugünkü select_cube", exc_info=True)
            return self._ic.select_cube(question, catalog, sema)


def sarmala(llm: Any, index: dict, istek: Any = None,
            varliklar: dict | None = None, onceki: dict | None = None,
            onceki_rapor: Any = None) -> Any:
    """🔴 `KURAL B`'nin tek satırı: kapalıyken **nesnenin kendisi** döner.

    ⚠ `settings`/`principal` **istekten türetilir**, çağırandan alınmaz — ve bu yalnız
    kısalık değil: ikisi de `request`in zaten taşıdığı şeyler (`ask.py:140`'ın kendi
    kalıbı). Çağırandan istemek, aynı gerçeği iki yerden okumaktı. *Bir bağlamı taşıyan
    nesne elindeyken, o bağlamın parçalarını ayrıca istemek onları ayrışmaya davet
    etmektir.*
    """
    from app.config import get_settings

    _p = getattr(getattr(istek, "state", None), "principal", None)
    # `§RD` — çağıran **ham belgeyi** verir, bölümlemeyi burası yapar. Gerekçe bu
    # fonksiyonun kendi ilkesidir (`settings`/`principal` ile aynı): *bir bağlamı taşıyan
    # nesne elindeyken, o bağlamın parçalarını ayrıca istemek onları ayrışmaya davet
    # etmektir.* Ve **tek sahip**: bölüm okuma mantığı `plan_tuketici._belge_bolumleri`de.
    from app.plan_tuketici import _belge_bolumleri
    return (PlanGarsonu(llm, index, istek, varliklar, onceki,
                        _belge_bolumleri(onceki_rapor))
            if acik_mi(get_settings(), _p, llm) else llm)


def acik_mi(settings: Any, principal: Any = None, llm: Any = None) -> bool:
    """🔴 `KURAL B`'nin tek satırı: bayrak kapalıysa **hiçbir şey olmaz**.

    ⊙ Bayrak çözümü çağıranda değil burada: `ask()`in gövdesi bir tavan kapısına bağlı
    ve bir bayrak adı ikinci bir yerde tekrarlanmasın diye (`KAT-1`).
    """
    try:
        from app.features import resolve_for
        if BAYRAK not in resolve_for(settings, principal):
            return False
        if llm is not None and not getattr(llm, "plan_kurabilir", False):
            _log.info("plan bayrağı açık ama sağlayıcı plan kuramıyor → bugünkü yol")
            return False
        return True
    except Exception:
        _log.warning("plan bayrağı çözülemedi → kapalı sayıldı", exc_info=True)
        return False
