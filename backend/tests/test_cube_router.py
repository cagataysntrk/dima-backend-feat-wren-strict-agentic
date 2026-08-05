"""cube_router birim golden'ları — gerçek kullanım loglarından türetilmiş vakalar.

Bu testler saf fonksiyonları ölçer (LLM/ağ yok): route eşleşmeleri, tarih filtreleri,
dönem tespiti, deterministik refine ve doğrulama. Bir keyword/kural değişikliğinin
neyi bozduğunu anında gösterir (ADR-0004 "değişiklikte doğruluk düşerse alarm").
"""

from __future__ import annotations

import pytest
from datetime import date

from app import cube_router
from app.llm import _norm


def route(schema, q: str):
    return cube_router.route(q, schema)


def test_archetype_net_satis_ayrimi():
    """'net satış' AYRI bir ölçüdür (net_satis = satış − iade). satis_tutari arketipi onu
    İÇERMEMELİ — yoksa "net satış" satis_tutari'ye kayıp YANLIŞ VERİ verir (brüt ≠ net;
    canlı 2026-07-25 accuracy bulgusu). Temel sinonimler ("satış"/"ciro") durur."""
    from app.archetypes import synonyms_for

    syns = {s.lower() for s in synonyms_for("satis_tutari")}
    assert "net satış" not in syns and "net satis" not in syns
    assert "satış" in syns and "ciro" in syns  # temel ölçü sinonimleri korunur


def test_norm_buyuk_i_combining_dot():
    """Türkçe büyük İ tuzağı (canlı 2026-07-25): "İ".lower() → i + U+0307 combining dot;
    _TR eşlemesi tetiklenmezdi → büyük-harf sorgu meta/değer/sinonim eşleşmesini kaybederdi.
    _norm combining dot'u silmeli — büyük-harf ve küçük-harf giriş AYNI normalize olmalı."""
    assert _norm("DİMA NEDİR?") == "dima nedir?"
    assert _norm("DSO NEDİR") == _norm("dso nedir") == "dso nedir"
    assert _norm("İADE") == _norm("iade") == "iade"
    assert _norm("İSTANBUL") == "istanbul"
    assert "̇" not in _norm("NEDİR İRSALİYE İSKONTO")  # combining dot dizgede kalmamalı


# --- route: cube eşleşmeleri (loglardan) ------------------------------------

def test_makine_bazinda_oee(schema):
    plan = route(schema, "makine bazında ortalama oee")
    assert plan is not None
    cq = plan["cube_query"]
    assert cq["cube"] == "oee"
    assert cq["measures"] == ["ort_oee"]
    assert cq["dimensions"] == ["makine"]


def test_vardiya_hafta_gunu_son_3_ay(schema):
    plan = route(schema, "Vardiya × haftanın günü verimliliği (son 3 ay)")
    assert plan is not None
    cq = plan["cube_query"]
    assert set(cq["dimensions"]) == {"vardiya", "hafta_gunu"}
    tarih = [f for f in cq.get("filters", []) if f["dimension"] == "tarih"]
    assert tarih and tarih[0]["operator"] == "gte"


def test_asama_bazinda_toplam_fire(schema):
    plan = route(schema, "aşama bazında toplam fire")
    assert plan is not None
    cq = plan["cube_query"]
    assert cq["cube"] == "parti"
    assert cq["measures"] == ["toplam_fire_kg"]
    assert cq["dimensions"] == ["asama"]


def test_toplam_uretim_pur_toplam(schema):
    plan = route(schema, "toplam üretim")
    assert plan is not None
    cq = plan["cube_query"]
    assert cq["measures"] == ["toplam_uretim_kg"]
    assert not cq.get("dimensions")
    # dönem yok → needs_period True (clarification tetiklenir)
    assert cube_router.needs_period(cq, _norm("toplam üretim"))


def test_liste_istekleri_cube_degil(schema):
    assert route(schema, "reddedilen partileri listele") is None


def test_capraz_verim_fire_cube_degil(schema):
    # verim + fire tek cube'a sığmaz → LLM
    assert route(schema, "makine bazında verim ve fire oranı") is None


# --- SESSİZ-YANLIŞ koruması (log satır 10: typo → dejenere cube) ------------

def test_typo_kirilim_niyeti_reddedilir(schema):
    """'m<kina bazında oee': boyut eşleşmiyor ama kırılım niyeti var → cube DÖNMEMELİ."""
    assert route(schema, "m<kina bazında oee") is None


def test_bilinmeyen_kirilim_reddedilir(schema):
    assert route(schema, "tedarikçi bazında oee") is None


def test_kirilim_basarisiz_trend_varken_de_reddedilir(schema):
    """Genel kök-neden düzeltmesi (1 Ağustos 2026, canlı bulgu): SESSİZ-YANLIŞ koruması
    eskiden `not gran` da şart koşuyordu — "trend"/"aylık" gibi bir zaman-kovası kelimesi
    `_time_gran()`'ı tetikleyip `gran`'ı dolduruyor, bu da karşılanamayan bir kırılım
    isteğinin (oee'de "tedarikçi" boyutu yok) SESSİZCE düşmesine yol açıyordu — kardeş
    testle (yukarıdaki, trend'siz hali) AYNI senaryo, yalnız trend kelimesi eklenmiş."""
    assert route(schema, "tedarikçi bazında oee trendini göster") is None


def test_kirilim_basarisiz_zaman_kelimesiyle_de_reddedilir(schema):
    """Aynı korumanın yalnız 'trend' kelimesine özgü bir yama olmadığını, diğer JENERİK
    (birim belirtmeyen) zaman tetikleyicisiyle ('zaman') de tutarlı çalıştığını kilitler."""
    assert route(schema, "tedarikçi bazında oee zaman içinde nasıl değişti") is None


def test_kirilim_acik_birim_ifadesiyle_hala_calisir(schema):
    """Regresyon kilidi: AÇIK bir zaman-birimi ifadesi ("aylara göre") — jenerik "trend"/
    "zaman" DEĞİL — kendi başına meşru bir kırılımdır; koruma bunu YANLIŞLIKLA reddetmemeli
    (bkz. test_time_gran_ceyrek_yil ile aynı sınıf — "göre" kelimesi hem zaman hem boyut
    ifadelerinde ortak olduğu için ilk taslak düzeltme bunu kırmıştı)."""
    plan = route(schema, "oee'yi aylara göre göster")
    assert plan is not None
    assert plan["cube_query"]["timeDimensions"][0]["granularity"] == "month"


# --- typo_correct YANLIŞ-POZİTİF regresyonu (canlı bulgu, 31 Temmuz 2026) ----------
# Gerçek kullanımda "hesapla" (calculate) katalogdaki "hesap" (mizan/cari boyutu,
# muhasebe hesap kodu) ile 0.83 benzerlik taşıyor → typo_correct bunu YANLIŞLIKLA
# "hesap"a düzeltmeye çalışıyordu (iki kelime aynı kökten ama tamamen farklı anlam).
# "kalemlere" de alakasız bir kelimeye ("bekleme") öneriliyordu — cube'a-daraltma
# (`only_cube`) + "hesapla" stop-stem ile ikisi de düzeltildi.

def test_iki_ayli_karsilastirma_typo_onerisine_donusmez(schema):
    # regresyon (Madde 1, 1 Ağustos 2026): _period_hit_words() ay-regex'i re.search
    # kullanıyordu → yalnız İLK ay ("mayis") yakalanıyor, "nisan" SESSİZCE "unknown"
    # kalıyor, ardından typo_correct() onu parti cube'unun "egitim" boyutundaki "Lisans"
    # değerine (difflib 0.727, MID-HIGH arası) "şunu mu demek istedin?" olarak öneriyordu.
    from app.cube_router import _norm, typo_correct

    q = _norm("mayıs ayı cirosunu nisan ayına göre karşılaştır")
    corrected, fixes = typo_correct(q, schema)
    assert corrected == q
    assert fixes == []


def test_hesapla_fiili_typo_onerisine_donusmez(schema):
    from app.cube_router import _norm, typo_correct

    q = _norm("ram 3 icin verimlilik hesapla")
    corrected, fixes = typo_correct(q, schema)
    assert corrected == q
    assert fixes == []


