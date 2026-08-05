"""FAZ F1 — ARAÇ KAYDI: beyan ile gerçeğin ayrışmasını engelleyen kapılar.

Bu depoda tekrar eden en pahalı hata sınıfı **"yorum doğru olanı söyler, kod onu tanımaz"**
oldu. Bu turda dört örneği ölçüldü:

  · `drill.flag_outliers` — *"yeni istatistik motoru İCAT EDİLMEZ"* yazıp formülü kopyaladı
  · `interpret()` — `cube_query` otoritesini aldı ve **yok saydı**
  · `config.py` — *"üretimde False"* yazıp varsayılanı `True` bıraktı
  · `consistency_k = 3` — bir davranış beyan etti, **sıfır tüketicisi** vardı

Araç kaydı **baştan sona bir beyandır**. Denetlenmezse aynı sınıfın en büyük örneği olur:
planlayıcıya "bu araç deterministiktir, şu izne bağlıdır, şu makbuzu üretir" der ve
hiçbiri doğru olmayabilir. Bu dosya beyanın her alanını gerçeğe karşı sınar.

Kapılar:
  1. **Çözülebilirlik** — beyan edilen her fonksiyon GERÇEKTEN var mı (import edilerek).
  2. **Yetki** — her aracın izni `authorize()` matrisinde VAR mı (uydurma izin = fail-closed).
  3. **Read-only değişmezi** — kayıtta `yan_etki="yazar"` bir araç OLAMAZ.
  4. **Deterministik-önce** — her LLM aracının deterministik bir alternatifi bildirilmiş mi.
  5. **Yetki devredilemez** — düşük rollü kullanıcı, yüksek izinli aracı GÖREMEZ.
  6. **Beyan bütünlüğü** — boş özet/not yok, ad tekrarı yok, LLM şeması tutarlı.
"""

from __future__ import annotations

import pytest

from app import tools
from control_plane.authorize import _ACTION_MIN_RANK, Principal


def test_kayit_BOS_DEGIL():
    assert len(tools.hepsi()) >= 8, "kayıt anlamlı sayıda yetenek taşımalı"


def test_adlar_TEKIL():
    adlar = [a.ad for a in tools.hepsi()]
    assert len(adlar) == len(set(adlar)), f"çift araç adı: {adlar}"


# --- 1. ÇÖZÜLEBİLİRLİK: beyan edilen fonksiyon GERÇEKTEN var mı ------------------

@pytest.mark.parametrize("arac", [a for a in tools.hepsi() if a.baglanma == "modul"],
                         ids=lambda a: a.ad)
def test_modul_araci_COZULUYOR(arac):
    """ASIL KAPI. Bir işaretçi çözülemiyorsa kayıt yalan söylüyordur ve planlayıcı
    çalışma zamanında patlar — üstelik kullanıcının sorusunun ortasında."""
    fn = arac.cagir()
    assert callable(fn), f"{arac.ad}: {arac.modul}.{arac.fonksiyon} çağrılabilir değil"


def test_servis_araclari_KAYNAK_ISTER():
    """Servise bağlı araçlar istek kapsamı olmadan çözülemez — bilinçli. Modül
    seviyesinde "çözülmüş" göstermek hangi tenant'ın motoruna gittiğini gizlerdi."""
    for a in tools.hepsi():
        if a.baglanma == "modul":
            continue
        with pytest.raises(ValueError, match="kaynak"):
            a.cagir()


def test_wren_araci_SERVISE_baglaninca_cozulur():
    """`servis:wren` beyanının gerçek olduğunun kanıtı."""
    from app.config import get_settings
    from app.wren_service import WrenService

    s = get_settings()
    svc = WrenService(project_dir=s.resolved_project_dir(), datasource=s.datasource,
                      connection_info=s.connection_dict())
    for a in tools.hepsi():
        if a.baglanma == "servis:wren":
            assert callable(a.cagir(svc)), f"{a.ad} WrenService'e bağlanamadı"


