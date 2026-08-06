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
