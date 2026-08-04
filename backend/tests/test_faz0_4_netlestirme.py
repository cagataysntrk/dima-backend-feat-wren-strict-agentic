"""FAZ 0.4 — ölçüm **kararının** kapısı.

0.4 kod indirmez; bir **karar** verir. O yüzden kapının koruduğu şey davranış değil,
**kararın dürüstlüğü**:

1. Ölçüm aleti kendi nüfusunu doğru kuruyor mu (≥2 sahip, dönem maskesi yok)
2. Karar kuralı **önceden yazılı** ve üç yolu da üretebiliyor mu
3. Ölçülmemiş bir bayrak **açık olamaz** — makbuzsuz karar yok
4. Alet, mevcut sahipleri **yeniden yazmıyor** (tek sahip kuralı)
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from lab import faz0_4_netlestirme as f04

KOK = Path(__file__).resolve().parents[1]


# ── 1 · NÜFUS KURULUMU ───────────────────────────────────────────────────────

def test_NUFUS_YALNIZ_IKI_SAHIPLI_TERIMLERDEN_KURULUR():
    """Tek sahibi olan terim nüfusa **giremez** — orada belirsizlik yoktur ve
    netleştirme chip'i saf gürültü olurdu."""
    sch = {"cubes": [
        {"name": "cari", "measure_synonyms": {"bakiye": ["bakiye", "hesap"]}},
        {"name": "mizan", "measure_synonyms": {"bakiye": ["bakiye"]}},
        {"name": "satis", "measure_synonyms": {"ciro": ["ciro"]}},
    ]}
    terimler = {t for _q, t, _c in f04._sorular(sch)}
    assert terimler == {"bakiye"}, f"nüfus yanlış kuruldu: {terimler}"


def test_SORU_DONEM_TASIR_yoksa_baska_bir_sey_olculur():
    """🔴 Dönemsiz sorulursa `CLARIFY:dönem` **önce** ateşlenir ve ölçü belirsizliğini
    maskeler. O koşumda ölçülen şey 0.4 **değildir** — ve yeşil görünürdü."""
    sch = {"cubes": [
        {"name": "a", "measure_synonyms": {"x": ["borç"]}},
        {"name": "b", "measure_synonyms": {"y": ["borç"]}},
    ]}
    sorular = [q for q, _t, _c in f04._sorular(sch)]
    assert sorular and all(q.startswith("bu yıl ") for q in sorular), sorular


def test_SAHIPLER_SIRALI_ve_tekil():
    sch = {"cubes": [
        {"name": "z", "measure_synonyms": {"m": ["t"]}},
        {"name": "a", "measure_synonyms": {"m": ["t"]}},
        {"name": "a", "measure_synonyms": {"n": ["t"]}},
    ]}
    (_q, _t, cubes), = f04._sorular(sch)
    assert cubes == ["a", "z"], cubes


# ── 2 · UYUM OKUYUCU ─────────────────────────────────────────────────────────

def test_UYUM_TYPO_YUZDESIYLE_KARISMAZ():
    """`ask.py` typo notunu ve uyum notunu **aynı satıra** birleştiriyor. İlk `%`'yi
    okumak, benzerlik oranını uyum sanmak olurdu — sayı gelir, yanlış sayı gelir."""
    d = {"trace": ["'fre'→'fire' düzeltildi (%88 benzerlik) · self-consistency %67 (3 örnek)"]}
    assert f04._uyum(d) == pytest.approx(0.67, abs=0.01)


def test_UYUM_YOKSA_NONE_doner_sifir_degil():
    """`0.0` *"hiç uzlaşmadı"* der; `None` *"bu soru sorulamaz"* der. İkisi ayrı şeydir
    ve karar kuralı ikisine ayrı davranır."""
    assert f04._uyum({"trace": ["Intent-path: cube"]}) is None
    assert f04._uyum({}) is None


# ── 3 · KARAR KURALI — üç yol + üçüncü hâl ───────────────────────────────────

def _tur(sinif, cube, uyum=1.0):
    return (sinif, cube, uyum)