def test_llm_araci_SAGLAYICIYA_baglaninca_cozulur():
    """`servis:llm` ördek-tiplidir ve **her sağlayıcıda YOKTUR** — kayıt yazılırken
    ölçüldü: `RuleBasedSqlGenerator` (anahtarsız yedek) `select_cube` TAŞIMAZ, üretim
    yolu da bunu `hasattr` ile denetliyor. Bu, planlayıcının bilmesi gereken bir sınırdır
    ve aracın `notlar`ına yazıldı; test onu iki yönlü kilitler."""
    from app.llm import AnthropicSqlGenerator, RuleBasedSqlGenerator

    llm_araclari = [a for a in tools.hepsi() if a.baglanma == "servis:llm"]
    assert llm_araclari, "servis:llm bağlı araç kalmamış — test bir şey korumuyor"
    for a in llm_araclari:
        assert callable(a.cagir(AnthropicSqlGenerator.__new__(AnthropicSqlGenerator))), \
            f"{a.ad} gerçek bir LLM sağlayıcısına bağlanamadı"
        with pytest.raises(AttributeError):
            a.cagir(RuleBasedSqlGenerator())   # yedek sağlayıcıda YOK — beyan bunu söyler


# --- 2. YETKİ: uydurma izin yok --------------------------------------------------

@pytest.mark.parametrize("arac", tools.hepsi(), ids=lambda a: a.ad)
def test_izin_MATRISTE_var(arac):
    """`authorize()` tanımsız aksiyonu fail-closed reddeder; kayıtta uydurma bir izin
    olsaydı o araç HİÇ KİMSEYE görünmez ve sessizce ölürdü — "yetki reddi" gibi
    görünen bir yazım hatası."""
    assert arac.izin in _ACTION_MIN_RANK, (
        f"{arac.ad}: `{arac.izin}` yetki matrisinde YOK — ya matrise ekleyin ya beyanı "
        "düzeltin. Uydurma izin, aracı sessizce erişilemez kılar.")


def test_IZIN_GRANULER_tek_anahtar_DEGIL():
    """🔴 **FAZ 1.3 — ölçülen kusur: 15 aracın 15'i `query:run` taşıyordu.**

    Tek izin, granülerlik değil bir **anahtardır**: `izinli_araclar()` ya **hepsini**
    döndürür ya **hiçbirini**. §11.2'nin *"ajan kullanıcının yetkisini AŞAMAZ"* değişmezi
    o hâlde aşılmıyordu ama **sınırlanamıyordu** da — bir değişmez, uygulanamıyorsa bir
    beyandır.

    ⚠ Kapı *"kaç aksiyon"* diye sormaz (sayı bir hedef olurdu, bölünme teşvik ederdi);
    **tek bir anahtara indirgenmemiş** olmasını ister.
    """
    izinler = {a.izin for a in tools.hepsi()}
    assert len(izinler) > 1, (
        f"tüm araçlar tek izinde: {izinler}. Yetki matrisi 16 aksiyon tanımlıyor ama "
        "kayıt bir tanesini kullanıyor — granülerlik BEYAN düzeyinde kalmış.")


def test_PAHALI_ARAC_VIEWER_RUTBESINDE_DEGIL():
    """🔴 **Yol haritasının 1.3 KAPI'sının adıyla istediği tek davranış değişikliği.**

    Ölçüldü: `contribution.report` maliyet sınıfı **`pahali`** (6 boyut tarama) ve
    `query:run` (rütbe 0) taşıyordu — yani **viewer** rolündeki bir kullanıcının ajanı
    onu çağırabiliyordu. Okuma tarafında bir **maliyet/yetki ayrımı yoktu**.

    ⚠ **Erişilebilirlik dürüstçe yazılıyor:** bugün üründe yalnız `owner` kullanılıyor
    (`CLAUDE.md`: *"rol matrisi uykuda"*), yani bu düzeltmenin **bugünkü kullanıcıya
    etkisi sıfırdır**. Kapatılan şey bir açık değil, bir **değişmezin uygulanabilirliği**:
    roller açıldığı gün ayrım **zaten** yerinde olur — sonradan eklenen bir sınır, o güne
    kadar üretilmiş her alışkanlığı geriye dönük kırar.
    """
    from control_plane.authorize import can

    viewer = _p("viewer")
    pahalilar = [a for a in tools.hepsi() if a.maliyet == "pahali"]
    assert pahalilar, "kayıtta `pahali` araç yok — testin ön koşulu düştü"
    for a in pahalilar:
        assert not can(viewer, a.izin), (
            f"{a.ad}: maliyet `pahali` ama viewer çağırabiliyor (`{a.izin}`). "
            "Okuma tarafında da maliyet/yetki ayrımı olmalı.")
        assert a not in tools.izinli_araclar(viewer)


