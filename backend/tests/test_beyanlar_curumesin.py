"""BÜTÜNSEL DENETİM — "tüketicisi yok" beyanları ÇÜRÜMESİN.

## Neden bu dosya var

Bu depoda üç primitif bilinçle **tüketicisiz** duruyor ve her biri MIMARI'de gerekçesiyle
kayıtlı. Bu meşrudur — ama **bir yorum çürüyebilir**. Bu turda sekiz kez ölçülen desen
(*beyan var, kod tanımaz*) tam olarak böyle doğar: birisi doğru bir cümle yazar, dünya
değişir, cümle kalır.

Buradaki testler o beyanları **kapıya** çevirir: beyan yanlışlaşırsa CI kırılır ve düzelten
kişi ya primitifi bağlar ya beyanı günceller. Üçüncü seçenek yoktur — `test_uc_yetim_degil`
uç seviyesinde ne yapıyorsa, bu dosya **modül seviyesinde** onu yapar.
"""

from __future__ import annotations

import inspect
import pathlib
import re

import pytest

APP = pathlib.Path(__file__).resolve().parents[1] / "app"


def _app_kaynagi(haric: str) -> str:
    return "\n".join(f.read_text(encoding="utf-8", errors="ignore")
                     for f in APP.rglob("*.py") if f.name != haric)


# --- G4: anlatım doğrulayıcı --------------------------------------------------

def test_ANLATIM_DOGRULAYICI_GERCEKTEN_DEVREDE():
    """⟳ **FAZ 5 (2026-08-03) — bu test TUZAKTAN KAPIYA dönüştü.**

    Eski hâli MIMARI §12.6'nın *"Tüketicisi HENÜZ YOK — bugün sistemde LLM-üretimi düz
    metin HİÇ YOKTUR"* beyanını koruyordu ve **Faz 5 landing ettiği gün kırıldı** — tam
    olarak kurulduğu iş buydu: düzelten kişiyi ya guard'ı takmaya ya beyanı güncellemeye
    ZORLAMAK. Guard takıldı, beyan güncellendi.

    Artık ölçtüğü şey **tersine döndü**: düz metin üreten her LLM yöntemi için
    `narration_guard` **gerçekten çağrılıyor mu**. Beyan bir kez daha çürümesin diye
    kapı yerinde kalıyor, yalnız yönü değişti.
    """
    llm = (APP / "llm.py").read_text(encoding="utf-8")
    uretenler = set(re.findall(r"def (generate_\w+|\w*_?(?:narrate|anlat|prose)\w*)\(", llm))
    metin_ureten = {a for a in uretenler
                    if not any(x in a for x in ("sql", "cube", "select", "refine", "repair"))}
    assert metin_ureten, ("llm.py'de düz metin üreten yöntem KALMADI — T2 anlatıcı geri mi "
                          "alındı? O hâlde MIMARI §12.6 ve bu test yeniden gözden geçirilmeli.")

    kaynak = _app_kaynagi("narration_guard.py")
    assert "guvenli_anlatim" in kaynak, (
        f"düz metin üreten yöntem(ler) VAR ({sorted(metin_ureten)}) ama `narration_guard` "
        "hiçbir üretim yolundan çağrılmıyor — KORUMASIZ BİR UYDURMA YÜZEYİ.")


def test_ANLATI_GUARD_ZORUNLU_kapidir():
    """Guard'ın *çağrılması* yetmez: LLM çıktısı ona UĞRAMADAN yayımlanabiliyor mu?
    `_anlati_ekle`'de `llm.anlat(...)` ile `interpretation["narration"]` ataması ARASINDA
    `guvenli_anlatim` bulunmak ZORUNDA."""
    from app import answer

    govde = inspect.getsource(answer._anlati_ekle)
    # ⟳ FAZ 9.8 — çapa KAYDI: çağrı artık `plan.calistir("llm.anlat", ...)`. Kapı
    # GEVŞETİLMEDİ, iki yönde KESKİNLEŞTİRİLDİ: (1) guard hâlâ arada olmalı,
    # (2) çağrının PLANLAYICIDAN geçtiği ayrıca ölçülüyor (MIMARI §12.6b'nin
    # *"kapısız LLM çağrısı olmasın"* şartı, denetimde karşılıksız çıkmıştı).
    assert 'calistir("llm.anlat"' in govde, (
        "T2 anlatıcı planlayıcıyı ATLIYOR — kapısız LLM çağrısı: bütçeye sayılmaz, "
        "makbuzda adım olarak görünmez (MIMARI §12.6b'nin beyanı karşılıksız kalır)")
    i_ham = govde.index('calistir("llm.anlat"')
    i_guard = govde.index("guvenli_anlatim(")
    i_yaz = govde.index('yorum["narration"] =')
    assert i_ham < i_guard < i_yaz, (
        "LLM çıktısı guard'a UĞRAMADAN yayımlanabiliyor — fail-closed sözleşme kırık")


def test_ANLATI_TUM_CUMLELER_DUSERSE_HIC_EKLENMEZ():
    """En kötü durum 'süssüz ama doğru' olmalı, asla 'akıcı ama uydurma'."""
    from app.narration_guard import guvenli_anlatim

    result = {"columns": ["ciro"], "rows": [{"ciro": 100.0}], "row_count": 1}
    metin, rapor = guvenli_anlatim("Ciro 999999 TL oldu. Kâr 12345 arttı.", result,
                                   yedek=None)
    assert metin == "", f"uydurma sayı yayımlandı: {metin!r}"
    assert rapor.reddedilen


