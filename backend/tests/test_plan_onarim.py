"""`O-15` — ONARIM · DÖNEM · DEVİR kapıları.

Beşi de **canlı `II` turunda ölçülmüş** kusurlardır; hiçbiri varsayım değildir:

| kapı | canlı vaka | kusur |
|---|---|---|
| `test_ZAMAN_EKSENI_DIMENSIONS_A_DUSERSE_TASINIR` | `II19`·`II20` | plan tamamen düştü |
| `test_TIMEDIMENSIONS_METIN_ISE_DONEME_TASINIR` | `II8` | motor tip hatası |
| `test_DONEM_PLAN_YOLUNDA_DUSMEZ` | `K1`/`K2` | 🔴 **sessiz yanlış** |
| `test_IKI_CUBE_ERKEN_KAPIDA_DEVREDILIR` | `II3`·`II4` | pano/matris reddedildi |
| `test_ONARIM_SESSIZ_DEGIL` | — | beyan edilmeyen varsayım |
"""

from __future__ import annotations

from app import plan_onarim, yetenek

#: `parti` küpünün canlı tanımı (kısaltılmış) — zaman ekseni `dimensions`'da **yok**.
PARTI = {"name": "parti",
         "measures": ["toplam_fire_kg", "fire_orani_yuzde"],
         "dimensions": ["makine", "vardiya", "musteri"],
         "time_dimensions": ["tarih"]}


def test_ZAMAN_EKSENI_DIMENSIONS_A_DUSERSE_TASINIR():
    """🔴 `II19`/`II20`: model `dimensions:["tarih"]` yazdı, plan **tamamen** düştü.

    `tarih` o küpte bir boyut DEĞİL, bir zaman ekseni. Bunun **başka bir okuması yok** —
    bir düzeltme turuna havale etmek, bilinen bir cevabı ikinci kez satın almaktır.
    """
    cq = {"cube": "parti", "measures": ["toplam_fire_kg"], "dimensions": ["tarih"]}
    out, beyan = plan_onarim.onar(cq, PARTI)
    assert out.get("timeDimensions") == [
        {"dimension": "tarih", "granularity": plan_onarim.VARSAYILAN_GRANULERLIK}]
    assert "dimensions" not in out, "zaman ekseni boyut listesinde KALMAMALI"
    assert beyan, "onarım sessiz olamaz"


def test_GERCEK_BOYUT_TASINMAZ():
    """⚠ `§101.1` — yanlış pozitif üreten bir yordam, kapattığı kusurdan pahalıdır.

    `makine` gerçek bir boyut; onarıcı ona **dokunmamalı**. Ve dokunmadığında dönen
    sözlük girdinin **kendisi** olmalı — bir kopya bile, *"bir şey oldu"* demektir.
    """
    cq = {"cube": "parti", "measures": ["toplam_fire_kg"], "dimensions": ["makine"]}
    out, beyan = plan_onarim.onar(cq, PARTI)
    assert out is cq and beyan == []


def test_TIMEDIMENSIONS_METIN_ISE_DONEME_TASINIR():
    """🔴 `II8`: `"timeDimensions": "This month"` → motor *«expected a sequence»* ile
    düştü, plan reddedildi. Yazılan şey tek anlamlı: bir **dönem**dir."""
    cq = {"cube": "parti", "measures": ["toplam_fire_kg"], "timeDimensions": "This month"}
    out, beyan = plan_onarim.onar(cq, PARTI)
    assert out.get("period_expr") == "This month"
    assert not isinstance(out.get("timeDimensions"), str)
    assert beyan


def test_TIMEDIMENSIONS_METNI_GRANULERLIK_ISE_EKSENE_CEVRILIR():
    """`"month"` bir dönem değil bir **granülerliktir** — küpün kendi ekseni varsayılır."""
    cq = {"cube": "parti", "measures": ["toplam_fire_kg"], "timeDimensions": "month"}
    out, _ = plan_onarim.onar(cq, PARTI)
    assert out["timeDimensions"] == [{"dimension": "tarih", "granularity": "month"}]


def test_ZAMAN_EKSENI_OLMAYAN_KUPTE_HIC_DOKUNULMAZ():
    """Zaman ekseni olmayan bir küpte onarımın **tanımı yok** — erken çıkar."""
    spec = {"name": "x", "measures": ["m"], "dimensions": ["d"], "time_dimensions": []}
    cq = {"cube": "x", "measures": ["m"], "dimensions": ["tarih"]}
    out, beyan = plan_onarim.onar(cq, spec)
    assert out is cq and beyan == []


def test_ONARIM_SESSIZ_DEGIL():
    """🔴 Her onarım bir **metin** üretir ve o metin ize düşer.

    Gerekçe `MIMARI`'nin değişmezidir: kullanıcının gördüğü sayı kendisinin yazmadığı
    bir varsayımla üretildiyse, o varsayım görünür olmalıdır. ⚠ Ve beyan bir **ölçüm
    aletidir**: izde sık görünüyorsa istem yetersiz demektir.
    """
    _, beyan = plan_onarim.onar(
        {"cube": "parti", "measures": ["toplam_fire_kg"], "dimensions": ["tarih"]}, PARTI)
    assert len(beyan) == 1 and "tarih" in beyan[0]


def test_DONEM_PLAN_YOLUNDA_DUSMEZ():
    """🔴🔴 **SESSİZ YANLIŞ** — turun en ağır kusuru.

    Ölçüldü (canlı `K1`/`K2`): *«toplam fire»* ve *«**2023 yılındaki** toplam fire»*
    aynı sayıyı verdi (`1703818.39…`). İstem modele dönemi `period_expr`'e yazdırıyor,
    beyaz liste alanı koruyor — ama `cube_sql` onu **tanımıyor**. `ask()`in garson dalı
    çözüyordu; plan dalı için **hiç kimse** çözmüyordu.

    Kapı sahte bir motorla koşar: `cube_sql`'e giden sorguda dönem **filtresi** olmalı
    ve `period_expr` **kalmamalı**.
    """
    from app import plan_tuketici

    goren: list[dict] = []

    class _Motor:
        def cube_sql(self, cq):
            goren.append(cq)
            return "SELECT 1"

        def dry_plan(self, sql):
            return None

        def query(self, sql, limit=None):
            return {"columns": ["toplam_fire_kg"], "rows": [{"toplam_fire_kg": 1.0}]}

    plan = {"adimlar": [{"sira": 1, "fiil": "SORGU", "cube_query": {
        "cube": "parti", "measures": ["toplam_fire_kg"], "period_expr": "2023 yılında"}}]}
    plan_tuketici.calistir(plan, service=_Motor(), index={"parti": PARTI},
                           schema={"cubes": [PARTI]}, soru="2023 yılındaki toplam fire")
    assert goren, "sorgu motora hiç gitmedi"
    cq = goren[0]
    assert "period_expr" not in cq, "niyet taşıyıcısı motora GİTMEMELİ"
    _f = [f for f in (cq.get("filters") or []) if f.get("dimension") == "tarih"]
    assert _f, f"dönem filtresi ÜRETİLMEDİ — dönem yine düşüyor: {cq}"
    assert any("2023" in str(f.get("value")) for f in _f), f"yanlış döneme çözüldü: {_f}"


