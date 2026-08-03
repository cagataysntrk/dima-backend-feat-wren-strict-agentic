"""FAZ 2b — K2(ii): terfi kuyruğu + ÖLÇÜME BAĞLI iki karar.

## 2b-1 — Red gerekçesi TRİYAJA girdi

Faz 0 `reject_reason`'ı ölçülebilir yaptı ama **tüketicisi yoktu** — bu deponun en sık
kusuru (*"beyan var, kod onu tanımıyor"*). Planın K2(ii) şartı açıktı: *"önceliği Faz 0'ın
red-gerekçesi telemetrisi belirler — **en çok hangi kelime kapıya takıldı**"*.

Aday kuyruğu artık her aday için `red_kodu` + insan-okur `red_gerekcesi` + **takılan
kelimeleri** taşıyor. Kelimeler `cube_router`'ın kapsam kapısıyla **aynı** dolgu
sözlüğünden hesaplanır — ayrı bir liste tutmak iki tarafı ayrıştırır ve admin'e kapının
gerçekte takıldığı kelimeden BAŞKA bir şey gösterirdi.

**Yeni uç/panel AÇILMADI**: var olan `/sadmin/synonyms/candidates` + `cubes` (field_kind
seçtiren) onay akışı besleniyor. *"Yeni özellik yeni panel doğurmaz."*

## 2b-3 — §1.6-5 KARAR KAPISI: ÖLÇÜLDÜ, AÇILMADI

Plan: *"Faz 0.5'in dönem-düzeltme sınıfında başarısızlıkların **≥%20'si** `Baglam`'ın ham
ifadeyi saklamamasına bağlanıyorsa `ham_ifade` alanı BU FAZIN maddesi olur; altındaysa
§8'in açık-nokta kaydı kalır. **Tahminle taahhüt edilmez, ölçümle açılır.**"*

Ölçüldü (`lab/reports/konusma_senaryolari/donem_duzeltme.md`): 6 senaryonun **5'i geçti**.
Tek başarısızlık `cari-daralt` ve kökü `Baglam` **değil** — ilk adım (`tüm zamanlar borç`)
2a-2'nin netleştirme chip'ine düşüyor (`borç (cari hesap)` / `borç (mizan)`), yani **doğru
davranış**; ikinci adımın çapası hiç oluşmuyor.

→ **%0 < %20 → kapı AÇILMIYOR.** `ham_ifade` bu fazın maddesi değildir; §8'in dürüst
açık-nokta kaydı olarak kalır.

> **Ölçüm aracının kendi hatası da bu turda bulundu:** `_daraldi` kontrolü BEKLENEN
> cube'un zaman boyutunu sabitliyordu; `route()` soruyu başka bir cube'a çözünce
> (`elektrik` → `surdurulebilirlik`) **çalışan** bir düzeltmeyi "başarısız" sayıyordu.
> MIMARI §6.4'ün dersi: *"ölçüm aracının kendisi de bir bağımlılıktır."* Düzeltildi;
> sınıf 4/6 → **5/6**.
"""

from __future__ import annotations

import inspect

from admin_app.routers import synonyms as syn_mod
from app import cube_router as cr


# --- 2b-1: red gerekçesi triyaja girdi -------------------------------------------

def test_ADAY_KUYRUGU_red_gerekcesini_TASIYOR():
    """Faz 0'ın ölçtüğü sinyalin TÜKETİCİSİ olmalı — yoksa ölçüm bir sayıdan ibaret kalır."""
    govde = inspect.getsource(syn_mod.mine_candidates)
    for alan in ("reject_reason", '"red_kodu"', '"red_gerekcesi"', '"takilan_kelimeler"'):
        assert alan in govde, f"aday kuyruğu {alan} taşımıyor"


def test_TAKILAN_KELIME_kapsam_kapisiyla_AYNI_sozlugu_okur():
    """Ayrı bir liste tutmak iki tarafı ayrıştırır ve admin'e kapının GERÇEKTE takıldığı
    kelimeden başka bir şey gösterirdi."""
    govde = inspect.getsource(syn_mod._takilan_kelimeler)
    for fn in ("_period_hit_words", "_misc_hit_words", "_uncovered"):
        assert fn in govde, f"{fn} kullanılmıyor — sözlük ayrıştı"


def test_TAKILAN_KELIME_gercekten_ACIKLANAMAYANI_verir():
    kelimeler = syn_mod._takilan_kelimeler("bu yıl zurnabalik uretimi")
    assert "zurnabalik" in kelimeler, f"katalog dışı kelime yakalanmadı: {kelimeler}"
    assert "yil" not in kelimeler, "dönem kelimesi aday sanıldı"


def test_TAKILAN_KELIME_dolgu_dondurmez():
    """`değişim`/`trend` Faz 0.5'te dolgu sözlüğüne girdi — aday sanılmamalı."""
    assert not (syn_mod._takilan_kelimeler("bu yıl degisim trendi")
                & {"degisim", "trend", "trendi"})