def test_ANLATI_SABLONU_EZMEZ():
    """§4.4'ün kullanıcı tarafından açıkça istenen şartı: anlatı `summary`/`facts`'i
    SİLMEZ, `narration` alanına biner — yoksa *"o konuşmayı grafiğe çevir"* çalışmazdı."""
    from app import answer

    govde = inspect.getsource(answer._anlati_ekle)
    assert 'yorum["narration"]' in govde
    for alan in ('yorum["summary"] =', 'yorum["facts"] ='):
        assert alan not in govde, f"anlatı deterministik alanı EZİYOR: {alan}"


# --- E-2: cube_query_hash -----------------------------------------------------

def test_CUBE_QUERY_HASH_beyani_HALA_dogru():
    """MIMARI §5: *"primitif, tüketici bekliyor"* (sonuç cache'i, Faz E-2 — plan onu
    ölçülen tekrar oranı eşiği aşmadan kurmamayı söylüyor). Cache kurulduğu gün bu
    test kırılır ve beyanın güncellenmesini zorlar."""
    kaynak = _app_kaynagi("contracts.py")
    assert "cube_query_hash" not in kaynak, (
        "`cube_query_hash` artık kullanılıyor — MIMARI'deki \"tüketici bekliyor\" "
        "beyanı bayat. Beyanı güncelle.")


# --- F4: LLM'e verilecek araç listesi -----------------------------------------

def test_LLM_ARAC_LISTESI_GERCEKTEN_TUKETILIYOR():
    """⟳ **FAZ 4 (2026-08-03) — bu tuzak ATEŞLEDİ ve TUZAKTAN KAPIYA dönüştü.**

    Eski hâli MIMARI §11.6d'nin *"F4 (plan SEÇİMİ) telemetriye bağlı olduğu için henüz
    tüketicisi yok"* beyanını koruyordu ve **bağlandığı gün kırıldı** — kurulduğu iş
    tam olarak buydu. Faz 0 telemetriyi kurdu, Faz 2b onu triyaja bağladı, Faz 4 `sec()`
    ile tüketiciyi taktı. Beyan güncellendi; kapı **yönü tersine çevrilerek** korunuyor.

    Artık ölçtüğü şey: seçici **gerçekten** bu süzülmüş listeyi mi görüyor? Süzgeç
    atlanırsa ajan yazma yan etkili araçları (`dashboards.create` …) görürdü — yani
    kullanıcının kendi eliyle yapamayacağı bir işi onun adına yapabilirdi.
    """
    kaynak = _app_kaynagi("tools.py")
    assert "llm_araclari" in kaynak, (
        "`tools.llm_araclari` artık ÇAĞRILMIYOR — F4'ün seçicisi geri mi alındı? "
        "O hâlde MIMARI §11.6d ve bu test yeniden gözden geçirilmeli.")

    from app import planner

    govde = inspect.getsource(planner.Planlayici.sec)
    assert "llm_araclari(self.principal)" in govde, (
        "seçici SÜZÜLMEMİŞ bir araç listesi görüyor olabilir — yetki/yazma sınırı delik")


# --- Planlayıcının itiraf mekanizması -----------------------------------------

def test_DIS_ADIM_API_si_KORUNUR_ama_tuketicisi_YOK():
    """`Planlayici.dis_adim()` kayıtsız adımları makbuzda `gated: false` ile itiraf eder.
    Faz F3'te `contribution.report` kayda girince tek tüketicisi kalktı.

    API **silinmedi** ve bu bilinçlidir: gerçek kayıtsız adımlar için itiraf mekanizması
    hâlâ doğru şeydir. Ama tüketicisi olmadığı **kaydedilmeli** — sessizce durması, bir
    sonraki geliştiricinin "demek ki bileşikler zaten itiraf ediliyor" diye varsaymasına
    yol açardı.
    """
    from app import planner

    assert hasattr(planner.Planlayici, "dis_adim")
    kaynak = _app_kaynagi("planner.py")
    # Yorumlar tarihçe anlatır; ÇAĞRI aranır (`plan.dis_adim(` / `.dis_adim(`).
    cagrilar = [s for s in kaynak.splitlines()
                if ".dis_adim(" in s and not s.strip().startswith("#")]
    assert not cagrilar, (
        "`dis_adim` yeniden çağrılıyor:\n  " + "\n  ".join(cagrilar)
        + "\nBu meşru olabilir (gerçek bir kayıtsız adım) ama MIMARI §11.6c'nin "
          "\"itiraf artık gereksiz\" cümlesi güncellenmeli.")


# --- Gerçekten ÖLÜ kod ---------------------------------------------------------

def test_OLU_AUTH_yardimcisi_GERI_gelmesin():
    """`app/auth/dependencies.require_superadmin` **silindi** (bütünsel denetim,
    2026-08-02): sıfır çağıranı vardı. Public plane'de superadmin-only bir uç YOK; admin
    plane AYRI bir serviste (ADR-0015) kendi kontrolünü yapıyor —
    `control_plane.auth_service`'in `require_superadmin` **parametresi** farklı bir şeydir
    ve o yaşıyor.

    Ölü bir YETKİ yardımcısı zararsız değildir: birisi onu "hazır" sanıp kullanır ve
    **yanlış plane'in** kontrolünü uygulamış olur. Bu test geri gelmesini engellemez —
    geri gelirse *kullanılmadan* durmasını engeller."""
    dep = (APP / "auth/dependencies.py").read_text(encoding="utf-8")
    if "def require_superadmin" in dep:
        kaynak = _app_kaynagi("dependencies.py")
        assert "require_superadmin" in kaynak, (
            "`require_superadmin` yeniden tanımlanmış ama HİÇBİR yerden kullanılmıyor — "
            "ya bağla ya sil (MIMARI §5: ölçülmemiş ihtiyaç için altyapı kurma). Public "
            "plane'de superadmin kontrolü gerekiyorsa önce ADR-0015'i (iki-plane ayrımı) "
            "gözden geçir.")