def test_kalemlere_alakasiz_oneriye_donusmez(schema):
    from app.cube_router import _norm, typo_correct

    q = _norm("kalemlere gore karsilastir satislari ve karlilik hesapla")
    corrected, fixes = typo_correct(q, schema)
    assert corrected == q
    assert fixes == []


def test_genis_havuzda_alakasiz_kelime_oneriye_donusmez(schema):
    """Genel kök-neden düzeltmesi (1 Ağustos 2026, canlı bulgu — "kalem"/"kalite"):
    cube çözülemediğinde (`_match_cube` None) typo_correct'in havuzu TÜM kataloğa
    genişliyor — bu rejimde "kalem"(5)/"kalite"(6) 0.7273 skorla eşleşip "'kalem' yerine
    'kalite' mi demek istedin?" öneriyordu (nisan/lisans ile MATEMATİKSEL AYNI desen:
    "kalem" hiçbir cube'un sözlüğünde yok, "kalite" TAMAMEN alakasız bir cube'un
    — oee.ort_kalite — ölçü sinonimi). Geniş havuzda öneri barajı artık _TYPO_HIGH'a
    çekildi — bu skor artık GEÇMİYOR."""
    from app.cube_router import _match_cube, _norm, typo_correct

    q = _norm("kalem")
    assert _match_cube(q, schema) is None  # ön-koşul: gerçekten geniş-havuz rejiminde
    corrected, fixes = typo_correct(q, schema)
    assert corrected == q
    assert fixes == []


def test_dar_havuzda_gercek_typo_hala_onerilir(schema):
    """Regresyon kilidi: cube TEK bir adaya çözülünce (only_cube dolu, havuz DARALIR)
    davranış eskisi gibi kalmalı — bu düzeltme YALNIZ `resolved is None` dalını etkiler.
    "vardya"/"vardiya" (0.923) zaten var olan, test edilmiş bir OTOMATİK düzeltmedir."""
    from app.cube_router import _norm, typo_correct

    q = _norm("vardya bazında oee")
    corrected, fixes = typo_correct(q, schema)
    assert "vardiya" in corrected
    assert any(f["kind"] == "auto" and f["from"] == "vardya" for f in fixes)


def test_kirilimsiz_pur_toplam_hala_calisir(schema):
    # koruma pür toplamları etkilememeli
    assert route(schema, "toplam fire") is not None


# --- value_index.py entegrasyonu (doğrulama turu düzeltmesi, 1 Ağustos 2026) --------
# `app/value_index.py` (ADR-0008) TAM yazılmıştı ama hiç bağlanmamıştı — yukarıdaki
# difflib geçişi yalnız TEK KELİMELİK düzeltme yapabiliyor (`_catalog_vocabulary` çok-
# kelimeli değerleri BİLE tek kelimelere bölüyor); `FuzzyIndex` komşu kelime ikilemelerini
# de dener. Bu YÜZDEN yukarıdaki geçişin YERİNE değil, YALNIZ onun çözemediği (hâlâ
# tanınmayan) kelimeler için EK bir deneme olarak eklendi (bkz. FAZ4-SONRASI-ONERILER
# P1-4). "KONTİNÜ KASAR" (oee cube'unun gerçek çok-kelimeli bir makine değeri) burada
# somut örnek: "kontinu" tek başına difflib geçişini geçemiyor (best==w ya da skor
# yetersiz), yalnız BİGRAM ("kontinu kasr") üzerinden value_index yakalıyor.

def test_value_index_multi_word_value_typo_fallback(schema):
    """Tek-kelimelik difflib geçişi çözemediği bir ÇOK-KELİMELİ değer typo'sunu
    value_index.py'nin bigram-farkında bulanık eşleştirmesi yakalamalı."""
    from app.cube_router import _norm, typo_correct

    q = _norm("kontinü kasr makinesinde oee bu yıl")
    corrected, fixes = typo_correct(q, schema)
    assert "kontinu kasar" in corrected
    assert any(f["kind"] == "auto" and "kontinu" in f["from"] and "kasar" in f["to"]
              for f in fixes)


def test_value_index_fallback_does_not_fire_when_nothing_left_unknown(schema):
    """Tüm kelimeler ZATEN tanınıyorsa (ya da ilk geçiş hepsini çözdüyse) value_index
    hiç DEVREYE GİRMEMELİ — regresyon kilidi (mevcut %100 hassasiyetli davranış korunur)."""
    from app.cube_router import _norm, typo_correct

    q = _norm("makine bazında ortalama oee")
    corrected, fixes = typo_correct(q, schema)
    assert corrected == q
    assert fixes == []


# --- metadata-tabanlı sinonimler (generic router — içerik Wren'de) ----------

def test_metadata_synonym_randiman_cihaz(schema):
    """Yeni sinonimler YAML'dan gelir: 'cihaz bazında randıman' Python değişikliği
    olmadan cube'a düşer (eskiden LLM'e giderdi)."""
    plan = route(schema, "cihaz bazında randıman")
    assert plan is not None
    cq = plan["cube_query"]
    assert cq["measures"] == ["ort_oee"] and cq["dimensions"] == ["makine"]


def test_metadata_synonym_tezgah_durus(schema):
    plan = route(schema, "tezgah bazında duruş")
    assert plan is not None
    assert plan["cube_query"]["measures"] == ["toplam_durus_dakika"]


def test_exact_word_kar_not_karsilastir(schema):
    """'kar!' tam-kelime: 'karşılaştır' fire cube'unu tetiklemez; karşılaştırma
    niyeti (önceki dönem/LAG) cube'a sığmaz → LLM golden yolu."""
    q = "kişilerin aylık verimlilik performanslarını karşılaştır ve önceki dönemleri ile de karşılaştır"
    assert route(schema, q) is None


def test_en_karli_musteriler(schema):
    plan = route(schema, "en karlı müşteriler")
    assert plan is not None
    cq = plan["cube_query"]
    assert cq["measures"] == ["kar"] and cq["dimensions"] == ["musteri"]


def test_kar_orani_marj_olcusu(schema):
    """Log regresyonu: "kar yüzdesi/karlılık oranı" katalogda yoktu → LLM sessizce
    fire_orani_yuzde İKAME etti (yanlış cevap). Artık kar_marji_yuzde ölçüsü var ve
    en-uzun-sinonim kuralı "kar oranı" > "kar!" ile marja gider."""
    for q in ("müşteri bazında kar oranı bu yıl", "kumaşlara göre kar yüzdesi bu yıl",
              "müşterilere göre karlılık oranı bu yıl"):
        plan = route(schema, q)
        assert plan is not None, q
        assert plan["cube_query"]["measures"] == ["kar_marji_yuzde"], q
    # mutlak kâr hâlâ ayrışıyor
    plan = route(schema, "en karlı müşteriler")
    assert plan["cube_query"]["measures"] == ["kar"]


# --- log regresyonları: hafta_gunu çekimleri + guard/filtre etkileşimi -------

def test_haftanin_gunleri_cekimi(schema):
    """'haftanın günLERİ bazında' — çekim eki boyutu kaçırmamalı (kök sinonim).
    OEE makine metriğidir (kişi yok); cinsiyet-bazlı kişi-verimliliği parti cube'undadır
    (bkz. golden test_kirilimli_soru_da_donem_sorar). Burada makine ekseninde çekim testi."""
    plan = route(schema, "makine bazında haftanın günleri bazında oee grafiği")
    assert plan is not None
    cq = plan["cube_query"]
    assert cq["cube"] == "oee"
    assert "hafta_gunu" in cq["dimensions"]
    # dönem bilgisi yok → kırılımlı da olsa clarification İSTENİR (sessiz tüm-zaman yok)
    assert cube_router.needs_period(cq, _norm("haftanın günleri bazında oee"))
    # "tüm zamanlar" bilinçli seçimi sormayı durdurur
    assert not cube_router.needs_period(cq, _norm("tüm zamanlar"))


