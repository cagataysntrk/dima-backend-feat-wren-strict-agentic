"""FAZ 4.5 kapısı — **MCP, HTTP'nin YANINA değil İÇİNE bağlanır.**

Yol haritasının değişmezi: *"MCP'den çağrılan araç HTTP'den çağrılanla **aynı dört
kapıdan** geçer ve **aynı makbuzu** üretir; ayrı bir yol açılırsa madde **yanlış
yapılmış demektir**."*

Bu dosya o cümleyi **yapısal olarak** (AST) ve **davranışsal olarak** (gerçek çağrı)
kilitler. Metin taraması bilerek kullanılmadı: `app/mcp.py`'nin docstring'i tam da bu
kuralı **anlatıyor** ve bir alt-dize taraması kendi belgesini ölçerdi — bu deponun on
kez ödediği ders.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from app import mcp, tools
from app.planner import Butce, Planlayici

_MCP = Path(__file__).resolve().parents[1] / "app/mcp.py"
_ROUTER = Path(__file__).resolve().parents[1] / "app/routers/mcp.py"


def _adlar(kaynak: Path) -> set[str]:
    agac = ast.parse(kaynak.read_text(encoding="utf-8"))
    out = {n.attr for n in ast.walk(agac) if isinstance(n, ast.Attribute)}
    out |= {n.id for n in ast.walk(agac) if isinstance(n, ast.Name)}
    return out


def test_MCP_kendi_KAYDINI_kurmaz():
    """🔴 *"İnce bir çevirici; kendi kaydını KURMAZ"* — `tools.py`'nin kendi notu.

    İkinci bir araç kaydı, üç yüzeyin (LLM · MCP · UI) **ayrışması** demekti: bir araç
    bir yüzeyde açık, ötekinde kapalı olurdu ve hangisinin doğru olduğunu kimse bilemezdi.
    """
    agac = ast.parse(_MCP.read_text(encoding="utf-8"))
    for n in ast.walk(agac):
        if isinstance(n, ast.Assign):
            for h in n.targets:
                assert getattr(h, "id", "") not in ("KAYIT", "ARACLAR", "_ARACLAR"), (
                    "🔴 `app/mcp.py` KENDİ araç kaydını kurmuş — çevirici olmaktan çıkıp "
                    "ikinci bir motor olmuş demektir.")
        # Bir `Arac(...)` örneği oluşturmak da aynı ihlaldir.
        if isinstance(n, ast.Call):
            assert getattr(n.func, "id", "") != "Arac", (
                "🔴 `app/mcp.py` KENDİ `Arac`'ını tanımlamış — kayıt tek yerde durmalı.")
    # Ve kaydı GERÇEKTEN `tools`'tan okuyor mu:
    #
    # ⚠ İlk sürüm tek bir ADA bağlıydı (`"llm_araclari" in _adlar(_MCP)`) ve `§C3` ④/②
    # düzeltmesinde liste `tools.okuyan_araclar()`'a geçince **yanlış-kırmızı** verdi:
    # kural yerindeydi (fonksiyon `llm_araclari`'ı kendi içinde çağırıyor), kapı **adı**
    # ölçüyordu. Bu, bu turda kapının bir cümleye bağlanmasının kaçıncı kez ceza
    # kestiğinin bir örneği — doğru ölçüm **iddianın kendisidir**:
    #   ① liste `tools`'un BİR üreticisinden gelir, ve
    #   ② yetki süzgeci burada İKİNCİ KEZ YAZILMAZ.
    uretici = {"llm_araclari", "okuyan_araclar"} & _adlar(_MCP)
    assert uretici, (
        "🔴 MCP araç listesi `tools`'un bir araç üreticisinden gelmiyor — yetki süzgeci "
        "ikinci kez yazılmış olabilir ve iki kopya AYRIŞIR.")
    assert not ({"izinli_araclar", "authorize"} & _adlar(_MCP)), (
        "🔴 `app/mcp.py` yetki matrisine DOĞRUDAN dokunuyor — süzgecin ikinci sahibi "
        "doğdu. Yetki kararı `tools.izinli_araclar()` → `authorize()` zincirinde kalır.")


def test_MCP_SALT_OKUMA_yazma_araci_SIZMAZ():
    """🔴 `§C3` ② — **listede yazma aracı YOK, ve bu artık YAPISAL.**

    Ölçüldü (2026-08-12): `yazma_araclari` bayrağı **açıkken** `tools.KAYIT` 25 → **28**
    olur ve `mcp.araclar(None)` de **28** döndürüyordu — üç yazma aracı MCP yüzeyinde
    **görünüyordu**. Kartın *«yazma araçları kayıtta yok (zaten öyle)»* güvencesi bir
    güvence değil bir **rastlantıydı**: kayıtta yazan araç olmadığı için doğruydu.

    *Bir sınırı bir rastlantının koruması, o sınırın hiç konmamış olmasıdır.*
    """
    from tests.kapi_ortak import yazma_araclari_acik

    with yazma_araclari_acik() as tools:
        from app import mcp

        yazanlar = {a.ad for a in tools.KAYIT if a.yan_etki != "yok"}
        assert yazanlar, (
            "⊘ ölçüm tabanı çöktü: bayrak açıkken bile kayıtta yazan araç yok — bu test "
            "o hâlde HİÇBİR ŞEY ölçmüyor demektir (boş bir kapı, yeşil bir kapıdan kötüdür).")
        listede = {a["name"] for a in mcp.araclar(None)}
        assert not (yazanlar & listede), (
            f"🔴 YAZMA aracı MCP yüzeyinde: {sorted(yazanlar & listede)}. MCP "
            "SALT-OKUMADIR; yazma yalnız onay akışı (`POST /ask/eylem`) üzerinden.")


def test_MCP_CAGRISI_yazma_aracini_REDDEDER():
    """🔴 Listeden gizlemek **yetmez** — adı bilen bir ajan yine çağırabilirdi.

    *Bir yüzeyi yalnız listeden gizleyerek kapatmak, kapıyı kilitlemek değil tabelayı
    indirmektir.*
    """
    from tests.kapi_ortak import yazma_araclari_acik
    from app.yazma_araclari import YAZMA_KAYIT

    sinif = type("SahteP", (), {"kosum": None})()
    with yazma_araclari_acik():
        from app import mcp
        r = mcp.cagir(sinif, YAZMA_KAYIT[0].ad, {"title": "x"})
    assert r["isError"] is True
    metin = r["content"][0]["text"]
    assert "SALT-OKUMA" in metin and "onay" in metin.lower(), (
        f"red DÜRÜST değil — neyin neden reddedildiği yazılmamış: {metin[:160]}")


def test_MCP_araci_kendisi_CAGIRMAZ_kapidan_gecirir():
    """🔴 Ayrı bir yürütme yolu **açılamaz**: `arac.cagir()`/`importlib` MCP'de YASAK."""
    adlar = _adlar(_MCP) | _adlar(_ROUTER)
    for yasak in ("import_module", "importlib"):
        assert yasak not in adlar, (
            f"🔴 MCP `{yasak}` kullanıyor — aracı kendi çözüyor demektir ve bu, dört "
            f"kapıyı (KAYIT · yetki · deterministik-önce · bütçe) ATLAR.")
    assert "calistir" in adlar, (
        "🔴 MCP `Planlayici.calistir()` çağırmıyor — dört kapıdan geçmeyen bir yol açılmış.")
    # Router'da yetki İKİNCİ KEZ hesaplanmamalı (matrisin ikinci kopyası olurdu).
    assert "can" not in _adlar(_ROUTER), (
        "🔴 MCP router'ı `authorize.can()`'i kendi çağırıyor — yetki kararı iki yerde "
        "olursa iki karar AYRIŞIR. Süzgeç `izinli_araclar()`'ın işidir.")


