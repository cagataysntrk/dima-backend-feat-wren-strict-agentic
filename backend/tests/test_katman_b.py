"""FAZ 1.3b — **Katman B: model allowlist** kapısı.

Ölçülen kusur iki katlıydı: `enforce_query` bir **stub**'dı (gövde tek satır `return`)
**ve çağıranı yoktu**. Yani ADR-0014 Karar 5'in beyan ettiği katman ne iş yapıyordu ne de
bağlıydı — *"beyan var, kod onu tanımıyor"* sınıfının güvenlik katmanındaki hâli.
"""

from __future__ import annotations

import pathlib
import re

import pytest

from app import katman_b

KOK = pathlib.Path(__file__).resolve().parents[1]


# ── 1 · KARAR (saf fonksiyon) ────────────────────────────────────────────────

def test_YAPILANDIRILMAMIS_ile_BOS_ALLOWLIST_AYNI_DEGIL():
    """🔴 **Bu maddenin kalbi.**

    Yol haritası *"boş allowlist artık «geçer» DEMEZ"* diyor ve **yön doğru**. Ama
    ölçüldü: `ModelPermission` **her tenant'ta boş**. Harfi harfine uygulanırsa **her
    sorgu reddedilir** — bir güvenlik katmanı adına **tam kesinti**.

    Ayrım kurtarıyor:
    * `None` → tenant'ta hiç satır yok → Katman B **kurulmamış** → Katman A yönetir.
    * `set()` → allowlist **aktif** ama boş → **hiçbir modele** izin yok.

    İkisini aynı değere indirgemek ya tüm sistemi kapatır ya katmanı **sonsuza dek** açık
    bırakır — ve bu maddenin var olma sebebi tam olarak ikincisiydi.
    """
    gecer, _ = katman_b.karar({"faturalar"}, None)
    assert gecer, "yapılandırılmamış tenant reddedildi — tam kesinti"

    gecer, gerekce = katman_b.karar({"faturalar"}, set())
    assert not gecer, "BOŞ allowlist geçti — fail-open sürüyor"
    assert "faturalar" in gerekce


def test_ALLOWLIST_DISI_MODEL_REDDEDILIYOR():
    gecer, gerekce = katman_b.karar({"faturalar", "cari"}, {"cari"})
    assert not gecer and "faturalar" in gerekce and "cari" in gerekce


def test_ALLOWLIST_ICI_GECIYOR():
    gecer, _ = katman_b.karar({"cari"}, {"cari", "faturalar"})
    assert gecer


def test_REFERANS_YOKSA_GECIYOR():
    """Hiçbir modele dokunmayan bir SQL (ör. `SELECT 1`) reddedilmez: yasaklanacak bir
    erişim yok. Reddetmek, katmanı **gürültüye** çevirirdi."""
    assert katman_b.karar(set(), set())[0]


# ── 2 · MODEL ÇÖZÜMÜ MOTORUN FONKSİYONUYLA ───────────────────────────────────

def test_MODEL_COZUMU_MOTORUN_KENDI_FONKSIYONUYLA():
    """🔴 Yetkilendirdiğimiz küme, motorun **gerçekten planladığı** küme olmalı. İkisi
    ayrışırsa *"izin verdik"* ile *"dokunuldu"* farklı şeyler olur — bir güvenlik
    katmanının **en sessiz** kırılma biçimi.

    Bu yüzden çözüm `wren.policy.resolve_model_name` ile yapılır; kendi çözücümüzü
    yazmıyoruz."""
    kaynak = (KOK / "app" / "katman_b.py").read_text(encoding="utf-8")
    assert "from wren.policy import resolve_model_name" in kaynak
    assert not re.search(r"^def resolve_model_name\b", kaynak, re.M), \
        "motorun çözücüsü YENİDEN yazılmış — iki sahip"


def test_REFERANS_MODELLER_MDL_DISINI_DONDURMUYOR():
    """MDL'de olmayan tablo döndürülmez: onu `strict_mode`'un kaynak-konumu kapısı zaten
    fail-closed reddediyor. Burada tekrar reddetmek **aynı kuralın ikinci sahibi** olurdu
    ve iki kapı zamanla ayrışırdı."""
    pytest.importorskip("wren.policy")
    bulunan = katman_b.referans_modeller(
        "SELECT * FROM faturalar JOIN bilinmeyen ON 1=1", {"faturalar"})
    assert bulunan == {"faturalar"}


def test_AYRISTIRILAMAYAN_SQL_REDDEDILIYOR():
    """🔴 **Karar verilemeyen bir yetki sorusu REDDEDİLİR.** Ayrıştırılamayan bir SQL'i
    *"model referansı yok"* sayıp geçirmek, ayrıştırıcıyı bir **baypas yüzeyine**
    çevirirdi."""
    pytest.importorskip("wren.policy")
    with pytest.raises(katman_b.ModelErisimReddi):
        katman_b.referans_modeller("SELECT FROM WHERE ((", {"faturalar"})