def test_gunler_gunluk_kova_degil():
    """'haftanın günleri' GÜNLÜK zaman kovası değildir (477-satır regresyonu)."""
    assert cube_router._time_gran(_norm("haftanın günleri bazında")) is None
    assert cube_router._time_gran(_norm("günlük üretim")) == "day"


def test_deger_filtresi_guardi_kurtarmaz(schema):
    """Kırılım kelimesi + eşleşmeyen boyut: değer filtresi (Erkek) eşleşse bile
    dejenere cube dönmemeli."""
    assert route(schema, "erkek çalışanlar için tedarikçi bazında oee") is None


def test_refine_olcu_duzeltme_kalibi(schema):
    """Log regresyonu (2026-07-20): "fire oranı değil kar oranı" bağlam kopması sanıldı,
    kırılımlar kayboldu. Düzeltme kalıbı ("X değil/yerine Y") ölçüyü deterministik takas
    eder; kırılım/kova/filtre KORUNUR."""
    prev = {"cube": "parti", "measures": ["fire_orani_yuzde"], "dimensions": ["musteri"],
            "timeDimensions": [{"dimension": "tarih", "granularity": "month"}],
            "filters": [{"dimension": "tarih", "operator": "gte", "value": "2026-01-01"}]}
    det = cube_router.deterministic_refine(prev, _norm("fire oranı değil kar oranı"), schema)
    assert det is not None
    assert det["measures"] == ["kar_marji_yuzde"]
    assert det["dimensions"] == ["musteri"]
    assert det["timeDimensions"][0]["granularity"] == "month"
    assert det["filters"] == prev["filters"]
    # "yerine" varyantı
    prev2 = {"cube": "parti", "measures": ["toplam_fire_kg"], "dimensions": ["asama"],
             "timeDimensions": [{"dimension": "tarih", "granularity": "month"}]}
    det2 = cube_router.deterministic_refine(prev2, _norm("toplam fire yerine fire oranı ver"), schema)
    assert det2 is not None and det2["measures"] == ["fire_orani_yuzde"]
    assert det2["dimensions"] == ["asama"]


def test_refine_olcu_kaldirma(schema):
    """Canlı 2026-07-25: çok-ölçülü rapordan ölçü çıkarma. 'çıkar/kaldır/sil/gösterme/
    istemiyorum' fiilleri deterministik düşürür (kalan ≥1). Fiil kelimeleri kapsam kapısına
    takılmamalı ("kaldır" uygulanıp coverage'ta None'a düşüyordu; "çıkar" hiç tetiklenmiyordu)."""
    prev = {"cube": "parti", "measures": ["toplam_fire_kg", "fire_orani_yuzde"],
            "dimensions": ["musteri"]}
    for q in ["fire oranını çıkar", "fire oranını kaldır", "fire oranını gösterme",
              "fire oranını sil", "fire oranı istemiyorum"]:
        det = cube_router.deterministic_refine(prev, _norm(q), schema)
        assert det is not None, q
        assert det["measures"] == ["toplam_fire_kg"], q
        assert det["dimensions"] == ["musteri"]
    # fiil ölçünün ARDINDA da olabilir (Türkçe devrik)
    det_after = cube_router.deterministic_refine(prev, _norm("çıkar fire oranını"), schema)
    assert det_after is not None and det_after["measures"] == ["toplam_fire_kg"]
    # son ölçü KORUNUR — tek ölçülü rapordan çıkarılamaz
    prev1 = {"cube": "parti", "measures": ["toplam_fire_kg"], "dimensions": ["musteri"]}
    det1 = cube_router.deterministic_refine(prev1, _norm("toplam fireyi çıkar"), schema)
    assert det1 is None or det1["measures"] == ["toplam_fire_kg"]


def test_refine_varlik_top_n(schema):
    """Log regresyonu: "en çok satış yapılan 3 müşterininkileri göster" limit:3 ile ilk
    ayın 3 satırını kesiyordu — varlık top-N: ölçüt=satış(ciro), boyut=müşteri, n=3."""
    prev = {"cube": "parti", "measures": ["kar_marji_yuzde"], "dimensions": ["musteri"],
            "timeDimensions": [{"dimension": "tarih", "granularity": "month"}],
            "filters": [{"dimension": "tarih", "operator": "gte", "value": "2026-01-01"}]}
    det = cube_router.deterministic_refine(
        prev, _norm("en çok satış yapılan 3 müşterininkileri göster"), schema)
    assert det is not None
    assert det.get("entity_limit") == {
        "dimension": "musteri", "measure": "toplam_ciro", "direction": "desc", "n": 3}
    assert "limit" not in det
    assert det["measures"] == ["kar_marji_yuzde"]  # rapor ölçüsü DEĞİŞMEZ (ölçüt ayrı)


def test_route_varlik_top_n(schema):
    """Taze soruda da: zaman kovası + kırılım + "en yüksek N" → entity_limit (satır limiti değil)."""
    plan = route(schema, "bu yıl aylık olarak en yüksek ciro yapan 3 müşteri")
    assert plan is not None
    cq = plan["cube_query"]
    assert cq.get("entity_limit", {}).get("n") == 3
    assert cq["entity_limit"]["dimension"] == "musteri"
    assert plan["limit"] is None


def test_eski_cube_adi_cozumu(schema):
    """Yeniden adlandırma göçü: "fire" (eski ad) TEK cube'un sinonimi → "parti"ye çözülür."""
    assert cube_router.resolve_cube_name("fire", schema) == "parti"
    assert cube_router.resolve_cube_name("parti", schema) == "parti"
    assert cube_router.resolve_cube_name("oee", schema) == "oee"
    assert cube_router.resolve_cube_name("bilinmeyen", schema) == "bilinmeyen"


def test_refine_noop_ayni_boyut(schema):
    """İstek zaten raporda olan boyutu istiyorsa → LLM'e düşmeden aynı rapor (no-op)."""
    prev = {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["vardiya", "hafta_gunu"]}
    det = cube_router.deterministic_refine(prev, _norm("haftanın günleri bazında"), schema)
    assert det is not None
    assert det.get("dimensions") == ["vardiya", "hafta_gunu"]
    assert "timeDimensions" not in det  # gün kovası EKLENMEMELİ


# --- tarih filtreleri (deterministik dönem, ADR-0007 Faz C) ------------------
#
# Tekil `date_filter` 2026-08-02'de SİLİNDİ (docstring'i "geriye uyum" diyordu, üretimde
# 0 çağıran vardı). Aşağıdaki şartname KAYBOLMADI: canlı çoğul `date_filters`'a taşındı —
# aynı ifadeler, aynı beklentiler. Silinen şey fonksiyondu, kural değil.

def _gte(q: str):
    """`date_filters` çıktısındaki `gte` filtresi (dönem başlangıcı)."""
    return next(f for f in cube_router.date_filters(_norm(q), "tarih")
                if f["operator"] == "gte")


def test_date_filter_son_3_ay():
    f = _gte("son 3 ay")
    assert date.fromisoformat(f["value"]) < date.today()


def test_date_filter_bu_ay():
    assert date.fromisoformat(_gte("bu ay")["value"]) == date.today().replace(day=1)


def test_date_filter_bu_yil():
    assert date.fromisoformat(_gte("bu yıl")["value"]) == date.today().replace(month=1, day=1)


