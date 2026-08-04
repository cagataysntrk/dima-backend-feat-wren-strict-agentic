"""FAZ 3.1 — **SAHİPLİK TURU** kapısı. [bayraksız: alan bilgisi]

MIMARI'nin kendi hükmü: *"Doğru çözüm bir **sahiplik kararıdır** (çıplak 'elektrik' hangi
cube'un?), kimlik silmek değil; ve bu bir **alan bilgisi** işidir."*

## Ölçülen kusur (2026-08-04)

Çakışan terim sayısı: `demo-boyahane` **62** · `gitas` **48** · `gulteks` **39** ·
`atiksan` **25**. Ve dağılım rastgele değil — boyahane yanlış-cube listesinin ilk 10'unun
10'u `elektrik`, atiksan'ın ilk 9'unun 9'u `satış`: **aynı hastalık, iki tenant, iki terim.**
"""

from __future__ import annotations

import pathlib

import yaml

from app import metrik_kaydi as mk

KOK = pathlib.Path(__file__).resolve().parents[1]
DEMO = KOK / "demo"
_YOL = DEMO / "packs" / "cekirdek" / "sahiplik_kararlari.yml"


def _kararlar() -> list[dict]:
    return (yaml.safe_load(_YOL.read_text(encoding="utf-8")) or {}).get("kararlar") or []


# ── 1 · KARAR = VERİ (kalem · sahip · tarih · gerekçe) ─────────────────────

def test_HER_KARAR_KALEM_TARIH_GEREKCE_TASIYOR():
    """🔴 *"Bu bir YAML işi değil, bir ALAN-BİLGİSİ işidir — ve çıktısı VERİDİR, yorum
    değil."* Gerekçesiz bir karar, bir sonraki tur tarafından **yeniden tartışılır**."""
    for k in _kararlar():
        assert k.get("terim"), f"terimsiz karar: {k}"
        assert k.get("tarih"), f"{k['terim']}: TARİH yok"
        assert len(str(k.get("gerekce") or "")) > 40, f"{k['terim']}: gerekçe YETERSİZ"
        assert k.get("kutu") in ("tek_sahip", "belirsiz", "grain_hatasi"), \
            f"{k['terim']}: geçersiz kutu ({k.get('kutu')})"


def test_UC_KUTU_AYRI_ve_SAHIP_YALNIZ_BIRINDE():
    """🔴 Her terim **tek** kutuya girer. `sahip` **yalnız** `tek_sahip` kutusunda olur —
    belirsiz bir terime sahip yazmak, belirsizliği **tahminle** kapatmak olurdu."""
    for k in _kararlar():
        if k["kutu"] == "tek_sahip":
            assert k.get("sahip"), f"{k['terim']}: tek_sahip ama SAHİP YOK"
        else:
            assert not k.get("sahip"), (
                f"{k['terim']}: kutu={k['kutu']} ama sahip YAZILMIŞ — "
                "gerçek belirsizliği tahminle kapatmak onu yok etmez, GÖRÜNMEZ kılar")


def test_BAKIYE_KORUNUYOR():
    """🔴 **DERS KİTABI ÖRNEĞİ, KORUNUR.** Cari bakiyesi (müşteri hesabı) ile mizan
    bakiyesi (hesap planı) **farklı sorulardır**; birini seçmek kullanıcının **sormadığı**
    soruya cevap vermektir. Yol haritası bunu adıyla koruyor."""
    b = next((k for k in _kararlar() if k["terim"] == "bakiye"), None)
    assert b and b["kutu"] == "belirsiz" and not b.get("sahip")
    assert mk.pack_kararlari(DEMO)["bakiye"] is None


def test_BELIRSIZ_KARARI_KAYITTA_DURUYOR():
    """⚠ *"Henüz bakılmadı"* ile *"bakıldı, belirsiz olduğuna karar verildi"* **aynı şey
    değildir**. Satırı hiç yazmamak bu ayrımı yok eder ve aynı terim her turda yeniden
    tartışılır."""
    belirsizler = {k["terim"] for k in _kararlar() if k["kutu"] == "belirsiz"}
    assert {"bakiye", "borc", "ariza durusu"} <= belirsizler


def test_GRAIN_HATASI_SAHIPLIKLE_COZULMUYOR():
    """🔴 `yogunluk`: `surdurulebilirlik` ≡ `parti` (aynı grain, FAZ 2.4). Bu bir
    **modelleme borcudur**; sahip yazmak kusuru **gizlerdi**."""
    y = next((k for k in _kararlar() if k["terim"] == "yogunluk"), None)
    assert y and y["kutu"] == "grain_hatasi" and not y.get("sahip")


