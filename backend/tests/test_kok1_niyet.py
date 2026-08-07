"""🔴🔴 KÖK-1 · **NİYET NESNESİ** — çözümleme ile eşleştirme ayrılsın. (FAZ 1)

## Raporun teşhisi

> *"KN-4 (uyum denetimi) **yazılamaz** çünkü karşılaştırılacak iki şey yok. KN-1
> **kaçınılmaz** çünkü taşınacak durum bir nesne değil."*

⊡ Ölçüldü: `app/`'de `Niyet` sınıfı **yoktu** ve o boşluk bu turda **beş ayrı yerde**
ayrı ayrı dolduruldu (`uyum` · `yetenek` · `donem_capasi` · `turetme` ·
`belirsizlik_chipi`). Beşi de aynı soruyu soruyor, beşi de kendi cevabını üretiyor —
deponun *"aynı kuralın iki sahibi"* sınıfının **beşe katlanmış** hâli.

## FAZ 1'in kapı ölçütü — raporun kendi cümlesi

> *"`Niyet` üretilir ve **loglanır**; `route()` davranışı **BİREBİR aynı** kalır.
> Kapı: `nl_corpus --kapi` sabit · `eval` `+0,0` · süit yeşil.
> **Sıfır gerileme, tam görünürlük.**"*

Bu dosya iki şeyi ölçer:
1. **Eşdeğerlik** — nesne, bugünkü dağınık okuyucularla **aynı şeyi** söylüyor mu?
   (Faz 2'de tüketiciler taşınırken kanıt bu olacak.)
2. **Sıfır müdahale** — nesne hiçbir kararı değiştirmiyor mu?

## 🔴 Ve nesnenin var olma sebebi ölçülebilir hâle geldi

`ocak ve haziran ciro karşılaştır` → `dönem=2 (çözülemedi)` · `🔴temsil-yok=cok_donem`.

Yani sistem artık **temsil edemediği şeyi SAYABİLİYOR**. `route()` bunu döndüremez
çünkü dönüş tipi taşıyamaz; `uyum` bunu bugün `cq` üzerinden **geriye doğru** çıkarmak
zorunda. *Bir sistemin temsil edemediği şeyi sayabilmesi, onu görebilmesinin ilk adımıdır.*
"""

from __future__ import annotations

import ast
import pathlib

import pytest

from app import niyet as n
from app import uyum
from app.cube_router import route

#: Raporun adıyla andığı temsil boşlukları.
TEMSIL_YOK = ["ocak ve haziran ciro karsilastir", "2025 ve 2026 ciro",
              "son 3 ay ve son 6 ay ciro"]

#: Bugün doğru çalışan ve bozulmaması gereken sorular.
CALISANLAR = ["bu yil makine bazinda oee", "bu yil toplam ciro",
              "en yuksek fire hangi makine", "son 6 ay ciro trendi",
              "mart ayinda fire orani"]


# ═══════════════════════════════════════════════════════════════════════════════
# 1 · EŞDEĞERLİK — nesne, dağınık okuyucularla AYNI şeyi söylüyor mu
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("q", TEMSIL_YOK + CALISANLAR)
def test_COK_DONEM_UYUMLA_AYNI(q, schema):
    """🔴 **Faz 2'nin kanıtı burada başlıyor.** `Niyet.cok_donem` ile `uyum._cok_donem`
    ayrışırsa, tüketiciyi taşımak bir davranış değişikliği olurdu.

    *Bir göçün ilk adımı, iki tarafın aynı şeyi söylediğini kanıtlamaktır.*"""
    assert n.coz(q, schema).cok_donem == (uyum._cok_donem(q) > 1)


@pytest.mark.parametrize("q", TEMSIL_YOK)
def test_TEMSIL_BOSLUGU_GORULUYOR(q, schema):
    """🔴 **Nesnenin var olma sebebi.** Soru iki dönem adlandırıyor, `CubeQuery` en
    fazla bir aralık taşıyabiliyor — ve bu artık **sayılabiliyor**."""
    niyet = n.coz(q, schema)
    assert niyet.donem_sayisi >= 2, f"🔴 «{q}» iki dönem taşıyor, nesne {niyet.donem_sayisi} sayıyor"
    assert "cok_donem" in niyet.temsil_edilemeyen
    assert "temsil-yok" in niyet.iz()


