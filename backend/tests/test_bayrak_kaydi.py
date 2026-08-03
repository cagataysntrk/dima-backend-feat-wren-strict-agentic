"""FAZ 9.11 — BU OTURUMUN ALTI FAZI YÖNETİM YÜZEYİNDE ADSIZDI.

## Ölçülen kusur (denetim, Faz 9)

`demo/packs/features.yml`'de **13** bayrak vardı, `app.features.FLAG_REGISTRY`'de **9**.
Eksik altısı — `adhoc_cube` · `liste_niyeti` · `llm_sema_kisitli` · `prompt_enhancer` ·
`agent_plan_secimi` · `t2_anlatici` — admin panelinde açıklamasız `snake_case` ve kategori
*"Diğer"* olarak görünüyordu (`admin_app/routers/features.py` etiketi kayıttan okur,
yoksa anahtarın kendisini gösterir).

Hepsi **KURAL B** bayrağıdır: *"canlı cevap yolunu değiştiren her faz kendi kapatma
bayrağını taşır."* Ama bir kill-switch yalnız KOD'da varsa **yarımdır** — onu açacak ya da
acil durumda kapatacak kişi ne yaptığını **okuyabilmelidir**.

> Kayıt bir dekor değil, kill-switch'in **kullanılabilir** yarısıdır.
"""

from __future__ import annotations

import pathlib

import yaml

from app.features import FLAG_REGISTRY, STAGES

KOK = pathlib.Path(__file__).resolve().parents[1]


def _yaml_bayraklari() -> dict:
    veri = yaml.safe_load((KOK / "demo" / "packs" / "features.yml").read_text(
        encoding="utf-8")) or {}
    return veri.get("features") or veri


def test_YAMLDAKI_HER_bayrak_KAYITTA_var():
    eksik = sorted(set(_yaml_bayraklari()) - set(FLAG_REGISTRY))
    assert not eksik, (
        f"admin panelinde ADSIZ bayrak(lar): {eksik} — açıklamasız `snake_case`, "
        "kategori 'Diğer'. Bir kill-switch yalnız KOD'da varsa yarımdır.")


def test_KAYITTAKI_her_bayragin_UC_ALANI_dolu():
    eksik = [k for k, v in FLAG_REGISTRY.items()
             if not (v.get("label") and v.get("description") and v.get("category"))]
    assert not eksik, f"kaydı yarım bayrak(lar): {eksik}"


def test_HICBIR_bayrak_DIGER_kategorisinde_degil():
    """*"Diğer"* kaydın YOKLUĞUNUN göstergesidir; kayıtta açıkça yazılmışsa kayıt
    okunamaz bir çöplüğe döner."""
    kotu = [k for k, v in FLAG_REGISTRY.items() if v.get("category") == "Diğer"]
    assert not kotu, f"'Diğer' kategorili bayrak(lar): {kotu}"


def test_KAYITTA_olup_YAMLDA_olmayanin_GEREKCESI_var():
    """Ters yön de sessiz kalmamalı. `ask_async_discovery`/`threaded_chat` **bilerek**
    YAML'a konmadı (varsayılan davranışı değiştirmesinler) ve bu, kaydın kendi
    açıklamasında yazılı. Gerekçesiz bir sapma, kaydı yanıltıcı yapar."""
    fazla = set(FLAG_REGISTRY) - set(_yaml_bayraklari())
    for k in sorted(fazla):
        aciklama = FLAG_REGISTRY[k]["description"].lower()
        assert "eklenmedi" in aciklama or "bilerek" in aciklama, (
            f"`{k}` kayıtta var, YAML'da yok ve GEREKÇESİ yazılmamış — okuyucu bunu "
            "eksiklik mi karar mı sanacağını bilemez")


def test_ADMIN_UCU_kaydi_GERCEKTEN_okuyor():
    """Kayıt bir tüketicisi olmadan dekordur — bu deponun `test_uc_yetim_degil` disiplini."""
    import inspect

    from admin_app.routers import features as fmod

    govde = inspect.getsource(fmod.list_features)
    for alan in ("label", "description", "category"):
        assert f'"{alan}"' in govde, f"admin ucu `{alan}` alanını servis etmiyor"
    assert "FLAG_REGISTRY" in inspect.getsource(fmod._registry)


def test_YAML_asamalari_GECERLI():
    kotu = {k: v for k, v in _yaml_bayraklari().items() if v not in STAGES}
    assert not kotu, f"geçersiz aşama: {kotu} (geçerli: {STAGES})"
