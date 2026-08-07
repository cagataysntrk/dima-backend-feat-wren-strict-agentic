"""FAZ 3a — ŞEMA-KISITLI ÇIKTI: hatayı SONRASINDA reddetmek yerine ÖNCESİNDE engelle.

## Kapatılan kayıp (plan §2.2 / §4.6b-C)

Bugünkü akış: *"serbest JSON iste, sonra `parse_cube_query` ile REDDET"*. Reddedilen her
sorgu bir **Discovery'ye düşüştür** — kayıp, hatanın SONRASINDA kapatılıyor. Bu şema
hatayı ÖNCESİNDE engeller: model geçersiz bir ad üretmek için şemanın dışına çıkmalı.

## İki tasarım kararı, ikisi de bu dosyanın kilitlediği

**1. Enum CUBE'A GÖRE daralır.** Düz bir `{"measures": {"enum": [tüm 81 ölçü]}}` çapraz
sızıntı üretirdi: model `parti` seçip `oee`'nin ölçüsünü isteyebilirdi — yapısal olarak
"geçerli", semantik olarak saçma, `parse_cube_query` yine reddederdi. Kısıt hiçbir işe
yaramazdı. `oneOf` ile her cube kendi dalını taşır.

**2. `cube:null` REDDETME DALI KORUNUR — en önemli madde.** Şema-kısıtlı çıktının klasik
tuzağı modeli **geçerli ama yanlış** bir seçime ZORLAMAKtır: seçenekler arasında "hiçbiri"
yoksa model illa birini seçer. Bu, sistemin en pahalı hata sınıfını (§6.1 sessiz-yanlış)
ÜRETİRDİ — yani kısıt, düzeltmeye çalıştığı şeyi büyütürdü.

## Ölçüm dürüstlüğü

Bu ortamda gerçek bir LLM sağlayıcı YOK (`RuleBasedSqlGenerator`). Planın kabul kapısı
*"whitelist reddi oranı ölçülüp DÜŞÜŞÜ doğrulanır"* bu koşumda **KARŞILANAMAZ** ve
karşılanmış gibi gösterilmiyor. Burada kilitlenen şey **mekanizmanın kendisi**: şemanın
doğruluğu, yedek yolun çalışması, bayrağın kapatabilmesi. Oranın ölçümü Faz 0.5'in
`--live` modunun işidir; red artık **loglanıyor** ki ölçülebilsin (eskiden SESSİZDİ).
"""

from __future__ import annotations

import pytest

from app import cube_router as cr


@pytest.fixture(scope="module")
def index(schema):
    _, idx = cr.build_catalog(schema)
    return idx


@pytest.fixture(scope="module")
def sema(index):
    return cr.cube_query_json_schema(index)


@pytest.fixture(scope="module")
def sema_harman(index):
    """🔴 `G6.5` — `referans_dili` AÇIKKEN üretilen şema. Ayrı bir fixture olması
    kill-switch'in kanıtıdır: `sema` (varsayılan) ile aralarındaki tek fark `blend`."""
    return cr.cube_query_json_schema(index, harman=True)


def _dal(sema, ad):
    return next((d for d in sema["oneOf"] if d.get("title") == ad), None)


# --- REDDETME YOLU: en önemli madde ---------------------------------------------

def test_CEVAPLANAMAZ_dali_VAR(sema):
    """Seçenekler arasında "hiçbiri" yoksa model illa birini seçer — kısıt, düzeltmeye
    çalıştığı sessiz-yanlışı BÜYÜTÜRDÜ."""
    d = _dal(sema, "cevaplanamaz")
    assert d is not None, "cube:null dalı yok — model reddetmeye ZORLANAMIYOR"
    assert d["properties"]["cube"] == {"type": "null"}
    assert d["required"] == ["cube"]