@pytest.mark.parametrize("q", CALISANLAR)
def test_CALISAN_SORUDA_TEMSIL_BOSLUGU_YOK(q, schema):
    """🔴 Kapının **asıl sınavı**: tek dönemli meşru sorular boşluk bildirmemeli.
    *Bir kapı, yakaladıklarıyla değil YANLIŞ yakaladıklarıyla sınanır.*"""
    assert not n.coz(q, schema).temsil_edilemeyen


def test_COZULEN_DONEM_SAYILIYOR(schema):
    """⚠ `_cok_donem` **adlandırılmış** dönemleri sayar; `bu yıl` gibi göreli bir dönemi
    saymaz. İkisi birleştirilmezse iz kendi verisiyle çelişirdi (`dönemler` dolu ama
    `dönem=0`). *Bir gözlem, gözlediği iki kaynağın ikisini de okumalıdır.*"""
    niyet = n.coz("bu yil toplam ciro", schema)
    assert niyet.donemler and niyet.donem_sayisi >= 1


def test_KIRILIM_UYUMLA_AYNI_YONDE(schema):
    """⚠ Kırılım okuması `_match_dims`ten gelir — `route()`'un kullandığı **aynı**
    fonksiyon. Ayrışırsa Faz 2'de kırılım tüketicisi taşınamaz."""
    assert "makine" in n.coz("bu yil makine bazinda oee", schema).kirilimlar
    assert not n.coz("bu yil toplam ciro", schema).kirilimlar


# ═══════════════════════════════════════════════════════════════════════════════
# 2 · SIFIR MÜDAHALE — Faz 1'in değişmez şartı
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("q", CALISANLAR + TEMSIL_YOK)
def test_ROUTE_DAVRANISI_DEGISMEDI(q, schema):
    """🔴 Raporun Faz 1 şartı: *"`route()` davranışı BİREBİR aynı kalır."*
    Nesne üretmek bir kararı değiştirmemeli — **iki kez çağırmak bile**."""
    once = route(q, schema)
    n.coz(q, schema)
    assert route(q, schema) == once, f"🔴 niyet çözümü «{q}» için route'u etkiledi"


def test_ROUTE_NIYETI_GORMUYOR():
    """🔴 **Yapısal güvence**: `cube_router` bu modülü import ETMEMELİ. Bir gün ederse
    Faz 1'in *"sıfır müdahale"* sözleşmesi sessizce delinmiş olur."""
    from app import cube_router as cr

    src = pathlib.Path(cr.__file__).read_text(encoding="utf-8")
    assert "app.niyet" not in src and "import niyet" not in src, \
        "🔴 route() niyet nesnesini görüyor — Faz 1 sözleşmesi delindi"


def test_NIYET_DEGISTIRILEMEZ():
    """⚠ `frozen`: niyet bir **okuma**dır, bir çalışma alanı değil. Değiştirilebilir
    olsaydı tüketiciler onu yerinde düzeltir ve *"kim değiştirdi"* sorusu doğardı —
    tam da bu nesnenin kapatmak için var olduğu belirsizlik."""
    import dataclasses

    with pytest.raises(dataclasses.FrozenInstanceError):
        n.Niyet(soru="x").soru = "y"          # type: ignore[misc]


# ═══════════════════════════════════════════════════════════════════════════════
# 3 · YENİ DİLBİLİM YAZILMADI — raporun açık şartı
# ═══════════════════════════════════════════════════════════════════════════════

def test_YENI_DILBILIM_YAZILMADI():
    """🔴 Raporun şartı: *"`_syn_hit` · `_covers` · `_ek_gecerli` · `compare_mode` —
    hepsi zaten var, dağınık. Yeni dilbilim **yazılmıyor**, var olan tek çatı altına
    alınıyor."*

    ⚠ AST ile taranır: bir `re.compile` ya da çıplak bir kalıp, bu nesneyi **altıncı
    bir sahip** yapardı — kapatmak için var olduğu şeyin ta kendisi."""
    kaynak = pathlib.Path(n.__file__).read_text(encoding="utf-8")
    agac = ast.parse(kaynak)
    kotu = [f"satır {d.lineno}" for d in ast.walk(agac)
            if isinstance(d, ast.Attribute) and d.attr in ("compile", "search",
                                                           "match", "findall", "finditer")]
    assert not kotu, f"🔴 niyet.py kendi dil kuralını yazıyor: {kotu}"
    assert "import re" not in kaynak, "🔴 `re` import edilmiş — çatı, sahip olmamalı"