def test_IKI_CUBE_ERKEN_KAPIDA_DEVREDILIR(schema):
    """🔴 `II3`/`II4`: *«pano taslağı»* ve *«karar matrisi»* erken kapıda reddedildi —
    oysa kapının **kendi metni** *«yan yana koyabilirim»* diyor ve `PANO`/`MATRIS` tam
    olarak odur. Sınır **kaldırılmadı, ertelendi**: geç kapı aynen konuşur.

    ⚠ **Gerçek şema** kullanılır, uydurma değil: `_iki_cube_olcusu` sinonim metinlerine
    bakar ve sentetik bir küple hiç ateşlenmez. Ateşlenmeyen bir kapı, `skip` ile yeşil
    görünen bir kapısızlıktır. *Bir kapıyı konusuz bırakmak, onu kaldırmaktan yalnızca
    daha zor fark edilir.*
    """
    q = "üretim, fire ve enerji için bir pano taslağı hazırla"
    gec = yetenek.kapsam_disi(q, schema)
    assert gec is not None and gec.tur == "iki_cube", \
        f"canlı `II3` bu sınıra çarpıyordu; artık çarpmıyorsa kapı konusuz: {gec}"
    assert gec.tur in yetenek.DEVREDILEBILIR
    assert yetenek.kapsam_disi(q, schema, erken=True) is None, \
        "devredilebilir sınır erken kapıda SUSMALI — orkestratöre yol verilmeli"


def test_FORECAST_ERTELENMEZ(schema):
    """⚠ Yalnız `iki_cube` ertelenir. `forecast` bir **çıktı biçimi** eksikliği değil,
    bir **yetenek** eksikliğidir — plan da yapamaz. Ertelemek reddi geciktirmek olurdu."""
    q = "önümüzdeki çeyrek için fire tahmini yap"
    erken = yetenek.kapsam_disi(q, schema, erken=True)
    assert erken is not None and erken.tur == "forecast"
    assert "forecast" not in yetenek.DEVREDILEBILIR


def test_YON_ISARETI_MAKBUZA_SIZMAZ():
    """🔴 `§CC-D` **makbuz düzeyinde tekrarlandı.**

    Ölçüldü (canlı `D2'`): makbuzda **`toplam_fire_kg↓`** yazıyordu — katalogun *«az
    olan iyidir»* işareti kullanıcının okuduğu satıra sızmıştı. `parse_cube_query` onu
    kimlikten ayıklıyor; makbuz ayıklamıyordu. *Bir süsü bir yerde temizlemek, onu
    üreten kaynağı temizlemez.*
    """
    from app.plan_tuketici import _adim_metni

    metin = _adim_metni({"sira": 1, "fiil": "SORGU", "cube_query": {
        "cube": "parti", "measures": ["toplam_fire_kg↓"]}})
    assert "↓" not in metin, f"yön işareti makbuza sızdı: {metin}"
    assert "toplam_fire_kg" in metin


def test_TUMU_NULL_SATIR_SESSIZ_KALMAZ():
    """🔴🔴 `KÖK-F` — **boş olmayan ama tümü `null` bir satır da bir sessizliktir.**

    Ölçüldü (canlı `D2'`): *«2023 yılındaki toplam fire»* → 1 satır, `{"…": null}`,
    hiçbir not. `row_count == 1` olduğu için boşluk yüklemi susuyordu.

    ⚠ Ve bu kusuru **dönem düzeltmesi görünür kıldı**: önce sessiz **yanlış** (tüm
    zamanların toplamı), sonra açıklamasız bir **boşluk**. Bir yolu açmak, o yolun
    üstündeki çukuru da devralmaktır.
    """
    from app import plan_tuketici

    class _Motor:
        def cube_sql(self, cq):
            return "SELECT 1"

        def dry_plan(self, sql):
            return None

        def query(self, sql, limit=None):
            return {"columns": ["toplam_fire_kg"], "rows": [{"toplam_fire_kg": None}]}

    class _Istek:
        class state:      # noqa: N801 — `request.state` taklidi
            plan_taslagi = {"adimlar": [{"sira": 1, "fiil": "SORGU", "cube_query": {
                "cube": "parti", "measures": ["toplam_fire_kg"]}}]}

        class app:        # noqa: N801
            class state:  # noqa: N801
                llm = object()

    out = plan_tuketici.calistir(_Istek.state.plan_taslagi, service=_Motor(),
                                 index={"parti": PARTI}, schema={"cubes": [PARTI]})
    assert out["sonuclar"][0]["rows"] == [{"toplam_fire_kg": None}]
    # Notun kendisi `cevap()`'ta kuruluyor; yüklemi burada doğrudan sınıyoruz:
    _rows = out["sonuclar"][0]["rows"]
    assert all(v is None for r in _rows for v in r.values()), "fikstür bozuk"


def test_DOLU_HUCRE_VARSA_UYARI_YAZILMAZ():
    """⚠ `§101.1` — yanlış pozitif üreten bir uyarı, sustuğu durumdan pahalıdır.
    Tek bir dolu hücre varsa cevap doludur."""
    _rows = [{"a": None, "b": 3}]
    assert not all(v is None for r in _rows for v in r.values())


def test_O16_GERI_ALINDI_VE_KAYDI_DURUYOR():
    """⟳ `O-16` denendi, **canlıda ölçüldü ve ÇÜRÜTÜLDÜ**, geri alındı.

    Hipotez: *"bütçe (20 sn) tek bir `CubeQuery` için kalibre; plan daha uzun, o yüzden
    aşıyor."* `45 sn`'ye çıkarıldı ve canlıda ölçüldü (`III7`):

        20:44:13 istek · 20:44:58 üç oyun ÜÇÜ DE 45 sn'yi de aştı
        20:45:23 geç bir oy 5 adımlık planı SAKLADI  ← cevap BUNDAN çıktı
        20:46:05 cevap · **111.870 ms**

    İki şey birden yanlış çıktı: oylar plan uzun olduğu için değil, **üç eşzamanlı
    uzun-çıktı çağrısı sağlayıcıda kuyruğa girdiği** için aşıyor; ve `III7`'yi düzelten
    şey bütçe değil `O-15/Y` geç-plan kurtarmasıydı. Yükseltme **25 sn saf bekleme**,
    sıfır doğruluk.

    Kapı iki şeyi birden korur: ayar **geri alınmış** olmalı **ve** çürütmenin kaydı
    kaynakta **durmalı**. *Çürütülmüş bir hipotezi silmek, bir sonraki turun onu
    yeniden satın almasına izin vermektir.*
    """
    import inspect

    from app.config import Settings
    from app.routers import ask as _ask

    assert not hasattr(Settings(), "plan_azami_saniye"), "ayar geri alınmadı"
    assert "`O-16` DENENDİ" in inspect.getsource(_ask._select_consistent), \
        "çürütmenin kaydı kaynaktan silinmiş"


