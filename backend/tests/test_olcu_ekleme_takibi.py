"""FAZ 4.3 borcunun kapanışı — **çıplak ikinci ölçü adı.** [bayrak: `olcu_ekleme_takibi`]

## Ölçülmüş borç

`lab/sharding.py`, `demo-boyahane`, **44 konuşmalık sabit kohort**:

| | tur 1 | tur 5 | düşüş | karar |
|---|---|---|---|---|
| bayrak **kapalı** *(bugün)* | %63,6 | **%45,5** | **−%18,2** | 🔴 `kaldi` |
| bayrak **açık** | %63,6 | **%59,1** | **−%4,5** | ✅ `gecti` |

Kaybedilen turların **tamamı** aynı şekle sahipti: takip mesajı **çıplak bir ikinci ölçü
adı**. Kök neden `deterministic_refine`'ın *"farklı metrik açıkça isteniyor"* varsayıp
zinciri terk etmesiydi — oysa *"bir de fire ekle"* **çalışıyordu**: mekanizma vardı,
**ipuçsuz hâli** yoktu.

## 🔴 Denetimin risk-1 şartı: kapı **benchmark + korpus BİRLİKTE**

> *"Çıplak ölçü adını tanıtmak, bugün **boyut** sanılan kelimeleri ölçüye çekebilir.
> Konuşma düzelirken katalog bozulursa **net zarardayız**."*

Korpus gerilemesi `lab/kapi.py --tam` ile demet sonunda ölçülür; bu dosya **davranışsal
sınırları** kilitler.
"""

from __future__ import annotations

import pytest

from app import cube_router as cr


@pytest.fixture(scope="module")
def _meta(schema):
    return next(c for c in schema["cubes"] if c["name"] == "parti")


def _prev(meta):
    olcu = (meta.get("measures") or ["toplam_fire_kg"])[0]
    return {"cube": "parti", "measures": [olcu], "dimensions": ["makine"]}


def _ikinci_olcu(meta, prev):
    for m in meta.get("measures") or []:
        if m not in prev["measures"]:
            return m
    pytest.skip("`parti` cube'unda ikinci ölçü yok")
    return ""


def test_BAYRAK_KAPALI_bugunku_davranis(schema, _meta):
    """🔴 KURAL B — kapalıyken **birebir bugünkü**: zincir terk edilir (`None`)."""
    prev = _prev(_meta)
    m2 = _ikinci_olcu(_meta, prev)
    ad = ((_meta.get("measure_synonyms") or {}).get(m2) or [m2])[0].removesuffix("!")
    assert cr.deterministic_refine(prev, cr._norm(ad), schema) is None, (
        "🔴 Bayrak KAPALIYKEN davranış değişmiş — GERİ AL sözleşmesi kırık.")


def test_BAYRAK_ACIK_olcu_EKLENIR(schema, _meta):
    prev = _prev(_meta)
    m2 = _ikinci_olcu(_meta, prev)
    ad = ((_meta.get("measure_synonyms") or {}).get(m2) or [m2])[0].removesuffix("!")
    cq = cr.deterministic_refine(prev, cr._norm(ad), schema, olcu_ekle=True)
    assert cq is not None, (
        f"🔴 `{ad}` hâlâ zinciri terk ediyor — 4.3 borcu kapanmamış.")
    assert cq["measures"] == [*prev["measures"], m2]


def test_EKLER_DEGISTIRMEZ(schema, _meta):
    """🔴 *Eklemek **geri alınabilir** bir yanlış anlamadır (kullanıcı ikisini de görür);
    değiştirmek **veri kaybıdır**.*"""
    prev = _prev(_meta)
    m2 = _ikinci_olcu(_meta, prev)
    ad = ((_meta.get("measure_synonyms") or {}).get(m2) or [m2])[0].removesuffix("!")
    cq = cr.deterministic_refine(prev, cr._norm(ad), schema, olcu_ekle=True)
    assert prev["measures"][0] in cq["measures"], "🔴 var olan ölçü DÜŞÜRÜLDÜ"
    # Kırılım ve şekil korunur.
    assert cq["dimensions"] == prev["dimensions"]