def test_TUM_ALANLAR_MEVCUT_COZUMLEYICIDEN():
    """⚠ Her alanın bir sahibi olmalı ve o sahip **başka bir modülde** olmalı.
    `coz()` yalnız çağırır ve toplar."""
    kaynak = pathlib.Path(n.__file__).read_text(encoding="utf-8")
    for cagri in ("date_filters", "compare_mode", "liste_niyeti", "_time_gran",
                  "_top_n", "measure_cube_candidates", "partial_unknowns",
                  "_measure_threshold", "_match_dims", "_cok_donem"):
        assert cagri in kaynak, f"🔴 `{cagri}` çağrısı kaybolmuş — alan sahipsiz kaldı"


def test_IZ_TEK_SATIR():
    """⚠ Faz 1'in tek ürünü **görünürlük**. Çok satırlı bir iz, iz olmaktan çıkar."""
    iz = n.Niyet(soru="x", turler={n.TUR_TOPLAM}).iz()
    assert "\n" not in iz and iz.startswith("niyet:")


def test_COZUMLEYICI_PATLARSA_NIYET_DUSMEZ(schema, monkeypatch):
    """🔴 *Bir gözlemcinin, gözlediği şeyi düşürmesi gözlemin kendisinden pahalıdır.*
    Bir alan çözülemezse boş kalır; nesne yine üretilir."""
    from app import cube_router as cr

    monkeypatch.setattr(cr, "date_filters", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("x")))
    niyet = n.coz("bu yil toplam ciro", schema)
    assert niyet.donemler == [] and niyet.iz().startswith("niyet:")


def test_BAYRAK_KAPALIYKEN_TEK_SATIR_BILE_YOK(client, monkeypatch):
    """🔴 **GERİ AL bir kod değişikliği gerektirmez.** `niyet_izi` kapalıyken tek bir iz
    satırı bile eklenmemeli — Faz 1'in *"sıfır gerileme"* sözleşmesinin geri-alma yüzü."""
    from app import features
    from tests.conftest import ask

    acik = ask(client, "bu yıl toplam ciro")
    assert any("niyet:" in (t or "") for t in (acik.get("trace") or [])), \
        "⊘ vaka bayatlamış — bayrak açıkken de iz yok"

    gercek = features.resolve_for
    monkeypatch.setattr(features, "resolve_for",
                        lambda *a, **k: {f for f in gercek(*a, **k) if f != "niyet_izi"})
    kapali = ask(client, "bu yıl toplam ciro")
    assert not any("niyet:" in (t or "") for t in (kapali.get("trace") or [])), \
        "🔴 bayrak kapalıyken iz yazıldı"


def test_BAYRAK_KAYITLI_VE_VARSAYILAN_ACIK():
    """⚠ Bayrak `FLAG_REGISTRY`'de **kayıtlı** olmalı: kayıtsız bir bayrak yönetim
    yüzeyinde görünmez ve kimse onu kapatamaz. *Geri alınamayan bir geri alma
    mekanizması, mekanizma değildir.*"""
    import pathlib

    from app.features import FLAG_REGISTRY

    assert "niyet_izi" in FLAG_REGISTRY, "🔴 bayrak kayıtlı değil"
    yml = (pathlib.Path(__file__).resolve().parents[1]
           / "demo" / "packs" / "features.yml").read_text(encoding="utf-8")
    assert 'niyet_izi: "prod"' in yml, "🔴 varsayılan değer pack'te YAZILI değil"


# ═══════════════════════════════════════════════════════════════════════════════
# 4 · FAZ 2 — TÜKETİCİ GÖÇÜ, ve her adımın kanıtı
# ═══════════════════════════════════════════════════════════════════════════════

