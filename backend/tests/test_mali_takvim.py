"""FAZ 2.6 — **MALİ TAKVİM** kapısı. *"Bu yıl"* her şirkette Ocak'ta başlamaz.

🔴 **BAYRAKSIZ, çünkü ölçülen şey bir SESSİZ-YANLIŞ:** `"bu yıl"` takvim yılı
varsayılıyordu (`today.replace(month=1, day=1)`) ve mali yılı Nisan'da başlayan bir
müşteride cevap **yanlış** ama rozet `◆ CUBE`, güven `1.0`, makbuz **tam**.
*Sessiz-yanlışın tanımı budur: sistem emin, sayı yanlış.* Bir bayrağın arkasına koymak,
yanlışı **varsayılan** yapmak olurdu.
"""

from __future__ import annotations

import ast
import pathlib
from datetime import date

import pytest

from app import mali_takvim as mt

KOK = pathlib.Path(__file__).resolve().parents[1]


# ── 1 · PENCERE MATEMATİĞİ ──────────────────────────────────────────────────

def test_TAKVIM_YILI_DAVRANISI_DEGISMIYOR():
    """Varsayılan `1` — yapılandırılmamış her tenant **bugünkü** davranışı görür.
    Bir düzeltme, düzeltmediği kurulumları **değiştirmemelidir**."""
    assert mt.VARSAYILAN_BASLANGIC_AY == 1
    assert mt.yil_penceresi(date(2026, 2, 10)) == (date(2026, 1, 1), date(2026, 12, 31))


def test_NISAN_BASLANGICLI_SIRKET():
    """🔴 **Maddenin kapısı, birebir.** `2026-02-10`: takvim yılı değişti ama **mali yıl
    değişmedi** — pencere hâlâ `2025-04-01 → 2026-03-31`."""
    assert mt.yil_penceresi(date(2026, 2, 10), baslangic_ay=4) == (
        date(2025, 4, 1), date(2026, 3, 31))
    assert mt.yil_basi(date(2026, 2, 10), 4) == date(2025, 4, 1)
    # Mali yıl başladıktan SONRA aynı takvim yılına oturur.
    assert mt.yil_basi(date(2026, 5, 10), 4) == date(2026, 4, 1)


def test_GECEN_MALI_YIL():
    """🔴 `12-31` sabiti yazmak, Ocak'ta başlamayan bir mali yılda pencereyi bir çeyrek
    **kaydırırdı** — ve kimse fark etmezdi."""
    assert mt.yil_penceresi(date(2026, 2, 10), kac_yil_once=1, baslangic_ay=4) == (
        date(2024, 4, 1), date(2025, 3, 31))


@pytest.mark.parametrize("ay", [0, 13, -1, None, "nisan"])
def test_GECERSIZ_AY_TAKVIME_DUSUYOR(ay):
    """⚠ Bir yapılandırma hatası yüzünden *"bu yıl"* sorusunu **cevapsız** bırakmak,
    kullanıcının yanlışını sistemin arızasına çevirirdi."""
    assert mt.yil_basi(date(2026, 2, 10), ay) == date(2026, 1, 1)


def test_ARTIK_YIL_SINIRINDA_DOGRU():
    """Şubat'ta başlayan bir mali yıl, artık yılda da doğru kapanmalı: bitiş **bir sonraki
    başlangıçtan bir gün önce**, sabit bir gün sayısı değil."""
    assert mt.yil_penceresi(date(2024, 6, 1), baslangic_ay=2) == (
        date(2024, 2, 1), date(2025, 1, 31))


# ── 2 · TEK SAHİP — iki kopya kusurun DOĞUŞ biçimiydi ───────────────────────

def test_TAKVIM_YILI_SABITLERI_KALDIRILDI():
    """🔴 Aynı hesabın **iki kopyası** vardı (`cube_router` + `yoy`) ve ikisi de takvim
    yılı varsayıyordu. *Bir kuralın iki sahibi, o kuralın iki kez yanlış olmasıdır.*"""
    # ⚠ **METİN DEĞİL YAPI** — ve bu bir düzeltme: ilk sürüm `f"{date.today().year}-01-01"`
    # dizisini arıyordu ve onu **kendi açıklama yorumumun içinde** buldu. Bu oturumda
    # SEKİZİNCİ kez aynı sınıf: *belgeyi tarayan bir kapı, hatayı ANLATMAYI cezalandırır.*
    def _cagriliyor(yol: str) -> bool:
        agac = ast.parse((KOK / "app" / yol).read_text(encoding="utf-8"))
        return any(isinstance(n, ast.Attribute) and n.attr in ("yil_basi", "yil_penceresi")
                   and getattr(n.value, "id", "") == "mali_takvim"
                   for n in ast.walk(agac))

    assert _cagriliyor("cube_router.py"), "router mali takvimi ÇAĞIRMIYOR"
    assert _cagriliyor("yoy.py"), "`yoy` mali takvimi ÇAĞIRMIYOR"
    # Ve eski sabitler KOD'da yok — yorumlar hariç (docstring/yorum AST'de yoktur).
    for yol in ("cube_router.py", "yoy.py"):
        kod = ast.unparse(ast.parse((KOK / "app" / yol).read_text(encoding="utf-8")))
        assert "replace(month=1, day=1)" not in kod, f"{yol}: takvim-yılı sabiti KODDA"
        assert "-01-01" not in kod or "yil_basi" in kod, f"{yol}: yıl sabiti KODDA"