@pytest.mark.parametrize("ifade", [
    "bu ay", "son 6 ay", "temmuz ayı", "tüm zamanlar",
    # önceki takvim dönemleri (log 2026-07-20: "geçen ay" gereksiz soruyordu)
    "geçen ay", "bir önceki ay", "geçen hafta", "geçen yıl", "dün",
    "2. çeyrek", "ikinci çeyrek 2026", "evvelki ay", "dün için",
])
def test_DONEM_IFADELERI_gercek_akista_karsilaniyor(ifade, schema):
    """⟳ **`is_period_only` KALDIRILDI — şartnamesi buraya TAŞINDI.**

    Fonksiyon üretimde **hiç çağrılmıyordu** (denetim: 0 prod referansı, 13 test) ve
    kendi docstring'i şunu diyordu: *"doğru kapanış: testleri gerçek akışın (refine)
    şartnamesine çevirip fonksiyonu kaldırmak — ayrı bir tur."*

    🔴 Bu, o tur. Ama **önce şartname taşındı, sonra fonksiyon kaldırıldı** — tersi sıra
    13 Türkçe dönem ifadesinin karşılanıp karşılanmadığını **ölçen hiçbir şey bırakmazdı**.
    *Ölü sanılan bir fonksiyonu silmek ucuzdur; onunla birlikte silinen şartnameyi geri
    getirmek değildir.*

    ⚠ Ölçülen şey artık **fonksiyonun kendisi değil, davranış**: takip mesajı yalnız bir
    dönem ifadesiyse `deterministic_refine` onu bir **dönem düzenlemesi** olarak
    karşılamalı — yani `filters` üretmeli ve ölçü/kırılımı **korumalı**.
    """
    meta = next(c for c in schema["cubes"] if c.get("time_dimensions"))
    prev = {"cube": meta["name"], "measures": [(meta.get("measures") or [""])[0]],
            "dimensions": list(meta.get("dimensions") or [])[:1],
            "filters": [{"dimension": "tarih", "operator": "gte",
                         "value": "2026-01-01"}]}
    cq = cube_router.deterministic_refine(prev, _norm(ifade), schema)
    assert cq is not None, (
        f"`{ifade}` bir dönem ifadesi ama zincir onu karşılamadı — kullanıcı "
        f"netleştirmeye cevap verdiğinde duvara çarpar.")
    # ⚠ *"Tüm zamanlar"* bir dönem **EKLEMEZ, KALDIRIR** — ve `period_confirmed` ile
    # damgalar. İlk yazımda bunu bir kusur sandım; ölçünce doğru davrandığı görüldü.
    # *Bir beklentinin karşılanmaması, davranışın yanlış olduğu anlamına gelmez.*
    if cube_router.is_all_time(_norm(ifade)):
        assert cq.get("period_confirmed") is True, (
            f"`{ifade}` tüm-zamanlar ifadesi ama onay damgası yok — sessizce filtresiz "
            f"bir sorgu, kullanıcının sormadığı bir soruya cevaptır.")
        assert not cq.get("filters"), f"`{ifade}` dönem filtresini KALDIRMALI: {cq}"
    else:
        assert cq.get("filters") or cq.get("timeDimensions"), (
            f"`{ifade}` bir dönem üretmedi: {cq}")
    # Ölçü ve kırılım KORUNUR — dönem bir düzenlemedir, yeni bir sorgu değil.
    assert cq["measures"] == prev["measures"]
    assert cq.get("dimensions") == prev.get("dimensions")


def test_DONEM_OLMAYAN_mesaj_donem_duzenlemesi_SAYILMAZ(schema):
    """`is_period_only`'nin negatif vakası da taşındı: *"bu ay toplam üretim"* yalnız bir
    dönem ifadesi **değildir** — bir ölçü de taşır."""
    meta = next(c for c in schema["cubes"] if c.get("time_dimensions"))
    prev = {"cube": meta["name"], "measures": [(meta.get("measures") or [""])[0]],
            "dimensions": []}
    cq = cube_router.deterministic_refine(prev, _norm("bu ay toplam üretim"), schema)
    # Karşılanabilir ya da karşılanmayabilir; şart olan tek şey ÖLÇÜNÜN sessizce
    # değişmemesi — bu mesaj bir dönem düzenlemesi DEĞİLDİR.
    if cq is not None:
        assert cq["measures"] == prev["measures"]


def test_gecen_ay_onceki_takvim_donemi():
    """"geçen ay" = önceki TAKVİM ayı (tam aralık, gte+lte) — netleştirme sorulmaz."""
    from datetime import timedelta

    fs = cube_router.date_filters(_norm("geçen ay"), "tarih")
    assert len(fs) == 2
    end = date.today().replace(day=1) - timedelta(days=1)
    assert fs[0] == {"dimension": "tarih", "operator": "gte",
                     "value": end.replace(day=1).isoformat()}
    assert fs[1]["value"] == end.isoformat()
    # geçen yıl → tam takvim yılı
    fy = cube_router.date_filters(_norm("bir önceki yıl"), "tarih")
    assert fy[0]["value"] == f"{date.today().year - 1}-01-01"
    assert fy[1]["value"] == f"{date.today().year - 1}-12-31"
    # dün → tek gün aralığı
    fd = cube_router.date_filters(_norm("dün"), "tarih")
    assert fd[0]["value"] == fd[1]["value"] == (date.today() - timedelta(days=1)).isoformat()


def test_cekimli_donem_ifadeleri(schema):
    """Log regresyonu (2026-07-20): "bu AYKİ satışlar" — çekimli dönem kelimesi kapsam
    kapısında tanınmayıp dürüstlük kapısına takılıyordu; "bu SENEKİ KARIMIZ" da hem
    dönem hem iyelik çekimi kaçırıyordu."""
    plan = route(schema, "birader bu ayki satışlar toplamı")
    assert plan is not None
    cq = plan["cube_query"]
    assert cq["measures"] == ["toplam_ciro"]
    assert cq["filters"][0]["value"] == date.today().replace(day=1).isoformat()
    plan2 = route(schema, "bu seneki karımız ne kadar")
    assert plan2 is not None
    cq2 = plan2["cube_query"]
    assert cq2["measures"] == ["kar"]
    assert cq2["filters"][0]["value"] == date.today().replace(month=1, day=1).isoformat()
    # "karşılaştır" tuzağı hâlâ güvende (kar! tam-kelime; iyelik çekimi ayrı sinonim)
    q = "kişilerin aylık verimlilik performanslarını karşılaştır ve önceki dönemleri ile de karşılaştır"
    assert route(schema, q) is None


def test_cins_cekimleri_tam_soru(schema):
    """Log (2026-07-21): "kumaş CİNSLERİ ve renklerine göre aylık satış grafiği" —
    "cinsleri" çekimi stop listesindeki sabit çekimlere uymayıp dürüstlük kapısına
    takılıyordu; kök ("cins") tüm çekimleri kapsar. Tam soru tek seferde çözülmeli."""
    plan = route(schema, "kumaş cinsleri ve renklerine göre aylık satış grafiği")
    assert plan is not None
    cq = plan["cube_query"]
    assert cq["measures"] == ["toplam_ciro"]
    assert set(cq["dimensions"]) == {"kumas_cinsi", "renk"}
    assert cq["timeDimensions"][0]["granularity"] == "month"


def test_ceyrek_donem_kova_degil(schema):
    """Log (2026-07-21): "2. çeyrek" DÖNEMDİR (Nis-Haz) — çeyrek KOVASI sanılıp
    timeDimensions ekleniyordu; "dönem 2. çeyrek" de çözülemeyip netleştirme soruyordu."""
    fs = cube_router.date_filters(_norm("2. çeyrek"), "tarih")
    y = date.today().year
    assert fs == [{"dimension": "tarih", "operator": "gte", "value": f"{y}-04-01"},
                  {"dimension": "tarih", "operator": "lte", "value": f"{y}-06-30"}]
    assert cube_router.date_filters(_norm("ikinci çeyrek"), "tarih")[0]["value"] == f"{y}-04-01"
    assert cube_router.date_filters(_norm("2025 4. çeyrek"), "tarih")[1]["value"] == "2025-12-31"
    # dönem ifadesi kova TETİKLEMEZ; salt kova ifadeleri çalışmaya devam eder
    assert cube_router._time_gran(_norm("2. çeyrek")) is None
    assert cube_router._time_gran(_norm("çeyreklere göre")) == "quarter"
    # ⟳ Son iki satır `is_period_only` çağırıyordu; fonksiyon KALDIRILDI (denetim D3).
    # Şartname gerçek akışa taşındı — chip/takip mesajı olarak tanınmanın kanıtı artık
    # `date_filters`'ın **gerçekten** bir aralık üretmesidir (yukarıdaki satırlar) ve
    # `test_DONEM_IFADELERI_gercek_akista_karsilaniyor` bunu `deterministic_refine`
    # üstünden bir kez daha ölçer. *Bir yeteneğin kanıtı, onu kullanan yoldur.*
    assert cube_router.date_filters(_norm("dönem 2. çeyrek"), "tarih")
    assert cube_router.date_filters(_norm("ikinci çeyrek için"), "tarih")
    # refine: rapora dönem uygulanır, kova EKLENMEZ
    prev = {"cube": "parti", "measures": ["fire_orani_yuzde"], "dimensions": ["hafta_gunu"],
            "filters": [{"dimension": "tarih", "operator": "gte", "value": "2026-01-01"}]}
    det = cube_router.deterministic_refine(prev, _norm("2. çeyrek"), schema)
    assert det is not None and "timeDimensions" not in det
    ops = sorted(f["operator"] for f in det["filters"])
    assert ops == ["gte", "lte"]