def test_CEVAPLANAMAZ_dali_ILK_sirada(sema):
    """Sıra modele bir sinyaldir; reddetme seçeneği listenin dibine gömülmemeli."""
    assert sema["oneOf"][0].get("title") == "cevaplanamaz"


# --- ÇAPRAZ SIZINTI YOK ----------------------------------------------------------

def test_HER_CUBE_yalniz_KENDI_olculerini_listeler(schema, sema, index):
    """Düz bir enum, `parti` seçip `oee`'nin ölçüsünü istemeye izin verirdi."""
    for ad, spec in index.items():
        d = _dal(sema, ad)
        if d is None:
            continue
        assert set(d["properties"]["measures"]["items"]["enum"]) == set(spec["measures"])


def test_HER_CUBE_yalniz_KENDI_boyutlarini_listeler(sema, index):
    for ad, spec in index.items():
        d = _dal(sema, ad)
        if d is None or "dimensions" not in d["properties"]:
            continue
        assert set(d["properties"]["dimensions"]["items"]["enum"]) == set(spec["dimensions"])


def test_FILTRE_boyutu_da_KISITLI(sema, index):
    """Filtre `dimension`'ı serbest string olsaydı model orada uydurabilirdi."""
    for ad, spec in index.items():
        d = _dal(sema, ad)
        if d is None or "filters" not in d["properties"]:
            continue
        f = d["properties"]["filters"]["items"]["properties"]
        assert set(f["dimension"]["enum"]) == set(spec["dimensions"])


def test_ZAMAN_boyutu_ve_GRANULERLIK_kisitli(sema, index):
    for ad, spec in index.items():
        d = _dal(sema, ad)
        if d is None or "timeDimensions" not in d["properties"]:
            continue
        td = d["properties"]["timeDimensions"]["items"]["properties"]
        assert set(td["dimension"]["enum"]) == set(spec["time_dimensions"])
        assert td["granularity"]["enum"] == ["year", "quarter", "month", "week", "day"]


# --- KAPSAM: yalnız beş çekirdek alan --------------------------------------------

def test_ORDER_LIMIT_enumlanmaz_ama_BLEND_ENUMLANIR(sema, sema_harman, index):
    """🔴 `G6.5` — **TUZAK TERSİNE ÇEVRİLDİ, ve gerekçe ikiye AYRIŞTI.**

    Eski hâl üçünü bir arada tutuyordu: *"`parse_cube_query` zaten hoşgörüyle düşürüyor."*
    O gerekçe `order`/`limit` için doğru kalır — onlar cevabın **sunumunu** değiştirir.
    `blend` cevabın **kapsamını** değiştirir: düşünce kullanıcı iki seri ister, bir seri
    alır ve bunu **fark edemez** (denetimin `Ç-14` maddesi).

    ⊙ Ölçülen: harman **mutfakta çalışıyordu** (`blend_sql` + `cross_cube_add`) ama taze
    soruda ifade edilemiyordu — *"verimlilik ve ciro"* `{cube: null}`'a düşüyordu (`Ö11`).
    *Bir yeteneği söyleyememek, ona sahip olmamakla aynı sonucu verir.*
    """
    for d in sema_harman["oneOf"]:
        assert not ({"order", "limit"} & set(d.get("properties") or {}))
    if len(index) > 1:
        assert all("blend" in (d.get("properties") or {}) for d in sema_harman["oneOf"][1:]), (
            "🔴 `blend` cube dallarından düşmüş — `Ö11` yeniden bloke")
        assert sema_harman["oneOf"][0]["properties"].keys() == {"cube"}, (
            "🔴 REDDETME dalına alan eklenmiş: *hiçbiri* seçeneği koşulsuz kalmalı")

    # 🔴 KILL-SWITCH (`KURAL B`): bayrak kapalıyken şema **bugünküyle birebir**.
    # ⚠ Kapsam kaybı değil, kapsam **eskisi**: kapalı bir bayrağın yanından geçen tek
    # çağrı, bayrağı iptal eder — bu yüzden `harman` varsayılanı KAPALI.
    assert all("blend" not in (d.get("properties") or {}) for d in sema["oneOf"])
    assert "$defs" not in sema, "🔴 kapalı bayrak `$defs` sızdırıyor"


