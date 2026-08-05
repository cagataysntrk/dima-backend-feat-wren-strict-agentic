"""FAZ 5.12 kapısı — **İçgörü Paketi.** [bayrak: `ui_icgoru_paketi`]

Yol haritasının tek açık şartı: 🔴 **tekil dönüş KIRILMIYOR.**

`viz.recommend()` sözleşmesi `VizSpec | list[VizSpec]` oldu ama `paket=False`
(varsayılan) **bugünkü sözlüğü bayt bayt** döndürür. *Geriye uyumluluk bir vaat değil,
imzanın kendisidir.*

## 🔴 Yeni motor yazılmadı

Paketin her üyesi `recommend()`'in **zaten hesapladığı** bir karardan doğar
(`partition` · `pivot` · `facet_measure` · zaman ekseni). *İkinci bir görsel dilbilgisi,
birincinin kararlarını sessizce ezerdi.*
"""

from __future__ import annotations

import pytest

from app import viz


def _sonuc(n=5, zaman=False):
    if zaman:
        return {"columns": ["tarih", "makine", "fire"],
                "rows": [{"tarih": f"2026-{i + 1:02d}", "makine": f"M{i % 3}",
                          "fire": i + 1} for i in range(n)]}
    return {"columns": ["makine", "fire"],
            "rows": [{"makine": f"M{i}", "fire": i + 1} for i in range(n)]}


def test_TEKIL_DONUS_KIRILMIYOR():
    """🔴 Yol haritasının tek açık şartı."""
    tek = viz.recommend(_sonuc(), {"fire": "kg"})
    assert isinstance(tek, dict), f"tekil dönüş bozuldu: {type(tek)}"
    assert "kind" in tek and "measures" in tek
    # ⚠ Ve `neden` alanı tekil dönüşe **SIZMAZ**: bayrak kapalıyken sözleşme bugünküdür.
    assert "neden" not in tek, (
        "🔴 Paket alanı tekil dönüşe sızdı — 'bayt bayt aynı' vaadi kırık.")


def test_PAKET_liste_doner_ve_HER_UYE_gerekce_tasir():
    """*Bir paket üyesi neden orada olduğunu söyleyemiyorsa, o üye gürültüdür.*"""
    pk = viz.recommend(_sonuc(), {"fire": "kg"}, paket=True)
    assert isinstance(pk, list) and pk
    for uye in pk:
        assert uye.get("neden"), f"gerekçesiz paket üyesi: {uye.get('kind')}"
        assert len(str(uye["neden"])) > 20, "gerekçe bir etiket değil, bir CÜMLE olmalı"


def test_PAKETIN_ILK_UYESI_tekil_kararla_AYNI():
    """⚠ Paket bir **ek**tir, bir **yeniden karar** değil.

    İlk üye tekil kararın kendisi olmazsa, bayrağı açmak kullanıcının bugün gördüğü
    grafiği **sessizce değiştirirdi**.
    """
    tek = viz.recommend(_sonuc(), {"fire": "kg"})
    pk = viz.recommend(_sonuc(), {"fire": "kg"}, paket=True)
    assert pk[0]["kind"] == tek["kind"]
    assert pk[0]["measures"] == tek["measures"]
    assert pk[0]["dims"] == tek["dims"]


def test_AZAMI_UC_uye():
    """⚠ *Üçten fazlası bir paket değil bir **yığın**dır* — kullanıcı hangisine bakacağını
    bilemez ve paket, tek kartın yaptığı işi de bozar."""
    assert viz._MAX_PAKET == 3
    pk = viz.recommend(_sonuc(6, zaman=True), {"fire": "kg"}, paket=True)
    assert len(pk) <= 3


def test_CIZILMEZ_karari_EZILMEZ():
    """🔴 §15.6 *"grafik çizilmez"* dediyse paket **tek üyeli** kalır.

    Aksi hâlde *"bu veri grafiğe uygun değil"* diyen bir karar, **üç grafik önererek
    kendi kendini çürütürdü**.
    """
    # 3 kategori × tek ölçü → FAZ 5.11 kural 2 → `cumle`
    pk = viz.recommend(_sonuc(3), {"fire": "kg"}, paket=True)
    assert isinstance(pk, list) and len(pk) == 1, (
        f"🔴 Çizilmeme kararı ezildi: {[u['kind'] for u in pk]}")
    assert pk[0]["kind"] == "cumle"
    assert pk[0]["neden"] == pk[0]["cizilmedi"], (
        "gerekçe, çizilmeme sebebinin kendisi olmalı — ikinci bir açıklama uydurulmaz")


def test_BOS_sonucta_paket_YOK():
    assert viz.recommend(None, paket=True) is None
    assert viz.recommend({"columns": [], "rows": []}, paket=True) is None


def test_YENI_MOTOR_yazilmadi():
    """⚠ Belirteç **AST**: `paket_ac` yeni bir analiz yapmamalı — yalnız `recommend`'in
    ürettiği `spec`i **seçip çoğaltmalı**."""
    import ast
    from pathlib import Path

    agac = ast.parse((Path(__file__).resolve().parents[1] / "app/viz.py")
                     .read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "paket_ac")
    cagrilar = {getattr(c.func, "id", getattr(c.func, "attr", ""))
                for c in ast.walk(fn) if isinstance(c, ast.Call)}
    for yasak in ("analyze", "recommend", "_card", "_additive"):
        assert yasak not in cagrilar, (
            f"🔴 `paket_ac` `{yasak}` çağırıyor — ikinci bir görsel dilbilgisi doğmuş ve "
            f"birincinin kararlarını sessizce ezebilir.")


def test_NEDEN_karardan_TURETILIR():
    """*Gerekçeyi kararın kendisinden ayırmak, ikisini zamanla ayrıştırır.*"""
    zaman = viz.recommend(_sonuc(8, zaman=True), {"fire": "kg"}, paket=True)
    assert any("zaman" in str(u["neden"]).lower() for u in zaman)


@pytest.mark.parametrize("n", [4, 5, 8])
def test_paket_her_zaman_EN_AZ_bir_uye(n):
    pk = viz.recommend(_sonuc(n), {"fire": "kg"}, paket=True)
    assert isinstance(pk, list) and len(pk) >= 1


def test_BAYRAK_kayitli_ve_KAPALI():
    from pathlib import Path

    import yaml

    from app.features import FLAG_REGISTRY

    assert "ui_icgoru_paketi" in FLAG_REGISTRY
    d = yaml.safe_load((Path(__file__).resolve().parents[1] / "demo/packs/features.yml")
                       .read_text(encoding="utf-8"))
    assert d["features"]["ui_icgoru_paketi"] == "off"
