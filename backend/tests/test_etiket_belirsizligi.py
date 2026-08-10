"""🔴🔴 `§EB` — **ETİKETTEN TÜREYEN BELİRSİZ TOKEN SİNONİM OLAMAZ.**

## Ölçülen kusur (canlı `XII`, 2026-08-10)

*«**renk grubuna** göre fire bu yıl»* → kırılım **üç** boyut:

    dimensions: ["ham_grup", "renk", "yas_grubu"]

Kullanıcı **renk** sordu, cevaba **personel yaş grubu** girdi. Rozet `source=cube` —
deterministik yol — ve **hiçbir beyan yok**.

⊙ Sebep: `_with_label` etiketi kelimelere bölüp her birini sinonim yapıyor.
*«Ham Grubu»* → `ham`, **`grubu`**; *«Yaş Grubu»* → `yas`, **`grubu`**. Çıplak `grubu`
pack'te **yazmıyor** — sistem **kendisi üretiyor** ve iki ayrı boyuta veriyor.

*Hiçbir şeyi ayırt etmeyen bir ad, bir ad değildir.*
"""

from __future__ import annotations

from app.wren_service import _etiket_belirsizligini_ayikla as ayikla


def test_ETIKETTEN_TUREYEN_BELIRSIZ_TOKEN_DUSER():
    """🔴 Ölçülen vaka: `grubu` iki boyutun da etiketinden türemiş → ikisinden de düşer."""
    sin = {"ham_grup": ["ham grubu", "ham", "grubu"],
           "yas_grubu": ["yas grubu", "yas", "grubu"]}
    beyan = {"ham_grup": {"ham grubu"}, "yas_grubu": {"yas grubu"}}
    etiketten = {"ham_grup": {"ham grubu", "ham", "grubu"},
                 "yas_grubu": {"yas grubu", "yas", "grubu"}}
    out = ayikla(sin, beyan, etiketten)
    assert "grubu" not in out["ham_grup"], out["ham_grup"]
    assert "grubu" not in out["yas_grubu"], out["yas_grubu"]
    # ⚠ Ayırt eden token'lar KALIR — ayıklama bir kırpma değil bir süzme.
    assert "ham" in out["ham_grup"] and "yas" in out["yas_grubu"]
    assert "ham grubu" in out["ham_grup"] and "yas grubu" in out["yas_grubu"]


def test_PACKIN_BEYAN_ETTIGI_SINONIM_ASLA_DUSMEZ():
    """🔴 **Beyan bir karardır, türetme bir tahmindir.** Pack açıkça iki boyuta aynı
    sinonimi verdiyse bu bilinçlidir ve geri alınamaz.

    *Bir kararı bir tahmin yüzünden geri almak, karar verenin yerine geçmektir.*
    """
    sin = {"a": ["ortak", "a_ozel"], "b": ["ortak", "b_ozel"]}
    beyan = {"a": {"ortak"}, "b": {"ortak"}}          # ikisi de AÇIKÇA beyan etmiş
    etiketten = {"a": set(), "b": set()}
    out = ayikla(sin, beyan, etiketten)
    assert out["a"] == ["ortak", "a_ozel"] and out["b"] == ["ortak", "b_ozel"]


def test_BOYUTUN_KENDI_ADI_KORUNUR():
    """⚠ Bir boyutun **kendi adı** başka bir boyutun etiketinden de türemiş olabilir
    (`renk` ↔ `renk_derinlik`). Sahibinden düşürmek boyutu adsız bırakırdı."""
    sin = {"renk": ["renk"], "renk_derinlik": ["renk derinligi", "renk", "derinlik"]}
    beyan = {"renk": set(), "renk_derinlik": {"derinlik"}}
    etiketten = {"renk": {"renk"}, "renk_derinlik": {"renk derinligi", "renk"}}
    out = ayikla(sin, beyan, etiketten)
    assert "renk" in out["renk"], "boyut kendi adını kaybetti"
    assert "renk" not in out["renk_derinlik"], "belirsiz token ödünç alandan düşmeliydi"


def test_CARPISMA_YOKSA_SOZLUK_AYNEN_DONER():
    """⚠ `KURAL B` — çarpışma yoksa **aynı nesne** döner; bir şey yapmıyorsa iz bırakmaz."""
    sin = {"a": ["x"], "b": ["y"]}
    out = ayikla(sin, {"a": set(), "b": set()}, {"a": set(), "b": set()})
    assert out is sin


