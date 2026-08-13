"""🔴 `G0b.9b` — **ALAN HARİTASI**: garson ile mutfak karışmaz.

## Neden bu kapı

Garson ara fazı iki katmanı birbirine yaklaştırıyor. Karıştırılan her sınır, bu deponun
adını koyduğu kusuru doğurur: **aynı kuralın iki sahibi**. Ayrım testi üç soru:

    ① DOĞAL DİL okuyor/yazıyor mu?           → GARSON
    ② VERİ / SORGU / MOTOR ile mi çalışıyor?  → MUTFAK
    ③ İKİSİ DE mi? → 🔴 KAPI olmak ZORUNDA.
                       Kapı olmayan bir "ikisi de" tanımı gereği bir KUSURDUR.

## ⚠ Bu kapı bir «kimse dokunmasın» kapısı DEĞİL

Sınıflandırma **listelidir ve gerekçelidir**; yeni bir modül eklenince listeye
yazılması gerekir. `test_modul_buyume.py`'nin muafiyet-listesi deseni: *sınıfsız modül
bırakılamaz* — çünkü sınıfsız bir modül, sınırı **düşünülmemiş** bir moduldür.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

APP = pathlib.Path(__file__).resolve().parents[1] / "app"

#: 🗣 GARSON — dil okur/yazar, **hiçbir şey çalıştırmaz**.
GARSON = {
    "niyet.py", "turetme.py", "typo_onerisi.py", "followup.py", "context.py",
    "donem_capasi.py", "netlestirme.py", "belirsizlik_chipi.py", "soz.py",
    "intent_semasi.py", "kapsam.py", "embed_kapsam.py", "yetenek.py",
    # 🔴 `FAZ O-2` — PLAN ŞEMASI. `intent_semasi.py` ile **aynı sınıf ve aynı sebep**:
    # ikisi de garsonun **ne söyleyebileceğini** sınırlayan bir sözleşme üretir. Katalogdan
    # enum türetir, LLM'in çıktısını daraltır, hiçbir sayı hesaplamaz, hiçbir sorgu koşmaz.
    # ⚠ `SORGU` fiilinin gövdesi `intent_semasi`'den **çağrılır** (kopyalanmaz) — yani bu
    # modül onun **üstünde** durur, yanında değil. *Bir sözleşmeyi genişletmek, onu ikinci
    # kez yazmak değildir.*
    "plan_semasi.py",
    # 🔴 `FAZ O-4` — PLAN GARSONU. Tanım gereği garson: soruyu alır, sağlayıcıya verir,
    # dönen METNİ okur. Motora hiç dokunmaz — bir adımı bile koşmaz, koşmayı
    # `plan_kosucu`'ya bırakır. ⚠ Ve sınıf sınırı burada bir **tasarım kanıtıdır**:
    # planlayıcı ile garson AYNI KİŞİ olduğu için planlayıcı da garson tarafında doğar.
    "plan_garson.py",
    "temellendirme.py",   # G1 — CubeQuery → "anladığım şu" (0 LLM, motora dokunmaz)
    "diyalog.py",         # G2 — slot durumu; saf fonksiyon, LLM YOK, motora dokunmaz
    "ek.py",              # G7 — Türkçe ek ÜRETİMİ (doğrulama değil); saf, LLM YOK
    "sinonim_onerici.py", "archetypes.py", "starters.py",
    # `§34` — üstünlük **yapısını** okur (`en` + sıfat) ve bir `cq` parçası üretir.
    # Hiçbir şey çalıştırmaz, motora dokunmaz: tanım gereği garson.
    "siralama.py",
    # `§54` — dilbilgisi işlev sözcükleri; dil okur, hiçbir şey çalıştırmaz.
    # ⚠ Ve `§56`'nın **görünür borcudur**: garson aday ürettiğinde Türkçe kapsam reddi
    # hiç koşmayacak ve bu dosya **silinecek**. Sınıfı garson tarafındadır çünkü yaptığı
    # tek şey bir cümlenin dilbilgisini tanımaktır.
    "islev_sozcukleri.py",
    # `§40` — ikizi; soruda tanınan niyet parçasını `cq`'ya yerleştirir. Aynı sınıf,
    # aynı kapsam: dil okur, hiçbir şey çalıştırmaz.
    "niyet_tasima.py",
    # 🔴 `§DK-2/§NT/§ÇE/§DK-5` — **SÜZGEÇ DEĞERİ ÇAPASI.** Sınırda duruyor ve sınıfı
    # bilerek garson: girdisi bir `cube_query` **ve kullanıcının cümlesi**, çıktısı bir
    # **beyan cümlesi** ya da bir netleştirme sorusudur. Katalog enum'unu **okur**
    # (şema, veri değil) ve hiçbir sorgu koşmaz — motora hiç dokunmaz. *Bir modülü
    # sınıflandıran şey neye baktığı değil, ne ürettiğidir.*
    "deger_capasi.py",
    # `§DK-3` — yukarıdakinin eşleştirme yarısı: kullanıcının yazdığı metni kataloğun
    # görünen etiketlerine bağlar. Saf dizgi işi, LLM yok, motor yok.
    "deger_eslesme.py",
    # 🔴 `§KV` — **VARLIK SORUSU.** Sınıfı `deger_capasi` ile **birebir aynı gerekçeyle**
    # garson: girdisi kullanıcının cümlesi **ve** bir `cube_query`, çıktısı düzeltilmiş
    # bir fiş **ve bir beyan cümlesi**. Hiçbir sorgu koşmaz, motora hiç dokunmaz.
    # ⚠ Ve iş bölümü doktrinin kendisi: *«kaç makinemiz var»*ın boyutunu **garson**
    # bulur (`dimensions: [makine]`), bu modül yalnız fişin **şeklini** düzeltir —
    # ölçüyü ve varsayılan dönemi düşürür. `cube_router`'ın büyüme tavanı onu buraya
    # çıkarttı; `simge.py` de öyle doğmuştu.
    "sayim.py",
    # `§SB` — teknik simge yazım sınıfı (`dE`·`kWh`·`pH`). Dil okur, hiçbir şey
    # çalıştırmaz; `cube_router`'ın büyüme tavanı onu buraya çıkarttı.
    "simge.py",
    # `C1/C3` — ters yön: bilinmeyen bir terimi kataloğun bir hedefine eşler. Dil okur,
    # bir `cq` parçası üretir; hiçbir şey çalıştırmaz.
    "ters_yon.py",
}

#: 🍳 MUTFAK — veri/sorgu ile çalışır, **dil bilmez**.
MUTFAK = {
    "wren_service.py", "compose.py", "contracts.py", "rls.py", "fanout.py",
    "katman_b.py", "stats.py", "contribution.py", "yoy.py", "kpi.py",
    # G6 — `yoy.py`'nin İKİZİ: filtre listesi üstünde saf cebir (çökmüş iki-dönem
    # aralığını `mom`/`yoy` bazına geri açar). Dil okumaz, motora dokunmaz; girdisi
    # bir CubeQuery parçası, çıktısı bir CubeQuery parçası — tanım gereği mutfak.
    "kiyas_cebiri.py",
    # 🔴 `§KN` — **KÖK-NEDEN CEBİRİ.** `contribution.py` ile aynı sınıf ve aynı sebep:
    # girdisi katalog + zaten hesaplanmış sayılar, çıktısı bir **ayrıştırma**. Dil
    # okumaz, soru ayrıştırmaz, sorgu koşmaz — saf cebir. ⚠ Ürettiği **cümle** onu
    # garson yapmaz: cümle bir sunum değil, ayrıştırmanın okunabilir hâlidir (aynı şeyi
    # `contribution` ve `drill` de yapar). *Bir modülü sınıflandıran şey neye baktığı
    # değil, ne ürettiğidir.*
    "kok_neden.py",
    # 🔴 `ÖNGÖRÜ KATMANI` (2026-08-13) — üçü de **MUTFAK**: hiçbiri LLM
    # çağırmaz, üçü de deterministiktir ve `E-8` gereği sıcak yola seri bir
    # ikinci tur **eklemez**.
    #   · `emin_miyim.py`  — *«emin miyim»* eşik aritmetiği (dört çağıranın tek sahibi)
    #   · `oneri.py`       — katalogdan yazarken-ara (leksik ⊕ vektör, RRF); yetki
    #                        süzmesi **sıralamadan önce**, sorgu **koşmaz**
    #   · `hasat.py`       — tıklama sinyali (konum yanlılığı) ve not biçimi; saf
    "emin_miyim.py", "oneri.py", "hasat.py",
    "statements.py", "drill.py", "audit_zinciri.py", "lineage.py", "tazelik.py",
    "veri_araligi.py", "result_shape.py", "sensitivity.py",
    # `M-6` — MOTORUN OPERATÖR ADLARI. Dil değil, **motorun kendi sözlüğü**: küme
    # motorun hata mesajından birebir alındı (*"expected one of `eq`, `neq`, …"*) ve on
    # üç aday tek tek `/cube`'a gönderilerek ölçüldü. Bir cümle okumaz, bir sayı
    # hesaplamaz; yalnız *"motor bu adı tanır mı"* sorusuna cevap verir — tanım gereği
    # mutfak. ⚠ Bir 🗣 modülü (`intent_semasi`) onu **import eder**; bu ters yön kapının
    # yasakladığı yön DEĞİLDİR (yasak: mutfak → dil).
    "cube_operatorleri.py",
    # 🔴 `FAZ O-1` — ORKESTRATÖRÜN İLKELLERİ (`BAGLA` · `HESAPLA`). Tanım gereği mutfak:
    # girdisi **koşmuş satırlar**, çıktısı **sayı**. Bir cümle okumaz, bir katalog
    # ayrıştırmaz, bir LLM çağırmaz, bir SQL yazmaz — yalnız *"bu satırlar içinde hangisi
    # ve akranlarından ne kadar farklı"* sorusuna cevap verir.
    # ⚠ `contribution.py`'nin (aynı sınıf) elle yazılmış gövdesinden **çıkarıldılar** ve
    # davranış denkliği canlıda doğrulandı — yani bu bir sınır geçişi değil, aynı sınıf
    # içinde bir **saflaştırma**. *Bir gövdeyi ilkelleştirmek, onun sınırını değiştirmez.*
    "ilkeller.py",
    # 🔴 `FAZ O-2` — PLAN ÇALIŞTIRICISI. Tanım gereği mutfak: koşmuş satırlar üzerinde
    # adımları sırayla koşar, referansları çözer, ilkelleri çağırır. Bir cümle okumaz,
    # bir LLM çağırmaz, bir SQL YAZMAZ — sorguyu bile kendisi koşmaz, `sorgu_kos`
    # **parametre olarak** verilir (bu yüzden `wren_service`'i hiç tanımaz).
    # ⚠ `plan_semasi.py` 🗣 tarafta (garsonun **ne söyleyebileceği**), bu 🍳 tarafta
    # (söylenenin **nasıl koşacağı**). Aynı fazın iki ucu, iki ayrı sınıf — ve bu
    # ayrım kapının yasakladığı yönü (mutfak → dil) hiç kurmuyor.
    "plan_kosucu.py",
    # 🔴 `FAZ O-4` — PLAN TÜKETİCİSİ. Planı motora bağlar (`cube_sql` → `dry_plan` →
    # `query`) ve çıktısını **kullanıcı metnine** çevirir. ⚠ Metin ÜRETİYOR ama dil
    # OKUMUYOR — kapının yasakladığı yön budur (mutfak → dil ayrıştırma). Ürettiği
    # cümleler kendi çıktısının rakamlarından kuruluyor; hiçbir soru cümlesi okunmuyor.
    "plan_tuketici.py",
    # 🔴 `FAZ O-15` — PLAN ONARICISI. **Mutfak, ve sınıfı bir tasarım kanıtıdır:**
    # kullanıcının cümlesini hiç görmez. Girdisi bir `cube_query` ile bir **küp
    # tanımıdır**; kararı *"bu ad bu küpte hangi alana ait"* sorusunun cevabıdır ve o
    # cevap katalogda **yazılıdır**. Sıfır LLM, sıfır dil, sıfır tahmin.
    #
    # ⚠ Bu ayrım kapının yasakladığı yönü kurmadığını **yapısal olarak** gösterir:
    # `onar(cq, spec)` imzasında bir soru cümlesi için yer yoktur. Modül dile
    # bakmak isteseydi, imzasını değiştirmesi gerekirdi — ve o değişiklik burada
    # görünürdü. *Bir sınırı en iyi koruyan şey, onu ihlal etmek için imza
    # değiştirmeyi zorunlu kılmaktır.*
    "plan_onarim.py",
}

#: 🍳 modüllerin ASLA import edemeyeceği 🗣 modüller — *"mutfak dil ayrıştıramaz"*.
DIL_MODULLERI = {"llm", "soz", "followup", "niyet", "turetme", "typo_onerisi",
                 "belirsizlik_chipi", "netlestirme", "intent_semasi"}

#: 🗣 modüllerin ASLA import edemeyeceği motor yüzeyleri — *"garson çalıştıramaz"*.
MOTOR_MODULLERI = {"wren_service", "katman_b", "compose"}

#: ⚠ GEREKÇELİ MUAFİYETLER — kapı bunları GÖRÜR ve geçirir; **gizlemez**.
#:
#: Bir muafiyet bir çözüm değildir; **görünür bırakılmış bir borçtur**. Listeye giren
#: her satır ya bir sonraki fazda kapanır ya kalıcı gerekçesini yanında taşır.
MUAF_GECISLER = {
    # 🔴 Ölçüldü (G0b, 2026-08-07): `wren_service.py:552,825` → `from app.llm import _norm`.
    # `_norm` bir METİN NORMALLEŞTİRİCİDİR, bir dil anlama yüzeyi değil — ama evi
    # `llm.py` olduğu için mutfak dil modülüne uzanmış görünüyor. Gerçek çözüm `_norm`'u
    # ortak bir yardımcıya taşımak; o **bu fazın konusu değil**. Kapı görüyor, biz
    # adlandırıyoruz: *sınır kokusu var ve kayıtlı.*
    ("wren_service.py", "llm"),
    # 🔴 **İKİNCİ KEZ — ve bu, kokuyu bir BORCA çeviriyor** (2026-08-13).
    # `oneri.py:63` → `from app.llm import _norm`. Gerekçe yukarıdakiyle
    # **aynı**: `_norm` küçük harfe indirip boşluk kırpar; bir dil anlama
    # yüzeyi **değildir** ve öneri motoru LLM'i hiç çağırmaz (`E-8` korunuyor,
    # `test_alan_haritasi` ve `routers/ask.py` taraması ayrıca doğruluyor).
    #
    # ⚠ Ama artık **iki** mutfak modülü aynı kapıdan geçiyor ve bir emsal
    # ikiye çıkınca **kural** olmaya başlar 🆍. Doğru çözüm belli: `_norm`
    # `llm.py`'den **ortak bir yardımcıya** taşınmalı (`KAT-1` korunur, ithal
    # yönü düzelir). ⊘ Bu turda yapılmadı çünkü `_norm`'u `llm`'den alan **beş**
    # modül var (ölçüldü) ve taşıma tek başına bir demet kapısı ister 🅗.
    #
    # ⚠㊱ Bu satır ilk yazılışında *«on yedi yerden»* diyordu — **ölçülmemiş bir
    # sayıydı**. Ölçüldü: **5**. *Gerekçeye konan her sayı da bir iddiadır.*
    ("oneri.py", "llm"),
}


def _importlar(dosya: pathlib.Path) -> set[str]:
    agac = ast.parse(dosya.read_text(encoding="utf-8"))
    out: set[str] = set()
    for d in ast.walk(agac):
        if isinstance(d, ast.Import):
            out |= {a.name.split(".")[-1] for a in d.names}
        elif isinstance(d, ast.ImportFrom) and d.module:
            parca = d.module.split(".")
            if parca[0] == "app" and len(parca) > 1:
                out.add(parca[1])
            out.add(parca[-1])
    return out


@pytest.mark.parametrize("ad", sorted(GARSON))
def test_GARSON_motora_dokunamaz(ad):
    """🗣 Garson **sorgu çalıştırmaz**. `route()` bile motora dokunmaz — o yüzden
    garsonun kulağıdır, aşçının tezgâhı değil."""
    yol = APP / ad
    if not yol.exists():
        pytest.skip(f"{ad} henüz yok")
    ihlal = _importlar(yol) & MOTOR_MODULLERI
    assert not ihlal, f"🔴 GARSON modülü {ad} motora dokunuyor: {sorted(ihlal)}"


@pytest.mark.parametrize("ad", sorted(MUTFAK))
def test_MUTFAK_dil_ayristiramaz(ad):
    """🍳 Mutfak **doğal dil bilmez**. Bir mutfak modülü `soz`/`followup` import
    ediyorsa, ya yanlış sınıflandırılmıştır ya bir sınır sızmıştır."""
    yol = APP / ad
    if not yol.exists():
        pytest.skip(f"{ad} henüz yok")
    ihlal = {m for m in _importlar(yol) & DIL_MODULLERI
             if (ad, m) not in MUAF_GECISLER}
    assert not ihlal, f"🔴 MUTFAK modülü {ad} dil modülü import ediyor: {sorted(ihlal)}"


def test_SINIFSIZ_MODUL_BIRAKILAMAZ():
    """🔴 Yeni bir modül eklenip haritaya yazılmazsa **CI kırmızı**.

    Sınıfsız bir modül, sınırı **düşünülmemiş** bir modüldür. Muafiyet listesi
    gerekçelidir: her satır ya bir sınıfa girer ya **neden girmediğini** söyler.
    """
    #: Sınıflandırma DIŞI — gerekçeleriyle. (🚪 kapı · 🌉 köprü · altyapı · teslim)
    MUAF = {
        # 🚪 KAPI — ikisinin arasında durur, ikisine de ait değildir
        "llm_guard.py": "🚪 çıkış kapısı — `safe_call`, fail-closed",
        "yayilim.py": "🚪 korunan yayılım — perdeleme/geri koyma (G0b)",
        "narration_guard.py": "🚪 metin→SAYI kapısı",
        # 📊 TELEMETRİ — kapıların KENDİSİNİ ölçer, hiçbir karara girmez.
        # `Ö5`: guard'lar fail-closed düştüğünde sistem "soğur" ama HİÇBİR ŞEY hata
        # vermez; bu modül o sessizliği bir sayıya çevirir. Ne dil okur ne sorgu kurar —
        # yalnız iki kapının çıktısını sayar. *Ölçen bir modül, ölçtüğü tarafa ait
        # değildir; aksi hâlde kendi sonucunu etkiler.*
        "guard_alarmi.py": "📊 telemetri — guard düşme oranı (Ö5), karara girmez",
        # 📊 `A1` — **ÖLÇÜM ALTYAPISI.** Sağlayıcının TAŞIMA metodunu sarar ve
        # cevaplarını kasete alır. Ne dil okur ne sorgu kurar; yalnız bir teli dinler.
        # `guard_alarmi` ile aynı sınıf ve aynı gerekçe: *ölçen bir modül, ölçtüğü
        # tarafa ait değildir.*
        "kaset.py": "📊 ölçüm altyapısı — sağlayıcı taşımasını kasete alır (A1)",
        "iddia.py": "🚪 metin→İDDİA kapısı (G4) — §4'ün değişmezinin ikinci yarısı",
        "uyum.py": "🚪 niyet↔sorgu uyum kapısı (beyan-açık)",
        "pii.py": "🚪 maskeleme, tek çıkış",
        "planner.py": "🚪 dört kapı (kayıt·yetki·det-önce·bütçe)",
        # 🚪 `§33` — **duvar-saati bütçesi.** Ne dil okur ne sorgu kurar; yalnız bir
        # beklemeyi keser. `planner.py`'nin bütçesi ADIM/SORGU sayar, bu SANİYE sayar —
        # ikisi farklı büyüklüklerdir ve tek modülde toplanmaları onları karıştırırdı.
        # *Ölçüsü farklı olan iki sınır, aynı sahibin altında birbirini gizler.*
        "butce.py": "🚪 duvar-saati bütçesi — beklemeyi keser, işi öldürmez (§33)",
        "tools.py": "🚪 araç kaydı",
        "cube_router.py": "🚪+🗣 route() garson · parse_cube_query KAPI — bilinçli, §1.2c",
        "answer.py": "🚪 KAPANIŞ ZİNCİRİ — her cevap `seal()`'den geçer",
        "llm.py": "🗣 sağlayıcı katmanı — garsonun ağzı ve kulağı; ama `safe_call`'ı da "
                  "barındırdığı için KAPI'ya da dokunur (tek çıkış geçidi orada sarılı)",
        # 🌉 KÖPRÜ — biri üretir, öteki tüketir
        "interpret.py": "🌉 mutfak üretir, garson tüketir (ham satır SIZDIRMAZ)",
        "value_index.py": "🌉 veri değeri okur, garson kullanır",
        # 🔴 `G0b.6` — `value_index`'in KARDEŞİ ve aynı sınıf: veri değerlerini okur
        # (`sensitivity` süzgeciyle) ama onları **garson için** perdeler. Sayı hesaplamaz,
        # SQL yazmaz, katalog dışına çıkmaz — köprünün tanımı budur.
        "varlik.py": "🌉 veri değeri okur, garson için PERDELER",
        # 🔴 LLM'in gördüğü METİN — `intent_semasi`'nin kardeşi (o şemayı, bu düz metni
        # üretir). Yönlendirme kararı vermez, katalog dışına çıkmaz: sunum katmanı.
        "katalog_metni.py": "🌉 katalogdan LLM'in okuduğu metni üretir",
        # 🗣 GARSON: cümle yazar, sayı hesaplamaz, ham satır görmez. `interpret()`'in
        # (mutfak) ürettiği olguları **anlatır** — köprünün öteki ucundaki tüketici.
        "anlatici.py": "🗣 olguları Türkçe cümleye çevirir (0 LLM)",
        "vqr.py": "🌉 soru→sorgu belleği",
        # 🎨 SUNUM
        "viz.py": "🎨", "report.py": "🎨", "prescribe.py": "🎨", "fmt.py": "🎨",
        "viz_email.py": "🎨", "email_render.py": "🎨", "gorsel_ekleme.py": "🎨",
        "result_shape.py": "🎨",
        # 🎨 `§SB-metin` — bir sayının **Türkçesi**. Dil OKUMAZ (garson değil), sorgu
        # KOŞMAZ (mutfak değil): sayıyı okunabilir hâle getirir. `fmt.py`'nin kardeşi.
        # ⊙ Ayrı bir dosya çünkü `§KN` ile `contribution` **kendi kopyalarını** yazmıştı
        # ve ayrıştılar (ölçüldü, `DD` turu: *«47,836 dk … %83.4'i»* — üç ayrı hata).
        "sayi_bicimi.py": "🎨",
        # 🎨 `§D3` — **cevabın BİÇİMİ bir karardır** (ADR-0024'ün kardeşi). Soru
        # türünden öneri-kovası kotası üretir; veri okumaz, sorgu kurmaz, dil
        # anlamaz — yalnız *"bu cevap nasıl görünmeli"* sorusunu cevaplar. Kararı
        # `answer.py` tüketir, `cube_router.suggest_next_steps` uygular.
        "bicim.py": "🎨",
    }
    hepsi = {p.name for p in APP.glob("*.py")} - {"__init__.py"}
    sinifli = GARSON | MUTFAK | set(MUAF)
    # Altyapı/teslim/yetki katmanı: bu fazın konusu değil, ayrı sahipleri var.
    ALTYAPI_ONEKLERI = (
        "main", "config", "logging_setup", "features", "schemas", "channels",
        "bildirim", "paylasim", "kanal_", "schedules", "eylem", "onay_", "yazma_",
        "eskalasyon", "decision", "hedef", "kpi_pin", "arkaplan_", "istek_",
        "ask_jobs", "mcp", "ossie", "cekirdek", "tercih", "bayrak_", "mali_",
        "rules", "discovery_kuyrugu", "terfi_", "kademeli_", "materialize",
        "db_introspect", "mdl_writer", "packs", "company_registry", "coldstart",
        "dataset", "adhoc_cube", "metrik_kaydi", "certification", "sertifika_",
        "sinonim", "kpi_", "starters", "kapsam", "embed_",
    )
    kalan = {a for a in hepsi - sinifli if not a.startswith(ALTYAPI_ONEKLERI)}
    assert not kalan, (
        f"🔴 SINIFSIZ MODÜL: {sorted(kalan)}\n"
        "Her modül ya 🗣 GARSON, ya 🍳 MUTFAK, ya MUAF (kapı/köprü/sunum) olmalı.\n"
        "Sınıfsız bir modül, sınırı DÜŞÜNÜLMEMİŞ bir modüldür — yol haritası §1.2c.")


def test_YAYILIM_llm_guardin_KOPYASI_DEGIL():
    """🔴 `G0b`'nin kendi dersi: perdeleme `llm_guard`'a yazılmıştı ve
    `test_DESEN_SOZLUGU_KOPYALANMAMIS` **haklı olarak** kırmızı verdi.

    İki ayrı soru, iki ayrı sahip: *"bu yük çıkabilir mi"* ≠ *"ne perdelenecek"*.
    """
    guard = (APP / "llm_guard.py").read_text(encoding="utf-8")
    assert "re.compile" not in guard, "llm_guard'a yine regex sızmış"
    assert "def perdele" not in guard, "perdeleme llm_guard'a geri taşınmış"
    yayilim = (APP / "yayilim.py").read_text(encoding="utf-8")
    assert "def perdele" in yayilim and "def geri_koy" in yayilim
