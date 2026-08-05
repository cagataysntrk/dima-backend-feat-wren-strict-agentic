"""FAZ 7.2 kapısı — **tasarım sistemi + karanlık mod.** [bayraksız: görsel regresyon]

## 🔴 TEŞHİS DÜZELTİLDİ

Sürüm 1 *"yalnız toggle eksik"* diyordu. **Ölçüldü ve teşhis EKSİKTİ**:
`prefers-color-scheme` **vardı** ama `data-theme` **0**, `.dark` **0**,
`@custom-variant dark` **0** — yani **sınıf-tabanlı katmanın kendisi yoktu** ve bir
toggle yazacak yer bulunamazdı.

## Kilitlenen dört karar

| # | Karar | Neden |
|---|---|---|
| 1 | `[data-theme]` blokları `@media`'den **SONRA** | *bir tercihi bir varsayımın altına koymak, tercihi yok saymaktır* |
| 2 | **İKİ YÖN** de yazılı (`dark` **ve** `light`) | tek yön: sistemi karanlık olan kullanıcı "açık" seçemez |
| 3 | **Üç durumlu** tema (`sistem` dahil) | ikiye indirmek *"karar vermedim"* hâlini yok eder |
| 4 | `"sistem"` seçilince öznitelik **silinir** | bırakılırsa CSS onu bir **karar** sanar |
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_FE = Path(__file__).resolve().parents[2] / "dima-frontend-demo-master"

pytestmark = pytest.mark.skipif(not _FE.exists(), reason="⊘ frontend ağacı yok")


def _css() -> str:
    return (_FE / "src/app/globals.css").read_text(encoding="utf-8")


def test_SINIF_TABANLI_katman_VAR():
    """🔴 Teşhisin düzeltilen yarısı: katmanın **kendisi** yoktu."""
    css = _css()
    assert ':root[data-theme="dark"]' in css, "🔴 `data-theme` katmanı yok"
    assert ':root[data-theme="light"]' in css, (
        "🔴 `light` yönü yok — sistemi karanlık olan bir kullanıcı 'açık' SEÇEMEZ ve "
        "toggle tek yönlü çalışır.")
    assert "@custom-variant dark" in css, "🔴 Tailwind `dark:` varyantı bağlanmamış"


def test_SIRA_BAGLAYICI_tercih_varsayimi_EZER():
    """🔴 *Bir tercihi bir varsayımın altına koymak, tercihi yok saymaktır.*

    `[data-theme]` blokları `@media (prefers-color-scheme)` **sonrasında** gelmeli;
    tersi sıra toggle'ı **çalışmıyor** gösterirdi.
    """
    css = _css()
    i_media = css.index("@media (prefers-color-scheme: dark)")
    i_attr = css.index(':root[data-theme="dark"]')
    assert i_attr > i_media, (
        "🔴 `[data-theme]` bloğu `@media`'den ÖNCE — sistem tercihi kullanıcının açık "
        "kararını ezer ve toggle çalışmıyor görünür.")


def test_IKINCI_MEKANIZMA_yok():
    """⚠ `.dark` sınıfı **ve** `[data-theme]` birlikte olsaydı, aynı kuralın iki sahibi
    olurdu."""
    css = _css()
    assert not re.search(r"^\s*\.dark\b", css, re.M), (
        "🔴 `.dark` sınıfı da tanımlanmış — aynı kuralın iki sahibi AYRIŞIR.")


def test_TOKEN_SETI_dolu():
    """Accent ölçeği · semantik renkler · grafik paleti · tipografi · radius/shadow."""
    css = _css()
    for tok in ("--accent-50", "--accent-900", "--positive", "--negative",
                "--chart-1", "--chart-8", "--text-3xs", "--text-2xl",
                "--radius-sm", "--shadow-1", "--opacity-disabled"):
        assert tok in css, f"🔴 token yok: {tok}"


def test_SEMANTIK_RENK_YON_bildirir_DEGER_degil():
    """🔴 `--positive`/`--negative` **yön** bildirir, değer değil.

    `lower_is_better` bir ölçüde **düşüş POZİTİFTİR**. Rengi doğrudan *"artış = yeşil"*
    diye bağlamak, **fire artışını kutlardı** — ve bu depoda o beyan `viz.py`'nin
    `lower_set`inde zaten var.
    """
    css = _css()
    assert "--positive" in css and "--negative" in css
    assert "lower_is_better" in css or "lower_set" in css, (
        "🔴 Rengin YÖNE bağlı olduğu CSS'te yazılı değil — bir gün biri 'artış = yeşil' "
        "diye bağlar ve fire artışı kutlanır.")


def test_KARANLIK_MODDA_semantik_renkler_de_DEGISIYOR():
    """⚠ Yalnız arka planı çevirmek yetmez: `#15803d` karanlık zeminde **okunmaz**."""
    css = _css()
    koyu = css[css.index(':root[data-theme="dark"]'):]
    koyu = koyu[:koyu.index("}")]
    for tok in ("--positive", "--negative", "--shadow-1"):
        assert tok in koyu, f"🔴 karanlık modda `{tok}` güncellenmiyor"


# --- TEMA TERCİHİ: ÜÇ DURUM ----------------------------------------------------------

def _tema_ts() -> str:
    return (_FE / "src/lib/tema.ts").read_text(encoding="utf-8")


def test_UC_DURUM_var():
    """🔴 İkiye indirmek *"karar vermedim"* hâlini **yok ederdi**: ilk açılışta bir
    varsayılan seçmek zorunda kalırdık ve o varsayılan, kullanıcının sistem tercihini
    **sessizce ezerdi**."""
    ts = _tema_ts()
    assert '"sistem" | "light" | "dark"' in ts


def test_SISTEM_secilince_oznitelik_SILINIR():
    """🔴 Öznitelik bırakılırsa CSS o değeri bir **karar** sanar ve `prefers-color-scheme`
    bir daha **hiç** devreye girmez. *"Karar vermedim" ile "açık seçtim" aynı şey
    değildir.*"""
    ts = _tema_ts()
    assert "removeAttribute" in ts and "removeItem" in ts, (
        "🔴 `sistem` seçilince öznitelik/kayıt silinmiyor — sistem tercihi bir daha "
        "devreye girmez.")


def test_BOZUK_deger_SISTEME_duser():
    """⚠ Bozuk bir `localStorage` değeri, kullanıcıyı **okuyamadığı** bir temaya
    kilitlememeli."""
    ts = _tema_ts()
    assert 'v === "light" || v === "dark" ? v : "sistem"' in ts


def test_FOUC_sinirini_GIZLEMIYOR():
    """⚠ *Burada çözülmüş gibi yapılmıyor* — sınır yazılı."""
    assert "FOUC" in _tema_ts()


def test_TOGGLE_yeni_PANEL_acmadi():
    """K5 tavanı 13/13 — *bir yetenek bir panel doğurmaz*."""
    fc = (_FE / "src/components/FloatingControls.tsx").read_text(encoding="utf-8")
    assert "TemaDugmesi" in fc, "🔴 tema düğmesi ikon şeridinde değil"
    assert not (_FE / "src/components/TemaPanel.tsx").exists(), (
        "🔴 Tema için AYRI bir panel açılmış — bir yetenek bir panel doğurmaz.")