# --- ADR-0007 K3: dönem politikası — beyan var, canlı kapı daha zayıf ------------

def _donem_politikasi_cagrilari() -> dict[str, list[str]]:
    """`needs_period` / `is_period_only`'nin ÜRETİMDEKİ çağrıları (tanım ve yorum hariç).

    ÇAĞRI aranır, ANMA değil: her iki ad da yorumlarda geçiyor (politikanın nerede
    bağlı olduğunu anlatan notlar) ve bu meşrudur — hatta istenen şeydir.
    """
    bulunan: dict[str, list[str]] = {"needs_period": [], "is_period_only": []}
    for satir in _app_kaynagi("cube_router.py").splitlines():
        s = satir.strip()
        if s.startswith("#"):
            continue
        for ad in bulunan:
            # ⟳ FAZ 9.12/9.14 — ESKİ DESEN NOKTALI ÇAĞRIYI GÖRMÜYORDU.
            # `(?<![\w.])` negatif lookbehind'ı `.`'yı da dışlıyordu; oysa bu depoda
            # kullanılan TEK çağrı biçimi `cube_router.needs_period(...)`. Artık TANIM
            # (`def ad(`) hariç her çağrı biçimi yakalanır.
            if re.search(rf"(?<!def )\b{ad}\s*\(", satir):
                bulunan[ad].append(s[:90])
    return bulunan


def test_DONEM_POLITIKASI_beyani_HALA_dogru():
    """⟳ **FAZ X (3 Ağustos 2026) — bu test TUZAKTAN KAPIYA dönüştü, tıpkı tasarlandığı gibi.**

    Eski hâli *"`needs_period`/`is_period_only`'nin üretimde SIFIR çağıranı var"* beyanını
    koruyor ve şunu yazıyordu: *"Biri bunları üretime bağladığı gün bu test kırılır ve
    MIMARI §6.2'nin güncellenmesini zorlar."*

    **O gün geldi.** Faz X'te ölçülen sessiz-yanlış (takip düzenlemesi TABAN soruyu VQR'da
    değiştiriyordu) düzeltilirken `needs_period` üretime bağlandı — ama **klarifikasyon
    kapısı olarak DEĞİL**. Ayrım kritik ve beyan artık bunu söylemeli:

    | ad | üretimde | rolü |
    |---|---|---|
    | `needs_period` | **1 çağıran** (`ask.py::_learn_chip_completion`) | CEVAPLANABİLİRLİK yordayıcısı — *"önceki mesaj tek başına cevaplanabiliyor muydu?"* |
    | `is_period_only` | **0 çağıran** | ADR-0007 K3 klarifikasyon politikası hâlâ bağlı DEĞİL |

    Yani `_period_gate`'in davranışı **değişmedi**: hangi soruların netleştirme alacağı
    aynı. Bağlanan şey politikanın kendisi değil, onun *yordayıcısı*. Bu ayrım kaybolursa
    biri *"ADR-0007 K3 canlıya alındı"* sanır — alınmadı.
    """
    cagrilar = _donem_politikasi_cagrilari()
    assert not cagrilar["is_period_only"], (
        "`is_period_only` artık üretimde ÇAĞRILIYOR:\n  "
        + "\n  ".join(cagrilar["is_period_only"])
        + "\nMIMARI §6.2'deki kayıt BAYAT — beyanı güncelle.")
    assert len(cagrilar["needs_period"]) == 1, (
        f"`needs_period` çağıran sayısı {len(cagrilar['needs_period'])} (1 bekleniyordu):\n  "
        + "\n  ".join(cagrilar["needs_period"])
        + "\nHer yeni çağıran bir POLİTİKA kararıdır: yordayıcıyı kullanmak ile ADR-0007 K3'ü "
          "canlıya almak AYRI şeylerdir. Beyanı (MIMARI §6.2) ve bu kapıyı birlikte güncelle.")


def test_DONEM_POLITIKASI_KLARIFIKASYON_KAPISI_DEGISMEDI(client):
    """Beyanın DAVRANIŞSAL yarısı: `needs_period` üretime bağlandı ama `_period_gate`
    aynı kaldı — dönemsiz bir soru sessizce TÜM-ZAMAN toplanmıyor.

    ⚠ İlk yazımım SIRAYA BAĞIMLIYDI: *"dönem sorulmalı"* diye sabitlemiştim, ama
    `test_ask_golden` o soruyu VQR'a öğretiyor ve sonrasında dönem kapısı **meşru
    biçimde** atlanıyor (doğrulanmış şekil dönemi zaten taşır). Tek başına yeşil, süitte
    kırmızıydı — yani test bir davranışı değil bir SIRAYI ölçüyordu.

    Sıradan bağımsız gerçek değişmez: **ya SORULUR ya da cevap AÇIK bir dönem taşır.**
    Yasak olan üçüncü ihtimaldir: dönemi sorulmadan, sessizce tüm zamanları toplamak.
    """
    from tests.conftest import ask

    d = ask(client, "kumaş türlerine göre fire oranı")
    cq = d.get("cube_query") or {}
    if d.get("sql"):
        donem_var = bool(cq.get("timeDimensions")) or any(
            f.get("dimension") == "tarih" for f in (cq.get("filters") or []))
        assert donem_var, (
            "dönem SORULMADAN ve AÇIK dönem OLMADAN cevap üretildi — sessiz tüm-zaman "
            f"toplama: {cq}")
    else:
        assert "dönem" in (d.get("note") or "").lower(), d.get("note")