def test_DEGIL_YERINE_kalibi_EKLEMEYE_donusmez(schema, _meta):
    """⚠ *"Fire değil kâr"* bir **yer değiştirmedir** ve `swap` onu zaten yakalar.

    Ekleme dalı `değil`/`yerine` varken **ateşlememeli**: aksi hâlde kullanıcı
    *"istemediğini"* söylerken ürün onu **ekliyor** olurdu.
    """
    prev = _prev(_meta)
    m2 = _ikinci_olcu(_meta, prev)
    ad2 = ((_meta.get("measure_synonyms") or {}).get(m2) or [m2])[0].removesuffix("!")
    ad1 = ((_meta.get("measure_synonyms") or {}).get(prev["measures"][0])
           or prev["measures"][0])
    ad1 = (ad1[0] if isinstance(ad1, list) else ad1).removesuffix("!")
    cq = cr.deterministic_refine(prev, cr._norm(f"{ad1} degil {ad2}"), schema,
                                 olcu_ekle=True)
    if cq is not None:
        assert cq["measures"] == [m2], (
            f"🔴 `değil` kalıbında EKLEME yapıldı: {cq['measures']}. Kullanıcı "
            f"istemediğini söylerken ürün onu ekliyor.")


def test_AYNI_olcu_tekrar_EKLENMEZ(schema, _meta):
    """Zaten var olan bir ölçüyü tekrar eklemek, kolonu iki kez basar."""
    prev = _prev(_meta)
    ad = ((_meta.get("measure_synonyms") or {}).get(prev["measures"][0])
          or prev["measures"][0])
    ad = (ad[0] if isinstance(ad, list) else ad).removesuffix("!")
    cq = cr.deterministic_refine(prev, cr._norm(ad), schema, olcu_ekle=True)
    if cq is not None:
        assert len(cq["measures"]) == len(set(cq["measures"])), "ölçü iki kez eklendi"


def test_BASKA_CUBEUN_olcusu_EKLENMEZ(schema, _meta):
    """⚠ `_match_measure` `cube_meta`'ya bakar — başka bir cube'un ölçüsü **konu
    değişimidir**, ekleme değil."""
    prev = _prev(_meta)
    cq = cr.deterministic_refine(prev, cr._norm("bakiye"), schema, olcu_ekle=True)
    if cq is not None:
        assert all(m in (_meta.get("measures") or []) for m in cq["measures"]), (
            "🔴 Başka bir cube'un ölçüsü eklendi — konu değişimi ekleme sanıldı.")


def test_FONKSIYON_SAF_kaldi():
    """🔴 Bayrak **parametrede**, `get_settings()` çağrısında değil.

    İçine bir ayar okuması koymak, fonksiyonu test edilebilirlikten ve `lab/`
    araçlarının **A/B koşabilmesinden** ederdi — ve o A/B, bu borcun kapandığının **tek
    kanıtı**.
    """
    import ast
    from pathlib import Path

    agac = ast.parse((Path(__file__).resolve().parents[1] / "app/cube_router.py")
                     .read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "deterministic_refine")
    cagrilar = {getattr(c.func, "id", getattr(c.func, "attr", ""))
                for c in ast.walk(fn) if isinstance(c, ast.Call)}
    for yasak in ("get_settings", "resolve_for"):
        assert yasak not in cagrilar, (
            f"🔴 `deterministic_refine` `{yasak}` çağırıyor — saflık kayboldu ve "
            f"`lab/sharding.py` artık A/B koşamaz.")
    assert any(a.arg == "olcu_ekle" for a in fn.args.kwonlyargs)


def test_SHARDING_araci_AB_kosabiliyor():
    """Borcun kapandığı **iddia edilmez, ölçülür** — araç iki hâli de koşabilmeli."""
    import inspect

    from lab.sharding import konusma_kos, kos

    assert "olcu_ekle" in inspect.signature(kos).parameters
    assert "olcu_ekle" in inspect.signature(konusma_kos).parameters


# ─────────────────────────────────────────────────────────────────────────────
# 🔴 DENETİMİN §4/RİSK-1'İ GERÇEKLEŞTİ — ve iki kez daraltıldı
# ─────────────────────────────────────────────────────────────────────────────

