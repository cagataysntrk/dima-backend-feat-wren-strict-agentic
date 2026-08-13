r"""🔴🔴 `§T8` — **SORU BİR DÖNEM ADLADI, SORGU ONU TAŞIMADI: SESSİZ-YANLIŞ.**

## Canlıda ölçülen kusur (curl turu, 2026-08-12)

    «2019 cirosu»  →  source=llm:openrouter · cube=adhoc · measures=['toplam_ciro_2019']

Önce *«Discovery'ye düşüyor»* diye teşhis koydum. **Ölçüm bunu çürüttü** — ve ortaya
**daha ağır** bir kusur çıkardı:

```
route('2019 cirosu') → {"cube":"parti","measures":["toplam_ciro"]}        ← FİLTRE YOK
route('bu yil ciro') → {"cube":"parti","measures":["toplam_ciro"],
                        "filters":[{"dimension":"tarih","operator":"gte",
                                    "value":"2026-01-01"}]}
```

`route` cube'u ve ölçüyü **doğru** buluyor, sonra **«2019»u sessizce atıyor**. Üretilen
sayı *«2019'un cirosu»* değil **«tüm zamanların cirosu»**dur — ve kullanıcı onu 2019
sanır. 🅫 *Doğru bir sayı, yanlış bir cümlede hâlâ yanlıştır.*

## Sinyal ZATEN üretiliyordu — kimse okumuyordu 🆌

```
niyet.coz('2019 cirosu') → donem_sayisi=1 · donemler=0
niyet.coz('bu yil ciro') → donem_sayisi=1 · donemler=1
```

`Niyet` bu ayrımı **saymak için** kurulmuştu (`KÖK-1 Faz 1`: *«sistem artık temsil
edemediği şeyi SAYABİLİYOR»*). `donem_sayisi` sorunun **adıyla saydığı**, `donemler`
**çözülebilenler**; farkı *«bilgi var, temsil yok»*un sayısal hâli. Düzeltme yalnız o
farkı **okuyor** — ikinci bir sayaç yazmıyor (`KAT-1`).

## `§101.1` — beyan ÜÇ şart birden tutunca

dönem **adlandı** · **hiçbiri çözülemedi** · sorgu bir **tarih kısıtı taşımıyor**.
Biri bile tutmazsa **susar**; aksi hâlde her cevabın altına bir uyarı düşer ve uyarı
okunmaz olur.
"""

from __future__ import annotations

import dataclasses as _dc

_CQ_FILTRESIZ = {"cube": "parti", "measures": ["toplam_ciro"]}
_CQ_FILTRELI = {"cube": "parti", "measures": ["toplam_ciro"],
                "filters": [{"dimension": "tarih", "operator": "gte",
                             "value": "2026-01-01"}]}


def _isaretler(q, cq, schema):
    from app import uyum
    return {i.isaret for i in uyum.denetle(q, cq, None, schema)}


def test_OLCUM_TABANI_SINIF_ARTIK_BOS(schema):
    """⟳ **ÖLÇÜM TABANI DEĞİŞTİ — ve sebebi bir DÜZELTME** 🅟.

    Bu yüklemin ilk hâli *«`2019 cirosu` sayılır ama **çözülemez**»* diyordu ve alttaki
    asıl kapının boş yeşil olmadığını böyle kanıtlıyordu. O örnek **kapandı**: çıplak yıl
    artık çözülüyor (`cube_router._YEAR_RE`, `K3`) ve soru Discovery'ye düşmüyor.

    ⊙ **On üç ifade tarandı** (`gelecek yıl` · `önümüzdeki ay` · `13. ayda` · `2019 kasım`
    · `bayram döneminde` · `kış aylarında` · `ilk çeyrek` · `mali yıl` · `yaz döneminde`
    · `pandemi döneminde` · `2019 üçüncü çeyrek` · `2019 ilk yarı` · `son mali çeyrek`) ve
    **hiçbiri** *«sayılır ama çözülemez»* sınıfına girmedi: ya çözülüyorlar ya hiç dönem
    sayılmıyorlar. Yani sayıcı ile çözücü **bugün aynı fikirde** 🆉.

    🔴 **Ama işaret KALDI** ve kalmalı: sınıf **kapanmadı**, yalnız **boşaldı**. Yeni bir
    dönem sözcüğü ya da yeni bir katalog onu bir günde yeniden doldurabilir. *Bir kapıyı,
    bugün örneği yok diye kaldırmak, yarın onu yeniden yazmaya söz vermektir.*

    ⚠ Bu yüzden asıl kapı (aşağıda) artık **birim düzeyinde** kuruluyor: canlı bir soru
    yerine sınıfın **kendisi** üretiliyor. Ölçtüğü şey değişmedi — nereden beslendiği
    değişti ㊺.
    """
    from app.niyet import coz

    ici = coz("bu yil ciro", schema)
    assert ici.donem_sayisi >= 1 and ici.donemler, (
        f"⊘ ölçüm tabanı: `bu yil` çözülemedi — {len(ici.donemler)}")
    disi = coz("2019 cirosu", schema)
    assert disi.donem_sayisi >= 1 and disi.donemler, (
        "⊘ `2019 cirosu` yeniden ÇÖZÜLEMEZ oldu — `K3` düzeltmesi geri gitmiş olabilir.")