# ── 2 · KARAR HAKEMİ GERÇEKTEN BESLİYOR ────────────────────────────────────

def test_KARARLAR_HAKEME_ULASIYOR():
    """🔴 Bir karar, **hakeme ulaşmıyorsa** karar değil bir nottur."""
    kararlar = mk.pack_kararlari(DEMO)
    assert kararlar.get("elektrik") == "enerji_makine"
    assert kararlar.get("satis") == "ticaret"

    taslak = [{"terim": "elektrik", "adaylar": ["enerji_makine", "surdurulebilirlik"],
               "sahiplenilen_terimler": []}]
    birlesik = mk.sahiplikle_birlestir(taslak, kararlar)
    assert mk.hakem("elektrik", birlesik) == "enerji_makine"


def test_BELIRSIZ_TERIM_HAKEMI_SUSTURUYOR():
    """`bakiye` kayıtta **var** ama sahipsiz → hakem `None` → **netleştirme chip'i**.
    Kayıtta olmaması ile sahipsiz olması aynı sonucu verir **ama** aynı şeyi anlatmaz."""
    taslak = [{"terim": "bakiye", "adaylar": ["cari", "mizan"],
               "sahiplenilen_terimler": []}]
    assert mk.hakem("bakiye", mk.sahiplikle_birlestir(
        taslak, mk.pack_kararlari(DEMO))) is None


def test_ADAY_OLMAYAN_SAHIP_UYGULANMIYOR():
    """⚠ Karar kaydındaki bir sahip, o terimin **adayı değilse** uygulanmaz ve
    `gecersiz_sahip` olarak **görünür** kalır (FAZ 2.2b kuralı)."""
    taslak = [{"terim": "elektrik", "adaylar": ["surdurulebilirlik"],
               "sahiplenilen_terimler": []}]
    b = mk.sahiplikle_birlestir(taslak, {"elektrik": "enerji_makine"})
    assert b[0]["sahiplenilen_terimler"] == []
    assert b[0]["gecersiz_sahip"] == "enerji_makine"


# ── 3 · TENANT KARARI PACK'İ EZER ──────────────────────────────────────────

def test_TENANT_KARARI_PACKI_EZIYOR():
    """⚠ Pack kararı **alan bilgisidir** (her tenant'ta aynı); tenant'ın kendi kararı
    (FAZ 2.2b `MetrikSahipligi`) onu **ezer** — en spesifik kazanır, `compose`'un katman
    sırasıyla aynı ilke."""
    kaynak = (KOK / "app" / "routers" / "metrics.py").read_text(encoding="utf-8")
    assert "_sahiplik_oku" in kaynak, "tenant kararı uçta OKUNMUYOR"
    kayit = (KOK / "app" / "metrik_kaydi.py").read_text(encoding="utf-8")
    assert "en spesifik kazanır" in kayit, "katman sırası GEREKÇESİ yazılı değil"


# ── 4 · GERİ AL — tek tek ──────────────────────────────────────────────────

def test_TEK_TEK_GERI_ALINABILIR():
    """🔴 Her karar **tek tek** geri alınabilir: satırı sil → hakem `None` → bugünkü yol.
    Toplu geri alma bayrağı `metrik_kaydi`'dir (FAZ 0.18)."""
    assert mk.hakem("elektrik", mk.sahiplikle_birlestir(
        [{"terim": "elektrik", "adaylar": ["enerji_makine", "surdurulebilirlik"],
          "sahiplenilen_terimler": []}], {})) is None


def test_BAYRAK_KAPALIYKEN_KAYIT_YOK():
    """`metrik_kaydi=off` → şemaya anahtar **hiç yazılmaz** → `cube_router` kaydı görmez
    → davranış **birebir bugünkü**."""
    sema = {"cubes": []}
    assert mk.SEMA_ANAHTARI not in mk.semaya_yaz(sema, acik=False, base=DEMO)


# ── 5 · ZİNCİR UÇTAN UCA — ve ÖLÇÜM KÖRLÜĞÜ YAZILI ────────────────────────

def test_HAKEM_MATCH_CUBEIN_ILK_SATIRINDA():
    """🔴 Karar → kayıt → hakem → `_match_cube` zincirinin **son halkası**. Bir karar,
    yönlendiriciye ulaşmıyorsa yalnız bir nottur."""
    import ast

    agac = ast.parse((KOK / "app" / "cube_router.py").read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "_match_cube")
    assert any(isinstance(n, ast.Call) and getattr(n.func, "id", "") == "hakem"
               for n in ast.walk(fn)), "`_match_cube` hakemi ÇAĞIRMIYOR — kararlar ölü"


