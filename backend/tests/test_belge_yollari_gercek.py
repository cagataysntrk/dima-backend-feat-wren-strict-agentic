"""🔴 `§81` — **CANLI BELGELERDE ANILAN YOL GERÇEKTEN VAR MI.**

## Neden

Yeni gelen bir geliştirici belgeyi **yol yol** okur: *«`app/oneri.py`'ye bak»* der ve
oraya gider. Yol yoksa iki şey birden kaybolur — aradığı dosya **ve** belgeye olan güveni.
Ve bu depoda o kusur **ölçüldü**: `belgeler/DOGRULUK.md` bir kapıyı
`test_f8_doğruluk_yayini.py` diye anıyordu (Türkçe **«ğ»** ile); gerçek dosya
`test_f8_dogruluk_yayini.py`. *Bir kapının adını yanlış yazmak, onu olmayan bir kapı
yapar.*

⊙ Kardeş kapı `test_belge_duzeni.py::test_INDEKS_kirik_bag_tasimaz` **yalnız indeksi** ve
yalnız markdown **bağlarını** (`[…](…)`) tarıyordu. Bu depoda yollar ağırlıkla **satır içi
kod** olarak anılıyor (`` `app/oneri.py` ``) ve **50 belgede yalnız 46** markdown bağı var
— yani asıl yüzey ölçülmüyordu ㉖.

## 🔴 Kapsam — ve neden bu kadarı 🆂

| sınıf | taranır mı | gerekçe |
|---|---|---|
| kök `*.md` · `belgeler/kilavuz` · `mimari` · `urun` · `00-INDEKS` | ✅ | **canlı**: bugünü anlatır |
| `backend/CLAUDE.md` · `MIMARI.md` · `README.md` · FE `CLAUDE.md` | ✅ | canlı |
| `belgeler/devir/` · `arsiv/` · `arastirma/` · `YYYY-AA-GG_*` | ⊘ | 🔒 **tarihsel kayıt** — o gün var olan bir dosyanın bugün olmaması **doğrudur**; düzeltmek kaydı **tahrif** olurdu |
| `belgeler/plan/*` | ⊘ | **gelecek kipi**: plan, henüz **yazılmamış** dosyaları adıyla anar (`DIMA-V1-YOL-HARITASI` 30+ test adı sayıyor) |
| `OPERASYON-DURUM.md` | ⊘ | **kapanmış** operasyonun günlüğü; içinde *«`app/merdiven.py` **bilerek yazılmadı**»* gibi **kasıtlı yokluk** kayıtları var — bir kararı «kırık bağ» sayamayız ㊸ |
| `wren/…` · `connector/…` | ⊘ | **kütüphane içi** (`site-packages/wren`) — repoda olmaması doğru ⑦ |

⚠ Yer tutucular (`*` · `<…>` · `{…}` · `NNNN` · `YYYY`) ve repo dışı yollar (`~/…`,
`/openapi.json`) **atlanır**: bunlar bir dosya değil bir **kalıp** anlatır.

⚠ Kökler **çoklu** çözülür — belgeler yolu kısaltarak anar: `routers/ask.py` aslında
`backend/app/routers/ask.py`'dir. Ölçüt bunu bilmezse **yanlış kırmızı** üretir ⑮ ve
gürültü üreten bir kapı, ilk kırmızısında güvenilirliğini kaybeder.
"""

from __future__ import annotations

import pathlib
import re

import pytest

_KOK = pathlib.Path(__file__).resolve().parents[2]

# ⚠ **ÖN KOŞUL TEK BİR DİZİNE BAKAMAZ** ⑯ — ölçüldü: standart test kabı `belgeler`i
# `/belgeler`e bağlıyor, yani `(_KOK/"belgeler").is_dir()` **doğru** çıkıyor ama kökün
# geri kalanı (`README.md` · `backend/`) orada **değil**. Tek koşullu ilk yazım bu yüzden
# `skipped` yerine **3 kırmızı** verdi. Kardeş kapı (`test_belge_duzeni`) aynı tuzağa
# iki parçalı bir koşulla çözüm bulmuştu; burada da öyle.
# *Bir ortamın «görünür» olması, aradığın her şeyin görünmesi demek değildir.*
pytestmark = pytest.mark.skipif(
    not ((_KOK / "belgeler").is_dir() and (_KOK / "README.md").exists()
         and (_KOK / "backend").is_dir()),
    reason="⊘ ÖLÇÜLEMEDİ — repo kökü görünmüyor; bu denetim kök mount ister: "
           '-v "$PWD:/repo" -w /repo/backend')

#: Satır içi kod olarak anılan yol (`` `app/oneri.py` ``).
_YOL = re.compile(r"`([^`\s]+\.(?:py|md|ts|tsx|yml|yaml|json|sh))`")

#: Bir dosya değil bir **kalıp** anlatan işaretler.
_KALIP = ("*", "<", "{", "NNNN", "YYYY", "?")

#: Belgelerin yolu **kısaltarak** anadığı kökler — en spesifik olan da dâhil.
_KOKLER = ("", "backend", "backend/app", "backend/demo", "belgeler",
           "backend/demo/wren-project", "backend/demo/wren-engine-proje/cubes",
           "dima-frontend-demo-master", "dima-frontend-demo-master/src")

