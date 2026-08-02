"""FAZ -1 (K1.5) — ÖLÜ UÇ: 13 cube'un 1'er örneğini dökmek bir cevap değildi.

## Canlı örnek (rapor §1.5)

Kullanıcı: *"son 6 ay personel bazlı çalışma süreleri kıyasla"* → sistem şunu döndürdü ve
**kaç kere denerse denesin bir daha asla LLM'e bile düşmedi**:

> *"Neyi karşılaştırmak/görmek istediğini anlayamadım. Hangi ölçüyü istersin?"*
> arıza sayısı · borç · elektrik · enpg · set · brüt maaş · rework kg ·
> toplam duruş dakikası · oee · fire · su yoğunluğu

**13 cube'un HER BİRİNDEN 1 ölçü** — kullanıcının deyimiyle *"bildiğini okuyor"*.

## Zincir (kod okunarak doğrulandı)

"kıyasla" → `compare_mode()` True · "son 6 ay" → `_period_hit_words()` True · ama
`partial_unknowns` `hits=[]` → "hiç konu yok" dalı ateşleniyor → `_finish(...)` **doğrudan
`return`** ediyor. `_finish` her zaman truthy bir `AskResponse` döner, çağıran taraf
`if fresh: return fresh` yapıyor → **Discovery'ye (adım 5) hiç sıra gelmiyor.**

## Elde sinyal VARDI, kullanılmıyordu

"personel" `ik`/`parti` cube'larında **zaten bir sinonim**. `partial_unknowns`'ın zayıf
cube/boyut taraması bunu görebilirdi — ama o tarama `if unknown and hits:` bloğunun
**İÇİNDEYDİ**, yani `hits` boşken (tam da sistemin en çaresiz olduğu anda) **erişilemiyordu**.

Faz -1 o taramayı `cube_router.ilgili_cubelar`'a **taşıdı** (kopyalamadı) ve üç dallı bir
karar kurdu: **daralt → Discovery'ye izin ver → dürüstçe reddet.**
"""

from __future__ import annotations

import pathlib
import re

import pytest

from app.cube_router import _norm, ilgili_cubelar

ASK = pathlib.Path(__file__).resolve().parents[1] / "app/routers/ask.py"


# --- ZAYIF SİNYAL: canlı örneğin kelimesi gerçekten yakalanıyor mu? ---------------

def test_PERSONEL_kelimesi_cube_daraltiyor(schema):
    """Canlı örneğin çekirdeği. "personel" katalogda bir sinonimdir; sistem 13 cube'u
    2-3'e indirebilecek sinyale SAHİPTİ ve kullanmıyordu."""
    ilgili = ilgili_cubelar(_norm("son 6 ay personel bazli calisma sureleri kiyasla"), schema)
    assert ilgili, "'personel' hiçbir cube'a bağlanmadı — daraltma sinyali çalışmıyor"
    assert len(ilgili) < len(schema.get("cubes") or []), "daraltma yok, tüm katalog döndü"
    adlar = {c["name"] for c in ilgili}
    assert adlar & {"ik", "parti"}, f"beklenen ik/parti, gelen: {sorted(adlar)}"


def test_TANINMAYAN_kelime_HICBIR_cube_getirmez(schema):
    """Sinyal ayırt edici olmalı: her soruya "ilgili" demek daraltma değil gürültüdür."""
    assert ilgili_cubelar(_norm("zxqw plmk asdf"), schema) == []


def test_HARIC_kumesi_calisiyor(schema):
    """`if unknown and hits:` dalı zaten eşleşmiş cube'ları dışlıyor — taşınan gövde bu
    davranışı korumalı."""
    hepsi = ilgili_cubelar(_norm("personel"), schema)
    if hepsi:
        ilk = hepsi[0]["name"]
        kalan = ilgili_cubelar(_norm("personel"), schema, haric={ilk})
        assert ilk not in {c["name"] for c in kalan}


def test_BOYUT_sinonimi_de_sinyal(schema):
    """"tedarikçi" bir ÖLÇÜ değil, başka bir cube'un BOYUTU olabilir — ikisi de "bu konu
    ilgili" sinyalidir (taşınan gövdenin kendi yorumu)."""
    import inspect

    from app import cube_router

    govde = inspect.getsource(cube_router.ilgili_cubelar)
    assert "dimension_synonyms" in govde, "boyut-düzeyi sinyal kayboldu"


# --- GÖVDE KOPYALANMADI, TAŞINDI -------------------------------------------------

def test_TARAMA_ask_py_de_KOPYALANMADI():
    """Bu depoda gövde kopyalamanın bedeli altı kez ölçüldü. İki çağıran da aynı
    fonksiyonu kullanmalı — `ask.py`'de ikinci bir `dimension_synonyms` taraması kalmamalı."""
    kaynak = ASK.read_text(encoding="utf-8")
    kod = "\n".join(s for s in kaynak.splitlines() if not s.strip().startswith("#"))
    assert "dimension_synonyms" not in kod, (
        "`ask.py` hâlâ kendi boyut-sinonim taramasını yapıyor — `ilgili_cubelar` çağrılmalı")
    assert kod.count("ilgili_cubelar(") >= 2, (
        "taşınan fonksiyonun iki çağıranı olmalı (kısmi-anlama dalı + ölü uç dalı)")