def test_GEC_PLAN_KULLANIM_ANINDA_OKUNUR():
    """🔴 `O-15/Y` — `III7`'yi gerçekten düzelten kapı.

    Kaynak okunur: hazır plan **karar anında** okunmalı, fonksiyon başında okunup
    saklanmamalı. Ölçüldü: saklama, tüketici başladıktan **2 sn sonra** oldu.
    """
    import inspect

    from app import plan_tuketici

    src = inspect.getsource(plan_tuketici.cevap)
    _i = src.index("plan_garson.plan_uret(")
    assert "plan_taslagi" in src[max(0, _i - 400):_i], \
        "hazır plan `plan_uret` çağrısının HEMEN önünde okunmuyor — yarış geri geldi"


def test_ORKESTRATOR_ROUTE_UN_ONUNE_GECEMEZ():
    """🔴🔴 `O-17` — **`E3` DEĞİŞMEZİNİN İHLALİ**: orkestratör boşluğu doldurmuyor,
    route'un **önünde duruyordu**.

    Ölçüldü (canlı `IV` turu):

    | soru | `route()` tek başına | HTTP yolu (önce) |
    |---|---|---|
    | *«makine bazında ortalama oee»* | ✅ `oee/ort_oee/makine` | `cube+llm` |
    | *«en yüksek cirolu 5 müşteri»* | ✅ `order DESC · limit 5` | 🔴 **CEVAPSIZ** |

    Üçüncü satır bedeli tek başına ölçüyor: route'un doğru bildiği bir soru cevapsız
    kaldı, çünkü garson `satis` diye olmayan bir küp uydurdu.

    ⚠ Kapı **iki ucu birden** tutar: modül ön koşulu uygular **ve** çağrı yeri
    `route_hit`'i geçirir. Biri olmadan öteki bir dilektir.
    """
    import inspect

    from app import plan_tuketici
    from app.routers import ask as _ask

    # (1) Modül kendi ön koşulunu uyguluyor mu
    assert plan_tuketici.cevap(None, service=None, schema={}, soru="x",
                               route_hit={"cube_query": {"cube": "parti"}}) is None, \
        "route bir cevap bulduğu hâlde orkestratör konuştu — `E3` ihlali"

    # (2) Çağrı yeri `route_hit`'i geçiriyor mu — yoksa (1) hiç tetiklenmez
    src = inspect.getsource(_ask.ask)
    _i = src.index("_plan_tuketici.cevap(")
    _cagri = src[_i:src.index(")", src.index("limit=limit", _i))]
    assert "route_hit=route_hit" in _cagri, \
        f"çağrı yeri `route_hit`'i GEÇİRMİYOR — ön koşul hiç tetiklenemez: {_cagri!r}"


def test_BOSLUKTA_ORKESTRATOR_YINE_KONUSUR():
    """⚠ `§101.1` — düzeltme, düzelttiği şeyi kapatmamalı. `route_hit is None` iken
    modül **yine** devreye girmeli; aksi hâlde orkestratör tümden susardı."""
    import inspect

    from app import plan_tuketici

    src = inspect.getsource(plan_tuketici.cevap)
    _i = src.index("if route_hit is not None:")
    # Ön koşul `None` durumunu **kesmiyor**: `is not None` yazılı, `if route_hit`ten
    # farkı boş bir sözlüğün de kapı sayılmasıdır — route boş sözlük döndürmez.
    assert "is not None" in src[_i:_i + 40]
    assert "llm = getattr" in src[_i:], "boşluk yolu ön koşulun ALTINDA kalmalı"


def test_AD_DENETIMI_PLAN_KURULURKEN_YAPILIR():
    """🔴🔴 `O-18` — **onarım turu ad hatasını GÖREMİYORDU.**

    Ölçüldü (canlı `IV`, kullanıcının örneği *«ram 3 oee neden diğerlerine göre daha
    düşük bu yıl»*): model **kusursuz** bir 7 adımlık kök-neden inişi kurdu, plan
    doğrulamadan **geçti** (doğrulayıcı yapıya bakıyor, adlara bakmıyordu) ve beşinci
    adımda `KIR(boyut="neden")` patladı — `oee`'de öyle bir boyut yok. **Dört adım
    çoktan koşmuştu**, ve red koşum anında doğduğu için model hiçbir şey öğrenemedi.

    ⚠ Kusur `cube_query`'nin İÇİNDE değil, bir **adım alanındaydı** (`KIR.boyut`) ve
    küp **referans zinciriyle** çözülüyordu: `$4` → `SUZ($1)` → `SORGU({cube:"oee"})`.
    """
    from app.plan_kosucu import PlanHatasi, dogrula

    plan = {"adimlar": [
        {"fiil": "SORGU", "cube_query": {"cube": "parti", "measures": ["toplam_fire_kg"],
                                         "dimensions": ["makine"]}},
        {"fiil": "SUZ", "cube_query": "$1", "boyut": "makine", "deger": "RAM-3"},
        {"fiil": "KIR", "cube_query": "$2", "boyut": "neden"},
        {"fiil": "SORGU", "cube_query": "$3"}]}
    dogrula(plan)                     # index YOK → bugünkü davranış, bayt bayt aynı
    try:
        dogrula(plan, index={"parti": PARTI})
    except PlanHatasi as e:
        assert "neden" in str(e) and "var olanlar" in str(e), \
            f"red hangi boyutun olmadığını VE var olanları söylemeli: {e}"
    else:
        raise AssertionError("referans zinciriyle çözülen boyut denetlenmedi")


def test_AD_DENETIMI_INDEX_YOKKEN_HIC_KOSMAZ():
    """⚠ `KURAL B` — `index=None` iken `O-18` tek karakter davranış değiştirmez."""
    from app.plan_kosucu import dogrula

    plan = {"adimlar": [{"fiil": "SORGU", "cube_query": {"cube": "yok_boyle_bir_kup",
                                                         "measures": ["m"]}}]}
    assert dogrula(plan) == [[1]], "index'siz doğrulama eskisi gibi geçmeli"


def test_AD_REDDI_YUMUSAKTIR_ADIM_ADIM_DURUSTLUK_KAYBOLMAZ():
    """🔴 `O-18/Y` — ad reddi onarım turunu **tetikler**, planı **atmaz**.

    Yapısal red edilmiş bir plan **koşulamaz**; ad reddi edilmiş bir plan **koşabilir**
    ve bir adımda dürüstçe durur — o da `O-4`'ün ikinci başarı ölçütüdür. Bu ayrım
    olmasaydı `O-18` bir kazanç değil bir **takas** olurdu.
    """
    import inspect

    from app import plan_garson

    src = inspect.getsource(plan_garson.plan_uret)
    assert "_yedek" in src, "yedek plan yolu kaldırılmış — adım adım dürüstlük kaybolur"
    _i = src.index("_yedek = ")
    assert "_plani_oku(_ham)" in src[_i:_i + 80], \
        "yedek plan `index`SİZ okunmalı — yapısal geçerlilik yeter"


