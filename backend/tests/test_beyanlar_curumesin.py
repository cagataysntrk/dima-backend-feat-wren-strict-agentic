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
    i_ham = govde.index("llm.anlat(")
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

def test_LLM_ARAC_LISTESI_beyani_HALA_dogru():
    """`tools.llm_araclari()` planlayıcının LLM yüzeyi için yazıldı; F4 (plan SEÇİMİ)
    telemetriye bağlı olduğu için henüz tüketicisi yok. Bağlandığı gün bu test kırılır."""
    kaynak = _app_kaynagi("tools.py")
    assert "llm_araclari" not in kaynak, (
        "`tools.llm_araclari` artık çağrılıyor — MIMARI §11.6d'deki \"F4 henüz yok\" "
        "beyanı bayat.")


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

def test_DONEM_POLITIKASI_beyani_HALA_dogru():
    """FAZ -0.5c. `cube_router.needs_period` ve `is_period_only` ADR-0007 K3'ün ("dönem
    eksikse SOR") **tam doğru politikasını** taşıyor ama **üretimde sıfır çağıranı var**
    (yalnız testlerde); canlı kapı `_period_gate` daha zayıf bir kural uyguluyor.

    ## Neden ne BAĞLANDI ne SİLİNDİ

    İkisi de bir POLİTİKA kararıdır, bir hata değil:
      * **Bağlamak** `_period_gate`'in davranışını değiştirir — hangi soruların netleştirme
        alacağı değişir. Bu, ölçülmeden verilecek bir karar değil (Faz 0.5 → Faz 2b).
      * **Silmek** 13 testlik bir ŞARTNAMEYİ yok eder. `is_period_only`'nin kendi
        docstring'i (`cube_router.py`) bunu zaten kaydediyor: *"0 prod referansı, 13 test"*.

    Kalan tek doğru hamle: beyanı **kapıya** çevirmek. Biri bunları üretime bağladığı gün
    bu test kırılır ve MIMARI §6.2'nin güncellenmesini zorlar — beyan sessizce çürüyemez.
    """
    # ÇAĞRI aranır, ANMA değil: her iki ad da `cube_router.py`/`ask.py`'de YORUMLARDA
    # geçiyor (politikanın neden bağlı olmadığını anlatan notlar) ve bu meşrudur — hatta
    # istenen şeydir. Düz `ad in kaynak` bu yorumları "bağlandı" sanıp testi ilk koşuşta
    # yanlış-pozitif verdi; `dis_adim` kapısında da aynı düzeltme yapılmıştı.
    cagrilar: list[str] = []
    for satir in _app_kaynagi("cube_router.py").splitlines():
        s = satir.strip()
        if s.startswith("#"):
            continue
        for ad in ("needs_period", "is_period_only"):
            if re.search(rf"(?<![\w.]){ad}\s*\(", satir):
                cagrilar.append(f"{ad}: {s[:90]}")
    assert not cagrilar, (
        "Dönem politikası artık üretimde ÇAĞRILIYOR:\n  " + "\n  ".join(cagrilar)
        + "\nMIMARI §6.2'deki \"beyan var, bağlı değil\" kaydı BAYAT. Beyanı güncelle ve bu "
          "testi politikanın GERÇEKTEN uygulandığını ölçen bir teste çevir. (ADR-0007 K3 "
          "canlıya alınıyorsa `_period_gate`'in eski kuralıyla çakışmadığı da gösterilmeli.)")


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