def test_DONEM_TASINMADIYSA_BEYAN_EDILIYOR(schema, monkeypatch):
    """🔴🔴 **ASIL KAPI.** Soru bir dönem adlayıp sorgu onu taşımıyorsa cümle bunu
    **söylemeli**. Sessiz kalmak, *«tüm zamanlar»*ı *«2019»* diye sunmaktır.

    ⟳ Girdi **birim düzeyinde** kuruluyor (yukarıdaki gerekçe): sınıfın canlı örneği
    bugün yok, ama sınıf var. Sahte olan **yalnız** `Niyet`in iki alanı; işaretin kendi
    mantığı **ürünündür** ve olduğu gibi koşuyor ㉕.

    🅑 Mutasyon: `uyum.py`'deki `donem_tasinmadi` dalı kaldırılırsa bu yüklem kırılır.
    """
    from app import niyet as _n
    from app import uyum

    # ⚠ Hedef `coz` değil **`coz_soru`** — `uyum.denetle` şemasız çözücüyü çağırır
    # (`uyum.py:746`) ve import **fonksiyon içinde** olduğu için yama çalışma anında
    # tutar. İlk denemem `coz`'u yamaladı ve **hiçbir şey değişmedi** ㉙: bir bağımlılığı
    # yamalamadan önce, kodun onu hangi **adla** çağırdığını okumak gerekir.
    gercek = _n.coz_soru("bu yil ciro")
    sahte = _dc.replace(gercek, donemler=[])          # sayılır ama ÇÖZÜLEMEZ
    monkeypatch.setattr(_n, "coz_soru", lambda *_a, **_k: sahte)
    assert "donem_tasinmadi" in _isaretler("bu yil ciro", _CQ_FILTRESIZ, schema), (
        "🔴 DÖNEM SESSİZCE DÜŞTÜ: soru bir dönem adlıyor, sorguda tarih kısıtı yok ve "
        "sistem bunu SÖYLEMİYOR — üretilen sayı tüm zamanları kapsıyor.")


def test_DONEM_COZULDUYSE_SUSUYOR(schema):
    """⚠ `§101.1` — **yanlış uyarı**, uyarısızlıktan pahalıdır. `bu yil` çözülüyor ve
    filtreye giriyor; burada beyan basmak beyanı gürültüye çevirirdi ㉜."""
    assert "donem_tasinmadi" not in _isaretler("bu yil ciro", _CQ_FILTRELI, schema), (
        "🔴 YANLIŞ UYARI: dönem ÇÖZÜLDÜ ve filtreye girdi, yine de beyan basılıyor.")


def test_TARIH_KISITI_VARSA_SUSUYOR(schema):
    """⚠ İkinci susma şartı: dönem çözülememiş olsa bile sorgu **zaten** bir tarih
    kısıtı taşıyorsa (ör. takip turundan miras) sayı tüm kayıtları kapsamıyordur."""
    assert "donem_tasinmadi" not in _isaretler("2019 cirosu", _CQ_FILTRELI, schema), (
        "🔴 sorgu bir tarih kısıtı TAŞIDIĞI hâlde «taşıyamadım» deniyor.")


def test_DONEM_ADLANMADIYSA_SUSUYOR(schema):
    """⚠ Üçüncü susma şartı: soru hiç dönem adlamadıysa taşınmayan bir şey yoktur."""
    assert "donem_tasinmadi" not in _isaretler("ciro", _CQ_FILTRESIZ, schema), (
        "🔴 dönem ADLANMADIĞI hâlde «dönem taşıyamadım» deniyor — her cevaba düşen "
        "bir uyarı, okunmayan bir uyarıdır.")


def test_IKI_KARDES_OLCUT_AYRI_KALDI():
    """⚠ ㊺ **Aynı adlı iki ölçüt olmasın.** `_zaman_ekseni_var` *«kırılımda zaman
    boyutu var mı»* (trend çizilebilir mi) sorusunu; `_tarih_kisiti_var` *«süzgeçte
    tarih var mı»* (dönem daraltıldı mı) sorusunu sorar. Biri ötekinin yerine geçerse
    `§T8` **sessiz** kalır."""
    from app import uyum

    assert uyum._tarih_kisiti_var(_CQ_FILTRELI) is True
    assert uyum._tarih_kisiti_var(_CQ_FILTRESIZ) is False
    # kırılımda zaman YOK ama süzgeçte tarih VAR → ikisi ayrışıyor
    assert uyum._zaman_ekseni_var(_CQ_FILTRELI, None) is False
