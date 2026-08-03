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


def _desenler(degisen: list[str]) -> list[re.Pattern[str]]:
    """Değişen kaynak dosya → o modüle BAĞIMLILIĞI gösteren desenler.

    ## Neden sade ad ARANMAZ (ölçüldü, 3 Ağustos 2026)

    İlk sürüm `\bask\b` gibi sade modül adlarını da arıyordu. Sonuç: `app/routers/ask.py`
    değişince **67/137 dosya** seçildi (3,4 dk) — çünkü `ask` aynı zamanda
    `tests/conftest.py`'nin **yardımcı fonksiyonudur** ve neredeyse her testte geçer.
    Yani sinyal bağımlılık değil, **ad çakışmasıydı**.

    Artık yalnız **import-biçimli** eşleşme sayılır (`app.routers.ask`,
    `from app.routers import ask`, `from app import ask`). Bir modülü import etmeden
    yalnız HTTP ucundan tüketen test kaçabilir — bu bilinçli: `--hizli` bir kapı değil
    sinyaldir ve kapsanmayanı sayısıyla yazar.
    """
    desenler: list[re.Pattern[str]] = []
    for d in degisen:
        yol = pathlib.PurePosixPath(d)
        if yol.suffix != ".py" or yol.name == "__init__.py":
            continue
        parcalar = [x for x in yol.parts if x not in ("backend", ".")]
        if not parcalar or parcalar[0] not in ("app", "control_plane", "lab"):
            continue
        paket, stem = ".".join(parcalar[:-1]), yol.stem
        nokta = re.escape(f"{paket}.{stem}")
        desenler.append(re.compile(
            rf"{nokta}\b"                                        # app.routers.ask...
            rf"|from\s+{re.escape(paket)}\s+import\s+[^\n]*\b{re.escape(stem)}\b"
            rf"|import\s+{nokta}\b"))
    return desenler


def _secim(degisen: list[str]) -> tuple[list[str], int]:
    hepsi = sorted(f.name for f in TESTLER.glob("test_*.py"))
    secili = {f for f in CEKIRDEK if (TESTLER / f).exists()}
    # Değişen test dosyaları HER ZAMAN koşar (yeni yazdığım kapı en olası kırılan yer).
    for d in degisen:
        ad = pathlib.PurePosixPath(d).name
        if ad.startswith("test_") and (TESTLER / ad).exists():
            secili.add(ad)
    desenler = _desenler(degisen)
    if desenler:
        for ad in hepsi:
            metin = (TESTLER / ad).read_text(encoding="utf-8", errors="ignore")
            if any(dsn.search(metin) for dsn in desenler):
                secili.add(ad)
    return sorted(secili), len(hepsi)


def _kos(komut: list[str], baslik: str) -> int:
    print(f"\n{'=' * 78}\n▶ {baslik}\n{'=' * 78}", flush=True)
    return subprocess.call(komut, cwd=KOK)


#: Özete girecek satırın seçiciler — her aracın "sonuç" satırı farklı biçimde.
_OZET_ISARET = ("passed", "failed", "error", "baseline'a göre", "TOPLAM doğru-cube",
                "ÖLÇÜLEMEDİ", "sınıf ")


def _son_anlamli(cikti: str) -> str:
    """Bir aracın çıktısından ÖZETE girecek satır(lar). Bulunamazsa son dolu satır —
    sessizce boş bırakmaktan iyidir (boş özet 'ölçüm yok'u 'sorun yok' gibi gösterir)."""
    satirlar = [s.strip() for s in cikti.splitlines() if s.strip()]
    isaretli = [s for s in satirlar if any(i in s for i in _OZET_ISARET)]
    return (isaretli[-1] if isaretli else (satirlar[-1] if satirlar else "(çıktı yok)"))[:120]


def _kos_yakala(komut: list[str], baslik: str) -> tuple[int, str]:
    """`_kos` gibi ama çıktıyı da döndürür — hem canlı basar hem özet için saklar."""
    print(f"\n{'=' * 78}\n▶ {baslik}\n{'=' * 78}", flush=True)
    p = subprocess.Popen(komut, cwd=KOK, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, text=True, bufsize=1)
    parcalar: list[str] = []
    assert p.stdout is not None
    for satir in p.stdout:
        print(satir, end="", flush=True)
        parcalar.append(satir)
    return p.wait(), "".join(parcalar)


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
    ozet: list[str] = []
    for komut, baslik in adimlar:
        rc, cikti = _kos_yakala(komut, baslik)
        ozet.append(f"  {'✓' if rc == 0 else '✗'} {baslik:22} {_son_anlamli(cikti)}")
        if rc != 0:
            kotu = rc
    # ÖZET EN SONDA ve TEK BLOK: kapı çıktısı çoğu zaman `tail` ile okunur; sayılar
    # ortada kalırsa kırpılır ve *"yeşil mi?"* sorusu cevaplanır ama *"kaç test, kaç
    # yüzde?"* cevapsız kalır (bu turda tam olarak bu oldu — ölçüm kaydı kayboldu).
    print("\n" + "=" * 78)
    print("FAZ KAPISI ÖZETİ")
    print("=" * 78)
    print("\n".join(ozet))
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
