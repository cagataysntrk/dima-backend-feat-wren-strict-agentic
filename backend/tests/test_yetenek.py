"""🔴 KÖK-6 — **YETENEK BEYANI: üç kutu.** (denetim raporu KN-3)

Ölçülen kusur: *"forecast v1'de yok"* gibi **ürün-düzeyi bir sınır** Discovery'ye düşüyor
ve **bir sayıya** dönüşüyor. Rozet dürüst (`source=llm:*`) — halüsinasyon değil; ama
kullanıcı ilan edilmiş bir sınırın cevabı yerine bir sayı görüyor.

## 🔴 Bu dosyanın en önemli kapısı YANLIŞ-POZİTİF kapısıdır

Bir sınır beyanı **cevaplanabilen bir soruyu asla reddetmemelidir**. Kapı geliştirilirken
gerçek katalogda **968 meşru soru** üretildi ve ölçüm üç kez düzeltildi:

| tur | yanlış-pozitif | kök neden |
|---|---|---|
| 1 | **27** (%6,1) | ölçüt *"iki ölçü ADI"*ydı — `elektrik` tek kelimesi iki cube'da farklı adlarla eşleşiyor |
| 2 | **21** (%4,8) | ölçüt *"iki sinonim METNİ"* oldu ama `«ariza sayisi»` ⊃ `«ariza»` kapsaması görülmüyordu |
| 3 | 🟢 **0** | cube'lar **arasında** da *"en uzun kazanır"* |

*Bir kapı, yakaladıklarıyla değil YANLIŞ yakaladıklarıyla sınanır.*
"""

from __future__ import annotations

import pytest

from app import yetenek
from app.yetenek import KUTU_YAPAMIYORUM, KUTU_YAPMIYORUM, kapsam_disi

#: Paket-şekilli küçük şema — birim testler için. Gerçek şema kapısı ayrıca aşağıda.
SEMA = {"cubes": [
    {"name": "parti", "synonyms": ["parti", "fire"],
     "measures": [{"name": "toplam_fire_kg", "synonyms": ["fire"]},
                  {"name": "toplam_ciro", "synonyms": ["ciro"]}],
     "dimensions": [{"name": "makine"}]},
    {"name": "oee", "synonyms": ["oee"],
     "measures": [{"name": "toplam_fire_kg", "synonyms": ["fire"]}], "dimensions": []},
    {"name": "kalite", "synonyms": ["kalite"],
     "measures": [{"name": "rework_sayisi", "synonyms": ["rework"]}], "dimensions": []},
]}


# ═══════════════════════════════════════════════════════════════════════════════
# ÜÇ KUTU — ve kutuların AYRI olması
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("soru,tur,kutu", [
    ("bu gidişle yılı nerede kapatırız", "forecast", KUTU_YAPMIYORUM),
    ("firesiz partiler kaç tane", "olumsuzluk", KUTU_YAPAMIYORUM),
    ("fire ve rework birlikte", "iki_cube", KUTU_YAPMIYORUM),
])
def test_UC_HEDEF_YAKALANIYOR(soru, tur, kutu):
    """Raporun ölçtüğü üç tur — üçü de bugün **sayı döndürüyordu**."""
    s = kapsam_disi(soru, SEMA)
    assert s is not None, f"🔴 «{soru}» kapıdan kaçtı — Discovery devralır, sayı döner"
    assert (s.tur, s.kutu) == (tur, kutu)


def test_KUTULAR_AYRI_KALIYOR():
    """🔴 *"Yapmıyorum"* bir **karardır**, *"yapamıyorum"* bir **eksikliktir**.

    ⚠ İkisini aynı mesajla vermek kullanıcıya *"bekle, gelecek"* dedirtir — oysa
    forecast **gelmeyecek**. Bir sınırı bir eksiklik gibi sunmak kullanıcının zamanını
    çalar; tersi de doğru: bir eksikliği karar gibi sunmak yol haritasını gizler."""
    assert kapsam_disi("bu gidişle nereye varırız", SEMA).kutu == KUTU_YAPMIYORUM
    assert kapsam_disi("firesiz partiler", SEMA).kutu == KUTU_YAPAMIYORUM