def test_BLEND_defs_ILE_kurulur_cunku_satir_ici_N_KARE(sema_harman, index):
    """🔴 Boyut bir tercih değil **zorunluluktu**: satır içi harman `N²` alt şema demekti.

    ⚠ Şema modele **her istekte** gönderilir; `N²` bir şema, kısıtın kazandırdığından
    fazlasını token olarak geri alır. `$defs` ile `N`'e iner ve ölçü enum'ları
    **cube'a göre dar** kalır (dal içi daralma kuralının aynısı)."""
    ogeler = sema_harman["$defs"]["harman_ogesi"]["oneOf"]
    assert len(ogeler) == len([a for a, s in index.items() if s.get("measures")])
    for o in ogeler:
        ad = o["properties"]["cube"]["const"]
        assert set(o["properties"]["measures"]["items"]["enum"]) == set(
            index[ad]["measures"]), f"🔴 {ad} harmanında ÇAPRAZ ölçü sızıntısı"


def test_BLEND_grain_UYUMUNU_sema_DEGIL_KAPI_dogrular(schema, index):
    """🔴 Sınır yazılı: şema *"hangi adlar"*ın, kapı *"birlikte anlamlı mı"*nın sahibi.

    Şema bir dalın öteki alanlarını göremez — bir cube'un o kırılımı taşıyıp taşımadığı
    ancak **tam sorgu** elde iken bilinir. `blend_sql`'in sözleşmesi bunu çağırandan
    ister; `G6.5`'ten önce garantiyi **tek** çağıran veriyordu ve yalnız `dimensions`
    için. *Bir garantiyi iki yerde vermek, bir gün yalnız birinde vermektir.*"""
    hedef = next(a for a, s in index.items() if s.get("dimensions"))
    boyut = index[hedef]["dimensions"][0]
    yabanci = next((a for a, s in index.items()
                    if a != hedef and boyut not in (s.get("dimensions") or [])
                    and s.get("measures")), None)
    if yabanci is None:
        pytest.skip("⊘ katalogda uyumsuz çift yok — vaka bayat")
    cq = {"cube": hedef, "measures": index[hedef]["measures"][:1],
          "dimensions": [boyut],
          "blend": [{"cube": yabanci, "measures": index[yabanci]["measures"][:1]}]}
    import json

    out = cr.parse_cube_query(json.dumps(cq), index)   # ⚠ METİN alır — şema-kısıtlı
    assert out and "blend" not in out, (
        f"🔴 {yabanci} `{boyut}` taşımıyor ama harmana girdi — o grain'de iki seri "
        f"FARKLI evrenlerden gelirdi")

    # ⚠ KARŞI YÖN — kapı her şeyi eleyerek de "yeşil" olabilirdi. Kırılımsız (yalnız
    # ölçü) bir harman **geçmeli**: paylaşılan anahtar yoksa uyumsuzluk da yoktur.
    # *Bir kapının kabul ettiği şeyi ölçmeden, reddettiği şey bir kanıt değildir.*
    acik = {"cube": hedef, "measures": index[hedef]["measures"][:1],
            "blend": [{"cube": yabanci, "measures": index[yabanci]["measures"][:1]}]}
    out2 = cr.parse_cube_query(json.dumps(acik), index)
    assert out2 and out2.get("blend"), "🔴 kapı uyumlu harmanı da eliyor — fazla dar"


def test_OLCUSUZ_cube_dal_ACMAZ(sema):
    """Ölçüsüz bir cube sorgulanamaz; dal açmak modele YANLIŞ bir seçenek sunardı."""
    for d in sema["oneOf"][1:]:
        assert d["properties"]["measures"]["items"]["enum"], d.get("title")