def test_gecen_aya_gore_hala_karsilastirma(schema):
    """"geçen aya GÖRE" dönem DEĞİL karşılaştırmadır → cube'a sığmaz, LLM yolu."""
    assert route(schema, "üretimi geçen aya göre karşılaştır") is None
    # yalın "geçen ay" ise taze soruda dönem filtresi olarak çözülür
    plan = route(schema, "geçen ay toplam üretim")
    assert plan is not None
    ops = {f["operator"] for f in plan["cube_query"]["filters"]}
    assert ops == {"gte", "lte"}


def test_ay_adi_tarih_araligi():
    """"temmuz ayı" → 1-31 Temmuz aralığı (gte+lte); yıl yoksa geçmişteki en yakın."""
    fs = cube_router.date_filters(_norm("temmuz ayında"), "tarih")
    assert len(fs) == 2
    assert fs[0]["operator"] == "gte" and fs[0]["value"].endswith("-07-01")
    assert fs[1]["operator"] == "lte" and fs[1]["value"].endswith("-07-31")
    # "aralık" tek başına belirsiz ("tarih aralığı") → ay sayılmaz; "aralık ayı" sayılır
    assert cube_router.date_filters(_norm("tarih aralığı seç"), "tarih") == []
    assert len(cube_router.date_filters(_norm("aralık ayı"), "tarih")) == 2


def test_tek_gun_ay_toplamina_donusmez():
    """Canlı bulgu (31 Temmuz 2026): "1 nisan" tüm Nisan'a değil O GÜNE (tek gün, gte=lte)
    çözülmeli — önceden gün numarası yok sayılıp `_month_range_filters` tüm ayı dönüyordu
    (sessiz-yanlış: kullanıcı NET bir gün sordu, ay-toplamı aldı)."""
    fs = cube_router.date_filters(_norm("1 nisan"), "tarih")
    assert len(fs) == 2
    assert fs[0] == {"dimension": "tarih", "operator": "gte", "value": fs[0]["value"]}
    assert fs[0]["value"] == fs[1]["value"]  # gte == lte → tek gün
    assert fs[0]["value"].endswith("-04-01")

    # "günü" ekiyle de aynı (gerçek kullanıcı ifadesi: "1 nisan günü ram 3 için ...")
    fs2 = cube_router.date_filters(_norm("1 nisan gunu"), "tarih")
    assert fs2 == fs

    # Yıl açıkça verilirse o yıl kullanılır; bare ay adı hâlâ TÜM AYI döner (regresyon yok).
    fs3 = cube_router.date_filters(_norm("15 mart 2026"), "tarih")
    assert fs3[0]["value"] == fs3[1]["value"] == "2026-03-15"
    fs4 = cube_router.date_filters(_norm("nisan ayi"), "tarih")
    assert fs4[0]["value"].endswith("-04-01") and fs4[1]["value"].endswith("-04-30")

    # Aralık/açık-uçlu ifadeler tek-gün mekanizmasına YAKALANMAZ (öncelik sırası korunur).
    rng = cube_router.date_filters(_norm("1 ocak 31 mart arasi"), "tarih")
    assert rng[0]["value"].endswith("01-01") and rng[1]["value"].endswith("03-31")
    opn = cube_router.date_filters(_norm("1 marttan itibaren"), "tarih")
    assert opn[0]["value"].endswith("03-01")


def test_refine_temmuz_ayi_yutulmaz(schema):
    """Log regresyonu: "temmuz ayı için ..." no-op'a YUTULMAMALI — tarih aralığı uygulanır."""
    prev = {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["hafta_gunu"],
            "filters": [{"dimension": "cinsiyet", "operator": "eq", "value": "Kadın"},
                        {"dimension": "tarih", "operator": "gte", "value": "2026-01-01"}]}
    det = cube_router.deterministic_refine(prev, _norm("temmuz ayı için haftanın günü ortalamaları"), schema)
    assert det is not None
    tarih = [f for f in det["filters"] if f["dimension"] == "tarih"]
    assert {f["operator"] for f in tarih} == {"gte", "lte"}
    assert tarih[0]["value"].endswith("-07-01")  # eski 01-01 filtresi değişti
    assert any(f["dimension"] == "cinsiyet" for f in det["filters"])  # filtre korunur


def test_refine_deger_filtresi_deterministik(schema):
    """"kadın çalışanlar için peki?" → LLM'siz cinsiyet=Kadın (Erkek'i değiştirir).
    Cinsiyet parti cube'unda (operatör köprüsü) — OEE makine metriği kişi taşımaz."""
    prev = {"cube": "parti", "measures": ["toplam_agirlik_kg"], "dimensions": ["hafta_gunu"],
            "filters": [{"dimension": "cinsiyet", "operator": "eq", "value": "Erkek"}]}
    det = cube_router.deterministic_refine(prev, _norm("kadın çalışanlar için peki?"), schema)
    assert det is not None
    assert {"dimension": "cinsiyet", "operator": "eq", "value": "Kadın"} in det["filters"]
    assert not any(f.get("value") == "Erkek" for f in det["filters"])


# --- deterministik refine (LLM'siz konuşmasal düzenleme) ---------------------

def test_refine_aylara_gore(schema):
    prev = {"cube": "oee", "measures": ["toplam_uretim_kg"],
            "filters": [{"dimension": "tarih", "operator": "gte", "value": "2026-01-20"}]}
    cq = cube_router.deterministic_refine(prev, _norm("aylara göre toplam üretim"), schema)
    assert cq is not None
    assert cq["timeDimensions"][0]["granularity"] == "month"
    # önceki tarih filtresi korunur
    assert any(f["dimension"] == "tarih" for f in cq["filters"])


def test_refine_kirilim_ekle(schema):
    prev = {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["makine"]}
    cq = cube_router.deterministic_refine(prev, _norm("vardiyalara göre de"), schema)
    assert cq is not None
    assert cq["dimensions"] == ["makine", "vardiya"]


def test_refine_en_dusuk_siralama(schema):
    prev = {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["makine"]}
    cq = cube_router.deterministic_refine(prev, _norm("en düşükleri göster"), schema)
    assert cq is not None
    assert cq["order"] == {"measure": "ort_oee", "direction": "asc"}


def test_refine_olcu_degisirse_none(schema):
    # farklı metrik açıkça isteniyorsa refine değil, yeni sorgu (LLM sınıflandırsın)
    prev = {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["makine"]}
    assert cube_router.deterministic_refine(prev, _norm("toplam fire ne kadar"), schema) is None


def test_refine_karsilanamayan_kirilim_none_doner(schema):
    """Genel kök-neden düzeltmesi (1 Ağustos 2026, canlı bulgu): önceki cube_query
    (oee, makine=RAM-2 filtresiyle) içindeyken "personel bazlı verimlilikleri karşılaştır
    son 6 ay" dendiğinde — oee'de personel/operatör boyutu YOK — eski kod eski makine
    filtresini SESSİZCE KORUYUP yalnız dönemi güncelleyip "başarılı" bir cevap
    döndürüyordu (RAM-2'nin OEE trendini, sorulan şeyle HİÇ ilgisi olmadan). Artık None
    dönerek çağıranın (ask.py) zaten var olan düşme zincirine (cross_cube_add →
    cross_cube_dim_switch → fresh route() → Discovery) ulaşmasını sağlıyor."""
    prev = {"cube": "oee", "measures": ["ort_oee"],
            "filters": [{"dimension": "makine", "operator": "eq", "value": "RAM-2"}]}
    cq = cube_router.deterministic_refine(
        prev, _norm("personel bazlı verimlilikleri karşılaştır son 6 ay"), schema)
    assert cq is None