def test_MESAJ_NE_YAPABILECEGINI_DE_SOYLUYOR():
    """*Bir sınır, yalnız "hayır" derse kullanıcıyı yolsuz bırakır.* Rapor bunu
    **proaktif sınır** diye adlandırıyor: reddin yanında **ne yapılabileceği** durmalı."""
    for soru in ("bu gidişle yılı nerede kapatırız", "firesiz partiler kaç tane",
                 "fire ve rework birlikte"):
        m = kapsam_disi(soru, SEMA).mesaj
        assert "Yapabildiğim" in m, f"🔴 «{soru}»: ret var, yol yok"
        assert len(m) > 80


# ═══════════════════════════════════════════════════════════════════════════════
# 🔴 YANLIŞ-POZİTİF — bu dosyanın en önemli kapısı
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("soru", [
    "bu yıl fire",
    "makine bazında fire",
    "geçen ay ciro ne kadar",
    "en yüksek fire hangi makine",
    # 🔴 Tek kavram, iki sahip → BELİRSİZLİK'tir, sınır değil. Doğru cevap netleştirme.
    "makine bazında fire ve oee",
    # 🔴 Tek cube ikisini de taşıyor → soru cevaplanabilir, sınır YOK.
    "fire ve ciro birlikte",
])
def test_CEVAPLANABILIR_SORU_KESILMIYOR(soru):
    """🔴 *Bir sınır beyanı, cevaplanabilen bir soruyu asla reddetmemelidir.*"""
    assert kapsam_disi(soru, SEMA) is None, f"🔴 «{soru}» yanlışlıkla kesildi"


def test_AYNI_KELIME_IKI_TANELILIK_SINIR_DEGIL():
    """🔴 **Ölçülerek bulundu** — 21 yanlış-pozitifin tamamı buydu.

    `«ariza sayisi»` (bakim) ve `«ariza»` (oee) **iki kavram değildir**; aynı kavramın
    iki taneliliğidir. `_match_measure` *"en uzun kazanır"* kuralını cube **içinde**
    uyguluyor ama cube'lar **arasında** kimse uygulamıyordu."""
    sema = {"cubes": [
        {"name": "bakim", "synonyms": ["bakim"],
         "measures": [{"name": "ariza_sayisi", "synonyms": ["ariza sayisi"]}], "dimensions": []},
        {"name": "oee", "synonyms": ["oee"],
         "measures": [{"name": "toplam_durus", "synonyms": ["ariza"]}], "dimensions": []},
    ]}
    assert kapsam_disi("ariza sayisi ve dönem kıyası", sema) is None


def test_BOS_SORU_CAKILMIYOR():
    assert kapsam_disi("", SEMA) is None
    assert kapsam_disi("   ", SEMA) is None


# ═══════════════════════════════════════════════════════════════════════════════
# YAPI — dedektörlerin ikisi YAPISAL olmalı (ADR-0008)
# ═══════════════════════════════════════════════════════════════════════════════

def test_OLUMSUZLUK_TEK_SAHIPTEN():
    """⚠ Olumsuzluk ekleri `cube_router._NEGATION_SUFFIXES`in — **ikinci bir liste yok**.

    *Bu depoda "aynı kuralın iki sahibi" ölçülmüş bir kusur sınıfıdır; bir ek listesini
    kopyalamak onun en sessiz hâli olurdu.*

    🔴 **Bu kapı ilk yazımında KENDİ BELGESİNİ yakaladı** — docstring'deki `firesiz`
    kelimesi `siz` içeriyordu. Bu, deponun **on ikiden fazla** kez ölçtüğü sınıftır:
    *bir metin taraması, tarayanın kendi metnini de tarar.* Çözüm metni daraltmak değil,
    **AST'ye geçmek**: belge bir sözdizim ağacında görünmez.

    ⚠ Ve ders genel: *"kelime var mı"* diye bakan bir kapı, bir **niyeti** değil bir
    **karakter dizisini** ölçer."""
    import ast as _ast
    import inspect

    agac = _ast.parse(inspect.getsource(yetenek))
    assert any(isinstance(n, _ast.Name) and n.id == "_NEGATION_SUFFIXES"
               for n in _ast.walk(agac)), "🔴 ekler tek sahipten alınmıyor"
    # Modülde olumsuzluk eki taşıyan bir DİZİ SABİTİ olmamalı (belge serbest).
    EKLER = {"siz", "suz", "sizl", "suzl", "mayan", "meyen", "maz", "mez"}
    for d in _ast.walk(agac):
        if isinstance(d, (_ast.Tuple, _ast.List, _ast.Set)):
            sabitler = {e.value for e in d.elts
                        if isinstance(e, _ast.Constant) and isinstance(e.value, str)}
            assert not (sabitler & EKLER), \
                f"🔴 olumsuzluk eki elle kopyalanmış: {sorted(sabitler & EKLER)}"


