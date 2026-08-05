"""FAZ 1.2 — **KOLON DÜZEYİ ERİŞİM DENETİMİ** (`columnLevelAccessControl`) kapısı.

Ön ölçüm (2026-08-04, `wren_core` üstünde uçtan uca):

| # | Soru | Sonuç |
|---|---|---|
| 1 | CLAC manifest round-trip'inde kalıyor mu? | ✅ |
| 2 | Seviye yetersizken ne olur? | 🔴 kolon **plandan tamamen DÜŞER** (`SELECT *` onu döndürmez) |
| 3 | Seviye yeterliyse? | ✅ gelir |
| 4 | Property yoksa? | ✅ **fail-closed** (planlama hatası) |

🔴 **(2) bu maddenin en önemli gerçeği ve varsayılanı belirledi.** CLS `pii.py`'den
**kategorik olarak farklıdır**: maskeleme kolonu **gösterir** (`123****89`), CLS onu **yok
eder** — ve yok etme **sessizdir**. Sessizce eksik bir tablo, maskeli bir tablodan **daha
kötüdür**, çünkü kullanıcı eksikliği **fark etmez**. Bu yüzden `motor_cls` varsayılanı
`off` ve `on` kademesi bir **kapıyla** kilitli (aşağıda).
"""

from __future__ import annotations

import ast
import base64
import json
import pathlib

import pytest

from app import rls

KOK = pathlib.Path(__file__).resolve().parents[1]
BOYAHANE = KOK / "demo" / "wren-projects" / "demo-boyahane" / "target" / "mdl.json"


def _ham() -> bytes:
    if not BOYAHANE.exists():
        pytest.skip("boyahane manifesti derlenmemiş")
    return BOYAHANE.read_bytes()


# ── 1 · KURAL B ──────────────────────────────────────────────────────────────

def test_OFF_ve_SHADOW_MANIFESTE_DOKUNMUYOR():
    """`off` bugünkü davranış; `shadow` **ölçer, davranmaz** (`motor_rls` ile aynı disiplin)."""
    ham = _ham()
    for kademe in ("off", "shadow"):
        assert rls.cls_manifeste_yaz(ham, kademe=kademe) == (ham, 0), kademe


def test_GECERSIZ_KADEME_HATA_VERIR():
    with pytest.raises(ValueError):
        rls.cls_manifeste_yaz(_ham(), kademe="acik")


# ── 2 · EŞLEME TEK SAHİPTEN ──────────────────────────────────────────────────

def test_SINIFLANDIRMA_SENSITIVITY_DEN_GELIYOR():
    """🔴 Hassasiyet kuralının **ikinci sahibi** olmaz. `pii.py` ve CLS aynı
    `sensitivity.classify`'ı okumazsa aynı kolon bir katmanda maskeli, ötekinde **görünür**
    olurdu — ve hangisinin doğru olduğu bilinemezdi."""
    kaynak = (KOK / "app" / "rls.py").read_text(encoding="utf-8")
    assert "from app.sensitivity import classify" in kaynak
    assert "_PERSON_TOKENS" not in kaynak and "_SPECIAL_TOKENS" not in kaynak, \
        "hassasiyet sözlüğü rls.py'ye KOPYALANMIŞ — iki sahip"


def test_NORMAL_KOLONA_CLAC_YAZILMIYOR():
    """`normal` sözlükte **yok** ve bu bilinçli: herkese görünür bir kolona kural yazmak
    her sorguya gereksiz bir session property zorunluluğu getirirdi."""
    assert "normal" not in rls.SENSITIVITY_ESIGI


def test_ESIKLER_VAR_OLAN_KARARDAN_TURUYOR():
    """🔴 **Yeni bir gizlilik merdiveni İCAT EDİLMEDİ.** `authorize.py` zaten
    `"pii:view": 2` (admin+) diyor ve gerekçesi yazılı. `gizlilik_seviyesi()` o kararı
    **okur**; ikinci bir kural yazmak bu deponun 1 numaralı kusuru olurdu."""
    kaynak = (KOK / "app" / "rls.py").read_text(encoding="utf-8")
    i = kaynak.index("def gizlilik_seviyesi")
    assert 'can(principal, "pii:view")' in kaynak[i:i + 900], \
        "seviye `pii:view`'dan türemiyor — ikinci bir merdiven icat edilmiş"