def test_DONEM_POLITIKASI_sartnamesi_KORUNUYOR():
    """Silme kararının bedeli: 13 test bir şartname olarak duruyor. Sayı düşerse
    şartname aşınıyor demektir — o zaman "sil" kararı yeniden değerlendirilmeli."""
    import pathlib
    import re

    t = (pathlib.Path(__file__).resolve().parents[1] / "tests/test_cube_router.py").read_text(
        encoding="utf-8")
    kullanim = len(re.findall(r"\b(needs_period|is_period_only)\s*\(", t))
    assert kullanim >= 13, (
        f"dönem politikası şartnamesi {kullanim} çağrıya düşmüş (>=13 bekleniyordu) — "
        "ya testler siliniyor ya politika taşınıyor; ikisi de bilinçli bir karar olmalı.")


# --- FAZ 9.10: MIMARI'nin SAYILARI da bir beyandır --------------------------------
#
# ## Ölçülen kusur (denetim, Faz 9)
#
# Denetim MIMARI'de *"18 test"* diyen bir satırın gerçekte **17** olduğunu buldu. Tek tek
# düzeltmek yerine HEPSİ ölçüldü: **13 iddianın 10'u yanlıştı** (15→17, 18→25, 16→20 …).
#
# Sebep yapısal: test eklemek doğal, MIMARI'yi güncellemek unutulur. Bir sayı sessizce
# çürür ve *"şu kapı N testle kilitli"* cümlesi bir güven verir ki karşılığı yoktur.
# Bu dosyanın kurduğu disiplinin (beyan → kapı) sayılara uygulanmış hâli.


def _toplanan_test_sayisi(yol) -> int | None:
    """Bir test dosyasının `pytest -q` ile TOPLANACAK test sayısı — pytest çağırmadan.

    `@pytest.mark.parametrize` her parametre için ayrı bir test üretir; sayı bu
    genişlemeyi içerir. Bir parametre listesi statik olarak çözülemiyorsa (değişken,
    fonksiyon çağrısı…) `None` döner: **tahmin etmek yerine ölçemediğini söyler**.
    """
    import ast

    agac = ast.parse(pathlib.Path(yol).read_text(encoding="utf-8"))
    toplam = 0
    for d in agac.body:
        if not (isinstance(d, (ast.FunctionDef, ast.AsyncFunctionDef))
                and d.name.startswith("test_")):
            continue
        carpan = 1
        for dek in d.decorator_list:
            if not (isinstance(dek, ast.Call) and "parametrize" in ast.unparse(dek.func)):
                continue
            if len(dek.args) < 2 or not isinstance(dek.args[1], (ast.List, ast.Tuple)):
                return None                       # statik değil → ÖLÇÜLEMEDİ
            carpan *= len(dek.args[1].elts)
        toplam += carpan
    return toplam


def test_MIMARI_TEST_SAYILARI_gercekle_uyusuyor():
    """`N test: \\`tests/X.py\\`` biçimindeki her iddia ÖLÇÜLÜR."""
    import ast

    kok = pathlib.Path(__file__).resolve().parents[1]
    metin = (kok / "MIMARI.md").read_text(encoding="utf-8")
    iddialar = re.findall(r"(\d+) test: `tests/([a-z0-9_]+\.py)`", metin)
    assert len(iddialar) >= 10, f"iddia bulunamadı ({len(iddialar)}) — desen mi değişti?"

    yanlis = []
    for beyan, dosya in iddialar:
        yol = kok / "tests" / dosya
        if not yol.exists():
            yanlis.append(f"{dosya}: DOSYA YOK (MIMARI {beyan} test diyor)")
            continue
        # pytest çağırmak yerine AST: hızlı, ağsız ve toplama sırasından bağımsız.
        #
        # ⚠️ İLK SÜRÜM YANLIŞ BİRİMİ SAYDI. Yalnız `def test_*` sayıyordu; pytest ise
        # `@pytest.mark.parametrize` GENİŞLEMELERİNİ ayrı test sayar. Dört dosyada iki
        # sayı ayrıştı (17↔8, 15↔9 …) ve kapı ÇALIŞAN bir MIMARI satırını "çürük"
        # raporladı. Ölçüm birimi tanımlanmadan yapılan kıyas, kıyas değildir — bu
        # oturumda ölçüm aracının kendisi altıncı kez yanlış ölçtü (MIMARI §6.4).
        #
        # BİRİM: `pytest -q tests/X.py`'nin bastığı sayı — okuyucunun yeniden
        # üretebileceği tek sayı odur.
        adet = _toplanan_test_sayisi(yol)
        if adet is None:
            continue          # statik olarak çözülemeyen parametrize → SESSİZCE geçme
        if int(beyan) != adet:
            yanlis.append(f"{dosya}: MIMARI={beyan} gerçek={adet}")
    assert not yanlis, (
        "MIMARI'nin test sayıları ÇÜRÜMÜŞ:\n  " + "\n  ".join(yanlis)
        + "\nSayıyı düzelt — *'şu kapı N testle kilitli'* cümlesi karşılığı olmayan bir "
          "güven verir.")