def test_planlayicisiz_cagri_REDDEDILIR():
    """`planlayici` zorunlu — opsiyonel olsaydı kapıları atlamak `None` geçmek kadar
    kolay olurdu."""
    with pytest.raises(ValueError, match="Planlayici"):
        mcp.cagir(None, "route", {})


def test_arac_listesi_LLM_yuzeyiyle_AYNI_kumedir():
    """Üç yüzey ayrışmaz: MCP'nin gördüğü araç kümesi LLM'inkiyle **birebir aynı**."""
    # ⟳ **AYNI KÜME → SALT-OKUMA ALT KÜMESİ (2026-08-12).** `yazma_araclari` bayrağı
    # açıldığı gün bu eşitlik kırılacaktı — ve o kırılma bir **kusur değil, kasıt**
    # olurdu: MCP salt-okumadır, ajan yüzeyi değildir. Eşitliği olduğu gibi bırakmak,
    # güvenlik sınırının kendisini bir gerileme gibi raporlardı.
    #
    # Değişmez korundu ve **daraltıldı**: MCP'de `tools` kaydında olmayan bir araç
    # bulunamaz (ayrışma yasağı), ve eksiği **yalnız** yazma araçları olabilir.
    m = {a["name"] for a in mcp.araclar(None)}
    l = {a["name"] for a in tools.llm_araclari(None)}
    assert m <= l, f"🔴 MCP'de `tools` kaydında OLMAYAN araç var: {sorted(m - l)}"
    yazanlar = {a.ad for a in tools.KAYIT if a.yan_etki != "yok"}
    assert (l - m) <= yazanlar, (
        f"🔴 MCP'den OKUYAN bir araç düşmüş: {sorted((l - m) - yazanlar)} — üç yüzey "
        "yalnız yazma sınırında ayrışabilir, başka hiçbir gerekçeyle.")
    # MCP spec camelCase ister; çeviri YALNIZ burada yapılır.
    assert all(mcp.SEMA_ALANI in a for a in mcp.araclar(None))
    assert all("input_schema" not in a for a in mcp.araclar(None))