def test_refine_kirilim_acik_zaman_ifadesiyle_hala_calisir(schema):
    """Regresyon kilidi: yeni koruma yalnız `_time_gran(q) is None` iken devreye girer —
    AÇIK bir zaman-birimi ifadesi ("aylara göre") kendi başına meşru bir istektir, boyut
    eşleşmese bile YANLIŞLIKLA reddedilmemeli (route()'un kırılım-koruması düzeltmesinde
    AYNI yanlış-pozitif sınıfı yakalanmıştı — bkz. test_refine_aylara_gore, bu test onun
    doğrudan bir regresyon kilidi karşılığıdır)."""
    prev = {"cube": "oee", "measures": ["toplam_uretim_kg"],
            "filters": [{"dimension": "tarih", "operator": "gte", "value": "2026-01-20"}]}
    cq = cube_router.deterministic_refine(prev, _norm("aylara göre toplam üretim"), schema)
    assert cq is not None
    assert cq["timeDimensions"][0]["granularity"] == "month"


# --- parse_cube_query: LLM çıktısı doğrulaması (halüsinasyon kapısı) ---------

def test_parse_rejects_unknown_measure(schema):
    import json

    _, index = cube_router.build_catalog(schema)
    bad = json.dumps({"cube": "oee", "measures": ["uydurma_olcu"]})
    assert cube_router.parse_cube_query(bad, index) is None


def test_parse_accepts_valid_with_order(schema):
    import json

    _, index = cube_router.build_catalog(schema)
    ok = json.dumps({
        "cube": "oee", "measures": ["ort_oee"], "dimensions": ["makine"],
        "order": {"measure": "ort_oee", "direction": "asc"}, "limit": 5,
    })
    cq = cube_router.parse_cube_query(ok, index)
    assert cq is not None and cq["order"]["direction"] == "asc" and cq["limit"] == 5


def test_time_gran_ceyrek_yil(schema):
    """Tam kova seti: çeyrek ve yıl da deterministik."""
    from app.llm import _norm as n

    assert cube_router._time_gran(n("çeyreklere göre üretim")) == "quarter"
    assert cube_router._time_gran(n("yıllık ciro")) == "year"
    plan = route(schema, "çeyreklere göre üretim")
    assert plan is not None
    assert plan["cube_query"]["timeDimensions"][0]["granularity"] == "quarter"


def test_calisan_bazli_personel_kirilimi(schema):
    """'operatör bazlı' kişi kırılımıdır — dolgu değil (sessiz yutma). Kişi ekseni parti
    cube'unda (operatör→personel köprüsü); OEE makine metriğidir, kişi taşımaz."""
    prev = {"cube": "parti", "measures": ["toplam_agirlik_kg"], "dimensions": ["hafta_gunu"],
            "filters": [{"dimension": "tarih", "operator": "gte", "value": "2026-01-01"}]}
    det = cube_router.deterministic_refine(prev, _norm("operatör bazlı işlenen kg"), schema)
    assert det is not None
    assert "operator" in det["dimensions"]


def test_tum_yil_donem(schema):
    """'tüm yıl' (log-kanıtlı terfi) = yıl başından beri; artık sorulmaz, çözülür."""
    f = _gte("tüm yıl için yap")
    assert f["value"] == f"{date.today().year}-01-01"


def test_son_n_aya_gore_kova_degil(schema):
    """Log regresyonu: "son 4 AYA göre yap" DÖNEM ifadesidir — "aya göre" parçası
    aylık kova tetiklememeli; "aylara göre" ise kova olmaya devam eder."""
    assert cube_router._time_gran(_norm("son 4 aya göre yap")) is None
    assert cube_router._time_gran(_norm("aylara göre")) == "month"
    assert cube_router._time_gran(_norm("son 2 yıla göre")) is None
    prev = {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["hafta_gunu", "vardiya"],
            "filters": [{"dimension": "tarih", "operator": "gte", "value": "2026-04-20"}]}
    det = cube_router.deterministic_refine(prev, _norm("son 4 aya göre yap"), schema)
    assert det is not None
    assert "timeDimensions" not in det  # kova EKLENMEDİ
    tarih = [f for f in det["filters"] if f["dimension"] == "tarih"]
    assert tarih and tarih[0]["operator"] == "gte"  # dönem güncellendi


def test_acik_uclu_donem_kaliplari(schema):
    """Log terfisi: "1 marttan itibaren" → gte; "15 nisana kadar" → lte (çekimli ay adları)."""
    fs = cube_router.date_filters(_norm("1 marttan itibaren yap"), "tarih")
    assert fs == [{"dimension": "tarih", "operator": "gte", "value": f"{date.today().year}-03-01"}]
    fs = cube_router.date_filters(_norm("hazirandan beri"), "tarih")
    assert fs[0]["value"].endswith("-06-01")
    fs = cube_router.date_filters(_norm("15 nisana kadar"), "tarih")
    assert fs == [{"dimension": "tarih", "operator": "lte", "value": f"{date.today().year}-04-15"}]
    # refine: log vakası — grid'de "1 marttan itibaren yap" artık SORMAZ, uygular
    prev = {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["hafta_gunu", "vardiya"],
            "filters": [{"dimension": "tarih", "operator": "gte", "value": "2026-03-20"}]}
    det = cube_router.deterministic_refine(prev, _norm("1 marttan itibaren yap"), schema)
    assert det is not None
    tarih = [f for f in det["filters"] if f["dimension"] == "tarih"]
    assert tarih == [{"dimension": "tarih", "operator": "gte", "value": f"{date.today().year}-03-01"}]


def test_kesme_isaretli_donem(schema):
    """Canlı log: "15 mart'tan itibaren" — kesme işareti deseni kaçırıp TÜM Mart'a
    düşürüyordu (15 yutuldu). Kesmeler normalize'de silinir; gün korunur."""
    fs = cube_router.date_filters(_norm("15 mart'tan itibaren"), "tarih")
    assert fs == [{"dimension": "tarih", "operator": "gte", "value": f"{date.today().year}-03-15"}]
    fs = cube_router.date_filters(_norm("2026'nın temmuz ayında"), "tarih")
    assert fs[0]["value"] == "2026-07-01" and fs[1]["value"] == "2026-07-31"


# --- Panel P0 düzeltmeleri (2026-07-24, çok-model eleştiri paneli) -----------

def _semi_schema() -> dict:
    """Sentetik cari cube: semi-additive `bakiye` + INTEGER enum boyutu (değer 1..8)."""
    return {
        "models": [{"columns": [
            {"name": "cari_adi", "values": ["ACME", "BEYPI"]},
            {"name": "islem_turu", "values": [str(i) for i in range(1, 9)]},
            {"name": "tarih"},
        ]}],
        "cubes": [{
            "name": "cari",
            "synonyms": ["cari", "bakiye", "hesap"],
            "measures": ["bakiye"],
            "measure_synonyms": {"bakiye": ["bakiye", "net bakiye", "kalan"]},
            "dimensions": ["cari_adi", "islem_turu"],
            "dimension_synonyms": {"cari_adi": ["cari", "musteri", "firma"],
                                   "islem_turu": ["islem turu"]},
            "dimension_labels": {"cari_adi": "cari", "islem_turu": "islem turu"},
            "time_dimensions": ["tarih"],
            "semi_additive": ["bakiye"],
        }],
    }


def test_semi_additive_donemsiz_bakiye_deterministik_kalir():
    # Dönemsiz "bakiye" = TÜM geçmişin SUM'ı = doğru güncel bakiye → deterministik + dönem SORMA
    plan = cube_router.route("bakiye ne kadar", _semi_schema())
    assert plan is not None
    assert plan["cube_query"]["measures"] == ["bakiye"]
    assert plan["period_optional"] is True