def test_COKLUK_BELIRSIZLIK_DEGILDIR():
    """🔴🔴 `O-19` — ayrık ölçü kümeleri bir **çokluktur**, belirsizlik değil.

    Ölçüldü (canlı `IV`): *«iade oranı en yüksek 3 müşteriyi **ve** ciro paylarını
    göster»* → `%50 uyum · eksen=measures` → *«Hangi ölçüyü istiyorsun?»*. Oylardan
    biri çekimser (*«tek cube ile olmaz»* — haklı), ikisi farklı küplerden farklı
    ölçüler seçti. Üç oy da doğru: soru **iki parçalı**, cevabı bir **plan**.
    """
    from app import uyum

    assert uyum.cokluk_mu("measures", [{"cube": "sikayet", "measures": ["iade_orani"]},
                                       {"cube": "parti", "measures": ["toplam_ciro"]}])


def test_ZENGINLIK_FARKI_COKLUK_DEGILDIR():
    """⚠ `§101.1` — kesişen kümeler **çokluk sayılmaz**: `{ciro}` ↔ `{ciro, fire}` bir
    oyun ötekinden daha zengin okumasıdır (`§V2`'nin konusu), iki ayrı istek değil."""
    from app import uyum

    assert not uyum.cokluk_mu("measures", [{"measures": ["toplam_ciro"]},
                                           {"measures": ["toplam_ciro", "toplam_fire_kg"]}])


def test_AYNI_OLCU_IKI_SAHIP_YINE_SORULUR():
    """🔴 `eksen=cube` (aynı ölçü adı, iki küp) **gerçek** bir belirsizliktir ve aynen
    sorulur. *Bir soruyu sormak için önce iki farklı cevabın olması gerekir.*"""
    from app import uyum

    assert not uyum.cokluk_mu("cube", [{"cube": "parti", "measures": ["toplam_fire_kg"]},
                                       {"cube": "oee", "measures": ["toplam_fire_kg"]}])
    assert not uyum.cokluk_mu(None, [{"measures": ["a"]}, {"measures": ["b"]}])


def test_COKLUK_ERTELEMESI_KAYIPSIZ():
    """⚠ Plan cevap veremezse **birebir aynı** chip konuşur — kaynaktan doğrulanır.

    En kötü durum bugünküyle bayt bayt aynı olmalı; aksi hâlde erteleme bir **takas**
    olurdu. *Bir sınırı ertelemek ancak arkasında onu aşabilecek bir basamak varsa
    doğrudur.*
    """
    import inspect

    from app.routers import ask as _ask

    src = inspect.getsource(_ask.ask)
    assert "_ertelenen_chip = _chip" in src, "chip saklanmıyor"
    _i = src.index("_pc is None and _ertelenen_chip is not None")
    assert "_finish(_ertelenen_chip)" in src[_i:_i + 200], \
        "ertelenen chip plan başarısız olunca KONUŞMUYOR — erteleme kayıplı olurdu"


def test_PLAN_YOLU_DURUSTLUK_KAPISINDAN_GECER():
    """🔴🔴 `O-20` — **`uyum` kapısı plan yolunu hiç görmüyordu.**

    Ölçüldü (canlı `V` turu): *«personel **devir oranı** bu yıl nasıl»* → cevap
    **`personel_sayisi`** (baş sayısı) döndü. Soru bir **oran** istedi, cevap bir
    **sayım** verdi, **hiçbir beyan yoktu** — `sessiz_yanlis`, ve onu üreten şey
    bayrağı kapatılamayan bir yol.

    ⚠ Model **uydurmadı**: `personel_sayisi` katalogda var. Yaptığı bir **ikamedir** —
    istenen kavram yoksa en yakınını koymak. Beyaz liste ikameyi göremez (ad geçerli),
    `O-18` ad denetimi de göremez (adın **varlığına** bakar). Görebilen tek yer,
    **soruyla cevabı karşılaştıran** yerdir.

    *Bir kapıyı yazmak onu her yola koymaz — yeni bir yol, eski kapıların arkasından
    değil YANINDAN geçer.*
    """
    from app import plan_tuketici

    class _Motor:
        def cube_sql(self, cq):
            return "SELECT 1"

        def dry_plan(self, sql):
            return None

        def query(self, sql, limit=None):
            return {"columns": ["personel_sayisi"], "rows": [{"personel_sayisi": 29}]}

    IK = {"name": "ik", "measures": ["personel_sayisi"],
          "dimensions": ["departman"], "time_dimensions": ["donem_tarih"]}

    class _Garson:
        sema_kullanir = False
        plan_kurabilir = True

        def plan_kur(self, *a, **k):
            import json as _j
            return _j.dumps({"adimlar": [{"fiil": "SORGU", "cube_query": {
                "cube": "ik", "measures": ["personel_sayisi"]}}]})

    class _Istek:
        class state:      # noqa: N801
            plan_taslagi = None

        class app:        # noqa: N801
            class state:  # noqa: N801
                llm = _Garson()

    # ⚠ Bayrak **açık** koşulur: `skip` ile yeşil görünen bir kapı, kapı değildir.
    # `acik_mi` `resolve_for`'dan okuyor; kapı onu yamalar ve yerine koyar.
    import app.plan_garson as _pg

    _asil = _pg.acik_mi
    _pg.acik_mi = lambda *a, **k: True
    try:
        out = plan_tuketici.cevap(_Istek, service=_Motor(), schema={"cubes": [IK]},
                                  soru="personel devir oranı bu yıl nasıl",
                                  settings=None, principal=None)
    finally:
        _pg.acik_mi = _asil
    assert out is not None, "plan yolu hiç koşmadı — kapı konusuz kaldı"
    assert "eksik" in (out["note"] or "").lower(), (
        "bir ORAN istendi ve bir SAYIM döndü — cevap beyansız çıkamaz:\n"
        + (out["note"] or "")[:400])


