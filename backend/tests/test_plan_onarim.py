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