def test_KARAR_A_KARARSIZ_bayragi_acar():
    """Aynı soru turlar arası farklı cube → yazı-tura kanıtlandı."""
    karar, _g = f04.karar_ver(
        {"q1": [_tur("sql", "cari"), _tur("sql", "mizan")],
         "q2": [_tur("sql", "cari"), _tur("sql", "cari")]}, nufus_n=10)
    assert karar.startswith("A"), karar
    assert "AÇILIR" in karar


def test_KARAR_C_TEK_CUBE_YIGILMASI_bayragi_acar():
    """Kararlı ama hep aynı cube → ayırt etme değil, sabit tercih. Öteki cube'un
    kullanıcısı **her seferinde** sessizce yanlış cevap alır."""
    karar, gerekce = f04.karar_ver(
        {"q1": [_tur("sql", "cari"), _tur("sql", "cari")],
         "q2": [_tur("sql", "cari"), _tur("sql", "cari")]}, nufus_n=10)
    assert karar.startswith("C") and "AÇILIR" in karar, karar
    assert any("cari" in g for g in gerekce)


def test_KARAR_B_BAGLAMDAN_COZUYOR_bayragi_KAPALI_tutar():
    """Her soru kendi içinde kararlı **ve** sorular arası cube değişiyor → LLM sorudaki
    ayırt edici bilgiyi gerçekten kullanıyor; netleştirme **gerçek kapsam kaybı**."""
    karar, _g = f04.karar_ver(
        {"q1": [_tur("sql", "cari"), _tur("sql", "cari")],
         "q2": [_tur("sql", "mizan"), _tur("sql", "mizan")]}, nufus_n=10)
    assert karar.startswith("B") and "KAPALI kalır" in karar, karar


def test_ZATEN_NETLESTIREN_SORU_KAZANCA_SAYILMAZ():
    """🔴 Bayrak KAPALIYKEN de netleştirme dönen soruda 0.4'ün **kazancı yoktur** —
    `_intent_uyusmazlik_chipi` zaten soruyor. Bunları kazanca saymak, maddenin
    faydasını **abartmak** olurdu."""
    karar, gerekce = f04.karar_ver(
        {"q1": [_tur("netlestirme", None), _tur("netlestirme", None)],
         "q2": [_tur("netlestirme", None), _tur("netlestirme", None)]}, nufus_n=10)
    assert karar.startswith("⊘"), karar
    assert any("zaten" in g for g in gerekce)


def test_LLM_KATILMADIYSA_KARAR_BASILMAZ():
    """🔴 **YANLIŞ-YEŞİL ÖLÇÜLDÜ (2026-08-04) — ve kapı ondan doğdu.**

    Canlı koşumda sağlayıcıların **hepsi** `429`/`503` verdi (*"TÜM sağlayıcılar
    başarısız"*), ama `karar_ver` **«B · bağlamdan çözüyor»** bastı: her tur aynı
    deterministik düşüşe uğradığı için sonuç *"kararlı"* göründü. Ölçülen kararlılık,
    LLM'in değil **BAŞARISIZLIĞIN** kararlılığıydı — ve o karar bir bayrağı kapalı
    tutmanın gerekçesi olacaktı.

    Kota **ön uçuşu** bunu yakalayamaz: ön uçuş bir ÖN koşuldur, kota koşumun
    **ortasında** tükenebilir. Katılım kanıtı `self-consistency` izidir (`k>1` iken
    `ask.py` onu trace'e yazar); hiçbir turda yoksa Intent dalı hiç çalışmamıştır.
    """
    karar, gerekce = f04.karar_ver(
        {"q1": [_tur("sql", "cari", None), _tur("sql", "cari", None)],
         "q2": [_tur("sql", "mizan", None), _tur("sql", "mizan", None)]}, nufus_n=41)
    assert karar.startswith("⊘"), (
        f"LLM hiç cevap vermediği hâlde karar basıldı: {karar!r}")
    assert any("başarısızlığın" in g.lower() or "hiçbir turda" in g for g in gerekce), \
        gerekce


