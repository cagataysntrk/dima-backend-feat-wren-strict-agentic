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
import json
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
    # ⟳ **ÇAPA KAYDI — T2 ŞABLON BASAMAĞI.** `index()` artık **ilk** `narration`
    # atamasını buluyordu ve o, LLM'den ÖNCE koşan **şablon** basamağının atamasıdır
    # (0 LLM). Kapı bu yüzden kırmızı verdi ve **haklıydı**: çapası kaymıştı.
    #
    # 🔴 Kapı GEVŞETİLMEDİ, iki yönde KESKİNLEŞTİRİLDİ:
    #   (1) LLM ataması `rindex` ile aranır — guard hâlâ arada olmak zorunda;
    #   (2) şablon atamasının LLM çağrısından **ÖNCE** olduğu ayrıca ölçülür, yani
    #       merdiven sırası da kilitli: ucuz basamak önce denenir.
    #
    # *Bir kapının çapası kayınca doğru tepki onu silmek değil, yeniden çakmaktır.*
    i_yaz = govde.rindex('yorum["narration"] =')
    assert i_ham < i_guard < i_yaz, (
        "LLM çıktısı guard'a UĞRAMADAN yayımlanabiliyor — fail-closed sözleşme kırık")
    i_sablon = govde.index('yorum["narration"] = _sablon')
    assert i_sablon < i_ham, (
        "🔴 MERDİVEN SIRASI TERS: şablon basamağı (0 LLM) LLM çağrısından SONRA "
        "deneniyor — ucuz basamağın pahalıdan sonra koşması, merdiveni merdiven "
        "olmaktan çıkarır")


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