def test_semi_additive_zaman_kovasi_llme_duser():
    # "aylara göre bakiye" düz SUM = dönemin net hareketi (sessiz-yanlış) → LLM devralsın
    assert cube_router.route("aylara gore bakiye", _semi_schema()) is None


def test_semi_additive_acik_donem_as_of_guncel_bakiye():
    # "bu ay bakiye" açık dönem → üst sınırsız → gte DÜŞER, tüm-geçmiş SUM = güncel bakiye
    plan = cube_router.route("bu ay bakiye", _semi_schema())
    assert plan is not None
    tarih = [f for f in plan["cube_query"].get("filters", []) if f["dimension"] == "tarih"]
    assert not tarih  # gte dönem filtresi düşürüldü (as-of bugün)
    assert plan["period_optional"] is True


def test_semi_additive_kapali_donem_as_of_lte():
    # "temmuz bakiye" kapalı dönem → dönem-SONU (`lte` 31 Temmuz) bakiyesi, net hareket değil
    plan = cube_router.route("temmuz bakiye", _semi_schema())
    assert plan is not None
    tarih = [f for f in plan["cube_query"].get("filters", []) if f["dimension"] == "tarih"]
    assert len(tarih) == 1 and tarih[0]["operator"] == "lte"
    assert tarih[0]["value"].endswith("-07-31")


def test_sayisal_deger_hayalet_filtre_yok():
    # `\b1\w*` öneki "15/10/1990"ı enum değeri "1" sanıp hayalet WHERE üretiyordu (panel K1)
    assert cube_router._value_token_hit("en cok satan 15 urun", "1") is False
    assert cube_router._value_token_hit("1990 yilindan beri satis", "1") is False
    assert cube_router._value_token_hit("ilk 5 cari borc", "5") is False      # top-N sayısı
    assert cube_router._value_token_hit("son 3 aydaki hareket", "3") is False  # dönem sayısı
    # Gerçek kategorik seçim KORUNUR
    assert cube_router._value_token_hit("sube 2 raporu", "2") is True


def test_tum_zamanlar_aylik_kova_degil():
    """Panel K7: "tüm zamanlar" TÜM-ZAMAN toplamıdır; "zaman" alt dizisi aylık kovayı
    yanlış tetikliyordu ("tüm zamanlar bakiye" → gran=month → semi bloğu None → kayıp).
    "zamana göre" (trend) davranışı korunur."""
    assert cube_router._time_gran(_norm("tüm zamanlar borç")) is None
    assert cube_router._time_gran(_norm("tüm zamanlar satış")) is None
    assert cube_router._time_gran(_norm("tüm zamanlar bakiye")) is None
    # trend ifadesi korunur
    assert cube_router._time_gran(_norm("zamana göre satış")) == "month"
    # semi ölçüde "tüm zamanlar bakiye" artık deterministik (as-of bugün = güncel bakiye)
    plan = cube_router.route(_norm("tüm zamanlar bakiye"), _semi_schema())
    assert plan is not None and plan["cube_query"]["measures"] == ["bakiye"]


def _two_cube_schema() -> dict:
    """ticaret + mal aynı satis_tutari'yi paylaşır (gerçek belirsizlik); ölçü/boyut kanıtı
    ayırır. Sinonimler NORMALİZE (ascii) — wren_service._syns çıktısıyla aynı biçim."""
    return {
        "models": [{"columns": [{"name": "cari_ref"}, {"name": "stok_ref"}, {"name": "tarih"}]}],
        "cubes": [
            {"name": "ticaret", "synonyms": ["satis", "ciro", "fatura"],
             "measures": ["satis_tutari", "satis_fatura_sayisi"],
             "measure_synonyms": {"satis_tutari": ["satis", "satis tutari", "ciro"],
                                  "satis_fatura_sayisi": ["fatura sayisi"]},
             "dimensions": ["cari_ref"], "dimension_synonyms": {"cari_ref": ["cari", "cari ref", "musteri"]},
             "dimension_labels": {"cari_ref": "cari ref"}, "time_dimensions": ["tarih"], "semi_additive": []},
            {"name": "mal", "synonyms": ["miktar", "kilo", "mal hareketi"],
             "measures": ["satis_miktari", "satis_tutari"],
             "measure_synonyms": {"satis_miktari": ["satis miktari", "miktar", "kac kilo"],
                                  "satis_tutari": ["satis", "satis tutari"]},
             "dimensions": ["stok_ref"], "dimension_synonyms": {"stok_ref": ["stok", "stok ref", "urun"]},
             "dimension_labels": {"stok_ref": "stok ref"}, "time_dimensions": ["tarih"], "semi_additive": []},
        ],
    }


def test_olcu_kaniti_en_spesifik_kazanir():
    # "satış miktarı" → mal.satis_miktari ("satış miktarı" ⊃ "satış"); ticaret'e gitmez
    plan = cube_router.route(_norm("satış miktarı"), _two_cube_schema())
    assert plan is not None and plan["cube_query"]["cube"] == "mal"
    assert plan["cube_query"]["measures"] == ["satis_miktari"]


def test_boyut_kaniti_belirsiz_olcuyu_ayirir():
    sc = _two_cube_schema()
    # satis_tutari HEM ticaret HEM mal'da; boyut ayırır:
    p1 = cube_router.route(_norm("stok ref bazında satış tutarı"), sc)
    assert p1 is not None and p1["cube_query"]["cube"] == "mal"      # stok_ref yalnız mal'da
    p2 = cube_router.route(_norm("cari ref bazında satış tutarı"), sc)
    assert p2 is not None and p2["cube_query"]["cube"] == "ticaret"  # cari_ref yalnız ticaret'te


def test_cube_pin_ambiguity_cozumu():
    """Canlı gitas log 2026-07-24: ambiguous 'satış tutarı' (ticaret+mal) → 'hangisi?'
    chip'i seçince cube-pin route_schema'yı tek cube'a indirir → döngü biter, deterministik.
    ask.py pin_cube → route(q, tek-cube-şema); burada pin'in ÖZÜ (kısıtlı şema) test edilir."""
    sc = _two_cube_schema()
    # satis_tutari HEM ticaret HEM mal'da → measure_cube_candidates ambiguity üretir (chip tetiği)
    cands = {c["name"] for c, _m in cube_router.measure_cube_candidates(_norm("satis tutari"), sc)}
    assert "mal" in cands  # en az bir aday cube-düzeyi eşleşmeden ölçüyle yakalanır
    # Pin: yalnız mal görünür → deterministik mal (chip tekrar sorulmaz, döngü biter)
    mal_only = {**sc, "cubes": [c for c in sc["cubes"] if c["name"] == "mal"]}
    plan = cube_router.route(_norm("satis tutari"), mal_only)
    assert plan is not None and plan["cube_query"]["cube"] == "mal"
    # Pin: yalnız ticaret → deterministik ticaret
    tic_only = {**sc, "cubes": [c for c in sc["cubes"] if c["name"] == "ticaret"]}
    plan2 = cube_router.route(_norm("satis tutari"), tic_only)
    assert plan2 is not None and plan2["cube_query"]["cube"] == "ticaret"


def _asimetrik_olcu_kaniti_schema() -> dict:
    """Gerçek demo-boyahane parti/ticaret çakışmasının küçültülmüş, hermetik izomorfu
    (canlı bulgu, 1 Ağustos 2026): "satis" hem A'nın (ÖLÇÜ sinonimi OLARAK) hem B'nin
    (YALNIZ cube-kimliği, HİÇ ölçü sinonimi YOK) kimliğidir. B'ye ÖZGÜ bir boyutu var
    (A'da YOK) — gerçek örnekte bu "tür" (yalnız ticaret'te), burada "tur" olarak."""
    return {
        "models": [{"columns": []}],
        "cubes": [
            {"name": "b_ticaret_gibi", "synonyms": ["satis", "fatura"],
             "measures": ["toplam_tutar"], "measure_synonyms": {"toplam_tutar": ["fatura tutari"]},
             "default_measure": "toplam_tutar",
             "dimensions": ["tur"], "dimension_synonyms": {"tur": ["tur", "tip"]},
             "dimension_labels": {}, "time_dimensions": ["tarih"], "semi_additive": []},
            {"name": "a_parti_gibi", "synonyms": ["satis", "ciro", "fire"],
             "measures": ["toplam_ciro"], "measure_synonyms": {"toplam_ciro": ["ciro", "satis"]},
             "dimensions": ["makine"], "dimension_synonyms": {"makine": ["makine"]},
             "dimension_labels": {}, "time_dimensions": ["tarih"], "semi_additive": []},
        ],
    }