def test_CANLI_SEMADA_CARPISMA_KALMADI(schema):
    """🔴 Kapının asıl ölçüsü: **gerçek şemada** aynı küpte iki boyutun paylaştığı
    etiket-türevi token kalmamalı. ⊙ Düzeltmeden önce **altı** çarpışma vardı."""
    from collections import defaultdict

    kalan = []
    for c in (schema.get("cubes") or []):
        sahip = defaultdict(list)
        for d, syns in (c.get("dimension_synonyms") or {}).items():
            for s in (syns or []):
                sahip[str(s)].append(d)
        for s, ds in sahip.items():
            if len(ds) > 1:
                kalan.append(f"{c['name']}: «{s}» → {ds}")
    assert not kalan, (
        "🔴 Aynı küpte iki boyut aynı token'ı paylaşıyor — o token hiçbirini ayırt "
        "etmiyor ve her ikisini birden kırılıma sokuyor:\n  " + "\n  ".join(kalan))


def test_BOYUT_ADI_SINONIM_YAPILMADI_KAYDI_DURUYOR():
    """⟳🔴 `§EB/A` denendi, **ölçüldü, geri alındı.**

    Hipotez doğruydu (*«bir boyut kendi adıyla anılabilmeli»*) ama bedeli ölçüldü:
    ad **her boyut için** eklenince katalog açgözlü oldu ve gerçek-dünya korpusunda
    `sessiz_yanlis` **12 → 18**. `§99.1`'in birebir tekrarı — teknik adlar kullanıcının
    **konuşmadığı** kelimelerdir: kazandırdıkları nadir, çarptırdıkları sık.

    *Bir kesinlik kazanmak için bir belirsizlik satın alıyorsan, takasın yönünü sayıyla
    bilmen gerekir.*
    """
    import inspect

    from app import wren_service

    src = inspect.getsource(wren_service.WrenService.schema)
    assert "GERİ ALINDI" in src, "çürütmenin kaydı silinmiş"
    assert "[_norm(d[\"name\"])]," not in src, "ad yeniden sinonim yapılmış — korpus ölçtü"

def test_DUSEN_TOKEN_DAGARCIKTA_KALIR(schema):
    """🔴 `§EB/T` — düşen token **ayırt etmez ama tanınır**.

    ⊙ Ölçüldü: `grubu` sinonimden düşünce kapsam kapısı da onu kaybetti ve
    *«… yas_grubu bazında …»* → *«"grubu" başka bir konu gibi görünüyor»*.
    `partial_unknowns` *"bu kelime dağarcığımızda mı"* diye sorar; `_match_dimension`
    *"hangi boyutu adlandırıyor"* diye. İkisini aynı listeden okumak, **tanınabilir**
    ile **ayırt edici**yi bir saymaktı.

    *Bir kelimeyi tanımak ile onunla bir şeyi seçmek aynı yetenek değildir.*
    """
    tokenli = [c["name"] for c in (schema.get("cubes") or [])
               if c.get("belirsiz_boyut_tokenlari")]
    assert tokenli, ("hiçbir küpte düşen token yok — ya ayıklama koşmuyor ya alan "
                     "şemaya yazılmıyor; `§EB` sessizce ölmüş olurdu")
    from app.cube_router import partial_unknowns

    # ⚠ Yüklem **ölçülen vakaya** bağlı: `partial_unknowns` yalnız sorunun çözüldüğü
    # küpün dağarcığını okur. Her düşen token'ı rastgele bir cümlede aramak, başka bir
    # küpe ait token için yanlış kırmızı verirdi (ölçüldü: `cari.tipi`, soru `parti`'ye
    # çözülüyor). *Bir kapının kapsamı, ölçtüğü mekanizmanın kapsamından geniş olamaz.*
    parti = next((c for c in (schema.get("cubes") or []) if c["name"] == "parti"), None)
    assert parti is not None and "grubu" in (parti.get("belirsiz_boyut_tokenlari") or []), \
        "ölçülen vaka (`parti.grubu`) düşen token listesinde yok — kapı konusuz"
    bilinmeyen, _ = partial_unknowns("bu yıl yas_grubu bazında işlenen kg", schema)
    assert "grubu" not in bilinmeyen, (
        "«grubu» düşürüldü ama dağarcıkta da kalmadı → kapsam kapısı onu «başka bir "
        f"konu» sanar (ölçülen canlı kusur): {bilinmeyen}")