#: `uyum`un okuduğu **yedi** soru-sinyali ↔ `Niyet`in taşıdığı karşılıkları.
#: 🔴 Bu tablo Faz 2'nin **sözleşmesidir**: bir tanesi ayrışırsa o tüketici taşınamaz.
YEDI_SINYAL = [
    # 🔴 `G6` (2026-08-07) — BU SATIR GENİŞLEDİ, GEVŞEMEDİ.
    #
    # Eskiden `TUR_KIYAS ≡ compare_mode`'du. Ölçüldü ki `compare_mode` **göreli**
    # kıyastır (`yoy`/`mom`) ve *"mart cirosunu şubat ile kıyasla"*ya `None` der — o soru
    # **iki uçlu**dur. Sonuç: niyet nesnesi kıyası **saymıyordu**, `uyum` da oradan
    # okuduğu için susuyordu ve soru **1 Şubat–31 Mart TOPLAMIYLA** etiketsiz cevaplanıyordu.
    #
    # Sol taraf hâlâ **ham router yüklemleri**, sağ taraf hâlâ **niyet alanı** — testin
    # şekli aynı, kapsamı düzeltildi. `kiyas_niyeti` yeni bir sözlük değil, var olan
    # `_KIYAS_FIIL`'in yüklem hâlidir (`ADR-0008`).
    ("kiyas", lambda cr, uy, qn: bool(cr.compare_mode(qn)) or cr.kiyas_niyeti(qn),
     lambda n: n_mod.TUR_KIYAS in n.turler),
    ("cok_donem", lambda cr, uy, qn: uy._cok_donem(qn) >= 2, lambda n: n.cok_donem),
    ("trend", lambda cr, uy, qn: uy.trend_istendi(qn), lambda n: n.trend_istendi),
    ("kirilim", lambda cr, uy, qn: cr._herhangi(qn, cr._BREAKDOWN_HINTS),
     lambda n: n.kirilim_istendi),
    ("ustunluk", lambda cr, uy, qn: uy.ustunluk_istendi(qn), lambda n: n.ustunluk_istendi),
    ("esik", lambda cr, uy, qn: bool(cr._measure_threshold(qn)),
     lambda n: any(f.get("operator") not in ("gte", "lte") for f in n.filtreler)),
    ("dislama", lambda cr, uy, qn: cr._herhangi(qn, cr._EXCLUDE_MARKERS),
     lambda n: n.dislama_istendi),
]

import app.niyet as n_mod  # noqa: E402  (YEDI_SINYAL lambda'ları için)


def test_FAZ2_ESDEGERLIK(schema):
    """🔴 **FAZ 2'NİN KANITI.** `Niyet`, `uyum`un yedi soru-sinyalini **birebir** aynı
    okuyor mu — katalogdan üretilmiş geniş bir soru kümesinde?

    ⊙ Ölçüldü (2026-08-06): **2 270** soruda **7/7 AYNI**. Göç ancak bundan sonra
    yapıldı. *Bir göçün ilk adımı, iki tarafın aynı şeyi söylediğini kanıtlamaktır.*

    ⚠ Bu kapı Faz 2'nin **her** adımında koşar: yeni bir tüketici taşınmadan önce onun
    okuduğu sinyal bu tabloya eklenir ve burada eşdeğerliği ölçülür.
    """
    from app import cube_router as cr
    from app import uyum as uy

    sorular = []
    for c in schema["cubes"]:
        for m, syns in list((c.get("measure_synonyms") or {}).items())[:4]:
            t = (syns or [m])[0].removesuffix("!")
            dims = (c.get("dimensions") or [])[:1]
            sorular += [f"bu yıl {t}", f"ocak ve haziran {t} karşılaştır",
                        f"{t} değişimi son 6 ay", f"en yüksek {t}",
                        f"{t} 1000 üstü", f"beyaz hariç {t}"]
            if dims:
                sorular.append(f"bu yıl {dims[0]} bazında {t}")
    assert len(sorular) > 300, f"⊘ ölçüm tabanı çöktü: {len(sorular)} soru"

    fark: dict[str, tuple] = {}
    for q in sorular:
        qn = uy._norm(q)
        niyet = n_mod.coz_soru(q)
        for ad, eski, yeni in YEDI_SINYAL:
            if bool(eski(cr, uy, qn)) != bool(yeni(niyet)) and ad not in fark:
                fark[ad] = (q[:60], eski(cr, uy, qn), yeni(niyet))
    assert not fark, ("🔴 niyet ile uyum AYRIŞIYOR — bu tüketici taşınamaz:\n  "
                      + "\n  ".join(f"{k}: «{v[0]}» uyum={v[1]} niyet={v[2]}"
                                    for k, v in fark.items()))


