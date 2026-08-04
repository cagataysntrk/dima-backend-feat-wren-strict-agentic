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
    assert "llm_araclari" in _adlar(_MCP), (
        "🔴 MCP araç listesi `tools.llm_araclari()`'ndan gelmiyor — yetki süzgeci ikinci "
        "kez yazılmış olabilir ve iki kopya AYRIŞIR.")


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
    m = {a["name"] for a in mcp.araclar(None)}
    l = {a["name"] for a in tools.llm_araclari(None)}
    assert m == l, f"MCP/LLM araç kümeleri ayrıştı: MCP−LLM={m - l}, LLM−MCP={l - m}"
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
    yazanlar = [a.ad for a in tools.hepsi() if a.yan_etki == "yazar"]
    assert not yazanlar, (
        f"🔴 Kayda yazan araç girmiş: {yazanlar}. MCP yüzeyi bir ÇEVİRİ olduğu için bu "
        f"araçlar oradan da çağrılabilir hâle geldi. FAZ 6.1'in onay kademesi inmeden "
        f"bu sınır gevşetilemez (MIMARI §4).")


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