# ═══════════════════════════════════════════════════════════════════════════════════
# FAZ −1 / KUTU C · ⟳ YÜRÜRLÜKTE TUZAKLARI
# ═══════════════════════════════════════════════════════════════════════════════════
#
# `MIMARI.md` §0'daki her ⟳ satırı **iki şey birden** iddia eder:
#   (a) bu başlıkta otorite yol haritasındadır,   (b) ve **HENÜZ UYGULANMADI**.
#
# (b) bir GEÇİCİ GERÇEKTİR ve gerçekler bayatlar. Aşağıdaki tuzaklar (b)'yi kilitler:
# **faz indiği gün test KIRILIR** → geliştirici ⟳ satırını silmek ve yerine ölçümlü bir
# `✅` yazmak ZORUNDA kalır. Belge güncellemesi böylece bir **CI zorunluluğu** olur.
#
# 🔴 **BU TESTLERİN KIRILMASI BİR BAŞARIDIR, BİR HATA DEĞİL.** Kırıldığında yapılacak:
#   1. `MIMARI.md` §0'dan o satırı SİL
#   2. İlgili bölüme ölçümlü `✅` yaz (sayı + HEAD damgası + komut — kural D2)
#   3. Buradaki tuzağı **TERS ÇEVİR** (artık "inmiş olmalı" diye kilitle) — silme
#
# Desen kanıtlanmış: bu dosyanın kendi kaydı — *"bu beyan bir TUZAKTI … kurulduğu iş buydu"*
# (`test_LLM_ARAC_LISTESI_GERCEKTEN_TUKETILIYOR` · `test_DONEM_POLITIKASI_beyani_HALA_dogru`).

def _yazan_arac_sayisi() -> int:
    """`tools.KAYIT`'ta `yan_etki="yazar"` olan GERÇEK araç sayısı — docstring DEĞİL.

    Alt-dize taraması bu dosyanın kendi açıklamasını yakalıyordu (`tools.py:26`, `:109`);
    beyan ile beyanın ANLATIMI ayrı şeylerdir."""
    import ast as _ast

    agac = _ast.parse((APP / "tools.py").read_text(encoding="utf-8"))
    return sum(1 for n in _ast.walk(agac)
               if isinstance(n, _ast.Call) and getattr(n.func, "id", "") == "Arac"
               and any(k.arg == "yan_etki" and getattr(k.value, "value", "") == "yazar"
                       for k in n.keywords))


#: (mimari_bolum, faz, "inmiş" belirteci → çağrılabilir, açıklama)
#: Belirteç UCUZ olmalı (dosya varlığı / grep) — tuzaklar her süitte koşar.
_YURURLUKTE_TUZAKLARI = [
    ("§3·§3.3", "FAZ 2.1",
     lambda: (APP.parent / "demo/packs/cekirdek").exists()
             or "_merge_cube_metadata" in _app_kaynagi(""),
     "çekirdek katman / compose birleştirme semantiği"),
    ("§3.4-RLS", "FAZ 1.1",
     lambda: "rowLevelAccessControl" in _app_kaynagi(""),
     "motor-seviyesi RLS"),
    ("§3.4-osi", "FAZ 3.4",
     # ⚠ Belirteç İKİ KEZ düzeltildi:
     #  (1) ilk sürüm `"ossie" in _app_kaynagi()` idi → `compose.py`'nin **YORUM** satırını
     #      yakalayıp tuzağı yanlış-KIRMIZI yaptı (ölçüm aracı kusuru);
     #  (2) ikinci sürüm yalnız `app/ossie_import.py` arıyordu → denetim ölçtü: FAZ 3.4'ün
     #      `NE`'si böyle bir DOSYA vaat etmiyor; vaat ettiği şey **`POST /connections/
     #      {id}/import-semantic` ucu** + `ossie_ithal` bayrağı + bir çevirici. Yani faz
     #      indiğinde tuzak **susacaktı** — yanlış-NEGATİF, yanlış-pozitiften DAHA tehlikeli.
     # Şimdi belirteç fazın KENDİ vaadine bağlı (üçünden biri yeterli: uç · bayrak · modül).
     lambda: ("import-semantic" in _app_kaynagi("")
              or "ossie_ithal" in (APP / "features.py").read_text(encoding="utf-8")
              or any(APP.glob("ossie*.py"))),
     "Ossie ithali (karar geri alındı)"),
    ("§4", "FAZ 6.0→6.2",
     # ⚠ AST ile bakılır: alt-dize taraması `tools.py`'nin **docstring'indeki**
     # `yan_etki="yazar"` cümlesini yakalayıp tuzağı yanlış-kırmızı yaptı. Beyan ile
     # BEYANIN ANLATIMI farklı şeylerdir — bu deponun kendi dersi.
     lambda: (APP / "onay_akisi.py").exists() or (APP / "yazma_araclari.py").exists()
             or _yazan_arac_sayisi() > 0,
     "ajan yazma yasağının kademelenmesi"),
    ("§5-grain", "FAZ 2.1",
     lambda: "grain" in (APP / "compose.py").read_text(encoding="utf-8"),
     "grain sözleşmesi (compose fail-closed)"),
    ("§5-18.yasak", "§G/AJ0",
     lambda: "if typo_suggestion:" not in
             (APP / "routers/ask.py").read_text(encoding="utf-8"),
     "cevapsız dal cevaplı yolu kesemez (KAT-2)"),
    # ⟳ `§7-CI` **TERS ÇEVRİLDİ** — FAZ 0.15 indi, tuzak
    # `test_TERS_TUZAK_FAZ_0_15_CI_KAPILARI_AYAKTA`'ya taşındı (silinmedi).
    # §0'ın `§7` satırı DARALDI: geriye **risk-kapsam eğrisi** (FAZ 4.2) kaldı ve
    # belirteç ona yeniden nişanlandı. Eski belirteç (`.github/workflows`'ta `kapi.py`)
    # bugün DOĞRU olduğu için tuzağı kalıcı-kırmızı bırakırdı; oysa satırın inmemiş
    # yarısı hâlâ bir işaretçiye muhtaç.
    ("§7-risk", "FAZ 4.2",
     lambda: (APP.parent / "lab/risk_kapsam.py").exists()
             or (APP.parent / "lab/reports/risk_kapsam.md").exists(),
     "risk-kapsam eğrisi (ayrık kapılar üzerinde)"),
    ("§9-metrik", "FAZ 0.18",
     lambda: "MetricDefinition" in
             (APP.parent / "control_plane/models.py").read_text(encoding="utf-8"),
     "metrik kaydı = hakem"),
    # ⟳ `§11-yetki` **TERS ÇEVRİLDİ** — FAZ 1.3 indi (5 aksiyon), tuzak
    # `test_TERS_TUZAK_FAZ_1_3_YETKI_GRANULERLIGI_AYAKTA`'ya taşındı (silinmedi).
    # §0'ın `§11` satırı DARALDI: geriye **onaylı yazma aksiyonları** (FAZ 6.1) kaldı ve
    # belirteç ona yeniden nişanlandı — `yan_etki="yazar"` bir araç kayda girdiği gün.
    ("§11-yazma", "FAZ 6.1",
     lambda: _yazan_arac_sayisi() > 0,
     "onaylı yazma aksiyonları (ajan bugün YAZAMAZ)"),
    ("§12-tür", "FAZ 5.1·5.2",
     lambda: "TUR_TAKIP" in (APP / "followup.py").read_text(encoding="utf-8")
             or "TUR_PAYLAS" in (APP / "followup.py").read_text(encoding="utf-8"),
     "6./7. konuşma türü"),
    ("§13-viz", "FAZ 5.11·5.12",
     lambda: "list[VizSpec]" in (APP / "viz.py").read_text(encoding="utf-8"),
     "viz.recommend() çoklu dönüş"),
    ("§8.2-ADR", "FAZ 4.6",
     lambda: (APP.parent / "docs/adr").exists(),
     "ADR dosyaları"),
]