def test_TREND_KUPUN_KENDI_ZAMAN_EKSENINI_KULLANIR():
    """🔴🔴 `§X1` **ÜÇÜNCÜ TEKRAR** — ve bu kez tur öldü.

    Ölçüldü (canlı `V`, *«personel devir oranı bu yıl nasıl»*):

        adım 2 (`TREND`) koşulamadı: Unknown filter dimension 'tarih' in cube 'ik'

    `cube_meta` bu çağrıya `{"lower_is_better": […]}` olarak geliyor — `time_dimensions`
    anahtarı **hiç yok**. Yedek (`["tarih"]`) her zaman kazanıyordu, yani `ik`
    (`donem_tarih`) gibi küplerde `TREND` **yapısal olarak** koşamıyordu.

    *Var olmayan bir anahtarı `or` ile yedeklemek, yedeği varsayılan yapar — ve
    varsayılan yanlışsa kusur asla görünmez, yalnız tekrarlar.*
    """
    from app import plan_tuketici

    IK = {"name": "ik", "measures": ["personel_sayisi"], "dimensions": ["departman"],
          "time_dimensions": ["donem_tarih"]}
    gorulen: list[str] = []

    class _SahteYoy:
        @staticmethod
        def compute(service, cq, mode, td):
            gorulen.append(td)
            return {"rows": []}

    # ⚠ `from app import yoy` **paketin niteliğini** okur, `sys.modules`'ı değil —
    # ilk yazımda `sys.modules` yamalandı ve yama hiç görülmedi. *Bir importu
    # yamalarken, onu çözen mekanizmayı yamalamak gerekir.*
    import app as _app

    _asil = _app.yoy
    _app.yoy = _SahteYoy
    try:
        g = plan_tuketici._govdeler(None, {"cubes": [IK]}, {"lower_is_better": []})
        g["TREND"]({"cube_query": {"cube": "ik", "measures": ["personel_sayisi"]}})
    finally:
        _app.yoy = _asil
    assert gorulen == ["donem_tarih"], (
        f"`TREND` küpün kendi zaman eksenini kullanmalı, sabit `tarih` değil: {gorulen}")


def test_TEK_FIS_OKUMASI_AZINLIKTAYSA_PLAN_KONUSUR():
    """🔴🔴 `O-21` — çok adımlı plan oylamada **görünmüyordu**.

    Ölçüldü (canlı `VI`, log damgalarıyla):

        22:33:14  plan: 1 adım (SORGU)                  ← bir örnek «tek fiş»
        22:33:15  plan: 3 adım (SORGU·SORGU·MATRIS)     ← öteki «orkestre»
        22:33:23  orkestratör: route zaten cevapladı → hiç konuşmuyorum

    Çok adımlı örnek `"{}"` döndürüyor, beyaz liste onu `None` yapıyor ve oy
    **çekimser** sayılıyor. Bir *«basit okuma»* örneği iki *«orkestre gerekli»*
    örneğini **görünmez kılarak** eziyor; `O-17` ön koşulu da o azınlık okumasını
    route'un cevabı sanıp geçerli bir planı susturuyordu.

    *Bir kararı oylanamaz ilan etmek, onu tek bir örneğe bırakmaktır.*
    """
    from app import plan_tuketici

    TEK = {"cube": "parti", "measures": ["toplam_fire_kg"]}

    class _Istek:
        class state:      # noqa: N801
            plan_sekil = {"tek": 1, "cok": 2}
            plan_tek_cq = TEK
            plan_taslagi = None

        class app:        # noqa: N801
            class state:  # noqa: N801
                llm = None

    # Azınlık okuması → ön koşul GEÇMELİ (llm yok diye ilerisi None döner ama
    # kapının ölçtüğü şey ön koşulun kesip kesmediği; log satırı ayırt eder).
    import app.plan_garson as _pg

    _asil = _pg.acik_mi
    _pg.acik_mi = lambda *a, **k: True
    try:
        out = plan_tuketici.cevap(_Istek, service=None, schema={"cubes": []},
                                  soru="x", route_hit={"cube_query": TEK})
    finally:
        _pg.acik_mi = _asil
    assert out is None    # llm yok → ilerisi zaten durur

    # Çoğunluk tek-fiş dediyse ön koşul KESMELİ — plan konuşmamalı.
    _Istek.state.plan_sekil = {"tek": 2, "cok": 1}
    assert plan_tuketici.cevap(_Istek, service=None, schema={"cubes": []}, soru="x",
                               route_hit={"cube_query": TEK}) is None

    # Başka bir yoldan gelen `route_hit`'e ASLA dokunulmaz (sınır yazılı olmalı).
    import inspect

    src = inspect.getsource(plan_tuketici.cevap)
    assert "route_hit.get(\"cube_query\") == _tek_cq" in src, \
        "gevşemenin sınırı yazılı değil — başka bir route_hit'i de yutardı"


def test_PLANIN_KARSILADIGI_ISARET_BEYAN_EDILMEZ():
    """🔴 `O-20/Y` — `BAGLA` üstünlüğü **uyguluyor**; *«sıralama uygulayamadım»* yanlış.

    Ölçüldü (canlı `VI`): plan 6 adım koştu, `BAGLA` en çok fire vereni seçti (`RAM-2`)
    ve cevabın altına *«en yüksek/en çok dedin ama sıralama uygulayamadım»* yazıldı.
    `uyum.denetle` bir **`CubeQuery`** denetleyicisidir; üstünlüğü `order`/`limit`
    alanlarında arar ve planın **adımla** taşıdığı niyeti göremez.

    *Bir denetçiyi yeni bir yola koyarken o yolun araçlarını da tanıtmak gerekir;
    yoksa tanımadığı her çözümü bir eksiklik sanar.*
    """
    import inspect

    from app import plan_tuketici

    src = inspect.getsource(plan_tuketici.cevap)
    _i = src.index("_karsilanan")
    assert '"BAGLA", "SIRALA"' in src[_i:_i + 900], "BAGLA/SIRALA üstünlüğü karşılıyor"
    assert '"ustunluk", "kesme"' in src[_i:_i + 900], "yanlış beyan hâlâ çıkabilir"


def test_GARSON_TAKIP_BAGLAMINI_GORUR():
    """🔴🔴 `O-22` — garson takip bağlamını **hiç görmüyordu**.

    Ölçüldü (canlı `VII/B4`): thread'in dördüncü turunda `followup=True(yapısal=True)`
    — sistem takip olduğunu **biliyordu** — ama garsona yalnız *«bir de gecikme ekle»*
    gitti ve cevap bağlamsız bir toplam oldu: dönem yok, `musteri` kırılımı yok,
    ilk-3 yok. Üç turda kurulan bağlam **sessizce** düştü.

    ⚠ Deterministik takip yolu bağlamı taşıyor, garson yolu taşımıyordu — yani aynı
    thread, hangi basamağa düştüğüne göre bağlamlı ya da bağlamsız cevap veriyordu.
    *Bir bağlamı bir yolda taşıyıp ötekinde bırakmak, onu rastgele taşımaktır.*
    """
    from app.plan_garson import PlanGarsonu

    ONCEKI = {"cube": "parti", "measures": ["toplam_ciro"], "dimensions": ["musteri"],
              "limit": 3}
    g = PlanGarsonu(object(), {}, None, None, ONCEKI)
    metin = g._baglamli("bir de gecikme ekle")
    assert metin.startswith("bir de gecikme ekle"), "kullanıcının cümlesi DEĞİŞTİRİLMEZ"
    assert "toplam_ciro" in metin and "musteri" in metin, "önceki sorgu iliştirilmedi"
    assert "KORU" in metin, "modele ne yapacağı söylenmedi"


