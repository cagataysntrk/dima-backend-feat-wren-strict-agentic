"""🔴 `G6` — **FRONTEND DERLENİYOR MU?** Ölçülen kusur: HAYIR, iki demettir derlenmiyordu.

## Nasıl görünmedi

`G1` `Temellendirme.tsx`'i, `G2` `DiyalogDurumu.tsx`'i ekledi. İkisi de commit edildi,
ikisi de **derlenmiyordu**:

| dosya | hata | sınıf |
|---|---|---|
| `ReportCard.tsx` | `TS1005: ')' expected` | 🔴 iki kardeş JSX elemanı **fragment'sız** |
| `DiyalogDurumu.tsx` · `Temellendirme.tsx` | `TS2305: no exported member 'AskItem'` | var olmayan tip adı |
| `DiyalogDurumu.tsx` | `TS7006: implicitly 'any'` | strict ihlali |

Kapı bunların **hiçbirini** göremezdi: yerel kapı yalnız `pytest` koşuyor ve bu operasyonda
`tsc` **hiç çağrılmadı**. Yani frontend bir demet boyunca **denetimsizdi** ve testler
yeşildi. *Bir dilin derleyicisi koşulmuyorsa, o dilde yazılan her şey denetimsizdir.*

⚠ Ve bu, deponun kendi defterindeki desenin tekrarı: *"kullanılamayan kapı kapatılır ve o
zaman hiç yoktur."* Burada kapı kapatılmamıştı bile — **hiç açılmamıştı**.

## İki katman, çünkü test imajında `node` YOK

1. **Yapısal denetim** — saf metin, her yerde koşar. `@/lib/types`'tan alınan her tip adı
   gerçekten dışa aktarılmış mı? `AskItem` kusurunu **tam olarak** bu yakalardı.
2. **`tsc --noEmit`** — `npx` varsa koşar, yoksa `skip`. Konteynerde atlanır, geliştirici
   makinesinde ve node'lu bir CI'da **tam** denetim yapar.

🔴 Birincisi ikincisinin **yerini tutmaz**; ikincisi olmadığında hiç olmamasından iyidir.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

_FRONT = Path(__file__).resolve().parents[2] / "dima-frontend-demo-master"
_SRC = _FRONT / "src"
_TYPES = _SRC / "lib" / "types.ts"

pytestmark = pytest.mark.skipif(not _SRC.is_dir(), reason="⊘ frontend ağacı mount edilmemiş")

_IMPORT_RE = re.compile(r'import\s+type\s*\{([^}]+)\}\s*from\s*"@/lib/types"')
_EXPORT_RE = re.compile(r"^export\s+(?:interface|type|const|enum)\s+(\w+)", re.M)


def _dosyalar() -> list[Path]:
    return sorted(p for p in _SRC.rglob("*.tsx") if "node_modules" not in p.parts)


def test_TIP_ADLARI_GERCEKTEN_VAR():
    """🔴 `@/lib/types`'tan alınan her ad **dışa aktarılmış** olmalı.

    `G1` ve `G2` `AskItem` diye bir tip aldı — öyle bir tip **yok** (doğrusu
    `AskResponse`). İki dosya iki demet boyunca derlenmedi ve hiçbir test bunu görmedi:
    Python kapısı TypeScript okumaz.
    """
    disa_aktarilan = set(_EXPORT_RE.findall(_TYPES.read_text(encoding="utf-8")))
    assert disa_aktarilan, "⊘ types.ts okunamadı — ölçüm tabanı çöktü"

    eksik: list[str] = []
    for p in _dosyalar():
        for blok in _IMPORT_RE.findall(p.read_text(encoding="utf-8")):
            for ad in (a.strip().split(" as ")[0].strip() for a in blok.split(",")):
                if ad and ad not in disa_aktarilan:
                    eksik.append(f"{p.name}: {ad}")
    assert not eksik, ("🔴 var olmayan tip adı içe aktarılmış (dosya DERLENMEZ):\n  "
                       + "\n  ".join(eksik))


def test_TSC_TEMIZ():
    """🔴 Tam denetim. `npx` yoksa **atlanır** — test imajında `node` yok, ama bu bir
    mazeret değil bir **sınırdır**: geliştirici makinesinde ve node'lu bir CI'da koşar.

    ⚠ `--no-install`: ağ yok, yalnız yerel `node_modules`. Kurulu değilse `skip` —
    *var olmayan bir aleti çağırmak, kapıyı sahte kırmızıya boğar.*
    """
    if not shutil.which("npx") or not (_FRONT / "node_modules" / ".bin" / "tsc").exists():
        pytest.skip("⊘ node/tsc yok (test imajı) — yapısal denetim geçerli")
    r = subprocess.run(["npx", "--no-install", "tsc", "--noEmit", "-p", "tsconfig.json"],
                       cwd=_FRONT, capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, ("🔴 frontend DERLENMİYOR:\n"
                               + "\n".join(r.stdout.splitlines()[:20]))


def test_KOSULLU_JSX_TEK_KOK():
    """🔴 `TS1005` sınıfı — `{koşul && ( … )}` içinde **iki kardeş** eleman.

    `G2` `<DiyalogDurumu>`'yu `<NextStepChips>`'in yanına fragment'sız koydu ve dosya
    derlenmez oldu. Bu denetim kaba ama **ucuz**: koşullu bloğun ilk satırından sonra
    aynı girintide ikinci bir `<Bileşen` başlıyorsa sarmalayıcı yoktur.

    ⚠ Yalnız **büyük harfle başlayan** bileşenler ve `<>` sayılır.

    ⚠ İlk yazım **beş yanlış-pozitif** verdi (`tsc` temizken): sarmalayıcıyı görmüyor,
    iç içe çocukları kardeş sanıyordu. Doğru ölçüt **girinti**dir: bloğun ilk elemanının
    girintisi kök girintidir; o girintide **ikinci** bir eleman varsa kök tek değildir.
    İç içe çocuklar daha derin girintilidir, `<>` sarmalayıcısı da bir eleman değildir.
    *Kullanılamayan bir kapı kapatılır — ve yanlış-pozitif veren bir kapı kullanılamaz.*
    """
    kusurlu: list[str] = []
    for p in _dosyalar():
        satirlar = p.read_text(encoding="utf-8").splitlines()
        for i, l in enumerate(satirlar):
            if not re.search(r"&&\s*\($", l.strip()):
                continue
            kok_girinti = None
            kardes = 0
            for s in satirlar[i + 1:i + 40]:
                if not s.strip():
                    continue
                girinti = len(s) - len(s.lstrip())
                if kok_girinti is None:
                    kok_girinti = girinti
                if girinti < kok_girinti:
                    break                       # blok bitti
                if girinti == kok_girinti and re.match(r"<([A-Z]\w*|>)", s.strip()):
                    kardes += 1
            if kardes >= 2:
                kusurlu.append(f"{p.name}:{i + 1}")
    assert not kusurlu, ("🔴 koşullu JSX'te sarmalayıcısız kardeş eleman (TS1005):\n  "
                         + "\n  ".join(kusurlu))


def test_MARKDOWN_ISARETI_YORUMLANIYOR():
    """🔴 `DA-8` — **backend markdown yazıyor, ekranda yorumlayıcı YOKTU.**

    Kullanıcıya giden metinler `**kalın**` taşıyor (`app/yetenek.py` · `app/uyum.py` ·
    `app/soz.py`) ve not blokları düz metin basıyordu: kullanıcı **yıldızları okuyordu**.

    *Bir vurgu işareti, yorumlanmadığında vurgunun tersini yapar: gözü tam da kritik
    kelimeden kaçırır.*

    Bu kapı iki yönü birden tutar: (1) backend gerçekten `**` üretiyor mu — üretmiyorsa
    kapı bir hayaleti korumaktadır ve düşmeli; (2) o metni basan yüzey `vurgula`'dan
    geçiyor mu.
    """
    import pathlib

    kok = pathlib.Path(__file__).resolve().parents[1] / "app"
    uretenler = [p.name for p in (kok / "yetenek.py", kok / "uyum.py", kok / "soz.py")
                 if p.exists() and "**" in p.read_text(encoding="utf-8")]
    if not uretenler:
        pytest.skip("⊘ backend artık `**` üretmiyor — kapı konusuz")

    vurgu = _SRC / "lib" / "vurgu.tsx"
    assert vurgu.exists(), (
        f"🔴 {uretenler} `**` üretiyor ama `src/lib/vurgu.tsx` yok — kullanıcı ham "
        "yıldız okuyor.")

    kart = (_SRC / "components" / "ReportCard.tsx").read_text(encoding="utf-8")
    assert "vurgula(item.soz || item.note)" in kart, (
        "🔴 not bloğu `vurgula`'dan geçmiyor — `**` ham basılır")
    assert "whitespace-pre-line" in kart, (
        "🔴 not bloğunda satır sonu korunmuyor — `\\n\\n` paragrafları tek satıra çöker")


def test_TSC_GECELIK_CIDA_KOSUYOR():
    """🔴 `K3`'ün açık borcu — **kapandı ve burada kilitlendi.**

    `test_TSC_TEMIZ` konteynerde `npx` bulamayınca `skip` eder; yani o test **tek başına**
    hiçbir şeyi garanti etmez. Garantiyi veren şey, `tsc`'nin **bir yerde gerçekten
    koşuyor** olmasıdır.

    ⊙ Ölçülen kusur: `tsc` bu depoda **hiç koşmamıştı**. Frontend `G1`'den beri
    derlenmiyordu (4 hata) ve Python süiti yeşildi — çünkü Python kapısı TypeScript okumaz.

    *Bir dilin derleyicisi koşulmuyorsa, o dilde yazılan her şey denetimsizdir.*

    ⚠ Ve iş **ayrı** olmalı: `kapi` işine eklemek node kurulumunu Python kapısının önüne
    koyardı — frontend kurulumu çökerse ölçüm kapıları hiç koşmazdı.
    *Bir kapının çökmesi, öteki kapının ölçümünü engellememelidir.*
    """
    import pathlib

    wf = (pathlib.Path(__file__).resolve().parents[2]
          / ".github/workflows/nightly.yml")
    if not wf.exists():
        pytest.skip("⊘ CI reçetesi mount edilmemiş")
    metin = wf.read_text(encoding="utf-8")
    assert "tsc --noEmit" in metin, (
        "🔴 `tsc` gecelik CI'da KOŞMUYOR — `test_TSC_TEMIZ` konteynerde atlandığı için "
        "TypeScript tarafı hiçbir yerde denetlenmez.")
    assert "frontend-tsc:" in metin, (
        "🔴 `tsc` ayrı bir iş değil — `kapi` işine gömülüyse frontend kurulumu çökünce "
        "ölçüm kapıları da koşmaz.")