@pytest.mark.parametrize("bolum,faz,indi_mi,konu",
                         _YURURLUKTE_TUZAKLARI,
                         ids=[x[0] for x in _YURURLUKTE_TUZAKLARI])
def test_YURURLUKTE_satiri_HALA_dogru(bolum, faz, indi_mi, konu):
    """⟳ satırı *"henüz uygulanmadı"* diyor — hâlâ doğru mu?"""
    try:
        indi = bool(indi_mi())
    except Exception:                       # belirteç kırıldıysa TUZAK DA KIRILIR
        raise AssertionError(
            f"{bolum} tuzağının BELİRTECİ çalışmıyor — kod taşınmış olabilir. "
            f"Tuzak güncellenmeden bu satır korunamaz.") from None
    assert not indi, (
        f"🎉 {faz} İNDİ ({konu}) — ve bu tuzak tam da bunun için kuruldu. "
        f"ŞİMDİ YAPILACAK, SIRAYLA: "
        f"(1) MIMARI.md §0'dan `{bolum}` satırını SİL · "
        f"(2) ilgili bölüme ÖLÇÜMLÜ `✅` yaz (sayı + @sha + komut — kural D2) · "
        f"(3) bu tuzağı TERS ÇEVİR (artık 'inmiş olmalı' diye kilitle) — SİLME")


def test_TERS_TUZAK_FAZ_0_14_KAPILARI_AYAKTA():
    """⟳ **TUZAKTAN KAPIYA — FAZ 0.14 indi (`45b5c6a`), tuzak TERS ÇEVRİLDİ.**

    `⟳` yaşam döngüsü: *"faz indiği gün satır **silinir**, yerine **ölçümlü ✅** yazılır,
    ve tuzak **ters çevrilerek** korunur."* Eski tuzak *"bu dosya HENÜZ YOK"* diyordu ve
    FAZ 0.14 landing ettiği gün **kırıldı** — kurulduğu iş buydu.

    Yeni yönü: beş kapı **ayakta kalmalı**. Bir kapının sessizce silinmesi, bu belgenin
    100+ maddesinin dayandığı zemini yok eder — ve `GERİ AL` kuralı bunu zaten yasaklıyor:
    *"kapı testi geri alınmaz, `xfail` işaretlenir."*"""
    kapilar = {
        "tests/kapi_ortak.py": "ortak iskelet (TEK SAHİP)",
        "tests/test_uc_yetim_degil.py": "K1 uç yetimi",
        "tests/test_cevap_alani_yetim_degil.py": "K2 alan yetimi",
        "tests/test_ters_yetim.py": "K3 ters yetim",
        "tests/test_yuzey_sadakati.py": "K4 yüzey sadakati",
        "tests/test_panel_sayisi.py": "K5 panel sayısı",
        "tests/test_yol_haritasi_butunlugu.py": "D5 belge kapısı",
    }
    eksik = {y: ad for y, ad in kapilar.items() if not (APP.parent / y).exists()}
    assert not eksik, (
        f"FAZ 0.14 KAPISI SİLİNMİŞ: {eksik}\n"
        "Kapı testi geri alınmaz — `xfail` işaretlenir ve gerekçesi buraya yazılır. "
        "Bir kapının kırmızısı bir BİLGİDİR; silindiğinde o bilgi de kaybolur.")


