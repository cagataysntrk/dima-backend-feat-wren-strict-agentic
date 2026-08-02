"""FAZ -0.5a — ÇOKLU AY: "ocak şubat mart" sessizce "yalnız Ocak" olmuyordu artık.

## Ölçülen kusur (canlı örnek, rapor §1.6)

Kullanıcı: *"ocak şubat mart ayları için ciro değişim trendi nedir"* → sistem dönemi
**"tümü"** aldı. Kod okununca **dört bağımsız mekanizmanın aynı anda kırıldığı** görüldü;
bu dosya birincisini ve onun kapı tarafındaki yansımasını kilitler.

`_month_range_filters` `re.search` kullanıyordu — **yalnız İLK ayı** yakalıyordu. Ve asıl
tehlike gözlemlenen "tümü" hatası DEĞİLDİ:

> §1.6 kritik yan bulgu: *"'değişim' kelimesi olmasaydı (kapsam kapısı geçilseydi), sistem
> **sessizce Ocak-only** bir cevap verir, `source="cube"` rozetiyle — gözlemlenenden **daha
> kötü** bir hata sınıfı."*

## Asimetri kodda kayıtlıydı

`_period_hit_words` **1 Ağustos'ta** `re.search`'ten `finditer`'a geçirilmişti (kodun kendi
yorumu, `cube_router.py:1375-1378`) — yani **KAPI** çoklu ay görüyordu. Ama **ÇÖZÜCÜ**
(`_month_range_filters`) hâlâ tek ay çözüyordu. Sonuç §1.6'nın çarpıcı cümlesi:

> *"Kullanıcı NE KADAR çok dönem detayı verirse, kapı O KADAR az soru soruyor."*

## Neden "bitişik/ayrık" ayrımı — ve neden ayrık burada ÇÖZÜLMÜYOR

`date_filters` düz bir `list[dict]` (AND zinciri) döner; bu biçim **tek bir aralık** ifade
edebilir. "ocak şubat mart" bitişiktir → `gte(01-01)/lte(03-31)` ile ifade edilir.
"ocak ve mart" ayrıktır → bir OR/küme gerektirir, bu bir **sözleşme genişletmesidir**
(Faz 2a). Burada yapılan tek şey ayrık durumu **sessizce yanlış çözmemek**: filtre
üretilmez ve dönem kapısı SORAR.
"""

from __future__ import annotations

from datetime import date

import pytest

from app.cube_router import (
    _adlandirilan_aylar,
    _bitisik_mi,
    cozulemeyen_ay_listesi,
    date_filters,
)


def _aralik(fs: list[dict]) -> tuple[str, str]:
    """[gte, lte] filtrelerinden (başlangıç, bitiş) çıkarır."""
    g = next(f["value"] for f in fs if f["operator"] == "gte")
    l = next(f["value"] for f in fs if f["operator"] == "lte")
    return g, l


# --- ASIL KAPI: çoklu ay artık tek aya düşmüyor ----------------------------------

def test_UC_BITISIK_AY_tek_araliga_cevrilir():
    """Canlı örneğin ta kendisi. Eskiden yalnız Ocak alınıyordu."""
    fs = date_filters("ocak subat mart aylari icin ciro", "tarih")
    assert fs, "hiç filtre üretilmedi"
    bas, bit = _aralik(fs)
    assert bas.endswith("-01-01"), f"başlangıç Ocak değil: {bas}"
    assert bit.endswith("-03-31"), f"bitiş Mart sonu değil: {bit} (yalnız Ocak alınmış olabilir)"


def test_TEK_AY_davranisi_DEGISMEDI():
    """Geriye uyum: tek ay bugünküyle birebir aynı kalmalı."""
    fs = date_filters("temmuz ayi cirosu", "tarih")
    bas, bit = _aralik(fs)
    assert bas.endswith("-07-01") and bit.endswith("-07-31")


def test_YIL_belirtilmisse_o_yil_kullanilir():
    fs = date_filters("2025 ocak subat cirosu", "tarih")
    bas, bit = _aralik(fs)
    assert bas == "2025-01-01" and bit == "2025-02-28"


def test_IKI_BITISIK_AY():
    fs = date_filters("kasim aralik ayi satislari", "tarih")
    bas, bit = _aralik(fs)
    assert bas.endswith("-11-01") and bit.endswith("-12-31")