def test_RUTBE_0_ARACLARDA_DAVRANIS_BIREBIR_AYNI():
    """**KURAL B'nin bu maddedeki karşılığı.** `drill:run` · `contribution:run` ·
    `llm:invoke` bilinçle **rütbe 0**: `query:run`'ı olan herkes onlara da sahip, yani
    granülerlik eklendi ama **davranış kıpırdamadı**. Tek istisna `contribution:scan`.

    Bu test o niyeti kilitler: yeni aksiyonlardan biri sessizce rütbe kazanırsa
    (ör. `llm:invoke` → 1) bugünkü kullanıcı **sessizce yetenek kaybederdi**.
    """
    from control_plane.authorize import can

    viewer = _p("viewer")
    beklenen_kisitli = {"contribution:scan"}
    # ⟳ **KAPSAM DARALTILDI (FAZ 6.2) — ve bu bir GÜÇLENDİRMEDİR.**
    #
    # Testin amacı *"rütbe 0 OKUMA araçlarında davranış kıpırdamadı"*dır. Yazma araçları
    # (FAZ 6.2) kayda girdiğinde `schedule:create`/`measure:approve` da viewer'a kapalı
    # çıkıyor — ama bu **doğru davranıştır**, bir gerileme değil: bir izleyici zamanlama
    # kuramamalı.
    #
    # 🔴 Aşağıda ayrıca **tersini** de ölçüyoruz: yazma araçları kayıttaysa viewer'a
    # **KAPALI OLMAK ZORUNDA**. Yani kapsam daralmadı, **ikiye ayrıldı**.
    okuma = [a for a in tools.hepsi() if a.yan_etki != "yazar"]
    kisitli = {a.izin for a in okuma if not can(viewer, a.izin)}
    assert kisitli == beklenen_kisitli, (
        f"viewer'a kapalı izinler {kisitli}, beklenen {beklenen_kisitli}. "
        "Bir aksiyonun rütbesi değiştiyse bu bir ÜRÜN kararıdır ve gerekçesiyle "
        "`authorize.py`'ye yazılmalıdır — sessizce yapılamaz.")

    # 🔴 YAZMA araçları viewer'a **KAPALI** olmalı — açık olsaydı, bir izleyici ajan
    # üzerinden kendi eliyle yapamayacağı bir işi yaptırabilirdi.
    for a in tools.hepsi():
        if a.yan_etki == "yazar" and a.izin != "query:run":
            assert not can(viewer, a.izin), (
                f"🔴 `{a.ad}` viewer'a AÇIK ({a.izin}) — ajan, kullanıcının kendi "
                f"eliyle yapamayacağı bir işi onun adına yapabilir.")


# --- 3. READ-ONLY DEĞİŞMEZİ ------------------------------------------------------

def test_ajan_YAZAMAZ():
    """⟳ **TERS ÇEVRİLDİ (FAZ 6.2)** — ama değişmez **gevşemedi, KADEMELENDİ**.

    Eski hâli *"kayıtta HİÇ yazan araç olmasın"* diyordu. `yazma_araclari` bayrağı o
    kararı **verdi**; ama üç şartla ve bu test artık **üçünü birden** kilitliyor:

    1. 🔴 **Bayrak KAPALIYKEN kayda HİÇ GİRMEZ** — bir filtreyle gizlenmiş değil, **var
       olmayan**. *Geri alma "kapatmak" değil **hiç açmamaktır**: bir aracı kayda alıp
       sonra engellemek, o engelin bir gün unutulabileceği anlamına gelir.*
    2. Bayrak açıkken **yalnız beyan edilmiş üç araç** girer — dördüncüsü sessizce
       giremez.
    3. Her yazan araç `geri_alma_ref` **taşır ya da `None`'la geri alınamazlığını
       AÇIKÇA söyler**.

    > *"Güvenlik imzadan değil, **yetki yüzeyinin genişlememesinden** geliyor."*
    """
    from app.config import get_settings

    acik = str(getattr(get_settings(), "yazma_araclari", "") or "").lower() in (
        "1", "true", "on", "yes")
    yazanlar = [a for a in tools.hepsi() if a.yan_etki == "yazar"]

    if not acik:
        assert not yazanlar, (
            f"🔴 Bayrak KAPALI ama kayıtta yazan araç var: {[a.ad for a in yazanlar]}. "
            f"Geri alma «kapatmak» değil «hiç açmamak»tır — kayda giren bir araç, bir "
            f"gün unutulacak bir engelin arkasında durur.")
        return

    beyan = {"dashboards.create", "schedules.create", "measures.approve"}
    assert {a.ad for a in yazanlar} == beyan, (
        f"🔴 Beyan EDİLMEMİŞ bir yazma aracı kayda girmiş: "
        f"{sorted({a.ad for a in yazanlar} - beyan)}. Yazma yüzeyi bir LİSTEDİR ve o "
        f"liste okunabilir olmalı.")
    for a in yazanlar:
        # `None` meşrudur — ama **beyan edilmiş** olmalı: `notlar` geri alınamazlığı
        # söylemek zorunda.
        if a.geri_alma_ref is None:
            assert "GERİ ALINAMAZ" in a.notlar.upper(), (
                f"🔴 `{a.ad}` geri alınamaz ama bunu SÖYLEMİYOR. *Geri alınamazlığı "
                f"gizlemek, onu geri alınabilir sanmaktan kötüdür: kullanıcı bir daha "
                f"hiç sormaz.*")