def test_YAZAN_arac_MCP_yuzeyinde_YOK():
    """🔴 MIMARI §4 read-only değişmezi MCP'de de geçerli.

    Ajanın yazma yetkisi ayrı bir mimari karardır (FAZ 6.1'in onay kademesi). MCP bir
    **çeviri** olduğu için bu sınır otomatik miras alınır — ama bir gün biri kayda
    `yan_etki="yazar"` bir araç eklerse, o araç **sessizce MCP'den de** çağrılabilir
    olurdu. Bu kapı o günü görünür kılar.
    """
    # ⟳ **İDDİA DÜZELTİLDİ (2026-08-12) — ve bu testin KENDİ ÖNGÖRÜSÜ gerçekleşti.**
    #
    # Yukarıdaki docstring aynen şunu yazıyordu: *"bir gün biri kayda `yan_etki='yazar'`
    # bir araç eklerse, o araç SESSİZCE MCP'den de çağrılabilir olurdu."* O gün geldi
    # (`yazma_araclari` bayrağı, `§F13`) ve öngörü **birebir** doğru çıktı: ölçüldü,
    # bayrak açıkken üç yazma aracı `mcp.araclar(None)`'da görünüyordu.
    #
    # Ama kapının **ölçtüğü şey** yanlıştı: kaydın boş olmasını istiyordu. Kayıt bir gün
    # dolacaktı — çünkü ajanın yazma ÖNERMESİ meşru bir hedeftir. Doğru değişmez kaydın
    # boşluğu değil, **yüzeyin sızdırmazlığıdır**; ve o artık yapısaldır
    # (`tools.okuyan_araclar` + `mcp.cagir`'in reddi).
    #
    # *Bir kapıyı bir şeyin YOKLUĞUNA bağlamak, o şey meşru olarak var olduğu gün kapıyı
    # bir engele çevirir.*
    yazanlar = {a.ad for a in tools.hepsi() if a.yan_etki == "yazar"}
    listede = {a["name"] for a in mcp.araclar(None)}
    assert not (yazanlar & listede), (
        f"🔴 YAZAN araç MCP yüzeyinde: {sorted(yazanlar & listede)}. MCP bir ÇEVİRİDİR "
        "ve salt-okumadır; ajanın yazma yetkisi ayrı bir mimari karardır (MIMARI §4).")