# --- AYRIK aylar: sessizce YANLIŞ çözülmüyor -------------------------------------

def test_AYRIK_AY_filtre_URETMEZ():
    """"ocak ve mart" tek bir aralık DEĞİLDİR. Yarım bir filtre (yalnız Ocak) hiç
    filtreden KÖTÜDÜR — `date_filters`'ın kendi "yarım uygulama yok" disiplini."""
    assert date_filters("ocak ve mart cirosu", "tarih") == []


def test_AYRIK_AY_kapiya_HABER_VERIR():
    """Filtre üretmemek yetmez: `_period_hit_words` ay adlarını görüp kapıyı susturuyor.
    Kapının bu durumu AYIRT EDEBİLMESİ için ayrı bir predikat gerekiyor."""
    assert cozulemeyen_ay_listesi("ocak ve mart cirosu") is True


def test_BITISIK_AY_kapiyi_SUSTURUR():
    """Bitişik aylar çözülebildiği için kapı sormamalı — yoksa doğru çözülen bir soruya
    gereksiz netleştirme sorulur."""
    assert cozulemeyen_ay_listesi("ocak subat mart cirosu") is False


def test_TEK_AY_kapiyi_SUSTURUR():
    assert cozulemeyen_ay_listesi("temmuz ayi cirosu") is False


def test_AY_YOKSA_kapi_ETKILENMEZ():
    assert cozulemeyen_ay_listesi("bu yil ciro") is False


# --- Korunan istisnalar -----------------------------------------------------------

def test_ARALIK_tek_basina_AY_SAYILMAZ():
    """"tarih aralığı" ile karışır — bugünkü bilinçli davranış korunmalı."""
    assert _adlandirilan_aylar("ocak mart araligi") == _adlandirilan_aylar("ocak mart")
    assert not any(m == 12 for _, m in _adlandirilan_aylar("ocak subat araligi"))


def test_ARALIK_AYI_acikca_istenirse_SAYILIR():
    aylar = _adlandirilan_aylar("aralik ayi cirosu")
    assert [m for _, m in aylar] == [12]


def test_ACIK_ARALIK_ifadesi_ONCE_gelir():
    """"1 ocak 31 mart arası" `_explicit_range_filters`'a aittir; çoklu-ay taraması onu
    ezmemeli (sıra `date_filters`'ta korunuyor)."""
    fs = date_filters("1 ocak 31 mart arasi ciro", "tarih")
    bas, bit = _aralik(fs)
    assert bas.endswith("-01-01") and bit.endswith("-03-31")


def test_TEKRARLI_ay_adi_bir_kez_sayilir():
    """"mart ayında mart hedefi" → tek ay, ayrık DEĞİL."""
    assert cozulemeyen_ay_listesi("mart ayinda mart hedefi") is False


# --- Yardımcıların kendisi --------------------------------------------------------

@pytest.mark.parametrize("aylar,beklenen", [
    ([(2025, 1), (2025, 2), (2025, 3)], True),
    ([(2025, 1), (2025, 3)], False),
    ([(2024, 12), (2025, 1)], False),   # yıl atlıyor → tek aralık DEĞİL (sözleşme sınırı)
    ([(2025, 5)], True),
    ([], True),
])
def test_BITISIKLIK_kurali(aylar, beklenen):
    assert _bitisik_mi(aylar) is beklenen


def test_GELECEK_ay_adi_GECEN_yila_sarar():
    """Bugünkü davranış: yıl verilmemişse geçmişteki en yakın o ay."""
    bugun = date.today()
    gelecek = 12 if bugun.month < 12 else 1
    ad = {1: "ocak", 12: "aralik ayi"}[gelecek]
    aylar = _adlandirilan_aylar(f"{ad} cirosu")
    if aylar:
        yil, _ = aylar[0]
        assert yil <= bugun.year


# --- FAZ -0.5b: ikiz `match_kpi` -------------------------------------------------

