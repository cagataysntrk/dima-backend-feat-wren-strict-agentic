"""KAPI — doğrulama maliyetini işin boyutuna göre ölçekler.

## Neden bu araç var

Tam süit + `eval` + korpus + senaryo ≈ **15 dakika**. Bu bir faz kapısı olarak doğru,
ama her düzenlemeden sonra koşturulunca geliştirmenin kendisini yavaşlatıyor (ölçüldü:
bir fazda üç kez koşturuldu → 45 dakika, ve üçünün ikisi hiçbir şey bulmadı).

Çözüm **daha az doğrulama** değil, **doğru zamanda doğru doğrulama**:

| Seviye | Ne koşar | Ne zaman |
|---|---|---|
| `--hizli` | değişen modüle **bağımlı** test dosyaları + çekirdek duman | geliştirme sırasında |
| `--tam` | süit + `eval` + korpus + senaryo | **faz sonunda, bir kez** |

## `--hizli` bir KAPI DEĞİLDİR — bir SİNYALDİR

Seçim `import` bağımlılığına bakar; bir modülü **adıyla anmayan** ama davranışına
dayanan bir test kaçabilir. Bu yüzden araç her koşumda **kapsanmayan dosya sayısını
yazar** — bu deponun *"sessiz kırpma yok"* disiplini ölçüm aracının kendisine de
uygulanır (MIMARI §6.4: *"ölçüm aracının kendisi de bir bağımlılıktır"*).

Yalnız `--tam` bir kapıdır. Commit öncesi o koşar.

## Kullanım

    # host'ta değişen dosyaları git verir, konteyner yalnız koşar
    python lab/kapi.py --hizli --degisen app/eylem.py tests/test_eylem_onayi.py
    python lab/kapi.py --tam
"""

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys

KOK = pathlib.Path(__file__).resolve().parents[1]
TESTLER = KOK / "tests"

#: ÇEKİRDEK DUMAN — değişiklik neye dokunursa dokunsun koşan, ucuz ve geniş kapsamlı
#: dosyalar. Merdivenin her basamağından en az bir tanık: deterministik route, takip
#: yolu, mühür/gizlilik, cevap alanlarının yetim olmaması.
CEKIRDEK = (
    "test_cube_router.py",              # deterministik basamak
    "test_ask_golden.py",               # uçtan uca altın yol
    "test_takip_ucuncu_sinif.py",       # takip/konuşma yolu
    "test_cevap_alani_yetim_degil.py",  # cevap alanlarının tüketicisi var mı
)


def _modul_adlari(degisen: list[str]) -> set[str]:
    """Değişen kaynak dosyalardan aranacak modül adları.

    `app/routers/ask.py` → {"ask", "app.routers.ask", "routers.ask"} — üçü de gerçek
    bir testte geçebilecek biçimlerdir; hangisinin kullanıldığını tahmin etmek yerine
    hepsi aranır (yanlış-pozitif seçim yalnız biraz daha çok test koşturur, yanlış-
    negatif ise sessizce kapsam kaybettirir — asimetri seçimi belirler).
    """
    adlar: set[str] = set()
    for d in degisen:
        p = pathlib.PurePosixPath(d)
        if p.suffix != ".py" or p.name == "__init__.py":
            continue
        parcalar = [x for x in p.parts if x not in ("backend", ".")]
        if not parcalar or parcalar[0] not in ("app", "control_plane", "lab"):
            continue
        adlar.add(p.stem)
        adlar.add(".".join([*parcalar[:-1], p.stem]))
    return adlar


def _secim(degisen: list[str]) -> tuple[list[str], int]:
    hepsi = sorted(f.name for f in TESTLER.glob("test_*.py"))
    secili = {f for f in CEKIRDEK if (TESTLER / f).exists()}
    # Değişen test dosyaları HER ZAMAN koşar (yeni yazdığım kapı en olası kırılan yer).
    for d in degisen:
        ad = pathlib.PurePosixPath(d).name
        if ad.startswith("test_") and (TESTLER / ad).exists():
            secili.add(ad)
    adlar = _modul_adlari(degisen)
    if adlar:
        desen = re.compile(r"\b(" + "|".join(re.escape(a) for a in sorted(adlar)) + r")\b")
        for ad in hepsi:
            if desen.search((TESTLER / ad).read_text(encoding="utf-8", errors="ignore")):
                secili.add(ad)
    return sorted(secili), len(hepsi)


def _kos(komut: list[str], baslik: str) -> int:
    print(f"\n{'=' * 78}\n▶ {baslik}\n{'=' * 78}", flush=True)
    return subprocess.call(komut, cwd=KOK)


def hizli(degisen: list[str]) -> int:
    secili, toplam = _secim(degisen)
    atlanan = toplam - len(secili)
    print(f"HIZLI KAPI · değişen={len(degisen)} → seçilen test dosyası "
          f"{len(secili)}/{toplam}")
    for s in secili:
        print(f"  · {s}")
    print(f"\n⚠ KAPSANMADI: {atlanan} test dosyası. Bu bir KAPI DEĞİL, bir SİNYALDİR — "
          f"seçim import bağımlılığına bakar, davranışa değil.\n"
          f"  Kapı: python lab/kapi.py --tam   (faz sonunda, commit'ten önce)")
    if not secili:
        return 0
    return _kos([sys.executable, "-m", "pytest", "-q", "-p", "no:warnings",
                 *[f"tests/{s}" for s in secili]], "pytest (seçili)")


def tam() -> int:
    adimlar = (
        ([sys.executable, "-m", "pytest", "-q", "-p", "no:warnings"], "tam süit"),
        ([sys.executable, "-m", "eval.run"], "eval.run"),
        ([sys.executable, "lab/nl_corpus.py", "--kapi"], "korpus kapısı"),
        ([sys.executable, "lab/konusma_senaryolari.py"], "konuşma senaryoları"),
    )
    kotu = 0
    for komut, baslik in adimlar:
        rc = _kos(komut, baslik)
        if rc != 0:
            print(f"✗ {baslik} BAŞARISIZ (rc={rc})")
            kotu = rc
    print("\n" + ("✓ FAZ KAPISI YEŞİL" if kotu == 0 else "✗ FAZ KAPISI KIRMIZI"))
    return kotu


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--hizli", action="store_true")
    ap.add_argument("--tam", action="store_true")
    ap.add_argument("--degisen", nargs="*", default=[],
                    help="değişen dosya yolları (host'ta `git status` verir)")
    a = ap.parse_args()
    if a.tam:
        return tam()
    if a.hizli:
        return hizli(a.degisen)
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