def test_MCP_cagrisi_AYNI_makbuzu_uretir():
    """🔴 **Jenerik MCP sunucularında olmayan fark:** her çağrı bir **adım kaydı** üretir.

    Ve o kayıt HTTP yolundakiyle **aynı alanları** taşır — ayrışırlarsa iki yüzey aynı
    koşumu farklı anlatır ve denetçi hangisine bakacağını bilemez.
    """
    plan_http = Planlayici(butce=Butce())
    plan_mcp = Planlayici(butce=Butce())

    # HTTP yolu: doğrudan `calistir`. MCP yolu: `mcp.cagir` → aynı `calistir`.
    for p in (plan_http,):
        with pytest.raises(KeyError):
            p.calistir("uydurma_arac")
    r = mcp.cagir(plan_mcp, "uydurma_arac", {})

    assert r["isError"] is True, "kayıtsız araç MCP'de de REDDEDİLMELİ (fail-closed)"
    assert "uydurma_arac" in r["content"][0]["text"]
    # ⚠ Hata **yutulmadı**: `calistir` KeyError'ı adım kaydına ulaşmadan attığı için
    # `_meta.makbuz` boş olabilir; boş olması gizlemek DEĞİLDİR — kayıt kapısı adımın
    # hiç başlamadığını söyler.
    assert "_meta" in r


def test_MCP_makbuzu_ADIM_alanlarini_tasir():
    """Gerçek bir araç: makbuz **araç · determinizm · süre**'yi taşımalı."""
    plan = Planlayici(butce=Butce())
    r = mcp.cagir(plan, "route", {"q": "", "schema": {"cubes": []}})
    m = r["_meta"]["makbuz"]
    assert m is not None, (
        "🔴 MCP çağrısı makbuz ÜRETMEDİ — jenerik bir MCP sunucusundan farkımız buydu.")
    for alan in ("arac", "determinizm", "sure_ms"):
        assert alan in m, f"makbuzda `{alan}` yok — HTTP yolundaki `Adim` ile ayrışmış"
    assert m["arac"] == "route"
    # Ve aynı adım `Planlayici.kosum`'da da duruyor: iki temsil DEĞİL, tek kayıt.
    assert plan.kosum.adimlar[-1].arac == "route"


def test_bayrak_KAPALIYKEN_uc_404(monkeypatch):
    """`GERİ AL`: `mcp_yuzeyi=off` → uç yok, HTTP yolu **etkilenmez**."""
    from fastapi import HTTPException

    from app.routers import mcp as router_mcp

    class _İstek:
        class state:                                     # noqa: N801
            principal = None

    monkeypatch.setattr("app.features.resolve_for", lambda *a, **k: set())
    with pytest.raises(HTTPException) as e:
        router_mcp._acik_mi(_İstek())
    assert e.value.status_code == 404


def test_bayrak_ACIKKEN_arac_listesi_gelir(monkeypatch):
    from app.routers import mcp as router_mcp

    class _İstek:
        class state:                                     # noqa: N801
            principal = None

    monkeypatch.setattr("app.features.resolve_for", lambda *a, **k: {"mcp_yuzeyi"})
    r = router_mcp.tools_list(_İstek())
    assert r["tools"] and all(mcp.SEMA_ALANI in a for a in r["tools"])