def test_olcu_kaniti_bos_taraf_kirilim_sahibine_kaybeder():
    """Genel kök-neden düzeltmesi (1 Ağustos 2026, canlı bulgu — "türlere göre satış
    trendi" HER ZAMAN parti'ye gidiyordu, "tür" boyutu YALNIZ ticaret'te olmasına
    rağmen): rakip adayın ölçü-kanıtı SIFIRSA (`snd_syn` boş), eski kod bunu her zaman
    "spesifik eşleşme" sayıp EZBERE kazandırıyordu — asıl kırılımı karşılayabilen (ama
    ölçü-kanıtsız) aday KAYBEDİYORDU."""
    sc = _asimetrik_olcu_kaniti_schema()
    plan = cube_router.route(_norm("satış trendini tür bazında göster"), sc)
    assert plan is not None and plan["cube_query"]["cube"] == "b_ticaret_gibi"
    assert plan["cube_query"]["dimensions"] == ["tur"]


def test_olcu_kaniti_kirilim_ipucu_yoksa_degismez():
    """Kırılım ipucu (`_BREAKDOWN_HINTS`) YOKSA yeni kural HİÇ devreye girmez — bare bir
    konu kelimesi (gerçek katalogdaki bakım/oee "arıza" çakışması gibi) yanlışlıkla
    etkilenmesin diye BİLİNÇLİ sınır. Ölçü-kanıtı OLAN aday (a_parti_gibi) kazanmaya
    devam eder."""
    sc = _asimetrik_olcu_kaniti_schema()
    plan = cube_router.route(_norm("satış"), sc)
    assert plan is not None and plan["cube_query"]["cube"] == "a_parti_gibi"


def test_boyut_kaniti_iki_taraf_da_olcu_kaniti_tasiyorsa_degismez():
    """Regresyon kilidi: rakip adayın ölçü-kanıtı BOŞ DEĞİLSE (iki taraf da ölçü
    sinonimi taşıyorsa) yeni kural devreye GİRMEZ — mevcut, test edilmiş davranış
    (test_boyut_kaniti_belirsiz_olcuyu_ayirir ile AYNI iki-cube şeması) korunur."""
    sc = _two_cube_schema()
    p1 = cube_router.route(_norm("stok ref bazında satış tutarı"), sc)
    assert p1 is not None and p1["cube_query"]["cube"] == "mal"
    p2 = cube_router.route(_norm("cari ref bazında satış tutarı"), sc)
    assert p2 is not None and p2["cube_query"]["cube"] == "ticaret"


def test_refine_gran_ekleyince_row_limit_entity_limite_donusur(schema):
    """Canlı gitas log 2026-07-24: "en çok 20 ürün" (limit:20) → "aylık" deyince
    limit:20 SATIR limitine dönüşüp aylık seriyi 20 satıra kesiyordu. Zaman kovası
    eklenince row-limit → entity_limit (20 VARLIK, hepsinin tüm ayları)."""
    prev = {"cube": "parti", "measures": ["toplam_ciro"], "dimensions": ["musteri"],
            "filters": [{"dimension": "tarih", "operator": "gte", "value": "2026-01-01"}],
            "order": {"measure": "toplam_ciro", "direction": "desc"}, "limit": 20}
    cq = cube_router.deterministic_refine(prev, _norm("aylık"), schema)
    assert cq is not None
    assert cq["timeDimensions"][0]["granularity"] == "month"
    assert "limit" not in cq and "order" not in cq  # row-limit kaldırıldı
    assert cq["entity_limit"] == {"dimension": "musteri", "measure": "toplam_ciro",
                                  "direction": "desc", "n": 20}


def test_measure_threshold_having():
    """Ölçü-eşiği ('10 milyon üzeri' = HAVING): parse + route measure_having (canlı gitas)."""
    assert cube_router._measure_threshold(_norm("10 milyon üzeri")) == {"op": ">", "value": 10_000_000}
    assert cube_router._measure_threshold(_norm("100 bin altında")) == {"op": "<", "value": 100_000}
    assert cube_router._measure_threshold(_norm("5 milyar tl den fazla")) == {"op": ">", "value": 5_000_000_000}
    assert cube_router._measure_threshold(_norm("50 milyon tl'nin altında")) == {"op": "<", "value": 50_000_000}
    assert cube_router._measure_threshold(_norm("satış raporu")) is None
    # route: eşik → cube_query.measure_having (cube_sql dış-WHERE ile uygular)
    sc = _two_cube_schema()
    plan = cube_router.route(_norm("stok ref bazında satış tutarı 1 milyon üzeri"), sc)
    assert plan is not None
    assert plan["cube_query"]["measure_having"] == {"measure": "satis_tutari", "op": ">", "value": 1_000_000}


# --- Faz 2b: makine_duruslari (duruş nedeni) — çakışma koruması + doğru yönlendirme ----

def test_durus_nedeni_dogru_cubea_yonlenir(schema):
    """"duruş nedenlerine göre toplam duruş" → yeni makine_duruslari cube'u (neden kırılımı) —
    OEE'nin bare "duruş" kimliğiyle YARIŞ ama en-uzun-eşleşme kuralıyla bu cube kazanır."""
    plan = cube_router.route(_norm("duruş nedenlerine göre toplam duruş bu yıl"), schema)
    assert plan is not None
    cq = plan["cube_query"]
    assert cq["cube"] == "makine_duruslari"
    assert cq["measures"] == ["toplam_sure_dk"]
    assert cq["dimensions"] == ["neden"]


def test_bare_durus_hala_oeeye_gider(schema):
    """Yeni cube, OEE'nin bare "duruş" sorularını ÇALMAMALI (çakışma koruması regresyonu).

    ⟳ **2026-08-02 (Faz 2a-3) — vaka listesi DÜZELTİLDİ, kural değil.** Test "bare" diyordu
    ama listesinde bare OLMAYAN bir vaka vardı: *"makine bazında **toplam duruş**"*.
    `"toplam durus"` `makine_duruslari.toplam_sure_dk`'nın **kendi sinonimidir** ve aynı
    ölçünün kardeş sinonimi `"toplam durus dakikasi"` zaten oraya gidiyordu — yani çalınan
    şey OEE'nin sorusu değil, `makine_duruslari`'nın **kendi** sorusuydu.

    Üç bağımsız kanıt:
      * bir üstteki test (`..._durus_nedenine_gore`) AYNI çifti *"en-uzun-eşleşme kuralıyla
        bu cube kazanır"* diyerek zaten `makine_duruslari` lehine çözmüş — bu test onunla
        çelişiyordu
      * `tests/test_sinonim_carpismasi.py`'nin ÖLÇÜLEN envanteri `('toplam durus',
        makine_duruslari → oee)` satırını **YANLIŞ-CUBE** olarak kaydetmişti
      * `makine_duruslari` `makine` boyutuna **sahip** — kırılım gerçekten karşılanıyor
        (SQL derlendi: `SELECT makine, SUM(sure_dk) … GROUP BY 1`)

    Testin ASIL koruduğu şey — **çıplak** "duruş" — aynen duruyor ve aşağıda kilitli.
    """
    plan = cube_router.route(_norm("makine bazında duruş bu yıl"), schema)
    assert plan is not None and plan["cube_query"]["cube"] == "oee"

    # ...ve nitelenmiş ifade kendi sahibine gider (yukarıdaki gerekçe).
    plan = cube_router.route(_norm("makine bazında toplam duruş bu yıl"), schema)
    assert plan is not None and plan["cube_query"]["cube"] == "makine_duruslari"
    assert plan["cube_query"]["dimensions"] == ["makine"]
