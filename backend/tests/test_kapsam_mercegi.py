"""FAZ 2.3 — **DEPARTMAN = MERCEK, KÜP DEĞİL** kapısı. [bayrak: `kapsam_mercegi`]

*"Bize bir satış küpü lazım"* isteğinin **meşru karşılığı** bir küp değil bir **kapsam
parametresidir** (Plan 3 §7.8). Bir departmanı küp yapmak, o departmanın **tüm sözlüğünü**
kimliğe yapıştırır — `surdurulebilirlik` felaketinin kökü buydu ve ölçüldü: kimliği
sadeleştirme denemesi erişimi **%64 → %56** düşürdü.
"""

from __future__ import annotations

import pathlib

from app import kapsam as K

KOK = pathlib.Path(__file__).resolve().parents[1]

_SEMA = {"cubes": [
    {"name": "ticaret", "departman": "satis"},
    {"name": "oee", "departman": "uretim"},
    {"name": "cari"},                                   # ataması YOK
]}


# ── 1 · 🔴 MERCEK GÜVENLİK SINIRI DEĞİL ─────────────────────────────────────

def test_MERCEK_HER_ZAMAN_ALT_KUME():
    """🔴 **Maddenin en kritik değişmezi.** Mercek yalnız **daraltır**; hiçbir kapsam,
    mercek kapalıyken görünmeyen bir küpü **görünür yapamaz**. *Merceği bir güvenlik
    katmanı gibi kullanmak, "kapsamı genişlet" düğmesini bir YETKİ YÜKSELTME aracına
    çevirirdi.*"""
    tam = set(K.daralt(_SEMA, "genel", departman=None))
    for k in K.KAPSAMLAR:
        for d in (None, "satis", "uretim", "olmayan"):
            assert set(K.daralt(_SEMA, k, departman=d)) <= tam, (
                f"kapsam={k} departman={d} tam kümeyi GENİŞLETMİŞ — mercek yetki açıyor")


def test_GUVENLIK_SINIRI_OLMADIGI_YAZILI():
    """⚠ Bir sonraki tur bu modülü bir yetki katmanı sanmamalı — sınır **yazılı**."""
    kaynak = (KOK / "app" / "kapsam.py").read_text(encoding="utf-8")
    assert "GÜVENLİK SINIRI DEĞİL" in kaynak and "authorize()" in kaynak


def test_YENI_BASE_OBJECT_DOGURMUYOR():
    """🔴 *"Kapsam parametresi, yeni motor değil."* Dönen şey bir **ad listesidir**;
    hiçbir küp, ifade ya da sayı değişmez."""
    out = K.daralt(_SEMA, "departman", departman="satis")
    assert all(isinstance(x, str) for x in out)
    kaynak = (KOK / "app" / "kapsam.py").read_text(encoding="utf-8")
    for yasak in ("base_object", "CREATE ", "expression"):
        assert yasak not in kaynak.replace("base_object` DOĞURMAZ", "").replace(
            "`base_object` DOĞURMAZ", ""), f"mercek küp ÜRETİYOR olabilir ({yasak!r})"


# ── 2 · ÜÇ SEVİYE ───────────────────────────────────────────────────────────

def test_GENEL_TAM_KATALOG():
    """`genel` = **bugünkü** davranış. Varsayılan bu olmalı: bir görünürlük aracı,
    varsayılanda hiçbir şey gizlememelidir."""
    assert K.VARSAYILAN == "genel"
    assert len(K.daralt(_SEMA, "genel", departman="satis")) == 3


def test_DEPARTMAN_DARALTIYOR():
    out = K.daralt(_SEMA, "departman", departman="satis")
    assert "ticaret" in out and "oee" not in out


def test_ATAMASI_OLMAYAN_KUP_GIZLENMIYOR():
    """🔴 Atanmamışlık bir *"gizle"* kararı **değildir**. Sessizce gizlemek, kullanıcının
    katalogdan **haberi olmamasına** yol açardı — ve o küp bir daha hiç sorulmazdı."""
    assert "cari" in K.daralt(_SEMA, "departman", departman="satis")


def test_GECERSIZ_KAPSAM_VARSAYILANA_DUSUYOR():
    """⚠ Geçersiz kapsamı **hata** yapmak bir yazım hatasını cevapsızlığa çevirirdi;
    *daha geniş* bir kapsama düşürmek ise sessizce daha çok göstermek olurdu."""
    for kotu in ("", None, "departmen", "PORTFOY!"):
        assert K.gecerli(kotu) == "genel"
    assert K.gecerli("PORTFOY") == "portfoy", "büyük harf REDDEDİLMEMELİ"