def test_YENI_MEKANIZMA_ICAT_EDILMEDI():
    """⚠ ContextVar bu depoda **iki kez** kanıtlanmış bir kalıp (`llm._llm_usage_var`,
    `cube_router._reddi_var`). Üçüncüsü **aynı** kalıp; imzalar sabit kaldı."""
    kaynak = (KOK / "app" / "mali_takvim.py").read_text(encoding="utf-8")
    assert "contextvars.ContextVar" in kaynak
    agac = ast.parse((KOK / "app" / "cube_router.py").read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "date_filters")
    assert [a.arg for a in fn.args.args] == ["q", "time_dim"], \
        "`date_filters` imzası DEĞİŞMİŞ — beş çağıran kırılırdı"


def test_HER_YOL_AYARI_GORUYOR():
    """🔴 Ayar `wren_for_request`'te kurulur: veriye giden **her** yolun geçtiği tek nokta.
    Başka bir yere koymak, bazı yolların onu **görmemesi** ve sessizce takvim yılına
    düşmesi demekti — yani tam olarak kapatılan kusura."""
    kaynak = (KOK / "app" / "company_registry.py").read_text(encoding="utf-8")
    i = kaynak.index("def wren_for_request")
    assert "mali_takvim.kur(" in kaynak[i:i + 700]


def test_TENANT_AYARI_VAR():
    from control_plane.models import TenantConfig

    alan = TenantConfig.model_fields["mali_yil_baslangic_ay"]
    assert alan.default == 1, "varsayılan takvim yılı DEĞİL — mevcut kurulumlar kayardı"


# ── 3 · KULLANICI PENCEREYİ GÖRÜYOR ─────────────────────────────────────────

def test_TAKVIMDEN_FARKLIYSA_ETIKET_VAR():
    """🔴 *Takvim yılından farklı bir pencereyi "bu yıl" diye sunmak, doğru sayıyı yanlış
    soruya cevap yapar.* Kullanıcı hangi pencereyi gördüğünü bilmeli."""
    assert mt.etiket(date(2026, 2, 10), 4) == "mali yıl: 2025-04-01 → 2026-03-31"


def test_TAKVIMLE_AYNIYSA_ETIKET_YOK():
    """⚠ Gürültü üretmez: takvim yılıyla aynıysa söylenecek bir şey **yoktur**."""
    assert mt.etiket(date(2026, 2, 10), 1) == ""


# ── 4 · §C/3 KESİŞİMİ — netleştirme oranı DEĞİŞMEZ ─────────────────────────

def test_NETLESTIRME_ORANINA_DOKUNMUYOR():
    """🔴 Yol haritasının açık uyarısı: bu madde dönem **çözümünü** değiştirir,
    **netleştirme oranını değil**. `CLARIFY:dönem` payı korpusta sabit kalmalı.

    Yapısal kanıt: değişen tek şey `start`/`end` **değerleridir**; hangi soruların
    netleştirmeye gittiği (`_current_period_filter`'ın `return None` dalı) **aynı**.
    """
    # ⚠ Pencere-tabanlı metin taraması DEĞİL: `_current_period_filter`'ın **kendi**
    # gövdesi AST'ten alınır, komşu fonksiyonun çağrıları karışmasın.
    agac = ast.parse((KOK / "app" / "cube_router.py").read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "_current_period_filter")
    assert any(isinstance(n, ast.Return) and n.value is None
               or (isinstance(n, ast.Return) and isinstance(n.value, ast.Constant)
                   and n.value.value is None)
               for n in ast.walk(fn)), "netleştirmeye giden `return None` dalı KALDIRILMIŞ"
    cagri = [n for n in ast.walk(fn) if isinstance(n, ast.Attribute)
             and getattr(n.value, "id", "") == "mali_takvim"]
    assert len(cagri) == 1, (
        f"mali takvim bu fonksiyonda {len(cagri)} kez geçiyor — dönem ÇÖZÜMÜ dışına "
        "(netleştirme kararına) karışmış olabilir")


# ── 5 · K2 · YETİM ALAN YOK — kullanıcı pencereyi EKRANDA görüyor ──────────

def test_MALI_DONEM_HER_YANITTA_ve_SEAL_DE():
    """`seal()` **her yanıtın** geçtiği kapanıştır; başka bir yere koymak onu **bazı**
    yanıtlarda eksik bırakırdı (`1.12`'nin aynı gerekçesi)."""
    from app.schemas import AskResponse

    assert AskResponse(question="x").mali_donem is None, "varsayılan DOLU — gürültü"
    agac = ast.parse((KOK / "app" / "answer.py").read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "seal")
    hedefler = {getattr(t, "attr", "") for n in ast.walk(fn)
                if isinstance(n, ast.Assign) for t in n.targets}
    assert "mali_donem" in hedefler


def test_EKRANDA_GORUNUYOR():
    """🔴 **K2 — yetim alan yok.** *"Bu yıl"* dediğinde Nisan–Mart penceresi gelen bir
    kullanıcı, hangi pencereyi gördüğünü **bilmeli**; doğru sayı, yanlış soruya cevap
    olabilir."""
    fe = KOK.parent / "dima-frontend-demo-master" / "src"
    if not fe.exists():
        pytest.skip("frontend bu koşumda mount edilmemiş")
    kart = (fe / "components" / "ReportCard.tsx").read_text(encoding="utf-8")
    assert "mali_donem" in kart, "mali dönem hiçbir yerde GÖSTERİLMİYOR"
    assert "mali_donem" in (fe / "lib" / "types.ts").read_text(encoding="utf-8")
    # ⚠ Frontend kendi pencere hesabını YAPMAMALI — ikinci sahip ayrışırdı.
    for sizinti in ("baslangic_ay", "getMonth()", "fiscal"):
        assert sizinti not in kart, f"pencere hesabı UI'a KOPYALANMIŞ ({sizinti!r})"