# ── 3 · STUB DOLDURULDU ve BAĞLANDI ──────────────────────────────────────────

def test_ENFORCE_QUERY_ARTIK_STUB_DEGIL():
    """⟳ Eski gövde **docstring + tek `return`**'dü; üstünde `# TODO(faz-2)` vardı.

    🔴 **ÖLÇÜM YAPISAL, METİN DEĞİL — ve bu bir düzeltme.** İlk sürüm `"TODO(faz-2)" not
    in govde` yazıyordu ve **fonksiyonun kendi tarihçe yorumunu** yakaladı (o yorum,
    stub'ın NE olduğunu anlatıyor). Bu oturumda aynı sınıfa **üçüncü** kez düşüldü
    (`⟳` sayacı · `0.21` tavan operatörü · burası). Doğru soru *"şu dizi geçiyor mu"*
    değil, **"gövde ne yapıyor"**: bir `raise` yolu var mı, `karar()` çağrılıyor mu.
    """
    import ast

    agac = ast.parse((KOK / "control_plane" / "authorize.py").read_text(encoding="utf-8"))
    fn = next((n for n in ast.walk(agac)
               if isinstance(n, ast.FunctionDef) and n.name == "enforce_query"), None)
    assert fn is not None, "`enforce_query` YOK — silinmiş olabilir"

    govde = [d for d in fn.body
             if not (isinstance(d, ast.Expr) and isinstance(d.value, ast.Constant))]
    assert not (len(govde) == 1 and isinstance(govde[0], ast.Return)), (
        "gövde hâlâ tek bir `return` — katman beyan seviyesinde")
    assert any(isinstance(n, ast.Raise) for n in ast.walk(fn)), \
        "katman hiçbir koşulda REDDETMİYOR — bir allowlist reddetmiyorsa allowlist değildir"
    assert any(isinstance(n, ast.Call) and getattr(n.func, "id", "") == "karar"
               for n in ast.walk(fn)), \
        "karar `app/katman_b.py::karar`'dan gelmiyor — ikinci bir karar sahibi doğmuş"


def test_ENFORCE_QUERY_NIN_GERCEK_BIR_CAGIRANI_VAR():
    """🔴 **Bir stub'ı doldurmak yetmez.** Ölçüldü: `enforce_query`'nin çağıranı **yoktu**
    — katman boş değil, **bağlı bile değildi** (`0.5`'in *"ölü modül"* bulgusunun güvenlik
    katmanındaki hâli). Bu test o bağı kilitler."""
    cagiranlar = [
        p for p in (KOK / "app").rglob("*.py")
        if "enforce_query" in p.read_text(encoding="utf-8", errors="ignore")
        and p.name != "katman_b.py"
    ]
    assert cagiranlar, "`enforce_query` yine YETİM — çağıran bir yol yok"


def test_SUPERADMIN_KATMAN_B_DEN_MUAF_ve_GEREKCESI_YAZILI():
    """ADR-0015 K7: superadmin için doktrin **ENGEL değil GÖRÜNÜRLÜK** — her erişim
    audit'e düşer. Katman B'yi ona uygulamak, `authorize()`'ın kendi kararıyla çelişirdi."""
    kaynak = (KOK / "app" / "routers" / "query.py").read_text(encoding="utf-8")
    assert "is_superadmin" in kaynak and "K7" in kaynak


def test_DB_ULASILAMAZSA_TAM_KESINTI_OLMUYOR():
    """⚠ Ulaşılamayan bir **yetki deposunu** boş allowlist saymak, bir altyapı arızasını
    **tam kesintiye** çevirirdi. `None` (yapılandırılmamış) döner ve Katman A yönetir."""
    kaynak = (KOK / "app" / "routers" / "query.py").read_text(encoding="utf-8")
    i = kaynak.index("def _allowlist")
    assert "return None" in kaynak[i:i + 1400]


def test_DISCOVERY_YOLUNUN_SIRASI_YAZILI():
    """`/ask`'in Discovery dalı **ikinci** çağrı yoludur ve ayrı turda bağlanır:
    `routers/ask.py` **risk sınırındadır** (demete girmez, kendi kapısını koşar).
    Sessizce atlanmadı — sırası **yazılı** olmalı, yoksa bir sonraki tur onu *"zaten
    bağlı"* sanır."""
    kaynak = (KOK / "app" / "routers" / "query.py").read_text(encoding="utf-8")
    assert "risk sınırında" in kaynak and "Discovery" in kaynak