# ── 3 · `portfoy` YALNIZ ÇOK-TENANT YETKİSİYLE ─────────────────────────────

class _P:
    def __init__(self, sa: bool = False):
        self.is_superadmin = sa


def test_PORTFOY_YETKI_ISTIYOR():
    """🔴 Maddenin ikinci şartı, birebir. Ve bu **tek** yetki kontrolü bir
    **genişletmeyi** engelliyor, bir daraltmayı değil."""
    assert K.izinli_mi("portfoy", _P(False)) is False
    assert K.izinli_mi("portfoy", _P(True)) is True
    assert K.izinli_mi("genel", _P(False)) is True
    assert K.izinli_mi("departman", None) is True


def test_UYDURMA_IZIN_ADI_YOK():
    """🔴 **Kapı beni yakaladı:** ilk yazımda `"tenant:read_all"` diye bir izin
    **uydurmuştum** — matriste öyle bir eylem yok. *Var olmayan bir izne dayanan kontrol,
    hiç yapılmayan bir kontroldür:* `izinli_mi` her zaman `False` döner ve `portfoy`
    **hiç kimseye** açılmazdı. Bu deponun çok-tenant sınırı `is_superadmin`'dir
    (ADR-0015 K7)."""
    kaynak = (KOK / "app" / "kapsam.py").read_text(encoding="utf-8")
    assert "tenant:read_all" not in kaynak.split("uydurmuştum")[-1], "uydurma izin geri gelmiş"
    assert "is_superadmin" in kaynak


# ── 4 · BAYRAK: KAPALIYKEN BUGÜNKÜ DAVRANIŞ ────────────────────────────────

def test_BAYRAK_KAPALIYKEN_UC_DARALTMIYOR():
    """🔴 **GERİ AL:** `kapsam_mercegi=off` → her kullanıcı **bugünkü tam katalogu**
    görür. Kapı, uçtaki bayrak kontrolünün **varlığını** yapısal olarak doğruluyor."""
    # ⚠ **Pencere değil, YAPI** — 2000 karakterlik pencere komşu fonksiyonlara taşıyor
    # ve yanlış yeri ölçüyordu (bu oturumda dokuzuncu kez). Fonksiyonun **kendi** gövdesi
    # AST'ten alınır.
    import ast

    agac = ast.parse((KOK / "app" / "routers" / "query.py").read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "get_schema")
    daralt_satiri = next((n.lineno for n in ast.walk(fn) if isinstance(n, ast.Call)
                          and getattr(n.func, "attr", "") == "daralt"), None)
    bayrak_satiri = next((n.lineno for n in ast.walk(fn) if isinstance(n, ast.Compare)
                          and any(isinstance(o, ast.In) for o in n.ops)
                          and any(isinstance(c, ast.Constant) and c.value == "kapsam_mercegi"
                                  for c in ast.walk(n))), None)
    assert bayrak_satiri is not None, "bayrak kontrolü YOK — geri alınamaz"
    assert daralt_satiri is not None, "daraltma HİÇ çağrılmıyor — mercek ölü"
    assert bayrak_satiri < daralt_satiri, \
        "daraltma bayraktan ÖNCE çalışıyor — kapalı bayrak katalogu değiştirir"


def test_VARSAYILAN_OFF():
    import yaml

    d = yaml.safe_load((KOK / "demo" / "packs" / "features.yml").read_text(encoding="utf-8"))
    bayraklar = d.get("features") or d.get("flags") or d
    assert bayraklar.get("kapsam_mercegi") == "off", (
        "varsayılan `off` değil — bir görünürlük aracı varsayılanda hiçbir şey gizlemez. "
        "⚠ YAML 1.1 çıplak `off`u BOOLEAN okur: tırnak ŞART.")