def test_CAPRAZ_CUBE_konu_degisimi_EKLEME_sanilmaz(schema):
    """🔴 **Gerçek gerileme, altın süit tarafından yakalandı.**

    *"Kumaş cinsine göre fire oranı bu yıl"* bir **konu değişimidir** (`oee` → `parti`)
    ama içindeki `fire oranı` `oee`'nin de bir ölçüsü. İlk sürümde ekleme sanıldı ve
    **çapraz-cube geçişi kayboldu**.

    ⚠ Korpus bunu **görmedi** (%93,1 birebir). *Bir riskin ölçülmemesi, yokluğu
    değildir.*
    """
    meta = next(c for c in schema["cubes"] if c["name"] == "oee")
    prev = {"cube": "oee", "measures": [(meta.get("measures") or ["ort_oee"])[0]],
            "timeDimensions": [{"dimension": "tarih", "granularity": "month"}]}
    cq = cr.deterministic_refine(
        prev, cr._norm("kumas cinsine gore fire orani bu yil"), schema, olcu_ekle=True)
    if cq is not None:
        assert len(cq.get("measures") or []) == len(prev["measures"]), (
            "🔴 Konu değişimi ÖLÇÜ EKLEME sanıldı — çapraz-cube geçişi kaybolur.")


def test_BOYUT_tasiyan_mesaj_EKLEME_dali_ATESLEMEZ(schema, _meta):
    prev = _prev(_meta)
    m2 = _ikinci_olcu(_meta, prev)
    ad = ((_meta.get("measure_synonyms") or {}).get(m2) or [m2])[0].removesuffix("!")
    boyut = (_meta.get("dimensions") or ["makine"])[0]
    b_ad = ((_meta.get("dimension_labels") or {}).get(boyut) or boyut).replace("_", " ")
    cq = cr.deterministic_refine(prev, cr._norm(f"{ad} {b_ad} bazinda"), schema,
                                 olcu_ekle=True)
    if cq is not None:
        assert cq.get("measures") == prev["measures"], (
            "🔴 Boyut taşıyan bir mesaj shard atomu DEĞİLDİR — normal zincire aittir.")


def test_DONEM_tasiyan_mesaj_EKLEME_dali_ATESLEMEZ(schema, _meta):
    prev = _prev(_meta)
    m2 = _ikinci_olcu(_meta, prev)
    ad = ((_meta.get("measure_synonyms") or {}).get(m2) or [m2])[0].removesuffix("!")
    cq = cr.deterministic_refine(prev, cr._norm(f"{ad} bu yil"), schema, olcu_ekle=True)
    if cq is not None:
        assert cq.get("measures") == prev["measures"], (
            "🔴 Dönem taşıyan bir mesaj shard atomu DEĞİLDİR.")


def test_AYRIM_METINSEL_DEGIL_SEMANTIK():
    """🔴 İkinci daraltma **ölçümle** düzeltildi.

    İlk daraltmam *"sinonimi çıkar, kalan boş olsun"* diyordu ve **faydayı tamamen
    öldürdü**: atom `fire orani yuzde`, eşleşen sinonim `fire orani` → geriye `yuzde`
    kalıyor ve mesaj *"çıplak değil"* sayılıyordu. Ölçüldü: düşüş −%4,5'ten **−%18,2'ye
    geri döndü** — yani düzeltme, düzelttiği şeyi geri aldı.

    ⚠ Belirteç AST: ayrım **sinyal yokluğuna** bakmalı (`_match_dims` · `_time_gran` ·
    `_period_hit_words`), metin çıkarmaya değil.
    """
    import ast
    from pathlib import Path

    agac = ast.parse((Path(__file__).resolve().parents[1] / "app/cube_router.py")
                     .read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "_ciplak_olcu_adi")
    cagrilar = {getattr(c.func, "id", getattr(c.func, "attr", ""))
                for c in ast.walk(fn) if isinstance(c, ast.Call)}
    assert {"_match_dims", "_time_gran", "_period_hit_words"} <= cagrilar, (
        f"🔴 Ayrım semantik değil: {sorted(cagrilar)}. Metinsel çıkarma, sinonim ile "
        f"atomun birebir örtüşmediği her vakada yanlış karar verir.")
