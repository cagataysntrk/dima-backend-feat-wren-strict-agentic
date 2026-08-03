"""FAZ A — ÖLÇÜM ALETİNİN KENDİSİ DENETLENİYOR (§6.4'ün doğrudan uygulaması).

## Neden bu dosya var

Plan şu sırayı dayatıyor: **ALET → ÖLÇÜT → ÖLÇÜM → KARAR.** Gerekçesi bu oturumda üç kez
ölçüldü:

* `konusma_senaryolari.py --live` **hiçbir zaman canlı değildi** (`tests.conftest`
  sağlayıcıyı `rule`'a sabitliyor) — o modla alınan her "canlı" ölçüm LLM hakkında
  hiçbir şey söylemiyordu.
* `lab/nl_accuracy.py` **tamamen kırıktı**: `TypeError: <lambda>() takes 2 positional
  arguments but 3 were given` → *"0 geçti · 2 kaldı"*, yani **sıfır vaka koşuyordu** ve
  CI'da olmadığı için aylardır görünmemişti.
* `lab/nl_corpus.py` aylarca kırıkken kimse fark etmemişti (MIMARI §6.4'ün özgün dersi).

> **Kırık bir alet üstüne vaka seti büyütmek, ölçmediğini ölçtüğünü sanmaktır.**

Bu testler aletin **kendi** değişmezlerini kilitler: imzalar toleranslı mı, `--live`
gerçekten canlı mı, vaka seti gerçekten dolu mu, A/B koşucusu bilinen bir farkı
görebiliyor mu.
"""

from __future__ import annotations

import inspect

from lab import konusma_senaryolari as ks
from lab import nl_accuracy as na


# --- ALETİN KIRILGANLIĞI: monkeypatch imzaları TOLERANSLI ---------------------------

def test_MONKEYPATCH_imzalari_TOLERANSLI():
    """Bu aracı sessizce öldüren kusur buydu: `dry_plan` üçüncü bir argüman kazandı ve
    dar imza `TypeError` fırlattı → her şirket yüklenemedi, **0 vaka koştu**."""
    govde = inspect.getsource(na._client)
    # ⚠️ ATAMANIN kendisi aranır, ADIN geçtiği yer değil: ilk sürüm `dry_plan` sözcüğünü
    # AÇIKLAMA YORUMUNDA yakaladı ve testi kırdı — bu oturumda altıncı kez bir testim
    # metni davranış sandı.
    for ad in ("_enrich_categorical", "_enrich_cube_dim_values", "dry_plan"):
        atama = f"ws.WrenService.{ad} = lambda"
        assert atama in govde, f"{ad} yamalanmıyor"
        i = govde.index(atama)
        parca = govde[i:i + 100]
        assert "*a, **k" in parca, (
            f"{ad} DAR imzayla yamalanıyor — motor bir argüman eklediği gün araç "
            "sessizce ölür (ölçüldü: aylarca öyle kaldı)")


def test_ARAC_GERCEKTEN_KOSUYOR():
    """En temel değişmez: vaka seti dolu ve şirketler yüklenebiliyor. `0 geçti` bir
    başarı değil, **aletin ölü olduğunun** işaretidir."""
    toplam = sum(len(v) for v in na.CASES.values())
    assert toplam >= 60, f"etiketli vaka sayısı yetersiz: {toplam}"
    assert len(na.CASES) >= 4, f"şirket kapsamı dar: {sorted(na.CASES)}"


# --- VAKA SETİNİN İKİ YARISI --------------------------------------------------------

def test_ZOR_KAZANILMIS_vakalar_SETTE():
    """Üretilen vakalar **inşa gereği** geçer (tautoloji); kapının gücü bu oturumda
    ölçülerek düzeltilmiş vakalardan gelir. Biri silinirse o ders kaybolur."""
    boyahane = [c["q"] for c in na.CASES["boyahane"]]
    beklenen = {
        "bu yıl sapma yüzdesi": "2a-3 en spesifik ölçü kazanır",
        "bu yıl elektrik tüketimi": "2a-1 kimlik SİLMEDEN çözüldü",
        "bu yıl en çok ciro yapan 10 müşteriyi listele": "2a-5 liste niyeti",
        "ocak ve mart ayları toplam fire": "2a-4 ayrık ay",
        "ocak şubat mart ayları ciro": "-0.5a bitişik çoklu ay",
        "merhaba bu yıl makine bazında oee": "D1 sosyal önek R10 vermemeli",
        "iyi çalışmalar, geçen ay fire nedir": "D1 sosyal önek R1 vermemeli",
    }
    eksik = [q for q in beklenen if q not in boyahane]
    assert not eksik, f"zor kazanılmış vaka(lar) silinmiş: {[(q, beklenen[q]) for q in eksik]}"


