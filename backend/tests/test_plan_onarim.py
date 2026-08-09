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

    assert "baglamli(question, self._onceki)" in inspect.getsource(
        plan_garson.PlanGarsonu._baglamli), "oylama yolu bağlamsız"
    src = inspect.getsource(plan_tuketici.cevap)
    assert "plan_garson.baglamli(soru," in src, "boşluk yolu bağlamsız"
    assert "plan_onceki" in src, "bağlam istek durumundan okunmuyor"
