"""🔴 **KATALOG SÖZLÜĞÜ** — LLM'in gördüğü dünya, artık `route()`'un gördüğü kadar.

## Ölçülen kusur

Şema 23 cube'un **23'ünde** Türkçe eşanlam beyan ediyor (`synonyms` +
`measure_synonyms` + `dimension_synonyms`). `route()` bu katmanı **tam** kullanıyor.
LLM'e giden katalog metninde ise `verim` **0 kez**, `randiman` **0**, `verimlilik` **0**,
`hasılat` **0**, `bordro` **0** geçiyordu.

⊙ Canlı sonucu: *"verimlilik"* soran bir kullanıcı için **9/9 Intent çağrısı
`{"cube":null}`** döndü — oylama uyuşmazlığı değil, **aday yokluğu**.

> Mimari tersine dönmüştü: *en çok güvendiğimiz basamak, en kör hâliyle koşuyordu.*

## ⚠ `ADR-0008` ile çelişmiyor

Yasak olan **sözlük icat etmek**tir. Burada yeni bir liste yazılmıyor; şemanın **zaten
beyan ettiği** liste, ikinci tüketicisine gösteriliyor. *Bir bilgiyi beyan edip
tüketicilerinden birine göstermemek, onu iki kez tanımlamaya davettir.*
"""

from __future__ import annotations

import pytest

from app import katalog_metni as km


@pytest.fixture(scope="module")
def _iki(schema):
    sade, _ = km.build_catalog(schema)
    zengin, _ = km.build_catalog(schema, sozluk=True)
    return sade, zengin


def test_SEMA_ESANLAMI_BEYAN_EDIYOR_ve_bu_vaka_TAZE(schema):
    """⚠ Ölçüm önce: kapının konusu gerçekten var mı? Beyan yoksa test **boşuna yeşil**
    olurdu — bu dosyanın bütün iddiası o beyanın varlığına dayanıyor."""
    beyanli = [c["name"] for c in schema["cubes"] if c.get("measure_synonyms")]
    assert len(beyanli) >= 5, f"⊘ ölçü sinonimi beyan eden cube çok az: {beyanli}"


def test_ESANLAMLAR_ARTIK_KATALOGDA(schema, _iki):
    """🔴 Kapının **asıl** iddiası: şemadaki her ölçü sinonimi metne giriyor."""
    sade, zengin = _iki
    kayip_sade, kayip_zengin = [], []
    for c in schema["cubes"]:
        for _olcu, syns in (c.get("measure_synonyms") or {}).items():
            for s in (syns or [])[:3]:
                s = str(s).rstrip("!")
                if len(s) < 4:
                    continue
                (kayip_sade if s.lower() not in sade.lower() else []).append(s)
                if s.lower() not in zengin.lower():
                    kayip_zengin.append(f"{c['name']}:{s}")
    assert kayip_sade, "⊘ eski katalog zaten eşanlam taşıyor — kapının konusu bayat"
    assert not kayip_zengin, (
        f"🔴 sözlük açıkken hâlâ eksik: {kayip_zengin[:10]} — dedup fazla agresif olabilir")


def test_BAYRAK_KAPALIYKEN_BAYT_BAYT_BUGUNKU(schema, _iki):
    """`KURAL B`. Ve kapının bu yarısı ötekinden **daha** önemli: sözlük eki prompt'u
    büyütüyor, yani geri alma yolu bir tercih değil bir **maliyet vanası**."""
    sade, zengin = _iki
    assert "«" not in sade and "»" not in sade
    assert sade != zengin
    for c in schema["cubes"][:5]:
        assert km.cube_satiri(c, sozluk=False) == (
            f'- {c["name"]}: measures[{", ".join(c["measures"])}]'
            + (f'; dimensions[{", ".join(c["dimensions"])}]' if c.get("dimensions") else "")
            + (f'; time[{", ".join(c["time_dimensions"])}]' if c.get("time_dimensions") else ""))