def test_IKI_YARI_AYRIMI_BELGELI():
    """Üretilen vakaların %100 geçmesi bir başarı göstergesi DEĞİLDİR — tautolojidir.
    Bu ayrım yazılı olmazsa sonraki okuyan sayıyı yanlış okur."""
    kaynak = inspect.getsource(na)
    assert "tautoloji" in kaynak.lower(), "iki yarı ayrımı belgelenmemiş"


# --- `--live` GERÇEKTEN CANLI ------------------------------------------------------

def test_LIVE_gercek_ortami_conftestTEN_ONCE_yakaliyor():
    """Yakalama SAHİBİNDE (`konusma_senaryolari`) ve conftest'ten ÖNCE olmalı."""
    kaynak = inspect.getsource(ks)
    i = kaynak.index("_GERCEK_ORTAM = {")
    j = kaynak.index("import tests.conftest")
    assert i < j, ("gerçek ortam conftest'ten SONRA yakalanıyor — o noktada değerler "
                   "zaten EZİLMİŞ olur ve geri yükleme `rule`'u geri yükler")


def test_LIVE_GERI_YUKLEME_TEK_SAHIP():
    """⟳ FAZ X — KOPYANIN BEDELİ ÖLÇÜLDÜ.

    `nl_accuracy` bu fonksiyonun **kendi kopyasını** taşıyordu. Sahipteki sözleşme
    *"ortamı geri yükle"*den *"AYAR ÖNBELLEĞİNİ de temizle ve gerçekten canlı bir üretici
    kurulduğunu DOĞRULA"*ya yükseltilirken kopya geride kaldı — yani `nl_accuracy --live`
    hâlâ sessizce `rule` ile koşuyordu ve o koşumlara dayanarak **bayrak kararı**
    alınabilirdi. Bir numaralı kusur sınıfının ölçüm katmanındaki hâli.
    """
    assert na._canli_ortami_geri_yukle is ks._canli_ortami_geri_yukle, \
        "nl_accuracy yeniden KENDİ kopyasını tanımlamış — sözleşme ayrışacak"
    kaynak = inspect.getsource(na)
    i = kaynak.index("from lab.konusma_senaryolari import")
    j = kaynak.index("import tests.conftest")
    assert i < j, ("sahip conftest'ten SONRA import ediliyor — yakalama o noktada "
                   "zaten ezilmiş değerleri okur")


def test_LIVE_AYAR_ONBELLEGI_TEMIZLENIYOR():
    """⟳ FAZ X — `--live` ÜÇÜNCÜ KEZ karşılıksız çıktı ve kökü buydu.

    Ortamı geri yüklemek YETMİYOR: `app.config.get_settings` `@lru_cache`'li ve
    **`import app.main` onu doldurur**. Bu araçlar `tests.conftest`'i modül seviyesinde
    yüklediği için önbelleğe `provider="rule"` giriyor; sonraki env geri yüklemesi ona
    HİÇ ULAŞMIYOR. Log kanıtı: "CANLI MOD" yazarken `LLM sağlayıcı: RuleBasedSqlGenerator`.
    """
    govde = inspect.getsource(ks._canli_ortami_geri_yukle)
    assert "cache_clear()" in govde, \
        "ayar önbelleği temizlenmiyor — env geri yüklemesi AYARA ulaşmaz"


def test_LIVE_BEYAN_DEGIL_OLCUM():
    """Env'e bakıp *"canlı"* demek yetmez: gerçekten canlı bir ÜRETİCİ kuruluyor mu?
    Fail-closed — kurulmuyorsa koşmamalı."""
    govde = inspect.getsource(ks._canli_ortami_geri_yukle)
    assert "build_generator" in govde and "RuleBasedSqlGenerator" in govde, \
        "canlılık DOĞRULANMIYOR — beyan yine karşılıksız kalabilir"


def test_LIVE_saglayici_yoksa_KOSMUYOR():
    """Fail-closed: sessizce `rule` ile koşan bir "canlı" ölçüm, hiç koşmamaktan kötüdür
    — yanlış bir güven verir ve o güvene dayanarak bayrak kararı alınır."""
    govde = inspect.getsource(na._canli_ortami_geri_yukle)
    assert "SystemExit" in govde and '"rule"' in govde


def test_LIVE_DB_izolasyonunu_BOZMUYOR():
    """Canlı bir ölçüm kullanıcının verisini kirletmemeli."""
    govde = inspect.getsource(na._canli_ortami_geri_yukle)
    i = govde.index("CANLI_YOLU_SUSTURANLAR")
    assert "DIMA_DATABASE_URL" not in govde[i:i + 300], \
        "DB izolasyonu canlı-yolu-susturanlar listesine girmiş"


# --- A/B KOŞUCUSU: bilinen bir farkı GÖREBİLİYOR MU --------------------------------