def test_OLUMSUZLUK_GOVDE_KATALOGDA_OLMALI():
    """⚠ Yanlış-pozitif kapanı: ek atılınca kalan gövde **katalogda bilinen bir terim**
    değilse olumsuzluk sayılmaz. Yoksa `-siz` ile biten her kelime kesilirdi."""
    assert kapsam_disi("firesiz partiler", SEMA) is not None      # fire → katalogda
    assert kapsam_disi("kablosuz ağ raporu", SEMA) is None        # kablo → katalogda YOK


def test_NORM_CUBE_ROUTER_ILE_AYNI():
    """🔴 `yetenek._norm` bir **kopyadır** (döngüsel bağımlılık yüzünden zorunlu).
    *Bir kopyayı güvenli yapan şey niyeti değil, kapısıdır* — ikisi aynı çıktıyı vermeli."""
    from app.cube_router import _norm as router_norm

    for s in ("Fire Oranı", "ŞUBAT", "ölçüm", "İŞÇİLİK", "çğıöşü", "ABC 123"):
        assert yetenek._norm(s) == router_norm(s), f"🔴 «{s}» ayrıştı"


def test_KAPI_DISCOVERY_ONUNDE_BAGLI():
    """🔴 **Konum bağlayıcı.** Modülün güvencesi kodunda değil, çağrıldığı yerde:
    `route()` ve Intent-JSON ikisi de pes ettikten SONRA çalışır. Daha erken bir yere
    bağlanırsa cevaplanabilir sorular kesilir."""
    import pathlib

    src = (pathlib.Path(__file__).resolve().parents[1]
           / "app" / "routers" / "ask.py").read_text(encoding="utf-8")
    # ⟳ **ÇAPA KAYDI.** Çağrı artık `_guvenli_kapsam_disi(` sarmalayıcısından geçiyor
    # (iki çağıran, tek `try/except` sözleşmesi — `KAT-1`). Eski çapa `_yetenek.kapsam_disi(`
    # artık **yalnız sarmalayıcının gövdesinde** geçiyor ve o, dosyanın başında duruyor;
    # kapı bu yüzden kırmızı verdi ve **haklıydı**: ölçtüğü şey konum, çapası kaymıştı.
    #
    # 🔴 Kapı GEVŞETİLMEDİ, **genişletildi**: artık `kapsam_disi`'yi çağıran **her yer**
    # Discovery'den önce olmak zorunda. İkinci çağıran (`AJ`/§17.4 — dönem netleştirmesi
    # sınırı **önce** sorar) bu yüzden ayrıca ölçülüyor.
    #
    # *Bir kapının çapası kayınca doğru tepki onu silmek değil, yeniden çakmaktır.*
    i_yol = src.index('_yol_izinli("discovery")')
    i_disc = src.index("def _run_discovery(")
    cagrilar = [m for m in range(len(src))
                if src.startswith("_guvenli_kapsam_disi(", m)
                and not src.startswith("def _guvenli_kapsam_disi(", max(0, m - 4))]
    assert len(cagrilar) >= 2, (
        f"🔴 beklenen iki çağıran (asıl kapı + dönem netleştirmesi) yok: {len(cagrilar)}")
    assert max(cagrilar) < i_disc, (
        "🔴 bir `kapsam_disi` çağrısı Discovery'den SONRA — o dal sınırı hiç duymaz")
    # Asıl kapı hâlâ `_yol_izinli("discovery")`'den sonra: erken bağlanırsa cevaplanabilir
    # sorular kesilir. ⚠ Dönem netleştirmesi ondan ÖNCEdir ve bu **kasıtlıdır** (§17.4).
    assert any(c > i_yol for c in cagrilar), (
        "🔴 asıl kapı Discovery yol izninden önce — cevaplanabilir sorular kesilir")