def test_MATCH_KPI_TEK_tanim():
    """`cube_router.py`'de İKİ `match_kpi` tanımı vardı; ilki (498) sessizce gölgeleniyor
    ve ÖLÜYDÜ. İkisinin semantiği de farklıydı (`_syn_hit` ekli vs çıplak `in`).
    İronik olarak yaşayan tanımın docstring'i fonksiyonun *"hiç tanımlanmamış"* olduğunu
    yazıyordu — gölgelenme kazası yazıya da geçmişti."""
    import pathlib
    import re

    kaynak = (pathlib.Path(__file__).resolve().parents[1] / "app/cube_router.py").read_text(
        encoding="utf-8")
    assert len(re.findall(r"^def match_kpi\(", kaynak, re.M)) == 1


def test_MATCH_KPI_yasayan_semantik_KILITLI():
    """Silinen tanımın davranışı geri gelmesin diye yaşayan semantik kilitlenir:
    normalize edilmiş metinde ALT DİZİ eşleşmesi + `len >= 3` tabanı + en uzun kazanır."""
    from app.cube_router import match_kpi

    sema = {"kpis": [
        {"name": "ccc", "label": "Nakit Döngüsü", "synonyms": ["nakit", "nakit donusum dongusu"]},
        {"name": "cari_oran", "label": "Cari Oran", "synonyms": ["cari oran"]},
    ]}
    assert match_kpi("nakit donusum dongusu nedir", sema) == "ccc"   # en UZUN kazanır
    assert match_kpi("cari oran nedir", sema) == "cari_oran"
    assert match_kpi("hicbir sey", sema) is None
    assert match_kpi("herhangi bir soru", {"kpis": []}) is None      # boş katalog kısa devre


# --- FAZ -0.5d: fresh Intent yolunun dönem asimetrisi ----------------------------

def test_INTENT_JSON_yolunda_DONEM_sistemce_cozuluyor():
    """`llm.py`'nin prompt'u LLM'e tarih yazmayı AÇIKÇA yasaklıyor ("sistem hesaplar").
    Ama "sistem" o beyanı yalnız İKİ yolda uyguluyordu: `route()` kendi içinde ve
    takip-düzenleme dalı (`_resolve_period`). **Taze Intent-JSON yolunda hesaplayan kimse
    yoktu** — LLM yazmıyor, sistem de hesaplamıyor → sessizce TÜM ZAMANLAR.

    Bu bir politika değil bir ASİMETRİDİR: beyan verilmiş, bir yol uyguluyor, öteki
    uygulamıyor. Bu test yapısal olarak asimetrinin kapandığını kilitler.
    """
    import pathlib

    kaynak = (pathlib.Path(__file__).resolve().parents[1] / "app/routers/ask.py").read_text(
        encoding="utf-8")
    # `if route_hit:` bloğunun içinde, `_period_gate` çağrısından ÖNCE bir dönem çözümü
    # olmalı ve yalnız `cube+llm` dalına uygulanmalı (route() zaten kendi çözüyor).
    # NOT: dosyada İKİ `if route_hit:` var (biri route() try bloğunda) — `split(...)[1]`
    # yanlışını yakaladı. Doğru çapa: kapıdan GERİYE doğru en yakın `if route_hit:`.
    _KAPI = 'gate = _period_gate(cq, cube_meta, route_hit.get("period_optional"), "Intent-path")'
    blok = kaynak.split(_KAPI)[0].rsplit("if route_hit:", 1)[1]
    assert 'intent_source == "cube+llm"' in blok, (
        "fresh Intent yolunda dönem çözümü yok — LLM tarih yazmıyor, sistem de hesaplamıyor")
    assert "date_filters" in blok, "dönem çözümü tek kaynağı (date_filters) çağırmıyor"
    assert "time_dimensions" in blok, (
        "zaman boyutu cube'un KENDİ beyanından alınmıyor — sabit 'tarih' varsayımı, farklı "
        "adlı zaman boyutu olan cube'da var olmayan kolona filtre yazar")