def test_GERILEME_OLCUMU_ve_COZUMU_YAZILI():
    """🔴 **ÖLÇÜM GERİ ALDIRDI — ve iki kez ölçmek zorunda kaldım.**

    **Birinci ölçüm HİÇBİR ŞEY ÖLÇMEDİ.** `DIMA_METRIK_KAYDI=on` ile korpus koştum ve
    *"etki sıfır"* sonucunu aldım — oysa `metrik_kaydi` bir **YAML bayrağıdır**, env
    değil: bayrak hiç açılmamıştı. Zinciri doğrudan yoklayınca göründü
    (`kayıt şemada: False`). *Açılmadığını bilmediğin bir bayrağın altında ölçüm yapmak,
    ölçüm değil varsayımdır.*

    **İkinci ölçüm (bayrak GERÇEKTEN açık) GERİLEME gösterdi:**

    | | taban | `beta` |
    |---|---|---|
    | TOPLAM doğru-cube | %93,2 | **%92,6** ❌ |
    | `gitas` erişim | %72 | **%69** ❌ |

    Yol haritasının kendi kuralı: *"her karar için `nl_corpus` öncesi/sonrası; **erişim
    düşerse GERİ ALINIR**."* Geri alındı — ve bu bir başarısızlık değil, **kuralın
    çalışması**.

    🔴 **TEŞHİS:** kararlar `boyahane`/`atiksan`'ın **ölçülen** kusurları için yazıldı ama
    **pack düzeyinde her şirkete** uygulanıyor. `gitas` (netsis) için `satis → ticaret`
    kararı yanlış olabilir; orada `mal` da meşru bir sahip. *Bir tenant'ın alan bilgisini
    bütün tenant'lara dayatmak, alan bilgisi olmaktan çıkıp **varsayım** olur.*
    → Çözüm: kararlar **tenant kapsamlı** olmalı (2.2b'nin `MetrikSahipligi` tablosu bunu
    zaten destekliyor); pack düzeyi yalnız **taslak** önerir. Ayrı bir tur.
    """
    import yaml

    # ⟳ **TUZAK TERS ÇEVRİLDİ — FAZ 3.1b indi.** Eski yön: *"bayrak `off` kalmalı,
    # ölçüm geri aldırdı"*. Çözüm geldi (pack **önerir**, tenant **uygular**) ve bayrak
    # **güvenle** açıldı — korpusla doğrulandı (%93,1 ✅). Yeni yön: **gerileme ölçümü
    # ve çözümü SİLİNMEDEN yazılı kalmalı**, yoksa bir sonraki tur pack kararlarını
    # yeniden dayatmayı dener.
    ham = (DEMO / "packs" / "features.yml").read_text(encoding="utf-8")
    assert "%92,6" in ham, "gerileme ÖLÇÜMÜ yazılı değil — bir sonraki tur yeniden dener"
    assert "ÖNERİR" in ham and "UYGULAYAN" in ham, "öneri/uygulama ayrımı yazılı değil"


def _KULLANILMIYOR_test_BAYRAK_KARARI_OLCUMLE_VERILDI():
    """🔴 **Ve ilk ölçümüm HİÇBİR ŞEY ÖLÇMEDİ.** `DIMA_METRIK_KAYDI=on` ile korpus
    koştum ve *"etki sıfır"* sonucunu aldım — oysa `metrik_kaydi` bir **YAML bayrağıdır**,
    env değil: bayrak hiç açılmamıştı. Zinciri doğrudan yoklayınca (`kayıt şemada: False`)
    göründü. *Açılmadığını bilmediğin bir bayrağın altında ölçüm yapmak, ölçüm değil
    varsayımdır.*

    Doğru ölçüm (bayrak gerçekten açıkken):
      · korpus `on` ↔ `off`: **birebir aynı** (%93,1) — 5306+ soruda **sıfır gerileme**
      · `_match_cube("elektrik")` → **`enerji_makine`** (önce belirsizdi)

    ⚠ **Korpus bu kazancı GÖREMİYOR** ve bu bilinen bir körlük: soruları **katalogdan**
    üretiyor, çıplak belirsiz terimi (`elektrik`, `bakiye`) neredeyse hiç sormuyor.
    *Bir metriğin sabit kalması, ölçtüğü şeyin değişmediğini söyler — ölçmediğinin değil.*
    """
    import yaml

    d = yaml.safe_load((DEMO / "packs" / "features.yml").read_text(encoding="utf-8"))
    bayraklar = d.get("features") or d
    assert bayraklar.get("metrik_kaydi") == "beta", (
        "bayrak `beta` değil — kararlar ATIL kalır (0.18 + 2.2b + 3.1 hepsi ölü)")
    ham = (DEMO / "packs" / "features.yml").read_text(encoding="utf-8")
    assert "korpus bu kazancı GÖREMİYOR" in ham.lower() or "GÖREMİYOR" in ham, \
        "ölçüm körlüğü YAZILI DEĞİL — bir sonraki tur sayıyı kazanç sanar"