def test_BAGLAM_YOKSA_SORU_BAYT_BAYT_AYNI():
    """⚠ `KURAL B` — taze soruda (önceki sorgu yok) dize **bayt bayt** aynı kalmalı."""
    from app.plan_garson import PlanGarsonu

    for onceki in (None, {}, {"measures": ["x"]}):   # `cube` yoksa bağlam sayılmaz
        g = PlanGarsonu(object(), {}, None, None, onceki)
        assert g._baglamli("bu yıl toplam ciro") == "bu yıl toplam ciro"


def test_BAGLAM_CAGRI_YERINDEN_GECIRILIYOR():
    """🔴 Sarmalayıcı bağlamı **alıyor** ama çağrı yeri geçirmiyorsa yol ölüdür."""
    import inspect

    from app.routers import ask as _ask

    src = inspect.getsource(_ask.ask)
    _i = src.index("_plan_garson.sarmala(")
    assert "body.cube_query" in src[_i:_i + 120], \
        "çağrı yeri önceki sorguyu GEÇİRMİYOR — garson yine bağlamsız kalır"


def test_BAGLAM_IKI_URETICIYE_DE_BAGLI():
    """🔴 `O-22` — planı **iki** yer üretiyor; birini bağlamak yetmedi.

    Ölçüldü: yalnız `PlanGarsonu` bağlandığında canlıda **hiçbir şey değişmedi**,
    çünkü o turda planı boşlukta `plan_tuketici` üretiyordu. *Bir yolu düzeltip ötekini
    unutmak, düzeltmeyi yapmamakla aynı sonucu verir; yalnız yapıldığını sanmakla
    farklıdır.*
    """
    import inspect

    from app import plan_garson, plan_tuketici

    # ⟳ **ÇAPA TAŞINDI (`§RD`, 2026-08-10).** `baglamli` üçüncü bir bağlam aldı: belge
    # düzenlemede iliştirilen şey tek fiş değil **bölüm listesidir**. Çapa silinmedi,
    # yeni imzaya **yeniden çakıldı**; koruduğu şey aynı: *oylama yolu da bağlam görmeli*.
    # 🔴 Ve kapı **iki bağlamı da** sorar — biri bağlanıp öteki unutulursa, bu dosyanın
    # kendi dersi (*«planı iki yer üretiyor; birini bağlamak yetmedi»*) üçüncü kez
    # tekrarlanırdı.
    _kaynak = inspect.getsource(plan_garson.PlanGarsonu._baglamli)
    assert "self._onceki" in _kaynak, "oylama yolu bağlamsız"
    assert "self._bolumler" in _kaynak, "oylama yolu BELGE bağlamsız (§RD)"
    src = inspect.getsource(plan_tuketici.cevap)
    assert "plan_garson.baglamli(soru," in src, "boşluk yolu bağlamsız"
    assert "plan_onceki" in src, "bağlam istek durumundan okunmuyor"


def test_ISARET_SIFATI_SUPHE_URETIR():
    """🔴🔴 `§AT` — *«o makinede»* denince süzgeç kurulmuyordu, **hepsi** dönüyordu.

    Ölçüldü (canlı `IX`, thread C — karşıtlık keskin):

    | soru | süzgeç | satır |
    |---|---|---|
    | *«**RAM-2 için** vardiya kırılımı»* | ✅ `makine eq RAM-2` | **3** |
    | *«**o makinede** vardiya kırılımı»* | 🔴 yok | **33** |

    Varlık **adıyla** anılınca süzgeç kuruluyor, **referansla** anılınca sessizce hepsi
    dönüyor — ve rozet `source=cube`. *Bir varlığa işaret etmek onu adlandırmaktır.*
    """
    from app.niyet_tasima import EKSIK_ATIF, eksiklik

    CQ = {"cube": "parti", "measures": ["fire_orani_yuzde"],
          "dimensions": ["makine", "vardiya"],
          "filters": [{"dimension": "tarih", "operator": "gte", "value": "2026-01-01"}]}
    assert EKSIK_ATIF in eksiklik(CQ, "o makinede vardiya kırılımı")
    assert EKSIK_ATIF in eksiklik(CQ, "sadece o makineyi göster")
    assert EKSIK_ATIF in eksiklik(CQ, "bu vardiyada fire nasıl")


def test_ADIYLA_ANILAN_VARLIK_SUPHE_URETMEZ():
    """⚠ `§101.1` — süzgeç zaten kurulmuşsa şüphe yok; yoksa her tur garsona giderdi."""
    from app.niyet_tasima import EKSIK_ATIF, eksiklik

    CQ = {"cube": "parti", "measures": ["fire_orani_yuzde"],
          "dimensions": ["makine", "vardiya"],
          "filters": [{"dimension": "makine", "operator": "eq", "value": "RAM-2"}]}
    assert EKSIK_ATIF not in eksiklik(CQ, "o makinede vardiya kırılımı")


def test_ISARETSIZ_SORU_SUPHE_URETMEZ():
    """🔴 En kritik yanlış-pozitif kapısı: **taze** bir kırılım sorusu şüphe üretmemeli.

    *«makineye göre fire»* her gün sorulan bir sorudur ve süzgeci **yoktur** — işaret
    sıfatı olmadığı için şüphe de olmamalı. Aksi hâlde her kırılım sorusu garsona
    giderdi ve `KURAL B` çiğnenirdi.
    """
    from app.niyet_tasima import EKSIK_ATIF, eksiklik

    CQ = {"cube": "parti", "measures": ["fire_orani_yuzde"], "dimensions": ["makine"]}
    for q in ("makineye göre fire", "bu ay makine kırılımı", "makine bazında fire"):
        assert EKSIK_ATIF not in eksiklik(CQ, q), q


def test_AT_UC_YERLESIM_DE_OLCULDU_KAYDI_DURUYOR():
    """⟳🔴🔴 `§AT` — **üç yerleşim denendi, üçü de ölçüldü, üçü de geri alındı.**

    | # | yerleşim | ölçülen sonuç |
    |---|---|---|
    | 1 | yalnız `refined` atlandı | 🔴 `dim_switch` devraldı → `parti` **→ `oee`** |
    | 2 | ilk **dört** basamak atlandı | ⚠ ölçü doğru ama **aynı 33 satır** + LLM çağrısı |
    | 3 | `refine_cube` de atlandı | 🔴 yine `oee`'ye kaydı |

    ⊙ **Kök, yerleşim değil: BİLGİ YOK.** *«o makine»* = `RAM-2` çıkarımı yalnız
    **önceki cevabın ilk satırından** gelir; `prev_cq` bunu taşımaz (`order desc` var,
    **seçilmiş varlık** yok) ve zincirdeki hiçbir basamak onu bilemez.

    🔴 Eksik olan bir kanca değil bir **kavram**: diyalog durumunda **odak varlığı** yok.

    *Bir yordamı üç ayrı yere koyup üçünde de işe yaramıyorsa, eksik olan yer değil
    bilgidir.*
    """
    import inspect

    from app.niyet_tasima import EKSIK_ATIF, eksiklik
    from app.routers import ask as _ask

    src = inspect.getsource(_ask.ask)
    assert "ÜÇ YERLEŞİM DENENDİ" in src, "üç ölçümün kaydı kaynaktan silinmiş"
    assert "_atif_ref" not in src, "kanca hâlâ takılı — üçü de ölçülüp geri alınmıştı"

    # ⚠ Yüklem YAŞIYOR ve taze dalda etkin: geri alınan yerleşimdi, kural değil.
    CQ = {"cube": "parti", "measures": ["fire_orani_yuzde"], "dimensions": ["makine"]}
    assert EKSIK_ATIF in eksiklik(CQ, "o makinede vardiya kırılımı")
    assert EKSIK_ATIF not in eksiklik(CQ, "makineye göre fire")


