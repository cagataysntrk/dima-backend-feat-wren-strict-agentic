"""FAZ 1.3b — **Katman B: model allowlist** kapısı.

Ölçülen kusur iki katlıydı: `enforce_query` bir **stub**'dı (gövde tek satır `return`)
**ve çağıranı yoktu**. Yani ADR-0014 Karar 5'in beyan ettiği katman ne iş yapıyordu ne de
bağlıydı — *"beyan var, kod onu tanımıyor"* sınıfının güvenlik katmanındaki hâli.
"""

from __future__ import annotations

import ast
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
    # ⟳ **FAZ 1.3b/2 düzeltmesi.** Eski ölçüm *"`katman_b.py` DIŞINDA bir dosyada
    # `enforce_query` geçiyor mu"* diye bakıyordu; zorlama tek sahibe taşınınca kapı
    # **yanlışlıkla kırmızı** oldu — oysa bağ **güçlendi**. Doğru soru bir dosya adı değil,
    # **zincirin kendisi**: `zorla` → `enforce_query` **ve** bir uç → `zorla`/`sarmala`.
    agac = ast.parse((KOK / "app" / "katman_b.py").read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "zorla")
    assert any(isinstance(n, ast.Call) and getattr(n.func, "id", "") == "enforce_query"
               for n in ast.walk(fn)), "`zorla` `enforce_query`'yi ÇAĞIRMIYOR"

    uclar = [p for p in (KOK / "app" / "routers").rglob("*.py")
             if re.search(r"katman_b\.(zorla|sarmala)\(",
                          p.read_text(encoding="utf-8", errors="ignore"))]
    assert len(uclar) >= 2, (
        f"Katman B yalnız {len(uclar)} uçtan çağrılıyor ({[p.name for p in uclar]}) — "
        "ham SQL'in İKİ yolu var: `/query` (kullanıcı SQL'i) ve `/ask` (Discovery)")


def test_SUPERADMIN_KATMAN_B_DEN_MUAF_ve_GEREKCESI_YAZILI():
    """ADR-0015 K7: superadmin için doktrin **ENGEL değil GÖRÜNÜRLÜK** — her erişim
    audit'e düşer. Katman B'yi ona uygulamak, `authorize()`'ın kendi kararıyla çelişirdi."""
    kaynak = (KOK / "app" / "katman_b.py").read_text(encoding="utf-8")
    assert "is_superadmin" in kaynak and "K7" in kaynak


def test_DB_ULASILAMAZSA_TAM_KESINTI_OLMUYOR():
    """⚠ Ulaşılamayan bir **yetki deposunu** boş allowlist saymak, bir altyapı arızasını
    **tam kesintiye** çevirirdi. `None` (yapılandırılmamış) döner ve Katman A yönetir."""
    kaynak = (KOK / "app" / "katman_b.py").read_text(encoding="utf-8")
    i = kaynak.index("def allowlist")
    assert "return None" in kaynak[i:i + 1400]


def test_DISCOVERY_YOLU_ARTIK_BAGLI():
    """⟳ **TUZAKTAN KAPIYA — `1.3b/2` indi, tuzak TERS ÇEVRİLDİ.**

    Eski yön: *"Discovery **ikinci** çağrı yoludur, ayrı turda bağlanacak — sırası yazılı
    olmalı ki bir sonraki tur onu «zaten bağlı» sanmasın"*. O tur geldi. Yeni yön:
    **gerçekten bağlı olmalı** — ve bu, metinle değil **yapıyla** ölçülür.

    🔴 Kapı `sarmala`'yı arar, bir yorum satırını değil: bu oturumda **yedi kez** bir metin
    taraması yanlış yeri ölçtü. Bir güvenlik katmanının bağlı olup olmadığı, ancak
    **çağrının kendisi** görülerek bilinir.
    """
    agac = ast.parse((KOK / "app" / "routers" / "ask.py").read_text(encoding="utf-8"))
    kesif = next(n for n in ast.walk(agac)
                 if isinstance(n, ast.FunctionDef) and n.name == "_run_discovery")
    assert any(isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "sarmala"
               for n in ast.walk(kesif)), \
        "Discovery dalı Katman B'den GEÇMİYOR — katman bağlı değil"


def test_DISCOVERY_MOTORA_KAPISIZ_DOKUNMUYOR():
    """🔴 **Sarmal varken bile çıplak `service.` kalırsa kapı DELİKTİR.** Sarmalın değeri
    *"yeni dallar dâhil hepsini kapsar"* olmasıdır; kapsam dışında kalan tek bir çağrı,
    o değeri **tamamen** yok eder — ve gözle görülmez."""
    kaynak = (KOK / "app" / "routers" / "ask.py").read_text(encoding="utf-8")
    agac = ast.parse(kaynak)
    kesif = next(n for n in ast.walk(agac)
                 if isinstance(n, ast.FunctionDef) and n.name == "_run_discovery")
    kacaklar = [n.lineno for n in ast.walk(kesif)
                if isinstance(n, ast.Attribute) and n.attr in ("dry_plan", "query")
                and getattr(n.value, "id", "") == "service"]
    assert not kacaklar, f"Discovery içinde KAPISIZ motor çağrısı: satır {kacaklar}"