def test_BAYRAK_ZORLAMA_calisiyor(client):
    """Aletin kendi kendini doğrulaması. `resolve_for` her tüketicide **fonksiyon içinde**
    import ediliyor → modül düzeyinde yamalamak hepsini kapsar."""
    from app import features
    from app.config import get_settings

    s = get_settings()
    with na._BayrakZorla("liste_niyeti", acik=False):
        assert "liste_niyeti" not in features.resolve_for(s, None)
    with na._BayrakZorla("liste_niyeti", acik=True):
        assert "liste_niyeti" in features.resolve_for(s, None)
    # ÇIKIŞTA GERİ ALINIR — ölçüm, ölçtüğü sistemi kalıcı olarak değiştirmemeli.
    assert "liste_niyeti" in features.resolve_for(s, None)


def test_AB_KOSUCUSU_BILINEN_farki_goruyor(client):
    """Planın A-kapısı: *"A3 bilinen bir farkı yeniden üretebilmeli"*. `liste_niyeti`
    KAPALIYKEN *"…listele"* vakası düşer, AÇIKKEN geçer — ölçüldü (kurtarılan=1).
    Alet bu farkı göremiyorsa bayrak ölçümlerinin hiçbirine güvenilemez."""
    from tests.conftest import ask

    soru = "bu yıl en çok ciro yapan 10 müşteriyi listele"
    with na._BayrakZorla("liste_niyeti", acik=False):
        kapali = ask(client, soru)
    with na._BayrakZorla("liste_niyeti", acik=True):
        acik = ask(client, soru)
    k_dims = (kapali.get("cube_query") or {}).get("dimensions") or []
    a_dims = (acik.get("cube_query") or {}).get("dimensions") or []
    assert "musteri" in a_dims and "musteri" not in k_dims, (
        f"A/B bilinen farkı GÖREMİYOR (kapalı={k_dims} açık={a_dims}) — bayrak "
        "ölçümlerinin hiçbiri güvenilir değil")


def test_AB_GERILEME_ve_KAZANC_ayri_olculuyor():
    """Etiketli vakalar `route()`'un zaten çözdüğü sorulardır; bir LLM bayrağı orada
    kazanç ÜRETEMEZ, ama BOZABİLİR. Kazanç ayrı bir korpus ister (bayrağın hedef
    nüfusu) — iki mod bu yüzden ayrı."""
    assert hasattr(na, "ab_kos") and hasattr(na, "ab_kurtarma_kos")
    govde = inspect.getsource(na.ab_kurtarma_kos)
    # ⟳ KORPUS DÜZELTİLDİ: katalog sinonimleri YANLIŞ nüfustu (orada `route()` çoğunlukla
    # BELİRSİZLİK yüzünden düşer ve yeniden yazmak belirsizliği çözmez). Enhancer'ın
    # hedefi katalog DIŞI doğal ifadelerdir → `REAL_PHRASINGS`.
    assert "REAL_PHRASINGS" in govde, \
        "kurtarma korpusu DOĞAL İFADELERDEN üretilmiyor — yanlış nüfus ölçülür"
    assert "cr.route(cr._norm(q), sch) is None" in govde, \
        "korpus `route()`'un ÇÖZEMEDİĞİ sorulardan süzülmüyor"
    assert "time.sleep(5" in govde, "hız sınırı yok — 10 sn/10 istek tavanı aşılabilir"


def test_KURTARMA_MODU_gercek_saglayici_ZORUNLU():
    """⚠️ Bu kapıyı kurup **kullanmayı unuttum**: `--ab-kurtarma`'yı `--live` olmadan
    koştum, sağlayıcı `rule`'a sabitliydi ve **0/14 kurtarma** çıktı — *"kazanç yok"* gibi
    okunuyordu, oysa ölçüm *"ölçmedim"* diyordu. Uyarı yeterli değildir; mod kendi ön
    koşulunu ZORUNLU kılmalı."""
    govde = inspect.getsource(na.ab_kurtarma_kos)
    assert "_canli_ortami_geri_yukle()" in govde, \
        "kurtarma modu `rule` sağlayıcıyla SESSİZCE koşabiliyor — ölçtüğünü sanır"


def test_KURTARMA_DOGRULUGU_da_olculuyor():
    """*"Cevap geldi"* ile *"DOĞRU cevap geldi"* bu depoda ayrı şeylerdir (§4.7-6).
    `REAL_PHRASINGS` beklenen ölçüyü bildiği için ikisi de ölçülebilir."""
    govde = inspect.getsource(na.ab_kurtarma_kos)
    assert "DOĞRU ölçüyle" in govde and "acik[q] == o" in govde, \
        "kurtarmanın DOĞRU ölçüye gidip gitmediği ölçülmüyor"