#: 🔒 Taranmayan sınıflar — gerekçeleri modül şerhinde.
_DONMUS = ("belgeler/devir/", "belgeler/arsiv/", "belgeler/arastirma/", "belgeler/plan/",
           "OPERASYON-DURUM.md")

#: ⊘ **KÜTÜPHANE İÇİ** — repoda olmayacak, olmaması **doğru**. `wren` motoru bir Python
#: paketidir (`site-packages/wren`, `MIMARI §10`: *motor IN-PROCESS*); `connector/` de
#: onun içindedir. Bunları aramak, kütüphanenin kaynağını repoda beklemek olurdu ⑦.
_KUTUPHANE = ("wren/", "connector/")
_TARIHLI = re.compile(r"\d{4}-\d{2}-\d{2}_")


def _canli_belgeler() -> list[pathlib.Path]:
    # ⚠ Süzgeç **kök dosyalara da** uygulanır ⑯: ilk yazımda yalnız `belgeler/` altı
    # süzülüyordu ve `OPERASYON-DURUM.md` (kökte, kapanmış operasyonun günlüğü) taranmaya
    # devam ediyordu. *Bir kuralı iki koleksiyondan yalnız birine uygulamak, kuralı
    # uygulamamaktır.*
    out: list[pathlib.Path] = []
    for p in list(_KOK.glob("*.md")) + list((_KOK / "belgeler").rglob("*.md")):
        bagil = str(p.relative_to(_KOK))
        if bagil.startswith(_DONMUS) or _TARIHLI.search(bagil):
            continue
        out.append(p)
    for ek in ("backend/CLAUDE.md", "backend/MIMARI.md", "backend/README.md",
               "dima-frontend-demo-master/CLAUDE.md"):
        if (_KOK / ek).exists():
            out.append(_KOK / ek)
    return out


def _var_mi(yol: str) -> bool:
    return any((_KOK / k / yol).exists() for k in _KOKLER)


def _eksikler() -> dict[str, list[str]]:
    eksik: dict[str, list[str]] = {}
    for p in _canli_belgeler():
        metin = p.read_text(encoding="utf-8", errors="ignore")
        for m in _YOL.finditer(metin):
            y = m.group(1)
            if "/" not in y or y.startswith(("/", "~")) or any(t in y for t in _KALIP):
                continue
            if y.startswith(_KUTUPHANE):
                continue
            if not _var_mi(y):
                eksik.setdefault(str(p.relative_to(_KOK)), []).append(y)
    return {f: sorted(set(v)) for f, v in eksik.items()}


def test_CANLI_BELGEDE_OLMAYAN_YOL_ANILMIYOR():
    """🔴 **ASIL DEĞİŞMEZ.** Canlı bir belge, var olmayan bir dosyayı adıyla anmaz."""
    eksik = _eksikler()
    assert not eksik, (
        "🔴 canlı belgede bulunamayan yol(lar):\n"
        + "\n".join(f"   {f}: {v}" for f, v in sorted(eksik.items()))
        + "\n   → dosya taşındıysa **yolu düzelt**; yazım hatasıysa **adı düzelt**;\n"
          "     henüz yazılmamış bir şeyse o cümle bir **plana** aittir (`belgeler/plan/`),\n"
          "     tarihsel bir kayıtsa `denetim/`·`devir/` altına (oralar taranmaz).")


def test_ZIT_OLCUT_OLCUT_GERCEKTEN_ARIYOR():
    """🆃 Kapının kurbanı: hiçbir şey bulamayan bir ölçüt de yeşil kalırdı ⑮.

    Uydurma bir yol **bulunmamalı**, gerçek bir yol **bulunmalı** — ve kısaltılmış
    biçim (`routers/ask.py`) de çözülmeli, yoksa kapı yanlış kırmızı üretir.
    """
    assert not _var_mi("app/olmayan_dosya_xyz.py"), "🔴 ölçüt her yolu 'var' sayıyor"
    assert _var_mi("app/oneri.py"), "🔴 gerçek yol bulunamadı"
    assert _var_mi("routers/ask.py"), (
        "🔴 kısaltılmış yol çözülmüyor — belgeler yolu kısaltarak anar ve kapı "
        "bunu bilmezse **yanlış kırmızı** üretir")


def test_KAPSAM_DONMUS_BELGELERI_TARAMIYOR():
    """🆂 Kapsam **beyandır**: `devir/`·`arsiv/`·`arastirma/`·`plan/` ve tarih damgalı
    dosyalar taranmaz. Bir tarihsel kaydı *«düzeltmek»* onu **tahrif** etmektir; bir planı
    düzeltmek ise gelecek kipini silmektir."""
    taranan = {str(p.relative_to(_KOK)) for p in _canli_belgeler()}
    assert not [t for t in taranan if t.startswith(_DONMUS)], "🔴 donmuş sınıf taranıyor"
    assert not [t for t in taranan if _TARIHLI.search(t)], "🔴 tarih damgalı belge taranıyor"
    assert "belgeler/00-INDEKS.md" in taranan, "🔴 indeks kapsam dışı kalmış"
    assert "README.md" in taranan, "🔴 kök README kapsam dışı kalmış"