def test_SCOPE_ASK_REQUESTE_KONMADI():
    """⟳ **Yol haritasından SAPMA — ve gerekçesi ölçüldü.** Yol haritası
    `AskRequest.scope` diyor; merceği **cevaplama yoluna** bağlamak, *aynı sorunun kapsam
    değişince farklı sayı döndürmesi* demekti — bir **görünürlük** tercihini **sonuca**
    karıştırmak. Mercek `/schema`'ya (katalog) bağlandı: kullanıcının **gördüğü küme**
    değişir, **aldığı sayı** değişmez.

    🔴 Ve yetim-alan kapısı bunu doğruladı: alanı `AskRequest`'e koyduğumda hiçbir
    tüketicisi olmadığı için `test_K2b_DIGER_SOZLESMELER_de_taranir` **kırmızı** verdi.
    *Bir sözleşme alanı, tüketicisi olmadan yalnız bir vaattir.*
    """
    from app.schemas import AskRequest

    assert "scope" not in AskRequest.model_fields, (
        "`scope` cevaplama yoluna geri konmuş — aynı soru kapsam değişince farklı sayı "
        "döndürür. Mercek `/schema`'nın parametresidir.")
    kaynak = (KOK / "app" / "schemas.py").read_text(encoding="utf-8")
    assert "GÖRÜNÜRLÜK tercihini SONUCA karıştırmak" in kaynak, "sapmanın GEREKÇESİ yazılı değil"


# ── 5 · K2 · EKRAN: anahtar var, ama KAPALIYKEN HİÇ ÇİZİLMİYOR ────────────

def test_KAPSAM_ANAHTARI_EKRANDA():
    """🔴 **K2 — yetim uç yok.** Bir kapsam parametresi, kullanıcı **seçemiyorsa** yoktur."""
    import pytest

    fe = KOK.parent / "dima-frontend-demo-master" / "src"
    if not fe.exists():
        pytest.skip("frontend bu koşumda mount edilmemiş")
    panel = (fe / "components" / "ChatPanel.tsx").read_text(encoding="utf-8")
    assert "onKapsam" in panel and "departmanım" in panel
    sayfa = (fe / "app" / "page.tsx").read_text(encoding="utf-8")
    assert 'useFeature("kapsam_mercegi")' in sayfa, "bayrak UI'da OKUNMUYOR"


def test_BAYRAK_KAPALIYKEN_ANAHTAR_CIZILMIYOR():
    """⚠ *Bir görünürlük aracı, kapalıyken kullanıcıya var olduğunu bile söylememelidir.*
    `onKapsam` verilmezse anahtar hiç çizilmez — gri bir düğme göstermek, kullanıcıya
    çalışmayan bir şey **teklif** etmek olurdu."""
    import pytest

    fe = KOK.parent / "dima-frontend-demo-master" / "src"
    if not fe.exists():
        pytest.skip("frontend mount edilmemiş")
    sayfa = (fe / "app" / "page.tsx").read_text(encoding="utf-8")
    assert "kapsamAcik ? setKapsam : undefined" in sayfa


def test_UI_YETKI_KARARI_VERMIYOR():
    """`portfoy` yalnız superadmin'e **teklif edilir** — ama sınır backend'de.
    *Görünürlük bir sınır değil, yapamayacağı bir şeyi kullanıcıya teklif etmeme
    nezaketidir.*"""
    import pytest

    fe = KOK.parent / "dima-frontend-demo-master" / "src"
    if not fe.exists():
        pytest.skip("frontend mount edilmemiş")
    panel = (fe / "components" / "ChatPanel.tsx").read_text(encoding="utf-8")
    assert "superadmin" in panel
    assert "nezaket" in panel, "görünürlük ≠ sınır ayrımı YAZILI DEĞİL"


def test_UI_KAPSAMI_GERCEKTEN_GONDERIYOR():
    """🔴 **Anahtar süs olmamalı.** Kullanıcı `departmanım` seçtiğinde istek gerçekten
    `scope` taşımalı — ve React Query **anahtarında** da olmalı, yoksa önbellekten
    **eski katalog** döner ve kullanıcı seçim yapar, hiçbir şey değişmez."""
    import pytest

    fe = KOK.parent / "dima-frontend-demo-master" / "src"
    if not fe.exists():
        pytest.skip("frontend mount edilmemiş")
    api = (fe / "lib" / "api-client.ts").read_text(encoding="utf-8")
    assert "params: { scope }" in api, "`scope` isteğe KONMUYOR — anahtar süs"
    panel = (fe / "components" / "SchemaPanel.tsx").read_text(encoding="utf-8")
    assert 'queryKey: ["schema", kapsam' in panel, \
        "kapsam sorgu ANAHTARINDA değil — önbellek eski katalogu döndürür"