def test_CLAC_FAIL_OPEN_DESENI_URETMIYOR():
    """`1.1`'de ölçülen `defaultExpr` / `required=False` fail-open'ı burada da yasak."""
    ham = _ham()
    yeni, n = rls.clac_manifesti(ham)
    assert n >= 1, "boyahane 20 `person` kolonu taşıyor — hiç kural üretilmedi"
    m = json.loads(yeni)
    for model in m["models"]:
        for kolon in model.get("columns") or []:
            k = kolon.get("columnLevelAccessControl")
            if not k:
                continue
            assert rls.kurallari_denetle([k]) == [], (kolon["name"], k)


# ── 3 · UÇTAN UCA: KOLON GERÇEKTEN DÜŞÜYOR ───────────────────────────────────

def _plan(manifest: bytes, seviye: str | None, sql: str) -> str:
    wc = pytest.importorskip("wren_core")
    props = frozenset({rls.OTURUM_GIZLILIK: seviye}.items()) if seviye else None
    return wc.SessionContext(base64.b64encode(manifest).decode(), None, props,
                             "duckdb").transform_sql(sql)


def _hassas_hedef(manifest: dict) -> tuple[str, str]:
    for model in manifest["models"]:
        for kolon in model.get("columns") or []:
            if kolon.get("columnLevelAccessControl"):
                return model["name"], kolon["name"]
    pytest.skip("CLAC'lı kolon yok")


def test_SEVIYE_YETERSIZ_KOLON_PLANDAN_DUSUYOR():
    """🔴 **Maskelemiyor, YOK EDİYOR.** `pii.py`'den kategorik fark budur."""
    yeni, _n = rls.clac_manifesti(_ham())
    model, kolon = _hassas_hedef(json.loads(yeni))
    sql = _plan(yeni, "0", f'SELECT * FROM "{model}"')
    assert kolon.lower() not in sql.lower(), f"{kolon} seviye 0'da hâlâ planda:\n{sql[:300]}"


def test_SEVIYE_YETERLI_KOLON_GELIYOR():
    yeni, _n = rls.clac_manifesti(_ham())
    model, kolon = _hassas_hedef(json.loads(yeni))
    assert kolon.lower() in _plan(yeni, "2", f'SELECT * FROM "{model}"').lower()


def test_PROPERTY_YOKSA_FAIL_CLOSED():
    """Sessizce **kolonlu** plan üretmek, katmanı bir süse çevirirdi."""
    yeni, _n = rls.clac_manifesti(_ham())
    model, _kolon = _hassas_hedef(json.loads(yeni))
    with pytest.raises(Exception):
        _plan(yeni, None, f'SELECT * FROM "{model}"')


# ── 4 · SQL LİTERALİ — birinci savunma ───────────────────────────────────────

def test_LITERAL_TIRNAK_KACIYOR():
    assert rls.sql_literal("o'brien") == "'o''brien'"
    assert rls.sql_literal(2) == "2"


def test_BOS_DEGER_NULL_URETMIYOR():
    """`NULL` üretmek, **hiçbir satırla eşleşmeyen ama hata da vermeyen** bir koşul
    doğururdu — sessiz bir boş sonuç, sessiz bir sızıntı kadar kötüdür."""
    for kotu in (None, ""):
        with pytest.raises(ValueError):
            rls.sql_literal(kotu)


def test_YAPILANDIRILMIS_DEGER_REDDEDILIYOR():
    with pytest.raises(TypeError):
        rls.sql_literal({"a": 1})


def test_PRINCIPALSIZ_OZELLIK_BOS_DONUYOR():
    """Uydurma bir varsayılan, motorun fail-closed dalını **sessizce** açardı."""
    assert rls.oturum_ozellikleri(None) == {}


# ── 5 · 🔴 BAYRAK, TESİSAT TAMAMLANMADAN AÇILAMAZ ────────────────────────────

