r"""🔴 `§F14`/`§F1` — **DOĞRUDAN İMPORT EDİLEN MOTOR PAKETİ BEYANSIZDI.**

`app/wren_service.py:1494,1733` `from wren_core import cube_query_to_sql` yazıyor, ama
`pyproject.toml` yalnız `wrenai>=0.13,<0.14` beyan ediyordu: `wren-core-py` **geçişli**
geliyordu. Raporun `:995` satırı ise *«`pyproject.toml` doğru tarafta (… +
`wren-core-py>=0.7.3`)»* diyordu — yani **dosya hakkında yanlış** bir cümle iki tur
boyunca bir ölçüm gibi okundu.

⚠ Neden önemli: geçişli bir bağımlılığa **doğrudan** import etmek, üst paket bir gün onu
bıraktığında **çözümleme anında değil, çalışma anında** kırılır — ve o gün hata mesajı
motorun kendisini işaret eder, bağımlılık beyanını değil.

> *Bir bağımlılığı yapılandırmadan çıkarmak, onu ortamdan çıkarmaz — yalnız görünmez
> yapar.*
"""

from __future__ import annotations

import ast
import pathlib
import re

_KOK = pathlib.Path(__file__).resolve().parents[1]


def _dogrudan_wren_importlari() -> set[str]:
    """`app/` içinde **doğrudan** import edilen üst düzey `wren*` paketleri."""
    bulunan: set[str] = set()
    for f in (_KOK / "app").rglob("*.py"):
        try:
            agac = ast.parse(f.read_text(encoding="utf-8"))
        except SyntaxError:                          # pragma: no cover
            continue
        for n in ast.walk(agac):
            if isinstance(n, ast.Import):
                bulunan |= {a.name.split(".")[0] for a in n.names}
            elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
                bulunan.add(n.module.split(".")[0])
    return {m for m in bulunan if m.startswith("wren")}


def _beyanlar() -> str:
    return (_KOK / "pyproject.toml").read_text(encoding="utf-8")


#: `import` adı → dağıtım (wheel) adı. **Kapalı** ve ölçülmüş: bir Python modülünün adı
#: paket adına eşit olmak zorunda değil (`wren_core` ↔ `wren-core-py`) — bu eşleşmeyi
#: tahmin etmek, olmayan bir beyanı var sanmaktır.
_DAGITIM = {"wren": "wrenai", "wren_core": "wren-core-py"}


def test_HER_DOGRUDAN_WREN_IMPORTU_BEYANLI():
    """🔴 **ASIL KAPI.**"""
    ithal = _dogrudan_wren_importlari()
    assert ithal, "⊘ ölçüm tabanı çöktü: `app/` altında hiç `wren*` importu bulunamadı"
    metin = _beyanlar()
    eksik = []
    for m in sorted(ithal):
        dagitim = _DAGITIM.get(m)
        assert dagitim, (
            f"🔴 `{m}` doğrudan import ediliyor ama dağıtım adı BİLİNMİYOR — `_DAGITIM`'a "
            "ölçülmüş karşılığıyla eklenmeli (tahmin edilmemeli).")
        if not re.search(rf'^\s*"{re.escape(dagitim)}[><=~!\s"]', metin, re.M):
            eksik.append(f"{m} → {dagitim}")
    assert not eksik, (
        f"🔴 BEYANSIZ DOĞRUDAN BAĞIMLILIK: {eksik}. Geçişli gelen bir pakete doğrudan "
        "import etmek, üst paket onu bıraktığı gün ÇALIŞMA ANINDA kırılır.")


def test_KURULU_SURUM_BEYANI_KARSILIYOR():
    """⚠ Beyan bir **aralıktır**; kurulu sürüm onun dışına düşerse beyan bir güvence
    değil bir süs olur. *Ölçülen* sürümle sınanır, varsayılanla değil."""
    import importlib.metadata as md

    try:
        s = md.version("wren-core-py")
    except md.PackageNotFoundError:                  # pragma: no cover
        import pytest
        pytest.skip("⊘ `wren-core-py` kurulu değil — ortam farkı, ürün kusuru değil")
    buyuk, kucuk = (int(x) for x in s.split(".")[:2])
    assert (buyuk, kucuk) >= (0, 7), (
        f"🔴 kurulu `wren-core-py` {s}, beyan `>=0.7.3` — beyan kurulu sürümü KARŞILAMIYOR.")
    assert buyuk == 0 and kucuk < 8, (
        f"🔴 kurulu `wren-core-py` {s} beyandaki `<0.8` tavanını AŞIYOR — beyan bayat.")
