r"""🔴 `FAZ 5.5/5.9` + `FAZ 6.6/6.7` — **TUŞ, SON BAKILANLAR, ve İKİ GEREKÇELİ ⊘.**

## `5.5` SIKLIK ÖNCELİĞİ — ⊘, çünkü **ÖLÇÜ YOK** ㊸

Plan sıklığı RRF skoruna küçük bir katsayıyla eklemek istiyordu. Kaynak **kodda
arandı** ㉙ (`interaction_log` DB probu yasak, ve zaten gerekmedi):

* `app/routers/stats.py:51` → `select(InteractionLog.kind, func.count())` — sayım
  **`kind` başına**dır (*«kaç Discovery, kaç cube»*), **ölçü başına değil**.
* `app/kaset.py`'deki `sayac` bir **test kaseti** sayacıdır, ürün telemetrisi değil.
* Katalog tarafında ölçü başına bir kullanım alanı **yok** (`metadata.yml` şeması
  `lower_is_better`/`unit`/`synonyms` taşır).

Yani sıklık **ölçülmüyor**. Ölçülmeyen bir şeyi sıralamaya katmak, uydurulmuş bir
sayıyı sıralamaya katmaktır ㊱ — ve `_RRF_K`'nın kendisi zaten **kalibre değil** 🅖;
üstüne ikinci bir kalibresiz terim koymak, iki bilinmeyeni birbirine dayamaktır.

⊙ **Ön koşulu yazılı:** ölçü başına kullanım sayacı doğduğunda (`InteractionLog`'a
`olcu` kırılımı ya da ayrı bir sayaç) `5.5` yeniden değerlendirilir. Kapı aşağıda:
sayaç doğarsa bu ⊘ **kırmızıya döner** ㊻.

## `6.7` ÜÇ ÇIKIŞ — ⊘, çünkü **ÖZNESİ YOK** ㊻

Plan *«marj kapısının üç çıkışı ekranda ayırt edilebilir»* istiyordu. Ama `FAZ 2`
marj kapısını **gerekçeli ⊘** bıraktı (`test_marj_kapisi_on_kosullari.py`, üç ölçülmüş
engel). Olmayan bir kapının çıkışlarını ekranda ayırt etmek **mümkün değil** — ve
öyleymiş gibi bir rozet çizmek 🆂 *beyanı koşula bağlayıp süs yapmak* olurdu.

⊙ Öneri şeridinin **kendi** üç hâli **zaten beyanlı**: `kip` (`leksik` / `vektor` /
`leksik+vektor`) ve `indeks.durum` (`taze` / `yok` / `kapali`). Bu, `6.7`'nin
karşılığı **değildir** ve öyle sayılmıyor 🅫.
"""

from __future__ import annotations

import pathlib

_KOK = pathlib.Path(__file__).resolve().parents[1]
_FE = _KOK.parent / "dima-frontend-demo-master" / "src"


def _yorumsuz(src: str) -> str:
    """TS/TSX yorumlarını düşürür 🅞 — *sözü değil kullanımı ara*.

    ⚠ `tests/_kod_ayikla.py`'nin TS karşılığı; Python `ast`'i burada işe yaramaz.
    Basit ama yeterli: `//…` satır sonuna kadar, `/*…*/` blok.
    """
    import re as _re

    src = _re.sub(r"/\*.*?\*/", "", src, flags=_re.S)
    return _re.sub(r"//[^\n]*", "", src)


def _fe(ad: str) -> str:
    import pytest

    y = _FE / ad
    if not y.is_file():
        pytest.skip(
            f"⊘ `{ad}` YOK — ön uç mount'u eksik, bu kapı ÖLÇMEDEN atlandı. "
            '`-v "$PWD/dima-frontend-demo-master:/dima-frontend-demo-master:ro"` eklenmeli.')
    return y.read_text(encoding="utf-8")


# ── `6.6` TUŞ — kapalıyken AĞA ÇIKMAZ 🆀 ────────────────────────────────────

def test_serit_BAYRAGA_bagli():
    """`6.6` — şerit `useFeature("oneri_katmani")` okumalı.

    ⚠ Planın `localStorage` çaresi **uygulanmadı** ㊱: `useFeature` zaten var ve
    bayrak normal kanaldan akıyor; planın kendi uyardığı **A/B kaybı** (`§40.3`)
    böylece **doğmuyor** 🆝.
    """
    src = _fe("components/OneriSeridi.tsx")
    assert 'useFeature("oneri_katmani")' in src, (
        "🔴 öneri şeridi bayrağa bağlı değil — tuşsuz bir yetenek geri alınamaz.")