def test_KOTA_ON_UCUSU_SELECT_CUBE_U_DA_DENIYOR():
    """🔴 **Ön uçuş, koşumun kullanmadığı yolu sertifikalıyordu.**

    Intent yolu `generate_sql`'i değil **`select_cube`**'u çağırır ve o **ayrı bir
    modele** gider (`*_select_model`); ikisinin **kotası da ayrıdır**. `generate_sql`
    yeşilken `select_cube` `429` verdi ve koşum başladı — bu, kimlik asimetrisinin
    ön-koşul katmanındaki hâli.

    Kural `konusma_senaryolari._kota_on_ucusu`'nun **tek sahipliğinde** durur; dört canlı
    alet de oradan geçer, ikinci bir kopya yazılmaz.
    """
    kaynak = (KOK / "lab" / "konusma_senaryolari.py").read_text(encoding="utf-8")
    i = kaynak.index("def _kota_on_ucusu")
    govde = kaynak[i:i + 4000]
    assert "select_cube" in govde, (
        "`_kota_on_ucusu` yalnız `generate_sql`'i deniyor. Intent yolu `select_cube` "
        "çağırır ve o AYRI modele/kotaya gider — ön uçuş koşumun kullanmadığı yolu "
        "sertifikalar (ölçüldü 2026-08-04: yanlış-yeşil bir karar üretti).")
    assert "hasattr(uretici, \"select_cube\")" in govde, (
        "`select_cube` KOŞULSUZ deneniyor. Yeteneği olmayan bir üreticide bu, "
        "ölçülemeyeni kırmızı göstermek olurdu — üçüncü hâl kaybolur.")


def test_BOS_OLCUM_UCUNCU_HAL_uretir_yesil_degil():
    """Koşmamış bir ölçüm **geçmez de kalmaz** — `⊘ ÖLÇÜLEMEDİ`. Bu deponun üçüncü hâli."""
    karar, _g = f04.karar_ver({}, nufus_n=0)
    assert karar.startswith("⊘"), karar


def test_DUSUK_UYUM_TEK_BASINA_KARARSIZ_sayilir():
    """Cube aynı kalsa bile `self-consistency` 2/3'ün altındaysa seçim **oylamayla zor
    kurtarılmış** demektir; kararlılık iddiası orada durmaz."""
    karar, _g = f04.karar_ver(
        {"q1": [_tur("sql", "cari", 0.34), _tur("sql", "cari", 0.34)],
         "q2": [_tur("sql", "mizan", 0.34), _tur("sql", "mizan", 0.34)]}, nufus_n=10)
    assert karar.startswith("A"), karar


# ── 4 · MAKBUZSUZ KARAR YOK ──────────────────────────────────────────────────

#: MIMARI'deki karar bölümünün başlığı — **tek çapa**, iki test de bunu kullanır.
_KARAR_BASLIGI = "### FAZ 0.4 (v1) · `netlestirme_onceligi` — **ÖLÇÜM KARARI:"


def _mimari() -> str:
    return (KOK / "MIMARI.md").read_text(encoding="utf-8")


def _yml_degeri() -> str:
    yml = yaml.safe_load((KOK / "demo" / "packs" / "features.yml").read_text())
    blok = (yml.get("features") or yml) or {}
    return str(blok.get("netlestirme_onceligi", "off"))


def test_KARAR_MIMARI_YE_YAZILDI():
    """🔴 Yol haritasının 0.4 KAPI'sı **birebir** bunu istiyor: *"…`off` kalır ve nedeni
    `MIMARI.md`'ye **yazılır**."*

    Karar 2026-08-03'te canlı ölçüldü ama gerekçe yalnız `features.yml` **yorumunda**
    duruyordu. Bir YAML yorumu mimari otorite değildir: `MIMARI.md` çelişkide kazanır ve
    orada bu maddeden **hiç söz edilmiyordu**. Kararın evi belgede olmalı, yoksa bir
    sonraki tur *"ölçülmemiş"* sanıp **kotayı yeniden yakar**.
    """
    m = _mimari()
    assert _KARAR_BASLIGI in m, (
        "FAZ 0.4'ün karar bölümü MIMARI.md'de YOK. Yol haritasının KAPI'sı bunu "
        "açıkça istiyor: 'nedeni MIMARI.md'ye yazılır'.")
    blok = m[m.index(_KARAR_BASLIGI):]
    for kanit in ("63 etiketli vaka", "5/6 KARARLI", "kaybedilen 5"):
        assert kanit in blok[:4000], f"karar bölümünde ölçüm kanıtı eksik: {kanit!r}"


