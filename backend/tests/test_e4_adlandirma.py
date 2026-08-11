"""🔴 `§E4` — *«KÖK NEDEN»* BİR NEDENSELLİK İDDİASIDIR; BİZ **KATKI** ÖLÇÜYORUZ.

## Kartın tamamı

> *«Kök neden»* yerine **«katkı analizi»** kullanmayı değerlendir. Tableau kendi
> dokümanında: *«Correlation is not causation… **not a tool to prove or disprove
> hypotheses**»*. Gerçek nedensel iddia **nedensel graf beyanı** ister (DoWhy sınıfı) ve
> bizde **yok**; uydurmak `GG8`'i çiğner.
> ⊙ **İsimlendirme başlı başına bir yanıltma kaynağıdır.**

## Ölçüm (2026-08-12) — iddia NEREDE görünüyor

`grep` ile tarandı: arka uçta *«kök neden»* geçen her satır **yorum ya da docstring**;
kullanıcıya dönen tek bir metin yok. **Kullanıcının okuduğu iddia ön-uçtaydı:**

| yer | metin |
|---|---|
| `DrillDownPanel.tsx:146` | `aria-label="Kök nedeni incele"` |
| `DrillDownPanel.tsx:155` | başlık: **Kök nedeni incele** |
| `DrillDownPanel.tsx:278` | `ilişkili veri (kök neden adayı)` |

⊙ Yani kusur *«kodun her yerinde»* değil, **tam olarak üç satırda** — ve üçü de
kullanıcının gördüğü yüzeyde. *Bir yanıltmanın büyüklüğü kod içindeki sıklığıyla değil,
kaç kişinin okuduğuyla ölçülür.*

## Düzeltme — ad **ve** sınır

* `Kök nedeni incele` → **`Katkıyı incele`** (aria + başlık)
* `kök neden adayı` → **`katkı adayı`**
* 🔴 Ve asıl istenen: **sınır YAZILDI.** Panel açılır açılmaz okunan tek satır —
  *«Bu bir **katkı analizidir**: hangi kalemin farkın ne kadarını açıkladığını ölçer.
  **Nedensellik iddiası değildir** — birlikte değişmek, birinin ötekine sebep olduğunu
  göstermez.»*

⚠ Sınır **gizlenmiyor, küçültülmüyor, katlanmıyor**: `§F7`'nin dersi (*«bir sınırı bir
eksiklik gibi sunmak kullanıcının zamanını çalar»*) burada tersinden geçerli — bir
**yeteneği olduğundan fazla** sunmak da kullanıcının güvenini çalar.

## Neden bu testi ARKA UÇTA tutuyoruz

Bu depoda ön-uç metni için ayrı bir kapı koşumu yok; `tests/test_frontend_buyume.py`
zaten ön-uç dosyalarını arka uç süitinden okuyor. Aynı kalıp: kapı **metnin yaşadığı
dosyayı** okur. *Bir kapıyı, koşulmadığı bir yere koymak onu yazmamakla aynıdır.*
"""

from __future__ import annotations

import pathlib

_PANEL = (pathlib.Path(__file__).parent.parent.parent / "dima-frontend-demo-master"
          / "src" / "components" / "DrillDownPanel.tsx")


def _metin() -> str:
    return _PANEL.read_text(encoding="utf-8")


def test_PANEL_dosyasi_okunabiliyor():
    """⚠ Ön koşul: kapı gerçekten dosyayı buluyor mu. Bu oturumda bir prob **yanlış
    dizinden** koşup sahte bir sıfır üretti — kapının kendi zemini önce sınanır."""
    assert _PANEL.is_file(), f"panel bulunamadı: {_PANEL}"
    assert len(_metin()) > 1000


def test_NEDENSELLIK_IDDIASI_baslikta_YOK():
    """🔴 Kusurun ta kendisi: kullanıcı *«Kök nedeni incele»* okuyordu."""
    m = _metin()
    assert 'aria-label="Katkıyı incele"' in m
    assert "Kök nedeni incele" not in m, "nedensellik iddiası başlığa geri döndü"