# --- ÜRETİLEN ŞEMA GERÇEKTEN parse_cube_query İLE UYUMLU MU ----------------------

def test_SEMAYA_UYAN_sorgu_parse_EDILIYOR(schema, sema, index):
    """En sert kapı: şemanın izin verdiği bir sorgu `parse_cube_query`'den GEÇMELİ.
    İkisi ayrışırsa model şemaya uyar, sistem yine reddeder — kısıt işe yaramaz."""
    import json

    for d in sema["oneOf"][1:]:
        ad = d["title"]
        cq = {"cube": ad, "measures": [d["properties"]["measures"]["items"]["enum"][0]]}
        if "dimensions" in d["properties"]:
            cq["dimensions"] = [d["properties"]["dimensions"]["items"]["enum"][0]]
        assert cr.parse_cube_query(json.dumps(cq), index) is not None, \
            f"{ad}: şema izin veriyor ama parse_cube_query reddediyor"


def test_KATALOG_DISI_ad_semada_YOK(sema):
    ham = str(sema)
    assert "uydurma_olcu" not in ham and "toplam_uydurma" not in ham


# --- YEDEK YOL + BAYRAK ----------------------------------------------------------

def test_SEMA_YOKSA_bugunku_yol(monkeypatch):
    """`sema=None` → bugünkü serbest-JSON çağrısı, birebir."""
    from app import llm as llm_mod

    cagrilar = []

    class _Sahte(llm_mod.AnthropicSqlGenerator):
        def __init__(self):  # noqa: D107 — istemci kurmadan davranış testi
            self._client, self._model, self._select_model = None, "m", "sm"

        def _ask(self, system, user, model=None):
            cagrilar.append("serbest"); return '{"cube":null}'

        def _arac_ile(self, system, user, sema):
            cagrilar.append("arac"); return '{"cube":null}'

    g = _Sahte()
    g.select_cube("s", "katalog")
    assert cagrilar == ["serbest"]


def test_ARAC_YOLU_patlarsa_SERBEST_JSONA_duser():
    """Sağlayıcı tool-use'u desteklemezse/patlarsa cevap KAYBOLMAMALI — ikisi de aynı
    `parse_cube_query`'ye varır, yani yedek yol zaten doğrulanmış."""
    from app import llm as llm_mod

    cagrilar = []

    class _Sahte(llm_mod.AnthropicSqlGenerator):
        def __init__(self):
            self._client, self._model, self._select_model = None, "m", "sm"

        def _ask(self, system, user, model=None):
            cagrilar.append("serbest"); return '{"cube":null}'

        def _arac_ile(self, system, user, sema):
            cagrilar.append("arac"); raise RuntimeError("tool-use yok")

    g = _Sahte()
    assert g.select_cube("s", "katalog", {"type": "object"}) == '{"cube":null}'
    assert cagrilar == ["arac", "serbest"]


def test_OPENAI_uyumlu_SEMAYI_kabul_eder_ama_KULLANMAZ():
    """`oneOf` OpenAI `strict` fonksiyon şemasında desteklenmiyor; kısıtı YARIM uygulamak
    uygulamamaktan KÖTÜDÜR (model geçerli ama yanlış bir dala zorlanabilirdi). İmza
    uyumlu kalır ki Failover ayrım yapmasın."""
    import inspect

    from app import llm as llm_mod

    sig = inspect.signature(llm_mod.OpenAICompatibleSqlGenerator.select_cube)
    assert "sema" in sig.parameters
    assert "KULLANILMAZ" in (llm_mod.OpenAICompatibleSqlGenerator.select_cube.__doc__ or "")