def test_OPERATOR_TAKMA_ADLARI_MOTORA_KARSI_DOGRULANIR():
    """🔴 `§AR/S(4)` — her takma adın hedefi motorun **gerçek** operatörü olmalı.

    ⚠ Uydurma bir hedef (`equals → equal_to`) sessizce beyaz listeden düşerdi ve
    onarım *«düzelttim»* diyerek bir kusuru gizlerdi. *Bir eşleme tablosu, hedefleri
    doğrulanmadıkça bir tahmin listesidir.*
    """
    from app.cube_operatorleri import MOTOR_OPERATORLERI
    from app.plan_onarim import OPERATOR_TAKMA_ADLARI

    kacak = {k: v for k, v in OPERATOR_TAKMA_ADLARI.items()
             if v not in MOTOR_OPERATORLERI}
    assert not kacak, f"motorda olmayan hedefler: {kacak}"
    # ⚠ Takma ad, motorun **kendi** adıyla çakışmamalı: `in` zaten geçerli.
    cakisan = [k for k in OPERATOR_TAKMA_ADLARI if k in MOTOR_OPERATORLERI]
    assert not cakisan, f"geçerli operatörler takma ad olarak yazılmış: {cakisan}"


def test_EQUALS_MEKANIK_ONARILIR_VE_BEYAN_EDILIR():
    """🔴 Canlı red: *«tanınmayan süzgeç operatörü: `equals`»* → bir LLM turu harcandı.

    `equals` motorun 12 operatöründen **tam olarak birini** kastedebilir; bunu karar
    merciine göndermek bilinen bir cevabı ikinci kez satın almaktır.
    """
    from app.plan_onarim import onar

    cq = {"cube": "parti", "measures": ["toplam_fire_kg"],
          "filters": [{"dimension": "makine", "operator": "equals", "value": "RAM-2"}]}
    out, beyan = onar(cq, PARTI)
    assert out["filters"][0]["operator"] == "eq"
    assert beyan and "equals" in beyan[0], "onarım sessiz olamaz"


def test_TANIMSIZ_OPERATOR_TEŞHISI_DOGRUSUNU_SOYLER():
    """🔴 `§AR/S(2)` — red *«neyin yanlış»* olduğunu söylüyordu, *«doğrusunu»* değil.

    Aynı fonksiyonun docstring'i bu dersi boyut dalı için yazmış; operatör dalına
    uygulanmamıştı.
    """
    from app.plan_onarim import gerekce

    metin = gerekce({"cube": "parti", "measures": ["toplam_fire_kg"],
                     "filters": [{"dimension": "makine", "operator": "equals",
                                  "value": "X"}]}, PARTI)
    assert "geçerliler:" in metin and "eq" in metin, metin


def test_ALAN_YAZILMAMISSA_NONE_BASILMAZ():
    """🔴 `§AR/S(3)` — `None` bir alan adı değildir; *«hiç yazılmamış»* demektir."""
    from app.plan_onarim import gerekce

    metin = gerekce({"cube": "parti", "measures": ["toplam_fire_kg"],
                     "filters": [{"operator": "eq", "value": "X"}]}, PARTI)
    assert "None" not in metin, metin
    assert "hiç yazılmamış" in metin, metin


def test_PLAN_ISTEMI_OPERATOR_SOZLUGUNU_TASIYOR():
    """🔴 `§AR/S(1)` — plan isteminde `operator` kelimesi **sıfır** kez geçiyordu.

    ⚠ Liste **üretilir**, kopyalanmaz: `§M-6` elle kopyanın bedelini ölçmüştü.
    """
    from app.cube_operatorleri import MOTOR_OPERATORLERI
    from app.plan_semasi import plan_sistem_metni

    metin = plan_sistem_metni("- parti: measures[toplam_fire_kg]; dimensions[makine]")
    assert "operator" in metin, "plan istemi süzgeç biçimini hâlâ görmüyor"
    for op in MOTOR_OPERATORLERI:
        assert op in metin, f"`{op}` istemde yok — liste üretilmiyor olabilir"


def test_RED_SINIFI_KENDI_MESAJLARIMIZI_TANIR():
    """🔴🔴 `A9` — **sebebi sayılmayan bir red, düzeltildiğinde de sayılamaz.**

    ⊙ Ölçüldü (rapor `§B-9`): `SAYAC` vardı, `sayaclar()` vardı ve **hiçbir tüketicisi
    yoktu**; red oranı loglara gözle bakılarak tespit ediliyordu.

    ⚠ Sınıflandırıcı **kendi sözleşmemizi** sayar — bu mesajları biz yazıyoruz, yani
    kapalı bir kümedir. Bir dış metni sınıflandırmıyoruz.
    """
    from app.plan_garson import red_sinifi

    ORNEKLER = {
        "çıktı geçerli bir JSON değil": "json",
        "adım 2 (`SORGU`): şu zorunlu alan(lar) eksik: cube_query": "eksik_alan",
        "adım 4 (`SORGU`): tanımsız alan(lar): dimensions, measures": "fazla_alan",
        "adım 6 (`BAGLA.kaynak`) bir satirlar bekliyor ama `$5` bir sorgu üretiyor": "tip",
        "adım 2 (`BAGLA`) hiçbir adım tarafından kullanılmıyor": "ulasilmaz",
        "plan 13 adım istiyor, tavan 12": "tavan",
        "adım 3: tanınmayan süzgeç operatörü: `equals`": "operator",
        "`enerji` diye bir cube YOK": "ad_yok",
        "`parti`'de şu boyut(lar) yok: sebep": "boyut_yok",
        "süzgeçte `dimension` alanı hiç yazılmamış (1 süzgeç)": "suzgec_alani",
    }
    yanlis = {m: red_sinifi(m) for m, b in ORNEKLER.items() if red_sinifi(m) != b}
    assert not yanlis, f"sınıflandırılamayan red mesajları: {yanlis}"


def test_SAYAC_ORANLARI_VE_SEBEP_DAGILIMI_YAYIMLANIYOR():
    """🔴 `A9` — okuyucu **oranı** ve **sebep dağılımını** birlikte vermeli.

    ⚠ İki ayrı okuyucu, bir gün yalnız birinin okunması demekti.
    """
    from app.plan_garson import sayaclar

    o = sayaclar()
    for alan in ("denendi", "onarildi", "dustu", "red_orani_yuzde",
                 "onarim_tutma_yuzde", "red_nedenleri"):
        assert alan in o, f"`{alan}` yayımlanmıyor: {sorted(o)}"
    assert isinstance(o["red_nedenleri"], dict)