#: Faz 2b ÖNCESİ ölçülen uç sayısı. Bu faz **sıfır** uç ekledi (`git diff`: 0 satır
#: `@router` eklendi) — sinyal var olan `mine_candidates` cevabını ZENGİNLEŞTİRDİ.
SYNONYMS_UC_SAYISI = 7


def test_YENI_UC_ACILMADI():
    """*"Yeni özellik yeni panel doğurmaz."* — bu deponun bağlayıcı kuralı (bkz. yetim-uç
    kapısı). Red-gerekçesi sinyali var olan onay akışını **besledi**, yanına ikinci bir
    yüzey açmadı. Sayı artarsa düzelten kişi ya ucu geri almalı ya bu sabiti bilinçli
    güncellemelidir — sessiz yüzey büyümesi yok."""
    kaynak = inspect.getsource(syn_mod)
    assert kaynak.count("@router.") == SYNONYMS_UC_SAYISI, (
        f"synonyms uç sayısı {kaynak.count('@router.')} — kayıtlı {SYNONYMS_UC_SAYISI}")
    assert "mine_candidates" in dir(syn_mod)


def test_ADMIN_PLANE_WRENSIZ_kosarsa_PATLAMAZ():
    """Admin AYRI bir ASGI süreçtir ve Wren'siz koşabilir — `_takilan_kelimeler` o
    durumda sessizce boş dönmeli, uç noktayı DÜŞÜRMEMELİ."""
    govde = inspect.getsource(syn_mod._takilan_kelimeler)
    assert "except Exception" in govde and "return set()" in govde


# --- 2b-3: §1.6-5 karar kapısı ---------------------------------------------------

def test_DONEM_DUZELTME_kokleri_BAGLAMA_bagli_DEGIL(schema):
    """Karar kapısının dayanağı: `cari-daralt`ın kökü `Baglam` değil, 2a-2'nin
    netleştirmesi. Bu test o gerekçeyi ölçümle sabitler — vaka bayatlarsa kapı yeniden
    değerlendirilmeli."""
    cr.reddi_sifirla()
    r = cr.route(cr._norm("tum zamanlar borc"), schema)
    assert r is None and cr.red_gerekcesi() == "R1", \
        "vaka bayat: `borç` artık belirsiz değil → §1.6-5 kapısı yeniden ölçülmeli"
    adaylar = cr.measure_cube_candidates(cr._norm("tum zamanlar borc"), schema)
    assert len({c["name"] for c, _ in adaylar}) >= 2, "belirsizlik kalktı"


def test_DONEM_DARALTMA_gercekten_CALISIYOR(schema):
    """Kapının kapalı kalmasının pozitif kanıtı: düzeltme deterministik olarak çalışıyor."""
    ilk = cr.route(cr._norm("tum zamanlar arıza sayısı"), schema)
    assert ilk is not None
    sonra = cr.deterministic_refine(ilk["cube_query"], cr._norm("sadece son 3 ay"), schema)
    assert sonra is not None, "dönem daraltma çalışmıyor — kapı yeniden ölçülmeli"
    assert any(f.get("operator") == "gte" for f in (sonra.get("filters") or [])), \
        f"daraltma dönem filtresi üretmedi: {sonra.get('filters')}"


def test_OLCUM_ARACI_cevabin_KENDI_cubeuna_bakiyor():
    """Aracın kendi hatası: beklenen cube'un zaman boyutunu SABİTLEMEK, `route()` başka
    bir cube'a çözünce çalışan düzeltmeyi 'başarısız' sayıyordu (MIMARI §6.4 dersi)."""
    from lab import konusma_senaryolari as ks

    govde = inspect.getsource(ks._uret)
    assert "cq.get(\"cube\")" in govde and "zamanlar = {" in govde, \
        "ölçüm aracı hâlâ beklenen cube'un zaman boyutunu sabitliyor olabilir"


# --- 2b-2: §1.7 KARARI — auto_cube replay'den çıktı, few-shot'ta kaldı ------------

def test_AUTO_CUBE_REPLAYden_CIKTI():
    """§1.7 kararı. Gerekçe **bu oturumun kendi ölçümünden** çıktı: `auto_cube` kaydı
    hem saf `cube` hem `cube+llm` cevaplarından üretiliyor ve saf `cube`'un replay'i
    **sıfır** kazandırır — `route()` onu zaten LLM'siz ve **daha doğru** çözer, çünkü
    **router iyileşir, dondurulmuş kayıt iyileşmez**.

    Kanıt: `elektrik tuketimi` · `toplam durus` · `sapma yüzdesi` · `ortalama sapma` bu
    oturumda **cube değiştirdi**. 2a-3 öncesi yazılmış bir kayıt, düzeltilmiş router'ın
    doğru cevabını **engellerdi** ve `source="vqr"`, `confidence=0.95` rozetiyle gelirdi —
    yani replay yalnız yanlışı kalıcılaştırmaz, **düzeltmeyi de görünmez yapar**."""
    from app import vqr as vqr_mod

    assert "auto_cube" not in vqr_mod._TRUSTED_SOURCES
    assert "auto_cube" in vqr_mod._FEW_SHOT_ONLY_SOURCES
    assert not vqr_mod.is_trusted("auto_cube")