def test_KAPALIYKEN_UCA_HIC_CIKILMAZ():
    """🔴🔴 **`6.6`'nın asıl şartı** 🆀: *«çizmemek»* yetmez.

    Bayrak kapalıyken `getOneri` **çağrılmamalı** — planın kendi ölçütü *«ağ
    sekmesinden görülebilir»*. Bir bayrak yalnız pikselleri kapatıyorsa, kapattığını
    sandığı maliyeti **kapatmamıştır**.

    🅑 Mutasyon: `kapaliBayrak` erken-dönüşü `useEffect`'ten çıkarılırsa bu yüklem
    kırılır (istek koruması **fetch'ten önce** olmalı ㊴).

    ⟳🔴 **DÜZELTİLDİ — kapı İKİ YÖNDE de yanılıyordu** (denetim ajanı ölçtü):
    eski hâli `'kapaliBayrak ||' in govde` diye **tek bir dize** arıyordu.
    ⓐ Koruma **silinip** metin bir **yoruma** taşındığında kapı **yeşil** verdi
    (yanlış-negatif) ⓑ davranışı doğru koruyan ama biçimi farklı bir yazım
    (`if (kapaliBayrak) { … return; }`) **kırmızı** verdi (yanlış-pozitif).
    *Bir kapı tek bir yazımı kilitliyorsa, kilitlediği şey davranış değil biçimdir.*

    ⊙ Yeni ölçüt: yorumlar **ayıklanır** 🅞, ve korumanın `getOneri` çağrısından
    **önce** geçtiği aranır — iki geçerli yazım da kabul, yorumdaki söz **kabul değil**.
    """
    src = _yorumsuz(_fe("components/OneriSeridi.tsx"))
    # ⚠ ③ **Çapa iki kez yanlış kondu ve ikisini de mutasyon söyledi** 🅑:
    # ① `'kapaliBayrak ||' in govde` — tek yazımı kilitliyordu (iki yönde yanıldı).
    # ② `src.index("useEffect")` — **import satırındaki** `useEffect` sözcüğünü
    #    buluyordu, dolayısıyla bildirimi «etkinin içinde» sanıyordu ve koruma
    #    silinse bile **yeşil** veriyordu.
    # Doğru çapa: `getOneri` çağrısını **içeren** etkinin başlangıcı.
    i_fetch = src.index("getOneri(")
    i_etki = src.rindex("useEffect(", 0, i_fetch)
    i_bayrak = src.find("kapaliBayrak", i_etki, i_fetch)
    assert i_bayrak >= 0, (
        "🔴 bayrak kontrolü **isteğin önünde** değil — kapalıyken bile `/oneri` "
        "çağrılıyor olabilir (`E-1`: ölçüm istekten başlar).")


# ── `5.9` BOŞ GİRDİ — son bakılanlar, YENİ DEPO AÇMADAN ─────────────────────

def test_son_bakilanlar_SOHBETTEN_turer_yeni_depo_YOK():
    """`5.9` — kaynak `temellendirme.olcu` (makbuzun *«ne anladım»* alanı), yani
    kullanıcının **gördüğü** ad; ham kolon adı değil 🅬.

    ⚠ Yeni bir kalıcı depo açılmadı: `localStorage` yok, sunucu tarafı yok.
    """
    src = _fe("lib/threads.ts")
    assert "export function sonBakilanEtiketler" in src
    assert "temellendirme?.olcu" in src, (
        "🔴 son bakılanlar ham ölçü adından türetiliyor olabilir — kullanıcı o adı "
        "hiç görmedi (`toplam_fire_kg` ≠ *«fire»*).")
    # ⚠ 🅞 **Bu yüklem ilk yazılışında KENDİ AÇIKLAMAMI yakaladı:** dosyada geçen tek
    # `localStorage`, *«`localStorage` yok»* diyen yorum satırıydı. Aranan şey bir
    # **kullanım**dır (`localStorage.` / `window.localStorage`), bir **söz** değil.
    assert "localStorage." not in src and "window.localStorage" not in src, (
        "🔴 `5.9` için yeni bir kalıcı depo açılmış — plan bunu istemedi ve bu, "
        "izin/senkron/temizlik borcu doğurur.")


def test_bos_girdide_UCA_CIKILMAZ():
    """Boş girdide öneri **ucu çağrılmaz** — liste sohbetten gelir. `q.length < 2`
    zaten erken döner; bu yüklem o korumanın **kaybolmamasını** tutar."""
    src = _fe("components/OneriSeridi.tsx")
    assert "q.length < 2" in src


# ── `5.5` ⊘ — ÖN KOŞUL KAPISI: sayaç doğarsa bu erteleme DÜŞER ㊻ ────────────

def test_5_5_ERTELEMESI_HALA_GECERLI():
    """🔴 **Gerekçeli bir ⊘'nün kapısı.** `5.5` *«ölçü başına sıklık kodda yok»*
    diyor. O ölçü doğduğu gün erteleme **dayanaksız** kalır ve bu yüklem söyler.

    ⚠ Aranan şey bir **kırılım**: `InteractionLog` üzerinde `olcu`/`measure` başına
    bir sayım. `kind` başına sayım (`stats.py:51`) **bu değildir** ㊺.
    """
    stats = (_KOK / "app" / "routers" / "stats.py").read_text(encoding="utf-8")
    assert "InteractionLog.kind, func.count()" in stats, (
        "🔴 `stats.py`'nin sayım kırılımı değişti — `5.5`'in ⊘ gerekçesi ("
        "*«sayım kind başına, ölçü başına değil»*) yeniden ölçülmeli.")
    for kirilim in ("InteractionLog.olcu", "InteractionLog.measure"):
        assert kirilim not in stats, (
            f"🔴 ölçü başına sayım doğmuş ({kirilim}) — `5.5` (sıklık önceliği) artık "
            "**uygulanabilir**, ertelemesi düştü.")


def test_6_7_ERTELEMESI_ON_KOSULA_BAGLI():
    """🔴 `6.7`'nin öznesi **marj kapısıdır** ve o kapı `FAZ 2`'de gerekçeli ⊘ oldu.

    Marj kapısı bir gün gelirse (`config.Settings`'te bir eşik + tüketicisi), bu
    yüklem kırmızı verir ve `6.7` yeniden değerlendirilir ㊻.
    """
    from app.config import Settings

    alanlar = set(getattr(Settings, "model_fields", {}))
    assert not ({"marj_esigi", "oneri_marj_esigi"} & alanlar), (
        "🔴 marj eşiği `Settings`'e girmiş — `FAZ 2` ⊘'sü düştü, dolayısıyla `6.7` "
        "(üç çıkışın ekranda ayırt edilmesi) artık **öznesi olan** bir iştir.")
