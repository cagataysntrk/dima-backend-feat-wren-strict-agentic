"""🔴 `G4` — **İDDİA KAPISI**: `narration_guard`'ın 20 testlik titizliğiyle.

`narration_guard` kendi sınırını itiraf ediyor: *"Sayı İÇERMEYEN cümleler geçer: bu kapı
**sayı uydurmasını** engeller, **üslubu değil**."* Bu dosya o boşluğu kilitler.

⚠ En tehlikeli sınıf **yetenek vaadi**: *"İstersen tedarikçi kırılımı da ekleyebilirim"*
— o boyut yoksa kullanıcı *"olsun"* der ve **sistem çuvallar**. Bir vaat, tutulamadığında
bir kusurdan **daha pahalıdır**: kullanıcı ona göre plan yapar.
"""

from __future__ import annotations

from app.iddia import Rapor, dogrula

_SEMA = {"cubes": [{
    "name": "satis",
    "synonyms": ["satış", "ciro"],
    "measures": [{"name": "toplam_ciro"}],
    "dimensions": [{"name": "sube"}, {"name": "musteri"}],
}]}


# --- GEÇENLER ---------------------------------------------------------------------


def test_duz_olgu_cumlesi_GECER():
    r = dogrula("Mart ayında ciro 1,2 milyon TL oldu.", _SEMA)
    assert r.gecti and r.reddedilen == []


def test_IZINLI_SOZ_EDIMLERI_gecer():
    """Garson bunları serbestçe söyleyebilir: sor · var olanı öner · ne yaptığını
    açıkla · bilmediğini söyle. Hiçbiri şema hakkında bir İDDİA taşımaz."""
    for c in ("Hangi dönem için bakayım?",
              "Bu soruyu anlayamadım.",
              "Anladığım şu: Mart 2026 cirosu.",
              "Bu kapsam dışı — tahmin desteklenmiyor."):
        assert dogrula(c, _SEMA).gecti, c


def test_KATALOGDA_OLAN_vaat_gecer():
    """Vaat, karşılığı **varsa** meşrudur: `sube` katalogda var."""
    r = dogrula("İstersen sube kırılımı da ekleyebilirim.", _SEMA)
    assert r.gecti, r.gerekceler


# --- DÜŞENLER ---------------------------------------------------------------------


def test_YETENEK_VAADI_katalogda_yoksa_DUSER():
    """🔴 Sınıfın en pahalı örneği — ve yol haritasının adıyla andığı vaka."""
    r = dogrula("İstersen tedarikçi kırılımı da ekleyebilirim.", _SEMA)
    assert not r.gecti
    assert "yetenek vaadi" in r.gerekceler[0]
    assert r.temiz_metin == ""


def test_DOGRULANAMAZ_GUVEN_duser():
    """🔴 Sistem kendi doğruluğuna kefil olamaz; kanıt `QueryContract`'tadır.
    ⚠ Bu cümle danışman belgesinin KENDİ örnek çıktısında vardı."""
    r = dogrula("Hesabın doğru olduğundan eminim.", _SEMA)
    assert not r.gecti and "güven" in r.gerekceler[0]


def test_KATALOG_YOKSA_vaat_FAIL_CLOSED():
    """Şüphede cümle düşer. Bir cümle eksik kalmak, tutulamayan bir vaatten UCUZDUR."""
    r = dogrula("İstersen tedarikçi kırılımı da ekleyebilirim.", None)
    assert not r.gecti and "doğrulanamaz" in r.gerekceler[0]


# --- CERRAHİ DAVRANIŞ -------------------------------------------------------------


def test_YALNIZ_SUCLU_CUMLE_duser():
    """🔴 `narration_guard` deseni: metnin tamamı değil, **düşen cümle** düşer.
    Kapı cerrahi olmalıdır ki kullanılabilir kalsın — *kullanılamayan kapı kapatılır
    ve o zaman hiç yoktur.*"""
    metin = ("Mart cirosu 1,2 milyon TL. "
             "İstersen tedarikçi kırılımı da ekleyebilirim. "
             "Şube bazında en yüksek Merkez.")
    r = dogrula(metin, _SEMA)
    assert not r.gecti
    assert len(r.reddedilen) == 1
    assert "Mart cirosu" in r.temiz_metin
    assert "Şube bazında" in r.temiz_metin
    assert "tedarikçi" not in r.temiz_metin


def test_BOS_METIN_gecer():
    assert dogrula("", _SEMA).gecti
    assert dogrula(None, _SEMA).gecti


# --- ÖLÇÜM ------------------------------------------------------------------------