def test_UYUM_SORUYU_ARTIK_KENDI_TARAMIYOR():
    """🔴 Göçün **yapısal** kanıtı: `denetle` soru tarafını `Niyet`ten okumalı.
    Eski tarayıcılar geri gelirse *"aynı kuralın iki sahibi"* de geri gelir."""
    import pathlib

    from app import uyum as uy

    # ⚠ AST — metin DEĞİL. Bu depoda bir kapı ÜÇÜNCÜ kez kendi belgelendirmesini
    # yakaladı: göçü ANLATAN yorum, göçün geri alındığı sanılmasına yol açtı.
    # Yorumlar ve docstring'ler AST'de yoktur; kapı yalnız ÇALIŞAN KODU görür.
    fn = _denetle_agaci(uy)
    kod = ast.unparse(fn)
    for eski in ("compare_mode(qn)", "_cok_donem(qn)", "_TREND.search(qn)",
                 "_BREAKDOWN_HINTS", "_EXCLUDE_MARKERS", "_measure_threshold(qn)"):
        assert eski not in kod, f"🔴 `denetle` soruyu yine kendi tarıyor: {eski}"
    assert "coz_soru" in kod, "🔴 `denetle` niyet nesnesini okumuyor"


def test_USTUNLUK_BILEREK_TASINMADI():
    """⊘ **SINIR — ve yazılı.** `_ustunluk_mu` `denetle` içinde `ic`+`cube_meta` ile
    çağrılır: ipucu bir **ölçü adının içindeyse** ipucu değildir (`kur` cube'unun ölçüsü
    literal olarak *"en yüksek kur"*; 525 meşru soruda **10** yanlış-pozitif buradan
    geliyordu).

    O denetim **eşleştirme** tarafıdır ve şemasız bir çözümlemede yapılamaz.
    *Ayrımın doğru yeri, ayrımın kendisi kadar önemlidir: yanlış yerden bölünen bir
    sorumluluk iki yerde de eksik kalır.*"""
    import pathlib

    from app import uyum as uy

    kod = ast.unparse(_denetle_agaci(uy))
    assert "_ustunluk_mu(qn, _TOPN_CUE, ic, cube_meta)" in kod, \
        "🔴 üstünlük denetimi cq-farkındalığını kaybetmiş — ölçü adı yanlış-pozitifi geri gelir"


def _denetle_agaci(uy):
    """`uyum.denetle`in AST gövdesi — **docstring'i çıkarılmış** hâliyle.

    ⚠ `ast.unparse` docstring'i korur; göçü ANLATAN docstring, göçün geri alındığı
    sanılmasına yol açardı. *Bir kapının baktığı metin, koruduğu şeyin kendisi olmalı;
    onun anlatısı değil.*
    """
    import pathlib

    agac = ast.parse(pathlib.Path(uy.__file__).read_text(encoding="utf-8"))
    fn = next(x for x in ast.walk(agac)
              if isinstance(x, ast.FunctionDef) and x.name == "denetle")
    govde = list(fn.body)
    if (govde and isinstance(govde[0], ast.Expr)
            and isinstance(govde[0].value, ast.Constant)):
        govde = govde[1:]
    return ast.Module(body=govde, type_ignores=[])


# ═══════════════════════════════════════════════════════════════════════════════
# 5 · İSTEK-KAPSAMLI BELLEK — Faz 2'nin ÖN KOŞULU
# ═══════════════════════════════════════════════════════════════════════════════