def test_MALIYET_OLCULDU_ve_SINIRLI(_iki):
    """🔴 **Maliyet gizlenmiyor, kilitleniyor.** Sözlük eki metni büyütür; büyümenin
    **iki katı** aşması, sözlüğün kendi değerini yiyeceği eşiktir.

    ⚠ Bu bir kırpma kapısı **değil**: kırpma, kapatmaya çalıştığımız boşluğu o kelime için
    yeniden açardı. Bu bir **alarm**: katalog iki katına çıktıysa ya beyanlar şişmiştir ya
    dedup bozulmuştur — ikisi de bakılmayı hak eder.

    ⊙ Ve maliyet **sabit bir önektir** (soru başına değişmez) → önbellekleme borcu `B6`
    ödendiğinde tekrar etmeyen maliyete döner.
    """
    sade, zengin = _iki
    oran = len(zengin) / max(1, len(sade))
    # ⊙ ÖLÇÜLEN: 1,93× (12.115 → 23.417 karakter). Bant ölçümün ETRAFINA kondu, ölçüm
    # banda uydurulmadı — ilk yazımda `< 2.0` tahmindi ve **2,47×** ölçüldü. Sınırı
    # ölçüye çekmek ile ölçüyü sınıra çekmek arasındaki fark, bu deponun `gitas` dersidir.
    assert 1.5 < oran < 2.1, (
        f"🔴 sözlük eki katalogu {oran:.2f}× yaptı (beklenen ~1,93×). <1,5 ise sözlük "
        f"GİRMİYOR ya da bir kategori sessizce düşmüş; >2,1 ise boyut sinonimleri geri "
        f"gelmiş ya da dedup bozulmuş — ikisi de bakılmayı hak eder.")


def test_DEDUP_AYNI_TERIMI_IKI_KEZ_YAZMIYOR(schema):
    """Bir cube'un kendi sinonimi çoğu zaman ana ölçüsünün sinonimini tekrar eder
    (`oee` → hem cube hem `ort_oee`). İkinci kopya modele bir **vurgu** gibi okunur."""
    c = next((c for c in schema["cubes"]
              if c.get("synonyms") and c.get("measure_synonyms")), None)
    if c is None:
        pytest.skip("⊘ hem cube hem ölçü sinonimi olan cube yok")
    satir = km.cube_satiri(c, sozluk=True)
    terimler = [t.strip() for p in satir.split("«")[1:] for t in p.split("»")[0].split(",")]
    assert len(terimler) == len({t.lower() for t in terimler}), (
        f"🔴 tekrar eden terim: {satir[:200]}")


def test_INDEKS_BAYRAKTAN_ETKILENMIYOR(schema):
    """🔴 **Doğrulama sınırı bir prompt tercihine bağlanamaz.** `parse_cube_query`'nin
    beyaz listesi iki hâlde de birebir aynı olmalı — *bir kapının genişliği, kapıdan
    geçenin nasıl anlatıldığına bağlı olamaz.*"""
    _, i1 = km.build_catalog(schema)
    _, i2 = km.build_catalog(schema, sozluk=True)
    assert i1 == i2


def test_YENI_SOZLUK_YAZILMADI():
    """🔴 `ADR-0008`. Bu modül bir eşanlam **icat etmez**; şemadan okur. Gövdesinde
    Türkçe terim sabiti olsaydı, düzelttiğimiz kusurun ikinci sahibi doğardı."""
    import inspect

    src = inspect.getsource(km.cube_satiri) + inspect.getsource(km._ek)
    for yasak in ("verim", "randiman", "ciro", "bordro", "hasilat"):
        govde = [l for l in src.splitlines()
                 if l.strip() and not l.strip().startswith(("#", '"', "*"))]
        assert not any(f'"{yasak}' in l or f"'{yasak}" in l for l in govde), (
            f"🔴 `{yasak}` koda gömülmüş — sözlüğün sahibi ŞEMA olmalı")


def test_BAYRAGI_TEK_YERDE_COZUYORUZ():
    """*Bir bayrağı N yerde okumak, N−1 yerde okumaya giden yoldur.* `catalog_text` dört
    çağrı yerinde üretiliyor; dördü de `metin_ve_indeks`'ten geçmeli."""
    import pathlib

    from app.routers import ask as ask_mod

    src = pathlib.Path(ask_mod.__file__).read_text(encoding="utf-8")
    satirlar = [l for l in src.splitlines() if "build_catalog(" in l]
    metin_alan = [l for l in satirlar if "catalog_text" in l]
    assert not metin_alan, (
        f"🔴 `catalog_text` bayrağı atlayarak üretiliyor: {metin_alan} — o yol sözlüğü "
        f"göremeyen TEK yol olurdu")