# --- ÜÇ DALLI KARAR: daralt → Discovery → dürüst red ------------------------------

def test_OLU_UC_dali_UC_SEVIYELI():
    """Yapısal kilit. Dal artık üç ayrı davranış taşımalı:
      (1) zayıf sinyal varsa DARALT,
      (2) gerçek katalog cube'u tanınıyorsa `None` dön → Discovery devralsın,
      (3) hiçbiri yoksa dürüst red (katalog örnekleri).
    """
    kaynak = ASK.read_text(encoding="utf-8")
    dal = kaynak.split("if not hits and (cube_router._period_hit_words")[1].split(
        "\n    def ")[0]
    assert "ilgili_cubelar(" in dal, "(1) daraltma yok"
    assert "_match_cube(" in dal, "(2) Discovery kapısı yok"
    assert "return None" in dal, "(2) Discovery'ye düşecek bir `return None` yolu yok"


def test_DISCOVERY_KAPISI_yapisal_takiple_AYNI():
    """Asimetri buydu: yapısal-takip zinciri `_match_cube is not None` kapısını zaten
    kullanıyordu, fresh zincirinde YOKTU. Aynı kapı, aynı fonksiyon — ikinci bir kural
    icat edilmedi."""
    kaynak = ASK.read_text(encoding="utf-8")
    assert kaynak.count("_match_cube(q_norm, schema) is not None") >= 1


# --- ÜÇ ÇAĞRI YERİ: biri atlanırsa düzeltme sızar ---------------------------------

def test_TRY_FRESH_INTENT_UC_cagri_yeri_var():
    """Doğrulama turunda ölçüldü: `_try_fresh_intent()` bugün ÜÇ yerden çağrılıyor
    (rapor birini biliyordu). Düzeltme fonksiyonun İÇİNDE yapıldığı için üçü de
    otomatik kapsanıyor — ama sayı değişirse bu varsayım bozulur ve test uyarır."""
    kaynak = ASK.read_text(encoding="utf-8")
    cagrilar = re.findall(r"^\s*fresh\s*=\s*_try_fresh_intent\(\)", kaynak, re.M)
    assert len(cagrilar) == 3, (
        f"{len(cagrilar)} çağrı yeri bulundu (3 bekleniyordu). Düzeltme `_try_fresh_intent`'in "
        "İÇİNDE olduğu için tüm çağrı yerlerini kapsıyor; sayı değiştiyse yeni yolun da "
        "aynı davranışı aldığı DOĞRULANMALI.")


def test_DUZELTME_fonksiyonun_ICINDE():
    """Üç çağrı yerine ayrı ayrı yama yazmak yerine kaynakta düzeltmek — yoksa dördüncü
    bir çağrı yeri eklendiği gün düzeltme oradan sızar."""
    kaynak = ASK.read_text(encoding="utf-8")
    govde = kaynak.split("def _try_fresh_intent(")[1].split("\n    def ")[0]
    assert "ilgili_cubelar(" in govde and "_match_cube(" in govde


# --- DÜRÜST RED korundu -----------------------------------------------------------

def test_HICBIR_KELIME_taninmazsa_KATALOG_dokumu_KALIR():
    """Hiçbir şey anlaşılmadığında katalog dökümü bir "bildiğini okuma" değil, sistemin
    NE YAPABİLDİĞİNİ göstermesidir — ve o durumda yapılabilecek en dürüst şeydir.
    Ama NOTU dürüst olmalı: "tanıdığım bir konu geçmiyor" demeli."""
    # Sabit karakter penceresi ("[:4000]") notu kaçırdı — dal yorumlarla birlikte uzun.
    # Fonksiyon GÖVDESİ kullanılır: sınır kod yapısından gelir, elle sayılan bir uzunluktan değil.
    kaynak = ASK.read_text(encoding="utf-8")
    dal = kaynak.split("def _try_fresh_intent(")[1].split("\n    def ")[0]
    assert "example_labels" in dal, "dürüst red dalı silinmiş"
    # Parça aranır, tam cümle değil: not kaynakta iki satıra bölünmüş bir string
    # birleşimidir ("…tanıdığım " + "bir konu geçmiyor…") — bitişik arama kaçırır.
    assert "bir konu geçmiyor" in dal, (
        "red notu hâlâ neden reddedildiğini söylemiyor — kullanıcı 13 chip'in NEDEN "
        "geldiğini anlayamaz")