def test_TERS_TUZAK_FAZ_1_3_YETKI_GRANULERLIGI_AYAKTA():
    """⟳ **TUZAKTAN KAPIYA — FAZ 1.3 indi, tuzak TERS ÇEVRİLDİ.**

    Eski yön: *"15/15 araç tek izinde"*. FAZ 1.3 indiği gün **kırıldı** — kurulduğu iş
    buydu. Yeni yön: **granülerlik ayakta kalmalı ve `pahali` araç viewer'ın dışında**.

    Neden ikisi birden: yalnız *"birden çok izin var"* demek yetmez — biri
    `contribution.report`'u tekrar `query:run`'a çekip ötekileri bırakabilir; sayı
    **yeşil** kalır, ölçülen kusur **geri döner**. Kapı, granülerliğin **işe yaradığı**
    noktayı tutar.
    """
    import ast as _ast

    from control_plane.authorize import _ACTION_MIN_RANK

    agac = _ast.parse((APP / "tools.py").read_text(encoding="utf-8"))
    araclar = []
    for n in _ast.walk(agac):
        if isinstance(n, _ast.Call) and getattr(n.func, "id", "") == "Arac":
            k = {a.arg: getattr(a.value, "value", None) for a in n.keywords}
            araclar.append((k.get("ad"), k.get("izin"), k.get("maliyet")))
    assert araclar, "araç kaydı okunamadı — kapı GÜNCELLENMELİ, silinmemeli"

    izinler = {i for _a, i, _m in araclar}
    assert len(izinler) > 1, (
        f"🔴 FAZ 1.3 GERİ ALINMIŞ: tüm araçlar tek izinde ({izinler}). Tek izin "
        "granülerlik değil bir ANAHTARDIR: süzgeç ya hepsini döndürür ya hiçbirini.")

    for ad, izin, maliyet in araclar:
        if maliyet == "pahali":
            assert _ACTION_MIN_RANK.get(izin, 0) > 0, (
                f"🔴 {ad}: maliyet `pahali` ama izni `{izin}` **viewer rütbesinde** "
                f"({_ACTION_MIN_RANK.get(izin)}). FAZ 1.3'ün ölçülen kusuru tam buydu — "
                "okuma tarafında maliyet/yetki ayrımı olmaması.")


def test_TERS_TUZAK_FAZ_0_15_CI_KAPILARI_AYAKTA():
    """⟳ **TUZAKTAN KAPIYA — FAZ 0.15 indi, tuzak TERS ÇEVRİLDİ.**

    Eski yön: *"CI'da ölçüm kapısı YOK"*. FAZ 0.15 indiği gün **kırıldı** — kurulduğu iş
    buydu. Yeni yön: **dört kapı CI'da ayakta kalmalı**.

    Neden `--tam` de aranıyor: bir workflow `kapi.py`'yi **çağırıp** yalnız `--hizli`
    koşarsa dosya adı yerinde durur ama ölçülen şey **kapı değil sinyaldir**
    (`CLAUDE.md`: *"Bu bir KAPI DEĞİL, sinyaldir"*). Yalnız dosya adını aramak, tam
    olarak bir önceki ölçümün düştüğü **çağıran-komuta-bakma** kusurunun aynadaki hâli
    olurdu.

    Neden `if: always()` de aranıyor: workflow'un kendi yorumu *"kırmızıda ham kütük
    LAZIM"* diyor — *"korpus %92,8'e düştü"* bilgisi, **hangi** soruların kaydığı
    bilinmeden düzeltilemez. Kırmızıda artefaktı yüklemeyen bir kapı, kırmızısını
    **okunamaz** hâle getirir.
    """
    wf = APP.parent.parent / ".github/workflows"
    assert wf.exists(), "`.github/workflows` YOK — FAZ 0.15 geri alınmış"
    metinler = {f.name: f.read_text(encoding="utf-8", errors="ignore")
                for f in sorted(wf.glob("*.yml"))}
    kosanlar = {ad: t for ad, t in metinler.items() if "kapi.py" in t}
    assert kosanlar, (
        "Hiçbir workflow `lab/kapi.py` çağırmıyor — FAZ 0.15 GERİ ALINMIŞ.\n"
        "Kapı testi geri alınmaz; gerekçesi buraya yazılır ve satır `xfail` işaretlenir.")
    assert any("--tam" in t for t in kosanlar.values()), (
        f"`kapi.py` çağrılıyor ({sorted(kosanlar)}) ama `--tam` YOK. `--hizli` bir KAPI "
        "değil, bir SİNYALDİR (seçim import bağımlılığına bakar; davranışa dayanan test "
        "kaçar). Dört kapı yalnız `--tam` ile koşar.")
    assert any("if: always()" in t for t in kosanlar.values()), (
        "Kapı workflow'u raporları `if: always()` ile YÜKLEMİYOR. Kırmızıda ham kütük "
        "lazım: *'korpus %92,8'e düştü'* bilgisi, HANGİ soruların kaydığı bilinmeden "
        "düzeltilemez.")


def test_TUZAK_SAYISI_MIMARI_ILE_ORTUSUYOR():
    """Tuzak sayısı §0'daki ⟳ satır sayısıyla **birebir** olmalı.

    Aksi hâlde biri ⟳ ekleyip tuzağını yazmayı unutur ve o satır **sessizce** bayatlar —
    tam olarak bu bloğun engellemek için var olduğu şey."""
    # ⚠ Sayım TABLO SATIRI üzerinden — alt-dize sayımı bloğun kendi AÇIKLAMASINI da
    # sayıyordu (ölçüldü: 14 ↔ 13). Bkz. `_yururlukte_satirlari` docstring'i.
    satir = len(_yururlukte_satirlari())
    assert satir == len(_YURURLUKTE_TUZAKLARI), (
        f"MIMARI §0'da {satir} ⟳ satırı var, tuzak sayısı {len(_YURURLUKTE_TUZAKLARI)}. "
        "Her ⟳ satırının bir tuzağı OLMALI — yoksa beyan sessizce çürür.")


def _yururlukte_blogu() -> str:
    mimari = (APP.parent / "MIMARI.md").read_text(encoding="utf-8")
    return mimari[mimari.index("## §0 · ⟳ YÜRÜRLÜKTE"):mimari.index("## 1. Sistem nedir")]


