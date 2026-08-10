"""**Intent-JSON ŞEMA SÖZLEŞMESİ** — `CubeQuery`'nin şema-kısıtlı biçimi.
[bayrak: `sema_kisitli` — karar `cube_router`'da kalır]

## Neden `cube_router`'dan ÇIKTI

`cube_router.py` modül tavanını **8 satır** aşmıştı (1749 / 1741). Kapının kuralı açık:
*"yeni eşleştirme kuralı bir **modüle** çıkar; tavanı yükseltme. Tavanı yükseltmek kapıyı
kapının kendisiyle çürütür."*

Ve taşınacak şey **rastgele seçilmedi**: bu fonksiyon bir **yönlendirme kararı vermez**,
bir **veri sözleşmesi tarif eder** — kataloğun o anki hâlini bir JSON Schema'ya çevirir.
`cube_router` *"hangi cube, hangi ölçü"* sorusunun sahibidir; *"bir Intent-JSON nasıl
görünür"* sorusunun sahibi değildir. **Sınır kavramsaldı, dosya onu geç yakaladı.**

⚠ **Şemanın ÜRETİLMESİ buraya taşındı, KULLANILMASI değil**: bayrak kontrolü ve reddetme
yolu (`parse_cube_query`) `cube_router`'da kaldı. *Bir kararı taşımak, onu bölmekten
farklıdır.*
"""

from __future__ import annotations

from app import cube_operatorleri as _ops  # `M-6` — operatör kümesinin TEK sahibi

_GRAN_ENUM = ["year", "quarter", "month", "week", "day"]