def test_FAILOVER_semayi_TASIYOR_ama_ESKI_uretece_de_calisir():
    """Şemayı kabul etmeyen (eski/üçüncü-parti) bir üreteç `TypeError` verir; Failover
    iki-argümanlı çağrıya düşmeli — karışım güvenli olmalı."""
    from app import llm as llm_mod

    class _Eski:
        def select_cube(self, question, catalog):  # sema YOK
            return '{"cube":null}'

    f = llm_mod.FailoverSqlGenerator.__new__(llm_mod.FailoverSqlGenerator)
    f._gens = [_Eski()]
    f._last = None
    assert f.select_cube("s", "k", {"type": "object"}) == '{"cube":null}'


def test_WHITELIST_REDDI_artik_LOGLANIYOR():
    """Planın §6 kapısı: *"whitelist reddi oranı ölçülüp düşüşü doğrulanır."* Bugün bu
    red SESSİZDİ — LLM bir cevap üretti, `parse_cube_query` düşürdü, geriye iz kalmadı.
    Ölçülemeyen bir kazanç doğrulanamaz."""
    import inspect

    from app.routers import ask as ask_mod

    govde = inspect.getsource(ask_mod._select_consistent)
    assert "whitelist REDD" in govde


# --- FAZ 9.13: KURAL B testi EKSİKTİ (bayraklı altı fazın tek istisnası) ----------
#
# ## Ölçülen boşluk (denetim, Faz 9)
#
# KURAL B: *"canlı cevap yolunu değiştiren her faz kendi kapatma bayrağını taşır; bayrak
# kapalıyken davranış BUGÜNKÜYLE BİREBİR AYNI olmalı ve bu TESTLE KİLİTLENMELİ."*
#
# Bayraklı altı fazın beşinde bu test vardı; **3a'da yoktu** — üstelik varsayılanı
# `beta`, yani **AÇIK**. En az korunan bayrak, en geniş açık olandı.

def test_BAYRAK_KAPALIYKEN_sema_URETILMIYOR(monkeypatch):
    """KURAL B'nin doğrudan ölçümü: kapalıyken `cube_query_json_schema` ÇAĞRILMAMALI —
    yalnız "sonuç aynı" değil, **yol da aynı** olmalı. Şema üretilip kullanılmasaydı
    bayrak kapalıyken de maliyet doğardı ve 'birebir aynı' iddiası çürürdü."""
    import inspect

    from app.routers import ask as ask_mod

    govde = inspect.getsource(ask_mod.ask)
    i = govde.index('"llm_sema_kisitli" in resolve_for')
    onceki = govde[max(0, i - 400):i]
    assert "_sema = None" in onceki, (
        "bayrak KAPALIYKEN `_sema` None kalmıyor olabilir — kill-switch yarım")
    # Şema üretimi bayrağın İÇİNDE olmalı; dışında olsaydı kapalıyken de koşardı.
    sonraki = govde[i:i + 500]
    assert "cube_query_json_schema(" in sonraki, "şema üretimi bayrağa BAĞLI değil"


def test_BAYRAK_KAPALIYKEN_SELECT_CONSISTENT_semasiz_cagriliyor():
    """`_select_consistent` şemayı SON argüman olarak alır; kapalıyken `None` gitmeli ve
    o yol bugünkü serbest-JSON yoludur (zaten `parse_cube_query`'ye varır)."""
    import inspect

    from app.routers import ask as ask_mod

    imza = inspect.signature(ask_mod._select_consistent)
    assert len(imza.parameters) >= 6, f"imza değişmiş: {list(imza.parameters)}"
    son = list(imza.parameters.values())[-1]
    assert son.default in (None, inspect.Parameter.empty), (
        "şema parametresi VARSAYILAN OLARAK DOLU — bayrak kapalıyken de kısıt uygulanır")