def test_YAZMA_ARACLARI_yalniz_ONAY_AKISI_uzerinden():
    """🔴 Doğrudan çağrı, onayı bir **SÜS** yapardı.

    ⚠ Belirteç yapısal: her yazma aracının `notlar`ı onay şartını **beyan etmeli** ve
    hiçbiri `llm_araclari()`'na **serbestçe** girmemelidir — planlayıcı onu bir okuma
    aracı gibi seçemez.
    """
    from app.config import get_settings

    if str(getattr(get_settings(), "yazma_araclari", "") or "").lower() not in (
            "1", "true", "on", "yes"):
        return                                    # bayrak kapalı → araç yok
    for a in (x for x in tools.hepsi() if x.yan_etki == "yazar"):
        assert "ONAY" in a.notlar.upper() or "istem" in a.notlar, (
            f"🔴 `{a.ad}` onay şartını beyan etmiyor — planlayıcı onu sıradan bir araç "
            f"sanabilir.")


def test_ham_satir_araci_KAYITTA_YOK():
    """`drill.raw` T1/T2 gizlilik sınırının en hassas yaprağıdır. Faz A2 onu üç baypastan
    kurtardı; ajan yüzeyine açmak o düzeltmeyi ölçekte geri alma riski taşır."""
    adlar = {a.ad for a in tools.hepsi()}
    assert "drill.raw" not in adlar and "drill_raw" not in adlar


# --- 4. DETERMİNİSTİK-ÖNCE -------------------------------------------------------

def test_her_LLM_aracinin_DETERMINISTIK_alternatifi_var():
    """Merdivenin felsefesi plan seviyesine taşınır: bir işi deterministik bir araç
    yapabiliyorsa LLM aracı SEÇİLEMEZ. Bu ancak alternatif BEYAN EDİLMİŞSE denetlenebilir —
    LLM aracı ile deterministik kardeşi aynı etikete sahip olmalı."""
    for a in tools.hepsi():
        if a.determinizm != "llm":
            continue
        alternatifler = [
            d.ad for d in tools.deterministik_olanlar()
            if set(d.etiketler) & (set(a.etiketler) - {"llm"})
        ]
        assert alternatifler, (
            f"{a.ad}: LLM aracı ama aynı etiketi taşıyan deterministik alternatif YOK "
            f"(etiketler={a.etiketler}). Planlayıcı 'önce deterministik' kuralını "
            "uygulayamaz — kural denetlenemezse kural değildir.")


def test_deterministik_olanlar_ETIKETE_gore_suzuluyor():
    hepsi = tools.deterministik_olanlar()
    assert hepsi and all(a.determinizm == "deterministik" for a in hepsi)
    sorgu = tools.deterministik_olanlar("sorgu-uretimi")
    assert {a.ad for a in sorgu} == {"route"}


def test_sifir_maliyetli_araclar_LLMSIZ():
    """`maliyet="sifir"` iddiası token harcamamak demektir — LLM aracı olamaz."""
    for a in tools.hepsi():
        if a.maliyet == "sifir":
            assert a.determinizm == "deterministik", f"{a.ad}: sıfır maliyet + LLM çelişkisi"


# --- 5. YETKİ DEVREDİLEMEZ -------------------------------------------------------

def _p(*roller: str) -> Principal:
    return Principal(user_id="u", tenant_id="t", roles=list(roller), tenant_slug="demo")


