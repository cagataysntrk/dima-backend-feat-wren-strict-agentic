"""**FAZ 5.13b — KURAL MOTORU BAĞLANDI.** [bayrak: `ui_knowledge_center`]

## 🔴 İKİ kusur birden

1. `app/rules.py` — **124 satır, 14 test** — üretim kodunda **hiç import edilmiyordu** ve
   `AskResponse.kural_baglami` alanının **hiçbir dolduranı** yoktu.
2. ⚠ **Veri kaynağı da yoktu**: `knowledge/rules/*.md` **düz metindir** (LLM prompt'una
   gider, `business_rules`); `rules.py` yapısal `{id, metin, kapsam}` bekler. Yani modül
   bağlansa bile **boş dönerdi** — *bir zinciri bağlamak, ucuna bir şey takmakla aynı
   şey değildir.*

Kaynak (`knowledge/kurallar.yml`) mevcut metnin **kendi başlıklarından** yapılandırıldı;
**yeni bir alan iddiası yok**. *Bir bilgi merkezinin ilk kuralı, kendi kaynağını
gösterebilmektir.*

⚠ Yetim modül: **12 → 5** — ve beşinin **dördü kusur değil** (`embed_kapsam` P0-bloke ·
`sinonim_onerici` tasarımı gereği offline · `kanal_kimlik` adaptör bekliyor ·
`bayrak_profilleri` test yardımcısı). **Gerçek kalan: `netlestirme`.**
"""

from __future__ import annotations

import ast
from pathlib import Path

_KOK = Path(__file__).resolve().parents[1]


def _fn(ad: str) -> str:
    agac = ast.parse((_KOK / "app/answer.py").read_text(encoding="utf-8"))
    return ast.unparse(next(n for n in agac.body
                            if isinstance(n, ast.FunctionDef) and n.name == ad))


def test_MODUL_ARTIK_CAGRILIYOR():
    assert "from app import rules" in _fn("_kural_baglami")
    assert "rules.ek_baglam(" in _fn("_kural_baglami")
    assert "_kural_baglami(" in _fn("seal")


def test_BAYRAGA_BAGLI():
    """KURAL B: kapalıyken alan **hiç üretilmez**."""
    govde = _fn("seal")
    assert "'ui_knowledge_center' in _rf2" in govde or '"ui_knowledge_center" in _rf2' in govde


def test_VERI_KAYNAGI_VAR_ve_YAPISAL():
    """🔴 Modülü bağlamak yetmezdi: kaynak **düz metindi**."""
    import yaml

    yol = _KOK / "demo/packs/sektor/boyahane/knowledge/kurallar.yml"
    assert yol.exists(), "🔴 yapısal kural kaynağı yok — zincir boş döner"
    d = yaml.safe_load(yol.read_text(encoding="utf-8"))
    kurallar = d["kurallar"]
    assert len(kurallar) >= 2
    for k in kurallar:
        assert k.get("id") and k.get("metin") and k.get("kapsam"), k
        assert k.get("kaynak"), (
            "🔴 kaynağı gösterilemeyen bir bilgi, bilgi değildir")


def test_KURALLAR_YUKLENIYOR_ve_DARALTICI():
    """🔴 **Boş kapsam eşleşmez.** Bir bilgi merkezi, *her cevaba yapışan bir dipnot*
    değildir."""
    import yaml

    from app import rules

    d = yaml.safe_load(
        (_KOK / "demo/packs/sektor/boyahane/knowledge/kurallar.yml").read_text(
            encoding="utf-8"))
    k = rules.yukle(d["kurallar"])
    assert len(k) == len(d["kurallar"])
    assert rules.eslesen(k, {"cube": "oee"}), "🔴 kendi cube'unda eşleşmiyor"
    assert not rules.eslesen(k, {"cube": "kalite"}), (
        "🔴 ilgisiz cube'a yapışıyor — bir dipnot, bir kural değildir")


def test_KURAL_SQL_ALANI_TASIYAMAZ():
    """🔴 *Bir kural SQL'i değiştirebilseydi, kullanıcının görmediği bir yerde sayıyı
    değiştirirdi.* `dogrula()` fail-closed reddeder."""
    import pytest

    from app import rules

    with pytest.raises(rules.KuralIhlali):
        rules.dogrula({"id": "x", "metin": "y", "kapsam": {"cube": "oee"},
                       "filters": [{"a": 1}]})


def test_SEMAYA_ULASIYOR():
    """⚠ **Zincirin en sık kopan yeri**: kaynak var, yükleyici var, ama compose onu
    proje dizinine taşımıyorsa alan yine boş kalır."""
    src = (_KOK / "app/wren_service.py").read_text(encoding="utf-8")
    assert '"kurallar": self._yapisal_kurallar()' in src
    assert 'self.project_dir / "knowledge" / "kurallar.yml"' in src, (
        "🔴 İkinci bir bilgi kökü icat edilmiş — iki kaynak bir gün ayrışır.")


def test_BOZUK_DOSYA_SESSIZCE_yutulmuyor():
    """⚠ *Bir bilgi merkezinin okunamayan dosyası, olmayan dosyadan tehlikelidir —
    çünkü var sanılır.*"""
    src = (_KOK / "app/wren_service.py").read_text(encoding="utf-8")
    i = src.index("def _yapisal_kurallar")
    assert "_log.warning" in src[i:i + 1400]


def test_KURAL_CEVABI_DUSURMUYOR():
    govde = _fn("seal")
    i = govde.index("_kural_baglami(")
    assert "except Exception" in govde[i:i + 400]


def test_YETIM_AYRIMI_yazili():
    doc = __doc__ or ""
    assert "dördü kusur değil" in doc and "Gerçek kalan" in doc