def test_ILISKILI_VERI_etiketi_de_KATKI():
    """Aynı iddia ikinci bir yerde durmamalı — biri düzeltilip öteki unutulursa bu
    depoda *«kimlik asimetrisi»* denen kusur doğar."""
    m = _metin()
    assert "katkı adayı" in m
    assert "kök neden adayı" not in m


def test_SINIR_BEYANI_panelde_ve_ACIK():
    """🔴 `§E4`'ün asıl isteği ad değil **sınırın yazılı olması**. Tableau'nun kendi
    cümlesiyle aynı sınır."""
    m = _metin()
    assert "katkı analizidir" in m, "sınır beyanı yok"
    assert "Nedensellik iddiası değildir" in m
    # Beyan **panelin gövdesinde**, bir yorum satırında değil: kullanıcı okumalı.
    govde = m.split("aria-modal", 1)[1]
    assert "Nedensellik iddiası değildir" in govde, "beyan render edilen gövdede değil"


def test_ARKA_UCTA_kullaniciya_donen_kok_neden_METNI_YOK():
    """Ölçüldü: arka uçtaki her *«kök neden»* bir yorum/docstring. Bir gün kullanıcıya
    dönen bir metne sızarsa bu test konuşur."""
    import ast
    import re
    app = pathlib.Path(__file__).parent.parent / "app"
    kacak: list[str] = []
    for p in app.rglob("*.py"):
        kaynak = p.read_text(encoding="utf-8")
        if not re.search(r"kök[- ]neden", kaynak, re.I):
            continue
        try:
            agac = ast.parse(kaynak)
        except SyntaxError:
            continue
        # ⚠ **Docstring'ler ELENİR** — ilk kaba yüklem onları da yakaladı ve dokuz
        # sahte kaçak üretti (bu turda aracın on altıncı yanılması). Bir docstring
        # kullanıcıya DÖNMEZ; dönen şey `return`/atama içindeki dizgedir.
        # ⚠ Düz döngü, kurgu DEĞİL: kurgudaki `for d in [n.body[0].value]` koşuldan
        # ÖNCE değerlendiriliyordu ve gövdesi `Try` olan bir düğümde patladı
        # (`AttributeError`). *Bir kurgunun kısalığı, değerlendirme sırasını gizler.*
        docstringler: set[int] = set()
        for n in ast.walk(agac):
            if not isinstance(n, (ast.Module, ast.FunctionDef,
                                  ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            ilk = n.body[0] if n.body else None
            if isinstance(ilk, ast.Expr) and isinstance(ilk.value, ast.Constant):
                docstringler.add(id(ilk.value))
        for n in ast.walk(agac):
            if not isinstance(n, ast.Constant) or not isinstance(n.value, str):
                continue
            if id(n) in docstringler or not re.search(r"kök[- ]neden", n.value, re.I):
                continue
            kacak.append(f"{p.name}:{n.lineno}: {n.value.strip()[:80]}")
    # ⚠ **KULLANICI METNİ OLMAYAN ÜÇ SINIF — adıyla ve gerekçesiyle muaf.** Bu ayrım
    # keyfî değil: `§E4`'ün derdi kullanıcıya **nedensellik vaat etmek**; bir izin ya da
    # yönetici açıklamasının okuyucusu kullanıcı değildir.
    #   · `plan_semasi` → **LLM İSTEMİ** (garsona *«kök nedene inmenin»* nasıl yapıldığı)
    #   · `features.py` → **yönetici paneli** bayrak açıklaması, cevap metni değil
    #   · `ask.py:§NB` → **iz satırı** (`trace`), geliştirici katmanı
    # *Bir muafiyet, sınıfı yazılmadan verilirse muafiyet değil bir delik olur.*
    MUAF = ("plan_semasi.py", "features.py")
    kacak = [x for x in kacak
             if not x.startswith(MUAF) and "§NB:" not in x]
    assert not kacak, (
        "🔴 kullanıcıya dönebilecek bir *«kök neden»* metni doğdu:\n  "
        + "\n  ".join(kacak)
        + "\n\nBiz KATKI ölçüyoruz; nedensel iddia nedensel graf beyanı ister (yok).")