def _principalsiz_cagrilar() -> list[str]:
    """`WrenService.query`/`dry_plan` çağrılarından `principal=` **geçmeyenler**.

    CLS session property'yi **zorunlu** kılar; bir çağrı sitesi principal geçmezse
    `motor_cls=on` iken o yol **fail-closed** patlar. Yani bayrak, tesisat tamamlanmadan
    açılırsa **kesinti** üretir — kapı bunu önceden söyler.
    """
    eksik: list[str] = []
    for yol in sorted((KOK / "app").rglob("*.py")):
        if yol.name in ("wren_service.py", "rls.py"):
            continue
        try:
            agac = ast.parse(yol.read_text(encoding="utf-8"))
        except SyntaxError:                                  # pragma: no cover
            continue
        for n in ast.walk(agac):
            if not isinstance(n, ast.Call) or not isinstance(n.func, ast.Attribute):
                continue
            if n.func.attr not in ("query", "dry_plan"):
                continue
            if any(k.arg == "principal" for k in n.keywords):
                continue
            eksik.append(f"{yol.relative_to(KOK)}:{n.lineno} · .{n.func.attr}()")
    return eksik


def test_MOTOR_CLS_ON_OLAMAZ_TESISAT_EKSIKKEN():
    """🔴 **Bayrak kendi ön koşulunu bilir.**

    `motor_cls=on` iken principal geçmeyen HER `query`/`dry_plan` çağrısı **fail-closed**
    patlar (motor zorunlu property'yi bulamaz). Bu test, bayrağın ancak tesisat
    tamamlandığında açılabilmesini **kodla** garanti eder — *"açtım ama yarısı çalışmıyor"*
    hâli, bir güvenlik katmanının en pahalı hatasıdır.

    ⚠ Kalan çağrı siteleri **sayıyla** raporlanır (sessiz kırpma yok): bir sonraki tur
    kaçının bağlanacağını **bilerek** başlar.
    """
    from app.config import get_settings

    eksik = _principalsiz_cagrilar()
    kademe = str(getattr(get_settings(), "motor_cls", "off") or "off").lower()
    if kademe != "on":
        return                    # `off`/`shadow` — eksik tesisat henüz zararsız
    # 🔴 **ÖLÇÜT DEĞİŞTİ — ve değişmesi bir DÜZELTMEDİR, bir gevşetme değil.**
    #
    # Bu test "her ÇAĞRI SİTESİ `principal=` geçiyor mu" diye soruyordu ve o soru, borcu
    # **fail-open** bir biçimde tarif ediyordu: 36'yı kapatsan, 37.'si yine açık doğardı.
    #
    # Doğru soru **"her GİRİŞ NOKTASI kimliği kuruyor mu"**dur. Kimlik artık
    # `app/istek_kimligi.py` ContextVar'ında yaşıyor ve `WrenService._oturum_ozellikleri`
    # açık argüman yoksa **oradan** okuyor. Yani bir çağrı sitesinin `principal=` geçmemesi
    # artık bir **açık** değil, bir **tercih**tir.
    #
    # ⚠ Açık argüman hâlâ bağlamı **ezer** — arka plan işleri kendi kimliğiyle koşabilsin.
    if _kimlik_baglami_kurulu():
        return
    assert not eksik, (
        f"🔴 `motor_cls=on`, kimlik bağlamı YOK ve {len(eksik)} çağrı sitesi principal "
        f"GEÇMİYOR:\n  " + "\n  ".join(eksik)
        + "\nHer biri fail-closed patlar. Önce tesisatı tamamla, sonra bayrağı aç.")