def test_ROUTE_yolu_IKINCI_KEZ_donem_cozmez():
    """`route()` tarihi zaten kendi çözüyor (`cube_router.py`: `filters.extend(date_filters)`).
    Düzeltme oraya da uygulansaydı aynı filtre iki kez eklenirdi."""
    import pathlib

    kaynak = (pathlib.Path(__file__).resolve().parents[1] / "app/routers/ask.py").read_text(
        encoding="utf-8")
    _KAPI = 'gate = _period_gate(cq, cube_meta, route_hit.get("period_optional"), "Intent-path")'
    blok = kaynak.split(_KAPI)[0].rsplit("if route_hit:", 1)[1]
    # Koşul `cube+llm`e bağlı olmalı — koşulsuz bir `date_filters` çağrısı route()'u da vurur.
    # YORUMLAR sayılmaz: düzeltmenin gerekçesi `date_filters`'ı ADIYLA anlatıyor ve ilk
    # sürümde bu test kendi açıklama metnini "üç çağrı" sanıp kırıldı — aynı kabalık
    # `test_beyanlar_curumesin`'de de yaşandı (anma ≠ çağrı).
    kod = "\n".join(s for s in blok.splitlines() if not s.strip().startswith("#"))
    assert kod.count("date_filters(") == 1, "dönem çözümü birden çok kez çağrılıyor"
    # Sıra da YORUMSUZ metinde ölçülür — gerekçe metni koşuldan önce geçtiği için
    # ham `blok` üzerinde index kıyası yanlış sonuç veriyordu.
    assert kod.index('intent_source == "cube+llm"') < kod.index("date_filters("), (
        "dönem çözümü `cube+llm` koşulunun İÇİNDE değil — route() da vurulur")


# --- UX: netleştirme CEVAPLANABİLİR bir soru sormalı -----------------------------

def test_AYRIK_AY_secenekleri_KULLANICININ_aylari():
    """Jenerik dönem chip'leri ("Bugün · Bu hafta · Bu ay · Bu yıl · Tümü") *"ocak ve
    mart"* diyen kullanıcıya HİÇBİR ŞEY söylemez — o iki belirli ay istedi. Belirsizlikte
    SORMAK (ADR-0008) yalnız soru sormak değil, **cevaplanabilir** bir soru sormaktır."""
    from app.cube_router import ay_netlestirme

    sec = ay_netlestirme("ocak ve mart cirosu")
    assert sec, "ayrık ay için seçenek üretilmedi"
    etiketler = [s["label"] for s in sec]
    assert any("Ocak" in e for e in etiketler) and any("Mart" in e for e in etiketler)
    assert any("arası" in e for e in etiketler), "kapsayan aralık seçeneği yok"


def test_AYRIK_AY_seceneklerinin_SORGULARI_gercekten_cozuluyor():
    """Bir chip'in `query`'si tıklanınca yeni soru olarak koşar. Çözülemeyen bir sorgu
    öneren chip, kullanıcıyı aynı duvara ikinci kez çarptırır."""
    from app.cube_router import _norm, ay_netlestirme, date_filters

    for s in ay_netlestirme("ocak ve mart cirosu"):
        fs = date_filters(_norm(s["query"]), "tarih")
        assert fs, f"chip çözülemeyen bir sorgu öneriyor: {s['query']!r}"


def test_KAPSAYAN_ARALIK_secenegi_ARADAKI_ayi_da_kapsar():
    """"Ocak–Mart arası" seçilirse Şubat da dahil olmalı — etiketin vaadi bu."""
    from app.cube_router import _norm, ay_netlestirme, date_filters

    kapsayan = [s for s in ay_netlestirme("ocak ve mart cirosu") if "arası" in s["label"]][0]
    fs = date_filters(_norm(kapsayan["query"]), "tarih")
    bas, bit = _aralik(fs)
    assert bas.endswith("-01-01") and bit.endswith("-03-31")


def test_BITISIK_ay_icin_secenek_URETILMEZ():
    """Bitişik aylar zaten çözülüyor — netleştirme sormak gereksiz gürültü olurdu."""
    from app.cube_router import ay_netlestirme

    assert ay_netlestirme("ocak subat mart cirosu") is None


def test_NETLESTIRME_yeni_yuzey_ACMAZ():
    """§14.1: yeni yetenek yeni panel/alan doğurmaz. Ayrık-ay netleştirmesi mevcut
    `suggestions` alanını ve mevcut chip bileşenini kullanır."""
    import pathlib

    kaynak = (pathlib.Path(__file__).resolve().parents[1] / "app/routers/ask.py").read_text(
        encoding="utf-8")
    blok = kaynak.split("cozulemeyen_ay_listesi(q_norm)")[1].split("return _finish")[1][:600]
    assert "suggestions=" in blok, "netleştirme mevcut chip alanını kullanmıyor"
    assert "Suggestion(" in blok, "yeni bir öneri tipi icat edilmiş"