def test_AUTO_CUBE_FEW_SHOTta_KALDI():
    """Kaybedilen "hızlı öğrenme" DEĞİL, **denetimsiz kalıcılaştırma**. Kayıt few-shot'ta
    kalır (her seferinde `parse_cube_query` ile YENİDEN doğrulanarak) ve `/ask/verify`
    onu `user_verified`'a terfi ettirebilir → replay'e girer."""
    import inspect

    from app import vqr as vqr_mod

    govde = inspect.getsource(vqr_mod.VQR.recall)
    assert "is_trusted" not in govde, "few-shot güven filtresi uyguluyor — kayıt kayboldu"
    assert "auto_cube" in vqr_mod.KNOWN_SOURCES, "kaynak sınıflandırması dışında kaldı"


def test_INSAN_ONAYI_yolu_ACIK():
    from app import vqr as vqr_mod

    for s in ("user_verified", "chip_approved"):
        assert vqr_mod.is_trusted(s), f"{s} replay'e giremiyor — terfi yolu kapalı"


# --- FAZ 9.15: TANINAN kelimeler aday listelenmemeli ------------------------------
#
# ## Ölçülen kusur (denetim, Faz 9)
#
# `_takilan_kelimeler`, `known` kümesine YALNIZ dolgu sözlüğünü veriyordu
# (`_period_hit_words | _misc_hit_words`); cube/ölçü/boyut sinonimleri **hiç
# eklenmiyordu**. Ölçüldü — admin'e şunlar aday olarak gösteriliyordu:
#
#     "bu yil ciro"           → ['ciro']      ← `parti.toplam_ciro`'nun ZATEN sinonimi
#     "musteri bazinda borc"  → ['borc', 'musteri']
#
# Yani triyaj kuyruğu, kapsam boşluğu göstermek yerine kataloğun **var olan sözlüğünü**
# tekrar öneriyordu ve gerçek boşluklar bu gürültünün içinde kayboluyordu. Dosyanın kendi
# docstring'i *"ayrı liste tutmak iki tarafı ayrıştırır"* diye uyarıyordu — uyarı tam da
# kendisi için geçerliydi.

def test_TANINAN_kelime_ADAY_LISTELENMIYOR(client):
    from admin_app.routers.synonyms import _takilan_kelimeler

    for soru in ("bu yil ciro", "musteri bazinda borc"):
        adaylar = _takilan_kelimeler(soru)
        assert not adaylar, (
            f"{soru!r} → {sorted(adaylar)}: katalogda TANINAN kelime sinonim adayı "
            "olarak gösteriliyor; admin'e zaten var olan sözlük öneriliyor")


def test_GERCEK_bosluk_YINE_yakalaniyor(client):
    """Kapı fazla geniş olmamalı: düzeltme, aracın ASIL işini bozmamalı."""
    from admin_app.routers.synonyms import _takilan_kelimeler

    assert _takilan_kelimeler("zzz qwerty flimflam ciro") >= {"qwerty", "flimflam"}
    # §1.5'in canlı vakası: gerçek katalog boşluğu "çalışma süresi"dir.
    assert "sureleri" in _takilan_kelimeler("personel bazli calisma sureleri")


def test_KAPSAM_KAPISIYLA_ayni_kaynak(client):
    """İki taraf ayrışırsa admin, kapının gerçekte takıldığından BAŞKA bir kelime görür."""
    import inspect

    from admin_app.routers import synonyms

    govde = inspect.getsource(synonyms._takilan_kelimeler)
    assert "_syn_hit_words" in govde, "katalog sözlüğü kapsam kapısıyla aynı yoldan okunmuyor"
    for kaynak in ("measure_synonyms", "dimension_synonyms", "_known_cubes("):
        assert kaynak in govde, f"{kaynak} okunmuyor — kapsam kapısıyla ayrışma sürüyor"


def test_KATALOG_OKUNAMAZSA_arac_CALISMAYA_devam(client, monkeypatch):
    """Admin plane Wren'siz koşabilir; katalog yoksa araç susmamalı, dolgu sözlüğüyle
    devam etmeli — eski davranış, düzeltmenin ALTINDA korunuyor."""
    from admin_app.routers import synonyms

    monkeypatch.setattr(synonyms, "_known_cubes",
                        lambda slug=None: (_ for _ in ()).throw(RuntimeError("yok")))
    assert synonyms._takilan_kelimeler("zzz qwerty flimflam") >= {"qwerty", "flimflam"}