def test_BEYAN_ILE_BAYRAK_AYRISMIYOR():
    """🔴 **Makbuzsuz karar yok — ve iki sahip yok.** MIMARI'nin ilan ettiği karar ile
    `features.yml`'deki değer **aynı şeyi** söylemeli.

    Biri `off` derken öteki `beta` olursa, hangisinin doğru olduğu bilinemez: bu deponun
    1 numaralı kusuru *"aynı kuralın iki sahibi"*dir ve karar/uygulama ayrışması onun en
    pahalı hâlidir. ⚠ Rapor dosyasına **dayanmaz**: `lab/reports/` **gitignore'da**, yani
    ona bağlı bir kapı ortama göre yeşil/kırmızı olurdu — kapı değil, kura.
    """
    m = _mimari()
    i = m.index(_KARAR_BASLIGI)
    ilan = m[i:i + len(_KARAR_BASLIGI) + 40]
    beklenen = "off" if "`off` KALIYOR" in ilan else None
    assert beklenen is not None, (
        f"MIMARI'nin 0.4 kararı okunamadı: {ilan!r}. Başlık bir DEĞER ilan etmeli.")
    assert _yml_degeri() == beklenen, (
        f"MIMARI '{beklenen}' diyor, `features.yml` {_yml_degeri()!r}. Karar ile "
        "uygulama AYRIŞMIŞ — biri güncellendi, öteki unutuldu.")


def test_AD_CAKISMASI_AYRISTIRILDI():
    """🔴 MIMARI'de **iki ayrı «Faz 0.4»** var ve biri ötekinin kararını TERS gösteriyor.

    Eski olan 2026-08-02'nin **kapsam kapısı** fazıdır (`475e691`, `_uncovered` alt-dizi
    onarımı) ve *"OK +6 · CUBE-SAPMA −25"* taşır — yani **sıkılaştırma lehine** sayılar.
    v1 yol haritasının FAZ 0.4'ü ise `netlestirme_onceligi`'nin ölçüm kararıdır ve sonucu
    **tam tersi**. Ayrıştırılmazsa okuyucu yanlış sayıya bakıp yanlış kararı çıkarır.
    """
    m = _mimari()
    assert "Faz 0.4 · KAPSAM KAPISI" in m, \
        "eski Faz 0.4 hâlâ nitelenmemiş — yeni 0.4 ile karışır"
    assert "AD ÇAKIŞMASI" in m, "ad çakışması uyarısı belgede yok"


def test_KARAR_KURALI_ALETIN_ICINDE_YAZILI():
    """Karar kuralı ölçümden **sonra** yazılırsa, ölçüm kararı değil karar ölçümü seçer.
    Üç yolun üçü de aletin belgesinde adıyla geçmeli."""
    kaynak = (KOK / "lab" / "faz0_4_netlestirme.py").read_text(encoding="utf-8")
    for yol in ("A · KARARSIZ", "B · BAĞLAMDAN ÇÖZÜYOR", "C · SİSTEMATİK YANLILIK"):
        assert yol in kaynak, f"karar yolu belgede yok: {yol}"


# ── 5 · TEK SAHİP ────────────────────────────────────────────────────────────

def test_ALET_MEVCUT_SAHIPLERI_YENIDEN_YAZMAZ():
    """`_BayrakZorla` · `_client` · `ACCOUNTS` · `_canli_ortami_geri_yukle` **çağrılır**,
    kopyalanmaz. Bu deponun 1 numaralı kusuru *"aynı kuralın iki sahibi"*."""
    kaynak = (KOK / "lab" / "faz0_4_netlestirme.py").read_text(encoding="utf-8")
    for ad in ("_BayrakZorla", "_client", "ACCOUNTS", "_canli_ortami_geri_yukle"):
        assert not re.search(rf"^(?:def|class)\s+{re.escape(ad)}\b", kaynak, re.M), \
            f"{ad} bu dosyada YENİDEN tanımlanmış — tek sahip kuralı ihlali"
        assert ad in kaynak, f"{ad} import edilmemiş"