def test_YETKI_REDDI_ONARIMA_DUSMUYOR():
    """🔴 Bir yetki reddi **onarılamaz**: `llm.repair` onu düzeltemez, yalnız bir LLM
    çağrısı harcar ve sonunda *"güvenilir bir sorgu üretemedim"* der. Kullanıcı **neden**
    cevap alamadığını öğrenemez; sınır kendini bir **arıza** gibi gösterir."""
    kaynak = (KOK / "app" / "routers" / "ask.py").read_text(encoding="utf-8")
    i = kaynak.index("planned = motor.dry_plan(wren_sql)")
    blok = kaynak[i:i + 400]
    assert "ModelErisimReddi" in blok, "ret, self-healing dalına düşüyor"
    assert blok.index("ModelErisimReddi") < blok.index("except Exception"), \
        "genel `except` önce geliyor — özel dal HİÇ çalışmaz"


def test_RET_NOTU_ALLOWLIST_ICERIGINI_SIZDIRMIYOR():
    """⚠ *"`personel_ozluk`'a erişemezsin"* cümlesi, erişilemeyen şeyin **varlığını**
    sızdırır. Gerekçenin tamamı `trace`'e ve audit'e yazılır — **kaybolmaz**, yalnız
    yetkili olan yerde durur."""
    assert "allowlist" not in katman_b.RED_NOTU.lower()
    assert "model" not in katman_b.RED_NOTU.lower()
    assert "yetki" in katman_b.RED_NOTU.lower()


def test_SARMAL_GERCEKTEN_REDDEDIYOR(monkeypatch):
    """🔴 **Kapı, kırmızı olabildiğini kanıtlayana kadar kapı değildir.** Yukarıdaki
    yapısal testler *"çağrı var"* der; bu test **davranışı** ölçer: allowlist'i
    yapılandırılmış bir principal, listede olmayan bir modele dokunan SQL'i motora
    **geçiremez** — ve red `dry_plan`'dan **ÖNCE** olur (yani sorgu hiç planlanmaz)."""
    plan_edildi: list[str] = []

    class _Sahte:
        def schema(self):
            return {"models": [{"name": "faturalar"}, {"name": "personel_ozluk"}]}

        def dry_plan(self, sql, *a, **kw):
            plan_edildi.append(sql)
            return "plan"

        def query(self, sql, *a, **kw):
            plan_edildi.append(sql)
            return {}

    class _P:
        tenant_id = "t1"
        is_superadmin = False
        roles = ("owner",)

    class _Istek:
        class state:
            principal = _P()

    monkeypatch.setattr(katman_b, "allowlist", lambda *_a, **_k: {"faturalar"})
    kapili = katman_b.sarmala(_Sahte(), _Istek())

    assert kapili.dry_plan("select 1 from faturalar") == "plan"      # izinli → geçer
    with pytest.raises(katman_b.ModelErisimReddi):
        kapili.dry_plan("select tc_kimlik from personel_ozluk")
    with pytest.raises(katman_b.ModelErisimReddi):
        kapili.query("select tc_kimlik from personel_ozluk")         # query de kapılı
    assert plan_edildi == ["select 1 from faturalar"], \
        "reddedilen SQL yine de motora GİTMİŞ — kapı red'i geç veriyor"


def test_YAPILANDIRILMAMIS_TENANT_ENGELLENMIYOR(monkeypatch):
    """⚠ `ModelPermission` tablosu bugün **her tenant'ta boş**. Sarmal, yapılandırılmamış
    bir tenant'ta hiçbir şeyi engellememeli — aksi hâlde bir güvenlik katmanı adına
    **tam kesinti** olurdu."""
    class _Sahte:
        def schema(self):
            return {"models": [{"name": "faturalar"}]}

        def dry_plan(self, sql, *a, **kw):
            return "plan"

    class _P:
        tenant_id = "t1"
        is_superadmin = False
        roles = ("owner",)

    class _Istek:
        class state:
            principal = _P()

    monkeypatch.setattr(katman_b, "allowlist", lambda *_a, **_k: None)
    assert katman_b.sarmala(_Sahte(), _Istek()).dry_plan("select 1 from her_ne") == "plan"


def test_SARMAL_SEFFAF():
    """Sarmal bir **kapıdır**, ikinci bir motor değil: öteki her nitelik olduğu gibi
    görünür. Görünmeseydi `mdl_version` gibi alanlar sessizce kaybolurdu."""
    class _Sahte:
        mdl_version = "v42"

        def dry_plan(self, sql, *a, **kw):
            return f"plan:{sql}"

        def query(self, sql, *a, **kw):
            return {"sql": sql}

        def schema(self):
            return {"models": []}

    class _Istek:
        class state:
            principal = None

    kapili = katman_b.sarmala(_Sahte(), _Istek())
    assert kapili.mdl_version == "v42"
    assert kapili.dry_plan("select 1") == "plan:select 1"
    assert kapili.query("select 1") == {"sql": "select 1"}


def test_YETKI_REDDI_422_DEGIL_403():
    """🔴 **Ölçülen kusur:** `/query`'de Katman B reddi `except Exception`'a düşüp **422**
    ("engine / DB errors") dönüyordu. İstemci bunu *"sorgum bozuk"* diye okur, geliştirici
    motorda arar. *Bir yetki sınırının kendini ARIZA gibi göstermesi, sınırın kendisini
    görünmez kılar.*"""
    kaynak = (KOK / "app" / "routers" / "query.py").read_text(encoding="utf-8")
    i = kaynak.index("except katman_b.ModelErisimReddi")
    blok = kaynak[i:i + 700]
    assert "status_code=403" in blok
    assert i < kaynak.index("except Exception as exc:  # engine / DB errors"), \
        "genel `except` önce geliyor — 403 dalı HİÇ çalışmaz"