def test_DUSME_ORANI_MAKBUZA_yazilir():
    """🔴 `narration_guard`'ın kendi dersi: kapı agresifse gevşetilir — ama ÖLÇÜYLE,
    sezgiyle değil. Oran görünmezse kapının agresifliği de görünmez."""
    r = dogrula("İstersen tedarikçi kırılımı da ekleyebilirim.", _SEMA)
    m = r.makbuza()
    assert m["dusen_cumle"] == 1
    assert m["gerekceler"] and isinstance(m["gerekceler"][0], str)


def test_RAPOR_SEKLI_narration_guard_ILE_AYNI():
    """Çağıran iki kapıyı **aynı biçimde** okumalı — iki farklı rapor şekli, iki farklı
    tüketici kodu demekti."""
    from app.narration_guard import Rapor as NRapor

    ortak = {"gecti", "temiz_metin", "reddedilen"}
    assert ortak <= set(Rapor.__dataclass_fields__)
    assert ortak <= set(NRapor.__dataclass_fields__)


# --- BEDAVA DENETİM ---------------------------------------------------------------


def test_DETERMINISTIK_METINLER_de_gecer():
    """🔴 Kapı deterministik metinlerde de koşar; orada bir cümle düşerse
    **deterministik yolda bir kusur var demektir** — ücretsiz bir denetim."""
    from app.soz import KATALOG

    for kayit in KATALOG.values():
        metin = str(kayit.get("metin") or "").replace("{ne}", "Mart cirosu")
        r = dogrula(metin, _SEMA)
        assert r.gecti, f"deterministik metin iddia kapısından düştü: {metin!r} → {r.gerekceler}"


# --- SINIR ------------------------------------------------------------------------


def test_IKINCI_DOGRULAMA_MIMARISI_YOK():
    """🔴 `narration_guard` deseniyle BİREBİR — ikinci bir mimari icat edilmez.
    Cümle ayırma disiplini bile aynı olmalı: iki farklı cümle tanımı, iki farklı kapı
    davranışı demekti."""
    import pathlib
    kok = pathlib.Path(__file__).resolve().parents[1] / "app"
    i = (kok / "iddia.py").read_text(encoding="utf-8")
    n = (kok / "narration_guard.py").read_text(encoding="utf-8")
    assert "from app.narration_guard import _CUMLE_RE" in i, (
        "iddia.py cümle ayırıcısını KOPYALAMIŞ — ödünç almalı. İlk sürüm tam bunu yaptı "
        "ve yazdığı desen sahibininkinden FARKLIYDI (üç nokta ve '1. madde' koruması "
        "eksikti). Fark SESSİZ olurdu.")
    assert "_CUMLE_RE = re.compile" in n, "cümle ayırıcısının sahibi narration_guard olmalı"
    assert "_CUMLE_RE = re.compile" not in i, "iddia.py ikinci bir sahip yaratmış"


# --- 🔴 CANLI KAPI BULDU — kapının şemaya GERÇEKTEN ulaştığı ------------------------


def test_ANLATI_YOLUNDA_SEMA_GERCEKTEN_OKUNUYOR():
    """🔴 `lab/garson.py --live` bunu buldu: `_anlati_ekle` içinde `wren_for_request`
    **import edilmemişti** → her turda `NameError` → `except Exception` onu **yuttu** →
    kapı sessizce **şemasız** koştu ve her yetenek vaadi *"katalog yok"* diye düştü.

    Hiçbir birim testi göremezdi: hepsi `dogrula()`'yı doğrudan şemayla çağırıyor.
    Süit de göremezdi: `t2_anlatici` kapalıyken bu dal hiç koşmuyor.

    *Bir `except Exception`, kapsadığı kodun yazılmamış olmasını da başarıyla gizler.*
    """
    import ast
    import pathlib

    kaynak = (pathlib.Path(__file__).resolve().parents[1]
              / "app/answer.py").read_text(encoding="utf-8")
    agac = ast.parse(kaynak)
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "_anlati_ekle")
    yerel_import = any(
        isinstance(n, ast.ImportFrom) and n.module == "app.company_registry"
        and any(a.name == "wren_for_request" for a in n.names)
        for n in ast.walk(fn))
    assert yerel_import, (
        "🔴 `_anlati_ekle` `wren_for_request`'i yerel import ETMİYOR. Bu modülde o ad "
        "modül düzeyinde YOK (`answer.py:248` notu: «HER YERDE yerel olarak alınıyor»); "
        "import olmadan `NameError` doğar ve `except Exception` onu sessizce yutar — "
        "iddia kapısı şemasız koşar, her yetenek vaadi haksız yere düşer.")