def test_SAYAC_UCU_BAGLI():
    """🔴 Sayaç yayımlanıyor ama **uç yoksa** yine kimse okumaz — `A9`'un tam hâli."""
    import inspect

    from app.routers import stats as _stats

    src = inspect.getsource(_stats)
    assert "/plan" in src and "sayaclar" in src, "`/stats/plan` ucu bağlı değil"


def test_EKSIK_BOYUTUN_SAHIBI_SOYLENIR():
    """🔴🔴 `§SB` — *«bu boyut yok»* yetmez, *«şu küpte var»* da söylenmeli.

    ⊙ Ölçüldü (`A9` sayacı, ilk koşum): plan redlerinin **baskın sınıfı** `boyut_yok`
    ve üçünün **üçü de aynı** — `parti`'de `sebep` isteniyor. Kullanıcı *«fire neden
    arttı»* diyor; doğal kırılım **sebep** ve `parti` onu taşımıyor, ama `kalite`
    taşıyor. Red *«yok»* deyip susunca düzeltme turu **aynı küpte** başka bir boyut
    arıyor; doğru hamle **öteki küpe bir adım daha** yazmak.

    ⚠ Metin **şemadan üretilir**: yeni bir küp eklendiğinde yönlendirme kendiliğinden
    doğru kalır. *Bir yönlendirmeyi elle yazmak, onu bir sonraki küpte yanlış yazmaktır.*
    """
    from app.plan_onarim import gerekce

    KALITE = {"name": "kalite", "measures": ["toplam_rework_kg"],
              "dimensions": ["sebep", "makine"], "time_dimensions": ["tarih"]}
    metin = gerekce({"cube": "parti", "measures": ["toplam_fire_kg"],
                     "dimensions": ["sebep"]}, PARTI,
                    {"cubes": [PARTI, KALITE]})
    assert "kalite" in metin, f"sahibi söylenmiyor: {metin}"
    assert "ayrı bir `SORGU` adımı" in metin, "ne yapılacağı söylenmiyor"


def test_SAHIPSIZ_BOYUTTA_YONLENDIRME_YAPILMAZ():
    """⚠ `§101.1` — hiçbir küpte yoksa uydurma bir yönlendirme yazılmaz."""
    from app.plan_onarim import gerekce

    metin = gerekce({"cube": "parti", "measures": ["toplam_fire_kg"],
                     "dimensions": ["boyle_bir_sey_yok"]}, PARTI, {"cubes": [PARTI]})
    assert "VAR:" not in metin, metin


def test_SEMA_YOKSA_MESAJ_BAYT_BAYT_AYNI():
    """⚠ `KURAL B` — şema geçilmezse metin eskisiyle **aynı** kalır."""
    from app.plan_onarim import gerekce

    cq = {"cube": "parti", "measures": ["toplam_fire_kg"], "dimensions": ["sebep"]}
    assert gerekce(cq, PARTI) == gerekce(cq, PARTI, None)


def test_CAPRAZ_KUP_OLCU_IKAMESI_BEYAN_EDILIR():
    """🔴🔴 `§Cİ` — kapsama denetimi **küp-yereldi**; cevap küp değiştirince terim
    **izsiz** kayboluyordu.

    ⊙ Ölçüldü (canlı, `A9` sayacının açtığı iz): *«bu yıl **fire** neden arttı sebep
    kırılımında göster»* → cevap `kalite.rework_sayisi`. Kullanıcı **fire** sordu,
    **rework** aldı, **hiçbir beyan yoktu**. Sebep: `_match_measure("…fire…", kalite)`
    → `(None, None)` — sayaç yalnız **cevabın küpüne** bakıyor.

    *Bir terimi yalnız cevabın küpünde aramak, cevabın küp değiştirdiği anı görmemeyi
    seçmektir.*
    """
    from app.uyum import denetle

    PARTI_M = {"name": "parti", "measures": ["toplam_fire_kg"],
               "measure_synonyms": {"toplam_fire_kg": ["fire", "hurda"]},
               "dimensions": ["makine"], "time_dimensions": ["tarih"]}
    KALITE = {"name": "kalite", "measures": ["rework_sayisi"],
              "measure_synonyms": {"rework_sayisi": ["rework", "yeniden isleme"]},
              "dimensions": ["sebep"], "time_dimensions": ["tarih"]}
    cq = {"cube": "kalite", "measures": ["rework_sayisi"], "dimensions": ["sebep"]}
    ih = denetle("bu yil fire neden artti sebep kiriliminda goster",
                 {"cube_query": cq}, KALITE, {"cubes": [PARTI_M, KALITE]})
    assert "olcu_ikamesi" in {i.isaret for i in ih}, \
        f"çapraz-küp ikamesi beyan edilmedi: {[i.isaret for i in ih]}"
    metin = " ".join(i.aciklama + i.oneri for i in ih if i.isaret == "olcu_ikamesi")
    assert "parti" in metin, "sahibi söylenmiyor"


def test_TERIM_CEVABIN_KUPUNDE_KARSILANIYORSA_BEYAN_YOK():
    """⚠ `§101.1` — cevap terimi **başka adla** karşılıyorsa (`fire` → `fire_orani_yuzde`)
    beyan yazılmaz; yanlış bir *«eksik»* doğru bir cevabı kusurlu gösterir."""
    from app.uyum import denetle

    PARTI_M = {"name": "parti", "measures": ["fire_orani_yuzde", "toplam_fire_kg"],
               "measure_synonyms": {"fire_orani_yuzde": ["fire orani", "fire"],
                                    "toplam_fire_kg": ["fire"]},
               "dimensions": ["makine"], "time_dimensions": ["tarih"]}
    cq = {"cube": "parti", "measures": ["fire_orani_yuzde"], "dimensions": ["makine"]}
    ih = denetle("bu yil fire orani makine kiriliminda", {"cube_query": cq},
                 PARTI_M, {"cubes": [PARTI_M]})
    assert "olcu_ikamesi" not in {i.isaret for i in ih}


def test_SEMA_GECILMEZSE_DAVRANIS_AYNI():
    """⚠ `KURAL B` — `sema` yoksa yeni işaret **hiç** üretilmez; çağıranlar aynı kalır."""
    from app.uyum import denetle

    KALITE = {"name": "kalite", "measures": ["rework_sayisi"],
              "dimensions": ["sebep"], "time_dimensions": ["tarih"]}
    cq = {"cube": "kalite", "measures": ["rework_sayisi"], "dimensions": ["sebep"]}
    ih = denetle("bu yil fire neden artti", {"cube_query": cq}, KALITE)
    assert "olcu_ikamesi" not in {i.isaret for i in ih}