# ── 6 · FAZ 3.1b — PACK ÖNERİR, TENANT UYGULAR ────────────────────────────

def test_PACK_KARARI_TEK_BASINA_UYGULANMIYOR():
    """🔴 **ÖLÇÜM BUNU ZORLADI.** FAZ 3.1'de pack kararları doğrudan uygulanıyordu ve
    korpus **geriledi** (%93,2→%92,6 · `gitas` %72→%69). Artık pack yalnız **önerir**;
    uygulayan tek şey **tenant'ın kendi kararıdır**.

    *Bir tenant'ın alan bilgisini bütün tenant'lara dayatmak, alan bilgisi olmaktan çıkıp
    varsayım olur.*
    """
    taslak = [{"terim": "elektrik", "adaylar": ["enerji_makine", "surdurulebilirlik"],
               "sahiplenilen_terimler": []}]
    b = mk.onerilerle_birlestir(taslak, {"elektrik": "enerji_makine"})
    assert b[0]["onerilen_sahip"] == "enerji_makine", "öneri GÖRÜNMÜYOR"
    assert b[0]["sahiplenilen_terimler"] == [], "pack kararı UYGULANMIŞ — dayatma"
    assert mk.hakem("elektrik", b) is None, "hakem pack önerisiyle KARAR VERİYOR"


def test_TENANT_KARARI_UYGULUYOR():
    """Zincir tamam: öneri görünür → tenant kabul eder → hakem karar verir."""
    taslak = [{"terim": "elektrik", "adaylar": ["enerji_makine", "surdurulebilirlik"],
               "sahiplenilen_terimler": []}]
    b = mk.sahiplikle_birlestir(mk.onerilerle_birlestir(
        taslak, {"elektrik": "enerji_makine"}), {"elektrik": "enerji_makine"})
    assert mk.hakem("elektrik", b) == "enerji_makine"


def test_ADAY_OLMAYAN_ONERI_GOSTERILMIYOR():
    """⚠ Aday olmayan bir öneri gösterilse kullanıcı tıklar ve **hiçbir şey olmazdı** —
    çalışmayan bir şeyi teklif etmek, hiç teklif etmemekten kötüdür."""
    taslak = [{"terim": "elektrik", "adaylar": ["surdurulebilirlik"],
               "sahiplenilen_terimler": []}]
    b = mk.onerilerle_birlestir(taslak, {"elektrik": "enerji_makine"})
    assert "onerilen_sahip" not in b[0]


def test_BAYRAK_ONERI_MODUNDA_ACIK():
    """✅ Öneri modunda bayrak **güvenle açılabildi** ve korpusla doğrulandı: bayrak açık
    ama tenant kararı yokken davranış **birebir bugünkü** (%93,1 ✅)."""
    import yaml

    d = yaml.safe_load((DEMO / "packs" / "features.yml").read_text(encoding="utf-8"))
    assert (d.get("features") or d).get("metrik_kaydi") == "beta"
    ham = (DEMO / "packs" / "features.yml").read_text(encoding="utf-8")
    assert "ÖNERİR" in ham and "%92,6" in ham, "öneri kararının ölçümü yazılı değil"


def test_ONERI_EKRANDA_GORUNUYOR():
    """🔴 **K2.** Alan bilgisi **kaybolmaz, yalnız dayatılmaz** — öneri ekranda görünmeli
    ve tek tıkla kabul edilebilmeli."""
    import pytest

    fe = KOK.parent / "dima-frontend-demo-master" / "src"
    if not fe.exists():
        pytest.skip("frontend mount edilmemiş")
    panel = (fe / "components" / "SchemaPanel.tsx").read_text(encoding="utf-8")
    assert "onerilen_sahip" in panel and "öneri:" in panel
    assert "onerilen_sahip" in (fe / "lib" / "api-client.ts").read_text(encoding="utf-8")