#: `--live` koşabilen lab aletleri — hepsi aynı içe aktarma sözleşmesine tabi.
_CANLI_ALETLER = ["faz0_4_netlestirme.py", "nl_accuracy.py", "deneyim.py", "vk_taban.py"]


@pytest.mark.parametrize("dosya", _CANLI_ALETLER)
def test_ICE_AKTARMA_SIRASI_CANLI_YAKALAMAYI_BOZMUYOR(dosya):
    """🔴 **Sıra bir sözleşmedir ve yorumla zorlanamaz.**

    `konusma_senaryolari` gerçek ortamı (`DIMA_LLM_PROVIDER` …) **modül düzeyinde**,
    `tests.conftest` onu `rule`'a sabitlemeden **ÖNCE** yakalar. Bir alet `tests.conftest`'i
    daha erken import ederse yakalama `rule`'u yakalar ve `--live` ya **fail-closed durur**
    (iyi hâl) ya da — kapan olmasaydı — sessizce `rule` ile koşup *"canlı"* diye raporlardı.

    Bu kural bugüne kadar yalnız `nl_accuracy.py`'nin bir **yorumunda** yazılıydı ve
    `faz0_4_netlestirme.py` ilk denemesinde tam oraya bastı. Ölçüldü: bu deponun
    *"beyan var, kod onu tanımıyor"* sınıfı — bu kez ölçüm katmanında. Yorum artık **kapı**.
    """
    kaynak = (KOK / "lab" / dosya).read_text(encoding="utf-8")
    i_canli = kaynak.find("from lab.konusma_senaryolari import")
    i_conf = kaynak.find("import tests.conftest")
    if i_canli < 0 or i_conf < 0:
        pytest.skip(f"{dosya} bu ikilinin ikisini birden import etmiyor")
    assert i_canli < i_conf, (
        f"{dosya}: `tests.conftest` canlı ortam yakalamasından ÖNCE import ediliyor. "
        "`konusma_senaryolari` gerçek `DIMA_LLM_PROVIDER`'ı modül düzeyinde yakalar; "
        "conftest önce koşarsa yakalanan değer `rule` olur ve `--live` ya durur ya da "
        "— daha kötüsü — sahte bir 'canlı' tur raporlar.")


def test_ILAN_EDILEN_ESKI_KAPININ_CALISMADIGI_YAZILI():
    """Yol haritası 0.4'ün kapısını `nl_corpus.py --kapi` diye ilan etmişti; o alette
    **bayrak zorlama yok** ve korpusun yer gerçeği bu nüfusta yazı-tura. Aletin belgesi
    bunu söylemezse, bir sonraki tur aynı ölçülemez kapıyı **tekrar** dener.

    ⚠ **Durum KATLANMAZ ve nedeni ölçüldü.** İlk sürüm `"hakemlik" in kaynak.lower()`
    yazıyordu ve **kırmızı verdi**: Türkçe `HAKEMLİK`'in `İ`'si `str.lower()`'da
    `i` + **birleşik nokta**'ya (`i̇`, U+0307) açılır, düz `i` ile eşleşmez. Yani kapı,
    belgede **yazan** bir cümleyi *"yazılmamış"* gördü — ölçüm aracının kendisi yanlış
    ölçtü. Bu depoda o sınıfın kaçıncı tekrarı olduğu `MIMARI §6.4`'te yazılı; burada
    çözüm basit: metin **yazıldığı gibi** aranır.
    """
    kaynak = (KOK / "lab" / "faz0_4_netlestirme.py").read_text(encoding="utf-8")
    assert "nl_corpus" in kaynak, "eski kapının adı alette geçmiyor"
    assert "HAKEMLİK EDEMEZ" in kaynak, \
        "korpusun bu nüfusa hakemlik edemediği alette yazılı değil"