def _yururlukte_satirlari() -> list[list[str]]:
    r"""§0 tablosunun VERİ satırları, hücrelerine ayrılmış — **tek ayrıştırıcı**.

    🔴 Bu fonksiyon bir kusurdan doğdu ve kusur **benim ölçüm aracımdaydı** (bu turda
    dördüncü kez). Sayaç `mimari.count("⟳ UYGULANMADI")` idi; §0'a bloğun kendi kapılarını
    anlatan bir paragraf eklendi ve o paragraf `⟳ UYGULANMADI` **ifadesini** taşıyordu →
    sayaç **14**, tablo **13**. Yani belge doğruydu, **sayaç yanlıştı** — tam olarak
    *"testler METNİ ölçtü, davranışı değil"* sınıfı.

    Doğru ölçüm: **tablo satırı** ayrıştırılır; düzyazı hiç sayılmaz. `\|` KAÇIŞLI boru
    işareti hücre ayracı DEĞİLDİR (§13 satırı `VizSpec \| list[VizSpec]` yazıyor)."""
    satirlar = [s for s in _yururlukte_blogu().splitlines() if s.lstrip().startswith("|")]
    veri = [s for s in satirlar[2:] if s.strip().strip("|").strip()]   # başlık + ayraç atlanır
    return [[c.strip() for c in re.split(r"(?<!\\)\|", s.strip().strip("|"))] for s in veri]


def test_YURURLUKTE_SATIRLARI_ISARETCI_bicimini_KORUYOR():
    """🔴 **Kutu B'nin bağlayıcı kısıtının ASIL kapısı — YAPISAL.**

    Kısıt şudur: ⟳ bloğu **otorite işaret eder, kural beyan etmez**. Bunu *"şu cümle
    geçmesin"* diye ölçmek **metin ölçmektir** ve bu depo o kusuru altı kez kaydetti.
    Yapısal karşılığı şudur: **her satır dört hücreli bir İŞARETÇİdir** —
    `MIMARI §` · konu · **otoriteyi alan faz** · `⟳ UYGULANMADI`. Bir kural beyanı bu
    şekle sığmaz: ne bir fazı işaret eder, ne *"uygulanmadı"* der.

    Özellikle `Durum` hücresi kritiktir: her satır **UYGULANMADI** demek zorundadır.
    Bir satır *"uygulandı"* demeye başladığı an artık işaretçi değil **beyandır** — ve
    §10'un `✅` = *"ölçüldü ve YAPILDI"* tanımını delerdi."""
    satirlar = _yururlukte_satirlari()
    assert satirlar, "⟳ tablosu BOŞ"
    for h in satirlar:
        s = " | ".join(h)
        assert len(h) == 4, f"⟳ satırı dört hücreli İŞARETÇİ değil ({len(h)} hücre): {s[:90]}"
        assert h[3] == "⟳ UYGULANMADI", (
            f"⟳ satırının `Durum` hücresi {h[3]!r} — işaretçi yalnız «UYGULANMADI» der. "
            "Başka bir şey diyorsa o bir BEYANDIR ve ilgili bölüme ölçümlü ✅ olarak "
            "yazılmalıdır (§10).")
        assert "FAZ" in h[2] or "§" in h[2], (
            f"⟳ satırı bir OTORİTE işaret etmiyor: {h[2]!r}. İşaretçinin işaret edeceği "
            "bir yer yoksa satır bir kuraldır.")
        assert h[0].strip("*` "), f"⟳ satırının MIMARI § hücresi boş: {s[:90]}"


def test_YURURLUKTE_BLOGU_KURAL_BEYAN_ETMIYOR():
    """Yapısal kapının yanındaki **tel tuzağı** (tripwire) — ve sınırı AÇIKÇA yazılıdır.

    Üç birebir ifade taranır. Bu **bir kanıt değildir**: bu kalıpları kullanmayan bir kural
    beyanı buradan geçer. Kısıtı gerçekten tutan şey yukarıdaki **yapısal** kapı (dört
    hücreli işaretçi + `⟳ UYGULANMADI`) ve her satırın **kendi tuzak testidir**. Tuzak,
    faz indiğinde kırılır; kırılmayan bir satır zaten yalan söylüyordur.

    ⚠ Kapsam **TABLO SATIRLARIDIR**, blok düzyazısı değil — ve bu bilinçlidir:
    bloğun düzyazısı **kendi defter tutma kuralını** (yaşam döngüsü: satır silinir →
    ölçümlü ✅ → tuzak ters çevrilir) anlatır. O bir MİMARİ kuralı değil, bu bloğun
    kullanma kılavuzudur; onu yasaklamak bloğu okunamaz yapardı. İlk sürüm blok
    TAMAMINI tarıyordu ve bloğun *kendi yasağını anlatan cümlesini* ihlal sandı —
    **yasağı anlatmak, yasağı çiğnemek değildir.**"""
    blok = _yururlukte_blogu()
    for yasak in ("yeni kural şudur", "artık şöyle olacak", "bundan sonra şu kural",
                  "bundan böyle", "yeni davranış şudur"):
        for h in _yururlukte_satirlari():
            s = " | ".join(h)
            assert yasak not in s.lower(), (
                f"⟳ TABLOSUNDA kural beyanı bulundu ({yasak!r}): {s[:90]}\n"
                "Blok yalnız OTORİTE işaret eder; kuralı yol haritası taşır.")
    # Bloğun kendi sınırını İLAN ETMESİ de kapının parçası: ilan silinirse okuyucu
    # satırları "yapılmış" sanabilir ve blok tam da engellemek için var olduğu şeyi doğurur.
    assert "BU BLOK BİR KURAL BEYAN ETMEZ" in blok, \
        "bloğun kendi sınır ilanı silinmiş — okuyucu satırları «yapılmış» sanabilir"