def _kimlik_baglami_kurulu() -> bool:
    """Kimlik **her giriş noktasında** kuruluyor mu — ve `WrenService` onu okuyor mu?

    🔴 Üç giriş noktası var ve üçü de sayılır; biri eksikse bağlam *"kurulu"* değildir:

    | giriş | kimliği nereden alır |
    |---|---|
    | HTTP | `get_current_principal` — token'dan doğar |
    | zamanlayıcı | `run_schedule` — `run_as_user_id` → `created_by`, çözülemezse **koşmaz** |
    | MCP | `Planlayici` — `cagir()` planlayıcıyı **zorunlu** ister |

    ⚠ Lab/CLI araçları **bilerek** sayılmıyor: onlar kimliksiz koşar ve `motor_cls=on`
    iken **en kısıtlı** seviyede sonuç alır. *Bir aracın az veri görmesi, bir kullanıcının
    fazla veri görmesinden iyidir.*
    """
    ws = (KOK / "app" / "wren_service.py").read_text(encoding="utf-8")
    if "istek_kimligi.simdiki()" not in ws:
        return False
    dep = (KOK / "app" / "auth" / "dependencies.py").read_text(encoding="utf-8")
    if "istek_kimligi.ayarla(principal)" not in dep:
        return False
    sch = (KOK / "app" / "schedules.py").read_text(encoding="utf-8")
    return "istek_kimligi.IstekKimligi(principal)" in sch


def test_MOTOR_CLS_VARSAYILANI_OFF_ve_GEREKCESI_YAZILI():
    """🔴 `motor_rls` `shadow`, `motor_cls` **`off`** — fark bilinçli ve ölçülmüş:
    CLS kolonu **düşürüyor** ve düşme **sessiz**."""
    kaynak = (KOK / "app" / "config.py").read_text(encoding="utf-8")
    i = kaynak.index("motor_cls")
    assert 'motor_cls: str = "off"' in kaynak, "varsayılan `off` değil"
    gerekce = kaynak[max(0, i - 1200):i]
    assert "PLANDAN DÜŞÜRÜR" in gerekce and "SESSİZ" in gerekce.upper(), \
        "varsayılanın gerekçesi yazılı değil"


def test_HANGI_KATMAN_HANGI_BICIM():
    """🔴 **İKİ KATMAN, İKİ BİÇİM — ve karıştırmak üç testi kırmızıya düşürdü.**

    * `wren_core.SessionContext(properties=…)` → **`frozenset`**
    * `wren.engine.WrenEngine.dry_plan/query(properties=…)` → **`dict`** (dönüşümü kendi
      yapar: `_plan` içinde `frozenset(properties.items())`)

    Ön ölçüm probe'u `SessionContext`'i doğrudan kullandığı için `frozenset` gördüm ve onu
    **bir katman yukarıya** taşıdım → `'frozenset' object has no attribute 'items'`.
    Belgelenmiş bir tuzak, **yanlış katmanda** uygulanınca yine tuzaktır. Bu test ikisini
    birden ölçer ki ayrım bir yorumda değil **kodda** dursun.
    """
    import inspect

    wc = pytest.importorskip("wren_core")
    engine = pytest.importorskip("wren.engine")

    # (a) SessionContext: düz sözlük REDDEDİLİR.
    # ⚠ Geçerli bir MDL ile denenir: `mdl_base64=None` iken property yolu hiç
    # değerlendirilmiyor ve test **yanlış-yeşil** olurdu (ilk yazımda öyle oldu).
    mdl = base64.b64encode(json.dumps({
        "catalog": "c", "schema": "s",
        "models": [{"name": "t",
                    "tableReference": {"catalog": "memory", "schema": "main", "table": "t"},
                    "columns": [{"name": "id", "type": "integer"}]}]}).encode()).decode()
    with pytest.raises(TypeError):
        wc.SessionContext(mdl, None, {"a": "1"}, "duckdb")

    # (b) WrenEngine: dönüşümü KENDİ yapıyor → sözlük bekliyor
    kaynak = inspect.getsource(engine)
    assert "frozenset(properties.items())" in kaynak, (
        "motor facade artık dönüşümü yapmıyor olabilir — `_oturum_ozellikleri`'nin "
        "döndürdüğü biçim GÜNCELLENMELİ (sessizce kaymamalı)")

    # (c) Bizim yardımcımız SÖZLÜK döndürüyor (facade'ın istediği)
    from app.wren_service import WrenService

    kaynak_ws = inspect.getsource(WrenService._oturum_ozellikleri)
    assert "frozenset" not in kaynak_ws.split('"""')[-1], \
        "`_oturum_ozellikleri` yine frozenset döndürüyor — facade `.items()` çağırır ve patlar"