def test_BELLEK_AYNI_ISTEKTE_TEK_KEZ_COZUYOR():
    """🔴 **Faz 2'nin ön koşulu.** Ölçüldü: reddedilen bir soruda `partial_unknowns`
    **dört kez** koşuyordu. Niyet nesnesi *"tek çatı"* olacaksa çatıya girmek **ucuz**
    olmalı — aksi hâlde her yeni tüketici tam bir yeniden-çözümleme ekler ve tek çatı,
    dağınık okuyuculardan **pahalı** hâle gelir.

    *Bir soyutlamanın benimsenmesi, ona girmenin maliyetiyle ters orantılıdır.*"""
    n_mod.bellek_sifirla()
    sayac = {"n": 0}
    gercek = n_mod._coz_soru

    try:
        n_mod._coz_soru = lambda q: (sayac.__setitem__("n", sayac["n"] + 1),
                                     gercek(q))[1]
        for _ in range(3):
            n_mod.coz_soru("bu yil toplam ciro")
        assert sayac["n"] == 1, f"🔴 aynı istekte {sayac['n']} kez çözüldü"
    finally:
        n_mod._coz_soru = gercek


def test_BELLEK_ISTEK_SINIRINDA_SIFIRLANIYOR():
    """⚠ Kapsam **istek**tir, süreç değil. Süreç ömrü boyunca önbelleklemek, şema
    değiştiğinde **bayat** bir niyet üretirdi — ve bu operasyon bayat okumanın bedelini
    ölçtü (`tests/test_olcum_semasi_taze.py`)."""
    n_mod.bellek_sifirla()
    n_mod.coz_soru("bu yil toplam ciro")
    n_mod.bellek_sifirla()
    assert n_mod._BELLEK.get() == {}, "🔴 sıfırlama belleği boşaltmıyor"


def test_ISTEK_DISI_CAGRI_ONBELLEKSIZ_CALISIYOR():
    """⚠ Lab araçları ve testler istek bağlamı olmadan çağırır. `ContextVar` orada
    `LookupError` verir ve niyet **yine üretilmeli** — önbelleksiz, ama çalışır.
    *Bir hızlandırmanın yokluğu, bir çalışmama sebebi olamaz.*"""
    import contextvars

    def _izole():
        return n_mod.coz_soru("bu yil toplam ciro").iz()

    assert contextvars.Context().run(_izole).startswith("niyet:")


def test_TURETME_ARTIK_NIYETTEN_OKUYOR():
    """🔴 Faz 2 göçü — `_turetme_adaylari` `partial_unknowns`u DOĞRUDAN çağırmamalı.
    ⊙ Ölçüldü: reddedilen soruda toplam çağrı **4 → 3**."""
    import pathlib

    from app.routers import ask as ask_mod

    kaynak = pathlib.Path(ask_mod.__file__).read_text(encoding="utf-8")
    agac = ast.parse(kaynak)
    fn = next(x for x in ast.walk(agac)
              if isinstance(x, ast.FunctionDef) and x.name == "_turetme_adaylari")
    kod = ast.unparse(fn)
    assert "partial_unknowns" not in kod, \
        "🔴 türetme yine kendi çözümlemesini yapıyor — tek çatının maliyeti ikiye katlanır"
    assert "coz(" in kod, "🔴 niyet nesnesinden okumuyor"


def test_BELLEK_ISTEK_SINIRINA_BAGLI():
    """⚠ `bellek_sifirla()` `ask()`in girişinde, `reset_llm_usage()` ile **aynı yerde**
    olmalı: ikisi de istek-kapsamlı bir birikimi temizler. Unutulursa iki istek aynı
    niyeti paylaşır — *bir önbellek, sınırını kaybettiğinde bir hataya dönüşür.*"""
    import pathlib

    from app.routers import ask as ask_mod

    kaynak = pathlib.Path(ask_mod.__file__).read_text(encoding="utf-8")
    fn = next(x for x in ast.walk(ast.parse(kaynak))
              if isinstance(x, ast.FunctionDef) and x.name == "ask")
    kod = ast.unparse(fn)
    assert "bellek_sifirla()" in kod, "🔴 istek sınırında bellek sıfırlanmıyor"
    assert kod.index("bellek_sifirla()") < kod.index("q_norm"), \
        "🔴 sıfırlama çözümlemeden SONRA — bir önceki isteğin niyeti sızabilir"