@pytest.mark.parametrize("soru", [
    "son 6 ay personel bazli calisma sureleri kiyasla",
    "bu yil tum aylarini karsilastir",
])
def test_CANLI_ORNEKLER_cokmuyor(schema, soru):
    """İki canlı örnek de en azından bir karar üretebilmeli (daraltma ya da red)."""
    ilgili = ilgili_cubelar(_norm(soru), schema)
    assert isinstance(ilgili, list)


# --- ZAMAN BOYUTU KONU SİNYALİ DEĞİLDİR (bu değişikliğin kendi testi yakaladı) ----

def test_DONEM_kelimesi_KONU_sanilmaz(schema):
    """ÖLÇÜLEN KUSUR (2026-08-02): ilk sürüm `"bu yıl tüm AYLARINI karşılaştır"` sorusunu
    — adı bile `test_konusuz_soru_tahmin_etmez` olan, HİÇBİR konu taşımayan soruyu —
    `ik`e bağlıyordu. Sebep: `ik.donem` boyutunun sinonimleri `['donem','ay','periyot',
    'period']` ve `"aylarini"` bunlardan birine ek-uyumlu eşleşiyor.

    Sonuç 13 seçenekli dökümden **DAHA KÖTÜYDÜ**: kendinden emin ve yanlış bir daraltma —
    bu deponun *"en tehlikeli sınıf"* dediği şeyin ta kendisi, üstelik bir DÜZELTMENİN
    içinden doğmuş hâli.

    Kural kelimeye özel bir yama değil: dönem kelimeleri HER zamansal soruda geçer ve konu
    hakkında hiçbir şey söylemez. Cube'un KENDİ `time_dimensions` beyanı okunur.
    """
    assert ilgili_cubelar(_norm("bu yil tum aylarini karsilastir"), schema) == [], (
        "dönem kelimesi hâlâ konu sinyali sayılıyor")


@pytest.mark.parametrize("soru", [
    "bu yil karsilastir", "gecen ay ne oldu", "haftalik trend", "gecen yila gore",
])
def test_SAF_DONEM_sorulari_konu_URETMEZ(schema, soru):
    """Tek bir örneği düzeltmek yetmez — dönem dilinin TAMAMI konu sinyali üretmemeli.

    **Dürüst sınır (ölçüldü):** çıplak *"dönem"* kelimesi bu listede YOK ve olmamalı —
    `ik` cube'unun `donem` adında **gerçek bir boyutu** var, ve `_period_hit_words`/
    `_misc_hit_words` de onu dolgu saymıyor. Yani o kelime gerçekten belirsizdir; testin
    onu "yanlış" ilan etmesi ölçüme değil benim ilk sezgime dayanırdı. İlk denememde
    `"son 3 ayin donemi"` vakası tam bu yüzden kırıldı ve **vaka çıkarıldı, kod değil.**
    """
    assert ilgili_cubelar(_norm(soru), schema) == [], f"{soru!r} yanlışlıkla konu üretti"


def test_GERCEK_KONU_hala_yakalanıyor(schema):
    """Dolgu elemesi asıl sinyali köreltmemeli — canlı örnek hâlâ çalışmalı."""
    assert ilgili_cubelar(_norm("personel bazli calisma sureleri"), schema)


def test_DOLGU_ELEMESI_MEVCUT_kapidan_okunuyor():
    """Kelime listesi ("ay", "yıl"…) SABİT KODLANMAZ. Bu deponun *"bu kelime dönem/
    granülerlik ifadesidir"* TEK KAYNAĞI `_period_hit_words | _misc_hit_words`'tür ve
    `_uncovered` zaten onu kullanıyor — yeni bir liste yazmak ADR-0008'in yasakladığı
    **ikinci doğruluk kaynağı** olurdu.

    **NOT — ilk denemem yetmedi ve nedeni ölçüldü:** çözümü `time_dimensions` beyanına
    dayandırmıştım. `ik`in zaman boyutu `donem_tarih`; sorunu çıkaran boyut ise
    **kategorik** `donem`. Beyan bu ayrımı taşımıyor, dolgu sözlüğü taşıyor."""
    import inspect

    from app import cube_router

    govde = inspect.getsource(cube_router.ilgili_cubelar)
    assert "_period_hit_words" in govde and "_misc_hit_words" in govde
    assert "_uncovered" in govde, "dolgu elemesi mevcut kapıyı kullanmıyor"
    # YALNIZ KOD taranır. Docstring ve yorumlar `['donem','ay','periyot','period']`
    # listesini KANIT olarak alıntılıyor (kusurun ne olduğunu gösteriyor) — ilk sürümde
    # bu kontrol kendi belgesini "sabit kodlama" sanıp kırıldı. Belge kanıt taşımalı;
    # kural kodun kendisinde aranmalı.
    _, _, sonrasi = govde.partition('"""')
    kod = "\n".join(s for s in sonrasi.partition('"""')[2].splitlines()
                    if not s.strip().startswith("#"))
    assert '"ay"' not in kod and "'ay'" not in kod, "dönem kelimesi KODDA sabit kodlanmış"