#: 🔴🔴 `§AR` — **ALAN REHBERİ: TEK SAHİP, İKİ TÜKETİCİ.**
#:
#: `pencere` ve `turev` alanlarının **ne anlama geldiği** bugüne kadar yalnız
#: `llm.py`'nin Intent isteminde yazılıydı. Plan istemi (`plan_semasi`) aynı `cube_query`
#: şemasını kullanıyor ama bu açıklamayı **hiç görmüyordu**.
#:
#: ⊙ Ölçüldü (canlı `XII`): *«toplam ciromun **yüzde kaçı** ilk 3 müşteriden geliyor»*
#: → plan `SORGU×2 + ANLAT` kurdu ve *«Sayı doğru ama eksik»* beyan etti. Oysa cevap
#: **ifade edilebilir**: `pencere:{taban:toplam_ciro, kip:pay}`. Intent yolu bunu
#: biliyor, plan yolu bilmiyordu.
#:
#: ⚠ Ve bu ders bu dosyada **zaten yazılı**: `llm.py`'nin kendi yorumu diyor ki
#: *«bir kuralı yanlış isteme yazmak, hiç yazmamaktır»* (`M-9`/`M-3`, kümülatif vakası).
#: Aynı hata bir seviye yukarıda tekrarlanmış: kural **doğru** isteme yazılmış ama
#: **ikinci** istem doğduğunda taşınmamış.
#:
#: 🔴 Metin **bayt bayt** korunur: `llm.py` bu sabiti aynı yere koyar, yani Intent
#: istemi değişmez (`KURAL B`). *Bir metni paylaşmak, onu değiştirmek değildir.*
ALAN_REHBERI = (
        '- PENCERE: "pencere":{"taban":"<ölçü>","kip":"kumulatif|hareketli_ort|sira|'
    'onceki|degisim_yuzde|pay"}. «kümülatif/birikimli»→kumulatif; «hareketli N aylık '
    'ortalama»→hareketli_ort + "pencere_boyu":N; «her X için en yüksek»→sira + '
    '"bolum":["<boyut>"]; «önceki döneme göre yüzde değişim»→degisim_yuzde; '
    # 🔴 `§V6` — `sira` AÇGÖZLÜYDÜ ve kural İKİ istemde birden yazılı (`KAT-1`).
    # Ölçüldü (`V13`/`D3`, canlı): *«duruş süresini AZALAN SIRADA İLK 5»* → garson
    # `pencere:sira` yazdı, `order`+`limit` yazmadı → **11 satır**, hepsi sıra
    # numaralı ama sıralanmamış ve kesilmemiş. ⊙ İkisi farklı şeydir: `sira` bir
    # **sütun** üretir (ROW_NUMBER), `order`+`limit` **sonucu** belirler. Kuraldaki
    # *«her X için»* bir sınırdı ama istemde bir **örnek** gibi duruyordu.
    # *Bir örnek, kural sanılırsa genişler.*
    '🔴 `sira` YALNIZ GRUP-İÇİ sıralamadır ve `"bolum"` ŞARTTIR («her makine için '
    'en yüksek vardiya»). Düz bir «en yüksek/ilk N» isteğinde `sira` DEĞİL '
    '`order`+`limit` yaz. '
    '«toplam içindeki payı / yüzde kaçı» → **pay** (turev DEĞİL). '
    "kumulatif/hareketli_ort/degisim_yuzde bir ZAMAN KOVASI ister (timeDimensions).\n"
    '- TÜREV (oran/pay): "turev":{"pay":"<ölçü>","payda":"<ölçü>","kip":"yuzde|oran|'
    'fark"} ve İKİ ölçüyü de measures\'a yaz. «üretimin yüzde kaçı fire», «toplam '
    "içindeki payı» bunun içindir. ⚠ Katalogda hazır bir oran ölçüsü VARSA "
    "(ör. `…_orani_yuzde`) **onu** seç, turev yazma.\n"
    # 🔴🔴 `§AR/Ö` — **KURAL VARDI, ÖRNEK YOKTU — ve bu depo aynı kusuru bir kez
    # ölçmüştü** (`AJ3.5`: *«dar düzenleme yapan `refine_cube` prompt'unda 4 örnek
    # vardı, doğal dili yorumlayan bu prompt'ta 0. Zor işi yapana örnek verilmemişti»*).
    #
    # ⊙ Ölçüldü (canlı `XV`, üç ayrı ifade): *«toplam ciromun yüzde kaçı ilk 3
    # müşteriden»* · *«her müşterinin toplam ciro içindeki payı»* · *«müşterilerin ciro
    # payı yüzde olarak»* → `pencere` **hiçbirinde** yazılmadı, hepsi `null`. Oysa kural
    # üç satır yukarıda yazılı ve **Intent istemi onu yıllardır taşıyor**.
    #
    # ⚠ Örnek **rehberin içinde** duruyor, `llm.py`'nin örnek bloğunda değil: rehber
    # iki istem tarafından okunuyor (`§AR`) ve kuralı örneğinden ayırmak, ikisinden
    # birini taşımayı unutmaya davettir.
    #
    # *Bir kuralı yazmak onu okunur yapar; bir örnek vermek uygulanabilir.*
    "  ⊙ ÖRNEK: «toplam cironun yüzde kaçı ilk 3 müşteriden» → "
    '{"measures":["<ciro>"],"dimensions":["<müşteri>"],'
    '"pencere":{"taban":"<ciro>","kip":"pay"},'
    '"order":{"measure":"<ciro>","direction":"desc"},"limit":3}\n'
)