def test_CUBE_QUERY_HASH_TUKETILIYOR_ama_CACHE_KURULMADI():
    """⟳ **BU TUZAK ATEŞLEDİ ve TUZAKTAN KAPIYA dönüştü (FAZ 5.13a).**

    Eski hâli MIMARI'nin *"primitif, tüketici bekliyor"* beyanını koruyordu ve
    **tüketici geldiği gün kırıldı** — kurulduğu iş buydu. Tüketici: `find_previous()`
    (**hayalet seri**).

    🔴 **Yeni kilit iki yönlü:** primitif **kullanılıyor** olmalı (yetim değil) **ama
    sonuç cache'i HÂLÂ KURULMAMIŞ** olmalı. İkincisi bilinçli: *tekrar oranı ölçülmedi
    ve ölçülmemiş bir ihtiyaç için altyapı kurulmaz.*

    ⚠ Hayalet seri bir cache **değildir**: bir sonucu **döndürmez**, bir öncekinin
    **var olduğunu** söyler. Aradaki fark, cevabın nereden geldiğidir.
    """
    kaynak = _app_kaynagi("contracts.py")
    assert "cube_query_hash" in kaynak, (
        "🔴 `cube_query_hash` artık HİÇ kullanılmıyor — hayalet seri (FAZ 5.13a) geri "
        "alınmış olabilir ve primitif yine yetim kaldı.")
    assert "find_previous" in kaynak
    # 🔴 Sonuç cache'i HÂLÂ kurulmamış olmalı: `find_previous` ham sonuç DÖNMEZ.
    import ast as _a

    agac = _a.parse((APP / "contracts.py").read_text(encoding="utf-8"))
    fn = next(n for n in _a.walk(agac)
              if isinstance(n, _a.FunctionDef) and n.name == "find_previous")
    donen = {c.value for c in _a.walk(fn)
             if isinstance(c, _a.Constant) and isinstance(c.value, str)}
    assert "result" not in donen and "rows" not in donen, (
        "🔴 `find_previous` ham SONUÇ döndürüyor — bu bir CACHE'tir ve tekrar oranı "
        "ÖLÇÜLMEDEN cache kurulmaz (MIMARI §5'in kendi kararı).")


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
    """Silme kararının bedeli: 13 vakalık bir şartname duruyor. Sayı düşerse şartname
    **aşınıyor** demektir.

    ⟳ **ÖLÇÜM YENİDEN NİŞANLANDI (denetim D3).** `is_period_only` KALDIRILDI ve şartnamesi
    **gerçek akışa** (`deterministic_refine`) taşındı — ama bu tuzak hâlâ **fonksiyon
    çağrısı** sayıyordu ve 13 → 3'e düştüğünü görüp kırmızı verdi.
    *Tuzak haklıydı: kaldırma gerçekten şartnameyi tehdit ediyordu.* Ama ölçtüğü şey
    yanlış yerdeydi: şartname artık **parametrik vakalardır**, çağrılar değil.

    🔴 Yeni belirteç **davranış vakalarını** sayar. Böylece şartname yalnız *"kaç kez
    çağrıldı"*yı değil, *"kaç Türkçe dönem ifadesi gerçek akıştan geçiyor"*u kilitler —
    ve bu, silinen fonksiyonun asla veremediği bir güvencedir.
    """
    import pathlib
    import re

    t = (pathlib.Path(__file__).resolve().parents[1] / "tests/test_cube_router.py").read_text(
        encoding="utf-8")
    # (a) eski yüzey (varsa) + (b) yeni parametrik şartname vakaları
    kullanim = len(re.findall(r"\b(needs_period|is_period_only)\s*\(", t))
    m = re.search(r"@pytest\.mark\.parametrize\(\s*\"ifade\",\s*\[(.*?)\]\s*\)",
                  t, re.S)
    kullanim += len(re.findall(r'"[^"]+"', m.group(1))) if m else 0
    assert kullanim >= 13, (
        f"dönem politikası şartnamesi {kullanim} vakaya düşmüş (>=13 bekleniyordu) — "
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

def _principalsiz_cagri_var() -> bool:
    """`WrenService.query`/`dry_plan` çağrılarından **kimlik geçmeyen** var mı?

    Ölçüm `test_motor_cls.py`'nin sahibinde; burada yalnız **çağrılır** — iki ayrı
    sayaç yazmak, birinin sessizce bayatlaması demekti.
    """
    import ast as _ast

    for yol in sorted(APP.rglob("*.py")):
        if yol.name in ("wren_service.py", "rls.py"):
            continue
        try:
            agac = _ast.parse(yol.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for n in _ast.walk(agac):
            if (isinstance(n, _ast.Call) and isinstance(n.func, _ast.Attribute)
                    and n.func.attr in ("query", "dry_plan")
                    and not any(k.arg == "principal" for k in n.keywords)):
                return True
    return False


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
    # ⟳ `§3·§3.3` **TERS ÇEVRİLDİ** — FAZ 2.1(a) indi (çekirdek katman + beşinci üreteç);
    # tuzak `test_TERS_TUZAK_FAZ_2_1_CEKIRDEK_KATMAN_AYAKTA`'ya taşındı (SİLİNMEDİ).
    # ⟳ `§3.4-RLS` **TERS ÇEVRİLDİ** — FAZ 1.1 indi (`always_filter` → RLAC), tuzak
    # `test_TERS_TUZAK_FAZ_1_1_MOTOR_RLS_AYAKTA`'ya taşındı (silinmedi).
    # §0'ın `§3.4` satırı DARALDI: geriye **kimliğe bağlı** RLS (`SessionProperty`, FAZ 1.2)
    # kaldı ve belirteç ona nişanlandı. `1.1` SABİT yüklemi çevirdi; session'a bağlı kural
    # doğmadan `oturum_ozellikleri()` yazmak K3 (ters yetim) ihlali olurdu.
    # ⚠ Belirteç **YAPISAL**, alt-dize DEĞİL — ve bu bir düzeltme: ilk sürüm
    # `"SessionProperty" in _app_kaynagi("")` idi ve `app/rls.py`'nin **YORUMUNU** yakalayıp
    # tuzağı yanlış-KIRMIZI yaptı (o yorum, session tesisatının NEDEN ertelendiğini
    # anlatıyor). `§3.4-osi` aynı yere iki kez düşmüştü; üçüncüsü olmasın diye artık
    # **tanımın kendisi** aranıyor: bir fonksiyon var mı, bir çağrı yapılıyor mu.
    # ⚠ `_app_kaynagi(x)` bir dosyayı **DIŞLAR**, seçmez — ilk yazımımda imzayı ters
    # kullandım ve tuzak yine yanlış yeri ölçtü. Dosya doğrudan okunuyor.
    # ⟳ `§3.4-session` **TERS ÇEVRİLDİ** — FAZ 1.2 ile `oturum_ozellikleri()` ve
    # `properties=` geçişi indi. Ama iş BİTMEDİ: 36 çağrı sitesi hâlâ kimlik geçmiyor
    # (`test_motor_cls.py::_principalsiz_cagrilar`). Satır o KUYRUĞA nişanlandı: sıfıra
    # indiği gün tuzak yine kırılır ve `motor_cls=on` açılabilir hâle gelir.
    ("§3.4-kuyruk", "FAZ 1.2 kuyruğu",
     lambda: not _principalsiz_cagri_var(),
     "SessionProperty TÜM çağrı sitelerinde"),
    # ⟳ `§3.4-osi`/`§3.4-mcp` **TAMAMEN KAPANDI** — FAZ 3.4 (Ossie ithali) ve FAZ 4.5
    # (MCP yüzeyi) indi; §0'ın `§3.4` *"bilerek alınmayanlar"* satırı SİLİNDİ ve gövdeye
    # ölçümlü `✅` yazıldı. İki ters tuzak (SİLİNMEDİ, çevrildi):
    # `test_TERS_TUZAK_FAZ_3_4_OSSIE_ITHALI_AYAKTA` · `test_TERS_TUZAK_FAZ_4_5_MCP_AYAKTA`.
    # ⟳ `§4` **TAMAMEN KAPANDI** — FAZ 6.0 (D9) · 6.1 (onay akışı) · 6.2 (yazma
    # araçları) indi. §0'ın `§4` satırı SİLİNDİ; ters tuzak:
    # `test_TERS_TUZAK_FAZ_6_2_YAZMA_ARACLARI_AYAKTA`.
    # ⟳ `§5-grain` **TERS ÇEVRİLDİ** — FAZ 2.1(a)/(b) indi (grain sözleşmesi fail-closed
    # ve `cari`'de gerçek pack'ler üstünde ateşliyor); aynı ters-tuzağa taşındı.
    # ⟳ `§5-18.yasak` **TERS ÇEVRİLDİ** (`B-G5`, 2026-08-07) — satır §0'dan SİLİNDİ çünkü
    # yasak indi: `MIMARI:442` yasağı, envanter kapısını (`test_kisa_devre_yok.py`, 13 dal
    # gerekçeli) ve adıyla anılan vakanın (`değişti→eğitim`) aday'a çevrilmesini anlatıyor.
    # ⚠ **Tam uygulaması ölçülüp GERİ ALINDI** (korpus %95,1→%93,5 · eval −%1,8 · süitte 7
    # kırmızı) ve yasağın **dördüncü koşulu** oradan doğdu. Tuzak SİLİNMEDİ, ters çevrildi:
    # `test_TERS_TUZAK_18_YASAK_ENVANTER_AYAKTA`.
    # ⟳ `§7-CI` **TERS ÇEVRİLDİ** — FAZ 0.15 indi, tuzak
    # `test_TERS_TUZAK_FAZ_0_15_CI_KAPILARI_AYAKTA`'ya taşındı (silinmedi).
    # §0'ın `§7` satırı DARALDI: geriye **risk-kapsam eğrisi** (FAZ 4.2) kaldı ve
    # belirteç ona yeniden nişanlandı. Eski belirteç (`.github/workflows`'ta `kapi.py`)
    # bugün DOĞRU olduğu için tuzağı kalıcı-kırmızı bırakırdı; oysa satırın inmemiş
    # yarısı hâlâ bir işaretçiye muhtaç.
    # ⟳ `§7-risk` **TERS ÇEVRİLDİ** — FAZ 4.2 indi (risk-kapsam eğrisi yayımlandı); tuzak
    # `test_TERS_TUZAK_FAZ_4_2_RISK_KAPSAM_AYAKTA`'ya taşındı (SİLİNMEDİ). §0'ın `§7` satırı
    # tamamen kapandı: ölçüm sözleşmesinin çerçevesi (A1) zaten `lab/kapi.py` ile inmişti.
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
    # ⟳ `§12` **TAMAMEN KAPANDI** — 6./7. tür (5.1/5.2) İNDİ ve çapa zinciri
    # (`capa_zinciri`) **beta'ya AÇILDI** (denetim D4). İki ters tuzak (SİLİNMEDİ):
    # `test_TERS_TUZAK_FAZ_5_1_5_2_YENI_TURLER_AYAKTA` ·
    # `test_TERS_TUZAK_CAPA_ZINCIRI_ACIK`.
    # ⟳ `§13-viz` **TERS ÇEVRİLDİ** — FAZ 5.11 (*"ne zaman çizilmez"*) ve 5.12 (çoklu
    # dönüş) indi; tuzak `test_TERS_TUZAK_FAZ_5_12_COKLU_DONUS_AYAKTA`'ya taşındı
    # (SİLİNMEDİ). §0'ın `§13` satırı tamamen kapandı.
    # ⟳ `§8.2-ADR` **TERS ÇEVRİLDİ** — FAZ 4.6 indi (20 dosya + kapı); tuzak
    # `test_TERS_TUZAK_FAZ_4_6_ADR_DOSYALARI_AYAKTA`'ya taşındı (SİLİNMEDİ).
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


def _yaml_bayraklari() -> dict:
    """`demo/packs/features.yml` fabrika varsayılanları — tuzak belirteçleri için."""
    import yaml as _y

    d = _y.safe_load((APP.parent / "demo/packs/features.yml").read_text(encoding="utf-8"))
    return dict((d or {}).get("features") or {})


def test_TERS_TUZAK_FAZ_6_2_YAZMA_ARACLARI_AYAKTA():
    """⟳ `§4` ters çevrildi: yazma araçları **var olmalı** ve **kapalıyken kayda hiç
    girmemeli**.

    🔴 İkinci şart birincisinden önemli ve maddenin tamamı odur: *geri alma "kapatmak"
    değil **hiç açmamaktır**.* Bir aracı kayda alıp sonra engellemek, o engelin bir gün
    **unutulabileceği** anlamına gelir; kayda hiç almamak unutulamaz.
    """
    from app.yazma_araclari import YAZMA_KAYIT, geri_alinamaz_olanlar

    assert (APP / "yazma_araclari.py").exists(), "🔴 FAZ 6.2 GERİ ALINDI."
    # ⟳ **`measures.approve` KAYITTAN ÇIKTI (2026-08-12) — ve bu bir karardır.**
    #
    # `/ask/eylem`'in kaydında (`EYLEM_KAYIT`) karşılığı **yok** ve o kayıt fail-closed
    # (`beyan()` → 400). Yani ajan onu önerse **kullanıcı onaylayamazdı**.
    # *Onay yolu olmayan bir öneri, bir öneri değil bir çıkmazdır.*
    #
    # ⚠ Eklenmesi `EYLEM_KAYIT`'a yeni bir eylem yazmayı gerektirir ve o, `/ask/eylem`'in
    # **kabul kümesini** değiştirir — ayrı bir karar, ayrı bir ölçüm. Ölçüsü de yazılı:
    # `measure:approve` bir ölçüyü **kataloğa** alır, kapsamı bir panodan geniştir.
    # ⟳ **`preferences.set` KAYDA GİRDİ (2026-08-12) — ve `measures.approve`'un TERSİ
    # sebeple.** O çıkarılmıştı çünkü `EYLEM_KAYIT`'ta karşılığı **yoktu**: ajan önerse
    # kullanıcı **onaylayamazdı** (*«onay yolu olmayan bir öneri bir çıkmazdır»*).
    # `preferences.set`'in onay yolu **var** — `ARAC_EYLEM["preferences.set"] =
    # "tercih.kaydet"` ve aşağıdaki `_eylem.beyan(...)` döngüsü onu **fail-closed**
    # doğruluyor: karşılığı olmasa bu satır `KeyError` ile düşerdi.
    #
    # ⊙ Yani listeye ad eklemek kapıyı **gevşetmiyor**; kapının asıl yüklemi (her yazma
    # aracının bir onay yolu olması) **aynen** koşuyor ve yeni adı da **o** sınıyor.
    # ⚠ Geri alınabilir olduğu için `geri_alinamaz_olanlar()` **değişmedi** — aşağıdaki
    # yüklem hâlâ yalnız `schedules.create` bekliyor ve bu **bilinçli**.
    assert {a.ad for a in YAZMA_KAYIT} == {"dashboards.create", "schedules.create",
                                           "preferences.set"}
    assert all(a.yan_etki == "yazar" for a in YAZMA_KAYIT)
    # 🔴 Ve kaydın **tamamının** onay yolu olmalı — iki kayıt birbirine bağlandı
    # (`ARAC_EYLEM`, `§C1`'in ikinci vakası). Bu satır, listenin bir gün yeniden
    # büyümesi hâlinde çıkmaz bir öneriyi **doğduğu anda** yakalar.
    from app import eylem as _eylem
    from app.yazma_araclari import ARAC_EYLEM
    for a in YAZMA_KAYIT:
        _eylem.beyan(ARAC_EYLEM[a.ad])          # fail-closed: yoksa KeyError

    # 🔴 GERİ ALINAMAZLIK GİZLENMİYOR.
    assert geri_alinamaz_olanlar() == ["schedules.create"], (
        "🔴 Geri alınamaz araç listesi değişti — *geri alınamazlığı gizlemek, onu geri "
        "alınabilir sanmaktan kötüdür: kullanıcı bir daha hiç sormaz.*")
    for a in YAZMA_KAYIT:
        assert a.geri_alma_ref or "GERİ ALINAMAZ" in a.notlar.upper()

    # 🔴 Kayda giriş **bayrağa** bağlı: `tools.py` onu `Settings`'ten çözmeli.
    kaynak = (APP / "tools.py").read_text(encoding="utf-8")
    assert "yazma_araclari" in kaynak and "_yazma_araclari()" in kaynak, (
        "🔴 Yazma araçları KOŞULSUZ kayda giriyor — bayrak kapalıyken de yüzey açık "
        "demektir.")


def test_TERS_TUZAK_FAZ_6_1_ONAY_AKISI_AYAKTA():
    """⟳ `§4` daraldı: onay akışı **inmiş olmalı** ve **yüzey büyümemiş** olmalı.

    🔴 İkinci şart birincisinden önemli. Bu maddenin tamamı şu cümleye dayanıyor:
    *"güvenlik imzadan değil, **yetki yüzeyinin genişlememesinden** geliyor."* Onay
    akışı bir **kademelendirmedir**; bir gün araç kaydına `yan_etki="yazar"` bir araç
    girerse, kademelendirme bir **genişlemeye** dönüşür ve o gün bu kapı kırmızı olur.
    """
    from app import onay_akisi as oa
    from app import tools

    assert (APP / "onay_akisi.py").exists(), (
        "🔴 FAZ 6.1 GERİ ALINDI: `app/onay_akisi.py` yok.")
    # Durum makinesi KAPALI kalmalı — serbest bir durum alanı bir dilektir.
    assert set(oa.DURUMLAR) == {"taslak", "onay_bekliyor", "onaylandi", "reddedildi",
                                "geri_alindi"}
    assert oa.GECISLER["reddedildi"] == ()
    # Süre aşımı KORUNUR: dün verilmiş bir "evet", bugünün dünyasına verilmemiştir.
    assert oa.VARSAYILAN_OMUR_SN > 0
    # 🔴 YÜZEY BÜYÜMEDİ.
    assert _yazan_arac_sayisi() == 0, (
        "🔴 Araç kaydına yazan araç girmiş — onay akışı bir KADEMELENDİRMEDİR, bir "
        "yüzey genişlemesi değil.")
    assert not [a.ad for a in tools.hepsi() if a.yan_etki == "yazar"]


def test_TERS_TUZAK_FAZ_5_12_COKLU_DONUS_AYAKTA():
    """⟳ `§13-viz` ters çevrildi: çoklu dönüş **inmiş olmalı** ve **tekil dönüş
    KIRILMAMALI**.

    🔴 İkinci şart birincisinden önemli: `recommend()` her zaman liste dönmeye başlarsa
    on küsur çağıran sessizce bozulur. *Geriye uyumluluk bir vaat değil, imzanın
    kendisidir.*
    """
    from app import viz

    assert "list[VizSpec]" in (APP / "viz.py").read_text(encoding="utf-8"), (
        "🔴 FAZ 5.12 GERİ ALINDI: `viz.recommend()` çoklu dönüş sözleşmesini taşımıyor.")
    r = {"columns": ["makine", "fire"],
         "rows": [{"makine": f"M{i}", "fire": i + 1} for i in range(5)]}
    assert isinstance(viz.recommend(r, {"fire": "kg"}), dict), (
        "🔴 TEKİL DÖNÜŞ KIRILDI — on küsur çağıran sessizce bozulur.")
    assert isinstance(viz.recommend(r, {"fire": "kg"}, paket=True), list)


def test_TERS_TUZAK_CAPA_ZINCIRI_ACIK():
    """⟳ `§12-çapa` ters çevrildi: çapa zinciri **açık kalmalı** ve kural **ateşlemeli**.

    🔴 Asıl kilit bayrağın değeri değil, **kuralın çalışması**: bayrak açık ama
    `KURAL_CAPA` hiç ateşlemiyorsa, açılış bir **kâğıt üstü kazanç** olur.

    ⚠ Ve çelişkide **SORULMALI** (ADR-0008): farklı cube'lardan iki çapa geldiğinde
    sistemin birini seçmesi, tam da bu deponun avladığı sessiz-yanlış sınıfıdır.
    """
    from app import context as ctx

    assert _yaml_bayraklari().get("capa_zinciri") not in (None, "off"), (
        "🔴 `capa_zinciri` yine kapalı — `_capalar` boş kalır ve karta yanıt verme kuralı "
        "üretimde HİÇ ateşlemez. Mekanizma var, yolu kapalı demektir.")
    cq = {"cube": "parti", "measures": ["fire_orani_yuzde"], "dimensions": ["makine"]}
    b = ctx.coz(cube_query=None, prev_sql=None, history=[], capalar=[cq],
                capa_etiketi="fire raporu", atif=False)
    assert b.kural == ctx.KURAL_CAPA and (b.cube_query or {}).get("cube") == "parti"
    b2 = ctx.coz(cube_query=None, prev_sql=None, history=[],
                 capalar=[cq, {"cube": "oee", "measures": ["ort_oee"]}],
                 capa_etiketi=None, atif=False)
    assert (b2.adaylar or []), (
        "🔴 Farklı cube'lardan iki çapada sistem SORMUYOR — belirsizlikte tahmin etmek "
        "(ADR-0008) bu deponun avladığı sessiz-yanlış sınıfıdır.")


def test_TERS_TUZAK_FAZ_5_1_5_2_YENI_TURLER_AYAKTA():
    """⟳ `§12-tür` ters çevrildi: 6. ve 7. tür **inmiş olmalı** ve **her thread sınıfında**
    çalışmalı.

    🔴 İkinci şart birincisinden önemli: 5.0 tam olarak *"yeni türler de aynı bloğun
    içine doğar"* riskini kapatmak için indi. Bir gün biri sınıflandırmayı yine bir
    `if`in içine taşırsa, `test_FAZ_5_0_sinifla_STRUCTURAL_BLOGUN_DISINDA` kırmızı olur
    ve bu tuzak onun **niçin** kurulduğunu anlatır.
    """
    from app import followup

    assert hasattr(followup, "TUR_TAKIP") and hasattr(followup, "TUR_PAYLAS"), (
        "🔴 FAZ 5.1/5.2 GERİ ALINDI — MIMARI §12'nin daraltılmış satırı artık yanlış.")
    for ifade, tur in (("bunu takip et", followup.TUR_TAKIP),
                       ("mudure 3 cumle yaz", followup.TUR_PAYLAS)):
        n = followup.sinifla(ifade, baglam_var=True)
        assert n.sinif == followup.SINIF_KONUSMA and n.tur == tur, (
            f"🔴 `{ifade}` artık tanınmıyor — ölçülmüş bir ERİŞİLEMEZLİK geri geldi.")


def test_TERS_TUZAK_FAZ_4_6_ADR_DOSYALARI_AYAKTA():
    """⟳ `§8.2` ters çevrildi: ADR dosyaları **var olmalı** ve **rekonstrüksiyon** kalmalı.

    🔴 İkinci şart birincisinden önemli: dosyalar bir gün *"orijinal karar kaydı"* gibi
    okunmaya başlarsa, uydurulmuş bir tarihle doldurulmuş bir arşive dönüşürler.
    """
    kok = APP.parent / "docs/adr"
    dosyalar = sorted(kok.glob("[0-9][0-9][0-9][0-9]-*.md"))
    assert len(dosyalar) >= 20, (
        f"🔴 FAZ 4.6 GERİ ALINDI: `docs/adr/` {len(dosyalar)} dosya. MIMARI §8.2'nin "
        f"ölçümlü `✅` beyanı DOĞRULANAMIYOR — ve `ADR-0007-K3`'e dayanan §C/3 çıkış "
        f"ölçütü yine var olmayan bir belgeye dayanır.")
    for p in dosyalar:
        metin = p.read_text(encoding="utf-8")
        ust = metin.upper()
        # ⚠ **KÖKEN İKİ HÂLLİ** (FAZ 4.6 sonrası): `0003…0024` rekonstrüksiyon, `0025+`
        # kararla **aynı turda** yazıldı. İkisini tek damgayla istemek, yeni kayıtları
        # *"sonradan türetilmiş"* diye **olduğundan zayıf** gösterirdi.
        assert ("REKONSTRÜKSİYON" in ust or "GÜNÜ YAZILDI" in ust), (
            f"🔴 `{p.name}` KÖKENİNİ ilan etmiyor — ne zaman yazıldığı bilinmeyen bir "
            f"karar kaydı, doğrulanamaz bir kayıttır.")
        assert "kod kazanır" in metin, (
            f"🔴 `{p.name}` çelişkide kodun kazandığını söylemiyor — belge bir otorite "
            f"gibi okunabilir hâle gelmiş.")


def test_TERS_TUZAK_FAZ_4_5_MCP_AYAKTA():
    """⟳ `§3.4-mcp` ters çevrildi: MCP **inmiş olmalı** ve **ince çevirici** kalmalı.

    🔴 Asıl kilit dosya varlığı değil, **ayrışmamaktır**: MCP kendi araç kaydını kurduğu
    gün üç yüzey (LLM · MCP · UI) ayrışır ve bir araç bir yüzeyde açık, ötekinde kapalı
    olur — hangisinin doğru olduğunu kimse bilemez. O gün bu kapı kırmızıya döner.
    """
    from app import mcp, tools

    assert (APP / "mcp.py").exists() and (APP / "routers/mcp.py").exists(), (
        "🔴 FAZ 4.5 GERİ ALINDI: MIMARI §3.4'ün ölçümlü `✅` beyanı DOĞRULANAMIYOR.")
    assert {a["name"] for a in mcp.araclar(None)} == {
        a["name"] for a in tools.llm_araclari(None)}, (
        "🔴 MCP ve LLM araç kümeleri AYRIŞTI — MCP kendi kaydını kurmuş olabilir.")


def test_TERS_TUZAK_FAZ_4_2_RISK_KAPSAM_AYAKTA():
    """⟳ `§7-risk` ters çevrildi: eğri **inmiş olmalı** ve *skaler güven* taşımamalı.

    🔴 Kapı yalnız *"dosya var mı"* demiyor — MIMARI'nin **yasağını** da kilitliyor:
    *"kalibre edilmediği sürece o sayı bir güven değil bir SÜSTÜR."* Eğri bir gün bir
    `confidence` alanı üretmeye başlarsa, bu kapı **kırmızı** olur.

    ⚠ Belirteç **YAPISAL** (AST), alt-dize değil: modülün kendi docstring'i `confidence`
    kelimesini *yasağı anlatmak için* kullanıyor. Bu deponun on kez ödediği ders —
    **beyan ile beyanın anlatımı farklı şeylerdir.**
    """
    import ast as _a

    yol = APP.parent / "lab/risk_kapsam.py"
    assert yol.exists(), (
        "🔴 FAZ 4.2 GERİ ALINDI: `lab/risk_kapsam.py` yok. MIMARI §9.1'in ölçümlü `✅` "
        "beyanı artık DOĞRULANAMIYOR — beyan ya geri alınmalı ya da araç geri gelmeli.")
    agac = _a.parse(yol.read_text(encoding="utf-8"))
    adlar = {n.id for n in _a.walk(agac) if isinstance(n, _a.Name)}
    adlar |= {n.attr for n in _a.walk(agac) if isinstance(n, _a.Attribute)}
    sabitler = {n.value for n in _a.walk(agac)
                if isinstance(n, _a.Constant) and isinstance(n.value, str)}
    # `confidence`/`consistency` KODDA geçmez (docstring bir Constant'tır ama modül
    # docstring'i hariç tutulur: aşağıda yalnız ad ve ANAHTAR sabitleri denetlenir).
    anahtarlar = {v for v in sabitler if len(v) < 40 and " " not in v}
    for yasak in ("confidence", "consistency_k", "auroc"):
        assert yasak not in adlar, (
            f"🔴 `risk_kapsam.py` artık `{yasak}` KULLANIYOR. MIMARI: *kalibre edilmediği "
            f"sürece o sayı bir güven değil bir SÜSTÜR.* Eğri ayrık kapılar üstünde kalır.")
        assert yasak not in anahtarlar, (
            f"🔴 `risk_kapsam.py` çıktısına `{yasak}` anahtarı girmiş — skaler güven "
            f"puanı UYDURULMAZ.")
    # Determinizm sınıfı taşınıyor mu — eğrinin ASIL taahhüdü bu.
    from lab.risk_kapsam import DETERMINIZM, KAPILAR, egri

    assert set(KAPILAR) >= {"route", "discovery"}
    nokta = egri({"route": 10, "tie_chip": 5, "llm_gerekli": 5})
    assert [n["kapi"] for n in nokta] == ["route", "tie_chip", "llm_gerekli"]
    assert all("determinizm" in n for n in nokta), "her nokta determinizm sınıfı taşımalı"
    assert all("hata_orani" not in n for n in nokta), (
        "🔴 `hata_orani` GERİ GELMİŞ — bu araç bir kapının hata oranını ÖLÇEMEZ; "
        "yazmak uydurma olurdu (MIMARI §9.1).")
    # Kapsam MONOTON artmalı: her kapı bir öncekinin cevaplayamadığını devralır.
    kapsamlar = [n["kapsam"] for n in nokta]
    assert kapsamlar == sorted(kapsamlar), "kapsam monoton artmalı"
    assert DETERMINIZM["route"] == "deterministik"


def test_TERS_TUZAK_FAZ_3_4_OSSIE_ITHALI_AYAKTA():
    """⟳ `§3.4-osi` daraldı: **ithal indi** ve `olculmedi` damgası ZORUNLU kalmalı.

    🔴 Asıl kilit dosya varlığı değil, **damgadır**: *ithal bir ilişki, sessiz "sağlıklı"
    DEĞİLDİR.* Bir gün biri `certified: "ok"` yazarsa, bu deponun en pahalı hatası
    (sessiz-yanlış) **ithal edilmiş** olur — ve o an bu kapı kırmızıya döner.
    """
    from app.ossie import SERTIFIKA_OLCULMEDI, OssieIthalHatasi, cevir

    r = cevir({"version": "0.1",
               "datasets": [{"name": "d", "metrics": [{"name": "m"}]}],
               "relationships": [{"name": "r", "datasets": ["a", "b"]}]})
    assert r["relationships"][0]["certified"] == SERTIFIKA_OLCULMEDI, (
        "🔴 İTHAL DAMGASI DÜŞTÜ: fan-out sertifikası ölçülmeden `olculmedi` DIŞINDA bir "
        "değer taşıyamaz. Başkasının modelinin doğru olduğunu VARSAYMAK, sessiz-yanlışı "
        "ithal etmektir.")
    assert r["cubes"][0]["ithal_kaynak"] == "ossie", "kaynak damgası kaybolmamalı"
    # Fail-closed: adsız kayıt ATLANMAZ, REDDEDİLİR.
    with pytest.raises(OssieIthalHatasi):
        cevir({"datasets": [{"name": "", "metrics": []}]})


def test_TERS_TUZAK_FAZ_2_1_CEKIRDEK_KATMAN_AYAKTA():
    """⟳ **TUZAKTAN KAPIYA — FAZ 2.1 indi, İKİ tuzak birden TERS ÇEVRİLDİ.**

    Eski yön (iki satır): *"`§3·§3.3` çekirdek katman / compose birleştirme semantiği
    HENÜZ UYGULANMADI"* ve *"`§5-grain` grain sözleşmesi HENÜZ UYGULANMADI"*. FAZ 2.1(a)
    indiği gün **ikisi de kırıldı** — kuruldukları iş buydu.

    Yeni yön: **dördü de ayakta kalmalı.** Bu bir belge iddiası değil, **yapısal** bir
    kontrol: çekirdek pack'i, beşinci üreteç, fail-closed grain kapısı ve gölge diff aracı.

    🔴 Bir üretecin sessizce kaldırılması, `compose()`'un `copy2` ile **dosya düzeyinde**
    ezmesine geri dönmek demektir — yani bir çekirdek katmanın ERP katmanı tarafından
    **sessizce silinmesi**. Ölçülen kusur buydu ([KANIT §10.2]).
    """
    import ast as _ast

    assert (APP.parent / "demo" / "packs" / "cekirdek" / "metrik_sozlugu.yml").is_file(), \
        "çekirdek metrik sözlüğü SİLİNMİŞ"
    kaynak = (APP / "compose.py").read_text(encoding="utf-8")
    fn = next(n for n in _ast.walk(_ast.parse(kaynak))
              if isinstance(n, _ast.FunctionDef) and n.name == "compose")
    cagrilar = {getattr(n.func, "id", "") for n in _ast.walk(fn) if isinstance(n, _ast.Call)}
    assert "_merge_cube_metadata" in cagrilar, \
        "beşinci üreteç compose()'tan ÇIKARILMIŞ — çekirdek katman ölü"
    assert "GrainIhlali" in (APP / "cekirdek.py").read_text(encoding="utf-8"), \
        "grain sözleşmesinin fail-closed reddi KALDIRILMIŞ"
    assert (APP.parent / "lab" / "mdl_diff.py").is_file(), \
        "gölge diff aracı silinmiş — göçün kabul ölçütü ÖLÇÜLEMEZ olur"


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


def test_TERS_TUZAK_FAZ_1_1_MOTOR_RLS_AYAKTA():
    """⟳ **TUZAKTAN KAPIYA — FAZ 1.1 indi, tuzak TERS ÇEVRİLDİ.**

    Eski yön: *"motor RLS'i kodda HİÇ geçmiyor"*. FAZ 1.1 indiği gün **kırıldı**.
    Yeni yön: **çeviri ayakta kalmalı ve `off` birebir kalmalı**.

    Neden ikisi birden: yalnız *"`app/rls.py` var"* demek yetmez — biri `manifeste_yaz`'ı
    `off`'ta da yazar hâle getirirse dosya **yerinde durur**, `GERİ AL` mekanizması
    **sessizce kaybolur** ve KURAL B çürür. Kapı, çevirinin **iki ucunu** birden tutar.
    """
    rls = pytest.importorskip("app.rls")
    assert "off" in rls.KADEMELER and "shadow" in rls.KADEMELER and "on" in rls.KADEMELER

    man = {"models": [{"name": "m"}],
           "cubes": [{"name": "c", "baseObject": "m", "alwaysFilter": "x = 0"}]}
    ham = json.dumps(man).encode()

    for kademe in ("off", "shadow"):
        yeni, n = rls.manifeste_yaz(ham, kademe=kademe)
        assert (yeni, n) == (ham, 0), (
            f"🔴 `{kademe}` manifesti DEĞİŞTİRİYOR — `off` GERİ AL'ı, `shadow` ise "
            "*'gölge ölçer, davranmaz'* kuralını çiğner.")

    yeni, n = rls.manifeste_yaz(ham, kademe="on")
    assert n == 1 and rls.MODEL_ANAHTARI in json.loads(yeni)["models"][0], (
        "🔴 FAZ 1.1 GERİ ALINMIŞ: `on` kademesinde RLAC yazılmıyor.")


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

    ⟳ **GÜNCELLEME (kullanıcı kararı, 2026-08-04):** aranan bayrak `--tam` değil
    **`--hepsi`**. Yerel demet kapısı **yalnız korpusa** indirildi; süit · `eval` ·
    senaryo **silinmedi**, gecelik CI'ya taşındı. Yani bu kapı artık **daha da
    kritiktir**: o üç adımın koştuğu **tek yer** burasıdır. Workflow `--tam` koşarsa
    yalnız korpus ölçülür ve üç adım **hiçbir yerde** koşmamış olur.

    Neden bir bayrak aranıyor: bir workflow `kapi.py`'yi **çağırıp** yalnız `--hizli`
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
    if not wf.exists():
        # ⊘ ÖLÇÜLEMEDİ — **kırmızı değil, üçüncü hâl.** Test konteynerine yalnız
        # `backend/` bağlanıyor; depo kökü (dolayısıyla `.github/`) o ortamda YOK.
        # 🔴 `assert` ile kırmızı vermek *"CI kapıları geri alındı"* diye bir YALAN
        # ALARM üretiyordu — ve bu kapının kendi konusu tam da budur: ölçülemeyen bir
        # şeyi ölçülmüş gibi raporlamak.
        # ⚠ Sessizce geçmek de yanlış olurdu: sebep yazılı, komut verili, atlama SAYILIR.
        pytest.skip("⊘ ÖLÇÜLEMEDİ — depo kökü bu ortamda görünmüyor. Kökten koşulmalı: "
                    "`docker run -v \"$PWD:/repo\" -w /repo/backend … pytest "
                    "tests/test_beyanlar_curumesin.py`")
    metinler = {f.name: f.read_text(encoding="utf-8", errors="ignore")
                for f in sorted(wf.glob("*.yml"))}
    kosanlar = {ad: t for ad, t in metinler.items() if "kapi.py" in t}
    assert kosanlar, (
        "Hiçbir workflow `lab/kapi.py` çağırmıyor — FAZ 0.15 GERİ ALINMIŞ.\n"
        "Kapı testi geri alınmaz; gerekçesi buraya yazılır ve satır `xfail` işaretlenir.")
    assert any("--hepsi" in t for t in kosanlar.values()), (
        f"`kapi.py` çağrılıyor ({sorted(kosanlar)}) ama `--hepsi` YOK.\n"
        "🔴 Süit · `eval` · senaryo yerel kapıdan ÇIKARILDI (2026-08-04) — koştukları "
        "TEK yer bu workflow. `--tam` yalnız korpus koşar; burada `--tam` yazmak o üç "
        "adımı HİÇBİR YERDE koşmamak demektir.")
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



def test_TERS_TUZAK_18_YASAK_ENVANTER_AYAKTA():
    """⟳ **TERS TUZAK** — `§5-18.yasak` §0'dan çıktı; bu test onun *"indi"* beyanının
    çürümediğini kanıtlar.

    `⟳` satırı bir **işaretçidir** ve `Durum` hücresi yalnız *"UYGULANMADI"* diyebilir.
    Yasak indiği için satır listede kalamazdı — ama bir beyanı listeden çıkarmak onu
    **korumasız** bırakır. Bu deponun cevabı: *kapananlar işaretlenir, silinmez;*
    tuzak **ters çevrilir**.

    İnen üç şey burada kilitlenir: (1) envanter kapısının kendisi, (2) her dalın
    gerekçeli olması, (3) yasağın **dördüncü koşulunun** yazılı olması — o koşul ölçülmüş
    bir geri almadan doğdu ve kaybı en kolay olan parçadır.
    """
    kapi = pathlib.Path(__file__).resolve().parent / "test_kisa_devre_yok.py"
    assert kapi.exists(), "🔴 kısa devre envanter kapısı SİLİNMİŞ — yasak korumasız kaldı"
    src = kapi.read_text(encoding="utf-8")
    assert "MUAF" in src, "🔴 envanterde gerekçeli muafiyet listesi yok"

    mimari = (APP.parent / "MIMARI.md").read_text(encoding="utf-8")
    assert "dördüncü koşulu" in mimari, (
        "🔴 yasağın DÖRDÜNCÜ KOŞULU (*bir sonraki basamak gerçekten daha yetenekli "
        "olmalı*) `MIMARI.md`'den düşmüş — o koşul ölçülmüş bir geri almadan doğdu "
        "(korpus %95,1→%93,5) ve kaybı en kolay olan parçadır.")