def test_VARSAYILAN_ASAMA_bilincli_bir_KARAR(monkeypatch):
    """Bayrak `beta` (açık) — bu meşru olabilir ama **kayıtlı** olmalı. `t2_anlatici`
    `off` çünkü sıcak yola LLM EKLİYOR; 3a ise var olan bir LLM çağrısını KISITLIYOR,
    yani riski azaltıyor. Ayrım burada yazılı kalsın ki bir sonraki okuyan tahmin etmesin.

    Kapı: aşama `off`/`alpha`/`beta`/`prod` dışına kayarsa ya da bayrak YAML'dan silinirse
    kırılır — sessiz bir varsayılan değişikliği olmaz."""
    import pathlib

    import yaml

    yol = pathlib.Path(__file__).resolve().parents[1] / "demo" / "packs" / "features.yml"
    veri = yaml.safe_load(yol.read_text(encoding="utf-8")) or {}
    blok = veri.get("features") or veri
    assert "llm_sema_kisitli" in blok, "bayrak YAML'dan silinmiş — kill-switch kayboldu"
    assert blok["llm_sema_kisitli"] == "beta", (
        f"varsayılan aşama değişmiş: {blok['llm_sema_kisitli']!r}. Bu bilinçli bir karar "
        "olmalı ve MIMARI §6.4z'de gerekçesiyle yazılmalı.")


def test_BAYRAK_ADMIN_PANELINDE_adli(monkeypatch):
    """FAZ 9.11 ile birlikte: bir kill-switch'i açacak kişi ne yaptığını OKUYABİLMELİ."""
    from app.features import FLAG_REGISTRY

    kayit = FLAG_REGISTRY.get("llm_sema_kisitli")
    assert kayit, "bayrak admin panelinde ADSIZ (`snake_case`, kategori 'Diğer')"
    assert kayit["label"] and kayit["description"] and kayit["category"] != "Diğer"


# --- 🔴 B5 — ŞEMA ÜRETİLİP ATILIYORDU ---------------------------------------------


def test_SAGLAYICI_YETENEGINI_KENDI_BEYAN_EDER():
    """🔴 Ölçüldü: aktif sağlayıcı (`openrouter` → `OpenAICompatibleSqlGenerator`) `sema`
    argümanını **hiç okumuyor** — kendi docstring'i söylüyor (*"BU SAĞLAYICIDA
    KULLANILMAZ"*). Ama `llm_sema_kisitli` bayrağı açık olduğu için `ask.py` şemayı **her
    istekte** kuruyordu: 23 cube'luk demoda ~**10.000 token**lık bir yapı, üretilip
    **atılıyor**.

    ⚠ Çözüm çağıranda bir `isinstance` **değil**: *aynı kuralın iki sahibi olmaz.* Bir
    sağlayıcının şema kullanıp kullanmadığını **kendisi** bilir.
    *Bir yeteneği dışarıdan tahmin etmek, onu iki yerde tanımlamaktır.*
    """
    from app.llm import AnthropicSqlGenerator, OpenAICompatibleSqlGenerator

    assert OpenAICompatibleSqlGenerator.sema_kullanir is False, (
        "🔴 `oneOf` desteklemeyen sağlayıcı şema kullanıyor diye beyan ediyor")
    assert AnthropicSqlGenerator.sema_kullanir is True, (
        "🔴 native tool-use'lu sağlayıcı şemayı kullanmıyor diye beyan ediyor")


def test_SEMA_YALNIZ_OKUYACAK_OLAN_ICIN_URETILIR():
    """⚠ **Fail-open:** bilinmeyen bir sağlayıcıda varsayılan `True` — şüphede şema
    üretilir ve davranış bugünküyle **birebir aynı** kalır. Bir optimizasyon, bilmediği
    bir sağlayıcıda yeteneği sessizce kapatmamalıdır."""
    import pathlib

    kaynak = (pathlib.Path(__file__).resolve().parents[1]
              / "app/routers/ask.py").read_text(encoding="utf-8")
    assert 'getattr(llm_probe, "sema_kullanir", True)' in kaynak, (
        "🔴 çağıran sağlayıcıya sormuyor ya da fail-open varsayılanı kaybolmuş")