def cube_query_json_schema(index: dict, *, harman: bool = False) -> dict:
    """FAZ 3a — CubeQuery'nin ŞEMA-KISITLI biçimi: adlar o ANKİ kataloğun **enum**'u.

    ## Neden (plan §4.6b-C)

    Bugünkü akış *"serbest JSON iste, sonra `parse_cube_query` ile REDDET"*. Reddedilen
    her sorgu bir Discovery'ye düşüştür — yani kayıp, hatanın **sonrasında** kapatılıyor.
    Bu şema hatayı **öncesinde** engellemeyi hedefler: model geçersiz bir ad üretmek için
    şemanın dışına çıkmak zorunda kalır.

    ## Kritik tasarım: enum CUBE'A GÖRE DARALIR

    Düz bir `{"measures": {"enum": [tüm 81 ölçü]}}` **çapraz sızıntı** üretirdi: model
    `parti` cube'unu seçip `oee`'nin ölçüsünü isteyebilirdi — yapısal olarak "geçerli",
    semantik olarak saçma, ve `parse_cube_query` yine reddederdi. Yani kısıt hiçbir işe
    yaramazdı. Bu yüzden `oneOf`: **her cube kendi dalını taşır** ve o dalda yalnız
    KENDİ ölçü/boyut/zaman adları listelenir.

    ## REDDETME YOLU KORUNUR — en önemli madde

    İlk dal `{"cube": null}`. Şema-kısıtlı çıktının klasik tuzağı, modeli **geçerli ama
    yanlış** bir seçime ZORLAMAKtır: seçenekler arasında "hiçbiri" yoksa model illa
    birini seçer. Bu, sistemin en pahalı hata sınıfını (§6.1 sessiz-yanlış) üretirdi.
    Bugünkü prompt zaten *"yanıtlanamıyorsa KESİNLİKLE {cube:null} döndür"* diyor; şema
    bunu **yapısal** hale getirir, gevşetmez.

    ## Kapsam: YALNIZ BEŞ ÇEKİRDEK ALAN

    `order`/`limit` **bilerek dışarıda** — `parse_cube_query` onları zaten hoşgörüyle
    **sessizce düşürüyor** (geçersiz değer sorguyu öldürmüyor), dolayısıyla enum'lamak
    kazanç getirmez, yalnız şemayı büyütür.

    🔴 **`blend` DIŞARIDAYDI, `G6.5` ile GİRDİ — ve gerekçe tersine döndü.** Denetimin
    `Ç-14` maddesi: *"`blend` teşhiste var, çözümde sessizce düşüyor."* Ölçüldü ve
    haklıydı: çapraz-cube harman **mutfakta çalışıyor** (`wren_service.blend_sql`,
    `cross_cube_add`) ama **taze** bir soruda ifade edilemiyordu — *"verimlilik ve ciro"*
    tek cube'a sığmadığı için `{cube: null}`'a, oradan Discovery'ye düşüyordu (`Ö11`).
    Yani düşürülen şey geçersiz bir değer değil, **var olan bir yetenekti**.

    ⚠ *"Sessizce düşüyor zaten"* gerekçesi `order`/`limit` için doğru kalır: onlar
    cevabın **sunumunu** değiştirir. `blend` cevabın **kapsamını** değiştirir — düşünce
    kullanıcı iki seri ister, bir seri alır ve bunu **fark edemez**.

    ## Boyut: `$defs` ZORUNLULUKTU, tercih değil

    Harman öğesini her cube dalına **satır içi** yazmak `N²` demekti (23 cube → 529 alt
    şema). Tek bir `$defs/blend_ogesi` ile `N`'e iner (23). Şema modele **her istekte**
    gönderilir; `N²` bir şema, kısıtın kazandırdığından fazlasını token olarak geri alır.

    🔴 Ve `blend` **iki öğeyle sınırlı**: `blend_sql` her ek cube için bir `FULL OUTER
    JOIN` üretir. Üç cube'un ortak anahtarda buluşması, `parse_cube_query`'nin grain
    kapısından geçse bile **satır sayısını** öngörülemez kılar. *Bir birleşimin sınırı,
    onu yazan yerde durmalı — çalıştıran yerde değil.*
    """
    dallar: list[dict] = [{
        "type": "object",
        "title": "cevaplanamaz",
        "description": "Soru TEK bir cube ile yanıtlanamıyorsa (liste, çapraz-cube, "
                       "tanımsız) BU dal seçilir. Tahmin etmek yerine reddetmek doğrudur.",
        "properties": {"cube": {"type": "null"}},
        "required": ["cube"],
        "additionalProperties": False,
    }]
    for ad, spec in (index or {}).items():
        olculer = list(spec.get("measures") or [])
        boyutlar = list(spec.get("dimensions") or [])
        zamanlar = list(spec.get("time_dimensions") or [])
        if not olculer:
            continue  # ölçüsüz cube sorgulanamaz — dal açmak yanlış seçenek sunardı
        props: dict = {
            "cube": {"const": ad},
            "measures": {"type": "array", "minItems": 1,
                         "items": {"type": "string", "enum": olculer}},
        }
        if boyutlar:
            props["dimensions"] = {"type": "array",
                                   "items": {"type": "string", "enum": boyutlar}}
        if zamanlar:
            props["timeDimensions"] = {
                "type": "array",
                "items": {"type": "object", "additionalProperties": False,
                          "properties": {
                              "dimension": {"type": "string", "enum": zamanlar},
                              "granularity": {"type": "string", "enum": _GRAN_ENUM}},
                          "required": ["dimension", "granularity"]}}
        if zamanlar:
            # 🔴 `B-G4` (`G6`) — DÖNEMSEL KIYAS ŞEMAYA GİRDİ.
            #
            # Borç şöyle yazılmıştı: *"Intent-JSON'da `compare`/`blend` YOK → `5.6` (peer)
            # BLOKE."* Küp yolu kıyası artık kurabiliyor (`app/kiyas_cebiri.py`), ama LLM
            # yolu onu **ifade bile edemiyordu**: `parse_cube_query` beyaz listeyle çalışır
            # ve `compare`'ı **düşürürdü** (`dashboards.py:187` bunu bilip elle geri ekler).
            #
            # ⚠ Yalnız **zaman boyutu olan** dalda açılır: `compare` `shift_period_back` ile
            # bir dönemi geri kaydırır; zaman ekseni olmayan bir cube'da o kaydırma
            # **tanımsızdır** — ve modele tanımsız bir seçenek sunmak, onu kullanmaya davettir.
            #
            # Kapsam **kapalı**: `yoy`/`mom`. `app/yoy.py`'nin bildiği tek iki mod bunlar;
            # üçüncü bir değer, motorun sessizce yutacağı bir söz olurdu.
            props["compare"] = {"type": "string", "enum": ["yoy", "mom"],
                                "description": "Dönemsel kıyas: yoy=geçen yıla göre, "
                                               "mom=geçen aya göre. Soru bir KIYAS "
                                               "istemiyorsa BU ALANI HİÇ YAZMA."}
        # 🔴 `G6.5` — ÇAPRAZ-CUBE HARMAN. Kendisi hariç her cube bir seçenektir; ölçü
        # adları `$defs`'te o cube'un **kendi** enum'undan gelir (dal içi daralma kuralı,
        # `oneOf`'un aynısı). ⚠ Grain uyumu burada **doğrulanamaz** (şema, sorgunun öteki
        # alanlarını göremez) — onu `parse_cube_query.blend_uyumlu` yapar. Şema *"hangi
        # adlar"* sorusunun, kapı *"birlikte anlamlı mı"* sorusunun sahibidir.
        # ⚠ `harman` VARSAYILAN OLARAK KAPALI: bu fonksiyonun üç çağıranı var ve ikisi
        # test. Varsayılanı açık yapmak, bayrağı **atlayan** bir yol bırakırdı — kapalı
        # bir kill-switch'in yanından geçen tek çağrı, kill-switch'i iptal eder.
        if harman and len(index or {}) > 1:
            props["blend"] = {
                "type": "array", "minItems": 1, "maxItems": 2,
                "items": {"$ref": "#/$defs/harman_ogesi"},
                "description": "Soru TEK cube'a sığmıyor ama iki cube'un ölçüleri ORTAK "
                               "bir zaman/boyut ekseninde yan yana konabiliyorsa buraya "
                               "ikinci cube'u yaz. Tek cube yetiyorsa BU ALANI HİÇ YAZMA."}
        # 🔴 `AJ3.3` — DÖNEM İFADESİ. Enum **değil** ve olamaz: bu bir katalog adı değil
        # kullanıcının **kendi sözü**. Model onu kopyalar, çözümü `date_filters` yapar
        # (tek sahip) — takip yolundaki `period_expr`'in **aynısı**, ikinci bir çözücü yok.
        # ⚠ Alan olmadan model dönemi hiçbir yere koyamıyordu ve prompt *"tarih yazma"*
        # diyordu: tutarlı tek davranışı dönemi düşürmek ya da soruyu reddetmekti.
        if zamanlar:
            props["period_expr"] = {
                "type": ["string", "null"],
                "description": "Sorudaki dönem/tarih ifadesi AYNEN («geçen çeyrek», "
                               "«yılbaşından bugüne»). Tarihi SEN hesaplama. Dönem "
                               "geçmiyorsa null."}
        # 🔴 `§AJ4` — **GARSONUN FİŞİ EKSİKTİ: mutfak 12 anahtar yazıyor, şema 7 tanıyordu.**
        #
        # ⊙ Ayrım `G6.5`'te kurulan kuralın aynısı: *"zaten sessizce düşüyor"* gerekçesi
        # **sunumu** değiştiren alanlar için doğru kalır, **kapsamı** değiştirenler için
        # değil — düşünce kullanıcı bir şey ister, başkasını alır ve **fark edemez**.
        #
        # `order`+`limit` birlikte **kapsamdır**: *"en yüksek 5 müşteri"* beş satır demek,
        # bir sıralama tercihi değil. Tek başına `order` sunumdur ama ikisi ayrılamaz —
        # sıralamasız bir limit **kuyruğu keser, sonucu değil** (`§20.3`).
        props["order"] = {
            "type": "object", "additionalProperties": False,
            "properties": {"measure": {"type": "string", "enum": olculer},
                           "direction": {"type": "string", "enum": ["asc", "desc"]}},
            "required": ["measure", "direction"],
            "description": "Sıralama. *«en yüksek/en düşük»* dendiyse yaz — `limit` ile "
                           "birlikte kullan, yalnız biri sonucu belirsiz bırakır."}
        props["limit"] = {
            "type": "integer", "minimum": 1, "maximum": 1000,
            "description": "Satır sayısı. *«ilk 5»*, *«en yüksek 3»* gibi bir sayı "
                           "geçtiyse yaz; geçmediyse BU ALANI HİÇ YAZMA."}
        # 🔴 `M-9`/`M-3` — PENCERE ve TÜREV FİŞE YAZILDI. `M-6`'nın dersi birebir burada:
        # *mutfak o yemeği yapabiliyor ama menüde yazmıyordu.* `wren_service` kümülatifi,
        # hareketli ortalamayı, grup-içi sırayı ve oran/pay'ı **sarabiliyor**; garsonun
        # onu **isteyebileceği bir alan yoktu**, dolayısıyla `kümülatif`·`hareketli`·`pay`
        # nitelemeleri cevaptan sessizce düşüyordu (`p15`·`p16`·`r18`·`r12`).
        props["pencere"] = {
            "type": "object", "additionalProperties": False,
            "properties": {
                "taban": {"type": "string", "enum": olculer},
                "kip": {"type": "string", "enum": list(_ops.PENCERE_KIPLERI)},
                "pencere_boyu": {"type": "integer", "minimum": 2, "maximum": 24},
                "bolum": {"type": "array", "items": {"type": "string", "enum": boyutlar}}
                          if boyutlar else {"type": "array", "items": {"type": "string"}},
                "yon": {"type": "string", "enum": ["asc", "desc"]}},
            "required": ["taban", "kip"],
            # 🔴 `§V6` — aynı sınır burada da yazılı: kural iki yerde yaşıyorsa ikisi de
            # aynı şeyi söylemeli, yoksa hangisinin okunduğuna göre davranış değişir.
            "description": "Zaman/grup PENCERESİ. *«kümülatif»*→`kumulatif`, *«hareketli "
                           "N aylık ortalama»*→`hareketli_ort`+`pencere_boyu`, *«her X "
                           "için en yüksek»*→`sira`+`bolum` (🔴 `sira` YALNIZ grup-içidir "
                           "ve `bolum` ŞARTTIR; düz bir *«ilk N»* isteğinde `sira` değil "
                           "`order`+`limit` kullan), *«önceki döneme göre yüzde "
                           "değişim»*→`degisim_yuzde`. `kumulatif`/`hareketli_ort`/"
                           "`degisim_yuzde` bir ZAMAN KOVASI ister (`timeDimensions`)."}
        props["turev"] = {
            "type": "object", "additionalProperties": False,
            "properties": {"pay": {"type": "string", "enum": olculer},
                           "payda": {"type": "string", "enum": olculer},
                           "kip": {"type": "string", "enum": list(_ops.TUREV_KIPLERI)}},
            "required": ["pay", "kip"],
            "description": "TÜREV ölçü — iki ölçü arasında oran/pay/fark. *«üretimin yüzde "
                           "kaçı fire»*, *«toplam içindeki payı»* → `kip:yuzde` ve iki "
                           "ölçüyü de `measures`'a yaz. Katalogda hazır bir oran ölçüsü "
                           "VARSA (ör. `…_orani_yuzde`) onu tercih et, bunu yazma."}
        props["measure_having"] = {
            "type": "object", "additionalProperties": False,
            "properties": {"measure": {"type": "string", "enum": olculer},
                           "op": {"type": "string", "enum": [">", ">=", "<", "<="]},
                           "value": {"type": "number"}},
            "required": ["measure", "op", "value"],
            "description": "ÖLÇÜ eşiği (*«10 milyon üzeri»*, *«100 binin altında»*). "
                           "Boyut değeri filtresi DEĞİL — o `filters`'a gider."}
        if boyutlar:
            props["filters"] = {
                "type": "array",
                "items": {"type": "object", "additionalProperties": False,
                          "properties": {
                              "dimension": {"type": "string", "enum": boyutlar},
                              # 🔴 `M-6` — ELLE YAZILMIŞ 7'LİK LİSTE SİLİNDİ, TEK KAYNAĞA
                              # BAĞLANDI. Eski liste `["eq","ne","gt","gte","lt","lte","in"]`
                              # idi ve iki kusuru vardı: (1) **`ne` motorda YOK** — canlı
                              # `/cube` sondajı (iki koşum) HTTP **400** ve motorun kendi
                              # cümlesi: *"unknown variant `ne`, expected one of `eq`,
                              # `neq`, …"* — yani şema, modele motorun **reddedeceği** bir
                              # ad yazdırıyordu; (2) motorun **ölçülmüş** 12 operatörünün
                              # beşi (`neq`·`not_in`·`contains`·`starts_with`·`is_null`/
                              # `is_not_null`) fişte yoktu → garson *"beyaz hariç"*,
                              # *"adı X ile başlayanlar"*, *"kodu boş olanlar"* niyetlerini
                              # **ifade edemiyor** ve Discovery'ye düşüyordu. Mutfak o
                              # yemeği yapabiliyor; **menüde yazmıyordu**.
                              "operator": {"type": "string",
                                           "enum": list(_ops.MOTOR_OPERATORLERI)},
                              "value": {}},
                          "required": ["dimension", "operator", "value"]}}
        dallar.append({"type": "object", "title": ad,
                       "properties": props, "required": ["cube", "measures"],
                       "additionalProperties": False})
    ogeler = [{"type": "object", "additionalProperties": False, "title": ad,
               "properties": {"cube": {"const": ad},
                              "measures": {"type": "array", "minItems": 1,
                                           "items": {"type": "string", "enum": ms}}},
               "required": ["cube", "measures"]}
              for ad, spec in (index or {}).items()
              if (ms := list(spec.get("measures") or []))]
    out: dict = {"type": "object", "oneOf": dallar}
    if harman and len(ogeler) > 1:
        out["$defs"] = {"harman_ogesi": {"oneOf": ogeler}}
    return out