def test_ajan_KULLANICININ_yetkisini_asamaz():
    """Aynı kaynak (authorize matrisi), aynı cevap. Kayıt ikinci bir kopya TUTMAZ."""
    viewer = {a.ad for a in tools.izinli_araclar(_p("viewer"))}
    owner = {a.ad for a in tools.izinli_araclar(_p("owner"))}
    assert viewer <= owner, "viewer, owner'ın göremediği bir aracı görüyor"
    assert owner == {a.ad for a in tools.hepsi()}, "owner tüm araçları görmeli"


def test_yetkisiz_kullanici_ARACI_GORMEZ():
    """Rol matrisinde `sql:run` analyst+; bir viewer o izne bağlı bir aracı görmemeli.

    ⟳ **Bu testin yorumu 2026-08-04'te GÜNCELLENDİ.** Eskiden *"bugün kayıtta öyle bir
    araç yok — test yine de mekanizmayı kilitler"* diyordu. **FAZ 1.3 ile artık var:**
    `contribution.report` → `contribution:scan` (rütbe 1). Yani bu test bir varsayımı
    değil **gerçek bir elemeyi** ölçüyor. Bayat bir *"bugün yok"* notu, kapının ne
    kadarının canlı olduğunu gizler."""
    from control_plane.authorize import can

    viewer = _p("viewer")
    for a in tools.hepsi():
        if not can(viewer, a.izin):
            assert a not in tools.izinli_araclar(viewer)


def test_superadmin_hepsini_gorur():
    sa = Principal(user_id="s", tenant_id=None, is_superadmin=True)
    assert len(tools.izinli_araclar(sa)) == len(tools.hepsi())


# --- 6. BEYAN BÜTÜNLÜĞÜ ----------------------------------------------------------

@pytest.mark.parametrize("arac", tools.hepsi(), ids=lambda a: a.ad)
def test_beyan_DOLU(arac):
    assert len(arac.ozet) >= 20, f"{arac.ad}: özet çok kısa — LLM'e giden tanım budur"
    assert arac.girdi, f"{arac.ad}: girdi şeması boş"
    assert arac.cikti, f"{arac.ad}: çıktı beyanı boş"
    assert arac.etiketler, f"{arac.ad}: etiketsiz — deterministik-önce kuralı çalışmaz"


def test_makbuz_beyani_TUTARLI():
    """`makbuz=None` bir eksiklik değil bir BEYANDIR: o araç veriye dokunmaz. Veriye
    dokunan (maliyet != sifir) her aracın ya makbuzu olmalı ya da neden olmadığı
    notlarında yazmalı."""
    for a in tools.hepsi():
        if a.maliyet == "sifir" or a.makbuz:
            continue
        assert a.notlar, (
            f"{a.ad}: veriye dokunuyor (maliyet={a.maliyet}), makbuz üretmiyor ve "
            "gerekçesi de yok. 'Her adım bir makbuz üretir' beyanı böyle aşınır.")


def test_get_BILINMEYEN_araci_reddeder():
    """Planlayıcı araç UYDURAMAZ — fail-closed."""
    with pytest.raises(KeyError, match="Kayıtlı olmayan"):
        tools.get("veritabanini_sil")
    assert tools.get("route").ad == "route"


# --- LLM yüzeyi ------------------------------------------------------------------

def test_llm_araclari_SEMASI():
    şema = tools.llm_araclari()
    assert len(şema) == len(tools.hepsi())
    for t in şema:
        assert t["name"] and t["description"]
        assert t["input_schema"]["type"] == "object"
        assert t["input_schema"]["required"] == list(t["input_schema"]["properties"])
        # Determinizm ve maliyet LLM'in GÖRDÜĞÜ metne girmeli: planlayıcı ucuz/deterministik
        # olanı tercih edebilsin diye. Gizlenirse "önce deterministik" bir temenni olur.
        assert "determinizm=" in t["description"] and "maliyet=" in t["description"]


def test_llm_araclari_PRINCIPALE_gore_suzulur():
    """LLM'e verilen liste de yetkiye tabidir — ajan görmediği aracı çağıramaz."""
    sa = Principal(user_id="s", tenant_id=None, is_superadmin=True)
    assert len(tools.llm_araclari(sa)) == len(tools.hepsi())
    assert len(tools.llm_araclari(_p("viewer"))) <= len(tools.hepsi())