def test_BOYUT_SINONIMLERI_BILEREK_DISARIDA(schema, _iki):
    """🔴 **Bir kapsam kararı — kırpma değil — ve ölçümle alındı.**

    | kapsam | katalog | oran |
    |---|---|---|
    | bugünkü | 12.115 | 1,00× |
    | + cube | 14.709 | 1,21× |
    | **+ ölçü** *(seçilen)* | **23.417** | **1,93×** |
    | + boyut | 29.889 | 2,47× |

    Boyut sinonimleri maliyetin **%30'unu** yiyor ama canlıda ölçülen kusuru
    (`{"cube":null}` — **cube seçimi**) çözmüyor: cube seçimini cube+ölçü sinonimleri
    taşır. Model boyut **adlarını** zaten görüyor ve onlar zaten Türkçe.

    ## ⚠ Bu kapı İKİ KEZ YANLIŞ YERE BAKTI — ve kaydı burada

    1. Önce **tüm metni** taradı: `durum`/`makine` boyut **ADI** olarak zaten basılıyor
       (ve basılmalı) → haksız kırmızı.
    2. Sonra yalnız `«…»` bloklarına baktı ama **tüm katalog** üzerinde: `equipment`
       `bakim`'ın boyut sinonimi, ama aynı zamanda `oee`'nin **ölçü** sinonimi
       (*"overall equipment effectiveness"*) → yine haksız kırmızı.

    🔴 Kanıt sonunda **kaynağa** taşındı: `cube_satiri` `dimension_synonyms`'a hiç
    bakmıyor. Bu ifade tektir, yanlış pozitif üretemez ve kararın kendisidir.
    ⊙ İkinci yön ölçüde: kategori geri gelirse oran **2,47×** olur ve bant kırmızı verir.

    *Bir kapının yanlış yerde araması, bulduğu şeyi kanıt olmaktan çıkarır.*
    """
    import inspect

    src = inspect.getsource(km.cube_satiri)
    govde = [l for l in src.splitlines()
             if l.strip() and not l.strip().startswith(("#", '"'))]
    assert not any("dimension_synonyms" in l for l in govde), (
        "🔴 boyut sinonimleri geri gelmiş — maliyet 1,93× → 2,47×. Karar değiştiyse "
        "`katalog_metni`'nin tablosunu ve bu kapıyı birlikte güncelle.")

    # ⚠ KARŞI YÖN: boyut **adları** basılmaya devam etmeli. Kategoriyi çıkarırken adları
    # da düşürmek, kapsamı daraltmak değil **bilgi silmek** olurdu.
    _, zengin = _iki
    c = next(c for c in schema["cubes"] if c.get("dimensions"))
    assert c["dimensions"][0] in zengin


def test_YARDIMCININ_IMZASI_EN_DAR_KAPSAMA_GORE(schema):
    """🔴 **Bir kapı bunu yakaladı ve kaydı burada.**

    İlk sürüm `metin_ve_indeks(schema, settings, principal)` diye zorunlu bir `settings`
    aldı. Dört çağrı yerinden **ikisinde o isim kapsamda yoktu** (`_prompt_enhance_dene`
    ve pilot dalı onu parametre almıyor); `NameError` çağıranın `except Exception`'ında
    **yutuldu** ve enhancer sessizce *"çözemedim"* demeye başladı.

    ⊙ Üç kapı kırmızıya döndü (`test_prompt_enhancer`) — yani kusur **bulundu**, ama
    doğduğu yerden üç fonksiyon ötede.

    *Bir yardımcının imzası, çağıranların en DAR kapsamına göre çizilir; aksi hâlde
    yardımcı, kaldırmaya çalıştığı tekrarı bir bağımlılığa çevirir.*
    """
    import inspect

    imza = inspect.signature(km.metin_ve_indeks)
    zorunlu = [a for a, p_ in imza.parameters.items()
               if p_.default is inspect.Parameter.empty]
    assert zorunlu == ["schema", "principal"], (
        f"🔴 zorunlu parametreler değişmiş: {zorunlu} — her yeni zorunlu argüman, onu "
        f"kapsamında taşımayan bir çağıranda SESSİZ bir NameError'dur")
    # Ve gerçekten `settings`siz çalışmalı:
    metin, idx = km.metin_ve_indeks(schema, None)
    assert metin and idx
