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
     # ⚠ Belirteç DOSYA varlığına bağlı: ilk sürümü `"ossie" in _app_kaynagi()` idi ve
     # **yorum satırlarını** yakalayıp tuzağı yanlış-kırmızı yaptı (ölçüm aracı kusuru).
     lambda: (APP / "ossie_import.py").exists() or (APP / "ossie.py").exists(),
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
    ("§7-CI", "FAZ 0.15",
     lambda: any("kapi.py" in f.read_text(encoding="utf-8", errors="ignore")
                 for f in (APP.parent.parent / ".github/workflows").glob("*.yml"))
             if (APP.parent.parent / ".github/workflows").exists() else False,
     "ölçüm kapıları CI'da"),
    ("§9-metrik", "FAZ 0.18",
     lambda: "MetricDefinition" in
             (APP.parent / "control_plane/models.py").read_text(encoding="utf-8"),
     "metrik kaydı = hakem"),
    ("§11-yetki", "FAZ 1.3",
     lambda: len({s.split('"')[1] for s in
                  (APP / "tools.py").read_text(encoding="utf-8").splitlines()
                  if s.strip().startswith("izin=")}) > 1,
     "yetki granülerliği (bugün 15/15 query:run)"),
    ("§12-tür", "FAZ 5.1·5.2",
     lambda: "TUR_TAKIP" in (APP / "followup.py").read_text(encoding="utf-8")
             or "TUR_PAYLAS" in (APP / "followup.py").read_text(encoding="utf-8"),
     "6./7. konuşma türü"),
    ("§13-viz", "FAZ 5.11·5.12",
     lambda: "list[VizSpec]" in (APP / "viz.py").read_text(encoding="utf-8"),
     "viz.recommend() çoklu dönüş"),
    ("§14-kapı", "FAZ 0.14",
     lambda: (APP.parent / "tests/test_yol_haritasi_butunlugu.py").exists(),
     "K1/K2'nin kör noktaları"),
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


def test_TUZAK_SAYISI_MIMARI_ILE_ORTUSUYOR():
    """Tuzak sayısı §0'daki ⟳ satır sayısıyla **birebir** olmalı.

    Aksi hâlde biri ⟳ ekleyip tuzağını yazmayı unutur ve o satır **sessizce** bayatlar —
    tam olarak bu bloğun engellemek için var olduğu şey."""
    mimari = (APP.parent / "MIMARI.md").read_text(encoding="utf-8")
    satir = mimari.count("⟳ UYGULANMADI")
    assert satir == len(_YURURLUKTE_TUZAKLARI), (
        f"MIMARI §0'da {satir} ⟳ satırı var, tuzak sayısı {len(_YURURLUKTE_TUZAKLARI)}. "
        "Her ⟳ satırının bir tuzağı OLMALI — yoksa beyan sessizce çürür.")


def test_YURURLUKTE_BLOGU_KURAL_BEYAN_ETMIYOR():
    """🔴 Kutu B'nin bağlayıcı kısıtı: ⟳ bloğu **otorite işaret eder, kural beyan etmez**.

    *"Yeni kural şudur"* diyen bir ⟳ satırı, okuyucuya **yapılmış** olduğunu düşündürür —
    ve `§10`'un `✅` = *"ölçüldü ve YAPILDI"* tanımını sessizce deler."""
    mimari = (APP.parent / "MIMARI.md").read_text(encoding="utf-8")
    bas = mimari.index("## §0 · ⟳ YÜRÜRLÜKTE")
    son = mimari.index("## 1. Sistem nedir")
    blok = mimari[bas:son]
    # ⚠ YALNIZ TABLO SATIRLARI taranır. İlk sürüm bloğun TAMAMINI tarıyordu ve bloğun
    # kendi AÇIKLAMASINI (*"hiçbir satır «yeni kural şudur» demez"*) bir ihlal sanıp
    # yanlış-kırmızı verdi. **Yasağı anlatmak, yasağı çiğnemek değildir.**
    tablo = [s for s in blok.splitlines() if s.lstrip().startswith("|")]
    for yasak in ("yeni kural şudur", "artık şöyle olacak", "bundan sonra şu kural"):
        for s in tablo:
            assert yasak not in s.lower(), (
                f"⟳ TABLOSUNDA kural beyanı bulundu ({yasak!r}): {s[:90]}\n"
                "Blok yalnız OTORİTE işaret eder; kuralı yol haritası taşır.")
    assert blok.count("⟳ UYGULANMADI") == len(_YURURLUKTE_TUZAKLARI)
